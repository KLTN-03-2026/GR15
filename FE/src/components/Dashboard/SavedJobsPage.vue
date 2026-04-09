<template>
  <!-- Page Header -->
  <div class="flex justify-between items-end mb-8">
    <div>
      <h1 class="text-2xl font-bold text-slate-900 dark:text-white">Tin đã lưu</h1>
      <p class="text-slate-500 text-sm mt-1">Các tin tuyển dụng bạn đã bookmark để xem lại sau.</p>
    </div>
    <div class="flex items-center gap-3">
      <div class="flex items-center gap-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2">
        <span class="material-symbols-outlined text-slate-400 text-[18px]">sort</span>
        <select class="bg-transparent border-none text-sm font-medium text-slate-700 dark:text-slate-300 focus:ring-0 p-0 pr-6 cursor-pointer">
          <option>Mới nhất</option>
          <option>Cũ nhất</option>
          <option>Matching cao nhất</option>
        </select>
      </div>
    </div>
  </div>

  <!-- Info Banner -->
  <div class="bg-[#2463eb]/5 border border-[#2463eb]/10 rounded-xl p-4 mb-6 flex items-center gap-3">
    <span class="material-symbols-outlined text-[#2463eb]">info</span>
    <p class="text-sm text-slate-600 dark:text-slate-400">Bạn đã lưu <strong class="text-[#2463eb]">6 tin</strong> tuyển dụng. Nhấn vào biểu tượng bookmark để bỏ lưu.</p>
  </div>

  <!-- Saved Jobs Grid -->
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
    <!-- Job Card 1 -->
    <div class="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 hover:border-[#2463eb]/50 transition-all group">
      <div class="flex items-start gap-4 mb-4">
        <div class="size-14 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center shrink-0 border border-slate-100 dark:border-slate-700">
          <span class="material-symbols-outlined text-slate-500 text-2xl">domain</span>
        </div>
        <div class="flex-1">
          <div class="flex justify-between">
            <span class="text-[10px] font-bold text-[#2463eb] bg-[#2463eb]/10 px-2 py-0.5 rounded uppercase">Hot Job</span>
            <button class="text-[#2463eb] hover:text-red-500 transition-colors" title="Bỏ lưu">
              <span class="material-symbols-outlined fill-1">bookmark</span>
            </button>
          </div>
          <h3 class="font-bold text-lg group-hover:text-[#2463eb] transition-colors mt-1">Senior Frontend Developer</h3>
          <p class="text-slate-500 text-sm">TechCorp Solutions • Quận 1, TP.HCM</p>
        </div>
      </div>
      <div class="flex flex-wrap gap-2 mb-4">
        <span class="text-xs bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded font-medium">ReactJS</span>
        <span class="text-xs bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded font-medium">TypeScript</span>
        <span class="text-xs bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded font-medium">Remote</span>
      </div>
      <div class="flex items-center justify-between pt-4 border-t border-slate-100 dark:border-slate-800">
        <div class="flex items-center gap-3">
          <p class="text-slate-600 dark:text-slate-400 font-bold text-sm">$2,500 - $3,500</p>
          <span class="text-[10px] text-slate-400">• Lưu 2 ngày trước</span>
        </div>
        <button class="bg-[#2463eb]/10 text-[#2463eb] hover:bg-[#2463eb] hover:text-white px-4 py-2 rounded-lg text-sm font-bold transition-all">
          Ứng tuyển
        </button>
      </div>
    </div>

    <!-- Job Card 2 -->
    <div class="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 hover:border-[#2463eb]/50 transition-all group">
      <div class="flex items-start gap-4 mb-4">
        <div class="size-14 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center shrink-0 border border-slate-100 dark:border-slate-700">
          <span class="material-symbols-outlined text-slate-500 text-2xl">domain</span>
        </div>
        <div class="flex-1">
          <div class="flex justify-between">
            <span class="text-[10px] font-bold text-green-600 bg-green-100 dark:bg-green-900/30 px-2 py-0.5 rounded uppercase">New</span>
            <button class="text-[#2463eb] hover:text-red-500 transition-colors" title="Bỏ lưu">
              <span class="material-symbols-outlined fill-1">bookmark</span>
            </button>
          </div>
          <h3 class="font-bold text-lg group-hover:text-[#2463eb] transition-colors mt-1">UI/UX Product Designer</h3>
          <p class="text-slate-500 text-sm">Innovate Labs • Quận 7, TP.HCM</p>
        </div>
      </div>
      <div class="flex flex-wrap gap-2 mb-4">
        <span class="text-xs bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded font-medium">Figma</span>
        <span class="text-xs bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded font-medium">UI/UX</span>
        <span class="text-xs bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded font-medium">Hybrid</span>
      </div>
      <div class="flex items-center justify-between pt-4 border-t border-slate-100 dark:border-slate-800">
        <div class="flex items-center gap-3">
          <p class="text-slate-600 dark:text-slate-400 font-bold text-sm">Thỏa thuận</p>
          <span class="text-[10px] text-slate-400">• Lưu 3 ngày trước</span>
        </div>
        <button class="bg-[#2463eb]/10 text-[#2463eb] hover:bg-[#2463eb] hover:text-white px-4 py-2 rounded-lg text-sm font-bold transition-all">
          Ứng tuyển
        </button>
      </div>
    </div>

    <!-- Job Card 3 -->
    <div class="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 hover:border-[#2463eb]/50 transition-all group">
      <div class="flex items-start gap-4 mb-4">
        <div class="size-14 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center shrink-0 border border-slate-100 dark:border-slate-700">
          <span class="material-symbols-outlined text-slate-500 text-2xl">domain</span>
        </div>
        <div class="flex-1">
          <div class="flex justify-between">
            <span class="text-[10px] font-bold text-amber-600 bg-amber-100 dark:bg-amber-900/30 px-2 py-0.5 rounded uppercase">Urgent</span>
            <button class="text-[#2463eb] hover:text-red-500 transition-colors" title="Bỏ lưu">
              <span class="material-symbols-outlined fill-1">bookmark</span>
            </button>
          </div>
          <h3 class="font-bold text-lg group-hover:text-[#2463eb] transition-colors mt-1">Fullstack Developer (Vue + Laravel)</h3>
          <p class="text-slate-500 text-sm">VNG Corporation • Quận Tân Bình, TP.HCM</p>
        </div>
      </div>
      <div class="flex flex-wrap gap-2 mb-4">
        <span class="text-xs bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded font-medium">VueJS</span>
        <span class="text-xs bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded font-medium">Laravel</span>
        <span class="text-xs bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded font-medium">Onsite</span>
      </div>
      <div class="flex items-center justify-between pt-4 border-t border-slate-100 dark:border-slate-800">
        <div class="flex items-center gap-3">
          <p class="text-slate-600 dark:text-slate-400 font-bold text-sm">$1,800 - $2,800</p>
          <span class="text-[10px] text-slate-400">• Lưu 5 ngày trước</span>
        </div>
        <button class="bg-[#2463eb]/10 text-[#2463eb] hover:bg-[#2463eb] hover:text-white px-4 py-2 rounded-lg text-sm font-bold transition-all">
          Ứng tuyển
        </button>
      </div>
    </div>

    <!-- Job Card 4 — Expired -->
    <div class="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 opacity-60 hover:opacity-100 transition-all group">
      <div class="flex items-start gap-4 mb-4">
        <div class="size-14 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center shrink-0 border border-slate-100 dark:border-slate-700">
          <span class="material-symbols-outlined text-slate-500 text-2xl">domain</span>
        </div>
        <div class="flex-1">
          <div class="flex justify-between">
            <span class="text-[10px] font-bold text-red-600 bg-red-100 dark:bg-red-900/30 px-2 py-0.5 rounded uppercase">Hết hạn</span>
            <button class="text-slate-400 hover:text-red-500 transition-colors" title="Bỏ lưu">
              <span class="material-symbols-outlined fill-1">bookmark</span>
            </button>
          </div>
          <h3 class="font-bold text-lg transition-colors mt-1 line-through text-slate-400">Data Analyst Intern</h3>
          <p class="text-slate-400 text-sm">FPT Software • Quận 9, TP.HCM</p>
        </div>
      </div>
      <div class="flex flex-wrap gap-2 mb-4">
        <span class="text-xs bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded font-medium">Python</span>
        <span class="text-xs bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded font-medium">SQL</span>
      </div>
      <div class="flex items-center justify-between pt-4 border-t border-slate-100 dark:border-slate-800">
        <div class="flex items-center gap-3">
          <p class="text-slate-400 font-bold text-sm">$800 - $1,200</p>
          <span class="text-[10px] text-red-400">• Hết hạn 2 ngày trước</span>
        </div>
        <button class="bg-slate-100 text-slate-400 px-4 py-2 rounded-lg text-sm font-bold cursor-not-allowed" disabled>
          Đã hết hạn
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
</script>
