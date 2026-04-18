<?php

namespace App\Http\Requests\UngTuyen;

use App\Models\UngTuyen;
use Carbon\Carbon;
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
                function (string $attribute, mixed $value, \Closure $fail): void {
                    try {
                        if (Carbon::parse((string) $value, 'UTC')->lt(now('UTC'))) {
                            $fail('Ngày giờ hẹn phỏng vấn phải lớn hơn hoặc bằng thời điểm hiện tại.');
                        }
                    } catch (\Throwable) {
                        $fail('Ngày giờ hẹn phỏng vấn không hợp lệ.');
                    }
                },
            ],
            'hinh_thuc_phong_van' => [
                'nullable',
                'string',
                Rule::in(['online', 'offline', 'phone']),
            ],
            'nguoi_phong_van' => [
                'nullable',
                'string',
                'max:255',
            ],
            'link_phong_van' => [
                'nullable',
                'string',
                'max:2048',
            ],
            'ket_qua_phong_van' => [
                'nullable',
                'string',
                'max:255'
            ],
            'hr_phu_trach_id' => [
                'nullable',
                'integer',
                'exists:nguoi_dungs,id',
            ],
            'ghi_chu' => [
                'nullable',
                'string',
                'max:5000'
            ]
        ];
    }

    protected function prepareForValidation(): void
    {
        if (!$this->filled('ngay_hen_phong_van')) {
            return;
        }

        try {
            $this->merge([
                'ngay_hen_phong_van' => Carbon::parse((string) $this->input('ngay_hen_phong_van'), 'Asia/Ho_Chi_Minh')
                    ->utc()
                    ->format('Y-m-d H:i:s'),
            ]);
        } catch (\Throwable) {
            // Giữ nguyên để validator xử lý.
        }
    }

    public function messages(): array
    {
        return [
            'trang_thai.required' => 'Vui lòng cung cấp trạng thái mới.',
            'trang_thai.in' => 'Trạng thái không hợp lệ.',
        ];
    }
}
