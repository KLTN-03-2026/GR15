import { createRouter, createWebHistory } from 'vue-router'
import { getAuthToken, getStoredUser } from '@/utils/authStorage'

const ROLE_CANDIDATE = 0
const ROLE_ADMIN = 2

const getAuthState = () => {
  const token = getAuthToken()
  const user = getStoredUser()
  const role = user?.vai_tro !== undefined && user?.vai_tro !== null ? Number(user.vai_tro) : null

  return {
    token,
    user,
    role,
    isAuthenticated: Boolean(token && user),
  }
}

const getHomeByRole = (role) => {
  switch (role) {
    case ROLE_ADMIN:
      return '/admin/matchings'
    case ROLE_CANDIDATE:
    default:
      return '/dashboard'
  }
}

const routes = [
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
    meta: { layout: 'auth' }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/components/Guest/RegisterPage.vue'),
    meta: { layout: 'auth' }
  },
  {
    path: '/auth',
    redirect: '/login'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
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
    path: '/my-skills',
    name: 'MySkills',
    component: () => import('@/components/Dashboard/MySkillsPage.vue'),
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
  {
    path: '/admin/matchings',
    name: 'AdminMatchingManagement',
    component: () => import('@/components/Admin/MatchingManagementPage.vue'),
    meta: { layout: 'dashboard', requiresAuth: true, role: ROLE_ADMIN }
  },
  {
    path: '/admin',
    redirect: '/admin/matchings'
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

router.beforeEach((to) => {
  const auth = getAuthState()
  const role = Number(auth.role ?? ROLE_CANDIDATE)

  if (to.meta?.requiresAuth && !auth.isAuthenticated) {
    return {
      path: '/login',
      query: { redirect: to.fullPath },
    }
  }

  if ((to.path === '/login' || to.path === '/register') && auth.isAuthenticated) {
    return getHomeByRole(role)
  }

  if (to.meta?.role !== undefined && role !== Number(to.meta.role)) {
    return getHomeByRole(role)
  }
})

export default router
