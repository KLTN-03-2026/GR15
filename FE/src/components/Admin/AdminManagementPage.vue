<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { adminAccountService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'
import { getStoredUser } from '@/utils/authStorage'
import FormModalShell from '@/components/FormModalShell.vue'
import AdminPaginationBar from '@/components/Admin/AdminPaginationBar.vue'
import {
  ADMIN_PERMISSION_DEFINITIONS,
  normalizeAdminPermissions,
} from '@/constants/adminPermissions'

const notify = useNotify()

const admins = ref([])
const loading = ref(false)
const error = ref(null)
const currentPage = ref(1)
const totalAdmins = ref(0)
const perPage = ref(10)
const searchQuery = ref('')
const selectedStatus = ref('')
const stats = reactive({
  tong_admin: 0,
  tong_super_admin: 0,
  tong_admin_thuong: 0,
  dang_hoat_dong: 0,
  bi_khoa: 0,
  tao_trong_30_ngay: 0,
})
const currentUser = ref(getStoredUser())

const activeTab = ref('accounts')
const permissionCatalog = ref([...ADMIN_PERMISSION_DEFINITIONS])
const permissionLoading = ref(false)
const permissionSaving = ref(false)
const permissionDefinitionSaving = ref(false)
const showPermissionDefinitionModal = ref(false)
const selectedPermissionAdminId = ref(null)
const permissionForm = ref(normalizeAdminPermissions())
const permissionSnapshot = ref(JSON.stringify(normalizeAdminPermissions()))
const permissionDefinitionForm = reactive({
  label: '',
  description: '',
  mapped_permission_key: 'users',
})

const showModal = ref(false)
const showDeleteModal = ref(false)
const editingAdminId = ref(null)
const deletingAdmin = ref(null)
const saving = ref(false)
const listSectionRef = ref(null)
let searchDebounceTimer = null

const formData = reactive({
  ho_ten: '',
  email: '',
  mat_khau: '',
  so_dien_thoai: '',
  ngay_sinh: '',
  gioi_tinh: '',
  dia_chi: '',
  trang_thai: 1,
})

const capAdminColors = {
  super_admin: 'border border-amber-200 bg-amber-50 text-amber-700',
  admin: 'border border-blue-200 bg-blue-50 text-blue-700',
}

const statusColors = {
  1: 'border border-emerald-200 bg-emerald-50 text-emerald-700',
  0: 'border border-rose-200 bg-rose-50 text-rose-700',
}

const totalPages = computed(() => Math.max(1, Math.ceil(totalAdmins.value / perPage.value)))
const isEditing = computed(() => editingAdminId.value !== null)
const regularAdmins = computed(() => admins.value.filter((admin) => !admin.la_super_admin))
const selectedPermissionAdmin = computed(() =>
  regularAdmins.value.find((admin) => Number(admin.id) === Number(selectedPermissionAdminId.value)) || null,
)
const grantedPermissionCount = computed(() => Object.values(permissionForm.value || {}).filter(Boolean).length)
const systemPermissionOptions = computed(() =>
  permissionCatalog.value.filter((permission) => !permission.is_custom && !permission.mapped_permission_key),
)
const permissionSummaryText = computed(() => {
  const total = permissionCatalog.value.length || Object.keys(permissionForm.value).length
  return `${grantedPermissionCount.value}/${total} chức năng đang được cấp`
})
const permissionDirty = computed(() => JSON.stringify(permissionForm.value) !== permissionSnapshot.value)

const syncCurrentUser = () => {
  currentUser.value = getStoredUser()
}

const canMutateAdmin = (admin) => {
  if (!admin) return false
  if (admin.la_super_admin) return false
  return Number(admin.id) !== Number(currentUser.value?.id)
}

const getAdminTypeLabel = (admin) => admin?.ten_cap_admin || (admin?.cap_admin === 'super_admin' ? 'Super Admin' : 'Admin')

const resetForm = () => {
  formData.ho_ten = ''
  formData.email = ''
  formData.mat_khau = ''
  formData.so_dien_thoai = ''
  formData.ngay_sinh = ''
  formData.gioi_tinh = ''
  formData.dia_chi = ''
  formData.trang_thai = 1
}

const mergeAdminRecord = (adminPayload) => {
  if (!adminPayload?.id) return

  const adminId = Number(adminPayload.id)
  const nextAdmins = admins.value.map((admin) =>
    Number(admin.id) === adminId ? { ...admin, ...adminPayload } : admin,
  )

  admins.value = nextAdmins
}

const ensurePermissionSelection = () => {
  if (!regularAdmins.value.length) {
    selectedPermissionAdminId.value = null
    permissionForm.value = normalizeAdminPermissions()
    permissionSnapshot.value = JSON.stringify(permissionForm.value)
    return
  }

  const hasSelected = regularAdmins.value.some((admin) => Number(admin.id) === Number(selectedPermissionAdminId.value))
  if (!hasSelected) {
    selectedPermissionAdminId.value = regularAdmins.value[0].id
  }
}

const applyPermissionPayload = (payload) => {
  const catalog = Array.isArray(payload?.catalog) && payload.catalog.length ? payload.catalog : ADMIN_PERMISSION_DEFINITIONS
  const submittedPermissions = payload?.quyen_admin || payload?.admin?.quyen_admin || {}
  const permissions = Object.fromEntries(catalog.map((permission) => [
    permission.key,
    Object.prototype.hasOwnProperty.call(submittedPermissions || {}, permission.key)
      ? Boolean(submittedPermissions[permission.key])
      : false,
  ]))

  permissionCatalog.value = catalog
  permissionForm.value = permissions
  permissionSnapshot.value = JSON.stringify(permissions)

  if (payload?.admin) {
    mergeAdminRecord(payload.admin)
  }
}

const normalizeListResponse = (response) => {
  const payload = response?.data || {}

  if (Array.isArray(payload.data)) {
    admins.value = payload.data
    totalAdmins.value = payload.total || payload.data.length
    return
  }

  admins.value = Array.isArray(payload) ? payload : []
  totalAdmins.value = payload.total || admins.value.length
}

const loadStats = async () => {
  try {
    const response = await adminAccountService.getAdminStats()
    Object.assign(stats, response?.data || {})
  } catch (err) {
    console.error('Không thể tải thống kê admin', err)
  }
}

const loadPermissionSettings = async (adminId = selectedPermissionAdminId.value) => {
  if (!adminId) return

  permissionLoading.value = true

  try {
    const response = await adminAccountService.getAdminPermissions(adminId)
    applyPermissionPayload(response?.data || {})
  } catch (err) {
    error.value = err.message || 'Không thể tải quyền chức năng của admin'
  } finally {
    permissionLoading.value = false
  }
}

const loadAdmins = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await adminAccountService.getAdmins({
      page: currentPage.value,
      per_page: perPage.value,
      trang_thai: selectedStatus.value === '' ? undefined : Number(selectedStatus.value),
      search: searchQuery.value.trim() || undefined,
    })

    normalizeListResponse(response)
    ensurePermissionSelection()

    if (activeTab.value === 'permissions' && selectedPermissionAdminId.value) {
      await loadPermissionSettings(selectedPermissionAdminId.value)
    }
  } catch (err) {
    error.value = err.message || 'Không thể tải danh sách admin'
  } finally {
    loading.value = false
  }
}

const scrollToListTop = async () => {
  await nextTick()
  listSectionRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const switchTab = async (tab) => {
  activeTab.value = tab

  if (tab === 'permissions') {
    ensurePermissionSelection()

    if (selectedPermissionAdminId.value) {
      await loadPermissionSettings(selectedPermissionAdminId.value)
    }
  }
}

const openCreateModal = () => {
  editingAdminId.value = null
  resetForm()
  showModal.value = true
}

const openEditModal = (admin) => {
  if (!canMutateAdmin(admin)) return

  editingAdminId.value = admin.id
  formData.ho_ten = admin.ho_ten || ''
  formData.email = admin.email || ''
  formData.mat_khau = ''
  formData.so_dien_thoai = admin.so_dien_thoai || ''
  formData.ngay_sinh = admin.ngay_sinh || ''
  formData.gioi_tinh = admin.gioi_tinh || ''
  formData.dia_chi = admin.dia_chi || ''
  formData.trang_thai = admin.trang_thai ?? 1
  showModal.value = true
}

const openPermissionTab = async (admin) => {
  if (!canMutateAdmin(admin)) return

  selectedPermissionAdminId.value = admin.id
  activeTab.value = 'permissions'
  await loadPermissionSettings(admin.id)
}

const closeModal = () => {
  if (saving.value) return
  showModal.value = false
  editingAdminId.value = null
}

const submitForm = async () => {
  saving.value = true
  error.value = null

  try {
    const payload = {
      ho_ten: formData.ho_ten,
      email: formData.email,
      so_dien_thoai: formData.so_dien_thoai || null,
      ngay_sinh: formData.ngay_sinh || null,
      gioi_tinh: formData.gioi_tinh || null,
      dia_chi: formData.dia_chi || null,
      trang_thai: Number(formData.trang_thai),
    }

    if (formData.mat_khau) {
      payload.mat_khau = formData.mat_khau
    }

    if (isEditing.value) {
      await adminAccountService.updateAdmin(editingAdminId.value, payload)
      notify.success('Đã cập nhật tài khoản admin.')
    } else {
      if (!payload.mat_khau) {
        throw { message: 'Vui lòng nhập mật khẩu cho tài khoản admin mới.' }
      }

      await adminAccountService.createAdmin(payload)
      notify.success('Đã tạo tài khoản admin thường.')
    }

    closeModal()
    await Promise.all([loadAdmins(), loadStats()])
  } catch (err) {
    error.value = err.message || 'Không thể lưu tài khoản admin'
  } finally {
    saving.value = false
  }
}

const savePermissions = async () => {
  if (!selectedPermissionAdminId.value) return

  permissionSaving.value = true
  error.value = null

  try {
    const response = await adminAccountService.updateAdminPermissions(
      selectedPermissionAdminId.value,
      permissionForm.value,
    )

    applyPermissionPayload(response?.data || {})
    await loadAdmins()
    notify.success('Đã cập nhật quyền chức năng cho admin.')
  } catch (err) {
    error.value = err.message || 'Không thể cập nhật quyền chức năng'
  } finally {
    permissionSaving.value = false
  }
}

const openPermissionDefinitionModal = () => {
  permissionDefinitionForm.label = ''
  permissionDefinitionForm.description = ''
  permissionDefinitionForm.mapped_permission_key = systemPermissionOptions.value[0]?.key || 'users'
  showPermissionDefinitionModal.value = true
}

const closePermissionDefinitionModal = () => {
  if (permissionDefinitionSaving.value) return
  showPermissionDefinitionModal.value = false
}

const createPermissionDefinition = async () => {
  const payload = {
    label: permissionDefinitionForm.label.trim(),
    description: permissionDefinitionForm.description.trim(),
    mapped_permission_key: permissionDefinitionForm.mapped_permission_key,
  }

  if (!payload.label) {
    notify.warning('Vui lòng nhập tên chức năng.')
    return
  }

  if (!payload.mapped_permission_key) {
    notify.warning('Vui lòng chọn chức năng hệ thống để gắn quyền mới.')
    return
  }

  permissionDefinitionSaving.value = true
  error.value = null

  try {
    const response = await adminAccountService.createAdminPermissionDefinition(payload)
    const catalog = response?.data?.catalog || permissionCatalog.value
    permissionCatalog.value = catalog
    permissionForm.value = Object.fromEntries(catalog.map((permission) => [
      permission.key,
      Boolean(permissionForm.value?.[permission.key]),
    ]))
    permissionSnapshot.value = JSON.stringify(permissionForm.value)
    showPermissionDefinitionModal.value = false
    notify.success('Đã tạo chức năng admin.')
  } catch (err) {
    error.value = err.message || 'Không thể tạo chức năng admin'
    notify.apiError(err, 'Không thể tạo chức năng admin.')
  } finally {
    permissionDefinitionSaving.value = false
  }
}

const selectAllPermissions = () => {
  permissionForm.value = Object.fromEntries(permissionCatalog.value.map((item) => [item.key, true]))
}

const clearAllPermissions = () => {
  permissionForm.value = Object.fromEntries(permissionCatalog.value.map((item) => [item.key, false]))
}

const confirmDelete = (admin) => {
  if (!canMutateAdmin(admin)) return
  deletingAdmin.value = admin
  showDeleteModal.value = true
}

const deleteAdmin = async () => {
  if (!deletingAdmin.value) return

  try {
    await adminAccountService.deleteAdmin(deletingAdmin.value.id)
    notify.success('Đã xóa tài khoản admin.')
    showDeleteModal.value = false
    deletingAdmin.value = null
    await Promise.all([loadAdmins(), loadStats()])
  } catch (err) {
    error.value = err.message || 'Không thể xóa tài khoản admin'
  }
}

const toggleLock = async (admin) => {
  if (!canMutateAdmin(admin)) return

  try {
    await adminAccountService.toggleAdminLock(admin.id)
    notify.success('Đã cập nhật trạng thái tài khoản admin.')
    await Promise.all([loadAdmins(), loadStats()])
  } catch (err) {
    error.value = err.message || 'Không thể cập nhật trạng thái admin'
  }
}

const onSearch = () => {
  currentPage.value = 1

  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer)
  }

  searchDebounceTimer = window.setTimeout(() => {
    loadAdmins()
  }, 250)
}

const onFilterChange = () => {
  currentPage.value = 1
  loadAdmins()
}

const resetFilters = () => {
  searchQuery.value = ''
  selectedStatus.value = ''
  perPage.value = 10
  currentPage.value = 1
  loadAdmins()
}

const goToPreviousPage = () => {
  if (currentPage.value === 1) return
  currentPage.value -= 1
  loadAdmins()
  scrollToListTop()
}

const goToNextPage = () => {
  if (currentPage.value === totalPages.value) return
  currentPage.value += 1
  loadAdmins()
  scrollToListTop()
}

onMounted(async () => {
  syncCurrentUser()
  await Promise.all([loadAdmins(), loadStats()])
  window.addEventListener('auth-changed', syncCurrentUser)
  window.addEventListener('admin-profile-updated', syncCurrentUser)
})

onBeforeUnmount(() => {
  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer)
  }

  window.removeEventListener('auth-changed', syncCurrentUser)
  window.removeEventListener('admin-profile-updated', syncCurrentUser)
})
</script>

<template>
  <div v-if="error" class="mb-6 flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4 dark:border-red-900 dark:bg-red-900/20">
    <span class="material-symbols-outlined mt-1 flex-shrink-0 text-red-600">error</span>
    <div class="flex-1 whitespace-pre-wrap break-words text-sm text-red-700 dark:text-red-400">{{ error }}</div>
    <button class="mt-1 flex-shrink-0 text-red-600 hover:text-red-700" @click="error = null">
      <span class="material-symbols-outlined">close</span>
    </button>
  </div>

  <div class="mb-8 flex flex-wrap items-center justify-between gap-4">
    <div class="flex flex-col gap-1">
      <h1 class="text-3xl font-black leading-tight tracking-tight">Quản Lý Admin</h1>
      <p class="text-base text-slate-500 dark:text-slate-400">Quản lý duy nhất các tài khoản quản trị viên hệ thống theo mô hình 1 super admin và nhiều admin thường.</p>
    </div>
    <button
      class="inline-flex items-center gap-2 rounded-2xl bg-[#2463eb] px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-[#1d56cf]"
      type="button"
      @click="openCreateModal"
    >
      <span class="material-symbols-outlined text-[18px]">person_add</span>
      Tạo admin thường
    </button>
  </div>

  <div class="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-5">
    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <p class="text-sm font-medium text-slate-500">Tổng admin</p>
      <p class="mt-3 text-2xl font-black text-slate-900 dark:text-white">{{ stats.tong_admin }}</p>
    </div>
    <div class="rounded-xl border border-amber-200 bg-white p-6 shadow-sm dark:border-amber-900/50 dark:bg-slate-900">
      <p class="text-sm font-medium text-slate-500">Super admin</p>
      <p class="mt-3 text-2xl font-black text-amber-600">{{ stats.tong_super_admin }}</p>
    </div>
    <div class="rounded-xl border border-blue-200 bg-white p-6 shadow-sm dark:border-blue-900/50 dark:bg-slate-900">
      <p class="text-sm font-medium text-slate-500">Admin thường</p>
      <p class="mt-3 text-2xl font-black text-[#2463eb]">{{ stats.tong_admin_thuong }}</p>
    </div>
    <div class="rounded-xl border border-emerald-200 bg-white p-6 shadow-sm dark:border-emerald-900/50 dark:bg-slate-900">
      <p class="text-sm font-medium text-slate-500">Đang hoạt động</p>
      <p class="mt-3 text-2xl font-black text-emerald-600">{{ stats.dang_hoat_dong }}</p>
    </div>
    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <p class="text-sm font-medium text-slate-500">Tạo trong 30 ngày</p>
      <p class="mt-3 text-2xl font-black text-slate-900 dark:text-white">{{ stats.tao_trong_30_ngay }}</p>
    </div>
  </div>

  <div class="mb-6 flex flex-wrap gap-3 rounded-2xl border border-slate-200 bg-white p-3 shadow-sm dark:border-slate-800 dark:bg-slate-900">
    <button
      :class="[
        'inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold transition',
        activeTab === 'accounts'
          ? 'bg-[#2463eb] text-white shadow-sm'
          : 'text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800',
      ]"
      type="button"
      @click="switchTab('accounts')"
    >
      <span class="material-symbols-outlined text-[18px]">shield_person</span>
      Tài khoản admin
    </button>
    <button
      :class="[
        'inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold transition',
        activeTab === 'permissions'
          ? 'bg-[#2463eb] text-white shadow-sm'
          : 'text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800',
      ]"
      type="button"
      @click="switchTab('permissions')"
    >
      <span class="material-symbols-outlined text-[18px]">tune</span>
      Chức năng
    </button>
  </div>

  <template v-if="activeTab === 'accounts'">
    <div class="mb-6 flex flex-wrap items-center gap-4 rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="relative min-w-[300px] flex-1">
        <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">search</span>
        <input
          v-model="searchQuery"
          class="w-full rounded-lg bg-slate-50 py-2 pl-10 pr-4 text-sm focus:ring-2 focus:ring-[#2463eb] dark:bg-slate-800"
          placeholder="Tìm theo tên, email hoặc số điện thoại..."
          type="text"
          @input="onSearch"
        />
      </div>
      <div class="flex flex-wrap items-center gap-3">
        <select
          v-model="selectedStatus"
          class="rounded-lg bg-slate-50 px-4 py-2 text-sm focus:ring-2 focus:ring-[#2463eb] dark:bg-slate-800"
          @change="onFilterChange"
        >
          <option value="">Tất cả trạng thái</option>
          <option value="1">Hoạt động</option>
          <option value="0">Khóa</option>
        </select>
        <select
          v-model="perPage"
          class="rounded-lg bg-slate-50 px-4 py-2 text-sm focus:ring-2 focus:ring-[#2463eb] dark:bg-slate-800"
          @change="onFilterChange"
        >
          <option :value="10">10 / trang</option>
          <option :value="20">20 / trang</option>
          <option :value="50">50 / trang</option>
        </select>
        <button
          class="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium transition hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-800"
          type="button"
          @click="resetFilters"
        >
          Reset bộ lọc
        </button>
      </div>
    </div>

    <div ref="listSectionRef" class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="overflow-x-auto">
        <table class="w-full border-collapse text-left">
          <thead>
            <tr class="border-b border-slate-200 bg-slate-50/50 dark:border-slate-800 dark:bg-slate-800/50">
              <th class="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">Tài khoản admin</th>
              <th class="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">Cấp admin</th>
              <th class="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">Chức năng</th>
              <th class="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">Ngày tham gia</th>
              <th class="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">Trạng thái</th>
              <th class="px-6 py-4 text-center text-xs font-semibold uppercase tracking-wider text-slate-500">Hành động</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 dark:divide-slate-800">
            <tr v-if="loading">
              <td colspan="6" class="px-6 py-8 text-center text-slate-500">
                <span class="material-symbols-outlined animate-spin">hourglass_empty</span>
                <div>Đang tải...</div>
              </td>
            </tr>
            <tr v-else-if="admins.length === 0">
              <td colspan="6" class="px-6 py-8 text-center text-slate-500">
                <span class="material-symbols-outlined mb-2 text-3xl">shield_person</span>
                <div>Không tìm thấy tài khoản admin phù hợp</div>
              </td>
            </tr>
            <template v-else>
              <tr v-for="admin in admins" :key="admin.id" class="transition-colors hover:bg-slate-50/50 dark:hover:bg-slate-800/50">
                <td class="px-6 py-4">
                  <div class="flex items-center gap-3">
                    <div class="flex h-10 w-10 items-center justify-center rounded-full bg-[#2463eb]/10 font-bold text-[#2463eb]">
                      {{ admin.ho_ten?.charAt(0).toUpperCase() || 'A' }}
                    </div>
                    <div>
                      <div class="font-semibold text-sm">{{ admin.ho_ten }}</div>
                      <div class="text-xs text-slate-500">{{ admin.email }}</div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <span :class="['inline-flex rounded-full px-3 py-1 text-xs font-semibold', capAdminColors[admin.cap_admin] || capAdminColors.admin]">
                    {{ getAdminTypeLabel(admin) }}
                  </span>
                </td>
                <td class="px-6 py-4 text-sm text-slate-600 dark:text-slate-400">
                  <template v-if="admin.la_super_admin">
                    Toàn quyền hệ thống
                  </template>
                  <template v-else>
                    {{ admin.so_quyen_admin || 0 }}/{{ admin.tong_quyen_admin || permissionCatalog.length }} chức năng
                  </template>
                </td>
                <td class="px-6 py-4 text-sm text-slate-600 dark:text-slate-400">
                  {{ admin.created_at ? new Date(admin.created_at).toLocaleDateString('vi-VN') : 'N/A' }}
                </td>
                <td class="px-6 py-4">
                  <span :class="['inline-flex rounded-full px-3 py-1 text-xs font-semibold', statusColors[admin.trang_thai] || statusColors[0]]">
                    {{ admin.trang_thai === 1 ? 'Hoạt động' : 'Đã khóa' }}
                  </span>
                </td>
                <td class="px-6 py-4">
                  <div class="flex items-center justify-center gap-2">
                    <template v-if="canMutateAdmin(admin)">
                      <button class="rounded-lg p-2 text-slate-400 transition-colors hover:text-[#2463eb]" title="Chỉnh sửa" @click="openEditModal(admin)">
                        <span class="material-symbols-outlined text-xl">edit</span>
                      </button>
                      <button class="rounded-lg p-2 text-slate-400 transition-colors hover:text-violet-600" title="Phân quyền chức năng" @click="openPermissionTab(admin)">
                        <span class="material-symbols-outlined text-xl">tune</span>
                      </button>
                      <button class="rounded-lg p-2 text-slate-400 transition-colors hover:text-amber-600" :title="admin.trang_thai === 1 ? 'Khóa' : 'Mở khóa'" @click="toggleLock(admin)">
                        <span class="material-symbols-outlined text-xl">{{ admin.trang_thai === 1 ? 'block' : 'lock_open' }}</span>
                      </button>
                      <button class="rounded-lg p-2 text-slate-400 transition-colors hover:text-red-600" title="Xóa" @click="confirmDelete(admin)">
                        <span class="material-symbols-outlined text-xl">delete</span>
                      </button>
                    </template>
                    <span v-else class="inline-flex rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-semibold text-slate-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300">
                      {{ admin.la_super_admin ? 'Tài khoản bảo vệ' : 'Tài khoản hiện tại' }}
                    </span>
                  </div>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>

      <AdminPaginationBar
        v-if="!loading && admins.length > 0"
        :summary="`Hiển thị ${admins.length} / ${totalAdmins} tài khoản admin`"
        :current-page="currentPage"
        :total-pages="totalPages"
        @prev="goToPreviousPage"
        @next="goToNextPage"
      />
    </div>
  </template>

  <template v-else>
    <div class="grid gap-6 xl:grid-cols-[320px_minmax(0,1fr)]">
      <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div class="mb-4">
          <p class="text-xs font-semibold uppercase tracking-[0.24em] text-[#2463eb]">Tab chức năng</p>
          <h2 class="mt-2 text-xl font-black">Cấp quyền theo admin</h2>
          <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">Chọn một admin thường để bật hoặc tắt từng module mà tài khoản đó được phép truy cập.</p>
        </div>

        <div v-if="regularAdmins.length === 0" class="rounded-2xl border border-dashed border-slate-200 bg-slate-50 px-4 py-8 text-center text-sm text-slate-500 dark:border-slate-700 dark:bg-slate-800/50">
          Chưa có admin thường nào trong danh sách hiện tại.
        </div>

        <div v-else class="space-y-3">
          <button
            v-for="admin in regularAdmins"
            :key="admin.id"
            :class="[
              'w-full rounded-2xl border px-4 py-4 text-left transition',
              Number(admin.id) === Number(selectedPermissionAdminId)
                ? 'border-[#2463eb] bg-[#2463eb]/5 shadow-sm'
                : 'border-slate-200 bg-slate-50/80 hover:border-slate-300 hover:bg-white dark:border-slate-700 dark:bg-slate-800/60',
            ]"
            type="button"
            @click="selectedPermissionAdminId = admin.id; loadPermissionSettings(admin.id)"
          >
            <div class="flex items-start justify-between gap-3">
              <div>
                <p class="font-semibold text-slate-900 dark:text-white">{{ admin.ho_ten }}</p>
                <p class="mt-1 text-xs text-slate-500">{{ admin.email }}</p>
              </div>
              <span :class="['inline-flex rounded-full px-3 py-1 text-[11px] font-semibold', statusColors[admin.trang_thai] || statusColors[0]]">
                {{ admin.trang_thai === 1 ? 'Hoạt động' : 'Khóa' }}
              </span>
            </div>
            <div class="mt-4 flex items-center justify-between gap-3 text-xs text-slate-500">
              <span>{{ admin.so_quyen_admin || 0 }}/{{ admin.tong_quyen_admin || permissionCatalog.length }} chức năng</span>
              <span class="inline-flex items-center gap-1 font-medium text-[#2463eb]">
                <span class="material-symbols-outlined text-[16px]">arrow_forward</span>
                Chỉnh quyền
              </span>
            </div>
          </button>
        </div>
      </div>

      <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <template v-if="selectedPermissionAdmin">
          <div class="mb-6 flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">Admin được chọn</p>
              <h2 class="mt-2 text-2xl font-black">{{ selectedPermissionAdmin.ho_ten }}</h2>
              <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">{{ selectedPermissionAdmin.email }}</p>
            </div>
            <div class="flex flex-wrap gap-2">
              <span class="inline-flex rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
                {{ permissionSummaryText }}
              </span>
              <span :class="['inline-flex rounded-full px-3 py-1 text-xs font-semibold', statusColors[selectedPermissionAdmin.trang_thai] || statusColors[0]]">
                {{ selectedPermissionAdmin.trang_thai === 1 ? 'Đang hoạt động' : 'Đã khóa' }}
              </span>
            </div>
          </div>

          <div class="mb-6 flex flex-wrap gap-3 rounded-2xl border border-slate-200 bg-slate-50/70 p-4 dark:border-slate-700 dark:bg-slate-800/50">
            <button
              class="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800"
              type="button"
              @click="selectAllPermissions"
            >
              Cấp toàn bộ
            </button>
            <button
              class="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800"
              type="button"
              @click="clearAllPermissions"
            >
              Bỏ toàn bộ
            </button>
            <button
              class="inline-flex items-center gap-2 rounded-xl bg-[#2463eb] px-4 py-2 text-sm font-semibold text-white transition hover:bg-[#1d56cf] disabled:cursor-not-allowed disabled:opacity-60"
              type="button"
              :disabled="permissionSaving || permissionLoading || !permissionDirty"
              @click="savePermissions"
            >
              <span class="material-symbols-outlined text-[18px]">{{ permissionSaving ? 'hourglass_top' : 'save' }}</span>
              {{ permissionSaving ? 'Đang lưu...' : 'Lưu quyền chức năng' }}
            </button>
            <button
              class="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800"
              type="button"
              @click="openPermissionDefinitionModal"
            >
              <span class="material-symbols-outlined text-[18px]">add</span>
              Thêm chức năng
            </button>
          </div>

          <div v-if="permissionLoading" class="flex min-h-[260px] items-center justify-center rounded-2xl border border-dashed border-slate-200 bg-slate-50 text-slate-500 dark:border-slate-700 dark:bg-slate-800/50">
            <div class="text-center">
              <span class="material-symbols-outlined animate-spin text-3xl">hourglass_empty</span>
              <p class="mt-3 text-sm">Đang tải cấu hình quyền...</p>
            </div>
          </div>

          <div v-else class="grid gap-4 lg:grid-cols-2">
            <label
              v-for="permission in permissionCatalog"
              :key="permission.key"
              class="flex cursor-pointer items-start gap-4 rounded-2xl border border-slate-200 bg-slate-50/80 p-4 transition hover:border-slate-300 hover:bg-white dark:border-slate-700 dark:bg-slate-800/60"
            >
              <input
                v-model="permissionForm[permission.key]"
                class="mt-1 h-5 w-5 rounded border-slate-300 text-[#2463eb] focus:ring-[#2463eb]"
                type="checkbox"
              />
              <div class="min-w-0">
                <div class="flex flex-wrap items-center gap-2">
                  <p class="font-semibold text-slate-900 dark:text-white">{{ permission.label }}</p>
                  <span
                    :class="[
                      'inline-flex rounded-full px-2.5 py-1 text-[11px] font-semibold',
                      permissionForm[permission.key]
                        ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300'
                        : 'bg-slate-200 text-slate-600 dark:bg-slate-700 dark:text-slate-200',
                    ]"
                  >
                    {{ permissionForm[permission.key] ? 'Đã cấp' : 'Đã tắt' }}
                  </span>
                </div>
                <p class="mt-2 text-sm leading-6 text-slate-500 dark:text-slate-400">{{ permission.description }}</p>
              </div>
            </label>
          </div>
        </template>

        <div v-else class="flex min-h-[340px] items-center justify-center rounded-2xl border border-dashed border-slate-200 bg-slate-50 text-center text-sm text-slate-500 dark:border-slate-700 dark:bg-slate-800/50">
          Chọn một admin thường ở cột bên trái để cấu hình quyền chức năng.
        </div>
      </div>
    </div>
  </template>

  <FormModalShell
    v-if="showModal"
    eyebrow="Quản lý admin"
    :title="isEditing ? 'Cập nhật tài khoản admin' : 'Tạo admin thường mới'"
    description="Module này chỉ dùng cho tài khoản admin thường. Super Admin duy nhất được bảo vệ và không chỉnh sửa trực tiếp tại đây."
    max-width-class="max-w-4xl"
    :submit-label="isEditing ? 'Cập nhật admin' : 'Tạo admin'"
    :submit-loading-label="isEditing ? 'Đang cập nhật...' : 'Đang tạo...'"
    :saving="saving"
    @close="closeModal"
    @submit="submitForm"
  >
    <template #summary>
      <div class="rounded-2xl border border-slate-200 bg-white p-4">
        <p class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">Loại tài khoản</p>
        <div class="mt-3">
          <span class="inline-flex rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-sm font-semibold text-blue-700">
            Admin thường
          </span>
        </div>
      </div>
      <div class="rounded-2xl border border-slate-200 bg-white p-4">
        <p class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">Phạm vi</p>
        <p class="mt-2 text-sm text-slate-500">Quản lý vận hành hệ thống nhưng không có quyền quản lý tài khoản admin khác. Quyền chức năng chi tiết được cấu hình riêng trong tab Chức năng.</p>
      </div>
      <div class="rounded-2xl border border-slate-200 bg-white p-4">
        <p class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">Trạng thái</p>
        <div class="mt-3">
          <span :class="['inline-flex rounded-full px-3 py-1 text-sm font-semibold', statusColors[formData.trang_thai] || statusColors[0]]">
            {{ formData.trang_thai === 1 ? 'Hoạt động' : 'Khóa' }}
          </span>
        </div>
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
        <label class="block text-sm font-semibold text-slate-700">Mật khẩu</label>
        <input v-model="formData.mat_khau" :required="!isEditing" type="password" minlength="6" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-base text-slate-900 outline-none transition focus:border-[#2463eb] focus:bg-white focus:ring-2 focus:ring-[#2463eb]/20" />
        <p class="text-xs text-slate-400">{{ isEditing ? 'Để trống nếu không đổi mật khẩu.' : 'Tối thiểu 6 ký tự.' }}</p>
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
        <label class="block text-sm font-semibold text-slate-700">Trạng thái</label>
        <select v-model.number="formData.trang_thai" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-base text-slate-900 outline-none transition focus:border-[#2463eb] focus:bg-white focus:ring-2 focus:ring-[#2463eb]/20">
          <option :value="1">Hoạt động</option>
          <option :value="0">Khóa</option>
        </select>
      </div>
    </div>
  </FormModalShell>

  <FormModalShell
    v-if="showPermissionDefinitionModal"
    eyebrow="Chức năng admin"
    title="Tạo chức năng admin mới"
    description="Chức năng mới sẽ xuất hiện trong tab Chức năng để Super Admin bật hoặc tắt cho từng tài khoản admin."
    max-width-class="max-w-3xl"
    submit-label="Tạo chức năng"
    submit-loading-label="Đang tạo..."
    :saving="permissionDefinitionSaving"
    @close="closePermissionDefinitionModal"
    @submit="createPermissionDefinition"
  >
    <div class="grid gap-5">
      <div class="space-y-2">
        <label class="block text-sm font-semibold text-slate-700">Tên chức năng</label>
        <input v-model="permissionDefinitionForm.label" type="text" required class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-base text-slate-900 outline-none transition focus:border-[#2463eb] focus:bg-white focus:ring-2 focus:ring-[#2463eb]/20" placeholder="Ví dụ: Báo cáo tuyển dụng nâng cao" />
      </div>
      <div class="space-y-2">
        <label class="block text-sm font-semibold text-slate-700">Gắn vào chức năng đang có</label>
        <select v-model="permissionDefinitionForm.mapped_permission_key" required class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-base text-slate-900 outline-none transition focus:border-[#2463eb] focus:bg-white focus:ring-2 focus:ring-[#2463eb]/20">
          <option v-for="permission in systemPermissionOptions" :key="permission.key" :value="permission.key">
            {{ permission.label }}
          </option>
        </select>
      </div>
      <div class="space-y-2">
        <label class="block text-sm font-semibold text-slate-700">Mô tả</label>
        <textarea v-model="permissionDefinitionForm.description" rows="4" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-base text-slate-900 outline-none transition focus:border-[#2463eb] focus:bg-white focus:ring-2 focus:ring-[#2463eb]/20" placeholder="Mô tả phạm vi thao tác của chức năng này." />
      </div>
    </div>
  </FormModalShell>

  <div v-if="showDeleteModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 dark:bg-black/70">
    <div class="mx-4 w-full max-w-sm rounded-xl bg-white shadow-xl dark:bg-slate-900">
      <div class="p-6">
        <div class="mb-4 flex items-center gap-3">
          <span class="material-symbols-outlined text-2xl text-red-600">warning</span>
          <h3 class="text-lg font-semibold">Xóa admin</h3>
        </div>
        <p class="mb-6 text-slate-600 dark:text-slate-400">
          Bạn có chắc muốn xóa <strong>{{ deletingAdmin?.ho_ten }}</strong>? Tài khoản này sẽ mất toàn bộ token đang đăng nhập.
        </p>
        <div class="flex gap-3">
          <button class="flex-1 rounded-lg border border-slate-300 px-4 py-2 transition-colors hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-800" @click="showDeleteModal = false; deletingAdmin = null">
            Hủy
          </button>
          <button class="flex-1 rounded-lg bg-red-600 px-4 py-2 font-medium text-white transition-colors hover:bg-red-700" @click="deleteAdmin">
            Xóa
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
