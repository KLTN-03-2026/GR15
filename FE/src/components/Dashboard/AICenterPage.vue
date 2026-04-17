<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, RouterView } from 'vue-router'
import { aiChatService, mockInterviewService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'
import { getStoredCandidate } from '@/utils/authStorage'

const notify = useNotify()

const loadingOverview = ref(false)
const chatSessionsCount = ref(0)
const mockDashboard = ref(null)

const currentUser = computed(() => {
  return getStoredCandidate()
})

const firstName = computed(() => {
  const fullName = currentUser.value?.ho_ten?.trim() || 'bạn'
  const parts = fullName.split(/\s+/)
  return parts[parts.length - 1]
})

const overviewCards = computed(() => [
  {
    label: 'Phiên chatbot',
    value: chatSessionsCount.value,
    helper: 'Phiên tư vấn đang lưu trong hệ thống',
    icon: 'forum',
    tone: 'bg-blue-500/10 text-blue-300 border-blue-500/20',
  },
  {
    label: 'Phiên mock interview',
    value: Number(mockDashboard.value?.completed_sessions || 0),
    helper: 'Phiên mock đã hoàn thành',
    icon: 'record_voice_over',
    tone: 'bg-violet-500/10 text-violet-300 border-violet-500/20',
  },
  {
    label: 'Báo cáo AI',
    value: Number(mockDashboard.value?.total_reports || 0),
    helper: 'Báo cáo đánh giá đã được tạo',
    icon: 'analytics',
    tone: 'bg-emerald-500/10 text-emerald-300 border-emerald-500/20',
  },
  {
    label: 'Điểm mock gần nhất',
    value: mockDashboard.value?.latest_overall_score
      ? `${Math.round(Number(mockDashboard.value.latest_overall_score))}/100`
      : '--',
    helper: 'Theo phiên mock interview mới nhất',
    icon: 'insights',
    tone: 'bg-amber-500/10 text-amber-300 border-amber-500/20',
  },
])

const latestFocus = computed(() => {
  const focus = mockDashboard.value?.latest_focus
  return Array.isArray(focus) ? focus.slice(0, 3) : []
})

const fetchOverview = async () => {
  loadingOverview.value = true
  try {
    const [chatRes, mockRes] = await Promise.all([
      aiChatService.getSessions(),
      mockInterviewService.getDashboard(),
    ])

    chatSessionsCount.value = Array.isArray(chatRes?.data) ? chatRes.data.length : 0
    mockDashboard.value = mockRes?.data || null
  } catch (error) {
    notify.apiError(error, 'Không tải được tổng quan AI Center.')
  } finally {
    loadingOverview.value = false
  }
}

onMounted(fetchOverview)
</script>

<template>
  <div class="space-y-8 text-slate-100">
    <section class="overflow-hidden rounded-[28px] border border-slate-800 bg-gradient-to-r from-[#101b44] via-[#183389] to-[#2463eb] shadow-2xl shadow-blue-950/20">
      <div class="grid gap-6 px-8 py-8 lg:grid-cols-[minmax(0,1.5fr)_320px] lg:items-end">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.32em] text-blue-200/80">AI Services</p>
          <h1 class="mt-3 text-4xl font-bold leading-tight text-white">AI Center của {{ firstName }}</h1>
          <p class="mt-4 max-w-3xl text-base leading-8 text-blue-100/90">
            Tư vấn nghề nghiệp, luyện mock interview và theo dõi tiến bộ AI trong cùng một không gian đồng nhất với dashboard ứng viên.
          </p>
        </div>

        <div class="rounded-[24px] border border-white/15 bg-white/10 p-5 backdrop-blur">
          <p class="text-sm font-semibold text-white/90">Lộ trình sử dụng khuyến nghị</p>
          <ol class="mt-4 space-y-2 text-sm leading-7 text-blue-50/85">
            <li>1. Dùng chatbot để hỏi về job phù hợp, kỹ năng còn thiếu và hướng cải thiện CV.</li>
            <li>2. Chuyển sang mock interview để luyện trả lời theo hồ sơ thật.</li>
            <li>3. Sinh báo cáo cuối phiên và dùng nó làm trọng tâm cải thiện cho vòng tiếp theo.</li>
          </ol>
        </div>
      </div>
    </section>

    <div class="grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-4">
      <article
        v-for="card in overviewCards"
        :key="card.label"
        class="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-sm shadow-black/10"
      >
        <div class="mb-4 flex items-start justify-between">
          <div class="rounded-xl border p-3" :class="card.tone">
            <span class="material-symbols-outlined">{{ card.icon }}</span>
          </div>
        </div>
        <p class="text-sm font-medium text-slate-400">{{ card.label }}</p>
        <h3 class="mt-2 text-3xl font-bold text-white">{{ loadingOverview ? '...' : card.value }}</h3>
        <p class="mt-3 text-xs leading-6 text-slate-500">{{ card.helper }}</p>
      </article>
    </div>

    <section class="rounded-2xl border border-slate-800 bg-slate-900/85 p-3 shadow-sm">
      <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
          <RouterLink
            :to="{ name: 'AICenterChatbot' }"
            class="h-full rounded-xl px-5 py-4 text-left transition"
            active-class="bg-gradient-to-r from-blue-600 to-indigo-500 text-white shadow-lg shadow-blue-600/20"
          >
            <div class="flex items-center gap-3">
              <span class="material-symbols-outlined">forum</span>
              <div>
                <p class="font-bold">Chatbot tư vấn nghề nghiệp</p>
                <p class="mt-1 text-sm text-slate-400 [a.active_&]:text-blue-50/90">
                  Hỏi nhanh về matching, CV, kỹ năng và job phù hợp.
                </p>
              </div>
            </div>
          </RouterLink>

          <RouterLink
            :to="{ name: 'AICenterMockInterview' }"
            class="h-full rounded-xl px-5 py-4 text-left transition"
            active-class="bg-gradient-to-r from-violet-600 to-fuchsia-500 text-white shadow-lg shadow-violet-600/20"
          >
            <div class="flex items-center gap-3">
              <span class="material-symbols-outlined">school</span>
              <div>
                <p class="font-bold">Mock Interview</p>
                <p class="mt-1 text-sm text-slate-400 [a.active_&]:text-violet-50/90">
                  Luyện phỏng vấn theo hồ sơ thật và xem báo cáo cuối phiên.
                </p>
              </div>
            </div>
          </RouterLink>
      </div>
    </section>

    <RouterView v-slot="{ Component }">
      <component :is="Component" @refresh-overview="fetchOverview" />
    </RouterView>
  </div>
</template>
