<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import AppLogo from '@/components/AppLogo.vue'
import { RouterLink } from 'vue-router'
import { getStoredUser } from '@/utils/authStorage'
import { hasAdminPermission } from '@/constants/adminPermissions'
import { useNotify } from '@/composables/useNotify'

defineProps({
  collapsed: {
    type: Boolean,
    default: false,
  },
})

const currentUser = ref(getStoredUser())
const notify = useNotify()
const lockedMessage = 'Bạn không có quyền thực hiện chức năng này'

const syncCurrentUser = () => {
  currentUser.value = getStoredUser()
}

const canManageAdmins = computed(() =>
  Number(currentUser.value?.vai_tro) === 2 && currentUser.value?.cap_admin === 'super_admin'
)

const navigationItems = [
  { to: '/admin', icon: 'dashboard', label: 'Dashboard' },
  { to: '/admin/users', icon: 'group', label: 'Người dùng', permission: 'users' },
  { to: '/admin/companies', icon: 'domain', label: 'Công ty', permission: 'companies' },
  { to: '/admin/profiles', icon: 'description', label: 'Hồ sơ', permission: 'profiles' },
  { to: '/admin/user-skills', icon: 'psychology', label: 'Kỹ năng người dùng', permission: 'user_skills' },
  { to: '/admin/matchings', icon: 'compare_arrows', label: 'AI Matching', permission: 'matchings' },
  { to: '/admin/career-advising', icon: 'travel_explore', label: 'AI Advising', permission: 'career_advising' },
  { to: '/admin/ai-usage', icon: 'memory', label: 'AI Usage', permission: 'ai_usage' },
  { to: '/admin/billing', icon: 'payments', label: 'Billing', permission: 'billing' },
  { to: '/admin/applications', icon: 'assignment', label: 'Ứng tuyển', permission: 'applications' },
  { to: '/admin/skills', icon: 'bolt', label: 'Kỹ năng', permission: 'skills' },
  { to: '/admin/industries', icon: 'factory', label: 'Ngành nghề', permission: 'industries' },
  { to: '/admin/jobs', icon: 'work', label: 'Tin tuyển dụng', permission: 'jobs' },
  { to: '/admin/cv-templates', icon: 'palette', label: 'Template CV', permission: 'cv_templates' },
  { to: '/admin/audit-logs', icon: 'history', label: 'Nhật ký hệ thống', permission: 'audit_logs' },
  { to: '/admin/stats', icon: 'leaderboard', label: 'Báo cáo & phân tích', permission: 'stats' },
]

const visibleNavigationItems = computed(() =>
  navigationItems.filter((item) => item.to !== '/admin')
)

const canAccessItem = (item) => !item.permission || hasAdminPermission(currentUser.value, item.permission)

const showLockedNotice = () => {
  notify.warning(lockedMessage)
}

onMounted(() => {
  window.addEventListener('auth-changed', syncCurrentUser)
  window.addEventListener('admin-profile-updated', syncCurrentUser)
})

onBeforeUnmount(() => {
  window.removeEventListener('auth-changed', syncCurrentUser)
  window.removeEventListener('admin-profile-updated', syncCurrentUser)
})
</script>

<template>
  <aside
    class="sticky top-0 flex h-screen flex-col border-r border-slate-200/80 bg-white/95 backdrop-blur dark:border-slate-800 dark:bg-slate-950/90 transition-all duration-200"
    :class="collapsed ? 'w-24' : 'w-64'"
  >
    <div class="flex items-center gap-3 p-6" :class="collapsed ? 'justify-center' : ''">
      <AppLogo
        :show-text="!collapsed"
        size="sm"
        title="AI Recruitment"
        subtitle="Management Console"
      />
    </div>
    <nav class="flex-1 space-y-1 overflow-y-auto px-4">
      <RouterLink
        to="/admin"
        exact-active-class="active-nav"
        class="nav-link flex items-center gap-3 rounded-xl px-3 py-2.5 text-slate-600 transition-colors font-medium hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800"
        :class="collapsed ? 'justify-center' : ''"
        :title="collapsed ? 'Dashboard' : ''"
      >
        <span class="material-symbols-outlined text-[22px]">dashboard</span>
        <span v-if="!collapsed" class="text-sm">Dashboard</span>
      </RouterLink>
      <RouterLink v-if="canManageAdmins" to="/admin/admins" active-class="active-nav" class="nav-link flex items-center gap-3 rounded-xl px-3 py-2.5 text-slate-600 transition-colors font-medium hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800" :class="collapsed ? 'justify-center' : ''" :title="collapsed ? 'Quản lý admin' : ''">
        <span class="material-symbols-outlined text-[22px]">admin_panel_settings</span>
        <span v-if="!collapsed" class="text-sm">Quản lý admin</span>
      </RouterLink>
      <button
        v-else
        class="nav-link locked-nav flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left font-medium text-slate-400 transition-colors hover:bg-slate-50 dark:text-slate-600 dark:hover:bg-slate-800"
        :class="collapsed ? 'justify-center' : ''"
        :title="lockedMessage"
        type="button"
        @click="showLockedNotice"
      >
        <span class="material-symbols-outlined text-[22px]">admin_panel_settings</span>
        <span v-if="!collapsed" class="text-sm">Quản lý admin</span>
        <span v-if="!collapsed" class="material-symbols-outlined ml-auto text-[17px]">lock</span>
      </button>

      <template v-for="item in visibleNavigationItems" :key="item.to">
        <RouterLink
          v-if="canAccessItem(item)"
          :to="item.to"
          active-class="active-nav"
          class="nav-link flex items-center gap-3 rounded-xl px-3 py-2.5 text-slate-600 transition-colors font-medium hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800"
          :class="collapsed ? 'justify-center' : ''"
          :title="collapsed ? item.label : ''"
        >
          <span class="material-symbols-outlined text-[22px]">{{ item.icon }}</span>
          <span v-if="!collapsed" class="text-sm">{{ item.label }}</span>
        </RouterLink>
        <button
          v-else
          class="nav-link locked-nav flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left font-medium text-slate-400 transition-colors hover:bg-slate-50 dark:text-slate-600 dark:hover:bg-slate-800"
          :class="collapsed ? 'justify-center' : ''"
          :title="lockedMessage"
          type="button"
          @click="showLockedNotice"
        >
          <span class="material-symbols-outlined text-[22px]">{{ item.icon }}</span>
          <span v-if="!collapsed" class="text-sm">{{ item.label }}</span>
          <span v-if="!collapsed" class="material-symbols-outlined ml-auto text-[17px]">lock</span>
        </button>
      </template>
    </nav>
  </aside>
</template>

<style scoped>
.nav-link.active-nav {
  background-color: rgb(36 99 235 / 0.1);
  color: #2463eb;
}

.nav-link.active-nav:hover {
  background-color: rgb(36 99 235 / 0.15);
}

.locked-nav {
  cursor: not-allowed;
}
</style>
