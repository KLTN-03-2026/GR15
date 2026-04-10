# Thiết Kế Chatbot V1 Thử Nghiệm

## 1. Mục tiêu của bản v1
Chatbot v1 được thiết kế để thử nghiệm nhanh nhưng vẫn bám sát dữ liệu thật của hệ thống. Đây không phải chatbot đa năng, mà là một **trợ lý tư vấn nghề nghiệp có giới hạn phạm vi**.

Mục tiêu của phiên bản v1:
- trả lời các câu hỏi liên quan đến hồ sơ CV, kết quả matching, định hướng nghề nghiệp và công việc trong hệ thống
- sử dụng dữ liệu thật đã có từ parser, matching, career report, semantic search
- hỗ trợ cả AI local và AI cloud để dễ test
- có khả năng stream response để giao diện chuyên nghiệp hơn
- từ chối các câu hỏi ngoài phạm vi bằng một câu trả lời mẫu thống nhất

## 2. Phạm vi hỗ trợ

### 2.1. Câu hỏi được phép
Chatbot chỉ trả lời các câu hỏi liên quan đến:
- hồ sơ CV đã phân tích
- kết quả matching
- nghề nghiệp phù hợp
- kỹ năng còn thiếu
- công việc nên ứng tuyển
- semantic search job trong hệ thống
- gợi ý cải thiện hồ sơ, cover letter, chuẩn bị phỏng vấn

Ví dụ:
- “Vì sao hồ sơ của tôi chỉ match 56 điểm?”
- “Tôi nên học gì để phù hợp hơn với vị trí backend?”
- “Trong hệ thống hiện có job nào gần nhất với hồ sơ của tôi?”
- “Tôi nên sửa CV như thế nào để tăng điểm matching?”

### 2.2. Câu hỏi ngoài phạm vi
Chatbot không trả lời các câu hỏi ngoài domain hệ thống.

Ví dụ:
- “Hôm nay thời tiết thế nào?”
- “Viết giúp tôi một bài văn”
- “Ai là tổng thống Mỹ?”
- “Giải giúp tôi bài toán này”

### 2.3. Câu trả lời mẫu khi ngoài phạm vi
Khi phát hiện câu hỏi ngoài phạm vi, chatbot trả lời:

> Tôi được thiết kế để hỗ trợ tư vấn nghề nghiệp, giải thích hồ sơ CV, kết quả matching và thông tin tuyển dụng trong hệ thống. Với câu hỏi này, tôi chưa phải là trợ lý phù hợp. Bạn có thể hỏi tôi về nghề nghiệp, kỹ năng cần bổ sung, CV, thư xin việc hoặc công việc phù hợp với hồ sơ của bạn.

## 3. Tận dụng schema hiện có
Hệ thống hiện đã có sẵn 2 bảng phù hợp để triển khai chatbot v1:

### 3.1. `ai_chat_sessions`
Dùng để lưu phiên chat.

Các cột hiện có:
- `nguoi_dung_id`
- `session_type`
- `related_ho_so_id`
- `related_tin_tuyen_dung_id`
- `status`
- `title`
- `summary`

Trong v1, session chatbot tư vấn nghề nghiệp sẽ dùng:
- `session_type = career_consultant`
- `related_ho_so_id`: hồ sơ ứng viên đang được tư vấn
- `related_tin_tuyen_dung_id`: job liên quan nếu user chat xoay quanh một JD cụ thể

### 3.2. `ai_chat_messages`
Dùng để lưu message trong hội thoại.

Các cột hiện có:
- `session_id`
- `role`
- `content`
- `metadata`
- `created_at`

Trong v1:
- `role = user` cho tin nhắn user
- `role = assistant` cho câu trả lời chatbot
- `metadata` dùng để lưu:
  - `model_version`
  - `provider`
  - `streamed`
  - `guardrail_triggered`

## 4. Nguồn dữ liệu ngữ cảnh
Chatbot v1 không nên trả lời tự do. Nó phải dựa trên dữ liệu thật từ hệ thống.

### 4.1. Context ưu tiên
- `ho_so_parsings`
- `ket_qua_matchings`
- `tu_van_nghe_nghieps`
- `tin_tuyen_dungs`
- `tin_tuyen_dung_parsings`
- `tin_tuyen_dung_ky_nangs`
- `semantic search`

### 4.2. Context package đề xuất
Trước khi gọi AI, backend cần dựng một `context package` như sau:

```json
{
  "candidate_profile": {
    "ho_ten": "...",
    "tieu_de_ho_so": "...",
    "kinh_nghiem_nam": 2,
    "trinh_do": "Đại học",
    "parsed_skills": ["Laravel", "MySQL", "REST API"]
  },
  "career_report": {
    "nghe_de_xuat": "...",
    "muc_do_phu_hop": 78.5,
    "goi_y_ky_nang_bo_sung": [...]
  },
  "top_matching_jobs": [
    {
      "job_title": "...",
      "score": 82.1,
      "missing_skills": [...]
    }
  ],
  "related_job": {
    "title": "...",
    "skills": [...]
  }
}
```

## 5. Kiến trúc tổng thể

### 5.1. Thành phần
- `FE`: giao diện chat
- `BE (Laravel)`: session, message, context builder, gọi AI service
- `AI Service (FastAPI)`: guardrail, prompt builder, provider selector, response generator
- `LLM Provider`: local hoặc cloud

### 5.2. Luồng tổng quát
```text
FE -> BE -> AI Service -> LLM Provider
             ^
             |
    CV / Matching / Career Report / Semantic Search
```

## 6. Luồng hoạt động v1

### 6.1. Tạo session
FE gọi API tạo session:

```http
POST /api/v1/ai-chat/sessions
```

Input:
- `related_ho_so_id`
- `related_tin_tuyen_dung_id` nullable
- `title` nullable

Kết quả:
- BE tạo bản ghi trong `ai_chat_sessions`

### 6.2. Gửi message
FE gọi:

```http
POST /api/v1/ai-chat/messages
```

Input:
```json
{
  "session_id": 1,
  "message": "Tôi nên học gì để phù hợp hơn với job backend?"
}
```

### 6.3. Backend xử lý
BE làm các bước:
1. kiểm tra session có thuộc user không
2. lưu user message vào `ai_chat_messages`
3. xây context từ DB
4. gửi sang AI service
5. nhận câu trả lời
6. lưu assistant message
7. trả response cho FE

## 7. Guardrail và domain filter
Chatbot v1 cần có một lớp kiểm tra câu hỏi trước khi gọi LLM.

### 7.1. Cách hoạt động
AI service sẽ:
- phân tích câu hỏi
- kiểm tra xem câu hỏi có thuộc domain nghề nghiệp/tuyển dụng của hệ thống không

### 7.2. Nếu trong phạm vi
- chuyển sang bước build prompt và sinh câu trả lời

### 7.3. Nếu ngoài phạm vi
- không gọi generation sâu
- trả câu trả lời mẫu đã định nghĩa
- đánh dấu trong metadata:
  - `guardrail_triggered = true`

## 8. Provider-based để dễ test local và cloud
Chatbot v1 nên dùng cùng triết lý với cover letter:

### 8.1. Provider local
- `Ollama`
- model ví dụ:
  - `qwen3`
  - `llama3`

### 8.2. Provider cloud
- `OpenAI`
- có thể mở rộng sang `Gemini`

### 8.3. Provider fallback
- `template`

Provider fallback hữu ích để:
- test luồng nghiệp vụ
- test FE/BE trước khi bật model thật

### 8.4. Cấu hình đề xuất
Trong `AI/.env`:

```env
CHATBOT_PROVIDER=template
CHATBOT_STREAM_ENABLED=true
```

Khi dùng local:

```env
CHATBOT_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5:3b
```

Khi dùng cloud:

```env
CHATBOT_PROVIDER=openai
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4.1-mini
```

## 9. Prompt strategy
Prompt hệ thống của chatbot cần quy định rõ:
- chỉ trả lời bằng tiếng Việt có dấu
- chỉ sử dụng dữ liệu được cung cấp trong context
- nếu dữ liệu chưa đủ thì nói rõ là chưa đủ
- không bịa kỹ năng, công việc hoặc kết quả
- nếu câu hỏi ngoài phạm vi thì dùng câu từ chối chuẩn

## 10. Streaming response

### 10.1. Vì sao nên stream
Chatbot nên stream để:
- tạo cảm giác phản hồi nhanh
- chuyên nghiệp hơn trên UI
- phù hợp với trải nghiệm chat hiện đại

### 10.2. Hướng triển khai
AI service dùng:
- `StreamingResponse`
- content type:
  - `text/event-stream`

### 10.3. Cách hoạt động
1. FE gửi message
2. BE gọi AI endpoint stream
3. AI stream text theo chunk
4. FE append từng đoạn text
5. khi hoàn tất, BE hoặc FE trigger lưu bản cuối

### 10.4. Hai cách lưu message

#### Cách A: lưu sau khi stream hoàn tất
- đơn giản hơn
- phù hợp v1

#### Cách B: lưu chunk tạm rồi finalize
- phức tạp hơn
- chưa cần cho v1

Với v1, nên chọn:
- **stream ra FE**
- **lưu message đầy đủ sau khi kết thúc stream**

## 11. API đề xuất cho v1

### 11.1. Tạo session
```http
POST /api/v1/ai-chat/sessions
```

### 11.2. Lấy danh sách session
```http
GET /api/v1/ai-chat/sessions
```

### 11.3. Gửi message không stream
```http
POST /api/v1/ai-chat/messages
```

### 11.4. Gửi message có stream
```http
POST /api/v1/ai-chat/messages/stream
```

### 11.5. Lấy lịch sử message
```http
GET /api/v1/ai-chat/sessions/{id}/messages
```

### 11.6. Đóng session
```http
PATCH /api/v1/ai-chat/sessions/{id}/status
```

## 12. Thiết kế response

### 12.1. Response thường
```json
{
  "success": true,
  "data": {
    "session_id": 1,
    "assistant_message": {
      "role": "assistant",
      "content": "Dựa trên hồ sơ hiện tại...",
      "model_version": "chatbot_v1::template"
    }
  }
}
```

### 12.2. Response khi ngoài phạm vi
```json
{
  "success": true,
  "data": {
    "assistant_message": {
      "role": "assistant",
      "content": "Tôi được thiết kế để hỗ trợ tư vấn nghề nghiệp...",
      "model_version": "chatbot_v1::guardrail"
    },
    "guardrail_triggered": true
  }
}
```

## 13. Luồng thử nghiệm đề xuất
Để thử nghiệm v1, chatbot nên hỗ trợ trước các câu sau:

### 13.1. Nhóm giải thích matching
- “Vì sao hồ sơ của tôi chưa phù hợp với job này?”
- “Những kỹ năng nào tôi đang thiếu?”

### 13.2. Nhóm định hướng nghề
- “Tôi đang phù hợp nhất với nghề nào?”
- “Nếu muốn lên senior backend thì nên học gì?”

### 13.3. Nhóm gợi ý công việc
- “Trong hệ thống hiện có job nào hợp với tôi?”
- “Job nào nên ưu tiên ứng tuyển trước?”

### 13.4. Nhóm hỗ trợ CV / chuẩn bị
- “Tôi nên sửa CV phần nào?”
- “Tôi nên nhấn mạnh điều gì khi viết thư xin việc?”

## 14. Roadmap triển khai

### Bước 1
- tạo API session
- tạo API message thường
- dùng `template provider`

### Bước 2
- thêm guardrail kiểm tra ngoài phạm vi
- thêm context builder từ CV + matching + career report

### Bước 3
- thêm `ollama provider`
- thêm `openai provider`

### Bước 4
- thêm stream endpoint
- FE render theo stream

## 15. Kết luận
Chatbot v1 thử nghiệm nên được triển khai theo hướng:

- domain-specific
- provider-based
- retrieval-augmented
- có guardrail ngoài phạm vi
- hỗ trợ stream response

Đây là bản thiết kế đủ gọn để triển khai nhanh, nhưng vẫn đủ chắc để mở rộng lên chatbot hoàn chỉnh ở các phiên bản sau.
