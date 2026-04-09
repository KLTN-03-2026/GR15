<?php

namespace App\Http\Requests\TinTuyenDung;

use App\Models\TinTuyenDung;
use Illuminate\Foundation\Http\FormRequest;

class CapNhatTinTuyenDungRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'tieu_de' => ['sometimes', 'string', 'max:200'],
            'mo_ta_cong_viec' => ['sometimes', 'string'],
            'dia_diem_lam_viec' => ['sometimes', 'string', 'max:255'],
            'hinh_thuc_lam_viec' => ['nullable', 'string', 'in:' . implode(',', TinTuyenDung::HINH_THUC_LIST)],
            'cap_bac' => ['nullable', 'string', 'max:50'],
            'so_luong_tuyen' => ['nullable', 'integer', 'min:1'],
            'muc_luong' => ['nullable', 'integer', 'min:0'],
            'kinh_nghiem_yeu_cau' => ['nullable', 'string', 'max:100'],
            'ngay_het_han' => ['nullable', 'date'],
            'trang_thai' => ['nullable', 'integer', 'in:0,1'],
            'nganh_nghes' => ['sometimes', 'array', 'min:1'],
            'nganh_nghes.*' => ['integer', 'exists:nganh_nghes,id'],
        ];
    }

    public function messages(): array
    {
        return [
            'nganh_nghes.min' => 'Vui lòng chọn ít nhất 1 ngành nghề.',
            'nganh_nghes.*.exists' => 'Ngành nghề không tồn tại.',
            'so_luong_tuyen.min' => 'Số lượng tuyển phải lớn hơn 0.',
        ];
    }
}
