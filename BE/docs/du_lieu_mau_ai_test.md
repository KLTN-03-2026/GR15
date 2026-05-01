# Dữ liệu mẫu và hướng dẫn test AI integration

Tài liệu này dùng kèm với:

- `KLTN_AI_Integration_Test.postman_collection.json`
- `KLTN_AI_Integration_Local.postman_environment.json`

## 1. Điều kiện trước khi test

### AI service

```bash
cd /Users/doankhanhmai/KLTN/AI
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

### BE service

```bash
cd /Users/doankhanhmai/KLTN/BE
php artisan serve
```

Đảm bảo `.env` trong `BE` có:

```env
AI_SERVICE_URL=http://127.0.0.1:8001
AI_SERVICE_TIMEOUT=120
```

## 2. Thứ tự test đề xuất trong Postman

### Bước 1 - Public và Auth

1. `Public - Get Industries`
2. `Candidate - Register`
3. `Candidate - Login`
4. `Recruiter - Register`
5. `Recruiter - Login`

Lưu ý:
- nếu tài khoản đã tồn tại, có thể bỏ qua request register và chỉ login
- `nganh_nghe_id` cần được set lại nếu hệ thống không có id = 1

### Bước 2 - Recruiter setup

1. `Recruiter - Create Company`
2. `Recruiter - Create Job`

Khi request thành công:
- `cong_ty_id` sẽ được lưu vào environment
- `tin_tuyen_dung_id` sẽ được lưu vào environment

### Bước 3 - Candidate setup

1. `Candidate - Create CV`

Lưu ý quan trọng:
- request này cần gắn tay 1 file PDF CV thật vào trường `file_cv`
- sau khi tạo thành công, `ho_so_id` sẽ được lưu vào environment

### Bước 4 - Test AI direct

1. `AI - Health`
2. `AI - Parse CV Direct`
3. `AI - Parse JD Direct`
4. `AI - Matching Direct`
5. `AI - Cover Letter Direct`
6. `AI - Career Report Direct`

### Bước 5 - Test AI qua BE

1. `Candidate - Parse CV via BE`
2. `Recruiter - Parse JD via BE`
3. `Candidate - Generate Matching via BE`
4. `Candidate - Generate Cover Letter via BE`
5. `Candidate - Generate Career Report via BE`
6. `Candidate - View Matching List`
7. `Candidate - View Career Reports`

## 3. Du lieu mau

### Tài khoản ứng viên

```json
{
  "ho_ten": "Ứng viên AI Test",
  "email": "candidate.ai.test@example.com",
  "mat_khau": "12345678",
  "mat_khau_confirmation": "12345678",
  "so_dien_thoai": "0901234567",
  "vai_tro": 0
}
```

### Tài khoản nhà tuyển dụng

```json
{
  "ho_ten": "Nhà tuyển dụng AI Test",
  "email": "recruiter.ai.test@example.com",
  "mat_khau": "12345678",
  "mat_khau_confirmation": "12345678",
  "so_dien_thoai": "0902345678",
  "vai_tro": 1
}
```

### Công ty mẫu

```json
{
  "ten_cong_ty": "Công ty AI Test",
  "ma_so_thue": "0312345678",
  "dia_chi": "Đà Nẵng",
  "email": "company-ai@example.com",
  "website": "https://example.com",
  "quy_mo": "11-50",
  "nganh_nghe_id": 1
}
```

### Tin tuyển dụng mẫu

```json
{
  "tieu_de": "Backend Developer Laravel",
  "mo_ta_cong_viec": "Tuyển dụng Backend Developer. Yêu cầu Laravel, MySQL, REST API, Git. Ưu tiên Docker và kiểm thử. Địa điểm Đà Nẵng. Làm việc toàn thời gian.",
  "dia_diem_lam_viec": "Đà Nẵng",
  "hinh_thuc_lam_viec": "Toàn thời gian",
  "cap_bac": "Nhân viên",
  "so_luong_tuyen": 2,
  "muc_luong": 18000000,
  "kinh_nghiem_yeu_cau": "2 năm",
  "ngay_het_han": "2026-12-31",
  "nganh_nghes": [1]
}
```

### Hồ sơ/CV mẫu

```json
{
  "tieu_de_ho_so": "CV Backend Laravel",
  "muc_tieu_nghe_nghiep": "Trở thành Backend Developer chuyên nghiệp.",
  "trinh_do": "dai_hoc",
  "kinh_nghiem_nam": 2,
  "mo_ta_ban_than": "Có kinh nghiệm Laravel, MySQL, REST API.",
  "trang_thai": 1
}
```

Cần gắn thêm file PDF thật cho trường `file_cv`.

## 4. Kiểm tra kết quả trong DB

Sau khi test qua BE, bạn có thể kiểm tra:

- `ho_so_parsings`
- `tin_tuyen_dung_parsings`
- `tin_tuyen_dung_ky_nangs`
- `ket_qua_matchings`
- `ung_tuyens`
- `tu_van_nghe_nghieps`

## 5. Lỗi thường gặp

### 401 / 403
- token sai
- chưa login
- sai vai trò

### 422
- thiếu `nganh_nghe_id` hợp lệ
- chưa gắn file CV thật
- dữ liệu body sai validate

### 502
-- AI service chưa chạy
- `AI_SERVICE_URL` sai
- AI service trả lời sai contract

## 6. Ghi chú

Hiện tại AI service đang ở dạng skeleton/mock:

- parse CV/JD chưa đọc file thật
- matching chưa tính thật
- cover letter và career report đang trả dữ liệu mẫu

Bộ test này được tạo để:
- xác minh BE đã nối đúng với AI service
- xác minh route mới và DB mới hoạt động đúng luồng
- sẵn sàng cho bước thay logic mock bằng logic AI thật
