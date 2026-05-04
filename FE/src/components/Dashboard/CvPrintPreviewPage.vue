<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import ProfileCvPreview from '@/components/Dashboard/ProfileCvPreview.vue'
import { readCvPrintPayload } from '@/utils/profileCvBuilder'

const route = useRoute()

const loading = ref(true)
const missingPayload = ref(false)
const profile = ref(null)
const owner = ref(null)

const token = computed(() => String(route.query.token || '').trim())

const triggerPrint = async () => {
  await nextTick()
  window.setTimeout(() => {
    window.print()
  }, 250)
}

const reopenPrintDialog = () => {
  window.print()
}

onMounted(async () => {
  let payload = readCvPrintPayload(token.value)

  if (!payload && typeof window !== 'undefined' && window.name) {
    try {
      const namedPayload = JSON.parse(window.name)
      if (namedPayload?.profile) {
        payload = namedPayload
      }
    } catch (error) {
      // ignore invalid window.name payload
    }
  }

  if (!payload?.profile) {
    missingPayload.value = true
    loading.value = false
    return
  }

  profile.value = payload.profile
  owner.value = payload.owner || {}
  loading.value = false

  await triggerPrint()
})
</script>

<template>
  <div class="min-h-screen bg-white">
    <div v-if="loading" class="mx-auto flex min-h-screen max-w-5xl items-center justify-center px-6">
      <div class="rounded-3xl border border-slate-200 bg-white px-8 py-10 text-center shadow-sm">
        <p class="text-sm font-semibold uppercase tracking-[0.24em] text-blue-500">CV Export</p>
        <h1 class="mt-3 text-2xl font-black text-slate-900">Đang chuẩn bị bản tải xuống</h1>
      </div>
    </div>

    <div v-else-if="missingPayload" class="mx-auto flex min-h-screen max-w-3xl items-center justify-center px-6">
      <div class="rounded-3xl border border-amber-200 bg-white px-8 py-10 text-center shadow-sm">
        <p class="text-sm font-semibold uppercase tracking-[0.24em] text-amber-500">Không tìm thấy dữ liệu</p>
        <h1 class="mt-3 text-2xl font-black text-slate-900">Không thể tạo bản CV tải xuống</h1>
        <p class="mt-3 text-sm leading-7 text-slate-500">
          Dữ liệu preview tạm thời đã hết hạn. Hãy quay lại màn tạo CV hoặc CV của tôi rồi bấm tải xuống lại.
        </p>
      </div>
    </div>

    <div v-else class="relative mx-auto max-w-5xl px-0 py-0 print:max-w-none print:px-0 print:py-0">
      <div class="overflow-hidden bg-white print:rounded-none print:border-0 print:shadow-none">
        <ProfileCvPreview :profile="profile" :owner="owner" />
      </div>

      <button
        class="fixed bottom-5 right-5 z-40 inline-flex items-center gap-2 rounded-full bg-slate-900 px-4 py-3 text-sm font-semibold text-white shadow-lg transition hover:bg-slate-700 print:hidden"
        type="button"
        @click="reopenPrintDialog"
      >
        <span class="material-symbols-outlined text-[18px]">picture_as_pdf</span>
        Tải PDF lại
      </button>
    </div>
  </div>
</template>

<style scoped>
@page {
  margin: 0;
}

@media print {
  :global(html),
  :global(body) {
    margin: 0 !important;
    padding: 0 !important;
    background: #fff !important;
  }
}
</style>
