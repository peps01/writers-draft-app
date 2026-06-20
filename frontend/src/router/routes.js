const routes = [
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('@/pages/IndexPage.vue') },
      { path: 'second', component: () => import('@/pages/SecondPage.vue') },
    ],
  },

  {
    path: '/login',
    component: () => import('@/pages/LoginPage.vue'),
    meta: { guest: true },
  },

  {
    path: '/register',
    component: () => import('@/pages/RegisterPage.vue'),
    meta: { guest: true },
  },

  {
    path: '/dashboard',
    component: () => import('@/pages/DashboardPage.vue'),
    meta: { requiresAuth: true },
  },

  {
    path: '/projects/:id',
    component: () => import('@/pages/ProjectDetailPage.vue'),
    meta: { requiresAuth: true },
  },

  {
    path: '/:catchAll(.*)*',
    component: () => import('@/pages/ErrorNotFound.vue'),
  },
]

export default routes
