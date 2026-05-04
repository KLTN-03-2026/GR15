<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { applicationService, jobService, profileService, savedJobService, walletService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'
import { getAuthToken, getStoredCandidate } from '@/utils/authStorage'
import {
  getBillingFeatureLabel,
  getEntitlementActionLabel,
  getEntitlementCoverageNote,
} from '@/utils/billing'

const route = useRoute()
const router = useRouter()
const notify = useNotify()

const loading = ref(false)
const job = ref(null)
const saving = ref(false)
const isSaved = ref(false)
const applyModalOpen = ref(false)
const applying = ref(false)
const generatingCoverLetter = ref(false)
const loadingProfiles = ref(false)
const loadingBillingContext = ref(false)
const profiles = ref([])
const selectedProfileId = ref('')
const coverLetter = ref('')
const generatedCoverLetterId = ref(null)
const generatedCoverLetter = ref('')
const wallet = ref(null)
const pricing = ref([])
const entitlements = ref([])
const currentSubscription = ref(null)

const hasAuthToken = computed(() => Boolean(getAuthToken()))
const currentUser = computed(() => getStoredCandidate())
const isCandidate = computed(() => hasAuthToken.value && currentUser.value?.vai_tro === 0)
const hasProfiles = computed(() => profiles.value.length > 0)
const selectedProfile = computed(() =>
  profiles.value.find((profile) => Number(profile.id) === Number(selectedProfileId.value)) || null
)

const walletAvailable = computed(() => Number(wallet.value?.so_du_kha_dung || 0))
const coverLetterPrice = computed(() =>
  Number(pricing.value.find((item) => item.feature_code === 'cover_letter_generation')?.don_gia || 0)
)
const coverLetterEntitlement = computed(() =>
  entitlements.value.find((item) => item.feature_code === 'cover_letter_generation') || null
)

const coverLetterBillingLabel = computed(() => {
  return getEntitlementActionLabel(coverLetterEntitlement.value, {
    actionLabel: 'Sinh thư AI',
    price: coverLetterPrice.value,
    formatCurrency,
  })
})

const coverLetterWalletNote = computed(() => {
  return getEntitlementCoverageNote(coverLetterEntitlement.value, {
    currentSubscription: currentSubscription.value,
    featureLabel: getBillingFeatureLabel('cover_letter_generation'),
    price: coverLetterPrice.value,
    formatCurrency,
  })
})

const formatCurrency = (value) => {
  if (value === null || value === undefined || value === '') return 'Thỏa thuận'
  return new Intl.NumberFormat('vi-VN').format(Number(value)) + ' đ'
}

const formatSalary = computed(() => {
  if (!job.value) return 'Thỏa thuận'
  if (job.value.muc_luong_tu && job.value.muc_luong_den) {
    return `${formatCurrency(job.value.muc_luong_tu)} - ${formatCurrency(job.value.muc_luong_den)}`
  }
  if (job.value.muc_luong_tu) return formatCurrency(job.value.muc_luong_tu)
  return 'Thỏa thuận'
})

const acceptedCount = computed(() => Number(job.value?.so_luong_da_nhan || 0))
const remainingSlots = computed(() => Number(job.value?.so_luong_con_lai || 0))
const totalSlots = computed(() => Number(job.value?.so_luong_tuyen || 0))
const isQuotaFull = computed(() => Boolean(job.value?.da_tuyen_du) || (totalSlots.value > 0 && remainingSlots.value <= 0))
const isJobInactive = computed(() => Number(job.value?.trang_thai) !== 1)

const parseDateTime = (value) => {
  if (!value) return null

  const normalized = String(value).includes(' ')
    ? String(value).replace(' ', 'T')
    : String(value)

  const parsed = new Date(normalized)
  return Number.isNaN(parsed.getTime()) ? null : parsed
}

const deadlineText = computed(() => {
  if (!job.value?.ngay_het_han) return 'Không giới hạn'

  const date = parseDateTime(job.value.ngay_het_han)
  if (!date) return 'Không giới hạn'

  return new Intl.DateTimeFormat('vi-VN', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date)
})

const industries = computed(() => job.value?.nganh_nghes || [])

const fetchJob = async () => {
  loading.value = true
  try {
    const response = await jobService.getJobById(route.params.id)
    job.value = response?.data || null
    if (isCandidate.value && job.value?.id) {
      await detectSavedState(job.value.id)
    }
  } catch (error) {
    job.value = null
    notify.apiError(error, 'Không tải được chi tiết tin tuyển dụng.')
  } finally {
    loading.value = false
  }
}

const loadProfiles = async () => {
  if (loadingProfiles.value) return

  loadingProfiles.value = true
  try {
    const response = await profileService.getProfiles({
      per_page: 100,
      sort_by: 'updated_at',
      sort_dir: 'desc',
    })
    const payload = response?.data || {}
    profiles.value = payload.data || []
    if (!selectedProfileId.value && profiles.value.length) {
      selectedProfileId.value = String(profiles.value[0].id)
    }
  } catch (error) {
    profiles.value = []
    selectedProfileId.value = ''
    notify.apiError(error, 'Không tải được danh sách hồ sơ để ứng tuyển.')
  } finally {
    loadingProfiles.value = false
  }
}

const loadBillingContext = async () => {
  loadingBillingContext.value = true
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
    wallet.value = null
    pricing.value = []
    currentSubscription.value = null
    entitlements.value = []
    notify.apiError(error, 'Không tải được dữ liệu ví AI.')
  } finally {
    loadingBillingContext.value = false
  }
}

const openApplyModal = async () => {
  if (!isCandidate.value) {
    notify.warning('Vui lòng đăng nhập bằng tài khoản ứng viên để ứng tuyển.')
    return
  }

  if (isJobInactive.value) {
    notify.warning('Tin tuyển dụng này hiện đã tạm ngưng, bạn không thể ứng tuyển thêm.')
    return
  }

  if (isQuotaFull.value) {
    notify.warning('Tin tuyển dụng này đã đủ chỉ tiêu tuyển dụng.')
    return
  }

  await Promise.all([loadProfiles(), loadBillingContext()])

  if (!profiles.value.length) {
    notify.warning('Bạn cần tạo ít nhất một hồ sơ/CV trước khi ứng tuyển.')
    return
  }

  resetCoverLetterDraft()
  applyModalOpen.value = true
}

const closeApplyModal = () => {
  if (applying.value || generatingCoverLetter.value) return
  applyModalOpen.value = false
}

const redirectToApplications = async () => {
  applyModalOpen.value = false
  resetCoverLetterDraft()
  await router.push({ name: 'Applications' })
}

const handleExistingApplicationError = async (error) => {
  const message = String(error?.message || error?.data?.message || '').toLowerCase()
  if (!message.includes('đã nộp hồ sơ') && !message.includes('da nop ho so')) {
    return false
  }

  notify.info('Bạn đã nộp job này rồi. Hệ thống sẽ chuyển sang Việc đã ứng tuyển để cập nhật CV.')
  await redirectToApplications()
  return true
}

const submitApplication = async () => {
  if (!job.value?.id || !selectedProfileId.value || applying.value) return

  applying.value = true
  try {
    const finalCoverLetter = coverLetter.value.trim() || null

    if (generatedCoverLetterId.value) {
      await applicationService.confirmCoverLetter(generatedCoverLetterId.value, finalCoverLetter)
    } else {
      await applicationService.apply({
        tin_tuyen_dung_id: job.value.id,
        ho_so_id: Number(selectedProfileId.value),
        thu_xin_viec: finalCoverLetter,
      })
    }

    notify.success('Ứng tuyển thành công. Bạn có thể theo dõi tại mục Việc đã ứng tuyển.')
    applyModalOpen.value = false
    resetCoverLetterDraft()
  } catch (error) {
    if (await handleExistingApplicationError(error)) {
      return
    }
    notify.apiError(error, 'Không thể ứng tuyển vào tin này.')
  } finally {
    applying.value = false
  }
}

const resetCoverLetterDraft = () => {
  coverLetter.value = ''
  generatedCoverLetterId.value = null
  generatedCoverLetter.value = ''
}

const generateCoverLetter = async () => {
  if (!job.value?.id || !selectedProfileId.value || generatingCoverLetter.value) return

  generatingCoverLetter.value = true
  try {
    const response = await applicationService.generateCoverLetter({
      tin_tuyen_dung_id: job.value.id,
      ho_so_id: Number(selectedProfileId.value),
    })
    const payload = response?.data || {}
    const draft = payload.thu_xin_viec_ai || ''

    generatedCoverLetterId.value = payload.ung_tuyen_id || null
    generatedCoverLetter.value = draft
    coverLetter.value = draft

    notify.success('Đã sinh thư ứng tuyển bằng AI. Bạn có thể chỉnh sửa trước khi nộp.')
    await loadBillingContext()
  } catch (error) {
    if (await handleExistingApplicationError(error)) {
      return
    }
    if (error?.code === 'WALLET_INSUFFICIENT_BALANCE') {
      notify.warning('Số dư ví không đủ để sinh Cover Letter AI. Hãy nạp thêm tiền rồi thử lại.')
      return
    }
    if (error?.code === 'BILLING_DUPLICATE_REQUEST') {
      notify.info('Yêu cầu sinh thư trước đó vẫn đang xử lý. Vui lòng chờ thêm một chút.')
      return
    }
    notify.apiError(error, 'Không thể sinh thư ứng tuyển AI cho tin này.')
  } finally {
    generatingCoverLetter.value = false
  }
}

const detectSavedState = async (jobId) => {
  try {
    const response = await savedJobService.getSavedJobs({ per_page: 100 })
    const savedJobs = response?.data?.data || []
    isSaved.value = savedJobs.some((item) => Number(item.id) === Number(jobId))
  } catch {
    isSaved.value = false
  }
}

const handleSaveJob = async () => {
  if (!isCandidate.value) {
    notify.warning('Vui lòng đăng nhập bằng tài khoản ứng viên để lưu tin.')
    return
  }

  if (!job.value?.id || saving.value) return

  saving.value = true
  try {
    const response = await savedJobService.toggleSavedJob(job.value.id)
    const savedState = Boolean(response?.data?.trang_thai_luu)
    isSaved.value = savedState
    if (savedState) {
      notify.success('Đã lưu tin tuyển dụng.')
    } else {
      notify.info('Đã bỏ lưu tin tuyển dụng.')
    }
  } catch (error) {
    notify.apiError(error, 'Không thể cập nhật trạng thái lưu tin.')
  } finally {
    saving.value = false
  }
}

onMounted(fetchJob)
watch(() => route.params.id, fetchJob)
watch(selectedProfileId, (nextValue, previousValue) => {
  if (!previousValue || nextValue === previousValue) return

  if (generatedCoverLetterId.value) {
    const shouldClearText = coverLetter.value.trim() === generatedCoverLetter.value.trim()
    generatedCoverLetterId.value = null
    generatedCoverLetter.value = ''

    if (shouldClearText) {
      coverLetter.value = ''
    }
  }
})
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 py-8">
    <div class="mb-6">
      <RouterLink
        :to="{ name: 'JobSearch' }"
        class="inline-flex items-center gap-2 text-sm font-semibold text-slate-600 transition hover:text-blue-600"
      >
        <span class="material-symbols-outlined text-base">arrow_back</span>
        Quay lại danh sách việc làm
      </RouterLink>
    </div>

    <div v-if="loading" class="grid grid-cols-1 gap-8 lg:grid-cols-12">
      <div class="lg:col-span-8 space-y-6">
        <div class="h-80 animate-pulse rounded-[28px] border border-slate-200 bg-white"></div>
        <div class="h-96 animate-pulse rounded-[28px] border border-slate-200 bg-white"></div>
      </div>
      <div class="lg:col-span-4">
        <div class="h-[520px] animate-pulse rounded-[28px] border border-slate-200 bg-white"></div>
      </div>
    </div>

    <div
      v-else-if="!job"
      class="rounded-[28px] border border-dashed border-slate-300 bg-white px-6 py-14 text-center shadow-sm"
    >
      <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-slate-100">
        <span class="material-symbols-outlined text-3xl text-slate-500">description_off</span>
      </div>
      <h1 class="mt-5 text-2xl font-bold text-slate-900">Không tìm thấy tin tuyển dụng</h1>
      <p class="mx-auto mt-3 max-w-xl text-sm leading-7 text-slate-500">
        Tin tuyển dụng có thể đã hết hạn, bị ẩn hoặc không còn khả dụng trong hệ thống.
      </p>
    </div>

    <div v-else class="grid grid-cols-1 gap-8 lg:grid-cols-12">
      <div class="space-y-6 lg:col-span-8">
        <section class="overflow-hidden rounded-[28px] border border-slate-200 bg-white shadow-sm">
          <div class="bg-gradient-to-r from-slate-900 via-blue-900 to-blue-600 px-6 py-8 text-white md:px-8">
            <div class="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
              <div class="max-w-3xl">
                <p class="text-xs font-semibold uppercase tracking-[0.32em] text-blue-100/80">Chi tiết việc làm</p>
                <span
                  v-if="job.is_featured"
                  class="mt-4 inline-flex items-center gap-1.5 rounded-full bg-amber-400/15 px-3 py-1 text-xs font-bold uppercase tracking-[0.18em] text-amber-100"
                >
                  <span class="material-symbols-outlined text-[14px]">rocket_launch</span>
                  Featured Listing
                </span>
                <h1 class="mt-3 text-3xl font-bold md:text-4xl">{{ job.tieu_de }}</h1>
                <p class="mt-4 text-sm font-semibold text-blue-100">
                  {{ job.cong_ty?.ten_cong_ty || 'Công ty đang cập nhật' }}
                </p>
              </div>
              <div class="rounded-2xl border border-white/15 bg-white/10 px-5 py-4 backdrop-blur">
                <p class="text-sm text-blue-100/80">Mức lương</p>
                <p class="mt-2 text-2xl font-bold">{{ formatSalary }}</p>
              </div>
            </div>
          </div>

          <div class="grid gap-4 px-6 py-6 md:grid-cols-4 md:px-8">
            <div class="rounded-2xl bg-slate-50 px-4 py-4">
              <p class="text-xs font-semibold uppercase tracking-wide text-slate-400">Địa điểm</p>
              <p class="mt-2 text-sm font-semibold text-slate-800">{{ job.dia_diem_lam_viec || 'Đang cập nhật' }}</p>
            </div>
            <div class="rounded-2xl bg-slate-50 px-4 py-4">
              <p class="text-xs font-semibold uppercase tracking-wide text-slate-400">Hình thức</p>
              <p class="mt-2 text-sm font-semibold text-slate-800">{{ job.hinh_thuc_lam_viec || 'Đang cập nhật' }}</p>
            </div>
            <div class="rounded-2xl bg-slate-50 px-4 py-4">
              <p class="text-xs font-semibold uppercase tracking-wide text-slate-400">Cấp bậc</p>
              <p class="mt-2 text-sm font-semibold text-slate-800">{{ job.cap_bac || 'Đang cập nhật' }}</p>
            </div>
            <div class="rounded-2xl bg-slate-50 px-4 py-4">
              <p class="text-xs font-semibold uppercase tracking-wide text-slate-400">Hạn nộp</p>
              <p class="mt-2 text-sm font-semibold text-slate-800">{{ deadlineText }}</p>
            </div>
            <div class="rounded-2xl bg-slate-50 px-4 py-4">
              <p class="text-xs font-semibold uppercase tracking-wide text-slate-400">Chỉ tiêu</p>
              <p class="mt-2 text-sm font-semibold text-slate-800">
                {{ acceptedCount }}/{{ totalSlots || '0' }} đã nhận
              </p>
            </div>
            <div
              class="rounded-2xl px-4 py-4"
              :class="isQuotaFull ? 'bg-rose-50' : 'bg-emerald-50'"
            >
              <p
                class="text-xs font-semibold uppercase tracking-wide"
                :class="isQuotaFull ? 'text-rose-400' : 'text-emerald-500'"
              >
                Còn lại
              </p>
              <p
                class="mt-2 text-sm font-semibold"
                :class="isQuotaFull ? 'text-rose-700' : 'text-emerald-700'"
              >
                {{ isQuotaFull ? 'Đã tuyển đủ' : `${remainingSlots} vị trí` }}
              </p>
            </div>
          </div>
        </section>

        <section class="rounded-[28px] border border-slate-200 bg-white px-6 py-6 shadow-sm md:px-8">
          <h2 class="text-2xl font-bold text-slate-900">Mô tả công việc</h2>
          <p class="mt-4 whitespace-pre-line text-sm leading-8 text-slate-600">
            {{ job.mo_ta_cong_viec || 'Nội dung mô tả đang được cập nhật.' }}
          </p>
        </section>

        <section class="rounded-[28px] border border-slate-200 bg-white px-6 py-6 shadow-sm md:px-8">
          <h2 class="text-2xl font-bold text-slate-900">Ngành nghề liên quan</h2>
          <div class="mt-4 flex flex-wrap gap-2">
            <span
              v-for="industry in industries"
              :key="industry.id"
              class="rounded-full bg-blue-50 px-4 py-2 text-sm font-semibold text-blue-700"
            >
              {{ industry.ten_nganh }}
            </span>
            <span
              v-if="!industries.length"
              class="rounded-full bg-slate-100 px-4 py-2 text-sm font-semibold text-slate-600"
            >
              Chưa có dữ liệu ngành nghề
            </span>
          </div>
        </section>

        <section class="rounded-[28px] border border-slate-200 bg-white px-6 py-6 shadow-sm md:px-8">
          <h2 class="text-2xl font-bold text-slate-900">Thông tin công ty</h2>
          <div class="mt-4 grid gap-4 md:grid-cols-2">
            <div class="rounded-2xl bg-slate-50 px-4 py-4">
              <p class="text-xs font-semibold uppercase tracking-wide text-slate-400">Tên công ty</p>
              <p class="mt-2 text-sm font-semibold text-slate-800">{{ job.cong_ty?.ten_cong_ty || 'Đang cập nhật' }}</p>
            </div>
            <div class="rounded-2xl bg-slate-50 px-4 py-4">
              <p class="text-xs font-semibold uppercase tracking-wide text-slate-400">Website</p>
              <p class="mt-2 text-sm font-semibold text-slate-800">{{ job.cong_ty?.website || 'Đang cập nhật' }}</p>
            </div>
            <div class="rounded-2xl bg-slate-50 px-4 py-4">
              <p class="text-xs font-semibold uppercase tracking-wide text-slate-400">Địa chỉ</p>
              <p class="mt-2 text-sm font-semibold text-slate-800">{{ job.cong_ty?.dia_chi || 'Đang cập nhật' }}</p>
            </div>
            <div class="rounded-2xl bg-slate-50 px-4 py-4">
              <p class="text-xs font-semibold uppercase tracking-wide text-slate-400">Quy mô</p>
              <p class="mt-2 text-sm font-semibold text-slate-800">{{ job.cong_ty?.quy_mo || 'Đang cập nhật' }}</p>
            </div>
          </div>
          <p class="mt-4 whitespace-pre-line text-sm leading-7 text-slate-600">
            {{ job.cong_ty?.mo_ta || 'Mô tả công ty đang được cập nhật.' }}
          </p>
        </section>
      </div>

      <aside class="lg:col-span-4">
        <div class="sticky top-6 space-y-5">
          <section class="overflow-hidden rounded-[28px] border border-blue-100 bg-white shadow-lg shadow-blue-100/70">
            <div class="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-6 text-white">
              <p class="text-xs font-semibold uppercase tracking-[0.3em] text-blue-100/80">Ứng tuyển nhanh</p>
              <h2 class="mt-2 text-2xl font-bold">Sẵn sàng cho vị trí này?</h2>
              <p class="mt-3 text-sm leading-7 text-blue-50/85">
                Bạn có thể xem chi tiết, lưu tin hoặc chuẩn bị CV trước khi nối luồng ứng tuyển chính thức.
              </p>
            </div>

            <div class="space-y-4 px-6 py-6">
              <div class="rounded-2xl bg-slate-50 px-4 py-4">
                <p class="text-xs font-semibold uppercase tracking-wide text-slate-400">Yêu cầu kinh nghiệm</p>
                <p class="mt-2 text-sm font-semibold text-slate-800">{{ job.kinh_nghiem_yeu_cau || 'Đang cập nhật' }}</p>
              </div>
              <div class="rounded-2xl bg-slate-50 px-4 py-4">
                <p class="text-xs font-semibold uppercase tracking-wide text-slate-400">Trình độ</p>
                <p class="mt-2 text-sm font-semibold text-slate-800">{{ job.trinh_do_yeu_cau || 'Đang cập nhật' }}</p>
              </div>
              <div class="rounded-2xl bg-slate-50 px-4 py-4">
                <p class="text-xs font-semibold uppercase tracking-wide text-slate-400">Lượt xem</p>
                <p class="mt-2 text-sm font-semibold text-slate-800">{{ job.luot_xem ?? 0 }}</p>
              </div>
              <div
                class="rounded-2xl px-4 py-4"
                :class="isQuotaFull ? 'bg-rose-50' : 'bg-emerald-50'"
              >
                <p
                  class="text-xs font-semibold uppercase tracking-wide"
                  :class="isQuotaFull ? 'text-rose-400' : 'text-emerald-500'"
                >
                  Chỉ tiêu tuyển dụng
                </p>
                <p
                  class="mt-2 text-sm font-semibold"
                  :class="isQuotaFull ? 'text-rose-700' : 'text-emerald-700'"
                >
                  {{ acceptedCount }}/{{ totalSlots || '0' }} đã nhận · {{ isQuotaFull ? 'Đã đủ' : `${remainingSlots} còn lại` }}
                </p>
              </div>

              <div class="grid gap-3">
                <button
                  class="rounded-2xl px-5 py-3 text-sm font-bold text-white transition"
                  :class="isQuotaFull ? 'cursor-not-allowed bg-slate-400' : 'bg-blue-600 hover:bg-blue-700'"
                  :disabled="isQuotaFull"
                  type="button"
                  @click="openApplyModal"
                >
                  {{ isQuotaFull ? 'Đã tuyển đủ chỉ tiêu' : 'Ứng tuyển ngay' }}
                </button>
                <button
                  class="rounded-2xl border px-5 py-3 text-sm font-semibold transition"
                  :class="isSaved
                    ? 'border-blue-200 bg-blue-50 text-blue-700 hover:bg-blue-100'
                    : 'border-slate-200 text-slate-700 hover:bg-slate-50'"
                  type="button"
                  @click="handleSaveJob"
                >
                  {{ saving ? 'Đang xử lý...' : isSaved ? 'Đã lưu tin' : 'Lưu tin tuyển dụng' }}
                </button>
              </div>
            </div>
          </section>
        </div>
      </aside>
    </div>

    <div
      v-if="applyModalOpen"
      class="fixed inset-0 z-50 overflow-y-auto bg-slate-950/55 px-4 py-6 backdrop-blur-sm"
      @click.self="closeApplyModal"
    >
      <div class="mx-auto w-full max-w-4xl rounded-[28px] border border-slate-200 bg-white shadow-2xl">
        <div class="flex items-start justify-between border-b border-slate-100 px-6 py-5">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.28em] text-blue-500">Ứng tuyển</p>
            <h3 class="mt-2 text-2xl font-bold text-slate-900">{{ job?.tieu_de }}</h3>
            <p class="mt-2 text-sm text-slate-500">
              Chọn hồ sơ phù hợp nhất và thêm vài dòng giới thiệu nếu bạn muốn.
            </p>
          </div>
          <button
            class="rounded-full p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700"
            type="button"
            @click="closeApplyModal"
          >
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>

        <div class="max-h-[calc(100vh-12rem)] space-y-5 overflow-y-auto px-6 py-6">
          <div v-if="loadingProfiles" class="rounded-2xl bg-slate-50 px-4 py-5 text-sm text-slate-500">
            Đang tải danh sách hồ sơ...
          </div>

          <template v-else>
            <div>
              <label class="mb-2 block text-sm font-semibold text-slate-700">Chọn hồ sơ ứng tuyển</label>
              <select
                v-model="selectedProfileId"
                class="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
              >
                <option value="" disabled>Chọn hồ sơ của bạn</option>
                <option v-for="profile in profiles" :key="profile.id" :value="String(profile.id)">
                  {{ profile.tieu_de_ho_so || `Hồ sơ #${profile.id}` }}
                </option>
              </select>
            </div>

            <div v-if="selectedProfile" class="rounded-2xl bg-slate-50 px-4 py-4 text-sm text-slate-600">
              <p class="font-semibold text-slate-800">{{ selectedProfile.tieu_de_ho_so || `Hồ sơ #${selectedProfile.id}` }}</p>
              <p class="mt-1">
                Kinh nghiệm: {{ selectedProfile.kinh_nghiem_nam || 0 }} năm
                <span v-if="selectedProfile.vi_tri_mong_muon">• Mục tiêu: {{ selectedProfile.vi_tri_mong_muon }}</span>
              </p>
            </div>

            <div class="rounded-2xl border border-emerald-100 bg-emerald-50/70 px-4 py-4 text-sm text-slate-700">
              <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p class="text-xs font-black uppercase tracking-[0.22em] text-emerald-700">AI Wallet</p>
                  <p class="mt-2 font-semibold text-slate-900">
                    {{ loadingBillingContext ? 'Đang tải số dư ví...' : `Khả dụng ${formatCurrency(walletAvailable)}` }}
                  </p>
                  <p class="mt-1 text-xs text-slate-500">
                    {{ coverLetterWalletNote }}
                  </p>
                </div>
                <RouterLink
                  :to="{ name: 'Wallet' }"
                  class="inline-flex items-center justify-center rounded-xl border border-emerald-200 bg-white px-4 py-2 text-sm font-bold text-emerald-700 transition hover:bg-emerald-50"
                >
                  Nạp ví AI
                </RouterLink>
              </div>
            </div>

            <div>
              <div class="mb-2 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <label class="block text-sm font-semibold text-slate-700">Thư giới thiệu / Cover Letter</label>
                <button
                  class="inline-flex items-center justify-center gap-2 rounded-xl border border-blue-200 bg-blue-50 px-4 py-2 text-sm font-semibold text-blue-700 transition hover:border-blue-300 hover:bg-blue-100 disabled:cursor-not-allowed disabled:opacity-60"
                  :disabled="!selectedProfileId || generatingCoverLetter || applying"
                  type="button"
                  @click="generateCoverLetter"
                >
                  <span class="material-symbols-outlined text-[18px]">auto_awesome</span>
                  {{ generatingCoverLetter ? 'Đang sinh thư AI...' : coverLetterBillingLabel }}
                </button>
              </div>
              <textarea
                v-model="coverLetter"
                rows="10"
                maxlength="5000"
                class="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
                placeholder="Ví dụ: Tôi đã có kinh nghiệm phù hợp với vị trí này và mong muốn được trao đổi thêm về dự án của công ty..."
              />
              <div class="mt-2 flex flex-col gap-2 text-xs text-slate-400 sm:flex-row sm:items-center sm:justify-between">
                <p v-if="generatedCoverLetterId" class="font-medium text-blue-600">
                  Đã có nháp AI. Bạn có thể chỉnh sửa nội dung trước khi nộp hồ sơ.
                </p>
                <p v-else>Thêm vài dòng giới thiệu để nhà tuyển dụng hiểu rõ hơn về bạn.</p>
                <div class="text-right">{{ coverLetter.length }}/5000</div>
              </div>
            </div>
          </template>
        </div>

        <div class="flex flex-col gap-3 border-t border-slate-100 px-6 py-5 sm:flex-row sm:justify-end">
          <RouterLink
            v-if="!hasProfiles"
            :to="{ name: 'MyCv' }"
            class="inline-flex items-center justify-center rounded-2xl border border-slate-200 px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
          >
            Tạo hồ sơ trước
          </RouterLink>
          <button
            class="rounded-2xl border border-slate-200 px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
            type="button"
            @click="closeApplyModal"
          >
            Để sau
          </button>
          <button
            class="rounded-2xl bg-blue-600 px-5 py-3 text-sm font-bold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-300"
            :disabled="!selectedProfileId || applying || loadingProfiles || generatingCoverLetter"
            type="button"
            @click="submitApplication"
          >
            {{ applying ? 'Đang nộp hồ sơ...' : generatedCoverLetterId ? 'Xác nhận thư và ứng tuyển' : 'Xác nhận ứng tuyển' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
