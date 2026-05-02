<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { adminCvTemplateService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'

const notify = useNotify()

const loading = ref(false)
const saving = ref(false)
const deletingId = ref(null)
const templates = ref([])
const pagination = ref(null)
const modalOpen = ref(false)
const editingId = ref(null)
const templateToDelete = ref(null)

const filters = reactive({
  search: '',
  page: 1,
  per_page: 20,
})

const form = reactive({
  ma_template: '',
  ten_template: '',
  mo_ta: '',
  bo_cuc: 'executive_navy',
  badges_text: '',
  thu_tu_hien_thi: 0,
  trang_thai: 1,
})

const layoutOptions = [
  { value: 'executive_navy', label: 'Executive Navy' },
  { value: 'topcv_maroon', label: 'Sidebar Maroon' },
  { value: 'ats_serif', label: 'ATS Serif' },
]

const isEditing = computed(() => editingId.value !== null)

const resetForm = () => {
  form.ma_template = ''
  form.ten_template = ''
  form.mo_ta = ''
  form.bo_cuc = 'executive_navy'
  form.badges_text = ''
  form.thu_tu_hien_thi = 0
  form.trang_thai = 1
  editingId.value = null
}

const badgesFromText = (value) =>
  String(value || '')
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)

const fetchTemplates = async () => {
  loading.value = true
  try {
    const response = await adminCvTemplateService.getTemplates(filters)
    const payload = response?.data || {}
    templates.value = payload.data || []
    pagination.value = payload
  } catch (error) {
    templates.value = []
    pagination.value = null
    notify.apiError(error, 'Không tải được danh sách template CV.')
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  resetForm()
  modalOpen.value = true
}

const openEditModal = (template) => {
  editingId.value = template.id
  form.ma_template = template.ma_template || ''
  form.ten_template = template.ten_template || ''
  form.mo_ta = template.mo_ta || ''
  form.bo_cuc = template.bo_cuc || 'executive_navy'
  form.badges_text = Array.isArray(template.badges) ? template.badges.join(', ') : ''
  form.thu_tu_hien_thi = Number(template.thu_tu_hien_thi || 0)
  form.trang_thai = Number(template.trang_thai ?? 1)
  modalOpen.value = true
}

const closeModal = () => {
  if (saving.value) return
  modalOpen.value = false
  resetForm()
}

const submitForm = async () => {
  saving.value = true
  try {
    const payload = {
      ma_template: form.ma_template.trim(),
      ten_template: form.ten_template.trim(),
      mo_ta: form.mo_ta.trim(),
      bo_cuc: form.bo_cuc,
      badges: badgesFromText(form.badges_text),
      thu_tu_hien_thi: Number(form.thu_tu_hien_thi || 0),
      trang_thai: Number(form.trang_thai ?? 1),
    }

    if (editingId.value) {
      await adminCvTemplateService.updateTemplate(editingId.value, payload)
      notify.success('Đã cập nhật template CV.')
    } else {
      await adminCvTemplateService.createTemplate(payload)
      notify.success('Đã tạo template CV mới.')
    }

    closeModal()
    await fetchTemplates()
  } catch (error) {
    notify.apiError(error, 'Không thể lưu template CV.')
  } finally {
    saving.value = false
  }
}

const toggleStatus = async (template) => {
  try {
    await adminCvTemplateService.toggleTemplateStatus(template.id)
    notify.success('Đã đổi trạng thái template CV.')
    await fetchTemplates()
  } catch (error) {
    notify.apiError(error, 'Không thể đổi trạng thái template CV.')
  }
}

const openDeleteModal = (template) => {
  templateToDelete.value = template
}

const closeDeleteModal = () => {
  if (deletingId.value) return
  templateToDelete.value = null
}

const deleteTemplate = async () => {
  if (!templateToDelete.value || deletingId.value) return

  deletingId.value = templateToDelete.value.id
  try {
    await adminCvTemplateService.deleteTemplate(templateToDelete.value.id)
    notify.success('Đã xóa template CV.')
    templateToDelete.value = null
    await fetchTemplates()
  } catch (error) {
    notify.apiError(error, 'Không thể xóa template CV.')
  } finally {
    deletingId.value = null
  }
}

const goToPage = async (page) => {
  if (!page || page === filters.page) return
  filters.page = page
  await fetchTemplates()
}

const applyFilters = async () => {
  filters.page = 1
  await fetchTemplates()
}

onMounted(fetchTemplates)
</script>

<template>
  <div class="space-y-6">
    <div class="flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 class="text-3xl font-black tracking-tight text-slate-900 dark:text-white">Template CV</h1>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Quản lý các template dùng cho tính năng tạo CV trực tiếp trên hệ thống.
        </p>
      </div>
      <button
        class="rounded-xl bg-[#2463eb] px-5 py-3 text-sm font-bold text-white transition hover:bg-blue-700"
        type="button"
        @click="openCreateModal"
      >
        Tạo template mới
      </button>
    </div>

    <div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="grid grid-cols-1 gap-3 md:grid-cols-[minmax(0,1fr)_160px]">
        <input
          v-model="filters.search"
          class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none focus:border-[#2463eb] dark:border-slate-800 dark:bg-slate-950"
          placeholder="Tìm theo mã hoặc tên template..."
          type="text"
          @keyup.enter="applyFilters"
        >
        <button
          class="rounded-xl border border-slate-200 px-4 py-3 text-sm font-bold transition hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-800"
          type="button"
          @click="applyFilters"
        >
          Áp dụng
        </button>
      </div>
    </div>

    <div class="rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div v-if="loading" class="space-y-3 p-4">
        <div v-for="index in 6" :key="index" class="h-16 animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800" />
      </div>

      <div v-else-if="!templates.length" class="p-8 text-center text-sm text-slate-500 dark:text-slate-400">
        Chưa có template CV nào.
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full text-left">
          <thead>
            <tr class="border-b border-slate-200 bg-slate-50 dark:border-slate-800 dark:bg-slate-800/50">
              <th class="px-5 py-4 text-xs font-bold uppercase tracking-wider text-slate-500">Template</th>
              <th class="px-5 py-4 text-xs font-bold uppercase tracking-wider text-slate-500">Bố cục</th>
              <th class="px-5 py-4 text-xs font-bold uppercase tracking-wider text-slate-500">Badge</th>
              <th class="px-5 py-4 text-xs font-bold uppercase tracking-wider text-slate-500">Trạng thái</th>
              <th class="px-5 py-4 text-right text-xs font-bold uppercase tracking-wider text-slate-500">Thao tác</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 dark:divide-slate-800">
            <tr v-for="template in templates" :key="template.id">
              <td class="px-5 py-4">
                <p class="font-semibold text-slate-900 dark:text-white">{{ template.ten_template }}</p>
                <p class="text-xs text-slate-500">{{ template.ma_template }}</p>
                <p class="mt-1 text-xs text-slate-400">{{ template.mo_ta || 'Chưa có mô tả' }}</p>
              </td>
              <td class="px-5 py-4 text-sm text-slate-600 dark:text-slate-300">{{ template.bo_cuc }}</td>
              <td class="px-5 py-4">
                <div class="flex flex-wrap gap-1.5">
                  <span
                    v-for="badge in template.badges || []"
                    :key="badge"
                    class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700 dark:bg-slate-800 dark:text-slate-300"
                  >
                    {{ badge }}
                  </span>
                </div>
              </td>
              <td class="px-5 py-4">
                <span
                  class="rounded-full px-2.5 py-1 text-xs font-bold"
                  :class="Number(template.trang_thai) === 1 ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300' : 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400'"
                >
                  {{ Number(template.trang_thai) === 1 ? 'Đang dùng' : 'Đã ẩn' }}
                </span>
              </td>
              <td class="px-5 py-4">
                <div class="flex justify-end gap-2">
                  <button class="rounded-lg border border-slate-200 px-3 py-2 text-sm font-semibold hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-800" @click="openEditModal(template)">Sửa</button>
                  <button class="rounded-lg border border-slate-200 px-3 py-2 text-sm font-semibold hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-800" @click="toggleStatus(template)">
                    {{ Number(template.trang_thai) === 1 ? 'Ẩn' : 'Hiện' }}
                  </button>
                  <button class="rounded-lg border border-rose-200 px-3 py-2 text-sm font-semibold text-rose-600 hover:bg-rose-50 dark:border-rose-900/30 dark:text-rose-300 dark:hover:bg-rose-900/10" :disabled="deletingId === template.id" @click="openDeleteModal(template)">
                    {{ deletingId === template.id ? 'Đang xóa...' : 'Xóa' }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="pagination" class="flex items-center justify-end gap-2 border-t border-slate-200 px-5 py-4 dark:border-slate-800">
        <button class="rounded-lg border border-slate-200 px-3 py-2 text-sm font-semibold disabled:opacity-50 dark:border-slate-700" :disabled="!pagination.prev_page_url" @click="goToPage((pagination.current_page || 1) - 1)">Trước</button>
        <button class="rounded-lg border border-slate-200 px-3 py-2 text-sm font-semibold disabled:opacity-50 dark:border-slate-700" :disabled="!pagination.next_page_url" @click="goToPage((pagination.current_page || 1) + 1)">Sau</button>
      </div>
    </div>

    <div v-if="modalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 px-4 py-6" @click.self="closeModal">
      <div class="w-full max-w-2xl rounded-3xl border border-slate-200 bg-white p-6 shadow-2xl dark:border-slate-800 dark:bg-slate-950">
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-bold text-slate-900 dark:text-white">{{ isEditing ? 'Cập nhật template CV' : 'Tạo template CV' }}</h2>
          <button class="rounded-lg p-2 hover:bg-slate-100 dark:hover:bg-slate-800" @click="closeModal">✕</button>
        </div>

        <div class="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2">
          <label class="block">
            <span class="mb-2 block text-sm font-semibold">Mã template</span>
            <input v-model="form.ma_template" class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm dark:border-slate-800 dark:bg-slate-900" type="text">
          </label>
          <label class="block">
            <span class="mb-2 block text-sm font-semibold">Tên template</span>
            <input v-model="form.ten_template" class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm dark:border-slate-800 dark:bg-slate-900" type="text">
          </label>
          <label class="block">
            <span class="mb-2 block text-sm font-semibold">Bố cục gốc</span>
            <select v-model="form.bo_cuc" class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm dark:border-slate-800 dark:bg-slate-900">
              <option v-for="option in layoutOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
            </select>
          </label>
          <label class="block">
            <span class="mb-2 block text-sm font-semibold">Thứ tự hiển thị</span>
            <input v-model="form.thu_tu_hien_thi" class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm dark:border-slate-800 dark:bg-slate-900" type="number" min="0">
          </label>
          <label class="block md:col-span-2">
            <span class="mb-2 block text-sm font-semibold">Mô tả</span>
            <textarea v-model="form.mo_ta" class="min-h-[100px] w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm dark:border-slate-800 dark:bg-slate-900" />
          </label>
          <label class="block md:col-span-2">
            <span class="mb-2 block text-sm font-semibold">Badge</span>
            <input v-model="form.badges_text" class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm dark:border-slate-800 dark:bg-slate-900" type="text" placeholder="Hợp Product / Business, Hợp HR / Finance">
          </label>
          <label class="block">
            <span class="mb-2 block text-sm font-semibold">Trạng thái</span>
            <select v-model="form.trang_thai" class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm dark:border-slate-800 dark:bg-slate-900">
              <option :value="1">Đang dùng</option>
              <option :value="0">Đã ẩn</option>
            </select>
          </label>
        </div>

        <div class="mt-6 flex justify-end gap-3">
          <button class="rounded-xl border border-slate-200 px-4 py-3 text-sm font-semibold dark:border-slate-700" @click="closeModal">Hủy</button>
          <button class="rounded-xl bg-[#2463eb] px-4 py-3 text-sm font-bold text-white disabled:opacity-60" :disabled="saving" @click="submitForm">
            {{ saving ? 'Đang lưu...' : (isEditing ? 'Lưu thay đổi' : 'Tạo template') }}
          </button>
        </div>
      </div>
    </div>

    <div
      v-if="templateToDelete"
      class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 px-4 py-6"
      @click.self="closeDeleteModal"
    >
      <div class="w-full max-w-md rounded-3xl border border-slate-200 bg-white p-6 shadow-2xl dark:border-slate-800 dark:bg-slate-950">
        <div class="flex h-14 w-14 items-center justify-center rounded-2xl bg-rose-50 text-rose-600 dark:bg-rose-900/20 dark:text-rose-300">
          <span class="material-symbols-outlined">delete_forever</span>
        </div>
        <h3 class="mt-5 text-xl font-black text-slate-900 dark:text-white">Xóa template CV?</h3>
        <p class="mt-3 text-sm leading-6 text-slate-500 dark:text-slate-400">
          Template <span class="font-semibold text-slate-900 dark:text-white">{{ templateToDelete.ten_template }}</span>
          sẽ bị xóa khỏi hệ thống. Hành động này không thể hoàn tác.
        </p>
        <div class="mt-6 flex justify-end gap-3">
          <button
            class="rounded-xl border border-slate-200 px-5 py-3 text-sm font-bold text-slate-700 transition hover:bg-slate-50 disabled:opacity-60 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
            :disabled="Boolean(deletingId)"
            type="button"
            @click="closeDeleteModal"
          >
            Hủy
          </button>
          <button
            class="rounded-xl bg-rose-600 px-5 py-3 text-sm font-bold text-white transition hover:bg-rose-700 disabled:cursor-not-allowed disabled:opacity-60"
            :disabled="Boolean(deletingId)"
            type="button"
            @click="deleteTemplate"
          >
            {{ deletingId ? 'Đang xóa...' : 'Xóa template' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
