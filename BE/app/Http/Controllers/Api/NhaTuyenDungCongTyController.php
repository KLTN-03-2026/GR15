<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Api\Concerns\ResolvesEmployerCompany;
use App\Http\Controllers\Controller;
use App\Http\Requests\CongTy\TaoCongTyRequest;
use App\Http\Requests\CongTy\CapNhatCongTyRequest;
use App\Models\CongTy;
use App\Models\NguoiDung;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
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
    use ResolvesEmployerCompany;

    private function mapCompanyData(CongTy $congTy): array
    {
        $user = $this->getAuthenticatedEmployer();
        $congTy->loadMissing([
            'nganhNghe:id,ten_nganh',
            'thanhViens:id,ho_ten,email,so_dien_thoai,anh_dai_dien',
        ]);
        $congTy->loadCount('nguoiDungTheoDois');

        $data = $congTy->toArray();
        $data['logo_url'] = $congTy->logo
            ? url('/api/v1/cong-ty-logo?path=' . urlencode($congTy->logo))
            : null;
        $data['tong_so_hr'] = $congTy->thanhViens->count();
        $data['so_nguoi_theo_doi'] = $congTy->nguoi_dung_theo_dois_count ?? 0;
        $data['la_chu_so_huu'] = $this->isCompanyOwner($user, $congTy);
        $data['vai_tro_noi_bo_hien_tai'] = $user?->layVaiTroNoiBoCongTy($congTy);
        $data['ten_vai_tro_noi_bo_hien_tai'] = CongTy::nhanVaiTroNoiBo($data['vai_tro_noi_bo_hien_tai']);
        $data['quyen_noi_bo'] = CongTy::quyenTheoVaiTroNoiBo($data['vai_tro_noi_bo_hien_tai']);
        $data['thanh_viens'] = $congTy->thanhViens->map(function (NguoiDung $member) {
            $payload = $member->toArray();
            $payload['vai_tro_noi_bo'] = $member->pivot?->vai_tro_noi_bo;
            $payload['ten_vai_tro_noi_bo'] = CongTy::nhanVaiTroNoiBo($member->pivot?->vai_tro_noi_bo);
            $payload['la_chu_so_huu'] = $member->pivot?->vai_tro_noi_bo === CongTy::VAI_TRO_NOI_BO_OWNER;
            $payload['avatar_url'] = $member->anh_dai_dien
                ? url('/api/v1/anh-dai-dien?path=' . urlencode($member->anh_dai_dien))
                : null;

            return $payload;
        })->values()->all();

        return $data;
    }

    /**
     * GET /api/v1/nha-tuyen-dung/cong-ty
     * Xem công ty của NTD đang đăng nhập.
     */
    public function show(): JsonResponse
    {
        $congTy = $this->getCurrentEmployerCompany();

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

        if ($this->getCurrentEmployerCompany()) {
            return response()->json([
                'success' => false,
                'message' => 'Bạn đã thuộc một công ty rồi. Hãy cập nhật thay vì tạo mới.',
            ], 422);
        }

        $data = $request->validated();
        $data['nguoi_dung_id'] = $nguoiDungId;

        if ($request->hasFile('logo')) {
            $data['logo'] = $request->file('logo')->store('cong_ty_logos', 'public');
        }

        $congTy = CongTy::create($data);
        $congTy->thanhViens()->syncWithoutDetaching([
            $nguoiDungId => [
                'vai_tro_noi_bo' => 'owner',
                'duoc_tao_boi' => $nguoiDungId,
                'created_at' => now(),
                'updated_at' => now(),
            ],
        ]);

        return response()->json([
            'success' => true,
            'message' => 'Tạo công ty thành công.',
            'data' => $this->mapCompanyData($congTy),
        ], 201);
    }

    /**
     * PUT /api/v1/nha-tuyen-dung/cong-ty
     * Cập nhật công ty của mình.
     */
    public function update(CapNhatCongTyRequest $request): JsonResponse
    {
        $congTy = $this->getCurrentEmployerCompany();

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
            'data' => $this->mapCompanyData($congTy->fresh()),
        ]);
    }

    public function members(): JsonResponse
    {
        $congTy = $this->getCurrentEmployerCompany();

        if (!$congTy) {
            return response()->json([
                'success' => false,
                'message' => 'Bạn chưa thuộc công ty nào.',
            ], 404);
        }

        return response()->json([
            'success' => true,
            'data' => [
                'cong_ty_id' => $congTy->id,
                'la_chu_so_huu' => $this->isCompanyOwner($this->getAuthenticatedEmployer(), $congTy),
                'vai_tro_noi_bo_options' => CongTy::VAI_TRO_NOI_BO_LABELS,
                'thanh_viens' => $this->mapCompanyData($congTy)['thanh_viens'],
            ],
        ]);
    }

    public function addMember(Request $request): JsonResponse
    {
        $congTy = $this->getCurrentEmployerCompany();
        $user = $this->getAuthenticatedEmployer();

        if (!$congTy || !$user) {
            return response()->json([
                'success' => false,
                'message' => 'Bạn chưa thuộc công ty nào.',
            ], 404);
        }

        if (!$this->isCompanyOwner($user, $congTy)) {
            return response()->json([
                'success' => false,
                'message' => 'Chỉ chủ sở hữu công ty mới có thể quản lý thành viên HR.',
            ], 403);
        }

        $data = $request->validate([
            'email' => ['required', 'email', 'max:150'],
            'vai_tro_noi_bo' => ['nullable', 'string', 'in:' . implode(',', array_filter(CongTy::danhSachVaiTroNoiBo(), fn ($role) => $role !== CongTy::VAI_TRO_NOI_BO_OWNER))],
        ]);

        $member = NguoiDung::where('email', $data['email'])->first();

        if (!$member) {
            return response()->json([
                'success' => false,
                'message' => 'Không tìm thấy tài khoản HR với email này. Vui lòng để HR đăng ký trước.',
            ], 404);
        }

        if (!$member->isNhaTuyenDung()) {
            return response()->json([
                'success' => false,
                'message' => 'Tài khoản này không phải nhà tuyển dụng.',
            ], 422);
        }

        if ((int) $member->id === (int) $user->id) {
            return response()->json([
                'success' => false,
                'message' => 'Bạn đã là thành viên của công ty này.',
            ], 422);
        }

        $existingCompany = $member->congTyHienTai();
        if ($existingCompany && (int) $existingCompany->id !== (int) $congTy->id) {
            return response()->json([
                'success' => false,
                'message' => 'Tài khoản HR này đã thuộc một công ty khác.',
            ], 422);
        }

        if ($congTy->thanhViens()->where('nguoi_dungs.id', $member->id)->exists()) {
            return response()->json([
                'success' => false,
                'message' => 'HR này đã thuộc công ty rồi.',
            ], 422);
        }

        $congTy->thanhViens()->attach($member->id, [
            'vai_tro_noi_bo' => $data['vai_tro_noi_bo'] ?? CongTy::VAI_TRO_NOI_BO_RECRUITER,
            'duoc_tao_boi' => $user->id,
            'created_at' => now(),
            'updated_at' => now(),
        ]);

        return response()->json([
            'success' => true,
            'message' => 'Đã thêm HR vào công ty.',
            'data' => [
                'cong_ty' => $this->mapCompanyData($congTy->fresh()),
            ],
        ], 201);
    }

    public function updateMemberRole(Request $request, int $memberId): JsonResponse
    {
        $congTy = $this->getCurrentEmployerCompany();
        $user = $this->getAuthenticatedEmployer();

        if (!$congTy || !$user) {
            return response()->json([
                'success' => false,
                'message' => 'Bạn chưa thuộc công ty nào.',
            ], 404);
        }

        if (!$this->isCompanyOwner($user, $congTy)) {
            return response()->json([
                'success' => false,
                'message' => 'Chỉ chủ sở hữu công ty mới có thể cập nhật vai trò HR.',
            ], 403);
        }

        $data = $request->validate([
            'vai_tro_noi_bo' => ['required', 'string', 'in:' . implode(',', array_filter(CongTy::danhSachVaiTroNoiBo(), fn ($role) => $role !== CongTy::VAI_TRO_NOI_BO_OWNER))],
        ], [
            'vai_tro_noi_bo.required' => 'Vui lòng chọn vai trò nội bộ.',
            'vai_tro_noi_bo.in' => 'Vai trò nội bộ không hợp lệ.',
        ]);

        $member = $congTy->thanhViens()
            ->where('nguoi_dungs.id', $memberId)
            ->first();

        if (!$member) {
            return response()->json([
                'success' => false,
                'message' => 'Không tìm thấy HR trong công ty.',
            ], 404);
        }

        if (($member->pivot?->vai_tro_noi_bo ?? '') === CongTy::VAI_TRO_NOI_BO_OWNER) {
            return response()->json([
                'success' => false,
                'message' => 'Không thể thay đổi vai trò của chủ sở hữu công ty.',
            ], 422);
        }

        $congTy->thanhViens()->updateExistingPivot($memberId, [
            'vai_tro_noi_bo' => $data['vai_tro_noi_bo'],
            'updated_at' => now(),
        ]);

        return response()->json([
            'success' => true,
            'message' => 'Đã cập nhật vai trò nội bộ.',
            'data' => [
                'cong_ty' => $this->mapCompanyData($congTy->fresh()),
            ],
        ]);
    }

    public function removeMember(int $memberId): JsonResponse
    {
        $congTy = $this->getCurrentEmployerCompany();
        $user = $this->getAuthenticatedEmployer();

        if (!$congTy || !$user) {
            return response()->json([
                'success' => false,
                'message' => 'Bạn chưa thuộc công ty nào.',
            ], 404);
        }

        if (!$this->isCompanyOwner($user, $congTy)) {
            return response()->json([
                'success' => false,
                'message' => 'Chỉ chủ sở hữu công ty mới có thể quản lý thành viên HR.',
            ], 403);
        }

        $member = $congTy->thanhViens()
            ->where('nguoi_dungs.id', $memberId)
            ->first();

        if (!$member) {
            return response()->json([
                'success' => false,
                'message' => 'Không tìm thấy HR trong công ty.',
            ], 404);
        }

        if (($member->pivot?->vai_tro_noi_bo ?? '') === CongTy::VAI_TRO_NOI_BO_OWNER) {
            return response()->json([
                'success' => false,
                'message' => 'Không thể gỡ chủ sở hữu công ty khỏi danh sách thành viên.',
            ], 422);
        }

        $congTy->thanhViens()->detach($memberId);

        return response()->json([
            'success' => true,
            'message' => 'Đã gỡ HR khỏi công ty.',
            'data' => [
                'cong_ty' => $this->mapCompanyData($congTy->fresh()),
            ],
        ]);
    }
}
