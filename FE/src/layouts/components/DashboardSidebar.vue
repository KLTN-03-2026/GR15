<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import AppLogo from '@/components/AppLogo.vue'
import { getStoredUser } from '@/utils/authStorage'

const ROLE_CANDIDATE = 0
const ROLE_ADMIN = 2

const currentUser = computed(() => getStoredUser())
const currentRole = computed(() => Number(currentUser.value?.vai_tro ?? ROLE_CANDIDATE))
const isCandidate = computed(() => currentRole.value === ROLE_CANDIDATE)
const isAdmin = computed(() => currentRole.value === ROLE_ADMIN)
</script>

<template>
  <aside class="hidden w-72 shrink-0 border-r border-slate-200 bg-white lg:flex lg:flex-col">
    <div class="px-6 py-6">
      <AppLogo :title="isAdmin ? 'SmartJob Admin' : 'SmartJob AI'" :subtitle="isAdmin ? 'Matching Management' : 'Candidate Workspace'" size="sm" />
    </div>

    <nav class="flex-1 space-y-1 px-4 pb-6">
      <template v-if="isCandidate">
        <RouterLink to="/dashboard" class="block rounded-xl px-4 py-3 text-sm font-medium text-slate-700 hover:bg-slate-100">Tổng quan</RouterLink>
        <RouterLink to="/profile" class="block rounded-xl px-4 py-3 text-sm font-medium text-slate-700 hover:bg-slate-100">Thông tin cá nhân</RouterLink>
        <RouterLink to="/my-cv" class="block rounded-xl px-4 py-3 text-sm font-medium text-slate-700 hover:bg-slate-100">Hồ sơ ứng viên</RouterLink>
        <RouterLink to="/my-skills" class="block rounded-xl px-4 py-3 text-sm font-medium text-slate-700 hover:bg-slate-100">Kỹ năng cá nhân</RouterLink>
        <RouterLink to="/matched-jobs" class="block rounded-xl px-4 py-3 text-sm font-medium text-slate-700 hover:bg-slate-100">Việc làm phù hợp</RouterLink>
        <RouterLink to="/career-report" class="block rounded-xl px-4 py-3 text-sm font-medium text-slate-700 hover:bg-slate-100">Career Report</RouterLink>
        <RouterLink to="/ai-center" class="block rounded-xl px-4 py-3 text-sm font-medium text-slate-700 hover:bg-slate-100">Trung tâm AI</RouterLink>
      </template>

      <template v-else-if="isAdmin">
        <RouterLink to="/admin/matchings" class="block rounded-xl px-4 py-3 text-sm font-medium text-slate-700 hover:bg-slate-100">Quản lý matching</RouterLink>
      </template>
    </nav>
  </aside>
</template>

<style scoped>
.router-link-active {
  background: rgb(37 99 235 / 0.1);
  color: #1d4ed8;
}
</style>
