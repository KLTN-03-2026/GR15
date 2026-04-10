# Checklist FE Hoàn Thiện Hệ Thống SmartJob AI

## 1. Cách đọc bảng

- `Có UI`: Đã có màn hình Vue trong FE.
- `Có API BE`: Backend đã có route/nghiệp vụ tương ứng.
- `Đã nối FE-BE`: FE đã gọi API thật và dùng dữ liệu thật ở mức cơ bản.
- `Ưu tiên`: `Rất cao`, `Cao`, `Trung bình`, `Thấp`.
- `Việc cần làm tiếp`: Phần còn thiếu để hoàn thiện.

---

## 2. Tổng quan hiện trạng

### 2.1. Nhận định nhanh

| Nhóm | Trạng thái hiện tại | Ghi chú |
| --- | --- | --- |
| Auth | Tương đối ổn | Đã có login/register ứng viên và doanh nghiệp, đã sửa route auth để khớp BE |
| Candidate core | Có UI, chưa nối đủ | Hồ sơ, CV, ứng tuyển, lưu tin, việc phù hợp vẫn cần nối API thật |
| Employer core | Có UI, chưa nối đủ | Dashboard và các màn quản lý employer còn thiếu service/API wrapper |
| Admin core | Có UI một phần | Users/companies có service; nhiều màn admin khác còn chưa nối |
| Candidate AI | Chưa có UI trong FE này | BE/AI đã có chatbot, mock interview, AI progress, career report, semantic search, cover letter |
| Service layer FE | Thiếu khá nhiều | Mới có `authService`, `userService`, `companyService` |

### 2.2. Kết luận ngắn

Frontend hiện tại đã có nền giao diện khá nhiều, nhưng phần mạnh nhất của hệ thống là AI và các nghiệp vụ nối API thật vẫn chưa được phản ánh đầy đủ ở FE này. Việc cần làm tiếp là đi theo cụm chức năng, không vá lẻ từng màn.

---

## 3. Bảng trạng thái chức năng theo module

## 3.1. Guest

| Chức năng | Có UI | Có API BE | Đã nối FE-BE | Ưu tiên | Việc cần làm tiếp |
| --- | --- | --- | --- | --- | --- |
| Trang chủ | Có | Không bắt buộc | Chưa cần | Thấp | Polish nội dung, CTA, điều hướng |
| Đăng nhập ứng viên | Có | Có | Có cơ bản | Rất cao | Kiểm tra redirect theo vai trò, thêm validate/toast đầy đủ |
| Đăng ký ứng viên | Có | Có | Có cơ bản | Rất cao | Đồng bộ validate và thông báo lỗi BE |
| Đăng nhập doanh nghiệp | Có | Có | Có cơ bản | Rất cao | Kiểm tra redirect employer dashboard |
| Đăng ký doanh nghiệp | Có | Có | Có cơ bản | Rất cao | Đồng bộ field với BE, hoàn thiện thông báo |
| Tìm kiếm việc làm | Có | Có | Chưa | Rất cao | Tạo `jobService`, gọi danh sách job thật, filter thật |
| Chi tiết việc làm | Có | Có | Chưa | Rất cao | Gọi API chi tiết job, hiển thị dữ liệu công ty/JD thật |
| Landing AI Career | Có | Có một phần | Chưa | Trung bình | Nếu dùng làm marketing page thì nối CTA tới AI Center/Career Report |

## 3.2. Candidate core

| Chức năng | Có UI | Có API BE | Đã nối FE-BE | Ưu tiên | Việc cần làm tiếp |
| --- | --- | --- | --- | --- | --- |
| Dashboard ứng viên | Có | Có một phần | Chưa | Cao | Nối dữ liệu tóm tắt thật: hồ sơ, ứng tuyển, việc lưu |
| Hồ sơ của tôi | Có | Có | Chưa | Rất cao | Tạo `profileService`, load/sửa hồ sơ thật |
| CV của tôi | Có | Có | Chưa | Rất cao | Upload CV, xem danh sách CV, parse CV |
| Việc đã ứng tuyển | Có | Có | Chưa | Rất cao | Gọi danh sách ứng tuyển thật |
| Việc đã lưu | Có | Có | Chưa | Rất cao | Gọi danh sách lưu tin thật |
| Việc phù hợp | Có | Có | Chưa | Rất cao | Nối matching hoặc semantic recommendation thật |

## 3.3. Candidate AI

| Chức năng | Có UI | Có API BE | Đã nối FE-BE | Ưu tiên | Việc cần làm tiếp |
| --- | --- | --- | --- | --- | --- |
| AI Center | Chưa | Có | Chưa | Rất cao | Tạo page trung tâm AI |
| Chatbot tư vấn nghề nghiệp | Chưa | Có | Chưa | Rất cao | Nối `ai-chat` + stream SSE |
| Mock Interview | Chưa | Có | Chưa | Rất cao | Nối phiên phỏng vấn, stream câu hỏi, report |
| AI Progress | Chưa | Có | Chưa | Cao | Tạo page tiến bộ mock interview |
| Career Report | Chưa | Có | Chưa | Cao | Tạo màn xem báo cáo nghề nghiệp |
| Semantic Search | Chưa | Có | Chưa | Cao | Tạo màn tìm việc bằng AI/semantic |
| Cover Letter | Chưa | Có | Chưa | Trung bình | Tạo màn sinh thư xin việc |

## 3.4. Employer

| Chức năng | Có UI | Có API BE | Đã nối FE-BE | Ưu tiên | Việc cần làm tiếp |
| --- | --- | --- | --- | --- | --- |
| Dashboard nhà tuyển dụng | Có | Có một phần | Chưa | Cao | Nối số liệu thật |
| Việc làm của tôi | Có | Có | Chưa | Rất cao | CRUD job employer, parse JD, đổi trạng thái |
| Ứng viên | Có | Có | Chưa | Rất cao | Xem danh sách ứng viên, trạng thái ứng tuyển |
| Phỏng vấn | Có | Có một phần | Chưa | Cao | Nối lịch phỏng vấn, cập nhật kết quả |
| Công ty | Có | Có | Chưa một phần | Cao | Nối cập nhật profile công ty thật |

## 3.5. Admin

| Chức năng | Có UI | Có API BE | Đã nối FE-BE | Ưu tiên | Việc cần làm tiếp |
| --- | --- | --- | --- | --- | --- |
| Dashboard admin | Có | Có một phần | Chưa | Cao | Nối số liệu thật |
| Quản lý người dùng | Có | Có | Có cơ bản | Rất cao | Hoàn thiện filter, phân trang, hành động |
| Quản lý công ty | Có | Có | Có cơ bản | Rất cao | Hoàn thiện duyệt/khóa/tìm kiếm |
| Quản lý ngành nghề | Có | Có | Chưa | Cao | Tạo `industryService`, nối CRUD thật |
| Quản lý kỹ năng | Có | Có | Chưa | Cao | Tạo `skillService`, nối CRUD thật |
| Quản lý tin tuyển dụng | Có | Có | Chưa | Cao | Tạo `adminJobService`, nối bảng thật |
| Thống kê admin | Có | Có một phần | Chưa | Trung bình | Làm rõ nguồn dữ liệu và API |
| Market Dashboard | Chưa trong FE này | Có | Chưa | Trung bình | Merge màn dashboard thị trường thật vào FE này nếu cần |

---

## 4. Bảng trạng thái service layer FE

| Service | Đã có | Mức hoàn thiện | Ưu tiên | Ghi chú |
| --- | --- | --- | --- | --- |
| `authService` | Có | Tương đối ổn | Rất cao | Đã sửa khớp BE auth |
| `userService` | Có | Cơ bản | Cao | Dùng cho admin user management |
| `companyService` | Có | Cơ bản | Cao | Dùng cho admin company management |
| `jobService` | Chưa | Chưa có | Rất cao | Cần cho guest + candidate + employer |
| `profileService` | Chưa | Chưa có | Rất cao | Cần cho candidate profile |
| `cvService` | Chưa | Chưa có | Rất cao | Cần upload/parse CV |
| `applicationService` | Chưa | Chưa có | Rất cao | Cần cho ứng tuyển và employer candidates |
| `savedJobService` | Chưa | Chưa có | Cao | Cần cho lưu tin |
| `matchingService` | Chưa | Chưa có | Cao | Cần cho matched jobs |
| `careerReportService` | Chưa | Chưa có | Cao | Cần cho AI candidate |
| `semanticSearchService` | Chưa | Chưa có | Cao | Cần cho AI search |
| `chatbotService` | Chưa | Chưa có | Rất cao | Cần cho AI Center |
| `mockInterviewService` | Chưa | Chưa có | Rất cao | Cần cho Mock Interview |
| `aiProgressService` | Chưa | Chưa có | Cao | Cần cho AI progress |
| `marketDashboardService` | Chưa | Chưa có | Trung bình | Cần cho admin market dashboard |
| `industryService` | Chưa | Chưa có | Cao | Cần cho admin ngành nghề |
| `skillService` | Chưa | Chưa có | Cao | Cần cho admin kỹ năng |

---

## 5. Chức năng BE đã có nhưng FE chưa có giao diện

| Chức năng backend/AI | Có UI FE | Ưu tiên | Ghi chú |
| --- | --- | --- | --- |
| Chatbot AI | Chưa | Rất cao | Một trong các giá trị mạnh nhất của hệ thống |
| Mock Interview | Chưa | Rất cao | Đã có AI + BE khá đầy đủ |
| AI Progress | Chưa | Cao | Nên đi cùng Mock Interview |
| Career Report | Chưa | Cao | Nối từ hồ sơ ứng viên |
| Semantic Search | Chưa | Cao | Có thể gắn vào tìm việc |
| Cover Letter | Chưa | Trung bình | Có thể làm sau chatbot/mock interview |
| CV Parse Trigger | Chưa | Rất cao | Nên nằm trong `MyCvPage` |
| Matching Trigger | Chưa | Cao | Nên nằm trong `MyCvPage` hoặc `MatchedJobsPage` |
| Admin Market Dashboard | Chưa trong FE này | Trung bình | Có BE route thật |
| Admin quản lý hồ sơ ứng viên | Chưa | Trung bình | Tùy phạm vi muốn làm |
| Admin thống kê matching/career/applications/saved | Chưa | Trung bình | Phù hợp nếu muốn làm admin analytics sâu hơn |

---

## 6. Thứ tự triển khai đề xuất

| Giai đoạn | Cụm chức năng | Mục tiêu |
| --- | --- | --- |
| 1 | Auth + Guest jobs | Đảm bảo luồng vào hệ thống và xem job chạy thật |
| 2 | Candidate core | Hồ sơ, CV, ứng tuyển, lưu tin, việc phù hợp |
| 3 | Candidate AI | AI Center, chatbot, mock interview, AI progress |
| 4 | Employer core | Jobs, candidates, interviews, company |
| 5 | Admin core | Ngành nghề, kỹ năng, tin tuyển dụng, dashboard |
| 6 | Polish | loading, empty state, notify, auth guard, reusable components |

---

## 7. Checklist thao tác nhanh

### 7.1. Việc nên làm ngay

| STT | Việc | Trạng thái |
| --- | --- | --- |
| 1 | Hoàn thiện `jobService` và nối `JobSearchPage` | [ ] |
| 2 | Hoàn thiện `JobDetailPage` bằng API thật | [ ] |
| 3 | Tạo `profileService` và nối `ProfilePage` | [ ] |
| 4 | Tạo `cvService` và nối `MyCvPage` | [ ] |
| 5 | Tạo `applicationService` và nối `ApplicationsPage` | [ ] |
| 6 | Tạo `savedJobService` và nối `SavedJobsPage` | [ ] |
| 7 | Tạo `matchingService` và nối `MatchedJobsPage` | [ ] |
| 8 | Tạo cụm `AI Center` | [ ] |
| 9 | Tạo `chatbotService` | [ ] |
| 10 | Tạo `mockInterviewService` | [ ] |

### 7.2. Việc nên làm sau đó

| STT | Việc | Trạng thái |
| --- | --- | --- |
| 1 | Tạo `careerReportService` | [ ] |
| 2 | Tạo `semanticSearchService` | [ ] |
| 3 | Tạo `aiProgressService` | [ ] |
| 4 | Hoàn thiện employer jobs/candidates/interviews | [ ] |
| 5 | Tạo `industryService` | [ ] |
| 6 | Tạo `skillService` | [ ] |
| 7 | Tạo `marketDashboardService` | [ ] |
| 8 | Rà lại auth guard theo role | [ ] |
| 9 | Tách reusable components | [ ] |
| 10 | Hoàn thiện loading/empty/error states | [ ] |

---

## 8. Kết luận

Frontend hiện tại không thiếu ý tưởng màn hình, mà thiếu ba thứ chính:

1. Nối API thật theo đúng backend hiện tại.
2. Đưa cụm AI mạnh nhất của hệ thống vào FE này.
3. Chuẩn hóa service layer để candidate, employer, admin cùng dùng dữ liệu thật.

Nếu làm theo đúng bảng trên, FE sẽ tiến rất nhanh mà không cần thay đổi kiến trúc BE/AI hiện có.
