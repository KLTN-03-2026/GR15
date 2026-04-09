<template>
  <div class="flex min-h-screen items-center justify-center px-4 py-10">
    <div class="grid w-full max-w-5xl overflow-hidden rounded-[32px] border border-slate-200 bg-white shadow-[0_30px_80px_rgba(15,23,42,0.12)] lg:grid-cols-[1.05fr_0.95fr]">
      <section class="hidden bg-[linear-gradient(160deg,#0f172a_0%,#1d4ed8_100%)] p-10 text-white lg:flex lg:flex-col lg:justify-between">
        <div>
          <div class="inline-flex items-center gap-3 rounded-full border border-white/15 bg-white/10 px-4 py-2 text-sm">
            <span class="material-symbols-outlined text-lg">business_center</span>
            Cổng doanh nghiệp
          </div>
          <h1 class="mt-8 text-4xl font-black leading-tight">
            Quay lại trung tâm tuyển dụng của doanh nghiệp.
          </h1>
          <p class="mt-4 max-w-lg text-sm leading-7 text-slate-200">
            Theo dõi tin đăng, quản lý ứng viên và điều phối phỏng vấn trong một không gian làm việc thống nhất.
          </p>
        </div>

        <div class="grid gap-4 sm:grid-cols-3">
          <div class="rounded-3xl border border-white/15 bg-white/10 p-4">
            <p class="text-2xl font-black">24/7</p>
            <p class="mt-1 text-sm text-slate-200">Quan ly quy trinh tuyen dung lien tuc</p>
          </div>
          <div class="rounded-3xl border border-white/15 bg-white/10 p-4">
            <p class="text-2xl font-black">1 nơi</p>
            <p class="mt-1 text-sm text-slate-200">Tổng hợp bài đăng, hồ sơ và lịch phỏng vấn</p>
          </div>
          <div class="rounded-3xl border border-white/15 bg-white/10 p-4">
            <p class="text-2xl font-black">Bảo mật</p>
            <p class="mt-1 text-sm text-slate-200">Chỉ dành cho tài khoản doanh nghiệp đã xác thực</p>
          </div>
        </div>
      </section>

      <section class="p-6 sm:p-8 lg:p-10">
        <div class="mx-auto max-w-md">
          <div class="mb-8">
            <div class="mb-4 inline-flex size-14 items-center justify-center rounded-2xl bg-blue-600 text-white shadow-lg shadow-blue-600/20">
              <span class="material-symbols-outlined text-[28px]">apartment</span>
            </div>
            <h2 class="text-3xl font-black tracking-tight text-slate-950">Đăng nhập doanh nghiệp</h2>
            <p class="mt-2 text-sm leading-6 text-slate-500">
              Sử dụng tài khoản doanh nghiệp để truy cập bảng điều khiển tuyển dụng.
            </p>
          </div>

          <div v-if="errorMessage" class="mb-6 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
            {{ errorMessage }}
          </div>

          <form class="space-y-5" @submit.prevent="handleLogin">
            <div>
              <label class="mb-2 block text-sm font-semibold text-slate-700">Email doanh nghiệp</label>
              <input
                v-model="loginForm.email"
                type="email"
                :disabled="isLoading"
                placeholder="hr@company.com"
                :class="[
                  'w-full rounded-2xl border bg-white px-4 py-3.5 text-sm text-slate-900 outline-none transition',
                  loginErrors.email
                    ? 'border-rose-400 ring-4 ring-rose-100'
                    : 'border-slate-200 focus:border-blue-500 focus:ring-4 focus:ring-blue-100',
                ]"
              />
              <p v-if="loginErrors.email" class="mt-2 text-xs font-medium text-rose-600">
                {{ loginErrors.email }}
              </p>
            </div>

            <div>
              <label class="mb-2 block text-sm font-semibold text-slate-700">Mật khẩu</label>
              <div class="relative">
                <input
                  v-model="loginForm.password"
                  :type="showPassword ? 'text' : 'password'"
                  :disabled="isLoading"
                  placeholder="Nhập mật khẩu"
                  :class="[
                    'w-full rounded-2xl border bg-white px-4 py-3.5 pr-12 text-sm text-slate-900 outline-none transition',
                    loginErrors.password
                      ? 'border-rose-400 ring-4 ring-rose-100'
                      : 'border-slate-200 focus:border-blue-500 focus:ring-4 focus:ring-blue-100',
                  ]"
                />
                <button
                  type="button"
                  class="absolute right-3 top-1/2 inline-flex -translate-y-1/2 items-center justify-center rounded-xl p-2 text-slate-500 transition hover:bg-slate-100 hover:text-slate-700"
                  @click="showPassword = !showPassword"
                >
                  <span class="material-symbols-outlined text-[20px]">
                    {{ showPassword ? 'visibility_off' : 'visibility' }}
                  </span>
                </button>
              </div>
              <p v-if="loginErrors.password" class="mt-2 text-xs font-medium text-rose-600">
                {{ loginErrors.password }}
              </p>
            </div>

            <label class="inline-flex items-center gap-3 text-sm text-slate-600">
              <input
                v-model="loginForm.rememberMe"
                type="checkbox"
                class="size-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
              />
              Ghi nhớ đăng nhập
            </label>

            <button
              type="submit"
              :disabled="isLoading"
              class="inline-flex w-full items-center justify-center gap-3 rounded-2xl bg-blue-600 px-4 py-4 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              <span v-if="!isLoading" class="inline-flex items-center gap-2">
                <span class="material-symbols-outlined text-[20px]">login</span>
                Đăng nhập
              </span>
              <span v-else class="inline-flex items-center gap-2">
                <span class="material-symbols-outlined animate-spin text-[20px]">progress_activity</span>
                Đang xử lý...
              </span>
            </button>
          </form>

          <p class="mt-6 text-sm text-slate-500">
            Chưa có tài khoản?
            <router-link to="/employer/register" class="font-semibold text-blue-700 hover:text-blue-900">
              Đăng ký doanh nghiệp
            </router-link>
          </p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '@/services/api'

const router = useRouter()
const isLoading = ref(false)
const showPassword = ref(false)
const errorMessage = ref('')

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
    loginErrors.email = 'Vui lòng nhập email doanh nghiệp'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(loginForm.email)) {
    loginErrors.email = 'Email không hợp lệ'
  }

  if (!loginForm.password) {
    loginErrors.password = 'Vui lòng nhập mật khẩu'
  }

  return Object.values(loginErrors).every((value) => !value)
}

const handleLogin = async () => {
  if (!validateLogin()) {
    return
  }

  isLoading.value = true
  errorMessage.value = ''

  try {
    const response = await authService.loginEmployer(loginForm.email, loginForm.password)
    const token = response.access_token || response.token
    const employer = response.employer || response.user || null

    if (token) {
      localStorage.setItem('access_token', token)
    }

    if (employer) {
      localStorage.setItem('employer_user', JSON.stringify(employer))
    }

    router.push('/employer')
  } catch (error) {
    errorMessage.value = error.message || 'Đăng nhập doanh nghiệp thất bại'
  } finally {
    isLoading.value = false
  }
}
</script>
