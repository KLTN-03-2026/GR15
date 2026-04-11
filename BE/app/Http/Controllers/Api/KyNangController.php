<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\KyNang;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class KyNangController extends Controller
{
    public function index(Request $request): JsonResponse
    {
        $query = KyNang::query();

        if ($request->filled('search')) {
            $search = trim((string) $request->input('search'));
            $query->where('ten_ky_nang', 'like', "%{$search}%");
        }

        $query->orderBy('ten_ky_nang');

        $perPage = (int) $request->get('per_page', 0);
        $data = $perPage > 0 ? $query->paginate(min($perPage, 100)) : $query->get();

        return response()->json([
            'success' => true,
            'data' => $data,
        ]);
    }

    public function show(int $id): JsonResponse
    {
        return response()->json([
            'success' => true,
            'data' => KyNang::query()->findOrFail($id),
        ]);
    }
}
