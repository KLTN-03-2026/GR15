<template>
  <header class="h-16 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between px-8 shrink-0">
    <div class="flex-1 max-w-md relative">
      <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-xl">search</span>
      <input class="w-full pl-10 pr-4 py-2 bg-slate-100 dark:bg-slate-800 border-none rounded-lg focus:ring-2 focus:ring-[#2463eb]/50 text-sm" placeholder="Tìm kiếm công việc, công ty..." type="text" />
    </div>
    <div class="flex items-center gap-4">
      <button class="relative p-2 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full transition-colors">
        <span class="material-symbols-outlined">notifications</span>
        <span class="absolute top-1.5 right-1.5 size-2 bg-red-500 rounded-full border-2 border-white dark:border-slate-900"></span>
      </button>
      <button class="p-2 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full transition-colors">
        <span class="material-symbols-outlined">mail</span>
      </button>
      <div class="h-8 w-[1px] bg-slate-200 dark:border-slate-800 mx-2"></div>
      <button class="flex items-center gap-2 hover:opacity-80 transition-opacity">
        <div class="size-8 rounded-full bg-slate-200 dark:bg-slate-800"></div>
      </button>
    </div>
  </header>
</template>

<script setup>
</script>
