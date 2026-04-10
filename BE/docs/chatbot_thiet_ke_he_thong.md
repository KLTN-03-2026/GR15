# Thiết Kế Hệ Thống Chatbot Tư Vấn Nghề Nghiệp

## 1. Mục tiêu
Chatbot trong hệ thống được thiết kế như một **trợ lý tư vấn nghề nghiệp có ngữ cảnh**, không phải chatbot trò chuyện tự do. Mục tiêu chính là hỗ trợ người dùng khai thác các dữ liệu đã có trong hệ thống như:

- hồ sơ CV đã phân tích
- kết quả matching với tin tuyển dụng
- báo cáo tư vấn nghề nghiệp
- dữ liệu tin tuyển dụng trong hệ thống
- kết quả semantic search

Chatbot phải giúp người dùng:

- hiểu vì sao hồ sơ phù hợp hoặc chưa phù hợp với một vị trí
- biết nên học thêm kỹ năng gì
- xác định hướng nghề nghiệp nên ưu tiên
- chọn công việc nên ứng tuyển
- chuẩn bị CV, thư xin việc và phỏng vấn tốt hơn

## 2. Phạm vi trả lời
Chatbot **chỉ trả lời các câu hỏi có liên quan đến hệ thống**. Điều này rất quan trọng để:

- giảm nguy cơ trả lời lan man
- hạn chế bịa thông tin
- đảm bảo chất lượng tư vấn
- giúp hệ thống nhất quán khi demo và bảo vệ

### 2.1. Các nhóm câu hỏi được phép trả lời
- giải thích hồ sơ CV đã phân tích
- giải thích kết quả matching
- gợi ý nghề phù hợp
- gợi ý kỹ năng nên bổ sung
- gợi ý các công việc nên ứng tuyển
- giải thích vì sao một job phù hợp hoặc chưa phù hợp
- hỗ trợ chỉnh hướng CV, cover letter, chuẩn bị phỏng vấn

### 2.2. Các nhóm câu hỏi không thuộc phạm vi
- kiến thức chung không liên quan đến nghề nghiệp trong hệ thống
- hỏi đáp đời sống, giải trí, chính trị, tôn giáo
- yêu cầu giải toán, viết văn, trả lời tri thức bách khoa không liên quan
- yêu cầu vượt ngoài dữ liệu mà hệ thống đang có

## 3. Cơ chế từ chối câu hỏi ngoài phạm vi
Khi người dùng hỏi câu không liên quan đến hệ thống, chatbot không nên cố trả lời. Thay vào đó, chatbot cần phản hồi bằng một câu mẫu thống nhất, ví dụ:

> Tôi được thiết kế để hỗ trợ tư vấn nghề nghiệp, giải thích hồ sơ CV, kết quả matching và thông tin tuyển dụng trong hệ thống. Với câu hỏi này, tôi chưa phải là trợ lý phù hợp. Bạn có thể hỏi tôi về nghề nghiệp, kỹ năng cần bổ sung, CV, thư xin việc hoặc công việc phù hợp với hồ sơ của bạn.

Mục tiêu của cơ chế này là:

- giữ chatbot trong đúng domain
- tăng độ tin cậy
- tránh tạo cảm giác chatbot “biết tất cả” nhưng trả lời sai

## 4. Kiến trúc tổng thể

### 4.1. Các thành phần
- `FE`: giao diện chat cho người dùng
- `BE (Laravel)`: quản lý session, message, lấy dữ liệu ngữ cảnh và gọi AI service
- `AI Service (FastAPI)`: xử lý logic chatbot, chọn provider local/cloud, dựng prompt và sinh câu trả lời
- `DB (MySQL)`: lưu session chat, message và các dữ liệu ngữ cảnh khác
- `LLM Provider`: local hoặc cloud

### 4.2. Nguồn dữ liệu ngữ cảnh
Chatbot lấy dữ liệu từ các thành phần đã có trong hệ thống:

- `ho_so_parsings`
- `ket_qua_matchings`
- `tu_van_nghe_nghieps`
- `tin_tuyen_dungs`
- `tin_tuyen_dung_parsings`
- `tin_tuyen_dung_ky_nangs`
- `semantic search`

## 5. Mô hình vận hành

### 5.1. Luồng cơ bản
1. Người dùng mở chatbot và tạo một session mới.
2. Người dùng gửi câu hỏi.
3. Backend kiểm tra session có thuộc người dùng hiện tại hay không.
4. Backend thu thập ngữ cảnh phù hợp từ hệ thống.
5. Backend gửi message và context sang AI service.
6. AI service kiểm tra câu hỏi có thuộc phạm vi hỗ trợ hay không.
7. Nếu câu hỏi hợp lệ, AI service chọn provider và sinh câu trả lời.
8. Nếu câu hỏi ngoài phạm vi, AI service trả về câu phản hồi mẫu.
9. Backend lưu hội thoại vào database.
10. Frontend hiển thị câu trả lời theo luồng stream.

### 5.2. Luồng dữ liệu
```text
FE -> BE -> AI Service -> LLM Provider
             ^
             |
   CV / Matching / Report / JD / Semantic Search
```

## 6. Thiết kế provider local và cloud
Chatbot nên dùng mô hình `provider-based`, tương tự như phần cover letter.

### 6.1. Provider local
Dùng khi:
- phát triển local
- demo offline
- tiết kiệm chi phí

Công nghệ:
- `Ollama`
- model ví dụ:
  - `qwen3`
  - `llama3`

### 6.2. Provider cloud
Dùng khi:
- staging
- production
- cần chất lượng trả lời ổn định hơn

Công nghệ:
- `OpenAI`
- có thể mở rộng sang `Gemini`

### 6.3. Provider fallback
Có thể dùng `template provider` hoặc `guard provider` trong giai đoạn đầu để:
- kiểm tra luồng nghiệp vụ
- test khi chưa bật model thật

## 7. Thiết kế database
Hệ thống đã có sẵn các bảng phù hợp:

### 7.1. `ai_chat_sessions`
Dùng để lưu thông tin một phiên chat.

Đề xuất ý nghĩa:
- `nguoi_dung_id`: chủ session
- `ho_so_id`: hồ sơ đang được tư vấn
- `session_type`: ví dụ `career_consultant`
- `tieu_de`: tiêu đề session
- `context_snapshot_json`: snapshot context khi cần
- `trang_thai`: trạng thái phiên chat

### 7.2. `ai_chat_messages`
Dùng để lưu từng tin nhắn trong phiên chat.

Đề xuất ý nghĩa:
- `session_id`
- `vai_tro`: `user`, `assistant`, `system`
- `noi_dung`
- `metadata_json`
- `model_version`

## 8. Phân loại và kiểm soát câu hỏi
Chatbot phải có lớp kiểm tra trước khi sinh câu trả lời.

### 8.1. Nếu câu hỏi thuộc phạm vi
Ví dụ:
- “Tôi đang thiếu kỹ năng gì để phù hợp hơn với job backend?”
- “Vì sao hồ sơ của tôi chỉ match 56 điểm?”
- “Tôi nên ứng tuyển vị trí nào trong hệ thống?”

Khi đó:
- hệ thống lấy context phù hợp
- sinh câu trả lời dựa trên dữ liệu thật

### 8.2. Nếu câu hỏi ngoài phạm vi
Ví dụ:
- “Thời tiết hôm nay thế nào?”
- “Viết hộ tôi một bài văn”
- “Ai là tổng thống Mỹ?”

Khi đó:
- chatbot không gọi luồng tư vấn sâu
- trả câu từ chối mẫu

## 9. Chiến lược sinh câu trả lời
Chatbot không nên dựa hoàn toàn vào LLM tự do. Thay vào đó, cần dùng hướng:

### 9.1. Retrieval-augmented conversation
Trước khi gọi model, hệ thống cần dựng `context package`, ví dụ:

- thông tin hồ sơ đã parse
- top matching jobs
- kỹ năng còn thiếu
- nghề đề xuất từ career report
- một số job gần nhất từ semantic search nếu câu hỏi liên quan đến việc làm

### 9.2. Prompt giới hạn phạm vi
Prompt hệ thống nên quy định:
- chỉ trả lời bằng tiếng Việt có dấu
- chỉ dùng ngữ cảnh được cung cấp
- nếu thiếu dữ liệu thì nói rõ
- không được bịa thông tin ngoài hệ thống
- nếu câu hỏi ngoài phạm vi thì trả câu từ chối chuẩn

## 10. Thiết kế stream response
Để trải nghiệm chuyên nghiệp hơn, chatbot nên trả lời theo **stream** thay vì chờ xong toàn bộ mới trả về.

### 10.1. Lý do nên stream
- tạo cảm giác phản hồi nhanh hơn
- chuyên nghiệp hơn trên giao diện
- phù hợp với trải nghiệm chat hiện đại
- giảm cảm giác hệ thống bị “đơ” khi model local/cloud trả lời chậm

### 10.2. Hướng triển khai
Có thể dùng:
- `StreamingResponse` trong FastAPI
- `text/event-stream` hoặc SSE

Luồng:
1. FE gửi message
2. BE chuyển yêu cầu sang AI service
3. AI service gọi provider hỗ trợ stream
4. AI service trả token/chunk dần về FE qua BE hoặc qua endpoint stream riêng

### 10.3. Hiển thị trên UI
Frontend nên:
- hiển thị typing indicator
- append từng chunk nội dung
- khi stream hoàn tất thì lưu message đầy đủ

## 11. Luồng đề xuất cho phiên bản v1
Chatbot v1 nên có phạm vi gọn nhưng thực dụng:

- tạo session
- gửi message
- lưu message
- trả lời trong domain nghề nghiệp
- từ chối câu hỏi ngoài phạm vi
- dùng context từ:
  - CV parsed
  - top 3 matching
  - career report gần nhất
- hỗ trợ stream response
- provider-based:
  - `template`
  - `ollama`
  - `openai`

## 12. Luồng kỹ thuật chi tiết

### 12.1. FE
- tạo session chat
- gửi message
- nhận stream response
- render hội thoại

### 12.2. BE
- xác thực người dùng
- kiểm tra session
- lấy context từ DB
- gọi `AiClientService`
- lưu hội thoại vào bảng chat

### 12.3. AI Service
- kiểm tra intent / scope
- dựng prompt
- chọn provider
- stream câu trả lời
- trả `model_version`

## 13. API đề xuất

### Tạo session
```http
POST /api/v1/ai-chat/sessions
```

### Gửi message
```http
POST /api/v1/ai-chat/messages
```

### Stream câu trả lời
```http
POST /api/v1/ai-chat/messages/stream
```

### Lấy lịch sử chat
```http
GET /api/v1/ai-chat/sessions/{id}/messages
```

## 14. Giải thích học thuật ngắn gọn
Chatbot được thiết kế theo mô hình **retrieval-augmented career assistant**, trong đó câu trả lời không được sinh ra một cách tự do hoàn toàn, mà dựa trên dữ liệu thực từ hồ sơ CV, kết quả matching, báo cáo nghề nghiệp và thông tin tuyển dụng trong hệ thống. Hệ thống sử dụng kiến trúc provider-based để hỗ trợ linh hoạt giữa AI local và AI cloud, đồng thời bổ sung cơ chế guardrail nhằm giới hạn chatbot trong đúng phạm vi tư vấn nghề nghiệp. Với cách tiếp cận này, chatbot vừa giữ được tính linh hoạt của mô hình ngôn ngữ lớn, vừa đảm bảo tính đúng ngữ cảnh, tính kiểm soát và khả năng triển khai thực tế.

## 15. Kết luận
Thiết kế chatbot phù hợp nhất cho hệ thống hiện tại là:

- chatbot tư vấn nghề nghiệp có ngữ cảnh
- giới hạn chặt trong domain hệ thống
- có câu phản hồi mẫu cho câu hỏi ngoài phạm vi
- hỗ trợ stream response
- provider-based để dễ chuyển giữa local và cloud

Đây là hướng triển khai cân bằng tốt giữa:
- chất lượng trải nghiệm người dùng
- khả năng kiểm soát nội dung
- chi phí phát triển
- khả năng demo và mở rộng sau này
