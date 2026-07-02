import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api, fetchCsrfToken } from '@/boot/axios'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const loading = ref(false)

  const isAuthenticated = computed(() => user.value !== null)

  const hasGeminiKey = computed(() => user.value?.has_gemini_key ?? false)
  const geminiApiKeyPreview = computed(() => user.value?.gemini_api_key_preview ?? null)
  const isPaidTier = computed(() => user.value?.is_paid_tier ?? false)
  const dailyWordGoal = computed(() => user.value?.daily_word_goal ?? null)
  const showWordGoal = computed(() => user.value?.show_word_goal ?? false)

  async function login(username, password) {
    const { data } = await api.post('/auth/login/', { username, password })
    user.value = data
    await fetchCsrfToken()
  }

  async function register(username, email, password) {
    const { data } = await api.post('/auth/register/', { username, email, password })
    return data
  }

  async function logout() {
    try {
      await api.post('/auth/logout/')
    } catch {
      // Log out locally even if the server is unreachable
    }
    user.value = null
    await fetchCsrfToken()
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

  async function updateProfile({
    geminiApiKey,
    isPaidTier,
    showWordGoal,
    dailyWordGoal,
    includeKey = false,
  } = {}) {
    const payload = {}
    if (includeKey && geminiApiKey !== undefined) {
      payload.gemini_api_key = geminiApiKey
    }
    if (isPaidTier !== undefined) {
      payload.is_paid_tier = isPaidTier
    }
    if (dailyWordGoal !== undefined) {
      payload.daily_word_goal = dailyWordGoal
    }
    if (showWordGoal !== undefined) {
      payload.show_word_goal = showWordGoal
    }
    const { data } = await api.patch('/auth/profile/', payload)
    if (user.value) {
      user.value.has_gemini_key = data.gemini_api_key_set
      user.value.gemini_api_key_preview = data.gemini_api_key_preview
      user.value.is_paid_tier = data.is_paid_tier
      user.value.daily_word_goal = data.daily_word_goal
      user.value.show_word_goal = data.show_word_goal
    }
    return data
  }

  async function testKey() {
    const { data } = await api.post('/auth/profile/test-key/')
    return data
  }

  return {
    user,
    loading,
    isAuthenticated,
    hasGeminiKey,
    geminiApiKeyPreview,
    isPaidTier,
    dailyWordGoal,
    showWordGoal,
    login,
    register,
    logout,
    fetchCurrentUser,
    updateProfile,
    testKey,
  }
})
