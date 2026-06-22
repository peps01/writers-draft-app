import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/boot/axios'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const loading = ref(false)

  const isAuthenticated = computed(() => user.value !== null)

  const hasGeminiKey = computed(() => user.value?.has_gemini_key ?? false)
  const isPaidTier = computed(() => user.value?.is_paid_tier ?? false)

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

  async function updateProfile(geminiApiKey, isPaidTier) {
    const payload = {}
    if (geminiApiKey !== undefined) {
      payload.gemini_api_key = geminiApiKey
    }
    if (isPaidTier !== undefined) {
      payload.is_paid_tier = isPaidTier
    }
    const { data } = await api.patch('/auth/profile/', payload)
    if (user.value) {
      user.value.has_gemini_key = data.gemini_api_key_set
      user.value.is_paid_tier = data.is_paid_tier
    }
    return data
  }

  return {
    user, loading, isAuthenticated, hasGeminiKey, isPaidTier,
    login, register, logout, fetchCurrentUser, updateProfile,
  }
})
