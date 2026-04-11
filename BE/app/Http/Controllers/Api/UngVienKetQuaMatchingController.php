<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\KetQuaMatching;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class UngVienKetQuaMatchingController extends Controller
{
    public function index(Request $request): JsonResponse
    {
        $user = $request->user();

        if (!$user) {
            return response()->json([
                'success' => false,
                'message' => 'Phiên đăng nhập không còn hợp lệ.',
            ], 401);
        }

        $query = KetQuaMatching::query()
            ->whereHas('hoSo', function ($subQuery) use ($user) {
                $subQuery->where('nguoi_dung_id', $user->id);
            })
            ->with([
                'tinTuyenDung:id,cong_ty_id,tieu_de,dia_diem_lam_viec,muc_luong,muc_luong_tu,muc_luong_den,hinh_thuc_lam_viec,trang_thai,created_at',
                'tinTuyenDung.congTy:id,ten_cong_ty,logo',
                'hoSo:id,tieu_de_ho_so',
            ])
            ->whereHas('tinTuyenDung', function ($subQuery) {
                $subQuery->where('trang_thai', 1)
                    ->where(function ($nestedQuery) {
                        $nestedQuery->whereNull('ngay_het_han')
                            ->orWhere('ngay_het_han', '>=', now());
                    });
            });

        if ($request->filled('ho_so_id')) {
            $query->where('ho_so_id', (int) $request->input('ho_so_id'));
        }

        $query->orderByDesc('diem_phu_hop')
            ->orderByDesc('thoi_gian_match');

        return response()->json([
            'success' => true,
            'message' => 'Lấy dữ liệu Việc làm phù hợp thành công.',
            'data' => $query->paginate((int) $request->get('per_page', 10)),
        ]);
    }
}
