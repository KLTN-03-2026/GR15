# Giải Thích Học Thuật: Career Report v2

## 1. Mục tiêu

Chức năng `Career Report v2` được xây dựng nhằm hỗ trợ ứng viên:

- xác định hướng nghề nghiệp phù hợp với hồ sơ hiện tại
- nhận diện nhóm năng lực nổi bật
- phát hiện khoảng thiếu hụt kỹ năng
- gợi ý lộ trình phát triển ngắn hạn

Khác với bản v1 chỉ đề xuất một nghề chính dựa trên nhóm kỹ năng trội nhất, bản v2 kết hợp nhiều nguồn tín hiệu để tăng độ chính xác và độ sâu tư vấn.

## 2. Dữ liệu đầu vào

Career Report v2 sử dụng ba nhóm dữ liệu chính:

### 2.1. Dữ liệu hồ sơ đã phân tích

Lấy từ:

- `ho_sos`
- `ho_so_parsings`

Các thuộc tính được khai thác gồm:

- tiêu đề hồ sơ
- trình độ học vấn
- số năm kinh nghiệm
- danh sách kỹ năng đã parse
- học vấn và kinh nghiệm được bóc tách từ CV

### 2.2. Danh mục kỹ năng chuẩn hóa

Lấy từ:

- `skill_aliases.json`
- bảng `ky_nangs`

Mỗi kỹ năng được gắn với một `category` như:

- `backend_development`
- `mobile_development`
- `digital_marketing`
- `finance_accounting`
- `logistics_supply_chain`

Việc gắn category giúp hệ thống không chỉ nhìn vào từng kỹ năng rời rạc, mà còn suy ra cụm năng lực chuyên môn lớn hơn.

### 2.3. Kết quả matching với các tin tuyển dụng

Lấy từ:

- `ket_qua_matchings`

Các thông tin được sử dụng:

- điểm phù hợp của từng job
- danh sách kỹ năng đã khớp
- danh sách kỹ năng còn thiếu
- level/cấp bậc công việc từ `chi_tiet_diem`

Nhờ đó hệ thống có thể phân tích không chỉ “ứng viên có gì”, mà còn “thị trường đang đòi hỏi gì”.

## 3. Logic xử lý của Career Report v2

### 3.1. Xác định nhóm năng lực nổi bật

Từ danh sách kỹ năng của CV, hệ thống đếm số lượng kỹ năng thuộc từng category.

Ví dụ:

- `Laravel`, `REST API`, `Git` -> `backend_development`
- `Docker` -> `devops_cloud`
- `MySQL` -> `database`

Sau đó lấy ra các category xuất hiện nhiều nhất để mô tả chân dung chuyên môn của ứng viên.

### 3.2. Ước lượng level ứng viên

Level ứng viên được suy ra từ:

- tiêu đề hồ sơ, ví dụ `Junior Backend Developer`
- số năm kinh nghiệm nếu tiêu đề không rõ

Ví dụ:

- `< 1 năm` -> `intern`
- `<= 1 năm` -> `fresher`
- `<= 2 năm` -> `junior`
- `<= 4 năm` -> `mid`
- `> 4 năm` -> `senior`

Mục đích của bước này là để gợi ý nghề ở mức cấp bậc phù hợp, thay vì chỉ nêu một chức danh chung chung.

### 3.3. Sinh danh sách nghề đề xuất

Career Report v2 không chỉ sinh một nghề duy nhất, mà tạo danh sách nghề đề xuất theo thứ tự ưu tiên từ hai nguồn:

#### Nguồn 1: các công việc đang match tốt

Những job có `diem_phu_hop` cao trong bảng `ket_qua_matchings` sẽ được ưu tiên sử dụng trực tiếp làm nghề đề xuất.

#### Nguồn 2: mapping từ category -> nhiều role

Ví dụ:

- `backend_development` -> `Backend Developer`, `PHP Developer`, `API Developer`
- `digital_marketing` -> `Chuyên viên Digital Marketing`, `Performance Marketing`, `Content Marketing Specialist`

Sau đó hệ thống có thể gắn thêm tiền tố level như:

- `Junior Backend Developer`
- `Senior DevOps Engineer`

### 3.4. Gợi ý kỹ năng cần bổ sung

Phần `goi_y_ky_nang_bo_sung` được tổng hợp từ hai nguồn:

#### Nguồn 1: kỹ năng còn thiếu lặp lại trong các JD có matching cao

Ví dụ:

- nhiều job backend đều thiếu `Docker`, `System Design`

=> đây là tín hiệu mạnh cho thấy ứng viên nên ưu tiên học các kỹ năng này.

#### Nguồn 2: bộ kỹ năng mặc định theo category

Ví dụ:

- `backend_development` -> `Docker`, `Thiết kế hệ thống`, `Kiểm thử phần mềm`
- `data_analysis` -> `Power BI`, `Tableau`, `Data Visualization`

Nhờ đó, nếu dữ liệu matching chưa đủ nhiều, hệ thống vẫn có thể sinh ra gợi ý hợp lý.

### 3.5. Tính mức độ phù hợp tổng quát

`muc_do_phu_hop` trong Career Report v2 được tính từ:

- điểm matching trung bình của các job phù hợp nhất
- bonus theo độ phong phú của nhóm kỹ năng

Mục tiêu của chỉ số này không phải để thay thế `diem_phu_hop` của từng job, mà để phản ánh “mức sẵn sàng nghề nghiệp tổng quan” của ứng viên.

## 4. Kết quả đầu ra

Career Report v2 trả về:

- `nghe_de_xuat`: nghề chính đề xuất
- `muc_do_phu_hop`: mức độ phù hợp tổng quan
- `goi_y_ky_nang_bo_sung`: JSON có cấu trúc gồm:
  - `skills`
  - `recommended_roles`
  - `candidate_level`
  - `top_matching_jobs`
  - `strength_categories`
- `bao_cao_chi_tiet`: báo cáo diễn giải bằng ngôn ngữ tự nhiên

## 5. Điểm cải tiến so với bản v1

So với Career Report v1, bản v2 có các cải tiến chính:

- không chỉ đề xuất một nghề đơn lẻ
- có xét level ứng viên
- kết hợp dữ liệu CV và dữ liệu thị trường tuyển dụng nội bộ
- gợi ý kỹ năng dựa trên cả skill gap thực tế lẫn category chuyên môn
- sinh báo cáo định hướng rõ ràng hơn về hướng phát triển tiếp theo

## 6. Ý nghĩa học thuật và thực tiễn

Về mặt học thuật, Career Report v2 thể hiện cách kết hợp:

- trích xuất thông tin từ CV
- chuẩn hóa kỹ năng
- đối sánh với nhu cầu tuyển dụng
- suy luận hướng nghề nghiệp

Về mặt thực tiễn, mô hình này giúp:

- tăng giá trị tư vấn cho ứng viên
- hỗ trợ định hướng học tập và phát triển nghề nghiệp
- nâng chất lượng recommendation trong hệ thống tuyển dụng tích hợp AI

## 7. Hạn chế hiện tại

Career Report v2 vẫn chủ yếu là mô hình rule-based có giải thích, nên còn các giới hạn:

- chưa dùng mô hình học sâu chuyên biệt cho tư vấn nghề nghiệp
- chưa sinh nhiều lộ trình nghề nghiệp theo thời gian
- chưa cá nhân hóa sâu theo sở thích hoặc mục tiêu cá nhân

Tuy nhiên, đây là một nền tảng tốt để phát triển lên chatbot tư vấn nghề nghiệp hoặc recommendation cá nhân hóa ở các giai đoạn tiếp theo.
