<script setup>
import { computed, nextTick, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { applicationService, profileService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'
import { getStoredUser } from '@/utils/authStorage'
import { connectPrivateChannel } from '@/services/realtime'
import { formatDateTimeVN, formatDateVN, formatHistoricalDateVN } from '@/utils/dateTime'
import {
  APPLICATION_STATUS,
  OFFER_STATUS,
  getOfferStatusMeta,
  getApplicationStatusMeta,
  isFinalApplicationStatus,
} from '@/utils/applicationStatus'

const notify = useNotify()
const route = useRoute()
const router = useRouter()

const STATUS_ALL = ''
const STATUS_PENDING = String(APPLICATION_STATUS.PENDING)
const STATUS_REVIEWED = String(APPLICATION_STATUS.REVIEWED)
const STATUS_INTERVIEW = String(APPLICATION_STATUS.INTERVIEW_SCHEDULED)
const STATUS_PASSED = String(APPLICATION_STATUS.INTERVIEW_PASSED)
const STATUS_HIRED = String(APPLICATION_STATUS.HIRED)
const STATUS_REJECTED = String(APPLICATION_STATUS.REJECTED)
const STATUS_WITHDRAWN = 'withdrawn'

const loading = ref(false)
const updating = ref(false)
const confirmingInterviewId = ref(null)
const respondingOfferId = ref(null)
const onboardingTaskUpdatingId = ref(null)
const exportingApplicationId = ref(null)
const loadingProfiles = ref(false)
const applications = ref([])
const profiles = ref([])
const activeStatus = ref(STATUS_ALL)
const editModalOpen = ref(false)
const selectedApplication = ref(null)
const selectedProfileId = ref('')
const coverLetter = ref('')
const statusTotals = reactive({
  all: 0,
  pending: 0,
  reviewed: 0,
  interview: 0,
  passed: 0,
  hired: 0,
  rejected: 0,
  withdrawn: 0,
})
const pagination = reactive({
  current_page: 1,
  last_page: 1,
  per_page: 10,
  total: 0,
  from: 0,
  to: 0,
})
const applicationListRef = ref(null)
let applicationRealtimeChannel = null

const cleanDeepLinkQueryKeys = [
  'highlight_application_id',
  'focus_section',
  'interview_round_id',
  'onboarding_plan_id',
  'onboarding_task_id',
]

const statusTabs = computed(() => [
  { value: STATUS_ALL, label: 'Tất cả', total: statusTotals.all },
  { value: STATUS_PENDING, label: 'Đang chờ', total: statusTotals.pending },
  { value: STATUS_REVIEWED, label: 'Đã xem', total: statusTotals.reviewed },
  { value: STATUS_INTERVIEW, label: 'Đã hẹn phỏng vấn', total: statusTotals.interview },
  { value: STATUS_PASSED, label: 'Qua phỏng vấn', total: statusTotals.passed },
  { value: STATUS_HIRED, label: 'Trúng tuyển', total: statusTotals.hired },
  { value: STATUS_REJECTED, label: 'Đã từ chối', total: statusTotals.rejected },
  { value: STATUS_WITHDRAWN, label: 'Đã rút', total: statusTotals.withdrawn },
])

const stats = computed(() => [
  {
    label: 'Tổng ứng tuyển',
    value: statusTotals.all,
    icon: 'send',
    iconClass: 'bg-[#2463eb]/10 text-[#2463eb]',
  },
  {
    label: 'Đang chờ duyệt',
    value: statusTotals.pending,
    icon: 'hourglass_top',
    iconClass: 'bg-amber-100 text-amber-600',
  },
  {
    label: 'Đã hẹn phỏng vấn',
    value: statusTotals.interview,
    icon: 'calendar_month',
    iconClass: 'bg-violet-100 text-violet-600',
  },
  {
    label: 'Trúng tuyển',
    value: statusTotals.hired,
    icon: 'task_alt',
    iconClass: 'bg-green-100 text-green-600',
  },
  {
    label: 'Đã từ chối',
    value: statusTotals.rejected,
    icon: 'cancel',
    iconClass: 'bg-red-100 text-red-600',
  },
])

const statusMeta = getApplicationStatusMeta
const offerStatusMeta = getOfferStatusMeta

const onboardingProgress = (application) => application?.onboarding_plan?.progress || {
  done: (application?.onboarding_plan?.tasks || []).filter((task) => task.trang_thai === 'done').length,
  total: (application?.onboarding_plan?.tasks || []).filter((task) => task.trang_thai !== 'skipped').length,
  percent: 0,
}

const formatCurrency = (value) => {
  if (value === null || value === undefined || value === '') return 'Thỏa thuận'
  return new Intl.NumberFormat('vi-VN').format(Number(value)) + ' đ'
}

const formatAppliedDate = (value) => {
  return formatHistoricalDateVN(value, 'Đang cập nhật')
}

const formatDateTime = (value) => formatDateTimeVN(value, 'Chưa lên lịch')

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

const interviewAttendanceMeta = (status) => {
  switch (Number(status)) {
    case 1:
      return {
        label: 'Đã xác nhận tham gia',
        classes: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400',
      }
    case 2:
      return {
        label: 'Báo không tham gia',
        classes: 'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400',
      }
    case 0:
      return {
        label: 'Chờ bạn xác nhận',
        classes: 'bg-violet-100 text-violet-700 dark:bg-violet-900/30 dark:text-violet-300',
      }
    default:
      return {
        label: 'Chưa có phản hồi',
        classes: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300',
      }
  }
}

const isInterviewResponseLocked = (application) => {
  return Boolean(application?.da_rut_don) || [
    APPLICATION_STATUS.INTERVIEW_PASSED,
    APPLICATION_STATUS.HIRED,
    APPLICATION_STATUS.REJECTED,
  ].includes(Number(application?.trang_thai))
}

const canRespondInterview = (application) => {
  if (isInterviewResponseLocked(application)) return false
  if (!application?.ngay_hen_phong_van || !application?.id) return false
  const interviewTime = new Date(application.ngay_hen_phong_van)
  if (Number.isNaN(interviewTime.getTime())) return false
  return interviewTime.getTime() > Date.now()
}

const sortedInterviewRounds = (application) =>
  [...(application?.interview_rounds || [])].sort((a, b) => Number(a.thu_tu || 0) - Number(b.thu_tu || 0))

const roundTypeLabel = (value) => ({
  hr: 'HR screening',
  technical: 'Technical',
  manager: 'Manager',
  final: 'Final',
  culture: 'Culture fit',
  other: 'Khác',
}[value] || value || 'Phỏng vấn')

const roundStatusMeta = (value) => {
  switch (Number(value)) {
    case 1:
      return { label: 'Hoàn thành', classes: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300' }
    case 2:
      return { label: 'Đã hủy', classes: 'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-300' }
    default:
      return { label: 'Đã lên lịch', classes: 'bg-violet-100 text-violet-700 dark:bg-violet-900/30 dark:text-violet-300' }
  }
}

const canRespondInterviewRound = (application, round) => {
  if (isInterviewResponseLocked(application)) return false
  if (!round?.ngay_hen_phong_van || !round?.id) return false
  if (Number(round.trang_thai || 0) !== 0) return false
  const interviewTime = new Date(round.ngay_hen_phong_van)
  if (Number.isNaN(interviewTime.getTime())) return false
  return interviewTime.getTime() > Date.now()
}

const canWithdrawApplication = (application) => {
  return !application?.da_rut_don
    && Number(application?.trang_thai_tham_gia_phong_van) === 2
    && !isFinalApplicationStatus(application?.trang_thai)
}

const shouldShowInterviewSection = (application) => {
  return !sortedInterviewRounds(application).length && Boolean(application?.ngay_hen_phong_van) && !isInterviewResponseLocked(application)
}

const hasOffer = (application) => Number(application?.trang_thai_offer || OFFER_STATUS.NOT_SENT) > OFFER_STATUS.NOT_SENT

const canRespondOffer = (application) => {
  if (!application?.id || application?.da_rut_don) return false
  if (Number(application?.trang_thai_offer || OFFER_STATUS.NOT_SENT) !== OFFER_STATUS.SENT) return false
  if (!application?.thoi_gian_gui_offer) return false
  if (!application?.han_phan_hoi_offer) return true
  const deadline = new Date(application.han_phan_hoi_offer)
  if (Number.isNaN(deadline.getTime())) return false
  return deadline.getTime() > Date.now()
}

const canExportDocument = (application, document) => {
  if (!application?.id) return false
  if (document === 'offer') return hasOffer(application)
  if (document === 'interview') return Boolean(
    application.ngay_hen_phong_van
    || sortedInterviewRounds(application).length
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

const editableApplication = computed(() => selectedApplication.value)
const selectedProfile = computed(() =>
  profiles.value.find((profile) => Number(profile.id) === Number(selectedProfileId.value)) || null
)

const fetchApplications = async (page = 1) => {
  loading.value = true
  try {
    const response = await applicationService.getApplications({
      page,
      per_page: pagination.per_page,
      trang_thai: activeStatus.value === STATUS_WITHDRAWN ? '' : activeStatus.value,
      da_rut_don: activeStatus.value === STATUS_WITHDRAWN ? 1 : 0,
    })
    const payload = response?.data || {}
    applications.value = payload.data || []
    pagination.current_page = payload.current_page || 1
    pagination.last_page = payload.last_page || 1
    pagination.total = payload.total || 0
    pagination.from = payload.from || 0
    pagination.to = payload.to || 0
  } catch (error) {
    applications.value = []
    pagination.current_page = 1
    pagination.last_page = 1
    pagination.total = 0
    pagination.from = 0
    pagination.to = 0
    notify.apiError(error, 'Không tải được danh sách việc đã ứng tuyển.')
  } finally {
    loading.value = false
  }
}

const fetchStatusTotals = async () => {
  try {
    const [allRes, pendingRes, reviewedRes, interviewRes, passedRes, hiredRes, rejectedRes, withdrawnRes] = await Promise.all([
      applicationService.getApplications({ page: 1, per_page: 1, da_rut_don: 0 }),
      applicationService.getApplications({ page: 1, per_page: 1, trang_thai: STATUS_PENDING, da_rut_don: 0 }),
      applicationService.getApplications({ page: 1, per_page: 1, trang_thai: STATUS_REVIEWED, da_rut_don: 0 }),
      applicationService.getApplications({ page: 1, per_page: 1, trang_thai: STATUS_INTERVIEW, da_rut_don: 0 }),
      applicationService.getApplications({ page: 1, per_page: 1, trang_thai: STATUS_PASSED, da_rut_don: 0 }),
      applicationService.getApplications({ page: 1, per_page: 1, trang_thai: STATUS_HIRED, da_rut_don: 0 }),
      applicationService.getApplications({ page: 1, per_page: 1, trang_thai: STATUS_REJECTED, da_rut_don: 0 }),
      applicationService.getApplications({ page: 1, per_page: 1, da_rut_don: 1 }),
    ])

    statusTotals.all = allRes?.data?.total || 0
    statusTotals.pending = pendingRes?.data?.total || 0
    statusTotals.reviewed = reviewedRes?.data?.total || 0
    statusTotals.interview = interviewRes?.data?.total || 0
    statusTotals.passed = passedRes?.data?.total || 0
    statusTotals.hired = hiredRes?.data?.total || 0
    statusTotals.rejected = rejectedRes?.data?.total || 0
    statusTotals.withdrawn = withdrawnRes?.data?.total || 0
  } catch {
    statusTotals.all = 0
    statusTotals.pending = 0
    statusTotals.reviewed = 0
    statusTotals.interview = 0
    statusTotals.passed = 0
    statusTotals.hired = 0
    statusTotals.rejected = 0
    statusTotals.withdrawn = 0
  }
}

const refreshApplicationsRealtime = async () => {
  if (loading.value) return
  await Promise.all([fetchApplications(pagination.current_page), fetchStatusTotals()])
}

const selectStatus = async (status) => {
  if (activeStatus.value === status) return
  activeStatus.value = status
}

const changePage = async (page) => {
  if (page < 1 || page > pagination.last_page || page === pagination.current_page) return
  await fetchApplications(page)
}

const loadProfiles = async () => {
  if (loadingProfiles.value) return

  loadingProfiles.value = true
  try {
    const response = await profileService.getProfiles({
      per_page: 100,
      sort_by: 'updated_at',
      sort_dir: 'desc',
    })
    const payload = response?.data || {}
    profiles.value = payload.data || []
  } catch (error) {
    profiles.value = []
    notify.apiError(error, 'Không tải được danh sách hồ sơ để cập nhật ứng tuyển.')
  } finally {
    loadingProfiles.value = false
  }
}

const canEditApplication = (application) => Number(application?.trang_thai) === APPLICATION_STATUS.PENDING

const openEditModal = async (application) => {
  await loadProfiles()
  selectedApplication.value = application
  selectedProfileId.value = String(application?.ho_so?.id || application?.ho_so_id || '')
  coverLetter.value = application?.thu_xin_viec || ''
  editModalOpen.value = true
}

const closeEditModal = (force = false) => {
  if (updating.value && !force) return
  editModalOpen.value = false
  selectedApplication.value = null
  selectedProfileId.value = ''
  coverLetter.value = ''
}

const submitApplicationUpdate = async () => {
  if (!selectedApplication.value?.id || !selectedProfileId.value || updating.value) return

  updating.value = true
  let updatedSuccessfully = false
  try {
    const response = await applicationService.updateApplication(selectedApplication.value.id, {
      ho_so_id: Number(selectedProfileId.value),
      thu_xin_viec: coverLetter.value.trim() || null,
    })
    const updated = response?.data || null
    applications.value = applications.value.map((item) =>
      Number(item.id) === Number(updated?.id) ? updated : item
    )
    notify.success('Đã cập nhật CV cho đơn ứng tuyển.')
    updatedSuccessfully = true
  } catch (error) {
    notify.apiError(error, 'Không thể cập nhật đơn ứng tuyển này.')
  } finally {
    updating.value = false
    if (updatedSuccessfully) {
      closeEditModal(true)
    }
  }
}

const handleInterviewResponseFeedback = async () => {
  const response = typeof route.query.interview_response === 'string' ? route.query.interview_response : ''
  const applicationId = typeof route.query.application_id === 'string' ? route.query.application_id : ''

  if (!response) return

  if (response === 'accepted') {
    notify.success('Bạn đã xác nhận tham gia phỏng vấn từ email.')
  } else if (response === 'declined') {
    notify.success('Đã ghi nhận phản hồi không thể tham gia của bạn từ email.')
  } else if (response === 'locked') {
    notify.info('Đơn ứng tuyển này đã chuyển sang giai đoạn xử lý tiếp theo nên không thể phản hồi lịch phỏng vấn nữa.')
  } else if (response === 'expired') {
    notify.warning('Liên kết phản hồi phỏng vấn đã hết hạn.')
  } else if (response === 'missing_schedule') {
    notify.info('Lịch phỏng vấn này không còn khả dụng để xác nhận.')
  } else {
    notify.error('Liên kết xác nhận phỏng vấn không hợp lệ.')
  }

  await focusApplicationDeepLink(applicationId, 'interview')

  const query = { ...route.query }
  delete query.interview_response
  delete query.application_id
  router.replace({ query })
}

const handleOfferResponseFeedback = async () => {
  const response = typeof route.query.offer_response === 'string' ? route.query.offer_response : ''
  const applicationId = typeof route.query.application_id === 'string' ? route.query.application_id : ''

  if (!response) return

  if (response === 'accepted') {
    notify.success('Bạn đã chấp nhận offer từ email.')
  } else if (response === 'declined') {
    notify.success('Đã ghi nhận phản hồi từ chối offer của bạn từ email.')
  } else if (response === 'locked') {
    notify.info('Offer này đã được phản hồi hoặc không còn khả dụng.')
  } else {
    notify.error('Liên kết phản hồi offer không hợp lệ.')
  }

  await focusApplicationDeepLink(applicationId, 'offer')

  const query = { ...route.query }
  delete query.offer_response
  delete query.application_id
  router.replace({ query })
}

const handleApplicationHighlight = async () => {
  const applicationId = typeof route.query.highlight_application_id === 'string'
    ? route.query.highlight_application_id
    : ''

  if (!applicationId) return

  await focusApplicationDeepLink(applicationId, route.query.focus_section, {
    interviewRoundId: route.query.interview_round_id,
    onboardingTaskId: route.query.onboarding_task_id,
  })

  const query = { ...route.query }
  cleanDeepLinkQueryKeys.forEach((key) => delete query[key])
  router.replace({ query })
}

const focusApplicationDeepLink = async (applicationId, section = '', options = {}) => {
  if (!applicationId) return
  await nextTick()

  const safeSection = String(section || '').trim()
  const selectors = []

  if (safeSection === 'interview' && options.interviewRoundId) {
    selectors.push(`[data-interview-round-id="${options.interviewRoundId}"]`)
  }
  if (safeSection === 'onboarding' && options.onboardingTaskId) {
    selectors.push(`[data-onboarding-task-id="${options.onboardingTaskId}"]`)
  }
  if (safeSection) {
    selectors.push(`[data-application-section="${applicationId}:${safeSection}"]`)
  }
  selectors.push(`[data-application-id="${applicationId}"]`)

  const target = selectors
    .map((selector) => applicationListRef.value?.querySelector(selector))
    .find(Boolean)

  if (target) {
    target.scrollIntoView({ behavior: 'smooth', block: 'center' })
    target.classList.add('ring-2', 'ring-[#2463eb]', 'ring-offset-2', 'ring-offset-white', 'dark:ring-offset-slate-950')

    window.setTimeout(() => {
      target.classList.remove('ring-2', 'ring-[#2463eb]', 'ring-offset-2', 'ring-offset-white', 'dark:ring-offset-slate-950')
    }, 2800)
  } else {
    notify.info('Đơn ứng tuyển cần xem không nằm trong trang hiện tại. Bạn có thể tìm trong danh sách hoặc đổi bộ lọc.')
  }
}

const respondInterview = async (application, attendanceStatus) => {
  if (!application?.id || confirmingInterviewId.value) return

  confirmingInterviewId.value = application.id
  try {
    const response = await applicationService.confirmInterviewAttendance(application.id, attendanceStatus)
    const updated = response?.data || null
    applications.value = applications.value.map((item) =>
      Number(item.id) === Number(updated?.id) ? updated : item
    )
    notify.success(
      Number(attendanceStatus) === 1
        ? 'Bạn đã xác nhận tham gia buổi phỏng vấn.'
        : 'Đã ghi nhận phản hồi không thể tham gia của bạn.'
    )
  } catch (error) {
    notify.apiError(error, 'Không thể cập nhật phản hồi phỏng vấn.')
  } finally {
    confirmingInterviewId.value = null
  }
}

const respondInterviewRound = async (application, round, attendanceStatus) => {
  if (!application?.id || !round?.id || confirmingInterviewId.value) return

  confirmingInterviewId.value = `${application.id}-${round.id}`
  try {
    const response = await applicationService.confirmInterviewRoundAttendance(application.id, round.id, attendanceStatus)
    const updated = response?.data || null
    applications.value = applications.value.map((item) =>
      Number(item.id) === Number(updated?.id) ? updated : item
    )
    notify.success(
      Number(attendanceStatus) === 1
        ? 'Bạn đã xác nhận tham gia vòng phỏng vấn.'
        : 'Đã ghi nhận phản hồi không thể tham gia vòng này.'
    )
  } catch (error) {
    notify.apiError(error, 'Không thể cập nhật phản hồi vòng phỏng vấn.')
  } finally {
    confirmingInterviewId.value = null
  }
}

const withdrawApplication = async (application) => {
  if (!application?.id || confirmingInterviewId.value) return

  confirmingInterviewId.value = application.id
  try {
    await applicationService.withdrawApplication(application.id)
    notify.success('Đã rút đơn ứng tuyển và chuyển sang mục Đã rút.')
    await Promise.all([fetchApplications(pagination.current_page), fetchStatusTotals()])
  } catch (error) {
    notify.apiError(error, 'Không thể rút đơn ứng tuyển này.')
  } finally {
    confirmingInterviewId.value = null
  }
}

const respondOffer = async (application, action) => {
  if (!application?.id || respondingOfferId.value) return

  respondingOfferId.value = application.id
  try {
    const response = await applicationService.respondOffer(application.id, action)
    const updated = response?.data || null
    applications.value = applications.value.map((item) =>
      Number(item.id) === Number(updated?.id) ? updated : item
    )
    notify.success(response?.message || (action === 'accept' ? 'Bạn đã chấp nhận offer.' : 'Đã từ chối offer.'))
    await fetchStatusTotals()
  } catch (error) {
    notify.apiError(error, 'Không thể phản hồi offer này.')
  } finally {
    respondingOfferId.value = null
  }
}

const updateOnboardingTask = async (application, task, status) => {
  if (!application?.id || !task?.id || onboardingTaskUpdatingId.value) return
  onboardingTaskUpdatingId.value = task.id
  try {
    const response = await applicationService.updateOnboardingTask(application.id, task.id, status)
    const plan = response?.data || null
    applications.value = applications.value.map((item) =>
      Number(item.id) === Number(application.id)
        ? { ...item, onboarding_plan: plan }
        : item
    )
    notify.success('Đã cập nhật checklist onboarding.')
  } catch (error) {
    notify.apiError(error, 'Không cập nhật được checklist onboarding.')
  } finally {
    onboardingTaskUpdatingId.value = null
  }
}

const downloadApplicationExport = async (application, document = 'full') => {
  if (!application?.id || exportingApplicationId.value) return
  exportingApplicationId.value = `${application.id}:${document}`
  try {
    const response = await applicationService.downloadExport(application.id, document)
    triggerDownload(response.blob, response.filename)
    notify.success('Đã tạo file PDF từ server.')
  } catch (error) {
    notify.apiError(error, 'Không tải được file PDF.')
  } finally {
    exportingApplicationId.value = null
  }
}

watch(activeStatus, async () => {
  await fetchApplications(1)
})

onMounted(async () => {
  await Promise.all([fetchApplications(), fetchStatusTotals()])
  await handleInterviewResponseFeedback()
  await handleOfferResponseFeedback()
  await handleApplicationHighlight()

  const user = getStoredUser()
  if (user?.id) {
    applicationRealtimeChannel = connectPrivateChannel(`user.${user.id}`)
    applicationRealtimeChannel?.listen('.application.changed', (event) => {
      const title = event?.payload?.tin_tuyen_dung_tieu_de
      notify.info(title ? `Ứng tuyển "${title}" vừa được cập nhật realtime.` : 'Đơn ứng tuyển của bạn vừa được cập nhật realtime.')
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
</script>

<template>
  <div>
    <div class="mb-8 flex justify-between items-end">
      <div>
        <h1 class="text-2xl font-bold text-slate-900 dark:text-white">Việc đã ứng tuyển</h1>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Theo dõi trạng thái hồ sơ ứng tuyển của bạn.</p>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
      <div
        v-for="stat in stats"
        :key="stat.label"
        class="bg-white dark:bg-slate-900 p-5 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800"
      >
        <div class="flex items-center justify-between mb-2">
          <p class="text-sm font-medium text-slate-500 dark:text-slate-400">{{ stat.label }}</p>
          <div class="p-2 rounded-lg" :class="stat.iconClass">
            <span class="material-symbols-outlined">{{ stat.icon }}</span>
          </div>
        </div>
        <h3 class="text-2xl font-bold">{{ stat.value }}</h3>
      </div>
    </div>

    <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
      <div class="flex border-b border-slate-200 dark:border-slate-800 px-6 gap-6 overflow-x-auto">
        <button
          v-for="tab in statusTabs"
          :key="tab.value || 'all'"
          class="flex items-center border-b-2 pb-3 pt-4 font-medium text-sm whitespace-nowrap transition"
          :class="activeStatus === tab.value
            ? 'border-[#2463eb] text-[#2463eb] font-bold'
            : 'border-transparent text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200'"
          type="button"
          @click="selectStatus(tab.value)"
        >
          {{ tab.label }}
          <span
            class="ml-2 px-2 py-0.5 rounded text-[10px]"
            :class="activeStatus === tab.value ? 'bg-[#2463eb]/10' : 'bg-slate-100 dark:bg-slate-800'"
          >
            {{ tab.total }}
          </span>
        </button>
      </div>

      <div v-if="loading" class="divide-y divide-slate-100 dark:divide-slate-800">
        <div
          v-for="index in 4"
          :key="index"
          class="p-5"
        >
          <div class="h-24 animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800"></div>
        </div>
      </div>

      <div
        v-else-if="!applications.length"
        class="px-6 py-16 text-center"
      >
        <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-slate-100 dark:bg-slate-800">
          <span class="material-symbols-outlined text-3xl text-slate-500">send</span>
        </div>
        <h2 class="mt-5 text-xl font-bold text-slate-900 dark:text-white">Chưa có ứng tuyển nào</h2>
        <p class="mx-auto mt-3 max-w-xl text-sm leading-7 text-slate-500 dark:text-slate-400">
          {{ activeStatus === STATUS_WITHDRAWN
            ? 'Bạn chưa rút đơn ứng tuyển nào.'
            : 'Bạn chưa nộp hồ sơ vào tin tuyển dụng nào trong nhóm trạng thái này.' }}
        </p>
        <RouterLink
          :to="{ name: 'JobSearch' }"
          class="mt-6 inline-flex rounded-xl bg-[#2463eb] px-5 py-3 text-sm font-bold text-white transition hover:bg-blue-700"
        >
          Tìm việc để ứng tuyển
        </RouterLink>
      </div>

      <div ref="applicationListRef" v-else class="divide-y divide-slate-100 dark:divide-slate-800">
        <div
          v-for="application in applications"
          :key="application.id"
          :data-application-id="application.id"
          class="p-5 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors"
        >
          <div class="flex flex-col gap-4">
            <div class="flex flex-col md:flex-row md:items-center gap-4 justify-between">
              <div class="flex items-center gap-4 flex-1">
              <div class="size-12 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center shrink-0">
                <span class="material-symbols-outlined text-slate-500">domain</span>
              </div>
                <div class="flex-1">
                  <h3 class="font-bold text-slate-900 dark:text-white">
                    {{ application.tin_tuyen_dung?.tieu_de || 'Tin tuyển dụng đang cập nhật' }}
                  </h3>
                  <p class="text-sm text-slate-500 dark:text-slate-400">
                    {{ application.tin_tuyen_dung?.cong_ty?.ten_cong_ty || 'Công ty đang cập nhật' }}
                    <span v-if="application.tin_tuyen_dung?.dia_diem_lam_viec">• {{ application.tin_tuyen_dung.dia_diem_lam_viec }}</span>
                  </p>
                  <div class="mt-1.5 flex flex-wrap items-center gap-4 text-xs text-slate-400 dark:text-slate-500">
                    <span class="flex items-center gap-1">
                      <span class="material-symbols-outlined text-[14px]">calendar_today</span>
                      Nộp ngày {{ formatAppliedDate(application.thoi_gian_ung_tuyen) }}
                    </span>
                    <span class="flex items-center gap-1">
                      <span class="material-symbols-outlined text-[14px]">description</span>
                      {{ application.ho_so?.tieu_de_ho_so || `Hồ sơ #${application.ho_so_id}` }}
                    </span>
                    <span class="flex items-center gap-1" v-if="application.tin_tuyen_dung?.muc_luong_tu">
                      <span class="material-symbols-outlined text-[14px]">payments</span>
                      {{ formatCurrency(application.tin_tuyen_dung.muc_luong_tu) }}
                    </span>
                  </div>
                </div>
              </div>

              <div class="flex items-center gap-4 shrink-0">
                <span
                  class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold"
                  :class="statusMeta(application.trang_thai).classes"
                >
                  <span class="size-1.5 rounded-full" :class="statusMeta(application.trang_thai).dot"></span>
                  {{ statusMeta(application.trang_thai).label }}
                </span>
                <span
                  v-if="hasOffer(application)"
                  class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold"
                  :class="offerStatusMeta(application.trang_thai_offer).classes"
                >
                  <span class="size-1.5 rounded-full" :class="offerStatusMeta(application.trang_thai_offer).dot"></span>
                  {{ offerStatusMeta(application.trang_thai_offer).label }}
                </span>
                <span
                  v-if="application.da_rut_don"
                  class="inline-flex items-center rounded-full bg-slate-200 px-2.5 py-1 text-xs font-bold text-slate-700 dark:bg-slate-700 dark:text-slate-200"
                >
                  Đã rút
                </span>
                <button
                  v-if="canEditApplication(application)"
                  class="inline-flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
                  type="button"
                  @click="openEditModal(application)"
                >
                  <span class="material-symbols-outlined text-[16px]">edit_square</span>
                  Cập nhật CV
                </button>
                <button
                  class="inline-flex items-center gap-2 rounded-lg border border-blue-200 px-3 py-2 text-xs font-semibold text-blue-700 transition hover:bg-blue-50 disabled:opacity-60 dark:border-blue-500/20 dark:text-blue-300 dark:hover:bg-blue-500/10"
                  :disabled="exportingApplicationId === `${application.id}:full`"
                  type="button"
                  @click="downloadApplicationExport(application, 'full')"
                >
                  <span class="material-symbols-outlined text-[16px]">picture_as_pdf</span>
                  {{ exportingApplicationId === `${application.id}:full` ? 'Đang tạo...' : 'PDF' }}
                </button>
                <RouterLink
                  v-if="application.tin_tuyen_dung?.id"
                  :to="{ name: 'JobDetail', params: { id: application.tin_tuyen_dung.id } }"
                  class="text-slate-400 transition hover:text-slate-600 dark:text-slate-500 dark:hover:text-slate-300"
                >
                  <span class="material-symbols-outlined">chevron_right</span>
                </RouterLink>
              </div>
            </div>

            <div
              v-if="application.application_timeline?.length"
              :data-application-section="`${application.id}:timeline`"
              class="rounded-2xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-950/40"
            >
              <div class="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p class="text-sm font-bold text-slate-900 dark:text-white">Timeline ứng tuyển tổng hợp</p>
                  <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">
                    Nộp hồ sơ, phỏng vấn, offer và onboarding trong một luồng.
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

            <div
              v-if="sortedInterviewRounds(application).length"
              :data-application-section="`${application.id}:interview`"
              class="rounded-2xl border border-violet-200 bg-violet-50/70 p-4 dark:border-violet-500/20 dark:bg-violet-500/10"
            >
              <div class="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p class="text-sm font-bold text-slate-900 dark:text-white">Timeline phỏng vấn</p>
                  <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">
                    {{ sortedInterviewRounds(application).length }} vòng trong quy trình tuyển dụng.
                  </p>
                </div>
                <button
                  v-if="canExportDocument(application, 'interview')"
                  class="inline-flex items-center gap-2 rounded-xl border border-violet-200 bg-white px-3 py-2 text-xs font-bold text-violet-700 transition hover:bg-violet-50 disabled:opacity-60 dark:border-violet-500/20 dark:bg-slate-950/40 dark:text-violet-300"
                  :disabled="exportingApplicationId === `${application.id}:interview`"
                  type="button"
                  @click="downloadApplicationExport(application, 'interview')"
                >
                  <span class="material-symbols-outlined text-[16px]">picture_as_pdf</span>
                  {{ exportingApplicationId === `${application.id}:interview` ? 'Đang tạo...' : 'PDF phỏng vấn' }}
                </button>
              </div>

              <div class="mt-4 space-y-3">
                <div
                  v-for="round in sortedInterviewRounds(application)"
                  :key="round.id"
                  :data-interview-round-id="round.id"
                  class="rounded-2xl bg-white p-4 dark:bg-slate-950/40"
                >
                  <div class="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                    <div>
                      <div class="flex flex-wrap items-center gap-2">
                        <p class="font-bold text-slate-900 dark:text-white">{{ round.ten_vong }}</p>
                        <span class="rounded-full px-2.5 py-1 text-[11px] font-bold" :class="roundStatusMeta(round.trang_thai).classes">
                          {{ roundStatusMeta(round.trang_thai).label }}
                        </span>
                        <span class="rounded-full px-2.5 py-1 text-[11px] font-bold" :class="interviewAttendanceMeta(round.trang_thai_tham_gia).classes">
                          {{ interviewAttendanceMeta(round.trang_thai_tham_gia).label }}
                        </span>
                      </div>
                      <p class="mt-2 text-sm text-slate-600 dark:text-slate-300">
                        {{ roundTypeLabel(round.loai_vong) }} • {{ formatDateTime(round.ngay_hen_phong_van) }}
                        <span v-if="round.hinh_thuc_phong_van">• {{ round.hinh_thuc_phong_van === 'online' ? 'Online' : round.hinh_thuc_phong_van === 'offline' ? 'Trực tiếp' : 'Điện thoại' }}</span>
                      </p>
                      <p v-if="round.nguoi_phong_van" class="mt-1 text-xs text-slate-500 dark:text-slate-400">
                        Người phỏng vấn: {{ round.nguoi_phong_van }}
                      </p>
                      <p v-if="round.link_phong_van" class="mt-1 break-words text-xs text-slate-500 dark:text-slate-400">
                        Link / địa điểm: {{ round.link_phong_van }}
                      </p>
                      <p v-if="round.ket_qua" class="mt-2 text-xs font-semibold text-slate-600 dark:text-slate-300">
                        Kết quả: {{ round.ket_qua }}
                      </p>
                    </div>

                    <div
                      v-if="canRespondInterviewRound(application, round)"
                      class="flex flex-wrap items-center gap-2 lg:justify-end"
                    >
                      <button
                        class="inline-flex items-center justify-center rounded-xl border border-emerald-200 bg-white px-4 py-2 text-xs font-bold text-emerald-700 transition hover:bg-emerald-50 disabled:opacity-60 dark:border-emerald-500/20 dark:bg-slate-950/40 dark:text-emerald-300"
                        :disabled="confirmingInterviewId === `${application.id}-${round.id}`"
                        type="button"
                        @click="respondInterviewRound(application, round, 1)"
                      >
                        {{ confirmingInterviewId === `${application.id}-${round.id}` ? 'Đang lưu...' : 'Xác nhận' }}
                      </button>
                      <button
                        class="inline-flex items-center justify-center rounded-xl border border-rose-200 bg-white px-4 py-2 text-xs font-bold text-rose-700 transition hover:bg-rose-50 disabled:opacity-60 dark:border-rose-500/20 dark:bg-slate-950/40 dark:text-rose-300"
                        :disabled="confirmingInterviewId === `${application.id}-${round.id}`"
                        type="button"
                        @click="respondInterviewRound(application, round, 2)"
                      >
                        Không tham gia
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div
              v-if="shouldShowInterviewSection(application)"
              :data-application-section="`${application.id}:interview`"
              class="rounded-2xl border border-violet-200 bg-violet-50/70 p-4 dark:border-violet-500/20 dark:bg-violet-500/10"
            >
              <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                <div class="space-y-2">
                  <div class="flex flex-wrap items-center gap-2">
                    <p class="text-sm font-bold text-slate-900 dark:text-white">Lịch phỏng vấn</p>
                    <span
                      class="inline-flex rounded-full px-2.5 py-1 text-[11px] font-bold"
                      :class="interviewAttendanceMeta(application.trang_thai_tham_gia_phong_van).classes"
                    >
                      {{ interviewAttendanceMeta(application.trang_thai_tham_gia_phong_van).label }}
                    </span>
                  </div>
                  <p class="text-sm text-slate-600 dark:text-slate-300">
                    {{ formatDateTime(application.ngay_hen_phong_van) }}
                    <span v-if="application.hinh_thuc_phong_van">• {{ application.hinh_thuc_phong_van === 'online' ? 'Online' : application.hinh_thuc_phong_van === 'offline' ? 'Trực tiếp' : 'Điện thoại' }}</span>
                  </p>
                  <p v-if="application.nguoi_phong_van" class="text-xs text-slate-500 dark:text-slate-400">
                    Người phỏng vấn: {{ application.nguoi_phong_van }}
                  </p>
                  <p v-if="application.link_phong_van" class="text-xs text-slate-500 dark:text-slate-400 break-words">
                    Link / địa điểm: {{ application.link_phong_van }}
                  </p>
                </div>

                <div
                  v-if="canRespondInterview(application) || canExportDocument(application, 'interview')"
                  class="flex flex-wrap items-center gap-2 lg:justify-end"
                >
                  <button
                    v-if="canExportDocument(application, 'interview')"
                    class="inline-flex items-center justify-center rounded-xl border border-violet-200 bg-white px-4 py-2 text-xs font-bold text-violet-700 transition hover:bg-violet-50 disabled:opacity-60 dark:border-violet-500/20 dark:bg-slate-950/40 dark:text-violet-300"
                    :disabled="exportingApplicationId === `${application.id}:interview`"
                    type="button"
                    @click="downloadApplicationExport(application, 'interview')"
                  >
                    {{ exportingApplicationId === `${application.id}:interview` ? 'Đang tạo...' : 'PDF phỏng vấn' }}
                  </button>
                  <button
                    v-if="canRespondInterview(application)"
                    class="inline-flex items-center justify-center rounded-xl border border-emerald-200 bg-white px-4 py-2 text-xs font-bold text-emerald-700 transition hover:bg-emerald-50 disabled:opacity-60 dark:border-emerald-500/20 dark:bg-slate-950/40 dark:text-emerald-300 dark:hover:bg-emerald-500/10"
                    :disabled="confirmingInterviewId === application.id"
                    type="button"
                    @click="respondInterview(application, 1)"
                  >
                    {{ confirmingInterviewId === application.id && Number(application.trang_thai_tham_gia_phong_van) !== 2 ? 'Đang lưu...' : 'Xác nhận tham gia' }}
                  </button>
                  <button
                    v-if="canRespondInterview(application)"
                    class="inline-flex items-center justify-center rounded-xl border border-rose-200 bg-white px-4 py-2 text-xs font-bold text-rose-700 transition hover:bg-rose-50 disabled:opacity-60 dark:border-rose-500/20 dark:bg-slate-950/40 dark:text-rose-300 dark:hover:bg-rose-500/10"
                    :disabled="confirmingInterviewId === application.id"
                    type="button"
                    @click="respondInterview(application, 2)"
                  >
                    {{ confirmingInterviewId === application.id && Number(application.trang_thai_tham_gia_phong_van) === 2 ? 'Đang lưu...' : 'Không tham gia được' }}
                  </button>
                </div>
              </div>

              <div
                v-if="canWithdrawApplication(application) || application.da_rut_don"
                class="mt-3 flex flex-wrap items-center gap-2"
              >
                <button
                  v-if="canWithdrawApplication(application)"
                  class="inline-flex items-center justify-center rounded-xl border border-slate-300 bg-white px-4 py-2 text-xs font-bold text-slate-700 transition hover:bg-slate-50 disabled:opacity-60 dark:border-slate-600 dark:bg-slate-950/40 dark:text-slate-200 dark:hover:bg-slate-800"
                  :disabled="confirmingInterviewId === application.id"
                  type="button"
                  @click="withdrawApplication(application)"
                >
                  {{ confirmingInterviewId === application.id ? 'Đang xử lý...' : 'Rút đơn ứng tuyển' }}
                </button>
                <p
                  v-if="application.da_rut_don"
                  class="text-xs text-slate-500 dark:text-slate-400"
                >
                  Đã rút lúc {{ formatDateTime(application.thoi_gian_rut_don) }}
                </p>
              </div>
            </div>

            <div
              v-if="hasOffer(application)"
              :data-application-section="`${application.id}:offer`"
              class="rounded-2xl border border-emerald-200 bg-emerald-50/80 p-4 dark:border-emerald-500/20 dark:bg-emerald-500/10"
            >
              <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                <div class="space-y-2">
                  <div class="flex flex-wrap items-center gap-2">
                    <p class="text-sm font-bold text-slate-900 dark:text-white">Offer / nhận việc</p>
                    <span
                      class="inline-flex rounded-full px-2.5 py-1 text-[11px] font-bold"
                      :class="offerStatusMeta(application.trang_thai_offer).classes"
                    >
                      {{ offerStatusMeta(application.trang_thai_offer).label }}
                    </span>
                  </div>
                  <p class="text-sm text-slate-600 dark:text-slate-300">
                    Gửi lúc {{ formatDateTime(application.thoi_gian_gui_offer) }}
                    <span v-if="application.han_phan_hoi_offer">• Hạn phản hồi {{ formatDateTime(application.han_phan_hoi_offer) }}</span>
                  </p>
                  <p v-if="application.ghi_chu_offer" class="text-sm leading-6 text-slate-600 dark:text-slate-300">
                    {{ application.ghi_chu_offer }}
                  </p>
                  <a
                    v-if="application.link_offer"
                    :href="application.link_offer"
                    class="inline-flex text-xs font-bold text-emerald-700 underline underline-offset-4 dark:text-emerald-300"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Xem tài liệu offer
                  </a>
                  <button
                    v-if="canExportDocument(application, 'offer')"
                    class="ml-0 inline-flex text-xs font-bold text-emerald-700 underline underline-offset-4 disabled:opacity-60 dark:text-emerald-300"
                    :disabled="exportingApplicationId === `${application.id}:offer`"
                    type="button"
                    @click="downloadApplicationExport(application, 'offer')"
                  >
                    {{ exportingApplicationId === `${application.id}:offer` ? 'Đang tạo offer PDF...' : 'Tải offer PDF' }}
                  </button>
                  <p v-if="application.thoi_gian_phan_hoi_offer" class="text-xs text-slate-500 dark:text-slate-400">
                    Đã phản hồi lúc {{ formatDateTime(application.thoi_gian_phan_hoi_offer) }}
                  </p>
                </div>

                <div
                  v-if="canRespondOffer(application)"
                  class="flex flex-wrap items-center gap-2 lg:justify-end"
                >
                  <button
                    class="inline-flex items-center justify-center rounded-xl bg-emerald-600 px-4 py-2 text-xs font-bold text-white transition hover:bg-emerald-700 disabled:opacity-60"
                    :disabled="respondingOfferId === application.id"
                    type="button"
                    @click="respondOffer(application, 'accept')"
                  >
                    {{ respondingOfferId === application.id ? 'Đang lưu...' : 'Chấp nhận offer' }}
                  </button>
                  <button
                    class="inline-flex items-center justify-center rounded-xl border border-rose-200 bg-white px-4 py-2 text-xs font-bold text-rose-700 transition hover:bg-rose-50 disabled:opacity-60 dark:border-rose-500/20 dark:bg-slate-950/40 dark:text-rose-300 dark:hover:bg-rose-500/10"
                    :disabled="respondingOfferId === application.id"
                    type="button"
                    @click="respondOffer(application, 'decline')"
                  >
                    {{ respondingOfferId === application.id ? 'Đang lưu...' : 'Từ chối offer' }}
                  </button>
                </div>
              </div>
            </div>

            <div
              v-if="application.onboarding_plan"
              :data-application-section="`${application.id}:onboarding`"
              class="rounded-2xl border border-blue-200 bg-blue-50/80 p-4 dark:border-blue-500/20 dark:bg-blue-500/10"
            >
              <div class="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                <div>
                  <p class="text-sm font-bold text-slate-900 dark:text-white">Onboarding nhận việc</p>
                  <p class="mt-1 text-sm text-slate-600 dark:text-slate-300">
                    Ngày bắt đầu: {{ application.onboarding_plan.ngay_bat_dau || 'HR sẽ cập nhật' }}
                    <span v-if="application.onboarding_plan.dia_diem_lam_viec">• {{ application.onboarding_plan.dia_diem_lam_viec }}</span>
                  </p>
                  <p v-if="application.onboarding_plan.loi_chao_mung" class="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-300">
                    {{ application.onboarding_plan.loi_chao_mung }}
                  </p>
                </div>
                <div class="text-left lg:text-right">
                  <p class="text-2xl font-black text-[#2463eb]">{{ onboardingProgress(application).percent || 0 }}%</p>
                  <p class="text-xs font-bold text-slate-500 dark:text-slate-400">
                    {{ onboardingProgress(application).done }}/{{ onboardingProgress(application).total }} hoàn tất
                  </p>
                  <button
                    v-if="canExportDocument(application, 'onboarding')"
                    class="mt-2 text-xs font-bold text-blue-700 underline underline-offset-4 disabled:opacity-60 dark:text-blue-300"
                    :disabled="exportingApplicationId === `${application.id}:onboarding`"
                    type="button"
                    @click="downloadApplicationExport(application, 'onboarding')"
                  >
                    {{ exportingApplicationId === `${application.id}:onboarding` ? 'Đang tạo PDF...' : 'Tải PDF' }}
                  </button>
                </div>
              </div>

              <div v-if="application.onboarding_plan.tai_lieu_can_chuan_bi?.length" class="mt-4">
                <p class="text-xs font-bold uppercase tracking-[0.18em] text-blue-700 dark:text-blue-300">Tài liệu cần chuẩn bị</p>
                <div class="mt-2 flex flex-wrap gap-2">
                  <span
                    v-for="doc in application.onboarding_plan.tai_lieu_can_chuan_bi"
                    :key="doc"
                    class="rounded-full bg-white px-3 py-1 text-xs font-semibold text-slate-600 dark:bg-slate-950/50 dark:text-slate-300"
                  >
                    {{ doc }}
                  </span>
                </div>
              </div>

              <div class="mt-4 space-y-2">
                <div
                  v-for="task in application.onboarding_plan.tasks || []"
                  :key="task.id"
                  :data-onboarding-task-id="task.id"
                  class="flex flex-col gap-3 rounded-xl bg-white px-4 py-3 dark:bg-slate-950/50 md:flex-row md:items-center md:justify-between"
                >
                  <div>
                    <p class="text-sm font-bold text-slate-900 dark:text-white">{{ task.tieu_de }}</p>
                    <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">
                      {{ task.nguoi_phu_trach === 'candidate' ? 'Bạn phụ trách' : 'HR phụ trách' }}
                      <span v-if="task.han_hoan_tat">• hạn {{ task.han_hoan_tat }}</span>
                    </p>
                  </div>
                  <div v-if="task.nguoi_phu_trach === 'candidate'" class="flex flex-wrap gap-2">
                    <button
                      class="rounded-xl border border-slate-200 px-3 py-2 text-xs font-bold text-slate-600 transition hover:bg-slate-50 disabled:opacity-60 dark:border-slate-700 dark:text-slate-300"
                      :disabled="onboardingTaskUpdatingId === task.id || task.trang_thai === 'in_progress'"
                      type="button"
                      @click="updateOnboardingTask(application, task, 'in_progress')"
                    >
                      Đang làm
                    </button>
                    <button
                      class="rounded-xl bg-blue-600 px-3 py-2 text-xs font-bold text-white transition hover:bg-blue-700 disabled:opacity-60"
                      :disabled="onboardingTaskUpdatingId === task.id || task.trang_thai === 'done'"
                      type="button"
                      @click="updateOnboardingTask(application, task, 'done')"
                    >
                      Hoàn tất
                    </button>
                  </div>
                  <span v-else class="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-500 dark:bg-slate-800 dark:text-slate-300">
                    {{ task.trang_thai === 'done' ? 'Hoàn tất' : task.trang_thai === 'in_progress' ? 'Đang làm' : 'Chờ HR' }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div
        v-if="!loading && applications.length && pagination.last_page > 1"
        class="flex items-center justify-between border-t border-slate-200 dark:border-slate-800 px-6 py-4"
      >
          <p class="text-xs text-slate-500 dark:text-slate-400">
          Hiển thị {{ pagination.from }}-{{ pagination.to }} của {{ pagination.total }} kết quả
        </p>
        <div class="flex gap-2">
          <button
            class="h-8 w-8 flex items-center justify-center rounded-lg border border-slate-200 dark:border-slate-800 text-slate-500 disabled:opacity-50"
            :disabled="pagination.current_page === 1"
            type="button"
            @click="changePage(pagination.current_page - 1)"
          >
            <span class="material-symbols-outlined text-[18px]">chevron_left</span>
          </button>
          <button
            v-for="page in pagination.last_page"
            :key="page"
            class="h-8 w-8 flex items-center justify-center rounded-lg font-bold text-xs transition"
            :class="page === pagination.current_page
              ? 'bg-[#2463eb] text-white'
              : 'border border-slate-200 dark:border-slate-800 text-slate-600 hover:bg-slate-50 dark:text-slate-300 dark:hover:bg-slate-800'"
            type="button"
            @click="changePage(page)"
          >
            {{ page }}
          </button>
          <button
            class="h-8 w-8 flex items-center justify-center rounded-lg border border-slate-200 dark:border-slate-800 text-slate-500 disabled:opacity-50"
            :disabled="pagination.current_page === pagination.last_page"
            type="button"
            @click="changePage(pagination.current_page + 1)"
          >
            <span class="material-symbols-outlined text-[18px]">chevron_right</span>
          </button>
        </div>
      </div>
    </div>

    <div
      v-if="editModalOpen"
      class="fixed inset-0 z-50 overflow-y-auto bg-slate-950/55 backdrop-blur-sm"
      @click.self="closeEditModal"
    >
      <div class="flex min-h-full items-center justify-center px-4 py-6">
        <div class="flex max-h-[calc(100vh-3rem)] w-full max-w-2xl flex-col overflow-hidden rounded-[28px] border border-slate-200 bg-white shadow-2xl dark:border-slate-800 dark:bg-slate-950">
        <div class="flex items-start justify-between border-b border-slate-100 px-6 py-5 dark:border-slate-800">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.28em] text-blue-500">Cập nhật ứng tuyển</p>
            <h3 class="mt-2 text-2xl font-bold text-slate-900 dark:text-white">{{ editableApplication?.tin_tuyen_dung?.tieu_de }}</h3>
            <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">
              Bạn chỉ có thể đổi CV khi đơn vẫn đang chờ duyệt.
            </p>
          </div>
          <button
            class="rounded-full p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-900 dark:hover:text-slate-200"
            type="button"
            @click="closeEditModal"
          >
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>

        <div class="min-h-0 flex-1 space-y-5 overflow-y-auto px-6 py-6">
          <div v-if="loadingProfiles" class="rounded-2xl bg-slate-50 px-4 py-5 text-sm text-slate-500 dark:bg-slate-900 dark:text-slate-400">
            Đang tải danh sách hồ sơ...
          </div>

          <template v-else>
            <div>
              <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-300">Chọn hồ sơ thay thế</label>
              <select
                v-model="selectedProfileId"
                class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-200 dark:focus:ring-blue-500/20"
              >
                <option value="" disabled>Chọn hồ sơ của bạn</option>
                <option v-for="profile in profiles" :key="profile.id" :value="String(profile.id)">
                  {{ profile.tieu_de_ho_so || `Hồ sơ #${profile.id}` }}
                </option>
              </select>
            </div>

            <div v-if="selectedProfile" class="rounded-2xl bg-slate-50 px-4 py-4 text-sm text-slate-600 dark:bg-slate-900 dark:text-slate-400">
              <p class="font-semibold text-slate-800 dark:text-slate-200">{{ selectedProfile.tieu_de_ho_so || `Hồ sơ #${selectedProfile.id}` }}</p>
              <p class="mt-1">
                Kinh nghiệm: {{ selectedProfile.kinh_nghiem_nam || 0 }} năm
                <span v-if="selectedProfile.vi_tri_mong_muon">• Mục tiêu: {{ selectedProfile.vi_tri_mong_muon }}</span>
              </p>
            </div>

            <div>
              <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-300">Thư xin việc hiện tại</label>
              <textarea
                v-model="coverLetter"
                rows="5"
                maxlength="5000"
                class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-200 dark:focus:ring-blue-500/20"
                placeholder="Bạn có thể chỉnh lại thư xin việc để phù hợp với hồ sơ mới."
              />
              <div class="mt-2 text-right text-xs text-slate-400 dark:text-slate-500">{{ coverLetter.length }}/5000</div>
            </div>
          </template>
        </div>

        <div class="flex flex-col gap-3 border-t border-slate-100 px-6 py-5 dark:border-slate-800 sm:flex-row sm:justify-end">
          <button
            class="rounded-2xl border border-slate-200 px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-900"
            type="button"
            @click="closeEditModal"
          >
            Hủy
          </button>
          <button
            class="rounded-2xl bg-blue-600 px-5 py-3 text-sm font-bold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-300"
            :disabled="!selectedProfileId || updating || loadingProfiles"
            type="button"
            @click="submitApplicationUpdate"
          >
            {{ updating ? 'Đang cập nhật...' : 'Lưu thay đổi' }}
          </button>
        </div>
      </div>
      </div>
    </div>
  </div>
</template>
