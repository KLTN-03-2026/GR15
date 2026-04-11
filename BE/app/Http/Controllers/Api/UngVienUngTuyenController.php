<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\UngTuyen\NopHoSoRequest;
use App\Http\Requests\UngTuyen\XacNhanPhongVanRequest;
use App\Models\TinTuyenDung;
use App\Models\UngTuyen;
use Carbon\Carbon;
use Illuminate\Http\JsonResponse;
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

    private function queryByUserId(int $userId)
    {
        return UngTuyen::query()
            ->whereHas('hoSo', function ($query) use ($userId) {
                $query->withTrashed()->where('nguoi_dung_id', $userId);
            });
    }

    private function loadRelations(UngTuyen $ungTuyen): UngTuyen
    {
        return $ungTuyen->load([
            'tinTuyenDung:id,cong_ty_id,tieu_de,dia_diem_lam_viec,muc_luong,muc_luong_tu,muc_luong_den,trang_thai',
            'tinTuyenDung.congTy:id,ten_cong_ty,logo',
            'hoSo' => function ($query) {
                $query->withTrashed()->select('id', 'nguoi_dung_id', 'tieu_de_ho_so', 'file_cv');
            },
        ]);
    }

    private function isInterviewResponseLocked(UngTuyen $ungTuyen): bool
    {
        return (bool) $ungTuyen->da_rut_don || in_array((int) $ungTuyen->trang_thai, [
            UngTuyen::TRANG_THAI_QUA_PHONG_VAN,
            UngTuyen::TRANG_THAI_TRUNG_TUYEN,
            UngTuyen::TRANG_THAI_TU_CHOI,
        ], true);
    }

    public function index(Request $request): JsonResponse
    {
        $user = $request->user();

        if (!$user) {
            return $this->unauthorizedResponse();
        }

        $withdrawn = $request->boolean('da_rut_don', false);

        $query = $this->queryByUserId($user->id)
            ->whereNotNull('thoi_gian_ung_tuyen')
            ->where('da_rut_don', $withdrawn)
            ->with([
                'tinTuyenDung:id,cong_ty_id,tieu_de,dia_diem_lam_viec,muc_luong,muc_luong_tu,muc_luong_den,trang_thai',
                'tinTuyenDung.congTy:id,ten_cong_ty,logo',
                'hoSo' => function ($subQuery) {
                    $subQuery->withTrashed()->select('id', 'nguoi_dung_id', 'tieu_de_ho_so', 'file_cv');
                },
            ]);

        if ($request->filled('trang_thai')) {
            $query->where('trang_thai', (int) $request->input('trang_thai'));
        }

        $query->orderByDesc('thoi_gian_ung_tuyen');

        return response()->json([
            'success' => true,
            'data' => $query->paginate((int) $request->get('per_page', 10)),
        ]);
    }

    public function store(NopHoSoRequest $request): JsonResponse
    {
        $user = $request->user();

        if (!$user) {
            return $this->unauthorizedResponse();
        }

        $tin = TinTuyenDung::query()->findOrFail((int) $request->input('tin_tuyen_dung_id'));

        if ($tin->trang_thai !== TinTuyenDung::TRANG_THAI_HOAT_DONG || ($tin->ngay_het_han && $tin->ngay_het_han->isPast())) {
            return response()->json([
                'success' => false,
                'message' => 'Tin tuyển dụng đã hết hạn hoặc tạm ngưng.',
            ], 400);
        }

        if ($tin->congTy && $tin->congTy->trang_thai !== 1) {
            return response()->json([
                'success' => false,
                'message' => 'Công ty tuyển dụng đang bị khóa hoặc chưa duyệt.',
            ], 400);
        }

        $tin->loadCount(['acceptedApplications as so_luong_da_nhan']);

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

        $daNop = $this->queryByUserId($user->id)
            ->where('tin_tuyen_dung_id', $tin->id)
            ->whereNotNull('thoi_gian_ung_tuyen')
            ->exists();

        if ($daNop) {
            return response()->json([
                'success' => false,
                'message' => 'Bạn đã nộp hồ sơ vào tin này rồi, không thể nộp thêm.',
            ], 400);
        }

        $ungTuyen = UngTuyen::query()->create([
            'tin_tuyen_dung_id' => $tin->id,
            'ho_so_id' => (int) $request->input('ho_so_id'),
            'thu_xin_viec' => $request->input('thu_xin_viec'),
            'trang_thai' => UngTuyen::TRANG_THAI_CHO_DUYET,
            'thoi_gian_ung_tuyen' => $this->nowUtc(),
        ]);

        return response()->json([
            'success' => true,
            'message' => 'Nộp hồ sơ thành công.',
            'data' => $this->loadRelations($ungTuyen),
        ], 201);
    }

    public function update(Request $request, int $id): JsonResponse
    {
        $user = $request->user();

        if (!$user) {
            return $this->unauthorizedResponse();
        }

        $validated = $request->validate([
            'ho_so_id' => [
                'required',
                'integer',
                'exists:ho_sos,id,deleted_at,NULL,nguoi_dung_id,' . $user->id,
            ],
            'thu_xin_viec' => ['nullable', 'string', 'max:5000'],
        ], [
            'ho_so_id.required' => 'Vui lòng chọn hồ sơ muốn cập nhật.',
            'ho_so_id.exists' => 'Hồ sơ không hợp lệ hoặc không thuộc quyền sở hữu của bạn.',
        ]);

        $ungTuyen = $this->queryByUserId($user->id)
            ->whereKey($id)
            ->whereNotNull('thoi_gian_ung_tuyen')
            ->firstOrFail();

        if ((int) $ungTuyen->trang_thai !== UngTuyen::TRANG_THAI_CHO_DUYET) {
            return response()->json([
                'success' => false,
                'message' => 'Chỉ có thể cập nhật hồ sơ khi đơn vẫn đang chờ duyệt.',
            ], 422);
        }

        $ungTuyen->fill([
            'ho_so_id' => (int) $validated['ho_so_id'],
            'thu_xin_viec' => $validated['thu_xin_viec'] ?: null,
        ])->save();

        return response()->json([
            'success' => true,
            'message' => 'Đã cập nhật hồ sơ ứng tuyển.',
            'data' => $this->loadRelations($ungTuyen->fresh()),
        ]);
    }

    public function xacNhanPhongVan(XacNhanPhongVanRequest $request, int $id): JsonResponse
    {
        $user = $request->user();

        if (!$user) {
            return $this->unauthorizedResponse();
        }

        $ungTuyen = $this->queryByUserId($user->id)
            ->whereKey($id)
            ->whereNotNull('thoi_gian_ung_tuyen')
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
        ])->save();

        return response()->json([
            'success' => true,
            'message' => (int) $ungTuyen->trang_thai_tham_gia_phong_van === UngTuyen::PHONG_VAN_DA_XAC_NHAN
                ? 'Bạn đã xác nhận tham gia phỏng vấn.'
                : 'Bạn đã báo không thể tham gia buổi phỏng vấn này.',
            'data' => $this->loadRelations($ungTuyen->fresh()),
        ]);
    }

    public function rutDon(Request $request, int $id): JsonResponse
    {
        $user = $request->user();

        if (!$user) {
            return $this->unauthorizedResponse();
        }

        $ungTuyen = $this->queryByUserId($user->id)
            ->whereKey($id)
            ->whereNotNull('thoi_gian_ung_tuyen')
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
        ])->save();

        return response()->json([
            'success' => true,
            'message' => 'Đã rút đơn ứng tuyển và chuyển sang mục lưu trữ.',
            'data' => $this->loadRelations($ungTuyen->fresh()),
        ]);
    }
}
