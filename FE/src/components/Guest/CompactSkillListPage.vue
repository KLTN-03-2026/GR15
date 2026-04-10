<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { jobService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'

const route = useRoute()
const router = useRouter()
const notify = useNotify()

const loading = ref(false)
const skills = ref([])
const totalSkills = ref(0)
const filters = ref({
  search: route.query.search || '',
  page: Number(route.query.page || 1),
  perPage: Number(route.query.per_page || 12),
})

const extractList = (response) => {
  const payload = response?.data
  if (Array.isArray(payload?.data)) return payload.data
  if (Array.isArray(payload)) return payload
  return []
}

const totalPages = computed(() => Math.max(1, Math.ceil(totalSkills.value / filters.value.perPage)))

const syncRoute = () => {
  router.replace({
    path: '/skills',
    query: {
      ...(filters.value.search ? { search: filters.value.search } : {}),
      ...(filters.value.page > 1 ? { page: filters.value.page } : {}),
      per_page: filters.value.perPage,
    },
  })
}

const loadSkills = async () => {
  loading.value = true
  try {
    const response = await jobService.getSkills({
      search: filters.value.search.trim() || undefined,
      per_page: filters.value.perPage,
    })

    const list = extractList(response)
    skills.value = list
    totalSkills.value = Number(response?.data?.total || list.length || 0)
  } catch (error) {
    skills.value = []
    totalSkills.value = 0
    notify.apiError(error, 'Khong the tai danh sach ky nang.')
  } finally {
    loading.value = false
  }
}

const applyFilters = () => {
  filters.value.page = 1
  syncRoute()
  loadSkills()
}

watch(
  () => route.query,
  (query) => {
    filters.value.search = query.search || ''
    filters.value.page = Number(query.page || 1)
    filters.value.perPage = Number(query.per_page || 12)
  },
)

onMounted(loadSkills)
</script>

<template>
  <section class="py-14 lg:py-16">
    <div class="mx-auto max-w-7xl px-6">
      <div class="rounded-[32px] border border-slate-200 bg-gradient-to-r from-white via-blue-50 to-indigo-100 p-8 shadow-xl">
        <p class="text-sm font-bold uppercase tracking-[0.35em] text-[#2463eb]">Skill Directory</p>
        <h1 class="mt-4 text-4xl font-black tracking-tight text-slate-900">Danh sach ky nang</h1>
        <p class="mt-4 max-w-3xl text-base leading-8 text-slate-600">
          Chi giu lai phan duyet, tim kiem va xem chi tiet ky nang de tap trung vao luong cot loi.
        </p>
      </div>

      <div class="mt-8 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="grid gap-4 lg:grid-cols-[1fr_220px_180px]">
          <div class="rounded-2xl bg-slate-50 px-4">
            <label class="block pt-3 text-xs font-bold uppercase tracking-[0.3em] text-slate-400">Tim ky nang</label>
            <input
              v-model="filters.search"
              type="text"
              class="w-full border-none bg-transparent py-3 text-slate-900 shadow-none outline-none ring-0 placeholder:text-slate-400 focus:ring-0"
              placeholder="Ten ky nang..."
              @keyup.enter="applyFilters"
            />
          </div>

          <label class="rounded-2xl bg-slate-50 px-4">
            <span class="block pt-3 text-xs font-bold uppercase tracking-[0.3em] text-slate-400">So dong / trang</span>
            <select
              v-model="filters.perPage"
              class="w-full border-none bg-transparent py-3 text-slate-900 outline-none ring-0 focus:ring-0"
              @change="applyFilters"
            >
              <option :value="12">12</option>
              <option :value="18">18</option>
              <option :value="24">24</option>
            </select>
          </label>

          <button
            type="button"
            class="rounded-2xl bg-[#2463eb] px-6 py-4 text-sm font-bold text-white transition hover:bg-blue-700"
            @click="applyFilters"
          >
            Ap dung
          </button>
        </div>
      </div>

      <div class="mt-6 flex items-center justify-between text-sm text-slate-500">
        <p>{{ totalSkills }} ky nang dang hien thi</p>
        <RouterLink to="/register" class="font-semibold text-[#2463eb] hover:underline">Dang ky tai khoan</RouterLink>
      </div>

      <div v-if="loading" class="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <div
          v-for="index in filters.perPage"
          :key="index"
          class="h-40 animate-pulse rounded-3xl bg-slate-200/70"
        ></div>
      </div>

      <div v-else-if="skills.length" class="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <div
          v-for="skill in skills"
          :key="skill.id"
          class="group flex h-full flex-col rounded-3xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:border-[#2463eb]/40 hover:shadow-xl"
        >
          <div class="flex items-center justify-between gap-4">
            <h2 class="text-lg font-bold text-slate-900 group-hover:text-[#2463eb]">
              {{ skill.ten_ky_nang || skill.ten }}
            </h2>
            <span class="rounded-full bg-blue-50 px-3 py-1 text-xs font-bold text-[#2463eb]">Skill</span>
          </div>

          <p class="mt-4 flex-1 text-sm leading-7 text-slate-600">
            {{ skill.mo_ta || 'Ky nang nay dang duoc cap nhat them mo ta va boi canh su dung.' }}
          </p>

          <div class="mt-5">
            <RouterLink
              :to="`/skills/${skill.id}`"
              class="inline-flex rounded-xl bg-slate-900 px-4 py-2 text-sm font-bold text-white transition hover:bg-[#2463eb]"
            >
              Chi tiet
            </RouterLink>
          </div>
        </div>
      </div>

      <div v-else class="mt-8 rounded-3xl border border-dashed border-slate-300 p-12 text-center">
        <p class="text-lg font-semibold text-slate-700">Chua tim thay ky nang phu hop.</p>
      </div>

      <div v-if="!loading && totalPages > 1" class="mt-8 flex items-center justify-center gap-2">
        <button
          type="button"
          class="rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-600 disabled:opacity-50"
          :disabled="filters.page <= 1"
          @click="filters.page -= 1; syncRoute(); loadSkills()"
        >
          Truoc
        </button>
        <span class="rounded-xl bg-slate-100 px-4 py-2 text-sm font-semibold text-slate-700">
          {{ filters.page }} / {{ totalPages }}
        </span>
        <button
          type="button"
          class="rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-600 disabled:opacity-50"
          :disabled="filters.page >= totalPages"
          @click="filters.page += 1; syncRoute(); loadSkills()"
        >
          Sau
        </button>
      </div>
    </div>
  </section>
</template>
