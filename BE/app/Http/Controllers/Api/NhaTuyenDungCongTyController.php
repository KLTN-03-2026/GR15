<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\CongTy\TaoCongTyRequest;
use App\Http\Requests\CongTy\CapNhatCongTyRequest;
use App\Models\CongTy;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Storage;

/**
 * NhaTuyenDungCongTyController - NTD quản lý công ty của mình
 *
 * Vai trò: Nhà tuyển dụng (vai_tro = 1)
 * Mỗi NTD có thể tạo 1 công ty duy nhất.
 *
 * Routes:
 *   GET   /api/v1/nha-tuyen-dung/cong-ty        - Xem công ty của mình
 *   POST  /api/v1/nha-tuyen-dung/cong-ty        - Tạo công ty
 *   PUT   /api/v1/nha-tuyen-dung/cong-ty        - Cập nhật công ty
 */
class NhaTuyenDungCongTyController extends Controller
{
    private function mapCompanyData(CongTy $congTy): array
    {
        $data = $congTy->toArray();
        $data['logo_url'] = $congTy->logo
            ? url('/api/v1/cong-ty-logo?path=' . urlencode($congTy->logo))
            : null;

        return $data;
    }

    /**
     * GET /api/v1/nha-tuyen-dung/cong-ty
     * Xem công ty của NTD đang đăng nhập.
     */
    public function show(): JsonResponse
    {
        $congTy = CongTy::with('nganhNghe:id,ten_nganh')
            ->where('nguoi_dung_id', auth()->id())
            ->first();

        if (!$congTy) {
            return response()->json([
                'success' => false,
                'message' => 'Bạn chưa tạo thông tin công ty.',
            ], 404);
        }

        return response()->json([
            'success' => true,
            'data' => $this->mapCompanyData($congTy),
        ]);
    }

    /**
     * POST /api/v1/nha-tuyen-dung/cong-ty
     * Tạo công ty (mỗi NTD chỉ 1 công ty).
     */
    public function store(TaoCongTyRequest $request): JsonResponse
    {
        $nguoiDungId = auth()->id();

        // Kiểm tra đã có công ty chưa
        $exists = CongTy::where('nguoi_dung_id', $nguoiDungId)->exists();
        if ($exists) {
            return response()->json([
                'success' => false,
                'message' => 'Bạn đã tạo công ty rồi. Hãy cập nhật thay vì tạo mới.',
            ], 422);
        }

        $data = $request->validated();
        $data['nguoi_dung_id'] = $nguoiDungId;

        if ($request->hasFile('logo')) {
            $data['logo'] = $request->file('logo')->store('cong_ty_logos', 'public');
        }

        $congTy = CongTy::create($data);

        return response()->json([
            'success' => true,
            'message' => 'Tạo công ty thành công.',
            'data' => $this->mapCompanyData($congTy->load('nganhNghe:id,ten_nganh')),
        ], 201);
    }

    /**
     * PUT /api/v1/nha-tuyen-dung/cong-ty
     * Cập nhật công ty của mình.
     */
    public function update(CapNhatCongTyRequest $request): JsonResponse
    {
        $congTy = CongTy::where('nguoi_dung_id', auth()->id())->first();

        if (!$congTy) {
            return response()->json([
                'success' => false,
                'message' => 'Bạn chưa tạo thông tin công ty.',
            ], 404);
        }

        $data = $request->validated();

        if ($request->hasFile('logo')) {
            if ($congTy->logo) {
                Storage::disk('public')->delete($congTy->logo);
            }

            $data['logo'] = $request->file('logo')->store('cong_ty_logos', 'public');
        }

        $congTy->update($data);

        return response()->json([
            'success' => true,
            'message' => 'Cập nhật công ty thành công.',
            'data' => $this->mapCompanyData($congTy->fresh()->load('nganhNghe:id,ten_nganh')),
        ]);
    }
}
