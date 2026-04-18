<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { employerApplicationService, employerJobService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'
import { getApplicationStatusMeta } from '@/utils/applicationStatus'
import { formatDateTimeVN, formatHistoricalDateTimeVN } from '@/utils/dateTime'

const route = useRoute()
const router = useRouter()
const notify = useNotify()

const loading = ref(false)
const parsingLoading = ref(false)
const togglingStatus = ref(false)
const job = ref(null)
const applications = ref([])

const formatDateTime = (value) => formatDateTimeVN(value, 'Chưa cập nhật')
const formatSubmittedDateTime = (value) => formatHistoricalDateTimeVN(value, 'Chưa cập nhật')

const formatSalary = (value) => {
  if (value === null || value === undefined || value === '') return 'Thỏa thuận'
  return `${Number(value).toLocaleString('vi-VN')} đ`
}

const statusLabel = computed(() => (Number(job.value?.trang_thai) === 1 ? 'Đang hoạt động' : 'Tạm ngưng'))
const statusTone = computed(() =>
  Number(job.value?.trang_thai) === 1
    ? 'bg-emerald-500/10 text-emerald-300 border border-emerald-400/20'
    : 'bg-amber-500/10 text-amber-300 border border-amber-400/20'
)

const parseStatusMeta = computed(() => {
  const status = Number(job.value?.parsing?.parse_status || 0)

  if (status === 1) {
    return {
      label: 'Đã parse JD',
      classes: 'bg-violet-500/10 text-violet-300 border border-violet-400/20',
    }
  }

  if (status === 2) {
    return {
      label: 'Parse lỗi',
      classes: 'bg-rose-500/10 text-rose-300 border border-rose-400/20',
    }
  }

  return {
    label: 'Chưa parse JD',
    classes: 'bg-slate-500/10 text-slate-300 border border-slate-400/20',
  }
})

const statusCards = computed(() => {
  const currentJob = job.value
  if (!currentJob) return []

  return [
    {
      label: 'Tổng hồ sơ',
      value: currentJob.tong_ho_so || 0,
      hint: 'Đã nộp vào tin này',
      icon: 'groups',
      tone: 'text-blue-300 bg-blue-500/10',
    },
    {
      label: 'Trúng tuyển',
      value: currentJob.so_luong_da_nhan || 0,
      hint: `${currentJob.so_luong_con_lai || 0} chỉ tiêu còn lại`,
      icon: 'task_alt',
      tone: 'text-emerald-300 bg-emerald-500/10',
    },
    {
      label: 'Đang chờ',
      value: currentJob.ho_so_dang_cho || 0,
      hint: 'Nên xử lý sớm',
      icon: 'hourglass_top',
      tone: 'text-amber-300 bg-amber-500/10',
    },
    {
      label: 'Đã xem',
      value: currentJob.ho_so_da_xem || 0,
      hint: `${currentJob.ho_so_tu_choi || 0} hồ sơ đã từ chối`,
      icon: 'visibility',
      tone: 'text-sky-300 bg-sky-500/10',
    },
  ]
})

const applicationStatusMeta = getApplicationStatusMeta

const requiredSkills = computed(() => {
  const manualSkills = (job.value?.ky_nang_yeu_caus || [])
    .map((item) => item?.ky_nang?.ten_ky_nang)
    .filter(Boolean)

  const parsedSkills = (job.value?.parsing?.parsed_skills_json || [])
    .map((item) => item?.skill_name || item?.ten_ky_nang || item?.name)
    .filter(Boolean)

  return [...new Set([...manualSkills, ...parsedSkills])]
})

const parsedRequirements = computed(() =>
  (job.value?.parsing?.parsed_requirements_json || [])
    .map((item) => {
      if (typeof item === 'string') return item
      return item?.requirement || item?.text || item?.value || item?.name || null
    })
    .filter(Boolean)
)

const parsedBenefits = computed(() =>
  (job.value?.parsing?.parsed_benefits_json || [])
    .map((item) => {
      if (typeof item === 'string') return item
      return item?.benefit || item?.text || item?.value || item?.name || null
    })
    .filter(Boolean)
)

const upcomingApplications = computed(() => applications.value.slice(0, 6))

const fetchJobDetail = async () => {
  loading.value = true
  try {
    const [jobResponse, applicationResponse] = await Promise.all([
      employerJobService.getJobById(route.params.id),
      employerApplicationService.getApplications({
        tin_tuyen_dung_id: route.params.id,
        per_page: 50,
      }),
    ])

    job.value = jobResponse?.data || null
    applications.value = applicationResponse?.data?.data || []
  } catch (error) {
    notify.apiError(error, 'Không tải được chi tiết tin tuyển dụng.')
    await router.push('/employer/jobs')
  } finally {
    loading.value = false
  }
}

const parseJob = async () => {
  if (!job.value) return

  parsingLoading.value = true
  try {
    await employerJobService.parseJob(job.value.id)
    notify.success('Đã gửi yêu cầu parse JD cho tin tuyển dụng.')
    await fetchJobDetail()
  } catch (error) {
    notify.apiError(error, 'Không thể parse JD cho tin tuyển dụng.')
  } finally {
    parsingLoading.value = false
  }
}

const toggleStatus = async () => {
  if (!job.value) return

  togglingStatus.value = true
  try {
    await employerJobService.toggleStatus(job.value.id)
    notify.success(`Đã chuyển trạng thái sang ${Number(job.value.trang_thai) === 1 ? 'tạm ngưng' : 'đang hoạt động'}.`)
    await fetchJobDetail()
  } catch (error) {
    notify.apiError(error, 'Không thể chuyển trạng thái tin tuyển dụng.')
  } finally {
    togglingStatus.value = false
  }
}

onMounted(fetchJobDetail)
</script>

<template>
  <div class="mx-auto max-w-7xl">
    <div v-if="loading" class="grid grid-cols-1 gap-5 lg:grid-cols-4">
      <div v-for="index in 8" :key="index" class="h-36 animate-pulse rounded-2xl bg-slate-200/60 dark:bg-slate-800/70" />
    </div>

    <template v-else-if="job">
      <div class="mb-8 rounded-3xl border border-slate-800 bg-gradient-to-r from-slate-900 via-slate-900 to-[#1e46a7] p-6 text-white shadow-[0_24px_70px_rgba(14,22,42,0.35)]">
        <div class="flex flex-col gap-6 xl:flex-row xl:items-start xl:justify-between">
          <div class="max-w-4xl">
            <div class="mb-3 flex flex-wrap items-center gap-3">
              <RouterLink to="/employer/jobs" class="inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1.5 text-xs font-bold text-white/90 transition hover:bg-white/15">
                <span class="material-symbols-outlined text-[16px]">arrow_back</span>
                Quay lại danh sách
              </RouterLink>
              <span class="inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-xs font-bold" :class="statusTone">
                <span class="h-2 w-2 rounded-full" :class="Number(job.trang_thai) === 1 ? 'bg-emerald-400' : 'bg-amber-400'" />
                {{ statusLabel }}
              </span>
              <span class="inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-xs font-bold" :class="parseStatusMeta.classes">
                {{ parseStatusMeta.label }}
              </span>
            </div>

            <h1 class="text-3xl font-black tracking-tight sm:text-4xl">{{ job.tieu_de }}</h1>
            <p class="mt-3 text-sm leading-7 text-blue-100/80 sm:text-base">
              {{ job.mo_ta_cong_viec }}
            </p>

            <div class="mt-5 flex flex-wrap gap-3 text-sm text-blue-100/85">
              <span class="inline-flex items-center gap-2 rounded-2xl bg-white/8 px-4 py-2 backdrop-blur">
                <span class="material-symbols-outlined text-[18px]">pin_drop</span>
                {{ job.dia_diem_lam_viec || 'Chưa cập nhật địa điểm' }}
              </span>
              <span class="inline-flex items-center gap-2 rounded-2xl bg-white/8 px-4 py-2 backdrop-blur">
                <span class="material-symbols-outlined text-[18px]">work_history</span>
                {{ job.hinh_thuc_lam_viec || 'Chưa cập nhật hình thức' }}
              </span>
              <span class="inline-flex items-center gap-2 rounded-2xl bg-white/8 px-4 py-2 backdrop-blur">
                <span class="material-symbols-outlined text-[18px]">payments</span>
                {{ formatSalary(job.muc_luong) }}
              </span>
              <span class="inline-flex items-center gap-2 rounded-2xl bg-white/8 px-4 py-2 backdrop-blur">
                <span class="material-symbols-outlined text-[18px]">event</span>
                Hết hạn: {{ formatDateTime(job.ngay_het_han) }}
              </span>
            </div>
          </div>

          <div class="flex flex-wrap gap-3 xl:justify-end">
            <button
              class="inline-flex items-center gap-2 rounded-2xl border border-white/15 bg-white/10 px-4 py-3 text-sm font-semibold text-white transition hover:bg-white/15 disabled:opacity-60"
              :disabled="parsingLoading"
              type="button"
              @click="parseJob"
            >
              <span class="material-symbols-outlined text-[18px]" :class="parsingLoading ? 'animate-spin' : ''">
                {{ parsingLoading ? 'progress_activity' : 'auto_awesome' }}
              </span>
              {{ parsingLoading ? 'Đang parse...' : 'Parse JD' }}
            </button>
            <button
              class="inline-flex items-center gap-2 rounded-2xl bg-white px-4 py-3 text-sm font-bold text-[#1f49b6] shadow-lg shadow-black/10 transition hover:-translate-y-0.5 disabled:opacity-60"
              :disabled="togglingStatus"
              type="button"
              @click="toggleStatus"
            >
              <span class="material-symbols-outlined text-[18px]">
                {{ Number(job.trang_thai) === 1 ? 'pause_circle' : 'play_circle' }}
              </span>
              {{ Number(job.trang_thai) === 1 ? 'Tạm ngưng tin' : 'Kích hoạt lại tin' }}
            </button>
          </div>
        </div>
      </div>

      <div class="mb-6 grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-4">
        <div
          v-for="card in statusCards"
          :key="card.label"
          class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm shadow-slate-950/5 dark:border-slate-800 dark:bg-slate-900"
        >
          <div class="flex items-start justify-between gap-3">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">{{ card.label }}</p>
              <p class="mt-3 text-3xl font-black text-slate-900 dark:text-white">{{ card.value }}</p>
            </div>
            <span class="material-symbols-outlined rounded-2xl p-3 text-[22px]" :class="card.tone">{{ card.icon }}</span>
          </div>
          <p class="mt-4 text-sm leading-6 text-slate-500 dark:text-slate-400">{{ card.hint }}</p>
        </div>
      </div>

      <div class="grid grid-cols-1 gap-6 xl:grid-cols-[minmax(0,1.45fr)_360px]">
        <div class="space-y-6">
          <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm shadow-slate-950/5 dark:border-slate-800 dark:bg-slate-900">
            <div class="flex items-center justify-between gap-4">
              <div>
                <h2 class="text-xl font-bold text-slate-900 dark:text-white">Tóm tắt JD</h2>
                <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Thông tin nhanh để bạn nhìn lại chất lượng tin tuyển dụng trước khi xử lý hồ sơ.</p>
              </div>
              <span
                class="inline-flex items-center rounded-full px-3 py-1 text-xs font-bold"
                :class="job.da_tuyen_du ? 'bg-rose-500/10 text-rose-300' : 'bg-emerald-500/10 text-emerald-300'"
              >
                {{ job.da_tuyen_du ? 'Đã đủ chỉ tiêu' : `${job.so_luong_con_lai || 0} vị trí còn lại` }}
              </span>
            </div>

            <div class="mt-5 grid grid-cols-1 gap-4 md:grid-cols-2">
              <div class="rounded-2xl bg-slate-50 p-5 dark:bg-slate-800/70">
                <p class="text-xs font-bold uppercase tracking-[0.22em] text-slate-400">Ngành nghề</p>
                <div class="mt-3 flex flex-wrap gap-2">
                  <span
                    v-for="industry in job.nganh_nghes || []"
                    :key="industry.id"
                    class="inline-flex items-center rounded-full bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 dark:bg-slate-900 dark:text-slate-200"
                  >
                    {{ industry.ten_nganh }}
                  </span>
                </div>
              </div>

              <div class="rounded-2xl bg-slate-50 p-5 dark:bg-slate-800/70">
                <p class="text-xs font-bold uppercase tracking-[0.22em] text-slate-400">Yêu cầu cơ bản</p>
                <div class="mt-3 space-y-3 text-sm text-slate-600 dark:text-slate-300">
                  <p><span class="font-semibold text-slate-900 dark:text-white">Cấp bậc:</span> {{ job.cap_bac || 'Chưa cập nhật' }}</p>
                  <p><span class="font-semibold text-slate-900 dark:text-white">Kinh nghiệm:</span> {{ job.kinh_nghiem_yeu_cau || 'Chưa cập nhật' }}</p>
                  <p><span class="font-semibold text-slate-900 dark:text-white">Số lượng tuyển:</span> {{ job.so_luong_tuyen || 0 }}</p>
                  <p><span class="font-semibold text-slate-900 dark:text-white">Hết hạn:</span> {{ formatDateTime(job.ngay_het_han) }}</p>
                </div>
              </div>
            </div>
          </div>

          <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm shadow-slate-950/5 dark:border-slate-800 dark:bg-slate-900">
            <div class="flex items-center justify-between gap-4">
              <div>
                <h2 class="text-xl font-bold text-slate-900 dark:text-white">Kỹ năng & yêu cầu đã parse</h2>
                <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Kết quả parse JD và các kỹ năng yêu cầu chuẩn hóa từ hệ thống.</p>
              </div>
              <span class="text-xs font-semibold uppercase tracking-[0.22em] text-slate-400">
                {{ requiredSkills.length }} kỹ năng
              </span>
            </div>

            <div class="mt-5">
              <p class="text-xs font-bold uppercase tracking-[0.22em] text-slate-400">Kỹ năng nổi bật</p>
              <div class="mt-3 flex flex-wrap gap-2">
                <span
                  v-for="skill in requiredSkills"
                  :key="skill"
                  class="inline-flex items-center rounded-full bg-[#2463eb]/10 px-3 py-1.5 text-xs font-semibold text-[#2463eb] dark:bg-[#2463eb]/15 dark:text-[#8fb1ff]"
                >
                  {{ skill }}
                </span>
                <span v-if="!requiredSkills.length" class="text-sm text-slate-500 dark:text-slate-400">Chưa có kỹ năng parse được cho JD này.</span>
              </div>
            </div>

            <div class="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
              <div class="rounded-2xl bg-slate-50 p-5 dark:bg-slate-800/70">
                <p class="text-xs font-bold uppercase tracking-[0.22em] text-slate-400">Yêu cầu trích xuất</p>
                <ul v-if="parsedRequirements.length" class="mt-3 space-y-2 text-sm leading-7 text-slate-600 dark:text-slate-300">
                  <li v-for="item in parsedRequirements" :key="item" class="flex gap-3">
                    <span class="mt-2 h-2 w-2 shrink-0 rounded-full bg-[#2463eb]" />
                    <span>{{ item }}</span>
                  </li>
                </ul>
                <p v-else class="mt-3 text-sm text-slate-500 dark:text-slate-400">Chưa có dữ liệu yêu cầu trích xuất.</p>
              </div>

              <div class="rounded-2xl bg-slate-50 p-5 dark:bg-slate-800/70">
                <p class="text-xs font-bold uppercase tracking-[0.22em] text-slate-400">Quyền lợi trích xuất</p>
                <ul v-if="parsedBenefits.length" class="mt-3 space-y-2 text-sm leading-7 text-slate-600 dark:text-slate-300">
                  <li v-for="item in parsedBenefits" :key="item" class="flex gap-3">
                    <span class="mt-2 h-2 w-2 shrink-0 rounded-full bg-emerald-400" />
                    <span>{{ item }}</span>
                  </li>
                </ul>
                <p v-else class="mt-3 text-sm text-slate-500 dark:text-slate-400">Chưa có dữ liệu quyền lợi trích xuất.</p>
              </div>
            </div>
          </div>

          <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm shadow-slate-950/5 dark:border-slate-800 dark:bg-slate-900">
            <div class="flex items-center justify-between gap-4">
              <div>
                <h2 class="text-xl font-bold text-slate-900 dark:text-white">Hồ sơ gần đây</h2>
                <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Các hồ sơ mới nộp vào tin này để bạn xử lý nhanh hơn.</p>
              </div>
              <RouterLink to="/employer/interviews" class="text-sm font-bold text-[#2463eb] hover:underline">
                Mở trang xử lý ứng tuyển
              </RouterLink>
            </div>

            <div v-if="upcomingApplications.length" class="mt-5 space-y-3">
              <div
                v-for="application in upcomingApplications"
                :key="application.id"
                class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4 dark:border-slate-800 dark:bg-slate-800/40"
              >
                <div class="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                  <div class="min-w-0 flex-1">
                    <p class="text-base font-bold text-slate-900 dark:text-white">
                      {{ application.ho_so?.tieu_de_ho_so || 'Hồ sơ ứng viên' }}
                    </p>
                    <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
                      {{ application.ho_so?.nguoi_dung?.email || 'Chưa có email' }}
                    </p>
                    <p class="mt-2 text-sm text-slate-600 dark:text-slate-300">
                      Nộp lúc {{ formatSubmittedDateTime(application.thoi_gian_ung_tuyen) }}
                    </p>
                  </div>
                  <span
                    class="inline-flex items-center rounded-full px-3 py-1 text-xs font-bold"
                    :class="applicationStatusMeta(application.trang_thai).classes"
                  >
                    {{ applicationStatusMeta(application.trang_thai).label }}
                  </span>
                </div>
              </div>
            </div>

            <div v-else class="mt-5 rounded-2xl border border-dashed border-slate-200 px-4 py-8 text-center text-sm text-slate-500 dark:border-slate-700 dark:text-slate-400">
              Chưa có hồ sơ nào nộp vào tin tuyển dụng này.
            </div>
          </div>
        </div>

        <div class="space-y-6">
          <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm shadow-slate-950/5 dark:border-slate-800 dark:bg-slate-900">
            <h2 class="text-xl font-bold text-slate-900 dark:text-white">Chỉ tiêu tuyển dụng</h2>
            <div class="mt-5 space-y-4">
              <div class="rounded-2xl bg-slate-50 px-4 py-4 dark:bg-slate-800/70">
                <p class="text-xs font-bold uppercase tracking-[0.22em] text-slate-400">Tổng cần tuyển</p>
                <p class="mt-2 text-3xl font-black text-slate-900 dark:text-white">{{ job.so_luong_tuyen || 0 }}</p>
              </div>
              <div class="grid grid-cols-2 gap-3">
                <div class="rounded-2xl bg-emerald-500/10 px-4 py-4">
                  <p class="text-xs font-bold uppercase tracking-[0.22em] text-emerald-300">Trúng tuyển</p>
                  <p class="mt-2 text-2xl font-black text-emerald-300">{{ job.so_luong_da_nhan || 0 }}</p>
                </div>
                <div class="rounded-2xl bg-blue-500/10 px-4 py-4">
                  <p class="text-xs font-bold uppercase tracking-[0.22em] text-[#2463eb] dark:text-[#8fb1ff]">Còn lại</p>
                  <p class="mt-2 text-2xl font-black text-[#2463eb] dark:text-[#8fb1ff]">{{ job.so_luong_con_lai || 0 }}</p>
                </div>
              </div>
            </div>
          </div>

          <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm shadow-slate-950/5 dark:border-slate-800 dark:bg-slate-900">
            <h2 class="text-xl font-bold text-slate-900 dark:text-white">Parse JD</h2>
            <div class="mt-5 space-y-4 text-sm text-slate-600 dark:text-slate-300">
              <p><span class="font-semibold text-slate-900 dark:text-white">Trạng thái:</span> {{ parseStatusMeta.label }}</p>
              <p><span class="font-semibold text-slate-900 dark:text-white">Model / phiên bản:</span> {{ job.parsing?.parser_version || 'Chưa có' }}</p>
              <p><span class="font-semibold text-slate-900 dark:text-white">Độ tin cậy:</span> {{ job.parsing?.confidence_score ? `${Math.round(job.parsing.confidence_score * 100)}%` : 'Chưa có' }}</p>
              <p><span class="font-semibold text-slate-900 dark:text-white">Cập nhật lần cuối:</span> {{ formatDateTime(job.parsing?.updated_at) }}</p>
              <p v-if="job.parsing?.error_message" class="rounded-2xl bg-rose-500/10 px-4 py-3 text-rose-300">
                {{ job.parsing.error_message }}
              </p>
            </div>
          </div>

          <div class="rounded-2xl border border-slate-200 bg-gradient-to-br from-[#2463eb] via-[#355dff] to-[#724dff] p-6 text-white shadow-[0_24px_60px_rgba(36,99,235,0.28)] dark:border-slate-800">
            <p class="text-xs font-semibold uppercase tracking-[0.24em] text-white/70">Gợi ý vận hành</p>
            <h3 class="mt-3 text-2xl font-black leading-tight">Giữ JD đủ rõ trước khi tăng tốc tuyển dụng</h3>
            <ul class="mt-5 space-y-3 text-sm leading-7 text-white/90">
              <li class="flex gap-3">
                <span class="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-white/90" />
                <span>JD đã parse tốt sẽ giúp matching, chatbot và cover letter sát hơn với nhu cầu tuyển dụng.</span>
              </li>
              <li class="flex gap-3">
                <span class="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-white/90" />
                <span>Hãy theo dõi chỉ tiêu còn lại để tránh chấp nhận vượt số lượng tuyển thực tế.</span>
              </li>
              <li class="flex gap-3">
                <span class="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-white/90" />
                <span>Khi hồ sơ bắt đầu tăng, nên chuyển sang trang phỏng vấn để hẹn lịch và gửi mail cho ứng viên ngay.</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
