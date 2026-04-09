<template>
  <div class="relative flex min-h-screen w-full flex-col bg-[#f6f6f8] dark:bg-[#111621] text-slate-900 dark:text-slate-100">
    <EmployerHeader />
    <div class="flex flex-1">
      <EmployerSidebar />
      <main class="flex-1 p-8 overflow-y-auto">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup>
import EmployerHeader from '@/layouts/components/EmployerHeader.vue'
import EmployerSidebar from '@/layouts/components/EmployerSidebar.vue'
</script>
