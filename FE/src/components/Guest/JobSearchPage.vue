<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { jobService, savedJobService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'
import { getAuthToken, getStoredCandidate } from '@/utils/authStorage'
import { VIETNAM_PROVINCES_34 } from '@/constants/vietnamProvinces'

const route = useRoute()
const router = useRouter()
const notify = useNotify()

const filters = reactive({
  search: route.query.search || '',
  nganh_nghe_id: route.query.nganh_nghe_id || '',
  dia_diem: route.query.dia_diem || '',
  per_page: Number(route.query.per_page || 9),
})

const jobs = ref([])
const industries = ref([])
const savedJobIds = ref(new Set())
const loading = ref(false)
const industriesLoading = ref(false)
const togglingJobId = ref(null)
const pagination = reactive({
  current_page: 1,
  last_page: 1,
  per_page: 9,
  total: 0,
  from: 0,
  to: 0,
})

const hasActiveFilters = computed(() =>
  Boolean(filters.search || filters.nganh_nghe_id || filters.dia_diem)
)

const showAllIndustries = ref(false)
const pageSizeOptions = [6, 9, 12, 15]

const visibleIndustries = computed(() =>
  showAllIndustries.value ? industries.value : industries.value.slice(0, 5)
)

const selectedIndustryName = computed(() => {
  if (!filters.nganh_nghe_id) return 'Tất cả ngành nghề'
  return industries.value.find((industry) => String(industry.id) === String(filters.nganh_nghe_id))?.ten_nganh || 'Ngành nghề đã chọn'
})

const summaryText = computed(() => {
  if (!pagination.total) return 'Chưa tìm thấy tin tuyển dụng phù hợp.'
  return `Hiển thị ${pagination.from}-${pagination.to} trên tổng ${pagination.total} tin tuyển dụng đang hoạt động.`
})

const hasAuthToken = computed(() => Boolean(getAuthToken()))
const currentUser = computed(() => getStoredCandidate())
const isCandidate = computed(() => hasAuthToken.value && currentUser.value?.vai_tro === 0)

const formatCurrency = (value) => {
  if (value === null || value === undefined || value === '') return 'Thỏa thuận'
  return new Intl.NumberFormat('vi-VN').format(Number(value)) + ' đ'
}

const formatSalary = (job) => {
  if (job.muc_luong_tu && job.muc_luong_den) {
    return `${formatCurrency(job.muc_luong_tu)} - ${formatCurrency(job.muc_luong_den)}`
  }
  if (job.muc_luong_tu) return formatCurrency(job.muc_luong_tu)
  return 'Thỏa thuận'
}

const formatRelativeDate = (value) => {
  if (!value) return 'Mới đăng'
  const createdAt = new Date(value)
  const now = new Date()
  const diffMs = now.getTime() - createdAt.getTime()
  const diffHours = Math.max(1, Math.floor(diffMs / (1000 * 60 * 60)))

  if (diffHours < 24) return `${diffHours} giờ trước`

  const diffDays = Math.floor(diffHours / 24)
  if (diffDays < 30) return `${diffDays} ngày trước`

  return createdAt.toLocaleDateString('vi-VN')
}

const getAcceptedCount = (job) => Number(job?.so_luong_da_nhan || 0)
const getRemainingSlots = (job) => Number(job?.so_luong_con_lai || 0)
const isQuotaFull = (job) => Boolean(job?.da_tuyen_du) || (Number(job?.so_luong_tuyen || 0) > 0 && getRemainingSlots(job) <= 0)

const buildQuery = (page = 1, extra = {}) => {
  const query = {}

  if (filters.search) query.search = filters.search
  if (filters.nganh_nghe_id) query.nganh_nghe_id = filters.nganh_nghe_id
  if (filters.dia_diem) query.dia_diem = filters.dia_diem
  if (filters.per_page !== 9) query.per_page = filters.per_page
  if (page > 1) query.page = page

  return {
    ...query,
    ...extra,
  }
}

const syncQuery = (page = 1, extra = {}) => {
  router.replace({ query: buildQuery(page, extra) })
}

const fetchIndustries = async () => {
  industriesLoading.value = true
  try {
    const response = await jobService.getIndustries({ per_page: 0 })
    industries.value = Array.isArray(response?.data) ? response.data : response?.data?.data || []
  } catch (error) {
    notify.apiError(error, 'Không tải được danh sách ngành nghề.')
  } finally {
    industriesLoading.value = false
  }
}

const fetchJobs = async (page = Number(route.query.page || 1)) => {
  loading.value = true
  try {
    const response = await jobService.getJobs({
      search: filters.search,
      nganh_nghe_id: filters.nganh_nghe_id,
      dia_diem: filters.dia_diem,
      per_page: filters.per_page,
      page,
    })

    const payload = response?.data || {}
    jobs.value = payload.data || []
    pagination.current_page = payload.current_page || 1
    pagination.last_page = payload.last_page || 1
    pagination.per_page = payload.per_page || filters.per_page
    pagination.total = payload.total || 0
    pagination.from = payload.from || 0
    pagination.to = payload.to || 0
    if (isCandidate.value) {
      await syncSavedState()
    }
  } catch (error) {
    jobs.value = []
    pagination.current_page = 1
    pagination.last_page = 1
    pagination.total = 0
    pagination.from = 0
    pagination.to = 0
    notify.apiError(error, 'Không tải được danh sách việc làm.')
  } finally {
    loading.value = false
  }
}

const syncSavedState = async () => {
  try {
    const response = await savedJobService.getSavedJobs({ per_page: 100 })
    const items = response?.data?.data || []
    savedJobIds.value = new Set(items.map((item) => Number(item.id)))
  } catch {
    savedJobIds.value = new Set()
  }
}

const applyFilters = async () => {
  syncQuery(1)
  await fetchJobs(1)
}

const resetFilters = async () => {
  filters.search = ''
  filters.nganh_nghe_id = ''
  filters.dia_diem = ''
  filters.per_page = 9
  syncQuery(1)
  await fetchJobs(1)
}

const changePage = async (page) => {
  if (page < 1 || page > pagination.last_page || page === pagination.current_page) return
  syncQuery(page)
  await fetchJobs(page)
}

const selectIndustry = (industryId) => {
  const nextValue = String(industryId)
  filters.nganh_nghe_id = String(filters.nganh_nghe_id) === nextValue ? '' : nextValue
}

const isSaved = (jobId) => savedJobIds.value.has(Number(jobId))

const toggleSavedJob = async (jobId) => {
  if (!isCandidate.value) {
    notify.warning('Vui lòng đăng nhập bằng tài khoản ứng viên để lưu tin.')
    return
  }

  if (togglingJobId.value) return
  togglingJobId.value = jobId

  try {
    const response = await savedJobService.toggleSavedJob(jobId)
    const savedState = Boolean(response?.data?.trang_thai_luu)
    const nextSet = new Set(savedJobIds.value)
    if (savedState) {
      nextSet.add(Number(jobId))
      notify.success('Đã lưu tin tuyển dụng.')
    } else {
      nextSet.delete(Number(jobId))
      notify.info('Đã bỏ lưu tin tuyển dụng.')
    }
    savedJobIds.value = nextSet
  } catch (error) {
    notify.apiError(error, 'Không thể cập nhật trạng thái lưu tin.')
  } finally {
    togglingJobId.value = null
  }
}

onMounted(async () => {
  await Promise.all([fetchIndustries(), fetchJobs(Number(route.query.page || 1))])
})

watch(
  () => route.query,
  (query) => {
    filters.search = query.search || ''
    filters.nganh_nghe_id = query.nganh_nghe_id || ''
    filters.dia_diem = query.dia_diem || ''
    filters.per_page = Number(query.per_page || 9)
  }
)
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 py-8">
    <div class="rounded-[28px] border border-slate-200 bg-gradient-to-r from-slate-900 via-blue-900 to-blue-600 px-6 py-8 text-white shadow-xl shadow-blue-200/50 md:px-8">
      <div class="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
        <div class="max-w-3xl">
          <p class="text-xs font-semibold uppercase tracking-[0.35em] text-blue-100/80">Việc làm nổi bật</p>
          <h1 class="mt-3 text-3xl font-bold md:text-5xl">Tìm công việc phù hợp với bạn</h1>
          <p class="mt-4 max-w-2xl text-sm leading-7 text-blue-50/85 md:text-base">
            Tìm kiếm tin tuyển dụng đang hoạt động theo từ khóa, ngành nghề và địa điểm để bắt đầu hành trình ứng tuyển nhanh hơn.
          </p>
        </div>
        <div class="rounded-2xl border border-white/15 bg-white/10 px-5 py-4 backdrop-blur">
          <p class="text-sm text-blue-100/80">Kết quả hiện tại</p>
          <p class="mt-2 text-3xl font-bold">{{ pagination.total }}</p>
          <p class="mt-2 text-sm text-blue-100/80">tin tuyển dụng đang hiển thị</p>
        </div>
      </div>
    </div>

    <div class="mt-8 flex flex-col gap-6 lg:flex-row lg:items-start">
      <aside class="w-full shrink-0 lg:w-80">
        <div class="sticky top-6 overflow-hidden rounded-[30px] border border-slate-200 bg-white shadow-[0_18px_50px_-24px_rgba(15,23,42,0.35)]">
          <div class="border-b border-slate-200 bg-slate-50/80 px-6 py-5">
            <div class="flex flex-nowrap items-center justify-between gap-4">
              <div class="min-w-0 flex-1">
                <div class="flex items-center gap-2 leading-none text-slate-900">
                  <span class="material-symbols-outlined text-[20px]">filter_alt</span>
                  <p class="text-[13px] font-extrabold uppercase tracking-[0.12em] sm:text-[14px]">Bộ lọc tìm việc</p>
                </div>
              </div>
              <button
                class="inline-flex shrink-0 items-center justify-center self-center rounded-full border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-600 transition hover:border-blue-200 hover:text-blue-600"
                type="button"
                @click="resetFilters"
              >
                Xóa lọc
              </button>
            </div>
            <p class="mt-3 text-sm leading-6 text-slate-500">Thu hẹp kết quả theo danh mục nghề, khu vực và nhu cầu tìm kiếm hiện tại.</p>
          </div>

          <form class="space-y-6 px-6 py-6" @submit.prevent="applyFilters">
            <section class="border-b border-dashed border-slate-200 pb-6">
              <div class="flex items-center justify-between gap-3">
                <h3 class="text-[15px] font-extrabold text-slate-800">Từ khóa tìm kiếm</h3>
                <span class="rounded-full bg-blue-50 px-3 py-1 text-[11px] font-bold uppercase tracking-[0.18em] text-blue-700">Keyword</span>
              </div>
              <div class="relative mt-4">
                <span class="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-slate-400">search</span>
                <input
                  v-model="filters.search"
                  class="w-full rounded-2xl border border-slate-200 bg-slate-50 py-3 pl-12 pr-4 text-sm text-slate-700 outline-none transition focus:border-emerald-500 focus:bg-white"
                  placeholder="VD: Backend Laravel, UI Designer..."
                  type="text"
                />
              </div>
            </section>

            <section class="border-b border-dashed border-slate-200 pb-6">
              <div class="flex items-center justify-between gap-3">
                <h3 class="text-[15px] font-extrabold text-slate-800">Theo danh mục nghề</h3>
                <span class="text-xs font-semibold text-slate-400">{{ selectedIndustryName }}</span>
              </div>

              <div class="mt-4 space-y-3">
                <label class="flex cursor-pointer items-center gap-3 rounded-2xl border border-slate-200 px-4 py-3 transition hover:border-emerald-300 hover:bg-emerald-50/50">
                  <input
                    :checked="!filters.nganh_nghe_id"
                    class="h-4 w-4 accent-emerald-600"
                    type="checkbox"
                    @change="filters.nganh_nghe_id = ''"
                  />
                  <span class="text-sm font-semibold text-slate-700">Tất cả ngành nghề</span>
                </label>

                <label
                  v-for="industry in visibleIndustries"
                  :key="industry.id"
                  class="flex cursor-pointer items-start gap-3 rounded-2xl px-1 py-1 transition"
                >
                  <input
                    :checked="String(filters.nganh_nghe_id) === String(industry.id)"
                    class="mt-1 h-4 w-4 shrink-0 accent-emerald-600"
                    type="checkbox"
                    @change="selectIndustry(industry.id)"
                  />
                  <span class="text-sm leading-6 text-slate-700">{{ industry.ten_nganh }}</span>
                </label>
              </div>

              <div class="mt-3 flex items-center justify-between">
                <p v-if="industriesLoading" class="text-xs text-slate-400">Đang tải danh mục ngành nghề...</p>
                <button
                  v-else-if="industries.length > 5"
                  class="text-sm font-bold text-emerald-600 transition hover:text-emerald-700"
                  type="button"
                  @click="showAllIndustries = !showAllIndustries"
                >
                  {{ showAllIndustries ? 'Thu gọn' : 'Xem thêm' }}
                </button>
              </div>
            </section>

            <section class="border-b border-dashed border-slate-200 pb-6">
              <h3 class="text-[15px] font-extrabold text-slate-800">Khu vực làm việc</h3>
              <div class="relative mt-4">
                <span class="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-slate-400">location_on</span>
                <select
                  v-model="filters.dia_diem"
                  class="w-full rounded-2xl border border-slate-200 bg-slate-50 py-3 pl-12 pr-4 text-sm text-slate-700 outline-none transition focus:border-emerald-500 focus:bg-white"
                >
                  <option value="">Tất cả tỉnh/thành</option>
                  <option v-for="province in VIETNAM_PROVINCES_34" :key="province" :value="province">
                    {{ province }}
                  </option>
                </select>
              </div>
            </section>

            <section>
              <h3 class="text-[15px] font-extrabold text-slate-800">Số kết quả mỗi trang</h3>
              <div class="mt-4 grid grid-cols-2 gap-3">
                <label
                  v-for="size in pageSizeOptions"
                  :key="size"
                  class="flex cursor-pointer items-center gap-3 rounded-2xl border px-4 py-3 transition"
                  :class="Number(filters.per_page) === size
                    ? 'border-emerald-500 bg-emerald-50 text-emerald-700'
                    : 'border-slate-200 bg-white text-slate-700 hover:border-slate-300 hover:bg-slate-50'"
                >
                  <input
                    v-model="filters.per_page"
                    :value="size"
                    class="h-4 w-4 accent-emerald-600"
                    type="radio"
                  />
                  <span class="text-sm font-semibold">{{ size }} tin</span>
                </label>
              </div>
            </section>

            <button
              class="w-full rounded-2xl bg-emerald-600 px-4 py-3.5 text-sm font-bold text-white transition hover:bg-emerald-700"
              type="submit"
            >
              Áp dụng bộ lọc
            </button>
          </form>
        </div>
      </aside>

      <section class="min-w-0 flex-1 space-y-6">
        <div class="flex flex-col gap-4 rounded-[24px] border border-slate-200 bg-white px-5 py-5 shadow-sm md:flex-row md:items-center md:justify-between">
          <div>
            <h2 class="text-2xl font-bold text-slate-900">Danh sách việc làm</h2>
            <p class="mt-2 text-sm text-slate-500">{{ summaryText }}</p>
          </div>
          <div class="flex flex-wrap gap-2" v-if="hasActiveFilters">
            <span
              v-if="filters.search"
              class="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700"
            >
              Từ khóa: {{ filters.search }}
            </span>
            <span
              v-if="filters.dia_diem"
              class="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700"
            >
              Địa điểm: {{ filters.dia_diem }}
            </span>
            <span
              v-if="filters.nganh_nghe_id"
              class="rounded-full bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-700"
            >
              Ngành nghề đã chọn
            </span>
          </div>
        </div>

        <div v-if="loading" class="mt-6 grid gap-4">
          <div
            v-for="index in 3"
            :key="index"
            class="h-56 animate-pulse rounded-[24px] border border-slate-200 bg-white"
          />
        </div>

        <div v-else-if="!jobs.length" class="mt-6 rounded-[24px] border border-dashed border-slate-300 bg-white px-6 py-12 text-center shadow-sm">
          <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-slate-100">
            <span class="material-symbols-outlined text-3xl text-slate-500">work_off</span>
          </div>
          <h3 class="mt-5 text-xl font-bold text-slate-900">Chưa tìm thấy việc làm phù hợp</h3>
          <p class="mx-auto mt-3 max-w-xl text-sm leading-7 text-slate-500">
            Hãy thử thay đổi từ khóa, bỏ bớt bộ lọc hoặc tìm theo địa điểm khác để xem thêm kết quả.
          </p>
          <button
            class="mt-6 rounded-2xl border border-slate-200 px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
            type="button"
            @click="resetFilters"
          >
            Xóa bộ lọc và tìm lại
          </button>
        </div>

        <div v-else class="mt-6 space-y-5">
          <article
            v-for="job in jobs"
            :key="job.id"
            class="group rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-0.5 hover:border-blue-200 hover:shadow-lg"
          >
            <div class="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
              <div class="min-w-0 flex-1">
                <div class="flex flex-wrap items-start justify-between gap-4">
                  <div class="min-w-0">
                    <div class="flex flex-wrap items-center gap-3">
                      <RouterLink
                        :to="{ name: 'JobDetail', params: { id: job.id } }"
                        class="text-xl font-bold text-slate-900 transition group-hover:text-blue-600"
                      >
                        {{ job.tieu_de }}
                      </RouterLink>
                      <span
                        v-if="job.is_featured"
                        class="rounded-full bg-amber-400/15 px-3 py-1 text-xs font-bold uppercase tracking-[0.16em] text-amber-700"
                      >
                        Featured
                      </span>
                    </div>
                    <p class="mt-2 text-sm font-semibold text-blue-600">
                      {{ job.cong_ty?.ten_cong_ty || 'Công ty đang cập nhật' }}
                    </p>
                  </div>
                  <div class="rounded-2xl bg-slate-50 px-3 py-2 text-right">
                    <p class="text-lg font-bold text-slate-900">{{ formatSalary(job) }}</p>
                    <p class="mt-1 text-xs text-slate-500">{{ formatRelativeDate(job.created_at) }}</p>
                  </div>
                </div>

                <div class="mt-4 flex flex-wrap gap-x-5 gap-y-2 text-sm text-slate-500">
                  <span class="inline-flex items-center gap-1.5">
                    <span class="material-symbols-outlined text-base">location_on</span>
                    {{ job.dia_diem_lam_viec || 'Địa điểm đang cập nhật' }}
                  </span>
                  <span class="inline-flex items-center gap-1.5">
                    <span class="material-symbols-outlined text-base">schedule</span>
                    {{ job.hinh_thuc_lam_viec || 'Đang cập nhật' }}
                  </span>
                  <span class="inline-flex items-center gap-1.5">
                    <span class="material-symbols-outlined text-base">workspace_premium</span>
                    {{ job.cap_bac || 'Chưa rõ cấp bậc' }}
                  </span>
                </div>

                <p class="mt-4 line-clamp-2 text-sm leading-7 text-slate-600">
                  {{ job.mo_ta_cong_viec || 'Mô tả công việc đang được cập nhật.' }}
                </p>

                <div class="mt-4 flex flex-wrap gap-2">
                  <span
                    v-for="industry in job.nganh_nghes || []"
                    :key="industry.id"
                    class="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700"
                  >
                    {{ industry.ten_nganh }}
                  </span>
                  <span
                    v-if="job.kinh_nghiem_yeu_cau"
                    class="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700"
                  >
                    {{ job.kinh_nghiem_yeu_cau }}
                  </span>
                  <span
                    class="rounded-full px-3 py-1 text-xs font-semibold"
                    :class="isQuotaFull(job) ? 'bg-rose-50 text-rose-700' : 'bg-emerald-50 text-emerald-700'"
                  >
                    {{ getAcceptedCount(job) }}/{{ job.so_luong_tuyen || 0 }} đã nhận · {{ isQuotaFull(job) ? 'Đã đủ chỉ tiêu' : `${getRemainingSlots(job)} còn lại` }}
                  </span>
                </div>
              </div>

              <div class="flex shrink-0 gap-3 lg:flex-col">
                <button
                  class="rounded-2xl border px-4 py-3 text-sm font-semibold transition"
                  :class="isSaved(job.id)
                    ? 'border-blue-200 bg-blue-50 text-blue-700 hover:bg-blue-100'
                    : 'border-slate-200 text-slate-700 hover:bg-slate-50'"
                  type="button"
                  @click="toggleSavedJob(job.id)"
                >
                  {{
                    togglingJobId === job.id
                      ? 'Đang xử lý...'
                      : isSaved(job.id)
                        ? 'Đã lưu'
                        : 'Lưu tin'
                  }}
                </button>
                <RouterLink
                  :to="{ name: 'JobDetail', params: { id: job.id } }"
                  class="rounded-2xl bg-blue-600 px-5 py-3 text-center text-sm font-bold text-white transition hover:bg-blue-700"
                >
                  Xem chi tiết
                </RouterLink>
              </div>
            </div>
          </article>
        </div>

        <div v-if="pagination.last_page > 1" class="mt-8 flex flex-wrap items-center justify-center gap-2">
          <button
            class="rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
            :disabled="pagination.current_page === 1"
            type="button"
            @click="changePage(pagination.current_page - 1)"
          >
            Trước
          </button>

          <button
            v-for="page in pagination.last_page"
            :key="page"
            class="h-11 min-w-11 rounded-xl border px-4 text-sm font-bold transition"
            :class="page === pagination.current_page
              ? 'border-blue-600 bg-blue-600 text-white'
              : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'"
            type="button"
            @click="changePage(page)"
          >
            {{ page }}
          </button>

          <button
            class="rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
            :disabled="pagination.current_page === pagination.last_page"
            type="button"
            @click="changePage(pagination.current_page + 1)"
          >
            Sau
          </button>
        </div>
      </section>
    </div>
  </div>
</template>
