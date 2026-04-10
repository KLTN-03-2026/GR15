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

        <!-- Left branding panel -->
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
                  Thiết lập mật khẩu mới
                </p>
                <h1 class="text-5xl font-black leading-tight tracking-tight">
                  Mật khẩu mới an toàn, bảo vệ tài khoản của bạn.
                </h1>
                <p class="text-base leading-7 text-slate-300">
                  Xác nhận đúng email, token và mật khẩu mới để tiếp tục quay lại hệ thống.
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
              "Sau khi hoàn tất, hệ thống sẽ tự động đưa bạn về trang đăng nhập."
            </p>
          </div>
        </section>

        <!-- Right form panel -->
        <section
          class="rounded-[32px] border border-white/70 bg-white/90 p-6 shadow-[0_24px_70px_rgba(148,163,184,0.28)] backdrop-blur-xl sm:p-8 lg:p-10"
        >
          <div class="mx-auto max-w-md">
            <!-- Icon header -->
            <div class="mb-8">
              <div
                class="mb-4 inline-flex size-14 items-center justify-center rounded-2xl bg-[#2463eb] text-white shadow-lg shadow-[#2463eb]/25"
              >
                <span class="material-symbols-outlined text-[28px]">key</span>
              </div>
              <p class="text-sm font-semibold uppercase tracking-[0.3em] text-slate-500">
                Đặt lại mật khẩu
              </p>
              <h2 class="mt-3 text-3xl font-black tracking-tight text-slate-950">
                Mật khẩu mới
              </h2>
              <p class="mt-2 text-sm leading-6 text-slate-500">
                Điền đầy đủ thông tin bên dưới để cập nhật mật khẩu mới cho tài khoản.
              </p>
            </div>

            <!-- Invalid link warning -->
            <div
              v-if="!hasValidResetLink"
              class="mb-6 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-700 flex items-center gap-2"
            >
              <span class="material-symbols-outlined text-[18px]">warning</span>
              Liên kết không hợp lệ. Vui lòng quay lại bước quên mật khẩu để nhận liên kết mới.
            </div>

            <!-- Alert messages -->
            <div v-if="errorMessage" class="mb-6 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700 flex items-center gap-2">
              <span class="material-symbols-outlined text-[18px]">error</span>
              {{ errorMessage }}
            </div>
            <div v-if="successMessage" class="mb-6 rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700 flex items-center gap-2">
              <span class="material-symbols-outlined text-[18px]">check_circle</span>
              {{ successMessage }} Đang chuyển về trang đăng nhập...
            </div>

            <!-- Form -->
            <form class="space-y-5" @submit.prevent="handleResetPassword">
              <!-- Email (readonly if from link) -->
              <div>
                <label class="mb-2 block text-sm font-semibold text-slate-700">Email tài khoản</label>
                <input
                  id="reset-email"
                  v-model="resetForm.email"
                  type="email"
                  placeholder="your@email.com"
                  :disabled="isLoading || hasValidResetLink"
                  :class="[
                    'w-full rounded-2xl border bg-white px-4 py-3.5 text-sm text-slate-900 outline-none transition',
                    resetErrors.email
                      ? 'border-rose-400 ring-4 ring-rose-100'
                      : 'border-slate-200 focus:border-[#2463eb] focus:ring-4 focus:ring-blue-100',
                    hasValidResetLink ? 'bg-slate-50 text-slate-500 cursor-not-allowed' : '',
                  ]"
                />
                <p v-if="resetErrors.email" class="mt-2 text-xs font-medium text-rose-600">
                  {{ resetErrors.email }}
                </p>
              </div>

              <!-- New password -->
              <div>
                <label class="mb-2 block text-sm font-semibold text-slate-700">Mật khẩu mới</label>
                <div class="relative">
                  <input
                    id="reset-password"
                    v-model="resetForm.password"
                    :type="showPassword ? 'text' : 'password'"
                    placeholder="Ít nhất 6 ký tự"
                    :disabled="isLoading"
                    :class="[
                      'w-full rounded-2xl border bg-white px-4 py-3.5 pr-12 text-sm text-slate-900 outline-none transition',
                      resetErrors.password
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
                <p v-if="resetErrors.password" class="mt-2 text-xs font-medium text-rose-600">
                  {{ resetErrors.password }}
                </p>
              </div>

              <!-- Confirm password -->
              <div>
                <label class="mb-2 block text-sm font-semibold text-slate-700">Xác nhận mật khẩu mới</label>
                <div class="relative">
                  <input
                    id="reset-confirm-password"
                    v-model="resetForm.confirmPassword"
                    :type="showConfirmPassword ? 'text' : 'password'"
                    placeholder="Nhập lại mật khẩu mới"
                    :disabled="isLoading"
                    :class="[
                      'w-full rounded-2xl border bg-white px-4 py-3.5 pr-12 text-sm text-slate-900 outline-none transition',
                      resetErrors.confirmPassword
                        ? 'border-rose-400 ring-4 ring-rose-100'
                        : 'border-slate-200 focus:border-[#2463eb] focus:ring-4 focus:ring-blue-100',
                    ]"
                  />
                  <button
                    type="button"
                    class="absolute right-3 top-1/2 inline-flex -translate-y-1/2 items-center justify-center rounded-xl p-2 text-slate-500 transition hover:bg-slate-100 hover:text-slate-700"
                    @click="showConfirmPassword = !showConfirmPassword"
                  >
                    <span class="material-symbols-outlined text-[20px]">
                      {{ showConfirmPassword ? 'visibility_off' : 'visibility' }}
                    </span>
                  </button>
                </div>
                <p v-if="resetErrors.confirmPassword" class="mt-2 text-xs font-medium text-rose-600">
                  {{ resetErrors.confirmPassword }}
                </p>
              </div>

              <button
                type="submit"
                :disabled="isLoading || !hasValidResetLink"
                class="inline-flex w-full items-center justify-center gap-3 rounded-2xl bg-slate-950 px-4 py-4 text-sm font-semibold text-white transition hover:bg-[#2463eb] disabled:cursor-not-allowed disabled:opacity-60"
              >
                <span v-if="!isLoading" class="inline-flex items-center gap-2">
                  <span class="material-symbols-outlined text-[20px]">lock_reset</span>
                  Lưu mật khẩu mới
                </span>
                <span v-else class="inline-flex items-center gap-2">
                  <span class="material-symbols-outlined animate-spin text-[20px]">progress_activity</span>
                  Đang cập nhật...
                </span>
              </button>
            </form>

            <!-- Footer links -->
            <div class="mt-8 rounded-3xl border border-slate-200 bg-slate-50 p-5">
              <p class="text-sm font-semibold text-slate-900">Muốn quay lại bước trước?</p>
              <p class="mt-1 text-sm leading-6 text-slate-500">
                Nếu không nhận được email, hãy thử lại từ bước quên mật khẩu.
              </p>
              <RouterLink
                to="/forgot-password"
                class="mt-4 inline-flex items-center gap-2 text-sm font-bold text-[#2463eb] transition hover:text-blue-800"
              >
                Quên mật khẩu
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
import { reactive, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { authService } from '@/services/api'

const route = useRoute()
const router = useRouter()
const isLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const hasValidResetLink = ref(false)

const featureCards = [
  {
    icon: 'key',
    title: 'Thay thế hoàn toàn',
    description: 'Mật khẩu mới sẽ thay thế hoàn toàn mật khẩu cũ, tất cả phiên đăng nhập cũ sẽ bị thu hồi.',
  },
  {
    icon: 'verified_user',
    title: 'Xác thực token',
    description: 'Token đặt lại mật khẩu có thời hạn 60 phút kể từ khi gửi email.',
  },
]

const resetForm = reactive({ email: '', token: '', password: '', confirmPassword: '' })
const resetErrors = reactive({ email: '', password: '', confirmPassword: '' })

// Tự động đọc email + token từ query string trong URL email
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
  if (!resetForm.email.trim()) resetErrors.email = 'Vui lòng nhập email'
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(resetForm.email)) resetErrors.email = 'Email không hợp lệ'
  if (!resetForm.password) resetErrors.password = 'Vui lòng nhập mật khẩu mới'
  else if (resetForm.password.length < 6) resetErrors.password = 'Mật khẩu phải có ít nhất 6 ký tự'
  if (!resetForm.confirmPassword) resetErrors.confirmPassword = 'Vui lòng xác nhận mật khẩu'
  else if (resetForm.confirmPassword !== resetForm.password)
    resetErrors.confirmPassword = 'Mật khẩu xác nhận không khớp'
  return Object.values(resetErrors).every((err) => !err)
}

const handleResetPassword = async () => {
  if (!hasValidResetLink.value) {
    errorMessage.value = 'Liên kết đặt lại mật khẩu không hợp lệ.'
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
    }, 1500)
  } catch (error) {
    errorMessage.value = error?.message || 'Không thể đặt lại mật khẩu. Token có thể đã hết hạn.'
  } finally {
    isLoading.value = false
  }
}
</script>
