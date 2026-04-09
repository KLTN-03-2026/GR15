<template>
  <div class="flex flex-wrap items-center justify-between gap-4 mb-8">
    <div>
      <h1 class="text-3xl font-black text-slate-900 dark:text-white tracking-tight">Bảng điều khiển doanh nghiệp</h1>
      <p class="text-slate-500 dark:text-slate-400 text-base mt-1">Chào mừng quay lại, John! Đây là tổng quan tuyển dụng hôm nay của bạn.</p>
    </div>
    <button class="flex items-center gap-2 px-6 py-3 bg-[#2463eb] text-white rounded-xl font-bold text-sm shadow-lg shadow-[#2463eb]/20 hover:scale-[1.02] active:scale-95 transition-all">
      <span class="material-symbols-outlined text-xl">add</span>
      Đăng tin mới
    </button>
  </div>

  <!-- Stats Cards -->
  <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
    <div class="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 flex flex-col gap-2">
      <div class="flex items-center justify-between">
        <p class="text-slate-500 dark:text-slate-400 text-sm font-medium">Tổng tin đang tuyển</p>
        <span class="material-symbols-outlined text-[#2463eb] bg-[#2463eb]/10 p-2 rounded-lg">work</span>
      </div>
      <p class="text-3xl font-bold text-slate-900 dark:text-white">12</p>
      <div class="flex items-center gap-1 text-emerald-600 dark:text-emerald-400 text-sm font-semibold">
        <span class="material-symbols-outlined text-sm">trending_up</span>
        <span>+2 trong tháng</span>
      </div>
    </div>
    <div class="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 flex flex-col gap-2">
      <div class="flex items-center justify-between">
        <p class="text-slate-500 dark:text-slate-400 text-sm font-medium">Tổng ứng viên</p>
        <span class="material-symbols-outlined text-[#2463eb] bg-[#2463eb]/10 p-2 rounded-lg">groups</span>
      </div>
      <p class="text-3xl font-bold text-slate-900 dark:text-white">1,284</p>
      <div class="flex items-center gap-1 text-emerald-600 dark:text-emerald-400 text-sm font-semibold">
        <span class="material-symbols-outlined text-sm">trending_up</span>
        <span>Tăng 15%</span>
      </div>
    </div>
    <div class="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 flex flex-col gap-2">
      <div class="flex items-center justify-between">
        <p class="text-slate-500 dark:text-slate-400 text-sm font-medium">Hồ sơ mới hôm nay</p>
        <span class="material-symbols-outlined text-[#2463eb] bg-[#2463eb]/10 p-2 rounded-lg">description</span>
      </div>
      <p class="text-3xl font-bold text-slate-900 dark:text-white">48</p>
      <div class="flex items-center gap-1 text-emerald-600 dark:text-emerald-400 text-sm font-semibold">
        <span class="material-symbols-outlined text-sm">trending_up</span>
        <span>Nhiều hơn hôm qua 12 hồ sơ</span>
      </div>
    </div>
  </div>

  <!-- Job Management Table -->
  <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden">
    <div class="p-6 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
      <h2 class="text-xl font-bold text-slate-900 dark:text-white">Tin tuyển dụng gần đây</h2>
      <div class="flex gap-2">
        <button class="px-3 py-1.5 text-sm font-medium border border-slate-200 dark:border-slate-800 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800">Lọc</button>
        <button class="px-3 py-1.5 text-sm font-medium border border-slate-200 dark:border-slate-800 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800">Xuất file</button>
      </div>
    </div>
    <div class="overflow-x-auto">
      <table class="w-full text-left border-collapse">
        <thead>
          <tr class="bg-slate-50 dark:bg-slate-800/50">
            <th class="px-6 py-4 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Vị trí</th>
            <th class="px-6 py-4 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Ngành</th>
            <th class="px-6 py-4 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider text-center">Candidates</th>
            <th class="px-6 py-4 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Status</th>
            <th class="px-6 py-4 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-200 dark:divide-slate-800">
          <tr class="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
            <td class="px-6 py-4">
              <div class="flex flex-col">
                <span class="text-sm font-bold text-slate-900 dark:text-white">Senior Product Designer</span>
                <span class="text-xs text-slate-500">Full-time • Remote</span>
              </div>
            </td>
            <td class="px-6 py-4 text-sm text-slate-600 dark:text-slate-400 font-medium">Design &amp; UX</td>
            <td class="px-6 py-4 text-center">
              <span class="px-2.5 py-1 text-xs font-bold bg-slate-100 dark:bg-slate-800 rounded-full text-slate-900 dark:text-slate-100">124</span>
            </td>
            <td class="px-6 py-4">
              <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> Đang tuyển
              </span>
            </td>
            <td class="px-6 py-4 text-right">
              <div class="flex justify-end gap-2">
                <button class="p-2 text-slate-500 hover:text-[#2463eb] transition-colors"><span class="material-symbols-outlined text-xl">edit</span></button>
                <button class="p-2 text-slate-500 hover:text-red-500 transition-colors"><span class="material-symbols-outlined text-xl">delete</span></button>
              </div>
            </td>
          </tr>
          <tr class="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
            <td class="px-6 py-4">
              <div class="flex flex-col">
                <span class="text-sm font-bold text-slate-900 dark:text-white">Frontend Developer (React)</span>
                <span class="text-xs text-slate-500">Contract • New York</span>
              </div>
            </td>
            <td class="px-6 py-4 text-sm text-slate-600 dark:text-slate-400 font-medium">Engineering</td>
            <td class="px-6 py-4 text-center">
              <span class="px-2.5 py-1 text-xs font-bold bg-slate-100 dark:bg-slate-800 rounded-full text-slate-900 dark:text-slate-100">86</span>
            </td>
            <td class="px-6 py-4">
              <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> Đang tuyển
              </span>
            </td>
            <td class="px-6 py-4 text-right">
              <div class="flex justify-end gap-2">
                <button class="p-2 text-slate-500 hover:text-[#2463eb] transition-colors"><span class="material-symbols-outlined text-xl">edit</span></button>
                <button class="p-2 text-slate-500 hover:text-red-500 transition-colors"><span class="material-symbols-outlined text-xl">delete</span></button>
              </div>
            </td>
          </tr>
          <tr class="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
            <td class="px-6 py-4">
              <div class="flex flex-col">
                <span class="text-sm font-bold text-slate-900 dark:text-white">Growth Marketing Lead</span>
                <span class="text-xs text-slate-500">Full-time • London</span>
              </div>
            </td>
            <td class="px-6 py-4 text-sm text-slate-600 dark:text-slate-400 font-medium">Marketing</td>
            <td class="px-6 py-4 text-center">
              <span class="px-2.5 py-1 text-xs font-bold bg-slate-100 dark:bg-slate-800 rounded-full text-slate-900 dark:text-slate-100">32</span>
            </td>
            <td class="px-6 py-4">
              <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-slate-200 text-slate-600 dark:bg-slate-800 dark:text-slate-400">
                <span class="w-1.5 h-1.5 rounded-full bg-slate-400"></span> Đã đóng
              </span>
            </td>
            <td class="px-6 py-4 text-right">
              <div class="flex justify-end gap-2">
                <button class="p-2 text-slate-500 hover:text-[#2463eb] transition-colors"><span class="material-symbols-outlined text-xl">edit</span></button>
                <button class="p-2 text-slate-500 hover:text-red-500 transition-colors"><span class="material-symbols-outlined text-xl">delete</span></button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="p-4 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between">
      <p class="text-xs text-slate-500 dark:text-slate-400">Hiển thị 1-4 trong tổng số 12 tin tuyển dụng</p>
      <div class="flex gap-2">
        <button class="p-1.5 rounded border border-slate-200 dark:border-slate-800 disabled:opacity-50" disabled>
          <span class="material-symbols-outlined text-sm">chevron_left</span>
        </button>
        <button class="p-1.5 rounded border border-slate-200 dark:border-slate-800 bg-[#2463eb] text-white text-xs font-bold">1</button>
        <button class="p-1.5 rounded border border-slate-200 dark:border-slate-800 text-xs font-bold hover:bg-slate-50 dark:hover:bg-slate-800">2</button>
        <button class="p-1.5 rounded border border-slate-200 dark:border-slate-800 text-xs font-bold hover:bg-slate-50 dark:hover:bg-slate-800">3</button>
        <button class="p-1.5 rounded border border-slate-200 dark:border-slate-800">
          <span class="material-symbols-outlined text-sm">chevron_right</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
</script>
