<template>
  <div class="flex h-screen overflow-hidden bg-[#f6f6f8] dark:bg-[#111621] text-slate-900 dark:text-slate-100">
    <DashboardSidebar />
    <main class="flex-1 flex flex-col overflow-hidden">
      <DashboardHeader />
      <div class="flex-1 overflow-y-auto p-8">
        <div class="max-w-6xl mx-auto space-y-8">
          <slot />
        </div>
        <div class="h-12"></div>
      </div>
    </main>
  </div>
</template>

<script setup>
import DashboardSidebar from '@/layouts/components/DashboardSidebar.vue'
import DashboardHeader from '@/layouts/components/DashboardHeader.vue'
</script>
