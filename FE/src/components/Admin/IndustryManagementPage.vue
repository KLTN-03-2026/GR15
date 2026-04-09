<template>
  <AlertMessage :message="toast.message" :type="toast.type" @close="clearToast" />
  
  <!-- Error Alert -->
  <div v-if="error" class="mb-6 flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-4 dark:border-red-900 dark:bg-red-900/20">
    <span class="material-symbols-outlined mt-1 flex-shrink-0 text-red-600">error</span>
    <div class="flex-1 break-words whitespace-pre-wrap text-sm text-red-700 dark:text-red-400">{{ error }}</div>
    <button @click="error = null" class="mt-1 flex-shrink-0 text-red-600 hover:text-red-700"><span class="material-symbols-outlined">close</span></button>
  </div>

  <!-- Page Header -->
  <div class="mb-8 flex flex-wrap items-center justify-between gap-4">
    <div>
      <h1 class="text-3xl font-black tracking-tight">Quản lý ngành nghề</h1>
      <p class="mt-1 text-slate-500">Quản lý cây ngành nghề, trạng thái hiển thị và dữ liệu phân loại dùng trong hệ thống.</p>
    </div>
    <button @click="openNewIndustryModal" class="flex h-11 items-center gap-2 rounded-xl bg-[#2463eb] px-5 text-sm font-bold text-white shadow-md shadow-[#2463eb]/20 transition-all hover:bg-[#2463eb]/90">
      <span class="material-symbols-outlined text-lg">add</span> Thêm ngành nghề
    </button>
  </div>

  <!-- Stats Grid -->
  <div class="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-4">
    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="mb-2 flex items-center justify-between"><span class="text-sm font-medium text-slate-500">Tổng ngành nghề</span><span class="material-symbols-outlined text-[#2463eb]/40">category</span></div>
      <div class="text-2xl font-bold">{{ stats.total }}</div>
      <div class="mt-2 text-xs font-medium text-[#2463eb]">Toàn bộ danh mục hiện có</div>
    </div>
    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="mb-2 flex items-center justify-between"><span class="text-sm font-medium text-slate-500">Ngành gốc</span><span class="material-symbols-outlined text-amber-500/40">account_tree</span></div>
      <div class="text-2xl font-bold">{{ stats.root }}</div>
      <div class="mt-2 text-xs font-medium text-amber-600">Danh mục cấp đầu</div>
    </div>
    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="mb-2 flex items-center justify-between"><span class="text-sm font-medium text-slate-500">Đang hiển thị</span><span class="material-symbols-outlined text-emerald-500/40">check_circle</span></div>
      <div class="text-2xl font-bold">{{ stats.visible }}</div>
      <div class="mt-2 text-xs font-medium text-emerald-600">Đang bật trên hệ thống</div>
    </div>
    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="mb-2 flex items-center justify-between"><span class="text-sm font-medium text-slate-500">Ngành bị ẩn</span><span class="material-symbols-outlined text-slate-500/40">visibility_off</span></div>
      <div class="text-2xl font-bold">{{ stats.hidden }}</div>
      <div class="mt-2 text-xs font-medium text-slate-500">Tạm thời không hiển thị trên hệ thống</div>
    </div>
  </div>

  <div class="mb-6 flex flex-wrap items-center gap-4 rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
    <div class="relative min-w-[300px] flex-1">
      <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">search</span>
      <input v-model="searchQuery" @input="onSearch" class="w-full rounded-lg border-none bg-slate-50 py-2 pl-10 pr-4 text-sm focus:ring-2 focus:ring-[#2463eb] dark:bg-slate-800" placeholder="Tìm theo tên ngành, mô tả hoặc slug..." type="text" />
    </div>
    <select v-model="selectedStatus" @change="onFilterChange" class="rounded-lg border-none bg-slate-50 px-4 py-2 text-sm focus:ring-2 focus:ring-[#2463eb] dark:bg-slate-800">
      <option value="">Tất cả trạng thái</option>
      <option value="1">Đang hiển thị</option>
      <option value="0">Đang ẩn</option>
    </select>
    <select v-model="sortOption" @change="onFilterChange" class="rounded-lg border-none bg-slate-50 px-4 py-2 text-sm focus:ring-2 focus:ring-[#2463eb] dark:bg-slate-800">
      <option value="name_asc">Tên A-Z</option>
      <option value="name_desc">Tên Z-A</option>
      <option value="newest">Mới thêm</option>
      <option value="oldest">Cũ nhất</option>
    </select>
  </div>

  <div class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
    <div class="overflow-x-auto">
      <table class="w-full border-collapse text-left">
        <thead>
          <tr class="border-b border-slate-200 bg-slate-50/50 dark:border-slate-800 dark:bg-slate-800/50">
            <th class="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">Ngành nghề</th>
            <th class="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">Slug</th>
            <th class="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">Danh mục cha</th>
            <th class="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">Trạng thái</th>
            <th class="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">Ngày tạo</th>
            <th class="px-6 py-4 text-center text-xs font-semibold uppercase tracking-wider text-slate-500">Hành động</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100 dark:divide-slate-800">
          <template v-if="loading">
            <tr><td colspan="6" class="px-6 py-8 text-center text-slate-500"><span class="material-symbols-outlined animate-spin">hourglass_empty</span><div>Đang tải...</div></td></tr>
          </template>
          <template v-else-if="industries.length === 0">
            <tr><td colspan="6" class="px-6 py-8 text-center text-slate-500"><span class="material-symbols-outlined mb-2 text-3xl">inbox</span><div>Không tìm thấy ngành nghề</div></td></tr>
          </template>
          <template v-else>
            <tr v-for="industry in industries" :key="industry.id" class="transition-colors hover:bg-slate-50/50 dark:hover:bg-slate-800/50">
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                  <div class="min-w-0">
                    <div class="flex items-center gap-2">
                      <div class="truncate text-sm font-semibold">{{ industry.ten_nganh }}</div>
                      <span v-if="resolveImageUrl(industry.icon)" class="inline-flex h-10 w-10 items-center justify-center rounded-full bg-slate-100 dark:bg-slate-800">
                        <img :src="resolveImageUrl(industry.icon)" :alt="industry.ten_nganh" class="h-8 w-8 rounded object-contain" />
                      </span>
                      <span v-else-if="resolveIconClass(industry.icon)" class="inline-flex h-10 w-10 items-center justify-center rounded-full bg-slate-100 text-base text-slate-600 dark:bg-slate-800 dark:text-slate-300">
                        <i :class="resolveIconClass(industry.icon)"></i>
                      </span>
                      <span v-else-if="industry.icon" class="inline-flex items-center rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-600 dark:bg-slate-800 dark:text-slate-300">{{ industry.icon }}</span>
                    </div>
                    <div class="line-clamp-1 text-xs text-slate-500">{{ industry.mo_ta || 'Chưa có mô tả' }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 text-sm text-slate-600 dark:text-slate-400">{{ industry.slug || 'N/A' }}</td>
              <td class="px-6 py-4 text-sm text-slate-600 dark:text-slate-400">{{ industry.danh_muc_cha?.ten_nganh || 'Ngành gốc' }}</td>
              <td class="px-6 py-4">
                <span :class="industry.trang_thai === 1 ? 'rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-medium text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' : 'rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-300'">{{ industry.trang_thai === 1 ? 'Hiển thị' : 'Đang ẩn' }}</span>
              </td>
              <td class="px-6 py-4 text-sm text-slate-600 dark:text-slate-400">{{ formatDate(industry.created_at) }}</td>
              <td class="px-6 py-4 text-right">
                <div class="flex items-center justify-center gap-2">
                  <button @click="openEditIndustryModal(industry)" :disabled="actionLoadingId === industry.id" class="rounded-lg p-2 text-slate-400 transition-colors hover:text-[#2463eb] disabled:cursor-not-allowed disabled:opacity-50" title="Chỉnh sửa"><span class="material-symbols-outlined text-xl">edit</span></button>
                  <button @click="toggleStatus(industry)" :disabled="actionLoadingId === industry.id" :class="industry.trang_thai === 1 ? 'rounded-lg p-2 text-slate-400 transition-colors hover:text-amber-600 disabled:cursor-not-allowed disabled:opacity-50' : 'rounded-lg p-2 text-slate-400 transition-colors hover:text-emerald-600 disabled:cursor-not-allowed disabled:opacity-50'" :title="industry.trang_thai === 1 ? 'Ẩn ngành nghề' : 'Hiển thị ngành nghề'"><span class="material-symbols-outlined text-xl">{{ actionLoadingId === industry.id ? 'progress_activity' : industry.trang_thai === 1 ? 'visibility_off' : 'visibility' }}</span></button>
                  <button @click="confirmDelete(industry)" :disabled="actionLoadingId === industry.id" class="rounded-lg p-2 text-slate-400 transition-colors hover:text-red-600 disabled:cursor-not-allowed disabled:opacity-50" title="Xóa"><span class="material-symbols-outlined text-xl">delete</span></button>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <div v-if="!loading && industries.length > 0" class="flex items-center justify-between border-t border-slate-200 bg-slate-50/50 px-6 py-4 dark:border-slate-800 dark:bg-slate-800/50">
      <div class="text-sm text-slate-500">
        Hiển thị <span class="font-medium text-slate-900 dark:text-slate-100">{{ (currentPage - 1) * perPage + 1 }}</span>
        đến <span class="font-medium text-slate-900 dark:text-slate-100">{{ Math.min(currentPage * perPage, totalIndustries) }}</span>
        trên <span class="font-medium text-slate-900 dark:text-slate-100">{{ totalIndustries }}</span> ngành nghề
      </div>
      <div class="flex items-center gap-2">
        <button @click="goToPreviousPage" :disabled="currentPage === 1" class="rounded-lg border border-slate-200 p-2 transition-colors hover:bg-slate-100 disabled:opacity-50 dark:border-slate-700 dark:hover:bg-slate-700"><span class="material-symbols-outlined">chevron_left</span></button>
        <button v-for="page in totalPages" :key="page" @click="goToPage(page)" :class="['h-8 w-8 rounded-lg text-sm font-medium transition-colors', currentPage === page ? 'bg-[#2463eb] text-white' : 'hover:bg-slate-200 dark:hover:bg-slate-700']">{{ page }}</button>
        <button @click="goToNextPage" :disabled="currentPage === totalPages || totalPages === 0" class="rounded-lg border border-slate-200 p-2 transition-colors hover:bg-slate-100 disabled:opacity-50 dark:border-slate-700 dark:hover:bg-slate-700"><span class="material-symbols-outlined">chevron_right</span></button>
      </div>
    </div>
  </div>

  <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-black/50 p-4 dark:bg-black/70">
    <div class="my-auto flex max-h-[calc(100vh-2rem)] w-full max-w-md flex-col overflow-hidden rounded-xl bg-white shadow-xl dark:bg-slate-900">
      <div class="flex items-center justify-between border-b border-slate-200 px-6 py-4 dark:border-slate-800">
        <h3 class="text-lg font-semibold">{{ editingIndustry ? 'Chỉnh sửa ngành nghề' : 'Tạo ngành nghề mới' }}</h3>
        <button @click="closeModal" :disabled="submitting" class="text-slate-400 hover:text-slate-600 disabled:opacity-60"><span class="material-symbols-outlined">close</span></button>
      </div>
      <form @submit.prevent="submitForm" class="flex min-h-0 flex-1 flex-col">
        <div class="min-h-0 flex-1 space-y-4 overflow-y-auto p-6">
          <div v-if="modalError" class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700 dark:border-red-900 dark:bg-red-900/20 dark:text-red-400">{{ modalError }}</div>
          <div>
            <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Tên ngành nghề</label>
            <input v-model="formData.ten_nganh" type="text" required maxlength="150" class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800" />
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Danh mục cha</label>
            <select v-model="formData.danh_muc_cha_id" class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800">
              <option value="">Ngành gốc</option>
              <option v-for="option in parentIndustryOptions" :key="option.id" :value="String(option.id)">{{ option.ten_nganh }}</option>
            </select>
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Icon</label>
            <input ref="iconFileInputRef" type="file" accept="image/png,image/jpeg,image/jpg,image/webp,image/svg+xml" class="hidden" @change="handleIconFileChange" />
            <div class="relative">
              <input v-model="formData.icon" type="text" maxlength="255" placeholder="Ví dụ: fa-solid fa-briefcase hoặc https://.../icon.png" class="w-full rounded-lg border border-slate-300 px-3 py-2 pr-11 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800" />
              <button type="button" @click="triggerIconFilePicker" class="absolute right-2 top-1/2 inline-flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-md text-slate-400 transition-colors hover:bg-slate-100 hover:text-[#2463eb] dark:hover:bg-slate-700" title="Chọn ảnh từ máy">
                <span class="material-symbols-outlined text-[18px]">folder_open</span>
              </button>
            </div>
            <p class="mt-1 text-xs text-slate-400">Hỗ trợ class icon hoặc link hình ảnh. Ví dụ: `fa-solid fa-briefcase` hoặc `https://.../icon.png`.</p>
            <div v-if="selectedIconFileName || iconPreviewUrl" class="mt-3 flex items-center justify-between gap-3 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 dark:border-slate-700 dark:bg-slate-800/60">
              <div class="flex min-w-0 items-center gap-3">
                <img v-if="iconPreviewUrl" :src="iconPreviewUrl" alt="Preview icon" class="h-9 w-9 rounded object-contain" />
                <div class="min-w-0">
                  <p class="truncate text-sm font-medium text-slate-700 dark:text-slate-200">{{ selectedIconFileName || 'Ảnh icon hiện tại' }}</p>
                  <p class="text-xs text-slate-400">Ảnh được chọn sẽ ưu tiên hơn giá trị text trong ô Icon.</p>
                </div>
              </div>
              <button v-if="selectedIconFile || selectedIconFileName" type="button" @click="clearSelectedIconFile" class="flex-shrink-0 rounded-lg px-2 py-1 text-sm font-medium text-red-600 transition-colors hover:bg-red-50 dark:hover:bg-red-950/30">Xóa</button>
            </div>
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Trạng thái</label>
            <select v-model="formData.trang_thai" class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800">
              <option value="1">Hiển thị</option>
              <option value="0">Ẩn</option>
            </select>
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Mô tả</label>
            <textarea v-model="formData.mo_ta" rows="4" class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800"></textarea>
          </div>
        </div>
        <div class="flex gap-3 border-t border-slate-200 px-6 py-4 dark:border-slate-800">
          <button type="button" @click="closeModal" :disabled="submitting" class="flex-1 rounded-lg border border-slate-300 px-4 py-2 transition-colors hover:bg-slate-50 disabled:opacity-60 dark:border-slate-700 dark:hover:bg-slate-800">Hủy</button>
          <button type="submit" :disabled="submitting" class="flex-1 rounded-lg bg-[#2463eb] px-4 py-2 font-medium text-white transition-colors hover:bg-[#2463eb]/90 disabled:opacity-60">{{ submitting ? 'Đang xử lý...' : editingIndustry ? 'Cập nhật' : 'Tạo' }}</button>
        </div>
      </form>
    </div>
  </div>

  <div v-if="showDeleteModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 dark:bg-black/70">
    <div class="mx-4 w-full max-w-sm rounded-xl bg-white shadow-xl dark:bg-slate-900">
      <div class="p-6">
        <div class="mb-4 flex items-center gap-3"><span class="material-symbols-outlined text-2xl text-red-600">warning</span><h3 class="text-lg font-semibold">Xóa ngành nghề</h3></div>
        <p class="mb-6 text-slate-600 dark:text-slate-400">Bạn có chắc muốn xóa <strong>{{ deletingIndustry?.ten_nganh }}</strong>? Hành động này không thể hoàn tác.</p>
        <div class="flex gap-3">
          <button @click="closeDeleteModal" :disabled="actionLoadingId === deletingIndustry?.id" class="flex-1 rounded-lg border border-slate-300 px-4 py-2 transition-colors hover:bg-slate-50 disabled:opacity-60 dark:border-slate-700 dark:hover:bg-slate-800">Hủy</button>
          <button @click="deleteIndustry" :disabled="actionLoadingId === deletingIndustry?.id" class="flex-1 rounded-lg bg-red-600 px-4 py-2 font-medium text-white transition-colors hover:bg-red-700 disabled:opacity-60">{{ actionLoadingId === deletingIndustry?.id ? 'Đang xóa...' : 'Xóa' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import AlertMessage from '@/components/AlertMessage.vue'
import { industryService } from '@/services/api'
import { resolvePrimaryStorageAssetUrl } from '@/utils/media'

const industries = ref([])
const parentIndustries = ref([])
const loading = ref(false)
const error = ref(null)
const currentPage = ref(1)
const totalIndustries = ref(0)
const perPage = ref(5)
const searchQuery = ref('')
const selectedStatus = ref('')
const sortOption = ref('name_asc')
const showModal = ref(false)
const showDeleteModal = ref(false)
const editingIndustry = ref(null)
const deletingIndustry = ref(null)
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
const stats = reactive({ total: 0, visible: 0, hidden: 0, root: 0, child: 0 })
const formData = reactive({ ten_nganh: '', mo_ta: '', danh_muc_cha_id: '', icon: '', trang_thai: '1' })

const totalPages = computed(() => Math.ceil(totalIndustries.value / perPage.value))
const parentIndustryOptions = computed(() => parentIndustries.value.filter((item) => item.id !== editingIndustry.value))

const normalizeSearchText = (value) => String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim()
const formatDate = (value) => {
  if (!value) return 'N/A'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? 'N/A' : date.toLocaleDateString('vi-VN')
}
const resolveSortParams = () => {
  switch (sortOption.value) {
    case 'name_desc': return { sort_by: 'ten_nganh', sort_dir: 'desc' }
    case 'newest': return { sort_by: 'created_at', sort_dir: 'desc' }
    case 'oldest': return { sort_by: 'created_at', sort_dir: 'asc' }
    default: return { sort_by: 'ten_nganh', sort_dir: 'asc' }
  }
}
const buildIndustryBadge = (industry) => {
  if (industry?.icon && !resolveImageUrl(industry.icon) && !resolveIconClass(industry.icon)) return String(industry.icon).trim().slice(0, 2)
  const parts = String(industry?.ten_nganh || '').trim().split(/\s+/).filter(Boolean)
  if (!parts.length) return 'NG'
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase()
  return `${parts[0][0]}${parts[1][0]}`.toUpperCase()
}
const resolveImageUrl = (value) => {
  const input = String(value || '').trim()
  if (!input) return ''
  const srcMatch = input.match(/src\s*=\s*["']([^"']+)["']/i)
  const candidate = (srcMatch?.[1] || input).trim()
  if (/^(https?:\/\/|\/|\.\/|\.\.\/)/i.test(candidate)) return candidate
  if (/^(storage\/|public\/storage\/|nganh_nghes\/)/i.test(candidate)) return resolvePrimaryStorageAssetUrl(candidate)
  if (/\.(png|jpe?g|gif|webp|svg|ico)$/i.test(candidate)) return `/${candidate.replace(/^\/+/, '')}`
  return ''
}
const resolveIconClass = (value) => {
  const input = String(value || '').trim()
  if (!input || resolveImageUrl(input)) return ''
  const classMatch = input.match(/class\s*=\s*["']([^"']+)["']/i)
  if (classMatch?.[1]) return classMatch[1].trim()
  return input.replace(/[<>]/g, '').trim()
}
const normalizeIconValue = (value) => {
  const imageUrl = resolveImageUrl(value)
  if (imageUrl) return imageUrl
  return resolveIconClass(value)
}
const normalizeIndustryListResponse = (response) => {
  if (Array.isArray(response)) return { items: response, total: response.length }
  if (Array.isArray(response?.data)) return { items: response.data, total: response.total ?? response.meta?.total ?? response.data.length }
  if (Array.isArray(response?.data?.data)) return { items: response.data.data, total: response.data.meta?.total ?? response.data.total ?? response.total ?? response.data.data.length }
  return { items: [], total: 0 }
}
const normalizeIndustryStatsResponse = (response) => {
  const source = response?.data ?? response ?? {}
  return {
    total: source.total ?? source.tong ?? 0,
    visible: source.visible ?? source.hien_thi ?? 0,
    hidden: source.hidden ?? source.an ?? 0,
    root: source.rootIndustries ?? source.nganh_goc ?? 0,
    child: source.childIndustries ?? source.nganh_con ?? 0
  }
}
const calculateStatsFromList = (items) => ({
  total: totalIndustries.value || items.length,
  visible: items.filter((item) => Number(item.trang_thai) === 1).length,
  hidden: items.filter((item) => Number(item.trang_thai) === 0).length,
  root: items.filter((item) => !item.danh_muc_cha_id).length,
  child: items.filter((item) => Boolean(item.danh_muc_cha_id)).length
})
const applyStats = (nextStats) => {
  stats.total = nextStats.total
  stats.visible = nextStats.visible
  stats.hidden = nextStats.hidden
  stats.root = nextStats.root
  stats.child = nextStats.child
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
const loadParentIndustries = async () => {
  try {
    const response = await industryService.getIndustries({ per_page: 100, sort_by: 'ten_nganh', sort_dir: 'asc' })
    parentIndustries.value = normalizeIndustryListResponse(response).items
  } catch {
    parentIndustries.value = []
  }
}
const loadIndustries = async () => {
  loading.value = true
  error.value = null
  try {
    const keyword = searchQuery.value.trim()
    const sortParams = resolveSortParams()
    const response = await industryService.getIndustries({
      page: currentPage.value,
      per_page: perPage.value,
      search: keyword || undefined,
      trang_thai: selectedStatus.value === '' ? undefined : Number(selectedStatus.value),
      sort_by: sortParams.sort_by,
      sort_dir: sortParams.sort_dir
    })
    const { items, total } = normalizeIndustryListResponse(response)
    const normalizedKeyword = normalizeSearchText(keyword)
    const filteredItems = normalizedKeyword
      ? items.filter((item) => normalizeSearchText(`${item.ten_nganh} ${item.mo_ta || ''} ${item.slug || ''}`).includes(normalizedKeyword))
      : items
    industries.value = filteredItems
    totalIndustries.value = normalizedKeyword ? filteredItems.length : total
    try {
      const statsResponse = await industryService.getIndustryStats()
      applyStats(normalizeIndustryStatsResponse(statsResponse))
    } catch {
      applyStats(calculateStatsFromList(items))
    }
  } catch (err) {
    error.value = err.message || 'Không thể tải danh sách ngành nghề'
  } finally {
    loading.value = false
  }
}
const resetForm = () => {
  formData.ten_nganh = ''
  formData.mo_ta = ''
  formData.danh_muc_cha_id = ''
  formData.icon = ''
  formData.trang_thai = '1'
  clearSelectedIconFile()
  modalError.value = ''
}
const closeModal = (force = false) => {
  if (submitting.value && !force) return
  showModal.value = false
  editingIndustry.value = null
  modalError.value = ''
}
const closeDeleteModal = (force = false) => {
  if (actionLoadingId.value === deletingIndustry.value?.id && !force) return
  showDeleteModal.value = false
  deletingIndustry.value = null
}
const openNewIndustryModal = async () => {
  editingIndustry.value = null
  resetForm()
  await loadParentIndustries()
  showModal.value = true
}
const openEditIndustryModal = async (industry) => {
  modalError.value = ''
  error.value = null
  actionLoadingId.value = industry.id
  try {
    const [detailResponse] = await Promise.all([industryService.getIndustryById(industry.id), loadParentIndustries()])
    const detail = detailResponse?.data ?? detailResponse ?? industry
    editingIndustry.value = detail.id ?? industry.id
    formData.ten_nganh = detail.ten_nganh ?? industry.ten_nganh ?? ''
    formData.mo_ta = detail.mo_ta ?? industry.mo_ta ?? ''
    formData.danh_muc_cha_id = detail.danh_muc_cha_id ? String(detail.danh_muc_cha_id) : ''
    formData.icon = normalizeIconValue(detail.icon ?? industry.icon ?? '')
    clearSelectedIconFile()
    iconPreviewUrl.value = resolveImageUrl(detail.icon ?? industry.icon ?? '')
    formData.trang_thai = String(detail.trang_thai ?? industry.trang_thai ?? 1)
    showModal.value = true
  } catch (err) {
    error.value = err.message || 'Không thể tải chi tiết ngành nghề'
  } finally {
    actionLoadingId.value = null
  }
}
const buildPayload = () => ({
  ten_nganh: formData.ten_nganh,
  mo_ta: formData.mo_ta || null,
  danh_muc_cha_id: formData.danh_muc_cha_id ? Number(formData.danh_muc_cha_id) : null,
  icon: normalizeIconValue(formData.icon) || null,
  trang_thai: Number(formData.trang_thai)
})
const submitForm = async () => {
  modalError.value = ''
  submitting.value = true
  try {
    const payload = selectedIconFile.value
      ? (() => {
          const formPayload = new FormData()
          const basePayload = buildPayload()
          Object.entries(basePayload).forEach(([key, value]) => {
            formPayload.append(key, value ?? '')
          })
          formPayload.append('icon_file', selectedIconFile.value)
          return formPayload
        })()
      : buildPayload()
    if (editingIndustry.value) {
      await industryService.updateIndustry(editingIndustry.value, payload)
      showToast('Cập nhật ngành nghề thành công.')
    } else {
      await industryService.createIndustry(payload)
      showToast('Tạo ngành nghề thành công.')
    }
    closeModal(true)
    await Promise.all([loadIndustries(), loadParentIndustries()])
  } catch (err) {
    const validationErrors = err?.data?.errors
    modalError.value = validationErrors ? Object.values(validationErrors).flat().join('\n') : err.message || 'Lỗi lưu ngành nghề'
  } finally {
    submitting.value = false
  }
}
const confirmDelete = (industry) => {
  error.value = null
  deletingIndustry.value = industry
  showDeleteModal.value = true
}
const deleteIndustry = async () => {
  if (!deletingIndustry.value) return
  try {
    actionLoadingId.value = deletingIndustry.value.id
    await industryService.deleteIndustry(deletingIndustry.value.id)
    showToast('Xóa ngành nghề thành công.')
    closeDeleteModal(true)
    await Promise.all([loadIndustries(), loadParentIndustries()])
  } catch (err) {
    error.value = err.message || 'Lỗi xóa ngành nghề'
  } finally {
    actionLoadingId.value = null
  }
}
const toggleStatus = async (industry) => {
  try {
    error.value = null
    actionLoadingId.value = industry.id
    await industryService.toggleIndustryStatus(industry.id)
    showToast(industry.trang_thai === 1 ? 'Đã ẩn ngành nghề.' : 'Đã hiển thị ngành nghề.')
    await loadIndustries()
  } catch (err) {
    error.value = err.message || 'Lỗi đổi trạng thái ngành nghề'
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
  if (iconPreviewUrl.value?.startsWith('blob:')) URL.revokeObjectURL(iconPreviewUrl.value)
  iconPreviewUrl.value = resolveImageUrl(formData.icon)
  if (iconFileInputRef.value) iconFileInputRef.value.value = ''
}
const handleIconFileChange = (event) => {
  const [file] = event.target.files || []
  if (!file) return
  if (iconPreviewUrl.value?.startsWith('blob:')) URL.revokeObjectURL(iconPreviewUrl.value)
  selectedIconFile.value = file
  selectedIconFileName.value = file.name
  iconPreviewUrl.value = URL.createObjectURL(file)
}
const onSearch = () => {
  currentPage.value = 1
  if (searchDebounceTimer) clearTimeout(searchDebounceTimer)
  searchDebounceTimer = window.setTimeout(() => loadIndustries(), 250)
}
const onFilterChange = () => {
  currentPage.value = 1
  loadIndustries()
}
const goToPage = (page) => {
  currentPage.value = page
  loadIndustries()
}
const goToPreviousPage = () => {
  if (currentPage.value === 1) return
  currentPage.value -= 1
  loadIndustries()
}
const goToNextPage = () => {
  if (currentPage.value >= totalPages.value) return
  currentPage.value += 1
  loadIndustries()
}
onMounted(async () => {
  await Promise.all([loadIndustries(), loadParentIndustries()])
})
onBeforeUnmount(() => {
  if (searchDebounceTimer) clearTimeout(searchDebounceTimer)
  if (toastTimer) clearTimeout(toastTimer)
  if (iconPreviewUrl.value?.startsWith('blob:')) URL.revokeObjectURL(iconPreviewUrl.value)
})
</script>
