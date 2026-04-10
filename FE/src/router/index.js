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

const getHomeByRole = (role) => {
  return role === ROLE_CANDIDATE ? '/applications' : '/skills'
}

const routes = [
  {
    path: '/',
    redirect: '/skills'
  },
  {
    path: '/skills',
    name: 'SkillList',
    component: () => import('@/components/Guest/CompactSkillListPage.vue'),
    meta: { layout: 'guest' }
  },
  {
    path: '/skills/:id',
    name: 'SkillDetail',
    component: () => import('@/components/Guest/CompactSkillDetailPage.vue'),
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
    path: '/applications',
    name: 'Applications',
    component: () => import('@/components/Dashboard/CompactApplicationsPage.vue'),
    meta: { layout: 'dashboard', requiresAuth: true, role: ROLE_CANDIDATE }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/skills'
  }
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
