import { extractApiErrorMessage } from '@/utils/apiErrors'

const show = (message) => {
  if (typeof window !== 'undefined') {
    window.alert(message)
  }
}

export const useNotify = () => ({
  success: show,
  error: show,
  info: show,
  warning: show,
  apiError: (error, fallback = 'Đã xảy ra lỗi, vui lòng thử lại.') => {
    show(extractApiErrorMessage(error, fallback))
  },
})
