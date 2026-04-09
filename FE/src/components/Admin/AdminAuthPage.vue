<template>
  <div class="relative isolate min-h-screen overflow-hidden bg-[radial-gradient(circle_at_top_left,_rgba(37,99,235,0.18),_transparent_30%),radial-gradient(circle_at_bottom_right,_rgba(15,23,42,0.16),_transparent_28%),linear-gradient(135deg,#f8fafc_0%,#eef2ff_40%,#e2e8f0_100%)]">
    <div class="absolute inset-0 bg-[linear-gradient(rgba(148,163,184,0.12)_1px,transparent_1px),linear-gradient(90deg,rgba(148,163,184,0.12)_1px,transparent_1px)] bg-[size:36px_36px] opacity-50"></div>

    <div class="relative mx-auto flex min-h-screen w-full max-w-7xl items-center px-4 py-10 md:px-8">
      <div class="grid w-full gap-8 lg:grid-cols-[1.15fr_0.85fr]">
        <section class="hidden rounded-[32px] border border-white/60 bg-slate-950 px-8 py-10 text-white shadow-[0_30px_80px_rgba(15,23,42,0.35)] lg:flex lg:flex-col lg:justify-between">
          <div class="space-y-8">
            <div class="inline-flex w-fit items-center gap-3 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-200 backdrop-blur">
              <span class="material-symbols-outlined text-lg text-sky-300">admin_panel_settings</span>
              Trung tâm điều hành quản trị
            </div>

            <div class="max-w-2xl space-y-5">
              <p class="text-sm font-semibold uppercase tracking-[0.35em] text-sky-300/90">
                Khu vực quản trị
              </p>
              <h1 class="text-5xl font-black leading-tight tracking-tight">
                Đăng nhập để kiểm soát toàn bộ nền tảng tuyển dụng.
              </h1>
              <p class="max-w-xl text-base leading-7 text-slate-300">
                Truy cập khu vực dành riêng cho quản trị viên để theo dõi vận hành hệ thống, phê duyệt doanh nghiệp và quản lý dữ liệu quan trọng.
              </p>
            </div>
          </div>

          <div class="grid gap-4 md:grid-cols-3">
            <article
              v-for="item in securityHighlights"
              :key="item.title"
              class="rounded-3xl border border-white/10 bg-white/5 p-5 backdrop-blur"
            >
              <div class="mb-4 flex size-12 items-center justify-center rounded-2xl bg-sky-400/10 text-sky-300">
                <span class="material-symbols-outlined">{{ item.icon }}</span>
              </div>
              <h2 class="text-base font-semibold">{{ item.title }}</h2>
              <p class="mt-2 text-sm leading-6 text-slate-300">
                {{ item.description }}
              </p>
            </article>
          </div>
        </section>

        <section class="rounded-[32px] border border-white/70 bg-white/85 p-6 shadow-[0_24px_70px_rgba(148,163,184,0.28)] backdrop-blur-xl sm:p-8 lg:p-10">
          <div class="mx-auto max-w-md">
            <div class="mb-8 flex items-start justify-between gap-4">
              <div>
                <div class="mb-4 inline-flex size-14 items-center justify-center rounded-2xl bg-slate-950 text-white shadow-lg shadow-slate-900/20">
                  <span class="material-symbols-outlined text-[28px]">security</span>
                </div>
                <p class="text-sm font-semibold uppercase tracking-[0.3em] text-slate-500">
                  Đăng nhập quản trị
                </p>
                <h2 class="mt-3 text-3xl font-black tracking-tight text-slate-950">
                  Chào mừng trở lại
                </h2>
                <p class="mt-2 text-sm leading-6 text-slate-500">
                  Đăng nhập bằng tài khoản quản trị để truy cập bảng điều khiển hệ thống.
                </p>
              </div>
              <div class="hidden rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2 text-right sm:block">
                <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Trạng thái</p>
                <p class="mt-1 text-sm font-semibold text-emerald-600">Bảo mật cao</p>
              </div>
            </div>

            <div v-if="errorMessage" class="mb-6 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
              {{ errorMessage }}
            </div>

            <form class="space-y-5" @submit.prevent="handleLogin">
              <div>
                <label class="mb-2 block text-sm font-semibold text-slate-700">Email quản trị</label>
                <input
                  v-model="loginForm.email"
                  type="email"
                  placeholder="admin@company.com"
                  :disabled="isLoading"
                  :class="[
                    'w-full rounded-2xl border bg-white px-4 py-3.5 text-sm text-slate-900 outline-none transition',
                    loginErrors.email
                      ? 'border-rose-400 ring-4 ring-rose-100'
                      : 'border-slate-200 focus:border-sky-500 focus:ring-4 focus:ring-sky-100',
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
                    placeholder="Nhap mat khau quan tri"
                    :disabled="isLoading"
                    :class="[
                      'w-full rounded-2xl border bg-white px-4 py-3.5 pr-12 text-sm text-slate-900 outline-none transition',
                      loginErrors.password
                        ? 'border-rose-400 ring-4 ring-rose-100'
                        : 'border-slate-200 focus:border-sky-500 focus:ring-4 focus:ring-sky-100',
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
              <button
                type="submit"
                :disabled="isLoading || !isFormValid"
                class="inline-flex w-full items-center justify-center gap-3 rounded-2xl bg-slate-950 px-4 py-4 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
              >
                <span v-if="!isLoading" class="inline-flex items-center gap-2">
                  <span class="material-symbols-outlined text-[20px]">login</span>
                  Truy cập bảng điều khiển
                </span>
                <span v-else class="inline-flex items-center gap-2">
                  <span class="material-symbols-outlined animate-spin text-[20px]">progress_activity</span>
                  Đang xác thực...
                </span>
              </button>
            </form>

            <div class="mt-8 rounded-3xl border border-slate-200 bg-slate-50 p-5">
              <div class="flex items-start gap-4">
                <div class="flex size-11 shrink-0 items-center justify-center rounded-2xl bg-sky-100 text-sky-700">
                  <span class="material-symbols-outlined">info</span>
                </div>
                <div>
                  <h3 class="text-sm font-semibold text-slate-900">Lưu ý đăng nhập quản trị</h3>
                  <p class="mt-1 text-sm leading-6 text-slate-600">
                    Khu vực này dành cho tài khoản nội bộ. Nếu bạn đăng nhập với vai trò ứng viên hoặc doanh nghiệp, vui lòng sử dụng cổng đăng nhập tương ứng.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
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

const securityHighlights = [
  {
    icon: 'shield_lock',
    title: 'Kiểm soát truy cập',
    description: 'Chỉ tài khoản quản trị được cấp quyền mới có thể đăng nhập vào khu vực này.',
  },
  {
    icon: 'monitoring',
    title: 'Theo dõi hệ thống',
    description: 'Quản lý người dùng, doanh nghiệp, bài đăng và số liệu nền tảng tại một nơi.',
  },
  {
    icon: 'verified_user',
    title: 'Phiên làm việc an toàn',
    description: 'Thông tin xác thực được lưu phiên cục bộ để hỗ trợ quản trị thuận tiện hơn.',
  },
]

const isFormValid = computed(() => Object.values(loginErrors).every((value) => !value))

onMounted(() => {
  const savedEmail = localStorage.getItem('admin_email')
  if (savedEmail) {
    loginForm.email = savedEmail
  }
})

const validateLogin = () => {
  loginErrors.email = ''
  loginErrors.password = ''

  if (!loginForm.email.trim()) {
    loginErrors.email = 'Vui lòng nhập email quản trị'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(loginForm.email)) {
    loginErrors.email = 'Email không hợp lệ'
  }

  if (!loginForm.password) {
    loginErrors.password = 'Vui lòng nhập mật khẩu'
  } else if (loginForm.password.length < 6) {
    loginErrors.password = 'Mật khẩu phải có ít nhất 6 ký tự'
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
    const response = await authService.loginAdmin(loginForm.email, loginForm.password)
    const payload = response.data || {}
    const token = payload.access_token || response.access_token || response.token
    const admin = payload.nguoi_dung || response.admin || response.user || null
    const role = payload.vai_tro ?? admin?.ten_vai_tro ?? admin?.vai_tro

    const isAdmin =
      role === 2 ||
      role === '2' ||
      String(role || '').toLowerCase() === 'admin'

    if (!isAdmin) {
      if (token && typeof admin?.id !== 'undefined') {
        localStorage.removeItem('access_token')
        localStorage.removeItem('admin_user')
      }
      throw new Error('Tài khoản này không có quyền truy cập trang quản trị.')
    }

    if (token) {
      localStorage.setItem('access_token', token)
    }

    if (admin) {
      localStorage.setItem('admin_user', JSON.stringify(admin))
    }

    localStorage.setItem('user_role', String(role))

    if (loginForm.rememberMe) {
      localStorage.setItem('admin_email', loginForm.email)
    } else {
      localStorage.removeItem('admin_email')
    }

    router.push('/admin')
  } catch (error) {
    localStorage.removeItem('access_token')
    localStorage.removeItem('admin_user')
    localStorage.removeItem('user_role')
    errorMessage.value = error.message || 'Đăng nhập quản trị thất bại'
  } finally {
    isLoading.value = false
  }
}
</script>
