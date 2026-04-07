<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { adminProfileService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'
import { formatDateTimeVN } from '@/utils/dateTime'

const notify = useNotify()

const ACTIVE_TAB = 'active'
const ARCHIVED_TAB = 'archived'

const loading = ref(false)
const detailLoading = ref(false)
const error = ref('')
const activeTab = ref(ACTIVE_TAB)
const profiles = ref([])
const selectedProfile = ref(null)
const currentPage = ref(1)
const perPage = ref(10)
const totalProfiles = ref(0)

const searchQuery = ref('')
const selectedStatus = ref('')
const selectedEducation = ref('')
const sortBy = ref('created_at')
const sortDir = ref('desc')

const showDetailModal = ref(false)
const showArchiveModal = ref(false)
const showForceDeleteModal = ref(false)
const deletingProfile = ref(null)
const forceDeletingProfile = ref(null)

const stats = reactive({
  total: 0,
  visible: 0,
  hidden: 0,
  trashed: 0,
  education: {},
})

const educationOptions = [
  { value: '', label: 'Tất cả trình độ' },
  { value: 'trung_hoc', label: 'Trung học' },
  { value: 'trung_cap', label: 'Trung cấp' },
  { value: 'cao_dang', label: 'Cao đẳng' },
  { value: 'dai_hoc', label: 'Đại học' },
  { value: 'thac_si', label: 'Thạc sĩ' },
  { value: 'tien_si', label: 'Tiến sĩ' },
  { value: 'khac', label: 'Khác' },
]

const sortOptions = [
  { value: 'created_at', label: 'Mới tạo' },
  { value: 'tieu_de_ho_so', label: 'Tiêu đề hồ sơ' },
  { value: 'kinh_nghiem_nam', label: 'Kinh nghiệm' },
  { value: 'trinh_do', label: 'Trình độ' },
]

const totalPages = computed(() => Math.max(1, Math.ceil(totalProfiles.value / perPage.value)))
const isArchivedTab = computed(() => activeTab.value === ARCHIVED_TAB)

const summaryCards = computed(() => [
  {
    label: 'Tổng hồ sơ',
    value: stats.total,
    icon: 'description',
    iconClass: 'bg-[#2463eb]/10 text-[#2463eb]',
    description: 'Tất cả hồ sơ ứng viên đang tồn tại',
  },
  {
    label: 'Công khai',
    value: stats.visible,
    icon: 'visibility',
    iconClass: 'bg-emerald-500/10 text-emerald-500',
    description: 'Hồ sơ đang được hiển thị',
  },
  {
    label: 'Đang ẩn',
    value: stats.hidden,
    icon: 'visibility_off',
    iconClass: 'bg-amber-500/10 text-amber-500',
    description: 'Hồ sơ tạm thời không hiển thị',
  },
  {
    label: 'Đang lưu trữ',
    value: stats.trashed,
    icon: 'inventory_2',
    iconClass: 'bg-rose-500/10 text-rose-500',
    description: 'Hồ sơ đang nằm trong lưu trữ',
  },
])

const educationBadges = computed(() => {
  const order = ['dai_hoc', 'cao_dang', 'thac_si', 'tien_si', 'trung_cap', 'trung_hoc', 'khac']
  return order
    .map((key) => ({
      key,
      label: educationOptions.find((item) => item.value === key)?.label || key,
      value: stats.education?.[key] || 0,
    }))
    .filter((item) => item.value > 0)
})

const statusMeta = (status) => {
  if (Number(status) === 1) {
    return {
      label: 'Công khai',
      classes: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400',
      dot: 'bg-emerald-500',
    }
  }

  return {
    label: 'Ẩn',
    classes: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300',
    dot: 'bg-slate-400',
  }
}

const formatEducation = (value) => {
  return educationOptions.find((item) => item.value === value)?.label || 'Chưa cập nhật'
}

const formatDateTime = (value) => {
  return formatDateTimeVN(value, 'Đang cập nhật')
}

const loadStats = async () => {
  try {
    const response = await adminProfileService.getStats()
    const payload = response?.data || {}
    stats.total = payload.tong || 0
    stats.visible = payload.cong_khai || 0
    stats.hidden = payload.an || 0
    stats.trashed = payload.da_xoa_mem || 0
    stats.education = payload.theo_trinh_do || {}
  } catch (err) {
    console.error('Không thể tải thống kê hồ sơ', err)
  }
}

const normalizeListPayload = (response) => {
  const payload = response?.data || {}
  profiles.value = payload.data || []
  totalProfiles.value = payload.total || 0
}

const loadProfiles = async () => {
  loading.value = true
  error.value = ''

  try {
    const commonOptions = {
      page: currentPage.value,
      per_page: perPage.value,
      search: searchQuery.value || undefined,
    }

    const response = isArchivedTab.value
      ? await adminProfileService.getDeletedProfiles(commonOptions)
      : await adminProfileService.getProfiles({
          ...commonOptions,
          trang_thai: selectedStatus.value,
          trinh_do: selectedEducation.value || undefined,
          sort_by: sortBy.value,
          sort_dir: sortDir.value,
        })

    normalizeListPayload(response)
  } catch (err) {
    profiles.value = []
    totalProfiles.value = 0
    error.value = err.message || 'Không thể tải danh sách hồ sơ ứng viên.'
  } finally {
    loading.value = false
  }
}

const refreshAll = async () => {
  await Promise.all([loadProfiles(), loadStats()])
}

const onFilterChange = async () => {
  currentPage.value = 1
  await loadProfiles()
}

const switchTab = async (tab) => {
  if (activeTab.value === tab) return
  activeTab.value = tab
  currentPage.value = 1
  await loadProfiles()
}

const changePage = async (page) => {
  if (page < 1 || page > totalPages.value || page === currentPage.value) return
  currentPage.value = page
  await loadProfiles()
}

const openDetailModal = async (profileId) => {
  detailLoading.value = true
  showDetailModal.value = true
  selectedProfile.value = null

  try {
    const response = await adminProfileService.getProfileById(profileId)
    selectedProfile.value = response?.data || null
  } catch (err) {
    notify.apiError(err, 'Không tải được chi tiết hồ sơ.')
    showDetailModal.value = false
  } finally {
    detailLoading.value = false
  }
}

const toggleStatus = async (profile) => {
  try {
    await adminProfileService.toggleStatus(profile.id)
    notify.success('Đã cập nhật trạng thái hồ sơ')
    await refreshAll()
  } catch (err) {
    notify.apiError(err, 'Không thể cập nhật trạng thái hồ sơ.')
  }
}

const confirmDelete = (profile) => {
  deletingProfile.value = profile
  showArchiveModal.value = true
}

const deleteProfile = async () => {
  if (!deletingProfile.value) return

  try {
    await adminProfileService.deleteProfile(deletingProfile.value.id)
    notify.success('Đã lưu trữ hồ sơ')
    showArchiveModal.value = false
    deletingProfile.value = null
    await refreshAll()
  } catch (err) {
    notify.apiError(err, 'Không thể lưu trữ hồ sơ.')
  }
}

const restoreProfile = async (profile) => {
  try {
    await adminProfileService.restoreProfile(profile.id)
    notify.success('Đã khôi phục hồ sơ')
    await refreshAll()
  } catch (err) {
    notify.apiError(err, 'Không thể khôi phục hồ sơ.')
  }
}

const confirmForceDelete = (profile) => {
  forceDeletingProfile.value = profile
  showForceDeleteModal.value = true
}

const forceDeleteProfile = async () => {
  if (!forceDeletingProfile.value) return

  try {
    await adminProfileService.forceDeleteProfile(forceDeletingProfile.value.id)
    notify.success('Đã xóa vĩnh viễn hồ sơ')
    showForceDeleteModal.value = false
    forceDeletingProfile.value = null
    await refreshAll()
  } catch (err) {
    notify.apiError(err, 'Không thể xóa vĩnh viễn hồ sơ.')
  }
}

onMounted(async () => {
  await refreshAll()
})
</script>

<template>
  <div v-if="error" class="mb-6 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-900 dark:bg-red-900/20 dark:text-red-300">
    {{ error }}
  </div>

  <div class="mb-8 flex flex-wrap items-end justify-between gap-4">
    <div class="flex flex-col gap-2">
      <h1 class="text-3xl font-extrabold tracking-tight">Quản lý hồ sơ ứng viên</h1>
      <p class="max-w-3xl text-base text-slate-500 dark:text-slate-400">
        Theo dõi trạng thái hồ sơ, ẩn/hiện hồ sơ công khai và quản lý khu lưu trữ hồ sơ trong toàn hệ thống.
      </p>
    </div>
  </div>

  <div class="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-4">
    <div
      v-for="card in summaryCards"
      :key="card.label"
      class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900"
    >
      <div class="mb-2 flex items-center justify-between">
        <p class="text-sm font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">{{ card.label }}</p>
        <span class="material-symbols-outlined rounded-lg p-2" :class="card.iconClass">{{ card.icon }}</span>
      </div>
      <p class="text-3xl font-bold">{{ card.value }}</p>
      <div class="mt-2 text-xs text-slate-400">{{ card.description }}</div>
    </div>
  </div>

  <div class="mb-6 flex flex-wrap gap-2">
    <span
      v-for="item in educationBadges"
      :key="item.key"
      class="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-600 shadow-sm dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300"
    >
      <span class="material-symbols-outlined text-[14px]">school</span>
      {{ item.label }}: {{ item.value }}
    </span>
  </div>

  <div class="rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
    <div class="border-b border-slate-200 px-6 py-4 dark:border-slate-800">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div class="flex flex-wrap gap-2">
          <button
            class="rounded-xl px-4 py-2 text-sm font-bold transition"
            :class="activeTab === ACTIVE_TAB ? 'bg-[#2463eb] text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300'"
            type="button"
            @click="switchTab(ACTIVE_TAB)"
          >
            Hồ sơ hiện tại
          </button>
          <button
            class="rounded-xl px-4 py-2 text-sm font-bold transition"
            :class="activeTab === ARCHIVED_TAB ? 'bg-rose-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300'"
            type="button"
            @click="switchTab(ARCHIVED_TAB)"
          >
            Lưu trữ
          </button>
        </div>
        <div class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
          {{ totalProfiles }} hồ sơ
        </div>
      </div>
    </div>

    <div
      class="grid grid-cols-1 gap-4 border-b border-slate-200 px-6 py-5 dark:border-slate-800"
      :class="
        isArchivedTab
          ? 'xl:grid-cols-[minmax(0,1.65fr)_minmax(280px,1fr)_220px]'
          : 'xl:grid-cols-[minmax(0,1.45fr)_260px_260px_200px_200px]'
      "
    >
      <label class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 dark:border-slate-700 dark:bg-slate-800">
        <span class="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-400">Tìm hồ sơ</span>
        <input
          v-model="searchQuery"
          type="text"
          class="w-full bg-transparent text-sm text-slate-700 outline-none dark:text-slate-200"
          placeholder="Tiêu đề hồ sơ, mục tiêu nghề nghiệp..."
          @keyup.enter="onFilterChange"
        >
      </label>

      <label
        v-if="!isArchivedTab"
        class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 dark:border-slate-700 dark:bg-slate-800"
      >
        <span class="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-400">Trạng thái</span>
        <select
          v-model="selectedStatus"
          class="w-full bg-transparent text-sm text-slate-700 outline-none dark:text-slate-200"
          @change="onFilterChange"
        >
          <option value="">Tất cả</option>
          <option value="1">Công khai</option>
          <option value="0">Ẩn</option>
        </select>
      </label>
      <div v-else class="rounded-xl border border-dashed border-slate-200 bg-slate-50 px-4 py-2.5 text-xs leading-6 text-slate-400 dark:border-slate-700 dark:bg-slate-800">
        Lưu trữ hiển thị các hồ sơ đã được cất khỏi danh sách chính.
      </div>

      <label
        v-if="!isArchivedTab"
        class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 dark:border-slate-700 dark:bg-slate-800"
      >
        <span class="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-400">Trình độ</span>
        <select
          v-model="selectedEducation"
          class="w-full bg-transparent text-sm text-slate-700 outline-none dark:text-slate-200"
          @change="onFilterChange"
        >
          <option v-for="option in educationOptions" :key="option.value || 'all'" :value="option.value">
            {{ option.label }}
          </option>
        </select>
      </label>
      <label
        v-else
        class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 dark:border-slate-700 dark:bg-slate-800"
      >
        <span class="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-400">Số dòng / trang</span>
        <select
          v-model="perPage"
          class="w-full bg-transparent text-sm text-slate-700 outline-none dark:text-slate-200"
          @change="onFilterChange"
        >
          <option :value="10">10</option>
          <option :value="15">15</option>
          <option :value="20">20</option>
        </select>
      </label>

      <label
        v-if="!isArchivedTab"
        class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 dark:border-slate-700 dark:bg-slate-800"
      >
        <span class="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-400">Sắp xếp</span>
        <select
          v-model="sortBy"
          class="w-full bg-transparent text-sm text-slate-700 outline-none dark:text-slate-200"
          @change="onFilterChange"
        >
          <option v-for="option in sortOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
        </select>
      </label>
      <label
        v-if="!isArchivedTab"
        class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 dark:border-slate-700 dark:bg-slate-800"
      >
        <span class="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-400">Chiều sắp xếp</span>
        <select
          v-model="sortDir"
          class="w-full bg-transparent text-sm text-slate-700 outline-none dark:text-slate-200"
          @change="onFilterChange"
        >
          <option value="desc">Mới nhất</option>
          <option value="asc">Cũ nhất</option>
        </select>
      </label>
    </div>

    <div v-if="loading" class="space-y-4 px-6 py-6">
      <div v-for="index in 4" :key="index" class="h-28 animate-pulse rounded-2xl bg-slate-100 dark:bg-slate-800" />
    </div>

    <div v-else-if="!profiles.length" class="px-6 py-16 text-center">
      <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-slate-100 dark:bg-slate-800">
        <span class="material-symbols-outlined text-3xl text-slate-500">folder_off</span>
      </div>
      <h2 class="mt-5 text-xl font-bold text-slate-900 dark:text-white">Không có hồ sơ phù hợp</h2>
      <p class="mx-auto mt-3 max-w-xl text-sm leading-7 text-slate-500 dark:text-slate-400">
        Hãy thay đổi bộ lọc hoặc thử từ khóa khác để tìm hồ sơ bạn cần quản lý.
      </p>
    </div>

    <div v-else class="divide-y divide-slate-100 dark:divide-slate-800">
      <div
        v-for="profile in profiles"
        :key="profile.id"
        class="grid grid-cols-1 gap-4 px-6 py-5 xl:grid-cols-[minmax(0,1.6fr)_220px_200px_auto]"
      >
        <div class="min-w-0">
          <div class="flex flex-wrap items-center gap-3">
            <h3 class="text-lg font-bold text-slate-900 dark:text-white">{{ profile.tieu_de_ho_so || `Hồ sơ #${profile.id}` }}</h3>
            <span
              v-if="!isArchivedTab"
              class="inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-bold"
              :class="statusMeta(profile.trang_thai).classes"
            >
              <span class="size-1.5 rounded-full" :class="statusMeta(profile.trang_thai).dot"></span>
              {{ statusMeta(profile.trang_thai).label }}
            </span>
            <span
              v-else
              class="inline-flex items-center gap-1 rounded-full bg-rose-100 px-2.5 py-1 text-xs font-bold text-rose-700 dark:bg-rose-900/30 dark:text-rose-400"
            >
              <span class="size-1.5 rounded-full bg-rose-500"></span>
              Đang lưu trữ
            </span>
          </div>
          <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">
            {{ profile.nguoi_dung?.ho_ten || 'Ứng viên đang cập nhật' }}
            <span v-if="profile.nguoi_dung?.email">• {{ profile.nguoi_dung.email }}</span>
          </p>
          <p class="mt-3 line-clamp-2 text-sm leading-7 text-slate-600 dark:text-slate-300">
            {{ profile.muc_tieu_nghe_nghiep || profile.mo_ta_ban_than || 'Chưa có mô tả hồ sơ.' }}
          </p>
        </div>

        <div class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 dark:border-slate-700 dark:bg-slate-800">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Thông tin chính</p>
          <div class="mt-3 space-y-2 text-sm text-slate-600 dark:text-slate-300">
            <p>Trình độ: <strong class="text-slate-900 dark:text-white">{{ formatEducation(profile.trinh_do) }}</strong></p>
            <p>Kinh nghiệm: <strong class="text-slate-900 dark:text-white">{{ profile.kinh_nghiem_nam || 0 }} năm</strong></p>
          </div>
        </div>

        <div class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 dark:border-slate-700 dark:bg-slate-800">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">{{ isArchivedTab ? 'Lưu trữ lúc' : 'Ngày tạo' }}</p>
          <p class="mt-3 text-sm font-semibold text-slate-900 dark:text-white">
            {{ formatDateTime(isArchivedTab ? profile.deleted_at : profile.created_at) }}
          </p>
        </div>

        <div class="flex flex-wrap items-center justify-start gap-2 xl:justify-end">
          <button
            class="inline-flex items-center gap-2 rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
            type="button"
            @click="openDetailModal(profile.id)"
          >
            <span class="material-symbols-outlined text-[18px]">visibility</span>
            Chi tiết
          </button>

          <button
            v-if="!isArchivedTab"
            class="inline-flex items-center gap-2 rounded-xl border border-blue-200 px-4 py-2 text-sm font-semibold text-blue-700 transition hover:bg-blue-50 dark:border-blue-900 dark:text-blue-400 dark:hover:bg-blue-950/30"
            type="button"
            @click="toggleStatus(profile)"
          >
            <span class="material-symbols-outlined text-[18px]">{{ Number(profile.trang_thai) === 1 ? 'visibility_off' : 'visibility' }}</span>
            {{ Number(profile.trang_thai) === 1 ? 'Ẩn hồ sơ' : 'Công khai' }}
          </button>

          <button
            v-if="!isArchivedTab"
            class="inline-flex items-center gap-2 rounded-xl border border-rose-200 px-4 py-2 text-sm font-semibold text-rose-700 transition hover:bg-rose-50 dark:border-rose-900 dark:text-rose-400 dark:hover:bg-rose-950/30"
            type="button"
            @click="confirmDelete(profile)"
          >
            <span class="material-symbols-outlined text-[18px]">inventory_2</span>
            Lưu trữ
          </button>

          <button
            v-else
            class="inline-flex items-center gap-2 rounded-xl border border-emerald-200 px-4 py-2 text-sm font-semibold text-emerald-700 transition hover:bg-emerald-50 dark:border-emerald-900 dark:text-emerald-400 dark:hover:bg-emerald-950/30"
            type="button"
            @click="restoreProfile(profile)"
          >
            <span class="material-symbols-outlined text-[18px]">restore_from_trash</span>
            Khôi phục
          </button>

          <button
            v-if="isArchivedTab"
            class="inline-flex items-center gap-2 rounded-xl border border-rose-200 px-4 py-2 text-sm font-semibold text-rose-700 transition hover:bg-rose-50 dark:border-rose-900 dark:text-rose-400 dark:hover:bg-rose-950/30"
            type="button"
            @click="confirmForceDelete(profile)"
          >
            <span class="material-symbols-outlined text-[18px]">delete_forever</span>
            Xóa vĩnh viễn
          </button>
        </div>
      </div>
    </div>

    <div
      v-if="!loading && profiles.length && totalPages > 1"
      class="flex flex-wrap items-center justify-between gap-3 border-t border-slate-200 px-6 py-4 text-sm dark:border-slate-800"
    >
      <p class="text-slate-500">Trang {{ currentPage }} / {{ totalPages }}</p>
      <div class="flex items-center gap-2">
        <button
          class="rounded-lg border border-slate-200 px-3 py-2 font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
          :disabled="currentPage === 1"
          type="button"
          @click="changePage(currentPage - 1)"
        >
          Trước
        </button>
        <button
          class="rounded-lg border border-slate-200 px-3 py-2 font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
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
    v-if="showDetailModal"
    class="fixed inset-0 z-50 overflow-y-auto bg-slate-950/55 backdrop-blur-sm"
    @click.self="showDetailModal = false"
  >
    <div class="flex min-h-full items-center justify-center px-4 py-6">
      <div class="flex max-h-[calc(100vh-3rem)] w-full max-w-3xl flex-col overflow-hidden rounded-[28px] border border-slate-200 bg-white shadow-2xl dark:border-slate-700 dark:bg-slate-900">
      <div class="flex items-start justify-between border-b border-slate-100 px-6 py-5 dark:border-slate-800">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.28em] text-blue-500">Chi tiết hồ sơ</p>
          <h3 class="mt-2 text-2xl font-bold text-slate-900 dark:text-white">{{ selectedProfile?.tieu_de_ho_so || 'Đang tải...' }}</h3>
          <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">
            {{ selectedProfile?.nguoi_dung?.ho_ten || 'Ứng viên đang cập nhật' }}
            <span v-if="selectedProfile?.nguoi_dung?.email">• {{ selectedProfile.nguoi_dung.email }}</span>
          </p>
        </div>
        <button
          class="rounded-full p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-800"
          type="button"
          @click="showDetailModal = false"
        >
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>

      <div v-if="detailLoading" class="flex-1 space-y-4 overflow-y-auto px-6 py-6">
        <div class="h-20 animate-pulse rounded-2xl bg-slate-100 dark:bg-slate-800"></div>
        <div class="h-32 animate-pulse rounded-2xl bg-slate-100 dark:bg-slate-800"></div>
      </div>

      <div v-else-if="selectedProfile" class="flex-1 space-y-5 overflow-y-auto px-6 py-6">
        <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div class="rounded-2xl bg-slate-50 px-4 py-4 dark:bg-slate-800">
            <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Trình độ</p>
            <p class="mt-2 text-sm font-semibold text-slate-900 dark:text-white">{{ formatEducation(selectedProfile.trinh_do) }}</p>
          </div>
          <div class="rounded-2xl bg-slate-50 px-4 py-4 dark:bg-slate-800">
            <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Kinh nghiệm</p>
            <p class="mt-2 text-sm font-semibold text-slate-900 dark:text-white">{{ selectedProfile.kinh_nghiem_nam || 0 }} năm</p>
          </div>
          <div class="rounded-2xl bg-slate-50 px-4 py-4 dark:bg-slate-800">
            <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Trạng thái</p>
            <span
              class="mt-2 inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-bold"
              :class="statusMeta(selectedProfile.trang_thai).classes"
            >
              <span class="size-1.5 rounded-full" :class="statusMeta(selectedProfile.trang_thai).dot"></span>
              {{ statusMeta(selectedProfile.trang_thai).label }}
            </span>
          </div>
        </div>

        <div class="rounded-2xl border border-slate-200 px-5 py-4 dark:border-slate-700">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Mục tiêu nghề nghiệp</p>
          <p class="mt-3 whitespace-pre-line text-sm leading-7 text-slate-600 dark:text-slate-300">
            {{ selectedProfile.muc_tieu_nghe_nghiep || 'Chưa cập nhật mục tiêu nghề nghiệp.' }}
          </p>
        </div>

        <div class="rounded-2xl border border-slate-200 px-5 py-4 dark:border-slate-700">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Mô tả bản thân</p>
          <p class="mt-3 whitespace-pre-line text-sm leading-7 text-slate-600 dark:text-slate-300">
            {{ selectedProfile.mo_ta_ban_than || 'Chưa cập nhật mô tả bản thân.' }}
          </p>
        </div>

        <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div class="rounded-2xl bg-slate-50 px-4 py-4 dark:bg-slate-800">
            <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Ngày tạo</p>
            <p class="mt-2 text-sm font-semibold text-slate-900 dark:text-white">{{ formatDateTime(selectedProfile.created_at) }}</p>
          </div>
          <div class="rounded-2xl bg-slate-50 px-4 py-4 dark:bg-slate-800">
            <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">CV đính kèm</p>
            <p class="mt-2 text-sm font-semibold text-slate-900 dark:text-white">
              {{ selectedProfile.file_cv ? 'Đã tải lên' : 'Chưa có file CV' }}
            </p>
          </div>
        </div>
      </div>
    </div>
    </div>
  </div>

  <div
    v-if="showArchiveModal"
    class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/55 px-4 py-6 backdrop-blur-sm"
    @click.self="showArchiveModal = false"
  >
    <div class="w-full max-w-lg rounded-[28px] border border-slate-200 bg-white p-6 shadow-2xl dark:border-slate-700 dark:bg-slate-900">
      <div class="flex items-start gap-4">
        <div class="rounded-2xl bg-rose-100 p-3 text-rose-600 dark:bg-rose-900/30 dark:text-rose-400">
          <span class="material-symbols-outlined">inventory_2</span>
        </div>
        <div>
          <h3 class="text-xl font-bold text-slate-900 dark:text-white">Lưu trữ hồ sơ</h3>
          <p class="mt-2 text-sm leading-7 text-slate-500 dark:text-slate-400">
            Hồ sơ <strong>{{ deletingProfile?.tieu_de_ho_so }}</strong> sẽ được chuyển vào lưu trữ và có thể khôi phục sau.
          </p>
        </div>
      </div>
      <div class="mt-6 flex justify-end gap-3">
        <button
          class="rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
          type="button"
          @click="showArchiveModal = false"
        >
          Hủy
        </button>
        <button
          class="rounded-xl bg-rose-600 px-4 py-2.5 text-sm font-bold text-white transition hover:bg-rose-700"
          type="button"
          @click="deleteProfile"
        >
          Lưu trữ
        </button>
      </div>
    </div>
  </div>

  <div
    v-if="showForceDeleteModal"
    class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/55 px-4 py-6 backdrop-blur-sm"
    @click.self="showForceDeleteModal = false"
  >
    <div class="w-full max-w-lg rounded-[28px] border border-slate-200 bg-white p-6 shadow-2xl dark:border-slate-700 dark:bg-slate-900">
      <div class="flex items-start gap-4">
        <div class="rounded-2xl bg-rose-100 p-3 text-rose-600 dark:bg-rose-900/30 dark:text-rose-400">
          <span class="material-symbols-outlined">delete_forever</span>
        </div>
        <div>
          <h3 class="text-xl font-bold text-slate-900 dark:text-white">Xóa vĩnh viễn hồ sơ</h3>
          <p class="mt-2 text-sm leading-7 text-slate-500 dark:text-slate-400">
            Hồ sơ <strong>{{ forceDeletingProfile?.tieu_de_ho_so }}</strong> sẽ bị xóa hẳn khỏi hệ thống và không thể khôi phục.
          </p>
        </div>
      </div>
      <div class="mt-6 flex justify-end gap-3">
        <button
          class="rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
          type="button"
          @click="showForceDeleteModal = false"
        >
          Hủy
        </button>
        <button
          class="rounded-xl bg-rose-600 px-4 py-2.5 text-sm font-bold text-white transition hover:bg-rose-700"
          type="button"
          @click="forceDeleteProfile"
        >
          Xóa vĩnh viễn
        </button>
      </div>
    </div>
  </div>
</template>
