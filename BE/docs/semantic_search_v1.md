# Semantic Search v3

## Mục tiêu
Semantic Search giúp người dùng tìm kiếm tin tuyển dụng theo **ý nghĩa ngữ cảnh**, không chỉ theo từ khóa trùng khớp tuyệt đối. Ví dụ, truy vấn `việc backend PHP dùng API` vẫn có thể tìm ra JD chứa `Laravel`, `REST API`, `MySQL` dù không ghi đúng từng từ của câu query.

Trong bản `v3`, hệ thống dùng **hybrid reranking** kết hợp với **cơ chế loại bỏ kết quả yếu / sai domain** để giảm các kết quả lạc ngành. Sau khi lấy top ứng viên từ FAISS, hệ thống chấm lại theo nhiều tín hiệu như keyword, skill, category và title match; sau đó chỉ giữ lại các kết quả vượt qua ngưỡng liên quan tối thiểu.

## Kiến trúc tổng thể

### Thành phần tham gia
- `FE`: gửi câu truy vấn semantic search.
- `BE (Laravel)`: lấy dữ liệu JD đang hoạt động, chuẩn hóa thành semantic documents, gọi AI service, lưu metadata embedding vào MySQL.
- `AI (FastAPI)`: tạo embedding cho query và documents, tính độ tương đồng, trả top kết quả.
- `MySQL`: lưu dữ liệu nghiệp vụ và bảng `vector_embeddings` làm metadata store.

### Công nghệ sử dụng
- `sentence-transformers`: tạo embedding ngữ nghĩa cho query/JD.
- `FAISS`: index và truy vấn vector nhanh trên local.
- `MySQL`: lưu metadata embedding trong bảng `vector_embeddings`.
- `Fallback hashed vector`: dùng khi máy chưa cài `sentence-transformers`/`faiss`, giúp test được ngay.

## Luồng hoạt động

### 1. FE gửi truy vấn
FE gọi:

```http
GET /api/v1/tin-tuyen-dungs/semantic-search?q=backend%20php%20api&top_k=10
```

### 2. BE lấy danh sách JD đang hoạt động
BE truy vấn `tin_tuyen_dungs` kèm:
- `congTy`
- `nganhNghes`
- `parsing`
- `kyNangYeuCaus`

### 3. BE chuẩn hóa semantic document cho từng JD
Mỗi JD được ghép thành một `text_content` tổng hợp từ:
- tiêu đề
- mô tả công việc
- địa điểm
- hình thức làm việc
- cấp bậc
- kinh nghiệm yêu cầu
- trình độ yêu cầu
- tên công ty
- ngành nghề
- kỹ năng chuẩn hóa
- skills/requirements parse từ JD

Ví dụ:

```text
Backend Developer Laravel. Xây dựng API và tối ưu hệ thống backend. Đà Nẵng.
Laravel. MySQL. REST API. Docker. Kinh nghiệm 2 năm. Công ty AI Test.
```

### 4. BE gửi dữ liệu sang AI service
Payload gửi sang AI:

```json
{
  "query": "backend php api",
  "top_k": 10,
  "documents": [
    {
      "entity_id": 1,
      "title": "Backend Developer Laravel",
      "text_content": "...",
      "company_name": "Công ty AI Test",
      "location": "Đà Nẵng",
      "level": "Junior",
      "metadata": {
        "nganh_nghes": ["Công nghệ thông tin"],
        "skills": ["Laravel", "MySQL", "REST API"]
      }
    }
  ]
}
```

### 5. AI tạo embedding và xếp hạng hai tầng
AI ưu tiên:
- `sentence-transformers` để tạo embedding semantic
- `FAISS` để search top-k nhanh

Nếu môi trường chưa cài 2 thư viện trên, hệ thống tự fallback sang:
- `hashed vector embedding` kích thước cố định
- cosine similarity thuần Python

Nhờ vậy, API vẫn test được ngay cả khi chưa tải model embedding.

### 6. Hybrid reranking
Sau khi có tập ứng viên semantic ban đầu, hệ thống tính lại điểm theo công thức:

```text
final_score
= semantic_score * 0.45
+ keyword_score * 0.20
+ skill_score * 0.20
+ category_score * 0.10
+ title_score * 0.05
```

Trong đó:
- `semantic_score`: độ gần nghĩa từ embedding
- `keyword_score`: mức trùng các từ khóa quan trọng của query
- `skill_score`: mức khớp kỹ năng từ query với `metadata.skills`
- `category_score`: mức khớp nhóm nghề
- `title_score`: mức khớp tiêu đề vị trí

### 7. Relevance gate và domain constraint
Sau khi có `final_score`, hệ thống tiếp tục áp dụng lớp lọc cuối cùng:

- loại kết quả nếu `final_score` quá thấp
- loại kết quả nếu `skill_score = 0` và `category_score = 0` trong khi mức liên quan tổng thể thấp
- giảm ảnh hưởng của các token quá chung như `developer`, `engineer`, `specialist`
- áp ràng buộc domain cho các truy vấn có tín hiệu nghề rõ ràng

Ví dụ:
- query `iOS Developer`
- nhưng hệ thống chỉ có JD backend

thì dù title có chữ `Developer`, job backend vẫn bị loại vì:
- không khớp category `mobile_development`
- không khớp skill iOS
- không vượt relevance gate

Kết quả khi đó là:
- `results = []`
- `no_relevant_results = true`
- `message = "Hiện chưa tìm thấy tin tuyển dụng đủ phù hợp với truy vấn này."`

### 8. AI trả kết quả semantic ranking
AI trả về:
- `semantic_score`
- `keyword_score`
- `skill_score`
- `category_score`
- `title_score`
- `final_score`
- `semantic_reason`
- `matched_keywords`
- `document_embeddings`
- `no_relevant_results`
- `message`

Trong đó `document_embeddings` chứa vector của từng JD để BE lưu xuống MySQL.

### 9. BE lưu metadata embedding vào MySQL
BE upsert vào bảng `vector_embeddings`:
- `entity_type = tin_tuyen_dung`
- `entity_id`
- `chunk_index = 0`
- `text_content`
- `embedding_vector`
- `model_name`
- `embedding_hash`
- `metadata_json`

Điều này giúp hệ thống:
- theo dõi document nào đã được vector hóa
- biết đang dùng model nào
- lưu thêm metadata phục vụ semantic reranking và debug
- sẵn sàng tái sử dụng cho các tính năng sau như chatbot/RAG

### 10. BE trả kết quả cho FE
Kết quả cuối cùng trả về:
- `query`
- `model_version`
- `search_engine`
- `no_relevant_results`
- `message`
- `results`

Mỗi result gồm:
- thông tin job
- `semantic_score`
- `keyword_score`
- `skill_score`
- `category_score`
- `title_score`
- `final_score`
- `semantic_reason`
- `matched_keywords`

## Cách hoạt động với MySQL hiện tại
Hệ thống **không dùng MySQL để tính similarity vector trực tiếp**. Thay vào đó:

- MySQL giữ vai trò **nguồn dữ liệu nghiệp vụ chính**
- MySQL lưu thêm **metadata embedding**
- AI service thực hiện phần embedding + ranking

Đây là cách phù hợp với kiến trúc hiện tại vì:
- không cần đổi DB sang PostgreSQL/pgvector
- ít phá kiến trúc đang có
- vẫn tận dụng được bảng `vector_embeddings` đã tạo trước đó

## Vì sao chọn hướng này

### Ưu điểm
- tận dụng MySQL hiện tại
- dễ triển khai trên local
- mở đường cho chatbot/RAG sau này
- semantic search tốt hơn search từ khóa
- hybrid reranking giúp giảm job lạc ngành
- có thể trả về rỗng một cách hợp lý nếu hệ thống không có JD phù hợp
- có fallback nên test được ngay

### Hạn chế của v3
- chưa có background indexing riêng
- mỗi lần search vẫn build corpus từ JD đang hoạt động
- FAISS index hiện ở mức in-memory trong request
- ngưỡng lọc và trọng số hiện vẫn là rule-based, cần tinh chỉnh thêm khi dữ liệu tăng

## Hướng nâng cấp sau này
- tạo job nền để re-index vector khi JD thay đổi
- cache FAISS index theo model
- mở semantic search cho cả CV và JD
- dùng lại vector cho chatbot tư vấn nghề nghiệp

## Endpoint triển khai

### FE/BE public endpoint
```http
GET /api/v1/tin-tuyen-dungs/semantic-search?q=...&top_k=10
```

### AI internal endpoint
```http
POST /search/semantic/jobs
```

## Gợi ý test nhanh
1. Parse JD trước để có kỹ năng và requirements chuẩn hóa.
2. Gọi semantic search với query như:
   - `backend php api`
   - `ios swift firebase`
   - `digital marketing ads content`
3. So sánh kết quả với search từ khóa thường để thấy sự khác biệt.

## Test bằng Postman

### Endpoint cần gọi
```http
GET /api/v1/tin-tuyen-dungs/semantic-search?q=backend%20php%20api&top_k=10
```

### Cách tạo request trong Postman
- Method: `GET`
- URL:

```text
{{be_url}}/v1/tin-tuyen-dungs/semantic-search?q=backend%20php%20api&top_k=10
```

### Thứ tự test khuyến nghị
1. Parse JD trước bằng request `Recruiter - Parse JD via BE`.
2. Gọi semantic search với một query gần nghĩa theo nhu cầu.
3. Kiểm tra response:
   - `model_version`
   - `search_engine`
   - `results[*].semantic_score`
   - `results[*].semantic_reason`
   - `results[*].matched_keywords`
4. Kiểm tra bảng `vector_embeddings` để xác nhận metadata embedding đã được lưu.

### Một số query nên thử
- `backend php api`
- `ios swift firebase`
- `marketing content ads`
- `ke toan thue bao cao tai chinh`

### Kỳ vọng
- các JD đúng ngữ cảnh sẽ lên trên dù không trùng hoàn toàn từng từ khóa
- với query mà hệ thống không có JD phù hợp, API sẽ trả danh sách rỗng thay vì ép trả kết quả gần đúng
- `search_engine` sẽ là:
  - `sentence_transformers_faiss_hybrid_rerank_v3` nếu đã cài đủ dependency semantic
  - `hashed_vector_hybrid_rerank_v3` nếu hệ thống đang chạy fallback
- `model_version` sẽ có dạng:
  - `semantic_search_v3::sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
  - hoặc `semantic_search_v3::hashed_fallback`
