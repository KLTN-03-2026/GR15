# Test case chức năng thanh toán

## 1. Mục tiêu

Tài liệu này dùng để test các chức năng thanh toán đã triển khai trong dự án:

- Ví AI
- Nạp tiền qua MoMo
- Free quota
- Quota Pro
- Pay-per-use cho AI feature
- Mua gói Pro qua MoMo

## 2. Phạm vi test

### Giao diện liên quan

- `Ví AI`
- `Gói Pro`
- `Career Report`
- `Chi tiết công việc` với `Cover Letter AI`
- `Việc đã lưu` với `Cover Letter AI`
- `AI Center / Chatbot`
- `AI Center / Mock Interview`

### Rule hiện tại trong code

- Thứ tự áp dụng đang là: `Pro -> Free -> Wallet`
- `quota còn lại` được tính động, không lưu cột riêng
- Local `127.0.0.1` đang dùng nhánh auto-complete cho `MoMo return success`

## 3. Dữ liệu chuẩn bị

- Tài khoản ứng viên có thể đăng nhập
- Có ít nhất 1 hồ sơ ứng viên hợp lệ
- Có ít nhất 1 job đang mở để test `Cover Letter`
- Có seed bảng giá AI
- Có seed gói `FREE`, `PRO_MONTHLY`, `PRO_YEARLY`
- Có cấu hình MoMo sandbox hợp lệ

## 4. Test case

### TC_PAY_001 - Xem thông tin ví AI

- Màn hình: `Ví AI`
- Bước test:
  1. Đăng nhập bằng tài khoản ứng viên
  2. Mở trang `Ví AI`
- Kết quả mong đợi:
  - Hiển thị `Số dư hiện tại`
  - Hiển thị `Đang tạm giữ`
  - Hiển thị `Khả dụng để dùng AI`
  - Hiển thị `Lịch sử biến động ví`
  - Hiển thị block `Hạn mức AI hiện tại`

### TC_PAY_002 - Xem hạn mức AI hiện tại

- Màn hình: `Ví AI`
- Bước test:
  1. Mở block `Hạn mức AI hiện tại`
- Kết quả mong đợi:
  - Có các card cho:
    - `Sinh thư xin việc AI`
    - `Sinh báo cáo định hướng nghề nghiệp`
    - `Chatbot tư vấn nghề nghiệp`
    - `Phiên mock interview`
  - Mỗi card hiển thị:
    - `Miễn phí còn`
    - `Pro còn`
    - `Giá ví`

### TC_PAY_003 - Tạo giao dịch nạp ví qua MoMo

- Màn hình: `Ví AI`
- Bước test:
  1. Chọn mệnh giá nhanh hoặc nhập số tiền hợp lệ
  2. Bấm `Tạo giao dịch MoMo`
- Kết quả mong đợi:
  - Không hiện toast “đã tạo giao dịch”
  - Redirect thẳng cùng tab sang cổng thanh toán MoMo

### TC_PAY_004 - Nạp ví thành công qua MoMo

- Màn hình: `Ví AI`
- Bước test:
  1. Thực hiện thanh toán thành công trên MoMo
  2. Chờ hệ thống quay về FE
- Kết quả mong đợi:
  - Redirect về `/wallet`
  - Hiện toast `Nạp tiền thành công`
  - Số dư ví tăng đúng
  - Lịch sử ví xuất hiện giao dịch nạp tiền

### TC_PAY_005 - Nạp ví với số tiền nhỏ hơn mức tối thiểu

- Màn hình: `Ví AI`
- Bước test:
  1. Nhập số tiền nhỏ hơn `MOMO_MIN_AMOUNT`
  2. Bấm tạo giao dịch
- Kết quả mong đợi:
  - Không tạo giao dịch
  - Hiển thị thông báo validate phù hợp

### TC_PAY_006 - Xem danh sách gói Pro

- Màn hình: `Gói Pro`
- Bước test:
  1. Mở trang `Gói Pro`
- Kết quả mong đợi:
  - Hiển thị card `Current Plan`
  - Hiển thị card `Quota hiện tại`
  - Hiển thị gói `Gói Pro Tháng`
  - Hiển thị gói `Gói Pro Năm`

### TC_PAY_007 - Mua gói Pro qua MoMo

- Màn hình: `Gói Pro`
- Bước test:
  1. Bấm mua một gói Pro
  2. Thanh toán thành công qua MoMo
- Kết quả mong đợi:
  - Redirect sang MoMo
  - Sau thành công quay về `/plans`
  - Hiện toast kích hoạt thành công
  - Card `Current Plan` cập nhật đúng gói
  - Badge `Đang dùng` hiển thị ở đúng card

### TC_PAY_008 - Xem quota hiện tại của Pro

- Màn hình: `Gói Pro`
- Bước test:
  1. Mở card `Quota hiện tại`
- Kết quả mong đợi:
  - Hiển thị quota từng feature
  - Hiển thị đúng số lượt còn lại theo entitlement API

### TC_PAY_009 - Sinh Career Report khi còn quota Pro

- Màn hình: `Career Report`
- Bước test:
  1. Đăng nhập bằng tài khoản đang có Pro
  2. Chọn hồ sơ
  3. Quan sát nút CTA rồi bấm sinh báo cáo
- Kết quả mong đợi:
  - Nút không hiện giá tiền
  - Nút hiện dạng số lượt như `119/120`
  - Sau khi sinh thành công, quota Pro giảm 1 lượt
  - Ví không bị trừ tiền

### TC_PAY_010 - Sinh Career Report khi còn free quota nhưng không có Pro

- Màn hình: `Career Report`
- Bước test:
  1. Dùng tài khoản không có Pro nhưng còn free quota
  2. Chọn hồ sơ và quan sát CTA
  3. Bấm sinh báo cáo
- Kết quả mong đợi:
  - Nút hiện `Miễn phí x/y`
  - Sau khi sinh thành công, free quota giảm 1 lượt
  - Ví không bị trừ tiền

### TC_PAY_011 - Sinh Career Report khi hết Pro và free quota

- Màn hình: `Career Report`
- Bước test:
  1. Dùng tài khoản hết quota Pro và free
  2. Quan sát CTA
  3. Bấm sinh báo cáo
- Kết quả mong đợi:
  - Nút hiện giá ví
  - Sau khi sinh thành công, ví bị trừ đúng số tiền
  - Quota không tăng/giảm sai

### TC_PAY_012 - Sinh Cover Letter từ trang Chi tiết công việc khi còn quota Pro

- Màn hình: `Chi tiết công việc`
- Bước test:
  1. Mở modal ứng tuyển
  2. Quan sát nút `Sinh thư AI`
  3. Bấm sinh thư
- Kết quả mong đợi:
  - Nút hiện dạng `299/300`, không hiện giá tiền
  - Sau khi sinh thành công, quota Pro giảm 1 lượt
  - Ví không bị trừ tiền

### TC_PAY_013 - Sinh Cover Letter khi còn free quota

- Màn hình: `Chi tiết công việc`
- Bước test:
  1. Dùng tài khoản không có Pro nhưng còn free quota
  2. Mở modal ứng tuyển
  3. Bấm sinh thư
- Kết quả mong đợi:
  - Nút hiện `Miễn phí x/y`
  - Sinh thư thành công
  - Free quota giảm 1 lượt

### TC_PAY_014 - Sinh Cover Letter khi hết quota và dùng ví

- Màn hình: `Chi tiết công việc`
- Bước test:
  1. Dùng tài khoản hết Pro và free quota
  2. Mở modal ứng tuyển
  3. Bấm sinh thư
- Kết quả mong đợi:
  - Nút hiện giá tiền
  - Sinh thư thành công
  - Ví giảm đúng đơn giá

### TC_PAY_015 - Sinh Cover Letter từ trang Việc đã lưu

- Màn hình: `Việc đã lưu`
- Bước test:
  1. Mở modal ứng tuyển từ một job đã lưu
  2. Test lần lượt 3 trạng thái:
    - còn Pro
    - còn free
    - dùng ví
- Kết quả mong đợi:
  - CTA đổi đúng theo entitlement
  - Hành vi trừ quota / trừ ví đúng như `Chi tiết công việc`

### TC_PAY_016 - Gửi tin nhắn Chatbot khi còn quota Pro

- Màn hình: `AI Center / Chatbot`
- Bước test:
  1. Dùng tài khoản có Pro
  2. Gửi một tin nhắn hợp lệ
- Kết quả mong đợi:
  - Tin nhắn gửi thành công
  - Quota Pro của `chatbot_message` giảm đúng 1 lượt
  - Ví không bị trừ

### TC_PAY_017 - Gửi tin nhắn Chatbot khi còn free quota

- Màn hình: `AI Center / Chatbot`
- Bước test:
  1. Dùng tài khoản không có Pro nhưng còn free quota
  2. Gửi một tin nhắn
- Kết quả mong đợi:
  - Tin nhắn gửi thành công
  - Free quota giảm đúng 1 lượt

### TC_PAY_018 - Gửi tin nhắn Chatbot khi dùng ví

- Màn hình: `AI Center / Chatbot`
- Bước test:
  1. Dùng tài khoản đã hết Pro và free quota
  2. Gửi một tin nhắn
- Kết quả mong đợi:
  - Tin nhắn gửi thành công
  - Ví bị trừ đúng đơn giá theo `message`

### TC_PAY_019 - Tạo phiên Mock Interview khi còn quota Pro

- Màn hình: `AI Center / Mock Interview`
- Bước test:
  1. Dùng tài khoản có Pro
  2. Tạo phiên mock mới
- Kết quả mong đợi:
  - Tạo phiên thành công
  - Quota Pro của `mock_interview_session` giảm 1 lượt
  - Ví không bị trừ

### TC_PAY_020 - Tạo phiên Mock Interview khi còn free quota

- Màn hình: `AI Center / Mock Interview`
- Bước test:
  1. Dùng tài khoản không có Pro nhưng còn free quota
  2. Tạo phiên mock
- Kết quả mong đợi:
  - Tạo phiên thành công
  - Free quota giảm 1 lượt

### TC_PAY_021 - Tạo phiên Mock Interview khi dùng ví

- Màn hình: `AI Center / Mock Interview`
- Bước test:
  1. Dùng tài khoản hết Pro và free
  2. Tạo phiên mock
- Kết quả mong đợi:
  - Tạo phiên thành công
  - Ví giảm đúng đơn giá theo `session`

### TC_PAY_022 - Số dư ví không đủ

- Màn hình: `Career Report`, `Cover Letter`, `Chatbot`, `Mock Interview`
- Bước test:
  1. Dùng tài khoản hết quota và số dư ví không đủ
  2. Thực hiện action AI
- Kết quả mong đợi:
  - Request bị chặn
  - Hiện thông báo nạp thêm ví
  - Không tạo usage sai

### TC_PAY_023 - Duplicate request billing

- Màn hình: `Career Report` hoặc `Cover Letter`
- Bước test:
  1. Bấm liên tục trong lúc request trước chưa xong
- Kết quả mong đợi:
  - Không bị trừ nhiều lần
  - Hiển thị thông báo request trước vẫn đang xử lý

### TC_PAY_024 - Lịch sử ví phản ánh đúng loại giao dịch

- Màn hình: `Ví AI`
- Bước test:
  1. Nạp ví
  2. Dùng `Career Report`
  3. Dùng `Cover Letter`
- Kết quả mong đợi:
  - Lịch sử có các dòng phù hợp:
    - nạp ví
    - tạm giữ
    - khấu trừ
    - hoàn tạm giữ nếu có lỗi

### TC_PAY_025 - Kiểm tra API entitlement

- Màn hình: không yêu cầu UI
- API: `GET /api/v1/ung-vien/billing/entitlements`
- Bước test:
  1. Gọi API bằng tài khoản ứng viên
- Kết quả mong đợi:
  - Trả đúng:
    - `feature_code`
    - `free_quota_total`
    - `free_quota_used`
    - `free_quota_remaining`
    - `subscription_quota_total`
    - `subscription_quota_used`
    - `subscription_quota_remaining`
    - `wallet_price`

## 5. Checklist regression nhanh

- [ ] Nạp ví thành công
- [ ] Mua gói Pro thành công
- [ ] CTA `Career Report` đúng theo entitlement
- [ ] CTA `Cover Letter` đúng theo entitlement
- [ ] CTA `Cover Letter` ở `Việc đã lưu` đúng theo entitlement
- [ ] Chatbot trừ đúng quota/ví
- [ ] Mock Interview trừ đúng quota/ví
- [ ] `Ví AI` hiển thị quota đúng
- [ ] `Gói Pro` hiển thị `Current Plan` và `Quota hiện tại` đúng

## 6. Kết quả rà soát hiện tại

Ngày rà soát: `2026-04-27`

### Các test case đã có backend automated test

- `TC_PAY_003`, `TC_PAY_004`, `TC_PAY_005`:
  - `tests/Feature/WalletTopUpFeatureTest.php`
- `TC_PAY_006`, `TC_PAY_007`, `TC_PAY_008`:
  - `tests/Feature/SubscriptionPurchaseFeatureTest.php`
  - `tests/Feature/BillingEntitlementFeatureTest.php`
- `TC_PAY_009`, `TC_PAY_010`, `TC_PAY_011`:
  - `tests/Feature/FeatureAccessBillingTest.php`
  - `tests/Feature/AiFeatureWalletBillingFeatureTest.php`
- `TC_PAY_012`, `TC_PAY_013`, `TC_PAY_014`, `TC_PAY_015`:
  - `tests/Feature/AiFeatureWalletBillingFeatureTest.php`
- `TC_PAY_016`, `TC_PAY_017`, `TC_PAY_018`:
  - `tests/Feature/FeatureAccessBillingTest.php`
- `TC_PAY_019`, `TC_PAY_020`, `TC_PAY_021`:
  - `tests/Feature/FeatureAccessBillingTest.php`
- `TC_PAY_022`, `TC_PAY_023`:
  - `tests/Feature/FeatureAccessBillingTest.php`
- `TC_PAY_024`:
  - `tests/Feature/WalletTopUpFeatureTest.php`
  - `tests/Feature/AiFeatureWalletBillingFeatureTest.php`
- `TC_PAY_025`:
  - `tests/Feature/BillingEntitlementFeatureTest.php`
- Luồng mới ngoài checklist cũ:
  - API danh sách và chi tiết thanh toán người dùng:
    - `tests/Feature/WalletPaymentsFeatureTest.php`
  - API tổng quan billing admin:
    - `tests/Feature/AdminBillingOverviewFeatureTest.php`
  - Event billing + reconcile pending payment:
    - `tests/Feature/BillingScaleFeatureTest.php`

### Các test case vẫn cần manual UI/regression

- `TC_PAY_001`, `TC_PAY_002`:
  - Chủ yếu là kiểm tra render FE của `Ví AI` và block entitlement.
- `TC_PAY_006`, `TC_PAY_008`:
  - Backend đã có test, nhưng vẫn nên click-through FE để xác nhận card `Current Plan`, `Quota hiện tại`.
- `TC_PAY_009` đến `TC_PAY_021`:
  - Backend billing đã có test, nhưng phần copy CTA và toast trên FE vẫn cần smoke test thủ công.
- `TC_PAY_024`:
  - Nên kiểm tra thêm màn `Lịch sử thanh toán` và deep link notification tới `/payments/{ma_giao_dich_noi_bo}`.

### Kết luận rà soát

- Backend coverage cho các luồng billing chính hiện đã có:
  - top-up MoMo
  - mua gói Pro
  - entitlement API
  - AI billing theo `Pro -> Free -> Wallet`
  - insufficient wallet
  - duplicate/idempotent request
  - payment history API cho user
  - billing overview API cho admin
  - billing event dispatch và reconcile pending payment
- Bộ test case trong file này nên tiếp tục được dùng như checklist manual cho FE và smoke test end-to-end.

## 7. Ghi chú

- Nếu test trên `127.0.0.1`, luồng MoMo đang có nhánh local để auto-complete sau `return success`
- Nếu test với hạ tầng public thật, cần kiểm tra thêm `IPN`
- Với `Cover Letter`, nếu user đã nộp vào job đó rồi thì backend sẽ chặn sinh thư mới và FE sẽ redirect sang `Việc đã ứng tuyển`
