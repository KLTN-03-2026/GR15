<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { careerReportService, profileService, walletService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'
import {
  getBillingFeatureLabel,
  getEntitlementActionLabel,
  getEntitlementCoverageNote,
  getEntitlementUsageHint,
} from '@/utils/billing'

const notify = useNotify()

const loadingProfiles = ref(false)
const loadingReports = ref(false)
const loadingBilling = ref(false)
const generating = ref(false)
const deletingReportId = ref(null)
const showDeleteModal = ref(false)
const reportToDelete = ref(null)
const profiles = ref([])
const reports = ref([])
const selectedProfileId = ref('')
const selectedReportId = ref(null)
const wallet = ref(null)
const pricing = ref([])
const entitlements = ref([])
const currentSubscription = ref(null)

const pagination = reactive({
  current_page: 1,
  last_page: 1,
  total: 0,
  from: 0,
  to: 0,
  per_page: 10,
})

const selectedProfile = computed(() =>
  profiles.value.find((item) => Number(item.id) === Number(selectedProfileId.value)) || null
)

const selectedReport = computed(() =>
  reports.value.find((item) => Number(item.id) === Number(selectedReportId.value)) || null
)

const walletStats = computed(() => ({
  available: Number(wallet.value?.so_du_kha_dung || 0),
  hold: Number(wallet.value?.so_du_tam_giu || 0),
}))

const careerReportPrice = computed(() =>
  Number(pricing.value.find((item) => item.feature_code === 'career_report_generation')?.don_gia || 0)
)

const careerReportEntitlement = computed(() =>
  entitlements.value.find((item) => item.feature_code === 'career_report_generation') || null
)

const careerReportBillingLabel = computed(() => {
  return getEntitlementActionLabel(careerReportEntitlement.value, {
    actionLabel: 'Sinh Career Report',
    price: careerReportPrice.value,
    formatCurrency,
  })
})

const careerReportWalletNote = computed(() => {
  return getEntitlementCoverageNote(careerReportEntitlement.value, {
    currentSubscription: currentSubscription.value,
    featureLabel: getBillingFeatureLabel('career_report_generation'),
    price: careerReportPrice.value,
    formatCurrency,
  })
})

const careerReportUsageHint = computed(() => {
  return getEntitlementUsageHint(careerReportEntitlement.value, {
    currentSubscription: currentSubscription.value,
    successOutcomeText: 'báo cáo được tạo thành công',
  })
})

const normalizeProfiles = (response) => {
  const payload = response?.data || {}
  profiles.value = payload.data || []

  if (!selectedProfileId.value && profiles.value.length) {
    selectedProfileId.value = String(profiles.value[0].id)
  }
}

const normalizeReports = (response) => {
  const payload = response?.data || {}
  reports.value = payload.data || []
  pagination.current_page = payload.current_page || 1
  pagination.last_page = payload.last_page || 1
  pagination.total = payload.total || 0
  pagination.from = payload.from || 0
  pagination.to = payload.to || 0

  if (reports.value.length) {
    const stillExists = reports.value.some((item) => Number(item.id) === Number(selectedReportId.value))
    if (!stillExists) {
      selectedReportId.value = reports.value[0].id
    }
  } else {
    selectedReportId.value = null
  }
}

const formattedReportBody = computed(() => {
  const raw = selectedReport.value?.bao_cao_chi_tiet || ''
  return raw
    .split(/\n+/)
    .map(line => line.trim())
    .filter(Boolean)
})

const formatCurrency = (value) =>
  `${new Intl.NumberFormat('vi-VN').format(Number(value || 0))} đ`

const formatDate = (value) => {
  if (!value) return 'Chưa rõ'
  return new Date(value).toLocaleString('vi-VN')
}

const loadProfiles = async () => {
  loadingProfiles.value = true
  try {
    const response = await profileService.getProfiles({
      per_page: 100,
      sort_by: 'updated_at',
      sort_dir: 'desc',
    })
    normalizeProfiles(response)
  } catch (error) {
    profiles.value = []
    selectedProfileId.value = ''
    notify.apiError(error, 'Không thể tải danh sách hồ sơ.')
  } finally {
    loadingProfiles.value = false
  }
}

const loadReports = async (page = 1) => {
  loadingReports.value = true
  try {
    const response = await careerReportService.getReports({
      page,
      per_page: pagination.per_page,
      ho_so_id: selectedProfileId.value || undefined,
    })
    normalizeReports(response)
  } catch (error) {
    reports.value = []
    selectedReportId.value = null
    notify.apiError(error, 'Không thể tải lịch sử Career Report.')
  } finally {
    loadingReports.value = false
  }
}

const loadBilling = async () => {
  loadingBilling.value = true
  try {
    const [walletResponse, pricingResponse, entitlementsResponse] = await Promise.all([
      walletService.getWallet(),
      walletService.getPricing(),
      walletService.getEntitlements(),
    ])

    wallet.value = walletResponse?.data?.wallet || null
    pricing.value = pricingResponse?.data || []
    currentSubscription.value = entitlementsResponse?.data?.current_subscription || null
    entitlements.value = entitlementsResponse?.data?.entitlements || []
  } catch (error) {
    notify.apiError(error, 'Không thể tải dữ liệu ví cho Career Report.')
  } finally {
    loadingBilling.value = false
  }
}

const handleBillingError = (error) => {
  if (error?.code === 'WALLET_INSUFFICIENT_BALANCE') {
    notify.warning('Số dư ví không đủ để sinh Career Report. Hãy nạp thêm tiền rồi thử lại.')
    return true
  }

  if (error?.code === 'BILLING_DUPLICATE_REQUEST') {
    notify.info('Yêu cầu sinh báo cáo trước đó vẫn đang xử lý. Vui lòng chờ thêm một chút.')
    return true
  }

  return false
}

const generateReport = async () => {
  if (!selectedProfileId.value) {
    notify.warning('Bạn cần chọn một hồ sơ trước khi sinh Career Report.')
    return
  }

  generating.value = true
  try {
    const response = await careerReportService.generateReport(selectedProfileId.value)
    notify.success('Đã sinh Career Report mới cho hồ sơ đã chọn.')
    await Promise.all([loadReports(1), loadBilling()])
    if (response?.data?.id) {
      selectedReportId.value = response.data.id
    }
  } catch (error) {
    if (handleBillingError(error)) return
    notify.apiError(error, 'Không thể sinh Career Report.')
  } finally {
    generating.value = false
  }
}

const openDeleteModal = (report) => {
  if (!report?.id) return
  reportToDelete.value = report
  showDeleteModal.value = true
}

const closeDeleteModal = () => {
  if (deletingReportId.value) return
  showDeleteModal.value = false
  reportToDelete.value = null
}

const deleteReport = async () => {
  if (!reportToDelete.value?.id) return

  deletingReportId.value = reportToDelete.value.id
  try {
    await careerReportService.deleteReport(reportToDelete.value.id)
    notify.success('Đã xóa Career Report khỏi lịch sử.')
    showDeleteModal.value = false
    reportToDelete.value = null
    await loadReports(pagination.current_page)
  } catch (error) {
    notify.apiError(error, 'Không thể xóa Career Report.')
  } finally {
    deletingReportId.value = null
  }
}

watch(selectedProfileId, async (value) => {
  if (!value) return
  await loadReports(1)
})

onMounted(async () => {
  await Promise.all([loadProfiles(), loadBilling()])
  if (selectedProfileId.value) {
    await loadReports(1)
  }
})
</script>

<template>
  <div class="min-h-screen text-slate-900 dark:text-white">
    <section class="mx-auto max-w-[1600px] px-6 py-6">
      <div class="grid gap-6 xl:grid-cols-[340px_minmax(0,1fr)]">
        <aside class="space-y-6">
          <section class="rounded-[28px] border border-emerald-200 bg-gradient-to-br from-emerald-50 via-white to-teal-50 p-6 shadow-[0_22px_60px_rgba(16,185,129,0.12)] dark:border-emerald-500/20 dark:bg-slate-900/85">
            <div class="flex items-start justify-between gap-4">
              <div>
                <p class="text-xs font-semibold uppercase tracking-[0.3em] text-emerald-600/80 dark:text-emerald-200/70">AI Wallet</p>
                <h2 class="mt-3 text-2xl font-bold text-slate-900 dark:text-white">
                  {{ loadingBilling ? 'Đang tải số dư...' : formatCurrency(walletStats.available) }}
                </h2>
                <p class="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-400">
                  {{ careerReportWalletNote }}
                </p>
              </div>
              <RouterLink
                :to="{ name: 'Wallet' }"
                class="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-4 py-3 text-sm font-bold text-white transition hover:bg-emerald-700"
              >
                <span class="material-symbols-outlined text-[18px]">account_balance_wallet</span>
                Nạp ví
              </RouterLink>
            </div>

            <div class="mt-5 grid grid-cols-2 gap-3">
              <div class="rounded-2xl border border-white/70 bg-white/85 px-4 py-4 dark:border-white/10 dark:bg-slate-950/40">
                <p class="text-xs uppercase tracking-[0.25em] text-slate-500">Khả dụng</p>
                <p class="mt-2 text-xl font-black text-slate-900 dark:text-white">{{ formatCurrency(walletStats.available) }}</p>
              </div>
              <div class="rounded-2xl border border-white/70 bg-white/85 px-4 py-4 dark:border-white/10 dark:bg-slate-950/40">
                <p class="text-xs uppercase tracking-[0.25em] text-slate-500">Tạm giữ</p>
                <p class="mt-2 text-xl font-black text-slate-900 dark:text-white">{{ formatCurrency(walletStats.hold) }}</p>
              </div>
            </div>
          </section>

          <section class="rounded-[28px] border border-slate-200 bg-white/95 p-6 shadow-[0_22px_60px_rgba(148,163,184,0.12)] dark:border-white/10 dark:bg-slate-900/85 dark:shadow-[0_22px_60px_rgba(15,23,42,0.32)]">
            <h2 class="text-2xl font-bold text-slate-900 dark:text-white">Sinh báo cáo mới</h2>
            <p class="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-400">
              Chọn hồ sơ muốn phân tích rồi sinh báo cáo tư vấn nghề nghiệp bằng AI. {{ careerReportUsageHint }}
            </p>

            <div class="mt-5">
              <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Hồ sơ ứng viên</label>
              <select
                v-model="selectedProfileId"
                class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-blue-400/60 dark:border-white/10 dark:bg-slate-800/90 dark:text-white"
                :disabled="loadingProfiles || generating"
              >
                <option value="" disabled>{{ loadingProfiles ? 'Đang tải hồ sơ...' : 'Chọn một hồ sơ' }}</option>
                <option v-for="profile in profiles" :key="profile.id" :value="String(profile.id)">
                  {{ profile.tieu_de_ho_so || `Hồ sơ #${profile.id}` }}
                </option>
              </select>
            </div>

            <div v-if="selectedProfile" class="mt-5 rounded-2xl border border-slate-200 bg-slate-50/80 p-4 dark:border-white/10 dark:bg-slate-950/45">
              <p class="text-[11px] uppercase tracking-[0.3em] text-slate-500 dark:text-slate-400">Hồ sơ đang chọn</p>
              <h3 class="mt-2 text-xl font-bold text-slate-900 dark:text-white">{{ selectedProfile.tieu_de_ho_so || `Hồ sơ #${selectedProfile.id}` }}</h3>
              <p class="mt-2 text-sm text-slate-600 dark:text-slate-400">
                {{ selectedProfile.trinh_do || 'Chưa cập nhật trình độ' }} · {{ selectedProfile.kinh_nghiem_nam || 0 }} năm kinh nghiệm
              </p>
            </div>

            <button
              type="button"
              class="mt-5 inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-[#2f67ee] to-[#5a5ff6] px-5 py-3.5 text-sm font-bold text-white shadow-[0_18px_32px_rgba(47,103,238,0.24)] transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-70"
              :disabled="generating || !selectedProfileId"
              @click="generateReport"
            >
              <span class="material-symbols-outlined">{{ generating ? 'hourglass_top' : 'auto_awesome' }}</span>
              <span>{{ generating ? 'Đang sinh báo cáo...' : careerReportBillingLabel }}</span>
            </button>

          </section>

          <section class="rounded-[28px] border border-slate-200 bg-white/95 p-6 shadow-[0_22px_60px_rgba(148,163,184,0.12)] dark:border-white/10 dark:bg-slate-900/85 dark:shadow-[0_22px_60px_rgba(15,23,42,0.32)]">
            <div class="flex items-center justify-between gap-3 border-b border-slate-200 pb-4 dark:border-white/10">
              <div>
                <h2 class="text-2xl font-bold text-slate-900 dark:text-white">Lịch sử báo cáo</h2>
                <p class="mt-2 text-sm text-slate-600 dark:text-slate-400">{{ pagination.total }} báo cáo đã lưu</p>
              </div>
            </div>

            <div v-if="loadingReports" class="space-y-3 pt-5">
              <div v-for="item in 4" :key="item" class="h-28 animate-pulse rounded-2xl border border-slate-200 bg-slate-100 dark:border-white/10 dark:bg-slate-800/70"></div>
            </div>

            <div v-else-if="!reports.length" class="pt-5 text-sm leading-7 text-slate-600 dark:text-slate-400">
              Chưa có báo cáo nào cho hồ sơ đang chọn. Hãy sinh báo cáo đầu tiên để xem định hướng nghề nghiệp bằng AI.
            </div>

            <div v-else class="space-y-3 pt-5">
              <div
                v-for="report in reports"
                :key="report.id"
                role="button"
                tabindex="0"
                class="w-full rounded-2xl border px-4 py-4 text-left transition"
                :class="Number(selectedReportId) === Number(report.id)
                  ? 'border-blue-400/40 bg-blue-500/10'
                  : 'border-slate-200 bg-slate-50 hover:border-slate-300 dark:border-white/10 dark:bg-slate-950/40 dark:hover:border-white/20'"
                @click="selectedReportId = report.id"
                @keydown.enter.prevent="selectedReportId = report.id"
                @keydown.space.prevent="selectedReportId = report.id"
              >
                <div class="flex items-start justify-between gap-3">
                  <div class="min-w-0 flex-1">
                    <h3 class="break-words text-base font-bold leading-6 text-slate-900 dark:text-white">{{ report.nghe_de_xuat || 'Chưa xác định' }}</h3>
                    <p class="mt-2 break-words text-sm leading-5 text-slate-600 dark:text-slate-400">
                      {{ report.ho_so?.tieu_de_ho_so || `Hồ sơ #${report.ho_so_id}` }}
                    </p>
                  </div>
                  <div class="shrink-0 rounded-full border border-emerald-400/20 bg-emerald-500/10 px-3 py-1 text-sm font-semibold text-emerald-700 dark:text-emerald-200">
                    {{ Math.round(Number(report.muc_do_phu_hop || 0)) }}%
                  </div>
                </div>
                <div class="mt-4 flex flex-wrap items-center justify-between gap-2">
                  <p class="text-xs font-semibold text-slate-500 dark:text-slate-400">{{ formatDate(report.created_at) }}</p>
                  <div class="flex items-center gap-2">
                    <button
                      type="button"
                      class="inline-flex h-8 w-8 items-center justify-center rounded-full bg-rose-50 text-rose-600 transition hover:bg-rose-100 disabled:opacity-60 dark:bg-rose-950/30 dark:text-rose-300 dark:hover:bg-rose-950/50"
                      :disabled="deletingReportId === report.id"
                      title="Xóa report"
                      @click.stop="openDeleteModal(report)"
                    >
                      <span class="material-symbols-outlined text-[18px]">{{ deletingReportId === report.id ? 'hourglass_top' : 'delete' }}</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </aside>

        <section class="rounded-[28px] border border-slate-200 bg-white/95 p-8 shadow-[0_22px_60px_rgba(148,163,184,0.12)] dark:border-white/10 dark:bg-slate-900/85 dark:shadow-[0_22px_60px_rgba(15,23,42,0.32)]">
          <div v-if="selectedReport" class="space-y-6">
            <div class="border-b border-slate-200 pb-5 dark:border-white/10">
              <div>
                <p class="text-xs font-semibold uppercase tracking-[0.35em] text-blue-600/70 dark:text-blue-100/60">Career Insight</p>
                <h2 class="mt-3 text-3xl font-black text-slate-900 dark:text-white">{{ selectedReport.nghe_de_xuat || 'Chưa xác định' }}</h2>
                <p class="mt-3 max-w-2xl text-sm leading-7 text-slate-600 dark:text-slate-400">
                  Báo cáo được sinh cho {{ selectedReport.ho_so?.tieu_de_ho_so || `Hồ sơ #${selectedReport.ho_so_id}` }}
                  vào {{ formatDate(selectedReport.created_at) }}.
                </p>
              </div>
            </div>

            <div class="rounded-[24px] border border-slate-200 bg-slate-50/80 p-7 dark:border-white/10 dark:bg-slate-950/45">
              <h3 class="text-2xl font-bold text-slate-900 dark:text-white">Báo cáo chi tiết</h3>
              <div v-if="formattedReportBody.length" class="mt-5 max-w-5xl space-y-4 text-base leading-8 text-slate-700 dark:text-slate-300">
                <p v-for="(line, index) in formattedReportBody" :key="`${selectedReport.id}-${index}`">{{ line }}</p>
              </div>
              <p v-else class="mt-4 text-sm leading-7 text-slate-600 dark:text-slate-400">Chưa có báo cáo chi tiết để hiển thị.</p>
            </div>
          </div>

          <div v-else class="flex min-h-[520px] flex-col items-center justify-center rounded-[26px] border border-dashed border-slate-300 bg-slate-50/70 px-6 text-center dark:border-white/10 dark:bg-slate-950/35">
            <div class="flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-500/15 text-blue-200">
              <span class="material-symbols-outlined text-3xl">insights</span>
            </div>
            <h3 class="mt-5 text-2xl font-bold text-slate-900 dark:text-white">Chưa có báo cáo để hiển thị</h3>
            <p class="mt-3 max-w-lg text-sm leading-7 text-slate-600 dark:text-slate-400">
              Hãy chọn một hồ sơ ở cột bên trái và sinh `Career Report` đầu tiên để xem gợi ý nghề nghiệp phù hợp với hồ sơ của bạn.
            </p>
          </div>
        </section>
      </div>
    </section>

    <div v-if="showDeleteModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4 dark:bg-black/70">
      <div class="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl dark:bg-slate-900">
        <div class="mb-5 flex items-center gap-3">
          <span class="material-symbols-outlined rounded-xl bg-rose-50 p-2 text-2xl text-rose-600 dark:bg-rose-950/40">warning</span>
          <div>
            <h3 class="text-lg font-bold text-slate-900 dark:text-white">Xóa lịch sử báo cáo</h3>
            <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Thao tác này chỉ xóa bản ghi report trong lịch sử của bạn.</p>
          </div>
        </div>

        <div class="rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm leading-6 text-slate-600 dark:border-slate-700 dark:bg-slate-950/50 dark:text-slate-300">
          Bạn có chắc muốn xóa Career Report
          <span class="font-bold text-slate-900 dark:text-white">"{{ reportToDelete?.nghe_de_xuat || 'chưa xác định' }}"</span>
          được tạo lúc {{ formatDate(reportToDelete?.created_at) }}?
        </div>

        <div class="mt-6 flex gap-3">
          <button
            class="flex-1 rounded-lg border border-slate-300 px-4 py-2 font-semibold text-slate-700 transition-colors hover:bg-slate-50 disabled:opacity-60 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
            :disabled="Boolean(deletingReportId)"
            type="button"
            @click="closeDeleteModal"
          >
            Hủy
          </button>
          <button
            class="flex-1 rounded-lg bg-rose-600 px-4 py-2 font-semibold text-white transition-colors hover:bg-rose-700 disabled:opacity-60"
            :disabled="Boolean(deletingReportId)"
            type="button"
            @click="deleteReport"
          >
            {{ deletingReportId ? 'Đang xóa...' : 'Xóa báo cáo' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
