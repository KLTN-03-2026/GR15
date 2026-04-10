import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '@/services/api'
import { clearAuthStorage, getStoredUser } from '@/utils/authStorage'

export const useAuth = () => {
  const router = useRouter()
  const user = ref(null)
  const isAuthenticated = computed(() => !!user.value)
  const isLoading = ref(false)
  const error = ref('')

  const loadUser = () => {
    user.value = getStoredUser()
  }

  // Logout
  const logout = async () => {
    isLoading.value = true
    try {
      await authService.logout()
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      clearAuthStorage()
      user.value = null
      isLoading.value = false
      await router.push('/skills')
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

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    loadUser,
    logout,
    changePassword,
  }
}
