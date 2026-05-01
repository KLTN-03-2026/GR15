<script setup>
import AppLogo from '@/components/AppLogo.vue'
</script>

<template>
  <footer class="bg-slate-900 py-12 text-slate-300">
    <div class="mx-auto max-w-7xl px-6">
      <div class="grid grid-cols-2 gap-8 md:grid-cols-4 lg:grid-cols-5">
        <div class="col-span-2 lg:col-span-2">
          <div class="mb-6">
            <AppLogo tone="light" subtitle="Career Intelligence Platform" />
          </div>
          <p class="max-w-xs text-sm leading-relaxed">
            Định hình tương lai sự nghiệp của bạn bằng sức mạnh Trí tuệ Nhân tạo. Tìm việc nhanh hơn, hiệu quả hơn và đúng định hướng hơn.
          </p>
        </div>
        <div>
          <h4 class="mb-6 text-sm font-bold uppercase tracking-wider text-white">Về chúng tôi</h4>
          <ul class="space-y-4 text-sm">
            <li><a class="hover:text-white transition-colors" href="#">Giới thiệu</a></li>
            <li><a class="hover:text-white transition-colors" href="#">Tin tuyển dụng</a></li>
            <li><a class="hover:text-white transition-colors" href="#">Liên hệ</a></li>
          </ul>
        </div>
        <div>
          <h4 class="mb-6 text-sm font-bold uppercase tracking-wider text-white">Hỗ trợ</h4>
          <ul class="space-y-4 text-sm">
            <li><a class="hover:text-white transition-colors" href="#">Điều khoản dịch vụ</a></li>
            <li><a class="hover:text-white transition-colors" href="#">Chính sách bảo mật</a></li>
            <li><a class="hover:text-white transition-colors" href="#">Câu hỏi thường gặp</a></li>
          </ul>
        </div>
        <div class="col-span-2 md:col-span-1">
          <h4 class="mb-6 text-sm font-bold uppercase tracking-wider text-white">Kết nối</h4>
          <div class="flex gap-4">
            <a class="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-800 hover:bg-[#2463eb] transition-colors" href="#">
              <span class="material-symbols-outlined text-xl">share</span>
            </a>
            <a class="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-800 hover:bg-[#2463eb] transition-colors" href="#">
              <span class="material-symbols-outlined text-xl">alternate_email</span>
            </a>
            <a class="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-800 hover:bg-[#2463eb] transition-colors" href="#">
              <span class="material-symbols-outlined text-xl">rss_feed</span>
            </a>
          </div>
        </div>
      </div>
      <div class="mt-12 border-t border-slate-800 pt-8 text-center text-xs">
        <p>&copy; 2026 AI Recruitment &amp; Career Consulting System. All rights reserved.</p>
      </div>
    </div>
  </footer>
</template>
