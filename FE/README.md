# SmartJob AI Frontend

Frontend của SmartJob AI là SPA viết bằng Vue 3 và Vite. Ứng dụng phục vụ 4 nhóm luồng chính: khách vãng lai, ứng viên, nhà tuyển dụng và quản trị viên.

## Công Nghệ

- Vue 3
- Vue Router 4
- Vite 7
- Tailwind CSS 4
- Laravel Echo + Pusher JS cho realtime notification
- vue-toastification cho thông báo UI

## Cấu Trúc Chính

```text
FE/
├── src/router/index.js              # route, layout, guard theo vai trò
├── src/services/api.js              # API client tập trung
├── src/services/realtime.js         # Laravel Echo/Reverb
├── src/components/Guest             # public pages
├── src/components/Dashboard         # ứng viên
├── src/components/Employer          # nhà tuyển dụng
├── src/components/Admin             # quản trị viên
├── src/layouts                      # guest/auth/candidate/employer/admin layouts
├── src/composables                  # auth, notification, permission helpers
└── scripts/smoke-test.mjs           # kiểm tra wiring frontend quan trọng
```

## Cài Đặt Local

```bash
npm install
cp .env.example .env
```

File `.env` tối thiểu:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
VITE_REVERB_APP_KEY=kltn-local-key
VITE_REVERB_HOST=127.0.0.1
VITE_REVERB_PORT=8080
VITE_REVERB_SCHEME=http
```

Không commit file `.env` thật.

## Chạy Frontend

```bash
npm run dev
```

Mặc định Vite chạy tại:

```text
http://localhost:5173
```

## Build Và Kiểm Tra

```bash
npm run build
npm run test:smoke
```

Smoke test kiểm tra các wiring quan trọng như AI Center, saved jobs/re-engagement, offer/onboarding, interview round, export PDF và notification deeplink.

## Các Khu Vực Giao Diện

- Guest: landing, đăng nhập/đăng ký, tìm việc, công ty, ngành nghề, kỹ năng.
- Ứng viên: dashboard, hồ sơ, CV builder, kỹ năng, ứng tuyển, việc đã lưu, công ty theo dõi, matching, career report, AI Center, ví/gói dịch vụ.
- Nhà tuyển dụng: công ty, HR nội bộ, tin tuyển dụng, ứng viên, phỏng vấn, billing, audit log.
- Admin: users, admins, companies, profiles, jobs, applications, skills, industries, matching, career advising, CV templates, billing, AI usage, audit logs, stats.

## Tài Liệu Liên Quan

- `../README.md`: tổng quan toàn hệ thống.
- `../BE/docs/TAI_LIEU_TONG_QUAN_HE_THONG_VA_KICH_BAN_DEMO.md`: tài liệu demo bảo vệ.
- `SETUP_GUIDE.md`: hướng dẫn setup frontend nếu cần chi tiết hơn.
