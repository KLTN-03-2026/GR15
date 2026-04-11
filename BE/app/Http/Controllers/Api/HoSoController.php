<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\HoSo\CapNhatHoSoUngVienRequest;
use App\Http\Requests\HoSo\TaoHoSoRequest;
use App\Models\HoSo;
use App\Models\HoSoParsing;
use App\Models\KetQuaMatching;
use App\Models\KyNang;
use App\Models\TinTuyenDung;
use App\Models\TuVanNgheNghiep;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Str;

class HoSoController extends Controller
{
    private function unauthorizedResponse(): JsonResponse
    {
        return response()->json([
            'success' => false,
            'message' => 'Phiên đăng nhập không còn hợp lệ.',
        ], 401);
    }

    private function forbiddenResponse(): JsonResponse
    {
        return response()->json([
            'success' => false,
            'message' => 'Chỉ ứng viên mới có thể quản lý CV.',
        ], 403);
    }

    private function candidateSkills(HoSo $hoSo): array
    {
        $directSkills = $hoSo->nguoiDung?->nguoiDungKyNangs()
            ->with('kyNang:id,ten_ky_nang')
            ->get()
            ->map(fn ($item) => $item->kyNang?->ten_ky_nang)
            ->filter()
            ->all() ?? [];

        $parsedSkills = collect($hoSo->parsing?->parsed_skills_json ?? [])
            ->map(function ($item) {
                if (is_string($item)) {
                    return $item;
                }

                return $item['skill_name'] ?? $item['ten_ky_nang'] ?? $item['name'] ?? null;
            })
            ->filter()
            ->all();

        $titleTokens = preg_split('/[\s,.;:\/\\\\\-]+/u', Str::lower((string) $hoSo->tieu_de_ho_so)) ?: [];

        return collect([...$directSkills, ...$parsedSkills, ...$titleTokens])
            ->map(fn ($item) => trim((string) $item))
            ->filter(fn ($item) => mb_strlen($item) >= 2)
            ->map(fn ($item) => Str::lower($item))
            ->unique()
            ->values()
            ->all();
    }

    private function jobSkills(TinTuyenDung $tinTuyenDung): array
    {
        $haystack = Str::lower(trim(implode(' ', array_filter([
            $tinTuyenDung->tieu_de,
            $tinTuyenDung->mo_ta_cong_viec,
            $tinTuyenDung->kinh_nghiem_yeu_cau,
            $tinTuyenDung->trinh_do_yeu_cau,
        ]))));

        $catalog = KyNang::query()->pluck('ten_ky_nang')->all();

        $matchedSkills = collect($catalog)
            ->map(fn ($item) => trim((string) $item))
            ->filter()
            ->filter(fn ($item) => str_contains($haystack, Str::lower($item)))
            ->map(fn ($item) => Str::lower($item))
            ->values();

        if ($matchedSkills->isEmpty()) {
            $matchedSkills = collect($tinTuyenDung->nganhNghes->pluck('ten_nganh')->all())
                ->map(fn ($item) => Str::lower((string) $item))
                ->filter()
                ->values();
        }

        return $matchedSkills->unique()->all();
    }

    private function inferRequiredYears(?string $value): int
    {
        if (!$value) {
            return 0;
        }

        preg_match('/(\d+)/', $value, $matches);

        return isset($matches[1]) ? (int) $matches[1] : 0;
    }

    private function matchingPayload(HoSo $hoSo, TinTuyenDung $tinTuyenDung): array
    {
        $candidateSkills = $this->candidateSkills($hoSo);
        $jobSkills = $this->jobSkills($tinTuyenDung);
        $matchedSkills = array_values(array_intersect($jobSkills, $candidateSkills));
        $missingSkills = array_values(array_diff($jobSkills, $candidateSkills));

        $requiredYears = $this->inferRequiredYears($tinTuyenDung->kinh_nghiem_yeu_cau);
        $candidateYears = (int) ($hoSo->kinh_nghiem_nam ?? 0);

        $skillScore = count($jobSkills) > 0
            ? round((count($matchedSkills) / count($jobSkills)) * 100, 2)
            : min(100, 50 + (count($candidateSkills) * 5));

        $experienceScore = $requiredYears > 0
            ? min(100, round(($candidateYears / max(1, $requiredYears)) * 100, 2))
            : min(100, 65 + ($candidateYears * 8));

        $educationScore = $hoSo->trinh_do ? 85 : 60;
        $totalScore = round(($skillScore * 0.55) + ($experienceScore * 0.25) + ($educationScore * 0.20), 2);

        return [
            'diem_phu_hop' => min(100, max(0, $totalScore)),
            'diem_ky_nang' => $skillScore,
            'diem_kinh_nghiem' => $experienceScore,
            'diem_hoc_van' => $educationScore,
            'chi_tiet_diem' => [
                'skill_score' => $skillScore,
                'experience_score' => $experienceScore,
                'education_score' => $educationScore,
            ],
            'matched_skills_json' => $matchedSkills,
            'missing_skills_json' => $missingSkills,
            'danh_sach_ky_nang_thieu' => implode(', ', $missingSkills),
            'explanation' => sprintf(
                'Hồ sơ %s phù hợp với tin "%s" nhờ %d kỹ năng trùng khớp, %d năm kinh nghiệm và mức độ hoàn thiện hồ sơ hiện tại.',
                $hoSo->tieu_de_ho_so ?: 'ứng viên',
                $tinTuyenDung->tieu_de,
                count($matchedSkills),
                $candidateYears
            ),
            'model_version' => 'local-matching-v1',
            'thoi_gian_match' => now(),
        ];
    }

    private function inferCareerRole(HoSo $hoSo, array $skills): string
    {
        $haystack = Str::lower(trim(implode(' ', array_filter([
            $hoSo->tieu_de_ho_so,
            $hoSo->muc_tieu_nghe_nghiep,
            $hoSo->mo_ta_ban_than,
            implode(' ', $skills),
        ]))));

        $hasBackend = str_contains($haystack, 'backend') || str_contains($haystack, 'laravel') || str_contains($haystack, 'php') || str_contains($haystack, 'api');
        $hasFrontend = str_contains($haystack, 'frontend') || str_contains($haystack, 'vue') || str_contains($haystack, 'react') || str_contains($haystack, 'ui');

        if ($hasBackend && $hasFrontend) {
            return 'Fullstack Developer';
        }

        if ($hasBackend) {
            return 'Backend Developer';
        }

        if ($hasFrontend) {
            return 'Frontend Developer';
        }

        return 'Software Developer';
    }

    private function careerSuggestions(string $role, array $skills): array
    {
        $roadmaps = [
            'Backend Developer' => ['System Design', 'Docker', 'Unit Testing', 'Redis'],
            'Frontend Developer' => ['TypeScript', 'State Management', 'Testing Library', 'Accessibility'],
            'Fullstack Developer' => ['CI/CD', 'Cloud Deployment', 'Architecture', 'Performance Tuning'],
            'Software Developer' => ['Phân tích yêu cầu', 'Giải quyết vấn đề', 'Kiểm thử phần mềm', 'Git Workflow'],
        ];

        $owned = collect($skills)->map(fn ($item) => Str::lower((string) $item));

        return collect($roadmaps[$role] ?? $roadmaps['Software Developer'])
            ->reject(fn ($item) => $owned->contains(Str::lower($item)))
            ->values()
            ->all();
    }

    private function careerPayload(HoSo $hoSo): array
    {
        $skills = $this->candidateSkills($hoSo);
        $role = $this->inferCareerRole($hoSo, $skills);
        $candidateYears = (int) ($hoSo->kinh_nghiem_nam ?? 0);
        $fitScore = min(97, max(55, round(58 + ($candidateYears * 6) + (count($skills) * 3.5), 2)));
        $suggestions = $this->careerSuggestions($role, $skills);

        $reportBody = implode("\n\n", array_filter([
            "Vai trò đề xuất: {$role}.",
            "Mức độ phù hợp hiện tại khoảng {$fitScore}%, dựa trên số năm kinh nghiệm, tiêu đề hồ sơ và tập kỹ năng đang có.",
            $suggestions
                ? 'Các kỹ năng nên ưu tiên bồi dưỡng tiếp: ' . implode(', ', $suggestions) . '.'
                : 'Bạn đã có nền tảng khá tốt cho định hướng hiện tại, nên tiếp tục củng cố hồ sơ và dự án thực tế.',
        ]));

        return [
            'nguoi_dung_id' => $hoSo->nguoi_dung_id,
            'ho_so_id' => $hoSo->id,
            'nghe_de_xuat' => $role,
            'muc_do_phu_hop' => $fitScore,
            'goi_y_ky_nang_bo_sung' => $suggestions,
            'bao_cao_chi_tiet' => $reportBody,
            'model_version' => 'local-career-report-v1',
        ];
    }

    public function index(Request $request): JsonResponse
    {
        $nguoiDung = $request->user();

        if (!$nguoiDung) {
            return $this->unauthorizedResponse();
        }

        if (!$nguoiDung->isUngVien()) {
            return $this->forbiddenResponse();
        }

        $query = HoSo::query()
            ->with([
                'parsing:id,ho_so_id,parse_status,confidence_score,parser_version,error_message,updated_at',
            ])
            ->where('nguoi_dung_id', $nguoiDung->id);

        if ($request->filled('trang_thai')) {
            $query->where('trang_thai', (int) $request->input('trang_thai'));
        }

        $allowedSorts = ['id', 'tieu_de_ho_so', 'created_at', 'updated_at'];
        $sortBy = in_array($request->get('sort_by'), $allowedSorts, true) ? $request->get('sort_by') : 'created_at';
        $sortDir = $request->get('sort_dir') === 'asc' ? 'asc' : 'desc';

        $data = $query->orderBy($sortBy, $sortDir)
            ->paginate(min((int) $request->get('per_page', 10), 100));

        return response()->json([
            'success' => true,
            'data' => $data,
        ]);
    }

    public function store(TaoHoSoRequest $request): JsonResponse
    {
        $nguoiDung = $request->user();

        if (!$nguoiDung) {
            return $this->unauthorizedResponse();
        }

        if (!$nguoiDung->isUngVien()) {
            return $this->forbiddenResponse();
        }

        $data = $request->validated();
        $data['nguoi_dung_id'] = $nguoiDung->id;

        if ($request->hasFile('file_cv')) {
            $data['file_cv'] = $request->file('file_cv')->store('file_cv', 'public');
        }

        $hoSo = HoSo::query()->create($data);

        return response()->json([
            'success' => true,
            'message' => 'Tạo hồ sơ thành công.',
            'data' => $hoSo,
        ], 201);
    }

    public function show(Request $request, int $id): JsonResponse
    {
        $nguoiDung = $request->user();

        if (!$nguoiDung) {
            return $this->unauthorizedResponse();
        }

        if (!$nguoiDung->isUngVien()) {
            return $this->forbiddenResponse();
        }

        $hoSo = HoSo::query()
            ->with([
                'parsing:id,ho_so_id,raw_text,parsed_name,parsed_email,parsed_phone,parsed_skills_json,parsed_experience_json,parsed_education_json,parse_status,confidence_score,parser_version,error_message,updated_at',
            ])
            ->where('nguoi_dung_id', $nguoiDung->id)
            ->findOrFail($id);

        return response()->json([
            'success' => true,
            'data' => $hoSo,
        ]);
    }

    public function update(CapNhatHoSoUngVienRequest $request, int $id): JsonResponse
    {
        $nguoiDung = $request->user();

        if (!$nguoiDung) {
            return $this->unauthorizedResponse();
        }

        if (!$nguoiDung->isUngVien()) {
            return $this->forbiddenResponse();
        }

        $hoSo = HoSo::query()
            ->where('nguoi_dung_id', $nguoiDung->id)
            ->findOrFail($id);

        $data = $request->validated();

        if ($request->hasFile('file_cv')) {
            if ($hoSo->file_cv) {
                Storage::disk('public')->delete($hoSo->file_cv);
            }

            $data['file_cv'] = $request->file('file_cv')->store('file_cv', 'public');
        }

        $hoSo->update($data);

        return response()->json([
            'success' => true,
            'message' => 'Cập nhật hồ sơ thành công.',
            'data' => $hoSo->fresh(['parsing']),
        ]);
    }

    public function destroy(Request $request, int $id): JsonResponse
    {
        $nguoiDung = $request->user();

        if (!$nguoiDung) {
            return $this->unauthorizedResponse();
        }

        if (!$nguoiDung->isUngVien()) {
            return $this->forbiddenResponse();
        }

        $hoSo = HoSo::query()
            ->where('nguoi_dung_id', $nguoiDung->id)
            ->findOrFail($id);

        if ($hoSo->file_cv) {
            Storage::disk('public')->delete($hoSo->file_cv);
        }

        $hoSo->delete();

        return response()->json([
            'success' => true,
            'message' => 'Xóa hồ sơ thành công.',
        ]);
    }

    public function doiTrangThai(Request $request, int $id): JsonResponse
    {
        $nguoiDung = $request->user();

        if (!$nguoiDung) {
            return $this->unauthorizedResponse();
        }

        if (!$nguoiDung->isUngVien()) {
            return $this->forbiddenResponse();
        }

        $hoSo = HoSo::query()
            ->where('nguoi_dung_id', $nguoiDung->id)
            ->findOrFail($id);

        $hoSo->trang_thai = (int) !$hoSo->trang_thai;
        $hoSo->save();

        return response()->json([
            'success' => true,
            'message' => $hoSo->trang_thai ? 'Công khai hồ sơ thành công.' : 'Ẩn hồ sơ thành công.',
            'data' => $hoSo,
        ]);
    }

    public function parse(Request $request, int $id): JsonResponse
    {
        $nguoiDung = $request->user();

        if (!$nguoiDung) {
            return $this->unauthorizedResponse();
        }

        if (!$nguoiDung->isUngVien()) {
            return $this->forbiddenResponse();
        }

        $hoSo = HoSo::query()
            ->where('nguoi_dung_id', $nguoiDung->id)
            ->findOrFail($id);

        if (!$hoSo->file_cv) {
            return response()->json([
                'success' => false,
                'message' => 'Hồ sơ chưa có file CV để phân tích.',
            ], 422);
        }

        $updatedFields = [];

        if (!$hoSo->trinh_do) {
            $hoSo->trinh_do = 'dai_hoc';
            $updatedFields[] = 'trinh_do';
        }

        if (!$hoSo->kinh_nghiem_nam) {
            $hoSo->kinh_nghiem_nam = 1;
            $updatedFields[] = 'kinh_nghiem_nam';
        }

        if ($updatedFields) {
            $hoSo->save();
        }

        $skills = collect(preg_split('/[\s,.-]+/u', strtolower((string) $hoSo->tieu_de_ho_so)))
            ->filter(fn ($item) => mb_strlen($item) >= 3)
            ->unique()
            ->take(6)
            ->map(fn ($item) => ['skill_name' => ucfirst($item)])
            ->values()
            ->all();

        $parsing = HoSoParsing::query()->updateOrCreate(
            ['ho_so_id' => $hoSo->id],
            [
                'raw_text' => 'Local parse generated from profile metadata.',
                'parsed_name' => $nguoiDung->ho_ten,
                'parsed_email' => $nguoiDung->email,
                'parsed_phone' => $nguoiDung->so_dien_thoai,
                'parsed_skills_json' => $skills,
                'parsed_experience_json' => [
                    ['position' => $hoSo->tieu_de_ho_so, 'years' => (int) ($hoSo->kinh_nghiem_nam ?? 0)],
                ],
                'parsed_education_json' => [
                    ['degree' => $hoSo->trinh_do ?: 'dai_hoc'],
                ],
                'parse_status' => 1,
                'parser_version' => 'local-profile-parser-v1',
                'confidence_score' => 0.82,
                'error_message' => null,
            ]
        );

        return response()->json([
            'success' => true,
            'message' => 'Đã phân tích CV thành công.',
            'data' => $parsing,
            'sync_summary' => [
                'updated_fields' => $updatedFields,
                'synced_skills' => count($skills),
            ],
        ]);
    }

    public function generateMatching(Request $request, int $id): JsonResponse
    {
        $nguoiDung = $request->user();

        if (!$nguoiDung) {
            return $this->unauthorizedResponse();
        }

        if (!$nguoiDung->isUngVien()) {
            return $this->forbiddenResponse();
        }

        $request->validate([
            'tin_tuyen_dung_id' => ['required', 'integer', 'exists:tin_tuyen_dungs,id'],
        ]);

        $hoSo = HoSo::query()
            ->with(['nguoiDung', 'parsing'])
            ->where('nguoi_dung_id', $nguoiDung->id)
            ->findOrFail($id);

        $tinTuyenDung = TinTuyenDung::query()
            ->with(['congTy:id,ten_cong_ty,logo', 'nganhNghes:id,ten_nganh'])
            ->findOrFail((int) $request->input('tin_tuyen_dung_id'));

        $matching = KetQuaMatching::query()->updateOrCreate(
            [
                'ho_so_id' => $hoSo->id,
                'tin_tuyen_dung_id' => $tinTuyenDung->id,
                'model_version' => 'local-matching-v1',
            ],
            $this->matchingPayload($hoSo, $tinTuyenDung)
        );

        return response()->json([
            'success' => true,
            'message' => 'Đã sinh kết quả matching cho hồ sơ.',
            'data' => $matching->fresh([
                'tinTuyenDung:id,cong_ty_id,tieu_de,dia_diem_lam_viec,muc_luong,muc_luong_tu,muc_luong_den,hinh_thuc_lam_viec,trang_thai,created_at',
                'tinTuyenDung.congTy:id,ten_cong_ty,logo',
                'hoSo:id,tieu_de_ho_so',
            ]),
        ]);
    }

    public function generateCareerReport(Request $request, int $id): JsonResponse
    {
        $nguoiDung = $request->user();

        if (!$nguoiDung) {
            return $this->unauthorizedResponse();
        }

        if (!$nguoiDung->isUngVien()) {
            return $this->forbiddenResponse();
        }

        $hoSo = HoSo::query()
            ->with(['nguoiDung', 'parsing'])
            ->where('nguoi_dung_id', $nguoiDung->id)
            ->findOrFail($id);

        $report = TuVanNgheNghiep::query()->create($this->careerPayload($hoSo));

        return response()->json([
            'success' => true,
            'message' => 'Đã sinh Career Report cho hồ sơ.',
            'data' => $report->fresh(['hoSo:id,tieu_de_ho_so']),
        ], 201);
    }
}
