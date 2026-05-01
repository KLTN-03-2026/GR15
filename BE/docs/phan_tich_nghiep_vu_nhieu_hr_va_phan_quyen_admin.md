# Phân Tích Nghiệp Vụ: Nhiều HR Trong Một Công Ty Và Phân Quyền Admin

## 1. Bối cảnh hiện tại

Trong schema hiện tại, hệ thống đang thiết kế theo hướng:

- một tài khoản trong `nguoi_dungs` có một `vai_tro` lớn:
  - `ung_vien`
  - `nha_tuyen_dung`
  - `admin`
- một công ty đang gắn với một tài khoản quản lý chính qua:
  - `cong_tys.nguoi_dung_id`

Điều này có nghĩa là ở mức nghiệp vụ hiện tại:

- một công ty chỉ có một HR hoặc một tài khoản nhà tuyển dụng chính quản lý
- toàn bộ admin hệ thống đang bị gom vào một nhóm `admin`

Mô hình này phù hợp cho giai đoạn đầu, demo hoặc MVP, vì:

- đơn giản
- dễ code
- dễ kiểm soát logic
- ít bảng hơn

Tuy nhiên, nếu xét theo nghiệp vụ thực tế của các nền tảng tuyển dụng, mô hình này sẽ sớm bộc lộ hạn chế.

---

## 2. Có nên để một công ty chỉ có một HR quản lý không?

## Kết luận ngắn

Không nên giữ cố định mô hình này nếu hệ thống muốn mở rộng thực tế.

## Vì sao?

Trong nghiệp vụ tuyển dụng thực tế, một công ty thường không chỉ có một người thao tác trên hệ thống. Thông thường sẽ có:

- người tạo tài khoản đầu tiên
- HR đăng tin tuyển dụng
- HR xử lý ứng viên
- trưởng nhóm tuyển dụng
- người chỉ xem báo cáo hoặc quản lý công ty

Nếu chỉ dùng `cong_tys.nguoi_dung_id`, hệ thống sẽ gặp các vấn đề:

- không thể cho nhiều HR cùng quản lý một công ty
- không biết ai là người tạo hoặc sửa tin tuyển dụng
- không tách được người có quyền duyệt ứng viên và người chỉ xem
- khó audit trách nhiệm nội bộ
- khó mở rộng doanh nghiệp vừa và lớn

## Khi nào mô hình hiện tại vẫn chấp nhận được?

Mô hình hiện tại vẫn có thể chấp nhận nếu:

- hệ thống chỉ phục vụ demo
- công ty giả định chỉ có một tài khoản sử dụng
- chưa cần phân quyền chi tiết nội bộ doanh nghiệp

Nhưng nếu muốn hệ thống giống nghiệp vụ tuyển dụng thật hơn, thì nên tách.

---

## 3. Có nên hỗ trợ một công ty có nhiều HR không?

## Kết luận ngắn

Có, nên hỗ trợ.

## Thiết kế nghiệp vụ phù hợp

Nên chuyển từ mô hình:

- `1 cong_ty -> 1 nguoi_dung`

sang mô hình:

- `1 cong_ty -> nhieu nguoi_dung`

thông qua bảng trung gian.

## Bảng nên thêm

Nên thêm bảng:

- `cong_ty_nguoi_dungs`

Ví dụ các thuộc tính chính:

- `id`
- `cong_ty_id`
- `nguoi_dung_id`
- `vai_tro_noi_bo`
- `duoc_tao_boi`
- `trang_thai`
- `created_at`
- `updated_at`

## Ý nghĩa của `vai_tro_noi_bo`

`vai_tro_noi_bo` là quyền bên trong công ty, ví dụ:

- `owner`
- `admin_hr`
- `recruiter`
- `viewer`

Nhờ đó:

- một công ty có thể có nhiều HR
- mỗi HR có phạm vi quyền riêng
- hệ thống phản ánh đúng vận hành doanh nghiệp hơn

## Có nên bỏ `cong_tys.nguoi_dung_id` không?

Không nhất thiết phải bỏ ngay.

Hướng thực tế nhất là:

- giữ `cong_tys.nguoi_dung_id` như người sở hữu hoặc người tạo công ty đầu tiên
- thêm `cong_ty_nguoi_dungs` để quản lý nhiều HR

Cách này giúp:

- không phá cấu trúc cũ quá mạnh
- dễ migrate dữ liệu
- giữ tương thích ngược với codebase hiện tại

---

## 4. Có nên chỉ giữ một loại admin hệ thống không?

## Kết luận ngắn

Không nên.

Nếu hệ thống có nhiều người vận hành, thì việc chỉ có một loại `admin` là quá thô và dễ gây rủi ro.

## Hạn chế của cách hiện tại

Nếu chỉ dùng:

- `nguoi_dungs.vai_tro = admin`

thì mọi admin sẽ có cùng một quyền, ví dụ:

- xem toàn bộ dữ liệu
- sửa toàn bộ dữ liệu
- quản lý người dùng
- quản lý công ty
- quản lý tin tuyển dụng
- thay đổi cấu hình hệ thống

Điều này gây ra:

- khó phân quyền
- khó kiểm soát thao tác nhạy cảm
- khó audit
- khó giao việc theo đúng trách nhiệm

---

## 5. Có nên có nhiều loại admin không?

## Kết luận ngắn

Có, nên có.

## Phân cấp admin nên có

Tối thiểu nên có 3 mức:

### `super_admin`

Quyền cao nhất:

- tạo hoặc khóa admin khác
- quản lý toàn bộ người dùng
- cấu hình hệ thống
- cấu hình AI provider
- quản lý billing hoặc payment
- xem toàn bộ dashboard và log

### `admin`

Quyền vận hành chung:

- quản lý công ty
- quản lý tin tuyển dụng
- quản lý ngành nghề, kỹ năng
- quản lý người dùng ở mức vận hành
- xem dashboard quản trị

### `moderator` hoặc `staff_admin`

Quyền thấp hơn:

- duyệt nội dung
- duyệt tin tuyển dụng hoặc công ty
- hỗ trợ người dùng
- xem dashboard mức cơ bản

Không nên có quyền:

- tạo admin khác
- sửa cấu hình hệ thống
- truy cập các tính năng nhạy cảm

---

## 6. Admin hệ thống có giống admin nội bộ công ty không?

Không giống.

Đây là hai lớp nghiệp vụ khác nhau.

## Admin hệ thống

Là người vận hành toàn nền tảng:

- quản trị hệ thống SmartJob AI
- quản lý dữ liệu và cấu hình toàn hệ thống

## Admin nội bộ công ty

Là người quản lý bên trong một công ty:

- quản lý HR khác trong công ty
- quản lý tin tuyển dụng của công ty
- xử lý ứng viên của công ty

Vì vậy, không nên gộp hai loại này thành một khái niệm duy nhất.

---

## 7. Nên thiết kế phân quyền admin theo cách nào?

Có hai hướng.

## Hướng 1: đơn giản, phù hợp KLTN

Giữ:

- `nguoi_dungs.vai_tro`

và thêm:

- `admin_role`

Ví dụ:

- `super_admin`
- `admin`
- `moderator`

Ưu điểm:

- dễ triển khai
- dễ giải thích
- đủ đẹp cho báo cáo

Nhược điểm:

- chưa linh hoạt bằng hệ RBAC đầy đủ

## Hướng 2: chuẩn sản phẩm, hướng mở rộng dài hạn

Thiết kế RBAC:

- `vai_tro_he_thongs`
- `quyen_he_thongs`
- `nguoi_dung_vai_tro_he_thongs`
- `vai_tro_quyen_he_thongs`

Ưu điểm:

- phân quyền rất linh hoạt
- dễ mở rộng
- phù hợp hệ thống lớn

Nhược điểm:

- phức tạp hơn
- nhiều bảng hơn
- nặng hơn cho giai đoạn KLTN nếu chưa thực sự cần code hết

---

## 8. Đề xuất phù hợp nhất cho hệ thống hiện tại

Nếu xét theo trạng thái hiện tại của hệ thống và mức độ hoàn thiện đang có, hướng phù hợp nhất là:

### Với doanh nghiệp

Thêm:

- `cong_ty_nguoi_dungs`

để hỗ trợ:

- nhiều HR trong một công ty
- phân quyền nội bộ công ty

### Với admin hệ thống

Giữ:

- `nguoi_dungs.vai_tro = admin`

và thêm phân tầng:

- `admin_role`

Ví dụ:

- `super_admin`
- `admin`
- `moderator`

Đây là hướng cân bằng tốt giữa:

- tính thực tế
- độ đẹp của nghiệp vụ
- khả năng giải thích trong khóa luận
- độ phức tạp triển khai

---

## 9. Đề xuất schema mở rộng sau cùng

## Giữ nguyên

- `nguoi_dungs`
- `cong_tys`

## Mở rộng thêm

### A. Cho nhiều HR trong một công ty

Thêm:

- `cong_ty_nguoi_dungs`

Ví dụ:

- `id`
- `cong_ty_id`
- `nguoi_dung_id`
- `vai_tro_noi_bo`
- `duoc_tao_boi`
- `trang_thai`
- `created_at`
- `updated_at`

### B. Cho nhiều loại admin hệ thống

### Cách nhẹ

Thêm vào `nguoi_dungs`:

- `admin_role`

### Cách chuẩn hơn

Thêm các bảng RBAC nếu muốn mở rộng sau này:

- `vai_tro_he_thongs`
- `quyen_he_thongs`
- `nguoi_dung_vai_tro_he_thongs`
- `vai_tro_quyen_he_thongs`

---

## 10. Kết luận

Nếu xét theo nghiệp vụ hệ thống tuyển dụng thực tế, thì:

- nên hỗ trợ một công ty có nhiều HR quản lý
- nên hỗ trợ nhiều admin hệ thống với các mức quyền khác nhau
- không nên khóa cứng mọi quyền chỉ trong `nguoi_dungs.vai_tro` như hiện tại nếu muốn hệ thống phát triển lâu dài

Tuy nhiên, với giai đoạn hiện tại của hệ thống, hướng hợp lý nhất là:

- mở rộng vừa đủ, không làm hệ thống phức tạp quá mức
- thêm bảng `cong_ty_nguoi_dungs`
- thêm `admin_role` hoặc tối thiểu hóa phân tầng admin

Đây là lựa chọn cân bằng tốt nhất giữa:

- nghiệp vụ thực tế
- độ hoàn thiện hệ thống
- chi phí triển khai
- khả năng bảo vệ và giải thích trong khóa luận
