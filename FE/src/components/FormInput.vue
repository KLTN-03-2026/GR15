<template>
  <div>
    <label :for="id" class="block text-sm font-semibold mb-1">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>
    <input 
      :id="id"
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      :type="type"
      :placeholder="placeholder"
      :disabled="disabled"
      :class="{
        'border-red-500 dark:border-red-500': error,
        'border-slate-200 dark:border-slate-700': !error
      }"
      class="w-full rounded-lg dark:bg-slate-800 focus:ring-[#2463eb] focus:border-[#2463eb] border transition-colors" 
    />
    <span v-if="error" class="text-red-500 text-xs mt-1 block">{{ error }}</span>
  </div>
</template>

<script setup>
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
  type: {
    type: String,
    default: 'text'
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
</script>
