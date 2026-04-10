<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\TinTuyenDung;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class TinTuyenDungController extends Controller
{
    public function index(Request $request): JsonResponse
    {
        $query = TinTuyenDung::query()
            ->with('congTy:id,ten_cong_ty,logo,dia_chi')
            ->where('trang_thai', TinTuyenDung::TRANG_THAI_HOAT_DONG)
            ->where(function ($builder) {
                $builder->whereNull('ngay_het_han')
                    ->orWhere('ngay_het_han', '>=', now());
            });

        if ($request->filled('search')) {
            $search = trim((string) $request->query('search'));
            $query->where(function ($builder) use ($search) {
                $builder->where('tieu_de', 'like', "%{$search}%")
                    ->orWhere('dia_diem_lam_viec', 'like', "%{$search}%")
                    ->orWhere('mo_ta_cong_viec', 'like', "%{$search}%")
                    ->orWhereHas('congTy', function ($companyQuery) use ($search) {
                        $companyQuery->where('ten_cong_ty', 'like', "%{$search}%");
                    });
            });
        }

        $jobs = $query
            ->orderByDesc('created_at')
            ->paginate(min((int) $request->query('per_page', 12), 50));

        return response()->json([
            'success' => true,
            'data' => $jobs,
        ]);
    }

    public function show(int $id): JsonResponse
    {
        $job = TinTuyenDung::query()
            ->with('congTy:id,ten_cong_ty,logo,dia_chi,website')
            ->where('trang_thai', TinTuyenDung::TRANG_THAI_HOAT_DONG)
            ->findOrFail($id);

        return response()->json([
            'success' => true,
            'data' => $job,
        ]);
    }
}
