<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { followCompanyService, jobService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'
import { connectPublicChannel, leaveRealtimeChannel } from '@/services/realtime'
import { getAuthToken, getStoredCandidate } from '@/utils/authStorage'

const route = useRoute()
const notify = useNotify()

const loading = ref(false)
const followSubmitting = ref(false)
const company = ref(null)
let followerChannelName = null

const hasAuthToken = computed(() => Boolean(getAuthToken()))
const currentUser = computed(() => getStoredCandidate())
const isCandidate = computed(() => hasAuthToken.value && currentUser.value?.vai_tro === 0)

const loadCompany = async () => {
  loading.value = true
  try {
    const response = await jobService.getCompanyById(route.params.id)
    company.value = response?.data || null
  } catch (error) {
    company.value = null
    notify.apiError(error, 'Không tải được thông tin công ty.')
  } finally {
    loading.value = false
  }
}

const formatSalary = (job) => {
  const from = Number(job?.muc_luong_tu || 0)
  const to = Number(job?.muc_luong_den || 0)

  if (from && to) return `${from.toLocaleString('vi-VN')} - ${to.toLocaleString('vi-VN')} đ`
  if (from) return `${from.toLocaleString('vi-VN')} đ`
  return 'Thỏa thuận'
}

const companyJobs = computed(() => company.value?.tin_tuyen_dungs || [])
const companyIndustry = computed(() => company.value?.nganh_nghe?.ten_nganh || 'Đang cập nhật')
const companyAddress = computed(() => company.value?.dia_chi || 'Đang cập nhật')
const companyWebsite = computed(() => company.value?.website || '')
const companyEmail = computed(() => company.value?.email || company.value?.nguoi_dung?.email || '')
const companyScale = computed(() => company.value?.quy_mo || 'Đang cập nhật')
const openJobsCount = computed(() => company.value?.so_tin_dang_hoat_dong || companyJobs.value.length || 0)
const followerCount = computed(() => Number(company.value?.so_nguoi_theo_doi || 0))
const isFollowed = computed(() => Boolean(company.value?.da_theo_doi))

const toggleFollowCompany = async () => {
  if (!company.value?.id || followSubmitting.value) return

  if (!isCandidate.value) {
    notify.warning('Vui lòng đăng nhập bằng tài khoản ứng viên để theo dõi công ty.')
    return
  }

  followSubmitting.value = true
  try {
    const response = await followCompanyService.toggleFollowCompany(company.value.id)
    const payload = response?.data || {}
    const followed = Boolean(payload?.trang_thai_theo_doi)

    company.value = {
      ...company.value,
      da_theo_doi: followed,
      so_nguoi_theo_doi: Number(payload?.so_nguoi_theo_doi || 0),
    }

    if (followed) {
      notify.success('Đã theo dõi công ty. Bạn sẽ nhận thông báo khi có job mới.')
    } else {
      notify.info('Đã bỏ theo dõi công ty.')
    }
  } catch (error) {
    notify.apiError(error, 'Không thể cập nhật trạng thái theo dõi công ty.')
  } finally {
    followSubmitting.value = false
  }
}

const subscribeFollowerChannel = (companyId) => {
  if (!companyId) return

  followerChannelName = `company.public.${companyId}`

  connectPublicChannel(followerChannelName)?.listen('.company.followers.updated', (payload) => {
    const followerCount = Number(payload?.follower_count)

    if (!Number.isFinite(followerCount) || !company.value) return

    company.value = {
      ...company.value,
      so_nguoi_theo_doi: followerCount,
    }
  })
}

watch(() => route.params.id, loadCompany)
onMounted(loadCompany)

watch(
  () => company.value?.id,
  (nextCompanyId, previousCompanyId) => {
    if (previousCompanyId) {
      leaveRealtimeChannel(`company.public.${previousCompanyId}`)
    }

    followerChannelName = null

    if (nextCompanyId) {
      subscribeFollowerChannel(nextCompanyId)
    }
  },
)

onUnmounted(() => {
  if (followerChannelName) {
    leaveRealtimeChannel(followerChannelName)
  }
})
</script>

<template>
  <section class="py-14 lg:py-16">
    <div class="mx-auto max-w-7xl px-6">
      <div v-if="loading" class="space-y-6">
        <div class="h-72 animate-pulse rounded-3xl bg-slate-200/70 dark:bg-slate-800/70"></div>
        <div class="grid gap-6 lg:grid-cols-[1.3fr_0.7fr]">
          <div class="h-96 animate-pulse rounded-3xl bg-slate-200/70 dark:bg-slate-800/70"></div>
          <div class="h-96 animate-pulse rounded-3xl bg-slate-200/70 dark:bg-slate-800/70"></div>
        </div>
      </div>

      <div v-else-if="company" class="space-y-8">
        <div class="rounded-[32px] border border-slate-200 bg-gradient-to-br from-white via-blue-50 to-indigo-100 p-8 shadow-xl dark:border-slate-800 dark:from-slate-900 dark:via-slate-900 dark:to-slate-800">
          <div class="flex flex-col gap-8 lg:flex-row lg:items-start lg:justify-between">
            <div class="flex min-w-0 gap-5">
              <img
                v-if="company.logo_url"
                :src="company.logo_url"
                :alt="company.ten_cong_ty"
                class="h-24 w-24 rounded-3xl object-cover ring-1 ring-slate-200 dark:ring-slate-700"
              />
              <div
                v-else
                class="flex h-24 w-24 items-center justify-center rounded-3xl bg-[#2463eb]/10 text-3xl font-black text-[#2463eb]"
              >
                {{ company.ten_cong_ty?.slice(0, 1) }}
              </div>

              <div class="min-w-0">
                <p class="text-sm font-bold uppercase tracking-[0.35em] text-[#2463eb]">Doanh nghiệp nổi bật</p>
                <h1 class="mt-3 text-3xl font-black tracking-tight text-slate-900 dark:text-white lg:text-4xl">
                  {{ company.ten_cong_ty }}
                </h1>
                <div class="mt-4 flex flex-wrap items-center gap-3 text-sm font-medium text-slate-600 dark:text-slate-400">
                  <RouterLink
                    v-if="company.nganh_nghe?.id"
                    :to="`/industries/${company.nganh_nghe.id}`"
                    class="rounded-full bg-white/80 px-3 py-1.5 transition hover:text-[#2463eb] dark:bg-slate-800/80"
                  >
                    {{ companyIndustry }}
                  </RouterLink>
                  <span
                    v-else
                    class="rounded-full bg-white/80 px-3 py-1.5 dark:bg-slate-800/80"
                  >
                    {{ companyIndustry }}
                  </span>
                  <span class="rounded-full bg-white/80 px-3 py-1.5 dark:bg-slate-800/80">{{ companyScale }}</span>
                  <span class="rounded-full bg-white/80 px-3 py-1.5 dark:bg-slate-800/80">{{ companyAddress }}</span>
                </div>
                <p class="mt-5 max-w-3xl text-base leading-8 text-slate-600 dark:text-slate-400">
                  {{ company.mo_ta || 'Doanh nghiệp đang cập nhật thêm thông tin giới thiệu.' }}
                </p>
              </div>
            </div>

            <div class="grid gap-4 sm:grid-cols-3 lg:min-w-[320px] lg:grid-cols-1">
              <div class="rounded-2xl border border-slate-200 bg-white/85 p-4 dark:border-slate-700 dark:bg-slate-900/70">
                <p class="text-xs font-bold uppercase tracking-[0.3em] text-slate-400">Tin đang mở</p>
                <p class="mt-3 text-3xl font-black text-slate-900 dark:text-white">{{ openJobsCount }}</p>
              </div>
              <div class="rounded-2xl border border-slate-200 bg-white/85 p-4 dark:border-slate-700 dark:bg-slate-900/70">
                <p class="text-xs font-bold uppercase tracking-[0.3em] text-slate-400">Người theo dõi</p>
                <p class="mt-3 text-3xl font-black text-slate-900 dark:text-white">{{ followerCount }}</p>
              </div>
              <div class="rounded-2xl border border-slate-200 bg-white/85 p-4 dark:border-slate-700 dark:bg-slate-900/70">
                <p class="text-xs font-bold uppercase tracking-[0.3em] text-slate-400">Liên hệ</p>
                <p class="mt-3 break-all text-sm font-semibold text-slate-900 dark:text-white">
                  {{ companyEmail || 'Đang cập nhật' }}
                </p>
              </div>
            </div>

            <div class="flex flex-wrap gap-3 lg:max-w-[320px] lg:justify-end">
              <button
                class="rounded-2xl px-5 py-4 text-center text-sm font-bold transition"
                :class="isFollowed
                  ? 'border border-emerald-200 bg-emerald-50 text-emerald-700 hover:bg-emerald-100'
                  : 'border border-[#2463eb]/20 bg-[#2463eb] text-white hover:bg-blue-700'"
                type="button"
                @click="toggleFollowCompany"
              >
                {{
                  followSubmitting
                    ? 'Đang xử lý...'
                    : isFollowed
                      ? 'Đang theo dõi'
                      : 'Theo dõi công ty'
                }}
              </button>
              <a
                v-if="companyWebsite"
                :href="companyWebsite"
                target="_blank"
                rel="noreferrer"
                class="rounded-2xl border border-slate-200 bg-white/85 px-5 py-4 text-center text-sm font-bold text-slate-700 transition hover:border-[#2463eb] hover:text-[#2463eb] dark:border-slate-700 dark:bg-slate-900/70 dark:text-white"
              >
                Truy cập website
              </a>
            </div>
          </div>
        </div>

        <div class="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <div class="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm dark:border-slate-800 dark:bg-slate-900">
            <div class="flex items-center justify-between gap-4">
              <div>
                <h2 class="text-2xl font-bold text-slate-900 dark:text-white">Tin tuyển dụng đang mở</h2>
                <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">Khám phá các vị trí mới nhất từ doanh nghiệp này.</p>
              </div>
              <RouterLink
                :to="{ path: '/jobs', query: { search: company.ten_cong_ty } }"
                class="hidden rounded-xl border border-slate-200 px-4 py-2 text-sm font-bold text-slate-700 transition hover:border-[#2463eb] hover:text-[#2463eb] dark:border-slate-700 dark:text-slate-200 lg:inline-flex"
              >
                Xem tất cả job
              </RouterLink>
            </div>

            <div v-if="companyJobs.length" class="mt-6 space-y-4">
              <div
                v-for="job in companyJobs"
                :key="job.id"
                class="rounded-2xl border border-slate-200 p-5 transition hover:border-[#2463eb]/40 dark:border-slate-800"
              >
                <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <h3 class="text-lg font-bold text-slate-900 dark:text-white">{{ job.tieu_de }}</h3>
                    <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
                      {{ job.dia_diem_lam_viec || 'Linh hoạt' }} • {{ job.hinh_thuc_lam_viec || 'Đang cập nhật' }}
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
              Công ty này hiện chưa có tin tuyển dụng đang hoạt động.
            </div>
          </div>

          <div class="space-y-6">
            <div class="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm dark:border-slate-800 dark:bg-slate-900">
              <h2 class="text-xl font-bold text-slate-900 dark:text-white">Thông tin nhanh</h2>
              <div class="mt-6 space-y-4 text-sm text-slate-600 dark:text-slate-400">
                <div>
                  <p class="font-bold uppercase tracking-[0.25em] text-slate-400">Ngành nghề</p>
                  <RouterLink
                    v-if="company.nganh_nghe?.id"
                    :to="`/industries/${company.nganh_nghe.id}`"
                    class="mt-2 inline-flex text-base font-semibold text-slate-900 hover:text-[#2463eb] dark:text-white"
                  >
                    {{ companyIndustry }}
                  </RouterLink>
                  <p v-else class="mt-2 text-base font-semibold text-slate-900 dark:text-white">{{ companyIndustry }}</p>
                </div>
                <div>
                  <p class="font-bold uppercase tracking-[0.25em] text-slate-400">Quy mô</p>
                  <p class="mt-2 text-base font-semibold text-slate-900 dark:text-white">{{ companyScale }}</p>
                </div>
                <div>
                  <p class="font-bold uppercase tracking-[0.25em] text-slate-400">Địa chỉ</p>
                  <p class="mt-2 text-base font-semibold text-slate-900 dark:text-white">{{ companyAddress }}</p>
                </div>
                <div>
                  <p class="font-bold uppercase tracking-[0.25em] text-slate-400">Người theo dõi</p>
                  <p class="mt-2 text-base font-semibold text-slate-900 dark:text-white">{{ followerCount }}</p>
                </div>
                <div v-if="companyEmail">
                  <p class="font-bold uppercase tracking-[0.25em] text-slate-400">Email</p>
                  <p class="mt-2 break-all text-base font-semibold text-slate-900 dark:text-white">{{ companyEmail }}</p>
                </div>
              </div>
            </div>

            <div class="rounded-3xl border border-slate-200 bg-gradient-to-br from-[#2463eb] to-indigo-500 p-8 text-white shadow-xl dark:border-slate-800">
              <p class="text-sm font-bold uppercase tracking-[0.35em] text-white/70">Gợi ý hành động</p>
              <h3 class="mt-4 text-2xl font-black">Khám phá thêm cơ hội phù hợp</h3>
              <p class="mt-3 text-sm leading-7 text-white/80">
                Tìm thêm việc làm của công ty hoặc lọc theo kỹ năng, ngành nghề và địa điểm để chọn vị trí phù hợp hơn.
              </p>
              <div class="mt-6 flex flex-wrap gap-3">
                <RouterLink
                  :to="{ path: '/jobs', query: { search: company.ten_cong_ty } }"
                  class="rounded-xl bg-white px-4 py-3 text-sm font-bold text-[#2463eb] transition hover:bg-slate-100"
                >
                  Xem việc của công ty
                </RouterLink>
                <RouterLink
                  to="/jobs"
                  class="rounded-xl border border-white/30 px-4 py-3 text-sm font-bold text-white transition hover:bg-white/10"
                >
                  Tìm việc khác
                </RouterLink>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="rounded-3xl border border-dashed border-slate-300 p-12 text-center dark:border-slate-700">
        <p class="text-lg font-semibold text-slate-700 dark:text-slate-300">Không tìm thấy thông tin công ty.</p>
        <RouterLink to="/" class="mt-4 inline-flex rounded-xl bg-[#2463eb] px-5 py-3 text-sm font-bold text-white">
          Quay lại trang chủ
        </RouterLink>
      </div>
    </div>
  </section>
</template>
