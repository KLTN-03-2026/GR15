<template>
  <AlertMessage :message="toast.message" :type="toast.type" @close="clearToast" />

  <div v-if="error" class="mb-6 flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-4 dark:border-red-900 dark:bg-red-900/20">
    <span class="material-symbols-outlined mt-1 flex-shrink-0 text-red-600">error</span>
    <div class="flex-1 break-words whitespace-pre-wrap text-sm text-red-700 dark:text-red-400">{{ error }}</div>
    <button @click="error = null" class="mt-1 flex-shrink-0 text-red-600 hover:text-red-700">
      <span class="material-symbols-outlined">close</span>
    </button>
  </div>

  <div class="mb-8 flex flex-wrap items-center justify-between gap-4">
    <div>
      <h1 class="text-3xl font-black tracking-tight">Kho kỹ năng</h1>
      <p class="mt-1 text-slate-500">Quản lý danh mục kỹ năng hệ thống dùng cho hồ sơ, matching và báo cáo.</p>
    </div>
    <button
      @click="openNewSkillModal"
      class="flex h-11 items-center gap-2 rounded-xl bg-[#2463eb] px-5 text-sm font-bold text-white shadow-md shadow-[#2463eb]/20 transition-all hover:bg-[#2463eb]/90"
    >
      <span class="material-symbols-outlined text-lg">add</span> Thêm kỹ năng
    </button>
  </div>

  <div class="mb-8 grid grid-cols-1 gap-6 md:grid-cols-3">
    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="mb-2 flex items-center justify-between">
        <span class="text-sm font-medium text-slate-500">Tổng kỹ năng</span>
        <span class="material-symbols-outlined text-[#2463eb]/40">psychology</span>
      </div>
      <div class="text-2xl font-bold">{{ stats.total }}</div>
      <div class="mt-2 text-xs font-medium text-[#2463eb]">Danh mục kỹ năng đang được theo dõi</div>
    </div>
    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="mb-2 flex items-center justify-between">
        <span class="text-sm font-medium text-slate-500">Có mô tả</span>
        <span class="material-symbols-outlined text-emerald-500/40">notes</span>
      </div>
      <div class="text-2xl font-bold">{{ stats.withDescription }}</div>
      <div class="mt-2 text-xs font-medium text-emerald-600">Đã bổ sung ngữ cảnh sử dụng</div>
    </div>
    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="mb-2 flex items-center justify-between">
        <span class="text-sm font-medium text-slate-500">Có icon</span>
        <span class="material-symbols-outlined text-amber-500/40">image</span>
      </div>
      <div class="text-2xl font-bold">{{ stats.withIcon }}</div>
      <div class="mt-2 text-xs font-medium text-amber-600">Đã chuẩn hóa nhận diện hiển thị</div>
    </div>
  </div>

  <div class="mb-6 flex flex-wrap items-center gap-4 rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
    <div class="relative min-w-[300px] flex-1">
      <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">search</span>
      <input
        v-model="searchQuery"
        @input="onSearch"
        class="w-full rounded-lg border-none bg-slate-50 py-2 pl-10 pr-4 text-sm focus:ring-2 focus:ring-[#2463eb] dark:bg-slate-800"
        placeholder="Tìm theo tên kỹ năng hoặc mô tả..."
        type="text"
      />
    </div>
    <select
      v-model="sortOption"
      @change="onFilterChange"
      class="rounded-lg border-none bg-slate-50 px-4 py-2 text-sm focus:ring-2 focus:ring-[#2463eb] dark:bg-slate-800"
    >
      <option value="name_asc">Tên A-Z</option>
      <option value="name_desc">Tên Z-A</option>
      <option value="newest">Mới thêm gần đây</option>
      <option value="oldest">Cũ nhất</option>
    </select>
  </div>

  <div class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
    <div class="overflow-x-auto">
      <table class="w-full border-collapse text-left">
        <thead>
          <tr class="border-b border-slate-200 bg-slate-50/50 dark:border-slate-800 dark:bg-slate-800/50">
            <th class="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">Kỹ năng</th>
            <th class="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">Mô tả</th>
            <th class="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">Icon</th>
            <th class="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">Ngày tạo</th>
            <th class="px-6 py-4 text-center text-xs font-semibold uppercase tracking-wider text-slate-500">Hành động</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100 dark:divide-slate-800">
          <template v-if="loading">
            <tr>
              <td colspan="5" class="px-6 py-8 text-center text-slate-500">
                <span class="material-symbols-outlined animate-spin">hourglass_empty</span>
                <div>Đang tải...</div>
              </td>
            </tr>
          </template>
          <template v-else-if="skills.length === 0">
            <tr>
              <td colspan="5" class="px-6 py-8 text-center text-slate-500">
                <span class="material-symbols-outlined mb-2 text-3xl">inbox</span>
                <div>Không tìm thấy kỹ năng</div>
              </td>
            </tr>
          </template>
          <template v-else>
            <tr v-for="skill in skills" :key="skill.id" class="transition-colors hover:bg-slate-50/50 dark:hover:bg-slate-800/50">
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                  <div class="flex h-10 w-10 items-center justify-center rounded-full bg-[#2463eb]/10 font-bold text-[#2463eb]">
                    {{ buildSkillBadge(skill) }}
                  </div>
                  <div class="text-sm font-semibold">{{ skill.ten_ky_nang }}</div>
                </div>
              </td>
              <td class="max-w-[420px] px-6 py-4 text-sm text-slate-600 dark:text-slate-400">
                <div class="line-clamp-2">{{ skill.mo_ta || 'Chưa có mô tả' }}</div>
              </td>
              <td class="px-6 py-4 text-sm">
                <span v-if="resolveImageUrl(skill.icon)" class="inline-flex h-10 w-10 items-center justify-center rounded-full bg-slate-100 dark:bg-slate-800">
                  <img :src="resolveImageUrl(skill.icon)" :alt="skill.ten_ky_nang" class="h-8 w-8 rounded object-contain" />
                </span>
                <span v-else-if="resolveIconClass(skill.icon)" class="inline-flex h-10 w-10 items-center justify-center rounded-full bg-slate-100 text-base text-slate-600 dark:bg-slate-800 dark:text-slate-300">
                  <i :class="resolveIconClass(skill.icon)"></i>
                </span>
                <span v-else class="text-slate-400">N/A</span>
              </td>
              <td class="px-6 py-4 text-sm text-slate-600 dark:text-slate-400">
                {{ formatDate(skill.created_at) }}
              </td>
              <td class="px-6 py-4 text-right">
                <div class="flex items-center justify-center gap-2">
                  <button
                    @click="openEditSkillModal(skill)"
                    :disabled="actionLoadingId === skill.id"
                    class="rounded-lg p-2 text-slate-400 transition-colors hover:text-[#2463eb] disabled:cursor-not-allowed disabled:opacity-50"
                    title="Chỉnh sửa"
                  >
                    <span class="material-symbols-outlined text-xl">edit</span>
                  </button>
                  <button
                    @click="confirmDelete(skill)"
                    :disabled="actionLoadingId === skill.id"
                    class="rounded-lg p-2 text-slate-400 transition-colors hover:text-red-600 disabled:cursor-not-allowed disabled:opacity-50"
                    title="Xóa"
                  >
                    <span class="material-symbols-outlined text-xl">delete</span>
                  </button>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <div
      v-if="!loading && skills.length > 0"
      class="flex items-center justify-between border-t border-slate-200 bg-slate-50/50 px-6 py-4 dark:border-slate-800 dark:bg-slate-800/50"
    >
      <div class="text-sm text-slate-500">
        Hiển thị <span class="font-medium text-slate-900 dark:text-slate-100">{{ (currentPage - 1) * perPage + 1 }}</span>
        đến <span class="font-medium text-slate-900 dark:text-slate-100">{{ Math.min(currentPage * perPage, totalSkills) }}</span>
        trên <span class="font-medium text-slate-900 dark:text-slate-100">{{ totalSkills }}</span> kỹ năng
      </div>
      <div class="flex items-center gap-2">
        <button
          @click="goToPreviousPage"
          :disabled="currentPage === 1"
          class="rounded-lg border border-slate-200 p-2 transition-colors hover:bg-slate-100 disabled:opacity-50 dark:border-slate-700 dark:hover:bg-slate-700"
        >
          <span class="material-symbols-outlined">chevron_left</span>
        </button>
        <button
          v-for="page in totalPages"
          :key="page"
          @click="goToPage(page)"
          :class="['h-8 w-8 rounded-lg text-sm font-medium transition-colors', currentPage === page ? 'bg-[#2463eb] text-white' : 'hover:bg-slate-200 dark:hover:bg-slate-700']"
        >
          {{ page }}
        </button>
        <button
          @click="goToNextPage"
          :disabled="currentPage === totalPages || totalPages === 0"
          class="rounded-lg border border-slate-200 p-2 transition-colors hover:bg-slate-100 disabled:opacity-50 dark:border-slate-700 dark:hover:bg-slate-700"
        >
          <span class="material-symbols-outlined">chevron_right</span>
        </button>
      </div>
    </div>
  </div>

  <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-black/50 p-4 dark:bg-black/70">
    <div class="my-auto flex max-h-[calc(100vh-2rem)] w-full max-w-md flex-col overflow-hidden rounded-xl bg-white shadow-xl dark:bg-slate-900">
      <div class="flex items-center justify-between border-b border-slate-200 px-6 py-4 dark:border-slate-800">
        <h3 class="text-lg font-semibold">{{ editingSkill ? 'Chỉnh sửa kỹ năng' : 'Tạo kỹ năng mới' }}</h3>
        <button @click="closeModal" :disabled="submitting" class="text-slate-400 hover:text-slate-600 disabled:opacity-60">
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>
      <form @submit.prevent="submitForm" class="flex min-h-0 flex-1 flex-col">
        <div class="min-h-0 flex-1 space-y-4 overflow-y-auto p-6">
          <div v-if="modalError" class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700 dark:border-red-900 dark:bg-red-900/20 dark:text-red-400">
            {{ modalError }}
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Tên kỹ năng</label>
            <input v-model="formData.ten_ky_nang" type="text" required maxlength="150" class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800" />
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Icon</label>
            <input
              ref="iconFileInputRef"
              type="file"
              accept="image/png,image/jpeg,image/jpg,image/webp,image/svg+xml"
              class="hidden"
              @change="handleIconFileChange"
            />
            <div class="relative">
              <input
                v-model="formData.icon"
                type="text"
                maxlength="255"
                placeholder="Ví dụ: fa-brands fa-aws hoặc https://.../aws.png"
                class="w-full rounded-lg border border-slate-300 px-3 py-2 pr-11 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800"
              />
              <button
                type="button"
                @click="triggerIconFilePicker"
                class="absolute right-2 top-1/2 inline-flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-md text-slate-400 transition-colors hover:bg-slate-100 hover:text-[#2463eb] dark:hover:bg-slate-700"
                title="Chọn ảnh từ máy"
              >
                <span class="material-symbols-outlined text-[18px]">folder_open</span>
              </button>
            </div>
            <p class="mt-1 text-xs text-slate-400">Hỗ trợ class icon hoặc link hình ảnh. Ví dụ: `fa-brands fa-aws` hoặc `https://.../aws.png`.</p>
            <div v-if="selectedIconFileName || iconPreviewUrl" class="mt-3 flex items-center justify-between gap-3 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 dark:border-slate-700 dark:bg-slate-800/60">
              <div class="flex min-w-0 items-center gap-3">
                <img v-if="iconPreviewUrl" :src="iconPreviewUrl" alt="Preview icon" class="h-9 w-9 rounded object-contain" />
                <div class="min-w-0">
                  <p class="truncate text-sm font-medium text-slate-700 dark:text-slate-200">
                    {{ selectedIconFileName || 'Ảnh icon hiện tại' }}
                  </p>
                  <p class="text-xs text-slate-400">Ảnh được chọn sẽ ưu tiên hơn giá trị text trong ô Icon.</p>
                </div>
              </div>
              <button
                v-if="selectedIconFile || selectedIconFileName"
                type="button"
                @click="clearSelectedIconFile"
                class="flex-shrink-0 rounded-lg px-2 py-1 text-sm font-medium text-red-600 transition-colors hover:bg-red-50 dark:hover:bg-red-950/30"
              >
                Xóa
              </button>
            </div>
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Mô tả</label>
            <textarea v-model="formData.mo_ta" rows="4" class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800"></textarea>
          </div>
        </div>
        <div class="flex gap-3 border-t border-slate-200 px-6 py-4 dark:border-slate-800">
          <button type="button" @click="closeModal" :disabled="submitting" class="flex-1 rounded-lg border border-slate-300 px-4 py-2 transition-colors hover:bg-slate-50 disabled:opacity-60 dark:border-slate-700 dark:hover:bg-slate-800">
            Hủy
          </button>
          <button type="submit" :disabled="submitting" class="flex-1 rounded-lg bg-[#2463eb] px-4 py-2 font-medium text-white transition-colors hover:bg-[#2463eb]/90 disabled:opacity-60">
            {{ submitting ? 'Đang xử lý...' : editingSkill ? 'Cập nhật' : 'Tạo' }}
          </button>
        </div>
      </form>
    </div>
  </div>

  <div v-if="showDeleteModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 dark:bg-black/70">
    <div class="mx-4 w-full max-w-sm rounded-xl bg-white shadow-xl dark:bg-slate-900">
      <div class="p-6">
        <div class="mb-4 flex items-center gap-3">
          <span class="material-symbols-outlined text-2xl text-red-600">warning</span>
          <h3 class="text-lg font-semibold">Xóa kỹ năng</h3>
        </div>
        <p class="mb-6 text-slate-600 dark:text-slate-400">
          Bạn có chắc muốn xóa <strong>{{ deletingSkill?.ten_ky_nang }}</strong>? Hành động này không thể hoàn tác.
        </p>
        <div class="flex gap-3">
          <button @click="closeDeleteModal" :disabled="actionLoadingId === deletingSkill?.id" class="flex-1 rounded-lg border border-slate-300 px-4 py-2 transition-colors hover:bg-slate-50 disabled:opacity-60 dark:border-slate-700 dark:hover:bg-slate-800">
            Hủy
          </button>
          <button @click="deleteSkill" :disabled="actionLoadingId === deletingSkill?.id" class="flex-1 rounded-lg bg-red-600 px-4 py-2 font-medium text-white transition-colors hover:bg-red-700 disabled:opacity-60">
            {{ actionLoadingId === deletingSkill?.id ? 'Đang xóa...' : 'Xóa' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import AlertMessage from '@/components/AlertMessage.vue'
import { skillService } from '@/services/api'
import { resolvePrimaryStorageAssetUrl } from '@/utils/media'

const skills = ref([])
const loading = ref(false)
const error = ref(null)
const currentPage = ref(1)
const totalSkills = ref(0)
const perPage = ref(5)
const searchQuery = ref('')
const sortOption = ref('name_asc')
const showModal = ref(false)
const showDeleteModal = ref(false)
const editingSkill = ref(null)
const deletingSkill = ref(null)
const submitting = ref(false)
const modalError = ref('')
const actionLoadingId = ref(null)
const iconFileInputRef = ref(null)
const selectedIconFile = ref(null)
const selectedIconFileName = ref('')
const iconPreviewUrl = ref('')
let searchDebounceTimer = null
let toastTimer = null

const toast = reactive({ message: '', type: 'success' })
const stats = reactive({ total: 0, withDescription: 0, withIcon: 0 })
const formData = reactive({ ten_ky_nang: '', mo_ta: '', icon: '' })

const totalPages = computed(() => Math.ceil(totalSkills.value / perPage.value))

const normalizeSearchText = (value) => String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim()

const resolveSortParams = () => {
  switch (sortOption.value) {
    case 'name_desc': return { sort_by: 'ten_ky_nang', sort_dir: 'desc' }
    case 'newest': return { sort_by: 'created_at', sort_dir: 'desc' }
    case 'oldest': return { sort_by: 'created_at', sort_dir: 'asc' }
    default: return { sort_by: 'ten_ky_nang', sort_dir: 'asc' }
  }
}

const formatDate = (value) => {
  if (!value) return 'N/A'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? 'N/A' : date.toLocaleDateString('vi-VN')
}

const buildSkillBadge = (skill) => {
  const parts = String(skill?.ten_ky_nang || '').trim().split(/\s+/).filter(Boolean)
  if (!parts.length) return 'SK'
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase()
  return `${parts[0][0]}${parts[1][0]}`.toUpperCase()
}

const resolveIconClass = (value) => {
  const input = String(value || '').trim()
  if (!input) return ''

  if (resolveImageUrl(input)) {
    return ''
  }

  const classMatch = input.match(/class\s*=\s*["']([^"']+)["']/i)
  if (classMatch?.[1]) {
    return classMatch[1].trim()
  }

  return input.replace(/[<>]/g, '').trim()
}

const resolveImageUrl = (value) => {
  const input = String(value || '').trim()
  if (!input) return ''

  const srcMatch = input.match(/src\s*=\s*["']([^"']+)["']/i)
  const candidate = (srcMatch?.[1] || input).trim()

  if (/^(https?:\/\/|\/|\.\/|\.\.\/)/i.test(candidate)) {
    return candidate
  }

  if (/^(storage\/|public\/storage\/|ky_nangs\/)/i.test(candidate)) {
    return resolvePrimaryStorageAssetUrl(candidate)
  }

  if (/\.(png|jpe?g|gif|webp|svg|ico)$/i.test(candidate)) {
    return `/${candidate.replace(/^\/+/, '')}`
  }

  return ''
}

const normalizeIconValue = (value) => {
  const imageUrl = resolveImageUrl(value)
  if (imageUrl) {
    return imageUrl
  }

  return resolveIconClass(value)
}

const normalizeSkillListResponse = (response) => {
  if (Array.isArray(response)) return { items: response, total: response.length }
  if (Array.isArray(response?.data)) return { items: response.data, total: response.total ?? response.meta?.total ?? response.data.length }
  if (Array.isArray(response?.data?.data)) return { items: response.data.data, total: response.data.meta?.total ?? response.data.total ?? response.total ?? response.data.data.length }
  if (Array.isArray(response?.ky_nangs)) return { items: response.ky_nangs, total: response.total ?? response.meta?.total ?? response.ky_nangs.length }
  if (Array.isArray(response?.data?.ky_nangs)) return { items: response.data.ky_nangs, total: response.data.total ?? response.data.meta?.total ?? response.data.ky_nangs.length }
  return { items: [], total: 0 }
}

const normalizeSkillStatsResponse = (response) => {
  const source = response?.data ?? response ?? {}
  return {
    total: source.total ?? source.tong ?? 0,
    withDescription: source.withDescription ?? source.co_mo_ta ?? 0,
    withIcon: source.withIcon ?? source.co_icon ?? 0
  }
}

const calculateStatsFromList = (items) => ({
  total: totalSkills.value || items.length,
  withDescription: items.filter((skill) => String(skill.mo_ta || '').trim()).length,
  withIcon: items.filter((skill) => String(skill.icon || '').trim()).length
})

const applyStats = (nextStats) => {
  stats.total = nextStats.total
  stats.withDescription = nextStats.withDescription
  stats.withIcon = nextStats.withIcon
}

const clearToast = () => {
  toast.message = ''
  if (toastTimer) {
    clearTimeout(toastTimer)
    toastTimer = null
  }
}

const showToast = (message, type = 'success') => {
  clearToast()
  toast.message = message
  toast.type = type
  toastTimer = window.setTimeout(() => clearToast(), 3000)
}

const loadSkills = async () => {
  loading.value = true
  error.value = null

  try {
    const keyword = searchQuery.value.trim()
    const sortParams = resolveSortParams()
    const response = await skillService.getSkills({
      page: currentPage.value,
      per_page: perPage.value,
      search: keyword || undefined,
      sort_by: sortParams.sort_by,
      sort_dir: sortParams.sort_dir
    })

    const { items, total } = normalizeSkillListResponse(response)
    const normalizedKeyword = normalizeSearchText(keyword)
    const filteredItems = normalizedKeyword
      ? items.filter((skill) => normalizeSearchText(`${skill.ten_ky_nang} ${skill.mo_ta || ''}`).includes(normalizedKeyword))
      : items

    skills.value = filteredItems
    totalSkills.value = normalizedKeyword ? filteredItems.length : total

    try {
      const statsResponse = await skillService.getSkillStats()
      applyStats(normalizeSkillStatsResponse(statsResponse))
    } catch {
      applyStats(calculateStatsFromList(items))
    }
  } catch (err) {
    error.value = err.message || 'Không thể tải danh sách kỹ năng'
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  formData.ten_ky_nang = ''
  formData.mo_ta = ''
  formData.icon = ''
  clearSelectedIconFile()
  modalError.value = ''
}

const closeModal = (force = false) => {
  if (submitting.value && !force) return
  showModal.value = false
  editingSkill.value = null
  modalError.value = ''
}

const closeDeleteModal = (force = false) => {
  if (actionLoadingId.value === deletingSkill.value?.id && !force) return
  showDeleteModal.value = false
  deletingSkill.value = null
}

const openNewSkillModal = () => {
  editingSkill.value = null
  resetForm()
  showModal.value = true
}

const openEditSkillModal = async (skill) => {
  error.value = null
  modalError.value = ''
  actionLoadingId.value = skill.id

  try {
    const response = await skillService.getSkillById(skill.id)
    const detail = response?.data ?? response ?? skill
    editingSkill.value = detail.id ?? skill.id
    formData.ten_ky_nang = detail.ten_ky_nang ?? skill.ten_ky_nang ?? ''
    formData.mo_ta = detail.mo_ta ?? skill.mo_ta ?? ''
    formData.icon = normalizeIconValue(detail.icon ?? skill.icon ?? '')
    clearSelectedIconFile()
    iconPreviewUrl.value = resolveImageUrl(detail.icon ?? skill.icon ?? '')
    showModal.value = true
  } catch (err) {
    error.value = err.message || 'Không thể tải chi tiết kỹ năng'
  } finally {
    actionLoadingId.value = null
  }
}

const submitForm = async () => {
  modalError.value = ''
  submitting.value = true

  try {
    const normalizedIcon = normalizeIconValue(formData.icon)
    const payload = selectedIconFile.value
      ? (() => {
          const formPayload = new FormData()
          formPayload.append('ten_ky_nang', formData.ten_ky_nang)
          formPayload.append('mo_ta', formData.mo_ta || '')
          formPayload.append('icon', normalizedIcon)
          formPayload.append('icon_file', selectedIconFile.value)
          return formPayload
        })()
      : {
          ten_ky_nang: formData.ten_ky_nang,
          mo_ta: formData.mo_ta,
          icon: normalizedIcon
        }
    if (editingSkill.value) {
      await skillService.updateSkill(editingSkill.value, payload)
      showToast('Cập nhật kỹ năng thành công.')
    } else {
      await skillService.createSkill(payload)
      showToast('Tạo kỹ năng thành công.')
    }
    closeModal(true)
    await loadSkills()
  } catch (err) {
    const validationErrors = err?.data?.errors
    modalError.value = validationErrors ? Object.values(validationErrors).flat().join('\n') : err.message || 'Lỗi lưu kỹ năng'
  } finally {
    submitting.value = false
  }
}

const confirmDelete = (skill) => {
  error.value = null
  deletingSkill.value = skill
  showDeleteModal.value = true
}

const deleteSkill = async () => {
  if (!deletingSkill.value) return

  try {
    actionLoadingId.value = deletingSkill.value.id
    await skillService.deleteSkill(deletingSkill.value.id)
    showToast('Xóa kỹ năng thành công.')
    closeDeleteModal(true)
    await loadSkills()
  } catch (err) {
    error.value = err.message || 'Lỗi xóa kỹ năng'
  } finally {
    actionLoadingId.value = null
  }
}

const triggerIconFilePicker = () => {
  iconFileInputRef.value?.click()
}

const clearSelectedIconFile = () => {
  selectedIconFile.value = null
  selectedIconFileName.value = ''

  if (iconPreviewUrl.value?.startsWith('blob:')) {
    URL.revokeObjectURL(iconPreviewUrl.value)
  }

  iconPreviewUrl.value = resolveImageUrl(formData.icon)

  if (iconFileInputRef.value) {
    iconFileInputRef.value.value = ''
  }
}

const handleIconFileChange = (event) => {
  const [file] = event.target.files || []

  if (!file) {
    return
  }

  if (iconPreviewUrl.value?.startsWith('blob:')) {
    URL.revokeObjectURL(iconPreviewUrl.value)
  }

  selectedIconFile.value = file
  selectedIconFileName.value = file.name
  iconPreviewUrl.value = URL.createObjectURL(file)
}

const onSearch = () => {
  currentPage.value = 1
  if (searchDebounceTimer) clearTimeout(searchDebounceTimer)
  searchDebounceTimer = window.setTimeout(() => loadSkills(), 250)
}

const onFilterChange = () => {
  currentPage.value = 1
  loadSkills()
}

const goToPage = (page) => {
  currentPage.value = page
  loadSkills()
}

const goToPreviousPage = () => {
  if (currentPage.value === 1) return
  currentPage.value -= 1
  loadSkills()
}

const goToNextPage = () => {
  if (currentPage.value >= totalPages.value) return
  currentPage.value += 1
  loadSkills()
}

onMounted(() => {
  loadSkills()
})

onBeforeUnmount(() => {
  if (searchDebounceTimer) clearTimeout(searchDebounceTimer)
  if (toastTimer) clearTimeout(toastTimer)
  if (iconPreviewUrl.value?.startsWith('blob:')) URL.revokeObjectURL(iconPreviewUrl.value)
})
</script>
