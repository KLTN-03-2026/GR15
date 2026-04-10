<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\NguoiDung\DangKyRequest;
use App\Http\Requests\NguoiDung\DangNhapRequest;
use App\Http\Requests\NguoiDung\DoiMatKhauRequest;
use App\Http\Requests\NguoiDung\CapNhatHoSoRequest;
use App\Models\NguoiDung;
use Illuminate\Auth\Events\PasswordReset;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Password;
use Illuminate\Support\Facades\Storage;

/**
 * AuthController - Xác thực & quản lý hồ sơ cá nhân
 *
 * Áp dụng cho: Admin, Nhà tuyển dụng, Ứng viên
 */
class AuthController extends Controller
{
    /**
     * POST /api/dang-ky
     * Đăng ký tài khoản mới (ứng viên hoặc nhà tuyển dụng).
     */
    public function dangKy(DangKyRequest $request): JsonResponse
    {
        $data = $request->validated();
        $data['vai_tro'] = $data['vai_tro'] ?? NguoiDung::VAI_TRO_UNG_VIEN;

        $nguoiDung = NguoiDung::create($data);

        return response()->json([
            'success' => true,
            'message' => 'Đăng ký tài khoản thành công.',
            'data' => $nguoiDung,
        ], 201);
    }

    /**
     * POST /api/dang-nhap
     * Đăng nhập - áp dụng cho tất cả vai trò.
     */
    public function dangNhap(DangNhapRequest $request): JsonResponse
    {
        $nguoiDung = NguoiDung::where('email', $request->email)->first();

        if (!$nguoiDung || !Hash::check($request->mat_khau, $nguoiDung->mat_khau)) {
            return response()->json([
                'success' => false,
                'message' => 'Email hoặc mật khẩu không đúng.',
            ], 401);
        }

        if (!$nguoiDung->isActive()) {
            return response()->json([
                'success' => false,
                'message' => 'Tài khoản đã bị khoá. Vui lòng liên hệ quản trị viên.',
            ], 403);
        }

        // Xoá token cũ, tạo token mới
        $nguoiDung->tokens()->delete();
        $token = $nguoiDung->createToken('auth_token')->plainTextToken;

        return response()->json([
            'success' => true,
            'message' => 'Đăng nhập thành công.',
            'data' => [
                'nguoi_dung' => $nguoiDung,
                'access_token' => $token,
                'token_type' => 'Bearer',
                'vai_tro' => $nguoiDung->ten_vai_tro,
            ],
        ]);
    }

    /**
     * POST /api/dang-xuat
     * Đăng xuất - thu hồi token hiện tại.
     */
    public function dangXuat(Request $request): JsonResponse
    {
        $request->user()->currentAccessToken()->delete();

        return response()->json([
            'success' => true,
            'message' => 'Đăng xuất thành công.',
        ]);
    }

    /**
     * GET /api/ho-so
     * Xem thông tin hồ sơ của người dùng đang đăng nhập.
     */
    public function hoSo(Request $request): JsonResponse
    {
        return response()->json([
            'success' => true,
            'data' => $request->user(),
        ]);
    }

    /**
     * PUT /api/ho-so
     * Cập nhật hồ sơ cá nhân.
     */
    public function capNhatHoSo(CapNhatHoSoRequest $request): JsonResponse
    {
        $nguoiDung = $request->user();
        $data = $request->validated();

        if ($request->hasFile('anh_dai_dien')) {
            if ($nguoiDung->anh_dai_dien) {
                Storage::disk('public')->delete($nguoiDung->anh_dai_dien);
            }
            $data['anh_dai_dien'] = $request->file('anh_dai_dien')
                ->store('anh_dai_dien', 'public');
        }

        $nguoiDung->update($data);

        return response()->json([
            'success' => true,
            'message' => 'Cập nhật hồ sơ thành công.',
            'data' => $nguoiDung->fresh(),
        ]);
    }

    /**
     * POST /api/doi-mat-khau
     * Đổi mật khẩu - thu hồi tất cả token, bắt đăng nhập lại.
     */
    public function doiMatKhau(DoiMatKhauRequest $request): JsonResponse
    {
        $nguoiDung = $request->user();

        if (!Hash::check($request->mat_khau_cu, $nguoiDung->mat_khau)) {
            return response()->json([
                'success' => false,
                'message' => 'Mật khẩu cũ không đúng.',
            ], 422);
        }

        $nguoiDung->update(['mat_khau' => $request->mat_khau_moi]);
        $nguoiDung->tokens()->delete();

        return response()->json([
            'success' => true,
            'message' => 'Đổi mật khẩu thành công. Vui lòng đăng nhập lại.',
        ]);
    }

    /**
     * POST /api/v1/quen-mat-khau
     * Tạo token đặt lại mật khẩu và gửi email.
     */
    public function quenMatKhau(Request $request): JsonResponse
    {
        $data = $request->validate([
            'email' => ['required', 'email'],
        ]);

        $nguoiDung = NguoiDung::where('email', $data['email'])->first();

        // Không tiết lộ email có tồn tại hay không (security by design)
        if (!$nguoiDung) {
            return response()->json([
                'success' => true,
                'message' => 'Nếu email tồn tại trong hệ thống, chúng tôi đã gửi liên kết đặt lại mật khẩu.',
            ]);
        }

        if (!$nguoiDung->isActive()) {
            return response()->json([
                'success' => false,
                'message' => 'Tài khoản đã bị khoá. Vui lòng liên hệ quản trị viên.',
            ], 403);
        }

        try {
            $token = Password::broker()->createToken($nguoiDung);

            // Gửi email sau response (không block response)
            dispatch(function () use ($nguoiDung, $token): void {
                $nguoiDung->fresh()?->sendPasswordResetNotification($token);
            })->afterResponse();
        } catch (\Throwable $exception) {
            return response()->json([
                'success' => false,
                'message' => 'Không thể gửi email đặt lại mật khẩu vào lúc này.',
            ], 500);
        }

        return response()->json([
            'success' => true,
            'message' => 'Nếu email tồn tại trong hệ thống, chúng tôi đã gửi liên kết đặt lại mật khẩu.',
        ]);
    }

    /**
     * POST /api/v1/dat-lai-mat-khau
     * Đặt lại mật khẩu bằng token đã cấp (từ email).
     */
    public function datLaiMatKhau(Request $request): JsonResponse
    {
        $data = $request->validate([
            'email'    => ['required', 'email'],
            'token'    => ['required', 'string'],
            'mat_khau' => ['required', 'string', 'min:6', 'confirmed'],
        ], [
            'mat_khau.confirmed' => 'Mật khẩu xác nhận không khớp.',
        ]);

        $status = Password::broker()->reset(
            [
                'email'                 => $data['email'],
                'token'                 => $data['token'],
                'password'              => $data['mat_khau'],
                'password_confirmation' => $request->input('mat_khau_confirmation'),
            ],
            function (NguoiDung $nguoiDung, string $password): void {
                $nguoiDung->forceFill(['mat_khau' => $password])->save();
                $nguoiDung->tokens()->delete(); // Thu hồi tất cả token cũ
                event(new PasswordReset($nguoiDung));
            }
        );

        if ($status !== Password::PASSWORD_RESET) {
            return response()->json([
                'success' => false,
                'message' => 'Token đặt lại mật khẩu không hợp lệ hoặc đã hết hạn.',
            ], 422);
        }

        return response()->json([
            'success' => true,
            'message' => 'Đặt lại mật khẩu thành công. Vui lòng đăng nhập lại.',
        ]);
    }
}
