<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { employerApplicationService, employerCompanyService, employerJobService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'
import { formatDateTimeVN, formatHistoricalDateTimeVN } from '@/utils/dateTime'
import { getApplicationStatusLabel, getApplicationStatusMeta } from '@/utils/applicationStatus'
import { useEmployerCompanyPermissions } from '@/composables/useEmployerCompanyPermissions'

const router = useRouter()
const notify = useNotify()

const loading = ref(false)
const company = ref(null)
const jobs = ref([])
const applications = ref([])
const {
  permissions,
  permissionsLoaded,
  ensurePermissionsLoaded,
} = useEmployerCompanyPermissions()
const canViewJobs = computed(() => permissionsLoaded.value && Boolean(permissions.value.jobs))
const canViewApplications = computed(() => permissionsLoaded.value && Boolean(permissions.value.applications))
const canViewCompany = computed(() => permissionsLoaded.value && Boolean(permissions.value.company_profile))
const lockedMessage = 'Bạn không có quyền thực hiện chức năng này'

const applicationStatusLabel = getApplicationStatusLabel
const applicationStatusTone = (status) => `${getApplicationStatusMeta(status).classes} border border-transparent`

const stats = computed(() => {
  const allJobs = jobs.value
  const activeJobs = allJobs.filter((item) => Number(item.trang_thai) === 1)
  const pausedJobs = allJobs.filter((item) => Number(item.trang_thai) !== 1)
  const allApplications = applications.value
  const pendingApplications = allApplications.filter((item) => Number(item.trang_thai) === 0)

  return [
    {
      label: 'Tin đang hoạt động',
      value: activeJobs.length,
      hint: pausedJobs.length ? `${pausedJobs.length} tin đang tạm ngưng` : 'Không có tin nào bị tạm ngưng',
      icon: 'work',
      tone: 'text-blue-300 bg-blue-500/10',
    },
    {
      label: 'Ứng viên đã nộp',
      value: allApplications.length,
      hint: pendingApplications.length ? `${pendingApplications.length} hồ sơ cần xử lý` : 'Không có hồ sơ chờ mới',
      icon: 'groups',
      tone: 'text-violet-300 bg-violet-500/10',
    },
    {
      label: 'CV chờ xem',
      value: pendingApplications.length,
      hint: 'Ưu tiên xử lý trong ngày',
      icon: 'description',
      tone: 'text-amber-300 bg-amber-500/10',
    },
    {
      label: 'Hồ sơ công ty',
      value: company.value ? 'Sẵn sàng' : 'Chưa có',
      hint: company.value?.ten_cong_ty || 'Thiết lập công ty để đăng tuyển',
      icon: 'apartment',
      tone: 'text-emerald-300 bg-emerald-500/10',
    },
  ]
})

const recentJobs = computed(() => jobs.value.slice(0, 4))
const recentApplications = computed(() => applications.value.slice(0, 5))

const funnelStats = computed(() => {
  const all = applications.value
  const total = all.length || 1
  const rows = [
    { label: 'Chờ duyệt', status: 0 },
    { label: 'Đã xem', status: 1 },
    { label: 'Hẹn phỏng vấn', status: 2 },
    { label: 'Qua phỏng vấn', status: 3 },
    { label: 'Trúng tuyển', status: 4 },
    { label: 'Từ chối', status: 5 },
  ]

  return rows.map((row) => {
    const count = all.filter((item) => Number(item.trang_thai) === row.status).length
    return {
      ...row,
      count,
      percent: Math.round((count / total) * 100),
    }
  })
})

const advancedMetrics = computed(() => {
  const all = applications.value
  const total = all.length || 0
  const interviewed = all.filter((item) => [2, 3, 4].includes(Number(item.trang_thai))).length
  const hired = all.filter((item) => Number(item.trang_thai) === 4).length
  const rejected = all.filter((item) => Number(item.trang_thai) === 5).length

  return [
    {
      label: 'Tỷ lệ vào phỏng vấn',
      value: total ? `${Math.round((interviewed / total) * 100)}%` : '0%',
      hint: `${interviewed}/${total} hồ sơ đã vào pipeline phỏng vấn`,
    },
    {
      label: 'Tỷ lệ tuyển thành công',
      value: total ? `${Math.round((hired / total) * 100)}%` : '0%',
      hint: `${hired}/${total} hồ sơ trúng tuyển`,
    },
    {
      label: 'Tỷ lệ từ chối',
      value: total ? `${Math.round((rejected / total) * 100)}%` : '0%',
      hint: `${rejected}/${total} hồ sơ không phù hợp`,
    },
  ]
})

const cvSourceStats = computed(() => {
  const uploaded = applications.value.filter((item) => item.ho_so?.file_cv).length
  const builder = applications.value.filter((item) => !item.ho_so?.file_cv).length
  const total = Math.max(1, uploaded + builder)

  return [
    { label: 'CV upload', count: uploaded, percent: Math.round((uploaded / total) * 100), tone: 'bg-blue-500' },
    { label: 'CV tạo trên hệ thống', count: builder, percent: Math.round((builder / total) * 100), tone: 'bg-emerald-500' },
  ]
})

const topApplicationJobs = computed(() => {
  const map = new Map()

  applications.value.forEach((application) => {
    const jobId = application.tin_tuyen_dung?.id || application.tin_tuyen_dung_id
    if (!jobId) return

    const current = map.get(jobId) || {
      id: jobId,
      title: application.tin_tuyen_dung?.tieu_de || 'Tin tuyển dụng',
      total: 0,
      pending: 0,
      hired: 0,
    }

    current.total += 1
    if (Number(application.trang_thai) === 0) current.pending += 1
    if (Number(application.trang_thai) === 4) current.hired += 1
    map.set(jobId, current)
  })

  return [...map.values()].sort((a, b) => b.total - a.total).slice(0, 5)
})

const hiringInsights = computed(() => {
  const insights = []

  if (!company.value) {
    insights.push('Hoàn thiện hồ sơ công ty để bắt đầu đăng tin tuyển dụng và tạo độ tin cậy với ứng viên.')
  }

  const activeJobs = jobs.value.filter((item) => Number(item.trang_thai) === 1).length
  if (!activeJobs) {
    insights.push('Hiện chưa có tin tuyển dụng đang hoạt động. Hãy đăng hoặc kích hoạt lại một tin để thu hút ứng viên.')
  }

  const pendingApplications = applications.value.filter((item) => Number(item.trang_thai) === 0).length
  if (pendingApplications) {
    insights.push(`Có ${pendingApplications} hồ sơ đang ở trạng thái chờ. Nên xem và phản hồi sớm để không bỏ lỡ ứng viên phù hợp.`)
  }

  const topJob = topApplicationJobs.value[0]
  if (topJob) {
    insights.push(`Tin "${topJob.title}" đang có nhiều ứng viên nhất (${topJob.total} hồ sơ). Nên ưu tiên rà soát pipeline cho tin này.`)
  }

  if (!insights.length) {
    insights.push('Dữ liệu tuyển dụng đang ổn định. Hãy tiếp tục cập nhật JD và theo dõi hồ sơ mới mỗi ngày.')
  }

  return insights.slice(0, 3)
})

const companyCompletion = computed(() => {
  if (!company.value) return 0

  const fields = [
    company.value.ten_cong_ty,
    company.value.mo_ta,
    company.value.dia_chi,
    company.value.website,
    company.value.nganh_nghe_id,
  ]

  const filled = fields.filter(Boolean).length
  return Math.round((filled / fields.length) * 100)
})

const fetchDashboard = async () => {
  loading.value = true
  try {
    await ensurePermissionsLoaded()
    const [companyRes, jobsRes, applicationsRes] = await Promise.all([
      employerCompanyService.getCompany().catch(() => null),
      canViewJobs.value ? employerJobService.getJobs({ per_page: 50 }) : Promise.resolve(null),
      canViewApplications.value ? employerApplicationService.getApplications({ per_page: 50 }) : Promise.resolve(null),
    ])

    company.value = companyRes?.data || null
    jobs.value = jobsRes?.data?.data || []
    applications.value = applicationsRes?.data?.data || []
  } catch (error) {
    notify.apiError(error, 'Không tải được dashboard nhà tuyển dụng.')
  } finally {
    loading.value = false
  }
}

const showLockedNotice = () => {
  notify.warning(lockedMessage)
}

const goToCompany = () => {
  if (!canViewCompany.value) {
    showLockedNotice()
    return
  }

  router.push('/employer/company')
}

const goToJobs = () => {
  if (!canViewJobs.value) {
    showLockedNotice()
    return
  }

  router.push('/employer/jobs')
}

const goToCandidates = () => {
  if (!canViewApplications.value) {
    showLockedNotice()
    return
  }

  router.push('/employer/candidates')
}

const refreshDashboard = async () => {
  await fetchDashboard()
  notify.info('Đã tải lại dashboard nhà tuyển dụng.')
}

const formatDateTime = (value) => formatDateTimeVN(value, 'Chưa cập nhật')
const formatSubmittedDateTime = (value) => formatHistoricalDateTimeVN(value, 'Chưa cập nhật')

onMounted(fetchDashboard)
</script>

<template>
  <div class="mx-auto max-w-7xl">
    <div class="mb-8 rounded-3xl border border-blue-200 bg-gradient-to-r from-white via-blue-50 to-[#dce7ff] p-6 text-slate-900 shadow-[0_24px_70px_rgba(148,163,184,0.18)] dark:border-slate-800 dark:bg-gradient-to-r dark:from-slate-900 dark:via-slate-900 dark:to-[#1e46a7] dark:text-white dark:shadow-[0_24px_70px_rgba(14,22,42,0.35)]">
      <div class="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
        <div class="max-w-3xl">
          <p class="mb-2 text-xs font-semibold uppercase tracking-[0.3em] text-blue-600/80 dark:text-blue-200/80">Nhà tuyển dụng</p>
          <h1 class="text-3xl font-black tracking-tight text-slate-900 sm:text-4xl dark:text-white">Tổng quan tuyển dụng hôm nay</h1>
          <p class="mt-3 text-sm leading-7 text-slate-600 sm:text-base dark:text-blue-100/80">
            Theo dõi nhanh tình trạng công ty, số tin đang mở và hồ sơ ứng viên cần xử lý để vận hành tuyển dụng mượt hơn.
          </p>
        </div>

        <div class="flex flex-wrap gap-3">
          <button
            class="inline-flex items-center gap-2 rounded-2xl border border-blue-200 bg-white/80 px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-white dark:border-white/15 dark:bg-white/10 dark:text-white dark:hover:bg-white/15"
            type="button"
            @click="refreshDashboard"
          >
            <span class="material-symbols-outlined text-[18px]">refresh</span>
            Tải lại
          </button>
          <button
            class="inline-flex items-center gap-2 rounded-2xl bg-[#2463eb] px-4 py-3 text-sm font-bold text-white shadow-lg shadow-[#2463eb]/20 transition hover:-translate-y-0.5 dark:bg-white dark:text-[#1f49b6] dark:shadow-black/10"
            type="button"
            @click="goToJobs"
          >
            <span class="material-symbols-outlined text-[18px]">add_circle</span>
            Quản lý tin tuyển dụng
          </button>
        </div>
      </div>

      <div class="mt-6 grid grid-cols-1 gap-3 md:grid-cols-3">
        <div class="rounded-2xl border border-blue-200 bg-white/70 px-4 py-4 backdrop-blur dark:border-white/10 dark:bg-white/8">
          <p class="text-xs uppercase tracking-[0.24em] text-blue-600/70 dark:text-blue-100/60">Công ty</p>
          <p class="mt-2 text-lg font-bold text-slate-900 dark:text-white">{{ company?.ten_cong_ty || 'Chưa thiết lập' }}</p>
          <p class="mt-1 text-sm text-slate-600 dark:text-blue-100/70">
            {{ company ? `Hồ sơ hoàn thiện ${companyCompletion}%` : 'Tạo hồ sơ công ty để bắt đầu đăng tuyển.' }}
          </p>
        </div>
        <div class="rounded-2xl border border-blue-200 bg-white/70 px-4 py-4 backdrop-blur dark:border-white/10 dark:bg-white/8">
          <p class="text-xs uppercase tracking-[0.24em] text-blue-600/70 dark:text-blue-100/60">Nhịp tuyển dụng</p>
          <p class="mt-2 text-lg font-bold text-slate-900 dark:text-white">{{ stats[0].value }} tin đang mở</p>
          <p class="mt-1 text-sm text-slate-600 dark:text-blue-100/70">{{ stats[1].hint }}</p>
        </div>
        <div class="rounded-2xl border border-blue-200 bg-white/70 px-4 py-4 backdrop-blur dark:border-white/10 dark:bg-white/8">
          <p class="text-xs uppercase tracking-[0.24em] text-blue-600/70 dark:text-blue-100/60">Ưu tiên hôm nay</p>
          <p class="mt-2 text-lg font-bold text-slate-900 dark:text-white">{{ stats[2].value }} hồ sơ chờ xử lý</p>
          <p class="mt-1 text-sm text-slate-600 dark:text-blue-100/70">Xử lý hồ sơ mới để không bỏ lỡ ứng viên phù hợp.</p>
        </div>
      </div>
    </div>

    <div v-if="loading" class="grid grid-cols-1 gap-5 lg:grid-cols-4">
      <div v-for="index in 8" :key="index" class="h-36 animate-pulse rounded-2xl bg-slate-200/60 dark:bg-slate-800/70" />
    </div>

    <template v-else>
      <div class="mb-6 grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-4">
        <div
          v-for="card in stats"
          :key="card.label"
          class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm shadow-slate-950/5 transition hover:-translate-y-0.5 dark:border-slate-800 dark:bg-slate-900"
        >
          <div class="flex items-start justify-between gap-3">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">{{ card.label }}</p>
              <p class="mt-3 text-3xl font-black text-slate-900 dark:text-white">{{ card.value }}</p>
            </div>
            <span class="material-symbols-outlined rounded-2xl p-3 text-[22px]" :class="card.tone">{{ card.icon }}</span>
          </div>
          <p class="mt-4 text-sm leading-6 text-slate-500 dark:text-slate-400">{{ card.hint }}</p>
        </div>
      </div>

      <div class="mb-6 grid grid-cols-1 gap-6 xl:grid-cols-[minmax(0,1.35fr)_420px]">
        <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm shadow-slate-950/5 dark:border-slate-800 dark:bg-slate-900">
          <div class="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <h2 class="text-xl font-bold text-slate-900 dark:text-white">Phễu tuyển dụng</h2>
              <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Theo dõi tỷ lệ hồ sơ ở từng bước xử lý để phát hiện điểm nghẽn.</p>
            </div>
            <span class="rounded-full bg-[#2463eb]/10 px-3 py-1 text-xs font-black text-[#2463eb] dark:text-[#8fb1ff]">
              {{ applications.length }} hồ sơ
            </span>
          </div>
          <div class="mt-5 space-y-4">
            <div v-for="row in funnelStats" :key="row.label">
              <div class="mb-2 flex items-center justify-between text-sm">
                <span class="font-semibold text-slate-700 dark:text-slate-200">{{ row.label }}</span>
                <span class="font-bold text-slate-900 dark:text-white">{{ row.count }} hồ sơ · {{ row.percent }}%</span>
              </div>
              <div class="h-3 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
                <div class="h-full rounded-full bg-gradient-to-r from-[#2463eb] to-[#724dff]" :style="{ width: `${row.percent}%` }" />
              </div>
            </div>
          </div>
        </div>

        <div class="space-y-4">
          <div class="grid grid-cols-1 gap-3">
            <div
              v-for="metric in advancedMetrics"
              :key="metric.label"
              class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm shadow-slate-950/5 dark:border-slate-800 dark:bg-slate-900"
            >
              <p class="text-xs font-bold uppercase tracking-[0.2em] text-slate-500">{{ metric.label }}</p>
              <p class="mt-2 text-3xl font-black text-slate-900 dark:text-white">{{ metric.value }}</p>
              <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">{{ metric.hint }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="mb-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm shadow-slate-950/5 dark:border-slate-800 dark:bg-slate-900">
          <h2 class="text-xl font-bold text-slate-900 dark:text-white">Nguồn CV trong ứng tuyển</h2>
          <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">So sánh tỷ trọng CV upload và CV tạo trực tiếp trên hệ thống.</p>
          <div class="mt-5 space-y-4">
            <div v-for="source in cvSourceStats" :key="source.label">
              <div class="mb-2 flex items-center justify-between text-sm">
                <span class="font-semibold text-slate-700 dark:text-slate-200">{{ source.label }}</span>
                <span class="font-bold text-slate-900 dark:text-white">{{ source.count }} · {{ source.percent }}%</span>
              </div>
              <div class="h-3 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
                <div class="h-full rounded-full" :class="source.tone" :style="{ width: `${source.percent}%` }" />
              </div>
            </div>
          </div>
        </div>

        <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm shadow-slate-950/5 dark:border-slate-800 dark:bg-slate-900">
          <h2 class="text-xl font-bold text-slate-900 dark:text-white">Top tin có nhiều ứng viên</h2>
          <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Ưu tiên theo dõi các tin đang tạo nhiều hồ sơ nhất.</p>
          <div v-if="topApplicationJobs.length" class="mt-5 space-y-3">
            <div
              v-for="job in topApplicationJobs"
              :key="job.id"
              class="rounded-2xl bg-slate-50 p-4 dark:bg-slate-800/70"
            >
              <p class="line-clamp-1 font-black text-slate-900 dark:text-white">{{ job.title }}</p>
              <div class="mt-2 flex flex-wrap gap-2 text-xs font-bold text-slate-500 dark:text-slate-400">
                <span>{{ job.total }} hồ sơ</span>
                <span>{{ job.pending }} chờ xử lý</span>
                <span>{{ job.hired }} trúng tuyển</span>
              </div>
            </div>
          </div>
          <p v-else class="mt-5 rounded-xl border border-dashed border-slate-200 px-4 py-8 text-center text-sm text-slate-500 dark:border-slate-700 dark:text-slate-400">
            Chưa có dữ liệu ứng tuyển theo tin.
          </p>
        </div>
      </div>

      <div class="grid grid-cols-1 gap-6 xl:grid-cols-[minmax(0,1.5fr)_380px]">
        <div class="space-y-6">
          <div class="rounded-2xl border border-slate-200 bg-white shadow-sm shadow-slate-950/5 dark:border-slate-800 dark:bg-slate-900">
            <div class="flex flex-col gap-3 border-b border-slate-200 px-6 py-5 dark:border-slate-800 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 class="text-xl font-bold text-slate-900 dark:text-white">Tin tuyển dụng gần đây</h2>
                <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Theo dõi nhanh các tin vừa tạo và tình trạng hiện tại.</p>
              </div>
              <button
                class="inline-flex items-center gap-2 rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
                type="button"
                @click="goToJobs"
              >
                <span class="material-symbols-outlined text-[18px]">arrow_outward</span>
                Xem tất cả
              </button>
            </div>

            <div v-if="recentJobs.length" class="divide-y divide-slate-200 dark:divide-slate-800">
              <div
                v-for="job in recentJobs"
                :key="job.id"
                class="flex flex-col gap-4 px-6 py-5 sm:flex-row sm:items-start sm:justify-between"
              >
                <div class="min-w-0">
                  <h3 class="text-lg font-bold text-slate-900 dark:text-white">{{ job.tieu_de }}</h3>
                  <div class="mt-2 flex flex-wrap gap-2 text-xs text-slate-500 dark:text-slate-400">
                    <span class="rounded-full bg-slate-100 px-2.5 py-1 font-medium dark:bg-slate-800">{{ job.hinh_thuc_lam_viec || 'Chưa cập nhật hình thức' }}</span>
                    <span class="rounded-full bg-slate-100 px-2.5 py-1 font-medium dark:bg-slate-800">{{ job.cap_bac || 'Chưa cập nhật cấp bậc' }}</span>
                    <span class="rounded-full bg-slate-100 px-2.5 py-1 font-medium dark:bg-slate-800">{{ job.dia_diem_lam_viec || 'Chưa cập nhật địa điểm' }}</span>
                  </div>
                  <p class="mt-3 text-sm leading-6 text-slate-500 dark:text-slate-400">
                    {{ job.mo_ta_cong_viec?.slice(0, 140) || 'Tin tuyển dụng chưa có mô tả chi tiết.' }}{{ job.mo_ta_cong_viec?.length > 140 ? '...' : '' }}
                  </p>
                </div>

                <div class="flex min-w-[180px] flex-col items-start gap-3 sm:items-end">
                  <span
                    class="inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-bold"
                    :class="Number(job.trang_thai) === 1 ? 'bg-emerald-500/10 text-emerald-700 border border-emerald-400/20 dark:text-emerald-300' : 'bg-slate-500/10 text-slate-700 border border-slate-400/20 dark:text-slate-300'"
                  >
                    <span class="h-2 w-2 rounded-full" :class="Number(job.trang_thai) === 1 ? 'bg-emerald-500 dark:bg-emerald-400' : 'bg-slate-500 dark:bg-slate-400'" />
                    {{ Number(job.trang_thai) === 1 ? 'Đang hoạt động' : 'Tạm ngưng' }}
                  </span>
                  <p class="text-sm font-semibold text-slate-900 dark:text-white">
                    {{ job.ngay_het_han ? `Hết hạn ${formatDateTime(job.ngay_het_han)}` : 'Chưa cập nhật hạn' }}
                  </p>
                </div>
              </div>
            </div>

            <div v-else class="px-6 py-12 text-center">
              <span class="material-symbols-outlined text-[42px] text-slate-400">work_off</span>
              <h3 class="mt-4 text-lg font-bold text-slate-900 dark:text-white">Chưa có tin tuyển dụng</h3>
              <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">Hãy tạo tin đầu tiên để bắt đầu thu hút ứng viên.</p>
              <button
                class="mt-5 inline-flex items-center gap-2 rounded-xl bg-[#2463eb] px-4 py-2.5 text-sm font-bold text-white shadow-lg shadow-[#2463eb]/20"
                type="button"
                @click="goToJobs"
              >
                <span class="material-symbols-outlined text-[18px]">add</span>
                Tạo tin tuyển dụng
              </button>
            </div>
          </div>

          <div class="rounded-2xl border border-slate-200 bg-white shadow-sm shadow-slate-950/5 dark:border-slate-800 dark:bg-slate-900">
            <div class="flex flex-col gap-3 border-b border-slate-200 px-6 py-5 dark:border-slate-800 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 class="text-xl font-bold text-slate-900 dark:text-white">Ứng viên mới nộp</h2>
                <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Danh sách hồ sơ gần nhất từ các tin tuyển dụng của công ty.</p>
              </div>
              <button
                class="inline-flex items-center gap-2 rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
                type="button"
                @click="goToCandidates"
              >
                <span class="material-symbols-outlined text-[18px]">groups</span>
                Xem hồ sơ công khai
              </button>
            </div>

            <div v-if="recentApplications.length" class="divide-y divide-slate-200 dark:divide-slate-800">
              <div
                v-for="application in recentApplications"
                :key="application.id"
                class="flex flex-col gap-3 px-6 py-5 sm:flex-row sm:items-center sm:justify-between"
              >
                <div class="min-w-0">
                  <p class="text-lg font-bold text-slate-900 dark:text-white">
                    {{ application.ho_so?.tieu_de_ho_so || 'Hồ sơ ứng viên' }}
                  </p>
                  <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
                    {{ application.ho_so?.nguoi_dung?.email || 'Chưa cập nhật email' }}
                  </p>
                  <p class="mt-2 text-sm text-slate-600 dark:text-slate-300">
                    Ứng tuyển vào: <span class="font-semibold">{{ application.tin_tuyen_dung?.tieu_de || 'Tin tuyển dụng' }}</span>
                  </p>
                </div>

                <div class="flex min-w-[220px] flex-col items-start gap-3 sm:items-end">
                  <span class="inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-bold" :class="applicationStatusTone(application.trang_thai)">
                    {{ applicationStatusLabel(application.trang_thai) || 'Chưa cập nhật' }}
                  </span>
                  <p class="text-xs text-slate-500 dark:text-slate-400">{{ formatSubmittedDateTime(application.thoi_gian_ung_tuyen) }}</p>
                </div>
              </div>
            </div>

            <div v-else class="px-6 py-12 text-center">
              <span class="material-symbols-outlined text-[42px] text-slate-400">inbox_text</span>
              <h3 class="mt-4 text-lg font-bold text-slate-900 dark:text-white">Chưa có ứng tuyển nào</h3>
              <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">Khi ứng viên nộp hồ sơ, bạn sẽ thấy lịch sử xử lý tại đây.</p>
            </div>
          </div>
        </div>

        <div class="space-y-6">
          <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm shadow-slate-950/5 dark:border-slate-800 dark:bg-slate-900">
            <div class="flex items-start justify-between gap-3">
              <div>
                <h2 class="text-xl font-bold text-slate-900 dark:text-white">Hồ sơ công ty</h2>
                <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Giữ thông tin công ty đầy đủ để tăng độ tin cậy khi tuyển dụng.</p>
              </div>
              <span class="material-symbols-outlined rounded-2xl bg-[#2463eb]/10 p-3 text-[22px] text-[#8cb4ff]">apartment</span>
            </div>

            <div class="mt-5 rounded-2xl border border-slate-200/80 bg-slate-50/80 p-4 dark:border-slate-800 dark:bg-slate-950/40">
              <div class="flex items-center justify-between text-sm font-semibold text-slate-700 dark:text-slate-200">
                <span>Tiến độ hoàn thiện</span>
                <span>{{ companyCompletion }}%</span>
              </div>
              <div class="mt-3 h-2.5 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800">
                <div class="h-full rounded-full bg-gradient-to-r from-[#2463eb] via-[#4d73ff] to-[#6f52ff]" :style="{ width: `${companyCompletion}%` }" />
              </div>
            </div>

            <div class="mt-5 space-y-3 text-sm text-slate-600 dark:text-slate-300">
              <div class="flex items-start justify-between gap-3">
                <span class="text-slate-500 dark:text-slate-400">Tên công ty</span>
                <span class="text-right font-semibold text-slate-900 dark:text-white">{{ company?.ten_cong_ty || 'Chưa thiết lập' }}</span>
              </div>
              <div class="flex items-start justify-between gap-3">
                <span class="text-slate-500 dark:text-slate-400">Website</span>
                <span class="text-right font-semibold text-slate-900 dark:text-white">{{ company?.website || 'Chưa cập nhật' }}</span>
              </div>
              <div class="flex items-start justify-between gap-3">
                <span class="text-slate-500 dark:text-slate-400">Địa chỉ</span>
                <span class="text-right font-semibold text-slate-900 dark:text-white">{{ company?.dia_chi || 'Chưa cập nhật' }}</span>
              </div>
            </div>

            <button
              class="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-[#2463eb] px-4 py-3 text-sm font-bold text-white shadow-lg shadow-[#2463eb]/20"
              type="button"
              @click="goToCompany"
            >
              <span class="material-symbols-outlined text-[18px]">edit_square</span>
              Cập nhật công ty
            </button>
          </div>

          <div class="rounded-2xl border border-slate-200 bg-gradient-to-br from-[#2463eb] via-[#355dff] to-[#724dff] p-6 text-white shadow-[0_24px_60px_rgba(36,99,235,0.28)] dark:border-slate-800">
            <p class="text-xs font-semibold uppercase tracking-[0.24em] text-white/70">Hàm ý vận hành</p>
            <h2 class="mt-3 text-2xl font-black leading-tight">3 việc nên làm ngay hôm nay</h2>
            <ul class="mt-5 space-y-3 text-sm leading-7 text-white/90">
              <li v-for="insight in hiringInsights" :key="insight" class="flex gap-3">
                <span class="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-white/90" />
                <span>{{ insight }}</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
