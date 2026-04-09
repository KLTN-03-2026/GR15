import { isCandidateAuthenticated } from './auth'

export const requireCandidateAuth = (to) => {
  if (isCandidateAuthenticated()) {
    return true
  }

  return {
    path: '/login',
    query: { redirect: to.fullPath }
  }
}

export const redirectCandidateFromLogin = () => {
  if (!isCandidateAuthenticated()) {
    return true
  }

  return { path: '/dashboard' }
}
