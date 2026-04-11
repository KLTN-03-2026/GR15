<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useNotify } from '@/composables/useNotify'
import { jobService } from '@/services/api'

const router = useRouter()
const notify = useNotify()

const searchMode = ref('quick')
const quickQuery = ref('')
const semanticQuery = ref('')

const featuredJobs = ref([])
const featuredIndustries = ref([])
const featuredSkills = ref([])
const featuredCompanies = ref([])
const loadingLanding = ref(false)

const placeholderText = computed(() =>
  searchMode.value === 'semantic'
    ? 'Ví dụ: backend Laravel remote, ưu tiên REST API và MySQL'
    : 'Kỹ năng, ngành nghề hoặc địa điểm...',
)

const scoreFeaturedJob = (job) => {
  const hasSalary = Number(job?.muc_luong || 0) || (Number(job?.muc_luong_tu || 0) && Number(job?.muc_luong_den || 0)) ? 1 : 0
  const views = Number(job?.luot_xem || 0)
  const createdAt = job?.created_at ? new Date(job.created_at).getTime() : 0
  return (hasSalary * 2000000000000) + (views * 1000000) + createdAt
}

const sortedFeaturedJobs = computed(() =>
  [...featuredJobs.value]
    .sort((a, b) => scoreFeaturedJob(b) - scoreFeaturedJob(a))
    .slice(0, 3),
)

const extractList = (response) => {
  const payload = response?.data
  if (Array.isArray(payload?.data)) return payload.data
  if (Array.isArray(payload)) return payload
  return []
}

const formatSalary = (job) => {
  const salaryFrom = Number(job?.muc_luong_tu || 0)
  const salaryTo = Number(job?.muc_luong_den || 0)
  const salary = Number(job?.muc_luong || 0)
  const formatMillion = (value) => {
    const million = value / 1000000
    return Number.isInteger(million)
      ? `${million}`
      : million.toLocaleString('vi-VN', { maximumFractionDigits: 1 })
  }

  if (salaryFrom && salaryTo) {
    return `${formatMillion(salaryFrom)} - ${formatMillion(salaryTo)} triệu`
  }

  if (salary) {
    return `${formatMillion(salary)} triệu`
  }

  return 'Thỏa thuận'
}

const getRemainingSlots = (job) => {
  const totalSlots = Number(job?.so_luong_tuyen || 0)
  const acceptedSlots = Number(job?.so_luong_da_nhan || 0)
  const explicitRemaining = Number(job?.so_luong_con_lai || 0)

  if (explicitRemaining > 0) return explicitRemaining
  if (totalSlots > 0) return Math.max(totalSlots - acceptedSlots, 0)
  return 0
}

const getHiringStatus = (job) => {
  const totalSlots = Number(job?.so_luong_tuyen || 0)
  const acceptedSlots = Number(job?.so_luong_da_nhan || 0)
  const remainingSlots = getRemainingSlots(job)

  if (!totalSlots) {
    return {
      label: 'Đang tuyển',
      tone: 'bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200/80 dark:bg-emerald-500/10 dark:text-emerald-300 dark:ring-emerald-500/20',
    }
  }

  if (remainingSlots <= 0) {
    return {
      label: `Đủ ${acceptedSlots}/${totalSlots} vị trí`,
      tone: 'bg-rose-50 text-rose-700 ring-1 ring-rose-200/80 dark:bg-rose-500/10 dark:text-rose-300 dark:ring-rose-500/20',
    }
  }

  return {
    label: `Còn ${remainingSlots}/${totalSlots} vị trí`,
    tone: 'bg-amber-50 text-amber-700 ring-1 ring-amber-200/80 dark:bg-amber-500/10 dark:text-amber-300 dark:ring-amber-500/20',
  }
}

const formatCompactNumber = (value) => Number(value || 0).toLocaleString('vi-VN')

const getCompanyName = (job) =>
  job?.cong_ty?.ten_cong_ty || job?.ten_cong_ty || 'Doanh nghiệp đang cập nhật'

const getLocationText = (job) => job?.dia_diem_lam_viec || 'Linh hoạt'

const getTagList = (job) => {
  const industries = Array.isArray(job?.nganh_nghes)
    ? job.nganh_nghes.map((item) => item?.ten_nganh || item?.ten_nganh_nghe).filter(Boolean)
    : []

  const skills = Array.isArray(job?.ky_nangs)
    ? job.ky_nangs.map((item) => item?.ten_ky_nang || item?.ten).filter(Boolean)
    : []

  return [...new Set([...industries, ...skills])].slice(0, 3)
}

const loadLandingData = async () => {
  loadingLanding.value = true

  try {
    const [jobsResponse, industriesResponse, skillsResponse, companiesResponse] = await Promise.all([
      jobService.getJobs({ per_page: 8 }),
      jobService.getIndustries({ per_page: 6 }),
      jobService.getSkills({ per_page: 8 }),
      jobService.getCompanies({ per_page: 4 }),
    ])

    featuredJobs.value = extractList(jobsResponse)
    featuredIndustries.value = extractList(industriesResponse)
    featuredSkills.value = extractList(skillsResponse)
    featuredCompanies.value = extractList(companiesResponse)
  } catch (error) {
    notify.apiError(error, 'Không thể tải dữ liệu trang chủ.')
  } finally {
    loadingLanding.value = false
  }
}

const handleHeroSearch = () => {
  const value = searchMode.value === 'semantic' ? semanticQuery.value.trim() : quickQuery.value.trim()

  if (!value) {
    notify.warning(
      searchMode.value === 'semantic'
        ? 'Hãy nhập mô tả công việc bạn muốn tìm bằng AI.'
        : 'Hãy nhập từ khóa hoặc địa điểm để tìm việc.',
    )
    return
  }

  router.push({
    path: '/jobs',
    query: searchMode.value === 'semantic'
      ? { semantic_q: value }
      : { search: value },
  })
}

onMounted(() => {
  loadLandingData()
})
</script>

<template>
  <section class="relative overflow-hidden py-16 lg:py-24">
    <div class="mx-auto max-w-7xl px-6">
      <div class="relative z-10 flex flex-col items-center text-center">
        <span class="mb-4 inline-flex items-center gap-2 rounded-full bg-[#2463eb]/10 px-4 py-1.5 text-sm font-semibold text-[#2463eb]">
          <span class="material-symbols-outlined text-sm">auto_awesome</span>
          Ứng dụng Trí tuệ Nhân tạo thế hệ mới
        </span>
        <h1 class="max-w-4xl text-4xl font-black tracking-tight text-slate-900 dark:text-white sm:text-6xl">
          Tìm công việc phù hợp với <span class="text-[#2463eb]">AI Matching</span>
        </h1>
        <p class="mt-6 max-w-2xl text-lg text-slate-600 dark:text-slate-400">
          Hệ thống phân tích CV và mô tả công việc để đưa ra mức độ phù hợp, gợi ý lộ trình phát triển và kết nối bạn với nhà tuyển dụng hàng đầu.
        </p>

        <div class="mt-10 w-full max-w-4xl rounded-[28px] bg-white/95 p-3 shadow-2xl ring-1 ring-slate-200 backdrop-blur dark:bg-slate-900/95 dark:ring-slate-800">
          <div class="flex flex-wrap items-center gap-2 border-b border-slate-200 px-2 pb-3 dark:border-slate-800">
            <button
              type="button"
              class="inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-bold transition-all"
              :class="searchMode === 'quick'
                ? 'bg-[#2463eb] text-white shadow-lg shadow-blue-200/60'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300'"
              @click="searchMode = 'quick'"
            >
              <span class="material-symbols-outlined text-base">search</span>
              Tìm nhanh
            </button>
            <button
              type="button"
              class="inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-bold transition-all"
              :class="searchMode === 'semantic'
                ? 'bg-[#2463eb] text-white shadow-lg shadow-blue-200/60'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300'"
              @click="searchMode = 'semantic'"
            >
              <span class="material-symbols-outlined text-base">auto_awesome</span>
              Semantic Search
            </button>
          </div>

          <div class="mt-3 flex flex-col gap-3 md:flex-row md:items-center">
            <div class="flex min-w-0 flex-1 items-center rounded-2xl bg-slate-50 px-4 dark:bg-slate-950">
              <span class="material-symbols-outlined text-slate-400">
                {{ searchMode === 'semantic' ? 'psychology' : 'search' }}
              </span>
              <input
                v-if="searchMode === 'quick'"
                v-model="quickQuery"
                class="w-full border-none bg-transparent py-4 text-slate-900 shadow-none outline-none ring-0 placeholder:text-slate-400 focus:border-transparent focus:outline-none focus:ring-0 focus:ring-offset-0 dark:text-white"
                :placeholder="placeholderText"
                type="text"
                @keyup.enter="handleHeroSearch"
              />
              <input
                v-else
                v-model="semanticQuery"
                class="w-full border-none bg-transparent py-4 text-slate-900 shadow-none outline-none ring-0 placeholder:text-slate-400 focus:border-transparent focus:outline-none focus:ring-0 focus:ring-offset-0 dark:text-white"
                :placeholder="placeholderText"
                type="text"
                @keyup.enter="handleHeroSearch"
              />
            </div>

            <button
              type="button"
              class="flex h-14 items-center justify-center gap-2 rounded-2xl bg-[#2463eb] px-8 font-bold text-white transition-all hover:bg-blue-700"
              @click="handleHeroSearch"
            >
              <span class="material-symbols-outlined text-base">{{ searchMode === 'semantic' ? 'auto_awesome' : 'search' }}</span>
              {{ searchMode === 'semantic' ? 'Tìm bằng AI' : 'Tìm kiếm' }}
            </button>
          </div>

          <div class="mt-3 flex flex-wrap items-center gap-2 px-2 text-left">
            <span class="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
              {{ searchMode === 'semantic' ? 'Mô tả tự nhiên, AI tự hiểu ý bạn' : 'Tìm nhanh theo từ khóa quen thuộc' }}
            </span>
            <span
              v-if="searchMode === 'semantic'"
              class="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600 dark:bg-slate-800 dark:text-slate-300"
            >
              Ví dụ: backend Laravel, Docker, Đà Nẵng hoặc remote
            </span>
          </div>
        </div>

        <div
          v-if="featuredIndustries.length || featuredSkills.length"
          class="mt-6 flex max-w-5xl flex-wrap items-center justify-center gap-3"
        >
          <RouterLink
            v-for="industry in featuredIndustries"
            :key="`industry-${industry.id}`"
            :to="`/industries/${industry.id}`"
            class="rounded-full border border-slate-200 bg-white/80 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-[#2463eb] hover:text-[#2463eb] dark:border-slate-700 dark:bg-slate-900/80 dark:text-slate-200"
          >
            {{ industry.ten_nganh || industry.ten_nganh_nghe }}
          </RouterLink>
            <RouterLink
              v-for="skill in featuredSkills.slice(0, 4)"
              :key="`skill-${skill.id}`"
              :to="`/skills/${skill.id}`"
              class="rounded-full bg-slate-900/5 px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-[#2463eb]/10 hover:text-[#2463eb] dark:bg-white/5 dark:text-slate-300"
            >
              {{ skill.ten_ky_nang || skill.ten }}
            </RouterLink>
          <RouterLink
            to="/industries"
            class="rounded-full border border-slate-200 bg-white/80 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-[#2463eb] hover:text-[#2463eb] dark:border-slate-700 dark:bg-slate-900/80 dark:text-slate-200"
          >
            Xem tất cả ngành nghề
          </RouterLink>
          <RouterLink
            to="/skills"
            class="rounded-full bg-slate-900/5 px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-[#2463eb]/10 hover:text-[#2463eb] dark:bg-white/5 dark:text-slate-300"
          >
            Xem tất cả kỹ năng
          </RouterLink>
        </div>

        <div class="mt-8 flex flex-wrap justify-center gap-4">
          <RouterLink
            to="/my-cv"
            class="flex h-12 items-center justify-center gap-2 rounded-xl border-2 border-[#2463eb] bg-[#2463eb] px-8 font-bold text-white transition-all hover:bg-blue-700"
          >
            <span class="material-symbols-outlined">upload_file</span>
            Tải CV của bạn
          </RouterLink>
          <RouterLink
            to="/jobs"
            class="flex h-12 items-center justify-center gap-2 rounded-xl border-2 border-slate-200 bg-transparent px-8 font-bold text-slate-900 transition-all hover:bg-slate-100 dark:border-slate-700 dark:text-white dark:hover:bg-slate-800"
          >
            Tìm việc ngay
          </RouterLink>
        </div>
      </div>
    </div>

    <div class="absolute -top-24 -left-24 h-96 w-96 rounded-full bg-[#2463eb]/5 blur-[100px]"></div>
    <div class="absolute top-1/2 -right-24 h-64 w-64 rounded-full bg-[#2463eb]/10 blur-[80px]"></div>
  </section>

  <section class="bg-white py-20 dark:bg-slate-900/50">
    <div class="mx-auto max-w-7xl px-6 text-center">
      <h2 class="text-3xl font-bold tracking-tight text-slate-900 dark:text-white sm:text-4xl">Tại sao chọn AI Recruitment?</h2>
      <p class="mt-4 text-slate-600 dark:text-slate-400">Công nghệ AI tiên tiến giúp tối ưu hóa quy trình tìm việc của bạn</p>
      <div class="mt-16 grid grid-cols-1 gap-8 md:grid-cols-3">
        <div class="flex flex-col items-center rounded-2xl border border-slate-100 bg-white p-8 shadow-sm transition-all hover:shadow-md dark:border-slate-800 dark:bg-slate-900">
          <div class="mb-6 flex h-14 w-14 items-center justify-center rounded-xl bg-blue-100 text-[#2463eb]">
            <span class="material-symbols-outlined text-3xl">analytics</span>
          </div>
          <h3 class="text-xl font-bold text-slate-900 dark:text-white">AI Matching Score</h3>
          <p class="mt-3 text-center text-slate-600 dark:text-slate-400">Đánh giá độ tương thích giữa CV và Job Description theo thời gian thực với độ chính xác cao.</p>
        </div>
        <div class="flex flex-col items-center rounded-2xl border border-slate-100 bg-white p-8 shadow-sm transition-all hover:shadow-md dark:border-slate-800 dark:bg-slate-900">
          <div class="mb-6 flex h-14 w-14 items-center justify-center rounded-xl bg-purple-100 text-purple-600">
            <span class="material-symbols-outlined text-3xl">psychology</span>
          </div>
          <h3 class="text-xl font-bold text-slate-900 dark:text-white">Skill Gap Analysis</h3>
          <p class="mt-3 text-center text-slate-600 dark:text-slate-400">Phân tích những kỹ năng còn thiếu và gợi ý các khóa học để bạn sẵn sàng cho công việc mơ ước.</p>
        </div>
        <div class="flex flex-col items-center rounded-2xl border border-slate-100 bg-white p-8 shadow-sm transition-all hover:shadow-md dark:border-slate-800 dark:bg-slate-900">
          <div class="mb-6 flex h-14 w-14 items-center justify-center rounded-xl bg-emerald-100 text-emerald-600">
            <span class="material-symbols-outlined text-3xl">explore</span>
          </div>
          <h3 class="text-xl font-bold text-slate-900 dark:text-white">Career Recommendation</h3>
          <p class="mt-3 text-center text-slate-600 dark:text-slate-400">Định hướng nghề nghiệp dựa trên năng lực và xu hướng thị trường lao động toàn cầu.</p>
        </div>
      </div>
    </div>
  </section>

  <section class="py-20">
    <div class="mx-auto max-w-7xl px-6">
      <div class="mb-12 flex items-center justify-between">
        <div>
          <h2 class="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">Việc làm nổi bật</h2>
          <p class="mt-2 text-slate-600 dark:text-slate-400">Những cơ hội nghề nghiệp tốt nhất đang mở cho bạn ngay lúc này.</p>
        </div>
        <RouterLink to="/jobs" class="hidden items-center gap-2 font-bold text-[#2463eb] hover:underline sm:flex">
          Xem tất cả <span class="material-symbols-outlined">arrow_forward</span>
        </RouterLink>
      </div>

      <div v-if="loadingLanding" class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="index in 3"
          :key="index"
          class="h-80 animate-pulse rounded-2xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900"
        ></div>
      </div>

      <div v-else-if="sortedFeaturedJobs.length" class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="job in sortedFeaturedJobs"
          :key="job.id"
          class="group relative flex flex-col overflow-hidden rounded-[28px] border border-slate-200/80 bg-white/95 p-5 shadow-[0_20px_60px_-35px_rgba(15,23,42,0.35)] ring-1 ring-white/70 backdrop-blur transition-all hover:-translate-y-1.5 hover:border-[#2463eb]/40 hover:shadow-[0_28px_80px_-38px_rgba(37,99,235,0.45)] dark:border-slate-800 dark:bg-slate-900/95 dark:ring-slate-800/80"
        >
          <div class="pointer-events-none absolute inset-x-0 top-0 h-28 bg-gradient-to-br from-[#2463eb]/12 via-sky-100/60 to-transparent opacity-90 transition-opacity group-hover:opacity-100 dark:from-[#2463eb]/18 dark:via-slate-900 dark:to-transparent"></div>

          <div class="relative flex items-start justify-between gap-4">
            <div class="flex min-w-0 items-center gap-3">
              <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-[#2463eb] to-sky-500 text-base font-black text-white shadow-lg shadow-blue-200/70">
                {{ getCompanyName(job).slice(0, 1) }}
              </div>
              <div class="min-w-0">
                <p class="truncate text-sm font-semibold text-slate-900 dark:text-white">{{ getCompanyName(job) }}</p>
                <p class="mt-0.5 inline-flex items-center gap-1 text-xs font-medium text-slate-500 dark:text-slate-400">
                  <span class="material-symbols-outlined text-[14px]">distance</span>
                  {{ getLocationText(job) }}
                </p>
              </div>
            </div>
            <span class="shrink-0 rounded-full border border-blue-200/70 bg-white/90 px-3 py-1 text-[11px] font-bold text-[#2463eb] shadow-sm backdrop-blur dark:border-blue-500/20 dark:bg-slate-950/80">
              {{ job.hinh_thuc_lam_viec || 'Cơ hội mới' }}
            </span>
          </div>

          <div class="relative mt-5">
            <h3 class="line-clamp-2 text-[1.05rem] font-black leading-6 tracking-tight text-slate-900 transition-colors group-hover:text-[#2463eb] dark:text-white">
              {{ job.tieu_de }}
            </h3>
          </div>

          <p class="relative mt-3 line-clamp-2 text-sm leading-6 text-slate-600 dark:text-slate-400">
            {{ job.mo_ta_cong_viec || 'Mô tả công việc đang được cập nhật.' }}
          </p>

          <div class="relative mt-4 flex flex-wrap gap-2">
            <span
              v-for="tag in getTagList(job)"
              :key="tag"
              class="rounded-full border border-slate-200/80 bg-slate-50/90 px-2.5 py-1 text-[11px] font-semibold text-slate-600 dark:border-slate-700 dark:bg-slate-800/80 dark:text-slate-300"
            >
              {{ tag }}
            </span>
          </div>

          <div class="relative mt-5 rounded-[24px] border border-slate-200/80 bg-slate-50/90 p-3.5 shadow-inner shadow-white/80 dark:border-slate-800 dark:bg-slate-950/80 dark:shadow-none">
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0">
                <p class="text-[10px] font-bold uppercase tracking-[0.24em] text-slate-400 dark:text-slate-500">Mức lương</p>
                <p class="mt-1 truncate text-lg font-black text-slate-900 dark:text-white">{{ formatSalary(job) }}</p>
              </div>
              <span
                class="shrink-0 rounded-full px-2.5 py-1 text-[11px] font-bold"
                :class="getHiringStatus(job).tone"
              >
                {{ getHiringStatus(job).label }}
              </span>
            </div>

            <div class="mt-3 flex flex-col gap-3 border-t border-slate-200/80 pt-3 sm:flex-row sm:items-center sm:justify-between dark:border-slate-800">
              <div class="flex flex-wrap items-center gap-2 text-[11px] font-semibold text-slate-500 dark:text-slate-400">
                <span class="inline-flex items-center gap-1 rounded-full bg-white px-2.5 py-1.5 ring-1 ring-slate-200/80 dark:bg-slate-900 dark:ring-slate-700">
                  <span class="material-symbols-outlined text-[15px]">visibility</span>
                  {{ formatCompactNumber(job.luot_xem) }} xem
                </span>
                <span
                  v-if="Number(job?.so_luong_tuyen || 0)"
                  class="inline-flex items-center gap-1 rounded-full bg-white px-2.5 py-1.5 ring-1 ring-slate-200/80 dark:bg-slate-900 dark:ring-slate-700"
                >
                  <span class="material-symbols-outlined text-[15px]">groups</span>
                  {{ formatCompactNumber(job.so_luong_tuyen) }} chỉ tiêu
                </span>
              </div>

              <RouterLink
                :to="`/jobs/${job.id}`"
                class="inline-flex items-center justify-center gap-2 rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-bold text-white transition-all hover:bg-[#2463eb] hover:shadow-lg hover:shadow-blue-200/60 dark:bg-white dark:text-slate-900 dark:hover:bg-[#2463eb] dark:hover:text-white"
              >
                Xem job
                <span class="material-symbols-outlined text-[18px]">arrow_outward</span>
              </RouterLink>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="rounded-2xl border border-dashed border-slate-300 p-10 text-center dark:border-slate-700">
        <p class="text-slate-600 dark:text-slate-400">Chưa có tin tuyển dụng nổi bật để hiển thị.</p>
      </div>
    </div>
  </section>

  <section v-if="featuredCompanies.length" class="bg-white/60 py-20 dark:bg-slate-900/40">
    <div class="mx-auto max-w-7xl px-6">
      <div class="mb-10">
        <h2 class="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">Nhà tuyển dụng nổi bật</h2>
        <p class="mt-2 text-slate-600 dark:text-slate-400">Khám phá những doanh nghiệp đang tuyển dụng và xây đội ngũ mạnh hơn mỗi ngày.</p>
      </div>

      <div class="mb-8 flex justify-end">
        <RouterLink
          to="/companies"
          class="inline-flex items-center gap-2 rounded-xl border border-slate-200 px-4 py-2 text-sm font-bold text-slate-700 transition hover:border-[#2463eb] hover:text-[#2463eb] dark:border-slate-700 dark:text-slate-200"
        >
          Xem tất cả doanh nghiệp
          <span class="material-symbols-outlined text-[18px]">arrow_forward</span>
        </RouterLink>
      </div>

      <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-4">
        <div
          v-for="company in featuredCompanies"
          :key="company.id"
          class="rounded-2xl border border-slate-200 bg-white p-5 transition hover:-translate-y-1 hover:border-[#2463eb]/40 hover:shadow-lg dark:border-slate-800 dark:bg-slate-900"
        >
          <div class="flex items-center gap-4">
            <img
              v-if="company.logo_url"
              :src="company.logo_url"
              :alt="company.ten_cong_ty"
              class="h-14 w-14 rounded-xl object-cover ring-1 ring-slate-200 dark:ring-slate-700"
            />
            <div
              v-else
              class="flex h-14 w-14 items-center justify-center rounded-xl bg-[#2463eb]/10 text-lg font-black text-[#2463eb]"
            >
              {{ company.ten_cong_ty?.slice(0, 1) }}
            </div>

            <div class="min-w-0">
              <h3 class="truncate text-base font-bold text-slate-900 dark:text-white">{{ company.ten_cong_ty }}</h3>
              <p class="truncate text-sm text-slate-500">
                {{ company.quy_mo || 'Doanh nghiệp công nghệ' }} • {{ company.so_tin_dang_hoat_dong || 0 }} tin đang mở
              </p>
            </div>
          </div>

          <p class="mt-4 line-clamp-3 text-sm leading-6 text-slate-600 dark:text-slate-400">
            {{ company.mo_ta || 'Doanh nghiệp đang mở rộng đội ngũ và tìm kiếm ứng viên phù hợp.' }}
          </p>

          <RouterLink
            :to="`/companies/${company.id}`"
            class="mt-5 inline-flex text-sm font-bold text-[#2463eb] hover:underline"
          >
            Xem doanh nghiệp
          </RouterLink>
        </div>
      </div>
    </div>
  </section>
</template>
