<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\HoSo;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

/**
 * NhaTuyenDungHoSoController - Nhà tuyển dụng xem hồ sơ ứng viên
 *
 * Vai trò được phép: Nhà tuyển dụng (vai_tro = 1)
 *
 * NTD chỉ có quyền XEM các hồ sơ công khai (trang_thai = 1).
 * Không có quyền tạo, sửa, xoá hồ sơ.
 *
 * Routes:
 *   GET  /api/v1/nha-tuyen-dung/ho-sos         - Danh sách hồ sơ công khai (có lọc + tìm kiếm + phân trang)
 *   GET  /api/v1/nha-tuyen-dung/ho-sos/{id}    - Chi tiết hồ sơ công khai
 */
class NhaTuyenDungHoSoController extends Controller
{
    /**
     * GET /api/v1/nha-tuyen-dung/ho-sos
     * Danh sách hồ sơ công khai của ứng viên.
     *
     * NTD chỉ thấy được hồ sơ có trang_thai = 1 (công khai).
     *
     * Query params:
     *   ?trinh_do=dai_hoc        Lọc theo trình độ
     *   ?kinh_nghiem_tu=2        Kinh nghiệm từ (năm)
     *   ?kinh_nghiem_den=5       Kinh nghiệm đến (năm)
     *   ?search=keyword          Tìm theo tiêu đề/mục tiêu/mô tả
     *   ?sort_by=created_at      Sắp xếp theo trường
     *   ?sort_dir=asc|desc       Chiều sắp xếp
     *   ?per_page=15             Số bản ghi mỗi trang
     */
    public function index(Request $request): JsonResponse
    {
        $query = HoSo::with('nguoiDung:id,ho_ten,email,so_dien_thoai,anh_dai_dien')
            ->where('trang_thai', HoSo::TRANG_THAI_CONG_KHAI);

        // Lọc theo trình độ
        if ($request->filled('trinh_do')) {
            $query->where('trinh_do', $request->trinh_do);
        }

        // Lọc theo khoảng kinh nghiệm
        if ($request->filled('kinh_nghiem_tu')) {
            $query->where('kinh_nghiem_nam', '>=', (int) $request->kinh_nghiem_tu);
        }

        if ($request->filled('kinh_nghiem_den')) {
            $query->where('kinh_nghiem_nam', '<=', (int) $request->kinh_nghiem_den);
        }

        // Tìm kiếm theo tiêu đề, mục tiêu, mô tả
        if ($request->filled('search')) {
            $search = $request->search;
            $query->where(function ($q) use ($search) {
                $q->where('tieu_de_ho_so', 'like', "%{$search}%")
                    ->orWhere('muc_tieu_nghe_nghiep', 'like', "%{$search}%")
                    ->orWhere('mo_ta_ban_than', 'like', "%{$search}%");
            });
        }

        // Sắp xếp
        $allowedSorts = ['id', 'tieu_de_ho_so', 'trinh_do', 'kinh_nghiem_nam', 'created_at'];
        $sortBy = in_array($request->get('sort_by'), $allowedSorts)
            ? $request->get('sort_by') : 'created_at';
        $sortDir = $request->get('sort_dir', 'desc') === 'asc' ? 'asc' : 'desc';
        $query->orderBy($sortBy, $sortDir);

        // Phân trang
        $perPage = min((int) $request->get('per_page', 15), 100);
        $hoSos = $query->paginate($perPage);

        return response()->json([
            'success' => true,
            'data' => $hoSos,
        ]);
    }

    /**
     * GET /api/v1/nha-tuyen-dung/ho-sos/{id}
     * Xem chi tiết hồ sơ công khai.
     *
     * NTD chỉ xem được hồ sơ có trang_thai = 1.
     */
    public function show(int $id): JsonResponse
    {
        $hoSo = HoSo::with('nguoiDung:id,ho_ten,email,so_dien_thoai,anh_dai_dien')
            ->where('trang_thai', HoSo::TRANG_THAI_CONG_KHAI)
            ->findOrFail($id);

        return response()->json([
            'success' => true,
            'data' => $hoSo,
        ]);
    }
}
