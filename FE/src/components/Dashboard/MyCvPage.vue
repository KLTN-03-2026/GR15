<template>
  <!-- Page Header -->
  <div class="flex justify-between items-end mb-8">
    <div>
      <h1 class="text-2xl font-bold text-slate-900 dark:text-white">CV của tôi</h1>
      <p class="text-slate-500 text-sm mt-1">Quản lý hồ sơ xin việc — tạo nhiều CV cho các vị trí khác nhau.</p>
    </div>
    <button class="bg-[#2463eb] text-white px-5 py-2.5 rounded-lg font-bold flex items-center gap-2 shadow-lg shadow-[#2463eb]/20 hover:bg-[#2463eb]/90 transition-all text-sm">
      <span class="material-symbols-outlined text-xl">add</span>
      Tạo CV mới
    </button>
  </div>

  <!-- Stats -->
  <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
    <div class="bg-white dark:bg-slate-900 p-5 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800">
      <div class="flex items-center justify-between mb-2">
        <p class="text-slate-500 text-sm font-medium">Tổng hồ sơ</p>
        <div class="p-2 bg-[#2463eb]/10 rounded-lg text-[#2463eb]">
          <span class="material-symbols-outlined">description</span>
        </div>
      </div>
      <h3 class="text-2xl font-bold">3</h3>
    </div>
    <div class="bg-white dark:bg-slate-900 p-5 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800">
      <div class="flex items-center justify-between mb-2">
        <p class="text-slate-500 text-sm font-medium">Đang công khai</p>
        <div class="p-2 bg-green-100 dark:bg-green-900/20 rounded-lg text-green-600">
          <span class="material-symbols-outlined">visibility</span>
        </div>
      </div>
      <h3 class="text-2xl font-bold">2</h3>
    </div>
    <div class="bg-white dark:bg-slate-900 p-5 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800">
      <div class="flex items-center justify-between mb-2">
        <p class="text-slate-500 text-sm font-medium">Lượt xem CV</p>
        <div class="p-2 bg-amber-100 dark:bg-amber-900/20 rounded-lg text-amber-600">
          <span class="material-symbols-outlined">bar_chart</span>
        </div>
      </div>
      <h3 class="text-2xl font-bold">48</h3>
    </div>
  </div>

  <!-- CV List -->
  <div class="space-y-4">
    <!-- CV Card 1 — Active -->
    <div class="bg-white dark:bg-slate-900 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-800 hover:border-[#2463eb]/40 transition-all">
      <div class="flex flex-col md:flex-row md:items-center gap-4 justify-between">
        <div class="flex items-center gap-4">
          <div class="size-14 bg-[#2463eb]/10 rounded-xl flex items-center justify-center shrink-0">
            <span class="material-symbols-outlined text-[#2463eb] text-3xl">description</span>
          </div>
          <div>
            <div class="flex items-center gap-3 mb-1">
              <h3 class="font-bold text-lg text-slate-900 dark:text-white">CV Frontend Developer</h3>
              <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400">
                <span class="size-1.5 rounded-full bg-green-500"></span> Công khai
              </span>
              <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-[#2463eb]/10 text-[#2463eb]">Chính</span>
            </div>
            <p class="text-slate-500 text-sm">Cập nhật lần cuối: 20/03/2026 • 2 trang • PDF</p>
            <div class="flex gap-2 mt-2">
              <span class="text-xs bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded font-medium">ReactJS</span>
              <span class="text-xs bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded font-medium">VueJS</span>
              <span class="text-xs bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded font-medium">TypeScript</span>
              <span class="text-xs text-slate-400 self-center">+3 kỹ năng</span>
            </div>
          </div>
        </div>
        <div class="flex items-center gap-2 shrink-0">
          <button class="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
            <span class="material-symbols-outlined text-[18px]">download</span> Tải xuống
          </button>
          <button class="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
            <span class="material-symbols-outlined text-[18px]">visibility_off</span> Ẩn
          </button>
          <button class="flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-bold text-[#2463eb] bg-[#2463eb]/10 hover:bg-[#2463eb] hover:text-white transition-all">
            <span class="material-symbols-outlined text-[18px]">edit</span> Chỉnh sửa
          </button>
        </div>
      </div>
    </div>

    <!-- CV Card 2 — Active -->
    <div class="bg-white dark:bg-slate-900 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-800 hover:border-[#2463eb]/40 transition-all">
      <div class="flex flex-col md:flex-row md:items-center gap-4 justify-between">
        <div class="flex items-center gap-4">
          <div class="size-14 bg-purple-100 dark:bg-purple-900/20 rounded-xl flex items-center justify-center shrink-0">
            <span class="material-symbols-outlined text-purple-600 text-3xl">description</span>
          </div>
          <div>
            <div class="flex items-center gap-3 mb-1">
              <h3 class="font-bold text-lg text-slate-900 dark:text-white">CV Product Designer</h3>
              <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400">
                <span class="size-1.5 rounded-full bg-green-500"></span> Công khai
              </span>
            </div>
            <p class="text-slate-500 text-sm">Cập nhật lần cuối: 18/03/2026 • 1 trang • PDF</p>
            <div class="flex gap-2 mt-2">
              <span class="text-xs bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded font-medium">Figma</span>
              <span class="text-xs bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded font-medium">UI/UX</span>
              <span class="text-xs bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded font-medium">Prototyping</span>
            </div>
          </div>
        </div>
        <div class="flex items-center gap-2 shrink-0">
          <button class="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
            <span class="material-symbols-outlined text-[18px]">download</span> Tải xuống
          </button>
          <button class="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
            <span class="material-symbols-outlined text-[18px]">visibility_off</span> Ẩn
          </button>
          <button class="flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-bold text-[#2463eb] bg-[#2463eb]/10 hover:bg-[#2463eb] hover:text-white transition-all">
            <span class="material-symbols-outlined text-[18px]">edit</span> Chỉnh sửa
          </button>
        </div>
      </div>
    </div>

    <!-- CV Card 3 — Hidden -->
    <div class="bg-white dark:bg-slate-900 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-800 opacity-70 hover:opacity-100 transition-all">
      <div class="flex flex-col md:flex-row md:items-center gap-4 justify-between">
        <div class="flex items-center gap-4">
          <div class="size-14 bg-slate-100 dark:bg-slate-800 rounded-xl flex items-center justify-center shrink-0">
            <span class="material-symbols-outlined text-slate-400 text-3xl">description</span>
          </div>
          <div>
            <div class="flex items-center gap-3 mb-1">
              <h3 class="font-bold text-lg text-slate-900 dark:text-white">CV Backend Developer</h3>
              <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400">
                <span class="size-1.5 rounded-full bg-slate-400"></span> Đã ẩn
              </span>
            </div>
            <p class="text-slate-500 text-sm">Cập nhật lần cuối: 10/02/2026 • 2 trang • PDF</p>
            <div class="flex gap-2 mt-2">
              <span class="text-xs bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded font-medium">Laravel</span>
              <span class="text-xs bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded font-medium">NodeJS</span>
              <span class="text-xs bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded font-medium">MySQL</span>
            </div>
          </div>
        </div>
        <div class="flex items-center gap-2 shrink-0">
          <button class="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
            <span class="material-symbols-outlined text-[18px]">download</span> Tải xuống
          </button>
          <button class="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium text-green-600 hover:bg-green-50 dark:hover:bg-green-900/20 transition-colors">
            <span class="material-symbols-outlined text-[18px]">visibility</span> Hiện
          </button>
          <button class="flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-bold text-[#2463eb] bg-[#2463eb]/10 hover:bg-[#2463eb] hover:text-white transition-all">
            <span class="material-symbols-outlined text-[18px]">edit</span> Chỉnh sửa
          </button>
          <button class="flex items-center justify-center size-9 rounded-lg text-red-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors">
            <span class="material-symbols-outlined text-[18px]">delete</span>
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Create New CV CTA -->
  <div class="mt-6">
    <button class="w-full flex items-center justify-center gap-3 p-6 border-2 border-dashed border-slate-200 dark:border-slate-800 rounded-xl text-slate-500 hover:border-[#2463eb] hover:text-[#2463eb] transition-all group">
      <span class="material-symbols-outlined text-2xl group-hover:scale-110 transition-transform">note_add</span>
      <span class="font-medium">Tạo hồ sơ mới để ứng tuyển nhiều vị trí khác nhau</span>
    </button>
  </div>
</template>

<script setup>
</script>
