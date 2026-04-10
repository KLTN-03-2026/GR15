import { createRouter, createWebHistory } from 'vue-router'

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
    component: () => import('@/components/Guest/AuthPage.vue'),
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
    name: 'Auth',
    component: () => import('@/components/Guest/AuthPage.vue'),
    meta: { layout: 'guest' }
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

export default router
