<script setup>
import { computed } from 'vue'
import {
  cvSkillLevelLabel,
  cvSkillLevelPercent,
  formatCvPeriod,
  getCvTemplateTheme,
  resolveProfileCvAvatarUrl,
  resolveCvTemplateValue,
} from '@/utils/profileCvBuilder'

const props = defineProps({
  profile: {
    type: Object,
    required: true,
  },
  owner: {
    type: Object,
    default: () => ({}),
  },
  compact: {
    type: Boolean,
    default: false,
  },
})

const degreeOptions = {
  trung_hoc: 'Trung học',
  trung_cap: 'Trung cấp',
  cao_dang: 'Cao đẳng',
  dai_hoc: 'Đại học',
  thac_si: 'Thạc sĩ',
  tien_si: 'Tiến sĩ',
  khac: 'Khác',
}

const template = computed(() => resolveCvTemplateValue(props.profile?.mau_cv || 'executive_navy'))
const theme = computed(() => getCvTemplateTheme(template.value))
const fullName = computed(() => props.owner?.ho_ten || 'Ứng viên')
const email = computed(() => props.owner?.email || 'Chưa cập nhật email')
const phone = computed(() => props.owner?.so_dien_thoai || 'Chưa cập nhật số điện thoại')
const avatarUrl = computed(() => resolveProfileCvAvatarUrl(props.profile, props.owner))
const avatarInitials = computed(() =>
  String(fullName.value || 'U')
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part.charAt(0).toUpperCase())
    .join(''),
)
const title = computed(() => props.profile?.tieu_de_ho_so || 'Hồ sơ ứng tuyển trên hệ thống')
const objective = computed(() => props.profile?.muc_tieu_nghe_nghiep || 'Chưa cập nhật mục tiêu nghề nghiệp.')
const summary = computed(() => props.profile?.mo_ta_ban_than || 'Chưa cập nhật mô tả bản thân.')
const degreeLabel = computed(() => degreeOptions[props.profile?.trinh_do] || 'Chưa cập nhật')
const years = computed(() => `${props.profile?.kinh_nghiem_nam || 0} năm`)
const targetPosition = computed(() => props.profile?.vi_tri_ung_tuyen_muc_tieu || 'Đa vị trí')
const targetIndustry = computed(() => props.profile?.ten_nganh_nghe_muc_tieu || 'Đang cập nhật')
const skills = computed(() => Array.isArray(props.profile?.ky_nang_json) ? props.profile.ky_nang_json.filter((item) => item?.ten) : [])
const experiences = computed(() => Array.isArray(props.profile?.kinh_nghiem_json) ? props.profile.kinh_nghiem_json.filter((item) => item?.vi_tri) : [])
const educations = computed(() => Array.isArray(props.profile?.hoc_van_json) ? props.profile.hoc_van_json.filter((item) => item?.truong) : [])
const projects = computed(() => Array.isArray(props.profile?.du_an_json) ? props.profile.du_an_json.filter((item) => item?.ten) : [])
const certificates = computed(() => Array.isArray(props.profile?.chung_chi_json) ? props.profile.chung_chi_json.filter((item) => item?.ten) : [])

const limitedExperiences = computed(() => experiences.value.slice(0, props.compact ? 2 : 4))
const limitedProjects = computed(() => projects.value.slice(0, props.compact ? 2 : 3))
const limitedCertificates = computed(() => certificates.value.slice(0, props.compact ? 2 : 3))
</script>

<template>
  <div class="overflow-hidden bg-white shadow-sm" :style="{ color: theme.text }">
    <template v-if="template === 'executive_navy'">
      <div class="bg-[#2f3557] px-6 py-7 text-center text-[#d7bd79] md:px-10">
        <h3 class="text-3xl font-medium uppercase tracking-[0.22em] md:text-4xl">{{ fullName }}</h3>
        <div class="mx-auto mt-4 h-[2px] w-40 bg-[#d7bd79] relative">
          <span class="absolute left-1/2 top-1/2 h-3.5 w-3.5 -translate-x-1/2 -translate-y-1/2 rotate-45 border-2 border-[#d7bd79] bg-[#2f3557]" />
        </div>
        <p class="mt-4 text-xs font-semibold uppercase tracking-[0.3em] md:text-sm">{{ title }}</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-[280px_minmax(0,1fr)]">
        <aside class="border-r border-slate-200 px-6 py-6">
          <section class="mb-6">
            <h4 class="text-xs font-bold uppercase tracking-[0.24em] text-slate-600">Liên lạc</h4>
            <div class="mt-3 h-px bg-slate-200" />
            <div class="mt-3 space-y-2 text-sm leading-6">
              <p>{{ phone }}</p>
              <p>{{ email }}</p>
              <p>{{ targetPosition }}</p>
              <p>{{ targetIndustry }}</p>
            </div>
          </section>

          <section class="mb-6">
            <h4 class="text-xs font-bold uppercase tracking-[0.24em] text-slate-600">Học vấn</h4>
            <div class="mt-3 h-px bg-slate-200" />
            <div v-if="educations.length" class="mt-3 space-y-4">
              <div v-for="(item, index) in educations" :key="`edu-navy-${index}`" class="text-sm leading-6">
                <p class="font-bold">{{ item.truong }}</p>
                <p>{{ item.chuyen_nganh || degreeLabel }}</p>
                <p class="text-slate-500">{{ formatCvPeriod(item.bat_dau, item.ket_thuc) }}</p>
              </div>
            </div>
            <p v-else class="mt-3 text-sm text-slate-500">Chưa cập nhật học vấn.</p>
          </section>

          <section class="mb-6">
            <h4 class="text-xs font-bold uppercase tracking-[0.24em] text-slate-600">Kỹ năng</h4>
            <div class="mt-3 h-px bg-slate-200" />
            <div class="mt-3 flex flex-wrap gap-2">
              <span
                v-for="(item, index) in skills"
                :key="`skill-navy-${index}`"
                class="rounded-full border border-slate-200 px-3 py-1 text-xs font-semibold text-slate-700"
              >
                {{ item.ten }}
              </span>
            </div>
            <p v-if="!skills.length" class="mt-3 text-sm text-slate-500">Chưa cập nhật kỹ năng.</p>
          </section>

          <section>
            <h4 class="text-xs font-bold uppercase tracking-[0.24em] text-slate-600">Chứng chỉ</h4>
            <div class="mt-3 h-px bg-slate-200" />
            <div v-if="limitedCertificates.length" class="mt-3 space-y-3 text-sm leading-6">
              <div v-for="(item, index) in limitedCertificates" :key="`cert-navy-${index}`">
                <p class="font-bold">{{ item.ten }}</p>
                <p>{{ item.don_vi }}</p>
                <p class="text-slate-500">{{ item.nam }}</p>
              </div>
            </div>
            <p v-else class="mt-3 text-sm text-slate-500">Chưa cập nhật chứng chỉ.</p>
          </section>
        </aside>

        <main class="px-6 py-6 md:px-8">
          <section class="mb-7">
            <h4 class="text-xs font-bold uppercase tracking-[0.24em] text-slate-600">Giới thiệu</h4>
            <div class="mt-3 h-px bg-slate-200" />
            <p class="mt-3 whitespace-pre-wrap text-sm leading-7">{{ summary }}</p>
          </section>

          <section class="mb-7">
            <h4 class="text-xs font-bold uppercase tracking-[0.24em] text-slate-600">Kinh nghiệm làm việc</h4>
            <div class="mt-3 h-px bg-slate-200" />
            <div v-if="limitedExperiences.length" class="mt-4 space-y-5">
              <article v-for="(item, index) in limitedExperiences" :key="`exp-navy-${index}`">
                <p class="text-sm font-bold">{{ item.vi_tri }}</p>
                <p class="mt-1 text-sm font-semibold">{{ item.cong_ty || 'Chưa cập nhật công ty' }}</p>
                <p class="mt-1 text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">{{ formatCvPeriod(item.bat_dau, item.ket_thuc) }}</p>
                <p v-if="item.mo_ta" class="mt-2 whitespace-pre-wrap text-sm leading-7 text-slate-600">{{ item.mo_ta }}</p>
              </article>
            </div>
            <p v-else class="mt-3 text-sm text-slate-500">Chưa cập nhật kinh nghiệm làm việc.</p>
          </section>

          <section>
            <h4 class="text-xs font-bold uppercase tracking-[0.24em] text-slate-600">Dự án nổi bật</h4>
            <div class="mt-3 h-px bg-slate-200" />
            <div v-if="limitedProjects.length" class="mt-4 space-y-5">
              <article v-for="(item, index) in limitedProjects" :key="`project-navy-${index}`">
                <p class="text-sm font-bold">{{ item.ten }}</p>
                <p class="mt-1 text-sm font-semibold">{{ item.vai_tro || 'Vai trò đang cập nhật' }}</p>
                <p v-if="item.cong_nghe" class="mt-1 text-xs uppercase tracking-[0.16em] text-slate-400">{{ item.cong_nghe }}</p>
                <p v-if="item.mo_ta" class="mt-2 whitespace-pre-wrap text-sm leading-7 text-slate-600">{{ item.mo_ta }}</p>
              </article>
            </div>
            <p v-else class="mt-3 text-sm text-slate-500">Chưa cập nhật dự án.</p>
          </section>
        </main>
      </div>
    </template>

    <template v-else-if="template === 'topcv_maroon'">
      <div class="grid grid-cols-1 md:grid-cols-[320px_minmax(0,1fr)]">
        <aside class="bg-[#5b3133] text-white">
          <div class="bg-[#a45a5d] px-6 py-7 text-center">
            <div class="mx-auto flex h-52 w-52 items-center justify-center overflow-hidden rounded-full border-4 border-white bg-white text-5xl font-bold text-[#5b3133]">
              <img v-if="avatarUrl" :src="avatarUrl" alt="avatar" class="h-full w-full object-cover" />
              <span v-else>{{ avatarInitials }}</span>
            </div>
            <h3 class="mt-6 text-3xl font-black">{{ fullName }}</h3>
            <p class="mt-3 text-xl font-medium text-white/90">{{ title }}</p>
          </div>

          <div class="px-6 py-6">
            <section class="mb-7 space-y-2 text-sm leading-6">
              <p>{{ phone }}</p>
              <p>{{ email }}</p>
              <p>{{ targetIndustry }}</p>
              <p>{{ targetPosition }}</p>
            </section>

            <section class="mb-7">
              <h4 class="text-[15px] font-bold">Mục tiêu nghề nghiệp</h4>
              <p class="mt-3 whitespace-pre-wrap text-sm leading-7 text-white/90">{{ objective }}</p>
            </section>

            <section class="mb-7">
              <h4 class="text-[15px] font-bold">Kỹ năng</h4>
              <div v-if="skills.length" class="mt-4 space-y-4">
                <div v-for="(item, index) in skills.slice(0, compact ? 4 : 5)" :key="`skill-maroon-${index}`">
                  <p class="mb-2 text-sm">{{ item.ten }}</p>
                  <div class="h-3 overflow-hidden bg-white/20">
                    <div class="h-full bg-[#d98a8f]" :style="{ width: `${cvSkillLevelPercent(item.muc_do)}%` }" />
                  </div>
                </div>
              </div>
              <p v-else class="mt-3 text-sm text-white/70">Chưa cập nhật kỹ năng.</p>
            </section>

            <section>
              <h4 class="text-[15px] font-bold">Chứng chỉ / Dự án</h4>
              <div class="mt-3 space-y-3 text-sm leading-6 text-white/90">
                <div v-for="(item, index) in limitedCertificates" :key="`cert-maroon-${index}`">
                  <p class="font-semibold">{{ item.ten }}</p>
                  <p>{{ item.don_vi }}</p>
                </div>
                <div v-for="(item, index) in limitedProjects" :key="`project-maroon-${index}`">
                  <p class="font-semibold">{{ item.ten }}</p>
                  <p>{{ item.vai_tro || item.cong_nghe }}</p>
                </div>
              </div>
              <p v-if="!limitedCertificates.length && !limitedProjects.length" class="mt-3 text-sm text-white/70">Chưa cập nhật chứng chỉ hoặc dự án.</p>
            </section>
          </div>
        </aside>

        <main class="bg-white px-8 py-8">
          <section class="mb-8">
            <h4 class="text-2xl font-bold text-slate-900">Học vấn</h4>
            <div v-if="educations.length" class="mt-4 space-y-5">
              <article v-for="(item, index) in educations" :key="`edu-maroon-${index}`">
                <div class="flex flex-col gap-2 md:flex-row md:justify-between">
                  <div>
                    <p class="text-lg font-bold text-slate-900">{{ item.chuyen_nganh || degreeLabel }}</p>
                    <p class="mt-1 text-base font-semibold text-slate-900">{{ item.truong }}</p>
                  </div>
                  <p class="text-base text-slate-600">{{ formatCvPeriod(item.bat_dau, item.ket_thuc) }}</p>
                </div>
                <p v-if="item.mo_ta" class="mt-2 whitespace-pre-wrap text-sm leading-7 text-slate-600">{{ item.mo_ta }}</p>
              </article>
            </div>
            <p v-else class="mt-3 text-sm text-slate-500">Chưa cập nhật học vấn.</p>
          </section>

          <section class="mb-8">
            <h4 class="text-2xl font-bold text-slate-900">Kinh nghiệm làm việc</h4>
            <div v-if="limitedExperiences.length" class="mt-4 space-y-6">
              <article v-for="(item, index) in limitedExperiences" :key="`exp-maroon-${index}`">
                <div class="flex flex-col gap-2 md:flex-row md:justify-between">
                  <div>
                    <p class="text-xl font-bold text-slate-900">{{ item.vi_tri }}</p>
                    <p class="mt-1 text-lg font-semibold text-slate-900">{{ item.cong_ty || 'Chưa cập nhật công ty' }}</p>
                  </div>
                  <p class="text-base text-slate-600">{{ formatCvPeriod(item.bat_dau, item.ket_thuc) }}</p>
                </div>
                <p v-if="item.mo_ta" class="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-700">{{ item.mo_ta }}</p>
              </article>
            </div>
            <p v-else class="mt-3 text-sm text-slate-500">Chưa cập nhật kinh nghiệm làm việc.</p>
          </section>

          <section>
            <h4 class="text-2xl font-bold text-slate-900">Giới thiệu / Tóm tắt</h4>
            <p class="mt-4 whitespace-pre-wrap text-sm leading-7 text-slate-700">{{ summary }}</p>
          </section>
        </main>
      </div>
    </template>

    <template v-else>
      <div class="px-8 py-10 md:px-12">
        <header>
          <h3 class="text-[40px] font-bold leading-none text-slate-950" style="font-family: Georgia, 'Times New Roman', serif;">{{ fullName }}</h3>
          <p class="mt-3 text-xl text-slate-900" style="font-family: Georgia, 'Times New Roman', serif;">
            {{ targetIndustry }} | {{ phone }}
          </p>
          <p class="mt-1 text-xl text-slate-900" style="font-family: Georgia, 'Times New Roman', serif;">{{ email }}</p>
        </header>

        <section class="mt-10">
          <h4 class="text-2xl font-bold text-slate-950" style="font-family: Georgia, 'Times New Roman', serif;">Summary</h4>
          <div class="mt-3 h-px bg-slate-300" />
          <p class="mt-4 whitespace-pre-wrap text-[15px] leading-8 text-slate-900" style="font-family: Georgia, 'Times New Roman', serif;">{{ summary || objective }}</p>
        </section>

        <section class="mt-10">
          <h4 class="text-2xl font-bold text-slate-950" style="font-family: Georgia, 'Times New Roman', serif;">Experience</h4>
          <div class="mt-3 h-px bg-slate-300" />
          <div v-if="limitedExperiences.length" class="mt-5 space-y-6">
            <article v-for="(item, index) in limitedExperiences" :key="`exp-ats-${index}`">
              <p class="text-[18px] font-bold text-slate-950" style="font-family: Georgia, 'Times New Roman', serif;">{{ item.vi_tri }}</p>
              <p class="mt-1 text-[17px] font-bold text-slate-950" style="font-family: Georgia, 'Times New Roman', serif;">{{ item.cong_ty || 'Personal Projects' }}</p>
              <p class="mt-1 text-[15px] text-slate-800" style="font-family: Georgia, 'Times New Roman', serif;">{{ formatCvPeriod(item.bat_dau, item.ket_thuc) }}</p>
              <p v-if="item.mo_ta" class="mt-2 whitespace-pre-wrap text-[15px] leading-8 text-slate-900" style="font-family: Georgia, 'Times New Roman', serif;">{{ item.mo_ta }}</p>
            </article>
          </div>
          <p v-else class="mt-4 text-[15px] text-slate-500" style="font-family: Georgia, 'Times New Roman', serif;">Chưa cập nhật kinh nghiệm.</p>
        </section>

        <section class="mt-10">
          <h4 class="text-2xl font-bold text-slate-950" style="font-family: Georgia, 'Times New Roman', serif;">Skills</h4>
          <div class="mt-3 h-px bg-slate-300" />
          <p class="mt-4 text-[15px] leading-8 text-slate-900" style="font-family: Georgia, 'Times New Roman', serif;">
            {{ skills.map((item) => item.ten).join(', ') || 'Chưa cập nhật kỹ năng.' }}
          </p>
        </section>

        <section class="mt-10">
          <h4 class="text-2xl font-bold text-slate-950" style="font-family: Georgia, 'Times New Roman', serif;">Education</h4>
          <div class="mt-3 h-px bg-slate-300" />
          <div v-if="educations.length" class="mt-5 space-y-4">
            <article v-for="(item, index) in educations" :key="`edu-ats-${index}`">
              <p class="text-[18px] font-bold text-slate-950" style="font-family: Georgia, 'Times New Roman', serif;">{{ item.truong }}</p>
              <p class="mt-1 text-[17px] font-bold text-slate-950" style="font-family: Georgia, 'Times New Roman', serif;">{{ item.chuyen_nganh || degreeLabel }} | {{ formatCvPeriod(item.bat_dau, item.ket_thuc) }}</p>
              <p v-if="item.mo_ta" class="mt-2 whitespace-pre-wrap text-[15px] leading-8 text-slate-900" style="font-family: Georgia, 'Times New Roman', serif;">{{ item.mo_ta }}</p>
            </article>
          </div>
          <p v-else class="mt-4 text-[15px] text-slate-500" style="font-family: Georgia, 'Times New Roman', serif;">Chưa cập nhật học vấn.</p>
        </section>

        <section class="mt-10">
          <h4 class="text-2xl font-bold text-slate-950" style="font-family: Georgia, 'Times New Roman', serif;">Projects & Certifications</h4>
          <div class="mt-3 h-px bg-slate-300" />
          <div class="mt-5 space-y-4">
            <article v-for="(item, index) in limitedProjects" :key="`project-ats-${index}`">
              <p class="text-[18px] font-bold text-slate-950" style="font-family: Georgia, 'Times New Roman', serif;">{{ item.ten }}</p>
              <p class="mt-1 text-[15px] text-slate-900" style="font-family: Georgia, 'Times New Roman', serif;">{{ item.cong_nghe }}<span v-if="item.vai_tro"> | {{ item.vai_tro }}</span></p>
              <p v-if="item.mo_ta" class="mt-2 whitespace-pre-wrap text-[15px] leading-8 text-slate-900" style="font-family: Georgia, 'Times New Roman', serif;">{{ item.mo_ta }}</p>
            </article>
            <article v-for="(item, index) in limitedCertificates" :key="`cert-ats-${index}`">
              <p class="text-[18px] font-bold text-slate-950" style="font-family: Georgia, 'Times New Roman', serif;">{{ item.ten }}</p>
              <p class="mt-1 text-[15px] text-slate-900" style="font-family: Georgia, 'Times New Roman', serif;">{{ item.don_vi }}<span v-if="item.nam"> | {{ item.nam }}</span></p>
            </article>
          </div>
          <p v-if="!limitedProjects.length && !limitedCertificates.length" class="mt-4 text-[15px] text-slate-500" style="font-family: Georgia, 'Times New Roman', serif;">Chưa cập nhật dự án hoặc chứng chỉ.</p>
        </section>
      </div>
    </template>
  </div>
</template>
