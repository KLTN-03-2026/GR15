<script setup>
import AppLogo from '@/components/AppLogo.vue'
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { getStoredEmployer } from '@/utils/authStorage'

defineProps({
  collapsed: {
    type: Boolean,
    default: false,
  },
})

const companyLabel = computed(() => {
  const employer = getStoredEmployer()
  return employer?.ho_ten || employer?.email || 'Nhà tuyển dụng'
})

const companyLetter = computed(() => companyLabel.value.trim().charAt(0).toUpperCase() || 'N')
</script>

<template>
  <aside
    class="sticky top-0 hidden h-screen shrink-0 flex-col border-r border-slate-200/80 bg-white/95 backdrop-blur transition-all duration-200 dark:border-slate-800 dark:bg-slate-950/90 lg:flex"
    :class="collapsed ? 'w-24' : 'w-64'"
  >
    <div class="flex items-center gap-3 px-6 pb-4 pt-6" :class="collapsed ? 'justify-center' : ''">
      <AppLogo
        :show-text="!collapsed"
        size="sm"
        title="AI Recruitment"
        subtitle="Employer Space"
      />
    </div>

    <nav class="flex-1 space-y-1 overflow-y-auto px-3">
      <RouterLink to="/" class="nav-link flex items-center gap-3 rounded-lg px-3 py-2 text-slate-600 transition-colors font-medium hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'Trang chủ' : ''">
        <span class="material-symbols-outlined">home</span>
        <span v-if="!collapsed" class="text-sm">Trang chủ</span>
      </RouterLink>
      <RouterLink to="/employer" exact-active-class="active-nav" class="nav-link flex items-center gap-3 rounded-lg px-3 py-2 text-slate-600 transition-colors font-medium hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'Dashboard' : ''">
        <span class="material-symbols-outlined">dashboard</span>
        <span v-if="!collapsed" class="text-sm">Dashboard</span>
      </RouterLink>
      <RouterLink to="/employer/jobs" active-class="active-nav" class="nav-link flex items-center gap-3 rounded-lg px-3 py-2 text-slate-600 transition-colors font-medium hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'Tin tuyển dụng' : ''">
        <span class="material-symbols-outlined">work</span>
        <span v-if="!collapsed" class="text-sm">Tin tuyển dụng</span>
      </RouterLink>
      <RouterLink to="/employer/candidates" active-class="active-nav" class="nav-link flex items-center gap-3 rounded-lg px-3 py-2 text-slate-600 transition-colors font-medium hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'Ứng viên' : ''">
        <span class="material-symbols-outlined">group</span>
        <span v-if="!collapsed" class="text-sm">Ứng viên</span>
      </RouterLink>
      <RouterLink to="/employer/interviews" active-class="active-nav" class="nav-link flex items-center gap-3 rounded-lg px-3 py-2 text-slate-600 transition-colors font-medium hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'Phỏng vấn' : ''">
        <span class="material-symbols-outlined">calendar_today</span>
        <span v-if="!collapsed" class="text-sm">Phỏng vấn</span>
      </RouterLink>
      <RouterLink to="/employer/company" active-class="active-nav" class="nav-link flex items-center gap-3 rounded-lg px-3 py-2 text-slate-600 transition-colors font-medium hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'Công ty' : ''">
        <span class="material-symbols-outlined">domain</span>
        <span v-if="!collapsed" class="text-sm">Công ty</span>
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
