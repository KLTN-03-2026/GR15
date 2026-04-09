<?php

namespace App\Http\Controllers\Api\Admin;

use App\Http\Controllers\Controller;
use App\Http\Requests\TinTuyenDung\TaoTinTuyenDungRequest;
use App\Http\Requests\TinTuyenDung\CapNhatTinTuyenDungRequest;
use App\Models\TinTuyenDung;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

/**
 * AdminTinTuyenDungController - Admin quản lý tin tuyển dụng toàn hệ thống
 */
class AdminTinTuyenDungController extends Controller
{
    /**
     * Danh sách tất cả tin
     */
    public function index(Request $request): JsonResponse
    {
        $query = TinTuyenDung::with([
            'congTy:id,ten_cong_ty,ma_so_thue',
            'nganhNghes:id,ten_nganh'
        ]);

        if ($request->filled('search')) {
            $search = $request->search;
            $query->where(function ($q) use ($search) {
                $q->where('tieu_de', 'like', "%{$search}%")
                  ->orWhereHas('congTy', function ($q2) use ($search) {
                      $q2->where('ten_cong_ty', 'like', "%{$search}%");
                  });
            });
        }

        if ($request->filled('cong_ty_id')) {
            $query->where('cong_ty_id', $request->cong_ty_id);
        }

        if ($request->filled('trang_thai')) {
            $query->where('trang_thai', $request->trang_thai);
        }

        $data = $query->orderBy('created_at', 'desc')->paginate((int) $request->get('per_page', 15));

        return response()->json([
            'success' => true,
            'data' => $data,
        ]);
    }

    /**
     * Tạo thay NTD (Lưu ý Request cần truyền thêm cong_ty_id)
     */
    public function store(TaoTinTuyenDungRequest $request): JsonResponse
    {
        $data = $request->validated();
        
        $cong_ty_id = $request->input('cong_ty_id');
        if (!$cong_ty_id) {
            return response()->json([
                'message' => 'Bắt buộc chọn cong_ty_id khi admin tạo tin.'
            ], 422);
        }
        $data['cong_ty_id'] = $cong_ty_id;

        $nganhNgheIds = $data['nganh_nghes'];
        unset($data['nganh_nghes']);

        $tin = TinTuyenDung::create($data);
        $tin->nganhNghes()->attach($nganhNgheIds);

        return response()->json([
            'success' => true,
            'message' => 'Admin tạo tin thành công.',
            'data' => $tin->load(['nganhNghes:id,ten_nganh', 'congTy:id,ten_cong_ty']),
        ], 201);
    }

    /**
     * Chi tiết tin (Admin)
     */
    public function show(int $id): JsonResponse
    {
        $tin = TinTuyenDung::with([
            'congTy:id,ten_cong_ty',
            'nganhNghes:id,ten_nganh'
        ])->findOrFail($id);

        return response()->json([
            'success' => true,
            'data' => $tin,
        ]);
    }

    /**
     * Cập nhật tin (Admin biên tập)
     */
    public function update(CapNhatTinTuyenDungRequest $request, int $id): JsonResponse
    {
        $tin = TinTuyenDung::findOrFail($id);
        $data = $request->validated();

        if (isset($data['nganh_nghes'])) {
            $tin->nganhNghes()->sync($data['nganh_nghes']);
            unset($data['nganh_nghes']);
        }

        $tin->update($data);

        return response()->json([
            'success' => true,
            'message' => 'Admin cập nhật thành công.',
            'data' => $tin->fresh()->load('nganhNghes:id,ten_nganh'),
        ]);
    }

    /**
     * Cập nhật trạng thái tin (Admin duyệt / huỷ / khóa tin)
     */
    public function doiTrangThai(int $id): JsonResponse
    {
        $tin = TinTuyenDung::findOrFail($id);
        
        $tin->trang_thai = $tin->trang_thai == 1 ? 0 : 1;
        $tin->save();

        return response()->json([
            'success' => true,
            'message' => 'Admin đã chuyển trạng thái tin.',
            'data' => $tin,
        ]);
    }

    /**
     * Xóa hoàn toàn
     */
    public function destroy(int $id): JsonResponse
    {
        $tin = TinTuyenDung::findOrFail($id);
        $tin->delete();

        return response()->json([
            'success' => true,
            'message' => 'Admin xoá tin thành công.',
        ]);
    }

    /**
     * Thống kê
     */
    public function thongKe(): JsonResponse
    {
        $total = TinTuyenDung::count();
        $hoatDong = TinTuyenDung::where('trang_thai', 1)->count();
        $tamNgung = TinTuyenDung::where('trang_thai', 0)->count();

        return response()->json([
            'success' => true,
            'data' => [
                'tong_tin' => $total,
                'hoat_dong' => $hoatDong,
                'tam_ngung' => $tamNgung,
            ],
        ]);
    }
}
