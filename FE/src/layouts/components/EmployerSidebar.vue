<script setup>
import AppLogo from '@/components/AppLogo.vue'
import { computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { getStoredEmployer } from '@/utils/authStorage'
import { useEmployerCompanyPermissions } from '@/composables/useEmployerCompanyPermissions'
import { useNotify } from '@/composables/useNotify'

defineProps({
  collapsed: {
    type: Boolean,
    default: false,
  },
})

const companyLabel = computed(() => {
  const employer = getStoredEmployer()
  return employer?.ho_ten || employer?.email || 'Nhà tuyển dụng'
})

const companyLetter = computed(() => companyLabel.value.trim().charAt(0).toUpperCase() || 'N')
const notify = useNotify()
const lockedMessage = 'Bạn không có quyền thực hiện chức năng này'
const {
  permissions,
  permissionsLoaded,
  permissionsLoading,
  ensurePermissionsLoaded,
} = useEmployerCompanyPermissions()

const navItems = computed(() => [
  {
    key: 'dashboard',
    to: '/employer',
    icon: 'dashboard',
    label: 'Dashboard',
    exact: true,
  },
  {
    key: 'jobs',
    to: '/employer/jobs',
    icon: 'work',
    label: 'Tin tuyển dụng',
    permission: 'jobs',
  },
  {
    key: 'candidates',
    to: '/employer/candidates',
    icon: 'group',
    label: 'Ứng viên',
    permission: 'applications',
  },
  {
    key: 'interviews',
    to: '/employer/interviews',
    icon: 'calendar_today',
    label: 'Phỏng vấn',
    permission: 'interviews',
  },
  {
    key: 'billing',
    to: '/employer/billing',
    icon: 'account_balance_wallet',
    label: 'Ví & Billing',
    permission: 'billing',
  },
  {
    key: 'company',
    to: '/employer/company',
    icon: 'domain',
    label: 'Công ty',
    permission: 'company_profile',
  },
  {
    key: 'hr-management',
    to: '/employer/hr-management',
    icon: 'groups',
    label: 'Nhân sự HR',
    permission: 'members',
  },
  {
    key: 'audit-logs',
    to: '/employer/audit-logs',
    icon: 'history',
    label: 'Nhật ký công ty',
    permission: 'audit_logs',
  },
])

const canAccessItem = (item) => !item.permission || (permissionsLoaded.value && Boolean(permissions.value[item.permission]))

const showLockedNotice = () => {
  notify.warning(lockedMessage)
}

onMounted(() => {
  ensurePermissionsLoaded().catch(() => {})
})
</script>

<template>
  <aside
    class="sticky top-0 hidden h-screen shrink-0 flex-col border-r border-slate-200/80 bg-white/95 backdrop-blur transition-all duration-200 dark:border-slate-800 dark:bg-slate-950/90 lg:flex"
    :class="collapsed ? 'w-24' : 'w-64'"
  >
    <div class="flex items-center gap-3 px-6 pb-4 pt-6" :class="collapsed ? 'justify-center' : ''">
      <AppLogo
        :show-text="!collapsed"
        size="sm"
        title="AI Recruitment"
        subtitle="Employer Space"
      />
    </div>

    <nav class="flex-1 space-y-1 overflow-y-auto px-3">
      <template v-for="item in navItems" :key="item.key">
        <RouterLink
          v-if="canAccessItem(item)"
          :to="item.to"
          :active-class="item.exact ? '' : 'active-nav'"
          :exact-active-class="item.exact ? 'active-nav' : ''"
          class="nav-link flex items-center gap-3 rounded-lg px-3 py-2 text-slate-600 transition-colors font-medium hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
          :class="collapsed ? 'justify-center' : ''"
          :title="collapsed ? item.label : ''"
        >
          <span class="material-symbols-outlined">{{ item.icon }}</span>
          <span v-if="!collapsed" class="text-sm">{{ item.label }}</span>
        </RouterLink>
        <button
          v-else
          class="nav-link locked-nav flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left font-medium text-slate-400 transition-colors hover:bg-slate-100 dark:text-slate-600 dark:hover:bg-slate-800"
          :class="collapsed ? 'justify-center' : ''"
          :title="lockedMessage"
          :disabled="permissionsLoading && !permissionsLoaded"
          type="button"
          @click="showLockedNotice"
        >
          <span class="material-symbols-outlined">{{ item.icon }}</span>
          <span v-if="!collapsed" class="text-sm">{{ item.label }}</span>
          <span v-if="!collapsed" class="material-symbols-outlined ml-auto text-[17px]">
            {{ permissionsLoading && !permissionsLoaded ? 'hourglass_top' : 'lock' }}
          </span>
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
