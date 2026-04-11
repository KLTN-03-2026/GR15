<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { applicationService, followCompanyService, matchingService, profileService, savedJobService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'
import { getStoredCandidate } from '@/utils/authStorage'
import { getApplicationStatusLabel } from '@/utils/applicationStatus'

const notify = useNotify()

const loading = ref(false)
const profileCount = ref(0)
const savedCount = ref(0)
const followedCompanyCount = ref(0)
const applicationCount = ref(0)
const matchingAverage = ref(0)
const topMatches = ref([])
const latestApplications = ref([])

const currentUser = computed(() => {
  return getStoredCandidate()
})

const firstName = computed(() => {
  const fullName = currentUser.value?.ho_ten?.trim() || 'bạn'
  const parts = fullName.split(/\s+/)
  return parts[parts.length - 1]
})

const stats = computed(() => [
  {
    label: 'Số hồ sơ hiện có',
    value: profileCount.value,
    icon: 'description',
    tone: 'bg-[#2463eb]/10 text-[#2463eb]',
    helper: profileCount.value > 0 ? 'Sẵn sàng để ứng tuyển' : 'Hãy tạo hồ sơ đầu tiên',
  },
  {
    label: 'Tin đã lưu',
    value: savedCount.value,
    icon: 'bookmark',
    tone: 'bg-amber-100 text-amber-600',
    helper: savedCount.value > 0 ? 'Để dành cho các vị trí tiềm năng' : 'Chưa có tin nào được lưu',
  },
  {
    label: 'Cong ty da follow',
    value: followedCompanyCount.value,
    icon: 'apartment',
    tone: 'bg-sky-100 text-sky-600',
    helper: followedCompanyCount.value > 0 ? 'Theo doi job moi tu doanh nghiep quan tam' : 'Chua follow cong ty nao',
  },
  {
    label: 'Số lần ứng tuyển',
    value: applicationCount.value,
    icon: 'assignment_turned_in',
    tone: 'bg-green-100 text-green-600',
    helper: applicationCount.value > 0 ? 'Theo dõi tại mục Việc đã ứng tuyển' : 'Chưa nộp hồ sơ nào',
  },
  {
    label: 'Matching score TB',
    value: `${matchingAverage.value}%`,
    icon: 'trending_up',
    tone: 'bg-indigo-100 text-indigo-600',
    helper: matchingAverage.value > 0 ? 'Tính từ các job đã được AI gợi ý' : 'Cần tạo matching để có dữ liệu',
  },
])

const recentApplicationsPreview = computed(() => latestApplications.value.slice(0, 3))
const topMatchingPreview = computed(() => topMatches.value.slice(0, 2))
const featuredMatch = computed(() => topMatchingPreview.value[0] || null)
const secondaryMatches = computed(() => topMatchingPreview.value.slice(1))

const scoreTone = (score) => {
  const value = Number(score || 0)
  if (value >= 90) return 'text-[#2463eb] bg-[#2463eb]/10'
  if (value >= 75) return 'text-green-600 bg-green-100'
  return 'text-amber-600 bg-amber-100'
}

const formatCurrency = (value) => {
  if (value === null || value === undefined || value === '') return 'Thỏa thuận'
  return new Intl.NumberFormat('vi-VN').format(Number(value)) + ' đ'
}

const formatSalary = (job) => {
  if (!job) return 'Thỏa thuận'
  if (job.muc_luong_tu && job.muc_luong_den) {
    return `${formatCurrency(job.muc_luong_tu)} - ${formatCurrency(job.muc_luong_den)}`
  }
  if (job.muc_luong) return formatCurrency(job.muc_luong)
  return 'Thỏa thuận'
}

const applicationStatusLabel = getApplicationStatusLabel

const fetchDashboardData = async () => {
  loading.value = true
  try {
    const [profilesRes, savedRes, followedCompaniesRes, applicationsRes, matchesRes] = await Promise.all([
      profileService.getProfiles({ per_page: 100, sort_by: 'updated_at', sort_dir: 'desc' }),
      savedJobService.getSavedJobs({ per_page: 100 }),
      followCompanyService.getFollowedCompanies({ per_page: 100 }),
      applicationService.getApplications({ per_page: 20, page: 1 }),
      matchingService.getMatchingResults({ per_page: 20, page: 1 }),
    ])

    const profilesPayload = profilesRes?.data || {}
    const savedPayload = savedRes?.data || {}
    const followedCompaniesPayload = followedCompaniesRes?.data || {}
    const applicationsPayload = applicationsRes?.data || {}
    const matchesPayload = matchesRes?.data || {}

    profileCount.value = profilesPayload.total || (profilesPayload.data || []).length || 0
    savedCount.value = savedPayload.total || (savedPayload.data || []).length || 0
    followedCompanyCount.value = followedCompaniesPayload.total || (followedCompaniesPayload.data || []).length || 0
    applicationCount.value = applicationsPayload.total || (applicationsPayload.data || []).length || 0

    topMatches.value = matchesPayload.data || []
    latestApplications.value = applicationsPayload.data || []

    const scores = topMatches.value.map((item) => Number(item.diem_phu_hop || 0)).filter((value) => !Number.isNaN(value))
    matchingAverage.value = scores.length ? Math.round(scores.reduce((sum, value) => sum + value, 0) / scores.length) : 0
  } catch (error) {
    notify.apiError(error, 'Không tải được dữ liệu dashboard ứng viên.')
  } finally {
    loading.value = false
  }
}

onMounted(fetchDashboardData)
</script>

<template>
  <div class="space-y-8 text-slate-900 dark:text-slate-100">
    <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.28em] text-blue-600/70 dark:text-blue-300/70">Dashboard ứng viên</p>
        <h1 class="mt-2 text-3xl font-bold text-slate-900 dark:text-white">Chào {{ firstName }}, sẵn sàng cho cơ hội tiếp theo?</h1>
        <p class="mt-2 text-slate-600 dark:text-slate-400">Theo dõi hồ sơ, việc đã lưu, ứng tuyển và gợi ý AI ở một nơi duy nhất.</p>
      </div>
      <RouterLink
        :to="{ name: 'MyCv' }"
        class="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-500 px-5 py-3 font-semibold text-white shadow-lg shadow-blue-500/20 transition-all hover:from-blue-500 hover:to-indigo-400"
      >
        <span class="material-symbols-outlined text-xl">upload_file</span>
        Cập nhật CV
      </RouterLink>
    </div>

    <div class="grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-5">
      <div
        v-for="stat in stats"
        :key="stat.label"
        class="rounded-2xl border border-slate-200 bg-white/90 p-6 shadow-sm shadow-slate-950/5 backdrop-blur dark:border-slate-800 dark:bg-slate-900/80 dark:shadow-black/10"
      >
        <div class="flex justify-between items-start mb-4">
          <div class="rounded-xl p-3" :class="stat.tone">
            <span class="material-symbols-outlined">{{ stat.icon }}</span>
          </div>
        </div>
        <p class="text-sm font-medium text-slate-500 dark:text-slate-400">{{ stat.label }}</p>
        <h3 class="mt-2 text-3xl font-bold text-slate-900 dark:text-white">{{ stat.value }}</h3>
        <p class="mt-3 text-xs leading-6 text-slate-500 dark:text-slate-500">{{ stat.helper }}</p>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-6 xl:grid-cols-[minmax(0,1.7fr)_minmax(340px,0.95fr)]">
      <section class="rounded-2xl border border-slate-200 bg-white/95 p-6 shadow-sm shadow-slate-950/5 space-y-6 dark:border-slate-800 dark:bg-slate-900/85">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-bold flex items-center gap-2 text-slate-900 dark:text-white">
            <span class="material-symbols-outlined text-[#2463eb]">recommend</span>
            Việc làm phù hợp cho bạn
          </h2>
          <RouterLink class="text-[#2463eb] text-sm font-medium hover:underline" :to="{ name: 'MatchedJobs' }">
            Xem tất cả
          </RouterLink>
        </div>

        <div v-if="loading" class="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div
            v-for="index in 2"
            :key="index"
            class="h-72 animate-pulse rounded-2xl bg-slate-200 dark:bg-slate-800"
          />
        </div>

        <div v-else-if="!topMatchingPreview.length" class="rounded-2xl border border-dashed border-slate-300 bg-slate-50/80 p-8 text-center dark:border-slate-700 dark:bg-slate-900/40">
          <div class="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-slate-200 dark:bg-slate-800">
            <span class="material-symbols-outlined text-2xl text-slate-500">auto_awesome</span>
          </div>
          <h3 class="mt-4 text-lg font-bold text-slate-900 dark:text-white">Chưa có gợi ý việc làm</h3>
          <p class="mt-2 text-sm text-slate-600 dark:text-slate-400">
            Hãy vào mục Việc làm phù hợp để hệ thống AI sinh matching từ hồ sơ của bạn.
          </p>
          <RouterLink
            :to="{ name: 'MatchedJobs' }"
            class="mt-5 inline-flex rounded-lg bg-[#2463eb] px-4 py-2 text-sm font-bold text-white hover:bg-[#2463eb]/90"
          >
            Mở trang matching
          </RouterLink>
        </div>

        <div v-else class="space-y-6">
          <div
            v-if="featuredMatch"
            class="group rounded-3xl border border-slate-200 bg-gradient-to-br from-white via-slate-50 to-blue-50 p-7 shadow-lg shadow-slate-950/5 dark:border-slate-800 dark:from-slate-900 dark:via-slate-900 dark:to-slate-950 dark:shadow-black/20"
          >
            <div class="flex items-start gap-4 mb-4">
              <div class="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl border border-slate-200 bg-white/80 dark:border-slate-700 dark:bg-slate-800/80">
                <span class="material-symbols-outlined text-slate-500 dark:text-slate-400 text-2xl">domain</span>
              </div>
              <div class="flex-1">
                <div class="flex flex-wrap items-center justify-between gap-3">
                  <span class="rounded-full px-3 py-1 text-[11px] font-bold uppercase tracking-wide" :class="scoreTone(featuredMatch.diem_phu_hop)">
                    {{ Math.round(Number(featuredMatch.diem_phu_hop || 0)) }}% match
                  </span>
                  <span class="text-xs font-medium text-slate-500 dark:text-slate-500">{{ featuredMatch.ho_so?.tieu_de_ho_so || 'Hồ sơ hiện tại' }}</span>
                </div>
                <h3 class="mt-3 text-3xl font-bold leading-tight text-slate-900 transition-colors group-hover:text-blue-600 dark:text-white dark:group-hover:text-blue-300">
                  {{ featuredMatch.tin_tuyen_dung?.tieu_de || 'Tin tuyển dụng đang cập nhật' }}
                </h3>
                <p class="mt-2 text-sm text-slate-600 dark:text-slate-400">
                  {{ featuredMatch.tin_tuyen_dung?.cong_ty?.ten_cong_ty || 'Công ty đang cập nhật' }}
                  <span v-if="featuredMatch.tin_tuyen_dung?.dia_diem_lam_viec">• {{ featuredMatch.tin_tuyen_dung.dia_diem_lam_viec }}</span>
                </p>
              </div>
            </div>

            <div class="space-y-4">
              <div class="flex items-center justify-between text-sm">
                <span class="font-medium text-slate-500 dark:text-slate-400">Độ phù hợp tổng thể</span>
                <span class="text-xl font-bold text-blue-300">{{ Math.round(Number(featuredMatch.diem_phu_hop || 0)) }}%</span>
              </div>
              <div class="h-2.5 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800">
                <div class="h-full rounded-full bg-gradient-to-r from-blue-500 to-indigo-500" :style="{ width: `${Math.round(Number(featuredMatch.diem_phu_hop || 0))}%` }"></div>
              </div>
              <p v-if="featuredMatch.explanation" class="max-w-3xl text-sm leading-7 text-slate-600 line-clamp-3 dark:text-slate-400">
                {{ featuredMatch.explanation }}
              </p>
              <div class="flex items-center justify-between border-t border-slate-200 pt-5 dark:border-slate-800">
                <p class="text-base font-bold text-slate-900 dark:text-white">{{ formatSalary(featuredMatch.tin_tuyen_dung) }}</p>
                <RouterLink
                  :to="{ name: 'JobDetail', params: { id: featuredMatch.tin_tuyen_dung?.id } }"
                  class="rounded-xl bg-gradient-to-r from-blue-600 to-indigo-500 px-5 py-3 text-sm font-bold text-white shadow-lg shadow-blue-500/20 transition-all hover:from-blue-500 hover:to-indigo-400"
                >
                  Ứng tuyển ngay
                </RouterLink>
              </div>
            </div>
          </div>

          <div v-if="secondaryMatches.length" class="grid grid-cols-1 gap-5 lg:grid-cols-2">
            <div
              v-for="item in secondaryMatches"
              :key="item.id"
              class="group rounded-2xl border border-slate-200 bg-white/90 p-5 shadow-sm shadow-slate-950/5 dark:border-slate-800 dark:bg-slate-900/80"
            >
              <div class="flex items-start justify-between gap-3">
                <div>
                  <span class="rounded-full px-2.5 py-1 text-[10px] font-bold uppercase" :class="scoreTone(item.diem_phu_hop)">
                    {{ Math.round(Number(item.diem_phu_hop || 0)) }}% match
                  </span>
                  <h3 class="mt-3 text-xl font-bold text-slate-900 transition-colors group-hover:text-blue-600 dark:text-white dark:group-hover:text-blue-300">
                    {{ item.tin_tuyen_dung?.tieu_de || 'Tin tuyển dụng đang cập nhật' }}
                  </h3>
                  <p class="mt-2 text-sm text-slate-600 dark:text-slate-400">
                    {{ item.tin_tuyen_dung?.cong_ty?.ten_cong_ty || 'Công ty đang cập nhật' }}
                  </p>
                </div>
                <div class="rounded-xl border border-slate-200 bg-slate-50/90 px-3 py-2 text-right dark:border-slate-700 dark:bg-slate-800/70">
                  <p class="text-[11px] uppercase tracking-wide text-slate-500">Lương</p>
                  <p class="mt-1 text-sm font-bold text-slate-900 dark:text-white">{{ formatSalary(item.tin_tuyen_dung) }}</p>
                </div>
              </div>
              <p v-if="item.explanation" class="mt-4 text-sm leading-7 text-slate-600 line-clamp-2 dark:text-slate-400">
                {{ item.explanation }}
              </p>
              <div class="mt-5 flex items-center justify-between border-t border-slate-200 pt-4 dark:border-slate-800">
                <span class="text-xs text-slate-500 dark:text-slate-500">Xem thêm chi tiết và ứng tuyển từ trang job</span>
                <RouterLink
                  :to="{ name: 'JobDetail', params: { id: item.tin_tuyen_dung?.id } }"
                  class="rounded-lg bg-blue-600/10 px-4 py-2 text-sm font-semibold text-blue-700 transition hover:bg-blue-600 hover:text-white dark:text-blue-300"
                >
                  Xem job
                </RouterLink>
              </div>
            </div>
          </div>
        </div>
      </section>

      <aside>
        <section class="rounded-2xl border border-slate-200 bg-white/95 p-6 shadow-sm shadow-slate-950/5 dark:border-slate-800 dark:bg-slate-900/85">
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-bold flex items-center gap-2 text-slate-900 dark:text-white">
              <span class="material-symbols-outlined text-[#2463eb]">history</span>
              Ứng tuyển gần đây
            </h2>
            <RouterLink class="text-[#2463eb] text-sm font-medium hover:underline" :to="{ name: 'Applications' }">
              Xem tất cả
            </RouterLink>
          </div>

          <div v-if="loading" class="mt-5 space-y-3">
            <div
              v-for="index in 3"
              :key="index"
              class="h-20 animate-pulse rounded-xl bg-slate-200 dark:bg-slate-800"
            />
          </div>

          <div v-else-if="!recentApplicationsPreview.length" class="mt-5 rounded-xl border border-dashed border-slate-300 p-4 text-sm text-slate-600 dark:border-slate-700 dark:text-slate-400">
            Bạn chưa có lượt ứng tuyển nào. Hãy bắt đầu từ một job phù hợp rồi nộp hồ sơ ngay.
          </div>

          <div v-else class="mt-5 space-y-3">
            <div
              v-for="application in recentApplicationsPreview"
              :key="application.id"
              class="rounded-xl border border-slate-200 bg-slate-50/80 p-4 dark:border-slate-800 dark:bg-slate-800/55"
            >
              <p class="font-semibold text-slate-900 dark:text-white">
                {{ application.tin_tuyen_dung?.tieu_de || 'Tin tuyển dụng đang cập nhật' }}
              </p>
              <p class="mt-1 text-sm text-slate-600 dark:text-slate-400">
                {{ application.tin_tuyen_dung?.cong_ty?.ten_cong_ty || 'Công ty đang cập nhật' }}
              </p>
              <div class="mt-3 flex items-center justify-between text-xs">
                <span class="rounded-full bg-blue-500/15 px-2 py-1 font-semibold text-blue-700 dark:text-blue-300">
                  {{ applicationStatusLabel(application.trang_thai) }}
                </span>
                <RouterLink
                  v-if="application.tin_tuyen_dung?.id"
                  :to="{ name: 'JobDetail', params: { id: application.tin_tuyen_dung.id } }"
                  class="font-semibold text-[#2463eb] hover:underline"
                >
                  Xem job
                </RouterLink>
              </div>
            </div>
          </div>
        </section>
      </aside>
    </div>

    <div class="relative overflow-hidden rounded-[28px] bg-gradient-to-br from-blue-600 via-indigo-500 to-violet-500 p-8 text-white shadow-xl shadow-blue-900/20">
      <div class="relative z-10 max-w-3xl">
        <h3 class="text-2xl font-bold mb-2">Tăng tỷ lệ ứng tuyển thành công</h3>
        <p class="mb-6 text-blue-50 opacity-90">
          Hoàn thiện hồ sơ, xem việc làm phù hợp và theo dõi lịch sử ứng tuyển để tối ưu cơ hội của bạn.
        </p>
        <div class="flex flex-wrap gap-3">
          <RouterLink
            :to="{ name: 'MatchedJobs' }"
            class="inline-flex items-center gap-2 rounded-lg bg-white px-5 py-2.5 font-bold text-[#2463eb] shadow-lg transition-colors hover:bg-slate-50"
          >
            <span class="material-symbols-outlined">auto_awesome</span>
            Mở AI matching
          </RouterLink>
          <RouterLink
            :to="{ name: 'MyCv' }"
            class="inline-flex items-center gap-2 rounded-lg border border-white/30 px-5 py-2.5 font-bold text-white transition-colors hover:bg-white/10"
          >
            <span class="material-symbols-outlined">description</span>
            Quản lý CV
          </RouterLink>
        </div>
      </div>
      <div class="absolute right-0 top-0 h-full w-1/3 opacity-20 pointer-events-none">
        <span class="material-symbols-outlined text-[200px] absolute -right-10 -top-10 rotate-12">auto_awesome</span>
      </div>
    </div>
  </div>
</template>
