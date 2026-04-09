<template>
  <!-- Dashboard Welcome -->
  <div class="flex justify-between items-end">
    <div>
      <h1 class="text-2xl font-bold text-slate-900 dark:text-white">Chào buổi sáng, A!</h1>
      <p class="text-slate-500">Cùng tìm kiếm cơ hội nghề nghiệp tuyệt vời hôm nay.</p>
    </div>
    <button class="bg-[#2463eb] text-white px-4 py-2 rounded-lg font-medium flex items-center gap-2 shadow-lg shadow-[#2463eb]/20 hover:bg-[#2463eb]/90 transition-all">
      <span class="material-symbols-outlined text-xl">upload_file</span>
      Cập nhật CV
    </button>
  </div>

  <!-- Stats Cards -->
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
    <div class="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800">
      <div class="flex justify-between items-start mb-4">
        <div class="p-2 bg-[#2463eb]/10 rounded-lg text-[#2463eb]">
          <span class="material-symbols-outlined">find_in_page</span>
        </div>
        <span class="text-green-500 text-xs font-bold bg-green-50 dark:bg-green-900/20 px-2 py-1 rounded">+12%</span>
      </div>
      <p class="text-slate-500 text-sm font-medium mb-1">Số việc phù hợp</p>
      <h3 class="text-2xl font-bold">128</h3>
    </div>
    <div class="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800">
      <div class="flex justify-between items-start mb-4">
        <div class="p-2 bg-[#2463eb]/10 rounded-lg text-[#2463eb]">
          <span class="material-symbols-outlined">assignment_turned_in</span>
        </div>
        <span class="text-green-500 text-xs font-bold bg-green-50 dark:bg-green-900/20 px-2 py-1 rounded">+2%</span>
      </div>
      <p class="text-slate-500 text-sm font-medium mb-1">Số lần ứng tuyển</p>
      <h3 class="text-2xl font-bold">15</h3>
    </div>
    <div class="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800">
      <div class="flex justify-between items-start mb-4">
        <div class="p-2 bg-[#2463eb]/10 rounded-lg text-[#2463eb]">
          <span class="material-symbols-outlined">trending_up</span>
        </div>
        <span class="text-green-500 text-xs font-bold bg-green-50 dark:bg-green-900/20 px-2 py-1 rounded">+5%</span>
      </div>
      <p class="text-slate-500 text-sm font-medium mb-1">Matching score TB</p>
      <h3 class="text-2xl font-bold">85%</h3>
    </div>
    <div class="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800">
      <div class="flex justify-between items-start mb-4">
        <div class="p-2 bg-[#2463eb]/10 rounded-lg text-[#2463eb]">
          <span class="material-symbols-outlined">psychology</span>
        </div>
        <span class="text-green-500 text-xs font-bold bg-green-50 dark:bg-green-900/20 px-2 py-1 rounded">+1</span>
      </div>
      <p class="text-slate-500 text-sm font-medium mb-1">Kỹ năng hiện có</p>
      <h3 class="text-2xl font-bold">12</h3>
    </div>
  </div>

  <!-- Suggested Jobs -->
  <section class="space-y-6">
    <div class="flex items-center justify-between">
      <h2 class="text-xl font-bold flex items-center gap-2">
        <span class="material-symbols-outlined text-[#2463eb]">recommend</span>
        Việc làm phù hợp cho bạn
      </h2>
      <a class="text-[#2463eb] font-medium text-sm hover:underline" href="#">Xem tất cả</a>
    </div>
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Job Card 1 -->
      <div class="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 hover:border-[#2463eb]/50 transition-all group">
        <div class="flex items-start gap-4 mb-4">
          <div class="size-16 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center overflow-hidden shrink-0 border border-slate-100 dark:border-slate-700"></div>
          <div class="flex-1">
            <div class="flex justify-between">
              <span class="text-[10px] font-bold text-[#2463eb] bg-[#2463eb]/10 px-2 py-0.5 rounded uppercase">Hot Job</span>
              <button class="text-slate-400 hover:text-[#2463eb] transition-colors">
                <span class="material-symbols-outlined">bookmark</span>
              </button>
            </div>
            <h3 class="font-bold text-lg group-hover:text-[#2463eb] transition-colors">Senior Frontend Developer</h3>
            <p class="text-slate-500 text-sm">TechCorp Solutions • Quận 1, TP.HCM</p>
          </div>
        </div>
        <div class="space-y-3">
          <div class="flex justify-between items-center text-sm mb-1">
            <span class="font-medium text-slate-600 dark:text-slate-400">Matching Score</span>
            <span class="font-bold text-[#2463eb]">92%</span>
          </div>
          <div class="w-full h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
            <div class="h-full bg-[#2463eb] rounded-full" style="width: 92%"></div>
          </div>
          <div class="flex flex-wrap gap-2 py-2">
            <span class="text-xs bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded">ReactJS</span>
            <span class="text-xs bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded">TypeScript</span>
            <span class="text-xs bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded">Tailwind</span>
          </div>
          <div class="flex items-center justify-between pt-4 border-t border-slate-100 dark:border-slate-800">
            <p class="text-slate-600 dark:text-slate-400 font-bold text-sm">$2,500 - $3,500</p>
            <button class="bg-[#2463eb]/10 text-[#2463eb] hover:bg-[#2463eb] hover:text-white px-4 py-2 rounded-lg text-sm font-bold transition-all">
              Ứng tuyển ngay
            </button>
          </div>
        </div>
      </div>
      <!-- Job Card 2 -->
      <div class="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 hover:border-[#2463eb]/50 transition-all group">
        <div class="flex items-start gap-4 mb-4">
          <div class="size-16 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center overflow-hidden shrink-0 border border-slate-100 dark:border-slate-700"></div>
          <div class="flex-1">
            <div class="flex justify-between">
              <span class="text-[10px] font-bold text-[#2463eb] bg-[#2463eb]/10 px-2 py-0.5 rounded uppercase">New</span>
              <button class="text-slate-400 hover:text-[#2463eb] transition-colors">
                <span class="material-symbols-outlined">bookmark</span>
              </button>
            </div>
            <h3 class="font-bold text-lg group-hover:text-[#2463eb] transition-colors">UI/UX Product Designer</h3>
            <p class="text-slate-500 text-sm">Innovate Labs • Quận 7, TP.HCM</p>
          </div>
        </div>
        <div class="space-y-3">
          <div class="flex justify-between items-center text-sm mb-1">
            <span class="font-medium text-slate-600 dark:text-slate-400">Matching Score</span>
            <span class="font-bold text-[#2463eb]">78%</span>
          </div>
          <div class="w-full h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
            <div class="h-full bg-[#2463eb] rounded-full" style="width: 78%"></div>
          </div>
          <div class="flex flex-wrap gap-2 py-2">
            <span class="text-xs bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded">Figma</span>
            <span class="text-xs bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded">Prototyping</span>
            <span class="text-xs bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded">English</span>
          </div>
          <div class="flex items-center justify-between pt-4 border-t border-slate-100 dark:border-slate-800">
            <p class="text-slate-600 dark:text-slate-400 font-bold text-sm">Thỏa thuận</p>
            <button class="bg-[#2463eb]/10 text-[#2463eb] hover:bg-[#2463eb] hover:text-white px-4 py-2 rounded-lg text-sm font-bold transition-all">
              Ứng tuyển ngay
            </button>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- AI Assistant Promo -->
  <div class="relative bg-gradient-to-r from-[#2463eb] to-indigo-600 rounded-2xl p-8 text-white overflow-hidden">
    <div class="relative z-10 max-w-lg">
      <h3 class="text-2xl font-bold mb-2">Tăng tỷ lệ ứng tuyển thành công 30%</h3>
      <p class="text-primary-100 mb-6 opacity-90">Sử dụng AI của chúng tôi để phân tích CV và so khớp với mô tả công việc, giúp bạn tối ưu hóa hồ sơ ngay lập tức.</p>
      <button class="bg-white text-[#2463eb] px-6 py-2.5 rounded-lg font-bold shadow-lg hover:bg-slate-50 transition-colors flex items-center gap-2">
        <span class="material-symbols-outlined">auto_awesome</span>
        Thử AI Advisor ngay
      </button>
    </div>
    <div class="absolute right-0 top-0 h-full w-1/3 opacity-20 pointer-events-none">
      <span class="material-symbols-outlined text-[200px] absolute -right-10 -top-10 rotate-12">auto_awesome</span>
    </div>
  </div>
</template>

<script setup>
</script>
