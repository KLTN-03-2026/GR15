<template>
  <!-- Hero Section -->
  <section class="relative overflow-hidden py-16 lg:py-24">
    <div class="mx-auto max-w-7xl px-6">
      <div class="relative z-10 flex flex-col items-center text-center">
        <span class="mb-4 inline-flex items-center gap-2 rounded-full bg-[#2463eb]/10 px-4 py-1.5 text-sm font-semibold text-[#2463eb]">
          <span class="material-symbols-outlined text-sm">auto_awesome</span>
          Ứng dụng Trí tuệ Nhân tạo thế hệ mới
        </span>
        <h1 class="max-w-4xl text-4xl font-black tracking-tight text-slate-900 dark:text-white sm:text-6xl">
          Tìm công việc phù hợp với <span class="text-[#2463eb]">AI Matching</span>
        </h1>
        <p class="mt-6 max-w-2xl text-lg text-slate-600 dark:text-slate-400">
          Hệ thống phân tích CV và mô tả công việc để đưa ra mức độ phù hợp, gợi ý lộ trình phát triển và kết nối bạn với nhà tuyển dụng hàng đầu.
        </p>
        <!-- Search Bar -->
        <div class="mt-10 w-full max-w-3xl overflow-hidden rounded-2xl bg-white dark:bg-slate-900 p-2 shadow-2xl ring-1 ring-slate-200 dark:ring-slate-800">
          <div class="flex flex-col md:flex-row items-center gap-2">
            <div class="flex flex-1 items-center px-4 w-full">
              <span class="material-symbols-outlined text-slate-400">search</span>
              <input class="w-full border-none bg-transparent py-4 text-slate-900 dark:text-white placeholder:text-slate-400 focus:ring-0" placeholder="Kỹ năng, Ngành nghề hoặc Địa điểm..." type="text" />
            </div>
            <div class="h-8 w-px bg-slate-200 dark:bg-slate-700 hidden md:block"></div>
            <button class="w-full md:w-auto flex h-12 items-center justify-center gap-2 rounded-xl bg-[#2463eb] px-8 font-bold text-white transition-all hover:bg-blue-700">
              Tìm kiếm
            </button>
          </div>
        </div>
        <div class="mt-8 flex flex-wrap justify-center gap-4">
          <button class="flex h-12 items-center justify-center gap-2 rounded-xl border-2 border-[#2463eb] bg-[#2463eb] px-8 font-bold text-white transition-all hover:bg-blue-700">
            <span class="material-symbols-outlined">upload_file</span>
            Tải CV của bạn
          </button>
          <RouterLink to="/jobs" class="flex h-12 items-center justify-center gap-2 rounded-xl border-2 border-slate-200 dark:border-slate-700 bg-transparent px-8 font-bold text-slate-900 dark:text-white transition-all hover:bg-slate-100 dark:hover:bg-slate-800">
            Tìm việc ngay
          </RouterLink>
        </div>
      </div>
    </div>
    <!-- Background Decorative Elements -->
    <div class="absolute -top-24 -left-24 h-96 w-96 rounded-full bg-[#2463eb]/5 blur-[100px]"></div>
    <div class="absolute top-1/2 -right-24 h-64 w-64 rounded-full bg-[#2463eb]/10 blur-[80px]"></div>
  </section>

  <!-- AI Features Section -->
  <section class="bg-white dark:bg-slate-900/50 py-20">
    <div class="mx-auto max-w-7xl px-6 text-center">
      <h2 class="text-3xl font-bold tracking-tight text-slate-900 dark:text-white sm:text-4xl">Tại sao chọn AI Recruitment?</h2>
      <p class="mt-4 text-slate-600 dark:text-slate-400">Công nghệ AI tiên tiến giúp tối ưu hóa quy trình tìm việc của bạn</p>
      <div class="mt-16 grid grid-cols-1 gap-8 md:grid-cols-3">
        <div class="flex flex-col items-center rounded-2xl border border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900 p-8 shadow-sm transition-all hover:shadow-md">
          <div class="mb-6 flex h-14 w-14 items-center justify-center rounded-xl bg-blue-100 text-[#2463eb]">
            <span class="material-symbols-outlined text-3xl">analytics</span>
          </div>
          <h3 class="text-xl font-bold text-slate-900 dark:text-white">Điểm phù hợp AI</h3>
          <p class="mt-3 text-slate-600 dark:text-slate-400 text-center">Đánh giá độ tương thích giữa CV và Job Description theo thời gian thực với độ chính xác cao.</p>
        </div>
        <div class="flex flex-col items-center rounded-2xl border border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900 p-8 shadow-sm transition-all hover:shadow-md">
          <div class="mb-6 flex h-14 w-14 items-center justify-center rounded-xl bg-purple-100 text-purple-600">
            <span class="material-symbols-outlined text-3xl">psychology</span>
          </div>
          <h3 class="text-xl font-bold text-slate-900 dark:text-white">Phân tích khoảng trống kỹ năng</h3>
          <p class="mt-3 text-slate-600 dark:text-slate-400 text-center">Phân tích những kỹ năng còn thiếu và gợi ý các khóa học để bạn sẵn sàng cho công việc mơ ước.</p>
        </div>
        <div class="flex flex-col items-center rounded-2xl border border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900 p-8 shadow-sm transition-all hover:shadow-md">
          <div class="mb-6 flex h-14 w-14 items-center justify-center rounded-xl bg-emerald-100 text-emerald-600">
            <span class="material-symbols-outlined text-3xl">explore</span>
          </div>
          <h3 class="text-xl font-bold text-slate-900 dark:text-white">Định hướng nghề nghiệp</h3>
          <p class="mt-3 text-slate-600 dark:text-slate-400 text-center">Định hướng nghề nghiệp dựa trên năng lực và xu hướng thị trường lao động toàn cầu.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- Featured Jobs Section -->
  <section class="py-20">
    <div class="mx-auto max-w-7xl px-6">
      <div class="flex items-center justify-between mb-12">
        <div>
          <h2 class="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">Việc làm nổi bật</h2>
          <p class="mt-2 text-slate-600 dark:text-slate-400">Những cơ hội nghề nghiệp tốt nhất được AI đề xuất cho bạn</p>
        </div>
        <RouterLink to="/jobs" class="hidden sm:flex items-center gap-2 text-[#2463eb] font-bold hover:underline">
          Xem tất cả <span class="material-symbols-outlined">arrow_forward</span>
        </RouterLink>
      </div>
      <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <!-- Job Card 1 -->
        <div class="group relative flex flex-col rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 transition-all hover:border-[#2463eb]/50 hover:shadow-lg">
          <div class="flex items-start justify-between">
            <div class="h-14 w-14 rounded-xl bg-slate-100 p-2 overflow-hidden"></div>
            <span class="rounded-full bg-emerald-100 px-3 py-1 text-xs font-bold text-emerald-700">95% AI Match</span>
          </div>
          <div class="mt-6">
            <h3 class="text-lg font-bold text-slate-900 dark:text-white group-hover:text-[#2463eb] transition-colors">Senior Frontend Developer</h3>
            <p class="text-sm font-medium text-slate-500">Google Inc. • Hà Nội</p>
          </div>
          <div class="mt-4 flex flex-wrap gap-2">
            <span class="rounded-md bg-slate-100 dark:bg-slate-800 px-2 py-1 text-xs font-medium text-slate-600 dark:text-slate-400">ReactJS</span>
            <span class="rounded-md bg-slate-100 dark:bg-slate-800 px-2 py-1 text-xs font-medium text-slate-600 dark:text-slate-400">TypeScript</span>
            <span class="rounded-md bg-slate-100 dark:bg-slate-800 px-2 py-1 text-xs font-medium text-slate-600 dark:text-slate-400">UI/UX</span>
          </div>
          <div class="mt-6 flex items-center justify-between border-t border-slate-100 dark:border-slate-800 pt-4">
            <span class="text-lg font-bold text-[#2463eb]">$2,500 - $4,000</span>
            <RouterLink to="/jobs/1" class="rounded-lg bg-slate-900 dark:bg-white px-4 py-2 text-sm font-bold text-white dark:text-slate-900 transition-all hover:bg-[#2463eb] dark:hover:bg-[#2463eb] dark:hover:text-white">Ứng tuyển</RouterLink>
          </div>
        </div>
        <!-- Job Card 2 -->
        <div class="group relative flex flex-col rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 transition-all hover:border-[#2463eb]/50 hover:shadow-lg">
          <div class="flex items-start justify-between">
            <div class="h-14 w-14 rounded-xl bg-slate-100 p-2 overflow-hidden"></div>
            <span class="rounded-full bg-blue-100 px-3 py-1 text-xs font-bold text-[#2463eb]">88% AI Match</span>
          </div>
          <div class="mt-6">
            <h3 class="text-lg font-bold text-slate-900 dark:text-white group-hover:text-[#2463eb] transition-colors">Product Manager</h3>
            <p class="text-sm font-medium text-slate-500">Microsoft • TP. HCM</p>
          </div>
          <div class="mt-4 flex flex-wrap gap-2">
            <span class="rounded-md bg-slate-100 dark:bg-slate-800 px-2 py-1 text-xs font-medium text-slate-600 dark:text-slate-400">Agile</span>
            <span class="rounded-md bg-slate-100 dark:bg-slate-800 px-2 py-1 text-xs font-medium text-slate-600 dark:text-slate-400">Data Analytics</span>
          </div>
          <div class="mt-6 flex items-center justify-between border-t border-slate-100 dark:border-slate-800 pt-4">
            <span class="text-lg font-bold text-[#2463eb]">Thoả thuận</span>
            <RouterLink to="/jobs/2" class="rounded-lg bg-slate-900 dark:bg-white px-4 py-2 text-sm font-bold text-white dark:text-slate-900 transition-all hover:bg-[#2463eb] dark:hover:bg-[#2463eb] dark:hover:text-white">Ứng tuyển</RouterLink>
          </div>
        </div>
        <!-- Job Card 3 -->
        <div class="group relative flex flex-col rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 transition-all hover:border-[#2463eb]/50 hover:shadow-lg">
          <div class="flex items-start justify-between">
            <div class="h-14 w-14 rounded-xl bg-slate-100 p-2 overflow-hidden"></div>
            <span class="rounded-full bg-orange-100 px-3 py-1 text-xs font-bold text-orange-700">New Post</span>
          </div>
          <div class="mt-6">
            <h3 class="text-lg font-bold text-slate-900 dark:text-white group-hover:text-[#2463eb] transition-colors">AI Engineer</h3>
            <p class="text-sm font-medium text-slate-500">VinAI • Hà Nội</p>
          </div>
          <div class="mt-4 flex flex-wrap gap-2">
            <span class="rounded-md bg-slate-100 dark:bg-slate-800 px-2 py-1 text-xs font-medium text-slate-600 dark:text-slate-400">Python</span>
            <span class="rounded-md bg-slate-100 dark:bg-slate-800 px-2 py-1 text-xs font-medium text-slate-600 dark:text-slate-400">PyTorch</span>
            <span class="rounded-md bg-slate-100 dark:bg-slate-800 px-2 py-1 text-xs font-medium text-slate-600 dark:text-slate-400">NLP</span>
          </div>
          <div class="mt-6 flex items-center justify-between border-t border-slate-100 dark:border-slate-800 pt-4">
            <span class="text-lg font-bold text-[#2463eb]">$3,000 - $5,500</span>
            <RouterLink to="/jobs/3" class="rounded-lg bg-slate-900 dark:bg-white px-4 py-2 text-sm font-bold text-white dark:text-slate-900 transition-all hover:bg-[#2463eb] dark:hover:bg-[#2463eb] dark:hover:text-white">Ứng tuyển</RouterLink>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>
