import { useToast } from 'vue-toastification'
import { extractApiErrorMessage } from '@/utils/apiErrors'

export const useNotify = () => {
  const toast = useToast()

  const success = (message, options = {}) =>
    toast.success(message, options)

  const error = (message, options = {}) =>
    toast.error(message, options)

  const info = (message, options = {}) =>
    toast.info(message, options)

  const warning = (message, options = {}) =>
    toast.warning(message, options)

  const apiError = (err, fallback = 'Đã xảy ra lỗi, vui lòng thử lại.') => {
    toast.error(extractApiErrorMessage(err, fallback))
  }

  const saved = (entity = 'Dữ liệu') => {
    toast.success(`${entity} đã được lưu thành công.`)
  }

  const deleted = (entity = 'Dữ liệu') => {
    toast.success(`${entity} đã được xóa thành công.`)
  }

  const created = (entity = 'Mục mới') => {
    toast.success(`${entity} đã được tạo thành công.`)
  }

  return {
    toast,
    success,
    error,
    info,
    warning,
    apiError,
    saved,
    deleted,
    created,
  }
}
