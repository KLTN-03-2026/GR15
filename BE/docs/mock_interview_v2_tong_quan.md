# Mock Interview v2

## 1. Mục tiêu của v2

`Mock Interview v2` là phiên bản nâng cấp từ `v1`, tập trung vào ba mục tiêu chính:

- tăng độ giống một buổi phỏng vấn thật
- tăng chất lượng đánh giá sau mỗi phiên
- tăng khả năng mở rộng về AI provider và loại câu hỏi

Nếu `v1` ưu tiên ổn định, dễ test và dễ giải thích, thì `v2` hướng tới:

- trải nghiệm phỏng vấn tốt hơn
- phản hồi chi tiết hơn
- đánh giá chính xác hơn theo vai trò, kỹ năng và mức độ phù hợp với JD

## 2. So với v1, v2 nâng cấp ở đâu

### v1 hiện có

- tạo phiên mock interview
- sinh câu hỏi đầu tiên tự động
- cho phép trả lời từng lượt
- tự sinh câu hỏi tiếp theo
- chấm điểm nội bộ từng lượt
- chỉ hiển thị câu hỏi trong giao diện
- sinh báo cáo tổng kết cuối phiên
- cho phép chọn số câu hỏi và có thanh tiến độ

### v2 sẽ nâng cấp thêm

- adaptive interview:
  - câu hỏi tiếp theo thay đổi theo chất lượng câu trả lời trước
- rubric chi tiết hơn:
  - không chỉ kỹ thuật, giao tiếp, phù hợp JD
  - mà còn chấm theo cấu trúc trả lời, độ rõ ràng, độ cụ thể, mức độ thuyết phục
- AI provider-based thật hơn:
  - hỗ trợ `Ollama`, `OpenAI`, fallback rule-based
- follow-up question thông minh:
  - bám vào câu trả lời của ứng viên thay vì chỉ đi theo question plan cứng
- báo cáo cuối sâu hơn:
  - phân tích theo nhóm kỹ năng
  - đề xuất cải thiện theo giai đoạn
  - gợi ý cách trả lời tốt hơn
- lịch sử tiến bộ theo nhiều phiên

## 3. Kiến trúc v2

### FE

FE tiếp tục dùng màn hình AI Center hiện tại, nhưng bổ sung:

- badge loại câu hỏi:
  - kỹ thuật
  - hành vi
  - xử lý tình huống
  - khoảng trống kỹ năng
- hiển thị tiến độ chi tiết hơn
- nút xem rubric từng câu sau khi kết thúc phiên
- so sánh nhanh giữa các phiên gần nhất

### BE

Laravel tiếp tục giữ vai trò:

- quản lý session
- lưu transcript
- lưu feedback từng lượt
- lưu báo cáo cuối
- chuẩn hóa context gửi sang AI

Ở `v2`, BE nên bổ sung thêm:

- `interview_config` theo phiên:
  - số câu
  - độ khó
  - mục tiêu phỏng vấn
  - kiểu phỏng vấn
- `question_trace`:
  - lưu vì sao câu hỏi tiếp theo được chọn
- `evaluation_trace`:
  - lưu rubric từng câu

### AI

FastAPI trong `v2` không chỉ sinh câu hỏi theo plan tĩnh nữa, mà sẽ có:

- `question planner`
- `answer evaluator`
- `follow-up generator`
- `report synthesizer`

Tức là luồng AI sẽ được chia rõ hơn:

1. xác định giai đoạn phỏng vấn hiện tại
2. đánh giá câu trả lời vừa xong
3. quyết định câu tiếp theo nên:
   - đào sâu kỹ thuật
   - hỏi follow-up
   - chuyển sang câu hành vi
   - hỏi vào khoảng trống kỹ năng
4. sinh báo cáo tổng kết cuối

## 4. Những thành phần AI nên có trong v2

### 4.1. Interview Planner

Dựa trên:

- hồ sơ ứng viên
- JD
- top matching
- career report
- transcript hiện tại
- điểm từng câu trước đó

Planner sẽ quyết định:

- đang ở giai đoạn nào
- có nên hỏi tiếp vào một skill cụ thể không
- có nên tăng độ khó không
- có nên chuyển sang hành vi/phối hợp không

### 4.2. Answer Evaluator

Evaluator chấm không chỉ nội dung, mà cả cách trả lời:

- `technical_score`
- `communication_score`
- `jd_fit_score`
- `clarity_score`
- `specificity_score`
- `structure_score`

Ngoài ra có thể gắn cờ:

- trả lời quá ngắn
- thiếu ví dụ
- né tránh skill còn yếu
- trả lời chung chung

### 4.3. Follow-up Generator

Nếu ứng viên trả lời:

- thiếu cụ thể
- thiếu ví dụ
- né skill yếu
- chỉ nói lý thuyết

thì thay vì chuyển luôn sang câu khác, hệ thống có thể hỏi tiếp:

- "Bạn có thể nêu ví dụ cụ thể hơn không?"
- "Bạn đã từng dùng skill đó trong dự án thật chưa?"
- "Nếu chưa mạnh skill này thì bạn sẽ bắt nhịp như thế nào?"

### 4.4. Report Synthesizer

Báo cáo cuối của `v2` nên gồm:

- tổng điểm
- điểm theo từng tiêu chí
- điểm mạnh nổi bật
- điểm yếu nổi bật
- nhóm kỹ năng cần ưu tiên
- gợi ý trả lời tốt hơn cho 1-2 câu yếu nhất
- kế hoạch cải thiện ngắn hạn

## 5. V2 nên hỗ trợ những loại phỏng vấn nào

`v2` nên cho phép chọn:

- `backend`
- `frontend`
- `mobile`
- `data`
- `qa`
- `devops`
- `general_hr`

Ngoài ra nên có mức độ:

- `fresher`
- `junior`
- `middle`

Như vậy câu hỏi và rubric sẽ sát hơn.

## 6. Trải nghiệm UI nên có trong v2

### Trong lúc phỏng vấn

- chỉ hiện câu hỏi đang hỏi
- có thanh tiến độ
- có badge loại câu hỏi
- có thể hiện nhẹ:
  - "đang đánh giá câu trả lời"

### Sau khi kết thúc

- mở báo cáo tổng kết
- tab:
  - tổng quan
  - từng tiêu chí
  - câu trả lời cần cải thiện
  - gợi ý luyện tiếp

## 7. Công nghệ đề xuất cho v2

### Giữ nguyên

- FE: Vue
- BE: Laravel
- AI service: FastAPI
- DB: MySQL

### Bổ sung

- local AI:
  - `Ollama`
  - model nhẹ để test local
- cloud AI:
  - `OpenAI`

### Cơ chế provider

`Mock Interview v2` nên đi theo hướng provider-based giống chatbot:

- `rule_based`
- `ollama`
- `openai`

Trong đó:

- `rule_based` là fallback ổn định
- `ollama/openai` để tăng tự nhiên và chiều sâu

## 8. Phần đã nên triển khai trong v2 giai đoạn đầu

Để không làm quá nặng ngay một lần, `v2` nên chia thành 2 bước:

### v2.0

- adaptive question selection
- rubric chi tiết hơn
- follow-up question cơ bản
- báo cáo cuối chi tiết hơn

### Những gì đã triển khai trong bản v2.0 hiện tại

- số câu hỏi theo từng phiên vẫn giữ được như v1.1
- AI chấm thêm các tiêu chí:
  - `clarity_score`
  - `specificity_score`
  - `structure_score`
- câu hỏi tiếp theo có thể đổi theo chất lượng câu vừa trả lời
- nếu câu trả lời còn yếu hoặc quá chung chung, hệ thống có thể sinh câu `follow_up`
- báo cáo cuối có thêm:
  - `rubric_summary`
  - `weakest_dimension`
  - `weakest_answer_summary`
  - `recommended_focus`
  - `practice_plan`
- UI đã hiển thị thêm:
  - rubric phụ
  - phần ưu tiên cải thiện
  - kế hoạch luyện tiếp
  - câu trả lời yếu nhất cần cải thiện

### v2.1

- provider-based AI cho mock interview
- phản hồi tự nhiên hơn
- badge loại câu hỏi
- so sánh nhiều phiên

## 9. Những gì mình đề xuất làm ngay sau v1

Nếu tiếp tục triển khai từ codebase hiện tại, bước nâng hợp lý nhất là:

1. thêm `interview_intent/type engine`
2. thêm `adaptive next question`
3. thêm `rubric chi tiết`
4. nâng `report`
5. thêm `provider-based explanation`

Đây là thứ tự tốt vì:

- ít phá kiến trúc hiện tại
- dễ test từng lớp
- mỗi lớp đều tạo khác biệt rõ trên UI

## 10. Kết luận

`Mock Interview v2` nên được hiểu là:

- từ một hệ thống hỏi đáp phỏng vấn theo plan cố định
- nâng lên thành một hệ thống phỏng vấn thích ứng, có rubric rõ, có follow-up hợp lý, có báo cáo sâu và có thể dùng AI provider để diễn giải tự nhiên hơn

Với codebase hiện tại, hướng nâng cấp này là khả thi và bám tốt vào những gì đã có trong:

- `ai_chat_sessions`
- `ai_chat_messages`
- `ai_interview_reports`
- `CV parsing`
- `matching`
- `career report`
- `job parsing`
