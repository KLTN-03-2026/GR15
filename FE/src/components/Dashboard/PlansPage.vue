<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { subscriptionService, walletService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'
import {
  getBillingFeatureLabel,
  getEntitlementLabel,
  getFreeQuotaText,
  getSubscriptionQuotaText,
  sortEntitlementsByFeature,
} from '@/utils/billing'

const notify = useNotify()
const route = useRoute()
const router = useRouter()

const loading = ref(false)
const purchasingCode = ref('')
const selectedGateway = ref('momo')
const plans = ref([])
const currentSubscription = ref(null)
const entitlements = ref([])
const wallet = ref(null)
const paymentGateways = [
  {
    value: 'momo',
    label: 'MoMo',
    description: 'Ví điện tử, chuyển nhanh sang app',
  },
  {
    value: 'vnpay',
    label: 'VNPay',
    description: 'ATM, QR hoặc ứng dụng ngân hàng',
  },
  {
    value: 'wallet',
    label: 'Ví AI',
    description: 'Dùng số dư hiện có để kích hoạt ngay',
  },
]

const formatCurrency = (value) =>
  `${new Intl.NumberFormat('vi-VN').format(Number(value || 0))} đ`

const getGatewayLabel = (gateway) => {
  if (gateway === 'vnpay') return 'VNPay'
  if (gateway === 'momo') return 'MoMo'
  if (gateway === 'wallet') return 'Ví AI'
  return 'cổng thanh toán'
}

const cycleLabel = (cycle) => {
  if (cycle === 'free') return 'Mặc định'
  if (cycle === 'monthly') return 'Theo tháng'
  if (cycle === 'yearly') return 'Theo năm'
  return cycle || 'Không xác định'
}

const currentPlanCode = computed(() => currentSubscription.value?.goi_dich_vu?.ma_goi || null)
const walletAvailable = computed(() => Number(wallet.value?.so_du_kha_dung || 0))

const entitlementRows = computed(() => sortEntitlementsByFeature(entitlements.value))

const sortedPlans = computed(() =>
  [...plans.value].sort((left, right) => Number(left.is_free || 0) - Number(right.is_free || 0) || Number(left.gia || 0) - Number(right.gia || 0))
)

const loadPlans = async () => {
  loading.value = true
  try {
    const [plansResponse, currentResponse, entitlementsResponse, walletResponse] = await Promise.all([
      subscriptionService.getPlans(),
      subscriptionService.getCurrent(),
      subscriptionService.getEntitlements(),
      walletService.getWallet(),
    ])

    plans.value = plansResponse?.data || []
    currentSubscription.value = currentResponse?.data || null
    entitlements.value = entitlementsResponse?.data?.entitlements || []
    wallet.value = walletResponse?.data?.wallet || null
  } catch (error) {
    notify.apiError(error, 'Không thể tải dữ liệu gói Pro.')
  } finally {
    loading.value = false
  }
}

const maybeHandleReturn = async () => {
  const status = typeof route.query.subscription === 'string' ? route.query.subscription : ''
  if (!status) return

  await loadPlans()

  const message = typeof route.query.message === 'string' && route.query.message
    ? route.query.message
    : (status === 'success'
        ? 'Kích hoạt gói Pro thành công.'
        : status === 'pending'
          ? 'Giao dịch đang chờ xác nhận thêm từ hệ thống.'
          : 'Thanh toán gói Pro chưa thành công.')

  if (status === 'success') {
    notify.success(message)
  } else if (status === 'pending') {
    notify.warning(message)
  } else {
    notify.error(message)
  }

  await router.replace({ path: '/plans' })
}

const purchasePlan = async (planCode) => {
  purchasingCode.value = planCode
  try {
    const createPayment = selectedGateway.value === 'wallet'
      ? subscriptionService.createWalletPurchase
      : selectedGateway.value === 'vnpay'
        ? subscriptionService.createVnpayPurchase
        : subscriptionService.createMomoPurchase
    const response = await createPayment(planCode)
    const payUrl = response?.data?.pay_url || ''
    const payment = response?.data?.payment || null

    if (payUrl) {
      window.location.href = payUrl
      return
    }

    if (selectedGateway.value === 'wallet' && payment?.trang_thai === 'success') {
      await loadPlans()
      notify.success(response?.message || 'Đã kích hoạt gói Pro bằng ví AI.')
      return
    }

    notify.warning('Giao dịch đã được tạo nhưng chưa có liên kết thanh toán để chuyển tiếp.')
  } catch (error) {
    notify.apiError(error, `Không thể tạo giao dịch mua gói Pro qua ${getGatewayLabel(selectedGateway.value)}.`)
  } finally {
    purchasingCode.value = ''
  }
}

onMounted(async () => {
  await maybeHandleReturn()

  if (typeof route.query.subscription !== 'string') {
    await loadPlans()
  }
})
</script>

<template>
  <div class="space-y-8">
    <section class="overflow-hidden rounded-[30px] border border-blue-200 bg-gradient-to-r from-[#0f163e] via-[#183389] to-[#2463eb] px-8 py-8 text-white shadow-[0_28px_90px_rgba(37,99,235,0.22)]">
      <div class="grid gap-6 lg:grid-cols-[minmax(0,1.45fr)_360px] lg:items-end">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.38em] text-blue-100/80">Pro Plans</p>
          <h1 class="mt-3 text-4xl font-black tracking-tight">Gói Pro cho AI Center</h1>
          <p class="mt-4 max-w-3xl text-base leading-8 text-blue-50/90">
            Free quota sẽ được dùng trước. Khi cần hạn mức lớn hơn cho chatbot, mock interview, cover letter và career report,
            bạn có thể kích hoạt Pro và thanh toán qua MoMo hoặc VNPay.
          </p>
        </div>

        <div class="rounded-[24px] border border-white/15 bg-white/10 p-5 backdrop-blur">
          <p class="text-sm font-semibold text-white/90">Trạng thái hiện tại</p>
          <template v-if="currentSubscription?.goi_dich_vu">
            <h2 class="mt-3 text-2xl font-black">{{ currentSubscription.goi_dich_vu.ten_goi }}</h2>
            <p class="mt-2 text-sm leading-7 text-blue-50/90">
              Hiệu lực đến:
              {{ currentSubscription.ngay_het_han ? new Intl.DateTimeFormat('vi-VN', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(currentSubscription.ngay_het_han)) : 'Không giới hạn' }}
            </p>
          </template>
          <p v-else class="mt-3 text-sm leading-7 text-blue-50/90">
            Bạn đang ở lớp Free mặc định. Hệ thống sẽ dùng free quota trước rồi mới đến ví AI.
          </p>
        </div>
      </div>
    </section>

    <div class="grid gap-6 xl:grid-cols-[300px_minmax(0,1fr)]">
      <div class="space-y-6">
        <section class="rounded-[28px] border border-slate-200 bg-white/95 p-6 shadow-[0_22px_60px_rgba(148,163,184,0.12)] dark:border-slate-800 dark:bg-slate-900/85">
          <p class="text-xs font-semibold uppercase tracking-[0.32em] text-blue-500/80">Current Plan</p>
          <h2 class="mt-3 text-2xl font-black text-slate-900 dark:text-white">
            {{ currentSubscription?.goi_dich_vu?.ten_goi || 'Free mặc định' }}
          </h2>
          <p class="mt-3 text-sm leading-7 text-slate-600 dark:text-slate-400">
            {{ currentSubscription?.goi_dich_vu?.mo_ta || 'Bạn chưa kích hoạt gói Pro. Các tính năng AI sẽ dùng free quota trước, sau đó fallback sang ví AI.' }}
          </p>

          <div class="mt-5 space-y-3">
            <RouterLink
              :to="{ name: 'Wallet' }"
              class="inline-flex w-full items-center justify-center gap-2 rounded-2xl border border-slate-200 px-4 py-3 text-sm font-bold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
            >
              <span class="material-symbols-outlined text-[18px]">account_balance_wallet</span>
              Nạp ví AI
            </RouterLink>

            <RouterLink
              :to="{ name: 'Payments' }"
              class="inline-flex w-full items-center justify-center gap-2 rounded-2xl border border-slate-200 px-4 py-3 text-sm font-bold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
            >
              <span class="material-symbols-outlined text-[18px]">receipt_long</span>
              Lịch sử thanh toán
            </RouterLink>

            <RouterLink
              :to="{ name: 'AICenterChatbot' }"
              class="inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-slate-900 px-4 py-3 text-sm font-bold text-white transition hover:brightness-110 dark:bg-slate-100 dark:text-slate-900"
            >
              <span class="material-symbols-outlined text-[18px]">auto_awesome</span>
              Đi tới AI Center
            </RouterLink>
          </div>
        </section>

        <section class="rounded-[28px] border border-slate-200 bg-white/95 p-6 shadow-[0_22px_60px_rgba(148,163,184,0.12)] dark:border-slate-800 dark:bg-slate-900/85">
          <p class="text-xs font-semibold uppercase tracking-[0.32em] text-blue-500/80">Quota hiện tại</p>
          <div class="mt-4 space-y-3">
            <article
              v-for="item in entitlementRows"
              :key="item.feature_code"
              class="rounded-2xl border border-slate-200 bg-slate-50/80 p-4 dark:border-slate-700 dark:bg-slate-950/45"
            >
              <p class="text-sm font-bold text-slate-900 dark:text-white">{{ getEntitlementLabel(item) }}</p>
              <div class="mt-3 space-y-2 text-xs">
                <div class="flex items-center justify-between gap-3">
                  <span class="text-slate-500 dark:text-slate-400">Free còn</span>
                  <span class="font-bold text-slate-900 dark:text-white">{{ getFreeQuotaText(item) }}</span>
                </div>
                <div class="flex items-center justify-between gap-3">
                  <span class="text-slate-500 dark:text-slate-400">Pro còn</span>
                  <span class="font-bold text-slate-900 dark:text-white">{{ getSubscriptionQuotaText(item, { hasCurrentSubscription: Boolean(currentSubscription) }) }}</span>
                </div>
              </div>
            </article>
          </div>
        </section>
      </div>

      <section class="space-y-4">
        <div class="rounded-[28px] border border-slate-200 bg-white/95 p-5 shadow-[0_22px_60px_rgba(148,163,184,0.12)] dark:border-slate-800 dark:bg-slate-900/85">
          <div class="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.32em] text-blue-500/80">Payment Gateway</p>
              <h2 class="mt-2 text-xl font-black text-slate-900 dark:text-white">Chọn cổng thanh toán cho giao dịch mới</h2>
              <p class="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-400">
                Lựa chọn này sẽ được dùng khi bạn bấm mua một gói Pro bên dưới. Nếu chọn Ví AI, hệ thống sẽ trừ số dư và kích hoạt ngay.
              </p>
            </div>
            <p class="text-sm font-semibold text-blue-700 dark:text-blue-200">
              Đang chọn: {{ getGatewayLabel(selectedGateway) }}
            </p>
          </div>

          <div class="mt-5 grid gap-3 sm:grid-cols-2">
            <button
              v-for="gateway in paymentGateways"
              :key="gateway.value"
              type="button"
              class="rounded-2xl border px-4 py-3 text-left transition"
              :class="selectedGateway === gateway.value
                ? 'border-blue-500 bg-blue-500/10 shadow-[0_16px_30px_rgba(37,99,235,0.12)]'
                : 'border-slate-200 bg-slate-50 hover:border-slate-300 dark:border-slate-700 dark:bg-slate-950/60 dark:hover:border-slate-600'"
              @click="selectedGateway = gateway.value"
            >
              <div class="flex items-center justify-between gap-3">
                <div>
                  <p class="text-sm font-bold text-slate-900 dark:text-white">{{ gateway.label }}</p>
                  <p class="mt-1 text-xs text-slate-600 dark:text-slate-400">
                    {{ gateway.value === 'wallet' ? `${gateway.description} · Khả dụng ${formatCurrency(walletAvailable)}` : gateway.description }}
                  </p>
                </div>
                <span
                  class="h-5 w-5 rounded-full border transition"
                  :class="selectedGateway === gateway.value
                    ? 'border-blue-500 bg-blue-500 shadow-[inset_0_0_0_4px_white]'
                    : 'border-slate-300 bg-white dark:border-slate-600 dark:bg-slate-900'"
                ></span>
              </div>
            </button>
          </div>
        </div>

        <div v-if="loading" class="grid gap-4 lg:grid-cols-2">
          <div v-for="index in 3" :key="index" class="h-72 animate-pulse rounded-[28px] bg-slate-100 dark:bg-slate-800/70"></div>
        </div>

        <div v-else class="grid gap-4 lg:grid-cols-2">
          <article
            v-for="plan in sortedPlans"
            :key="plan.id"
            class="rounded-[28px] border bg-white/95 p-6 shadow-[0_22px_60px_rgba(148,163,184,0.12)] dark:bg-slate-900/85"
            :class="plan.ma_goi === currentPlanCode
              ? 'border-blue-400 ring-2 ring-blue-200/70 dark:border-blue-500 dark:ring-blue-500/20'
              : 'border-slate-200 dark:border-slate-800'"
          >
            <div class="flex items-start justify-between gap-4">
              <div>
                <h2 class="text-2xl font-black text-slate-900 dark:text-white">{{ plan.ten_goi }}</h2>
                <p class="mt-3 text-sm leading-7 text-slate-600 dark:text-slate-400">{{ plan.mo_ta }}</p>
              </div>
              <span
                v-if="plan.ma_goi === currentPlanCode"
                class="inline-flex items-center justify-center text-center rounded-full bg-blue-500/10 px-3 py-1 text-xs font-bold uppercase tracking-wide text-blue-700 dark:text-blue-200"
              >
                Đang dùng
              </span>
            </div>

            <div class="mt-5 rounded-2xl border border-slate-200 bg-slate-50/80 p-4 dark:border-slate-700 dark:bg-slate-950/45">
              <p class="text-3xl font-black text-slate-900 dark:text-white">
                {{ Number(plan.gia || 0) > 0 ? formatCurrency(plan.gia) : 'Miễn phí' }}
              </p>
              <p class="mt-2 text-sm text-slate-600 dark:text-slate-400">{{ cycleLabel(plan.chu_ky) }}</p>
            </div>

            <div class="mt-5 space-y-3">
              <div
                v-for="feature in plan.tinh_nangs || []"
                :key="feature.id"
                class="flex items-center justify-between gap-3 rounded-2xl border border-slate-200 bg-white/80 px-4 py-3 text-sm dark:border-slate-700 dark:bg-slate-950/30"
              >
                <span class="font-medium text-slate-700 dark:text-slate-200">{{ getBillingFeatureLabel(feature.feature_code) }}</span>
                <span class="font-bold text-slate-900 dark:text-white">
                  {{ feature.is_unlimited ? 'Không giới hạn' : `${feature.quota || 0} lượt` }}
                </span>
              </div>
            </div>

            <button
              type="button"
              class="mt-5 inline-flex w-full items-center justify-center gap-2 rounded-2xl px-5 py-3.5 text-sm font-bold transition disabled:cursor-not-allowed disabled:opacity-70"
              :class="plan.is_free || plan.ma_goi === currentPlanCode
                ? 'border border-slate-200 bg-slate-100 text-slate-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-400'
                : 'bg-gradient-to-r from-blue-600 to-cyan-500 text-white shadow-[0_18px_32px_rgba(37,99,235,0.24)] hover:brightness-110'"
              :disabled="plan.is_free || plan.ma_goi === currentPlanCode || purchasingCode === plan.ma_goi"
              @click="purchasePlan(plan.ma_goi)"
            >
              <span class="material-symbols-outlined text-[18px]">
                {{ purchasingCode === plan.ma_goi ? 'hourglass_top' : 'payments' }}
              </span>
              <span>
                {{
                  plan.is_free
                    ? 'Gói mặc định'
                    : plan.ma_goi === currentPlanCode
                      ? 'Đang kích hoạt'
                      : purchasingCode === plan.ma_goi
                        ? 'Đang tạo giao dịch...'
                        : selectedGateway === 'wallet'
                          ? `Mua bằng ${getGatewayLabel(selectedGateway)}`
                          : `Mua qua ${getGatewayLabel(selectedGateway)}`
                }}
              </span>
            </button>
          </article>
        </div>
      </section>
    </div>
  </div>
</template>
