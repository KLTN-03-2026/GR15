<?php

namespace App\Http\Controllers\Api;

use App\Events\FollowedCompanyJobActivated;
use App\Http\Controllers\Api\Concerns\ResolvesEmployerCompany;
use App\Http\Controllers\Controller;
use App\Http\Requests\TinTuyenDung\TaoTinTuyenDungRequest;
use App\Http\Requests\TinTuyenDung\CapNhatTinTuyenDungRequest;
use App\Models\CongTy;
use App\Models\TinTuyenDung;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

/**
 * NhaTuyenDungTinTuyenDungController - Quyền: Nhà Tuyển Dụng
 */
class NhaTuyenDungTinTuyenDungController extends Controller
{
    use ResolvesEmployerCompany;

    private function resolveValidHrPhuTrachId(?int $memberId, CongTy $congTy, int $fallbackUserId): int
    {
        if (!$memberId) {
            return $fallbackUserId;
        }

        $exists = $congTy->thanhViens()
            ->where('nguoi_dungs.id', $memberId)
            ->exists();

        return $exists ? $memberId : $fallbackUserId;
    }

    private function isPubliclyActive(TinTuyenDung $tin): bool
    {
        $tin->loadMissing('congTy:id,trang_thai');

        if ((int) $tin->trang_thai !== TinTuyenDung::TRANG_THAI_HOAT_DONG) {
            return false;
        }

        if ((int) optional($tin->congTy)->trang_thai !== CongTy::TRANG_THAI_HOAT_DONG) {
            return false;
        }

        return !$tin->ngay_het_han || $tin->ngay_het_han->greaterThanOrEqualTo(now());
    }

    private function broadcastJobActivityIfNeeded(TinTuyenDung $tin, bool $wasPubliclyActive = false): void
    {
        if ($wasPubliclyActive || !$this->isPubliclyActive($tin)) {
            return;
        }

        $activityType = $tin->published_at
            ? FollowedCompanyJobActivated::TYPE_REOPENED
            : FollowedCompanyJobActivated::TYPE_PUBLISHED;

        $tin->forceFill([
            'published_at' => $activityType === FollowedCompanyJobActivated::TYPE_PUBLISHED
                ? ($tin->published_at ?? now())
                : $tin->published_at,
            'reactivated_at' => $activityType === FollowedCompanyJobActivated::TYPE_REOPENED
                ? now()
                : null,
        ])->save();

        $event = FollowedCompanyJobActivated::fromJob($tin->fresh(), $activityType);

        if (!$event) {
            return;
        }

        try {
            broadcast($event);
        } catch (\Throwable $exception) {
            report($exception);
        }
    }

    /**
     * Lấy ID công ty của NTD đang đăng nhập.
     */
    private function getCongTyId(): ?int
    {
        return $this->getCurrentEmployerCompany()?->id;
    }

    /**
     * Danh sách tin của công ty NTD.
     */
    public function index(Request $request): JsonResponse
    {
        $congTyId = $this->getCongTyId();
        if (!$congTyId) {
            return response()->json([
                'success' => false,
                'message' => 'Bạn chưa tạo cấu hình công ty. Vui lòng tạo tài khoản doanh nghiệp trước.',
            ], 404);
        }

        $query = TinTuyenDung::with(['nganhNghes:id,ten_nganh', 'hrPhuTrach:id,ho_ten,email'])
            ->withCount([
                'acceptedApplications as so_luong_da_nhan',
                'ungTuyens as tong_ung_tuyen_thuc_te' => fn ($query) => $query->whereNotNull('thoi_gian_ung_tuyen'),
            ])
            ->where('cong_ty_id', $congTyId);

        if ($request->filled('trang_thai')) {
            $query->where('trang_thai', $request->trang_thai);
        }

        if ($request->filled('search')) {
            $search = $request->search;
            $query->where('tieu_de', 'like', "%{$search}%");
        }

        if ($request->filled('hr_phu_trach_id')) {
            $hrPhuTrachId = $request->input('hr_phu_trach_id') === 'me'
                ? (int) auth()->id()
                : (int) $request->input('hr_phu_trach_id');

            $query->where('hr_phu_trach_id', $hrPhuTrachId);
        }

        $data = $query->orderBy('created_at', 'desc')->paginate((int) $request->get('per_page', 15));

        return response()->json([
            'success' => true,
            'data' => $data,
        ]);
    }

    /**
     * Tạo tin tuyển dụng mới.
     */
    public function store(TaoTinTuyenDungRequest $request): JsonResponse
    {
        $congTyId = $this->getCongTyId();
        if (!$congTyId) {
            return response()->json([
                'success' => false,
                'message' => 'Bạn cần thiết lập thông tin công ty trước khi tạo tin.',
            ], 403);
        }

        $data = $request->validated();
        $nganhNgheIds = $data['nganh_nghes'];
        unset($data['nganh_nghes']);

        $data['cong_ty_id'] = $congTyId;
        $congTy = $this->getCurrentEmployerCompany();
        $data['hr_phu_trach_id'] = $this->resolveValidHrPhuTrachId(
            isset($data['hr_phu_trach_id']) ? (int) $data['hr_phu_trach_id'] : null,
            $congTy,
            (int) auth()->id(),
        );

        $tin = TinTuyenDung::create($data);
        $tin->nganhNghes()->attach($nganhNgheIds);
        $tin->load(['nganhNghes:id,ten_nganh', 'hrPhuTrach:id,ho_ten,email']);

        $this->broadcastJobActivityIfNeeded($tin);

        return response()->json([
            'success' => true,
            'message' => 'Tạo tin tuyển dụng thành công.',
            'data' => $tin,
        ], 201);
    }

    /**
     * Cập nhật tin tuyển dụng.
     */
    public function update(CapNhatTinTuyenDungRequest $request, int $id): JsonResponse
    {
        $congTyId = $this->getCongTyId();
        $tin = TinTuyenDung::where('cong_ty_id', $congTyId)->findOrFail($id);
        $wasPubliclyActive = $this->isPubliclyActive($tin);

        $data = $request->validated();

        if (isset($data['nganh_nghes'])) {
            $tin->nganhNghes()->sync($data['nganh_nghes']);
            unset($data['nganh_nghes']);
        }

        if (array_key_exists('hr_phu_trach_id', $data)) {
            $congTy = $this->getCurrentEmployerCompany();
            $data['hr_phu_trach_id'] = $this->resolveValidHrPhuTrachId(
                $data['hr_phu_trach_id'] ? (int) $data['hr_phu_trach_id'] : null,
                $congTy,
                (int) auth()->id(),
            );
        }

        $tin->update($data);
        $tin = $tin->fresh()->load(['nganhNghes:id,ten_nganh', 'hrPhuTrach:id,ho_ten,email']);

        $this->broadcastJobActivityIfNeeded($tin, $wasPubliclyActive);

        return response()->json([
            'success' => true,
            'message' => 'Cập nhật tin thành công.',
            'data' => $tin,
        ]);
    }

    /**
     * Xem chi tiết tin.
     */
    public function show(int $id): JsonResponse
    {
        $congTyId = $this->getCongTyId();
        $tin = TinTuyenDung::with([
                'nganhNghes:id,ten_nganh',
                'hrPhuTrach:id,ho_ten,email',
                'parsing:id,tin_tuyen_dung_id,parsed_skills_json,parsed_requirements_json,parsed_benefits_json,parsed_salary_json,parsed_location_json,parse_status,parser_version,confidence_score,error_message,updated_at',
                'kyNangYeuCaus.kyNang:id,ten_ky_nang,icon',
            ])
            ->withCount([
                'acceptedApplications as so_luong_da_nhan',
                'ungTuyens as tong_ung_tuyen_thuc_te' => fn ($query) => $query->whereNotNull('thoi_gian_ung_tuyen'),
                'ungTuyens as tong_ho_so',
                'ungTuyens as ho_so_dang_cho' => fn ($query) => $query->where('trang_thai', \App\Models\UngTuyen::TRANG_THAI_CHO_DUYET),
                'ungTuyens as ho_so_da_xem' => fn ($query) => $query->where('trang_thai', \App\Models\UngTuyen::TRANG_THAI_DA_XEM),
                'ungTuyens as ho_so_phong_van' => fn ($query) => $query->where('trang_thai', \App\Models\UngTuyen::TRANG_THAI_DA_HEN_PHONG_VAN),
                'ungTuyens as ho_so_qua_phong_van' => fn ($query) => $query->where('trang_thai', \App\Models\UngTuyen::TRANG_THAI_QUA_PHONG_VAN),
                'ungTuyens as ho_so_da_nhan' => fn ($query) => $query->where('trang_thai', \App\Models\UngTuyen::TRANG_THAI_TRUNG_TUYEN),
                'ungTuyens as ho_so_tu_choi' => fn ($query) => $query->where('trang_thai', \App\Models\UngTuyen::TRANG_THAI_TU_CHOI),
            ])
            ->where('cong_ty_id', $congTyId)
            ->findOrFail($id);

        return response()->json([
            'success' => true,
            'data' => $tin,
        ]);
    }

    /**
     * Bật / tắt hiển thị (đổi trạng thái).
     */
    public function doiTrangThai(int $id): JsonResponse
    {
        $congTyId = $this->getCongTyId();
        $tin = TinTuyenDung::where('cong_ty_id', $congTyId)->findOrFail($id);
        $wasPubliclyActive = $this->isPubliclyActive($tin);

        $tin->trang_thai = $tin->trang_thai == 1 ? 0 : 1;
        $tin->save();
        $tin = $tin->fresh();

        $this->broadcastJobActivityIfNeeded($tin, $wasPubliclyActive);

        return response()->json([
            'success' => true,
            'message' => 'Chuyển trạng thái thành công.',
            'data' => $tin,
        ]);
    }

    /**
     * Xoá tin.
     */
    public function destroy(int $id): JsonResponse
    {
        $congTyId = $this->getCongTyId();
        $tin = TinTuyenDung::where('cong_ty_id', $congTyId)->findOrFail($id);

        if ($tin->ungTuyens()->whereNotNull('thoi_gian_ung_tuyen')->exists()) {
            return response()->json([
                'success' => false,
                'message' => 'Tin tuyển dụng này đã có đơn ứng tuyển. Bạn chỉ có thể tạm ngưng thay vì xóa.',
            ], 422);
        }

        $tin->delete();

        return response()->json([
            'success' => true,
            'message' => 'Xoá tin tuyển dụng thành công.',
        ]);
    }
}
