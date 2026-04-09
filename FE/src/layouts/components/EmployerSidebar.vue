<template>
  <aside class="w-64 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hidden lg:flex flex-col p-4 gap-6">
    <div class="flex flex-col gap-1">
      <p class="px-3 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Menu chính</p>
      <RouterLink to="/employer" exact-active-class="active-nav" class="nav-link flex items-center gap-3 px-3 py-2 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors font-medium">
        <span class="material-symbols-outlined">dashboard</span>
        <span class="text-sm">Tổng quan</span>
      </RouterLink>
      <RouterLink to="/employer/jobs" active-class="active-nav" class="nav-link flex items-center gap-3 px-3 py-2 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors font-medium">
        <span class="material-symbols-outlined">work</span>
        <span class="text-sm">Tin tuyển dụng</span>
      </RouterLink>
      <RouterLink to="/employer/candidates" active-class="active-nav" class="nav-link flex items-center gap-3 px-3 py-2 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors font-medium">
        <span class="material-symbols-outlined">group</span>
        <span class="text-sm">Ứng viên</span>
      </RouterLink>
      <RouterLink to="/employer/interviews" active-class="active-nav" class="nav-link flex items-center gap-3 px-3 py-2 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors font-medium">
        <span class="material-symbols-outlined">calendar_today</span>
        <span class="text-sm">Phỏng vấn</span>
      </RouterLink>
      <RouterLink to="/employer/company" active-class="active-nav" class="nav-link flex items-center gap-3 px-3 py-2 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors font-medium">
        <span class="material-symbols-outlined">domain</span>
        <span class="text-sm">Công ty</span>
      </RouterLink>
    </div>
    <div class="flex flex-col gap-1 mt-auto">
      <div class="p-4 bg-[#2463eb]/5 rounded-xl border border-[#2463eb]/20">
        <p class="text-xs font-bold text-[#2463eb] mb-1 uppercase">Gói Pro</p>
        <p class="text-xs text-slate-500 dark:text-slate-400 mb-3">Bạn còn 5 vị trí đăng tuyển cao cấp.</p>
        <button class="w-full py-2 bg-[#2463eb] text-white text-xs font-bold rounded-lg hover:bg-[#2463eb]/90">Nâng cấp ngay</button>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>

<style scoped>
.nav-link.active-nav {
  background-color: rgb(36 99 235 / 0.1);
  color: #2463eb;
}

.nav-link.active-nav:hover {
  background-color: rgb(36 99 235 / 0.15);
}
</style>
