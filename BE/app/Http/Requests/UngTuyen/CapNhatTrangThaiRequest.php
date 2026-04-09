<?php

namespace App\Http\Requests\UngTuyen;

use App\Models\UngTuyen;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

class CapNhatTrangThaiRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true; // Phân quyền sẽ ở Controller/Middleware
    }

    public function rules(): array
    {
        return [
            'trang_thai' => [
                'required',
                'integer',
                Rule::in(UngTuyen::TRANG_THAI_LIST)
            ],
            'ngay_hen_phong_van' => [
                'nullable',
                'date',
                'after_or_equal:today'
            ],
            'ket_qua_phong_van' => [
                'nullable',
                'string',
                'max:255'
            ],
            'ghi_chu' => [
                'nullable',
                'string',
                'max:5000'
            ]
        ];
    }

    public function messages(): array
    {
        return [
            'trang_thai.required' => 'Vui lòng cung cấp trạng thái mới.',
            'trang_thai.in' => 'Trạng thái không hợp lệ (Chỉ có 0: Chờ duyệt, 1: Đã xem, 2: Chấp nhận, 3: Từ chối).',
        ];
    }
}
