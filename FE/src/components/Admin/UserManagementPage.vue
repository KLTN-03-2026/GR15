<template>
  <AlertMessage
    :message="toast.message"
    :type="toast.type"
    @close="clearToast"
  />

  <!-- Error Alert -->
  <div v-if="error" class="mb-6 flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-4 dark:border-red-900 dark:bg-red-900/20">
    <span class="material-symbols-outlined mt-1 flex-shrink-0 text-red-600">error</span>
    <div class="flex-1 break-words whitespace-pre-wrap text-sm text-red-700 dark:text-red-400">{{ error }}</div>
    <button @click="error = null" class="mt-1 flex-shrink-0 text-red-600 hover:text-red-700">
      <span class="material-symbols-outlined">close</span>
    </button>
  </div>

    <!-- Page Header -->
  <div class="mb-8 flex flex-wrap items-center justify-between gap-4">
    <div class="flex flex-col gap-1">
      <h1 class="text-3xl font-black leading-tight tracking-tight">Quản Lý Người Dùng</h1>
      <p class="text-base text-slate-500 dark:text-slate-400">Quản lý danh sách người dùng và tình trạng tài khoản.</p>
    </div>
  </div>

  <!-- Stats Grid -->
  <div class="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="mb-2 flex items-center justify-between">
        <span class="text-sm font-medium text-slate-500">Tổng người dùng</span>
        <span class="material-symbols-outlined text-[#2463eb]/40">groups</span>
      </div>
      <div class="text-2xl font-bold">{{ stats.total }}</div>
      <div class="mt-2 flex items-center text-xs font-medium text-emerald-600">
        <span class="material-symbols-outlined mr-1 text-xs">check_circle</span> Tất cả chủ động quản lý
      </div>
    </div>
    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="mb-2 flex items-center justify-between">
        <span class="text-sm font-medium text-slate-500">Ứng viên</span>
        <span class="material-symbols-outlined text-[#2463eb]/40">person_search</span>
      </div>
      <div class="text-2xl font-bold">{{ stats.jobSeekers }}</div>
      <div class="mt-2 flex items-center text-xs font-medium text-emerald-600">
        <span class="material-symbols-outlined mr-1 text-xs">trending_up</span> Hoạt động
      </div>
    </div>
    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="mb-2 flex items-center justify-between">
        <span class="text-sm font-medium text-slate-500">Nhà tuyển dụng</span>
        <span class="material-symbols-outlined text-[#2463eb]/40">business</span>
      </div>
      <div class="text-2xl font-bold">{{ stats.employers }}</div>
      <div class="mt-2 flex items-center text-xs font-medium text-emerald-600">
        <span class="material-symbols-outlined mr-1 text-xs">trending_up</span> Hoạt động
      </div>
    </div>
    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="mb-2 flex items-center justify-between">
        <span class="text-sm font-medium text-slate-500">Bị khóa</span>
        <span class="material-symbols-outlined text-red-500/40">block</span>
      </div>
      <div class="text-2xl font-bold">{{ stats.lockedUsers }}</div>
      <div class="mt-2 flex items-center text-xs font-medium text-red-500">
        <span class="material-symbols-outlined mr-1 text-xs">block</span> Tài khoản đang bị khóa
      </div>
    </div>
  </div>

  <!-- Filters -->
  <div class="mb-6 flex flex-wrap items-center gap-4 rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
    <div class="relative min-w-[300px] flex-1">
      <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">search</span>
      <input
        v-model="searchQuery"
        @input="onSearch"
        class="w-full rounded-lg border-none bg-slate-50 py-2 pl-10 pr-4 text-sm focus:ring-2 focus:ring-[#2463eb] dark:bg-slate-800"
        placeholder="Tìm theo tên, email hoặc công ty..."
        type="text"
      />
    </div>
    <div class="flex items-center gap-3">
      <select
        v-model="selectedRole"
        @change="onFilterChange"
        class="rounded-lg border-none bg-slate-50 px-4 py-2 text-sm focus:ring-2 focus:ring-[#2463eb] dark:bg-slate-800"
      >
        <option value="">Tất cả vai trò</option>
        <option value="0">Ứng viên</option>
        <option value="1">Nhà tuyển dụng</option>
        <option value="2">Admin</option>
      </select>
      <select
        v-model="selectedStatus"
        @change="onFilterChange"
        class="rounded-lg border-none bg-slate-50 px-4 py-2 text-sm focus:ring-2 focus:ring-[#2463eb] dark:bg-slate-800"
      >
        <option value="">Tất cả trạng thái</option>
        <option value="active">Hoạt động</option>
        <option value="inactive">Khóa</option>
      </select>
    </div>
    <button
      @click="openNewUserModal"
      class="flex items-center gap-2 rounded-lg bg-[#2463eb] px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-[#2463eb]/90"
    >
      <span class="material-symbols-outlined">add</span> Tạo mới
    </button>
  </div>

  <!-- User Table -->
  <div class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
    <div class="overflow-x-auto">
      <table class="w-full border-collapse text-left">
        <thead>
          <tr class="border-b border-slate-200 bg-slate-50/50 dark:border-slate-800 dark:bg-slate-800/50">
            <th class="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">Thông tin người dùng</th>
            <th class="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">Vai trò</th>
            <th class="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">Ngày tham gia</th>
            <th class="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">Trạng thái</th>
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
          <template v-else-if="users.length === 0">
            <tr>
              <td colspan="5" class="px-6 py-8 text-center text-slate-500">
                <span class="material-symbols-outlined mb-2 text-3xl">inbox</span>
                <div>Không tìm thấy người dùng</div>
              </td>
            </tr>
          </template>
          <template v-else>
            <tr v-for="user in users" :key="user.id" class="transition-colors hover:bg-slate-50/50 dark:hover:bg-slate-800/50">
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                  <div class="flex h-10 w-10 items-center justify-center rounded-full bg-[#2463eb]/10 font-bold text-[#2463eb]">
                    {{ user.ho_ten?.charAt(0).toUpperCase() || 'U' }}
                  </div>
                  <div>
                    <div class="text-sm font-semibold">{{ user.ho_ten }}</div>
                    <div class="text-xs text-slate-500">{{ user.email }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4">
                <span :class="['rounded px-2 py-1 text-xs font-medium', roleColors[user.vai_tro] || defaultRoleColor]">
                  {{ roleMap[user.vai_tro] || user.vai_tro || 'N/A' }}
                </span>
              </td>
              <td class="px-6 py-4 text-sm text-slate-600 dark:text-slate-400">
                {{ user.created_at ? new Date(user.created_at).toLocaleDateString('vi-VN') : 'N/A' }}
              </td>
              <td class="px-6 py-4">
                <div class="flex items-center gap-2">
                  <div :class="['h-2 w-2 rounded-full', user.trang_thai === 1 ? 'bg-emerald-500' : 'bg-red-500']"></div>
                  <span :class="['text-sm font-medium', user.trang_thai === 1 ? 'text-emerald-600' : 'text-red-600']">
                    {{ user.trang_thai === 1 ? 'Hoạt động' : 'Đã khóa' }}
                  </span>
                </div>
              </td>
              <td class="px-6 py-4 text-right">
                <div class="flex items-center justify-center gap-2">
                  <button
                    @click="openEditUserModal(user)"
                    :disabled="actionLoadingId === user.id"
                    class="rounded-lg p-2 text-slate-400 transition-colors hover:text-[#2463eb] disabled:cursor-not-allowed disabled:opacity-50"
                    title="Chỉnh sửa"
                  >
                    <span class="material-symbols-outlined text-xl">edit</span>
                  </button>
                  <button
                    @click="toggleLock(user.id)"
                    :disabled="actionLoadingId === user.id"
                    :class="['rounded-lg p-2 transition-colors', user.trang_thai === 1 ? 'text-slate-400 hover:text-amber-600' : 'text-slate-400 hover:text-green-600']"
                    :title="user.trang_thai === 1 ? 'Khóa' : 'Mở khóa'"
                  >
                    <span class="material-symbols-outlined text-xl">{{ actionLoadingId === user.id ? 'progress_activity' : user.trang_thai === 1 ? 'block' : 'lock_open' }}</span>
                  </button>
                  <button
                    @click="confirmDelete(user)"
                    :disabled="actionLoadingId === user.id"
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
      v-if="!loading && users.length > 0"
      class="flex items-center justify-between border-t border-slate-200 bg-slate-50/50 px-6 py-4 dark:border-slate-800 dark:bg-slate-800/50"
    >
      <div class="text-sm text-slate-500">
        Hiển thị <span class="font-medium text-slate-900 dark:text-slate-100">{{ (currentPage - 1) * perPage + 1 }}</span>
        đến <span class="font-medium text-slate-900 dark:text-slate-100">{{ Math.min(currentPage * perPage, totalUsers) }}</span>
        trên <span class="font-medium text-slate-900 dark:text-slate-100">{{ totalUsers }}</span> người dùng
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

  <!-- Modal: Tạo/Sửa người dùng -->
  <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-black/50 p-4 dark:bg-black/70">
    <div class="my-auto flex max-h-[calc(100vh-2rem)] w-full max-w-md flex-col overflow-hidden rounded-xl bg-white shadow-xl dark:bg-slate-900">
      <div class="flex items-center justify-between border-b border-slate-200 px-6 py-4 dark:border-slate-800">
        <h3 class="text-lg font-semibold">{{ editingUser ? 'Chỉnh sửa người dùng' : 'Tạo người dùng mới' }}</h3>
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
          <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Họ tên</label>
          <input v-model="formData.ho_ten" type="text" required class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800" />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Email</label>
          <input v-model="formData.email" type="email" :required="!editingUser" class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800" />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Điện thoại</label>
          <input v-model="formData.so_dien_thoai" type="tel" class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800" />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Ngày sinh</label>
          <input v-model="formData.ngay_sinh" type="date" class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800" />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Giới tính</label>
          <select v-model="formData.gioi_tinh" class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800">
            <option value="">-- Chọn --</option>
            <option value="nam">Nam</option>
            <option value="nu">Nữ</option>
            <option value="khac">Khác</option>
          </select>
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Địa chỉ</label>
          <input v-model="formData.dia_chi" type="text" class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800" />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Vai trò</label>
          <select v-model.number="formData.vai_tro" class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800">
            <option value="0">Ứng viên</option>
            <option value="1">Nhà tuyển dụng</option>
            <option value="2">Admin</option>
          </select>
        </div>
        <div v-if="!editingUser">
          <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Mật khẩu</label>
          <input v-model="formData.mat_khau" type="password" required minlength="8" class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800" />
        </div>
        <div v-if="!editingUser">
          <label class="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Xác nhận mật khẩu</label>
          <input v-model="formData.mat_khau_confirmation" type="password" required minlength="8" class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-[#2463eb] dark:border-slate-700 dark:bg-slate-800" />
        </div>
        </div>
        <div class="flex gap-3 border-t border-slate-200 px-6 py-4 dark:border-slate-800">
          <button type="button" @click="closeModal" :disabled="submitting" class="flex-1 rounded-lg border border-slate-300 px-4 py-2 transition-colors hover:bg-slate-50 disabled:opacity-60 dark:border-slate-700 dark:hover:bg-slate-800">
            Hủy
          </button>
          <button type="submit" :disabled="submitting" class="flex-1 rounded-lg bg-[#2463eb] px-4 py-2 font-medium text-white transition-colors hover:bg-[#2463eb]/90 disabled:opacity-60">
            {{ submitting ? 'Đang xử lý...' : editingUser ? 'Cập nhật' : 'Tạo' }}
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
          <h3 class="text-lg font-semibold">Xóa người dùng</h3>
        </div>
        <p class="mb-6 text-slate-600 dark:text-slate-400">
          Bạn có chắc muốn xóa <strong>{{ deletingUser?.ho_ten }}</strong>? Hành động này không thể hoàn tác.
        </p>
        <div class="flex gap-3">
          <button @click="closeDeleteModal" :disabled="actionLoadingId === deletingUser?.id" class="flex-1 rounded-lg border border-slate-300 px-4 py-2 transition-colors hover:bg-slate-50 disabled:opacity-60 dark:border-slate-700 dark:hover:bg-slate-800">
            Hủy
          </button>
          <button @click="deleteUser" :disabled="actionLoadingId === deletingUser?.id" class="flex-1 rounded-lg bg-red-600 px-4 py-2 font-medium text-white transition-colors hover:bg-red-700 disabled:opacity-60">
            {{ actionLoadingId === deletingUser?.id ? 'Đang xóa...' : 'Xóa' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import AlertMessage from '@/components/AlertMessage.vue'
import { userService } from '@/services/api'

const users = ref([])
const loading = ref(false)
const error = ref(null)
const currentPage = ref(1)
const totalUsers = ref(0)
const perPage = ref(5)

const searchQuery = ref('')
const selectedRole = ref('')
const selectedStatus = ref('')

const stats = reactive({
  total: 0,
  jobSeekers: 0,
  employers: 0,
  lockedUsers: 0
})

const showModal = ref(false)
const showDeleteModal = ref(false)
const editingUser = ref(null)
const deletingUser = ref(null)
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
  ho_ten: '',
  email: '',
  so_dien_thoai: '',
  ngay_sinh: '',
  gioi_tinh: '',
  dia_chi: '',
  vai_tro: 0,
  mat_khau: '',
  mat_khau_confirmation: ''
})

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

const defaultRoleColor = 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300'

const totalPages = computed(() => Math.ceil(totalUsers.value / perPage.value))

const normalizeSearchText = (value) => {
  return String(value || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .trim()
}

const normalizeDateForInput = (value) => {
  if (!value) {
    return ''
  }

  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    return value
  }

  const parsedDate = new Date(value)
  if (Number.isNaN(parsedDate.getTime())) {
    return ''
  }

  const year = parsedDate.getFullYear()
  const month = String(parsedDate.getMonth() + 1).padStart(2, '0')
  const day = String(parsedDate.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const normalizeUserListResponse = (response) => {
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

  if (Array.isArray(response?.nguoi_dungs)) {
    return {
      items: response.nguoi_dungs,
      total: response.total ?? response.meta?.total ?? response.nguoi_dungs.length
    }
  }

  if (Array.isArray(response?.data?.nguoi_dungs)) {
    return {
      items: response.data.nguoi_dungs,
      total: response.data.total ?? response.data.meta?.total ?? response.data.nguoi_dungs.length
    }
  }

  return { items: [], total: 0 }
}

const normalizeUserStatsResponse = (response) => {
  const source = response?.data ?? response ?? {}

  return {
    total: source.total ?? source.tong_nguoi_dung ?? source.tong ?? 0,
    jobSeekers: source.jobSeekers ?? source.ung_vien ?? source.candidate ?? 0,
    employers: source.employers ?? source.nha_tuyen_dung ?? source.employer ?? 0,
    lockedUsers: source.lockedUsers ?? source.bi_khoa ?? source.locked ?? 0
  }
}

const calculateStatsFromList = (items) => ({
  total: totalUsers.value || items.length,
  jobSeekers: items.filter((user) => user.vai_tro === 0).length,
  employers: items.filter((user) => user.vai_tro === 1).length,
  lockedUsers: items.filter((user) => user.trang_thai === 0).length
})

const applyStats = (nextStats) => {
  stats.total = nextStats.total
  stats.jobSeekers = nextStats.jobSeekers
  stats.employers = nextStats.employers
  stats.lockedUsers = nextStats.lockedUsers
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

const loadUsers = async () => {
  loading.value = true
  error.value = null

  try {
    const keyword = searchQuery.value.trim()
    const response = await userService.getUsers({
      page: currentPage.value,
      per_page: perPage.value,
      vai_tro: selectedRole.value ? Number.parseInt(selectedRole.value, 10) : undefined,
      trang_thai: selectedStatus.value ? (selectedStatus.value === 'active' ? 1 : 0) : undefined,
      search: keyword || undefined
    })

    const { items, total } = normalizeUserListResponse(response)
    const normalizedKeyword = normalizeSearchText(keyword)
    const filteredItems = normalizedKeyword
      ? items.filter((user) => normalizeSearchText(user.ho_ten).includes(normalizedKeyword))
      : items

    users.value = filteredItems
    totalUsers.value = normalizedKeyword ? filteredItems.length : total

    try {
      const statsResponse = await userService.getUserStats()
      applyStats(normalizeUserStatsResponse(statsResponse))
    } catch {
      applyStats(calculateStatsFromList(items))
    }
  } catch (err) {
    error.value = err.message || 'Không thể tải danh sách người dùng'
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  formData.ho_ten = ''
  formData.email = ''
  formData.so_dien_thoai = ''
  formData.ngay_sinh = ''
  formData.gioi_tinh = ''
  formData.dia_chi = ''
  formData.vai_tro = 0
  formData.mat_khau = ''
  formData.mat_khau_confirmation = ''
  modalError.value = ''
}

const closeModal = (force = false) => {
  if (submitting.value && !force) {
    return
  }

  showModal.value = false
  editingUser.value = null
  modalError.value = ''
}

const closeDeleteModal = (force = false) => {
  if (actionLoadingId.value === deletingUser.value?.id && !force) {
    return
  }

  showDeleteModal.value = false
  deletingUser.value = null
}

const openNewUserModal = () => {
  editingUser.value = null
  resetForm()
  showModal.value = true
}

const openEditUserModal = async (user) => {
  modalError.value = ''
  error.value = null
  actionLoadingId.value = user.id

  try {
    const response = await userService.getUserById(user.id)
    const detail = response?.data ?? response ?? user

    editingUser.value = detail.id ?? user.id
    formData.ho_ten = detail.ho_ten ?? user.ho_ten ?? ''
    formData.email = detail.email ?? user.email ?? ''
    formData.so_dien_thoai = detail.so_dien_thoai ?? user.so_dien_thoai ?? ''
    formData.ngay_sinh = normalizeDateForInput(detail.ngay_sinh ?? user.ngay_sinh ?? '')
    formData.gioi_tinh = detail.gioi_tinh ?? user.gioi_tinh ?? ''
    formData.dia_chi = detail.dia_chi ?? user.dia_chi ?? ''
    formData.vai_tro = Number(detail.vai_tro ?? user.vai_tro ?? 0)
    formData.mat_khau = ''
    formData.mat_khau_confirmation = ''
    showModal.value = true
  } catch (err) {
    error.value = err.message || 'Không thể tải chi tiết người dùng'
  } finally {
    actionLoadingId.value = null
  }
}

const submitForm = async () => {
  modalError.value = ''

  if (!editingUser.value && formData.mat_khau !== formData.mat_khau_confirmation) {
    modalError.value = 'Xác nhận mật khẩu không khớp.'
    return
  }

  submitting.value = true

  try {
    if (editingUser.value) {
      const updatePayload = {
        ho_ten: formData.ho_ten,
        email: formData.email,
        so_dien_thoai: formData.so_dien_thoai,
        ngay_sinh: formData.ngay_sinh,
        gioi_tinh: formData.gioi_tinh,
        dia_chi: formData.dia_chi,
        vai_tro: formData.vai_tro
      }

      await userService.updateUser(editingUser.value, updatePayload)
      showToast('Cập nhật người dùng thành công.')
    } else {
      const createPayload = {
        ho_ten: formData.ho_ten,
        email: formData.email,
        so_dien_thoai: formData.so_dien_thoai,
        ngay_sinh: formData.ngay_sinh,
        gioi_tinh: formData.gioi_tinh,
        dia_chi: formData.dia_chi,
        vai_tro: formData.vai_tro,
        mat_khau: formData.mat_khau,
        mat_khau_confirmation: formData.mat_khau_confirmation
      }

      await userService.createUser(createPayload)
      showToast('Tạo người dùng thành công.')
    }

    closeModal(true)
    await loadUsers()
  } catch (err) {
    const validationErrors = err?.data?.errors
    modalError.value = validationErrors
      ? Object.values(validationErrors).flat().join('\n')
      : err.message || 'Lỗi lưu người dùng'
  } finally {
    submitting.value = false
  }
}

const confirmDelete = (user) => {
  error.value = null
  deletingUser.value = user
  showDeleteModal.value = true
}

const deleteUser = async () => {
  if (!deletingUser.value) {
    return
  }

  try {
    actionLoadingId.value = deletingUser.value.id
    await userService.deleteUser(deletingUser.value.id)
    showToast('Xóa người dùng thành công.')
    closeDeleteModal(true)
    await loadUsers()
  } catch (err) {
    error.value = err.message || 'Lỗi xóa người dùng'
  } finally {
    actionLoadingId.value = null
  }
}

const toggleLock = async (userId) => {
  try {
    error.value = null
    actionLoadingId.value = userId
    const targetUser = users.value.find((user) => user.id === userId)
    const nextActionLabel = Number(targetUser?.trang_thai) === 1 ? 'Khóa' : 'Mở khóa'
    await userService.toggleLock(userId)
    showToast(`${nextActionLabel} tài khoản thành công.`)
    await loadUsers()
  } catch (err) {
    error.value = err.message || 'Lỗi khoá/mở khoá tài khoản'
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
    loadUsers()
  }, 250)
}

const onFilterChange = () => {
  currentPage.value = 1
  loadUsers()
}

const goToPage = (page) => {
  currentPage.value = page
  loadUsers()
}

const goToPreviousPage = () => {
  if (currentPage.value === 1) {
    return
  }

  currentPage.value -= 1
  loadUsers()
}

const goToNextPage = () => {
  if (currentPage.value >= totalPages.value) {
    return
  }

  currentPage.value += 1
  loadUsers()
}

onMounted(() => {
  loadUsers()
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
