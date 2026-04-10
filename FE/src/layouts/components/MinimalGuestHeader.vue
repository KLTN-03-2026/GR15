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

const isAuthenticatedUser = computed(() => hasAuthToken.value && Boolean(currentUser.value))
const displayName = computed(() => currentUser.value?.ho_ten || currentUser.value?.email || 'Tai khoan')
const avatarLetter = computed(() => displayName.value.trim().charAt(0).toUpperCase() || 'U')

watch(
  () => route.fullPath,
  () => {
    refreshAuthState()
    userMenuOpen.value = false
  },
  { immediate: true }
)

const handleClickOutside = (event) => {
  if (userMenuRef.value && !userMenuRef.value.contains(event.target)) {
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
    notify.success('Dang xuat thanh cong.')
  } catch (error) {
    notify.apiError(error, 'Khong the dang xuat khoi he thong.')
  }
}
</script>

<template>
  <header class="sticky top-0 z-50 w-full border-b border-slate-200/80 bg-white/90 backdrop-blur-md">
    <div class="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6">
      <RouterLink to="/skills" class="flex items-center gap-3 text-[#2463eb]">
        <AppLogo subtitle="Skill & Application Portal" />
      </RouterLink>

      <nav class="hidden items-center gap-2 rounded-full border border-slate-200 bg-white px-2 py-2 shadow-sm lg:flex">
        <RouterLink to="/register" class="rounded-full px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100 hover:text-[#2463eb]">
          Dang ky
        </RouterLink>
        <RouterLink to="/skills" class="rounded-full px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100 hover:text-[#2463eb]">
          Danh sach ky nang
        </RouterLink>
        <RouterLink to="/applications" class="rounded-full px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100 hover:text-[#2463eb]">
          Theo doi don
        </RouterLink>
      </nav>

      <div class="flex items-center gap-3">
        <template v-if="isAuthenticatedUser">
          <div ref="userMenuRef" class="relative">
            <button
              class="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white px-3 py-2 text-sm shadow-sm transition hover:border-blue-200 hover:bg-blue-50"
              type="button"
              @click.stop="userMenuOpen = !userMenuOpen"
            >
              <span class="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 text-xs font-bold text-blue-700">
                {{ avatarLetter }}
              </span>
              <span class="hidden max-w-[160px] truncate font-semibold text-slate-700 sm:block">{{ displayName }}</span>
              <span class="material-symbols-outlined text-[18px] text-slate-400">
                {{ userMenuOpen ? 'expand_less' : 'expand_more' }}
              </span>
            </button>

            <div
              v-if="userMenuOpen"
              class="absolute right-0 top-[calc(100%+10px)] z-50 w-64 overflow-hidden rounded-2xl border border-slate-200 bg-white p-2 shadow-2xl shadow-slate-200/70"
            >
              <div class="border-b border-slate-100 px-3 pb-3 pt-2">
                <p class="truncate text-sm font-bold text-slate-900">{{ displayName }}</p>
                <p class="mt-1 text-xs text-slate-500">Tai khoan dang dang nhap</p>
              </div>

              <div class="pt-2">
                <RouterLink
                  to="/applications"
                  class="flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
                  @click="userMenuOpen = false"
                >
                  <span class="material-symbols-outlined text-[18px]">dashboard</span>
                  <span>Theo doi don ung tuyen</span>
                </RouterLink>

                <button
                  class="mt-1 flex w-full items-center gap-3 rounded-xl px-3 py-2 text-sm font-semibold text-red-500 transition hover:bg-red-50 disabled:opacity-60"
                  type="button"
                  :disabled="isLoading"
                  @click="handleLogout"
                >
                  <span class="material-symbols-outlined text-[18px]">logout</span>
                  <span>{{ isLoading ? 'Dang dang xuat...' : 'Dang xuat' }}</span>
                </button>
              </div>
            </div>
          </div>
        </template>

        <template v-else>
          <RouterLink to="/login" class="hidden h-10 items-center justify-center rounded-2xl border border-slate-200 bg-white px-4 text-sm font-bold text-slate-700 shadow-sm transition-all hover:border-slate-300 hover:bg-slate-50 sm:flex">
            Dang nhap
          </RouterLink>
          <RouterLink to="/register" class="flex h-10 items-center justify-center rounded-2xl bg-[#2463eb] px-6 text-sm font-bold text-white shadow-lg shadow-[#2463eb]/20 transition-all hover:bg-blue-700">
            Dang ky
          </RouterLink>
        </template>
      </div>
    </div>
  </header>
</template>
