<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\TuVanNgheNghiep;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class UngVienTuVanNgheNghiepController extends Controller
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

        $query = TuVanNgheNghiep::query()
            ->where('nguoi_dung_id', $user->id)
            ->with(['hoSo:id,tieu_de_ho_so']);

        if ($request->filled('ho_so_id')) {
            $query->where('ho_so_id', (int) $request->input('ho_so_id'));
        }

        $query->orderByDesc('muc_do_phu_hop')
            ->orderByDesc('created_at');

        return response()->json([
            'success' => true,
            'message' => 'Lấy Báo cáo định hướng nghề nghiệp thành công.',
            'data' => $query->paginate((int) $request->get('per_page', 10)),
        ]);
    }
}
