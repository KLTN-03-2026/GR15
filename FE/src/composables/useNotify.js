const dispatchNotification = (type, message) => {
  if (typeof window === 'undefined' || !message) return

  window.dispatchEvent(new CustomEvent('app-notify', {
    detail: {
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      type,
      message,
    },
  }))
}

export const useNotify = () => {
  const success = (message) => dispatchNotification('success', message)
  const error = (message) => dispatchNotification('error', message)
  const info = (message) => dispatchNotification('info', message)
  const warning = (message) => dispatchNotification('warning', message)

  const apiError = (err, fallback = 'Đã xảy ra lỗi, vui lòng thử lại.') => {
    error(
      err?.message ||
      err?.data?.message ||
      err?.response?.data?.message ||
      fallback
    )
  }

  return {
    success,
    error,
    info,
    warning,
    apiError,
  }
}
