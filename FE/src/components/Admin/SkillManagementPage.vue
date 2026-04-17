<template>
  <div class="p-6">
    <div class="mb-6 flex flex-col justify-between gap-4 md:flex-row md:items-end">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">Quản lý Kỹ năng</h1>
        <p class="mt-1 text-sm text-slate-500">Bộ từ khóa kỹ năng phục vụ AI Matching.</p>
      </div>
      <div class="flex gap-3">
        <div class="relative">
          <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">search</span>
          <input 
            v-model="searchQuery" 
            @input="handleSearch"
            type="text" 
            placeholder="Tìm kiếm kỹ năng..." 
            class="w-64 rounded-xl border border-slate-200 bg-white py-2 pl-10 pr-4 text-sm text-slate-700 outline-none focus:border-[#2463eb]"
          />
        </div>
        <button @click="openModal()" class="flex items-center gap-2 rounded-xl bg-[#2463eb] px-4 py-2 text-sm font-bold text-white transition hover:bg-blue-700">
          <span class="material-symbols-outlined text-[18px]">add</span>
          Thêm kỹ năng
        </button>
      </div>
    </div>

    <!-- Stats Grid -->
    <div class="mb-6 grid gap-4 grid-cols-1 md:grid-cols-3">
      <div class="rounded-2xl border border-blue-200 bg-blue-50 px-5 py-4">
        <p class="text-xs font-bold uppercase tracking-wider text-blue-600">Tổng số kỹ năng</p>
        <p class="mt-1 text-3xl font-black text-blue-900">{{ stats.total || 0 }}</p>
      </div>
      <div class="rounded-2xl border border-slate-200 bg-white px-5 py-4 shadow-sm">
        <p class="text-xs font-bold uppercase tracking-wider text-slate-500">Có Icon</p>
        <p class="mt-1 text-2xl font-black text-slate-800">{{ stats.have_icon || 0 }}</p>
      </div>
      <div class="rounded-2xl border border-slate-200 bg-white px-5 py-4 shadow-sm">
        <p class="text-xs font-bold uppercase tracking-wider text-slate-500">Có mô tả</p>
        <p class="mt-1 text-2xl font-black text-slate-800">{{ stats.have_description || 0 }}</p>
      </div>
    </div>

    <!-- Table -->
    <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <table class="w-full text-left text-sm text-slate-600">
        <thead class="bg-slate-50 text-xs uppercase text-slate-500 border-b border-slate-200">
          <tr>
            <th class="px-6 py-4 font-bold">ID</th>
            <th class="px-6 py-4 font-bold">Icon & Tên kỹ năng</th>
            <th class="px-6 py-4 font-bold">Mô tả</th>
            <th class="px-6 py-4 text-right font-bold w-24">Phím</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <template v-if="loading">
            <tr v-for="i in 5" :key="i" class="animate-pulse">
              <td class="px-6 py-4"><div class="h-4 w-8 rounded bg-slate-200"></div></td>
              <td class="px-6 py-4 flex gap-3"><div class="size-8 rounded-lg bg-slate-200"></div><div class="h-4 w-32 mt-2 rounded bg-slate-200"></div></td>
              <td class="px-6 py-4"><div class="h-4 w-48 rounded bg-slate-200"></div></td>
              <td class="px-6 py-4 text-right"><div class="h-8 w-16 float-right rounded bg-slate-200"></div></td>
            </tr>
          </template>
          <template v-else-if="skills.length">
            <tr v-for="skill in skills" :key="skill.id" class="transition hover:bg-slate-50">
              <td class="px-6 py-4 font-semibold text-slate-500">#{{ skill.id }}</td>
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                  <div v-if="skill.icon" class="flex size-8 shrink-0 items-center justify-center rounded-lg bg-slate-100 text-xl shadow-sm" v-html="skill.icon"></div>
                  <div v-else class="flex size-8 shrink-0 items-center justify-center rounded-lg bg-slate-100 text-slate-400"><span class="material-symbols-outlined text-sm">code</span></div>
                  <span class="font-bold text-slate-900">{{ skill.ten_ky_nang }}</span>
                </div>
              </td>
              <td class="px-6 py-4 text-slate-500">{{ skill.mo_ta || 'Không có mô tả' }}</td>
              <td class="px-6 py-4 text-right">
                <button @click="openModal(skill)" class="mr-2 text-slate-400 hover:text-[#2463eb]" title="Sửa">
                  <span class="material-symbols-outlined text-[20px]">edit</span>
                </button>
                <button @click="confirmDelete(skill.id)" class="text-slate-400 hover:text-rose-600" title="Xoá">
                  <span class="material-symbols-outlined text-[20px]">delete</span>
                </button>
              </td>
            </tr>
          </template>
          <template v-else>
            <tr>
              <td colspan="4" class="py-12 text-center text-slate-500">Không tìm thấy kỹ năng nào.</td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <!-- Modal Form CRUD -->
    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4">
      <div class="w-full max-w-md rounded-3xl bg-white p-6 shadow-2xl">
        <h2 class="mb-5 text-xl font-bold text-slate-900">{{ editMode ? 'Sửa kỹ năng' : 'Thêm kỹ năng mới' }}</h2>
        <form @submit.prevent="saveSkill" class="space-y-4">
          <div>
            <label class="mb-1 block text-sm font-semibold text-slate-700">Tên kỹ năng *</label>
            <input v-model="form.ten_ky_nang" type="text" required class="w-full rounded-xl border border-slate-200 px-4 py-2 text-sm text-slate-900 outline-none focus:border-[#2463eb]" placeholder="VD: Vue 3" />
          </div>
          <div>
            <label class="mb-1 block text-sm font-semibold text-slate-700">Icon (SVG, Emoji, v.v)</label>
            <input v-model="form.icon" type="text" class="w-full rounded-xl border border-slate-200 px-4 py-2 text-sm text-slate-900 outline-none focus:border-[#2463eb]" placeholder="SVG Code hoặc URL" />
          </div>
          <div>
            <label class="mb-1 block text-sm font-semibold text-slate-700">Mô tả chi tiết</label>
            <textarea v-model="form.mo_ta" rows="3" class="w-full rounded-xl border border-slate-200 px-4 py-2 text-sm text-slate-900 outline-none focus:border-[#2463eb]" placeholder="Mô tả kỹ năng..."></textarea>
          </div>
          <div class="mt-6 flex justify-end gap-3 pt-2">
            <button type="button" @click="closeModal" class="rounded-xl px-5 py-2.5 text-sm font-bold text-slate-600 hover:bg-slate-100">Huỷ bỏ</button>
            <button type="submit" class="rounded-xl bg-[#2463eb] px-5 py-2.5 text-sm font-bold text-white hover:bg-blue-700">{{ editMode ? 'Lưu thay đổi' : 'Tạo mới' }}</button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'

const skills = ref([])
const stats = ref({})
const loading = ref(true)
const searchQuery = ref('')
let searchTimeout = null

// Modal states
const isModalOpen = ref(false)
const editMode = ref(false)
const form = reactive({ id: null, ten_ky_nang: '', icon: '', mo_ta: '' })

const fetchStats = () => {
  stats.value = { total: 420, have_icon: 110, have_description: 380 }
}

const loadSkills = () => {
  loading.value = true
  // Mock API Call
  setTimeout(() => {
    skills.value = [
      { id: 1, ten_ky_nang: 'Vue.js', icon: '🍃', mo_ta: 'Progressive JavaScript Framework' },
      { id: 2, ten_ky_nang: 'Laravel', icon: '🔨', mo_ta: 'The PHP Framework for Web Artisans' },
      { id: 3, ten_ky_nang: 'FastAPI', icon: '⚡', mo_ta: 'Modern, fast web framework for Python' },
      { id: 4, ten_ky_nang: 'MySQL', icon: '🐬', mo_ta: 'Relational Database Management System' },
    ]
    loading.value = false
  }, 400)
}

const handleSearch = () => {
  clearTimeout(searchTimeout)
  // Debounce 250ms chống spam request
  searchTimeout = setTimeout(() => {
    loadSkills()
  }, 250)
}

const openModal = (skill = null) => {
  if (skill) {
    editMode.value = true
    form.id = skill.id
    form.ten_ky_nang = skill.ten_ky_nang
    form.icon = skill.icon
    form.mo_ta = skill.mo_ta
  } else {
    editMode.value = false
    form.id = null
    form.ten_ky_nang = ''
    form.icon = ''
    form.mo_ta = ''
  }
  isModalOpen.value = true
}

const closeModal = () => {
  isModalOpen.value = false
}

const saveSkill = () => {
  closeModal()
  loadSkills()
  fetchStats()
}

const confirmDelete = (id) => {
  if(confirm('Bạn có chắc chắn muốn xoá kỹ năng này? Hành động này không thể hoàn tác.')) {
    // Delete action mock
    skills.value = skills.value.filter(s => s.id !== id)
    fetchStats()
  }
}

onMounted(() => {
  fetchStats()
  loadSkills()
})
</script>
