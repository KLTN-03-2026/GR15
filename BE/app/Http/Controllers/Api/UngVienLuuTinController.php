<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\TinTuyenDung;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class UngVienLuuTinController extends Controller
{
    private function unauthorizedResponse(): JsonResponse
    {
        return response()->json([
            'success' => false,
            'message' => 'Phiên đăng nhập không còn hợp lệ.',
        ], 401);
    }

    private function forbiddenResponse(): JsonResponse
    {
        return response()->json([
            'success' => false,
            'message' => 'Chỉ ứng viên mới có thể lưu tin tuyển dụng.',
        ], 403);
    }

    public function index(Request $request): JsonResponse
    {
        $user = $request->user();

        if (!$user) {
            return $this->unauthorizedResponse();
        }

        if (!$user->isUngVien()) {
            return $this->forbiddenResponse();
        }

        $data = $user->tinDaLuus()
            ->with([
                'congTy:id,ten_cong_ty,ma_so_thue,logo,dia_chi',
                'nganhNghes:id,ten_nganh',
            ])
            ->orderBy('luu_tins.created_at', 'desc')
            ->paginate((int) $request->get('per_page', 15));

        return response()->json([
            'success' => true,
            'data' => $data,
        ]);
    }

    public function toggle(Request $request, int $tinId): JsonResponse
    {
        $user = $request->user();

        if (!$user) {
            return $this->unauthorizedResponse();
        }

        if (!$user->isUngVien()) {
            return $this->forbiddenResponse();
        }

        TinTuyenDung::query()->findOrFail($tinId);

        $changes = $user->tinDaLuus()->toggle($tinId);
        $daLuu = count($changes['attached']) > 0;

        return response()->json([
            'success' => true,
            'message' => $daLuu ? 'Đã lưu tin tuyển dụng.' : 'Đã bỏ lưu tin tuyển dụng.',
            'data' => [
                'tin_id' => $tinId,
                'trang_thai_luu' => $daLuu,
            ],
        ], $daLuu ? 201 : 200);
    }
}
