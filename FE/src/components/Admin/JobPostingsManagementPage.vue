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
      <h1 class="text-3xl font-black tracking-tight">Tin tuyển dụng</h1>
      <p class="mt-1 text-slate-500">Quản lý toàn bộ tin tuyển dụng, công ty sở hữu, ngành nghề và thời hạn hiển thị.</p>
    </div>
    <button @click="openNewJobModal" class="flex h-11 items-center gap-2 rounded-xl bg-[#2463eb] px-5 text-sm font-bold text-white shadow-md shadow-[#2463eb]/20 transition-all hover:bg-[#2463eb]/90">
      <span class="material-symbols-outlined text-lg">add</span> Thêm tin tuyển dụng
    </button>
  </div>

  <div class="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-4">
    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="mb-2 flex items-center justify-between">
        <span class="text-sm font-medium text-slate-500">Tổng tin đăng</span>
        <span class="material-symbols-outlined text-[#2463eb]/40">work</span>
      </div>
      <div class="text-2xl font-bold">{{ stats.total }}</div>
      <div class="mt-2 text-xs font-medium text-[#2463eb]">Toàn bộ tin trong hệ thống</div>
    </div>
    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="mb-2 flex items-center justify-between">
        <span class="text-sm font-medium text-slate-500">Đang hoạt động</span>
        <span class="material-symbols-outlined text-emerald-500/40">check_circle</span>
      </div>
      <div class="text-2xl font-bold">{{ stats.active }}</div>
      <div class="mt-2 text-xs font-medium text-emerald-600">Tin đang hiển thị và nhận ứng tuyển</div>
    </div>
    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="mb-2 flex items-center justify-between">
        <span class="text-sm font-medium text-slate-500">Tạm ngưng</span>
        <span class="material-symbols-outlined text-amber-500/40">pause_circle</span>
      </div>
      <div class="text-2xl font-bold">{{ stats.inactive }}</div>
      <div class="mt-2 text-xs font-medium text-amber-600">Tin đang bị tắt thủ công</div>
    </div>
    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="mb-2 flex items-center justify-between">
        <span class="text-sm font-medium text-slate-500">Đã hết hạn</span>
        <span class="material-symbols-outlined text-slate-500/40">event_busy</span>
      </div>
      <div class="text-2xl font-bold">{{ stats.expired }}</div>
      <div class="mt-2 text-xs font-medium text-slate-500">Tính trên dữ liệu đang tải</div>
    </div>
  </div>

  <div class="mb-6 flex flex-wrap items-center gap-4 rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
    <div class="relative min-w-[280px] flex-1">
      <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">search</span>
      <input v-model="searchQuery" @input="onSearch" class="w-full rounded-lg border-none bg-slate-50 py-2 pl-10 pr-4 text-sm focus:ring-2 focus:ring-[#2463eb] dark:bg-slate-800" placeholder="Tìm theo tiêu đề hoặc công ty..." type="text" />
    </div>
    <select v-model="selectedCompanyId" @change="onFilterChange" class="rounded-lg border-none bg-slate-50 px-4 py-2 text-sm focus:ring-2 focus:ring-[#2463eb] dark:bg-slate-800">
      <option value="">Tất cả công ty</option>
      <option v-for="company in companyOptions" :key="company.id" :value="String(company.id)">{{ company.ten_cong_ty }}</option>
    </select>
    <select v-model="selectedStatus" @change="onFilterChange" class="rounded-lg border-none bg-slate-50 px-4 py-2 text-sm focus:ring-2 focus:ring-[#2463eb] dark:bg-slate-800">
      <option value="">Tất cả trạng thái</option>
      <option value="1">Hoạt động</option>
      <option value="0">Tạm ngưng</option>
    </select>
    <select v-model="sortOption" @change="onFilterChange" class="rounded-lg border-none bg-slate-50 px-4 py-2 text-sm focus:ring-2 focus:ring-[#2463eb] dark:bg-slate-800">
      <option value="newest">Mới nhất</option>
      <option value="oldest">Cũ nhất</option>
      <option value="title_asc">Tiêu đề A-Z</option>
      <option value="title_desc">Tiêu đề Z-A</option>
      <option value="expiry_asc">Hạn gần nhất</option>
      <option value="expiry_desc">Hạn xa nhất</option>
    </select>
  </div>

  <div class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
    <div class="overflow-x-auto">
      <table class="w-full border-collapse text-left">
        <thead>
          <tr class="border-b border-slate-200 bg-slate-50/50 dark:border-slate-800 dark:bg-slate-800/50">
            <th class="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">Tin tuyển dụng</th>
            <th class="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">Công ty</th>
            <th class="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">Ngành nghề</th>
            <th class="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">Hạn nộp</th>
            <th class="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">Trạng thái</th>
            <th class="px-6 py-4 text-center text-xs font-semibold uppercase tracking-wider text-slate-500">Hành động</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100 dark:divide-slate-800">
          <template v-if="loading">
            <tr><td colspan="6" class="px-6 py-8 text-center text-slate-500"><span class="material-symbols-outlined animate-spin">hourglass_empty</span><div>Đang tải...</div></td></tr>
          </template>
          <template v-else-if="jobPostings.length === 0">
            <tr><td colspan="6" class="px-6 py-8 text-center text-slate-500"><span class="material-symbols-outlined mb-2 text-3xl">inbox</span><div>Không tìm thấy tin tuyển dụng</div></td></tr>
          </template>
          <template v-else>
            <tr v-for="job in jobPostings" :key="job.id" class="transition-colors hover:bg-slate-50/50 dark:hover:bg-slate-800/50">
              <td class="px-6 py-4">
                <div class="min-w-[250px]">
                  <div class="text-sm font-semibold">{{ job.tieu_de }}</div>
                  <div class="mt-1 flex flex-wrap items-center gap-2 text-xs text-slate-500">
                    <span>{{ job.dia_diem_lam_viec || 'Chưa có địa điểm' }}</span>
                    <span v-if="job.hinh_thuc_lam_viec">• {{ job.hinh_thuc_lam_viec }}</span>
                    <span v-if="job.cap_bac">• {{ job.cap_bac }}</span>
                  </div>
                  <div class="mt-1 text-xs text-slate-400">
                    {{ formatSalary(job.muc_luong) }}<span v-if="job.so_luong_tuyen"> • {{ job.so_luong_tuyen }} vị trí</span>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                  <div class="flex h-10 w-10 items-center justify-center rounded-full bg-[#2463eb]/10 font-bold text-[#2463eb]">{{ buildCompanyBadge(job.cong_ty?.ten_cong_ty) }}</div>
                  <div class="min-w-[160px]">
                    <div class="text-sm font-medium">{{ job.cong_ty?.ten_cong_ty || 'N/A' }}</div>
                    <div class="text-xs text-slate-500">Lượt xem: {{ job.luot_xem ?? 0 }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4">
                <div class="flex max-w-[220px] flex-wrap gap-2">
                  <span v-for="industry in job.nganh_nghes || []" :key="industry.id" class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-300">{{ industry.ten_nganh }}</span>
                  <span v-if="!(job.nganh_nghes || []).length" class="text-sm text-slate-400">Chưa gán ngành</span>
                </div>
              </td>
              <td class="px-6 py-4">
                <div class="text-sm text-slate-700 dark:text-slate-300">{{ formatDate(job.ngay_het_han) }}</div>
                <div v-if="isExpired(job)" class="mt-1 text-xs font-medium text-amber-600">Đã hết hạn</div>
              </td>
              <td class="px-6 py-4"><span :class="getStatusClasses(job)">{{ getStatusLabel(job) }}</span></td>
              <td class="px-6 py-4 text-right">
                <div class="flex items-center justify-center gap-2">
                  <button @click="openEditJobModal(job)" :disabled="actionLoadingId === job.id" class="rounded-lg p-2 text-slate-400 transition-colors hover:text-[#2463eb] disabled:cursor-not-allowed disabled:opacity-50" title="Chỉnh sửa"><span class="material-symbols-outlined text-xl">edit</span></button>
                  <button @click="toggleStatus(job)" :disabled="actionLoadingId === job.id" class="rounded-lg p-2 text-slate-400 transition-colors hover:text-amber-600 disabled:cursor-not-allowed disabled:opacity-50" title="Đổi trạng thái"><span class="material-symbols-outlined text-xl">{{ actionLoadingId === job.id ? 'progress_activity' : 'toggle_on' }}</span></button>
                  <button @click="confirmDelete(job)" :disabled="actionLoadingId === job.id" class="rounded-lg p-2 text-slate-400 transition-colors hover:text-red-600 disabled:cursor-not-allowed disabled:opacity-50" title="Xóa"><span class="material-symbols-outlined text-xl">delete</span></button>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <div v-if="!loading && jobPostings.length > 0" class="flex items-center justify-between border-t border-slate-200 bg-slate-50/50 px-6 py-4 dark:border-slate-800 dark:bg-slate-800/50">
      <div class="text-sm text-slate-500">
        Hiển thị <span class="font-medium text-slate-900 dark:text-slate-100">{{ (currentPage - 1) * perPage + 1 }}</span>
        đến <span class="font-medium text-slate-900 dark:text-slate-100">{{ Math.min(currentPage * perPage, totalJobs) }}</span>
        trên <span class="font-medium text-slate-900 dark:text-slate-100">{{ totalJobs }}</span> tin tuyển dụng
      </div>
      <div class="flex items-center gap-2">
        <button @click="goToPreviousPage" :disabled="currentPage === 1" class="rounded-lg border border-slate-200 p-2 transition-colors hover:bg-slate-100 disabled:opacity-50 dark:border-slate-700 dark:hover:bg-slate-700"><span class="material-symbols-outlined">chevron_left</span></button>
        <button v-for="page in totalPages" :key="page" @click="goToPage(page)" :class="['h-8 w-8 rounded-lg text-sm font-medium transition-colors', currentPage === page ? 'bg-[#2463eb] text-white' : 'hover:bg-slate-200 dark:hover:bg-slate-700']">{{ page }}</button>
        <button @click="goToNextPage" :disabled="currentPage === totalPages || totalPages === 0" class="rounded-lg border border-slate-200 p-2 transition-colors hover:bg-slate-100 disabled:opacity-50 dark:border-slate-700 dark:hover:bg-slate-700"><span class="material-symbols-outlined">chevron_right</span></button>
      </div>
    </div>
  </div>

  <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-black/50 p-4 dark:bg-black/70">
    <div class="my-auto flex max-h-[calc(100vh-2rem)] w-full max-w-3xl flex-col overflow-hidden rounded-xl bg-white shadow-xl dark:bg-slate-900">
      <div class="flex items-center justify-between border-b border-slate-200 px-6 py-4 dark:border-slate-800">
        <h3 class="text-lg font-semibold">{{ editingJobId ? 'Chỉnh sửa tin tuyển dụng' : 'Tạo tin tuyển dụng mới' }}</h3>
        <button @click="closeModal" :disabled="submitting" class="text-slate-400 hover:text-slate-600 disabled:opacity-60"><span class="material-symbols-outlined">close</span></button>
      </div>
      <form @submit.prevent="submitForm" class="flex min-h-0 flex-1 flex-col">
        <div class="min-h-0 flex-1 overflow-y-auto p-6">
          <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div v-if="modalError" class="md:col-span-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700 dark:border-red-900 dark:bg-red-900/20 dark:text-red-400">{{ modalError }}</div>
            <div class="md:col-span-2">
              <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Tiêu đề</label>
              <input v-model="formData.tieu_de" type="text" required maxlength="200" class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800" />
            </div>
            <div>
              <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Công ty</label>
              <select v-if="!editingJobId" v-model="formData.cong_ty_id" required class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800">
                <option value="">-- Chọn công ty --</option>
                <option v-for="company in companyOptions" :key="company.id" :value="String(company.id)">{{ company.ten_cong_ty }}</option>
              </select>
              <div v-else class="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-600 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300">{{ editingCompanyName || 'Không xác định' }}</div>
            </div>
            <div>
              <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Trạng thái</label>
              <select v-model="formData.trang_thai" class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800">
                <option value="1">Hoạt động</option>
                <option value="0">Tạm ngưng</option>
              </select>
            </div>
            <div>
              <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Địa điểm làm việc</label>
              <input v-model="formData.dia_diem_lam_viec" type="text" required maxlength="255" class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800" />
            </div>
            <div>
              <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Hình thức làm việc</label>
              <select v-model="formData.hinh_thuc_lam_viec" class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800">
                <option value="">-- Chọn hình thức --</option>
                <option v-for="option in jobTypeOptions" :key="option" :value="option">{{ option }}</option>
              </select>
            </div>
            <div>
              <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Cấp bậc</label>
              <input v-model="formData.cap_bac" type="text" maxlength="50" placeholder="Ví dụ: Nhân viên, Senior..." class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800" />
            </div>
            <div>
              <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Kinh nghiệm yêu cầu</label>
              <input v-model="formData.kinh_nghiem_yeu_cau" type="text" maxlength="100" placeholder="Ví dụ: 2 năm" class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800" />
            </div>
            <div>
              <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Số lượng tuyển</label>
              <input v-model="formData.so_luong_tuyen" type="number" min="1" class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800" />
            </div>
            <div>
              <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Mức lương (VNĐ)</label>
              <input v-model="formData.muc_luong" type="number" min="0" step="1000" class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800" />
            </div>
            <div class="md:col-span-2">
              <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Ngành nghề</label>
              <select v-model="formData.nganh_nghes" multiple class="min-h-[132px] w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800">
                <option v-for="industry in industryOptions" :key="industry.id" :value="String(industry.id)">{{ industry.ten_nganh }}</option>
              </select>
              <p class="mt-1 text-xs text-slate-400">Giữ `Ctrl` hoặc `Cmd` để chọn nhiều ngành nghề.</p>
            </div>
            <div>
              <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Ngày hết hạn</label>
              <input v-model="formData.ngay_het_han" type="date" class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800" />
            </div>
            <div class="md:col-span-2">
              <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Mô tả công việc</label>
              <textarea v-model="formData.mo_ta_cong_viec" rows="6" required class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800"></textarea>
            </div>
          </div>
        </div>
        <div class="flex gap-3 border-t border-slate-200 px-6 py-4 dark:border-slate-800">
          <button type="button" @click="closeModal" :disabled="submitting" class="flex-1 rounded-lg border border-slate-300 px-4 py-2 transition-colors hover:bg-slate-50 disabled:opacity-60 dark:border-slate-700 dark:hover:bg-slate-800">Hủy</button>
          <button type="submit" :disabled="submitting" class="flex-1 rounded-lg bg-[#2463eb] px-4 py-2 font-medium text-white transition-colors hover:bg-[#2463eb]/90 disabled:opacity-60">{{ submitting ? 'Đang xử lý...' : editingJobId ? 'Cập nhật' : 'Tạo' }}</button>
        </div>
      </form>
    </div>
  </div>

  <div v-if="showDeleteModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 dark:bg-black/70">
    <div class="mx-4 w-full max-w-sm rounded-xl bg-white shadow-xl dark:bg-slate-900">
      <div class="p-6">
        <div class="mb-4 flex items-center gap-3"><span class="material-symbols-outlined text-2xl text-red-600">warning</span><h3 class="text-lg font-semibold">Xóa tin tuyển dụng</h3></div>
        <p class="mb-6 text-slate-600 dark:text-slate-400">Bạn có chắc muốn xóa <strong>{{ deletingJob?.tieu_de }}</strong>? Hành động này không thể hoàn tác.</p>
        <div class="flex gap-3">
          <button @click="closeDeleteModal" :disabled="actionLoadingId === deletingJob?.id" class="flex-1 rounded-lg border border-slate-300 px-4 py-2 transition-colors hover:bg-slate-50 disabled:opacity-60 dark:border-slate-700 dark:hover:bg-slate-800">Hủy</button>
          <button @click="deleteJob" :disabled="actionLoadingId === deletingJob?.id" class="flex-1 rounded-lg bg-red-600 px-4 py-2 font-medium text-white transition-colors hover:bg-red-700 disabled:opacity-60">{{ actionLoadingId === deletingJob?.id ? 'Đang xóa...' : 'Xóa' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import AlertMessage from '@/components/AlertMessage.vue'
import { companyService, industryService, jobPostingService } from '@/services/api'

const jobPostings = ref([])
const companyOptions = ref([])
const industryOptions = ref([])
const loading = ref(false)
const error = ref(null)
const currentPage = ref(1)
const totalJobs = ref(0)
const perPage = ref(5)
const searchQuery = ref('')
const selectedCompanyId = ref('')
const selectedStatus = ref('')
const sortOption = ref('newest')
const showModal = ref(false)
const showDeleteModal = ref(false)
const editingJobId = ref(null)
const editingCompanyName = ref('')
const deletingJob = ref(null)
const submitting = ref(false)
const modalError = ref('')
const actionLoadingId = ref(null)
const toast = reactive({ message: '', type: 'success' })
const stats = reactive({ total: 0, active: 0, inactive: 0, expired: 0 })
const formData = reactive({
  tieu_de: '',
  mo_ta_cong_viec: '',
  dia_diem_lam_viec: '',
  hinh_thuc_lam_viec: '',
  cap_bac: '',
  so_luong_tuyen: '1',
  muc_luong: '',
  kinh_nghiem_yeu_cau: '',
  ngay_het_han: '',
  cong_ty_id: '',
  trang_thai: '1',
  nganh_nghes: []
})

const jobTypeOptions = ['Toàn thời gian', 'Bán thời gian', 'Thực tập', 'Remote', 'Freelance']
const totalPages = computed(() => Math.ceil(totalJobs.value / perPage.value))
let searchDebounceTimer = null
let toastTimer = null

const formatDate = (value) => {
  if (!value) return 'Không giới hạn'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? 'Không hợp lệ' : date.toLocaleDateString('vi-VN')
}

const formatDateInput = (value) => {
  if (!value) return ''
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? '' : date.toISOString().slice(0, 10)
}

const formatSalary = (value) => {
  const amount = Number(value)
  if (!amount) return 'Lương thỏa thuận'
  return `${amount.toLocaleString('vi-VN')} VNĐ`
}

const buildCompanyBadge = (name) => {
  const parts = String(name || '').trim().split(/\s+/).filter(Boolean)
  if (!parts.length) return 'CT'
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase()
  return `${parts[0][0]}${parts[1][0]}`.toUpperCase()
}

const isExpired = (job) => {
  if (!job?.ngay_het_han) return false
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const expiryDate = new Date(job.ngay_het_han)
  expiryDate.setHours(0, 0, 0, 0)
  return expiryDate < today
}

const getStatusLabel = (job) => {
  if (Number(job?.trang_thai) !== 1) return 'Tạm ngưng'
  if (isExpired(job)) return 'Hết hạn'
  return 'Hoạt động'
}

const getStatusClasses = (job) => {
  if (Number(job?.trang_thai) !== 1) return 'rounded-full bg-amber-100 px-2.5 py-1 text-xs font-medium text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'
  if (isExpired(job)) return 'rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-300'
  return 'rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-medium text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
}

const resolveSortFn = () => {
  switch (sortOption.value) {
    case 'oldest': return (a, b) => new Date(a.created_at || 0) - new Date(b.created_at || 0)
    case 'title_asc': return (a, b) => String(a.tieu_de || '').localeCompare(String(b.tieu_de || ''), 'vi')
    case 'title_desc': return (a, b) => String(b.tieu_de || '').localeCompare(String(a.tieu_de || ''), 'vi')
    case 'expiry_asc': return (a, b) => (a.ngay_het_han || '9999-12-31').localeCompare(b.ngay_het_han || '9999-12-31')
    case 'expiry_desc': return (a, b) => (b.ngay_het_han || '').localeCompare(a.ngay_het_han || '')
    default: return (a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0)
  }
}

const normalizeListResponse = (response) => {
  if (Array.isArray(response)) return { items: response, total: response.length }
  if (Array.isArray(response?.data)) return { items: response.data, total: response.total ?? response.meta?.total ?? response.data.length }
  if (Array.isArray(response?.data?.data)) return { items: response.data.data, total: response.data.meta?.total ?? response.data.total ?? response.total ?? response.data.data.length }
  return { items: [], total: 0 }
}

const normalizeStatsResponse = (response) => {
  const source = response?.data ?? response ?? {}
  return {
    total: source.total ?? source.tong_tin ?? source.tong ?? 0,
    active: source.active ?? source.hoat_dong ?? 0,
    inactive: source.inactive ?? source.tam_ngung ?? 0
  }
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

const resetForm = () => {
  formData.tieu_de = ''
  formData.mo_ta_cong_viec = ''
  formData.dia_diem_lam_viec = ''
  formData.hinh_thuc_lam_viec = ''
  formData.cap_bac = ''
  formData.so_luong_tuyen = '1'
  formData.muc_luong = ''
  formData.kinh_nghiem_yeu_cau = ''
  formData.ngay_het_han = ''
  formData.cong_ty_id = ''
  formData.trang_thai = '1'
  formData.nganh_nghes = []
  modalError.value = ''
  editingCompanyName.value = ''
}

const buildPayload = () => {
  const payload = {
    tieu_de: formData.tieu_de,
    mo_ta_cong_viec: formData.mo_ta_cong_viec,
    dia_diem_lam_viec: formData.dia_diem_lam_viec,
    hinh_thuc_lam_viec: formData.hinh_thuc_lam_viec || null,
    cap_bac: formData.cap_bac || null,
    so_luong_tuyen: formData.so_luong_tuyen ? Number(formData.so_luong_tuyen) : null,
    muc_luong: formData.muc_luong ? Number(formData.muc_luong) : null,
    kinh_nghiem_yeu_cau: formData.kinh_nghiem_yeu_cau || null,
    ngay_het_han: formData.ngay_het_han || null,
    trang_thai: Number(formData.trang_thai),
    nganh_nghes: formData.nganh_nghes.map((id) => Number(id))
  }
  if (!editingJobId.value) payload.cong_ty_id = Number(formData.cong_ty_id)
  return payload
}

const loadJobOptions = async () => {
  try {
    const [companyResponse, industryResponse] = await Promise.all([
      companyService.getCompanies({ per_page: 100, sort_by: 'ten_cong_ty', sort_dir: 'asc' }),
      industryService.getIndustries({ per_page: 100, sort_by: 'ten_nganh', sort_dir: 'asc', trang_thai: 1 })
    ])
    companyOptions.value = normalizeListResponse(companyResponse).items
    industryOptions.value = normalizeListResponse(industryResponse).items
  } catch (err) {
    error.value = err.message || 'Không thể tải danh sách công ty và ngành nghề'
  }
}

const loadJobPostings = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await jobPostingService.getJobPostings({
      page: currentPage.value,
      per_page: perPage.value,
      search: searchQuery.value.trim() || undefined,
      cong_ty_id: selectedCompanyId.value ? Number(selectedCompanyId.value) : undefined,
      trang_thai: selectedStatus.value === '' ? undefined : Number(selectedStatus.value)
    })
    const { items, total } = normalizeListResponse(response)
    jobPostings.value = [...items].sort(resolveSortFn())
    totalJobs.value = total

    try {
      const statsResponse = await jobPostingService.getJobPostingStats()
      const normalized = normalizeStatsResponse(statsResponse)
      stats.total = normalized.total
      stats.active = normalized.active
      stats.inactive = normalized.inactive
    } catch {
      stats.total = total
      stats.active = items.filter((item) => Number(item.trang_thai) === 1).length
      stats.inactive = items.filter((item) => Number(item.trang_thai) !== 1).length
    }

    stats.expired = items.filter((item) => isExpired(item)).length
  } catch (err) {
    error.value = err.message || 'Không thể tải danh sách tin tuyển dụng'
  } finally {
    loading.value = false
  }
}

const openNewJobModal = async () => {
  resetForm()
  editingJobId.value = null
  await loadJobOptions()
  showModal.value = true
}

const openEditJobModal = async (job) => {
  modalError.value = ''
  error.value = null
  actionLoadingId.value = job.id
  try {
    await loadJobOptions()
    const response = await jobPostingService.getJobPostingById(job.id)
    const detail = response?.data ?? response ?? job
    editingJobId.value = detail.id ?? job.id
    editingCompanyName.value = detail.cong_ty?.ten_cong_ty ?? job.cong_ty?.ten_cong_ty ?? ''
    formData.tieu_de = detail.tieu_de ?? ''
    formData.mo_ta_cong_viec = detail.mo_ta_cong_viec ?? ''
    formData.dia_diem_lam_viec = detail.dia_diem_lam_viec ?? ''
    formData.hinh_thuc_lam_viec = detail.hinh_thuc_lam_viec ?? ''
    formData.cap_bac = detail.cap_bac ?? ''
    formData.so_luong_tuyen = String(detail.so_luong_tuyen ?? 1)
    formData.muc_luong = detail.muc_luong != null ? String(detail.muc_luong) : ''
    formData.kinh_nghiem_yeu_cau = detail.kinh_nghiem_yeu_cau ?? ''
    formData.ngay_het_han = formatDateInput(detail.ngay_het_han)
    formData.cong_ty_id = detail.cong_ty_id != null ? String(detail.cong_ty_id) : ''
    formData.trang_thai = String(detail.trang_thai ?? 1)
    formData.nganh_nghes = (detail.nganh_nghes || []).map((industry) => String(industry.id))
    showModal.value = true
  } catch (err) {
    error.value = err.message || 'Không thể tải chi tiết tin tuyển dụng'
  } finally {
    actionLoadingId.value = null
  }
}

const closeModal = (force = false) => {
  if (submitting.value && !force) return
  showModal.value = false
  editingJobId.value = null
  editingCompanyName.value = ''
  modalError.value = ''
}

const closeDeleteModal = (force = false) => {
  if (actionLoadingId.value === deletingJob.value?.id && !force) return
  showDeleteModal.value = false
  deletingJob.value = null
}

const submitForm = async () => {
  modalError.value = ''
  submitting.value = true
  try {
    const payload = buildPayload()
    if (editingJobId.value) {
      await jobPostingService.updateJobPosting(editingJobId.value, payload)
      showToast('Cập nhật tin tuyển dụng thành công.')
    } else {
      await jobPostingService.createJobPosting(payload)
      showToast('Tạo tin tuyển dụng thành công.')
    }
    closeModal(true)
    await loadJobPostings()
  } catch (err) {
    const validationErrors = err?.data?.errors
    modalError.value = validationErrors ? Object.values(validationErrors).flat().join('\n') : err.message || 'Lỗi lưu tin tuyển dụng'
  } finally {
    submitting.value = false
  }
}

const confirmDelete = (job) => {
  error.value = null
  deletingJob.value = job
  showDeleteModal.value = true
}

const deleteJob = async () => {
  if (!deletingJob.value) return
  try {
    actionLoadingId.value = deletingJob.value.id
    await jobPostingService.deleteJobPosting(deletingJob.value.id)
    showToast('Xóa tin tuyển dụng thành công.')
    closeDeleteModal(true)
    await loadJobPostings()
  } catch (err) {
    error.value = err.message || 'Lỗi xóa tin tuyển dụng'
  } finally {
    actionLoadingId.value = null
  }
}

const toggleStatus = async (job) => {
  try {
    error.value = null
    actionLoadingId.value = job.id
    await jobPostingService.toggleJobPostingStatus(job.id)
    showToast(Number(job.trang_thai) === 1 ? 'Đã chuyển tin sang tạm ngưng.' : 'Đã chuyển tin sang hoạt động.')
    await loadJobPostings()
  } catch (err) {
    error.value = err.message || 'Lỗi cập nhật trạng thái tin tuyển dụng'
  } finally {
    actionLoadingId.value = null
  }
}

const onSearch = () => {
  currentPage.value = 1
  if (searchDebounceTimer) clearTimeout(searchDebounceTimer)
  searchDebounceTimer = window.setTimeout(() => loadJobPostings(), 250)
}

const onFilterChange = () => {
  currentPage.value = 1
  loadJobPostings()
}

const goToPage = (page) => {
  currentPage.value = page
  loadJobPostings()
}

const goToPreviousPage = () => {
  if (currentPage.value === 1) return
  currentPage.value -= 1
  loadJobPostings()
}

const goToNextPage = () => {
  if (currentPage.value >= totalPages.value) return
  currentPage.value += 1
  loadJobPostings()
}

onMounted(async () => {
  await Promise.all([loadJobOptions(), loadJobPostings()])
})

onBeforeUnmount(() => {
  if (searchDebounceTimer) clearTimeout(searchDebounceTimer)
  if (toastTimer) clearTimeout(toastTimer)
})
</script>
