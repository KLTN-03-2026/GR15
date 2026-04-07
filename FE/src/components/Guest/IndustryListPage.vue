<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { jobService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'

const route = useRoute()
const router = useRouter()
const notify = useNotify()

const loading = ref(false)
const industries = ref([])
const totalIndustries = ref(0)
const filters = ref({
  search: route.query.search || '',
  parentId: route.query.parent_id || '',
  page: Number(route.query.page || 1),
  perPage: Number(route.query.per_page || 9),
})

const extractList = (response) => {
  const payload = response?.data
  if (Array.isArray(payload?.data)) return payload.data
  if (Array.isArray(payload)) return payload
  return []
}

const parentOptions = computed(() => industries.value.filter((item) => !item.danh_muc_cha_id))
const totalPages = computed(() => Math.max(1, Math.ceil(totalIndustries.value / filters.value.perPage)))

const syncRoute = () => {
  router.replace({
    path: '/industries',
    query: {
      ...(filters.value.search ? { search: filters.value.search } : {}),
      ...(filters.value.parentId ? { parent_id: filters.value.parentId } : {}),
      ...(filters.value.page > 1 ? { page: filters.value.page } : {}),
      per_page: filters.value.perPage,
    },
  })
}

const loadIndustries = async () => {
  loading.value = true
  try {
    const response = await jobService.getIndustries({
      search: filters.value.search.trim() || undefined,
      danh_muc_cha_id: filters.value.parentId || undefined,
      per_page: filters.value.perPage,
    })

    const list = extractList(response)
    industries.value = list
    totalIndustries.value = Number(response?.data?.total || list.length || 0)
  } catch (error) {
    industries.value = []
    totalIndustries.value = 0
    notify.apiError(error, 'Không thể tải danh sách ngành nghề.')
  } finally {
    loading.value = false
  }
}

const applyFilters = () => {
  filters.value.page = 1
  syncRoute()
  loadIndustries()
}

watch(
  () => route.query,
  (query) => {
    filters.value.search = query.search || ''
    filters.value.parentId = query.parent_id || ''
    filters.value.page = Number(query.page || 1)
    filters.value.perPage = Number(query.per_page || 9)
  },
)

onMounted(loadIndustries)
</script>

<template>
  <section class="py-14 lg:py-16">
    <div class="mx-auto max-w-7xl px-6">
      <div class="rounded-[32px] border border-slate-200 bg-gradient-to-r from-white via-blue-50 to-indigo-100 p-8 shadow-xl dark:border-slate-800 dark:from-slate-900 dark:via-slate-900 dark:to-slate-800">
        <p class="text-sm font-bold uppercase tracking-[0.35em] text-[#2463eb]">Industry Directory</p>
        <h1 class="mt-4 text-4xl font-black tracking-tight text-slate-900 dark:text-white">
          Khám phá toàn bộ ngành nghề
        </h1>
        <p class="mt-4 max-w-3xl text-base leading-8 text-slate-600 dark:text-slate-400">
          Đi từ danh mục tổng để tìm đúng nhóm ngành bạn quan tâm, sau đó mở chi tiết ngành và các việc làm liên quan.
        </p>
      </div>

      <div class="mt-8 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div class="grid gap-4 lg:grid-cols-[1fr_260px_220px_180px]">
          <div class="rounded-2xl bg-slate-50 px-4 dark:bg-slate-950">
            <label class="block pt-3 text-xs font-bold uppercase tracking-[0.3em] text-slate-400">Tìm ngành nghề</label>
            <input
              v-model="filters.search"
              type="text"
              class="w-full border-none bg-transparent py-3 text-slate-900 shadow-none outline-none ring-0 placeholder:text-slate-400 focus:ring-0 dark:text-white"
              placeholder="Tên ngành, mô tả..."
              @keyup.enter="applyFilters"
            />
          </div>

          <label class="rounded-2xl bg-slate-50 px-4 dark:bg-slate-950">
            <span class="block pt-3 text-xs font-bold uppercase tracking-[0.3em] text-slate-400">Danh mục cha</span>
            <select
              v-model="filters.parentId"
              class="w-full border-none bg-transparent py-3 text-slate-900 outline-none ring-0 focus:ring-0 dark:text-white"
              @change="applyFilters"
            >
              <option value="">Tất cả ngành nghề</option>
              <option
                v-for="item in parentOptions"
                :key="item.id"
                :value="item.id"
              >
                {{ item.ten_nganh }}
              </option>
            </select>
          </label>

          <label class="rounded-2xl bg-slate-50 px-4 dark:bg-slate-950">
            <span class="block pt-3 text-xs font-bold uppercase tracking-[0.3em] text-slate-400">Số dòng / trang</span>
            <select
              v-model="filters.perPage"
              class="w-full border-none bg-transparent py-3 text-slate-900 outline-none ring-0 focus:ring-0 dark:text-white"
              @change="applyFilters"
            >
              <option :value="9">9</option>
              <option :value="12">12</option>
              <option :value="18">18</option>
            </select>
          </label>

          <button
            type="button"
            class="rounded-2xl bg-[#2463eb] px-6 py-4 text-sm font-bold text-white transition hover:bg-blue-700"
            @click="applyFilters"
          >
            Áp dụng
          </button>
        </div>
      </div>

      <div class="mt-6 flex items-center justify-between text-sm text-slate-500 dark:text-slate-400">
        <p>{{ totalIndustries }} ngành nghề đang hiển thị</p>
        <RouterLink to="/" class="font-semibold text-[#2463eb] hover:underline">Quay lại trang chủ</RouterLink>
      </div>

      <div v-if="loading" class="mt-8 grid gap-6 sm:grid-cols-2 xl:grid-cols-3">
        <div
          v-for="index in filters.perPage"
          :key="index"
          class="h-64 animate-pulse rounded-3xl bg-slate-200/70 dark:bg-slate-800/70"
        ></div>
      </div>

      <div v-else-if="industries.length" class="mt-8 grid gap-6 sm:grid-cols-2 xl:grid-cols-3">
        <div
          v-for="industry in industries"
          :key="industry.id"
          class="group flex h-full flex-col rounded-3xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:border-[#2463eb]/40 hover:shadow-xl dark:border-slate-800 dark:bg-slate-900"
        >
          <div class="flex items-start justify-between gap-4">
            <div class="flex h-16 w-16 items-center justify-center rounded-2xl bg-[#2463eb]/10 text-xl font-black text-[#2463eb]">
              {{ (industry.ten_nganh || 'N').slice(0, 1) }}
            </div>
            <span class="rounded-full bg-slate-100 px-3 py-1.5 text-xs font-bold text-slate-600 dark:bg-slate-800 dark:text-slate-300">
              {{ industry.danh_muc_cha_id ? 'Ngành con' : 'Ngành gốc' }}
            </span>
          </div>

          <div class="mt-5">
            <h2 class="text-lg font-bold text-slate-900 group-hover:text-[#2463eb] dark:text-white">
              {{ industry.ten_nganh }}
            </h2>
            <p class="mt-2 text-sm text-slate-500">
              {{ industry.danh_muc_cha_id ? 'Thuộc nhóm ngành cấp trên' : 'Danh mục chính' }}
            </p>
          </div>

          <p class="mt-5 line-clamp-4 flex-1 text-sm leading-7 text-slate-600 dark:text-slate-400">
            {{ industry.mo_ta || 'Ngành nghề này đang được cập nhật thêm mô tả chi tiết và bối cảnh tuyển dụng.' }}
          </p>

          <div class="mt-5 flex items-center justify-between gap-3">
            <RouterLink
              :to="{ path: '/jobs', query: { nganh_nghe_id: industry.id } }"
              class="rounded-xl border border-slate-200 px-4 py-2 text-sm font-bold text-slate-700 transition hover:border-[#2463eb] hover:text-[#2463eb] dark:border-slate-700 dark:text-slate-200"
            >
              Xem việc
            </RouterLink>
            <RouterLink
              :to="`/industries/${industry.id}`"
              class="shrink-0 rounded-xl bg-slate-900 px-4 py-2 text-sm font-bold text-white transition hover:bg-[#2463eb] dark:bg-white dark:text-slate-900 dark:hover:bg-[#2463eb] dark:hover:text-white"
            >
              Chi tiết
            </RouterLink>
          </div>
        </div>
      </div>

      <div v-else class="mt-8 rounded-3xl border border-dashed border-slate-300 p-12 text-center dark:border-slate-700">
        <p class="text-lg font-semibold text-slate-700 dark:text-slate-300">Chưa tìm thấy ngành nghề phù hợp.</p>
      </div>
    </div>
  </section>
</template>
