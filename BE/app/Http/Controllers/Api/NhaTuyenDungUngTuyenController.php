<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\UngTuyen\CapNhatTrangThaiRequest;
use App\Models\UngTuyen;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class NhaTuyenDungUngTuyenController extends Controller
{
    /**
     * Xem danh sách CV ứng viên đã nộp vào CÔNG TY CỦA ĐANG ĐĂNG NHẬP
     */
    public function index(Request $request): JsonResponse
    {
        $user = auth()->user();
        $congTy = $user->congTy;

        if (!$congTy) {
            return response()->json([
                'success' => false,
                'message' => 'Vui lòng thiết lập thông tin công ty trước.'
            ], 403);
        }

        // Lấy danh sách hồ sơ nộp vào các tin tuyển dụng của công ty
        $query = UngTuyen::whereHas('tinTuyenDung', function ($q) use ($congTy) {
            $q->where('cong_ty_id', $congTy->id);
        })->with([
            'tinTuyenDung:id,tieu_de,hinh_thuc_lam_viec,trang_thai',
            'hoSo' => function ($q) {
                // Bao gồm hồ sơ đã xoá mềm 
                $q->withTrashed()
                  ->select('id', 'nguoi_dung_id', 'tieu_de_ho_so', 'muc_tieu_nghe_nghiep', 'file_cv')
                  ->with('nguoiDung:id,email'); // Chỉ lấy email
            }
        ]);

        // Lọc theo tin tuyển dụng cụ thể (VD chọn xem danh sách của chỉ 1 tin)
        if ($request->has('tin_tuyen_dung_id') && $request->tin_tuyen_dung_id !== '') {
            $query->where('tin_tuyen_dung_id', $request->tin_tuyen_dung_id);
        }

        // Lọc theo trạng thái hồ sơ 
        if ($request->has('trang_thai') && $request->trang_thai !== '') {
            $query->where('trang_thai', $request->trang_thai);
        }

        $query->orderBy('thoi_gian_ung_tuyen', 'desc');

        $ungTuyens = $query->paginate((int) $request->get('per_page', 15));

        return response()->json([
            'success' => true,
            'data' => $ungTuyens
        ]);
    }

    /**
     * Đổi trạng thái (Chờ, Xem, Đậu, Rớt) của đơn ứng tuyển
     */
    public function updateTrangThai(CapNhatTrangThaiRequest $request, $id): JsonResponse
    {
        $user = auth()->user();
        $congTy = $user->congTy;

        if (!$congTy) {
            return response()->json(['success' => false, 'message' => 'Lỗi công ty'], 403);
        }

        $ungTuyen = UngTuyen::whereHas('tinTuyenDung', function ($q) use ($congTy) {
            $q->where('cong_ty_id', $congTy->id);
        })->findOrFail($id);

        $dataUpdate = [
            'trang_thai' => $request->trang_thai
        ];

        if ($request->has('ngay_hen_phong_van')) {
            $dataUpdate['ngay_hen_phong_van'] = $request->ngay_hen_phong_van;
        }

        if ($request->has('ket_qua_phong_van')) {
            $dataUpdate['ket_qua_phong_van'] = $request->ket_qua_phong_van;
        }

        if ($request->has('ghi_chu')) {
            $dataUpdate['ghi_chu'] = $request->ghi_chu;
        }

        $ungTuyen->update($dataUpdate);

        return response()->json([
            'success' => true,
            'message' => 'Cập nhật trạng thái vòng phỏng vấn/ứng tuyển thành công.',
            'data' => $ungTuyen
        ]);
    }
}
