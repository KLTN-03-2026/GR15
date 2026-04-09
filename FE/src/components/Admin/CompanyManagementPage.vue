<template>
  <AlertMessage :message="toast.message" :type="toast.type" @close="clearToast" />

  <!-- Error Alert -->
  <div v-if="error"
    class="mb-6 flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-4 dark:border-red-900 dark:bg-red-900/20">
    <span class="material-symbols-outlined mt-1 flex-shrink-0 text-red-600">error</span>
    <div class="flex-1 break-words whitespace-pre-wrap text-sm text-red-700 dark:text-red-400">{{ error }}</div>
    <button @click="error = null" class="mt-1 flex-shrink-0 text-red-600 hover:text-red-700">
      <span class="material-symbols-outlined">close</span>
    </button>
  </div>

  <!-- Page Header -->
  <div class="mb-8 flex flex-wrap items-center justify-between gap-4">
    <div class="flex flex-col gap-1">
      <h1 class="text-3xl font-black leading-tight tracking-tight">Quản Lý Công Ty</h1>
      <p class="text-base text-slate-500 dark:text-slate-400">Quản lý danh sách công ty và tình trạng xác minh.</p>
    </div>
  </div>

  <!-- Stats Grid -->
  <div class="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="mb-2 flex items-center justify-between">
        <span class="text-sm font-medium text-slate-500">Tổng công ty</span>
        <span class="material-symbols-outlined text-[#2463eb]/40">business</span>
      </div>
      <div class="text-2xl font-bold">{{ stats.total }}</div>
      <div class="mt-2 flex items-center text-xs font-medium text-[#2463eb]">
        <span class="material-symbols-outlined mr-1 text-xs">check_circle</span> Tất cả chủ động quản lý
      </div>
    </div>
    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="mb-2 flex items-center justify-between">
        <span class="text-sm font-medium text-slate-500">Hoạt động</span>
        <span class="material-symbols-outlined text-emerald-500/40">verified</span>
      </div>
      <div class="text-2xl font-bold">{{ stats.active }}</div>
      <div class="mt-2 flex items-center text-xs font-medium text-emerald-600">
        <span class="material-symbols-outlined mr-1 text-xs">trending_up</span> Hoạt động
      </div>
    </div>
    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="mb-2 flex items-center justify-between">
        <span class="text-sm font-medium text-slate-500">Tạm ngưng</span>
        <span class="material-symbols-outlined text-amber-500/40">pause_circle</span>
      </div>
      <div class="text-2xl font-bold">{{ stats.inactive }}</div>
      <div class="mt-2 flex items-center text-xs font-medium text-amber-600">
        <span class="material-symbols-outlined mr-1 text-xs">pause</span> Đang tạm ngưng
      </div>
    </div>
  </div>

  <!-- Filters -->
  <div
    class="mb-6 flex flex-wrap items-center gap-4 rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
    <div class="relative min-w-[300px] flex-1">
      <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">search</span>
      <input v-model="searchQuery" @input="onSearch"
        class="w-full rounded-lg border-none bg-slate-50 py-2 pl-10 pr-4 text-sm focus:ring-2 focus:ring-[#2463eb] dark:bg-slate-800"
        placeholder="Tìm theo tên công ty hoặc địa chỉ..." type="text" />
    </div>
    <div class="flex items-center gap-3">
      <select v-model="selectedStatus" @change="onFilterChange"
        class="rounded-lg border-none bg-slate-50 px-4 py-2 text-sm focus:ring-2 focus:ring-[#2463eb] dark:bg-slate-800">
        <option value="">Tất cả trạng thái</option>
        <option value="1">Hoạt động</option>
        <option value="0">Tạm ngưng</option>
      </select>
    </div>
    <button @click="openNewCompanyModal"
      class="flex h-11 items-center gap-2 rounded-xl bg-[#2463eb] px-5 text-sm font-bold text-white shadow-md shadow-[#2463eb]/20 transition-all hover:bg-[#2463eb]/90">
      <span class="material-symbols-outlined text-lg">add</span> Thêm Công Ty
    </button>
  </div>

  <!-- Company Table -->
  <div
    class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
    <div class="overflow-x-auto">
      <table class="w-full border-collapse text-left">
        <thead>
          <tr class="border-b border-slate-200 bg-slate-50/50 dark:border-slate-800 dark:bg-slate-800/50">
            <th class="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">Tên công ty</th>
            <th class="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">Quy mô</th>
            <th class="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">Địa chỉ</th>
            <th class="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">Trạng thái</th>
            <th class="px-6 py-4 text-center text-xs font-semibold uppercase tracking-wider text-slate-500">Hành động
            </th>
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
          <template v-else-if="companies.length === 0">
            <tr>
              <td colspan="5" class="px-6 py-8 text-center text-slate-500">
                <span class="material-symbols-outlined mb-2 text-3xl">inbox</span>
                <div>Không tìm thấy công ty</div>
              </td>
            </tr>
          </template>
          <template v-else>
            <tr v-for="company in companies" :key="company.id"
              class="transition-colors hover:bg-slate-50/50 dark:hover:bg-slate-800/50">
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                  <div
                    class="flex h-10 w-10 items-center justify-center rounded-full bg-[#2463eb]/10 font-bold text-[#2463eb]">
                    {{ company.ten_cong_ty?.charAt(0).toUpperCase() || 'C' }}
                  </div>
                  <div>
                    <div class="text-sm font-semibold">{{ company.ten_cong_ty }}</div>
                    <div class="text-xs text-slate-500">{{ company.website || 'N/A' }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 text-sm">{{ company.quy_mo }}</td>
              <td class="px-6 py-4 text-sm text-slate-600 dark:text-slate-400">{{ company.dia_chi }}</td>
              <td class="px-6 py-4">
                <div class="flex items-center gap-2">
                  <div :class="['h-2 w-2 rounded-full', company.trang_thai === 1 ? 'bg-emerald-500' : 'bg-amber-500']">
                  </div>
                  <span
                    :class="['text-sm font-medium', company.trang_thai === 1 ? 'text-emerald-600' : 'text-amber-600']">
                    {{ company.trang_thai === 1 ? 'Hoạt động' : 'Tạm ngưng' }}
                  </span>
                </div>
              </td>
              <td class="px-6 py-4 text-right">
                <div class="flex items-center justify-end gap-2">
                  <button @click="openEditCompanyModal(company)" :disabled="actionLoadingId === company.id"
                    class="rounded-lg p-2 text-slate-400 transition-colors hover:text-[#2463eb] disabled:cursor-not-allowed disabled:opacity-50"
                    title="Chỉnh sửa">
                    <span class="material-symbols-outlined text-xl">edit</span>
                  </button>
                  <button @click="toggleStatus(company.id)" :disabled="actionLoadingId === company.id"
                    class="rounded-lg p-2 text-slate-400 transition-colors hover:text-amber-600 disabled:cursor-not-allowed disabled:opacity-50"
                    title="Đổi trạng thái">
                    <span class="material-symbols-outlined text-xl">{{ actionLoadingId === company.id ?
                      'progress_activity' : 'toggle_on' }}</span>
                  </button>
                  <button @click="confirmDelete(company)" :disabled="actionLoadingId === company.id"
                    class="rounded-lg p-2 text-slate-400 transition-colors hover:text-red-600 disabled:cursor-not-allowed disabled:opacity-50"
                    title="Xóa">
                    <span class="material-symbols-outlined text-xl">delete</span>
                  </button>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <div v-if="!loading && companies.length > 0"
      class="flex items-center justify-between border-t border-slate-200 bg-slate-50/50 px-6 py-4 dark:border-slate-800 dark:bg-slate-800/50">
      <div class="text-sm text-slate-500">
        Hiển thị <span class="font-medium text-slate-900 dark:text-slate-100">{{ (currentPage - 1) * perPage + 1
          }}</span>
        đến <span class="font-medium text-slate-900 dark:text-slate-100">{{ Math.min(currentPage * perPage,
          totalCompanies)
          }}</span>
        trên <span class="font-medium text-slate-900 dark:text-slate-100">{{ totalCompanies }}</span> công ty
      </div>
      <div class="flex items-center gap-2">
        <button @click="goToPreviousPage" :disabled="currentPage === 1"
          class="rounded-lg border border-slate-200 p-2 transition-colors hover:bg-slate-100 disabled:opacity-50 dark:border-slate-700 dark:hover:bg-slate-700">
          <span class="material-symbols-outlined">chevron_left</span>
        </button>
        <button v-for="page in totalPages" :key="page" @click="goToPage(page)"
          :class="['h-8 w-8 rounded-lg text-sm font-medium transition-colors', currentPage === page ? 'bg-[#2463eb] text-white' : 'hover:bg-slate-200 dark:hover:bg-slate-700']">
          {{ page }}
        </button>
        <button @click="goToNextPage" :disabled="currentPage === totalPages || totalPages === 0"
          class="rounded-lg border border-slate-200 p-2 transition-colors hover:bg-slate-100 disabled:opacity-50 dark:border-slate-700 dark:hover:bg-slate-700">
          <span class="material-symbols-outlined">chevron_right</span>
        </button>
      </div>
    </div>
  </div>

  <!-- Modal: Tạo/Sửa công ty -->
  <div v-if="showModal"
    class="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-black/50 p-4 dark:bg-black/70">
    <div
      class="my-auto flex max-h-[calc(100vh-2rem)] w-full max-w-md flex-col overflow-hidden rounded-xl bg-white shadow-xl dark:bg-slate-900">
      <div class="flex items-center justify-between border-b border-slate-200 px-6 py-4 dark:border-slate-800">
        <h3 class="text-lg font-semibold">{{ editingCompany ? 'Chỉnh sửa công ty' : 'Tạo công ty mới' }}</h3>
        <button @click="closeModal" :disabled="submitting"
          class="text-slate-400 hover:text-slate-600 disabled:opacity-60">
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>
      <form @submit.prevent="submitForm" class="flex min-h-0 flex-1 flex-col">
        <div class="min-h-0 flex-1 space-y-4 overflow-y-auto p-6">
          <div v-if="modalError"
            class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700 dark:border-red-900 dark:bg-red-900/20 dark:text-red-400">
            {{ modalError }}
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Tên công ty</label>
            <input v-model="formData.ten_cong_ty" type="text" required
              class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800" />
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">ID nhà tuyển dụng sở
              hữu</label>
            <select v-model.number="formData.nguoi_dung_id" required
              class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800">
              <option :value="null">-- Chọn nhà tuyển dụng --</option>
              <option v-for="employer in employers" :key="employer.id" :value="employer.id">
                {{ employer.ho_ten }} - {{ employer.email }}
              </option>
            </select>
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Email công ty</label>
            <input v-model="formData.email" type="email"
              class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800" />
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Mã số thuế</label>
            <input v-model="formData.ma_so_thue" type="text" required maxlength="20"
              class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800" />
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Điện thoại</label>
            <input v-model="formData.dien_thoai" type="text" maxlength="20"
              class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800" />
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Địa chỉ</label>
            <input v-model="formData.dia_chi" type="text"
              class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800" />
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Ngành nghề chính</label>
            <select v-model.number="formData.nganh_nghe_id"
              class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800">
              <option :value="null">-- Chọn ngành nghề --</option>
              <option v-for="industry in industries" :key="industry.id" :value="industry.id">
                {{ industry.ten_nganh }}
              </option>
            </select>
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Quy mô</label>
            <select v-model="formData.quy_mo"
              class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800">
              <option value="">-- Chọn quy mô --</option>
              <option v-for="option in scaleOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Website</label>
            <input v-model="formData.website" type="text" placeholder="https://..."
              class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800" />
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Logo URL</label>
            <input v-model="formData.logo" type="text" placeholder="https://.../logo.png"
              class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800" />
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Mô tả</label>
            <textarea v-model="formData.mo_ta" rows="3"
              class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800"></textarea>
          </div>
        </div>
        <div class="flex gap-3 border-t border-slate-200 px-6 py-4 dark:border-slate-800">
          <button type="button" @click="closeModal" :disabled="submitting"
            class="flex-1 rounded-lg border border-slate-300 px-4 py-2 transition-colors hover:bg-slate-50 disabled:opacity-60 dark:border-slate-700 dark:hover:bg-slate-800">
            Hủy
          </button>
          <button type="submit" :disabled="submitting"
            class="flex-1 rounded-lg bg-[#2463eb] px-4 py-2 font-medium text-white transition-colors hover:bg-[#2463eb]/90 disabled:opacity-60">
            {{ submitting ? 'Đang xử lý...' : editingCompany ? 'Cập nhật' : 'Tạo' }}
          </button>
        </div>
      </form>
    </div>
  </div>

  <!-- Modal: Xác nhận xóa -->
  <div v-if="showDeleteModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 dark:bg-black/70">
    <div class="mx-4 w-full max-w-sm rounded-xl bg-white shadow-xl dark:bg-slate-900">
      <div class="p-6">
        <div class="mb-4 flex items-center gap-3">
          <span class="material-symbols-outlined text-2xl text-red-600">warning</span>
          <h3 class="text-lg font-semibold">Xóa công ty</h3>
        </div>
        <p class="mb-6 text-slate-600 dark:text-slate-400">
          Bạn có chắc muốn xóa <strong>{{ deletingCompany?.ten_cong_ty }}</strong>? Hành động này không thể hoàn tác.
        </p>
        <div class="flex gap-3">
          <button @click="closeDeleteModal" :disabled="actionLoadingId === deletingCompany?.id"
            class="flex-1 rounded-lg border border-slate-300 px-4 py-2 transition-colors hover:bg-slate-50 disabled:opacity-60 dark:border-slate-700 dark:hover:bg-slate-800">
            Hủy
          </button>
          <button @click="deleteCompany" :disabled="actionLoadingId === deletingCompany?.id"
            class="flex-1 rounded-lg bg-red-600 px-4 py-2 font-medium text-white transition-colors hover:bg-red-700 disabled:opacity-60">
            {{ actionLoadingId === deletingCompany?.id ? 'Đang xóa...' : 'Xóa' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import AlertMessage from '@/components/AlertMessage.vue'
import { companyService, industryService, userService } from '@/services/api'

const companies = ref([])
const employers = ref([])
const industries = ref([])
const loading = ref(false)
const error = ref(null)
const currentPage = ref(1)
const totalCompanies = ref(0)
const perPage = ref(5)

const searchQuery = ref('')
const selectedStatus = ref('')

const stats = reactive({
  total: 0,
  active: 0,
  inactive: 0
})

const showModal = ref(false)
const showDeleteModal = ref(false)
const editingCompany = ref(null)
const deletingCompany = ref(null)
const submitting = ref(false)
const modalError = ref('')
const actionLoadingId = ref(null)
let searchDebounceTimer = null
let toastTimer = null

const toast = reactive({
  message: '',
  type: 'success'
})

const formData = reactive({
  ten_cong_ty: '',
  nguoi_dung_id: null,
  email: '',
  ma_so_thue: '',
  dien_thoai: '',
  dia_chi: '',
  nganh_nghe_id: null,
  quy_mo: '',
  mo_ta: '',
  website: '',
  logo: ''
})

const scaleOptions = [
  { value: '1-10', label: '1-10 nhân viên' },
  { value: '11-50', label: '11-50 nhân viên' },
  { value: '51-200', label: '51-200 nhân viên' },
  { value: '201-500', label: '201-500 nhân viên' },
  { value: '500+', label: 'Trên 500 nhân viên' }
]

const totalPages = computed(() => Math.ceil(totalCompanies.value / perPage.value))

const normalizeSearchText = (value) => {
  return String(value || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .trim()
}

const normalizeCollectionResponse = (response, key = null) => {
  if (Array.isArray(response)) {
    return response
  }

  if (Array.isArray(response?.data)) {
    return response.data
  }

  if (Array.isArray(response?.data?.data)) {
    return response.data.data
  }

  if (key && Array.isArray(response?.[key])) {
    return response[key]
  }

  if (key && Array.isArray(response?.data?.[key])) {
    return response.data[key]
  }

  return []
}

const normalizeCompanyListResponse = (response) => {
  if (Array.isArray(response)) {
    return { items: response, total: response.length }
  }

  if (Array.isArray(response?.data)) {
    return {
      items: response.data,
      total: response.total ?? response.meta?.total ?? response.data.length
    }
  }

  if (Array.isArray(response?.data?.data)) {
    return {
      items: response.data.data,
      total: response.data.meta?.total ?? response.data.total ?? response.total ?? response.data.data.length
    }
  }

  if (Array.isArray(response?.cong_tys)) {
    return {
      items: response.cong_tys,
      total: response.total ?? response.meta?.total ?? response.cong_tys.length
    }
  }

  if (Array.isArray(response?.data?.cong_tys)) {
    return {
      items: response.data.cong_tys,
      total: response.data.total ?? response.data.meta?.total ?? response.data.cong_tys.length
    }
  }

  return { items: [], total: 0 }
}

const normalizeCompanyStatsResponse = (response) => {
  const source = response?.data ?? response ?? {}

  return {
    total: source.total ?? source.tong_cong_ty ?? source.tong ?? 0,
    active: source.active ?? source.hoat_dong ?? source.da_duyet ?? source.approved ?? 0,
    inactive: source.inactive ?? source.tam_ngung ?? 0
  }
}

const calculateStatsFromList = (items) => ({
  total: totalCompanies.value || items.length,
  active: items.filter((company) => Number(company.trang_thai) === 1).length,
  inactive: items.filter((company) => Number(company.trang_thai) !== 1).length
})

const applyStats = (nextStats) => {
  stats.total = nextStats.total
  stats.active = nextStats.active
  stats.inactive = nextStats.inactive
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
  toastTimer = window.setTimeout(() => {
    clearToast()
  }, 3000)
}

const loadCompanies = async () => {
  loading.value = true
  error.value = null

  try {
    const keyword = searchQuery.value.trim()
    const response = await companyService.getCompanies({
      page: currentPage.value,
      per_page: perPage.value,
      search: keyword || undefined,
      trang_thai: selectedStatus.value !== '' ? Number(selectedStatus.value) : undefined
    })

    const { items, total } = normalizeCompanyListResponse(response)
    const normalizedKeyword = normalizeSearchText(keyword)
    const filteredItems = normalizedKeyword
      ? items.filter((company) => normalizeSearchText(company.ten_cong_ty).includes(normalizedKeyword))
      : items

    companies.value = filteredItems
    totalCompanies.value = normalizedKeyword ? filteredItems.length : total

    try {
      const statsResponse = await companyService.getCompanyStats()
      applyStats(normalizeCompanyStatsResponse(statsResponse))
    } catch {
      applyStats(calculateStatsFromList(items))
    }
  } catch (err) {
    error.value = err.message || 'Không thể tải danh sách công ty'
  } finally {
    loading.value = false
  }
}

const loadFormOptions = async () => {
  try {
    const [employersResponse, industriesResponse] = await Promise.all([
      userService.getUsers({ per_page: 100, vai_tro: 1, sort_by: 'created_at', sort_dir: 'desc' }),
      industryService.getIndustries({ per_page: 100, sort_by: 'ten_nganh', sort_dir: 'asc' })
    ])

    employers.value = normalizeCollectionResponse(employersResponse)
    industries.value = normalizeCollectionResponse(industriesResponse)
  } catch (err) {
    error.value = err.message || 'Không thể tải dữ liệu nhà tuyển dụng và ngành nghề'
  }
}

const resetForm = () => {
  formData.ten_cong_ty = ''
  formData.nguoi_dung_id = null
  formData.email = ''
  formData.ma_so_thue = ''
  formData.dien_thoai = ''
  formData.dia_chi = ''
  formData.nganh_nghe_id = null
  formData.quy_mo = ''
  formData.mo_ta = ''
  formData.website = ''
  formData.logo = ''
  modalError.value = ''
}

const closeModal = (force = false) => {
  if (submitting.value && !force) {
    return
  }

  showModal.value = false
  editingCompany.value = null
  modalError.value = ''
}

const closeDeleteModal = (force = false) => {
  if (actionLoadingId.value === deletingCompany.value?.id && !force) {
    return
  }

  showDeleteModal.value = false
  deletingCompany.value = null
}

const openNewCompanyModal = () => {
  editingCompany.value = null
  resetForm()
  showModal.value = true
}

const openEditCompanyModal = async (company) => {
  error.value = null
  modalError.value = ''
  actionLoadingId.value = company.id

  try {
    const response = await companyService.getCompanyById(company.id)
    const detail = response?.data ?? response ?? company

    editingCompany.value = detail.id ?? company.id
    formData.ten_cong_ty = detail.ten_cong_ty ?? company.ten_cong_ty ?? ''
    formData.nguoi_dung_id = Number(detail.nguoi_dung_id ?? detail.nguoi_dung?.id ?? company.nguoi_dung_id ?? 0) || null
    formData.email = detail.email ?? company.email ?? ''
    formData.ma_so_thue = detail.ma_so_thue ?? company.ma_so_thue ?? ''
    formData.dien_thoai = detail.dien_thoai ?? company.dien_thoai ?? ''
    formData.dia_chi = detail.dia_chi ?? company.dia_chi ?? ''
    formData.nganh_nghe_id = Number(detail.nganh_nghe_id ?? detail.nganh_nghe?.id ?? company.nganh_nghe_id ?? 0) || null
    formData.quy_mo = detail.quy_mo ?? company.quy_mo ?? ''
    formData.mo_ta = detail.mo_ta ?? company.mo_ta ?? ''
    formData.website = detail.website ?? company.website ?? ''
    formData.logo = detail.logo ?? company.logo ?? ''
    showModal.value = true
  } catch (err) {
    error.value = err.message || 'Không thể tải chi tiết công ty'
  } finally {
    actionLoadingId.value = null
  }
}

const submitForm = async () => {
  modalError.value = ''
  submitting.value = true

  try {
    const payload = {
      ten_cong_ty: formData.ten_cong_ty,
      nguoi_dung_id: formData.nguoi_dung_id,
      email: formData.email,
      ma_so_thue: formData.ma_so_thue,
      dien_thoai: formData.dien_thoai,
      dia_chi: formData.dia_chi,
      nganh_nghe_id: formData.nganh_nghe_id,
      quy_mo: formData.quy_mo,
      mo_ta: formData.mo_ta,
      website: formData.website,
      logo: formData.logo
    }

    if (editingCompany.value) {
      await companyService.updateCompany(editingCompany.value, payload)
      showToast('Cập nhật công ty thành công.')
    } else {
      await companyService.createCompany(payload)
      showToast('Tạo công ty thành công.')
    }

    closeModal(true)
    await loadCompanies()
  } catch (err) {
    const validationErrors = err?.data?.errors
    modalError.value = validationErrors
      ? Object.values(validationErrors).flat().join('\n')
      : err.message || 'Lỗi lưu công ty'
  } finally {
    submitting.value = false
  }
}

const confirmDelete = (company) => {
  error.value = null
  deletingCompany.value = company
  showDeleteModal.value = true
}

const deleteCompany = async () => {
  if (!deletingCompany.value) {
    return
  }

  try {
    actionLoadingId.value = deletingCompany.value.id
    await companyService.deleteCompany(deletingCompany.value.id)
    showToast('Xóa công ty thành công.')
    closeDeleteModal(true)
    await loadCompanies()
  } catch (err) {
    error.value = err.message || 'Lỗi xóa công ty'
  } finally {
    actionLoadingId.value = null
  }
}

const toggleStatus = async (companyId) => {
  try {
    error.value = null
    actionLoadingId.value = companyId
    const targetCompany = companies.value.find((company) => company.id === companyId)
    const nextStatusLabel = Number(targetCompany?.trang_thai) === 1 ? 'tạm ngưng' : 'hoạt động'
    await companyService.toggleCompanyStatus(companyId)
    showToast(`Đã chuyển trạng thái công ty sang ${nextStatusLabel}.`)
    await loadCompanies()
  } catch (err) {
    error.value = err.message || 'Lỗi cập nhật trạng thái'
  } finally {
    actionLoadingId.value = null
  }
}

const onSearch = () => {
  currentPage.value = 1

  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer)
  }

  searchDebounceTimer = window.setTimeout(() => {
    loadCompanies()
  }, 250)
}

const onFilterChange = () => {
  currentPage.value = 1
  loadCompanies()
}

const goToPage = (page) => {
  currentPage.value = page
  loadCompanies()
}

const goToPreviousPage = () => {
  if (currentPage.value === 1) {
    return
  }

  currentPage.value -= 1
  loadCompanies()
}

const goToNextPage = () => {
  if (currentPage.value >= totalPages.value) {
    return
  }

  currentPage.value += 1
  loadCompanies()
}

onMounted(() => {
  loadFormOptions()
  loadCompanies()
})

onBeforeUnmount(() => {
  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer)
  }

  if (toastTimer) {
    clearTimeout(toastTimer)
  }
})
</script>
