import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/boot/axios'

export const useScenesStore = defineStore('scenes', () => {
  const scenes = ref([])
  const loading = ref(false)
  const error = ref(null)
  const activeSceneId = ref(null)
  const saveStatus = ref('idle')

  async function fetchScenes(projectId) {
    error.value = null
    loading.value = true
    try {
      const { data } = await api.get(`/projects/${projectId}/scenes/`)
      scenes.value = data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to load scenes.'
    } finally {
      loading.value = false
    }
  }

  async function createScene(projectId, { title }) {
    error.value = null
    try {
      const maxOrder = scenes.value.reduce((max, s) => Math.max(max, s.order), -1)
      const { data } = await api.post(`/projects/${projectId}/scenes/`, {
        title: title || '',
        content: '',
        order: maxOrder + 1,
      })
      scenes.value.push(data)
      return data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to create scene.'
      throw err
    }
  }

  async function deleteScene(projectId, id) {
    error.value = null
    try {
      await api.delete(`/projects/${projectId}/scenes/${id}/`)
      scenes.value = scenes.value.filter((s) => s.id !== id)
      if (activeSceneId.value === id) {
        activeSceneId.value = null
      }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to delete scene.'
      throw err
    }
  }

  async function reorderScenes(projectId, orderedIds) {
    error.value = null
    const previousOrder = [...scenes.value]
    try {
      for (let i = 0; i < orderedIds.length; i++) {
        await api.patch(`/projects/${projectId}/scenes/${orderedIds[i]}/`, { order: i })
      }
      const idMap = {}
      previousOrder.forEach((s) => {
        idMap[s.id] = s
      })
      scenes.value = orderedIds.map((id, i) => ({ ...idMap[id], order: i }))
    } catch (err) {
      await fetchScenes(projectId)
      error.value = 'Failed to save new order. The list has been refreshed from the server.'
      throw err
    }
  }

  async function updateSceneContent(projectId, id, content) {
    saveStatus.value = 'saving'
    error.value = null
    try {
      const { data } = await api.patch(`/projects/${projectId}/scenes/${id}/`, { content })
      const idx = scenes.value.findIndex((s) => s.id === id)
      if (idx !== -1) {
        scenes.value[idx] = data
      }
      saveStatus.value = 'saved'
      return data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to save content.'
      saveStatus.value = 'error'
      throw err
    }
  }

  async function updateSceneMeta(projectId, id, payload) {
    error.value = null
    try {
      const { data } = await api.patch(`/projects/${projectId}/scenes/${id}/`, payload)
      const idx = scenes.value.findIndex((s) => s.id === id)
      if (idx !== -1) {
        scenes.value[idx] = data
      }
      return data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to update scene.'
      throw err
    }
  }

  function setActiveScene(id) {
    activeSceneId.value = id
  }

  function clearError() {
    error.value = null
  }

  return {
    scenes,
    loading,
    error,
    activeSceneId,
    saveStatus,
    fetchScenes,
    createScene,
    deleteScene,
    reorderScenes,
    updateSceneContent,
    updateSceneMeta,
    setActiveScene,
    clearError,
  }
})
