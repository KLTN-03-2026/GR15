# Hướng dẫn Setup - Quản lý Người Dùng Admin

## 📋 Tổng quan
Giao diện quản lý người dùng admin cho hệ thống AI Recruitment & Career Consulting.

**URL:** `/admin/users`
**API Domain:** `http://127.0.0.1:8000/api/v1`

---

## 🔧 Cấu hình

### 1. File Environment (`.env`)
```
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

**Cách thay đổi domain:**
- Mở file `.env` trong thư mục root
- Chỉnh sửa giá trị `VITE_API_BASE_URL`
- Ứng dụng sẽ tự động sử dụng domain mới

### 2. API Service (`src/services/api.js`)
Chứa các hàm gọi API:
- Authentication (đăng nhập, đăng xuất)
- User Management (CRUD người dùng)

**Import trong component:**
```javascript
import { userService, authService } from '@/services/api'
```

---

## 📱 Tính năng Giao Diện

### Thống kê (Stats)
- **Tổng người dùng** - Số lượng tất cả người dùng
- **Ứng viên** - Số lượng ứng viên (vai_tro = 0)
- **Nhà tuyển dụng** - Số lượng nhà tuyển dụng (vai_tro = 1)
- **Đơi phê duyệt** - Tài khoản chuyên người dùng đang đợi xử lý

### Tìm kiếm & Lọc
- 🔍 **Tìm kiếm** - Theo tên, email, địa chỉ
- **Lọc vai trò** - Ứng viên, Nhà tuyển dụng, Admin
- **Lọc trạng thái** - Hoạt động, Đã khóa

### Hành động
- ✏️ **Chỉnh sửa** - Cập nhật thông tin người dùng
- 🔒 **Khóa/Mở khóa** - Toggle trạng thái tài khoản
- 🗑️ **Xóa** - Xóa người dùng khỏi hệ thống
- ➕ **Tạo mới** - Thêm người dùng mới

### Phân trang
- Hiển thị 10 người dùng mỗi trang
- Điều hướng giữa các trang

---

## 🔌 API Endpoints được sử dụng

### Danh sách người dùng
```
GET /admin/users?page=1&per_page=10&vai_tro=0&is_active=true&search=text
```

### Thống kê
```
GET /admin/users/stats
```

### Chi tiết người dùng
```
GET /admin/users/:id
```

### Tạo người dùng
```
POST /admin/users
```

### Cập nhật người dùng
```
PUT /admin/users/:id
```

### Khóa/Mở khóa tài khoản
```
PATCH /admin/users/:id
```

### Xóa người dùng
```
DELETE /admin/users/:id
```

---

## 🔐 Authentication

Token được lưu tự động vào `localStorage` khi đăng nhập.

**API Service tự động:**
- Gửi `Authorization: Bearer {token}` với mỗi request
- Lấy token từ localStorage nếu tồn tại

---

## 🎨 Styling

Dự án sử dụng **Tailwind CSS v4.2.1**

### Màu chính
- Xanh dương: `#2463eb`
- Emerald (thành công): `emerald-600`
- Amber (cảnh báo): `amber-600`
- Red (lỗi): `red-600`

---

## 📝 Cấu trúc Data Model

### User Object
```javascript
{
  id: number,
  ho_ten: string,              // Họ tên
  email: string,
  so_dien_thoai: string,       // Điện thoại
  ngay_sinh: string,           // Ngày sinh (YYYY-MM-DD)
  gioi_tinh: string,           // nam/nu/khac
  dia_chi: string,             // Địa chỉ
  vai_tro: number,             // 0=ứng viên, 1=NTD, 2=Admin
  is_active: boolean,          // Trạng thái tài khoản
  created_at: string,          // ISO datetime
  updated_at: string           // ISO datetime
}
```

---

## ⚠️ Lưu ý quan trọng

1. **Xóa tài khoản** - Không thể khôi phục, hãy cẩn thận
2. **Khóa tài khoản** - Tài khoản bị khóa không thể đăng nhập
3. **Domain thay đổi** - Chỉ cần chỉnh sửa file `.env`
4. **Token hết hạn** - Khi đó sẽ cần đăng nhập lại

---

## 🚀 Khởi động ứng dụng

```bash
npm install
npm run dev
```

Ứng dụng chạy tại: `http://localhost:5173`

---

## 📚 File quan trọng

```
KLTN_FE/
├── .env                                      (Cấu hình domain)
├── src/
│   ├── services/
│   │   └── api.js                            (API service)
│   └── components/
│       └── Admin/
│           └── UserManagementPage.vue        (Giao diện chính)
```

---

## 💡 Mở rộng

Để thêm API mới:

1. Thêm function vào `userService` trong `src/services/api.js`
2. Import và sử dụng trong component

Ví dụ:
```javascript
// Trong src/services/api.js
userService.newFunction = (data) =>
  apiCall('/endpoint', {
    method: 'POST',
    body: JSON.stringify(data)
  })
```

---

Được tạo: 2024
