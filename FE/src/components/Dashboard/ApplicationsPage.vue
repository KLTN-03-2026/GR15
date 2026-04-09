<template>
  <!-- Page Header -->
  <div class="flex justify-between items-end mb-8">
    <div>
      <h1 class="text-2xl font-bold text-slate-900 dark:text-white">Việc đã ứng tuyển</h1>
      <p class="text-slate-500 text-sm mt-1">Theo dõi trạng thái hồ sơ ứng tuyển của bạn.</p>
    </div>
  </div>

  <!-- Stats -->
  <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
    <div class="bg-white dark:bg-slate-900 p-5 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800">
      <div class="flex items-center justify-between mb-2">
        <p class="text-slate-500 text-sm font-medium">Tổng ứng tuyển</p>
        <div class="p-2 bg-[#2463eb]/10 rounded-lg text-[#2463eb]">
          <span class="material-symbols-outlined">send</span>
        </div>
      </div>
      <h3 class="text-2xl font-bold">15</h3>
    </div>
    <div class="bg-white dark:bg-slate-900 p-5 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800">
      <div class="flex items-center justify-between mb-2">
        <p class="text-slate-500 text-sm font-medium">Đang chờ duyệt</p>
        <div class="p-2 bg-amber-100 dark:bg-amber-900/20 rounded-lg text-amber-600">
          <span class="material-symbols-outlined">hourglass_top</span>
        </div>
      </div>
      <h3 class="text-2xl font-bold">8</h3>
    </div>
    <div class="bg-white dark:bg-slate-900 p-5 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800">
      <div class="flex items-center justify-between mb-2">
        <p class="text-slate-500 text-sm font-medium">Đã chấp nhận</p>
        <div class="p-2 bg-green-100 dark:bg-green-900/20 rounded-lg text-green-600">
          <span class="material-symbols-outlined">check_circle</span>
        </div>
      </div>
      <h3 class="text-2xl font-bold">5</h3>
    </div>
    <div class="bg-white dark:bg-slate-900 p-5 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800">
      <div class="flex items-center justify-between mb-2">
        <p class="text-slate-500 text-sm font-medium">Đã từ chối</p>
        <div class="p-2 bg-red-100 dark:bg-red-900/20 rounded-lg text-red-600">
          <span class="material-symbols-outlined">cancel</span>
        </div>
      </div>
      <h3 class="text-2xl font-bold">2</h3>
    </div>
  </div>

  <!-- Tabs -->
  <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
    <div class="flex border-b border-slate-200 dark:border-slate-800 px-6 gap-6 overflow-x-auto">
      <a class="flex items-center border-b-2 border-[#2463eb] text-[#2463eb] pb-3 pt-4 font-bold text-sm whitespace-nowrap" href="#">
        Tất cả <span class="ml-2 bg-[#2463eb]/10 px-2 py-0.5 rounded text-[10px]">15</span>
      </a>
      <a class="flex items-center border-b-2 border-transparent text-slate-500 pb-3 pt-4 font-medium text-sm hover:text-slate-700 whitespace-nowrap" href="#">
        Đang chờ <span class="ml-2 bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded text-[10px]">8</span>
      </a>
      <a class="flex items-center border-b-2 border-transparent text-slate-500 pb-3 pt-4 font-medium text-sm hover:text-slate-700 whitespace-nowrap" href="#">
        Đã chấp nhận <span class="ml-2 bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded text-[10px]">5</span>
      </a>
      <a class="flex items-center border-b-2 border-transparent text-slate-500 pb-3 pt-4 font-medium text-sm hover:text-slate-700 whitespace-nowrap" href="#">
        Đã từ chối <span class="ml-2 bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded text-[10px]">2</span>
      </a>
    </div>

    <!-- Application List -->
    <div class="divide-y divide-slate-100 dark:divide-slate-800">
      <!-- Application 1 — Accepted -->
      <div class="p-5 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
        <div class="flex flex-col md:flex-row md:items-center gap-4 justify-between">
          <div class="flex items-center gap-4 flex-1">
            <div class="size-12 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center shrink-0">
              <span class="material-symbols-outlined text-slate-500">domain</span>
            </div>
            <div class="flex-1">
              <h3 class="font-bold text-slate-900 dark:text-white">Senior Frontend Developer</h3>
              <p class="text-slate-500 text-sm">TechCorp Solutions • Quận 1, TP.HCM</p>
              <div class="flex items-center gap-4 mt-1.5 text-xs text-slate-400">
                <span class="flex items-center gap-1"><span class="material-symbols-outlined text-[14px]">calendar_today</span> Nộp ngày 15/03/2026</span>
                <span class="flex items-center gap-1"><span class="material-symbols-outlined text-[14px]">description</span> CV Frontend Developer</span>
              </div>
            </div>
          </div>
          <div class="flex items-center gap-4 shrink-0">
            <div class="flex flex-col items-center">
              <div class="flex items-center gap-1 text-[#2463eb]">
                <span class="material-symbols-outlined text-[16px]">auto_awesome</span>
                <span class="font-bold text-sm">92%</span>
              </div>
              <span class="text-[10px] text-slate-400 font-medium">Matching</span>
            </div>
            <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400">
              <span class="size-1.5 rounded-full bg-green-500"></span> Đã chấp nhận
            </span>
            <button class="text-slate-400 hover:text-slate-600">
              <span class="material-symbols-outlined">chevron_right</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Application 2 — Pending -->
      <div class="p-5 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
        <div class="flex flex-col md:flex-row md:items-center gap-4 justify-between">
          <div class="flex items-center gap-4 flex-1">
            <div class="size-12 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center shrink-0">
              <span class="material-symbols-outlined text-slate-500">domain</span>
            </div>
            <div class="flex-1">
              <h3 class="font-bold text-slate-900 dark:text-white">UI/UX Product Designer</h3>
              <p class="text-slate-500 text-sm">Innovate Labs • Quận 7, TP.HCM</p>
              <div class="flex items-center gap-4 mt-1.5 text-xs text-slate-400">
                <span class="flex items-center gap-1"><span class="material-symbols-outlined text-[14px]">calendar_today</span> Nộp ngày 12/03/2026</span>
                <span class="flex items-center gap-1"><span class="material-symbols-outlined text-[14px]">description</span> CV Product Designer</span>
              </div>
            </div>
          </div>
          <div class="flex items-center gap-4 shrink-0">
            <div class="flex flex-col items-center">
              <div class="flex items-center gap-1 text-[#2463eb]">
                <span class="material-symbols-outlined text-[16px]">auto_awesome</span>
                <span class="font-bold text-sm">78%</span>
              </div>
              <span class="text-[10px] text-slate-400 font-medium">Matching</span>
            </div>
            <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400">
              <span class="size-1.5 rounded-full bg-amber-500"></span> Đang chờ
            </span>
            <button class="text-slate-400 hover:text-slate-600">
              <span class="material-symbols-outlined">chevron_right</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Application 3 — Pending -->
      <div class="p-5 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
        <div class="flex flex-col md:flex-row md:items-center gap-4 justify-between">
          <div class="flex items-center gap-4 flex-1">
            <div class="size-12 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center shrink-0">
              <span class="material-symbols-outlined text-slate-500">domain</span>
            </div>
            <div class="flex-1">
              <h3 class="font-bold text-slate-900 dark:text-white">Fullstack Developer (NodeJS)</h3>
              <p class="text-slate-500 text-sm">VNG Corporation • Quận Tân Bình, TP.HCM</p>
              <div class="flex items-center gap-4 mt-1.5 text-xs text-slate-400">
                <span class="flex items-center gap-1"><span class="material-symbols-outlined text-[14px]">calendar_today</span> Nộp ngày 10/03/2026</span>
                <span class="flex items-center gap-1"><span class="material-symbols-outlined text-[14px]">description</span> CV Frontend Developer</span>
              </div>
            </div>
          </div>
          <div class="flex items-center gap-4 shrink-0">
            <div class="flex flex-col items-center">
              <div class="flex items-center gap-1 text-[#2463eb]">
                <span class="material-symbols-outlined text-[16px]">auto_awesome</span>
                <span class="font-bold text-sm">85%</span>
              </div>
              <span class="text-[10px] text-slate-400 font-medium">Matching</span>
            </div>
            <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400">
              <span class="size-1.5 rounded-full bg-amber-500"></span> Đang chờ
            </span>
            <button class="text-slate-400 hover:text-slate-600">
              <span class="material-symbols-outlined">chevron_right</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Application 4 — Rejected -->
      <div class="p-5 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors opacity-70">
        <div class="flex flex-col md:flex-row md:items-center gap-4 justify-between">
          <div class="flex items-center gap-4 flex-1">
            <div class="size-12 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center shrink-0">
              <span class="material-symbols-outlined text-slate-500">domain</span>
            </div>
            <div class="flex-1">
              <h3 class="font-bold text-slate-900 dark:text-white">Backend Developer (Laravel)</h3>
              <p class="text-slate-500 text-sm">FPT Software • Quận 9, TP.HCM</p>
              <div class="flex items-center gap-4 mt-1.5 text-xs text-slate-400">
                <span class="flex items-center gap-1"><span class="material-symbols-outlined text-[14px]">calendar_today</span> Nộp ngày 01/03/2026</span>
                <span class="flex items-center gap-1"><span class="material-symbols-outlined text-[14px]">description</span> CV Backend Developer</span>
              </div>
            </div>
          </div>
          <div class="flex items-center gap-4 shrink-0">
            <div class="flex flex-col items-center">
              <div class="flex items-center gap-1 text-slate-400">
                <span class="material-symbols-outlined text-[16px]">auto_awesome</span>
                <span class="font-bold text-sm">65%</span>
              </div>
              <span class="text-[10px] text-slate-400 font-medium">Matching</span>
            </div>
            <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400">
              <span class="size-1.5 rounded-full bg-red-500"></span> Đã từ chối
            </span>
            <button class="text-slate-400 hover:text-slate-600">
              <span class="material-symbols-outlined">chevron_right</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div class="flex items-center justify-between border-t border-slate-200 dark:border-slate-800 px-6 py-4">
      <p class="text-xs text-slate-500">Hiển thị 1-4 của 15 kết quả</p>
      <div class="flex gap-2">
        <button class="h-8 w-8 flex items-center justify-center rounded-lg border border-slate-200 dark:border-slate-800 text-slate-500 disabled:opacity-50" disabled>
          <span class="material-symbols-outlined text-[18px]">chevron_left</span>
        </button>
        <button class="h-8 w-8 flex items-center justify-center rounded-lg bg-[#2463eb] text-white font-bold text-xs">1</button>
        <button class="h-8 w-8 flex items-center justify-center rounded-lg border border-slate-200 dark:border-slate-800 text-slate-600 hover:bg-slate-50 font-bold text-xs">2</button>
        <button class="h-8 w-8 flex items-center justify-center rounded-lg border border-slate-200 dark:border-slate-800 text-slate-500 hover:bg-slate-50">
          <span class="material-symbols-outlined text-[18px]">chevron_right</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
</script>
