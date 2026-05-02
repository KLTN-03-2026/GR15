/**
 * API Service
 * Quản lý tất cả các request đến Backend
 */

import { clearAuthStorage, getAuthToken } from '@/utils/authStorage'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

const buildHeaders = (options = {}) => {
  const isFormData = options.body instanceof FormData
  const headers = {
    ...options.headers,
  }

  if (!isFormData) {
    headers['Content-Type'] = headers['Content-Type'] || 'application/json'
  }

  const token = getAuthToken()
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  return headers
}

const handleUnauthorized = () => {
  if (typeof window === 'undefined') return

  clearAuthStorage()
  window.dispatchEvent(new Event('auth-invalidated'))
}

// Hàm fetch chung
const apiCall = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`
  const headers = buildHeaders(options)

  try {
    const response = await fetch(url, {
      ...options,
      headers
    })

    // Kiểm tra content type
    const contentType = response.headers.get('content-type')
    let data = null

    if (contentType && contentType.includes('application/json')) {
      data = await response.json()
    } else {
      const text = await response.text()
      if (!response.ok) {
        throw {
          status: response.status,
          message: `API Error: ${response.status} ${response.statusText}`,
          details: text.substring(0, 200)
        }
      }
      return { data: {} }
    }

    if (!response.ok) {
      if (response.status === 401) {
        handleUnauthorized()
      }
      throw {
        status: response.status,
        message: data.message || `Lỗi ${response.status}: ${response.statusText}`,
        code: data.code || null,
        errors: data.errors || null,
        requiredRoles: data.required_roles || null,
        requiredRoleLabels: data.required_role_labels || null,
        currentRole: data.current_role || null,
        currentRoleLabel: data.current_role_label || null,
        requiredCompanyRoles: data.required_company_roles || null,
        requiredCompanyRoleLabels: data.required_company_role_labels || null,
        currentCompanyRole: data.current_company_role || null,
        currentCompanyRoleLabel: data.current_company_role_label || null,
        data
      }
    }

    return data
  } catch (err) {
    // Nếu lỗi network
    if (err instanceof TypeError) {
      throw {
        status: 0,
        message: 'Không thể kết nối đến API. Kiểm tra:\n1. Backend đang chạy tại ' + API_BASE_URL + '\n2. CORS được bật\n3. Network connection',
        error: err.message
      }
    }
    throw err
  }
}

const parseFilename = (disposition) => {
  if (!disposition) return ''
  const utf8Match = disposition.match(/filename\*=UTF-8''([^;]+)/i)
  if (utf8Match?.[1]) return decodeURIComponent(utf8Match[1].replace(/"/g, ''))
  const match = disposition.match(/filename="?([^"]+)"?/i)
  return match?.[1] || ''
}

const blobApiCall = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`
  const headers = buildHeaders({
    ...options,
    headers: {
      Accept: 'application/pdf',
      ...(options.headers || {}),
    },
  })
  delete headers['Content-Type']

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    })

    if (!response.ok) {
      if (response.status === 401) {
        handleUnauthorized()
      }

      const contentType = response.headers.get('content-type') || ''
      let message = `Lỗi ${response.status}: ${response.statusText}`

      if (contentType.includes('application/json')) {
        const data = await response.json()
        message = data?.message || message
        throw { status: response.status, message, data }
      }

      const text = await response.text()
      throw { status: response.status, message: text || message }
    }

    return {
      blob: await response.blob(),
      filename: parseFilename(response.headers.get('content-disposition')),
    }
  } catch (err) {
    if (err instanceof TypeError) {
      throw {
        status: 0,
        message: 'Không thể tải file từ API. Kiểm tra backend và kết nối mạng.',
        error: err.message,
      }
    }
    throw err
  }
}

const streamApiCall = async (endpoint, options = {}, handlers = {}) => {
  const url = `${API_BASE_URL}${endpoint}`
  const headers = buildHeaders(options)

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    })

    if (!response.ok) {
      if (response.status === 401) {
        handleUnauthorized()
      }

      const contentType = response.headers.get('content-type') || ''
      let message = `Lỗi ${response.status}: ${response.statusText}`

      if (contentType.includes('application/json')) {
        const data = await response.json()
        message = data?.message || message
        throw {
          status: response.status,
          message,
          code: data?.code || null,
          errors: data?.errors || null,
          data,
        }
      } else {
        const text = await response.text()
        message = text || message
      }

      throw {
        status: response.status,
        message,
      }
    }

    if (!response.body) {
      throw {
        status: 0,
        message: 'Trình duyệt không hỗ trợ stream response.',
      }
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''

    const dispatchEvent = (eventName, payload) => {
      handlers.onEvent?.(eventName, payload)

      if (eventName === 'meta') handlers.onMeta?.(payload)
      if (eventName === 'chunk') handlers.onChunk?.(payload)
      if (eventName === 'done') handlers.onDone?.(payload)
      if (eventName === 'error') handlers.onError?.(payload)
    }

    const processBuffer = () => {
      const events = buffer.split(/\n\n/)
      buffer = events.pop() || ''

      for (const rawEvent of events) {
        const lines = rawEvent.split(/\r?\n/)
        let eventName = 'message'
        const dataLines = []

        for (const line of lines) {
          if (line.startsWith('event:')) {
            eventName = line.slice(6).trim()
          }

          if (line.startsWith('data:')) {
            dataLines.push(line.slice(5).trim())
          }
        }

        if (!dataLines.length) continue

        const rawPayload = dataLines.join('\n')
        let payload = rawPayload

        try {
          payload = JSON.parse(rawPayload)
        } catch {
          payload = { message: rawPayload }
        }

        dispatchEvent(eventName, payload)
      }
    }

    while (true) {
      const { done, value } = await reader.read()

      if (done) {
        buffer += decoder.decode()
        processBuffer()
        break
      }

      buffer += decoder.decode(value, { stream: true })
      processBuffer()
    }

    return true
  } catch (err) {
    if (err instanceof TypeError) {
      throw {
        status: 0,
        message: 'Không thể kết nối đến API stream. Vui lòng kiểm tra backend hoặc network.',
        error: err.message,
      }
    }

    throw err
  }
}

const createIdempotencyKey = (prefix = 'request') => {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return `${prefix}-${crypto.randomUUID()}`
  }

  return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2)}`
}

// === Auth APIs ===
export const authService = {
  // Guest/Candidate registration
  registerCandidate: (fullName, email, phone, password, confirmPassword) =>
    apiCall('/dang-ky', {
      method: 'POST',
      body: JSON.stringify({
        ho_ten: fullName,
        email,
        so_dien_thoai: phone,
        mat_khau: password,
        mat_khau_confirmation: confirmPassword,
        vai_tro: 0,
      })
    }),

  // Guest login
  login: (email, password) =>
    apiCall('/dang-nhap', {
      method: 'POST',
      body: JSON.stringify({
        email,
        mat_khau: password,
      })
    }),

  // Employer registration
  registerEmployer: (companyName, contactPerson, email, phone, password, confirmPassword) =>
    apiCall('/dang-ky', {
      method: 'POST',
      body: JSON.stringify({
        ho_ten: contactPerson,
        ten_cong_ty: companyName,
        email,
        so_dien_thoai: phone,
        mat_khau: password,
        mat_khau_confirmation: confirmPassword,
        vai_tro: 1,
      })
    }),

  getGoogleAuthUrl: (roleHint = 0, redirect = '') => {
    const params = new URLSearchParams()
    params.set('role_hint', String(roleHint))

    if (redirect) {
      params.set('redirect', redirect)
    }

    return `${API_BASE_URL}/auth/google/redirect?${params.toString()}`
  },

  logout: () =>
    apiCall('/dang-xuat', {
      method: 'POST'
    }),

  getProfile: () =>
    apiCall('/ho-so', {
      method: 'GET'
    }),

  updateProfile: (data) =>
    (() => {
      if (data instanceof FormData) {
        const payload = new FormData()

        for (const [key, value] of data.entries()) {
          payload.append(key, value)
        }

        payload.append('_method', 'PUT')

        return apiCall('/ho-so', {
          method: 'POST',
          body: payload,
        })
      }

      return apiCall('/ho-so', {
        method: 'PUT',
        body: JSON.stringify(data)
      })
    })(),

  changePassword: (oldPassword, newPassword, confirmPassword) =>
    apiCall('/doi-mat-khau', {
      method: 'POST',
      body: JSON.stringify({
        mat_khau_cu: oldPassword,
        mat_khau_moi: newPassword,
        mat_khau_moi_confirmation: confirmPassword,
      })
    }),

  forgotPassword: (email) =>
    apiCall('/quen-mat-khau', {
      method: 'POST',
      body: JSON.stringify({ email })
    }),

  resetPassword: ({ email, token, password, confirmPassword }) =>
    apiCall('/dat-lai-mat-khau', {
      method: 'POST',
      body: JSON.stringify({
        email,
        token,
        mat_khau: password,
        mat_khau_confirmation: confirmPassword,
      })
    }),

  resendVerificationEmail: (email) =>
    apiCall('/gui-lai-email-xac-thuc', {
      method: 'POST',
      body: JSON.stringify({ email })
    })
}

// === Admin User APIs ===
export const userService = {
  // Lấy danh sách người dùng với phân trang & filter
  getUsers: (options = {}) => {
    const params = new URLSearchParams()
    if (options.page) params.append('page', options.page)
    if (options.per_page) params.append('per_page', options.per_page)
    if (options.vai_tro !== undefined) params.append('vai_tro', options.vai_tro)
    if (options.trang_thai !== undefined) params.append('trang_thai', options.trang_thai)
    if (options.search) params.append('search', options.search)
    
    // Thêm sort parameters
    params.append('sort_by', options.sort_by || 'created_at')
    params.append('sort_dir', options.sort_dir || 'desc')

    const query = params.toString()
    const endpoint = `/admin/nguoi-dungs${query ? '?' + query : ''}`

    return apiCall(endpoint, {
      method: 'GET'
    })
  },

  // Lấy thống kê người dùng
  getUserStats: () =>
    apiCall('/admin/nguoi-dungs/thong-ke', {
      method: 'GET'
    }),

  // Lấy chi tiết người dùng
  getUserById: (id) =>
    apiCall(`/admin/nguoi-dungs/${id}`, {
      method: 'GET'
    }),

  // Tạo người dùng mới
  createUser: (data) =>
    apiCall('/admin/nguoi-dungs', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  // Cập nhật người dùng
  updateUser: (id, data) =>
    apiCall(`/admin/nguoi-dungs/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    }),

  // Đặt lại mật khẩu
  resetPassword: (id, mat_khau) =>
    apiCall(`/admin/nguoi-dungs/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ mat_khau })
    }),

  // Toggle khoá/mở khoá tài khoản
  toggleLock: (id) =>
    apiCall(`/admin/nguoi-dungs/${id}/khoa`, {
      method: 'PATCH'
    }),

  // Xoá người dùng
  deleteUser: (id) =>
    apiCall(`/admin/nguoi-dungs/${id}`, {
      method: 'DELETE'
    })
}

export const adminAccountService = {
  getAdmins: (options = {}) => {
    const params = new URLSearchParams()
    if (options.page) params.append('page', options.page)
    if (options.per_page) params.append('per_page', options.per_page)
    if (options.search) params.append('search', options.search)
    if (options.trang_thai !== undefined && options.trang_thai !== null && options.trang_thai !== '') {
      params.append('trang_thai', options.trang_thai)
    }
    if (options.cap_admin) params.append('cap_admin', options.cap_admin)
    params.append('sort_by', options.sort_by || 'created_at')
    params.append('sort_dir', options.sort_dir || 'desc')

    const query = params.toString()
    return apiCall(`/admin/admins${query ? `?${query}` : ''}`, {
      method: 'GET',
    })
  },

  getAdminStats: () =>
    apiCall('/admin/admins/thong-ke', {
      method: 'GET',
    }),

  getAdminById: (id) =>
    apiCall(`/admin/admins/${id}`, {
      method: 'GET',
    }),

  getAdminPermissions: (id) =>
    apiCall(`/admin/admins/${id}/permissions`, {
      method: 'GET',
    }),

  createAdmin: (payload) =>
    apiCall('/admin/admins', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  updateAdmin: (id, payload) =>
    apiCall(`/admin/admins/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    }),

  updateAdminPermissions: (id, permissions) =>
    apiCall(`/admin/admins/${id}/permissions`, {
      method: 'PUT',
      body: JSON.stringify({ quyen_admin: permissions }),
    }),

  createAdminPermissionDefinition: (payload) =>
    apiCall('/admin/admins/permissions/definitions', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  toggleAdminLock: (id) =>
    apiCall(`/admin/admins/${id}/khoa`, {
      method: 'PATCH',
    }),

  deleteAdmin: (id) =>
    apiCall(`/admin/admins/${id}`, {
      method: 'DELETE',
    }),
}

// === Admin Company APIs ===
export const companyService = {
  // Lấy danh sách công ty
  getCompanies: (options = {}) => {
    const params = new URLSearchParams()
    if (options.page) params.append('page', options.page)
    if (options.per_page) params.append('per_page', options.per_page)
    if (options.search) params.append('search', options.search)
    if (options.trang_thai !== undefined && options.trang_thai !== null && options.trang_thai !== '') {
      params.append('trang_thai', options.trang_thai)
    }
    
    params.append('sort_by', options.sort_by || 'created_at')
    params.append('sort_dir', options.sort_dir || 'desc')

    const query = params.toString()
    const endpoint = `/admin/cong-tys${query ? '?' + query : ''}`

    return apiCall(endpoint, {
      method: 'GET'
    })
  },

  // Lấy thống kê công ty
  getCompanyStats: () =>
    apiCall('/admin/cong-tys/thong-ke', {
      method: 'GET'
    }),

  // Lấy chi tiết công ty
  getCompanyById: (id) =>
    apiCall(`/admin/cong-tys/${id}`, {
      method: 'GET'
    }),

  // Tạo công ty
  createCompany: (data) =>
    apiCall('/admin/cong-tys', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  // Cập nhật công ty
  updateCompany: (id, data) =>
    apiCall(`/admin/cong-tys/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    }),

  // Đổi trạng thái duyệt công ty
  toggleCompanyStatus: (id) =>
    apiCall(`/admin/cong-tys/${id}/trang-thai`, {
      method: 'PATCH'
    }),

  // Xoá công ty
  deleteCompany: (id) =>
    apiCall(`/admin/cong-tys/${id}`, {
      method: 'DELETE'
    })
}

export const adminMarketService = {
  getDashboard: () =>
    apiCall('/admin/thi-truong/dashboard', {
      method: 'GET',
    }),
}

export const adminBillingService = {
  getOverview: () =>
    apiCall('/admin/billing/overview', {
      method: 'GET',
    }),

  getPayments: (options = {}) => {
    const params = new URLSearchParams()
    ;['page', 'per_page', 'loai_giao_dich', 'trang_thai', 'gateway', 'q'].forEach((key) => {
      const value = options[key]
      if (value !== undefined && value !== null && value !== '') params.append(key, value)
    })
    const query = params.toString()
    return apiCall(`/admin/billing/payments${query ? `?${query}` : ''}`, {
      method: 'GET',
    })
  },

  getPaymentDetail: (maGiaoDichNoiBo) =>
    apiCall(`/admin/billing/payments/${maGiaoDichNoiBo}`, {
      method: 'GET',
    }),

  reconcilePayment: (maGiaoDichNoiBo) =>
    apiCall(`/admin/billing/payments/${maGiaoDichNoiBo}/reconcile`, {
      method: 'POST',
    }),

  getPlans: () =>
    apiCall('/admin/billing/plans', {
      method: 'GET',
    }),

  createPlan: (payload) =>
    apiCall('/admin/billing/plans', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  updatePlan: (id, payload) =>
    apiCall(`/admin/billing/plans/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    }),

  getPrices: () =>
    apiCall('/admin/billing/prices', {
      method: 'GET',
    }),

  createPrice: (payload) =>
    apiCall('/admin/billing/prices', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  updatePrice: (id, payload) =>
    apiCall(`/admin/billing/prices/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    }),

  getSubscriptions: (options = {}) => {
    const params = new URLSearchParams()
    ;['page', 'per_page', 'trang_thai', 'q'].forEach((key) => {
      const value = options[key]
      if (value !== undefined && value !== null && value !== '') params.append(key, value)
    })
    const query = params.toString()
    return apiCall(`/admin/billing/subscriptions${query ? `?${query}` : ''}`, {
      method: 'GET',
    })
  },
}

const buildAuditLogQuery = (options = {}) => {
  const params = new URLSearchParams()
  const keys = ['page', 'per_page', 'actor_id', 'actor_query', 'actor_role', 'company_id', 'action', 'scope', 'target_type', 'from', 'to']

  keys.forEach((key) => {
    const value = options[key]
    if (value !== undefined && value !== null && value !== '') {
      params.append(key, value)
    }
  })

  return params.toString()
}

export const adminAuditLogService = {
  getLogs: (options = {}) => {
    const query = buildAuditLogQuery(options)
    return apiCall(`/admin/audit-logs${query ? `?${query}` : ''}`, {
      method: 'GET',
    })
  },
}

const buildAiUsageQuery = (options = {}) => {
  const params = new URLSearchParams()
  const keys = [
    'page',
    'per_page',
    'days',
    'feature',
    'status',
    'used_fallback',
    'user_id',
    'company_id',
    'request_ref_type',
    'request_ref_id',
    'from',
    'to',
  ]

  keys.forEach((key) => {
    const value = options[key]
    if (value !== undefined && value !== null && value !== '') {
      params.append(key, value)
    }
  })

  return params.toString()
}

export const adminAiUsageService = {
  getOverview: (options = {}) => {
    const query = buildAiUsageQuery(options)
    return apiCall(`/admin/ai-usage/overview${query ? `?${query}` : ''}`, {
      method: 'GET',
    })
  },

  getLogs: (options = {}) => {
    const query = buildAiUsageQuery(options)
    return apiCall(`/admin/ai-usage/logs${query ? `?${query}` : ''}`, {
      method: 'GET',
    })
  },

  getFeatures: () =>
    apiCall('/admin/ai-usage/features', {
      method: 'GET',
    }),
}

export const notificationService = {
  getNotifications: (options = {}) => {
    const params = new URLSearchParams()
    if (options.page) params.append('page', options.page)
    if (options.per_page) params.append('per_page', options.per_page)
    if (options.type) params.append('type', options.type)
    if (options.unread_only) params.append('unread_only', '1')

    const query = params.toString()
    return apiCall(`/notifications${query ? `?${query}` : ''}`, {
      method: 'GET',
    })
  },

  getUnreadCount: () =>
    apiCall('/notifications/unread-count', {
      method: 'GET',
    }),

  markAsRead: (id) =>
    apiCall(`/notifications/${id}/read`, {
      method: 'PATCH',
    }),

  markAllAsRead: () =>
    apiCall('/notifications/read-all', {
      method: 'PATCH',
    }),
}

export const adminJobPostingService = {
  getJobs: (options = {}) => {
    const params = new URLSearchParams()

    if (options.page) params.append('page', options.page)
    if (options.per_page) params.append('per_page', options.per_page)
    if (options.search) params.append('search', options.search)
    if (options.trang_thai !== '' && options.trang_thai !== undefined && options.trang_thai !== null) {
      params.append('trang_thai', options.trang_thai)
    }
    if (options.cong_ty_id) params.append('cong_ty_id', options.cong_ty_id)

    const query = params.toString()
    return apiCall(`/admin/tin-tuyen-dungs${query ? `?${query}` : ''}`, {
      method: 'GET',
    })
  },

  getStats: () =>
    apiCall('/admin/tin-tuyen-dungs/thong-ke', {
      method: 'GET',
    }),

  updateJob: (id, data) =>
    apiCall(`/admin/tin-tuyen-dungs/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  toggleStatus: (id) =>
    apiCall(`/admin/tin-tuyen-dungs/${id}/trang-thai`, {
      method: 'PATCH',
    }),

  deleteJob: (id) =>
    apiCall(`/admin/tin-tuyen-dungs/${id}`, {
      method: 'DELETE',
    }),
}

export const adminIndustryService = {
  getIndustries: (options = {}) => {
    const params = new URLSearchParams()

    if (options.page) params.append('page', options.page)
    if (options.per_page) params.append('per_page', options.per_page)
    if (options.search) params.append('search', options.search)
    if (options.trang_thai !== '' && options.trang_thai !== undefined && options.trang_thai !== null) {
      params.append('trang_thai', options.trang_thai)
    }
    if (options.danh_muc_cha_id !== '' && options.danh_muc_cha_id !== undefined && options.danh_muc_cha_id !== null) {
      params.append('danh_muc_cha_id', options.danh_muc_cha_id)
    }

    const query = params.toString()
    return apiCall(`/admin/nganh-nghes${query ? `?${query}` : ''}`, {
      method: 'GET',
    })
  },

  getStats: () =>
    apiCall('/admin/nganh-nghes/thong-ke', {
      method: 'GET',
    }),

  createIndustry: (data) =>
    apiCall('/admin/nganh-nghes', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateIndustry: (id, data) =>
    apiCall(`/admin/nganh-nghes/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  toggleStatus: (id) =>
    apiCall(`/admin/nganh-nghes/${id}/trang-thai`, {
      method: 'PATCH',
    }),

  deleteIndustry: (id) =>
    apiCall(`/admin/nganh-nghes/${id}`, {
      method: 'DELETE',
    }),
}

export const adminSkillService = {
  getSkills: (options = {}) => {
    const params = new URLSearchParams()

    if (options.page) params.append('page', options.page)
    if (options.per_page) params.append('per_page', options.per_page)
    if (options.search) params.append('search', options.search)
    if (options.sort_by) params.append('sort_by', options.sort_by)
    if (options.sort_dir) params.append('sort_dir', options.sort_dir)

    const query = params.toString()
    return apiCall(`/admin/ky-nangs${query ? `?${query}` : ''}`, {
      method: 'GET',
    })
  },

  getStats: () =>
    apiCall('/admin/ky-nangs/thong-ke', {
      method: 'GET',
    }),

  createSkill: (data) =>
    apiCall('/admin/ky-nangs', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateSkill: (id, data) =>
    apiCall(`/admin/ky-nangs/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  deleteSkill: (id) =>
    apiCall(`/admin/ky-nangs/${id}`, {
      method: 'DELETE',
    }),
}

export const adminProfileService = {
  getProfiles: (options = {}) => {
    const params = new URLSearchParams()

    if (options.page) params.append('page', options.page)
    if (options.per_page) params.append('per_page', options.per_page)
    if (options.search) params.append('search', options.search)
    if (options.nguoi_dung_id) params.append('nguoi_dung_id', options.nguoi_dung_id)
    if (options.trang_thai !== '' && options.trang_thai !== undefined && options.trang_thai !== null) {
      params.append('trang_thai', options.trang_thai)
    }
    if (options.trinh_do) params.append('trinh_do', options.trinh_do)
    if (options.sort_by) params.append('sort_by', options.sort_by)
    if (options.sort_dir) params.append('sort_dir', options.sort_dir)

    const query = params.toString()
    return apiCall(`/admin/ho-sos${query ? `?${query}` : ''}`, {
      method: 'GET',
    })
  },

  getDeletedProfiles: (options = {}) => {
    const params = new URLSearchParams()
    if (options.page) params.append('page', options.page)
    if (options.per_page) params.append('per_page', options.per_page)
    if (options.search) params.append('search', options.search)

    const query = params.toString()
    return apiCall(`/admin/ho-sos/da-xoa${query ? `?${query}` : ''}`, {
      method: 'GET',
    })
  },

  getStats: () =>
    apiCall('/admin/ho-sos/thong-ke', {
      method: 'GET',
    }),

  getProfileById: (id) =>
    apiCall(`/admin/ho-sos/${id}`, {
      method: 'GET',
    }),

  toggleStatus: (id) =>
    apiCall(`/admin/ho-sos/${id}/trang-thai`, {
      method: 'PATCH',
    }),

  deleteProfile: (id) =>
    apiCall(`/admin/ho-sos/${id}`, {
      method: 'DELETE',
    }),

  restoreProfile: (id) =>
    apiCall(`/admin/ho-sos/${id}/khoi-phuc`, {
      method: 'PATCH',
    }),

  forceDeleteProfile: (id) =>
    apiCall(`/admin/ho-sos/${id}/xoa-vinh-vien`, {
      method: 'DELETE',
    }),
}

export const adminUserSkillService = {
  getStats: () =>
    apiCall('/admin/nguoi-dung-ky-nangs/thong-ke', {
      method: 'GET',
    }),

  getUserSkills: (options = {}) => {
    const params = new URLSearchParams()

    if (options.per_page !== undefined && options.per_page !== null) params.append('per_page', options.per_page)
    if (options.nguoi_dung_id) params.append('nguoi_dung_id', options.nguoi_dung_id)
    if (options.ky_nang_id) params.append('ky_nang_id', options.ky_nang_id)
    if (options.muc_do) params.append('muc_do', options.muc_do)

    const query = params.toString()
    return apiCall(`/admin/nguoi-dung-ky-nangs${query ? `?${query}` : ''}`, {
      method: 'GET',
    })
  },

  getSkillsByUserId: (userId) =>
    apiCall(`/admin/nguoi-dung-ky-nangs/nguoi-dung/${userId}`, {
      method: 'GET',
    }),
}

export const adminStatsService = {
  getApplicationStats: () =>
    apiCall('/admin/ung-tuyens/thong-ke', {
      method: 'GET',
    }),

  getSavedJobTop: () =>
    apiCall('/admin/luu-tins/thong-ke', {
      method: 'GET',
    }),

  getMatchingStats: () =>
    apiCall('/admin/ket-qua-matchings/thong-ke', {
      method: 'GET',
    }),

  getCareerStats: () =>
    apiCall('/admin/tu-van-nghe-nghieps/thong-ke', {
      method: 'GET',
    }),
}

export const adminApplicationService = {
  getStats: () =>
    apiCall('/admin/ung-tuyens/thong-ke', {
      method: 'GET',
    }),

  getApplications: (options = {}) => {
    const params = new URLSearchParams()

    if (options.page) params.append('page', options.page)
    if (options.per_page) params.append('per_page', options.per_page)
    if (options.cong_ty_id) params.append('cong_ty_id', options.cong_ty_id)
    if (options.trang_thai !== '' && options.trang_thai !== undefined && options.trang_thai !== null) {
      params.append('trang_thai', options.trang_thai)
    }

    const query = params.toString()
    return apiCall(`/admin/ung-tuyens${query ? `?${query}` : ''}`, {
      method: 'GET',
    })
  },
}

export const adminMatchingService = {
  getStats: () =>
    apiCall('/admin/ket-qua-matchings/thong-ke', {
      method: 'GET',
    }),

  getMatchings: (options = {}) => {
    const params = new URLSearchParams()

    if (options.page) params.append('page', options.page)
    if (options.per_page) params.append('per_page', options.per_page)
    if (options.model_version) params.append('model_version', options.model_version)
    if (options.min_score !== '' && options.min_score !== undefined && options.min_score !== null) params.append('min_score', options.min_score)
    if (options.max_score !== '' && options.max_score !== undefined && options.max_score !== null) params.append('max_score', options.max_score)

    const query = params.toString()
    return apiCall(`/admin/ket-qua-matchings${query ? `?${query}` : ''}`, {
      method: 'GET',
    })
  },
}

export const adminCareerAdvisingService = {
  getStats: () =>
    apiCall('/admin/tu-van-nghe-nghieps/thong-ke', {
      method: 'GET',
    }),

  getReports: (options = {}) => {
    const params = new URLSearchParams()

    if (options.page) params.append('page', options.page)
    if (options.per_page) params.append('per_page', options.per_page)
    if (options.nghe_de_xuat) params.append('nghe_de_xuat', options.nghe_de_xuat)
    if (options.min_score !== '' && options.min_score !== undefined && options.min_score !== null) {
      params.append('min_score', options.min_score)
    }

    const query = params.toString()
    return apiCall(`/admin/tu-van-nghe-nghieps${query ? `?${query}` : ''}`, {
      method: 'GET',
    })
  },
}

export const cvTemplateService = {
  getActiveTemplates: () =>
    apiCall('/cv-templates', {
      method: 'GET',
    }),
}

export const adminCvTemplateService = {
  getTemplates: (options = {}) => {
    const params = new URLSearchParams()
    if (options.page) params.append('page', options.page)
    if (options.per_page) params.append('per_page', options.per_page)
    if (options.search) params.append('search', options.search)

    const query = params.toString()
    return apiCall(`/admin/cv-templates${query ? `?${query}` : ''}`, {
      method: 'GET',
    })
  },

  createTemplate: (data) =>
    apiCall('/admin/cv-templates', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateTemplate: (id, data) =>
    apiCall(`/admin/cv-templates/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  toggleTemplateStatus: (id) =>
    apiCall(`/admin/cv-templates/${id}/trang-thai`, {
      method: 'PATCH',
    }),

  deleteTemplate: (id) =>
    apiCall(`/admin/cv-templates/${id}`, {
      method: 'DELETE',
    }),
}

// === Employer APIs ===
export const employerCompanyService = {
  getCompany: () =>
    apiCall('/nha-tuyen-dung/cong-ty', {
      method: 'GET'
    }),

  getMembers: () =>
    apiCall('/nha-tuyen-dung/cong-ty/thanh-viens', {
      method: 'GET'
    }),

  createCompany: (data) =>
    apiCall('/nha-tuyen-dung/cong-ty', {
      method: 'POST',
      body: data instanceof FormData ? data : JSON.stringify(data)
    }),

  updateCompany: (data) =>
    (() => {
      if (data instanceof FormData) {
        const payload = new FormData()

        for (const [key, value] of data.entries()) {
          payload.append(key, value)
        }

        payload.append('_method', 'PUT')

        return apiCall('/nha-tuyen-dung/cong-ty', {
          method: 'POST',
          body: payload,
        })
      }

      return apiCall('/nha-tuyen-dung/cong-ty', {
        method: 'PUT',
        body: JSON.stringify(data)
      })
    })(),

  addMember: (payload) =>
    apiCall('/nha-tuyen-dung/cong-ty/thanh-viens', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  updateMemberRole: (memberId, vaiTroNoiBo) =>
    apiCall(`/nha-tuyen-dung/cong-ty/thanh-viens/${memberId}/vai-tro`, {
      method: 'PATCH',
      body: JSON.stringify({ vai_tro_noi_bo: vaiTroNoiBo }),
    }),

  updateMember: (memberId, payload) =>
    apiCall(`/nha-tuyen-dung/cong-ty/thanh-viens/${memberId}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    }),

  toggleMemberStatus: (memberId) =>
    apiCall(`/nha-tuyen-dung/cong-ty/thanh-viens/${memberId}/khoa`, {
      method: 'PATCH',
    }),

  getMemberPermissions: (memberId) =>
    apiCall(`/nha-tuyen-dung/cong-ty/thanh-viens/${memberId}/permissions`, {
      method: 'GET',
    }),

  updateMemberPermissions: (memberId, permissions) =>
    apiCall(`/nha-tuyen-dung/cong-ty/thanh-viens/${memberId}/permissions`, {
      method: 'PUT',
      body: JSON.stringify({ quyen_noi_bo: permissions }),
    }),

  createHrPermissionDefinition: (payload) =>
    apiCall('/nha-tuyen-dung/cong-ty/thanh-viens/permissions/definitions', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  removeMember: (memberId) =>
    apiCall(`/nha-tuyen-dung/cong-ty/thanh-viens/${memberId}`, {
      method: 'DELETE',
    }),

  getInternalRoles: () =>
    apiCall('/nha-tuyen-dung/cong-ty/vai-tro-noi-bo', {
      method: 'GET',
    }),

  createInternalRole: (payload) =>
    apiCall('/nha-tuyen-dung/cong-ty/vai-tro-noi-bo', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  updateInternalRole: (roleId, payload) =>
    apiCall(`/nha-tuyen-dung/cong-ty/vai-tro-noi-bo/${roleId}`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    }),

  deleteInternalRole: (roleId) =>
    apiCall(`/nha-tuyen-dung/cong-ty/vai-tro-noi-bo/${roleId}`, {
      method: 'DELETE',
    }),

  getHrAuditLogs: (options = {}) => {
    const params = new URLSearchParams()
    if (options.page) params.append('page', options.page)
    if (options.per_page) params.append('per_page', options.per_page)

    const query = params.toString()
    return apiCall(`/nha-tuyen-dung/cong-ty/hr-audit-logs${query ? `?${query}` : ''}`, {
      method: 'GET',
    })
  },
}

export const employerAuditLogService = {
  getLogs: (options = {}) => {
    const query = buildAuditLogQuery(options)
    return apiCall(`/nha-tuyen-dung/audit-logs${query ? `?${query}` : ''}`, {
      method: 'GET',
    })
  },
}

export const employerBillingService = {
  getWallet: () =>
    apiCall('/nha-tuyen-dung/vi', {
      method: 'GET',
    }),

  getEntitlements: () =>
    apiCall('/nha-tuyen-dung/billing/entitlements', {
      method: 'GET',
    }),

  getTransactions: (options = {}) => {
    const params = new URLSearchParams()

    if (options.page) params.append('page', options.page)
    if (options.per_page) params.append('per_page', options.per_page)

    const query = params.toString()
    return apiCall(`/nha-tuyen-dung/vi/bien-dong${query ? `?${query}` : ''}`, {
      method: 'GET',
    })
  },

  getPricing: () =>
    apiCall('/nha-tuyen-dung/ai-pricing', {
      method: 'GET',
    }),

  createMomoTopUp: (so_tien) =>
    apiCall('/nha-tuyen-dung/vi/nap-tien/momo', {
      method: 'POST',
      body: JSON.stringify({ so_tien }),
    }),

  createVnpayTopUp: (so_tien, bank_code) =>
    apiCall('/nha-tuyen-dung/vi/nap-tien/vnpay', {
      method: 'POST',
      body: JSON.stringify({
        so_tien,
        ...(bank_code ? { bank_code } : {}),
      }),
    }),

  getTopUp: (maGiaoDichNoiBo) =>
    apiCall(`/nha-tuyen-dung/vi/nap-tien/${maGiaoDichNoiBo}`, {
      method: 'GET',
    }),
}

export const employerJobService = {
  getJobs: (options = {}) => {
    const params = new URLSearchParams()

    if (options.page) params.append('page', options.page)
    if (options.per_page) params.append('per_page', options.per_page)
    if (options.search) params.append('search', options.search)
    if (options.hr_phu_trach_id !== undefined && options.hr_phu_trach_id !== null && options.hr_phu_trach_id !== '') {
      params.append('hr_phu_trach_id', options.hr_phu_trach_id)
    }
    if (options.trang_thai !== undefined && options.trang_thai !== null && options.trang_thai !== '' && options.trang_thai !== 'all') {
      params.append('trang_thai', options.trang_thai)
    }

    const query = params.toString()
    return apiCall(`/nha-tuyen-dung/tin-tuyen-dungs${query ? `?${query}` : ''}`, {
      method: 'GET'
    })
  },

  getJobById: (id) =>
    apiCall(`/nha-tuyen-dung/tin-tuyen-dungs/${id}`, {
      method: 'GET'
    }),

  sponsorJob: (id, featureCode, options = {}) =>
    apiCall(`/nha-tuyen-dung/tin-tuyen-dungs/${id}/sponsor`, {
      method: 'POST',
      headers: {
        'X-Idempotency-Key': options.idempotencyKey || createIdempotencyKey('featured-job'),
      },
      body: JSON.stringify({
        feature_code: featureCode,
      })
    }),

  createJob: (data) =>
    apiCall('/nha-tuyen-dung/tin-tuyen-dungs', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  updateJob: (id, data) =>
    apiCall(`/nha-tuyen-dung/tin-tuyen-dungs/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    }),

  toggleStatus: (id) =>
    apiCall(`/nha-tuyen-dung/tin-tuyen-dungs/${id}/trang-thai`, {
      method: 'PATCH'
    }),

  deleteJob: (id) =>
    apiCall(`/nha-tuyen-dung/tin-tuyen-dungs/${id}`, {
      method: 'DELETE'
    }),

  parseJob: (id) =>
    apiCall(`/nha-tuyen-dung/tin-tuyen-dungs/${id}/parse`, {
      method: 'POST'
    }),

  getShortlist: (id, options = {}) => {
    const params = new URLSearchParams()
    if (options.limit) params.append('limit', options.limit)
    if (options.ai_explain !== undefined) params.append('ai_explain', options.ai_explain ? '1' : '0')
    if (options.scope) params.append('scope', options.scope)

    const query = params.toString()
    return apiCall(`/nha-tuyen-dung/tin-tuyen-dungs/${id}/shortlist${query ? `?${query}` : ''}`, {
      method: 'GET',
      headers: options.ai_explain
        ? {
            'X-Idempotency-Key': options.idempotencyKey || createIdempotencyKey('employer-shortlist'),
          }
        : undefined,
    })
  },

  compareShortlistCandidates: (id, hoSoIds, options = {}) => {
    const params = new URLSearchParams()
    if (options.ai_explain !== undefined) params.append('ai_explain', options.ai_explain ? '1' : '0')

    const query = params.toString()
    return apiCall(`/nha-tuyen-dung/tin-tuyen-dungs/${id}/shortlist/compare${query ? `?${query}` : ''}`, {
      method: 'POST',
      headers: options.ai_explain
        ? {
            'X-Idempotency-Key': options.idempotencyKey || createIdempotencyKey('employer-compare'),
          }
        : undefined,
      body: JSON.stringify({ ho_so_ids: hoSoIds })
    })
  },
}

export const employerCandidateService = {
  getCandidates: (options = {}) => {
    const params = new URLSearchParams()

    if (options.page) params.append('page', options.page)
    if (options.per_page) params.append('per_page', options.per_page)
    if (options.search) params.append('search', options.search)
    if (options.trinh_do) params.append('trinh_do', options.trinh_do)
    if (options.kinh_nghiem_tu !== undefined && options.kinh_nghiem_tu !== '') params.append('kinh_nghiem_tu', options.kinh_nghiem_tu)
    if (options.kinh_nghiem_den !== undefined && options.kinh_nghiem_den !== '') params.append('kinh_nghiem_den', options.kinh_nghiem_den)
    if (options.sort_by) params.append('sort_by', options.sort_by)
    if (options.sort_dir) params.append('sort_dir', options.sort_dir)

    const query = params.toString()
    return apiCall(`/nha-tuyen-dung/ho-sos${query ? `?${query}` : ''}`, {
      method: 'GET'
    })
  },

  getCandidateById: (id) =>
    apiCall(`/nha-tuyen-dung/ho-sos/${id}`, {
      method: 'GET'
    }),
}

export const employerApplicationService = {
  getApplications: (options = {}) => {
    const params = new URLSearchParams()

    if (options.page) params.append('page', options.page)
    if (options.per_page) params.append('per_page', options.per_page)
    if (options.tin_tuyen_dung_id) params.append('tin_tuyen_dung_id', options.tin_tuyen_dung_id)
    if (options.hr_phu_trach_id !== undefined && options.hr_phu_trach_id !== null && options.hr_phu_trach_id !== '') {
      params.append('hr_phu_trach_id', options.hr_phu_trach_id)
    }
    if (options.trang_thai !== undefined && options.trang_thai !== null && options.trang_thai !== '') {
      params.append('trang_thai', options.trang_thai)
    }

    const query = params.toString()
    return apiCall(`/nha-tuyen-dung/ung-tuyens${query ? `?${query}` : ''}`, {
      method: 'GET'
    })
  },

  updateStatus: (id, data) =>
    apiCall(`/nha-tuyen-dung/ung-tuyens/${id}/trang-thai`, {
      method: 'PATCH',
      body: JSON.stringify(data)
    }),

  getNotificationTemplates: () =>
    apiCall('/nha-tuyen-dung/ung-tuyens/notification-templates', {
      method: 'GET',
    }),

  getInterviewRounds: (id) =>
    apiCall(`/nha-tuyen-dung/ung-tuyens/${id}/interview-rounds`, {
      method: 'GET',
    }),

  createInterviewRound: (id, data) =>
    apiCall(`/nha-tuyen-dung/ung-tuyens/${id}/interview-rounds`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateInterviewRound: (id, roundId, data) =>
    apiCall(`/nha-tuyen-dung/ung-tuyens/${id}/interview-rounds/${roundId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  deleteInterviewRound: (id, roundId) =>
    apiCall(`/nha-tuyen-dung/ung-tuyens/${id}/interview-rounds/${roundId}`, {
      method: 'DELETE',
    }),

  generateInterviewCopilot: (id, data = {}) => {
    const { idempotencyKey, ...payload } = data || {}

    return apiCall(`/nha-tuyen-dung/ung-tuyens/${id}/interview-copilot/generate`, {
      method: 'POST',
      headers: {
        'X-Idempotency-Key': idempotencyKey || createIdempotencyKey('interview-copilot-generate'),
      },
      body: JSON.stringify(payload),
    })
  },

  evaluateInterviewCopilot: (id, data = {}) => {
    const { idempotencyKey, ...payload } = data || {}

    return apiCall(`/nha-tuyen-dung/ung-tuyens/${id}/interview-copilot/evaluate`, {
      method: 'POST',
      headers: {
        'X-Idempotency-Key': idempotencyKey || createIdempotencyKey('interview-copilot-evaluate'),
      },
      body: JSON.stringify(payload),
    })
  },

  sendOffer: (id, data) =>
    apiCall(`/nha-tuyen-dung/ung-tuyens/${id}/gui-offer`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getOnboarding: (id) =>
    apiCall(`/nha-tuyen-dung/ung-tuyens/${id}/onboarding`, {
      method: 'GET',
    }),

  updateOnboarding: (id, data) =>
    apiCall(`/nha-tuyen-dung/ung-tuyens/${id}/onboarding`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  createOnboardingTask: (id, data) =>
    apiCall(`/nha-tuyen-dung/ung-tuyens/${id}/onboarding/tasks`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateOnboardingTask: (id, taskId, data) =>
    apiCall(`/nha-tuyen-dung/ung-tuyens/${id}/onboarding/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  deleteOnboardingTask: (id, taskId) =>
    apiCall(`/nha-tuyen-dung/ung-tuyens/${id}/onboarding/tasks/${taskId}`, {
      method: 'DELETE',
    }),

  resendInterviewEmail: (id) =>
    apiCall(`/nha-tuyen-dung/ung-tuyens/${id}/gui-lai-email-phong-van`, {
      method: 'POST',
    }),

  downloadExport: (id, document = 'full') =>
    blobApiCall(`/nha-tuyen-dung/ung-tuyens/${id}/export/${document}`, {
      method: 'GET',
    }),
}

// === Public Job APIs ===
export const jobService = {
  getJobs: (options = {}) => {
    const params = new URLSearchParams()

    if (options.page) params.append('page', options.page)
    if (options.per_page) params.append('per_page', options.per_page)
    if (options.search) params.append('search', options.search)
    if (options.nganh_nghe_id) params.append('nganh_nghe_id', options.nganh_nghe_id)
    if (options.dia_diem) params.append('dia_diem', options.dia_diem)

    const query = params.toString()
    return apiCall(`/tin-tuyen-dungs${query ? `?${query}` : ''}`, {
      method: 'GET'
    })
  },

  getJobById: (id) =>
    apiCall(`/tin-tuyen-dungs/${id}`, {
      method: 'GET'
    }),

  semanticSearch: (q, top_k = 8) =>
    apiCall(`/tin-tuyen-dungs/semantic-search?q=${encodeURIComponent(q)}&top_k=${top_k}`, {
      method: 'GET',
    }),

  getIndustries: (options = {}) => {
    const params = new URLSearchParams()

    if (options.search) params.append('search', options.search)
    if (options.per_page !== undefined) params.append('per_page', options.per_page)
    if (options.goc !== undefined) params.append('goc', options.goc)
    if (options.danh_muc_cha_id) params.append('danh_muc_cha_id', options.danh_muc_cha_id)

    const query = params.toString()
    return apiCall(`/nganh-nghes${query ? `?${query}` : ''}`, {
      method: 'GET'
    })
  },

  getSkills: (options = {}) => {
    const params = new URLSearchParams()

    if (options.search) params.append('search', options.search)
    if (options.per_page !== undefined) params.append('per_page', options.per_page)

    const query = params.toString()
    return apiCall(`/ky-nangs${query ? `?${query}` : ''}`, {
      method: 'GET'
    })
  },

  getCompanies: (options = {}) => {
    const params = new URLSearchParams()

    if (options.search) params.append('search', options.search)
    if (options.page) params.append('page', options.page)
    if (options.per_page !== undefined) params.append('per_page', options.per_page)

    const query = params.toString()
    return apiCall(`/cong-tys${query ? `?${query}` : ''}`, {
      method: 'GET'
    })
  },

  getCompanyById: (id) =>
    apiCall(`/cong-tys/${id}`, {
      method: 'GET'
    }),

  getIndustryById: (id) =>
    apiCall(`/nganh-nghes/${id}`, {
      method: 'GET'
    }),

  getSkillById: (id) =>
    apiCall(`/ky-nangs/${id}`, {
      method: 'GET'
    })
}

// === Candidate Saved Job APIs ===
export const savedJobService = {
  getSavedJobs: (options = {}) => {
    const params = new URLSearchParams()

    if (options.page) params.append('page', options.page)
    if (options.per_page) params.append('per_page', options.per_page)

    const query = params.toString()
    return apiCall(`/ung-vien/tin-da-luu${query ? `?${query}` : ''}`, {
      method: 'GET'
    })
  },

  toggleSavedJob: (jobId) =>
    apiCall(`/ung-vien/tin-da-luu/${jobId}/toggle`, {
      method: 'POST'
    })
}

// === Candidate Re-engagement APIs ===
export const reEngagementService = {
  getInsights: (options = {}) => {
    const params = new URLSearchParams()

    if (options.similar_limit) params.append('similar_limit', options.similar_limit)

    const query = params.toString()
    return apiCall(`/ung-vien/re-engagement/insights${query ? `?${query}` : ''}`, {
      method: 'GET',
    })
  },
}

// === Candidate Follow Company APIs ===
export const followCompanyService = {
  getFollowedCompanies: (options = {}) => {
    const params = new URLSearchParams()

    if (options.page) params.append('page', options.page)
    if (options.per_page) params.append('per_page', options.per_page)
    if (options.recent_jobs_limit) params.append('recent_jobs_limit', options.recent_jobs_limit)

    const query = params.toString()
    return apiCall(`/ung-vien/cong-ty-theo-doi${query ? `?${query}` : ''}`, {
      method: 'GET',
    })
  },

  toggleFollowCompany: (companyId) =>
    apiCall(`/ung-vien/cong-ty-theo-doi/${companyId}/toggle`, {
      method: 'POST',
    }),
}

// === Candidate Profile APIs ===
export const profileService = {
  getProfiles: (options = {}) => {
    const params = new URLSearchParams()

    if (options.page) params.append('page', options.page)
    if (options.per_page) params.append('per_page', options.per_page)
    if (options.trang_thai !== undefined && options.trang_thai !== null && options.trang_thai !== '') {
      params.append('trang_thai', options.trang_thai)
    }
    if (options.sort_by) params.append('sort_by', options.sort_by)
    if (options.sort_dir) params.append('sort_dir', options.sort_dir)

    const query = params.toString()
    return apiCall(`/ung-vien/ho-sos${query ? `?${query}` : ''}`, {
      method: 'GET'
    })
  },

  getProfileById: (id) =>
    apiCall(`/ung-vien/ho-sos/${id}`, {
      method: 'GET'
    }),

  createProfile: (data) =>
    apiCall('/ung-vien/ho-sos', {
      method: 'POST',
      body: data,
    }),

  updateProfile: (id, data) =>
    apiCall(`/ung-vien/ho-sos/${id}`, {
      method: 'POST',
      headers: {
        'X-HTTP-Method-Override': 'PUT',
      },
      body: data,
    }),

  toggleProfileStatus: (id) =>
    apiCall(`/ung-vien/ho-sos/${id}/trang-thai`, {
      method: 'PATCH'
    }),

  deleteProfile: (id) =>
    apiCall(`/ung-vien/ho-sos/${id}`, {
      method: 'DELETE'
    }),

  parseProfileCv: (id) =>
    apiCall(`/ung-vien/ho-sos/${id}/parse`, {
      method: 'POST'
    }),

  tailorProfileForJob: (id, jobId, data = {}) =>
    apiCall(`/ung-vien/ho-sos/${id}/tailor/${jobId}`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
}

export const walletService = {
  getWallet: () =>
    apiCall('/ung-vien/vi', {
      method: 'GET',
    }),

  getEntitlements: () =>
    apiCall('/ung-vien/billing/entitlements', {
      method: 'GET',
    }),

  getTransactions: (options = {}) => {
    const params = new URLSearchParams()

    if (options.page) params.append('page', options.page)
    if (options.per_page) params.append('per_page', options.per_page)

    const query = params.toString()
    return apiCall(`/ung-vien/vi/bien-dong${query ? `?${query}` : ''}`, {
      method: 'GET',
    })
  },

  getPricing: () =>
    apiCall('/ung-vien/ai-pricing', {
      method: 'GET',
    }),

  createMomoTopUp: (so_tien) =>
    apiCall('/ung-vien/vi/nap-tien/momo', {
      method: 'POST',
      body: JSON.stringify({ so_tien }),
    }),

  createVnpayTopUp: (so_tien, bank_code) =>
    apiCall('/ung-vien/vi/nap-tien/vnpay', {
      method: 'POST',
      body: JSON.stringify({
        so_tien,
        ...(bank_code ? { bank_code } : {}),
      }),
    }),

  getTopUp: (maGiaoDichNoiBo) =>
    apiCall(`/ung-vien/vi/nap-tien/${maGiaoDichNoiBo}`, {
      method: 'GET',
    }),
}

export const paymentService = {
  getPayments: (options = {}) => {
    const params = new URLSearchParams()

    if (options.page) params.append('page', options.page)
    if (options.per_page) params.append('per_page', options.per_page)
    if (options.loai_giao_dich) params.append('loai_giao_dich', options.loai_giao_dich)
    if (options.trang_thai) params.append('trang_thai', options.trang_thai)

    const query = params.toString()
    return apiCall(`/ung-vien/payments${query ? `?${query}` : ''}`, {
      method: 'GET',
    })
  },

  getPaymentDetail: (maGiaoDichNoiBo) =>
    apiCall(`/ung-vien/payments/${maGiaoDichNoiBo}`, {
      method: 'GET',
    }),
}

export const subscriptionService = {
  getPlans: () =>
    apiCall('/ung-vien/goi-dich-vus', {
      method: 'GET',
    }),

  getEntitlements: () =>
    apiCall('/ung-vien/billing/entitlements', {
      method: 'GET',
    }),

  getCurrent: () =>
    apiCall('/ung-vien/goi-dich-vu-hien-tai', {
      method: 'GET',
    }),

  createMomoPurchase: (ma_goi) =>
    apiCall('/ung-vien/goi-dich-vus/mua/momo', {
      method: 'POST',
      body: JSON.stringify({ ma_goi }),
    }),

  createWalletPurchase: (ma_goi) =>
    apiCall('/ung-vien/goi-dich-vus/mua/vi', {
      method: 'POST',
      body: JSON.stringify({ ma_goi }),
    }),

  createVnpayPurchase: (ma_goi, bank_code) =>
    apiCall('/ung-vien/goi-dich-vus/mua/vnpay', {
      method: 'POST',
      body: JSON.stringify({
        ma_goi,
        ...(bank_code ? { bank_code } : {}),
      }),
    }),
}

export const cvBuilderAiService = {
  generateWriting: (payload) =>
    apiCall('/ung-vien/cv-builder/ai-writing', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
}

// === Candidate Personal Skill APIs ===
export const candidateSkillService = {
  getCatalog: (options = {}) => {
    const params = new URLSearchParams()

    if (options.search) params.append('search', options.search)
    if (options.per_page !== undefined) params.append('per_page', options.per_page)

    const query = params.toString()
    return apiCall(`/ky-nangs${query ? `?${query}` : ''}`, {
      method: 'GET',
    })
  },

  getMySkills: () =>
    apiCall('/ung-vien/ky-nangs', {
      method: 'GET',
    }),

  createSkill: (data) =>
    apiCall('/ung-vien/ky-nangs', {
      method: 'POST',
      body: data,
    }),

  updateSkill: (id, data) => {
    const payload = new FormData()

    for (const [key, value] of data.entries()) {
      payload.append(key, value)
    }

    payload.append('_method', 'PUT')

    return apiCall(`/ung-vien/ky-nangs/${id}`, {
      method: 'POST',
      body: payload,
    })
  },

  deleteSkill: (id) =>
    apiCall(`/ung-vien/ky-nangs/${id}`, {
      method: 'DELETE',
    }),
}

// === Candidate Application APIs ===
export const applicationService = {
  getApplications: (options = {}) => {
    const params = new URLSearchParams()

    if (options.page) params.append('page', options.page)
    if (options.per_page) params.append('per_page', options.per_page)
    if (options.trang_thai !== undefined && options.trang_thai !== null && options.trang_thai !== '') {
      params.append('trang_thai', options.trang_thai)
    }
    if (options.da_rut_don !== undefined && options.da_rut_don !== null && options.da_rut_don !== '') {
      params.append('da_rut_don', options.da_rut_don)
    }

    const query = params.toString()
    return apiCall(`/ung-vien/ung-tuyens${query ? `?${query}` : ''}`, {
      method: 'GET'
    })
  },

  apply: ({ tin_tuyen_dung_id, ho_so_id, thu_xin_viec }) =>
    apiCall('/ung-vien/ung-tuyens', {
      method: 'POST',
      body: JSON.stringify({
        tin_tuyen_dung_id,
        ho_so_id,
        thu_xin_viec,
      })
    }),

  updateApplication: (id, { ho_so_id, thu_xin_viec }) =>
    apiCall(`/ung-vien/ung-tuyens/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({
        ho_so_id,
        thu_xin_viec,
      })
    }),

  confirmInterviewAttendance: (id, trang_thai_tham_gia_phong_van) =>
    apiCall(`/ung-vien/ung-tuyens/${id}/xac-nhan-phong-van`, {
      method: 'PATCH',
      body: JSON.stringify({
        trang_thai_tham_gia_phong_van,
      })
    }),

  confirmInterviewRoundAttendance: (id, roundId, trang_thai_tham_gia_phong_van) =>
    apiCall(`/ung-vien/ung-tuyens/${id}/interview-rounds/${roundId}/xac-nhan`, {
      method: 'PATCH',
      body: JSON.stringify({
        trang_thai_tham_gia_phong_van,
      })
    }),

  respondOffer: (id, action) =>
    apiCall(`/ung-vien/ung-tuyens/${id}/phan-hoi-offer`, {
      method: 'PATCH',
      body: JSON.stringify({ action }),
    }),

  getOnboarding: (id) =>
    apiCall(`/ung-vien/ung-tuyens/${id}/onboarding`, {
      method: 'GET',
    }),

  updateOnboardingTask: (id, taskId, trang_thai) =>
    apiCall(`/ung-vien/ung-tuyens/${id}/onboarding/tasks/${taskId}`, {
      method: 'PATCH',
      body: JSON.stringify({ trang_thai }),
    }),

  withdrawApplication: (id) =>
    apiCall(`/ung-vien/ung-tuyens/${id}/rut-don`, {
      method: 'PATCH',
    }),

  downloadExport: (id, document = 'full') =>
    blobApiCall(`/ung-vien/ung-tuyens/${id}/export/${document}`, {
      method: 'GET',
    }),

  generateCoverLetter: ({ tin_tuyen_dung_id, ho_so_id, idempotencyKey = null }) =>
    apiCall('/ung-vien/ung-tuyens/generate-cover-letter', {
      method: 'POST',
      headers: {
        'X-Idempotency-Key': idempotencyKey || createIdempotencyKey('cover-letter'),
      },
      body: JSON.stringify({
        tin_tuyen_dung_id,
        ho_so_id,
      })
    }),

  confirmCoverLetter: (id, thu_xin_viec) =>
    apiCall(`/ung-vien/ung-tuyens/${id}/confirm-cover-letter`, {
      method: 'PATCH',
      body: JSON.stringify({
        thu_xin_viec,
      })
    }),
}

// === Candidate Matching APIs ===
export const matchingService = {
  getMatchingResults: (options = {}) => {
    const params = new URLSearchParams()

    if (options.page) params.append('page', options.page)
    if (options.per_page) params.append('per_page', options.per_page)
    if (options.ho_so_id) params.append('ho_so_id', options.ho_so_id)

    const query = params.toString()
    return apiCall(`/ung-vien/ket-qua-matchings${query ? `?${query}` : ''}`, {
      method: 'GET'
    })
  },

  generateMatching: (hoSoId, tinTuyenDungId) =>
    apiCall(`/ung-vien/ho-sos/${hoSoId}/matching`, {
      method: 'POST',
      body: JSON.stringify({
        tin_tuyen_dung_id: tinTuyenDungId,
      })
    }),
}

// === Candidate Career Report APIs ===
export const careerReportService = {
  getReports: (options = {}) => {
    const params = new URLSearchParams()

    if (options.page) params.append('page', options.page)
    if (options.per_page) params.append('per_page', options.per_page)
    if (options.ho_so_id) params.append('ho_so_id', options.ho_so_id)

    const query = params.toString()
    return apiCall(`/ung-vien/tu-van-nghe-nghieps${query ? `?${query}` : ''}`, {
      method: 'GET',
    })
  },

  generateReport: (hoSoId, options = {}) =>
    apiCall(`/ung-vien/ho-sos/${hoSoId}/career-report`, {
      method: 'POST',
      headers: {
        'X-Idempotency-Key': options.idempotencyKey || createIdempotencyKey('career-report'),
      },
    }),

  deleteReport: (reportId) =>
    apiCall(`/ung-vien/tu-van-nghe-nghieps/${reportId}`, {
      method: 'DELETE',
    }),
}

// === Candidate AI Chat APIs ===
export const aiChatService = {
  getSessions: () =>
    apiCall('/ai-chat/sessions', {
      method: 'GET'
    }),

  createSession: (data) =>
    apiCall('/ai-chat/sessions', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  getMessages: (sessionId) =>
    apiCall(`/ai-chat/sessions/${sessionId}/messages`, {
      method: 'GET'
    }),

  sendMessage: ({ session_id, message, force_model = true }) =>
    apiCall('/ai-chat/messages', {
      method: 'POST',
      body: JSON.stringify({
        session_id,
        message,
        force_model,
      })
    }),

  sendMessageStream: ({ session_id, message, force_model = true }, handlers = {}) =>
    streamApiCall('/ai-chat/messages/stream', {
      method: 'POST',
      body: JSON.stringify({
        session_id,
        message,
        force_model,
      })
    }, handlers),

  updateSessionStatus: (sessionId, status, summary = null) =>
    apiCall(`/ai-chat/sessions/${sessionId}/status`, {
      method: 'PATCH',
      body: JSON.stringify({
        status,
        summary,
      })
    }),

  deleteSession: (sessionId) =>
    apiCall(`/ai-chat/sessions/${sessionId}/messages`, {
      method: 'DELETE'
    }),
}

// === Candidate Mock Interview APIs ===
export const mockInterviewService = {
  getDashboard: () =>
    apiCall('/mock-interview/dashboard', {
      method: 'GET'
    }),

  getSessions: () =>
    apiCall('/mock-interview/sessions', {
      method: 'GET'
    }),

  createSession: (data) =>
    apiCall('/mock-interview/sessions', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  getMessages: (sessionId) =>
    apiCall(`/mock-interview/sessions/${sessionId}/messages`, {
      method: 'GET'
    }),

  answer: ({ session_id, answer }) =>
    apiCall('/mock-interview/messages', {
      method: 'POST',
      body: JSON.stringify({
        session_id,
        answer,
      })
    }),

  answerStream: ({ session_id, answer }, handlers = {}) =>
    streamApiCall('/mock-interview/messages/stream', {
      method: 'POST',
      body: JSON.stringify({
        session_id,
        answer,
      })
    }, handlers),

  getReport: (sessionId) =>
    apiCall(`/mock-interview/sessions/${sessionId}/report`, {
      method: 'GET'
    }),

  generateReport: (sessionId) =>
    apiCall(`/mock-interview/sessions/${sessionId}/report`, {
      method: 'POST'
    }),

  generateReportStream: (sessionId, handlers = {}) =>
    streamApiCall(`/mock-interview/sessions/${sessionId}/report/stream`, {
      method: 'POST'
    }, handlers),

  updateSessionStatus: (sessionId, status, summary = null) =>
    apiCall(`/mock-interview/sessions/${sessionId}/status`, {
      method: 'PATCH',
      body: JSON.stringify({
        status,
        summary,
      })
    }),

  deleteSession: (sessionId) =>
    apiCall(`/mock-interview/sessions/${sessionId}`, {
      method: 'DELETE'
    }),
}

export default {
  authService,
  userService,
  adminAccountService,
  companyService,
  jobService,
  savedJobService,
  reEngagementService,
  followCompanyService,
  profileService,
  walletService,
  paymentService,
  subscriptionService,
  cvBuilderAiService,
  applicationService,
  matchingService,
  adminProfileService,
  adminUserSkillService,
  adminBillingService,
  adminAiUsageService,
  aiChatService,
  mockInterviewService,
  adminMatchingService,
  adminCareerAdvisingService,
}
