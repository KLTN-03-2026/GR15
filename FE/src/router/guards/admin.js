import { isAdminAuthenticated } from './auth'

export const requireAdminAuth = (to) => {
  if (isAdminAuthenticated()) {
    return true
  }

  return {
    path: '/admin/login',
    query: { redirect: to.fullPath }
  }
}

export const redirectAdminFromLogin = () => {
  if (!isAdminAuthenticated()) {
    return true
  }

  return { path: '/admin' }
}
