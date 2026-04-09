<template>
  <div class="max-w-7xl mx-auto px-4 py-8">
    <div class="mb-12 flex flex-col items-center text-center">
      <div class="inline-flex items-center gap-2 rounded-full bg-[#2463eb]/10 px-4 py-1.5 text-xs font-bold uppercase tracking-wider text-[#2463eb] mb-4">
        <span class="material-symbols-outlined text-sm">auto_awesome</span>
        Phân tích nghề nghiệp thế hệ mới
      </div>
      <h1 class="max-w-3xl text-4xl font-black tracking-tight text-slate-900 dark:text-white sm:text-6xl">
        Mở khóa hành trình <span class="text-[#2463eb]">phát triển nghề nghiệp</span>
      </h1>
      <p class="mt-4 max-w-2xl text-lg text-slate-500 dark:text-slate-400">
        Công cụ AI phân tích bộ kỹ năng riêng của bạn để gợi ý những hướng đi nghề nghiệp phù hợp và có tiềm năng cao.
      </p>
    </div>
    <div class="grid grid-cols-1 gap-8 lg:grid-cols-12">
      <div class="lg:col-span-5 space-y-6">
        <section class="glass-panel rounded-2xl p-6 shadow-sm border border-[#2463eb]/10">
          <h2 class="flex items-center gap-2 text-xl font-bold text-slate-900 dark:text-white mb-6">
            <span class="material-symbols-outlined text-[#2463eb]">data_object</span> Phân tích hồ sơ
          </h2>
          <div class="space-y-6">
            <div class="relative rounded-xl border-2 border-dashed border-[#2463eb]/30 bg-[#2463eb]/5 p-8 text-center hover:border-[#2463eb] transition-colors cursor-pointer group">
              <input class="absolute inset-0 w-full h-full opacity-0 cursor-pointer" type="file" />
              <span class="material-symbols-outlined text-4xl text-[#2463eb] mb-2 group-hover:scale-110 transition-transform">upload_file</span>
              <p class="text-sm font-semibold text-slate-700 dark:text-slate-300">Tải CV của bạn lên</p>
              <p class="text-xs text-slate-500 mt-1">PDF, DOCX tối đa 10MB</p>
            </div>
            <div class="space-y-2">
              <label class="text-sm font-bold text-slate-700 dark:text-slate-300">Kỹ năng và chuyên môn cụ thể</label>
              <textarea class="w-full rounded-xl border border-slate-200 bg-white/50 pl-4 pt-2.5 text-sm focus:border-[#2463eb] focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800/50" placeholder="Ví dụ: Python, Thiết kế UX..." rows="4"></textarea>
            </div>
            <button class="ai-gradient flex w-full items-center justify-center gap-2 rounded-xl py-4 text-lg font-bold text-white shadow-lg shadow-[#2463eb]/30 transition-all hover:scale-[1.02] active:scale-[0.98]">
              <span class="material-symbols-outlined">rocket_launch</span> Phân tích lộ trình nghề nghiệp
            </button>
          </div>
        </section>
        <div class="rounded-2xl bg-slate-900 p-6 text-white overflow-hidden relative">
          <div class="absolute top-0 right-0 p-4 opacity-20">
            <span class="material-symbols-outlined text-8xl">trending_up</span>
          </div>
          <h3 class="text-lg font-bold mb-4 relative z-10">Market Pulse</h3>
          <div class="grid grid-cols-2 gap-4 relative z-10">
            <div>
              <p class="text-slate-400 text-xs uppercase tracking-widest font-bold">Growth Roles</p>
              <p class="text-2xl font-black text-[#2463eb]">+42%</p>
            </div>
            <div>
              <p class="text-slate-400 text-xs uppercase tracking-widest font-bold">Khoảng trống kỹ năng</p>
              <p class="text-2xl font-black text-emerald-400">18%</p>
            </div>
          </div>
        </div>
      </div>
      <div class="lg:col-span-7 space-y-6">
        <section class="glass-panel rounded-2xl p-6 shadow-sm border border-[#2463eb]/10">
          <div class="flex items-center justify-between mb-6">
            <h2 class="flex items-center gap-2 text-xl font-bold text-slate-900 dark:text-white">
              <span class="material-symbols-outlined text-[#2463eb]">target</span> Gợi ý phù hợp từ AI
            </h2>
            <span class="text-xs font-medium text-slate-500 bg-slate-100 dark:bg-slate-800 px-3 py-1 rounded-full">Vừa cập nhật</span>
          </div>
          <div class="grid gap-4">
            <div class="group rounded-xl border border-slate-100 bg-white p-5 hover:border-[#2463eb]/40 hover:shadow-md dark:border-slate-800 dark:bg-slate-900/40 transition-all">
              <div class="flex items-start justify-between">
                <div class="flex gap-4">
                  <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-[#2463eb]/10 text-[#2463eb]">
                    <span class="material-symbols-outlined">terminal</span>
                  </div>
                  <div>
                    <h3 class="text-lg font-bold text-slate-900 dark:text-white">Senior Software Architect</h3>
                    <p class="text-sm text-slate-500 mt-1">Phù hợp 94% với chuyên môn backend của bạn.</p>
                  </div>
                </div>
                <span class="inline-flex items-center rounded-md bg-emerald-100 px-2 py-1 text-xs font-bold text-emerald-700">Khớp 94%</span>
              </div>
            </div>
            <div class="group rounded-xl border border-slate-100 bg-white p-5 hover:border-[#2463eb]/40 hover:shadow-md dark:border-slate-800 dark:bg-slate-900/40 transition-all">
              <div class="flex items-start justify-between">
                <div class="flex gap-4">
                  <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-[#2463eb]/10 text-[#2463eb]">
                    <span class="material-symbols-outlined">insights</span>
                  </div>
                  <div>
                    <h3 class="text-lg font-bold text-slate-900 dark:text-white">AI Strategy Consultant</h3>
                    <p class="text-sm text-slate-500 mt-1">Phù hợp với nhóm kỹ năng lãnh đạo của bạn.</p>
                  </div>
                </div>
                <span class="inline-flex items-center rounded-md bg-blue-100 px-2 py-1 text-xs font-bold text-blue-700">Khớp 88%</span>
              </div>
            </div>
          </div>
        </section>
        <section class="glass-panel rounded-2xl p-6 shadow-sm border border-[#2463eb]/10">
          <h2 class="flex items-center gap-2 text-xl font-bold text-slate-900 dark:text-white mb-6">
            <span class="material-symbols-outlined text-[#2463eb]">school</span> Lộ trình tối ưu kỹ năng
          </h2>
          <div class="space-y-4">
            <div class="rounded-xl bg-[#2463eb]/5 p-4 border border-[#2463eb]/10">
              <div class="flex items-center justify-between mb-2">
                <p class="text-sm font-bold text-slate-700 dark:text-slate-200">System Design (Advanced)</p>
                <span class="text-xs font-bold text-[#2463eb]">Tác động cao</span>
              </div>
              <div class="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                <div class="bg-[#2463eb] h-full w-[65%] rounded-full"></div>
              </div>
            </div>
            <div class="rounded-xl bg-[#2463eb]/5 p-4 border border-[#2463eb]/10">
              <div class="flex items-center justify-between mb-2">
                <p class="text-sm font-bold text-slate-700 dark:text-slate-200">Cloud Security Architecture</p>
                <span class="text-xs font-bold text-amber-500">Tác động vừa</span>
              </div>
              <div class="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                <div class="bg-[#2463eb] h-full w-[30%] rounded-full"></div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
</script>
