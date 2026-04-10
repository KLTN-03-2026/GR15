<template>
  <div
    class="relative isolate min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(37,99,235,0.10),_transparent_30%),linear-gradient(180deg,#f8fbff_0%,#eef4ff_45%,#f8fafc_100%)]"
  >
    <section class="py-14 lg:py-16">
      <div class="mx-auto max-w-7xl px-6">

        <!-- Hero banner -->
        <div
          class="rounded-[32px] border border-slate-200 bg-gradient-to-r from-white via-blue-50 to-indigo-100 p-8 shadow-xl"
        >
          <p class="text-sm font-bold uppercase tracking-[0.35em] text-[#2463eb]">Industry Directory</p>
          <h1 class="mt-4 text-4xl font-black tracking-tight text-slate-900">
            Khám phá toàn bộ ngành nghề
          </h1>
          <p class="mt-4 max-w-3xl text-base leading-8 text-slate-600">
            Tìm kiếm ngành nghề phù hợp với định hướng nghề nghiệp của bạn. Mỗi ngành nghề đều kết nối
            tới danh sách việc làm đang tuyển dụng trực tiếp.
          </p>
        </div>

        <!-- Filter bar -->
        <div class="mt-8 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <div class="grid gap-4 lg:grid-cols-[1fr_260px_220px_auto]">
            <!-- Search input -->
            <div class="rounded-2xl bg-slate-50 px-4">
              <label
                for="industry-search"
                class="block pt-3 text-xs font-bold uppercase tracking-[0.3em] text-slate-400"
              >
                Tìm ngành nghề
              </label>
              <input
                id="industry-search"
                v-model="filters.search"
                type="text"
                placeholder="Tên ngành, mô tả..."
                class="w-full border-none bg-transparent py-3 text-sm text-slate-900 outline-none"
                @keyup.enter="applyFilters"
              />
            </div>

            <!-- Parent category filter -->
            <label class="rounded-2xl bg-slate-50 px-4">
              <span class="block pt-3 text-xs font-bold uppercase tracking-[0.3em] text-slate-400">
                Danh mục cha
              </span>
              <select
                id="industry-parent"
                v-model="filters.parentId"
                class="w-full border-none bg-transparent py-3 text-sm text-slate-700 outline-none"
                @change="applyFilters"
              >
                <option value="">Tất cả ngành nghề</option>
                <option v-for="item in parentOptions" :key="item.id" :value="item.id">
                  {{ item.ten_nganh }}
                </option>
              </select>
            </label>

            <!-- Per page -->
            <label class="rounded-2xl bg-slate-50 px-4">
              <span class="block pt-3 text-xs font-bold uppercase tracking-[0.3em] text-slate-400">
                Số dòng / trang
              </span>
              <select
                id="industry-perpage"
                v-model="filters.perPage"
                class="w-full border-none bg-transparent py-3 text-sm text-slate-700 outline-none"
                @change="applyFilters"
              >
                <option :value="9">9</option>
                <option :value="12">12</option>
                <option :value="18">18</option>
                <option :value="0">Tất cả</option>
              </select>
            </label>

            <!-- Apply button -->
            <button
              type="button"
              class="self-end rounded-2xl bg-[#2463eb] px-6 py-4 text-sm font-bold text-white transition hover:bg-blue-700"
              @click="applyFilters"
            >
              Áp dụng
            </button>
          </div>
        </div>

        <!-- Stats bar -->
        <div class="mt-6 flex flex-wrap items-center justify-between gap-3 text-sm text-slate-500">
          <p>
            <span class="font-bold text-slate-900">{{ totalIndustries }}</span>
            ngành nghề đang hiển thị
          </p>
          <RouterLink
            to="/"
            class="font-semibold text-[#2463eb] hover:text-blue-800 hover:underline"
          >
            Quay lại trang chủ
          </RouterLink>
        </div>

        <!-- Loading skeleton -->
        <div v-if="loading" class="mt-8 grid gap-6 sm:grid-cols-2 xl:grid-cols-3">
          <div
            v-for="i in filters.perPage || 9"
            :key="i"
            class="h-64 animate-pulse rounded-3xl bg-slate-200/70"
          ></div>
        </div>

        <!-- Industry grid -->
        <div v-else-if="industries.length" class="mt-8 grid gap-6 sm:grid-cols-2 xl:grid-cols-3">
          <div
            v-for="industry in industries"
            :key="industry.id"
            class="group flex h-full flex-col rounded-3xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:border-[#2463eb]/40 hover:shadow-xl"
          >
            <!-- Card header -->
            <div class="flex items-start justify-between gap-4">
              <div
                class="flex h-16 w-16 flex-shrink-0 items-center justify-center rounded-2xl bg-[#2463eb]/10 text-2xl font-black text-[#2463eb]"
              >
                {{ (industry.ten_nganh || 'N').slice(0, 1).toUpperCase() }}
              </div>
              <span
                class="rounded-full px-3 py-1.5 text-xs font-bold"
                :class="
                  industry.danh_muc_cha_id
                    ? 'bg-violet-50 text-violet-600'
                    : 'bg-sky-50 text-sky-600'
                "
              >
                {{ industry.danh_muc_cha_id ? 'Ngành con' : 'Ngành gốc' }}
              </span>
            </div>

            <!-- Card body -->
            <div class="mt-5">
              <h2
                class="text-lg font-bold text-slate-900 transition group-hover:text-[#2463eb]"
              >
                {{ industry.ten_nganh }}
              </h2>
              <p class="mt-1 text-xs text-slate-400">
                {{ industry.danh_muc_cha_id ? 'Thuộc nhóm ngành cấp trên' : 'Danh mục chính' }}
              </p>
            </div>

            <p class="mt-4 line-clamp-4 flex-1 text-sm leading-7 text-slate-500">
              {{ industry.mo_ta || 'Ngành nghề này đang được cập nhật thêm mô tả chi tiết.' }}
            </p>

            <!-- Card footer -->
            <div class="mt-5 flex items-center justify-between gap-3 border-t border-slate-100 pt-4">
              <RouterLink
                :to="{ path: '/jobs', query: { nganh_nghe_id: industry.id } }"
                class="rounded-xl border border-slate-200 px-4 py-2 text-sm font-bold text-slate-700 transition hover:border-[#2463eb] hover:text-[#2463eb]"
              >
                Xem việc
              </RouterLink>
              <RouterLink
                :to="`/industries/${industry.id}`"
                class="shrink-0 rounded-xl bg-slate-900 px-4 py-2 text-sm font-bold text-white transition hover:bg-[#2463eb]"
              >
                Chi tiết →
              </RouterLink>
            </div>
          </div>
        </div>

        <!-- Empty state -->
        <div
          v-else
          class="mt-8 rounded-3xl border border-dashed border-slate-300 p-12 text-center"
        >
          <div
            class="mx-auto mb-5 flex size-16 items-center justify-center rounded-2xl bg-slate-100"
          >
            <span class="material-symbols-outlined text-3xl text-slate-400">search_off</span>
          </div>
          <p class="text-lg font-semibold text-slate-700">Chưa tìm thấy ngành nghề phù hợp.</p>
          <p class="mt-2 text-sm text-slate-500">Thử tìm kiếm với từ khoá khác hoặc xoá bộ lọc.</p>
          <button
            type="button"
            class="mt-5 inline-flex rounded-xl bg-[#2463eb] px-5 py-2.5 text-sm font-bold text-white hover:bg-blue-700"
            @click="clearFilters"
          >
            Xoá bộ lọc
          </button>
        </div>

        <!-- Pagination -->
        <div
          v-if="!loading && totalPages > 1"
          class="mt-10 flex items-center justify-center gap-2"
        >
          <button
            type="button"
            :disabled="filters.page <= 1"
            class="inline-flex h-10 w-10 items-center justify-center rounded-2xl border border-slate-200 text-slate-600 transition hover:border-[#2463eb] hover:text-[#2463eb] disabled:opacity-40"
            @click="changePage(filters.page - 1)"
          >
            <span class="material-symbols-outlined text-[20px]">chevron_left</span>
          </button>
          <span class="px-4 text-sm font-semibold text-slate-700">
            Trang {{ filters.page }} / {{ totalPages }}
          </span>
          <button
            type="button"
            :disabled="filters.page >= totalPages"
            class="inline-flex h-10 w-10 items-center justify-center rounded-2xl border border-slate-200 text-slate-600 transition hover:border-[#2463eb] hover:text-[#2463eb] disabled:opacity-40"
            @click="changePage(filters.page + 1)"
          >
            <span class="material-symbols-outlined text-[20px]">chevron_right</span>
          </button>
        </div>

      </div>
    </section>
  </div>
</template>

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

// Chỉ ngành cha để hiển thị trong dropdown lọc
const parentOptions = computed(() =>
  industries.value.filter((item) => !item.danh_muc_cha_id)
)

const totalPages = computed(() =>
  filters.value.perPage > 0
    ? Math.max(1, Math.ceil(totalIndustries.value / filters.value.perPage))
    : 1
)

const syncRoute = () => {
  const q = {}
  if (filters.value.search) q.search = filters.value.search
  if (filters.value.parentId) q.parent_id = filters.value.parentId
  if (filters.value.page > 1) q.page = filters.value.page
  if (filters.value.perPage !== 9) q.per_page = filters.value.perPage
  router.replace({ path: '/industries', query: q })
}

const loadIndustries = async () => {
  loading.value = true
  try {
    const opts = {
      per_page: filters.value.perPage,
    }
    if (filters.value.search.trim()) opts.search = filters.value.search.trim()
    if (filters.value.parentId) opts.danh_muc_cha_id = filters.value.parentId

    const response = await jobService.getIndustries(opts)
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

const clearFilters = () => {
  filters.value.search = ''
  filters.value.parentId = ''
  filters.value.page = 1
  filters.value.perPage = 9
  applyFilters()
}

const changePage = (page) => {
  filters.value.page = page
  syncRoute()
  loadIndustries()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

watch(
  () => route.query,
  (query) => {
    filters.value.search = query.search || ''
    filters.value.parentId = query.parent_id || ''
    filters.value.page = Number(query.page || 1)
    filters.value.perPage = Number(query.per_page || 9)
  }
)

onMounted(loadIndustries)
</script>
