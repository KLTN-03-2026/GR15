<template>
  <div class="fixed top-20 left-0 right-0 mx-auto max-w-[1000px] z-50 pointer-events-none">
    <div 
      v-if="message"
      :class="typeClasses"
      class="px-6 py-3 rounded-lg mx-4 flex items-center gap-2 pointer-events-auto shadow-lg animate-in slide-in-from-top duration-300"
    >
      <span class="material-symbols-outlined text-lg">{{ icon }}</span>
      <span>{{ message }}</span>
      <button 
        type="button"
        @click="$emit('close')"
        class="ml-auto"
      >
        <span class="material-symbols-outlined text-lg">close</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  message: {
    type: String,
    default: ''
  },
  type: {
    type: String,
    enum: ['success', 'error', 'warning', 'info'],
    default: 'info'
  }
})

const typeClasses = computed(() => {
  switch (props.type) {
    case 'success':
      return 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700 text-green-700 dark:text-green-200'
    case 'error':
      return 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 text-red-700 dark:text-red-200'
    case 'warning':
      return 'bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 text-yellow-700 dark:text-yellow-200'
    default:
      return 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 text-blue-700 dark:text-blue-200'
  }
})

const icon = computed(() => {
  switch (props.type) {
    case 'success':
      return 'check_circle'
    case 'error':
      return 'error'
    case 'warning':
      return 'warning'
    default:
      return 'info'
  }
})

defineEmits(['close'])
</script>
