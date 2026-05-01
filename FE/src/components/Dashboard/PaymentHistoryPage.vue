<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/20 p-4 md:p-8">

    <!-- ── Header ──────────────────────────────────────────────────── -->
    <div class="mx-auto max-w-4xl">
      <div class="mb-8 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 class="text-2xl font-black text-slate-900">Lịch sử thanh toán</h1>
          <p class="mt-1 text-sm text-slate-500">Tra cứu toàn bộ giao dịch của bạn trên SmartJob AI.</p>
        </div>
        <!-- Filter bar -->
        <div class="flex flex-wrap gap-2">
          <select
            v-model="filters.loai_giao_dich"
            @change="loadPayments(true)"
            class="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 shadow-sm outline-none focus:border-[#2463eb]"
          >
            <option value="">Tất cả loại</option>
            <option value="topup_wallet">Nạp ví AI</option>
            <option value="buy_subscription">Mua gói Pro</option>
          </select>
          <select
            v-model="filters.trang_thai"
            @change="loadPayments(true)"
            class="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 shadow-sm outline-none focus:border-[#2463eb]"
          >
            <option value="">Tất cả trạng thái</option>
            <option value="pending">Chờ xác nhận</option>
            <option value="thanh_cong">Thành công</option>
            <option value="that_bai">Thất bại</option>
            <option value="huy">Đã hủy</option>
          </select>
        </div>
      </div>

      <!-- ── Loading skeleton ───────────────────────────────────────── -->
      <div v-if="loading" class="space-y-3">
        <div v-for="i in 5" :key="i" class="h-20 animate-pulse rounded-2xl bg-slate-200"></div>
      </div>

      <!-- ── Empty state ───────────────────────────────────────────── -->
      <div v-else-if="!payments.length" class="flex flex-col items-center gap-4 py-20 text-center">
        <div class="flex size-16 items-center justify-center rounded-full bg-slate-100">
          <span class="material-symbols-outlined text-3xl text-slate-400">receipt_long</span>
        </div>
        <p class="font-semibold text-slate-500">Chưa có giao dịch nào.</p>
      </div>

      <!-- ── Payment list ──────────────────────────────────────────── -->
      <div v-else class="space-y-3">
        <div
          v-for="p in payments"
          :key="p.id"
          @click="$router.push(`/payments/${p.ma_giao_dich_noi_bo}`)"
          class="group flex cursor-pointer items-center justify-between rounded-2xl border border-slate-200 bg-white px-5 py-4 shadow-sm transition hover:border-[#2463eb]/30 hover:shadow-md hover:-translate-y-0.5"
        >
          <div class="flex items-center gap-4">
            <!-- Icon by type -->
            <div
              class="flex size-11 shrink-0 items-center justify-center rounded-2xl"
              :class="typeIconBg(p.loai_giao_dich)"
            >
              <span class="material-symbols-outlined text-xl">
                {{ p.loai_giao_dich === 'buy_subscription' ? 'workspace_premium' : 'account_balance_wallet' }}
              </span>
            </div>
            <div>
              <p class="font-bold text-slate-800">{{ typeLabel(p.loai_giao_dich) }}</p>
              <p class="mt-0.5 text-xs text-slate-500">
                {{ formatDatetime(p.created_at) }} · {{ p.gateway?.toUpperCase() }}
              </p>
            </div>
          </div>
          <div class="flex flex-col items-end gap-1">
            <p class="font-black text-slate-900">{{ formatCurrency(p.so_tien) }}</p>
            <span
              class="flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-bold"
              :class="statusClass(p.trang_thai)"
            >
              <span class="size-1.5 rounded-full bg-current"></span>
              {{ statusLabel(p.trang_thai) }}
            </span>
          </div>
        </div>
      </div>

      <!-- ── Pagination ──────────────────────────────────────────────── -->
      <div v-if="pagination && pagination.last_page > 1" class="mt-6 flex items-center justify-center gap-2">
        <button
          :disabled="pagination.current_page <= 1"
          @click="goPage(pagination.current_page - 1)"
          class="flex size-9 items-center justify-center rounded-xl border border-slate-200 bg-white text-slate-600 shadow-sm transition hover:border-[#2463eb] hover:text-[#2463eb] disabled:opacity-40"
        >
          <span class="material-symbols-outlined text-[18px]">chevron_left</span>
        </button>
        <span class="text-sm font-semibold text-slate-600">
          Trang {{ pagination.current_page }} / {{ pagination.last_page }}
        </span>
        <button
          :disabled="pagination.current_page >= pagination.last_page"
          @click="goPage(pagination.current_page + 1)"
          class="flex size-9 items-center justify-center rounded-xl border border-slate-200 bg-white text-slate-600 shadow-sm transition hover:border-[#2463eb] hover:text-[#2463eb] disabled:opacity-40"
        >
          <span class="material-symbols-outlined text-[18px]">chevron_right</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { paymentService } from '@/services/api.js'

const router = useRouter()

const payments   = ref([])
const pagination = ref(null)
const loading    = ref(true)

const filters = reactive({
  loai_giao_dich: '',
  trang_thai:     '',
  page:           1,
  per_page:       10,
})

const loadPayments = async (resetPage = false) => {
  if (resetPage) filters.page = 1
  loading.value = true
  try {
    const response = await paymentService.getPayments(filters)
    const raw = response?.data
    if (raw?.data) {
      // Laravel paginated response
      payments.value   = raw.data
      pagination.value = {
        current_page: raw.current_page,
        last_page:    raw.last_page,
        total:        raw.total,
      }
    } else if (Array.isArray(raw)) {
      payments.value   = raw
      pagination.value = null
    } else {
      payments.value = []
    }
  } catch (e) {
    payments.value = []
  } finally {
    loading.value = false
  }
}

const goPage = (page) => {
  filters.page = page
  loadPayments()
}

onMounted(() => loadPayments())

// ── Helpers ────────────────────────────────────────────────────────────────────
const typeLabel = (type) => {
  const map = { topup_wallet: 'Nạp ví AI', buy_subscription: 'Mua gói Pro' }
  return map[type] || 'Thanh toán'
}

const typeIconBg = (type) => {
  const map = {
    topup_wallet:     'bg-indigo-100 text-indigo-600',
    buy_subscription: 'bg-amber-100 text-amber-600',
  }
  return map[type] || 'bg-slate-100 text-slate-600'
}

const statusLabel = (status) => {
  const map = {
    pending:    'Chờ xác nhận',
    thanh_cong: 'Thành công',
    that_bai:   'Thất bại',
    huy:        'Đã hủy',
  }
  return map[status] || status
}

const statusClass = (status) => {
  const map = {
    pending:    'bg-amber-50 text-amber-600',
    thanh_cong: 'bg-emerald-50 text-emerald-700',
    that_bai:   'bg-rose-50 text-rose-600',
    huy:        'bg-slate-100 text-slate-500',
  }
  return map[status] || 'bg-slate-100 text-slate-500'
}

const formatCurrency = (amount) => {
  if (amount == null) return '—'
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency', currency: 'VND', maximumFractionDigits: 0,
  }).format(amount)
}

const formatDatetime = (value) => {
  if (!value) return '—'
  return new Intl.DateTimeFormat('vi-VN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit',
    hour12: false,
  }).format(new Date(value))
}
</script>
