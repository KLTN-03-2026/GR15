<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\GiaoDichThanhToan;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class PaymentHistoryController extends Controller
{
    public function index(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'per_page' => ['nullable', 'integer', 'min:1', 'max:50'],
            'loai_giao_dich' => ['nullable', 'string'],
            'trang_thai' => ['nullable', 'string'],
        ]);

        $payments = GiaoDichThanhToan::query()
            ->with('goiDichVu:id,ma_goi,ten_goi')
            ->where('nguoi_dung_id', $request->user()->id)
            ->when(
                !empty($validated['loai_giao_dich']),
                fn ($query) => $query->where('loai_giao_dich', (string) $validated['loai_giao_dich'])
            )
            ->when(
                !empty($validated['trang_thai']),
                fn ($query) => $query->where('trang_thai', (string) $validated['trang_thai'])
            )
            ->latest('id')
            ->paginate((int) ($validated['per_page'] ?? 10));

        return response()->json([
            'success' => true,
            'data' => $payments,
        ]);
    }

    public function show(Request $request, string $maGiaoDichNoiBo): JsonResponse
    {
        $payment = GiaoDichThanhToan::query()
            ->with([
                'goiDichVu:id,ma_goi,ten_goi',
                'viNguoiDung:id,nguoi_dung_id,so_du_hien_tai,so_du_tam_giu',
            ])
            ->where('nguoi_dung_id', $request->user()->id)
            ->where('ma_giao_dich_noi_bo', $maGiaoDichNoiBo)
            ->firstOrFail();

        return response()->json([
            'success' => true,
            'data' => $payment,
        ]);
    }
}
