<template>
  <!-- Page Header -->
  <div class="flex justify-between items-end mb-8">
    <div>
      <h1 class="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
        <span class="material-symbols-outlined text-[#2463eb]">auto_awesome</span>
        Việc làm phù hợp
      </h1>
      <p class="text-slate-500 text-sm mt-1">AI đã phân tích hồ sơ của bạn và gợi ý các công việc phù hợp nhất.</p>
    </div>
    <div class="flex items-center gap-3">
      <div class="flex items-center gap-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2">
        <span class="material-symbols-outlined text-slate-400 text-[18px]">sort</span>
        <select class="bg-transparent border-none text-sm font-medium text-slate-700 dark:text-slate-300 focus:ring-0 p-0 pr-6 cursor-pointer">
          <option>Matching cao nhất</option>
          <option>Mới nhất</option>
          <option>Lương cao nhất</option>
        </select>
      </div>
    </div>
  </div>

  <!-- AI Matching Info -->
  <div class="bg-gradient-to-r from-[#2463eb]/5 to-indigo-500/5 border border-[#2463eb]/10 rounded-xl p-5 mb-6 flex flex-col md:flex-row items-start md:items-center gap-4 justify-between">
    <div class="flex items-center gap-3">
      <div class="p-2.5 bg-[#2463eb]/10 rounded-xl">
        <span class="material-symbols-outlined text-[#2463eb] text-2xl">psychology</span>
      </div>
      <div>
        <p class="text-sm font-bold text-slate-900 dark:text-white">AI đã tìm thấy <span class="text-[#2463eb]">24 việc làm</span> phù hợp với hồ sơ của bạn</p>
        <p class="text-xs text-slate-500 mt-0.5">Cập nhật lần cuối: 5 phút trước • Dựa trên CV Frontend Developer</p>
      </div>
    </div>
    <button class="flex items-center gap-2 px-4 py-2 bg-[#2463eb] text-white rounded-lg font-bold text-sm hover:bg-[#2463eb]/90 transition-all shadow-sm">
      <span class="material-symbols-outlined text-[18px]">refresh</span>
      Cập nhật gợi ý
    </button>
  </div>

  <!-- Stats -->
  <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
    <div class="bg-white dark:bg-slate-900 p-5 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800">
      <div class="flex items-center justify-between mb-2">
        <p class="text-slate-500 text-sm font-medium">Matching trung bình</p>
        <div class="p-2 bg-[#2463eb]/10 rounded-lg text-[#2463eb]">
          <span class="material-symbols-outlined">trending_up</span>
        </div>
      </div>
      <h3 class="text-2xl font-bold text-[#2463eb]">85%</h3>
    </div>
    <div class="bg-white dark:bg-slate-900 p-5 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800">
      <div class="flex items-center justify-between mb-2">
        <p class="text-slate-500 text-sm font-medium">Matching &gt; 90%</p>
        <div class="p-2 bg-green-100 dark:bg-green-900/20 rounded-lg text-green-600">
          <span class="material-symbols-outlined">verified</span>
        </div>
      </div>
      <h3 class="text-2xl font-bold">6</h3>
    </div>
    <div class="bg-white dark:bg-slate-900 p-5 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800">
      <div class="flex items-center justify-between mb-2">
        <p class="text-slate-500 text-sm font-medium">Việc mới hôm nay</p>
        <div class="p-2 bg-amber-100 dark:bg-amber-900/20 rounded-lg text-amber-600">
          <span class="material-symbols-outlined">fiber_new</span>
        </div>
      </div>
      <h3 class="text-2xl font-bold">3</h3>
    </div>
  </div>

  <!-- Job Cards -->
  <div class="space-y-4">
    <!-- Job 1 — 95% match -->
    <div class="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 hover:border-[#2463eb]/50 transition-all group">
      <div class="flex items-start gap-4 mb-4">
        <div class="size-14 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center shrink-0 border border-slate-100 dark:border-slate-700">
          <span class="material-symbols-outlined text-slate-500 text-2xl">domain</span>
        </div>
        <div class="flex-1">
          <div class="flex justify-between">
            <div class="flex items-center gap-2">
              <span class="text-[10px] font-bold text-[#2463eb] bg-[#2463eb]/10 px-2 py-0.5 rounded uppercase">Top Match</span>
              <span class="text-[10px] font-bold text-green-600 bg-green-100 dark:bg-green-900/30 px-2 py-0.5 rounded uppercase">New</span>
            </div>
            <button class="text-slate-400 hover:text-[#2463eb] transition-colors">
              <span class="material-symbols-outlined">bookmark</span>
            </button>
          </div>
          <h3 class="font-bold text-lg group-hover:text-[#2463eb] transition-colors mt-1">Senior Frontend Developer</h3>
          <p class="text-slate-500 text-sm">TechCorp Solutions • Quận 1, TP.HCM • Full-time</p>
        </div>
      </div>
      <div class="space-y-3">
        <div class="flex justify-between items-center text-sm mb-1">
          <span class="font-medium text-slate-600 dark:text-slate-400">AI Matching Score</span>
          <span class="font-bold text-[#2463eb]">95%</span>
        </div>
        <div class="w-full h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
          <div class="h-full bg-gradient-to-r from-[#2463eb] to-indigo-500 rounded-full transition-all" style="width: 95%"></div>
        </div>
        <div class="flex flex-wrap gap-2 py-2">
          <span class="text-xs bg-[#2463eb]/10 text-[#2463eb] px-2 py-1 rounded font-bold">ReactJS ✓</span>
          <span class="text-xs bg-[#2463eb]/10 text-[#2463eb] px-2 py-1 rounded font-bold">TypeScript ✓</span>
          <span class="text-xs bg-[#2463eb]/10 text-[#2463eb] px-2 py-1 rounded font-bold">Tailwind ✓</span>
          <span class="text-xs bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded">NextJS</span>
        </div>
        <div class="flex items-center justify-between pt-4 border-t border-slate-100 dark:border-slate-800">
          <div class="flex items-center gap-4">
            <p class="text-slate-600 dark:text-slate-400 font-bold text-sm">$2,500 - $3,500</p>
            <span class="text-xs text-slate-400">• Đăng 2 ngày trước</span>
          </div>
          <div class="flex items-center gap-2">
            <button class="px-4 py-2 rounded-lg text-sm font-bold text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
              Xem chi tiết
            </button>
            <button class="bg-[#2463eb] text-white px-5 py-2 rounded-lg text-sm font-bold hover:bg-[#2463eb]/90 transition-all shadow-md shadow-[#2463eb]/20">
              Ứng tuyển ngay
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Job 2 — 88% match -->
    <div class="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 hover:border-[#2463eb]/50 transition-all group">
      <div class="flex items-start gap-4 mb-4">
        <div class="size-14 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center shrink-0 border border-slate-100 dark:border-slate-700">
          <span class="material-symbols-outlined text-slate-500 text-2xl">domain</span>
        </div>
        <div class="flex-1">
          <div class="flex justify-between">
            <span class="text-[10px] font-bold text-[#2463eb] bg-[#2463eb]/10 px-2 py-0.5 rounded uppercase">Recommended</span>
            <button class="text-slate-400 hover:text-[#2463eb] transition-colors">
              <span class="material-symbols-outlined">bookmark</span>
            </button>
          </div>
          <h3 class="font-bold text-lg group-hover:text-[#2463eb] transition-colors mt-1">Fullstack Developer (Vue + Node)</h3>
          <p class="text-slate-500 text-sm">VNG Corporation • Quận Tân Bình, TP.HCM • Full-time</p>
        </div>
      </div>
      <div class="space-y-3">
        <div class="flex justify-between items-center text-sm mb-1">
          <span class="font-medium text-slate-600 dark:text-slate-400">AI Matching Score</span>
          <span class="font-bold text-[#2463eb]">88%</span>
        </div>
        <div class="w-full h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
          <div class="h-full bg-gradient-to-r from-[#2463eb] to-indigo-500 rounded-full transition-all" style="width: 88%"></div>
        </div>
        <div class="flex flex-wrap gap-2 py-2">
          <span class="text-xs bg-[#2463eb]/10 text-[#2463eb] px-2 py-1 rounded font-bold">VueJS ✓</span>
          <span class="text-xs bg-[#2463eb]/10 text-[#2463eb] px-2 py-1 rounded font-bold">NodeJS ✓</span>
          <span class="text-xs bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded">Docker</span>
          <span class="text-xs bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded">AWS</span>
        </div>
        <div class="flex items-center justify-between pt-4 border-t border-slate-100 dark:border-slate-800">
          <div class="flex items-center gap-4">
            <p class="text-slate-600 dark:text-slate-400 font-bold text-sm">$2,000 - $3,000</p>
            <span class="text-xs text-slate-400">• Đăng 3 ngày trước</span>
          </div>
          <div class="flex items-center gap-2">
            <button class="px-4 py-2 rounded-lg text-sm font-bold text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
              Xem chi tiết
            </button>
            <button class="bg-[#2463eb]/10 text-[#2463eb] hover:bg-[#2463eb] hover:text-white px-5 py-2 rounded-lg text-sm font-bold transition-all">
              Ứng tuyển ngay
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Job 3 — 78% match -->
    <div class="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 hover:border-[#2463eb]/50 transition-all group">
      <div class="flex items-start gap-4 mb-4">
        <div class="size-14 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center shrink-0 border border-slate-100 dark:border-slate-700">
          <span class="material-symbols-outlined text-slate-500 text-2xl">domain</span>
        </div>
        <div class="flex-1">
          <div class="flex justify-between">
            <span class="text-[10px] font-bold text-amber-600 bg-amber-100 dark:bg-amber-900/30 px-2 py-0.5 rounded uppercase">Good Match</span>
            <button class="text-[#2463eb] hover:text-red-500 transition-colors">
              <span class="material-symbols-outlined fill-1">bookmark</span>
            </button>
          </div>
          <h3 class="font-bold text-lg group-hover:text-[#2463eb] transition-colors mt-1">UI/UX Product Designer</h3>
          <p class="text-slate-500 text-sm">Innovate Labs • Quận 7, TP.HCM • Hybrid</p>
        </div>
      </div>
      <div class="space-y-3">
        <div class="flex justify-between items-center text-sm mb-1">
          <span class="font-medium text-slate-600 dark:text-slate-400">AI Matching Score</span>
          <span class="font-bold text-amber-600">78%</span>
        </div>
        <div class="w-full h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
          <div class="h-full bg-gradient-to-r from-amber-400 to-amber-500 rounded-full transition-all" style="width: 78%"></div>
        </div>
        <div class="flex flex-wrap gap-2 py-2">
          <span class="text-xs bg-[#2463eb]/10 text-[#2463eb] px-2 py-1 rounded font-bold">Figma ✓</span>
          <span class="text-xs bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded">Prototyping</span>
          <span class="text-xs bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded">User Research</span>
        </div>
        <div class="flex items-center justify-between pt-4 border-t border-slate-100 dark:border-slate-800">
          <div class="flex items-center gap-4">
            <p class="text-slate-600 dark:text-slate-400 font-bold text-sm">Thỏa thuận</p>
            <span class="text-xs text-slate-400">• Đăng 5 ngày trước</span>
          </div>
          <div class="flex items-center gap-2">
            <button class="px-4 py-2 rounded-lg text-sm font-bold text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
              Xem chi tiết
            </button>
            <button class="bg-[#2463eb]/10 text-[#2463eb] hover:bg-[#2463eb] hover:text-white px-5 py-2 rounded-lg text-sm font-bold transition-all">
              Ứng tuyển ngay
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Load More -->
  <div class="flex justify-center mt-8">
    <button class="flex items-center gap-2 px-8 py-3 rounded-lg border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 font-bold text-sm transition-colors">
      <span class="material-symbols-outlined text-[18px]">expand_more</span>
      Xem thêm 21 việc làm phù hợp
    </button>
  </div>
</template>

<script setup>
</script>
