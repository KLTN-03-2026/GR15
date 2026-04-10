<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\HoSo;
use App\Models\KetQuaMatching;
use App\Models\TinTuyenDung;
use App\Models\UngTuyen;
use App\Services\Ai\AiClientService;
use Carbon\Carbon;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use RuntimeException;

class CoverLetterController extends Controller
{
    public function __construct(
        private readonly AiClientService $aiClientService
    ) {
    }

    private function nowUtc(): Carbon
    {
        return Carbon::now('Asia/Ho_Chi_Minh')->utc();
    }

    public function generate(Request $request): JsonResponse
    {
        $request->validate([
            'ho_so_id' => ['required', 'integer', 'exists:ho_sos,id'],
            'tin_tuyen_dung_id' => ['required', 'integer', 'exists:tin_tuyen_dungs,id'],
        ]);

        $hoSo = HoSo::with('parsing')
            ->where('nguoi_dung_id', $request->user()->id)
            ->findOrFail((int) $request->ho_so_id);

        $tin = TinTuyenDung::with(['parsing', 'kyNangYeuCaus.kyNang', 'congTy'])
            ->findOrFail((int) $request->tin_tuyen_dung_id);

        $tin->loadCount([
            'acceptedApplications as so_luong_da_nhan',
        ]);

        if ($tin->so_luong_con_lai <= 0) {
            return response()->json([
                'success' => false,
                'message' => 'Tin tuyển dụng này đã tuyển đủ chỉ tiêu, không thể tạo thêm thư xin việc mới.',
                'data' => [
                    'so_luong_tuyen' => $tin->so_luong_tuyen,
                    'so_luong_da_nhan' => $tin->so_luong_da_nhan,
                    'so_luong_con_lai' => $tin->so_luong_con_lai,
                ],
            ], 422);
        }

        $matching = KetQuaMatching::query()
            ->where('ho_so_id', $hoSo->id)
            ->where('tin_tuyen_dung_id', $tin->id)
            ->latest('updated_at')
            ->first();

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

        $jdProfile = [
            'tieu_de' => $tin->tieu_de,
            'ten_cong_ty' => $tin->congTy?->ten_cong_ty,
            'cap_bac' => $tin->cap_bac,
            'kinh_nghiem_yeu_cau' => $tin->kinh_nghiem_yeu_cau,
            'trinh_do_yeu_cau' => $tin->trinh_do_yeu_cau,
            'raw_text' => $tin->parsing?->raw_text ?? $tin->mo_ta_cong_viec,
            'parsed_skills' => $tin->parsing?->parsed_skills_json ?? [],
            'required_skills' => $tin->kyNangYeuCaus
                ->map(function ($item) {
                    return [
                        'skill_name' => $item->kyNang?->ten_ky_nang,
                        'bat_buoc' => (bool) $item->bat_buoc,
                        'trong_so' => $item->trong_so ?? 1.0,
                    ];
                })
                ->filter(fn ($item) => !empty($item['skill_name']))
                ->values()
                ->all(),
        ];

        $matchingProfile = $matching ? [
            'diem_phu_hop' => $matching->diem_phu_hop,
            'diem_ky_nang' => $matching->diem_ky_nang,
            'diem_kinh_nghiem' => $matching->diem_kinh_nghiem,
            'diem_hoc_van' => $matching->diem_hoc_van,
            'chi_tiet_diem' => $matching->chi_tiet_diem ?? [],
            'matched_skills_json' => $matching->matched_skills_json ?? [],
            'missing_skills_json' => $matching->missing_skills_json ?? [],
            'explanation' => $matching->explanation,
        ] : [
            // AI service yêu cầu matching_profile luôn là object/dictionary.
            'diem_phu_hop' => null,
            'diem_ky_nang' => null,
            'diem_kinh_nghiem' => null,
            'diem_hoc_van' => null,
            'chi_tiet_diem' => [],
            'matched_skills_json' => [],
            'missing_skills_json' => [],
            'explanation' => null,
        ];

        try {
            $result = $this->aiClientService->generateCoverLetter(
                $hoSo->id,
                $tin->id,
                $cvProfile,
                $jdProfile,
                $matchingProfile,
            );
            $data = $result['data'] ?? [];
            $draft = $data['thu_xin_viec_ai'] ?? $data['content'] ?? null;

            $ungTuyenDaNop = UngTuyen::query()
                ->where('tin_tuyen_dung_id', (int) $request->tin_tuyen_dung_id)
                ->whereHas('hoSo', function ($query) use ($request) {
                    $query->withTrashed()->where('nguoi_dung_id', $request->user()->id);
                })
                ->whereNotNull('thoi_gian_ung_tuyen')
                ->first();

            if ($ungTuyenDaNop) {
                return response()->json([
                    'success' => false,
                    'message' => 'Bạn đã nộp hồ sơ vào tin này rồi, không thể tạo thêm thư xin việc mới.',
                ], 422);
            }

            $ungTuyen = UngTuyen::query()
                ->where('tin_tuyen_dung_id', (int) $request->tin_tuyen_dung_id)
                ->whereHas('hoSo', function ($query) use ($request) {
                    $query->withTrashed()->where('nguoi_dung_id', $request->user()->id);
                })
                ->whereNull('thoi_gian_ung_tuyen')
                ->latest('updated_at')
                ->first()
                ?? new UngTuyen([
                    'tin_tuyen_dung_id' => (int) $request->tin_tuyen_dung_id,
                ]);

            $ungTuyen->ho_so_id = $hoSo->id;
            $ungTuyen->thu_xin_viec_ai = $draft;
            $ungTuyen->thu_xin_viec = null;
            if (!$ungTuyen->exists) {
                $ungTuyen->trang_thai = UngTuyen::TRANG_THAI_CHO_DUYET;
            }
            $ungTuyen->save();
        } catch (RuntimeException $e) {
            $message = $e->getMessage();

            if (str_contains($message, 'matching_profile')) {
                $message = 'Hệ thống đang đồng bộ dữ liệu matching cho CV này. Vui lòng thử sinh thư AI lại sau ít phút.';
            }

            return response()->json([
                'success' => false,
                'message' => $message,
            ], 502);
        }

        return response()->json([
            'success' => true,
            'message' => 'Tạo nháp thư xin việc thành công.',
            'data' => [
                'ung_tuyen_id' => $ungTuyen->id,
                'thu_xin_viec_ai' => $ungTuyen->thu_xin_viec_ai,
            ],
        ]);
    }

    public function confirm(Request $request, int $id): JsonResponse
    {
        $request->validate([
            'thu_xin_viec' => ['nullable', 'string'],
        ]);

        $ungTuyen = UngTuyen::where('id', $id)
            ->whereHas('hoSo', function ($query) use ($request) {
                $query->withTrashed()->where('nguoi_dung_id', $request->user()->id);
            })
            ->firstOrFail();

        $finalContent = trim((string) ($request->thu_xin_viec ?? $ungTuyen->thu_xin_viec_ai ?? ''));
        if ($finalContent === '') {
            return response()->json([
                'success' => false,
                'message' => 'Chưa có nội dung thư xin việc để xác nhận.',
            ], 422);
        }

        $ungTuyen->thu_xin_viec = $finalContent;
        $ungTuyen->thoi_gian_ung_tuyen ??= $this->nowUtc();
        if ($ungTuyen->trang_thai === null) {
            $ungTuyen->trang_thai = UngTuyen::TRANG_THAI_CHO_DUYET;
        }

        $tin = TinTuyenDung::query()
            ->withCount([
                'acceptedApplications as so_luong_da_nhan',
            ])
            ->findOrFail((int) $ungTuyen->tin_tuyen_dung_id);

        if ($tin->so_luong_con_lai <= 0) {
            return response()->json([
                'success' => false,
                'message' => 'Tin tuyển dụng này đã tuyển đủ chỉ tiêu, không thể xác nhận thêm hồ sơ mới.',
                'data' => [
                    'so_luong_tuyen' => $tin->so_luong_tuyen,
                    'so_luong_da_nhan' => $tin->so_luong_da_nhan,
                    'so_luong_con_lai' => $tin->so_luong_con_lai,
                ],
            ], 422);
        }

        $ungTuyen->save();

        return response()->json([
            'success' => true,
            'message' => 'Đã xác nhận thư xin việc thành bản chính thức.',
            'data' => [
                'ung_tuyen_id' => $ungTuyen->id,
                'thu_xin_viec' => $ungTuyen->thu_xin_viec,
                'thu_xin_viec_ai' => $ungTuyen->thu_xin_viec_ai,
            ],
        ]);
    }
}
