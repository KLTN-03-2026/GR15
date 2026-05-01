<script setup>
const props = defineProps({
  maxWidthClass: {
    type: String,
    default: 'max-w-4xl',
  },
  eyebrow: {
    type: String,
    default: 'Quản lý dữ liệu',
  },
  title: {
    type: String,
    required: true,
  },
  description: {
    type: String,
    default: '',
  },
  submitLabel: {
    type: String,
    default: 'Lưu thay đổi',
  },
  submitLoadingLabel: {
    type: String,
    default: 'Đang cập nhật...',
  },
  cancelLabel: {
    type: String,
    default: 'Hủy',
  },
  saving: {
    type: Boolean,
    default: false,
  },
  disableClose: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['close', 'submit'])

const onClose = () => {
  if (props.disableClose) return
  emit('close')
}
</script>

<template>
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/25 p-4 backdrop-blur-sm"
    @click.self="onClose"
  >
    <div :class="['flex max-h-[calc(100vh-2rem)] w-full flex-col overflow-hidden rounded-[28px] border border-slate-200 bg-white shadow-[0_24px_80px_rgba(15,23,42,0.18)]', maxWidthClass]">
      <div class="flex items-start justify-between gap-4 border-b border-slate-200 px-6 py-5 sm:px-7">
        <div class="space-y-3">
          <div class="flex flex-wrap items-center gap-3">
            <span class="inline-flex h-11 w-11 items-center justify-center rounded-2xl bg-[#2463eb]/10 text-[#2463eb]">
              <span class="material-symbols-outlined text-[22px]">edit_square</span>
            </span>
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.32em] text-slate-400">{{ eyebrow }}</p>
              <h3 class="text-xl font-bold text-slate-900">{{ title }}</h3>
            </div>
          </div>
          <p v-if="description" class="max-w-2xl text-sm leading-6 text-slate-500">
            {{ description }}
          </p>
        </div>
        <button
          class="inline-flex h-11 w-11 items-center justify-center rounded-2xl border border-slate-200 bg-white text-slate-400 transition hover:border-slate-300 hover:text-slate-700 disabled:cursor-not-allowed disabled:opacity-50"
          :disabled="disableClose"
          type="button"
          @click="onClose"
        >
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>

      <div v-if="$slots.summary" class="grid gap-4 border-b border-slate-200 bg-slate-50/80 px-6 py-5 sm:grid-cols-3 sm:px-7">
        <slot name="summary" />
      </div>

      <form class="flex min-h-0 flex-1 flex-col" @submit.prevent="emit('submit')">
        <div class="min-h-0 flex-1 overflow-y-auto px-6 py-6 sm:px-7">
          <slot />
        </div>

        <div class="flex flex-col-reverse gap-3 border-t border-slate-200 bg-white px-6 py-5 sm:flex-row sm:justify-end sm:px-7">
          <button
            class="inline-flex items-center justify-center rounded-2xl border border-slate-200 px-5 py-3 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
            :disabled="disableClose || saving"
            type="button"
            @click="onClose"
          >
            {{ cancelLabel }}
          </button>
          <button
            class="inline-flex items-center justify-center rounded-2xl bg-[#2463eb] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[#1d56cf] disabled:cursor-not-allowed disabled:opacity-70"
            :disabled="saving"
            type="submit"
          >
            {{ saving ? submitLoadingLabel : submitLabel }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
