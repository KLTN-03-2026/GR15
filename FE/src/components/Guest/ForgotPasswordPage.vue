<template>
  <div
    class="relative isolate min-h-screen overflow-hidden bg-[radial-gradient(circle_at_top_left,_rgba(37,99,235,0.18),_transparent_30%),radial-gradient(circle_at_bottom_right,_rgba(14,165,233,0.16),_transparent_28%),linear-gradient(180deg,#f8fbff_0%,#eef4ff_45%,#f8fafc_100%)]"
  >
    <!-- Grid overlay -->
    <div
      class="absolute inset-0 bg-[linear-gradient(rgba(148,163,184,0.12)_1px,transparent_1px),linear-gradient(90deg,rgba(148,163,184,0.12)_1px,transparent_1px)] bg-[size:34px_34px] opacity-50"
    ></div>

    <div class="relative mx-auto flex min-h-screen max-w-7xl items-center px-4 py-10 md:px-8">
      <div class="grid w-full gap-8 lg:grid-cols-[1.05fr_0.95fr]">

        <!-- Left panel: branding -->
        <section
          class="hidden overflow-hidden rounded-[32px] bg-slate-950 text-white shadow-[0_30px_80px_rgba(15,23,42,0.35)] lg:flex lg:flex-col lg:justify-between"
        >
          <div class="relative px-10 py-12">
            <div
              class="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_rgba(56,189,248,0.22),_transparent_26%),radial-gradient(circle_at_bottom_left,_rgba(37,99,235,0.18),_transparent_32%)]"
            ></div>
            <div class="relative space-y-8">
              <RouterLink
                to="/"
                class="inline-flex items-center gap-3 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-200 backdrop-blur"
              >
                <span class="material-symbols-outlined text-sky-300">rocket_launch</span>
                SmartJob AI
              </RouterLink>

              <div class="max-w-xl space-y-5">
                <p class="text-sm font-semibold uppercase tracking-[0.35em] text-sky-300/90">
                  Lấy lại quyền truy cập
                </p>
                <h1 class="text-5xl font-black leading-tight tracking-tight">
                  Quên mật khẩu? Chúng tôi giúp bạn lấy lại ngay.
                </h1>
                <p class="text-base leading-7 text-slate-300">
                  Nhập email tài khoản để tiếp tục bước đặt lại mật khẩu an toàn qua hòm thư.
                </p>
              </div>

              <div class="grid gap-4 sm:grid-cols-2">
                <article
                  v-for="item in featureCards"
                  :key="item.title"
                  class="rounded-3xl border border-white/10 bg-white/5 p-5 backdrop-blur"
                >
                  <div
                    class="mb-4 flex size-12 items-center justify-center rounded-2xl bg-sky-400/10 text-sky-300"
                  >
                    <span class="material-symbols-outlined">{{ item.icon }}</span>
                  </div>
                  <h2 class="text-base font-semibold">{{ item.title }}</h2>
                  <p class="mt-2 text-sm leading-6 text-slate-300">{{ item.description }}</p>
                </article>
              </div>
            </div>
          </div>

          <div class="border-t border-white/10 bg-white/5 px-10 py-6 backdrop-blur">
            <p class="text-sm text-slate-300">
              "Bảo mật tài khoản là ưu tiên hàng đầu — token đặt lại mật khẩu chỉ có hiệu lực trong 60 phút."
            </p>
          </div>
        </section>

        <!-- Right panel: form -->
        <section
          class="rounded-[32px] border border-white/70 bg-white/90 p-6 shadow-[0_24px_70px_rgba(148,163,184,0.28)] backdrop-blur-xl sm:p-8 lg:p-10"
        >
          <div class="mx-auto max-w-md">
            <!-- Icon header -->
            <div class="mb-8">
              <div
                class="mb-4 inline-flex size-14 items-center justify-center rounded-2xl bg-[#2463eb] text-white shadow-lg shadow-[#2463eb]/25"
              >
                <span class="material-symbols-outlined text-[28px]">lock_reset</span>
              </div>
              <p class="text-sm font-semibold uppercase tracking-[0.3em] text-slate-500">
                Quên mật khẩu
              </p>
              <h2 class="mt-3 text-3xl font-black tracking-tight text-slate-950">
                Đặt lại mật khẩu
              </h2>
              <p class="mt-2 text-sm leading-6 text-slate-500">
                Nhập email bạn đã dùng để đăng ký. Hệ thống sẽ gửi liên kết đặt lại mật khẩu tới hộp thư.
              </p>
            </div>

            <!-- Alert messages -->
            <div v-if="errorMessage" class="mb-6 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700 flex items-center gap-2">
              <span class="material-symbols-outlined text-[18px]">error</span>
              {{ errorMessage }}
            </div>
            <div v-if="successMessage" class="mb-6 rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700 flex items-center gap-2">
              <span class="material-symbols-outlined text-[18px]">check_circle</span>
              {{ successMessage }}
            </div>

            <!-- Form -->
            <form class="space-y-5" @submit.prevent="handleForgotPassword">
              <div>
                <label class="mb-2 block text-sm font-semibold text-slate-700">Email tài khoản</label>
                <input
                  id="forgot-email"
                  v-model="forgotForm.email"
                  type="email"
                  placeholder="your@email.com"
                  :disabled="isLoading || !!successMessage"
                  :class="[
                    'w-full rounded-2xl border bg-white px-4 py-3.5 text-sm text-slate-900 outline-none transition',
                    forgotErrors.email
                      ? 'border-rose-400 ring-4 ring-rose-100'
                      : 'border-slate-200 focus:border-[#2463eb] focus:ring-4 focus:ring-blue-100',
                  ]"
                />
                <p v-if="forgotErrors.email" class="mt-2 text-xs font-medium text-rose-600">
                  {{ forgotErrors.email }}
                </p>
              </div>

              <button
                type="submit"
                :disabled="isLoading || !!successMessage"
                class="inline-flex w-full items-center justify-center gap-3 rounded-2xl bg-slate-950 px-4 py-4 text-sm font-semibold text-white transition hover:bg-[#2463eb] disabled:cursor-not-allowed disabled:opacity-60"
              >
                <span v-if="!isLoading" class="inline-flex items-center gap-2">
                  <span class="material-symbols-outlined text-[20px]">send</span>
                  Gửi liên kết đặt lại mật khẩu
                </span>
                <span v-else class="inline-flex items-center gap-2">
                  <span class="material-symbols-outlined animate-spin text-[20px]">progress_activity</span>
                  Đang gửi email...
                </span>
              </button>
            </form>

            <!-- Footer links -->
            <div class="mt-8 rounded-3xl border border-slate-200 bg-slate-50 p-5">
              <p class="text-sm font-semibold text-slate-900">Đã nhớ mật khẩu?</p>
              <p class="mt-1 text-sm leading-6 text-slate-500">
                Quay lại trang đăng nhập để tiếp tục truy cập tài khoản của bạn.
              </p>
              <RouterLink
                to="/login"
                class="mt-4 inline-flex items-center gap-2 text-sm font-bold text-[#2463eb] transition hover:text-blue-800"
              >
                Quay lại đăng nhập
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
import { authService } from '@/services/api'

const isLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const featureCards = [
  {
    icon: 'shield_lock',
    title: 'Xác minh an toàn',
    description: 'Xác minh đúng tài khoản trước khi cấp quyền đổi mật khẩu.',
  },
  {
    icon: 'bolt',
    title: 'Nhanh chóng',
    description: 'Email đặt lại được gửi ngay lập tức, kiểm tra cả hộp thư spam.',
  },
]

const forgotForm = reactive({ email: '' })
const forgotErrors = reactive({ email: '' })

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
  errorMessage.value = ''
  successMessage.value = ''
  try {
    const response = await authService.forgotPassword(forgotForm.email)
    successMessage.value =
      response?.message || 'Nếu email tồn tại, chúng tôi đã gửi liên kết đặt lại mật khẩu.'
    forgotForm.email = ''
  } catch (error) {
    errorMessage.value = error?.message || 'Không thể xử lý yêu cầu quên mật khẩu.'
  } finally {
    isLoading.value = false
  }
}
</script>
