# HR Management Module Roadmap

## 1. Mục tiêu module
Module `Quản lý HR nội bộ` dùng để cho phép một công ty có nhiều tài khoản nhà tuyển dụng cùng tham gia vận hành tuyển dụng, thay vì chỉ một owner duy nhất.

Mục tiêu nghiệp vụ:
- một công ty có nhiều HR/recruiter cùng hoạt động
- phân quyền rõ theo vai trò nội bộ
- kiểm soát ai được quản lý công ty, job, ứng tuyển, phỏng vấn
- theo dõi người phụ trách từng công việc tuyển dụng

---

## 2. Hiện trạng codebase

### 2.1. Những gì đã có

#### Dữ liệu và quan hệ
- Bảng pivot `cong_ty_nguoi_dungs`
- Quan hệ nhiều thành viên trong công ty đã có ở:
  - `BE/app/Models/NguoiDung.php`
  - `BE/app/Models/CongTy.php`
- Migration:
  - `BE/database/migrations/2026_04_09_000002_create_cong_ty_nguoi_dungs_table.php`

#### Vai trò nội bộ hiện có
- `owner`
- `member`

#### API backend đã có
Ở `BE/app/Http/Controllers/Api/NhaTuyenDungCongTyController.php`:
- xem danh sách thành viên công ty
- thêm HR vào công ty bằng email
- gỡ HR khỏi công ty

Routes đã có:
- `GET /v1/nha-tuyen-dung/cong-ty/thanh-viens`
- `POST /v1/nha-tuyen-dung/cong-ty/thanh-viens`
- `DELETE /v1/nha-tuyen-dung/cong-ty/thanh-viens/{memberId}`

#### Rule backend đã có
- chỉ `owner` mới được thêm/gỡ HR
- chỉ tài khoản `nhà tuyển dụng` mới được thêm vào công ty
- không thể add chính mình
- không thể add tài khoản đã thuộc công ty khác
- không thể gỡ `owner`

#### Frontend service đã có
Ở `FE/src/services/api.js`:
- `employerCompanyService.getMembers()`
- `employerCompanyService.addMember(email)`
- `employerCompanyService.removeMember(memberId)`

---

### 2.2. Những gì còn thiếu

#### UI quản lý HR chưa hoàn chỉnh
Hiện chưa có module UI hoàn chỉnh để:
- xem danh sách HR nội bộ
- phân biệt `owner` và `member`
- thêm HR bằng email
- gỡ HR khỏi công ty

#### Chưa có phân quyền nội bộ thật sự
Mới chỉ có:
- `owner`
- `member`

Chưa có các vai trò sâu hơn như:
- `admin_hr`
- `recruiter`
- `interviewer`
- `viewer`

#### Chưa áp quyền nội bộ vào employer flow
Các route employer hiện chủ yếu chặn theo:
- `role:nha_tuyen_dung`

Chưa chặn sâu theo:
- có thuộc công ty này không
- có phải owner không
- có quyền quản lý job không
- có quyền xử lý ứng tuyển không

#### Chưa có invitation flow
Hiện tại add HR là thêm trực tiếp bằng email.

Chưa có:
- gửi lời mời
- HR chấp nhận / từ chối
- token mời tham gia công ty

#### Chưa gắn HR vào nghiệp vụ vận hành
Chưa có các trường kiểu:
- người tạo job
- HR phụ trách job
- HR đang xử lý ứng tuyển
- interviewer phụ trách vòng phỏng vấn

#### Chưa có audit trail cho nhiều HR
Khi nhiều HR cùng thao tác, hiện chưa có log rõ:
- ai đổi trạng thái
- ai hẹn lịch
- ai gửi offer
- ai phụ trách job nào

---

## 3. Mục tiêu hoàn thiện

Sau khi hoàn thiện, module nên đạt các khả năng sau:
- công ty có nhiều HR nội bộ
- owner có thể quản lý danh sách HR
- mỗi HR có vai trò nội bộ rõ ràng
- từng chức năng employer được chặn đúng theo quyền nội bộ
- job/application/interview có người phụ trách rõ ràng
- có lịch sử thao tác cơ bản

---

## 4. Lộ trình triển khai đề xuất

## Giai đoạn 1. Hoàn thiện UI quản lý HR

### Mục tiêu
Biến backend/service hiện có thành chức năng dùng được thật trên UI employer.

### Việc cần làm
- thêm block `Thành viên HR` trong `EmployerCompanyPage`
- hiển thị:
  - danh sách HR
  - họ tên
  - email
  - vai trò nội bộ
  - trạng thái owner/member
- thêm form:
  - nhập email để thêm HR
- thêm action:
  - gỡ HR khỏi công ty

### Kết quả mong muốn
- owner thao tác được hoàn toàn trên UI
- member chỉ xem được danh sách nếu cần

### Mức ưu tiên
Rất cao

---

## Giai đoạn 2. Mở rộng vai trò nội bộ

### Mục tiêu
Chuyển từ mô hình `owner/member` sang mô hình đủ dùng cho vận hành tuyển dụng.

### Vai trò đề xuất
- `owner`
- `admin_hr`
- `recruiter`
- `interviewer`
- `viewer`

### Việc cần làm
- mở rộng cột `vai_tro_noi_bo`
- bổ sung validation backend
- cập nhật UI chọn vai trò khi thêm/sửa HR
- hiển thị nhãn role trong danh sách HR

### Kết quả mong muốn
- phân vai rõ ràng
- dễ mở rộng quyền về sau

### Mức ưu tiên
Cao

---

## Giai đoạn 3. Áp phân quyền nội bộ vào employer flow

### Mục tiêu
Không chỉ thêm HR, mà phải chặn đúng quyền thao tác.

### Quyền cần áp
- quản lý công ty
- đăng/sửa/xóa/tạm ngưng job
- xem ứng viên
- xử lý ứng tuyển
- hẹn lịch phỏng vấn
- gửi offer

### Việc cần làm
- thêm middleware/policy:
  - `company.owner`
  - `company.can_manage_jobs`
  - `company.can_manage_applications`
  - `company.can_manage_interviews`
- cập nhật controller employer để dùng rule nội bộ thay vì chỉ dựa vào `role:nha_tuyen_dung`

### Kết quả mong muốn
- đúng nghiệp vụ
- an toàn hơn
- nhiều HR không chồng quyền sai

### Mức ưu tiên
Rất cao

---

## Giai đoạn 4. Gắn người phụ trách vào job và ứng tuyển

### Mục tiêu
Biết rõ ai đang phụ trách cái gì trong công ty.

### Việc cần làm
- thêm trường:
  - `nguoi_phu_trach_id` cho job
  - `nguoi_xu_ly_id` cho application
  - `nguoi_phong_van_id` hoặc `nguoi_dieu_phoi_id` cho interview
- hiển thị trên UI employer:
  - job này do ai phụ trách
  - đơn này đang do ai xử lý

### Kết quả mong muốn
- vận hành rõ ràng
- tránh trùng thao tác
- dễ audit

### Mức ưu tiên
Cao

---

## Giai đoạn 5. Invitation flow

### Mục tiêu
Chuyển từ add trực tiếp bằng email sang quy trình mời tham gia công ty.

### Việc cần làm
- tạo bảng lời mời tham gia công ty
- gửi email mời
- cho HR:
  - chấp nhận
  - từ chối
- chỉ sau khi accept mới trở thành thành viên công ty

### Kết quả mong muốn
- trải nghiệm chuyên nghiệp hơn
- an toàn hơn
- phù hợp sản phẩm thật hơn

### Mức ưu tiên
Trung bình

---

## Giai đoạn 6. Audit log theo HR nội bộ

### Mục tiêu
Theo dõi được ai đã thao tác gì.

### Việc cần log
- tạo/sửa/xóa job
- cập nhật trạng thái ứng tuyển
- hẹn / đổi lịch phỏng vấn
- gửi offer
- thêm/gỡ HR

### Kết quả mong muốn
- dễ truy vết
- dễ quản trị khi nhiều HR cùng làm việc

### Mức ưu tiên
Trung bình

---

## 5. Roadmap triển khai ngắn hạn

### P1. Nên làm trước
1. UI quản lý HR trong `EmployerCompanyPage`
2. hiển thị owner/member
3. thêm/gỡ HR từ UI

### P2. Nên làm ngay sau đó
1. mở rộng role nội bộ
2. áp quyền nội bộ vào employer flow

### P3. Làm để module mạnh hơn
1. người phụ trách job/application/interview
2. invitation flow
3. audit trail

---

## 6. Checklist nghiệm thu

### Dữ liệu
- [ ] Một công ty có thể có nhiều tài khoản employer
- [ ] `owner` và `member` hiển thị đúng
- [ ] Không add được HR đã thuộc công ty khác

### UI
- [ ] Owner xem được danh sách thành viên HR
- [ ] Owner thêm được HR bằng email
- [ ] Owner gỡ được HR khỏi công ty
- [ ] Không thể gỡ owner

### Phân quyền
- [ ] Owner quản lý được thành viên
- [ ] Member không quản lý được thành viên
- [ ] Các route employer được chặn đúng theo quyền nội bộ sau khi triển khai phase 2

### Nghiệp vụ mở rộng
- [ ] Job có người phụ trách
- [ ] Application có người xử lý
- [ ] Có log ai thao tác gì

---

## 7. Kết luận
Hiện tại hệ thống đã có nền tảng backend cho module quản lý HR nội bộ, nhưng mới ở mức dữ liệu + API cơ bản.

Để thành một module hoàn chỉnh, các bước quan trọng nhất là:
1. làm UI quản lý HR
2. bổ sung phân quyền nội bộ thật sự
3. áp quyền nội bộ vào toàn bộ employer flow
4. gắn người phụ trách vào nghiệp vụ tuyển dụng

Nếu chỉ cần nâng hệ thống lên mức dùng được ngay, ưu tiên thực tế nhất là:
- hoàn thiện UI `Thành viên HR`
- giữ `owner/member`
- sau đó mới nâng tiếp role và permissions.
