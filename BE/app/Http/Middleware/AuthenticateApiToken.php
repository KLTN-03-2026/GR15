<?php

namespace App\Http\Middleware;

use App\Models\ApiAccessToken;
use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class AuthenticateApiToken
{
    public function handle(Request $request, Closure $next): Response
    {
        $token = $request->bearerToken();

        if (!$token) {
            return response()->json([
                'success' => false,
                'message' => 'Chưa xác thực. Vui lòng đăng nhập.',
            ], 401);
        }

        $accessToken = ApiAccessToken::query()
            ->where('token_hash', hash('sha256', $token))
            ->with('nguoiDung')
            ->first();

        if (!$accessToken || !$accessToken->nguoiDung || !$accessToken->nguoiDung->isActive()) {
            return response()->json([
                'success' => false,
                'message' => 'Phiên đăng nhập không còn hợp lệ.',
            ], 401);
        }

        $accessToken->forceFill(['last_used_at' => now()])->save();

        $request->attributes->set('api_access_token_id', $accessToken->id);
        $request->setUserResolver(fn () => $accessToken->nguoiDung);

        return $next($request);
    }
}
