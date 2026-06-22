import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/boot/axios'

export const useCharactersStore = defineStore('characters', () => {
  const characters = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function fetchCharacters(projectId) {
    error.value = null
    loading.value = true
    try {
      const { data } = await api.get(`/projects/${projectId}/characters/`)
      characters.value = data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to load characters.'
    } finally {
      loading.value = false
    }
  }

  async function createCharacter(projectId, payload) {
    error.value = null
    try {
      const { data } = await api.post(`/projects/${projectId}/characters/`, payload)
      characters.value.push(data)
      return data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to create character.'
      throw err
    }
  }

  async function updateCharacter(projectId, id, payload) {
    error.value = null
    try {
      const { data } = await api.patch(`/projects/${projectId}/characters/${id}/`, payload)
      const idx = characters.value.findIndex((c) => c.id === id)
      if (idx !== -1) {
        characters.value[idx] = data
      }
      return data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to update character.'
      throw err
    }
  }

  async function deleteCharacter(projectId, id) {
    error.value = null
    try {
      await api.delete(`/projects/${projectId}/characters/${id}/`)
      characters.value = characters.value.filter((c) => c.id !== id)
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to delete character.'
      throw err
    }
  }

  function clearError() {
    error.value = null
  }

  return {
    characters,
    loading,
    error,
    fetchCharacters,
    createCharacter,
    updateCharacter,
    deleteCharacter,
    clearError,
  }
})
