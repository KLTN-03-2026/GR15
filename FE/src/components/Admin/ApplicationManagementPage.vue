<script setup>
import { computed, onMounted, ref } from 'vue'
import { adminApplicationService, companyService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'
import { formatDateTimeVN, formatHistoricalDateTimeVN } from '@/utils/dateTime'
import { APPLICATION_STATUS_OPTIONS, getApplicationStatusMeta } from '@/utils/applicationStatus'

const notify = useNotify()

const loading = ref(false)
const error = ref('')
const applications = ref([])
const currentPage = ref(1)
const perPage = ref(10)
const totalApplications = ref(0)

const selectedStatus = ref('')
const selectedCompany = ref('')
const companies = ref([])
const stats = ref({
  tong_don_ung_tuyen: 0,
  chi_tiet: {
    cho_duyet: 0,
    da_xem: 0,
    da_hen_phong_van: 0,
    qua_phong_van: 0,
    trung_tuyen: 0,
    tu_choi: 0,
  },
})

const showDetailModal = ref(false)
const selectedApplication = ref(null)

const totalPages = computed(() => Math.max(1, Math.ceil(totalApplications.value / perPage.value)))

const statusOptions = [
  { value: '', label: 'Tất cả trạng thái' },
  ...APPLICATION_STATUS_OPTIONS,
]

const summaryCards = computed(() => [
  {
    label: 'Tổng đơn ứng tuyển',
    value: stats.value?.tong_don_ung_tuyen || 0,
    description: 'Tổng số đơn ứng tuyển toàn hệ thống.',
    icon: 'work_history',
    iconClass: 'bg-[#2463eb]/10 text-[#2463eb]',
  },
  {
    label: 'Đang chờ',
    value: stats.value?.chi_tiet?.cho_duyet || 0,
    description: 'Các đơn mới đang chờ nhà tuyển dụng xử lý.',
    icon: 'schedule',
    iconClass: 'bg-amber-500/10 text-amber-500',
  },
  {
    label: 'Đã xem',
    value: stats.value?.chi_tiet?.da_xem || 0,
    description: 'Đơn đã được nhà tuyển dụng mở và xem xét.',
    icon: 'visibility',
    iconClass: 'bg-sky-500/10 text-sky-500',
  },
  {
    label: 'Đã chốt',
    value: (stats.value?.chi_tiet?.trung_tuyen || stats.value?.chi_tiet?.chap_nhan || 0) + (stats.value?.chi_tiet?.tu_choi || 0),
    description: 'Tổng đơn đã có kết luận trúng tuyển hoặc từ chối.',
    icon: 'task_alt',
    iconClass: 'bg-emerald-500/10 text-emerald-500',
  },
])

const statusMeta = getApplicationStatusMeta

const formatDateTime = (value) => {
  return formatDateTimeVN(value)
}

const formatSubmittedDateTime = (value) => {
  return formatHistoricalDateTimeVN(value)
}

const normalizePayload = (response) => {
  const payload = response?.data || {}
  applications.value = payload.data || []
  totalApplications.value = payload.total || 0
}

const loadStats = async () => {
  const response = await adminApplicationService.getStats()
  stats.value = response?.data || stats.value
}

const loadCompanies = async () => {
  const response = await companyService.getCompanies({
    per_page: 100,
    sort_by: 'created_at',
    sort_dir: 'desc',
  })

  const payload = response?.data || {}
  companies.value = payload.data || []
}

const loadApplications = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await adminApplicationService.getApplications({
      page: currentPage.value,
      per_page: perPage.value,
      cong_ty_id: selectedCompany.value || undefined,
      trang_thai: selectedStatus.value,
    })
    normalizePayload(response)
  } catch (err) {
    error.value = err.message || 'Không thể tải danh sách ứng tuyển.'
    applications.value = []
    totalApplications.value = 0
  } finally {
    loading.value = false
  }
}

const refreshAll = async () => {
  await Promise.all([loadStats(), loadCompanies(), loadApplications()])
}

const applyFilters = async () => {
  currentPage.value = 1
  await loadApplications()
}

const resetFilters = async () => {
  selectedStatus.value = ''
  selectedCompany.value = ''
  perPage.value = 10
  currentPage.value = 1
  await loadApplications()
}

const changePage = async (page) => {
  if (page < 1 || page > totalPages.value || page === currentPage.value) return
  currentPage.value = page
  await loadApplications()
}

const openDetail = (application) => {
  selectedApplication.value = application
  showDetailModal.value = true
}

onMounted(async () => {
  try {
    await refreshAll()
  } catch (err) {
    notify.apiError(err, 'Không thể tải dữ liệu ứng tuyển toàn hệ thống.')
  }
})
</script>

<template>
  <div v-if="error" class="mb-6 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-900 dark:bg-red-900/20 dark:text-red-300">
    {{ error }}
  </div>

  <div class="mb-8">
    <h1 class="text-3xl font-extrabold tracking-tight">Quản lý ứng tuyển toàn hệ thống</h1>
    <p class="mt-2 max-w-3xl text-base text-slate-500 dark:text-slate-400">
      Theo dõi các đơn ứng tuyển, trạng thái xử lý của nhà tuyển dụng và kiểm soát luồng nộp hồ sơ trên toàn bộ nền tảng.
    </p>
  </div>

  <div class="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-4">
    <div
      v-for="card in summaryCards"
      :key="card.label"
      class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900"
    >
      <div class="mb-2 flex items-center justify-between gap-3">
        <p class="text-sm font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">{{ card.label }}</p>
        <span class="material-symbols-outlined rounded-lg p-2" :class="card.iconClass">{{ card.icon }}</span>
      </div>
      <p class="text-3xl font-bold break-words">{{ card.value }}</p>
      <p class="mt-2 text-xs text-slate-400">{{ card.description }}</p>
    </div>
  </div>

  <div class="rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
    <div class="grid grid-cols-1 gap-4 border-b border-slate-200 px-6 py-5 dark:border-slate-800 xl:grid-cols-[280px_220px_180px_auto]">
      <label class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 dark:border-slate-700 dark:bg-slate-800">
        <span class="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-400">Công ty</span>
        <select
          v-model="selectedCompany"
          class="w-full bg-transparent text-sm text-slate-700 outline-none dark:text-slate-200"
          @change="applyFilters"
        >
          <option value="">Tất cả công ty</option>
          <option v-for="company in companies" :key="company.id" :value="company.id">
            {{ company.ten_cong_ty }}
          </option>
        </select>
      </label>

      <label class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 dark:border-slate-700 dark:bg-slate-800">
        <span class="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-400">Trạng thái</span>
        <select
          v-model="selectedStatus"
          class="w-full bg-transparent text-sm text-slate-700 outline-none dark:text-slate-200"
          @change="applyFilters"
        >
          <option v-for="option in statusOptions" :key="option.label" :value="option.value">{{ option.label }}</option>
        </select>
      </label>

      <label class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 dark:border-slate-700 dark:bg-slate-800">
        <span class="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-400">Số dòng / trang</span>
        <select
          v-model="perPage"
          class="w-full bg-transparent text-sm text-slate-700 outline-none dark:text-slate-200"
          @change="applyFilters"
        >
          <option :value="10">10</option>
          <option :value="15">15</option>
          <option :value="20">20</option>
        </select>
      </label>

      <div class="flex items-end justify-end">
        <button
          class="rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
          type="button"
          @click="resetFilters"
        >
          Reset bộ lọc
        </button>
      </div>
    </div>

    <div v-if="loading" class="space-y-4 px-6 py-6">
      <div v-for="index in 4" :key="index" class="h-28 animate-pulse rounded-2xl bg-slate-100 dark:bg-slate-800" />
    </div>

    <div v-else-if="!applications.length" class="px-6 py-16 text-center">
      <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-slate-100 dark:bg-slate-800">
        <span class="material-symbols-outlined text-3xl text-slate-500">work_history</span>
      </div>
      <h2 class="mt-5 text-xl font-bold text-slate-900 dark:text-white">Chưa có đơn ứng tuyển phù hợp</h2>
      <p class="mx-auto mt-3 max-w-xl text-sm leading-7 text-slate-500 dark:text-slate-400">
        Hãy điều chỉnh bộ lọc hoặc chờ thêm hoạt động ứng tuyển mới từ ứng viên và nhà tuyển dụng.
      </p>
    </div>

    <div v-else class="divide-y divide-slate-100 dark:divide-slate-800">
      <div
        v-for="application in applications"
        :key="application.id"
        class="grid grid-cols-1 gap-4 px-6 py-5 xl:grid-cols-[minmax(0,1.6fr)_220px_220px_auto]"
      >
        <div class="min-w-0">
          <div class="flex flex-wrap items-center gap-3">
            <h3 class="text-lg font-bold text-slate-900 dark:text-white">
              {{ application.ho_so?.tieu_de_ho_so || `Hồ sơ #${application.ho_so_id}` }}
            </h3>
            <span class="inline-flex items-center rounded-full px-3 py-1 text-xs font-bold" :class="statusMeta(application.trang_thai).classes">
              {{ statusMeta(application.trang_thai).label }}
            </span>
          </div>
          <p class="mt-1 text-sm font-semibold text-[#2463eb]">
            {{ application.tin_tuyen_dung?.tieu_de || `Tin #${application.tin_tuyen_dung_id}` }}
          </p>
          <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
            {{ application.tin_tuyen_dung?.cong_ty?.ten_cong_ty || 'Chưa có công ty' }}
            <span class="mx-2 text-slate-300">•</span>
            {{ application.ho_so?.nguoi_dung?.email || 'Chưa có email' }}
          </p>
          <p class="mt-3 line-clamp-2 text-sm leading-7 text-slate-500 dark:text-slate-400">
            {{ application.thu_xin_viec || application.thu_xin_viec_ai || 'Ứng viên chưa bổ sung thư xin việc cho đơn này.' }}
          </p>
        </div>

        <div class="rounded-2xl bg-slate-50 p-4 dark:bg-slate-800/60">
          <p class="text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-400">Thời gian nộp</p>
          <p class="mt-3 text-sm font-semibold leading-7 text-slate-800 dark:text-slate-100">
            {{ formatSubmittedDateTime(application.thoi_gian_ung_tuyen) }}
          </p>
        </div>

        <div class="rounded-2xl bg-slate-50 p-4 dark:bg-slate-800/60">
          <p class="text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-400">Lịch phỏng vấn</p>
          <p class="mt-3 text-sm font-semibold leading-7 text-slate-800 dark:text-slate-100">
            {{ formatDateTime(application.ngay_hen_phong_van) }}
          </p>
          <p class="mt-2 text-xs text-slate-500 dark:text-slate-400">
            {{ application.ket_qua_phong_van || 'Chưa có kết quả phỏng vấn.' }}
          </p>
        </div>

        <div class="flex items-center justify-end">
          <button
            class="rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
            type="button"
            @click="openDetail(application)"
          >
            Chi tiết
          </button>
        </div>
      </div>
    </div>

    <div v-if="totalApplications > perPage" class="flex flex-col gap-3 border-t border-slate-200 px-6 py-5 text-sm dark:border-slate-800 md:flex-row md:items-center md:justify-between">
      <p class="text-slate-500 dark:text-slate-400">
        Hiển thị {{ applications.length }} / {{ totalApplications }} đơn ứng tuyển
      </p>
      <div class="flex items-center gap-2">
        <button
          class="rounded-lg border border-slate-200 px-3 py-2 font-semibold text-slate-600 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
          :disabled="currentPage === 1"
          type="button"
          @click="changePage(currentPage - 1)"
        >
          Trước
        </button>
        <span class="rounded-lg bg-slate-100 px-3 py-2 font-semibold text-slate-700 dark:bg-slate-800 dark:text-slate-200">
          {{ currentPage }} / {{ totalPages }}
        </span>
        <button
          class="rounded-lg border border-slate-200 px-3 py-2 font-semibold text-slate-600 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
          :disabled="currentPage === totalPages"
          type="button"
          @click="changePage(currentPage + 1)"
        >
          Sau
        </button>
      </div>
    </div>
  </div>

  <div
    v-if="showDetailModal && selectedApplication"
    class="fixed inset-0 z-50 overflow-y-auto bg-slate-950/55 px-4 py-6 backdrop-blur-sm"
    @click.self="showDetailModal = false"
  >
    <div class="mx-auto w-full max-w-4xl rounded-[28px] border border-slate-200 bg-white shadow-2xl dark:border-slate-800 dark:bg-slate-900">
      <div class="flex items-start justify-between border-b border-slate-100 px-6 py-5 dark:border-slate-800">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.28em] text-[#2463eb]">Chi tiết đơn ứng tuyển</p>
          <h3 class="mt-2 text-2xl font-bold text-slate-900 dark:text-white">
            {{ selectedApplication.ho_so?.tieu_de_ho_so || `Đơn #${selectedApplication.id}` }}
          </h3>
          <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">
            {{ selectedApplication.ho_so?.nguoi_dung?.email || 'Chưa có email' }}
          </p>
        </div>
        <button
          class="rounded-full p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-800 dark:hover:text-slate-200"
          type="button"
          @click="showDetailModal = false"
        >
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>

      <div class="max-h-[calc(100vh-12rem)] overflow-y-auto px-6 py-6">
        <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div class="rounded-2xl bg-slate-50 p-4 dark:bg-slate-800/60">
            <p class="text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-400">Trạng thái</p>
            <span class="mt-3 inline-flex rounded-full px-3 py-1 text-xs font-bold" :class="statusMeta(selectedApplication.trang_thai).classes">
              {{ statusMeta(selectedApplication.trang_thai).label }}
            </span>
          </div>
          <div class="rounded-2xl bg-slate-50 p-4 dark:bg-slate-800/60">
            <p class="text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-400">Thời gian nộp</p>
            <p class="mt-3 text-sm font-semibold leading-7 text-slate-800 dark:text-slate-100">
              {{ formatSubmittedDateTime(selectedApplication.thoi_gian_ung_tuyen) }}
            </p>
          </div>
          <div class="rounded-2xl bg-slate-50 p-4 dark:bg-slate-800/60">
            <p class="text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-400">Lịch phỏng vấn</p>
            <p class="mt-3 text-sm font-semibold leading-7 text-slate-800 dark:text-slate-100">
              {{ formatDateTime(selectedApplication.ngay_hen_phong_van) }}
            </p>
          </div>
        </div>

        <div class="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div class="rounded-3xl border border-slate-200 p-5 dark:border-slate-800">
            <h4 class="text-lg font-bold text-slate-900 dark:text-white">Thông tin job</h4>
            <div class="mt-4 space-y-3 text-sm text-slate-600 dark:text-slate-300">
              <p><span class="font-semibold text-slate-900 dark:text-white">Tiêu đề:</span> {{ selectedApplication.tin_tuyen_dung?.tieu_de || 'Chưa cập nhật' }}</p>
              <p><span class="font-semibold text-slate-900 dark:text-white">Công ty:</span> {{ selectedApplication.tin_tuyen_dung?.cong_ty?.ten_cong_ty || 'Chưa cập nhật' }}</p>
              <p><span class="font-semibold text-slate-900 dark:text-white">Trạng thái tin:</span> {{ Number(selectedApplication.tin_tuyen_dung?.trang_thai) === 1 ? 'Đang hoạt động' : 'Tạm ngưng' }}</p>
            </div>
          </div>

          <div class="rounded-3xl border border-slate-200 p-5 dark:border-slate-800">
            <h4 class="text-lg font-bold text-slate-900 dark:text-white">Thông tin hồ sơ</h4>
            <div class="mt-4 space-y-3 text-sm text-slate-600 dark:text-slate-300">
              <p><span class="font-semibold text-slate-900 dark:text-white">Hồ sơ:</span> {{ selectedApplication.ho_so?.tieu_de_ho_so || 'Chưa cập nhật' }}</p>
              <p><span class="font-semibold text-slate-900 dark:text-white">Email ứng viên:</span> {{ selectedApplication.ho_so?.nguoi_dung?.email || 'Chưa cập nhật' }}</p>
            </div>
          </div>
        </div>

        <div class="mt-6 rounded-3xl border border-slate-200 p-5 dark:border-slate-800">
          <h4 class="text-lg font-bold text-slate-900 dark:text-white">Thư xin việc</h4>
          <div class="mt-4 rounded-2xl bg-slate-50 p-4 text-sm leading-7 text-slate-600 dark:bg-slate-800/60 dark:text-slate-300">
            {{ selectedApplication.thu_xin_viec || selectedApplication.thu_xin_viec_ai || 'Ứng viên chưa để lại thư xin việc.' }}
          </div>
        </div>

        <div class="mt-6 rounded-3xl border border-slate-200 p-5 dark:border-slate-800">
          <h4 class="text-lg font-bold text-slate-900 dark:text-white">Ghi chú & kết quả</h4>
          <div class="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
            <div class="rounded-2xl bg-slate-50 p-4 text-sm leading-7 text-slate-600 dark:bg-slate-800/60 dark:text-slate-300">
              <p class="text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-400">Kết quả phỏng vấn</p>
              <p class="mt-2">{{ selectedApplication.ket_qua_phong_van || 'Chưa cập nhật' }}</p>
            </div>
            <div class="rounded-2xl bg-slate-50 p-4 text-sm leading-7 text-slate-600 dark:bg-slate-800/60 dark:text-slate-300">
              <p class="text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-400">Ghi chú</p>
              <p class="mt-2">{{ selectedApplication.ghi_chu || 'Chưa có ghi chú từ nhà tuyển dụng.' }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
