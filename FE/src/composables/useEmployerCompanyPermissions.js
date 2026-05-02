import { computed, readonly, ref } from 'vue'
import { employerCompanyService } from '@/services/api'
import { getStoredEmployer } from '@/utils/authStorage'

const company = ref(null)
const loading = ref(false)
const loaded = ref(false)
const loadedForEmployerId = ref(null)
let authResetListenerRegistered = false
let pendingLoadPromise = null

const defaultPermissions = {
  company_profile: false,
  members: false,
  jobs: false,
  applications: false,
  interviews: false,
  offers: false,
  onboarding: false,
  exports: false,
  audit_logs: false,
}

const normalizePermissions = (payload) => ({
  ...defaultPermissions,
  ...(payload || {}),
})

const currentStoredEmployerId = () => Number(getStoredEmployer()?.id || 0) || null

const resetEmployerCompanyPermissions = () => {
  company.value = null
  loaded.value = false
  loading.value = false
  loadedForEmployerId.value = null
}

const ensureAuthResetListener = () => {
  if (authResetListenerRegistered || typeof window === 'undefined') return

  const reset = (event) => {
    const employerId = currentStoredEmployerId()
    const eventType = event?.detail?.type || ''

    if (eventType === 'profile-updated' && employerId && loadedForEmployerId.value === employerId) {
      return
    }

    resetEmployerCompanyPermissions()

    if (employerId) {
      loadEmployerCompanyPermissions().catch(() => {})
    }
  }

  window.addEventListener('auth-changed', reset)
  window.addEventListener('auth-invalidated', reset)
  authResetListenerRegistered = true
}

const loadEmployerCompanyPermissions = async ({ force = false } = {}) => {
  ensureAuthResetListener()

  const employerId = currentStoredEmployerId()

  if (loadedForEmployerId.value && loadedForEmployerId.value !== employerId) {
    resetEmployerCompanyPermissions()
  }

  if (loading.value && pendingLoadPromise) return pendingLoadPromise
  if (loaded.value && !force) return company.value

  pendingLoadPromise = (async () => {
    loading.value = true
    try {
      const response = await employerCompanyService.getCompany()
      company.value = response?.data || null
      loadedForEmployerId.value = employerId
    } catch (error) {
      if (error?.status === 404) {
        company.value = null
        loadedForEmployerId.value = employerId
      } else {
        throw error
      }
    } finally {
      loaded.value = true
      loading.value = false
      pendingLoadPromise = null
    }

    return company.value
  })()

  return pendingLoadPromise
}

export const useEmployerCompanyPermissions = () => {
  ensureAuthResetListener()

  const currentEmployer = computed(() => getStoredEmployer() || null)
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
  const currentEmployerId = computed(() => Number(currentEmployer.value?.id || 0) || null)
  const hasCompany = computed(() => Boolean(company.value?.id))
  const canViewEmployerData = computed(() => Boolean(
    permissions.value.company_profile
    || permissions.value.members
    || permissions.value.jobs
    || permissions.value.applications
    || permissions.value.interviews
    || permissions.value.offers
    || permissions.value.onboarding
    || permissions.value.audit_logs,
  ))
  const canManageCompanyProfile = computed(() => Boolean(permissions.value.company_profile))
  const canManageJobs = computed(() => Boolean(permissions.value.jobs))
  const canProcessApplications = computed(() => Boolean(permissions.value.applications || permissions.value.interviews || permissions.value.offers || permissions.value.onboarding))
  const canManageMembers = computed(() => Boolean(permissions.value.members))
  const canManageAllAssignments = computed(() => Boolean(permissions.value.members || permissions.value.jobs || permissions.value.applications))
  const canViewCompanyAuditLogs = computed(() => Boolean(permissions.value.audit_logs))

  return {
    company: readonly(company),
    companyMembers,
    assignableMembers,
    permissions,
    hasCompany,
    currentEmployerId,
    currentInternalRole,
    currentInternalRoleLabel,
    canViewEmployerData,
    canManageCompanyProfile,
    canManageJobs,
    canProcessApplications,
    canManageMembers,
    canManageAllAssignments,
    canViewCompanyAuditLogs,
    permissionsLoading: readonly(loading),
    permissionsLoaded: readonly(loaded),
    ensurePermissionsLoaded: loadEmployerCompanyPermissions,
    refreshPermissions: () => loadEmployerCompanyPermissions({ force: true }),
    resetPermissions: resetEmployerCompanyPermissions,
  }
}
