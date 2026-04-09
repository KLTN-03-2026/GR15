<template>
  <div class="max-w-7xl mx-auto px-4 py-8">
    <div class="flex flex-col lg:flex-row gap-8">
      <!-- Filter Sidebar -->
      <aside class="w-full lg:w-64 shrink-0 space-y-6">
        <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm">
          <div class="p-4 border-b border-slate-100 dark:border-slate-800 flex justify-between items-center">
            <h2 class="font-bold text-slate-900 dark:text-white">Bộ lọc</h2>
            <button class="text-xs font-semibold text-[#2463eb] hover:underline">Đặt lại</button>
          </div>
          <div class="p-4 space-y-6">
            <div>
              <label class="flex items-center gap-2 text-sm font-semibold mb-3">
                <span class="material-symbols-outlined text-lg">factory</span> Ngành nghề
              </label>
              <div class="space-y-2">
                <label class="flex items-center gap-2 text-sm cursor-pointer group">
                  <input checked class="rounded border-slate-300 text-[#2463eb] focus:ring-[#2463eb] cursor-pointer" type="checkbox" />
                  <span class="text-slate-600 dark:text-slate-400 group-hover:text-[#2463eb]">Công nghệ</span>
                </label>
                <label class="flex items-center gap-2 text-sm cursor-pointer group">
                  <input class="rounded border-slate-300 text-[#2463eb] focus:ring-[#2463eb] cursor-pointer" type="checkbox" />
                  <span class="text-slate-600 dark:text-slate-400 group-hover:text-[#2463eb]">Tài chính</span>
                </label>
                <label class="flex items-center gap-2 text-sm cursor-pointer group">
                  <input class="rounded border-slate-300 text-[#2463eb] focus:ring-[#2463eb] cursor-pointer" type="checkbox" />
                  <span class="text-slate-600 dark:text-slate-400 group-hover:text-[#2463eb]">Y tế</span>
                </label>
              </div>
            </div>
            <div>
              <label class="flex items-center gap-2 text-sm font-semibold mb-3">
                <span class="material-symbols-outlined text-lg">psychology</span> Kỹ năng
              </label>
              <div class="flex flex-wrap gap-2">
                <span class="px-2 py-1 bg-[#2463eb]/10 text-[#2463eb] text-xs font-medium rounded-lg flex items-center gap-1">
                  React <span class="material-symbols-outlined text-xs cursor-pointer">close</span>
                </span>
                <span class="px-2 py-1 bg-[#2463eb]/10 text-[#2463eb] text-xs font-medium rounded-lg flex items-center gap-1">
                  UI/UX <span class="material-symbols-outlined text-xs cursor-pointer">close</span>
                </span>
                <button class="px-2 py-1 border border-dashed border-slate-300 dark:border-slate-700 text-slate-400 text-xs font-medium rounded-lg">+ Thêm</button>
              </div>
            </div>
            <div>
              <label class="flex items-center gap-2 text-sm font-semibold mb-3">
                <span class="material-symbols-outlined text-lg">payments</span> Mức lương
              </label>
              <input class="w-full accent-[#2463eb]" type="range" />
              <div class="flex justify-between text-xs text-slate-500 mt-2">
                <span>$80k</span>
                <span>$200k+</span>
              </div>
            </div>
            <div>
              <label class="flex items-center gap-2 text-sm font-semibold mb-3">
                <span class="material-symbols-outlined text-lg">clinical_notes</span> Kinh nghiệm
              </label>
              <select class="w-full bg-slate-50 dark:bg-slate-800 border-slate-200 dark:border-slate-700 rounded-lg text-sm focus:ring-[#2463eb]">
                <option>Trung cấp (3-5 năm)</option>
                <option>Mới bắt đầu</option>
                <option>Cấp cao</option>
                <option>Quản lý</option>
              </select>
            </div>
            <div>
              <label class="flex items-center gap-2 text-sm font-semibold mb-3">
                <span class="material-symbols-outlined text-lg">location_on</span> Địa điểm
              </label>
              <div class="relative">
                <span class="material-symbols-outlined absolute left-2 top-1/2 -translate-y-1/2 text-slate-400 text-sm">search</span>
                <input class="w-full pl-8 bg-slate-50 dark:bg-slate-800 border-slate-200 dark:border-slate-700 rounded-lg text-sm focus:ring-[#2463eb]" placeholder="San Francisco, CA" type="text" />
              </div>
            </div>
          </div>
        </div>
      </aside>

      <!-- Job Listings -->
      <section class="flex-1 space-y-6">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-2xl font-bold text-slate-900 dark:text-white">Gợi ý dành cho bạn</h2>
            <p class="text-sm text-slate-500">Dựa trên hồ sơ và lịch sử tìm kiếm của bạn</p>
          </div>
          <div class="flex items-center gap-2 text-sm">
            <span class="text-slate-500">Sắp xếp theo:</span>
            <button class="font-semibold text-slate-900 dark:text-white flex items-center gap-1">
              Phù hợp nhất <span class="material-symbols-outlined text-base">expand_more</span>
            </button>
          </div>
        </div>
        <div class="space-y-4">
          <!-- Job Card 1 -->
          <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm hover:shadow-md hover:border-[#2463eb]/30 transition-all group">
            <div class="flex flex-start gap-4">
              <div class="w-14 h-14 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center shrink-0 border border-slate-200 dark:border-slate-700 overflow-hidden"></div>
              <div class="flex-1">
                <div class="flex justify-between items-start">
                  <div>
                    <h3 class="text-lg font-bold text-slate-900 dark:text-white group-hover:text-[#2463eb] transition-colors">Senior Product Designer</h3>
                    <p class="text-[#2463eb] font-medium text-sm">TechFlow Systems</p>
                  </div>
                  <div class="flex flex-col items-end gap-2">
                    <span class="bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded-full flex items-center gap-1">
                      <span class="material-symbols-outlined text-xs">verified</span> 98% Match
                    </span>
                    <span class="text-xs text-slate-400">2 hours ago</span>
                  </div>
                </div>
                <div class="mt-4 flex flex-wrap items-center gap-y-2 gap-x-6 text-sm text-slate-600 dark:text-slate-400">
                  <div class="flex items-center gap-1.5">
                    <span class="material-symbols-outlined text-base text-slate-400">location_on</span>
                    San Francisco, CA (Remote)
                  </div>
                  <div class="flex items-center gap-1.5">
                    <span class="material-symbols-outlined text-base text-slate-400">payments</span>
                    $140k - $185k
                  </div>
                  <div class="flex items-center gap-1.5">
                    <span class="material-symbols-outlined text-base text-slate-400">work</span>
                    Full-time
                  </div>
                </div>
                <div class="mt-4 flex flex-wrap gap-2">
                  <span class="px-3 py-1 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 text-xs font-medium rounded-full">Figma</span>
                  <span class="px-3 py-1 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 text-xs font-medium rounded-full">Prototyping</span>
                  <span class="px-3 py-1 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 text-xs font-medium rounded-full">Design Systems</span>
                </div>
                <div class="mt-6 flex items-center justify-between">
                  <p class="text-xs text-slate-500 max-w-md line-clamp-1 italic">"We're looking for a visionary designer to lead our next-gen dashboard initiatives..."</p>
                  <div class="flex gap-3">
                    <button class="p-2 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
                      <span class="material-symbols-outlined">bookmark</span>
                    </button>
                    <button class="px-6 py-2 bg-[#2463eb] text-white font-bold rounded-lg hover:bg-[#2463eb]/90 transition-all text-sm shadow-sm">Ứng tuyển ngay</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <!-- Job Card 2 -->
          <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm hover:shadow-md hover:border-[#2463eb]/30 transition-all group">
            <div class="flex flex-start gap-4">
              <div class="w-14 h-14 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center shrink-0 border border-slate-200 dark:border-slate-700 overflow-hidden"></div>
              <div class="flex-1">
                <div class="flex justify-between items-start">
                  <div>
                    <h3 class="text-lg font-bold text-slate-900 dark:text-white group-hover:text-[#2463eb] transition-colors">Frontend Architect</h3>
                    <p class="text-[#2463eb] font-medium text-sm">SoundScape Media</p>
                  </div>
                  <div class="flex flex-col items-end gap-2">
                    <span class="bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded-full flex items-center gap-1">
                      <span class="material-symbols-outlined text-xs">star</span> 85% Match
                    </span>
                    <span class="text-xs text-slate-400">5 hours ago</span>
                  </div>
                </div>
                <div class="mt-4 flex flex-wrap items-center gap-y-2 gap-x-6 text-sm text-slate-600 dark:text-slate-400">
                  <div class="flex items-center gap-1.5">
                    <span class="material-symbols-outlined text-base text-slate-400">location_on</span>
                    New York, NY
                  </div>
                  <div class="flex items-center gap-1.5">
                    <span class="material-symbols-outlined text-base text-slate-400">payments</span>
                    $160k - $210k
                  </div>
                  <div class="flex items-center gap-1.5">
                    <span class="material-symbols-outlined text-base text-slate-400">work</span>
                    Hybrid
                  </div>
                </div>
                <div class="mt-4 flex flex-wrap gap-2">
                  <span class="px-3 py-1 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 text-xs font-medium rounded-full">React</span>
                  <span class="px-3 py-1 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 text-xs font-medium rounded-full">TypeScript</span>
                  <span class="px-3 py-1 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 text-xs font-medium rounded-full">GraphQL</span>
                </div>
                <div class="mt-6 flex items-center justify-between">
                  <p class="text-xs text-slate-500 max-w-md line-clamp-1 italic">"Join a world-class team building the future of audio discovery..."</p>
                  <div class="flex gap-3">
                    <button class="p-2 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
                      <span class="material-symbols-outlined">bookmark</span>
                    </button>
                    <button class="px-6 py-2 bg-[#2463eb] text-white font-bold rounded-lg hover:bg-[#2463eb]/90 transition-all text-sm shadow-sm">Ứng tuyển ngay</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="flex justify-center pt-8">
          <button class="flex items-center gap-2 text-[#2463eb] font-bold hover:gap-3 transition-all">
            Xem thêm kết quả
            <span class="material-symbols-outlined">arrow_forward</span>
          </button>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
</script>
