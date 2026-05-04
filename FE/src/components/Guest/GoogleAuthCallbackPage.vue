<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { persistAuthSession } from '@/utils/authStorage'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

const route = useRoute()
const router = useRouter()

const isLoading = ref(true)
const errorMessage = ref('')

const getHomeByRole = (role) => {
  switch (Number(role)) {
    case 1:
      return '/employer'
    case 2:
      return '/admin'
    case 0:
    default:
      return '/dashboard'
  }
}

onMounted(async () => {
  const token = typeof route.query.token === 'string' ? route.query.token : ''
  const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : ''

  if (!token) {
    errorMessage.value = 'Không nhận được thông tin đăng nhập từ Google.'
    isLoading.value = false
    return
  }

  try {
    const response = await fetch(`${API_BASE_URL}/ho-so`, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
        Authorization: `Bearer ${token}`,
      },
    })

    const payload = response.headers.get('content-type')?.includes('application/json')
      ? await response.json()
      : null

    if (!response.ok || !payload?.data) {
      throw new Error(payload?.message || 'Không thể hoàn tất đăng nhập bằng Google.')
    }

    persistAuthSession(token, payload.data)

    await router.replace(redirect || getHomeByRole(payload.data.vai_tro))
  } catch (error) {
    errorMessage.value = error?.message || 'Không thể hoàn tất đăng nhập bằng Google.'
    window.setTimeout(() => {
      void router.replace({
        path: '/login',
        query: {
          google_error: errorMessage.value,
        },
      })
    }, 1200)
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-slate-50 px-6 py-12">
    <div class="w-full max-w-md rounded-3xl border border-slate-200 bg-white px-8 py-10 text-center shadow-xl shadow-slate-200/60">
      <div
        class="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl"
        :class="isLoading ? 'bg-blue-50 text-blue-600' : 'bg-red-50 text-red-600'"
      >
        <span
          class="material-symbols-outlined text-3xl"
          :class="isLoading ? 'animate-spin' : ''"
        >
          {{ isLoading ? 'progress_activity' : 'error' }}
        </span>
      </div>

      <h1 class="mt-6 text-2xl font-black tracking-tight text-slate-900">
        {{ isLoading ? 'Đang hoàn tất đăng nhập Google' : 'Không thể đăng nhập với Google' }}
      </h1>

      <p class="mt-3 text-sm leading-7 text-slate-500">
        {{ isLoading ? 'Hệ thống đang đồng bộ phiên đăng nhập và chuyển bạn tới đúng khu vực làm việc.' : errorMessage }}
      </p>
    </div>
  </div>
</template>
