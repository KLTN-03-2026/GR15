export const ADMIN_SCOPE_SUPER_ADMIN = 'super_admin'

export const ADMIN_PERMISSION_DEFINITIONS = [
  {
    key: 'users',
    label: 'Người dùng',
    description: 'Quản lý tài khoản người dùng thường trên toàn hệ thống.',
  },
  {
    key: 'companies',
    label: 'Công ty',
    description: 'Quản lý thông tin và trạng thái công ty.',
  },
  {
    key: 'profiles',
    label: 'Hồ sơ',
    description: 'Quản lý hồ sơ ứng viên và dữ liệu đã lưu trữ.',
  },
  {
    key: 'user_skills',
    label: 'Kỹ năng người dùng',
    description: 'Theo dõi kỹ năng ứng viên đang khai báo.',
  },
  {
    key: 'matchings',
    label: 'AI Matching',
    description: 'Xem kết quả và thống kê matching.',
  },
  {
    key: 'career_advising',
    label: 'AI Advising',
    description: 'Theo dõi báo cáo tư vấn nghề nghiệp AI.',
  },
  {
    key: 'ai_usage',
    label: 'AI Usage',
    description: 'Theo dõi lượng dùng và log AI.',
  },
  {
    key: 'billing',
    label: 'Billing',
    description: 'Quản lý giao dịch, gói dịch vụ và bảng giá.',
  },
  {
    key: 'applications',
    label: 'Ứng tuyển',
    description: 'Theo dõi đơn ứng tuyển toàn hệ thống.',
  },
  {
    key: 'skills',
    label: 'Kỹ năng',
    description: 'Quản trị danh mục kỹ năng dùng chung.',
  },
  {
    key: 'industries',
    label: 'Ngành nghề',
    description: 'Quản trị danh mục ngành nghề.',
  },
  {
    key: 'jobs',
    label: 'Tin tuyển dụng',
    description: 'Quản lý tin tuyển dụng trên nền tảng.',
  },
  {
    key: 'cv_templates',
    label: 'Template CV',
    description: 'Quản lý thư viện mẫu CV.',
  },
  {
    key: 'audit_logs',
    label: 'Nhật ký hệ thống',
    description: 'Xem audit log và lịch sử thao tác quản trị.',
  },
  {
    key: 'stats',
    label: 'Báo cáo & phân tích',
    description: 'Xem báo cáo tổng hợp về ứng tuyển, lưu tin và hiệu suất AI.',
  },
]

export const ADMIN_PERMISSION_DEFAULTS = Object.fromEntries(
  ADMIN_PERMISSION_DEFINITIONS.map((permission) => [permission.key, false]),
)

export const normalizeAdminPermissions = (permissions = {}) => {
  const normalized = { ...ADMIN_PERMISSION_DEFAULTS }

  Object.keys(ADMIN_PERMISSION_DEFAULTS).forEach((key) => {
    if (Object.prototype.hasOwnProperty.call(permissions || {}, key)) {
      normalized[key] = Boolean(permissions[key])
    }
  })

  return normalized
}

export const hasAdminPermission = (user, permission) => {
  if (Number(user?.vai_tro) !== 2) return false
  if (user?.cap_admin === ADMIN_SCOPE_SUPER_ADMIN) return true
  if (!permission) return true

  const permissions = normalizeAdminPermissions(user?.quyen_admin)
  return permissions[permission] === true
}

export const getGrantedAdminPermissionCount = (user) => {
  return Object.values(normalizeAdminPermissions(user?.quyen_admin)).filter(Boolean).length
}
