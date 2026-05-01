# Mock Interview v3

## 1. Mock Interview v3 là gì

`Mock Interview v3` là phiên bản nâng cấp từ `v2.0` theo hướng:

- vẫn giữ lõi chấm điểm ổn định theo rule-based
- nhưng bắt đầu dùng `AI local Ollama` để sinh câu hỏi và diễn giải báo cáo tự nhiên hơn
- có fallback về `rule_based` nếu model local không phản hồi

## 2. Điểm khác biệt chính của v3

### v2.0

- adaptive question selection
- rubric chi tiết
- follow-up question cơ bản
- báo cáo cuối chi tiết hơn

### v3.0

- `Ollama` viết lại câu hỏi phỏng vấn theo ngôn ngữ tự nhiên hơn
- `Ollama` viết lại phần coaching/report cuối dễ đọc hơn
- câu hỏi vẫn bám đúng logic phỏng vấn do engine nội bộ quyết định
- không để model tự do hoàn toàn quyết định rubric hay logic chấm điểm

## 3. V3 đã dùng Ollama để sinh câu hỏi hay chưa

### Trước v3

Chưa.

Ở `v2.0`, hệ thống sinh câu hỏi bằng:

- question plan nội bộ
- adaptive selection nội bộ
- follow-up generator nội bộ

Tức là câu hỏi được sinh theo logic rule-based, chưa gọi `Ollama` để diễn đạt lại.

### Từ v3

Có.

Ở `v3.0`, sau khi engine nội bộ quyết định:

- hỏi gì
- hỏi theo hướng nào
- follow-up ra sao

hệ thống sẽ gọi `Ollama` để:

- viết lại câu hỏi cho tự nhiên hơn
- giữ đúng ý kỹ thuật/nghiệp vụ
- làm câu hỏi giống cách hỏi thực tế hơn

Nếu `Ollama` lỗi hoặc không phản hồi:

- hệ thống tự động fallback về câu hỏi rule-based

## 4. Kiến trúc v3

### Tầng 1: Rule-based engine

Chịu trách nhiệm:

- chọn loại câu hỏi
- chọn câu tiếp theo
- quyết định follow-up
- chấm rubric
- xác định điểm yếu chính
- tổng hợp dữ liệu báo cáo

### Tầng 2: Ollama generation layer

Chịu trách nhiệm:

- viết lại câu hỏi cho tự nhiên hơn
- viết lại phần coaching của báo cáo cuối

### Tầng 3: Fallback

Nếu `Ollama` không dùng được:

- quay về câu hỏi và report do rule-based engine tạo

## 5. V3 hiện làm được gì

- sinh câu hỏi đầu phiên bằng `Ollama` nếu provider bật
- sinh câu follow-up bằng `Ollama` nếu provider bật
- viết lại coaching report cuối bằng `Ollama`
- lưu `generation_provider` để biết câu hỏi được sinh từ đâu
- vẫn giữ:
  - số câu hỏi theo từng phiên
  - thanh tiến độ
  - hidden feedback mỗi lượt
  - report tổng kết chi tiết

## 6. Công nghệ đang dùng ở v3

- FE: Vue
- BE: Laravel
- AI service: FastAPI
- DB: MySQL
- AI local: `Ollama`
- model local hiện tại:
  - `qwen2.5:3b`

## 7. Provider mock interview ở v3

Biến môi trường:

- `MOCK_INTERVIEW_PROVIDER=ollama`

Giá trị hỗ trợ hiện tại:

- `ollama`
- `rule_based`

## 8. Lợi ích của cách làm này

- câu hỏi nghe tự nhiên hơn
- báo cáo cuối đỡ khô và máy móc hơn
- vẫn kiểm soát được chất lượng chấm điểm
- ít rủi ro hơn so với để model tự quyết định toàn bộ luồng phỏng vấn

## 9. Hướng mở tiếp sau v3.0

- thêm `OpenAI` provider cho mock interview
- stream phản hồi coaching theo thời gian thực
- rubric theo từng role:
  - backend
  - frontend
  - mobile
  - data
- dashboard tiến bộ theo nhiều phiên
