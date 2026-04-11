<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import GuestWrapper from '@/layouts/wrapper/GuestLayout.vue'
import AuthWrapper from '@/layouts/wrapper/AuthLayout.vue'
import DashboardWrapper from '@/layouts/wrapper/DashboardLayout.vue'
import AppNotificationHost from '@/components/AppNotificationHost.vue'
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
        await router.replace('/login')
      }
    }
  } finally {
    isCheckingSession = false
  }
}

const handleAuthInvalidated = async () => {
  if (route.meta?.requiresAuth) {
    await router.replace('/login')
  }
}

onMounted(() => {
  window.addEventListener('focus', forceLogoutIfSessionExpired)
  window.addEventListener('auth-invalidated', handleAuthInvalidated)

  sessionCheckInterval = window.setInterval(() => {
    void forceLogoutIfSessionExpired()
  }, 20000)
})

onUnmounted(() => {
  window.removeEventListener('focus', forceLogoutIfSessionExpired)
  window.removeEventListener('auth-invalidated', handleAuthInvalidated)

  if (sessionCheckInterval) {
    window.clearInterval(sessionCheckInterval)
  }
})
</script>

<template>
  <AppNotificationHost />
  <component :is="layoutComponent">
    <RouterView />
  </component>
</template>
