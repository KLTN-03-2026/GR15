<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { employerCandidateService } from '@/services/api'
import { useEmployerCompanyPermissions } from '@/composables/useEmployerCompanyPermissions'
import { useNotify } from '@/composables/useNotify'
import { getAuthToken } from '@/utils/authStorage'
import { hasBuilderCv, openCvPrintPreview } from '@/utils/profileCvBuilder'

const notify = useNotify()
const { currentInternalRoleLabel, ensurePermissionsLoaded } = useEmployerCompanyPermissions()

const loading = ref(false)
const candidates = ref([])
const pagination = ref(null)
const selectedCvByCandidate = reactive({})

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
  { value: 'Trung học', label: 'Trung học' },
  { value: 'Trung cấp', label: 'Trung cấp' },
  { value: 'Cao đẳng', label: 'Cao đẳng' },
  { value: 'Đại học', label: 'Đại học' },
  { value: 'Thạc sĩ', label: 'Thạc sĩ' },
  { value: 'Tiến sĩ', label: 'Tiến sĩ' },
  { value: 'Khác', label: 'Khác' },
]

const stats = computed(() => {
  const all = candidates.value
  const senior = all.filter((item) => Number(item.kinh_nghiem_nam || 0) >= 5).length
  const availableCv = all.filter((item) => (item.ho_sos || []).some((profile) => canOpenProfileCv(profile))).length
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
      label: 'Có CV xem được',
      value: availableCv,
      hint: 'Gồm file upload và CV tạo trên hệ thống',
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
  return `Hiển thị ${pagination.value.from || 0}-${pagination.value.to || 0} trên ${pagination.value.total || 0} ứng viên`
})

const degreeLabel = (value) => {
  const match = degreeOptions.find((item) => item.value === value || item.label === value)
  return match?.label || value || 'Chưa cập nhật'
}

const formatYears = (value) => {
  const years = Number(value || 0)
  if (!years) return 'Chưa cập nhật kinh nghiệm'
  return `${years} năm kinh nghiệm`
}

const truncate = (text, max = 360) => {
  if (!text) return 'Ứng viên chưa bổ sung mô tả bản thân.'
  return text.length > max ? `${text.slice(0, max).trim()}...` : text
}

const candidateProfiles = (candidate) => Array.isArray(candidate?.ho_sos) ? candidate.ho_sos : []

const getSelectedProfile = (candidate) => {
  const profiles = candidateProfiles(candidate)
  if (!profiles.length) return candidate?.ho_so_mac_dinh || candidate

  const selectedId = selectedCvByCandidate[candidate.id]
  return profiles.find((profile) => Number(profile.id) === Number(selectedId))
    || candidate.ho_so_mac_dinh
    || profiles[0]
}

const profileOptionLabel = (profile, index) => {
  const title = profile?.tieu_de_ho_so || `CV ${index + 1}`
  const source = hasBuilderCv(profile) && !profile?.file_cv_url ? 'Tạo trên hệ thống' : 'Upload file'
  const template = profile?.ten_template_cv ? ` - ${profile.ten_template_cv}` : ''
  return `${title} (${source}${template})`
}

const canOpenProfileCv = (profile) => Boolean(profile?.file_cv_url || hasBuilderCv(profile))

const syncDefaultCvSelections = () => {
  candidates.value.forEach((candidate) => {
    const profile = getSelectedProfile(candidate)
    if (candidate?.id && profile?.id && !selectedCvByCandidate[candidate.id]) {
      selectedCvByCandidate[candidate.id] = profile.id
    }
  })
}

const fetchCandidates = async () => {
  loading.value = true
  try {
    const response = await employerCandidateService.getCandidates(filters)
    const payload = response?.data || {}
    candidates.value = payload.data || []
    pagination.value = payload
    syncDefaultCvSelections()
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
  const selectedProfile = getSelectedProfile(candidate)
  const cvUrl = selectedProfile?.file_cv_url

  if (!canOpenProfileCv(selectedProfile)) {
    notify.info('CV đang chọn chưa có file upload hoặc dữ liệu CV tạo trên hệ thống để xem.')
    return
  }

  if (!cvUrl && hasBuilderCv(selectedProfile)) {
    const opened = openCvPrintPreview({
      profile: selectedProfile,
      owner: candidate?.nguoi_dung,
    })

    if (!opened) {
      notify.warning('Trình duyệt đang chặn cửa sổ xem CV. Hãy cho phép popup và thử lại.')
    }
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
          placeholder="Tìm theo tên ứng viên, email, tiêu đề CV, mô tả hoặc mục tiêu nghề nghiệp..."
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
      Chưa có ứng viên công khai nào phù hợp với bộ lọc hiện tại.
    </div>

    <div v-else class="grid grid-cols-1 gap-4">
      <div
        v-for="candidate in candidates"
        :key="candidate.id"
        class="grid grid-cols-1 gap-5 rounded-xl border border-slate-200 bg-white p-5 transition-shadow hover:shadow-md dark:border-slate-800 dark:bg-slate-900 xl:grid-cols-[minmax(0,1fr)_240px]"
      >
        <div class="flex min-w-0 flex-col gap-4 sm:flex-row sm:items-start">
          <div class="relative shrink-0">
            <div class="size-16 rounded-full border-2 border-[#2463eb]/20 p-0.5">
              <div class="flex h-full w-full items-center justify-center overflow-hidden rounded-full bg-slate-200 text-slate-500 dark:bg-slate-700">
                <img
                  v-if="candidate.nguoi_dung?.avatar_url"
                  :src="candidate.nguoi_dung.avatar_url"
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

          <div class="min-w-0 flex-1">
            <div class="flex flex-col gap-2 lg:flex-row lg:items-start lg:justify-between">
              <div class="min-w-0">
                <h4 class="truncate text-lg font-bold text-slate-900 dark:text-slate-100">
                  {{ candidate.nguoi_dung?.ho_ten || 'Ứng viên công khai' }}
                </h4>
                <p class="mt-0.5 truncate text-sm text-slate-500">
                  {{ getSelectedProfile(candidate)?.tieu_de_ho_so || 'Chưa có tiêu đề CV' }}
                </p>
              </div>
              <span class="w-fit rounded-full bg-emerald-100 px-3 py-1 text-[10px] font-bold uppercase tracking-tight text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300">
                Công khai
              </span>
            </div>

            <div class="mt-3 flex flex-wrap items-center gap-2">
              <span class="rounded-full bg-[#2463eb]/10 px-2.5 py-1 text-[10px] font-bold uppercase tracking-tight text-[#2463eb]">
                {{ formatYears(getSelectedProfile(candidate)?.kinh_nghiem_nam || candidate.kinh_nghiem_nam) }}
              </span>
              <span class="rounded-full bg-sky-100 px-2.5 py-1 text-[10px] font-bold uppercase tracking-tight text-sky-700 dark:bg-sky-900/30 dark:text-sky-300">
                {{ degreeLabel(getSelectedProfile(candidate)?.trinh_do || candidate.trinh_do) }}
              </span>
              <span class="rounded-full bg-violet-100 px-2.5 py-1 text-[10px] font-bold uppercase tracking-tight text-violet-700 dark:bg-violet-900/30 dark:text-violet-300">
                {{ candidate.so_luong_cv || candidateProfiles(candidate).length || 1 }} CV công khai
              </span>
              <span
                v-if="candidate.nguoi_dung?.email"
                class="rounded-full bg-slate-100 px-2.5 py-1 text-[10px] font-bold uppercase tracking-tight text-slate-600 dark:bg-slate-800 dark:text-slate-300"
              >
                {{ candidate.nguoi_dung.email }}
              </span>
              <span class="rounded-full bg-slate-100 px-2.5 py-1 text-[10px] font-bold uppercase tracking-tight text-slate-500 dark:bg-slate-800 dark:text-slate-300">
                {{ candidate.nguoi_dung?.so_dien_thoai || 'Chưa có SĐT' }}
              </span>
            </div>

            <p class="mt-4 text-sm leading-7 text-slate-500 dark:text-slate-400">
              {{ truncate(getSelectedProfile(candidate)?.mo_ta_ban_than || getSelectedProfile(candidate)?.muc_tieu_nghe_nghiep) }}
            </p>
          </div>
        </div>

        <div class="flex flex-col gap-3 border-t border-slate-100 pt-4 dark:border-slate-800 xl:border-l xl:border-t-0 xl:pl-5 xl:pt-1">
          <select
            v-if="candidateProfiles(candidate).length > 1"
            v-model="selectedCvByCandidate[candidate.id]"
            class="h-10 w-full rounded-lg border border-slate-200 bg-slate-50 px-3 text-xs font-semibold text-slate-800 outline-none transition focus:border-[#2463eb] dark:border-slate-700 dark:bg-slate-800 dark:text-white"
          >
            <option
              v-for="(profile, index) in candidateProfiles(candidate)"
              :key="profile.id"
              :value="profile.id"
            >
              {{ profileOptionLabel(profile, index) }}
            </option>
          </select>
          <p v-else class="truncate rounded-lg bg-slate-50 px-3 py-2 text-xs font-semibold text-slate-500 dark:bg-slate-800 dark:text-slate-300">
            {{ profileOptionLabel(getSelectedProfile(candidate), 0) }}
          </p>
          <button
            class="flex h-10 items-center justify-center gap-2 rounded-lg bg-slate-100 px-4 text-sm font-bold text-slate-700 transition-colors hover:bg-slate-200 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-slate-800 dark:text-slate-200"
            :disabled="!canOpenProfileCv(getSelectedProfile(candidate))"
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
