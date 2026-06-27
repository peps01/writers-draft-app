import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/boot/axios'

export const useItemsStore = defineStore('items', () => {
  const items = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function fetchItems(projectId) {
    error.value = null
    loading.value = true
    try {
      const { data } = await api.get(`/projects/${projectId}/items/`)
      items.value = data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to load items.'
    } finally {
      loading.value = false
    }
  }

  async function createItem(projectId, payload) {
    error.value = null
    try {
      const { data } = await api.post(`/projects/${projectId}/items/`, payload)
      items.value.push(data)
      return data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to create item.'
      throw err
    }
  }

  async function updateItem(projectId, id, payload) {
    error.value = null
    try {
      const { data } = await api.patch(`/projects/${projectId}/items/${id}/`, payload)
      const idx = items.value.findIndex((i) => i.id === id)
      if (idx !== -1) {
        items.value[idx] = data
      }
      return data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to update item.'
      throw err
    }
  }

  async function deleteItem(projectId, id) {
    error.value = null
    try {
      await api.delete(`/projects/${projectId}/items/${id}/`)
      items.value = items.value.filter((i) => i.id !== id)
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to delete item.'
      throw err
    }
  }

  function clearError() {
    error.value = null
  }

  return { items, loading, error, fetchItems, createItem, updateItem, deleteItem, clearError }
})
