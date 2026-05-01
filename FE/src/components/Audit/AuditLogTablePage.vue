<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useNotify } from '@/composables/useNotify'
import { companyService } from '@/services/api'

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  description: {
    type: String,
    required: true,
  },
  fetchLogs: {
    type: Function,
    required: true,
  },
  adminMode: {
    type: Boolean,
    default: false,
  },
})

const notify = useNotify()
const loading = ref(false)
const loadingCompanies = ref(false)
const logs = ref([])
const pagination = ref(null)
const companyOptions = ref([])

const filters = reactive({
  page: 1,
  per_page: 20,
  scope: '',
  action: '',
  actor_query: '',
  actor_role: '',
  company_id: '',
  from: '',
  to: '',
})

const scopeOptions = computed(() => [
  { value: '', label: 'Tất cả phạm vi' },
  { value: 'hr', label: 'HR nội bộ' },
  { value: 'employer_job', label: 'Tin tuyển dụng' },
  { value: 'employer_application', label: 'Ứng tuyển / phỏng vấn' },
  { value: 'candidate_application', label: 'Ứng viên ứng tuyển' },
  { value: 'candidate_follow', label: 'Theo dõi công ty' },
  ...(props.adminMode ? [
    { value: 'admin_user', label: 'Admin - người dùng' },
    { value: 'admin_company', label: 'Admin - công ty' },
    { value: 'admin_job', label: 'Admin - tin tuyển dụng' },
    { value: 'admin_cv_template', label: 'Admin - template CV' },
  ] : []),
])

const roleOptions = [
  { value: '', label: 'Tất cả vai trò' },
  { value: 'admin', label: 'Admin' },
  { value: 'nha_tuyen_dung', label: 'Nhà tuyển dụng' },
  { value: 'ung_vien', label: 'Ứng viên' },
]

const baseActionGroups = [
  {
    label: 'Công ty & nhân sự HR',
    actions: [
      { value: 'company_created', label: 'Tạo công ty' },
      { value: 'company_updated', label: 'Cập nhật thông tin công ty' },
      { value: 'member_added', label: 'Thêm HR trực tiếp' },
      { value: 'member_role_updated', label: 'Cập nhật quyền HR' },
      { value: 'member_removed', label: 'Gỡ HR khỏi công ty' },
    ],
  },
  {
    label: 'Tin tuyển dụng',
    actions: [
      { value: 'employer_job_created', label: 'Tạo tin tuyển dụng' },
      { value: 'employer_job_updated', label: 'Cập nhật tin tuyển dụng' },
      { value: 'employer_job_status_toggled', label: 'Bật/tắt trạng thái tin' },
      { value: 'employer_job_deleted', label: 'Xóa tin tuyển dụng' },
    ],
  },
  {
    label: 'Ứng tuyển & phỏng vấn',
    actions: [
      { value: 'employer_application_updated', label: 'Cập nhật đơn ứng tuyển' },
      { value: 'employer_interview_scheduled', label: 'Tạo lịch phỏng vấn' },
      { value: 'employer_interview_rescheduled', label: 'Đổi lịch phỏng vấn' },
      { value: 'employer_interview_email_resent', label: 'Gửi lại email lịch hẹn' },
      { value: 'employer_interview_round_created', label: 'Tạo vòng phỏng vấn' },
      { value: 'employer_interview_round_updated', label: 'Cập nhật vòng phỏng vấn' },
      { value: 'employer_interview_round_rescheduled', label: 'Đổi lịch vòng phỏng vấn' },
      { value: 'employer_interview_round_deleted', label: 'Xóa vòng phỏng vấn' },
      { value: 'employer_offer_sent', label: 'Gửi offer nhận việc' },
      { value: 'employer_onboarding_updated', label: 'Cập nhật onboarding' },
      { value: 'employer_interview_copilot_generated', label: 'Tạo bộ câu hỏi phỏng vấn AI' },
      { value: 'employer_interview_copilot_evaluated', label: 'AI đánh giá phỏng vấn' },
    ],
  },
  {
    label: 'Ứng viên',
    actions: [
      { value: 'candidate_application_submitted', label: 'Ứng viên nộp đơn' },
      { value: 'candidate_application_updated', label: 'Ứng viên cập nhật đơn' },
      { value: 'candidate_application_withdrawn', label: 'Ứng viên rút đơn' },
      { value: 'candidate_interview_responded', label: 'Ứng viên phản hồi phỏng vấn' },
      { value: 'candidate_interview_round_responded', label: 'Ứng viên phản hồi vòng phỏng vấn' },
      { value: 'candidate_offer_accepted', label: 'Ứng viên chấp nhận offer' },
      { value: 'candidate_offer_declined', label: 'Ứng viên từ chối offer' },
      { value: 'candidate_offer_accepted_email', label: 'Ứng viên chấp nhận offer qua email' },
      { value: 'candidate_offer_declined_email', label: 'Ứng viên từ chối offer qua email' },
      { value: 'candidate_company_followed', label: 'Ứng viên theo dõi công ty' },
      { value: 'candidate_company_unfollowed', label: 'Ứng viên bỏ theo dõi công ty' },
    ],
  },
]

const adminActionGroups = [
  {
    label: 'Admin - người dùng',
    actions: [
      { value: 'admin_user_created', label: 'Tạo người dùng' },
      { value: 'admin_user_updated', label: 'Cập nhật người dùng' },
      { value: 'admin_user_locked', label: 'Khóa tài khoản' },
      { value: 'admin_user_unlocked', label: 'Mở khóa tài khoản' },
      { value: 'admin_user_deleted', label: 'Xóa người dùng' },
    ],
  },
  {
    label: 'Admin - công ty',
    actions: [
      { value: 'admin_company_created', label: 'Tạo công ty' },
      { value: 'admin_company_updated', label: 'Cập nhật công ty' },
      { value: 'admin_company_status_toggled', label: 'Bật/tắt trạng thái công ty' },
      { value: 'admin_company_deleted', label: 'Xóa công ty' },
    ],
  },
  {
    label: 'Admin - tin tuyển dụng',
    actions: [
      { value: 'admin_job_created', label: 'Tạo tin tuyển dụng' },
      { value: 'admin_job_updated', label: 'Cập nhật tin tuyển dụng' },
      { value: 'admin_job_status_toggled', label: 'Bật/tắt trạng thái tin' },
      { value: 'admin_job_deleted', label: 'Xóa tin tuyển dụng' },
    ],
  },
  {
    label: 'Admin - template CV',
    actions: [
      { value: 'admin_cv_template_created', label: 'Tạo template CV' },
      { value: 'admin_cv_template_updated', label: 'Cập nhật template CV' },
      { value: 'admin_cv_template_status_toggled', label: 'Bật/tắt template CV' },
      { value: 'admin_cv_template_deleted', label: 'Xóa template CV' },
    ],
  },
]

const actionGroups = computed(() => [
  ...baseActionGroups,
  ...(props.adminMode ? adminActionGroups : []),
])

const actionLabelMap = computed(() => {
  const pairs = actionGroups.value.flatMap((group) => group.actions.map((action) => [action.value, action.label]))
  return Object.fromEntries(pairs)
})

const getActionLabel = (action) => actionLabelMap.value[action] || action

const formatDateTime = (value) => {
  if (!value) return '--'
  return new Intl.DateTimeFormat('vi-VN', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(new Date(value))
}

const fetchData = async () => {
  loading.value = true
  try {
    const response = await props.fetchLogs(filters)
    const payload = response?.data || {}
    logs.value = payload.data || []
    pagination.value = payload
  } catch (error) {
    logs.value = []
    pagination.value = null
    notify.apiError(error, 'Không tải được nhật ký audit.')
  } finally {
    loading.value = false
  }
}

const fetchCompanyOptions = async () => {
  if (!props.adminMode) return

  loadingCompanies.value = true
  try {
    const response = await companyService.getCompanies({
      sort_by: 'ten_cong_ty',
      sort_dir: 'asc',
    })
    const payload = response?.data
    companyOptions.value = Array.isArray(payload)
      ? payload
      : Array.isArray(payload?.data)
        ? payload.data
        : []
  } catch (error) {
    companyOptions.value = []
    notify.apiError(error, 'Không tải được danh sách công ty để lọc nhật ký.')
  } finally {
    loadingCompanies.value = false
  }
}

const applyFilters = async () => {
  filters.page = 1
  await fetchData()
}

const resetFilters = async () => {
  filters.page = 1
  filters.scope = ''
  filters.action = ''
  filters.actor_query = ''
  filters.actor_role = ''
  filters.company_id = ''
  filters.from = ''
  filters.to = ''
  await fetchData()
}

const goToPage = async (page) => {
  if (!page || page === filters.page) return
  filters.page = page
  await fetchData()
}

onMounted(() => {
  fetchData()
  fetchCompanyOptions()
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex flex-wrap items-end justify-between gap-4">
      <div>
        <p class="text-xs font-bold uppercase tracking-[0.24em] text-blue-600/80 dark:text-blue-300/80">Audit log</p>
        <h1 class="mt-2 text-3xl font-black tracking-tight text-slate-900 dark:text-white">{{ title }}</h1>
        <p class="mt-1 max-w-3xl text-sm text-slate-500 dark:text-slate-400">{{ description }}</p>
      </div>
      <button
        class="rounded-xl border border-slate-200 px-4 py-3 text-sm font-bold transition hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-800"
        type="button"
        @click="fetchData"
      >
        Làm mới
      </button>
    </div>

    <div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        <div>
          <label class="mb-2 block text-xs font-bold uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">
            Phạm vi nhật ký
          </label>
          <select
            v-model="filters.scope"
            class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none focus:border-[#2463eb] dark:border-slate-800 dark:bg-slate-950"
          >
            <option v-for="option in scopeOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </div>
        <div>
          <label class="mb-2 block text-xs font-bold uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">
            Loại thao tác
          </label>
          <select
            v-model="filters.action"
            class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none focus:border-[#2463eb] dark:border-slate-800 dark:bg-slate-950"
          >
            <option value="">Tất cả thao tác</option>
            <optgroup v-for="group in actionGroups" :key="group.label" :label="group.label">
              <option v-for="action in group.actions" :key="action.value" :value="action.value">
                {{ action.label }}
              </option>
            </optgroup>
          </select>
          <p class="mt-1 text-xs text-slate-400">
            Chọn theo tên nghiệp vụ, hệ thống tự lọc bằng mã action tương ứng.
          </p>
        </div>
        <div>
          <label class="mb-2 block text-xs font-bold uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">
            Người thực hiện
          </label>
          <input
            v-model="filters.actor_query"
            class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none focus:border-[#2463eb] dark:border-slate-800 dark:bg-slate-950"
            placeholder="Nhập tên, email hoặc ID"
            type="text"
            @keyup.enter="applyFilters"
          >
          <p class="mt-1 text-xs text-slate-400">
            Ví dụ: Nguyễn Văn A, hr@company.com hoặc 12.
          </p>
        </div>
        <div v-if="adminMode">
          <label class="mb-2 block text-xs font-bold uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">
            Vai trò người thực hiện
          </label>
          <select
            v-model="filters.actor_role"
            class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none focus:border-[#2463eb] dark:border-slate-800 dark:bg-slate-950"
          >
            <option v-for="option in roleOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </div>
        <div v-if="adminMode">
          <label class="mb-2 block text-xs font-bold uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">
            Công ty
          </label>
          <select
            v-model="filters.company_id"
            :disabled="loadingCompanies"
            class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none focus:border-[#2463eb] dark:border-slate-800 dark:bg-slate-950"
          >
            <option value="">
              {{ loadingCompanies ? 'Đang tải công ty...' : 'Tất cả công ty' }}
            </option>
            <option v-for="company in companyOptions" :key="company.id" :value="company.id">
              {{ company.ten_cong_ty }}{{ company.email ? ` - ${company.email}` : '' }}
            </option>
          </select>
        </div>
        <div>
          <label class="mb-2 block text-xs font-bold uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">
            Từ ngày
          </label>
          <input
            v-model="filters.from"
            class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none focus:border-[#2463eb] dark:border-slate-800 dark:bg-slate-950"
            type="date"
          >
        </div>
        <div>
          <label class="mb-2 block text-xs font-bold uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">
            Đến ngày
          </label>
          <input
            v-model="filters.to"
            class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none focus:border-[#2463eb] dark:border-slate-800 dark:bg-slate-950"
            type="date"
          >
        </div>
      </div>
      <div class="mt-4 flex flex-wrap gap-3">
        <button
          class="rounded-xl bg-[#2463eb] px-5 py-3 text-sm font-bold text-white transition hover:bg-blue-700"
          type="button"
          @click="applyFilters"
        >
          Áp dụng bộ lọc
        </button>
        <button
          class="rounded-xl border border-slate-200 px-5 py-3 text-sm font-bold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
          type="button"
          @click="resetFilters"
        >
          Xóa lọc
        </button>
      </div>
    </div>

    <div class="rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div v-if="loading" class="space-y-3 p-4">
        <div v-for="index in 6" :key="index" class="h-20 animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800" />
      </div>

      <div v-else-if="!logs.length" class="p-10 text-center">
        <div class="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-300">
          <span class="material-symbols-outlined">manage_search</span>
        </div>
        <h2 class="mt-4 text-lg font-black text-slate-900 dark:text-white">Chưa có nhật ký phù hợp</h2>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Thử đổi bộ lọc hoặc thực hiện một thao tác có ghi audit.</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full min-w-[840px] text-left">
          <thead>
            <tr class="border-b border-slate-200 bg-slate-50 dark:border-slate-800 dark:bg-slate-800/50">
              <th class="px-5 py-4 text-xs font-bold uppercase tracking-wider text-slate-500">Thời gian</th>
              <th class="px-5 py-4 text-xs font-bold uppercase tracking-wider text-slate-500">Người thực hiện</th>
              <th class="px-5 py-4 text-xs font-bold uppercase tracking-wider text-slate-500">Thao tác</th>
              <th class="px-5 py-4 text-xs font-bold uppercase tracking-wider text-slate-500">Mô tả</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 dark:divide-slate-800">
            <tr v-for="log in logs" :key="log.id" class="align-top">
              <td class="px-5 py-4 text-sm text-slate-600 dark:text-slate-300">
                {{ formatDateTime(log.created_at) }}
              </td>
              <td class="px-5 py-4">
                <p class="text-sm font-bold text-slate-900 dark:text-white">{{ log.actor?.ho_ten || 'Hệ thống' }}</p>
                <p class="text-xs text-slate-500">{{ log.actor?.email || log.actor_role || '--' }}</p>
                <p v-if="log.company" class="mt-1 text-xs text-slate-400">{{ log.company.ten_cong_ty }}</p>
              </td>
              <td class="px-5 py-4">
                <span class="rounded-full bg-blue-50 px-3 py-1 text-xs font-bold text-blue-700 dark:bg-blue-500/10 dark:text-blue-200">
                  {{ getActionLabel(log.action) }}
                </span>
              </td>
              <td class="max-w-2xl px-5 py-4 text-sm text-slate-600 dark:text-slate-300">
                {{ log.description }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div
        v-if="pagination && pagination.last_page > 1"
        class="flex items-center justify-between border-t border-slate-200 px-5 py-4 text-sm dark:border-slate-800"
      >
        <span class="text-slate-500">
          Trang {{ pagination.current_page }} / {{ pagination.last_page }}
        </span>
        <div class="flex gap-2">
          <button
            class="rounded-lg border border-slate-200 px-3 py-2 font-bold disabled:cursor-not-allowed disabled:opacity-40 dark:border-slate-700"
            :disabled="pagination.current_page <= 1 || loading"
            type="button"
            @click="goToPage(pagination.current_page - 1)"
          >
            Trước
          </button>
          <button
            class="rounded-lg border border-slate-200 px-3 py-2 font-bold disabled:cursor-not-allowed disabled:opacity-40 dark:border-slate-700"
            :disabled="pagination.current_page >= pagination.last_page || loading"
            type="button"
            @click="goToPage(pagination.current_page + 1)"
          >
            Sau
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
