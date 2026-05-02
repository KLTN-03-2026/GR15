<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { adminAiUsageService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'

const notify = useNotify()

const loading = ref(false)
const logsLoading = ref(false)
const overview = ref(null)
const features = ref([])
const logs = ref([])
const pagination = ref({
  current_page: 1,
  last_page: 1,
  per_page: 20,
  total: 0,
})

const filters = ref({
  days: 30,
  feature: '',
  status: '',
  used_fallback: '',
  from: '',
  to: '',
  request_ref_type: '',
  request_ref_id: '',
  page: 1,
  per_page: 20,
})

const featureLabels = {
  cv_parse: 'Parse CV',
  cv_parse_raw_text: 'Parse CV text',
  jd_parse: 'Parse JD',
  cv_jd_matching: 'Matching CV-JD',
  cover_letter: 'Cover letter',
  career_report: 'Career report',
  cv_tailoring: 'CV Tailoring',
  semantic_job_search: 'Semantic Search',
  career_chat: 'Career Chat',
  career_chat_stream: 'Career Chat Stream',
  mock_interview_question: 'Mock Interview Question',
  mock_interview_answer_evaluation: 'Mock Answer Evaluation',
  mock_interview_report: 'Mock Interview Report',
  interview_copilot_generate: 'Interview Copilot',
  interview_copilot_evaluate: 'Interview Evaluation',
  employer_shortlist_ai_explanation: 'AI Shortlist',
}

const statusMeta = {
  success: {
    label: 'Thành công',
    classes: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-300',
    dot: 'bg-emerald-500',
  },
  error: {
    label: 'Lỗi',
    classes: 'bg-rose-50 text-rose-700 dark:bg-rose-500/10 dark:text-rose-300',
    dot: 'bg-rose-500',
  },
  fallback: {
    label: 'Fallback',
    classes: 'bg-amber-50 text-amber-700 dark:bg-amber-500/10 dark:text-amber-300',
    dot: 'bg-amber-500',
  },
}

const featureLabel = (feature) => featureLabels[feature] || feature || 'Không rõ'
const summary = computed(() => overview.value?.summary || {})
const dailyTrend = computed(() => overview.value?.daily_trend || [])
const featureStats = computed(() => overview.value?.feature_stats || [])
const slowestRequests = computed(() => overview.value?.slowest_requests || [])
const recentIssues = computed(() => overview.value?.recent_issues || [])

const trendMax = computed(() => Math.max(...dailyTrend.value.map((item) => Number(item.total || 0)), 1))
const issueCount = computed(() => Number(summary.value.error_count || 0) + Number(summary.value.fallback_count || 0))

const statCards = computed(() => [
  {
    label: 'Tổng request AI',
    value: formatNumber(summary.value.total_requests || 0),
    helper: `${summary.value.success_rate || 0}% thành công`,
    icon: 'smart_toy',
    tone: 'bg-blue-50 text-blue-700 dark:bg-blue-500/10 dark:text-blue-300',
  },
  {
    label: 'Độ trễ trung bình',
    value: formatDuration(summary.value.avg_duration_ms),
    helper: 'Tính trên request có duration',
    icon: 'speed',
    tone: 'bg-cyan-50 text-cyan-700 dark:bg-cyan-500/10 dark:text-cyan-300',
  },
  {
    label: 'Lỗi AI service',
    value: formatNumber(summary.value.error_count || 0),
    helper: `${summary.value.error_rate || 0}% trong kỳ`,
    icon: 'error',
    tone: 'bg-rose-50 text-rose-700 dark:bg-rose-500/10 dark:text-rose-300',
  },
  {
    label: 'Fallback đã dùng',
    value: formatNumber(summary.value.fallback_count || 0),
    helper: `${summary.value.fallback_rate || 0}% trong kỳ`,
    icon: 'alt_route',
    tone: 'bg-amber-50 text-amber-700 dark:bg-amber-500/10 dark:text-amber-300',
  },
])

function formatNumber(value) {
  return new Intl.NumberFormat('vi-VN').format(Number(value || 0))
}

function formatDuration(value) {
  if (value === null || value === undefined || value === '') return '0 ms'
  const duration = Number(value || 0)
  if (duration >= 1000) return `${(duration / 1000).toFixed(1)}s`
  return `${Math.round(duration)} ms`
}

function formatDateTime(value) {
  if (!value) return 'Chưa có'
  return new Intl.DateTimeFormat('vi-VN', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(new Date(value))
}

function logStatusMeta(log) {
  if (log?.used_fallback) return statusMeta.fallback
  return statusMeta[log?.status] || statusMeta.success
}

function barHeight(item) {
  return `${Math.max(8, Math.round((Number(item.total || 0) / trendMax.value) * 100))}%`
}

function resetFilters() {
  filters.value = {
    days: 30,
    feature: '',
    status: '',
    used_fallback: '',
    from: '',
    to: '',
    request_ref_type: '',
    request_ref_id: '',
    page: 1,
    per_page: 20,
  }
}

async function refreshAll() {
  await Promise.all([fetchOverview(), fetchLogs(1)])
}

async function clearFilters() {
  resetFilters()
  await refreshAll()
}

async function fetchOverview() {
  loading.value = true
  try {
    const response = await adminAiUsageService.getOverview({ days: filters.value.days })
    overview.value = response?.data || null
  } catch (error) {
    notify.apiError(error, 'Không tải được dashboard AI usage.')
  } finally {
    loading.value = false
  }
}

async function fetchFeatures() {
  try {
    const response = await adminAiUsageService.getFeatures()
    features.value = response?.data || []
  } catch (error) {
    notify.apiError(error, 'Không tải được danh sách tính năng AI.')
  }
}

async function fetchLogs(page = filters.value.page) {
  logsLoading.value = true
  filters.value.page = page

  try {
    const response = await adminAiUsageService.getLogs(filters.value)
    const payload = response?.data || {}
    logs.value = payload.data || []
    pagination.value = {
      current_page: payload.current_page || 1,
      last_page: payload.last_page || 1,
      per_page: payload.per_page || filters.value.per_page,
      total: payload.total || 0,
    }
  } catch (error) {
    notify.apiError(error, 'Không tải được lịch sử AI usage.')
  } finally {
    logsLoading.value = false
  }
}

watch(
  () => filters.value.days,
  () => {
    fetchOverview()
  }
)

onMounted(async () => {
  await Promise.all([fetchOverview(), fetchFeatures(), fetchLogs(1)])
})
</script>

<template>
  <div class="space-y-6">
    <section class="flex flex-col gap-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900 xl:flex-row xl:items-end xl:justify-between">
      <div>
        <div class="inline-flex items-center gap-2 rounded-full bg-[#2463eb]/10 px-3 py-1 text-xs font-bold uppercase text-[#2463eb]">
          <span class="material-symbols-outlined text-[16px]">memory</span>
          AI observability
        </div>
        <h2 class="mt-3 text-3xl font-extrabold tracking-tight text-slate-950 dark:text-white">AI Usage Dashboard</h2>
        <p class="mt-1 max-w-3xl text-sm leading-6 text-slate-500 dark:text-slate-400">
          Theo dõi request, lỗi, fallback, độ trễ và tính năng AI đang được dùng trong toàn hệ thống.
        </p>
      </div>

      <div class="flex flex-col gap-3 sm:flex-row sm:items-center">
        <label class="text-sm font-semibold text-slate-600 dark:text-slate-300">
          Khoảng thời gian
          <select v-model="filters.days" class="mt-1 w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm outline-none focus:border-[#2463eb] dark:border-slate-700 dark:bg-slate-950 dark:text-white sm:w-44">
            <option :value="7">7 ngày</option>
            <option :value="30">30 ngày</option>
            <option :value="90">90 ngày</option>
            <option :value="180">180 ngày</option>
          </select>
        </label>
        <button class="inline-flex items-center justify-center gap-2 rounded-xl bg-[#2463eb] px-4 py-3 text-sm font-bold text-white transition hover:bg-blue-700 disabled:opacity-60" type="button" :disabled="loading || logsLoading" @click="refreshAll">
          <span class="material-symbols-outlined text-[18px]" :class="loading || logsLoading ? 'animate-spin' : ''">refresh</span>
          Làm mới
        </button>
      </div>
    </section>

    <div class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
      <article v-for="card in statCards" :key="card.label" class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div class="flex items-start justify-between gap-3">
          <div class="flex size-11 items-center justify-center rounded-xl" :class="card.tone">
            <span class="material-symbols-outlined">{{ card.icon }}</span>
          </div>
          <span v-if="loading" class="rounded-full bg-slate-100 px-2 py-1 text-xs font-bold text-slate-400 dark:bg-slate-800">...</span>
        </div>
        <p class="mt-4 text-sm font-semibold text-slate-500 dark:text-slate-400">{{ card.label }}</p>
        <h3 class="mt-2 text-2xl font-black text-slate-950 dark:text-white">{{ card.value }}</h3>
        <p class="mt-2 text-xs font-medium text-slate-500 dark:text-slate-400">{{ card.helper }}</p>
      </article>
    </div>

    <div class="grid grid-cols-1 gap-6 xl:grid-cols-[minmax(0,1.65fr)_420px]">
      <section class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div class="mb-5 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h3 class="text-lg font-bold text-slate-950 dark:text-white">Xu hướng request</h3>
            <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Tổng request, lỗi và fallback theo ngày.</p>
          </div>
          <span class="inline-flex w-fit items-center gap-2 rounded-full px-3 py-1 text-xs font-bold" :class="issueCount ? 'bg-amber-50 text-amber-700 dark:bg-amber-500/10 dark:text-amber-300' : 'bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-300'">
            <span class="material-symbols-outlined text-[16px]">{{ issueCount ? 'warning' : 'check_circle' }}</span>
            {{ issueCount ? `${formatNumber(issueCount)} issue` : 'Ổn định' }}
          </span>
        </div>

        <div class="flex h-[300px] items-end gap-2 overflow-x-auto pb-2">
          <div v-for="item in dailyTrend" :key="item.date" class="flex h-full min-w-10 flex-1 flex-col items-center justify-end gap-2">
            <div class="flex w-full flex-1 items-end rounded-t-lg bg-slate-100 dark:bg-slate-800">
              <div class="relative w-full rounded-t-lg bg-[#2463eb] transition-all hover:bg-blue-700" :style="{ height: barHeight(item) }">
                <div v-if="item.error_count || item.fallback_count" class="absolute bottom-0 left-0 right-0 rounded-t-lg bg-amber-400" :style="{ height: `${Math.min(100, Math.max(12, ((item.error_count + item.fallback_count) / Math.max(item.total, 1)) * 100))}%` }"></div>
              </div>
            </div>
            <div class="text-center">
              <p class="text-xs font-bold text-slate-900 dark:text-white">{{ item.total }}</p>
              <p class="mt-1 text-[11px] text-slate-500 dark:text-slate-400">{{ item.label }}</p>
            </div>
          </div>
        </div>
      </section>

      <section class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div class="mb-5 flex items-center justify-between gap-3">
          <h3 class="text-lg font-bold text-slate-950 dark:text-white">Top tính năng</h3>
          <span class="text-xs font-bold uppercase text-slate-400">Theo request</span>
        </div>
        <div class="space-y-4">
          <div v-for="feature in featureStats" :key="feature.feature" class="space-y-2">
            <div class="flex items-center justify-between gap-3 text-sm">
              <span class="min-w-0 truncate font-semibold text-slate-800 dark:text-slate-100">{{ featureLabel(feature.feature) }}</span>
              <span class="shrink-0 text-slate-500 dark:text-slate-400">{{ formatNumber(feature.total) }}</span>
            </div>
            <div class="h-2 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
              <div class="h-full rounded-full bg-[#2463eb]" :style="{ width: `${Math.min(100, Math.max(8, feature.success_rate || 0))}%` }"></div>
            </div>
            <div class="flex items-center justify-between text-[11px] font-medium text-slate-500 dark:text-slate-400">
              <span>{{ feature.success_rate }}% success</span>
              <span>{{ formatDuration(feature.avg_duration_ms) }}</span>
            </div>
          </div>
          <p v-if="!featureStats.length && !loading" class="rounded-xl bg-slate-50 p-4 text-sm text-slate-500 dark:bg-slate-950 dark:text-slate-400">Chưa có usage log trong kỳ này.</p>
        </div>
      </section>
    </div>

    <div class="grid grid-cols-1 gap-6 xl:grid-cols-2">
      <section class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div class="mb-5 flex items-center justify-between gap-3">
          <h3 class="text-lg font-bold text-slate-950 dark:text-white">Request chậm nhất</h3>
          <span class="material-symbols-outlined text-slate-400">timer</span>
        </div>
        <div class="space-y-3">
          <div v-for="log in slowestRequests" :key="`slow-${log.id}`" class="flex items-center justify-between gap-4 rounded-xl border border-slate-100 bg-slate-50 px-4 py-3 dark:border-slate-800 dark:bg-slate-950">
            <div class="min-w-0">
              <p class="truncate text-sm font-bold text-slate-900 dark:text-white">{{ featureLabel(log.feature) }}</p>
              <p class="mt-1 truncate text-xs text-slate-500 dark:text-slate-400">{{ log.user?.email || log.company?.ten_cong_ty || log.endpoint || 'System' }}</p>
            </div>
            <span class="shrink-0 rounded-full bg-cyan-50 px-3 py-1 text-xs font-bold text-cyan-700 dark:bg-cyan-500/10 dark:text-cyan-300">{{ formatDuration(log.duration_ms) }}</span>
          </div>
          <p v-if="!slowestRequests.length && !loading" class="text-sm text-slate-500 dark:text-slate-400">Chưa có request có duration để hiển thị.</p>
        </div>
      </section>

      <section class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div class="mb-5 flex items-center justify-between gap-3">
          <h3 class="text-lg font-bold text-slate-950 dark:text-white">Lỗi & fallback gần đây</h3>
          <span class="material-symbols-outlined text-slate-400">running_with_errors</span>
        </div>
        <div class="space-y-3">
          <div v-for="log in recentIssues" :key="`issue-${log.id}`" class="rounded-xl border border-slate-100 bg-slate-50 px-4 py-3 dark:border-slate-800 dark:bg-slate-950">
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0">
                <p class="truncate text-sm font-bold text-slate-900 dark:text-white">{{ featureLabel(log.feature) }}</p>
                <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">{{ formatDateTime(log.created_at) }}</p>
              </div>
              <span class="inline-flex shrink-0 items-center gap-1 rounded-full px-2.5 py-1 text-xs font-bold" :class="logStatusMeta(log).classes">
                <span class="h-1.5 w-1.5 rounded-full" :class="logStatusMeta(log).dot"></span>
                {{ logStatusMeta(log).label }}
              </span>
            </div>
            <p v-if="log.error_message" class="mt-2 line-clamp-2 text-xs leading-5 text-slate-500 dark:text-slate-400">{{ log.error_message }}</p>
          </div>
          <p v-if="!recentIssues.length && !loading" class="text-sm text-slate-500 dark:text-slate-400">Chưa có lỗi hoặc fallback trong kỳ này.</p>
        </div>
      </section>
    </div>

    <section class="rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="border-b border-slate-200 p-5 dark:border-slate-800">
        <div class="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
          <div>
            <h3 class="text-lg font-bold text-slate-950 dark:text-white">Lịch sử AI usage</h3>
            <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">{{ formatNumber(pagination.total) }} log phù hợp bộ lọc.</p>
          </div>
          <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-7">
            <select v-model="filters.feature" class="rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none focus:border-[#2463eb] dark:border-slate-700 dark:bg-slate-950 dark:text-white">
              <option value="">Tất cả tính năng</option>
              <option v-for="feature in features" :key="feature.feature" :value="feature.feature">{{ featureLabel(feature.feature) }}</option>
            </select>
            <select v-model="filters.status" class="rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none focus:border-[#2463eb] dark:border-slate-700 dark:bg-slate-950 dark:text-white">
              <option value="">Tất cả trạng thái</option>
              <option value="success">Thành công</option>
              <option value="error">Lỗi</option>
              <option value="fallback">Fallback</option>
            </select>
            <select v-model="filters.used_fallback" class="rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none focus:border-[#2463eb] dark:border-slate-700 dark:bg-slate-950 dark:text-white">
              <option value="">Fallback?</option>
              <option value="1">Có fallback</option>
              <option value="0">Không fallback</option>
            </select>
            <input v-model="filters.from" type="date" class="rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none focus:border-[#2463eb] dark:border-slate-700 dark:bg-slate-950 dark:text-white" />
            <input v-model="filters.to" type="date" class="rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none focus:border-[#2463eb] dark:border-slate-700 dark:bg-slate-950 dark:text-white" />
            <button class="inline-flex items-center justify-center gap-2 rounded-xl bg-[#2463eb] px-4 py-2.5 text-sm font-bold text-white transition hover:bg-blue-700 disabled:opacity-60" type="button" :disabled="logsLoading" @click="fetchLogs(1)">
              <span class="material-symbols-outlined text-[18px]">filter_alt</span>
              Lọc
            </button>
            <button class="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-bold text-slate-600 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800" type="button" @click="clearFilters">
              <span class="material-symbols-outlined text-[18px]">restart_alt</span>
              Xóa
            </button>
          </div>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-slate-200 text-sm dark:divide-slate-800">
          <thead class="bg-slate-50 text-left text-xs font-bold uppercase text-slate-500 dark:bg-slate-950 dark:text-slate-400">
            <tr>
              <th class="px-5 py-3">Thời gian</th>
              <th class="px-5 py-3">Tính năng</th>
              <th class="px-5 py-3">Trạng thái</th>
              <th class="px-5 py-3">Người dùng</th>
              <th class="px-5 py-3">Công ty</th>
              <th class="px-5 py-3">Model</th>
              <th class="px-5 py-3 text-right">Độ trễ</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 dark:divide-slate-800">
            <tr v-for="log in logs" :key="log.id" class="hover:bg-slate-50 dark:hover:bg-slate-950/70">
              <td class="whitespace-nowrap px-5 py-4 text-slate-600 dark:text-slate-300">{{ formatDateTime(log.created_at) }}</td>
              <td class="px-5 py-4">
                <p class="font-bold text-slate-900 dark:text-white">{{ featureLabel(log.feature) }}</p>
                <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">{{ log.request_ref_type || log.endpoint || 'system' }}<span v-if="log.request_ref_id"> #{{ log.request_ref_id }}</span></p>
              </td>
              <td class="px-5 py-4">
                <span class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-bold" :class="logStatusMeta(log).classes">
                  <span class="h-1.5 w-1.5 rounded-full" :class="logStatusMeta(log).dot"></span>
                  {{ logStatusMeta(log).label }}
                </span>
                <p v-if="log.error_message" class="mt-2 max-w-xs truncate text-xs text-rose-500">{{ log.error_message }}</p>
              </td>
              <td class="px-5 py-4 text-slate-600 dark:text-slate-300">
                <p class="font-semibold">{{ log.user?.ho_ten || 'System' }}</p>
                <p class="mt-1 text-xs text-slate-500">{{ log.user?.email || 'Không có' }}</p>
              </td>
              <td class="px-5 py-4 text-slate-600 dark:text-slate-300">{{ log.company?.ten_cong_ty || 'Không có' }}</td>
              <td class="px-5 py-4">
                <p class="font-semibold text-slate-800 dark:text-slate-100">{{ log.model || log.provider || 'AI service' }}</p>
                <p class="mt-1 max-w-[180px] truncate text-xs text-slate-500 dark:text-slate-400">{{ log.model_version || 'default' }}</p>
              </td>
              <td class="whitespace-nowrap px-5 py-4 text-right font-bold text-slate-900 dark:text-white">{{ formatDuration(log.duration_ms) }}</td>
            </tr>
            <tr v-if="!logs.length && !logsLoading">
              <td colspan="7" class="px-5 py-10 text-center text-sm text-slate-500 dark:text-slate-400">Không có log phù hợp.</td>
            </tr>
            <tr v-if="logsLoading">
              <td colspan="7" class="px-5 py-10 text-center text-sm text-slate-500 dark:text-slate-400">Đang tải log...</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="flex flex-col gap-3 border-t border-slate-200 p-4 dark:border-slate-800 sm:flex-row sm:items-center sm:justify-between">
        <p class="text-sm text-slate-500 dark:text-slate-400">Trang {{ pagination.current_page }} / {{ pagination.last_page }}</p>
        <div class="flex items-center gap-2">
          <button class="inline-flex items-center gap-1 rounded-xl border border-slate-200 px-3 py-2 text-sm font-bold text-slate-600 disabled:opacity-40 dark:border-slate-700 dark:text-slate-300" type="button" :disabled="pagination.current_page <= 1 || logsLoading" @click="fetchLogs(pagination.current_page - 1)">
            <span class="material-symbols-outlined text-[18px]">chevron_left</span>
            Trước
          </button>
          <button class="inline-flex items-center gap-1 rounded-xl border border-slate-200 px-3 py-2 text-sm font-bold text-slate-600 disabled:opacity-40 dark:border-slate-700 dark:text-slate-300" type="button" :disabled="pagination.current_page >= pagination.last_page || logsLoading" @click="fetchLogs(pagination.current_page + 1)">
            Sau
            <span class="material-symbols-outlined text-[18px]">chevron_right</span>
          </button>
        </div>
      </div>
    </section>
  </div>
</template>
