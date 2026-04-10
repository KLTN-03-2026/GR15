<template>
  <footer class="border-t border-slate-200 bg-white/80 py-6">
    <div class="mx-auto flex max-w-7xl flex-col gap-3 px-6 text-sm text-slate-500 sm:flex-row sm:items-center sm:justify-between">
      <p>SmartJob AI - phien ban toi gian cho dang ky, ky nang va theo doi don.</p>
      <div class="flex items-center gap-4">
        <RouterLink to="/register" class="font-semibold text-[#2463eb] hover:underline">Dang ky</RouterLink>
        <RouterLink to="/skills" class="font-semibold text-[#2463eb] hover:underline">Ky nang</RouterLink>
        <RouterLink to="/applications" class="font-semibold text-[#2463eb] hover:underline">Don ung tuyen</RouterLink>
      </div>
    </div>
  </footer>
</template>
