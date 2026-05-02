<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: 'MM/YYYY' },
  allowPresent: { type: Boolean, default: false },
  presentLabel: { type: String, default: 'Hiện tại' },
  minYear: { type: Number, default: 1970 },
  maxYear: { type: Number, default: new Date().getFullYear() + 5 },
})

const emit = defineEmits(['update:modelValue'])

const isOpen = ref(false)
const pickerRef = ref(null)
const triggerRef = ref(null)

const months = [
  { value: '01', label: 'Th01' },
  { value: '02', label: 'Th02' },
  { value: '03', label: 'Th03' },
  { value: '04', label: 'Th04' },
  { value: '05', label: 'Th05' },
  { value: '06', label: 'Th06' },
  { value: '07', label: 'Th07' },
  { value: '08', label: 'Th08' },
  { value: '09', label: 'Th09' },
  { value: '10', label: 'Th10' },
  { value: '11', label: 'Th11' },
  { value: '12', label: 'Th12' },
]

const currentDisplayYear = ref(new Date().getFullYear())

const selectedMonth = ref('')
const selectedYear = ref('')
const isPresent = ref(false)

const displayValue = computed(() => {
  if (isPresent.value) return props.presentLabel
  if (!props.modelValue) return ''
  return props.modelValue
})

const yearRange = computed(() => {
  const years = []
  for (let y = props.maxYear; y >= props.minYear; y--) {
    years.push(y)
  }
  return years
})

const isCurrentMonth = (monthVal) => {
  const now = new Date()
  return (
    Number(currentDisplayYear.value) === now.getFullYear() &&
    Number(monthVal) === now.getMonth() + 1
  )
}

const isSelectedMonth = (monthVal) => {
  return (
    selectedMonth.value === monthVal &&
    String(selectedYear.value) === String(currentDisplayYear.value)
  )
}

const parseValue = (val) => {
  if (!val) return { month: '', year: '' }

  if (props.allowPresent && (val === props.presentLabel || val.toLowerCase() === 'hiện tại')) {
    isPresent.value = true
    return { month: '', year: '' }
  }

  isPresent.value = false
  const parts = String(val).split('/')
  if (parts.length === 2) {
    return { month: parts[0].padStart(2, '0'), year: parts[1] }
  }
  return { month: '', year: '' }
}

const selectMonth = (monthVal) => {
  isPresent.value = false
  selectedMonth.value = monthVal
  selectedYear.value = String(currentDisplayYear.value)
  const formatted = `${monthVal}/${currentDisplayYear.value}`
  emit('update:modelValue', formatted)
  isOpen.value = false
}

const selectPresent = () => {
  isPresent.value = true
  selectedMonth.value = ''
  selectedYear.value = ''
  emit('update:modelValue', props.presentLabel)
  isOpen.value = false
}

const clearValue = () => {
  isPresent.value = false
  selectedMonth.value = ''
  selectedYear.value = ''
  emit('update:modelValue', '')
  isOpen.value = false
}

const prevYear = () => {
  if (currentDisplayYear.value > props.minYear) {
    currentDisplayYear.value--
  }
}

const nextYear = () => {
  if (currentDisplayYear.value < props.maxYear) {
    currentDisplayYear.value++
  }
}

const togglePicker = () => {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    if (selectedYear.value) {
      currentDisplayYear.value = Number(selectedYear.value)
    } else {
      currentDisplayYear.value = new Date().getFullYear()
    }
  }
}

const handleClickOutside = (e) => {
  if (
    pickerRef.value &&
    !pickerRef.value.contains(e.target) &&
    triggerRef.value &&
    !triggerRef.value.contains(e.target)
  ) {
    isOpen.value = false
  }
}

watch(
  () => props.modelValue,
  (val) => {
    const parsed = parseValue(val)
    selectedMonth.value = parsed.month
    selectedYear.value = parsed.year
  },
  { immediate: true },
)

onMounted(() => {
  document.addEventListener('mousedown', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('mousedown', handleClickOutside)
})
</script>

<template>
  <div class="myp-wrapper">
    <button
      ref="triggerRef"
      class="myp-trigger"
      :class="{ 'myp-trigger--active': isOpen, 'myp-trigger--has-value': displayValue }"
      type="button"
      @click="togglePicker"
    >
      <span class="myp-trigger__icon material-symbols-outlined">calendar_month</span>
      <span class="myp-trigger__text" :class="{ 'myp-trigger__text--placeholder': !displayValue }">
        {{ displayValue || placeholder }}
      </span>
      <span v-if="displayValue" class="myp-trigger__clear" @click.stop="clearValue">
        <span class="material-symbols-outlined" style="font-size: 16px">close</span>
      </span>
      <span v-else class="myp-trigger__chevron material-symbols-outlined">expand_more</span>
    </button>

    <Transition name="myp-dropdown">
      <div v-if="isOpen" ref="pickerRef" class="myp-dropdown">
        <div class="myp-dropdown__header">
          <button
            class="myp-dropdown__nav-btn"
            type="button"
            :disabled="currentDisplayYear <= minYear"
            @click="prevYear"
          >
            <span class="material-symbols-outlined" style="font-size: 20px">chevron_left</span>
          </button>
          <div class="myp-dropdown__year-display">
            <span class="myp-dropdown__year-label">{{ currentDisplayYear }}</span>
          </div>
          <button
            class="myp-dropdown__nav-btn"
            type="button"
            :disabled="currentDisplayYear >= maxYear"
            @click="nextYear"
          >
            <span class="material-symbols-outlined" style="font-size: 20px">chevron_right</span>
          </button>
        </div>

        <div class="myp-dropdown__grid">
          <button
            v-for="month in months"
            :key="month.value"
            class="myp-dropdown__month"
            :class="{
              'myp-dropdown__month--selected': isSelectedMonth(month.value),
              'myp-dropdown__month--current': isCurrentMonth(month.value) && !isSelectedMonth(month.value),
            }"
            type="button"
            @click="selectMonth(month.value)"
          >
            {{ month.label }}
          </button>
        </div>

        <div v-if="allowPresent" class="myp-dropdown__footer">
          <button
            class="myp-dropdown__present-btn"
            :class="{ 'myp-dropdown__present-btn--active': isPresent }"
            type="button"
            @click="selectPresent"
          >
            <span class="material-symbols-outlined" style="font-size: 16px">work_history</span>
            {{ presentLabel }}
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.myp-wrapper {
  position: relative;
  width: 100%;
}

/* ── Trigger button ── */
.myp-trigger {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 11px 16px;
  border: 1.5px solid var(--myp-border, #e2e8f0);
  border-radius: 16px;
  background: var(--myp-bg, #fff);
  color: var(--myp-text, #334155);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  outline: none;
  text-align: left;
}

.myp-trigger:hover {
  border-color: var(--myp-border-hover, #cbd5e1);
  background: var(--myp-bg-hover, #f8fafc);
}

.myp-trigger--active {
  border-color: #3b82f6;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
}

.myp-trigger__icon {
  font-size: 20px;
  color: #94a3b8;
  flex-shrink: 0;
  transition: color 0.2s;
}

.myp-trigger--active .myp-trigger__icon,
.myp-trigger--has-value .myp-trigger__icon {
  color: #3b82f6;
}

.myp-trigger__text {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 500;
}

.myp-trigger__text--placeholder {
  color: #94a3b8;
  font-weight: 400;
}

.myp-trigger__clear {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #f1f5f9;
  color: #64748b;
  flex-shrink: 0;
  transition: all 0.15s;
}

.myp-trigger__clear:hover {
  background: #fee2e2;
  color: #ef4444;
}

.myp-trigger__chevron {
  font-size: 20px;
  color: #94a3b8;
  flex-shrink: 0;
  transition: transform 0.25s ease;
}

.myp-trigger--active .myp-trigger__chevron {
  transform: rotate(180deg);
}

/* ── Dropdown panel ── */
.myp-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  right: 0;
  min-width: 280px;
  z-index: 50;
  border: 1.5px solid #e2e8f0;
  border-radius: 20px;
  background: #fff;
  box-shadow:
    0 20px 25px -5px rgba(0, 0, 0, 0.08),
    0 8px 10px -6px rgba(0, 0, 0, 0.04),
    0 0 0 1px rgba(0, 0, 0, 0.02);
  overflow: hidden;
}

/* ── Header with year nav ── */
.myp-dropdown__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px 10px;
  border-bottom: 1px solid #f1f5f9;
}

.myp-dropdown__nav-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 12px;
  border: 1.5px solid #e2e8f0;
  background: #fff;
  color: #475569;
  cursor: pointer;
  transition: all 0.15s;
}

.myp-dropdown__nav-btn:hover:not(:disabled) {
  background: #f1f5f9;
  border-color: #cbd5e1;
}

.myp-dropdown__nav-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.myp-dropdown__year-display {
  display: flex;
  align-items: center;
  gap: 6px;
}

.myp-dropdown__year-label {
  font-size: 18px;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.02em;
}

/* ── Month grid ── */
.myp-dropdown__grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 6px;
  padding: 12px 14px;
}

.myp-dropdown__month {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px 4px;
  border-radius: 12px;
  border: 1.5px solid transparent;
  background: transparent;
  color: #334155;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.myp-dropdown__month:hover {
  background: #f1f5f9;
  border-color: #e2e8f0;
}

.myp-dropdown__month--selected {
  background: #2563eb !important;
  color: #fff !important;
  border-color: #2563eb !important;
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3);
}

.myp-dropdown__month--current {
  border-color: #93c5fd;
  color: #2563eb;
  background: #eff6ff;
}

/* ── Footer ── */
.myp-dropdown__footer {
  padding: 10px 14px 14px;
  border-top: 1px solid #f1f5f9;
}

.myp-dropdown__present-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 100%;
  padding: 10px 16px;
  border-radius: 12px;
  border: 1.5px dashed #e2e8f0;
  background: #fafafa;
  color: #64748b;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.myp-dropdown__present-btn:hover {
  background: #f0fdf4;
  border-color: #86efac;
  color: #16a34a;
}

.myp-dropdown__present-btn--active {
  background: #f0fdf4 !important;
  border-color: #22c55e !important;
  border-style: solid !important;
  color: #16a34a !important;
}

/* ── Dropdown transition ── */
.myp-dropdown-enter-active {
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.myp-dropdown-leave-active {
  transition: all 0.15s ease-in;
}

.myp-dropdown-enter-from {
  opacity: 0;
  transform: translateY(-8px) scale(0.97);
}

.myp-dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px) scale(0.98);
}

/* ── Dark mode ── */
@media (prefers-color-scheme: dark) {
  .myp-trigger {
    --myp-border: #334155;
    --myp-bg: #0f172a;
    --myp-text: #e2e8f0;
    --myp-border-hover: #475569;
    --myp-bg-hover: #1e293b;
  }

  .myp-trigger__text--placeholder {
    color: #64748b;
  }

  .myp-trigger__clear {
    background: #1e293b;
    color: #94a3b8;
  }

  .myp-trigger__clear:hover {
    background: #7f1d1d33;
    color: #f87171;
  }

  .myp-dropdown {
    background: #0f172a;
    border-color: #334155;
    box-shadow:
      0 20px 25px -5px rgba(0, 0, 0, 0.35),
      0 8px 10px -6px rgba(0, 0, 0, 0.25);
  }

  .myp-dropdown__header {
    border-bottom-color: #1e293b;
  }

  .myp-dropdown__nav-btn {
    border-color: #334155;
    background: #0f172a;
    color: #94a3b8;
  }

  .myp-dropdown__nav-btn:hover:not(:disabled) {
    background: #1e293b;
    border-color: #475569;
  }

  .myp-dropdown__year-label {
    color: #f1f5f9;
  }

  .myp-dropdown__month {
    color: #cbd5e1;
  }

  .myp-dropdown__month:hover {
    background: #1e293b;
    border-color: #334155;
  }

  .myp-dropdown__month--current {
    border-color: #1e40af;
    color: #60a5fa;
    background: #1e3a5f30;
  }

  .myp-dropdown__footer {
    border-top-color: #1e293b;
  }

  .myp-dropdown__present-btn {
    border-color: #334155;
    background: #1e293b;
    color: #94a3b8;
  }

  .myp-dropdown__present-btn:hover {
    background: #14532d22;
    border-color: #166534;
    color: #4ade80;
  }

  .myp-dropdown__present-btn--active {
    background: #14532d33 !important;
    border-color: #22c55e !important;
    color: #4ade80 !important;
  }
}

/* Tailwind dark mode class-based override */
:global(.dark) .myp-trigger {
  --myp-border: #334155;
  --myp-bg: #0f172a;
  --myp-text: #e2e8f0;
  --myp-border-hover: #475569;
  --myp-bg-hover: #1e293b;
}

:global(.dark) .myp-trigger__text--placeholder {
  color: #64748b;
}

:global(.dark) .myp-trigger__clear {
  background: #1e293b;
  color: #94a3b8;
}

:global(.dark) .myp-trigger__clear:hover {
  background: #7f1d1d33;
  color: #f87171;
}

:global(.dark) .myp-dropdown {
  background: #0f172a;
  border-color: #334155;
  box-shadow:
    0 20px 25px -5px rgba(0, 0, 0, 0.35),
    0 8px 10px -6px rgba(0, 0, 0, 0.25);
}

:global(.dark) .myp-dropdown__header {
  border-bottom-color: #1e293b;
}

:global(.dark) .myp-dropdown__nav-btn {
  border-color: #334155;
  background: #0f172a;
  color: #94a3b8;
}

:global(.dark) .myp-dropdown__nav-btn:hover:not(:disabled) {
  background: #1e293b;
  border-color: #475569;
}

:global(.dark) .myp-dropdown__year-label {
  color: #f1f5f9;
}

:global(.dark) .myp-dropdown__month {
  color: #cbd5e1;
}

:global(.dark) .myp-dropdown__month:hover {
  background: #1e293b;
  border-color: #334155;
}

:global(.dark) .myp-dropdown__month--current {
  border-color: #1e40af;
  color: #60a5fa;
  background: #1e3a5f30;
}

:global(.dark) .myp-dropdown__footer {
  border-top-color: #1e293b;
}

:global(.dark) .myp-dropdown__present-btn {
  border-color: #334155;
  background: #1e293b;
  color: #94a3b8;
}

:global(.dark) .myp-dropdown__present-btn:hover {
  background: #14532d22;
  border-color: #166534;
  color: #4ade80;
}

:global(.dark) .myp-dropdown__present-btn--active {
  background: #14532d33 !important;
  border-color: #22c55e !important;
  color: #4ade80 !important;
}
</style>
