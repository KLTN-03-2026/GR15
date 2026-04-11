<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { applicationService, profileService, savedJobService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'

const notify = useNotify()
const router = useRouter()

const loading = ref(false)
const removingJobId = ref(null)
const applyingJobId = ref(null)
const generatingCoverLetter = ref(false)
const loadingProfiles = ref(false)
const jobs = ref([])
const profiles = ref([])
const sortOption = ref('newest')
const applyModalOpen = ref(false)
const selectedJob = ref(null)
const selectedProfileId = ref('')
const coverLetter = ref('')
const generatedCoverLetterId = ref(null)
const generatedCoverLetter = ref('')
const pagination = reactive({
  current_page: 1,
  last_page: 1,
  per_page: 12,
  total: 0,
  from: 0,
  to: 0,
})

const sortedJobs = computed(() => {
  const items = [...jobs.value]
  if (sortOption.value === 'oldest') {
    return items.sort((a, b) => new Date(a.pivot?.created_at || 0) - new Date(b.pivot?.created_at || 0))
  }
  return items.sort((a, b) => new Date(b.pivot?.created_at || 0) - new Date(a.pivot?.created_at || 0))
})

const formatCurrency = (value) => {
  if (value === null || value === undefined || value === '') return 'Thỏa thuận'
  return new Intl.NumberFormat('vi-VN').format(Number(value)) + ' đ'
}

const formatSalary = (job) => {
  if (job.muc_luong_tu && job.muc_luong_den) {
    return `${formatCurrency(job.muc_luong_tu)} - ${formatCurrency(job.muc_luong_den)}`
  }
  if (job.muc_luong) {
    return formatCurrency(job.muc_luong)
  }
  return 'Thỏa thuận'
}

const formatSavedDate = (value) => {
  if (!value) return 'Mới lưu'
  const date = new Date(value)
  return `Lưu ${date.toLocaleDateString('vi-VN')}`
}

const getAcceptedCount = (job) => Number(job?.so_luong_da_nhan || 0)
const getRemainingSlots = (job) => Number(job?.so_luong_con_lai || 0)
const isQuotaFull = (job) => Boolean(job?.da_tuyen_du) || (Number(job?.so_luong_tuyen || 0) > 0 && getRemainingSlots(job) <= 0)

const selectedProfile = computed(() =>
  profiles.value.find((profile) => Number(profile.id) === Number(selectedProfileId.value)) || null
)

const fetchSavedJobs = async (page = 1) => {
  loading.value = true
  try {
    const response = await savedJobService.getSavedJobs({
      page,
      per_page: pagination.per_page,
    })
    const payload = response?.data || {}
    jobs.value = payload.data || []
    pagination.current_page = payload.current_page || 1
    pagination.last_page = payload.last_page || 1
    pagination.total = payload.total || 0
    pagination.from = payload.from || 0
    pagination.to = payload.to || 0
  } catch (error) {
    jobs.value = []
    pagination.current_page = 1
    pagination.last_page = 1
    pagination.total = 0
    pagination.from = 0
    pagination.to = 0
    notify.apiError(error, 'Không tải được danh sách tin đã lưu.')
  } finally {
    loading.value = false
  }
}

const toggleSaved = async (jobId) => {
  if (removingJobId.value) return
  removingJobId.value = jobId
  try {
    await savedJobService.toggleSavedJob(jobId)
    notify.info('Đã bỏ lưu tin tuyển dụng.')
    jobs.value = jobs.value.filter((job) => Number(job.id) !== Number(jobId))
    pagination.total = Math.max(0, pagination.total - 1)
  } catch (error) {
    notify.apiError(error, 'Không thể cập nhật tin đã lưu.')
  } finally {
    removingJobId.value = null
  }
}

const changePage = async (page) => {
  if (page < 1 || page > pagination.last_page || page === pagination.current_page) return
  await fetchSavedJobs(page)
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

const openApplyModal = async (job) => {
  if (isQuotaFull(job)) {
    notify.warning('Tin tuyển dụng này đã đủ chỉ tiêu tuyển dụng.')
    return
  }

  await loadProfiles()

  if (!profiles.value.length) {
    notify.warning('Bạn cần tạo ít nhất một hồ sơ/CV trước khi ứng tuyển.')
    return
  }

  selectedJob.value = job
  resetCoverLetterDraft()
  applyModalOpen.value = true
}

const closeApplyModal = () => {
  if (applyingJobId.value || generatingCoverLetter.value) return
  applyModalOpen.value = false
  selectedJob.value = null
}

const redirectToApplications = async () => {
  applyModalOpen.value = false
  selectedJob.value = null
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
  if (!selectedJob.value?.id || !selectedProfileId.value || applyingJobId.value) return

  applyingJobId.value = selectedJob.value.id
  try {
    await applicationService.apply({
      tin_tuyen_dung_id: selectedJob.value.id,
      ho_so_id: Number(selectedProfileId.value),
      thu_xin_viec: coverLetter.value.trim() || null,
    })

    notify.success('Ứng tuyển thành công. Bạn có thể theo dõi tại mục Việc đã ứng tuyển.')
    applyModalOpen.value = false
    selectedJob.value = null
    resetCoverLetterDraft()
  } catch (error) {
    if (await handleExistingApplicationError(error)) {
      return
    }
    notify.apiError(error, 'Không thể ứng tuyển vào tin này.')
  } finally {
    applyingJobId.value = null
  }
}

const resetCoverLetterDraft = () => {
  coverLetter.value = ''
  generatedCoverLetterId.value = null
  generatedCoverLetter.value = ''
}

const generateCoverLetter = async () => {
  notify.info('Cover letter AI chưa được bật trong bản HoangLong. Bạn vẫn có thể nhập thư ứng tuyển thủ công.')
}

onMounted(() => {
  fetchSavedJobs()
})

watch(selectedProfileId, (nextValue, previousValue) => {
  if (!generatedCoverLetterId.value || !previousValue || nextValue === previousValue) return

  const shouldClearText = coverLetter.value.trim() === generatedCoverLetter.value.trim()
  generatedCoverLetterId.value = null
  generatedCoverLetter.value = ''

  if (shouldClearText) {
    coverLetter.value = ''
  }
})
</script>

<template>
  <div>
    <div class="mb-8 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-900 dark:text-white">Tin đã lưu</h1>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Các tin tuyển dụng bạn đã bookmark để xem lại và ứng tuyển sau.
        </p>
      </div>
      <div class="flex items-center gap-3">
        <div class="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <span class="material-symbols-outlined text-[18px] text-slate-400">sort</span>
          <select
            v-model="sortOption"
            class="cursor-pointer border-none bg-transparent p-0 pr-6 text-sm font-medium text-slate-700 focus:ring-0 dark:text-slate-300"
          >
            <option value="newest">Lưu gần đây nhất</option>
            <option value="oldest">Lưu lâu nhất</option>
          </select>
        </div>
      </div>
    </div>

    <div class="mb-6 flex items-center gap-3 rounded-xl border border-blue-100 bg-blue-50/70 p-4 dark:border-blue-500/20 dark:bg-blue-500/10">
      <span class="material-symbols-outlined text-blue-600 dark:text-blue-400">bookmark_added</span>
      <p class="text-sm text-slate-600 dark:text-slate-300">
        Bạn đang lưu <strong class="text-blue-600">{{ pagination.total }}</strong> tin tuyển dụng. Bấm biểu tượng bookmark để bỏ lưu.
      </p>
    </div>

    <div v-if="loading" class="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <div
        v-for="index in 4"
        :key="index"
        class="h-64 animate-pulse rounded-xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900"
      />
    </div>

    <div
      v-else-if="!sortedJobs.length"
      class="rounded-2xl border border-dashed border-slate-300 bg-white px-6 py-14 text-center shadow-sm dark:border-slate-700 dark:bg-slate-900"
    >
      <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-slate-100 dark:bg-slate-800">
        <span class="material-symbols-outlined text-3xl text-slate-500">bookmarks</span>
      </div>
      <h2 class="mt-5 text-xl font-bold text-slate-900 dark:text-white">Bạn chưa lưu tin tuyển dụng nào</h2>
      <p class="mx-auto mt-3 max-w-xl text-sm leading-7 text-slate-500 dark:text-slate-400">
        Hãy quay lại trang tìm việc và lưu những vị trí bạn muốn theo dõi để ứng tuyển vào thời điểm phù hợp.
      </p>
      <RouterLink
        :to="{ name: 'JobSearch' }"
        class="mt-6 inline-flex rounded-xl bg-blue-600 px-5 py-3 text-sm font-bold text-white transition hover:bg-blue-700"
      >
        Tìm việc ngay
      </RouterLink>
    </div>

    <div v-else class="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <div
        v-for="job in sortedJobs"
        :key="job.id"
        class="group rounded-xl border border-slate-200 bg-white p-6 shadow-sm transition-all hover:border-blue-300 hover:shadow-md dark:border-slate-800 dark:bg-slate-900"
      >
        <div class="mb-4 flex items-start gap-4">
          <div class="flex size-14 shrink-0 items-center justify-center rounded-lg border border-slate-100 bg-slate-100 dark:border-slate-700 dark:bg-slate-800">
            <span class="material-symbols-outlined text-2xl text-slate-500">domain</span>
          </div>
          <div class="flex-1">
            <div class="flex justify-between gap-3">
              <span class="rounded bg-blue-50 px-2 py-0.5 text-[10px] font-bold uppercase text-blue-700 dark:bg-blue-500/10 dark:text-blue-400">
                {{ job.cap_bac || 'Tin tuyển dụng' }}
              </span>
              <button
                class="text-blue-600 transition-colors hover:text-red-500"
                title="Bỏ lưu"
                type="button"
                @click="toggleSaved(job.id)"
              >
                <span class="material-symbols-outlined fill-1">
                  {{ removingJobId === job.id ? 'hourglass_top' : 'bookmark' }}
                </span>
              </button>
            </div>

            <RouterLink
              :to="{ name: 'JobDetail', params: { id: job.id } }"
              class="mt-2 block text-lg font-bold text-slate-900 transition-colors group-hover:text-blue-600 dark:text-white"
            >
              {{ job.tieu_de }}
            </RouterLink>
            <p class="text-sm text-slate-500 dark:text-slate-400">
              {{ job.cong_ty?.ten_cong_ty || 'Công ty đang cập nhật' }} • {{ job.dia_diem_lam_viec || 'Địa điểm đang cập nhật' }}
            </p>
          </div>
        </div>

        <div class="mb-4 flex flex-wrap gap-2">
          <span
            v-for="industry in job.nganh_nghes || []"
            :key="industry.id"
            class="rounded bg-slate-100 px-2 py-1 text-xs font-medium dark:bg-slate-800"
          >
            {{ industry.ten_nganh }}
          </span>
          <span
            v-if="job.hinh_thuc_lam_viec"
            class="rounded bg-slate-100 px-2 py-1 text-xs font-medium dark:bg-slate-800"
          >
            {{ job.hinh_thuc_lam_viec }}
          </span>
          <span
            class="rounded px-2 py-1 text-xs font-semibold"
            :class="isQuotaFull(job)
              ? 'bg-rose-50 text-rose-700 dark:bg-rose-500/10 dark:text-rose-300'
              : 'bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-300'"
          >
            {{ getAcceptedCount(job) }}/{{ job.so_luong_tuyen || 0 }} đã nhận · {{ isQuotaFull(job) ? 'Đã đủ chỉ tiêu' : `${getRemainingSlots(job)} còn lại` }}
          </span>
        </div>

        <div class="flex items-center justify-between border-t border-slate-100 pt-4 dark:border-slate-800">
          <div class="flex items-center gap-3">
            <p class="text-sm font-bold text-slate-700 dark:text-slate-300">{{ formatSalary(job) }}</p>
            <span class="text-[10px] text-slate-400">{{ formatSavedDate(job.pivot?.created_at) }}</span>
          </div>
          <div class="flex items-center gap-2">
            <RouterLink
              :to="{ name: 'JobDetail', params: { id: job.id } }"
              class="rounded-lg border border-slate-200 px-3 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
            >
              Xem chi tiết
            </RouterLink>
            <button
              class="rounded-lg px-4 py-2 text-sm font-bold text-white transition-all"
              :class="isQuotaFull(job) ? 'cursor-not-allowed bg-slate-400' : 'bg-blue-600 hover:bg-blue-700'"
              :disabled="isQuotaFull(job)"
              type="button"
              @click="openApplyModal(job)"
            >
              {{ isQuotaFull(job) ? 'Đã tuyển đủ' : 'Ứng tuyển' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="pagination.last_page > 1" class="mt-8 flex flex-wrap items-center justify-center gap-2">
      <button
        class="rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
        :disabled="pagination.current_page === 1"
        type="button"
        @click="changePage(pagination.current_page - 1)"
      >
        Trước
      </button>

      <button
        v-for="page in pagination.last_page"
        :key="page"
        class="h-11 min-w-11 rounded-xl border px-4 text-sm font-bold transition"
        :class="page === pagination.current_page
          ? 'border-blue-600 bg-blue-600 text-white'
          : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800'"
        type="button"
        @click="changePage(page)"
      >
        {{ page }}
      </button>

      <button
        class="rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
        :disabled="pagination.current_page === pagination.last_page"
        type="button"
        @click="changePage(pagination.current_page + 1)"
      >
        Sau
      </button>
    </div>

    <div
      v-if="applyModalOpen"
      class="fixed inset-0 z-50 overflow-y-auto bg-slate-950/55 px-4 py-6 backdrop-blur-sm"
      @click.self="closeApplyModal"
    >
      <div class="mx-auto w-full max-w-4xl rounded-[28px] border border-slate-200 bg-white shadow-2xl dark:border-slate-800 dark:bg-slate-950">
        <div class="flex items-start justify-between border-b border-slate-100 px-6 py-5 dark:border-slate-800">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.28em] text-blue-500">Ứng tuyển từ tin đã lưu</p>
            <h3 class="mt-2 text-2xl font-bold text-slate-900 dark:text-white">{{ selectedJob?.tieu_de }}</h3>
            <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">
              {{ selectedJob?.cong_ty?.ten_cong_ty || 'Công ty đang cập nhật' }}
            </p>
            <p
              v-if="selectedJob"
              class="mt-2 inline-flex rounded-full px-3 py-1 text-xs font-semibold"
              :class="isQuotaFull(selectedJob)
                ? 'bg-rose-50 text-rose-700 dark:bg-rose-500/10 dark:text-rose-300'
                : 'bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-300'"
            >
              {{ getAcceptedCount(selectedJob) }}/{{ selectedJob.so_luong_tuyen || 0 }} đã nhận · {{ isQuotaFull(selectedJob) ? 'Đã đủ chỉ tiêu' : `${getRemainingSlots(selectedJob)} còn lại` }}
            </p>
          </div>
          <button
            class="rounded-full p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-900 dark:hover:text-slate-200"
            type="button"
            @click="closeApplyModal"
          >
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>

        <div class="max-h-[calc(100vh-12rem)] space-y-5 overflow-y-auto px-6 py-6">
          <div v-if="loadingProfiles" class="rounded-2xl bg-slate-50 px-4 py-5 text-sm text-slate-500 dark:bg-slate-900 dark:text-slate-400">
            Đang tải danh sách hồ sơ...
          </div>

          <template v-else>
            <div>
              <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-300">Chọn hồ sơ ứng tuyển</label>
              <select
                v-model="selectedProfileId"
                class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-200 dark:focus:ring-blue-500/20"
              >
                <option value="" disabled>Chọn hồ sơ của bạn</option>
                <option v-for="profile in profiles" :key="profile.id" :value="String(profile.id)">
                  {{ profile.tieu_de_ho_so || `Hồ sơ #${profile.id}` }}
                </option>
              </select>
            </div>

            <div v-if="selectedProfile" class="rounded-2xl bg-slate-50 px-4 py-4 text-sm text-slate-600 dark:bg-slate-900 dark:text-slate-400">
              <p class="font-semibold text-slate-800 dark:text-slate-200">{{ selectedProfile.tieu_de_ho_so || `Hồ sơ #${selectedProfile.id}` }}</p>
              <p class="mt-1">
                Kinh nghiệm: {{ selectedProfile.kinh_nghiem_nam || 0 }} năm
                <span v-if="selectedProfile.vi_tri_mong_muon">• Mục tiêu: {{ selectedProfile.vi_tri_mong_muon }}</span>
              </p>
            </div>

            <div>
              <div class="mb-2 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <label class="block text-sm font-semibold text-slate-700 dark:text-slate-300">Thư giới thiệu / Cover Letter</label>
                <button
                  class="inline-flex items-center justify-center gap-2 rounded-xl border border-blue-200 bg-blue-50 px-4 py-2 text-sm font-semibold text-blue-700 transition hover:border-blue-300 hover:bg-blue-100 disabled:cursor-not-allowed disabled:opacity-60 dark:border-blue-500/20 dark:bg-blue-500/10 dark:text-blue-300 dark:hover:bg-blue-500/15"
                  :disabled="!selectedProfileId || generatingCoverLetter || applyingJobId"
                  type="button"
                  @click="generateCoverLetter"
                >
                  <span class="material-symbols-outlined text-[18px]">auto_awesome</span>
                  {{ generatingCoverLetter ? 'Đang sinh thư AI...' : 'Sinh thư AI' }}
                </button>
              </div>
              <textarea
                v-model="coverLetter"
                rows="10"
                maxlength="5000"
                class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-200 dark:focus:ring-blue-500/20"
                placeholder="Ví dụ: Tôi mong muốn được tham gia phỏng vấn để trao đổi thêm về kinh nghiệm và mức độ phù hợp với vị trí này."
              />
              <div class="mt-2 flex flex-col gap-2 text-xs text-slate-400 dark:text-slate-500 sm:flex-row sm:items-center sm:justify-between">
                <p v-if="generatedCoverLetterId" class="font-medium text-blue-600">
                  Đã có nháp AI. Bạn có thể chỉnh sửa nội dung trước khi nộp hồ sơ.
                </p>
                <p v-else>AI có thể giúp bạn khởi tạo nhanh thư ứng tuyển theo đúng hồ sơ đã chọn.</p>
                <div class="text-right">{{ coverLetter.length }}/5000</div>
              </div>
            </div>
          </template>
        </div>

        <div class="flex flex-col gap-3 border-t border-slate-100 px-6 py-5 dark:border-slate-800 sm:flex-row sm:justify-end">
          <RouterLink
            v-if="!profiles.length"
            :to="{ name: 'MyCv' }"
            class="inline-flex items-center justify-center rounded-2xl border border-slate-200 px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-900"
          >
            Tạo hồ sơ trước
          </RouterLink>
          <button
            class="rounded-2xl border border-slate-200 px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-900"
            type="button"
            @click="closeApplyModal"
          >
            Để sau
          </button>
          <button
            class="rounded-2xl bg-blue-600 px-5 py-3 text-sm font-bold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-300"
            :disabled="!selectedProfileId || applyingJobId || loadingProfiles || generatingCoverLetter"
            type="button"
            @click="submitApplication"
          >
            {{ applyingJobId ? 'Đang nộp hồ sơ...' : generatedCoverLetterId ? 'Xác nhận thư và ứng tuyển' : 'Xác nhận ứng tuyển' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
