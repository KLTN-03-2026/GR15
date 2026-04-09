<template>
  <div class="relative isolate min-h-screen overflow-hidden bg-[radial-gradient(circle_at_top_right,_rgba(37,99,235,0.18),_transparent_28%),radial-gradient(circle_at_bottom_left,_rgba(14,165,233,0.14),_transparent_30%),linear-gradient(180deg,#f8fbff_0%,#eff6ff_42%,#f8fafc_100%)]">
    <div class="absolute inset-0 bg-[linear-gradient(rgba(148,163,184,0.1)_1px,transparent_1px),linear-gradient(90deg,rgba(148,163,184,0.1)_1px,transparent_1px)] bg-[size:34px_34px] opacity-50"></div>

    <div class="relative mx-auto flex min-h-screen max-w-7xl items-center px-4 py-10 md:px-8">
      <div class="grid w-full gap-8 lg:grid-cols-[0.95fr_1.05fr]">
        <section class="rounded-[32px] border border-white/70 bg-white/90 p-6 shadow-[0_24px_70px_rgba(148,163,184,0.28)] backdrop-blur-xl sm:p-8 lg:p-10">
          <div class="mx-auto max-w-md">
            <div class="mb-8">
              <div class="mb-4 inline-flex size-14 items-center justify-center rounded-2xl bg-[#2463eb] text-white shadow-lg shadow-[#2463eb]/25">
                <span class="material-symbols-outlined text-[28px]">person_add</span>
              </div>
              <p class="text-sm font-semibold uppercase tracking-[0.3em] text-slate-500">
                Đăng ký
              </p>
              <h2 class="mt-3 text-3xl font-black tracking-tight text-slate-950">
                Tạo tài khoản ứng viên
              </h2>
              <p class="mt-2 text-sm leading-6 text-slate-500">
                Tạo hồ sơ để tìm việc nhanh hơn, lưu công việc phù hợp và nhận đề xuất từ AI.
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

            <form class="space-y-5" @submit.prevent="handleRegister">
              <div>
                <label class="mb-2 block text-sm font-semibold text-slate-700">Họ và tên</label>
                <input
                  v-model="registerForm.fullName"
                  type="text"
                  placeholder="Nguyễn Văn A"
                  :disabled="isLoading"
                  :class="[
                    'w-full rounded-2xl border bg-white px-4 py-3.5 text-sm text-slate-900 outline-none transition',
                    registerErrors.fullName
                      ? 'border-rose-400 ring-4 ring-rose-100'
                      : 'border-slate-200 focus:border-[#2463eb] focus:ring-4 focus:ring-blue-100',
                  ]"
                />
                <p v-if="registerErrors.fullName" class="mt-2 text-xs font-medium text-rose-600">
                  {{ registerErrors.fullName }}
                </p>
              </div>

              <div class="grid gap-5 sm:grid-cols-2">
                <div>
                  <label class="mb-2 block text-sm font-semibold text-slate-700">Email</label>
                  <input
                    v-model="registerForm.email"
                    type="email"
                    placeholder="ban@example.com"
                    :disabled="isLoading"
                    :class="[
                      'w-full rounded-2xl border bg-white px-4 py-3.5 text-sm text-slate-900 outline-none transition',
                      registerErrors.email
                        ? 'border-rose-400 ring-4 ring-rose-100'
                        : 'border-slate-200 focus:border-[#2463eb] focus:ring-4 focus:ring-blue-100',
                    ]"
                  />
                  <p v-if="registerErrors.email" class="mt-2 text-xs font-medium text-rose-600">
                    {{ registerErrors.email }}
                  </p>
                </div>

                <div>
                  <label class="mb-2 block text-sm font-semibold text-slate-700">Số điện thoại</label>
                  <input
                    v-model="registerForm.phone"
                    type="tel"
                    placeholder="0901234567"
                    :disabled="isLoading"
                    :class="[
                      'w-full rounded-2xl border bg-white px-4 py-3.5 text-sm text-slate-900 outline-none transition',
                      registerErrors.phone
                        ? 'border-rose-400 ring-4 ring-rose-100'
                        : 'border-slate-200 focus:border-[#2463eb] focus:ring-4 focus:ring-blue-100',
                    ]"
                  />
                  <p v-if="registerErrors.phone" class="mt-2 text-xs font-medium text-rose-600">
                    {{ registerErrors.phone }}
                  </p>
                </div>
              </div>

              <div>
                <label class="mb-2 block text-sm font-semibold text-slate-700">Mật khẩu</label>
                <div class="relative">
                  <input
                    v-model="registerForm.password"
                    :type="showPassword ? 'text' : 'password'"
                    placeholder="Tạo mật khẩu"
                    :disabled="isLoading"
                    :class="[
                      'w-full rounded-2xl border bg-white px-4 py-3.5 pr-12 text-sm text-slate-900 outline-none transition',
                      registerErrors.password
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
                <p v-if="registerErrors.password" class="mt-2 text-xs font-medium text-rose-600">
                  {{ registerErrors.password }}
                </p>
              </div>

              <label class="inline-flex items-start gap-3 text-sm leading-6 text-slate-600">
                <input type="checkbox" checked class="mt-1 size-4 rounded border-slate-300 text-[#2463eb] focus:ring-[#2463eb]" />
                Tôi đồng ý với điều khoản sử dụng và chính sách bảo mật của nền tảng.
              </label>

              <button
                type="submit"
                :disabled="isLoading"
                class="inline-flex w-full items-center justify-center gap-3 rounded-2xl bg-[#2463eb] px-4 py-4 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
              >
                <span v-if="!isLoading" class="inline-flex items-center gap-2">
                  <span class="material-symbols-outlined text-[20px]">how_to_reg</span>
                  Tạo tài khoản
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
                <span class="mx-4 text-sm text-slate-400">Hoặc đăng ký với</span>
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
          </div>
        </section>

        <section class="hidden overflow-hidden rounded-[32px] bg-slate-950 text-white shadow-[0_30px_80px_rgba(15,23,42,0.35)] lg:flex lg:flex-col lg:justify-between">
          <div class="relative px-10 py-12">
            <div class="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(56,189,248,0.22),_transparent_26%),radial-gradient(circle_at_bottom_right,_rgba(37,99,235,0.18),_transparent_30%)]"></div>
            <div class="relative space-y-8">
              <div class="inline-flex items-center gap-3 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-200 backdrop-blur">
                <span class="material-symbols-outlined text-sky-300">verified</span>
                Hồ sơ ứng viên chuyên nghiệp
              </div>

              <div class="max-w-xl space-y-5">
                <p class="text-sm font-semibold uppercase tracking-[0.35em] text-sky-300/90">
                  Bắt đầu ngay hôm nay
                </p>
                <h1 class="text-5xl font-black leading-tight tracking-tight">
                  Tạo tài khoản để mở khóa cơ hội phù hợp hơn.
                </h1>
                <p class="text-base leading-7 text-slate-300">
                  Hoàn thiện hồ sơ, nhận gợi ý việc làm, theo dõi khoảng trống kỹ năng và quản lý toàn bộ quá trình ứng tuyển trên một nền tảng.
                </p>
              </div>

              <div class="space-y-4">
                <article
                  v-for="item in registerBenefits"
                  :key="item.title"
                  class="flex items-start gap-4 rounded-3xl border border-white/10 bg-white/5 p-5 backdrop-blur"
                >
                  <div class="flex size-12 shrink-0 items-center justify-center rounded-2xl bg-sky-400/10 text-sky-300">
                    <span class="material-symbols-outlined">{{ item.icon }}</span>
                  </div>
                  <div>
                    <h2 class="text-base font-semibold">{{ item.title }}</h2>
                    <p class="mt-1 text-sm leading-6 text-slate-300">
                      {{ item.description }}
                    </p>
                  </div>
                </article>
              </div>
            </div>
          </div>

          <div class="border-t border-white/10 bg-white/5 px-10 py-6 backdrop-blur">
            <p class="text-sm text-slate-300">
              Đã có tài khoản?
              <RouterLink to="/login" class="ml-2 font-semibold text-sky-300 hover:text-sky-200">
                Đăng nhập tại đây
              </RouterLink>
            </p>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { authService } from '@/services/api'

const router = useRouter()
const isLoading = ref(false)
const showPassword = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

const registerBenefits = [
  {
    icon: 'manage_accounts',
    title: 'Hồ sơ nổi bật hơn',
    description: 'Tạo hồ sơ cá nhân để nhà tuyển dụng nhìn thấy đầy đủ năng lực và kinh nghiệm của bạn.',
  },
  {
    icon: 'tips_and_updates',
    title: 'Gợi ý phù hợp từ AI',
    description: 'Nhận việc làm phù hợp, kỹ năng cần bổ sung và định hướng phát triển ngay sau khi hoàn thiện hồ sơ.',
  },
  {
    icon: 'bookmark_added',
    title: 'Lưu và theo dõi dễ dàng',
    description: 'Lưu tin tuyển dụng, xem tiến trình ứng tuyển và quản lý mọi tương tác với nhà tuyển dụng.',
  },
]

const registerForm = reactive({
  fullName: '',
  email: '',
  phone: '',
  password: '',
})

const registerErrors = reactive({
  fullName: '',
  email: '',
  phone: '',
  password: '',
})

const validateRegister = () => {
  registerErrors.fullName = ''
  registerErrors.email = ''
  registerErrors.phone = ''
  registerErrors.password = ''

  if (!registerForm.fullName.trim()) {
    registerErrors.fullName = 'Vui lòng nhập họ và tên'
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

  return Object.values(registerErrors).every((value) => !value)
}

const handleRegister = async () => {
  if (!validateRegister()) {
    return
  }

  isLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const response = await authService.registerCandidate(
      registerForm.fullName,
      registerForm.email,
      registerForm.phone,
      registerForm.password,
    )

    if (response.success || response.message || response.data) {
      successMessage.value = 'Đăng ký thành công! Bạn có thể đăng nhập ngay bây giờ.'
      Object.assign(registerForm, {
        fullName: '',
        email: '',
        phone: '',
        password: '',
      })

      setTimeout(() => {
        router.push('/login')
      }, 1200)
    }
  } catch (error) {
    errorMessage.value = error.message || 'Đăng ký thất bại'
  } finally {
    isLoading.value = false
  }
}

const handleSocialLogin = (provider) => {
  console.log(`Đăng ký với ${provider}`)
}
</script>
