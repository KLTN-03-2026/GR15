<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useNotifications } from '@/composables/useNotifications'

const props = defineProps({
  role: {
    type: String,
    required: true,
  },
  buttonClass: {
    type: String,
    default: 'relative p-2 text-slate-600 transition hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800 rounded-full',
  },
  panelClass: {
    type: String,
    default: 'w-[360px]',
  },
  badgeClass: {
    type: String,
    default: 'border-white dark:border-slate-900',
  },
})

const containerRef = ref(null)
const open = ref(false)

const {
  items,
  loading,
  error,
  unreadCount,
  realtimeStatus,
  realtimeStatusLabel,
  isRealtimeConnected,
  refresh,
  markAsRead,
  markAllAsRead,
} = useNotifications(props.role)

const titleMap = {
  candidate: 'Thông báo ứng tuyển',
  employer: 'Thông báo tuyển dụng',
  admin: 'Thông báo vận hành',
}

const panelTitle = computed(() => titleMap[props.role] || 'Thông báo')
const realtimeStatusTone = computed(() => {
  if (isRealtimeConnected.value) return 'bg-emerald-500'
  if (['connecting', 'idle'].includes(realtimeStatus.value)) return 'bg-amber-400'
  if (realtimeStatus.value === 'disabled') return 'bg-slate-300 dark:bg-slate-600'
  return 'bg-rose-500'
})

const closePanel = () => {
  open.value = false
}

const togglePanel = async () => {
  open.value = !open.value

  if (open.value) {
    await refresh()
  }
}

const handleOutsideClick = (event) => {
  if (!open.value || !containerRef.value) return
  if (!containerRef.value.contains(event.target)) {
    closePanel()
  }
}

onMounted(() => {
  if (typeof window !== 'undefined') {
    window.addEventListener('click', handleOutsideClick)
  }
})

onUnmounted(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('click', handleOutsideClick)
  }
})
</script>

<template>
  <div ref="containerRef" class="relative">
    <button :class="buttonClass" type="button" @click.stop="togglePanel">
      <span class="material-symbols-outlined">notifications</span>
      <span
        v-if="unreadCount > 0"
        class="absolute -right-1 -top-1 inline-flex min-h-5 min-w-5 items-center justify-center rounded-full border-2 bg-rose-500 px-1 text-[10px] font-bold text-white"
        :class="badgeClass"
      >
        {{ unreadCount > 9 ? '9+' : unreadCount }}
      </span>
    </button>

    <transition
      enter-active-class="transition duration-150 ease-out"
      enter-from-class="translate-y-2 opacity-0"
      enter-to-class="translate-y-0 opacity-100"
      leave-active-class="transition duration-100 ease-in"
      leave-from-class="translate-y-0 opacity-100"
      leave-to-class="translate-y-2 opacity-0"
    >
      <div
        v-if="open"
        class="absolute right-0 top-full z-[80] mt-3 rounded-2xl border border-slate-200 bg-white shadow-xl shadow-slate-900/10 dark:border-slate-700 dark:bg-slate-900"
        :class="panelClass"
      >
        <div class="flex items-center justify-between border-b border-slate-100 px-4 py-3 dark:border-slate-800">
          <div>
            <h3 class="text-sm font-bold text-slate-900 dark:text-white">{{ panelTitle }}</h3>
            <p class="text-xs text-slate-400">
              {{ unreadCount > 0 ? `${unreadCount} thông báo chưa đọc` : 'Mọi cập nhật gần đây của bạn' }}
            </p>
            <div class="mt-2 inline-flex items-center gap-2 rounded-full bg-slate-100 px-2.5 py-1 text-[11px] font-semibold text-slate-500 dark:bg-slate-800 dark:text-slate-300">
              <span class="h-2 w-2 rounded-full" :class="realtimeStatusTone"></span>
              {{ realtimeStatusLabel }}
            </div>
          </div>
          <div class="flex items-center gap-1">
            <button
              class="inline-flex h-8 w-8 items-center justify-center rounded-lg text-slate-500 transition hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
              type="button"
              title="Tải lại"
              @click="refresh"
            >
              <span class="material-symbols-outlined text-[18px]">refresh</span>
            </button>
            <button
              class="rounded-lg px-2 py-1 text-xs font-semibold text-[#2463eb] transition hover:bg-[#2463eb]/5 disabled:cursor-not-allowed disabled:opacity-40"
              :disabled="unreadCount === 0"
              type="button"
              @click="markAllAsRead"
            >
              Đọc hết
            </button>
          </div>
        </div>

        <div v-if="loading" class="space-y-3 px-4 py-4">
          <div
            v-for="index in 3"
            :key="index"
            class="animate-pulse rounded-2xl border border-slate-100 p-3 dark:border-slate-800"
          >
            <div class="mb-2 h-4 w-2/3 rounded bg-slate-100 dark:bg-slate-800"></div>
            <div class="h-3 w-full rounded bg-slate-100 dark:bg-slate-800"></div>
          </div>
        </div>

        <div v-else-if="error" class="px-4 py-5 text-sm text-rose-500">
          {{ error }}
        </div>

        <div v-else-if="items.length === 0" class="px-4 py-8 text-center">
          <div class="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100 text-slate-400 dark:bg-slate-800">
            <span class="material-symbols-outlined">notifications_none</span>
          </div>
          <p class="text-sm font-semibold text-slate-700 dark:text-slate-200">Chưa có thông báo mới</p>
          <p class="mt-1 text-xs text-slate-400">Các cập nhật quan trọng sẽ xuất hiện tại đây.</p>
        </div>

        <div v-else class="max-h-[420px] overflow-y-auto px-3 py-3">
          <RouterLink
            v-for="item in items"
            :key="item.id"
            :to="item.to || '#'"
            class="mb-2 flex items-start gap-3 rounded-2xl border px-3 py-3 transition last:mb-0"
            :class="item.read
              ? 'border-slate-100 bg-white hover:border-slate-200 hover:bg-slate-50 dark:border-slate-800 dark:bg-slate-900 dark:hover:border-slate-700 dark:hover:bg-slate-800/80'
              : 'border-[#2463eb]/10 bg-[#2463eb]/[0.04] hover:border-[#2463eb]/20 dark:border-[#2463eb]/20 dark:bg-[#2463eb]/10 dark:hover:bg-[#2463eb]/15'"
            @click="markAsRead(item.id); closePanel()"
          >
            <div class="mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl" :class="item.tone">
              <span class="material-symbols-outlined text-[20px]">{{ item.icon }}</span>
            </div>
            <div class="min-w-0 flex-1">
              <div class="flex items-start justify-between gap-2">
                <p class="text-sm font-semibold text-slate-900 dark:text-white">{{ item.title }}</p>
                <span
                  v-if="!item.read"
                  class="mt-1 h-2.5 w-2.5 shrink-0 rounded-full bg-[#2463eb]"
                ></span>
              </div>
              <p class="mt-1 break-words text-xs leading-5 text-slate-500 dark:text-slate-400">
                {{ item.message }}
              </p>
              <p class="mt-2 text-[11px] font-medium uppercase tracking-[0.12em] text-slate-400">
                {{ item.timeLabel }}
              </p>
            </div>
          </RouterLink>
        </div>
      </div>
    </transition>
  </div>
</template>
