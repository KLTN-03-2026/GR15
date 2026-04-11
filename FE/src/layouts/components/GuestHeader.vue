<template>
  <header class="sticky top-0 z-50 w-full border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-[#111621]/80 backdrop-blur-md">
    <div class="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
      <RouterLink to="/" class="flex items-center gap-2 text-[#2463eb]">
        <span class="material-symbols-outlined text-3xl font-bold">rocket_launch</span>
        <h2 class="text-slate-900 dark:text-white text-xl font-bold tracking-tight">AI Recruitment</h2>
      </RouterLink>
      <nav class="hidden lg:flex items-center gap-8">
        <RouterLink to="/" class="text-sm font-medium hover:text-[#2463eb] transition-colors">Trang chủ</RouterLink>
        <RouterLink to="/jobs" class="text-sm font-medium hover:text-[#2463eb] transition-colors">Việc làm</RouterLink>
        <RouterLink to="/profile" class="text-sm font-medium hover:text-[#2463eb] transition-colors">Profile ứng viên</RouterLink>
        <RouterLink to="/my-cv" class="text-sm font-medium hover:text-[#2463eb] transition-colors">Quản lý CV</RouterLink>
      </nav>
      <div class="flex items-center gap-3">
        <template v-if="!isAuthenticated">
          <RouterLink to="/login" class="hidden sm:flex h-10 items-center justify-center rounded-lg px-4 text-sm font-bold text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all">
            Đăng nhập
          </RouterLink>
          <RouterLink to="/register" class="flex h-10 items-center justify-center rounded-lg bg-[#2463eb] px-6 text-sm font-bold text-white shadow-lg shadow-[#2463eb]/20 hover:bg-blue-700 transition-all">
            Đăng ký
          </RouterLink>
        </template>
        <template v-else>
          <RouterLink to="/profile" class="hidden sm:flex h-10 items-center justify-center rounded-lg px-4 text-sm font-bold text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all">
            Hồ sơ
          </RouterLink>
          <RouterLink to="/my-cv" class="flex h-10 items-center justify-center rounded-lg bg-[#2463eb] px-6 text-sm font-bold text-white shadow-lg shadow-[#2463eb]/20 hover:bg-blue-700 transition-all">
            CV của tôi
          </RouterLink>
        </template>
      </div>
    </div>
  </header>
</template>

<script setup>
import { RouterLink } from 'vue-router'
import { computed } from 'vue'
import { getAuthToken } from '@/utils/authStorage'

const isAuthenticated = computed(() => Boolean(getAuthToken()))
</script>
