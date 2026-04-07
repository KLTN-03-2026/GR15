<?php

namespace App\Http\Requests\HoSo;

use Illuminate\Foundation\Http\FormRequest;

class TaoHoSoRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'tieu_de_ho_so' => ['required', 'string', 'max:200'],
            'muc_tieu_nghe_nghiep' => ['nullable', 'string'],
            'trinh_do' => ['nullable', 'string', 'max:100', 'in:trung_hoc,trung_cap,cao_dang,dai_hoc,thac_si,tien_si,khac'],
            'kinh_nghiem_nam' => ['nullable', 'integer', 'min:0', 'max:50'],
            'mo_ta_ban_than' => ['nullable', 'string'],
            'file_cv' => ['nullable', 'file', 'mimes:pdf,doc,docx', 'max:5120'],
            'trang_thai' => ['nullable', 'integer', 'in:0,1'],
        ];
    }

    public function messages(): array
    {
        return [
            'tieu_de_ho_so.required' => 'Tiêu đề hồ sơ không được để trống.',
            'tieu_de_ho_so.max' => 'Tiêu đề hồ sơ tối đa 200 ký tự.',
            'trinh_do.in' => 'Trình độ phải là: trung_hoc, trung_cap, cao_dang, dai_hoc, thac_si, tien_si, khac.',
            'kinh_nghiem_nam.integer' => 'Kinh nghiệm năm phải là số nguyên.',
            'kinh_nghiem_nam.min' => 'Kinh nghiệm năm không được nhỏ hơn 0.',
            'kinh_nghiem_nam.max' => 'Kinh nghiệm năm không được lớn hơn 50.',
            'file_cv.file' => 'File CV phải là một tệp tin.',
            'file_cv.mimes' => 'File CV chỉ chấp nhận: pdf, doc, docx.',
            'file_cv.max' => 'File CV tối đa 5MB.',
            'trang_thai.in' => 'Trạng thái phải là 0 (ẩn) hoặc 1 (công khai).',
        ];
    }
}
