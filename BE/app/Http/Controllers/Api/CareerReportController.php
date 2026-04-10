<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\HoSo;
use App\Models\KetQuaMatching;
use App\Models\TuVanNgheNghiep;
use App\Services\Ai\AiClientService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use RuntimeException;

class CareerReportController extends Controller
{
    public function __construct(
        private readonly AiClientService $aiClientService
    ) {
    }

    public function generate(Request $request, int $id): JsonResponse
    {
        $hoSo = HoSo::with('parsing')
            ->where('nguoi_dung_id', $request->user()->id)
            ->findOrFail($id);

        $cvProfile = [
            'ho_ten' => $request->user()->ho_ten,
            'tieu_de_ho_so' => $hoSo->tieu_de_ho_so,
            'trinh_do' => $hoSo->trinh_do,
            'kinh_nghiem_nam' => $hoSo->kinh_nghiem_nam,
            'parsed_name' => $hoSo->parsing?->parsed_name,
            'parsed_skills' => $hoSo->parsing?->parsed_skills_json ?? [],
            'parsed_experience' => $hoSo->parsing?->parsed_experience_json ?? [],
            'parsed_education' => $hoSo->parsing?->parsed_education_json ?? [],
            'raw_text' => $hoSo->parsing?->raw_text,
        ];

        $matchingProfiles = KetQuaMatching::query()
            ->where('ho_so_id', $hoSo->id)
            ->with('tinTuyenDung:id,tieu_de')
            ->orderByDesc('diem_phu_hop')
            ->limit(5)
            ->get()
            ->map(function (KetQuaMatching $item) {
                return [
                    'job_title' => $item->tinTuyenDung?->tieu_de,
                    'diem_phu_hop' => $item->diem_phu_hop,
                    'matched_skills_json' => $item->matched_skills_json,
                    'missing_skills_json' => $item->missing_skills_json,
                    'chi_tiet_diem' => $item->chi_tiet_diem,
                ];
            })
            ->values()
            ->all();

        try {
            $result = $this->aiClientService->generateCareerReport(
                $hoSo->id,
                $cvProfile,
                $matchingProfiles,
            );
            $data = $result['data'] ?? [];

            $report = TuVanNgheNghiep::create([
                'nguoi_dung_id' => $request->user()->id,
                'ho_so_id' => $hoSo->id,
                'nghe_de_xuat' => $data['nghe_de_xuat'] ?? 'Chưa xác định',
                'muc_do_phu_hop' => $data['muc_do_phu_hop'] ?? 0,
                'goi_y_ky_nang_bo_sung' => $data['goi_y_ky_nang_bo_sung'] ?? null,
                'bao_cao_chi_tiet' => $data['bao_cao_chi_tiet'] ?? null,
                'model_version' => $data['model_version'] ?? ($result['model_version'] ?? 'career_report_v1'),
            ]);
        } catch (RuntimeException $e) {
            return response()->json([
                'success' => false,
                'message' => $e->getMessage(),
            ], 502);
        }

        return response()->json([
            'success' => true,
            'message' => 'Sinh báo cáo tư vấn nghề nghiệp thành công.',
            'data' => $report,
        ]);
    }
}
