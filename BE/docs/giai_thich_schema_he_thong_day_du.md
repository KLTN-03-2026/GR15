# Giải Thích Schema Hệ Thống SmartJob AI

Tài liệu này mô tả schema hoàn thiện hiện tại của hệ thống SmartJob AI, ý nghĩa nghiệp vụ của từng bảng, từng nhóm thuộc tính quan trọng, đồng thời đề xuất phương án mở rộng khi một công ty có nhiều HR cùng quản lý và cách phân quyền phù hợp trong hệ thống.

## 1. Tổng quan kiến trúc dữ liệu

Schema hiện tại được chia thành các nhóm chính:

- `Xác thực và người dùng`
- `Hồ sơ ứng viên và kỹ năng`
- `Công ty, tuyển dụng và ứng tuyển`
- `AI parsing, matching, tư vấn nghề nghiệp`
- `Chatbot và mock interview`
- `Semantic search và thống kê thị trường`
- `Billing và phân quyền mở rộng` (mới ở mức thiết kế)

Hệ thống hiện tại phù hợp tốt với mô hình:

- Một tài khoản ứng viên có thể có nhiều hồ sơ
- Một tài khoản nhà tuyển dụng quản lý một công ty
- Một công ty đăng nhiều tin tuyển dụng
- Một hồ sơ có thể ứng tuyển nhiều tin tuyển dụng
- AI được gắn vào toàn bộ luồng phân tích, tư vấn và luyện phỏng vấn

---

## 2. Nhóm bảng xác thực và người dùng

### 2.1. `nguoi_dungs`

Đây là bảng gốc của toàn hệ thống, lưu tất cả tài khoản đăng nhập.

#### Thuộc tính chính

- `id`: khóa chính người dùng
- `ho_ten`: họ tên hiển thị
- `email`: email đăng nhập, duy nhất
- `email_verified_at`: thời điểm xác thực email
- `mat_khau`: mật khẩu đã băm
- `so_dien_thoai`: số điện thoại
- `ngay_sinh`, `gioi_tinh`, `dia_chi`: thông tin cá nhân cơ bản
- `anh_dai_dien`: ảnh đại diện
- `vai_tro`: vai trò toàn cục của tài khoản
  - `0`: ứng viên
  - `1`: nhà tuyển dụng
  - `2`: admin
- `trang_thai`: hoạt động hay bị khóa
- `remember_token`: token nhớ đăng nhập
- `created_at`, `updated_at`: thời gian tạo và cập nhật
- `deleted_at`: xóa mềm

#### Ý nghĩa nghiệp vụ

- Là bảng trung tâm để xác định tài khoản thuộc loại nào
- Hiện tại mỗi tài khoản chỉ có một vai trò toàn cục
- Đây là nơi dùng để xác thực, phân quyền route và gắn ownership dữ liệu

---

## 3. Nhóm bảng hồ sơ ứng viên

### 3.1. `ho_sos`

Lưu hồ sơ/CV của ứng viên.

#### Thuộc tính chính

- `nguoi_dung_id`: ứng viên sở hữu hồ sơ
- `tieu_de_ho_so`: tên hồ sơ
- `file_cv`, `file_cv_goc`: file CV đã xử lý và file gốc
- `mo_ta`: mô tả ngắn
- `muc_tieu_nghe_nghiep`: mục tiêu nghề nghiệp
- `kinh_nghiem_nam`: số năm kinh nghiệm
- `vi_tri_mong_muon`: vị trí ứng tuyển mong muốn
- `muc_luong_mong_muon`: lương kỳ vọng
- `dia_diem_mong_muon`: khu vực mong muốn
- `hinh_thuc_lam_viec`: full-time, remote, hybrid...
- `trang_thai`: công khai hoặc ẩn

#### Ý nghĩa nghiệp vụ

- Một ứng viên có thể có nhiều hồ sơ
- Là đầu vào cho:
  - parse CV
  - matching
  - career report
  - chatbot
  - mock interview

### 3.2. `nguoi_dung_ky_nangs`

Lưu kỹ năng cá nhân của người dùng theo catalog chuẩn.

#### Thuộc tính chính

- `nguoi_dung_id`: người dùng sở hữu kỹ năng
- `ky_nang_id`: kỹ năng chuẩn hóa
- `muc_do`: mức độ kỹ năng
- `nam_kinh_nghiem`: số năm kinh nghiệm cho kỹ năng này
- `so_chung_chi`: số chứng chỉ
- `hinh_anh`: minh chứng nếu có

#### Ý nghĩa nghiệp vụ

- Dùng để làm giàu hồ sơ ứng viên
- Hỗ trợ matching và tư vấn nghề nghiệp

### 3.3. `ho_so_parsings`

Lưu kết quả AI parse CV.

#### Thuộc tính chính

- `ho_so_id`: hồ sơ được parse
- `raw_text`: text trích xuất từ CV
- `parsed_skills_json`: kỹ năng trích xuất
- `parsed_experience_json`: kinh nghiệm làm việc
- `parsed_education_json`: học vấn
- `parsed_projects_json`: dự án
- `parsed_summary_json`: tóm tắt hồ sơ
- `extracted_title`: chức danh AI suy ra
- `total_experience_years`: tổng năm kinh nghiệm AI tính
- `confidence_score`: độ tin cậy
- `model_name`: model AI đã dùng

#### Ý nghĩa nghiệp vụ

- Là nguồn dữ liệu đầu vào quan trọng cho:
  - matching
  - career report
  - chatbot
  - mock interview

---

## 4. Nhóm bảng công ty và tuyển dụng

### 4.1. `cong_tys`

Lưu thông tin công ty.

#### Thuộc tính chính

- `nguoi_dung_id`: tài khoản nhà tuyển dụng đang sở hữu/quản lý công ty
- `ten_cong_ty`: tên công ty
- `ma_so_thue`: mã số thuế
- `mo_ta`: giới thiệu công ty
- `dia_chi`: địa chỉ
- `website`: website
- `quy_mo`: quy mô nhân sự
- `logo`: logo công ty
- `trang_thai`: trạng thái công ty

#### Ý nghĩa nghiệp vụ hiện tại

- Hiện schema này đang thể hiện mô hình:
  - `một công ty gắn với một tài khoản HR chính`
- Đây là điểm hiện tại đơn giản, đủ tốt cho MVP/KLTN

### 4.2. `tin_tuyen_dungs`

Lưu tin tuyển dụng.

#### Thuộc tính chính

- `tieu_de`: tiêu đề công việc
- `mo_ta_cong_viec`: mô tả JD
- `dia_diem_lam_viec`: nơi làm việc
- `hinh_thuc_lam_viec`: full-time, remote...
- `cap_bac`: level
- `so_luong_tuyen`: số lượng tuyển
- `muc_luong`, `muc_luong_tu`, `muc_luong_den`, `don_vi_luong`: lương
- `kinh_nghiem_yeu_cau`: yêu cầu kinh nghiệm
- `trinh_do_yeu_cau`: yêu cầu học vấn
- `ngay_het_han`: hạn tuyển
- `luot_xem`: số lượt xem
- `cong_ty_id`: công ty đăng tin
- `trang_thai`: hoạt động hay tạm ngưng

#### Ý nghĩa nghiệp vụ

- Là đơn vị trung tâm của bài toán tuyển dụng
- Được dùng trong:
  - public job listing
  - matching
  - semantic search
  - mock interview
  - market dashboard

### 4.3. `chi_tiet_nganh_nghes`

Bảng nối nhiều-nhiều giữa `tin_tuyen_dungs` và `nganh_nghes`.

#### Ý nghĩa nghiệp vụ

- Một job có thể thuộc nhiều ngành nghề
- Một ngành nghề có nhiều job

### 4.4. `tin_tuyen_dung_parsings`

Lưu kết quả AI parse JD.

#### Thuộc tính chính

- `tin_tuyen_dung_id`: job được parse
- `parsed_skills_json`: kỹ năng AI trích
- `parsed_requirements_json`: yêu cầu chính
- `parsed_benefits_json`: quyền lợi
- `parsed_salary_json`: thông tin lương
- `parsed_location_json`: địa điểm
- `model_name`: model đã dùng
- `confidence_score`: độ tin cậy parse

### 4.5. `tin_tuyen_dung_ky_nangs`

Lưu kỹ năng yêu cầu đã chuẩn hóa của JD.

#### Thuộc tính chính

- `tin_tuyen_dung_id`, `ky_nang_id`
- `muc_do_yeu_cau`: độ sâu yêu cầu
- `bat_buoc`: có bắt buộc hay không
- `trong_so`: trọng số cho matching
- `nguon_du_lieu`: nguồn dữ liệu, ví dụ parser
- `do_tin_cay`: độ tin cậy

#### Ý nghĩa nghiệp vụ

- Là đầu vào rất quan trọng cho matching và semantic search

---

## 5. Nhóm bảng ứng tuyển

### 5.1. `ung_tuyens`

Lưu quan hệ ứng tuyển giữa hồ sơ và tin tuyển dụng.

#### Thuộc tính chính

- `tin_tuyen_dung_id`: job được nộp vào
- `ho_so_id`: hồ sơ ứng tuyển
- `trang_thai`: trạng thái đơn
  - chờ duyệt
  - đã xem
  - chấp nhận
  - từ chối
- `thu_xin_viec`: thư xin việc do người dùng nhập
- `thu_xin_viec_ai`: thư xin việc AI sinh
- `ngay_hen_phong_van`: lịch hẹn
- `ket_qua_phong_van`: kết quả phỏng vấn
- `ghi_chu`: ghi chú của HR
- `thoi_gian_ung_tuyen`: thời điểm nộp

### 5.2. `luu_tins`

Lưu job mà ứng viên đánh dấu lưu lại.

#### Thuộc tính chính

- `nguoi_dung_id`
- `tin_tuyen_dung_id`

---

## 6. Nhóm bảng AI matching và tư vấn nghề nghiệp

### 6.1. `ket_qua_matchings`

Lưu kết quả matching giữa hồ sơ và job.

#### Thuộc tính chính

- `ho_so_id`, `tin_tuyen_dung_id`
- `diem_tong`: điểm tổng
- `diem_ky_nang`
- `diem_kinh_nghiem`
- `diem_hoc_van`
- `diem_tuong_dong_noi_dung`
- `skill_gap_json`: khoảng trống kỹ năng
- `matched_skills_json`: kỹ năng đang khớp
- `missing_skills_json`: kỹ năng còn thiếu
- `keyword_matches_json`: keyword trùng
- `giai_thich`: giải thích kết quả
- `mo_hinh_su_dung`: model/công thức đã dùng

### 6.2. `tu_van_nghe_nghieps`

Lưu báo cáo tư vấn nghề nghiệp.

#### Thuộc tính chính

- `ho_so_id`
- `nghe_de_xuat`
- `cap_do_hien_tai`
- `muc_tieu_goi_y`
- `diem_san_sang`
- `ky_nang_noi_bat_json`
- `ky_nang_can_bo_sung_json`
- `lo_trinh_goi_y_json`
- `cong_viec_phu_hop_json`
- `bao_cao_text`
- `model_name`

#### Ý nghĩa nghiệp vụ

- Hỗ trợ định hướng nghề nghiệp
- Là một nguồn context cho chatbot và AI center

---

## 7. Nhóm semantic search và thống kê thị trường

### 7.1. `vector_embeddings`

Lưu metadata phục vụ semantic search.

#### Thuộc tính chính

- `entity_type`: loại dữ liệu được vector hóa
- `entity_id`: id đối tượng
- `text_content`: đoạn text dùng để embedding
- `embedding_hash`: hash kiểm soát cập nhật
- `model_name`: model embedding
- `metadata_json`: metadata đi kèm

### 7.2. `market_stats_daily`

Lưu snapshot thống kê thị trường theo ngày.

#### Thuộc tính chính

- `stat_date`: ngày thống kê
- `nganh_nghe_id`: theo ngành nào
- `avg_salary`: lương trung bình
- `median_salary`: lương median
- `demand_count`: số lượng nhu cầu tuyển dụng
- `top_skills`: top kỹ năng của ngành/ngày đó

#### Ý nghĩa nghiệp vụ

- Phục vụ dashboard admin về xu hướng thị trường
- Có thể dùng như bảng tổng hợp thay vì query trực tiếp từ dữ liệu live

---

## 8. Nhóm chatbot và mock interview

### 8.1. `ai_chat_sessions`

Lưu phiên hội thoại AI hoặc phiên mock interview.

#### Thuộc tính chính

- `nguoi_dung_id`: chủ sở hữu phiên
- `session_type`: loại phiên
  - chatbot career
  - mock interview
- `tieu_de`: tên phiên
- `related_ho_so_id`: hồ sơ liên quan
- `related_tin_tuyen_dung_id`: job liên quan
- `trang_thai`: active, closed...
- `summary`: tóm tắt ngắn
- `conversation_summary`: summary ngữ cảnh hội thoại
- `metadata_json`: dữ liệu mở rộng

### 8.2. `ai_chat_messages`

Lưu từng tin nhắn trong phiên.

#### Thuộc tính chính

- `ai_chat_session_id`
- `vai_tro`: user / assistant / system
- `noi_dung`: nội dung message
- `intent`: ý định câu hỏi
- `model_version`: model/provider đã dùng
- `metadata_json`
- `hidden_in_ui`: vẫn lưu nhưng không hiện trên UI

### 8.3. `ai_interview_reports`

Lưu báo cáo tổng kết mock interview.

#### Thuộc tính chính

- `ai_chat_session_id`
- `nguoi_dung_id`
- `related_ho_so_id`
- `related_tin_tuyen_dung_id`
- `tong_diem`
- `diem_ky_thuat`
- `diem_giao_tiep`
- `diem_phu_hop_jd`
- `diem_ro_y`
- `diem_cu_the`
- `diem_cau_truc`
- `diem_yeu_nhat`
- `cau_tra_loi_can_cai_thien_nhat`
- `diem_manh_json`
- `diem_yeu_json`
- `uu_tien_cai_thien_json`
- `ke_hoach_luyen_tiep_json`
- `de_xuat_cai_thien_text`
- `metadata_json`

#### Ý nghĩa nghiệp vụ

- Theo dõi hiệu quả mock interview
- Sinh dashboard tiến bộ nhiều phiên

---

## 9. Mô hình hiện tại: một công ty chỉ có một HR quản lý

Ở schema hiện tại, bảng `cong_tys` có cột:

- `nguoi_dung_id`

Điều này đang phản ánh mô hình:

- mỗi công ty gắn với một tài khoản nhà tuyển dụng chính

### Ưu điểm

- đơn giản
- dễ triển khai
- phù hợp với MVP hoặc KLTN giai đoạn đầu

### Hạn chế

- không hỗ trợ nhiều HR trong cùng công ty
- không có phân quyền nội bộ trong công ty
- khó mở rộng khi doanh nghiệp có nhiều recruiter

---

## 10. Nếu muốn một công ty có nhiều HR quản lý thì làm sao?

### 10.1. Cách đúng nhất

Không nên tiếp tục dùng `cong_tys.nguoi_dung_id` như quan hệ duy nhất.

Thay vào đó, nên chuyển sang mô hình:

- `một công ty có nhiều người dùng nội bộ`
- `một người dùng có thể thuộc một hoặc nhiều công ty`

### 10.2. Nên thêm bảng trung gian

Ví dụ:

### `cong_ty_nguoi_dungs`

Các cột nên có:

- `id`
- `cong_ty_id`
- `nguoi_dung_id`
- `vai_tro_noi_bo`
  - `owner`
  - `admin_hr`
  - `recruiter`
  - `viewer`
- `duoc_tao_boi`
- `trang_thai`
- `created_at`
- `updated_at`

### Ý nghĩa

- `owner`: người tạo công ty hoặc người cao nhất của công ty trong hệ thống
- `admin_hr`: HR admin nội bộ, có quyền mời/xóa recruiter khác
- `recruiter`: HR thường, quản lý tin tuyển dụng và ứng viên theo quyền được cấp
- `viewer`: chỉ được xem

### 10.3. Quyền tạo tài khoản HR mới

Bạn hỏi:
> Do người tạo tài khoản quản lý quyền thì làm sao?

Cách đúng là:

- tài khoản đầu tiên tạo công ty sẽ được gán `owner`
- `owner` có quyền:
  - mời thêm HR
  - gán vai trò cho HR
  - khóa hoặc gỡ HR khỏi công ty

Khi đó:

- không cần tạo tài khoản nhà tuyển dụng tách rời mỗi lần bằng admin hệ thống
- chính doanh nghiệp tự quản trị người dùng nội bộ của họ

### 10.4. Khi đó bảng `cong_tys` nên sửa thế nào?

Có 2 lựa chọn:

#### Lựa chọn A: vẫn giữ `nguoi_dung_id`

Xem nó là:

- `owner_id`
- tức là chủ sở hữu chính của công ty

Đây là cách thực dụng và ít phá schema nhất.

#### Lựa chọn B: bỏ hẳn `nguoi_dung_id`

Toàn bộ quan hệ công ty-người dùng chuyển sang bảng `cong_ty_nguoi_dungs`.

Đây là cách sạch hơn về mặt thiết kế, nhưng thay đổi lớn hơn.

### 10.5. Khuyến nghị thực tế

Nếu tiếp tục phát triển sản phẩm:

- nên dùng `Lựa chọn A` trước:
  - đổi nghĩa `nguoi_dung_id` thành `owner_id`
  - thêm bảng `cong_ty_nguoi_dungs`

Như vậy:

- vừa giữ tương thích với code hiện tại
- vừa mở rộng được nhiều HR

---

## 11. Có cần phân quyền cho admin không?

### 11.1. Có, nhưng phải phân biệt 2 lớp quyền

Hiện tại hệ thống có:

- `admin` toàn cục của nền tảng

Nếu mở rộng nhiều HR/công ty, bạn nên có thêm:

- `admin nội bộ công ty`

Đây là hai thứ khác nhau.

### 11.2. Admin toàn cục của nền tảng

Là tài khoản trong `nguoi_dungs.vai_tro = 2`

Quyền:

- quản lý toàn bộ người dùng
- quản lý công ty
- quản lý ngành nghề
- quản lý kỹ năng
- quản lý tin tuyển dụng
- dashboard thị trường
- log hệ thống
- cài đặt hệ thống

### 11.3. Admin nội bộ công ty

Không nên dùng chung với `vai_tro = 2`.

Nó nên nằm ở bảng `cong_ty_nguoi_dungs.vai_tro_noi_bo`.

Ví dụ:

- `owner`
- `admin_hr`

Quyền:

- mời thêm HR
- gán quyền cho recruiter
- xem toàn bộ ứng viên của công ty
- quản lý job của công ty

### 11.4. Vì sao cần tách hai lớp này?

Vì:

- `admin hệ thống` quản lý toàn nền tảng
- `admin công ty` chỉ quản lý dữ liệu nội bộ của công ty đó

Nếu không tách:

- rất dễ lẫn quyền
- nguy cơ một HR có quyền quá lớn trên toàn hệ thống

---

## 12. Đề xuất schema mở rộng cuối cùng nếu hệ thống đi xa hơn

### Giữ nguyên

- `nguoi_dungs`
- `cong_tys`
- `tin_tuyen_dungs`
- `ung_tuyens`
- toàn bộ AI tables

### Thêm mới

#### `cong_ty_nguoi_dungs`

- `id`
- `cong_ty_id`
- `nguoi_dung_id`
- `vai_tro_noi_bo`
- `duoc_tao_boi`
- `trang_thai`
- timestamps

#### Có thể thêm nếu muốn chi tiết hơn

##### `cong_ty_quyen_hans`

- định nghĩa quyền nội bộ theo role

##### hoặc đơn giản hơn

Lưu quyền chi tiết vào:

- `metadata_json`

trong bảng `cong_ty_nguoi_dungs`

---

## 13. Kết luận

### Với schema hiện tại

Hệ thống đã phù hợp tốt cho:

- KLTN
- MVP
- một công ty có một HR chính quản lý

### Nếu muốn mở rộng thật

Cần bổ sung:

- quan hệ nhiều-nhiều giữa `cong_tys` và `nguoi_dungs`
- phân quyền nội bộ công ty
- tách rõ:
  - `admin nền tảng`
  - `admin công ty`

### Khuyến nghị thiết kế tốt nhất

- Giữ `admin` toàn cục trong `nguoi_dungs.vai_tro`
- Thêm bảng `cong_ty_nguoi_dungs` để phân quyền nhiều HR trong từng công ty
- Giữ `cong_tys.nguoi_dung_id` như `owner_id` để không phá logic cũ quá nhiều

