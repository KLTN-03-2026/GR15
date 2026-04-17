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
      return '/employer/company'
    case ROLE_ADMIN:
      return '/admin/stats'
    case ROLE_CANDIDATE:
    default:
      return '/applications'
  }
}

const routes = [
  {
    path: '/',
    redirect: '/skills',
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/components/Guest/LoginPage.vue'),
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
    path: '/oauth/google/callback',
    name: 'GoogleAuthCallback',
    component: () => import('@/components/Guest/GoogleAuthCallbackPage.vue'),
    meta: { layout: 'auth', guestOnly: true },
  },
  {
    path: '/auth',
    redirect: '/login',
  },
  {
    path: '/employer/auth',
    redirect: '/login',
  },
  {
    path: '/employer/login',
    redirect: '/login',
  },
  {
    path: '/employer/register',
    redirect: '/register?role=employer',
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
    path: '/applications',
    name: 'Applications',
    component: () => import('@/components/Dashboard/ApplicationsPage.vue'),
    meta: { layout: 'dashboard', requiresAuth: true, role: ROLE_CANDIDATE },
  },
  {
    path: '/employer',
    redirect: '/employer/company',
  },
  {
    path: '/employer/company',
    name: 'EmployerCompany',
    component: () => import('@/components/Employer/EmployerCompanyPage.vue'),
    meta: { layout: 'employer', requiresAuth: true, role: ROLE_EMPLOYER },
  },
  {
    path: '/admin',
    redirect: '/admin/stats',
  },
  {
    path: '/admin/users',
    name: 'UserManagement',
    component: () => import('@/components/Admin/UserManagementPage.vue'),
    meta: { layout: 'admin', requiresAuth: true, role: ROLE_ADMIN },
  },
  {
    path: '/admin/companies',
    name: 'CompanyManagement',
    component: () => import('@/components/Admin/CompanyManagementPage.vue'),
    meta: { layout: 'admin', requiresAuth: true, role: ROLE_ADMIN },
  },
  {
    path: '/admin/profiles',
    name: 'AdminProfileManagement',
    component: () => import('@/components/Admin/ProfileManagementPage.vue'),
    meta: { layout: 'admin', requiresAuth: true, role: ROLE_ADMIN },
  },
  {
    path: '/admin/user-skills',
    name: 'AdminUserSkillManagement',
    component: () => import('@/components/Admin/UserSkillManagementPage.vue'),
    meta: { layout: 'admin', requiresAuth: true, role: ROLE_ADMIN },
  },
  {
    path: '/admin/applications',
    name: 'AdminApplicationManagement',
    component: () => import('@/components/Admin/ApplicationManagementPage.vue'),
    meta: { layout: 'admin', requiresAuth: true, role: ROLE_ADMIN },
  },
  {
    path: '/admin/skills',
    name: 'SkillManagement',
    component: () => import('@/components/Admin/SkillManagementPage.vue'),
    meta: { layout: 'admin', requiresAuth: true, role: ROLE_ADMIN },
  },
  {
    path: '/admin/stats',
    name: 'StatsManagement',
    component: () => import('@/components/Admin/StatsManagementPage.vue'),
    meta: { layout: 'admin', requiresAuth: true, role: ROLE_ADMIN },
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/skills',
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
        return '/skills'
      }
    }
  }

  if (to.meta?.requiresAuth && auth.isAuthenticated && to.meta?.role !== undefined && auth.role !== to.meta.role) {
    return getHomeByRole(auth.role)
  }

  return true
})

export default router
