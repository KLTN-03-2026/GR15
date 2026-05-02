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
        subtitle="Admin Console"
      />
    </div>
    <nav class="flex-1 space-y-1 px-4">
      <RouterLink to="/admin/users" active-class="active-nav" class="nav-link flex items-center gap-3 rounded-xl px-3 py-2.5 text-slate-600 transition-colors font-medium hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'Quan ly nguoi dung' : ''">
        <span class="material-symbols-outlined text-[22px]">group</span>
        <span v-if="!collapsed" class="text-sm">Quan ly nguoi dung</span>
      </RouterLink>
      <RouterLink to="/admin/companies" active-class="active-nav" class="nav-link flex items-center gap-3 rounded-xl px-3 py-2.5 text-slate-600 transition-colors font-medium hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'Quan ly cong ty' : ''">
        <span class="material-symbols-outlined text-[22px]">domain</span>
        <span v-if="!collapsed" class="text-sm">Quan ly cong ty</span>
      </RouterLink>
      <RouterLink to="/admin/profiles" active-class="active-nav" class="nav-link flex items-center gap-3 rounded-xl px-3 py-2.5 text-slate-600 transition-colors font-medium hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'Quan ly ho so' : ''">
        <span class="material-symbols-outlined text-[22px]">description</span>
        <span v-if="!collapsed" class="text-sm">Quan ly ho so</span>
      </RouterLink>
      <RouterLink to="/admin/user-skills" active-class="active-nav" class="nav-link flex items-center gap-3 rounded-xl px-3 py-2.5 text-slate-600 transition-colors font-medium hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'Quan ly ky nang nguoi dung' : ''">
        <span class="material-symbols-outlined text-[22px]">psychology</span>
        <span v-if="!collapsed" class="text-sm">Quan ly ky nang nguoi dung</span>
      </RouterLink>
      <RouterLink to="/admin/applications" active-class="active-nav" class="nav-link flex items-center gap-3 rounded-xl px-3 py-2.5 text-slate-600 transition-colors font-medium hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'Theo doi don ung tuyen' : ''">
        <span class="material-symbols-outlined text-[22px]">assignment</span>
        <span v-if="!collapsed" class="text-sm">Theo doi don ung tuyen</span>
      </RouterLink>
      <RouterLink to="/admin/skills" active-class="active-nav" class="nav-link flex items-center gap-3 rounded-xl px-3 py-2.5 text-slate-600 transition-colors font-medium hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'Danh sach ky nang' : ''">
        <span class="material-symbols-outlined text-[22px]">bolt</span>
        <span v-if="!collapsed" class="text-sm">Danh sach ky nang</span>
      </RouterLink>
      <RouterLink to="/admin/stats" active-class="active-nav" class="nav-link flex items-center gap-3 rounded-xl px-3 py-2.5 text-slate-600 transition-colors font-medium hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'Quan ly thong ke' : ''">
        <span class="material-symbols-outlined text-[22px]">leaderboard</span>
        <span v-if="!collapsed" class="text-sm">Quan ly thong ke</span>
      </RouterLink>
      <RouterLink to="/admin/audit-logs" active-class="active-nav" class="nav-link flex items-center gap-3 rounded-xl px-3 py-2.5 text-slate-600 transition-colors font-medium hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'Nhat ky he thong' : ''">
        <span class="material-symbols-outlined text-[22px]">history</span>
        <span v-if="!collapsed" class="text-sm">Nhat ky he thong</span>
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
