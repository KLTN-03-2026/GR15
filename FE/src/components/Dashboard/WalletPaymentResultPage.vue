<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { walletService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'

const route = useRoute()
const router = useRouter()
const notify = useNotify()

const payment = ref(null)
const loading = ref(true)
const checking = ref(false)
const polling = ref(false)
const pollAttempts = ref(0)
const redirectCountdown = ref(2)
let pollTimer = null
let redirectTimer = null

const paymentCode = computed(() => String(route.params.maGiaoDichNoiBo || ''))
const resultCode = computed(() => String(route.query.resultCode || ''))
const gatewayMessage = computed(() => String(route.query.message || ''))
const paymentStorageKey = computed(() => `wallet-payment-draft:${paymentCode.value}`)

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

const clearPollTimer = () => {
  if (pollTimer) {
    window.clearTimeout(pollTimer)
    pollTimer = null
  }
}

const clearRedirectTimer = () => {
  if (redirectTimer) {
    window.clearInterval(redirectTimer)
    redirectTimer = null
  }
}

const gatewaySucceeded = computed(() => resultCode.value === '0' || resultCode.value === '00')

const paymentStatus = computed(() => payment.value?.trang_thai || 'pending')
const gatewayLabel = computed(() => getGatewayLabel(payment.value?.gateway))

const heroTitle = computed(() => {
  if (paymentStatus.value === 'success') return 'Nạp ví thành công'
  if (paymentStatus.value === 'failed' || paymentStatus.value === 'cancelled') return 'Giao dịch không thành công'
  if (gatewaySucceeded.value) return 'Cổng thanh toán đã trả về thành công'
  return 'Đang chờ xác nhận giao dịch'
})

const heroDescription = computed(() => {
  if (paymentStatus.value === 'success') {
    return 'Số tiền đã được ghi nhận vào ví AI của bạn. Bạn có thể quay lại ví để xem số dư mới.'
  }

  if (paymentStatus.value === 'failed' || paymentStatus.value === 'cancelled') {
    return gatewayMessage.value || 'Giao dịch chưa hoàn tất. Bạn có thể quay lại ví và tạo lại giao dịch mới.'
  }

  if (gatewaySucceeded.value) {
    return `${gatewayLabel.value} đã chuyển hướng về hệ thống, nhưng backend vẫn đang đợi xác nhận cuối cùng từ cổng thanh toán.`
  }

  return gatewayMessage.value || 'Giao dịch đang được kiểm tra. Hãy tải lại sau ít giây nếu trạng thái chưa đổi.'
})

const statusTone = computed(() => {
  if (paymentStatus.value === 'success') {
    return 'border-emerald-200 bg-emerald-50 text-emerald-700'
  }

  if (paymentStatus.value === 'failed' || paymentStatus.value === 'cancelled') {
    return 'border-rose-200 bg-rose-50 text-rose-700'
  }

  return 'border-amber-200 bg-amber-50 text-amber-700'
})

const statusLabel = computed(() => {
  if (paymentStatus.value === 'success') return 'Đã cộng ví'
  if (paymentStatus.value === 'failed') return 'Thanh toán thất bại'
  if (paymentStatus.value === 'cancelled') return 'Đã hủy giao dịch'
  if (gatewaySucceeded.value) return 'Đang chờ IPN / xác nhận cuối'
  return 'Đang xử lý'
})

const shouldAutoRedirectToWallet = computed(() => paymentStatus.value === 'success')

const startSuccessRedirect = () => {
  clearRedirectTimer()

  if (!shouldAutoRedirectToWallet.value) return

  redirectCountdown.value = 2
  redirectTimer = window.setInterval(async () => {
    if (redirectCountdown.value <= 1) {
      clearRedirectTimer()
      await router.replace('/wallet')
      return
    }

    redirectCountdown.value -= 1
  }, 1000)
}

const loadPayment = async (options = {}) => {
  if (!paymentCode.value) return

  const { silent = false, fromPolling = false } = options

  if (fromPolling) {
    polling.value = true
  } else if (silent) {
    checking.value = true
  } else {
    loading.value = true
  }

  try {
    const response = await walletService.getTopUp(paymentCode.value)
    payment.value = response?.data || null

    if (payment.value?.trang_thai === 'success') {
      sessionStorage.removeItem(paymentStorageKey.value)
      clearPollTimer()
      startSuccessRedirect()
    }
  } catch (error) {
    if (!silent) {
      notify.apiError(error, 'Không thể tải kết quả thanh toán.')
    }
  } finally {
    loading.value = false
    if (fromPolling) {
      polling.value = false
    } else if (silent) {
      checking.value = false
    }
  }
}

const scheduleStatusPolling = () => {
  clearPollTimer()

  if (!gatewaySucceeded.value) return
  if (payment.value?.trang_thai === 'success' || payment.value?.trang_thai === 'failed' || payment.value?.trang_thai === 'cancelled') {
    return
  }
  if (pollAttempts.value >= 5) return

  pollTimer = window.setTimeout(async () => {
    pollAttempts.value += 1
    await loadPayment({ silent: true, fromPolling: true })
    scheduleStatusPolling()
  }, 3000)
}

const refreshPayment = async () => {
  pollAttempts.value = 0
  await loadPayment({ silent: true })
  scheduleStatusPolling()
}

onMounted(async () => {
  await loadPayment({})
  scheduleStatusPolling()
})

onBeforeUnmount(() => {
  clearPollTimer()
  clearRedirectTimer()
})
</script>

<template>
  <div class="mx-auto max-w-5xl space-y-6">
    <section class="overflow-hidden rounded-[30px] border px-8 py-8 shadow-[0_28px_90px_rgba(15,23,42,0.12)]" :class="statusTone">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.38em] opacity-80">Payment Result</p>
          <h1 class="mt-3 text-4xl font-black tracking-tight">{{ heroTitle }}</h1>
          <p class="mt-4 max-w-3xl text-base leading-8 opacity-90">
            {{ heroDescription }}
          </p>
          <p v-if="shouldAutoRedirectToWallet" class="mt-3 text-sm font-semibold opacity-80">
            Tự động quay về Ví AI sau {{ redirectCountdown }} giây.
          </p>
        </div>

        <div class="rounded-[24px] border border-current/15 bg-white/55 p-5 backdrop-blur">
          <p class="text-sm font-semibold opacity-80">Trạng thái</p>
          <p class="mt-3 text-2xl font-black">{{ statusLabel }}</p>
        </div>
      </div>
    </section>

    <section class="grid gap-6 lg:grid-cols-[minmax(0,1.2fr)_320px]">
      <article class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-[0_22px_60px_rgba(148,163,184,0.12)]">
        <div v-if="loading" class="rounded-2xl border border-dashed border-slate-200 px-6 py-12 text-center text-slate-500">
          Đang tải kết quả thanh toán...
        </div>

        <div v-else-if="payment" class="space-y-5">
          <div class="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p class="text-sm font-semibold uppercase tracking-[0.22em] text-slate-400">Mã giao dịch</p>
              <p class="mt-2 text-2xl font-black text-slate-900">{{ payment.ma_giao_dich_noi_bo }}</p>
            </div>
            <span class="rounded-full border px-4 py-2 text-sm font-bold" :class="statusTone">
              {{ statusLabel }}
            </span>
          </div>

          <div class="grid gap-4 sm:grid-cols-2">
            <div class="rounded-2xl border border-slate-200 bg-slate-50 px-5 py-4">
              <p class="text-sm font-medium text-slate-500">Số tiền</p>
              <p class="mt-2 text-3xl font-black text-slate-900">{{ formatCurrency(payment.so_tien) }}</p>
            </div>
            <div class="rounded-2xl border border-slate-200 bg-slate-50 px-5 py-4">
              <p class="text-sm font-medium text-slate-500">Thời điểm cập nhật</p>
              <p class="mt-2 text-lg font-bold text-slate-900">{{ formatDateTime(payment.updated_at) }}</p>
            </div>
          </div>

          <div class="rounded-2xl border border-slate-200 bg-slate-50 px-5 py-4">
            <p class="text-sm font-medium text-slate-500">Cổng thanh toán</p>
            <p class="mt-2 text-lg font-bold text-slate-900">{{ gatewayLabel }}</p>
          </div>

          <div class="rounded-2xl border border-slate-200 bg-slate-50 px-5 py-4">
            <p class="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">Thông điệp từ cổng thanh toán</p>
            <p class="mt-2 text-base leading-7 text-slate-700">
              {{ gatewayMessage || 'Không có thông điệp bổ sung từ cổng thanh toán.' }}
            </p>
          </div>

          <div class="flex flex-wrap gap-3">
            <button
              type="button"
              class="inline-flex items-center justify-center gap-2 rounded-2xl bg-slate-900 px-5 py-3 text-sm font-bold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-70"
              :disabled="checking"
              @click="refreshPayment"
            >
              <span class="material-symbols-outlined">{{ checking ? 'hourglass_top' : 'refresh' }}</span>
              <span>{{ checking ? 'Đang kiểm tra...' : 'Kiểm tra lại trạng thái' }}</span>
            </button>

            <RouterLink
              to="/wallet"
              class="inline-flex items-center justify-center rounded-2xl border border-slate-200 px-5 py-3 text-sm font-bold text-slate-700 transition hover:border-slate-300 hover:bg-slate-50"
            >
              Quay lại Ví AI
            </RouterLink>
          </div>
        </div>

        <div v-else class="rounded-2xl border border-dashed border-rose-200 bg-rose-50 px-6 py-12 text-center text-rose-700">
          Không tìm thấy giao dịch thanh toán.
        </div>
      </article>

      <aside class="space-y-4">
        <div class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-[0_22px_60px_rgba(148,163,184,0.12)]">
          <p class="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">Lưu ý</p>
          <ul class="mt-4 space-y-3 text-sm leading-7 text-slate-600">
            <li>1. Redirect thành công từ cổng thanh toán chưa đồng nghĩa backend đã cộng ví xong.</li>
            <li>2. Hệ thống ưu tiên IPN để chốt kết quả cuối cùng và ghi số dư ví.</li>
            <li>3. Nếu đang chạy local, IPN từ cổng thanh toán có thể không gọi được về `127.0.0.1`.</li>
          </ul>
        </div>
      </aside>
    </section>
  </div>
</template>
