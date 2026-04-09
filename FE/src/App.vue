<template>
  <component :is="layoutComponent">
    <RouterView />
  </component>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import GuestWrapper from '@/layouts/wrapper/GuestLayout.vue'
import AuthWrapper from '@/layouts/wrapper/AuthLayout.vue'
import DashboardWrapper from '@/layouts/wrapper/DashboardLayout.vue'
import AdminWrapper from '@/layouts/wrapper/AdminLayout.vue'
import EmployerWrapper from '@/layouts/wrapper/EmployerLayout.vue'

const route = useRoute()

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
</script>

<style scoped></style>
