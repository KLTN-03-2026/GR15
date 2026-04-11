<script setup>
import { computed, ref } from 'vue'
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
const { logout, isLoading } = useAuth()
const notify = useNotify()

const currentUser = computed(() => getStoredCandidate())
const displayName = computed(() => currentUser.value?.ho_ten || 'Ứng viên')
const avatarLetter = computed(() => displayName.value.trim().charAt(0).toUpperCase() || 'U')

const submitSearch = () => {
  const keyword = searchKeyword.value.trim()
  router.push(keyword ? `/jobs?search=${encodeURIComponent(keyword)}` : '/jobs')
}

const handleLogout = async () => {
  profileMenuOpen.value = false
  try {
    await logout()
    notify.success('Đăng xuất thành công.')
  } catch (error) {
    notify.apiError(error, 'Không thể đăng xuất.')
  }
}
</script>

<template>
  <header class="sticky top-0 z-20 flex h-20 items-center justify-between border-b border-slate-200 bg-white/90 px-4 backdrop-blur sm:px-6">
    <div class="flex flex-1 items-center gap-4">
      <button
        type="button"
        class="inline-flex h-11 w-11 items-center justify-center rounded-2xl border border-slate-200 bg-white text-slate-600 shadow-sm transition hover:bg-slate-50"
        :title="props.sidebarCollapsed ? 'Mở rộng sidebar' : 'Thu gọn sidebar'"
        @click="$emit('toggle-sidebar')"
      >
        <span class="material-symbols-outlined">{{ props.sidebarCollapsed ? 'right_panel_open' : 'left_panel_close' }}</span>
      </button>

      <form class="relative w-full max-w-xl" @submit.prevent="submitSearch">
        <span class="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-slate-400">search</span>
        <input
          v-model="searchKeyword"
          class="h-12 w-full rounded-2xl border border-slate-200 bg-white pl-12 pr-4 text-sm text-slate-700 outline-none transition focus:border-[#2463eb] focus:ring-4 focus:ring-[#2463eb]/10"
          placeholder="Tìm nhanh việc làm..."
          type="text"
        />
      </form>
    </div>

    <div class="relative ml-5">
      <button
        type="button"
        class="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white px-3 py-2 shadow-sm transition hover:bg-slate-50"
        @click="profileMenuOpen = !profileMenuOpen"
      >
        <div class="flex h-10 w-10 items-center justify-center rounded-2xl bg-[#2463eb]/10 font-black text-[#2463eb]">
          {{ avatarLetter }}
        </div>
        <div class="hidden text-left sm:block">
          <p class="max-w-[180px] truncate text-sm font-bold text-slate-900">{{ displayName }}</p>
          <p class="text-xs uppercase tracking-[0.2em] text-slate-400">Ứng viên</p>
        </div>
        <span class="material-symbols-outlined text-slate-400">expand_more</span>
      </button>

      <div v-if="profileMenuOpen" class="absolute right-0 mt-3 w-56 rounded-2xl border border-slate-200 bg-white p-2 shadow-xl">
        <button class="menu-item" type="button" @click="router.push('/profile'); profileMenuOpen = false">
          <span class="material-symbols-outlined text-[18px]">account_circle</span>
          Hồ sơ cá nhân
        </button>
        <button class="menu-item" type="button" @click="router.push('/my-cv'); profileMenuOpen = false">
          <span class="material-symbols-outlined text-[18px]">description</span>
          Quản lý CV
        </button>
        <button class="menu-item text-rose-600 hover:bg-rose-50" :disabled="isLoading" type="button" @click="handleLogout">
          <span class="material-symbols-outlined text-[18px]">logout</span>
          {{ isLoading ? 'Đang đăng xuất...' : 'Đăng xuất' }}
        </button>
      </div>
    </div>
  </header>
</template>

<style scoped>
.menu-item {
  display: flex;
  width: 100%;
  align-items: center;
  gap: 0.75rem;
  border-radius: 0.9rem;
  padding: 0.75rem 0.85rem;
  text-align: left;
  font-size: 0.92rem;
  font-weight: 600;
  color: #334155;
  transition: 0.2s ease;
}

.menu-item:hover {
  background: #f8fafc;
}
</style>
