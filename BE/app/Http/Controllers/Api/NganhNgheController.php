<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\NganhNghe;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class NganhNgheController extends Controller
{
    public function index(Request $request): JsonResponse
    {
        $query = NganhNghe::query()
            ->where('trang_thai', NganhNghe::TRANG_THAI_HIEN_THI);

        if ($request->filled('search')) {
            $search = trim((string) $request->input('search'));
            $query->where(function ($subQuery) use ($search) {
                $subQuery->where('ten_nganh', 'like', "%{$search}%")
                    ->orWhere('mo_ta', 'like', "%{$search}%");
            });
        }

        if ($request->filled('danh_muc_cha_id')) {
            $query->where('danh_muc_cha_id', (int) $request->input('danh_muc_cha_id'));
        }

        if ($request->input('goc') == '1') {
            $query->whereNull('danh_muc_cha_id');
        }

        $query->orderBy('ten_nganh');

        $perPage = (int) $request->get('per_page', 0);
        $data = $perPage > 0 ? $query->paginate(min($perPage, 100)) : $query->get();

        return response()->json([
            'success' => true,
            'data' => $data,
        ]);
    }

    public function show(int $id): JsonResponse
    {
        $nganhNghe = NganhNghe::query()
            ->where('trang_thai', NganhNghe::TRANG_THAI_HIEN_THI)
            ->with([
                'danhMucCha:id,ten_nganh,slug',
                'danhMucCon' => fn ($query) => $query->where('trang_thai', NganhNghe::TRANG_THAI_HIEN_THI)
                    ->select('id', 'ten_nganh', 'slug', 'icon', 'danh_muc_cha_id'),
            ])
            ->findOrFail($id);

        return response()->json([
            'success' => true,
            'data' => $nganhNghe,
        ]);
    }
}
