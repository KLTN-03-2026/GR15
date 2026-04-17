<template>
  <div class="p-6">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-slate-900">Thông tin Doanh nghiệp</h1>
      <p class="mt-1 text-sm text-slate-500">Quản lý hồ sơ công ty và đội ngũ nhân sự nội bộ.</p>
    </div>

    <!-- Company Profile Form -->
    <div class="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm mb-8">
      <h2 class="mb-6 text-lg font-bold text-slate-900">Chi tiết doanh nghiệp</h2>

      <div class="flex flex-col gap-8 md:flex-row">
        <!-- Logo Section -->
        <div class="flex-shrink-0">
          <label class="mb-2 block text-sm font-semibold text-slate-700">Logo công ty</label>
          <div class="relative mt-2">
            <div class="flex h-36 w-36 items-center justify-center overflow-hidden rounded-2xl border-2 border-dashed border-slate-300 bg-slate-50 relative group">
              <img v-if="logoPreview" :src="logoPreview" alt="Logo" class="h-full w-full object-cover" />
              <div v-else class="text-center text-slate-400">
                <span class="material-symbols-outlined text-4xl">domain_add</span>
                <p class="mt-1 text-xs font-semibold">Tải ảnh lên</p>
              </div>
              <div class="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition flex items-center justify-center cursor-pointer">
                <span class="material-symbols-outlined text-white text-2xl">edit</span>
                <input type="file" @change="handleLogoChange" class="absolute inset-0 opacity-0 cursor-pointer w-full h-full" accept="image/*" />
              </div>
            </div>
          </div>
        </div>

        <!-- Form Section -->
        <form @submit.prevent="updateCompany" class="flex-1 space-y-5">
          <div v-if="saveMessage" class="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700 font-medium">
            {{ saveMessage }}
          </div>

          <div class="grid gap-5 md:grid-cols-2">
            <div>
              <label class="mb-1 block text-sm font-semibold text-slate-700">Tên công ty *</label>
              <input v-model="form.ten_cong_ty" type="text" required class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none focus:border-[#2463eb]" placeholder="VD: FPT Software" />
            </div>
            <div>
              <label class="mb-1 block text-sm font-semibold text-slate-700">Mã số thuế</label>
              <input v-model="form.ma_so_thue" type="text" class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none focus:border-[#2463eb]" placeholder="Mã số đăng ký kinh doanh" />
            </div>
            <div class="md:col-span-2">
              <label class="mb-1 block text-sm font-semibold text-slate-700">Trụ sở chính</label>
              <input v-model="form.dia_chi" type="text" class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none focus:border-[#2463eb]" placeholder="Địa chỉ đầy đủ" />
            </div>
            <div>
              <label class="mb-1 block text-sm font-semibold text-slate-700">Website</label>
              <input v-model="form.website" type="url" class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none focus:border-[#2463eb]" placeholder="https://" />
            </div>
            <div>
              <label class="mb-1 block text-sm font-semibold text-slate-700">Quy mô nhân sự</label>
              <select v-model="form.quy_mo" class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none focus:border-[#2463eb]">
                <option value="">Chọn quy mô</option>
                <option value="1-50">1 - 50 nhân viên</option>
                <option value="51-150">51 - 150 nhân viên</option>
                <option value="150+">150+ nhân viên</option>
              </select>
            </div>
          </div>
          <div>
            <label class="mb-1 block text-sm font-semibold text-slate-700">Mô tả công ty</label>
            <textarea v-model="form.mo_ta" rows="4" class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none focus:border-[#2463eb]" placeholder="Giới thiệu về doanh nghiệp, môi trường văn hoá..."></textarea>
          </div>
          
          <div class="pt-4 text-right">
            <button type="submit" :disabled="loading" class="rounded-xl bg-[#2463eb] px-6 py-3 text-sm font-bold text-white transition hover:bg-blue-700 disabled:opacity-50">
              {{ loading ? 'Đang cập nhật...' : 'Lưu thông tin' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- HR Management Panel -->
    <div class="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
      <div class="mb-6 flex flex-col justify-between gap-4 md:flex-row md:items-center">
        <div>
          <h2 class="text-lg font-bold text-slate-900">Quản lý Nhân sự (HR)</h2>
          <p class="text-sm text-slate-500">Phân quyền các thành viên tham gia tuyển dụng.</p>
        </div>
        <button class="flex items-center gap-2 rounded-xl bg-slate-900 px-4 py-2 text-sm font-bold text-white hover:bg-slate-800">
          <span class="material-symbols-outlined text-[18px]">person_add</span>
          Mời thành viên mới
        </button>
      </div>

      <div class="overflow-x-auto rounded-2xl border border-slate-200">
        <table class="w-full text-left text-sm text-slate-600">
          <thead class="bg-slate-50 text-xs uppercase text-slate-500">
            <tr>
              <th class="px-6 py-4 font-bold">Thành viên</th>
              <th class="px-6 py-4 font-bold">Quyền hạn (Role)</th>
              <th class="px-6 py-4 font-bold text-right">Phím</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="member in members" :key="member.id" class="transition hover:bg-slate-50">
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                  <div class="flex size-10 shrink-0 items-center justify-center rounded-full bg-[#2463eb] text-sm font-bold text-white">
                    {{ member.ho_ten.charAt(0).toUpperCase() }}
                  </div>
                  <div>
                    <h3 class="font-bold text-slate-900">{{ member.ho_ten }}</h3>
                    <p class="text-xs text-slate-500">{{ member.email }}</p>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4">
                <select 
                  v-model="member.role" 
                  @change="updateRole(member)"
                  :disabled="!isOwner || member.role === 'owner'"
                  class="rounded-lg border border-slate-200 px-3 py-1.5 text-sm font-semibold outline-none focus:border-[#2463eb]"
                >
                  <option value="owner" disabled>Chủ sở hữu</option>
                  <option value="admin">Quản lý (Admin)</option>
                  <option value="hr">Nhà tuyển dụng (HR)</option>
                  <option value="member">Nhân viên</option>
                </select>
              </td>
              <td class="px-6 py-4 text-right">
                <button 
                  v-if="member.role !== 'owner' && isOwner"
                  @click="removeMember(member.id)"
                  class="text-rose-500 hover:text-rose-700" 
                  title="Xoá thành viên"
                >
                  <span class="material-symbols-outlined text-[20px]">person_remove</span>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'

const loading = ref(false)
const saveMessage = ref('')
const isOwner = ref(true) // Mock true cho admin access

const form = reactive({ ten_cong_ty: '', ma_so_thue: '', dia_chi: '', website: '', quy_mo: '', mo_ta: '' })
const logoPreview = ref(null)
const members = ref([])

const loadData = () => {
  // Mock Data
  Object.assign(form, {
    ten_cong_ty: 'Công ty TNHH SmartJob AI',
    ma_so_thue: '0101234567',
    dia_chi: 'QTSC Building 1, CVPM Quang Trung, Q.12, TP.HCM',
    website: 'https://smartjob-ai.com',
    quy_mo: '51-150',
    mo_ta: 'Tiên phong trong lĩnh vực AI Recruitment Platform.'
  })
  
  members.value = [
    { id: 1, ho_ten: 'Lê Văn Owner', email: 'owner@smartjob.com', role: 'owner' },
    { id: 2, ho_ten: 'Trần Thị HR', email: 'hr1@smartjob.com', role: 'hr' },
    { id: 3, ho_ten: 'Bùi Admin', email: 'admin@smartjob.com', role: 'admin' },
  ]
}

const handleLogoChange = (e) => {
  const file = e.target.files[0]
  if (file) {
    logoPreview.value = URL.createObjectURL(file)
  }
}

const updateCompany = () => {
  loading.value = true
  saveMessage.value = ''
  setTimeout(() => {
    loading.value = false
    saveMessage.value = 'Thông tin doanh nghiệp đã được cập nhật.'
    setTimeout(() => saveMessage.value = '', 4000)
  }, 600)
}

const updateRole = (member) => {
  console.log('Update role for', member.id, 'to', member.role)
  // Thực tế sẽ gọi API: apiCall(`/nha-tuyen-dung/cong-ty/thanh-viens`, { method: 'PUT', body: JSON.stringify({nguoi_dung_id: member.id, vai_tro_noi_bo: member.role}) })
}

const removeMember = (id) => {
  if (confirm('Chắc chắn muốn xoá thành viên này khỏi doanh nghiệp?')) {
    members.value = members.value.filter(m => m.id !== id)
  }
}

// Websocket Realtime follower simulation
onMounted(() => {
  loadData()
  console.log('[Echo WebSocket] Subscribed to .company.followers.updated (companyId: 1)')
})

onUnmounted(() => {
  console.log('[Echo WebSocket] Unsubscribed from company channel')
})
</script>
