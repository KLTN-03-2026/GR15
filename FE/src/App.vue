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

const route = useRoute()

const layoutComponent = computed(() => {
  const layout = route.meta?.layout || 'guest'
  switch (layout) {
    case 'auth': return AuthWrapper
    case 'dashboard': return DashboardWrapper
    default: return GuestWrapper
  }
})
</script>

<style scoped></style>
