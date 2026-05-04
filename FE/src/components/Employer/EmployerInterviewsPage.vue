<script setup>
import { computed, nextTick, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { employerApplicationService, employerBillingService, employerCandidateService, employerJobService } from '@/services/api'
import { useEmployerCompanyPermissions } from '@/composables/useEmployerCompanyPermissions'
import { useNotify } from '@/composables/useNotify'
import { getAuthToken } from '@/utils/authStorage'
import { connectPrivateChannel } from '@/services/realtime'
import { formatDateTimeVN, formatHistoricalDateTimeVN, toDateTimeLocalInputVN } from '@/utils/dateTime'
import {
  APPLICATION_STATUS,
  APPLICATION_STATUS_OPTIONS,
  OFFER_STATUS,
  getOfferStatusMeta,
  getApplicationStatusMeta,
  isFinalApplicationStatus as isFinalApplicationStatusValue,
} from '@/utils/applicationStatus'

const notify = useNotify()
const route = useRoute()
const router = useRouter()
const {
  company,
  canProcessApplications,
  currentInternalRoleLabel,
  assignableMembers,
  companyMembers,
  ensurePermissionsLoaded,
  currentEmployerId,
  canManageAllAssignments,
} = useEmployerCompanyPermissions()

const loading = ref(false)
const saving = ref(false)
const resendingEmailId = ref(null)
const sendingOfferId = ref(null)
const roundSaving = ref(false)
const roundDeletingId = ref(null)
const onboardingLoading = ref(false)
const onboardingSaving = ref(false)
const onboardingTaskSavingId = ref(null)
const exportingApplicationId = ref(null)
const copilotGenerating = ref(false)
const copilotEvaluating = ref(false)
const applications = ref([])
const applicationListRef = ref(null)
const jobs = ref([])
const pagination = ref(null)
const modalOpen = ref(false)
const modalBodyRef = ref(null)
const modalFocusSection = ref('')
const selectedApplication = ref(null)
const selectedRoundId = ref('')
const candidateDetailOpen = ref(false)
const candidateDetailLoading = ref(false)
const candidateDetail = ref(null)
const notificationTemplates = ref({})
const copilotSnapshot = ref(null)
const copilotScores = reactive({})
const billingLoading = ref(false)
const billingWallet = ref(null)
const billingPricing = ref([])
const billingEntitlements = ref([])
let applicationRealtimeChannel = null

const cleanDeepLinkQueryKeys = [
  'highlight_application_id',
  'focus_section',
  'interview_round_id',
  'onboarding_plan_id',
  'onboarding_task_id',
]

const filters = reactive({
  tin_tuyen_dung_id: '',
  trang_thai: '',
  hr_phu_trach_id: '',
  per_page: 10,
  page: 1,
})

const formatCurrency = (value) => `${Number(value || 0).toLocaleString('vi-VN')} đ`

const hrFilterOptions = computed(() => ([
  { id: '', label: 'Tất cả HR phụ trách' },
  { id: 'me', label: 'Tôi phụ trách' },
  ...assignableMembers.value,
]))

const interviewerOptions = computed(() => {
  const options = companyMembers.value.map((member) => ({
    value: String(member?.ho_ten || '').trim(),
    label: `${member?.ho_ten || 'HR'}${member?.ten_vai_tro_noi_bo ? ` (${member.ten_vai_tro_noi_bo})` : ''}`,
  })).filter((item) => item.value)

  const currentValue = String(form.nguoi_phong_van || '').trim()
  if (currentValue && !options.some((item) => item.value === currentValue)) {
    options.unshift({
      value: currentValue,
      label: `${currentValue} (dữ liệu cũ)`,
    })
  }

  return options
})

const form = reactive({
  trang_thai: 0,
  ngay_hen_phong_van: '',
  hinh_thuc_phong_van: '',
  nguoi_phong_van: '',
  link_phong_van: '',
  ket_qua_phong_van: '',
  hr_phu_trach_id: '',
  ghi_chu: '',
})

const roundForm = reactive({
  id: '',
  thu_tu: '',
  ten_vong: '',
  loai_vong: 'hr',
  trang_thai: 0,
  ngay_hen_phong_van: '',
  hinh_thuc_phong_van: '',
  nguoi_phong_van: '',
  interviewer_user_id: '',
  link_phong_van: '',
  ket_qua: '',
  diem_so: '',
  ghi_chu: '',
})

const offerForm = reactive({
  ghi_chu_offer: '',
  link_offer: '',
  han_phan_hoi_offer: '',
})

const onboardingForm = reactive({
  ngay_bat_dau: '',
  dia_diem_lam_viec: '',
  trang_thai: 'preparing',
  loi_chao_mung: '',
  ghi_chu_ung_vien: '',
  ghi_chu_noi_bo: '',
  tai_lieu_text: '',
})

const onboardingTaskForm = reactive({
  tieu_de: '',
  mo_ta: '',
  han_hoan_tat: '',
  nguoi_phu_trach: 'candidate',
})

const statusOptions = [
  { value: '', label: 'Tất cả trạng thái' },
  ...APPLICATION_STATUS_OPTIONS,
]

const activeTemplate = computed(() => notificationTemplates.value?.[Number(form.trang_thai)] || null)
const copilotPreInterview = computed(() => copilotSnapshot.value?.pre_interview || null)
const copilotPostInterview = computed(() => copilotSnapshot.value?.post_interview || null)
const selectedInterviewRounds = computed(() =>
  [...(selectedApplication.value?.interview_rounds || [])].sort((a, b) => Number(a.thu_tu || 0) - Number(b.thu_tu || 0))
)
const selectedRound = computed(() =>
  selectedInterviewRounds.value.find((round) => Number(round.id) === Number(selectedRoundId.value)) || null
)
const selectedOnboardingPlan = computed(() => selectedApplication.value?.onboarding_plan || null)
const canManageOnboarding = computed(() =>
  Number(selectedApplication.value?.trang_thai_offer || OFFER_STATUS.NOT_SENT) === OFFER_STATUS.ACCEPTED
)

const stats = computed(() => {
  const all = applications.value
  const pending = all.filter((item) => Number(item.trang_thai) === APPLICATION_STATUS.PENDING).length
  const reviewed = all.filter((item) => Number(item.trang_thai) === APPLICATION_STATUS.REVIEWED).length
  const scheduled = all.filter((item) => Number(item.trang_thai) === APPLICATION_STATUS.INTERVIEW_SCHEDULED).length
  const hired = all.filter((item) => Number(item.trang_thai) === APPLICATION_STATUS.HIRED).length

  return [
    {
      label: 'Hồ sơ đang chờ',
      value: pending,
      hint: 'Nên xử lý sớm để giữ trải nghiệm ứng viên tốt.',
      icon: 'hourglass_top',
      tone: 'text-amber-300 bg-amber-500/10',
    },
    {
      label: 'Đã xem',
      value: reviewed,
      hint: 'Các hồ sơ đã được mở và đánh giá sơ bộ.',
      icon: 'visibility',
      tone: 'text-sky-300 bg-sky-500/10',
    },
    {
      label: 'Lịch đã hẹn',
      value: scheduled,
      hint: 'Đơn đang ở giai đoạn phỏng vấn đã được lên lịch.',
      icon: 'calendar_month',
      tone: 'text-violet-300 bg-violet-500/10',
    },
    {
      label: 'Quá lịch cần cập nhật',
      value: overdueInterviews.value.length,
      hint: 'Lịch phỏng vấn đã qua nhưng chưa chốt trúng tuyển hoặc từ chối.',
      icon: 'notification_important',
      tone: 'text-rose-300 bg-rose-500/10',
    },
    {
      label: 'Trúng tuyển',
      value: hired,
      hint: 'Các hồ sơ đã có kết quả tuyển dụng cuối cùng.',
      icon: 'task_alt',
      tone: 'text-emerald-300 bg-emerald-500/10',
    },
  ]
})

const paginationSummary = computed(() => {
  if (!pagination.value) return 'Chưa có dữ liệu'
  return `Hiển thị ${pagination.value.from || 0}-${pagination.value.to || 0} trên ${pagination.value.total || 0} đơn ứng tuyển`
})

const upcomingInterviews = computed(() =>
  applications.value
    .filter((item) => item.ngay_hen_phong_van && !isInterviewResultOverdue(item))
    .sort((a, b) => new Date(a.ngay_hen_phong_van) - new Date(b.ngay_hen_phong_van))
    .slice(0, 5)
)

const statusMeta = getApplicationStatusMeta
const offerStatusMeta = getOfferStatusMeta

const interviewModeLabel = (value) => {
  const labels = {
    online: 'Online',
    offline: 'Trực tiếp',
    phone: 'Điện thoại',
  }

  return labels[value] || 'Chưa cập nhật'
}

const interviewAttendanceMeta = (value) => {
  const labels = {
    0: {
      label: 'Chờ xác nhận',
      classes: 'border border-violet-300/60 bg-violet-50 text-violet-700 dark:border-violet-400/20 dark:bg-violet-500/10 dark:text-violet-300',
    },
    1: {
      label: 'Đã xác nhận',
      classes: 'border border-emerald-300/60 bg-emerald-50 text-emerald-700 dark:border-emerald-400/20 dark:bg-emerald-500/10 dark:text-emerald-300',
    },
    2: {
      label: 'Không tham gia',
      classes: 'border border-rose-300/60 bg-rose-50 text-rose-700 dark:border-rose-400/20 dark:bg-rose-500/10 dark:text-rose-300',
    },
  }

  return labels[Number(value)] || {
    label: 'Chưa phản hồi',
    classes: 'border border-slate-200 bg-slate-50 text-slate-600 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300',
  }
}

const roundTypeLabel = (value) => ({
  hr: 'HR screening',
  technical: 'Technical',
  manager: 'Manager',
  final: 'Final',
  culture: 'Culture fit',
  other: 'Khác',
}[value] || value || 'HR screening')

const roundStatusMeta = (value) => {
  switch (Number(value)) {
    case 1:
      return { label: 'Hoàn thành', classes: 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-300' }
    case 2:
      return { label: 'Đã hủy', classes: 'bg-rose-500/10 text-rose-700 dark:text-rose-300' }
    default:
      return { label: 'Đã lên lịch', classes: 'bg-violet-500/10 text-violet-700 dark:text-violet-300' }
  }
}

const isUrl = (value) => /^https?:\/\//i.test(String(value || '').trim())

const degreeLabel = (value) => {
  const labels = {
    trung_hoc: 'Trung học',
    trung_cap: 'Trung cấp',
    cao_dang: 'Cao đẳng',
    dai_hoc: 'Đại học',
    thac_si: 'Thạc sĩ',
    tien_si: 'Tiến sĩ',
    khac: 'Khác',
  }

  return labels[value] || value || 'Chưa cập nhật'
}

const formatDateTime = (value) => {
  return formatDateTimeVN(value, 'Chưa lên lịch')
}

const formatSubmittedDateTime = (value) => {
  return formatHistoricalDateTimeVN(value, 'Chưa cập nhật')
}

const timelineDate = (item) =>
  formatDateTimeVN(item?.occurred_at || item?.scheduled_at || item?.due_at, 'Chưa cập nhật')

const timelineStatusClasses = (status) => ({
  completed: 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-500/20 dark:bg-emerald-500/10 dark:text-emerald-300',
  current: 'border-blue-200 bg-blue-50 text-blue-700 dark:border-blue-500/20 dark:bg-blue-500/10 dark:text-blue-300',
  pending: 'border-slate-200 bg-slate-50 text-slate-600 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300',
  cancelled: 'border-rose-200 bg-rose-50 text-rose-700 dark:border-rose-500/20 dark:bg-rose-500/10 dark:text-rose-300',
}[status] || 'border-slate-200 bg-slate-50 text-slate-600 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300')

const timelineStatusLabel = (status) => ({
  completed: 'Hoàn tất',
  current: 'Đang xử lý',
  pending: 'Sắp tới',
  cancelled: 'Đã dừng',
}[status] || 'Theo dõi')

const formatDateTimeInput = (value) => {
  return toDateTimeLocalInputVN(value)
}

const isFinalApplicationStatus = (application) => isFinalApplicationStatusValue(application?.trang_thai)

const canEmployerUpdateApplication = (application) => !application?.da_rut_don
const isOwnedApplication = (application) => {
  const ownedByApplication = Number(application?.hr_phu_trach?.id || application?.hr_phu_trach_id || 0) === Number(currentEmployerId.value || 0)
  const ownedByJob = Number(application?.tin_tuyen_dung?.hr_phu_trach?.id || application?.tin_tuyen_dung?.hr_phu_trach_id || 0) === Number(currentEmployerId.value || 0)
  return ownedByApplication || ownedByJob
}
const canMutateApplication = (application) => Boolean(
  canProcessApplications.value
  && !application?.da_rut_don
  && (canManageAllAssignments.value || isOwnedApplication(application)),
)
const canUseInterviewCopilotFor = (application) => Boolean(
  canMutateApplication(application)
  && !isFinalApplicationStatus(application),
)
const walletAvailable = computed(() => Number(billingWallet.value?.so_du_kha_dung || 0))
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
const copilotGenerateFeature = computed(() => resolveBillingFeature('interview_copilot_generate'))
const copilotEvaluateFeature = computed(() => resolveBillingFeature('interview_copilot_evaluate'))
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
const candidateName = (application) =>
  application?.ho_so?.nguoi_dung?.ho_ten
  || application?.ho_so?.tieu_de_ho_so
  || application?.ho_so?.nguoi_dung?.email
  || 'Ứng viên'

const isInterviewResultOverdue = (application) => {
  if (!application?.ngay_hen_phong_van || application?.da_rut_don || isFinalApplicationStatus(application)) {
    return false
  }

  return Number(application.trang_thai) >= APPLICATION_STATUS.INTERVIEW_SCHEDULED
    && new Date(application.ngay_hen_phong_van).getTime() < Date.now()
}
const ownershipHint = computed(() =>
  canProcessApplications.value && !canManageAllAssignments.value
    ? `Vai trò ${currentInternalRoleLabel.value} chỉ có thể xử lý các đơn ứng tuyển mình phụ trách.`
    : ''
)
const canUseSelectedInterviewCopilot = computed(() => canUseInterviewCopilotFor(selectedApplication.value))
const canGenerateSelectedInterviewCopilot = computed(() =>
  canUseSelectedInterviewCopilot.value && canRunPaidFeature(copilotGenerateFeature.value)
)
const canEvaluateSelectedInterviewCopilot = computed(() =>
  canUseSelectedInterviewCopilot.value && canRunPaidFeature(copilotEvaluateFeature.value)
)
const needsInterviewCopilotTopup = computed(() =>
  canUseSelectedInterviewCopilot.value
  && (!canRunPaidFeature(copilotGenerateFeature.value) || !canRunPaidFeature(copilotEvaluateFeature.value))
)
const selectedInterviewOverdue = computed(() => isInterviewResultOverdue(selectedApplication.value))
const overdueInterviews = computed(() =>
  applications.value
    .filter(isInterviewResultOverdue)
    .sort((a, b) => new Date(a.ngay_hen_phong_van) - new Date(b.ngay_hen_phong_van))
)

const canResendInterviewEmail = (application) =>
  Boolean(application?.id)
  && Boolean(application?.ngay_hen_phong_van)
  && !application?.da_rut_don
  && !isFinalApplicationStatus(application)

const canSendOffer = (application) =>
  Boolean(application?.id)
  && canMutateApplication(application)
  && !application?.da_rut_don
  && Number(application?.trang_thai) !== APPLICATION_STATUS.REJECTED
  && Number(application?.trang_thai_offer || OFFER_STATUS.NOT_SENT) !== OFFER_STATUS.ACCEPTED

const canExportDocument = (application, document) => {
  if (!application?.id) return false
  if (document === 'offer') return Number(application.trang_thai_offer || OFFER_STATUS.NOT_SENT) > OFFER_STATUS.NOT_SENT
  if (document === 'interview') return Boolean(
    application.ngay_hen_phong_van
    || application.interview_rounds?.length
    || application.ket_qua_phong_van
    || application.rubric_danh_gia_phong_van,
  )
  if (document === 'onboarding') return Boolean(application.onboarding_plan)
  return true
}

const triggerDownload = (blob, filename) => {
  const objectUrl = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = objectUrl
  link.download = filename || `application-export-${Date.now()}.pdf`
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.setTimeout(() => URL.revokeObjectURL(objectUrl), 30_000)
}

const statusOptionsForSelectedApplication = computed(() => {
  if (!selectedApplication.value) return statusOptions.slice(1)

  if (isFinalApplicationStatus(selectedApplication.value)) {
    return statusOptions
      .slice(1)
      .filter(status => Number(status.value) === Number(selectedApplication.value?.trang_thai))
  }

  return statusOptions.slice(1)
})

const fetchJobs = async () => {
  try {
    const response = await employerJobService.getJobs({ per_page: 100 })
    jobs.value = response?.data?.data || []
  } catch {
    jobs.value = []
  }
}

const fetchNotificationTemplates = async () => {
  try {
    const response = await employerApplicationService.getNotificationTemplates()
    notificationTemplates.value = response?.data || {}
  } catch {
    notificationTemplates.value = {}
  }
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

const fetchApplications = async () => {
  loading.value = true
  try {
    const response = await employerApplicationService.getApplications(filters)
    const payload = response?.data || {}
    applications.value = payload.data || []
    pagination.value = payload
  } catch (error) {
    applications.value = []
    pagination.value = null
    notify.apiError(error, 'Không tải được danh sách ứng tuyển.')
  } finally {
    loading.value = false
  }
}

const refreshApplicationsRealtime = async () => {
  if (loading.value) return
  await fetchApplications()
}

const handleApplicationHighlight = async () => {
  const applicationId = typeof route.query.highlight_application_id === 'string'
    ? route.query.highlight_application_id
    : ''

  if (!applicationId) return

  await nextTick()
  const target = applicationListRef.value?.querySelector(`[data-application-id="${applicationId}"]`)
  const application = applications.value.find((item) => Number(item.id) === Number(applicationId))

  if (target) {
    target.scrollIntoView({ behavior: 'smooth', block: 'center' })
    target.classList.add('ring-2', 'ring-[#2463eb]', 'ring-offset-2', 'ring-offset-white', 'dark:ring-offset-slate-950')

    window.setTimeout(() => {
      target.classList.remove('ring-2', 'ring-[#2463eb]', 'ring-offset-2', 'ring-offset-white', 'dark:ring-offset-slate-950')
    }, 2600)
  } else {
    notify.info('Đơn ứng tuyển cần xem không nằm trong trang hiện tại. Bạn có thể đổi bộ lọc hoặc tìm theo tin tuyển dụng.')
  }

  if (application && route.query.focus_section) {
    if (route.query.interview_round_id) {
      const round = (application.interview_rounds || []).find((item) => Number(item.id) === Number(route.query.interview_round_id))
      if (round) selectRound(round)
    }
    openModal(application, {
      focusSection: route.query.focus_section,
      interviewRoundId: route.query.interview_round_id,
    })
    await nextTick()
    scrollModalToFocus()
  }

  const query = { ...route.query }
  cleanDeepLinkQueryKeys.forEach((key) => delete query[key])
  router.replace({ query })
}

const applyFilters = async () => {
  filters.page = 1
  await fetchApplications()
}

const resetFilters = async () => {
  filters.tin_tuyen_dung_id = ''
  filters.trang_thai = ''
  filters.hr_phu_trach_id = ''
  filters.per_page = 10
  filters.page = 1
  await fetchApplications()
}

const goToPage = async (page) => {
  if (!page || page === filters.page) return
  filters.page = page
  await fetchApplications()
}

const openModal = (application, options = {}) => {
  if (!canMutateApplication(application)) {
    notify.warning(canProcessApplications.value
      ? 'Bạn chỉ có thể xử lý các đơn ứng tuyển mình phụ trách.'
      : `Vai trò ${currentInternalRoleLabel.value} không thể cập nhật quy trình ứng tuyển.`)
    return
  }

  selectedApplication.value = application
  form.trang_thai = Number(application.trang_thai ?? 0)
  form.ngay_hen_phong_van = formatDateTimeInput(application.ngay_hen_phong_van)
  form.hinh_thuc_phong_van = application.hinh_thuc_phong_van || ''
  form.nguoi_phong_van = application.nguoi_phong_van || ''
  form.link_phong_van = application.link_phong_van || ''
  form.ket_qua_phong_van = application.ket_qua_phong_van || ''
  form.hr_phu_trach_id = application.hr_phu_trach?.id ? String(application.hr_phu_trach.id) : ''
  form.ghi_chu = application.ghi_chu || ''
  offerForm.ghi_chu_offer = application.ghi_chu_offer || ''
  offerForm.link_offer = application.link_offer || ''
  offerForm.han_phan_hoi_offer = formatDateTimeInput(application.han_phan_hoi_offer)
  copilotSnapshot.value = parseCopilotSnapshot(application.rubric_danh_gia_phong_van)
  resetCopilotScores(copilotPreInterview.value?.rubric || [])
  const requestedRound = options.interviewRoundId
    ? (application.interview_rounds || []).find((round) => Number(round.id) === Number(options.interviewRoundId))
    : null
  const latestRound = requestedRound || [...(application.interview_rounds || [])].sort((a, b) => Number(b.thu_tu || 0) - Number(a.thu_tu || 0))[0]
  if (latestRound) {
    selectRound(latestRound)
  } else {
    resetRoundForm()
    roundForm.thu_tu = 1
    roundForm.ten_vong = 'Vòng 1 - HR screening'
  }
  modalFocusSection.value = String(options.focusSection || '')
  modalOpen.value = true
  if (Number(application.trang_thai_offer || OFFER_STATUS.NOT_SENT) === OFFER_STATUS.ACCEPTED) {
    fetchOnboardingPlan()
  }
}

const scrollModalToFocus = () => {
  const section = modalFocusSection.value
  if (!section || !modalBodyRef.value) return
  const target = modalBodyRef.value.querySelector(`[data-modal-section="${section}"]`)
  if (!target) return
  target.scrollIntoView({ behavior: 'smooth', block: 'start' })
  target.classList.add('ring-2', 'ring-[#2463eb]', 'ring-offset-2', 'ring-offset-white', 'dark:ring-offset-slate-950')
  window.setTimeout(() => {
    target.classList.remove('ring-2', 'ring-[#2463eb]', 'ring-offset-2', 'ring-offset-white', 'dark:ring-offset-slate-950')
  }, 2800)
}

const scrollModalToSection = (section) => {
  modalFocusSection.value = section
  nextTick(() => scrollModalToFocus())
}

const openInterviewCopilotWorkspace = (application) => {
  openModal(application)
  if (!canUseInterviewCopilotFor(application) && isFinalApplicationStatus(application)) {
    notify.info('Đơn đã có kết quả cuối. Interview Copilot chỉ còn ở chế độ xem lại.')
  }
}

const closeModal = () => {
  modalOpen.value = false
  selectedApplication.value = null
  form.trang_thai = 0
  form.ngay_hen_phong_van = ''
  form.hinh_thuc_phong_van = ''
  form.nguoi_phong_van = ''
  form.link_phong_van = ''
  form.ket_qua_phong_van = ''
  form.hr_phu_trach_id = ''
  form.ghi_chu = ''
  offerForm.ghi_chu_offer = ''
  offerForm.link_offer = ''
  offerForm.han_phan_hoi_offer = ''
  modalFocusSection.value = ''
  resetOnboardingForm()
  copilotSnapshot.value = null
  resetCopilotScores([])
  resetRoundForm()
}

const resetOnboardingForm = () => {
  onboardingForm.ngay_bat_dau = ''
  onboardingForm.dia_diem_lam_viec = ''
  onboardingForm.trang_thai = 'preparing'
  onboardingForm.loi_chao_mung = ''
  onboardingForm.ghi_chu_ung_vien = ''
  onboardingForm.ghi_chu_noi_bo = ''
  onboardingForm.tai_lieu_text = ''
  onboardingTaskForm.tieu_de = ''
  onboardingTaskForm.mo_ta = ''
  onboardingTaskForm.han_hoan_tat = ''
  onboardingTaskForm.nguoi_phu_trach = 'candidate'
}

const fillOnboardingForm = (plan) => {
  onboardingForm.ngay_bat_dau = plan?.ngay_bat_dau || ''
  onboardingForm.dia_diem_lam_viec = plan?.dia_diem_lam_viec || ''
  onboardingForm.trang_thai = plan?.trang_thai || 'preparing'
  onboardingForm.loi_chao_mung = plan?.loi_chao_mung || ''
  onboardingForm.ghi_chu_ung_vien = plan?.ghi_chu_ung_vien || ''
  onboardingForm.ghi_chu_noi_bo = plan?.ghi_chu_noi_bo || ''
  onboardingForm.tai_lieu_text = (plan?.tai_lieu_can_chuan_bi || plan?.tai_lieu_can_chuan_bi_json || []).join('\n')
}

const setSelectedOnboardingPlan = (plan) => {
  if (!selectedApplication.value) return
  selectedApplication.value = {
    ...selectedApplication.value,
    onboarding_plan: plan,
  }
  applications.value = applications.value.map((item) =>
    Number(item.id) === Number(selectedApplication.value.id)
      ? { ...item, onboarding_plan: plan }
      : item
  )
  fillOnboardingForm(plan)
}

const resetRoundForm = () => {
  selectedRoundId.value = ''
  roundForm.id = ''
  roundForm.thu_tu = ''
  roundForm.ten_vong = ''
  roundForm.loai_vong = 'hr'
  roundForm.trang_thai = 0
  roundForm.ngay_hen_phong_van = ''
  roundForm.hinh_thuc_phong_van = ''
  roundForm.nguoi_phong_van = ''
  roundForm.interviewer_user_id = ''
  roundForm.link_phong_van = ''
  roundForm.ket_qua = ''
  roundForm.diem_so = ''
  roundForm.ghi_chu = ''
}

const selectRound = (round) => {
  selectedRoundId.value = String(round?.id || '')
  roundForm.id = round?.id || ''
  roundForm.thu_tu = round?.thu_tu || ''
  roundForm.ten_vong = round?.ten_vong || ''
  roundForm.loai_vong = round?.loai_vong || 'hr'
  roundForm.trang_thai = Number(round?.trang_thai || 0)
  roundForm.ngay_hen_phong_van = formatDateTimeInput(round?.ngay_hen_phong_van)
  roundForm.hinh_thuc_phong_van = round?.hinh_thuc_phong_van || ''
  roundForm.nguoi_phong_van = round?.nguoi_phong_van || ''
  roundForm.interviewer_user_id = round?.interviewer_user_id ? String(round.interviewer_user_id) : ''
  roundForm.link_phong_van = round?.link_phong_van || ''
  roundForm.ket_qua = round?.ket_qua || ''
  roundForm.diem_so = round?.diem_so ?? ''
  roundForm.ghi_chu = round?.ghi_chu || ''
  copilotSnapshot.value = parseCopilotSnapshot(round?.rubric_danh_gia_json)
  resetCopilotScores(copilotPreInterview.value?.rubric || [])
}

const parseCopilotSnapshot = (value) => {
  if (!value) return null
  if (typeof value === 'object') return value

  try {
    const parsed = JSON.parse(value)
    return parsed && typeof parsed === 'object' ? parsed : null
  } catch {
    return null
  }
}

const resetCopilotScores = (rubric = []) => {
  Object.keys(copilotScores).forEach((key) => delete copilotScores[key])
  rubric.forEach((item, index) => {
    const key = item.criterion || `criterion_${index}`
    copilotScores[key] = ''
  })
}

const syncCopilotFromResponse = (payload) => {
  copilotSnapshot.value = payload?.copilot || null
  if (payload?.interview_round?.id) {
    selectedRoundId.value = String(payload.interview_round.id)
    const updatedRound = payload.interview_round
    selectedApplication.value = {
      ...selectedApplication.value,
      interview_rounds: (selectedApplication.value?.interview_rounds || []).map((round) =>
        Number(round.id) === Number(updatedRound.id) ? updatedRound : round
      ),
    }
    selectRound(updatedRound)
  }
  if (payload?.ket_qua_phong_van !== undefined) form.ket_qua_phong_van = payload.ket_qua_phong_van || form.ket_qua_phong_van
  if (payload?.ghi_chu !== undefined) form.ghi_chu = payload.ghi_chu || form.ghi_chu
  resetCopilotScores(copilotPreInterview.value?.rubric || [])
}

const closeCandidateDetail = () => {
  candidateDetailOpen.value = false
  candidateDetailLoading.value = false
  candidateDetail.value = null
}

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

const openCv = async (candidate) => {
  const cvUrl = candidate?.file_cv_url
  if (!cvUrl) {
    notify.info('Ứng viên này chưa có file CV đính kèm.')
    return
  }

  try {
    const blob = await fetchProtectedFile(cvUrl)
    if (!blob) return

    const objectUrl = URL.createObjectURL(blob)
    window.open(objectUrl, '_blank', 'noopener')
    setTimeout(() => URL.revokeObjectURL(objectUrl), 60_000)
  } catch {
    notify.error('Không mở được file CV. Vui lòng thử lại.')
  }
}

const openCandidateDetail = async (application) => {
  const candidateId = application?.ho_so?.id
  if (!candidateId) {
    notify.info('Không tìm thấy hồ sơ chi tiết của ứng viên này.')
    return
  }

  candidateDetailOpen.value = true
  candidateDetailLoading.value = true
  candidateDetail.value = null

  try {
    const response = await employerCandidateService.getCandidateById(candidateId)
    candidateDetail.value = response?.data || null
  } catch (error) {
    notify.apiError(error, 'Không tải được chi tiết hồ sơ ứng viên.')
    closeCandidateDetail()
  } finally {
    candidateDetailLoading.value = false
  }
}

const saveApplication = async () => {
  if (!selectedApplication.value) return
  if (!canMutateApplication(selectedApplication.value)) {
    notify.warning(canProcessApplications.value
      ? 'Bạn chỉ có thể xử lý các đơn ứng tuyển mình phụ trách.'
      : `Vai trò ${currentInternalRoleLabel.value} không thể cập nhật trạng thái ứng tuyển.`)
    return
  }

  saving.value = true
  try {
    await employerApplicationService.updateStatus(selectedApplication.value.id, {
      trang_thai: Number(form.trang_thai),
      ngay_hen_phong_van: form.ngay_hen_phong_van || null,
      hinh_thuc_phong_van: form.hinh_thuc_phong_van || null,
      nguoi_phong_van: form.nguoi_phong_van || null,
      link_phong_van: form.link_phong_van || null,
      ket_qua_phong_van: form.ket_qua_phong_van || null,
      hr_phu_trach_id: form.hr_phu_trach_id ? Number(form.hr_phu_trach_id) : null,
      ghi_chu: form.ghi_chu || null,
    })

    notify.success('Đã cập nhật ứng tuyển và gửi email khi cần.')
    closeModal()
    await fetchApplications()
  } catch (error) {
    notify.apiError(error, 'Không cập nhật được trạng thái ứng tuyển.')
  } finally {
    saving.value = false
  }
}

const refreshSelectedApplicationRounds = async () => {
  if (!selectedApplication.value?.id) return
  try {
    const response = await employerApplicationService.getInterviewRounds(selectedApplication.value.id)
    selectedApplication.value = {
      ...selectedApplication.value,
      interview_rounds: response?.data || [],
    }
  } catch (error) {
    notify.apiError(error, 'Không tải lại được timeline phỏng vấn.')
  }
}

const saveInterviewRound = async () => {
  if (!selectedApplication.value?.id || !roundForm.ten_vong || roundSaving.value) return

  roundSaving.value = true
  const payload = {
    thu_tu: roundForm.thu_tu ? Number(roundForm.thu_tu) : null,
    ten_vong: roundForm.ten_vong,
    loai_vong: roundForm.loai_vong || 'hr',
    trang_thai: Number(roundForm.trang_thai || 0),
    ngay_hen_phong_van: roundForm.ngay_hen_phong_van || null,
    hinh_thuc_phong_van: roundForm.hinh_thuc_phong_van || null,
    nguoi_phong_van: roundForm.nguoi_phong_van || null,
    interviewer_user_id: roundForm.interviewer_user_id ? Number(roundForm.interviewer_user_id) : null,
    link_phong_van: roundForm.link_phong_van || null,
    ket_qua: roundForm.ket_qua || null,
    diem_so: roundForm.diem_so !== '' ? Number(roundForm.diem_so) : null,
    ghi_chu: roundForm.ghi_chu || null,
  }

  try {
    const response = roundForm.id
      ? await employerApplicationService.updateInterviewRound(selectedApplication.value.id, roundForm.id, payload)
      : await employerApplicationService.createInterviewRound(selectedApplication.value.id, payload)
    const savedRound = response?.data
    notify.success(response?.message || 'Đã lưu vòng phỏng vấn.')
    await refreshSelectedApplicationRounds()
    await fetchApplications()
    if (savedRound?.id) {
      const freshRound = (selectedApplication.value?.interview_rounds || []).find((round) => Number(round.id) === Number(savedRound.id)) || savedRound
      selectRound(freshRound)
    }
  } catch (error) {
    notify.apiError(error, 'Không lưu được vòng phỏng vấn.')
  } finally {
    roundSaving.value = false
  }
}

const deleteInterviewRound = async (round) => {
  if (!selectedApplication.value?.id || !round?.id || roundDeletingId.value) return

  roundDeletingId.value = round.id
  try {
    await employerApplicationService.deleteInterviewRound(selectedApplication.value.id, round.id)
    notify.success('Đã xóa vòng phỏng vấn.')
    await refreshSelectedApplicationRounds()
    await fetchApplications()
    resetRoundForm()
  } catch (error) {
    notify.apiError(error, 'Không xóa được vòng phỏng vấn.')
  } finally {
    roundDeletingId.value = null
  }
}

const generateInterviewCopilot = async () => {
  if (!selectedApplication.value) return
  if (!canUseInterviewCopilotFor(selectedApplication.value)) {
    notify.warning(isFinalApplicationStatus(selectedApplication.value)
      ? 'Đơn đã có kết quả cuối nên không thể tạo lại Interview Copilot.'
      : 'Bạn không có quyền tạo Interview Copilot cho đơn ứng tuyển này.')
    return
  }
  if (!canRunPaidFeature(copilotGenerateFeature.value)) {
    notify.info('Ví employer không đủ để tạo Interview Copilot. Vui lòng nạp thêm ví trước khi tiếp tục.')
    return
  }

  copilotGenerating.value = true
  try {
    const response = await employerApplicationService.generateInterviewCopilot(selectedApplication.value.id, {
      interview_round_id: selectedRoundId.value ? Number(selectedRoundId.value) : undefined,
    })
    syncCopilotFromResponse(response?.data)
    notify.success(response?.message || 'Đã tạo Interview Copilot.')
    await Promise.all([fetchApplications(), loadBillingContext()])
  } catch (error) {
    notify.apiError(error, 'Không tạo được Interview Copilot.')
  } finally {
    copilotGenerating.value = false
  }
}

const evaluateInterviewCopilot = async () => {
  if (!selectedApplication.value) return
  if (!canUseInterviewCopilotFor(selectedApplication.value)) {
    notify.warning(isFinalApplicationStatus(selectedApplication.value)
      ? 'Đơn đã có kết quả cuối nên không thể đánh giá lại bằng Interview Copilot.'
      : 'Bạn không có quyền đánh giá Interview Copilot cho đơn ứng tuyển này.')
    return
  }
  if (!canRunPaidFeature(copilotEvaluateFeature.value)) {
    notify.info('Ví employer không đủ để đánh giá sau phỏng vấn. Vui lòng nạp thêm ví trước khi tiếp tục.')
    return
  }

  copilotEvaluating.value = true
  try {
    const response = await employerApplicationService.evaluateInterviewCopilot(selectedApplication.value.id, {
      notes: form.ghi_chu || '',
      decision: form.ket_qua_phong_van || '',
      scores: { ...copilotScores },
      interview_round_id: selectedRoundId.value ? Number(selectedRoundId.value) : undefined,
    })
    syncCopilotFromResponse(response?.data)
    notify.success(response?.message || 'Đã tạo đánh giá sau phỏng vấn.')
    await Promise.all([fetchApplications(), loadBillingContext()])
  } catch (error) {
    notify.apiError(error, 'Không tạo được đánh giá sau phỏng vấn.')
  } finally {
    copilotEvaluating.value = false
  }
}

const resendInterviewEmail = async (application) => {
  if (!canMutateApplication(application)) {
    notify.warning(canProcessApplications.value
      ? 'Bạn chỉ có thể gửi lại email cho các đơn ứng tuyển mình phụ trách.'
      : `Vai trò ${currentInternalRoleLabel.value} không thể gửi lại email lịch phỏng vấn.`)
    return
  }

  if (!canResendInterviewEmail(application)) {
    notify.info('Đơn này hiện không thể gửi lại email lịch phỏng vấn.')
    return
  }

  resendingEmailId.value = application.id
  try {
    await employerApplicationService.resendInterviewEmail(application.id)
    notify.success('Đã gửi lại email lịch phỏng vấn cho ứng viên.')
  } catch (error) {
    notify.apiError(error, 'Không gửi lại được email lịch phỏng vấn.')
  } finally {
    resendingEmailId.value = null
  }
}

const sendOffer = async () => {
  if (!selectedApplication.value || sendingOfferId.value) return

  if (!canSendOffer(selectedApplication.value)) {
    notify.warning('Đơn này hiện không thể gửi offer.')
    return
  }

  sendingOfferId.value = selectedApplication.value.id
  try {
    const response = await employerApplicationService.sendOffer(selectedApplication.value.id, {
      ghi_chu_offer: offerForm.ghi_chu_offer || null,
      link_offer: offerForm.link_offer || null,
      han_phan_hoi_offer: offerForm.han_phan_hoi_offer || null,
    })
    const updated = response?.data || null
    if (updated?.id) {
      selectedApplication.value = updated
      applications.value = applications.value.map((item) =>
        Number(item.id) === Number(updated.id) ? updated : item
      )
    }
    notify.success(response?.message || 'Đã gửi offer cho ứng viên.')
    await fetchApplications()
  } catch (error) {
    notify.apiError(error, 'Không gửi được offer cho ứng viên.')
  } finally {
    sendingOfferId.value = null
  }
}

const fetchOnboardingPlan = async () => {
  if (!selectedApplication.value?.id || !canManageOnboarding.value) return
  onboardingLoading.value = true
  try {
    const response = await employerApplicationService.getOnboarding(selectedApplication.value.id)
    if (response?.data) {
      setSelectedOnboardingPlan(response.data)
    }
  } catch (error) {
    notify.apiError(error, 'Không tải được onboarding cho ứng viên.')
  } finally {
    onboardingLoading.value = false
  }
}

const saveOnboardingPlan = async () => {
  if (!selectedApplication.value?.id || !canManageOnboarding.value || onboardingSaving.value) return
  onboardingSaving.value = true
  try {
    const response = await employerApplicationService.updateOnboarding(selectedApplication.value.id, {
      ngay_bat_dau: onboardingForm.ngay_bat_dau || null,
      dia_diem_lam_viec: onboardingForm.dia_diem_lam_viec || null,
      trang_thai: onboardingForm.trang_thai,
      loi_chao_mung: onboardingForm.loi_chao_mung || null,
      ghi_chu_ung_vien: onboardingForm.ghi_chu_ung_vien || null,
      ghi_chu_noi_bo: onboardingForm.ghi_chu_noi_bo || null,
      tai_lieu_can_chuan_bi: onboardingForm.tai_lieu_text
        .split('\n')
        .map((item) => item.trim())
        .filter(Boolean),
    })
    setSelectedOnboardingPlan(response?.data)
    notify.success(response?.message || 'Đã lưu onboarding.')
  } catch (error) {
    notify.apiError(error, 'Không lưu được onboarding.')
  } finally {
    onboardingSaving.value = false
  }
}

const createOnboardingTask = async () => {
  if (!selectedApplication.value?.id || !onboardingTaskForm.tieu_de || onboardingTaskSavingId.value) return
  onboardingTaskSavingId.value = 'new'
  try {
    const response = await employerApplicationService.createOnboardingTask(selectedApplication.value.id, {
      tieu_de: onboardingTaskForm.tieu_de,
      mo_ta: onboardingTaskForm.mo_ta || null,
      han_hoan_tat: onboardingTaskForm.han_hoan_tat || null,
      nguoi_phu_trach: onboardingTaskForm.nguoi_phu_trach,
    })
    setSelectedOnboardingPlan(response?.data)
    onboardingTaskForm.tieu_de = ''
    onboardingTaskForm.mo_ta = ''
    onboardingTaskForm.han_hoan_tat = ''
    onboardingTaskForm.nguoi_phu_trach = 'candidate'
    notify.success('Đã thêm checklist onboarding.')
  } catch (error) {
    notify.apiError(error, 'Không thêm được checklist onboarding.')
  } finally {
    onboardingTaskSavingId.value = null
  }
}

const updateOnboardingTaskStatus = async (task, status) => {
  if (!selectedApplication.value?.id || !task?.id || onboardingTaskSavingId.value) return
  onboardingTaskSavingId.value = task.id
  try {
    const response = await employerApplicationService.updateOnboardingTask(selectedApplication.value.id, task.id, {
      trang_thai: status,
    })
    setSelectedOnboardingPlan(response?.data)
  } catch (error) {
    notify.apiError(error, 'Không cập nhật được checklist.')
  } finally {
    onboardingTaskSavingId.value = null
  }
}

const deleteOnboardingTask = async (task) => {
  if (!selectedApplication.value?.id || !task?.id || onboardingTaskSavingId.value) return
  onboardingTaskSavingId.value = task.id
  try {
    const response = await employerApplicationService.deleteOnboardingTask(selectedApplication.value.id, task.id)
    setSelectedOnboardingPlan(response?.data)
    notify.info('Đã xóa checklist onboarding.')
  } catch (error) {
    notify.apiError(error, 'Không xóa được checklist.')
  } finally {
    onboardingTaskSavingId.value = null
  }
}

const downloadApplicationExport = async (application, document = 'full') => {
  if (!application?.id || exportingApplicationId.value) return
  exportingApplicationId.value = `${application.id}:${document}`
  try {
    const response = await employerApplicationService.downloadExport(application.id, document)
    triggerDownload(response.blob, response.filename)
    notify.success('Đã tạo file PDF từ server.')
  } catch (error) {
    notify.apiError(error, 'Không tải được file PDF.')
  } finally {
    exportingApplicationId.value = null
  }
}

onMounted(async () => {
  await Promise.all([ensurePermissionsLoaded(), fetchJobs(), fetchApplications(), fetchNotificationTemplates(), loadBillingContext()])
  await handleApplicationHighlight()

  const companyId = company.value?.id
  if (companyId) {
    applicationRealtimeChannel = connectPrivateChannel(`company.${companyId}`)
    applicationRealtimeChannel?.listen('.application.changed', (event) => {
      const title = event?.payload?.tin_tuyen_dung_tieu_de
      notify.info(title ? `Pipeline "${title}" vừa có cập nhật realtime.` : 'Pipeline ứng tuyển vừa có cập nhật realtime.')
      void refreshApplicationsRealtime()
    })
  }
})

onUnmounted(() => {
  if (applicationRealtimeChannel) {
    applicationRealtimeChannel.stopListening('.application.changed')
    applicationRealtimeChannel = null
  }
})

watch(() => form.hr_phu_trach_id, (value) => {
  if (!value || form.nguoi_phong_van) return

  const selectedMember = companyMembers.value.find((member) => String(member?.id) === String(value))
  if (selectedMember?.ho_ten) {
    form.nguoi_phong_van = selectedMember.ho_ten
  }
})
</script>

<template>
  <div class="mx-auto max-w-7xl">
    <div class="mb-8 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
      <div>
        <h2 class="text-3xl font-black tracking-tight text-slate-900 dark:text-white">Phỏng vấn & xử lý ứng tuyển</h2>
        <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">
          Theo dõi các hồ sơ vừa nộp, lên lịch phỏng vấn và cập nhật kết quả xử lý trong một nơi duy nhất.
        </p>
      </div>
      <button
        class="inline-flex items-center justify-center gap-2 rounded-xl bg-[#2463eb] px-5 py-3 text-sm font-bold text-white shadow-lg shadow-[#2463eb]/20 transition hover:-translate-y-0.5"
        type="button"
        @click="fetchApplications"
      >
        <span class="material-symbols-outlined text-[18px]">refresh</span>
        Tải lại danh sách
      </button>
    </div>

    <div
      v-if="!canProcessApplications"
      class="mb-6 rounded-2xl border border-slate-200 bg-slate-50 px-5 py-4 text-sm text-slate-600 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300"
    >
      Bạn đang đăng nhập với vai trò <span class="font-bold">{{ currentInternalRoleLabel }}</span>. Màn này đang ở chế độ chỉ xem, các thao tác xử lý ứng tuyển và phỏng vấn đã bị khóa.
    </div>
    <div
      v-else-if="ownershipHint"
      class="mb-6 rounded-2xl border border-blue-200 bg-blue-50 px-5 py-4 text-sm text-blue-700 dark:border-blue-500/20 dark:bg-blue-500/10 dark:text-blue-200"
    >
      {{ ownershipHint }}
    </div>
    <div
      v-if="overdueInterviews.length"
      class="mb-6 rounded-2xl border border-rose-200 bg-rose-50 px-5 py-4 text-sm text-rose-700 dark:border-rose-500/20 dark:bg-rose-500/10 dark:text-rose-200"
    >
      Có <span class="font-black">{{ overdueInterviews.length }}</span> lịch phỏng vấn đã quá hạn nhưng chưa chốt kết quả cuối. Cần cập nhật sang trúng tuyển/từ chối hoặc ghi rõ bước xử lý tiếp theo để tránh tồn đọng pipeline.
    </div>

    <div class="mb-6 grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-5">
      <div
        v-for="card in stats"
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

    <div class="grid grid-cols-1 gap-6 xl:grid-cols-[minmax(0,1.55fr)_360px]">
      <div class="space-y-6">
        <div class="rounded-2xl border border-slate-200 bg-white shadow-sm shadow-slate-950/5 dark:border-slate-800 dark:bg-slate-900">
          <div class="grid grid-cols-1 items-center gap-3 border-b border-slate-200 p-4 dark:border-slate-800 md:grid-cols-2 lg:grid-cols-5">
            <select
              v-model="filters.tin_tuyen_dung_id"
              class="h-14 w-full min-w-0 rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm text-slate-900 outline-none transition focus:border-[#2463eb] dark:border-slate-800 dark:bg-slate-800/70 dark:text-white md:col-span-2 lg:col-span-1"
              @change="applyFilters"
            >
              <option value="">Tất cả tin tuyển dụng</option>
              <option v-for="job in jobs" :key="job.id" :value="job.id">
                {{ job.tieu_de }}
              </option>
            </select>

            <select
              v-model="filters.trang_thai"
              class="h-14 w-full min-w-0 rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm text-slate-900 outline-none transition focus:border-[#2463eb] dark:border-slate-800 dark:bg-slate-800/70 dark:text-white"
              @change="applyFilters"
            >
              <option v-for="status in statusOptions" :key="String(status.value)" :value="status.value">
                {{ status.label }}
              </option>
            </select>

            <select
              v-model="filters.hr_phu_trach_id"
              class="h-14 w-full min-w-0 rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm text-slate-900 outline-none transition focus:border-[#2463eb] dark:border-slate-800 dark:bg-slate-800/70 dark:text-white"
              @change="applyFilters"
            >
              <option v-for="option in hrFilterOptions" :key="option.id || 'all-hr'" :value="option.id">
                {{ option.label }}
              </option>
            </select>

            <select
              v-model="filters.per_page"
              class="h-14 w-full min-w-0 rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm text-slate-900 outline-none transition focus:border-[#2463eb] dark:border-slate-800 dark:bg-slate-800/70 dark:text-white"
              @change="applyFilters"
            >
              <option :value="10">10 / trang</option>
              <option :value="20">20 / trang</option>
              <option :value="30">30 / trang</option>
            </select>

            <button
              class="flex h-14 w-full min-w-0 items-center justify-center rounded-xl border border-slate-200 px-3 text-sm font-bold text-slate-600 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
              type="button"
              @click="resetFilters"
            >
              Reset
            </button>
          </div>

          <div class="flex items-center justify-between px-5 py-3 text-xs text-slate-500 dark:text-slate-400">
            <span>{{ paginationSummary }}</span>
            <span>{{ jobs.length }} tin tuyển dụng khả dụng để lọc</span>
          </div>
        </div>

        <div v-if="loading" class="grid grid-cols-1 gap-4">
          <div v-for="index in 4" :key="index" class="h-40 animate-pulse rounded-2xl bg-slate-100 dark:bg-slate-800" />
        </div>

        <div
          v-else-if="!applications.length"
          class="rounded-2xl border border-slate-200 bg-white px-6 py-12 text-center shadow-sm shadow-slate-950/5 dark:border-slate-800 dark:bg-slate-900"
        >
          <span class="material-symbols-outlined text-[42px] text-slate-400">calendar_add_on</span>
          <h3 class="mt-4 text-lg font-bold text-slate-900 dark:text-white">Chưa có ứng tuyển nào</h3>
          <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">
            Khi ứng viên nộp hồ sơ vào tin tuyển dụng của công ty, bạn sẽ thấy danh sách xử lý tại đây.
          </p>
        </div>

        <div ref="applicationListRef" v-else class="space-y-4">
          <div
            v-for="application in applications"
            :key="application.id"
            :data-application-id="application.id"
            class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm shadow-slate-950/5 dark:border-slate-800 dark:bg-slate-900"
          >
            <div class="flex flex-col gap-4">
              <div class="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
                <div class="min-w-0 flex-1">
                  <div class="flex flex-wrap items-center gap-3">
                    <h3 class="text-xl font-bold text-slate-900 dark:text-white">
                      {{ application.tin_tuyen_dung?.tieu_de || 'Tin tuyển dụng' }}
                    </h3>
                    <span class="inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-bold" :class="statusMeta(application.trang_thai).classes">
                      <span class="h-2 w-2 rounded-full" :class="statusMeta(application.trang_thai).dot" />
                      {{ statusMeta(application.trang_thai).label }}
                    </span>
                    <span
                      v-if="Number(application.trang_thai_offer || 0) > OFFER_STATUS.NOT_SENT"
                      class="inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-bold"
                      :class="offerStatusMeta(application.trang_thai_offer).classes"
                    >
                      <span class="h-2 w-2 rounded-full" :class="offerStatusMeta(application.trang_thai_offer).dot" />
                      {{ offerStatusMeta(application.trang_thai_offer).label }}
                    </span>
                    <span
                      v-if="application.da_rut_don"
                      class="inline-flex items-center rounded-full border border-slate-300 bg-slate-100 px-3 py-1 text-xs font-bold text-slate-700 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
                    >
                      Đã rút đơn
                    </span>
                    <span
                      v-if="isInterviewResultOverdue(application)"
                      class="inline-flex items-center gap-1 rounded-full border border-rose-200 bg-rose-50 px-3 py-1 text-xs font-bold text-rose-700 dark:border-rose-500/20 dark:bg-rose-500/10 dark:text-rose-300"
                    >
                      <span class="material-symbols-outlined text-[14px]">notification_important</span>
                      Quá lịch cần cập nhật
                    </span>
                  </div>

                  <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">
                    {{ candidateName(application) }}
                  </p>
                </div>

                <div class="flex items-center gap-3 xl:justify-end">
                  <button
                    v-if="canResendInterviewEmail(application)"
                    class="inline-flex h-11 items-center justify-center gap-2 rounded-xl border border-emerald-200 bg-emerald-50 px-4 text-sm font-bold text-emerald-700 transition hover:bg-emerald-100 dark:border-emerald-500/20 dark:bg-emerald-500/10 dark:text-emerald-300 dark:hover:bg-emerald-500/15"
                    :disabled="resendingEmailId === application.id || !canMutateApplication(application)"
                    type="button"
                    @click="resendInterviewEmail(application)"
                  >
                    <span
                      class="material-symbols-outlined text-[18px]"
                      :class="resendingEmailId === application.id ? 'animate-spin' : ''"
                    >
                      {{ resendingEmailId === application.id ? 'progress_activity' : 'forward_to_inbox' }}
                    </span>
                    {{ resendingEmailId === application.id ? 'Đang gửi...' : 'Gửi lại email' }}
                  </button>
                  <button
                    v-if="application.ngay_hen_phong_van || application.rubric_danh_gia_phong_van"
                    class="inline-flex h-11 items-center justify-center gap-2 rounded-xl border border-violet-200 bg-violet-50 px-4 text-sm font-bold text-violet-700 transition hover:bg-violet-100 disabled:cursor-not-allowed disabled:opacity-60 dark:border-violet-500/20 dark:bg-violet-500/10 dark:text-violet-300 dark:hover:bg-violet-500/15"
                    :disabled="!canMutateApplication(application)"
                    type="button"
                    @click="openInterviewCopilotWorkspace(application)"
                  >
                    <span class="material-symbols-outlined text-[18px]">auto_awesome</span>
                    Copilot
                  </button>
                  <button
                    class="inline-flex h-11 items-center justify-center gap-2 rounded-xl border border-slate-200 px-4 text-sm font-bold text-slate-600 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
                    type="button"
                    @click="openCandidateDetail(application)"
                  >
                    <span class="material-symbols-outlined text-[18px]">badge</span>
                    Xem hồ sơ
                  </button>
                  <button
                    class="inline-flex h-11 items-center justify-center gap-2 rounded-xl border border-blue-200 px-4 text-sm font-bold text-blue-700 transition hover:bg-blue-50 disabled:opacity-60 dark:border-blue-500/20 dark:text-blue-300 dark:hover:bg-blue-500/10"
                    :disabled="exportingApplicationId === `${application.id}:full`"
                    type="button"
                    @click="downloadApplicationExport(application, 'full')"
                  >
                    <span class="material-symbols-outlined text-[18px]">picture_as_pdf</span>
                    {{ exportingApplicationId === `${application.id}:full` ? 'Đang tạo...' : 'PDF' }}
                  </button>
                  <button
                    class="inline-flex h-11 items-center justify-center gap-2 rounded-xl border px-4 text-sm font-bold transition disabled:cursor-not-allowed disabled:opacity-60"
                    :class="canMutateApplication(application)
                      ? 'border-slate-200 text-slate-600 hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800'
                      : 'border-slate-200 text-slate-400 dark:border-slate-800 dark:text-slate-500'"
                    :disabled="!canMutateApplication(application)"
                    type="button"
                    @click="openModal(application)"
                  >
                    <span class="material-symbols-outlined text-[18px]">edit_calendar</span>
                    Cập nhật
                  </button>
                </div>
              </div>

              <div class="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4">
                <div class="rounded-xl bg-slate-50 px-4 py-3 dark:bg-slate-800/70 min-h-[96px] h-full">
                  <p class="text-[10px] font-bold uppercase tracking-[0.22em] text-slate-400">Ứng viên</p>
                  <p class="mt-2 text-sm font-semibold leading-7 text-slate-900 dark:text-white">
                    {{ candidateName(application) }}
                  </p>
                </div>
                <div class="rounded-xl bg-slate-50 px-4 py-3 dark:bg-slate-800/70 min-h-[96px] h-full">
                  <p class="text-[10px] font-bold uppercase tracking-[0.22em] text-slate-400">Thời gian nộp</p>
                  <p class="mt-2 text-sm font-semibold leading-7 text-slate-900 dark:text-white">
                    {{ formatSubmittedDateTime(application.thoi_gian_ung_tuyen) }}
                  </p>
                </div>
                <div class="rounded-xl bg-slate-50 px-4 py-3 dark:bg-slate-800/70 min-h-[96px] h-full">
                  <p class="text-[10px] font-bold uppercase tracking-[0.22em] text-slate-400">Lịch phỏng vấn</p>
                  <p class="mt-2 text-sm font-semibold leading-7 text-slate-900 dark:text-white">
                    {{ formatDateTime(application.ngay_hen_phong_van) }}
                  </p>
                </div>
                <div class="rounded-xl bg-slate-50 px-4 py-3 dark:bg-slate-800/70 min-h-[96px] h-full">
                  <p class="text-[10px] font-bold uppercase tracking-[0.22em] text-slate-400">Hình thức</p>
                  <p class="mt-2 text-sm font-semibold leading-7 text-slate-900 dark:text-white">
                    {{ interviewModeLabel(application.hinh_thuc_phong_van) }}
                  </p>
                </div>
              </div>

              <div v-if="application.nguoi_phong_van" class="rounded-xl bg-slate-50 px-4 py-3 text-sm text-slate-600 dark:bg-slate-800/70 dark:text-slate-300">
                <span class="font-semibold text-slate-900 dark:text-white">Người phỏng vấn:</span>
                <span class="ml-2 break-words">{{ application.nguoi_phong_van }}</span>
              </div>

              <div
                v-if="application.application_timeline?.length"
                :data-application-section="`${application.id}:timeline`"
                class="rounded-xl border border-slate-200 bg-white px-4 py-4 dark:border-slate-800 dark:bg-slate-950/40"
              >
                <div class="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <p class="text-sm font-bold text-slate-900 dark:text-white">Timeline ứng tuyển tổng hợp</p>
                    <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">
                      Theo dõi toàn bộ luồng từ nộp hồ sơ đến onboarding.
                    </p>
                  </div>
                  <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-500 dark:bg-slate-800 dark:text-slate-300">
                    {{ application.application_timeline.length }} mốc
                  </span>
                </div>
                <div class="mt-4 grid gap-3 lg:grid-cols-2">
                  <article
                    v-for="item in application.application_timeline"
                    :key="item.key"
                    class="rounded-2xl border px-4 py-3"
                    :class="timelineStatusClasses(item.status)"
                  >
                    <div class="flex items-start gap-3">
                      <span class="material-symbols-outlined mt-0.5 text-[20px]">{{ item.icon || 'radio_button_checked' }}</span>
                      <div class="min-w-0 flex-1">
                        <div class="flex flex-wrap items-center gap-2">
                          <p class="font-bold">{{ item.title }}</p>
                          <span class="rounded-full bg-white/70 px-2 py-0.5 text-[10px] font-black uppercase tracking-wide dark:bg-slate-950/40">
                            {{ timelineStatusLabel(item.status) }}
                          </span>
                        </div>
                        <p class="mt-1 text-xs opacity-80">{{ timelineDate(item) }}</p>
                        <p v-if="item.description" class="mt-2 text-sm leading-6">{{ item.description }}</p>
                        <p v-if="item.due_at" class="mt-1 text-xs font-semibold">Hạn: {{ formatDateTime(item.due_at) }}</p>
                      </div>
                    </div>
                  </article>
                </div>
              </div>

              <div class="rounded-xl bg-slate-50 px-4 py-3 text-sm text-slate-600 dark:bg-slate-800/70 dark:text-slate-300">
                <span class="font-semibold text-slate-900 dark:text-white">HR phụ trách:</span>
                <span class="ml-2 break-words">{{ application.hr_phu_trach?.ho_ten || application.tin_tuyen_dung?.hr_phu_trach?.ho_ten || 'Chưa gán' }}</span>
                <span
                  v-if="canProcessApplications && !canManageAllAssignments && !isOwnedApplication(application)"
                  class="ml-2 inline-flex rounded-full bg-amber-500/10 px-2.5 py-1 text-[11px] font-semibold text-amber-300"
                >
                  Không thuộc phần việc của bạn
                </span>
              </div>

              <div
                v-if="application.ngay_hen_phong_van"
                class="rounded-xl bg-slate-50 px-4 py-3 text-sm text-slate-600 dark:bg-slate-800/70 dark:text-slate-300"
              >
                <span class="font-semibold text-slate-900 dark:text-white">Phản hồi ứng viên:</span>
                <span
                  class="ml-2 inline-flex items-center rounded-full px-2.5 py-1 text-xs font-bold"
                  :class="interviewAttendanceMeta(application.trang_thai_tham_gia_phong_van).classes"
                >
                  {{ interviewAttendanceMeta(application.trang_thai_tham_gia_phong_van).label }}
                </span>
                <span
                  v-if="application.thoi_gian_phan_hoi_phong_van"
                  class="ml-2 text-xs text-slate-500 dark:text-slate-400"
                >
                  • {{ formatDateTime(application.thoi_gian_phan_hoi_phong_van) }}
                </span>
              </div>

              <div
                v-if="application.interview_rounds?.length"
                :data-application-section="`${application.id}:interview`"
                class="rounded-xl bg-violet-50 px-4 py-3 text-sm text-violet-800 dark:bg-violet-500/10 dark:text-violet-200"
              >
                <span class="font-semibold">Timeline phỏng vấn:</span>
                <span class="ml-2">
                  {{ application.interview_rounds.length }} vòng
                  <span v-if="application.interview_rounds[application.interview_rounds.length - 1]?.ten_vong">
                    • mới nhất: {{ application.interview_rounds[application.interview_rounds.length - 1].ten_vong }}
                  </span>
                </span>
                <button
                  v-if="canExportDocument(application, 'interview')"
                  class="ml-3 text-xs font-bold text-violet-700 underline underline-offset-4 disabled:opacity-60 dark:text-violet-300"
                  :disabled="exportingApplicationId === `${application.id}:interview`"
                  type="button"
                  @click="downloadApplicationExport(application, 'interview')"
                >
                  {{ exportingApplicationId === `${application.id}:interview` ? 'Đang tạo PDF...' : 'PDF phỏng vấn' }}
                </button>
              </div>

              <div v-if="application.link_phong_van" class="rounded-xl bg-slate-50 px-4 py-3 text-sm text-slate-600 dark:bg-slate-800/70 dark:text-slate-300">
                <span class="font-semibold text-slate-900 dark:text-white">Link / địa điểm:</span>
                <a
                  v-if="isUrl(application.link_phong_van)"
                  :href="application.link_phong_van"
                  class="ml-2 break-all text-[#2463eb] hover:underline"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {{ application.link_phong_van }}
                </a>
                <span v-else class="ml-2 break-words">{{ application.link_phong_van }}</span>
              </div>

              <div v-if="application.ket_qua_phong_van" class="rounded-xl bg-slate-50 px-4 py-3 text-sm text-slate-600 dark:bg-slate-800/70 dark:text-slate-300">
                <span class="font-semibold text-slate-900 dark:text-white">Kết quả phỏng vấn:</span>
                <span class="ml-2">{{ application.ket_qua_phong_van }}</span>
              </div>

              <div
                v-if="Number(application.trang_thai_offer || 0) > OFFER_STATUS.NOT_SENT"
                :data-application-section="`${application.id}:offer`"
                class="rounded-xl border border-emerald-100 bg-emerald-50 px-4 py-3 text-sm text-emerald-800 dark:border-emerald-500/20 dark:bg-emerald-500/10 dark:text-emerald-200"
              >
                <div class="flex flex-wrap items-center gap-2">
                  <span class="font-semibold">Offer:</span>
                  <span
                    class="inline-flex items-center rounded-full px-2.5 py-1 text-xs font-bold"
                    :class="offerStatusMeta(application.trang_thai_offer).classes"
                  >
                    {{ offerStatusMeta(application.trang_thai_offer).label }}
                  </span>
                  <span v-if="application.thoi_gian_gui_offer" class="text-xs">
                    gửi lúc {{ formatDateTime(application.thoi_gian_gui_offer) }}
                  </span>
                  <span v-if="application.han_phan_hoi_offer" class="text-xs">
                    • hạn {{ formatDateTime(application.han_phan_hoi_offer) }}
                  </span>
                  <button
                    v-if="canExportDocument(application, 'offer')"
                    class="ml-2 text-xs font-bold text-emerald-700 underline underline-offset-4 disabled:opacity-60 dark:text-emerald-300"
                    :disabled="exportingApplicationId === `${application.id}:offer`"
                    type="button"
                    @click="downloadApplicationExport(application, 'offer')"
                  >
                    {{ exportingApplicationId === `${application.id}:offer` ? 'Đang tạo PDF...' : 'PDF offer' }}
                  </button>
                </div>
                <p v-if="application.ghi_chu_offer" class="mt-2 leading-6">{{ application.ghi_chu_offer }}</p>
                <p v-if="application.ghi_chu_phan_hoi_offer" class="mt-2 text-xs leading-5">
                  Phản hồi ứng viên: {{ application.ghi_chu_phan_hoi_offer }}
                </p>
              </div>

              <p class="text-sm leading-7 text-slate-500 dark:text-slate-400">
                {{ application.ghi_chu || 'Chưa có ghi chú xử lý cho hồ sơ này.' }}
              </p>
              <p
                v-if="application.da_rut_don && application.thoi_gian_rut_don"
                class="text-xs text-slate-400 dark:text-slate-500"
              >
                Ứng viên đã rút đơn lúc {{ formatDateTime(application.thoi_gian_rut_don) }}.
              </p>
            </div>
          </div>
        </div>

        <div class="flex items-center justify-between px-2">
          <p class="text-sm text-slate-500 dark:text-slate-400">{{ paginationSummary }}</p>
          <div class="flex gap-2">
            <button
              class="flex h-10 w-10 items-center justify-center rounded-xl border border-slate-200 text-slate-500 transition hover:bg-slate-50 disabled:opacity-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
              :disabled="!pagination?.prev_page_url"
              type="button"
              @click="goToPage((pagination?.current_page || 1) - 1)"
            >
              <span class="material-symbols-outlined text-[20px]">chevron_left</span>
            </button>
            <button class="flex h-10 min-w-10 items-center justify-center rounded-xl bg-[#2463eb] px-4 text-sm font-bold text-white">
              {{ pagination?.current_page || 1 }}
            </button>
            <button
              class="flex h-10 w-10 items-center justify-center rounded-xl border border-slate-200 text-slate-500 transition hover:bg-slate-50 disabled:opacity-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
              :disabled="!pagination?.next_page_url"
              type="button"
              @click="goToPage((pagination?.current_page || 1) + 1)"
            >
              <span class="material-symbols-outlined text-[20px]">chevron_right</span>
            </button>
          </div>
        </div>
      </div>

      <div class="space-y-6">
        <div
          v-if="overdueInterviews.length"
          class="rounded-2xl border border-rose-200 bg-white p-6 shadow-sm shadow-rose-950/5 dark:border-rose-500/20 dark:bg-slate-900"
        >
          <h3 class="text-xl font-bold text-slate-900 dark:text-white">Cần cập nhật kết quả</h3>
          <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Các lịch đã qua nhưng chưa được chốt kết quả cuối.</p>

          <div class="mt-5 space-y-4">
            <div
              v-for="application in overdueInterviews.slice(0, 5)"
              :key="`overdue-${application.id}`"
              class="rounded-xl border border-rose-100 bg-rose-50 px-4 py-4 dark:border-rose-500/20 dark:bg-rose-500/10"
            >
              <div class="flex items-start justify-between gap-3">
                <div>
                  <p class="font-semibold text-slate-900 dark:text-white">{{ application.tin_tuyen_dung?.tieu_de || 'Tin tuyển dụng' }}</p>
                  <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">{{ candidateName(application) }}</p>
                </div>
                <span class="material-symbols-outlined rounded-xl bg-rose-500/10 p-2 text-[18px] text-rose-600 dark:text-rose-300">priority_high</span>
              </div>
              <p class="mt-3 text-sm font-semibold text-rose-700 dark:text-rose-200">{{ formatDateTime(application.ngay_hen_phong_van) }}</p>
              <button
                class="mt-3 inline-flex h-9 items-center justify-center rounded-xl bg-rose-600 px-3 text-xs font-bold text-white transition hover:bg-rose-700 disabled:opacity-60"
                :disabled="!canMutateApplication(application)"
                type="button"
                @click="openModal(application)"
              >
                Cập nhật kết quả
              </button>
            </div>
          </div>
        </div>

        <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm shadow-slate-950/5 dark:border-slate-800 dark:bg-slate-900">
          <h3 class="text-xl font-bold text-slate-900 dark:text-white">Lịch phỏng vấn sắp tới</h3>
          <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Những hồ sơ đã có lịch hẹn để bạn chủ động chuẩn bị.</p>

          <div v-if="upcomingInterviews.length" class="mt-5 space-y-4">
            <div
              v-for="application in upcomingInterviews"
              :key="application.id"
              class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-4 dark:border-slate-800 dark:bg-slate-950/40"
            >
              <div class="flex items-start justify-between gap-3">
                <div>
                  <p class="font-semibold text-slate-900 dark:text-white">{{ application.tin_tuyen_dung?.tieu_de || 'Tin tuyển dụng' }}</p>
                  <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">{{ candidateName(application) }}</p>
                </div>
                <span class="material-symbols-outlined rounded-xl bg-[#2463eb]/10 p-2 text-[18px] text-[#7ea8ff]">event_available</span>
              </div>
              <p class="mt-3 text-sm font-semibold text-slate-900 dark:text-white">{{ formatDateTime(application.ngay_hen_phong_van) }}</p>
              <span
                class="mt-2 inline-flex rounded-full px-2.5 py-1 text-[11px] font-bold"
                :class="interviewAttendanceMeta(application.trang_thai_tham_gia_phong_van).classes"
              >
                {{ interviewAttendanceMeta(application.trang_thai_tham_gia_phong_van).label }}
              </span>
              <p v-if="application.nguoi_phong_van" class="mt-2 text-xs text-slate-500 dark:text-slate-400">
                Người phỏng vấn: {{ application.nguoi_phong_van }}
              </p>
            </div>
          </div>

          <div v-else class="mt-5 rounded-xl border border-dashed border-slate-200 px-4 py-8 text-center text-sm text-slate-500 dark:border-slate-700 dark:text-slate-400">
            Chưa có lịch hẹn phỏng vấn nào. Hãy cập nhật hồ sơ để thêm lịch khi cần.
          </div>
        </div>

        <div class="rounded-2xl border border-blue-200 bg-gradient-to-br from-blue-50 via-indigo-50 to-violet-100 p-6 text-slate-900 shadow-[0_24px_60px_rgba(36,99,235,0.16)] dark:border-slate-800 dark:bg-gradient-to-br dark:from-[#2463eb] dark:via-[#355dff] dark:to-[#724dff] dark:text-white dark:shadow-[0_24px_60px_rgba(36,99,235,0.28)]">
          <p class="text-xs font-semibold uppercase tracking-[0.24em] text-blue-600/80 dark:text-white/70">Gợi ý vận hành</p>
          <h3 class="mt-3 text-2xl font-black leading-tight">Đừng để hồ sơ chờ quá lâu</h3>
          <ul class="mt-5 space-y-3 text-sm leading-7 text-slate-700 dark:text-white/90">
            <li class="flex gap-3">
              <span class="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-blue-500 dark:bg-white/90" />
              <span>Hồ sơ chờ phản hồi lâu dễ làm giảm thiện cảm của ứng viên chất lượng.</span>
            </li>
            <li class="flex gap-3">
              <span class="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-blue-500 dark:bg-white/90" />
              <span>Khi đã hẹn lịch, nên cập nhật kết quả hoặc ghi chú ngay để team không bị mất ngữ cảnh.</span>
            </li>
            <li class="flex gap-3">
              <span class="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-blue-500 dark:bg-white/90" />
              <span>Dùng tab này như một “hàng đợi xử lý” ứng tuyển thay vì theo dõi rời rạc từng tin tuyển dụng.</span>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <div v-if="modalOpen" class="fixed inset-0 z-50 overflow-y-auto bg-slate-950/60 backdrop-blur-sm">
      <div class="flex min-h-full items-center justify-center px-4 py-6">
        <div class="flex max-h-[calc(100vh-2rem)] w-full max-w-[min(1500px,calc(100vw-2rem))] flex-col overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-[0_30px_80px_rgba(15,23,42,0.18)] dark:border-slate-800 dark:bg-slate-950 dark:shadow-[0_30px_80px_rgba(15,23,42,0.55)]">
        <div class="flex items-center justify-between border-b border-slate-200 px-6 py-5 dark:border-slate-800">
          <div>
            <h3 class="text-xl font-bold text-slate-900 dark:text-white">Cập nhật ứng tuyển</h3>
            <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
              {{ selectedApplication?.tin_tuyen_dung?.tieu_de || 'Tin tuyển dụng' }}
            </p>
          </div>
          <button class="rounded-xl p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-900 dark:hover:text-white" type="button" @click="closeModal">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>

        <div ref="modalBodyRef" class="flex-1 overflow-y-auto bg-slate-50/70 dark:bg-slate-950">
          <div class="grid gap-6 p-5 xl:grid-cols-[250px_minmax(0,1fr)]">
            <aside class="hidden xl:block">
              <div class="sticky top-0 rounded-2xl border border-slate-200 bg-white p-3 shadow-sm dark:border-slate-800 dark:bg-slate-900">
                <p class="px-3 py-2 text-[11px] font-black uppercase tracking-[0.22em] text-slate-400">Khu vực xử lý</p>
                <div class="space-y-1">
                  <button class="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-left text-sm font-bold text-slate-600 transition hover:bg-slate-50 hover:text-[#2463eb] dark:text-slate-300 dark:hover:bg-slate-800" type="button" @click="scrollModalToSection('overview')">
                    <span class="material-symbols-outlined text-[18px]">fact_check</span>
                    Tổng quan
                  </button>
                  <button class="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-left text-sm font-bold text-slate-600 transition hover:bg-slate-50 hover:text-[#2463eb] dark:text-slate-300 dark:hover:bg-slate-800" type="button" @click="scrollModalToSection('interview')">
                    <span class="material-symbols-outlined text-[18px]">account_tree</span>
                    Vòng phỏng vấn
                  </button>
                  <button class="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-left text-sm font-bold text-slate-600 transition hover:bg-slate-50 hover:text-[#2463eb] dark:text-slate-300 dark:hover:bg-slate-800" type="button" @click="scrollModalToSection('copilot')">
                    <span class="material-symbols-outlined text-[18px]">auto_awesome</span>
                    Interview Copilot
                  </button>
                  <button class="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-left text-sm font-bold text-slate-600 transition hover:bg-slate-50 hover:text-[#2463eb] dark:text-slate-300 dark:hover:bg-slate-800" type="button" @click="scrollModalToSection('interview-basic')">
                    <span class="material-symbols-outlined text-[18px]">event</span>
                    Lịch hẹn chung
                  </button>
                  <button class="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-left text-sm font-bold text-slate-600 transition hover:bg-slate-50 hover:text-[#2463eb] dark:text-slate-300 dark:hover:bg-slate-800" type="button" @click="scrollModalToSection('offer')">
                    <span class="material-symbols-outlined text-[18px]">workspace_premium</span>
                    Offer
                  </button>
                  <button v-if="canManageOnboarding" class="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-left text-sm font-bold text-slate-600 transition hover:bg-slate-50 hover:text-[#2463eb] dark:text-slate-300 dark:hover:bg-slate-800" type="button" @click="scrollModalToSection('onboarding')">
                    <span class="material-symbols-outlined text-[18px]">fact_check</span>
                    Onboarding
                  </button>
                  <button class="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-left text-sm font-bold text-slate-600 transition hover:bg-slate-50 hover:text-[#2463eb] dark:text-slate-300 dark:hover:bg-slate-800" type="button" @click="scrollModalToSection('notes')">
                    <span class="material-symbols-outlined text-[18px]">notes</span>
                    Ghi chú
                  </button>
                </div>
              </div>
            </aside>

            <div class="grid grid-cols-1 gap-5 md:grid-cols-2">
          <div class="md:col-span-2 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900" data-modal-section="overview">
            <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Trạng thái</label>
            <select
              v-model="form.trang_thai"
              :disabled="!canProcessApplications"
              class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-[#2463eb] dark:border-slate-800 dark:bg-slate-950 dark:text-white disabled:cursor-not-allowed disabled:opacity-60"
            >
              <option v-for="status in statusOptionsForSelectedApplication" :key="String(status.value)" :value="status.value">
                {{ status.label }}
              </option>
            </select>
            <p
              v-if="selectedApplication && isFinalApplicationStatus(selectedApplication)"
              class="mt-2 text-xs text-slate-500 dark:text-slate-400"
            >
              Đơn này đã có kết quả cuối, bạn chỉ có thể cập nhật ghi chú nội bộ hoặc thông tin bổ sung mà không đổi trạng thái.
            </p>
          </div>

          <div v-if="activeTemplate" class="md:col-span-2 rounded-2xl border border-blue-100 bg-blue-50 p-4 dark:border-blue-500/20 dark:bg-blue-500/10">
            <div class="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
              <div>
                <p class="text-xs font-black uppercase tracking-[0.2em] text-blue-600 dark:text-blue-300">Template thông báo</p>
                <h4 class="mt-2 text-base font-black text-slate-900 dark:text-white">{{ activeTemplate.title }}</h4>
                <p class="mt-1 text-sm font-semibold text-slate-700 dark:text-slate-200">Tiêu đề email: {{ activeTemplate.subject }}</p>
              </div>
              <span class="rounded-full bg-white px-3 py-1 text-xs font-bold text-blue-700 dark:bg-slate-900 dark:text-blue-300">
                {{ activeTemplate.status_label }}
              </span>
            </div>
            <p class="mt-3 text-sm leading-7 text-slate-700 dark:text-slate-200">{{ activeTemplate.body }}</p>
            <p class="mt-3 text-xs leading-5 text-slate-500 dark:text-slate-400">{{ activeTemplate.usage_hint }}</p>
          </div>

          <div class="md:col-span-2 rounded-2xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-900/70" data-modal-section="interview">
            <div class="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
              <div>
                <p class="text-xs font-black uppercase tracking-[0.2em] text-slate-500">Timeline phỏng vấn</p>
                <h4 class="mt-2 text-base font-black text-slate-900 dark:text-white">Quản lý nhiều vòng phỏng vấn riêng biệt</h4>
                <p class="mt-1 text-sm leading-6 text-slate-600 dark:text-slate-300">
                  Mỗi vòng có lịch, interviewer, kết quả, điểm và Copilot riêng. Vòng đang chọn sẽ được dùng cho Copilot bên dưới.
                </p>
              </div>
              <button
                class="inline-flex h-10 items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 text-sm font-bold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-200"
                type="button"
                @click="resetRoundForm(); roundForm.thu_tu = selectedInterviewRounds.length + 1; roundForm.ten_vong = `Vòng ${selectedInterviewRounds.length + 1}`"
              >
                <span class="material-symbols-outlined text-[18px]">add</span>
                Thêm vòng
              </button>
              <button
                v-if="canExportDocument(selectedApplication, 'interview')"
                class="inline-flex h-10 items-center justify-center gap-2 rounded-xl border border-violet-200 bg-white px-4 text-sm font-bold text-violet-700 transition hover:bg-violet-50 disabled:opacity-60 dark:border-violet-500/20 dark:bg-slate-950 dark:text-violet-300"
                :disabled="exportingApplicationId === `${selectedApplication?.id}:interview`"
                type="button"
                @click="downloadApplicationExport(selectedApplication, 'interview')"
              >
                <span class="material-symbols-outlined text-[18px]">picture_as_pdf</span>
                {{ exportingApplicationId === `${selectedApplication?.id}:interview` ? 'Đang tạo...' : 'PDF phỏng vấn' }}
              </button>
            </div>

            <div v-if="selectedInterviewRounds.length" class="mt-4 grid grid-cols-1 gap-3 lg:grid-cols-2">
              <button
                v-for="round in selectedInterviewRounds"
                :key="round.id"
                :data-interview-round-id="round.id"
                class="rounded-2xl border p-4 text-left transition hover:border-violet-300 hover:bg-white dark:hover:border-violet-500/40 dark:hover:bg-slate-950/50"
                :class="Number(selectedRoundId) === Number(round.id)
                  ? 'border-violet-400 bg-white shadow-sm dark:border-violet-500/50 dark:bg-slate-950/50'
                  : 'border-slate-200 bg-slate-100/70 dark:border-slate-800 dark:bg-slate-950/30'"
                type="button"
                @click="selectRound(round)"
              >
                <div class="flex items-start justify-between gap-3">
                  <div>
                    <p class="font-black text-slate-900 dark:text-white">{{ round.ten_vong }}</p>
                    <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">
                      {{ roundTypeLabel(round.loai_vong) }} • {{ formatDateTime(round.ngay_hen_phong_van) }}
                    </p>
                  </div>
                  <span class="rounded-full px-2.5 py-1 text-[11px] font-bold" :class="roundStatusMeta(round.trang_thai).classes">
                    {{ roundStatusMeta(round.trang_thai).label }}
                  </span>
                </div>
                <p v-if="round.nguoi_phong_van" class="mt-2 text-xs text-slate-500 dark:text-slate-400">Interviewer: {{ round.nguoi_phong_van }}</p>
                <p class="mt-2 text-xs" :class="interviewAttendanceMeta(round.trang_thai_tham_gia).classes">
                  {{ interviewAttendanceMeta(round.trang_thai_tham_gia).label }}
                </p>
              </button>
            </div>

            <div v-else class="mt-4 rounded-2xl border border-dashed border-slate-300 px-4 py-6 text-center text-sm text-slate-500 dark:border-slate-700 dark:text-slate-400">
              Chưa có vòng phỏng vấn riêng. Tạo vòng đầu tiên để chuẩn hóa timeline.
            </div>

            <div class="mt-5 grid grid-cols-1 gap-4 md:grid-cols-2">
              <div>
                <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Tên vòng</label>
                <input v-model="roundForm.ten_vong" class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none focus:border-violet-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white" placeholder="Vòng 1 - HR screening">
              </div>
              <div>
                <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Loại vòng</label>
                <select v-model="roundForm.loai_vong" class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none focus:border-violet-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white">
                  <option value="hr">HR screening</option>
                  <option value="technical">Technical</option>
                  <option value="manager">Manager</option>
                  <option value="final">Final</option>
                  <option value="culture">Culture fit</option>
                  <option value="other">Khác</option>
                </select>
              </div>
              <div>
                <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Thời gian</label>
                <input v-model="roundForm.ngay_hen_phong_van" class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none focus:border-violet-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white" type="datetime-local">
              </div>
              <div>
                <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Hình thức</label>
                <select v-model="roundForm.hinh_thuc_phong_van" class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none focus:border-violet-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white">
                  <option value="">Chưa chọn</option>
                  <option value="online">Online</option>
                  <option value="offline">Trực tiếp</option>
                  <option value="phone">Điện thoại</option>
                </select>
              </div>
              <div>
                <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Interviewer</label>
                <input v-model="roundForm.nguoi_phong_van" class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none focus:border-violet-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white" placeholder="Tên người phỏng vấn">
              </div>
              <div>
                <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Trạng thái vòng</label>
                <select v-model="roundForm.trang_thai" class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none focus:border-violet-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white">
                  <option :value="0">Đã lên lịch</option>
                  <option :value="1">Hoàn thành</option>
                  <option :value="2">Đã hủy</option>
                </select>
              </div>
              <div class="md:col-span-2">
                <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Link / địa điểm</label>
                <input v-model="roundForm.link_phong_van" class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none focus:border-violet-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white" placeholder="https://meet.google.com/... hoặc địa điểm">
              </div>
              <div>
                <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Điểm</label>
                <input v-model="roundForm.diem_so" class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none focus:border-violet-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white" min="0" max="10" type="number">
              </div>
              <div>
                <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Kết quả</label>
                <input v-model="roundForm.ket_qua" class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none focus:border-violet-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white" placeholder="Qua vòng / cần cân nhắc...">
              </div>
              <div class="md:col-span-2">
                <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Ghi chú vòng</label>
                <textarea v-model="roundForm.ghi_chu" class="min-h-[90px] w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none focus:border-violet-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white" placeholder="Ghi chú riêng cho vòng này..." />
              </div>
            </div>

            <div class="mt-4 flex flex-wrap justify-end gap-2">
              <button
                v-if="roundForm.id"
                class="rounded-xl border border-rose-200 px-4 py-2 text-sm font-bold text-rose-700 transition hover:bg-rose-50 disabled:opacity-60 dark:border-rose-500/20 dark:text-rose-300 dark:hover:bg-rose-500/10"
                :disabled="roundDeletingId === roundForm.id"
                type="button"
                @click="deleteInterviewRound(selectedRound)"
              >
                {{ roundDeletingId === roundForm.id ? 'Đang xóa...' : 'Xóa vòng' }}
              </button>
              <button
                class="rounded-xl bg-violet-600 px-4 py-2 text-sm font-bold text-white transition hover:bg-violet-700 disabled:opacity-60"
                :disabled="roundSaving || !roundForm.ten_vong"
                type="button"
                @click="saveInterviewRound"
              >
                {{ roundSaving ? 'Đang lưu...' : (roundForm.id ? 'Lưu vòng' : 'Tạo vòng') }}
              </button>
            </div>
          </div>

          <div class="md:col-span-2 rounded-2xl border border-violet-100 bg-violet-50 p-4 dark:border-violet-500/20 dark:bg-violet-500/10" data-modal-section="copilot">
            <div class="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
              <div>
                <p class="text-xs font-black uppercase tracking-[0.2em] text-violet-600 dark:text-violet-300">Interview Copilot</p>
                <h4 class="mt-2 text-base font-black text-slate-900 dark:text-white">AI hỗ trợ HR chuẩn bị và đánh giá phỏng vấn</h4>
                <p class="mt-1 text-sm leading-6 text-slate-600 dark:text-slate-300">
                  Sinh tóm tắt CV, câu hỏi phỏng vấn, rubric đánh giá và gợi ý kết luận sau khi HR nhập ghi chú. Employer được tính phí theo lượt dùng thành công.
                </p>
              </div>
              <div class="flex flex-wrap gap-2">
                <button
                  class="inline-flex h-10 items-center justify-center gap-2 rounded-xl bg-violet-600 px-4 text-sm font-bold text-white transition hover:bg-violet-700 disabled:opacity-60"
                  :disabled="billingLoading || copilotGenerating || !canGenerateSelectedInterviewCopilot"
                  type="button"
                  @click="generateInterviewCopilot"
                >
                  <span class="material-symbols-outlined text-[18px]" :class="copilotGenerating ? 'animate-spin' : ''">
                    {{ copilotGenerating ? 'progress_activity' : 'auto_awesome' }}
                  </span>
                  {{ copilotGenerating ? 'Đang tạo...' : `Tạo Copilot · ${formatFeaturePrice(copilotGenerateFeature)}` }}
                </button>
                <button
                  class="inline-flex h-10 items-center justify-center gap-2 rounded-xl bg-slate-900 px-4 text-sm font-bold text-white transition hover:bg-slate-800 disabled:opacity-60 dark:bg-white dark:text-slate-900"
                  :disabled="billingLoading || copilotEvaluating || !canEvaluateSelectedInterviewCopilot"
                  type="button"
                  @click="evaluateInterviewCopilot"
                >
                  <span class="material-symbols-outlined text-[18px]" :class="copilotEvaluating ? 'animate-spin' : ''">
                    {{ copilotEvaluating ? 'progress_activity' : 'fact_check' }}
                  </span>
                  {{ copilotEvaluating ? 'Đang đánh giá...' : `Đánh giá sau PV · ${formatFeaturePrice(copilotEvaluateFeature)}` }}
                </button>
              </div>
            </div>

            <div class="mt-4 grid grid-cols-1 gap-3 lg:grid-cols-3">
              <div class="rounded-2xl border border-violet-200 bg-white px-4 py-3 text-sm dark:border-violet-500/20 dark:bg-slate-950/50">
                <p class="text-xs font-bold uppercase tracking-[0.18em] text-violet-500">Generate</p>
                <p class="mt-1 font-black text-slate-900 dark:text-white">{{ formatFeaturePrice(copilotGenerateFeature) }}</p>
                <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">Tạo tóm tắt CV, focus area, câu hỏi và rubric.</p>
              </div>
              <div class="rounded-2xl border border-violet-200 bg-white px-4 py-3 text-sm dark:border-violet-500/20 dark:bg-slate-950/50">
                <p class="text-xs font-bold uppercase tracking-[0.18em] text-violet-500">Ví Employer</p>
                <p class="mt-1 font-black text-slate-900 dark:text-white">{{ billingLoading ? 'Đang tải...' : formatCurrency(walletAvailable) }}</p>
                <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">Ví chỉ bị trừ sau khi AI trả kết quả thành công.</p>
              </div>
              <div class="rounded-2xl border border-violet-200 bg-white px-4 py-3 text-sm dark:border-violet-500/20 dark:bg-slate-950/50">
                <p class="text-xs font-bold uppercase tracking-[0.18em] text-violet-500">Evaluate</p>
                <p class="mt-1 font-black text-slate-900 dark:text-white">{{ formatFeaturePrice(copilotEvaluateFeature) }}</p>
                <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">Fallback local hoặc lỗi AI sẽ không trừ ví employer.</p>
              </div>
            </div>

            <div
              v-if="selectedApplication && !canUseSelectedInterviewCopilot"
              class="mt-4 rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-600 dark:border-slate-800 dark:bg-slate-950/50 dark:text-slate-300"
            >
              <span class="font-bold text-slate-900 dark:text-white">Chế độ xem lại:</span>
              <span class="ml-1">
                {{ isFinalApplicationStatus(selectedApplication)
                  ? 'Đơn đã trúng tuyển hoặc từ chối nên không thể tạo/đánh giá Copilot mới.'
                  : 'Bạn không có quyền thao tác Interview Copilot cho đơn này.' }}
              </span>
            </div>
            <div
              v-else-if="needsInterviewCopilotTopup"
              class="mt-4 flex flex-col gap-3 rounded-2xl border border-amber-200 bg-white px-4 py-3 text-sm text-amber-800 dark:border-amber-500/20 dark:bg-slate-950/50 dark:text-amber-200"
            >
              <p>Ví employer hiện không đủ để dùng Interview Copilot theo lượt. Nạp thêm ví để tiếp tục tạo hoặc đánh giá bằng AI.</p>
              <button
                class="inline-flex w-fit items-center gap-2 rounded-xl bg-amber-500 px-4 py-2 font-bold text-white transition hover:bg-amber-600"
                type="button"
                @click="router.push('/employer/billing')"
              >
                <span class="material-symbols-outlined text-[18px]">account_balance_wallet</span>
                Nạp ví employer
              </button>
            </div>
            <div
              v-if="selectedInterviewOverdue"
              class="mt-4 rounded-2xl border border-rose-200 bg-white px-4 py-3 text-sm leading-6 text-rose-700 dark:border-rose-500/20 dark:bg-slate-950/50 dark:text-rose-200"
            >
              Lịch phỏng vấn đã quá thời gian nhưng đơn chưa có kết quả cuối. Sau khi xem lại ghi chú/Copilot, nên cập nhật trạng thái sang <span class="font-bold">Trúng tuyển</span> hoặc <span class="font-bold">Từ chối</span> nếu đã có quyết định.
            </div>

            <div v-if="copilotPreInterview" class="mt-4 space-y-4">
              <div class="rounded-2xl bg-white p-4 dark:bg-slate-950/50">
                <p class="text-xs font-black uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">Tóm tắt nhanh</p>
                <p class="mt-2 text-sm leading-7 text-slate-700 dark:text-slate-200">{{ copilotPreInterview.candidate_summary }}</p>
              </div>

              <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
                <div class="rounded-2xl bg-white p-4 dark:bg-slate-950/50">
                  <p class="text-xs font-black uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">Trọng tâm phỏng vấn</p>
                  <ul class="mt-3 space-y-2 text-sm leading-6 text-slate-700 dark:text-slate-200">
                    <li v-for="item in copilotPreInterview.focus_areas || []" :key="item" class="flex gap-2">
                      <span class="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-violet-500" />
                      <span>{{ item }}</span>
                    </li>
                  </ul>
                </div>
                <div class="rounded-2xl bg-white p-4 dark:bg-slate-950/50">
                  <p class="text-xs font-black uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">Rủi ro cần kiểm tra</p>
                  <ul class="mt-3 space-y-2 text-sm leading-6 text-slate-700 dark:text-slate-200">
                    <li v-for="item in copilotPreInterview.red_flags || []" :key="item" class="flex gap-2">
                      <span class="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                      <span>{{ item }}</span>
                    </li>
                  </ul>
                </div>
              </div>

              <div class="rounded-2xl bg-white p-4 dark:bg-slate-950/50">
                <p class="text-xs font-black uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">Câu hỏi phỏng vấn gợi ý</p>
                <div class="mt-3 grid grid-cols-1 gap-3 lg:grid-cols-2">
                  <div
                    v-for="group in copilotPreInterview.questions || []"
                    :key="group.group"
                    class="rounded-xl bg-slate-50 p-3 dark:bg-slate-900"
                  >
                    <p class="font-bold text-slate-900 dark:text-white">{{ group.group }}</p>
                    <ol class="mt-2 list-decimal space-y-1 pl-5 text-sm leading-6 text-slate-600 dark:text-slate-300">
                      <li v-for="question in group.items || []" :key="question">{{ question }}</li>
                    </ol>
                  </div>
                </div>
              </div>

              <div class="rounded-2xl bg-white p-4 dark:bg-slate-950/50">
                <p class="text-xs font-black uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">Rubric đánh giá</p>
                <div class="mt-3 space-y-3">
                  <div
                    v-for="(item, index) in copilotPreInterview.rubric || []"
                    :key="`${item.criterion}-${index}`"
                    class="grid grid-cols-1 gap-3 rounded-xl bg-slate-50 p-3 dark:bg-slate-900 lg:grid-cols-[minmax(0,1fr)_120px]"
                  >
                    <div>
                      <p class="font-bold text-slate-900 dark:text-white">
                        {{ item.criterion }}
                        <span v-if="item.weight" class="text-xs font-semibold text-slate-500">({{ item.weight }}%)</span>
                      </p>
                      <p class="mt-1 text-sm leading-6 text-slate-600 dark:text-slate-300">{{ item.expectation || 'Chưa có mô tả kỳ vọng.' }}</p>
                    </div>
                    <input
                      v-model="copilotScores[item.criterion]"
                      class="h-11 rounded-xl border border-slate-200 bg-white px-3 text-sm text-slate-900 outline-none focus:border-violet-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white"
                      max="10"
                      min="0"
                      placeholder="0-10"
                      type="number"
                    >
                  </div>
                </div>
              </div>
            </div>

            <div v-if="copilotPostInterview" class="mt-4 rounded-2xl bg-white p-4 dark:bg-slate-950/50">
              <p class="text-xs font-black uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">Gợi ý sau phỏng vấn</p>
              <p class="mt-2 text-sm font-semibold leading-7 text-slate-900 dark:text-white">{{ copilotPostInterview.summary }}</p>
              <div class="mt-3 grid grid-cols-1 gap-3 lg:grid-cols-3">
                <div class="rounded-xl bg-emerald-50 p-3 dark:bg-emerald-900/20">
                  <p class="text-xs font-black uppercase text-emerald-700 dark:text-emerald-300">Điểm mạnh</p>
                  <ul class="mt-2 space-y-1 text-sm leading-6 text-slate-700 dark:text-slate-200">
                    <li v-for="item in copilotPostInterview.strengths || []" :key="item">{{ item }}</li>
                  </ul>
                </div>
                <div class="rounded-xl bg-amber-50 p-3 dark:bg-amber-900/20">
                  <p class="text-xs font-black uppercase text-amber-700 dark:text-amber-300">Điểm cần lưu ý</p>
                  <ul class="mt-2 space-y-1 text-sm leading-6 text-slate-700 dark:text-slate-200">
                    <li v-for="item in copilotPostInterview.concerns || []" :key="item">{{ item }}</li>
                  </ul>
                </div>
                <div class="rounded-xl bg-blue-50 p-3 dark:bg-blue-900/20">
                  <p class="text-xs font-black uppercase text-blue-700 dark:text-blue-300">Bước tiếp theo</p>
                  <ul class="mt-2 space-y-1 text-sm leading-6 text-slate-700 dark:text-slate-200">
                    <li v-for="item in copilotPostInterview.next_steps || []" :key="item">{{ item }}</li>
                  </ul>
                </div>
              </div>
              <p class="mt-3 rounded-xl bg-violet-50 p-3 text-sm font-semibold leading-6 text-violet-700 dark:bg-violet-900/20 dark:text-violet-300">
                Khuyến nghị: {{ copilotPostInterview.recommendation }}
              </p>
            </div>
          </div>

          <div class="md:col-span-2 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900" data-modal-section="interview-basic">
            <div class="mb-5">
              <p class="text-xs font-black uppercase tracking-[0.2em] text-slate-500">Lịch hẹn chung</p>
              <h4 class="mt-2 text-base font-black text-slate-900 dark:text-white">Thông tin phỏng vấn ở cấp ứng tuyển</h4>
              <p class="mt-1 text-sm leading-6 text-slate-600 dark:text-slate-300">
                Dùng cho lịch hẹn tổng quát của đơn. Nếu quy trình có nhiều vòng, hãy ưu tiên cập nhật trong từng vòng phỏng vấn phía trên.
              </p>
            </div>
            <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div class="md:col-span-2">
            <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Ngày hẹn phỏng vấn</label>
            <input
              v-model="form.ngay_hen_phong_van"
              :disabled="!canProcessApplications"
              class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-[#2463eb] dark:border-slate-800 dark:bg-slate-900 dark:text-white disabled:opacity-60 disabled:cursor-not-allowed"
              type="datetime-local"
            >
          </div>

          <div>
            <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Hình thức phỏng vấn</label>
            <select
              v-model="form.hinh_thuc_phong_van"
              :disabled="!canProcessApplications"
              class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-[#2463eb] dark:border-slate-800 dark:bg-slate-900 dark:text-white disabled:opacity-60 disabled:cursor-not-allowed"
            >
              <option value="">Chưa chọn</option>
              <option value="online">Online</option>
              <option value="offline">Trực tiếp</option>
              <option value="phone">Điện thoại</option>
            </select>
          </div>

          <div>
            <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Người phỏng vấn</label>
            <select
              v-model="form.nguoi_phong_van"
              :disabled="!canProcessApplications"
              class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-[#2463eb] dark:border-slate-800 dark:bg-slate-900 dark:text-white disabled:opacity-60 disabled:cursor-not-allowed"
            >
              <option value="">Chọn người phỏng vấn</option>
              <option v-for="option in interviewerOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
            <p class="mt-2 text-xs text-slate-500 dark:text-slate-400">
              Chỉ hiển thị các HR nội bộ hiện có của công ty.
            </p>
          </div>

          <div>
            <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">HR phụ trách</label>
            <select
              v-model="form.hr_phu_trach_id"
              :disabled="!canManageAllAssignments || !canProcessApplications"
              class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-[#2463eb] dark:border-slate-800 dark:bg-slate-900 dark:text-white disabled:opacity-60 disabled:cursor-not-allowed"
            >
              <option value="">Tự gán theo người xử lý</option>
              <option v-for="member in assignableMembers" :key="member.id" :value="String(member.id)">
                {{ member.label }}
              </option>
            </select>
            <p v-if="!canManageAllAssignments" class="mt-2 text-xs text-slate-500 dark:text-slate-400">
              Với vai trò {{ currentInternalRoleLabel }}, đơn ứng tuyển sẽ luôn được gán cho chính bạn khi cập nhật.
            </p>
          </div>

          <div class="md:col-span-2">
            <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Link meeting / địa điểm</label>
            <input
              v-model="form.link_phong_van"
              :disabled="!canProcessApplications"
              class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-[#2463eb] dark:border-slate-800 dark:bg-slate-900 dark:text-white disabled:opacity-60 disabled:cursor-not-allowed"
              placeholder="https://meet.google.com/... hoặc địa điểm phỏng vấn"
              type="text"
            >
          </div>

          <div class="md:col-span-2">
            <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Kết quả phỏng vấn</label>
            <input
              v-model="form.ket_qua_phong_van"
              :disabled="!canProcessApplications"
              class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-[#2463eb] dark:border-slate-800 dark:bg-slate-900 dark:text-white disabled:opacity-60 disabled:cursor-not-allowed"
              placeholder="Ví dụ: Qua vòng 1, cần thêm bài test..."
              type="text"
            >
          </div>
            </div>
          </div>

          <div class="md:col-span-2 rounded-2xl border border-emerald-100 bg-emerald-50 p-4 dark:border-emerald-500/20 dark:bg-emerald-500/10" data-modal-section="offer">
            <div class="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
              <div>
                <p class="text-xs font-black uppercase tracking-[0.2em] text-emerald-700 dark:text-emerald-300">Offer / nhận việc</p>
                <h4 class="mt-2 text-base font-black text-slate-900 dark:text-white">
                  Gửi đề nghị nhận việc và chờ ứng viên phản hồi
                </h4>
                <p class="mt-1 text-sm leading-6 text-slate-600 dark:text-slate-300">
                  Khi gửi offer, đơn sẽ chuyển sang trạng thái trúng tuyển và ứng viên có thể chấp nhận hoặc từ chối trên UI/email.
                </p>
              </div>
              <span
                v-if="selectedApplication"
                class="inline-flex rounded-full px-3 py-1 text-xs font-bold"
                :class="offerStatusMeta(selectedApplication.trang_thai_offer).classes"
              >
                {{ offerStatusMeta(selectedApplication.trang_thai_offer).label }}
              </span>
            </div>

            <div class="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
              <div class="md:col-span-2">
                <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Tóm tắt offer</label>
                <textarea
                  v-model="offerForm.ghi_chu_offer"
                  :disabled="!canSendOffer(selectedApplication)"
                  class="min-h-[110px] w-full rounded-2xl border border-emerald-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-emerald-500 dark:border-emerald-500/20 dark:bg-slate-950/50 dark:text-white disabled:opacity-60"
                  maxlength="5000"
                  placeholder="Ví dụ: mức lương, ngày bắt đầu, địa điểm làm việc, phúc lợi chính..."
                />
              </div>
              <div>
                <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Link tài liệu offer</label>
                <input
                  v-model="offerForm.link_offer"
                  :disabled="!canSendOffer(selectedApplication)"
                  class="w-full rounded-2xl border border-emerald-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-emerald-500 dark:border-emerald-500/20 dark:bg-slate-950/50 dark:text-white disabled:opacity-60"
                  placeholder="https://..."
                  type="url"
                >
              </div>
              <div>
                <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Hạn phản hồi</label>
                <input
                  v-model="offerForm.han_phan_hoi_offer"
                  :disabled="!canSendOffer(selectedApplication)"
                  class="w-full rounded-2xl border border-emerald-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-emerald-500 dark:border-emerald-500/20 dark:bg-slate-950/50 dark:text-white disabled:opacity-60"
                  type="datetime-local"
                >
              </div>
            </div>

            <div class="mt-4 flex flex-wrap items-center justify-between gap-3">
              <p class="text-xs leading-5 text-emerald-800 dark:text-emerald-200">
                Link phản hồi trong email sẽ hết hạn theo hạn phản hồi offer. Nếu bỏ trống, hệ thống dùng mặc định 14 ngày.
              </p>
              <button
                class="inline-flex h-11 items-center justify-center gap-2 rounded-xl bg-emerald-600 px-4 text-sm font-bold text-white transition hover:bg-emerald-700 disabled:opacity-60"
                :disabled="!canSendOffer(selectedApplication) || sendingOfferId === selectedApplication?.id"
                type="button"
                @click="sendOffer"
              >
                <span
                  class="material-symbols-outlined text-[18px]"
                  :class="sendingOfferId === selectedApplication?.id ? 'animate-spin' : ''"
                >
                  {{ sendingOfferId === selectedApplication?.id ? 'progress_activity' : 'workspace_premium' }}
                </span>
                {{ Number(selectedApplication?.trang_thai_offer || 0) === OFFER_STATUS.SENT ? 'Gửi lại / cập nhật offer' : 'Gửi offer' }}
              </button>
              <button
                v-if="canExportDocument(selectedApplication, 'offer')"
                class="inline-flex h-11 items-center justify-center gap-2 rounded-xl border border-emerald-200 bg-white px-4 text-sm font-bold text-emerald-700 transition hover:bg-emerald-50 disabled:opacity-60 dark:border-emerald-500/20 dark:bg-slate-950/40 dark:text-emerald-300"
                :disabled="exportingApplicationId === `${selectedApplication?.id}:offer`"
                type="button"
                @click="downloadApplicationExport(selectedApplication, 'offer')"
              >
                <span class="material-symbols-outlined text-[18px]">picture_as_pdf</span>
                {{ exportingApplicationId === `${selectedApplication?.id}:offer` ? 'Đang tạo...' : 'Tải offer PDF' }}
              </button>
            </div>
          </div>

          <div
            v-if="canManageOnboarding"
            data-modal-section="onboarding"
            class="md:col-span-2 rounded-2xl border border-blue-100 bg-blue-50 p-4 dark:border-blue-500/20 dark:bg-blue-500/10"
          >
            <div class="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
              <div>
                <p class="text-xs font-black uppercase tracking-[0.2em] text-blue-700 dark:text-blue-300">Onboarding sau offer</p>
                <h4 class="mt-2 text-base font-black text-slate-900 dark:text-white">Checklist chuẩn bị nhận việc</h4>
                <p class="mt-1 text-sm leading-6 text-slate-600 dark:text-slate-300">
                  Theo dõi ngày bắt đầu, tài liệu cần chuẩn bị và các bước HR/ứng viên cần hoàn tất sau khi ứng viên chấp nhận offer.
                </p>
              </div>
              <div class="text-right">
                <p class="text-2xl font-black text-[#2463eb]">{{ selectedOnboardingPlan?.progress?.percent || 0 }}%</p>
                  <p class="text-xs font-bold text-slate-500 dark:text-slate-300">
                    {{ selectedOnboardingPlan?.progress?.done || 0 }}/{{ selectedOnboardingPlan?.progress?.total || 0 }} việc
                  </p>
                  <button
                    v-if="canExportDocument(selectedApplication, 'onboarding')"
                    class="mt-2 text-xs font-bold text-blue-700 underline underline-offset-4 disabled:opacity-60 dark:text-blue-300"
                    :disabled="exportingApplicationId === `${selectedApplication?.id}:onboarding`"
                    type="button"
                    @click="downloadApplicationExport(selectedApplication, 'onboarding')"
                  >
                    {{ exportingApplicationId === `${selectedApplication?.id}:onboarding` ? 'Đang tạo PDF...' : 'Tải PDF' }}
                  </button>
                </div>
              </div>

            <div v-if="onboardingLoading" class="mt-4 rounded-xl bg-white/70 p-4 text-sm text-slate-500 dark:bg-slate-950/40 dark:text-slate-300">
              Đang tải onboarding...
            </div>

            <div v-else class="mt-4 space-y-4">
              <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
                <div>
                  <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Ngày bắt đầu</label>
                  <input v-model="onboardingForm.ngay_bat_dau" type="date" class="w-full rounded-2xl border border-blue-200 bg-white px-4 py-3 text-sm outline-none focus:border-blue-500 dark:border-blue-500/20 dark:bg-slate-950/50 dark:text-white">
                </div>
                <div>
                  <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Trạng thái</label>
                  <select v-model="onboardingForm.trang_thai" class="w-full rounded-2xl border border-blue-200 bg-white px-4 py-3 text-sm outline-none focus:border-blue-500 dark:border-blue-500/20 dark:bg-slate-950/50 dark:text-white">
                    <option value="not_started">Chưa bắt đầu</option>
                    <option value="preparing">Đang chuẩn bị</option>
                    <option value="in_progress">Đang thực hiện</option>
                    <option value="completed">Hoàn tất</option>
                    <option value="cancelled">Hủy</option>
                  </select>
                </div>
                <div>
                  <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Địa điểm</label>
                  <input v-model="onboardingForm.dia_diem_lam_viec" class="w-full rounded-2xl border border-blue-200 bg-white px-4 py-3 text-sm outline-none focus:border-blue-500 dark:border-blue-500/20 dark:bg-slate-950/50 dark:text-white" placeholder="Văn phòng / remote / hybrid">
                </div>
                <div class="md:col-span-3">
                  <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Lời nhắn cho ứng viên</label>
                  <textarea v-model="onboardingForm.loi_chao_mung" class="min-h-[86px] w-full rounded-2xl border border-blue-200 bg-white px-4 py-3 text-sm outline-none focus:border-blue-500 dark:border-blue-500/20 dark:bg-slate-950/50 dark:text-white" placeholder="Chào mừng, hướng dẫn ngày đầu tiên..." />
                </div>
                <div class="md:col-span-2">
                  <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Tài liệu cần chuẩn bị</label>
                  <textarea v-model="onboardingForm.tai_lieu_text" class="min-h-[100px] w-full rounded-2xl border border-blue-200 bg-white px-4 py-3 text-sm outline-none focus:border-blue-500 dark:border-blue-500/20 dark:bg-slate-950/50 dark:text-white" placeholder="Mỗi dòng là một tài liệu" />
                </div>
                <div>
                  <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Ghi chú nội bộ</label>
                  <textarea v-model="onboardingForm.ghi_chu_noi_bo" class="min-h-[100px] w-full rounded-2xl border border-blue-200 bg-white px-4 py-3 text-sm outline-none focus:border-blue-500 dark:border-blue-500/20 dark:bg-slate-950/50 dark:text-white" placeholder="Chỉ HR thấy" />
                </div>
              </div>

              <div class="flex justify-end">
                <button class="inline-flex items-center gap-2 rounded-xl bg-[#2463eb] px-4 py-3 text-sm font-bold text-white transition hover:bg-blue-700 disabled:opacity-60" type="button" :disabled="onboardingSaving" @click="saveOnboardingPlan">
                  <span class="material-symbols-outlined text-[18px]" :class="onboardingSaving ? 'animate-spin' : ''">{{ onboardingSaving ? 'progress_activity' : 'save' }}</span>
                  Lưu onboarding
                </button>
              </div>

              <div class="rounded-2xl border border-blue-100 bg-white p-4 dark:border-blue-500/20 dark:bg-slate-950/40">
                <div class="grid grid-cols-1 gap-3 md:grid-cols-[1fr_160px_150px_auto]">
                  <input v-model="onboardingTaskForm.tieu_de" class="rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-blue-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white" placeholder="Tên checklist mới">
                  <input v-model="onboardingTaskForm.han_hoan_tat" type="date" class="rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-blue-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white">
                  <select v-model="onboardingTaskForm.nguoi_phu_trach" class="rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-blue-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white">
                    <option value="candidate">Ứng viên</option>
                    <option value="hr">HR</option>
                  </select>
                  <button class="rounded-xl bg-blue-600 px-4 py-2 text-sm font-bold text-white disabled:opacity-60" type="button" :disabled="!onboardingTaskForm.tieu_de || onboardingTaskSavingId === 'new'" @click="createOnboardingTask">Thêm</button>
                </div>

                <div class="mt-4 space-y-2">
                  <div v-for="task in selectedOnboardingPlan?.tasks || []" :key="task.id" class="flex flex-col gap-3 rounded-xl border border-slate-100 bg-slate-50 p-3 dark:border-slate-800 dark:bg-slate-900 md:flex-row md:items-center md:justify-between">
                    <div>
                      <p class="font-bold text-slate-900 dark:text-white">{{ task.tieu_de }}</p>
                      <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">
                        {{ task.nguoi_phu_trach === 'candidate' ? 'Ứng viên phụ trách' : 'HR phụ trách' }}
                        <span v-if="task.han_hoan_tat"> • hạn {{ task.han_hoan_tat }}</span>
                      </p>
                    </div>
                    <div class="flex flex-wrap gap-2">
                      <select :value="task.trang_thai" class="rounded-xl border border-slate-200 px-3 py-2 text-xs font-bold outline-none dark:border-slate-700 dark:bg-slate-950 dark:text-white" :disabled="onboardingTaskSavingId === task.id" @change="updateOnboardingTaskStatus(task, $event.target.value)">
                        <option value="pending">Chờ làm</option>
                        <option value="in_progress">Đang làm</option>
                        <option value="done">Hoàn tất</option>
                        <option value="skipped">Bỏ qua</option>
                      </select>
                      <button class="rounded-xl border border-rose-200 px-3 py-2 text-xs font-bold text-rose-600 disabled:opacity-60 dark:border-rose-500/30" type="button" :disabled="onboardingTaskSavingId === task.id" @click="deleteOnboardingTask(task)">Xóa</button>
                    </div>
                  </div>
                  <p v-if="!(selectedOnboardingPlan?.tasks || []).length" class="text-sm text-slate-500 dark:text-slate-400">Chưa có checklist onboarding.</p>
                </div>
              </div>
            </div>
          </div>

          <div class="md:col-span-2 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900" data-modal-section="notes">
            <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Ghi chú</label>
            <textarea
              v-model="form.ghi_chu"
              :disabled="!canProcessApplications"
              class="min-h-[130px] w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-[#2463eb] dark:border-slate-800 dark:bg-slate-900 dark:text-white disabled:opacity-60 disabled:cursor-not-allowed"
              placeholder="Ghi chú nội bộ về hồ sơ, phản hồi sau buổi phỏng vấn hoặc bước tiếp theo..."
            />
          </div>
            </div>
          </div>
        </div>

        <div class="flex items-center justify-end gap-3 border-t border-slate-200 px-6 py-5 dark:border-slate-800">
          <button
            v-if="canResendInterviewEmail(selectedApplication)"
            class="rounded-2xl border border-emerald-500/20 bg-emerald-500/10 px-5 py-3 text-sm font-bold text-emerald-300 transition hover:bg-emerald-500/15 disabled:opacity-60"
            :disabled="resendingEmailId === selectedApplication?.id || !canProcessApplications"
            type="button"
            @click="resendInterviewEmail(selectedApplication)"
          >
            {{ resendingEmailId === selectedApplication?.id ? 'Đang gửi lại...' : 'Gửi lại email lịch hẹn' }}
          </button>
          <button
            class="rounded-2xl border border-slate-200 px-5 py-3 text-sm font-bold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-900"
            type="button"
            @click="closeModal"
          >
            Hủy
          </button>
          <button
            class="inline-flex min-w-[150px] items-center justify-center gap-2 rounded-2xl bg-[#2463eb] px-5 py-3 text-sm font-bold text-white shadow-lg shadow-[#2463eb]/20 transition hover:-translate-y-0.5 disabled:opacity-60"
            :disabled="saving || !canProcessApplications"
            type="button"
            @click="saveApplication"
          >
            <span v-if="saving" class="material-symbols-outlined animate-spin text-[18px]">progress_activity</span>
            {{ saving ? 'Đang lưu...' : 'Lưu cập nhật' }}
          </button>
        </div>
      </div>
      </div>
    </div>

    <div v-if="candidateDetailOpen" class="fixed inset-0 z-50 overflow-y-auto bg-slate-950/60 backdrop-blur-sm">
      <div class="flex min-h-full items-center justify-center px-4 py-6">
        <div class="flex max-h-[calc(100vh-3rem)] w-full max-w-3xl flex-col overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-[0_30px_80px_rgba(15,23,42,0.18)] dark:border-slate-800 dark:bg-slate-950 dark:shadow-[0_30px_80px_rgba(15,23,42,0.55)]">
        <div class="flex items-center justify-between border-b border-slate-200 px-6 py-5 dark:border-slate-800">
          <div>
            <h3 class="text-xl font-bold text-slate-900 dark:text-white">Chi tiết hồ sơ ứng viên</h3>
            <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
              {{ candidateDetail?.nguoi_dung?.ho_ten || candidateDetail?.tieu_de_ho_so || 'Hồ sơ công khai' }}
            </p>
          </div>
          <button class="rounded-xl p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-900 dark:hover:text-white" type="button" @click="closeCandidateDetail">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>

        <div v-if="candidateDetailLoading" class="flex-1 space-y-4 overflow-y-auto px-6 py-6">
          <div v-for="index in 4" :key="index" class="h-20 animate-pulse rounded-2xl bg-slate-100 dark:bg-slate-900" />
        </div>

        <div v-else-if="candidateDetail" class="grid flex-1 grid-cols-1 gap-5 overflow-y-auto p-6 md:grid-cols-2">
          <div class="md:col-span-2 rounded-2xl border border-slate-200 bg-slate-50 p-5 dark:border-slate-800 dark:bg-slate-900/60">
            <div class="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
              <div>
                <p class="text-2xl font-black text-slate-900 dark:text-white">{{ candidateDetail.tieu_de_ho_so || 'Hồ sơ ứng viên' }}</p>
                <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">
                  {{ candidateDetail.nguoi_dung?.ho_ten || 'Ứng viên công khai' }} • {{ candidateDetail.nguoi_dung?.email || 'Chưa có email' }}
                </p>
              </div>
              <span class="rounded-full bg-emerald-50 px-3 py-1 text-xs font-bold uppercase text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-300">
                Công khai
              </span>
            </div>
          </div>

          <div class="rounded-2xl border border-slate-200 bg-slate-50 p-5 dark:border-slate-800 dark:bg-slate-900/60">
            <p class="text-xs font-bold uppercase tracking-[0.22em] text-slate-400">Trình độ</p>
            <p class="mt-3 text-lg font-bold text-slate-900 dark:text-white">{{ degreeLabel(candidateDetail.trinh_do) }}</p>
          </div>

          <div class="rounded-2xl border border-slate-200 bg-slate-50 p-5 dark:border-slate-800 dark:bg-slate-900/60">
            <p class="text-xs font-bold uppercase tracking-[0.22em] text-slate-400">Kinh nghiệm</p>
            <p class="mt-3 text-lg font-bold text-slate-900 dark:text-white">{{ candidateDetail.kinh_nghiem_nam || 0 }} năm</p>
          </div>

          <div class="rounded-2xl border border-slate-200 bg-slate-50 p-5 dark:border-slate-800 dark:bg-slate-900/60">
            <p class="text-xs font-bold uppercase tracking-[0.22em] text-slate-400">Số điện thoại</p>
            <p class="mt-3 break-words text-lg font-bold text-slate-900 dark:text-white">{{ candidateDetail.nguoi_dung?.so_dien_thoai || 'Chưa cập nhật' }}</p>
          </div>

          <div class="rounded-2xl border border-slate-200 bg-slate-50 p-5 dark:border-slate-800 dark:bg-slate-900/60">
            <p class="text-xs font-bold uppercase tracking-[0.22em] text-slate-400">Email</p>
            <p class="mt-3 break-all text-lg font-bold text-slate-900 dark:text-white">{{ candidateDetail.nguoi_dung?.email || 'Chưa cập nhật' }}</p>
          </div>

          <div class="md:col-span-2 rounded-2xl border border-slate-200 bg-slate-50 p-5 dark:border-slate-800 dark:bg-slate-900/60">
            <p class="text-xs font-bold uppercase tracking-[0.22em] text-slate-400">Mục tiêu nghề nghiệp</p>
            <p class="mt-3 text-sm leading-7 text-slate-600 dark:text-slate-300">
              {{ candidateDetail.muc_tieu_nghe_nghiep || 'Ứng viên chưa bổ sung mục tiêu nghề nghiệp.' }}
            </p>
          </div>

          <div class="md:col-span-2 rounded-2xl border border-slate-200 bg-slate-50 p-5 dark:border-slate-800 dark:bg-slate-900/60">
            <p class="text-xs font-bold uppercase tracking-[0.22em] text-slate-400">Mô tả bản thân</p>
            <p class="mt-3 text-sm leading-7 text-slate-600 dark:text-slate-300">
              {{ candidateDetail.mo_ta_ban_than || 'Ứng viên chưa bổ sung mô tả bản thân.' }}
            </p>
          </div>
        </div>

        <div class="flex items-center justify-between gap-3 border-t border-slate-200 px-6 py-5 dark:border-slate-800">
          <button
            class="inline-flex items-center gap-2 rounded-2xl border border-slate-200 px-5 py-3 text-sm font-bold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-900"
            type="button"
            @click="openCv(candidateDetail)"
          >
            <span class="material-symbols-outlined text-[18px]">description</span>
            Xem CV
          </button>

          <button
            class="rounded-2xl border border-slate-200 px-5 py-3 text-sm font-bold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-900"
            type="button"
            @click="closeCandidateDetail"
          >
            Đóng
          </button>
        </div>
      </div>
      </div>
    </div>
  </div>
</template>
