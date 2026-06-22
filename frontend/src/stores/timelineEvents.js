import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/boot/axios'

export const useTimelineEventsStore = defineStore('timelineEvents', () => {
  const timelineEvents = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function fetchTimelineEvents(projectId) {
    error.value = null
    loading.value = true
    try {
      const { data } = await api.get(`/projects/${projectId}/timeline-events/`)
      timelineEvents.value = data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to load timeline events.'
    } finally {
      loading.value = false
    }
  }

  async function createTimelineEvent(projectId, payload) {
    error.value = null
    try {
      const { data } = await api.post(`/projects/${projectId}/timeline-events/`, payload)
      timelineEvents.value.push(data)
      return data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to create timeline event.'
      throw err
    }
  }

  async function updateTimelineEvent(projectId, id, payload) {
    error.value = null
    try {
      const { data } = await api.patch(`/projects/${projectId}/timeline-events/${id}/`, payload)
      const idx = timelineEvents.value.findIndex((e) => e.id === id)
      if (idx !== -1) {
        timelineEvents.value[idx] = data
      }
      return data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to update timeline event.'
      throw err
    }
  }

  async function deleteTimelineEvent(projectId, id) {
    error.value = null
    try {
      await api.delete(`/projects/${projectId}/timeline-events/${id}/`)
      timelineEvents.value = timelineEvents.value.filter((e) => e.id !== id)
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to delete timeline event.'
      throw err
    }
  }

  async function reorderTimelineEvents(projectId, orderedIds) {
    error.value = null
    const previousOrder = [...timelineEvents.value]
    try {
      for (let i = 0; i < orderedIds.length; i++) {
        await api.patch(`/projects/${projectId}/timeline-events/${orderedIds[i]}/`, { order: i })
      }
      const idMap = {}
      previousOrder.forEach((e) => {
        idMap[e.id] = e
      })
      timelineEvents.value = orderedIds.map((id, i) => ({ ...idMap[id], order: i }))
    } catch (err) {
      await fetchTimelineEvents(projectId)
      error.value = 'Failed to save new order. The list has been refreshed from the server.'
      throw err
    }
  }

  function clearError() {
    error.value = null
  }

  return {
    timelineEvents,
    loading,
    error,
    fetchTimelineEvents,
    createTimelineEvent,
    updateTimelineEvent,
    deleteTimelineEvent,
    reorderTimelineEvents,
    clearError,
  }
})
