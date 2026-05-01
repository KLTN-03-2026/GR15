<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\HoSo;
use App\Models\KetQuaMatching;
use App\Models\TinTuyenDung;
use App\Services\Ai\AiClientService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use RuntimeException;

class CvTailoringController extends Controller
{
    public function __construct(private readonly AiClientService $aiClientService)
    {
    }

    public function tailorForJob(Request $request, int $id, int $tinTuyenDungId): JsonResponse
    {
        $data = $request->validate([
            'preview_only' => ['nullable', 'boolean'],
            'tailoring' => ['nullable', 'array'],
        ]);
        $user = $request->user();

        if (!$user) {
            return response()->json([
                'success' => false,
                'message' => 'Phiên đăng nhập không còn hợp lệ.',
            ], 401);
        }

        $sourceProfile = HoSo::with([
                'parsing:id,ho_so_id,raw_text,parsed_skills_json,parsed_experience_json,parsed_education_json,parse_status,confidence_score',
            ])
            ->where('nguoi_dung_id', $user->id)
            ->findOrFail($id);

        $job = TinTuyenDung::with([
                'congTy:id,ten_cong_ty',
                'nganhNghes:id,ten_nganh',
                'kyNangYeuCaus.kyNang:id,ten_ky_nang',
                'parsing:id,tin_tuyen_dung_id,raw_text,parsed_skills_json,parsed_requirements_json,parse_status,confidence_score',
            ])
            ->where('trang_thai', TinTuyenDung::TRANG_THAI_HOAT_DONG)
            ->findOrFail($tinTuyenDungId);

        $cvProfile = $this->buildCvProfile($sourceProfile);
        $jdProfile = $this->buildJdProfile($job);
        $usedFallback = false;
        $tailoring = isset($data['tailoring']) && is_array($data['tailoring'])
            ? $this->normalizeTailoringPayload($data['tailoring'], $sourceProfile, $job)
            : null;

        if (!$tailoring) {
            try {
                $response = $this->aiClientService->tailorCvForJob((int) $sourceProfile->id, (int) $job->id, $cvProfile, $jdProfile);
                $tailoring = $this->normalizeTailoringPayload($response['data'] ?? $response, $sourceProfile, $job);
            } catch (RuntimeException $exception) {
                $usedFallback = true;
                $this->aiClientService->recordFallback(
                    'cv_tailoring',
                    $exception->getMessage(),
                    [
                        'ho_so_id' => (int) $sourceProfile->id,
                        'tin_tuyen_dung_id' => (int) $job->id,
                        'cv_profile' => $cvProfile,
                        'jd_profile' => $jdProfile,
                    ],
                    ['preview_only' => (bool) ($data['preview_only'] ?? false)]
                );
                $tailoring = $this->fallbackTailoringPayload($sourceProfile, $job, $cvProfile, $jdProfile, $exception->getMessage());
            }
        }

        $comparison = $this->buildTailoringComparison($sourceProfile, $job, $tailoring, $cvProfile, $jdProfile);

        if ((bool) ($data['preview_only'] ?? false)) {
            return response()->json([
                'success' => true,
                'message' => $usedFallback
                    ? 'AI service chưa phản hồi, hệ thống đã tạo preview CV tối ưu bằng bộ quy tắc dự phòng.'
                    : 'Đã tạo preview CV tối ưu theo tin tuyển dụng.',
                'data' => [
                    'profile' => null,
                    'preview_profile' => $this->buildTailoredProfileData($sourceProfile, $job, $tailoring),
                    'source_profile_id' => $sourceProfile->id,
                    'job_id' => $job->id,
                    'job_title' => $job->tieu_de,
                    'company_name' => $job->congTy?->ten_cong_ty,
                    'tailoring' => $tailoring,
                    'comparison' => $comparison,
                    'matching' => null,
                    'used_fallback' => $usedFallback,
                ],
            ]);
        }

        $profileData = $this->buildTailoredProfileData($sourceProfile, $job, $tailoring);
        $tailoredProfile = HoSo::create($profileData);
        $matching = $this->generateMatchingForTailoredProfile($tailoredProfile->fresh(), $job);

        return response()->json([
            'success' => true,
            'message' => $usedFallback
                ? 'AI service chưa phản hồi, hệ thống đã tạo CV tối ưu bằng bộ quy tắc dự phòng.'
                : 'Đã tạo CV tối ưu theo tin tuyển dụng.',
            'data' => [
                'profile' => $tailoredProfile->fresh(),
                'source_profile_id' => $sourceProfile->id,
                'job_id' => $job->id,
                'job_title' => $job->tieu_de,
                'company_name' => $job->congTy?->ten_cong_ty,
                'tailoring' => $tailoring,
                'comparison' => $comparison,
                'matching' => $matching,
                'used_fallback' => $usedFallback,
            ],
        ], 201);
    }

    private function buildCvProfile(HoSo $profile): array
    {
        $parsing = $profile->parsing;

        return [
            'id' => $profile->id,
            'title' => $profile->tieu_de_ho_so,
            'career_goal' => $profile->muc_tieu_nghe_nghiep,
            'summary' => $profile->mo_ta_ban_than,
            'education_level' => $profile->trinh_do,
            'years_experience' => $profile->kinh_nghiem_nam,
            'target_position' => $profile->vi_tri_ung_tuyen_muc_tieu,
            'target_industry' => $profile->ten_nganh_nghe_muc_tieu,
            'skills' => $this->extractSkillNames($profile->ky_nang_json ?: $parsing?->parsed_skills_json ?: []),
            'skill_items' => $profile->ky_nang_json ?: [],
            'experiences' => $profile->kinh_nghiem_json ?: $parsing?->parsed_experience_json ?: [],
            'education' => $profile->hoc_van_json ?: $parsing?->parsed_education_json ?: [],
            'projects' => $profile->du_an_json ?: [],
            'certificates' => $profile->chung_chi_json ?: [],
            'raw_text' => mb_substr((string) ($parsing?->raw_text ?? ''), 0, 6000),
        ];
    }

    private function buildJdProfile(TinTuyenDung $job): array
    {
        $skillNames = $job->kyNangYeuCaus
            ? $job->kyNangYeuCaus->map(fn ($item) => $item->kyNang?->ten_ky_nang)->filter()->values()->all()
            : [];

        if ($skillNames === [] && $job->parsing?->parsed_skills_json) {
            $skillNames = $this->extractSkillNames($job->parsing->parsed_skills_json);
        }

        return [
            'id' => $job->id,
            'title' => $job->tieu_de,
            'company' => $job->congTy?->ten_cong_ty,
            'description' => $job->mo_ta_cong_viec,
            'requirements' => $job->parsing?->parsed_requirements_json ?: $job->mo_ta_cong_viec,
            'experience_required' => $job->kinh_nghiem_yeu_cau,
            'education_required' => $job->trinh_do_yeu_cau,
            'level' => $job->cap_bac,
            'work_type' => $job->hinh_thuc_lam_viec,
            'industries' => $job->nganhNghes?->pluck('ten_nganh')->values()->all() ?? [],
            'skills' => $skillNames,
            'raw_text' => mb_substr((string) ($job->parsing?->raw_text ?? $job->mo_ta_cong_viec ?? ''), 0, 6000),
        ];
    }

    private function normalizeTailoringPayload(array $payload, HoSo $sourceProfile, TinTuyenDung $job): array
    {
        $tailored = is_array($payload['tailored_profile'] ?? null) ? $payload['tailored_profile'] : $payload;

        return [
            'title' => (string) ($tailored['title'] ?? "CV {$job->tieu_de} - {$job->congTy?->ten_cong_ty}"),
            'career_goal' => (string) ($tailored['career_goal'] ?? $sourceProfile->muc_tieu_nghe_nghiep ?? ''),
            'summary' => (string) ($tailored['summary'] ?? $sourceProfile->mo_ta_ban_than ?? ''),
            'skills' => $this->normalizeSkillItems($tailored['skills'] ?? $sourceProfile->ky_nang_json ?? []),
            'experiences' => $this->normalizeArray($tailored['experiences'] ?? $sourceProfile->kinh_nghiem_json ?? []),
            'projects' => $this->normalizeArray($tailored['projects'] ?? $sourceProfile->du_an_json ?? []),
            'education' => $this->normalizeArray($tailored['education'] ?? $sourceProfile->hoc_van_json ?? []),
            'certificates' => $this->normalizeArray($tailored['certificates'] ?? $sourceProfile->chung_chi_json ?? []),
            'matched_keywords' => $this->normalizeStringList($payload['matched_keywords'] ?? $tailored['matched_keywords'] ?? []),
            'skill_gaps' => $this->normalizeStringList($payload['skill_gaps'] ?? $tailored['skill_gaps'] ?? []),
            'recommendations' => $this->normalizeStringList($payload['recommendations'] ?? $tailored['recommendations'] ?? []),
            'cover_letter_suggestion' => (string) ($payload['cover_letter_suggestion'] ?? $tailored['cover_letter_suggestion'] ?? ''),
            'model_version' => (string) ($payload['model_version'] ?? 'cv_tailoring_v1'),
        ];
    }

    private function fallbackTailoringPayload(HoSo $sourceProfile, TinTuyenDung $job, array $cvProfile, array $jdProfile, ?string $aiError = null): array
    {
        $jobSkills = $this->normalizeStringList($jdProfile['skills'] ?? []);
        $candidateSkills = $this->normalizeStringList($cvProfile['skills'] ?? []);
        $matched = array_values(array_filter($candidateSkills, fn ($skill) => $this->containsSimilarSkill($skill, $jobSkills)));
        $missing = array_values(array_filter($jobSkills, fn ($skill) => !$this->containsSimilarSkill($skill, $candidateSkills)));

        $prioritizedSkills = collect([
                ...$matched,
                ...array_slice($candidateSkills, 0, 12),
            ])
            ->filter()
            ->unique(fn ($item) => mb_strtolower($item))
            ->take(14)
            ->map(fn ($name) => ['ten' => $name, 'muc_do' => in_array($name, $matched, true) ? 'tot' : 'kha'])
            ->values()
            ->all();

        return [
            'title' => mb_substr("CV {$job->tieu_de} - {$job->congTy?->ten_cong_ty}", 0, 190),
            'career_goal' => "Ứng tuyển vị trí {$job->tieu_de}, tập trung thể hiện kinh nghiệm và kỹ năng phù hợp với yêu cầu của {$job->congTy?->ten_cong_ty}.",
            'summary' => $this->tailoredSummary($sourceProfile, $job, $matched),
            'skills' => $prioritizedSkills ?: $this->normalizeSkillItems($sourceProfile->ky_nang_json ?: []),
            'experiences' => $this->prioritizeItemsByKeywords($sourceProfile->kinh_nghiem_json ?: [], $jobSkills),
            'projects' => $this->prioritizeItemsByKeywords($sourceProfile->du_an_json ?: [], $jobSkills),
            'education' => $this->normalizeArray($sourceProfile->hoc_van_json ?: []),
            'certificates' => $this->normalizeArray($sourceProfile->chung_chi_json ?: []),
            'matched_keywords' => $matched,
            'skill_gaps' => $missing,
            'recommendations' => [
                'Đưa các kỹ năng khớp JD lên đầu phần kỹ năng.',
                'Bổ sung số liệu kết quả cụ thể cho kinh nghiệm/dự án liên quan.',
                $missing ? 'Nếu có kinh nghiệm với ' . implode(', ', array_slice($missing, 0, 4)) . ', hãy bổ sung minh chứng trước khi ứng tuyển.' : 'CV đã có nhiều keyword phù hợp, nên kiểm tra lại chính tả và mức độ cụ thể.',
            ],
            'cover_letter_suggestion' => "Tôi quan tâm tới vị trí {$job->tieu_de} tại {$job->congTy?->ten_cong_ty} và tin rằng kinh nghiệm của mình với " . (implode(', ', array_slice($matched, 0, 3)) ?: 'các dự án liên quan') . ' có thể đóng góp tốt cho đội ngũ.',
            'model_version' => 'local_fallback_cv_tailoring_v1',
            'ai_error' => $aiError,
        ];
    }

    private function buildTailoredProfileData(HoSo $sourceProfile, TinTuyenDung $job, array $tailoring): array
    {
        $layout = in_array($sourceProfile->bo_cuc_cv, ['executive_navy', 'topcv_maroon', 'ats_serif'], true)
            ? $sourceProfile->bo_cuc_cv
            : 'executive_navy';

        return [
            'nguoi_dung_id' => $sourceProfile->nguoi_dung_id,
            'tieu_de_ho_so' => mb_substr($tailoring['title'], 0, 200),
            'muc_tieu_nghe_nghiep' => $tailoring['career_goal'],
            'trinh_do' => $sourceProfile->trinh_do,
            'kinh_nghiem_nam' => $sourceProfile->kinh_nghiem_nam,
            'mo_ta_ban_than' => $tailoring['summary'],
            'nguon_ho_so' => 'builder',
            'mau_cv' => $sourceProfile->mau_cv ?: 'executive_navy',
            'bo_cuc_cv' => $layout,
            'ten_template_cv' => $sourceProfile->ten_template_cv ?: 'Executive Navy',
            'che_do_mau_cv' => 'position',
            'vi_tri_ung_tuyen_muc_tieu' => $job->tieu_de,
            'ten_nganh_nghe_muc_tieu' => $job->nganhNghes?->pluck('ten_nganh')->first() ?: $sourceProfile->ten_nganh_nghe_muc_tieu,
            'che_do_anh_cv' => 'profile',
            'ky_nang_json' => $tailoring['skills'],
            'kinh_nghiem_json' => $tailoring['experiences'],
            'hoc_van_json' => $tailoring['education'],
            'du_an_json' => $tailoring['projects'],
            'chung_chi_json' => $tailoring['certificates'],
            'trang_thai' => HoSo::TRANG_THAI_CONG_KHAI,
        ];
    }

    private function buildTailoringComparison(HoSo $sourceProfile, TinTuyenDung $job, array $tailoring, array $cvProfile, array $jdProfile): array
    {
        $originalSkills = $this->normalizeStringList($cvProfile['skills'] ?? []);
        $tailoredSkills = $this->extractSkillNames($tailoring['skills'] ?? []);
        $jobSkills = $this->normalizeStringList($jdProfile['skills'] ?? []);
        $prioritizedSkills = array_values(array_filter($tailoredSkills, fn ($skill) => $this->containsSimilarSkill($skill, $jobSkills)));
        $addedSkills = array_values(array_filter($tailoredSkills, fn ($skill) => !$this->containsSimilarSkill($skill, $originalSkills)));

        return [
            'original_title' => $sourceProfile->tieu_de_ho_so,
            'tailored_title' => $tailoring['title'],
            'job_title' => $job->tieu_de,
            'summary_changed' => trim((string) $sourceProfile->mo_ta_ban_than) !== trim((string) $tailoring['summary']),
            'career_goal_changed' => trim((string) $sourceProfile->muc_tieu_nghe_nghiep) !== trim((string) $tailoring['career_goal']),
            'original_skill_count' => count($originalSkills),
            'tailored_skill_count' => count($tailoredSkills),
            'prioritized_skills' => array_slice($prioritizedSkills, 0, 8),
            'added_skills' => array_slice($addedSkills, 0, 8),
            'reordered_sections' => [
                'experiences' => $this->sectionOrderChanged($sourceProfile->kinh_nghiem_json ?: [], $tailoring['experiences'] ?? []),
                'projects' => $this->sectionOrderChanged($sourceProfile->du_an_json ?: [], $tailoring['projects'] ?? []),
            ],
        ];
    }

    private function generateMatchingForTailoredProfile(HoSo $profile, TinTuyenDung $job): ?array
    {
        try {
            $cvProfile = [
                'tieu_de_ho_so' => $profile->tieu_de_ho_so,
                'trinh_do' => $profile->trinh_do,
                'kinh_nghiem_nam' => $profile->kinh_nghiem_nam,
                'raw_text' => $this->profilePlainText($profile),
                'parsed_skills' => $this->extractSkillNames($profile->ky_nang_json ?: []),
                'parsed_experience' => $profile->kinh_nghiem_json ?: [],
                'parsed_education' => $profile->hoc_van_json ?: [],
            ];

            $jdProfile = [
                'tieu_de' => $job->tieu_de,
                'cap_bac' => $job->cap_bac,
                'kinh_nghiem_yeu_cau' => $job->kinh_nghiem_yeu_cau,
                'trinh_do_yeu_cau' => $job->trinh_do_yeu_cau,
                'raw_text' => $job->parsing?->raw_text ?? $job->mo_ta_cong_viec,
                'parsed_skills' => $job->parsing?->parsed_skills_json ?? [],
                'required_skills' => $job->kyNangYeuCaus
                    ->map(fn ($item) => [
                        'skill_name' => $item->kyNang?->ten_ky_nang,
                        'bat_buoc' => (bool) ($item->bat_buoc ?? false),
                        'trong_so' => $item->trong_so ?? 1.0,
                    ])
                    ->filter(fn ($item) => !empty($item['skill_name']))
                    ->values()
                    ->all(),
            ];

            $result = $this->aiClientService->matchCvJd((int) $profile->id, (int) $job->id, $cvProfile, $jdProfile);
            $data = $result['data'] ?? [];

            $matching = KetQuaMatching::updateOrCreate(
                [
                    'ho_so_id' => $profile->id,
                    'tin_tuyen_dung_id' => $job->id,
                    'model_version' => $data['model_version'] ?? ($result['model_version'] ?? 'matching_v1'),
                ],
                [
                    'diem_phu_hop' => $data['diem_phu_hop'] ?? 0,
                    'diem_ky_nang' => $data['diem_ky_nang'] ?? null,
                    'diem_kinh_nghiem' => $data['diem_kinh_nghiem'] ?? null,
                    'diem_hoc_van' => $data['diem_hoc_van'] ?? null,
                    'chi_tiet_diem' => $data['chi_tiet_diem'] ?? null,
                    'matched_skills_json' => $data['matched_skills_json'] ?? null,
                    'missing_skills_json' => $data['missing_skills_json'] ?? null,
                    'explanation' => $data['explanation'] ?? null,
                    'danh_sach_ky_nang_thieu' => $data['danh_sach_ky_nang_thieu'] ?? null,
                    'thoi_gian_match' => now(),
                ]
            );

            return $matching->fresh()?->toArray();
        } catch (RuntimeException $exception) {
            report($exception);
            return null;
        }
    }

    private function sectionOrderChanged(array $original, array $tailored): bool
    {
        if (count($original) < 2 || count($tailored) < 2) {
            return false;
        }

        return json_encode($original[0] ?? [], JSON_UNESCAPED_UNICODE) !== json_encode($tailored[0] ?? [], JSON_UNESCAPED_UNICODE);
    }

    private function profilePlainText(HoSo $profile): string
    {
        return collect([
            $profile->tieu_de_ho_so,
            $profile->muc_tieu_nghe_nghiep,
            $profile->mo_ta_ban_than,
            json_encode($profile->ky_nang_json ?: [], JSON_UNESCAPED_UNICODE),
            json_encode($profile->kinh_nghiem_json ?: [], JSON_UNESCAPED_UNICODE),
            json_encode($profile->du_an_json ?: [], JSON_UNESCAPED_UNICODE),
        ])->filter()->implode("\n");
    }

    private function extractSkillNames(mixed $items): array
    {
        if (!is_array($items)) {
            return [];
        }

        return collect($items)
            ->map(function ($item) {
                if (is_string($item)) {
                    return $item;
                }

                if (is_array($item)) {
                    return $item['ten'] ?? $item['name'] ?? $item['skill_name'] ?? $item['ten_ky_nang'] ?? null;
                }

                return null;
            })
            ->filter()
            ->map(fn ($item) => trim((string) $item))
            ->filter()
            ->unique(fn ($item) => mb_strtolower($item))
            ->values()
            ->all();
    }

    private function normalizeSkillItems(mixed $items): array
    {
        if (!is_array($items)) {
            return [];
        }

        return collect($items)
            ->map(function ($item) {
                if (is_string($item)) {
                    return ['ten' => trim($item), 'muc_do' => 'kha'];
                }

                if (is_array($item)) {
                    $name = trim((string) ($item['ten'] ?? $item['name'] ?? $item['skill_name'] ?? $item['ten_ky_nang'] ?? ''));
                    if ($name === '') {
                        return null;
                    }

                    return [
                        'ten' => $name,
                        'muc_do' => $item['muc_do'] ?? $item['level'] ?? 'kha',
                    ];
                }

                return null;
            })
            ->filter()
            ->unique(fn ($item) => mb_strtolower($item['ten']))
            ->values()
            ->all();
    }

    private function normalizeArray(mixed $items): array
    {
        return is_array($items) ? array_values($items) : [];
    }

    private function normalizeStringList(mixed $items): array
    {
        if (is_string($items) && trim($items) !== '') {
            return [trim($items)];
        }

        if (!is_array($items)) {
            return [];
        }

        return collect($items)
            ->map(fn ($item) => is_array($item) ? ($item['ten'] ?? $item['name'] ?? $item['skill_name'] ?? $item['text'] ?? null) : $item)
            ->filter()
            ->map(fn ($item) => trim((string) $item))
            ->filter()
            ->unique(fn ($item) => mb_strtolower($item))
            ->values()
            ->all();
    }

    private function containsSimilarSkill(string $needle, array $haystack): bool
    {
        $needleLower = mb_strtolower($needle);

        foreach ($haystack as $item) {
            $candidate = mb_strtolower((string) $item);
            if ($candidate === $needleLower || str_contains($candidate, $needleLower) || str_contains($needleLower, $candidate)) {
                return true;
            }
        }

        return false;
    }

    private function prioritizeItemsByKeywords(array $items, array $keywords): array
    {
        return collect($items)
            ->sortByDesc(function ($item) use ($keywords) {
                $text = mb_strtolower(json_encode($item, JSON_UNESCAPED_UNICODE) ?: '');

                return collect($keywords)->reduce(
                    fn ($score, $keyword) => $score + (str_contains($text, mb_strtolower((string) $keyword)) ? 1 : 0),
                    0
                );
            })
            ->values()
            ->all();
    }

    private function tailoredSummary(HoSo $sourceProfile, TinTuyenDung $job, array $matchedSkills): string
    {
        $base = trim((string) ($sourceProfile->mo_ta_ban_than ?: $sourceProfile->muc_tieu_nghe_nghiep));
        $skills = implode(', ', array_slice($matchedSkills, 0, 4));

        if ($skills) {
            return "Ứng viên có định hướng phù hợp với vị trí {$job->tieu_de}, nổi bật ở các kỹ năng {$skills}. " . $base;
        }

        return "Ứng viên quan tâm tới vị trí {$job->tieu_de} và có thể đóng góp dựa trên kinh nghiệm, kỹ năng đã trình bày trong CV. " . $base;
    }
}
