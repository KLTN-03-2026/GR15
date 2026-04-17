<?php

namespace App\Http\Middleware;

use App\Models\CongTy;
use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class KiemTraVaiTroNoiBoCongTy
{
    public function handle(Request $request, Closure $next, string ...$vaiTrosNoiBo): Response
    {
        $nguoiDung = $request->user();

        if (!$nguoiDung) {
            return response()->json([
                'success' => false,
                'message' => 'Chưa xác thực. Vui lòng đăng nhập.',
            ], 401);
        }

        $congTy = $nguoiDung->congTyHienTai();

        if (!$congTy) {
            return response()->json([
                'success' => false,
                'message' => 'Bạn chưa thuộc công ty nào.',
            ], 403);
        }

        $vaiTroNoiBo = $nguoiDung->layVaiTroNoiBoCongTy($congTy);

        if (!$vaiTroNoiBo || !in_array($vaiTroNoiBo, CongTy::danhSachVaiTroNoiBo(), true)) {
            return response()->json([
                'success' => false,
                'message' => 'Bạn không thuộc nhóm HR nội bộ của công ty này.',
            ], 403);
        }

        if (!$vaiTrosNoiBo) {
            return $next($request);
        }

        if (!$nguoiDung->coVaiTroNoiBoCongTy($vaiTrosNoiBo, $congTy)) {
            return response()->json([
                'success' => false,
                'message' => 'Vai trò nội bộ hiện tại không đủ quyền thực hiện hành động này.',
            ], 403);
        }

        return $next($request);
    }
}
