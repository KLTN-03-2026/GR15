<template>
  <AlertMessage :message="toast.message" :type="toast.type" @close="clearToast" />

  <div v-if="error" class="mb-6 flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-4 dark:border-red-900 dark:bg-red-900/20">
    <span class="material-symbols-outlined mt-1 flex-shrink-0 text-red-600">error</span>
    <div class="flex-1 break-words whitespace-pre-wrap text-sm text-red-700 dark:text-red-400">{{ error }}</div>
    <button @click="error = null" class="mt-1 flex-shrink-0 text-red-600 hover:text-red-700">
      <span class="material-symbols-outlined">close</span>
    </button>
  </div>

  <div class="mb-8 flex flex-wrap items-center justify-between gap-4">
    <div class="flex flex-col gap-1">
      <h1 class="text-3xl font-black tracking-tight">Tổng quan phân tích</h1>
      <p class="text-slate-500 dark:text-slate-400">Dashboard tổng hợp dữ liệu thật từ người dùng, hồ sơ, công ty, việc làm và AI.</p>
    </div>
    <button @click="refreshDashboard" :disabled="loading" class="flex items-center gap-2 rounded-xl bg-[#2463eb] px-5 py-2.5 text-sm font-bold text-white shadow-md shadow-[#2463eb]/20 transition-all hover:bg-[#2463eb]/90 disabled:opacity-60">
      <span class="material-symbols-outlined text-[18px]">{{ loading ? 'progress_activity' : 'refresh' }}</span>
      {{ loading ? 'Đang tải...' : 'Làm mới dữ liệu' }}
    </button>
  </div>

  <div class="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-4">
    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="mb-2 flex items-center justify-between">
        <span class="text-sm font-medium text-slate-500">Ứng viên</span>
        <span class="material-symbols-outlined text-[#2463eb]/40">person</span>
      </div>
      <div class="text-3xl font-bold">{{ overview.candidates }}</div>
      <div class="mt-2 text-xs font-medium text-[#2463eb]">Tài khoản ứng viên trên hệ thống</div>
    </div>
    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="mb-2 flex items-center justify-between">
        <span class="text-sm font-medium text-slate-500">Nhà tuyển dụng</span>
        <span class="material-symbols-outlined text-emerald-500/40">business_center</span>
      </div>
      <div class="text-3xl font-bold">{{ overview.employers }}</div>
      <div class="mt-2 text-xs font-medium text-emerald-600">{{ overview.companies }} công ty đã được tạo</div>
    </div>
    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="mb-2 flex items-center justify-between">
        <span class="text-sm font-medium text-slate-500">Đơn ứng tuyển</span>
        <span class="material-symbols-outlined text-amber-500/40">description</span>
      </div>
      <div class="text-3xl font-bold">{{ overview.applications }}</div>
      <div class="mt-2 text-xs font-medium text-amber-600">{{ overview.pendingApplications }} đơn đang chờ duyệt</div>
    </div>
    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="mb-2 flex items-center justify-between">
        <span class="text-sm font-medium text-slate-500">Tỉ lệ ứng tuyển / tin</span>
        <span class="material-symbols-outlined text-slate-500/40">monitoring</span>
      </div>
      <div class="text-3xl font-bold">{{ overview.applicationRate }}</div>
      <div class="mt-2 text-xs font-medium text-slate-500">Dựa trên tổng đơn và tổng tin tuyển dụng</div>
    </div>
  </div>

  <div class="mb-8 grid grid-cols-1 gap-6 xl:grid-cols-3">
    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="mb-5 flex items-center justify-between">
        <h3 class="font-bold">Sức khỏe nền tảng</h3>
        <span class="material-symbols-outlined text-[#2463eb]">analytics</span>
      </div>
      <div class="space-y-4">
        <div>
          <div class="mb-2 flex items-center justify-between text-sm">
            <span>Người dùng đang hoạt động</span>
            <span class="font-semibold">{{ health.activeUsers }}/{{ health.totalUsers }}</span>
          </div>
          <div class="h-2 rounded-full bg-slate-100 dark:bg-slate-800">
            <div class="h-full rounded-full bg-[#2463eb]" :style="{ width: `${health.activeUsersPercent}%` }"></div>
          </div>
        </div>
        <div>
          <div class="mb-2 flex items-center justify-between text-sm">
            <span>Hồ sơ công khai</span>
            <span class="font-semibold">{{ health.publicProfiles }}/{{ health.totalProfiles }}</span>
          </div>
          <div class="h-2 rounded-full bg-slate-100 dark:bg-slate-800">
            <div class="h-full rounded-full bg-emerald-500" :style="{ width: `${health.publicProfilesPercent}%` }"></div>
          </div>
        </div>
        <div>
          <div class="mb-2 flex items-center justify-between text-sm">
            <span>Tin tuyển dụng hoạt động</span>
            <span class="font-semibold">{{ health.activeJobs }}/{{ health.totalJobs }}</span>
          </div>
          <div class="h-2 rounded-full bg-slate-100 dark:bg-slate-800">
            <div class="h-full rounded-full bg-amber-500" :style="{ width: `${health.activeJobsPercent}%` }"></div>
          </div>
        </div>
      </div>
    </div>

    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="mb-5 flex items-center justify-between">
        <h3 class="font-bold">Trạng thái ứng tuyển</h3>
        <span class="material-symbols-outlined text-[#2463eb]">assignment</span>
      </div>
      <div class="space-y-3">
        <div v-for="item in applicationBreakdown" :key="item.label">
          <div class="mb-2 flex items-center justify-between text-sm">
            <span>{{ item.label }}</span>
            <span class="font-semibold">{{ item.value }}</span>
          </div>
          <div class="h-2 rounded-full bg-slate-100 dark:bg-slate-800">
            <div class="h-full rounded-full" :class="item.color" :style="{ width: `${item.percent}%` }"></div>
          </div>
        </div>
      </div>
    </div>

    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="mb-5 flex items-center justify-between">
        <h3 class="font-bold">AI Matching</h3>
        <span class="material-symbols-outlined text-[#2463eb]">auto_awesome</span>
      </div>
      <div class="space-y-4">
        <div class="rounded-lg bg-slate-50 p-4 dark:bg-slate-800/60">
          <div class="text-xs uppercase tracking-wide text-slate-500">Tổng phiên bản model</div>
          <div class="mt-1 text-2xl font-bold">{{ matchingSummary.totalVersions }}</div>
        </div>
        <div class="rounded-lg bg-slate-50 p-4 dark:bg-slate-800/60">
          <div class="text-xs uppercase tracking-wide text-slate-500">Điểm trung bình tốt nhất</div>
          <div class="mt-1 text-2xl font-bold">{{ matchingSummary.bestAverageScore }}</div>
          <div class="mt-1 text-xs text-slate-500">{{ matchingSummary.bestVersion }}</div>
        </div>
        <div class="rounded-lg bg-slate-50 p-4 dark:bg-slate-800/60">
          <div class="text-xs uppercase tracking-wide text-slate-500">Ngành được AI gợi ý nhiều nhất</div>
          <div class="mt-1 text-lg font-bold">{{ careerSummary.topSuggestion }}</div>
          <div class="mt-1 text-xs text-slate-500">{{ careerSummary.topSuggestionCount }}</div>
        </div>
      </div>
    </div>
  </div>

  <div class="mb-8 grid grid-cols-1 gap-6 xl:grid-cols-2">
    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="mb-5 flex items-center justify-between">
        <h3 class="font-bold">Top kỹ năng người dùng</h3>
        <span class="material-symbols-outlined text-[#2463eb]">bolt</span>
      </div>
      <div v-if="topSkills.length" class="space-y-4">
        <div v-for="skill in topSkills" :key="skill.id || skill.ten_ky_nang">
          <div class="mb-2 flex items-center justify-between text-sm">
            <span class="font-medium">{{ skill.ten_ky_nang }}</span>
            <span class="font-semibold">{{ skill.so_nguoi }}</span>
          </div>
          <div class="h-2 rounded-full bg-slate-100 dark:bg-slate-800">
            <div class="h-full rounded-full bg-[#2463eb]" :style="{ width: `${skill.percent}%` }"></div>
          </div>
        </div>
      </div>
      <div v-else class="rounded-lg bg-slate-50 px-4 py-6 text-sm text-slate-500 dark:bg-slate-800/60">Chưa có dữ liệu kỹ năng người dùng.</div>
    </div>

    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="mb-5 flex items-center justify-between">
        <h3 class="font-bold">Quy mô công ty</h3>
        <span class="material-symbols-outlined text-[#2463eb]">domain</span>
      </div>
      <div class="space-y-4">
        <div v-for="companySize in companySizeStats" :key="companySize.label">
          <div class="mb-2 flex items-center justify-between text-sm">
            <span>{{ companySize.label }}</span>
            <span class="font-semibold">{{ companySize.value }}</span>
          </div>
          <div class="h-2 rounded-full bg-slate-100 dark:bg-slate-800">
            <div class="h-full rounded-full bg-emerald-500" :style="{ width: `${companySize.percent}%` }"></div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="grid grid-cols-1 gap-6 xl:grid-cols-2">
    <div class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="border-b border-slate-200 px-6 py-4 dark:border-slate-800">
        <h3 class="font-bold">Tin được lưu nhiều nhất</h3>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-left">
          <thead>
            <tr class="bg-slate-50 text-xs font-semibold uppercase tracking-wider text-slate-500 dark:bg-slate-800/50">
              <th class="px-6 py-4">Tin tuyển dụng</th>
              <th class="px-6 py-4">Công ty</th>
              <th class="px-6 py-4 text-right">Lượt lưu</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 dark:divide-slate-800">
            <tr v-for="job in savedJobs" :key="job.id" class="hover:bg-slate-50/50 dark:hover:bg-slate-800/50">
              <td class="px-6 py-4 text-sm font-medium">{{ job.tieu_de }}</td>
              <td class="px-6 py-4 text-sm text-slate-500">{{ job.cong_ty?.ten_cong_ty || 'N/A' }}</td>
              <td class="px-6 py-4 text-right text-sm font-semibold">{{ job.nguoi_dung_luus_count ?? 0 }}</td>
            </tr>
            <tr v-if="!savedJobs.length">
              <td colspan="3" class="px-6 py-8 text-center text-sm text-slate-500">Chưa có dữ liệu lưu tin.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="border-b border-slate-200 px-6 py-4 dark:border-slate-800">
        <h3 class="font-bold">Phiên bản AI Matching</h3>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-left">
          <thead>
            <tr class="bg-slate-50 text-xs font-semibold uppercase tracking-wider text-slate-500 dark:bg-slate-800/50">
              <th class="px-6 py-4">Model</th>
              <th class="px-6 py-4">Số lượt match</th>
              <th class="px-6 py-4 text-right">Điểm TB</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 dark:divide-slate-800">
            <tr v-for="model in matchingModels" :key="model.model_version" class="hover:bg-slate-50/50 dark:hover:bg-slate-800/50">
              <td class="px-6 py-4 text-sm font-medium">{{ model.model_version || 'Chưa rõ phiên bản' }}</td>
              <td class="px-6 py-4 text-sm text-slate-500">{{ model.total_matches ?? 0 }}</td>
              <td class="px-6 py-4 text-right text-sm font-semibold">{{ formatScore(model.average_score) }}</td>
            </tr>
            <tr v-if="!matchingModels.length">
              <td colspan="3" class="px-6 py-8 text-center text-sm text-slate-500">Chưa có dữ liệu matching AI.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import AlertMessage from '@/components/AlertMessage.vue'
import { statsService } from '@/services/api'

const loading = ref(false)
const error = ref(null)
const savedJobs = ref([])
const matchingModels = ref([])
const topSkillsRaw = ref([])
const companyScaleMap = ref({})
const toast = reactive({ message: '', type: 'success' })
let toastTimer = null

const dashboard = reactive({
  users: null,
  profiles: null,
  companies: null,
  jobs: null,
  applications: null,
  matching: [],
  userSkills: null,
  advising: [],
  savedJobs: []
})

const safeNumber = (value) => Number(value || 0)
const formatPercent = (value) => `${safeNumber(value).toFixed(1)}%`
const formatScore = (value) => {
  if (value == null || Number.isNaN(Number(value))) return '0.0'
  return Number(value).toFixed(1)
}
const percentOf = (value, total) => (safeNumber(total) > 0 ? Math.min((safeNumber(value) / safeNumber(total)) * 100, 100) : 0)

const overview = computed(() => {
  const users = dashboard.users?.data ?? dashboard.users ?? {}
  const companies = dashboard.companies?.data ?? dashboard.companies ?? {}
  const jobs = dashboard.jobs?.data ?? dashboard.jobs ?? {}
  const applications = dashboard.applications?.data ?? dashboard.applications ?? {}
  const totalJobs = safeNumber(jobs.tong_tin)
  const totalApplications = safeNumber(applications.tong_don_ung_tuyen)

  return {
    candidates: safeNumber(users.ung_vien),
    employers: safeNumber(users.nha_tuyen_dung),
    companies: safeNumber(companies.tong),
    applications: totalApplications,
    pendingApplications: safeNumber(applications.chi_tiet?.cho_duyet),
    applicationRate: totalJobs > 0 ? formatPercent((totalApplications / totalJobs) * 100) : '0.0%'
  }
})

const health = computed(() => {
  const users = dashboard.users?.data ?? dashboard.users ?? {}
  const profiles = dashboard.profiles?.data ?? dashboard.profiles ?? {}
  const jobs = dashboard.jobs?.data ?? dashboard.jobs ?? {}

  const totalUsers = safeNumber(users.tong)
  const activeUsers = safeNumber(users.dang_hoat_dong)
  const totalProfiles = safeNumber(profiles.tong)
  const publicProfiles = safeNumber(profiles.cong_khai)
  const totalJobs = safeNumber(jobs.tong_tin)
  const activeJobs = safeNumber(jobs.hoat_dong)

  return {
    totalUsers,
    activeUsers,
    totalProfiles,
    publicProfiles,
    totalJobs,
    activeJobs,
    activeUsersPercent: percentOf(activeUsers, totalUsers),
    publicProfilesPercent: percentOf(publicProfiles, totalProfiles),
    activeJobsPercent: percentOf(activeJobs, totalJobs)
  }
})

const applicationBreakdown = computed(() => {
  const detail = dashboard.applications?.data?.chi_tiet ?? dashboard.applications?.chi_tiet ?? {}
  const total = safeNumber(dashboard.applications?.data?.tong_don_ung_tuyen ?? dashboard.applications?.tong_don_ung_tuyen)
  return [
    { label: 'Chờ duyệt', value: safeNumber(detail.cho_duyet), percent: percentOf(detail.cho_duyet, total), color: 'bg-amber-500' },
    { label: 'Đã xem', value: safeNumber(detail.da_xem), percent: percentOf(detail.da_xem, total), color: 'bg-[#2463eb]' },
    { label: 'Chấp nhận', value: safeNumber(detail.chap_nhan), percent: percentOf(detail.chap_nhan, total), color: 'bg-emerald-500' },
    { label: 'Từ chối', value: safeNumber(detail.tu_choi), percent: percentOf(detail.tu_choi, total), color: 'bg-rose-500' }
  ]
})

const matchingSummary = computed(() => {
  const items = matchingModels.value
  const best = [...items].sort((a, b) => safeNumber(b.average_score) - safeNumber(a.average_score))[0]
  return {
    totalVersions: items.length,
    bestAverageScore: best ? formatScore(best.average_score) : '0.0',
    bestVersion: best ? `Hiệu quả nhất: ${best.model_version}` : 'Chưa có dữ liệu'
  }
})

const careerSummary = computed(() => {
  const first = (dashboard.advising || [])[0]
  return {
    topSuggestion: first?.nghe_de_xuat || 'Chưa có dữ liệu',
    topSuggestionCount: first ? `${safeNumber(first.total_suggestions)} lượt AI gợi ý` : 'Chưa có thống kê tư vấn'
  }
})

const topSkills = computed(() => {
  const max = Math.max(...topSkillsRaw.value.map((item) => safeNumber(item.so_nguoi)), 0)
  return topSkillsRaw.value.map((item) => ({
    id: item.ky_nang_id ?? item.kyNang?.id,
    ten_ky_nang: item.ky_nang?.ten_ky_nang ?? item.kyNang?.ten_ky_nang ?? 'Không rõ',
    so_nguoi: safeNumber(item.so_nguoi),
    percent: max > 0 ? (safeNumber(item.so_nguoi) / max) * 100 : 0
  }))
})

const companySizeStats = computed(() => {
  const entries = Object.entries(companyScaleMap.value || {})
  const max = Math.max(...entries.map(([, value]) => safeNumber(value)), 0)
  return entries.map(([label, value]) => ({
    label,
    value: safeNumber(value),
    percent: max > 0 ? (safeNumber(value) / max) * 100 : 0
  }))
})

const clearToast = () => {
  toast.message = ''
  if (toastTimer) {
    clearTimeout(toastTimer)
    toastTimer = null
  }
}

const showToast = (message, type = 'success') => {
  clearToast()
  toast.message = message
  toast.type = type
  toastTimer = window.setTimeout(() => clearToast(), 3000)
}

const loadDashboard = async ({ notify = false } = {}) => {
  loading.value = true
  error.value = null

  try {
    const [
      userStats,
      profileStats,
      companyStats,
      jobStats,
      applicationStats,
      matchingStats,
      userSkillStats,
      advisingStats,
      savedJobStats
    ] = await Promise.all([
      statsService.getUserStats(),
      statsService.getProfileStats(),
      statsService.getCompanyStats(),
      statsService.getJobPostingStats(),
      statsService.getApplicationStats(),
      statsService.getMatchingStats(),
      statsService.getUserSkillStats(),
      statsService.getCareerAdvisingStats(),
      statsService.getSavedJobStats()
    ])

    dashboard.users = userStats
    dashboard.profiles = profileStats
    dashboard.companies = companyStats
    dashboard.jobs = jobStats
    dashboard.applications = applicationStats
    dashboard.matching = matchingStats?.data ?? matchingStats ?? []
    dashboard.userSkills = userSkillStats
    dashboard.advising = advisingStats?.data ?? advisingStats ?? []
    dashboard.savedJobs = savedJobStats?.data ?? savedJobStats ?? []

    matchingModels.value = dashboard.matching
    topSkillsRaw.value = dashboard.userSkills?.data?.top_ky_nang ?? dashboard.userSkills?.top_ky_nang ?? []
    companyScaleMap.value = dashboard.companies?.data?.theo_quy_mo ?? dashboard.companies?.theo_quy_mo ?? {}
    savedJobs.value = dashboard.savedJobs

    if (notify) {
      showToast('Đã làm mới dữ liệu thống kê.')
    }
  } catch (err) {
    error.value = err.message || 'Không thể tải dashboard thống kê'
  } finally {
    loading.value = false
  }
}

const refreshDashboard = async () => {
  await loadDashboard({ notify: true })
}

onMounted(() => {
  loadDashboard()
})

onBeforeUnmount(() => {
  if (toastTimer) {
    clearTimeout(toastTimer)
  }
})
</script>
