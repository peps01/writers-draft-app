import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/boot/axios'

export const usePlacesStore = defineStore('places', () => {
  const places = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function fetchPlaces(projectId) {
    error.value = null
    loading.value = true
    try {
      const { data } = await api.get(`/projects/${projectId}/places/`)
      places.value = data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to load places.'
    } finally {
      loading.value = false
    }
  }

  async function createPlace(projectId, payload) {
    error.value = null
    try {
      const { data } = await api.post(`/projects/${projectId}/places/`, payload)
      places.value.push(data)
      return data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to create place.'
      throw err
    }
  }

  async function updatePlace(projectId, id, payload) {
    error.value = null
    try {
      const { data } = await api.patch(`/projects/${projectId}/places/${id}/`, payload)
      const idx = places.value.findIndex((p) => p.id === id)
      if (idx !== -1) {
        places.value[idx] = data
      }
      return data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to update place.'
      throw err
    }
  }

  async function deletePlace(projectId, id) {
    error.value = null
    try {
      await api.delete(`/projects/${projectId}/places/${id}/`)
      places.value = places.value.filter((p) => p.id !== id)
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to delete place.'
      throw err
    }
  }

  function clearError() {
    error.value = null
  }

  return { places, loading, error, fetchPlaces, createPlace, updatePlace, deletePlace, clearError }
})
