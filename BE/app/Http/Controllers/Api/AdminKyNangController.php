<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\KyNang;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class AdminKyNangController extends Controller
{
    /**
     * GET /api/v1/admin/ky-nangs
     */
    public function index(Request $request): JsonResponse
    {
        $search = $request->query('search');
        $sortBy = $request->query('sort_by', 'id');
        $sortDir = $request->query('sort_dir', 'desc');
        $perPage = $request->query('per_page', 15);

        $query = KyNang::query();

        if ($search) {
            $query->where(function ($q) use ($search) {
                $q->where('ten_ky_nang', 'like', "%{$search}%")
                  ->orWhere('mo_ta', 'like', "%{$search}%");
            });
        }

        $query->orderBy($sortBy, $sortDir);

        return response()->json($query->paginate($perPage));
    }

    /**
     * POST /api/v1/admin/ky-nangs
     */
    public function store(Request $request): JsonResponse
    {
        $data = $request->validate([
            'ten_ky_nang' => 'required|string|max:255|unique:ky_nangs',
            'mo_ta' => 'nullable|string',
            'icon' => 'nullable|string'
        ]);

        $kyNang = KyNang::create($data);

        return response()->json([
            'success' => true,
            'message' => 'Tạo kỹ năng thành công',
            'data' => $kyNang
        ]);
    }

    /**
     * PUT /api/v1/admin/ky-nangs/{id}
     */
    public function update(Request $request, $id): JsonResponse
    {
        $kyNang = KyNang::findOrFail($id);

        $data = $request->validate([
            'ten_ky_nang' => 'required|string|max:255|unique:ky_nangs,ten_ky_nang,' . $id,
            'mo_ta' => 'nullable|string',
            'icon' => 'nullable|string'
        ]);

        $kyNang->update($data);

        return response()->json([
            'success' => true,
            'message' => 'Cập nhật kỹ năng thành công',
            'data' => $kyNang
        ]);
    }

    /**
     * DELETE /api/v1/admin/ky-nangs/{id}
     */
    public function destroy($id): JsonResponse
    {
        $kyNang = KyNang::findOrFail($id);
        $kyNang->delete();

        return response()->json([
            'success' => true,
            'message' => 'Xoá kỹ năng thành công'
        ]);
    }

    /**
     * GET /api/v1/admin/ky-nangs/thong-ke
     */
    public function thongKe(): JsonResponse
    {
        return response()->json([
            'total' => KyNang::count(),
            'have_icon' => KyNang::whereNotNull('icon')->count(),
            'have_description' => KyNang::whereNotNull('mo_ta')->count()
        ]);
    }
}
