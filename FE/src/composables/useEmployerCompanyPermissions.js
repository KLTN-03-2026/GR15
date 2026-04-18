import { computed, readonly, ref } from 'vue'
import { employerCompanyService } from '@/services/api'

const company = ref(null)
const loading = ref(false)
const loaded = ref(false)

const defaultPermissions = {
  co_the_xem: false,
  co_the_quan_ly_cong_ty: false,
  co_the_quan_ly_tin_tuyen_dung: false,
  co_the_xu_ly_ung_tuyen: false,
  co_the_quan_ly_thanh_vien: false,
}

const normalizePermissions = (payload) => ({
  ...defaultPermissions,
  ...(payload || {}),
})

const loadEmployerCompanyPermissions = async ({ force = false } = {}) => {
  if (loading.value) return company.value
  if (loaded.value && !force) return company.value

  loading.value = true
  try {
    const response = await employerCompanyService.getCompany()
    company.value = response?.data || null
  } catch (error) {
    if (error?.status === 404) {
      company.value = null
    } else {
      throw error
    }
  } finally {
    loaded.value = true
    loading.value = false
  }

  return company.value
}

export const useEmployerCompanyPermissions = () => {
  const permissions = computed(() => normalizePermissions(company.value?.quyen_noi_bo))
  const companyMembers = computed(() => Array.isArray(company.value?.thanh_viens) ? company.value.thanh_viens : [])
  const assignableMembers = computed(() =>
    companyMembers.value.map((member) => ({
      id: member.id,
      label: `${member.ho_ten} (${member.ten_vai_tro_noi_bo || 'HR Member'})`,
      role: member.vai_tro_noi_bo || null,
    })),
  )
  const currentInternalRole = computed(() => company.value?.vai_tro_noi_bo_hien_tai || null)
  const currentInternalRoleLabel = computed(() => company.value?.ten_vai_tro_noi_bo_hien_tai || 'HR Member')
  const hasCompany = computed(() => Boolean(company.value?.id))
  const canViewEmployerData = computed(() => Boolean(permissions.value.co_the_xem))
  const canManageCompanyProfile = computed(() => Boolean(permissions.value.co_the_quan_ly_cong_ty))
  const canManageJobs = computed(() => Boolean(permissions.value.co_the_quan_ly_tin_tuyen_dung))
  const canProcessApplications = computed(() => Boolean(permissions.value.co_the_xu_ly_ung_tuyen))
  const canManageMembers = computed(() => Boolean(permissions.value.co_the_quan_ly_thanh_vien))

  return {
    company: readonly(company),
    companyMembers,
    assignableMembers,
    permissions,
    hasCompany,
    currentInternalRole,
    currentInternalRoleLabel,
    canViewEmployerData,
    canManageCompanyProfile,
    canManageJobs,
    canProcessApplications,
    canManageMembers,
    permissionsLoading: readonly(loading),
    permissionsLoaded: readonly(loaded),
    ensurePermissionsLoaded: loadEmployerCompanyPermissions,
    refreshPermissions: () => loadEmployerCompanyPermissions({ force: true }),
  }
}
