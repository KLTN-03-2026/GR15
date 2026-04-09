/**
 * API Service
 * Quản lý tất cả các request đến Backend
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

// Lấy token từ localStorage
const getAuthToken = () => {
  return localStorage.getItem('access_token')
}

const clearStoredSession = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('token')
  localStorage.removeItem('user_role')
  localStorage.removeItem('admin_user')
  localStorage.removeItem('employer_user')
  localStorage.removeItem('employer')
  localStorage.removeItem('user')
}

const handleUnauthorizedResponse = (data) => {
  if (typeof window === 'undefined') {
    clearStoredSession()
    return
  }

  const currentPath = window.location.pathname || '/'
  const isAdminArea = currentPath.startsWith('/admin')
  const isEmployerArea = currentPath.startsWith('/employer')

  clearStoredSession()
  window.dispatchEvent(new CustomEvent('auth-expired', { detail: data || null }))

  if (isAdminArea && currentPath !== '/admin/login') {
    window.location.assign('/admin/login')
    return
  }

  if (isEmployerArea && currentPath !== '/employer/auth') {
    window.location.assign('/employer/auth')
    return
  }

  if (!['/login', '/auth', '/register', '/'].includes(currentPath)) {
    window.location.assign('/login')
  }
}

// Hàm fetch chung
const apiCall = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`
  const isFormData = options.body instanceof FormData
  
  const headers = {
    ...options.headers
  }

  if (!isFormData) {
    headers['Content-Type'] = 'application/json'
  }

  // Lấy token nếu có
  const token = getAuthToken()
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

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
        handleUnauthorizedResponse(data)
      }

      throw {
        status: response.status,
        message: data.message || `Lỗi ${response.status}: ${response.statusText}`,
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

// === Auth APIs ===
export const authService = {
  // Guest/Candidate registration
  registerCandidate: (fullName, email, phone, password) =>
    apiCall('/auth/register-candidate', {
      method: 'POST',
      body: JSON.stringify({ fullName, email, phone, password })
    }),

  // Guest login
  login: (email, password) =>
    apiCall('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    }),

  // Employer registration
  registerEmployer: (companyName, contactPerson, email, phone, password) =>
    apiCall('/auth/register-employer', {
      method: 'POST',
      body: JSON.stringify({ companyName, contactPerson, email, phone, password })
    }),

  // Employer login
  loginEmployer: (email, password) =>
    apiCall('/employer/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    }),

  // Admin login
  loginAdmin: (email, password) =>
    apiCall('/dang-nhap', {
      method: 'POST',
      body: JSON.stringify({ email, mat_khau: password })
    }),

  logout: () =>
    apiCall('/dang-xuat', {
      method: 'POST'
    }),

  getProfile: () =>
    apiCall('/ho-so', {
      method: 'GET'
    }),

  updateProfile: (data) =>
    data instanceof FormData
      ? (() => {
          data.append('_method', 'PUT')
          return apiCall('/ho-so', {
            method: 'POST',
            body: data
          })
        })()
      : apiCall('/ho-so', {
          method: 'PUT',
          body: JSON.stringify(data)
        }),

  changePassword: (oldPassword, newPassword, confirmPassword) =>
    apiCall('/doi-mat-khau', {
      method: 'POST',
      body: JSON.stringify({
        mat_khau_cu: oldPassword,
        mat_khau_moi: newPassword,
        mat_khau_moi_confirmation: confirmPassword
      })
    }),

  forgotPassword: (email) =>
    apiCall('/auth/forgot-password', {
      method: 'POST',
      body: JSON.stringify({ email })
    }),

  resetPassword: (token, newPassword, confirmPassword) =>
    apiCall('/auth/reset-password', {
      method: 'POST',
      body: JSON.stringify({ token, newPassword, confirmPassword })
    }),

  verifyEmail: (token) =>
    apiCall('/auth/verify-email', {
      method: 'POST',
      body: JSON.stringify({ token })
    }),

  resendVerificationEmail: (email) =>
    apiCall('/auth/resend-verification', {
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

// === Admin Industry APIs ===
export const industryService = {
  getIndustries: (options = {}) => {
    const params = new URLSearchParams()
    if (options.page) params.append('page', options.page)
    if (options.per_page) params.append('per_page', options.per_page)
    if (options.search) params.append('search', options.search)
    if (options.trang_thai !== undefined) params.append('trang_thai', options.trang_thai)
    if (options.danh_muc_cha_id !== undefined) params.append('danh_muc_cha_id', options.danh_muc_cha_id)

    params.append('sort_by', options.sort_by || 'ten_nganh')
    params.append('sort_dir', options.sort_dir || 'asc')

    const query = params.toString()
    const endpoint = `/admin/nganh-nghes${query ? '?' + query : ''}`

    return apiCall(endpoint, {
      method: 'GET'
    })
  },

  getIndustryStats: () =>
    apiCall('/admin/nganh-nghes/thong-ke', {
      method: 'GET'
    }),

  getIndustryById: (id) =>
    apiCall(`/admin/nganh-nghes/${id}`, {
      method: 'GET'
    }),

  createIndustry: (data) =>
    apiCall('/admin/nganh-nghes', {
      method: 'POST',
      body: data instanceof FormData ? data : JSON.stringify(data)
    }),

  updateIndustry: (id, data) =>
    data instanceof FormData
      ? (() => {
          data.append('_method', 'PUT')
          return apiCall(`/admin/nganh-nghes/${id}`, {
            method: 'POST',
            body: data
          })
        })()
      : apiCall(`/admin/nganh-nghes/${id}`, {
          method: 'PUT',
          body: JSON.stringify(data)
        }),

  toggleIndustryStatus: (id) =>
    apiCall(`/admin/nganh-nghes/${id}/trang-thai`, {
      method: 'PATCH'
    }),

  deleteIndustry: (id) =>
    apiCall(`/admin/nganh-nghes/${id}`, {
      method: 'DELETE'
    })
}

// === Admin Company APIs ===
export const companyService = {
  // Lấy danh sách công ty
  getCompanies: (options = {}) => {
    const params = new URLSearchParams()
    if (options.page) params.append('page', options.page)
    if (options.per_page) params.append('per_page', options.per_page)
    if (options.search) params.append('search', options.search)
    if (options.trang_thai !== undefined) params.append('trang_thai', options.trang_thai)
    if (options.nganh_nghe_id !== undefined) params.append('nganh_nghe_id', options.nganh_nghe_id)
    if (options.quy_mo) params.append('quy_mo', options.quy_mo)
    
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

// === Admin Skill APIs ===
export const skillService = {
  getSkills: (options = {}) => {
    const params = new URLSearchParams()
    if (options.page) params.append('page', options.page)
    if (options.per_page) params.append('per_page', options.per_page)
    if (options.search) params.append('search', options.search)

    params.append('sort_by', options.sort_by || 'ten_ky_nang')
    params.append('sort_dir', options.sort_dir || 'asc')

    const query = params.toString()
    const endpoint = `/admin/ky-nangs${query ? '?' + query : ''}`

    return apiCall(endpoint, {
      method: 'GET'
    })
  },

  getSkillStats: () =>
    apiCall('/admin/ky-nangs/thong-ke', {
      method: 'GET'
    }),

  getSkillById: (id) =>
    apiCall(`/admin/ky-nangs/${id}`, {
      method: 'GET'
    }),

  createSkill: (data) =>
    apiCall('/admin/ky-nangs', {
      method: 'POST',
      body: data instanceof FormData ? data : JSON.stringify(data)
    }),

  updateSkill: (id, data) =>
    data instanceof FormData
      ? (() => {
          data.append('_method', 'PUT')
          return apiCall(`/admin/ky-nangs/${id}`, {
            method: 'POST',
            body: data
          })
        })()
      : apiCall(`/admin/ky-nangs/${id}`, {
          method: 'PUT',
          body: JSON.stringify(data)
        }),

  deleteSkill: (id) =>
    apiCall(`/admin/ky-nangs/${id}`, {
      method: 'DELETE'
    })
}

// === Admin Job Posting APIs ===
export const jobPostingService = {
  getJobPostings: (options = {}) => {
    const params = new URLSearchParams()
    if (options.page) params.append('page', options.page)
    if (options.per_page) params.append('per_page', options.per_page)
    if (options.search) params.append('search', options.search)
    if (options.cong_ty_id !== undefined) params.append('cong_ty_id', options.cong_ty_id)
    if (options.trang_thai !== undefined) params.append('trang_thai', options.trang_thai)

    const query = params.toString()
    const endpoint = `/admin/tin-tuyen-dungs${query ? '?' + query : ''}`

    return apiCall(endpoint, {
      method: 'GET'
    })
  },

  getJobPostingStats: () =>
    apiCall('/admin/tin-tuyen-dungs/thong-ke', {
      method: 'GET'
    }),

  getJobPostingById: (id) =>
    apiCall(`/admin/tin-tuyen-dungs/${id}`, {
      method: 'GET'
    }),

  createJobPosting: (data) =>
    apiCall('/admin/tin-tuyen-dungs', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  updateJobPosting: (id, data) =>
    apiCall(`/admin/tin-tuyen-dungs/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    }),

  toggleJobPostingStatus: (id) =>
    apiCall(`/admin/tin-tuyen-dungs/${id}/trang-thai`, {
      method: 'PATCH'
    }),

  deleteJobPosting: (id) =>
    apiCall(`/admin/tin-tuyen-dungs/${id}`, {
      method: 'DELETE'
    })
}

// === Admin Stats APIs ===
export const statsService = {
  getUserStats: () =>
    apiCall('/admin/nguoi-dungs/thong-ke', {
      method: 'GET'
    }),

  getProfileStats: () =>
    apiCall('/admin/ho-sos/thong-ke', {
      method: 'GET'
    }),

  getCompanyStats: () =>
    apiCall('/admin/cong-tys/thong-ke', {
      method: 'GET'
    }),

  getJobPostingStats: () =>
    apiCall('/admin/tin-tuyen-dungs/thong-ke', {
      method: 'GET'
    }),

  getApplicationStats: () =>
    apiCall('/admin/ung-tuyens/thong-ke', {
      method: 'GET'
    }),

  getMatchingStats: () =>
    apiCall('/admin/ket-qua-matchings/thong-ke', {
      method: 'GET'
    }),

  getSavedJobStats: () =>
    apiCall('/admin/luu-tins/thong-ke', {
      method: 'GET'
    }),

  getUserSkillStats: () =>
    apiCall('/admin/nguoi-dung-ky-nangs/thong-ke', {
      method: 'GET'
    }),

  getCareerAdvisingStats: () =>
    apiCall('/admin/tu-van-nghe-nghieps/thong-ke', {
      method: 'GET'
    })
}

export default {
  authService,
  userService,
  companyService,
  industryService,
  skillService,
  jobPostingService,
  statsService
}
