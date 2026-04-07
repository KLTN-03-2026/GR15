<template>
  <div>
    <label :for="id" class="block text-sm font-semibold mb-1">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>
    <div class="relative">
      <input 
        :id="id"
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        :type="showPassword ? 'text' : 'password'"
        :placeholder="placeholder"
        :disabled="disabled"
        :class="{
          'border-red-500 dark:border-red-500': error,
          'border-slate-200 dark:border-slate-700': !error
        }"
        class="w-full rounded-lg dark:bg-slate-800 focus:ring-[#2463eb] focus:border-[#2463eb] border transition-colors pr-10" 
      />
      <button 
        type="button"
        @click="showPassword = !showPassword"
        :disabled="disabled"
        class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 disabled:opacity-50"
      >
        <span class="material-symbols-outlined text-sm">{{ showPassword ? 'visibility_off' : 'visibility' }}</span>
      </button>
    </div>
    <span v-if="error" class="text-red-500 text-xs mt-1 block">{{ error }}</span>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  id: {
    type: String,
    required: true
  },
  label: {
    type: String,
    required: true
  },
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: ''
  },
  error: {
    type: String,
    default: ''
  },
  disabled: {
    type: Boolean,
    default: false
  },
  required: {
    type: Boolean,
    default: false
  }
})

defineEmits(['update:modelValue'])

const showPassword = ref(false)
</script>
