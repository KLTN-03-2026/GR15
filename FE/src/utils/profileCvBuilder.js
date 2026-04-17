export const cvTemplateOptions = [
  {
    value: 'executive_navy',
    label: 'Executive Navy',
    description: 'Bám theo mẫu header xanh đậm, tên căn giữa, sidebar trái và phần kinh nghiệm chi tiết.',
    badges: ['Hợp Product / Business', 'Hợp HR / Finance'],
  },
  {
    value: 'topcv_maroon',
    label: 'Sidebar Maroon',
    description: 'Bám theo mẫu sidebar đỏ nâu có ảnh đại diện lớn, cột trái đậm màu và nội dung trắng bên phải.',
    badges: ['Hợp Frontend / Mobile', 'Hợp Marketing / UI UX'],
  },
  {
    value: 'ats_serif',
    label: 'ATS Serif',
    description: 'Bám theo mẫu ATS trắng tối giản, chữ serif, một cột, ưu tiên đọc nhanh và in đẹp.',
    badges: ['Hợp ATS / Software', 'Hợp Data / Intern'],
  },
]

export const cvTemplateModeOptions = [
  { value: 'style', label: 'Theo phong cách', description: 'Chọn trực tiếp phong cách CV bám theo các mẫu tham chiếu.' },
  { value: 'position', label: 'Theo vị trí ứng tuyển', description: 'Chọn vị trí mục tiêu để hệ thống đề xuất mẫu CV phù hợp hơn.' },
]

export const cvStyleFamilyOptions = [
  {
    value: 'executive_navy',
    label: 'Executive Navy',
    description: 'Phù hợp Product, Business, HR, Finance và các hồ sơ cần cảm giác điều hành, trang trọng.',
  },
  {
    value: 'topcv_maroon',
    label: 'Sidebar Maroon',
    description: 'Phù hợp Frontend, Mobile, Marketing, UI/UX hoặc hồ sơ cần điểm nhấn hình ảnh mạnh hơn.',
  },
  {
    value: 'ats_serif',
    label: 'ATS Serif',
    description: 'Phù hợp Software Engineer, Data, Intern và hồ sơ cần tối ưu đọc nhanh, in đẹp, dễ scan.',
  },
]

export const cvTargetPositionOptions = [
  { value: 'backend_developer', label: 'Backend Developer', template: 'ats_serif' },
  { value: 'frontend_mobile', label: 'Frontend / Mobile Developer', template: 'topcv_maroon' },
  { value: 'data_analyst', label: 'Data Analyst', template: 'ats_serif' },
  { value: 'product_manager', label: 'Product Manager / Business Analyst', template: 'executive_navy' },
  { value: 'product_designer', label: 'Product Designer / UI UX', template: 'topcv_maroon' },
  { value: 'digital_marketer', label: 'Digital Marketer', template: 'topcv_maroon' },
  { value: 'hr_recruiter', label: 'HR / Recruiter', template: 'executive_navy' },
  { value: 'finance_accounting', label: 'Finance / Accounting', template: 'executive_navy' },
  { value: 'operations_customer_success', label: 'Operations / Customer Success', template: 'ats_serif' },
]

export const cvStylePreferenceOptions = [
  { value: 'balanced', label: 'Cân bằng' },
  { value: 'formal', label: 'Trang trọng' },
  { value: 'creative', label: 'Nổi bật' },
  { value: 'compact', label: 'Tối giản' },
]

export const cvSkillLevelOptions = [
  { value: 'co_ban', label: 'Cơ bản' },
  { value: 'kha', label: 'Khá' },
  { value: 'tot', label: 'Tốt' },
  { value: 'chuyen_sau', label: 'Chuyên sâu' },
]

const TEMPLATE_ALIAS_MAP = {
  classic: 'executive_navy',
  executive: 'executive_navy',
  minimal: 'ats_serif',
  compact: 'ats_serif',
  modern: 'topcv_maroon',
  creative: 'topcv_maroon',
}

const DEFAULT_TEMPLATE = 'executive_navy'

const asArray = (value) => (Array.isArray(value) ? value.filter(Boolean) : [])

export const resolveProfileCvAvatarUrl = (profile, owner) => {
  const photoMode = String(profile?.che_do_anh_cv || 'profile').trim()

  if (photoMode === 'upload') {
    const uploadedPhoto =
      profile?.anh_cv_preview_url ||
      profile?.anh_cv_url ||
      profile?.anh_cv ||
      ''

    if (uploadedPhoto) {
      return uploadedPhoto
    }
  }

  return owner?.avatar_url || owner?.anh_dai_dien_url || owner?.anh_dai_dien || ''
}

export const resolveCvTemplateValue = (value) => {
  const normalized = String(value || '').trim()
  if (!normalized) return DEFAULT_TEMPLATE
  return TEMPLATE_ALIAS_MAP[normalized] || normalized
}

export const hasBuilderCv = (profile) => {
  if (!profile) return false
  if (profile.nguon_ho_so && profile.nguon_ho_so !== 'upload') return true

  return [
    profile.ky_nang_json,
    profile.kinh_nghiem_json,
    profile.hoc_van_json,
    profile.du_an_json,
    profile.chung_chi_json,
  ].some((items) => asArray(items).length > 0)
}

export const cvTemplateLabel = (value) =>
  cvTemplateOptions.find((item) => item.value === resolveCvTemplateValue(value))?.label || 'Executive Navy'

export const inferCvStyleFamily = (template) => resolveCvTemplateValue(template)

export const getCvTemplatesForMode = () => cvTemplateOptions

const cvTemplateThemes = {
  executive_navy: {
    accent: '#d7bd79',
    accentSoft: '#d7dbe7',
    panel: '#f4f5f8',
    text: '#243049',
    hero: '#2f3557',
    sidebar: '#ffffff',
    border: '#d7dbe7',
  },
  topcv_maroon: {
    accent: '#a45a5d',
    accentSoft: '#ead6d7',
    panel: '#f7eded',
    text: '#2a2526',
    hero: '#a45a5d',
    sidebar: '#5b3133',
    border: '#e7d5d6',
  },
  ats_serif: {
    accent: '#111111',
    accentSoft: '#d9d9d9',
    panel: '#f7f7f7',
    text: '#111111',
    hero: '#ffffff',
    sidebar: '#ffffff',
    border: '#d2d2d2',
  },
}

export const getCvTemplateTheme = (value) =>
  cvTemplateThemes[resolveCvTemplateValue(value)] || cvTemplateThemes[DEFAULT_TEMPLATE]

export const cvSkillLevelLabel = (value) =>
  cvSkillLevelOptions.find((item) => item.value === value)?.label || 'Tự đánh giá'

export const cvSkillLevelPercent = (value) => {
  switch (value) {
    case 'chuyen_sau':
      return 96
    case 'tot':
      return 82
    case 'kha':
      return 68
    case 'co_ban':
    default:
      return 48
  }
}

export const formatCvPeriod = (start, end) => {
  const from = String(start || '').trim()
  const to = String(end || '').trim()

  if (from && to) return `${from} - ${to}`
  if (from) return `${from} - Hiện tại`
  if (to) return to
  return 'Chưa cập nhật'
}

const normalizeIndustryName = (value) =>
  String(value || '')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')

const industryPresetMatchers = [
  {
    keywords: ['product', 'business analyst', 'business', 'quan tri', 'quản trị', 'van hanh san pham', 'san pham'],
    templates: {
      balanced: 'executive_navy',
      formal: 'executive_navy',
      creative: 'topcv_maroon',
      compact: 'ats_serif',
    },
    suggestedTitle: 'CV Product / Business',
    suggestedObjective:
      'Tập trung vào tư duy sản phẩm, khả năng phân tích nhu cầu người dùng, ưu tiên tính năng và phối hợp đa phòng ban để đưa sản phẩm ra thị trường.',
    suggestedSkills: ['Phân tích yêu cầu', 'Product thinking', 'Stakeholder management'],
  },
  {
    keywords: ['cntt', 'cong nghe', 'it', 'software', 'developer', 'backend', 'frontend', 'mobile', 'data', 'ai', 'lap trinh'],
    templates: {
      balanced: 'ats_serif',
      formal: 'executive_navy',
      creative: 'topcv_maroon',
      compact: 'ats_serif',
    },
    suggestedTitle: 'CV Software Engineer',
    suggestedObjective:
      'Nhấn mạnh stack công nghệ chính, dự án thực tế, kết quả đo lường được và khả năng triển khai sản phẩm từ yêu cầu đến vận hành.',
    suggestedSkills: ['Giải quyết vấn đề', 'Làm việc nhóm', 'Phân tích yêu cầu'],
  },
  {
    keywords: ['thiet ke', 'design', 'ui', 'ux', 'creative', 'multimedia', 'branding'],
    templates: {
      balanced: 'topcv_maroon',
      formal: 'executive_navy',
      creative: 'topcv_maroon',
      compact: 'ats_serif',
    },
    suggestedTitle: 'CV Product Designer / UI UX',
    suggestedObjective:
      'Làm nổi bật tư duy thiết kế, case study thực tế, khả năng giải quyết bài toán người dùng và trình bày portfolio mạch lạc.',
    suggestedSkills: ['Wireframing', 'Design system', 'User research'],
  },
  {
    keywords: ['marketing', 'truyen thong', 'content', 'seo', 'digital', 'social'],
    templates: {
      balanced: 'topcv_maroon',
      formal: 'executive_navy',
      creative: 'topcv_maroon',
      compact: 'ats_serif',
    },
    suggestedTitle: 'CV Digital Marketing',
    suggestedObjective:
      'Ưu tiên trình bày chiến dịch đã triển khai, chỉ số hiệu quả và khả năng phối hợp nội dung, quảng cáo và phân tích dữ liệu.',
    suggestedSkills: ['Campaign planning', 'Content strategy', 'Data analysis'],
  },
  {
    keywords: ['tai chinh', 'ke toan', 'finance', 'accounting', 'kiem toan', 'audit', 'ngan hang', 'nhan su', 'recruitment', 'hr'],
    templates: {
      balanced: 'executive_navy',
      formal: 'executive_navy',
      creative: 'topcv_maroon',
      compact: 'ats_serif',
    },
    suggestedTitle: 'CV Chuyên nghiệp',
    suggestedObjective:
      'Ưu tiên sự rõ ràng, độ tin cậy và tính chuyên nghiệp trong cách trình bày kinh nghiệm, quy trình làm việc và kết quả đạt được.',
    suggestedSkills: ['Giao tiếp', 'Quản lý quy trình', 'Tổ chức công việc'],
  },
]

const positionPresetMap = {
  backend_developer: {
    template: 'ats_serif',
    suggestedTitle: 'CV Backend Developer',
    suggestedObjective:
      'Nhấn mạnh kinh nghiệm xây dựng API, cơ sở dữ liệu, hiệu năng hệ thống, bảo mật và khả năng triển khai dịch vụ ổn định.',
    suggestedSkills: ['Laravel', 'REST API', 'MySQL/PostgreSQL', 'Redis', 'Docker'],
  },
  frontend_mobile: {
    template: 'topcv_maroon',
    suggestedTitle: 'CV Frontend / Mobile Developer',
    suggestedObjective:
      'Tập trung vào trải nghiệm người dùng, giao diện responsive, khả năng triển khai tính năng end-to-end và phối hợp chặt với backend, product, design.',
    suggestedSkills: ['Vue.js / React', 'Flutter / Swift', 'Responsive UI', 'State management', 'API integration'],
  },
  data_analyst: {
    template: 'ats_serif',
    suggestedTitle: 'CV Data Analyst',
    suggestedObjective:
      'Làm nổi bật tư duy phân tích dữ liệu, xây dashboard, trực quan hóa insight và hỗ trợ ra quyết định dựa trên số liệu.',
    suggestedSkills: ['SQL', 'Power BI / Tableau', 'Excel', 'Python', 'Data visualization'],
  },
  product_manager: {
    template: 'executive_navy',
    suggestedTitle: 'CV Product Manager / Business Analyst',
    suggestedObjective:
      'Nhấn mạnh khả năng phân tích người dùng, ưu tiên backlog, phối hợp stakeholder và dẫn dắt sản phẩm từ ý tưởng đến phát hành.',
    suggestedSkills: ['Product strategy', 'Backlog prioritization', 'Stakeholder management', 'Agile', 'User research'],
  },
  product_designer: {
    template: 'topcv_maroon',
    suggestedTitle: 'CV Product Designer / UI UX',
    suggestedObjective:
      'Nhấn mạnh case study, hiểu người dùng, wireframe, prototype và khả năng triển khai design system nhất quán.',
    suggestedSkills: ['Figma', 'Wireframing', 'Prototype', 'User research', 'Design system'],
  },
  digital_marketer: {
    template: 'topcv_maroon',
    suggestedTitle: 'CV Digital Marketer',
    suggestedObjective:
      'Tập trung vào planning chiến dịch, tối ưu hiệu quả chuyển đổi, đo lường KPI và triển khai đa kênh marketing.',
    suggestedSkills: ['Performance marketing', 'SEO/Content', 'Google Analytics', 'Campaign planning', 'Social media'],
  },
  hr_recruiter: {
    template: 'executive_navy',
    suggestedTitle: 'CV HR / Recruiter',
    suggestedObjective:
      'Làm rõ khả năng tuyển dụng đầu cuối, sàng lọc hồ sơ, phối hợp phỏng vấn và vận hành quy trình nhân sự hiệu quả.',
    suggestedSkills: ['Talent sourcing', 'Interview coordination', 'Employer branding', 'Communication', 'Process management'],
  },
  finance_accounting: {
    template: 'executive_navy',
    suggestedTitle: 'CV Finance / Accounting',
    suggestedObjective:
      'Ưu tiên độ chính xác, khả năng lập báo cáo, phân tích tài chính, kiểm soát rủi ro và tuân thủ quy trình kế toán.',
    suggestedSkills: ['Financial reporting', 'Accounting', 'Excel', 'Cost control', 'ERP'],
  },
  operations_customer_success: {
    template: 'ats_serif',
    suggestedTitle: 'CV Operations / Customer Success',
    suggestedObjective:
      'Thể hiện khả năng vận hành quy trình, theo dõi KPI dịch vụ, giải quyết vấn đề nhanh và duy trì trải nghiệm khách hàng ổn định.',
    suggestedSkills: ['Process operations', 'Customer support', 'Communication', 'Problem solving', 'CRM'],
  },
}

const resolveIndustryPreset = (industryName) => {
  const normalized = normalizeIndustryName(industryName)
  return industryPresetMatchers.find((item) => item.keywords.some((keyword) => normalized.includes(keyword))) || null
}

export const suggestCvTemplate = (industryName, preference = 'balanced') => {
  const preset = resolveIndustryPreset(industryName)
  if (!preset) {
    const fallback = {
      balanced: 'ats_serif',
      formal: 'executive_navy',
      creative: 'topcv_maroon',
      compact: 'ats_serif',
    }
    return fallback[preference] || fallback.balanced
  }

  return preset.templates?.[preference] || preset.templates?.balanced || DEFAULT_TEMPLATE
}

export const buildCvIndustryPreset = (industryName, preference = 'balanced') => {
  const preset = resolveIndustryPreset(industryName)
  const template = suggestCvTemplate(industryName, preference)

  return {
    template,
    suggestedTitle: preset?.suggestedTitle || 'CV Ứng tuyển chuyên nghiệp',
    suggestedObjective:
      preset?.suggestedObjective ||
      'Tập trung vào điểm mạnh cốt lõi, thành tựu nổi bật và mức độ phù hợp với vị trí mục tiêu.',
    suggestedSkills: preset?.suggestedSkills || ['Giao tiếp', 'Làm việc nhóm', 'Chủ động'],
  }
}

export const suggestCvTemplateByMode = ({
  mode = 'style',
  industryName = '',
  styleFamily = 'executive_navy',
  positionValue = '',
  preference = 'balanced',
} = {}) => {
  if (mode === 'position' && positionValue) {
    return positionPresetMap[positionValue]?.template || suggestCvTemplate(industryName, preference)
  }

  return resolveCvTemplateValue(styleFamily || suggestCvTemplate(industryName, preference))
}

export const buildCvPresetByMode = ({
  mode = 'style',
  industryName = '',
  styleFamily = 'executive_navy',
  positionValue = '',
  preference = 'balanced',
} = {}) => {
  if (mode === 'position' && positionValue && positionPresetMap[positionValue]) {
    const preset = positionPresetMap[positionValue]
    return {
      template: preset.template,
      suggestedTitle: preset.suggestedTitle,
      suggestedObjective: preset.suggestedObjective,
      suggestedSkills: preset.suggestedSkills,
    }
  }

  const preset = buildCvIndustryPreset(industryName, preference)
  return {
    ...preset,
    template: suggestCvTemplateByMode({ mode, industryName, styleFamily, positionValue, preference }),
  }
}

const escapeHtml = (value) =>
  String(value || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')

const renderList = (items, renderItem) => asArray(items).map(renderItem).join('')

const getProfileOwnerData = ({ profile, owner }) => {
  const template = resolveCvTemplateValue(profile?.mau_cv)
  const theme = getCvTemplateTheme(template)
  const fullName = owner?.ho_ten || 'Ứng viên'
  const email = owner?.email || 'Chưa cập nhật email'
  const phone = owner?.so_dien_thoai || 'Chưa cập nhật số điện thoại'
  const avatarUrl = resolveProfileCvAvatarUrl(profile, owner)
  const initials = String(fullName || 'U')
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part.charAt(0).toUpperCase())
    .join('')
  const targetPosition = profile?.vi_tri_ung_tuyen_muc_tieu || 'Đa vị trí'
  const targetIndustry = profile?.ten_nganh_nghe_muc_tieu || 'Chưa cập nhật'

  return {
    template,
    theme,
    fullName,
    email,
    phone,
    avatarUrl,
    initials,
    title: profile?.tieu_de_ho_so || 'Hồ sơ ứng tuyển',
    objective: profile?.muc_tieu_nghe_nghiep || 'Chưa cập nhật mục tiêu nghề nghiệp.',
    summary: profile?.mo_ta_ban_than || 'Chưa cập nhật mô tả bản thân.',
    targetPosition,
    targetIndustry,
    degree: profile?.trinh_do || 'Chưa cập nhật',
    years: String(profile?.kinh_nghiem_nam ?? 0),
    skills: asArray(profile?.ky_nang_json),
    experiences: asArray(profile?.kinh_nghiem_json),
    educations: asArray(profile?.hoc_van_json),
    projects: asArray(profile?.du_an_json),
    certificates: asArray(profile?.chung_chi_json),
  }
}

const buildExecutiveNavyHtml = (data) => `
<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8" />
  <title>${escapeHtml(data.title)}</title>
  <style>
    * { box-sizing: border-box; }
    body { margin: 0; background: #eef1f6; color: #243049; font-family: Arial, sans-serif; }
    .page { width: 980px; margin: 20px auto; background: #fff; box-shadow: 0 12px 36px rgba(36,48,73,.12); }
    .top { background: #2f3557; color: #d7bd79; text-align: center; padding: 28px 32px 24px; }
    .top h1 { margin: 0; font-size: 34px; letter-spacing: .18em; font-weight: 500; text-transform: uppercase; }
    .line { width: 150px; height: 2px; background: #d7bd79; margin: 16px auto 12px; position: relative; }
    .line::after { content: ""; width: 14px; height: 14px; border: 2px solid #d7bd79; background: #2f3557; position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%) rotate(45deg); }
    .subtitle { margin: 0; font-size: 14px; letter-spacing: .25em; text-transform: uppercase; }
    .layout { display: grid; grid-template-columns: 270px 1fr; }
    .sidebar { padding: 24px 22px 28px; border-right: 1px solid #d7dbe7; }
    .main { padding: 24px 28px 28px; }
    .section { margin-bottom: 24px; }
    .section h2 { margin: 0 0 10px; font-size: 13px; letter-spacing: .18em; text-transform: uppercase; color: #4b5875; }
    .section .rule { height: 1px; background: #d7dbe7; margin-bottom: 12px; }
    .small { font-size: 13px; line-height: 1.7; color: #243049; }
    .muted { color: #6b7280; }
    .job { margin-bottom: 16px; }
    .job-title { font-weight: 700; font-size: 14px; }
    .company { font-weight: 700; margin-top: 2px; }
    .period { font-size: 12px; color: #6b7280; margin-top: 2px; }
    ul { margin: 8px 0 0 18px; padding: 0; }
    li { margin: 5px 0; line-height: 1.65; }
    .chip { display: inline-block; margin: 0 6px 6px 0; padding: 5px 10px; border: 1px solid #d7dbe7; border-radius: 999px; font-size: 12px; }
    @media print {
      body { background: #fff; }
      .page { margin: 0; width: auto; box-shadow: none; }
    }
  </style>
</head>
<body>
  <div class="page">
    <div class="top">
      <h1>${escapeHtml(data.fullName)}</h1>
      <div class="line"></div>
      <p class="subtitle">${escapeHtml(data.title)}</p>
    </div>
    <div class="layout">
      <aside class="sidebar">
        <div class="section">
          <h2>Liên lạc</h2>
          <div class="rule"></div>
          <div class="small">
            <div>${escapeHtml(data.phone)}</div>
            <div>${escapeHtml(data.email)}</div>
            <div>${escapeHtml(data.targetPosition)}</div>
            <div>${escapeHtml(data.targetIndustry)}</div>
          </div>
        </div>
        <div class="section">
          <h2>Học vấn</h2>
          <div class="rule"></div>
          ${renderList(data.educations, (item) => `
            <div class="small" style="margin-bottom: 12px;">
              <div><strong>${escapeHtml(item?.truong || '')}</strong></div>
              <div>${escapeHtml(item?.chuyen_nganh || '')}</div>
              <div class="muted">${escapeHtml(formatCvPeriod(item?.bat_dau, item?.ket_thuc))}</div>
            </div>
          `) || '<div class="small muted">Chưa cập nhật học vấn.</div>'}
        </div>
        <div class="section">
          <h2>Kỹ năng</h2>
          <div class="rule"></div>
          <div>${renderList(data.skills, (item) => `<span class="chip">${escapeHtml(item?.ten || '')}</span>` ) || '<div class="small muted">Chưa cập nhật kỹ năng.</div>'}</div>
        </div>
        <div class="section">
          <h2>Chứng chỉ</h2>
          <div class="rule"></div>
          ${renderList(data.certificates, (item) => `
            <div class="small" style="margin-bottom: 10px;">
              <div><strong>${escapeHtml(item?.ten || '')}</strong></div>
              <div>${escapeHtml(item?.don_vi || '')}</div>
              <div class="muted">${escapeHtml(item?.nam || '')}</div>
            </div>
          `) || '<div class="small muted">Chưa cập nhật chứng chỉ.</div>'}
        </div>
      </aside>
      <main class="main">
        <div class="section">
          <h2>Giới thiệu</h2>
          <div class="rule"></div>
          <div class="small">${escapeHtml(data.summary)}</div>
        </div>
        <div class="section">
          <h2>Kinh nghiệm làm việc</h2>
          <div class="rule"></div>
          ${renderList(data.experiences, (item) => `
            <div class="job">
              <div class="job-title">${escapeHtml(item?.vi_tri || '')}</div>
              <div class="company">${escapeHtml(item?.cong_ty || '')}</div>
              <div class="period">${escapeHtml(formatCvPeriod(item?.bat_dau, item?.ket_thuc))}</div>
              ${item?.mo_ta ? `<div class="small" style="margin-top: 8px;">${escapeHtml(item.mo_ta)}</div>` : ''}
            </div>
          `) || '<div class="small muted">Chưa cập nhật kinh nghiệm làm việc.</div>'}
        </div>
        <div class="section">
          <h2>Dự án nổi bật</h2>
          <div class="rule"></div>
          ${renderList(data.projects, (item) => `
            <div class="job">
              <div class="job-title">${escapeHtml(item?.ten || '')}</div>
              <div class="company">${escapeHtml(item?.vai_tro || '')}</div>
              <div class="small" style="margin-top: 6px;">${escapeHtml(item?.mo_ta || '')}</div>
            </div>
          `) || '<div class="small muted">Chưa cập nhật dự án.</div>'}
        </div>
      </main>
    </div>
  </div>
  <script>window.onload = () => window.print();</script>
</body>
</html>`

const buildTopcvMaroonHtml = (data) => `
<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8" />
  <title>${escapeHtml(data.title)}</title>
  <style>
    * { box-sizing: border-box; }
    body { margin: 0; background: #efe7e7; color: #201b1c; font-family: Arial, sans-serif; }
    .page { width: 980px; margin: 20px auto; background: #fff; box-shadow: 0 12px 36px rgba(42,37,38,.12); }
    .layout { display: grid; grid-template-columns: 320px 1fr; }
    .sidebar { background: #5b3133; color: #fff; min-height: 100%; }
    .hero { background: #a45a5d; padding: 28px 26px 22px; text-align: center; }
    .avatar { width: 220px; height: 220px; margin: 0 auto 18px; border-radius: 999px; overflow: hidden; background: #fff; display: flex; align-items: center; justify-content: center; color: #5b3133; font-size: 52px; font-weight: 700; }
    .avatar img { width: 100%; height: 100%; object-fit: cover; }
    .hero h1 { margin: 0; font-size: 28px; line-height: 1.2; }
    .hero p { margin: 8px 0 0; font-size: 16px; opacity: .92; }
    .sidebar-body { padding: 18px 26px 28px; }
    .section { margin-bottom: 22px; }
    .section h2 { margin: 0 0 12px; font-size: 13px; text-transform: none; color: #fff; }
    .section p, .section li, .section div { font-size: 13px; line-height: 1.7; }
    .contact-item { margin-bottom: 8px; }
    .skill-row { margin-bottom: 12px; }
    .skill-row span { display: block; margin-bottom: 6px; }
    .bar { height: 12px; background: rgba(255,255,255,.22); overflow: hidden; }
    .bar > b { display: block; height: 100%; background: #d98a8f; }
    .main { padding: 30px 34px 28px; }
    .main-section { margin-bottom: 24px; }
    .main-section h2 { margin: 0 0 12px; font-size: 18px; color: #1f1a1b; }
    .entry { margin-bottom: 20px; }
    .row { display: flex; justify-content: space-between; gap: 12px; }
    .title { font-size: 16px; font-weight: 700; }
    .company { margin-top: 4px; font-size: 14px; font-weight: 700; }
    .period { color: #555; font-size: 13px; }
    ul { margin: 8px 0 0 18px; padding: 0; }
    li { margin: 4px 0; line-height: 1.65; }
    @media print {
      body { background: #fff; }
      .page { margin: 0; width: auto; box-shadow: none; }
    }
  </style>
</head>
<body>
  <div class="page">
    <div class="layout">
      <aside class="sidebar">
        <div class="hero">
          <div class="avatar">
            ${data.avatarUrl ? `<img src="${escapeHtml(data.avatarUrl)}" alt="avatar" />` : escapeHtml(data.initials)}
          </div>
          <h1>${escapeHtml(data.fullName)}</h1>
          <p>${escapeHtml(data.title)}</p>
        </div>
        <div class="sidebar-body">
          <div class="section">
            <div class="contact-item">${escapeHtml(data.phone)}</div>
            <div class="contact-item">${escapeHtml(data.email)}</div>
            <div class="contact-item">${escapeHtml(data.targetIndustry)}</div>
            <div class="contact-item">${escapeHtml(data.targetPosition)}</div>
          </div>
          <div class="section">
            <h2>Mục tiêu nghề nghiệp</h2>
            <div>${escapeHtml(data.objective)}</div>
          </div>
          <div class="section">
            <h2>Kỹ năng</h2>
            ${renderList(data.skills.slice(0, 5), (item) => `
              <div class="skill-row">
                <span>${escapeHtml(item?.ten || '')}</span>
                <div class="bar"><b style="width:${cvSkillLevelPercent(item?.muc_do)}%"></b></div>
              </div>
            `) || '<div>Chưa cập nhật kỹ năng.</div>'}
          </div>
          <div class="section">
            <h2>Chứng chỉ / Dự án</h2>
            ${renderList(data.certificates.slice(0, 2), (item) => `<div style="margin-bottom: 8px;"><strong>${escapeHtml(item?.ten || '')}</strong><div>${escapeHtml(item?.don_vi || '')}</div></div>`)}
            ${renderList(data.projects.slice(0, 2), (item) => `<div style="margin-bottom: 8px;"><strong>${escapeHtml(item?.ten || '')}</strong><div>${escapeHtml(item?.vai_tro || '')}</div></div>`)}
            ${!data.certificates.length && !data.projects.length ? '<div>Chưa cập nhật chứng chỉ hoặc dự án.</div>' : ''}
          </div>
        </div>
      </aside>
      <main class="main">
        <section class="main-section">
          <h2>Học vấn</h2>
          ${renderList(data.educations, (item) => `
            <div class="entry">
              <div class="row">
                <div>
                  <div class="title">${escapeHtml(item?.chuyen_nganh || 'Chưa cập nhật chuyên ngành')}</div>
                  <div class="company">${escapeHtml(item?.truong || '')}</div>
                </div>
                <div class="period">${escapeHtml(formatCvPeriod(item?.bat_dau, item?.ket_thuc))}</div>
              </div>
              ${item?.mo_ta ? `<div style="margin-top: 6px; line-height: 1.65;">${escapeHtml(item.mo_ta)}</div>` : ''}
            </div>
          `) || '<div>Chưa cập nhật học vấn.</div>'}
        </section>
        <section class="main-section">
          <h2>Kinh nghiệm làm việc</h2>
          ${renderList(data.experiences, (item) => `
            <div class="entry">
              <div class="row">
                <div>
                  <div class="title">${escapeHtml(item?.vi_tri || '')}</div>
                  <div class="company">${escapeHtml(item?.cong_ty || '')}</div>
                </div>
                <div class="period">${escapeHtml(formatCvPeriod(item?.bat_dau, item?.ket_thuc))}</div>
              </div>
              ${item?.mo_ta ? `<div style="margin-top: 8px; line-height: 1.7;">${escapeHtml(item.mo_ta)}</div>` : ''}
            </div>
          `) || '<div>Chưa cập nhật kinh nghiệm làm việc.</div>'}
        </section>
        <section class="main-section">
          <h2>Dự án nổi bật</h2>
          ${renderList(data.projects, (item) => `
            <div class="entry">
              <div class="row">
                <div>
                  <div class="title">${escapeHtml(item?.ten || '')}</div>
                  <div class="company">${escapeHtml(item?.vai_tro || '')}</div>
                </div>
                <div class="period">${escapeHtml(item?.cong_nghe || '')}</div>
              </div>
              ${item?.mo_ta ? `<div style="margin-top: 8px; line-height: 1.7;">${escapeHtml(item.mo_ta)}</div>` : ''}
            </div>
          `) || '<div>Chưa cập nhật dự án.</div>'}
        </section>
      </main>
    </div>
  </div>
  <script>window.onload = () => window.print();</script>
</body>
</html>`

const buildAtsSerifHtml = (data) => `
<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8" />
  <title>${escapeHtml(data.title)}</title>
  <style>
    * { box-sizing: border-box; }
    body { margin: 0; background: #f4f4f4; color: #111; font-family: Georgia, "Times New Roman", serif; }
    .page { width: 960px; margin: 20px auto; background: #fff; box-shadow: 0 10px 30px rgba(0,0,0,.08); padding: 40px 56px 56px; }
    .name { font-size: 28px; font-weight: 700; margin: 0; }
    .contact { margin-top: 8px; line-height: 1.5; font-size: 15px; }
    .section { margin-top: 28px; }
    .section h2 { margin: 0 0 8px; font-size: 19px; font-weight: 700; }
    .rule { height: 1px; background: #bdbdbd; margin-bottom: 14px; }
    .text { white-space: pre-wrap; line-height: 1.55; font-size: 14px; }
    .entry { margin-bottom: 18px; }
    .entry-title { font-size: 16px; font-weight: 700; }
    .entry-sub { font-size: 15px; font-weight: 700; margin-top: 2px; }
    .meta { color: #444; margin-top: 2px; font-size: 14px; }
    ul { margin: 8px 0 0 24px; padding: 0; }
    li { margin: 4px 0; line-height: 1.55; font-size: 14px; }
    .skills { font-size: 15px; line-height: 1.6; }
    @media print {
      body { background: #fff; }
      .page { margin: 0; width: auto; box-shadow: none; }
    }
  </style>
</head>
<body>
  <div class="page">
    <h1 class="name">${escapeHtml(data.fullName)}</h1>
    <div class="contact">${escapeHtml(data.targetIndustry)} | ${escapeHtml(data.phone)}<br />${escapeHtml(data.email)}</div>

    <section class="section">
      <h2>Summary</h2>
      <div class="rule"></div>
      <div class="text">${escapeHtml(data.summary || data.objective)}</div>
    </section>

    <section class="section">
      <h2>Experience</h2>
      <div class="rule"></div>
      ${renderList(data.experiences, (item) => `
        <div class="entry">
          <div class="entry-title">${escapeHtml(item?.vi_tri || '')}</div>
          <div class="entry-sub">${escapeHtml(item?.cong_ty || 'Personal Projects')}</div>
          <div class="meta">${escapeHtml(formatCvPeriod(item?.bat_dau, item?.ket_thuc))}</div>
          ${item?.mo_ta ? `<div class="text" style="margin-top: 6px;">${escapeHtml(item.mo_ta)}</div>` : ''}
        </div>
      `) || '<div class="text">Chưa cập nhật kinh nghiệm.</div>'}
    </section>

    <section class="section">
      <h2>Skills</h2>
      <div class="rule"></div>
      <div class="skills">${data.skills.map((item) => escapeHtml(item?.ten || '')).join(', ') || 'Chưa cập nhật kỹ năng.'}</div>
    </section>

    <section class="section">
      <h2>Education</h2>
      <div class="rule"></div>
      ${renderList(data.educations, (item) => `
        <div class="entry">
          <div class="entry-title">${escapeHtml(item?.truong || '')}</div>
          <div class="entry-sub">${escapeHtml(item?.chuyen_nganh || '')} | ${escapeHtml(formatCvPeriod(item?.bat_dau, item?.ket_thuc))}</div>
          ${item?.mo_ta ? `<div class="text" style="margin-top: 6px;">${escapeHtml(item.mo_ta)}</div>` : ''}
        </div>
      `) || '<div class="text">Chưa cập nhật học vấn.</div>'}
    </section>

    <section class="section">
      <h2>Projects & Certifications</h2>
      <div class="rule"></div>
      ${renderList(data.projects, (item) => `
        <div class="entry">
          <div class="entry-title">${escapeHtml(item?.ten || '')}</div>
          <div class="meta">${escapeHtml(item?.cong_nghe || '')}${item?.vai_tro ? ` | ${escapeHtml(item.vai_tro)}` : ''}</div>
          ${item?.mo_ta ? `<div class="text" style="margin-top: 6px;">${escapeHtml(item.mo_ta)}</div>` : ''}
        </div>
      `)}
      ${renderList(data.certificates, (item) => `
        <div class="entry">
          <div class="entry-title">${escapeHtml(item?.ten || '')}</div>
          <div class="meta">${escapeHtml(item?.don_vi || '')}${item?.nam ? ` | ${escapeHtml(item.nam)}` : ''}</div>
        </div>
      `) || (!data.projects.length ? '<div class="text">Chưa cập nhật dự án hoặc chứng chỉ.</div>' : '')}
    </section>
  </div>
  <script>window.onload = () => window.print();</script>
</body>
</html>`

export const buildProfileCvPrintHtml = ({ profile, owner }) => {
  const data = getProfileOwnerData({ profile, owner })

  switch (data.template) {
    case 'topcv_maroon':
      return buildTopcvMaroonHtml(data)
    case 'ats_serif':
      return buildAtsSerifHtml(data)
    case 'executive_navy':
    default:
      return buildExecutiveNavyHtml(data)
  }
}
