<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { adminSkillService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'
import FormModalShell from '@/components/FormModalShell.vue'
import AdminPaginationBar from '@/components/Admin/AdminPaginationBar.vue'

const notify = useNotify()

const skills = ref([])
const loading = ref(false)
const error = ref('')
const currentPage = ref(1)
const totalSkills = ref(0)
const perPage = ref(10)
const searchQuery = ref('')
const sortBy = ref('ten_ky_nang')
const sortDir = ref('asc')

const stats = reactive({
  total: 0,
  withDescription: 0,
  withIcon: 0,
})

const showModal = ref(false)
const showDeleteModal = ref(false)
const editingSkill = ref(null)
const deletingSkill = ref(null)
const saving = ref(false)
const listSectionRef = ref(null)
let searchDebounceTimer = null

const formData = reactive({
  ten_ky_nang: '',
  mo_ta: '',
  icon: '',
})

const totalPages = computed(() => Math.max(1, Math.ceil(totalSkills.value / perPage.value)))

const scrollToListTop = async () => {
  await nextTick()

  listSectionRef.value?.scrollIntoView({
    behavior: 'smooth',
    block: 'start',
  })
}

const normalizeSkills = (response) => {
  const payload = response?.data

  if (Array.isArray(payload)) {
    skills.value = payload
    totalSkills.value = response?.total || payload.length
    return
  }

  if (payload?.data && Array.isArray(payload.data)) {
    skills.value = payload.data
    totalSkills.value = payload.total || payload.meta?.total || payload.data.length
    return
  }

  skills.value = []
  totalSkills.value = 0
}

const loadStats = async () => {
  try {
    const response = await adminSkillService.getStats()
    const payload = response?.data || {}
    stats.total = payload.tong || 0
    stats.withDescription = payload.co_mo_ta || 0
    stats.withIcon = payload.co_icon || 0
  } catch (err) {
    console.error('Không thể tải thống kê kỹ năng', err)
  }
}

const loadSkills = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await adminSkillService.getSkills({
      page: currentPage.value,
      per_page: perPage.value,
      search: searchQuery.value || undefined,
      sort_by: sortBy.value,
      sort_dir: sortDir.value,
    })

    normalizeSkills(response)
  } catch (err) {
    error.value = err.message || 'Không thể tải danh sách kỹ năng'
  } finally {
    loading.value = false
  }
}

const refreshAll = async () => {
  await Promise.all([loadSkills(), loadStats()])
}

const resetForm = () => {
  formData.ten_ky_nang = ''
  formData.mo_ta = ''
  formData.icon = ''
}

const openCreateModal = () => {
  editingSkill.value = null
  resetForm()
  showModal.value = true
}

const openEditModal = (skill) => {
  editingSkill.value = skill
  formData.ten_ky_nang = skill.ten_ky_nang || ''
  formData.mo_ta = skill.mo_ta || ''
  formData.icon = skill.icon || ''
  showModal.value = true
}

const closeModal = () => {
  if (saving.value) return
  showModal.value = false
}

const submitForm = async () => {
  saving.value = true
  try {
    const payload = {
      ten_ky_nang: formData.ten_ky_nang,
      mo_ta: formData.mo_ta || null,
      icon: formData.icon || null,
    }

    if (editingSkill.value) {
      await adminSkillService.updateSkill(editingSkill.value.id, payload)
      notify.success('Đã cập nhật kỹ năng')
    } else {
      await adminSkillService.createSkill(payload)
      notify.success('Đã tạo kỹ năng')
    }

    closeModal()
    await refreshAll()
  } catch (err) {
    error.value = err.message || 'Không thể lưu kỹ năng'
  } finally {
    saving.value = false
  }
}

const confirmDelete = (skill) => {
  deletingSkill.value = skill
  showDeleteModal.value = true
}

const deleteSkill = async () => {
  try {
    await adminSkillService.deleteSkill(deletingSkill.value.id)
    showDeleteModal.value = false
    deletingSkill.value = null
    notify.success('Đã xóa kỹ năng')
    await refreshAll()
  } catch (err) {
    error.value = err.message || 'Không thể xóa kỹ năng'
  }
}

const onFilterChange = async () => {
  currentPage.value = 1
  await loadSkills()
}

const onSearch = () => {
  currentPage.value = 1

  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer)
  }

  searchDebounceTimer = window.setTimeout(() => {
    loadSkills()
  }, 250)
}

const resetFilters = async () => {
  searchQuery.value = ''
  sortBy.value = 'ten_ky_nang'
  sortDir.value = 'asc'
  perPage.value = 10
  currentPage.value = 1
  await loadSkills()
}

const goToPage = async (page) => {
  currentPage.value = page
  await loadSkills()
  await scrollToListTop()
}

const goToPreviousPage = async () => {
  if (currentPage.value === 1) return
  currentPage.value -= 1
  await loadSkills()
  await scrollToListTop()
}

const goToNextPage = async () => {
  if (currentPage.value === totalPages.value) return
  currentPage.value += 1
  await loadSkills()
  await scrollToListTop()
}

onMounted(async () => {
  await refreshAll()
})

onBeforeUnmount(() => {
  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer)
  }
})
</script>

<template>
  <div v-if="error" class="mb-6 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-900 dark:bg-red-900/20 dark:text-red-300">
    {{ error }}
  </div>

  <div class="mb-8 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
    <div>
      <h1 class="text-3xl font-black tracking-tight">Quản lý kỹ năng</h1>
      <p class="mt-1 text-slate-500">Quản lý danh mục kỹ năng để phục vụ matching, CV parsing và AI recommendation.</p>
    </div>
    <button @click="openCreateModal" class="flex h-11 items-center gap-2 rounded-xl bg-[#2463eb] px-5 text-sm font-bold text-white shadow-lg shadow-[#2463eb]/20 transition-all hover:bg-[#2463eb]/90">
      <span class="material-symbols-outlined">add</span> Thêm kỹ năng
    </button>
  </div>

  <div class="mb-8 grid grid-cols-1 gap-6 sm:grid-cols-3">
    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <p class="text-sm font-medium text-slate-500">Tổng kỹ năng</p>
      <div class="mt-2 flex items-center justify-between">
        <p class="text-3xl font-bold">{{ stats.total }}</p>
        <span class="rounded bg-[#2463eb]/10 px-2 py-1 text-xs font-bold text-[#2463eb]">Catalog</span>
      </div>
    </div>
    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <p class="text-sm font-medium text-slate-500">Có mô tả</p>
      <div class="mt-2 flex items-center justify-between">
        <p class="text-3xl font-bold">{{ stats.withDescription }}</p>
        <span class="rounded bg-emerald-500/10 px-2 py-1 text-xs font-bold text-emerald-500">Chuẩn hóa</span>
      </div>
    </div>
    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <p class="text-sm font-medium text-slate-500">Có icon</p>
      <div class="mt-2 flex items-center justify-between">
        <p class="text-3xl font-bold">{{ stats.withIcon }}</p>
        <span class="rounded bg-slate-100 px-2 py-1 text-xs font-bold text-slate-500 dark:bg-slate-800 dark:text-slate-300">Hiển thị tốt</span>
      </div>
    </div>
  </div>

  <div ref="listSectionRef" class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
    <div class="flex flex-wrap items-center justify-between gap-4 border-b border-slate-200 p-4 dark:border-slate-800">
      <div class="relative min-w-[260px] flex-1">
        <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">search</span>
        <input
          v-model="searchQuery"
          @input="onSearch"
          type="text"
          class="w-full rounded-lg border-none bg-slate-100 py-2.5 pl-10 pr-4 text-sm text-slate-600 focus:ring-2 focus:ring-[#2463eb] dark:bg-slate-800 dark:text-slate-400"
          placeholder="Tìm theo tên kỹ năng hoặc mô tả..."
        />
      </div>
      <div class="flex items-center gap-3">
        <select v-model="sortBy" @change="onFilterChange" class="h-10 rounded-lg border-none bg-slate-100 px-3 text-sm text-slate-600 focus:ring-2 focus:ring-[#2463eb] dark:bg-slate-800 dark:text-slate-400">
          <option value="ten_ky_nang">Tên kỹ năng</option>
          <option value="created_at">Ngày tạo</option>
          <option value="id">ID</option>
        </select>
        <select v-model="sortDir" @change="onFilterChange" class="h-10 rounded-lg border-none bg-slate-100 px-3 text-sm text-slate-600 focus:ring-2 focus:ring-[#2463eb] dark:bg-slate-800 dark:text-slate-400">
          <option value="asc">A-Z / Cũ trước</option>
          <option value="desc">Z-A / Mới trước</option>
        </select>
        <select v-model="perPage" @change="onFilterChange" class="h-10 rounded-lg border-none bg-slate-100 px-3 text-sm text-slate-600 focus:ring-2 focus:ring-[#2463eb] dark:bg-slate-800 dark:text-slate-400">
          <option :value="10">10 / trang</option>
          <option :value="20">20 / trang</option>
          <option :value="50">50 / trang</option>
        </select>
        <button @click="resetFilters" class="h-10 rounded-lg border border-slate-200 px-4 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800">
          Reset bộ lọc
        </button>
      </div>
    </div>

    <div class="overflow-x-auto">
      <table class="w-full table-fixed text-left">
        <thead class="border-b border-slate-200 bg-slate-50 dark:border-slate-800 dark:bg-slate-800/50">
          <tr>
            <th class="w-[30%] px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-500">Kỹ năng</th>
            <th class="w-[40%] px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-500">Mô tả</th>
            <th class="w-[15%] px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-500">Icon</th>
            <th class="w-[15%] px-6 py-4 text-center text-xs font-bold uppercase tracking-wider text-slate-500">Hành động</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100 dark:divide-slate-800">
          <tr v-if="loading">
            <td colspan="4" class="px-6 py-10 text-center text-slate-500">
              <span class="material-symbols-outlined animate-spin">hourglass_empty</span>
              <div class="mt-2">Đang tải kỹ năng...</div>
            </td>
          </tr>

          <tr v-else-if="skills.length === 0">
            <td colspan="4" class="px-6 py-10 text-center text-slate-500">
              <span class="material-symbols-outlined text-3xl">psychology</span>
              <div class="mt-2">Không tìm thấy kỹ năng phù hợp.</div>
            </td>
          </tr>

          <tr v-for="skill in skills" :key="skill.id" class="hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition-colors">
            <td class="px-6 py-4">
              <div class="flex items-center gap-3">
                <div class="flex size-8 items-center justify-center rounded bg-[#2463eb]/10 font-bold text-[#2463eb]">
                  {{ skill.ten_ky_nang?.slice(0, 2).toUpperCase() }}
                </div>
                <span class="font-bold">{{ skill.ten_ky_nang }}</span>
              </div>
            </td>
            <td class="px-6 py-4 text-sm text-slate-500">
              {{ skill.mo_ta || 'Chưa có mô tả' }}
            </td>
            <td class="px-6 py-4 text-sm text-slate-500">
              {{ skill.icon || 'Không có' }}
            </td>
            <td class="px-6 py-4 text-center">
              <button @click="openEditModal(skill)" class="text-slate-400 hover:text-[#2463eb]">
                <span class="material-symbols-outlined text-[20px]">edit</span>
              </button>
              <button @click="confirmDelete(skill)" class="ml-3 text-slate-400 hover:text-red-500">
                <span class="material-symbols-outlined text-[20px]">delete</span>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <AdminPaginationBar
      v-if="!loading && skills.length > 0"
      :summary="`Hiển thị ${Math.min(skills.length, perPage)} / ${totalSkills} kỹ năng`"
      :current-page="currentPage"
      :total-pages="totalPages"
      @prev="goToPreviousPage"
      @next="goToNextPage"
    />
  </div>

  <FormModalShell
    v-if="showModal"
    eyebrow="Quản lý kỹ năng"
    :title="editingSkill ? 'Cập nhật kỹ năng' : 'Tạo kỹ năng mới'"
    description="Chuẩn hóa tên, icon và mô tả để danh mục kỹ năng nhất quán trên toàn hệ thống."
    max-width-class="max-w-3xl"
    :submit-label="editingSkill ? 'Lưu thay đổi' : 'Tạo kỹ năng'"
    :submit-loading-label="editingSkill ? 'Đang cập nhật...' : 'Đang tạo...'"
    :saving="saving"
    @close="closeModal"
    @submit="submitForm"
  >
    <template #summary>
      <div class="rounded-2xl border border-slate-200 bg-white p-4 sm:col-span-2">
        <p class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">Kỹ năng</p>
        <p class="mt-2 text-base font-semibold text-slate-900">{{ formData.ten_ky_nang || 'Chưa nhập tên kỹ năng' }}</p>
        <p class="mt-1 text-sm text-slate-500">{{ formData.icon || 'Chưa có icon' }}</p>
      </div>
    </template>

    <div class="grid gap-5 lg:grid-cols-2">
      <div class="space-y-2 lg:col-span-2">
        <label class="block text-sm font-semibold text-slate-700">Tên kỹ năng</label>
        <input v-model="formData.ten_ky_nang" type="text" required class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-base text-slate-900 outline-none transition focus:border-[#2463eb] focus:bg-white focus:ring-2 focus:ring-[#2463eb]/20" />
      </div>
      <div class="space-y-2 lg:col-span-2">
        <label class="block text-sm font-semibold text-slate-700">Icon</label>
        <input v-model="formData.icon" type="text" placeholder="code" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-base text-slate-900 outline-none transition focus:border-[#2463eb] focus:bg-white focus:ring-2 focus:ring-[#2463eb]/20" />
      </div>
      <div class="space-y-2 lg:col-span-2">
        <label class="block text-sm font-semibold text-slate-700">Mô tả</label>
        <textarea v-model="formData.mo_ta" rows="5" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-base leading-7 text-slate-900 outline-none transition focus:border-[#2463eb] focus:bg-white focus:ring-2 focus:ring-[#2463eb]/20"></textarea>
      </div>
    </div>
  </FormModalShell>

  <div v-if="showDeleteModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
    <div class="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl dark:bg-slate-900">
      <div class="mb-3 flex items-center gap-3">
        <span class="material-symbols-outlined text-2xl text-red-500">warning</span>
        <h3 class="text-lg font-semibold">Xóa kỹ năng</h3>
      </div>
      <p class="text-sm leading-6 text-slate-500">
        Bạn có chắc muốn xóa kỹ năng <strong>{{ deletingSkill?.ten_ky_nang }}</strong>?
      </p>
      <div class="mt-6 flex justify-end gap-3">
        <button @click="showDeleteModal = false" class="rounded-lg border border-slate-300 px-4 py-2 transition-colors hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-800">Hủy</button>
        <button @click="deleteSkill" class="rounded-lg bg-red-600 px-4 py-2 text-white transition-colors hover:bg-red-700">
          Xóa kỹ năng
        </button>
      </div>
    </div>
  </div>
</template>
