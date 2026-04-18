<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { authService, profileService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'
import { getStoredCandidate, updateStoredCandidate } from '@/utils/authStorage'
import { formatDateVN } from '@/utils/dateTime'
import { hasBuilderCv } from '@/utils/profileCvBuilder'

const notify = useNotify()

const loading = ref(false)
const saving = ref(false)
const deletingId = ref(null)
const togglingId = ref(null)
const parsingId = ref(null)
const profiles = ref([])
const modalOpen = ref(false)
const editingProfileId = ref(null)
const selectedFile = ref(null)
const parseResultModalOpen = ref(false)
const parseResult = ref(null)
const applyingPersonalInfo = ref(false)
const currentCandidate = ref(getStoredCandidate())
const selectedPersonalFieldKeys = ref([])
const detailModalOpen = ref(false)
const selectedProfileDetail = ref(null)

const educationOptions = [
  { value: 'trung_hoc', label: 'Trung học' },
  { value: 'trung_cap', label: 'Trung cấp' },
  { value: 'cao_dang', label: 'Cao đẳng' },
  { value: 'dai_hoc', label: 'Đại học' },
  { value: 'thac_si', label: 'Thạc sĩ' },
  { value: 'tien_si', label: 'Tiến sĩ' },
  { value: 'khac', label: 'Khác' },
]

const form = reactive({
  tieu_de_ho_so: '',
  muc_tieu_nghe_nghiep: '',
  trinh_do: '',
  kinh_nghiem_nam: '',
  mo_ta_ban_than: '',
  trang_thai: 1,
})

const totalProfiles = computed(() => profiles.value.length)
const publicProfiles = computed(() => profiles.value.filter((item) => Number(item.trang_thai) === 1).length)
const withFiles = computed(() => profiles.value.filter((item) => item.file_cv).length)
const parsedProfiles = computed(() =>
  profiles.value.filter((item) => Number(item?.parsing?.parse_status) === 1).length
)

const formatDate = (value) => {
  return formatDateVN(value)
}

const statusMeta = (value) => {
  if (Number(value) === 1) {
    return {
      label: 'Công khai',
      classes: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
      dot: 'bg-green-500',
      action: 'Ẩn',
      actionIcon: 'visibility_off',
      actionClass: 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800',
    }
  }

  return {
    label: 'Đã ẩn',
    classes: 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400',
    dot: 'bg-slate-400',
    action: 'Hiện',
    actionIcon: 'visibility',
    actionClass: 'text-green-600 hover:bg-green-50 dark:hover:bg-green-900/20',
  }
}

const degreeLabel = (value) => {
  return educationOptions.find((option) => option.value === value)?.label || 'Chưa cập nhật'
}

const parseStatusMeta = (profile) => {
  const parsing = profile?.parsing

  if (!profile?.file_cv && !hasBuilderCv(profile)) {
    return {
      label: 'Chưa có dữ liệu CV',
      classes: 'bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400',
      icon: 'upload_file',
    }
  }

  if (!parsing) {
    return {
      label: 'Chưa parse',
      classes: 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300',
      icon: 'psychology_alt',
    }
  }

  if (Number(parsing.parse_status) === 1) {
    return {
      label: 'Đã parse',
      classes: 'bg-violet-100 text-violet-700 dark:bg-violet-900/30 dark:text-violet-300',
      icon: 'check_circle',
    }
  }

  if (Number(parsing.parse_status) === 2) {
    return {
      label: 'Parse lỗi',
      classes: 'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-300',
      icon: 'error',
    }
  }

  return {
    label: 'Đang parse',
    classes: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300',
    icon: 'hourglass_top',
  }
}

const cvFileUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `http://127.0.0.1:8000/storage/${path}`
}

const formatDisplayText = (value) => {
  const text = String(value || '')
    .replace(/[_-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()

  if (!text) return ''

  return text.charAt(0).toUpperCase() + text.slice(1)
}

const normalizedSkillItems = (value) => {
  if (!Array.isArray(value)) return []

  return value
    .map((item) => {
      if (typeof item === 'string') return formatDisplayText(item)
      if (!item || typeof item !== 'object') return ''
      return formatDisplayText(item.skill_name || item.name || item.skill || item.keyword || '')
    })
    .filter(Boolean)
    .filter((item, index, array) => array.indexOf(item) === index)
}

const normalizedSectionItems = (value) => {
  if (!Array.isArray(value)) return []

  return value
    .map((item) => {
      if (typeof item === 'string') return formatDisplayText(item)
      if (!item || typeof item !== 'object') return ''

      const ignoredKeys = ['confidence', 'score', 'type', 'label', 'raw_text']
      const parts = Object.entries(item)
        .filter(([key, raw]) => !ignoredKeys.includes(key) && raw !== null && raw !== undefined && String(raw).trim() !== '')
        .map(([, raw]) => formatDisplayText(raw))
        .filter(Boolean)

      return parts.join(' • ')
    })
    .filter(Boolean)
    .filter((item, index, array) => array.indexOf(item) === index)
}

const parsedSkills = computed(() => normalizedSkillItems(parseResult.value?.parsed_skills_json).slice(0, 12))
const parsedEducation = computed(() => normalizedSectionItems(parseResult.value?.parsed_education_json).slice(0, 8))
const parsedExperience = computed(() => normalizedSectionItems(parseResult.value?.parsed_experience_json).slice(0, 8))
const normalizedParsedPhone = computed(() => {
  const raw = String(parseResult.value?.parsed_phone || '').replace(/\D/g, '')
  if (/^0\d{9}$/.test(raw)) return raw
  if (/^84\d{9}$/.test(raw)) return `0${raw.slice(2)}`
  return ''
})
const candidateSnapshot = computed(() => currentCandidate.value || {})
const availablePersonalFields = computed(() => {
  const fields = []

  if (String(parseResult.value?.parsed_name || '').trim()) {
    fields.push({
      key: 'ho_ten',
      label: 'Họ và tên',
      currentValue: candidateSnapshot.value?.ho_ten || 'Chưa cập nhật',
      parsedValue: String(parseResult.value.parsed_name).trim(),
    })
  }

  if (String(parseResult.value?.parsed_email || '').trim()) {
    fields.push({
      key: 'email',
      label: 'Email',
      currentValue: candidateSnapshot.value?.email || 'Chưa cập nhật',
      parsedValue: String(parseResult.value.parsed_email).trim(),
    })
  }

  if (normalizedParsedPhone.value) {
    fields.push({
      key: 'so_dien_thoai',
      label: 'Số điện thoại',
      currentValue: candidateSnapshot.value?.so_dien_thoai || 'Chưa cập nhật',
      parsedValue: normalizedParsedPhone.value,
    })
  }

  return fields
})

const resetForm = () => {
  form.tieu_de_ho_so = ''
  form.muc_tieu_nghe_nghiep = ''
  form.trinh_do = ''
  form.kinh_nghiem_nam = ''
  form.mo_ta_ban_than = ''
  form.trang_thai = 1
  selectedFile.value = null
  editingProfileId.value = null
}

const fillForm = (profile) => {
  form.tieu_de_ho_so = profile?.tieu_de_ho_so || ''
  form.muc_tieu_nghe_nghiep = profile?.muc_tieu_nghe_nghiep || ''
  form.trinh_do = profile?.trinh_do || ''
  form.kinh_nghiem_nam = profile?.kinh_nghiem_nam ?? ''
  form.mo_ta_ban_than = profile?.mo_ta_ban_than || ''
  form.trang_thai = Number(profile?.trang_thai ?? 1)
  selectedFile.value = null
}

const fetchProfiles = async () => {
  loading.value = true
  try {
    const response = await profileService.getProfiles({
      per_page: 100,
      sort_by: 'updated_at',
      sort_dir: 'desc',
    })
    const payload = response?.data || {}
    profiles.value = payload.data || []
  } catch (error) {
    profiles.value = []
    notify.apiError(error, 'Không tải được danh sách hồ sơ/CV.')
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  resetForm()
  modalOpen.value = true
}

const openEditModal = (profile) => {
  editingProfileId.value = profile.id
  fillForm(profile)
  modalOpen.value = true
}

const openDetailModal = (profile) => {
  selectedProfileDetail.value = profile
  detailModalOpen.value = true
}

const closeDetailModal = () => {
  detailModalOpen.value = false
  selectedProfileDetail.value = null
}

const closeModal = () => {
  if (saving.value) return
  modalOpen.value = false
  resetForm()
}

const handleFileChange = (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  selectedFile.value = file
}

const buildFormData = () => {
  const payload = new FormData()
  payload.append('tieu_de_ho_so', form.tieu_de_ho_so)
  payload.append('muc_tieu_nghe_nghiep', form.muc_tieu_nghe_nghiep || '')
  payload.append('trinh_do', form.trinh_do || '')
  payload.append('kinh_nghiem_nam', String(form.kinh_nghiem_nam || 0))
  payload.append('mo_ta_ban_than', form.mo_ta_ban_than || '')
  payload.append('trang_thai', String(form.trang_thai))
  if (selectedFile.value) {
    payload.append('file_cv', selectedFile.value)
  }
  return payload
}

const submitProfile = async () => {
  saving.value = true
  try {
    const payload = buildFormData()
    if (editingProfileId.value) {
      await profileService.updateProfile(editingProfileId.value, payload)
      notify.success('Cập nhật hồ sơ thành công.')
    } else {
      await profileService.createProfile(payload)
      notify.success('Tạo hồ sơ mới thành công.')
    }
    modalOpen.value = false
    resetForm()
    await fetchProfiles()
  } catch (error) {
    notify.apiError(error, 'Không thể lưu hồ sơ/CV.')
  } finally {
    saving.value = false
  }
}

const toggleProfileStatus = async (profile) => {
  if (togglingId.value) return
  togglingId.value = profile.id
  try {
    await profileService.toggleProfileStatus(profile.id)
    notify.success(`Đã ${Number(profile.trang_thai) === 1 ? 'ẩn' : 'công khai'} hồ sơ.`)
    await fetchProfiles()
  } catch (error) {
    notify.apiError(error, 'Không thể cập nhật trạng thái hồ sơ.')
  } finally {
    togglingId.value = null
  }
}

const deleteProfile = async (profile) => {
  if (deletingId.value) return
  const confirmed = window.confirm(`Bạn có chắc muốn xóa hồ sơ "${profile.tieu_de_ho_so}" không?`)
  if (!confirmed) return

  deletingId.value = profile.id
  try {
    await profileService.deleteProfile(profile.id)
    notify.success('Đã xóa hồ sơ thành công.')
    await fetchProfiles()
  } catch (error) {
    notify.apiError(error, 'Không thể xóa hồ sơ.')
  } finally {
    deletingId.value = null
  }
}

const openParseResultModal = (result) => {
  currentCandidate.value = getStoredCandidate()
  parseResult.value = result
  selectedPersonalFieldKeys.value = [
    String(result?.parsed_name || '').trim() ? 'ho_ten' : null,
    String(result?.parsed_email || '').trim() ? 'email' : null,
    (() => {
      const raw = String(result?.parsed_phone || '').replace(/\D/g, '')
      return /^0\d{9}$/.test(raw) || /^84\d{9}$/.test(raw) ? 'so_dien_thoai' : null
    })(),
  ].filter(Boolean)
  parseResultModalOpen.value = true
}

const closeParseResultModal = () => {
  if (parsingId.value || applyingPersonalInfo.value) return
  parseResultModalOpen.value = false
  parseResult.value = null
  selectedPersonalFieldKeys.value = []
}

const applyPersonalInfoFromCv = async () => {
  if (applyingPersonalInfo.value) return

  const payload = {}

  if (selectedPersonalFieldKeys.value.includes('ho_ten') && String(parseResult.value?.parsed_name || '').trim()) {
    payload.ho_ten = String(parseResult.value.parsed_name).trim()
  }

  if (selectedPersonalFieldKeys.value.includes('email') && String(parseResult.value?.parsed_email || '').trim()) {
    payload.email = String(parseResult.value.parsed_email).trim()
  }

  if (selectedPersonalFieldKeys.value.includes('so_dien_thoai') && normalizedParsedPhone.value) {
    payload.so_dien_thoai = normalizedParsedPhone.value
  }

  if (!Object.keys(payload).length) {
    notify.warning('Hãy chọn ít nhất một trường hợp lệ để áp dụng từ CV.')
    return
  }

  applyingPersonalInfo.value = true
  try {
    const response = await authService.updateProfile(payload)
    const updatedUser = response?.data || null

    if (updatedUser) {
      updateStoredCandidate(updatedUser)
      currentCandidate.value = updatedUser
    }

    const appliedLabels = availablePersonalFields.value
      .filter((item) => selectedPersonalFieldKeys.value.includes(item.key))
      .map((item) => item.label)
      .join(', ')
    notify.success(`Đã áp dụng thông tin cá nhân từ CV: ${appliedLabels}.`)
  } catch (error) {
    notify.apiError(error, 'Không thể áp dụng thông tin cá nhân từ CV.')
  } finally {
    applyingPersonalInfo.value = false
  }
}

const parseProfile = async (profile) => {
  if (parsingId.value) return

  if (!profile.file_cv && !hasBuilderCv(profile)) {
    notify.warning('Hồ sơ này chưa có đủ dữ liệu để phân tích.')
    return
  }

  parsingId.value = profile.id
  try {
    const response = await profileService.parseProfileCv(profile.id)
    const payload = response?.data || {}
    const syncSummary = response?.sync_summary || null
    openParseResultModal({
      ...payload,
      profileTitle: profile.tieu_de_ho_so,
      syncSummary,
    })
    const updatedFields = Array.isArray(syncSummary?.updated_fields) ? syncSummary.updated_fields : []
    const syncedSkills = Number(syncSummary?.synced_skills || 0)
    const summaryParts = []

    if (updatedFields.length) {
      summaryParts.push(`đã tự điền ${updatedFields.length} trường hồ sơ`)
    }

    if (syncedSkills > 0) {
      summaryParts.push(`đồng bộ ${syncedSkills} kỹ năng`)
    }

    notify.success(
      summaryParts.length
        ? `Đã phân tích CV thành công, ${summaryParts.join(' và ')}.`
        : `Đã phân tích ${profile.file_cv ? 'CV file' : 'CV web'} thành công.`
    )
    await fetchProfiles()
  } catch (error) {
    notify.apiError(error, 'Không thể phân tích CV này.')
    await fetchProfiles()
  } finally {
    parsingId.value = null
  }
}

onMounted(fetchProfiles)
</script>

<template>
  <div>
    <div class="flex justify-between items-end mb-8">
      <div>
        <h1 class="text-2xl font-bold text-slate-900 dark:text-white">CV của tôi</h1>
        <p class="text-slate-500 text-sm mt-1">Quản lý hồ sơ xin việc, chuẩn bị nhiều phiên bản CV cho các vị trí khác nhau.</p>
      </div>
      <button
        class="bg-[#2463eb] text-white px-5 py-2.5 rounded-lg font-bold flex items-center gap-2 shadow-lg shadow-[#2463eb]/20 hover:bg-[#2463eb]/90 transition-all text-sm"
        type="button"
        @click="openCreateModal"
      >
        <span class="material-symbols-outlined text-xl">add</span>
        Tạo CV mới
      </button>
    </div>

    <div class="grid grid-cols-1 gap-4 mb-8 md:grid-cols-2 xl:grid-cols-4">
      <div class="bg-white dark:bg-slate-900 p-5 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800">
        <div class="flex items-center justify-between mb-2">
          <p class="text-slate-500 text-sm font-medium">Tổng hồ sơ</p>
          <div class="p-2 bg-[#2463eb]/10 rounded-lg text-[#2463eb]">
            <span class="material-symbols-outlined">description</span>
          </div>
        </div>
        <h3 class="text-2xl font-bold">{{ totalProfiles }}</h3>
      </div>
      <div class="bg-white dark:bg-slate-900 p-5 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800">
        <div class="flex items-center justify-between mb-2">
          <p class="text-slate-500 text-sm font-medium">Đang công khai</p>
          <div class="p-2 bg-green-100 dark:bg-green-900/20 rounded-lg text-green-600">
            <span class="material-symbols-outlined">visibility</span>
          </div>
        </div>
        <h3 class="text-2xl font-bold">{{ publicProfiles }}</h3>
      </div>
      <div class="bg-white dark:bg-slate-900 p-5 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800">
        <div class="flex items-center justify-between mb-2">
          <p class="text-slate-500 text-sm font-medium">Đã upload file CV</p>
          <div class="p-2 bg-amber-100 dark:bg-amber-900/20 rounded-lg text-amber-600">
            <span class="material-symbols-outlined">upload_file</span>
          </div>
        </div>
        <h3 class="text-2xl font-bold">{{ withFiles }}</h3>
      </div>
      <div class="bg-white dark:bg-slate-900 p-5 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800">
        <div class="flex items-center justify-between mb-2">
          <p class="text-slate-500 text-sm font-medium">Đã AI parse</p>
          <div class="p-2 bg-violet-100 dark:bg-violet-900/20 rounded-lg text-violet-600">
            <span class="material-symbols-outlined">psychology_alt</span>
          </div>
        </div>
        <h3 class="text-2xl font-bold">{{ parsedProfiles }}</h3>
      </div>
    </div>

    <div v-if="loading" class="space-y-4">
      <div
        v-for="index in 3"
        :key="index"
        class="h-32 animate-pulse rounded-xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900"
      />
    </div>

    <div v-else-if="!profiles.length" class="rounded-2xl border border-dashed border-slate-300 bg-white px-6 py-14 text-center shadow-sm dark:border-slate-700 dark:bg-slate-900">
      <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-slate-100 dark:bg-slate-800">
        <span class="material-symbols-outlined text-3xl text-slate-500">description</span>
      </div>
      <h2 class="mt-5 text-xl font-bold text-slate-900 dark:text-white">Bạn chưa có hồ sơ nào</h2>
      <p class="mx-auto mt-3 max-w-xl text-sm leading-7 text-slate-500 dark:text-slate-400">
        Tạo hồ sơ đầu tiên để bắt đầu ứng tuyển. Bạn có thể chuẩn bị nhiều phiên bản CV cho các vị trí khác nhau.
      </p>
      <button
        class="mt-6 inline-flex rounded-xl bg-[#2463eb] px-5 py-3 text-sm font-bold text-white transition hover:bg-blue-700"
        type="button"
        @click="openCreateModal"
      >
        Tạo hồ sơ đầu tiên
      </button>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="profile in profiles"
        :key="profile.id"
        class="bg-white dark:bg-slate-900 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-800 hover:border-[#2463eb]/40 transition-all"
      >
        <div class="flex flex-col md:flex-row md:items-center gap-4 justify-between">
          <div class="flex items-center gap-4">
            <div class="size-14 bg-[#2463eb]/10 rounded-xl flex items-center justify-center shrink-0">
              <span class="material-symbols-outlined text-[#2463eb] text-3xl">description</span>
            </div>
            <div>
              <div class="flex flex-wrap items-center gap-3 mb-1">
                <h3 class="font-bold text-lg text-slate-900 dark:text-white">{{ profile.tieu_de_ho_so }}</h3>
                <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold" :class="statusMeta(profile.trang_thai).classes">
                  <span class="size-1.5 rounded-full" :class="statusMeta(profile.trang_thai).dot"></span>
                  {{ statusMeta(profile.trang_thai).label }}
                </span>
                <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold" :class="parseStatusMeta(profile).classes">
                  <span class="material-symbols-outlined text-[12px]">{{ parseStatusMeta(profile).icon }}</span>
                  {{ parseStatusMeta(profile).label }}
                </span>
              </div>
              <p class="text-slate-500 text-sm">
                Cập nhật lần cuối: {{ formatDate(profile.updated_at) }}
                <span v-if="profile.file_cv">• Có file CV</span>
                <span v-else>• Chưa upload file CV</span>
              </p>
              <div class="flex flex-wrap gap-2 mt-2">
                <span class="text-xs bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded font-medium">
                  {{ degreeLabel(profile.trinh_do) }}
                </span>
                <span class="text-xs bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded font-medium">
                  {{ profile.kinh_nghiem_nam ?? 0 }} năm kinh nghiệm
                </span>
              </div>
              <p v-if="profile.muc_tieu_nghe_nghiep" class="mt-3 max-w-3xl text-sm text-slate-500 dark:text-slate-400 line-clamp-2">
                {{ profile.muc_tieu_nghe_nghiep }}
              </p>
            </div>
          </div>

          <div class="flex flex-wrap items-center gap-2 shrink-0">
            <a
              v-if="profile.file_cv"
              :href="cvFileUrl(profile.file_cv)"
              class="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              target="_blank"
              rel="noopener noreferrer"
            >
              <span class="material-symbols-outlined text-[18px]">download</span> Tải xuống
            </a>
            <button
              class="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors"
              :class="statusMeta(profile.trang_thai).actionClass"
              type="button"
              @click="toggleProfileStatus(profile)"
            >
              <span class="material-symbols-outlined text-[18px]">
                {{ togglingId === profile.id ? 'hourglass_top' : statusMeta(profile.trang_thai).actionIcon }}
              </span>
              {{ statusMeta(profile.trang_thai).action }}
            </button>
            <button
              class="flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-bold text-slate-700 bg-slate-100 hover:bg-slate-900 hover:text-white transition-all dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700"
              type="button"
              @click="openDetailModal(profile)"
            >
              <span class="material-symbols-outlined text-[18px]">article</span> Xem chi tiết
            </button>
            <button
              class="flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-bold text-violet-600 bg-violet-600/10 hover:bg-violet-600 hover:text-white transition-all disabled:cursor-not-allowed disabled:opacity-60"
              :disabled="parsingId === profile.id"
              type="button"
              @click="parseProfile(profile)"
            >
              <span class="material-symbols-outlined text-[18px]">
                {{ parsingId === profile.id ? 'hourglass_top' : 'auto_awesome' }}
              </span>
              {{ parsingId === profile.id ? 'Đang parse...' : 'Parse CV' }}
            </button>
            <button
              class="flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-bold text-[#2463eb] bg-[#2463eb]/10 hover:bg-[#2463eb] hover:text-white transition-all"
              type="button"
              @click="openEditModal(profile)"
            >
              <span class="material-symbols-outlined text-[18px]">edit</span> Chỉnh sửa
            </button>
            <button
              class="flex items-center justify-center size-9 rounded-lg text-red-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
              type="button"
              @click="deleteProfile(profile)"
            >
              <span class="material-symbols-outlined text-[18px]">
                {{ deletingId === profile.id ? 'hourglass_top' : 'delete' }}
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="mt-6">
      <button
        class="w-full flex items-center justify-center gap-3 p-6 border-2 border-dashed border-slate-200 dark:border-slate-800 rounded-xl text-slate-500 hover:border-[#2463eb] hover:text-[#2463eb] transition-all group"
        type="button"
        @click="openCreateModal"
      >
        <span class="material-symbols-outlined text-2xl group-hover:scale-110 transition-transform">note_add</span>
        <span class="font-medium">Tạo thêm hồ sơ để ứng tuyển nhiều vị trí khác nhau</span>
      </button>
    </div>

    <div
      v-if="modalOpen"
      class="fixed inset-0 z-50 overflow-y-auto bg-slate-950/55 backdrop-blur-sm"
      @click.self="closeModal"
    >
      <div class="flex min-h-full items-center justify-center px-4 py-6">
        <div class="flex max-h-[calc(100vh-3rem)] w-full max-w-3xl flex-col overflow-hidden rounded-[28px] border border-slate-200 bg-white shadow-2xl">
        <div class="flex items-start justify-between border-b border-slate-100 px-6 py-5">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.28em] text-blue-500">{{ editingProfileId ? 'Chỉnh sửa hồ sơ' : 'Tạo hồ sơ mới' }}</p>
            <h3 class="mt-2 text-2xl font-bold text-slate-900">
              {{ editingProfileId ? 'Cập nhật hồ sơ ứng tuyển' : 'Chuẩn bị hồ sơ ứng tuyển mới' }}
            </h3>
          </div>
          <button
            class="rounded-full p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700"
            type="button"
            @click="closeModal"
          >
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>

        <div class="grid flex-1 grid-cols-1 gap-5 overflow-y-auto px-6 py-6 md:grid-cols-2">
          <div class="md:col-span-2">
            <label class="mb-2 block text-sm font-semibold text-slate-700">Tiêu đề hồ sơ</label>
            <input
              v-model="form.tieu_de_ho_so"
              class="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
              placeholder="Ví dụ: CV Backend Developer Laravel"
              type="text"
            />
          </div>

          <div>
            <label class="mb-2 block text-sm font-semibold text-slate-700">Trình độ</label>
            <select
              v-model="form.trinh_do"
              class="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
            >
              <option value="">Chọn trình độ</option>
              <option v-for="option in educationOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </div>

          <div>
            <label class="mb-2 block text-sm font-semibold text-slate-700">Số năm kinh nghiệm</label>
            <input
              v-model="form.kinh_nghiem_nam"
              min="0"
              max="50"
              class="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
              type="number"
            />
          </div>

          <div class="md:col-span-2">
            <label class="mb-2 block text-sm font-semibold text-slate-700">Mục tiêu nghề nghiệp</label>
            <textarea
              v-model="form.muc_tieu_nghe_nghiep"
              rows="4"
              class="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
              placeholder="Mô tả ngắn định hướng nghề nghiệp và vị trí bạn muốn ứng tuyển."
            />
          </div>

          <div class="md:col-span-2">
            <label class="mb-2 block text-sm font-semibold text-slate-700">Mô tả bản thân</label>
            <textarea
              v-model="form.mo_ta_ban_than"
              rows="4"
              class="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
              placeholder="Tóm tắt ngắn về kinh nghiệm, điểm mạnh và định hướng cá nhân."
            />
          </div>

          <div>
            <label class="mb-2 block text-sm font-semibold text-slate-700">Trạng thái hồ sơ</label>
            <select
              v-model="form.trang_thai"
              class="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
            >
              <option :value="1">Công khai</option>
              <option :value="0">Ẩn</option>
            </select>
          </div>

          <div>
            <label class="mb-2 block text-sm font-semibold text-slate-700">File CV (PDF/DOC/DOCX)</label>
            <label class="flex min-h-[54px] cursor-pointer items-center rounded-2xl border border-dashed border-slate-300 px-4 py-3 text-sm text-slate-500 transition hover:border-blue-400 hover:text-blue-600">
              <input class="hidden" type="file" accept=".pdf,.doc,.docx" @change="handleFileChange" />
              {{ selectedFile ? selectedFile.name : editingProfileId ? 'Chọn file mới nếu muốn thay thế CV hiện tại' : 'Chọn file CV để upload' }}
            </label>
          </div>
        </div>

        <div class="flex flex-col gap-3 border-t border-slate-100 px-6 py-5 sm:flex-row sm:justify-end">
          <button
            class="rounded-2xl border border-slate-200 px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
            type="button"
            @click="closeModal"
          >
            Hủy
          </button>
          <button
            class="rounded-2xl bg-[#2463eb] px-5 py-3 text-sm font-bold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-300"
            :disabled="saving || !form.tieu_de_ho_so"
            type="button"
            @click="submitProfile"
          >
            {{ saving ? 'Đang lưu...' : editingProfileId ? 'Lưu thay đổi' : 'Tạo hồ sơ' }}
          </button>
        </div>
      </div>
      </div>
    </div>

    <div
      v-if="detailModalOpen && selectedProfileDetail"
      class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/55 px-4 py-6 backdrop-blur-sm"
      @click.self="closeDetailModal"
    >
      <div class="w-full max-w-3xl rounded-[28px] border border-slate-200 bg-white shadow-2xl">
        <div class="flex items-start justify-between border-b border-slate-100 px-6 py-5">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.28em] text-slate-500">Chi tiết hồ sơ</p>
            <h3 class="mt-2 text-2xl font-bold text-slate-900">
              {{ selectedProfileDetail.tieu_de_ho_so }}
            </h3>
          </div>
          <button
            class="rounded-full p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700"
            type="button"
            @click="closeDetailModal"
          >
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>

        <div class="max-h-[calc(100vh-10rem)] overflow-y-auto px-6 py-6">
          <div class="flex flex-wrap items-center gap-2">
            <span class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold" :class="statusMeta(selectedProfileDetail.trang_thai).classes">
              <span class="size-1.5 rounded-full" :class="statusMeta(selectedProfileDetail.trang_thai).dot"></span>
              {{ statusMeta(selectedProfileDetail.trang_thai).label }}
            </span>
            <span class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold" :class="parseStatusMeta(selectedProfileDetail).classes">
              <span class="material-symbols-outlined text-[14px]">{{ parseStatusMeta(selectedProfileDetail).icon }}</span>
              {{ parseStatusMeta(selectedProfileDetail).label }}
            </span>
          </div>

          <div class="mt-5 grid grid-cols-1 gap-4 md:grid-cols-2">
            <div class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4">
              <p class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">Trình độ</p>
              <p class="mt-2 text-base font-bold text-slate-900">{{ degreeLabel(selectedProfileDetail.trinh_do) }}</p>
            </div>
            <div class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4">
              <p class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">Kinh nghiệm</p>
              <p class="mt-2 text-base font-bold text-slate-900">{{ selectedProfileDetail.kinh_nghiem_nam ?? 0 }} năm</p>
            </div>
            <div class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4 md:col-span-2">
              <p class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">Cập nhật lần cuối</p>
              <p class="mt-2 text-base font-bold text-slate-900">{{ formatDate(selectedProfileDetail.updated_at) }}</p>
            </div>
          </div>

          <div class="mt-5 space-y-4">
            <div class="rounded-2xl border border-slate-200 px-4 py-4">
              <p class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">Mục tiêu nghề nghiệp</p>
              <p class="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-700">
                {{ selectedProfileDetail.muc_tieu_nghe_nghiep || 'Chưa cập nhật mục tiêu nghề nghiệp.' }}
              </p>
            </div>

            <div class="rounded-2xl border border-slate-200 px-4 py-4">
              <p class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">Mô tả bản thân</p>
              <p class="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-700">
                {{ selectedProfileDetail.mo_ta_ban_than || 'Chưa cập nhật mô tả bản thân.' }}
              </p>
            </div>

            <div class="rounded-2xl border border-slate-200 px-4 py-4">
              <p class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">File CV</p>
              <div class="mt-3">
                <a
                  v-if="selectedProfileDetail.file_cv"
                  :href="cvFileUrl(selectedProfileDetail.file_cv)"
                  class="inline-flex items-center gap-2 rounded-xl bg-[#2463eb]/10 px-4 py-2.5 text-sm font-semibold text-[#2463eb] transition hover:bg-[#2463eb] hover:text-white"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <span class="material-symbols-outlined text-[18px]">download</span>
                  Tải xuống CV
                </a>
                <p v-else class="text-sm text-slate-500">Hồ sơ này chưa có file CV.</p>
              </div>
            </div>
          </div>
        </div>

        <div class="flex justify-end border-t border-slate-100 px-6 py-5">
          <button
            class="rounded-2xl bg-slate-900 px-5 py-3 text-sm font-bold text-white transition hover:bg-slate-700"
            type="button"
            @click="closeDetailModal"
          >
            Đóng
          </button>
        </div>
      </div>
    </div>

    <div
      v-if="parseResultModalOpen"
      class="fixed inset-0 z-50 overflow-y-auto bg-slate-950/55 px-4 py-6 backdrop-blur-sm"
      @click.self="closeParseResultModal"
    >
      <div class="mx-auto w-full max-w-4xl rounded-[28px] border border-slate-200 bg-white shadow-2xl">
        <div class="flex items-start justify-between border-b border-slate-100 px-6 py-5">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.28em] text-violet-500">Kết quả AI Parse CV</p>
            <h3 class="mt-2 text-2xl font-bold text-slate-900">
              {{ parseResult?.profileTitle || 'Phân tích hồ sơ' }}
            </h3>
          </div>
          <button
            class="rounded-full p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700"
            type="button"
            @click="closeParseResultModal"
          >
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>

        <div class="max-h-[calc(100vh-10rem)] overflow-y-auto px-6 py-6">
          <div
            v-if="parseResult?.syncSummary"
            class="mb-6 rounded-3xl border border-emerald-200 bg-emerald-50/80 p-5"
          >
            <div class="flex items-start gap-3">
              <div class="rounded-2xl bg-emerald-100 p-2 text-emerald-600">
                <span class="material-symbols-outlined">auto_fix_high</span>
              </div>
              <div class="flex-1">
                <h4 class="text-base font-bold text-emerald-900">Đã tự động đồng bộ thông tin</h4>
                <p class="mt-1 text-sm text-emerald-800">
                  Hệ thống đã lấy kết quả AI parse để giảm thao tác nhập tay cho hồ sơ và kỹ năng cá nhân.
                </p>
                <div class="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2">
                  <div class="min-h-[150px] rounded-2xl bg-white/90 p-4">
                    <p class="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-500">Trường hồ sơ đã điền</p>
                    <div
                      v-if="Array.isArray(parseResult.syncSummary.updated_fields) && parseResult.syncSummary.updated_fields.length"
                      class="mt-3 flex flex-wrap gap-2"
                    >
                      <span
                        v-for="field in parseResult.syncSummary.updated_fields"
                        :key="field"
                        class="rounded-full bg-emerald-100 px-3 py-1.5 text-xs font-semibold text-emerald-700"
                      >
                        {{ field === 'trinh_do' ? 'Trình độ' : field === 'kinh_nghiem_nam' ? 'Kinh nghiệm' : field }}
                      </span>
                    </div>
                    <p v-else class="mt-3 text-sm text-slate-500">
                      Chưa tự điền thêm trường nào vì hồ sơ đã có dữ liệu sẵn hoặc AI chưa suy luận đủ chắc chắn.
                    </p>
                  </div>
                  <div class="min-h-[150px] rounded-2xl bg-white/90 p-4">
                    <p class="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-500">Kỹ năng đã đồng bộ</p>
                    <p class="mt-3 text-3xl font-bold text-emerald-700">
                      {{ Number(parseResult.syncSummary.synced_skills || 0) }}
                    </p>
                    <p class="mt-1 text-sm text-slate-500">
                      kỹ năng mới đã được thêm vào mục <span class="font-semibold text-slate-700">Kỹ năng của tôi</span>.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="mt-4 rounded-3xl border border-blue-200 bg-blue-50/70 p-5">
            <div class="flex flex-col gap-4">
              <div class="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
                <div class="max-w-2xl">
                  <h4 class="text-base font-bold text-blue-900">Áp dụng thông tin cá nhân từ CV</h4>
                  <p class="mt-1 text-sm text-blue-800">
                    Dùng nhanh kết quả AI parse để điền vào hồ sơ cá nhân, tránh nhập tay lại từ đầu.
                  </p>
                </div>

                <button
                  class="inline-flex min-w-[250px] items-center justify-center self-start rounded-2xl bg-blue-600 px-5 py-3 text-sm font-bold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-300"
                  :disabled="applyingPersonalInfo || !selectedPersonalFieldKeys.length"
                  type="button"
                  @click="applyPersonalInfoFromCv"
                >
                  {{ applyingPersonalInfo ? 'Đang áp dụng...' : 'Áp dụng thông tin cá nhân từ CV' }}
                </button>
              </div>

              <div v-if="availablePersonalFields.length" class="grid grid-cols-1 items-stretch gap-3 md:grid-cols-3">
                <label
                  v-for="field in availablePersonalFields"
                  :key="field.key"
                  class="flex h-full rounded-2xl border border-blue-200 bg-white/90 p-4 transition hover:border-blue-300"
                >
                  <div class="flex w-full items-start gap-3">
                    <input
                      v-model="selectedPersonalFieldKeys"
                      :value="field.key"
                      class="mt-1 h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                      type="checkbox"
                    />
                    <div class="flex min-h-[220px] flex-1 flex-col">
                      <p class="text-sm font-bold text-slate-900">{{ field.label }}</p>
                      <div class="mt-2 flex min-w-0 flex-1 flex-col gap-3 text-sm">
                        <div class="flex min-h-[0] min-w-0 flex-1 flex-col justify-center overflow-hidden rounded-xl bg-slate-50 px-4 py-3">
                          <p class="text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-400">Hiện tại</p>
                          <p class="mt-1 min-w-0 break-all leading-6 text-slate-700">{{ field.currentValue }}</p>
                        </div>
                        <div class="flex min-h-[0] min-w-0 flex-1 flex-col justify-center overflow-hidden rounded-xl bg-blue-50 px-4 py-3">
                          <p class="text-[11px] font-semibold uppercase tracking-[0.2em] text-blue-500">Từ CV</p>
                          <p class="mt-1 min-w-0 break-all leading-6 font-semibold text-blue-800">{{ field.parsedValue }}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </label>
              </div>
              <p v-else class="text-sm text-slate-500">
                Chưa có đủ dữ liệu cá nhân hợp lệ để tự động áp dụng.
              </p>
            </div>
          </div>

          <div class="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div class="rounded-3xl border border-slate-200 p-5">
              <div class="flex items-center justify-between gap-4">
                <h4 class="text-lg font-bold text-slate-900">Kỹ năng trích xuất</h4>
                <span class="rounded-full bg-violet-100 px-3 py-1 text-xs font-bold text-violet-600">
                  {{ parsedSkills.length }} kỹ năng
                </span>
              </div>
              <div v-if="parsedSkills.length" class="mt-4 flex flex-wrap gap-2">
                <span
                  v-for="skill in parsedSkills"
                  :key="skill"
                  class="rounded-full bg-slate-100 px-3 py-1.5 text-xs font-semibold text-slate-700"
                >
                  {{ skill }}
                </span>
              </div>
              <p v-else class="mt-4 text-sm text-slate-500">Chưa trích xuất được kỹ năng nổi bật.</p>
            </div>

            <div class="rounded-3xl border border-slate-200 p-5">
              <h4 class="text-lg font-bold text-slate-900">Học vấn</h4>
              <ul v-if="parsedEducation.length" class="mt-4 space-y-3 text-sm leading-7 text-slate-700">
                <li v-for="item in parsedEducation" :key="item" class="rounded-2xl bg-slate-50 px-4 py-3">
                  <div class="flex items-start gap-3">
                    <span class="mt-2 h-2 w-2 flex-shrink-0 rounded-full bg-violet-500"></span>
                    <p class="leading-7">{{ item }}</p>
                  </div>
                </li>
              </ul>
              <p v-else class="mt-4 text-sm text-slate-500">Chưa trích xuất được thông tin học vấn.</p>
            </div>
          </div>

          <div class="mt-6 rounded-3xl border border-slate-200 p-5">
            <h4 class="text-lg font-bold text-slate-900">Kinh nghiệm làm việc</h4>
            <ul v-if="parsedExperience.length" class="mt-4 space-y-3 text-sm leading-7 text-slate-700">
              <li v-for="item in parsedExperience" :key="item" class="rounded-2xl bg-slate-50 px-4 py-3">
                <div class="flex items-start gap-3">
                  <span class="mt-2 h-2 w-2 flex-shrink-0 rounded-full bg-blue-500"></span>
                  <p class="leading-7">{{ item }}</p>
                </div>
              </li>
            </ul>
            <p v-else class="mt-4 text-sm text-slate-500">Chưa trích xuất được phần kinh nghiệm.</p>
          </div>

          <div class="mt-5 rounded-2xl border border-dashed border-slate-200 bg-slate-50/70 px-4 py-3 text-sm text-slate-500">
            Hiện tại AI chỉ áp dụng trực tiếp được các trường cá nhân có độ tin cậy cao nhất:
            <span class="font-semibold text-slate-700">Họ và tên, Email, Số điện thoại</span>.
            Các trường như <span class="font-semibold text-slate-700">Ngày sinh, Giới tính, Địa chỉ</span> chưa được parser trả về ổn định nên chưa tự điền để tránh sai lệch dữ liệu.
          </div>
        </div>

        <div class="flex justify-end border-t border-slate-100 px-6 py-5">
          <button
            class="rounded-2xl bg-violet-600 px-5 py-3 text-sm font-bold text-white transition hover:bg-violet-700"
            type="button"
            @click="closeParseResultModal"
          >
            Đóng kết quả
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
