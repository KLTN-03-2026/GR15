<template>
  <div class="flex min-h-screen bg-[#f6f6f8] dark:bg-[#111621] text-slate-900 dark:text-slate-100">
    <AdminSidebar />
    <main class="flex-1 flex flex-col min-w-0">
      <AdminHeader />
      <div class="p-8 space-y-8">
        <slot />
      </div>
    </main>
  </div>
</template>

<script setup>
import AdminSidebar from '@/layouts/components/AdminSidebar.vue'
import AdminHeader from '@/layouts/components/AdminHeader.vue'
</script>
