<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\HoSo\TaoHoSoRequest;
use App\Http\Requests\HoSo\CapNhatHoSoUngVienRequest;
use App\Models\HoSo;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;

/**
 * HoSoController - Quản lý hồ sơ dành cho Ứng viên
 *
 * Vai trò được phép: Ứng viên (vai_tro = 0)
 *
 * Routes:
 *   GET    /api/v1/ung-vien/ho-sos              - Danh sách hồ sơ của ứng viên
 *   POST   /api/v1/ung-vien/ho-sos              - Tạo hồ sơ mới
 *   GET    /api/v1/ung-vien/ho-sos/{id}         - Xem chi tiết hồ sơ
 *   PUT    /api/v1/ung-vien/ho-sos/{id}         - Cập nhật hồ sơ
 *   DELETE /api/v1/ung-vien/ho-sos/{id}         - Xoá hồ sơ
 *   PATCH  /api/v1/ung-vien/ho-sos/{id}/trang-thai - Đổi trạng thái (công khai/ẩn)
 */
class HoSoController extends Controller
{
    private function unauthorizedResponse(): JsonResponse
    {
        return response()->json([
            'success' => false,
            'message' => 'Phiên đăng nhập không còn hợp lệ.',
        ], 401);
    }

    /**
     * GET /api/v1/ung-vien/ho-sos
     * Danh sách hồ sơ của người dùng đang đăng nhập.
     */
    public function index(Request $request): JsonResponse
    {
        $nguoiDung = $request->user();

        if (!$nguoiDung) {
            return $this->unauthorizedResponse();
        }

        $query = HoSo::with([
                'parsing:id,ho_so_id,parse_status,confidence_score,parser_version,error_message,updated_at'
            ])
            ->where('nguoi_dung_id', $nguoiDung->id);

        if ($request->filled('trang_thai')) {
            $query->where('trang_thai', $request->trang_thai);
        }

        $allowedSorts = ['id', 'tieu_de_ho_so', 'created_at', 'updated_at'];
        $sortBy = in_array($request->get('sort_by'), $allowedSorts)
            ? $request->get('sort_by') : 'created_at';
        $sortDir = $request->get('sort_dir', 'desc') === 'asc' ? 'asc' : 'desc';
        $query->orderBy($sortBy, $sortDir);

        $perPage = min((int) $request->get('per_page', 10), 50);
        $hoSos = $query->paginate($perPage);

        return response()->json([
            'success' => true,
            'data' => $hoSos,
        ]);
    }

    /**
     * POST /api/v1/ung-vien/ho-sos
     * Ứng viên tạo hồ sơ mới.
     */
    public function store(TaoHoSoRequest $request): JsonResponse
    {
        $nguoiDung = $request->user();

        if (!$nguoiDung) {
            return $this->unauthorizedResponse();
        }

        $data = $request->validated();
        $data['nguoi_dung_id'] = $nguoiDung->id;

        // Upload file CV nếu có
        if ($request->hasFile('file_cv')) {
            $data['file_cv'] = $request->file('file_cv')
                ->store('file_cv', 'public');
        }

        $hoSo = HoSo::create($data);

        return response()->json([
            'success' => true,
            'message' => 'Tạo hồ sơ thành công.',
            'data' => $hoSo,
        ], 201);
    }

    /**
     * GET /api/v1/ung-vien/ho-sos/{id}
     * Xem chi tiết hồ sơ (chỉ xem được hồ sơ của mình).
     */
    public function show(Request $request, int $id): JsonResponse
    {
        $nguoiDung = $request->user();

        if (!$nguoiDung) {
            return $this->unauthorizedResponse();
        }

        $hoSo = HoSo::with([
                'parsing:id,ho_so_id,raw_text,parsed_name,parsed_email,parsed_phone,parsed_skills_json,parsed_experience_json,parsed_education_json,parse_status,confidence_score,parser_version,error_message,updated_at'
            ])
            ->where('nguoi_dung_id', $nguoiDung->id)
            ->findOrFail($id);

        return response()->json([
            'success' => true,
            'data' => $hoSo,
        ]);
    }

    /**
     * PUT /api/v1/ung-vien/ho-sos/{id}
     * Ứng viên cập nhật hồ sơ của mình.
     */
    public function update(CapNhatHoSoUngVienRequest $request, int $id): JsonResponse
    {
        $nguoiDung = $request->user();

        if (!$nguoiDung) {
            return $this->unauthorizedResponse();
        }

        $hoSo = HoSo::where('nguoi_dung_id', $nguoiDung->id)
            ->findOrFail($id);

        $data = $request->validated();

        // Upload file CV mới nếu có, xoá file cũ
        if ($request->hasFile('file_cv')) {
            if ($hoSo->file_cv) {
                Storage::disk('public')->delete($hoSo->file_cv);
            }
            $data['file_cv'] = $request->file('file_cv')
                ->store('file_cv', 'public');
        }

        $hoSo->update($data);

        return response()->json([
            'success' => true,
            'message' => 'Cập nhật hồ sơ thành công.',
            'data' => $hoSo->fresh(),
        ]);
    }

    /**
     * DELETE /api/v1/ung-vien/ho-sos/{id}
     * Ứng viên xoá hồ sơ của mình.
     */
    public function destroy(Request $request, int $id): JsonResponse
    {
        $nguoiDung = $request->user();

        if (!$nguoiDung) {
            return $this->unauthorizedResponse();
        }

        $hoSo = HoSo::where('nguoi_dung_id', $nguoiDung->id)
            ->findOrFail($id);

        // Xoá file CV nếu có
        if ($hoSo->file_cv) {
            Storage::disk('public')->delete($hoSo->file_cv);
        }

        $hoSo->delete();

        return response()->json([
            'success' => true,
            'message' => 'Xoá hồ sơ thành công.',
        ]);
    }

    /**
     * PATCH /api/v1/ung-vien/ho-sos/{id}/trang-thai
     * Ứng viên đổi trạng thái hồ sơ (công khai/ẩn).
     */
    public function doiTrangThai(Request $request, int $id): JsonResponse
    {
        $nguoiDung = $request->user();

        if (!$nguoiDung) {
            return $this->unauthorizedResponse();
        }

        $hoSo = HoSo::where('nguoi_dung_id', $nguoiDung->id)
            ->findOrFail($id);

        $hoSo->trang_thai = $hoSo->trang_thai ? 0 : 1;
        $hoSo->save();

        $action = $hoSo->trang_thai ? 'Công khai' : 'Ẩn';

        return response()->json([
            'success' => true,
            'message' => "{$action} hồ sơ thành công.",
            'data' => $hoSo,
        ]);
    }
}
