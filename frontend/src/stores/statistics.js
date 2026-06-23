import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/boot/axios'

export const useStatisticsStore = defineStore('statistics', () => {
  const stats = ref(null)
  const loading = ref(false)
  const error = ref(null)

  async function fetchStatistics(projectId) {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.get(`/projects/${projectId}/statistics/`)
      stats.value = data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to load statistics.'
      stats.value = null
    } finally {
      loading.value = false
    }
  }

  return {
    stats, loading, error,
    fetchStatistics,
  }
})
