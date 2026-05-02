<script setup>
import AppLogo from '@/components/AppLogo.vue'
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useNotify } from '@/composables/useNotify'
import { getAuthToken, getStoredUser } from '@/utils/authStorage'

const { logout, isLoading } = useAuth()
const notify = useNotify()
const route = useRoute()
const userMenuOpen = ref(false)
const userMenuRef = ref(null)

const authVersion = ref(0)
const refreshAuthState = () => {
  authVersion.value += 1
}

const hasAuthToken = computed(() => {
  authVersion.value
  return Boolean(getAuthToken())
})

const currentUser = computed(() => {
  authVersion.value
  return getStoredUser()
})
const currentRole = computed(() => {
  const role = currentUser.value?.vai_tro
  if (role === undefined || role === null) return null
  const normalizedRole = Number(role)
  return Number.isNaN(normalizedRole) ? null : normalizedRole
})
const isAuthenticatedUser = computed(() => hasAuthToken.value && currentRole.value !== undefined && currentRole.value !== null)
const displayName = computed(() => currentUser.value?.ho_ten || currentUser.value?.email || 'Tài khoản')
const avatarLetter = computed(() => displayName.value.trim().charAt(0).toUpperCase() || 'U')
const accountLabel = computed(() => {
  if (currentRole.value === 1) return 'Nhà tuyển dụng đang đăng nhập'
  if (currentRole.value === 2) return 'Quản trị viên đang đăng nhập'
  return 'Ứng viên đang đăng nhập'
})
const dashboardLink = computed(() => {
  if (currentRole.value === 1) return '/employer'
  if (currentRole.value === 2) return '/admin'
  return '/dashboard'
})
const dashboardText = computed(() => {
  if (currentRole.value === 1) return 'Vào dashboard tuyển dụng'
  if (currentRole.value === 2) return 'Vào trang quản trị'
  return 'Về trang chủ ứng viên'
})

watch(
  () => route.fullPath,
  () => {
    refreshAuthState()
    userMenuOpen.value = false
  },
  { immediate: true }
)

const handleClickOutside = (event) => {
  if (!userMenuRef.value) return
  if (!userMenuRef.value.contains(event.target)) {
    userMenuOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  window.addEventListener('auth-changed', refreshAuthState)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
  window.removeEventListener('auth-changed', refreshAuthState)
})

const handleLogout = async () => {
  try {
    await logout()
    refreshAuthState()
    userMenuOpen.value = false
    notify.success('Đăng xuất thành công.')
  } catch (error) {
    notify.apiError(error, 'Không thể đăng xuất khỏi hệ thống.')
  }
}
</script>

<template>
  <header class="sticky top-0 z-50 w-full border-b border-slate-200/80 bg-white/85 backdrop-blur-md dark:border-slate-800 dark:bg-[#111621]/85">
    <div class="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6">
      <RouterLink to="/" class="flex items-center gap-3 text-[#2463eb]">
        <AppLogo subtitle="Career Intelligence Platform" />
      </RouterLink>
      <nav class="hidden lg:flex items-center gap-2 rounded-full border border-slate-200 bg-white/80 px-2 py-2 shadow-sm dark:border-slate-700 dark:bg-slate-900/80">
        <RouterLink to="/" class="rounded-full px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100 hover:text-[#2463eb] dark:text-slate-300 dark:hover:bg-slate-800">Trang chủ</RouterLink>
        <RouterLink to="/jobs" class="rounded-full px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100 hover:text-[#2463eb] dark:text-slate-300 dark:hover:bg-slate-800">Việc làm</RouterLink>
        <RouterLink to="/companies" class="rounded-full px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100 hover:text-[#2463eb] dark:text-slate-300 dark:hover:bg-slate-800">Doanh nghiệp</RouterLink>
        <RouterLink to="/industries" class="rounded-full px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100 hover:text-[#2463eb] dark:text-slate-300 dark:hover:bg-slate-800">Ngành nghề</RouterLink>
        <RouterLink to="/skills" class="rounded-full px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100 hover:text-[#2463eb] dark:text-slate-300 dark:hover:bg-slate-800">Kỹ năng</RouterLink>
        <!-- <RouterLink to="/ai-career" class="text-sm font-medium hover:text-[#2463eb] transition-colors">Tư vấn nghề nghiệp AI</RouterLink> -->
      </nav>
      <div class="flex items-center gap-3">
        <template v-if="isAuthenticatedUser">
          <div ref="userMenuRef" class="relative">
            <button
              class="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white px-3 py-2 text-sm shadow-sm transition hover:border-blue-200 hover:bg-blue-50 dark:border-slate-700 dark:bg-slate-900 dark:hover:bg-slate-800"
              type="button"
              @click.stop="userMenuOpen = !userMenuOpen"
            >
              <span class="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 text-xs font-bold text-blue-700 dark:bg-slate-800 dark:text-slate-200">
                {{ avatarLetter }}
              </span>
              <span class="hidden max-w-[160px] truncate font-semibold text-slate-700 dark:text-slate-200 sm:block">{{ displayName }}</span>
              <span class="material-symbols-outlined text-[18px] text-slate-400">
                {{ userMenuOpen ? 'expand_less' : 'expand_more' }}
              </span>
            </button>

            <div
              v-if="userMenuOpen"
              class="absolute right-0 top-[calc(100%+10px)] z-50 w-56 overflow-hidden rounded-2xl border border-slate-200 bg-white p-2 shadow-2xl shadow-slate-200/70 dark:border-slate-700 dark:bg-slate-900 dark:shadow-slate-950/40"
            >
              <div class="border-b border-slate-100 px-3 pb-3 pt-2 dark:border-slate-800">
                <p class="truncate text-sm font-bold text-slate-900 dark:text-white">{{ displayName }}</p>
                <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">{{ accountLabel }}</p>
              </div>

              <div class="pt-2">
                <RouterLink
                  :to="dashboardLink"
                  class="flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 dark:text-slate-200 dark:hover:bg-slate-800"
                  @click="userMenuOpen = false"
                >
                  <span class="material-symbols-outlined text-[18px]">dashboard</span>
                  <span>{{ dashboardText }}</span>
                </RouterLink>

                <button
                  class="mt-1 flex w-full items-center gap-3 rounded-xl px-3 py-2 text-sm font-semibold text-red-500 transition hover:bg-red-50 dark:hover:bg-red-900/10 disabled:opacity-60"
                  type="button"
                  :disabled="isLoading"
                  @click="handleLogout"
                >
                  <span class="material-symbols-outlined text-[18px]">logout</span>
                  <span>{{ isLoading ? 'Đang đăng xuất...' : 'Đăng xuất' }}</span>
                </button>
              </div>
            </div>
          </div>
        </template>
        <template v-else>
          <RouterLink to="/login" class="hidden h-10 items-center justify-center rounded-2xl border border-slate-200 bg-white px-4 text-sm font-bold text-slate-700 shadow-sm transition-all hover:border-slate-300 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800 sm:flex">
            Đăng nhập
          </RouterLink>
          <RouterLink to="/register" class="flex h-10 items-center justify-center rounded-2xl bg-[#2463eb] px-6 text-sm font-bold text-white shadow-lg shadow-[#2463eb]/20 transition-all hover:bg-blue-700">
            Đăng ký
          </RouterLink>
        </template>
      </div>
    </div>
  </header>
</template>
