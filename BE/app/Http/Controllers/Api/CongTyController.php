<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\CongTy;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

/**
 * CongTyController - Xem công ty (Public)
 *
 * Không yêu cầu đăng nhập.
 *
 * Routes:
 *   GET  /api/v1/cong-tys          - Danh sách công ty (hoạt động)
 *   GET  /api/v1/cong-tys/{id}     - Chi tiết công ty
 */
class CongTyController extends Controller
{
    /**
     * GET /api/v1/cong-tys
     * Danh sách công ty đang hoạt động.
     */
    public function index(Request $request): JsonResponse
    {
        $query = CongTy::with('nganhNghe:id,ten_nganh')
            ->where('trang_thai', CongTy::TRANG_THAI_HOAT_DONG);

        if ($request->filled('search')) {
            $search = $request->search;
            $query->where(function ($q) use ($search) {
                $q->where('ten_cong_ty', 'like', "%{$search}%")
                    ->orWhere('dia_chi', 'like', "%{$search}%");
            });
        }

        if ($request->filled('nganh_nghe_id')) {
            $query->where('nganh_nghe_id', $request->nganh_nghe_id);
        }

        if ($request->filled('quy_mo')) {
            $query->where('quy_mo', $request->quy_mo);
        }

        $query->orderBy('ten_cong_ty', 'asc');

        $perPage = (int) $request->get('per_page', 0);
        if ($perPage > 0) {
            $data = $query->paginate(min($perPage, 100));
        } else {
            $data = $query->get();
        }

        return response()->json([
            'success' => true,
            'data' => $data,
        ]);
    }

    /**
     * GET /api/v1/cong-tys/{id}
     * Chi tiết công ty.
     */
    public function show(int $id): JsonResponse
    {
        $congTy = CongTy::with([
            'nganhNghe:id,ten_nganh',
            'nguoiDung:id,ho_ten,email',
        ])
            ->where('trang_thai', CongTy::TRANG_THAI_HOAT_DONG)
            ->findOrFail($id);

        return response()->json([
            'success' => true,
            'data' => $congTy,
        ]);
    }
}
