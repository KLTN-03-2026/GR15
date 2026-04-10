<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\HoSo;
use App\Models\HoSoParsing;
use App\Models\KyNang;
use App\Models\NguoiDungKyNang;
use App\Services\Ai\AiClientService;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Str;
use Illuminate\Http\Request;
use RuntimeException;

class CvParsingController extends Controller
{
    public function __construct(
        private readonly AiClientService $aiClientService
    ) {
    }

    public function parse(Request $request, int $id): JsonResponse
    {
        $hoSo = HoSo::where('nguoi_dung_id', $request->user()->id)->findOrFail($id);

        if (!$hoSo->file_cv) {
            return response()->json([
                'success' => false,
                'message' => 'Hồ sơ chưa có file CV để phân tích.',
            ], 422);
        }

        try {
            $result = $this->aiClientService->parseCv($hoSo->id, $hoSo->file_cv);
            $data = $result['data'] ?? [];

            $parsing = HoSoParsing::updateOrCreate(
                ['ho_so_id' => $hoSo->id],
                [
                    'raw_text' => $data['raw_text'] ?? null,
                    'parsed_name' => $data['parsed_name'] ?? null,
                    'parsed_email' => $data['parsed_email'] ?? null,
                    'parsed_phone' => $data['parsed_phone'] ?? null,
                    'parsed_skills_json' => $data['parsed_skills_json'] ?? null,
                    'parsed_experience_json' => $data['parsed_experience_json'] ?? null,
                    'parsed_education_json' => $data['parsed_education_json'] ?? null,
                    'parse_status' => ($result['success'] ?? false) ? 1 : 2,
                    'parser_version' => $result['parser_version'] ?? null,
                    'confidence_score' => $result['confidence_score'] ?? null,
                    'error_message' => $result['error'] ?? null,
                ]
            );

            $syncSummary = $this->dongBoDuLieuSauParse($hoSo, $data, (float) ($result['confidence_score'] ?? 0));
        } catch (RuntimeException $e) {
            HoSoParsing::updateOrCreate(
                ['ho_so_id' => $hoSo->id],
                [
                    'parse_status' => 2,
                    'error_message' => $e->getMessage(),
                ]
            );

            return response()->json([
                'success' => false,
                'message' => $e->getMessage(),
            ], 502);
        }

        return response()->json([
            'success' => true,
            'message' => 'Phân tích CV thành công và đã tự động đồng bộ dữ liệu.',
            'data' => $parsing,
            'sync_summary' => $syncSummary ?? null,
        ]);
    }

    private function dongBoDuLieuSauParse(HoSo $hoSo, array $data, float $confidenceScore): array
    {
        $updatedFields = [];

        $trinhDo = $this->suyLuanTrinhDo($data['parsed_education_json'] ?? []);
        if (!$hoSo->trinh_do && $trinhDo) {
            $hoSo->trinh_do = $trinhDo;
            $updatedFields[] = 'trinh_do';
        }

        $kinhNghiemNam = $this->uocLuongKinhNghiemNam($data['parsed_experience_json'] ?? [], $data['raw_text'] ?? null);
        if ((int) ($hoSo->kinh_nghiem_nam ?? 0) === 0 && $kinhNghiemNam > 0) {
            $hoSo->kinh_nghiem_nam = $kinhNghiemNam;
            $updatedFields[] = 'kinh_nghiem_nam';
        }

        if ($updatedFields) {
            $hoSo->save();
        }

        $syncedSkills = $this->dongBoKyNangChoNguoiDung($hoSo->nguoi_dung_id, $data['parsed_skills_json'] ?? [], $confidenceScore);

        return [
            'updated_fields' => $updatedFields,
            'synced_skills' => $syncedSkills,
        ];
    }

    private function dongBoKyNangChoNguoiDung(int $nguoiDungId, array $parsedSkills, float $confidenceScore): int
    {
        $inserted = 0;

        foreach ($parsedSkills as $skill) {
            $skillName = trim((string) ($skill['skill_name'] ?? $skill['name'] ?? ''));
            if ($skillName === '') {
                continue;
            }

            $catalogSkill = KyNang::firstOrCreate(
                ['ten_ky_nang' => $skillName],
                ['mo_ta' => 'Được tạo tự động từ AI parse CV.']
            );

            $exists = NguoiDungKyNang::where('nguoi_dung_id', $nguoiDungId)
                ->where('ky_nang_id', $catalogSkill->id)
                ->exists();

            if ($exists) {
                continue;
            }

            NguoiDungKyNang::create([
                'nguoi_dung_id' => $nguoiDungId,
                'ky_nang_id' => $catalogSkill->id,
                'muc_do' => 3,
                'nam_kinh_nghiem' => 0,
                'so_chung_chi' => 0,
                'nguon_du_lieu' => 'cv_parser',
                'do_tin_cay' => $skill['confidence'] ?? $confidenceScore ?: null,
            ]);

            $inserted++;
        }

        return $inserted;
    }

    private function suyLuanTrinhDo(array $educationBlocks): ?string
    {
        $text = Str::lower(implode(' ', array_map(function ($item) {
            return is_string($item) ? $item : json_encode($item, JSON_UNESCAPED_UNICODE);
        }, $educationBlocks)));

        return match (true) {
            str_contains($text, 'tiến sĩ') || str_contains($text, 'tien si') || str_contains($text, 'phd') => 'tien_si',
            str_contains($text, 'thạc sĩ') || str_contains($text, 'thac si') || str_contains($text, 'master') => 'thac_si',
            str_contains($text, 'đại học') || str_contains($text, 'dai hoc') || str_contains($text, 'university') => 'dai_hoc',
            str_contains($text, 'cao đẳng') || str_contains($text, 'cao dang') || str_contains($text, 'college') => 'cao_dang',
            str_contains($text, 'trung cấp') || str_contains($text, 'trung cap') => 'trung_cap',
            str_contains($text, 'trung học') || str_contains($text, 'trung hoc') || str_contains($text, 'high school') => 'trung_hoc',
            default => null,
        };
    }

    private function uocLuongKinhNghiemNam(array $experienceBlocks, ?string $rawText): int
    {
        $text = implode(' ', array_map(function ($item) {
            return is_string($item) ? $item : json_encode($item, JSON_UNESCAPED_UNICODE);
        }, $experienceBlocks));

        $text .= ' ' . (string) $rawText;

        preg_match_all('/(\d+)\s*\+?\s*(?:nam|năm|years?)/iu', $text, $matches);
        if (!empty($matches[1])) {
            return min(max((int) max($matches[1]), 0), 50);
        }

        return 0;
    }
}
