<script setup>
import { computed, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { employerCompanyService, employerJobService, jobService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'
import { connectPublicChannel, leaveRealtimeChannel } from '@/services/realtime'
import { getStoredEmployer } from '@/utils/authStorage'

const notify = useNotify()

const loading = ref(false)
const saving = ref(false)
const company = ref(null)
const industries = ref([])
const logoPreview = ref('')
const selectedLogoFile = ref(null)
const stats = ref({
  totalJobs: 0,
  activeJobs: 0,
})
let followerChannelName = null

const form = reactive({
  ten_cong_ty: '',
  ma_so_thue: '',
  email: '',
  dien_thoai: '',
  website: '',
  quy_mo: '',
  dia_chi: '',
  nganh_nghe_id: '',
  mo_ta: '',
  logo: '',
})

const hasCompany = computed(() => Boolean(company.value?.id))

const completionPercent = computed(() => {
  const fields = [
    form.ten_cong_ty,
    form.ma_so_thue,
    form.email,
    form.dien_thoai,
    form.website,
    form.quy_mo,
    form.dia_chi,
    form.nganh_nghe_id,
    form.mo_ta,
  ]
  const completed = fields.filter((value) => String(value || '').trim()).length
  return Math.round((completed / fields.length) * 100)
})

const currentIndustryLabel = computed(() => {
  const selected = industries.value.find((item) => Number(item.id) === Number(form.nganh_nghe_id))
  return selected?.ten_nganh || 'Chưa chọn ngành nghề'
})

const companyBadgeLabel = computed(() =>
  hasCompany.value ? 'Đã thiết lập' : 'Chưa thiết lập'
)

const companyBadgeTone = computed(() =>
  hasCompany.value
    ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
    : 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300'
)

const quickBenefits = computed(() => {
  const result = []
  if (form.quy_mo) result.push(`Quy mô doanh nghiệp: ${form.quy_mo} nhân sự`)
  if (form.website) result.push(`Website công ty: ${form.website}`)
  if (form.dia_chi) result.push(`Văn phòng: ${form.dia_chi}`)
  if (form.nganh_nghe_id) result.push(`Ngành chính: ${currentIndustryLabel.value}`)
  if (!result.length) {
    result.push('Bổ sung mô tả công ty, website và quy mô để hồ sơ doanh nghiệp thuyết phục hơn.')
  }
  return result.slice(0, 4)
})

const resetForm = () => {
  form.ten_cong_ty = ''
  form.ma_so_thue = ''
  form.email = ''
  form.dien_thoai = ''
  form.website = ''
  form.quy_mo = ''
  form.dia_chi = ''
  form.nganh_nghe_id = ''
  form.mo_ta = ''
  form.logo = ''
  logoPreview.value = ''
  selectedLogoFile.value = null
}

const fillForm = (payload) => {
  form.ten_cong_ty = payload?.ten_cong_ty || ''
  form.ma_so_thue = payload?.ma_so_thue || ''
  form.email = payload?.email || ''
  form.dien_thoai = payload?.dien_thoai || ''
  form.website = payload?.website || ''
  form.quy_mo = payload?.quy_mo || ''
  form.dia_chi = payload?.dia_chi || ''
  form.nganh_nghe_id = payload?.nganh_nghe_id ? String(payload.nganh_nghe_id) : ''
  form.mo_ta = payload?.mo_ta || ''
  form.logo = payload?.logo || ''
  logoPreview.value = payload?.logo_url || getLogoUrl(payload?.logo || '')
}

const getLogoUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `http://127.0.0.1:8000/storage/${path}`
}

const loadDraftCompany = () => {
  const draftRaw = window.sessionStorage.getItem('employer_company_draft')
  const employer = getStoredEmployer()

  let draft = null
  if (draftRaw) {
    try {
      draft = JSON.parse(draftRaw)
    } catch {
      draft = null
    }
  }

  fillForm({
    ten_cong_ty: draft?.ten_cong_ty || '',
    email: draft?.email || employer?.email || '',
    dien_thoai: draft?.dien_thoai || employer?.so_dien_thoai || '',
  })
}

const fetchIndustries = async () => {
  try {
    const response = await jobService.getIndustries({ per_page: 100 })
    industries.value = response?.data?.data || response?.data || []
  } catch (error) {
    notify.apiError(error, 'Không tải được danh mục ngành nghề.')
  }
}

const fetchCompany = async () => {
  loading.value = true
  try {
    const response = await employerCompanyService.getCompany()
    company.value = response?.data || null
    fillForm(company.value)
  } catch (error) {
    if (error?.status === 404) {
      company.value = null
      resetForm()
      loadDraftCompany()
    } else {
      notify.apiError(error, 'Không tải được thông tin công ty.')
    }
  } finally {
    loading.value = false
  }
}

const fetchStats = async () => {
  try {
    const response = await employerJobService.getJobs({ page: 1, per_page: 100 })
    const rows = response?.data?.data || []
    stats.value = {
      totalJobs: response?.data?.total || rows.length,
      activeJobs: rows.filter((item) => Number(item.trang_thai) === 1).length,
    }
  } catch {
    stats.value = {
      totalJobs: 0,
      activeJobs: 0,
    }
  }
}

const subscribeFollowerChannel = (companyId) => {
  if (!companyId) return

  followerChannelName = `company.public.${companyId}`

  connectPublicChannel(followerChannelName)?.listen('.company.followers.updated', (payload) => {
    const followerCount = Number(payload?.follower_count)

    if (!Number.isFinite(followerCount)) return

    company.value = company.value
      ? {
          ...company.value,
          so_nguoi_theo_doi: followerCount,
        }
      : company.value
  })
}

const saveCompany = async () => {
  if (!form.ten_cong_ty.trim() || !form.ma_so_thue.trim()) {
    notify.warning('Vui lòng nhập tối thiểu tên công ty và mã số thuế.')
    return
  }

  saving.value = true
  try {
    const payload = new FormData()
    payload.append('ten_cong_ty', form.ten_cong_ty.trim())
    payload.append('ma_so_thue', form.ma_so_thue.trim())
    payload.append('email', form.email || '')
    payload.append('dien_thoai', form.dien_thoai || '')
    payload.append('website', form.website || '')
    payload.append('quy_mo', form.quy_mo || '')
    payload.append('dia_chi', form.dia_chi || '')
    payload.append('mo_ta', form.mo_ta || '')

    if (form.nganh_nghe_id) {
      payload.append('nganh_nghe_id', form.nganh_nghe_id)
    }

    if (selectedLogoFile.value) {
      payload.append('logo', selectedLogoFile.value)
    }

    if (hasCompany.value) {
      await employerCompanyService.updateCompany(payload)
      notify.saved('Thông tin công ty')
    } else {
      await employerCompanyService.createCompany(payload)
      notify.created('Thông tin công ty')
    }

    window.sessionStorage.removeItem('employer_company_draft')
    selectedLogoFile.value = null
    await Promise.all([fetchCompany(), fetchStats()])
  } catch (error) {
    notify.apiError(error, 'Không thể lưu thông tin công ty.')
  } finally {
    saving.value = false
  }
}

const handleLogoChange = (event) => {
  const file = event.target.files?.[0]
  if (!file) return

  selectedLogoFile.value = file
  logoPreview.value = URL.createObjectURL(file)
}

const restoreFromServer = async () => {
  await fetchCompany()
  notify.info('Đã tải lại dữ liệu công ty từ hệ thống.')
}

onMounted(async () => {
  await Promise.all([fetchIndustries(), fetchCompany(), fetchStats()])
})

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
  <div class="max-w-5xl mx-auto">
    <div class="mb-8 flex items-end justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-900 dark:text-white">Thông tin công ty</h1>
        <p class="mt-1 text-sm text-slate-500">Quản lý hồ sơ công ty để thu hút ứng viên tốt hơn.</p>
      </div>
      <div class="flex items-center gap-3">
        <button
          class="rounded-lg border border-slate-300 px-5 py-2.5 text-sm font-bold transition-colors hover:bg-slate-100 dark:border-slate-700 dark:hover:bg-slate-800"
          type="button"
          @click="restoreFromServer"
        >
          Tải lại
        </button>
        <button
          class="flex items-center gap-2 rounded-lg bg-[#2463eb] px-5 py-2.5 text-sm font-bold text-white shadow-lg shadow-[#2463eb]/20 transition-all hover:bg-[#2463eb]/90 disabled:cursor-not-allowed disabled:opacity-60"
          :disabled="saving || loading"
          type="button"
          @click="saveCompany"
        >
          <span class="material-symbols-outlined text-xl">save</span>
          {{ saving ? 'Đang lưu...' : 'Lưu thay đổi' }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="grid grid-cols-1 gap-8 lg:grid-cols-12">
      <div class="space-y-6 lg:col-span-4">
        <div class="h-80 animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800" />
        <div class="h-52 animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800" />
      </div>
      <div class="space-y-6 lg:col-span-8">
        <div class="h-80 animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800" />
        <div class="h-64 animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800" />
      </div>
    </div>

    <div v-else class="grid grid-cols-1 gap-8 lg:grid-cols-12">
      <aside class="flex flex-col gap-6 lg:col-span-4">
        <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div class="flex flex-col items-center text-center">
            <div class="relative mb-4">
              <div class="flex size-28 items-center justify-center overflow-hidden rounded-2xl border-4 border-[#2463eb]/20 bg-slate-50 dark:bg-slate-800">
                <span v-if="!logoPreview" class="material-symbols-outlined text-5xl text-slate-300">domain</span>
                <img v-else :src="logoPreview" alt="logo công ty" class="h-full w-full object-cover">
              </div>
            </div>
            <h3 class="text-xl font-bold text-slate-900 dark:text-white">
              {{ form.ten_cong_ty || 'Tên công ty của bạn' }}
            </h3>
            <p class="text-sm text-slate-500">{{ currentIndustryLabel }}</p>
            <div class="mt-2 flex items-center gap-1">
              <span class="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-bold" :class="companyBadgeTone">
                <span class="size-1.5 rounded-full" :class="hasCompany ? 'bg-green-500' : 'bg-amber-500'" />
                {{ companyBadgeLabel }}
              </span>
            </div>
            <div class="mt-4 mb-2 h-2 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
              <div class="h-full rounded-full bg-[#2463eb]" :style="{ width: `${completionPercent}%` }" />
            </div>
            <p class="text-xs font-medium text-slate-400">Hồ sơ hoàn thiện: {{ completionPercent }}%</p>
          </div>
        </div>

        <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <h4 class="mb-4 flex items-center gap-2 font-bold">
            <span class="material-symbols-outlined text-[#2463eb]">analytics</span> Thống kê nhanh
          </h4>
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <span class="text-sm text-slate-500">Tin tuyển dụng</span>
              <span class="font-bold">{{ stats.totalJobs }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-slate-500">Tin đang hoạt động</span>
              <span class="font-bold text-green-600 dark:text-green-400">{{ stats.activeJobs }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-slate-500">Số người follow</span>
              <span class="font-bold">{{ company?.so_nguoi_theo_doi || 0 }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-slate-500">Ngành nghề</span>
              <span class="font-bold">{{ currentIndustryLabel }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-slate-500">Trạng thái hồ sơ</span>
              <span class="font-bold">{{ companyBadgeLabel }}</span>
            </div>
          </div>
        </div>
      </aside>

      <div class="space-y-6 lg:col-span-8">
        <section class="rounded-xl border border-slate-200 bg-white p-8 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <h3 class="mb-6 flex items-center gap-2 text-lg font-bold">
            <span class="material-symbols-outlined text-[#2463eb]">domain</span> Thông tin cơ bản
          </h3>
          <div class="grid grid-cols-1 gap-6 md:grid-cols-2">
            <div class="space-y-1">
              <label class="text-sm font-semibold text-slate-500 dark:text-slate-400">Tên công ty</label>
              <input v-model="form.ten_cong_ty" class="w-full rounded-lg border border-slate-200 bg-slate-50 py-2.5 px-4 transition-all focus:border-transparent focus:ring-2 focus:ring-[#2463eb] dark:border-slate-800 dark:bg-slate-800/50" type="text">
            </div>
            <div class="space-y-1">
              <label class="text-sm font-semibold text-slate-500 dark:text-slate-400">Ngành nghề</label>
              <select v-model="form.nganh_nghe_id" class="w-full rounded-lg border border-slate-200 bg-slate-50 py-2.5 px-4 transition-all focus:border-transparent focus:ring-2 focus:ring-[#2463eb] dark:border-slate-800 dark:bg-slate-800/50">
                <option value="">Chọn ngành nghề</option>
                <option v-for="industry in industries" :key="industry.id" :value="String(industry.id)">
                  {{ industry.ten_nganh }}
                </option>
              </select>
            </div>
            <div class="space-y-1">
              <label class="text-sm font-semibold text-slate-500 dark:text-slate-400">Email liên hệ</label>
              <input v-model="form.email" class="w-full rounded-lg border border-slate-200 bg-slate-50 py-2.5 px-4 transition-all focus:border-transparent focus:ring-2 focus:ring-[#2463eb] dark:border-slate-800 dark:bg-slate-800/50" type="email">
            </div>
            <div class="space-y-1">
              <label class="text-sm font-semibold text-slate-500 dark:text-slate-400">Số điện thoại</label>
              <input v-model="form.dien_thoai" class="w-full rounded-lg border border-slate-200 bg-slate-50 py-2.5 px-4 transition-all focus:border-transparent focus:ring-2 focus:ring-[#2463eb] dark:border-slate-800 dark:bg-slate-800/50" type="tel">
            </div>
            <div class="space-y-1">
              <label class="text-sm font-semibold text-slate-500 dark:text-slate-400">Website</label>
              <input v-model="form.website" class="w-full rounded-lg border border-slate-200 bg-slate-50 py-2.5 px-4 transition-all focus:border-transparent focus:ring-2 focus:ring-[#2463eb] dark:border-slate-800 dark:bg-slate-800/50" type="url">
            </div>
            <div class="space-y-1">
              <label class="text-sm font-semibold text-slate-500 dark:text-slate-400">Quy mô</label>
              <select v-model="form.quy_mo" class="w-full rounded-lg border border-slate-200 bg-slate-50 py-2.5 px-4 transition-all focus:border-transparent focus:ring-2 focus:ring-[#2463eb] dark:border-slate-800 dark:bg-slate-800/50">
                <option value="">Chọn quy mô</option>
                <option value="1-10">1-10 nhân viên</option>
                <option value="11-50">11-50 nhân viên</option>
                <option value="51-200">51-200 nhân viên</option>
                <option value="201-500">201-500 nhân viên</option>
                <option value="500+">500+ nhân viên</option>
              </select>
            </div>
            <div class="space-y-1 md:col-span-2">
              <label class="text-sm font-semibold text-slate-500 dark:text-slate-400">Mã số thuế</label>
              <input v-model="form.ma_so_thue" class="w-full rounded-lg border border-slate-200 bg-slate-50 py-2.5 px-4 transition-all focus:border-transparent focus:ring-2 focus:ring-[#2463eb] dark:border-slate-800 dark:bg-slate-800/50" type="text">
            </div>
            <div class="space-y-1 md:col-span-2">
              <label class="text-sm font-semibold text-slate-500 dark:text-slate-400">Địa chỉ</label>
              <input v-model="form.dia_chi" class="w-full rounded-lg border border-slate-200 bg-slate-50 py-2.5 px-4 transition-all focus:border-transparent focus:ring-2 focus:ring-[#2463eb] dark:border-slate-800 dark:bg-slate-800/50" type="text">
            </div>
            <div class="space-y-1 md:col-span-2">
              <label class="text-sm font-semibold text-slate-500 dark:text-slate-400">Logo công ty</label>
              <label class="flex w-full cursor-pointer items-center justify-between rounded-lg border border-dashed border-slate-300 bg-slate-50 px-4 py-3 text-sm font-medium text-slate-600 transition hover:border-[#2463eb] hover:bg-blue-50 dark:border-slate-700 dark:bg-slate-800/50 dark:text-slate-300 dark:hover:bg-slate-800">
                <span class="flex items-center gap-2">
                  <span class="material-symbols-outlined text-[#2463eb]">upload</span>
                  {{ selectedLogoFile ? selectedLogoFile.name : (form.logo ? 'Đổi logo công ty' : 'Chọn file logo') }}
                </span>
                <span class="text-xs text-slate-400">PNG, JPG tối đa 2MB</span>
                <input class="hidden" type="file" accept="image/*" @change="handleLogoChange">
              </label>
            </div>
          </div>
        </section>

        <section class="rounded-xl border border-slate-200 bg-white p-8 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <h3 class="mb-6 flex items-center gap-2 text-lg font-bold">
            <span class="material-symbols-outlined text-[#2463eb]">article</span> Giới thiệu công ty
          </h3>
          <div class="space-y-1">
            <label class="text-sm font-semibold text-slate-500 dark:text-slate-400">Mô tả</label>
            <textarea
              v-model="form.mo_ta"
              class="w-full resize-none rounded-lg border border-slate-200 bg-slate-50 py-3 px-4 transition-all focus:border-transparent focus:ring-2 focus:ring-[#2463eb] dark:border-slate-800 dark:bg-slate-800/50"
              rows="6"
              placeholder="Mô tả về công ty, văn hóa, sứ mệnh..."
            />
          </div>
        </section>

        <section class="rounded-xl border border-slate-200 bg-white p-8 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div class="mb-6 flex items-center justify-between">
            <h3 class="flex items-center gap-2 text-lg font-bold">
              <span class="material-symbols-outlined text-[#2463eb]">workspace_premium</span> Hồ sơ nổi bật
            </h3>
            <span class="rounded-lg bg-[#2463eb]/10 px-3 py-1 text-xs font-bold text-[#2463eb]">Tự động gợi ý</span>
          </div>
          <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
            <div
              v-for="(benefit, index) in quickBenefits"
              :key="`${index}-${benefit}`"
              class="flex items-center gap-3 rounded-lg border border-slate-100 bg-slate-50 p-3 dark:border-slate-800 dark:bg-slate-800/50"
            >
              <span class="material-symbols-outlined text-green-500">check_circle</span>
              <span class="text-sm font-medium">{{ benefit }}</span>
            </div>
          </div>
        </section>

        <div class="flex justify-end gap-4 pb-8">
          <button class="rounded-lg border border-slate-300 px-8 py-3 font-bold transition-colors hover:bg-slate-100 dark:border-slate-700 dark:hover:bg-slate-800" type="button" @click="restoreFromServer">
            Hủy thay đổi
          </button>
          <button
            class="rounded-lg bg-[#2463eb] px-8 py-3 font-bold text-white transition-all hover:shadow-lg disabled:cursor-not-allowed disabled:opacity-60"
            :disabled="saving"
            type="button"
            @click="saveCompany"
          >
            {{ saving ? 'Đang lưu...' : hasCompany ? 'Lưu thông tin' : 'Tạo công ty' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
