<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { jobService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'

const route = useRoute()
const router = useRouter()
const notify = useNotify()

const loading = ref(false)
const companies = ref([])
const totalCompanies = ref(0)
const filters = ref({
  search: route.query.search || '',
  page: Number(route.query.page || 1),
  perPage: Number(route.query.per_page || 8),
})

const extractList = (response) => {
  const payload = response?.data
  if (Array.isArray(payload?.data)) return payload.data
  if (Array.isArray(payload)) return payload
  return []
}

const totalPages = computed(() => Math.max(1, Math.ceil(totalCompanies.value / filters.value.perPage)))

const syncRoute = () => {
  router.replace({
    path: '/companies',
    query: {
      ...(filters.value.search ? { search: filters.value.search } : {}),
      ...(filters.value.page > 1 ? { page: filters.value.page } : {}),
      per_page: filters.value.perPage,
    },
  })
}

const loadCompanies = async () => {
  loading.value = true
  try {
    const response = await jobService.getCompanies({
      search: filters.value.search.trim() || undefined,
      page: filters.value.page,
      per_page: filters.value.perPage,
    })

    companies.value = extractList(response)
    totalCompanies.value = Number(response?.data?.total || companies.value.length || 0)
  } catch (error) {
    companies.value = []
    totalCompanies.value = 0
    notify.apiError(error, 'Không thể tải danh sách công ty.')
  } finally {
    loading.value = false
  }
}

const applyFilters = () => {
  filters.value.page = 1
  syncRoute()
  loadCompanies()
}

const setPage = (page) => {
  if (page < 1 || page > totalPages.value || page === filters.value.page) return
  filters.value.page = page
  syncRoute()
  loadCompanies()
}

watch(
  () => route.query,
  (query) => {
    filters.value.search = query.search || ''
    filters.value.page = Number(query.page || 1)
    filters.value.perPage = Number(query.per_page || 8)
  },
)

onMounted(loadCompanies)
</script>

<template>
  <section class="py-14 lg:py-16">
    <div class="mx-auto max-w-7xl px-6">
      <div class="rounded-[32px] border border-slate-200 bg-gradient-to-r from-white via-blue-50 to-indigo-100 p-8 shadow-xl shadow-slate-200/70 dark:border-slate-800 dark:from-slate-900 dark:via-slate-900 dark:to-slate-800 dark:shadow-slate-950/30">
        <p class="text-sm font-bold uppercase tracking-[0.35em] text-[#2463eb]">Company Explorer</p>
        <h1 class="mt-4 text-4xl font-black tracking-tight text-slate-900 dark:text-white">
          Khám phá doanh nghiệp đang tuyển dụng
        </h1>
        <p class="mt-4 max-w-3xl text-base leading-8 text-slate-600 dark:text-slate-400">
          Theo dõi các công ty đang hoạt động, xem nhanh quy mô, mô tả và chuyển vào chi tiết doanh nghiệp để khám phá những vị trí phù hợp.
        </p>
      </div>

      <div class="mt-8 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm shadow-slate-200/60 dark:border-slate-800 dark:bg-slate-900 dark:shadow-slate-950/20">
        <div class="grid gap-4 xl:grid-cols-[minmax(0,1fr)_220px_190px]">
          <div class="rounded-2xl border border-slate-200 bg-slate-50 px-4 dark:border-slate-800 dark:bg-slate-950">
            <label class="block pt-3 text-xs font-bold uppercase tracking-[0.3em] text-slate-400">Tìm công ty</label>
            <input
              v-model="filters.search"
              type="text"
              class="w-full border-none bg-transparent py-3 text-slate-900 shadow-none outline-none ring-0 placeholder:text-slate-400 focus:ring-0 dark:text-white"
              placeholder="Tên công ty, địa chỉ..."
              @keyup.enter="applyFilters"
            />
          </div>

          <label class="rounded-2xl border border-slate-200 bg-slate-50 px-4 dark:border-slate-800 dark:bg-slate-950">
            <span class="block pt-3 text-xs font-bold uppercase tracking-[0.3em] text-slate-400">Số dòng / trang</span>
            <select
              v-model="filters.perPage"
              class="w-full border-none bg-transparent py-3 text-slate-900 outline-none ring-0 focus:ring-0 dark:text-white"
              @change="applyFilters"
            >
              <option :value="8">8</option>
              <option :value="12">12</option>
              <option :value="16">16</option>
            </select>
          </label>

          <button
            type="button"
            class="rounded-2xl bg-[#2463eb] px-6 py-4 text-sm font-bold text-white shadow-lg shadow-[#2463eb]/20 transition hover:bg-blue-700"
            @click="applyFilters"
          >
            Áp dụng bộ lọc
          </button>
        </div>
      </div>

      <div class="mt-6 flex flex-col gap-3 text-sm text-slate-500 dark:text-slate-400 sm:flex-row sm:items-center sm:justify-between">
        <p>{{ totalCompanies }} công ty đang hiển thị</p>
        <RouterLink to="/" class="font-semibold text-[#2463eb] hover:underline">Quay lại trang chủ</RouterLink>
      </div>

      <div v-if="loading" class="mt-8 grid gap-6 sm:grid-cols-2 xl:grid-cols-3">
        <div
          v-for="index in filters.perPage"
          :key="index"
          class="h-72 animate-pulse rounded-3xl bg-slate-200/70 dark:bg-slate-800/70"
        ></div>
      </div>

      <div v-else-if="companies.length" class="mt-8 grid gap-6 sm:grid-cols-2 xl:grid-cols-3">
        <div
          v-for="company in companies"
          :key="company.id"
          class="group flex h-full flex-col rounded-3xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:border-[#2463eb]/40 hover:shadow-xl dark:border-slate-800 dark:bg-slate-900"
        >
          <div class="flex items-center gap-4">
            <img
              v-if="company.logo_url"
              :src="company.logo_url"
              :alt="company.ten_cong_ty"
              class="h-16 w-16 rounded-2xl object-cover ring-1 ring-slate-200 dark:ring-slate-700"
            />
            <div
              v-else
              class="flex h-16 w-16 items-center justify-center rounded-2xl bg-[#2463eb]/10 text-xl font-black text-[#2463eb]"
            >
              {{ company.ten_cong_ty?.slice(0, 1) }}
            </div>

            <div class="min-w-0">
              <h2 class="truncate text-lg font-bold text-slate-900 group-hover:text-[#2463eb] dark:text-white">
                {{ company.ten_cong_ty }}
              </h2>
              <RouterLink
                v-if="company.nganh_nghe?.id"
                :to="`/industries/${company.nganh_nghe.id}`"
                class="truncate text-sm text-slate-500 transition hover:text-[#2463eb]"
              >
                {{ company.nganh_nghe?.ten_nganh || 'Doanh nghiệp công nghệ' }}
              </RouterLink>
              <p v-else class="truncate text-sm text-slate-500">
                {{ company.nganh_nghe?.ten_nganh || 'Doanh nghiệp công nghệ' }}
              </p>
            </div>
          </div>

          <div class="mt-5 flex flex-wrap gap-2">
            <span class="rounded-full bg-blue-50 px-3 py-1.5 text-xs font-bold text-[#2463eb] dark:bg-slate-800 dark:text-blue-300">
              {{ company.quy_mo || 'Đang cập nhật quy mô' }}
            </span>
            <span class="rounded-full bg-slate-100 px-3 py-1.5 text-xs font-bold text-slate-600 dark:bg-slate-800 dark:text-slate-300">
              {{ company.so_tin_dang_hoat_dong || 0 }} tin đang mở
            </span>
          </div>

          <p class="mt-5 line-clamp-4 flex-1 text-sm leading-7 text-slate-600 dark:text-slate-400">
            {{ company.mo_ta || 'Doanh nghiệp đang cập nhật thêm phần giới thiệu và thông tin tuyển dụng.' }}
          </p>

          <div class="mt-5 flex items-center justify-between gap-3">
            <p class="line-clamp-2 text-sm text-slate-500">{{ company.dia_chi || 'Địa chỉ đang cập nhật' }}</p>
            <RouterLink
              :to="`/companies/${company.id}`"
              class="shrink-0 rounded-xl bg-slate-900 px-4 py-2 text-sm font-bold text-white transition hover:bg-[#2463eb] dark:bg-white dark:text-slate-900 dark:hover:bg-[#2463eb] dark:hover:text-white"
            >
              Xem chi tiết
            </RouterLink>
          </div>
        </div>
      </div>

      <div v-else class="mt-8 rounded-3xl border border-dashed border-slate-300 p-12 text-center dark:border-slate-700">
        <p class="text-lg font-semibold text-slate-700 dark:text-slate-300">Chưa tìm thấy công ty phù hợp.</p>
      </div>

      <div v-if="totalPages > 1" class="mt-10 flex items-center justify-center gap-3">
        <button
          type="button"
          class="rounded-xl border border-slate-200 px-4 py-2 text-sm font-bold text-slate-700 transition hover:border-[#2463eb] hover:text-[#2463eb] disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700 dark:text-slate-200"
          :disabled="filters.page <= 1"
          @click="setPage(filters.page - 1)"
        >
          Trước
        </button>
        <span class="text-sm font-semibold text-slate-500 dark:text-slate-400">
          Trang {{ filters.page }} / {{ totalPages }}
        </span>
        <button
          type="button"
          class="rounded-xl border border-slate-200 px-4 py-2 text-sm font-bold text-slate-700 transition hover:border-[#2463eb] hover:text-[#2463eb] disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700 dark:text-slate-200"
          :disabled="filters.page >= totalPages"
          @click="setPage(filters.page + 1)"
        >
          Sau
        </button>
      </div>
    </div>
  </section>
</template>
