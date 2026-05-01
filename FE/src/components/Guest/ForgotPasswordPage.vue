<script setup>
import { onBeforeUnmount, reactive, ref, watch } from 'vue'
import { authService } from '@/services/api'

const ALERT_AUTO_DISMISS_MS = 5000
const isLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const alertTimeoutId = ref(null)

const forgotForm = reactive({
  email: '',
})

const forgotErrors = reactive({
  email: '',
})

const resetMessages = () => {
  if (alertTimeoutId.value) {
    clearTimeout(alertTimeoutId.value)
    alertTimeoutId.value = null
  }

  errorMessage.value = ''
  successMessage.value = ''
}

const scheduleAlertDismiss = () => {
  if (alertTimeoutId.value) {
    clearTimeout(alertTimeoutId.value)
  }

  if (!errorMessage.value && !successMessage.value) {
    alertTimeoutId.value = null
    return
  }

  alertTimeoutId.value = window.setTimeout(() => {
    resetMessages()
  }, ALERT_AUTO_DISMISS_MS)
}

watch([errorMessage, successMessage], () => {
  scheduleAlertDismiss()
})

onBeforeUnmount(() => {
  if (alertTimeoutId.value) {
    clearTimeout(alertTimeoutId.value)
  }
})

const validateForm = () => {
  forgotErrors.email = ''

  if (!forgotForm.email.trim()) {
    forgotErrors.email = 'Vui lòng nhập email'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(forgotForm.email)) {
    forgotErrors.email = 'Email không hợp lệ'
  }

  return !forgotErrors.email
}

const handleForgotPassword = async () => {
  if (!validateForm()) return

  isLoading.value = true
  resetMessages()

  try {
    const response = await authService.forgotPassword(forgotForm.email)
    successMessage.value = response?.message || 'Nếu email tồn tại trong hệ thống, chúng tôi đã gửi liên kết đặt lại mật khẩu.'
  } catch (error) {
    errorMessage.value = error.message || 'Không thể xử lý yêu cầu quên mật khẩu.'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="auth-page auth-page--forgot">
    <section class="auth-showcase">
      <div class="showcase-inner">
        <RouterLink to="/" class="showcase-brand">
          <span class="brand-mark">
            <span class="material-symbols-outlined">rocket_launch</span>
          </span>
          <span>SmartJob AI</span>
        </RouterLink>

        <div class="showcase-copy">
          <h1>Lấy lại quyền truy cập thật nhanh.</h1>
          <p>
            Nhập email tài khoản để tiếp tục bước đặt lại mật khẩu trong cùng trải nghiệm đăng nhập quen thuộc.
          </p>
        </div>

        <div class="showcase-feature-list">
          <div class="feature-item">
            <span class="material-symbols-outlined">shield_lock</span>
            <span>Xác minh đúng tài khoản trước khi đổi mật khẩu</span>
          </div>
          <div class="feature-item">
            <span class="material-symbols-outlined">bolt</span>
            <span>Luồng test nhanh trên localhost, không cần rời khỏi hệ thống</span>
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
          <h2>Quên mật khẩu</h2>
          <p>Nhập email bạn đã dùng để đăng ký. Hệ thống sẽ gửi một liên kết đặt lại mật khẩu tới hộp thư của bạn.</p>
        </div>

        <form class="auth-form" @submit.prevent="handleForgotPassword">
          <div class="field-group">
            <label for="email">Email tài khoản</label>
            <div class="input-shell" :class="{ 'input-shell--error': forgotErrors.email }">
              <span class="material-symbols-outlined">mail</span>
              <input
                id="email"
                v-model="forgotForm.email"
                type="email"
                placeholder="your@email.com"
                :disabled="isLoading"
              >
            </div>
            <span v-if="forgotErrors.email" class="field-error">{{ forgotErrors.email }}</span>
          </div>

          <button type="submit" class="submit-button" :disabled="isLoading">
            <span v-if="isLoading" class="spinner"></span>
            <span>{{ isLoading ? 'Đang gửi email...' : 'Gửi liên kết đặt lại mật khẩu' }}</span>
          </button>
        </form>

        <p class="auth-switch">
          Đã nhớ mật khẩu?
          <RouterLink to="/login">Quay lại đăng nhập</RouterLink>
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

.auth-note {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  margin-top: 1.4rem;
  padding: 1rem 1.1rem;
  border-radius: 1rem;
  border: 1px solid #dbe5f3;
  background: #f8fbff;
  color: #475569;
  line-height: 1.6;
}

.auth-note .material-symbols-outlined {
  font-size: 1.2rem;
  color: #295fe6;
}

.auth-form {
  margin-top: 1.8rem;
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
