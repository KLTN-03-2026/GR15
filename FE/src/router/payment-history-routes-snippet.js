{
  path: '/payments',
  name: 'Payments',
  component: () => import('@/components/Dashboard/PaymentsPage.vue'),
  meta: { layout: 'dashboard', requiresAuth: true, role: ROLE_CANDIDATE }
},
{
  path: '/payments/:maGiaoDichNoiBo',
  name: 'PaymentDetail',
  component: () => import('@/components/Dashboard/PaymentDetailPage.vue'),
  meta: { layout: 'dashboard', requiresAuth: true, role: ROLE_CANDIDATE }
}
