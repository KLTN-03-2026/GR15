import { createRouter, createWebHistory } from 'vue-router'
import { authService } from '@/services/api'
import { getAuthToken, getStoredUser } from '@/utils/authStorage'

const ROLE_CANDIDATE = 0
const ROLE_EMPLOYER = 1
const ROLE_ADMIN = 2

const getAuthState = () => {
  const token = getAuthToken()
  const user = getStoredUser()
  const role = typeof user?.vai_tro === 'number' ? user.vai_tro : null

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
    path: '/employer',
    name: 'EmployerDashboard',
    component: () => import('@/components/Employer/EmployerDashboardPage.vue'),
    meta: { layout: 'employer', requiresAuth: true, role: ROLE_EMPLOYER }
  },
  {
    path: '/employer/jobs',
    name: 'EmployerJobs',
    component: () => import('@/components/Employer/EmployerJobsPage.vue'),
    meta: { layout: 'employer', requiresAuth: true, role: ROLE_EMPLOYER }
  },
  {
    path: '/employer/jobs/:id',
    name: 'EmployerJobDetail',
    component: () => import('@/components/Employer/EmployerJobDetailPage.vue'),
    meta: { layout: 'employer', requiresAuth: true, role: ROLE_EMPLOYER }
  },
  {
    path: '/employer/candidates',
    name: 'EmployerCandidates',
    component: () => import('@/components/Employer/EmployerCandidatesPage.vue'),
    meta: { layout: 'employer', requiresAuth: true, role: ROLE_EMPLOYER }
  },
  {
    path: '/employer/interviews',
    name: 'EmployerInterviews',
    component: () => import('@/components/Employer/EmployerInterviewsPage.vue'),
    meta: { layout: 'employer', requiresAuth: true, role: ROLE_EMPLOYER }
  },
  {
    path: '/employer/company',
    name: 'EmployerCompany',
    component: () => import('@/components/Employer/EmployerCompanyPage.vue'),
    meta: { layout: 'employer', requiresAuth: true, role: ROLE_EMPLOYER }
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
    path: '/admin/users',
    name: 'UserManagement',
    component: () => import('@/components/Admin/UserManagementPage.vue'),
    meta: { layout: 'admin', requiresAuth: true, role: ROLE_ADMIN }
  },
  {
    path: '/admin/companies',
    name: 'CompanyManagement',
    component: () => import('@/components/Admin/CompanyManagementPage.vue'),
    meta: { layout: 'admin', requiresAuth: true, role: ROLE_ADMIN }
  },
  {
    path: '/admin/profiles',
    name: 'AdminProfileManagement',
    component: () => import('@/components/Admin/ProfileManagementPage.vue'),
    meta: { layout: 'admin', requiresAuth: true, role: ROLE_ADMIN }
  },
  {
    path: '/admin/user-skills',
    name: 'AdminUserSkillManagement',
    component: () => import('@/components/Admin/UserSkillManagementPage.vue'),
    meta: { layout: 'admin', requiresAuth: true, role: ROLE_ADMIN }
  },
  {
    path: '/admin/matchings',
    name: 'AdminMatchingManagement',
    component: () => import('@/components/Admin/MatchingManagementPage.vue'),
    meta: { layout: 'admin', requiresAuth: true, role: ROLE_ADMIN }
  },
  {
    path: '/admin/career-advising',
    name: 'AdminCareerAdvisingManagement',
    component: () => import('@/components/Admin/CareerAdvisingManagementPage.vue'),
    meta: { layout: 'admin', requiresAuth: true, role: ROLE_ADMIN }
  },
  {
    path: '/admin/applications',
    name: 'AdminApplicationManagement',
    component: () => import('@/components/Admin/ApplicationManagementPage.vue'),
    meta: { layout: 'admin', requiresAuth: true, role: ROLE_ADMIN }
  },
  {
    path: '/admin/industries',
    name: 'IndustryManagement',
    component: () => import('@/components/Admin/IndustryManagementPage.vue'),
    meta: { layout: 'admin', requiresAuth: true, role: ROLE_ADMIN }
  },
  {
    path: '/admin/skills',
    name: 'SkillManagement',
    component: () => import('@/components/Admin/SkillManagementPage.vue'),
    meta: { layout: 'admin', requiresAuth: true, role: ROLE_ADMIN }
  },
  {
    path: '/admin/jobs',
    name: 'JobPostingsManagement',
    component: () => import('@/components/Admin/JobPostingsManagementPage.vue'),
    meta: { layout: 'admin', requiresAuth: true, role: ROLE_ADMIN }
  },
  {
    path: '/admin/stats',
    name: 'StatsManagement',
    component: () => import('@/components/Admin/StatsManagementPage.vue'),
    meta: { layout: 'admin', requiresAuth: true, role: ROLE_ADMIN }
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

  if (to.meta?.requiresAuth && !auth.isAuthenticated) {
    return {
      path: '/login',
      query: { redirect: to.fullPath }
    }
  }

  if (to.meta?.requiresAuth && auth.isAuthenticated) {
    try {
      await authService.getProfile()
    } catch (error) {
      if (error?.status === 401) {
        return '/'
      }
    }
  }

  if (to.meta?.requiresAuth && auth.isAuthenticated && to.meta?.role !== undefined && auth.role !== to.meta.role) {
    return getHomeByRole(auth.role)
  }

  return true
})

export default router
