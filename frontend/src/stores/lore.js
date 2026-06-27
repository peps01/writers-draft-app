import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/boot/axios'

export const useLoreStore = defineStore('lore', () => {
  const lore = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function fetchLore(projectId) {
    error.value = null
    loading.value = true
    try {
      const { data } = await api.get(`/projects/${projectId}/lore/`)
      lore.value = data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to load lore.'
    } finally {
      loading.value = false
    }
  }

  async function createLore(projectId, payload) {
    error.value = null
    try {
      const { data } = await api.post(`/projects/${projectId}/lore/`, payload)
      lore.value.push(data)
      return data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to create lore.'
      throw err
    }
  }

  async function updateLore(projectId, id, payload) {
    error.value = null
    try {
      const { data } = await api.patch(`/projects/${projectId}/lore/${id}/`, payload)
      const idx = lore.value.findIndex((l) => l.id === id)
      if (idx !== -1) {
        lore.value[idx] = data
      }
      return data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to update lore.'
      throw err
    }
  }

  async function deleteLore(projectId, id) {
    error.value = null
    try {
      await api.delete(`/projects/${projectId}/lore/${id}/`)
      lore.value = lore.value.filter((l) => l.id !== id)
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to delete lore.'
      throw err
    }
  }

  function clearError() {
    error.value = null
  }

  return { lore, loading, error, fetchLore, createLore, updateLore, deleteLore, clearError }
})
