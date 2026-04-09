<template>
  <aside class="w-64 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex flex-col sticky top-0 h-screen">
    <div class="p-6 flex items-center gap-3">
      <div class="size-10 bg-[#2463eb] rounded-xl flex items-center justify-center text-white">
        <span class="material-symbols-outlined">analytics</span>
      </div>
      <div>
        <h1 class="font-bold text-slate-900 dark:text-white leading-tight">Quản trị hệ thống</h1>
        <p class="text-xs text-slate-500 dark:text-slate-400">Bảng điều khiển quản lý</p>
      </div>
    </div>
    <nav class="flex-1 px-4 space-y-1">
      <RouterLink to="/admin" exact-active-class="active-nav" class="nav-link flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors font-medium">
        <span class="material-symbols-outlined text-[22px]">dashboard</span>
        <span class="text-sm">Tổng quan</span>
      </RouterLink>
      <RouterLink to="/admin/users" active-class="active-nav" class="nav-link flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors font-medium">
        <span class="material-symbols-outlined text-[22px]">group</span>
        <span class="text-sm">Người dùng</span>
      </RouterLink>
      <RouterLink to="/admin/companies" active-class="active-nav" class="nav-link flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors font-medium">
        <span class="material-symbols-outlined text-[22px]">domain</span>
        <span class="text-sm">Công ty</span>
      </RouterLink>
      <RouterLink to="/admin/skills" active-class="active-nav" class="nav-link flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors font-medium">
        <span class="material-symbols-outlined text-[22px]">bolt</span>
        <span class="text-sm">Kỹ năng</span>
      </RouterLink>
      <RouterLink to="/admin/industries" active-class="active-nav" class="nav-link flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors font-medium">
        <span class="material-symbols-outlined text-[22px]">factory</span>
        <span class="text-sm">Ngành nghề</span>
      </RouterLink>
      <RouterLink to="/admin/jobs" active-class="active-nav" class="nav-link flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors font-medium">
        <span class="material-symbols-outlined text-[22px]">work</span>
        <span class="text-sm">Tin tuyển dụng</span>
      </RouterLink>
      <RouterLink to="/admin/stats" active-class="active-nav" class="nav-link flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors font-medium">
        <span class="material-symbols-outlined text-[22px]">leaderboard</span>
        <span class="text-sm">Thống kê</span>
      </RouterLink>
    </nav>
    <div class="p-4 border-t border-slate-200 dark:border-slate-800">
      <div ref="menuRef" class="relative">
        <div class="flex items-center gap-3 rounded-lg p-2 hover:bg-slate-50 dark:hover:bg-slate-800">
          <div class="flex size-8 items-center justify-center overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
            <img
              v-if="adminAvatar && !avatarLoadFailed"
              :src="adminAvatar"
              :alt="adminName"
              class="h-full w-full object-cover"
              @error="handleAvatarError"
            />
            <span v-else class="text-xs font-bold text-slate-700 dark:text-slate-200">
              {{ adminInitials }}
            </span>
          </div>
          <div class="flex-1 overflow-hidden">
            <p class="truncate text-sm font-semibold">{{ adminName }}</p>
            <p class="truncate text-xs text-slate-500">{{ adminRole }}</p>
          </div>
          <button
            type="button"
            @click.stop="toggleMenu"
            class="flex h-9 w-9 items-center justify-center rounded-lg text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-800"
            aria-label="Mở menu quản trị"
          >
            <span class="material-symbols-outlined">settings</span>
          </button>
        </div>

        <div
          v-if="isMenuOpen"
          class="absolute bottom-full right-0 mb-2 w-44 overflow-hidden rounded-xl border border-slate-200 bg-white py-2 shadow-lg shadow-slate-900/10 dark:border-slate-800 dark:bg-slate-900"
        >
          <button
            type="button"
            @click="goToProfile"
            class="flex w-full items-center gap-3 px-4 py-2.5 text-left text-sm font-medium text-slate-600 transition-colors hover:bg-slate-50 hover:text-slate-900 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-white"
          >
            <span class="material-symbols-outlined text-[20px]">person</span>
            <span>Profile</span>
          </button>
          <button
            type="button"
            @click="handleLogout"
            class="flex w-full items-center gap-3 px-4 py-2.5 text-left text-sm font-medium text-red-600 transition-colors hover:bg-red-50 dark:hover:bg-red-950/30"
          >
            <span class="material-symbols-outlined text-[20px]">logout</span>
            <span>Đăng xuất</span>
          </button>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { authService } from '@/services/api'
import { buildStorageAssetCandidates } from '@/utils/media'

const router = useRouter()
const adminUser = ref(null)
const isMenuOpen = ref(false)
const menuRef = ref(null)
const avatarCandidates = ref([])
const avatarCandidateIndex = ref(0)
const avatarLoadFailed = ref(false)

const normalizeAdminProfile = (payload) => {
  const profile = payload?.data ?? payload ?? {}

  return {
    ...adminUser.value,
    ...profile,
    ho_ten: profile.ho_ten ?? profile.name ?? profile.ten ?? adminUser.value?.ho_ten,
    ten_vai_tro: profile.ten_vai_tro ?? profile.vai_tro ?? adminUser.value?.ten_vai_tro,
    anh_dai_dien: profile.anh_dai_dien ?? profile.avatarPath ?? profile.avatar ?? profile.hinh_anh ?? adminUser.value?.anh_dai_dien,
    anh_dai_dien_url: profile.anh_dai_dien_url ?? profile.avatar ?? adminUser.value?.anh_dai_dien_url,
    anh_dai_dien_goc: profile.anh_dai_dien_goc ?? profile.avatarPath ?? profile.anh_dai_dien ?? profile.avatar ?? profile.hinh_anh ?? adminUser.value?.anh_dai_dien_goc
  }
}

const loadAdminUser = () => {
  const storedUser = localStorage.getItem('admin_user')

  if (!storedUser) {
    adminUser.value = null
    return
  }

  try {
    adminUser.value = JSON.parse(storedUser)
  } catch {
    adminUser.value = null
  }
}

const syncAdminProfile = async () => {
  try {
    const response = await authService.getProfile()
    const normalizedProfile = normalizeAdminProfile(response)

    adminUser.value = normalizedProfile
    localStorage.setItem('admin_user', JSON.stringify(normalizedProfile))
  } catch (error) {
    console.error('Unable to sync admin profile:', error)
  }
}

const handleAdminProfileUpdated = (event) => {
  const updatedProfile = event.detail

  if (!updatedProfile) {
    return
  }

  const normalizedProfile = normalizeAdminProfile(updatedProfile)
  adminUser.value = normalizedProfile
  localStorage.setItem('admin_user', JSON.stringify(normalizedProfile))
}

onMounted(() => {
  loadAdminUser()
  syncAdminProfile()
  document.addEventListener('click', handleClickOutside)
  window.addEventListener('admin-profile-updated', handleAdminProfileUpdated)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
  window.removeEventListener('admin-profile-updated', handleAdminProfileUpdated)
})

watch(
  () => adminUser.value,
  (user) => {
    const rawAvatar =
      user?.anh_dai_dien_goc ||
      user?.anh_dai_dien ||
      user?.anh_dai_dien_url ||
      user?.avatar ||
      user?.hinh_anh ||
      ''

    avatarCandidates.value = buildStorageAssetCandidates(rawAvatar)
    avatarCandidateIndex.value = 0
    avatarLoadFailed.value = false
  },
  { immediate: true }
)

const adminName = computed(() => {
  return (
    adminUser.value?.ho_ten ||
    adminUser.value?.name ||
    adminUser.value?.ten ||
    'Quản trị viên'
  )
})

const adminRole = computed(() => {
  const role = adminUser.value?.ten_vai_tro ?? adminUser.value?.vai_tro

  if (role === 2 || role === '2' || String(role || '').toLowerCase() === 'admin') {
    return 'Quản trị viên'
  }

  return role || 'Quản trị viên'
})

const adminAvatar = computed(() => {
  return avatarCandidates.value[avatarCandidateIndex.value] || adminUser.value?.anh_dai_dien_url || ''
})

const adminInitials = computed(() => {
  const words = adminName.value
    .trim()
    .split(/\s+/)
    .filter(Boolean)

  if (!words.length) {
    return 'A'
  }

  if (words.length === 1) {
    return words[0].charAt(0).toUpperCase()
  }

  return `${words[0].charAt(0)}${words[words.length - 1].charAt(0)}`.toUpperCase()
})

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
}

const closeMenu = () => {
  isMenuOpen.value = false
}

const handleClickOutside = (event) => {
  if (!menuRef.value?.contains(event.target)) {
    closeMenu()
  }
}

const handleAvatarError = () => {
  if (avatarCandidateIndex.value < avatarCandidates.value.length - 1) {
    avatarCandidateIndex.value += 1
    return
  }

  avatarLoadFailed.value = true
}

const goToProfile = async () => {
  closeMenu()
  await router.push('/admin/profile')
}

const handleLogout = async () => {
  closeMenu()

  try {
    await authService.logout()
  } catch (error) {
    console.error('Admin logout failed:', error)
  } finally {
    localStorage.removeItem('access_token')
    localStorage.removeItem('admin_user')
    localStorage.removeItem('user_role')
    await router.push('/admin/login')
  }
}
</script>

<style scoped>
.nav-link.active-nav {
  background-color: rgb(36 99 235 / 0.1);
  color: #2463eb;
}

.nav-link.active-nav:hover {
  background-color: rgb(36 99 235 / 0.15);
}
</style>
