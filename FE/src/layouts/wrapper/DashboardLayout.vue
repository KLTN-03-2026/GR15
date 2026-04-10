<script setup>
import DashboardHeader from '@/layouts/components/DashboardHeader.vue'
import DashboardSidebar from '@/layouts/components/DashboardSidebar.vue'
</script>

<template>
  <div class="flex min-h-screen bg-slate-50 text-slate-900">
    <DashboardSidebar />
    <div class="flex min-w-0 flex-1 flex-col">
      <DashboardHeader />
      <main class="flex-1 px-4 py-6 sm:px-6 lg:px-8">
        <div class="mx-auto max-w-7xl">
          <slot />
        </div>
      </main>
    </div>
  </div>
</template>
