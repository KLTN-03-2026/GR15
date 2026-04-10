<script setup>
import { computed, getCurrentInstance } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: 'AI Recruitment',
  },
  subtitle: {
    type: String,
    default: 'Career Intelligence Platform',
  },
  showText: {
    type: Boolean,
    default: true,
  },
  size: {
    type: String,
    default: 'md',
  },
  tone: {
    type: String,
    default: 'dark',
  },
})

const instance = getCurrentInstance()
const gradientCoreId = `logo-core-${instance?.uid ?? 'shared'}`
const gradientAccentId = `logo-accent-${instance?.uid ?? 'shared'}`

const sizeClasses = computed(() => {
  if (props.size === 'sm') {
    return {
      wrapper: 'gap-2.5',
      icon: 'h-10 w-10 rounded-2xl',
      title: 'text-base font-bold',
      subtitle: 'text-[10px] tracking-[0.24em]',
    }
  }

  if (props.size === 'lg') {
    return {
      wrapper: 'gap-3.5',
      icon: 'h-14 w-14 rounded-[1.25rem]',
      title: 'text-2xl font-black',
      subtitle: 'text-xs tracking-[0.28em]',
    }
  }

  return {
    wrapper: 'gap-3',
    icon: 'h-11 w-11 rounded-2xl',
    title: 'text-xl font-bold',
    subtitle: 'text-[11px] tracking-[0.22em]',
  }
})

const toneClasses = computed(() => {
  if (props.tone === 'light') {
    return {
      title: 'text-white',
      subtitle: 'text-white/70',
      iconShell: 'bg-white/12 shadow-[0_18px_35px_rgba(15,23,42,0.14)] ring-1 ring-white/14',
    }
  }

  if (props.tone === 'brand') {
    return {
      title: 'text-[#2463eb]',
      subtitle: 'text-slate-400',
      iconShell: 'bg-white shadow-[0_16px_34px_rgba(36,99,235,0.18)] ring-1 ring-[#2463eb]/10',
    }
  }

  return {
    title: 'text-slate-900 dark:text-white',
    subtitle: 'text-slate-500 dark:text-slate-400',
    iconShell: 'bg-white shadow-[0_16px_34px_rgba(15,23,42,0.08)] ring-1 ring-slate-200/80 dark:bg-slate-900 dark:ring-slate-700/70',
  }
})
</script>

<template>
  <div class="inline-flex items-center" :class="sizeClasses.wrapper">
    <div
      class="relative flex shrink-0 items-center justify-center overflow-hidden"
      :class="[sizeClasses.icon, toneClasses.iconShell]"
      aria-hidden="true"
    >
      <svg viewBox="0 0 64 64" class="h-[76%] w-[76%]" fill="none" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient :id="gradientCoreId" x1="10" y1="8" x2="56" y2="56" gradientUnits="userSpaceOnUse">
            <stop stop-color="#6EA8FF" />
            <stop offset="0.55" stop-color="#2463EB" />
            <stop offset="1" stop-color="#0F3BB8" />
          </linearGradient>
          <linearGradient :id="gradientAccentId" x1="18" y1="12" x2="50" y2="48" gradientUnits="userSpaceOnUse">
            <stop stop-color="#8CF6D2" />
            <stop offset="1" stop-color="#1EC7A5" />
          </linearGradient>
        </defs>

        <rect x="7" y="7" width="50" height="50" rx="18" :fill="`url(#${gradientCoreId})`" />
        <path
          d="M21 41.5C24.3 46.7 31.1 49.3 37.5 47.8C43.9 46.2 49 40.6 49.8 33.8"
          stroke="white"
          stroke-width="3.5"
          stroke-linecap="round"
          opacity="0.92"
        />
        <path
          d="M19 34.6L28.4 24.8L35 31.3L45 20.5"
          :stroke="`url(#${gradientAccentId})`"
          stroke-width="4.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
        <path
          d="M39.7 20.5H45V25.7"
          :stroke="`url(#${gradientAccentId})`"
          stroke-width="4.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
        <circle cx="19" cy="34.6" r="3.4" fill="white" />
        <circle cx="28.4" cy="24.8" r="3.4" fill="#D8E7FF" />
        <circle cx="35" cy="31.3" r="3.4" fill="white" />
        <circle cx="45" cy="20.5" r="3.6" fill="#8CF6D2" />
      </svg>
    </div>

    <div v-if="showText" class="min-w-0">
      <div class="truncate leading-tight" :class="[sizeClasses.title, toneClasses.title]">
        {{ title }}
      </div>
      <div
        v-if="subtitle"
        class="truncate uppercase font-semibold"
        :class="[sizeClasses.subtitle, toneClasses.subtitle]"
      >
        {{ subtitle }}
      </div>
    </div>
  </div>
</template>
