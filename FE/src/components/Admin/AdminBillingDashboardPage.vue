<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { adminBillingService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'

const notify = useNotify()

const loading = ref(false)
const managementLoading = ref(false)
const savingPlan = ref(false)
const savingPrice = ref(false)
const reconcilingPayment = ref('')
const showPlanModal = ref(false)
const showPriceModal = ref(false)
const overview = ref(null)
const payments = ref([])
const plans = ref([])
const prices = ref([])
const subscriptions = ref([])
const paymentPagination = reactive({ current_page: 1, last_page: 1, total: 0, per_page: 8 })
const subscriptionPagination = reactive({ current_page: 1, last_page: 1, total: 0, per_page: 8 })
const paymentFilters = reactive({ q: '', loai_giao_dich: '', trang_thai: '' })
const subscriptionFilters = reactive({ q: '', trang_thai: '' })
const planForm = reactive({
  id: null,
  ma_goi: '',
  ten_goi: '',
  mo_ta: '',
  gia: 0,
  chu_ky: 'monthly',
  trang_thai: 'active',
  is_free: false,
  features_text: '',
})
const priceForm = reactive({
  id: null,
  feature_code: '',
  ten_hien_thi: '',
  don_gia: 0,
  don_vi_tinh: 'request',
  trang_thai: 'active',
})

const formatCurrency = (value) => {
  const amount = Number(value || 0)
  if (!amount) return '0 đ'
  return `${new Intl.NumberFormat('vi-VN').format(amount)} đ`
}

const formatDateTime = (value) => {
  if (!value) return 'Chưa cập nhật'

  return new Intl.DateTimeFormat('vi-VN', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(new Date(value))
}

const formatStatusLabel = (status) => {
  if (status === 'success') return 'Thành công'
  if (status === 'pending') return 'Đang chờ'
  if (status === 'failed') return 'Thất bại'
  if (status === 'cancelled') return 'Đã hủy'
  return status || 'Không rõ'
}

const formatTypeLabel = (type) => {
  if (type === 'topup_wallet') return 'Nạp ví AI'
  if (type === 'buy_subscription') return 'Mua gói Pro'
  return 'Thanh toán'
}

const getGatewayLabel = (gateway) => {
  if (gateway === 'momo') return 'MoMo'
  if (gateway === 'vnpay') return 'VNPay'
  if (gateway === 'wallet') return 'Ví AI'
  return String(gateway || 'Không rõ').toUpperCase()
}

const statusTone = (status) => {
  if (status === 'success') return 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-300'
  if (status === 'pending') return 'bg-amber-500/10 text-amber-700 dark:text-amber-300'
  if (status === 'failed') return 'bg-rose-500/10 text-rose-700 dark:text-rose-300'
  return 'bg-slate-200 text-slate-700 dark:bg-slate-800 dark:text-slate-300'
}

const canReconcilePayment = (payment) =>
  ['momo', 'vnpay'].includes(String(payment?.gateway || '')) && payment?.trang_thai === 'pending'

const getReconcileLabel = (payment) => `Đối soát ${getGatewayLabel(payment?.gateway)}`

const totals = computed(() => overview.value?.totals || {})

const parsePlanFeatures = () =>
  String(planForm.features_text || '')
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      const [featureCode, quota = '0', resetCycle = planForm.chu_ky, unlimited = '0'] = line.split('|').map((item) => item.trim())
      return {
        feature_code: featureCode,
        quota: Number(quota || 0),
        reset_cycle: resetCycle || null,
        is_unlimited: ['1', 'true', 'yes', 'unlimited'].includes(String(unlimited).toLowerCase()),
      }
    })

const formatPlanFeatures = (features = []) =>
  features
    .map((feature) => [
      feature.feature_code,
      feature.is_unlimited ? '' : Number(feature.quota || 0),
      feature.reset_cycle || '',
      feature.is_unlimited ? '1' : '0',
    ].join('|'))
    .join('\n')

const statusCards = computed(() => [
  {
    label: 'Doanh thu đã xử lý',
    value: formatCurrency(totals.value.processed_amount),
    helper: `${totals.value.pending_count || 0} giao dịch đang chờ`,
    tone: 'bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-300',
    icon: 'payments',
  },
  {
    label: 'Nạp ví AI',
    value: formatCurrency(totals.value.topup_amount),
    helper: `${totals.value.topup_count || 0} giao dịch thành công`,
    tone: 'bg-emerald-50 text-emerald-600 dark:bg-emerald-900/20 dark:text-emerald-300',
    icon: 'account_balance_wallet',
  },
  {
    label: 'Doanh thu gói Pro',
    value: formatCurrency(totals.value.subscription_revenue),
    helper: `${totals.value.subscription_count || 0} lượt kích hoạt`,
    tone: 'bg-violet-50 text-violet-600 dark:bg-violet-900/20 dark:text-violet-300',
    icon: 'workspace_premium',
  },
  {
    label: 'Subscription đang hoạt động',
    value: totals.value.active_subscription_count || 0,
    helper: `Ví AI toàn hệ thống ${formatCurrency(totals.value.wallet_balance_amount)}`,
    tone: 'bg-amber-50 text-amber-600 dark:bg-amber-900/20 dark:text-amber-300',
    icon: 'rocket_launch',
  },
])

const loadOverview = async () => {
  loading.value = true
  try {
    const response = await adminBillingService.getOverview()
    overview.value = response?.data || null
  } catch (error) {
    notify.apiError(error, 'Không tải được dashboard billing.')
  } finally {
    loading.value = false
  }
}

const normalizePayments = (response) => {
  const payload = response?.data || {}
  payments.value = payload.data || []
  paymentPagination.current_page = payload.current_page || 1
  paymentPagination.last_page = payload.last_page || 1
  paymentPagination.total = payload.total || 0
}

const normalizeSubscriptions = (response) => {
  const payload = response?.data || {}
  subscriptions.value = payload.data || []
  subscriptionPagination.current_page = payload.current_page || 1
  subscriptionPagination.last_page = payload.last_page || 1
  subscriptionPagination.total = payload.total || 0
}

const loadPayments = async (page = paymentPagination.current_page) => {
  const response = await adminBillingService.getPayments({
    ...paymentFilters,
    page,
    per_page: paymentPagination.per_page,
  })
  normalizePayments(response)
}

const loadSubscriptions = async (page = subscriptionPagination.current_page) => {
  const response = await adminBillingService.getSubscriptions({
    ...subscriptionFilters,
    page,
    per_page: subscriptionPagination.per_page,
  })
  normalizeSubscriptions(response)
}

const loadManagementData = async () => {
  managementLoading.value = true
  try {
    const [paymentsResponse, plansResponse, pricesResponse, subscriptionsResponse] = await Promise.all([
      adminBillingService.getPayments({ page: 1, per_page: paymentPagination.per_page }),
      adminBillingService.getPlans(),
      adminBillingService.getPrices(),
      adminBillingService.getSubscriptions({ page: 1, per_page: subscriptionPagination.per_page }),
    ])

    normalizePayments(paymentsResponse)
    plans.value = plansResponse?.data || []
    prices.value = pricesResponse?.data || []
    normalizeSubscriptions(subscriptionsResponse)
  } catch (error) {
    notify.apiError(error, 'Không tải được dữ liệu quản trị billing.')
  } finally {
    managementLoading.value = false
  }
}

const resetPlanForm = () => {
  Object.assign(planForm, {
    id: null,
    ma_goi: '',
    ten_goi: '',
    mo_ta: '',
    gia: 0,
    chu_ky: 'monthly',
    trang_thai: 'active',
    is_free: false,
    features_text: '',
  })
}

const editPlan = (plan) => {
  Object.assign(planForm, {
    id: plan.id,
    ma_goi: plan.ma_goi || '',
    ten_goi: plan.ten_goi || '',
    mo_ta: plan.mo_ta || '',
    gia: Number(plan.gia || 0),
    chu_ky: plan.chu_ky || 'monthly',
    trang_thai: plan.trang_thai || 'active',
    is_free: Boolean(plan.is_free),
    features_text: formatPlanFeatures(plan.tinh_nangs || []),
  })
  showPlanModal.value = true
}

const openCreatePlanModal = () => {
  resetPlanForm()
  showPlanModal.value = true
}

const closePlanModal = () => {
  if (savingPlan.value) return
  showPlanModal.value = false
}

const savePlan = async () => {
  if (!planForm.ma_goi || !planForm.ten_goi) {
    notify.warning('Vui lòng nhập mã gói và tên gói.')
    return
  }

  savingPlan.value = true
  try {
    const payload = {
      ma_goi: planForm.ma_goi,
      ten_goi: planForm.ten_goi,
      mo_ta: planForm.mo_ta || null,
      gia: Number(planForm.gia || 0),
      chu_ky: planForm.chu_ky,
      trang_thai: planForm.trang_thai,
      is_free: Boolean(planForm.is_free),
      features: parsePlanFeatures(),
    }

    if (planForm.id) {
      await adminBillingService.updatePlan(planForm.id, payload)
      notify.success('Đã cập nhật gói dịch vụ.')
    } else {
      await adminBillingService.createPlan(payload)
      notify.success('Đã tạo gói dịch vụ.')
    }

    resetPlanForm()
    showPlanModal.value = false
    const response = await adminBillingService.getPlans()
    plans.value = response?.data || []
    await loadOverview()
  } catch (error) {
    notify.apiError(error, 'Không lưu được gói dịch vụ.')
  } finally {
    savingPlan.value = false
  }
}

const resetPriceForm = () => {
  Object.assign(priceForm, {
    id: null,
    feature_code: '',
    ten_hien_thi: '',
    don_gia: 0,
    don_vi_tinh: 'request',
    trang_thai: 'active',
  })
}

const editPrice = (price) => {
  Object.assign(priceForm, {
    id: price.id,
    feature_code: price.feature_code || '',
    ten_hien_thi: price.ten_hien_thi || '',
    don_gia: Number(price.don_gia || 0),
    don_vi_tinh: price.don_vi_tinh || 'request',
    trang_thai: price.trang_thai || 'active',
  })
  showPriceModal.value = true
}

const openCreatePriceModal = () => {
  resetPriceForm()
  showPriceModal.value = true
}

const closePriceModal = () => {
  if (savingPrice.value) return
  showPriceModal.value = false
}

const savePrice = async () => {
  if (!priceForm.feature_code || !priceForm.ten_hien_thi) {
    notify.warning('Vui lòng nhập mã tính năng và tên hiển thị.')
    return
  }

  savingPrice.value = true
  try {
    const payload = {
      feature_code: priceForm.feature_code,
      ten_hien_thi: priceForm.ten_hien_thi,
      don_gia: Number(priceForm.don_gia || 0),
      don_vi_tinh: priceForm.don_vi_tinh,
      trang_thai: priceForm.trang_thai,
    }

    if (priceForm.id) {
      await adminBillingService.updatePrice(priceForm.id, payload)
      notify.success('Đã cập nhật bảng giá AI.')
    } else {
      await adminBillingService.createPrice(payload)
      notify.success('Đã tạo bảng giá AI.')
    }

    resetPriceForm()
    showPriceModal.value = false
    const response = await adminBillingService.getPrices()
    prices.value = response?.data || []
  } catch (error) {
    notify.apiError(error, 'Không lưu được bảng giá AI.')
  } finally {
    savingPrice.value = false
  }
}

const reconcilePayment = async (payment) => {
  if (!payment?.ma_giao_dich_noi_bo) return

  reconcilingPayment.value = payment.ma_giao_dich_noi_bo
  try {
    await adminBillingService.reconcilePayment(payment.ma_giao_dich_noi_bo)
    notify.success(`Đã đối soát giao dịch với ${getGatewayLabel(payment.gateway)}.`)
    await Promise.all([loadOverview(), loadPayments(paymentPagination.current_page), loadSubscriptions(subscriptionPagination.current_page)])
  } catch (error) {
    notify.apiError(error, `Không đối soát được giao dịch ${getGatewayLabel(payment.gateway)}.`)
  } finally {
    reconcilingPayment.value = ''
  }
}

watch(
  () => [paymentFilters.q, paymentFilters.loai_giao_dich, paymentFilters.trang_thai],
  async () => {
    try {
      await loadPayments(1)
    } catch (error) {
      notify.apiError(error, 'Không lọc được giao dịch.')
    }
  },
)

watch(
  () => [subscriptionFilters.q, subscriptionFilters.trang_thai],
  async () => {
    try {
      await loadSubscriptions(1)
    } catch (error) {
      notify.apiError(error, 'Không lọc được subscription.')
    }
  },
)

onMounted(async () => {
  await Promise.all([loadOverview(), loadManagementData()])
})
</script>

<template>
  <div class="space-y-6">
    <section class="flex flex-col gap-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <h2 class="text-3xl font-extrabold tracking-tight">Billing Dashboard</h2>
        <p class="mt-1 text-slate-500 dark:text-slate-400">
          Theo dõi doanh thu, top-up ví AI, hiệu suất gói Pro và diễn biến giao dịch thanh toán trên toàn hệ thống.
        </p>
      </div>
      <div class="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-medium text-slate-500 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-300">
        <span class="material-symbols-outlined text-[#2463eb]">monitoring</span>
        Ví đang giữ {{ formatCurrency(totals.wallet_hold_amount) }}
      </div>
    </section>

    <div class="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-4">
      <article
        v-for="card in statusCards"
        :key="card.label"
        class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900"
      >
        <div class="mb-4 flex items-start justify-between gap-3">
          <div class="flex size-11 items-center justify-center rounded-xl" :class="card.tone">
            <span class="material-symbols-outlined">{{ card.icon }}</span>
          </div>
          <span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-bold text-slate-500 dark:bg-slate-800 dark:text-slate-300">
            Billing
          </span>
        </div>
        <p class="text-sm font-medium text-slate-500 dark:text-slate-400">{{ card.label }}</p>
        <h3 class="mt-2 text-2xl font-bold">
          {{ loading ? '...' : card.value }}
        </h3>
        <p class="mt-2 text-sm font-medium text-slate-600 dark:text-slate-300">{{ card.helper }}</p>
      </article>
    </div>

    <section class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="mb-5 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <h4 class="text-lg font-bold">Quản lý giao dịch</h4>
          <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Lọc giao dịch toàn hệ thống và đối soát lại các giao dịch gateway đang chờ.
          </p>
        </div>
        <div class="flex flex-col gap-2 sm:flex-row">
          <input v-model.trim="paymentFilters.q" class="rounded-xl border border-slate-200 px-4 py-2 text-sm outline-none focus:border-blue-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white" placeholder="Mã GD / email / tên">
          <select v-model="paymentFilters.loai_giao_dich" class="rounded-xl border border-slate-200 px-4 py-2 text-sm outline-none dark:border-slate-700 dark:bg-slate-950 dark:text-white">
            <option value="">Tất cả loại</option>
            <option value="topup_wallet">Nạp ví</option>
            <option value="buy_subscription">Mua gói</option>
          </select>
          <select v-model="paymentFilters.trang_thai" class="rounded-xl border border-slate-200 px-4 py-2 text-sm outline-none dark:border-slate-700 dark:bg-slate-950 dark:text-white">
            <option value="">Tất cả trạng thái</option>
            <option value="pending">Đang chờ</option>
            <option value="success">Thành công</option>
            <option value="failed">Thất bại</option>
            <option value="cancelled">Đã hủy</option>
          </select>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="min-w-full text-left text-sm">
          <thead class="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-400 dark:border-slate-800">
            <tr>
              <th class="py-3 pr-4">Giao dịch</th>
              <th class="py-3 pr-4">Người dùng</th>
              <th class="py-3 pr-4">Loại</th>
              <th class="py-3 pr-4">Số tiền</th>
              <th class="py-3 pr-4">Trạng thái</th>
              <th class="py-3 pr-4">Thao tác</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="payment in payments" :key="payment.id" class="border-b border-slate-100 dark:border-slate-800">
              <td class="py-3 pr-4">
                <p class="font-bold text-slate-900 dark:text-white">{{ payment.ma_giao_dich_noi_bo }}</p>
                <p class="mt-1 text-xs text-slate-500">{{ payment.ma_giao_dich_gateway || 'Chưa có mã gateway' }}</p>
              </td>
              <td class="py-3 pr-4">
                <p class="font-semibold text-slate-800 dark:text-slate-100">{{ payment.nguoi_dung?.ho_ten || 'Người dùng' }}</p>
                <p class="text-xs text-slate-500">{{ payment.nguoi_dung?.email }}</p>
              </td>
              <td class="py-3 pr-4">{{ formatTypeLabel(payment.loai_giao_dich) }}</td>
              <td class="py-3 pr-4 font-bold">{{ formatCurrency(payment.so_tien) }}</td>
              <td class="py-3 pr-4">
                <span class="rounded-full px-2.5 py-1 text-xs font-bold" :class="statusTone(payment.trang_thai)">
                  {{ formatStatusLabel(payment.trang_thai) }}
                </span>
              </td>
              <td class="py-3 pr-4">
                <button
                  class="rounded-xl border border-blue-200 px-3 py-2 text-xs font-bold text-blue-700 transition hover:bg-blue-50 disabled:opacity-60 dark:border-blue-500/20 dark:text-blue-300 dark:hover:bg-blue-500/10"
                  type="button"
                  :disabled="!canReconcilePayment(payment) || reconcilingPayment === payment.ma_giao_dich_noi_bo"
                  @click="reconcilePayment(payment)"
                >
                  {{ reconcilingPayment === payment.ma_giao_dich_noi_bo ? 'Đang đối soát...' : getReconcileLabel(payment) }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-if="!payments.length && !managementLoading" class="py-8 text-center text-sm text-slate-500">Chưa có giao dịch phù hợp.</p>
      </div>
    </section>

    <div class="grid gap-6 xl:grid-cols-2">
      <section class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div class="mb-5 flex items-start justify-between gap-4">
          <div>
            <h4 class="text-lg font-bold">Quản lý gói dịch vụ</h4>
            <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
              Tạo, cập nhật và xem nhanh quyền lợi của từng gói.
            </p>
          </div>
          <button class="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-bold text-white transition hover:bg-blue-700" type="button" @click="openCreatePlanModal">
            <span class="material-symbols-outlined text-base">add</span>
            Tạo gói
          </button>
        </div>

        <div class="space-y-3">
          <article v-for="plan in plans" :key="plan.id" class="rounded-xl border border-slate-200 p-4 dark:border-slate-700">
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0">
                <p class="font-bold text-slate-900 dark:text-white">{{ plan.ten_goi }} <span class="text-xs text-slate-400">({{ plan.ma_goi }})</span></p>
                <p class="mt-1 text-sm text-slate-500">{{ formatCurrency(plan.gia) }} · {{ plan.chu_ky }} · {{ plan.trang_thai }}</p>
              </div>
              <button class="inline-flex items-center gap-1 rounded-lg border border-slate-200 px-3 py-2 text-xs font-bold text-slate-600 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800" type="button" @click="editPlan(plan)">
                <span class="material-symbols-outlined text-sm">edit</span>
                Sửa
              </button>
            </div>
            <div class="mt-3 flex flex-wrap gap-2">
              <span v-for="feature in plan.tinh_nangs || []" :key="feature.id" class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-600 dark:bg-slate-800 dark:text-slate-300">
                {{ feature.feature_code }}: {{ feature.is_unlimited ? 'unlimited' : feature.quota }}
              </span>
            </div>
          </article>
          <p v-if="!plans.length && !managementLoading" class="py-8 text-center text-sm text-slate-500">Chưa có gói dịch vụ.</p>
        </div>
      </section>

      <section class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div class="mb-5 flex items-start justify-between gap-4">
          <div>
            <h4 class="text-lg font-bold">Bảng giá tính năng AI</h4>
            <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Cấu hình đơn giá ví cho từng tính năng.</p>
          </div>
          <button class="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-bold text-white transition hover:bg-blue-700" type="button" @click="openCreatePriceModal">
            <span class="material-symbols-outlined text-base">add</span>
            Tạo bảng giá
          </button>
        </div>

        <div class="space-y-3">
          <article v-for="price in prices" :key="price.id" class="flex items-start justify-between gap-3 rounded-xl border border-slate-200 p-4 dark:border-slate-700">
            <div class="min-w-0">
              <p class="font-bold text-slate-900 dark:text-white">{{ price.ten_hien_thi }}</p>
              <p class="mt-1 text-sm text-slate-500">{{ price.feature_code }} · {{ formatCurrency(price.don_gia) }}/{{ price.don_vi_tinh }} · {{ price.trang_thai }}</p>
            </div>
            <button class="inline-flex items-center gap-1 rounded-lg border border-slate-200 px-3 py-2 text-xs font-bold text-slate-600 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800" type="button" @click="editPrice(price)">
              <span class="material-symbols-outlined text-sm">edit</span>
              Sửa
            </button>
          </article>
          <p v-if="!prices.length && !managementLoading" class="py-8 text-center text-sm text-slate-500">Chưa có bảng giá tính năng AI.</p>
        </div>
      </section>
    </div>

    <section class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="mb-5 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <h4 class="text-lg font-bold">Subscription người dùng</h4>
          <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Theo dõi gói đang active, hết hạn hoặc đã hủy.</p>
        </div>
        <div class="flex flex-col gap-2 sm:flex-row">
          <input v-model.trim="subscriptionFilters.q" class="rounded-xl border border-slate-200 px-4 py-2 text-sm outline-none focus:border-blue-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white" placeholder="Email / tên / mã gói">
          <select v-model="subscriptionFilters.trang_thai" class="rounded-xl border border-slate-200 px-4 py-2 text-sm outline-none dark:border-slate-700 dark:bg-slate-950 dark:text-white">
            <option value="">Tất cả trạng thái</option>
            <option value="active">Active</option>
            <option value="expired">Expired</option>
            <option value="cancelled">Cancelled</option>
            <option value="pending">Pending</option>
          </select>
        </div>
      </div>

      <div class="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        <article v-for="subscription in subscriptions" :key="subscription.id" class="rounded-2xl border border-slate-200 p-4 dark:border-slate-700">
          <div class="flex items-start justify-between gap-3">
            <div>
              <p class="font-bold text-slate-900 dark:text-white">{{ subscription.nguoi_dung?.ho_ten || subscription.nguoi_dung?.email }}</p>
              <p class="mt-1 text-sm text-slate-500">{{ subscription.nguoi_dung?.email }}</p>
            </div>
            <span class="rounded-full bg-blue-500/10 px-2.5 py-1 text-xs font-bold text-blue-700 dark:text-blue-300">{{ subscription.trang_thai }}</span>
          </div>
          <p class="mt-3 text-sm font-semibold">{{ subscription.goi_dich_vu?.ten_goi || 'Không rõ gói' }}</p>
          <p class="mt-1 text-xs text-slate-500">
            {{ formatDateTime(subscription.ngay_bat_dau) }} -> {{ formatDateTime(subscription.ngay_het_han) }}
          </p>
        </article>
      </div>
      <p v-if="!subscriptions.length && !managementLoading" class="py-8 text-center text-sm text-slate-500">Chưa có subscription phù hợp.</p>
    </section>

    <div
      v-if="showPlanModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/55 p-4"
      role="dialog"
      aria-modal="true"
      @click.self="closePlanModal"
    >
      <section class="max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-xl bg-white p-6 shadow-2xl dark:bg-slate-900">
        <div class="mb-5 flex items-start justify-between gap-4">
          <div>
            <h4 class="text-lg font-bold">{{ planForm.id ? 'Cập nhật gói dịch vụ' : 'Tạo gói dịch vụ' }}</h4>
            <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Nhập thông tin gói và danh sách quyền lợi áp dụng cho người dùng.</p>
          </div>
          <button class="inline-flex size-9 items-center justify-center rounded-lg text-slate-500 transition hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800" type="button" @click="closePlanModal">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>

        <div class="grid gap-4 md:grid-cols-2">
          <label class="space-y-1.5">
            <span class="text-xs font-bold uppercase text-slate-500 dark:text-slate-400">Mã gói</span>
            <input v-model.trim="planForm.ma_goi" class="w-full rounded-lg border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white" placeholder="pro_monthly">
          </label>
          <label class="space-y-1.5">
            <span class="text-xs font-bold uppercase text-slate-500 dark:text-slate-400">Tên gói</span>
            <input v-model.trim="planForm.ten_goi" class="w-full rounded-lg border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white" placeholder="Gói Pro tháng">
          </label>
          <label class="space-y-1.5">
            <span class="text-xs font-bold uppercase text-slate-500 dark:text-slate-400">Giá</span>
            <input v-model.number="planForm.gia" type="number" min="0" class="w-full rounded-lg border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white" placeholder="99000">
          </label>
          <label class="space-y-1.5">
            <span class="text-xs font-bold uppercase text-slate-500 dark:text-slate-400">Chu kỳ</span>
            <select v-model="planForm.chu_ky" class="w-full rounded-lg border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white">
              <option value="free">Free</option>
              <option value="monthly">Monthly</option>
              <option value="yearly">Yearly</option>
            </select>
          </label>
          <label class="space-y-1.5">
            <span class="text-xs font-bold uppercase text-slate-500 dark:text-slate-400">Trạng thái</span>
            <select v-model="planForm.trang_thai" class="w-full rounded-lg border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white">
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </label>
          <label class="space-y-1.5">
            <span class="text-xs font-bold uppercase text-slate-500 dark:text-slate-400">Loại gói</span>
            <span class="flex min-h-[46px] items-center gap-2 rounded-lg border border-slate-200 px-4 py-3 text-sm font-semibold dark:border-slate-700">
              <input v-model="planForm.is_free" type="checkbox">
              Gói miễn phí
            </span>
          </label>
          <label class="space-y-1.5 md:col-span-2">
            <span class="text-xs font-bold uppercase text-slate-500 dark:text-slate-400">Mô tả gói</span>
            <textarea v-model="planForm.mo_ta" class="min-h-20 w-full rounded-lg border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white" placeholder="Mô tả ngắn về quyền lợi của gói" />
          </label>
          <label class="space-y-1.5 md:col-span-2">
            <span class="text-xs font-bold uppercase text-slate-500 dark:text-slate-400">Danh sách tính năng</span>
            <textarea v-model="planForm.features_text" class="min-h-32 w-full rounded-lg border border-slate-200 px-4 py-3 font-mono text-xs outline-none focus:border-blue-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white" placeholder="feature_code|quota|reset_cycle|is_unlimited" />
            <span class="block text-xs text-slate-500 dark:text-slate-400">Mỗi dòng theo dạng: feature_code|quota|reset_cycle|is_unlimited. Ví dụ: chatbot_message|200|monthly|0</span>
          </label>
        </div>

        <div class="mt-6 flex justify-end gap-3">
          <button class="rounded-lg border border-slate-200 px-4 py-2 text-sm font-bold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800" type="button" @click="closePlanModal">Hủy</button>
          <button class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-bold text-white transition hover:bg-blue-700 disabled:opacity-60" type="button" :disabled="savingPlan" @click="savePlan">
            {{ savingPlan ? 'Đang lưu...' : (planForm.id ? 'Cập nhật gói' : 'Tạo gói') }}
          </button>
        </div>
      </section>
    </div>

    <div
      v-if="showPriceModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/55 p-4"
      role="dialog"
      aria-modal="true"
      @click.self="closePriceModal"
    >
      <section class="w-full max-w-2xl rounded-xl bg-white p-6 shadow-2xl dark:bg-slate-900">
        <div class="mb-5 flex items-start justify-between gap-4">
          <div>
            <h4 class="text-lg font-bold">{{ priceForm.id ? 'Cập nhật bảng giá AI' : 'Tạo bảng giá AI' }}</h4>
            <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Thiết lập đơn giá dùng ví cho từng tính năng AI.</p>
          </div>
          <button class="inline-flex size-9 items-center justify-center rounded-lg text-slate-500 transition hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800" type="button" @click="closePriceModal">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>

        <div class="grid gap-4 md:grid-cols-2">
          <label class="space-y-1.5">
            <span class="text-xs font-bold uppercase text-slate-500 dark:text-slate-400">Mã tính năng</span>
            <input v-model.trim="priceForm.feature_code" class="w-full rounded-lg border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white" placeholder="employer_shortlist_ai_explanation">
          </label>
          <label class="space-y-1.5">
            <span class="text-xs font-bold uppercase text-slate-500 dark:text-slate-400">Tên hiển thị</span>
            <input v-model.trim="priceForm.ten_hien_thi" class="w-full rounded-lg border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white" placeholder="AI giải thích shortlist">
          </label>
          <label class="space-y-1.5">
            <span class="text-xs font-bold uppercase text-slate-500 dark:text-slate-400">Đơn giá</span>
            <input v-model.number="priceForm.don_gia" type="number" min="0" class="w-full rounded-lg border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white" placeholder="4000">
          </label>
          <label class="space-y-1.5">
            <span class="text-xs font-bold uppercase text-slate-500 dark:text-slate-400">Đơn vị tính</span>
            <input v-model.trim="priceForm.don_vi_tinh" class="w-full rounded-lg border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white" placeholder="request">
          </label>
          <label class="space-y-1.5 md:col-span-2">
            <span class="text-xs font-bold uppercase text-slate-500 dark:text-slate-400">Trạng thái</span>
            <select v-model="priceForm.trang_thai" class="w-full rounded-lg border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white">
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </label>
        </div>

        <div class="mt-6 flex justify-end gap-3">
          <button class="rounded-lg border border-slate-200 px-4 py-2 text-sm font-bold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800" type="button" @click="closePriceModal">Hủy</button>
          <button class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-bold text-white transition hover:bg-blue-700 disabled:opacity-60" type="button" :disabled="savingPrice" @click="savePrice">
            {{ savingPrice ? 'Đang lưu...' : (priceForm.id ? 'Cập nhật bảng giá' : 'Tạo bảng giá') }}
          </button>
        </div>
      </section>
    </div>
  </div>
</template>
