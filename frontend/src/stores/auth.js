import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/boot/axios'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const loading = ref(false)

  const isAuthenticated = computed(() => user.value !== null)

  async function login(username, password) {
    const { data } = await api.post('/auth/login/', { username, password })
    user.value = data
  }

  async function register(username, email, password) {
    const { data } = await api.post('/auth/register/', { username, email, password })
    user.value = data
  }

  async function logout() {
    await api.post('/auth/logout/')
    user.value = null
  }

  async function fetchCurrentUser() {
    loading.value = true
    try {
      const { data } = await api.get('/auth/user/')
      user.value = data
    } catch {
      user.value = null
    } finally {
      loading.value = false
    }
  }

  return { user, loading, isAuthenticated, login, register, logout, fetchCurrentUser }
})
