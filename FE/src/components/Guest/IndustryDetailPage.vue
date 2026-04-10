<template>
  <div
    class="relative isolate min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(37,99,235,0.10),_transparent_30%),linear-gradient(180deg,#f8fbff_0%,#eef4ff_45%,#f8fafc_100%)]"
  >
    <section class="py-14 lg:py-16">
      <div class="mx-auto max-w-7xl px-6">

        <!-- Loading skeleton -->
        <div v-if="loading" class="space-y-6">
          <div class="h-72 animate-pulse rounded-[32px] bg-slate-200/70"></div>
          <div class="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
            <div class="h-96 animate-pulse rounded-3xl bg-slate-200/70"></div>
            <div class="space-y-4">
              <div class="h-52 animate-pulse rounded-3xl bg-slate-200/70"></div>
              <div class="h-52 animate-pulse rounded-3xl bg-slate-200/70"></div>
            </div>
          </div>
        </div>

        <!-- Main content -->
        <div v-else-if="industry" class="space-y-8">

          <!-- Hero section -->
          <div
            class="rounded-[32px] border border-slate-200 bg-gradient-to-br from-white via-blue-50 to-indigo-100 p-8 shadow-xl"
          >
            <div class="flex flex-col gap-8 lg:flex-row lg:items-start lg:justify-between">
              <div class="min-w-0">
                <!-- Breadcrumb -->
                <nav class="flex flex-wrap items-center gap-2 text-sm font-semibold text-slate-500">
                  <RouterLink to="/" class="transition hover:text-[#2463eb]">Trang chủ</RouterLink>
                  <span class="text-slate-300">/</span>
                  <RouterLink to="/industries" class="transition hover:text-[#2463eb]">Ngành nghề</RouterLink>
                  <template v-if="parentIndustry">
                    <span class="text-slate-300">/</span>
                    <RouterLink
                      :to="`/industries/${parentIndustry.id}`"
                      class="transition hover:text-[#2463eb]"
                    >
                      {{ parentIndustry.ten_nganh }}
                    </RouterLink>
                  </template>
                  <span class="text-slate-300">/</span>
                  <span class="text-slate-900">{{ industryName }}</span>
                </nav>

                <p class="mt-6 text-sm font-bold uppercase tracking-[0.35em] text-[#2463eb]">
                  Khám phá ngành nghề
                </p>
                <h1 class="mt-3 text-3xl font-black tracking-tight text-slate-900 lg:text-4xl">
                  {{ industryName }}
                </h1>
                <p class="mt-5 max-w-3xl text-base leading-8 text-slate-600">
                  {{ industryDescription }}
                </p>

                <div class="mt-6 flex flex-wrap gap-3">
                  <RouterLink
                    :to="{ path: '/jobs', query: { nganh_nghe_id: industry.id } }"
                    class="inline-flex items-center gap-2 rounded-xl bg-[#2463eb] px-5 py-3 text-sm font-bold text-white transition hover:bg-blue-700"
                  >
                    <span class="material-symbols-outlined text-[18px]">work</span>
                    Xem việc theo ngành
                  </RouterLink>
                  <RouterLink
                    to="/industries"
                    class="inline-flex items-center gap-2 rounded-xl border border-slate-200 px-5 py-3 text-sm font-bold text-slate-700 transition hover:border-[#2463eb] hover:text-[#2463eb]"
                  >
                    <span class="material-symbols-outlined text-[18px]">grid_view</span>
                    Danh mục ngành
                  </RouterLink>
                </div>
              </div>

              <!-- Stats cards -->
              <div class="grid gap-4 sm:grid-cols-3 lg:min-w-[340px] lg:grid-cols-1">
                <div class="rounded-2xl border border-slate-200 bg-white/85 p-5 shadow-sm">
                  <p class="text-xs font-bold uppercase tracking-[0.3em] text-slate-400">
                    Việc đang mở
                  </p>
                  <p class="mt-3 text-4xl font-black text-slate-900">{{ openJobsCount }}</p>
                </div>
                <div class="rounded-2xl border border-slate-200 bg-white/85 p-5 shadow-sm">
                  <p class="text-xs font-bold uppercase tracking-[0.3em] text-slate-400">
                    Nhóm ngành
                  </p>
                  <p class="mt-3 text-base font-semibold text-slate-900">
                    {{ parentIndustry?.ten_nganh || 'Ngành gốc' }}
                  </p>
                </div>
                <div class="rounded-2xl border border-slate-200 bg-white/85 p-5 shadow-sm">
                  <p class="text-xs font-bold uppercase tracking-[0.3em] text-slate-400">
                    Ngành con
                  </p>
                  <p class="mt-3 text-base font-semibold text-slate-900">
                    {{ childIndustries.length }}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Content + sidebar grid -->
          <div class="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">

            <!-- Jobs list panel -->
            <div class="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
              <h2 class="text-2xl font-bold text-slate-900">Việc làm thuộc ngành này</h2>

              <!-- Jobs -->
              <div v-if="industryJobs.length" class="mt-6 space-y-4">
                <div
                  v-for="job in industryJobs"
                  :key="job.id"
                  class="group rounded-2xl border border-slate-200 p-5 transition hover:border-[#2463eb]/40 hover:shadow-md"
                >
                  <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                    <div>
                      <h3 class="text-base font-bold text-slate-900 transition group-hover:text-[#2463eb]">
                        {{ job.tieu_de }}
                      </h3>
                      <p class="mt-1 text-sm text-slate-500">
                        {{ job.cong_ty?.ten_cong_ty || 'Doanh nghiệp đang cập nhật' }}
                        <span v-if="job.dia_diem_lam_viec"> · {{ job.dia_diem_lam_viec }}</span>
                      </p>
                    </div>
                    <span
                      class="shrink-0 rounded-full bg-blue-50 px-3 py-1 text-sm font-bold text-[#2463eb]"
                    >
                      {{ formatSalary(job) }}
                    </span>
                  </div>
                  <p class="mt-4 line-clamp-3 text-sm leading-7 text-slate-600">
                    {{ job.mo_ta_cong_viec || 'Mô tả công việc đang được cập nhật.' }}
                  </p>
                  <div class="mt-4 flex flex-wrap gap-2">
                    <span
                      v-for="item in job.nganh_nghes || []"
                      :key="`${job.id}-${item.id}`"
                      class="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-600"
                    >
                      {{ item.ten_nganh }}
                    </span>
                  </div>
                  <div class="mt-5">
                    <RouterLink
                      :to="`/jobs/${job.id}`"
                      class="inline-flex items-center gap-2 rounded-xl bg-slate-900 px-4 py-2 text-sm font-bold text-white transition hover:bg-[#2463eb]"
                    >
                      Xem chi tiết
                      <span class="material-symbols-outlined text-[16px]">arrow_forward</span>
                    </RouterLink>
                  </div>
                </div>
              </div>

              <!-- No jobs -->
              <div
                v-else
                class="mt-6 rounded-2xl border border-dashed border-slate-300 p-8 text-center"
              >
                <div class="mx-auto mb-4 flex size-14 items-center justify-center rounded-2xl bg-slate-100">
                  <span class="material-symbols-outlined text-2xl text-slate-400">work_off</span>
                </div>
                <p class="text-sm font-semibold text-slate-600">
                  Hiện chưa có tin tuyển dụng nào gắn với ngành nghề này.
                </p>
                <RouterLink
                  to="/jobs"
                  class="mt-4 inline-flex items-center gap-2 text-sm font-bold text-[#2463eb] hover:underline"
                >
                  Tìm kiếm tất cả việc làm
                  <span class="material-symbols-outlined text-[16px]">arrow_forward</span>
                </RouterLink>
              </div>
            </div>

            <!-- Right sidebar -->
            <div class="space-y-6">

              <!-- Related industries -->
              <div class="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
                <h2 class="text-xl font-bold text-slate-900">Ngành liên quan</h2>

                <!-- Parent -->
                <div v-if="parentIndustry" class="mt-5 rounded-2xl border border-slate-200 bg-slate-50 p-4">
                  <p class="text-xs font-bold uppercase tracking-[0.25em] text-slate-400">
                    Danh mục cha
                  </p>
                  <RouterLink
                    :to="`/industries/${parentIndustry.id}`"
                    class="mt-2 inline-flex items-center gap-2 text-base font-semibold text-slate-900 transition hover:text-[#2463eb]"
                  >
                    {{ parentIndustry.ten_nganh }}
                    <span class="material-symbols-outlined text-[16px]">arrow_forward</span>
                  </RouterLink>
                </div>

                <!-- Children -->
                <div class="mt-5">
                  <p class="text-xs font-bold uppercase tracking-[0.25em] text-slate-400">Ngành con</p>
                  <div v-if="childIndustries.length" class="mt-3 flex flex-wrap gap-3">
                    <RouterLink
                      v-for="child in childIndustries"
                      :key="child.id"
                      :to="`/industries/${child.id}`"
                      class="rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-[#2463eb] hover:text-[#2463eb]"
                    >
                      {{ child.ten_nganh }}
                    </RouterLink>
                  </div>
                  <p v-else class="mt-3 text-sm text-slate-500">
                    Chưa có ngành con được công bố.
                  </p>
                </div>
              </div>

              <!-- CTA banner -->
              <div
                class="rounded-3xl border bg-gradient-to-br from-[#2463eb] to-indigo-500 p-8 text-white shadow-xl"
              >
                <p class="text-sm font-bold uppercase tracking-[0.35em] text-white/70">
                  Khám phá sâu hơn
                </p>
                <h3 class="mt-4 text-2xl font-black">
                  Tìm cơ hội theo đúng năng lực
                </h3>
                <p class="mt-3 text-sm leading-7 text-white/80">
                  Sử dụng hệ thống tìm kiếm thông minh để mô tả vị trí bạn mong muốn bằng ngôn ngữ tự nhiên.
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

        <!-- Not found -->
        <div
          v-else
          class="rounded-3xl border border-dashed border-slate-300 p-12 text-center"
        >
          <div class="mx-auto mb-5 flex size-16 items-center justify-center rounded-2xl bg-slate-100">
            <span class="material-symbols-outlined text-3xl text-slate-400">search_off</span>
          </div>
          <p class="text-lg font-semibold text-slate-700">Không tìm thấy thông tin ngành nghề.</p>
          <p class="mt-2 text-sm text-slate-500">Ngành nghề này có thể đã bị ẩn hoặc không tồn tại.</p>
          <RouterLink
            to="/industries"
            class="mt-6 inline-flex items-center gap-2 rounded-xl bg-[#2463eb] px-5 py-3 text-sm font-bold text-white hover:bg-blue-700"
          >
            <span class="material-symbols-outlined text-[18px]">grid_view</span>
            Xem tất cả ngành nghề
          </RouterLink>
        </div>

      </div>
    </section>
  </div>
</template>

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
  industry.value = null
  industryJobs.value = []
  try {
    // Gọi song song: chi tiết ngành + danh sách việc theo ngành
    const [industryResponse, jobsResponse] = await Promise.all([
      jobService.getIndustryById(route.params.id),
      jobService.getJobs({ nganh_nghe_id: route.params.id, per_page: 6 }),
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
const industryDescription = computed(
  () => industry.value?.mo_ta || 'Ngành nghề này đang được cập nhật thêm mô tả chi tiết.'
)
const parentIndustry = computed(() => industry.value?.danh_muc_cha || null)
const childIndustries = computed(() =>
  Array.isArray(industry.value?.danh_muc_con) ? industry.value.danh_muc_con : []
)
const openJobsCount = computed(() => industryJobs.value.length)

const formatSalary = (job) => {
  const from = Number(job?.muc_luong_tu || 0)
  const to = Number(job?.muc_luong_den || 0)
  const single = Number(job?.muc_luong || 0)
  if (from && to) return `${from.toLocaleString('vi-VN')} - ${to.toLocaleString('vi-VN')} đ`
  if (single) return `${single.toLocaleString('vi-VN')} đ`
  return 'Thỏa thuận'
}

// Reload khi params.id thay đổi (e.g. navigate từ ngành con)
watch(() => route.params.id, (newId) => {
  if (newId) loadIndustryDetail()
})

onMounted(loadIndustryDetail)
</script>
