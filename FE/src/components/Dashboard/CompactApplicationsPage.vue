<script setup>
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { applicationService, profileService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'
import { formatDateTimeVN, formatHistoricalDateVN } from '@/utils/dateTime'
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
  { value: STATUS_ALL, label: 'Tat ca', total: statusTotals.all },
  { value: STATUS_PENDING, label: 'Dang cho', total: statusTotals.pending },
  { value: STATUS_REVIEWED, label: 'Da xem', total: statusTotals.reviewed },
  { value: STATUS_INTERVIEW, label: 'Phong van', total: statusTotals.interview },
  { value: STATUS_PASSED, label: 'Da qua PV', total: statusTotals.passed },
  { value: STATUS_HIRED, label: 'Trung tuyen', total: statusTotals.hired },
  { value: STATUS_REJECTED, label: 'Tu choi', total: statusTotals.rejected },
  { value: STATUS_WITHDRAWN, label: 'Da rut', total: statusTotals.withdrawn },
])

const stats = computed(() => [
  { label: 'Tong don', value: statusTotals.all, icon: 'send', iconClass: 'bg-[#2463eb]/10 text-[#2463eb]' },
  { label: 'Dang cho', value: statusTotals.pending, icon: 'hourglass_top', iconClass: 'bg-amber-100 text-amber-600' },
  { label: 'Phong van', value: statusTotals.interview, icon: 'calendar_month', iconClass: 'bg-violet-100 text-violet-600' },
  { label: 'Trung tuyen', value: statusTotals.hired, icon: 'task_alt', iconClass: 'bg-green-100 text-green-600' },
])

const statusMeta = getApplicationStatusMeta
const formatAppliedDate = (value) => formatHistoricalDateVN(value, 'Dang cap nhat')
const formatDateTime = (value) => formatDateTimeVN(value, 'Chua len lich')

const interviewAttendanceMeta = (status) => {
  switch (Number(status)) {
    case 1:
      return { label: 'Da xac nhan tham gia', classes: 'bg-emerald-100 text-emerald-700' }
    case 2:
      return { label: 'Bao khong tham gia', classes: 'bg-rose-100 text-rose-700' }
    case 0:
      return { label: 'Cho ban xac nhan', classes: 'bg-violet-100 text-violet-700' }
    default:
      return { label: 'Chua co phan hoi', classes: 'bg-slate-100 text-slate-700' }
  }
}

const isInterviewResponseLocked = (application) => Boolean(application?.da_rut_don) || [
  APPLICATION_STATUS.INTERVIEW_PASSED,
  APPLICATION_STATUS.HIRED,
  APPLICATION_STATUS.REJECTED,
].includes(Number(application?.trang_thai))

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

const shouldShowInterviewSection = (application) => Boolean(application?.ngay_hen_phong_van) && !isInterviewResponseLocked(application)
const editableApplication = computed(() => selectedApplication.value)
const selectedProfile = computed(() => profiles.value.find((profile) => Number(profile.id) === Number(selectedProfileId.value)) || null)

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
    notify.apiError(error, 'Khong tai duoc danh sach don ung tuyen.')
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
    Object.keys(statusTotals).forEach((key) => {
      statusTotals[key] = 0
    })
  }
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
    notify.apiError(error, 'Khong tai duoc danh sach ho so.')
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
    applications.value = applications.value.map((item) => Number(item.id) === Number(updated?.id) ? updated : item)
    notify.success('Da cap nhat CV cho don ung tuyen.')
    updatedSuccessfully = true
  } catch (error) {
    notify.apiError(error, 'Khong the cap nhat don ung tuyen nay.')
  } finally {
    updating.value = false
    if (updatedSuccessfully) closeEditModal(true)
  }
}

const handleInterviewResponseFeedback = async () => {
  const response = typeof route.query.interview_response === 'string' ? route.query.interview_response : ''
  const applicationId = typeof route.query.application_id === 'string' ? route.query.application_id : ''
  if (!response) return

  if (response === 'accepted') notify.success('Ban da xac nhan tham gia phong van tu email.')
  else if (response === 'declined') notify.success('Da ghi nhan phan hoi khong the tham gia cua ban.')
  else if (response === 'locked') notify.info('Don ung tuyen nay da chuyen sang giai doan tiep theo.')
  else if (response === 'expired') notify.warning('Lien ket phan hoi phong van da het han.')
  else if (response === 'missing_schedule') notify.info('Lich phong van nay khong con kha dung.')
  else notify.error('Lien ket xac nhan phong van khong hop le.')

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
    applications.value = applications.value.map((item) => Number(item.id) === Number(updated?.id) ? updated : item)
    notify.success(Number(attendanceStatus) === 1 ? 'Da xac nhan tham gia phong van.' : 'Da ghi nhan phan hoi khong tham gia.')
  } catch (error) {
    notify.apiError(error, 'Khong the cap nhat phan hoi phong van.')
  } finally {
    confirmingInterviewId.value = null
  }
}

const withdrawApplication = async (application) => {
  if (!application?.id || confirmingInterviewId.value) return
  confirmingInterviewId.value = application.id
  try {
    await applicationService.withdrawApplication(application.id)
    notify.success('Da rut don ung tuyen.')
    await Promise.all([fetchApplications(pagination.current_page), fetchStatusTotals()])
  } catch (error) {
    notify.apiError(error, 'Khong the rut don ung tuyen nay.')
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
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-slate-900">Theo doi don ung tuyen</h1>
      <p class="mt-1 text-sm text-slate-500">Chi giu lai man theo doi va cap nhat trang thai ho so ung tuyen.</p>
    </div>

    <div class="mb-8 grid grid-cols-1 gap-4 md:grid-cols-4">
      <div v-for="stat in stats" :key="stat.label" class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="mb-2 flex items-center justify-between">
          <p class="text-sm font-medium text-slate-500">{{ stat.label }}</p>
          <div class="rounded-lg p-2" :class="stat.iconClass">
            <span class="material-symbols-outlined">{{ stat.icon }}</span>
          </div>
        </div>
        <h3 class="text-2xl font-bold">{{ stat.value }}</h3>
      </div>
    </div>

    <div class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <div class="flex gap-6 overflow-x-auto border-b border-slate-200 px-6">
        <button
          v-for="tab in statusTabs"
          :key="tab.value || 'all'"
          class="flex items-center whitespace-nowrap border-b-2 pb-3 pt-4 text-sm font-medium transition"
          :class="activeStatus === tab.value ? 'border-[#2463eb] font-bold text-[#2463eb]' : 'border-transparent text-slate-500 hover:text-slate-700'"
          type="button"
          @click="activeStatus = tab.value"
        >
          {{ tab.label }}
          <span class="ml-2 rounded px-2 py-0.5 text-[10px]" :class="activeStatus === tab.value ? 'bg-[#2463eb]/10' : 'bg-slate-100'">
            {{ tab.total }}
          </span>
        </button>
      </div>

      <div v-if="loading" class="divide-y divide-slate-100">
        <div v-for="index in 4" :key="index" class="p-5">
          <div class="h-24 animate-pulse rounded-xl bg-slate-100"></div>
        </div>
      </div>

      <div v-else-if="!applications.length" class="px-6 py-16 text-center">
        <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-slate-100">
          <span class="material-symbols-outlined text-3xl text-slate-500">send</span>
        </div>
        <h2 class="mt-5 text-xl font-bold text-slate-900">Chua co ung tuyen nao</h2>
        <p class="mx-auto mt-3 max-w-xl text-sm leading-7 text-slate-500">
          {{ activeStatus === STATUS_WITHDRAWN ? 'Ban chua rut don ung tuyen nao.' : 'Ban chua nop ho so trong nhom trang thai nay.' }}
        </p>
        <RouterLink to="/skills" class="mt-6 inline-flex rounded-xl bg-[#2463eb] px-5 py-3 text-sm font-bold text-white transition hover:bg-blue-700">
          Xem danh sach ky nang
        </RouterLink>
      </div>

      <div ref="applicationListRef" v-else class="divide-y divide-slate-100">
        <div
          v-for="application in applications"
          :key="application.id"
          :data-application-id="application.id"
          class="p-5 transition-colors hover:bg-slate-50"
        >
          <div class="flex flex-col gap-4">
            <div class="flex flex-col justify-between gap-4 md:flex-row md:items-center">
              <div class="flex flex-1 items-center gap-4">
                <div class="flex size-12 shrink-0 items-center justify-center rounded-lg bg-slate-100">
                  <span class="material-symbols-outlined text-slate-500">domain</span>
                </div>
                <div class="flex-1">
                  <h3 class="font-bold text-slate-900">{{ application.tin_tuyen_dung?.tieu_de || 'Tin tuyen dung dang cap nhat' }}</h3>
                  <p class="text-sm text-slate-500">{{ application.tin_tuyen_dung?.cong_ty?.ten_cong_ty || 'Cong ty dang cap nhat' }}</p>
                  <div class="mt-1.5 flex flex-wrap items-center gap-4 text-xs text-slate-400">
                    <span class="flex items-center gap-1">
                      <span class="material-symbols-outlined text-[14px]">calendar_today</span>
                      Nop ngay {{ formatAppliedDate(application.thoi_gian_ung_tuyen) }}
                    </span>
                    <span class="flex items-center gap-1">
                      <span class="material-symbols-outlined text-[14px]">description</span>
                      {{ application.ho_so?.tieu_de_ho_so || `Ho so #${application.ho_so_id}` }}
                    </span>
                  </div>
                </div>
              </div>

              <div class="flex shrink-0 items-center gap-4">
                <span class="inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-bold" :class="statusMeta(application.trang_thai).classes">
                  <span class="size-1.5 rounded-full" :class="statusMeta(application.trang_thai).dot"></span>
                  {{ statusMeta(application.trang_thai).label }}
                </span>
                <span v-if="application.da_rut_don" class="inline-flex items-center rounded-full bg-slate-200 px-2.5 py-1 text-xs font-bold text-slate-700">
                  Da rut
                </span>
                <button
                  v-if="canEditApplication(application)"
                  class="inline-flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-700 transition hover:bg-slate-50"
                  type="button"
                  @click="openEditModal(application)"
                >
                  <span class="material-symbols-outlined text-[16px]">edit_square</span>
                  Cap nhat CV
                </button>
              </div>
            </div>

            <div v-if="shouldShowInterviewSection(application)" class="rounded-2xl border border-violet-200 bg-violet-50/70 p-4">
              <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                <div class="space-y-2">
                  <div class="flex flex-wrap items-center gap-2">
                    <p class="text-sm font-bold text-slate-900">Lich phong van</p>
                    <span class="inline-flex rounded-full px-2.5 py-1 text-[11px] font-bold" :class="interviewAttendanceMeta(application.trang_thai_tham_gia_phong_van).classes">
                      {{ interviewAttendanceMeta(application.trang_thai_tham_gia_phong_van).label }}
                    </span>
                  </div>
                  <p class="text-sm text-slate-600">{{ formatDateTime(application.ngay_hen_phong_van) }}</p>
                  <p v-if="application.nguoi_phong_van" class="text-xs text-slate-500">Nguoi phong van: {{ application.nguoi_phong_van }}</p>
                  <p v-if="application.link_phong_van" class="break-words text-xs text-slate-500">Link / dia diem: {{ application.link_phong_van }}</p>
                </div>

                <div v-if="canRespondInterview(application)" class="flex flex-wrap items-center gap-2 lg:justify-end">
                  <button class="inline-flex items-center justify-center rounded-xl border border-emerald-200 bg-white px-4 py-2 text-xs font-bold text-emerald-700 transition hover:bg-emerald-50 disabled:opacity-60" :disabled="confirmingInterviewId === application.id" type="button" @click="respondInterview(application, 1)">
                    {{ confirmingInterviewId === application.id && Number(application.trang_thai_tham_gia_phong_van) !== 2 ? 'Dang luu...' : 'Xac nhan tham gia' }}
                  </button>
                  <button class="inline-flex items-center justify-center rounded-xl border border-rose-200 bg-white px-4 py-2 text-xs font-bold text-rose-700 transition hover:bg-rose-50 disabled:opacity-60" :disabled="confirmingInterviewId === application.id" type="button" @click="respondInterview(application, 2)">
                    {{ confirmingInterviewId === application.id && Number(application.trang_thai_tham_gia_phong_van) === 2 ? 'Dang luu...' : 'Khong tham gia duoc' }}
                  </button>
                </div>
              </div>

              <div v-if="canWithdrawApplication(application) || application.da_rut_don" class="mt-3 flex flex-wrap items-center gap-2">
                <button v-if="canWithdrawApplication(application)" class="inline-flex items-center justify-center rounded-xl border border-slate-300 bg-white px-4 py-2 text-xs font-bold text-slate-700 transition hover:bg-slate-50 disabled:opacity-60" :disabled="confirmingInterviewId === application.id" type="button" @click="withdrawApplication(application)">
                  {{ confirmingInterviewId === application.id ? 'Dang xu ly...' : 'Rut don ung tuyen' }}
                </button>
                <p v-if="application.da_rut_don" class="text-xs text-slate-500">Da rut luc {{ formatDateTime(application.thoi_gian_rut_don) }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="!loading && applications.length && pagination.last_page > 1" class="flex items-center justify-between border-t border-slate-200 px-6 py-4">
        <p class="text-xs text-slate-500">Hien thi {{ pagination.from }}-{{ pagination.to }} cua {{ pagination.total }} ket qua</p>
        <div class="flex gap-2">
          <button class="flex h-8 w-8 items-center justify-center rounded-lg border border-slate-200 text-slate-500 disabled:opacity-50" :disabled="pagination.current_page === 1" type="button" @click="changePage(pagination.current_page - 1)">
            <span class="material-symbols-outlined text-[18px]">chevron_left</span>
          </button>
          <button v-for="page in pagination.last_page" :key="page" class="flex h-8 w-8 items-center justify-center rounded-lg text-xs font-bold transition" :class="page === pagination.current_page ? 'bg-[#2463eb] text-white' : 'border border-slate-200 text-slate-600 hover:bg-slate-50'" type="button" @click="changePage(page)">
            {{ page }}
          </button>
          <button class="flex h-8 w-8 items-center justify-center rounded-lg border border-slate-200 text-slate-500 disabled:opacity-50" :disabled="pagination.current_page === pagination.last_page" type="button" @click="changePage(pagination.current_page + 1)">
            <span class="material-symbols-outlined text-[18px]">chevron_right</span>
          </button>
        </div>
      </div>
    </div>

    <div v-if="editModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/55 px-4 py-6 backdrop-blur-sm" @click.self="closeEditModal">
      <div class="w-full max-w-2xl rounded-[28px] border border-slate-200 bg-white shadow-2xl">
        <div class="flex items-start justify-between border-b border-slate-100 px-6 py-5">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.28em] text-blue-500">Cap nhat ung tuyen</p>
            <h3 class="mt-2 text-2xl font-bold text-slate-900">{{ editableApplication?.tin_tuyen_dung?.tieu_de }}</h3>
            <p class="mt-2 text-sm text-slate-500">Ban chi co the doi CV khi don van dang cho duyet.</p>
          </div>
          <button class="rounded-full p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700" type="button" @click="closeEditModal">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>

        <div class="space-y-5 px-6 py-6">
          <div v-if="loadingProfiles" class="rounded-2xl bg-slate-50 px-4 py-5 text-sm text-slate-500">Dang tai danh sach ho so...</div>
          <template v-else>
            <div>
              <label class="mb-2 block text-sm font-semibold text-slate-700">Chon ho so thay the</label>
              <select v-model="selectedProfileId" class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100">
                <option value="" disabled>Chon ho so cua ban</option>
                <option v-for="profile in profiles" :key="profile.id" :value="String(profile.id)">
                  {{ profile.tieu_de_ho_so || `Ho so #${profile.id}` }}
                </option>
              </select>
            </div>

            <div v-if="selectedProfile" class="rounded-2xl bg-slate-50 px-4 py-4 text-sm text-slate-600">
              <p class="font-semibold text-slate-800">{{ selectedProfile.tieu_de_ho_so || `Ho so #${selectedProfile.id}` }}</p>
              <p class="mt-1">
                Kinh nghiem: {{ selectedProfile.kinh_nghiem_nam || 0 }} nam
                <span v-if="selectedProfile.vi_tri_mong_muon">• Muc tieu: {{ selectedProfile.vi_tri_mong_muon }}</span>
              </p>
            </div>

            <div>
              <label class="mb-2 block text-sm font-semibold text-slate-700">Thu xin viec hien tai</label>
              <textarea v-model="coverLetter" rows="5" maxlength="5000" class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100" placeholder="Ban co the chinh lai thu xin viec de phu hop voi ho so moi." />
              <div class="mt-2 text-right text-xs text-slate-400">{{ coverLetter.length }}/5000</div>
            </div>
          </template>
        </div>

        <div class="flex flex-col gap-3 border-t border-slate-100 px-6 py-5 sm:flex-row sm:justify-end">
          <button class="rounded-2xl border border-slate-200 px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50" type="button" @click="closeEditModal">Huy</button>
          <button class="rounded-2xl bg-blue-600 px-5 py-3 text-sm font-bold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-300" :disabled="!selectedProfileId || updating || loadingProfiles" type="button" @click="submitApplicationUpdate">
            {{ updating ? 'Dang cap nhat...' : 'Luu thay doi' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
