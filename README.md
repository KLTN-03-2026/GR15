# SmartJob AI - Nền tảng tuyển dụng, phân tích CV và tư vấn nghề nghiệp bằng AI

> _"AI Recruitment Platform for Candidates, Employers and Admin"_

SmartJob AI là hệ thống tuyển dụng toàn diện được xây dựng theo mô hình tách biệt `FE + BE + AI`, hỗ trợ ứng viên tìm việc, nhà tuyển dụng quản lý quy trình tuyển dụng, và quản trị viên theo dõi vận hành hệ thống. Dự án tập trung vào việc kết hợp nghiệp vụ tuyển dụng truyền thống với các tính năng AI như phân tích CV, phân tích mô tả công việc, job matching, sinh thư xin việc, chatbot tư vấn nghề nghiệp và mock interview.

---

## Giới thiệu & ý tưởng tổng thể

Trong quy trình tuyển dụng hiện đại, cả ứng viên lẫn nhà tuyển dụng đều gặp nhiều vấn đề:

- Ứng viên khó đánh giá mức độ phù hợp giữa hồ sơ và tin tuyển dụng.
- CV và JD thường được xử lý thủ công, tốn thời gian và dễ bỏ sót thông tin.
- Doanh nghiệp cần một dashboard để quản lý bài đăng, ứng viên và lịch phỏng vấn.
- Hệ thống tuyển dụng thông thường thiếu lớp AI hỗ trợ tư vấn, matching và phân tích.

SmartJob AI được xây dựng để giải bài toán đó bằng một nền tảng web có khả năng vận hành theo nhiều vai trò và mở rộng AI service riêng để xử lý các bài toán thông minh.

---

## Mục tiêu dự án

- Số hóa quy trình tuyển dụng cho ứng viên, nhà tuyển dụng và admin.
- Nâng cao chất lượng matching giữa CV và tin tuyển dụng bằng AI.
- Hỗ trợ ứng viên cải thiện hồ sơ, định hướng nghề nghiệp và luyện phỏng vấn.
- Giúp nhà tuyển dụng quản lý công ty, bài đăng, ứng viên và trạng thái tuyển dụng trên cùng một hệ thống.
- Xây dựng kiến trúc để tách lớp giao diện, API nghiệp vụ và AI service để dễ bảo trì và mở rộng.

---

## Thách thức mà dự án hướng tới

- Dữ liệu CV và JD không đồng nhất, khó đối chiếu thủ công.
- Ứng viên cần gợi ý việc làm và định hướng nghề nghiệp cá nhân hóa.
- Nhà tuyển dụng cần theo dõi ứng viên, email phỏng vấn và trạng thái xử lý theo quy trình.
- Hệ thống cần phân quyền rõ ràng cho 3 nhóm vai trò: ứng viên, nhà tuyển dụng, admin.

---

## Giải pháp SmartJob AI

- Frontend `Vue 3 + Vite` cho các giao diện guest, candidate dashboard, employer dashboard và admin dashboard.
- Backend `Laravel 12 + Sanctum + Socialite` xử lý auth, phân quyền, CRUD nghiệp vụ và API REST.
- AI service `FastAPI` phục vụ parse CV, parse JD, semantic search, matching, cover letter, career report, career chatbot và mock interview.
- Luồng dữ liệu tách thành 3 khối `FE`, `BE`, `AI` để dễ phát triển song song và thay thế mô đun.

---

## Đối tượng hướng đến

### 1. Ứng viên

**Mục tiêu:** Tìm việc, quản lý hồ sơ và nhận gợi ý cá nhân hóa.

**Lợi ích:**

- Đăng ký, đăng nhập, quản lý thông tin cá nhân và hồ sơ CV.
- Parse CV bằng AI để trích xuất kỹ năng và thông tin chuyên môn.
- Xem việc phù hợp, matching score và báo cáo định hướng nghề nghiệp.
- Tạo thư xin việc và trò chuyện với AI career consultant.
- Luyện mock interview và xem báo cáo đánh giá.

---

### 2. Nhà tuyển dụng

**Mục tiêu:** Quản lý công ty, bài đăng và quá trình tuyển dụng.

**Lợi ích:**

- Quản lý thông tin công ty và logo doanh nghiệp.
- Tạo, cập nhật, ẩn/hiện tin tuyển dụng.
- Parse JD để chuẩn hóa dữ liệu bài đăng.
- Theo dõi danh sách ứng viên và cập nhật trạng thái ứng tuyển.
- Gửi lại email phỏng vấn và quản lý luồng phỏng vấn.

---

### 3. Quản trị viên

**Mục tiêu:** Điều phối và giám sát toàn bộ hệ thống.

**Lợi ích:**

- Quản lý người dùng, công ty, hồ sơ, kỹ năng, ngành nghề, tin tuyển dụng.
- Xem thống kê ứng tuyển, matching, lưu tin và tư vấn nghề nghiệp.
- Theo dõi dashboard thị trường và tình hình vận hành tổng quan.
- Kiểm soát phân quyền và khóa/mở khóa tài khoản.

---

## Chức năng chính

- Xác thực tài khoản bằng email, Bearer Token và đăng nhập Google.
- Quản lý hồ sơ ứng viên, kỹ năng cá nhân và CV upload.
- Quản lý công ty, tin tuyển dụng và danh sách ứng viên.
- Quản lý ứng tuyển, trạng thái phỏng vấn, xác nhận tham gia và rút đơn.
- Semantic search tin tuyển dụng.
- AI CV parsing, JD parsing, job matching.
- AI career report, cover letter generation, chatbot career consultant.
- AI mock interview theo phiên và báo cáo sau phỏng vấn.
- Admin dashboard và các trang quản trị nghiệp vụ.

---

## Tính năng nổi bật

### AI phân tích hồ sơ và bài đăng

- Parse CV từ file hồ sơ ứng viên.
- Parse JD để trích xuất yêu cầu công việc.
- Match CV và JD để tính mức độ phù hợp.

### AI hỗ trợ ứng viên

- Tạo thư xin việc dựa trên hồ sơ và tin tuyển dụng.
- Sinh career report dựa trên profile và kết quả matching.
- Chatbot tư vấn nghề nghiệp có hỗ trợ stream response.
- Mock interview gồm sinh câu hỏi, đánh giá câu trả lời và tổng hợp báo cáo.

### Hệ thống quản lý đa vai trò

- Guest pages cho đăng ký, đăng nhập, tìm việc, xem công ty, ngành nghề, kỹ năng.
- Candidate dashboard cho profile, CV, skills, applications, matched jobs, AI center.
- Employer dashboard cho công ty, jobs, candidates, interviews.
- Admin dashboard cho users, companies, profiles, skills, industries, jobs, stats.

---

## Kiến trúc hệ thống

Hệ thống được tổ chức thành 3 khối chính:

| Thành phần | Vai trò                                                                      |
---------------------------------------------------------------------------------------------
| `FE/`      | Giao diện người dùng viết bằng `Vue 3`, `Vue Router`, `Vite`, `Tailwind CSS` |
| `BE/`      | API nghiệp vụ viết bằng `Laravel 12`, `Sanctum`, `Socialite`, `Pest`         |
| `AI/`      | Dịch vụ AI viết bằng `FastAPI`, `Pydantic`, `sentence-transformers`, `FAISS` |

---

## Công nghệ sử dụng

| Thành phần     | Công nghệ                                                                |
---------------------------------------------------------------------------------------------
| Frontend       | Vue 3, Vite, Vue Router, Tailwind CSS 4, vue-toastification              |
| Backend        | Laravel 12, PHP 8.2, Laravel Sanctum, Laravel Socialite, L5 Swagger      |
| AI Service     | FastAPI, Uvicorn, Pydantic, pdfplumber, sentence-transformers, faiss-cpu |
| Database       | MySQL / cấu hình qua Laravel                                             |
| Authentication | Bearer Token, Google OAuth, role-based middleware                        |
| Testing        | Pest, PHPUnit, Python regression tests                                   |

---

## Cấu trúc thư mục

```text
KLTN/
├── AI/                    # AI service FastAPI
├── BE/                    # Backend Laravel API
├── FE/                    # Frontend Vue 3
└── README.md              # Tổng quan dự án
```

---

## Luồng dữ liệu chính

1. Người dùng thao tác trên `FE`.
2. `FE` gọi API REST tại `BE` thông qua `VITE_API_BASE_URL`.
3. `BE` xử lý auth, phân quyền, CRUD và các quy trình nghiệp vụ.
4. Khi cần xử lý AI, `BE` gọi sang `AI service`.
5. `AI service` trả về JSON cho parse, matching, generation, chat hoặc interview.
6. `BE` lưu kết quả vào database và trả response lại cho `FE`.

---

## Các module AI hiện có

- `POST /parse/cv`
- `POST /parse/jd`
- `POST /match/cv-jd`
- `POST /generate/cover-letter`
- `POST /generate/career-report`
- `POST /search/semantic/jobs`
- `POST /chat/career-consultant`
- `POST /chat/career-consultant/stream`
- `POST /interview/mock/question`
- `POST /interview/mock/evaluate`
- `POST /interview/mock/report`

---

## Hướng dẫn cài đặt

### Yêu cầu

- `PHP 8.2+`
- `Composer`
- `Node.js 20+`
- `npm`
- `Python 3.11+`
- `MySQL`
- `Git`

---

### 1. Clone repository

```bash
git clone https://github.com/KLTN-03-2026/GR15.git
cd GR15
```

Nếu bạn đang làm việc với thư mục local khác, hãy thay đường dẫn tương ứng.

---

### 2. Cài đặt Backend Laravel

```bash
cd BE
composer install
copy .env.example .env
php artisan key:generate
php artisan migrate
npm install
```

Chạy backend local:

```bash
php artisan serve
```

Hoặc chạy chế độ phát triển tổng hợp của Laravel:

```bash
composer run dev
```

Mặc định backend sẽ phục vụ tại:

```text
http://127.0.0.1:8000
```

---

### 3. Cài đặt Frontend Vue

```bash
cd FE
npm install
```

Tạo file `.env` trong `FE/` nếu cần:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

Chạy frontend:

```bash
npm run dev
```

Mặc định frontend sẽ chạy tại:

```text
http://127.0.0.1:5173
```

---

### 4. Cài đặt AI Service

```bash
cd AI
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

AI service sẽ chạy tại:

```text
http://127.0.0.1:8001
```

---

## Môi trường phát triển đề xuất

### Backend

- Cập nhật file `BE/.env` cho database, mail, Sanctum và biến liên quan AI.
- Kiểm tra route API tại `BE/routes/api.php`.

### Frontend

- API client nằm trong `FE/src/services/api.js`.
- Router nằm trong `FE/src/router/index.js`.

### AI

- App entry nằm trong `AI/app/main.py`.
- Các router AI nằm trong `AI/app/routers/`.
- Các service xử lý nghiệp vụ AI nằm trong `AI/app/services/`.

---

## Hướng phát triển tương lai

- Cải thiện độ chính xác của matching và semantic search.
- Bổ sung dashboard phân tích sâu hơn cho employer và admin.
- Mở rộng bộ câu hỏi và rubric cho mock interview.
- Tích hợp thêm model AI provider linh hoạt hơn cho chat và generation.
- Tăng cường test tự động cho cả `FE`, `BE` và `AI`.

---

## Báo lỗi

Nếu bạn phát hiện lỗi, hãy tạo issue kèm theo:

- Mô tả lỗi chi tiết
- Cách tái hiện
- Màn hình lỗi nếu có
- Môi trường chạy

Repository:

- https://github.com/KLTN-03-2026/GR15

---

## Đóng góp

- Fork repository và tạo branch mới cho tính năng hoặc bugfix.
- Giữ code style nhất quán với từng module.
- Với backend, ưu tiên viết test bằng `Pest` khi thay đổi nghiệp vụ quan trọng.
- Với AI service, có thể bổ sung regression test Python cho chatbot và mock interview.

---


## Liên hệ dự án

Dự án hiện được quản lý qua repository:

- https://github.com/KLTN-03-2026/GR15

---
