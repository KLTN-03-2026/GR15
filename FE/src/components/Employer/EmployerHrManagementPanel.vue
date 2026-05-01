<script setup>
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { employerCompanyService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'
import FormModalShell from '@/components/FormModalShell.vue'
import AdminPaginationBar from '@/components/Admin/AdminPaginationBar.vue'

const notify = useNotify()

const loading = ref(false)
const error = ref(null)
const memberSubmitting = ref(false)
const roleSubmitting = ref(false)
const roleUpdatingIds = ref([])
const removingMemberIds = ref([])
const deletingRoleIds = ref([])
const company = ref(null)
const activeTab = ref('members')
const showCreateModal = ref(false)
const showEditMemberModal = ref(false)
const showRoleModal = ref(false)
const showRemoveModal = ref(false)
const removingMember = ref(null)
const editingMember = ref(null)
const editingRole = ref(null)
const permissionCatalog = ref([])
const permissionForm = ref({})
const permissionSnapshot = ref('{}')
const permissionLoading = ref(false)
const permissionSaving = ref(false)
const permissionDefinitionSaving = ref(false)
const showPermissionDefinitionModal = ref(false)
const selectedPermissionMemberId = ref(null)
const permissionDefinitionForm = reactive({
  label: '',
  description: '',
  mapped_permission_key: 'jobs',
})
const searchQuery = ref('')
const selectedRole = ref('')
const currentPage = ref(1)
const perPage = ref(10)
const listSectionRef = ref(null)
const hrAuditLogs = ref([])
const hrAuditPagination = ref(null)

const memberForm = reactive({
  ho_ten: '',
  email: '',
  mat_khau: '',
  so_dien_thoai: '',
  vai_tro_noi_bo: 'viewer',
})

const memberEditForm = reactive({
  ho_ten: '',
  email: '',
  mat_khau: '',
  so_dien_thoai: '',
  trang_thai: 1,
})

const roleForm = reactive({
  ten_vai_tro: '',
  mo_ta: '',
  vai_tro_goc: 'viewer',
})

const roleColors = {
  owner: 'border border-amber-200 bg-amber-50 text-amber-700 dark:border-amber-900/50 dark:bg-amber-900/20 dark:text-amber-300',
  admin_hr: 'border border-violet-200 bg-violet-50 text-violet-700 dark:border-violet-900/50 dark:bg-violet-900/20 dark:text-violet-300',
  recruiter: 'border border-blue-200 bg-blue-50 text-blue-700 dark:border-blue-900/50 dark:bg-blue-900/20 dark:text-blue-300',
  interviewer: 'border border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-900/50 dark:bg-emerald-900/20 dark:text-emerald-300',
  viewer: 'border border-slate-200 bg-slate-50 text-slate-700 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300',
}

const hasCompany = computed(() => Boolean(company.value?.id))
const companyMembers = computed(() => Array.isArray(company.value?.thanh_viens) ? company.value.thanh_viens : [])
const customInternalRoles = computed(() => Array.isArray(company.value?.vai_tro_noi_bo_custom) ? company.value.vai_tro_noi_bo_custom : [])
const canManageMembers = computed(() => Boolean(company.value?.quyen_noi_bo?.members))
const currentInternalRoleLabel = computed(() => company.value?.ten_vai_tro_noi_bo_hien_tai || 'HR Member')
const baseRoleOptions = computed(() => {
  const defaultOptions = {
    recruiter: 'Tuyển dụng',
    interviewer: 'Phỏng vấn',
    viewer: 'Chỉ xem',
    admin_hr: 'Quản trị HR',
  }

  return Object.entries(defaultOptions)
})
const internalRoleOptions = computed(() => {
  const defaultOptions = {
    recruiter: 'Tuyển dụng',
    interviewer: 'Phỏng vấn',
    viewer: 'Chỉ xem',
    admin_hr: 'Quản trị HR',
  }

  return Object.entries(company.value?.vai_tro_noi_bo_options || defaultOptions)
    .filter(([role]) => role !== 'owner')
})

const roleFilterOptions = computed(() => [
  ['owner', 'Owner'],
  ['member', 'HR thường'],
])

const ownerSummary = computed(() => {
  if (!hasCompany.value) return 'Bạn cần tạo công ty trước khi có thể quản lý nhân sự HR nội bộ.'
  if (canManageMembers.value) return 'Bạn có thể tạo tài khoản HR và cấp quyền chức năng trực tiếp cho từng người.'
  return 'Bạn chỉ có thể xem dữ liệu theo các chức năng được cấp.'
})

const hrStats = computed(() => {
  const members = companyMembers.value

  return {
    total: members.length,
    owners: members.filter((member) => member.la_chu_so_huu || member.vai_tro_noi_bo === 'owner').length,
    assignableHr: members.filter((member) => !member.la_chu_so_huu).length,
    lockedHr: members.filter((member) => !member.la_chu_so_huu && Number(member.trang_thai) !== 1).length,
    grantedPermissions: members.reduce((total, member) => total + Number(member.so_quyen_noi_bo || 0), 0),
    customRoles: customInternalRoles.value.length,
    auditLogs: Number(hrAuditPagination.value?.total || hrAuditLogs.value.length || 0),
  }
})

const filteredMembers = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()

  return companyMembers.value.filter((member) => {
    const role = member.la_chu_so_huu ? 'owner' : 'member'
    const matchesRole = !selectedRole.value || role === selectedRole.value
    const haystack = [
      member.ho_ten,
      member.email,
      member.so_dien_thoai,
      member.ten_vai_tro_noi_bo,
    ].filter(Boolean).join(' ').toLowerCase()

    return matchesRole && (!query || haystack.includes(query))
  })
})

const totalMemberPages = computed(() => Math.max(1, Math.ceil(filteredMembers.value.length / Number(perPage.value || 10))))
const paginatedMembers = computed(() => {
  const pageSize = Number(perPage.value || 10)
  const start = (currentPage.value - 1) * pageSize
  return filteredMembers.value.slice(start, start + pageSize)
})

const auditCurrentPage = computed(() => Number(hrAuditPagination.value?.current_page || 1))
const auditTotalPages = computed(() => Number(hrAuditPagination.value?.last_page || 1))
const isEditingRole = computed(() => Boolean(editingRole.value?.id))
const assignablePermissionMembers = computed(() => companyMembers.value.filter((member) => !member.la_chu_so_huu))
const selectedPermissionMember = computed(() =>
  assignablePermissionMembers.value.find((member) => Number(member.id) === Number(selectedPermissionMemberId.value)) || null,
)
const grantedPermissionCount = computed(() => Object.values(permissionForm.value || {}).filter(Boolean).length)
const permissionSummaryText = computed(() => `${grantedPermissionCount.value}/${permissionCatalog.value.length} chức năng đang được cấp`)
const permissionDirty = computed(() => JSON.stringify(permissionForm.value) !== permissionSnapshot.value)
const systemPermissionOptions = computed(() =>
  permissionCatalog.value.filter((permission) => !permission.is_custom && !permission.mapped_permission_key),
)

const baseRoleFor = (role) => {
  if (!role) return null
  if (['owner', 'admin_hr', 'recruiter', 'interviewer', 'viewer'].includes(role)) return role
  return customInternalRoles.value.find((item) => item.ma_vai_tro === role)?.vai_tro_goc || 'viewer'
}

const roleLabel = (memberOrRole) => {
  const role = typeof memberOrRole === 'string'
    ? memberOrRole
    : (memberOrRole?.la_chu_so_huu ? 'owner' : memberOrRole?.vai_tro_noi_bo)

  if (role === 'owner') return 'Owner'

  return internalRoleOptions.value.find(([value]) => value === role)?.[1] || 'HR Member'
}

const roleClass = (member) => {
  const role = member?.la_chu_so_huu ? 'owner' : baseRoleFor(member?.vai_tro_noi_bo || 'viewer')
  return roleColors[role] || roleColors.viewer
}

const roleIcon = (member) => {
  if (member?.la_chu_so_huu) return 'workspace_premium'

  return {
    admin_hr: 'admin_panel_settings',
    recruiter: 'person_search',
    interviewer: 'record_voice_over',
    viewer: 'visibility',
  }[baseRoleFor(member?.vai_tro_noi_bo)] || 'badge'
}

const messageFromError = (err, fallback) => err?.message || fallback

const resetMemberForm = () => {
  memberForm.ho_ten = ''
  memberForm.email = ''
  memberForm.mat_khau = ''
  memberForm.so_dien_thoai = ''
  memberForm.vai_tro_noi_bo = 'viewer'
}

const resetMemberEditForm = () => {
  memberEditForm.ho_ten = ''
  memberEditForm.email = ''
  memberEditForm.mat_khau = ''
  memberEditForm.so_dien_thoai = ''
  memberEditForm.trang_thai = 1
}

const resetRoleForm = () => {
  roleForm.ten_vai_tro = ''
  roleForm.mo_ta = ''
  roleForm.vai_tro_goc = 'viewer'
}

const normalizeHrPermissions = (permissions = {}) => {
  const catalog = permissionCatalog.value.length ? permissionCatalog.value : (company.value?.catalog_quyen_noi_bo || [])
  const normalized = Object.fromEntries(catalog.map((permission) => [permission.key, false]))

  Object.keys(normalized).forEach((key) => {
    if (Object.prototype.hasOwnProperty.call(permissions || {}, key)) {
      normalized[key] = Boolean(permissions[key])
    }
  })

  return normalized
}

const applyPermissionPayload = (payload) => {
  const catalog = Array.isArray(payload?.catalog) && payload.catalog.length
    ? payload.catalog
    : (company.value?.catalog_quyen_noi_bo || [])
  permissionCatalog.value = catalog
  const permissions = normalizeHrPermissions(payload?.quyen_noi_bo || payload?.hr?.quyen_noi_bo || {})
  permissionForm.value = permissions
  permissionSnapshot.value = JSON.stringify(permissions)

  if (payload?.cong_ty) {
    company.value = payload.cong_ty
  }
}

const ensurePermissionSelection = () => {
  if (!assignablePermissionMembers.value.length) {
    selectedPermissionMemberId.value = null
    permissionForm.value = normalizeHrPermissions()
    permissionSnapshot.value = JSON.stringify(permissionForm.value)
    return
  }

  const hasSelected = assignablePermissionMembers.value.some((member) => Number(member.id) === Number(selectedPermissionMemberId.value))
  if (!hasSelected) {
    selectedPermissionMemberId.value = assignablePermissionMembers.value[0].id
  }
}

const loadMemberPermissionSettings = async (memberId = selectedPermissionMemberId.value) => {
  if (!memberId) return

  permissionLoading.value = true
  error.value = null

  try {
    const response = await employerCompanyService.getMemberPermissions(memberId)
    applyPermissionPayload(response?.data || {})
  } catch (err) {
    error.value = messageFromError(err, 'Không thể tải quyền chức năng của HR.')
  } finally {
    permissionLoading.value = false
  }
}

const fetchCompany = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await employerCompanyService.getCompany()
    company.value = response?.data || null
    permissionCatalog.value = Array.isArray(company.value?.catalog_quyen_noi_bo) ? company.value.catalog_quyen_noi_bo : permissionCatalog.value
    ensurePermissionSelection()
  } catch (err) {
    if (err?.status === 404) {
      company.value = null
    } else {
      error.value = messageFromError(err, 'Không tải được dữ liệu quản lý HR.')
      notify.apiError(err, 'Không tải được dữ liệu quản lý HR.')
    }
  } finally {
    loading.value = false
  }
}

const fetchHrAuditLogs = async (page = 1) => {
  try {
    const response = await employerCompanyService.getHrAuditLogs({ page, per_page: 8 })
    const payload = response?.data || {}
    hrAuditLogs.value = Array.isArray(payload.data) ? payload.data : []
    hrAuditPagination.value = payload
  } catch (err) {
    hrAuditLogs.value = []
    hrAuditPagination.value = null
    error.value = messageFromError(err, 'Không tải được lịch sử thao tác HR.')
    notify.apiError(err, 'Không tải được lịch sử thao tác HR.')
  }
}

const refreshData = async () => {
  await Promise.all([fetchCompany(), fetchHrAuditLogs(hrAuditPagination.value?.current_page || 1)])
}

const openCreateModal = () => {
  if (!hasCompany.value) {
    notify.warning('Hãy tạo công ty trước khi thêm HR.')
    return
  }

  if (!canManageMembers.value) {
    notify.warning('Chỉ owner mới có thể thêm HR vào công ty.')
    return
  }

  resetMemberForm()
  showCreateModal.value = true
}

const closeCreateModal = () => {
  if (memberSubmitting.value) return
  showCreateModal.value = false
}

const openEditMemberModal = (member) => {
  if (!canManageMembers.value || !member || member.la_chu_so_huu) return

  editingMember.value = member
  memberEditForm.ho_ten = member.ho_ten || ''
  memberEditForm.email = member.email || ''
  memberEditForm.mat_khau = ''
  memberEditForm.so_dien_thoai = member.so_dien_thoai || ''
  memberEditForm.trang_thai = Number(member.trang_thai ?? 1)
  showEditMemberModal.value = true
}

const closeEditMemberModal = () => {
  if (memberSubmitting.value) return
  showEditMemberModal.value = false
  editingMember.value = null
  resetMemberEditForm()
}

const addHrMember = async () => {
  const payload = {
    ho_ten: String(memberForm.ho_ten || '').trim(),
    email: String(memberForm.email || '').trim(),
    mat_khau: String(memberForm.mat_khau || ''),
    so_dien_thoai: String(memberForm.so_dien_thoai || '').trim(),
  }

  if (!payload.ho_ten || !payload.email) {
    notify.warning('Vui lòng nhập họ tên và email HR.')
    return
  }

  if (!payload.mat_khau || payload.mat_khau.length < 6) {
    notify.warning('Vui lòng nhập mật khẩu HR tối thiểu 6 ký tự.')
    return
  }

  memberSubmitting.value = true
  error.value = null

  try {
    const response = await employerCompanyService.addMember(payload)
    company.value = response?.data?.cong_ty || response?.data?.data?.cong_ty || company.value

    if (!company.value) {
      await fetchCompany()
    }

    await fetchHrAuditLogs()
    resetMemberForm()
    showCreateModal.value = false
    notify.success('Đã tạo tài khoản HR với mật khẩu khởi tạo.')
  } catch (err) {
    error.value = messageFromError(err, 'Không thể tạo tài khoản HR.')
    notify.apiError(err, 'Không thể tạo tài khoản HR.')
  } finally {
    memberSubmitting.value = false
  }
}

const updateHrMember = async () => {
  const memberId = Number(editingMember.value?.id || 0)
  if (!memberId) return

  const payload = {
    ho_ten: String(memberEditForm.ho_ten || '').trim(),
    email: String(memberEditForm.email || '').trim(),
    so_dien_thoai: String(memberEditForm.so_dien_thoai || '').trim() || null,
    trang_thai: Number(memberEditForm.trang_thai ?? 1),
  }

  const password = String(memberEditForm.mat_khau || '')
  if (password) {
    if (password.length < 6) {
      notify.warning('Mật khẩu mới phải có ít nhất 6 ký tự.')
      return
    }
    payload.mat_khau = password
  }

  if (!payload.ho_ten || !payload.email) {
    notify.warning('Vui lòng nhập họ tên và email HR.')
    return
  }

  memberSubmitting.value = true
  error.value = null

  try {
    const response = await employerCompanyService.updateMember(memberId, payload)
    company.value = response?.data?.cong_ty || response?.data?.data?.cong_ty || company.value

    if (!company.value) {
      await fetchCompany()
    }

    await fetchHrAuditLogs(hrAuditPagination.value?.current_page || 1)
    showEditMemberModal.value = false
    editingMember.value = null
    resetMemberEditForm()
    notify.success('Đã cập nhật tài khoản HR.')
  } catch (err) {
    error.value = messageFromError(err, 'Không thể cập nhật tài khoản HR.')
    notify.apiError(err, 'Không thể cập nhật tài khoản HR.')
  } finally {
    memberSubmitting.value = false
  }
}

const toggleHrMemberStatus = async (member) => {
  const memberId = Number(member?.id || 0)
  if (!memberId || member?.la_chu_so_huu) return

  if (!canManageMembers.value) {
    notify.warning('Chỉ owner mới có thể khóa hoặc mở khóa HR.')
    return
  }

  roleUpdatingIds.value = [...roleUpdatingIds.value, memberId]
  error.value = null

  try {
    const response = await employerCompanyService.toggleMemberStatus(memberId)
    company.value = response?.data?.cong_ty || response?.data?.data?.cong_ty || company.value

    if (!company.value) {
      await fetchCompany()
    }

    await fetchHrAuditLogs(hrAuditPagination.value?.current_page || 1)
    notify.success(Number(member.trang_thai) === 1 ? 'Đã khóa tài khoản HR.' : 'Đã mở khóa tài khoản HR.')
  } catch (err) {
    error.value = messageFromError(err, 'Không thể cập nhật trạng thái HR.')
    notify.apiError(err, 'Không thể cập nhật trạng thái HR.')
  } finally {
    roleUpdatingIds.value = roleUpdatingIds.value.filter((id) => id !== memberId)
  }
}

const openCreateRoleModal = () => {
  if (!hasCompany.value) {
    notify.warning('Hãy tạo công ty trước khi thêm vai trò nội bộ.')
    return
  }

  if (!canManageMembers.value) {
    notify.warning('Chỉ owner mới có thể tạo vai trò nội bộ.')
    return
  }

  editingRole.value = null
  resetRoleForm()
  showRoleModal.value = true
}

const openEditRoleModal = (role) => {
  if (!canManageMembers.value || !role?.id) return

  editingRole.value = role
  roleForm.ten_vai_tro = role.ten_vai_tro || ''
  roleForm.mo_ta = role.mo_ta || ''
  roleForm.vai_tro_goc = role.vai_tro_goc || 'viewer'
  showRoleModal.value = true
}

const closeRoleModal = () => {
  if (roleSubmitting.value) return
  showRoleModal.value = false
  editingRole.value = null
}

const saveInternalRole = async () => {
  const payload = {
    ten_vai_tro: String(roleForm.ten_vai_tro || '').trim(),
    mo_ta: String(roleForm.mo_ta || '').trim(),
    vai_tro_goc: roleForm.vai_tro_goc || 'viewer',
  }

  if (!payload.ten_vai_tro) {
    notify.warning('Vui lòng nhập tên vai trò nội bộ.')
    return
  }

  roleSubmitting.value = true
  error.value = null

  try {
    const wasEditing = isEditingRole.value
    const response = wasEditing
      ? await employerCompanyService.updateInternalRole(editingRole.value.id, payload)
      : await employerCompanyService.createInternalRole(payload)

    company.value = response?.data?.cong_ty || response?.data?.data?.cong_ty || company.value

    if (!company.value) {
      await fetchCompany()
    }

    await fetchHrAuditLogs(hrAuditPagination.value?.current_page || 1)
    showRoleModal.value = false
    editingRole.value = null
    resetRoleForm()
    notify.success(wasEditing ? 'Đã cập nhật vai trò nội bộ.' : 'Đã tạo vai trò nội bộ.')
  } catch (err) {
    error.value = messageFromError(err, isEditingRole.value ? 'Không thể cập nhật vai trò nội bộ.' : 'Không thể tạo vai trò nội bộ.')
    notify.apiError(err, isEditingRole.value ? 'Không thể cập nhật vai trò nội bộ.' : 'Không thể tạo vai trò nội bộ.')
  } finally {
    roleSubmitting.value = false
  }
}

const deleteInternalRole = async (role) => {
  if (!role?.id || !canManageMembers.value) return

  const confirmed = window.confirm(`Xóa vai trò "${role.ten_vai_tro}"? Vai trò đang được gán cho HR sẽ không thể xóa.`)
  if (!confirmed) return

  deletingRoleIds.value = [...deletingRoleIds.value, role.id]
  error.value = null

  try {
    const response = await employerCompanyService.deleteInternalRole(role.id)
    company.value = response?.data?.cong_ty || response?.data?.data?.cong_ty || company.value

    if (!company.value) {
      await fetchCompany()
    }

    await fetchHrAuditLogs(hrAuditPagination.value?.current_page || 1)
    notify.success('Đã xóa vai trò nội bộ.')
  } catch (err) {
    error.value = messageFromError(err, 'Không thể xóa vai trò nội bộ.')
    notify.apiError(err, 'Không thể xóa vai trò nội bộ.')
  } finally {
    deletingRoleIds.value = deletingRoleIds.value.filter((id) => id !== role.id)
  }
}

const updateHrMemberRole = async (member, nextRole) => {
  const memberId = Number(member?.id || 0)
  const normalizedRole = String(nextRole || '').trim()

  if (!memberId || !normalizedRole || member?.la_chu_so_huu) return
  if (normalizedRole === member?.vai_tro_noi_bo) return

  if (!canManageMembers.value) {
    notify.warning('Chỉ owner mới có thể cập nhật vai trò HR.')
    return
  }

  roleUpdatingIds.value = [...roleUpdatingIds.value, memberId]
  error.value = null

  try {
    const response = await employerCompanyService.updateMemberRole(memberId, normalizedRole)
    company.value = response?.data?.cong_ty || response?.data?.data?.cong_ty || company.value

    if (!company.value) {
      await fetchCompany()
    }

    await fetchHrAuditLogs(hrAuditPagination.value?.current_page || 1)
    notify.success('Đã cập nhật vai trò nội bộ.')
  } catch (err) {
    error.value = messageFromError(err, 'Không thể cập nhật vai trò nội bộ.')
    notify.apiError(err, 'Không thể cập nhật vai trò nội bộ.')
  } finally {
    roleUpdatingIds.value = roleUpdatingIds.value.filter((id) => id !== memberId)
  }
}

const confirmRemoveMember = (member) => {
  if (!canManageMembers.value) {
    notify.warning('Chỉ owner mới có thể gỡ HR khỏi công ty.')
    return
  }

  if (!member || member.la_chu_so_huu) return

  removingMember.value = member
  showRemoveModal.value = true
}

const closeRemoveModal = () => {
  if (removingMemberIds.value.includes(removingMember.value?.id)) return
  showRemoveModal.value = false
  removingMember.value = null
}

const removeHrMember = async () => {
  const member = removingMember.value
  const memberId = Number(member?.id || 0)
  if (!memberId) return

  removingMemberIds.value = [...removingMemberIds.value, memberId]
  error.value = null

  try {
    const response = await employerCompanyService.removeMember(memberId)
    company.value = response?.data?.cong_ty || response?.data?.data?.cong_ty || company.value

    if (!company.value) {
      await fetchCompany()
    }

    await fetchHrAuditLogs(hrAuditPagination.value?.current_page || 1)
    notify.success('Đã gỡ HR khỏi công ty.')
    showRemoveModal.value = false
    removingMember.value = null
  } catch (err) {
    error.value = messageFromError(err, 'Không thể gỡ HR khỏi công ty.')
    notify.apiError(err, 'Không thể gỡ HR khỏi công ty.')
  } finally {
    removingMemberIds.value = removingMemberIds.value.filter((id) => id !== memberId)
  }
}

const switchTab = (tab) => {
  activeTab.value = tab

  if (tab === 'permissions') {
    ensurePermissionSelection()

    if (selectedPermissionMemberId.value) {
      loadMemberPermissionSettings(selectedPermissionMemberId.value)
    }
  }
}

const openPermissionTab = async (member) => {
  if (!member || member.la_chu_so_huu) return

  selectedPermissionMemberId.value = member.id
  activeTab.value = 'permissions'
  await loadMemberPermissionSettings(member.id)
}

const savePermissions = async () => {
  if (!selectedPermissionMemberId.value) return

  permissionSaving.value = true
  error.value = null

  try {
    const response = await employerCompanyService.updateMemberPermissions(
      selectedPermissionMemberId.value,
      permissionForm.value,
    )

    applyPermissionPayload(response?.data || {})
    notify.success('Đã cập nhật quyền chức năng cho HR.')
  } catch (err) {
    error.value = messageFromError(err, 'Không thể cập nhật quyền chức năng HR.')
    notify.apiError(err, 'Không thể cập nhật quyền chức năng HR.')
  } finally {
    permissionSaving.value = false
  }
}

const openPermissionDefinitionModal = () => {
  permissionDefinitionForm.label = ''
  permissionDefinitionForm.description = ''
  permissionDefinitionForm.mapped_permission_key = systemPermissionOptions.value[0]?.key || 'jobs'
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
    notify.warning('Vui lòng chọn tab hoặc chức năng hệ thống để gắn quyền mới.')
    return
  }

  permissionDefinitionSaving.value = true
  error.value = null

  try {
    const response = await employerCompanyService.createHrPermissionDefinition(payload)
    const catalog = response?.data?.catalog || permissionCatalog.value
    permissionCatalog.value = catalog
    permissionForm.value = normalizeHrPermissions(permissionForm.value)
    permissionSnapshot.value = JSON.stringify(permissionForm.value)
    showPermissionDefinitionModal.value = false
    notify.success('Đã tạo chức năng HR.')
  } catch (err) {
    error.value = messageFromError(err, 'Không thể tạo chức năng HR.')
    notify.apiError(err, 'Không thể tạo chức năng HR.')
  } finally {
    permissionDefinitionSaving.value = false
  }
}

const selectAllPermissions = () => {
  permissionForm.value = normalizeHrPermissions(
    Object.fromEntries(permissionCatalog.value.map((item) => [item.key, true])),
  )
}

const clearAllPermissions = () => {
  permissionForm.value = normalizeHrPermissions(
    Object.fromEntries(permissionCatalog.value.map((item) => [item.key, false])),
  )
}

const scrollToListTop = async () => {
  await nextTick()
  listSectionRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const onSearch = () => {
  currentPage.value = 1
}

const onFilterChange = () => {
  currentPage.value = 1
}

const resetFilters = () => {
  searchQuery.value = ''
  selectedRole.value = ''
  perPage.value = 10
  currentPage.value = 1
}

const goToPreviousPage = () => {
  if (currentPage.value === 1) return
  currentPage.value -= 1
  scrollToListTop()
}

const goToNextPage = () => {
  if (currentPage.value === totalMemberPages.value) return
  currentPage.value += 1
  scrollToListTop()
}

const goToPreviousAuditPage = () => {
  if (auditCurrentPage.value === 1) return
  fetchHrAuditLogs(auditCurrentPage.value - 1)
}

const goToNextAuditPage = () => {
  if (auditCurrentPage.value === auditTotalPages.value) return
  fetchHrAuditLogs(auditCurrentPage.value + 1)
}

onMounted(async () => {
  await refreshData()
})
</script>

<template>
  <div v-if="error" class="mb-6 flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4 dark:border-red-900 dark:bg-red-900/20">
    <span class="material-symbols-outlined mt-1 flex-shrink-0 text-red-600">error</span>
    <div class="flex-1 whitespace-pre-wrap break-words text-sm text-red-700 dark:text-red-400">{{ error }}</div>
    <button class="mt-1 flex-shrink-0 text-red-600 hover:text-red-700" type="button" @click="error = null">
      <span class="material-symbols-outlined">close</span>
    </button>
  </div>

  <div class="mb-8 flex flex-wrap items-center justify-between gap-4">
    <div class="flex flex-col gap-1">
      <h1 class="text-3xl font-black leading-tight tracking-tight text-slate-900 dark:text-white">Quản Lý Nhân Sự HR</h1>
      <p class="text-base text-slate-500 dark:text-slate-400">{{ ownerSummary }}</p>
    </div>
    <div class="flex flex-wrap gap-3">
      <button
        class="inline-flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800"
        type="button"
        @click="refreshData"
      >
        <span class="material-symbols-outlined text-[18px]">refresh</span>
        Tải lại
      </button>
      <button
        class="inline-flex items-center gap-2 rounded-2xl bg-[#2463eb] px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-[#1d56cf] disabled:cursor-not-allowed disabled:opacity-60"
        :disabled="!hasCompany || !canManageMembers"
        type="button"
        @click="openCreateModal"
      >
        <span class="material-symbols-outlined text-[18px]">person_add</span>
        Tạo HR mới
      </button>
    </div>
  </div>

  <div class="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-5">
    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <p class="text-sm font-medium text-slate-500">Tổng HR</p>
      <p class="mt-3 text-2xl font-black text-slate-900 dark:text-white">{{ hrStats.total }}</p>
    </div>
    <div class="rounded-xl border border-amber-200 bg-white p-6 shadow-sm dark:border-amber-900/50 dark:bg-slate-900">
      <p class="text-sm font-medium text-slate-500">HR được phân quyền</p>
      <p class="mt-3 text-2xl font-black text-amber-600">{{ hrStats.assignableHr }}</p>
    </div>
    <div class="rounded-xl border border-violet-200 bg-white p-6 shadow-sm dark:border-violet-900/50 dark:bg-slate-900">
      <p class="text-sm font-medium text-slate-500">Tổng quyền đã cấp</p>
      <p class="mt-3 text-2xl font-black text-violet-600">{{ hrStats.grantedPermissions }}</p>
    </div>
    <div class="rounded-xl border border-blue-200 bg-white p-6 shadow-sm dark:border-blue-900/50 dark:bg-slate-900">
      <p class="text-sm font-medium text-slate-500">HR bị khóa</p>
      <p class="mt-3 text-2xl font-black text-[#2463eb]">{{ hrStats.lockedHr }}</p>
    </div>
    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <p class="text-sm font-medium text-slate-500">Owner</p>
      <p class="mt-3 text-2xl font-black text-slate-900 dark:text-white">{{ hrStats.owners }}</p>
    </div>
  </div>

  <div class="mb-6 flex flex-wrap gap-3 rounded-2xl border border-slate-200 bg-white p-3 shadow-sm dark:border-slate-800 dark:bg-slate-900">
    <button
      :class="[
        'inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold transition',
        activeTab === 'members'
          ? 'bg-[#2463eb] text-white shadow-sm'
          : 'text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800',
      ]"
      type="button"
      @click="switchTab('members')"
    >
      <span class="material-symbols-outlined text-[18px]">groups</span>
      Tài khoản HR
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
    <button
      :class="[
        'inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold transition',
        activeTab === 'audit'
          ? 'bg-[#2463eb] text-white shadow-sm'
          : 'text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800',
      ]"
      type="button"
      @click="switchTab('audit')"
    >
      <span class="material-symbols-outlined text-[18px]">history</span>
      Lịch sử thao tác
    </button>
  </div>

  <template v-if="activeTab === 'members'">
    <div class="mb-6 flex flex-wrap items-center gap-4 rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="relative min-w-[280px] flex-1">
        <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">search</span>
        <input
          v-model="searchQuery"
          class="w-full rounded-lg bg-slate-50 py-2 pl-10 pr-4 text-sm outline-none focus:ring-2 focus:ring-[#2463eb] dark:bg-slate-800"
          placeholder="Tìm theo tên, email hoặc số điện thoại..."
          type="text"
          @input="onSearch"
        >
      </div>
      <div class="flex flex-wrap items-center gap-3">
        <select
          v-model="selectedRole"
          class="rounded-lg bg-slate-50 px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-[#2463eb] dark:bg-slate-800"
          @change="onFilterChange"
        >
          <option value="">Tất cả HR</option>
          <option v-for="[role, label] in roleFilterOptions" :key="role" :value="role">
            {{ label }}
          </option>
        </select>
        <select
          v-model.number="perPage"
          class="rounded-lg bg-slate-50 px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-[#2463eb] dark:bg-slate-800"
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
              <th class="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">Tài khoản HR</th>
              <th class="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">Chức năng</th>
              <th class="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">Liên hệ</th>
              <th class="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">Phạm vi quyền</th>
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
            <tr v-else-if="!hasCompany">
              <td colspan="6" class="px-6 py-8 text-center text-slate-500">
                <span class="material-symbols-outlined mb-2 text-3xl">domain_disabled</span>
                <div>Bạn cần tạo công ty trước khi sử dụng module quản lý HR.</div>
              </td>
            </tr>
            <tr v-else-if="filteredMembers.length === 0">
              <td colspan="6" class="px-6 py-8 text-center text-slate-500">
                <span class="material-symbols-outlined mb-2 text-3xl">groups</span>
                <div>Không tìm thấy HR phù hợp</div>
              </td>
            </tr>
            <template v-else>
              <tr v-for="member in paginatedMembers" :key="member.id" class="transition-colors hover:bg-slate-50/50 dark:hover:bg-slate-800/50">
                <td class="px-6 py-4">
                  <div class="flex items-center gap-3">
                    <div class="flex h-10 w-10 items-center justify-center overflow-hidden rounded-full bg-[#2463eb]/10 font-bold text-[#2463eb]">
                      <img v-if="member.avatar_url" :src="member.avatar_url" alt="avatar HR" class="h-full w-full object-cover">
                      <span v-else>{{ String(member.ho_ten || 'H').trim().charAt(0).toUpperCase() }}</span>
                    </div>
                    <div class="min-w-0">
                      <div class="text-sm font-semibold text-slate-900 dark:text-white">{{ member.ho_ten }}</div>
                      <div class="truncate text-xs text-slate-500">{{ member.email }}</div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <span class="inline-flex rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
                    {{ member.so_quyen_noi_bo || 0 }}/{{ member.tong_quyen_noi_bo || permissionCatalog.length }} chức năng
                  </span>
                </td>
                <td class="px-6 py-4 text-sm text-slate-600 dark:text-slate-400">
                  {{ member.so_dien_thoai || 'Chưa cập nhật' }}
                </td>
                <td class="px-6 py-4">
                  <span
                    :class="[
                      'inline-flex rounded-full px-3 py-1 text-xs font-semibold',
                      member.la_chu_so_huu
                        ? 'border border-amber-200 bg-amber-50 text-amber-700'
                        : 'border border-blue-200 bg-blue-50 text-blue-700',
                    ]"
                  >
                    {{ member.la_chu_so_huu ? 'Tài khoản sở hữu' : 'Theo quyền chức năng' }}
                  </span>
                </td>
                <td class="px-6 py-4">
                  <div class="flex items-center gap-2">
                    <div :class="['h-2 w-2 rounded-full', Number(member.trang_thai) === 1 ? 'bg-emerald-500' : 'bg-red-500']"></div>
                    <span :class="['text-sm font-medium', Number(member.trang_thai) === 1 ? 'text-emerald-600' : 'text-red-600']">
                      {{ Number(member.trang_thai) === 1 ? 'Hoạt động' : 'Đã khóa' }}
                    </span>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <div class="flex items-center justify-center gap-2">
                    <template v-if="canManageMembers && !member.la_chu_so_huu">
                      <button class="rounded-lg p-2 text-slate-400 transition-colors hover:text-[#2463eb]" title="Chỉnh sửa" type="button" @click="openEditMemberModal(member)">
                        <span class="material-symbols-outlined text-xl">edit</span>
                      </button>
                      <button
                        :class="[
                          'rounded-lg p-2 transition-colors disabled:cursor-not-allowed disabled:opacity-60',
                          Number(member.trang_thai) === 1 ? 'text-slate-400 hover:text-amber-600' : 'text-slate-400 hover:text-green-600',
                        ]"
                        :disabled="roleUpdatingIds.includes(member.id)"
                        :title="Number(member.trang_thai) === 1 ? 'Khóa' : 'Mở khóa'"
                        type="button"
                        @click="toggleHrMemberStatus(member)"
                      >
                        <span class="material-symbols-outlined text-xl">{{ Number(member.trang_thai) === 1 ? 'block' : 'lock_open' }}</span>
                      </button>
                      <button class="rounded-lg p-2 text-slate-400 transition-colors hover:text-violet-600" title="Phân quyền chức năng" type="button" @click="openPermissionTab(member)">
                        <span class="material-symbols-outlined text-xl">tune</span>
                      </button>
                      <button
                        class="rounded-lg p-2 text-slate-400 transition-colors hover:text-red-600 disabled:cursor-not-allowed disabled:opacity-60"
                        :disabled="removingMemberIds.includes(member.id) || roleUpdatingIds.includes(member.id)"
                        title="Gỡ HR"
                        type="button"
                        @click="confirmRemoveMember(member)"
                      >
                        <span class="material-symbols-outlined text-xl">person_remove</span>
                      </button>
                    </template>
                    <span v-else class="inline-flex rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-semibold text-slate-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300">
                      {{ member.la_chu_so_huu ? 'Tài khoản sở hữu' : 'Chỉ xem' }}
                    </span>
                  </div>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>

      <AdminPaginationBar
        v-if="!loading && filteredMembers.length > 0"
        :summary="`Hiển thị ${paginatedMembers.length} / ${filteredMembers.length} nhân sự HR`"
        :current-page="currentPage"
        :total-pages="totalMemberPages"
        @prev="goToPreviousPage"
        @next="goToNextPage"
      />
    </div>
  </template>

  <template v-else-if="activeTab === 'permissions'">
    <div class="grid gap-6 xl:grid-cols-[320px_minmax(0,1fr)]">
      <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div class="mb-4">
          <p class="text-xs font-semibold uppercase tracking-[0.24em] text-[#2463eb]">Tab chức năng</p>
          <h2 class="mt-2 text-xl font-black text-slate-900 dark:text-white">Cấp quyền theo HR</h2>
          <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">Chọn một tài khoản HR để bật hoặc tắt từng chức năng mà tài khoản đó được phép thao tác.</p>
        </div>

        <div v-if="assignablePermissionMembers.length === 0" class="rounded-2xl border border-dashed border-slate-200 bg-slate-50 px-4 py-8 text-center text-sm text-slate-500 dark:border-slate-700 dark:bg-slate-800/50">
          Chưa có HR thường nào để cấu hình quyền.
        </div>

        <div v-else class="space-y-3">
          <button
            v-for="member in assignablePermissionMembers"
            :key="member.id"
            :class="[
              'w-full rounded-2xl border px-4 py-4 text-left transition',
              Number(member.id) === Number(selectedPermissionMemberId)
                ? 'border-[#2463eb] bg-[#2463eb]/5 shadow-sm'
                : 'border-slate-200 bg-slate-50/80 hover:border-slate-300 hover:bg-white dark:border-slate-700 dark:bg-slate-800/60',
            ]"
            type="button"
            @click="selectedPermissionMemberId = member.id; loadMemberPermissionSettings(member.id)"
          >
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0">
                <p class="truncate font-semibold text-slate-900 dark:text-white">{{ member.ho_ten }}</p>
                <p class="mt-1 truncate text-xs text-slate-500">{{ member.email }}</p>
              </div>
              <span class="inline-flex shrink-0 rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-[11px] font-semibold text-blue-700">
                {{ member.so_quyen_noi_bo || 0 }} quyền
              </span>
            </div>
            <div class="mt-4 flex items-center justify-between gap-3 text-xs text-slate-500">
              <span>{{ member.so_quyen_noi_bo || 0 }}/{{ member.tong_quyen_noi_bo || permissionCatalog.length }} chức năng</span>
              <span class="inline-flex items-center gap-1 font-medium text-[#2463eb]">
                <span class="material-symbols-outlined text-[16px]">arrow_forward</span>
                Chỉnh quyền
              </span>
            </div>
          </button>
        </div>
      </div>

      <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <template v-if="selectedPermissionMember">
          <div class="mb-6 flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">HR được chọn</p>
              <h2 class="mt-2 text-2xl font-black text-slate-900 dark:text-white">{{ selectedPermissionMember.ho_ten }}</h2>
              <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">{{ selectedPermissionMember.email }}</p>
            </div>
            <div class="flex flex-wrap gap-2">
              <span class="inline-flex rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
                {{ permissionSummaryText }}
              </span>
              <span class="inline-flex rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-semibold text-slate-600">
                Tài khoản HR
              </span>
            </div>
          </div>

          <div class="mb-6 flex flex-wrap gap-3 rounded-2xl border border-slate-200 bg-slate-50/70 p-4 dark:border-slate-700 dark:bg-slate-800/50">
            <button class="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800" type="button" @click="selectAllPermissions">
              Cấp toàn bộ
            </button>
            <button class="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800" type="button" @click="clearAllPermissions">
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
              >
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
          Chọn một tài khoản HR ở cột bên trái để cấu hình quyền chức năng.
        </div>
      </div>
    </div>
  </template>

  <template v-else>
    <div class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="flex flex-col gap-3 border-b border-slate-200 bg-slate-50/50 px-6 py-5 dark:border-slate-800 dark:bg-slate-800/50 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 class="text-lg font-bold text-slate-900 dark:text-white">Lịch sử thao tác HR nội bộ</h2>
          <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Theo dõi các thay đổi quan trọng như thêm HR, cập nhật quyền chức năng và gỡ thành viên khỏi công ty.</p>
        </div>
        <button
          class="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-semibold transition hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 dark:hover:bg-slate-800"
          type="button"
          @click="fetchHrAuditLogs(hrAuditPagination?.current_page || 1)"
        >
          <span class="material-symbols-outlined text-[18px]">refresh</span>
          Tải lại log
        </button>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full border-collapse text-left">
          <thead>
            <tr class="border-b border-slate-200 bg-slate-50/50 dark:border-slate-800 dark:bg-slate-800/50">
              <th class="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">Nội dung thao tác</th>
              <th class="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">Người thực hiện</th>
              <th class="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">Đối tượng</th>
              <th class="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">Thời gian</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 dark:divide-slate-800">
            <tr v-if="hrAuditLogs.length === 0">
              <td colspan="4" class="px-6 py-8 text-center text-slate-500">
                <span class="material-symbols-outlined mb-2 text-3xl">history</span>
                <div>Chưa có lịch sử thao tác HR nội bộ nào để hiển thị.</div>
              </td>
            </tr>
            <template v-else>
              <tr v-for="log in hrAuditLogs" :key="`audit-${log.id}`" class="transition-colors hover:bg-slate-50/50 dark:hover:bg-slate-800/50">
                <td class="px-6 py-4">
                  <p class="text-sm font-semibold text-slate-900 dark:text-white">{{ log.mo_ta }}</p>
                </td>
                <td class="px-6 py-4 text-sm text-slate-600 dark:text-slate-400">
                  {{ log.nguoi_thuc_hien?.ho_ten || log.nguoi_thuc_hien?.email || 'Hệ thống' }}
                </td>
                <td class="px-6 py-4 text-sm text-slate-600 dark:text-slate-400">
                  {{ log.nguoi_bi_tac_dong?.ho_ten || log.nguoi_bi_tac_dong?.email || 'Không có' }}
                </td>
                <td class="px-6 py-4 text-sm text-slate-600 dark:text-slate-400">
                  {{ log.created_at ? new Date(log.created_at).toLocaleString('vi-VN') : 'N/A' }}
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>

      <AdminPaginationBar
        v-if="hrAuditPagination && hrAuditLogs.length > 0"
        :summary="`Hiển thị ${hrAuditLogs.length} / ${hrAuditPagination.total || hrAuditLogs.length} lịch sử thao tác`"
        :current-page="auditCurrentPage"
        :total-pages="auditTotalPages"
        @prev="goToPreviousAuditPage"
        @next="goToNextAuditPage"
      />
    </div>
  </template>

  <FormModalShell
    v-if="showCreateModal"
    eyebrow="Quản lý nhân sự HR"
    title="Tạo tài khoản HR mới"
    description="Tài khoản HR được gắn vào công ty hiện tại và đăng nhập bằng mật khẩu khởi tạo do bạn đặt."
    max-width-class="max-w-4xl"
    submit-label="Tạo HR"
    submit-loading-label="Đang tạo..."
    :saving="memberSubmitting"
    @close="closeCreateModal"
    @submit="addHrMember"
  >
    <template #summary>
      <div class="rounded-2xl border border-slate-200 bg-white p-4">
        <p class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">Công ty</p>
        <p class="mt-2 text-sm font-semibold text-slate-900">{{ company?.ten_cong_ty || company?.ten || 'Công ty hiện tại' }}</p>
      </div>
      <div class="rounded-2xl border border-slate-200 bg-white p-4">
        <p class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">Phân quyền</p>
        <div class="mt-3">
          <span class="inline-flex rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-sm font-semibold text-blue-700">
            Theo quyền chức năng
          </span>
        </div>
      </div>
      <div class="rounded-2xl border border-slate-200 bg-white p-4">
        <p class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">Quyền tạo</p>
        <p class="mt-2 text-sm text-slate-500">Chỉ owner công ty có thể tạo, cấp quyền chức năng hoặc gỡ HR nội bộ.</p>
      </div>
    </template>

    <div class="grid gap-5 lg:grid-cols-2">
      <div class="space-y-2">
        <label class="block text-sm font-semibold text-slate-700">Họ tên</label>
        <input v-model="memberForm.ho_ten" type="text" required class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-base text-slate-900 outline-none transition focus:border-[#2463eb] focus:bg-white focus:ring-2 focus:ring-[#2463eb]/20" placeholder="Nguyễn Văn A">
      </div>
      <div class="space-y-2">
        <label class="block text-sm font-semibold text-slate-700">Email</label>
        <input v-model="memberForm.email" type="email" required class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-base text-slate-900 outline-none transition focus:border-[#2463eb] focus:bg-white focus:ring-2 focus:ring-[#2463eb]/20" placeholder="hr@company.com">
      </div>
      <div class="space-y-2">
        <label class="block text-sm font-semibold text-slate-700">Mật khẩu</label>
        <input v-model="memberForm.mat_khau" type="password" required minlength="6" autocomplete="new-password" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-base text-slate-900 outline-none transition focus:border-[#2463eb] focus:bg-white focus:ring-2 focus:ring-[#2463eb]/20" placeholder="Tối thiểu 6 ký tự">
        <p class="text-xs text-slate-400">HR sẽ dùng mật khẩu này để đăng nhập lần đầu.</p>
      </div>
      <div class="space-y-2">
        <label class="block text-sm font-semibold text-slate-700">Số điện thoại</label>
        <input v-model="memberForm.so_dien_thoai" type="tel" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-base text-slate-900 outline-none transition focus:border-[#2463eb] focus:bg-white focus:ring-2 focus:ring-[#2463eb]/20" placeholder="090...">
      </div>
    </div>
  </FormModalShell>

  <FormModalShell
    v-if="showEditMemberModal"
    eyebrow="Quản lý nhân sự HR"
    title="Chỉnh sửa tài khoản HR"
    description="Cập nhật thông tin đăng nhập, liên hệ và trạng thái hoạt động của tài khoản HR."
    max-width-class="max-w-4xl"
    submit-label="Lưu thay đổi"
    submit-loading-label="Đang lưu..."
    :saving="memberSubmitting"
    @close="closeEditMemberModal"
    @submit="updateHrMember"
  >
    <template #summary>
      <div class="rounded-2xl border border-slate-200 bg-white p-4">
        <p class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">Tài khoản</p>
        <p class="mt-2 text-base font-semibold text-slate-900">{{ memberEditForm.ho_ten || 'Chưa nhập họ tên' }}</p>
        <p class="mt-1 text-sm text-slate-500">{{ memberEditForm.email || 'Chưa có email' }}</p>
      </div>
      <div class="rounded-2xl border border-slate-200 bg-white p-4">
        <p class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">Phân quyền</p>
        <div class="mt-3">
          <span class="inline-flex rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-sm font-semibold text-blue-700">
            Theo quyền chức năng
          </span>
        </div>
        <p class="mt-2 text-sm text-slate-500">Quyền chi tiết được chỉnh ở tab Chức năng.</p>
      </div>
      <div class="rounded-2xl border border-slate-200 bg-white p-4">
        <p class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">Trạng thái</p>
        <div class="mt-3">
          <span
            :class="[
              'inline-flex rounded-full px-3 py-1 text-sm font-semibold',
              Number(memberEditForm.trang_thai) === 1
                ? 'border border-emerald-200 bg-emerald-50 text-emerald-700'
                : 'border border-rose-200 bg-rose-50 text-rose-700',
            ]"
          >
            {{ Number(memberEditForm.trang_thai) === 1 ? 'Hoạt động' : 'Khóa' }}
          </span>
        </div>
        <p class="mt-2 text-sm text-slate-500">Tài khoản bị khóa sẽ không thể đăng nhập hệ thống.</p>
      </div>
    </template>

    <div class="grid gap-5 lg:grid-cols-2">
      <div class="space-y-2">
        <label class="block text-sm font-semibold text-slate-700">Họ tên</label>
        <input v-model="memberEditForm.ho_ten" type="text" required class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-base text-slate-900 outline-none transition focus:border-[#2463eb] focus:bg-white focus:ring-2 focus:ring-[#2463eb]/20">
      </div>
      <div class="space-y-2">
        <label class="block text-sm font-semibold text-slate-700">Email</label>
        <input v-model="memberEditForm.email" type="email" required class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-base text-slate-900 outline-none transition focus:border-[#2463eb] focus:bg-white focus:ring-2 focus:ring-[#2463eb]/20">
      </div>
      <div class="space-y-2">
        <label class="block text-sm font-semibold text-slate-700">Mật khẩu mới</label>
        <input v-model="memberEditForm.mat_khau" type="password" minlength="6" autocomplete="new-password" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-base text-slate-900 outline-none transition focus:border-[#2463eb] focus:bg-white focus:ring-2 focus:ring-[#2463eb]/20">
        <p class="text-xs text-slate-400">Để trống nếu không muốn đổi mật khẩu.</p>
      </div>
      <div class="space-y-2">
        <label class="block text-sm font-semibold text-slate-700">Số điện thoại</label>
        <input v-model="memberEditForm.so_dien_thoai" type="tel" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-base text-slate-900 outline-none transition focus:border-[#2463eb] focus:bg-white focus:ring-2 focus:ring-[#2463eb]/20">
      </div>
      <div class="space-y-2">
        <label class="block text-sm font-semibold text-slate-700">Trạng thái</label>
        <select v-model.number="memberEditForm.trang_thai" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-base text-slate-900 outline-none transition focus:border-[#2463eb] focus:bg-white focus:ring-2 focus:ring-[#2463eb]/20">
          <option :value="1">Hoạt động</option>
          <option :value="0">Khóa</option>
        </select>
      </div>
    </div>
  </FormModalShell>

  <FormModalShell
    v-if="showPermissionDefinitionModal"
    eyebrow="Chức năng HR"
    title="Tạo chức năng HR mới"
    description="Chức năng mới sẽ xuất hiện trong tab Chức năng để bật hoặc tắt cho từng tài khoản HR."
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
        <input v-model="permissionDefinitionForm.label" type="text" required class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-base text-slate-900 outline-none transition focus:border-[#2463eb] focus:bg-white focus:ring-2 focus:ring-[#2463eb]/20" placeholder="Ví dụ: Quản lý ví" />
      </div>
      <div class="space-y-2">
        <label class="block text-sm font-semibold text-slate-700">Gắn vào tab/chức năng đang có</label>
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

  <FormModalShell
    v-if="showRoleModal"
    eyebrow="Vai trò nội bộ"
    :title="isEditingRole ? 'Cập nhật vai trò nội bộ' : 'Tạo vai trò nội bộ mới'"
    description="Vai trò tùy chỉnh sẽ kế thừa quyền thao tác từ một vai trò hệ thống để các route hiện tại vẫn kiểm soát quyền nhất quán."
    max-width-class="max-w-3xl"
    :submit-label="isEditingRole ? 'Cập nhật vai trò' : 'Tạo vai trò'"
    :submit-loading-label="isEditingRole ? 'Đang cập nhật...' : 'Đang tạo...'"
    :saving="roleSubmitting"
    @close="closeRoleModal"
    @submit="saveInternalRole"
  >
    <template #summary>
      <div class="rounded-2xl border border-slate-200 bg-white p-4">
        <p class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">Loại vai trò</p>
        <p class="mt-2 text-sm font-semibold text-slate-900">Vai trò tùy chỉnh</p>
      </div>
      <div class="rounded-2xl border border-slate-200 bg-white p-4">
        <p class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">Kế thừa quyền</p>
        <div class="mt-3">
          <span :class="['inline-flex rounded-full px-3 py-1 text-sm font-semibold', roleColors[roleForm.vai_tro_goc] || roleColors.viewer]">
            {{ roleLabel(roleForm.vai_tro_goc) }}
          </span>
        </div>
      </div>
      <div class="rounded-2xl border border-slate-200 bg-white p-4">
        <p class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">Ghi chú</p>
        <p class="mt-2 text-sm text-slate-500">Mã vai trò được hệ thống tạo tự động và giữ ổn định sau khi tạo.</p>
      </div>
    </template>

    <div class="grid gap-5">
      <div class="space-y-2">
        <label class="block text-sm font-semibold text-slate-700">Tên vai trò</label>
        <input v-model="roleForm.ten_vai_tro" type="text" required class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-base text-slate-900 outline-none transition focus:border-[#2463eb] focus:bg-white focus:ring-2 focus:ring-[#2463eb]/20" placeholder="Ví dụ: Talent Acquisition Lead">
      </div>
      <div class="space-y-2">
        <label class="block text-sm font-semibold text-slate-700">Kế thừa quyền từ</label>
        <select v-model="roleForm.vai_tro_goc" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-base text-slate-900 outline-none transition focus:border-[#2463eb] focus:bg-white focus:ring-2 focus:ring-[#2463eb]/20">
          <option v-for="[role, label] in baseRoleOptions" :key="role" :value="role">
            {{ label }}
          </option>
        </select>
      </div>
      <div class="space-y-2">
        <label class="block text-sm font-semibold text-slate-700">Mô tả</label>
        <textarea v-model="roleForm.mo_ta" rows="4" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-base text-slate-900 outline-none transition focus:border-[#2463eb] focus:bg-white focus:ring-2 focus:ring-[#2463eb]/20" placeholder="Mô tả phạm vi công việc hoặc trách nhiệm của vai trò này." />
      </div>
    </div>
  </FormModalShell>

  <div v-if="showRemoveModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 dark:bg-black/70">
    <div class="mx-4 w-full max-w-sm rounded-xl bg-white shadow-xl dark:bg-slate-900">
      <div class="p-6">
        <div class="mb-4 flex items-center gap-3">
          <span class="material-symbols-outlined text-2xl text-red-600">warning</span>
          <h3 class="text-lg font-semibold text-slate-900 dark:text-white">Gỡ HR khỏi công ty</h3>
        </div>
        <p class="mb-6 text-slate-600 dark:text-slate-400">
          Bạn có chắc muốn gỡ <strong>{{ removingMember?.ho_ten }}</strong> khỏi công ty? Tài khoản này sẽ không còn quyền thao tác trong workspace hiện tại.
        </p>
        <div class="flex gap-3">
          <button class="flex-1 rounded-lg border border-slate-300 px-4 py-2 transition-colors hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-800" type="button" @click="closeRemoveModal">
            Hủy
          </button>
          <button
            class="flex-1 rounded-lg bg-red-600 px-4 py-2 font-medium text-white transition-colors hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-60"
            :disabled="removingMemberIds.includes(removingMember?.id)"
            type="button"
            @click="removeHrMember"
          >
            {{ removingMemberIds.includes(removingMember?.id) ? 'Đang gỡ...' : 'Gỡ HR' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
