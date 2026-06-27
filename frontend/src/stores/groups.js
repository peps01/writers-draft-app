import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/boot/axios'

export const useGroupsStore = defineStore('groups', () => {
  const groups = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function fetchGroups(projectId) {
    error.value = null
    loading.value = true
    try {
      const { data } = await api.get(`/projects/${projectId}/groups/`)
      groups.value = data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to load groups.'
    } finally {
      loading.value = false
    }
  }

  async function createGroup(projectId, payload) {
    error.value = null
    try {
      const { data } = await api.post(`/projects/${projectId}/groups/`, payload)
      groups.value.push(data)
      return data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to create group.'
      throw err
    }
  }

  async function updateGroup(projectId, id, payload) {
    error.value = null
    try {
      const { data } = await api.patch(`/projects/${projectId}/groups/${id}/`, payload)
      const idx = groups.value.findIndex((g) => g.id === id)
      if (idx !== -1) {
        groups.value[idx] = data
      }
      return data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to update group.'
      throw err
    }
  }

  async function deleteGroup(projectId, id) {
    error.value = null
    try {
      await api.delete(`/projects/${projectId}/groups/${id}/`)
      groups.value = groups.value.filter((g) => g.id !== id)
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to delete group.'
      throw err
    }
  }

  function clearError() {
    error.value = null
  }

  return { groups, loading, error, fetchGroups, createGroup, updateGroup, deleteGroup, clearError }
})
