<script setup>
const shortcuts = [
  {
    title: 'Hồ sơ ứng viên',
    description: 'Tạo và cập nhật CV dùng cho matching và career report.',
    to: '/my-cv',
  },
  {
    title: 'Kỹ năng cá nhân',
    description: 'Khai báo kỹ năng, mức độ và chứng chỉ của bạn.',
    to: '/my-skills',
  },
  {
    title: 'Việc làm phù hợp',
    description: 'Sinh và xem danh sách công việc được AI đề xuất.',
    to: '/matched-jobs',
  },
  {
    title: 'Career Report',
    description: 'Xem báo cáo định hướng nghề nghiệp từ hồ sơ hiện có.',
    to: '/career-report',
  },
]
</script>

<template>
  <section class="space-y-6">
    <div class="rounded-3xl bg-gradient-to-r from-blue-600 to-indigo-600 px-8 py-10 text-white shadow-lg">
      <p class="text-xs uppercase tracking-[0.35em] text-blue-100">SmartJob AI</p>
      <h2 class="mt-3 text-4xl font-bold">Không gian ứng viên</h2>
      <p class="mt-3 max-w-3xl text-base text-blue-50">
        Từ đây bạn có thể đăng nhập, quản lý hồ sơ và kỹ năng, tạo kết quả việc làm phù hợp, rồi sinh báo cáo định hướng nghề nghiệp ngay trong hệ thống hiện tại.
      </p>
    </div>

    <div class="grid gap-5 md:grid-cols-2">
      <RouterLink
        v-for="item in shortcuts"
        :key="item.to"
        :to="item.to"
        class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
      >
        <h3 class="text-xl font-semibold text-slate-900">{{ item.title }}</h3>
        <p class="mt-3 text-sm leading-6 text-slate-600">{{ item.description }}</p>
      </RouterLink>
    </div>
  </section>
</template>
