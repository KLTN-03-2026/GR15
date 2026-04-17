<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, computed, nextTick } from 'vue'
import { userService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'
import FormModalShell from '@/components/FormModalShell.vue'
import AdminPaginationBar from '@/components/Admin/AdminPaginationBar.vue'

const notify = useNotify()

// State
const users = ref([])
const loading = ref(false)
const error = ref(null)
const currentPage = ref(1)
const totalUsers = ref(0)
const perPage = ref(5)

// Filters
const searchQuery = ref('')
const selectedRole = ref('')
const selectedStatus = ref('')

// Stats
const stats = reactive({
  total: 0,
  jobSeekers: 0,
  employers: 0,
  pendingApprovals: 0
})

// Modals
const showModal = ref(false)
const showDeleteModal = ref(false)
const editingUser = ref(null)
const deletingUser = ref(null)
const saving = ref(false)
const listSectionRef = ref(null)
let searchDebounceTimer = null

// Form data
const formData = reactive({
  ho_ten: '',
  email: '',
  mat_khau: '',
  so_dien_thoai: '',
  ngay_sinh: '',
  gioi_tinh: '',
  dia_chi: '',
  vai_tro: 0,
  trang_thai: 1,
})

// Map vai_tro to display text
const roleMap = {
  0: 'Ứng viên',
  1: 'Nhà tuyển dụng',
  2: 'Admin'
}

const roleColors = {
  0: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
  1: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400',
  2: 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300'
}

const rolePillColors = {
  0: 'border border-blue-200 bg-blue-50 text-blue-700',
  1: 'border border-violet-200 bg-violet-50 text-violet-700',
  2: 'border border-slate-200 bg-slate-100 text-slate-700',
}

const userStatusPillColors = {
  1: 'border border-emerald-200 bg-emerald-50 text-emerald-700',
  0: 'border border-rose-200 bg-rose-50 text-rose-700',
}

const scrollToListTop = async () => {
  await nextTick()
  listSectionRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const normalizeSearchText = (value) => {
  return String(value || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .trim()
}

const normalizeDigits = (value) => {
  return String(value || '').replace(/\D/g, '')
}

const matchesUserSearch = (user, query) => {
  const normalizedQuery = normalizeSearchText(query)

  if (!normalizedQuery) {
    return true
  }

  const queryTokens = normalizedQuery.split(/\s+/).filter(Boolean)
  const name = normalizeSearchText(user?.ho_ten)
  const nameWords = name.split(/\s+/).filter(Boolean)
  const email = normalizeSearchText(user?.email)
  const phone = normalizeDigits(user?.so_dien_thoai)
  const digitQuery = normalizeDigits(query)
  const looksLikeEmailQuery = normalizedQuery.includes('@')

  return queryTokens.every((token) => {
    const matchesNameWord = nameWords.some((word) => word.includes(token))
    if (matchesNameWord) {
      return true
    }

    if (looksLikeEmailQuery || token.length >= 4) {
      if (email.includes(token)) {
        return true
      }
    }

    if (digitQuery && phone.includes(digitQuery)) {
      return true
    }

    return false
  })
}

const loadStats = async () => {
  try {
    const response = await userService.getUserStats()
    const payload = response?.data || {}

    stats.total = payload.tong || 0
    stats.jobSeekers = payload.ung_vien || 0
    stats.employers = payload.nha_tuyen_dung || 0
    stats.pendingApprovals = payload.bi_khoa || 0
  } catch (err) {
    console.error('Không thể tải thống kê người dùng', err)
  }
}

// Load users
const loadUsers = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await userService.getUsers({
      page: currentPage.value,
      per_page: perPage.value,
      vai_tro: selectedRole.value ? parseInt(selectedRole.value) : undefined,
      trang_thai: selectedStatus.value ? (selectedStatus.value === 'active' ? 1 : 0) : undefined,
      search: searchQuery.value || undefined
    })

    // Xử lý response từ API Laravel
    let users_list = []
    let total = 0

    if (response.data) {
      // Kiểm tra nếu response.data là array (format đơn giản)
      if (Array.isArray(response.data)) {
        users_list = response.data
        total = response.total || response.data.length
      }
      // Kiểm tra nếu response.data có property 'data' (paginated format)
      else if (response.data.data && Array.isArray(response.data.data)) {
        users_list = response.data.data
        total = response.data.meta?.total || response.data.total || 0
      }
      // Kiểm tra nếu response có property 'nguoi_dungs' (custom format)
      else if (response.nguoi_dungs) {
        users_list = response.nguoi_dungs
        total = response.total || response.nguoi_dungs.length
      }
    }

    const filteredUsers = users_list.filter((user) => matchesUserSearch(user, searchQuery.value))

    users.value = filteredUsers
    totalUsers.value = searchQuery.value.trim() ? filteredUsers.length : total
  } catch (err) {
    error.value = err.message || 'Không thể tải danh sách người dùng'
  } finally {
    loading.value = false
  }
}

// Open modal for editing user
const openEditUserModal = (user) => {
  editingUser.value = user.id
  formData.ho_ten = user.ho_ten
  formData.email = user.email
  formData.mat_khau = ''
  formData.so_dien_thoai = user.so_dien_thoai || ''
  formData.ngay_sinh = user.ngay_sinh || ''
  formData.gioi_tinh = user.gioi_tinh || ''
  formData.dia_chi = user.dia_chi || ''
  formData.vai_tro = user.vai_tro
  formData.trang_thai = user.trang_thai ?? 1
  showModal.value = true
}

const closeEditUserModal = () => {
  if (saving.value) return
  showModal.value = false
  editingUser.value = null
}

// Submit form
const submitForm = async () => {
  saving.value = true
  try {
    const payload = {
      ho_ten: formData.ho_ten,
      email: formData.email,
      so_dien_thoai: formData.so_dien_thoai || null,
      ngay_sinh: formData.ngay_sinh || null,
      gioi_tinh: formData.gioi_tinh || null,
      dia_chi: formData.dia_chi || null,
      vai_tro: formData.vai_tro,
      trang_thai: formData.trang_thai,
    }

    if (editingUser.value) {
      if (formData.mat_khau) {
        payload.mat_khau = formData.mat_khau
      }
      await userService.updateUser(editingUser.value, payload)
      notify.success('Đã cập nhật người dùng')
    }
    closeEditUserModal()
    await loadUsers()
    await loadStats()
  } catch (err) {
    error.value = err.message || 'Lỗi lưu người dùng'
  } finally {
    saving.value = false
  }
}

// Delete confirmation modal
const confirmDelete = (user) => {
  deletingUser.value = user
  showDeleteModal.value = true
}

// Delete user
const deleteUser = async () => {
  try {
    await userService.deleteUser(deletingUser.value.id)
    showDeleteModal.value = false
    await loadUsers()
    await loadStats()
    notify.success('Đã xóa người dùng')
  } catch (err) {
    error.value = err.message || 'Lỗi xóa người dùng'
  }
}

// Toggle lock
const toggleLock = async (userId) => {
  try {
    await userService.toggleLock(userId)
    await loadUsers()
    await loadStats()
    notify.success('Đã cập nhật trạng thái tài khoản')
  } catch (err) {
    error.value = err.message || 'Lỗi khoá/mở khoá tài khoản'
  }
}

// Computed properties
const totalPages = computed(() => Math.ceil(totalUsers.value / perPage.value))

// Watchers
const onSearch = () => {
  currentPage.value = 1

  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer)
  }

  searchDebounceTimer = window.setTimeout(() => {
    loadUsers()
  }, 250)
}

const onFilterChange = () => {
  currentPage.value = 1
  loadUsers()
}

const resetFilters = () => {
  searchQuery.value = ''
  selectedRole.value = ''
  selectedStatus.value = ''
  perPage.value = 5
  currentPage.value = 1
  loadUsers()
}

const goToPage = (page) => {
  currentPage.value = page
  loadUsers()
  scrollToListTop()
}

const goToPreviousPage = () => {
  if (currentPage.value === 1) return
  currentPage.value -= 1
  loadUsers()
  scrollToListTop()
}

const goToNextPage = () => {
  if (currentPage.value === totalPages.value) return
  currentPage.value += 1
  loadUsers()
  scrollToListTop()
}

// Lifecycle
onMounted(() => {
  loadUsers()
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
      <h1 class="text-3xl font-black leading-tight tracking-tight">Quản Lý Người Dùng</h1>
      <p class="text-slate-500 dark:text-slate-400 text-base">Quản lý danh sách người dùng và tình trạng tài khoản.</p>
    </div>
  </div>

  <!-- Stats Grid -->
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
    <div class="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
      <div class="flex items-center justify-between mb-2">
        <span class="text-slate-500 text-sm font-medium">Tổng người dùng</span>
        <span class="material-symbols-outlined text-[#2463eb]/40">groups</span>
      </div>
      <div class="text-2xl font-bold">{{ stats.total }}</div>
      <div class="mt-2 text-xs text-emerald-600 font-medium flex items-center">
        <span class="material-symbols-outlined text-xs mr-1">check_circle</span> Tất cả chủ động quản lý
      </div>
    </div>
    <div class="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
      <div class="flex items-center justify-between mb-2">
        <span class="text-slate-500 text-sm font-medium">Ứng viên</span>
        <span class="material-symbols-outlined text-[#2463eb]/40">person_search</span>
      </div>
      <div class="text-2xl font-bold">{{ stats.jobSeekers }}</div>
      <div class="mt-2 text-xs text-emerald-600 font-medium flex items-center">
        <span class="material-symbols-outlined text-xs mr-1">trending_up</span> Hoạt động
      </div>
    </div>
    <div class="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
      <div class="flex items-center justify-between mb-2">
        <span class="text-slate-500 text-sm font-medium">Nhà tuyển dụng</span>
        <span class="material-symbols-outlined text-[#2463eb]/40">business</span>
      </div>
      <div class="text-2xl font-bold">{{ stats.employers }}</div>
      <div class="mt-2 text-xs text-emerald-600 font-medium flex items-center">
        <span class="material-symbols-outlined text-xs mr-1">trending_up</span> Hoạt động
      </div>
    </div>
    <div class="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
      <div class="flex items-center justify-between mb-2">
        <span class="text-slate-500 text-sm font-medium">Đợi phê duyệt</span>
        <span class="material-symbols-outlined text-amber-500/40">pending_actions</span>
      </div>
      <div class="text-2xl font-bold text-amber-500">{{ stats.pendingApprovals }}</div>
      <div class="mt-2 text-xs text-slate-400 font-medium">Cần xử lý</div>
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
        placeholder="Tìm theo tên, email hoặc công ty..."
        type="text"
      />
    </div>
    <div class="flex items-center gap-3">
      <select
        v-model="selectedRole"
        @change="onFilterChange"
        class="bg-slate-50 dark:bg-slate-800 border-none rounded-lg text-sm px-4 py-2 focus:ring-2 focus:ring-[#2463eb]"
      >
        <option value="">Tất cả vai trò</option>
        <option value="0">Ứng viên</option>
        <option value="1">Nhà tuyển dụng</option>
        <option value="2">Admin</option>
      </select>
      <select
        v-model="selectedStatus"
        @change="onFilterChange"
        class="bg-slate-50 dark:bg-slate-800 border-none rounded-lg text-sm px-4 py-2 focus:ring-2 focus:ring-[#2463eb]"
      >
        <option value="">Tất cả trạng thái</option>
        <option value="active">Hoạt động</option>
        <option value="inactive">Khóa</option>
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

  <!-- User Table -->
  <div ref="listSectionRef" class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
    <div class="overflow-x-auto">
      <table class="w-full text-left border-collapse">
        <thead>
          <tr class="border-b border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/50">
            <th class="px-6 py-4 font-semibold text-xs uppercase tracking-wider text-slate-500">Thông tin người dùng</th>
            <th class="px-6 py-4 font-semibold text-xs uppercase tracking-wider text-slate-500">Vai trò</th>
            <th class="px-6 py-4 font-semibold text-xs uppercase tracking-wider text-slate-500">Ngày tham gia</th>
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
          <template v-else-if="users.length === 0">
            <tr>
              <td colspan="5" class="px-6 py-8 text-center text-slate-500">
                <span class="material-symbols-outlined text-3xl mb-2">inbox</span>
                <div>Không tìm thấy người dùng</div>
              </td>
            </tr>
          </template>
          <template v-else>
            <tr v-for="user in users" :key="user.id" class="hover:bg-slate-50/50 dark:hover:bg-slate-800/50 transition-colors">
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-full bg-[#2463eb]/10 flex items-center justify-center text-[#2463eb] font-bold">
                    {{ user.ho_ten?.charAt(0).toUpperCase() || 'U' }}
                  </div>
                  <div>
                    <div class="font-semibold text-sm">{{ user.ho_ten }}</div>
                    <div class="text-xs text-slate-500">{{ user.email }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4">
                <span :class="['px-2 py-1 rounded text-xs font-medium', roleColors[user.vai_tro]]">
                  {{ roleMap[user.vai_tro] }}
                </span>
              </td>
              <td class="px-6 py-4 text-sm text-slate-600 dark:text-slate-400">
                {{ user.created_at ? new Date(user.created_at).toLocaleDateString('vi-VN') : 'N/A' }}
              </td>
              <td class="px-6 py-4">
                <div class="flex items-center gap-2">
                  <div :class="['w-2 h-2 rounded-full', user.trang_thai === 1 ? 'bg-emerald-500' : 'bg-red-500']"></div>
                  <span :class="['text-sm font-medium', user.trang_thai === 1 ? 'text-emerald-600' : 'text-red-600']">
                    {{ user.trang_thai === 1 ? 'Hoạt động' : 'Đã khóa' }}
                  </span>
                </div>
              </td>
              <td class="px-6 py-4 text-right">
                <div class="flex items-center justify-center gap-2">
                  <button
                    @click="openEditUserModal(user)"
                    class="p-2 text-slate-400 hover:text-[#2463eb] transition-colors rounded-lg"
                    title="Chỉnh sửa"
                  >
                    <span class="material-symbols-outlined text-xl">edit</span>
                  </button>
                  <button
                    @click="toggleLock(user.id)"
                    :class="['p-2 transition-colors rounded-lg', user.trang_thai === 1 ? 'text-slate-400 hover:text-amber-600' : 'text-slate-400 hover:text-green-600']"
                    :title="user.trang_thai === 1 ? 'Khóa' : 'Mở khóa'"
                  >
                    <span class="material-symbols-outlined text-xl">{{ user.trang_thai === 1 ? 'block' : 'lock_open' }}</span>
                  </button>
                  <button
                    @click="confirmDelete(user)"
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
      v-if="!loading && users.length > 0"
      :summary="`Hiển thị ${users.length} / ${totalUsers} người dùng`"
      :current-page="currentPage"
      :total-pages="totalPages"
      @prev="goToPreviousPage"
      @next="goToNextPage"
    />
  </div>

  <FormModalShell
    v-if="showModal"
    eyebrow="Quản lý người dùng"
    title="Cập nhật tài khoản hệ thống"
    description="Điều chỉnh thông tin tài khoản, quyền truy cập và trạng thái hoạt động của người dùng."
    max-width-class="max-w-4xl"
    submit-label="Cập nhật người dùng"
    submit-loading-label="Đang cập nhật..."
    :saving="saving"
    @close="closeEditUserModal"
    @submit="submitForm"
  >
    <template #summary>
      <div class="rounded-2xl border border-slate-200 bg-white p-4">
        <p class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">Người dùng</p>
        <p class="mt-2 text-base font-semibold text-slate-900">{{ formData.ho_ten || 'Chưa nhập họ tên' }}</p>
        <p class="mt-1 text-sm text-slate-500">{{ formData.email || 'Chưa có email' }}</p>
      </div>
      <div class="rounded-2xl border border-slate-200 bg-white p-4">
        <p class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">Vai trò</p>
        <div class="mt-3">
          <span :class="['inline-flex rounded-full px-3 py-1 text-sm font-semibold', rolePillColors[formData.vai_tro]]">
            {{ roleMap[formData.vai_tro] }}
          </span>
        </div>
        <p class="mt-2 text-sm text-slate-500">Phân quyền hiển thị và nhóm chức năng mà tài khoản có thể truy cập.</p>
      </div>
      <div class="rounded-2xl border border-slate-200 bg-white p-4">
        <p class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">Trạng thái</p>
        <div class="mt-3">
          <span :class="['inline-flex rounded-full px-3 py-1 text-sm font-semibold', userStatusPillColors[formData.trang_thai]]">
            {{ formData.trang_thai === 1 ? 'Hoạt động' : 'Khóa' }}
          </span>
        </div>
        <p class="mt-2 text-sm text-slate-500">Dùng để kiểm soát khả năng đăng nhập và sử dụng hệ thống.</p>
      </div>
    </template>

    <div class="grid gap-5 lg:grid-cols-2">
      <div class="space-y-2">
        <label class="block text-sm font-semibold text-slate-700">Họ tên</label>
        <input v-model="formData.ho_ten" type="text" required class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-base text-slate-900 outline-none transition focus:border-[#2463eb] focus:bg-white focus:ring-2 focus:ring-[#2463eb]/20" />
      </div>
      <div class="space-y-2">
        <label class="block text-sm font-semibold text-slate-700">Email</label>
        <input v-model="formData.email" type="email" required class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-base text-slate-900 outline-none transition focus:border-[#2463eb] focus:bg-white focus:ring-2 focus:ring-[#2463eb]/20" />
      </div>
      <div class="space-y-2">
        <label class="block text-sm font-semibold text-slate-700">Mật khẩu mới</label>
        <input v-model="formData.mat_khau" type="password" minlength="6" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-base text-slate-900 outline-none transition focus:border-[#2463eb] focus:bg-white focus:ring-2 focus:ring-[#2463eb]/20" />
        <p class="text-xs text-slate-400">Để trống nếu không muốn thay đổi mật khẩu.</p>
      </div>
      <div class="space-y-2">
        <label class="block text-sm font-semibold text-slate-700">Điện thoại</label>
        <input v-model="formData.so_dien_thoai" type="tel" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-base text-slate-900 outline-none transition focus:border-[#2463eb] focus:bg-white focus:ring-2 focus:ring-[#2463eb]/20" />
      </div>
      <div class="space-y-2">
        <label class="block text-sm font-semibold text-slate-700">Ngày sinh</label>
        <input v-model="formData.ngay_sinh" type="date" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-base text-slate-900 outline-none transition focus:border-[#2463eb] focus:bg-white focus:ring-2 focus:ring-[#2463eb]/20" />
      </div>
      <div class="space-y-2">
        <label class="block text-sm font-semibold text-slate-700">Giới tính</label>
        <select v-model="formData.gioi_tinh" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-base text-slate-900 outline-none transition focus:border-[#2463eb] focus:bg-white focus:ring-2 focus:ring-[#2463eb]/20">
          <option value="">-- Chọn --</option>
          <option value="nam">Nam</option>
          <option value="nu">Nữ</option>
          <option value="khac">Khác</option>
        </select>
      </div>
      <div class="space-y-2 lg:col-span-2">
        <label class="block text-sm font-semibold text-slate-700">Địa chỉ</label>
        <input v-model="formData.dia_chi" type="text" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-base text-slate-900 outline-none transition focus:border-[#2463eb] focus:bg-white focus:ring-2 focus:ring-[#2463eb]/20" />
      </div>
      <div class="space-y-2">
        <label class="block text-sm font-semibold text-slate-700">Vai trò</label>
        <select v-model.number="formData.vai_tro" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-base text-slate-900 outline-none transition focus:border-[#2463eb] focus:bg-white focus:ring-2 focus:ring-[#2463eb]/20">
          <option value="0">Ứng viên</option>
          <option value="1">Nhà tuyển dụng</option>
          <option value="2">Admin</option>
        </select>
      </div>
      <div class="space-y-2">
        <label class="block text-sm font-semibold text-slate-700">Trạng thái</label>
        <select v-model.number="formData.trang_thai" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-base text-slate-900 outline-none transition focus:border-[#2463eb] focus:bg-white focus:ring-2 focus:ring-[#2463eb]/20">
          <option :value="1">Hoạt động</option>
          <option :value="0">Khóa</option>
        </select>
      </div>
    </div>
  </FormModalShell>

  <!-- Modal: Xác nhận xóa -->
  <div v-if="showDeleteModal" class="fixed inset-0 bg-black/50 dark:bg-black/70 flex items-center justify-center z-50">
    <div class="bg-white dark:bg-slate-900 rounded-xl shadow-xl max-w-sm w-full mx-4">
      <div class="p-6">
        <div class="flex items-center gap-3 mb-4">
          <span class="material-symbols-outlined text-2xl text-red-600">warning</span>
          <h3 class="text-lg font-semibold">Xóa người dùng</h3>
        </div>
        <p class="text-slate-600 dark:text-slate-400 mb-6">
          Bạn có chắc muốn xóa <strong>{{ deletingUser?.ho_ten }}</strong>? Hành động này không thể hoàn tác.
        </p>
        <div class="flex gap-3">
          <button @click="showDeleteModal = false" class="flex-1 px-4 py-2 border border-slate-300 dark:border-slate-700 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
            Hủy
          </button>
          <button @click="deleteUser" class="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium">
            Xóa
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
