<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { authService } from '@/services/api'

const router = useRouter()
const route = useRoute()
const accountType = ref('candidate')
const isLoading = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

const registerForm = reactive({
  fullName: '',
  companyName: '',
  contactPerson: '',
  email: '',
  phone: '',
  password: '',
  confirmPassword: '',
})

const registerErrors = reactive({
  fullName: '',
  companyName: '',
  contactPerson: '',
  email: '',
  phone: '',
  password: '',
  confirmPassword: '',
})

const isEmployer = computed(() => accountType.value === 'employer')

const pageCopy = computed(() => {
  if (isEmployer.value) {
    return {
      showcaseTitle: 'Tăng tốc tuyển dụng cùng AI.',
      showcaseDescription:
        'Thiết lập hồ sơ doanh nghiệp, đăng tin nhanh hơn và tiếp cận đúng ứng viên với hệ thống tuyển dụng thông minh.',
      headTitle: 'Đăng ký nhà tuyển dụng',
      headDescription: 'Tạo tài khoản doanh nghiệp để quản lý công ty và đăng tin tuyển dụng.',
      submitLabel: 'Tạo tài khoản tuyển dụng',
      loginHint: 'Đã có tài khoản doanh nghiệp?',
      fullNameLabel: 'Người liên hệ',
      fullNamePlaceholder: 'Nhập họ tên người phụ trách tuyển dụng',
    }
  }

  return {
    showcaseTitle: 'Nâng tầm sự nghiệp cùng AI.',
    showcaseDescription:
      'Kết nối đúng người, đúng việc với công nghệ trí tuệ nhân tạo hàng đầu. Khởi đầu hành trình mới của bạn ngay hôm nay.',
    headTitle: 'Đăng ký ứng viên',
    headDescription: 'Tham gia mạng lưới tuyển dụng thông minh ngay hôm nay.',
    submitLabel: 'Tạo tài khoản SmartJob AI',
    loginHint: 'Bạn đã có tài khoản?',
    fullNameLabel: 'Họ và tên',
    fullNamePlaceholder: 'Nhập họ và tên của bạn',
  }
})

const resetMessages = () => {
  errorMessage.value = ''
  successMessage.value = ''
}

const clearValidationErrors = () => {
  registerErrors.fullName = ''
  registerErrors.companyName = ''
  registerErrors.contactPerson = ''
  registerErrors.email = ''
  registerErrors.phone = ''
  registerErrors.password = ''
  registerErrors.confirmPassword = ''
}

watch(
  () => route.query.role,
  (role) => {
    accountType.value = role === 'employer' ? 'employer' : 'candidate'
  },
  { immediate: true }
)

watch(accountType, (type) => {
  clearValidationErrors()
  resetMessages()

  router.replace({
    query: type === 'employer' ? { ...route.query, role: 'employer' } : {},
  })
})

const validateRegister = () => {
  clearValidationErrors()

  if (isEmployer.value) {
    if (!registerForm.companyName.trim()) {
      registerErrors.companyName = 'Vui lòng nhập tên công ty'
    }

    if (!registerForm.contactPerson.trim()) {
      registerErrors.contactPerson = 'Vui lòng nhập người liên hệ'
    }
  } else if (!registerForm.fullName.trim()) {
    registerErrors.fullName = 'Vui lòng nhập họ tên'
  }

  if (!registerForm.email.trim()) {
    registerErrors.email = 'Vui lòng nhập email'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(registerForm.email)) {
    registerErrors.email = 'Email không hợp lệ'
  }

  if (!registerForm.phone.trim()) {
    registerErrors.phone = 'Vui lòng nhập số điện thoại'
  } else if (!/^0\d{9}$/.test(registerForm.phone.replace(/\s+/g, ''))) {
    registerErrors.phone = 'Số điện thoại không hợp lệ'
  }

  if (!registerForm.password) {
    registerErrors.password = 'Vui lòng nhập mật khẩu'
  } else if (registerForm.password.length < 6) {
    registerErrors.password = 'Mật khẩu phải có ít nhất 6 ký tự'
  }

  if (!registerForm.confirmPassword) {
    registerErrors.confirmPassword = 'Vui lòng xác nhận mật khẩu'
  } else if (registerForm.confirmPassword !== registerForm.password) {
    registerErrors.confirmPassword = 'Mật khẩu xác nhận không khớp'
  }

  return Object.values(registerErrors).every(err => !err)
}

const handleRegister = async () => {
  if (!validateRegister()) return

  isLoading.value = true
  resetMessages()

  try {
    const registeredEmail = registerForm.email.trim()
    const companyDraft = isEmployer.value
      ? {
        ten_cong_ty: registerForm.companyName.trim(),
        email: registeredEmail,
        dien_thoai: registerForm.phone.trim(),
        nguoi_lien_he: registerForm.contactPerson.trim(),
      }
      : null

    const response = isEmployer.value
      ? await authService.registerEmployer(
        registerForm.companyName,
        registerForm.contactPerson,
        registerForm.email,
        registerForm.phone,
        registerForm.password
      )
      : await authService.registerCandidate(
        registerForm.fullName,
        registerForm.email,
        registerForm.phone,
        registerForm.password
      )

    if (response.success || response.message) {
      if (companyDraft) {
        window.sessionStorage.setItem('employer_company_draft', JSON.stringify(companyDraft))
      }

      successMessage.value = 'Đăng ký thành công! Vui lòng đăng nhập.'
      Object.assign(registerForm, {
        fullName: '',
        companyName: '',
        contactPerson: '',
        email: '',
        phone: '',
        password: '',
        confirmPassword: '',
      })

      setTimeout(() => {
        router.push({
          path: '/login',
          query: {
            verify_pending: '1',
            email: registeredEmail,
          },
        })
      }, 1200)
    }
  } catch (error) {
    errorMessage.value = error.message || 'Đăng ký thất bại'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="auth-page auth-page--register">
    <section class="auth-showcase">
      <div class="showcase-inner">
        <RouterLink to="/" class="showcase-brand">
          <span class="brand-mark">
            <span class="material-symbols-outlined">rocket_launch</span>
          </span>
          <span>SmartJob AI</span>
        </RouterLink>

        <div class="showcase-copy">
          <h1>{{ pageCopy.showcaseTitle }}</h1>
          <p>{{ pageCopy.showcaseDescription }}</p>
        </div>

        <div class="showcase-stats">
          <div class="stat-card">
            <strong>10k+</strong>
            <span>Việc làm mới</span>
          </div>
          <div class="stat-card">
            <strong>500+</strong>
            <span>Doanh nghiệp</span>
          </div>
        </div>
      </div>
    </section>

    <section class="auth-panel">
      <div class="auth-shell">
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
          <h2>{{ pageCopy.headTitle }}</h2>
          <p>{{ pageCopy.headDescription }}</p>
        </div>

        <div class="auth-card">
          <div class="role-switch" role="tablist" aria-label="Chọn vai trò">
            <button
              type="button"
              class="role-button"
              :class="{ active: accountType === 'candidate' }"
              @click="accountType = 'candidate'"
            >
              Tôi muốn tìm việc
            </button>
            <button
              type="button"
              class="role-button"
              :class="{ active: accountType === 'employer' }"
              @click="accountType = 'employer'"
            >
              Tôi muốn tuyển dụng
            </button>
          </div>

          <form class="auth-form" @submit.prevent="handleRegister">
            <div v-if="isEmployer" class="field-group">
              <label for="companyName">Tên công ty</label>
              <div class="input-shell" :class="{ 'input-shell--error': registerErrors.companyName }">
                <span class="material-symbols-outlined">business</span>
                <input
                  id="companyName"
                  v-model="registerForm.companyName"
                  type="text"
                  placeholder="Nhập tên công ty"
                  :disabled="isLoading"
                >
              </div>
              <span v-if="registerErrors.companyName" class="field-error">{{ registerErrors.companyName }}</span>
            </div>

            <div class="field-group">
              <label for="fullName">{{ pageCopy.fullNameLabel }}</label>
              <div class="input-shell" :class="{ 'input-shell--error': isEmployer ? registerErrors.contactPerson : registerErrors.fullName }">
                <span class="material-symbols-outlined">person</span>
                <input
                  v-if="isEmployer"
                  id="fullName"
                  v-model="registerForm.contactPerson"
                  type="text"
                  :placeholder="pageCopy.fullNamePlaceholder"
                  :disabled="isLoading"
                >
                <input
                  v-else
                  id="fullName"
                  v-model="registerForm.fullName"
                  type="text"
                  :placeholder="pageCopy.fullNamePlaceholder"
                  :disabled="isLoading"
                >
              </div>
              <span v-if="isEmployer && registerErrors.contactPerson" class="field-error">{{ registerErrors.contactPerson }}</span>
              <span v-else-if="!isEmployer && registerErrors.fullName" class="field-error">{{ registerErrors.fullName }}</span>
            </div>

            <div class="field-group">
              <label for="email">Email</label>
              <div class="input-shell" :class="{ 'input-shell--error': registerErrors.email }">
                <span class="material-symbols-outlined">mail</span>
                <input
                  id="email"
                  v-model="registerForm.email"
                  type="email"
                  placeholder="example@email.com"
                  :disabled="isLoading"
                >
              </div>
              <span v-if="registerErrors.email" class="field-error">{{ registerErrors.email }}</span>
            </div>

            <div class="field-group">
              <label for="phone">Số điện thoại</label>
              <div class="input-shell" :class="{ 'input-shell--error': registerErrors.phone }">
                <span class="material-symbols-outlined">call</span>
                <input
                  id="phone"
                  v-model="registerForm.phone"
                  type="tel"
                  placeholder="Nhập số điện thoại"
                  :disabled="isLoading"
                >
              </div>
              <span v-if="registerErrors.phone" class="field-error">{{ registerErrors.phone }}</span>
            </div>

            <div class="field-group">
              <label for="password">Mật khẩu</label>
              <div class="input-shell" :class="{ 'input-shell--error': registerErrors.password }">
                <span class="material-symbols-outlined">lock</span>
                <input
                  id="password"
                  v-model="registerForm.password"
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
              <span v-if="registerErrors.password" class="field-error">{{ registerErrors.password }}</span>
            </div>

            <div class="field-group">
              <label for="confirmPassword">Xác nhận mật khẩu</label>
              <div class="input-shell" :class="{ 'input-shell--error': registerErrors.confirmPassword }">
                <span class="material-symbols-outlined">verified_user</span>
                <input
                  id="confirmPassword"
                  v-model="registerForm.confirmPassword"
                  :type="showConfirmPassword ? 'text' : 'password'"
                  placeholder="Nhập lại mật khẩu"
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
              <span v-if="registerErrors.confirmPassword" class="field-error">{{ registerErrors.confirmPassword }}</span>
            </div>

            <button type="submit" class="submit-button" :disabled="isLoading">
              <span v-if="isLoading" class="spinner"></span>
              <span>{{ isLoading ? 'Đang đăng ký...' : pageCopy.submitLabel }}</span>
            </button>
          </form>
        </div>

        <p class="auth-switch">
          {{ pageCopy.loginHint }}
          <RouterLink to="/login">Đăng nhập ngay</RouterLink>
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
    radial-gradient(circle at top left, rgba(103, 190, 255, 0.16), transparent 22%),
    linear-gradient(180deg, #2f67ee 0%, #334fc6 46%, #2f3fa6 100%);
  color: #fff;
}

.auth-showcase::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image: radial-gradient(rgba(255, 255, 255, 0.24) 1px, transparent 1px);
  background-size: 50px 50px;
  opacity: 0.55;
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

.showcase-stats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1.4rem;
  max-width: 35rem;
  margin-top: 3rem;
}

.stat-card {
  padding: 1.6rem;
  border-radius: 1.4rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(12px);
}

.stat-card strong {
  display: block;
  font-size: 2rem;
  font-weight: 800;
}

.stat-card span {
  display: block;
  margin-top: 0.35rem;
  color: rgba(236, 242, 255, 0.86);
}

.auth-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem;
}

.auth-shell {
  width: 100%;
  max-width: 37rem;
}

.auth-alert-wrap {
  display: grid;
  gap: 0.75rem;
  margin-bottom: 1rem;
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

.auth-card {
  margin-top: 1.6rem;
  padding: 2.2rem;
  border-radius: 2rem;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(199, 210, 254, 0.7);
  box-shadow: 0 30px 80px rgba(30, 64, 175, 0.12);
  backdrop-filter: blur(14px);
}

.role-switch {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  padding: 0.35rem;
  border-radius: 1.25rem;
  background: #eef4ff;
}

.role-button {
  min-height: 3.2rem;
  border: none;
  border-radius: 1rem;
  background: transparent;
  color: #475569;
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
}

.role-button.active {
  background: #fff;
  color: #1d4ed8;
  box-shadow: 0 8px 20px rgba(41, 95, 230, 0.12);
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
    padding: 1.25rem;
    border-radius: 1.4rem;
  }

  .showcase-copy h1 {
    font-size: 2.3rem;
  }

  .showcase-stats {
    grid-template-columns: 1fr;
  }
}
</style>
