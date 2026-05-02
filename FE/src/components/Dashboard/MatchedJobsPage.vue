<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { jobService, matchingService, profileService, savedJobService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'

const notify = useNotify()

const loading = ref(false)
const refreshing = ref(false)
const loadingProfiles = ref(false)
const togglingSaveId = ref(null)
const profiles = ref([])
const matches = ref([])
const selectedProfileId = ref('')
const sortOption = ref('match_desc')
const savedJobIds = ref(new Set())

const pagination = reactive({
  current_page: 1,
  last_page: 1,
  per_page: 10,
  total: 0,
  from: 0,
  to: 0,
})

const selectedProfile = computed(() =>
  profiles.value.find((profile) => Number(profile.id) === Number(selectedProfileId.value)) || null
)

const sortedMatches = computed(() => {
  const items = [...matches.value]

  switch (sortOption.value) {
    case 'newest':
      return items.sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0))
    case 'salary_desc':
      return items.sort((a, b) => {
        const salaryA = Number(a.tin_tuyen_dung?.muc_luong_tu || 0)
        const salaryB = Number(b.tin_tuyen_dung?.muc_luong_tu || 0)
        return salaryB - salaryA
      })
    case 'match_desc':
    default:
      return items.sort((a, b) => Number(b.diem_phu_hop || 0) - Number(a.diem_phu_hop || 0))
  }
})

const stats = computed(() => {
  const items = matches.value
  const average =
    items.length > 0
      ? Math.round(items.reduce((sum, item) => sum + Number(item.diem_phu_hop || 0), 0) / items.length)
      : 0
  const highMatch = items.filter((item) => Number(item.diem_phu_hop || 0) >= 90).length
  const newJobs = items.filter((item) => {
    if (!item.tin_tuyen_dung?.created_at) return false
    const diff = Date.now() - new Date(item.tin_tuyen_dung.created_at).getTime()
    return diff <= 1000 * 60 * 60 * 24
  }).length

  return {
    average,
    highMatch,
    newJobs,
  }
})

const formatCurrency = (value) => {
  if (value === null || value === undefined || value === '') return 'Thỏa thuận'
  return new Intl.NumberFormat('vi-VN').format(Number(value)) + ' đ'
}

const formatSalary = (job) => {
  if (!job) return 'Thỏa thuận'
  if (job.muc_luong_tu && job.muc_luong_den) {
    return `${formatCurrency(job.muc_luong_tu)} - ${formatCurrency(job.muc_luong_den)}`
  }
  if (job.muc_luong_tu) return formatCurrency(job.muc_luong_tu)
  return 'Thỏa thuận'
}

const formatPostedTime = (job) => {
  if (!job?.created_at) return 'Đăng gần đây'
  const now = Date.now()
  const createdAt = new Date(job.created_at).getTime()
  const diffHours = Math.floor((now - createdAt) / (1000 * 60 * 60))
  if (diffHours < 24) {
    return `Đăng ${diffHours || 1} giờ trước`
  }
  return `Đăng ${Math.floor(diffHours / 24)} ngày trước`
}

const scoreTone = (score) => {
  const value = Number(score || 0)
  if (value >= 90) {
    return {
      label: 'Top Match',
      badgeClass: 'text-[#2463eb] bg-[#2463eb]/10',
      barClass: 'from-[#2463eb] to-indigo-500',
      textClass: 'text-[#2463eb]',
    }
  }
  if (value >= 75) {
    return {
      label: 'Recommended',
      badgeClass: 'text-green-600 bg-green-100 dark:bg-green-900/30',
      barClass: 'from-green-500 to-emerald-500',
      textClass: 'text-green-600',
    }
  }
  return {
    label: 'Good Match',
    badgeClass: 'text-amber-600 bg-amber-100 dark:bg-amber-900/30',
    barClass: 'from-amber-400 to-amber-500',
    textClass: 'text-amber-600',
  }
}

const matchingSummary = (item) => {
  const matched = item.matched_skills_json || []
  const missing = item.missing_skills_json || []
  const tags = []

  matched.slice(0, 3).forEach((skill) => {
    const label = typeof skill === 'string'
      ? skill
      : skill?.skill_name || skill?.ten_ky_nang || skill?.name
    if (label) {
      tags.push({ label: `${label} ✓`, matched: true })
    }
  })

  missing.slice(0, 2).forEach((skill) => {
    const label = typeof skill === 'string'
      ? skill
      : skill?.skill_name || skill?.ten_ky_nang || skill?.name
    if (label) {
      tags.push({ label, matched: false })
    }
  })

  return tags
}

const loadProfiles = async () => {
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
      const preferred = profiles.value.find((item) => Number(item.trang_thai) === 1) || profiles.value[0]
      selectedProfileId.value = String(preferred.id)
    }
  } catch (error) {
    profiles.value = []
    selectedProfileId.value = ''
    notify.apiError(error, 'Không tải được hồ sơ để xem matching.')
  } finally {
    loadingProfiles.value = false
  }
}

const loadSavedJobIds = async () => {
  try {
    const response = await savedJobService.getSavedJobs({ per_page: 100 })
    const savedJobs = response?.data?.data || []
    savedJobIds.value = new Set(savedJobs.map((item) => Number(item.id)))
  } catch {
    savedJobIds.value = new Set()
  }
}

const fetchMatches = async (page = 1) => {
  if (!selectedProfileId.value) {
    matches.value = []
    pagination.current_page = 1
    pagination.last_page = 1
    pagination.total = 0
    pagination.from = 0
    pagination.to = 0
    return
  }

  loading.value = true
  try {
    const response = await matchingService.getMatchingResults({
      page,
      per_page: pagination.per_page,
      ho_so_id: selectedProfileId.value,
    })
    const payload = response?.data || {}
    matches.value = payload.data || []
    pagination.current_page = payload.current_page || 1
    pagination.last_page = payload.last_page || 1
    pagination.total = payload.total || 0
    pagination.from = payload.from || 0
    pagination.to = payload.to || 0
  } catch (error) {
    matches.value = []
    pagination.current_page = 1
    pagination.last_page = 1
    pagination.total = 0
    pagination.from = 0
    pagination.to = 0
    notify.apiError(error, 'Không tải được danh sách việc làm phù hợp.')
  } finally {
    loading.value = false
  }
}

const regenerateMatches = async () => {
  if (!selectedProfileId.value) {
    notify.warning('Bạn cần tạo hoặc chọn một hồ sơ trước khi cập nhật gợi ý.')
    return
  }

  refreshing.value = true
  try {
    const jobsResponse = await jobService.getJobs({ per_page: 8, page: 1 })
    const jobs = jobsResponse?.data?.data || []

    if (!jobs.length) {
      notify.warning('Hiện chưa có tin tuyển dụng hoạt động để tạo matching.')
      return
    }

    await Promise.allSettled(
      jobs.map((job) => matchingService.generateMatching(Number(selectedProfileId.value), job.id))
    )

    await fetchMatches(1)
    notify.success('Đã cập nhật gợi ý việc làm phù hợp theo hồ sơ đang chọn.')
  } catch (error) {
    notify.apiError(error, 'Không thể cập nhật gợi ý việc làm phù hợp.')
  } finally {
    refreshing.value = false
  }
}

const toggleSaved = async (jobId) => {
  if (togglingSaveId.value) return
  togglingSaveId.value = jobId
  try {
    const response = await savedJobService.toggleSavedJob(jobId)
    const savedState = Boolean(response?.data?.trang_thai_luu)
    const next = new Set(savedJobIds.value)
    if (savedState) {
      next.add(Number(jobId))
      notify.success('Đã lưu tin tuyển dụng.')
    } else {
      next.delete(Number(jobId))
      notify.info('Đã bỏ lưu tin tuyển dụng.')
    }
    savedJobIds.value = next
  } catch (error) {
    notify.apiError(error, 'Không thể cập nhật trạng thái lưu tin.')
  } finally {
    togglingSaveId.value = null
  }
}

const changePage = async (page) => {
  if (page < 1 || page > pagination.last_page || page === pagination.current_page) return
  await fetchMatches(page)
}

watch(selectedProfileId, async () => {
  await fetchMatches(1)
})

onMounted(async () => {
  await Promise.all([loadProfiles(), loadSavedJobIds()])
  if (selectedProfileId.value) {
    await fetchMatches()
  }
})
</script>

<template>
  <div>
    <div class="flex justify-between items-end mb-8">
      <div>
        <h1 class="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <span class="material-symbols-outlined text-[#2463eb]">auto_awesome</span>
          Việc làm phù hợp
        </h1>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">AI đã phân tích hồ sơ của bạn và gợi ý các công việc phù hợp nhất.</p>
      </div>
      <div class="flex flex-wrap items-center gap-3">
        <div class="flex items-center gap-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2">
          <span class="material-symbols-outlined text-slate-400 text-[18px]">badge</span>
          <select
            v-model="selectedProfileId"
            class="bg-transparent border-none text-sm font-medium text-slate-700 dark:text-slate-300 focus:ring-0 p-0 pr-6 cursor-pointer"
          >
            <option value="" disabled>{{ loadingProfiles ? 'Đang tải hồ sơ...' : 'Chọn hồ sơ' }}</option>
            <option v-for="profile in profiles" :key="profile.id" :value="String(profile.id)">
              {{ profile.tieu_de_ho_so }}
            </option>
          </select>
        </div>
        <div class="flex items-center gap-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2">
          <span class="material-symbols-outlined text-slate-400 text-[18px]">sort</span>
          <select
            v-model="sortOption"
            class="bg-transparent border-none text-sm font-medium text-slate-700 dark:text-slate-300 focus:ring-0 p-0 pr-6 cursor-pointer"
          >
            <option value="match_desc">Matching cao nhất</option>
            <option value="newest">Mới nhất</option>
            <option value="salary_desc">Lương cao nhất</option>
          </select>
        </div>
      </div>
    </div>

    <div class="bg-gradient-to-r from-[#2463eb]/5 to-indigo-500/5 border border-[#2463eb]/10 rounded-xl p-5 mb-6 flex flex-col md:flex-row items-start md:items-center gap-4 justify-between">
      <div class="flex items-center gap-3">
        <div class="p-2.5 bg-[#2463eb]/10 rounded-xl">
          <span class="material-symbols-outlined text-[#2463eb] text-2xl">psychology</span>
        </div>
        <div>
          <p class="text-sm font-bold text-slate-900 dark:text-white">
            AI đã tìm thấy <span class="text-[#2463eb]">{{ pagination.total }}</span> việc làm phù hợp
            <span v-if="selectedProfile"> cho {{ selectedProfile.tieu_de_ho_so }}</span>
          </p>
          <p class="mt-0.5 text-xs text-slate-500 dark:text-slate-400">
            {{ selectedProfile ? 'Bạn có thể làm mới để sinh lại matching với các tin đang mở.' : 'Hãy chọn một hồ sơ để xem danh sách phù hợp.' }}
          </p>
        </div>
      </div>
      <button
        class="flex items-center gap-2 px-4 py-2 bg-[#2463eb] text-white rounded-lg font-bold text-sm hover:bg-[#2463eb]/90 transition-all shadow-sm disabled:opacity-60"
        :disabled="refreshing || !selectedProfileId"
        type="button"
        @click="regenerateMatches"
      >
        <span class="material-symbols-outlined text-[18px]">{{ refreshing ? 'hourglass_top' : 'refresh' }}</span>
        {{ refreshing ? 'Đang cập nhật...' : 'Cập nhật gợi ý' }}
      </button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
      <div class="bg-white dark:bg-slate-900 p-5 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800">
        <div class="flex items-center justify-between mb-2">
          <p class="text-sm font-medium text-slate-500 dark:text-slate-400">Matching trung bình</p>
          <div class="p-2 bg-[#2463eb]/10 rounded-lg text-[#2463eb]">
            <span class="material-symbols-outlined">trending_up</span>
          </div>
        </div>
        <h3 class="text-2xl font-bold text-[#2463eb]">{{ stats.average }}%</h3>
      </div>
      <div class="bg-white dark:bg-slate-900 p-5 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800">
        <div class="flex items-center justify-between mb-2">
          <p class="text-sm font-medium text-slate-500 dark:text-slate-400">Matching &gt; 90%</p>
          <div class="p-2 bg-green-100 dark:bg-green-900/20 rounded-lg text-green-600">
            <span class="material-symbols-outlined">verified</span>
          </div>
        </div>
        <h3 class="text-2xl font-bold">{{ stats.highMatch }}</h3>
      </div>
      <div class="bg-white dark:bg-slate-900 p-5 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800">
        <div class="flex items-center justify-between mb-2">
          <p class="text-sm font-medium text-slate-500 dark:text-slate-400">Việc mới hôm nay</p>
          <div class="p-2 bg-amber-100 dark:bg-amber-900/20 rounded-lg text-amber-600">
            <span class="material-symbols-outlined">fiber_new</span>
          </div>
        </div>
        <h3 class="text-2xl font-bold">{{ stats.newJobs }}</h3>
      </div>
    </div>

    <div v-if="loading" class="space-y-4">
      <div
        v-for="index in 3"
        :key="index"
        class="h-72 animate-pulse rounded-xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900"
      />
    </div>

    <div v-else-if="!profiles.length" class="rounded-2xl border border-dashed border-slate-300 bg-white px-6 py-14 text-center shadow-sm dark:border-slate-700 dark:bg-slate-900">
      <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-slate-100 dark:bg-slate-800">
        <span class="material-symbols-outlined text-3xl text-slate-500">description</span>
      </div>
      <h2 class="mt-5 text-xl font-bold text-slate-900 dark:text-white">Bạn chưa có hồ sơ nào để matching</h2>
      <p class="mx-auto mt-3 max-w-xl text-sm leading-7 text-slate-500 dark:text-slate-400">
        Hãy tạo hồ sơ trước, sau đó quay lại trang này để hệ thống gợi ý việc làm phù hợp.
      </p>
      <RouterLink
        :to="{ name: 'MyCv' }"
        class="mt-6 inline-flex rounded-xl bg-[#2463eb] px-5 py-3 text-sm font-bold text-white transition hover:bg-blue-700"
      >
        Tạo hồ sơ ngay
      </RouterLink>
    </div>

    <div v-else-if="!sortedMatches.length" class="rounded-2xl border border-dashed border-slate-300 bg-white px-6 py-14 text-center shadow-sm dark:border-slate-700 dark:bg-slate-900">
      <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-slate-100 dark:bg-slate-800">
        <span class="material-symbols-outlined text-3xl text-slate-500">auto_awesome</span>
      </div>
      <h2 class="mt-5 text-xl font-bold text-slate-900 dark:text-white">Chưa có dữ liệu matching cho hồ sơ này</h2>
      <p class="mx-auto mt-3 max-w-xl text-sm leading-7 text-slate-500 dark:text-slate-400">
        Bấm `Cập nhật gợi ý` để hệ thống sinh matching mới dựa trên các tin tuyển dụng đang hoạt động.
      </p>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="item in sortedMatches"
        :key="item.id"
        class="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 hover:border-[#2463eb]/50 transition-all group"
      >
        <div class="flex items-start gap-4 mb-4">
          <div class="size-14 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center shrink-0 border border-slate-100 dark:border-slate-700">
            <span class="material-symbols-outlined text-slate-500 text-2xl">domain</span>
          </div>
          <div class="flex-1">
            <div class="flex justify-between gap-3">
              <div class="flex items-center gap-2 flex-wrap">
                <span class="text-[10px] font-bold px-2 py-0.5 rounded uppercase" :class="scoreTone(item.diem_phu_hop).badgeClass">
                  {{ scoreTone(item.diem_phu_hop).label }}
                </span>
                <span class="rounded bg-slate-100 px-2 py-0.5 text-[10px] font-bold uppercase text-slate-500 dark:bg-slate-800 dark:text-slate-400">
                  {{ item.ho_so?.tieu_de_ho_so || 'Hồ sơ hiện tại' }}
                </span>
              </div>
              <button
                class="text-slate-400 transition-colors hover:text-[#2463eb]"
                type="button"
                @click="toggleSaved(item.tin_tuyen_dung?.id)"
              >
                <span class="material-symbols-outlined">
                  {{ togglingSaveId === item.tin_tuyen_dung?.id
                    ? 'hourglass_top'
                    : savedJobIds.has(Number(item.tin_tuyen_dung?.id)) ? 'bookmark' : 'bookmark_add' }}
                </span>
              </button>
            </div>
            <h3 class="font-bold text-lg group-hover:text-[#2463eb] transition-colors mt-1">
              {{ item.tin_tuyen_dung?.tieu_de || 'Tin tuyển dụng đang cập nhật' }}
            </h3>
            <p class="text-sm text-slate-500 dark:text-slate-400">
              {{ item.tin_tuyen_dung?.cong_ty?.ten_cong_ty || 'Công ty đang cập nhật' }}
              <span v-if="item.tin_tuyen_dung?.dia_diem_lam_viec">• {{ item.tin_tuyen_dung.dia_diem_lam_viec }}</span>
              <span v-if="item.tin_tuyen_dung?.hinh_thuc_lam_viec">• {{ item.tin_tuyen_dung.hinh_thuc_lam_viec }}</span>
            </p>
          </div>
        </div>

        <div class="space-y-3">
          <div class="flex justify-between items-center text-sm mb-1">
            <span class="font-medium text-slate-600 dark:text-slate-400">AI Matching Score</span>
            <span class="font-bold" :class="scoreTone(item.diem_phu_hop).textClass">{{ Math.round(Number(item.diem_phu_hop || 0)) }}%</span>
          </div>
          <div class="w-full h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
            <div
              class="h-full rounded-full transition-all bg-gradient-to-r"
              :class="scoreTone(item.diem_phu_hop).barClass"
              :style="{ width: `${Math.min(100, Math.max(0, Math.round(Number(item.diem_phu_hop || 0))))}%` }"
            />
          </div>

          <div class="flex flex-wrap gap-2 py-2">
            <span
              v-for="tag in matchingSummary(item)"
              :key="tag.label"
              class="text-xs px-2 py-1 rounded font-bold"
              :class="tag.matched
                ? 'bg-[#2463eb]/10 text-[#2463eb]'
                : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300'"
            >
              {{ tag.label }}
            </span>
          </div>

          <p v-if="item.explanation" class="text-sm leading-7 text-slate-500 dark:text-slate-400 line-clamp-2">
            {{ item.explanation }}
          </p>

          <div class="flex items-center justify-between pt-4 border-t border-slate-100 dark:border-slate-800">
            <div class="flex items-center gap-4">
              <p class="text-slate-600 dark:text-slate-400 font-bold text-sm">{{ formatSalary(item.tin_tuyen_dung) }}</p>
              <span class="text-xs text-slate-400 dark:text-slate-500">• {{ formatPostedTime(item.tin_tuyen_dung) }}</span>
            </div>
            <div class="flex items-center gap-2">
              <RouterLink
                :to="{ name: 'JobDetail', params: { id: item.tin_tuyen_dung?.id } }"
                class="px-4 py-2 rounded-lg text-sm font-bold text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              >
                Xem chi tiết
              </RouterLink>
              <RouterLink
                :to="{ name: 'JobDetail', params: { id: item.tin_tuyen_dung?.id } }"
                class="bg-[#2463eb] text-white px-5 py-2 rounded-lg text-sm font-bold hover:bg-[#2463eb]/90 transition-all shadow-md shadow-[#2463eb]/20"
              >
                Ứng tuyển ngay
              </RouterLink>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!loading && sortedMatches.length && pagination.last_page > 1" class="flex justify-center mt-8 gap-2">
      <button
        class="flex items-center gap-2 px-4 py-3 rounded-lg border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 font-bold text-sm transition-colors disabled:opacity-50"
        :disabled="pagination.current_page === 1"
        type="button"
        @click="changePage(pagination.current_page - 1)"
      >
        <span class="material-symbols-outlined text-[18px]">chevron_left</span>
        Trước
      </button>
      <button
        class="flex items-center gap-2 px-4 py-3 rounded-lg border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 font-bold text-sm transition-colors disabled:opacity-50"
        :disabled="pagination.current_page === pagination.last_page"
        type="button"
        @click="changePage(pagination.current_page + 1)"
      >
        Sau
        <span class="material-symbols-outlined text-[18px]">chevron_right</span>
      </button>
    </div>
  </div>
</template>
