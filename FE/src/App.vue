<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import GuestWrapper from '@/layouts/wrapper/GuestLayout.vue'
import AuthWrapper from '@/layouts/wrapper/AuthLayout.vue'
import DashboardWrapper from '@/layouts/wrapper/DashboardLayout.vue'
import AdminWrapper from '@/layouts/wrapper/AdminLayout.vue'
import EmployerWrapper from '@/layouts/wrapper/EmployerLayout.vue'
import { authService } from '@/services/api'
import { clearAuthStorage, getAuthToken } from '@/utils/authStorage'

const route = useRoute()
const router = useRouter()
let sessionCheckInterval = null
let isCheckingSession = false

const layoutComponent = computed(() => {
  const layout = route.meta?.layout || 'guest'
  switch (layout) {
    case 'auth': return AuthWrapper
    case 'dashboard': return DashboardWrapper
    case 'admin': return AdminWrapper
    case 'employer': return EmployerWrapper
    default: return GuestWrapper
  }
})

const forceLogoutIfSessionExpired = async () => {
  if (isCheckingSession || !getAuthToken()) return

  isCheckingSession = true

  try {
    await authService.getProfile()
  } catch (error) {
    if (error?.status === 401) {
      clearAuthStorage()

      if (route.meta?.requiresAuth) {
        await router.replace('/')
      }
    }
  } finally {
    isCheckingSession = false
  }
}

const handleVisibilityChange = async () => {
  if (!document.hidden) {
    await forceLogoutIfSessionExpired()
  }
}

const handleAuthInvalidated = async () => {
  if (route.meta?.requiresAuth) {
    await router.replace('/')
  }
}

onMounted(() => {
  window.addEventListener('focus', forceLogoutIfSessionExpired)
  window.addEventListener('auth-invalidated', handleAuthInvalidated)
  document.addEventListener('visibilitychange', handleVisibilityChange)

  sessionCheckInterval = window.setInterval(() => {
    void forceLogoutIfSessionExpired()
  }, 15000)

  void forceLogoutIfSessionExpired()
})

onUnmounted(() => {
  window.removeEventListener('focus', forceLogoutIfSessionExpired)
  window.removeEventListener('auth-invalidated', handleAuthInvalidated)
  document.removeEventListener('visibilitychange', handleVisibilityChange)

  if (sessionCheckInterval) {
    window.clearInterval(sessionCheckInterval)
  }
})
</script>

<template>
  <component :is="layoutComponent">
    <RouterView />
  </component>
</template>

<style scoped></style>
