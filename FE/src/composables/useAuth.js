import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '@/services/api'

export const useAuth = () => {
  const router = useRouter()
  const user = ref(null)
  const isAuthenticated = computed(() => !!user.value)
  const isLoading = ref(false)
  const error = ref('')

  // Load user from localStorage on app initialization
  const loadUser = () => {
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      try {
        user.value = JSON.parse(storedUser)
      } catch (e) {
        console.error('Error loading user from localStorage:', e)
      }
    }
  }

  // Guest/Candidate login
  const loginCandidate = async (email, password) => {
    isLoading.value = true
    error.value = ''
    try {
      const response = await authService.login(email, password)
      const payload = response.data || {}
      const token = payload.access_token || response.access_token || response.token
      const candidateUser = payload.nguoi_dung || payload.user || response.user || null

      if (token && candidateUser) {
        localStorage.setItem('access_token', token)
        localStorage.removeItem('token')
        localStorage.setItem('user', JSON.stringify(candidateUser))
        user.value = candidateUser
        await router.push('/dashboard')
        return response
      }
    } catch (err) {
      error.value = err.message || 'Login failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // Guest/Candidate registration
  const registerCandidate = async (fullName, email, phone, password) => {
    isLoading.value = true
    error.value = ''
    try {
      const response = await authService.registerCandidate(fullName, email, phone, password)
      return response
    } catch (err) {
      error.value = err.message || 'Registration failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // Employer login
  const loginEmployer = async (email, password) => {
    isLoading.value = true
    error.value = ''
    try {
      const response = await authService.loginEmployer(email, password)
      const payload = response.data || {}
      const token = payload.access_token || response.access_token || response.token
      const employerUser = payload.nguoi_dung || payload.employer || payload.user || response.employer || response.user || null

      if (token && employerUser) {
        localStorage.setItem('access_token', token)
        localStorage.removeItem('token')
        localStorage.setItem('employer_user', JSON.stringify(employerUser))
        localStorage.removeItem('employer')
        user.value = employerUser
        await router.push('/employer')
        return response
      }
    } catch (err) {
      error.value = err.message || 'Login failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // Employer registration
  const registerEmployer = async (companyName, contactPerson, email, phone, password) => {
    isLoading.value = true
    error.value = ''
    try {
      const response = await authService.registerEmployer(companyName, contactPerson, email, phone, password)
      return response
    } catch (err) {
      error.value = err.message || 'Registration failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // Logout
  const logout = async () => {
    isLoading.value = true
    try {
      await authService.logout()
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      localStorage.removeItem('access_token')
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.removeItem('employer')
      localStorage.removeItem('employer_user')
      localStorage.removeItem('admin_user')
      localStorage.removeItem('user_role')
      user.value = null
      isLoading.value = false
      await router.push('/')
    }
  }

  // Change password
  const changePassword = async (oldPassword, newPassword, confirmPassword) => {
    isLoading.value = true
    error.value = ''
    try {
      const response = await authService.changePassword(oldPassword, newPassword, confirmPassword)
      return response
    } catch (err) {
      error.value = err.message || 'Password change failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // Forgot password
  const forgotPassword = async (email) => {
    isLoading.value = true
    error.value = ''
    try {
      const response = await authService.forgotPassword(email)
      return response
    } catch (err) {
      error.value = err.message || 'Failed to send reset email'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // Reset password
  const resetPassword = async (token, newPassword, confirmPassword) => {
    isLoading.value = true
    error.value = ''
    try {
      const response = await authService.resetPassword(token, newPassword, confirmPassword)
      return response
    } catch (err) {
      error.value = err.message || 'Password reset failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    loadUser,
    loginCandidate,
    registerCandidate,
    loginEmployer,
    registerEmployer,
    logout,
    changePassword,
    forgotPassword,
    resetPassword
  }
}
