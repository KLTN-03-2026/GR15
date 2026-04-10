<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { getStoredUser } from '@/utils/authStorage'

const router = useRouter()
const { logout, isLoading } = useAuth()

const currentUser = computed(() => getStoredUser())
const displayName = computed(() => currentUser.value?.ho_ten || 'Ứng viên')

const handleLogout = async () => {
  await logout()
}
</script>

<template>
  <header class="sticky top-0 z-10 border-b border-slate-200 bg-white/95 backdrop-blur">
    <div class="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
      <div>
        <p class="text-xs uppercase tracking-[0.3em] text-blue-600">Candidate Space</p>
        <h1 class="text-lg font-semibold text-slate-900">{{ displayName }}</h1>
      </div>

      <div class="flex items-center gap-3">
        <button
          type="button"
          class="rounded-xl border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
          @click="router.push('/matched-jobs')"
        >
          Matching
        </button>
        <button
          type="button"
          class="rounded-xl bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-60"
          :disabled="isLoading"
          @click="handleLogout"
        >
          {{ isLoading ? 'Đang đăng xuất...' : 'Đăng xuất' }}
        </button>
      </div>
    </div>
  </header>
</template>
