<script setup>
import { computed, onMounted, ref } from 'vue'
import { adminMarketService, companyService, userService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'

const notify = useNotify()

const loading = ref(false)
const userStats = ref(null)
const companyStats = ref(null)
const marketDashboard = ref(null)

const formatCurrency = (value) => {
  const amount = Number(value || 0)
  if (!amount) return '0 đ'
  return `${new Intl.NumberFormat('vi-VN').format(amount)} đ`
}

const safePercent = (value, total) => {
  if (!total) return 0
  return Math.min(100, Math.round((Number(value || 0) / Number(total || 1)) * 100))
}

const statCards = computed(() => {
  const users = userStats.value || {}
  const companies = companyStats.value || {}
  const overview = marketDashboard.value?.overview || {}

  return [
    {
      label: 'Người dùng toàn hệ thống',
      value: users.tong || 0,
      subValue: `${users.ung_vien || 0} ứng viên • ${users.nha_tuyen_dung || 0} nhà tuyển dụng`,
      helper: `${users.dang_hoat_dong || 0} tài khoản đang hoạt động`,
      icon: 'groups',
      tone: 'bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-300',
      progress: safePercent(users.dang_hoat_dong, users.tong),
    },
    {
      label: 'Công ty trên nền tảng',
      value: companies.tong || 0,
      subValue: `${companies.hoat_dong || 0} công ty đang hoạt động`,
      helper: `${companies.tam_ngung || 0} công ty tạm ngưng`,
      icon: 'domain',
      tone: 'bg-purple-50 text-purple-600 dark:bg-purple-900/20 dark:text-purple-300',
      progress: safePercent(companies.hoat_dong, companies.tong),
    },
    {
      label: 'Tin tuyển dụng đang chạy',
      value: overview.active_job_count || 0,
      subValue: `${overview.application_count || 0} lượt ứng tuyển`,
      helper: `${overview.company_count || 0} công ty đang có tin hoạt động`,
      icon: 'work',
      tone: 'bg-amber-50 text-amber-600 dark:bg-amber-900/20 dark:text-amber-300',
      progress: 100,
    },
    {
      label: 'Lương trung bình thị trường',
      value: formatCurrency(overview.average_salary),
      subValue: `Median ${formatCurrency(overview.median_salary)}`,
      helper: `${overview.remote_job_count || 0} tin remote đang mở`,
      icon: 'payments',
      tone: 'bg-emerald-50 text-emerald-600 dark:bg-emerald-900/20 dark:text-emerald-300',
      progress: safePercent(overview.remote_job_count, overview.active_job_count),
    },
  ]
})

const topSkills = computed(() => (marketDashboard.value?.top_skills || []).slice(0, 5))
const insights = computed(() => marketDashboard.value?.insights || [])
const monthlyTrend = computed(() => {
  const rows = marketDashboard.value?.monthly_job_trend || []
  const max = Math.max(...rows.map((item) => Number(item.count || 0)), 1)

  return rows.map((item) => ({
    ...item,
    height: `${Math.max(14, Math.round((Number(item.count || 0) / max) * 100))}%`,
  }))
})

const workModes = computed(() => (marketDashboard.value?.work_modes || []).slice(0, 4))
const seniorityLevels = computed(() => (marketDashboard.value?.seniority_levels || []).slice(0, 4))
const topCategories = computed(() => (marketDashboard.value?.top_categories || []).slice(0, 4))

const fetchDashboard = async () => {
  loading.value = true
  try {
    const [usersRes, companiesRes, marketRes] = await Promise.all([
      userService.getUserStats(),
      companyService.getCompanyStats(),
      adminMarketService.getDashboard(),
    ])

    userStats.value = usersRes?.data || null
    companyStats.value = companiesRes?.data || null
    marketDashboard.value = marketRes?.data || null
  } catch (error) {
    notify.apiError(error, 'Không tải được dữ liệu dashboard quản trị.')
  } finally {
    loading.value = false
  }
}

onMounted(fetchDashboard)
</script>

<template>
  <div class="space-y-6">
    <section class="flex flex-col gap-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <h2 class="text-3xl font-extrabold tracking-tight">Dashboard quản trị</h2>
        <p class="mt-1 text-slate-500 dark:text-slate-400">
          Theo dõi sức khỏe toàn hệ thống, thị trường tuyển dụng và hành vi sử dụng theo thời gian thực.
        </p>
      </div>
      <div class="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-medium text-slate-500 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-300">
        <span class="material-symbols-outlined text-[#2463eb]">monitoring</span>
        {{ marketDashboard?.data_source === 'market_stats_daily + live_jobs' ? 'Dữ liệu tổng hợp + live jobs' : 'Dữ liệu live jobs' }}
      </div>
    </section>

    <div class="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-4">
      <article
        v-for="card in statCards"
        :key="card.label"
        class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900"
      >
        <div class="mb-4 flex items-start justify-between gap-3">
          <div class="flex size-11 items-center justify-center rounded-xl" :class="card.tone">
            <span class="material-symbols-outlined">{{ card.icon }}</span>
          </div>
          <span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-bold text-slate-500 dark:bg-slate-800 dark:text-slate-300">
            Live
          </span>
        </div>
        <p class="text-sm font-medium text-slate-500 dark:text-slate-400">{{ card.label }}</p>
        <h3 class="mt-2 text-2xl font-bold">
          {{ loading ? '...' : card.value }}
        </h3>
        <p class="mt-2 text-sm font-medium text-slate-600 dark:text-slate-300">{{ card.subValue }}</p>
        <p class="mt-1 text-xs leading-6 text-slate-500 dark:text-slate-400">{{ card.helper }}</p>
        <div class="mt-4 h-1.5 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
          <div class="h-full rounded-full bg-[#2463eb]" :style="{ width: `${card.progress}%` }"></div>
        </div>
      </article>
    </div>

    <div class="grid grid-cols-1 gap-6 xl:grid-cols-[minmax(0,1.7fr)_420px]">
      <section class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div class="mb-6 flex items-center justify-between">
          <div>
            <h4 class="font-bold text-lg">Xu hướng tin tuyển dụng 6 tháng</h4>
            <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Số lượng tin được tạo mới theo từng tháng.</p>
          </div>
          <span class="rounded-full bg-[#2463eb]/10 px-3 py-1 text-xs font-bold text-[#2463eb]">Live trend</span>
        </div>
        <div class="flex h-[320px] items-end justify-between gap-3">
          <div
            v-for="item in monthlyTrend"
            :key="item.label"
            class="flex h-full flex-1 flex-col items-center gap-3"
          >
            <div class="flex w-full flex-1 items-end justify-center rounded-t-xl bg-[#2463eb]/10 px-1 transition-all hover:bg-[#2463eb]/15">
              <div class="w-full rounded-t-xl bg-[#2463eb]" :style="{ height: item.height }"></div>
            </div>
            <div class="text-center">
              <p class="text-sm font-bold text-slate-900 dark:text-slate-100">{{ item.count }}</p>
              <p class="mt-1 text-xs font-medium text-slate-500 dark:text-slate-400">{{ item.label }}</p>
            </div>
          </div>
        </div>
      </section>

      <section class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div class="mb-6 flex items-center justify-between">
          <h4 class="font-bold text-lg">Kỹ năng nổi bật</h4>
          <span class="text-xs font-semibold uppercase tracking-wider text-slate-400">Top 5</span>
        </div>
        <div class="space-y-5">
          <div
            v-for="skill in topSkills"
            :key="skill.name"
            class="space-y-2"
          >
            <div class="flex items-center justify-between gap-3 text-sm">
              <span class="font-semibold">{{ skill.name }}</span>
              <span class="text-slate-500 dark:text-slate-400">{{ skill.job_count }} tin</span>
            </div>
            <div class="h-2 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
              <div
                class="h-full rounded-full bg-[#2463eb]"
                :style="{ width: `${Math.min(100, Math.max(12, skill.job_count * 10))}%` }"
              ></div>
            </div>
          </div>
          <p v-if="!topSkills.length && !loading" class="text-sm text-slate-500 dark:text-slate-400">
            Chưa có dữ liệu kỹ năng để hiển thị.
          </p>
        </div>
      </section>
    </div>

    <div class="grid grid-cols-1 gap-6 xl:grid-cols-3">
      <section class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div class="mb-5 flex items-center justify-between">
          <h4 class="font-bold text-lg">Ngành nổi bật</h4>
          <span class="text-xs font-semibold uppercase tracking-wider text-slate-400">Top ngành</span>
        </div>
        <div class="space-y-4">
          <div
            v-for="category in topCategories"
            :key="category.name"
            class="rounded-xl border border-slate-100 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-950/70"
          >
            <div class="flex items-start justify-between gap-3">
              <div>
                <p class="font-semibold text-slate-900 dark:text-slate-100">{{ category.name }}</p>
                <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">{{ category.job_count }} tin đang hoạt động</p>
              </div>
              <span class="rounded-full bg-[#2463eb]/10 px-2.5 py-1 text-xs font-bold text-[#2463eb]">
                {{ formatCurrency(category.average_salary) }}
              </span>
            </div>
          </div>
          <p v-if="!topCategories.length && !loading" class="text-sm text-slate-500 dark:text-slate-400">Chưa có dữ liệu ngành nổi bật.</p>
        </div>
      </section>

      <section class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div class="mb-5 flex items-center justify-between">
          <h4 class="font-bold text-lg">Phân bố hình thức làm việc</h4>
          <span class="text-xs font-semibold uppercase tracking-wider text-slate-400">Work mode</span>
        </div>
        <div class="space-y-4">
          <div
            v-for="mode in workModes"
            :key="mode.label"
            class="space-y-2"
          >
            <div class="flex items-center justify-between text-sm">
              <span class="font-medium">{{ mode.label }}</span>
              <span class="text-slate-500 dark:text-slate-400">{{ mode.count }}</span>
            </div>
            <div class="h-2 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
              <div class="h-full rounded-full bg-purple-500" :style="{ width: `${Math.min(100, Math.max(12, mode.count * 8))}%` }"></div>
            </div>
          </div>
          <p v-if="!workModes.length && !loading" class="text-sm text-slate-500 dark:text-slate-400">Chưa có dữ liệu hình thức làm việc.</p>
        </div>
      </section>

      <section class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div class="mb-5 flex items-center justify-between">
          <h4 class="font-bold text-lg">Điểm nhấn quản trị</h4>
          <span class="text-xs font-semibold uppercase tracking-wider text-slate-400">Insight</span>
        </div>
        <div class="space-y-4">
          <div
            v-for="insight in insights"
            :key="insight"
            class="rounded-xl border border-slate-100 bg-slate-50 p-4 text-sm leading-7 text-slate-600 dark:border-slate-800 dark:bg-slate-950/70 dark:text-slate-300"
          >
            {{ insight }}
          </div>
          <div v-if="seniorityLevels.length" class="rounded-xl border border-dashed border-slate-200 p-4 dark:border-slate-700">
            <p class="text-xs font-bold uppercase tracking-[0.24em] text-slate-400">Cấp bậc phổ biến</p>
            <div class="mt-3 flex flex-wrap gap-2">
              <span
                v-for="level in seniorityLevels"
                :key="level.label"
                class="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600 dark:bg-slate-800 dark:text-slate-300"
              >
                {{ level.label }} · {{ level.count }}
              </span>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>
