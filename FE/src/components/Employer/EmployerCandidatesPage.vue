<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { employerCandidateService } from '@/services/api'
import { useEmployerCompanyPermissions } from '@/composables/useEmployerCompanyPermissions'
import { useNotify } from '@/composables/useNotify'
import { getAuthToken } from '@/utils/authStorage'

const notify = useNotify()
const { currentInternalRoleLabel, ensurePermissionsLoaded } = useEmployerCompanyPermissions()

const loading = ref(false)
const candidates = ref([])
const pagination = ref(null)

const filters = reactive({
  search: '',
  trinh_do: '',
  kinh_nghiem_tu: '',
  kinh_nghiem_den: '',
  sort_by: 'created_at',
  sort_dir: 'desc',
  per_page: 10,
  page: 1,
})

const degreeOptions = [
  { value: '', label: 'Tất cả trình độ' },
  { value: 'trung_hoc', label: 'Trung học' },
  { value: 'trung_cap', label: 'Trung cấp' },
  { value: 'cao_dang', label: 'Cao đẳng' },
  { value: 'dai_hoc', label: 'Đại học' },
  { value: 'thac_si', label: 'Thạc sĩ' },
  { value: 'tien_si', label: 'Tiến sĩ' },
  { value: 'khac', label: 'Khác' },
]

const stats = computed(() => {
  const all = candidates.value
  const senior = all.filter((item) => Number(item.kinh_nghiem_nam || 0) >= 5).length
  const availableCv = all.filter((item) => item.file_cv).length
  const degreeCount = new Set(all.map((item) => item.trinh_do).filter(Boolean)).size

  return [
    {
      label: 'Ứng viên công khai',
      value: pagination.value?.total ?? all.length,
      hint: 'Có thể xem ngay từ hệ thống',
      icon: 'groups',
      tone: 'text-blue-300 bg-blue-500/10',
    },
    {
      label: 'Từ 5 năm kinh nghiệm',
      value: senior,
      hint: 'Nguồn ứng viên senior hiện có',
      icon: 'military_tech',
      tone: 'text-violet-300 bg-violet-500/10',
    },
    {
      label: 'Có file CV',
      value: availableCv,
      hint: 'Sẵn sàng để xem nhanh',
      icon: 'description',
      tone: 'text-emerald-300 bg-emerald-500/10',
    },
    {
      label: 'Nhóm trình độ',
      value: degreeCount,
      hint: 'Đang xuất hiện trong kết quả',
      icon: 'school',
      tone: 'text-amber-300 bg-amber-500/10',
    },
  ]
})

const paginationSummary = computed(() => {
  if (!pagination.value) return 'Chưa có dữ liệu'
  return `Hiển thị ${pagination.value.from || 0}-${pagination.value.to || 0} trên ${pagination.value.total || 0} hồ sơ`
})

const degreeLabel = (value) => {
  const match = degreeOptions.find((item) => item.value === value)
  return match?.label || 'Chưa cập nhật'
}

const formatYears = (value) => {
  const years = Number(value || 0)
  if (!years) return 'Chưa cập nhật kinh nghiệm'
  return `${years} năm kinh nghiệm`
}

const truncate = (text, max = 180) => {
  if (!text) return 'Ứng viên chưa bổ sung mô tả bản thân.'
  return text.length > max ? `${text.slice(0, max).trim()}...` : text
}

const fetchCandidates = async () => {
  loading.value = true
  try {
    const response = await employerCandidateService.getCandidates(filters)
    const payload = response?.data || {}
    candidates.value = payload.data || []
    pagination.value = payload
  } catch (error) {
    candidates.value = []
    pagination.value = null
    notify.apiError(error, 'Không tải được danh sách ứng viên.')
  } finally {
    loading.value = false
  }
}

const applyFilters = async () => {
  filters.page = 1
  await fetchCandidates()
}

const resetFilters = async () => {
  filters.search = ''
  filters.trinh_do = ''
  filters.kinh_nghiem_tu = ''
  filters.kinh_nghiem_den = ''
  filters.sort_by = 'created_at'
  filters.sort_dir = 'desc'
  filters.per_page = 10
  filters.page = 1
  await fetchCandidates()
}

const goToPage = async (page) => {
  if (!page || page === filters.page) return
  filters.page = page
  await fetchCandidates()
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
  const cvUrl = candidate.file_cv_url

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
  } catch (error) {
    notify.error('Không mở được file CV. Vui lòng thử lại.')
  }
}

onMounted(async () => {
  await Promise.all([ensurePermissionsLoaded(), fetchCandidates()])
})
</script>

<template>
  <div class="max-w-6xl mx-auto">
    <div class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h3 class="text-3xl font-bold leading-tight text-slate-900 dark:text-slate-100">Ứng viên</h3>
        <p class="mt-1 text-sm text-slate-500">
          Xem các hồ sơ công khai trong hệ thống, lọc nhanh theo trình độ và kinh nghiệm.
        </p>
      </div>
      <div class="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm text-slate-500 shadow-sm dark:border-slate-800 dark:bg-slate-900 dark:text-slate-400">
        Gợi ý: mở CV trực tiếp từ từng hồ sơ công khai để đánh giá nhanh ứng viên.
      </div>
    </div>

    <div class="mb-6 rounded-2xl border border-slate-200 bg-slate-50 px-5 py-4 text-sm text-slate-600 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300">
      Vai trò hiện tại: <span class="font-bold">{{ currentInternalRoleLabel }}</span>. Màn ứng viên được mở ở chế độ tra cứu hồ sơ công khai trong hệ thống.
    </div>

    <div class="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <div
        v-for="card in stats"
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
      <div class="grid grid-cols-1 gap-3 border-b border-slate-200 p-4 dark:border-slate-800 xl:grid-cols-[minmax(0,1.4fr)_220px_140px_140px_170px]">
        <input
          v-model="filters.search"
          class="w-full rounded-lg border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-[#2463eb] dark:border-slate-800 dark:bg-slate-800/70 dark:text-white"
          placeholder="Tìm theo tiêu đề hồ sơ, mô tả hoặc mục tiêu nghề nghiệp..."
          type="text"
          @keyup.enter="applyFilters"
        >
        <select
          v-model="filters.trinh_do"
          class="rounded-lg border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-[#2463eb] dark:border-slate-800 dark:bg-slate-800/70 dark:text-white"
          @change="applyFilters"
        >
          <option v-for="option in degreeOptions" :key="option.value || 'all'" :value="option.value">
            {{ option.label }}
          </option>
        </select>
        <input
          v-model="filters.kinh_nghiem_tu"
          class="rounded-lg border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-[#2463eb] dark:border-slate-800 dark:bg-slate-800/70 dark:text-white"
          min="0"
          placeholder="KN từ"
          type="number"
        >
        <input
          v-model="filters.kinh_nghiem_den"
          class="rounded-lg border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-[#2463eb] dark:border-slate-800 dark:bg-slate-800/70 dark:text-white"
          min="0"
          placeholder="KN đến"
          type="number"
        >
        <div class="flex gap-2">
          <button
            class="flex-1 rounded-lg bg-[#2463eb] px-4 py-2.5 text-sm font-bold text-white transition hover:bg-blue-700"
            type="button"
            @click="applyFilters"
          >
            Lọc
          </button>
          <button
            class="rounded-lg border border-slate-200 px-4 py-2.5 text-sm font-bold text-slate-600 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
            type="button"
            @click="resetFilters"
          >
            Reset
          </button>
        </div>
      </div>

      <div class="flex items-center justify-between px-4 py-3 text-xs text-slate-500 dark:text-slate-400">
        <span>{{ paginationSummary }}</span>
        <div class="flex items-center gap-2">
          <span>Sắp xếp</span>
          <select
            v-model="filters.sort_by"
            class="rounded-md border border-slate-200 bg-slate-50 px-2 py-1 text-xs dark:border-slate-700 dark:bg-slate-800"
            @change="applyFilters"
          >
            <option value="created_at">Mới nhất</option>
            <option value="kinh_nghiem_nam">Kinh nghiệm</option>
            <option value="tieu_de_ho_so">Tiêu đề hồ sơ</option>
            <option value="trinh_do">Trình độ</option>
          </select>
          <select
            v-model="filters.sort_dir"
            class="rounded-md border border-slate-200 bg-slate-50 px-2 py-1 text-xs dark:border-slate-700 dark:bg-slate-800"
            @change="applyFilters"
          >
            <option value="desc">Giảm dần</option>
            <option value="asc">Tăng dần</option>
          </select>
        </div>
      </div>
    </div>

    <div v-if="loading" class="grid grid-cols-1 gap-4">
      <div v-for="index in 4" :key="index" class="h-40 animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800" />
    </div>

    <div v-else-if="!candidates.length" class="rounded-xl border border-slate-200 bg-white p-10 text-center text-sm text-slate-500 shadow-sm dark:border-slate-800 dark:bg-slate-900 dark:text-slate-400">
      Chưa có hồ sơ công khai nào phù hợp với bộ lọc hiện tại.
    </div>

    <div v-else class="grid grid-cols-1 gap-4">
      <div
        v-for="candidate in candidates"
        :key="candidate.id"
        class="flex flex-col gap-6 rounded-xl border border-slate-200 bg-white p-5 transition-shadow hover:shadow-md dark:border-slate-800 dark:bg-slate-900 lg:flex-row lg:items-center"
      >
        <div class="flex flex-1 items-center gap-4">
          <div class="relative">
            <div class="size-16 rounded-full border-2 border-[#2463eb]/20 p-0.5">
              <div class="flex h-full w-full items-center justify-center overflow-hidden rounded-full bg-slate-200 text-slate-500 dark:bg-slate-700">
                <img
                  v-if="candidate.nguoi_dung?.anh_dai_dien"
                  :src="candidate.nguoi_dung.anh_dai_dien"
                  alt="avatar"
                  class="h-full w-full object-cover"
                >
                <span v-else class="text-2xl font-bold">
                  {{ (candidate.nguoi_dung?.ho_ten || candidate.tieu_de_ho_so || 'U').charAt(0).toUpperCase() }}
                </span>
              </div>
            </div>
            <div class="absolute -bottom-1 -right-1 size-4 rounded-full border-2 border-white bg-green-500 dark:border-slate-900" title="Công khai"></div>
          </div>

          <div>
            <h4 class="text-lg font-bold text-slate-900 dark:text-slate-100">
              {{ candidate.nguoi_dung?.ho_ten || 'Ứng viên công khai' }}
            </h4>
            <p class="text-sm text-slate-500">
              {{ candidate.tieu_de_ho_so }} • {{ degreeLabel(candidate.trinh_do) }}
            </p>
            <div class="mt-2 flex flex-wrap items-center gap-2">
              <span class="rounded-full bg-[#2463eb]/10 px-2 py-0.5 text-[10px] font-bold uppercase tracking-tight text-[#2463eb]">
                {{ formatYears(candidate.kinh_nghiem_nam) }}
              </span>
              <span
                v-if="candidate.nguoi_dung?.email"
                class="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-bold uppercase tracking-tight text-slate-600 dark:bg-slate-800 dark:text-slate-300"
              >
                {{ candidate.nguoi_dung.email }}
              </span>
            </div>
            <p class="mt-3 max-w-2xl text-sm leading-7 text-slate-500 dark:text-slate-400">
              {{ truncate(candidate.mo_ta_ban_than || candidate.muc_tieu_nghe_nghiep) }}
            </p>
          </div>
        </div>

        <div class="flex items-center gap-8 lg:px-6 lg:border-x lg:border-slate-100 dark:lg:border-slate-800">
          <div class="flex flex-col items-center min-w-[132px]">
            <div class="flex items-center gap-1 text-[#2463eb]">
              <span class="material-symbols-outlined text-[20px]">school</span>
              <span class="text-lg font-black">{{ degreeLabel(candidate.trinh_do) }}</span>
            </div>
            <p class="mt-1 text-[10px] font-bold uppercase tracking-widest text-slate-400">Trình độ</p>
          </div>
          <div class="flex flex-col min-w-[156px]">
            <span class="rounded-full bg-emerald-100 px-2.5 py-1 text-center text-[10px] font-bold uppercase text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300">
              Công khai
            </span>
            <p class="mt-1 text-center text-[10px] font-medium text-slate-400">
              {{ candidate.nguoi_dung?.so_dien_thoai || 'Chưa có số điện thoại' }}
            </p>
          </div>
        </div>

        <div class="ml-auto flex items-center gap-3">
          <button
            class="flex h-10 items-center justify-center gap-2 rounded-lg bg-slate-100 px-4 text-sm font-bold text-slate-700 transition-colors hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-200"
            type="button"
            @click="openCv(candidate)"
          >
            <span class="material-symbols-outlined text-[18px]">description</span>
            Xem CV
          </button>
        </div>
      </div>
    </div>

    <div class="mt-8 flex items-center justify-between px-2">
      <p class="text-sm text-slate-500">{{ paginationSummary }}</p>
      <div class="flex gap-2">
        <button
          class="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 text-slate-500 transition hover:bg-slate-50 disabled:opacity-50 dark:border-slate-800"
          :disabled="!pagination?.prev_page_url"
          type="button"
          @click="goToPage((pagination?.current_page || 1) - 1)"
        >
          <span class="material-symbols-outlined text-[20px]">chevron_left</span>
        </button>
        <button class="flex h-9 min-w-9 items-center justify-center rounded-lg bg-[#2463eb] px-3 text-sm font-bold text-white">
          {{ pagination?.current_page || 1 }}
        </button>
        <button
          class="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 text-slate-500 transition hover:bg-slate-50 disabled:opacity-50 dark:border-slate-800"
          :disabled="!pagination?.next_page_url"
          type="button"
          @click="goToPage((pagination?.current_page || 1) + 1)"
        >
          <span class="material-symbols-outlined text-[20px]">chevron_right</span>
        </button>
      </div>
    </div>
  </div>
</template>
