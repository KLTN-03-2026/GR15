<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, computed, nextTick } from 'vue'
import { companyService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'
import AdminPaginationBar from '@/components/Admin/AdminPaginationBar.vue'

const notify = useNotify()

// State
const companies = ref([])
const loading = ref(false)
const error = ref(null)
const currentPage = ref(1)
const totalCompanies = ref(0)
const perPage = ref(5)

// Filters
const searchQuery = ref('')
const selectedStatus = ref('')

// Stats
const stats = reactive({
  total: 0,
  active: 0,
  paused: 0,
  scaleSummary: {}
})

// Modals
const showModal = ref(false)
const showDeleteModal = ref(false)
const editingCompany = ref(null)
const deletingCompany = ref(null)
const saving = ref(false)
const listSectionRef = ref(null)
let searchDebounceTimer = null

// Form data
const formData = reactive({
  ten_cong_ty: '',
  ma_so_thue: '',
  dia_chi: '',
  dien_thoai: '',
  email: '',
  quy_mo: '',
  mo_ta: '',
  website: '',
  trang_thai: 1,
})

// Quy mô options
const scaleOptions = [
  { value: '1-10', label: '1-10 nhân viên' },
  { value: '11-50', label: '11-50 nhân viên' },
  { value: '51-200', label: '51-200 nhân viên' },
  { value: '201-500', label: '201-500 nhân viên' },
  { value: '500+', label: 'Trên 500 nhân viên' }
]

const statusMap = {
  1: 'Hoạt động',
  0: 'Tạm ngưng',
}

const statusColors = {
  1: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400',
  0: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'
}

const statusPillColors = {
  1: 'border border-emerald-200 bg-emerald-50 text-emerald-700',
  0: 'border border-amber-200 bg-amber-50 text-amber-700',
}

const scrollToListTop = async () => {
  await nextTick()
  listSectionRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const getScaleValue = (value) => {
  if (!value) return ''

  const matched = scaleOptions.find((option) => option.value === value || option.label === value)
  return matched?.value || value
}

const resetForm = () => {
  formData.ten_cong_ty = ''
  formData.ma_so_thue = ''
  formData.dia_chi = ''
  formData.dien_thoai = ''
  formData.email = ''
  formData.quy_mo = ''
  formData.mo_ta = ''
  formData.website = ''
  formData.trang_thai = 1
}

const closeEditCompanyModal = () => {
  showModal.value = false
  editingCompany.value = null
  resetForm()
}

const loadStats = async () => {
  try {
    const response = await companyService.getCompanyStats()
    const payload = response?.data || {}
    stats.total = payload.tong || 0
    stats.active = payload.hoat_dong || 0
    stats.paused = payload.tam_ngung || 0
    stats.scaleSummary = payload.theo_quy_mo || {}
  } catch (err) {
    console.error('Không thể tải thống kê công ty', err)
  }
}

// Load companies
const loadCompanies = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await companyService.getCompanies({
      page: currentPage.value,
      per_page: perPage.value,
      search: searchQuery.value || undefined,
      trang_thai: selectedStatus.value !== '' ? selectedStatus.value : undefined
    })

    // Xử lý response từ API Laravel
    // Format 1: {data: [...], meta: {...}} hoặc {data: [...], total: 100}
    // Format 2: {success: true, data: {data: [...], meta: {...}}}
    let companies_list = []
    let total = 0

    if (response.data) {
      // Kiểm tra nếu response.data là array (format đơn giản)
      if (Array.isArray(response.data)) {
        companies_list = response.data
        total = response.total || response.data.length
      } 
      // Kiểm tra nếu response.data có property 'data' (paginated format)
      else if (response.data.data && Array.isArray(response.data.data)) {
        companies_list = response.data.data
        total = response.data.meta?.total || response.data.total || 0
      }
      // Kiểm tra nếu response có property 'cong_tys' (custom format)
      else if (response.cong_tys) {
        companies_list = response.cong_tys
        total = response.total || response.cong_tys.length
      }
    }

    companies.value = companies_list
    totalCompanies.value = total
  } catch (err) {
    error.value = err.message || 'Không thể tải danh sách công ty'
  } finally {
    loading.value = false
  }
}

// Open modal for editing company
const openEditCompanyModal = (company) => {
  editingCompany.value = company.id
  formData.ten_cong_ty = company.ten_cong_ty
  formData.ma_so_thue = company.ma_so_thue || ''
  formData.dia_chi = company.dia_chi || ''
  formData.dien_thoai = company.dien_thoai || ''
  formData.email = company.email || ''
  formData.quy_mo = getScaleValue(company.quy_mo)
  formData.mo_ta = company.mo_ta || ''
  formData.website = company.website || ''
  formData.trang_thai = company.trang_thai ?? 1
  showModal.value = true
}

// Submit form
const submitForm = async () => {
  if (!editingCompany.value) return

  saving.value = true
  try {
    await companyService.updateCompany(editingCompany.value, formData)
    closeEditCompanyModal()
    await loadCompanies()
    await loadStats()
    notify.success('Đã cập nhật công ty')
  } catch (err) {
    error.value = err.message || 'Lỗi lưu công ty'
  } finally {
    saving.value = false
  }
}

// Delete confirmation modal
const confirmDelete = (company) => {
  deletingCompany.value = company
  showDeleteModal.value = true
}

// Delete company
const deleteCompany = async () => {
  try {
    await companyService.deleteCompany(deletingCompany.value.id)
    showDeleteModal.value = false
    await loadCompanies()
    await loadStats()
    notify.success('Đã xóa công ty')
  } catch (err) {
    error.value = err.message || 'Lỗi xóa công ty'
  }
}

// Toggle status
const toggleStatus = async (companyId) => {
  try {
    await companyService.toggleCompanyStatus(companyId)
    await loadCompanies()
    await loadStats()
    notify.success('Đã cập nhật trạng thái công ty')
  } catch (err) {
    error.value = err.message || 'Lỗi cập nhật trạng thái'
  }
}

// Computed properties
const totalPages = computed(() => Math.ceil(totalCompanies.value / perPage.value))

// Watchers
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

const resetFilters = () => {
  searchQuery.value = ''
  selectedStatus.value = ''
  perPage.value = 5
  currentPage.value = 1
  loadCompanies()
}

const goToPage = (page) => {
  currentPage.value = page
  loadCompanies()
  scrollToListTop()
}

const goToPreviousPage = () => {
  if (currentPage.value === 1) return
  currentPage.value -= 1
  loadCompanies()
  scrollToListTop()
}

const goToNextPage = () => {
  if (currentPage.value === totalPages.value) return
  currentPage.value += 1
  loadCompanies()
  scrollToListTop()
}

// Lifecycle
onMounted(() => {
  loadCompanies()
  loadStats()
})

onBeforeUnmount(() => {
  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer)
  }
})
</script>

<template>
  <!-- Error Alert -->
  <div v-if="error" class="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-900 rounded-lg flex items-start gap-3">
    <span class="material-symbols-outlined text-red-600 mt-1 flex-shrink-0">error</span>
    <div class="flex-1 text-sm text-red-700 dark:text-red-400 whitespace-pre-wrap break-words">{{ error }}</div>
    <button @click="error = null" class="text-red-600 hover:text-red-700 flex-shrink-0 mt-1">
      <span class="material-symbols-outlined">close</span>
    </button>
  </div>

  <!-- Page Header -->
  <div class="flex flex-wrap items-center justify-between gap-4 mb-8">
    <div class="flex flex-col gap-1">
      <h1 class="text-3xl font-black leading-tight tracking-tight">Quản Lý Công Ty</h1>
      <p class="text-slate-500 dark:text-slate-400 text-base">Quản lý danh sách công ty và tình trạng xác minh.</p>
    </div>
  </div>

  <!-- Stats Grid -->
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
    <div class="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
      <div class="flex items-center justify-between mb-2">
        <span class="text-slate-500 text-sm font-medium">Tổng công ty</span>
        <span class="material-symbols-outlined text-[#2463eb]/40">business</span>
      </div>
      <div class="text-2xl font-bold">{{ stats.total }}</div>
      <div class="mt-2 text-xs text-emerald-600 font-medium flex items-center">
        <span class="material-symbols-outlined text-xs mr-1">check_circle</span> Tất cả chủ động quản lý
      </div>
    </div>
    <div class="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
      <div class="flex items-center justify-between mb-2">
        <span class="text-slate-500 text-sm font-medium">Đã duyệt</span>
        <span class="material-symbols-outlined text-[#2463eb]/40">verified</span>
      </div>
      <div class="text-2xl font-bold">{{ stats.active }}</div>
      <div class="mt-2 text-xs text-emerald-600 font-medium flex items-center">
        <span class="material-symbols-outlined text-xs mr-1">trending_up</span> Hoạt động
      </div>
    </div>
    <div class="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
      <div class="flex items-center justify-between mb-2">
        <span class="text-slate-500 text-sm font-medium">Tạm ngưng</span>
        <span class="material-symbols-outlined text-amber-500/40">pending_actions</span>
      </div>
      <div class="text-2xl font-bold text-amber-500">{{ stats.paused }}</div>
      <div class="mt-2 text-xs text-amber-600 font-medium flex items-center">
        <span class="material-symbols-outlined text-xs mr-1">pause_circle</span> Cần rà soát
      </div>
    </div>
    <div class="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
      <div class="flex items-center justify-between mb-2">
        <span class="text-slate-500 text-sm font-medium">Quy mô nổi bật</span>
        <span class="material-symbols-outlined text-[#2463eb]/40">bar_chart</span>
      </div>
      <div class="text-2xl font-bold text-[#2463eb]">
        {{ Object.keys(stats.scaleSummary).find((key) => stats.scaleSummary[key]) || 'N/A' }}
      </div>
      <div class="mt-2 text-xs text-slate-500 font-medium flex items-center">
        <span class="material-symbols-outlined text-xs mr-1">insights</span> Theo dữ liệu hiện tại
      </div>
    </div>
  </div>

  <!-- Filters -->
  <div class="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm mb-6 flex flex-wrap items-center gap-4">
    <div class="flex-1 min-w-[300px] relative">
      <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">search</span>
      <input 
        v-model="searchQuery"
        @input="onSearch"
        class="w-full pl-10 pr-4 py-2 bg-slate-50 dark:bg-slate-800 border-none rounded-lg focus:ring-2 focus:ring-[#2463eb] text-sm" 
        placeholder="Tìm theo tên công ty hoặc địa chỉ..." 
        type="text" 
      />
    </div>
    <div class="flex items-center gap-3">
      <select 
        v-model="selectedStatus"
        @change="onFilterChange"
        class="bg-slate-50 dark:bg-slate-800 border-none rounded-lg text-sm px-4 py-2 focus:ring-2 focus:ring-[#2463eb]"
      >
        <option value="">Tất cả trạng thái</option>
        <option :value="1">Hoạt động</option>
        <option :value="0">Tạm ngưng</option>
      </select>
      <select
        v-model="perPage"
        @change="onFilterChange"
        class="bg-slate-50 dark:bg-slate-800 border-none rounded-lg text-sm px-4 py-2 focus:ring-2 focus:ring-[#2463eb]"
      >
        <option :value="5">5 / trang</option>
        <option :value="10">10 / trang</option>
        <option :value="20">20 / trang</option>
      </select>
      <button
        @click="resetFilters"
        class="px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-700 text-sm font-medium hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
      >
        Reset bộ lọc
      </button>
    </div>
  </div>

  <!-- Company Table -->
  <div ref="listSectionRef" class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
    <div class="overflow-x-auto">
      <table class="w-full text-left border-collapse">
        <thead>
          <tr class="border-b border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/50">
            <th class="px-6 py-4 font-semibold text-xs uppercase tracking-wider text-slate-500">Tên công ty</th>
            <th class="px-6 py-4 font-semibold text-xs uppercase tracking-wider text-slate-500">Quy mô</th>
            <th class="px-6 py-4 font-semibold text-xs uppercase tracking-wider text-slate-500">Địa chỉ</th>
            <th class="px-6 py-4 font-semibold text-xs uppercase tracking-wider text-slate-500">Trạng thái</th>
            <th class="px-6 py-4 font-semibold text-xs uppercase tracking-wider text-slate-500 text-center">Hành động</th>
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
                <span class="material-symbols-outlined text-3xl mb-2">inbox</span>
                <div>Không tìm thấy công ty</div>
              </td>
            </tr>
          </template>
          <template v-else>
            <tr v-for="company in companies" :key="company.id" class="hover:bg-slate-50/50 dark:hover:bg-slate-800/50 transition-colors">
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-full bg-[#2463eb]/10 flex items-center justify-center text-[#2463eb] font-bold">
                    {{ company.ten_cong_ty?.charAt(0).toUpperCase() || 'C' }}
                  </div>
                  <div>
                    <div class="font-semibold text-sm">{{ company.ten_cong_ty }}</div>
                    <div class="text-xs text-slate-500">{{ company.website || 'N/A' }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 text-sm">
                {{ company.quy_mo }}
              </td>
              <td class="px-6 py-4 text-sm text-slate-600 dark:text-slate-400">
                {{ company.dia_chi }}
              </td>
              <td class="px-6 py-4">
                <span :class="['px-2 py-1 rounded text-xs font-medium', statusColors[company.trang_thai]]">
                  {{ statusMap[company.trang_thai] || 'N/A' }}
                </span>
              </td>
              <td class="px-6 py-4 text-right">
                <div class="flex items-center justify-end gap-2">
                  <button 
                    @click="openEditCompanyModal(company)"
                    class="p-2 text-slate-400 hover:text-[#2463eb] transition-colors rounded-lg"
                    title="Chỉnh sửa"
                  >
                    <span class="material-symbols-outlined text-xl">edit</span>
                  </button>
                  <button 
                    @click="toggleStatus(company.id)"
                    class="p-2 text-slate-400 hover:text-amber-600 transition-colors rounded-lg"
                    title="Đổi trạng thái"
                  >
                    <span class="material-symbols-outlined text-xl">toggle_on</span>
                  </button>
                  <button 
                    @click="confirmDelete(company)"
                    class="p-2 text-slate-400 hover:text-red-600 transition-colors rounded-lg"
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
    <!-- Pagination -->
    <AdminPaginationBar
      v-if="!loading && companies.length > 0"
      :summary="`Hiển thị ${companies.length} / ${totalCompanies} công ty`"
      :current-page="currentPage"
      :total-pages="totalPages"
      @prev="goToPreviousPage"
      @next="goToNextPage"
    />
  </div>

  <!-- Modal: Tạo/Sửa công ty -->
  <div
    v-if="showModal"
    class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/25 p-4 backdrop-blur-sm"
    @click.self="closeEditCompanyModal"
  >
    <div class="flex max-h-[calc(100vh-2rem)] w-full max-w-4xl flex-col overflow-hidden rounded-[28px] border border-slate-200 bg-white shadow-[0_24px_80px_rgba(15,23,42,0.18)]">
      <div class="flex items-start justify-between gap-4 border-b border-slate-200 px-6 py-5 sm:px-7">
        <div class="space-y-3">
          <div class="flex flex-wrap items-center gap-3">
            <span class="inline-flex h-11 w-11 items-center justify-center rounded-2xl bg-[#2463eb]/10 text-[#2463eb]">
              <span class="material-symbols-outlined text-[22px]">apartment</span>
            </span>
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.32em] text-slate-400">Quản lý công ty</p>
              <h3 class="text-xl font-bold text-slate-900">Cập nhật hồ sơ doanh nghiệp</h3>
            </div>
          </div>
          <p class="max-w-2xl text-sm leading-6 text-slate-500">
            Điều chỉnh thông tin hiển thị cho doanh nghiệp để dữ liệu trong hệ thống đồng bộ và dễ rà soát hơn.
          </p>
        </div>
        <button
          @click="closeEditCompanyModal"
          class="inline-flex h-11 w-11 items-center justify-center rounded-2xl border border-slate-200 bg-white text-slate-400 transition hover:border-slate-300 hover:text-slate-700"
          type="button"
        >
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>

      <form @submit.prevent="submitForm" class="flex min-h-0 flex-1 flex-col">
        <div class="grid gap-4 border-b border-slate-200 bg-slate-50/80 px-6 py-5 sm:grid-cols-3 sm:px-7">
          <div class="rounded-2xl border border-slate-200 bg-white p-4">
            <p class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">Doanh nghiệp</p>
            <p class="mt-2 text-base font-semibold text-slate-900">{{ formData.ten_cong_ty || 'Chưa nhập tên công ty' }}</p>
            <p class="mt-1 text-sm text-slate-500">{{ formData.website || 'Chưa có website' }}</p>
          </div>
          <div class="rounded-2xl border border-slate-200 bg-white p-4">
            <p class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">Liên hệ</p>
            <p class="mt-2 text-base font-semibold text-slate-900">{{ formData.email || 'Chưa có email liên hệ' }}</p>
            <p class="mt-1 text-sm text-slate-500">{{ formData.dien_thoai || 'Chưa có số điện thoại' }}</p>
          </div>
          <div class="rounded-2xl border border-slate-200 bg-white p-4">
            <p class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">Trạng thái</p>
            <div class="mt-3">
              <span :class="['inline-flex rounded-full px-3 py-1 text-sm font-semibold', statusPillColors[formData.trang_thai]]">
                {{ statusMap[formData.trang_thai] }}
              </span>
            </div>
            <p class="mt-2 text-sm text-slate-500">Kiểm soát khả năng hiển thị và vận hành của công ty trong hệ thống.</p>
          </div>
        </div>

        <div class="min-h-0 flex-1 overflow-y-auto px-6 py-6 sm:px-7">
          <div class="grid gap-5 lg:grid-cols-2">
            <div class="space-y-2">
              <label class="block text-sm font-semibold text-slate-700">Tên công ty</label>
              <input v-model="formData.ten_cong_ty" type="text" required class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-base text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-[#2463eb] focus:bg-white focus:ring-2 focus:ring-[#2463eb]/20" />
            </div>
            <div class="space-y-2">
              <label class="block text-sm font-semibold text-slate-700">Mã số thuế</label>
              <input v-model="formData.ma_so_thue" type="text" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-base text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-[#2463eb] focus:bg-white focus:ring-2 focus:ring-[#2463eb]/20" />
            </div>
            <div class="space-y-2 lg:col-span-2">
              <label class="block text-sm font-semibold text-slate-700">Địa chỉ</label>
              <input v-model="formData.dia_chi" type="text" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-base text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-[#2463eb] focus:bg-white focus:ring-2 focus:ring-[#2463eb]/20" />
            </div>
            <div class="space-y-2">
              <label class="block text-sm font-semibold text-slate-700">Điện thoại</label>
              <input v-model="formData.dien_thoai" type="text" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-base text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-[#2463eb] focus:bg-white focus:ring-2 focus:ring-[#2463eb]/20" />
            </div>
            <div class="space-y-2">
              <label class="block text-sm font-semibold text-slate-700">Email liên hệ</label>
              <input v-model="formData.email" type="email" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-base text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-[#2463eb] focus:bg-white focus:ring-2 focus:ring-[#2463eb]/20" />
            </div>
            <div class="space-y-2">
              <label class="block text-sm font-semibold text-slate-700">Quy mô</label>
              <select v-model="formData.quy_mo" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-base text-slate-900 outline-none transition focus:border-[#2463eb] focus:bg-white focus:ring-2 focus:ring-[#2463eb]/20">
                <option value="">-- Chọn quy mô --</option>
                <option v-for="option in scaleOptions" :key="option.value" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
            </div>
            <div class="space-y-2">
              <label class="block text-sm font-semibold text-slate-700">Trạng thái</label>
              <select v-model.number="formData.trang_thai" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-base text-slate-900 outline-none transition focus:border-[#2463eb] focus:bg-white focus:ring-2 focus:ring-[#2463eb]/20">
                <option :value="1">Hoạt động</option>
                <option :value="0">Tạm ngưng</option>
              </select>
            </div>
            <div class="space-y-2 lg:col-span-2">
              <label class="block text-sm font-semibold text-slate-700">Website</label>
              <input v-model="formData.website" type="text" placeholder="https://..." class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-base text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-[#2463eb] focus:bg-white focus:ring-2 focus:ring-[#2463eb]/20" />
            </div>
            <div class="space-y-2 lg:col-span-2">
              <label class="block text-sm font-semibold text-slate-700">Mô tả</label>
              <textarea v-model="formData.mo_ta" rows="5" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-base leading-7 text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-[#2463eb] focus:bg-white focus:ring-2 focus:ring-[#2463eb]/20"></textarea>
            </div>
          </div>
        </div>

        <div class="flex flex-col-reverse gap-3 border-t border-slate-200 bg-white px-6 py-5 sm:flex-row sm:justify-end sm:px-7">
          <button
            type="button"
            @click="closeEditCompanyModal"
            class="inline-flex items-center justify-center rounded-2xl border border-slate-200 px-5 py-3 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:bg-slate-50"
          >
            Hủy
          </button>
          <button
            type="submit"
            :disabled="saving"
            class="inline-flex items-center justify-center rounded-2xl bg-[#2463eb] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[#1d56cf] disabled:cursor-not-allowed disabled:opacity-70"
          >
            {{ saving ? 'Đang cập nhật...' : 'Cập nhật công ty' }}
          </button>
        </div>
      </form>
    </div>
  </div>

  <!-- Modal: Xác nhận xóa -->
  <div v-if="showDeleteModal" class="fixed inset-0 bg-black/50 dark:bg-black/70 flex items-center justify-center z-50">
    <div class="bg-white dark:bg-slate-900 rounded-xl shadow-xl max-w-sm w-full mx-4">
      <div class="p-6">
        <div class="flex items-center gap-3 mb-4">
          <span class="material-symbols-outlined text-2xl text-red-600">warning</span>
          <h3 class="text-lg font-semibold">Xóa công ty</h3>
        </div>
        <p class="text-slate-600 dark:text-slate-400 mb-6">
          Bạn có chắc muốn xóa <strong>{{ deletingCompany?.ten_cong_ty }}</strong>? Hành động này không thể hoàn tác.
        </p>
        <div class="flex gap-3">
          <button @click="showDeleteModal = false" class="flex-1 px-4 py-2 border border-slate-300 dark:border-slate-700 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
            Hủy
          </button>
          <button @click="deleteCompany" class="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium">
            Xóa
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
