import { createRouter, createWebHistory } from 'vue-router'
import { authService } from '@/services/api'
import { getAuthToken, getStoredUser } from '@/utils/authStorage'

const ROLE_CANDIDATE = 0

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

const routes = [
  {
    path: '/',
    name: 'Landing',
    component: () => import('@/components/Guest/LandingPage.vue'),
    meta: { layout: 'guest' },
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/components/Guest/AuthPage.vue'),
    meta: { layout: 'auth', guestOnly: true },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/components/Guest/RegisterPage.vue'),
    meta: { layout: 'auth', guestOnly: true },
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('@/components/Guest/ForgotPasswordPage.vue'),
    meta: { layout: 'auth', guestOnly: true },
  },
  {
    path: '/reset-password',
    name: 'ResetPassword',
    component: () => import('@/components/Guest/ResetPasswordPage.vue'),
    meta: { layout: 'auth', guestOnly: true },
  },
  {
    path: '/jobs',
    name: 'JobSearch',
    component: () => import('@/components/Guest/JobSearchPage.vue'),
    meta: { layout: 'guest' },
  },
  {
    path: '/jobs/:id',
    name: 'JobDetail',
    component: () => import('@/components/Guest/JobDetailPage.vue'),
    meta: { layout: 'guest' },
  },
  {
    path: '/companies',
    name: 'CompanyList',
    component: () => import('@/components/Guest/CompanyListPage.vue'),
    meta: { layout: 'guest' },
  },
  {
    path: '/companies/:id',
    name: 'CompanyDetail',
    component: () => import('@/components/Guest/CompanyDetailPage.vue'),
    meta: { layout: 'guest' },
  },
  {
    path: '/industries',
    name: 'IndustryList',
    component: () => import('@/components/Guest/IndustryListPage.vue'),
    meta: { layout: 'guest' },
  },
  {
    path: '/industries/:id',
    name: 'IndustryDetail',
    component: () => import('@/components/Guest/IndustryDetailPage.vue'),
    meta: { layout: 'guest' },
  },
  {
    path: '/skills',
    name: 'SkillList',
    component: () => import('@/components/Guest/SkillListPage.vue'),
    meta: { layout: 'guest' },
  },
  {
    path: '/skills/:id',
    name: 'SkillDetail',
    component: () => import('@/components/Guest/SkillDetailPage.vue'),
    meta: { layout: 'guest' },
  },
  {
    path: '/dashboard',
    name: 'SeekerDashboard',
    component: () => import('@/components/Dashboard/SeekerDashboardPage.vue'),
    meta: { layout: 'dashboard', requiresAuth: true, role: ROLE_CANDIDATE },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/components/Dashboard/ProfilePage.vue'),
    meta: { layout: 'dashboard', requiresAuth: true, role: ROLE_CANDIDATE },
  },
  {
    path: '/my-cv',
    name: 'MyCv',
    component: () => import('@/components/Dashboard/MyCvPage.vue'),
    meta: { layout: 'dashboard', requiresAuth: true, role: ROLE_CANDIDATE },
  },
  {
    path: '/saved-jobs',
    name: 'SavedJobs',
    component: () => import('@/components/Dashboard/SavedJobsPage.vue'),
    meta: { layout: 'dashboard', requiresAuth: true, role: ROLE_CANDIDATE },
  },
  {
    path: '/matched-jobs',
    name: 'MatchedJobs',
    component: () => import('@/components/Dashboard/MatchedJobsPage.vue'),
    meta: { layout: 'dashboard', requiresAuth: true, role: ROLE_CANDIDATE },
  },
  {
    path: '/applications',
    name: 'Applications',
    component: () => import('@/components/Dashboard/ApplicationsPage.vue'),
    meta: { layout: 'dashboard', requiresAuth: true, role: ROLE_CANDIDATE },
  },
  {
    path: '/my-skills',
    name: 'MySkills',
    component: () => import('@/components/Dashboard/MySkillsPage.vue'),
    meta: { layout: 'dashboard', requiresAuth: true, role: ROLE_CANDIDATE },
  },
  {
    path: '/career-report',
    name: 'CareerReport',
    component: () => import('@/components/Dashboard/CareerReportPage.vue'),
    meta: { layout: 'dashboard', requiresAuth: true, role: ROLE_CANDIDATE },
  },
  {
    path: '/auth',
    redirect: '/login',
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

router.beforeEach(async (to) => {
  const auth = getAuthState()

  if (to.meta?.guestOnly && auth.isAuthenticated) {
    return '/dashboard'
  }

  if (to.meta?.requiresAuth && !auth.isAuthenticated) {
    return {
      path: '/login',
      query: { redirect: to.fullPath },
    }
  }

  if (to.meta?.requiresAuth && auth.isAuthenticated) {
    try {
      await authService.getProfile()
    } catch (error) {
      if (error?.status === 401) {
        return '/login'
      }
    }
  }

  if (to.meta?.requiresAuth && auth.role !== to.meta.role) {
    return '/'
  }

  return true
})

export default router
