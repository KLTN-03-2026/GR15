<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import {
  adminApplicationService,
  adminBillingService,
  adminJobPostingService,
  adminProfileService,
  companyService,
  userService,
} from '@/services/api'
import { useNotify } from '@/composables/useNotify'
import { getStoredUser } from '@/utils/authStorage'
import { hasAdminPermission } from '@/constants/adminPermissions'

const notify = useNotify()

const loading = ref(false)
const userStats = ref(null)
const profileStats = ref(null)
const jobStats = ref(null)
const applicationStats = ref(null)
const billingOverview = ref(null)
const recentUsers = ref([])
const recentPayments = ref([])
const recentJobs = ref([])
const recentCompanies = ref([])

const currentAdmin = computed(() => getStoredUser())
const canViewUsers = computed(() => hasAdminPermission(currentAdmin.value, 'users'))
const canViewCompanies = computed(() => hasAdminPermission(currentAdmin.value, 'companies'))
const canViewProfiles = computed(() => hasAdminPermission(currentAdmin.value, 'profiles'))
const canViewJobs = computed(() => hasAdminPermission(currentAdmin.value, 'jobs'))
const canViewApplications = computed(() => hasAdminPermission(currentAdmin.value, 'applications'))
const canViewBilling = computed(() => hasAdminPermission(currentAdmin.value, 'billing'))

const formatNumber = (value) => new Intl.NumberFormat('vi-VN').format(Number(value || 0))

const formatCurrencyCompact = (value) => {
  const amount = Number(value || 0)
  if (amount >= 1000000000) return `${(amount / 1000000000).toFixed(amount % 1000000000 ? 1 : 0)}B đ`
  if (amount >= 1000000) return `${(amount / 1000000).toFixed(amount % 1000000 ? 1 : 0)}M đ`
  return `${formatNumber(amount)} đ`
}

const formatDate = (value) => {
  if (!value) return 'Chưa cập nhật'
  return new Intl.DateTimeFormat('vi-VN', { dateStyle: 'short' }).format(new Date(value))
}

const formatRelativeTime = (value) => {
  if (!value) return 'Vừa cập nhật'
  const diffMs = Date.now() - new Date(value).getTime()
  const diffMinutes = Math.max(0, Math.floor(diffMs / 60000))
  if (diffMinutes < 1) return 'Vừa xong'
  if (diffMinutes < 60) return `${diffMinutes} phút trước`
  const diffHours = Math.floor(diffMinutes / 60)
  if (diffHours < 24) return `${diffHours} giờ trước`
  const diffDays = Math.floor(diffHours / 24)
  return `${diffDays} ngày trước`
}

const safePercent = (value, total) => {
  if (!total) return 0
  return Math.min(100, Math.round((Number(value || 0) / Number(total || 1)) * 100))
}

const normalizePaginatedList = (response) => {
  const payload = response?.data
  if (Array.isArray(payload)) return payload
  if (Array.isArray(payload?.data)) return payload.data
  if (Array.isArray(response?.nguoi_dungs)) return response.nguoi_dungs
  return []
}

const roleLabel = (role) => {
  if (Number(role) === 1) return 'Nhà tuyển dụng'
  if (Number(role) === 2) return 'Admin'
  return 'Ứng viên'
}

const statusLabel = (status) => Number(status) === 1 ? 'Hoạt động' : 'Tạm khóa'

const kpiCards = computed(() => {
  const users = userStats.value || {}
  const jobs = jobStats.value || {}
  const profiles = profileStats.value || {}
  const billingTotals = billingOverview.value?.totals || {}

  return [
    canViewUsers.value ? {
      label: 'Tổng người dùng',
      value: formatNumber(users.tong || 0),
      badge: `${safePercent(users.dang_hoat_dong, users.tong)}%`,
      badgeTone: 'text-emerald-500',
      icon: 'person_add',
      iconTone: 'bg-blue-50 text-blue-600',
      helper: `${formatNumber(users.dang_hoat_dong || 0)} tài khoản hoạt động`,
    } : null,
    canViewJobs.value ? {
      label: 'Tin tuyển dụng',
      value: formatNumber(jobs.tong_tin || 0),
      badge: `${safePercent(jobs.hoat_dong, jobs.tong_tin)}%`,
      badgeTone: 'text-emerald-500',
      icon: 'assignment',
      iconTone: 'bg-orange-50 text-orange-600',
      helper: `${formatNumber(jobs.hoat_dong || 0)} tin đang hoạt động`,
    } : null,
    canViewProfiles.value ? {
      label: 'Tổng hồ sơ',
      value: formatNumber(profiles.tong || 0),
      badge: `${safePercent(profiles.cong_khai, profiles.tong)}%`,
      badgeTone: 'text-emerald-500',
      icon: 'description',
      iconTone: 'bg-emerald-50 text-emerald-600',
      helper: `${formatNumber(profiles.cong_khai || 0)} hồ sơ công khai`,
    } : null,
    canViewBilling.value ? {
      label: 'Doanh thu',
      value: formatCurrencyCompact(billingTotals.processed_amount),
      badge: `${safePercent(billingTotals.topup_amount, billingTotals.processed_amount)}%`,
      badgeTone: 'text-emerald-500',
      icon: 'payments',
      iconTone: 'bg-rose-50 text-orange-600',
      helper: `${formatNumber(billingTotals.pending_count || 0)} giao dịch pending`,
    } : null,
  ].filter(Boolean)
})

const monthBuckets = computed(() => {
  const now = new Date()
  const buckets = Array.from({ length: 6 }, (_, index) => {
    const date = new Date(now.getFullYear(), now.getMonth() - (5 - index), 1)
    return {
      key: `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`,
      label: `T${date.getMonth() + 1}`,
      value: 0,
    }
  })

  recentUsers.value.forEach((user) => {
    if (!user.created_at) return
    const date = new Date(user.created_at)
    const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
    const bucket = buckets.find((item) => item.key === key)
    if (bucket) bucket.value += 1
  })

  return buckets
})

const chartBars = computed(() => {
  const max = Math.max(...monthBuckets.value.map((item) => item.value), 1)
  return monthBuckets.value.map((item) => ({
    ...item,
    height: Math.max(10, Math.round((item.value / max) * 100)),
  }))
})

const recentActivities = computed(() => {
  const activities = []

  recentCompanies.value.slice(0, 2).forEach((company) => {
    activities.push({
      id: `company-${company.id}`,
      title: 'Nhà tuyển dụng mới đăng ký',
      description: `${company.ten_cong_ty || 'Công ty'} - ${formatRelativeTime(company.created_at)}`,
      dot: 'bg-emerald-500',
      createdAt: company.created_at,
    })
  })

  recentPayments.value.slice(0, 2).forEach((payment) => {
    activities.push({
      id: `payment-${payment.id || payment.ma_giao_dich_noi_bo}`,
      title: payment.loai_giao_dich === 'buy_subscription' ? 'Thanh toán gói Pro' : 'Nạp ví AI',
      description: `${payment.nguoi_dung?.ho_ten || payment.nguoi_dung?.email || 'User'} - ${formatRelativeTime(payment.created_at)}`,
      dot: 'bg-orange-500',
      createdAt: payment.created_at,
    })
  })

  recentJobs.value.slice(0, 2).forEach((job) => {
    activities.push({
      id: `job-${job.id}`,
      title: 'Tin tuyển dụng mới',
      description: `${job.tieu_de || 'Tin tuyển dụng'} - ${formatRelativeTime(job.created_at)}`,
      dot: 'bg-blue-500',
      createdAt: job.created_at,
    })
  })

  if (canViewApplications.value) {
    const totalApplications = applicationStats.value?.tong_don_ung_tuyen || 0
    activities.push({
      id: 'applications-total',
      title: `${formatNumber(totalApplications)} hồ sơ đã ứng tuyển`,
      description: 'Tổng đơn ứng tuyển toàn hệ thống',
      dot: 'bg-emerald-500',
      createdAt: null,
    })
  }

  return activities
    .sort((left, right) => new Date(right.createdAt || 0) - new Date(left.createdAt || 0))
    .slice(0, 5)
})

const fetchDashboard = async () => {
  loading.value = true
  try {
    const tasks = []
    const enqueue = (enabled, request, assign) => {
      if (!enabled) return
      tasks.push(request().then((response) => assign(response)))
    }

    enqueue(canViewUsers.value, userService.getUserStats, (response) => { userStats.value = response?.data || null })
    enqueue(canViewProfiles.value, adminProfileService.getStats, (response) => { profileStats.value = response?.data || null })
    enqueue(canViewJobs.value, adminJobPostingService.getStats, (response) => { jobStats.value = response?.data || null })
    enqueue(canViewApplications.value, adminApplicationService.getStats, (response) => { applicationStats.value = response?.data || null })
    enqueue(canViewBilling.value, adminBillingService.getOverview, (response) => { billingOverview.value = response?.data || null })
    enqueue(canViewUsers.value, () => userService.getUsers({ page: 1, per_page: 100, sort_by: 'created_at', sort_dir: 'desc' }), (response) => {
      recentUsers.value = normalizePaginatedList(response)
    })
    enqueue(canViewBilling.value, () => adminBillingService.getPayments({ page: 1, per_page: 5 }), (response) => {
      recentPayments.value = normalizePaginatedList(response)
    })
    enqueue(canViewJobs.value, () => adminJobPostingService.getJobs({ page: 1, per_page: 5 }), (response) => {
      recentJobs.value = normalizePaginatedList(response)
    })
    enqueue(canViewCompanies.value, () => companyService.getCompanies({ page: 1, per_page: 5, sort_by: 'created_at', sort_dir: 'desc' }), (response) => {
      recentCompanies.value = normalizePaginatedList(response)
    })

    const results = await Promise.allSettled(tasks)
    if (results.some((result) => result.status === 'rejected')) {
      notify.warning('Một vài khối dashboard chưa tải được dữ liệu, các phần còn lại vẫn được hiển thị.')
    }
  } catch (error) {
    notify.apiError(error, 'Không tải được dữ liệu dashboard quản trị.')
  } finally {
    loading.value = false
  }
}

onMounted(fetchDashboard)
</script>

<template>
  <div class="space-y-8">
    <div class="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-4">
      <article
        v-for="card in kpiCards"
        :key="card.label"
        class="rounded-[18px] border border-slate-200 bg-white p-7 shadow-sm dark:border-slate-800 dark:bg-slate-900"
      >
        <div class="flex items-start justify-between gap-4">
          <div class="flex size-16 items-center justify-center rounded-2xl" :class="card.iconTone">
            <span class="material-symbols-outlined text-4xl">{{ card.icon }}</span>
          </div>
          <span class="inline-flex items-center gap-1 text-lg font-black" :class="card.badgeTone">
            {{ card.badge }}
            <span class="material-symbols-outlined text-[18px]">trending_up</span>
          </span>
        </div>
        <p class="mt-7 text-xl font-semibold text-slate-500 dark:text-slate-400">{{ card.label }}</p>
        <h2 class="mt-2 text-4xl font-black tracking-tight text-slate-950 dark:text-white">
          {{ loading ? '...' : card.value }}
        </h2>
        <p class="mt-3 text-sm font-medium text-slate-500 dark:text-slate-400">{{ card.helper }}</p>
      </article>
    </div>

    <div class="grid gap-6 xl:grid-cols-[minmax(0,2fr)_minmax(360px,0.95fr)]">
      <section class="rounded-[18px] border border-slate-200 bg-white p-7 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h2 class="text-2xl font-black text-slate-950 dark:text-white">Tăng trưởng người dùng</h2>
            <p class="mt-2 text-lg text-slate-500 dark:text-slate-400">Thống kê 6 tháng gần nhất từ dữ liệu đăng ký.</p>
          </div>
          <span class="rounded-2xl bg-slate-50 px-5 py-3 text-base font-bold text-slate-700 dark:bg-slate-800 dark:text-slate-200">
            {{ new Date().getFullYear() }}
          </span>
        </div>

        <div class="mt-8 flex h-[340px] items-end gap-4 overflow-x-auto pb-2">
          <div v-for="bar in chartBars" :key="bar.key" class="flex h-full min-w-20 flex-1 flex-col items-center justify-end gap-3">
            <p class="text-sm font-black text-slate-950 dark:text-white">{{ formatNumber(bar.value) }}</p>
            <div class="flex h-[260px] w-full items-end rounded-2xl bg-slate-50 px-3 py-3 dark:bg-slate-950">
              <div
                class="w-full rounded-xl bg-[#f45112] shadow-[0_18px_34px_rgba(244,81,18,0.18)] transition-all"
                :style="{ height: `${bar.height}%` }"
              ></div>
            </div>
            <p class="text-sm font-bold text-slate-500 dark:text-slate-400">{{ bar.label }}</p>
          </div>
        </div>
      </section>

      <section class="rounded-[18px] border border-slate-200 bg-white p-7 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <h2 class="text-2xl font-black text-slate-950 dark:text-white">Hoạt động gần đây</h2>
        <div class="mt-8 space-y-7">
          <article v-for="activity in recentActivities" :key="activity.id" class="flex gap-5">
            <span class="mt-2 size-3 shrink-0 rounded-full" :class="activity.dot"></span>
            <div>
              <h3 class="text-lg font-black text-slate-950 dark:text-white">{{ activity.title }}</h3>
              <p class="mt-1 text-base text-slate-500 dark:text-slate-400">{{ activity.description }}</p>
            </div>
          </article>
          <p v-if="!recentActivities.length && !loading" class="rounded-2xl bg-slate-50 p-5 text-sm text-slate-500 dark:bg-slate-950 dark:text-slate-400">
            Chưa có hoạt động gần đây phù hợp với quyền hiện tại.
          </p>
        </div>
        <RouterLink
          v-if="canViewBilling || canViewUsers"
          :to="canViewBilling ? '/admin/billing' : '/admin/users'"
          class="mt-10 inline-flex w-full justify-center text-lg font-black text-[#f45112] hover:underline"
        >
          Xem tất cả hoạt động
        </RouterLink>
      </section>
    </div>

    <section v-if="canViewUsers" class="overflow-hidden rounded-[18px] border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="flex items-center justify-between gap-4 p-7">
        <div>
          <h2 class="text-2xl font-black text-slate-950 dark:text-white">Danh sách người dùng mới</h2>
          <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">Các tài khoản được tạo gần đây nhất trong hệ thống.</p>
        </div>
        <RouterLink to="/admin/users" class="text-base font-semibold text-slate-500 transition hover:text-[#2463eb] dark:text-slate-400">
          Xem toàn bộ
        </RouterLink>
      </div>

      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-slate-200 text-sm dark:divide-slate-800">
          <thead class="bg-slate-50 text-left text-xs font-black uppercase tracking-[0.18em] text-slate-500 dark:bg-slate-950 dark:text-slate-400">
            <tr>
              <th class="px-7 py-4">Người dùng</th>
              <th class="px-7 py-4">Vai trò</th>
              <th class="px-7 py-4">Ngày đăng ký</th>
              <th class="px-7 py-4">Trạng thái</th>
              <th class="px-7 py-4 text-right">Hành động</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 dark:divide-slate-800">
            <tr v-for="user in recentUsers.slice(0, 6)" :key="user.id" class="hover:bg-slate-50 dark:hover:bg-slate-950/60">
              <td class="px-7 py-5">
                <p class="font-black text-slate-950 dark:text-white">{{ user.ho_ten || 'Người dùng chưa cập nhật' }}</p>
                <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">{{ user.email }}</p>
              </td>
              <td class="px-7 py-5 text-slate-600 dark:text-slate-300">{{ roleLabel(user.vai_tro) }}</td>
              <td class="px-7 py-5 text-slate-600 dark:text-slate-300">{{ formatDate(user.created_at) }}</td>
              <td class="px-7 py-5">
                <span
                  class="inline-flex rounded-full px-3 py-1 text-xs font-bold"
                  :class="Number(user.trang_thai) === 1 ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-300' : 'bg-rose-50 text-rose-700 dark:bg-rose-500/10 dark:text-rose-300'"
                >
                  {{ statusLabel(user.trang_thai) }}
                </span>
              </td>
              <td class="px-7 py-5 text-right">
                <RouterLink to="/admin/users" class="font-bold text-[#2463eb] hover:underline">Xem</RouterLink>
              </td>
            </tr>
            <tr v-if="!recentUsers.length && !loading">
              <td colspan="5" class="px-7 py-10 text-center text-slate-500 dark:text-slate-400">Chưa có người dùng mới để hiển thị.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section
      v-if="!kpiCards.length"
      class="rounded-xl border border-dashed border-slate-200 bg-white p-8 text-center text-slate-500 shadow-sm dark:border-slate-800 dark:bg-slate-900 dark:text-slate-400"
    >
      Tài khoản admin này chưa được cấp quyền xem dữ liệu dashboard. Vui lòng liên hệ Super Admin để được cấp quyền module phù hợp.
    </section>
  </div>
</template>
