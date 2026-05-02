import { createRouter, createWebHistory } from 'vue-router'
import { authService } from '@/services/api'
import { getAuthToken, getStoredUser, updateStoredCandidate, updateStoredEmployer } from '@/utils/authStorage'
import { ADMIN_SCOPE_SUPER_ADMIN, hasAdminPermission } from '@/constants/adminPermissions'
import { useEmployerCompanyPermissions } from '@/composables/useEmployerCompanyPermissions'

const ROLE_CANDIDATE = 0
const ROLE_EMPLOYER = 1
const ROLE_ADMIN = 2

const getAuthState = () => {
  const token = getAuthToken()
  const user = getStoredUser()
  const normalizedRole = user?.vai_tro !== undefined && user?.vai_tro !== null ? Number(user.vai_tro) : null
  const role = Number.isNaN(normalizedRole) ? null : normalizedRole

  return {
    token,
    user,
    role,
    isAuthenticated: Boolean(token && user),
  }
}

const getHomeByRole = (role) => {
  switch (role) {
    case ROLE_EMPLOYER:
      return '/employer'
    case ROLE_ADMIN:
      return '/admin'
    case ROLE_CANDIDATE:
    default:
      return '/dashboard'
  }
}

const syncStoredUser = (user) => {
  if (!user) return

  if (Number(user.vai_tro) === ROLE_EMPLOYER) {
    updateStoredEmployer(user)
    return
  }

  updateStoredCandidate(user)
}

const routes = [
  // Guest pages
  {
    path: '/',
    name: 'Landing',
    component: () => import('@/components/Guest/LandingPage.vue'),
    meta: { layout: 'guest' }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/components/Guest/LoginPage.vue'),
    meta: { layout: 'auth', guestOnly: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/components/Guest/RegisterPage.vue'),
    meta: { layout: 'auth', guestOnly: true }
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('@/components/Guest/ForgotPasswordPage.vue'),
    meta: { layout: 'auth', guestOnly: true }
  },
  {
    path: '/reset-password',
    name: 'ResetPassword',
    component: () => import('@/components/Guest/ResetPasswordPage.vue'),
    meta: { layout: 'auth', guestOnly: true }
  },
  {
    path: '/oauth/google/callback',
    name: 'GoogleAuthCallback',
    component: () => import('@/components/Guest/GoogleAuthCallbackPage.vue'),
    meta: { layout: 'auth', guestOnly: true }
  },
  {
    path: '/application-action-result',
    name: 'ApplicationActionResult',
    component: () => import('@/components/Guest/ApplicationActionResultPage.vue'),
    meta: { layout: 'guest' }
  },
  {
    path: '/auth',
    name: 'Auth',
    redirect: '/login'
  },
  {
    path: '/employer/auth',
    name: 'EmployerAuth',
    redirect: '/login'
  },
  {
    path: '/employer/login',
    name: 'EmployerLogin',
    redirect: '/login'
  },
  {
    path: '/employer/register',
    name: 'EmployerRegister',
    redirect: '/register?role=employer'
  },
  {
    path: '/jobs',
    name: 'JobSearch',
    component: () => import('@/components/Guest/JobSearchPage.vue'),
    meta: { layout: 'guest' }
  },
  {
    path: '/companies',
    name: 'CompanyList',
    component: () => import('@/components/Guest/CompanyListPage.vue'),
    meta: { layout: 'guest' }
  },
  {
    path: '/industries',
    name: 'IndustryList',
    component: () => import('@/components/Guest/IndustryListPage.vue'),
    meta: { layout: 'guest' }
  },
  {
    path: '/skills',
    name: 'SkillList',
    component: () => import('@/components/Guest/SkillListPage.vue'),
    meta: { layout: 'guest' }
  },
  {
    path: '/jobs/:id',
    name: 'JobDetail',
    component: () => import('@/components/Guest/JobDetailPage.vue'),
    meta: { layout: 'guest' }
  },
  {
    path: '/companies/:id',
    name: 'CompanyDetail',
    component: () => import('@/components/Guest/CompanyDetailPage.vue'),
    meta: { layout: 'guest' }
  },
  {
    path: '/industries/:id',
    name: 'IndustryDetail',
    component: () => import('@/components/Guest/IndustryDetailPage.vue'),
    meta: { layout: 'guest' }
  },
  {
    path: '/skills/:id',
    name: 'SkillDetail',
    component: () => import('@/components/Guest/SkillDetailPage.vue'),
    meta: { layout: 'guest' }
  },
  // Dashboard pages (Job Seeker)
  {
    path: '/dashboard',
    name: 'SeekerDashboard',
    component: () => import('@/components/Dashboard/SeekerDashboardPage.vue'),
    meta: { layout: 'dashboard', requiresAuth: true, role: ROLE_CANDIDATE }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/components/Dashboard/ProfilePage.vue'),
    meta: { layout: 'dashboard', requiresAuth: true, role: ROLE_CANDIDATE }
  },
  {
    path: '/my-cv',
    name: 'MyCv',
    component: () => import('@/components/Dashboard/MyCvPage.vue'),
    meta: { layout: 'dashboard', requiresAuth: true, role: ROLE_CANDIDATE }
  },
  {
    path: '/cv-builder',
    name: 'CvBuilder',
    component: () => import('@/components/Dashboard/CvBuilderPage.vue'),
    meta: { layout: 'cv-builder', requiresAuth: true, role: ROLE_CANDIDATE, pageTitle: 'Tạo CV trên hệ thống' }
  },
  {
    path: '/cv-print-preview',
    name: 'CvPrintPreview',
    component: () => import('@/components/Dashboard/CvPrintPreviewPage.vue'),
    meta: { layout: 'plain', pageTitle: 'Xuất CV' }
  },
  {
    path: '/my-skills',
    name: 'MySkills',
    component: () => import('@/components/Dashboard/MySkillsPage.vue'),
    meta: { layout: 'dashboard', requiresAuth: true, role: ROLE_CANDIDATE }
  },
  {
    path: '/applications',
    name: 'Applications',
    component: () => import('@/components/Dashboard/ApplicationsPage.vue'),
    meta: { layout: 'dashboard', requiresAuth: true, role: ROLE_CANDIDATE }
  },
  {
    path: '/saved-jobs',
    name: 'SavedJobs',
    component: () => import('@/components/Dashboard/SavedJobsPage.vue'),
    meta: { layout: 'dashboard', requiresAuth: true, role: ROLE_CANDIDATE }
  },
  {
    path: '/followed-companies',
    name: 'FollowedCompanies',
    component: () => import('@/components/Dashboard/FollowedCompaniesPage.vue'),
    meta: { layout: 'dashboard', requiresAuth: true, role: ROLE_CANDIDATE }
  },
  {
    path: '/matched-jobs',
    name: 'MatchedJobs',
    component: () => import('@/components/Dashboard/MatchedJobsPage.vue'),
    meta: { layout: 'dashboard', requiresAuth: true, role: ROLE_CANDIDATE }
  },
  {
    path: '/career-report',
    name: 'CareerReport',
    component: () => import('@/components/Dashboard/CareerReportPage.vue'),
    meta: { layout: 'dashboard', requiresAuth: true, role: ROLE_CANDIDATE }
  },
  {
    path: '/wallet',
    name: 'Wallet',
    component: () => import('@/components/Dashboard/WalletPage.vue'),
    meta: { layout: 'dashboard', requiresAuth: true, role: ROLE_CANDIDATE }
  },
  {
    path: '/plans',
    name: 'Plans',
    component: () => import('@/components/Dashboard/PlansPage.vue'),
    meta: { layout: 'dashboard', requiresAuth: true, role: ROLE_CANDIDATE }
  },
  {
    path: '/payments',
    name: 'Payments',
    component: () => import('@/components/Dashboard/PaymentsPage.vue'),
    meta: { layout: 'dashboard', requiresAuth: true, role: ROLE_CANDIDATE }
  },
  {
    path: '/payments/:maGiaoDichNoiBo',
    name: 'PaymentDetail',
    component: () => import('@/components/Dashboard/PaymentDetailPage.vue'),
    meta: { layout: 'dashboard', requiresAuth: true, role: ROLE_CANDIDATE }
  },
  {
    path: '/wallet/payment-result/:maGiaoDichNoiBo',
    name: 'WalletPaymentResult',
    component: () => import('@/components/Dashboard/WalletPaymentResultPage.vue'),
    meta: { layout: 'dashboard', requiresAuth: true, role: ROLE_CANDIDATE }
  },
  {
    path: '/ai-center',
    component: () => import('@/components/Dashboard/AICenterPage.vue'),
    meta: { layout: 'dashboard', requiresAuth: true, role: ROLE_CANDIDATE },
    redirect: { name: 'AICenterChatbot' },
    children: [
      {
        path: 'chatbot',
        name: 'AICenterChatbot',
        component: () => import('@/components/Dashboard/AICenterChatPage.vue'),
      },
      {
        path: 'mock-interview',
        name: 'AICenterMockInterview',
        component: () => import('@/components/Dashboard/AICenterMockInterviewPage.vue'),
      },
    ],
  },
    // Employer pages
  {
    path: '/employer/home',
    name: 'EmployerHome',
    redirect: '/employer'
  },
  {
    path: '/employer',
    name: 'EmployerDashboard',
    component: () => import('@/components/Employer/EmployerDashboardPage.vue'),
    meta: { layout: 'employer', requiresAuth: true, role: ROLE_EMPLOYER }
  },
  {
    path: '/employer/jobs',
    name: 'EmployerJobs',
    component: () => import('@/components/Employer/EmployerJobsPage.vue'),
    meta: { layout: 'employer', requiresAuth: true, role: ROLE_EMPLOYER, employerPermission: 'jobs' }
  },
  {
    path: '/employer/jobs/:id',
    name: 'EmployerJobDetail',
    component: () => import('@/components/Employer/EmployerJobDetailPage.vue'),
    meta: { layout: 'employer', requiresAuth: true, role: ROLE_EMPLOYER, employerPermission: 'jobs' }
  },
  {
    path: '/employer/candidates',
    name: 'EmployerCandidates',
    component: () => import('@/components/Employer/EmployerCandidatesPage.vue'),
    meta: { layout: 'employer', requiresAuth: true, role: ROLE_EMPLOYER, employerPermission: 'applications' }
  },
  {
    path: '/employer/interviews',
    name: 'EmployerInterviews',
    component: () => import('@/components/Employer/EmployerInterviewsPage.vue'),
    meta: { layout: 'employer', requiresAuth: true, role: ROLE_EMPLOYER, employerPermission: 'interviews' }
  },
  {
    path: '/employer/billing',
    name: 'EmployerBilling',
    component: () => import('@/components/Employer/EmployerBillingPage.vue'),
    meta: { layout: 'employer', requiresAuth: true, role: ROLE_EMPLOYER, employerPermission: 'billing' }
  },
  {
    path: '/employer/company',
    name: 'EmployerCompany',
    component: () => import('@/components/Employer/EmployerCompanyPage.vue'),
    meta: { layout: 'employer', requiresAuth: true, role: ROLE_EMPLOYER, employerPermission: 'company_profile' }
  },
  {
    path: '/employer/hr-management',
    name: 'EmployerHrManagement',
    component: () => import('@/components/Employer/EmployerHrManagementPage.vue'),
    meta: { layout: 'employer', requiresAuth: true, role: ROLE_EMPLOYER, employerPermission: 'members' }
  },
  {
    path: '/employer/audit-logs',
    name: 'EmployerAuditLogs',
    component: () => import('@/components/Employer/EmployerAuditLogPage.vue'),
    meta: { layout: 'employer', requiresAuth: true, role: ROLE_EMPLOYER, employerPermission: 'audit_logs' }
  },
  {
    path: '/employer/profile',
    name: 'EmployerProfile',
    component: () => import('@/components/Employer/EmployerProfilePage.vue'),
    meta: { layout: 'employer', requiresAuth: true, role: ROLE_EMPLOYER }
  },
  // Admin pages
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: () => import('@/components/Admin/AdminDashboardPage.vue'),
    meta: { layout: 'admin', requiresAuth: true, role: ROLE_ADMIN }
  },
  {
    path: '/admin/profile',
    name: 'AdminProfile',
    component: () => import('@/components/Admin/AdminProfilePage.vue'),
    meta: { layout: 'admin', requiresAuth: true, role: ROLE_ADMIN }
  },
  {
    path: '/admin/audit-logs',
    name: 'AdminAuditLogs',
    component: () => import('@/components/Admin/AdminAuditLogPage.vue'),
    meta: { layout: 'admin', requiresAuth: true, role: ROLE_ADMIN, adminPermission: 'audit_logs' }
  },
  {
    path: '/admin/ai-usage',
    name: 'AdminAiUsage',
    component: () => import('@/components/Admin/AiUsageDashboardPage.vue'),
    meta: { layout: 'admin', requiresAuth: true, role: ROLE_ADMIN, adminPermission: 'ai_usage' }
  },
  {
    path: '/admin/billing',
    name: 'AdminBilling',
    component: () => import('@/components/Admin/AdminBillingDashboardPage.vue'),
    meta: { layout: 'admin', requiresAuth: true, role: ROLE_ADMIN, adminPermission: 'billing' }
  },
  {
    path: '/admin/users',
    name: 'UserManagement',
    component: () => import('@/components/Admin/UserManagementPage.vue'),
    meta: { layout: 'admin', requiresAuth: true, role: ROLE_ADMIN, adminPermission: 'users' }
  },
  {
    path: '/admin/admins',
    name: 'AdminManagement',
    component: () => import('@/components/Admin/AdminManagementPage.vue'),
    meta: { layout: 'admin', requiresAuth: true, role: ROLE_ADMIN, superAdmin: true }
  },
  {
    path: '/admin/companies',
    name: 'CompanyManagement',
    component: () => import('@/components/Admin/CompanyManagementPage.vue'),
    meta: { layout: 'admin', requiresAuth: true, role: ROLE_ADMIN, adminPermission: 'companies' }
  },
  {
    path: '/admin/profiles',
    name: 'AdminProfileManagement',
    component: () => import('@/components/Admin/ProfileManagementPage.vue'),
    meta: { layout: 'admin', requiresAuth: true, role: ROLE_ADMIN, adminPermission: 'profiles' }
  },
  {
    path: '/admin/user-skills',
    name: 'AdminUserSkillManagement',
    component: () => import('@/components/Admin/UserSkillManagementPage.vue'),
    meta: { layout: 'admin', requiresAuth: true, role: ROLE_ADMIN, adminPermission: 'user_skills' }
  },
  {
    path: '/admin/matchings',
    name: 'AdminMatchingManagement',
    component: () => import('@/components/Admin/MatchingManagementPage.vue'),
    meta: { layout: 'admin', requiresAuth: true, role: ROLE_ADMIN, adminPermission: 'matchings' }
  },
  {
    path: '/admin/career-advising',
    name: 'AdminCareerAdvisingManagement',
    component: () => import('@/components/Admin/CareerAdvisingManagementPage.vue'),
    meta: { layout: 'admin', requiresAuth: true, role: ROLE_ADMIN, adminPermission: 'career_advising' }
  },
  {
    path: '/admin/applications',
    name: 'AdminApplicationManagement',
    component: () => import('@/components/Admin/ApplicationManagementPage.vue'),
    meta: { layout: 'admin', requiresAuth: true, role: ROLE_ADMIN, adminPermission: 'applications' }
  },
  {
    path: '/admin/industries',
    name: 'IndustryManagement',
    component: () => import('@/components/Admin/IndustryManagementPage.vue'),
    meta: { layout: 'admin', requiresAuth: true, role: ROLE_ADMIN, adminPermission: 'industries' }
  },
  {
    path: '/admin/skills',
    name: 'SkillManagement',
    component: () => import('@/components/Admin/SkillManagementPage.vue'),
    meta: { layout: 'admin', requiresAuth: true, role: ROLE_ADMIN, adminPermission: 'skills' }
  },
  {
    path: '/admin/jobs',
    name: 'JobPostingsManagement',
    component: () => import('@/components/Admin/JobPostingsManagementPage.vue'),
    meta: { layout: 'admin', requiresAuth: true, role: ROLE_ADMIN, adminPermission: 'jobs' }
  },
  {
    path: '/admin/cv-templates',
    name: 'CvTemplateManagement',
    component: () => import('@/components/Admin/CvTemplateManagementPage.vue'),
    meta: { layout: 'admin', requiresAuth: true, role: ROLE_ADMIN, adminPermission: 'cv_templates' }
  },
  {
    path: '/admin/stats',
    name: 'StatsManagement',
    component: () => import('@/components/Admin/StatsManagementPage.vue'),
    meta: { layout: 'admin', requiresAuth: true, role: ROLE_ADMIN, adminPermission: 'stats' }
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

router.beforeEach(async (to) => {
  const auth = getAuthState()
  let latestUser = auth.user

  if (to.path === '/' && auth.isAuthenticated && [ROLE_EMPLOYER, ROLE_ADMIN].includes(auth.role)) {
    return getHomeByRole(auth.role)
  }

  if (to.meta?.guestOnly && auth.isAuthenticated) {
    return getHomeByRole(auth.role)
  }

  if (to.meta?.requiresAuth && !auth.isAuthenticated) {
    return {
      path: '/login',
      query: { redirect: to.fullPath }
    }
  }

  if (to.meta?.requiresAuth && auth.isAuthenticated) {
    try {
      const response = await authService.getProfile()
      latestUser = response?.data || latestUser
      syncStoredUser(latestUser)
    } catch (error) {
      if (error?.status === 401) {
        return '/login'
      }
    }
  }

  if (to.meta?.requiresAuth && auth.isAuthenticated && to.meta?.role !== undefined && auth.role !== to.meta.role) {
    return getHomeByRole(auth.role)
  }

  if (
    to.meta?.requiresAuth
    && auth.isAuthenticated
    && auth.role === ROLE_EMPLOYER
    && to.meta?.employerPermission
  ) {
    const { permissions, ensurePermissionsLoaded } = useEmployerCompanyPermissions()

    try {
      await ensurePermissionsLoaded()
    } catch (error) {
      return {
        path: '/employer',
        query: {
          permission_error: '1',
        },
      }
    }

    if (!permissions.value?.[to.meta.employerPermission]) {
      return {
        path: '/employer',
        query: {
          permission_denied: String(to.meta.employerPermission),
        },
      }
    }
  }

  if (to.meta?.superAdmin && latestUser?.cap_admin !== ADMIN_SCOPE_SUPER_ADMIN) {
    return '/admin'
  }

  if (to.meta?.adminPermission && !hasAdminPermission(latestUser, to.meta.adminPermission)) {
    return '/admin/profile'
  }

  return true
})

export default router
