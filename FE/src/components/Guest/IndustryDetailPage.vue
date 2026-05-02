<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { jobService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'

const route = useRoute()
const notify = useNotify()

const loading = ref(false)
const industry = ref(null)
const industryJobs = ref([])

const extractList = (response) => {
  const payload = response?.data
  if (Array.isArray(payload?.data)) return payload.data
  if (Array.isArray(payload)) return payload
  return []
}

const loadIndustryDetail = async () => {
  loading.value = true

  try {
    const [industryResponse, jobsResponse] = await Promise.all([
      jobService.getIndustryById(route.params.id),
      jobService.getJobs({
        nganh_nghe_id: route.params.id,
        per_page: 6,
      }),
    ])

    industry.value = industryResponse?.data || null
    industryJobs.value = extractList(jobsResponse)
  } catch (error) {
    industry.value = null
    industryJobs.value = []
    notify.apiError(error, 'Không tải được thông tin ngành nghề.')
  } finally {
    loading.value = false
  }
}

const industryName = computed(() => industry.value?.ten_nganh || 'Ngành nghề')
const industryDescription = computed(() => industry.value?.mo_ta || 'Ngành nghề này đang được cập nhật thêm phần mô tả chi tiết.')
const parentIndustry = computed(() => industry.value?.danh_muc_cha || null)
const childIndustries = computed(() => Array.isArray(industry.value?.danh_muc_con) ? industry.value.danh_muc_con : [])
const openJobsCount = computed(() => industryJobs.value.length)

const formatSalary = (job) => {
  const from = Number(job?.muc_luong_tu || 0)
  const to = Number(job?.muc_luong_den || 0)

  if (from && to) return `${from.toLocaleString('vi-VN')} - ${to.toLocaleString('vi-VN')} đ`
  if (from) return `${from.toLocaleString('vi-VN')} đ`
  return 'Thỏa thuận'
}

watch(() => route.params.id, loadIndustryDetail)
onMounted(loadIndustryDetail)
</script>

<template>
  <section class="py-14 lg:py-16">
    <div class="mx-auto max-w-7xl px-6">
      <div v-if="loading" class="space-y-6">
        <div class="h-72 animate-pulse rounded-[32px] bg-slate-200/70 dark:bg-slate-800/70"></div>
        <div class="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <div class="h-96 animate-pulse rounded-3xl bg-slate-200/70 dark:bg-slate-800/70"></div>
          <div class="h-96 animate-pulse rounded-3xl bg-slate-200/70 dark:bg-slate-800/70"></div>
        </div>
      </div>

      <div v-else-if="industry" class="space-y-8">
        <div class="rounded-[32px] border border-slate-200 bg-gradient-to-br from-white via-blue-50 to-indigo-100 p-8 shadow-xl dark:border-slate-800 dark:from-slate-900 dark:via-slate-900 dark:to-slate-800">
          <div class="flex flex-col gap-8 lg:flex-row lg:items-start lg:justify-between">
            <div class="min-w-0">
              <div class="flex flex-wrap items-center gap-3 text-sm font-semibold text-slate-500 dark:text-slate-400">
                <RouterLink to="/" class="hover:text-[#2463eb]">Trang chủ</RouterLink>
                <span>/</span>
                <RouterLink to="/jobs" class="hover:text-[#2463eb]">Việc làm</RouterLink>
                <template v-if="parentIndustry">
                  <span>/</span>
                  <RouterLink
                    :to="`/industries/${parentIndustry.id}`"
                    class="hover:text-[#2463eb]"
                  >
                    {{ parentIndustry.ten_nganh }}
                  </RouterLink>
                </template>
              </div>

              <p class="mt-5 text-sm font-bold uppercase tracking-[0.35em] text-[#2463eb]">Khám phá ngành nghề</p>
              <h1 class="mt-3 text-3xl font-black tracking-tight text-slate-900 dark:text-white lg:text-4xl">
                {{ industryName }}
              </h1>
              <p class="mt-5 max-w-3xl text-base leading-8 text-slate-600 dark:text-slate-400">
                {{ industryDescription }}
              </p>

              <div class="mt-6 flex flex-wrap gap-3">
                <RouterLink
                  :to="{ path: '/jobs', query: { nganh_nghe_id: industry.id } }"
                  class="rounded-xl bg-[#2463eb] px-5 py-3 text-sm font-bold text-white transition hover:bg-blue-700"
                >
                  Xem việc theo ngành
                </RouterLink>
                <RouterLink
                  to="/industries"
                  class="rounded-xl border border-slate-200 px-5 py-3 text-sm font-bold text-slate-700 transition hover:border-[#2463eb] hover:text-[#2463eb] dark:border-slate-700 dark:text-slate-200"
                >
                  Xem danh mục ngành
                </RouterLink>
                <RouterLink
                  to="/companies"
                  class="rounded-xl border border-slate-200 px-5 py-3 text-sm font-bold text-slate-700 transition hover:border-[#2463eb] hover:text-[#2463eb] dark:border-slate-700 dark:text-slate-200"
                >
                  Khám phá doanh nghiệp
                </RouterLink>
              </div>
            </div>

            <div class="grid gap-4 sm:grid-cols-3 lg:min-w-[340px] lg:grid-cols-1">
              <div class="rounded-2xl border border-slate-200 bg-white/85 p-4 dark:border-slate-700 dark:bg-slate-900/70">
                <p class="text-xs font-bold uppercase tracking-[0.3em] text-slate-400">Việc đang mở</p>
                <p class="mt-3 text-3xl font-black text-slate-900 dark:text-white">{{ openJobsCount }}</p>
              </div>
              <div class="rounded-2xl border border-slate-200 bg-white/85 p-4 dark:border-slate-700 dark:bg-slate-900/70">
                <p class="text-xs font-bold uppercase tracking-[0.3em] text-slate-400">Nhóm ngành</p>
                <p class="mt-3 text-base font-semibold text-slate-900 dark:text-white">
                  {{ parentIndustry?.ten_nganh || 'Ngành gốc' }}
                </p>
              </div>
              <div class="rounded-2xl border border-slate-200 bg-white/85 p-4 dark:border-slate-700 dark:bg-slate-900/70">
                <p class="text-xs font-bold uppercase tracking-[0.3em] text-slate-400">Ngành con</p>
                <p class="mt-3 text-base font-semibold text-slate-900 dark:text-white">{{ childIndustries.length }}</p>
              </div>
            </div>
          </div>
        </div>

        <div class="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <div class="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm dark:border-slate-800 dark:bg-slate-900">
            <div class="flex items-center justify-between gap-4">
              <div>
                <h2 class="text-2xl font-bold text-slate-900 dark:text-white">Việc làm thuộc ngành này</h2>
                <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">Các vị trí đang hoạt động được gắn với ngành nghề hiện tại.</p>
              </div>
              <RouterLink
                :to="{ path: '/jobs', query: { nganh_nghe_id: industry.id } }"
                class="hidden rounded-xl border border-slate-200 px-4 py-2 text-sm font-bold text-slate-700 transition hover:border-[#2463eb] hover:text-[#2463eb] dark:border-slate-700 dark:text-slate-200 lg:inline-flex"
              >
                Xem tất cả
              </RouterLink>
            </div>

            <div v-if="industryJobs.length" class="mt-6 space-y-4">
              <div
                v-for="job in industryJobs"
                :key="job.id"
                class="rounded-2xl border border-slate-200 p-5 transition hover:border-[#2463eb]/40 dark:border-slate-800"
              >
                <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <h3 class="text-lg font-bold text-slate-900 dark:text-white">{{ job.tieu_de }}</h3>
                    <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
                      {{ job.cong_ty?.ten_cong_ty || 'Doanh nghiệp đang cập nhật' }} • {{ job.dia_diem_lam_viec || 'Linh hoạt' }}
                    </p>
                  </div>
                  <span class="rounded-full bg-blue-50 px-3 py-1 text-sm font-bold text-[#2463eb] dark:bg-slate-800 dark:text-blue-300">
                    {{ formatSalary(job) }}
                  </span>
                </div>

                <p class="mt-4 line-clamp-3 text-sm leading-7 text-slate-600 dark:text-slate-400">
                  {{ job.mo_ta_cong_viec || 'Mô tả công việc đang được cập nhật.' }}
                </p>

                <div class="mt-4 flex flex-wrap gap-2">
                  <span
                    v-for="item in job.nganh_nghes || []"
                    :key="`${job.id}-${item.id}`"
                    class="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-600 dark:bg-slate-800 dark:text-slate-300"
                  >
                    {{ item.ten_nganh }}
                  </span>
                </div>

                <div class="mt-5">
                  <RouterLink
                    :to="`/jobs/${job.id}`"
                    class="inline-flex rounded-xl bg-slate-900 px-4 py-2 text-sm font-bold text-white transition hover:bg-[#2463eb] dark:bg-white dark:text-slate-900 dark:hover:bg-[#2463eb] dark:hover:text-white"
                  >
                    Xem chi tiết
                  </RouterLink>
                </div>
              </div>
            </div>

            <div v-else class="mt-6 rounded-2xl border border-dashed border-slate-300 p-6 text-sm text-slate-500 dark:border-slate-700 dark:text-slate-400">
              Hiện chưa có tin tuyển dụng hoạt động nào gắn với ngành nghề này.
            </div>
          </div>

          <div class="space-y-6">
            <div class="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm dark:border-slate-800 dark:bg-slate-900">
              <h2 class="text-xl font-bold text-slate-900 dark:text-white">Ngành liên quan</h2>

              <div v-if="parentIndustry" class="mt-5 rounded-2xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-950">
                <p class="text-xs font-bold uppercase tracking-[0.25em] text-slate-400">Danh mục cha</p>
                <RouterLink
                  :to="`/industries/${parentIndustry.id}`"
                  class="mt-2 inline-flex text-base font-semibold text-slate-900 hover:text-[#2463eb] dark:text-white"
                >
                  {{ parentIndustry.ten_nganh }}
                </RouterLink>
              </div>

              <div class="mt-5">
                <p class="text-xs font-bold uppercase tracking-[0.25em] text-slate-400">Ngành con</p>
                <div v-if="childIndustries.length" class="mt-3 flex flex-wrap gap-3">
                  <RouterLink
                    v-for="child in childIndustries"
                    :key="child.id"
                    :to="`/industries/${child.id}`"
                    class="rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-[#2463eb] hover:text-[#2463eb] dark:border-slate-700 dark:text-slate-200"
                  >
                    {{ child.ten_nganh }}
                  </RouterLink>
                </div>
                <p v-else class="mt-3 text-sm text-slate-500 dark:text-slate-400">
                  Chưa có ngành con được công bố cho danh mục này.
                </p>
              </div>
            </div>

            <div class="rounded-3xl border border-slate-200 bg-gradient-to-br from-[#2463eb] to-indigo-500 p-8 text-white shadow-xl dark:border-slate-800">
              <p class="text-sm font-bold uppercase tracking-[0.35em] text-white/70">Khám phá sâu hơn</p>
              <h3 class="mt-4 text-2xl font-black">Tìm cơ hội theo đúng năng lực</h3>
              <p class="mt-3 text-sm leading-7 text-white/80">
                Dùng semantic search để mô tả vị trí bạn muốn bằng ngôn ngữ tự nhiên, sau đó so sánh với các job trong ngành này.
              </p>
              <div class="mt-6 flex flex-wrap gap-3">
                <RouterLink
                  :to="{ path: '/jobs', query: { nganh_nghe_id: industry.id } }"
                  class="rounded-xl bg-white px-4 py-3 text-sm font-bold text-[#2463eb] transition hover:bg-slate-100"
                >
                  Xem việc theo ngành
                </RouterLink>
                <RouterLink
                  to="/jobs"
                  class="rounded-xl border border-white/30 px-4 py-3 text-sm font-bold text-white transition hover:bg-white/10"
                >
                  Mở trang tìm việc
                </RouterLink>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="rounded-3xl border border-dashed border-slate-300 p-12 text-center dark:border-slate-700">
        <p class="text-lg font-semibold text-slate-700 dark:text-slate-300">Không tìm thấy thông tin ngành nghề.</p>
        <RouterLink to="/jobs" class="mt-4 inline-flex rounded-xl bg-[#2463eb] px-5 py-3 text-sm font-bold text-white">
          Quay lại tìm việc
        </RouterLink>
      </div>
    </div>
  </section>
</template>
