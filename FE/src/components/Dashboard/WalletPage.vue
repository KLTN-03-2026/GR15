<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { subscriptionService, walletService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'
import {
  getBillingFeatureLabel,
} from '@/utils/billing'

const notify = useNotify()
const route = useRoute()
const router = useRouter()

const loading = ref(false)
const refreshing = ref(false)
const creatingTopUp = ref(false)
const selectedAmount = ref(50000)
const selectedGateway = ref('momo')
const wallet = ref(null)
const pricing = ref([])
const plans = ref([])
const transactions = ref([])
const paymentDraft = ref(null)

const pagination = reactive({
  current_page: 1,
  last_page: 1,
  per_page: 10,
  total: 0,
  from: 0,
  to: 0,
})

const quickAmounts = [20000, 50000, 100000, 200000]
const paymentGateways = [
  {
    value: 'momo',
    label: 'MoMo',
    description: 'Ví điện tử, quét QR nhanh',
  },
  {
    value: 'vnpay',
    label: 'VNPay',
    description: 'ATM, QR hoặc app ngân hàng',
  },
]

const walletStats = computed(() => ({
  current: Number(wallet.value?.so_du_hien_tai || 0),
  hold: Number(wallet.value?.so_du_tam_giu || 0),
  available: Number(wallet.value?.so_du_kha_dung || 0),
}))

const pricedFeatures = computed(() =>
  [...pricing.value].sort((left, right) => Number(left.don_gia || 0) - Number(right.don_gia || 0))
)

const proPlans = computed(() => {
  const paidPlans = plans.value.filter((plan) => !Number(plan.is_free || 0) && Number(plan.gia || 0) > 0)
  return [...paidPlans].sort((left, right) => Number(left.gia || 0) - Number(right.gia || 0))
})

const formatCurrency = (value) =>
  `${new Intl.NumberFormat('vi-VN').format(Number(value || 0))} đ`

const getGatewayLabel = (gateway) => {
  if (gateway === 'vnpay') return 'VNPay'
  if (gateway === 'momo') return 'MoMo'
  return 'cổng thanh toán'
}

const formatDateTime = (value) => {
  if (!value) return 'Chưa cập nhật'

  return new Intl.DateTimeFormat('vi-VN', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(new Date(value))
}

const cycleLabel = (cycle) => {
  if (cycle === 'free') return 'Mặc định'
  if (cycle === 'monthly') return 'Theo tháng'
  if (cycle === 'yearly') return 'Theo năm'
  return cycle || 'Không xác định'
}

const getFeatureDescription = (featureCode) => {
  if (featureCode === 'cv_builder_ai') return 'AI gợi ý nội dung CV và thư ứng tuyển theo hồ sơ.'
  if (featureCode === 'career_report_ai') return 'Sinh báo cáo định hướng nghề nghiệp dựa trên kỹ năng và mục tiêu.'
  if (featureCode === 'career_chatbot_message') return 'Chatbot tư vấn nghề nghiệp, lộ trình học và chuẩn bị ứng tuyển.'
  if (featureCode === 'mock_interview_session') return 'Tạo phiên luyện phỏng vấn mô phỏng theo vị trí và kỹ năng.'
  return 'Tính năng AI đang bật theo mô hình pay-per-use từ ví.'
}

const getTransactionLabel = (transaction) => {
  switch (transaction?.loai_bien_dong) {
    case 'topup_credit':
      return 'Nạp tiền vào ví'
    case 'usage_reserve':
      return `Tạm giữ cho ${getBillingFeatureLabel(transaction?.metadata_json?.feature_code)}`
    case 'usage_capture':
      return `Đã thanh toán cho ${getBillingFeatureLabel(transaction?.metadata_json?.feature_code)}`
    case 'usage_release':
      return `Hoàn tạm giữ cho ${getBillingFeatureLabel(transaction?.metadata_json?.feature_code)}`
    default:
      return transaction?.mo_ta || 'Biến động ví'
  }
}

const getTransactionStatusLabel = (transaction) => {
  switch (transaction?.loai_bien_dong) {
    case 'topup_credit':
      return 'Nạp tiền'
    case 'usage_reserve':
      return 'Tạm giữ'
    case 'usage_capture':
      return 'Đã thanh toán'
    case 'usage_release':
      return 'Hoàn tạm giữ'
    default:
      return 'Biến động ví'
  }
}

const getTransactionDescription = (transaction) => {
  const featureLabel = getBillingFeatureLabel(transaction?.metadata_json?.feature_code)

  switch (transaction?.loai_bien_dong) {
    case 'topup_credit':
      return 'Số tiền đã được cộng vào ví AI của bạn.'
    case 'usage_reserve':
      return `Hệ thống đang tạm giữ tiền để xử lý ${featureLabel}.`
    case 'usage_capture':
      return `Yêu cầu ${featureLabel} đã hoàn tất và số tiền đã được khấu trừ từ ví.`
    case 'usage_release':
      return `Yêu cầu ${featureLabel} không hoàn tất nên số tiền tạm giữ đã được hoàn lại.`
    default:
      return transaction?.mo_ta || 'Không có mô tả thêm.'
  }
}

const getTransactionTone = (transaction) => {
  switch (transaction?.loai_bien_dong) {
    case 'topup_credit':
      return 'bg-emerald-500/10 text-emerald-700 border-emerald-200 dark:text-emerald-200 dark:border-emerald-500/20'
    case 'usage_capture':
      return 'bg-rose-500/10 text-rose-700 border-rose-200 dark:text-rose-200 dark:border-rose-500/20'
    case 'usage_release':
      return 'bg-amber-500/10 text-amber-700 border-amber-200 dark:text-amber-200 dark:border-amber-500/20'
    default:
      return 'bg-blue-500/10 text-blue-700 border-blue-200 dark:text-blue-200 dark:border-blue-500/20'
  }
}

const normalizeTransactions = (response) => {
  const payload = response?.data || {}
  transactions.value = payload.data || []
  pagination.current_page = payload.current_page || 1
  pagination.last_page = payload.last_page || 1
  pagination.total = payload.total || 0
  pagination.from = payload.from || 0
  pagination.to = payload.to || 0
}

const loadBillingData = async (page = pagination.current_page, showLoading = true) => {
  if (showLoading) {
    loading.value = true
  } else {
    refreshing.value = true
  }

  try {
    const [walletResponse, pricingResponse, plansResponse, transactionsResponse] = await Promise.all([
      walletService.getWallet(),
      walletService.getPricing(),
      subscriptionService.getPlans(),
      walletService.getTransactions({
        page,
        per_page: pagination.per_page,
      }),
    ])

    wallet.value = walletResponse?.data?.wallet || null
    pricing.value = pricingResponse?.data || []
    plans.value = plansResponse?.data || []
    normalizeTransactions(transactionsResponse)
  } catch (error) {
    notify.apiError(error, 'Không thể tải dữ liệu ví AI.')
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

const changePage = async (page) => {
  if (page < 1 || page > pagination.last_page || page === pagination.current_page) return
  await loadBillingData(page, false)
}

const maybeHandleTopUpReturn = async () => {
  if (route.query.topup !== 'success') return

  const message = typeof route.query.message === 'string' && route.query.message
    ? route.query.message
    : 'Nạp tiền thành công.'

  await loadBillingData(1)
  notify.success(message)

  await router.replace({ path: '/wallet' })
}

const createTopUp = async () => {
  const amount = Number(selectedAmount.value || 0)
  if (!Number.isFinite(amount) || amount < 1000) {
    notify.warning('Số tiền nạp tối thiểu là 1.000 đ.')
    return
  }

  creatingTopUp.value = true
  try {
    const createPayment = selectedGateway.value === 'vnpay'
      ? walletService.createVnpayTopUp
      : walletService.createMomoTopUp
    const response = await createPayment(amount)
    const payment = response?.data?.payment || null
    const payUrl = response?.data?.pay_url || ''

    paymentDraft.value = payment

    if (payUrl) {
      window.location.href = payUrl
    } else if (payment?.ma_giao_dich_noi_bo) {
      notify.warning('Giao dịch đã được tạo nhưng chưa có liên kết thanh toán để chuyển tiếp.')
    }
  } catch (error) {
    notify.apiError(error, `Không thể tạo giao dịch nạp tiền qua ${getGatewayLabel(selectedGateway.value)}.`)
  } finally {
    creatingTopUp.value = false
  }
}

onMounted(async () => {
  await maybeHandleTopUpReturn()

  if (route.query.topup !== 'success') {
    await loadBillingData(1)
  }
})
</script>

<template>
  <div class="space-y-8">
    <section class="overflow-hidden rounded-[30px] border border-emerald-200 bg-gradient-to-r from-[#082f28] via-[#0f5f53] to-[#3aa78d] px-8 py-8 text-white shadow-[0_28px_90px_rgba(15,118,110,0.22)]">
        <div class="grid gap-6 lg:grid-cols-[minmax(0,1.4fr)_360px] lg:items-center">
          <div class="flex flex-col justify-center">
          <p class="text-xs font-semibold uppercase tracking-[0.38em] text-emerald-100/75">AI Wallet</p>
          <h1 class="mt-3 text-4xl font-black tracking-tight">Ví AI và lịch sử khấu trừ</h1>
          <p class="mt-4 max-w-3xl text-base leading-8 text-emerald-50/90">
            Nạp tiền vào ví qua MoMo hoặc VNPay, theo dõi số dư khả dụng và xem rõ từng lần AI giữ tiền, khấu trừ hoặc hoàn lại.
          </p>
        </div>

        <div class="rounded-[24px] border border-white/15 bg-white/10 p-5 backdrop-blur">
          <p class="text-sm font-semibold text-white/90">Quy tắc hiện tại</p>
          <ul class="mt-4 space-y-2 text-sm leading-7 text-emerald-50/90">
            <li>1. MoMo và VNPay chỉ dùng để nạp ví, không thanh toán từng request AI riêng lẻ.</li>
            <li>2. Free quota và quota Pro được theo dõi riêng cho từng tính năng AI.</li>
            <li>3. Khi cần, bạn có thể xem ngay số lượt còn lại của từng lớp ở phần hạn mức bên dưới.</li>
          </ul>
        </div>
      </div>
    </section>

    <div class="grid gap-5 md:grid-cols-3">
      <article class="rounded-2xl border border-slate-200 bg-white/95 p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900/85">
        <p class="text-sm font-medium text-slate-500 dark:text-slate-400">Số dư hiện tại</p>
        <h2 class="mt-3 text-3xl font-black text-slate-900 dark:text-white">
          {{ loading ? '...' : formatCurrency(walletStats.current) }}
        </h2>
      </article>
      <article class="rounded-2xl border border-slate-200 bg-white/95 p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900/85">
        <p class="text-sm font-medium text-slate-500 dark:text-slate-400">Đang tạm giữ</p>
        <h2 class="mt-3 text-3xl font-black text-slate-900 dark:text-white">
          {{ loading ? '...' : formatCurrency(walletStats.hold) }}
        </h2>
      </article>
      <article class="rounded-2xl border border-slate-200 bg-white/95 p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900/85">
        <p class="text-sm font-medium text-slate-500 dark:text-slate-400">Khả dụng để dùng AI</p>
        <h2 class="mt-3 text-3xl font-black text-emerald-700 dark:text-emerald-200">
          {{ loading ? '...' : formatCurrency(walletStats.available) }}
        </h2>
      </article>
    </div>

    <div class="grid gap-6 xl:grid-cols-[380px_minmax(0,1fr)]">
      <aside class="space-y-6">
        <section class="rounded-[28px] border border-slate-200 bg-white/95 p-6 shadow-[0_22px_60px_rgba(148,163,184,0.12)] dark:border-slate-800 dark:bg-slate-900/85">
          <div class="flex items-start justify-between gap-4">
            <div>
              <h2 class="text-2xl font-bold text-slate-900 dark:text-white">Nạp tiền vào ví AI</h2>
              <p class="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-400">
                Chọn cổng thanh toán, mức nạp nhanh hoặc nhập số tiền riêng. Sau khi tạo giao dịch, hệ thống sẽ mở trang thanh toán tương ứng.
              </p>
            </div>
            <span class="material-symbols-outlined rounded-2xl bg-emerald-500/10 p-3 text-emerald-500">account_balance_wallet</span>
          </div>

          <div class="mt-5 grid gap-3 sm:grid-cols-2">
            <button
              v-for="gateway in paymentGateways"
              :key="gateway.value"
              type="button"
              class="rounded-2xl border px-4 py-3 text-left transition"
              :class="selectedGateway === gateway.value
                ? 'border-emerald-500 bg-emerald-500/10 shadow-[0_16px_30px_rgba(16,185,129,0.12)]'
                : 'border-slate-200 bg-slate-50 hover:border-slate-300 dark:border-slate-700 dark:bg-slate-950/60 dark:hover:border-slate-600'"
              @click="selectedGateway = gateway.value"
            >
              <div class="flex items-center justify-between gap-3">
                <div>
                  <p class="text-sm font-bold text-slate-900 dark:text-white">{{ gateway.label }}</p>
                  <p class="mt-1 text-xs text-slate-600 dark:text-slate-400">{{ gateway.description }}</p>
                </div>
                <span
                  class="h-5 w-5 rounded-full border transition"
                  :class="selectedGateway === gateway.value
                    ? 'border-emerald-500 bg-emerald-500 shadow-[inset_0_0_0_4px_white]'
                    : 'border-slate-300 bg-white dark:border-slate-600 dark:bg-slate-900'"
                ></span>
              </div>
            </button>
          </div>

          <div class="mt-5 grid grid-cols-2 gap-3">
            <button
              v-for="amount in quickAmounts"
              :key="amount"
              type="button"
              class="rounded-2xl border px-4 py-3 text-sm font-bold transition"
              :class="Number(selectedAmount) === amount
                ? 'border-emerald-500 bg-emerald-500 text-white'
                : 'border-slate-200 bg-slate-50 text-slate-700 hover:border-slate-300 dark:border-slate-700 dark:bg-slate-950/60 dark:text-slate-200 dark:hover:border-slate-600'"
              @click="selectedAmount = amount"
            >
              {{ formatCurrency(amount) }}
            </button>
          </div>

          <label class="mt-5 block">
            <span class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-300">Số tiền nạp</span>
            <input
              v-model.number="selectedAmount"
              type="number"
              min="1000"
              step="1000"
              class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-emerald-500 dark:border-slate-700 dark:bg-slate-950/70 dark:text-white"
            >
          </label>

          <button
            type="button"
            class="mt-5 inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-emerald-600 to-teal-500 px-5 py-3.5 text-sm font-bold text-white shadow-[0_18px_32px_rgba(16,185,129,0.24)] transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-70"
            :disabled="creatingTopUp"
            @click="createTopUp"
          >
            <span class="material-symbols-outlined">{{ creatingTopUp ? 'hourglass_top' : 'qr_code_2' }}</span>
            <span>{{ creatingTopUp ? 'Đang tạo giao dịch...' : `Tạo giao dịch ${getGatewayLabel(selectedGateway)}` }}</span>
          </button>

          <div v-if="paymentDraft" class="mt-5 rounded-2xl border border-emerald-200 bg-emerald-50/80 p-4 text-sm text-emerald-800 dark:border-emerald-500/20 dark:bg-emerald-500/10 dark:text-emerald-100">
            <p class="font-bold">Giao dịch gần nhất đã được tạo.</p>
            <p class="mt-2">Mã giao dịch: <span class="font-semibold">{{ paymentDraft.ma_giao_dich_noi_bo }}</span></p>
            <p class="mt-1">Số tiền: <span class="font-semibold">{{ formatCurrency(paymentDraft.so_tien) }}</span></p>
            <p class="mt-1">Cổng thanh toán: <span class="font-semibold">{{ getGatewayLabel(paymentDraft.gateway) }}</span></p>
            <p class="mt-1">Trạng thái cuối cùng sẽ cập nhật theo callback/IPN từ cổng thanh toán.</p>
          </div>

          <RouterLink
            :to="{ name: 'Payments' }"
            class="mt-5 inline-flex w-full items-center justify-center gap-2 rounded-2xl border border-slate-200 px-5 py-3.5 text-sm font-bold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
          >
            <span class="material-symbols-outlined text-[18px]">receipt_long</span>
            Xem lịch sử thanh toán
          </RouterLink>
        </section>

        <section class="rounded-[28px] border border-slate-200 bg-white/95 p-6 shadow-[0_22px_60px_rgba(148,163,184,0.12)] dark:border-slate-800 dark:bg-slate-900/85">
          <h2 class="text-2xl font-bold text-slate-900 dark:text-white">Bảng giá AI</h2>
          <p class="mt-2 text-sm text-slate-600 dark:text-slate-400">Gói Pro và các tính năng đang bật pay-per-use.</p>

          <div v-if="proPlans.length" class="mt-5">
            <p class="text-xs font-black uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">Gói Pro</p>
            <div class="mt-3 space-y-3">
              <article
                v-for="plan in proPlans"
                :key="plan.id"
                class="rounded-2xl border border-slate-200 bg-slate-50/80 p-4 dark:border-slate-700 dark:bg-slate-950/50"
              >
                <div class="flex items-start justify-between gap-4">
                  <div>
                    <p class="text-sm font-bold text-slate-900 dark:text-white">{{ plan.ten_goi }}</p>
                    <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">{{ plan.mo_ta || cycleLabel(plan.chu_ky) }}</p>
                    <RouterLink
                      :to="{ name: 'Plans' }"
                      class="mt-3 inline-flex items-center gap-1 text-xs font-bold text-emerald-700 hover:underline dark:text-emerald-200"
                    >
                      Xem gói
                      <span class="material-symbols-outlined text-[16px]">arrow_forward</span>
                    </RouterLink>
                  </div>
                  <span class="rounded-2xl bg-emerald-500/10 px-3 py-2 text-sm font-black text-emerald-700 dark:text-emerald-200">
                    {{ formatCurrency(plan.gia) }}
                  </span>
                </div>
              </article>
            </div>
          </div>

          <div class="mt-6">
            <p class="text-xs font-black uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">AI Pay-Per-Use</p>
            <div class="mt-3 space-y-3">
            <article
              v-for="item in pricedFeatures"
              :key="item.id"
              class="rounded-2xl border border-slate-200 bg-slate-50/80 p-4 dark:border-slate-700 dark:bg-slate-950/50"
            >
              <div class="flex items-start justify-between gap-4">
                <div>
                  <p class="text-sm font-bold text-slate-900 dark:text-white">{{ item.ten_hien_thi }}</p>
                  <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">{{ getFeatureDescription(item.feature_code) }}</p>
                </div>
                <span class="rounded-2xl bg-blue-500/10 px-3 py-2 text-sm font-black text-blue-700 dark:text-blue-200">
                  {{ formatCurrency(item.don_gia) }}
                </span>
              </div>
            </article>
            </div>
          </div>
        </section>
      </aside>

      <section class="rounded-[28px] border border-slate-200 bg-white/95 p-6 shadow-[0_22px_60px_rgba(148,163,184,0.12)] dark:border-slate-800 dark:bg-slate-900/85">
        <div class="flex flex-col gap-4 border-b border-slate-200 pb-5 md:flex-row md:items-center md:justify-between dark:border-slate-800">
          <div>
            <h2 class="text-2xl font-bold text-slate-900 dark:text-white">Lịch sử biến động ví</h2>
            <p class="mt-2 text-sm text-slate-600 dark:text-slate-400">
              {{ pagination.total }} giao dịch · từ {{ pagination.from || 0 }} đến {{ pagination.to || 0 }}
            </p>
          </div>

          <button
            type="button"
            class="inline-flex items-center gap-2 rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:opacity-60 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
            :disabled="refreshing"
            @click="loadBillingData(pagination.current_page, false)"
          >
            <span class="material-symbols-outlined">{{ refreshing ? 'progress_activity' : 'refresh' }}</span>
            Làm mới
          </button>
        </div>

        <div v-if="loading" class="mt-5 space-y-3">
          <div v-for="index in 6" :key="index" class="h-24 animate-pulse rounded-2xl bg-slate-100 dark:bg-slate-800/70"></div>
        </div>

        <div v-else-if="!transactions.length" class="mt-5 rounded-2xl border border-dashed border-slate-300 bg-slate-50/70 px-6 py-12 text-center text-sm leading-7 text-slate-600 dark:border-slate-700 dark:bg-slate-950/40 dark:text-slate-400">
          Chưa có biến động ví nào. Hãy nạp tiền hoặc dùng một tính năng AI trả phí để lịch sử bắt đầu xuất hiện.
        </div>

        <div v-else class="mt-5 space-y-3">
          <article
            v-for="transaction in transactions"
            :key="transaction.id"
            class="rounded-2xl border border-slate-200 bg-slate-50/80 p-4 transition dark:border-slate-700 dark:bg-slate-950/45"
          >
            <div class="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
              <div class="min-w-0">
                <div class="flex flex-wrap items-center gap-2">
                  <p class="text-base font-bold text-slate-900 dark:text-white">{{ getTransactionLabel(transaction) }}</p>
                  <span class="rounded-full border px-2.5 py-1 text-[11px] font-bold uppercase tracking-wide" :class="getTransactionTone(transaction)">
                    {{ getTransactionStatusLabel(transaction) }}
                  </span>
                </div>
                <p class="mt-2 text-sm text-slate-600 dark:text-slate-400">
                  {{ getTransactionDescription(transaction) }}
                </p>
                <p class="mt-2 text-xs uppercase tracking-[0.25em] text-slate-500">
                  {{ formatDateTime(transaction.created_at) }}
                </p>
              </div>

              <div class="grid min-w-[220px] gap-2 text-sm">
                <div class="flex items-center justify-between rounded-xl bg-white/85 px-3 py-2 dark:bg-slate-900/80">
                  <span class="text-slate-500 dark:text-slate-400">Số tiền</span>
                  <span class="font-bold text-slate-900 dark:text-white">{{ formatCurrency(transaction.so_tien) }}</span>
                </div>
                <div class="flex items-center justify-between rounded-xl bg-white/85 px-3 py-2 dark:bg-slate-900/80">
                  <span class="text-slate-500 dark:text-slate-400">Số dư sau</span>
                  <span class="font-bold text-slate-900 dark:text-white">{{ formatCurrency(transaction.so_du_sau) }}</span>
                </div>
                <div class="flex items-center justify-between rounded-xl bg-white/85 px-3 py-2 dark:bg-slate-900/80">
                  <span class="text-slate-500 dark:text-slate-400">Tạm giữ sau</span>
                  <span class="font-bold text-slate-900 dark:text-white">{{ formatCurrency(transaction.tam_giu_sau) }}</span>
                </div>
              </div>
            </div>
          </article>
        </div>

        <div v-if="pagination.last_page > 1" class="mt-6 flex flex-wrap items-center justify-center gap-2">
          <button
            type="button"
            class="rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:opacity-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
            :disabled="pagination.current_page === 1"
            @click="changePage(pagination.current_page - 1)"
          >
            Trước
          </button>

          <button
            v-for="page in pagination.last_page"
            :key="page"
            type="button"
            class="h-11 min-w-11 rounded-xl border px-4 text-sm font-bold transition"
            :class="page === pagination.current_page
              ? 'border-emerald-600 bg-emerald-600 text-white'
              : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800'"
            @click="changePage(page)"
          >
            {{ page }}
          </button>

          <button
            type="button"
            class="rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:opacity-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
            :disabled="pagination.current_page === pagination.last_page"
            @click="changePage(pagination.current_page + 1)"
          >
            Sau
          </button>
        </div>
      </section>
    </div>
  </div>
</template>
