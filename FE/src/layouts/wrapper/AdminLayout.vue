<script setup>
import { ref } from 'vue'
import AdminSidebar from '@/layouts/components/AdminSidebar.vue'
import AdminHeader from '@/layouts/components/AdminHeader.vue'

const sidebarCollapsed = ref(false)
</script>

<template>
  <div class="flex min-h-screen bg-[radial-gradient(circle_at_top,_rgba(36,99,235,0.08),_transparent_28%),linear-gradient(180deg,_#f8fafc_0%,_#f3f5fb_100%)] dark:bg-[#111621] text-slate-900 dark:text-slate-100">
    <AdminSidebar :collapsed="sidebarCollapsed" />
    <main class="flex-1 flex flex-col min-w-0">
      <AdminHeader :sidebar-collapsed="sidebarCollapsed" @toggle-sidebar="sidebarCollapsed = !sidebarCollapsed" />
      <div class="space-y-8 px-4 py-6 sm:px-6 xl:px-8">
        <slot />
      </div>
    </main>
  </div>
</template>
