<?php

namespace App\Http\Requests\UngTuyen;

use Illuminate\Foundation\Http\FormRequest;

class GuiOfferRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'ghi_chu_offer' => ['nullable', 'string', 'max:5000'],
            'link_offer' => ['nullable', 'url', 'max:2048'],
        ];
    }

    public function messages(): array
    {
        return [
            'link_offer.url' => 'Liên kết offer không hợp lệ.',
        ];
    }
}
