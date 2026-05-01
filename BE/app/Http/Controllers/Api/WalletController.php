<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\GiaoDichThanhToan;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class WalletController extends Controller
{
    /**
     * Danh sách thanh toán của ứng viên đang đăng nhập
     * GET /v1/ung-vien/payments
     *
     * Query params:
     *   page            - Số trang (mặc định 1)
     *   per_page        - Số bản ghi mỗi trang (mặc định 15)
     *   loai_giao_dich  - Lọc theo loại: topup_wallet | buy_subscription
     *   trang_thai      - Lọc theo trạng thái: pending | thanh_cong | that_bai | huy
     */
    public function payments(Request $request): JsonResponse
    {
        $query = GiaoDichThanhToan::query()
            ->with([
                'goiDichVu:id,ma_goi,ten_goi',
                'viNguoiDung:id,nguoi_dung_id,so_du_hien_tai,so_du_tam_giu',
            ])
            ->where('nguoi_dung_id', $request->user()->id)
            ->orderByDesc('created_at');

        // Lọc theo loại giao dịch
        if ($request->filled('loai_giao_dich')) {
            $query->where('loai_giao_dich', $request->loai_giao_dich);
        }

        // Lọc theo trạng thái
        if ($request->filled('trang_thai')) {
            $query->where('trang_thai', $request->trang_thai);
        }

        $perPage = min((int) $request->get('per_page', 15), 100);
        $payments = $query->paginate($perPage);

        return response()->json([
            'success' => true,
            'data'    => $payments,
        ]);
    }

    /**
     * Chi tiết một giao dịch thanh toán của ứng viên
     * GET /v1/ung-vien/payments/{maGiaoDichNoiBo}
     */
    public function paymentDetail(Request $request, string $maGiaoDichNoiBo): JsonResponse
    {
        $payment = GiaoDichThanhToan::query()
            ->with([
                'goiDichVu:id,ma_goi,ten_goi',
                'viNguoiDung:id,nguoi_dung_id,so_du_hien_tai,so_du_tam_giu',
            ])
            ->where('nguoi_dung_id', $request->user()->id) // chỉ xem giao dịch của chính mình
            ->where('ma_giao_dich_noi_bo', $maGiaoDichNoiBo)
            ->firstOrFail();

        return response()->json([
            'success' => true,
            'data'    => $payment,
        ]);
    }
}
