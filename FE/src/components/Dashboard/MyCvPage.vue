<script setup>
import { onMounted, reactive, ref } from 'vue'
import { profileService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'

const notify = useNotify()
const loading = ref(false)
const saving = ref(false)
const profiles = ref([])
const editingId = ref(null)

const form = reactive({
  tieu_de_ho_so: '',
  muc_tieu_nghe_nghiep: '',
  trinh_do: '',
  kinh_nghiem_nam: '',
  mo_ta_ban_than: '',
  trang_thai: 1,
})

const resetForm = () => {
  editingId.value = null
  form.tieu_de_ho_so = ''
  form.muc_tieu_nghe_nghiep = ''
  form.trinh_do = ''
  form.kinh_nghiem_nam = ''
  form.mo_ta_ban_than = ''
  form.trang_thai = 1
}

const loadProfiles = async () => {
  loading.value = true
  try {
    const response = await profileService.getProfiles({ per_page: 100 })
    profiles.value = response?.data?.data || response?.data || []
  } catch (error) {
    notify.apiError(error, 'Không thể tải danh sách hồ sơ.')
  } finally {
    loading.value = false
  }
}

const buildPayload = () => {
  const payload = new FormData()
  payload.append('tieu_de_ho_so', form.tieu_de_ho_so)
  payload.append('muc_tieu_nghe_nghiep', form.muc_tieu_nghe_nghiep)
  payload.append('trinh_do', form.trinh_do)
  payload.append('kinh_nghiem_nam', String(form.kinh_nghiem_nam || 0))
  payload.append('mo_ta_ban_than', form.mo_ta_ban_than)
  payload.append('trang_thai', String(form.trang_thai))
  return payload
}

const submitProfile = async () => {
  saving.value = true
  try {
    const payload = buildPayload()
    if (editingId.value) {
      await profileService.updateProfile(editingId.value, payload)
      notify.success('Cập nhật hồ sơ thành công.')
    } else {
      await profileService.createProfile(payload)
      notify.success('Tạo hồ sơ thành công.')
    }
    resetForm()
    await loadProfiles()
  } catch (error) {
    notify.apiError(error, 'Không thể lưu hồ sơ.')
  } finally {
    saving.value = false
  }
}

const editProfile = (item) => {
  editingId.value = item.id
  form.tieu_de_ho_so = item.tieu_de_ho_so || ''
  form.muc_tieu_nghe_nghiep = item.muc_tieu_nghe_nghiep || ''
  form.trinh_do = item.trinh_do || ''
  form.kinh_nghiem_nam = item.kinh_nghiem_nam ?? ''
  form.mo_ta_ban_than = item.mo_ta_ban_than || ''
  form.trang_thai = Number(item.trang_thai ?? 1)
}

const removeProfile = async (id) => {
  if (!window.confirm('Xóa hồ sơ này?')) return

  try {
    await profileService.deleteProfile(id)
    notify.success('Đã xóa hồ sơ.')
    if (editingId.value === id) {
      resetForm()
    }
    await loadProfiles()
  } catch (error) {
    notify.apiError(error, 'Không thể xóa hồ sơ.')
  }
}

const toggleStatus = async (id) => {
  try {
    await profileService.toggleProfileStatus(id)
    await loadProfiles()
  } catch (error) {
    notify.apiError(error, 'Không thể đổi trạng thái hồ sơ.')
  }
}

onMounted(loadProfiles)
</script>

<template>
  <div class="grid gap-6 xl:grid-cols-[380px_minmax(0,1fr)]">
    <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <p class="text-xs uppercase tracking-[0.3em] text-blue-600">Hồ sơ ứng viên</p>
      <h2 class="mt-2 text-2xl font-bold text-slate-900">{{ editingId ? 'Cập nhật hồ sơ' : 'Tạo hồ sơ mới' }}</h2>

      <form class="mt-6 space-y-4" @submit.prevent="submitProfile">
        <input v-model="form.tieu_de_ho_so" required placeholder="Tiêu đề hồ sơ" class="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none focus:border-blue-400" />
        <input v-model="form.trinh_do" placeholder="Trình độ: dai_hoc, cao_dang..." class="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none focus:border-blue-400" />
        <input v-model="form.kinh_nghiem_nam" type="number" min="0" placeholder="Số năm kinh nghiệm" class="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none focus:border-blue-400" />
        <textarea v-model="form.muc_tieu_nghe_nghiep" rows="3" placeholder="Mục tiêu nghề nghiệp" class="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none focus:border-blue-400"></textarea>
        <textarea v-model="form.mo_ta_ban_than" rows="4" placeholder="Mô tả bản thân" class="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none focus:border-blue-400"></textarea>

        <div class="flex gap-3">
          <button type="submit" class="rounded-2xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800 disabled:opacity-60" :disabled="saving">
            {{ saving ? 'Đang lưu...' : editingId ? 'Cập nhật' : 'Tạo hồ sơ' }}
          </button>
          <button v-if="editingId" type="button" class="rounded-2xl border border-slate-200 px-5 py-3 text-sm font-semibold text-slate-700 hover:bg-slate-50" @click="resetForm">
            Hủy
          </button>
        </div>
      </form>
    </section>

    <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-xs uppercase tracking-[0.3em] text-blue-600">Danh sách hồ sơ</p>
          <h2 class="mt-2 text-2xl font-bold text-slate-900">CV đang có</h2>
        </div>
      </div>

      <div v-if="loading" class="mt-6 text-sm text-slate-500">Đang tải hồ sơ...</div>
      <div v-else-if="profiles.length === 0" class="mt-6 rounded-2xl border border-dashed border-slate-300 px-6 py-10 text-center text-sm text-slate-500">
        Chưa có hồ sơ nào. Hãy tạo hồ sơ đầu tiên để dùng cho matching và career report.
      </div>

      <div v-else class="mt-6 space-y-4">
        <article v-for="item in profiles" :key="item.id" class="rounded-2xl border border-slate-200 p-5">
          <div class="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
            <div>
              <h3 class="text-lg font-semibold text-slate-900">{{ item.tieu_de_ho_so }}</h3>
              <p class="mt-2 text-sm text-slate-600">{{ item.trinh_do || 'Chưa có trình độ' }} · {{ item.kinh_nghiem_nam || 0 }} năm kinh nghiệm</p>
              <p class="mt-3 text-sm leading-6 text-slate-600">{{ item.muc_tieu_nghe_nghiep || item.mo_ta_ban_than || 'Chưa có mô tả.' }}</p>
            </div>

            <div class="flex flex-wrap gap-2">
              <button type="button" class="rounded-xl border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50" @click="editProfile(item)">Sửa</button>
              <button type="button" class="rounded-xl border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50" @click="toggleStatus(item.id)">
                {{ Number(item.trang_thai) === 1 ? 'Ẩn' : 'Công khai' }}
              </button>
              <button type="button" class="rounded-xl border border-rose-200 px-4 py-2 text-sm font-medium text-rose-600 hover:bg-rose-50" @click="removeProfile(item.id)">Xóa</button>
            </div>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>
