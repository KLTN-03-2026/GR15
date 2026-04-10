<script setup>
import { onMounted, reactive, ref } from 'vue'
import { authService } from '@/services/api'
import { updateStoredCandidate } from '@/utils/authStorage'
import { useNotify } from '@/composables/useNotify'

const notify = useNotify()
const loading = ref(false)
const saving = ref(false)

const form = reactive({
  ho_ten: '',
  email: '',
  so_dien_thoai: '',
  ngay_sinh: '',
  gioi_tinh: '',
  dia_chi: '',
})

const loadProfile = async () => {
  loading.value = true
  try {
    const response = await authService.getProfile()
    const user = response?.data || {}
    form.ho_ten = user.ho_ten || ''
    form.email = user.email || ''
    form.so_dien_thoai = user.so_dien_thoai || ''
    form.ngay_sinh = user.ngay_sinh || ''
    form.gioi_tinh = user.gioi_tinh || ''
    form.dia_chi = user.dia_chi || ''
  } catch (error) {
    notify.apiError(error, 'Không thể tải thông tin cá nhân.')
  } finally {
    loading.value = false
  }
}

const saveProfile = async () => {
  saving.value = true
  try {
    const response = await authService.updateProfile({ ...form })
    updateStoredCandidate(response?.data || { ...form })
    notify.success('Cập nhật thông tin cá nhân thành công.')
  } catch (error) {
    notify.apiError(error, 'Không thể cập nhật thông tin cá nhân.')
  } finally {
    saving.value = false
  }
}

onMounted(loadProfile)
</script>

<template>
  <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
    <div class="max-w-3xl">
      <p class="text-xs uppercase tracking-[0.3em] text-blue-600">Tài khoản</p>
      <h2 class="mt-2 text-3xl font-bold text-slate-900">Thông tin cá nhân</h2>
      <p class="mt-3 text-sm text-slate-600">Cập nhật dữ liệu cơ bản dùng cho hồ sơ, matching và career report.</p>
    </div>

    <div v-if="loading" class="mt-6 text-sm text-slate-500">Đang tải dữ liệu...</div>

    <form v-else class="mt-8 grid gap-5 md:grid-cols-2" @submit.prevent="saveProfile">
      <label class="block">
        <span class="mb-2 block text-sm font-medium text-slate-700">Họ và tên</span>
        <input v-model="form.ho_ten" class="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none focus:border-blue-400" />
      </label>
      <label class="block">
        <span class="mb-2 block text-sm font-medium text-slate-700">Email</span>
        <input v-model="form.email" type="email" class="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none focus:border-blue-400" />
      </label>
      <label class="block">
        <span class="mb-2 block text-sm font-medium text-slate-700">Số điện thoại</span>
        <input v-model="form.so_dien_thoai" class="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none focus:border-blue-400" />
      </label>
      <label class="block">
        <span class="mb-2 block text-sm font-medium text-slate-700">Ngày sinh</span>
        <input v-model="form.ngay_sinh" type="date" class="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none focus:border-blue-400" />
      </label>
      <label class="block">
        <span class="mb-2 block text-sm font-medium text-slate-700">Giới tính</span>
        <select v-model="form.gioi_tinh" class="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none focus:border-blue-400">
          <option value="">Chọn giới tính</option>
          <option value="nam">Nam</option>
          <option value="nu">Nữ</option>
          <option value="khac">Khác</option>
        </select>
      </label>
      <label class="block md:col-span-2">
        <span class="mb-2 block text-sm font-medium text-slate-700">Địa chỉ</span>
        <input v-model="form.dia_chi" class="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none focus:border-blue-400" />
      </label>

      <div class="md:col-span-2">
        <button type="submit" class="rounded-2xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800 disabled:opacity-60" :disabled="saving">
          {{ saving ? 'Đang lưu...' : 'Lưu thay đổi' }}
        </button>
      </div>
    </form>
  </section>
</template>
