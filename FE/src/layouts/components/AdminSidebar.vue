<script setup>
import AppLogo from '@/components/AppLogo.vue'
import { RouterLink } from 'vue-router'

defineProps({
  collapsed: {
    type: Boolean,
    default: false,
  },
})
</script>

<template>
  <aside
    class="sticky top-0 flex h-screen flex-col border-r border-slate-200/80 bg-white/95 backdrop-blur dark:border-slate-800 dark:bg-slate-950/90 transition-all duration-200"
    :class="collapsed ? 'w-24' : 'w-64'"
  >
    <div class="flex items-center gap-3 p-6" :class="collapsed ? 'justify-center' : ''">
      <AppLogo
        :show-text="!collapsed"
        size="sm"
        title="AI Recruitment"
        subtitle="Management Console"
      />
    </div>
    <nav class="flex-1 space-y-1 px-4">
      <RouterLink to="/admin" exact-active-class="active-nav" class="nav-link flex items-center gap-3 rounded-xl px-3 py-2.5 text-slate-600 transition-colors font-medium hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'Tổng quan' : ''">
        <span class="material-symbols-outlined text-[22px]">dashboard</span>
        <span v-if="!collapsed" class="text-sm">Tổng quan</span>
      </RouterLink>
      <RouterLink to="/admin/users" active-class="active-nav" class="nav-link flex items-center gap-3 rounded-xl px-3 py-2.5 text-slate-600 transition-colors font-medium hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'Người dùng' : ''">
        <span class="material-symbols-outlined text-[22px]">group</span>
        <span v-if="!collapsed" class="text-sm">Người dùng</span>
      </RouterLink>
      <RouterLink to="/admin/companies" active-class="active-nav" class="nav-link flex items-center gap-3 rounded-xl px-3 py-2.5 text-slate-600 transition-colors font-medium hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'Công ty' : ''">
        <span class="material-symbols-outlined text-[22px]">domain</span>
        <span v-if="!collapsed" class="text-sm">Công ty</span>
      </RouterLink>
      <RouterLink to="/admin/profiles" active-class="active-nav" class="nav-link flex items-center gap-3 rounded-xl px-3 py-2.5 text-slate-600 transition-colors font-medium hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'Hồ sơ' : ''">
        <span class="material-symbols-outlined text-[22px]">description</span>
        <span v-if="!collapsed" class="text-sm">Hồ sơ</span>
      </RouterLink>
      <RouterLink to="/admin/user-skills" active-class="active-nav" class="nav-link flex items-center gap-3 rounded-xl px-3 py-2.5 text-slate-600 transition-colors font-medium hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'Kỹ năng người dùng' : ''">
        <span class="material-symbols-outlined text-[22px]">psychology</span>
        <span v-if="!collapsed" class="text-sm">Kỹ năng người dùng</span>
      </RouterLink>
      <RouterLink to="/admin/matchings" active-class="active-nav" class="nav-link flex items-center gap-3 rounded-xl px-3 py-2.5 text-slate-600 transition-colors font-medium hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'AI Matching' : ''">
        <span class="material-symbols-outlined text-[22px]">compare_arrows</span>
        <span v-if="!collapsed" class="text-sm">AI Matching</span>
      </RouterLink>
      <RouterLink to="/admin/career-advising" active-class="active-nav" class="nav-link flex items-center gap-3 rounded-xl px-3 py-2.5 text-slate-600 transition-colors font-medium hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'AI Advising' : ''">
        <span class="material-symbols-outlined text-[22px]">travel_explore</span>
        <span v-if="!collapsed" class="text-sm">AI Advising</span>
      </RouterLink>
      <RouterLink to="/admin/applications" active-class="active-nav" class="nav-link flex items-center gap-3 rounded-xl px-3 py-2.5 text-slate-600 transition-colors font-medium hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'Ứng tuyển' : ''">
        <span class="material-symbols-outlined text-[22px]">assignment</span>
        <span v-if="!collapsed" class="text-sm">Ứng tuyển</span>
      </RouterLink>
      <RouterLink to="/admin/skills" active-class="active-nav" class="nav-link flex items-center gap-3 rounded-xl px-3 py-2.5 text-slate-600 transition-colors font-medium hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'Kỹ năng' : ''">
        <span class="material-symbols-outlined text-[22px]">bolt</span>
        <span v-if="!collapsed" class="text-sm">Kỹ năng</span>
      </RouterLink>
      <RouterLink to="/admin/industries" active-class="active-nav" class="nav-link flex items-center gap-3 rounded-xl px-3 py-2.5 text-slate-600 transition-colors font-medium hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'Ngành nghề' : ''">
        <span class="material-symbols-outlined text-[22px]">factory</span>
        <span v-if="!collapsed" class="text-sm">Ngành nghề</span>
      </RouterLink>
      <RouterLink to="/admin/jobs" active-class="active-nav" class="nav-link flex items-center gap-3 rounded-xl px-3 py-2.5 text-slate-600 transition-colors font-medium hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'Tin tuyển dụng' : ''">
        <span class="material-symbols-outlined text-[22px]">work</span>
        <span v-if="!collapsed" class="text-sm">Tin tuyển dụng</span>
      </RouterLink>
      <RouterLink to="/admin/stats" active-class="active-nav" class="nav-link flex items-center gap-3 rounded-xl px-3 py-2.5 text-slate-600 transition-colors font-medium hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'Thống kê' : ''">
        <span class="material-symbols-outlined text-[22px]">leaderboard</span>
        <span v-if="!collapsed" class="text-sm">Thống kê</span>
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
