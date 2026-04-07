<script setup>
import GuestHeader from '@/layouts/components/GuestHeader.vue'
import GuestFooter from '@/layouts/components/GuestFooter.vue'
</script>

<template>
  <div class="relative flex min-h-screen w-full flex-col overflow-x-hidden bg-[radial-gradient(circle_at_top,_rgba(36,99,235,0.08),_transparent_26%),linear-gradient(180deg,_#f8fafc_0%,_#f4f6fb_100%)] dark:bg-[#111621] text-slate-900 dark:text-slate-100">
    <GuestHeader />
    <main class="flex-1">
      <slot />
    </main>
    <GuestFooter />
  </div>
</template>
