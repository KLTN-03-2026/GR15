# Thiết Kế Chức Năng Trả Phí Cho Hệ Thống AI Tuyển Dụng

## 1. Mục tiêu
Chức năng trả phí được thiết kế để hỗ trợ việc thương mại hóa các dịch vụ AI trong hệ thống tuyển dụng, đồng thời vẫn giữ được trải nghiệm dùng thử cho người dùng mới. Hệ thống cần cho phép:

- Dùng thử miễn phí một số lượt đầu
- Trả phí theo lượt dùng khi hết quota miễn phí
- Nâng cấp tài khoản lên gói `Pro`
- Mở rộng tiếp lên `Enterprise` khi hệ thống scale

Thiết kế này cần phù hợp với kiến trúc hiện tại của hệ thống, đồng thời đủ linh hoạt để tích hợp cổng thanh toán bên thứ ba như `VNPAY`, `MoMo` trong giai đoạn sau.

## 2. Các mô hình kinh doanh đề xuất

### 2.1. Free
Người dùng mới được cấp một số lượt miễn phí để trải nghiệm hệ thống.

Ví dụ:
- 1 lần tạo cover letter
- 1 lần tạo career report
- 20 tin nhắn chatbot
- 1 phiên mock interview

### 2.2. Pay-per-use
Sau khi hết lượt miễn phí, người dùng có thể trả phí theo từng lần sử dụng.

Ví dụ:
- mỗi lần tạo cover letter: X VNĐ
- mỗi 10 tin nhắn chatbot: Y VNĐ
- mỗi phiên mock interview: Z VNĐ

### 2.3. Pro
Người dùng trả phí theo chu kỳ tháng hoặc năm và được cấp quota lớn hơn hoặc gần như không giới hạn cho một số tính năng.

Ví dụ:
- 50 cover letters/tháng
- 200 chatbot messages/tháng
- 10 mock interviews/tháng

### 2.4. Enterprise
Giai đoạn scale sau này có thể mở rộng thêm gói doanh nghiệp:
- nhiều người dùng trong một tổ chức
- quota riêng
- hợp đồng riêng
- xuất hóa đơn

## 3. Những tính năng nên tính phí
Không nên thu phí mọi thứ. Nên tập trung vào các tính năng AI có giá trị cao hoặc tốn chi phí model:

- `cover_letter_generation`
- `career_report_generation`
- `chatbot_message`
- `mock_interview_session`

Các tính năng nên cân nhắc giữ miễn phí hoặc quota cao:
- CV Parser
- JD Parser
- matching cơ bản

Lý do:
- đây là chức năng lõi giúp người dùng thấy giá trị hệ thống
- nếu khóa quá sớm sẽ giảm chuyển đổi

## 4. Kiến trúc tổng thể

### 4.1. Thành phần chính
- `FeatureAccessService`
- `SubscriptionService`
- `UsageTrackingService`
- `BillingService`
- `PaymentGatewayService`
- `WebhookHandlerService`

### 4.2. Nguyên tắc thiết kế
Logic trả phí không nên nhúng trực tiếp trong controller AI. Thay vào đó:

1. Controller gọi lớp kiểm tra quyền dùng tính năng
2. Nếu hợp lệ mới cho gọi AI
3. Nếu thành công mới ghi usage hoàn tất
4. Nếu thất bại thì không trừ lượt hoặc rollback usage

Điều này giúp:
- dễ bảo trì
- dễ test
- dễ thay đổi chính sách billing
- tránh trừ tiền sai khi AI lỗi

## 5. Luồng nghiệp vụ chuẩn

### 5.1. Khi người dùng sử dụng một tính năng AI
Ví dụ với `Cover Letter Generator`:

1. FE gọi API tạo cover letter.
2. BE gọi `FeatureAccessService` để kiểm tra:
   - user còn quota free không
   - user có gói Pro đang hoạt động không
   - nếu không có Pro thì user có đủ số dư hoặc quyền pay-per-use không
3. Nếu không hợp lệ:
   - trả về thông báo yêu cầu nâng cấp hoặc thanh toán
4. Nếu hợp lệ:
   - tạo usage record ở trạng thái `pending`
   - gọi AI service
5. Nếu AI thành công:
   - update usage thành `success`
   - trừ quota hoặc ghi nhận chi phí
6. Nếu AI thất bại:
   - usage chuyển `failed`
   - không trừ lượt hoặc hoàn trả usage

### 5.2. Luồng người dùng nâng cấp gói
1. FE hiển thị gói dịch vụ.
2. User chọn gói.
3. BE tạo `payment intent`.
4. BE gọi gateway thanh toán để lấy URL.
5. FE redirect sang cổng thanh toán.
6. Gateway trả kết quả hoặc gọi webhook.
7. BE xác minh giao dịch.
8. BE kích hoạt gói tương ứng cho user.

## 6. Thiết kế cơ sở dữ liệu

### 6.1. `goi_dich_vus`
Lưu thông tin các gói dịch vụ.

Đề xuất cột:
- `id`
- `ma_goi`
- `ten_goi`
- `mo_ta`
- `gia`
- `chu_ky`
- `trang_thai`
- `created_at`
- `updated_at`

Ví dụ:
- `FREE`
- `PRO_MONTHLY`
- `PRO_YEARLY`

### 6.2. `goi_dich_vu_tinh_nangs`
Map gói dịch vụ với từng tính năng và quota.

Đề xuất cột:
- `id`
- `goi_dich_vu_id`
- `feature_code`
- `quota`
- `reset_cycle`
- `is_unlimited`
- `created_at`
- `updated_at`

Ví dụ:
- `feature_code = chatbot_message`
- `quota = 200`
- `reset_cycle = monthly`

### 6.3. `nguoi_dung_goi_dich_vus`
Lưu gói mà user đang dùng.

Đề xuất cột:
- `id`
- `nguoi_dung_id`
- `goi_dich_vu_id`
- `ngay_bat_dau`
- `ngay_het_han`
- `trang_thai`
- `auto_renew`
- `created_at`
- `updated_at`

### 6.4. `dich_vu_ai_gias`
Lưu bảng giá pay-per-use cho từng tính năng.

Đề xuất cột:
- `id`
- `feature_code`
- `ten_hien_thi`
- `don_gia`
- `don_vi_tinh`
- `trang_thai`
- `created_at`
- `updated_at`

Ví dụ:
- `cover_letter_generation`
- `chatbot_message`
- `mock_interview_session`

### 6.5. `lich_su_su_dung_dich_vus`
Lưu mỗi lần người dùng sử dụng một tính năng AI.

Đề xuất cột:
- `id`
- `nguoi_dung_id`
- `feature_code`
- `so_luong`
- `mien_phi`
- `chi_phi`
- `trang_thai`
- `billing_mode`
- `tham_chieu_loai`
- `tham_chieu_id`
- `metadata_json`
- `created_at`
- `updated_at`

Ý nghĩa:
- `billing_mode`: `free`, `subscription`, `pay_per_use`
- `tham_chieu_loai`: ví dụ `ung_tuyen`, `ai_chat_session`
- `tham_chieu_id`: record liên quan

### 6.6. `giao_dich_thanh_toans`
Lưu lịch sử giao dịch thanh toán.

Đề xuất cột:
- `id`
- `nguoi_dung_id`
- `gateway`
- `ma_giao_dich_noi_bo`
- `ma_giao_dich_gateway`
- `loai_giao_dich`
- `so_tien`
- `noi_dung`
- `trang_thai`
- `raw_response_json`
- `created_at`
- `updated_at`

### 6.7. `vi_nguoi_dungs` và `bien_dong_vi` (nếu muốn mô hình nạp tiền)
Chỉ cần nếu hệ thống muốn cho người dùng nạp trước rồi trừ dần.

`vi_nguoi_dungs`:
- `nguoi_dung_id`
- `so_du`

`bien_dong_vi`:
- `vi_id`
- `so_tien_thay_doi`
- `loai_bien_dong`
- `tham_chieu_loai`
- `tham_chieu_id`

## 7. Các rule billing đề xuất

### 7.1. Rule theo feature
Ví dụ:

#### Cover letter
- free: 1 lượt
- pro: 50 lượt/tháng
- pay-per-use: 3.000 VNĐ/lượt

#### Career report
- free: 1 lượt
- pro: 20 lượt/tháng
- pay-per-use: 5.000 VNĐ/lượt

#### Chatbot
- free: 20 messages
- pro: 200 messages/tháng
- pay-per-use: 500 VNĐ/message hoặc 5.000 VNĐ/10 messages

#### Mock interview
- free: 1 phiên
- pro: 10 phiên/tháng
- pay-per-use: 10.000 VNĐ/phiên

### 7.2. Rule khi AI lỗi
Nếu AI service lỗi:
- không trừ quota
- không trừ tiền
- usage record đánh dấu `failed`

### 7.3. Rule idempotency
Mỗi hành động tính phí nên có:
- `request_id`
- hoặc `idempotency_key`

để tránh:
- người dùng bấm lại nhiều lần
- gateway callback trùng
- AI timeout rồi retry gây trừ tiền 2 lần

## 8. Tích hợp thanh toán bên thứ ba

### 8.1. Nguyên tắc chung
Không viết logic thanh toán trực tiếp trong controller. Nên có abstraction:

- `PaymentGatewayInterface`
- `VnpayGateway`
- `MomoGateway`

Như vậy:
- dễ thay cổng
- dễ test
- dễ mock khi demo

### 8.2. Luồng thanh toán chuẩn
1. FE gửi yêu cầu thanh toán.
2. BE tạo bản ghi `pending` trong `giao_dich_thanh_toans`.
3. BE gọi gateway để sinh URL thanh toán.
4. FE redirect user sang trang thanh toán.
5. User thanh toán trên VNPAY hoặc MoMo.
6. Gateway trả về `return_url` cho FE.
7. Đồng thời gateway gọi `IPN/Webhook` về BE.
8. BE xác minh chữ ký, số tiền, trạng thái.
9. Nếu hợp lệ:
   - cập nhật giao dịch thành `success`
   - kích hoạt gói hoặc cộng tiền vào ví
10. FE gọi API kiểm tra trạng thái cuối cùng.

## 9. Tích hợp VNPAY

### 9.1. Những gì cần có
- mã terminal / merchant
- secret key
- return URL
- IPN URL

### 9.2. Cách làm
- Backend build URL thanh toán VNPAY
- Redirect user sang URL đó
- Nhận dữ liệu callback
- Verify chữ ký bằng secret key
- Đối chiếu:
  - mã đơn
  - số tiền
  - trạng thái

### 9.3. Lưu ý
- không xác nhận thành công chỉ dựa trên `return_url`
- phải dùng `IPN` để chốt

## 10. Tích hợp MoMo

### 10.1. Những gì cần có
- partner code
- access key
- secret key
- return URL
- notify URL

### 10.2. Cách làm
- Backend tạo request tới MoMo
- nhận `payUrl`
- FE redirect user
- MoMo callback về hệ thống
- Backend verify signature
- cập nhật trạng thái giao dịch

### 10.3. Lưu ý
- luôn verify chữ ký
- không cập nhật trạng thái chỉ theo dữ liệu FE gửi lên

## 11. Hướng phát triển theo giai đoạn

### Giai đoạn 1: chuẩn bị kiến trúc
- thiết kế schema billing
- tạo service access control
- chưa cần cổng thanh toán thật

### Giai đoạn 2: Free + Pro
- triển khai quota free
- triển khai nâng cấp gói Pro
- có thể dùng mock payment hoặc admin kích hoạt thủ công

### Giai đoạn 3: Pay-per-use
- thêm bảng giá từng dịch vụ
- thêm usage tracking
- trừ phí theo lượt dùng

### Giai đoạn 4: tích hợp gateway thật
- VNPAY
- MoMo
- webhook/IPN
- xử lý idempotency

### Giai đoạn 5: scale
- tách billing module rõ ràng
- queue cho payment và usage
- event-driven cho:
  - `payment_succeeded`
  - `subscription_activated`
  - `ai_feature_used`

## 12. Hướng scale hệ thống
Khi hệ thống lớn hơn, phần billing nên được tách theo logic độc lập:

- `AI usage metering`
- `subscription management`
- `payment processing`

Các hướng mở rộng:
- queue để xử lý callback
- event bus để đồng bộ usage
- dashboard thống kê doanh thu
- phân tích churn / conversion
- quản lý coupon / trial campaign

## 13. Đề xuất phù hợp nhất với hệ thống hiện tại
Với hệ thống hiện tại, hướng thực tế nhất là:

### Giai đoạn đầu
- chỉ thiết kế schema và service
- triển khai `Free + Pro`
- khóa/mở tính năng theo quota
- chưa cần thanh toán thật ngay

### Giai đoạn sau
- thêm `Pay-per-use`
- tích hợp `VNPAY` hoặc `MoMo`
- thêm ví nội bộ nếu cần

Lý do:
- dễ triển khai
- dễ bảo vệ
- không làm hệ thống phình quá sớm
- vẫn có hướng mở rộng rõ ràng

## 14. Kết luận
Chức năng trả phí nên được thiết kế theo hướng:

- `subscription + quota + usage tracking + payment abstraction`
- kiểm tra quyền dùng trước khi gọi AI
- tách billing khỏi logic AI
- hỗ trợ cả `Free`, `Pay-per-use`, `Pro`
- sẵn sàng tích hợp `VNPAY`, `MoMo`

Đây là hướng phát triển phù hợp nhất vì:
- không phá kiến trúc hiện tại
- dễ mở rộng khi scale
- dễ chuyển từ mô hình demo sang mô hình thương mại hóa thật
