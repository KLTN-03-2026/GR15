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
    class="sticky top-0 hidden h-screen shrink-0 flex-col border-r border-slate-200/80 bg-white/95 backdrop-blur transition-all duration-200 dark:border-slate-800 dark:bg-slate-950/90 lg:flex"
    :class="collapsed ? 'w-24' : 'w-64'"
  >
    <div class="flex items-center gap-3 px-6 pb-4 pt-6" :class="collapsed ? 'justify-center' : ''">
      <AppLogo
        :show-text="!collapsed"
        size="sm"
        title="AI Recruitment"
        subtitle="Company Management"
      />
    </div>

    <nav class="flex-1 space-y-1 overflow-y-auto px-3">
      <RouterLink to="/employer/company" exact-active-class="active-nav" class="nav-link flex items-center gap-3 rounded-lg px-3 py-2 text-slate-600 transition-colors font-medium hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'Quan ly cong ty' : ''">
        <span class="material-symbols-outlined">domain</span>
        <span v-if="!collapsed" class="text-sm">Quan ly cong ty</span>
      </RouterLink>
      <RouterLink to="/employer/audit-logs" exact-active-class="active-nav" class="nav-link flex items-center gap-3 rounded-lg px-3 py-2 text-slate-600 transition-colors font-medium hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'Nhat ky cong ty' : ''">
        <span class="material-symbols-outlined">history</span>
        <span v-if="!collapsed" class="text-sm">Nhat ky cong ty</span>
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
