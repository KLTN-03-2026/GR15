<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { candidateSkillService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'

const notify = useNotify()

const isLoading = ref(true)
const isSubmitting = ref(false)
const catalogLoading = ref(false)
const isEditMode = ref(false)
const currentSkillId = ref(null)
const deletingSkillId = ref(null)
const skillToDelete = ref(null)

const catalogOptions = ref([])
const mySkills = ref([])

const form = reactive({
  ky_nang_id: '',
  muc_do: '3',
  nam_kinh_nghiem: '',
  so_chung_chi: '',
  hinh_anh: null,
})

const previewUrl = ref('')

const levelOptions = [
  { value: '1', label: '1 - Cơ bản' },
  { value: '2', label: '2 - Trung bình' },
  { value: '3', label: '3 - Khá' },
  { value: '4', label: '4 - Giỏi' },
  { value: '5', label: '5 - Chuyên gia' },
]

const levelLabel = (value) => {
  return levelOptions.find(option => Number(option.value) === Number(value))?.label?.replace(/^\d+\s-\s/, '') || 'Chưa rõ'
}

const summary = computed(() => {
  const total = mySkills.value.length
  const averageLevel = total
    ? (mySkills.value.reduce((sum, item) => sum + Number(item.muc_do || 0), 0) / total).toFixed(1)
    : '0.0'
  const totalYears = mySkills.value.reduce((sum, item) => sum + Number(item.nam_kinh_nghiem || 0), 0)
  const totalCertificates = mySkills.value.reduce((sum, item) => sum + Number(item.so_chung_chi || 0), 0)

  return {
    total,
    averageLevel,
    totalYears,
    totalCertificates,
  }
})

const resetForm = () => {
  form.ky_nang_id = ''
  form.muc_do = '3'
  form.nam_kinh_nghiem = ''
  form.so_chung_chi = ''
  form.hinh_anh = null
  previewUrl.value = ''
  isEditMode.value = false
  currentSkillId.value = null
}

const normalizeCatalog = (payload) => {
  const items = payload?.data?.data || payload?.data || []
  catalogOptions.value = Array.isArray(items) ? items : []
}

const normalizeMySkills = (payload) => {
  const items = payload?.data || payload?.data?.data || []
  mySkills.value = Array.isArray(items) ? items : []
}

const loadCatalog = async () => {
  catalogLoading.value = true
  try {
    const response = await candidateSkillService.getCatalog({ per_page: 100 })
    normalizeCatalog(response)
  } catch (error) {
    notify.apiError(error, 'Không thể tải danh mục kỹ năng.')
  } finally {
    catalogLoading.value = false
  }
}

const loadMySkills = async () => {
  isLoading.value = true
  try {
    const response = await candidateSkillService.getMySkills()
    normalizeMySkills(response)
  } catch (error) {
    notify.apiError(error, 'Không thể tải kỹ năng cá nhân.')
  } finally {
    isLoading.value = false
  }
}

const onFileChange = (event) => {
  const [file] = event.target.files || []
  form.hinh_anh = file || null
  previewUrl.value = file ? URL.createObjectURL(file) : ''
}

const buildPayload = () => {
  const payload = new FormData()

  if (!isEditMode.value) {
    payload.append('ky_nang_id', form.ky_nang_id)
  }

  payload.append('muc_do', form.muc_do)

  if (form.nam_kinh_nghiem !== '') {
    payload.append('nam_kinh_nghiem', String(form.nam_kinh_nghiem))
  }

  if (form.so_chung_chi !== '') {
    payload.append('so_chung_chi', String(form.so_chung_chi))
  }

  if (form.hinh_anh instanceof File) {
    payload.append('hinh_anh', form.hinh_anh)
  }

  return payload
}

const validateForm = () => {
  if (!isEditMode.value && !form.ky_nang_id) {
    notify.warning('Vui lòng chọn kỹ năng cần thêm.')
    return false
  }

  return true
}

const handleSubmit = async () => {
  if (!validateForm()) return

  isSubmitting.value = true

  try {
    const payload = buildPayload()

    if (isEditMode.value && currentSkillId.value) {
      await candidateSkillService.updateSkill(currentSkillId.value, payload)
      notify.success('Cập nhật kỹ năng thành công.')
    } else {
      await candidateSkillService.createSkill(payload)
      notify.success('Thêm kỹ năng thành công.')
    }

    resetForm()
    await loadMySkills()
  } catch (error) {
    notify.apiError(error, isEditMode.value ? 'Không thể cập nhật kỹ năng.' : 'Không thể thêm kỹ năng.')
  } finally {
    isSubmitting.value = false
  }
}

const handleEdit = (item) => {
  isEditMode.value = true
  currentSkillId.value = item.id
  form.ky_nang_id = String(item.ky_nang_id || '')
  form.muc_do = String(item.muc_do || '3')
  form.nam_kinh_nghiem = item.nam_kinh_nghiem ?? ''
  form.so_chung_chi = item.so_chung_chi ?? ''
  form.hinh_anh = null
  previewUrl.value = item.hinh_anh_url || ''
}

const askDelete = (item) => {
  skillToDelete.value = item
}

const confirmDelete = async () => {
  if (!skillToDelete.value) return

  deletingSkillId.value = skillToDelete.value.id
  try {
    await candidateSkillService.deleteSkill(skillToDelete.value.id)
    notify.success('Xóa kỹ năng thành công.')

    if (currentSkillId.value === skillToDelete.value.id) {
      resetForm()
    }

    skillToDelete.value = null
    await loadMySkills()
  } catch (error) {
    notify.apiError(error, 'Không thể xóa kỹ năng.')
  } finally {
    deletingSkillId.value = null
  }
}

onMounted(async () => {
  await Promise.all([loadCatalog(), loadMySkills()])
})
</script>

<template>
  <div class="min-h-screen text-slate-900 dark:text-white">
    <section class="mx-auto max-w-7xl px-6 py-8">
      <div class="rounded-[30px] border border-blue-200 bg-gradient-to-r from-white via-blue-50 to-[#dce7ff] px-8 py-8 shadow-[0_28px_90px_rgba(148,163,184,0.18)] dark:border-blue-500/20 dark:bg-gradient-to-r dark:from-slate-900 dark:via-[#16264d] dark:to-[#1b49d4] dark:shadow-[0_28px_90px_rgba(14,21,45,0.45)]">
        <div class="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div class="max-w-3xl">
            <p class="text-xs font-semibold uppercase tracking-[0.45em] text-blue-600/80 dark:text-blue-100/70">Candidate Skills</p>
            <h1 class="mt-3 text-4xl font-black tracking-tight text-slate-900 dark:text-white">Kỹ năng của tôi</h1>
            <p class="mt-3 max-w-2xl text-base leading-7 text-slate-600 dark:text-blue-50/80">
              Quản lý kỹ năng, số năm kinh nghiệm và chứng chỉ để gợi ý việc làm, AI matching và mock interview bám hồ sơ sát hơn.
            </p>
          </div>

          <div class="grid min-w-[320px] grid-cols-2 gap-3 sm:grid-cols-4">
            <div class="rounded-2xl border border-blue-200 bg-white/70 px-4 py-4 backdrop-blur dark:border-white/10 dark:bg-white/8">
              <p class="text-xs uppercase tracking-[0.28em] text-blue-600/70 dark:text-blue-100/65">Tổng kỹ năng</p>
              <p class="mt-3 text-3xl font-black text-slate-900 dark:text-white">{{ summary.total }}</p>
            </div>
            <div class="rounded-2xl border border-blue-200 bg-white/70 px-4 py-4 backdrop-blur dark:border-white/10 dark:bg-white/8">
              <p class="text-xs uppercase tracking-[0.28em] text-blue-600/70 dark:text-blue-100/65">Mức độ TB</p>
              <p class="mt-3 text-3xl font-black text-slate-900 dark:text-white">{{ summary.averageLevel }}</p>
            </div>
            <div class="rounded-2xl border border-blue-200 bg-white/70 px-4 py-4 backdrop-blur dark:border-white/10 dark:bg-white/8">
              <p class="text-xs uppercase tracking-[0.28em] text-blue-600/70 dark:text-blue-100/65">Năm KN</p>
              <p class="mt-3 text-3xl font-black text-slate-900 dark:text-white">{{ summary.totalYears }}</p>
            </div>
            <div class="rounded-2xl border border-blue-200 bg-white/70 px-4 py-4 backdrop-blur dark:border-white/10 dark:bg-white/8">
              <p class="text-xs uppercase tracking-[0.28em] text-blue-600/70 dark:text-blue-100/65">Chứng chỉ</p>
              <p class="mt-3 text-3xl font-black text-slate-900 dark:text-white">{{ summary.totalCertificates }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="mt-8 grid gap-6 xl:grid-cols-[420px_minmax(0,1fr)]">
        <section class="self-start rounded-[28px] border border-slate-200 bg-white/95 p-6 shadow-[0_22px_60px_rgba(148,163,184,0.12)] dark:border-white/10 dark:bg-slate-900/85 dark:shadow-[0_22px_60px_rgba(15,23,42,0.32)]">
          <div class="flex items-start justify-between gap-4">
            <div>
              <h2 class="text-2xl font-bold text-slate-900 dark:text-white">{{ isEditMode ? 'Cập nhật kỹ năng' : 'Thêm kỹ năng mới' }}</h2>
              <p class="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-400">
                Chọn kỹ năng trong danh mục chung rồi thêm mức độ thành thạo và chứng chỉ liên quan.
              </p>
            </div>

            <button
              v-if="isEditMode"
              type="button"
              class="rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 hover:border-blue-400/40 hover:text-slate-900 dark:border-white/10 dark:text-slate-200 dark:hover:text-white"
              @click="resetForm"
            >
              Hủy sửa
            </button>
          </div>

          <form class="mt-6 space-y-4" @submit.prevent="handleSubmit">
            <div>
              <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Kỹ năng</label>
              <select
                v-model="form.ky_nang_id"
                class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-blue-400/60 dark:border-white/10 dark:bg-slate-800/90 dark:text-white"
                :disabled="isEditMode || catalogLoading || isSubmitting"
              >
                <option value="" disabled>{{ catalogLoading ? 'Đang tải danh mục...' : 'Chọn kỹ năng' }}</option>
                <option v-for="skill in catalogOptions" :key="skill.id" :value="String(skill.id)">
                  {{ skill.ten_ky_nang }}
                </option>
              </select>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <div>
                <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Mức độ</label>
                <select
                  v-model="form.muc_do"
                  class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-blue-400/60 dark:border-white/10 dark:bg-slate-800/90 dark:text-white"
                  :disabled="isSubmitting"
                >
                  <option v-for="option in levelOptions" :key="option.value" :value="option.value">
                    {{ option.label }}
                  </option>
                </select>
              </div>

              <div>
                <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Năm kinh nghiệm</label>
                <input
                  v-model="form.nam_kinh_nghiem"
                  type="number"
                  min="0"
                  max="50"
                  class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-blue-400/60 dark:border-white/10 dark:bg-slate-800/90 dark:text-white"
                  placeholder="Ví dụ: 2"
                  :disabled="isSubmitting"
                >
              </div>
            </div>

            <div>
              <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Số chứng chỉ</label>
              <input
                v-model="form.so_chung_chi"
                type="number"
                min="0"
                class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-blue-400/60 dark:border-white/10 dark:bg-slate-800/90 dark:text-white"
                placeholder="Ví dụ: 1"
                :disabled="isSubmitting"
              >
            </div>

            <div>
              <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Ảnh chứng chỉ</label>
              <label class="flex cursor-pointer items-center justify-center gap-3 rounded-2xl border border-dashed border-slate-300 bg-slate-50/90 px-4 py-4 text-sm text-slate-600 transition hover:border-blue-400/40 hover:text-slate-900 dark:border-white/15 dark:bg-slate-800/80 dark:text-slate-300 dark:hover:text-white">
                <span class="material-symbols-outlined text-xl text-blue-300">upload</span>
                <span>{{ form.hinh_anh ? form.hinh_anh.name : 'Chọn ảnh chứng chỉ (không bắt buộc)' }}</span>
                <input type="file" class="hidden" accept="image/png,image/jpeg,image/jpg,image/webp" @change="onFileChange">
              </label>

              <div v-if="previewUrl" class="mt-3 overflow-hidden rounded-2xl border border-slate-200 bg-slate-100 dark:border-white/10 dark:bg-slate-950/70">
                <img :src="previewUrl" alt="Xem trước chứng chỉ" class="h-44 w-full object-cover">
              </div>
            </div>

            <button
              type="submit"
              class="inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-[#2f67ee] to-[#5a5ff6] px-5 py-3.5 text-sm font-bold text-white shadow-[0_18px_32px_rgba(47,103,238,0.24)] transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-70"
              :disabled="isSubmitting"
            >
              <span class="material-symbols-outlined text-lg">{{ isEditMode ? 'edit' : 'add' }}</span>
              <span>{{ isSubmitting ? (isEditMode ? 'Đang cập nhật...' : 'Đang thêm...') : (isEditMode ? 'Lưu cập nhật kỹ năng' : 'Thêm kỹ năng vào hồ sơ') }}</span>
            </button>
          </form>
        </section>

        <section class="rounded-[28px] border border-slate-200 bg-white/95 p-6 shadow-[0_22px_60px_rgba(148,163,184,0.12)] dark:border-white/10 dark:bg-slate-900/85 dark:shadow-[0_22px_60px_rgba(15,23,42,0.32)]">
          <div class="flex flex-col gap-3 border-b border-slate-200 pb-5 dark:border-white/10 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h2 class="text-2xl font-bold text-slate-900 dark:text-white">Danh sách kỹ năng cá nhân</h2>
              <p class="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-400">
                Những kỹ năng này sẽ được dùng cho matching, tư vấn AI và luồng mock interview.
              </p>
            </div>
            <div class="rounded-2xl border border-blue-400/20 bg-blue-500/10 px-4 py-3 text-sm text-blue-700 dark:text-blue-100">
              {{ mySkills.length }} kỹ năng đã thêm
            </div>
          </div>

          <div v-if="isLoading" class="grid gap-4 pt-6 md:grid-cols-2">
            <div v-for="item in 4" :key="item" class="h-48 animate-pulse rounded-[26px] border border-slate-200 bg-slate-100 dark:border-white/10 dark:bg-slate-800/70"></div>
          </div>

          <div v-else-if="!mySkills.length" class="flex min-h-[320px] flex-col items-center justify-center rounded-[26px] border border-dashed border-slate-300 bg-slate-50/70 px-6 text-center dark:border-white/10 dark:bg-slate-950/40">
            <div class="flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-500/15 text-blue-200">
              <span class="material-symbols-outlined text-3xl">psychology</span>
            </div>
            <h3 class="mt-5 text-2xl font-bold text-slate-900 dark:text-white">Bạn chưa có kỹ năng nào</h3>
            <p class="mt-3 max-w-lg text-sm leading-7 text-slate-600 dark:text-slate-400">
              Hãy thêm kỹ năng đầu tiên để hệ thống gợi ý việc làm chính xác hơn và làm hồ sơ của bạn nổi bật hơn khi matching.
            </p>
          </div>

          <div v-else class="grid gap-4 pt-6 md:grid-cols-2">
            <article
              v-for="item in mySkills"
              :key="item.id"
              class="overflow-hidden rounded-[22px] border border-slate-200 bg-white p-4 shadow-[0_14px_36px_rgba(148,163,184,0.10)] transition hover:-translate-y-0.5 hover:shadow-[0_18px_40px_rgba(148,163,184,0.14)] dark:border-white/10 dark:bg-slate-950/45 dark:shadow-[0_14px_36px_rgba(15,23,42,0.22)]"
            >
              <div class="rounded-[18px] border border-blue-100 bg-gradient-to-r from-blue-50 via-white to-indigo-50 p-3.5 dark:border-white/10 dark:bg-gradient-to-r dark:from-slate-900 dark:via-slate-900 dark:to-slate-800/80">
                <div class="flex items-start justify-between gap-3">
                  <div class="min-w-0">
                    <div class="inline-flex items-center gap-1.5 rounded-full border border-blue-400/20 bg-blue-500/10 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.22em] text-blue-700 dark:text-blue-100/80">
                      <span class="material-symbols-outlined text-sm">star</span>
                      {{ levelLabel(item.muc_do) }}
                    </div>
                    <h3 class="mt-2.5 text-[1.75rem] font-bold tracking-tight text-slate-900 dark:text-white">
                      {{ item.ky_nang?.ten_ky_nang || `Kỹ năng #${item.ky_nang_id}` }}
                    </h3>
                    <p class="mt-1.5 text-sm leading-6 text-slate-600 dark:text-slate-400">
                      {{ Number(item.nam_kinh_nghiem || 0) }} năm kinh nghiệm
                      <br>
                      {{ Number(item.so_chung_chi || 0) }} chứng chỉ
                    </p>
                  </div>

                  <div class="flex items-center gap-2">
                    <button
                      type="button"
                      class="inline-flex h-10 w-10 items-center justify-center rounded-[18px] border border-slate-200 bg-white text-slate-600 transition hover:border-blue-400/40 hover:text-slate-900 dark:border-white/10 dark:bg-slate-900/70 dark:text-slate-300 dark:hover:text-white"
                      @click="handleEdit(item)"
                    >
                      <span class="material-symbols-outlined">edit</span>
                    </button>
                  <button
                    type="button"
                    class="inline-flex h-10 w-10 items-center justify-center rounded-[18px] border border-red-400/20 bg-white text-red-600 transition hover:border-red-400/50 hover:bg-red-500/10 dark:bg-slate-900/70 dark:text-red-300"
                    @click="askDelete(item)"
                  >
                    <span class="material-symbols-outlined">delete</span>
                    </button>
                  </div>
                </div>

                <div class="mt-3.5">
                  <div class="mb-2 flex items-center justify-between text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">
                    <span>Độ thành thạo</span>
                    <span>{{ item.muc_do }}/5</span>
                  </div>
                  <div class="h-2 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800">
                    <div
                      class="h-full rounded-full bg-gradient-to-r from-blue-500 via-indigo-500 to-violet-500"
                      :style="{ width: `${Math.max(8, Number(item.muc_do || 0) * 20)}%` }"
                    />
                  </div>
                </div>
              </div>

              <div class="mt-3.5 grid grid-cols-3 gap-2.5">
                <div class="rounded-[18px] border border-slate-200 bg-slate-50/80 px-3 py-3 dark:border-white/8 dark:bg-slate-900/70">
                  <p class="text-[11px] uppercase tracking-[0.3em] text-slate-500 dark:text-slate-400">Mức độ</p>
                  <p class="mt-1.5 text-lg font-bold text-slate-900 dark:text-white">{{ item.muc_do }}/5</p>
                  <p class="mt-0.5 text-xs text-slate-500 dark:text-slate-400">{{ levelLabel(item.muc_do) }}</p>
                </div>
                <div class="rounded-[18px] border border-slate-200 bg-slate-50/80 px-3 py-3 dark:border-white/8 dark:bg-slate-900/70">
                  <p class="text-[11px] uppercase tracking-[0.3em] text-slate-500 dark:text-slate-400">Kinh nghiệm</p>
                  <p class="mt-1.5 text-lg font-bold text-slate-900 dark:text-white">{{ item.nam_kinh_nghiem || 0 }} năm</p>
                  <p class="mt-0.5 text-xs text-slate-500 dark:text-slate-400">Thời gian tích lũy</p>
                </div>
                <div class="rounded-[18px] border border-slate-200 bg-slate-50/80 px-3 py-3 dark:border-white/8 dark:bg-slate-900/70">
                  <p class="text-[11px] uppercase tracking-[0.3em] text-slate-500 dark:text-slate-400">Chứng chỉ</p>
                  <p class="mt-1.5 text-lg font-bold text-slate-900 dark:text-white">{{ item.so_chung_chi || 0 }}</p>
                  <p class="mt-0.5 text-xs text-slate-500 dark:text-slate-400">Tài liệu liên quan</p>
                </div>
              </div>

            </article>
          </div>
        </section>
      </div>
    </section>

    <div
      v-if="skillToDelete"
      class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 px-4 backdrop-blur-sm"
    >
      <div class="w-full max-w-md rounded-[28px] border border-slate-200 bg-white p-6 shadow-[0_26px_80px_rgba(148,163,184,0.24)] dark:border-white/10 dark:bg-slate-900 dark:shadow-[0_26px_80px_rgba(15,23,42,0.55)]">
        <div class="flex h-14 w-14 items-center justify-center rounded-2xl bg-red-500/10 text-red-300">
          <span class="material-symbols-outlined text-3xl">delete_forever</span>
        </div>

        <h3 class="mt-5 text-2xl font-bold text-slate-900 dark:text-white">Xóa kỹ năng này?</h3>
        <p class="mt-3 text-sm leading-7 text-slate-600 dark:text-slate-400">
          Kỹ năng <span class="font-semibold text-slate-900 dark:text-white">{{ skillToDelete.ky_nang?.ten_ky_nang || `#${skillToDelete.ky_nang_id}` }}</span>
          sẽ bị xóa khỏi hồ sơ và chứng chỉ đính kèm cũng sẽ bị gỡ khỏi hệ thống.
        </p>

        <div class="mt-6 flex gap-3">
          <button
            type="button"
            class="flex-1 rounded-2xl border border-slate-200 px-4 py-3 font-semibold text-slate-600 transition hover:border-slate-300 hover:text-slate-900 dark:border-white/10 dark:text-slate-200 dark:hover:border-white/20 dark:hover:text-white"
            @click="skillToDelete = null"
          >
            Hủy
          </button>
          <button
            type="button"
            class="flex-1 rounded-2xl bg-red-500 px-4 py-3 font-semibold text-white transition hover:bg-red-400 disabled:cursor-not-allowed disabled:opacity-70"
            :disabled="deletingSkillId === skillToDelete.id"
            @click="confirmDelete"
          >
            {{ deletingSkillId === skillToDelete.id ? 'Đang xóa...' : 'Xóa kỹ năng' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
