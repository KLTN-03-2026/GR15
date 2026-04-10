<?php

namespace App\Http\Controllers\Api;

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
    /**
     * Lấy ID công ty của NTD đang đăng nhập.
     */
    private function getCongTyId(): ?int
    {
        return CongTy::where('nguoi_dung_id', auth()->id())->value('id');
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

        $query = TinTuyenDung::with('nganhNghes:id,ten_nganh')
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

        $tin = TinTuyenDung::create($data);
        $tin->nganhNghes()->attach($nganhNgheIds);

        return response()->json([
            'success' => true,
            'message' => 'Tạo tin tuyển dụng thành công.',
            'data' => $tin->load('nganhNghes:id,ten_nganh'),
        ], 201);
    }

    /**
     * Cập nhật tin tuyển dụng.
     */
    public function update(CapNhatTinTuyenDungRequest $request, int $id): JsonResponse
    {
        $congTyId = $this->getCongTyId();
        $tin = TinTuyenDung::where('cong_ty_id', $congTyId)->findOrFail($id);

        $data = $request->validated();

        if (isset($data['nganh_nghes'])) {
            $tin->nganhNghes()->sync($data['nganh_nghes']);
            unset($data['nganh_nghes']);
        }

        $tin->update($data);

        return response()->json([
            'success' => true,
            'message' => 'Cập nhật tin thành công.',
            'data' => $tin->fresh()->load('nganhNghes:id,ten_nganh'),
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

        $tin->trang_thai = $tin->trang_thai == 1 ? 0 : 1;
        $tin->save();

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
