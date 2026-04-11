<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\NguoiDung\CapNhatHoSoRequest;
use App\Http\Requests\NguoiDung\DangKyRequest;
use App\Http\Requests\NguoiDung\DangNhapRequest;
use App\Http\Requests\NguoiDung\DoiMatKhauRequest;
use App\Models\ApiAccessToken;
use App\Models\NguoiDung;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Carbon;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Str;

class AuthController extends Controller
{
    private function frontendUrl(): string
    {
        return rtrim((string) env('FRONTEND_URL', 'http://localhost:5173'), '/');
    }

    private function mapUserData(NguoiDung $nguoiDung): array
    {
        $data = $nguoiDung->toArray();
        $data['ten_vai_tro'] = $nguoiDung->ten_vai_tro;
        $data['da_xac_thuc_email'] = !is_null($nguoiDung->email_verified_at);
        $data['avatar_url'] = $nguoiDung->anh_dai_dien
            ? url('/api/v1/anh-dai-dien?path=' . urlencode($nguoiDung->anh_dai_dien))
            : null;

        return $data;
    }

    public function dangKy(DangKyRequest $request): JsonResponse
    {
        $data = $request->validated();
        $data['vai_tro'] = (int) ($data['vai_tro'] ?? NguoiDung::VAI_TRO_UNG_VIEN);
        $data['trang_thai'] = 1;
        $data['email_verified_at'] = now();

        $nguoiDung = NguoiDung::create($data);

        return response()->json([
            'success' => true,
            'message' => 'Đăng ký tài khoản thành công.',
            'data' => $this->mapUserData($nguoiDung),
        ], 201);
    }

    public function dangNhap(DangNhapRequest $request): JsonResponse
    {
        $nguoiDung = NguoiDung::query()
            ->where('email', $request->input('email'))
            ->first();

        if (!$nguoiDung || !Hash::check($request->input('mat_khau'), $nguoiDung->mat_khau)) {
            return response()->json([
                'success' => false,
                'message' => 'Email hoặc mật khẩu không đúng.',
            ], 401);
        }

        if (!$nguoiDung->isActive()) {
            return response()->json([
                'success' => false,
                'message' => 'Tài khoản đã bị khóa.',
            ], 403);
        }

        $plainTextToken = Str::random(64);

        $nguoiDung->apiTokens()->delete();
        $nguoiDung->apiTokens()->create([
            'token_hash' => hash('sha256', $plainTextToken),
            'last_used_at' => now(),
        ]);

        return response()->json([
            'success' => true,
            'message' => 'Đăng nhập thành công.',
            'data' => [
                'nguoi_dung' => $this->mapUserData($nguoiDung),
                'access_token' => $plainTextToken,
                'token_type' => 'Bearer',
                'vai_tro' => $nguoiDung->ten_vai_tro,
            ],
        ]);
    }

    public function quenMatKhau(Request $request): JsonResponse
    {
        $data = $request->validate([
            'email' => ['required', 'email'],
        ]);

        $nguoiDung = NguoiDung::query()->where('email', $data['email'])->first();

        if (!$nguoiDung) {
            return response()->json([
                'success' => true,
                'message' => 'Nếu email tồn tại trong hệ thống, chúng tôi đã gửi liên kết đặt lại mật khẩu.',
            ]);
        }

        if (!$nguoiDung->isActive()) {
            return response()->json([
                'success' => false,
                'message' => 'Tài khoản đã bị khóa. Vui lòng liên hệ quản trị viên.',
            ], 403);
        }

        $plainToken = Str::random(64);

        DB::table('password_reset_tokens')->updateOrInsert(
            ['email' => $nguoiDung->email],
            [
                'token' => Hash::make($plainToken),
                'created_at' => now(),
            ]
        );

        $resetUrl = $this->frontendUrl() . '/reset-password?email=' . urlencode((string) $nguoiDung->email)
            . '&token=' . urlencode($plainToken);

        return response()->json([
            'success' => true,
            'message' => 'Nếu email tồn tại trong hệ thống, chúng tôi đã gửi liên kết đặt lại mật khẩu.',
            'data' => [
                'email' => $nguoiDung->email,
                'reset_url' => $resetUrl,
            ],
        ]);
    }

    public function datLaiMatKhau(Request $request): JsonResponse
    {
        $data = $request->validate([
            'email' => ['required', 'email'],
            'token' => ['required', 'string'],
            'mat_khau' => ['required', 'string', 'min:6', 'confirmed'],
        ], [
            'mat_khau.confirmed' => 'Mật khẩu xác nhận không khớp.',
        ]);

        $resetRow = DB::table('password_reset_tokens')
            ->where('email', $data['email'])
            ->first();

        if (
            !$resetRow
            || !Hash::check($data['token'], $resetRow->token)
            || Carbon::parse($resetRow->created_at)->addMinutes(60)->isPast()
        ) {
            return response()->json([
                'success' => false,
                'message' => 'Token đặt lại mật khẩu không hợp lệ hoặc đã hết hạn.',
            ], 422);
        }

        $nguoiDung = NguoiDung::query()->where('email', $data['email'])->first();

        if (!$nguoiDung) {
            return response()->json([
                'success' => false,
                'message' => 'Tài khoản không tồn tại.',
            ], 404);
        }

        $nguoiDung->update([
            'mat_khau' => $data['mat_khau'],
        ]);

        $nguoiDung->apiTokens()->delete();
        DB::table('password_reset_tokens')->where('email', $data['email'])->delete();

        return response()->json([
            'success' => true,
            'message' => 'Đặt lại mật khẩu thành công. Vui lòng đăng nhập lại.',
        ]);
    }

    public function dangXuat(Request $request): JsonResponse
    {
        $tokenId = $request->attributes->get('api_access_token_id');

        if ($tokenId) {
            ApiAccessToken::query()->whereKey($tokenId)->delete();
        }

        return response()->json([
            'success' => true,
            'message' => 'Đăng xuất thành công.',
        ]);
    }

    public function hoSo(Request $request): JsonResponse
    {
        $nguoiDung = $request->user();

        if (!$nguoiDung) {
            return response()->json([
                'success' => false,
                'message' => 'Phiên đăng nhập không còn hợp lệ.',
            ], 401);
        }

        return response()->json([
            'success' => true,
            'data' => $this->mapUserData($nguoiDung),
        ]);
    }

    public function capNhatHoSo(CapNhatHoSoRequest $request): JsonResponse
    {
        $nguoiDung = $request->user();

        if (!$nguoiDung) {
            return response()->json([
                'success' => false,
                'message' => 'Phiên đăng nhập không còn hợp lệ.',
            ], 401);
        }

        $data = $request->validated();

        if ($request->hasFile('anh_dai_dien')) {
            if ($nguoiDung->anh_dai_dien) {
                Storage::disk('public')->delete($nguoiDung->anh_dai_dien);
            }

            $data['anh_dai_dien'] = $request->file('anh_dai_dien')->store('anh_dai_dien', 'public');
        }

        $nguoiDung->update($data);

        return response()->json([
            'success' => true,
            'message' => 'Cập nhật hồ sơ thành công.',
            'data' => $this->mapUserData($nguoiDung->fresh()),
        ]);
    }

    public function doiMatKhau(DoiMatKhauRequest $request): JsonResponse
    {
        $nguoiDung = $request->user();

        if (!$nguoiDung) {
            return response()->json([
                'success' => false,
                'message' => 'Phiên đăng nhập không còn hợp lệ.',
            ], 401);
        }

        if (!Hash::check($request->input('mat_khau_cu'), $nguoiDung->mat_khau)) {
            return response()->json([
                'success' => false,
                'message' => 'Mật khẩu cũ không đúng.',
            ], 422);
        }

        $nguoiDung->update([
            'mat_khau' => $request->input('mat_khau_moi'),
        ]);

        $nguoiDung->apiTokens()->delete();

        return response()->json([
            'success' => true,
            'message' => 'Đổi mật khẩu thành công. Vui lòng đăng nhập lại.',
        ]);
    }

    public function avatar(Request $request)
    {
        $path = (string) $request->query('path', '');

        abort_unless($path !== '' && str_starts_with($path, 'anh_dai_dien/'), 404);
        abort_unless(Storage::disk('public')->exists($path), 404);

        return response()->file(Storage::disk('public')->path($path));
    }
}
