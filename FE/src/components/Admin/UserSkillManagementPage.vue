<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { adminSkillService, adminUserSkillService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'

const notify = useNotify()

const loading = ref(false)
const detailLoading = ref(false)
const error = ref('')

const rawRecords = ref([])
const skillOptions = ref([])
const selectedUser = ref(null)
const userSkills = ref([])
const showDetailModal = ref(false)

const searchQuery = ref('')
const selectedSkillId = ref('')
const selectedLevel = ref('')

const stats = reactive({
  totalRecords: 0,
  totalUsers: 0,
  topSkill: '',
  levelBreakdown: {},
})

const levelOptions = [
  { value: '', label: 'Tất cả mức độ' },
  { value: '1', label: 'Cơ bản' },
  { value: '2', label: 'Trung bình' },
  { value: '3', label: 'Khá' },
  { value: '4', label: 'Giỏi' },
  { value: '5', label: 'Chuyên gia' },
]

const levelLabel = (value) => {
  return levelOptions.find((item) => item.value === String(value))?.label || `Mức ${value}`
}

const statCards = computed(() => [
  {
    label: 'Bản ghi kỹ năng',
    value: stats.totalRecords,
    description: 'Tổng số bản ghi người dùng đang khai báo.',
    icon: 'bolt',
    iconClass: 'bg-[#2463eb]/10 text-[#2463eb]',
  },
  {
    label: 'Người dùng có kỹ năng',
    value: stats.totalUsers,
    description: 'Số tài khoản đã thêm ít nhất một kỹ năng.',
    icon: 'group',
    iconClass: 'bg-emerald-500/10 text-emerald-500',
  },
  {
    label: 'Kỹ năng nổi bật',
    value: stats.topSkill || 'Chưa có',
    description: 'Kỹ năng được nhiều người khai báo nhất.',
    icon: 'workspace_premium',
    iconClass: 'bg-amber-500/10 text-amber-500',
  },
  {
    label: 'Mức phổ biến nhất',
    value: levelLabel(
      Object.entries(stats.levelBreakdown).sort((a, b) => Number(b[1]) - Number(a[1]))[0]?.[0] || ''
    ),
    description: 'Phân nhóm kỹ năng được dùng nhiều nhất.',
    icon: 'stacked_bar_chart',
    iconClass: 'bg-rose-500/10 text-rose-500',
  },
])

const groupedUsers = computed(() => {
  const map = new Map()

  rawRecords.value.forEach((record) => {
    const userId = record.nguoi_dung?.id || record.nguoi_dung_id
    if (!userId) return

    const existing = map.get(userId) || {
      id: userId,
      name: record.nguoi_dung?.ho_ten || 'Người dùng chưa cập nhật',
      email: record.nguoi_dung?.email || 'Chưa có email',
      skillCount: 0,
      totalLevel: 0,
      years: 0,
      skills: [],
    }

    existing.skillCount += 1
    existing.totalLevel += Number(record.muc_do || 0)
    existing.years += Number(record.nam_kinh_nghiem || 0)
    existing.skills.push({
      id: record.id,
      name: record.ky_nang?.ten_ky_nang || 'Kỹ năng',
      level: Number(record.muc_do || 0),
      years: Number(record.nam_kinh_nghiem || 0),
      certificates: Number(record.so_chung_chi || 0),
    })

    map.set(userId, existing)
  })

  return Array.from(map.values())
    .map((user) => ({
      ...user,
      avgLevel: user.skillCount ? (user.totalLevel / user.skillCount).toFixed(1) : '0.0',
      topSkills: user.skills
        .sort((a, b) => b.level - a.level)
        .slice(0, 4),
    }))
    .filter((user) => {
      if (!searchQuery.value) return true
      const query = searchQuery.value.toLowerCase()
      return (
        user.name.toLowerCase().includes(query) ||
        user.email.toLowerCase().includes(query) ||
        user.skills.some((skill) => skill.name.toLowerCase().includes(query))
      )
    })
})

const loadStats = async () => {
  const response = await adminUserSkillService.getStats()
  const payload = response?.data || {}

  stats.totalRecords = payload.tong_ban_ghi || 0
  stats.totalUsers = payload.so_nguoi_co_ky_nang || 0
  stats.levelBreakdown = {
    1: payload.theo_muc_do?.co_ban || 0,
    2: payload.theo_muc_do?.trung_binh || 0,
    3: payload.theo_muc_do?.kha || 0,
    4: payload.theo_muc_do?.gioi || 0,
    5: payload.theo_muc_do?.chuyen_gia || 0,
  }
  stats.topSkill = payload.top_ky_nang?.[0]?.ky_nang?.ten_ky_nang || ''
}

const loadSkillOptions = async () => {
  const response = await adminSkillService.getSkills({ per_page: 100, sort_by: 'ten_ky_nang', sort_dir: 'asc' })
  skillOptions.value = response?.data?.data || []
}

const loadUserSkills = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await adminUserSkillService.getUserSkills({
      per_page: 100,
      ky_nang_id: selectedSkillId.value || undefined,
      muc_do: selectedLevel.value || undefined,
    })

    const payload = response?.data
    rawRecords.value = Array.isArray(payload) ? payload : payload?.data || []
  } catch (err) {
    rawRecords.value = []
    error.value = err.message || 'Không thể tải kỹ năng người dùng.'
  } finally {
    loading.value = false
  }
}

const refreshAll = async () => {
  await Promise.all([loadStats(), loadSkillOptions(), loadUserSkills()])
}

const onFilterChange = async () => {
  await loadUserSkills()
}

const openDetail = async (user) => {
  detailLoading.value = true
  showDetailModal.value = true
  selectedUser.value = user
  userSkills.value = []

  try {
    const response = await adminUserSkillService.getSkillsByUserId(user.id)
    userSkills.value = response?.data || []
  } catch (err) {
    notify.apiError(err, 'Không tải được chi tiết kỹ năng người dùng.')
    showDetailModal.value = false
  } finally {
    detailLoading.value = false
  }
}

onMounted(async () => {
  await refreshAll()
})
</script>

<template>
  <div v-if="error" class="mb-6 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-900 dark:bg-red-900/20 dark:text-red-300">
    {{ error }}
  </div>

  <div class="mb-8">
    <h1 class="text-3xl font-extrabold tracking-tight">Quản lý kỹ năng người dùng</h1>
    <p class="mt-2 max-w-3xl text-base text-slate-500 dark:text-slate-400">
      Theo dõi kỹ năng ứng viên đang khai báo, mức độ thành thạo và rà soát nhanh theo từng tài khoản.
    </p>
  </div>

  <div class="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-4">
    <div
      v-for="card in statCards"
      :key="card.label"
      class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900"
    >
      <div class="mb-2 flex items-center justify-between gap-3">
        <p class="text-sm font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">{{ card.label }}</p>
        <span class="material-symbols-outlined rounded-lg p-2" :class="card.iconClass">{{ card.icon }}</span>
      </div>
      <p class="text-3xl font-bold break-words">{{ card.value }}</p>
      <p class="mt-2 text-xs text-slate-400">{{ card.description }}</p>
    </div>
  </div>

  <div class="rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
    <div class="grid grid-cols-1 gap-4 border-b border-slate-200 px-6 py-5 dark:border-slate-800 xl:grid-cols-[minmax(0,1.5fr)_280px_220px]">
      <label class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 dark:border-slate-700 dark:bg-slate-800">
        <span class="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-400">Tìm người dùng / kỹ năng</span>
        <input
          v-model="searchQuery"
          type="text"
          class="w-full bg-transparent text-sm text-slate-700 outline-none dark:text-slate-200"
          placeholder="Tên người dùng, email hoặc kỹ năng..."
        >
      </label>

      <label class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 dark:border-slate-700 dark:bg-slate-800">
        <span class="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-400">Kỹ năng</span>
        <select
          v-model="selectedSkillId"
          class="w-full bg-transparent text-sm text-slate-700 outline-none dark:text-slate-200"
          @change="onFilterChange"
        >
          <option value="">Tất cả kỹ năng</option>
          <option v-for="skill in skillOptions" :key="skill.id" :value="skill.id">{{ skill.ten_ky_nang }}</option>
        </select>
      </label>

      <label class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 dark:border-slate-700 dark:bg-slate-800">
        <span class="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-400">Mức độ</span>
        <select
          v-model="selectedLevel"
          class="w-full bg-transparent text-sm text-slate-700 outline-none dark:text-slate-200"
          @change="onFilterChange"
        >
          <option v-for="option in levelOptions" :key="option.label" :value="option.value">{{ option.label }}</option>
        </select>
      </label>
    </div>

    <div v-if="loading" class="space-y-4 px-6 py-6">
      <div v-for="index in 4" :key="index" class="h-28 animate-pulse rounded-2xl bg-slate-100 dark:bg-slate-800" />
    </div>

    <div v-else-if="!groupedUsers.length" class="px-6 py-16 text-center">
      <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-slate-100 dark:bg-slate-800">
        <span class="material-symbols-outlined text-3xl text-slate-500">bolt</span>
      </div>
      <h2 class="mt-5 text-xl font-bold text-slate-900 dark:text-white">Chưa có dữ liệu kỹ năng phù hợp</h2>
      <p class="mx-auto mt-3 max-w-xl text-sm leading-7 text-slate-500 dark:text-slate-400">
        Hãy thay đổi bộ lọc hoặc chờ người dùng cập nhật thêm kỹ năng trong hồ sơ của họ.
      </p>
    </div>

    <div v-else class="divide-y divide-slate-100 dark:divide-slate-800">
      <div
        v-for="user in groupedUsers"
        :key="user.id"
        class="grid grid-cols-1 gap-4 px-6 py-5 xl:grid-cols-[minmax(0,1.55fr)_230px_230px_auto]"
      >
        <div class="min-w-0">
          <div class="flex flex-wrap items-center gap-3">
            <h3 class="text-lg font-bold text-slate-900 dark:text-white">{{ user.name }}</h3>
            <span class="inline-flex items-center gap-1 rounded-full bg-[#2463eb]/10 px-2.5 py-1 text-xs font-bold text-[#2463eb]">
              {{ user.skillCount }} kỹ năng
            </span>
          </div>
          <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">{{ user.email }}</p>
          <div class="mt-3 flex flex-wrap gap-2">
            <span
              v-for="skill in user.topSkills"
              :key="skill.id"
              class="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-semibold text-slate-600 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300"
            >
              {{ skill.name }}
              <span class="rounded-full bg-slate-200 px-1.5 py-0.5 text-[10px] dark:bg-slate-700">{{ levelLabel(skill.level) }}</span>
            </span>
          </div>
        </div>

        <div class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 dark:border-slate-700 dark:bg-slate-800">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Tổng quan</p>
          <div class="mt-3 space-y-2 text-sm text-slate-600 dark:text-slate-300">
            <p>Mức trung bình: <strong class="text-slate-900 dark:text-white">{{ user.avgLevel }}</strong></p>
            <p>Kinh nghiệm cộng dồn: <strong class="text-slate-900 dark:text-white">{{ user.years.toFixed(1) }} năm</strong></p>
          </div>
        </div>

        <div class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 dark:border-slate-700 dark:bg-slate-800">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Mức nổi bật</p>
          <p class="mt-3 text-sm font-semibold text-slate-900 dark:text-white">
            {{ levelLabel(user.topSkills[0]?.level || '') }}
          </p>
        </div>

        <div class="flex items-center justify-start xl:justify-end">
          <button
            class="inline-flex items-center gap-2 rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
            type="button"
            @click="openDetail(user)"
          >
            <span class="material-symbols-outlined text-[18px]">visibility</span>
            Chi tiết kỹ năng
          </button>
        </div>
      </div>
    </div>
  </div>

  <div
    v-if="showDetailModal"
    class="fixed inset-0 z-50 overflow-y-auto bg-slate-950/55 backdrop-blur-sm"
    @click.self="showDetailModal = false"
  >
    <div class="flex min-h-full items-center justify-center px-4 py-6">
      <div class="flex max-h-[calc(100vh-3rem)] w-full max-w-4xl flex-col overflow-hidden rounded-[28px] border border-slate-200 bg-white shadow-2xl dark:border-slate-700 dark:bg-slate-900">
      <div class="flex items-start justify-between border-b border-slate-100 px-6 py-5 dark:border-slate-800">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.28em] text-blue-500">Kỹ năng người dùng</p>
          <h3 class="mt-2 text-2xl font-bold text-slate-900 dark:text-white">{{ selectedUser?.name }}</h3>
          <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">{{ selectedUser?.email }}</p>
        </div>
        <button
          class="rounded-full p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-800"
          type="button"
          @click="showDetailModal = false"
        >
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>

      <div v-if="detailLoading" class="flex-1 space-y-4 overflow-y-auto px-6 py-6">
        <div v-for="index in 4" :key="index" class="h-20 animate-pulse rounded-2xl bg-slate-100 dark:bg-slate-800" />
      </div>

      <div v-else class="flex-1 overflow-y-auto px-6 py-6">
        <div v-if="!userSkills.length" class="rounded-2xl border border-dashed border-slate-200 px-5 py-10 text-center text-sm text-slate-500 dark:border-slate-700 dark:text-slate-400">
          Người dùng này chưa có kỹ năng nào được khai báo.
        </div>

        <div v-else class="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div
            v-for="skill in userSkills"
            :key="skill.id"
            class="rounded-2xl border border-slate-200 bg-slate-50 px-5 py-4 dark:border-slate-700 dark:bg-slate-800"
          >
            <div class="flex items-center justify-between gap-3">
              <h4 class="text-base font-bold text-slate-900 dark:text-white">{{ skill.ky_nang?.ten_ky_nang || 'Kỹ năng' }}</h4>
              <span class="rounded-full bg-[#2463eb]/10 px-2.5 py-1 text-xs font-bold text-[#2463eb]">{{ levelLabel(skill.muc_do) }}</span>
            </div>
            <div class="mt-4 grid grid-cols-2 gap-3 text-sm text-slate-600 dark:text-slate-300">
              <div>
                <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Kinh nghiệm</p>
                <p class="mt-1 font-semibold text-slate-900 dark:text-white">{{ Number(skill.nam_kinh_nghiem || 0).toFixed(1) }} năm</p>
              </div>
              <div>
                <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Chứng chỉ</p>
                <p class="mt-1 font-semibold text-slate-900 dark:text-white">{{ skill.so_chung_chi || 0 }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    </div>
  </div>
</template>
