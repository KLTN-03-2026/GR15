<script setup>
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import AppLogo from '@/components/AppLogo.vue'
import { getStoredCandidate } from '@/utils/authStorage'

const route = useRoute()

const currentUser = computed(() => getStoredCandidate())
const displayName = computed(() => currentUser.value?.ho_ten || 'Ứng viên')
const currentPageTitle = computed(() => route.meta?.pageTitle || 'CV Builder')
</script>

<template>
  <div class="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(36,99,235,0.08),_transparent_26%),linear-gradient(180deg,_#f8fafc_0%,_#f4f6fb_100%)] text-slate-900 dark:bg-[#111621] dark:text-slate-100">
    <header class="sticky top-0 z-30 border-b border-slate-200/80 bg-white/90 backdrop-blur dark:border-slate-800 dark:bg-slate-950/85">
      <div class="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-4 sm:px-6 xl:px-8">
        <div class="flex items-center gap-4">
          <RouterLink
            to="/"
            class="inline-flex items-center gap-3 rounded-2xl px-2 py-1.5 transition hover:bg-slate-100 dark:hover:bg-slate-800"
          >
            <AppLogo size="sm" title="AI Recruitment" subtitle="CV Builder" />
          </RouterLink>
          <div class="hidden h-10 w-px bg-slate-200 dark:bg-slate-700 md:block" />
          <div class="hidden md:block">
            <p class="text-xs font-semibold uppercase tracking-[0.28em] text-blue-500">Candidate Tools</p>
            <h1 class="mt-1 text-lg font-bold text-slate-900 dark:text-white">{{ currentPageTitle }}</h1>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <RouterLink
            to="/my-cv"
            class="inline-flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800"
          >
            <span class="material-symbols-outlined text-[18px]">description</span>
            CV của tôi
          </RouterLink>
          <div class="hidden rounded-2xl border border-slate-200 bg-white px-4 py-2.5 text-right dark:border-slate-700 dark:bg-slate-900 sm:block">
            <p class="text-xs uppercase tracking-[0.24em] text-slate-400">Ứng viên</p>
            <p class="mt-1 text-sm font-semibold text-slate-900 dark:text-white">{{ displayName }}</p>
          </div>
        </div>
      </div>
    </header>

    <main class="px-4 py-6 sm:px-6 xl:px-8">
      <div class="mx-auto max-w-7xl">
        <slot />
      </div>
    </main>
  </div>
</template>
