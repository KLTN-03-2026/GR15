# Giải thích nghiệp vụ chức năng thanh toán

## 1. Mục đích

Chức năng thanh toán được xây dựng để quản lý cách ứng viên sử dụng các tính năng AI trong hệ thống theo 3 lớp:

- `Gói Pro`
- `Free quota`
- `Ví AI`

Mục tiêu nghiệp vụ là:

- Cho phép người dùng dùng thử miễn phí ở mức giới hạn
- Khuyến khích nâng cấp lên `Gói Pro` để có quota lớn hơn
- Vẫn cho phép tiếp tục sử dụng bằng `Ví AI` khi hết quota
- Theo dõi được toàn bộ giao dịch thanh toán và tiêu hao AI

## 2. Đối tượng sử dụng

### Ứng viên

Ứng viên là đối tượng chính của module này. Ứng viên có thể:

- Nạp tiền vào `Ví AI`
- Mua `Gói Pro`
- Dùng AI qua `Career Report`
- Dùng AI qua `Cover Letter`
- Dùng AI qua `Chatbot`
- Dùng AI qua `Mock Interview`
- Xem lịch sử thanh toán
- Xem hạn mức còn lại theo từng tính năng

### Admin

Admin có thể:

- Xem tổng quan doanh thu
- Xem số giao dịch nạp ví
- Xem số giao dịch mua gói
- Xem trạng thái giao dịch
- Theo dõi gói nào đang được mua nhiều

## 3. Bài toán nghiệp vụ cần giải quyết

Nếu chỉ thu tiền theo một cách duy nhất thì trải nghiệm sẽ kém linh hoạt:

- Bắt trả phí ngay từ đầu sẽ khó thu hút người dùng mới
- Chỉ dùng subscription sẽ không phù hợp với người dùng ít nhu cầu
- Chỉ dùng pay-per-use sẽ khó tạo doanh thu định kỳ

Vì vậy hệ thống dùng mô hình kết hợp:

- Người mới có `free quota`
- Người cần dùng nhiều có thể mua `Gói Pro`
- Khi hết quota vẫn có thể trả theo lượt bằng `Ví AI`

## 4. Các khái niệm nghiệp vụ chính

### Ví AI

`Ví AI` là số dư tiền nội bộ để thanh toán cho các lượt dùng AI.

Ví có 3 giá trị quan trọng:

- `Số dư hiện tại`
- `Số dư tạm giữ`
- `Số dư khả dụng`

Ý nghĩa:

- `Số dư hiện tại` là tổng tiền trong ví
- `Số dư tạm giữ` là phần tiền đã được giữ chỗ cho request đang xử lý
- `Số dư khả dụng` là phần tiền còn dùng được ngay

### Free quota

`Free quota` là số lượt miễn phí theo từng tính năng AI. Đây là lớp ưu đãi để người dùng trải nghiệm trước khi trả phí.

### Gói Pro

`Gói Pro` là subscription theo chu kỳ:

- `PRO_MONTHLY`
- `PRO_YEARLY`

Mỗi gói cung cấp quota riêng cho từng tính năng AI.

### Ví trả theo lượt

Khi người dùng không còn `Pro quota` và cũng hết `free quota`, hệ thống sẽ tính tiền trực tiếp từ `Ví AI` theo bảng giá từng tính năng.

### Giao dịch thanh toán

Giao dịch thanh toán là bản ghi ghi nhận:

- Nạp ví
- Mua gói Pro

Trạng thái nghiệp vụ gồm:

- `pending`
- `success`
- `failed`
- `cancelled`

### Entitlement

`Entitlement` là ảnh chụp nhanh quyền sử dụng AI hiện tại của người dùng theo từng tính năng. Nó trả về:

- quota miễn phí
- quota Pro
- giá ví

Frontend dùng entitlement để quyết định CTA nào cần hiển thị.

## 5. Thứ tự ưu tiên thanh toán

Đây là rule cốt lõi nhất của toàn bộ nghiệp vụ:

- `Pro -> Free -> Wallet`

Ý nghĩa:

1. Nếu còn quota từ `Gói Pro`, hệ thống dùng quota Pro trước.
2. Nếu không còn quota Pro nhưng còn `free quota`, hệ thống dùng quota miễn phí.
3. Nếu đã hết cả hai, hệ thống trừ tiền từ `Ví AI`.

Rule này giúp:

- Tối ưu giá trị cho người đã mua gói
- Không lãng phí quota subscription
- Giữ logic nhất quán trên mọi tính năng AI

## 6. Các tính năng AI chịu billing

Hệ thống hiện áp dụng chung rule billing cho 4 tính năng:

- `cover_letter_generation`
- `career_report_generation`
- `chatbot_message`
- `mock_interview_session`

Mỗi tính năng có:

- quota miễn phí riêng
- quota Pro riêng
- đơn giá ví riêng

## 7. Luồng nghiệp vụ chính

### Luồng 1: Nạp tiền vào Ví AI

1. Ứng viên vào trang `Ví AI`
2. Chọn số tiền muốn nạp
3. Hệ thống tạo giao dịch `pending`
4. Người dùng được chuyển sang cổng thanh toán `MoMo`
5. Nếu MoMo thanh toán thành công, hệ thống ghi nhận giao dịch `success`
6. Ví AI được cộng tiền
7. Người dùng có thể dùng số dư đó để trả cho AI

Giá trị nghiệp vụ:

- Biến MoMo thành nguồn nạp tiền chung cho toàn bộ tính năng AI
- Không cần thanh toán lẻ từng request với cổng thanh toán bên ngoài

### Luồng 2: Mua Gói Pro

1. Ứng viên vào trang `Gói Pro`
2. Chọn `Gói Pro Tháng` hoặc `Gói Pro Năm`
3. Hệ thống tạo giao dịch mua gói
4. Người dùng thanh toán qua `MoMo`
5. Khi thành công, hệ thống kích hoạt subscription
6. Quota Pro của các feature được mở khóa

Giá trị nghiệp vụ:

- Tạo doanh thu định kỳ
- Cho người dùng có nhu cầu cao một mức giá tối ưu hơn trả theo lượt

### Luồng 3: Dùng AI khi còn quota Pro

1. Người dùng bấm sử dụng một tính năng AI
2. Hệ thống kiểm tra entitlement
3. Nếu còn quota Pro, hệ thống trừ quota Pro
4. Không trừ tiền ví

Giá trị nghiệp vụ:

- Người dùng cảm nhận rõ lợi ích của gói Pro

### Luồng 4: Dùng AI khi còn free quota

1. Người dùng chưa có Pro hoặc Pro đã hết quota
2. Hệ thống kiểm tra `free quota`
3. Nếu còn, hệ thống cho dùng miễn phí
4. Không trừ ví

Giá trị nghiệp vụ:

- Hỗ trợ onboarding
- Tăng tỷ lệ trải nghiệm AI trước khi trả phí

### Luồng 5: Dùng AI bằng Ví AI

1. Người dùng đã hết `Pro quota` và `free quota`
2. Hệ thống lấy đơn giá của tính năng
3. Kiểm tra ví có đủ tiền không
4. Nếu đủ, hệ thống giữ tiền tạm thời
5. Khi AI xử lý thành công, hệ thống kết toán chính thức
6. Nếu AI lỗi, hệ thống hoàn phần tiền tạm giữ

Giá trị nghiệp vụ:

- Tránh thu sai tiền khi request thất bại
- Tăng độ tin cậy cho trải nghiệm trả phí

## 8. Tại sao phải có cơ chế `reserve / commit / release`

Đây là phần quan trọng về nghiệp vụ kiểm soát tiền:

- `reserve`: giữ chỗ tiền trước khi gọi AI
- `commit`: chốt thu tiền khi request thành công
- `release`: trả lại tiền khi request thất bại

Nếu không có cơ chế này:

- có thể trừ tiền dù AI bị lỗi
- có thể phát sinh sai lệch ví khi request bị gián đoạn

Nghiệp vụ này giúp ví hoạt động giống một ledger mini, có thể kiểm toán được.

## 9. Ý nghĩa của entitlement trên giao diện

Frontend không chỉ hiển thị nút dùng AI, mà phải hiển thị đúng bối cảnh trả phí hiện tại.

Ví dụ:

- Nếu còn Pro: hiện số lượt còn lại
- Nếu còn miễn phí: hiện `Miễn phí x/y`
- Nếu phải dùng ví: hiện giá tiền

Giá trị nghiệp vụ:

- Minh bạch chi phí trước khi bấm
- Giảm khiếu nại “bị trừ tiền mà không biết”
- Tăng khả năng upsell lên gói Pro

## 10. Lịch sử giao dịch và ý nghĩa nghiệp vụ

Người dùng cần xem được:

- đã nạp bao nhiêu
- đã mua gói nào
- giao dịch nào đang chờ
- giao dịch nào thành công hoặc thất bại

Admin cần xem được:

- doanh thu tổng
- tỷ trọng nạp ví và mua gói
- giao dịch pending để theo dõi bất thường
- gói nào bán tốt

Lịch sử giao dịch là phần giúp minh bạch tài chính và hỗ trợ xử lý khiếu nại.

## 11. Vai trò của admin billing dashboard

Dashboard billing không chỉ để xem doanh thu, mà phục vụ 3 nhu cầu quản trị:

- Theo dõi sức khỏe tài chính của module AI
- Đánh giá hiệu quả của `Ví AI` và `Gói Pro`
- Phát hiện sớm giao dịch lỗi, giao dịch pending bất thường

## 12. Vai trò của queue và billing event

Sau khi thanh toán hoặc kích hoạt gói, hệ thống phát event billing để:

- ghi log hoạt động
- gửi notification cho người dùng

Tách phần này sang queue giúp:

- không làm chậm request chính
- giảm lỗi dây chuyền khi notification hoặc log gặp vấn đề
- dễ mở rộng thêm các xử lý sau thanh toán sau này

## 13. Các rule nghiệp vụ quan trọng

### Rule 1: Không dùng ví nếu vẫn còn quota phù hợp

Nếu còn `Pro` hoặc `free quota`, hệ thống không được trừ ví.

### Rule 2: Không trừ tiền hai lần cho cùng một request

Các request quan trọng có cơ chế chống duplicate để tránh double charge khi người dùng bấm nhiều lần.

### Rule 3: Không ghi nhận thành công nếu cổng thanh toán chưa xác nhận

Giao dịch MoMo chỉ được coi là hoàn tất khi hệ thống nhận đủ dữ liệu xác nhận hợp lệ.

### Rule 4: Không tạo usage sai khi ví không đủ tiền

Nếu ví không đủ, request phải bị chặn ngay.

### Rule 5: Quota còn lại được tính động

Hệ thống không lưu một cột quota còn lại riêng, mà tính từ:

- quota tổng
- số lượt đã dùng

Điều này giúp tránh lệch dữ liệu.

## 14. Các giới hạn nghiệp vụ hiện tại

- Chưa có retry/replay riêng cho webhook MoMo ở môi trường public
- Chưa có monitoring chuyên biệt cho IPN lỗi
- Nhánh local đang có logic auto-complete để demo nhanh trên `127.0.0.1`

Các điểm này không làm sai core nghiệp vụ, nhưng cần hoàn thiện thêm trước khi scale production lớn.

## 15. Kết luận

Chức năng thanh toán của hệ thống đang theo mô hình `hybrid billing`:

- miễn phí để thu hút người dùng mới
- subscription để tối ưu cho người dùng thường xuyên
- wallet để đảm bảo mọi nhu cầu phát sinh đều có cách thanh toán

Về mặt nghiệp vụ, module này giúp cân bằng 3 mục tiêu:

- tăng trải nghiệm dùng thử
- tạo doanh thu
- giữ minh bạch tài chính cho cả người dùng và admin
