<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { employerBillingService } from '@/services/api'
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
const selectedAmount = ref(100000)
const selectedGateway = ref('momo')
const wallet = ref(null)
const pricing = ref([])
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

const quickAmounts = [50000, 100000, 200000, 500000]
const paymentGateways = [
  {
    value: 'momo',
    label: 'MoMo',
    description: 'Quét QR hoặc ví điện tử',
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

const featuredPricing = computed(() =>
  pricing.value.filter((item) => String(item.feature_code || '').startsWith('employer_featured_job_'))
)
const aiPricing = computed(() =>
  pricing.value.filter((item) => !String(item.feature_code || '').startsWith('employer_featured_job_'))
)

const formatCurrency = (value) =>
  `${new Intl.NumberFormat('vi-VN').format(Number(value || 0))} đ`

const formatDateTime = (value) => {
  if (!value) return 'Chưa cập nhật'

  return new Intl.DateTimeFormat('vi-VN', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(new Date(value))
}

const getGatewayLabel = (gateway) => {
  if (gateway === 'vnpay') return 'VNPay'
  if (gateway === 'momo') return 'MoMo'
  return 'cổng thanh toán'
}

const getFeatureDescription = (featureCode) => {
  if (featureCode === 'employer_featured_job_7d') return 'Đẩy tin lên nhóm nổi bật trong 7 ngày.'
  if (featureCode === 'employer_featured_job_30d') return 'Đẩy tin lên nhóm nổi bật trong 30 ngày.'
  if (featureCode === 'employer_shortlist_ai_explanation') return 'AI chấm nhanh shortlist và giải thích lý do phù hợp.'
  if (featureCode === 'employer_candidate_compare_ai') return 'AI so sánh nhiều CV trên cùng một JD.'
  if (featureCode === 'interview_copilot_generate') return 'Sinh câu hỏi và rubric phỏng vấn theo từng hồ sơ.'
  if (featureCode === 'interview_copilot_evaluate') return 'Đánh giá ghi chú phỏng vấn và gợi ý quyết định.'
  return 'Tính năng đang dùng ví AI pay-per-use.'
}

const getTransactionLabel = (transaction) => {
  switch (transaction?.loai_bien_dong) {
    case 'topup_credit':
      return 'Nạp tiền vào ví employer'
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

const getTransactionDescription = (transaction) => {
  const featureLabel = getBillingFeatureLabel(transaction?.metadata_json?.feature_code)

  switch (transaction?.loai_bien_dong) {
    case 'topup_credit':
      return 'Số tiền đã được cộng vào ví để dùng cho featured listing và các chức năng AI tuyển dụng.'
    case 'usage_reserve':
      return `Hệ thống đang tạm giữ tiền để xử lý ${featureLabel}.`
    case 'usage_capture':
      return `${featureLabel} đã hoàn tất và số tiền đã được khấu trừ.`
    case 'usage_release':
      return `${featureLabel} không hoàn tất nên số tiền tạm giữ đã được hoàn lại.`
    default:
      return transaction?.mo_ta || 'Không có mô tả thêm.'
  }
}

const getTransactionTone = (transaction) => {
  switch (transaction?.loai_bien_dong) {
    case 'topup_credit':
      return 'bg-emerald-500/10 text-emerald-700 border-emerald-200'
    case 'usage_capture':
      return 'bg-rose-500/10 text-rose-700 border-rose-200'
    case 'usage_release':
      return 'bg-amber-500/10 text-amber-700 border-amber-200'
    default:
      return 'bg-blue-500/10 text-blue-700 border-blue-200'
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
    const [walletResponse, pricingResponse, transactionsResponse] = await Promise.all([
      employerBillingService.getWallet(),
      employerBillingService.getPricing(),
      employerBillingService.getTransactions({
        page,
        per_page: pagination.per_page,
      }),
    ])

    wallet.value = walletResponse?.data?.wallet || null
    pricing.value = pricingResponse?.data || []
    normalizeTransactions(transactionsResponse)
  } catch (error) {
    notify.apiError(error, 'Không thể tải dữ liệu ví employer.')
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
  const topupState = typeof route.query.topup === 'string' ? route.query.topup : ''
  const orderId = typeof route.query.orderId === 'string' ? route.query.orderId : ''
  const message = typeof route.query.message === 'string' && route.query.message
    ? route.query.message
    : ''

  if (!topupState && !orderId) return

  if (orderId) {
    try {
      paymentDraft.value = (await employerBillingService.getTopUp(orderId))?.data || null
    } catch {
      paymentDraft.value = null
    }
  }

  await loadBillingData(1)

  if (topupState === 'success') {
    notify.success(message || 'Nạp tiền thành công.')
  } else if (topupState === 'failed') {
    notify.warning(message || 'Giao dịch nạp tiền chưa thành công.')
  } else if (topupState === 'pending') {
    notify.info(message || 'Giao dịch đang chờ đối soát từ cổng thanh toán.')
  }

  await router.replace({ path: '/employer/billing' })
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
      ? employerBillingService.createVnpayTopUp
      : employerBillingService.createMomoTopUp
    const response = await createPayment(amount)
    const payment = response?.data?.payment || null
    const payUrl = response?.data?.pay_url || ''

    paymentDraft.value = payment

    if (payUrl) {
      window.location.href = payUrl
      return
    }

    notify.warning('Giao dịch đã được tạo nhưng chưa có liên kết thanh toán để chuyển tiếp.')
  } catch (error) {
    notify.apiError(error, `Không thể tạo giao dịch nạp tiền qua ${getGatewayLabel(selectedGateway.value)}.`)
  } finally {
    creatingTopUp.value = false
  }
}

onMounted(async () => {
  await maybeHandleTopUpReturn()

  if (!route.query.topup && !route.query.orderId) {
    await loadBillingData(1)
  }
})
</script>

<template>
  <div class="space-y-8">
    <section class="overflow-hidden rounded-[30px] border border-slate-200 bg-gradient-to-r from-slate-950 via-[#143c8c] to-[#2f7de1] px-8 py-8 text-white shadow-[0_24px_70px_rgba(15,23,42,0.28)]">
      <div class="grid gap-6 lg:grid-cols-[minmax(0,1.35fr)_360px] lg:items-center">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.35em] text-blue-100/80">Employer Billing</p>
          <h1 class="mt-3 text-4xl font-black tracking-tight">Ví employer cho featured và AI tuyển dụng</h1>
          <p class="mt-4 max-w-3xl text-base leading-8 text-blue-50/90">
            Nạp tiền một lần để chạy Sponsored Job, AI Shortlist, Compare ứng viên và Interview Copilot. Hệ thống sẽ trừ ví tự động theo từng lượt AI thành công hoặc theo từng gói featured.
          </p>
        </div>

        <div class="rounded-[24px] border border-white/15 bg-white/10 p-5 backdrop-blur">
            <p class="text-sm font-semibold text-white/90">Dùng cho 3 nhóm chính</p>
            <ul class="mt-4 space-y-2 text-sm leading-7 text-blue-50/90">
              <li>1. Featured listing để tăng hiển thị tin tuyển dụng.</li>
              <li>2. AI Shortlist và Compare CV theo từng job.</li>
              <li>3. AI Interview Copilot pay-per-use trước và sau phỏng vấn.</li>
            </ul>
          </div>
      </div>
    </section>

    <div class="grid gap-5 md:grid-cols-3">
      <article class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <p class="text-sm font-medium text-slate-500">Số dư hiện tại</p>
        <h2 class="mt-3 text-3xl font-black text-slate-900">
          {{ loading ? '...' : formatCurrency(walletStats.current) }}
        </h2>
      </article>
      <article class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <p class="text-sm font-medium text-slate-500">Đang tạm giữ</p>
        <h2 class="mt-3 text-3xl font-black text-slate-900">
          {{ loading ? '...' : formatCurrency(walletStats.hold) }}
        </h2>
      </article>
      <article class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <p class="text-sm font-medium text-slate-500">Khả dụng để dùng</p>
        <h2 class="mt-3 text-3xl font-black text-emerald-700">
          {{ loading ? '...' : formatCurrency(walletStats.available) }}
        </h2>
      </article>
    </div>

    <div class="grid gap-6 xl:grid-cols-[380px_minmax(0,1fr)]">
      <aside class="space-y-6">
        <section class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
          <div class="flex items-start justify-between gap-4">
            <div>
              <h2 class="text-2xl font-bold text-slate-900">Nạp tiền vào ví employer</h2>
              <p class="mt-2 text-sm leading-6 text-slate-600">
                Dùng MoMo hoặc VNPay để nạp ví rồi chi tiêu dần cho featured listing và các chức năng AI.
              </p>
            </div>
            <span class="material-symbols-outlined rounded-2xl bg-blue-500/10 p-3 text-[#2463eb]">account_balance_wallet</span>
          </div>

          <div class="mt-5 grid gap-3 sm:grid-cols-2">
            <button
              v-for="gateway in paymentGateways"
              :key="gateway.value"
              type="button"
              class="rounded-2xl border px-4 py-3 text-left transition"
              :class="selectedGateway === gateway.value
                ? 'border-[#2463eb] bg-blue-50 shadow-sm'
                : 'border-slate-200 bg-slate-50 hover:border-slate-300'"
              @click="selectedGateway = gateway.value"
            >
              <p class="text-sm font-bold text-slate-900">{{ gateway.label }}</p>
              <p class="mt-1 text-xs text-slate-500">{{ gateway.description }}</p>
            </button>
          </div>

          <div class="mt-5 grid grid-cols-2 gap-3">
            <button
              v-for="amount in quickAmounts"
              :key="amount"
              type="button"
              class="rounded-2xl border px-4 py-3 text-sm font-bold transition"
              :class="Number(selectedAmount) === amount
                ? 'border-[#2463eb] bg-[#2463eb] text-white'
                : 'border-slate-200 bg-slate-50 text-slate-700 hover:border-slate-300'"
              @click="selectedAmount = amount"
            >
              {{ formatCurrency(amount) }}
            </button>
          </div>

          <label class="mt-5 block">
            <span class="mb-2 block text-sm font-semibold text-slate-700">Số tiền nạp</span>
            <input
              v-model.number="selectedAmount"
              type="number"
              min="1000"
              step="1000"
              class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-[#2463eb]"
            >
          </label>

          <button
            type="button"
            class="mt-5 inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-[#2463eb] px-5 py-3.5 text-sm font-bold text-white transition hover:bg-blue-700 disabled:opacity-70"
            :disabled="creatingTopUp"
            @click="createTopUp"
          >
            <span class="material-symbols-outlined">{{ creatingTopUp ? 'hourglass_top' : 'qr_code_2' }}</span>
            <span>{{ creatingTopUp ? 'Đang tạo giao dịch...' : `Tạo giao dịch ${getGatewayLabel(selectedGateway)}` }}</span>
          </button>

          <div v-if="paymentDraft" class="mt-5 rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-900">
            <p class="font-bold">Giao dịch gần nhất</p>
            <p class="mt-2">Mã: <span class="font-semibold">{{ paymentDraft.ma_giao_dich_noi_bo }}</span></p>
            <p class="mt-1">Số tiền: <span class="font-semibold">{{ formatCurrency(paymentDraft.so_tien) }}</span></p>
            <p class="mt-1">Cổng thanh toán: <span class="font-semibold">{{ getGatewayLabel(paymentDraft.gateway) }}</span></p>
          </div>
        </section>

        <section class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
          <h2 class="text-2xl font-bold text-slate-900">Bảng giá nhanh</h2>

          <div v-if="featuredPricing.length" class="mt-5">
            <p class="text-xs font-black uppercase tracking-[0.18em] text-slate-500">Featured Listing</p>
            <div class="mt-3 space-y-3">
              <article
                v-for="item in featuredPricing"
                :key="item.id"
                class="rounded-2xl border border-slate-200 bg-slate-50 p-4"
              >
                <div class="flex items-start justify-between gap-4">
                  <div>
                    <p class="text-sm font-bold text-slate-900">{{ item.ten_hien_thi }}</p>
                    <p class="mt-1 text-xs text-slate-500">{{ getFeatureDescription(item.feature_code) }}</p>
                  </div>
                  <span class="rounded-2xl bg-blue-500/10 px-3 py-2 text-sm font-black text-[#2463eb]">
                    {{ formatCurrency(item.don_gia) }}
                  </span>
                </div>
              </article>
            </div>
          </div>

          <div v-if="aiPricing.length" class="mt-6">
            <p class="text-xs font-black uppercase tracking-[0.18em] text-slate-500">AI Pay-Per-Use</p>
            <div class="mt-3 space-y-3">
              <article
                v-for="item in aiPricing"
                :key="item.id"
                class="rounded-2xl border border-slate-200 bg-slate-50 p-4"
              >
                <div class="flex items-start justify-between gap-4">
                  <div>
                    <p class="text-sm font-bold text-slate-900">{{ item.ten_hien_thi }}</p>
                    <p class="mt-1 text-xs text-slate-500">{{ getFeatureDescription(item.feature_code) }}</p>
                  </div>
                  <span class="rounded-2xl bg-slate-900/5 px-3 py-2 text-sm font-black text-slate-900">
                    {{ formatCurrency(item.don_gia) }}
                  </span>
                </div>
              </article>
            </div>
          </div>
        </section>
      </aside>

      <section class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
        <div class="flex flex-col gap-4 border-b border-slate-200 pb-5 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 class="text-2xl font-bold text-slate-900">Lịch sử biến động ví</h2>
            <p class="mt-2 text-sm text-slate-600">
              {{ pagination.total }} giao dịch · từ {{ pagination.from || 0 }} đến {{ pagination.to || 0 }}
            </p>
          </div>

          <button
            type="button"
            class="inline-flex items-center gap-2 rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:opacity-60"
            :disabled="refreshing"
            @click="loadBillingData(pagination.current_page, false)"
          >
            <span class="material-symbols-outlined">{{ refreshing ? 'progress_activity' : 'refresh' }}</span>
            Làm mới
          </button>
        </div>

        <div v-if="loading" class="mt-5 space-y-3">
          <div v-for="index in 6" :key="index" class="h-24 animate-pulse rounded-2xl bg-slate-100"></div>
        </div>

        <div v-else-if="!transactions.length" class="mt-5 rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-6 py-12 text-center text-sm leading-7 text-slate-600">
          Chưa có biến động ví nào. Hãy nạp tiền hoặc dùng featured / AI để lịch sử bắt đầu xuất hiện.
        </div>

        <div v-else class="mt-5 space-y-3">
          <article
            v-for="transaction in transactions"
            :key="transaction.id"
            class="rounded-2xl border border-slate-200 bg-slate-50 p-4"
          >
            <div class="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
              <div class="min-w-0">
                <div class="flex flex-wrap items-center gap-2">
                  <p class="text-base font-bold text-slate-900">{{ getTransactionLabel(transaction) }}</p>
                  <span class="rounded-full border px-2.5 py-1 text-[11px] font-bold uppercase tracking-wide" :class="getTransactionTone(transaction)">
                    {{ transaction.loai_bien_dong }}
                  </span>
                </div>
                <p class="mt-2 text-sm text-slate-600">{{ getTransactionDescription(transaction) }}</p>
                <p class="mt-2 text-xs uppercase tracking-[0.25em] text-slate-500">
                  {{ formatDateTime(transaction.created_at) }}
                </p>
              </div>

              <div class="grid min-w-[220px] gap-2 text-sm">
                <div class="flex items-center justify-between rounded-xl bg-white px-3 py-2">
                  <span class="text-slate-500">Số tiền</span>
                  <span class="font-bold text-slate-900">{{ formatCurrency(transaction.so_tien) }}</span>
                </div>
                <div class="flex items-center justify-between rounded-xl bg-white px-3 py-2">
                  <span class="text-slate-500">Số dư sau</span>
                  <span class="font-bold text-slate-900">{{ formatCurrency(transaction.so_du_sau) }}</span>
                </div>
                <div class="flex items-center justify-between rounded-xl bg-white px-3 py-2">
                  <span class="text-slate-500">Tạm giữ sau</span>
                  <span class="font-bold text-slate-900">{{ formatCurrency(transaction.tam_giu_sau) }}</span>
                </div>
              </div>
            </div>
          </article>
        </div>

        <div v-if="pagination.last_page > 1" class="mt-6 flex flex-wrap items-center justify-center gap-2">
          <button
            type="button"
            class="rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:opacity-50"
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
              ? 'border-[#2463eb] bg-[#2463eb] text-white'
              : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'"
            @click="changePage(page)"
          >
            {{ page }}
          </button>

          <button
            type="button"
            class="rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:opacity-50"
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
