<script setup>
import { ref } from 'vue'
import EmployerHeader from '@/layouts/components/EmployerHeader.vue'
import EmployerSidebar from '@/layouts/components/EmployerSidebar.vue'

const sidebarCollapsed = ref(false)
</script>

<template>
  <div
    class="flex min-h-screen bg-[radial-gradient(circle_at_top,_rgba(36,99,235,0.08),_transparent_28%),linear-gradient(180deg,_#f8fafc_0%,_#f3f5fb_100%)] dark:bg-[#111621] text-slate-900 dark:text-slate-100"
  >
    <EmployerSidebar :collapsed="sidebarCollapsed" />
    <main class="flex min-w-0 flex-1 flex-col">
      <EmployerHeader :sidebar-collapsed="sidebarCollapsed" @toggle-sidebar="sidebarCollapsed = !sidebarCollapsed" />
      <div class="flex-1 overflow-y-auto px-4 py-6 sm:px-6 xl:px-8">
        <div class="mx-auto max-w-7xl">
          <slot />
        </div>
      </div>
    </main>
  </div>
</template>
