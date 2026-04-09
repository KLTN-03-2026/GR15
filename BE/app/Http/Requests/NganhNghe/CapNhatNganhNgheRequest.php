<?php

namespace App\Http\Requests\NganhNghe;

use Illuminate\Foundation\Http\FormRequest;

class CapNhatNganhNgheRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'ten_nganh' => ['sometimes', 'string', 'max:150'],
            'mo_ta' => ['nullable', 'string'],
            'danh_muc_cha_id' => ['nullable', 'integer', 'exists:nganh_nghes,id'],
            'icon' => ['nullable', 'string', 'max:255'],
            'icon_file' => ['nullable', 'image', 'mimes:jpeg,png,jpg,webp,svg', 'max:2048'],
            'trang_thai' => ['nullable', 'integer', 'in:0,1'],
        ];
    }

    public function messages(): array
    {
        return [
            'ten_nganh.max' => 'Tên ngành nghề tối đa 150 ký tự.',
            'danh_muc_cha_id.exists' => 'Danh mục cha không tồn tại.',
            'icon.max' => 'Icon tối đa 255 ký tự.',
            'icon_file.image' => 'Icon tải lên phải là file ảnh.',
            'icon_file.mimes' => 'Icon tải lên chỉ chấp nhận: jpeg, png, jpg, webp, svg.',
            'icon_file.max' => 'Icon tải lên tối đa 2MB.',
            'trang_thai.in' => 'Trạng thái phải là 0 (ẩn) hoặc 1 (hiển thị).',
        ];
    }
}
