<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { authService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'
import { updateStoredCandidate } from '@/utils/authStorage'

const notify = useNotify()

const loading = ref(false)
const saving = ref(false)
const avatarPreview = ref('')
const selectedAvatarFile = ref(null)

const form = reactive({
  ho_ten: '',
  email: '',
  so_dien_thoai: '',
  ngay_sinh: '',
  gioi_tinh: '',
  dia_chi: '',
  anh_dai_dien: '',
  ten_vai_tro: '',
})

const genderOptions = [
  { value: 'nam', label: 'Nam' },
  { value: 'nu', label: 'Nữ' },
  { value: 'khac', label: 'Khác' },
]

const avatarLetter = computed(() => (form.ho_ten || 'Ứng viên').trim().charAt(0).toUpperCase() || 'U')

const profileStrength = computed(() => {
  let score = 30
  if (form.ho_ten) score += 15
  if (form.email) score += 10
  if (form.so_dien_thoai) score += 10
  if (form.ngay_sinh) score += 10
  if (form.gioi_tinh) score += 5
  if (form.dia_chi) score += 10
  if (form.anh_dai_dien || avatarPreview.value) score += 10
  return Math.min(100, score)
})

const getAvatarUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `http://127.0.0.1:8000/storage/${path}`
}

const syncStoredUser = (user) => {
  if (!user) return
  updateStoredCandidate(user)
}

const fillForm = (user) => {
  form.ho_ten = user?.ho_ten || ''
  form.email = user?.email || ''
  form.so_dien_thoai = user?.so_dien_thoai || ''
  form.ngay_sinh = user?.ngay_sinh ? String(user.ngay_sinh).slice(0, 10) : ''
  form.gioi_tinh = user?.gioi_tinh || ''
  form.dia_chi = user?.dia_chi || ''
  form.anh_dai_dien = user?.anh_dai_dien || ''
  form.ten_vai_tro = user?.ten_vai_tro || 'Ứng viên'
  avatarPreview.value = user?.avatar_url || getAvatarUrl(user?.anh_dai_dien || '')
}

const fetchProfile = async () => {
  loading.value = true
  try {
    const response = await authService.getProfile()
    const user = response?.data || null
    fillForm(user)
    syncStoredUser(user)
  } catch (error) {
    notify.apiError(error, 'Không tải được hồ sơ cá nhân.')
  } finally {
    loading.value = false
  }
}

const handleAvatarChange = (event) => {
  const file = event.target.files?.[0]
  if (!file) return

  selectedAvatarFile.value = file
  avatarPreview.value = URL.createObjectURL(file)
}

const submitProfile = async () => {
  saving.value = true
  try {
    const payload = new FormData()
    payload.append('ho_ten', form.ho_ten)
    payload.append('email', form.email)
    payload.append('so_dien_thoai', form.so_dien_thoai || '')
    payload.append('ngay_sinh', form.ngay_sinh || '')
    payload.append('gioi_tinh', form.gioi_tinh || '')
    payload.append('dia_chi', form.dia_chi || '')

    if (selectedAvatarFile.value) {
      payload.append('anh_dai_dien', selectedAvatarFile.value)
    }

    const response = await authService.updateProfile(payload)
    const updatedUser = response?.data || null
    fillForm(updatedUser)
    syncStoredUser(updatedUser)
    selectedAvatarFile.value = null
    notify.success('Cập nhật hồ sơ cá nhân thành công.')
  } catch (error) {
    notify.apiError(error, 'Không thể cập nhật hồ sơ cá nhân.')
  } finally {
    saving.value = false
  }
}

onMounted(fetchProfile)
</script>

<template>
  <div class="max-w-5xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8">
    <aside class="lg:col-span-4 flex flex-col gap-6">
      <div class="bg-white dark:bg-slate-900 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-800">
        <div v-if="loading" class="space-y-4">
          <div class="mx-auto h-32 w-32 animate-pulse rounded-full bg-slate-100 dark:bg-slate-800"></div>
          <div class="h-6 animate-pulse rounded bg-slate-100 dark:bg-slate-800"></div>
          <div class="h-4 animate-pulse rounded bg-slate-100 dark:bg-slate-800"></div>
        </div>

        <div v-else class="flex flex-col items-center text-center">
          <div class="relative group">
            <div class="mb-4 flex size-32 items-center justify-center overflow-hidden rounded-full border-4 border-[#2463eb]/20 bg-slate-50 shadow-[0_12px_30px_rgba(15,23,42,0.18)]">
              <img
                v-if="avatarPreview"
                :src="avatarPreview"
                alt="Ảnh đại diện"
                class="h-full w-full object-cover"
              />
              <span v-else class="text-4xl font-bold text-[#2463eb]">{{ avatarLetter }}</span>
            </div>
            <label
              class="absolute bottom-3 right-1 flex size-11 cursor-pointer items-center justify-center rounded-full border-4 border-white bg-[#2463eb] text-white shadow-lg shadow-[#2463eb]/30 transition hover:bg-[#1f57cf] active:scale-95 dark:border-slate-900"
            >
              <span class="material-symbols-outlined text-[18px]">photo_camera</span>
              <input class="hidden" type="file" accept="image/*" @change="handleAvatarChange" />
            </label>
          </div>
          <h3 class="text-xl font-bold text-slate-900 dark:text-slate-100">{{ form.ho_ten || 'Ứng viên' }}</h3>
          <p class="text-slate-500 dark:text-slate-400 text-sm mb-4">{{ form.ten_vai_tro }}</p>
          <div class="w-full h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden mb-2">
            <div class="bg-[#2463eb] h-full rounded-full transition-all" :style="{ width: `${profileStrength}%` }"></div>
          </div>
          <p class="text-xs font-medium text-slate-400 mb-6">Hoàn thiện hồ sơ: {{ profileStrength }}%</p>
          <button
            class="w-full bg-[#2463eb] text-white font-bold py-2.5 rounded-lg hover:shadow-lg hover:shadow-[#2463eb]/30 transition-all disabled:opacity-60"
            :disabled="saving"
            type="button"
            @click="submitProfile"
          >
            {{ saving ? 'Đang cập nhật...' : 'Lưu hồ sơ cá nhân' }}
          </button>
        </div>
      </div>

      <div class="bg-white dark:bg-slate-900 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-800">
        <h4 class="font-bold mb-4 flex items-center gap-2">
          <span class="material-symbols-outlined text-[#2463eb]">badge</span> Tóm tắt tài khoản
        </h4>
        <div class="space-y-3 text-sm text-slate-600 dark:text-slate-300">
          <div class="rounded-lg border border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 p-4">
            <p class="text-xs uppercase tracking-wide text-slate-400">Email đăng nhập</p>
            <p class="mt-2 font-semibold text-slate-900 dark:text-white">{{ form.email || 'Chưa cập nhật' }}</p>
          </div>
          <div class="rounded-lg border border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 p-4">
            <p class="text-xs uppercase tracking-wide text-slate-400">Số điện thoại</p>
            <p class="mt-2 font-semibold text-slate-900 dark:text-white">{{ form.so_dien_thoai || 'Chưa cập nhật' }}</p>
          </div>
          <div class="rounded-lg border border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 p-4">
            <p class="text-xs uppercase tracking-wide text-slate-400">Địa chỉ</p>
            <p class="mt-2 font-semibold text-slate-900 dark:text-white">{{ form.dia_chi || 'Chưa cập nhật' }}</p>
          </div>
        </div>
      </div>
    </aside>

    <div class="lg:col-span-8 space-y-8">
      <section class="bg-white dark:bg-slate-900 rounded-xl p-8 shadow-sm border border-slate-200 dark:border-slate-800">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-xl font-bold flex items-center gap-2">
            <span class="material-symbols-outlined text-[#2463eb]">person</span> Thông tin cá nhân
          </h3>
          <span class="text-sm font-medium text-slate-400">Dữ liệu đang đồng bộ với tài khoản đăng nhập</span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="space-y-1">
            <label class="text-sm font-semibold text-slate-500 dark:text-slate-400">Họ và tên</label>
            <input
              v-model="form.ho_ten"
              class="w-full bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-800 rounded-lg py-2.5 px-4 focus:ring-2 focus:ring-[#2463eb] focus:border-transparent transition-all"
              type="text"
            />
          </div>
          <div class="space-y-1">
            <label class="text-sm font-semibold text-slate-500 dark:text-slate-400">Email</label>
            <input
              v-model="form.email"
              class="w-full bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-800 rounded-lg py-2.5 px-4 focus:ring-2 focus:ring-[#2463eb] focus:border-transparent transition-all"
              type="email"
            />
          </div>
          <div class="space-y-1">
            <label class="text-sm font-semibold text-slate-500 dark:text-slate-400">Số điện thoại</label>
            <input
              v-model="form.so_dien_thoai"
              class="w-full bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-800 rounded-lg py-2.5 px-4 focus:ring-2 focus:ring-[#2463eb] focus:border-transparent transition-all"
              type="tel"
            />
          </div>
          <div class="space-y-1">
            <label class="text-sm font-semibold text-slate-500 dark:text-slate-400">Ngày sinh</label>
            <input
              v-model="form.ngay_sinh"
              class="w-full bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-800 rounded-lg py-2.5 px-4 focus:ring-2 focus:ring-[#2463eb] focus:border-transparent transition-all"
              type="date"
            />
          </div>
          <div class="space-y-1">
            <label class="text-sm font-semibold text-slate-500 dark:text-slate-400">Giới tính</label>
            <select
              v-model="form.gioi_tinh"
              class="w-full bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-800 rounded-lg py-2.5 px-4 focus:ring-2 focus:ring-[#2463eb] focus:border-transparent transition-all"
            >
              <option value="">Chọn giới tính</option>
              <option v-for="option in genderOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </div>
          <div class="md:col-span-2 space-y-1">
            <label class="text-sm font-semibold text-slate-500 dark:text-slate-400">Địa chỉ</label>
            <input
              v-model="form.dia_chi"
              class="w-full bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-800 rounded-lg py-2.5 px-4 focus:ring-2 focus:ring-[#2463eb] focus:border-transparent transition-all"
              type="text"
            />
          </div>
        </div>
      </section>

      <section class="bg-white dark:bg-slate-900 rounded-xl p-8 shadow-sm border border-slate-200 dark:border-slate-800">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-xl font-bold flex items-center gap-2">
            <span class="material-symbols-outlined text-[#2463eb]">tips_and_updates</span> Gợi ý hoàn thiện
          </h3>
          <span class="rounded-full bg-blue-50 px-3 py-1 text-xs font-bold text-blue-700">Dành cho hồ sơ ứng viên</span>
        </div>
        <div class="space-y-4 text-sm text-slate-600 dark:text-slate-300">
          <div class="rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-800/40 p-4">
            Điền đầy đủ số điện thoại, ngày sinh và địa chỉ để tăng độ tin cậy khi ứng tuyển.
          </div>
          <div class="rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-800/40 p-4">
            Nên sử dụng ảnh đại diện rõ khuôn mặt và chuyên nghiệp để hồ sơ cá nhân trông chỉn chu hơn.
          </div>
          <div class="rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-800/40 p-4">
            Sau khi cập nhật thông tin cá nhân, hãy hoàn thiện thêm phần `CV của tôi` để tăng khả năng ứng tuyển thành công.
          </div>
        </div>
      </section>
    </div>
  </div>
</template>
