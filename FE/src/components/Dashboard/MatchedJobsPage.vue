<script setup>
import { computed, onMounted, ref } from 'vue'
import { jobService, matchingService, profileService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'

const notify = useNotify()
const loadingProfiles = ref(false)
const loadingMatches = ref(false)
const refreshing = ref(false)
const profiles = ref([])
const matches = ref([])
const selectedProfileId = ref('')

const selectedProfile = computed(() =>
  profiles.value.find((item) => Number(item.id) === Number(selectedProfileId.value)) || null
)

const loadProfiles = async () => {
  loadingProfiles.value = true
  try {
    const response = await profileService.getProfiles({ per_page: 100 })
    profiles.value = response?.data?.data || []
    if (!selectedProfileId.value && profiles.value.length) {
      selectedProfileId.value = String(profiles.value[0].id)
    }
  } catch (error) {
    notify.apiError(error, 'Không thể tải hồ sơ để matching.')
  } finally {
    loadingProfiles.value = false
  }
}

const loadMatches = async () => {
  if (!selectedProfileId.value) {
    matches.value = []
    return
  }

  loadingMatches.value = true
  try {
    const response = await matchingService.getMatchingResults({
      per_page: 20,
      ho_so_id: selectedProfileId.value,
    })
    matches.value = response?.data?.data || []
  } catch (error) {
    notify.apiError(error, 'Không thể tải kết quả matching.')
  } finally {
    loadingMatches.value = false
  }
}

const regenerateMatches = async () => {
  if (!selectedProfileId.value) {
    notify.warning('Bạn cần chọn một hồ sơ trước.')
    return
  }

  refreshing.value = true
  try {
    const jobsResponse = await jobService.getJobs({ per_page: 8 })
    const jobs = jobsResponse?.data?.data || []

    if (!jobs.length) {
      notify.warning('Hiện chưa có tin tuyển dụng hoạt động.')
      return
    }

    await Promise.allSettled(
      jobs.map((job) => matchingService.generateMatching(selectedProfileId.value, job.id))
    )

    await loadMatches()
    notify.success('Đã làm mới danh sách việc làm phù hợp.')
  } catch (error) {
    notify.apiError(error, 'Không thể sinh kết quả matching.')
  } finally {
    refreshing.value = false
  }
}

onMounted(async () => {
  await loadProfiles()
  await loadMatches()
})
</script>

<template>
  <section class="space-y-6">
    <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p class="text-xs uppercase tracking-[0.3em] text-blue-600">AI Matching</p>
          <h2 class="mt-2 text-3xl font-bold text-slate-900">Việc làm phù hợp</h2>
          <p class="mt-3 text-sm leading-6 text-slate-600">
            Chọn hồ sơ ứng viên rồi sinh danh sách công việc được AI so khớp từ dữ liệu tuyển dụng hiện có.
          </p>
        </div>

        <div class="flex flex-col gap-3 sm:flex-row">
          <select v-model="selectedProfileId" class="rounded-2xl border border-slate-200 px-4 py-3 outline-none focus:border-blue-400" :disabled="loadingProfiles" @change="loadMatches">
            <option value="" disabled>{{ loadingProfiles ? 'Đang tải hồ sơ...' : 'Chọn hồ sơ' }}</option>
            <option v-for="profile in profiles" :key="profile.id" :value="String(profile.id)">
              {{ profile.tieu_de_ho_so }}
            </option>
          </select>

          <button type="button" class="rounded-2xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800 disabled:opacity-60" :disabled="refreshing || !selectedProfileId" @click="regenerateMatches">
            {{ refreshing ? 'Đang tạo matching...' : 'Sinh việc làm phù hợp' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="selectedProfile" class="rounded-3xl border border-blue-200 bg-blue-50 px-6 py-5 text-sm text-blue-900">
      Hồ sơ đang xem: <strong>{{ selectedProfile.tieu_de_ho_so }}</strong>
    </div>

    <div v-if="loadingMatches" class="rounded-3xl border border-slate-200 bg-white px-6 py-10 text-sm text-slate-500 shadow-sm">
      Đang tải kết quả matching...
    </div>

    <div v-else-if="matches.length === 0" class="rounded-3xl border border-dashed border-slate-300 bg-white px-6 py-12 text-center text-sm text-slate-500 shadow-sm">
      Chưa có kết quả matching. Hãy chọn hồ sơ rồi bấm “Sinh việc làm phù hợp”.
    </div>

    <div v-else class="grid gap-4">
      <article v-for="item in matches" :key="item.id" class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <p class="text-xs uppercase tracking-[0.25em] text-blue-600">{{ item.tin_tuyen_dung?.cong_ty?.ten_cong_ty || 'Doanh nghiệp' }}</p>
            <h3 class="mt-2 text-2xl font-semibold text-slate-900">{{ item.tin_tuyen_dung?.tieu_de || 'Tin tuyển dụng' }}</h3>
            <p class="mt-2 text-sm text-slate-600">
              {{ item.tin_tuyen_dung?.dia_diem_lam_viec || 'Địa điểm đang cập nhật' }}
            </p>
            <p class="mt-4 text-sm leading-6 text-slate-600">{{ item.explanation || 'Kết quả được tính từ hồ sơ, kỹ năng và kinh nghiệm liên quan.' }}</p>
          </div>

          <div class="rounded-2xl bg-slate-900 px-5 py-4 text-center text-white">
            <p class="text-xs uppercase tracking-[0.25em] text-slate-300">Độ phù hợp</p>
            <p class="mt-2 text-3xl font-bold">{{ Number(item.diem_phu_hop || 0).toFixed(0) }}%</p>
          </div>
        </div>

        <div class="mt-5 grid gap-4 md:grid-cols-2">
          <div class="rounded-2xl bg-emerald-50 p-4">
            <p class="text-sm font-semibold text-emerald-800">Kỹ năng phù hợp</p>
            <div class="mt-3 flex flex-wrap gap-2">
              <span
                v-for="skill in item.matched_skills_json || []"
                :key="typeof skill === 'string' ? skill : skill.skill_name || skill.ten_ky_nang"
                class="rounded-full bg-emerald-100 px-3 py-1 text-xs font-medium text-emerald-800"
              >
                {{ typeof skill === 'string' ? skill : skill.skill_name || skill.ten_ky_nang || skill.name }}
              </span>
            </div>
          </div>

          <div class="rounded-2xl bg-amber-50 p-4">
            <p class="text-sm font-semibold text-amber-800">Kỹ năng còn thiếu</p>
            <div class="mt-3 flex flex-wrap gap-2">
              <span
                v-for="skill in item.missing_skills_json || []"
                :key="typeof skill === 'string' ? skill : skill.skill_name || skill.ten_ky_nang"
                class="rounded-full bg-amber-100 px-3 py-1 text-xs font-medium text-amber-800"
              >
                {{ typeof skill === 'string' ? skill : skill.skill_name || skill.ten_ky_nang || skill.name }}
              </span>
            </div>
          </div>
        </div>
      </article>
    </div>
  </section>
</template>
