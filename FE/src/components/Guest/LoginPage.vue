<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { authService } from '@/services/api'
import { persistAuthSession } from '@/utils/authStorage'
import { extractApiErrorMessage } from '@/utils/apiErrors'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const errorMessage = ref('')

const form = reactive({
  email: '',
  password: '',
})

const handleSubmit = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    const response = await authService.login(form.email, form.password)
    const token = response?.data?.access_token
    const user = response?.data?.nguoi_dung
    persistAuthSession(token, user)
    await router.push(typeof route.query.redirect === 'string' ? route.query.redirect : '/dashboard')
  } catch (error) {
    errorMessage.value = extractApiErrorMessage(error, 'Đăng nhập thất bại.')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="mx-auto grid min-h-[calc(100vh-140px)] max-w-6xl items-center gap-10 px-6 py-10 lg:grid-cols-2">
    <section class="rounded-[32px] bg-gradient-to-br from-slate-900 via-blue-900 to-blue-600 px-8 py-10 text-white shadow-2xl">
      <p class="text-xs uppercase tracking-[0.35em] text-blue-200">SmartJob AI</p>
      <h1 class="mt-4 text-4xl font-bold">Đăng nhập để tiếp tục hành trình nghề nghiệp.</h1>
      <p class="mt-4 text-base leading-7 text-blue-50/90">
        Sau khi đăng nhập, bạn có thể quản lý hồ sơ ứng viên, kỹ năng cá nhân, tạo việc làm phù hợp và xem báo cáo định hướng nghề nghiệp ngay trong workspace hiện tại.
      </p>
    </section>

    <section class="rounded-[32px] border border-slate-200 bg-white p-8 shadow-lg">
      <p class="text-xs uppercase tracking-[0.35em] text-blue-600">Candidate Login</p>
      <h2 class="mt-3 text-3xl font-bold text-slate-900">Đăng nhập</h2>
      <p class="mt-3 text-sm text-slate-600">Sử dụng email và mật khẩu của tài khoản ứng viên.</p>

      <div v-if="errorMessage" class="mt-5 rounded-2xl bg-rose-50 px-4 py-3 text-sm text-rose-700">
        {{ errorMessage }}
      </div>

      <form class="mt-6 space-y-4" @submit.prevent="handleSubmit">
        <label class="block">
          <span class="mb-2 block text-sm font-medium text-slate-700">Email</span>
          <input v-model="form.email" type="email" required class="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none focus:border-blue-400" />
        </label>

        <label class="block">
          <span class="mb-2 block text-sm font-medium text-slate-700">Mật khẩu</span>
          <input v-model="form.password" type="password" required class="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none focus:border-blue-400" />
        </label>

        <button type="submit" class="w-full rounded-2xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800 disabled:opacity-60" :disabled="loading">
          {{ loading ? 'Đang đăng nhập...' : 'Đăng nhập' }}
        </button>
      </form>

      <p class="mt-5 text-sm text-slate-600">
        Chưa có tài khoản?
        <RouterLink to="/register" class="font-semibold text-blue-600 hover:text-blue-700">Đăng ký ngay</RouterLink>
      </p>
    </section>
  </div>
</template>
