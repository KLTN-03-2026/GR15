<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { jobService } from '@/services/api'
import { useNotify } from '@/composables/useNotify'

const route = useRoute()
const notify = useNotify()

const loading = ref(false)
const skill = ref(null)
const relatedSkills = ref([])

const extractList = (response) => {
  const payload = response?.data
  if (Array.isArray(payload?.data)) return payload.data
  if (Array.isArray(payload)) return payload
  return []
}

const loadSkillDetail = async () => {
  loading.value = true

  try {
    const skillResponse = await jobService.getSkillById(route.params.id)
    const skillPayload = skillResponse?.data || null
    skill.value = skillPayload

    if (!skillPayload) {
      relatedSkills.value = []
      return
    }

    const relatedSkillsResponse = await jobService.getSkills({
      search: skillPayload.ten_ky_nang.split(/\s+/).slice(0, 1).join(' '),
      per_page: 8,
    })

    relatedSkills.value = extractList(relatedSkillsResponse)
      .filter((item) => item.id !== skillPayload.id)
      .slice(0, 6)
  } catch (error) {
    skill.value = null
    relatedSkills.value = []
    notify.apiError(error, 'Khong tai duoc thong tin ky nang.')
  } finally {
    loading.value = false
  }
}

const skillName = computed(() => skill.value?.ten_ky_nang || 'Ky nang')
const skillDescription = computed(() => skill.value?.mo_ta || 'Ky nang nay dang duoc cap nhat them mo ta va ngu canh su dung.')

watch(() => route.params.id, loadSkillDetail)
onMounted(loadSkillDetail)
</script>

<template>
  <section class="py-14 lg:py-16">
    <div class="mx-auto max-w-7xl px-6">
      <div v-if="loading" class="space-y-6">
        <div class="h-72 animate-pulse rounded-[32px] bg-slate-200/70"></div>
        <div class="h-96 animate-pulse rounded-3xl bg-slate-200/70"></div>
      </div>

      <div v-else-if="skill" class="space-y-8">
        <div class="rounded-[32px] border border-slate-200 bg-gradient-to-br from-white via-blue-50 to-indigo-100 p-8 shadow-xl">
          <div class="flex flex-col gap-8 lg:flex-row lg:items-start lg:justify-between">
            <div class="min-w-0">
              <div class="flex flex-wrap items-center gap-3 text-sm font-semibold text-slate-500">
                <RouterLink to="/skills" class="hover:text-[#2463eb]">Ky nang</RouterLink>
                <span>/</span>
                <span>{{ skillName }}</span>
              </div>

              <p class="mt-5 text-sm font-bold uppercase tracking-[0.35em] text-[#2463eb]">Chi tiet ky nang</p>
              <h1 class="mt-3 text-3xl font-black tracking-tight text-slate-900 lg:text-4xl">
                {{ skillName }}
              </h1>
              <p class="mt-5 max-w-3xl text-base leading-8 text-slate-600">
                {{ skillDescription }}
              </p>

              <div class="mt-6 flex flex-wrap gap-3">
                <RouterLink
                  to="/skills"
                  class="rounded-xl border border-slate-200 px-5 py-3 text-sm font-bold text-slate-700 transition hover:border-[#2463eb] hover:text-[#2463eb]"
                >
                  Quay lai danh sach
                </RouterLink>
                <RouterLink to="/register" class="rounded-xl bg-[#2463eb] px-5 py-3 text-sm font-bold text-white transition hover:bg-blue-700">
                  Dang ky ngay
                </RouterLink>
              </div>
            </div>

            <div class="grid gap-4 sm:grid-cols-2 lg:min-w-[340px] lg:grid-cols-1">
              <div class="rounded-2xl border border-slate-200 bg-white/85 p-4">
                <p class="text-xs font-bold uppercase tracking-[0.3em] text-slate-400">Ky nang</p>
                <p class="mt-3 text-2xl font-black text-slate-900">{{ skillName }}</p>
              </div>
              <div class="rounded-2xl border border-slate-200 bg-white/85 p-4">
                <p class="text-xs font-bold uppercase tracking-[0.3em] text-slate-400">Lien quan</p>
                <p class="mt-3 text-base font-semibold text-slate-900">{{ relatedSkills.length }} ky nang</p>
              </div>
              <div class="rounded-2xl border border-slate-200 bg-white/85 p-4">
                <p class="text-xs font-bold uppercase tracking-[0.3em] text-slate-400">Ung dung</p>
                <p class="mt-3 text-base font-semibold text-slate-900">Mo ta, phan loai, tham khao hoc tap</p>
              </div>
            </div>
          </div>
        </div>

        <div class="space-y-6">
          <div class="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
            <h2 class="text-xl font-bold text-slate-900">Ky nang lien quan</h2>
            <div v-if="relatedSkills.length" class="mt-5 flex flex-wrap gap-3">
              <RouterLink
                v-for="item in relatedSkills"
                :key="item.id"
                :to="`/skills/${item.id}`"
                class="rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-[#2463eb] hover:text-[#2463eb]"
              >
                {{ item.ten_ky_nang || item.ten }}
              </RouterLink>
            </div>
            <p v-else class="mt-5 text-sm text-slate-500">
              Chua co them ky nang lien quan de goi y.
            </p>
          </div>

          <div class="rounded-3xl border border-slate-200 bg-gradient-to-br from-[#2463eb] to-indigo-500 p-8 text-white shadow-xl">
            <p class="text-sm font-bold uppercase tracking-[0.35em] text-white/70">Goi y hanh dong</p>
            <h3 class="mt-4 text-2xl font-black">Tap trung vao 4 chuc nang chinh</h3>
            <p class="mt-3 text-sm leading-7 text-white/80">
              Trang chi tiet nay giu lai thong tin mo ta ky nang va cac goi y lien quan, khong mo rong sang cac module khac.
            </p>
            <div class="mt-6 flex flex-wrap gap-3">
              <RouterLink to="/skills" class="rounded-xl bg-white px-4 py-3 text-sm font-bold text-[#2463eb] transition hover:bg-slate-100">
                Danh sach ky nang
              </RouterLink>
              <RouterLink to="/applications" class="rounded-xl border border-white/30 px-4 py-3 text-sm font-bold text-white transition hover:bg-white/10">
                Theo doi don
              </RouterLink>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="rounded-3xl border border-dashed border-slate-300 p-12 text-center">
        <p class="text-lg font-semibold text-slate-700">Khong tim thay thong tin ky nang.</p>
        <RouterLink to="/skills" class="mt-4 inline-flex rounded-xl bg-[#2463eb] px-5 py-3 text-sm font-bold text-white">
          Quay lai danh sach ky nang
        </RouterLink>
      </div>
    </div>
  </section>
</template>
