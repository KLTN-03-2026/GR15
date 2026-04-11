const ACCESS_TOKEN_KEY = 'access_token'
const TOKEN_KEY = 'token'
const USER_KEY = 'user'
const EMPLOYER_KEY = 'employer'

const getStorage = () => {
  if (typeof window === 'undefined') return null
  return window.sessionStorage
}

const parseJson = (raw) => {
  if (!raw) return null
  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}

export const emitAuthChanged = () => {
  if (typeof window === 'undefined') return
  window.dispatchEvent(new Event('auth-changed'))
}

export const getAuthToken = () => {
  const storage = getStorage()
  if (!storage) return null
  return storage.getItem(ACCESS_TOKEN_KEY) || storage.getItem(TOKEN_KEY)
}

export const getStoredCandidate = () => {
  const storage = getStorage()
  if (!storage) return null
  return parseJson(storage.getItem(USER_KEY))
}

export const getStoredEmployer = () => {
  const storage = getStorage()
  if (!storage) return null
  return parseJson(storage.getItem(EMPLOYER_KEY))
}

export const getStoredUser = () => getStoredCandidate() || getStoredEmployer()

export const clearAuthStorage = () => {
  if (typeof window === 'undefined') return

  window.sessionStorage.removeItem(ACCESS_TOKEN_KEY)
  window.sessionStorage.removeItem(TOKEN_KEY)
  window.sessionStorage.removeItem(USER_KEY)
  window.sessionStorage.removeItem(EMPLOYER_KEY)

  window.localStorage.removeItem(ACCESS_TOKEN_KEY)
  window.localStorage.removeItem(TOKEN_KEY)
  window.localStorage.removeItem(USER_KEY)
  window.localStorage.removeItem(EMPLOYER_KEY)

  emitAuthChanged()
}

export const persistAuthSession = (token, user) => {
  const storage = getStorage()
  if (!storage) return

  clearAuthStorage()

  if (token) {
    storage.setItem(ACCESS_TOKEN_KEY, token)
    storage.setItem(TOKEN_KEY, token)
  }

  if (user) {
    if (Number(user.vai_tro) === 1) {
      storage.setItem(EMPLOYER_KEY, JSON.stringify(user))
    } else {
      storage.setItem(USER_KEY, JSON.stringify(user))
    }
  }

  emitAuthChanged()
}

export const updateStoredCandidate = (user) => {
  const storage = getStorage()
  if (!storage || !user) return

  storage.setItem(USER_KEY, JSON.stringify(user))
  emitAuthChanged()
}

export const updateStoredEmployer = (user) => {
  const storage = getStorage()
  if (!storage || !user) return

  storage.setItem(EMPLOYER_KEY, JSON.stringify(user))
  emitAuthChanged()
}
