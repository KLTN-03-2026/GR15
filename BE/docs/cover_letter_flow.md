# Cover Letter Generator Flow

## 1. Mục tiêu

Chức năng `Cover Letter Generator` được thiết kế theo mô hình:

- AI sinh **bản nháp**
- người dùng xem và có thể chỉnh sửa
- người dùng **xác nhận**
- hệ thống lưu **bản chính thức**

Việc tách 2 bước này giúp phân biệt rõ:

- `thu_xin_viec_ai`: bản AI sinh ra để gợi ý
- `thu_xin_viec`: bản cuối cùng người dùng đồng ý dùng để nộp

## 2. Luồng FE -> BE -> AI

### Bước 1: Người dùng yêu cầu tạo thư xin việc

FE gọi:

`POST /api/v1/ung-vien/ung-tuyens/generate-cover-letter`

Body:

```json
{
  "ho_so_id": 1,
  "tin_tuyen_dung_id": 10
}
```

### Bước 2: BE chuẩn bị dữ liệu đầu vào

BE lấy:

- hồ sơ ứng viên và `ho_so_parsings`
- tin tuyển dụng, `tin_tuyen_dung_parsings`, `tin_tuyen_dung_ky_nangs`
- kết quả matching gần nhất trong `ket_qua_matchings`

BE gom thành:

- `cv_profile`
- `jd_profile`
- `matching_profile`

rồi gọi AI service.

### Bước 3: AI tạo thư nháp

AI nhận dữ liệu và dùng provider phù hợp:

- `template`
- `ollama`
- `openai`

AI luôn được ép sinh nội dung bằng **tiếng Việt**.

AI trả về:

```json
{
  "success": true,
  "model_version": "cover_letter::template",
  "data": {
    "thu_xin_viec_ai": "..."
  }
}
```

### Bước 4: BE lưu bản nháp

BE tạo hoặc cập nhật bản ghi `ung_tuyens`:

- `thu_xin_viec_ai` = nội dung AI sinh
- `thu_xin_viec` vẫn chưa chốt

### Bước 5: FE hiển thị bản nháp cho người dùng

FE hiển thị:

- nội dung `thu_xin_viec_ai`
- form cho phép chỉnh sửa

Người dùng có thể:

- dùng nguyên bản nháp AI
- chỉnh sửa lại

### Bước 6: Người dùng xác nhận thành bản chính thức

FE gọi:

`PATCH /api/v1/ung-vien/ung-tuyens/{id}/confirm-cover-letter`

Có 2 trường hợp:

#### Trường hợp A: Không sửa gì

Body có thể để trống:

```json
{}
```

BE sẽ lấy `thu_xin_viec_ai` làm bản chính thức.

#### Trường hợp B: Có chỉnh sửa

Body:

```json
{
  "thu_xin_viec": "Nội dung đã được người dùng chỉnh sửa..."
}
```

BE sẽ lưu nội dung này vào `thu_xin_viec`.

### Bước 7: Database lưu bản cuối

Sau khi xác nhận:

- `thu_xin_viec_ai`: vẫn giữ lại bản AI sinh
- `thu_xin_viec`: là bản chính thức dùng để nộp

## 3. Ý nghĩa nghiệp vụ

Thiết kế này giúp:

- bảo toàn bản AI gốc để so sánh hoặc audit
- người dùng luôn là người chịu trách nhiệm nội dung cuối cùng
- phù hợp với UX thực tế của hệ thống tuyển dụng
- dễ giải thích trong báo cáo khóa luận

## 4. Provider-based generation

Phần AI tạo sinh hiện hỗ trợ 3 provider:

- `template`
- `ollama`
- `openai`

Chọn bằng biến môi trường:

```env
COVER_LETTER_PROVIDER=template
```

Hoặc:

```env
COVER_LETTER_PROVIDER=ollama
OLLAMA_URL=http://127.0.0.1:11434/api/generate
OLLAMA_MODEL=qwen2.5:3b
```

Hoặc:

```env
COVER_LETTER_PROVIDER=openai
OPENAI_API_KEY=your_key
OPENAI_MODEL=gpt-4.1-mini
```

## 5. Gợi ý FE

Giao diện nên có:

- nút `Tạo thư xin việc bằng AI`
- textarea hiển thị thư nháp
- nút `Xác nhận dùng bản này`
- hoặc `Lưu thư chính thức`

Nếu người dùng chỉnh sửa, FE gửi nội dung đã sửa lên endpoint confirm.
