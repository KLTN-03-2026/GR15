<?php

namespace App\Http\Requests\HoSo;

use Illuminate\Foundation\Http\FormRequest;

class TaoHoSoRequest extends FormRequest
{
    protected array $jsonFields = [
        'ky_nang_json',
        'kinh_nghiem_json',
        'hoc_van_json',
        'du_an_json',
        'chung_chi_json',
    ];

    public function authorize(): bool
    {
        return true;
    }

    protected function prepareForValidation(): void
    {
        $payload = [];

        foreach ($this->jsonFields as $field) {
            $value = $this->input($field);

            if (is_string($value) && $value !== '') {
                $decoded = json_decode($value, true);
                if (json_last_error() === JSON_ERROR_NONE) {
                    $payload[$field] = $decoded;
                }
            }
        }

        if ($this->input('kinh_nghiem_nam') === '') {
            $payload['kinh_nghiem_nam'] = null;
        }

        if (!empty($payload)) {
            $this->merge($payload);
        }
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
            'nguon_ho_so' => ['nullable', 'string', 'in:upload,builder,hybrid'],
            'mau_cv' => ['nullable', 'string', 'in:classic,minimal,executive,modern,creative,compact'],
            'ky_nang_json' => ['nullable', 'array', 'max:30'],
            'ky_nang_json.*.ten' => ['required_with:ky_nang_json', 'string', 'max:120'],
            'ky_nang_json.*.muc_do' => ['nullable', 'string', 'in:co_ban,kha,tot,chuyen_sau'],
            'kinh_nghiem_json' => ['nullable', 'array', 'max:20'],
            'kinh_nghiem_json.*.vi_tri' => ['required_with:kinh_nghiem_json', 'string', 'max:150'],
            'kinh_nghiem_json.*.cong_ty' => ['nullable', 'string', 'max:150'],
            'kinh_nghiem_json.*.bat_dau' => ['nullable', 'string', 'max:20'],
            'kinh_nghiem_json.*.ket_thuc' => ['nullable', 'string', 'max:20'],
            'kinh_nghiem_json.*.mo_ta' => ['nullable', 'string'],
            'hoc_van_json' => ['nullable', 'array', 'max:10'],
            'hoc_van_json.*.truong' => ['required_with:hoc_van_json', 'string', 'max:150'],
            'hoc_van_json.*.chuyen_nganh' => ['nullable', 'string', 'max:150'],
            'hoc_van_json.*.bat_dau' => ['nullable', 'string', 'max:20'],
            'hoc_van_json.*.ket_thuc' => ['nullable', 'string', 'max:20'],
            'hoc_van_json.*.mo_ta' => ['nullable', 'string'],
            'du_an_json' => ['nullable', 'array', 'max:10'],
            'du_an_json.*.ten' => ['required_with:du_an_json', 'string', 'max:150'],
            'du_an_json.*.vai_tro' => ['nullable', 'string', 'max:150'],
            'du_an_json.*.cong_nghe' => ['nullable', 'string', 'max:255'],
            'du_an_json.*.mo_ta' => ['nullable', 'string'],
            'du_an_json.*.link' => ['nullable', 'url', 'max:255'],
            'chung_chi_json' => ['nullable', 'array', 'max:10'],
            'chung_chi_json.*.ten' => ['required_with:chung_chi_json', 'string', 'max:150'],
            'chung_chi_json.*.don_vi' => ['nullable', 'string', 'max:150'],
            'chung_chi_json.*.nam' => ['nullable', 'digits:4'],
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
            'nguon_ho_so.in' => 'Nguồn hồ sơ không hợp lệ.',
            'mau_cv.in' => 'Mẫu CV không hợp lệ.',
            'ky_nang_json.array' => 'Danh sách kỹ năng không hợp lệ.',
            'ky_nang_json.*.ten.required_with' => 'Tên kỹ năng không được để trống.',
            'kinh_nghiem_json.array' => 'Danh sách kinh nghiệm không hợp lệ.',
            'kinh_nghiem_json.*.vi_tri.required_with' => 'Vị trí kinh nghiệm không được để trống.',
            'hoc_van_json.array' => 'Danh sách học vấn không hợp lệ.',
            'hoc_van_json.*.truong.required_with' => 'Tên trường học không được để trống.',
            'du_an_json.array' => 'Danh sách dự án không hợp lệ.',
            'du_an_json.*.ten.required_with' => 'Tên dự án không được để trống.',
            'du_an_json.*.link.url' => 'Link dự án phải là URL hợp lệ.',
            'chung_chi_json.array' => 'Danh sách chứng chỉ không hợp lệ.',
            'chung_chi_json.*.ten.required_with' => 'Tên chứng chỉ không được để trống.',
            'chung_chi_json.*.nam.digits' => 'Năm cấp chứng chỉ phải gồm 4 chữ số.',
            'trang_thai.in' => 'Trạng thái phải là 0 (ẩn) hoặc 1 (công khai).',
        ];
    }
}
