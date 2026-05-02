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
  const fieldMessages = Object.values(fieldErrors).flat().filter(Boolean)

  if (fieldMessages.length) {
    return fieldMessages.slice(0, 4).join('\n')
  }

  return error?.message || error?.data?.message || error?.response?.data?.message || fallback
}
