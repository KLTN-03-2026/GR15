import { isEmployerAuthenticated } from './auth'

export const requireEmployerAuth = (to) => {
  if (isEmployerAuthenticated()) {
    return true
  }

  return {
    path: '/employer/auth',
    query: { redirect: to.fullPath }
  }
}

export const redirectEmployerFromLogin = () => {
  if (!isEmployerAuthenticated()) {
    return true
  }

  return { path: '/employer' }
}
