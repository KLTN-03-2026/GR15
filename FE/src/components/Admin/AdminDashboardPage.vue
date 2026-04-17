<template>
  <div class="p-6">
    <div class="mb-8 flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">Dashboard Admin</h1>
        <p class="text-sm text-slate-500">Tổng quan thị trường và sức khỏe nền tảng</p>
      </div>
      <button @click="loadDashboard" class="flex items-center gap-2 rounded-xl bg-[#2463eb] px-4 py-2 font-semibold text-white hover:bg-blue-700">
        <span class="material-symbols-outlined text-lg">refresh</span>
        Làm mới
      </button>
    </div>

    <!-- Overview Cards -->
    <div class="grid gap-6 md:grid-cols-3">
      <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="flex items-center gap-4">
          <div class="flex size-14 items-center justify-center rounded-2xl bg-blue-50 text-[#2463eb]">
            <span class="material-symbols-outlined text-2xl">group</span>
          </div>
          <div>
            <p class="text-sm font-semibold text-slate-500">Tổng người dùng</p>
            <h3 class="text-3xl font-black text-slate-900">{{ overview.total_users || 0 }}</h3>
          </div>
        </div>
      </div>

      <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="flex items-center gap-4">
          <div class="flex size-14 items-center justify-center rounded-2xl bg-indigo-50 text-indigo-600">
            <span class="material-symbols-outlined text-2xl">domain</span>
          </div>
          <div>
            <p class="text-sm font-semibold text-slate-500">Doanh nghiệp</p>
            <h3 class="text-3xl font-black text-slate-900">{{ overview.total_companies || 0 }}</h3>
          </div>
        </div>
      </div>

      <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="flex items-center gap-4">
          <div class="flex size-14 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-600">
            <span class="material-symbols-outlined text-2xl">work</span>
          </div>
          <div>
            <p class="text-sm font-semibold text-slate-500">Việc đang mở</p>
            <h3 class="text-3xl font-black text-slate-900">{{ overview.active_jobs || 0 }}</h3>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts & Insights Layer -->
    <div class="mt-8 grid gap-6 lg:grid-cols-2">
      <!-- Top Categories -->
      <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 class="mb-4 text-lg font-bold text-slate-900">Danh mục thịnh hành</h2>
        <div class="space-y-4">
          <div v-for="(cat, idx) in topCategories" :key="idx" class="flex items-center justify-between">
            <span class="text-sm font-medium text-slate-700">{{ cat.name }}</span>
            <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-600">
              {{ cat.count }} jobs
            </span>
          </div>
        </div>
      </div>

      <!-- Trend & Insights -->
      <div class="space-y-6">
        <!-- AI Hints Insight Box -->
        <div class="rounded-2xl border border-amber-200 bg-amber-50 p-6">
          <h2 class="mb-3 flex items-center gap-2 text-lg font-bold text-amber-900">
            <span class="material-symbols-outlined">lightbulb</span>
            Market Insights
          </h2>
          <ul class="space-y-2 text-sm text-amber-800">
            <li v-for="(hint, index) in hints" :key="index" class="flex gap-2">
              <span class="text-amber-500">•</span> {{ hint }}
            </li>
          </ul>
        </div>

        <!-- Job creation trend graph representation -->
        <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 class="mb-4 text-lg font-bold text-slate-900">Xu hướng tuyển dụng (6 tháng)</h2>
          <div class="flex h-40 items-end gap-2">
            <div 
              v-for="(trend, i) in monthlyTrend" 
              :key="i"
              class="group relative flex flex-1 flex-col items-center justify-end"
            >
              <div 
                class="w-full rounded-t-lg bg-[#2463eb] transition-all group-hover:bg-blue-600"
                :style="{ height: Math.max(trend.jobs * 2, 10) + 'px', maxHeight: '100%' }"
              ></div>
              <p class="mt-2 text-xs font-semibold text-slate-500">{{ trend.month }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// Fake API calls until api.js is fully wired for this
const loadDashboardData = async () => {
  // Simulate fetch to /api/v1/admin/dashboard/market
  return new Promise(resolve => {
    setTimeout(() => {
      resolve({
        overview: { total_users: 1250, total_companies: 84, active_jobs: 312 },
        top_categories: [
          { name: 'Công nghệ thông tin', count: 120 },
          { name: 'Marketing / PR', count: 85 },
          { name: 'Kinh doanh / Bán hàng', count: 64 },
          { name: 'Thiết kế đồ họa', count: 32 }
        ],
        monthly_job_trend: [
          { month: '11/2023', jobs: 20 },
          { month: '12/2023', jobs: 35 },
          { month: '01/2024', jobs: 40 },
          { month: '02/2024', jobs: 18 },
          { month: '03/2024', jobs: 55 },
          { month: '04/2024', jobs: 70 }
        ],
        hints: [
          'IT Companies are actively hiring remote developers.',
          'Significant spike in "Marketing" roles this month.'
        ]
      })
    }, 600)
  })
}

const overview = ref({})
const topCategories = ref([])
const monthlyTrend = ref([])
const hints = ref([])

const loadDashboard = async () => {
  const data = await loadDashboardData()
  overview.value = data.overview
  topCategories.value = data.top_categories
  monthlyTrend.value = data.monthly_job_trend
  hints.value = data.hints
}

onMounted(() => {
  loadDashboard()
})
</script>
