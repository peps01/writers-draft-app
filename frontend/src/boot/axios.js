import { boot } from 'quasar/wrappers'
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  withCredentials: true,
})

let csrfToken = null

export async function fetchCsrfToken() {
  try {
    const { data } = await api.get('/auth/csrf/')
    csrfToken = data.csrfToken
  } catch {
    csrfToken = null
  }
}

api.interceptors.request.use((config) => {
  if (['post', 'put', 'patch', 'delete'].includes(config.method)) {
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken
    }
  }
  return config
})

api.interceptors.response.use(
  response => response,
  async error => {
    if (!error.response && !error.config._retryCount) {
      error.config._retryCount = (error.config._retryCount || 0) + 1
      if (error.config._retryCount <= 3) {
        await new Promise(r => setTimeout(r, 3000 * error.config._retryCount))
        if (!csrfToken) {
          await fetchCsrfToken()
        }
        return api(error.config)
      }
    }
    if (error.response?.status === 401) {
      const { useAuthStore } = await import('../stores/auth')
      const authStore = useAuthStore()
      authStore.user = null
      window.location.href = '/#/login'
    }
    if (!error.response) {
      console.error('Network error:', error.message)
    }
    return Promise.reject(error)
  }
)

export default boot(async ({ app }) => {
  await fetchCsrfToken()
  app.config.globalProperties.$axios = axios
  app.config.globalProperties.$api = api
})

export { api }
