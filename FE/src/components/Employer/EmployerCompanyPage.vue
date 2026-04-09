<template>
  <div class="max-w-5xl mx-auto">
    <!-- Page Header -->
    <div class="flex justify-between items-end mb-8">
      <div>
        <h1 class="text-2xl font-bold text-slate-900 dark:text-white">Thông tin công ty</h1>
        <p class="text-slate-500 text-sm mt-1">Quản lý hồ sơ công ty để thu hút ứng viên tốt hơn.</p>
      </div>
      <button class="bg-[#2463eb] text-white px-5 py-2.5 rounded-lg font-bold flex items-center gap-2 shadow-lg shadow-[#2463eb]/20 hover:bg-[#2463eb]/90 transition-all text-sm">
        <span class="material-symbols-outlined text-xl">save</span>
        Lưu thay đổi
      </button>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
      <!-- Sidebar -->
      <aside class="lg:col-span-4 flex flex-col gap-6">
        <!-- Company Logo & Info -->
        <div class="bg-white dark:bg-slate-900 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-800">
          <div class="flex flex-col items-center text-center">
            <div class="relative group mb-4">
              <div class="size-28 rounded-2xl overflow-hidden border-4 border-[#2463eb]/20 bg-slate-50 dark:bg-slate-800 flex items-center justify-center">
                <span class="material-symbols-outlined text-slate-300 text-5xl">domain</span>
              </div>
              <button class="absolute bottom-0 right-0 bg-[#2463eb] text-white p-2 rounded-lg shadow-lg hover:bg-[#2463eb]/90 transition-transform active:scale-95">
                <span class="material-symbols-outlined text-sm">photo_camera</span>
              </button>
            </div>
            <h3 class="text-xl font-bold text-slate-900 dark:text-white">TechCorp Solutions</h3>
            <p class="text-slate-500 text-sm">Công nghệ thông tin</p>
            <div class="flex items-center gap-1 mt-2">
              <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400">
                <span class="size-1.5 rounded-full bg-green-500"></span> Đã xác minh
              </span>
            </div>
            <div class="w-full h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden mt-4 mb-2">
              <div class="bg-[#2463eb] h-full w-[75%] rounded-full"></div>
            </div>
            <p class="text-xs font-medium text-slate-400">Hồ sơ hoàn thiện: 75%</p>
          </div>
        </div>

        <!-- Quick Stats -->
        <div class="bg-white dark:bg-slate-900 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-800">
          <h4 class="font-bold mb-4 flex items-center gap-2">
            <span class="material-symbols-outlined text-[#2463eb]">analytics</span> Thống kê nhanh
          </h4>
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <span class="text-sm text-slate-500">Tin tuyển dụng</span>
              <span class="font-bold">12</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-slate-500">Tổng ứng viên</span>
              <span class="font-bold">1,284</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-slate-500">Đã tuyển</span>
              <span class="font-bold text-green-600">23</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-slate-500">Lượt xem hồ sơ</span>
              <span class="font-bold">5,842</span>
            </div>
          </div>
        </div>
      </aside>

      <!-- Main Form -->
      <div class="lg:col-span-8 space-y-6">
        <!-- Basic Info -->
        <section class="bg-white dark:bg-slate-900 rounded-xl p-8 shadow-sm border border-slate-200 dark:border-slate-800">
          <h3 class="text-lg font-bold flex items-center gap-2 mb-6">
            <span class="material-symbols-outlined text-[#2463eb]">domain</span> Thông tin cơ bản
          </h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="space-y-1">
              <label class="text-sm font-semibold text-slate-500 dark:text-slate-400">Tên công ty</label>
              <input class="w-full bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800 rounded-lg py-2.5 px-4 focus:ring-2 focus:ring-[#2463eb] focus:border-transparent transition-all" type="text" value="TechCorp Solutions" />
            </div>
            <div class="space-y-1">
              <label class="text-sm font-semibold text-slate-500 dark:text-slate-400">Ngành nghề</label>
              <select class="w-full bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800 rounded-lg py-2.5 px-4 focus:ring-2 focus:ring-[#2463eb] focus:border-transparent transition-all">
                <option selected>Công nghệ thông tin</option>
                <option>Tài chính - Ngân hàng</option>
                <option>Marketing</option>
                <option>Giáo dục</option>
              </select>
            </div>
            <div class="space-y-1">
              <label class="text-sm font-semibold text-slate-500 dark:text-slate-400">Email liên hệ</label>
              <input class="w-full bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800 rounded-lg py-2.5 px-4 focus:ring-2 focus:ring-[#2463eb] focus:border-transparent transition-all" type="email" value="hr@techcorp.vn" />
            </div>
            <div class="space-y-1">
              <label class="text-sm font-semibold text-slate-500 dark:text-slate-400">Số điện thoại</label>
              <input class="w-full bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800 rounded-lg py-2.5 px-4 focus:ring-2 focus:ring-[#2463eb] focus:border-transparent transition-all" type="tel" value="+84 28 3456 7890" />
            </div>
            <div class="space-y-1">
              <label class="text-sm font-semibold text-slate-500 dark:text-slate-400">Website</label>
              <input class="w-full bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800 rounded-lg py-2.5 px-4 focus:ring-2 focus:ring-[#2463eb] focus:border-transparent transition-all" type="url" value="https://techcorp.vn" />
            </div>
            <div class="space-y-1">
              <label class="text-sm font-semibold text-slate-500 dark:text-slate-400">Quy mô</label>
              <select class="w-full bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800 rounded-lg py-2.5 px-4 focus:ring-2 focus:ring-[#2463eb] focus:border-transparent transition-all">
                <option>1-10 nhân viên</option>
                <option>11-50 nhân viên</option>
                <option selected>51-200 nhân viên</option>
                <option>201-500 nhân viên</option>
                <option>500+ nhân viên</option>
              </select>
            </div>
            <div class="md:col-span-2 space-y-1">
              <label class="text-sm font-semibold text-slate-500 dark:text-slate-400">Địa chỉ</label>
              <input class="w-full bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800 rounded-lg py-2.5 px-4 focus:ring-2 focus:ring-[#2463eb] focus:border-transparent transition-all" type="text" value="123 Nguyễn Huệ, Quận 1, TP. Hồ Chí Minh" />
            </div>
          </div>
        </section>

        <!-- Description -->
        <section class="bg-white dark:bg-slate-900 rounded-xl p-8 shadow-sm border border-slate-200 dark:border-slate-800">
          <h3 class="text-lg font-bold flex items-center gap-2 mb-6">
            <span class="material-symbols-outlined text-[#2463eb]">article</span> Giới thiệu công ty
          </h3>
          <div class="space-y-1">
            <label class="text-sm font-semibold text-slate-500 dark:text-slate-400">Mô tả</label>
            <textarea class="w-full bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800 rounded-lg py-3 px-4 focus:ring-2 focus:ring-[#2463eb] focus:border-transparent transition-all resize-none" rows="5" placeholder="Mô tả về công ty, văn hóa, sứ mệnh...">TechCorp Solutions là công ty công nghệ hàng đầu chuyên cung cấp giải pháp phần mềm cho doanh nghiệp. Với đội ngũ hơn 150 kỹ sư giàu kinh nghiệm, chúng tôi tự hào mang đến các sản phẩm chất lượng cao cho khách hàng trong và ngoài nước.</textarea>
          </div>
        </section>

        <!-- Benefits -->
        <section class="bg-white dark:bg-slate-900 rounded-xl p-8 shadow-sm border border-slate-200 dark:border-slate-800">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-lg font-bold flex items-center gap-2">
              <span class="material-symbols-outlined text-[#2463eb]">workspace_premium</span> Phúc lợi
            </h3>
            <button class="bg-[#2463eb]/10 text-[#2463eb] px-4 py-1.5 rounded-lg text-sm font-bold hover:bg-[#2463eb]/20 transition-colors">+ Thêm</button>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div class="flex items-center gap-3 p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800">
              <span class="material-symbols-outlined text-green-500">check_circle</span>
              <span class="text-sm font-medium">Bảo hiểm sức khỏe cao cấp</span>
            </div>
            <div class="flex items-center gap-3 p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800">
              <span class="material-symbols-outlined text-green-500">check_circle</span>
              <span class="text-sm font-medium">13 tháng lương + Bonus</span>
            </div>
            <div class="flex items-center gap-3 p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800">
              <span class="material-symbols-outlined text-green-500">check_circle</span>
              <span class="text-sm font-medium">Flexible working hours</span>
            </div>
            <div class="flex items-center gap-3 p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800">
              <span class="material-symbols-outlined text-green-500">check_circle</span>
              <span class="text-sm font-medium">Training & Development</span>
            </div>
            <div class="flex items-center gap-3 p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800">
              <span class="material-symbols-outlined text-green-500">check_circle</span>
              <span class="text-sm font-medium">15 ngày phép/năm</span>
            </div>
            <div class="flex items-center gap-3 p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800">
              <span class="material-symbols-outlined text-green-500">check_circle</span>
              <span class="text-sm font-medium">Team building hàng quý</span>
            </div>
          </div>
        </section>

        <!-- Action Buttons -->
        <div class="flex justify-end gap-4 pb-8">
          <button class="px-8 py-3 rounded-lg border border-slate-300 dark:border-slate-700 font-bold hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">Hủy thay đổi</button>
          <button class="px-8 py-3 rounded-lg bg-[#2463eb] text-white font-bold hover:shadow-lg transition-all">Lưu thông tin</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
</script>
