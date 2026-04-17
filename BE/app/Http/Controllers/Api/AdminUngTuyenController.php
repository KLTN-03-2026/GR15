<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\UngTuyen;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class AdminUngTuyenController extends Controller
{
    /**
     * GET /api/v1/admin/ung-tuyens
     */
    public function index(Request $request): JsonResponse
    {
        $status = $request->query('trang_thai');
        $companyId = $request->query('cong_ty_id');
        $perPage = $request->query('per_page', 10);

        // Tối ưu N+1 Query
        $query = UngTuyen::with([
            'tinTuyenDung:id,cong_ty_id,tieu_de,trang_thai',
            'tinTuyenDung.congTy:id,ten_cong_ty',
            'hoSo' => function ($q) {
                $q->withTrashed()->with('nguoiDung:id,email,ho_ten');
            }
        ]);

        if ($status) {
            $query->where('trang_thai', $status);
        }

        if ($companyId) {
            $query->whereHas('tinTuyenDung', function ($q) use ($companyId) {
                $q->where('cong_ty_id', $companyId);
            });
        }

        $applications = $query->paginate($perPage);

        return response()->json($applications);
    }

    /**
     * GET /api/v1/admin/ung-tuyens/thong-ke
     */
    public function thongKe(): JsonResponse
    {
        $stats = UngTuyen::selectRaw('trang_thai, count(*) as count')
            ->groupBy('trang_thai')
            ->get()
            ->pluck('count', 'trang_thai');

        return response()->json([
            'chov_duyet' => $stats['cho_duyet'] ?? 0,
            'da_xem' => $stats['da_xem'] ?? 0,
            'phong_van' => $stats['phong_van'] ?? 0,
            'chap_nhan' => $stats['chap_nhan'] ?? 0,
            'tu_choi' => $stats['tu_choi'] ?? 0,
            'total' => UngTuyen::count()
        ]);
    }
}
