<template>
  <div class="relative isolate min-h-screen overflow-hidden bg-[radial-gradient(circle_at_top_left,_rgba(37,99,235,0.18),_transparent_30%),radial-gradient(circle_at_bottom_right,_rgba(14,165,233,0.16),_transparent_28%),linear-gradient(180deg,#f8fbff_0%,#eef4ff_45%,#f8fafc_100%)]">
    <div class="absolute inset-0 bg-[linear-gradient(rgba(148,163,184,0.12)_1px,transparent_1px),linear-gradient(90deg,rgba(148,163,184,0.12)_1px,transparent_1px)] bg-[size:34px_34px] opacity-50"></div>

    <div class="relative mx-auto flex min-h-screen max-w-7xl items-center px-4 py-10 md:px-8">
      <div class="grid w-full gap-8 lg:grid-cols-[1.05fr_0.95fr]">
        <section class="hidden overflow-hidden rounded-[32px] bg-slate-950 text-white shadow-[0_30px_80px_rgba(15,23,42,0.35)] lg:flex lg:flex-col lg:justify-between">
          <div class="relative px-10 py-12">
            <div class="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_rgba(56,189,248,0.22),_transparent_26%),radial-gradient(circle_at_bottom_left,_rgba(37,99,235,0.18),_transparent_32%)]"></div>
            <div class="relative space-y-8">
              <div class="inline-flex items-center gap-3 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-200 backdrop-blur">
                <span class="material-symbols-outlined text-sky-300">rocket_launch</span>
                Cổng ứng viên AI Recruitment
              </div>

              <div class="max-w-xl space-y-5">
                <p class="text-sm font-semibold uppercase tracking-[0.35em] text-sky-300/90">
                  Đăng nhập thông minh
                </p>
                <h1 class="text-5xl font-black leading-tight tracking-tight">
                  Quay lại hành trình tìm việc phù hợp với bạn.
                </h1>
                <p class="text-base leading-7 text-slate-300">
                  Đăng nhập để theo dõi việc làm phù hợp, cập nhật hồ sơ, nhận gợi ý nghề nghiệp và quản lý các lần ứng tuyển tại một nơi.
                </p>
              </div>

              <div class="grid gap-4 sm:grid-cols-3">
                <article
                  v-for="item in featureCards"
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
            </div>
          </div>

          <div class="border-t border-white/10 bg-white/5 px-10 py-6 backdrop-blur">
            <p class="text-sm text-slate-300">
              “Mỗi lần đăng nhập là một bước tiến gần hơn tới cơ hội phù hợp nhất.”
            </p>
          </div>
        </section>

        <section class="rounded-[32px] border border-white/70 bg-white/90 p-6 shadow-[0_24px_70px_rgba(148,163,184,0.28)] backdrop-blur-xl sm:p-8 lg:p-10">
          <div class="mx-auto max-w-md">
            <div class="mb-8">
              <div class="mb-4 inline-flex size-14 items-center justify-center rounded-2xl bg-[#2463eb] text-white shadow-lg shadow-[#2463eb]/25">
                <span class="material-symbols-outlined text-[28px]">login</span>
              </div>
              <p class="text-sm font-semibold uppercase tracking-[0.3em] text-slate-500">
                Đăng nhập
              </p>
              <h2 class="mt-3 text-3xl font-black tracking-tight text-slate-950">
                Chào mừng trở lại
              </h2>
              <p class="mt-2 text-sm leading-6 text-slate-500">
                Đăng nhập bằng tài khoản ứng viên để tiếp tục tìm kiếm cơ hội phù hợp.
              </p>
            </div>

            <div v-if="errorMessage || successMessage" class="mb-6 space-y-3">
              <div v-if="errorMessage" class="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
                {{ errorMessage }}
              </div>
              <div v-if="successMessage" class="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
                {{ successMessage }}
              </div>
            </div>

            <form class="space-y-5" @submit.prevent="handleLogin">
              <div>
                <label class="mb-2 block text-sm font-semibold text-slate-700">Email</label>
                <input
                  v-model="loginForm.email"
                  type="email"
                  placeholder="ban@example.com"
                  :disabled="isLoading"
                  :class="[
                    'w-full rounded-2xl border bg-white px-4 py-3.5 text-sm text-slate-900 outline-none transition',
                    loginErrors.email
                      ? 'border-rose-400 ring-4 ring-rose-100'
                      : 'border-slate-200 focus:border-[#2463eb] focus:ring-4 focus:ring-blue-100',
                  ]"
                />
                <p v-if="loginErrors.email" class="mt-2 text-xs font-medium text-rose-600">
                  {{ loginErrors.email }}
                </p>
              </div>

              <div>
                <div class="mb-2 flex items-center justify-between gap-3">
                  <label class="block text-sm font-semibold text-slate-700">Mật khẩu</label>
                  <button type="button" class="text-sm font-semibold text-[#2463eb] transition hover:text-blue-800">
                    Quên mật khẩu?
                  </button>
                </div>
                <div class="relative">
                  <input
                    v-model="loginForm.password"
                    :type="showPassword ? 'text' : 'password'"
                    placeholder="Nhập mật khẩu"
                    :disabled="isLoading"
                    :class="[
                      'w-full rounded-2xl border bg-white px-4 py-3.5 pr-12 text-sm text-slate-900 outline-none transition',
                      loginErrors.password
                        ? 'border-rose-400 ring-4 ring-rose-100'
                        : 'border-slate-200 focus:border-[#2463eb] focus:ring-4 focus:ring-blue-100',
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
                  class="size-4 rounded border-slate-300 text-[#2463eb] focus:ring-[#2463eb]"
                />
                Ghi nhớ đăng nhập
              </label>

              <button
                type="submit"
                :disabled="isLoading"
                class="inline-flex w-full items-center justify-center gap-3 rounded-2xl bg-slate-950 px-4 py-4 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
              >
                <span v-if="!isLoading" class="inline-flex items-center gap-2">
                  <span class="material-symbols-outlined text-[20px]">arrow_forward</span>
                  Đăng nhập tài khoản
                </span>
                <span v-else class="inline-flex items-center gap-2">
                  <span class="material-symbols-outlined animate-spin text-[20px]">progress_activity</span>
                  Đang xử lý...
                </span>
              </button>
            </form>

            <div class="mt-8">
              <div class="relative flex items-center py-5">
                <div class="flex-grow border-t border-slate-200"></div>
                <span class="mx-4 text-sm text-slate-400">Hoặc tiếp tục với</span>
                <div class="flex-grow border-t border-slate-200"></div>
              </div>

              <div class="grid grid-cols-2 gap-4">
                <button
                  type="button"
                  @click="handleSocialLogin('google')"
                  :disabled="isLoading"
                  class="flex items-center justify-center gap-2 rounded-2xl border border-slate-200 py-3 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:opacity-50"
                >
                  <svg class="h-5 w-5" viewBox="0 0 24 24">
                    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"></path>
                    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"></path>
                    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05"></path>
                    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"></path>
                  </svg>
                  Google
                </button>
                <button
                  type="button"
                  @click="handleSocialLogin('facebook')"
                  :disabled="isLoading"
                  class="flex items-center justify-center gap-2 rounded-2xl border border-slate-200 py-3 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:opacity-50"
                >
                  <svg class="h-5 w-5" fill="#1877F2" viewBox="0 0 24 24">
                    <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"></path>
                  </svg>
                  Facebook
                </button>
              </div>
            </div>

            <div class="mt-8 rounded-3xl border border-slate-200 bg-slate-50 p-5">
              <p class="text-sm font-semibold text-slate-900">Chưa có tài khoản?</p>
              <p class="mt-1 text-sm leading-6 text-slate-500">
                Tạo tài khoản ứng viên để lưu việc làm, cập nhật CV và nhận đề xuất từ AI.
              </p>
              <RouterLink
                to="/register"
                class="mt-4 inline-flex items-center gap-2 text-sm font-bold text-[#2463eb] transition hover:text-blue-800"
              >
                Đăng ký ngay
                <span class="material-symbols-outlined text-[18px]">arrow_forward</span>
              </RouterLink>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { RouterLink } from 'vue-router'

const isLoading = ref(false)
const showPassword = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const featureCards = [
  {
    icon: 'manage_search',
    title: 'Theo dõi việc làm',
    description: 'Quản lý các cơ hội đã lưu, việc làm phù hợp và tiến trình ứng tuyển ở cùng một nơi.',
  },
  {
    icon: 'auto_awesome',
    title: 'Gợi ý từ AI',
    description: 'Nhận đề xuất nghề nghiệp và kỹ năng cần cải thiện dựa trên hồ sơ thực tế của bạn.',
  },
  {
    icon: 'description',
    title: 'Hồ sơ sẵn sàng',
    description: 'Cập nhật CV, thông tin cá nhân và chuẩn bị hồ sơ để ứng tuyển nhanh hơn.',
  },
]

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

  return Object.values(loginErrors).every((value) => !value)
}

const handleLogin = () => {
  if (!validateLogin()) {
    successMessage.value = ''
    return
  }

  errorMessage.value = ''
  successMessage.value = 'Đây là bản giao diện mẫu. Form đăng nhập hiện không kết nối backend.'
}

const handleSocialLogin = (provider) => {
  errorMessage.value = ''
  successMessage.value = `Đăng nhập với ${provider} đang được tắt trong bản UI-only.`
}
</script>
