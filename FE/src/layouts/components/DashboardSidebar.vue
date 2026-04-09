<template>
  <aside class="w-64 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col shrink-0">
    <div class="p-6 flex items-center gap-3">
      <div class="size-8 bg-[#2463eb] rounded-lg flex items-center justify-center text-white">
        <span class="material-symbols-outlined">rocket_launch</span>
      </div>
      <h2 class="text-xl font-bold tracking-tight text-[#2463eb]">HRTech</h2>
    </div>
    <div class="px-4 py-2 flex items-center gap-3 mb-6">
      <div class="size-10 rounded-full bg-slate-200 dark:bg-slate-800 shrink-0"></div>
      <div class="overflow-hidden">
        <p class="font-semibold truncate text-sm">Nguyễn Văn A</p>
        <p class="text-xs text-slate-500 truncate">Ứng viên</p>
      </div>
    </div>
    <nav class="flex-1 px-3 space-y-1 overflow-y-auto">
      <RouterLink to="/dashboard" exact-active-class="active-nav" class="nav-link flex items-center gap-3 px-3 py-2 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors font-medium">
        <span class="material-symbols-outlined">dashboard</span>
        <span class="text-sm">Tổng quan</span>
      </RouterLink>
      <RouterLink to="/profile" active-class="active-nav" class="nav-link flex items-center gap-3 px-3 py-2 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors font-medium">
        <span class="material-symbols-outlined">account_circle</span>
        <span class="text-sm">Hồ sơ cá nhân</span>
      </RouterLink>
      <RouterLink to="/my-cv" active-class="active-nav" class="nav-link flex items-center gap-3 px-3 py-2 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors font-medium">
        <span class="material-symbols-outlined">description</span>
        <span class="text-sm">CV của tôi</span>
      </RouterLink>
      <RouterLink to="/matched-jobs" active-class="active-nav" class="nav-link flex items-center gap-3 px-3 py-2 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors font-medium">
        <span class="material-symbols-outlined">work</span>
        <span class="text-sm">Việc làm phù hợp</span>
      </RouterLink>
      <RouterLink to="/applications" active-class="active-nav" class="nav-link flex items-center gap-3 px-3 py-2 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors font-medium">
        <span class="material-symbols-outlined">send</span>
        <span class="text-sm">Việc đã ứng tuyển</span>
      </RouterLink>
      <RouterLink to="/saved-jobs" active-class="active-nav" class="nav-link flex items-center gap-3 px-3 py-2 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors font-medium">
        <span class="material-symbols-outlined">bookmark</span>
        <span class="text-sm">Tin đã lưu</span>
      </RouterLink>
      <div class="pt-4 pb-2 text-[10px] uppercase font-bold text-slate-400 px-3 tracking-widest">Dịch vụ AI</div>
      <RouterLink to="/ai-career" active-class="active-nav" class="nav-link flex items-center gap-3 px-3 py-2 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors group font-medium">
        <span class="material-symbols-outlined text-[#2463eb] group-hover:scale-110 transition-transform">auto_awesome</span>
        <span class="text-sm">Tư vấn nghề nghiệp AI</span>
      </RouterLink>
    </nav>
    <div class="p-4 border-t border-slate-200 dark:border-slate-800">
      <a class="flex items-center gap-3 px-3 py-2 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors" href="#">
        <span class="material-symbols-outlined">settings</span>
        <span class="text-sm">Cài đặt</span>
      </a>
      <RouterLink to="/" class="flex items-center gap-3 px-3 py-2 rounded-lg text-red-500 hover:bg-red-50 dark:hover:bg-red-900/10 transition-colors">
        <span class="material-symbols-outlined">logout</span>
        <span class="text-sm">Đăng xuất</span>
      </RouterLink>
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
