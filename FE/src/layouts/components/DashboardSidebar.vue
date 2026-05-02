<script setup>
import AppLogo from '@/components/AppLogo.vue'
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
const displayRole = computed(() => currentUser.value?.ten_vai_tro || 'Job Seeker')
const avatarLetter = computed(() => displayName.value.trim().charAt(0).toUpperCase() || 'U')

onMounted(() => {
  window.addEventListener('auth-changed', syncCurrentUser)
  syncCurrentUser()
})

onBeforeUnmount(() => {
  window.removeEventListener('auth-changed', syncCurrentUser)
})

</script>

<template>
  <aside
    class="sticky top-0 flex h-screen shrink-0 flex-col border-r border-slate-200/80 bg-white/95 backdrop-blur transition-all duration-200 dark:border-slate-800 dark:bg-slate-950/90"
    :class="collapsed ? 'w-24' : 'w-64'"
  >
    <div class="flex items-center gap-3 px-6 pb-4 pt-6" :class="collapsed ? 'justify-center' : ''">
      <AppLogo
        :show-text="!collapsed"
        size="sm"
        title="AI Recruitment"
        subtitle="Candidate Space"
      />
    </div>
    <nav class="flex-1 space-y-1 overflow-y-auto px-3">
      <RouterLink to="/" class="nav-link flex items-center gap-3 rounded-lg px-3 py-2 text-slate-600 transition-colors font-medium hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'Trang chủ' : ''">
        <span class="material-symbols-outlined">home</span>
        <span v-if="!collapsed" class="text-sm">Trang chủ</span>
      </RouterLink>
      <RouterLink to="/dashboard" exact-active-class="active-nav" class="nav-link flex items-center gap-3 rounded-lg px-3 py-2 text-slate-600 transition-colors font-medium hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'Dashboard' : ''">
        <span class="material-symbols-outlined">dashboard</span>
        <span v-if="!collapsed" class="text-sm">Dashboard</span>
      </RouterLink>
      <RouterLink to="/profile" active-class="active-nav" class="nav-link flex items-center gap-3 rounded-lg px-3 py-2 text-slate-600 transition-colors font-medium hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'Hồ sơ cá nhân' : ''">
        <span class="material-symbols-outlined">account_circle</span>
        <span v-if="!collapsed" class="text-sm">Hồ sơ cá nhân</span>
      </RouterLink>
      <RouterLink to="/my-cv" active-class="active-nav" class="nav-link flex items-center gap-3 rounded-lg px-3 py-2 text-slate-600 transition-colors font-medium hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'CV của tôi' : ''">
        <span class="material-symbols-outlined">description</span>
        <span v-if="!collapsed" class="text-sm">CV của tôi</span>
      </RouterLink>
      <RouterLink to="/my-skills" active-class="active-nav" class="nav-link flex items-center gap-3 rounded-lg px-3 py-2 text-slate-600 transition-colors font-medium hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'Kỹ năng của tôi' : ''">
        <span class="material-symbols-outlined">psychology</span>
        <span v-if="!collapsed" class="text-sm">Kỹ năng của tôi</span>
      </RouterLink>
      <RouterLink to="/matched-jobs" active-class="active-nav" class="nav-link flex items-center gap-3 rounded-lg px-3 py-2 text-slate-600 transition-colors font-medium hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'Việc làm phù hợp' : ''">
        <span class="material-symbols-outlined">work</span>
        <span v-if="!collapsed" class="text-sm">Việc làm phù hợp</span>
      </RouterLink>
      <RouterLink to="/career-report" active-class="active-nav" class="nav-link flex items-center gap-3 rounded-lg px-3 py-2 text-slate-600 transition-colors font-medium hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'Career Report' : ''">
        <span class="material-symbols-outlined">insights</span>
        <span v-if="!collapsed" class="text-sm">Career Report</span>
      </RouterLink>
      <RouterLink to="/wallet" active-class="active-nav" class="nav-link flex items-center gap-3 rounded-lg px-3 py-2 text-slate-600 transition-colors font-medium hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'Ví AI' : ''">
        <span class="material-symbols-outlined">account_balance_wallet</span>
        <span v-if="!collapsed" class="text-sm">Ví AI</span>
      </RouterLink>
      <RouterLink to="/plans" active-class="active-nav" class="nav-link flex items-center gap-3 rounded-lg px-3 py-2 text-slate-600 transition-colors font-medium hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'Gói Pro' : ''">
        <span class="material-symbols-outlined">workspace_premium</span>
        <span v-if="!collapsed" class="text-sm">Gói Pro</span>
      </RouterLink>
      <RouterLink to="/payments" active-class="active-nav" class="nav-link flex items-center gap-3 rounded-lg px-3 py-2 text-slate-600 transition-colors font-medium hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'Lịch sử thanh toán' : ''">
        <span class="material-symbols-outlined">receipt_long</span>
        <span v-if="!collapsed" class="text-sm">Lịch sử thanh toán</span>
      </RouterLink>
      <RouterLink to="/applications" active-class="active-nav" class="nav-link flex items-center gap-3 rounded-lg px-3 py-2 text-slate-600 transition-colors font-medium hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'Việc đã ứng tuyển' : ''">
        <span class="material-symbols-outlined">send</span>
        <span v-if="!collapsed" class="text-sm">Việc đã ứng tuyển</span>
      </RouterLink>
      <RouterLink to="/saved-jobs" active-class="active-nav" class="nav-link flex items-center gap-3 rounded-lg px-3 py-2 text-slate-600 transition-colors font-medium hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'Tin đã lưu' : ''">
        <span class="material-symbols-outlined">bookmark</span>
        <span v-if="!collapsed" class="text-sm">Tin đã lưu</span>
      </RouterLink>
      <RouterLink to="/followed-companies" active-class="active-nav" class="nav-link flex items-center gap-3 rounded-lg px-3 py-2 text-slate-600 transition-colors font-medium hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'Công ty đã follow' : ''">
        <span class="material-symbols-outlined">apartment</span>
        <span v-if="!collapsed" class="text-sm">Công ty đã follow</span>
      </RouterLink>
      <div v-if="!collapsed" class="px-3 pb-2 pt-4 text-[10px] font-bold uppercase tracking-widest text-slate-400">AI Services</div>
      <RouterLink to="/ai-center/chatbot" active-class="active-nav" class="nav-link group flex items-center gap-3 rounded-lg px-3 py-2 text-slate-600 transition-colors font-medium hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'AI Center' : ''">
        <span class="material-symbols-outlined text-[#2463eb] group-hover:scale-110 transition-transform">auto_awesome</span>
        <span v-if="!collapsed" class="text-sm">AI Center</span>
      </RouterLink>
    </nav>
  </aside>
</template>

<style scoped>
.nav-link.active-nav {
  background-color: rgb(36 99 235 / 0.1);
  color: #2463eb;
}

.nav-link.active-nav:hover {
  background-color: rgb(36 99 235 / 0.15);
}
</style>
