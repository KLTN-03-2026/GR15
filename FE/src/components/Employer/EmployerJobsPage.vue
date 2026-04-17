<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { employerJobService, jobService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'
import { formatDateTimeVN, toDateTimeLocalInputVN } from '@/utils/dateTime'

const notify = useNotify()

const loading = ref(false)
const saving = ref(false)
const jobs = ref([])
const industries = ref([])
const pagination = ref(null)
const companyMissing = ref(false)
const activeTab = ref('all')
const showModal = ref(false)
const editingJobId = ref(null)
const deleteTarget = ref(null)
const expiryDate = ref('')
const expiryDateDisplay = ref('')
const expiryTime = ref('')
const expiryDateInput = ref(null)
const expiryTimeInput = ref(null)

const filters = reactive({
  search: '',
  trang_thai: 'all',
  page: 1,
  per_page: 10,
})

const jobForm = reactive({
  tieu_de: '',
  mo_ta_cong_viec: '',
  dia_diem_lam_viec: '',
  hinh_thuc_lam_viec: 'Toàn thời gian',
  cap_bac: '',
  so_luong_tuyen: 1,
  muc_luong: '',
  kinh_nghiem_yeu_cau: '',
  ngay_het_han: '',
  trang_thai: 1,
  nganh_nghes: [],
})

const resetJobForm = () => {
  jobForm.tieu_de = ''
  jobForm.mo_ta_cong_viec = ''
  jobForm.dia_diem_lam_viec = ''
  jobForm.hinh_thuc_lam_viec = 'Toàn thời gian'
  jobForm.cap_bac = ''
  jobForm.so_luong_tuyen = 1
  jobForm.muc_luong = ''
  jobForm.kinh_nghiem_yeu_cau = ''
  jobForm.ngay_het_han = ''
  jobForm.trang_thai = 1
  jobForm.nganh_nghes = []
  expiryDate.value = ''
  expiryDateDisplay.value = ''
  expiryTime.value = ''
}

const statusTabs = computed(() => {
  const all = jobs.value
  return [
    { key: 'all', label: 'Tất cả', count: all.length },
    { key: '1', label: 'Đang hoạt động', count: all.filter((item) => Number(item.trang_thai) === 1).length },
    { key: '0', label: 'Tạm ngưng', count: all.filter((item) => Number(item.trang_thai) === 0).length },
  ]
})

const statCards = computed(() => {
  const all = jobs.value
  const active = all.filter((item) => Number(item.trang_thai) === 1)
  const paused = all.filter((item) => Number(item.trang_thai) === 0)
  const expiringSoon = active.filter((item) => {
    if (!item.ngay_het_han) return false
    const expiryDate = parseDateTime(item.ngay_het_han)
    if (!expiryDate) return false
    const diff = expiryDate.getTime() - Date.now()
    return diff >= 0 && diff <= 7 * 24 * 60 * 60 * 1000
  })

  return [
    {
      label: 'Tổng tin đang hoạt động',
      value: active.length,
      hint: 'Đang mở nhận hồ sơ',
      icon: 'work',
      tone: 'text-blue-300 bg-blue-500/10',
    },
    {
      label: 'Tổng tin đã tạo',
      value: pagination.value?.total ?? all.length,
      hint: 'Bao gồm mọi trạng thái',
      icon: 'inventory_2',
      tone: 'text-violet-300 bg-violet-500/10',
    },
    {
      label: 'Tin tạm ngưng',
      value: paused.length,
      hint: 'Có thể bật lại bất cứ lúc nào',
      icon: 'pause_circle',
      tone: 'text-amber-300 bg-amber-500/10',
    },
    {
      label: 'Sắp hết hạn',
      value: expiringSoon.length,
      hint: 'Trong vòng 7 ngày tới',
      icon: 'event_upcoming',
      tone: 'text-emerald-300 bg-emerald-500/10',
    },
  ]
})

const filteredJobs = computed(() => {
  if (activeTab.value === 'all') return jobs.value
  return jobs.value.filter((item) => String(item.trang_thai) === activeTab.value)
})

const paginationSummary = computed(() => {
  if (!pagination.value) return 'Chưa có dữ liệu'
  return `Hiển thị ${pagination.value.from || 0}-${pagination.value.to || 0} trên ${pagination.value.total || 0} tin tuyển dụng`
})

const isEditing = computed(() => editingJobId.value !== null)

const statusLabel = (status) => (Number(status) === 1 ? 'Đang hoạt động' : 'Tạm ngưng')
const statusTone = (status) =>
  Number(status) === 1
    ? 'bg-emerald-500/10 text-emerald-300'
    : 'bg-amber-500/10 text-amber-300'

const parseDateTime = (value) => {
  if (!value) return null

  const normalized = String(value).includes(' ')
    ? String(value).replace(' ', 'T')
    : String(value)

  const parsed = new Date(normalized)
  return Number.isNaN(parsed.getTime()) ? null : parsed
}

const formatDateTime = (value) => formatDateTimeVN(value, 'Chưa đặt hạn')
const formatDateTimeInput = (value) => toDateTimeLocalInputVN(value)

const formatExpiryDateDisplay = (value) => {
  if (!value) return ''

  const [year, month, day] = String(value).split('-')
  if (!year || !month || !day) return ''

  return `${day.padStart(2, '0')}/${month.padStart(2, '0')}/${year}`
}

const parseExpiryDateDisplay = (value) => {
  const trimmed = String(value || '').trim()
  if (!trimmed) return ''

  const normalized = trimmed.replace(/-/g, '/')
  const match = normalized.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/)
  if (!match) return null

  const [, dayRaw, monthRaw, year] = match
  const day = dayRaw.padStart(2, '0')
  const month = monthRaw.padStart(2, '0')
  const iso = `${year}-${month}-${day}`
  const parsed = new Date(`${iso}T00:00:00`)

  if (Number.isNaN(parsed.getTime())) return null
  if (
    parsed.getFullYear() !== Number(year)
    || parsed.getMonth() + 1 !== Number(month)
    || parsed.getDate() !== Number(day)
  ) {
    return null
  }

  return iso
}

const commitExpiryDateDisplay = () => {
  const trimmed = String(expiryDateDisplay.value || '').trim()

  if (!trimmed) {
    expiryDate.value = ''
    expiryDateDisplay.value = ''
    return true
  }

  const parsed = parseExpiryDateDisplay(trimmed)
  if (!parsed) {
    expiryDate.value = ''
    return false
  }

  expiryDate.value = parsed
  expiryDateDisplay.value = formatExpiryDateDisplay(parsed)
  return true
}

const syncExpiryInputsFromForm = () => {
  const formatted = formatDateTimeInput(jobForm.ngay_het_han)

  if (!formatted) {
    expiryDate.value = ''
    expiryDateDisplay.value = ''
    expiryTime.value = ''
    return
  }

  const [datePart, timePart = ''] = formatted.split('T')
  expiryDate.value = datePart || ''
  expiryDateDisplay.value = formatExpiryDateDisplay(datePart || '')
  expiryTime.value = timePart.slice(0, 5)
}

const formatSalary = (value) => {
  if (value === null || value === undefined || value === '') return 'Thỏa thuận'
  return `${Number(value).toLocaleString('vi-VN')} đ`
}

const getSubmittedApplicationCount = (job) => Number(job?.tong_ung_tuyen_thuc_te || 0)
const getAcceptedCount = (job) => Number(job?.so_luong_da_nhan || 0)
const getRemainingSlots = (job) => Number(job?.so_luong_con_lai || Math.max(Number(job?.so_luong_tuyen || 0) - getAcceptedCount(job), 0))
const isQuotaFull = (job) => Boolean(job?.da_tuyen_du) || (Number(job?.so_luong_tuyen || 0) > 0 && getRemainingSlots(job) <= 0)
const canDeleteJob = (job) => getSubmittedApplicationCount(job) === 0

const syncTabWithFilter = () => {
  filters.trang_thai = activeTab.value
  filters.page = 1
}

const fetchIndustries = async () => {
  try {
    const response = await jobService.getIndustries({ per_page: 100 })
    industries.value = response?.data?.data || response?.data || []
  } catch (error) {
    notify.apiError(error, 'Không tải được danh mục ngành nghề.')
  }
}

const fetchEmployerJobs = async () => {
  loading.value = true
  companyMissing.value = false
  try {
    const response = await employerJobService.getJobs(filters)
    const payload = response?.data || {}
    jobs.value = payload.data || []
    pagination.value = payload
  } catch (error) {
    jobs.value = []
    pagination.value = null
    if (error?.status === 404) {
      companyMissing.value = true
      return
    }
    notify.apiError(error, 'Không tải được danh sách tin tuyển dụng.')
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  editingJobId.value = null
  resetJobForm()
  showModal.value = true
}

const openEditModal = (job) => {
  editingJobId.value = job.id
  jobForm.tieu_de = job.tieu_de || ''
  jobForm.mo_ta_cong_viec = job.mo_ta_cong_viec || ''
  jobForm.dia_diem_lam_viec = job.dia_diem_lam_viec || ''
  jobForm.hinh_thuc_lam_viec = job.hinh_thuc_lam_viec || 'Toàn thời gian'
  jobForm.cap_bac = job.cap_bac || ''
  jobForm.so_luong_tuyen = Number(job.so_luong_tuyen || 1)
  jobForm.muc_luong = job.muc_luong ?? ''
  jobForm.kinh_nghiem_yeu_cau = job.kinh_nghiem_yeu_cau || ''
  jobForm.ngay_het_han = formatDateTimeInput(job.ngay_het_han)
  jobForm.trang_thai = Number(job.trang_thai ?? 1)
  jobForm.nganh_nghes = (job.nganh_nghes || []).map((item) => item.id)
  syncExpiryInputsFromForm()
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingJobId.value = null
}

const openDeleteModal = (job) => {
  if (!canDeleteJob(job)) {
    notify.warning('Tin này đã có ứng tuyển. Hãy chuyển sang tạm ngưng thay vì xóa.')
    return
  }
  deleteTarget.value = job
}

const closeDeleteModal = () => {
  deleteTarget.value = null
}

const openNativePicker = (inputRef) => {
  const input = inputRef?.showPicker
    ? inputRef
    : inputRef?.value?.showPicker
      ? inputRef.value
      : null

  if (!input) return

  if (typeof input.showPicker === 'function') {
    input.showPicker()
    return
  }

  if (typeof input.click === 'function') {
    input.click()
  }

  input.focus()
}

const buildPayload = () => ({
  tieu_de: jobForm.tieu_de.trim(),
  mo_ta_cong_viec: jobForm.mo_ta_cong_viec.trim(),
  dia_diem_lam_viec: jobForm.dia_diem_lam_viec.trim(),
  hinh_thuc_lam_viec: jobForm.hinh_thuc_lam_viec || null,
  cap_bac: jobForm.cap_bac || null,
  so_luong_tuyen: Number(jobForm.so_luong_tuyen || 1),
  muc_luong: jobForm.muc_luong === '' ? null : Number(jobForm.muc_luong),
  kinh_nghiem_yeu_cau: jobForm.kinh_nghiem_yeu_cau || null,
  ngay_het_han: jobForm.ngay_het_han || null,
  trang_thai: Number(jobForm.trang_thai ?? 1),
  nganh_nghes: jobForm.nganh_nghes,
})

const submitJobForm = async () => {
  if (!commitExpiryDateDisplay()) {
    notify.warning('Vui lòng nhập ngày hết hạn theo định dạng dd/mm/yyyy.')
    return
  }

  if (!jobForm.tieu_de.trim() || !jobForm.mo_ta_cong_viec.trim() || !jobForm.dia_diem_lam_viec.trim()) {
    notify.warning('Vui lòng nhập đầy đủ tiêu đề, mô tả và địa điểm làm việc.')
    return
  }
  if (!jobForm.nganh_nghes.length) {
    notify.warning('Vui lòng chọn ít nhất một ngành nghề.')
    return
  }
  if (expiryTime.value && !expiryDate.value) {
    notify.warning('Vui lòng chọn ngày hết hạn nếu bạn đã nhập giờ hết hạn.')
    return
  }

  saving.value = true
  try {
    const payload = buildPayload()
    if (editingJobId.value) {
      await employerJobService.updateJob(editingJobId.value, payload)
      notify.saved('Tin tuyển dụng')
    } else {
      await employerJobService.createJob(payload)
      notify.created('Tin tuyển dụng')
    }
    closeModal()
    await fetchEmployerJobs()
  } catch (error) {
    notify.apiError(error, 'Không thể lưu tin tuyển dụng.')
  } finally {
    saving.value = false
  }
}

const toggleJobStatus = async (job) => {
  try {
    await employerJobService.toggleStatus(job.id)
    notify.success(`Đã chuyển trạng thái sang ${Number(job.trang_thai) === 1 ? 'tạm ngưng' : 'đang hoạt động'}.`)
    await fetchEmployerJobs()
  } catch (error) {
    notify.apiError(error, 'Không thể chuyển trạng thái tin.')
  }
}

const deleteJob = async (job) => {
  try {
    await employerJobService.deleteJob(job.id)
    notify.deleted('Tin tuyển dụng')
    closeDeleteModal()
    await fetchEmployerJobs()
  } catch (error) {
    notify.apiError(error, 'Không thể xóa tin tuyển dụng. Nếu tin đã có ứng tuyển, hãy dùng Tạm ngưng.')
  }
}

const parseJob = async (job) => {
  try {
    await employerJobService.parseJob(job.id)
    notify.success('Đã gửi yêu cầu parse JD cho tin tuyển dụng.')
  } catch (error) {
    notify.apiError(error, 'Không thể parse JD cho tin tuyển dụng.')
  }
}

const goToPage = async (page) => {
  if (!page || page === filters.page) return
  filters.page = page
  await fetchEmployerJobs()
}

const applyFilters = async () => {
  filters.page = 1
  await fetchEmployerJobs()
}

onMounted(async () => {
  await Promise.all([fetchIndustries(), fetchEmployerJobs()])
})

watch([expiryDate, expiryTime], ([dateValue, timeValue]) => {
  if (!dateValue) {
    jobForm.ngay_het_han = ''
    return
  }

  jobForm.ngay_het_han = `${dateValue}T${timeValue || '23:59'}`
})

watch(expiryDate, (value) => {
  expiryDateDisplay.value = formatExpiryDateDisplay(value)
})
</script>

<template>
  <div class="max-w-7xl mx-auto w-full">
    <div class="mb-8 flex flex-wrap items-end justify-between gap-4">
      <div class="flex flex-col gap-1">
        <h1 class="text-3xl font-black tracking-tight text-slate-900 dark:text-white">Việc làm của tôi</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400">
          Tạo, cập nhật và theo dõi các tin tuyển dụng của công ty trên cùng một màn hình.
        </p>
      </div>
      <button
        class="flex h-11 items-center justify-center gap-2 rounded-lg bg-[#2463eb] px-6 font-semibold text-white shadow-lg shadow-[#2463eb]/20 transition-colors hover:bg-blue-700"
        type="button"
        @click="openCreateModal"
      >
        <span class="material-symbols-outlined text-[20px]">add</span>
        <span>Đăng tin mới</span>
      </button>
    </div>

    <div v-if="companyMissing" class="rounded-2xl border border-amber-500/30 bg-amber-500/10 p-6 text-amber-100 shadow-sm">
      <h2 class="text-lg font-bold">Bạn chưa thiết lập công ty</h2>
      <p class="mt-2 text-sm leading-7 text-amber-50/90">
        Hệ thống chỉ cho phép đăng tin sau khi doanh nghiệp hoàn tất thông tin công ty.
      </p>
      <RouterLink
        to="/employer/company"
        class="mt-4 inline-flex items-center gap-2 rounded-xl bg-white px-4 py-2.5 text-sm font-bold text-amber-700 transition hover:bg-amber-50"
      >
        <span class="material-symbols-outlined text-lg">domain</span>
        Đi tới thông tin công ty
      </RouterLink>
    </div>

    <template v-else>
      <div class="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div
          v-for="card in statCards"
          :key="card.label"
          class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900"
        >
          <div class="flex items-center justify-between">
            <p class="mb-1 text-xs font-bold uppercase tracking-wider text-slate-500">{{ card.label }}</p>
            <span class="material-symbols-outlined rounded-lg p-2 text-[20px]" :class="card.tone">{{ card.icon }}</span>
          </div>
          <p class="text-2xl font-black text-slate-900 dark:text-white">{{ card.value }}</p>
          <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">{{ card.hint }}</p>
        </div>
      </div>

      <div class="mb-6 rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div class="flex flex-wrap gap-2 border-b border-slate-200 px-4 dark:border-slate-800">
          <button
            v-for="tab in statusTabs"
            :key="tab.key"
            type="button"
            class="flex items-center gap-2 border-b-2 px-4 pb-3 pt-4 text-sm font-bold transition"
            :class="activeTab === tab.key ? 'border-[#2463eb] text-[#2463eb]' : 'border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'"
            @click="activeTab = tab.key; syncTabWithFilter(); fetchEmployerJobs()"
          >
            {{ tab.label }}
            <span class="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] dark:bg-slate-800">{{ tab.count }}</span>
          </button>
        </div>

        <div class="grid grid-cols-1 gap-3 border-b border-slate-200 p-4 dark:border-slate-800 md:grid-cols-[minmax(0,1fr)_180px_140px]">
          <input
            v-model="filters.search"
            class="w-full rounded-lg border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-[#2463eb] dark:border-slate-800 dark:bg-slate-800/70 dark:text-white"
            placeholder="Tìm theo tiêu đề tin tuyển dụng..."
            type="text"
            @keyup.enter="applyFilters"
          >
          <select
            v-model="filters.per_page"
            class="rounded-lg border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-[#2463eb] dark:border-slate-800 dark:bg-slate-800/70 dark:text-white"
            @change="applyFilters"
          >
            <option :value="10">10 tin / trang</option>
            <option :value="15">15 tin / trang</option>
            <option :value="20">20 tin / trang</option>
          </select>
          <button
            class="rounded-lg bg-[#2463eb] px-4 py-2.5 text-sm font-bold text-white transition hover:bg-blue-700"
            type="button"
            @click="applyFilters"
          >
            Áp dụng bộ lọc
          </button>
        </div>

        <div v-if="loading" class="space-y-3 p-4">
          <div v-for="index in 5" :key="index" class="h-16 animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800" />
        </div>

        <div v-else-if="!filteredJobs.length" class="p-8 text-center text-sm text-slate-500 dark:text-slate-400">
          Chưa có tin tuyển dụng nào phù hợp với bộ lọc hiện tại.
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full border-collapse text-left">
            <thead>
              <tr class="border-b border-slate-200 bg-slate-50 dark:border-slate-800 dark:bg-slate-800/50">
                <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-500">Tiêu đề</th>
                <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-500">Ngành nghề</th>
                <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-500">Mức lương</th>
                <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-500">Trạng thái</th>
                <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-500">Hết hạn</th>
                <th class="px-6 py-4 text-right text-xs font-bold uppercase tracking-wider text-slate-500">Thao tác</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 dark:divide-slate-800">
              <tr
                v-for="job in filteredJobs"
                :key="job.id"
                class="transition-colors hover:bg-slate-50 dark:hover:bg-slate-800/50"
              >
                <td class="px-6 py-4">
                  <div class="flex flex-col">
                    <RouterLink
                      :to="`/employer/jobs/${job.id}`"
                      class="text-sm font-semibold text-slate-900 transition hover:text-[#2463eb] dark:text-white dark:hover:text-[#7ea8ff]"
                    >
                      {{ job.tieu_de }}
                    </RouterLink>
                    <span class="mt-1 text-xs text-slate-500">{{ job.dia_diem_lam_viec }} · {{ job.cap_bac || 'Chưa đặt cấp bậc' }}</span>
                    <span
                      class="mt-2 inline-flex w-fit rounded-full px-2.5 py-1 text-[11px] font-semibold"
                      :class="isQuotaFull(job) ? 'bg-rose-500/10 text-rose-300' : 'bg-emerald-500/10 text-emerald-300'"
                    >
                      {{ getAcceptedCount(job) }}/{{ job.so_luong_tuyen || 0 }} đã nhận · {{ isQuotaFull(job) ? 'Đã đủ chỉ tiêu' : `${getRemainingSlots(job)} còn lại` }}
                    </span>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <div class="flex flex-wrap gap-1.5">
                    <span
                      v-for="industry in job.nganh_nghes || []"
                      :key="industry.id"
                      class="inline-flex items-center rounded-md bg-slate-100 px-2 py-1 text-xs font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-300"
                    >
                      {{ industry.ten_nganh }}
                    </span>
                  </div>
                </td>
                <td class="px-6 py-4 text-sm font-semibold text-slate-900 dark:text-white">
                  {{ formatSalary(job.muc_luong) }}
                </td>
                <td class="px-6 py-4">
                  <span class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-bold" :class="statusTone(job.trang_thai)">
                    <span class="size-1.5 rounded-full" :class="Number(job.trang_thai) === 1 ? 'bg-emerald-400' : 'bg-amber-400'" />
                    {{ statusLabel(job.trang_thai) }}
                  </span>
                </td>
                <td class="px-6 py-4 text-sm text-slate-500 dark:text-slate-400">
                  {{ formatDateTime(job.ngay_het_han) }}
                </td>
                <td class="px-6 py-4">
                  <div class="flex justify-end gap-2">
                    <RouterLink
                      :to="`/employer/jobs/${job.id}`"
                      class="flex size-9 items-center justify-center rounded-lg text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-800 dark:hover:text-white"
                      title="Xem chi tiết"
                    >
                      <span class="material-symbols-outlined text-[18px]">visibility</span>
                    </RouterLink>
                    <button
                      class="flex size-9 items-center justify-center rounded-lg text-slate-400 transition-colors hover:bg-[#2463eb]/10 hover:text-[#2463eb]"
                      title="Sửa tin"
                      type="button"
                      @click="openEditModal(job)"
                    >
                      <span class="material-symbols-outlined text-[18px]">edit</span>
                    </button>
                    <button
                      class="flex size-9 items-center justify-center rounded-lg text-slate-400 transition-colors hover:bg-violet-500/10 hover:text-violet-300"
                      title="Parse JD"
                      type="button"
                      @click="parseJob(job)"
                    >
                      <span class="material-symbols-outlined text-[18px]">auto_awesome</span>
                    </button>
                    <button
                      class="flex size-9 items-center justify-center rounded-lg text-slate-400 transition-colors hover:bg-amber-500/10 hover:text-amber-300"
                      :title="Number(job.trang_thai) === 1 ? 'Tạm ngưng tin' : 'Bật lại tin'"
                      type="button"
                      @click="toggleJobStatus(job)"
                    >
                      <span class="material-symbols-outlined text-[18px]">
                        {{ Number(job.trang_thai) === 1 ? 'pause_circle' : 'play_circle' }}
                      </span>
                    </button>
                    <button
                      class="flex size-9 items-center justify-center rounded-lg transition-colors"
                      :class="canDeleteJob(job)
                        ? 'text-slate-400 hover:bg-red-500/10 hover:text-red-400'
                        : 'text-slate-300/80 hover:bg-amber-500/10 hover:text-amber-400 dark:text-slate-600 dark:hover:text-amber-300'"
                      :title="canDeleteJob(job) ? 'Xóa tin' : `Tin đã có ${getSubmittedApplicationCount(job)} ứng tuyển, hãy tạm ngưng thay vì xóa`"
                      type="button"
                      @click="openDeleteModal(job)"
                    >
                      <span class="material-symbols-outlined text-[18px]">
                        {{ canDeleteJob(job) ? 'delete' : 'lock' }}
                      </span>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="flex items-center justify-between border-t border-slate-200 bg-slate-50/50 px-6 py-4 dark:border-slate-800 dark:bg-slate-900">
          <p class="text-xs font-medium text-slate-500">{{ paginationSummary }}</p>
          <div class="flex gap-2">
            <button
              class="rounded-md border border-slate-200 px-3 py-1 text-xs font-bold text-slate-600 transition-colors hover:bg-white disabled:opacity-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
              :disabled="!pagination?.prev_page_url"
              type="button"
              @click="goToPage((pagination?.current_page || 1) - 1)"
            >
              Trước
            </button>
            <button
              class="rounded-md border border-slate-200 px-3 py-1 text-xs font-bold text-slate-600 transition-colors hover:bg-white disabled:opacity-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
              :disabled="!pagination?.next_page_url"
              type="button"
              @click="goToPage((pagination?.current_page || 1) + 1)"
            >
              Sau
            </button>
          </div>
        </div>
      </div>
    </template>

  <div
    v-if="showModal"
    class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 px-4 py-6 backdrop-blur-sm"
    @click.self="closeModal"
  >
      <div class="max-h-[92vh] w-full max-w-4xl overflow-y-auto rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl">
        <div class="flex items-start justify-between gap-4">
          <div>
            <h2 class="text-2xl font-black text-white">{{ isEditing ? 'Cập nhật tin tuyển dụng' : 'Tạo tin tuyển dụng mới' }}</h2>
            <p class="mt-1 text-sm text-slate-400">Giữ phong cách cũ nhưng nối trực tiếp vào dữ liệu thật của hệ thống.</p>
          </div>
          <button class="rounded-lg p-2 text-slate-400 transition hover:bg-slate-800 hover:text-white" type="button" @click="closeModal">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>

        <div class="mt-6 grid grid-cols-1 gap-5 md:grid-cols-2">
          <label class="block md:col-span-2">
            <span class="mb-2 block text-sm font-semibold text-slate-300">Tiêu đề tin tuyển dụng</span>
            <input v-model="jobForm.tieu_de" class="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none transition focus:border-[#2463eb]" type="text">
          </label>

          <label class="block">
            <span class="mb-2 block text-sm font-semibold text-slate-300">Địa điểm làm việc</span>
            <input v-model="jobForm.dia_diem_lam_viec" class="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none transition focus:border-[#2463eb]" type="text">
          </label>

          <label class="block">
            <span class="mb-2 block text-sm font-semibold text-slate-300">Hình thức làm việc</span>
            <select v-model="jobForm.hinh_thuc_lam_viec" class="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none transition focus:border-[#2463eb]">
              <option value="Toàn thời gian">Toàn thời gian</option>
              <option value="Bán thời gian">Bán thời gian</option>
              <option value="Thực tập">Thực tập</option>
              <option value="Freelance">Freelance</option>
              <option value="Remote">Remote</option>
            </select>
          </label>

          <label class="block">
            <span class="mb-2 block text-sm font-semibold text-slate-300">Cấp bậc</span>
            <input v-model="jobForm.cap_bac" class="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none transition focus:border-[#2463eb]" placeholder="Junior / Senior / Manager" type="text">
          </label>

          <label class="block">
            <span class="mb-2 block text-sm font-semibold text-slate-300">Kinh nghiệm yêu cầu</span>
            <input v-model="jobForm.kinh_nghiem_yeu_cau" class="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none transition focus:border-[#2463eb]" placeholder="Ví dụ: 2 năm" type="text">
          </label>

          <label class="block">
            <span class="mb-2 block text-sm font-semibold text-slate-300">Số lượng tuyển</span>
            <input v-model.number="jobForm.so_luong_tuyen" class="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none transition focus:border-[#2463eb]" min="1" type="number">
          </label>

          <label class="block">
            <span class="mb-2 block text-sm font-semibold text-slate-300">Mức lương (VND)</span>
            <input v-model="jobForm.muc_luong" class="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none transition focus:border-[#2463eb]" min="0" placeholder="18000000" type="number">
          </label>

          <div class="block">
            <span class="mb-2 block text-sm font-semibold text-slate-300">Ngày giờ hết hạn</span>
            <div class="grid grid-cols-1 gap-3 sm:grid-cols-[minmax(0,1fr)_150px]">
              <div class="relative">
                <input
                  v-model="expiryDateDisplay"
                  class="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 pr-12 text-sm text-white outline-none transition focus:border-[#2463eb]"
                  placeholder="dd/mm/yyyy"
                  type="text"
                  @blur="commitExpiryDateDisplay"
                  @keyup.enter="commitExpiryDateDisplay"
                >
                <input
                  ref="expiryDateInput"
                  v-model="expiryDate"
                  class="pointer-events-none absolute inset-0 opacity-0"
                  tabindex="-1"
                  type="date"
                >
                <button
                  class="absolute inset-y-0 right-0 inline-flex w-11 items-center justify-center text-white/90 transition hover:text-white"
                  type="button"
                  @click="openNativePicker(expiryDateInput)"
                >
                  <span class="material-symbols-outlined text-[18px]">calendar_month</span>
                </button>
              </div>
              <div class="relative">
                <input
                  ref="expiryTimeInput"
                  v-model="expiryTime"
                  class="datetime-picker-white w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 pr-12 text-sm text-white outline-none transition focus:border-[#2463eb]"
                  step="60"
                  type="time"
                >
                <button
                  class="absolute inset-y-0 right-0 inline-flex w-11 items-center justify-center text-white/90 transition hover:text-white"
                  type="button"
                  @click="openNativePicker(expiryTimeInput)"
                >
                  <span class="material-symbols-outlined text-[18px]">schedule</span>
                </button>
              </div>
            </div>
            <p class="mt-2 text-xs text-slate-400">
              Có thể gõ trực tiếp hoặc bấm chọn. Nếu chỉ chọn ngày, hệ thống sẽ lấy giờ mặc định là 23:59.
            </p>
          </div>

          <label class="block">
            <span class="mb-2 block text-sm font-semibold text-slate-300">Trạng thái ban đầu</span>
            <select v-model="jobForm.trang_thai" class="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none transition focus:border-[#2463eb]">
              <option :value="1">Đang hoạt động</option>
              <option :value="0">Tạm ngưng</option>
            </select>
          </label>

          <div class="md:col-span-2">
            <span class="mb-2 block text-sm font-semibold text-slate-300">Ngành nghề</span>
            <div class="grid max-h-44 grid-cols-1 gap-2 overflow-y-auto rounded-xl border border-slate-700 bg-slate-950 p-3 sm:grid-cols-2">
              <label
                v-for="industry in industries"
                :key="industry.id"
                class="inline-flex items-center gap-2 rounded-lg px-2 py-1 text-sm text-slate-300 transition hover:bg-slate-800"
              >
                <input
                  :value="industry.id"
                  :checked="jobForm.nganh_nghes.includes(industry.id)"
                  class="accent-[#2463eb]"
                  type="checkbox"
                  @change="
                    $event.target.checked
                      ? jobForm.nganh_nghes.push(industry.id)
                      : jobForm.nganh_nghes = jobForm.nganh_nghes.filter((id) => id !== industry.id)
                  "
                >
                {{ industry.ten_nganh }}
              </label>
            </div>
          </div>

          <label class="block md:col-span-2">
            <span class="mb-2 block text-sm font-semibold text-slate-300">Mô tả công việc</span>
            <textarea
              v-model="jobForm.mo_ta_cong_viec"
              class="min-h-[180px] w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm leading-7 text-white outline-none transition focus:border-[#2463eb]"
            />
          </label>
        </div>

        <div class="mt-6 flex justify-end gap-3">
          <button class="rounded-xl border border-slate-700 px-5 py-3 text-sm font-bold text-slate-300 transition hover:bg-slate-800" type="button" @click="closeModal">
            Hủy
          </button>
          <button
            class="rounded-xl bg-[#2463eb] px-5 py-3 text-sm font-bold text-white shadow-lg shadow-[#2463eb]/20 transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
            :disabled="saving"
            type="button"
            @click="submitJobForm"
          >
            {{ saving ? 'Đang lưu...' : isEditing ? 'Lưu thay đổi' : 'Tạo tin tuyển dụng' }}
          </button>
        </div>
      </div>
    </div>
  </div>

  <div
    v-if="deleteTarget"
    class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 px-4 py-6 backdrop-blur-sm"
    @click.self="closeDeleteModal"
  >
    <div class="w-full max-w-lg rounded-3xl border border-red-500/20 bg-slate-950/95 p-6 shadow-2xl shadow-red-950/20">
      <div class="flex items-start gap-4">
        <div class="flex size-12 items-center justify-center rounded-2xl bg-red-500/10 text-red-300">
          <span class="material-symbols-outlined">delete</span>
        </div>

        <div class="flex-1">
          <p class="text-xs font-semibold uppercase tracking-[0.35em] text-red-300/80">
            Xác nhận xóa
          </p>
          <h3 class="mt-2 text-2xl font-semibold text-white">
            Xóa tin tuyển dụng này?
          </h3>
          <p class="mt-3 text-sm leading-7 text-slate-300">
            Tin
            <span class="font-semibold text-white">"{{ deleteTarget.tieu_de }}"</span>
            sẽ bị xóa khỏi danh sách tuyển dụng của bạn. Hành động này không thể hoàn tác.
          </p>
          <p class="mt-3 text-xs leading-6 text-slate-400">
            Nếu tin này đã có đơn ứng tuyển, hệ thống sẽ chặn xóa để giữ lịch sử xử lý. Hãy chuyển tin sang trạng thái tạm ngưng.
          </p>
        </div>
      </div>

      <div class="mt-8 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
        <button
          class="inline-flex items-center justify-center rounded-2xl border border-slate-700 px-5 py-3 text-sm font-semibold text-slate-200 transition hover:border-slate-600 hover:bg-slate-900"
          type="button"
          @click="closeDeleteModal"
        >
          Hủy
        </button>
        <button
          class="inline-flex items-center justify-center rounded-2xl bg-red-500 px-5 py-3 text-sm font-semibold text-white transition hover:bg-red-400"
          type="button"
          @click="deleteJob(deleteTarget)"
        >
          Xóa tin tuyển dụng
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.datetime-picker-white {
  color-scheme: dark;
}

.datetime-picker-white::-webkit-calendar-picker-indicator {
  opacity: 0;
  position: absolute;
  right: 0;
  width: 2.75rem;
  height: 100%;
  cursor: pointer;
}
</style>
