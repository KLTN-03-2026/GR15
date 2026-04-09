<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\UngTuyen\NopHoSoRequest;
use App\Models\TinTuyenDung;
use App\Models\UngTuyen;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class UngVienUngTuyenController extends Controller
{
    /**
     * Xem danh sách các công việc đã nộp hồ sơ
     */
    public function index(Request $request): JsonResponse
    {
        $userId = auth()->id();

        // Query các ứng tuyển thông qua hồ sơ của user hiện tại
        $query = UngTuyen::whereHas('hoSo', function ($q) use ($userId) {
            // Bao gồm cả hoSo đã soft delete
            $q->withTrashed()->where('nguoi_dung_id', $userId);
        })
        ->with([
            'tinTuyenDung:id,cong_ty_id,tieu_de,dia_diem_lam_viec,muc_luong,trang_thai',
            'tinTuyenDung.congTy:id,ten_cong_ty,logo',
            'hoSo' => function ($q) {
                // Bao gồm cả hồ sơ bị xóa
                $q->withTrashed()->select('id', 'nguoi_dung_id', 'tieu_de_ho_so', 'file_cv');
            }
        ]);

        // Lọc theo trạng thái ứng tuyển (nếu có)
        if ($request->has('trang_thai') && $request->trang_thai !== '') {
            $query->where('trang_thai', $request->trang_thai);
        }

        $query->orderBy('thoi_gian_ung_tuyen', 'desc');

        $ungTuyens = $query->paginate((int) $request->get('per_page', 10));

        return response()->json([
            'success' => true,
            'data' => $ungTuyens
        ]);
    }

    /**
     * Nộp hồ sơ vào 1 tin tuyển dụng
     */
    public function store(NopHoSoRequest $request): JsonResponse
    {
        $userId = auth()->id();
        $tinId = $request->tin_tuyen_dung_id;

        // 1. Kiểm tra tin tuyển dụng có còn hoạt động không
        $tin = TinTuyenDung::find($tinId);
        if ($tin->trang_thai != 1 || ($tin->ngay_het_han && \Carbon\Carbon::parse($tin->ngay_het_han)->isPast())) {
            return response()->json([
                'success' => false,
                'message' => 'Tin tuyển dụng đã hết hạn hoặc tạm ngưng.'
            ], 400);
        }

        // 2. Kiểm tra cty có đang hoạt động không
        if ($tin->congTy && $tin->congTy->trang_thai != 1) {
            return response()->json([
                'success' => false,
                'message' => 'Công ty tuyển dụng đang bị khóa hoặc chưa duyệt.'
            ], 400);
        }

        // 3. Kiểm tra xem người dùng này ĐÃ nộp hồ sơ vào tin này CHƯA 
        // (Dù nộp bằng hồ sơ khác cũng không cho, 1 tài khoản chỉ nộp 1 lần/tin)
        $daNop = UngTuyen::where('tin_tuyen_dung_id', $tinId)
            ->whereHas('hoSo', function ($q) use ($userId) {
                $q->withTrashed()->where('nguoi_dung_id', $userId);
            })->exists();

        if ($daNop) {
            return response()->json([
                'success' => false,
                'message' => 'Bạn đã nộp hồ sơ vào tin này rồi, không thể nộp thêm.'
            ], 400);
        }

        // Tạo ứng tuyển
        $ungTuyen = UngTuyen::create([
            'tin_tuyen_dung_id' => $tinId,
            'ho_so_id' => $request->ho_so_id,
            'thu_xin_viec' => $request->thu_xin_viec,
            'trang_thai' => UngTuyen::TRANG_THAI_CHO_DUYET,
            // 'thoi_gian_ung_tuyen' sinh bằng DB default CURRENT_TIMESTAMP
        ]);

        // Load relationship trả về
        $ungTuyen->load([
            'tinTuyenDung:id,tieu_de',
            'hoSo:id,tieu_de_ho_so'
        ]);

        return response()->json([
            'success' => true,
            'message' => 'Nộp hồ sơ thành công!',
            'data' => $ungTuyen
        ], 201);
    }
}
