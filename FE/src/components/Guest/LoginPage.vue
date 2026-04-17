<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { authService } from '@/services/api'
import { persistAuthSession } from '@/utils/authStorage'

const router = useRouter()
const route = useRoute()
const isLoading = ref(false)
const googleLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const showPassword = ref(false)
const resendLoading = ref(false)
const verificationPendingEmail = ref('')
const REMEMBER_LOGIN_KEY = 'remember_login_email'

const loginForm = reactive({
  email: '',
  password: '',
  rememberMe: false,
})

const loginErrors = reactive({
  email: '',
  password: '',
})

const validateLogin = () => {
  loginErrors.email = ''
  loginErrors.password = ''

  if (!loginForm.email.trim()) {
    loginErrors.email = 'Vui lòng nhập email'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(loginForm.email)) {
    loginErrors.email = 'Email không hợp lệ'
  }

  if (!loginForm.password) {
    loginErrors.password = 'Vui lòng nhập mật khẩu'
  }

  return Object.values(loginErrors).every(err => !err)
}

const loadRememberedLogin = () => {
  if (typeof window === 'undefined') return

  const raw = window.localStorage.getItem(REMEMBER_LOGIN_KEY)
  if (!raw) return

  try {
    const parsed = JSON.parse(raw)
    loginForm.email = typeof parsed.email === 'string' ? parsed.email : ''
    loginForm.rememberMe = Boolean(parsed.rememberMe)
  } catch {
    window.localStorage.removeItem(REMEMBER_LOGIN_KEY)
  }
}

const persistRememberedLogin = () => {
  if (typeof window === 'undefined') return

  if (!loginForm.rememberMe) {
    window.localStorage.removeItem(REMEMBER_LOGIN_KEY)
    return
  }

  window.localStorage.setItem(REMEMBER_LOGIN_KEY, JSON.stringify({
    email: loginForm.email.trim(),
    rememberMe: true,
  }))
}

const persistAuth = (response) => {
  const token = response?.access_token || response?.token || response?.data?.access_token || response?.data?.token
  const user = response?.user || response?.data?.user || response?.nguoi_dung || response?.data?.nguoi_dung

  if (token && user) {
    persistAuthSession(token, user)
  }
}

const handleLogin = async () => {
  if (!validateLogin()) return

  isLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const response = await authService.login(loginForm.email, loginForm.password)
    persistRememberedLogin()
    persistAuth(response)
    successMessage.value = response.message || 'Đăng nhập thành công'

    setTimeout(() => {
      const role = Number(
        response?.user?.vai_tro ??
        response?.data?.user?.vai_tro ??
        response?.nguoi_dung?.vai_tro ??
        response?.data?.nguoi_dung?.vai_tro ??
        0
      )
      const fallback = role === 2 ? '/admin' : role === 1 ? '/employer' : '/dashboard'
      router.push(typeof route.query.redirect === 'string' ? route.query.redirect : fallback)
    }, 500)
  } catch (error) {
    errorMessage.value = error.message || 'Đăng nhập thất bại'
    verificationPendingEmail.value = error?.data?.email || loginForm.email.trim()
  } finally {
    isLoading.value = false
  }
}

const handleResendVerification = async () => {
  if (!verificationPendingEmail.value || resendLoading.value) return

  resendLoading.value = true
  errorMessage.value = ''

  try {
    const response = await authService.resendVerificationEmail(verificationPendingEmail.value)
    successMessage.value = response?.message || 'Đã gửi lại email xác thực.'
  } catch (error) {
    errorMessage.value = error.message || 'Không thể gửi lại email xác thực.'
  } finally {
    resendLoading.value = false
  }
}

const handleGoogleLogin = () => {
  googleLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  window.location.href = authService.getGoogleAuthUrl(
    0,
    typeof route.query.redirect === 'string' ? route.query.redirect : ''
  )
}

onMounted(() => {
  loadRememberedLogin()

  const email = typeof route.query.email === 'string' ? route.query.email : ''
  if (email) {
    loginForm.email = email
    verificationPendingEmail.value = email
  }

  if (route.query.verified === '1') {
    successMessage.value = 'Email đã được xác thực thành công. Bạn có thể đăng nhập ngay.'
  } else if (route.query.verified === '0') {
    errorMessage.value = 'Liên kết xác thực email không hợp lệ hoặc đã hết hạn.'
  } else if (route.query.verify_pending === '1') {
    successMessage.value = 'Đăng ký thành công. Vui lòng kiểm tra email để xác thực tài khoản trước khi đăng nhập.'
  } else if (typeof route.query.google_error === 'string' && route.query.google_error.trim()) {
    errorMessage.value = route.query.google_error
  }
})
</script>

<template>
  <div class="auth-page auth-page--login">
    <section class="auth-showcase">
      <div class="showcase-inner">
        <RouterLink to="/" class="showcase-brand">
          <span class="brand-mark">
            <span class="material-symbols-outlined">rocket_launch</span>
          </span>
          <span>SmartJob AI</span>
        </RouterLink>

        <div class="showcase-copy">
          <h1>Nâng tầm sự nghiệp của bạn</h1>
          <p>
            Khám phá cơ hội nghề nghiệp tốt nhất được cá nhân hóa bởi trí tuệ nhân tạo hàng đầu.
          </p>
        </div>

        <div class="showcase-feature-list">
          <div class="feature-item">
            <span class="material-symbols-outlined">verified</span>
            <span>Phân tích CV chuyên sâu bằng AI</span>
          </div>
          <div class="feature-item">
            <span class="material-symbols-outlined">auto_awesome</span>
            <span>Gợi ý việc làm phù hợp theo hồ sơ</span>
          </div>
        </div>
      </div>
    </section>

    <section class="auth-panel">
      <div class="auth-card">
        <div v-if="errorMessage || successMessage" class="auth-alert-wrap">
          <div v-if="errorMessage" class="auth-alert auth-alert--error">
            <span class="material-symbols-outlined">error</span>
            <span>{{ errorMessage }}</span>
          </div>
          <div v-if="successMessage" class="auth-alert auth-alert--success">
            <span class="material-symbols-outlined">check_circle</span>
            <span>{{ successMessage }}</span>
          </div>
          <button
            v-if="verificationPendingEmail && errorMessage.includes('xác thực email')"
            type="button"
            class="mt-3 inline-flex items-center justify-center rounded-xl border border-blue-200 bg-blue-50 px-4 py-2 text-sm font-semibold text-blue-700 transition hover:bg-blue-100 disabled:cursor-not-allowed disabled:opacity-60"
            :disabled="resendLoading"
            @click="handleResendVerification"
          >
            {{ resendLoading ? 'Đang gửi lại...' : 'Gửi lại email xác thực' }}
          </button>
        </div>

        <div class="auth-head">
          <h2>Đăng nhập - SmartJob AI</h2>
          <p>Chào mừng quay trở lại với tương lai nghề nghiệp của bạn.</p>
        </div>

        <form class="auth-form" autocomplete="on" @submit.prevent="handleLogin">
          <div class="field-group">
            <label for="email">Email</label>
            <div class="input-shell" :class="{ 'input-shell--error': loginErrors.email }">
              <span class="material-symbols-outlined">mail</span>
              <input
                id="email"
                v-model="loginForm.email"
                type="email"
                autocomplete="email"
                placeholder="your@email.com"
                :disabled="isLoading"
              >
            </div>
            <span v-if="loginErrors.email" class="field-error">{{ loginErrors.email }}</span>
          </div>

          <div class="field-group">
            <label for="password">Mật khẩu</label>
            <div class="input-shell" :class="{ 'input-shell--error': loginErrors.password }">
              <span class="material-symbols-outlined">lock</span>
              <input
                id="password"
                v-model="loginForm.password"
                :type="showPassword ? 'text' : 'password'"
                autocomplete="current-password"
                placeholder="••••••••"
                :disabled="isLoading"
              >
              <button
                type="button"
                class="toggle-visibility"
                :aria-label="showPassword ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'"
                @click="showPassword = !showPassword"
              >
                <span class="material-symbols-outlined">{{ showPassword ? 'visibility_off' : 'visibility' }}</span>
              </button>
            </div>
            <span v-if="loginErrors.password" class="field-error">{{ loginErrors.password }}</span>
          </div>

          <div class="form-meta">
            <label class="remember-row">
              <input v-model="loginForm.rememberMe" type="checkbox">
              <span>Ghi nhớ đăng nhập</span>
            </label>
            <RouterLink to="/forgot-password" class="meta-link">Quên mật khẩu?</RouterLink>
          </div>

          <button type="submit" class="submit-button" :disabled="isLoading">
            <span v-if="isLoading" class="spinner"></span>
            <span>{{ isLoading ? 'Đang đăng nhập...' : 'Đăng nhập hệ thống' }}</span>
          </button>
        </form>

        <div class="divider">
          <span>Hoặc tiếp tục với</span>
        </div>

        <div class="social-grid">
          <button type="button" class="social-button" :disabled="googleLoading" @click="handleGoogleLogin">
            <svg class="social-icon" viewBox="0 0 24 24" aria-hidden="true">
              <path fill="#EA4335" d="M12 10.2v3.9h5.4c-.2 1.3-1.6 3.8-5.4 3.8-3.2 0-5.9-2.7-5.9-6s2.7-6 5.9-6c1.8 0 3 .8 3.7 1.5l2.5-2.4C16.7 3.6 14.6 2.7 12 2.7 6.9 2.7 2.8 6.8 2.8 12s4.1 9.3 9.2 9.3c5.3 0 8.8-3.7 8.8-8.9 0-.6-.1-1.1-.2-1.6H12Z" />
              <path fill="#4285F4" d="M21 12c0-.6-.1-1.1-.2-1.6H12v3.9h5.4c-.3 1.4-1.1 2.6-2.4 3.4l2.9 2.2c1.7-1.6 2.6-4 2.6-6.9Z" />
              <path fill="#FBBC05" d="M6.5 14.2c-.2-.6-.4-1.3-.4-2.2s.1-1.5.4-2.2L3.5 7.5C2.9 8.8 2.6 10.3 2.6 12s.3 3.2.9 4.5l3-2.3Z" />
              <path fill="#34A853" d="M12 21.3c2.6 0 4.7-.9 6.3-2.5l-2.9-2.2c-.8.5-1.9.9-3.4.9-3.2 0-5.9-2.7-5.9-6 0-.8.2-1.5.4-2.2L3.5 7.5C2.9 8.8 2.6 10.3 2.6 12 2.6 17.2 6.8 21.3 12 21.3Z" />
            </svg>
            <span>{{ googleLoading ? 'Đang chuyển tới Google...' : 'Tiếp tục với Google' }}</span>
          </button>
        </div>

        <p class="auth-switch">
          Chưa có tài khoản?
          <RouterLink to="/register">Đăng ký ngay</RouterLink>
        </p>

        <div class="auth-footer-links">
          <RouterLink to="/">Quy định bảo mật</RouterLink>
          <RouterLink to="/">Điều khoản sử dụng</RouterLink>
          <RouterLink to="/">Liên hệ</RouterLink>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1.02fr 1fr;
  background: #f8fbff;
}

.auth-showcase {
  position: relative;
  overflow: hidden;
  background:
    radial-gradient(circle at 50% 70%, rgba(137, 92, 255, 0.34), transparent 24%),
    radial-gradient(circle at left center, rgba(59, 130, 246, 0.55), transparent 22%),
    linear-gradient(180deg, #295fe6 0%, #2f46bf 45%, #2a358e 100%);
  color: #fff;
}

.auth-showcase::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at center, rgba(255, 255, 255, 0.18), transparent 34%),
    linear-gradient(115deg, transparent 38%, rgba(120, 188, 255, 0.25) 50%, transparent 62%);
  opacity: 0.95;
  pointer-events: none;
}

.showcase-inner {
  position: relative;
  z-index: 1;
  min-height: 100%;
  padding: 4rem 7vw;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.showcase-brand {
  display: inline-flex;
  align-items: center;
  gap: 1rem;
  color: #fff;
  text-decoration: none;
  font-size: 1.7rem;
  font-weight: 800;
  margin-bottom: 3rem;
}

.brand-mark {
  width: 3.6rem;
  height: 3.6rem;
  display: grid;
  place-items: center;
  border-radius: 1.15rem;
  background: rgba(255, 255, 255, 0.14);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.12);
}

.brand-mark .material-symbols-outlined {
  font-size: 1.8rem;
}

.showcase-copy h1 {
  max-width: 34rem;
  margin: 0 0 1.25rem;
  font-size: clamp(3rem, 5vw, 4.7rem);
  line-height: 1.05;
  font-weight: 800;
  letter-spacing: -0.04em;
}

.showcase-copy p {
  max-width: 34rem;
  margin: 0;
  color: rgba(236, 242, 255, 0.92);
  font-size: 1.18rem;
  line-height: 1.8;
}

.showcase-feature-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 2.6rem;
}

.feature-item {
  display: inline-flex;
  align-items: center;
  gap: 0.9rem;
  width: fit-content;
  padding: 0.9rem 1.15rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(10px);
  color: rgba(255, 255, 255, 0.98);
}

.feature-item .material-symbols-outlined {
  font-size: 1.2rem;
}

.auth-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem;
}

.auth-card {
  width: 100%;
  max-width: 35rem;
  padding: 2.6rem;
  border-radius: 2rem;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(199, 210, 254, 0.7);
  box-shadow: 0 30px 80px rgba(30, 64, 175, 0.12);
  backdrop-filter: blur(14px);
}

.auth-alert-wrap {
  display: grid;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}

.auth-alert {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.9rem 1rem;
  border-radius: 1rem;
  font-size: 0.95rem;
}

.auth-alert--error {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #b91c1c;
}

.auth-alert--success {
  background: #ecfdf5;
  border: 1px solid #a7f3d0;
  color: #047857;
}

.auth-head h2 {
  margin: 0;
  font-size: 2rem;
  font-weight: 800;
  color: #0f172a;
}

.auth-head p {
  margin: 0.65rem 0 0;
  color: #64748b;
  line-height: 1.7;
}

.auth-form {
  margin-top: 2rem;
}

.field-group + .field-group {
  margin-top: 1rem;
}

.field-group label {
  display: block;
  margin-bottom: 0.55rem;
  font-size: 0.95rem;
  font-weight: 700;
  color: #0f172a;
}

.input-shell {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 0 1rem;
  min-height: 3.7rem;
  border-radius: 1rem;
  border: 1px solid #dbe5f3;
  background: #f8fbff;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.input-shell:focus-within {
  border-color: #295fe6;
  box-shadow: 0 0 0 4px rgba(41, 95, 230, 0.12);
}

.input-shell--error {
  border-color: #ef4444;
}

.input-shell .material-symbols-outlined {
  font-size: 1.25rem;
  color: #6b7ca8;
}

.input-shell input {
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  font-size: 1rem;
  color: #0f172a;
}

.toggle-visibility {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  color: #64748b;
  cursor: pointer;
}

.field-error {
  display: block;
  margin-top: 0.45rem;
  color: #dc2626;
  font-size: 0.82rem;
}

.form-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-top: 1rem;
}

.remember-row {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
  color: #475569;
  font-size: 0.92rem;
}

.meta-link {
  color: #295fe6;
  font-size: 0.92rem;
  font-weight: 600;
  text-decoration: none;
}

.submit-button {
  margin-top: 1.4rem;
  width: 100%;
  min-height: 3.7rem;
  border: none;
  border-radius: 1rem;
  background: linear-gradient(135deg, #2f67ee 0%, #2f46bf 100%);
  color: #fff;
  font-size: 1rem;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.7rem;
  cursor: pointer;
  box-shadow: 0 18px 32px rgba(47, 103, 238, 0.24);
}

.submit-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.spinner {
  width: 1rem;
  height: 1rem;
  border-radius: 999px;
  border: 2px solid rgba(255, 255, 255, 0.45);
  border-top-color: #fff;
  animation: spin 0.8s linear infinite;
}

.divider {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin: 1.8rem 0 1.2rem;
  color: #94a3b8;
  font-size: 0.88rem;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #dbe5f3;
}

.social-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.9rem;
}

.social-button {
  width: 100%;
  min-height: 3.55rem;
  border-radius: 1rem;
  border: 1px solid #dbe5f3;
  background: #fff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  font-weight: 700;
  color: #0f172a;
  cursor: pointer;
}

.social-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.social-icon {
  width: 1.15rem;
  height: 1.15rem;
}

.auth-switch {
  margin: 1.6rem 0 0;
  color: #64748b;
  text-align: center;
}

.auth-switch a {
  margin-left: 0.35rem;
  color: #295fe6;
  font-weight: 700;
  text-decoration: none;
}

.auth-footer-links {
  margin-top: 1.5rem;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 1rem;
}

.auth-footer-links a {
  color: #94a3b8;
  font-size: 0.85rem;
  text-decoration: none;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 980px) {
  .auth-page {
    grid-template-columns: 1fr;
  }

  .auth-showcase {
    min-height: 22rem;
  }

  .auth-panel {
    padding: 1.5rem;
  }

  .showcase-inner {
    padding: 3rem 1.5rem;
  }
}

@media (max-width: 640px) {
  .auth-card {
    padding: 1.4rem;
    border-radius: 1.4rem;
  }

  .showcase-copy h1 {
    font-size: 2.3rem;
  }

  .form-meta {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
