<template>
  <header class="flex items-center justify-between whitespace-nowrap border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-6 py-3 sticky top-0 z-50">
    <div class="flex items-center gap-8">
      <div class="flex items-center gap-2 text-[#2463eb]">
        <span class="material-symbols-outlined text-3xl font-bold">stream</span>
        <h2 class="text-slate-900 dark:text-white text-xl font-bold leading-tight tracking-tight">HireStream</h2>
      </div>
      <label class="flex flex-col min-w-64 h-10">
        <div class="flex w-full flex-1 items-stretch rounded-lg h-full">
          <div class="text-slate-500 flex border-none bg-slate-100 dark:bg-slate-800 items-center justify-center pl-4 rounded-l-lg">
            <span class="material-symbols-outlined">search</span>
          </div>
          <input class="flex w-full min-w-0 flex-1 border-none bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:ring-0 h-full placeholder:text-slate-500 px-4 rounded-r-lg text-sm" placeholder="Search candidates or jobs..." />
        </div>
      </label>
    </div>
    <div class="flex items-center gap-4">
      <div class="flex gap-2">
        <button class="flex items-center justify-center rounded-lg h-10 w-10 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700">
          <span class="material-symbols-outlined">notifications</span>
        </button>
        <button class="flex items-center justify-center rounded-lg h-10 w-10 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700">
          <span class="material-symbols-outlined">settings</span>
        </button>
      </div>
      <div class="h-10 w-10 rounded-full bg-[#2463eb] flex items-center justify-center text-white font-bold">
        JD
      </div>
    </div>
  </header>
</template>

<script setup>
</script>
