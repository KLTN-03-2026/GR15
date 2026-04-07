<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\UngTuyen\CapNhatTrangThaiRequest;
use App\Models\UngTuyen;
use App\Notifications\ApplicationStatusNotification;
use App\Notifications\InterviewScheduledNotification;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class NhaTuyenDungUngTuyenController extends Controller
{
    private function isFinalStatus(UngTuyen $ungTuyen): bool
    {
        return in_array((int) $ungTuyen->trang_thai, UngTuyen::TRANG_THAI_CUOI, true);
    }

    private function shouldSendInterviewNotification(UngTuyen $ungTuyen, array $dataUpdate): bool
    {
        $incomingDate = $dataUpdate['ngay_hen_phong_van'] ?? null;
        $incomingMethod = $dataUpdate['hinh_thuc_phong_van'] ?? null;
        $incomingInterviewer = $dataUpdate['nguoi_phong_van'] ?? null;
        $incomingLink = $dataUpdate['link_phong_van'] ?? null;

        if (empty($incomingDate)) {
            return false;
        }

        $current = $ungTuyen->ngay_hen_phong_van?->format('Y-m-d H:i:s');
        $incoming = date('Y-m-d H:i:s', strtotime((string) $incomingDate));

        if ($current !== $incoming) {
            return true;
        }

        return (string) ($ungTuyen->hinh_thuc_phong_van ?? '') !== (string) ($incomingMethod ?? '')
            || (string) ($ungTuyen->nguoi_phong_van ?? '') !== (string) ($incomingInterviewer ?? '')
            || (string) ($ungTuyen->link_phong_van ?? '') !== (string) ($incomingLink ?? '');
    }

    private function dispatchInterviewNotification(UngTuyen $ungTuyen, bool $wasRescheduled = false): void
    {
        $ungTuyen->loadMissing([
            'tinTuyenDung.congTy',
            'hoSo.nguoiDung',
        ]);

        $ungVien = $ungTuyen->hoSo?->nguoiDung;

        if (!$ungVien || !$ungVien->email) {
            return;
        }

        dispatch(function () use ($ungVien, $ungTuyen, $wasRescheduled): void {
            $ungTuyenFresh = $ungTuyen->fresh(['tinTuyenDung.congTy', 'hoSo.nguoiDung']);
            $ungVien->notify(new InterviewScheduledNotification($ungTuyenFresh, $wasRescheduled));
        })->afterResponse();
    }

    private function shouldSendStatusNotification(UngTuyen $ungTuyen, int $trangThaiMoi): bool
    {
        return (int) $ungTuyen->trang_thai !== $trangThaiMoi
            && in_array($trangThaiMoi, UngTuyen::TRANG_THAI_CUOI, true);
    }

    /**
     * Xem danh sách CV ứng viên đã nộp vào CÔNG TY CỦA ĐANG ĐĂNG NHẬP
     */
    public function index(Request $request): JsonResponse
    {
        $user = auth()->user();
        $congTy = $user->congTy;

        if (!$congTy) {
            return response()->json([
                'success' => false,
                'message' => 'Vui lòng thiết lập thông tin công ty trước.'
            ], 403);
        }

        // Lấy danh sách hồ sơ nộp vào các tin tuyển dụng của công ty
        $query = UngTuyen::whereHas('tinTuyenDung', function ($q) use ($congTy) {
            $q->where('cong_ty_id', $congTy->id);
        })->with([
            'tinTuyenDung' => function ($q) {
                $q->select('id', 'tieu_de', 'hinh_thuc_lam_viec', 'trang_thai', 'so_luong_tuyen')
                    ->withCount([
                        'acceptedApplications as so_luong_da_nhan',
                    ]);
            },
            'hoSo' => function ($q) {
                // Bao gồm hồ sơ đã xoá mềm 
                $q->withTrashed()
                  ->select('id', 'nguoi_dung_id', 'tieu_de_ho_so', 'muc_tieu_nghe_nghiep', 'file_cv')
                  ->with('nguoiDung:id,email'); // Chỉ lấy email
            }
        ]);

        // Lọc theo tin tuyển dụng cụ thể (VD chọn xem danh sách của chỉ 1 tin)
        if ($request->has('tin_tuyen_dung_id') && $request->tin_tuyen_dung_id !== '') {
            $query->where('tin_tuyen_dung_id', $request->tin_tuyen_dung_id);
        }

        // Lọc theo trạng thái hồ sơ 
        if ($request->has('trang_thai') && $request->trang_thai !== '') {
            $query->where('trang_thai', $request->trang_thai);
        }

        $query->orderBy('thoi_gian_ung_tuyen', 'desc');

        $ungTuyens = $query->paginate((int) $request->get('per_page', 15));

        return response()->json([
            'success' => true,
            'data' => $ungTuyens
        ]);
    }

    /**
     * Đổi trạng thái xử lý đơn ứng tuyển
     */
    public function updateTrangThai(CapNhatTrangThaiRequest $request, $id): JsonResponse
    {
        $user = auth()->user();
        $congTy = $user->congTy;

        if (!$congTy) {
            return response()->json(['success' => false, 'message' => 'Lỗi công ty'], 403);
        }

        $ungTuyen = UngTuyen::whereHas('tinTuyenDung', function ($q) use ($congTy) {
            $q->where('cong_ty_id', $congTy->id);
        })->findOrFail($id);

        $trangThaiMoi = (int) $request->trang_thai;

        if ($ungTuyen->da_rut_don) {
            return response()->json([
                'success' => false,
                'message' => 'Ứng viên đã rút đơn ứng tuyển nên không thể cập nhật xử lý nữa.',
            ], 422);
        }

        if ($this->isFinalStatus($ungTuyen) && (int) $ungTuyen->trang_thai !== $trangThaiMoi) {
            return response()->json([
                'success' => false,
                'message' => 'Đơn ứng tuyển đã có kết quả cuối nên không thể đổi sang trạng thái khác.',
            ], 422);
        }

        if (
            $trangThaiMoi === UngTuyen::TRANG_THAI_TRUNG_TUYEN
            && (int) $ungTuyen->trang_thai !== UngTuyen::TRANG_THAI_TRUNG_TUYEN
        ) {
            $tin = $ungTuyen->tinTuyenDung()
                ->withCount([
                    'acceptedApplications as so_luong_da_nhan',
                ])
                ->first();

            if ($tin && $tin->so_luong_con_lai <= 0) {
                return response()->json([
                    'success' => false,
                        'message' => 'Tin tuyển dụng đã đủ chỉ tiêu. Không thể đánh dấu trúng tuyển thêm ứng viên.',
                    'data' => [
                        'so_luong_tuyen' => $tin->so_luong_tuyen,
                        'so_luong_da_nhan' => $tin->so_luong_da_nhan,
                        'so_luong_con_lai' => $tin->so_luong_con_lai,
                    ],
                ], 422);
            }
        }

        if (
            $request->filled('ngay_hen_phong_van')
            && !in_array($trangThaiMoi, UngTuyen::TRANG_THAI_CUOI, true)
            && $trangThaiMoi < UngTuyen::TRANG_THAI_DA_HEN_PHONG_VAN
        ) {
            $trangThaiMoi = UngTuyen::TRANG_THAI_DA_HEN_PHONG_VAN;
        }

        $dataUpdate = [
            'trang_thai' => $trangThaiMoi
        ];

        if ($request->has('ngay_hen_phong_van')) {
            $dataUpdate['ngay_hen_phong_van'] = $request->ngay_hen_phong_van;
        }

        if ($request->has('hinh_thuc_phong_van')) {
            $dataUpdate['hinh_thuc_phong_van'] = $request->hinh_thuc_phong_van;
        }

        if ($request->has('nguoi_phong_van')) {
            $dataUpdate['nguoi_phong_van'] = $request->nguoi_phong_van;
        }

        if ($request->has('link_phong_van')) {
            $dataUpdate['link_phong_van'] = $request->link_phong_van;
        }

        if ($request->has('ket_qua_phong_van')) {
            $dataUpdate['ket_qua_phong_van'] = $request->ket_qua_phong_van;
        }

        if ($request->has('ghi_chu')) {
            $dataUpdate['ghi_chu'] = $request->ghi_chu;
        }

        $shouldNotifyInterview = $this->shouldSendInterviewNotification($ungTuyen, $dataUpdate);
        $shouldNotifyStatus = !$shouldNotifyInterview && $this->shouldSendStatusNotification($ungTuyen, $trangThaiMoi);
        $wasRescheduled = !is_null($ungTuyen->ngay_hen_phong_van);

        if ($request->has('ngay_hen_phong_van')) {
            if (empty($dataUpdate['ngay_hen_phong_van'])) {
                $dataUpdate['trang_thai_tham_gia_phong_van'] = null;
                $dataUpdate['thoi_gian_phan_hoi_phong_van'] = null;
            } elseif ($shouldNotifyInterview) {
                $dataUpdate['trang_thai_tham_gia_phong_van'] = UngTuyen::PHONG_VAN_CHO_XAC_NHAN;
                $dataUpdate['thoi_gian_phan_hoi_phong_van'] = null;
            }
        }

        $ungTuyen->update($dataUpdate);

        if ($shouldNotifyInterview || $shouldNotifyStatus) {
            if ($shouldNotifyInterview) {
                $this->dispatchInterviewNotification($ungTuyen, $wasRescheduled);
            } else {
                $ungTuyen->loadMissing([
                    'tinTuyenDung.congTy',
                    'hoSo.nguoiDung',
                ]);

                $ungVien = $ungTuyen->hoSo?->nguoiDung;

                if ($ungVien && $ungVien->email) {
                    dispatch(function () use ($ungVien, $ungTuyen): void {
                        $ungTuyenFresh = $ungTuyen->fresh(['tinTuyenDung.congTy', 'hoSo.nguoiDung']);
                        $ungVien->notify(new ApplicationStatusNotification($ungTuyenFresh));
                    })->afterResponse();
                }
            }
        }

        $message = 'Cập nhật trạng thái vòng phỏng vấn/ứng tuyển thành công.';

        if ($shouldNotifyInterview) {
            $message = 'Cập nhật trạng thái thành công và đã gửi email lịch phỏng vấn cho ứng viên.';
        } elseif ($shouldNotifyStatus) {
            $message = 'Cập nhật trạng thái thành công và đã gửi email thông báo kết quả cho ứng viên.';
        }

        return response()->json([
            'success' => true,
            'message' => $message,
            'data' => $ungTuyen->fresh()->load([
                'tinTuyenDung' => function ($q) {
                    $q->select('id', 'tieu_de', 'hinh_thuc_lam_viec', 'trang_thai', 'so_luong_tuyen')
                        ->withCount([
                            'acceptedApplications as so_luong_da_nhan',
                        ]);
                },
            ])
        ]);
    }

    public function guiLaiEmailPhongVan(Request $request, $id): JsonResponse
    {
        $user = auth()->user();
        $congTy = $user->congTy;

        if (!$congTy) {
            return response()->json([
                'success' => false,
                'message' => 'Vui lòng thiết lập thông tin công ty trước.'
            ], 403);
        }

        $ungTuyen = UngTuyen::whereHas('tinTuyenDung', function ($q) use ($congTy) {
            $q->where('cong_ty_id', $congTy->id);
        })->with(['tinTuyenDung.congTy', 'hoSo.nguoiDung'])->findOrFail($id);

        if ($ungTuyen->da_rut_don) {
            return response()->json([
                'success' => false,
                'message' => 'Ứng viên đã rút đơn nên không thể gửi lại email lịch phỏng vấn.',
            ], 422);
        }

        if ($this->isFinalStatus($ungTuyen)) {
            return response()->json([
                'success' => false,
                'message' => 'Đơn ứng tuyển đã có kết quả cuối nên không thể gửi lại email lịch phỏng vấn.',
            ], 422);
        }

        if (!$ungTuyen->ngay_hen_phong_van) {
            return response()->json([
                'success' => false,
                'message' => 'Ứng tuyển này chưa có lịch phỏng vấn để gửi lại email.',
            ], 422);
        }

        $this->dispatchInterviewNotification($ungTuyen, true);

        return response()->json([
            'success' => true,
            'message' => 'Đã gửi lại email lịch phỏng vấn cho ứng viên.',
        ]);
    }
}
