# Tài liệu triển khai production cho MoMo và Reverb

## 1. Mục tiêu

Tài liệu này dùng để triển khai production cho:

- Thanh toán MoMo cho `nạp ví` và `mua gói Pro`
- Reverb cho realtime notification và broadcast event

Phạm vi tài liệu bám theo code hiện tại trong:

- `config/services.php`
- `config/broadcasting.php`
- `config/reverb.php`
- `routes/api.php`
- `routes/channels.php`
- `FE/src/services/realtime.js`

## 2. Kiến trúc production tối thiểu

- Backend Laravel chạy HTTPS công khai, ví dụ `https://api.example.com`
- Frontend chạy HTTPS công khai, ví dụ `https://app.example.com`
- Queue worker chạy nền vì notification billing đang dùng queue after commit
- Scheduler chạy định kỳ vì có command `billing:reconcile-pending-payments`
- Reverb chạy như một process riêng phía backend
- Reverse proxy public WebSocket qua `Nginx` hoặc `Apache`
- MoMo cấu hình `redirect_url` và `ipn_url` trỏ đúng domain public

## 3. Checklist trước khi mở production

- Đã có domain HTTPS public cho backend và frontend
- Đã cấp credential production thật từ MoMo
- Đã bật queue production, không dùng xử lý thủ công
- Đã có Redis nếu muốn scale Reverb nhiều instance
- Đã chốt firewall cho cổng Reverb nội bộ
- Đã xác nhận `broadcasting/auth` truy cập được từ frontend đã đăng nhập

## 4. Biến môi trường backend bắt buộc

### App và queue

```env
APP_ENV=production
APP_DEBUG=false
APP_URL=https://api.example.com
FRONTEND_URL=https://app.example.com

LOG_CHANNEL=stack
LOG_LEVEL=info

QUEUE_CONNECTION=database
BROADCAST_CONNECTION=reverb
```

Nếu production dùng Redis queue thì đổi:

```env
QUEUE_CONNECTION=redis
```

### MoMo production

```env
MOMO_BASE_URL=https://payment.momo.vn
MOMO_PARTNER_CODE=your-production-partner-code
MOMO_PARTNER_NAME=YourBrand
MOMO_STORE_ID=your-production-store-id
MOMO_ACCESS_KEY=your-production-access-key
MOMO_SECRET_KEY=your-production-secret-key
MOMO_REQUEST_TYPE=captureWallet
MOMO_LANG=vi
MOMO_TIMEOUT=30
MOMO_REDIRECT_URL=https://api.example.com/api/v1/payments/momo/return
MOMO_IPN_URL=https://api.example.com/api/v1/payments/momo/ipn
MOMO_MIN_AMOUNT=1000
MOMO_AUTO_COMPLETE_RETURN_LOCAL=false
```

Lưu ý:

- Production phải để `MOMO_AUTO_COMPLETE_RETURN_LOCAL=false`
- `MOMO_REDIRECT_URL` và `MOMO_IPN_URL` phải là URL public HTTPS thật
- Không dùng domain `localhost`, `127.0.0.1`, `ngrok` tạm trong production

### Reverb production

```env
REVERB_APP_ID=your-reverb-app-id
REVERB_APP_KEY=your-reverb-app-key
REVERB_APP_SECRET=your-reverb-app-secret

REVERB_HOST=ws.example.com
REVERB_PORT=443
REVERB_SCHEME=https

REVERB_SERVER_HOST=127.0.0.1
REVERB_SERVER_PORT=8080
REVERB_SERVER_PATH=
```

Nếu scale nhiều instance Reverb:

```env
REVERB_SCALING_ENABLED=true
REVERB_SCALING_CHANNEL=reverb
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
```

## 5. Biến môi trường frontend cho Reverb

Trong frontend, file env production cần có:

```env
VITE_API_BASE_URL=https://api.example.com/api/v1
VITE_REVERB_APP_KEY=your-reverb-app-key
VITE_REVERB_HOST=ws.example.com
VITE_REVERB_PORT=443
VITE_REVERB_SCHEME=https
```

Lưu ý:

- `VITE_REVERB_APP_KEY` phải khớp `REVERB_APP_KEY` của backend
- `VITE_REVERB_HOST` là host public mà browser sẽ kết nối WebSocket
- Nếu frontend và backend khác subdomain, cần kiểm tra CORS, Sanctum, cookie/session auth cho `broadcasting/auth`

## 6. Command triển khai backend

Sau khi cập nhật env production:

```bash
composer install --no-dev --optimize-autoloader
php artisan migrate --force
php artisan config:cache
php artisan route:cache
php artisan event:cache
php artisan view:cache
```

Nếu dùng frontend build trên server:

```bash
cd FE
npm ci
npm run build
```

## 7. Process nền bắt buộc

### Queue worker

Vì listener billing hiện dùng `ShouldQueueAfterCommit`, production bắt buộc phải chạy worker:

```bash
php artisan queue:work --tries=3 --timeout=120
```

### Scheduler

Command reconcile pending payment đang được schedule, nên cần cron:

```cron
* * * * * cd /var/www/khanhmai/BE && php artisan schedule:run >> /dev/null 2>&1
```

### Reverb server

Chạy process WebSocket riêng:

```bash
php artisan reverb:start --host=127.0.0.1 --port=8080
```

## 8. Reverse proxy cho Reverb

Ví dụ `Nginx` cho `ws.example.com`:

```nginx
server {
    listen 443 ssl http2;
    server_name ws.example.com;

    ssl_certificate /etc/letsencrypt/live/ws.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ws.example.com/privkey.pem;

    location / {
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_read_timeout 60s;
        proxy_pass http://127.0.0.1:8080;
    }
}
```

Lưu ý:

- Browser sẽ kết nối tới `ws.example.com:443`
- Reverb server nội bộ vẫn có thể chạy tại `127.0.0.1:8080`
- Nếu dùng path riêng, cần đồng bộ `REVERB_SERVER_PATH` và proxy config

## 9. Cấu hình MoMo production

### Endpoint đang dùng trong code

- Tạo payment: `POST /v2/gateway/api/create` trên `MOMO_BASE_URL`
- Return URL backend:
  - `GET /api/v1/payments/momo/return`
- IPN backend:
  - `POST /api/v1/payments/momo/ipn`

### Quy tắc vận hành

- Luồng `return` chỉ dùng để redirect người dùng quay lại frontend
- Luồng `ipn` mới là callback server-to-server quan trọng nhất để chốt trạng thái thanh toán
- Production phải cho MoMo gọi được `ipn_url` từ internet
- Nên whitelist hoặc monitor request đến `ipn_url`

### Smoke test production cho MoMo

1. Tạo giao dịch nạp ví thật từ tài khoản test production.
2. Kiểm tra user được redirect sang MoMo thành công.
3. Thanh toán thành công.
4. Xác nhận backend nhận `IPN`.
5. Xác nhận `giao_dich_thanh_toans.trang_thai = success`.
6. Xác nhận ví hoặc subscription được cập nhật đúng.
7. Xác nhận notification billing được tạo qua queue.
8. Xác nhận frontend mở được `/payments/{ma_giao_dich_noi_bo}`.

## 10. Smoke test production cho Reverb

1. Đăng nhập frontend bằng tài khoản thật.
2. Mở browser console, bảo đảm không có lỗi kết nối `ws` hoặc `wss`.
3. Thực hiện action tạo notification hoặc event realtime.
4. Xác nhận frontend nhận được event mới mà không cần reload.
5. Xác nhận `POST /broadcasting/auth` trả về thành công cho private channel.

## 11. Rủi ro cần chặn trước khi go-live

- Không để `APP_DEBUG=true` trên production
- Không để credential local/sandbox tồn tại trong env production
- Không để `MOMO_AUTO_COMPLETE_RETURN_LOCAL=true`
- Không chạy billing listener mà không có queue worker
- Không expose trực tiếp cổng Reverb nội bộ ra internet nếu chưa có reverse proxy và TLS
- Không để `allowed_origins` quá rộng nếu hạ tầng đã chốt domain chính thức

## 12. Hậu kiểm sau triển khai

- Kiểm tra log application sau đợt thanh toán đầu tiên
- Kiểm tra bảng `jobs` và `failed_jobs`
- Kiểm tra command reconcile có chạy theo lịch
- Kiểm tra notification billing và deep link `/payments/...`
- Kiểm tra thống kê `/api/v1/admin/billing/overview`

## 13. Kết luận

Để production ổn định với code hiện tại, tối thiểu phải có:

- HTTPS public cho backend, frontend, WebSocket
- Queue worker đang chạy
- Scheduler đang chạy
- MoMo production credential đúng
- Reverb process + reverse proxy hoạt động
- Kiểm tra smoke test cho cả `top-up`, `subscription`, `notification`, `payments detail`
