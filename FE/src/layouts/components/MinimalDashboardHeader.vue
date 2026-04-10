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
const profileMenuOpen = ref(false)
const profileMenuRef = ref(null)
const { logout, isLoading } = useAuth()
const notify = useNotify()

const currentUser = computed(() => getStoredCandidate())
const displayName = computed(() => currentUser.value?.ho_ten || 'Ung vien')
const avatarLetter = computed(() => displayName.value.trim().charAt(0).toUpperCase() || 'U')

const closeProfileMenu = () => {
  profileMenuOpen.value = false
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
  <header class="sticky top-0 z-20 flex h-20 shrink-0 items-center justify-between border-b border-slate-200/80 bg-white/90 px-4 backdrop-blur-md sm:px-6 xl:px-8">
    <div class="flex flex-1 items-center gap-4">
      <button
        class="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl border border-slate-200 bg-white text-slate-600 shadow-sm transition hover:border-slate-300 hover:bg-slate-50"
        type="button"
        :title="props.sidebarCollapsed ? 'Mo rong sidebar' : 'Thu gon sidebar'"
        @click="$emit('toggle-sidebar')"
      >
        <span class="material-symbols-outlined text-[20px]">
          {{ props.sidebarCollapsed ? 'right_panel_open' : 'left_panel_close' }}
        </span>
      </button>

      <div>
        <p class="text-xs font-bold uppercase tracking-[0.28em] text-[#2463eb]">Candidate Portal</p>
        <h1 class="text-lg font-bold text-slate-900">Theo doi don ung tuyen</h1>
      </div>
    </div>

    <div ref="profileMenuRef" class="relative">
      <button
        class="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white px-3 py-2 text-left shadow-sm transition hover:border-slate-300 hover:bg-slate-50"
        type="button"
        @click.stop="profileMenuOpen = !profileMenuOpen"
      >
        <div class="flex h-10 w-10 items-center justify-center rounded-2xl bg-[#2463eb]/10 text-sm font-black text-[#2463eb]">
          {{ avatarLetter }}
        </div>
        <div class="hidden min-w-0 sm:block">
          <p class="truncate text-sm font-semibold text-slate-900">{{ displayName }}</p>
          <p class="truncate text-xs uppercase tracking-[0.18em] text-slate-400">Ung vien</p>
        </div>
        <span class="material-symbols-outlined text-[18px] text-slate-400">expand_more</span>
      </button>

      <div
        v-if="profileMenuOpen"
        class="absolute right-0 mt-3 w-56 overflow-hidden rounded-2xl border border-slate-200 bg-white p-2 shadow-xl"
      >
        <button
          class="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm font-medium text-slate-700 transition hover:bg-slate-50"
          type="button"
          @click="router.push('/skills'); closeProfileMenu()"
        >
          <span class="material-symbols-outlined text-[18px]">psychology</span>
          Danh sach ky nang
        </button>
        <button
          class="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm font-medium text-red-600 transition hover:bg-red-50"
          :disabled="isLoading"
          type="button"
          @click="handleLogout"
        >
          <span class="material-symbols-outlined text-[18px]">logout</span>
          {{ isLoading ? 'Dang dang xuat...' : 'Dang xuat' }}
        </button>
      </div>
    </div>
  </header>
</template>
