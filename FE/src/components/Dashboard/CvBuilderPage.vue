<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { jobService, profileService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'
import { getStoredCandidate } from '@/utils/authStorage'
import ProfileCvPreview from '@/components/Dashboard/ProfileCvPreview.vue'
import {
  buildCvPresetByMode,
  buildProfileCvPrintHtml,
  cvStyleFamilyOptions,
  cvSkillLevelOptions,
  cvTargetPositionOptions,
  cvTemplateModeOptions,
  cvStylePreferenceOptions,
  cvTemplateLabel,
  cvTemplateOptions,
  getCvTemplatesForMode,
  inferCvStyleFamily,
  resolveProfileCvAvatarUrl,
  suggestCvTemplateByMode,
} from '@/utils/profileCvBuilder'

const route = useRoute()
const router = useRouter()
const notify = useNotify()

const loading = ref(false)
const saving = ref(false)
const loadingIndustries = ref(false)
const previewModalOpen = ref(false)
const currentCandidate = ref(getStoredCandidate())
const industryOptions = ref([])
const selectedIndustryId = ref('')
const templateMode = ref('style')
const styleFamily = ref('executive_navy')
const targetPosition = ref('')
const stylePreference = ref('balanced')
const cvPhotoObjectUrl = ref('')

const educationOptions = [
  { value: 'trung_hoc', label: 'Trung học' },
  { value: 'trung_cap', label: 'Trung cấp' },
  { value: 'cao_dang', label: 'Cao đẳng' },
  { value: 'dai_hoc', label: 'Đại học' },
  { value: 'thac_si', label: 'Thạc sĩ' },
  { value: 'tien_si', label: 'Tiến sĩ' },
  { value: 'khac', label: 'Khác' },
]

const createSkillItem = (ten = '', muc_do = 'kha') => ({ ten, muc_do })
const createExperienceItem = () => ({ vi_tri: '', cong_ty: '', bat_dau: '', ket_thuc: '', mo_ta: '' })
const createEducationItem = () => ({ truong: '', chuyen_nganh: '', bat_dau: '', ket_thuc: '', mo_ta: '' })
const createProjectItem = () => ({ ten: '', vai_tro: '', cong_nghe: '', mo_ta: '', link: '' })
const createCertificateItem = () => ({ ten: '', don_vi: '', nam: '' })

const form = reactive({
  tieu_de_ho_so: '',
  muc_tieu_nghe_nghiep: '',
  trinh_do: '',
  kinh_nghiem_nam: '',
  mo_ta_ban_than: '',
  nguon_ho_so: 'builder',
  mau_cv: 'executive_navy',
  che_do_mau_cv: 'style',
  vi_tri_ung_tuyen_muc_tieu: '',
  ten_nganh_nghe_muc_tieu: '',
  che_do_anh_cv: 'profile',
  anh_cv: null,
  anh_cv_url: '',
  ky_nang_json: [createSkillItem()],
  kinh_nghiem_json: [createExperienceItem()],
  hoc_van_json: [createEducationItem()],
  du_an_json: [],
  chung_chi_json: [],
  trang_thai: 1,
})

const extractList = (response) => {
  const payload = response?.data
  if (Array.isArray(payload?.data)) return payload.data
  if (Array.isArray(payload)) return payload
  return []
}

const normalizeItems = (items, requiredKeys = []) => {
  if (!Array.isArray(items)) return []

  return items
    .map((item) => {
      if (!item || typeof item !== 'object') return null
      const normalized = Object.fromEntries(
        Object.entries(item).map(([key, value]) => [key, String(value ?? '').trim()]),
      )

      const hasRequired = requiredKeys.length
        ? requiredKeys.some((key) => normalized[key])
        : Object.values(normalized).some(Boolean)

      return hasRequired ? normalized : null
    })
    .filter(Boolean)
}

const editingProfileId = computed(() => {
  const raw = String(route.query.id || '').trim()
  return raw ? Number(raw) || null : null
})

const pageTitle = computed(() => (editingProfileId.value ? 'Chỉnh sửa CV hệ thống' : 'Tạo CV trên hệ thống'))
const pageDescription = computed(() =>
  editingProfileId.value
    ? 'Cập nhật CV builder với các mẫu bám theo layout tham chiếu bạn đã chọn.'
    : 'Dựng CV trực tiếp trên hệ thống với các mẫu bám theo layout tham chiếu thực tế, có thể chọn theo phong cách hoặc theo vị trí ứng tuyển.',
)

const selectedIndustry = computed(() =>
  industryOptions.value.find((item) => String(item.id) === String(selectedIndustryId.value)) || null,
)

const selectedIndustryName = computed(
  () => selectedIndustry.value?.ten_nganh || selectedIndustry.value?.ten_nganh_nghe || '',
)

const recommendedTemplate = computed(() => suggestCvTemplateByMode({
  mode: templateMode.value,
  industryName: selectedIndustryName.value,
  styleFamily: styleFamily.value,
  positionValue: targetPosition.value,
  preference: stylePreference.value,
}))
const candidateAvatarUrl = computed(() =>
  currentCandidate.value?.avatar_url ||
  currentCandidate.value?.anh_dai_dien_url ||
  currentCandidate.value?.anh_dai_dien ||
  '',
)
const cvPhotoPreviewUrl = computed(() => {
  if (form.che_do_anh_cv !== 'upload') {
    return ''
  }

  return cvPhotoObjectUrl.value || form.anh_cv_url || ''
})
const availableTemplates = computed(() => getCvTemplatesForMode(templateMode.value, styleFamily.value))
const previewProfile = computed(() => ({
  ...form,
  che_do_mau_cv: templateMode.value,
  vi_tri_ung_tuyen_muc_tieu: targetPosition.value,
  ten_nganh_nghe_muc_tieu: selectedIndustryName.value,
  che_do_anh_cv: form.che_do_anh_cv,
  anh_cv_preview_url: cvPhotoPreviewUrl.value,
  ky_nang_json: normalizeItems(form.ky_nang_json, ['ten']),
  kinh_nghiem_json: normalizeItems(form.kinh_nghiem_json, ['vi_tri']),
  hoc_van_json: normalizeItems(form.hoc_van_json, ['truong']),
  du_an_json: normalizeItems(form.du_an_json, ['ten']),
  chung_chi_json: normalizeItems(form.chung_chi_json, ['ten']),
}))

const templatePreviewBase = computed(() => ({
  ...previewProfile.value,
  tieu_de_ho_so: previewProfile.value.tieu_de_ho_so || 'Senior Product Manager',
  muc_tieu_nghe_nghiep:
    previewProfile.value.muc_tieu_nghe_nghiep ||
    'Tập trung vào kinh nghiệm nổi bật, kỹ năng cốt lõi và cách trình bày phù hợp với vai trò mục tiêu.',
  mo_ta_ban_than:
    previewProfile.value.mo_ta_ban_than ||
    'Ứng viên có kinh nghiệm thực tế, định hướng rõ ràng và muốn thể hiện hồ sơ theo bố cục dễ quét cho nhà tuyển dụng.',
  vi_tri_ung_tuyen_muc_tieu: previewProfile.value.vi_tri_ung_tuyen_muc_tieu || 'Product Manager',
  ten_nganh_nghe_muc_tieu: previewProfile.value.ten_nganh_nghe_muc_tieu || 'Công nghệ thông tin',
  ky_nang_json: previewProfile.value.ky_nang_json.length
    ? previewProfile.value.ky_nang_json
    : [
        { ten: 'Stakeholder Management', muc_do: 'tot' },
        { ten: 'Product Strategy', muc_do: 'tot' },
        { ten: 'Agile', muc_do: 'kha' },
      ],
  kinh_nghiem_json: previewProfile.value.kinh_nghiem_json.length
    ? previewProfile.value.kinh_nghiem_json
    : [
        {
          vi_tri: 'Product Manager',
          cong_ty: 'Tech Company',
          bat_dau: '03/2022',
          ket_thuc: 'Hiện tại',
          mo_ta: 'Dẫn dắt roadmap sản phẩm, phối hợp team đa chức năng và tối ưu trải nghiệm người dùng.',
        },
      ],
  hoc_van_json: previewProfile.value.hoc_van_json.length
    ? previewProfile.value.hoc_van_json
    : [
        {
          truong: 'Đại học Duy Tân',
          chuyen_nganh: 'Quản trị / Công nghệ',
          bat_dau: '09/2018',
          ket_thuc: '06/2022',
          mo_ta: '',
        },
      ],
}))

const getTemplatePreviewProfile = (templateValue) => ({
  ...templatePreviewBase.value,
  mau_cv: templateValue,
})

const resetForm = () => {
  if (cvPhotoObjectUrl.value) {
    URL.revokeObjectURL(cvPhotoObjectUrl.value)
    cvPhotoObjectUrl.value = ''
  }
  form.tieu_de_ho_so = ''
  form.muc_tieu_nghe_nghiep = ''
  form.trinh_do = ''
  form.kinh_nghiem_nam = ''
  form.mo_ta_ban_than = ''
  form.nguon_ho_so = 'builder'
  form.mau_cv = 'executive_navy'
  form.che_do_mau_cv = 'style'
  form.vi_tri_ung_tuyen_muc_tieu = ''
  form.ten_nganh_nghe_muc_tieu = ''
  form.che_do_anh_cv = 'profile'
  form.anh_cv = null
  form.anh_cv_url = ''
  form.ky_nang_json = [createSkillItem()]
  form.kinh_nghiem_json = [createExperienceItem()]
  form.hoc_van_json = [createEducationItem()]
  form.du_an_json = []
  form.chung_chi_json = []
  form.trang_thai = 1
  selectedIndustryId.value = ''
  templateMode.value = 'style'
  styleFamily.value = 'executive_navy'
  targetPosition.value = ''
  stylePreference.value = 'balanced'
}

const fillForm = (profile) => {
  if (cvPhotoObjectUrl.value) {
    URL.revokeObjectURL(cvPhotoObjectUrl.value)
    cvPhotoObjectUrl.value = ''
  }
  form.tieu_de_ho_so = profile?.tieu_de_ho_so || ''
  form.muc_tieu_nghe_nghiep = profile?.muc_tieu_nghe_nghiep || ''
  form.trinh_do = profile?.trinh_do || ''
  form.kinh_nghiem_nam = profile?.kinh_nghiem_nam ?? ''
  form.mo_ta_ban_than = profile?.mo_ta_ban_than || ''
  form.nguon_ho_so = 'builder'
  form.mau_cv = profile?.mau_cv || 'executive_navy'
  form.che_do_mau_cv = profile?.che_do_mau_cv || 'style'
  form.vi_tri_ung_tuyen_muc_tieu = profile?.vi_tri_ung_tuyen_muc_tieu || ''
  form.ten_nganh_nghe_muc_tieu = profile?.ten_nganh_nghe_muc_tieu || ''
  form.che_do_anh_cv = profile?.che_do_anh_cv || 'profile'
  form.anh_cv = null
  form.anh_cv_url = profile?.anh_cv_url || ''
  form.ky_nang_json = Array.isArray(profile?.ky_nang_json) && profile.ky_nang_json.length
    ? profile.ky_nang_json.map((item) => ({ ten: item?.ten || '', muc_do: item?.muc_do || 'kha' }))
    : [createSkillItem()]
  form.kinh_nghiem_json = Array.isArray(profile?.kinh_nghiem_json) && profile.kinh_nghiem_json.length
    ? profile.kinh_nghiem_json.map((item) => ({ vi_tri: item?.vi_tri || '', cong_ty: item?.cong_ty || '', bat_dau: item?.bat_dau || '', ket_thuc: item?.ket_thuc || '', mo_ta: item?.mo_ta || '' }))
    : [createExperienceItem()]
  form.hoc_van_json = Array.isArray(profile?.hoc_van_json) && profile.hoc_van_json.length
    ? profile.hoc_van_json.map((item) => ({ truong: item?.truong || '', chuyen_nganh: item?.chuyen_nganh || '', bat_dau: item?.bat_dau || '', ket_thuc: item?.ket_thuc || '', mo_ta: item?.mo_ta || '' }))
    : [createEducationItem()]
  form.du_an_json = Array.isArray(profile?.du_an_json)
    ? profile.du_an_json.map((item) => ({ ten: item?.ten || '', vai_tro: item?.vai_tro || '', cong_nghe: item?.cong_nghe || '', mo_ta: item?.mo_ta || '', link: item?.link || '' }))
    : []
  form.chung_chi_json = Array.isArray(profile?.chung_chi_json)
    ? profile.chung_chi_json.map((item) => ({ ten: item?.ten || '', don_vi: item?.don_vi || '', nam: item?.nam || '' }))
    : []
  form.trang_thai = Number(profile?.trang_thai ?? 1)
  templateMode.value = form.che_do_mau_cv || 'style'
  targetPosition.value = form.vi_tri_ung_tuyen_muc_tieu || ''
  styleFamily.value = inferCvStyleFamily(form.mau_cv)
}

const handleCvPhotoChange = (event) => {
  const [file] = Array.from(event?.target?.files || [])
  form.anh_cv = file || null

  if (cvPhotoObjectUrl.value) {
    URL.revokeObjectURL(cvPhotoObjectUrl.value)
    cvPhotoObjectUrl.value = ''
  }

  if (!file) {
    return
  }

  cvPhotoObjectUrl.value = URL.createObjectURL(file)
}

const clearCvPhotoUpload = () => {
  form.anh_cv = null
  form.anh_cv_url = ''

  if (cvPhotoObjectUrl.value) {
    URL.revokeObjectURL(cvPhotoObjectUrl.value)
    cvPhotoObjectUrl.value = ''
  }
}

const loadIndustries = async () => {
  loadingIndustries.value = true
  try {
    const response = await jobService.getIndustries({ per_page: 200 })
    industryOptions.value = extractList(response)
  } catch (error) {
    industryOptions.value = []
    notify.apiError(error, 'Không thể tải danh sách ngành nghề cho CV builder.')
  } finally {
    loadingIndustries.value = false
  }
}

const loadEditingProfile = async () => {
  if (!editingProfileId.value) {
    resetForm()
    return
  }

  loading.value = true
  try {
    const response = await profileService.getProfileById(editingProfileId.value)
    const profile = response?.data || null

    if (!profile) {
      notify.warning('Không tìm thấy hồ sơ cần chỉnh sửa.')
      router.replace('/my-cv')
      return
    }

    fillForm(profile)
  } catch (error) {
    notify.apiError(error, 'Không thể tải CV hệ thống cần chỉnh sửa.')
    router.replace('/my-cv')
  } finally {
    loading.value = false
  }
}

const addSectionItem = (field) => {
  if (field === 'ky_nang_json') form.ky_nang_json.push(createSkillItem())
  if (field === 'kinh_nghiem_json') form.kinh_nghiem_json.push(createExperienceItem())
  if (field === 'hoc_van_json') form.hoc_van_json.push(createEducationItem())
  if (field === 'du_an_json') form.du_an_json.push(createProjectItem())
  if (field === 'chung_chi_json') form.chung_chi_json.push(createCertificateItem())
}

const removeSectionItem = (field, index) => {
  if (!Array.isArray(form[field])) return
  form[field].splice(index, 1)
  if (!form[field].length && ['ky_nang_json', 'kinh_nghiem_json', 'hoc_van_json'].includes(field)) {
    addSectionItem(field)
  }
}

const applyTemplatePreset = () => {
  if (templateMode.value === 'position' && !targetPosition.value) {
    notify.warning('Hãy chọn vị trí ứng tuyển trước khi áp preset.')
    return
  }

  if (templateMode.value === 'style' && !selectedIndustryName.value && !styleFamily.value) {
    notify.warning('Hãy chọn ít nhất ngành nghề hoặc phong cách trước khi áp preset.')
    return
  }

  const preset = buildCvPresetByMode({
    mode: templateMode.value,
    industryName: selectedIndustryName.value,
    styleFamily: styleFamily.value,
    positionValue: targetPosition.value,
    preference: stylePreference.value,
  })
  form.mau_cv = preset.template
  form.che_do_mau_cv = templateMode.value
  form.vi_tri_ung_tuyen_muc_tieu = targetPosition.value
  form.ten_nganh_nghe_muc_tieu = selectedIndustryName.value

  if (!String(form.tieu_de_ho_so).trim()) {
    form.tieu_de_ho_so = preset.suggestedTitle
  }

  if (!String(form.muc_tieu_nghe_nghiep).trim()) {
    form.muc_tieu_nghe_nghiep = preset.suggestedObjective
  }

  const existingSkills = normalizeItems(form.ky_nang_json, ['ten']).map((item) => item.ten.toLowerCase())
  const missingSkills = preset.suggestedSkills.filter((item) => !existingSkills.includes(item.toLowerCase()))
  if (missingSkills.length) {
    form.ky_nang_json = [...normalizeItems(form.ky_nang_json, ['ten']), ...missingSkills.map((item) => createSkillItem(item, 'kha'))]
  }

  notify.success(
    templateMode.value === 'position'
      ? 'Đã áp dụng preset CV theo vị trí ứng tuyển.'
      : `Đã áp dụng preset CV theo phong cách ${cvStyleFamilyOptions.find((item) => item.value === styleFamily.value)?.label?.toLowerCase() || 'đã chọn'}.`
  )
}

const exportPreview = () => {
  const popup = window.open('', '_blank', 'noopener,noreferrer')
  if (!popup) {
    notify.warning('Trình duyệt đang chặn cửa sổ in. Hãy cho phép popup và thử lại.')
    return
  }

  popup.document.open()
  popup.document.write(buildProfileCvPrintHtml({ profile: previewProfile.value, owner: currentCandidate.value }))
  popup.document.close()
}

const openPreviewModal = () => {
  previewModalOpen.value = true
}

const closePreviewModal = () => {
  previewModalOpen.value = false
}

const buildFormData = () => {
  const payload = new FormData()
  payload.append('tieu_de_ho_so', form.tieu_de_ho_so)
  payload.append('muc_tieu_nghe_nghiep', form.muc_tieu_nghe_nghiep || '')
  payload.append('trinh_do', form.trinh_do || '')
  payload.append('kinh_nghiem_nam', String(form.kinh_nghiem_nam || 0))
  payload.append('mo_ta_ban_than', form.mo_ta_ban_than || '')
  payload.append('nguon_ho_so', 'builder')
  payload.append('mau_cv', form.mau_cv || 'executive_navy')
  payload.append('che_do_mau_cv', templateMode.value)
  payload.append('vi_tri_ung_tuyen_muc_tieu', targetPosition.value || '')
  payload.append('ten_nganh_nghe_muc_tieu', selectedIndustryName.value || '')
  payload.append('che_do_anh_cv', form.che_do_anh_cv || 'profile')
  if (form.che_do_anh_cv === 'upload' && form.anh_cv instanceof File) {
    payload.append('anh_cv', form.anh_cv)
  }
  payload.append('ky_nang_json', JSON.stringify(normalizeItems(form.ky_nang_json, ['ten'])))
  payload.append('kinh_nghiem_json', JSON.stringify(normalizeItems(form.kinh_nghiem_json, ['vi_tri'])))
  payload.append('hoc_van_json', JSON.stringify(normalizeItems(form.hoc_van_json, ['truong'])))
  payload.append('du_an_json', JSON.stringify(normalizeItems(form.du_an_json, ['ten'])))
  payload.append('chung_chi_json', JSON.stringify(normalizeItems(form.chung_chi_json, ['ten'])))
  payload.append('trang_thai', String(form.trang_thai))
  return payload
}

const submitProfile = async () => {
  if (form.che_do_anh_cv === 'upload' && !form.anh_cv && !form.anh_cv_url) {
    notify.warning('Hãy chọn ảnh đại diện riêng cho CV hoặc chuyển sang dùng ảnh tài khoản.')
    return
  }

  saving.value = true
  try {
    const payload = buildFormData()
    if (editingProfileId.value) {
      await profileService.updateProfile(editingProfileId.value, payload)
      notify.success('Đã cập nhật CV hệ thống.')
    } else {
      await profileService.createProfile(payload)
      notify.success('Đã tạo CV hệ thống mới.')
    }

    router.push('/my-cv')
  } catch (error) {
    notify.apiError(error, 'Không thể lưu CV hệ thống.')
  } finally {
    saving.value = false
  }
}

watch(
  () => route.query.id,
  async () => {
    await loadEditingProfile()
  },
  { immediate: true },
)

watch(industryOptions, (items) => {
  if (!form.ten_nganh_nghe_muc_tieu || selectedIndustryId.value) return

  const matched = items.find((item) =>
    String(item?.ten_nganh || item?.ten_nganh_nghe || '').trim().toLowerCase() ===
    String(form.ten_nganh_nghe_muc_tieu || '').trim().toLowerCase()
  )

  if (matched?.id) {
    selectedIndustryId.value = String(matched.id)
  }
})

watch(templateMode, (mode) => {
  form.che_do_mau_cv = mode

  if (mode === 'style') {
    targetPosition.value = ''
    form.vi_tri_ung_tuyen_muc_tieu = ''
    if (!availableTemplates.value.some((item) => item.value === form.mau_cv)) {
      form.mau_cv = suggestCvTemplateByMode({
        mode,
        industryName: selectedIndustryName.value,
        styleFamily: styleFamily.value,
        preference: stylePreference.value,
      })
    }
    return
  }

  styleFamily.value = inferCvStyleFamily(form.mau_cv)
  if (!availableTemplates.value.some((item) => item.value === form.mau_cv)) {
    form.mau_cv = recommendedTemplate.value
  }
})

watch([styleFamily, targetPosition, selectedIndustryId], () => {
  form.vi_tri_ung_tuyen_muc_tieu = targetPosition.value || ''
  form.ten_nganh_nghe_muc_tieu = selectedIndustryName.value || ''

  if (!availableTemplates.value.some((item) => item.value === form.mau_cv)) {
    form.mau_cv = recommendedTemplate.value
  }
})

onMounted(async () => {
  await loadIndustries()
})

onBeforeUnmount(() => {
  if (cvPhotoObjectUrl.value) {
    URL.revokeObjectURL(cvPhotoObjectUrl.value)
  }
})
</script>

<template>
  <div class="space-y-8">
    <div class="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.28em] text-blue-500">CV Builder</p>
        <h1 class="mt-2 text-3xl font-black text-slate-900 dark:text-white">{{ pageTitle }}</h1>
        <p class="mt-3 max-w-3xl text-sm leading-7 text-slate-600 dark:text-slate-400">
          {{ pageDescription }}
        </p>
      </div>

      <div class="flex flex-wrap gap-3">
        <button
          class="inline-flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200"
          type="button"
          @click="router.push('/my-cv')"
        >
          <span class="material-symbols-outlined text-[18px]">arrow_back</span>
          Quay lại CV của tôi
        </button>
        <button
          class="inline-flex items-center gap-2 rounded-2xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-700"
          type="button"
          @click="exportPreview"
        >
          <span class="material-symbols-outlined text-[18px]">print</span>
          In / Xuất PDF
        </button>
      </div>
    </div>

    <div class="space-y-6">
        <section class="rounded-[28px] border border-blue-100 bg-gradient-to-r from-blue-50 via-white to-sky-50 p-6 shadow-sm dark:border-blue-900/20 dark:from-slate-900 dark:via-slate-900 dark:to-slate-950">
          <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <div>
              <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Cách tạo template</label>
              <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
                <button
                  v-for="option in cvTemplateModeOptions"
                  :key="option.value"
                  class="rounded-2xl border px-4 py-4 text-left transition"
                  :class="templateMode === option.value
                    ? 'border-slate-900 bg-slate-900 text-white dark:border-slate-200 dark:bg-slate-100 dark:text-slate-900'
                    : 'border-slate-200 bg-white text-slate-700 hover:border-slate-300 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200'"
                  type="button"
                  @click="templateMode = option.value"
                >
                  <p class="text-sm font-bold">{{ option.label }}</p>
                  <p class="mt-1 text-xs leading-6" :class="templateMode === option.value ? 'text-white/80 dark:text-slate-700' : 'text-slate-500 dark:text-slate-400'">
                    {{ option.description }}
                  </p>
                </button>
              </div>
            </div>

            <div v-if="templateMode === 'style'">
              <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Nhóm phong cách</label>
              <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
                <button
                  v-for="option in cvStyleFamilyOptions"
                  :key="option.value"
                  class="rounded-2xl border px-4 py-4 text-left transition"
                  :class="styleFamily === option.value
                    ? 'border-blue-600 bg-blue-600 text-white'
                    : 'border-slate-200 bg-white text-slate-700 hover:border-slate-300 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200'"
                  type="button"
                  @click="styleFamily = option.value"
                >
                  <p class="text-sm font-bold">{{ option.label }}</p>
                  <p class="mt-1 text-xs leading-6" :class="styleFamily === option.value ? 'text-white/80' : 'text-slate-500 dark:text-slate-400'">
                    {{ option.description }}
                  </p>
                </button>
              </div>
            </div>

            <div v-else>
              <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Vị trí ứng tuyển mục tiêu</label>
              <select
                v-model="targetPosition"
                class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
              >
                <option value="">Chọn vị trí ứng tuyển</option>
                <option
                  v-for="option in cvTargetPositionOptions"
                  :key="option.value"
                  :value="option.value"
                >
                  {{ option.label }}
                </option>
              </select>
            </div>
          </div>

          <div class="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-[minmax(0,1fr)_220px_220px_auto] lg:items-end">
            <div>
              <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Ngành nghề mục tiêu</label>
              <select
                v-model="selectedIndustryId"
                class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
              >
                <option value="">Chọn ngành nghề để gợi ý template</option>
                <option
                  v-for="industry in industryOptions"
                  :key="industry.id"
                  :value="String(industry.id)"
                >
                  {{ industry.ten_nganh || industry.ten_nganh_nghe }}
                </option>
              </select>
            </div>

            <div>
              <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Phong cách hiển thị</label>
              <select
                v-model="stylePreference"
                class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
              >
                <option v-for="option in cvStylePreferenceOptions" :key="option.value" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
            </div>

            <div class="rounded-2xl border border-white/80 bg-white/90 px-4 py-3 shadow-sm dark:border-slate-700 dark:bg-slate-900/80">
              <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Template đề xuất</p>
              <p class="mt-2 text-lg font-bold text-slate-900 dark:text-white">{{ cvTemplateLabel(recommendedTemplate) }}</p>
            </div>

            <button
              class="inline-flex h-[50px] items-center justify-center gap-2 rounded-2xl bg-[#2463eb] px-5 text-sm font-bold text-white transition hover:bg-blue-700"
              :disabled="loadingIndustries || (templateMode === 'position' ? !targetPosition : !selectedIndustryId && !styleFamily)"
              type="button"
              @click="applyTemplatePreset"
            >
              <span class="material-symbols-outlined text-[18px]">auto_fix_high</span>
              Áp preset
            </button>
          </div>

          <div class="mt-4 rounded-2xl border border-blue-100 bg-white/90 p-4 text-sm leading-7 text-slate-600 shadow-sm dark:border-slate-700 dark:bg-slate-900/70 dark:text-slate-300">
            <p>
              Ở chế độ <span class="font-semibold">theo phong cách</span>, hệ thống gợi ý template dựa trên gu hiển thị và ngành nghề.
              Ở chế độ <span class="font-semibold">theo vị trí ứng tuyển</span>, hệ thống gợi ý nội dung CV sát hơn với vai trò mục tiêu.
            </p>
          </div>
        </section>

        <section v-if="loading" class="rounded-[28px] border border-slate-200 bg-white p-10 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div class="h-40 animate-pulse rounded-3xl bg-slate-100 dark:bg-slate-800" />
        </section>

        <template v-else>
          <section class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
            <div class="grid grid-cols-1 gap-5 md:grid-cols-2">
              <div class="md:col-span-2">
                <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Tiêu đề hồ sơ</label>
                <input
                  v-model="form.tieu_de_ho_so"
                  class="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100"
                  placeholder="Ví dụ: CV Backend Developer Laravel"
                  type="text"
                />
              </div>

              <div>
                <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Trình độ</label>
                <select
                  v-model="form.trinh_do"
                  class="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100"
                >
                  <option value="">Chọn trình độ</option>
                  <option v-for="option in educationOptions" :key="option.value" :value="option.value">
                    {{ option.label }}
                  </option>
                </select>
              </div>

              <div>
                <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Số năm kinh nghiệm</label>
                <input
                  v-model="form.kinh_nghiem_nam"
                  min="0"
                  max="50"
                  class="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100"
                  type="number"
                />
              </div>

              <div>
                <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Trạng thái hồ sơ</label>
                <select
                  v-model="form.trang_thai"
                  class="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100"
                >
                  <option :value="1">Công khai</option>
                  <option :value="0">Ẩn</option>
                </select>
              </div>

              <div>
                <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Template đang dùng</label>
                <div class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-semibold text-slate-700 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100">
                  {{ cvTemplateLabel(form.mau_cv) }}
                </div>
              </div>

              <div>
                <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Chế độ template</label>
                <div class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-semibold text-slate-700 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100">
                  {{ cvTemplateModeOptions.find((item) => item.value === templateMode)?.label || 'Theo phong cách' }}
                </div>
              </div>

              <div>
                <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Vị trí mục tiêu</label>
                <div class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-semibold text-slate-700 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100">
                  {{ cvTargetPositionOptions.find((item) => item.value === targetPosition)?.label || form.vi_tri_ung_tuyen_muc_tieu || 'Chưa chọn' }}
                </div>
              </div>

              <div class="md:col-span-2 rounded-3xl border border-slate-200 p-5 dark:border-slate-700">
                <div class="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                  <div>
                    <label class="block text-sm font-semibold text-slate-700 dark:text-slate-200">Ảnh đại diện trên CV</label>
                    <p class="mt-1 text-sm leading-6 text-slate-500 dark:text-slate-400">
                      Bạn có thể dùng ảnh đại diện hiện tại của tài khoản hoặc tải một ảnh riêng chỉ áp dụng cho CV này.
                    </p>
                  </div>
                  <div class="flex items-center gap-3">
                    <div class="flex h-16 w-16 items-center justify-center overflow-hidden rounded-full border border-slate-200 bg-slate-100 text-lg font-bold text-slate-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300">
                      <img
                        v-if="resolveProfileCvAvatarUrl(previewProfile, currentCandidate)"
                        :src="resolveProfileCvAvatarUrl(previewProfile, currentCandidate)"
                        alt="Ảnh CV"
                        class="h-full w-full object-cover"
                      />
                      <span v-else>{{ String(currentCandidate?.ho_ten || 'U').trim().charAt(0).toUpperCase() }}</span>
                    </div>
                    <div class="text-xs leading-5 text-slate-500 dark:text-slate-400">
                      <p class="font-semibold text-slate-700 dark:text-slate-200">
                        {{ form.che_do_anh_cv === 'upload' ? 'Đang dùng ảnh riêng cho CV' : 'Đang dùng ảnh đại diện tài khoản' }}
                      </p>
                      <p v-if="form.che_do_anh_cv === 'upload' && !cvPhotoPreviewUrl">Chưa chọn ảnh mới cho CV này.</p>
                      <p v-else-if="form.che_do_anh_cv === 'upload'">Ảnh này chỉ áp dụng cho hồ sơ CV hiện tại.</p>
                      <p v-else>Ảnh lấy từ hồ sơ cá nhân hiện tại của bạn.</p>
                    </div>
                  </div>
                </div>

                <div class="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2">
                  <button
                    class="rounded-2xl border px-4 py-4 text-left transition"
                    :class="form.che_do_anh_cv === 'profile'
                      ? 'border-slate-900 bg-slate-900 text-white dark:border-slate-200 dark:bg-slate-100 dark:text-slate-900'
                      : 'border-slate-200 bg-white text-slate-700 hover:border-slate-300 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-200'"
                    type="button"
                    @click="form.che_do_anh_cv = 'profile'"
                  >
                    <p class="text-sm font-bold">Dùng ảnh đại diện tài khoản</p>
                    <p class="mt-1 text-xs leading-6" :class="form.che_do_anh_cv === 'profile' ? 'text-white/80 dark:text-slate-700' : 'text-slate-500 dark:text-slate-400'">
                      Phù hợp nếu bạn muốn đồng bộ ảnh hồ sơ cá nhân với tất cả CV hệ thống.
                    </p>
                  </button>

                  <button
                    class="rounded-2xl border px-4 py-4 text-left transition"
                    :class="form.che_do_anh_cv === 'upload'
                      ? 'border-blue-600 bg-blue-600 text-white'
                      : 'border-slate-200 bg-white text-slate-700 hover:border-slate-300 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-200'"
                    type="button"
                    @click="form.che_do_anh_cv = 'upload'"
                  >
                    <p class="text-sm font-bold">Upload ảnh riêng cho CV</p>
                    <p class="mt-1 text-xs leading-6" :class="form.che_do_anh_cv === 'upload' ? 'text-white/80' : 'text-slate-500 dark:text-slate-400'">
                      Dùng ảnh khác với avatar tài khoản nếu bạn muốn một phiên bản CV riêng biệt hơn.
                    </p>
                  </button>
                </div>

                <div v-if="form.che_do_anh_cv === 'upload'" class="mt-4 rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-950">
                  <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                    <div class="text-sm leading-6 text-slate-500 dark:text-slate-400">
                      <p class="font-semibold text-slate-700 dark:text-slate-200">Ảnh cho template CV</p>
                      <p>Chấp nhận `jpg`, `png`, `webp`, tối đa 2MB. Nên dùng ảnh chân dung vuông hoặc gần vuông để hiển thị đẹp hơn.</p>
                    </div>
                    <label class="inline-flex cursor-pointer items-center gap-2 rounded-2xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-700">
                      <span class="material-symbols-outlined text-[18px]">upload</span>
                      Chọn ảnh
                      <input
                        accept="image/png,image/jpeg,image/jpg,image/webp"
                        class="hidden"
                        type="file"
                        @change="handleCvPhotoChange"
                      />
                    </label>
                  </div>

                  <div v-if="cvPhotoPreviewUrl || form.anh_cv_url" class="mt-4 flex items-center justify-between gap-4 rounded-2xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-900">
                    <div class="flex items-center gap-4">
                      <div class="h-20 w-20 overflow-hidden rounded-2xl border border-slate-200 bg-slate-100 dark:border-slate-700 dark:bg-slate-800">
                        <img :src="cvPhotoPreviewUrl || form.anh_cv_url" alt="Preview ảnh CV" class="h-full w-full object-cover" />
                      </div>
                      <div class="text-sm leading-6 text-slate-500 dark:text-slate-400">
                        <p class="font-semibold text-slate-700 dark:text-slate-200">
                          {{ form.anh_cv?.name || (form.anh_cv_url ? 'Ảnh CV đã lưu' : 'Ảnh mới chưa lưu') }}
                        </p>
                        <p>{{ form.anh_cv ? 'Ảnh mới sẽ được lưu khi bấm tạo/cập nhật CV.' : 'Đang dùng ảnh riêng đã lưu cho hồ sơ này.' }}</p>
                      </div>
                    </div>
                    <button
                      class="rounded-xl border border-rose-200 px-3 py-2 text-sm font-semibold text-rose-500 transition hover:bg-rose-50 dark:border-rose-900/40 dark:hover:bg-rose-900/10"
                      type="button"
                      @click="clearCvPhotoUpload"
                    >
                      Xóa ảnh riêng
                    </button>
                  </div>
                </div>
              </div>

              <div class="md:col-span-2">
                <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Mục tiêu nghề nghiệp</label>
                <textarea
                  v-model="form.muc_tieu_nghe_nghiep"
                  rows="4"
                  class="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100"
                  placeholder="Mô tả ngắn định hướng nghề nghiệp và vị trí bạn muốn ứng tuyển."
                />
              </div>

              <div class="md:col-span-2">
                <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Mô tả bản thân</label>
                <textarea
                  v-model="form.mo_ta_ban_than"
                  rows="4"
                  class="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100"
                  placeholder="Tóm tắt ngắn về kinh nghiệm, điểm mạnh và định hướng cá nhân."
                />
              </div>
            </div>
          </section>

          <section class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
            <div class="mb-4 flex items-center justify-between gap-4">
              <div>
                <h2 class="text-lg font-bold text-slate-900 dark:text-white">Kỹ năng</h2>
                <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Liệt kê những kỹ năng nổi bật bạn muốn employer nhìn thấy ngay.</p>
              </div>
              <button class="rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white" type="button" @click="addSectionItem('ky_nang_json')">
                Thêm kỹ năng
              </button>
            </div>

            <div class="space-y-3">
              <div v-for="(item, index) in form.ky_nang_json" :key="`skill-${index}`" class="grid grid-cols-1 gap-3 md:grid-cols-[minmax(0,1fr)_220px_56px]">
                <input v-model="item.ten" class="rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100" placeholder="Ví dụ: Laravel, Vue.js, PostgreSQL" type="text" />
                <select v-model="item.muc_do" class="rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100">
                  <option v-for="level in cvSkillLevelOptions" :key="level.value" :value="level.value">{{ level.label }}</option>
                </select>
                <button class="rounded-2xl border border-rose-200 text-rose-500 transition hover:bg-rose-50 dark:border-rose-900/40 dark:hover:bg-rose-900/10" type="button" @click="removeSectionItem('ky_nang_json', index)">
                  <span class="material-symbols-outlined">delete</span>
                </button>
              </div>
            </div>
          </section>

          <section class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
            <div class="mb-4 flex items-center justify-between gap-4">
              <div>
                <h2 class="text-lg font-bold text-slate-900 dark:text-white">Kinh nghiệm làm việc</h2>
                <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Tập trung vào vị trí, công ty, thời gian và tác động nổi bật.</p>
              </div>
              <button class="rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white" type="button" @click="addSectionItem('kinh_nghiem_json')">
                Thêm kinh nghiệm
              </button>
            </div>

            <div class="space-y-4">
              <div v-for="(item, index) in form.kinh_nghiem_json" :key="`exp-${index}`" class="rounded-3xl border border-slate-200 p-4 dark:border-slate-700">
                <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
                  <input v-model="item.vi_tri" class="rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100" placeholder="Vị trí" type="text" />
                  <input v-model="item.cong_ty" class="rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100" placeholder="Công ty" type="text" />
                  <input v-model="item.bat_dau" class="rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100" placeholder="Bắt đầu (MM/YYYY)" type="text" />
                  <input v-model="item.ket_thuc" class="rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100" placeholder="Kết thúc / Hiện tại" type="text" />
                  <textarea v-model="item.mo_ta" rows="3" class="md:col-span-2 rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100" placeholder="Mô tả ngắn các đầu việc, thành tựu hoặc tác động nổi bật." />
                </div>
                <div class="mt-3 flex justify-end">
                  <button class="rounded-xl border border-rose-200 px-3 py-2 text-sm font-semibold text-rose-500 transition hover:bg-rose-50 dark:border-rose-900/40 dark:hover:bg-rose-900/10" type="button" @click="removeSectionItem('kinh_nghiem_json', index)">
                    Xóa kinh nghiệm
                  </button>
                </div>
              </div>
            </div>
          </section>

          <section class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
            <div class="mb-4 flex items-center justify-between gap-4">
              <div>
                <h2 class="text-lg font-bold text-slate-900 dark:text-white">Học vấn</h2>
                <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Dùng để employer nắm nhanh nền tảng học thuật của bạn.</p>
              </div>
              <button class="rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white" type="button" @click="addSectionItem('hoc_van_json')">
                Thêm học vấn
              </button>
            </div>

            <div class="space-y-4">
              <div v-for="(item, index) in form.hoc_van_json" :key="`edu-${index}`" class="rounded-3xl border border-slate-200 p-4 dark:border-slate-700">
                <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
                  <input v-model="item.truong" class="rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100" placeholder="Trường học" type="text" />
                  <input v-model="item.chuyen_nganh" class="rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100" placeholder="Chuyên ngành" type="text" />
                  <input v-model="item.bat_dau" class="rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100" placeholder="Bắt đầu (MM/YYYY)" type="text" />
                  <input v-model="item.ket_thuc" class="rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100" placeholder="Kết thúc" type="text" />
                  <textarea v-model="item.mo_ta" rows="3" class="md:col-span-2 rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100" placeholder="Điểm nổi bật, GPA, hoạt động học thuật..." />
                </div>
                <div class="mt-3 flex justify-end">
                  <button class="rounded-xl border border-rose-200 px-3 py-2 text-sm font-semibold text-rose-500 transition hover:bg-rose-50 dark:border-rose-900/40 dark:hover:bg-rose-900/10" type="button" @click="removeSectionItem('hoc_van_json', index)">
                    Xóa học vấn
                  </button>
                </div>
              </div>
            </div>
          </section>

          <section class="grid grid-cols-1 gap-6 xl:grid-cols-2">
            <div class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
              <div class="mb-4 flex items-center justify-between gap-4">
                <div>
                  <h2 class="text-lg font-bold text-slate-900 dark:text-white">Dự án</h2>
                  <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Nêu các dự án nổi bật để CV có chiều sâu hơn.</p>
                </div>
                <button class="rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white" type="button" @click="addSectionItem('du_an_json')">
                  Thêm dự án
                </button>
              </div>

              <div class="space-y-4">
                <div v-for="(item, index) in form.du_an_json" :key="`project-${index}`" class="rounded-3xl border border-slate-200 p-4 dark:border-slate-700">
                  <div class="grid grid-cols-1 gap-3">
                    <input v-model="item.ten" class="rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100" placeholder="Tên dự án" type="text" />
                    <input v-model="item.vai_tro" class="rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100" placeholder="Vai trò" type="text" />
                    <input v-model="item.cong_nghe" class="rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100" placeholder="Công nghệ" type="text" />
                    <input v-model="item.link" class="rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100" placeholder="Link demo / GitHub" type="text" />
                    <textarea v-model="item.mo_ta" rows="3" class="rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100" placeholder="Mô tả dự án và kết quả nổi bật." />
                  </div>
                  <div class="mt-3 flex justify-end">
                    <button class="rounded-xl border border-rose-200 px-3 py-2 text-sm font-semibold text-rose-500 transition hover:bg-rose-50 dark:border-rose-900/40 dark:hover:bg-rose-900/10" type="button" @click="removeSectionItem('du_an_json', index)">
                      Xóa dự án
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
              <div class="mb-4 flex items-center justify-between gap-4">
                <div>
                  <h2 class="text-lg font-bold text-slate-900 dark:text-white">Chứng chỉ</h2>
                  <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Bổ sung các chứng chỉ hoặc khóa học đáng chú ý.</p>
                </div>
                <button class="rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white" type="button" @click="addSectionItem('chung_chi_json')">
                  Thêm chứng chỉ
                </button>
              </div>

              <div class="space-y-4">
                <div v-for="(item, index) in form.chung_chi_json" :key="`cert-${index}`" class="rounded-3xl border border-slate-200 p-4 dark:border-slate-700">
                  <div class="grid grid-cols-1 gap-3">
                    <input v-model="item.ten" class="rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100" placeholder="Tên chứng chỉ" type="text" />
                    <input v-model="item.don_vi" class="rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100" placeholder="Đơn vị cấp" type="text" />
                    <input v-model="item.nam" class="rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100" placeholder="Năm cấp" type="text" />
                  </div>
                  <div class="mt-3 flex justify-end">
                    <button class="rounded-xl border border-rose-200 px-3 py-2 text-sm font-semibold text-rose-500 transition hover:bg-rose-50 dark:border-rose-900/40 dark:hover:bg-rose-900/10" type="button" @click="removeSectionItem('chung_chi_json', index)">
                      Xóa chứng chỉ
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <section class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
            <div class="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
              <div>
                <h2 class="text-lg font-bold text-slate-900 dark:text-white">Template theo sở thích</h2>
                <p class="mt-2 max-w-2xl text-sm leading-7 text-slate-500 dark:text-slate-400">
                  Chỉ hiển thị các template phù hợp với chế độ bạn đang chọn. Bạn có thể đổi thủ công sau khi áp preset.
                </p>
              </div>
              <div class="flex flex-wrap gap-3">
                <button
                  class="inline-flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-200 dark:hover:bg-slate-800"
                  type="button"
                  @click="openPreviewModal"
                >
                  <span class="material-symbols-outlined text-[18px]">visibility</span>
                  Xem preview
                </button>
                <button
                  class="inline-flex items-center gap-2 rounded-2xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-700"
                  type="button"
                  @click="exportPreview"
                >
                  <span class="material-symbols-outlined text-[18px]">print</span>
                  In / Xuất PDF
                </button>
              </div>
            </div>

            <div class="mt-5 grid grid-cols-1 gap-3 lg:grid-cols-2 2xl:grid-cols-3">
              <button
                v-for="option in availableTemplates"
                :key="`template-${option.value}`"
                class="overflow-hidden rounded-2xl border text-left transition"
                :class="form.mau_cv === option.value
                  ? 'border-slate-900 bg-slate-900 text-white dark:border-slate-200 dark:bg-slate-100 dark:text-slate-900'
                  : 'border-slate-200 bg-white text-slate-700 hover:border-slate-300 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-200 dark:hover:border-slate-500'"
                type="button"
                @click="form.mau_cv = option.value"
              >
                <div class="aspect-[4/5] overflow-hidden border-b"
                  :class="form.mau_cv === option.value ? 'border-white/15 dark:border-slate-300/30' : 'border-slate-200 dark:border-slate-800'"
                >
                  <div class="relative h-full origin-top-left scale-[0.34] transform p-3 sm:scale-[0.4]">
                    <div class="absolute left-6 top-6 z-10 flex flex-wrap gap-2">
                      <span
                        v-if="recommendedTemplate === option.value"
                        class="rounded-full bg-emerald-600 px-3 py-1 text-[10px] font-bold uppercase tracking-[0.16em] text-white shadow-sm"
                      >
                        Đề xuất cho bạn
                      </span>
                      <span
                        v-for="badge in option.badges || []"
                        :key="`${option.value}-${badge}`"
                        class="rounded-full bg-slate-950/80 px-3 py-1 text-[10px] font-bold uppercase tracking-[0.16em] text-white shadow-sm"
                      >
                        {{ badge }}
                      </span>
                    </div>
                    <div class="min-h-[720px] min-w-[720px] overflow-hidden rounded-[22px] bg-white shadow-md">
                      <ProfileCvPreview
                        :profile="getTemplatePreviewProfile(option.value)"
                        :owner="currentCandidate"
                        compact
                      />
                    </div>
                  </div>
                </div>
                <div class="px-4 py-4">
                  <div class="flex items-start justify-between gap-3">
                    <div>
                      <p class="text-sm font-bold">{{ option.label }}</p>
                      <div class="mt-2 flex flex-wrap gap-2">
                        <span
                          v-if="recommendedTemplate === option.value"
                          class="rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.14em] text-emerald-700"
                          :class="form.mau_cv === option.value ? 'dark:border-emerald-300/40 dark:bg-emerald-100/70 dark:text-emerald-900' : ''"
                        >
                          Đề xuất cho bạn
                        </span>
                        <span
                          v-for="badge in option.badges || []"
                          :key="`${option.value}-${badge}-footer`"
                          class="rounded-full border px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.14em]"
                          :class="form.mau_cv === option.value
                            ? 'border-white/20 text-white/90 dark:border-slate-400 dark:text-slate-900'
                            : 'border-slate-200 text-slate-500 dark:border-slate-700 dark:text-slate-400'"
                        >
                          {{ badge }}
                        </span>
                      </div>
                      <p
                        class="mt-3 text-xs leading-6"
                        :class="form.mau_cv === option.value ? 'text-white/80 dark:text-slate-700' : 'text-slate-500 dark:text-slate-400'"
                      >
                        {{ option.description }}
                      </p>
                    </div>
                    <span
                      class="mt-0.5 inline-flex h-6 min-w-6 items-center justify-center rounded-full border px-1.5 text-[11px] font-bold"
                      :class="form.mau_cv === option.value
                        ? 'border-white/20 text-white dark:border-slate-400 dark:text-slate-900'
                        : 'border-slate-200 text-slate-400 dark:border-slate-700 dark:text-slate-500'"
                    >
                      {{ form.mau_cv === option.value ? 'Đang dùng' : 'Xem' }}
                    </span>
                  </div>
                </div>
              </button>
            </div>
          </section>

          <div class="flex flex-col gap-3 sm:flex-row sm:justify-end">
            <button
              class="rounded-2xl border border-slate-200 px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
              type="button"
              @click="router.push('/my-cv')"
            >
              Hủy
            </button>
            <button
              class="rounded-2xl bg-[#2463eb] px-5 py-3 text-sm font-bold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-300"
              :disabled="saving || !form.tieu_de_ho_so"
              type="button"
              @click="submitProfile"
            >
              {{ saving ? 'Đang lưu...' : editingProfileId ? 'Lưu thay đổi' : 'Tạo CV hệ thống' }}
            </button>
          </div>
        </template>
    </div>

    <div
      v-if="previewModalOpen"
      class="fixed inset-0 z-50 overflow-y-auto bg-slate-950/55 px-4 py-6 backdrop-blur-sm"
      @click.self="closePreviewModal"
    >
      <div class="mx-auto w-full max-w-5xl rounded-[28px] border border-slate-200 bg-white shadow-2xl dark:border-slate-800 dark:bg-slate-900">
        <div class="flex items-start justify-between border-b border-slate-100 px-6 py-5 dark:border-slate-800">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.28em] text-blue-500">Preview CV</p>
            <h3 class="mt-2 text-2xl font-bold text-slate-900 dark:text-white">{{ form.tieu_de_ho_so || 'CV hệ thống' }}</h3>
            <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
              Xem thử CV với dữ liệu bạn đang nhập trước khi lưu chính thức.
            </p>
          </div>
          <button
            class="rounded-full p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-800"
            type="button"
            @click="closePreviewModal"
          >
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>

        <div class="max-h-[calc(100vh-8rem)] overflow-y-auto px-6 py-6">
          <ProfileCvPreview :profile="previewProfile" :owner="currentCandidate" />
        </div>

        <div class="flex flex-col gap-3 border-t border-slate-100 px-6 py-5 sm:flex-row sm:justify-end dark:border-slate-800">
          <button
            class="rounded-2xl border border-slate-200 px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
            type="button"
            @click="closePreviewModal"
          >
            Đóng preview
          </button>
          <button
            class="rounded-2xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-700"
            type="button"
            @click="exportPreview"
          >
            In / Xuất PDF
          </button>
        </div>
      </div>
    </div>

    <div class="pointer-events-none fixed inset-x-0 bottom-5 z-40 flex justify-center px-4">
      <div class="pointer-events-auto flex items-center gap-3 rounded-full border border-slate-200 bg-white/95 px-3 py-3 shadow-2xl backdrop-blur dark:border-slate-700 dark:bg-slate-900/95">
        <button
          class="inline-flex items-center gap-2 rounded-full bg-[#2463eb] px-4 py-2.5 text-sm font-bold text-white transition hover:bg-blue-700"
          type="button"
          @click="openPreviewModal"
        >
          <span class="material-symbols-outlined text-[18px]">visibility</span>
          Xem preview
        </button>
        <button
          class="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 dark:border-slate-600 dark:bg-slate-950 dark:text-slate-200 dark:hover:bg-slate-800"
          type="button"
          @click="exportPreview"
        >
          <span class="material-symbols-outlined text-[18px]">print</span>
          In PDF
        </button>
      </div>
    </div>
  </div>
</template>
