<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\UngTuyen\NopHoSoRequest;
use App\Http\Requests\UngTuyen\XacNhanPhongVanRequest;
use App\Models\TinTuyenDung;
use App\Models\UngTuyen;
use Carbon\Carbon;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;

class UngVienUngTuyenController extends Controller
{
    private function nowUtc(): Carbon
    {
        return Carbon::now('Asia/Ho_Chi_Minh')->utc();
    }

    private function unauthorizedResponse(): JsonResponse
    {
        return response()->json([
            'success' => false,
            'message' => 'Phiên đăng nhập không còn hợp lệ.',
        ], 401);
    }

    private function isInterviewResponseLocked(UngTuyen $ungTuyen): bool
    {
        return (bool) $ungTuyen->da_rut_don || in_array((int) $ungTuyen->trang_thai, [
            UngTuyen::TRANG_THAI_QUA_PHONG_VAN,
            UngTuyen::TRANG_THAI_TRUNG_TUYEN,
            UngTuyen::TRANG_THAI_TU_CHOI,
        ], true);
    }

    /**
     * Xem danh sách các công việc đã nộp hồ sơ
     */
    public function index(Request $request): JsonResponse
    {
        $userId = auth()->id();

        if (!$userId) {
            return $this->unauthorizedResponse();
        }

        $withdrawn = $request->boolean('da_rut_don', false);

        // Query các ứng tuyển thông qua hồ sơ của user hiện tại
        $query = UngTuyen::whereHas('hoSo', function ($q) use ($userId) {
            // Bao gồm cả hoSo đã soft delete
            $q->withTrashed()->where('nguoi_dung_id', $userId);
        })
        ->whereNotNull('thoi_gian_ung_tuyen')
        ->where('da_rut_don', $withdrawn)
        ->with([
            'tinTuyenDung:id,cong_ty_id,tieu_de,dia_diem_lam_viec,muc_luong,trang_thai',
            'tinTuyenDung.congTy:id,ten_cong_ty,logo',
            'hoSo' => function ($q) {
                // Bao gồm cả hồ sơ bị xóa
                $q->withTrashed()->select('id', 'nguoi_dung_id', 'tieu_de_ho_so', 'file_cv');
            }
        ]);

        // Lọc theo trạng thái ứng tuyển (nếu có)
        if ($request->has('trang_thai') && $request->trang_thai !== '') {
            $query->where('trang_thai', $request->trang_thai);
        }

        $query->orderBy('thoi_gian_ung_tuyen', 'desc');

        $ungTuyens = $query->paginate((int) $request->get('per_page', 10));

        return response()->json([
            'success' => true,
            'data' => $ungTuyens
        ]);
    }

    /**
     * Nộp hồ sơ vào 1 tin tuyển dụng
     */
    public function store(NopHoSoRequest $request): JsonResponse
    {
        $userId = auth()->id();

        if (!$userId) {
            return $this->unauthorizedResponse();
        }

        $tinId = $request->tin_tuyen_dung_id;
        $hoSoId = (int) $request->ho_so_id;

        // 1. Kiểm tra tin tuyển dụng có còn hoạt động không
        $tin = TinTuyenDung::find($tinId);
        if ($tin->trang_thai != 1 || ($tin->ngay_het_han && \Carbon\Carbon::parse($tin->ngay_het_han)->isPast())) {
            return response()->json([
                'success' => false,
                'message' => 'Tin tuyển dụng đã hết hạn hoặc tạm ngưng.'
            ], 400);
        }

        // 2. Kiểm tra cty có đang hoạt động không
        if ($tin->congTy && $tin->congTy->trang_thai != 1) {
            return response()->json([
                'success' => false,
                'message' => 'Công ty tuyển dụng đang bị khóa hoặc chưa duyệt.'
            ], 400);
        }

        $tin->loadCount([
            'acceptedApplications as so_luong_da_nhan',
        ]);

        if ($tin->so_luong_con_lai <= 0) {
            return response()->json([
                'success' => false,
                'message' => 'Tin tuyển dụng này đã tuyển đủ chỉ tiêu.',
                'data' => [
                    'so_luong_tuyen' => $tin->so_luong_tuyen,
                    'so_luong_da_nhan' => $tin->so_luong_da_nhan,
                    'so_luong_con_lai' => $tin->so_luong_con_lai,
                ],
            ], 422);
        }

        // 3. Nếu đã có nháp cover letter cho tin này thì tái sử dụng nháp đó.
        $ungTuyenNhaps = UngTuyen::where('tin_tuyen_dung_id', $tinId)
            ->whereHas('hoSo', function ($q) use ($userId) {
                $q->withTrashed()->where('nguoi_dung_id', $userId);
            })
            ->whereNull('thoi_gian_ung_tuyen')
            ->orderByDesc('updated_at')
            ->get();

        $ungTuyenNhap = $ungTuyenNhaps->first(function (UngTuyen $item) {
            return !empty($item->thu_xin_viec_ai) || empty($item->thu_xin_viec);
        });

        if ($ungTuyenNhap) {
            $ungTuyenNhap->fill([
                'ho_so_id' => $hoSoId,
                'thu_xin_viec' => $request->thu_xin_viec ?: $ungTuyenNhap->thu_xin_viec_ai,
                'trang_thai' => UngTuyen::TRANG_THAI_CHO_DUYET,
                'thoi_gian_ung_tuyen' => $this->nowUtc(),
            ]);
            $ungTuyenNhap->save();
            $ungTuyenNhap->load([
                'tinTuyenDung:id,tieu_de',
                'hoSo:id,tieu_de_ho_so'
            ]);

            return response()->json([
                'success' => true,
                'message' => 'Nộp hồ sơ thành công!',
                'data' => $ungTuyenNhap
            ], 201);
        }

        // 4. Kiểm tra xem người dùng này ĐÃ nộp hồ sơ hoàn chỉnh vào tin này CHƯA
        // (Dù nộp bằng hồ sơ khác cũng không cho, 1 tài khoản chỉ nộp 1 lần/tin)
        $daNop = UngTuyen::where('tin_tuyen_dung_id', $tinId)
            ->whereHas('hoSo', function ($q) use ($userId) {
                $q->withTrashed()->where('nguoi_dung_id', $userId);
            })
            ->whereNotNull('thoi_gian_ung_tuyen')
            ->exists();

        if ($daNop) {
            return response()->json([
                'success' => false,
                'message' => 'Bạn đã nộp hồ sơ vào tin này rồi, không thể nộp thêm.'
            ], 400);
        }

        // Tạo ứng tuyển
        $ungTuyen = UngTuyen::create([
            'tin_tuyen_dung_id' => $tinId,
            'ho_so_id' => $hoSoId,
            'thu_xin_viec' => $request->thu_xin_viec,
            'trang_thai' => UngTuyen::TRANG_THAI_CHO_DUYET,
            'thoi_gian_ung_tuyen' => $this->nowUtc(),
        ]);

        // Load relationship trả về
        $ungTuyen->load([
            'tinTuyenDung:id,tieu_de',
            'hoSo:id,tieu_de_ho_so'
        ]);

        return response()->json([
            'success' => true,
            'message' => 'Nộp hồ sơ thành công!',
            'data' => $ungTuyen
        ], 201);
    }

    /**
     * Cập nhật CV/thư xin việc cho đơn đã nộp.
     */
    public function update(Request $request, int $id): JsonResponse
    {
        if (!auth()->id()) {
            return $this->unauthorizedResponse();
        }

        $validated = $request->validate([
            'ho_so_id' => [
                'required',
                'integer',
                'exists:ho_sos,id,deleted_at,NULL,nguoi_dung_id,' . auth()->id()
            ],
            'thu_xin_viec' => ['nullable', 'string', 'max:5000'],
        ], [
            'ho_so_id.required' => 'Vui lòng chọn hồ sơ muốn cập nhật.',
            'ho_so_id.exists' => 'Hồ sơ không hợp lệ hoặc không thuộc quyền sở hữu của bạn.',
        ]);

        $ungTuyen = UngTuyen::query()
            ->where('id', $id)
            ->whereHas('hoSo', function ($query) {
                $query->withTrashed()->where('nguoi_dung_id', auth()->id());
            })
            ->whereNotNull('thoi_gian_ung_tuyen')
            ->firstOrFail();

        if ($ungTuyen->trang_thai !== UngTuyen::TRANG_THAI_CHO_DUYET) {
            return response()->json([
                'success' => false,
                'message' => 'Chỉ có thể cập nhật hồ sơ khi đơn vẫn đang chờ duyệt.',
            ], 422);
        }

        $ungTuyen->fill([
            'ho_so_id' => (int) $validated['ho_so_id'],
            'thu_xin_viec' => $validated['thu_xin_viec'] ?: null,
        ]);
        $ungTuyen->save();

        $ungTuyen->load([
            'tinTuyenDung:id,cong_ty_id,tieu_de,dia_diem_lam_viec,muc_luong,trang_thai',
            'tinTuyenDung.congTy:id,ten_cong_ty,logo',
            'hoSo' => function ($q) {
                $q->withTrashed()->select('id', 'nguoi_dung_id', 'tieu_de_ho_so', 'file_cv');
            }
        ]);

        return response()->json([
            'success' => true,
            'message' => 'Đã cập nhật hồ sơ ứng tuyển.',
            'data' => $ungTuyen,
        ]);
    }

    public function xacNhanPhongVan(XacNhanPhongVanRequest $request, int $id): JsonResponse
    {
        $userId = auth()->id();

        if (!$userId) {
            return $this->unauthorizedResponse();
        }

        $ungTuyen = UngTuyen::query()
            ->where('id', $id)
            ->whereHas('hoSo', function ($query) use ($userId) {
                $query->withTrashed()->where('nguoi_dung_id', $userId);
            })
            ->whereNotNull('thoi_gian_ung_tuyen')
            ->with([
                'tinTuyenDung:id,cong_ty_id,tieu_de,dia_diem_lam_viec,muc_luong,trang_thai',
                'tinTuyenDung.congTy:id,ten_cong_ty,logo',
                'hoSo' => function ($q) {
                    $q->withTrashed()->select('id', 'nguoi_dung_id', 'tieu_de_ho_so', 'file_cv');
                },
            ])
            ->firstOrFail();

        if (!$ungTuyen->ngay_hen_phong_van) {
            return response()->json([
                'success' => false,
                'message' => 'Ứng tuyển này chưa có lịch phỏng vấn để xác nhận.',
            ], 422);
        }

        if ($this->isInterviewResponseLocked($ungTuyen)) {
            return response()->json([
                'success' => false,
                'message' => 'Đơn ứng tuyển này đã được chuyển sang giai đoạn xử lý tiếp theo nên không thể phản hồi lịch phỏng vấn nữa.',
            ], 422);
        }

        if ($ungTuyen->ngay_hen_phong_van->isPast()) {
            return response()->json([
                'success' => false,
                'message' => 'Lịch phỏng vấn đã qua nên không thể cập nhật xác nhận tham gia nữa.',
            ], 422);
        }

        $ungTuyen->fill([
            'trang_thai_tham_gia_phong_van' => (int) $request->input('trang_thai_tham_gia_phong_van'),
            'thoi_gian_phan_hoi_phong_van' => $this->nowUtc(),
        ]);
        $ungTuyen->save();

        $message = (int) $ungTuyen->trang_thai_tham_gia_phong_van === UngTuyen::PHONG_VAN_DA_XAC_NHAN
            ? 'Bạn đã xác nhận tham gia phỏng vấn.'
            : 'Bạn đã báo không thể tham gia buổi phỏng vấn này.';

        return response()->json([
            'success' => true,
            'message' => $message,
            'data' => $ungTuyen->fresh([
                'tinTuyenDung:id,cong_ty_id,tieu_de,dia_diem_lam_viec,muc_luong,trang_thai',
                'tinTuyenDung.congTy:id,ten_cong_ty,logo',
                'hoSo' => function ($q) {
                    $q->withTrashed()->select('id', 'nguoi_dung_id', 'tieu_de_ho_so', 'file_cv');
                },
            ]),
        ]);
    }

    public function rutDon(Request $request, int $id): JsonResponse
    {
        $userId = auth()->id();

        if (!$userId) {
            return $this->unauthorizedResponse();
        }

        $ungTuyen = UngTuyen::query()
            ->where('id', $id)
            ->whereHas('hoSo', function ($query) use ($userId) {
                $query->withTrashed()->where('nguoi_dung_id', $userId);
            })
            ->whereNotNull('thoi_gian_ung_tuyen')
            ->with([
                'tinTuyenDung:id,cong_ty_id,tieu_de,dia_diem_lam_viec,muc_luong,trang_thai',
                'tinTuyenDung.congTy:id,ten_cong_ty,logo',
                'hoSo' => function ($q) {
                    $q->withTrashed()->select('id', 'nguoi_dung_id', 'tieu_de_ho_so', 'file_cv');
                },
            ])
            ->firstOrFail();

        if ($ungTuyen->da_rut_don) {
            return response()->json([
                'success' => false,
                'message' => 'Đơn ứng tuyển này đã được rút trước đó.',
            ], 422);
        }

        if (in_array((int) $ungTuyen->trang_thai, UngTuyen::TRANG_THAI_CUOI, true)) {
            return response()->json([
                'success' => false,
                'message' => 'Đơn ứng tuyển đã có kết quả cuối nên không thể rút nữa.',
            ], 422);
        }

        if ((int) $ungTuyen->trang_thai_tham_gia_phong_van !== UngTuyen::PHONG_VAN_KHONG_THAM_GIA) {
            return response()->json([
                'success' => false,
                'message' => 'Chỉ có thể rút đơn sau khi bạn đã phản hồi không tham gia phỏng vấn.',
            ], 422);
        }

        $ungTuyen->fill([
            'da_rut_don' => true,
            'thoi_gian_rut_don' => $this->nowUtc(),
        ]);
        $ungTuyen->save();

        return response()->json([
            'success' => true,
            'message' => 'Đã rút đơn ứng tuyển và chuyển sang mục lưu trữ.',
            'data' => $ungTuyen->fresh([
                'tinTuyenDung:id,cong_ty_id,tieu_de,dia_diem_lam_viec,muc_luong,trang_thai',
                'tinTuyenDung.congTy:id,ten_cong_ty,logo',
                'hoSo' => function ($q) {
                    $q->withTrashed()->select('id', 'nguoi_dung_id', 'tieu_de_ho_so', 'file_cv');
                },
            ]),
        ]);
    }

    public function xacNhanPhongVanQuaEmail(Request $request, int $id, string $action): RedirectResponse
    {
        if (!$request->hasValidSignature()) {
            return redirect($this->buildInterviewResponseRedirectUrl('invalid', $id));
        }

        $ungTuyen = UngTuyen::query()
            ->with([
                'hoSo' => function ($query) {
                    $query->withTrashed()->with('nguoiDung');
                },
            ])
            ->findOrFail($id);

        $ownerId = (int) ($ungTuyen->hoSo?->nguoiDung?->id ?? 0);
        $expectedOwnerId = (int) $request->integer('user');

        if (!$ownerId || $ownerId !== $expectedOwnerId) {
            return redirect($this->buildInterviewResponseRedirectUrl('invalid', $id));
        }

        if (!$ungTuyen->ngay_hen_phong_van) {
            return redirect($this->buildInterviewResponseRedirectUrl('missing_schedule', $id));
        }

        if ($this->isInterviewResponseLocked($ungTuyen)) {
            return redirect($this->buildInterviewResponseRedirectUrl('locked', $id));
        }

        if ($ungTuyen->ngay_hen_phong_van->isPast()) {
            return redirect($this->buildInterviewResponseRedirectUrl('expired', $id));
        }

        $normalizedAction = strtolower(trim($action));
        $status = match ($normalizedAction) {
            'accept' => UngTuyen::PHONG_VAN_DA_XAC_NHAN,
            'decline' => UngTuyen::PHONG_VAN_KHONG_THAM_GIA,
            default => null,
        };

        if ($status === null) {
            return redirect($this->buildInterviewResponseRedirectUrl('invalid', $id));
        }

        $ungTuyen->fill([
            'trang_thai_tham_gia_phong_van' => $status,
            'thoi_gian_phan_hoi_phong_van' => $this->nowUtc(),
        ]);
        $ungTuyen->save();

        return redirect($this->buildInterviewResponseRedirectUrl(
            $status === UngTuyen::PHONG_VAN_DA_XAC_NHAN ? 'accepted' : 'declined',
            $id
        ));
    }

    private function buildInterviewResponseRedirectUrl(string $status, int $applicationId): string
    {
        $frontEndUrl = rtrim((string) env('FRONTEND_URL', 'http://localhost:5173'), '/');

        return $frontEndUrl . '/applications?interview_response=' . urlencode($status)
            . '&application_id=' . urlencode((string) $applicationId);
    }
}
