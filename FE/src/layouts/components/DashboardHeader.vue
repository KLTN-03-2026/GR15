<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useNotify } from '@/composables/useNotify'
import { getStoredCandidate } from '@/utils/authStorage'

const props = defineProps({
  sidebarCollapsed: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['toggle-sidebar'])

const router = useRouter()
const searchKeyword = ref('')
const profileMenuOpen = ref(false)
const profileMenuRef = ref(null)
const { logout, isLoading } = useAuth()
const notify = useNotify()

const currentUser = computed(() => getStoredCandidate())
const displayName = computed(() => currentUser.value?.ho_ten || 'Ung vien')
const displayRole = computed(() => currentUser.value?.ten_vai_tro || 'Candidate')
const avatarLetter = computed(() => displayName.value.trim().charAt(0).toUpperCase() || 'U')

const submitSearch = () => {
  const keyword = searchKeyword.value.trim()
  router.push(keyword ? `/skills?search=${encodeURIComponent(keyword)}` : '/skills')
}

const toggleProfileMenu = () => {
  profileMenuOpen.value = !profileMenuOpen.value
}

const closeProfileMenu = () => {
  profileMenuOpen.value = false
}

const goToApplications = () => {
  closeProfileMenu()
  router.push('/applications')
}

const handleLogout = async () => {
  closeProfileMenu()
  try {
    await logout()
    notify.success('Dang xuat thanh cong.')
  } catch (error) {
    notify.apiError(error, 'Khong the dang xuat khoi he thong.')
  }
}

const handleClickOutside = (event) => {
  if (!profileMenuRef.value?.contains(event.target)) {
    closeProfileMenu()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <header class="sticky top-0 z-20 flex h-20 shrink-0 items-center justify-between border-b border-slate-200/80 bg-white/85 px-4 backdrop-blur-md dark:border-slate-800 dark:bg-slate-950/80 sm:px-6 xl:px-8">
    <div class="flex flex-1 items-center gap-4">
      <button
        class="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl border border-slate-200 bg-white text-slate-600 shadow-sm transition hover:border-slate-300 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800"
        type="button"
        :title="props.sidebarCollapsed ? 'Mo rong sidebar' : 'Thu gon sidebar'"
        @click="$emit('toggle-sidebar')"
      >
        <span class="material-symbols-outlined text-[20px]">
          {{ props.sidebarCollapsed ? 'right_panel_open' : 'left_panel_close' }}
        </span>
      </button>
      <form class="relative w-full max-w-xl" @submit.prevent="submitSearch">
        <span class="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 text-xl">search</span>
        <input
          v-model="searchKeyword"
          class="h-12 w-full rounded-2xl border border-slate-200 bg-white pl-12 pr-4 text-sm text-slate-700 shadow-sm outline-none transition focus:border-[#2463eb] focus:ring-4 focus:ring-[#2463eb]/10 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
          placeholder="Tim ky nang..."
          type="text"
        />
      </form>
    </div>
    <div class="ml-6 flex items-center gap-3">
      <button
        class="inline-flex h-10 w-10 items-center justify-center rounded-2xl border border-slate-200 bg-white text-slate-600 transition hover:border-slate-300 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800"
        type="button"
        title="Mo trang theo doi don ung tuyen"
        @click="router.push('/applications')"
      >
        <span class="material-symbols-outlined">assignment</span>
      </button>
      <div class="mx-1 h-8 w-px bg-slate-200 dark:bg-slate-800"></div>
      <div ref="profileMenuRef" class="relative">
        <button
          class="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white px-3 py-2 text-left shadow-sm transition hover:border-slate-300 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 dark:hover:bg-slate-800"
          type="button"
          @click.stop="toggleProfileMenu"
        >
          <div class="flex h-10 w-10 items-center justify-center rounded-2xl bg-[#2463eb]/10 text-sm font-black text-[#2463eb]">
            {{ avatarLetter }}
          </div>
          <div class="hidden min-w-0 sm:block">
            <p class="truncate text-sm font-semibold text-slate-900 dark:text-white">{{ displayName }}</p>
            <p class="truncate text-xs uppercase tracking-[0.18em] text-slate-400">{{ displayRole }}</p>
          </div>
          <span class="material-symbols-outlined text-slate-400 text-[18px]">expand_more</span>
        </button>

        <div
          v-if="profileMenuOpen"
          class="absolute right-0 mt-3 w-56 overflow-hidden rounded-2xl border border-slate-200 bg-white p-2 shadow-xl dark:border-slate-700 dark:bg-slate-900"
        >
          <button
            class="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm font-medium text-slate-700 transition hover:bg-slate-50 dark:text-slate-200 dark:hover:bg-slate-800"
            type="button"
            @click="goToApplications"
          >
            <span class="material-symbols-outlined text-[18px]">assignment</span>
            Theo doi don ung tuyen
          </button>
          <button
            class="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm font-medium text-red-600 transition hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-500/10"
            :disabled="isLoading"
            type="button"
            @click="handleLogout"
          >
            <span class="material-symbols-outlined text-[18px]">logout</span>
            {{ isLoading ? 'Dang dang xuat...' : 'Dang xuat' }}
          </button>
        </div>
      </div>
    </div>
  </header>
</template>
