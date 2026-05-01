<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import {
  adminMarketService,
  adminStatsService,
} from '@/services/api'

const overview = reactive({
  totalApplications: 0,
  conversionRate: 0,
})

const applicationBreakdown = reactive({
  cho_duyet: 0,
  da_xem: 0,
  da_hen_phong_van: 0,
  qua_phong_van: 0,
  trung_tuyen: 0,
  tu_choi: 0,
})

const marketOverview = ref(null)
const topSavedJobs = ref([])
const matchingStats = ref([])
const careerStats = ref([])
const loading = ref(false)
const error = ref('')

const applicationBars = computed(() => {
  const total = overview.totalApplications || 1

  return [
    { label: 'Chờ duyệt', value: applicationBreakdown.cho_duyet, color: 'bg-amber-500', width: `${(applicationBreakdown.cho_duyet / total) * 100}%` },
    { label: 'Đã xem', value: applicationBreakdown.da_xem, color: 'bg-sky-500', width: `${(applicationBreakdown.da_xem / total) * 100}%` },
    { label: 'Đã hẹn phỏng vấn', value: applicationBreakdown.da_hen_phong_van, color: 'bg-violet-500', width: `${(applicationBreakdown.da_hen_phong_van / total) * 100}%` },
    { label: 'Qua phỏng vấn', value: applicationBreakdown.qua_phong_van, color: 'bg-indigo-500', width: `${(applicationBreakdown.qua_phong_van / total) * 100}%` },
    { label: 'Trúng tuyển', value: applicationBreakdown.trung_tuyen, color: 'bg-emerald-500', width: `${(applicationBreakdown.trung_tuyen / total) * 100}%` },
    { label: 'Từ chối', value: applicationBreakdown.tu_choi, color: 'bg-rose-500', width: `${(applicationBreakdown.tu_choi / total) * 100}%` },
  ]
})

const topMatchingModels = computed(() => matchingStats.value.slice(0, 5))
const topCareerSuggestions = computed(() => careerStats.value.slice(0, 6))
const topMarketSkills = computed(() => marketOverview.value?.top_skills?.slice(0, 6) || [])
const topCategories = computed(() => marketOverview.value?.top_categories?.slice(0, 5) || [])
const monthlyTrend = computed(() => marketOverview.value?.monthly_job_trend || [])
const totalAiMatches = computed(() => matchingStats.value.reduce((total, item) => total + Number(item.total_matches || 0), 0))
const averageAiScore = computed(() => {
  const totalMatches = totalAiMatches.value
  if (!totalMatches) return 0

  const weightedScore = matchingStats.value.reduce((total, item) => {
    return total + Number(item.average_score || 0) * Number(item.total_matches || 0)
  }, 0)

  return weightedScore / totalMatches
})
const totalCareerSuggestions = computed(() => careerStats.value.reduce((total, item) => total + Number(item.total_suggestions || 0), 0))

const formatCurrency = (value) => {
  if (value === null || value === undefined || value === '') return 'N/A'
  return new Intl.NumberFormat('vi-VN').format(Number(value)) + ' đ'
}

const formatDecimal = (value) => {
  if (value === null || value === undefined || value === '') return '0.0'
  return Number(value).toFixed(1)
}

const analysisCards = computed(() => [
  {
    label: 'Lượt ứng tuyển',
    value: overview.totalApplications,
    helper: 'Tổng số đơn ứng tuyển đã ghi nhận trong hệ thống.',
    icon: 'assignment',
    tone: 'text-amber-500',
    bar: 'bg-amber-500',
    progress: Math.min(100, overview.totalApplications / 10),
  },
  {
    label: 'Tỷ lệ trúng tuyển',
    value: `${overview.conversionRate}%`,
    helper: `${applicationBreakdown.trung_tuyen} đơn đã trúng tuyển trên tổng đơn ứng tuyển.`,
    icon: 'trending_up',
    tone: 'text-purple-500',
    bar: 'bg-purple-500',
    progress: Math.min(100, overview.conversionRate),
  },
  {
    label: 'AI Matching đã chạy',
    value: totalAiMatches.value,
    helper: `Điểm matching trung bình: ${formatDecimal(averageAiScore.value)}.`,
    icon: 'stars',
    tone: 'text-[#2463eb]',
    bar: 'bg-[#2463eb]',
    progress: Math.min(100, totalAiMatches.value / 10),
  },
  {
    label: 'Lượt AI gợi ý nghề',
    value: totalCareerSuggestions.value,
    helper: `${topCareerSuggestions.value.length} nhóm nghề nổi bật đang được ghi nhận.`,
    icon: 'auto_awesome',
    tone: 'text-emerald-500',
    bar: 'bg-emerald-500',
    progress: Math.min(100, totalCareerSuggestions.value / 10),
  },
])

const loadStats = async () => {
  loading.value = true
  error.value = ''

  try {
    const [
      applicationStatsResponse,
      marketDashboardResponse,
      savedJobResponse,
      matchingStatsResponse,
      careerStatsResponse,
    ] = await Promise.all([
      adminStatsService.getApplicationStats(),
      adminMarketService.getDashboard(),
      adminStatsService.getSavedJobTop(),
      adminStatsService.getMatchingStats(),
      adminStatsService.getCareerStats(),
    ])

    const applicationStats = applicationStatsResponse?.data || {}
    const hiredCount = applicationStats.chi_tiet?.trung_tuyen || applicationStats.chi_tiet?.chap_nhan || 0

    overview.totalApplications = applicationStats.tong_don_ung_tuyen || 0
    overview.conversionRate = overview.totalApplications > 0
      ? Math.round((hiredCount / overview.totalApplications) * 1000) / 10
      : 0

    applicationBreakdown.cho_duyet = applicationStats.chi_tiet?.cho_duyet || 0
    applicationBreakdown.da_xem = applicationStats.chi_tiet?.da_xem || 0
    applicationBreakdown.da_hen_phong_van = applicationStats.chi_tiet?.da_hen_phong_van || 0
    applicationBreakdown.qua_phong_van = applicationStats.chi_tiet?.qua_phong_van || 0
    applicationBreakdown.trung_tuyen = hiredCount
    applicationBreakdown.tu_choi = applicationStats.chi_tiet?.tu_choi || 0

    marketOverview.value = marketDashboardResponse?.data || marketDashboardResponse || {}
    topSavedJobs.value = savedJobResponse?.data || []
    matchingStats.value = matchingStatsResponse?.data || []
    careerStats.value = careerStatsResponse?.data || []
  } catch (err) {
    error.value = err.message || 'Không thể tải thống kê hệ thống'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadStats()
})
</script>

<template>
  <div v-if="error" class="mb-6 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-900 dark:bg-red-900/20 dark:text-red-300">
    {{ error }}
  </div>

  <div class="mb-8 flex flex-col gap-1">
    <p class="text-xs font-bold uppercase tracking-[0.24em] text-[#2463eb]">Báo cáo chuyên sâu</p>
    <h1 class="text-2xl font-bold">Báo cáo & phân tích hệ thống</h1>
    <p class="text-slate-500 dark:text-slate-400">
      Tập trung vào hiệu quả ứng tuyển, AI Matching, hành vi lưu tin và tín hiệu thị trường thay vì lặp lại KPI tổng quan.
    </p>
  </div>

  <div class="mb-8 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
    <div
      v-for="card in analysisCards"
      :key="card.label"
      class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800"
    >
      <div class="flex items-center justify-between">
        <span class="text-sm font-medium uppercase tracking-wider text-slate-500 dark:text-slate-400">{{ card.label }}</span>
        <span class="material-symbols-outlined" :class="card.tone">{{ card.icon }}</span>
      </div>
      <p class="mt-3 text-3xl font-bold">{{ loading ? '...' : card.value }}</p>
      <p class="mt-2 min-h-[40px] text-sm leading-5 text-slate-500 dark:text-slate-400">{{ card.helper }}</p>
      <div class="mt-4 h-1 w-full rounded-full bg-slate-100 dark:bg-slate-700">
        <div class="h-full rounded-full" :class="card.bar" :style="{ width: `${card.progress}%` }"></div>
      </div>
    </div>
  </div>

  <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800">
      <div class="mb-5 flex items-center justify-between">
        <h3 class="flex items-center gap-2 font-bold">
          <span class="material-symbols-outlined text-[#2463eb]">bar_chart</span>
          Phân rã trạng thái ứng tuyển
        </h3>
      </div>
      <div class="space-y-4">
        <div v-for="item in applicationBars" :key="item.label" class="space-y-2">
          <div class="flex items-center justify-between text-sm">
            <span class="font-medium">{{ item.label }}</span>
            <span class="text-slate-500">{{ item.value }}</span>
          </div>
          <div class="h-2 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-700">
            <div class="h-full rounded-full" :class="item.color" :style="{ width: item.width }"></div>
          </div>
        </div>
      </div>
    </div>

    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800">
      <div class="mb-5 flex items-center justify-between">
        <h3 class="flex items-center gap-2 font-bold">
          <span class="material-symbols-outlined text-[#2463eb]">timeline</span>
          Xu hướng tuyển dụng theo tháng
        </h3>
      </div>
      <div class="flex h-64 items-end justify-between gap-3 overflow-hidden rounded-lg bg-slate-50 px-4 pb-4 pt-6 dark:bg-slate-900/50">
        <div v-for="month in monthlyTrend" :key="month.month" class="flex flex-1 flex-col items-center justify-end gap-2">
          <div
            class="w-full max-w-[36px] rounded-t-md bg-[#2463eb]"
            :style="{ height: `${Math.max(12, month.count * 6)}px` }"
          ></div>
          <span class="text-[11px] text-slate-400">{{ month.month }}</span>
          <span class="text-[11px] font-bold">{{ month.count }}</span>
        </div>
      </div>
    </div>

    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800">
      <div class="mb-5 flex items-center justify-between">
        <h3 class="flex items-center gap-2 font-bold">
          <span class="material-symbols-outlined text-[#2463eb]">stars</span>
          Hiệu suất AI Matching
        </h3>
      </div>
      <div class="space-y-4">
        <div v-for="item in topMatchingModels" :key="item.model_version" class="rounded-lg border border-slate-100 p-4 dark:border-slate-700">
          <div class="flex items-center justify-between">
            <p class="font-semibold">{{ item.model_version || 'Unknown model' }}</p>
            <span class="rounded bg-[#2463eb]/10 px-2 py-1 text-xs font-bold text-[#2463eb]">{{ item.total_matches }} lượt</span>
          </div>
          <div class="mt-3 grid grid-cols-3 gap-3 text-sm text-slate-500">
            <div>
              <div class="text-xs uppercase">TB</div>
              <div class="font-semibold text-slate-900 dark:text-slate-100">{{ formatDecimal(item.average_score) }}</div>
            </div>
            <div>
              <div class="text-xs uppercase">Max</div>
              <div class="font-semibold text-slate-900 dark:text-slate-100">{{ formatDecimal(item.max_score) }}</div>
            </div>
            <div>
              <div class="text-xs uppercase">Min</div>
              <div class="font-semibold text-slate-900 dark:text-slate-100">{{ formatDecimal(item.min_score) }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800">
      <div class="mb-5 flex items-center justify-between">
        <h3 class="flex items-center gap-2 font-bold">
          <span class="material-symbols-outlined text-[#2463eb]">auto_awesome</span>
          Nghề AI gợi ý nhiều nhất
        </h3>
      </div>
      <div class="space-y-3">
        <div v-for="item in topCareerSuggestions" :key="item.nghe_de_xuat" class="flex items-center justify-between rounded-lg border border-slate-100 px-4 py-3 dark:border-slate-700">
          <div>
            <p class="font-medium">{{ item.nghe_de_xuat || 'Chưa xác định' }}</p>
            <p class="text-xs text-slate-500">Độ phù hợp TB: {{ formatDecimal(item.average_confidence) }}</p>
          </div>
          <span class="rounded bg-emerald-500/10 px-2 py-1 text-xs font-bold text-emerald-500">{{ item.total_suggestions }}</span>
        </div>
      </div>
    </div>

    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800">
      <div class="mb-5 flex items-center justify-between">
        <h3 class="flex items-center gap-2 font-bold">
          <span class="material-symbols-outlined text-[#2463eb]">bookmark</span>
          Tin tuyển dụng được lưu nhiều
        </h3>
      </div>
      <div class="space-y-3">
        <div v-for="job in topSavedJobs" :key="job.id" class="rounded-lg border border-slate-100 p-4 dark:border-slate-700">
          <p class="font-semibold">{{ job.tieu_de }}</p>
          <p class="mt-1 text-sm text-slate-500">{{ job.cong_ty?.ten_cong_ty || 'N/A' }}</p>
          <div class="mt-2 text-xs font-bold text-[#2463eb]">{{ job.nguoi_dung_luus_count }} lượt lưu</div>
        </div>
      </div>
    </div>

    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800">
      <div class="mb-5 flex items-center justify-between">
        <h3 class="flex items-center gap-2 font-bold">
          <span class="material-symbols-outlined text-[#2463eb]">workspace_premium</span>
          Điểm nhấn thị trường
        </h3>
      </div>
      <div class="space-y-4">
        <div>
          <p class="text-xs uppercase text-slate-400">Lương trung bình</p>
          <p class="mt-1 text-xl font-bold">{{ formatCurrency(marketOverview?.overview?.average_salary) }}</p>
        </div>
        <div>
          <p class="text-xs uppercase text-slate-400">Top kỹ năng</p>
          <div class="mt-2 flex flex-wrap gap-2">
            <span v-for="skill in topMarketSkills" :key="skill.name" class="rounded-full bg-[#2463eb]/10 px-3 py-1 text-xs font-bold text-[#2463eb]">
              {{ skill.name || skill.skill }} ({{ skill.count }})
            </span>
          </div>
        </div>
        <div>
          <p class="text-xs uppercase text-slate-400">Top ngành</p>
          <div class="mt-2 flex flex-wrap gap-2">
            <span v-for="category in topCategories" :key="category.name" class="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-600 dark:bg-slate-700 dark:text-slate-200">
              {{ category.name }} ({{ category.count }})
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
