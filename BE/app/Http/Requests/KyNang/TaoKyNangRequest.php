<?php

namespace App\Http\Requests\KyNang;

use Illuminate\Foundation\Http\FormRequest;

class TaoKyNangRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'ten_ky_nang' => ['required', 'string', 'max:150', 'unique:ky_nangs,ten_ky_nang'],
            'mo_ta' => ['nullable', 'string'],
            'icon' => ['nullable', 'string', 'max:255', 'required_without:icon_file'],
            'icon_file' => ['nullable', 'image', 'mimes:jpeg,png,jpg,webp,svg', 'max:2048', 'required_without:icon'],
        ];
    }

    public function messages(): array
    {
        return [
            'ten_ky_nang.required' => 'Tên kỹ năng không được để trống.',
            'ten_ky_nang.max' => 'Tên kỹ năng tối đa 150 ký tự.',
            'ten_ky_nang.unique' => 'Tên kỹ năng đã tồn tại.',
            'icon.max' => 'Icon tối đa 255 ký tự.',
            'icon.required_without' => 'Vui lòng nhập icon hoặc chọn ảnh tải lên.',
            'icon_file.required_without' => 'Vui lòng chọn ảnh tải lên hoặc nhập icon.',
            'icon_file.image' => 'Icon tải lên phải là file ảnh.',
            'icon_file.mimes' => 'Icon tải lên chỉ chấp nhận: jpeg, png, jpg, webp, svg.',
            'icon_file.max' => 'Icon tải lên tối đa 2MB.',
        ];
    }
}
