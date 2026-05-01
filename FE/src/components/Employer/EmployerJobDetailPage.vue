<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { employerApplicationService, employerBillingService, employerJobService } from '@/services/api'
import { useEmployerCompanyPermissions } from '@/composables/useEmployerCompanyPermissions'
import { useNotify } from '@/composables/useNotify'
import { getApplicationStatusMeta } from '@/utils/applicationStatus'
import { formatDateTimeVN, formatHistoricalDateTimeVN } from '@/utils/dateTime'
import { getAuthToken } from '@/utils/authStorage'
import { hasBuilderCv, openCvPrintPreview } from '@/utils/profileCvBuilder'

const route = useRoute()
const router = useRouter()
const notify = useNotify()
const { ensurePermissionsLoaded, canManageJobs, canManageAllAssignments, currentEmployerId, currentInternalRoleLabel } = useEmployerCompanyPermissions()

const loading = ref(false)
const billingLoading = ref(false)
const parsingLoading = ref(false)
const togglingStatus = ref(false)
const shortlistLoading = ref(false)
const aiScoringLoading = ref(false)
const comparingShortlist = ref(false)
const sponsorLoading = ref('')
const job = ref(null)
const applications = ref([])
const shortlistItems = ref([])
const shortlistMeta = ref(null)
const selectedCompareProfileIds = ref([])
const comparisonResult = ref(null)
const shortlistScope = ref('public')
const billingWallet = ref(null)
const billingPricing = ref([])
const billingEntitlements = ref([])

const formatDateTime = (value) => formatDateTimeVN(value, 'Chưa cập nhật')
const formatSubmittedDateTime = (value) => formatHistoricalDateTimeVN(value, 'Chưa cập nhật')
const formatCurrency = (value) => `${Number(value || 0).toLocaleString('vi-VN')} đ`

const formatSalary = (job) => {
  const salaryFrom = Number(job?.muc_luong_tu || 0)
  const salaryTo = Number(job?.muc_luong_den || 0)

  if (salaryFrom && salaryTo) {
    return `${salaryFrom.toLocaleString('vi-VN')} đ - ${salaryTo.toLocaleString('vi-VN')} đ`
  }

  if (salaryFrom) return `${salaryFrom.toLocaleString('vi-VN')} đ`
  return 'Thỏa thuận'
}

const statusLabel = computed(() => (Number(job.value?.trang_thai) === 1 ? 'Đang hoạt động' : 'Tạm ngưng'))
const statusTone = computed(() =>
  Number(job.value?.trang_thai) === 1
    ? 'bg-emerald-500/10 text-emerald-300 border border-emerald-400/20'
    : 'bg-amber-500/10 text-amber-300 border border-amber-400/20'
)

const parseStatusMeta = computed(() => {
  const status = Number(job.value?.parsing?.parse_status || 0)

  if (status === 1) {
    return {
      label: 'Đã parse JD',
      classes: 'bg-violet-500/10 text-violet-300 border border-violet-400/20',
    }
  }

  if (status === 2) {
    return {
      label: 'Parse lỗi',
      classes: 'bg-rose-500/10 text-rose-300 border border-rose-400/20',
    }
  }

  return {
    label: 'Chưa parse JD',
    classes: 'bg-slate-500/10 text-slate-300 border border-slate-400/20',
  }
})

const statusCards = computed(() => {
  const currentJob = job.value
  if (!currentJob) return []

  return [
    {
      label: 'Tổng hồ sơ',
      value: currentJob.tong_ho_so || 0,
      hint: 'Đã nộp vào tin này',
      icon: 'groups',
      tone: 'text-blue-300 bg-blue-500/10',
    },
    {
      label: 'Trúng tuyển',
      value: currentJob.so_luong_da_nhan || 0,
      hint: `${currentJob.so_luong_con_lai || 0} chỉ tiêu còn lại`,
      icon: 'task_alt',
      tone: 'text-emerald-300 bg-emerald-500/10',
    },
    {
      label: 'Đang chờ',
      value: currentJob.ho_so_dang_cho || 0,
      hint: 'Nên xử lý sớm',
      icon: 'hourglass_top',
      tone: 'text-amber-300 bg-amber-500/10',
    },
    {
      label: 'Đã xem',
      value: currentJob.ho_so_da_xem || 0,
      hint: `${currentJob.ho_so_tu_choi || 0} hồ sơ đã từ chối`,
      icon: 'visibility',
      tone: 'text-sky-300 bg-sky-500/10',
    },
  ]
})

const applicationStatusMeta = getApplicationStatusMeta
const isOwnedJob = computed(() => Number(job.value?.hr_phu_trach?.id || job.value?.hr_phu_trach_id || 0) === Number(currentEmployerId.value || 0))
const canMutateCurrentJob = computed(() => Boolean(canManageJobs.value && (canManageAllAssignments.value || isOwnedJob.value)))
const walletAvailable = computed(() => Number(billingWallet.value?.so_du_kha_dung || 0))
const featuredStatusLabel = computed(() => {
  if (!job.value?.is_featured) return 'Tin đang chạy hiển thị thường'
  return `Đang nổi bật đến ${formatDateTime(job.value?.featured_until)}`
})
const resolveBillingFeature = (featureCode) => {
  const pricing = billingPricing.value.find((item) => item.feature_code === featureCode) || null
  const entitlement = billingEntitlements.value.find((item) => item.feature_code === featureCode) || null
  const hasIncludedQuota = Boolean(entitlement?.subscription_is_unlimited)
    || Number(entitlement?.subscription_quota_remaining || 0) > 0
    || Number(entitlement?.free_quota_remaining || 0) > 0
  const walletPrice = Number(pricing?.don_gia || entitlement?.wallet_price || 0)
  const walletUnit = pricing?.don_vi_tinh || entitlement?.wallet_unit || 'lượt'
  const requiresWallet = !hasIncludedQuota && walletPrice > 0

  return {
    featureCode,
    pricing,
    entitlement,
    hasIncludedQuota,
    walletPrice,
    walletUnit,
    requiresWallet,
    affordable: !requiresWallet || walletAvailable.value >= walletPrice,
  }
}
const shortlistAiFeature = computed(() => resolveBillingFeature('employer_shortlist_ai_explanation'))
const compareAiFeature = computed(() => resolveBillingFeature('employer_candidate_compare_ai'))
const featuredPackages = computed(() =>
  ['employer_featured_job_7d', 'employer_featured_job_30d']
    .map((featureCode) => {
      const pricing = billingPricing.value.find((item) => item.feature_code === featureCode) || null
      const entitlement = billingEntitlements.value.find((item) => item.feature_code === featureCode) || null

      return {
        featureCode,
        label: pricing?.ten_hien_thi || (featureCode === 'employer_featured_job_7d' ? 'Featured Job 7 ngày' : 'Featured Job 30 ngày'),
        description: featureCode === 'employer_featured_job_7d'
          ? 'Đẩy tin lên nhóm nổi bật trong 7 ngày.'
          : 'Giữ tin trong nhóm nổi bật trong 30 ngày.',
        price: Number(pricing?.don_gia || entitlement?.wallet_price || 0),
        unit: pricing?.don_vi_tinh || entitlement?.wallet_unit || 'listing',
      }
    })
    .filter((item) => item.price > 0)
)

const requiredSkills = computed(() => {
  const manualSkills = (job.value?.ky_nang_yeu_caus || [])
    .map((item) => item?.ky_nang?.ten_ky_nang)
    .filter(Boolean)

  const parsedSkills = (job.value?.parsing?.parsed_skills_json || [])
    .map((item) => item?.skill_name || item?.ten_ky_nang || item?.name)
    .filter(Boolean)

  return [...new Set([...manualSkills, ...parsedSkills])]
})

const parsedRequirements = computed(() =>
  (job.value?.parsing?.parsed_requirements_json || [])
    .map((item) => {
      if (typeof item === 'string') return item
      return item?.requirement || item?.text || item?.value || item?.name || null
    })
    .filter(Boolean)
)

const parsedBenefits = computed(() =>
  (job.value?.parsing?.parsed_benefits_json || [])
    .map((item) => {
      if (typeof item === 'string') return item
      return item?.benefit || item?.text || item?.value || item?.name || null
    })
    .filter(Boolean)
)

const upcomingApplications = computed(() => applications.value.slice(0, 6))
const topShortlistItems = computed(() => shortlistItems.value.slice(0, 5))
const canCompareShortlist = computed(() => selectedCompareProfileIds.value.length >= 2)
const formatFeaturePrice = (feature) => {
  if (!feature?.walletPrice) return 'Chưa cấu hình giá'
  return `${formatCurrency(feature.walletPrice)}/${feature.walletUnit || 'lượt'}`
}
const canRunPaidFeature = (feature) => {
  if (!feature) return true
  if (feature.hasIncludedQuota) return true
  if (!feature.walletPrice) return true
  return feature.affordable
}

const loadBillingContext = async () => {
  billingLoading.value = true
  try {
    const [walletResponse, pricingResponse, entitlementsResponse] = await Promise.all([
      employerBillingService.getWallet(),
      employerBillingService.getPricing(),
      employerBillingService.getEntitlements(),
    ])

    billingWallet.value = walletResponse?.data?.wallet || null
    billingPricing.value = pricingResponse?.data || []
    billingEntitlements.value = entitlementsResponse?.data?.entitlements || []
  } catch (error) {
    billingWallet.value = null
    billingPricing.value = []
    billingEntitlements.value = []
    notify.apiError(error, 'Không tải được dữ liệu billing employer.')
  } finally {
    billingLoading.value = false
  }
}

const fetchJobDetail = async () => {
  loading.value = true
  try {
    const [jobResponse, applicationResponse] = await Promise.all([
      employerJobService.getJobById(route.params.id),
      employerApplicationService.getApplications({
        tin_tuyen_dung_id: route.params.id,
        per_page: 50,
      }),
    ])

    job.value = jobResponse?.data || null
    applications.value = applicationResponse?.data?.data || []
    if (job.value?.id) {
      await fetchShortlist(false)
    }
  } catch (error) {
    notify.apiError(error, 'Không tải được chi tiết tin tuyển dụng.')
    await router.push('/employer/jobs')
  } finally {
    loading.value = false
  }
}

const sponsorJob = async (featureCode) => {
  if (!job.value?.id) return
  if (!canMutateCurrentJob.value) {
    notify.warning(canManageJobs.value
      ? 'Bạn chỉ có thể đẩy nổi bật cho tin tuyển dụng mình phụ trách.'
      : `Vai trò ${currentInternalRoleLabel.value} không thể đẩy nổi bật tin tuyển dụng.`)
    return
  }

  sponsorLoading.value = featureCode
  try {
    const response = await employerJobService.sponsorJob(job.value.id, featureCode)
    notify.success(response?.message || 'Đã kích hoạt featured listing cho tin tuyển dụng.')
    await Promise.all([fetchJobDetail(), loadBillingContext()])
  } catch (error) {
    notify.apiError(error, 'Không thể kích hoạt featured listing cho tin tuyển dụng.')
  } finally {
    sponsorLoading.value = ''
  }
}

const fetchShortlist = async (withAi = false) => {
  if (!route.params.id) return

  if (withAi) {
    aiScoringLoading.value = true
  } else {
    shortlistLoading.value = true
  }

  try {
    const response = await employerJobService.getShortlist(route.params.id, {
      limit: 10,
      scope: shortlistScope.value,
      ai_explain: withAi,
    })
    shortlistItems.value = response?.data?.items || []
    shortlistMeta.value = response?.data?.meta || null
    selectedCompareProfileIds.value = []
    comparisonResult.value = null
    if (withAi) {
      await loadBillingContext()
    }
  } catch (error) {
    shortlistItems.value = []
    shortlistMeta.value = null
    selectedCompareProfileIds.value = []
    comparisonResult.value = null
    notify.apiError(error, 'Không tải được AI Shortlist cho tin tuyển dụng.')
  } finally {
    shortlistLoading.value = false
    aiScoringLoading.value = false
  }
}

const changeShortlistScope = async (scope) => {
  if (shortlistScope.value === scope) return
  shortlistScope.value = scope
  await fetchShortlist(false)
}

const rescoreShortlistWithAi = async () => {
  await fetchShortlist(true)
}

const isSelectedForCompare = (item) => selectedCompareProfileIds.value.includes(Number(item?.ho_so?.id || 0))

const toggleCompareSelection = (item) => {
  const profileId = Number(item?.ho_so?.id || 0)
  if (!profileId) return

  if (selectedCompareProfileIds.value.includes(profileId)) {
    selectedCompareProfileIds.value = selectedCompareProfileIds.value.filter((id) => id !== profileId)
    return
  }

  if (selectedCompareProfileIds.value.length >= 5) {
    notify.warning('Chỉ có thể so sánh tối đa 5 CV trong một lần.')
    return
  }

  selectedCompareProfileIds.value = [...selectedCompareProfileIds.value, profileId]
}

const compareShortlistCandidates = async () => {
  if (!canCompareShortlist.value) {
    notify.info('Vui lòng chọn ít nhất 2 CV để so sánh.')
    return
  }

  comparingShortlist.value = true
  try {
    const response = await employerJobService.compareShortlistCandidates(route.params.id, selectedCompareProfileIds.value, { ai_explain: true })
    comparisonResult.value = response?.data || null
    await loadBillingContext()
  } catch (error) {
    comparisonResult.value = null
    notify.apiError(error, 'Không so sánh được các ứng viên đã chọn.')
  } finally {
    comparingShortlist.value = false
  }
}

const clearComparison = () => {
  selectedCompareProfileIds.value = []
  comparisonResult.value = null
}

const scoreTone = (score) => {
  const value = Number(score || 0)
  if (value >= 80) return 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-300'
  if (value >= 65) return 'bg-blue-500/10 text-blue-600 dark:text-blue-300'
  if (value >= 50) return 'bg-amber-500/10 text-amber-600 dark:text-amber-300'
  return 'bg-rose-500/10 text-rose-600 dark:text-rose-300'
}

const confidenceTone = (level) => {
  if (level === 'high') return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300'
  if (level === 'medium') return 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300'
  return 'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-300'
}

const explanationGroups = (structured) => [
  { key: 'strengths', label: 'Điểm mạnh', items: structured?.strengths || [] },
  { key: 'weaknesses', label: 'Điểm yếu', items: structured?.weaknesses || [] },
  { key: 'risks', label: 'Rủi ro', items: structured?.risks || [] },
  { key: 'interview_questions', label: 'Câu hỏi phỏng vấn', items: structured?.interview_questions || [] },
].filter((group) => group.items.length)

const fetchProtectedFile = async (url) => {
  const token = getAuthToken()

  if (!token) {
    notify.warning('Vui lòng đăng nhập lại để xem file CV.')
    return null
  }

  const response = await fetch(encodeURI(url), {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: 'application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,*/*',
    },
  })

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`)
  }

  return response.blob()
}

const openShortlistCv = async (item) => {
  const profile = item?.ho_so

  if (!profile?.file_cv_url && !hasBuilderCv(profile)) {
    notify.info('Hồ sơ này chưa có file CV hoặc dữ liệu CV tạo trên hệ thống để xem.')
    return
  }

  if (!profile.file_cv_url && hasBuilderCv(profile)) {
    const opened = openCvPrintPreview({
      profile,
      owner: item?.candidate,
    })

    if (!opened) {
      notify.warning('Trình duyệt đang chặn cửa sổ xem CV. Hãy cho phép popup và thử lại.')
    }
    return
  }

  try {
    const blob = await fetchProtectedFile(profile.file_cv_url)
    if (!blob) return
    const objectUrl = URL.createObjectURL(blob)
    window.open(objectUrl, '_blank', 'noopener')
    setTimeout(() => URL.revokeObjectURL(objectUrl), 60_000)
  } catch (error) {
    notify.error('Không mở được file CV. Vui lòng thử lại.')
  }
}

const parseJob = async () => {
  if (!job.value) return
  if (!canMutateCurrentJob.value) {
    notify.warning(canManageJobs.value
      ? 'Bạn chỉ có thể parse JD cho tin tuyển dụng mình phụ trách.'
      : `Vai trò ${currentInternalRoleLabel.value} không thể parse JD cho tin tuyển dụng.`)
    return
  }

  parsingLoading.value = true
  try {
    await employerJobService.parseJob(job.value.id)
    notify.success('Đã gửi yêu cầu parse JD cho tin tuyển dụng.')
    await fetchJobDetail()
  } catch (error) {
    notify.apiError(error, 'Không thể parse JD cho tin tuyển dụng.')
  } finally {
    parsingLoading.value = false
  }
}

const toggleStatus = async () => {
  if (!job.value) return
  if (!canMutateCurrentJob.value) {
    notify.warning(canManageJobs.value
      ? 'Bạn chỉ có thể đổi trạng thái cho tin tuyển dụng mình phụ trách.'
      : `Vai trò ${currentInternalRoleLabel.value} không thể đổi trạng thái tin tuyển dụng.`)
    return
  }

  togglingStatus.value = true
  try {
    await employerJobService.toggleStatus(job.value.id)
    notify.success(`Đã chuyển trạng thái sang ${Number(job.value.trang_thai) === 1 ? 'tạm ngưng' : 'đang hoạt động'}.`)
    await fetchJobDetail()
  } catch (error) {
    notify.apiError(error, 'Không thể chuyển trạng thái tin tuyển dụng.')
  } finally {
    togglingStatus.value = false
  }
}

onMounted(async () => {
  await ensurePermissionsLoaded()
  await Promise.all([fetchJobDetail(), loadBillingContext()])
})
</script>

<template>
  <div class="mx-auto max-w-7xl">
    <div v-if="loading" class="grid grid-cols-1 gap-5 lg:grid-cols-4">
      <div v-for="index in 8" :key="index" class="h-36 animate-pulse rounded-2xl bg-slate-200/60 dark:bg-slate-800/70" />
    </div>

    <template v-else-if="job">
      <div class="mb-8 rounded-3xl border border-slate-800 bg-gradient-to-r from-slate-900 via-slate-900 to-[#1e46a7] p-6 text-white shadow-[0_24px_70px_rgba(14,22,42,0.35)]">
        <div class="flex flex-col gap-6 xl:flex-row xl:items-start xl:justify-between">
          <div class="max-w-4xl">
            <div class="mb-3 flex flex-wrap items-center gap-3">
              <RouterLink to="/employer/jobs" class="inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1.5 text-xs font-bold text-white/90 transition hover:bg-white/15">
                <span class="material-symbols-outlined text-[16px]">arrow_back</span>
                Quay lại danh sách
              </RouterLink>
              <span class="inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-xs font-bold" :class="statusTone">
                <span class="h-2 w-2 rounded-full" :class="Number(job.trang_thai) === 1 ? 'bg-emerald-400' : 'bg-amber-400'" />
                {{ statusLabel }}
              </span>
              <span class="inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-xs font-bold" :class="parseStatusMeta.classes">
                {{ parseStatusMeta.label }}
              </span>
              <span
                v-if="job.is_featured"
                class="inline-flex items-center gap-2 rounded-full border border-amber-300/40 bg-amber-400/15 px-3 py-1.5 text-xs font-bold text-amber-100"
              >
                <span class="material-symbols-outlined text-[16px]">rocket_launch</span>
                Featured đến {{ formatDateTime(job.featured_until) }}
              </span>
            </div>

            <h1 class="text-3xl font-black tracking-tight sm:text-4xl">{{ job.tieu_de }}</h1>
            <p class="mt-3 text-sm leading-7 text-blue-100/80 sm:text-base">
              {{ job.mo_ta_cong_viec }}
            </p>

            <div class="mt-5 flex flex-wrap gap-3 text-sm text-blue-100/85">
              <span class="inline-flex items-center gap-2 rounded-2xl bg-white/8 px-4 py-2 backdrop-blur">
                <span class="material-symbols-outlined text-[18px]">pin_drop</span>
                {{ job.dia_diem_lam_viec || 'Chưa cập nhật địa điểm' }}
              </span>
              <span class="inline-flex items-center gap-2 rounded-2xl bg-white/8 px-4 py-2 backdrop-blur">
                <span class="material-symbols-outlined text-[18px]">work_history</span>
                {{ job.hinh_thuc_lam_viec || 'Chưa cập nhật hình thức' }}
              </span>
              <span class="inline-flex items-center gap-2 rounded-2xl bg-white/8 px-4 py-2 backdrop-blur">
                <span class="material-symbols-outlined text-[18px]">payments</span>
                {{ formatSalary(job) }}
              </span>
              <span class="inline-flex items-center gap-2 rounded-2xl bg-white/8 px-4 py-2 backdrop-blur">
                <span class="material-symbols-outlined text-[18px]">event</span>
                Hết hạn: {{ formatDateTime(job.ngay_het_han) }}
              </span>
              <span class="inline-flex items-center gap-2 rounded-2xl bg-white/8 px-4 py-2 backdrop-blur">
                <span class="material-symbols-outlined text-[18px]">badge</span>
                HR phụ trách: {{ job.hr_phu_trach?.ho_ten || 'Chưa gán' }}
              </span>
            </div>
            <p
              v-if="canManageJobs && !canManageAllAssignments && !isOwnedJob"
              class="mt-4 inline-flex rounded-full bg-amber-500/15 px-3 py-1.5 text-xs font-semibold text-amber-100"
            >
              Bạn đang xem tin không thuộc phần việc của mình. Các thao tác cập nhật đã bị khóa.
            </p>
          </div>

          <div class="flex flex-wrap gap-3 xl:justify-end">
            <button
              class="inline-flex items-center gap-2 rounded-2xl border border-white/15 bg-white/10 px-4 py-3 text-sm font-semibold text-white transition hover:bg-white/15 disabled:opacity-60"
              :disabled="shortlistLoading"
              type="button"
              @click="fetchShortlist"
            >
              <span class="material-symbols-outlined text-[18px]" :class="shortlistLoading ? 'animate-spin' : ''">
                {{ shortlistLoading ? 'progress_activity' : 'psychology' }}
              </span>
              {{ shortlistLoading ? 'Đang xếp hạng...' : 'Tải Shortlist' }}
            </button>
            <button
              class="inline-flex items-center gap-2 rounded-2xl border border-white/15 bg-white/10 px-4 py-3 text-sm font-semibold text-white transition hover:bg-white/15 disabled:opacity-60"
              :disabled="parsingLoading || !canMutateCurrentJob"
              type="button"
              @click="parseJob"
            >
              <span class="material-symbols-outlined text-[18px]" :class="parsingLoading ? 'animate-spin' : ''">
                {{ parsingLoading ? 'progress_activity' : 'auto_awesome' }}
              </span>
              {{ parsingLoading ? 'Đang parse...' : 'Parse JD' }}
            </button>
            <button
              class="inline-flex items-center gap-2 rounded-2xl bg-white px-4 py-3 text-sm font-bold text-[#1f49b6] shadow-lg shadow-black/10 transition hover:-translate-y-0.5 disabled:opacity-60"
              :disabled="togglingStatus || !canMutateCurrentJob"
              type="button"
              @click="toggleStatus"
            >
              <span class="material-symbols-outlined text-[18px]">
                {{ Number(job.trang_thai) === 1 ? 'pause_circle' : 'play_circle' }}
              </span>
              {{ Number(job.trang_thai) === 1 ? 'Tạm ngưng tin' : 'Kích hoạt lại tin' }}
            </button>
          </div>
        </div>
      </div>

      <div class="mb-6 rounded-3xl border border-amber-100 bg-white p-6 shadow-sm shadow-slate-950/5 dark:border-amber-500/20 dark:bg-slate-900">
        <div class="flex flex-col gap-5 xl:flex-row xl:items-start xl:justify-between">
          <div class="max-w-3xl">
            <p class="text-xs font-bold uppercase tracking-[0.28em] text-amber-500">Sponsored Job</p>
            <h2 class="mt-2 text-2xl font-black text-slate-900 dark:text-white">Featured listing cho tin tuyển dụng này</h2>
            <p class="mt-2 text-sm leading-7 text-slate-500 dark:text-slate-400">
              Đẩy job vào nhóm hiển thị nổi bật để tăng lượng click và CV. Gói sẽ cộng dồn thêm thời gian nếu tin đang chạy featured.
            </p>
          </div>

          <div class="rounded-2xl bg-amber-50 px-4 py-3 text-sm dark:bg-amber-500/10">
            <p class="font-bold text-slate-900 dark:text-white">{{ featuredStatusLabel }}</p>
            <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">
              {{ billingLoading ? 'Đang tải ví employer...' : `Ví khả dụng: ${formatCurrency(walletAvailable)}` }}
            </p>
          </div>
        </div>

        <div class="mt-5 grid gap-4 lg:grid-cols-2">
          <article
            v-for="item in featuredPackages"
            :key="item.featureCode"
            class="rounded-2xl border border-slate-200 bg-slate-50 p-5 dark:border-slate-800 dark:bg-slate-800/60"
          >
            <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <p class="text-lg font-black text-slate-900 dark:text-white">{{ item.label }}</p>
                <p class="mt-2 text-sm leading-6 text-slate-500 dark:text-slate-400">{{ item.description }}</p>
              </div>
              <div class="rounded-2xl bg-white px-4 py-3 text-right shadow-sm dark:bg-slate-900">
                <p class="text-xs font-bold uppercase tracking-[0.2em] text-slate-400">Giá</p>
                <p class="mt-1 text-2xl font-black text-slate-900 dark:text-white">{{ formatCurrency(item.price) }}</p>
              </div>
            </div>

            <button
              class="mt-5 inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-amber-500 px-4 py-3 text-sm font-bold text-white transition hover:bg-amber-600 disabled:opacity-60"
              :disabled="billingLoading || sponsorLoading === item.featureCode || !canMutateCurrentJob"
              type="button"
              @click="sponsorJob(item.featureCode)"
            >
              <span class="material-symbols-outlined text-[18px]" :class="sponsorLoading === item.featureCode ? 'animate-spin' : ''">
                {{ sponsorLoading === item.featureCode ? 'progress_activity' : 'rocket_launch' }}
              </span>
              {{ sponsorLoading === item.featureCode ? 'Đang kích hoạt...' : `Mua gói ${item.label}` }}
            </button>
          </article>

          <div
            v-if="!featuredPackages.length"
            class="rounded-2xl border border-dashed border-slate-200 px-5 py-8 text-sm text-slate-500 dark:border-slate-700 dark:text-slate-400"
          >
            Chưa có gói featured nào được cấu hình trong bảng giá AI.
          </div>
        </div>
      </div>

      <div class="mb-6 rounded-3xl border border-blue-100 bg-white p-6 shadow-sm shadow-slate-950/5 dark:border-blue-500/20 dark:bg-slate-900">
        <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <p class="text-xs font-bold uppercase tracking-[0.28em] text-[#2463eb]">AI Shortlist</p>
            <h2 class="mt-2 text-2xl font-black text-slate-900 dark:text-white">Ứng viên phù hợp nhất với JD này</h2>
            <p class="mt-2 max-w-3xl text-sm leading-7 text-slate-500 dark:text-slate-400">
              Hệ thống so khớp kỹ năng, kinh nghiệm, trình độ và ngành nghề. Mặc định chấm nhanh bằng rule-based, khi cần có thể chấm lại bằng AI để có giải thích sâu hơn.
            </p>
          </div>
          <div class="flex flex-col items-start gap-2 rounded-2xl bg-slate-50 px-4 py-3 text-sm dark:bg-slate-800 lg:items-end">
            <span class="font-bold text-slate-900 dark:text-white">
              {{ shortlistMeta?.total_candidates_scanned || 0 }} ứng viên đã quét
            </span>
            <span class="text-xs text-slate-500 dark:text-slate-400">
              {{ shortlistMeta?.total_profiles_scanned || 0 }} CV - {{ shortlistMeta?.scope_label || 'CV công khai' }}
            </span>
            <span v-if="shortlistMeta?.permission_scope" class="text-xs font-semibold text-slate-400">
              Quyền xem: {{ shortlistMeta.permission_scope === 'company' ? 'Toàn công ty' : 'Tin phụ trách' }}
            </span>
          </div>
        </div>

        <div class="mt-5 flex flex-col gap-3 rounded-2xl border border-slate-200 bg-slate-50 p-3 dark:border-slate-800 dark:bg-slate-800/50 lg:flex-row lg:items-center lg:justify-between">
          <div class="flex flex-wrap gap-2">
            <button
              class="rounded-xl px-4 py-2 text-sm font-bold transition"
              :class="shortlistScope === 'public' ? 'bg-[#2463eb] text-white' : 'bg-white text-slate-600 hover:bg-slate-100 dark:bg-slate-900 dark:text-slate-300'"
              type="button"
              @click="changeShortlistScope('public')"
            >
              CV công khai
            </button>
            <button
              class="rounded-xl px-4 py-2 text-sm font-bold transition"
              :class="shortlistScope === 'applied' ? 'bg-[#2463eb] text-white' : 'bg-white text-slate-600 hover:bg-slate-100 dark:bg-slate-900 dark:text-slate-300'"
              type="button"
              @click="changeShortlistScope('applied')"
            >
              Ứng viên đã ứng tuyển
            </button>
          </div>
          <div class="flex flex-col items-start gap-2 lg:items-end">
            <p class="text-xs text-slate-500 dark:text-slate-400">
              {{ billingLoading ? 'Đang tải bảng giá AI...' : `AI shortlist: ${formatFeaturePrice(shortlistAiFeature)} · AI compare: ${formatFeaturePrice(compareAiFeature)}` }}
            </p>
            <p class="text-xs text-slate-500 dark:text-slate-400">
              {{ billingLoading ? 'Đang tải số dư ví employer...' : `Ví khả dụng: ${formatCurrency(walletAvailable)}` }}
            </p>
            <button
              class="inline-flex h-10 items-center justify-center gap-2 rounded-xl bg-slate-900 px-4 text-sm font-bold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60 dark:bg-white dark:text-slate-900"
              :disabled="billingLoading || shortlistLoading || aiScoringLoading || !canRunPaidFeature(shortlistAiFeature)"
              type="button"
              @click="rescoreShortlistWithAi"
            >
              <span class="material-symbols-outlined text-[18px]" :class="aiScoringLoading ? 'animate-spin' : ''">
                {{ aiScoringLoading ? 'progress_activity' : 'auto_awesome' }}
              </span>
              {{ aiScoringLoading ? 'AI đang chấm...' : `Chấm lại bằng AI · ${formatFeaturePrice(shortlistAiFeature)}` }}
            </button>
          </div>
        </div>

        <div class="mt-3 flex flex-col gap-2 rounded-2xl border border-dashed border-slate-200 bg-white px-4 py-3 text-xs leading-6 text-slate-500 dark:border-slate-800 dark:bg-slate-900/60 dark:text-slate-400">
          <p>Shortlist mặc định là rule-based và không trừ ví. Chỉ các thao tác AI như chấm lại bằng AI hoặc compare bằng AI mới charge sau khi AI trả kết quả thành công.</p>
          <RouterLink
            v-if="(!canRunPaidFeature(shortlistAiFeature) || !canRunPaidFeature(compareAiFeature)) && !billingLoading"
            class="inline-flex items-center gap-2 font-bold text-[#2463eb] transition hover:text-[#1d4ed8]"
            to="/employer/billing"
          >
            <span class="material-symbols-outlined text-[16px]">account_balance_wallet</span>
            Nạp thêm ví employer để tiếp tục dùng AI
          </RouterLink>
        </div>

        <div v-if="shortlistLoading" class="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-3">
          <div v-for="index in 3" :key="index" class="h-48 animate-pulse rounded-2xl bg-slate-100 dark:bg-slate-800" />
        </div>

        <div v-else-if="topShortlistItems.length" class="mt-6">
          <div class="mb-4 flex flex-col gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 dark:border-slate-800 dark:bg-slate-800/50 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p class="text-sm font-bold text-slate-900 dark:text-white">
                Đã chọn {{ selectedCompareProfileIds.length }}/5 CV để so sánh
              </p>
              <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">
                Chọn 2 đến 5 CV trong shortlist để xem bảng so sánh theo kỹ năng, kinh nghiệm, chất lượng CV và minh chứng.
              </p>
            </div>
            <div class="flex flex-wrap gap-2">
              <button
                class="inline-flex h-10 items-center justify-center gap-2 rounded-xl bg-[#2463eb] px-4 text-sm font-bold text-white transition hover:bg-[#1d4ed8] disabled:cursor-not-allowed disabled:opacity-50"
                :disabled="billingLoading || !canCompareShortlist || comparingShortlist || !canRunPaidFeature(compareAiFeature)"
                type="button"
                @click="compareShortlistCandidates"
              >
                <span class="material-symbols-outlined text-[18px]" :class="comparingShortlist ? 'animate-spin' : ''">
                  {{ comparingShortlist ? 'progress_activity' : 'compare_arrows' }}
                </span>
                {{ comparingShortlist ? 'Đang so sánh...' : `So sánh ứng viên · ${formatFeaturePrice(compareAiFeature)}` }}
              </button>
              <button
                v-if="selectedCompareProfileIds.length || comparisonResult"
                class="inline-flex h-10 items-center justify-center rounded-xl border border-slate-200 px-4 text-sm font-bold text-slate-600 transition hover:bg-white dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-900"
                type="button"
                @click="clearComparison"
              >
                Bỏ chọn
              </button>
            </div>
          </div>

          <div class="grid grid-cols-1 gap-4 xl:grid-cols-5">
            <div
              v-for="item in topShortlistItems"
              :key="`${item.candidate?.id}-${item.ho_so?.id}`"
              class="flex flex-col rounded-2xl border bg-slate-50 p-4 transition dark:bg-slate-800/50"
              :class="isSelectedForCompare(item) ? 'border-[#2463eb] ring-2 ring-[#2463eb]/20 dark:border-[#8fb1ff]' : 'border-slate-200 dark:border-slate-800'"
            >
              <div class="flex items-start gap-3">
                <div class="size-12 shrink-0 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
                  <img
                    v-if="item.candidate?.avatar_url"
                    :src="item.candidate.avatar_url"
                    alt="avatar"
                    class="h-full w-full object-cover"
                  >
                  <div v-else class="flex h-full w-full items-center justify-center text-lg font-black text-slate-500">
                    {{ (item.candidate?.ho_ten || 'U').charAt(0).toUpperCase() }}
                  </div>
                </div>
                <div class="min-w-0 flex-1">
                  <h3 class="truncate text-base font-black text-slate-900 dark:text-white">
                    {{ item.candidate?.ho_ten || 'Ứng viên' }}
                  </h3>
                  <p class="mt-1 line-clamp-2 text-xs leading-5 text-slate-500 dark:text-slate-400">
                    {{ item.ho_so?.tieu_de_ho_so || 'Hồ sơ ứng viên' }}
                  </p>
                  <div class="mt-2 flex flex-wrap gap-1.5">
                    <span class="rounded-full bg-white px-2 py-1 text-[10px] font-bold text-slate-500 dark:bg-slate-900 dark:text-slate-300">
                      {{ item.source_insights?.label || 'CV' }}
                    </span>
                    <span
                      v-if="item.ai_explanation"
                      class="rounded-full bg-violet-100 px-2 py-1 text-[10px] font-bold text-violet-700 dark:bg-violet-900/30 dark:text-violet-300"
                    >
                      AI giải thích
                    </span>
                    <span
                      v-if="item.confidence?.label"
                      class="rounded-full px-2 py-1 text-[10px] font-bold"
                      :class="confidenceTone(item.confidence.level)"
                    >
                      {{ item.confidence.label }}
                    </span>
                  </div>
                </div>
              </div>

              <div class="mt-4 flex items-center justify-between gap-3">
                <span class="rounded-full px-3 py-1 text-xs font-black" :class="scoreTone(item.score)">
                  {{ Math.round(item.score || 0) }}%
                </span>
                <span class="text-right text-[11px] font-bold uppercase tracking-tight text-slate-400">
                  {{ item.recommendation }}
                </span>
              </div>

              <p class="mt-4 max-h-40 min-h-[100px] overflow-y-auto pr-1 text-xs leading-5 text-slate-600 dark:text-slate-300 whitespace-pre-line">
                {{ item.explanation }}
              </p>
              <p v-if="item.ai_error" class="mt-2 text-[11px] leading-5 text-amber-600 dark:text-amber-300">
                AI service chưa phản hồi, đang dùng điểm rule-based.
              </p>
              <div v-if="item.confidence?.warnings?.length" class="mt-2 rounded-xl bg-amber-50 p-2 text-[11px] leading-5 text-amber-700 dark:bg-amber-900/20 dark:text-amber-300">
                {{ item.confidence.warnings.slice(0, 2).join(' ') }}
              </div>

              <div class="mt-4 space-y-2">
                <div class="flex flex-wrap gap-1.5">
                  <span
                    v-for="skill in (item.matched_skills || []).slice(0, 3)"
                    :key="skill"
                    class="rounded-full bg-emerald-100 px-2 py-1 text-[10px] font-bold text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300"
                  >
                    {{ skill }}
                  </span>
                </div>
                <div v-if="item.missing_skills?.length" class="text-[11px] leading-5 text-slate-500 dark:text-slate-400">
                  Thiếu: {{ item.missing_skills.slice(0, 3).join(', ') }}
                </div>
              </div>

              <div class="mt-auto grid grid-cols-2 gap-2 pt-4">
                <button
                  class="inline-flex h-10 items-center justify-center gap-2 rounded-xl bg-white px-3 text-sm font-bold text-slate-700 shadow-sm transition hover:bg-slate-100 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-950"
                  type="button"
                  @click="openShortlistCv(item)"
                >
                  <span class="material-symbols-outlined text-[18px]">description</span>
                  Xem CV
                </button>
                <button
                  class="inline-flex h-10 items-center justify-center rounded-xl border px-3 text-sm font-bold transition"
                  :class="isSelectedForCompare(item)
                    ? 'border-[#2463eb] bg-[#2463eb] text-white'
                    : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200'"
                  type="button"
                  @click="toggleCompareSelection(item)"
                >
                  {{ isSelectedForCompare(item) ? 'Đã chọn' : 'So sánh' }}
                </button>
              </div>
            </div>
          </div>

          <div
            v-if="comparisonResult?.matrix?.rows?.length"
            class="mt-5 overflow-hidden rounded-2xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900"
          >
            <div class="border-b border-slate-200 px-5 py-4 dark:border-slate-800">
              <h3 class="text-lg font-black text-slate-900 dark:text-white">Bảng so sánh ứng viên</h3>
              <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
                So sánh dựa trên điểm hybrid, kỹ năng khớp/thiếu và vùng mạnh/yếu trong CV.
              </p>
            </div>
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-slate-200 text-sm dark:divide-slate-800">
                <thead class="bg-slate-50 text-left text-xs font-bold uppercase tracking-[0.18em] text-slate-500 dark:bg-slate-800/60">
                  <tr>
                    <th class="px-5 py-3">Ứng viên</th>
                    <th class="px-5 py-3">Điểm</th>
                    <th class="px-5 py-3">Nguồn CV</th>
                    <th class="px-5 py-3">Độ tin cậy</th>
                    <th class="px-5 py-3">Điểm mạnh nổi bật</th>
                    <th class="px-5 py-3">Điểm cần cải thiện</th>
                    <th class="px-5 py-3">Kỹ năng khớp</th>
                    <th class="px-5 py-3">Kỹ năng/yêu cầu còn thiếu</th>
                    <th class="px-5 py-3">Giải thích AI</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-100 dark:divide-slate-800">
                  <tr
                    v-for="row in comparisonResult.matrix.rows"
                    :key="row.ho_so_id"
                    class="align-top text-slate-700 dark:text-slate-300"
                  >
                    <td class="px-5 py-4 font-bold text-slate-900 dark:text-white">{{ row.candidate_name }}</td>
                    <td class="px-5 py-4">
                      <span class="rounded-full px-3 py-1 text-xs font-black" :class="scoreTone(row.score)">
                        {{ Math.round(row.score || 0) }}%
                      </span>
                    </td>
                    <td class="px-5 py-4">{{ row.source || 'CV' }}</td>
                    <td class="min-w-48 px-5 py-4">
                      <span
                        v-if="row.confidence?.label"
                        class="rounded-full px-3 py-1 text-xs font-black"
                        :class="confidenceTone(row.confidence.level)"
                      >
                        {{ row.confidence.label }}
                      </span>
                      <p v-if="row.confidence?.warnings?.length" class="mt-2 text-xs leading-5 text-slate-500 dark:text-slate-400">
                        {{ row.confidence.warnings.slice(0, 2).join(' ') }}
                      </p>
                    </td>
                    <td class="min-w-[260px] px-5 py-4 leading-7">{{ row.strongest_area }}</td>
                    <td class="min-w-[260px] px-5 py-4 leading-7">{{ row.weakest_area }}</td>
                    <td class="min-w-56 max-w-xs px-5 py-4">{{ (row.matched_skills || []).slice(0, 6).join(', ') || 'Chưa rõ' }}</td>
                    <td class="min-w-56 max-w-xs px-5 py-4">{{ (row.missing_skills || []).slice(0, 6).join(', ') || 'Không có' }}</td>
                    <td class="min-w-[360px] max-w-xl whitespace-pre-line px-5 py-4 leading-7">
                      {{ row.ai_explanation || row.explanation || 'Chưa có giải thích AI chi tiết.' }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div class="border-t border-slate-200 bg-slate-50 p-5 dark:border-slate-800 dark:bg-slate-800/40">
              <h4 class="text-sm font-black uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">
                Giải thích chi tiết
              </h4>
              <div class="mt-4 grid grid-cols-1 gap-3 lg:grid-cols-2">
                <div
                  v-for="row in comparisonResult.matrix.rows"
                  :key="`explanation-${row.ho_so_id}`"
                  class="rounded-2xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-900"
                >
                  <div class="flex items-center justify-between gap-3">
                    <p class="font-black text-slate-900 dark:text-white">{{ row.candidate_name }}</p>
                    <span class="rounded-full px-3 py-1 text-xs font-black" :class="scoreTone(row.score)">
                      {{ Math.round(row.score || 0) }}%
                    </span>
                  </div>
                  <p class="mt-3 whitespace-pre-line text-sm leading-7 text-slate-600 dark:text-slate-300">
                    {{ row.ai_explanation || row.explanation || 'Chưa có giải thích AI chi tiết.' }}
                  </p>
                  <div v-if="row.structured_explanation" class="mt-4 space-y-3">
                    <div
                      v-for="group in explanationGroups(row.structured_explanation)"
                      :key="`${row.ho_so_id}-${group.key}`"
                      class="rounded-xl bg-slate-50 p-3 dark:bg-slate-800"
                    >
                      <p class="text-xs font-black uppercase tracking-[0.16em] text-slate-500 dark:text-slate-400">{{ group.label }}</p>
                      <ul class="mt-2 space-y-1 text-sm leading-6 text-slate-600 dark:text-slate-300">
                        <li v-for="entry in group.items" :key="entry" class="flex gap-2">
                          <span class="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-[#2463eb]" />
                          <span>{{ entry }}</span>
                        </li>
                      </ul>
                    </div>
                    <p
                      v-if="row.structured_explanation.recommendation"
                      class="rounded-xl bg-blue-50 p-3 text-sm font-semibold leading-6 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300"
                    >
                      Khuyến nghị: {{ row.structured_explanation.recommendation }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="mt-6 rounded-2xl border border-dashed border-slate-200 px-5 py-8 text-center text-sm text-slate-500 dark:border-slate-700 dark:text-slate-400">
          Chưa có ứng viên phù hợp trong phạm vi {{ shortlistScope === 'applied' ? 'đã ứng tuyển' : 'CV công khai' }} để tạo shortlist cho tin này.
        </div>
      </div>

      <div class="mb-6 grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-4">
        <div
          v-for="card in statusCards"
          :key="card.label"
          class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm shadow-slate-950/5 dark:border-slate-800 dark:bg-slate-900"
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

      <div class="grid grid-cols-1 gap-6 xl:grid-cols-[minmax(0,1.45fr)_360px]">
        <div class="space-y-6">
          <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm shadow-slate-950/5 dark:border-slate-800 dark:bg-slate-900">
            <div class="flex items-center justify-between gap-4">
              <div>
                <h2 class="text-xl font-bold text-slate-900 dark:text-white">Tóm tắt JD</h2>
                <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Thông tin nhanh để bạn nhìn lại chất lượng tin tuyển dụng trước khi xử lý hồ sơ.</p>
              </div>
              <span
                class="inline-flex items-center rounded-full px-3 py-1 text-xs font-bold"
                :class="job.da_tuyen_du ? 'bg-rose-500/10 text-rose-300' : 'bg-emerald-500/10 text-emerald-300'"
              >
                {{ job.da_tuyen_du ? 'Đã đủ chỉ tiêu' : `${job.so_luong_con_lai || 0} vị trí còn lại` }}
              </span>
            </div>

            <div class="mt-5 grid grid-cols-1 gap-4 md:grid-cols-2">
              <div class="rounded-2xl bg-slate-50 p-5 dark:bg-slate-800/70">
                <p class="text-xs font-bold uppercase tracking-[0.22em] text-slate-400">Ngành nghề</p>
                <div class="mt-3 flex flex-wrap gap-2">
                  <span
                    v-for="industry in job.nganh_nghes || []"
                    :key="industry.id"
                    class="inline-flex items-center rounded-full bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 dark:bg-slate-900 dark:text-slate-200"
                  >
                    {{ industry.ten_nganh }}
                  </span>
                </div>
              </div>

              <div class="rounded-2xl bg-slate-50 p-5 dark:bg-slate-800/70">
                <p class="text-xs font-bold uppercase tracking-[0.22em] text-slate-400">Yêu cầu cơ bản</p>
                <div class="mt-3 space-y-3 text-sm text-slate-600 dark:text-slate-300">
                  <p><span class="font-semibold text-slate-900 dark:text-white">Cấp bậc:</span> {{ job.cap_bac || 'Chưa cập nhật' }}</p>
                  <p><span class="font-semibold text-slate-900 dark:text-white">Kinh nghiệm:</span> {{ job.kinh_nghiem_yeu_cau || 'Chưa cập nhật' }}</p>
                  <p><span class="font-semibold text-slate-900 dark:text-white">Số lượng tuyển:</span> {{ job.so_luong_tuyen || 0 }}</p>
                  <p><span class="font-semibold text-slate-900 dark:text-white">Hết hạn:</span> {{ formatDateTime(job.ngay_het_han) }}</p>
                </div>
              </div>
            </div>
          </div>

          <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm shadow-slate-950/5 dark:border-slate-800 dark:bg-slate-900">
            <div class="flex items-center justify-between gap-4">
              <div>
                <h2 class="text-xl font-bold text-slate-900 dark:text-white">Kỹ năng & yêu cầu đã parse</h2>
                <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Kết quả parse JD và các kỹ năng yêu cầu chuẩn hóa từ hệ thống.</p>
              </div>
              <span class="text-xs font-semibold uppercase tracking-[0.22em] text-slate-400">
                {{ requiredSkills.length }} kỹ năng
              </span>
            </div>

            <div class="mt-5">
              <p class="text-xs font-bold uppercase tracking-[0.22em] text-slate-400">Kỹ năng nổi bật</p>
              <div class="mt-3 flex flex-wrap gap-2">
                <span
                  v-for="skill in requiredSkills"
                  :key="skill"
                  class="inline-flex items-center rounded-full bg-[#2463eb]/10 px-3 py-1.5 text-xs font-semibold text-[#2463eb] dark:bg-[#2463eb]/15 dark:text-[#8fb1ff]"
                >
                  {{ skill }}
                </span>
                <span v-if="!requiredSkills.length" class="text-sm text-slate-500 dark:text-slate-400">Chưa có kỹ năng parse được cho JD này.</span>
              </div>
            </div>

            <div class="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
              <div class="rounded-2xl bg-slate-50 p-5 dark:bg-slate-800/70">
                <p class="text-xs font-bold uppercase tracking-[0.22em] text-slate-400">Yêu cầu trích xuất</p>
                <ul v-if="parsedRequirements.length" class="mt-3 space-y-2 text-sm leading-7 text-slate-600 dark:text-slate-300">
                  <li v-for="item in parsedRequirements" :key="item" class="flex gap-3">
                    <span class="mt-2 h-2 w-2 shrink-0 rounded-full bg-[#2463eb]" />
                    <span>{{ item }}</span>
                  </li>
                </ul>
                <p v-else class="mt-3 text-sm text-slate-500 dark:text-slate-400">Chưa có dữ liệu yêu cầu trích xuất.</p>
              </div>

              <div class="rounded-2xl bg-slate-50 p-5 dark:bg-slate-800/70">
                <p class="text-xs font-bold uppercase tracking-[0.22em] text-slate-400">Quyền lợi trích xuất</p>
                <ul v-if="parsedBenefits.length" class="mt-3 space-y-2 text-sm leading-7 text-slate-600 dark:text-slate-300">
                  <li v-for="item in parsedBenefits" :key="item" class="flex gap-3">
                    <span class="mt-2 h-2 w-2 shrink-0 rounded-full bg-emerald-400" />
                    <span>{{ item }}</span>
                  </li>
                </ul>
                <p v-else class="mt-3 text-sm text-slate-500 dark:text-slate-400">Chưa có dữ liệu quyền lợi trích xuất.</p>
              </div>
            </div>
          </div>

          <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm shadow-slate-950/5 dark:border-slate-800 dark:bg-slate-900">
            <div class="flex items-center justify-between gap-4">
              <div>
                <h2 class="text-xl font-bold text-slate-900 dark:text-white">Hồ sơ gần đây</h2>
                <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Các hồ sơ mới nộp vào tin này để bạn xử lý nhanh hơn.</p>
              </div>
              <RouterLink to="/employer/interviews" class="text-sm font-bold text-[#2463eb] hover:underline">
                Mở trang xử lý ứng tuyển
              </RouterLink>
            </div>

            <div v-if="upcomingApplications.length" class="mt-5 space-y-3">
              <div
                v-for="application in upcomingApplications"
                :key="application.id"
                class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4 dark:border-slate-800 dark:bg-slate-800/40"
              >
                <div class="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                  <div class="min-w-0 flex-1">
                    <p class="text-base font-bold text-slate-900 dark:text-white">
                      {{ application.ho_so?.tieu_de_ho_so || 'Hồ sơ ứng viên' }}
                    </p>
                    <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
                      {{ application.ho_so?.nguoi_dung?.email || 'Chưa có email' }}
                    </p>
                    <p class="mt-2 text-sm text-slate-600 dark:text-slate-300">
                      Nộp lúc {{ formatSubmittedDateTime(application.thoi_gian_ung_tuyen) }}
                    </p>
                  </div>
                  <span
                    class="inline-flex items-center rounded-full px-3 py-1 text-xs font-bold"
                    :class="applicationStatusMeta(application.trang_thai).classes"
                  >
                    {{ applicationStatusMeta(application.trang_thai).label }}
                  </span>
                </div>
              </div>
            </div>

            <div v-else class="mt-5 rounded-2xl border border-dashed border-slate-200 px-4 py-8 text-center text-sm text-slate-500 dark:border-slate-700 dark:text-slate-400">
              Chưa có hồ sơ nào nộp vào tin tuyển dụng này.
            </div>
          </div>
        </div>

        <div class="space-y-6">
          <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm shadow-slate-950/5 dark:border-slate-800 dark:bg-slate-900">
            <h2 class="text-xl font-bold text-slate-900 dark:text-white">Chỉ tiêu tuyển dụng</h2>
            <div class="mt-5 space-y-4">
              <div class="rounded-2xl bg-slate-50 px-4 py-4 dark:bg-slate-800/70">
                <p class="text-xs font-bold uppercase tracking-[0.22em] text-slate-400">Tổng cần tuyển</p>
                <p class="mt-2 text-3xl font-black text-slate-900 dark:text-white">{{ job.so_luong_tuyen || 0 }}</p>
              </div>
              <div class="grid grid-cols-2 gap-3">
                <div class="rounded-2xl bg-emerald-500/10 px-4 py-4">
                  <p class="text-xs font-bold uppercase tracking-[0.22em] text-emerald-300">Trúng tuyển</p>
                  <p class="mt-2 text-2xl font-black text-emerald-300">{{ job.so_luong_da_nhan || 0 }}</p>
                </div>
                <div class="rounded-2xl bg-blue-500/10 px-4 py-4">
                  <p class="text-xs font-bold uppercase tracking-[0.22em] text-[#2463eb] dark:text-[#8fb1ff]">Còn lại</p>
                  <p class="mt-2 text-2xl font-black text-[#2463eb] dark:text-[#8fb1ff]">{{ job.so_luong_con_lai || 0 }}</p>
                </div>
              </div>
            </div>
          </div>

          <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm shadow-slate-950/5 dark:border-slate-800 dark:bg-slate-900">
            <h2 class="text-xl font-bold text-slate-900 dark:text-white">Parse JD</h2>
            <div class="mt-5 space-y-4 text-sm text-slate-600 dark:text-slate-300">
              <p><span class="font-semibold text-slate-900 dark:text-white">Trạng thái:</span> {{ parseStatusMeta.label }}</p>
              <p><span class="font-semibold text-slate-900 dark:text-white">Model / phiên bản:</span> {{ job.parsing?.parser_version || 'Chưa có' }}</p>
              <p><span class="font-semibold text-slate-900 dark:text-white">Độ tin cậy:</span> {{ job.parsing?.confidence_score ? `${Math.round(job.parsing.confidence_score * 100)}%` : 'Chưa có' }}</p>
              <p><span class="font-semibold text-slate-900 dark:text-white">Cập nhật lần cuối:</span> {{ formatDateTime(job.parsing?.updated_at) }}</p>
              <p v-if="job.parsing?.error_message" class="rounded-2xl bg-rose-500/10 px-4 py-3 text-rose-300">
                {{ job.parsing.error_message }}
              </p>
            </div>
          </div>

          <div class="rounded-2xl border border-slate-200 bg-gradient-to-br from-[#2463eb] via-[#355dff] to-[#724dff] p-6 text-white shadow-[0_24px_60px_rgba(36,99,235,0.28)] dark:border-slate-800">
            <p class="text-xs font-semibold uppercase tracking-[0.24em] text-white/70">Gợi ý vận hành</p>
            <h3 class="mt-3 text-2xl font-black leading-tight">Giữ JD đủ rõ trước khi tăng tốc tuyển dụng</h3>
            <ul class="mt-5 space-y-3 text-sm leading-7 text-white/90">
              <li class="flex gap-3">
                <span class="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-white/90" />
                <span>JD đã parse tốt sẽ giúp matching, chatbot và cover letter sát hơn với nhu cầu tuyển dụng.</span>
              </li>
              <li class="flex gap-3">
                <span class="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-white/90" />
                <span>Hãy theo dõi chỉ tiêu còn lại để tránh chấp nhận vượt số lượng tuyển thực tế.</span>
              </li>
              <li class="flex gap-3">
                <span class="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-white/90" />
                <span>Khi hồ sơ bắt đầu tăng, nên chuyển sang trang phỏng vấn để hẹn lịch và gửi mail cho ứng viên ngay.</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
