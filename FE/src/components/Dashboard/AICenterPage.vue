<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, RouterView } from 'vue-router'
import { aiChatService, mockInterviewService, walletService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'
import { getStoredCandidate } from '@/utils/authStorage'

const notify = useNotify()

const loadingOverview = ref(false)
const loadingBilling = ref(false)
const chatSessionsCount = ref(0)
const mockDashboard = ref(null)
const wallet = ref(null)
const pricing = ref([])

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

const walletStats = computed(() => ({
  available: Number(wallet.value?.so_du_kha_dung || 0),
  hold: Number(wallet.value?.so_du_tam_giu || 0),
}))

const pricingMap = computed(() =>
  pricing.value.reduce((accumulator, item) => {
    accumulator[item.feature_code] = Number(item.don_gia || 0)
    return accumulator
  }, {})
)

const formatCurrency = (value) =>
  `${new Intl.NumberFormat('vi-VN').format(Number(value || 0))} đ`

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

const fetchBilling = async () => {
  loadingBilling.value = true
  try {
    const [walletRes, pricingRes] = await Promise.all([
      walletService.getWallet(),
      walletService.getPricing(),
    ])

    wallet.value = walletRes?.data?.wallet || null
    pricing.value = pricingRes?.data || []
  } catch (error) {
    notify.apiError(error, 'Không tải được dữ liệu ví AI.')
  } finally {
    loadingBilling.value = false
  }
}

onMounted(async () => {
  await Promise.all([fetchOverview(), fetchBilling()])
})
</script>

<template>
  <div class="-m-6 min-h-[calc(100vh-5rem)] bg-[#f8f4f1] text-slate-950">
    <RouterView v-slot="{ Component }">
      <component :is="Component" @refresh-overview="fetchOverview" />
    </RouterView>
  </div>
</template>
