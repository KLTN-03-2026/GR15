<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { authService } from '@/services/api'
import { emitAuthChanged, getStoredEmployer, updateStoredEmployer } from '@/utils/authStorage'
import { buildStorageAssetCandidates, resolvePrimaryStorageAssetUrl } from '@/utils/media'

const isLoading = ref(true)
const isSaving = ref(false)
const isUploadingAvatar = ref(false)
const avatarInputRef = ref(null)
const selectedAvatarFile = ref(null)
const avatarPreviewUrl = ref('')
const avatarLoadError = ref(false)
const employerProfile = ref(null)
const persistedAvatarCandidates = ref([])
const persistedAvatarIndex = ref(0)

const alert = reactive({
  type: 'success',
  message: '',
})

const form = reactive({
  ho_ten: '',
  email: '',
  so_dien_thoai: '',
  ngay_sinh: '',
  gioi_tinh: '',
  dia_chi: '',
  anh_dai_dien: '',
})

let alertTimeoutId = null

const clearAlertTimeout = () => {
  if (alertTimeoutId) {
    window.clearTimeout(alertTimeoutId)
    alertTimeoutId = null
  }
}

const setAlert = (type, message, options = {}) => {
  const { autoDismiss = type === 'success', duration = 3000 } = options

  clearAlertTimeout()
  alert.type = type
  alert.message = message

  if (autoDismiss && message) {
    alertTimeoutId = window.setTimeout(() => {
      alert.message = ''
      alertTimeoutId = null
    }, duration)
  }
}

const formatDate = (value) => {
  if (!value) return 'Chưa cập nhật'

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'Chưa cập nhật'

  return date.toLocaleDateString('vi-VN')
}

const normalizeDateInput = (value) => {
  if (!value) return ''

  const normalizedValue = String(value).trim()

  if (/^\d{4}-\d{2}-\d{2}$/.test(normalizedValue)) return normalizedValue
  if (/^\d{4}-\d{2}-\d{2}T/.test(normalizedValue)) return normalizedValue.slice(0, 10)

  const viDateMatch = normalizedValue.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/)
  if (viDateMatch) {
    const [, day, month, year] = viDateMatch
    return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`
  }

  const date = new Date(normalizedValue)
  if (Number.isNaN(date.getTime())) return ''

  return new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 10)
}

const normalizeProfile = (payload) => {
  const profile = payload?.data ?? payload ?? {}
  const currentStoredUser = getStoredEmployer() || {}
  const avatarPath = profile.anh_dai_dien ?? profile.avatar ?? profile.hinh_anh ?? ''
  const avatarUrl = profile.avatar_url ?? profile.anh_dai_dien_url ?? resolvePrimaryStorageAssetUrl(avatarPath)

  return {
    id: profile.id ?? null,
    ho_ten: profile.ho_ten ?? profile.name ?? profile.ten ?? '',
    email: profile.email ?? '',
    so_dien_thoai: profile.so_dien_thoai ?? profile.phone ?? '',
    ngay_sinh: normalizeDateInput(profile.ngay_sinh ?? ''),
    gioi_tinh: profile.gioi_tinh ?? '',
    dia_chi: profile.dia_chi ?? '',
    vai_tro: profile.vai_tro ?? currentStoredUser.vai_tro ?? 1,
    anh_dai_dien: avatarPath,
    avatar_url: avatarUrl,
    avatar_candidates: [
      ...(avatarUrl ? [avatarUrl] : []),
      ...buildStorageAssetCandidates(avatarPath),
    ].filter((value, index, array) => Boolean(value) && array.indexOf(value) === index),
    ten_vai_tro: profile.ten_vai_tro ?? profile.role ?? 'Nhà tuyển dụng',
    trang_thai: profile.trang_thai,
    created_at: profile.created_at ?? null,
    updated_at: profile.updated_at ?? null,
  }
}

const syncStoredEmployerProfile = (profile) => {
  if (!profile) return

  const currentStoredUser = getStoredEmployer() || {}

  updateStoredEmployer({
    ...currentStoredUser,
    ...profile,
    vai_tro: profile.vai_tro ?? currentStoredUser.vai_tro ?? 1,
  })
  emitAuthChanged()

  if (typeof window !== 'undefined') {
    window.dispatchEvent(new CustomEvent('employer-profile-updated', { detail: profile }))
  }
}

const applyProfileToForm = (profile) => {
  form.ho_ten = profile.ho_ten || ''
  form.email = profile.email || ''
  form.so_dien_thoai = profile.so_dien_thoai || ''
  form.ngay_sinh = profile.ngay_sinh || ''
  form.gioi_tinh = profile.gioi_tinh || ''
  form.dia_chi = profile.dia_chi || ''
  form.anh_dai_dien = profile.avatar_url || ''
  persistedAvatarCandidates.value = profile.avatar_candidates || []
  persistedAvatarIndex.value = 0
  avatarLoadError.value = false
}

const clearSelectedAvatar = () => {
  selectedAvatarFile.value = null
  avatarLoadError.value = false

  if (avatarPreviewUrl.value) {
    URL.revokeObjectURL(avatarPreviewUrl.value)
    avatarPreviewUrl.value = ''
  }

  if (avatarInputRef.value) {
    avatarInputRef.value.value = ''
  }
}

const loadProfile = async () => {
  isLoading.value = true
  clearAlertTimeout()
  alert.message = ''

  try {
    const response = await authService.getProfile()
    const normalized = normalizeProfile(response)
    employerProfile.value = normalized
    applyProfileToForm(normalized)
    syncStoredEmployerProfile(normalized)
  } catch (error) {
    setAlert('error', error.message || 'Không thể tải hồ sơ nhà tuyển dụng.', { autoDismiss: false })
  } finally {
    isLoading.value = false
  }
}

const refreshProfileFromServer = async () => {
  const response = await authService.getProfile()
  const normalized = normalizeProfile(response)
  employerProfile.value = normalized
  applyProfileToForm(normalized)
  syncStoredEmployerProfile(normalized)
  return normalized
}

const resetForm = () => {
  if (!employerProfile.value) return

  alert.message = ''
  clearSelectedAvatar()
  applyProfileToForm(employerProfile.value)
}

const saveProfile = async () => {
  isSaving.value = true
  alert.message = ''

  try {
    const payload = new FormData()
    payload.append('ho_ten', form.ho_ten || '')
    payload.append('email', form.email || '')
    payload.append('so_dien_thoai', form.so_dien_thoai || '')
    payload.append('ngay_sinh', form.ngay_sinh || '')
    payload.append('gioi_tinh', form.gioi_tinh || '')
    payload.append('dia_chi', form.dia_chi || '')

    if (selectedAvatarFile.value) {
      payload.append('anh_dai_dien', selectedAvatarFile.value)
    }

    const response = await authService.updateProfile(payload)
    await refreshProfileFromServer()
    clearSelectedAvatar()
    setAlert('success', response.message || 'Cập nhật hồ sơ thành công.')
  } catch (error) {
    setAlert('error', error.message || 'Không thể cập nhật hồ sơ.', { autoDismiss: false })
  } finally {
    isSaving.value = false
  }
}

const uploadAvatarImmediately = async () => {
  if (!selectedAvatarFile.value) return

  isUploadingAvatar.value = true
  alert.message = ''

  try {
    const payload = new FormData()
    payload.append('anh_dai_dien', selectedAvatarFile.value)

    const response = await authService.updateProfile(payload)
    await refreshProfileFromServer()
    clearSelectedAvatar()
    setAlert('success', response.message || 'Đã cập nhật ảnh đại diện.')
  } catch (error) {
    setAlert('error', error.message || 'Không thể cập nhật ảnh đại diện.', { autoDismiss: false })
  } finally {
    isUploadingAvatar.value = false
  }
}

const handleAvatarChange = (event) => {
  const [file] = event.target.files || []
  if (!file) return

  if (avatarPreviewUrl.value) {
    URL.revokeObjectURL(avatarPreviewUrl.value)
  }

  selectedAvatarFile.value = file
  avatarPreviewUrl.value = URL.createObjectURL(file)
  avatarLoadError.value = false
  uploadAvatarImmediately()
}

const handleAvatarError = () => {
  if (avatarPreviewUrl.value) {
    avatarLoadError.value = true
    return
  }

  if (persistedAvatarIndex.value < persistedAvatarCandidates.value.length - 1) {
    persistedAvatarIndex.value += 1
    return
  }

  avatarLoadError.value = true
}

const triggerAvatarPicker = () => {
  avatarInputRef.value?.click()
}

const employerInitials = computed(() => {
  const words = (form.ho_ten || 'Nhà tuyển dụng')
    .trim()
    .split(/\s+/)
    .filter(Boolean)

  if (!words.length) return 'NT'
  if (words.length === 1) return words[0].slice(0, 2).toUpperCase()

  return `${words[0][0]}${words[words.length - 1][0]}`.toUpperCase()
})

const roleLabel = computed(() => {
  const role = employerProfile.value?.ten_vai_tro

  if (role === 1 || role === '1') {
    return 'Nhà tuyển dụng'
  }

  return role || 'Nhà tuyển dụng'
})

const statusLabel = computed(() => {
  const status = employerProfile.value?.trang_thai

  if (status === 1 || status === '1' || status === true || status === undefined || status === null) {
    return 'Đang hoạt động'
  }

  return 'Đã khóa'
})

const createdAtLabel = computed(() => formatDate(employerProfile.value?.created_at))
const persistedAvatar = computed(() => persistedAvatarCandidates.value[persistedAvatarIndex.value] || form.anh_dai_dien || '')
const previewAvatar = computed(() => avatarPreviewUrl.value || persistedAvatar.value || '')

onMounted(() => {
  loadProfile()
})

onBeforeUnmount(() => {
  clearAlertTimeout()

  if (avatarPreviewUrl.value) {
    URL.revokeObjectURL(avatarPreviewUrl.value)
  }
})
</script>

<template>
  <div class="mx-auto grid max-w-6xl grid-cols-1 gap-6 xl:grid-cols-[320px_minmax(0,1fr)]">
    <aside class="space-y-5">
      <section class="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div class="bg-[radial-gradient(circle_at_top_right,_rgba(37,99,235,0.18),_transparent_36%),linear-gradient(135deg,#082f49_0%,#0f3f78_55%,#1d4ed8_100%)] px-6 pb-8 pt-7 text-white">
          <div class="mb-2 mt-3 flex items-start gap-4">
            <button
              type="button"
              class="group relative flex h-20 w-20 items-center justify-center overflow-hidden rounded-3xl border border-white/10 bg-white/10 text-2xl font-black text-white transition hover:scale-[1.02]"
              @click="triggerAvatarPicker"
            >
              <img
                v-if="previewAvatar && !avatarLoadError"
                :src="previewAvatar"
                :alt="form.ho_ten"
                class="h-full w-full object-cover"
                @error="handleAvatarError"
              />
              <span v-else>{{ employerInitials }}</span>
              <span class="absolute inset-x-0 bottom-0 flex items-center justify-center gap-1 bg-slate-950/65 px-2 py-1 text-[11px] font-semibold opacity-0 transition group-hover:opacity-100">
                <span class="material-symbols-outlined text-[14px]">photo_camera</span>
                {{ isUploadingAvatar ? 'Đang tải...' : 'Đổi ảnh' }}
              </span>
            </button>
            <div class="min-w-0">
              <p class="truncate text-2xl font-black">{{ form.ho_ten || 'Nhà tuyển dụng' }}</p>
              <p class="mt-1 truncate text-sm text-sky-100/90">{{ form.email || 'employer@example.com' }}</p>
              <p class="mt-3 inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1 text-xs font-semibold text-sky-50">
                <span class="material-symbols-outlined text-sm">business_center</span>
                {{ roleLabel }}
              </p>
            </div>
          </div>
        </div>

        <div class="space-y-4 p-5">
          <div class="rounded-2xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-800/60">
            <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Trạng thái</p>
            <div class="mt-3 flex items-center gap-3">
              <span class="inline-flex h-2.5 w-2.5 rounded-full bg-emerald-500"></span>
              <span class="text-sm font-semibold text-slate-700 dark:text-slate-200">{{ statusLabel }}</span>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <article class="rounded-2xl border border-slate-200 p-4 dark:border-slate-800">
              <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Ngày tạo</p>
              <p class="mt-3 text-sm font-semibold text-slate-800 dark:text-slate-100">{{ createdAtLabel }}</p>
            </article>
            <article class="rounded-2xl border border-slate-200 p-4 dark:border-slate-800">
              <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Phiên đăng nhập</p>
              <p class="mt-3 text-sm font-semibold text-slate-800 dark:text-slate-100">Bảo mật token</p>
            </article>
          </div>

          <div class="rounded-2xl border border-slate-200 p-4 dark:border-slate-800">
            <div class="flex items-center gap-2">
              <span class="material-symbols-outlined text-[#2463eb]">work_history</span>
              <p class="text-sm font-bold text-slate-900 dark:text-slate-100">Phạm vi công việc</p>
            </div>
            <p class="mt-3 text-sm leading-6 text-slate-600 dark:text-slate-300">
              Quản lý tin tuyển dụng, theo dõi ứng viên và phối hợp lịch phỏng vấn với công ty của bạn.
            </p>
          </div>
        </div>
      </section>
    </aside>

    <div class="space-y-6">
      <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <p class="text-sm font-semibold uppercase tracking-[0.28em] text-slate-400">Employer account</p>
            <h1 class="mt-2 text-3xl font-black tracking-tight text-slate-950 dark:text-white">Hồ sơ nhà tuyển dụng</h1>
          </div>
          <div class="flex items-center gap-3">
            <button
              type="button"
              class="rounded-2xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-600 transition-colors hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
              @click="resetForm"
            >
              Đặt lại
            </button>
            <button
              type="button"
              class="inline-flex items-center gap-2 rounded-2xl bg-slate-950 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
              :disabled="isSaving || isLoading"
              @click="saveProfile"
            >
              <span v-if="!isSaving" class="material-symbols-outlined text-[18px]">save</span>
              <span v-else class="material-symbols-outlined animate-spin text-[18px]">progress_activity</span>
              {{ isSaving ? 'Đang lưu...' : 'Lưu thay đổi' }}
            </button>
          </div>
        </div>

        <div
          v-if="alert.message"
          :class="[
            'mt-6 rounded-2xl border px-4 py-3 text-sm',
            alert.type === 'error'
              ? 'border-rose-200 bg-rose-50 text-rose-700'
              : 'border-emerald-200 bg-emerald-50 text-emerald-700',
          ]"
        >
          {{ alert.message }}
        </div>

        <input
          ref="avatarInputRef"
          type="file"
          accept="image/png,image/jpeg,image/jpg,image/webp"
          class="hidden"
          @change="handleAvatarChange"
        />

        <div
          v-if="isLoading"
          class="mt-6 flex items-center gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4 text-sm text-slate-500 dark:border-slate-800 dark:bg-slate-800/60"
        >
          <span class="material-symbols-outlined animate-spin">progress_activity</span>
          Đang tải thông tin nhà tuyển dụng...
        </div>

        <form v-else class="mt-6 space-y-6" @submit.prevent="saveProfile">
          <section class="rounded-2xl border border-slate-200 p-5 dark:border-slate-800">
            <div class="mb-5 flex items-center gap-3">
              <div class="flex h-11 w-11 items-center justify-center rounded-2xl bg-[#2463eb]/10 text-[#2463eb]">
                <span class="material-symbols-outlined">person</span>
              </div>
              <h2 class="text-xl font-bold text-slate-950 dark:text-white">Thông tin cá nhân</h2>
            </div>

            <div class="grid grid-cols-1 gap-5 md:grid-cols-2">
              <div class="space-y-2 md:col-span-2">
                <label class="text-sm font-semibold text-slate-600 dark:text-slate-300">Họ và tên</label>
                <input
                  v-model="form.ho_ten"
                  type="text"
                  class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none transition focus:border-[#2463eb] focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-800"
                  placeholder="Nhập họ và tên"
                />
              </div>
              <div class="space-y-2">
                <label class="text-sm font-semibold text-slate-600 dark:text-slate-300">Địa chỉ email</label>
                <input
                  v-model="form.email"
                  type="email"
                  class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none transition focus:border-[#2463eb] focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-800"
                  placeholder="employer@example.com"
                />
              </div>
              <div class="space-y-2">
                <label class="text-sm font-semibold text-slate-600 dark:text-slate-300">Số điện thoại</label>
                <input
                  v-model="form.so_dien_thoai"
                  type="tel"
                  class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none transition focus:border-[#2463eb] focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-800"
                  placeholder="0901234567"
                />
              </div>
              <div class="space-y-2">
                <label class="text-sm font-semibold text-slate-600 dark:text-slate-300">Ngày sinh</label>
                <input
                  v-model="form.ngay_sinh"
                  type="date"
                  class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none transition focus:border-[#2463eb] focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-800"
                />
              </div>
              <div class="space-y-2">
                <label class="text-sm font-semibold text-slate-600 dark:text-slate-300">Giới tính</label>
                <select
                  v-model="form.gioi_tinh"
                  class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none transition focus:border-[#2463eb] focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-800"
                >
                  <option value="">Chọn giới tính</option>
                  <option value="nam">Nam</option>
                  <option value="nu">Nữ</option>
                  <option value="khac">Khác</option>
                </select>
              </div>
              <div class="space-y-2 md:col-span-2">
                <label class="text-sm font-semibold text-slate-600 dark:text-slate-300">Địa chỉ</label>
                <input
                  v-model="form.dia_chi"
                  type="text"
                  class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none transition focus:border-[#2463eb] focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-800"
                  placeholder="Nhập địa chỉ"
                />
              </div>
            </div>
          </section>
        </form>
      </section>
    </div>
  </div>
</template>
