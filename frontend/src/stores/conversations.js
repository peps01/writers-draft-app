import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/boot/axios'

export const useConversationsStore = defineStore('conversations', () => {
  const conversation = ref(null)
  const messages = ref([])
  const loading = ref(false)
  const sending = ref(false)
  const checkingContradictions = ref(false)
  const generatingPrompt = ref(false)
  const error = ref(null)
  const isFreeTier = ref(false)

  async function fetchOrCreateConversation(projectId, sceneId) {
    loading.value = true
    try {
      const { data: list } = await api.get(`/projects/${projectId}/conversations/`, {
        params: { scene: sceneId },
      })
      if (list.length > 0) {
        conversation.value = list[0]
      } else {
        const { data } = await api.post(`/projects/${projectId}/conversations/`, {
          scene: sceneId,
        })
        conversation.value = data
      }
    } finally {
      loading.value = false
    }
  }

  async function fetchMessages(projectId) {
    if (!conversation.value) return
    loading.value = true
    try {
      const { data } = await api.get(
        `/projects/${projectId}/conversations/${conversation.value.id}/messages/`
      )
      messages.value = data
    } finally {
      loading.value = false
    }
  }

  async function sendMessage(projectId, content) {
    if (!conversation.value) return
    sending.value = true
    error.value = null
    try {
      const { data } = await api.post(
        `/projects/${projectId}/conversations/${conversation.value.id}/messages/`,
        { content },
      )
      messages.value.push(data.user_message)
      messages.value.push(data.assistant_message)
      isFreeTier.value = data.is_free_tier
    } catch (err) {
      const detail = err.response?.data?.error || err.response?.data?.detail || ''
      const status = err.response?.status || 0
      if (status === 503) {
        error.value = detail || 'AI assistant is not configured.'
      } else if (status === 502) {
        error.value = detail || 'AI service error. Try again.'
      } else if (status === 0) {
        error.value = 'Network error. Check your connection.'
      } else {
        error.value = detail || `Request failed (${status}). Try again.`
      }
    } finally {
      sending.value = false
    }
  }

  async function generateWritingPrompt(projectId, sceneId) {
    generatingPrompt.value = true
    error.value = null
    try {
      const { data } = await api.post(
        `/projects/${projectId}/scenes/${sceneId}/writing-prompt/`
      )
      messages.value.push(data.message)
    } catch (err) {
      const detail = err.response?.data?.error || err.response?.data?.detail || ''
      const status = err.response?.status || 0
      if (status === 503) {
        error.value = detail || 'AI assistant is not configured.'
      } else if (status === 502) {
        error.value = detail || 'AI service error. Try again.'
      } else if (status === 0) {
        error.value = 'Network error. Check your connection.'
      } else {
        error.value = detail || `Request failed (${status}). Try again.`
      }
    } finally {
      generatingPrompt.value = false
    }
  }

  async function checkContradictions(projectId, sceneId) {
    if (!conversation.value) return
    checkingContradictions.value = true
    error.value = null
    try {
      const { data } = await api.post(
        `/projects/${projectId}/scenes/${sceneId}/check-contradictions/`
      )
      messages.value.push(data)
    } catch (err) {
      const detail = err.response?.data?.error || err.response?.data?.detail || ''
      const status = err.response?.status || 0
      if (status === 503) {
        error.value = detail || 'AI assistant is not configured.'
      } else if (status === 502) {
        error.value = detail || 'AI service error. Try again.'
      } else if (status === 0) {
        error.value = 'Network error. Check your connection.'
      } else {
        error.value = detail || `Request failed (${status}). Try again.`
      }
    } finally {
      checkingContradictions.value = false
    }
  }

  function reset() {
    conversation.value = null
    messages.value = []
    loading.value = false
    sending.value = false
    checkingContradictions.value = false
    generatingPrompt.value = false
    error.value = null
    isFreeTier.value = false
  }

  return {
    conversation, messages, loading, sending, checkingContradictions, generatingPrompt, error, isFreeTier,
    fetchOrCreateConversation, fetchMessages, sendMessage, checkContradictions, generateWritingPrompt, reset,
  }
})
