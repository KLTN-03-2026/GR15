<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\CongTy;
use App\Models\TinTuyenDung;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class TinTuyenDungController extends Controller
{
    private function publicQuery()
    {
        return TinTuyenDung::query()
            ->with([
                'congTy:id,ten_cong_ty,ma_so_thue,logo,dia_chi,website,mo_ta,quy_mo,trang_thai',
                'nganhNghes:id,ten_nganh',
            ])
            ->withCount([
                'acceptedApplications as so_luong_da_nhan',
            ])
            ->where('trang_thai', TinTuyenDung::TRANG_THAI_HOAT_DONG)
            ->where(function ($query) {
                $query->whereNull('ngay_het_han')
                    ->orWhere('ngay_het_han', '>=', now());
            })
            ->whereHas('congTy', fn ($query) => $query->where('trang_thai', CongTy::TRANG_THAI_HOAT_DONG));
    }

    public function index(Request $request): JsonResponse
    {
        $query = $this->publicQuery();

        if ($request->filled('search')) {
            $search = trim((string) $request->input('search'));
            $query->where(function ($subQuery) use ($search) {
                $subQuery->where('tieu_de', 'like', "%{$search}%")
                    ->orWhere('dia_diem_lam_viec', 'like', "%{$search}%")
                    ->orWhere('mo_ta_cong_viec', 'like', "%{$search}%")
                    ->orWhereHas('congTy', fn ($companyQuery) => $companyQuery->where('ten_cong_ty', 'like', "%{$search}%"));
            });
        }

        if ($request->filled('nganh_nghe_id')) {
            $nganhNgheId = (int) $request->input('nganh_nghe_id');
            $query->whereHas('nganhNghes', fn ($subQuery) => $subQuery->where('nganh_nghes.id', $nganhNgheId));
        }

        if ($request->filled('dia_diem')) {
            $query->where('dia_diem_lam_viec', 'like', '%' . $request->input('dia_diem') . '%');
        }

        $query->orderByDesc('created_at');

        $perPage = (int) $request->get('per_page', 15);
        $data = $query->paginate(max(1, min($perPage, 50)));

        return response()->json([
            'success' => true,
            'data' => $data,
        ]);
    }

    public function show(int $id): JsonResponse
    {
        $tinTuyenDung = $this->publicQuery()->findOrFail($id);
        $tinTuyenDung->increment('luot_xem');
        $tinTuyenDung = $this->publicQuery()->findOrFail($id);

        return response()->json([
            'success' => true,
            'data' => $tinTuyenDung,
        ]);
    }
}
