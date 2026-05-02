<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { paymentService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'

const notify = useNotify()

const loading = ref(false)
const refreshing = ref(false)
const payments = ref([])

const filters = reactive({
  loai_giao_dich: '',
  trang_thai: '',
})

const pagination = reactive({
  current_page: 1,
  last_page: 1,
  per_page: 10,
  total: 0,
  from: 0,
  to: 0,
})

const formatCurrency = (value) =>
  `${new Intl.NumberFormat('vi-VN').format(Number(value || 0))} đ`

const formatDateTime = (value) => {
  if (!value) return 'Chưa cập nhật'

  return new Intl.DateTimeFormat('vi-VN', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(new Date(value))
}

const getTypeLabel = (type) => {
  if (type === 'topup_wallet') return 'Nạp ví AI'
  if (type === 'buy_subscription') return 'Mua gói Pro'
  return 'Thanh toán'
}

const getStatusLabel = (status) => {
  if (status === 'success') return 'Thành công'
  if (status === 'pending') return 'Đang chờ'
  if (status === 'failed') return 'Thất bại'
  if (status === 'cancelled') return 'Đã hủy'
  return status || 'Không rõ'
}

const getStatusTone = (status) => {
  if (status === 'success') return 'border-emerald-200 bg-emerald-50 text-emerald-700'
  if (status === 'pending') return 'border-amber-200 bg-amber-50 text-amber-700'
  if (status === 'failed') return 'border-rose-200 bg-rose-50 text-rose-700'
  if (status === 'cancelled') return 'border-slate-200 bg-slate-100 text-slate-600'
  return 'border-slate-200 bg-slate-50 text-slate-600'
}

const getGatewayLabel = (gateway) => {
  if (gateway === 'momo') return 'MoMo'
  if (gateway === 'vnpay') return 'VNPay'
  if (gateway === 'wallet') return 'Ví AI'
  return String(gateway || 'Không rõ').toUpperCase()
}

const getPaymentTitle = (payment) => {
  if (payment?.loai_giao_dich === 'buy_subscription') {
    return payment?.goi_dich_vu?.ten_goi
      ? `Thanh toán ${payment.goi_dich_vu.ten_goi}`
      : 'Thanh toán gói Pro'
  }

  return 'Nạp tiền vào ví AI'
}

const canContinuePayment = (payment) =>
  payment?.trang_thai === 'pending' && Boolean(payment?.redirect_url) && !payment?.is_payment_link_expired

const continuePayment = (payment) => {
  if (!canContinuePayment(payment)) return

  window.location.href = payment.redirect_url
}

const paymentStats = computed(() => ({
  topups: payments.value.filter((item) => item.loai_giao_dich === 'topup_wallet').length,
  subscriptions: payments.value.filter((item) => item.loai_giao_dich === 'buy_subscription').length,
  pending: payments.value.filter((item) => item.trang_thai === 'pending').length,
}))

const normalizePayments = (response) => {
  const payload = response?.data || {}
  payments.value = payload.data || []
  pagination.current_page = payload.current_page || 1
  pagination.last_page = payload.last_page || 1
  pagination.total = payload.total || 0
  pagination.from = payload.from || 0
  pagination.to = payload.to || 0
}

const loadPayments = async (page = pagination.current_page, silent = false) => {
  if (silent) {
    refreshing.value = true
  } else {
    loading.value = true
  }

  try {
    const response = await paymentService.getPayments({
      page,
      per_page: pagination.per_page,
      loai_giao_dich: filters.loai_giao_dich || undefined,
      trang_thai: filters.trang_thai || undefined,
    })

    normalizePayments(response)
  } catch (error) {
    if (!silent) {
      notify.apiError(error, 'Không thể tải lịch sử thanh toán.')
    }
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

const changePage = async (page) => {
  if (page < 1 || page > pagination.last_page || page === pagination.current_page) return
  await loadPayments(page, true)
}

watch(
  () => [filters.loai_giao_dich, filters.trang_thai],
  async () => {
    await loadPayments(1)
  },
)

onMounted(async () => {
  await loadPayments(1)
})
</script>

<template>
  <div class="space-y-8">
    <section class="overflow-hidden rounded-[30px] border border-sky-200 bg-gradient-to-r from-[#0d1b38] via-[#17417c] to-[#2563eb] px-8 py-8 text-white shadow-[0_28px_90px_rgba(37,99,235,0.2)]">
      <div class="grid gap-6 lg:grid-cols-[minmax(0,1.4fr)_340px] lg:items-end">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.38em] text-sky-100/80">Payment History</p>
          <h1 class="mt-3 text-4xl font-black tracking-tight">Lịch sử thanh toán</h1>
          <p class="mt-4 max-w-3xl text-base leading-8 text-sky-50/90">
            Theo dõi toàn bộ giao dịch nạp ví AI và mua gói Pro, kiểm tra trạng thái cuối cùng và mở chi tiết từng giao dịch khi cần.
          </p>
        </div>

        <div class="rounded-[24px] border border-white/15 bg-white/10 p-5 backdrop-blur">
          <p class="text-sm font-semibold text-white/90">Bản ghi hiện có</p>
          <h2 class="mt-3 text-3xl font-black">{{ pagination.total }}</h2>
          <p class="mt-2 text-sm leading-7 text-sky-50/85">
            {{ filters.loai_giao_dich || filters.trang_thai ? 'Danh sách đang được lọc theo tiêu chí bạn chọn.' : 'Bao gồm cả nạp ví và thanh toán gói Pro.' }}
          </p>
        </div>
      </div>
    </section>

    <div class="grid gap-5 md:grid-cols-4">
      <article class="rounded-2xl border border-slate-200 bg-white/95 p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900/85">
        <p class="text-sm font-medium text-slate-500 dark:text-slate-400">Tổng giao dịch</p>
        <h2 class="mt-3 text-3xl font-black text-slate-900 dark:text-white">{{ pagination.total }}</h2>
      </article>
      <article class="rounded-2xl border border-slate-200 bg-white/95 p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900/85">
        <p class="text-sm font-medium text-slate-500 dark:text-slate-400">Nạp ví AI</p>
        <h2 class="mt-3 text-3xl font-black text-slate-900 dark:text-white">{{ paymentStats.topups }}</h2>
      </article>
      <article class="rounded-2xl border border-slate-200 bg-white/95 p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900/85">
        <p class="text-sm font-medium text-slate-500 dark:text-slate-400">Mua gói Pro</p>
        <h2 class="mt-3 text-3xl font-black text-slate-900 dark:text-white">{{ paymentStats.subscriptions }}</h2>
      </article>
      <article class="rounded-2xl border border-slate-200 bg-white/95 p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900/85">
        <p class="text-sm font-medium text-slate-500 dark:text-slate-400">Đang chờ xác nhận</p>
        <h2 class="mt-3 text-3xl font-black text-amber-600 dark:text-amber-200">{{ paymentStats.pending }}</h2>
      </article>
    </div>

    <section class="rounded-[28px] border border-slate-200 bg-white/95 p-6 shadow-[0_22px_60px_rgba(148,163,184,0.12)] dark:border-slate-800 dark:bg-slate-900/85">
      <div class="flex flex-col gap-4 border-b border-slate-200 pb-5 md:flex-row md:items-end md:justify-between dark:border-slate-800">
        <div>
          <h2 class="text-2xl font-bold text-slate-900 dark:text-white">Danh sách giao dịch</h2>
          <p class="mt-2 text-sm text-slate-600 dark:text-slate-400">
            {{ pagination.total }} giao dịch · từ {{ pagination.from || 0 }} đến {{ pagination.to || 0 }}
          </p>
        </div>

        <div class="flex flex-col gap-3 sm:flex-row">
          <select
            v-model="filters.loai_giao_dich"
            class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-sky-500 dark:border-slate-700 dark:bg-slate-950/60 dark:text-slate-200"
          >
            <option value="">Tất cả loại giao dịch</option>
            <option value="topup_wallet">Nạp ví AI</option>
            <option value="buy_subscription">Mua gói Pro</option>
          </select>

          <select
            v-model="filters.trang_thai"
            class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-sky-500 dark:border-slate-700 dark:bg-slate-950/60 dark:text-slate-200"
          >
            <option value="">Tất cả trạng thái</option>
            <option value="success">Thành công</option>
            <option value="pending">Đang chờ</option>
            <option value="failed">Thất bại</option>
            <option value="cancelled">Đã hủy</option>
          </select>

          <button
            type="button"
            class="inline-flex items-center justify-center gap-2 rounded-2xl border border-slate-200 px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:opacity-60 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
            :disabled="refreshing"
            @click="loadPayments(pagination.current_page, true)"
          >
            <span class="material-symbols-outlined text-[18px]">{{ refreshing ? 'progress_activity' : 'refresh' }}</span>
            Làm mới
          </button>
        </div>
      </div>

      <div v-if="loading" class="mt-5 space-y-3">
        <div v-for="index in 6" :key="index" class="h-28 animate-pulse rounded-2xl bg-slate-100 dark:bg-slate-800/70"></div>
      </div>

      <div v-else-if="!payments.length" class="mt-5 rounded-2xl border border-dashed border-slate-300 bg-slate-50/70 px-6 py-12 text-center text-sm leading-7 text-slate-600 dark:border-slate-700 dark:bg-slate-950/40 dark:text-slate-400">
        Chưa có giao dịch nào khớp với bộ lọc hiện tại.
      </div>

      <div v-else class="mt-5 space-y-3">
        <article
          v-for="payment in payments"
          :key="payment.id"
          class="rounded-2xl border border-slate-200 bg-slate-50/80 p-4 transition dark:border-slate-700 dark:bg-slate-950/45"
        >
          <div class="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
            <div class="min-w-0">
              <div class="flex flex-wrap items-center gap-2">
                <p class="text-base font-bold text-slate-900 dark:text-white">{{ getPaymentTitle(payment) }}</p>
                <span class="rounded-full border px-2.5 py-1 text-[11px] font-bold uppercase tracking-wide" :class="getStatusTone(payment.trang_thai)">
                  {{ getStatusLabel(payment.trang_thai) }}
                </span>
              </div>
              <p class="mt-2 text-sm text-slate-600 dark:text-slate-400">
                {{ getTypeLabel(payment.loai_giao_dich) }} · Mã {{ payment.ma_giao_dich_noi_bo }}
              </p>
              <p v-if="payment.goi_dich_vu?.ten_goi" class="mt-1 text-sm text-slate-500 dark:text-slate-400">
                Gói: {{ payment.goi_dich_vu.ten_goi }}
              </p>
              <p class="mt-2 text-xs uppercase tracking-[0.25em] text-slate-500">
                {{ formatDateTime(payment.paid_at || payment.updated_at || payment.created_at) }}
              </p>
            </div>

            <div class="grid min-w-[220px] gap-2 text-sm">
              <div class="flex items-center justify-between rounded-xl bg-white/85 px-3 py-2 dark:bg-slate-900/80">
                <span class="text-slate-500 dark:text-slate-400">Số tiền</span>
                <span class="font-bold text-slate-900 dark:text-white">{{ formatCurrency(payment.so_tien) }}</span>
              </div>
              <div class="flex items-center justify-between rounded-xl bg-white/85 px-3 py-2 dark:bg-slate-900/80">
                <span class="text-slate-500 dark:text-slate-400">Gateway</span>
                <span class="font-bold text-slate-900 dark:text-white">{{ getGatewayLabel(payment.gateway) }}</span>
              </div>
              <button
                v-if="canContinuePayment(payment)"
                type="button"
                class="inline-flex items-center justify-center rounded-xl bg-emerald-600 px-3 py-2 text-sm font-bold text-white transition hover:bg-emerald-700"
                @click="continuePayment(payment)"
              >
                Tiếp tục thanh toán
              </button>
              <RouterLink
                :to="{ name: 'PaymentDetail', params: { maGiaoDichNoiBo: payment.ma_giao_dich_noi_bo } }"
                class="inline-flex items-center justify-center rounded-xl bg-slate-900 px-3 py-2 text-sm font-bold text-white transition hover:bg-slate-800 dark:bg-slate-100 dark:text-slate-900"
              >
                Xem chi tiết
              </RouterLink>
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
            ? 'border-sky-600 bg-sky-600 text-white'
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
</template>
