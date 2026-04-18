<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { employerApplicationService, employerCandidateService, employerJobService } from '@/services/api'
import { useEmployerCompanyPermissions } from '@/composables/useEmployerCompanyPermissions'
import { useNotify } from '@/composables/useNotify'
import { getAuthToken } from '@/utils/authStorage'
import { formatDateTimeVN, formatHistoricalDateTimeVN, toDateTimeLocalInputVN } from '@/utils/dateTime'
import {
  APPLICATION_STATUS,
  APPLICATION_STATUS_OPTIONS,
  getApplicationStatusMeta,
  isFinalApplicationStatus as isFinalApplicationStatusValue,
} from '@/utils/applicationStatus'

const notify = useNotify()
const { canProcessApplications, currentInternalRoleLabel, assignableMembers, ensurePermissionsLoaded } = useEmployerCompanyPermissions()

const loading = ref(false)
const saving = ref(false)
const resendingEmailId = ref(null)
const applications = ref([])
const jobs = ref([])
const pagination = ref(null)
const modalOpen = ref(false)
const selectedApplication = ref(null)
const candidateDetailOpen = ref(false)
const candidateDetailLoading = ref(false)
const candidateDetail = ref(null)

const filters = reactive({
  tin_tuyen_dung_id: '',
  trang_thai: '',
  hr_phu_trach_id: '',
  per_page: 10,
  page: 1,
})

const hrFilterOptions = computed(() => ([
  { id: '', label: 'Tất cả HR phụ trách' },
  { id: 'me', label: 'Tôi phụ trách' },
  ...assignableMembers.value,
]))

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

const statusOptions = [
  { value: '', label: 'Tất cả trạng thái' },
  ...APPLICATION_STATUS_OPTIONS,
]

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
    .filter((item) => item.ngay_hen_phong_van)
    .sort((a, b) => new Date(a.ngay_hen_phong_van) - new Date(b.ngay_hen_phong_van))
    .slice(0, 5)
)

const statusMeta = getApplicationStatusMeta

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

const formatDateTimeInput = (value) => {
  return toDateTimeLocalInputVN(value)
}

const isFinalApplicationStatus = (application) => isFinalApplicationStatusValue(application?.trang_thai)

const canEmployerUpdateApplication = (application) => !application?.da_rut_don

const canResendInterviewEmail = (application) =>
  Boolean(application?.id)
  && Boolean(application?.ngay_hen_phong_van)
  && !application?.da_rut_don
  && !isFinalApplicationStatus(application)

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

const openModal = (application) => {
  if (!canProcessApplications.value) {
    notify.warning(`Vai trò ${currentInternalRoleLabel.value} không thể cập nhật quy trình ứng tuyển.`)
    return
  }

  if (!canEmployerUpdateApplication(application)) {
    notify.info('Ứng viên đã rút đơn nên không thể cập nhật xử lý nữa.')
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
  modalOpen.value = true
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
  if (!canProcessApplications.value) {
    notify.warning(`Vai trò ${currentInternalRoleLabel.value} không thể cập nhật trạng thái ứng tuyển.`)
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

const resendInterviewEmail = async (application) => {
  if (!canProcessApplications.value) {
    notify.warning(`Vai trò ${currentInternalRoleLabel.value} không thể gửi lại email lịch phỏng vấn.`)
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

onMounted(async () => {
  await Promise.all([ensurePermissionsLoaded(), fetchJobs(), fetchApplications()])
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

    <div class="mb-6 grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
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
          <div class="grid grid-cols-1 gap-3 border-b border-slate-200 p-4 dark:border-slate-800 lg:grid-cols-[minmax(0,1fr)_220px_220px_170px_150px]">
            <select
              v-model="filters.tin_tuyen_dung_id"
              class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-[#2463eb] dark:border-slate-800 dark:bg-slate-800/70 dark:text-white"
              @change="applyFilters"
            >
              <option value="">Tất cả tin tuyển dụng</option>
              <option v-for="job in jobs" :key="job.id" :value="job.id">
                {{ job.tieu_de }}
              </option>
            </select>

            <select
              v-model="filters.trang_thai"
              class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-[#2463eb] dark:border-slate-800 dark:bg-slate-800/70 dark:text-white"
              @change="applyFilters"
            >
              <option v-for="status in statusOptions" :key="String(status.value)" :value="status.value">
                {{ status.label }}
              </option>
            </select>

            <select
              v-model="filters.hr_phu_trach_id"
              class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-[#2463eb] dark:border-slate-800 dark:bg-slate-800/70 dark:text-white"
              @change="applyFilters"
            >
              <option v-for="option in hrFilterOptions" :key="option.id || 'all-hr'" :value="option.id">
                {{ option.label }}
              </option>
            </select>

            <select
              v-model="filters.per_page"
              class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-[#2463eb] dark:border-slate-800 dark:bg-slate-800/70 dark:text-white"
              @change="applyFilters"
            >
              <option :value="10">10 / trang</option>
              <option :value="20">20 / trang</option>
              <option :value="30">30 / trang</option>
            </select>

            <button
              class="rounded-xl border border-slate-200 px-4 py-3 text-sm font-bold text-slate-600 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
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

        <div v-else class="space-y-4">
          <div
            v-for="application in applications"
            :key="application.id"
            class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm shadow-slate-950/5 dark:border-slate-800 dark:bg-slate-900"
          >
            <div class="flex flex-col gap-4">
              <div class="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
                <div class="min-w-0 flex-1">
                  <div class="flex flex-wrap items-center gap-3">
                    <h3 class="text-xl font-bold text-slate-900 dark:text-white">
                      {{ application.ho_so?.tieu_de_ho_so || 'Hồ sơ ứng viên' }}
                    </h3>
                    <span class="inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-bold" :class="statusMeta(application.trang_thai).classes">
                      <span class="h-2 w-2 rounded-full" :class="statusMeta(application.trang_thai).dot" />
                      {{ statusMeta(application.trang_thai).label }}
                    </span>
                    <span
                      v-if="application.da_rut_don"
                      class="inline-flex items-center rounded-full border border-slate-300 bg-slate-100 px-3 py-1 text-xs font-bold text-slate-700 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
                    >
                      Đã rút đơn
                    </span>
                  </div>

                  <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">
                    {{ application.ho_so?.nguoi_dung?.email || 'Chưa có email' }}
                  </p>
                </div>

                <div class="flex items-center gap-3 xl:justify-end">
                  <button
                    v-if="canResendInterviewEmail(application)"
                    class="inline-flex h-11 items-center justify-center gap-2 rounded-xl border border-emerald-200 bg-emerald-50 px-4 text-sm font-bold text-emerald-700 transition hover:bg-emerald-100 dark:border-emerald-500/20 dark:bg-emerald-500/10 dark:text-emerald-300 dark:hover:bg-emerald-500/15"
                    :disabled="resendingEmailId === application.id || !canProcessApplications"
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
                    class="inline-flex h-11 items-center justify-center gap-2 rounded-xl border border-slate-200 px-4 text-sm font-bold text-slate-600 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
                    type="button"
                    @click="openCandidateDetail(application)"
                  >
                    <span class="material-symbols-outlined text-[18px]">badge</span>
                    Xem hồ sơ
                  </button>
                  <button
                    class="inline-flex h-11 items-center justify-center gap-2 rounded-xl border px-4 text-sm font-bold transition disabled:cursor-not-allowed disabled:opacity-60"
                    :class="canEmployerUpdateApplication(application)
                      ? 'border-slate-200 text-slate-600 hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800'
                      : 'border-slate-200 text-slate-400 dark:border-slate-800 dark:text-slate-500'"
                    :disabled="!canEmployerUpdateApplication(application) || !canProcessApplications"
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
                  <p class="text-[10px] font-bold uppercase tracking-[0.22em] text-slate-400">Tin ứng tuyển</p>
                  <p class="mt-2 text-sm font-semibold leading-7 text-slate-900 dark:text-white">
                    {{ application.tin_tuyen_dung?.tieu_de || 'Chưa cập nhật' }}
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

              <div class="rounded-xl bg-slate-50 px-4 py-3 text-sm text-slate-600 dark:bg-slate-800/70 dark:text-slate-300">
                <span class="font-semibold text-slate-900 dark:text-white">HR phụ trách:</span>
                <span class="ml-2 break-words">{{ application.hr_phu_trach?.ho_ten || application.tin_tuyen_dung?.hr_phu_trach?.ho_ten || 'Chưa gán' }}</span>
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
                  <p class="font-semibold text-slate-900 dark:text-white">{{ application.ho_so?.tieu_de_ho_so || 'Hồ sơ ứng viên' }}</p>
                  <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">{{ application.tin_tuyen_dung?.tieu_de || 'Tin tuyển dụng' }}</p>
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
        <div class="flex max-h-[calc(100vh-3rem)] w-full max-w-2xl flex-col overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-[0_30px_80px_rgba(15,23,42,0.18)] dark:border-slate-800 dark:bg-slate-950 dark:shadow-[0_30px_80px_rgba(15,23,42,0.55)]">
        <div class="flex items-center justify-between border-b border-slate-200 px-6 py-5 dark:border-slate-800">
          <div>
            <h3 class="text-xl font-bold text-slate-900 dark:text-white">Cập nhật ứng tuyển</h3>
            <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
              {{ selectedApplication?.ho_so?.tieu_de_ho_so || 'Hồ sơ ứng viên' }}
            </p>
          </div>
          <button class="rounded-xl p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-900 dark:hover:text-white" type="button" @click="closeModal">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>

        <div class="grid flex-1 grid-cols-1 gap-5 overflow-y-auto p-6 md:grid-cols-2">
          <div class="md:col-span-2">
            <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Trạng thái</label>
            <select
              v-model="form.trang_thai"
              class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-[#2463eb] dark:border-slate-800 dark:bg-slate-900 dark:text-white"
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

          <div class="md:col-span-2">
            <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Ngày hẹn phỏng vấn</label>
            <input
              v-model="form.ngay_hen_phong_van"
              class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-[#2463eb] dark:border-slate-800 dark:bg-slate-900 dark:text-white"
              type="datetime-local"
            >
          </div>

          <div>
            <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Hình thức phỏng vấn</label>
            <select
              v-model="form.hinh_thuc_phong_van"
              class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-[#2463eb] dark:border-slate-800 dark:bg-slate-900 dark:text-white"
            >
              <option value="">Chưa chọn</option>
              <option value="online">Online</option>
              <option value="offline">Trực tiếp</option>
              <option value="phone">Điện thoại</option>
            </select>
          </div>

          <div>
            <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Người phỏng vấn</label>
            <input
              v-model="form.nguoi_phong_van"
              class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-[#2463eb] dark:border-slate-800 dark:bg-slate-900 dark:text-white"
              placeholder="Ví dụ: Anh Nguyễn Văn A"
              type="text"
            >
          </div>

          <div>
            <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">HR phụ trách</label>
            <select
              v-model="form.hr_phu_trach_id"
              class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-[#2463eb] dark:border-slate-800 dark:bg-slate-900 dark:text-white"
            >
              <option value="">Tự gán theo người xử lý</option>
              <option v-for="member in assignableMembers" :key="member.id" :value="String(member.id)">
                {{ member.label }}
              </option>
            </select>
          </div>

          <div class="md:col-span-2">
            <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Link meeting / địa điểm</label>
            <input
              v-model="form.link_phong_van"
              class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-[#2463eb] dark:border-slate-800 dark:bg-slate-900 dark:text-white"
              placeholder="https://meet.google.com/... hoặc địa điểm phỏng vấn"
              type="text"
            >
          </div>

          <div class="md:col-span-2">
            <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Kết quả phỏng vấn</label>
            <input
              v-model="form.ket_qua_phong_van"
              class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-[#2463eb] dark:border-slate-800 dark:bg-slate-900 dark:text-white"
              placeholder="Ví dụ: Qua vòng 1, cần thêm bài test..."
              type="text"
            >
          </div>

          <div class="md:col-span-2">
            <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Ghi chú</label>
            <textarea
              v-model="form.ghi_chu"
              class="min-h-[130px] w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-[#2463eb] dark:border-slate-800 dark:bg-slate-900 dark:text-white"
              placeholder="Ghi chú nội bộ về hồ sơ, phản hồi sau buổi phỏng vấn hoặc bước tiếp theo..."
            />
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
