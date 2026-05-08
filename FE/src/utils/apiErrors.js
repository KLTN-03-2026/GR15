const DEFAULT_API_ERROR_MESSAGE = 'Đã xảy ra lỗi, vui lòng thử lại.'
const VIETNAMESE_CHAR_PATTERN = /[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]/iu
const VIETNAMESE_WORD_PATTERN = /\b(không|vui lòng|hệ thống|đăng nhập|không thể|dữ liệu|quyền|phiên|tài khoản|lỗi|tối thiểu|tối đa)\b/iu

const normalizeString = (value) => (typeof value === 'string' ? value.trim() : '')

const containsAny = (text, needles) =>
  needles.some((needle) => needle && text.includes(needle))

const looksVietnamese = (message) =>
  VIETNAMESE_CHAR_PATTERN.test(message) || VIETNAMESE_WORD_PATTERN.test(message)

const toMessageList = (value) => {
  if (Array.isArray(value)) {
    return value.flatMap((item) => toMessageList(item))
  }

  if (value && typeof value === 'object') {
    return Object.values(value).flatMap((item) => toMessageList(item))
  }

  return value === undefined || value === null ? [] : [value]
}

export const localizeApiErrorText = (value, fallback = DEFAULT_API_ERROR_MESSAGE) => {
  const raw = normalizeString(value)
  if (!raw) {
    return fallback
  }

  const message = raw.toLowerCase()

  if (
    containsAny(message, [
      "'nonetype' object has no attribute 'get'",
      '"nonetype" object has no attribute "get"',
      "has no attribute 'get'",
      'has no attribute "get"',
      'is not subscriptable',
      'cannot unpack non-iterable',
    ])
  ) {
    return 'Hệ thống chưa nhận đủ dữ liệu để xử lý yêu cầu AI. Vui lòng thử lại hoặc bổ sung thêm thông tin đầu vào.'
  }

  if (containsAny(message, ['timed out', 'timeout', 'read timed out', 'operation timed out', 'curl error 28'])) {
    return 'Hệ thống xử lý quá lâu. Vui lòng thử lại sau ít phút.'
  }

  if (containsAny(message, ['internal server error', 'bad gateway', 'service unavailable'])) {
    return 'Hệ thống gặp lỗi khi xử lý yêu cầu. Vui lòng thử lại sau.'
  }

  if (
    containsAny(message, [
      'failed to fetch',
      'networkerror',
      'load failed',
      'connection refused',
      'failed to connect',
      'could not resolve host',
      'name or service not known',
      'network is unreachable',
      'temporary failure in name resolution',
      'curl error 6',
      'curl error 7',
      'max retries exceeded',
    ])
  ) {
    return 'Không thể kết nối tới hệ thống hoặc dịch vụ AI. Vui lòng thử lại sau.'
  }

  if (containsAny(message, ['invalid json', 'json decode', 'expecting value', 'extra data', 'unterminated string'])) {
    return 'Dịch vụ xử lý đang trả về dữ liệu không hợp lệ. Vui lòng thử lại sau.'
  }

  if (containsAny(message, ['field required', 'input should be', 'validation error'])) {
    return 'Dữ liệu gửi lên chưa hợp lệ. Vui lòng kiểm tra lại.'
  }

  if (containsAny(message, ['sqlstate[23000]', 'integrity constraint violation', 'duplicate entry'])) {
    return 'Dữ liệu đã tồn tại hoặc đang được liên kết, nên không thể thực hiện thao tác này.'
  }

  if (containsAny(message, ['sqlstate', 'syntax error or access violation', 'database is locked'])) {
    return 'Hệ thống dữ liệu gặp lỗi khi xử lý yêu cầu. Vui lòng thử lại sau.'
  }

  if (containsAny(message, ['unauthenticated', 'unauthorized'])) {
    return 'Phiên đăng nhập đã hết hạn hoặc chưa hợp lệ. Vui lòng đăng nhập lại.'
  }

  if (containsAny(message, ['forbidden', 'access denied'])) {
    return 'Bạn không có quyền thực hiện thao tác này.'
  }

  if (containsAny(message, ['not found', 'no query results for model'])) {
    return 'Không tìm thấy dữ liệu yêu cầu.'
  }

  if (containsAny(message, ['attributeerror', 'typeerror', 'keyerror', 'indexerror', 'valueerror', 'runtimeerror'])) {
    return 'Hệ thống gặp lỗi xử lý nội bộ. Vui lòng thử lại sau.'
  }

  if (looksVietnamese(raw)) {
    return raw
  }

  return fallback || ''
}

const normalizeFieldErrors = (rawErrors) => {
  if (!rawErrors || typeof rawErrors !== 'object') {
    return {}
  }

  return Object.fromEntries(
    Object.entries(rawErrors).map(([field, messages]) => [
      field,
      (Array.isArray(messages) ? messages : [messages])
        .map((message) => localizeApiErrorText(message, 'Dữ liệu không hợp lệ.'))
        .filter(Boolean),
    ])
  )
}

const normalizeDetails = (rawDetails, baseMessage) => {
  if (!rawDetails) {
    return null
  }

  if (typeof rawDetails === 'string') {
    const detail = localizeApiErrorText(rawDetails, '')
    return !detail || detail === baseMessage ? null : detail
  }

  if (Array.isArray(rawDetails) || typeof rawDetails === 'object') {
    const details = [...new Set(
      toMessageList(rawDetails)
        .map((item) => localizeApiErrorText(item, ''))
        .filter((item) => item && item !== baseMessage)
    )].slice(0, 3)

    return details.length ? details : null
  }

  return null
}

export const normalizeApiErrorObject = (error, fallback = DEFAULT_API_ERROR_MESSAGE) => {
  const source = error && typeof error === 'object' ? error : { message: error }
  const fieldErrors = normalizeFieldErrors(
    source.errors ||
    source.data?.errors ||
    source.response?.data?.errors ||
    null
  )
  const message = localizeApiErrorText(
    source.message ||
    source.data?.message ||
    source.response?.data?.message ||
    '',
    fallback
  )
  const details = normalizeDetails(
    source.details ||
    source.data?.details ||
    source.response?.data?.details ||
    null,
    message
  )
  const normalizedErrors = Object.keys(fieldErrors).length ? fieldErrors : null
  const normalizedData = source.data && typeof source.data === 'object'
    ? {
      ...source.data,
      message,
      details,
      errors: normalizedErrors,
    }
    : source.data

  return {
    ...source,
    message,
    details,
    errors: normalizedErrors,
    ...(normalizedData !== undefined ? { data: normalizedData } : {}),
  }
}

export const extractApiFieldErrors = (error) =>
  normalizeApiErrorObject(error).errors || {}

export const extractApiErrorMessage = (error, fallback = DEFAULT_API_ERROR_MESSAGE) => {
  const normalizedError = normalizeApiErrorObject(error, fallback)
  const fieldMessages = Object.values(normalizedError.errors || {}).flat().filter(Boolean)

  if (fieldMessages.length) {
    return fieldMessages.slice(0, 4).join('\n')
  }

  if (!normalizedError.details) {
    return normalizedError.message
  }

  if (typeof normalizedError.details === 'string') {
    return `${normalizedError.message}\n${normalizedError.details}`
  }

  if (Array.isArray(normalizedError.details)) {
    return `${normalizedError.message}\n${normalizedError.details.join('\n')}`
  }

  return normalizedError.message
}
