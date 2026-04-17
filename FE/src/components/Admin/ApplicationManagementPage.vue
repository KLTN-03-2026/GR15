<template>
  <div class="p-6">
    <div class="mb-6 flex flex-col justify-between gap-4 md:flex-row md:items-center">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">Quản lý Đơn ứng tuyển</h1>
        <p class="mt-1 text-sm text-slate-500">Giám sát tổng thể các hồ sơ ứng tuyển trên hệ thống.</p>
      </div>
      <div class="flex gap-2">
        <select v-model="selectedStatus" @change="loadApplications" class="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm text-slate-700 outline-none">
          <option value="">Tất cả trạng thái</option>
          <option value="cho_duyet">Chờ duyệt</option>
          <option value="da_xem">Đã xem</option>
          <option value="phong_van">Phỏng vấn</option>
          <option value="chap_nhan">Chấp nhận</option>
          <option value="tu_choi">Từ chối</option>
        </select>
        <button class="rounded-xl bg-slate-100 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-200">
          <span class="material-symbols-outlined text-[18px] align-middle">download</span>
          Xuất báo cáo
        </button>
      </div>
    </div>

    <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm text-slate-600">
          <thead class="bg-slate-50 text-xs uppercase text-slate-500">
            <tr>
              <th scope="col" class="px-6 py-4 font-bold">Ứng viên / Email</th>
              <th scope="col" class="px-6 py-4 font-bold">Vị trí ứng tuyển</th>
              <th scope="col" class="px-6 py-4 font-bold">Công ty</th>
              <th scope="col" class="px-6 py-4 font-bold">Thời gian nộp</th>
              <th scope="col" class="px-6 py-4 font-bold text-center">Trạng thái</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200">
            <template v-if="loading">
              <tr v-for="i in 5" :key="i" class="animate-pulse">
                <td class="px-6 py-4"><div class="h-4 w-32 rounded bg-slate-200"></div></td>
                <td class="px-6 py-4"><div class="h-4 w-40 rounded bg-slate-200"></div></td>
                <td class="px-6 py-4"><div class="h-4 w-24 rounded bg-slate-200"></div></td>
                <td class="px-6 py-4"><div class="h-4 w-20 rounded bg-slate-200"></div></td>
                <td class="px-6 py-4"><div class="mx-auto h-6 w-20 rounded-full bg-slate-200"></div></td>
              </tr>
            </template>
            <tr v-else-if="applications.length" v-for="app in applications" :key="app.id" class="transition hover:bg-slate-50">
              <td class="px-6 py-4">
                <div class="font-bold text-slate-900">{{ app.ho_so?.nguoi_dung?.ho_ten || 'Ứng viên' }}</div>
                <div class="text-xs text-slate-400">{{ app.ho_so?.nguoi_dung?.email || 'N/A' }}</div>
              </td>
              <td class="px-6 py-4 font-medium text-slate-800">
                {{ app.tin_tuyen_dung?.tieu_de || 'Không rõ' }}
              </td>
              <td class="px-6 py-4 text-slate-500">
                {{ app.tin_tuyen_dung?.cong_ty?.ten_cong_ty || 'N/A' }}
              </td>
              <td class="px-6 py-4 text-slate-500">
                10/04/2026
              </td>
              <td class="px-6 py-4 text-center text-xs font-semibold">
                <span v-if="app.trang_thai === 'cho_duyet'" class="rounded-full bg-slate-100 px-3 py-1 text-slate-600">Chờ duyệt</span>
                <span v-else-if="app.trang_thai === 'phong_van'" class="rounded-full bg-blue-100 px-3 py-1 text-blue-700">Phỏng vấn</span>
                <span v-else-if="app.trang_thai === 'chap_nhan'" class="rounded-full bg-emerald-100 px-3 py-1 text-emerald-700">Chấp nhận</span>
                <span v-else-if="app.trang_thai === 'tu_choi'" class="rounded-full bg-rose-100 px-3 py-1 text-rose-700">Từ chối</span>
                <span v-else class="rounded-full bg-slate-100 px-3 py-1 text-slate-800">{{ app.trang_thai }}</span>
              </td>
            </tr>
            <tr v-else>
              <td colspan="5" class="px-6 py-12 text-center text-slate-500">Không có đơn ứng tuyển nào được tìm thấy.</td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- AdminPaginationBar Mock -->
      <div v-if="!loading && applications.length" class="flex items-center justify-between border-t border-slate-200 bg-white px-6 py-4">
        <p class="text-sm text-slate-500">Hiển thị <span class="font-bold">1</span> đến <span class="font-bold">10</span> trong <span class="font-bold">42</span> kết quả</p>
        <div class="flex gap-1">
          <button class="rounded-md border border-slate-200 px-3 py-1 text-sm hover:bg-slate-50 text-slate-500">Trước</button>
          <button class="rounded-md bg-[#2463eb] px-3 py-1 text-sm font-bold text-white">1</button>
          <button class="rounded-md border border-slate-200 px-3 py-1 text-sm hover:bg-slate-50">2</button>
          <button class="rounded-md border border-slate-200 px-3 py-1 text-sm hover:bg-slate-50 text-slate-500">Sau</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const applications = ref([])
const loading = ref(true)
const selectedStatus = ref('')
const selectedCompany = ref('')

const loadApplications = () => {
  loading.value = true
  // Mock API call to adminApplicationService.getApplications
  setTimeout(() => {
    applications.value = [
      { id: 1, trang_thai: 'cho_duyet', ho_so: { nguoi_dung: { ho_ten: 'Nguyễn Văn A', email: 'nguyenvana@gmail.com' } }, tin_tuyen_dung: { tieu_de: 'Frontend Developer (VueJS)', cong_ty: { ten_cong_ty: 'FPT Software' } } },
      { id: 2, trang_thai: 'phong_van', ho_so: { nguoi_dung: { ho_ten: 'Trần B', email: 'tranb@gmail.com' } }, tin_tuyen_dung: { tieu_de: 'Senior PHP Laravel', cong_ty: { ten_cong_ty: 'VNG Corporation' } } },
      { id: 3, trang_thai: 'chap_nhan', ho_so: { nguoi_dung: { ho_ten: 'Lê C', email: 'lec@gmail.com' } }, tin_tuyen_dung: { tieu_de: 'UI/UX Designer', cong_ty: { ten_cong_ty: 'Tiki' } } },
    ]
    loading.value = false
  }, 600)
}

onMounted(() => {
  loadApplications()
})
</script>
