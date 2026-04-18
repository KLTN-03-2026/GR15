<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

/**
 * Middleware kiểm tra quyền truy cập theo vai trò.
 *
 * Cách dùng trong routes:
 *   ->middleware('role:admin')
 *   ->middleware('role:nha_tuyen_dung')
 *   ->middleware('role:admin,nha_tuyen_dung')   // Cho phép nhiều vai trò
 */
class KiemTraVaiTro
{
    public function handle(Request $request, Closure $next, string ...$vaiTros): Response
    {
        $nguoiDung = $request->user();

        if (!$nguoiDung) {
            return response()->json([
                'success' => false,
                'message' => 'Chưa xác thực. Vui lòng đăng nhập.',
            ], 401);
        }

        if (!$nguoiDung->isActive()) {
            return response()->json([
                'success' => false,
                'message' => 'Tài khoản đã bị khoá. Vui lòng liên hệ quản trị viên.',
            ], 403);
        }

        $vaiTroMap = [
            'admin' => \App\Models\NguoiDung::VAI_TRO_ADMIN,
            'nha_tuyen_dung' => \App\Models\NguoiDung::VAI_TRO_NHA_TUYEN_DUNG,
            'ung_vien' => \App\Models\NguoiDung::VAI_TRO_UNG_VIEN,
        ];

        foreach ($vaiTros as $vaiTro) {
            if (isset($vaiTroMap[$vaiTro]) && $nguoiDung->vai_tro === $vaiTroMap[$vaiTro]) {
                return $next($request);
            }
        }

        return response()->json([
            'success' => false,
            'message' => 'Bạn không có quyền thực hiện hành động này.',
        ], 403);
    }
}
