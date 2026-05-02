# Mock Interview v1

## 1. Mục tiêu

`Mock Interview` là chức năng mô phỏng phỏng vấn dựa trên:

- hồ sơ ứng viên đã parse
- tin tuyển dụng đang chọn
- kết quả matching
- career report

Mục tiêu của bản `v1` là:

- tạo phiên phỏng vấn thử
- sinh câu hỏi phỏng vấn đầu tiên
- cho phép ứng viên trả lời từng câu
- chấm nhanh câu trả lời theo từng lượt
- sinh câu hỏi tiếp theo theo đúng mạch phỏng vấn
- tạo báo cáo tổng kết cuối phiên

## 2. Kiến trúc v1

### FE

Hiện tại chưa triển khai giao diện riêng trong phạm vi v1. Có thể test qua Postman hoặc nối UI sau.

### BE

Laravel giữ vai trò:

- tạo và quản lý phiên `mock_interview`
- lưu lịch sử hỏi đáp vào `ai_chat_messages`
- xây ngữ cảnh từ hồ sơ, JD, matching, career report
- gọi AI service để:
  - sinh câu hỏi
  - chấm câu trả lời
  - sinh báo cáo cuối
- lưu báo cáo vào `ai_interview_reports`

### AI

FastAPI giữ vai trò:

- sinh bộ câu hỏi phỏng vấn theo hồ sơ và JD
- đánh giá câu trả lời theo rule-based logic ổn định
- tạo báo cáo tổng kết phỏng vấn

## 3. Tận dụng dữ liệu hiện có

V1 tận dụng các bảng sẵn có:

- `ai_chat_sessions`
  - dùng `session_type = mock_interview`
- `ai_chat_messages`
  - lưu câu hỏi phỏng vấn, câu trả lời ứng viên, phản hồi AI
- `ai_interview_reports`
  - lưu báo cáo tổng kết cuối phiên
- `ho_so_parsings`
- `ket_qua_matchings`
- `tu_van_nghe_nghieps`
- `tin_tuyen_dung_parsings`
- `tin_tuyen_dung_ky_nangs`

## 4. Luồng hoạt động v1

### Bước 1: tạo phiên phỏng vấn

Ứng viên chọn:

- hồ sơ
- tin tuyển dụng liên quan
- tiêu đề phiên

BE tạo `ai_chat_session` với:

- `session_type = mock_interview`

Sau đó BE gọi AI để sinh câu hỏi đầu tiên và lưu vào `ai_chat_messages`.

### Bước 2: ứng viên trả lời

Ứng viên gửi câu trả lời cho câu hỏi hiện tại.

BE sẽ:

- lưu câu trả lời của ứng viên
- lấy câu hỏi gần nhất
- dựng context
- gọi AI để:
  - chấm nhanh câu trả lời
  - sinh câu hỏi tiếp theo

AI trả về:

- điểm kỹ thuật
- điểm giao tiếp
- điểm phù hợp JD
- điểm mạnh
- điểm cần cải thiện
- câu hỏi tiếp theo

BE lưu phản hồi AI vào `ai_chat_messages`.

### Bước 3: lặp theo từng lượt

Phiên phỏng vấn tiếp tục cho đến khi:

- đạt số câu tối đa của v1
- hoặc người dùng chủ động kết thúc

### Bước 4: sinh báo cáo cuối

BE lấy transcript và context phiên phỏng vấn, gửi sang AI.

AI tạo báo cáo cuối gồm:

- tổng điểm
- điểm kỹ thuật
- điểm giao tiếp
- điểm phù hợp JD
- các điểm mạnh nổi bật
- các điểm yếu nổi bật
- đề xuất cải thiện

Báo cáo được lưu vào `ai_interview_reports`.

## 5. Công nghệ sử dụng trong v1

- FE: Vue
- BE: Laravel
- AI service: FastAPI
- dữ liệu chính: MySQL
- logic chính của v1: rule-based + context-aware generation

## 6. Vì sao v1 dùng rule-based trước

V1 ưu tiên:

- ổn định
- dễ test
- dễ giải thích khi bảo vệ
- ít sinh lỗi ngữ cảnh hơn

Với chức năng `Mock Interview`, nếu để model tự sinh toàn bộ quá sớm thì rất dễ gặp:

- câu hỏi lặp
- chấm điểm thiếu nhất quán
- phản hồi dài dòng
- khó debug

Do đó v1 dùng:

- question plan theo lượt
- chấm điểm bán cấu trúc
- phản hồi ngắn, rõ, nhất quán

## 7. Phạm vi v1 đã làm được

V1 dự kiến hoàn thành:

- tạo phiên mock interview
- sinh câu hỏi đầu tiên tự động
- trả lời từng lượt
- phản hồi theo từng lượt
- sinh câu hỏi tiếp theo
- tạo báo cáo tổng kết
- lưu lịch sử và báo cáo vào DB

### API v1

- `GET /api/v1/mock-interview/sessions`
- `POST /api/v1/mock-interview/sessions`
- `GET /api/v1/mock-interview/sessions/{id}/messages`
- `POST /api/v1/mock-interview/messages`
- `POST /api/v1/mock-interview/sessions/{id}/report`
- `GET /api/v1/mock-interview/sessions/{id}/report`
- `PATCH /api/v1/mock-interview/sessions/{id}/status`
- `DELETE /api/v1/mock-interview/sessions/{id}`

### V1 hiện đang làm được gì

- tạo phiên `mock_interview`
- tự sinh câu hỏi đầu tiên sau khi tạo phiên
- lưu câu hỏi vào `ai_chat_messages`
- nhận câu trả lời ứng viên
- chấm nhanh theo:
  - điểm kỹ thuật
  - điểm giao tiếp
  - điểm phù hợp JD
- trả phản hồi ngắn gọn cho từng lượt
- sinh câu hỏi tiếp theo theo từng giai đoạn
- tự kết thúc sau số câu tối đa của v1
- sinh báo cáo tổng kết và lưu vào `ai_interview_reports`

### Cách test ngắn gọn cho v1

1. tạo session mock interview
2. lấy message đầu tiên để xem câu hỏi mở đầu
3. gửi câu trả lời qua endpoint `POST /mock-interview/messages`
4. lặp lại vài lượt
5. gọi `POST /mock-interview/sessions/{id}/report`
6. lấy báo cáo bằng `GET /mock-interview/sessions/{id}/report`

## 8. Giới hạn của v1

V1 chưa tập trung vào:

- phỏng vấn voice
- nhận diện cảm xúc / tốc độ nói
- agentic interview động hoàn toàn
- adaptive branching quá sâu
- provider-based streaming riêng cho phỏng vấn

## 9. Hướng nâng cấp sau v1

### v1.1

- thêm stream response cho phản hồi phỏng vấn
- thêm câu hỏi follow-up linh hoạt hơn
- thêm badge loại câu hỏi:
  - technical
  - behavioral
  - experience
  - gap-skill

### v2

- cho phép dùng `Ollama/OpenAI` để diễn giải phản hồi tự nhiên hơn
- adaptive interview theo performance từng câu
- scoring rubric chi tiết hơn

### v3

- voice mock interview
- transcript theo thời gian thực
- chấm confidence / clarity / structure
- dashboard tiến bộ theo nhiều phiên

## 10. Kết luận

`Mock Interview v1` được thiết kế theo hướng:

- tận dụng tối đa dữ liệu AI đã có trong hệ thống
- triển khai gọn, ổn định, dễ test
- đủ tốt để mở rộng thành một hệ sinh thái luyện phỏng vấn hoàn chỉnh ở các phiên bản sau
