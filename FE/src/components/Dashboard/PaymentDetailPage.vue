<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/20 p-4 md:p-8">

    <!-- ── Loading skeleton ─────────────────────────────────────── -->
    <template v-if="loading">
      <div class="mx-auto max-w-3xl animate-pulse space-y-6">
        <div class="h-10 w-48 rounded-2xl bg-slate-200"></div>
        <div class="h-56 rounded-3xl bg-slate-200"></div>
        <div class="h-72 rounded-3xl bg-slate-200"></div>
      </div>
    </template>

    <!-- ── Error state ────────────────────────────────────────────── -->
    <template v-else-if="error">
      <div class="mx-auto flex max-w-md flex-col items-center gap-6 py-20 text-center">
        <div class="flex size-20 items-center justify-center rounded-full bg-rose-100">
          <span class="material-symbols-outlined text-4xl text-rose-500">error_outline</span>
        </div>
        <div>
          <h2 class="text-xl font-bold text-slate-900">Không tìm thấy giao dịch</h2>
          <p class="mt-2 text-sm text-slate-500">{{ error }}</p>
        </div>
        <button
          @click="$router.push('/payments')"
          class="flex items-center gap-2 rounded-2xl bg-[#2463eb] px-6 py-3 text-sm font-bold text-white shadow-lg shadow-blue-200 transition hover:bg-blue-700 hover:-translate-y-0.5"
        >
          <span class="material-symbols-outlined text-[18px]">arrow_back</span>
          Quay lại lịch sử
        </button>
      </div>
    </template>

    <!-- ── Main content ───────────────────────────────────────────── -->
    <template v-else-if="payment">
      <div class="mx-auto max-w-3xl space-y-6">

        <!-- Back button -->
        <button
          @click="$router.push('/payments')"
          class="flex items-center gap-2 text-sm font-semibold text-slate-500 transition hover:text-[#2463eb]"
        >
          <span class="material-symbols-outlined text-[18px]">arrow_back</span>
          Lịch sử thanh toán
        </button>

        <!-- ── Hero card ──────────────────────────────────────────── -->
        <div
          class="relative overflow-hidden rounded-3xl p-8 text-white shadow-xl"
          :class="heroGradient"
        >
          <!-- Decorative circles -->
          <div class="pointer-events-none absolute -right-12 -top-12 size-48 rounded-full bg-white/10"></div>
          <div class="pointer-events-none absolute -bottom-8 -left-8 size-32 rounded-full bg-white/10"></div>

          <div class="relative">
            <!-- Icon + status badge -->
            <div class="flex items-start justify-between">
              <div class="flex size-14 items-center justify-center rounded-2xl bg-white/20 backdrop-blur">
                <span class="material-symbols-outlined text-3xl">{{ heroIcon }}</span>
              </div>
              <span
                class="flex items-center gap-1.5 rounded-full px-4 py-1.5 text-xs font-bold uppercase tracking-wider backdrop-blur"
                :class="statusBadge"
              >
                <span class="size-1.5 rounded-full bg-current"></span>
                {{ statusLabel }}
              </span>
            </div>

            <!-- Amount -->
            <div class="mt-6">
              <p class="text-sm font-medium text-white/70">Số tiền</p>
              <p class="mt-1 text-4xl font-black tracking-tight">
                {{ formatCurrency(payment.so_tien) }}
              </p>
            </div>

            <!-- Title + desc -->
            <div class="mt-4">
              <h1 class="text-xl font-bold">{{ heroTitle }}</h1>
              <p class="mt-1 text-sm text-white/80">{{ heroDescription }}</p>
            </div>
          </div>
        </div>

        <!-- ── Actions sidebar ────────────────────────────────────── -->
        <div v-if="canContinuePayment || true" class="flex flex-wrap gap-3">
          <!-- Continue payment (only when pending + has URL + not expired) -->
          <button
            v-if="canContinuePayment"
            @click="continuePayment"
            class="flex flex-1 items-center justify-center gap-2 rounded-2xl bg-[#2463eb] px-6 py-3 text-sm font-bold text-white shadow-lg shadow-blue-200 transition hover:bg-blue-700 hover:-translate-y-0.5"
          >
            <span class="material-symbols-outlined text-[18px]">open_in_new</span>
            Tiếp tục thanh toán
          </button>

          <!-- Go to destination based on transaction type -->
          <router-link
            :to="payment.loai_giao_dich === 'buy_subscription' ? '/plans' : '/wallet'"
            class="flex flex-1 items-center justify-center gap-2 rounded-2xl border border-slate-200 bg-white px-6 py-3 text-sm font-bold text-slate-700 shadow-sm transition hover:border-[#2463eb] hover:text-[#2463eb] hover:-translate-y-0.5"
          >
            <span class="material-symbols-outlined text-[18px]">
              {{ payment.loai_giao_dich === 'buy_subscription' ? 'workspace_premium' : 'account_balance_wallet' }}
            </span>
            {{ payment.loai_giao_dich === 'buy_subscription' ? 'Đi tới Gói Pro' : 'Đi tới Ví AI' }}
          </router-link>
        </div>

        <!-- ── Detail cards ────────────────────────────────────────── -->
        <div class="rounded-3xl border border-slate-200 bg-white shadow-sm">
          <div class="border-b border-slate-100 px-6 py-4">
            <h2 class="font-bold text-slate-900">Thông tin giao dịch</h2>
          </div>
          <div class="divide-y divide-slate-50">
            <DetailRow label="Mã giao dịch nội bộ" icon="tag">
              <code class="rounded-lg bg-slate-100 px-2 py-1 text-xs font-bold text-slate-800">
                {{ payment.ma_giao_dich_noi_bo }}
              </code>
            </DetailRow>

            <DetailRow label="Loại giao dịch" icon="swap_horiz">
              <span class="inline-flex items-center gap-1.5 rounded-full bg-blue-50 px-3 py-1 text-xs font-bold text-blue-700">
                <span class="material-symbols-outlined text-[14px]">
                  {{ payment.loai_giao_dich === 'buy_subscription' ? 'workspace_premium' : 'account_balance_wallet' }}
                </span>
                {{ paymentTypeLabel }}
              </span>
            </DetailRow>

            <DetailRow label="Phương thức thanh toán" icon="payments">
              <div class="flex items-center gap-2">
                <span class="font-semibold uppercase text-slate-700">{{ payment.gateway }}</span>
              </div>
            </DetailRow>

            <DetailRow v-if="payment.ma_giao_dich_gateway" label="Mã giao dịch gateway" icon="receipt_long">
              <code class="rounded-lg bg-slate-100 px-2 py-1 text-xs font-bold text-slate-800">
                {{ payment.ma_giao_dich_gateway }}
              </code>
            </DetailRow>

            <DetailRow label="Tạo lúc" icon="schedule">
              <span class="text-slate-700">{{ formatDatetime(payment.created_at) }}</span>
            </DetailRow>

            <DetailRow v-if="payment.paid_at" label="Thanh toán lúc" icon="check_circle">
              <span class="text-emerald-700 font-semibold">{{ formatDatetime(payment.paid_at) }}</span>
            </DetailRow>

            <DetailRow v-if="payment.payment_link_expires_at && payment.trang_thai === 'pending'" label="Link hết hạn lúc" icon="timer">
              <span :class="payment.is_payment_link_expired ? 'text-rose-600 font-bold' : 'text-amber-700 font-semibold'">
                {{ formatDatetime(payment.payment_link_expires_at) }}
                <span v-if="payment.is_payment_link_expired" class="ml-2 text-xs font-bold text-rose-500">(Đã hết hạn)</span>
              </span>
            </DetailRow>

            <DetailRow v-if="payment.noi_dung" label="Nội dung" icon="description">
              <span class="text-slate-700">{{ payment.noi_dung }}</span>
            </DetailRow>
          </div>
        </div>

        <!-- ── Gói dịch vụ ──────────────────────────────────────────── -->
        <div v-if="payment.goi_dich_vu" class="rounded-3xl border border-slate-200 bg-white shadow-sm">
          <div class="border-b border-slate-100 px-6 py-4">
            <h2 class="font-bold text-slate-900">Gói dịch vụ</h2>
          </div>
          <div class="divide-y divide-slate-50">
            <DetailRow label="Tên gói" icon="workspace_premium">
              <span class="font-bold text-indigo-700">{{ payment.goi_dich_vu.ten_goi }}</span>
            </DetailRow>
            <DetailRow label="Mã gói" icon="label">
              <code class="rounded-lg bg-slate-100 px-2 py-1 text-xs font-bold text-slate-800">
                {{ payment.goi_dich_vu.ma_goi }}
              </code>
            </DetailRow>
          </div>
        </div>

        <!-- ── Ví người dùng ──────────────────────────────────────── -->
        <div v-if="payment.vi_nguoi_dung" class="rounded-3xl border border-slate-200 bg-white shadow-sm">
          <div class="border-b border-slate-100 px-6 py-4">
            <h2 class="font-bold text-slate-900">Thông tin ví</h2>
          </div>
          <div class="divide-y divide-slate-50">
            <DetailRow label="Số dư hiện tại" icon="account_balance_wallet">
              <span class="text-lg font-black text-emerald-700">
                {{ formatCurrency(payment.vi_nguoi_dung.so_du_hien_tai) }}
              </span>
            </DetailRow>
            <DetailRow label="Số dư tạm giữ" icon="lock">
              <span class="font-bold text-amber-700">
                {{ formatCurrency(payment.vi_nguoi_dung.so_du_tam_giu) }}
              </span>
            </DetailRow>
          </div>
        </div>

      </div>
    </template>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, defineComponent, h } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { paymentService } from '@/services/api.js'

// ── Internal sub-component ────────────────────────────────────────────────────
const DetailRow = defineComponent({
  props: { label: String, icon: String },
  setup(props, { slots }) {
    return () =>
      h('div', { class: 'flex items-start gap-4 px-6 py-4' }, [
        h('div', { class: 'flex size-8 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-500' }, [
          h('span', { class: 'material-symbols-outlined text-[18px]' }, props.icon)
        ]),
        h('div', { class: 'flex-1 min-w-0' }, [
          h('p', { class: 'text-xs font-semibold uppercase tracking-wider text-slate-400' }, props.label),
          h('div', { class: 'mt-1' }, slots.default?.())
        ])
      ])
  }
})

// ── Composables ───────────────────────────────────────────────────────────────
const route  = useRoute()
const router = useRouter()

// ── State ─────────────────────────────────────────────────────────────────────
const payment = ref(null)
const loading = ref(true)
const error   = ref(null)

// ── Params ────────────────────────────────────────────────────────────────────
const paymentCode = computed(() => String(route.params.maGiaoDichNoiBo || ''))

// ── Data fetch ────────────────────────────────────────────────────────────────
const loadPaymentDetail = async () => {
  loading.value = true
  error.value   = null
  try {
    const response = await paymentService.getPaymentDetail(paymentCode.value)
    payment.value = response?.data || null
    if (!payment.value) error.value = 'Không tìm thấy giao dịch.'
  } catch (err) {
    error.value = err?.message || 'Đã xảy ra lỗi khi tải dữ liệu.'
  } finally {
    loading.value = false
  }
}

onMounted(loadPaymentDetail)

// ── Computed labels ───────────────────────────────────────────────────────────
const paymentTypeLabel = computed(() => {
  if (!payment.value) return ''
  const map = {
    topup_wallet:     'Nạp ví AI',
    buy_subscription: 'Mua gói Pro',
  }
  return map[payment.value.loai_giao_dich] || 'Thanh toán'
})

const statusLabel = computed(() => {
  if (!payment.value) return ''
  const map = {
    pending:    'Đang chờ xác nhận',
    thanh_cong: 'Thành công',
    that_bai:   'Thất bại',
    huy:        'Đã hủy',
  }
  return map[payment.value.trang_thai] || payment.value.trang_thai
})

const statusBadge = computed(() => {
  if (!payment.value) return ''
  const map = {
    pending:    'bg-amber-500/20 text-amber-100',
    thanh_cong: 'bg-emerald-500/20 text-emerald-100',
    that_bai:   'bg-rose-500/20 text-rose-100',
    huy:        'bg-slate-500/20 text-slate-100',
  }
  return map[payment.value.trang_thai] || 'bg-slate-500/20 text-slate-100'
})

const heroGradient = computed(() => {
  if (!payment.value) return 'bg-slate-700'
  const map = {
    pending:    'bg-gradient-to-br from-amber-500 to-orange-600',
    thanh_cong: 'bg-gradient-to-br from-emerald-500 to-teal-600',
    that_bai:   'bg-gradient-to-br from-rose-500 to-red-700',
    huy:        'bg-gradient-to-br from-slate-500 to-slate-700',
  }
  return map[payment.value.trang_thai] || 'bg-gradient-to-br from-slate-500 to-slate-700'
})

const heroIcon = computed(() => {
  if (!payment.value) return 'receipt'
  const map = {
    pending:    'hourglass_top',
    thanh_cong: 'check_circle',
    that_bai:   'cancel',
    huy:        'block',
  }
  return map[payment.value.trang_thai] || 'receipt'
})

const heroTitle = computed(() => {
  if (!payment.value) return ''
  const map = {
    pending:    'Giao dịch đang chờ xử lý',
    thanh_cong: 'Thanh toán thành công 🎉',
    that_bai:   'Thanh toán thất bại',
    huy:        'Giao dịch đã bị hủy',
  }
  return map[payment.value.trang_thai] || 'Chi tiết giao dịch'
})

const heroDescription = computed(() => {
  if (!payment.value) return ''
  const typeMap = {
    topup_wallet:     'Nạp tiền vào ví AI để sử dụng các tính năng AI.',
    buy_subscription: 'Mua gói Pro để trải nghiệm đầy đủ tính năng cao cấp.',
  }
  return typeMap[payment.value.loai_giao_dich] || 'Giao dịch thanh toán trên SmartJob AI.'
})

const canContinuePayment = computed(() => {
  if (!payment.value) return false
  return (
    payment.value.trang_thai === 'pending' &&
    payment.value.redirect_url &&
    !payment.value.is_payment_link_expired
  )
})

// ── Actions ───────────────────────────────────────────────────────────────────
const continuePayment = () => {
  if (payment.value?.redirect_url) {
    window.location.href = payment.value.redirect_url
  }
}

// ── Helpers ───────────────────────────────────────────────────────────────────
const formatCurrency = (amount) => {
  if (amount == null) return '—'
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
    maximumFractionDigits: 0,
  }).format(amount)
}

const formatDatetime = (value) => {
  if (!value) return '—'
  return new Intl.DateTimeFormat('vi-VN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit',
    hour12: false,
  }).format(new Date(value))
}
</script>
