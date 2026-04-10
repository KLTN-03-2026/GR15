<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { careerReportService, profileService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'

const notify = useNotify()

const loadingProfiles = ref(false)
const loadingReports = ref(false)
const generating = ref(false)
const profiles = ref([])
const reports = ref([])
const selectedProfileId = ref('')
const selectedReportId = ref(null)

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

const summary = computed(() => {
  const total = reports.value.length
  const latest = selectedReport.value || reports.value[0] || null
  const averageFit = total
    ? Math.round(reports.value.reduce((sum, item) => sum + Number(item.muc_do_phu_hop || 0), 0) / total)
    : 0

  return {
    total,
    averageFit,
    latestRole: latest?.nghe_de_xuat || 'Chưa có',
    latestModel: latest?.model_version || 'Nội bộ',
  }
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

const parseSkillSuggestions = (value) => {
  if (!value) return []

  if (Array.isArray(value)) {
    return value.flatMap((item) => {
      if (typeof item === 'string') return item
      return item?.label || item?.name || item?.ten_ky_nang || null
    }).filter(Boolean)
  }

  if (typeof value === 'object') {
    if (Array.isArray(value.items)) return parseSkillSuggestions(value.items)
    if (typeof value.raw_text === 'string') {
      return value.raw_text
        .split(/[\n,;-]+/)
        .map(item => item.trim())
        .filter(Boolean)
    }
  }

  if (typeof value === 'string') {
    return value
      .split(/[\n,;-]+/)
      .map(item => item.trim())
      .filter(Boolean)
  }

  return []
}

const reportSkills = computed(() => parseSkillSuggestions(selectedReport.value?.goi_y_ky_nang_bo_sung))

const formattedReportBody = computed(() => {
  const raw = selectedReport.value?.bao_cao_chi_tiet || ''
  return raw
    .split(/\n+/)
    .map(line => line.trim())
    .filter(Boolean)
})

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

const generateReport = async () => {
  if (!selectedProfileId.value) {
    notify.warning('Bạn cần chọn một hồ sơ trước khi sinh Career Report.')
    return
  }

  generating.value = true
  try {
    await careerReportService.generateReport(selectedProfileId.value)
    notify.success('Đã sinh Career Report mới cho hồ sơ đã chọn.')
    await loadReports(1)
  } catch (error) {
    notify.apiError(error, 'Không thể sinh Career Report.')
  } finally {
    generating.value = false
  }
}

watch(selectedProfileId, async (value) => {
  if (!value) return
  await loadReports(1)
})

onMounted(async () => {
  await loadProfiles()
  if (selectedProfileId.value) {
    await loadReports(1)
  }
})
</script>

<template>
  <div class="min-h-screen text-slate-900 dark:text-white">
    <section class="mx-auto max-w-7xl px-6 py-8">
      <div class="rounded-[30px] border border-blue-200 bg-gradient-to-r from-white via-blue-50 to-[#dce7ff] px-8 py-8 shadow-[0_28px_90px_rgba(148,163,184,0.18)] dark:border-blue-500/20 dark:bg-gradient-to-r dark:from-slate-900 dark:via-[#16264d] dark:to-[#1b49d4] dark:shadow-[0_28px_90px_rgba(14,21,45,0.45)]">
        <div class="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div class="max-w-3xl">
            <p class="text-xs font-semibold uppercase tracking-[0.45em] text-blue-600/80 dark:text-blue-100/70">Career Report</p>
            <h1 class="mt-3 text-4xl font-black tracking-tight text-slate-900 dark:text-white">Báo cáo định hướng nghề nghiệp</h1>
            <p class="mt-3 max-w-2xl text-base leading-7 text-slate-600 dark:text-blue-50/80">
              Sinh báo cáo riêng từ CV của bạn để xem mức độ phù hợp, nghề gợi ý và các kỹ năng nên ưu tiên bồi dưỡng tiếp.
            </p>
          </div>

          <div class="grid min-w-[320px] grid-cols-2 gap-3 sm:grid-cols-4">
            <div class="rounded-2xl border border-blue-200 bg-white/70 px-4 py-4 backdrop-blur dark:border-white/10 dark:bg-white/8">
              <p class="text-xs uppercase tracking-[0.28em] text-blue-600/70 dark:text-blue-100/65">Tổng báo cáo</p>
              <p class="mt-3 text-3xl font-black text-slate-900 dark:text-white">{{ summary.total }}</p>
            </div>
            <div class="rounded-2xl border border-blue-200 bg-white/70 px-4 py-4 backdrop-blur dark:border-white/10 dark:bg-white/8">
              <p class="text-xs uppercase tracking-[0.28em] text-blue-600/70 dark:text-blue-100/65">Phù hợp TB</p>
              <p class="mt-3 text-3xl font-black text-slate-900 dark:text-white">{{ summary.averageFit }}%</p>
            </div>
            <div class="rounded-2xl border border-blue-200 bg-white/70 px-4 py-4 backdrop-blur dark:border-white/10 dark:bg-white/8">
              <p class="text-xs uppercase tracking-[0.28em] text-blue-600/70 dark:text-blue-100/65">Gợi ý gần nhất</p>
              <p class="mt-3 text-lg font-black leading-6 text-slate-900 dark:text-white">{{ summary.latestRole }}</p>
            </div>
            <div class="rounded-2xl border border-blue-200 bg-white/70 px-4 py-4 backdrop-blur dark:border-white/10 dark:bg-white/8">
              <p class="text-xs uppercase tracking-[0.28em] text-blue-600/70 dark:text-blue-100/65">Model</p>
              <p class="mt-3 text-lg font-black leading-6 text-slate-900 dark:text-white">{{ summary.latestModel }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="mt-8 grid gap-6 xl:grid-cols-[360px_minmax(0,1fr)]">
        <aside class="space-y-6">
          <section class="rounded-[28px] border border-slate-200 bg-white/95 p-6 shadow-[0_22px_60px_rgba(148,163,184,0.12)] dark:border-white/10 dark:bg-slate-900/85 dark:shadow-[0_22px_60px_rgba(15,23,42,0.32)]">
            <h2 class="text-2xl font-bold text-slate-900 dark:text-white">Sinh báo cáo mới</h2>
            <p class="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-400">
              Chọn hồ sơ muốn phân tích rồi sinh báo cáo tư vấn nghề nghiệp bằng AI.
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
              <span>{{ generating ? 'Đang sinh báo cáo...' : 'Sinh Career Report mới' }}</span>
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
              <button
                v-for="report in reports"
                :key="report.id"
                type="button"
                class="w-full rounded-2xl border px-4 py-4 text-left transition"
                :class="Number(selectedReportId) === Number(report.id)
                  ? 'border-blue-400/40 bg-blue-500/10'
                  : 'border-slate-200 bg-slate-50 hover:border-slate-300 dark:border-white/10 dark:bg-slate-950/40 dark:hover:border-white/20'"
                @click="selectedReportId = report.id"
              >
                <div class="flex items-start justify-between gap-4">
                  <div>
                    <h3 class="text-lg font-bold text-slate-900 dark:text-white">{{ report.nghe_de_xuat || 'Chưa xác định' }}</h3>
                    <p class="mt-2 text-sm text-slate-600 dark:text-slate-400">
                      {{ report.ho_so?.tieu_de_ho_so || `Hồ sơ #${report.ho_so_id}` }}
                    </p>
                  </div>
                  <div class="rounded-full border border-emerald-400/20 bg-emerald-500/10 px-3 py-1 text-sm font-semibold text-emerald-700 dark:text-emerald-200">
                    {{ Math.round(Number(report.muc_do_phu_hop || 0)) }}%
                  </div>
                </div>
                <p class="mt-3 text-xs uppercase tracking-[0.3em] text-slate-500">{{ formatDate(report.created_at) }}</p>
              </button>
            </div>
          </section>
        </aside>

        <section class="rounded-[28px] border border-slate-200 bg-white/95 p-6 shadow-[0_22px_60px_rgba(148,163,184,0.12)] dark:border-white/10 dark:bg-slate-900/85 dark:shadow-[0_22px_60px_rgba(15,23,42,0.32)]">
          <div v-if="selectedReport" class="space-y-6">
            <div class="flex flex-col gap-4 border-b border-slate-200 pb-5 lg:flex-row lg:items-start lg:justify-between dark:border-white/10">
              <div>
                <p class="text-xs font-semibold uppercase tracking-[0.35em] text-blue-600/70 dark:text-blue-100/60">Career Insight</p>
                <h2 class="mt-3 text-3xl font-black text-slate-900 dark:text-white">{{ selectedReport.nghe_de_xuat || 'Chưa xác định' }}</h2>
                <p class="mt-3 max-w-2xl text-sm leading-7 text-slate-600 dark:text-slate-400">
                  Báo cáo được sinh cho {{ selectedReport.ho_so?.tieu_de_ho_so || `Hồ sơ #${selectedReport.ho_so_id}` }}
                  vào {{ formatDate(selectedReport.created_at) }}.
                </p>
              </div>

              <div class="flex flex-wrap gap-3">
                <div class="rounded-2xl border border-slate-200 bg-slate-50/90 px-4 py-4 text-center dark:border-white/10 dark:bg-slate-950/50">
                  <p class="text-[11px] uppercase tracking-[0.3em] text-slate-500 dark:text-slate-400">Mức độ phù hợp</p>
                  <p class="mt-2 text-3xl font-black text-slate-900 dark:text-white">{{ Math.round(Number(selectedReport.muc_do_phu_hop || 0)) }}%</p>
                </div>
                <div class="rounded-2xl border border-slate-200 bg-slate-50/90 px-4 py-4 text-center dark:border-white/10 dark:bg-slate-950/50">
                  <p class="text-[11px] uppercase tracking-[0.3em] text-slate-500 dark:text-slate-400">Model</p>
                  <p class="mt-2 text-lg font-black text-slate-900 dark:text-white">{{ selectedReport.model_version || 'Nội bộ' }}</p>
                </div>
              </div>
            </div>

            <div class="grid gap-4 lg:grid-cols-[minmax(0,1.2fr)_minmax(320px,0.8fr)]">
              <div class="rounded-[24px] border border-slate-200 bg-slate-50/80 p-5 dark:border-white/10 dark:bg-slate-950/45">
                <h3 class="text-xl font-bold text-slate-900 dark:text-white">Báo cáo chi tiết</h3>
                <div v-if="formattedReportBody.length" class="mt-4 space-y-3 text-sm leading-7 text-slate-700 dark:text-slate-300">
                  <p v-for="(line, index) in formattedReportBody" :key="`${selectedReport.id}-${index}`">{{ line }}</p>
                </div>
                <p v-else class="mt-4 text-sm leading-7 text-slate-600 dark:text-slate-400">Chưa có báo cáo chi tiết để hiển thị.</p>
              </div>

              <div class="space-y-4">
                <div class="rounded-[24px] border border-slate-200 bg-slate-50/80 p-5 dark:border-white/10 dark:bg-slate-950/45">
                  <h3 class="text-xl font-bold text-slate-900 dark:text-white">Kỹ năng nên ưu tiên</h3>
                  <div v-if="reportSkills.length" class="mt-4 flex flex-wrap gap-2">
                    <span
                      v-for="skill in reportSkills"
                      :key="skill"
                      class="rounded-full border border-blue-400/20 bg-blue-500/10 px-3 py-2 text-sm font-semibold text-blue-700 dark:text-blue-100"
                    >
                      {{ skill }}
                    </span>
                  </div>
                  <p v-else class="mt-4 text-sm leading-7 text-slate-600 dark:text-slate-400">Chưa có gợi ý kỹ năng cụ thể trong báo cáo này.</p>
                </div>

                <div class="rounded-[24px] border border-white/10 bg-gradient-to-br from-[#1c56f4] to-[#5a5ff6] p-5 shadow-[0_20px_48px_rgba(41,95,230,0.28)]">
                  <p class="text-xs font-semibold uppercase tracking-[0.3em] text-blue-100/70">Next Step</p>
                  <h3 class="mt-3 text-2xl font-black text-white">Dùng báo cáo này để nâng cấp hồ sơ</h3>
                  <p class="mt-3 text-sm leading-7 text-blue-50/85">
                    Sau khi xem xong, bạn có thể quay lại `Kỹ năng của tôi`, `CV của tôi` hoặc `Mock Interview` để luyện tập đúng hướng AI đang gợi ý.
                  </p>
                </div>
              </div>
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
  </div>
</template>
