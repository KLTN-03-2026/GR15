import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '@/services/api'
import { clearAuthStorage, getStoredUser } from '@/utils/authStorage'

export const useAuth = () => {
  const router = useRouter()
  const user = ref(getStoredUser())
  const isAuthenticated = computed(() => Boolean(user.value))
  const isLoading = ref(false)
  const error = ref('')

  const loadUser = () => {
    user.value = getStoredUser()
  }

  const logout = async () => {
    isLoading.value = true

    try {
      await authService.logout()
    } finally {
      clearAuthStorage()
      user.value = null
      isLoading.value = false
      await router.push('/')
    }
  }

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    loadUser,
    logout,
  }
}
