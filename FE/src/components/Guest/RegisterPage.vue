<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '@/services/api'
import { extractApiErrorMessage } from '@/utils/apiErrors'

const router = useRouter()
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const form = reactive({
  fullName: '',
  email: '',
  phone: '',
  password: '',
  confirmPassword: '',
})

const handleSubmit = async () => {
  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  if (form.password !== form.confirmPassword) {
    errorMessage.value = 'Xác nhận mật khẩu không khớp.'
    loading.value = false
    return
  }

  try {
    await authService.registerCandidate(form.fullName, form.email, form.phone, form.password)
    successMessage.value = 'Đăng ký thành công. Bạn có thể đăng nhập ngay.'
    setTimeout(() => router.push('/login'), 800)
  } catch (error) {
    errorMessage.value = extractApiErrorMessage(error, 'Đăng ký thất bại.')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="mx-auto grid min-h-[calc(100vh-140px)] max-w-6xl items-center gap-10 px-6 py-10 lg:grid-cols-2">
    <section class="rounded-[32px] bg-gradient-to-br from-blue-600 via-indigo-600 to-slate-900 px-8 py-10 text-white shadow-2xl">
      <p class="text-xs uppercase tracking-[0.35em] text-blue-100">SmartJob AI</p>
      <h1 class="mt-4 text-4xl font-bold">Tạo tài khoản để bắt đầu với AI tuyển dụng.</h1>
      <p class="mt-4 text-base leading-7 text-blue-50/90">
        Sau khi đăng ký, bạn có thể xây dựng hồ sơ, cập nhật kỹ năng, tạo matching với tin tuyển dụng và nhận báo cáo định hướng nghề nghiệp từ AI.
      </p>
    </section>

    <section class="rounded-[32px] border border-slate-200 bg-white p-8 shadow-lg">
      <p class="text-xs uppercase tracking-[0.35em] text-blue-600">Candidate Register</p>
      <h2 class="mt-3 text-3xl font-bold text-slate-900">Đăng ký ứng viên</h2>

      <div v-if="errorMessage" class="mt-5 rounded-2xl bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ errorMessage }}</div>
      <div v-if="successMessage" class="mt-5 rounded-2xl bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{{ successMessage }}</div>

      <form class="mt-6 space-y-4" @submit.prevent="handleSubmit">
        <input v-model="form.fullName" required placeholder="Họ và tên" class="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none focus:border-blue-400" />
        <input v-model="form.email" type="email" required placeholder="Email" class="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none focus:border-blue-400" />
        <input v-model="form.phone" placeholder="Số điện thoại" class="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none focus:border-blue-400" />
        <input v-model="form.password" type="password" required placeholder="Mật khẩu" class="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none focus:border-blue-400" />
        <input v-model="form.confirmPassword" type="password" required placeholder="Xác nhận mật khẩu" class="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none focus:border-blue-400" />

        <button type="submit" class="w-full rounded-2xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800 disabled:opacity-60" :disabled="loading">
          {{ loading ? 'Đang đăng ký...' : 'Tạo tài khoản' }}
        </button>
      </form>

      <p class="mt-5 text-sm text-slate-600">
        Đã có tài khoản?
        <RouterLink to="/login" class="font-semibold text-blue-600 hover:text-blue-700">Đăng nhập</RouterLink>
      </p>
    </section>
  </div>
</template>
