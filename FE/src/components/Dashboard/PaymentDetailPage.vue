<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { paymentService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'

const route = useRoute()
const notify = useNotify()

const loading = ref(true)
const payment = ref(null)

const paymentCode = computed(() => String(route.params.maGiaoDichNoiBo || ''))

const formatCurrency = (value) =>
  `${new Intl.NumberFormat('vi-VN').format(Number(value || 0))} đ`

const formatDateTime = (value) => {
  if (!value) return 'Chưa cập nhật'

  return new Intl.DateTimeFormat('vi-VN', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

const getGatewayLabel = (gateway) => {
  if (gateway === 'momo') return 'MoMo'
  if (gateway === 'vnpay') return 'VNPay'
  if (gateway === 'wallet') return 'Ví AI'
  return String(gateway || 'Không rõ').toUpperCase()
}

const paymentTypeLabel = computed(() => {
  if (payment.value?.loai_giao_dich === 'topup_wallet') return 'Nạp ví AI'
  if (payment.value?.loai_giao_dich === 'buy_subscription') return 'Mua gói Pro'
  return 'Thanh toán'
})

const statusLabel = computed(() => {
  if (payment.value?.trang_thai === 'success') return 'Thành công'
  if (payment.value?.trang_thai === 'pending') return 'Đang chờ xác nhận'
  if (payment.value?.trang_thai === 'failed') return 'Thất bại'
  if (payment.value?.trang_thai === 'cancelled') return 'Đã hủy'
  return 'Không rõ'
})

const statusTone = computed(() => {
  if (payment.value?.trang_thai === 'success') return 'border-emerald-200 bg-emerald-50 text-emerald-700'
  if (payment.value?.trang_thai === 'pending') return 'border-amber-200 bg-amber-50 text-amber-700'
  if (payment.value?.trang_thai === 'failed') return 'border-rose-200 bg-rose-50 text-rose-700'
  if (payment.value?.trang_thai === 'cancelled') return 'border-slate-200 bg-slate-100 text-slate-600'
  return 'border-slate-200 bg-slate-50 text-slate-600'
})

const heroTitle = computed(() => {
  if (payment.value?.trang_thai === 'success') return 'Giao dịch đã hoàn tất'
  if (payment.value?.trang_thai === 'pending') return 'Giao dịch đang chờ xác nhận'
  if (payment.value?.trang_thai === 'failed') return 'Giao dịch đã thất bại'
  if (payment.value?.trang_thai === 'cancelled') return 'Giao dịch đã bị hủy'
  return 'Chi tiết giao dịch'
})

const heroDescription = computed(() => {
  if (payment.value?.loai_giao_dich === 'buy_subscription') {
    return 'Theo dõi trạng thái giao dịch mua gói Pro, mã gateway và thời điểm hệ thống ghi nhận quyền lợi.'
  }

  return 'Theo dõi trạng thái nạp ví AI, mã giao dịch gateway và số dư ví liên quan tới giao dịch này.'
})

const canContinuePayment = computed(() =>
  payment.value?.trang_thai === 'pending'
    && Boolean(payment.value?.redirect_url)
    && !payment.value?.is_payment_link_expired
)

const continuePayment = () => {
  if (!canContinuePayment.value) return

  window.location.href = payment.value.redirect_url
}

const loadPaymentDetail = async () => {
  loading.value = true
  try {
    const response = await paymentService.getPaymentDetail(paymentCode.value)
    payment.value = response?.data || null
  } catch (error) {
    payment.value = null
    notify.apiError(error, 'Không thể tải chi tiết giao dịch thanh toán.')
  } finally {
    loading.value = false
  }
}

onMounted(loadPaymentDetail)
</script>

<template>
  <div class="mx-auto max-w-6xl space-y-6">
    <section class="overflow-hidden rounded-[30px] border px-8 py-8 shadow-[0_28px_90px_rgba(15,23,42,0.12)]" :class="statusTone">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.38em] opacity-80">Payment Detail</p>
          <h1 class="mt-3 text-4xl font-black tracking-tight">{{ heroTitle }}</h1>
          <p class="mt-4 max-w-3xl text-base leading-8 opacity-90">
            {{ heroDescription }}
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
          Đang tải chi tiết giao dịch...
        </div>

        <div v-else-if="payment" class="space-y-5">
          <div class="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p class="text-sm font-semibold uppercase tracking-[0.22em] text-slate-400">Mã giao dịch nội bộ</p>
              <p class="mt-2 text-2xl font-black text-slate-900">{{ payment.ma_giao_dich_noi_bo }}</p>
            </div>
            <span class="rounded-full border px-4 py-2 text-sm font-bold" :class="statusTone">
              {{ statusLabel }}
            </span>
          </div>

          <div class="grid gap-4 md:grid-cols-2">
            <div class="rounded-2xl border border-slate-200 bg-slate-50 px-5 py-4">
              <p class="text-sm font-medium text-slate-500">Loại giao dịch</p>
              <p class="mt-2 text-xl font-black text-slate-900">{{ paymentTypeLabel }}</p>
            </div>
            <div class="rounded-2xl border border-slate-200 bg-slate-50 px-5 py-4">
              <p class="text-sm font-medium text-slate-500">Số tiền</p>
              <p class="mt-2 text-3xl font-black text-slate-900">{{ formatCurrency(payment.so_tien) }}</p>
            </div>
            <div class="rounded-2xl border border-slate-200 bg-slate-50 px-5 py-4">
              <p class="text-sm font-medium text-slate-500">Gateway</p>
              <p class="mt-2 text-lg font-bold text-slate-900">{{ getGatewayLabel(payment.gateway) }}</p>
            </div>
            <div class="rounded-2xl border border-slate-200 bg-slate-50 px-5 py-4">
              <p class="text-sm font-medium text-slate-500">Mã gateway</p>
              <p class="mt-2 text-lg font-bold text-slate-900">{{ payment.ma_giao_dich_gateway || 'Chưa có' }}</p>
            </div>
          </div>

          <div class="grid gap-4 md:grid-cols-2">
            <div class="rounded-2xl border border-slate-200 bg-slate-50 px-5 py-4">
              <p class="text-sm font-medium text-slate-500">Tạo lúc</p>
              <p class="mt-2 text-base font-bold text-slate-900">{{ formatDateTime(payment.created_at) }}</p>
            </div>
            <div class="rounded-2xl border border-slate-200 bg-slate-50 px-5 py-4">
              <p class="text-sm font-medium text-slate-500">Thanh toán lúc</p>
              <p class="mt-2 text-base font-bold text-slate-900">{{ formatDateTime(payment.paid_at) }}</p>
            </div>
          </div>

          <div v-if="payment.goi_dich_vu?.ten_goi" class="rounded-2xl border border-slate-200 bg-slate-50 px-5 py-4">
            <p class="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">Gói dịch vụ</p>
            <p class="mt-2 text-base font-bold text-slate-900">{{ payment.goi_dich_vu.ten_goi }}</p>
            <p class="mt-1 text-sm text-slate-500">Mã gói: {{ payment.goi_dich_vu.ma_goi || 'Chưa có' }}</p>
          </div>

          <div v-if="payment.vi_nguoi_dung" class="rounded-2xl border border-slate-200 bg-slate-50 px-5 py-4">
            <p class="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">Ví liên quan</p>
            <div class="mt-3 grid gap-4 md:grid-cols-2">
              <div>
                <p class="text-sm text-slate-500">Số dư hiện tại</p>
                <p class="mt-1 text-lg font-bold text-slate-900">{{ formatCurrency(payment.vi_nguoi_dung.so_du_hien_tai) }}</p>
              </div>
              <div>
                <p class="text-sm text-slate-500">Đang tạm giữ</p>
                <p class="mt-1 text-lg font-bold text-slate-900">{{ formatCurrency(payment.vi_nguoi_dung.so_du_tam_giu) }}</p>
              </div>
            </div>
          </div>

          <div class="rounded-2xl border border-slate-200 bg-slate-50 px-5 py-4">
            <p class="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">Nội dung giao dịch</p>
            <p class="mt-2 text-base leading-7 text-slate-700">
              {{ payment.noi_dung || 'Không có nội dung bổ sung.' }}
            </p>
          </div>
        </div>

        <div v-else class="rounded-2xl border border-dashed border-rose-200 bg-rose-50 px-6 py-12 text-center text-rose-700">
          Không tìm thấy giao dịch thanh toán.
        </div>
      </article>

      <aside class="space-y-4">
        <div class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-[0_22px_60px_rgba(148,163,184,0.12)]">
          <p class="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">Điều hướng</p>
          <div class="mt-4 space-y-3">
            <button
              v-if="canContinuePayment"
              type="button"
              class="inline-flex w-full items-center justify-center rounded-2xl bg-emerald-600 px-4 py-3 text-sm font-bold text-white transition hover:bg-emerald-700"
              @click="continuePayment"
            >
              Tiếp tục thanh toán
            </button>

            <RouterLink
              to="/payments"
              class="inline-flex w-full items-center justify-center rounded-2xl bg-slate-900 px-4 py-3 text-sm font-bold text-white transition hover:bg-slate-800"
            >
              Quay lại lịch sử thanh toán
            </RouterLink>

            <RouterLink
              :to="payment?.loai_giao_dich === 'buy_subscription' ? '/plans' : '/wallet'"
              class="inline-flex w-full items-center justify-center rounded-2xl border border-slate-200 px-4 py-3 text-sm font-bold text-slate-700 transition hover:bg-slate-50"
            >
              {{ payment?.loai_giao_dich === 'buy_subscription' ? 'Đi tới Gói Pro' : 'Đi tới Ví AI' }}
            </RouterLink>
          </div>
        </div>

        <div class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-[0_22px_60px_rgba(148,163,184,0.12)]">
          <p class="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">Lưu ý</p>
          <ul class="mt-4 space-y-3 text-sm leading-7 text-slate-600">
            <li>1. Với giao dịch `pending`, hệ thống vẫn đang chờ xác nhận cuối từ gateway hoặc tiến trình nội bộ.</li>
            <li>2. Link thanh toán qua gateway ngoài chỉ nên được mở lại trong thời gian còn hiệu lực.</li>
            <li>3. Nạp ví AI và mua gói Pro dùng chung bảng giao dịch, nhưng quyền lợi được ghi nhận theo từng loại.</li>
            <li>4. Nếu giao dịch đã thành công nhưng giao diện cũ chưa cập nhật, hãy tải lại trang hoặc quay về màn hình tương ứng.</li>
          </ul>
        </div>
      </aside>
    </section>
  </div>
</template>
