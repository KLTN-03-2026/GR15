<template>
  <div class="p-6">
    <div class="mx-auto max-w-2xl">
      <h1 class="text-2xl font-bold text-slate-900">Hồ sơ Quản trị viên</h1>
      <p class="mt-1 text-sm text-slate-500">Quản lý thông tin cá nhân và cài đặt bảo mật.</p>

      <div class="mt-8 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        
        <!-- Avatar Section -->
        <div class="flex items-center gap-6 border-b border-slate-100 pb-6">
          <div class="relative">
            <div class="flex h-24 w-24 shrink-0 items-center justify-center overflow-hidden rounded-full border-4 border-slate-100 bg-slate-50">
              <img v-if="avatarPreview" :src="avatarPreview" alt="Avatar" class="h-full w-full object-cover" />
              <span v-else class="material-symbols-outlined text-4xl text-slate-300">person</span>
            </div>
            <label class="absolute bottom-0 right-0 flex h-8 w-8 cursor-pointer items-center justify-center rounded-full bg-[#2463eb] text-white ring-2 ring-white hover:bg-blue-700">
              <span class="material-symbols-outlined text-sm">edit</span>
              <input type="file" class="hidden" accept="image/*" @change="handleAvatarChange" />
            </label>
          </div>
          <div>
            <h3 class="text-lg font-bold text-slate-900">{{ form.ho_ten || 'Đang tải...' }}</h3>
            <p class="text-sm text-slate-500">System Administrator</p>
            <p class="mt-2 text-xs font-semibold uppercase tracking-wider text-green-600 bg-green-50 inline-block px-2 py-1 rounded">Active</p>
          </div>
        </div>

        <!-- Profile Form -->
        <form @submit.prevent="updateProfile" class="mt-6 space-y-5">
          <div v-if="successMsg" class="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
            {{ successMsg }}
          </div>

          <div>
            <label class="mb-1 block text-sm font-semibold text-slate-700">Họ và tên</label>
            <input 
              v-model="form.ho_ten" 
              type="text" 
              class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none focus:border-[#2463eb] focus:ring-4 focus:ring-blue-100" 
              placeholder="Nhập họ và tên"
            />
          </div>

          <div>
            <label class="mb-1 block text-sm font-semibold text-slate-700">Số điện thoại</label>
            <input 
              v-model="form.so_dien_thoai" 
              type="text" 
              class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none focus:border-[#2463eb] focus:ring-4 focus:ring-blue-100" 
              placeholder="Nhập số điện thoại"
            />
          </div>

          <div class="pt-4">
            <button 
              type="submit" 
              class="rounded-xl bg-[#2463eb] px-6 py-3 test-sm font-bold text-white transition hover:bg-blue-700"
              :disabled="loading"
            >
              Cập nhật hồ sơ
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'

const loading = ref(false)
const successMsg = ref('')
const avatarPreview = ref(null)

const form = reactive({
  ho_ten: '',
  so_dien_thoai: '',
  avatarFile: null
})

// Sync stored admin for testing (Mock)
const syncStoredAdmin = (data) => {
  localStorage.setItem('admin_profile', JSON.stringify(data))
  window.dispatchEvent(new Event('admin-profile-updated'))
}

const loadProfile = () => {
  // Mock fetch config
  const stored = JSON.parse(localStorage.getItem('admin_profile') || '{}')
  form.ho_ten = stored.ho_ten || 'Admin Root'
  form.so_dien_thoai = stored.so_dien_thoai || '0123456789'
  if (stored.avatar_url) avatarPreview.value = stored.avatar_url
}

const handleAvatarChange = (e) => {
  const file = e.target.files[0]
  if (!file) return

  form.avatarFile = file
  avatarPreview.value = URL.createObjectURL(file)
  uploadAvatarImmediately()
}

const uploadAvatarImmediately = async () => {
  // Logic mock API call immediately when image selected
  successMsg.value = 'Ảnh đại diện đã được thay đổi.'
  setTimeout(() => successMsg.value = '', 3000)
}

const updateProfile = async () => {
  loading.value = true
  // Mock update api
  setTimeout(() => {
    syncStoredAdmin({
      ho_ten: form.ho_ten,
      so_dien_thoai: form.so_dien_thoai,
      avatar_url: avatarPreview.value
    })
    successMsg.value = 'Cập nhật bộ hồ sơ thành công.'
    loading.value = false
    setTimeout(() => successMsg.value = '', 3000)
  }, 500)
}

onMounted(() => {
  loadProfile()
})
</script>
