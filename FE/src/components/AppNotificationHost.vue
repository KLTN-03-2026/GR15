<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'

const items = ref([])
let cleanupMap = new Map()

const colorMap = {
  success: 'border-emerald-200 bg-emerald-50 text-emerald-800',
  error: 'border-rose-200 bg-rose-50 text-rose-800',
  info: 'border-blue-200 bg-blue-50 text-blue-800',
  warning: 'border-amber-200 bg-amber-50 text-amber-800',
}

const iconMap = {
  success: 'check_circle',
  error: 'error',
  info: 'info',
  warning: 'warning',
}

const removeItem = (id) => {
  items.value = items.value.filter((item) => item.id !== id)

  const timeout = cleanupMap.get(id)
  if (timeout) {
    window.clearTimeout(timeout)
    cleanupMap.delete(id)
  }
}

const handleNotify = (event) => {
  const item = event?.detail
  if (!item?.id || !item?.message) return

  items.value = [...items.value, item].slice(-4)

  const timeout = window.setTimeout(() => {
    removeItem(item.id)
  }, 3200)

  cleanupMap.set(item.id, timeout)
}

onMounted(() => {
  window.addEventListener('app-notify', handleNotify)
})

onBeforeUnmount(() => {
  window.removeEventListener('app-notify', handleNotify)
  cleanupMap.forEach((timeout) => window.clearTimeout(timeout))
  cleanupMap.clear()
})
</script>

<template>
  <div class="pointer-events-none fixed right-4 top-4 z-[100] flex w-full max-w-sm flex-col gap-3">
    <transition-group name="toast">
      <div
        v-for="item in items"
        :key="item.id"
        class="pointer-events-auto rounded-2xl border px-4 py-3 shadow-lg backdrop-blur"
        :class="colorMap[item.type] || colorMap.info"
      >
        <div class="flex items-start gap-3">
          <span class="material-symbols-outlined text-[20px]">{{ iconMap[item.type] || iconMap.info }}</span>
          <p class="flex-1 text-sm font-medium leading-6">{{ item.message }}</p>
          <button type="button" class="text-current/70 transition hover:text-current" @click="removeItem(item.id)">
            <span class="material-symbols-outlined text-[18px]">close</span>
          </button>
        </div>
      </div>
    </transition-group>
  </div>
</template>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.18s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
