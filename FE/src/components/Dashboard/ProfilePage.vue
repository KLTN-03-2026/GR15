<template>
  <div class="max-w-5xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8">
    <!-- Sidebar Profile Card -->
    <aside class="lg:col-span-4 flex flex-col gap-6">
      <div class="bg-white dark:bg-slate-900 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-800">
        <div class="flex flex-col items-center text-center">
          <div class="relative group">
            <div class="size-32 rounded-full overflow-hidden border-4 border-[#2463eb]/20 bg-slate-50 mb-4"></div>
            <button class="absolute bottom-4 right-0 bg-[#2463eb] text-white p-2 rounded-full shadow-lg hover:bg-[#2463eb]/90 transition-transform active:scale-95">
              <span class="material-symbols-outlined text-sm">photo_camera</span>
            </button>
          </div>
          <h3 class="text-xl font-bold text-slate-900 dark:text-slate-100">Nguyen Van A</h3>
          <p class="text-slate-500 dark:text-slate-400 text-sm mb-4">Senior Full Stack Developer</p>
          <div class="w-full h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden mb-2">
            <div class="bg-[#2463eb] h-full w-[85%] rounded-full"></div>
          </div>
          <p class="text-xs font-medium text-slate-400 mb-6">Độ hoàn thiện hồ sơ: 85%</p>
          <button class="w-full bg-[#2463eb] text-white font-bold py-2.5 rounded-lg hover:shadow-lg hover:shadow-[#2463eb]/30 transition-all">Cập nhật CV</button>
        </div>
      </div>
      <div class="bg-white dark:bg-slate-900 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-800">
        <h4 class="font-bold mb-4 flex items-center gap-2">
          <span class="material-symbols-outlined text-[#2463eb]">description</span> Tài liệu
        </h4>
        <div class="space-y-3">
          <div class="flex items-center justify-between p-3 rounded-lg border border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50">
            <div class="flex items-center gap-3">
              <span class="material-symbols-outlined text-red-500">picture_as_pdf</span>
              <div>
                <p class="text-sm font-semibold truncate max-w-[120px]">CV_NguyenVanA.pdf</p>
                <p class="text-[10px] text-slate-400">Thêm ngày 24/10/2023</p>
              </div>
            </div>
            <button class="text-slate-400 hover:text-[#2463eb] transition-colors">
              <span class="material-symbols-outlined">download</span>
            </button>
          </div>
          <label class="cursor-pointer flex flex-col items-center justify-center p-4 border-2 border-dashed border-slate-200 dark:border-slate-800 rounded-lg hover:border-[#2463eb] transition-colors group">
            <span class="material-symbols-outlined text-slate-400 group-hover:text-[#2463eb] mb-1">upload_file</span>
            <p class="text-xs font-medium text-slate-500 group-hover:text-[#2463eb] text-center">Tải CV mới lên (PDF, tối đa 5MB)</p>
            <input class="hidden" type="file" />
          </label>
        </div>
      </div>
    </aside>
    <!-- Main Form Section -->
    <div class="lg:col-span-8 space-y-8">
      <section class="bg-white dark:bg-slate-900 rounded-xl p-8 shadow-sm border border-slate-200 dark:border-slate-800">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-xl font-bold flex items-center gap-2">
            <span class="material-symbols-outlined text-[#2463eb]">person</span> Thông tin cá nhân
          </h3>
          <button class="text-[#2463eb] text-sm font-bold flex items-center gap-1 hover:underline">
            <span class="material-symbols-outlined text-sm">edit</span> Chỉnh sửa
          </button>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="space-y-1">
            <label class="text-sm font-semibold text-slate-500 dark:text-slate-400">Họ và tên</label>
            <input class="w-full bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-800 rounded-lg py-2.5 px-4 focus:ring-2 focus:ring-[#2463eb] focus:border-transparent transition-all" type="text" value="Nguyen Van A" />
          </div>
          <div class="space-y-1">
            <label class="text-sm font-semibold text-slate-500 dark:text-slate-400">Địa chỉ email</label>
            <input class="w-full bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-800 rounded-lg py-2.5 px-4 focus:ring-2 focus:ring-[#2463eb] focus:border-transparent transition-all" type="email" value="vana.nguyen@example.com" />
          </div>
          <div class="space-y-1">
            <label class="text-sm font-semibold text-slate-500 dark:text-slate-400">Số điện thoại</label>
            <input class="w-full bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-800 rounded-lg py-2.5 px-4 focus:ring-2 focus:ring-[#2463eb] focus:border-transparent transition-all" type="tel" value="+84 987 654 321" />
          </div>
          <div class="space-y-1">
            <label class="text-sm font-semibold text-slate-500 dark:text-slate-400">Ngày sinh</label>
            <input class="w-full bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-800 rounded-lg py-2.5 px-4 focus:ring-2 focus:ring-[#2463eb] focus:border-transparent transition-all" type="date" value="1995-05-15" />
          </div>
          <div class="md:col-span-2 space-y-1">
            <label class="text-sm font-semibold text-slate-500 dark:text-slate-400">Địa chỉ</label>
            <input class="w-full bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-800 rounded-lg py-2.5 px-4 focus:ring-2 focus:ring-[#2463eb] focus:border-transparent transition-all" type="text" value="District 1, Ho Chi Minh City, Vietnam" />
          </div>
        </div>
      </section>
      <section class="bg-white dark:bg-slate-900 rounded-xl p-8 shadow-sm border border-slate-200 dark:border-slate-800">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-xl font-bold flex items-center gap-2">
            <span class="material-symbols-outlined text-[#2463eb]">psychology</span> Kỹ năng &amp; Kinh nghiệm
          </h3>
          <button class="bg-[#2463eb]/10 text-[#2463eb] px-4 py-1.5 rounded-lg text-sm font-bold hover:bg-[#2463eb]/20 transition-colors">+ Thêm mới</button>
        </div>
        <div class="space-y-6">
          <div class="p-4 rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30 flex flex-col md:flex-row md:items-center gap-4 justify-between">
            <div class="flex items-center gap-4">
              <div class="size-12 bg-white dark:bg-slate-900 rounded-lg shadow-sm flex items-center justify-center">
                <span class="material-symbols-outlined text-[#F7DF1E]">javascript</span>
              </div>
              <div>
                <p class="font-bold">JavaScript</p>
                <p class="text-xs text-slate-500">Thành thạo nâng cao</p>
              </div>
            </div>
            <div class="flex items-center gap-6">
              <div class="text-right">
                <p class="text-sm font-semibold text-[#2463eb]">5+ năm</p>
              </div>
              <div class="flex gap-1">
                <div class="w-6 h-2 rounded-full bg-[#2463eb]"></div>
                <div class="w-6 h-2 rounded-full bg-[#2463eb]"></div>
                <div class="w-6 h-2 rounded-full bg-[#2463eb]"></div>
                <div class="w-6 h-2 rounded-full bg-slate-200 dark:bg-slate-700"></div>
              </div>
            </div>
          </div>
          <div class="p-4 rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30 flex flex-col md:flex-row md:items-center gap-4 justify-between">
            <div class="flex items-center gap-4">
              <div class="size-12 bg-white dark:bg-slate-900 rounded-lg shadow-sm flex items-center justify-center">
                <span class="material-symbols-outlined text-[#42B883]">hexagon</span>
              </div>
              <div>
                <p class="font-bold">VueJS</p>
                <p class="text-xs text-slate-500">Mức chuyên gia</p>
              </div>
            </div>
            <div class="flex items-center gap-6">
              <div class="text-right">
                <p class="text-sm font-semibold text-[#2463eb]">4 năm</p>
              </div>
              <div class="flex gap-1">
                <div class="w-6 h-2 rounded-full bg-[#2463eb]"></div>
                <div class="w-6 h-2 rounded-full bg-[#2463eb]"></div>
                <div class="w-6 h-2 rounded-full bg-[#2463eb]"></div>
                <div class="w-6 h-2 rounded-full bg-[#2463eb]"></div>
              </div>
            </div>
          </div>
        </div>
      </section>
      <div class="flex justify-end gap-4 pb-12">
        <button class="px-8 py-3 rounded-lg border border-slate-300 dark:border-slate-700 font-bold hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">Hủy thay đổi</button>
        <button class="px-8 py-3 rounded-lg bg-[#2463eb] text-white font-bold hover:shadow-lg transition-all">Lưu hồ sơ</button>
      </div>
    </div>
  </div>
</template>

<script setup>
</script>
