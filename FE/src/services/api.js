import { clearAuthStorage, getAuthToken } from '@/utils/authStorage'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

const buildHeaders = (options = {}) => {
  const headers = {
    ...options.headers,
  }

  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = headers['Content-Type'] || 'application/json'
  }

  const token = getAuthToken()
  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  return headers
}

const handleUnauthorized = () => {
  clearAuthStorage()
  window.dispatchEvent(new Event('auth-invalidated'))
}

const apiCall = async (endpoint, options = {}) => {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: buildHeaders(options),
  })

  const contentType = response.headers.get('content-type') || ''
  const data = contentType.includes('application/json')
    ? await response.json()
    : await response.text()

  if (!response.ok) {
    if (response.status === 401) {
      handleUnauthorized()
    }

    throw {
      status: response.status,
      message: data?.message || `Lỗi ${response.status}: ${response.statusText}`,
      data,
    }
  }

  return data
}

export const authService = {
  registerCandidate: (fullName, email, phone, password) =>
    apiCall('/dang-ky', {
      method: 'POST',
      body: JSON.stringify({
        ho_ten: fullName,
        email,
        so_dien_thoai: phone,
        mat_khau: password,
        mat_khau_confirmation: password,
        vai_tro: 0,
      }),
    }),

  login: (email, password) =>
    apiCall('/dang-nhap', {
      method: 'POST',
      body: JSON.stringify({
        email,
        mat_khau: password,
      }),
    }),

  forgotPassword: (email) =>
    apiCall('/quen-mat-khau', {
      method: 'POST',
      body: JSON.stringify({ email }),
    }),

  resetPassword: ({ email, token, password, confirmPassword }) =>
    apiCall('/dat-lai-mat-khau', {
      method: 'POST',
      body: JSON.stringify({
        email,
        token,
        mat_khau: password,
        mat_khau_confirmation: confirmPassword,
      }),
    }),

  changePassword: (oldPassword, newPassword, confirmPassword) =>
    apiCall('/doi-mat-khau', {
      method: 'POST',
      body: JSON.stringify({
        mat_khau_cu: oldPassword,
        mat_khau_moi: newPassword,
        mat_khau_moi_confirmation: confirmPassword,
      }),
    }),

  logout: () =>
    apiCall('/dang-xuat', {
      method: 'POST',
    }),

  getProfile: () =>
    apiCall('/ho-so', {
      method: 'GET',
    }),

  updateProfile: (data) => {
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
      body: JSON.stringify(data),
    })
  },
}

export const jobService = {
  getJobs: (options = {}) => {
    const params = new URLSearchParams()
    if (options.page) params.append('page', options.page)
    if (options.per_page) params.append('per_page', options.per_page)
    if (options.search) params.append('search', options.search)
    if (options.nganh_nghe_id) params.append('nganh_nghe_id', options.nganh_nghe_id)
    if (options.dia_diem) params.append('dia_diem', options.dia_diem)

    const query = params.toString()
    return apiCall(`/tin-tuyen-dungs${query ? `?${query}` : ''}`, { method: 'GET' })
  },

  getJobById: (id) =>
    apiCall(`/tin-tuyen-dungs/${id}`, { method: 'GET' }),

  semanticSearch: (q, top_k = 8) =>
    apiCall(`/tin-tuyen-dungs/semantic-search?q=${encodeURIComponent(q)}&top_k=${top_k}`, { method: 'GET' }),

  getIndustries: (options = {}) => {
    const params = new URLSearchParams()
    if (options.search) params.append('search', options.search)
    if (options.per_page !== undefined) params.append('per_page', options.per_page)
    if (options.goc !== undefined) params.append('goc', options.goc)
    if (options.danh_muc_cha_id) params.append('danh_muc_cha_id', options.danh_muc_cha_id)

    const query = params.toString()
    return apiCall(`/nganh-nghes${query ? `?${query}` : ''}`, { method: 'GET' })
  },

  getIndustryById: (id) =>
    apiCall(`/nganh-nghes/${id}`, { method: 'GET' }),

  getSkills: (options = {}) => {
    const params = new URLSearchParams()
    if (options.search) params.append('search', options.search)
    if (options.per_page !== undefined) params.append('per_page', options.per_page)

    const query = params.toString()
    return apiCall(`/ky-nangs${query ? `?${query}` : ''}`, { method: 'GET' })
  },

  getSkillById: (id) =>
    apiCall(`/ky-nangs/${id}`, { method: 'GET' }),

  getCompanies: (options = {}) => {
    const params = new URLSearchParams()
    if (options.search) params.append('search', options.search)
    if (options.page) params.append('page', options.page)
    if (options.per_page !== undefined) params.append('per_page', options.per_page)

    const query = params.toString()
    return apiCall(`/cong-tys${query ? `?${query}` : ''}`, { method: 'GET' })
  },

  getCompanyById: (id) =>
    apiCall(`/cong-tys/${id}`, { method: 'GET' }),
}

export const savedJobService = {
  getSavedJobs: (options = {}) => {
    const params = new URLSearchParams()
    if (options.page) params.append('page', options.page)
    if (options.per_page) params.append('per_page', options.per_page)

    const query = params.toString()
    return apiCall(`/ung-vien/tin-da-luu${query ? `?${query}` : ''}`, { method: 'GET' })
  },

  toggleSavedJob: (jobId) =>
    apiCall(`/ung-vien/tin-da-luu/${jobId}/toggle`, { method: 'POST' }),
}

export const followCompanyService = {
  getFollowedCompanies: (options = {}) => {
    const params = new URLSearchParams()
    if (options.page) params.append('page', options.page)
    if (options.per_page) params.append('per_page', options.per_page)
    if (options.recent_jobs_limit) params.append('recent_jobs_limit', options.recent_jobs_limit)

    const query = params.toString()
    return apiCall(`/ung-vien/cong-ty-theo-doi${query ? `?${query}` : ''}`, { method: 'GET' })
  },

  toggleFollowCompany: (companyId) =>
    apiCall(`/ung-vien/cong-ty-theo-doi/${companyId}/toggle`, { method: 'POST' }),
}

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
    return apiCall(`/ung-vien/ho-sos${query ? `?${query}` : ''}`, { method: 'GET' })
  },

  getProfileById: (id) =>
    apiCall(`/ung-vien/ho-sos/${id}`, { method: 'GET' }),

  createProfile: (data) =>
    apiCall('/ung-vien/ho-sos', {
      method: 'POST',
      body: data,
    }),

  updateProfile: (id, data) => {
    const payload = new FormData()
    for (const [key, value] of data.entries()) {
      payload.append(key, value)
    }
    payload.append('_method', 'PUT')

    return apiCall(`/ung-vien/ho-sos/${id}`, {
      method: 'POST',
      body: payload,
    })
  },

  toggleProfileStatus: (id) =>
    apiCall(`/ung-vien/ho-sos/${id}/trang-thai`, { method: 'PATCH' }),

  deleteProfile: (id) =>
    apiCall(`/ung-vien/ho-sos/${id}`, { method: 'DELETE' }),

  parseProfileCv: (id) =>
    apiCall(`/ung-vien/ho-sos/${id}/parse`, { method: 'POST' }),
}

export const candidateSkillService = {
  getCatalog: (options = {}) => {
    const params = new URLSearchParams()
    if (options.search) params.append('search', options.search)
    if (options.per_page !== undefined) params.append('per_page', options.per_page)

    const query = params.toString()
    return apiCall(`/ky-nangs${query ? `?${query}` : ''}`, { method: 'GET' })
  },

  getMySkills: () =>
    apiCall('/ung-vien/ky-nangs', { method: 'GET' }),

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
    apiCall(`/ung-vien/ky-nangs/${id}`, { method: 'DELETE' }),
}

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
    return apiCall(`/ung-vien/ung-tuyens${query ? `?${query}` : ''}`, { method: 'GET' })
  },

  apply: ({ tin_tuyen_dung_id, ho_so_id, thu_xin_viec }) =>
    apiCall('/ung-vien/ung-tuyens', {
      method: 'POST',
      body: JSON.stringify({
        tin_tuyen_dung_id,
        ho_so_id,
        thu_xin_viec,
      }),
    }),

  updateApplication: (id, { ho_so_id, thu_xin_viec }) =>
    apiCall(`/ung-vien/ung-tuyens/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({
        ho_so_id,
        thu_xin_viec,
      }),
    }),

  confirmInterviewAttendance: (id, trang_thai_tham_gia_phong_van) =>
    apiCall(`/ung-vien/ung-tuyens/${id}/xac-nhan-phong-van`, {
      method: 'PATCH',
      body: JSON.stringify({
        trang_thai_tham_gia_phong_van,
      }),
    }),

  withdrawApplication: (id) =>
    apiCall(`/ung-vien/ung-tuyens/${id}/rut-don`, {
      method: 'PATCH',
    }),
}

export const matchingService = {
  getMatchingResults: (options = {}) => {
    const params = new URLSearchParams()
    if (options.page) params.append('page', options.page)
    if (options.per_page) params.append('per_page', options.per_page)
    if (options.ho_so_id) params.append('ho_so_id', options.ho_so_id)

    const query = params.toString()
    return apiCall(`/ung-vien/ket-qua-matchings${query ? `?${query}` : ''}`, { method: 'GET' })
  },

  generateMatching: (hoSoId, tinTuyenDungId) =>
    apiCall(`/ung-vien/ho-sos/${hoSoId}/matching`, {
      method: 'POST',
      body: JSON.stringify({
        tin_tuyen_dung_id: tinTuyenDungId,
      }),
    }),
}

export const careerReportService = {
  getReports: (options = {}) => {
    const params = new URLSearchParams()
    if (options.page) params.append('page', options.page)
    if (options.per_page) params.append('per_page', options.per_page)
    if (options.ho_so_id) params.append('ho_so_id', options.ho_so_id)

    const query = params.toString()
    return apiCall(`/ung-vien/tu-van-nghe-nghieps${query ? `?${query}` : ''}`, { method: 'GET' })
  },

  generateReport: (hoSoId) =>
    apiCall(`/ung-vien/ho-sos/${hoSoId}/career-report`, {
      method: 'POST',
    }),
}

export default {
  authService,
  jobService,
  savedJobService,
  followCompanyService,
  profileService,
  candidateSkillService,
  applicationService,
  matchingService,
  careerReportService,
}
