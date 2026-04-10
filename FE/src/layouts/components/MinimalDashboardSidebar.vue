<script setup>
import AppLogo from '@/components/AppLogo.vue'

defineProps({
  collapsed: {
    type: Boolean,
    default: false,
  },
})
</script>

<template>
  <aside
    class="sticky top-0 flex h-screen shrink-0 flex-col border-r border-slate-200/80 bg-white/95 backdrop-blur transition-all duration-200"
    :class="collapsed ? 'w-24' : 'w-64'"
  >
    <div class="flex items-center gap-3 px-6 pb-4 pt-6" :class="collapsed ? 'justify-center' : ''">
      <AppLogo :show-text="!collapsed" size="sm" title="SmartJob AI" subtitle="Candidate" />
    </div>

    <nav class="flex-1 space-y-1 overflow-y-auto px-3">
      <RouterLink to="/skills" class="nav-link flex items-center gap-3 rounded-lg px-3 py-2 font-medium text-slate-600 transition-colors hover:bg-slate-100" :class="collapsed ? 'justify-center' : ''">
        <span class="material-symbols-outlined">psychology</span>
        <span v-if="!collapsed" class="text-sm">Danh sach ky nang</span>
      </RouterLink>

      <RouterLink to="/applications" active-class="active-nav" class="nav-link flex items-center gap-3 rounded-lg px-3 py-2 font-medium text-slate-600 transition-colors hover:bg-slate-100" :class="collapsed ? 'justify-center' : ''">
        <span class="material-symbols-outlined">send</span>
        <span v-if="!collapsed" class="text-sm">Theo doi don ung tuyen</span>
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
