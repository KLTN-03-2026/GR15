<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\TinTuyenDung;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

/**
 * TinTuyenDungController - Public / Ứng viên
 *
 * Routes:
 *   GET /api/v1/tin-tuyen-dungs
 *   GET /api/v1/tin-tuyen-dungs/{id}
 */
class TinTuyenDungController extends Controller
{
    /**
     * Danh sách tin tuyển dụng đang hoạt động, công ty hoạt động, còn hạn.
     */
    public function index(Request $request): JsonResponse
    {
        // Lọc các tin có trạng thái = 1, ngay_het_han >= today, và công ty hoạt động
        $query = TinTuyenDung::with([
                'congTy:id,ten_cong_ty,ma_so_thue,logo,dia_chi',
                'nganhNghes:id,ten_nganh'
            ])
            ->where('trang_thai', TinTuyenDung::TRANG_THAI_HOAT_DONG)
            ->where(function ($q) {
                $q->whereNull('ngay_het_han')
                  ->orWhere('ngay_het_han', '>=', now()->toDateString());
            })
            ->whereHas('congTy', function ($q) {
                $q->where('trang_thai', \App\Models\CongTy::TRANG_THAI_HOAT_DONG);
            });

        // Tìm kiếm chung (tiêu đề, công ty, địa điểm, kỹ năng/mô tả)
        if ($request->filled('search')) {
            $search = $request->search;
            $query->where(function ($q) use ($search) {
                $q->where('tieu_de', 'like', "%{$search}%")
                  ->orWhere('dia_diem_lam_viec', 'like', "%{$search}%")
                  ->orWhere('mo_ta_cong_viec', 'like', "%{$search}%")
                  ->orWhereHas('congTy', function ($q2) use ($search) {
                      $q2->where('ten_cong_ty', 'like', "%{$search}%");
                  });
            });
        }

        // Lọc theo ngành nghề
        if ($request->filled('nganh_nghe_id')) {
            $query->whereHas('nganhNghes', function ($q) use ($request) {
                $q->where('nganh_nghes.id', $request->nganh_nghe_id);
            });
        }

        // Lọc theo tỉnh/thành phố hoặc địa điểm
        if ($request->filled('dia_diem')) {
            $query->where('dia_diem_lam_viec', 'like', '%' . $request->dia_diem . '%');
        }

        $query->orderBy('created_at', 'desc');

        $perPage = (int) $request->get('per_page', 15);
        $data = $query->paginate($perPage);

        return response()->json([
            'success' => true,
            'data' => $data,
        ]);
    }

    /**
     * Chi tiết tin tuyển dụng.
     */
    public function show(int $id): JsonResponse
    {
        $tinTuyenDung = TinTuyenDung::with([
                'congTy:id,ten_cong_ty,ma_so_thue,logo,dia_chi,website,mo_ta,quy_mo',
                'nganhNghes:id,ten_nganh'
            ])
            ->where('trang_thai', TinTuyenDung::TRANG_THAI_HOAT_DONG)
            ->whereHas('congTy', function ($q) {
                $q->where('trang_thai', \App\Models\CongTy::TRANG_THAI_HOAT_DONG);
            })
            ->findOrFail($id);

        // Tăng lượt xem
        $tinTuyenDung->increment('luot_xem');

        return response()->json([
            'success' => true,
            'data' => $tinTuyenDung,
        ]);
    }
}
