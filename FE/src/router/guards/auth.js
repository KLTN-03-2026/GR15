const safeParse = (value) => {
  if (!value) {
    return null
  }

  try {
    return JSON.parse(value)
  } catch {
    return null
  }
}

export const getAuthSession = () => {
  const accessToken = localStorage.getItem('access_token')
  const userRole = localStorage.getItem('user_role')
  const adminUser = safeParse(localStorage.getItem('admin_user'))
  const employerUser = safeParse(localStorage.getItem('employer_user'))
  const candidateUser = safeParse(localStorage.getItem('user'))

  return {
    accessToken,
    userRole,
    adminUser,
    employerUser,
    candidateUser
  }
}

export const resolveRole = (session = getAuthSession()) => {
  return (
    session.userRole ??
    session.adminUser?.ten_vai_tro ??
    session.adminUser?.vai_tro ??
    session.employerUser?.ten_vai_tro ??
    session.employerUser?.vai_tro ??
    session.candidateUser?.ten_vai_tro ??
    session.candidateUser?.vai_tro ??
    null
  )
}

export const hasRole = (expectedRole) => {
  const session = getAuthSession()
  const role = resolveRole(session)

  if (!session.accessToken || role === null || typeof role === 'undefined') {
    return false
  }

  return String(role).toLowerCase() === String(expectedRole).toLowerCase()
}

export const isAdminAuthenticated = () => {
  const session = getAuthSession()

  if (!session.accessToken) {
    return false
  }

  const role = resolveRole(session)

  return (
    role === 2 ||
    role === '2' ||
    hasRole('admin')
  )
}

export const isEmployerAuthenticated = () => {
  const session = getAuthSession()

  return Boolean(session.accessToken && session.employerUser)
}

export const isCandidateAuthenticated = () => {
  const session = getAuthSession()

  return Boolean(session.accessToken && session.candidateUser)
}
