<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { adminMatchingService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'
import { formatDateTimeVN } from '@/utils/dateTime'

const notify = useNotify()

const loading = ref(false)
const error = ref('')
const records = ref([])
const currentPage = ref(1)
const perPage = ref(10)
const totalRecords = ref(0)

const selectedModel = ref('')
const minScore = ref('')
const maxScore = ref('')

const showDetailModal = ref(false)
const selectedRecord = ref(null)

const modelStats = ref([])

const totalPages = computed(() => Math.max(1, Math.ceil(totalRecords.value / perPage.value)))

const modelOptions = computed(() => {
  const set = new Set(modelStats.value.map((item) => item.model_version).filter(Boolean))
  return Array.from(set)
})

const summaryCards = computed(() => {
  const totalMatches = modelStats.value.reduce((sum, item) => sum + Number(item.total_matches || 0), 0)
  const bestModel = [...modelStats.value].sort((a, b) => Number(b.average_score || 0) - Number(a.average_score || 0))[0]
  const highestScore = Math.max(...modelStats.value.map((item) => Number(item.max_score || 0)), 0)

  return [
    {
      label: 'Lượt matching',
      value: totalMatches,
      description: 'Tổng số lần AI đã so khớp hồ sơ và tin tuyển dụng.',
      icon: 'compare_arrows',
      iconClass: 'bg-[#2463eb]/10 text-[#2463eb]',
    },
    {
      label: 'Model tốt nhất',
      value: bestModel?.model_version || 'Chưa có',
      description: 'Model có điểm trung bình cao nhất hiện tại.',
      icon: 'psychiatry',
      iconClass: 'bg-emerald-500/10 text-emerald-500',
    },
    {
      label: 'Điểm cao nhất',
      value: `${highestScore.toFixed(1)}%`,
      description: 'Match tốt nhất từng được ghi nhận trong hệ thống.',
      icon: 'workspace_premium',
      iconClass: 'bg-amber-500/10 text-amber-500',
    },
    {
      label: 'Model đang dùng',
      value: modelOptions.value.length,
      description: 'Số model/version AI matching hiện có dữ liệu.',
      icon: 'tune',
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

const normalizePayload = (response) => {
  const payload = response?.data || {}
  records.value = payload.data || []
  totalRecords.value = payload.total || 0
}

const loadStats = async () => {
  const response = await adminMatchingService.getStats()
  modelStats.value = response?.data || []
}

const loadMatchings = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await adminMatchingService.getMatchings({
      page: currentPage.value,
      per_page: perPage.value,
      model_version: selectedModel.value || undefined,
      min_score: minScore.value || undefined,
      max_score: maxScore.value || undefined,
    })

    normalizePayload(response)
  } catch (err) {
    error.value = err.message || 'Không thể tải lịch sử AI matching.'
    records.value = []
    totalRecords.value = 0
  } finally {
    loading.value = false
  }
}

const refreshAll = async () => {
  await Promise.all([loadStats(), loadMatchings()])
}

const applyFilters = async () => {
  currentPage.value = 1
  await loadMatchings()
}

const changePage = async (page) => {
  if (page < 1 || page > totalPages.value || page === currentPage.value) return
  currentPage.value = page
  await loadMatchings()
}

const openDetail = (record) => {
  selectedRecord.value = record
  showDetailModal.value = true
}

onMounted(async () => {
  try {
    await refreshAll()
  } catch (err) {
    notify.apiError(err, 'Không thể tải dữ liệu AI matching.')
  }
})
</script>

<template>
  <div v-if="error" class="mb-6 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-900 dark:bg-red-900/20 dark:text-red-300">
    {{ error }}
  </div>

  <div class="mb-8">
    <h1 class="text-3xl font-extrabold tracking-tight">Lịch sử AI Matching</h1>
    <p class="mt-2 max-w-3xl text-base text-slate-500 dark:text-slate-400">
      Theo dõi các lần so khớp hồ sơ và tin tuyển dụng, kiểm tra model đang dùng và đọc giải thích AI chi tiết.
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
    <div class="grid grid-cols-1 gap-4 border-b border-slate-200 px-6 py-5 dark:border-slate-800 xl:grid-cols-[260px_180px_180px_180px_auto]">
      <label class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 dark:border-slate-700 dark:bg-slate-800">
        <span class="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-400">Model</span>
        <select
          v-model="selectedModel"
          class="w-full bg-transparent text-sm text-slate-700 outline-none dark:text-slate-200"
          @change="applyFilters"
        >
          <option value="">Tất cả model</option>
          <option v-for="model in modelOptions" :key="model" :value="model">{{ model }}</option>
        </select>
      </label>

      <label class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 dark:border-slate-700 dark:bg-slate-800">
        <span class="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-400">Điểm từ</span>
        <input
          v-model="minScore"
          type="number"
          min="0"
          max="100"
          class="w-full bg-transparent text-sm text-slate-700 outline-none dark:text-slate-200"
          placeholder="Ví dụ 60"
          @keyup.enter="applyFilters"
        >
      </label>

      <label class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 dark:border-slate-700 dark:bg-slate-800">
        <span class="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-400">Điểm đến</span>
        <input
          v-model="maxScore"
          type="number"
          min="0"
          max="100"
          class="w-full bg-transparent text-sm text-slate-700 outline-none dark:text-slate-200"
          placeholder="Ví dụ 100"
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
          @click="selectedModel = ''; minScore = ''; maxScore = ''; perPage = 10; applyFilters()"
        >
          Reset bộ lọc
        </button>
      </div>
    </div>

    <div v-if="loading" class="space-y-4 px-6 py-6">
      <div v-for="index in 4" :key="index" class="h-28 animate-pulse rounded-2xl bg-slate-100 dark:bg-slate-800" />
    </div>

    <div v-else-if="!records.length" class="px-6 py-16 text-center">
      <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-slate-100 dark:bg-slate-800">
        <span class="material-symbols-outlined text-3xl text-slate-500">psychology_alt</span>
      </div>
      <h2 class="mt-5 text-xl font-bold text-slate-900 dark:text-white">Chưa có lịch sử matching phù hợp</h2>
      <p class="mx-auto mt-3 max-w-xl text-sm leading-7 text-slate-500 dark:text-slate-400">
        Hãy điều chỉnh bộ lọc hoặc chờ thêm lượt matching mới được sinh ra trong hệ thống.
      </p>
    </div>

    <div v-else class="divide-y divide-slate-100 dark:divide-slate-800">
      <div
        v-for="record in records"
        :key="record.id"
        class="grid grid-cols-1 gap-4 px-6 py-5 xl:grid-cols-[minmax(0,1.55fr)_220px_220px_auto]"
      >
        <div class="min-w-0">
          <div class="flex flex-wrap items-center gap-3">
            <h3 class="text-lg font-bold text-slate-900 dark:text-white">
              {{ record.ho_so?.tieu_de_ho_so || `Hồ sơ #${record.ho_so_id}` }}
            </h3>
            <span class="inline-flex items-center rounded-full px-2.5 py-1 text-xs font-bold" :class="scoreColor(record.diem_phu_hop)">
              {{ Number(record.diem_phu_hop || 0).toFixed(1) }}% phù hợp
            </span>
          </div>

          <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">
            {{ record.ho_so?.nguoi_dung?.email || 'Chưa có email' }}
            <span v-if="record.tin_tuyen_dung?.tieu_de">• {{ record.tin_tuyen_dung.tieu_de }}</span>
          </p>

          <p class="mt-3 text-sm leading-7 text-slate-600 dark:text-slate-300">
            {{ record.explanation || 'Chưa có giải thích chi tiết cho lượt matching này.' }}
          </p>
        </div>

        <div class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 dark:border-slate-700 dark:bg-slate-800">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Điểm thành phần</p>
          <div class="mt-3 space-y-2 text-sm text-slate-600 dark:text-slate-300">
            <p>Kỹ năng: <strong class="text-slate-900 dark:text-white">{{ Number(record.diem_ky_nang || 0).toFixed(1) }}</strong></p>
            <p>Kinh nghiệm: <strong class="text-slate-900 dark:text-white">{{ Number(record.diem_kinh_nghiem || 0).toFixed(1) }}</strong></p>
            <p>Học vấn: <strong class="text-slate-900 dark:text-white">{{ Number(record.diem_hoc_van || 0).toFixed(1) }}</strong></p>
          </div>
        </div>

        <div class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 dark:border-slate-700 dark:bg-slate-800">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Model & thời gian</p>
          <div class="mt-3 space-y-2 text-sm text-slate-600 dark:text-slate-300">
            <p class="font-semibold text-slate-900 dark:text-white">{{ record.model_version || 'Chưa rõ' }}</p>
            <p>{{ formatDateTime(record.thoi_gian_match) }}</p>
          </div>
        </div>

        <div class="flex items-center justify-start xl:justify-end">
          <button
            class="inline-flex items-center gap-2 rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
            type="button"
            @click="openDetail(record)"
          >
            <span class="material-symbols-outlined text-[18px]">visibility</span>
            Xem chi tiết
          </button>
        </div>
      </div>
    </div>

    <div
      v-if="!loading && records.length && totalPages > 1"
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
    class="fixed inset-0 z-50 overflow-y-auto bg-slate-950/55 backdrop-blur-sm"
    @click.self="showDetailModal = false"
  >
    <div class="flex min-h-full items-center justify-center px-4 py-6">
      <div class="flex max-h-[calc(100vh-3rem)] w-full max-w-4xl flex-col overflow-hidden rounded-[28px] border border-slate-200 bg-white shadow-2xl dark:border-slate-700 dark:bg-slate-900">
      <div class="flex items-start justify-between border-b border-slate-100 px-6 py-5 dark:border-slate-800">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.28em] text-blue-500">Chi tiết AI matching</p>
          <h3 class="mt-2 text-2xl font-bold text-slate-900 dark:text-white">
            {{ selectedRecord?.ho_so?.tieu_de_ho_so || `Kết quả #${selectedRecord?.id}` }}
          </h3>
          <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">
            {{ selectedRecord?.tin_tuyen_dung?.tieu_de || 'Chưa có tin tuyển dụng' }}
            <span v-if="selectedRecord?.tin_tuyen_dung?.cong_ty?.ten_cong_ty">• {{ selectedRecord.tin_tuyen_dung.cong_ty.ten_cong_ty }}</span>
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

      <div v-if="selectedRecord" class="flex-1 space-y-5 overflow-y-auto px-6 py-6">
        <div class="grid grid-cols-1 gap-4 md:grid-cols-4">
          <div class="rounded-2xl bg-slate-50 px-4 py-4 dark:bg-slate-800">
            <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Điểm tổng</p>
            <p class="mt-2 text-sm font-semibold text-slate-900 dark:text-white">{{ Number(selectedRecord.diem_phu_hop || 0).toFixed(1) }}%</p>
          </div>
          <div class="rounded-2xl bg-slate-50 px-4 py-4 dark:bg-slate-800">
            <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Kỹ năng</p>
            <p class="mt-2 text-sm font-semibold text-slate-900 dark:text-white">{{ Number(selectedRecord.diem_ky_nang || 0).toFixed(1) }}</p>
          </div>
          <div class="rounded-2xl bg-slate-50 px-4 py-4 dark:bg-slate-800">
            <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Kinh nghiệm</p>
            <p class="mt-2 text-sm font-semibold text-slate-900 dark:text-white">{{ Number(selectedRecord.diem_kinh_nghiem || 0).toFixed(1) }}</p>
          </div>
          <div class="rounded-2xl bg-slate-50 px-4 py-4 dark:bg-slate-800">
            <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Học vấn</p>
            <p class="mt-2 text-sm font-semibold text-slate-900 dark:text-white">{{ Number(selectedRecord.diem_hoc_van || 0).toFixed(1) }}</p>
          </div>
        </div>

        <div class="rounded-2xl border border-slate-200 px-5 py-4 dark:border-slate-700">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Giải thích AI</p>
          <p class="mt-3 whitespace-pre-line text-sm leading-7 text-slate-600 dark:text-slate-300">
            {{ selectedRecord.explanation || 'Chưa có giải thích chi tiết.' }}
          </p>
        </div>

        <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div class="rounded-2xl border border-slate-200 px-5 py-4 dark:border-slate-700">
            <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Kỹ năng khớp</p>
            <div class="mt-3 flex flex-wrap gap-2">
              <span
                v-for="skill in selectedRecord.matched_skills_json || []"
                :key="skill"
                class="rounded-full bg-emerald-500/10 px-3 py-1.5 text-xs font-semibold text-emerald-600"
              >
                {{ skill }}
              </span>
              <span v-if="!(selectedRecord.matched_skills_json || []).length" class="text-sm text-slate-400">
                Chưa có kỹ năng khớp được ghi nhận.
              </span>
            </div>
          </div>

          <div class="rounded-2xl border border-slate-200 px-5 py-4 dark:border-slate-700">
            <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Kỹ năng còn thiếu</p>
            <div class="mt-3 flex flex-wrap gap-2">
              <span
                v-for="skill in selectedRecord.missing_skills_json || []"
                :key="skill"
                class="rounded-full bg-rose-500/10 px-3 py-1.5 text-xs font-semibold text-rose-600"
              >
                {{ skill }}
              </span>
              <span v-if="!(selectedRecord.missing_skills_json || []).length" class="text-sm text-slate-400">
                Không có kỹ năng thiếu nổi bật.
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
    </div>
  </div>
</template>
