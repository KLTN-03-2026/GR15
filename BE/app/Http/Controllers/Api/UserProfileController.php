<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;

class UserProfileController extends Controller
{
    /**
     * Cập nhật hồ sơ (Role admin hoặc user thường)
     */
    public function capNhatHoSo(Request $request): JsonResponse
    {
        $user = $request->user();
        
        $data = $request->validate([
            'ho_ten' => 'nullable|string|max:255',
            'so_dien_thoai' => 'nullable|string|max:20',
            'avatar' => 'nullable|image|max:2048'
        ]);

        if ($request->hasFile('avatar')) {
            // Lưu avatar vào public disk
            if ($user->avatar && Storage::disk('public')->exists($user->avatar)) {
                Storage::disk('public')->delete($user->avatar);
            }
            $path = $request->file('avatar')->store('avatars', 'public');
            $user->avatar = $path;
        }

        if (isset($data['ho_ten'])) {
            $user->ho_ten = $data['ho_ten'];
        }
        if (isset($data['so_dien_thoai'])) {
            $user->so_dien_thoai = $data['so_dien_thoai'];
        }

        $user->save();

        return response()->json([
            'success' => true,
            'message' => 'Cập nhật hồ sơ thành công',
            'data' => [
                'ho_ten' => $user->ho_ten,
                'so_dien_thoai' => $user->so_dien_thoai,
                'avatar_url' => $user->avatar ? asset('storage/' . $user->avatar) : null
            ]
        ]);
    }
}
