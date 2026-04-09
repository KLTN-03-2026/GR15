<template>
  <div class="mx-auto grid max-w-7xl grid-cols-1 gap-8 xl:grid-cols-[340px_minmax(0,1fr)]">
    <aside class="space-y-6">
      <section class="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div class="bg-[radial-gradient(circle_at_top_right,_rgba(37,99,235,0.18),_transparent_36%),linear-gradient(135deg,#0f172a_0%,#1e293b_60%,#0f172a_100%)] px-6 pb-8 pt-7 text-white">
          <div class="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.25em] text-sky-200">
            <span class="material-symbols-outlined text-sm">shield</span>
            Hồ sơ admin
          </div>
          <div class="mt-6 flex items-start gap-4">
            <button
              type="button"
              @click="triggerAvatarPicker"
              class="group relative flex h-20 w-20 items-center justify-center overflow-hidden rounded-3xl border border-white/10 bg-white/10 text-2xl font-black text-white transition hover:scale-[1.02]"
            >
              <img
                v-if="previewAvatar && !avatarLoadError"
                :src="previewAvatar"
                :alt="form.name"
                class="h-full w-full object-cover"
                @error="handleAvatarError"
              />
              <span v-else>{{ adminInitials }}</span>
              <span class="absolute inset-x-0 bottom-0 flex items-center justify-center gap-1 bg-slate-950/65 px-2 py-1 text-[11px] font-semibold opacity-0 transition group-hover:opacity-100">
                <span class="material-symbols-outlined text-[14px]">photo_camera</span>
                Đổi ảnh
              </span>
            </button>
            <div class="min-w-0">
              <p class="truncate text-2xl font-black">{{ form.name || 'Quản trị viên' }}</p>
              <p class="mt-1 truncate text-sm text-slate-300">{{ form.email || 'admin@example.com' }}</p>
              <p class="mt-3 inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1 text-xs font-semibold text-sky-100">
                <span class="material-symbols-outlined text-sm">verified_user</span>
                {{ roleLabel }}
              </p>
            </div>
          </div>
        </div>

        <div class="space-y-4 p-6">
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
              <span class="material-symbols-outlined text-[#2463eb]">admin_panel_settings</span>
              <p class="text-sm font-bold text-slate-900 dark:text-slate-100">Pham vi quan tri</p>
            </div>
            <ul class="mt-4 space-y-3 text-sm text-slate-600 dark:text-slate-300">
              <li class="flex items-center gap-3">
                <span class="material-symbols-outlined text-[18px] text-emerald-500">check_circle</span>
                Quản lý người dùng và quyền truy cập
              </li>
              <li class="flex items-center gap-3">
                <span class="material-symbols-outlined text-[18px] text-emerald-500">check_circle</span>
                Phê duyệt công ty và bài đăng tuyển dụng
              </li>
              <li class="flex items-center gap-3">
                <span class="material-symbols-outlined text-[18px] text-emerald-500">check_circle</span>
                Theo dõi thống kê và sức khỏe nền tảng
              </li>
            </ul>
          </div>
        </div>
      </section>

      <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div class="flex items-center gap-3">
          <div class="flex h-11 w-11 items-center justify-center rounded-2xl bg-[#2463eb]/10 text-[#2463eb]">
            <span class="material-symbols-outlined">notifications_active</span>
          </div>
          <div>
            <p class="text-sm font-bold text-slate-900 dark:text-slate-100">Lưu ý bảo mật</p>
            <p class="text-sm text-slate-500 dark:text-slate-400">Thay đổi thông tin tài khoản sẽ cập nhật ngay cho phiên hiện tại.</p>
          </div>
        </div>
      </section>
    </aside>

    <div class="space-y-8">
      <section class="rounded-3xl border border-slate-200 bg-white p-7 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div class="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
          <div>
            <p class="text-sm font-semibold uppercase tracking-[0.28em] text-slate-400">Tài khoản nội bộ</p>
            <h1 class="mt-2 text-3xl font-black tracking-tight text-slate-950 dark:text-white">Hồ sơ quản trị</h1>
            <p class="mt-2 max-w-2xl text-sm leading-6 text-slate-500 dark:text-slate-400">
              Quản lý thông tin cá nhân, cập nhật kênh liên hệ và giữ cho tài khoản quản trị luôn chính xác trong hệ thống.
            </p>
          </div>
          <div class="flex items-center gap-3">
            <button
              type="button"
              @click="resetForm"
              class="rounded-2xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-600 transition-colors hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
            >
              Đặt lại
            </button>
            <button
              type="button"
              @click="saveProfile"
              :disabled="isSaving || isLoading || isUploadingAvatar"
              class="inline-flex items-center gap-2 rounded-2xl bg-slate-950 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
            >
              <span v-if="!isSaving" class="material-symbols-outlined text-[18px]">save</span>
              <span v-else class="material-symbols-outlined animate-spin text-[18px]">progress_activity</span>
              {{ isSaving ? 'Đang lưu...' : 'Lưu thay đổi' }}
            </button>
          </div>
        </div>

        <div v-if="alert.message" :class="['mt-6 rounded-2xl border px-4 py-3 text-sm', alert.type === 'error' ? 'border-rose-200 bg-rose-50 text-rose-700' : 'border-emerald-200 bg-emerald-50 text-emerald-700']">
          {{ alert.message }}
        </div>

        <div v-if="isLoading" class="mt-8 flex items-center gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4 text-sm text-slate-500 dark:border-slate-800 dark:bg-slate-800/60">
          <span class="material-symbols-outlined animate-spin">progress_activity</span>
          Đang tải thông tin quản trị...
        </div>

        <form v-else class="mt-8 space-y-8" @submit.prevent="saveProfile">
          <section class="space-y-5">
            <div class="flex items-center gap-3">
              <div class="flex h-11 w-11 items-center justify-center rounded-2xl bg-[#2463eb]/10 text-[#2463eb]">
                <span class="material-symbols-outlined">badge</span>
              </div>
              <div>
                <h2 class="text-lg font-bold text-slate-950 dark:text-white">Thông tin cơ bản</h2>
                <p class="text-sm text-slate-500 dark:text-slate-400">Cập nhật các thông tin nhận diện hiển thị trong hệ thống.</p>
              </div>
            </div>

            <div class="grid grid-cols-1 gap-5 md:grid-cols-2">
              <div class="space-y-2 md:col-span-2">
                <label class="text-sm font-semibold text-slate-600 dark:text-slate-300">Ho va ten</label>
                <input v-model="form.name" type="text" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none transition focus:border-[#2463eb] focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-800" placeholder="Nhập họ và tên" />
              </div>
              <div class="space-y-2">
                <label class="text-sm font-semibold text-slate-600 dark:text-slate-300">Email</label>
                <input v-model="form.email" type="email" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none transition focus:border-[#2463eb] focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-800" placeholder="admin@example.com" />
              </div>
              <div class="space-y-2">
                <label class="text-sm font-semibold text-slate-600 dark:text-slate-300">So dien thoai</label>
                <input v-model="form.phone" type="tel" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none transition focus:border-[#2463eb] focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-800" placeholder="0901234567" />
              </div>
            </div>
          </section>

          <section class="space-y-5">
            <div class="flex items-center gap-3">
              <div class="flex h-11 w-11 items-center justify-center rounded-2xl bg-emerald-500/10 text-emerald-600">
                <span class="material-symbols-outlined">contact_mail</span>
              </div>
              <div>
                <h2 class="text-lg font-bold text-slate-950 dark:text-white">Liên hệ và hồ sơ</h2>
                <p class="text-sm text-slate-500 dark:text-slate-400">Thông tin này được dùng để hiển thị và hỗ trợ vận hành nội bộ.</p>
              </div>
            </div>

            <div class="grid grid-cols-1 gap-5 md:grid-cols-2">
              <div class="space-y-2">
                <label class="text-sm font-semibold text-slate-600 dark:text-slate-300">Ngày sinh</label>
                <input v-model="form.birthDate" type="date" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none transition focus:border-[#2463eb] focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-800" />
              </div>
              <div class="space-y-2">
                <label class="text-sm font-semibold text-slate-600 dark:text-slate-300">Giới tính</label>
                <select v-model="form.gender" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none transition focus:border-[#2463eb] focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-800">
                  <option value="">Chọn giới tính</option>
                  <option value="nam">Nam</option>
                  <option value="nu">Nữ</option>
                  <option value="khac">Khác</option>
                </select>
              </div>
              <div class="space-y-2 md:col-span-2">
                <label class="text-sm font-semibold text-slate-600 dark:text-slate-300">Địa chỉ</label>
                <input v-model="form.address" type="text" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none transition focus:border-[#2463eb] focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-800" placeholder="Nhập địa chỉ" />
              </div>
              <div class="space-y-2 md:col-span-2">
                <label class="text-sm font-semibold text-slate-600 dark:text-slate-300">Ảnh đại diện</label>
                <input
                  ref="avatarInputRef"
                  type="file"
                  accept="image/png,image/jpeg,image/jpg,image/webp"
                  class="hidden"
                  @change="handleAvatarChange"
                />
                <div class="rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-800/70">
                  <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                    <div class="min-w-0">
                      <p class="text-sm font-semibold text-slate-800 dark:text-slate-100">
                        {{ selectedAvatarName || 'Chưa chọn ảnh mới' }}
                      </p>
                      <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">
                        Chọn PNG, JPG hoặc WEBP. Ảnh sẽ được tải lên và cập nhật ngay sau khi chọn.
                      </p>
                    </div>
                    <div class="flex items-center gap-3">
                      <button
                        type="button"
                        @click="triggerAvatarPicker"
                        :disabled="isUploadingAvatar"
                        class="rounded-2xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-700"
                      >
                        {{ isUploadingAvatar ? 'Đang tải...' : 'Chọn ảnh' }}
                      </button>
                      <button
                        v-if="selectedAvatarFile || selectedAvatarName"
                        type="button"
                        @click="clearSelectedAvatar"
                        :disabled="isUploadingAvatar"
                        class="rounded-2xl px-4 py-2 text-sm font-semibold text-rose-600 transition hover:bg-rose-50 dark:hover:bg-rose-950/30"
                      >
                        Xóa
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </form>
      </section>

      <section class="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div class="flex items-center gap-3">
            <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-[#2463eb]/10 text-[#2463eb]">
              <span class="material-symbols-outlined">manage_accounts</span>
            </div>
            <div>
              <p class="text-sm text-slate-500 dark:text-slate-400">Mức độ sẵn sàng</p>
              <p class="text-xl font-black text-slate-950 dark:text-white">{{ profileCompletion }}%</p>
            </div>
          </div>
          <div class="mt-4 h-2 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
            <div class="h-full rounded-full bg-[#2463eb]" :style="{ width: `${profileCompletion}%` }"></div>
          </div>
        </article>

        <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div class="flex items-center gap-3">
            <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-amber-500/10 text-amber-600">
              <span class="material-symbols-outlined">security</span>
            </div>
            <div>
              <p class="text-sm text-slate-500 dark:text-slate-400">Xác thực</p>
              <p class="text-xl font-black text-slate-950 dark:text-white">Bearer Token</p>
            </div>
          </div>
          <p class="mt-4 text-sm leading-6 text-slate-500 dark:text-slate-400">Tài khoản đang dùng phiên xác thực qua API và sẽ bị thu hồi khi đăng xuất.</p>
        </article>

        <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div class="flex items-center gap-3">
            <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-500/10 text-emerald-600">
              <span class="material-symbols-outlined">history</span>
            </div>
            <div>
              <p class="text-sm text-slate-500 dark:text-slate-400">Cập nhật cuối</p>
              <p class="text-xl font-black text-slate-950 dark:text-white">{{ updatedAtLabel }}</p>
            </div>
          </div>
          <p class="mt-4 text-sm leading-6 text-slate-500 dark:text-slate-400">Dữ liệu được đồng bộ từ tài khoản đang đăng nhập và có thể lưu trực tiếp từ trang này.</p>
        </article>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { authService } from '@/services/api'
import { buildStorageAssetCandidates, resolvePrimaryStorageAssetUrl } from '@/utils/media'

const isLoading = ref(true)
const isSaving = ref(false)
const adminProfile = ref(null)
const avatarInputRef = ref(null)
const selectedAvatarFile = ref(null)
const selectedAvatarName = ref('')
const avatarPreviewUrl = ref('')
const avatarLoadError = ref(false)
const isUploadingAvatar = ref(false)
const persistedAvatarCandidates = ref([])
const persistedAvatarIndex = ref(0)
const alert = reactive({
  type: 'success',
  message: ''
})

const form = reactive({
  name: '',
  email: '',
  phone: '',
  birthDate: '',
  gender: '',
  address: '',
  avatar: ''
})

const formatDate = (value) => {
  if (!value) {
    return 'Chưa cập nhật'
  }

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return 'Chưa cập nhật'
  }

  return date.toLocaleDateString('vi-VN')
}

const normalizeProfile = (payload) => {
  const profile = payload?.data ?? payload ?? {}
  const avatarPath = profile.anh_dai_dien ?? profile.avatar ?? profile.hinh_anh ?? ''

  return {
    id: profile.id ?? null,
    name: profile.ho_ten ?? profile.name ?? profile.ten ?? '',
    email: profile.email ?? '',
    phone: profile.so_dien_thoai ?? profile.phone ?? '',
    birthDate: profile.ngay_sinh ?? '',
    gender: profile.gioi_tinh ?? '',
    address: profile.dia_chi ?? '',
    avatarPath,
    avatar: resolvePrimaryStorageAssetUrl(avatarPath),
    avatarCandidates: buildStorageAssetCandidates(avatarPath),
    role: profile.ten_vai_tro ?? profile.vai_tro ?? 'admin',
    status: profile.trang_thai,
    createdAt: profile.created_at ?? null,
    updatedAt: profile.updated_at ?? null
  }
}

const syncLocalAdminUser = (profile) => {
  localStorage.setItem('admin_user', JSON.stringify({
    ...JSON.parse(localStorage.getItem('admin_user') || '{}'),
    ho_ten: profile.name,
    email: profile.email,
    so_dien_thoai: profile.phone,
    ngay_sinh: profile.birthDate,
    gioi_tinh: profile.gender,
    dia_chi: profile.address,
    anh_dai_dien: profile.avatarPath || profile.avatar,
    anh_dai_dien_url: profile.avatar,
    anh_dai_dien_goc: profile.avatarPath || '',
    ten_vai_tro: profile.role,
    trang_thai: profile.status,
    created_at: profile.createdAt,
    updated_at: profile.updatedAt
  }))
}

const broadcastAdminProfileUpdate = (profile) => {
  if (typeof window === 'undefined') {
    return
  }

  window.dispatchEvent(new CustomEvent('admin-profile-updated', {
    detail: profile
  }))
}

const applyProfileToForm = (profile) => {
  form.name = profile.name
  form.email = profile.email
  form.phone = profile.phone
  form.birthDate = profile.birthDate
  form.gender = profile.gender
  form.address = profile.address
  form.avatar = profile.avatar
  persistedAvatarCandidates.value = profile.avatarCandidates || buildStorageAssetCandidates(profile.avatarPath || profile.avatar)
  persistedAvatarIndex.value = 0
  avatarLoadError.value = false
}

const loadProfile = async () => {
  isLoading.value = true
  alert.message = ''

  try {
    const response = await authService.getProfile()
    const normalized = normalizeProfile(response)
    adminProfile.value = normalized
    applyProfileToForm(normalized)
    syncLocalAdminUser(normalized)
    broadcastAdminProfileUpdate(normalized)
  } catch (error) {
    alert.type = 'error'
    alert.message = error.message || 'Không thể tải hồ sơ quản trị.'
  } finally {
    isLoading.value = false
  }
}

const resetForm = () => {
  if (!adminProfile.value) {
    return
  }

  alert.message = ''
  clearSelectedAvatar()
  applyProfileToForm(adminProfile.value)
}

const saveProfile = async () => {
  isSaving.value = true
  alert.message = ''

  try {
    const payload = new FormData()
    payload.append('ho_ten', form.name || '')
    payload.append('email', form.email || '')
    payload.append('so_dien_thoai', form.phone || '')
    payload.append('ngay_sinh', form.birthDate || '')
    payload.append('gioi_tinh', form.gender || '')
    payload.append('dia_chi', form.address || '')

    if (selectedAvatarFile.value) {
      payload.append('anh_dai_dien', selectedAvatarFile.value)
    }

    const response = await authService.updateProfile(payload)

    const normalized = normalizeProfile(response)
    adminProfile.value = {
      ...adminProfile.value,
      ...normalized
    }
    applyProfileToForm(adminProfile.value)
    syncLocalAdminUser(adminProfile.value)
    broadcastAdminProfileUpdate(adminProfile.value)
    clearSelectedAvatar()

    alert.type = 'success'
    alert.message = response.message || 'Cập nhật hồ sơ thành công.'
  } catch (error) {
    alert.type = 'error'
    alert.message = error.message || 'Không thể cập nhật hồ sơ.'
  } finally {
    isSaving.value = false
  }
}

const adminInitials = computed(() => {
  const words = (form.name || 'Quản trị viên')
    .trim()
    .split(/\s+/)
    .filter(Boolean)

  if (!words.length) {
    return 'AD'
  }

  if (words.length === 1) {
    return words[0].slice(0, 2).toUpperCase()
  }

  return `${words[0][0]}${words[words.length - 1][0]}`.toUpperCase()
})

const persistedAvatar = computed(() => persistedAvatarCandidates.value[persistedAvatarIndex.value] || form.avatar || '')
const previewAvatar = computed(() => avatarPreviewUrl.value || persistedAvatar.value || '')

const roleLabel = computed(() => {
  const role = adminProfile.value?.role

  if (role === 2 || role === '2' || String(role || '').toLowerCase() === 'admin') {
    return 'Quản trị viên hệ thống'
  }

  return role || 'Quản trị viên hệ thống'
})

const statusLabel = computed(() => {
  const status = adminProfile.value?.status

  if (status === 1 || status === '1' || status === true || typeof status === 'undefined' || status === null) {
    return 'Đang hoạt động'
  }

  return 'Đã khóa'
})

const createdAtLabel = computed(() => formatDate(adminProfile.value?.createdAt))
const updatedAtLabel = computed(() => formatDate(adminProfile.value?.updatedAt))

const profileCompletion = computed(() => {
  const fields = [form.name, form.email, form.phone, form.birthDate, form.gender, form.address, form.avatar]
  const completed = fields.filter((field) => Boolean(String(field || '').trim())).length
  return Math.round((completed / fields.length) * 100)
})

onMounted(() => {
  loadProfile()
})

onBeforeUnmount(() => {
  if (avatarPreviewUrl.value) {
    URL.revokeObjectURL(avatarPreviewUrl.value)
  }
})

const triggerAvatarPicker = () => {
  avatarInputRef.value?.click()
}

const clearSelectedAvatar = () => {
  selectedAvatarFile.value = null
  selectedAvatarName.value = ''
  avatarLoadError.value = false

  if (avatarPreviewUrl.value) {
    URL.revokeObjectURL(avatarPreviewUrl.value)
    avatarPreviewUrl.value = ''
  }

  if (avatarInputRef.value) {
    avatarInputRef.value.value = ''
  }
}

const uploadAvatarImmediately = async () => {
  if (!selectedAvatarFile.value) {
    return
  }

  isUploadingAvatar.value = true
  alert.message = ''

  try {
    const payload = new FormData()
    payload.append('ho_ten', form.name || '')
    payload.append('email', form.email || '')
    payload.append('so_dien_thoai', form.phone || '')
    payload.append('ngay_sinh', form.birthDate || '')
    payload.append('gioi_tinh', form.gender || '')
    payload.append('dia_chi', form.address || '')
    payload.append('anh_dai_dien', selectedAvatarFile.value)

    const response = await authService.updateProfile(payload)
    const normalized = normalizeProfile(response)

    adminProfile.value = {
      ...adminProfile.value,
      ...normalized
    }

    applyProfileToForm(adminProfile.value)
    syncLocalAdminUser(adminProfile.value)
    broadcastAdminProfileUpdate(adminProfile.value)
    clearSelectedAvatar()

    alert.type = 'success'
    alert.message = response.message || 'Đã cập nhật ảnh đại diện.'
  } catch (error) {
    alert.type = 'error'
    alert.message = error.message || 'Không thể cập nhật ảnh đại diện.'
  } finally {
    isUploadingAvatar.value = false
  }
}

const handleAvatarChange = (event) => {
  const [file] = event.target.files || []

  if (!file) {
    return
  }

  if (avatarPreviewUrl.value) {
    URL.revokeObjectURL(avatarPreviewUrl.value)
  }

  selectedAvatarFile.value = file
  selectedAvatarName.value = file.name
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
</script>
