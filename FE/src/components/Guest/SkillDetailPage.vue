<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { jobService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'

const route = useRoute()
const notify = useNotify()

const loading = ref(false)
const skill = ref(null)
const skillJobs = ref([])
const relatedSkills = ref([])

const extractList = (response) => {
  const payload = response?.data
  if (Array.isArray(payload?.data)) return payload.data
  if (Array.isArray(payload)) return payload
  return []
}

const loadSkillDetail = async () => {
  loading.value = true

  try {
    const skillResponse = await jobService.getSkillById(route.params.id)
    const skillPayload = skillResponse?.data || null
    skill.value = skillPayload

    if (!skillPayload) {
      skillJobs.value = []
      relatedSkills.value = []
      return
    }

    const [jobsResponse, relatedSkillsResponse] = await Promise.all([
      jobService.getJobs({
        search: skillPayload.ten_ky_nang,
        per_page: 6,
      }),
      jobService.getSkills({
        search: skillPayload.ten_ky_nang.split(/\s+/).slice(0, 1).join(' '),
        per_page: 8,
      }),
    ])

    skillJobs.value = extractList(jobsResponse)
    relatedSkills.value = extractList(relatedSkillsResponse)
      .filter((item) => item.id !== skillPayload.id)
      .slice(0, 6)
  } catch (error) {
    skill.value = null
    skillJobs.value = []
    relatedSkills.value = []
    notify.apiError(error, 'Không tải được thông tin kỹ năng.')
  } finally {
    loading.value = false
  }
}

const skillName = computed(() => skill.value?.ten_ky_nang || 'Kỹ năng')
const skillDescription = computed(() => skill.value?.mo_ta || 'Kỹ năng này đang được cập nhật thêm mô tả và ngữ cảnh sử dụng trong tuyển dụng.')
const openJobsCount = computed(() => skillJobs.value.length)

const formatSalary = (job) => {
  const from = Number(job?.muc_luong_tu || 0)
  const to = Number(job?.muc_luong_den || 0)

  if (from && to) return `${from.toLocaleString('vi-VN')} - ${to.toLocaleString('vi-VN')} đ`
  if (from) return `${from.toLocaleString('vi-VN')} đ`
  return 'Thỏa thuận'
}

watch(() => route.params.id, loadSkillDetail)
onMounted(loadSkillDetail)
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

      <div v-else-if="skill" class="space-y-8">
        <div class="rounded-[32px] border border-slate-200 bg-gradient-to-br from-white via-blue-50 to-indigo-100 p-8 shadow-xl dark:border-slate-800 dark:from-slate-900 dark:via-slate-900 dark:to-slate-800">
          <div class="flex flex-col gap-8 lg:flex-row lg:items-start lg:justify-between">
            <div class="min-w-0">
              <div class="flex flex-wrap items-center gap-3 text-sm font-semibold text-slate-500 dark:text-slate-400">
                <RouterLink to="/" class="hover:text-[#2463eb]">Trang chủ</RouterLink>
                <span>/</span>
                <RouterLink to="/jobs" class="hover:text-[#2463eb]">Việc làm</RouterLink>
                <span>/</span>
                <span>{{ skillName }}</span>
              </div>

              <p class="mt-5 text-sm font-bold uppercase tracking-[0.35em] text-[#2463eb]">Khám phá kỹ năng</p>
              <h1 class="mt-3 text-3xl font-black tracking-tight text-slate-900 dark:text-white lg:text-4xl">
                {{ skillName }}
              </h1>
              <p class="mt-5 max-w-3xl text-base leading-8 text-slate-600 dark:text-slate-400">
                {{ skillDescription }}
              </p>

              <div class="mt-6 flex flex-wrap gap-3">
                <RouterLink
                  :to="{ path: '/jobs', query: { search: skillName } }"
                  class="rounded-xl bg-[#2463eb] px-5 py-3 text-sm font-bold text-white transition hover:bg-blue-700"
                >
                  Tìm việc theo kỹ năng
                </RouterLink>
                <RouterLink
                  to="/skills"
                  class="rounded-xl border border-slate-200 px-5 py-3 text-sm font-bold text-slate-700 transition hover:border-[#2463eb] hover:text-[#2463eb] dark:border-slate-700 dark:text-slate-200"
                >
                  Xem danh mục kỹ năng
                </RouterLink>
                <RouterLink
                  to="/jobs"
                  class="rounded-xl border border-slate-200 px-5 py-3 text-sm font-bold text-slate-700 transition hover:border-[#2463eb] hover:text-[#2463eb] dark:border-slate-700 dark:text-slate-200"
                >
                  Mở trang việc làm
                </RouterLink>
              </div>
            </div>

            <div class="grid gap-4 sm:grid-cols-3 lg:min-w-[340px] lg:grid-cols-1">
              <div class="rounded-2xl border border-slate-200 bg-white/85 p-4 dark:border-slate-700 dark:bg-slate-900/70">
                <p class="text-xs font-bold uppercase tracking-[0.3em] text-slate-400">Việc liên quan</p>
                <p class="mt-3 text-3xl font-black text-slate-900 dark:text-white">{{ openJobsCount }}</p>
              </div>
              <div class="rounded-2xl border border-slate-200 bg-white/85 p-4 dark:border-slate-700 dark:bg-slate-900/70">
                <p class="text-xs font-bold uppercase tracking-[0.3em] text-slate-400">Kỹ năng liên quan</p>
                <p class="mt-3 text-base font-semibold text-slate-900 dark:text-white">{{ relatedSkills.length }}</p>
              </div>
              <div class="rounded-2xl border border-slate-200 bg-white/85 p-4 dark:border-slate-700 dark:bg-slate-900/70">
                <p class="text-xs font-bold uppercase tracking-[0.3em] text-slate-400">Ứng dụng</p>
                <p class="mt-3 text-base font-semibold text-slate-900 dark:text-white">Tìm việc, matching, CV parse</p>
              </div>
            </div>
          </div>
        </div>

        <div class="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <div class="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm dark:border-slate-800 dark:bg-slate-900">
            <div class="flex items-center justify-between gap-4">
              <div>
                <h2 class="text-2xl font-bold text-slate-900 dark:text-white">Việc làm liên quan đến kỹ năng này</h2>
                <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">Các job được tìm thấy theo tên kỹ năng để bạn khám phá nhanh hơn.</p>
              </div>
              <RouterLink
                :to="{ path: '/jobs', query: { search: skillName } }"
                class="hidden rounded-xl border border-slate-200 px-4 py-2 text-sm font-bold text-slate-700 transition hover:border-[#2463eb] hover:text-[#2463eb] dark:border-slate-700 dark:text-slate-200 lg:inline-flex"
              >
                Xem tất cả
              </RouterLink>
            </div>

            <div v-if="skillJobs.length" class="mt-6 space-y-4">
              <div
                v-for="job in skillJobs"
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

                <div class="mt-4">
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
              Hiện chưa tìm thấy job phù hợp trực tiếp theo từ khóa kỹ năng này.
            </div>
          </div>

          <div class="space-y-6">
            <div class="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm dark:border-slate-800 dark:bg-slate-900">
              <h2 class="text-xl font-bold text-slate-900 dark:text-white">Kỹ năng liên quan</h2>
              <div v-if="relatedSkills.length" class="mt-5 flex flex-wrap gap-3">
                <RouterLink
                  v-for="item in relatedSkills"
                  :key="item.id"
                  :to="`/skills/${item.id}`"
                  class="rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-[#2463eb] hover:text-[#2463eb] dark:border-slate-700 dark:text-slate-200"
                >
                  {{ item.ten_ky_nang }}
                </RouterLink>
              </div>
              <p v-else class="mt-5 text-sm text-slate-500 dark:text-slate-400">
                Chưa có thêm kỹ năng liên quan để gợi ý.
              </p>
            </div>

            <div class="rounded-3xl border border-slate-200 bg-gradient-to-br from-[#2463eb] to-indigo-500 p-8 text-white shadow-xl dark:border-slate-800">
              <p class="text-sm font-bold uppercase tracking-[0.35em] text-white/70">Gợi ý hành động</p>
              <h3 class="mt-4 text-2xl font-black">Tìm việc theo kỹ năng nổi bật</h3>
              <p class="mt-3 text-sm leading-7 text-white/80">
                Lọc danh sách việc làm theo kỹ năng này, sau đó kết hợp thêm ngành nghề, cấp bậc hoặc địa điểm để tìm vị trí phù hợp hơn.
              </p>
              <div class="mt-6 flex flex-wrap gap-3">
                <RouterLink
                  :to="{ path: '/jobs', query: { search: skillName } }"
                  class="rounded-xl bg-white px-4 py-3 text-sm font-bold text-[#2463eb] transition hover:bg-slate-100"
                >
                  Tìm việc theo kỹ năng
                </RouterLink>
                <RouterLink
                  to="/ai-career"
                  class="rounded-xl border border-white/30 px-4 py-3 text-sm font-bold text-white transition hover:bg-white/10"
                >
                  Xem AI tư vấn
                </RouterLink>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="rounded-3xl border border-dashed border-slate-300 p-12 text-center dark:border-slate-700">
        <p class="text-lg font-semibold text-slate-700 dark:text-slate-300">Không tìm thấy thông tin kỹ năng.</p>
        <RouterLink to="/jobs" class="mt-4 inline-flex rounded-xl bg-[#2463eb] px-5 py-3 text-sm font-bold text-white">
          Quay lại tìm việc
        </RouterLink>
      </div>
    </div>
  </section>
</template>
