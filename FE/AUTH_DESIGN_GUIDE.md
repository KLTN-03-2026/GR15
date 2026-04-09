# Hướng dẫn Thiết kế Trang Đăng nhập & Đăng ký

## 📋 Tổng quan

Dự án này cung cấp trang đăng nhập/đăng ký cho hai loại người dùng:
- **Guest (Ứng viên - Job Seekers)**
- **Employer (Doanh nghiệp - Companies)**

---

## 🎨 Các Component Chính

### 1. **AuthPage.vue** (Guest/Candidate)
**Đường dẫn:** `/src/components/Guest/AuthPage.vue`

#### Tính năng:
- ✅ Đăng ký tài khoản với lựa chọn: Ứng viên hoặc Doanh nghiệp
- ✅ Đăng nhập với email/password
- ✅ Validation form toàn bộ
- ✅ Toggle hiệu lực mật khẩu
- ✅ Đăng nhập qua Google & Facebook (OAuth placeholder)
- ✅ Thông báo lỗi và thành công
- ✅ Trạng thái loading

#### Route:
```
GET /auth
```

#### Form Fields (Đăng ký):
- Họ tên (fullName)
- Email (email)
- Số điện thoại (phone)
- Mật khẩu (password)
- Loại tài khoản (candidate/employer)

#### Form Fields (Đăng nhập):
- Email (email)
- Mật khẩu (password)
- Ghi nhớ đăng nhập (rememberMe)

---

### 2. **EmployerAuthPage.vue** (Employer)
**Đường dẫn:** `/src/components/Employer/EmployerAuthPage.vue`

#### Tính năng:
- ✅ Đăng ký tài khoản doanh nghiệp
- ✅ Đăng nhập doanh nghiệp
- ✅ Validation form toàn bộ
- ✅ Toggle hiệu lực mật khẩu
- ✅ Đăng nhập qua Google & Facebook
- ✅ Thông báo lỗi và thành công
- ✅ Trạng thái loading

#### Route:
```
GET /employer/auth
```

#### Form Fields (Đăng ký):
- Tên công ty (companyName)
- Người liên hệ (contactPerson)
- Email công ty (email)
- Số điện thoại (phone)
- Mật khẩu (password)

#### Form Fields (Đăng nhập):
- Email (email)
- Mật khẩu (password)
- Ghi nhớ đăng nhập (rememberMe)

---

## 🧩 Các Component Reusable

### 1. **FormInput.vue**
**Đường dẫn:** `/src/components/FormInput.vue`

Một component input field có thể tái sử dụng với validation.

```vue
<FormInput
  id="email"
  v-model="form.email"
  label="Email"
  type="email"
  placeholder="your@email.com"
  :error="errors.email"
  :disabled="isLoading"
  required
/>
```

#### Props:
- `id` - ID của input
- `v-model` - Giá trị hai chiều
- `label` - Nhãn của field
- `type` - Loại input (text, email, tel, etc.)
- `placeholder` - Text placeholder
- `error` - Thông báo lỗi
- `disabled` - Disabled state
- `required` - Hiển thị dấu * bắt buộc

---

### 2. **FormPassword.vue**
**Đường dẫn:** `/src/components/FormPassword.vue`

Component password input với nút toggle hiệu lực.

```vue
<FormPassword
  id="password"
  v-model="form.password"
  label="Mật khẩu"
  placeholder="••••••••"
  :error="errors.password"
  :disabled="isLoading"
  required
/>
```

#### Props:
- `id` - ID của input
- `v-model` - Giá trị hai chiều
- `label` - Nhãn của field
- `placeholder` - Text placeholder
- `error` - Thông báo lỗi
- `disabled` - Disabled state
- `required` - Hiển thị dấu * bắt buộc

---

### 3. **AlertMessage.vue**
**Đường dẫn:** `/src/components/AlertMessage.vue`

Component thông báo toàn cục với tự động ẩn.

```vue
<AlertMessage
  :message="successMessage"
  type="success"
  @close="successMessage = ''"
/>
```

#### Props:
- `message` - Nội dung thông báo
- `type` - Loại thông báo (success, error, warning, info)

#### Events:
- `@close` - Khi người dùng đóng thông báo

---

## 🔑 API Services

### **authService** (`/src/services/api.js`)

#### 1. Đăng ký Ứng viên
```javascript
await authService.registerCandidate(fullName, email, phone, password)
```

#### 2. Đăng nhập Ứng viên
```javascript
await authService.login(email, password)
```

#### 3. Đăng ký Doanh nghiệp
```javascript
await authService.registerEmployer(companyName, contactPerson, email, phone, password)
```

#### 4. Đăng nhập Doanh nghiệp
```javascript
await authService.loginEmployer(email, password)
```

#### 5. Đăng xuất
```javascript
await authService.logout()
```

#### 6. Quên mật khẩu
```javascript
await authService.forgotPassword(email)
```

#### 7. Đặt lại mật khẩu
```javascript
await authService.resetPassword(token, newPassword, confirmPassword)
```

#### 8. Thay đổi mật khẩu
```javascript
await authService.changePassword(oldPassword, newPassword, confirmPassword)
```

---

## 🎣 Composable Hook

### **useAuth** (`/src/composables/useAuth.js`)

```javascript
import { useAuth } from '@/composables/useAuth'

// Sử dụng trong component
const {
  user,                 // Người dùng hiện tại
  isAuthenticated,      // Boolean xác thực
  isLoading,           // Trạng thái loading
  error,               // Thông báo lỗi
  loadUser,            // Tải người dùng từ localStorage
  loginCandidate,      // Đăng nhập ứng viên
  registerCandidate,   // Đăng ký ứng viên
  loginEmployer,       // Đăng nhập doanh nghiệp
  registerEmployer,    // Đăng ký doanh nghiệp
  logout,              // Đăng xuất
  changePassword,      // Thay đổi mật khẩu
  forgotPassword,      // Quên mật khẩu
  resetPassword        // Đặt lại mật khẩu
} = useAuth()
```

---

## 📱 Responsive Design

Cả hai trang đều có giao diện responsive:

- **Mobile (< 768px)**: Layout stack chiều dọc
- **Tablet (768px - 1024px)**: Layout hai cột
- **Desktop (> 1024px)**: Layout hai cột đầy đủ

---

## 🎨 Styling & Theme

### Màu sắc
- Primary: `#2463eb` (Xanh dương)
- Dark Mode: Hỗ trợ đầy đủ

### Font
- Font: `Inter` (từ Google Fonts)
- Icons: `Material Symbols Outlined`

---

## ✅ Validation Rules

### Email
- Định dạng email hợp lệ
- Pattern: `/^[^\s@]+@[^\s@]+\.[^\s@]+$/`

### Số điện thoại
- Bắt đầu với số 0
- Tổng 10 chữ số
- Pattern: `/^0\d{9}$/`

### Mật khẩu
- Tối thiểu 6 ký tự

### Họ tên / Tên công ty
- Không được để trống
- Căt bỏ khoảng trắng đầu/cuối

---

## 🚀 Cách sử dụng

### 1. Đăng ký Ứng viên
```
URL: /auth
- Chọn "Ứng viên"
- Điền tất cả thông tin
- Nhấn "Đăng ký"
```

### 2. Đăng ký Doanh nghiệp (qua trang riêng)
```
URL: /employer/auth
- Điền thông tin công ty
- Nhấn "Đăng ký Doanh Nghiệp"
```

### 3. Đăng nhập
```
URL: /auth hoặc /employer/auth
- Nhập email & mật khẩu
- Nhấn "Đăng nhập"
```

---

## 🔐 Security

- ✅ Password toggle (show/hide)
- ✅ Token lưu trong localStorage
- ✅ Authorization header tự động
- ✅ Validation client-side
- ✅ Input sanitization (cơ bản)

---

## 📊 Directory Structure

```
src/
├── components/
│   ├── Guest/
│   │   └── AuthPage.vue           # Trang đăng nhập/ký Guest
│   ├── Employer/
│   │   └── EmployerAuthPage.vue   # Trang đăng nhập/ký Employer
│   ├── FormInput.vue              # Component input reusable
│   ├── FormPassword.vue           # Component password reusable
│   └── AlertMessage.vue           # Component thông báo
├── services/
│   └── api.js                     # API service
├── composables/
│   └── useAuth.js                 # Auth composable hook
└── router/
    └── index.js                   # Route configuration
```

---

## 🔄 Luồng Hoạt động

### Guest Registration & Login
```
1. User truy cập /auth
2. Chọn loại tài khoản (Ứng viên/Doanh nghiệp)
3. Điền form đăng ký
4. Server xác thực & lưu token
5. Redirect đến /dashboard
```

### Employer Registration & Login
```
1. User truy cập /employer/auth
2. Điền form đăng ký công ty
3. Server xác thực & lưu token
4. Redirect đến /employer
```

---

## 🛠️ Tùy chỉnh

### Thay đổi API Endpoint
Edit trong `/src/services/api.js`:
```javascript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL
```

### Thay đổi Màu Sắc
Edit trong HTML/CSS:
- Primary color: `#2463eb`
- Background: `#f6f6f8`

### Thay đổi Validation
Edit logic trong `AuthPage.vue` hoặc `EmployerAuthPage.vue`:
```javascript
const validateRegister = () => {
  // Custom validation logic
}
```

---

## 📝 Notes

- Components sử dụng Vue 3 Composition API
- Tailwind CSS cho styling
- Fetch API cho HTTP requests
- LocalStorage cho token persistence

---

**Cập nhật lần cuối:** 18/03/2026
