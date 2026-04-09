import { createRouter, createWebHistory } from 'vue-router'
import { redirectAdminFromLogin, requireAdminAuth } from './guards/admin'
import { redirectEmployerFromLogin, requireEmployerAuth } from './guards/employer'
import { redirectCandidateFromLogin, requireCandidateAuth } from './guards/candidate'

const routes = [
  // Guest pages
  {
    path: '/',
    name: 'Landing',
    component: () => import('@/components/Guest/LandingPage.vue'),
    meta: { layout: 'guest' }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/components/Guest/AuthPage.vue'),
    meta: { layout: 'auth' },
    beforeEnter: redirectCandidateFromLogin
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/components/Guest/RegisterPage.vue'),
    meta: { layout: 'auth' }
  },
  {
    path: '/auth',
    name: 'Auth',
    component: () => import('@/components/Guest/AuthPage.vue'),
    meta: { layout: 'guest' }
  },
  {
    path: '/employer/auth',
    name: 'EmployerAuth',
    component: () => import('@/components/Employer/EmployerAuthPage.vue'),
    meta: { layout: 'guest' },
    beforeEnter: redirectEmployerFromLogin
  },
  {
    path: '/employer/register',
    name: 'EmployerRegister',
    component: () => import('@/components/Employer/EmployerRegisterPage.vue'),
    meta: { layout: 'auth' }
  },
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: () => import('@/components/Admin/AdminAuthPage.vue'),
    meta: { layout: 'auth' },
    beforeEnter: redirectAdminFromLogin
  },
  {
    path: '/jobs',
    name: 'JobSearch',
    component: () => import('@/components/Guest/JobSearchPage.vue'),
    meta: { layout: 'guest' }
  },
  {
    path: '/jobs/:id',
    name: 'JobDetail',
    component: () => import('@/components/Guest/JobDetailPage.vue'),
    meta: { layout: 'guest' }
  },
  {
    path: '/ai-career',
    name: 'AICareer',
    component: () => import('@/components/Guest/AICareerPage.vue'),
    meta: { layout: 'guest' }
  },
  // Dashboard pages (Job Seeker)
  {
    path: '/dashboard',
    name: 'SeekerDashboard',
    component: () => import('@/components/Dashboard/SeekerDashboardPage.vue'),
    meta: { layout: 'dashboard' },
    beforeEnter: requireCandidateAuth
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/components/Dashboard/ProfilePage.vue'),
    meta: { layout: 'dashboard' },
    beforeEnter: requireCandidateAuth
  },
  {
    path: '/my-cv',
    name: 'MyCv',
    component: () => import('@/components/Dashboard/MyCvPage.vue'),
    meta: { layout: 'dashboard' },
    beforeEnter: requireCandidateAuth
  },
  {
    path: '/applications',
    name: 'Applications',
    component: () => import('@/components/Dashboard/ApplicationsPage.vue'),
    meta: { layout: 'dashboard' },
    beforeEnter: requireCandidateAuth
  },
  {
    path: '/saved-jobs',
    name: 'SavedJobs',
    component: () => import('@/components/Dashboard/SavedJobsPage.vue'),
    meta: { layout: 'dashboard' },
    beforeEnter: requireCandidateAuth
  },
  {
    path: '/matched-jobs',
    name: 'MatchedJobs',
    component: () => import('@/components/Dashboard/MatchedJobsPage.vue'),
    meta: { layout: 'dashboard' },
    beforeEnter: requireCandidateAuth
  },
    // Employer pages
  {
    path: '/employer',
    name: 'EmployerDashboard',
    component: () => import('@/components/Employer/EmployerDashboardPage.vue'),
    meta: { layout: 'employer' },
    beforeEnter: requireEmployerAuth
  },
  {
    path: '/employer/jobs',
    name: 'EmployerJobs',
    component: () => import('@/components/Employer/EmployerJobsPage.vue'),
    meta: { layout: 'employer' },
    beforeEnter: requireEmployerAuth
  },
  {
    path: '/employer/candidates',
    name: 'EmployerCandidates',
    component: () => import('@/components/Employer/EmployerCandidatesPage.vue'),
    meta: { layout: 'employer' },
    beforeEnter: requireEmployerAuth
  },
  {
    path: '/employer/interviews',
    name: 'EmployerInterviews',
    component: () => import('@/components/Employer/EmployerInterviewsPage.vue'),
    meta: { layout: 'employer' },
    beforeEnter: requireEmployerAuth
  },
  {
    path: '/employer/company',
    name: 'EmployerCompany',
    component: () => import('@/components/Employer/EmployerCompanyPage.vue'),
    meta: { layout: 'employer' },
    beforeEnter: requireEmployerAuth
  },
  // Admin pages
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: () => import('@/components/Admin/AdminDashboardPage.vue'),
    meta: { layout: 'admin' },
    beforeEnter: requireAdminAuth
  },
  {
    path: '/admin/profile',
    name: 'AdminProfile',
    component: () => import('@/components/Admin/AdminProfilePage.vue'),
    meta: { layout: 'admin' },
    beforeEnter: requireAdminAuth
  },
  {
    path: '/admin/users',
    name: 'UserManagement',
    component: () => import('@/components/Admin/UserManagementPage.vue'),
    meta: { layout: 'admin' },
    beforeEnter: requireAdminAuth
  },
  {
    path: '/admin/companies',
    name: 'CompanyManagement',
    component: () => import('@/components/Admin/CompanyManagementPage.vue'),
    meta: { layout: 'admin' },
    beforeEnter: requireAdminAuth
  },
  {
    path: '/admin/industries',
    name: 'IndustryManagement',
    component: () => import('@/components/Admin/IndustryManagementPage.vue'),
    meta: { layout: 'admin' },
    beforeEnter: requireAdminAuth
  },
  {
    path: '/admin/skills',
    name: 'SkillManagement',
    component: () => import('@/components/Admin/SkillManagementPage.vue'),
    meta: { layout: 'admin' },
    beforeEnter: requireAdminAuth
  },
  {
    path: '/admin/jobs',
    name: 'JobPostingsManagement',
    component: () => import('@/components/Admin/JobPostingsManagementPage.vue'),
    meta: { layout: 'admin' },
    beforeEnter: requireAdminAuth
  },
  {
    path: '/admin/stats',
    name: 'StatsManagement',
    component: () => import('@/components/Admin/StatsManagementPage.vue'),
    meta: { layout: 'admin' },
    beforeEnter: requireAdminAuth
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

export default router
