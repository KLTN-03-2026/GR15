<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\TinTuyenDung\TaoTinTuyenDungRequest;
use App\Http\Requests\TinTuyenDung\CapNhatTinTuyenDungRequest;
use App\Models\CongTy;
use App\Models\TinTuyenDung;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

/**
 * NhaTuyenDungTinTuyenDungController - Quyền: Nhà Tuyển Dụng
 */
class NhaTuyenDungTinTuyenDungController extends Controller
{
    /**
     * Lấy ID công ty của NTD đang đăng nhập.
     */
    private function getCongTyId(): ?int
    {
        return CongTy::where('nguoi_dung_id', auth()->id())->value('id');
    }

    /**
     * Danh sách tin của công ty NTD.
     */
    public function index(Request $request): JsonResponse
    {
        $congTyId = $this->getCongTyId();
        if (!$congTyId) {
            return response()->json([
                'success' => false,
                'message' => 'Bạn chưa tạo cấu hình công ty. Vui lòng tạo tài khoản doanh nghiệp trước.',
            ], 404);
        }

        $query = TinTuyenDung::with('nganhNghes:id,ten_nganh')
            ->where('cong_ty_id', $congTyId);

        if ($request->filled('trang_thai')) {
            $query->where('trang_thai', $request->trang_thai);
        }

        if ($request->filled('search')) {
            $search = $request->search;
            $query->where('tieu_de', 'like', "%{$search}%");
        }

        $data = $query->orderBy('created_at', 'desc')->paginate((int) $request->get('per_page', 15));

        return response()->json([
            'success' => true,
            'data' => $data,
        ]);
    }

    /**
     * Tạo tin tuyển dụng mới.
     */
    public function store(TaoTinTuyenDungRequest $request): JsonResponse
    {
        $congTyId = $this->getCongTyId();
        if (!$congTyId) {
            return response()->json([
                'success' => false,
                'message' => 'Bạn cần thiết lập thông tin công ty trước khi tạo tin.',
            ], 403);
        }

        $data = $request->validated();
        $nganhNgheIds = $data['nganh_nghes'];
        unset($data['nganh_nghes']);

        $data['cong_ty_id'] = $congTyId;

        $tin = TinTuyenDung::create($data);
        $tin->nganhNghes()->attach($nganhNgheIds);

        return response()->json([
            'success' => true,
            'message' => 'Tạo tin tuyển dụng thành công.',
            'data' => $tin->load('nganhNghes:id,ten_nganh'),
        ], 201);
    }

    /**
     * Cập nhật tin tuyển dụng.
     */
    public function update(CapNhatTinTuyenDungRequest $request, int $id): JsonResponse
    {
        $congTyId = $this->getCongTyId();
        $tin = TinTuyenDung::where('cong_ty_id', $congTyId)->findOrFail($id);

        $data = $request->validated();

        if (isset($data['nganh_nghes'])) {
            $tin->nganhNghes()->sync($data['nganh_nghes']);
            unset($data['nganh_nghes']);
        }

        $tin->update($data);

        return response()->json([
            'success' => true,
            'message' => 'Cập nhật tin thành công.',
            'data' => $tin->fresh()->load('nganhNghes:id,ten_nganh'),
        ]);
    }

    /**
     * Xem chi tiết tin.
     */
    public function show(int $id): JsonResponse
    {
        $congTyId = $this->getCongTyId();
        $tin = TinTuyenDung::with('nganhNghes:id,ten_nganh')
            ->where('cong_ty_id', $congTyId)
            ->findOrFail($id);

        return response()->json([
            'success' => true,
            'data' => $tin,
        ]);
    }

    /**
     * Bật / tắt hiển thị (đổi trạng thái).
     */
    public function doiTrangThai(int $id): JsonResponse
    {
        $congTyId = $this->getCongTyId();
        $tin = TinTuyenDung::where('cong_ty_id', $congTyId)->findOrFail($id);

        $tin->trang_thai = $tin->trang_thai == 1 ? 0 : 1;
        $tin->save();

        return response()->json([
            'success' => true,
            'message' => 'Chuyển trạng thái thành công.',
            'data' => $tin,
        ]);
    }

    /**
     * Xoá tin.
     */
    public function destroy(int $id): JsonResponse
    {
        $congTyId = $this->getCongTyId();
        $tin = TinTuyenDung::where('cong_ty_id', $congTyId)->findOrFail($id);

        // Các reference (chi_tiet_nganh_nghes, vv) sẽ bị cascade delete
        $tin->delete();

        return response()->json([
            'success' => true,
            'message' => 'Xoá tin tuyển dụng thành công.',
        ]);
    }
}
