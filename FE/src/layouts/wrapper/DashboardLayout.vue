<script setup>
import { ref } from 'vue'
import DashboardSidebar from '@/layouts/components/DashboardSidebar.vue'
import DashboardHeader from '@/layouts/components/DashboardHeader.vue'

const sidebarCollapsed = ref(false)
</script>

<template>
  <div class="flex min-h-screen bg-[radial-gradient(circle_at_top,_rgba(36,99,235,0.08),_transparent_28%),linear-gradient(180deg,_#f8fafc_0%,_#f2f6ff_100%)]">
    <DashboardSidebar :collapsed="sidebarCollapsed" />
    <main class="flex min-w-0 flex-1 flex-col">
      <DashboardHeader :sidebar-collapsed="sidebarCollapsed" @toggle-sidebar="sidebarCollapsed = !sidebarCollapsed" />
      <div class="flex-1 px-4 py-6 sm:px-6 xl:px-8">
        <div class="mx-auto max-w-7xl">
          <slot />
        </div>
      </div>
    </main>
  </div>
</template>
