<template>
  <div>
    <!-- Page Header -->
    <div class="flex flex-wrap items-center justify-between gap-4 mb-6">
      <div class="flex flex-col gap-1">
        <h2 class="text-slate-900 dark:text-slate-100 text-3xl font-extrabold leading-tight tracking-tight">Phỏng vấn</h2>
        <p class="text-slate-500 text-sm font-normal">Xem lại và quản lý các buổi đánh giá ứng viên sắp tới</p>
      </div>
      <button class="flex items-center justify-center gap-2 rounded-lg h-11 px-6 bg-[#2463eb] text-white text-sm font-bold shadow-md hover:bg-blue-700 transition-all">
        <span class="material-symbols-outlined text-lg">add</span>
        <span>Lên lịch phỏng vấn</span>
      </button>
    </div>

    <!-- Tabs -->
    <div class="mb-6">
      <div class="flex border-b border-slate-200 dark:border-slate-800 gap-8">
        <a class="flex items-center gap-2 border-b-2 border-[#2463eb] text-[#2463eb] pb-3 pt-4 font-semibold text-sm" href="#">
          <span class="material-symbols-outlined text-sm">view_list</span>
          Dạng danh sách
        </a>
        <a class="flex items-center gap-2 border-b-2 border-transparent text-slate-500 hover:text-slate-700 pb-3 pt-4 font-semibold text-sm" href="#">
          <span class="material-symbols-outlined text-sm">calendar_month</span>
          Dạng lịch
        </a>
      </div>
    </div>

    <!-- Content Area -->
    <div class="flex flex-col lg:flex-row gap-8">
      <!-- Interview List -->
      <div class="flex-1 flex flex-col gap-4">
        <!-- Today -->
        <div class="flex items-center justify-between py-2">
          <h3 class="text-slate-900 dark:text-slate-100 font-bold">Lịch hôm nay</h3>
          <span class="text-xs text-slate-400 font-medium">3 buổi phỏng vấn đã lên lịch</span>
        </div>
        <div class="space-y-3">
          <!-- Interview Card 1 -->
          <div class="bg-white dark:bg-slate-900 rounded-xl p-4 shadow-sm border border-slate-100 dark:border-slate-800 flex flex-wrap items-center justify-between gap-4">
            <div class="flex items-center gap-4">
              <div class="h-12 w-12 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden flex items-center justify-center text-slate-500">
                <span class="material-symbols-outlined">person</span>
              </div>
              <div>
                <h4 class="text-slate-900 dark:text-slate-100 font-bold text-base">Sarah Jenkins</h4>
                <p class="text-slate-500 text-sm">Senior Product Designer</p>
              </div>
            </div>
            <div class="flex items-center gap-8">
              <div class="flex flex-col">
                <span class="text-slate-400 text-[10px] font-bold uppercase tracking-wider">Date &amp; Time</span>
                <p class="text-slate-700 dark:text-slate-300 text-sm font-semibold">Today, 2:00 PM</p>
              </div>
              <a class="flex items-center gap-2 text-[#2463eb] hover:underline text-sm font-semibold" href="#">
                <span class="material-symbols-outlined text-lg">videocam</span>
                Tham gia Zoom
              </a>
            </div>
            <button class="text-slate-400 hover:text-slate-600">
              <span class="material-symbols-outlined">more_vert</span>
            </button>
          </div>

          <!-- Interview Card 2 -->
          <div class="bg-white dark:bg-slate-900 rounded-xl p-4 shadow-sm border border-slate-100 dark:border-slate-800 flex flex-wrap items-center justify-between gap-4">
            <div class="flex items-center gap-4">
              <div class="h-12 w-12 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden flex items-center justify-center text-slate-500">
                <span class="material-symbols-outlined">person</span>
              </div>
              <div>
                <h4 class="text-slate-900 dark:text-slate-100 font-bold text-base">Michael Chen</h4>
                <p class="text-slate-500 text-sm">Frontend Engineer</p>
              </div>
            </div>
            <div class="flex items-center gap-8">
              <div class="flex flex-col">
                <span class="text-slate-400 text-[10px] font-bold uppercase tracking-wider">Date &amp; Time</span>
                <p class="text-slate-700 dark:text-slate-300 text-sm font-semibold">Today, 4:30 PM</p>
              </div>
              <a class="flex items-center gap-2 text-[#2463eb] hover:underline text-sm font-semibold" href="#">
                <span class="material-symbols-outlined text-lg">videocam</span>
                Google Meet
              </a>
            </div>
            <button class="text-slate-400 hover:text-slate-600">
              <span class="material-symbols-outlined">more_vert</span>
            </button>
          </div>
        </div>

        <!-- Tomorrow -->
        <div class="flex items-center justify-between py-2 mt-4">
          <h3 class="text-slate-900 dark:text-slate-100 font-bold">Ngày mai</h3>
          <span class="text-xs text-slate-400 font-medium">Oct 26, 2023</span>
        </div>
        <div class="space-y-3">
          <!-- Interview Card 3 -->
          <div class="bg-white dark:bg-slate-900 rounded-xl p-4 shadow-sm border border-slate-100 dark:border-slate-800 flex flex-wrap items-center justify-between gap-4">
            <div class="flex items-center gap-4">
              <div class="h-12 w-12 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden flex items-center justify-center text-slate-500">
                <span class="material-symbols-outlined">person</span>
              </div>
              <div>
                <h4 class="text-slate-900 dark:text-slate-100 font-bold text-base">Elena Rodriguez</h4>
                <p class="text-slate-500 text-sm">Marketing Manager</p>
              </div>
            </div>
            <div class="flex items-center gap-8">
              <div class="flex flex-col">
                <span class="text-slate-400 text-[10px] font-bold uppercase tracking-wider">Date &amp; Time</span>
                <p class="text-slate-700 dark:text-slate-300 text-sm font-semibold">Ngày mai, 10:00 AM</p>
              </div>
              <a class="flex items-center gap-2 text-[#2463eb] hover:underline text-sm font-semibold" href="#">
                <span class="material-symbols-outlined text-lg">call</span>
                Gọi điện thoại
              </a>
            </div>
            <button class="text-slate-400 hover:text-slate-600">
              <span class="material-symbols-outlined">more_vert</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Right Sidebar: Calendar & Tip -->
      <div class="w-full lg:w-80 flex flex-col gap-6">
        <!-- Mini Calendar -->
        <div class="bg-white dark:bg-slate-900 rounded-xl p-6 shadow-sm border border-slate-100 dark:border-slate-800">
          <div class="flex items-center justify-between mb-4">
            <button class="text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 p-1 rounded">
              <span class="material-symbols-outlined">chevron_left</span>
            </button>
            <h4 class="text-slate-900 dark:text-slate-100 font-bold text-sm">October 2023</h4>
            <button class="text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 p-1 rounded">
              <span class="material-symbols-outlined">chevron_right</span>
            </button>
          </div>
          <div class="grid grid-cols-7 text-center text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2">
            <span>Su</span><span>Mo</span><span>Tu</span><span>We</span><span>Th</span><span>Fr</span><span>Sa</span>
          </div>
          <div class="grid grid-cols-7 text-center gap-y-1">
            <span class="text-slate-300 py-2 text-sm">24</span>
            <span class="text-slate-300 py-2 text-sm">25</span>
            <span class="text-slate-300 py-2 text-sm">26</span>
            <span class="text-slate-300 py-2 text-sm">27</span>
            <span class="text-slate-300 py-2 text-sm">28</span>
            <span class="text-slate-300 py-2 text-sm">29</span>
            <span class="text-slate-300 py-2 text-sm">30</span>
            <span class="text-slate-900 dark:text-slate-100 py-2 text-sm hover:bg-slate-50 dark:hover:bg-slate-800 rounded-full cursor-pointer font-medium">1</span>
            <span class="text-slate-900 dark:text-slate-100 py-2 text-sm hover:bg-slate-50 dark:hover:bg-slate-800 rounded-full cursor-pointer font-medium">2</span>
            <span class="text-slate-900 dark:text-slate-100 py-2 text-sm hover:bg-slate-50 dark:hover:bg-slate-800 rounded-full cursor-pointer font-medium">3</span>
            <span class="text-slate-900 dark:text-slate-100 py-2 text-sm hover:bg-slate-50 dark:hover:bg-slate-800 rounded-full cursor-pointer font-medium">4</span>
            <span class="bg-[#2463eb] text-white py-2 text-sm rounded-full cursor-pointer font-bold shadow-sm">25</span>
            <span class="text-slate-900 dark:text-slate-100 py-2 text-sm hover:bg-slate-50 dark:hover:bg-slate-800 rounded-full cursor-pointer font-medium relative">
              6 <div class="absolute bottom-1 left-1/2 -translate-x-1/2 size-1 bg-[#2463eb] rounded-full"></div>
            </span>
            <span class="text-slate-900 dark:text-slate-100 py-2 text-sm hover:bg-slate-50 dark:hover:bg-slate-800 rounded-full cursor-pointer font-medium">7</span>
            <span class="text-slate-900 dark:text-slate-100 py-2 text-sm hover:bg-slate-50 dark:hover:bg-slate-800 rounded-full cursor-pointer font-medium">8</span>
            <span class="text-slate-900 dark:text-slate-100 py-2 text-sm hover:bg-slate-50 dark:hover:bg-slate-800 rounded-full cursor-pointer font-medium">9</span>
            <span class="text-slate-900 dark:text-slate-100 py-2 text-sm hover:bg-slate-50 dark:hover:bg-slate-800 rounded-full cursor-pointer font-medium relative">
              10 <div class="absolute bottom-1 left-1/2 -translate-x-1/2 size-1 bg-[#2463eb] rounded-full"></div>
            </span>
            <span class="text-slate-900 dark:text-slate-100 py-2 text-sm hover:bg-slate-50 dark:hover:bg-slate-800 rounded-full cursor-pointer font-medium">11</span>
            <span class="text-slate-900 dark:text-slate-100 py-2 text-sm hover:bg-slate-50 dark:hover:bg-slate-800 rounded-full cursor-pointer font-medium">12</span>
            <span class="text-slate-900 dark:text-slate-100 py-2 text-sm hover:bg-slate-50 dark:hover:bg-slate-800 rounded-full cursor-pointer font-medium">13</span>
            <span class="text-slate-900 dark:text-slate-100 py-2 text-sm hover:bg-slate-50 dark:hover:bg-slate-800 rounded-full cursor-pointer font-medium">14</span>
          </div>
        </div>

        <!-- Pro Tip Card -->
        <div class="bg-[#2463eb]/5 rounded-xl p-5 border border-[#2463eb]/10">
          <h4 class="text-[#2463eb] font-bold text-sm mb-2">Mẹo hữu ích</h4>
          <p class="text-slate-600 dark:text-slate-400 text-xs leading-relaxed">
            Connect your Google or Outlook calendar to automatically detect scheduling conflicts and sync meeting links.
          </p>
          <button class="mt-4 text-xs font-bold text-[#2463eb] flex items-center gap-1 hover:gap-2 transition-all">
            Kết nối lịch <span class="material-symbols-outlined text-xs">arrow_forward</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
</script>
