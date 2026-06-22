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
    path: '/dashboard',
    component: () => import('@/pages/DashboardPage.vue'),
    meta: { requiresAuth: true },
  },

  {
    path: '/settings',
    component: () => import('@/pages/SettingsPage.vue'),
    meta: { requiresAuth: true },
  },

  {
    path: '/projects/:id',
    component: () => import('@/pages/ProjectDetailPage.vue'),
    meta: { requiresAuth: true },
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
    path: '/:catchAll(.*)*',
    component: () => import('@/pages/ErrorNotFound.vue'),
  },
]

export default routes
