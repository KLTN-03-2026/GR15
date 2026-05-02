# Danh sách task chức năng thanh toán

## 1. Ví AI và ledger

- [x] Tạo bảng `vi_nguoi_dungs`
- [x] Tạo bảng `bien_dong_vi`
- [x] Tạo service xử lý `reserve / commit / release`
- [x] Tạo API lấy số dư ví và lịch sử biến động
- [x] Tạo giao diện `Ví AI`
- [x] Hiển thị số dư khả dụng, đang tạm giữ và lịch sử ví

## 2. Bảng giá AI

- [x] Tạo bảng `bang_gia_tinh_nang_ai`
- [x] Seed đơn giá cho:
  - `cover_letter_generation`
  - `career_report_generation`
  - `chatbot_message`
  - `mock_interview_session`
- [x] Tạo API lấy bảng giá

## 3. MoMo nạp ví

- [x] Tạo service tạo giao dịch MoMo
- [x] Tạo bảng `giao_dich_thanh_toans`
- [x] Tạo endpoint nạp ví qua MoMo
- [x] Redirect thẳng sang `payUrl`
- [x] Redirect quay về `/wallet` sau thanh toán thành công ở local
- [x] Auto complete payment khi chạy local `127.0.0.1`
- [x] Tách webhook handler riêng

## 4. Pay-per-use

- [x] Tạo bảng `su_dung_tinh_nang_ais`
- [x] Tạo flow billing theo lượt dùng
- [x] Áp dụng cho `Cover Letter`
- [x] Áp dụng cho `Career Report`
- [x] Áp dụng cho `Chatbot`
- [x] Áp dụng cho `Mock Interview`

## 5. Free quota

- [x] Tạo rule free quota theo từng feature trong config
- [x] Tạo logic dùng free quota trước khi fallback lớp khác
- [x] Trả dữ liệu free quota qua API entitlement
- [x] Hiển thị free quota trên FE

## 6. Gói Pro

- [x] Tạo bảng `goi_dich_vus`
- [x] Tạo bảng `goi_dich_vu_tinh_nangs`
- [x] Tạo bảng `nguoi_dung_goi_dich_vus`
- [x] Seed `FREE`, `PRO_MONTHLY`, `PRO_YEARLY`
- [x] Tạo `SubscriptionService`
- [x] Tạo API lấy gói hiện tại và danh sách gói
- [x] Tạo giao diện `Gói Pro`
- [x] Hiển thị `Current Plan`
- [x] Hiển thị `Quota hiện tại`
- [x] Mua gói Pro qua MoMo

## 7. Entitlement và access control

- [x] Tạo `FeatureAccessService`
- [x] Tạo `BillingEntitlementService`
- [x] Tạo endpoint `billing/entitlements`
- [x] FE đọc entitlement để đổi CTA theo:
  - `Pro quota`
  - `Free quota`
  - `Wallet price`

## 8. FE đồng bộ billing

- [x] Trang `Ví AI` hiển thị quota từng tính năng
- [x] Trang `Gói Pro` hiển thị quota hiện tại
- [x] `Career Report` đổi nút theo entitlement
- [x] `Cover Letter` đổi nút theo entitlement
- [x] `AI Center` hiển thị đơn giá `Chatbot` và `Mock Interview`
- [x] Thanh toán thành công quay về đúng màn hình FE

## 9. Test và vận hành

- [x] Test top-up wallet
- [x] Test mua gói Pro
- [x] Test entitlement API
- [x] Test billing AI features
- [x] Thêm command reconcile giao dịch pending
- [x] Schedule reconcile định kỳ

## 10. Task nên làm tiếp

- [x] Thêm admin dashboard cho doanh thu, top-up, subscription
- [x] Thêm màn hình chi tiết giao dịch thanh toán cho người dùng
- [x] Bổ sung queue/listener cho event billing
- [x] Chuẩn hóa copy UI cho tất cả CTA AI theo entitlement
- [x] Kiểm tra lại toàn bộ test case trong `test_case_chuc_nang_thanh_toan.md`
- [x] Viết tài liệu triển khai production cho MoMo và Reverb
- [ ] Khi có môi trường public, thêm log/monitoring riêng cho webhook/IPN lỗi
- [ ] Khi có môi trường public, thêm cơ chế retry/replay cho webhook MoMo để xử lý lỗi callback an toàn

## 11. Lưu ý hiện tại

- Thứ tự đang áp dụng trong code: `Pro -> Free -> Wallet`
- `quota còn lại` không lưu trực tiếp trong một bảng riêng
- `free quota total` lấy từ config
- `subscription quota total` lấy từ `goi_dich_vu_tinh_nangs`
- `quota used` được đếm từ `su_dung_tinh_nang_ais`
- Local đang có nhánh đặc biệt cho MoMo return success để demo trên `127.0.0.1`
