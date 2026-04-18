export const extractApiFieldErrors = (error) => {
  const rawErrors =
    error?.data?.errors ||
    error?.response?.data?.errors ||
    null

  if (!rawErrors || typeof rawErrors !== 'object') {
    return {}
  }

  return Object.fromEntries(
    Object.entries(rawErrors).map(([field, messages]) => [
      field,
      Array.isArray(messages) ? messages.filter(Boolean) : [messages].filter(Boolean),
    ])
  )
}

export const extractApiErrorMessage = (error, fallback = 'Đã xảy ra lỗi, vui lòng thử lại.') => {
  const fieldErrors = extractApiFieldErrors(error)
  const firstFieldMessage = Object.values(fieldErrors).flat().find(Boolean)

  return (
    firstFieldMessage ||
    error?.message ||
    error?.data?.message ||
    error?.response?.data?.message ||
    fallback
  )
}
