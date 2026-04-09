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
    <div>
      <h1 class="text-3xl font-black tracking-tight">Tổng quan hệ thống</h1>
      <p class="mt-1 text-slate-500 dark:text-slate-400">Màn hình điều hành nhanh cho admin: sức khỏe nền tảng, việc cần xử lý và lối tắt quản trị.</p>
    </div>
    <div class="flex items-center gap-3">
      <RouterLink :to="{ name: 'StatsManagement' }" class="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition-colors hover:bg-slate-50 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800">
        <span class="material-symbols-outlined text-[18px]">insights</span>
        Xem thống kê
      </RouterLink>
      <button @click="refreshDashboard" :disabled="loading" class="flex items-center gap-2 rounded-xl bg-[#2463eb] px-5 py-2.5 text-sm font-bold text-white shadow-md shadow-[#2463eb]/20 transition-all hover:bg-[#2463eb]/90 disabled:opacity-60">
        <span class="material-symbols-outlined text-[18px]">{{ loading ? 'progress_activity' : 'refresh' }}</span>
        {{ loading ? 'Đang tải...' : 'Làm mới' }}
      </button>
    </div>
  </div>

  <div class="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-4">
    <div v-for="card in kpiCards" :key="card.label" class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="mb-4 flex items-center justify-between">
        <div :class="['flex h-10 w-10 items-center justify-center rounded-lg', card.iconBg]">
          <span :class="['material-symbols-outlined', card.iconText]">{{ card.icon }}</span>
        </div>
        <span :class="['rounded-full px-2 py-0.5 text-xs font-bold', card.pillClass]">{{ card.pill }}</span>
      </div>
      <p class="text-sm font-medium text-slate-500 dark:text-slate-400">{{ card.label }}</p>
      <h3 class="mt-1 text-2xl font-bold">{{ card.value }}</h3>
      <p class="mt-2 text-xs font-medium" :class="card.subClass">{{ card.sub }}</p>
    </div>
  </div>

  <div class="mb-8 grid grid-cols-1 gap-6 xl:grid-cols-3">
    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="mb-5 flex items-center justify-between">
        <h3 class="font-bold">Việc cần chú ý</h3>
        <span class="material-symbols-outlined text-[#2463eb]">notification_important</span>
      </div>
      <div class="space-y-4">
        <div v-for="item in alertCards" :key="item.label" class="rounded-lg border border-slate-200 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-800/60">
          <div class="flex items-center justify-between gap-3">
            <div>
              <div class="text-sm font-semibold">{{ item.label }}</div>
              <div class="mt-1 text-xs text-slate-500">{{ item.description }}</div>
            </div>
            <div class="text-xl font-bold" :class="item.valueClass">{{ item.value }}</div>
          </div>
        </div>
      </div>
    </div>

    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="mb-5 flex items-center justify-between">
        <h3 class="font-bold">Top kỹ năng</h3>
        <span class="material-symbols-outlined text-[#2463eb]">bolt</span>
      </div>
      <div v-if="topSkills.length" class="space-y-4">
        <div v-for="skill in topSkills" :key="skill.label">
          <div class="mb-2 flex items-center justify-between text-sm">
            <span class="font-medium">{{ skill.label }}</span>
            <span class="font-semibold">{{ skill.value }}</span>
          </div>
          <div class="h-2 rounded-full bg-slate-100 dark:bg-slate-800">
            <div class="h-full rounded-full bg-[#2463eb]" :style="{ width: `${skill.percent}%` }"></div>
          </div>
        </div>
      </div>
      <div v-else class="rounded-lg bg-slate-50 px-4 py-6 text-sm text-slate-500 dark:bg-slate-800/60">Chưa có dữ liệu kỹ năng.</div>
    </div>

    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="mb-5 flex items-center justify-between">
        <h3 class="font-bold">Tóm tắt AI</h3>
        <span class="material-symbols-outlined text-[#2463eb]">auto_awesome</span>
      </div>
      <div class="space-y-4">
        <div class="rounded-lg bg-slate-50 p-4 dark:bg-slate-800/60">
          <div class="text-xs uppercase tracking-wide text-slate-500">Phiên bản matching</div>
          <div class="mt-1 text-2xl font-bold">{{ aiSummary.totalVersions }}</div>
          <div class="mt-1 text-xs text-slate-500">{{ aiSummary.bestVersion }}</div>
        </div>
        <div class="rounded-lg bg-slate-50 p-4 dark:bg-slate-800/60">
          <div class="text-xs uppercase tracking-wide text-slate-500">Điểm matching tốt nhất</div>
          <div class="mt-1 text-2xl font-bold">{{ aiSummary.bestAverage }}</div>
          <div class="mt-1 text-xs text-slate-500">Điểm trung bình cao nhất giữa các model</div>
        </div>
        <div class="rounded-lg bg-slate-50 p-4 dark:bg-slate-800/60">
          <div class="text-xs uppercase tracking-wide text-slate-500">Gợi ý nghề nổi bật</div>
          <div class="mt-1 text-lg font-bold">{{ aiSummary.topSuggestion }}</div>
          <div class="mt-1 text-xs text-slate-500">{{ aiSummary.topSuggestionCount }}</div>
        </div>
      </div>
    </div>
  </div>

  <div class="mb-8 grid grid-cols-1 gap-6 xl:grid-cols-2">
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

    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="mb-5 flex items-center justify-between">
        <h3 class="font-bold">Đi nhanh tới quản trị</h3>
        <span class="material-symbols-outlined text-[#2463eb]">apps</span>
      </div>
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <RouterLink v-for="shortcut in shortcuts" :key="shortcut.name" :to="{ name: shortcut.name }" class="group rounded-xl border border-slate-200 bg-slate-50 p-4 transition-all hover:border-[#2463eb]/30 hover:bg-[#2463eb]/5 dark:border-slate-700 dark:bg-slate-800/60 dark:hover:border-[#2463eb]/30 dark:hover:bg-[#2463eb]/10">
          <div class="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-[#2463eb]/10 text-[#2463eb]">
            <span class="material-symbols-outlined">{{ shortcut.icon }}</span>
          </div>
          <div class="text-sm font-semibold">{{ shortcut.label }}</div>
          <div class="mt-1 text-xs text-slate-500">{{ shortcut.description }}</div>
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { RouterLink } from 'vue-router'
import AlertMessage from '@/components/AlertMessage.vue'
import { statsService } from '@/services/api'

const loading = ref(false)
const error = ref(null)
const savedJobs = ref([])
const matchingModels = ref([])
const topSkillsRaw = ref([])
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

const shortcuts = [
  { name: 'UserManagement', icon: 'groups', label: 'Người dùng', description: 'Quản lý ứng viên, nhà tuyển dụng và admin.' },
  { name: 'CompanyManagement', icon: 'apartment', label: 'Công ty', description: 'Theo dõi trạng thái và hồ sơ doanh nghiệp.' },
  { name: 'IndustryManagement', icon: 'category', label: 'Ngành nghề', description: 'Quản lý cây danh mục ngành nghề.' },
  { name: 'SkillManagement', icon: 'bolt', label: 'Kỹ năng', description: 'Chuẩn hóa kho kỹ năng của hệ thống.' },
  { name: 'JobPostingsManagement', icon: 'work', label: 'Tin tuyển dụng', description: 'Kiểm tra và điều phối tin đăng tuyển.' },
  { name: 'StatsManagement', icon: 'insights', label: 'Thống kê', description: 'Xem dashboard dữ liệu chi tiết hơn.' }
]

const safeNumber = (value) => Number(value || 0)
const formatPercent = (value) => `${safeNumber(value).toFixed(1)}%`
const formatScore = (value) => {
  if (value == null || Number.isNaN(Number(value))) return '0.0'
  return Number(value).toFixed(1)
}
const percentOf = (value, total) => (safeNumber(total) > 0 ? Math.min((safeNumber(value) / safeNumber(total)) * 100, 100) : 0)

const kpiCards = computed(() => {
  const users = dashboard.users?.data ?? dashboard.users ?? {}
  const jobs = dashboard.jobs?.data ?? dashboard.jobs ?? {}
  const applications = dashboard.applications?.data ?? dashboard.applications ?? {}
  const profiles = dashboard.profiles?.data ?? dashboard.profiles ?? {}
  const totalJobs = safeNumber(jobs.tong_tin)
  const totalApplications = safeNumber(applications.tong_don_ung_tuyen)

  return [
    {
      label: 'Tổng người dùng',
      value: safeNumber(users.tong),
      sub: `${safeNumber(users.ung_vien)} ứng viên và ${safeNumber(users.nha_tuyen_dung)} nhà tuyển dụng`,
      icon: 'groups',
      iconBg: 'bg-blue-50 dark:bg-blue-900/30',
      iconText: 'text-blue-600',
      pill: `${safeNumber(users.bi_khoa)} bị khóa`,
      pillClass: 'bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300',
      subClass: 'text-blue-600'
    },
    {
      label: 'Tin đang hoạt động',
      value: safeNumber(jobs.hoat_dong),
      sub: `${safeNumber(jobs.tam_ngung)} tin đang tạm ngưng`,
      icon: 'work',
      iconBg: 'bg-emerald-50 dark:bg-emerald-900/30',
      iconText: 'text-emerald-600',
      pill: `${safeNumber(jobs.tong_tin)} tổng tin`,
      pillClass: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-300',
      subClass: 'text-emerald-600'
    },
    {
      label: 'Đơn ứng tuyển',
      value: totalApplications,
      sub: `${safeNumber(applications.chi_tiet?.cho_duyet)} đơn đang chờ duyệt`,
      icon: 'description',
      iconBg: 'bg-amber-50 dark:bg-amber-900/30',
      iconText: 'text-amber-600',
      pill: `${safeNumber(applications.chi_tiet?.chap_nhan)} chấp nhận`,
      pillClass: 'bg-amber-50 text-amber-700 dark:bg-amber-900/20 dark:text-amber-300',
      subClass: 'text-amber-600'
    },
    {
      label: 'Tỉ lệ công khai hồ sơ',
      value: formatPercent(percentOf(profiles.cong_khai, profiles.tong)),
      sub: `${safeNumber(profiles.cong_khai)} / ${safeNumber(profiles.tong)} hồ sơ đang công khai`,
      icon: 'monitoring',
      iconBg: 'bg-rose-50 dark:bg-rose-900/30',
      iconText: 'text-rose-600',
      pill: totalJobs > 0 ? `${formatPercent((totalApplications / totalJobs) * 100)} ứng tuyển/tin` : '0.0% ứng tuyển/tin',
      pillClass: 'bg-rose-50 text-rose-700 dark:bg-rose-900/20 dark:text-rose-300',
      subClass: 'text-rose-600'
    }
  ]
})

const alertCards = computed(() => {
  const users = dashboard.users?.data ?? dashboard.users ?? {}
  const applications = dashboard.applications?.data ?? dashboard.applications ?? {}
  const profiles = dashboard.profiles?.data ?? dashboard.profiles ?? {}
  const companies = dashboard.companies?.data ?? dashboard.companies ?? {}

  return [
    {
      label: 'Đơn ứng tuyển chờ duyệt',
      description: 'Nên xử lý sớm để tránh chậm phản hồi cho ứng viên.',
      value: safeNumber(applications.chi_tiet?.cho_duyet),
      valueClass: 'text-amber-600'
    },
    {
      label: 'Tài khoản bị khóa',
      description: 'Theo dõi các tài khoản không còn hoạt động bình thường.',
      value: safeNumber(users.bi_khoa),
      valueClass: 'text-rose-600'
    },
    {
      label: 'Hồ sơ đã xóa mềm',
      description: 'Có thể cần rà soát hoặc khôi phục nếu người dùng yêu cầu.',
      value: safeNumber(profiles.da_xoa_mem),
      valueClass: 'text-slate-600'
    },
    {
      label: 'Công ty tạm ngưng',
      description: 'Kiểm tra các doanh nghiệp đang không hiển thị.',
      value: safeNumber(companies.tam_ngung),
      valueClass: 'text-[#2463eb]'
    }
  ]
})

const topSkills = computed(() => {
  const max = Math.max(...topSkillsRaw.value.map((item) => safeNumber(item.so_nguoi)), 0)
  return topSkillsRaw.value.slice(0, 5).map((item) => ({
    label: item.ky_nang?.ten_ky_nang ?? item.kyNang?.ten_ky_nang ?? 'Không rõ',
    value: safeNumber(item.so_nguoi),
    percent: max > 0 ? (safeNumber(item.so_nguoi) / max) * 100 : 0
  }))
})

const aiSummary = computed(() => {
  const matching = matchingModels.value
  const bestMatching = [...matching].sort((a, b) => safeNumber(b.average_score) - safeNumber(a.average_score))[0]
  const bestAdvising = (dashboard.advising || [])[0]

  return {
    totalVersions: matching.length,
    bestVersion: bestMatching ? `Model nổi bật: ${bestMatching.model_version}` : 'Chưa có dữ liệu model',
    bestAverage: bestMatching ? formatScore(bestMatching.average_score) : '0.0',
    topSuggestion: bestAdvising?.nghe_de_xuat || 'Chưa có dữ liệu',
    topSuggestionCount: bestAdvising ? `${safeNumber(bestAdvising.total_suggestions)} lượt AI gợi ý` : 'Chưa có thống kê tư vấn'
  }
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
    savedJobs.value = dashboard.savedJobs

    if (notify) {
      showToast('Đã làm mới dữ liệu dashboard.')
    }
  } catch (err) {
    error.value = err.message || 'Không thể tải dashboard admin'
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
