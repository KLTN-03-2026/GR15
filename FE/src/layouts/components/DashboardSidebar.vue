<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { getStoredCandidate } from '@/utils/authStorage'

defineProps({
  collapsed: {
    type: Boolean,
    default: false,
  },
})

const currentUser = ref(getStoredCandidate())

const syncCurrentUser = () => {
  currentUser.value = getStoredCandidate()
}

const displayName = computed(() => currentUser.value?.ho_ten || 'Ứng viên')
const avatarLetter = computed(() => displayName.value.trim().charAt(0).toUpperCase() || 'U')

onMounted(() => {
  window.addEventListener('auth-changed', syncCurrentUser)
})

onBeforeUnmount(() => {
  window.removeEventListener('auth-changed', syncCurrentUser)
})
</script>

<template>
  <aside
    class="sticky top-0 flex h-screen shrink-0 flex-col border-r border-slate-200 bg-white/95 backdrop-blur"
    :class="collapsed ? 'w-24' : 'w-72'"
  >
    <div class="border-b border-slate-200 px-5 py-6">
      <RouterLink to="/" class="flex items-center gap-3" :class="collapsed ? 'justify-center' : ''">
        <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-[#2463eb] text-white shadow-lg shadow-blue-200/60">
          <span class="material-symbols-outlined">rocket_launch</span>
        </div>
        <div v-if="!collapsed">
          <p class="text-lg font-black tracking-tight text-slate-900">AI Recruitment</p>
          <p class="text-xs font-semibold uppercase tracking-[0.25em] text-slate-400">Candidate Space</p>
        </div>
      </RouterLink>
    </div>

    <div class="border-b border-slate-200 px-5 py-5" :class="collapsed ? 'text-center' : ''">
      <div class="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-[#2463eb]/10 text-lg font-black text-[#2463eb]">
        {{ avatarLetter }}
      </div>
      <div v-if="!collapsed" class="mt-3">
        <p class="truncate font-bold text-slate-900">{{ displayName }}</p>
        <p class="text-sm text-slate-500">Khu vực ứng viên</p>
      </div>
    </div>

    <nav class="flex-1 space-y-2 px-3 py-4">
      <RouterLink to="/dashboard" class="nav-link" :class="collapsed ? 'justify-center' : ''">
        <span class="material-symbols-outlined">space_dashboard</span>
        <span v-if="!collapsed">Dashboard ứng viên</span>
      </RouterLink>
      <RouterLink to="/" class="nav-link" :class="collapsed ? 'justify-center' : ''">
        <span class="material-symbols-outlined">home</span>
        <span v-if="!collapsed">Trang chủ</span>
      </RouterLink>
      <RouterLink to="/jobs" class="nav-link" :class="collapsed ? 'justify-center' : ''">
        <span class="material-symbols-outlined">work</span>
        <span v-if="!collapsed">Danh sách việc làm</span>
      </RouterLink>
      <RouterLink to="/profile" class="nav-link" :class="collapsed ? 'justify-center' : ''">
        <span class="material-symbols-outlined">account_circle</span>
        <span v-if="!collapsed">Profile ứng viên</span>
      </RouterLink>
      <RouterLink to="/my-cv" class="nav-link" :class="collapsed ? 'justify-center' : ''">
        <span class="material-symbols-outlined">description</span>
        <span v-if="!collapsed">Quản lý CV</span>
      </RouterLink>
      <RouterLink to="/saved-jobs" class="nav-link" :class="collapsed ? 'justify-center' : ''">
        <span class="material-symbols-outlined">bookmark</span>
        <span v-if="!collapsed">Việc làm đã lưu</span>
      </RouterLink>
      <RouterLink to="/matched-jobs" class="nav-link" :class="collapsed ? 'justify-center' : ''">
        <span class="material-symbols-outlined">recommend</span>
        <span v-if="!collapsed">Việc làm phù hợp</span>
      </RouterLink>
      <RouterLink to="/applications" class="nav-link" :class="collapsed ? 'justify-center' : ''">
        <span class="material-symbols-outlined">send</span>
        <span v-if="!collapsed">Theo dõi ứng tuyển</span>
      </RouterLink>
      <RouterLink to="/my-skills" class="nav-link" :class="collapsed ? 'justify-center' : ''">
        <span class="material-symbols-outlined">psychology</span>
        <span v-if="!collapsed">Kỹ năng cá nhân</span>
      </RouterLink>
      <RouterLink to="/career-report" class="nav-link" :class="collapsed ? 'justify-center' : ''">
        <span class="material-symbols-outlined">insights</span>
        <span v-if="!collapsed">Career Report</span>
      </RouterLink>
    </nav>
  </aside>
</template>

<style scoped>
.nav-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  border-radius: 1rem;
  padding: 0.85rem 0.95rem;
  color: #475569;
  font-size: 0.95rem;
  font-weight: 700;
  transition: 0.2s ease;
}

.nav-link:hover,
.router-link-active.nav-link {
  background: rgba(36, 99, 235, 0.1);
  color: #2463eb;
}
</style>
