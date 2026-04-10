/**
 * useNotify — Composable thông báo đơn giản
 * Dùng console.warn để tránh phụ thuộc thư viện ngoài.
 * Có thể nâng cấp sau bằng toast lib.
 */
export const useNotify = () => {
  const apiError = (error, fallbackMsg = 'Đã có lỗi xảy ra.') => {
    const msg = error?.message || fallbackMsg
    console.warn('[Notify apiError]', msg, error)
  }

  const success = (msg) => {
    console.info('[Notify success]', msg)
  }

  return { apiError, success }
}
