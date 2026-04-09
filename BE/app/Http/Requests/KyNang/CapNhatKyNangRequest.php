<?php

namespace App\Http\Requests\KyNang;

use Illuminate\Foundation\Http\FormRequest;

class CapNhatKyNangRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        $id = $this->route('id');

        return [
            'ten_ky_nang' => ['sometimes', 'string', 'max:150', "unique:ky_nangs,ten_ky_nang,{$id}"],
            'mo_ta' => ['nullable', 'string'],
            'icon' => ['nullable', 'string', 'max:255'],
            'icon_file' => ['nullable', 'image', 'mimes:jpeg,png,jpg,webp,svg', 'max:2048'],
        ];
    }

    public function messages(): array
    {
        return [
            'ten_ky_nang.max' => 'Tên kỹ năng tối đa 150 ký tự.',
            'ten_ky_nang.unique' => 'Tên kỹ năng đã tồn tại.',
            'icon.max' => 'Icon tối đa 255 ký tự.',
            'icon_file.image' => 'Icon tải lên phải là file ảnh.',
            'icon_file.mimes' => 'Icon tải lên chỉ chấp nhận: jpeg, png, jpg, webp, svg.',
            'icon_file.max' => 'Icon tải lên tối đa 2MB.',
        ];
    }
}
