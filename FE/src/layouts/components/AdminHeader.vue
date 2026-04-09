<template>
  <header class="h-16 border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md sticky top-0 z-10 px-8 flex items-center justify-between">
    <div class="flex items-center gap-4 flex-1">
      <div class="relative w-full max-w-md">
        <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-xl">search</span>
        <input class="w-full pl-10 pr-4 py-2 bg-slate-100 dark:bg-slate-800 border-none rounded-lg text-sm focus:ring-2 focus:ring-[#2463eb]/50 transition-all" placeholder="Tìm báo cáo, người dùng hoặc cài đặt..." type="text" />
      </div>
    </div>
    <div class="flex items-center gap-3">
      <button class="p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg relative">
        <span class="material-symbols-outlined">notifications</span>
        <span class="absolute top-2 right-2 size-2 bg-red-500 rounded-full border-2 border-white dark:border-slate-900"></span>
      </button>
      <button class="p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg">
        <span class="material-symbols-outlined">help</span>
      </button>
      <div class="h-6 w-px bg-slate-200 dark:border-slate-800 mx-2"></div>
      <button class="px-4 py-2 bg-[#2463eb] text-white text-sm font-semibold rounded-lg shadow-sm shadow-[#2463eb]/30 hover:bg-[#2463eb]/90 transition-all flex items-center gap-2">
        <span class="material-symbols-outlined text-lg">add</span>
        Báo cáo mới
      </button>
    </div>
  </header>
</template>

<script setup>
</script>
