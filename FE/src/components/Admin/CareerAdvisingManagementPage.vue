<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { adminCareerAdvisingService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'
import { formatDateTimeVN } from '@/utils/dateTime'

const notify = useNotify()

const loading = ref(false)
const error = ref('')
const reports = ref([])
const stats = ref([])
const selectedCareer = ref('')
const minScore = ref('')
const currentPage = ref(1)
const perPage = ref(10)
const totalReports = ref(0)

const showDetailModal = ref(false)
const selectedReport = ref(null)

const totalPages = computed(() => Math.max(1, Math.ceil(totalReports.value / perPage.value)))

const careerOptions = computed(() => stats.value.map((item) => item.nghe_de_xuat).filter(Boolean))

const summaryCards = computed(() => {
  const total = stats.value.reduce((sum, item) => sum + Number(item.total_suggestions || 0), 0)
  const topCareer = stats.value[0]
  const avgConfidence = stats.value.length
    ? stats.value.reduce((sum, item) => sum + Number(item.average_confidence || 0), 0) / stats.value.length
    : 0

  return [
    {
      label: 'Báo cáo tư vấn',
      value: total,
      description: 'Tổng số báo cáo hướng nghiệp AI đã tạo.',
      icon: 'auto_awesome',
      iconClass: 'bg-[#2463eb]/10 text-[#2463eb]',
    },
    {
      label: 'Nghề nổi bật',
      value: topCareer?.nghe_de_xuat || 'Chưa có',
      description: 'Nghề được AI gợi ý nhiều nhất cho người dùng.',
      icon: 'explore',
      iconClass: 'bg-emerald-500/10 text-emerald-500',
    },
    {
      label: 'Độ phù hợp TB',
      value: `${avgConfidence.toFixed(1)}%`,
      description: 'Mức độ phù hợp trung bình của các báo cáo AI.',
      icon: 'signal_cellular_alt',
      iconClass: 'bg-amber-500/10 text-amber-500',
    },
    {
      label: 'Nhóm nghề AI',
      value: stats.value.length,
      description: 'Số nghề đề xuất đang xuất hiện trong dữ liệu.',
      icon: 'category',
      iconClass: 'bg-rose-500/10 text-rose-500',
    },
  ]
})

const formatDateTime = (value) => {
  return formatDateTimeVN(value, 'Đang cập nhật')
}

const scoreColor = (score) => {
  const numeric = Number(score || 0)
  if (numeric >= 80) return 'text-emerald-500 bg-emerald-500/10'
  if (numeric >= 60) return 'text-amber-500 bg-amber-500/10'
  return 'text-rose-500 bg-rose-500/10'
}

const SKILL_OBJECT_KEYS = ['skill', 'name', 'ky_nang', 'ten_ky_nang']
const NON_SKILL_OBJECT_KEYS = [
  'job_title',
  'title',
  'nghe_de_xuat',
  'career',
  'role',
  'cap_do',
  'job_level',
  'score',
  'matched_skills',
  'missing_skills',
  'matched_keywords',
  'keyword_matches',
]

const NON_SKILL_PATTERNS = [
  /\bdeveloper\b/i,
  /\bengineer\b/i,
  /\bfresher\b/i,
  /\bintern\b/i,
  /\bjunior\b/i,
  /\bsenior\b/i,
  /\blead\b/i,
  /\bmobile developer\b/i,
  /\bbackend developer\b/i,
  /\bfrontend developer\b/i,
  /\bandroid developer\b/i,
  /\bios developer\b/i,
  /lập trình viên/i,
  /phát triển mobile/i,
  /phát triển backend/i,
  /devops và cloud/i,
]

const isLikelySkill = (value) => {
  const text = String(value || '').trim()
  if (!text) return false
  if (text.includes('{') || text.includes('}') || text.includes('[') || text.includes(']')) return false
  if (text.includes('(') || text.includes(')')) return false
  if (NON_SKILL_PATTERNS.some((pattern) => pattern.test(text))) return false
  return true
}

const toReadableValue = (value) => {
  if (value === null || value === undefined || value === '') return null

  if (Array.isArray(value)) {
    return value
      .flatMap((item) => {
        const normalized = toReadableValue(item)
        return Array.isArray(normalized) ? normalized : normalized ? [normalized] : []
      })
      .filter(Boolean)
  }

  if (typeof value === 'object') {
    const preferredSkillValue = SKILL_OBJECT_KEYS.find(
      (key) => typeof value[key] === 'string' && value[key].trim(),
    )

    if (preferredSkillValue) {
      return value[preferredSkillValue].trim()
    }

    return Object.entries(value)
      .filter(([key]) => !NON_SKILL_OBJECT_KEYS.includes(key))
      .flatMap(([, item]) => {
        const normalized = toReadableValue(item)
        return Array.isArray(normalized) ? normalized : normalized ? [normalized] : []
      })
      .filter(Boolean)
  }

  if (typeof value === 'string') {
    const trimmed = value.trim()
    if (!trimmed) return null

    if (
      (trimmed.startsWith('[') && trimmed.endsWith(']')) ||
      (trimmed.startsWith('{') && trimmed.endsWith('}'))
    ) {
      try {
        return toReadableValue(JSON.parse(trimmed))
      } catch {
        return trimmed
      }
    }

    return trimmed
  }

  return String(value)
}

const normalizedSuggestedSkills = computed(() => {
  const raw = selectedReport.value?.goi_y_ky_nang_bo_sung
  const normalized = toReadableValue(raw)
  const list = Array.isArray(normalized) ? normalized : normalized ? [normalized] : []

  return [
    ...new Set(
      list
        .map((item) => String(item).trim())
        .filter(Boolean)
        .filter(isLikelySkill),
    ),
  ]
})

const normalizePayload = (response) => {
  const payload = response?.data || {}
  reports.value = payload.data || []
  totalReports.value = payload.total || 0
}

const loadStats = async () => {
  const response = await adminCareerAdvisingService.getStats()
  stats.value = response?.data || []
}

const loadReports = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await adminCareerAdvisingService.getReports({
      page: currentPage.value,
      per_page: perPage.value,
      nghe_de_xuat: selectedCareer.value || undefined,
      min_score: minScore.value || undefined,
    })

    normalizePayload(response)
  } catch (err) {
    error.value = err.message || 'Không thể tải lịch sử tư vấn nghề nghiệp.'
    reports.value = []
    totalReports.value = 0
  } finally {
    loading.value = false
  }
}

const refreshAll = async () => {
  await Promise.all([loadStats(), loadReports()])
}

const applyFilters = async () => {
  currentPage.value = 1
  await loadReports()
}

const changePage = async (page) => {
  if (page < 1 || page > totalPages.value || page === currentPage.value) return
  currentPage.value = page
  await loadReports()
}

const openDetail = (report) => {
  selectedReport.value = report
  showDetailModal.value = true
}

onMounted(async () => {
  try {
    await refreshAll()
  } catch (err) {
    notify.apiError(err, 'Không thể tải dữ liệu tư vấn nghề nghiệp.')
  }
})
</script>

<template>
  <div v-if="error" class="mb-6 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-900 dark:bg-red-900/20 dark:text-red-300">
    {{ error }}
  </div>

  <div class="mb-8">
    <h1 class="text-3xl font-extrabold tracking-tight">Lịch sử tư vấn nghề nghiệp AI</h1>
    <p class="mt-2 max-w-3xl text-base text-slate-500 dark:text-slate-400">
      Theo dõi các nghề AI đã gợi ý cho người dùng, mức độ phù hợp và nội dung báo cáo chi tiết theo từng hồ sơ.
    </p>
  </div>

  <div class="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-4">
    <div
      v-for="card in summaryCards"
      :key="card.label"
      class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900"
    >
      <div class="mb-2 flex items-center justify-between gap-3">
        <p class="text-sm font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">{{ card.label }}</p>
        <span class="material-symbols-outlined rounded-lg p-2" :class="card.iconClass">{{ card.icon }}</span>
      </div>
      <p class="text-3xl font-bold break-words">{{ card.value }}</p>
      <p class="mt-2 text-xs text-slate-400">{{ card.description }}</p>
    </div>
  </div>

  <div class="rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
    <div class="grid grid-cols-1 gap-4 border-b border-slate-200 px-6 py-5 dark:border-slate-800 xl:grid-cols-[260px_180px_180px_auto]">
      <label class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 dark:border-slate-700 dark:bg-slate-800">
        <span class="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-400">Nghề đề xuất</span>
        <select
          v-model="selectedCareer"
          class="w-full bg-transparent text-sm text-slate-700 outline-none dark:text-slate-200"
          @change="applyFilters"
        >
          <option value="">Tất cả nghề</option>
          <option v-for="career in careerOptions" :key="career" :value="career">{{ career }}</option>
        </select>
      </label>

      <label class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 dark:border-slate-700 dark:bg-slate-800">
        <span class="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-400">Điểm tối thiểu</span>
        <input
          v-model="minScore"
          type="number"
          min="0"
          max="100"
          class="w-full bg-transparent text-sm text-slate-700 outline-none dark:text-slate-200"
          placeholder="Ví dụ 70"
          @keyup.enter="applyFilters"
        >
      </label>

      <label class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 dark:border-slate-700 dark:bg-slate-800">
        <span class="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-400">Số dòng / trang</span>
        <select
          v-model="perPage"
          class="w-full bg-transparent text-sm text-slate-700 outline-none dark:text-slate-200"
          @change="applyFilters"
        >
          <option :value="10">10</option>
          <option :value="15">15</option>
          <option :value="20">20</option>
        </select>
      </label>

      <div class="flex items-end justify-end">
        <button
          class="rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
          type="button"
          @click="selectedCareer = ''; minScore = ''; perPage = 10; applyFilters()"
        >
          Reset bộ lọc
        </button>
      </div>
    </div>

    <div v-if="loading" class="space-y-4 px-6 py-6">
      <div v-for="index in 4" :key="index" class="h-28 animate-pulse rounded-2xl bg-slate-100 dark:bg-slate-800" />
    </div>

    <div v-else-if="!reports.length" class="px-6 py-16 text-center">
      <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-slate-100 dark:bg-slate-800">
        <span class="material-symbols-outlined text-3xl text-slate-500">travel_explore</span>
      </div>
      <h2 class="mt-5 text-xl font-bold text-slate-900 dark:text-white">Chưa có báo cáo tư vấn phù hợp</h2>
      <p class="mx-auto mt-3 max-w-xl text-sm leading-7 text-slate-500 dark:text-slate-400">
        Hãy điều chỉnh bộ lọc hoặc chờ thêm báo cáo tư vấn nghề nghiệp được tạo trong hệ thống.
      </p>
    </div>

    <div v-else class="divide-y divide-slate-100 dark:divide-slate-800">
      <div
        v-for="report in reports"
        :key="report.id"
        class="grid grid-cols-1 gap-4 px-6 py-5 xl:grid-cols-[minmax(0,1.55fr)_220px_220px_auto]"
      >
        <div class="min-w-0">
          <div class="flex flex-wrap items-center gap-3">
            <h3 class="text-lg font-bold text-slate-900 dark:text-white">
              {{ report.nghe_de_xuat || 'Chưa có nghề đề xuất' }}
            </h3>
            <span class="inline-flex items-center rounded-full px-2.5 py-1 text-xs font-bold" :class="scoreColor(report.muc_do_phu_hop)">
              {{ Number(report.muc_do_phu_hop || 0).toFixed(1) }}% phù hợp
            </span>
          </div>

          <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">
            {{ report.nguoi_dung?.ho_ten || 'Người dùng' }}
            <span v-if="report.nguoi_dung?.email">• {{ report.nguoi_dung.email }}</span>
            <span v-if="report.ho_so?.tieu_de_ho_so">• {{ report.ho_so.tieu_de_ho_so }}</span>
          </p>

          <p class="mt-3 line-clamp-3 text-sm leading-7 text-slate-600 dark:text-slate-300">
            {{ report.bao_cao_chi_tiet || 'Chưa có báo cáo chi tiết.' }}
          </p>
        </div>

        <div class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 dark:border-slate-700 dark:bg-slate-800">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Model & hồ sơ</p>
          <div class="mt-3 space-y-2 text-sm text-slate-600 dark:text-slate-300">
            <p class="font-semibold text-slate-900 dark:text-white">{{ report.model_version || 'Chưa rõ model' }}</p>
            <p>{{ report.ho_so?.tieu_de_ho_so || 'Chưa có hồ sơ' }}</p>
          </div>
        </div>

        <div class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 dark:border-slate-700 dark:bg-slate-800">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Thời gian tạo</p>
          <p class="mt-3 text-sm font-semibold text-slate-900 dark:text-white">
            {{ formatDateTime(report.created_at) }}
          </p>
        </div>

        <div class="flex items-center justify-start xl:justify-end">
          <button
            class="inline-flex items-center gap-2 rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
            type="button"
            @click="openDetail(report)"
          >
            <span class="material-symbols-outlined text-[18px]">visibility</span>
            Xem chi tiết
          </button>
        </div>
      </div>
    </div>

    <div
      v-if="!loading && reports.length && totalPages > 1"
      class="flex flex-wrap items-center justify-between gap-3 border-t border-slate-200 px-6 py-4 text-sm dark:border-slate-800"
    >
      <p class="text-slate-500">Trang {{ currentPage }} / {{ totalPages }}</p>
      <div class="flex items-center gap-2">
        <button
          class="rounded-lg border border-slate-200 px-3 py-2 font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
          :disabled="currentPage === 1"
          type="button"
          @click="changePage(currentPage - 1)"
        >
          Trước
        </button>
        <button
          class="rounded-lg border border-slate-200 px-3 py-2 font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
          :disabled="currentPage === totalPages"
          type="button"
          @click="changePage(currentPage + 1)"
        >
          Sau
        </button>
      </div>
    </div>
  </div>

  <div
    v-if="showDetailModal"
    class="fixed inset-0 z-50 overflow-y-auto bg-slate-950/55 px-4 py-6 backdrop-blur-sm"
    @click.self="showDetailModal = false"
  >
    <div class="mx-auto my-4 w-full max-w-4xl overflow-hidden rounded-[28px] border border-slate-200 bg-white shadow-2xl dark:border-slate-700 dark:bg-slate-900">
      <div class="flex items-start justify-between border-b border-slate-100 px-6 py-5 dark:border-slate-800">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.28em] text-blue-500">Chi tiết tư vấn nghề nghiệp</p>
          <h3 class="mt-2 text-2xl font-bold text-slate-900 dark:text-white">{{ selectedReport?.nghe_de_xuat || 'Báo cáo AI' }}</h3>
          <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">
            {{ selectedReport?.nguoi_dung?.ho_ten || 'Người dùng' }}
            <span v-if="selectedReport?.nguoi_dung?.email">• {{ selectedReport.nguoi_dung.email }}</span>
          </p>
        </div>
        <button
          class="rounded-full p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-800"
          type="button"
          @click="showDetailModal = false"
        >
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>

      <div v-if="selectedReport" class="max-h-[calc(100vh-10rem)] space-y-5 overflow-y-auto px-6 py-6">
        <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div class="rounded-2xl bg-slate-50 px-4 py-4 dark:bg-slate-800">
            <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Mức độ phù hợp</p>
            <p class="mt-2 text-sm font-semibold text-slate-900 dark:text-white">{{ Number(selectedReport.muc_do_phu_hop || 0).toFixed(1) }}%</p>
          </div>
          <div class="rounded-2xl bg-slate-50 px-4 py-4 dark:bg-slate-800">
            <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Model</p>
            <p class="mt-2 text-sm font-semibold text-slate-900 dark:text-white">{{ selectedReport.model_version || 'Chưa rõ' }}</p>
          </div>
          <div class="rounded-2xl bg-slate-50 px-4 py-4 dark:bg-slate-800">
            <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Hồ sơ dùng để phân tích</p>
            <p class="mt-2 text-sm font-semibold text-slate-900 dark:text-white">{{ selectedReport.ho_so?.tieu_de_ho_so || 'Chưa có hồ sơ' }}</p>
          </div>
        </div>

        <div class="rounded-2xl border border-slate-200 px-5 py-4 dark:border-slate-700">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Kỹ năng nên bổ sung</p>
          <div class="mt-3 flex flex-wrap gap-2">
            <span
              v-for="skill in normalizedSuggestedSkills"
              :key="skill"
              class="rounded-full bg-amber-500/10 px-3 py-1.5 text-xs font-semibold text-amber-600"
            >
              {{ skill }}
            </span>
            <span v-if="!normalizedSuggestedSkills.length" class="text-sm text-slate-400">
              Chưa có kỹ năng bổ sung nổi bật.
            </span>
          </div>
        </div>

        <div class="rounded-2xl border border-slate-200 px-5 py-4 dark:border-slate-700">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Báo cáo chi tiết</p>
          <p class="mt-3 whitespace-pre-line text-sm leading-7 text-slate-600 dark:text-slate-300">
            {{ selectedReport.bao_cao_chi_tiet || 'Chưa có nội dung báo cáo chi tiết.' }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
