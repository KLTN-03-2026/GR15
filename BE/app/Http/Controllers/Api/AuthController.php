<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\NguoiDung\DangKyRequest;
use App\Http\Requests\NguoiDung\DangNhapRequest;
use App\Http\Requests\NguoiDung\DoiMatKhauRequest;
use App\Http\Requests\NguoiDung\CapNhatHoSoRequest;
use App\Models\NguoiDung;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
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
}
