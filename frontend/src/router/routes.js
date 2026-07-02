const routes = [
  {
    path: '/',
    redirect: '/dashboard',
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
    path: '/verification-sent',
    component: () => import('@/pages/VerificationSentPage.vue'),
    meta: { guest: true },
  },

  {
    path: '/verify-email',
    component: () => import('@/pages/VerifyEmailPage.vue'),
    meta: { guest: true },
  },

  {
    path: '/',
    component: () => import('@/layouts/MainAppLayout.vue'),
    children: [
      {
        path: '/dashboard',
        component: () => import('@/pages/DashboardPage.vue'),
        meta: { requiresAuth: true },
      },

      {
        path: '/projects',
        component: () => import('@/pages/ProjectsPage.vue'),
        meta: { requiresAuth: true },
      },

      {
        path: '/settings',
        component: () => import('@/pages/SettingsPage.vue'),
        meta: { requiresAuth: true },
      },

      {
        path: '/projects/new',
        component: () => import('@/pages/CreateProjectPage.vue'),
        meta: { requiresAuth: true },
      },

      {
        path: '/projects/:id/edit',
        component: () => import('@/pages/CreateProjectPage.vue'),
        meta: { requiresAuth: true },
      },

      {
        path: '/projects/:id',
        redirect: (to) => ({ path: `/projects/${to.params.id}/write` }),
      },

      {
        path: '/projects/:id/story-bible',
        component: () => import('@/pages/StoryBiblePage.vue'),
        meta: { requiresAuth: true },
      },

      {
        path: '/projects/:id/write',
        component: () => import('@/pages/WritePage.vue'),
        meta: { requiresAuth: true },
      },

      {
        path: '/projects/:id/statistics',
        component: () => import('@/pages/StatisticsPage.vue'),
        meta: { requiresAuth: true },
      },
    ],
  },

  {
    path: '/:catchAll(.*)*',
    component: () => import('@/pages/ErrorNotFound.vue'),
  },
]

export default routes
