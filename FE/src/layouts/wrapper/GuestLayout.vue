<template>
  <div class="relative flex min-h-screen w-full flex-col overflow-x-hidden bg-[#f6f6f8] dark:bg-[#111621] text-slate-900 dark:text-slate-100">
    <GuestHeader />
    <main class="flex-1">
      <slot />
    </main>
    <GuestFooter />
  </div>
</template>

<script setup>
import GuestHeader from '@/layouts/components/GuestHeader.vue'
import GuestFooter from '@/layouts/components/GuestFooter.vue'
</script>
