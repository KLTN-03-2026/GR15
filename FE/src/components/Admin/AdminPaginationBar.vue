<script setup>
defineProps({
  summary: {
    type: String,
    default: '',
  },
  currentPage: {
    type: Number,
    required: true,
  },
  totalPages: {
    type: Number,
    required: true,
  },
})

defineEmits(['prev', 'next'])
</script>

<template>
  <div class="flex flex-col gap-3 border-t border-slate-200 px-6 py-5 text-sm dark:border-slate-800 md:flex-row md:items-center md:justify-between">
    <p class="text-slate-500 dark:text-slate-400">
      {{ summary }}
    </p>
    <div v-if="totalPages > 1" class="flex items-center gap-2">
      <button
        class="rounded-lg border border-slate-200 px-3 py-2 font-semibold text-slate-600 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
        :disabled="currentPage === 1"
        type="button"
        @click="$emit('prev')"
      >
        Trước
      </button>
      <span class="rounded-lg bg-slate-100 px-3 py-2 font-semibold text-slate-700 dark:bg-slate-800 dark:text-slate-200">
        {{ currentPage }} / {{ totalPages }}
      </span>
      <button
        class="rounded-lg border border-slate-200 px-3 py-2 font-semibold text-slate-600 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
        :disabled="currentPage === totalPages"
        type="button"
        @click="$emit('next')"
      >
        Sau
      </button>
    </div>
  </div>
</template>
