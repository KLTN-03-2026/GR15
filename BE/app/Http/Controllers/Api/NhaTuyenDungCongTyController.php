<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\CongTy;
use App\Models\NguoiDung;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;

class NhaTuyenDungCongTyController extends Controller
{
    /**
     * GET /api/v1/nha-tuyen-dung/cong-ty
     */
    public function show(Request $request): JsonResponse
    {
        $user = $request->user();
        $congTy = $user->congTys()->with('thanhViens:id,email,ho_ten')->first();

        if (!$congTy) {
            return response()->json(['message' => 'Bạn chưa có công ty nào.'], 404);
        }

        return response()->json($congTy);
    }

    /**
     * PUT /api/v1/nha-tuyen-dung/cong-ty
     */
    public function update(Request $request): JsonResponse
    {
        $user = $request->user();
        $congTy = $user->congTys()->first();

        if (!$congTy) {
            $congTy = new CongTy();
            $request->validate([
                'ten_cong_ty' => 'required|string|max:255',
            ]);
        } else {
            // Check nếu user la_chu_so_huu (pivot table)
            $pivot = $congTy->thanhViens()->where('nguoi_dung_id', $user->id)->first()->pivot;
            if ($pivot->vai_tro_noi_bo !== 'owner') {
                return response()->json(['message' => 'Không có quyền cập nhật.'], 403);
            }
        }

        $data = $request->validate([
            'ten_cong_ty' => 'nullable|string|max:255',
            'ma_so_thue' => 'nullable|string|max:50',
            'dia_chi' => 'nullable|string',
            'website' => 'nullable|string',
            'quy_mo' => 'nullable|string',
            'mo_ta' => 'nullable|string',
            'logo' => 'nullable|image|max:2048'
        ]);

        if ($request->hasFile('logo')) {
            if ($congTy->logo && Storage::disk('public')->exists($congTy->logo)) {
                Storage::disk('public')->delete($congTy->logo);
            }
            $data['logo'] = $request->file('logo')->store('cong_ty_logos', 'public');
        }

        if (!$congTy->exists) {
            $congTy->fill($data);
            $congTy->save();
            $congTy->thanhViens()->attach($user->id, ['vai_tro_noi_bo' => 'owner']);
        } else {
            $congTy->update($data);
        }

        return response()->json([
            'success' => true,
            'message' => 'Cập nhật công ty thành công',
            'data' => $congTy
        ]);
    }

    /**
     * GET /api/v1/nha-tuyen-dung/cong-ty/thanh-viens
     */
    public function getMembers(Request $request): JsonResponse
    {
        $user = $request->user();
        $congTy = $user->congTys()->first();

        if (!$congTy) {
            return response()->json([], 404);
        }

        return response()->json($congTy->thanhViens);
    }

    /**
     * PUT /api/v1/nha-tuyen-dung/cong-ty/thanh-viens
     */
    public function updateMemberRole(Request $request): JsonResponse
    {
        $user = $request->user();
        $congTy = $user->congTys()->first();

        if (!$congTy) {
            return response()->json(['message' => 'Chưa có công ty'], 404);
        }

        $pivot = $congTy->thanhViens()->where('nguoi_dung_id', $user->id)->first()->pivot;
        if ($pivot->vai_tro_noi_bo !== 'owner') {
            return response()->json(['message' => 'Chỉ chủ sở hữu mới có quyền.'], 403);
        }

        $data = $request->validate([
            'nguoi_dung_id' => 'required|exists:nguoi_dungs,id',
            'vai_tro_noi_bo' => 'required|in:admin,hr,member'
        ]);

        $congTy->thanhViens()->updateExistingPivot($data['nguoi_dung_id'], [
            'vai_tro_noi_bo' => $data['vai_tro_noi_bo']
        ]);

        return response()->json(['success' => true, 'message' => 'Cập nhật role thành công']);
    }

    /**
     * DELETE /api/v1/nha-tuyen-dung/cong-ty/thanh-viens/{id}
     */
    public function removeMember(Request $request, $id): JsonResponse
    {
        $user = $request->user();
        $congTy = $user->congTys()->first();

        if (!$congTy) {
            return response()->json(['message' => 'Chưa có công ty'], 404);
        }

        $pivot = $congTy->thanhViens()->where('nguoi_dung_id', $user->id)->first()->pivot;
        if ($pivot->vai_tro_noi_bo !== 'owner') {
            return response()->json(['message' => 'Chỉ chủ sở hữu mới có quyền.'], 403);
        }

        if ($id == $user->id) {
            return response()->json(['message' => 'Không thể xoá chính mình'], 400);
        }

        $congTy->thanhViens()->detach($id);

        return response()->json(['success' => true, 'message' => 'Xoá thành viên thành công']);
    }
}
