<script setup>
import AppLogo from '@/components/AppLogo.vue'
import { reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { authService } from '@/services/api'

const route = useRoute()
const router = useRouter()
const isLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const hasValidResetLink = ref(false)

const resetForm = reactive({
  email: '',
  token: '',
  password: '',
  confirmPassword: '',
})

const resetErrors = reactive({
  email: '',
  password: '',
  confirmPassword: '',
})

watch(
  () => route.query,
  (query) => {
    resetForm.email = typeof query.email === 'string' ? query.email : resetForm.email
    resetForm.token = typeof query.token === 'string' ? query.token : resetForm.token
    hasValidResetLink.value = Boolean(resetForm.email && resetForm.token)
  },
  { immediate: true, deep: true }
)

const validateForm = () => {
  resetErrors.email = ''
  resetErrors.password = ''
  resetErrors.confirmPassword = ''

  if (!resetForm.email.trim()) {
    resetErrors.email = 'Vui lòng nhập email'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(resetForm.email)) {
    resetErrors.email = 'Email không hợp lệ'
  }

  if (!resetForm.password) {
    resetErrors.password = 'Vui lòng nhập mật khẩu mới'
  } else if (resetForm.password.length < 6) {
    resetErrors.password = 'Mật khẩu phải có ít nhất 6 ký tự'
  }

  if (!resetForm.confirmPassword) {
    resetErrors.confirmPassword = 'Vui lòng xác nhận mật khẩu'
  } else if (resetForm.confirmPassword !== resetForm.password) {
    resetErrors.confirmPassword = 'Mật khẩu xác nhận không khớp'
  }

  return Object.values(resetErrors).every(err => !err)
}

const handleResetPassword = async () => {
  if (!hasValidResetLink.value) {
    errorMessage.value = 'Liên kết đặt lại mật khẩu không hợp lệ hoặc đã bị thiếu thông tin.'
    return
  }

  if (!validateForm()) return

  isLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const response = await authService.resetPassword({
      email: resetForm.email.trim(),
      token: resetForm.token.trim(),
      password: resetForm.password,
      confirmPassword: resetForm.confirmPassword,
    })

    successMessage.value = response?.message || 'Đặt lại mật khẩu thành công.'

    setTimeout(() => {
      router.push('/login')
    }, 1200)
  } catch (error) {
    errorMessage.value = error.message || 'Không thể đặt lại mật khẩu.'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="auth-page auth-page--reset">
    <section class="auth-showcase">
      <div class="showcase-inner">
        <RouterLink to="/" class="showcase-brand">
          <AppLogo size="lg" tone="light" title="AI Recruitment" subtitle="Career Intelligence Platform" />
        </RouterLink>

        <div class="showcase-copy">
          <h1>Thiết lập mật khẩu mới an toàn.</h1>
          <p>
            Xác nhận đúng email, token và mật khẩu mới để tiếp tục quay lại hệ thống với vai trò hiện tại của bạn.
          </p>
        </div>

        <div class="showcase-feature-list">
          <div class="feature-item">
            <span class="material-symbols-outlined">key</span>
            <span>Mật khẩu mới sẽ thay thế hoàn toàn mật khẩu cũ</span>
          </div>
          <div class="feature-item">
            <span class="material-symbols-outlined">lock_reset</span>
            <span>Sau khi hoàn tất, hệ thống sẽ đưa bạn về màn đăng nhập</span>
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
        </div>

        <div class="auth-head">
          <h2>Đặt lại mật khẩu</h2>
          <p>Điền đầy đủ thông tin xác thực bên dưới để cập nhật mật khẩu mới cho tài khoản của bạn.</p>
        </div>

        <div v-if="!hasValidResetLink" class="auth-alert auth-alert--error">
          <span class="material-symbols-outlined">error</span>
          <span>Liên kết đặt lại mật khẩu không hợp lệ. Vui lòng quay lại bước quên mật khẩu để nhận email mới.</span>
        </div>

        <form class="auth-form" @submit.prevent="handleResetPassword">
          <div class="field-group">
            <label for="email">Email tài khoản</label>
            <div class="input-shell" :class="{ 'input-shell--error': resetErrors.email }">
              <span class="material-symbols-outlined">mail</span>
              <input
                id="email"
                v-model="resetForm.email"
                type="email"
                placeholder="your@email.com"
                :disabled="isLoading || hasValidResetLink"
              >
            </div>
            <span v-if="resetErrors.email" class="field-error">{{ resetErrors.email }}</span>
          </div>

          <div class="field-group">
            <label for="password">Mật khẩu mới</label>
            <div class="input-shell" :class="{ 'input-shell--error': resetErrors.password }">
              <span class="material-symbols-outlined">lock</span>
              <input
                id="password"
                v-model="resetForm.password"
                :type="showPassword ? 'text' : 'password'"
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
            <span v-if="resetErrors.password" class="field-error">{{ resetErrors.password }}</span>
          </div>

          <div class="field-group">
            <label for="confirmPassword">Xác nhận mật khẩu mới</label>
            <div class="input-shell" :class="{ 'input-shell--error': resetErrors.confirmPassword }">
              <span class="material-symbols-outlined">verified_user</span>
              <input
                id="confirmPassword"
                v-model="resetForm.confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                placeholder="Nhập lại mật khẩu mới"
                :disabled="isLoading"
              >
              <button
                type="button"
                class="toggle-visibility"
                :aria-label="showConfirmPassword ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'"
                @click="showConfirmPassword = !showConfirmPassword"
              >
                <span class="material-symbols-outlined">{{ showConfirmPassword ? 'visibility_off' : 'visibility' }}</span>
              </button>
            </div>
            <span v-if="resetErrors.confirmPassword" class="field-error">{{ resetErrors.confirmPassword }}</span>
          </div>

          <button type="submit" class="submit-button" :disabled="isLoading || !hasValidResetLink">
            <span v-if="isLoading" class="spinner"></span>
            <span>{{ isLoading ? 'Đang cập nhật...' : 'Lưu mật khẩu mới' }}</span>
          </button>
        </form>

        <p class="auth-switch">
          Muốn quay lại bước trước?
          <RouterLink to="/forgot-password">Quên mật khẩu</RouterLink>
        </p>
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
  color: #fff;
  text-decoration: none;
  margin-bottom: 3rem;
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

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 1100px) {
  .auth-page {
    grid-template-columns: 1fr;
  }

  .auth-showcase {
    min-height: 28rem;
  }
}

@media (max-width: 640px) {
  .auth-panel,
  .showcase-inner {
    padding: 1.5rem;
  }

  .auth-card {
    padding: 1.4rem;
    border-radius: 1.35rem;
  }
}
</style>
