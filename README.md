# SmartJob AI - Nền tảng tuyển dụng, phân tích CV và tư vấn nghề nghiệp bằng AI

> _"AI Recruitment Platform for Candidates, Employers and Admin"_

SmartJob AI là hệ thống tuyển dụng đa vai trò được tổ chức theo mô hình tách biệt `FE + BE + AI`. Dự án phục vụ 3 nhóm người dùng chính:

- Ứng viên tìm việc, quản lý hồ sơ và dùng các tính năng AI.
- Nhà tuyển dụng quản lý công ty, bài đăng, ứng viên và phỏng vấn.
- Quản trị viên theo dõi vận hành, phân quyền, AI usage, billing và thống kê hệ thống.

Hệ thống kết hợp nghiệp vụ tuyển dụng truyền thống với các tính năng AI như parse CV, parse JD, matching, sinh thư xin việc, hỗ trợ viết nội dung CV, chatbot tư vấn nghề nghiệp, mock interview và interview copilot.

---

## Tổng quan

SmartJob AI được xây dựng để giải quyết các bài toán phổ biến trong tuyển dụng:

- CV và JD thường không đồng nhất, khó đối chiếu thủ công.
- Ứng viên khó tự đánh giá mức độ phù hợp với công việc.
- Nhà tuyển dụng cần một dashboard thống nhất để quản lý job, ứng viên, lịch phỏng vấn và nội bộ công ty.
- Hệ thống tuyển dụng truyền thống thiếu lớp AI để phân tích, tư vấn và hỗ trợ ra quyết định.

Kiến trúc tách riêng frontend, backend và AI service giúp nhóm phát triển song song, giảm coupling và dễ thay thế từng mô-đun khi mở rộng.

---

## Chức năng chính

- Xác thực tài khoản bằng email, Bearer Token và đăng nhập Google.
- Quản lý hồ sơ ứng viên, kỹ năng cá nhân, CV upload và CV builder.
- Quản lý công ty, tin tuyển dụng, ứng viên và các vòng phỏng vấn.
- Quản lý ví, thanh toán, gói dịch vụ và entitlement theo tính năng.
- Gợi ý việc làm phù hợp từ dữ liệu matching.
- AI CV parsing, JD parsing và job matching với semantic skill scoring nội bộ.
- AI cover letter, career report, CV builder writing assistant và career chatbot có stream response.
- AI mock interview và interview copilot cho phía tuyển dụng.
- Dashboard và màn quản trị cho users, admins, companies, profiles, skills, industries, jobs, applications, AI usage, billing, CV templates, audit logs và stats.

---

## Đối tượng sử dụng

### 1. Ứng viên

- Đăng ký, đăng nhập, quản lý thông tin cá nhân và hồ sơ.
- Tải CV, parse CV và quản lý kỹ năng.
- Xem công việc phù hợp, kết quả matching và career report.
- Tạo thư xin việc, trò chuyện với AI và luyện mock interview.
- Quản lý ví, lịch sử thanh toán và gói dịch vụ.

### 2. Nhà tuyển dụng

- Quản lý thông tin công ty và phân quyền nội bộ.
- Tạo, cập nhật, ẩn hoặc xuất bản tin tuyển dụng.
- Parse JD để chuẩn hóa yêu cầu công việc.
- Theo dõi ứng viên, shortlist, lịch phỏng vấn và offer.
- Dùng interview copilot để hỗ trợ quy trình phỏng vấn.
- Quản lý billing, audit log và thông báo nội bộ.

### 3. Quản trị viên

- Quản lý người dùng, quản trị viên, công ty, hồ sơ, kỹ năng, ngành nghề và tin tuyển dụng.
- Theo dõi AI usage, billing, CV templates và audit logs.
- Xem thống kê tổng hợp về lưu tin, ứng tuyển, matching và tư vấn nghề nghiệp.
- Kiểm soát phân quyền admin và trạng thái tài khoản toàn hệ thống.

---

## Kiến trúc hệ thống

Hệ thống được tổ chức thành 3 khối chính:

| Thành phần | Vai trò                                                                                                  |
| -----------| -------------------------------------------------------------------------------------------------------- |
| `FE/`      | Giao diện người dùng viết bằng `Vue 3`, `Vue Router`, `Vite`, `Tailwind CSS`, `Laravel Echo`             |
| `BE/`      | API nghiệp vụ viết bằng `Laravel 12`, `Sanctum`, `Socialite`, `Reverb`, `Pest`                           |
| `AI/`      | Dịch vụ AI viết bằng `FastAPI`, `Pydantic`, `pdfplumber`, provider-based integration với `Ollama/OpenAI` |

Luồng dữ liệu chính:

1. Người dùng thao tác trên `FE`.
2. `FE` gọi API REST tại `BE` thông qua `VITE_API_BASE_URL`.
3. `BE` xử lý auth, phân quyền, CRUD nghiệp vụ, billing, notification và realtime.
4. Khi cần AI, `BE` gọi sang `AI service`.
5. `AI service` trả về JSON hoặc stream response cho các tác vụ parse, matching, generation, chat và interview.
6. `BE` lưu kết quả vào database và trả response lại cho `FE`.

---

## Công nghệ sử dụng

| Thành phần     | Công nghệ                                                                             |
| ---------------| ------------------------------------------------------------------------------------- |
| Frontend       | Vue 3, Vite, Vue Router, Tailwind CSS 4, vue-toastification, laravel-echo, pusher-js  |
| Backend        | Laravel 12, PHP 8.2, Laravel Sanctum, Laravel Socialite, Laravel Reverb, L5 Swagger   |
| AI Service     | FastAPI, Uvicorn, Pydantic, pdfplumber, python-dotenv, pytest                         |
| Database       | MySQL qua cấu hình Laravel                                                            |
| Authentication | Bearer Token, Google OAuth, role-based middleware                                     |
| Testing        | Pest, PHPUnit, Python regression tests, FE smoke test script                          |

---

## Cấu trúc thư mục

```text
KLTN/
├── AI/          # AI service FastAPI
├── BE/          # Backend Laravel API
├── Documents/   # Tài liệu phân tích, backlog, test plan, UI design
├── FE/          # Frontend Vue 3
└── README.md    # Tổng quan dự án
```

---

## Các module AI hiện có

Các endpoint AI đang được mount trực tiếp trong `AI/app/main.py`:

- `GET /health`
- `POST /parse/cv`
- `POST /parse/jd`
- `POST /match/cv-jd`
- `POST /generate/cover-letter`
- `POST /generate/career-report`
- `POST /generate/cv-builder-writing`
- `POST /chat/career-consultant`
- `POST /chat/career-consultant/stream`
- `POST /interview/mock/question`
- `POST /interview/mock/evaluate`
- `POST /interview/mock/report`
- `POST /interview/copilot/generate`
- `POST /interview/copilot/evaluate`

Lưu ý:

- Matching hiện có thành phần semantic skill scoring trong logic chấm điểm.
- Repo hiện không có module `semantic search` độc lập hoặc endpoint `POST /search/semantic/jobs`.

---

## Các khu vực giao diện chính

- Guest pages: landing, login, register, quên mật khẩu, tìm việc, xem công ty, ngành nghề, kỹ năng.
- Candidate dashboard: profile, CV, CV builder, skills, applications, saved jobs, followed companies, matched jobs, career report, AI center, wallet, plans, payments.
- Employer dashboard: company, jobs, candidates, interviews, HR management, billing, audit logs, profile.
- Admin dashboard: users, admins, companies, profiles, user skills, industries, skills, jobs, applications, matchings, career advising, CV templates, AI usage, billing, audit logs, stats.

---

## Hướng dẫn cài đặt

### Yêu cầu

- `PHP 8.2+`
- `Composer`
- `Node.js 20.19+` hoặc `>= 22.12.0`
- `npm`
- `Python 3.11+`
- `MySQL`
- `Git`
- `Ollama` hoặc `OpenAI API key` nếu muốn chạy đầy đủ các tính năng AI

### 1. Clone repository

```bash
git clone https://github.com/KLTN-03-2026/GR15.git
cd GR15
```

Nếu bạn đang làm việc trong thư mục local khác, hãy thay đường dẫn tương ứng.

### 2. Cài đặt Backend Laravel

```bash
cd BE
composer install
npm install
```

Repo hiện không kèm `BE/.env.example`, vì vậy cần tự tạo `BE/.env` từ cấu hình nội bộ của nhóm hoặc từ môi trường đã có sẵn. Các nhóm biến quan trọng thường bao gồm:

- `APP_*`
- `DB_*`
- `FRONTEND_URL`
- `AI_SERVICE_URL`, `AI_SERVICE_TIMEOUT`
- `GOOGLE_*`
- `MAIL_*`
- `REVERB_*`
- `MOMO_*`
- `VNPAY_*`

Sau khi có `BE/.env`, chạy:

```bash
php artisan key:generate
php artisan migrate
```

Chạy backend local:

```bash
php artisan serve
```

Hoặc chạy chế độ phát triển tổng hợp của Laravel:

```bash
composer run dev
```

Mặc định backend phục vụ tại:

```text
http://127.0.0.1:8000
```

### 3. Cài đặt Frontend Vue

```bash
cd FE
npm install
```

Tạo `FE/.env` nếu chưa có:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
VITE_REVERB_APP_KEY=
VITE_REVERB_HOST=127.0.0.1
VITE_REVERB_PORT=8080
VITE_REVERB_SCHEME=http
```

Trong đó:

- `VITE_API_BASE_URL` là bắt buộc.
- Nhóm `VITE_REVERB_*` là cần thiết nếu muốn bật realtime notifications qua Reverb.

Chạy frontend:

```bash
npm run dev
```

Mặc định frontend chạy tại:

```text
http://127.0.0.1:5173
```

### 4. Cài đặt AI Service

```bash
cd AI
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Repo hiện không kèm `AI/.env.example`, vì vậy cần tự tạo `AI/.env`. Một cấu hình tối thiểu có thể bắt đầu như sau:

```env
AI_SERVICE_NAME=KLTN AI Service
AI_DEBUG=false
LOCAL_LLM_MODEL=qwen2.5:3b
OLLAMA_URL=http://127.0.0.1:11434/api/generate
OLLAMA_MODEL=qwen2.5:3b
OPENAI_API_KEY=
OPENAI_BASE_URL=https://api.openai.com/v1/responses
OPENAI_MODEL=gpt-4.1-mini
CHATBOT_PROVIDER=ollama
COVER_LETTER_PROVIDER=ollama
CAREER_REPORT_PROVIDER=ollama
MOCK_INTERVIEW_PROVIDER=ollama
```

Chạy AI service:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

AI service mặc định chạy tại:

```text
http://127.0.0.1:8001
```

---

## Vị trí mã nguồn quan trọng

### Frontend

- API client: `FE/src/services/api.js`
- Realtime client: `FE/src/services/realtime.js`
- Router: `FE/src/router/index.js`
- Layout và shell UI: `FE/src/layouts/`

### Backend

- API routes: `BE/routes/api.php`
- Controllers: `BE/app/Http/Controllers/Api/`
- Form requests: `BE/app/Http/Requests/`
- Models: `BE/app/Models/`
- AI bridge: `BE/app/Services/Ai/AiClientService.php`

### AI

- App entry: `AI/app/main.py`
- Routers: `AI/app/routers/`
- Schemas: `AI/app/schemas/`
- Services: `AI/app/services/`
- Runtime config: `AI/app/core/config.py`

---

## Kiểm thử

### Backend

```bash
cd BE
php artisan test
```

### Frontend

```bash
cd FE
npm run build
npm run test:smoke
```

### AI

```bash
cd AI
pytest
```

---

## Hướng phát triển tiếp theo

- Cải thiện chất lượng matching và semantic scoring.
- Mở rộng bộ prompt, rubric và báo cáo cho mock interview.
- Tăng độ linh hoạt khi chuyển provider giữa `Ollama` và `OpenAI`.
- Tăng cường test tự động cho `FE`, `BE` và `AI`.
- Hoàn thiện thêm tài liệu riêng cho từng module `FE/`, `BE/`, `AI/`.

---

## Báo lỗi và đóng góp

Nếu bạn phát hiện lỗi, hãy tạo issue kèm theo:

- Mô tả lỗi chi tiết
- Cách tái hiện
- Màn hình lỗi nếu có
- Môi trường chạy

Repository:

- https://github.com/KLTN-03-2026/GR15

Nguyên tắc đóng góp:

- Giữ code style nhất quán với từng module.
- Với backend, ưu tiên viết test bằng `Pest` khi thay đổi nghiệp vụ quan trọng.
- Với AI service, nên bổ sung regression test cho chatbot, career report và interview flows khi thay đổi prompt hoặc provider.

---

## Liên hệ dự án

Dự án hiện được quản lý qua repository:

- https://github.com/KLTN-03-2026/GR15

