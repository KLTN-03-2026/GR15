<?php

namespace App\Http\Requests\CongTy;

use App\Models\CongTy;
use App\Models\NguoiDung;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

class TaoCongTyRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'nguoi_dung_id' => [
                'required',
                'integer',
                Rule::exists('nguoi_dungs', 'id')->where(fn ($query) => $query->where('vai_tro', NguoiDung::VAI_TRO_NHA_TUYEN_DUNG)),
            ],
            'ten_cong_ty' => ['required', 'string', 'max:200'],
            'ma_so_thue' => ['required', 'string', 'max:20', 'unique:cong_tys,ma_so_thue'],
            'mo_ta' => ['nullable', 'string'],
            'dia_chi' => ['nullable', 'string', 'max:255'],
            'dien_thoai' => ['nullable', 'string', 'max:20'],
            'email' => ['nullable', 'email', 'max:100'],
            'website' => ['nullable', 'string', 'max:200'],
            'logo' => ['nullable', 'string', 'max:255'],
            'nganh_nghe_id' => ['nullable', 'integer', 'exists:nganh_nghes,id'],
            'quy_mo' => ['nullable', 'string', 'in:' . implode(',', CongTy::QUY_MO_LIST)],
        ];
    }

    public function messages(): array
    {
        return [
            'nguoi_dung_id.required' => 'Nhà tuyển dụng sở hữu không được để trống.',
            'nguoi_dung_id.exists' => 'Người dùng sở hữu phải là nhà tuyển dụng hợp lệ.',
            'ten_cong_ty.required' => 'Tên công ty không được để trống.',
            'ten_cong_ty.max' => 'Tên công ty tối đa 200 ký tự.',
            'ma_so_thue.required' => 'Mã số thuế không được để trống.',
            'ma_so_thue.max' => 'Mã số thuế tối đa 20 ký tự.',
            'ma_so_thue.unique' => 'Mã số thuế đã tồn tại.',
            'email.email' => 'Email không đúng định dạng.',
            'nganh_nghe_id.exists' => 'Ngành nghề không tồn tại.',
            'quy_mo.in' => 'Quy mô không hợp lệ (1-10, 11-50, 51-200, 201-500, 500+).',
        ];
    }
}
