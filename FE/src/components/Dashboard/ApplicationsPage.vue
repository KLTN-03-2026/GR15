<script setup>
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { applicationService, profileService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'
import { formatDateTimeVN, formatDateVN, formatHistoricalDateVN } from '@/utils/dateTime'
import {
  APPLICATION_STATUS,
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

const formatCurrency = (value) => {
  if (value === null || value === undefined || value === '') return 'Thỏa thuận'
  return new Intl.NumberFormat('vi-VN').format(Number(value)) + ' đ'
}

const formatAppliedDate = (value) => {
  return formatHistoricalDateVN(value, 'Đang cập nhật')
}

const formatDateTime = (value) => formatDateTimeVN(value, 'Chưa lên lịch')

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

const canWithdrawApplication = (application) => {
  return !application?.da_rut_don
    && Number(application?.trang_thai_tham_gia_phong_van) === 2
    && !isFinalApplicationStatus(application?.trang_thai)
}

const shouldShowInterviewSection = (application) => {
  return Boolean(application?.ngay_hen_phong_van) && !isInterviewResponseLocked(application)
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

  await nextTick()

  if (applicationId && applicationListRef.value) {
    const target = applicationListRef.value.querySelector(`[data-application-id="${applicationId}"]`)
    target?.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }

  const query = { ...route.query }
  delete query.interview_response
  delete query.application_id
  router.replace({ query })
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

watch(activeStatus, async () => {
  await fetchApplications(1)
})

onMounted(async () => {
  await Promise.all([fetchApplications(), fetchStatusTotals()])
  await handleInterviewResponseFeedback()
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
                    <span class="flex items-center gap-1" v-if="application.tin_tuyen_dung?.muc_luong">
                      <span class="material-symbols-outlined text-[14px]">payments</span>
                      {{ formatCurrency(application.tin_tuyen_dung.muc_luong) }}
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
              v-if="shouldShowInterviewSection(application)"
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
                  v-if="canRespondInterview(application)"
                  class="flex flex-wrap items-center gap-2 lg:justify-end"
                >
                  <button
                    class="inline-flex items-center justify-center rounded-xl border border-emerald-200 bg-white px-4 py-2 text-xs font-bold text-emerald-700 transition hover:bg-emerald-50 disabled:opacity-60 dark:border-emerald-500/20 dark:bg-slate-950/40 dark:text-emerald-300 dark:hover:bg-emerald-500/10"
                    :disabled="confirmingInterviewId === application.id"
                    type="button"
                    @click="respondInterview(application, 1)"
                  >
                    {{ confirmingInterviewId === application.id && Number(application.trang_thai_tham_gia_phong_van) !== 2 ? 'Đang lưu...' : 'Xác nhận tham gia' }}
                  </button>
                  <button
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
