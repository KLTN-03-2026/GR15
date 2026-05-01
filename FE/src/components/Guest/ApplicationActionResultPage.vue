<script setup>
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { getAuthToken } from '@/utils/authStorage'

const route = useRoute()

const actionType = computed(() => String(route.query.type || 'interview'))
const status = computed(() => String(route.query.status || 'invalid'))
const applicationId = computed(() => String(route.query.application_id || '').trim())

const targetPath = computed(() => {
  const query = applicationId.value
    ? `?highlight_application_id=${encodeURIComponent(applicationId.value)}`
    : ''

  return `/applications${query}`
})

const isAuthenticated = computed(() => Boolean(getAuthToken()))

const copy = computed(() => {
  const typeLabel = actionType.value === 'offer' ? 'offer' : 'lịch phỏng vấn'

  if (status.value === 'accepted') {
    return {
      icon: actionType.value === 'offer' ? 'workspace_premium' : 'event_available',
      tone: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-300',
      title: actionType.value === 'offer' ? 'Đã chấp nhận offer' : 'Đã xác nhận tham gia phỏng vấn',
      message: actionType.value === 'offer'
        ? 'Phản hồi của bạn đã được ghi nhận. Nhà tuyển dụng sẽ tiếp tục các bước nhận việc.'
        : 'Phản hồi của bạn đã được ghi nhận. Nhà tuyển dụng đã được thông báo realtime.',
    }
  }

  if (status.value === 'declined') {
    return {
      icon: 'cancel',
      tone: 'bg-amber-500/10 text-amber-600 dark:text-amber-300',
      title: actionType.value === 'offer' ? 'Đã từ chối offer' : 'Đã từ chối tham gia phỏng vấn',
      message: `Hệ thống đã ghi nhận phản hồi từ email cho ${typeLabel} này.`,
    }
  }

  if (status.value === 'expired') {
    return {
      icon: 'timer_off',
      tone: 'bg-rose-500/10 text-rose-600 dark:text-rose-300',
      title: 'Liên kết đã hết hạn',
      message: 'Vui lòng mở trang ứng tuyển hoặc liên hệ nhà tuyển dụng để xử lý tiếp.',
    }
  }

  if (status.value === 'locked') {
    return {
      icon: 'lock',
      tone: 'bg-slate-500/10 text-slate-600 dark:text-slate-300',
      title: 'Không thể phản hồi thêm',
      message: actionType.value === 'offer'
        ? 'Offer này đã được phản hồi hoặc không còn khả dụng.'
        : 'Đơn ứng tuyển đã chuyển sang giai đoạn xử lý tiếp theo.',
    }
  }

  if (status.value === 'missing_schedule') {
    return {
      icon: 'event_busy',
      tone: 'bg-slate-500/10 text-slate-600 dark:text-slate-300',
      title: 'Lịch không còn khả dụng',
      message: 'Lịch phỏng vấn này có thể đã được đổi hoặc hủy.',
    }
  }

  return {
    icon: 'error',
    tone: 'bg-rose-500/10 text-rose-600 dark:text-rose-300',
    title: 'Liên kết không hợp lệ',
    message: 'Liên kết email action không còn hợp lệ hoặc đã bị thay đổi.',
  }
})
</script>

<template>
  <main class="min-h-[calc(100vh-96px)] bg-slate-50 px-4 py-12 dark:bg-slate-950">
    <section class="mx-auto max-w-2xl rounded-2xl border border-slate-200 bg-white p-6 shadow-sm shadow-slate-950/5 dark:border-slate-800 dark:bg-slate-900 sm:p-8">
      <div class="flex flex-col gap-5 sm:flex-row sm:items-start">
        <div class="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl" :class="copy.tone">
          <span class="material-symbols-outlined text-[30px]">{{ copy.icon }}</span>
        </div>

        <div class="min-w-0 flex-1">
          <p class="text-xs font-black uppercase tracking-[0.2em] text-[#2463eb]">
            Kết quả phản hồi email
          </p>
          <h1 class="mt-2 text-2xl font-black tracking-tight text-slate-900 dark:text-white">
            {{ copy.title }}
          </h1>
          <p class="mt-3 text-sm leading-6 text-slate-500 dark:text-slate-300">
            {{ copy.message }}
          </p>

          <div
            v-if="applicationId"
            class="mt-5 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-300"
          >
            Mã đơn ứng tuyển: <span class="font-bold text-slate-900 dark:text-white">#{{ applicationId }}</span>
          </div>

          <div class="mt-6 flex flex-col gap-3 sm:flex-row">
            <RouterLink
              v-if="isAuthenticated"
              :to="targetPath"
              class="inline-flex items-center justify-center gap-2 rounded-xl bg-[#2463eb] px-5 py-3 text-sm font-bold text-white transition hover:bg-[#1d4ed8]"
            >
              <span class="material-symbols-outlined text-[18px]">assignment</span>
              Xem đơn ứng tuyển
            </RouterLink>
            <RouterLink
              v-else
              :to="{ path: '/login', query: { redirect: targetPath } }"
              class="inline-flex items-center justify-center gap-2 rounded-xl bg-[#2463eb] px-5 py-3 text-sm font-bold text-white transition hover:bg-[#1d4ed8]"
            >
              <span class="material-symbols-outlined text-[18px]">login</span>
              Đăng nhập để xem đơn
            </RouterLink>
            <RouterLink
              to="/"
              class="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 px-5 py-3 text-sm font-bold text-slate-600 transition hover:border-slate-300 hover:bg-slate-50 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
            >
              <span class="material-symbols-outlined text-[18px]">home</span>
              Về trang chủ
            </RouterLink>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>
