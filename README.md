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

## Tách mã Backend và Frontend các chức năng

Dưới đây là tóm tắt mã nguồn (Frontend bằng Vue 3, Backend bằng Laravel) cho 6 chức năng chính: **Lấy lại mật khẩu, Thông tin công ty (Nhà tuyển dụng), Dashboard admin, Hồ sơ admin, Quản lý đơn ứng tuyển, Quản lý kỹ năng**.

### 1. Lấy lại mật khẩu (Reset Password)
Chức năng cho phép người dùng đặt lại mật khẩu mới thông qua token được gửi tới email.

*   **Frontend (`ResetPasswordPage.vue`)**
    *   **Luồng hoạt động**: Tự động lấy `email` và `token` từ Query String (URL params) khi người dùng click link trong email. Cung cấp Form 3 trường (Mật khẩu mới, Xác nhận mật khẩu) với chức năng Show/Hide. Sử dụng `authService.resetPassword()`.
    *   **API File**: `authService.resetPassword({ email, token, mat_khau, mat_khau_confirmation })`
    *   **Giao diện**:
        ```vue
        <template>
          <form @submit.prevent="handleSubmit">
            <input type="password" v-model="form.mat_khau" placeholder="Mật khẩu mới" />
            <input type="password" v-model="form.mat_khau_confirmation" placeholder="Xác nhận mật khẩu mới" />
            <button :disabled="loading">Xác nhận đổi mật khẩu</button>
          </form>
        </template>
        ```

*   **Backend (`AuthController.php`)**
    *   **Action**: `datLaiMatKhau(DatLaiMatKhauRequest $request)`
    *   **Route**: `POST /api/v1/dat-lai-mat-khau`
    *   **Logic**:
        *   Broker xử lý reset password thông qua `Password::broker()->reset()`.
        *   Validate email, password mới (`min:8`...).
        *   Xóa toàn bộ token API cũ (Sanctum Tokens) của người dùng để bắt buộc phải đăng nhập lại với mật khẩu mới.
        ```php
        // Xóa toàn bộ phiên đăng nhập
        $nguoiDung->tokens()->delete();
        ```

### 2. Thông tin công ty (Nhà tuyển dụng)
Nhà tuyển dụng quản lý hồ sơ công ty và cấu hình các thành viên nhân sự HR nội bộ với phân quyền.

*   **Frontend (`EmployerCompanyPage.vue`)**
    *   **Luồng hoạt động**: Cho phép lấy toàn bộ chi tiết công ty, update/tạo mới công ty (`employerCompanyService.updateCompany()`). Hỗ trợ Realtime WebSocket follower qua Laravel Echo. Cung cấp Panel quản lý nhân sự HR (Thêm/Sửa role/Xóa member).
    *   **API File**: `employerCompanyService.getCompany()`, `createCompany()`, `updateCompany()`, `addMember()`, `updateMemberRole()`, `removeMember()`
    *   **Giao diện**:
        ```vue
        <script setup>
        // Flow Tải Company: Promise.all([fetchIndustries(), fetchCompany(), fetchStats()])
        // Realtime Connect: subscribeFollowerChannel(companyId) -> lắng nghe '.company.followers.updated'
        </script>
        ```

*   **Backend (`NhaTuyenDungCongTyController.php`)**
    *   **Routes**: `GET/POST/PUT /api/v1/nha-tuyen-dung/cong-ty`, `GET/POST/PUT/DELETE /api/v1/nha-tuyen-dung/cong-ty/thanh-viens`
    *   **Logic**:
        *   Cập nhật Logo file upload bằng Laravel Storage `request->file('logo')->store('cong_ty_logos')`.
        *   Check quan hệ `la_chu_so_huu`: Xác định chủ công ty được quyền quản lý Role theo `vai_tro_noi_bo` trên bảng pivot `nguoi_dung_cong_ty`.
        *   Ràng buộc: Mỗi Nhà tuyển dụng chỉ được sở hữu 1 công ty.
        ```php
        // Logic Cập nhật Role HR
        $congTy->thanhViens()->updateExistingPivot($memberId, [
              'vai_tro_noi_bo' => $data['vai_tro_noi_bo'],
        ]);
        ```

### 3. Dashboard Admin
Khu vực thống kê overview thị trường tổng quan và sức khoẻ của hệ thống tuyển dụng dành cho Quản trị viên.

*   **Frontend (`AdminDashboardPage.vue`)**
    *   **Luồng hoạt động**: Gọi song song 3 API để lấy thống kê chi tiết của Người dùng, Công ty, và Thị trường. Tính toán xu hướng chart theo phần trăm. Render giao diện với số liệu Real-time.
    *   **API File**: `adminMarketService.getDashboard()`, `userService.getUserStats()`, `companyService.getCompanyStats()`
    *   **Giao diện**: Render nhiều Cards (`overview`, `top_categories`, `monthly_job_trend`). Hiển thị Insight động từ thị trường (`hints`).

*   **Backend (`AdminMarketDashboardController.php`)**
    *   **Route**: `GET /api/v1/admin/dashboard/market`
    *   **Logic**: Tổng hợp phân tích Data Market live job (Job đang active).
        *   Thống kê tỷ lệ các công ty có Job theo level, form work (Remote, Offline).
        *   Phân tích Top list kỹ năng yêu cầu (group by `tin_tuyen_dung_ky_nangs` bảng pivot).
        *   Lấy Market Trend (Job Creation Flow theo 6 tháng).
        ```php
        public function overview(): JsonResponse {
            return response()->json([
                'overview' => $this->buildOverview(),
                'top_categories' => $this->buildTopCategories(...),
                'monthly_job_trend' => $this->buildMonthlyJobTrend(),
                // Tính toán Insight báo cáo tự động...
            ]);
        }
        ```

### 4. Hồ sơ Admin
Trang cá nhân cho phép Quản trị viên chỉnh sửa thông tin tài khoản và đổi Avatar.

*   **Frontend (`AdminProfilePage.vue`)**
    *   **Luồng hoạt động**: Tải adminProfile info từ `authService.getProfile()`. Cho phép Preview ảnh Avatar ngay khi chọn thông qua `URL.createObjectURL()`. Tự động gọi API upload Avatar lập tức sau khi file được handle (`uploadAvatarImmediately()`).
    *   **Giao diện**: Form profile hỗ trợ đồng bộ (`syncStoredAdmin()`) thông tin user vào localStorage để cập nhật toàn cục trạng thái đăng nhập hệ thống bằng Dispatch Event `admin-profile-updated`.

*   **Backend (`AuthController.php` / `UserProfileController.php`)**
    *   **Action**: Lấy qua `me(Request $request)`, update bằng `capNhatHoSo(CapNhatHoSoRequest $request)`.
    *   **Logic**:
        *   Admin là `User` có role đặc biệt. Profile API có thể xử lý việc tải hình ảnh file lên AWS S3 / Local System disk (lưu tại storage `public/avatars`).
        *   Phản hồi `avatar_url` có chứa full Public URL ảnh.

### 5. Quản lý đơn ứng tuyển (Toàn hệ thống)
Theo dõi toàn bộ các luồng luân chuyển hồ sơ xin việc trên hệ thống, kèm theo các trạng thái phỏng vấn/từ chối.

*   **Frontend (`ApplicationManagementPage.vue`)**
    *   **Luồng hoạt động**: Sử dụng AdminPaginationBar để xem danh sách `applications`. Hỗ trợ bộ lọc Status linh hoạt (Waiting, Checked, Interview, Accept/Deny). Form Detail xem thông tin Thư xin việc (Cover Letter) kèm trạng thái hẹn Interview lịch.
    *   **API File**: `adminApplicationService.getApplications()`, `adminApplicationService.getStats()`
    *   **Giao diện**:
        ```javascript
        // Lọc Filter động:
        const loadApplications = async () => {
            adminApplicationService.getApplications({ page: 1, trang_thai: selectedStatus, cong_ty_id: selectedCompany })
        }
        ```

*   **Backend (`AdminUngTuyenController.php`)**
    *   **Routes**: `GET /api/v1/admin/ung-tuyens`, `GET /api/v1/admin/ung-tuyens/thong-ke`
    *   **Logic**: Sử dụng Eager Loading (`with`) tối ưu N+1 Query. Load `TinTuyenDung`, Load `HoSo`, Load Email của User thuộc về hồ sơ.
        ```php
        $query = UngTuyen::with([
            'tinTuyenDung:id,cong_ty_id,tieu_de,trang_thai',
            'tinTuyenDung.congTy:id,ten_cong_ty',
            'hoSo' => function ($q) {
                $q->withTrashed()->with('nguoiDung:id,email'); // Chỉ load email ứng viên liên đới
            }
        ]);
        ```

### 6. Quản lý Kỹ năng (Skils Collection)
Bộ kỹ năng từ khóa phục vụ cho AI matching sau này như hệ thống Catalog.

*   **Frontend (`SkillManagementPage.vue`)**
    *   **Luồng hoạt động**: Bảng danh sách Kỹ Năng Admin sử dụng Debounce Search chống spam request ($250 \text{ms}$). Popup Modal thêm/Sửa kỹ năng cùng confirm delete Kĩ năng. Quản lý Thống kê (`có Icon`, `có mô tả`).
    *   **Giao diện**: Render Data Table truyền thống, kết hợp cùng Form Modal cho CRUD thao tác nhanh ngay trên màn hình. Mọi thay đổi đều Refresh API danh sách kèm Update Stats lập tức.

*   **Backend (`AdminKyNangController.php`)**
    *   **Routes**: RESTful Resource (index, store, show, update, destroy, thongKe). `GET/POST/PUT/DELETE /api/v1/admin/ky-nangs`
    *   **Logic**:
        *   Khởi tạo Data từ request validation: `TaoKyNangRequest`, `CapNhatKyNangRequest`.
        *   Hỗ trợ sắp xếp Sort Động (`sort_by`, `sort_dir`) kết hợp Filter Search (`LIKE`) cho tên kỹ năng.
        ```php
        // Logic Filter Search mạnh:
        $query->where(function ($q) use ($search) {
            $q->where('ten_ky_nang', 'like', "%{$search}%")
              ->orWhere('mo_ta', 'like', "%{$search}%");
        });
        ```

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
