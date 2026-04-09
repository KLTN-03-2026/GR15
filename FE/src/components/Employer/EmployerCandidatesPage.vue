<template>
  <div class="max-w-6xl mx-auto">
    <!-- Header & Tabs -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-4">
      <div>
        <h3 class="text-slate-900 dark:text-slate-100 text-3xl font-bold leading-tight">Ứng viên</h3>
        <p class="text-slate-500 text-sm mt-1">Đang xem 124 ứng viên cho 8 vị trí đang tuyển</p>
      </div>
      <button class="inline-flex items-center justify-center gap-2 px-4 py-2 bg-[#2463eb] text-white rounded-lg font-bold text-sm shadow-lg shadow-[#2463eb]/20 hover:scale-[1.02] transition-transform">
        <span class="material-symbols-outlined text-[18px]">add</span>
        Thêm ứng viên
      </button>
    </div>

    <!-- Secondary Nav & Filters -->
    <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden mb-6">
      <div class="flex border-b border-slate-200 dark:border-slate-800 px-6 gap-8 overflow-x-auto">
        <a class="flex items-center border-b-2 border-[#2463eb] text-[#2463eb] pb-3 pt-4 font-bold text-sm whitespace-nowrap" href="#">
          Tất cả ứng viên
          <span class="ml-2 bg-[#2463eb]/10 px-2 py-0.5 rounded text-[10px]">124</span>
        </a>
        <a class="flex items-center border-b-2 border-transparent text-slate-500 pb-3 pt-4 font-bold text-sm hover:text-slate-700 whitespace-nowrap" href="#">
          Rút gọn
          <span class="ml-2 bg-slate-100 px-2 py-0.5 rounded text-[10px]">32</span>
        </a>
        <a class="flex items-center border-b-2 border-transparent text-slate-500 pb-3 pt-4 font-bold text-sm hover:text-slate-700 whitespace-nowrap" href="#">
          Đang xem xét
          <span class="ml-2 bg-slate-100 px-2 py-0.5 rounded text-[10px]">18</span>
        </a>
        <a class="flex items-center border-b-2 border-transparent text-slate-500 pb-3 pt-4 font-bold text-sm hover:text-slate-700 whitespace-nowrap" href="#">
          Đã từ chối
        </a>
      </div>

      <!-- Filter Bar -->
      <div class="flex flex-wrap gap-3 p-4 bg-slate-50/50 dark:bg-slate-800/20">
        <button class="flex items-center gap-2 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 px-4 py-2 text-slate-700 dark:text-slate-200 text-sm font-medium hover:border-[#2463eb] transition-colors">
          <span class="material-symbols-outlined text-[18px] text-slate-400">work</span>
          <span>Vị trí: Product Designer</span>
          <span class="material-symbols-outlined text-[18px]">expand_more</span>
        </button>
        <button class="flex items-center gap-2 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 px-4 py-2 text-slate-700 dark:text-slate-200 text-sm font-medium hover:border-[#2463eb] transition-colors">
          <span class="material-symbols-outlined text-[18px] text-slate-400">history</span>
          <span>Kinh nghiệm: 5+ năm</span>
          <span class="material-symbols-outlined text-[18px]">expand_more</span>
        </button>
        <button class="flex items-center gap-2 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 px-4 py-2 text-slate-700 dark:text-slate-200 text-sm font-medium hover:border-[#2463eb] transition-colors">
          <span class="material-symbols-outlined text-[18px] text-slate-400">location_on</span>
          <span>Địa điểm: Remote</span>
          <span class="material-symbols-outlined text-[18px]">expand_more</span>
        </button>
        <button class="flex items-center gap-2 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 px-4 py-2 text-slate-400 text-sm font-medium hover:bg-slate-50 dark:hover:bg-slate-700 ml-auto">
          <span class="material-symbols-outlined text-[18px]">filter_list</span>
          <span>Bộ lọc nâng cao</span>
        </button>
      </div>
    </div>

    <!-- Candidates List -->
    <div class="grid grid-cols-1 gap-4">
      <!-- Candidate Card 1 -->
      <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 hover:shadow-md transition-shadow flex flex-col lg:flex-row lg:items-center gap-6">
        <div class="flex items-center gap-4 flex-1">
          <div class="relative">
            <div class="size-16 rounded-full border-2 border-[#2463eb]/20 p-0.5">
              <div class="w-full h-full rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center">
                <span class="material-symbols-outlined text-slate-400 text-2xl">person</span>
              </div>
            </div>
            <div class="absolute -bottom-1 -right-1 bg-green-500 border-2 border-white dark:border-slate-900 size-4 rounded-full" title="Available now"></div>
          </div>
          <div>
            <h4 class="text-slate-900 dark:text-slate-100 font-bold text-lg">Sarah Jenkins</h4>
            <p class="text-slate-500 text-sm">Senior Product Designer • San Francisco, CA</p>
            <div class="flex items-center gap-2 mt-2">
              <span class="bg-[#2463eb]/10 text-[#2463eb] text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-tight">Design Systems</span>
              <span class="bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-tight">Figma Specialist</span>
            </div>
          </div>
        </div>
        <div class="flex items-center gap-8 lg:px-6 lg:border-x lg:border-slate-100 dark:lg:border-slate-800">
          <div class="flex flex-col items-center">
            <div class="flex items-center gap-1 text-[#2463eb]">
              <span class="material-symbols-outlined text-[20px] fill-1">auto_awesome</span>
              <span class="text-xl font-black">98%</span>
            </div>
            <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">AI Match Score</p>
          </div>
          <div class="flex flex-col">
            <span class="bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300 text-[10px] font-bold px-2.5 py-1 rounded-full uppercase text-center">Interviewing</span>
            <p class="text-[10px] font-medium text-slate-400 text-center mt-1">Vòng 2: Kỹ thuật</p>
          </div>
        </div>
        <div class="flex items-center gap-3 ml-auto">
          <button class="flex items-center justify-center gap-2 h-10 px-4 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 font-bold text-sm hover:bg-slate-200 transition-colors">
            <span class="material-symbols-outlined text-[18px]">chat_bubble</span>
            Nhắn tin
          </button>
          <button class="flex items-center justify-center gap-2 h-10 px-6 rounded-lg bg-[#2463eb] text-white font-bold text-sm hover:bg-[#2463eb]/90 transition-all shadow-md shadow-[#2463eb]/20">
            <span class="material-symbols-outlined text-[18px]">how_to_reg</span>
            Tuyển dụng
          </button>
        </div>
      </div>

      <!-- Candidate Card 2 -->
      <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 hover:shadow-md transition-shadow flex flex-col lg:flex-row lg:items-center gap-6">
        <div class="flex items-center gap-4 flex-1">
          <div class="relative">
            <div class="size-16 rounded-full border-2 border-[#2463eb]/20 p-0.5">
              <div class="w-full h-full rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center">
                <span class="material-symbols-outlined text-slate-400 text-2xl">person</span>
              </div>
            </div>
          </div>
          <div>
            <h4 class="text-slate-900 dark:text-slate-100 font-bold text-lg">Michael Chen</h4>
            <p class="text-slate-500 text-sm">Product Designer • Austin, TX (Remote)</p>
            <div class="flex items-center gap-2 mt-2">
              <span class="bg-[#2463eb]/10 text-[#2463eb] text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-tight">Prototyping</span>
              <span class="bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-tight">UX Research</span>
            </div>
          </div>
        </div>
        <div class="flex items-center gap-8 lg:px-6 lg:border-x lg:border-slate-100 dark:lg:border-slate-800">
          <div class="flex flex-col items-center">
            <div class="flex items-center gap-1 text-[#2463eb]">
              <span class="material-symbols-outlined text-[20px] fill-1">auto_awesome</span>
              <span class="text-xl font-black">84%</span>
            </div>
            <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">AI Match Score</p>
          </div>
          <div class="flex flex-col">
            <span class="bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400 text-[10px] font-bold px-2.5 py-1 rounded-full uppercase text-center">New Application</span>
            <p class="text-[10px] font-medium text-slate-400 text-center mt-1">2 hours ago</p>
          </div>
        </div>
        <div class="flex items-center gap-3 ml-auto">
          <button class="flex items-center justify-center gap-2 h-10 px-4 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 font-bold text-sm hover:bg-slate-200 transition-colors">
            <span class="material-symbols-outlined text-[18px]">chat_bubble</span>
            Nhắn tin
          </button>
          <button class="flex items-center justify-center gap-2 h-10 px-6 rounded-lg bg-[#2463eb] text-white font-bold text-sm hover:bg-[#2463eb]/90 transition-all shadow-md shadow-[#2463eb]/20">
            <span class="material-symbols-outlined text-[18px]">how_to_reg</span>
            Tuyển dụng
          </button>
        </div>
      </div>

      <!-- Candidate Card 3 -->
      <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 hover:shadow-md transition-shadow flex flex-col lg:flex-row lg:items-center gap-6">
        <div class="flex items-center gap-4 flex-1">
          <div class="relative">
            <div class="size-16 rounded-full border-2 border-[#2463eb]/20 p-0.5">
              <div class="w-full h-full rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center">
                <span class="material-symbols-outlined text-slate-400 text-2xl">person</span>
              </div>
            </div>
          </div>
          <div>
            <h4 class="text-slate-900 dark:text-slate-100 font-bold text-lg">Elena Rodriguez</h4>
            <p class="text-slate-500 text-sm">Visual Designer • Madrid, ES (Remote)</p>
            <div class="flex items-center gap-2 mt-2">
              <span class="bg-[#2463eb]/10 text-[#2463eb] text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-tight">UI Design</span>
              <span class="bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-tight">Branding</span>
            </div>
          </div>
        </div>
        <div class="flex items-center gap-8 lg:px-6 lg:border-x lg:border-slate-100 dark:lg:border-slate-800">
          <div class="flex flex-col items-center">
            <div class="flex items-center gap-1 text-slate-400">
              <span class="material-symbols-outlined text-[20px]">auto_awesome</span>
              <span class="text-xl font-black">72%</span>
            </div>
            <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">AI Match Score</p>
          </div>
          <div class="flex flex-col">
            <span class="bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300 text-[10px] font-bold px-2.5 py-1 rounded-full uppercase text-center">Đang xem xét</span>
            <p class="text-[10px] font-medium text-slate-400 text-center mt-1">Applied Oct 12</p>
          </div>
        </div>
        <div class="flex items-center gap-3 ml-auto">
          <button class="flex items-center justify-center gap-2 h-10 px-4 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 font-bold text-sm hover:bg-slate-200 transition-colors">
            <span class="material-symbols-outlined text-[18px]">chat_bubble</span>
            Nhắn tin
          </button>
          <button class="flex items-center justify-center gap-2 h-10 px-6 rounded-lg bg-[#2463eb] text-white font-bold text-sm hover:bg-[#2463eb]/90 transition-all shadow-md shadow-[#2463eb]/20">
            <span class="material-symbols-outlined text-[18px]">how_to_reg</span>
            Tuyển dụng
          </button>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div class="flex items-center justify-between mt-8 px-2">
      <p class="text-sm text-slate-500">Hiển thị 1 đến 10 trong tổng số 124 kết quả</p>
      <div class="flex gap-2">
        <button class="h-9 w-9 flex items-center justify-center rounded-lg border border-slate-200 dark:border-slate-800 text-slate-500 hover:bg-slate-50 disabled:opacity-50" disabled>
          <span class="material-symbols-outlined text-[20px]">chevron_left</span>
        </button>
        <button class="h-9 w-9 flex items-center justify-center rounded-lg bg-[#2463eb] text-white font-bold text-sm">1</button>
        <button class="h-9 w-9 flex items-center justify-center rounded-lg border border-slate-200 dark:border-slate-800 text-slate-600 hover:bg-slate-50 font-bold text-sm">2</button>
        <button class="h-9 w-9 flex items-center justify-center rounded-lg border border-slate-200 dark:border-slate-800 text-slate-600 hover:bg-slate-50 font-bold text-sm">3</button>
        <span class="px-2 self-center text-slate-400">...</span>
        <button class="h-9 w-9 flex items-center justify-center rounded-lg border border-slate-200 dark:border-slate-800 text-slate-600 hover:bg-slate-50 font-bold text-sm">13</button>
        <button class="h-9 w-9 flex items-center justify-center rounded-lg border border-slate-200 dark:border-slate-800 text-slate-500 hover:bg-slate-50">
          <span class="material-symbols-outlined text-[20px]">chevron_right</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
</script>
