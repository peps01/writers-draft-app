import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/boot/axios'
import { useScenesStore } from '@/stores/scenes'

export const useSceneVersionsStore = defineStore('sceneVersions', () => {
  const versions = ref([])
  const loading = ref(false)
  const hasMore = ref(false)
  const currentPage = ref(1)
  const restoring = ref(false)
  const restoreError = ref(null)

  async function fetchVersions(projectId, sceneId, page = 1) {
    loading.value = true
    try {
      const { data } = await api.get(`/projects/${projectId}/scenes/${sceneId}/versions/`, {
        params: { page },
      })
      if (page === 1) {
        versions.value = data.results
      } else {
        versions.value.push(...data.results)
      }
      hasMore.value = data.next !== null
      currentPage.value = page
    } finally {
      loading.value = false
    }
  }

  async function loadMoreVersions(projectId, sceneId) {
    if (!hasMore.value || loading.value) return
    await fetchVersions(projectId, sceneId, currentPage.value + 1)
  }

  async function restoreVersion(projectId, sceneId, versionId, password) {
    restoring.value = true
    restoreError.value = null
    try {
      const { data } = await api.post(
        `/projects/${projectId}/scenes/${sceneId}/versions/${versionId}/restore/`,
        { password },
      )
      const scenesStore = useScenesStore()
      const idx = scenesStore.scenes.findIndex((s) => s.id === data.id)
      if (idx !== -1) {
        scenesStore.scenes[idx] = data
      }
    } catch (err) {
      if (err.response?.status === 403) {
        restoreError.value = 'Incorrect password.'
      } else {
        restoreError.value = 'Failed to restore version. Please try again.'
      }
    } finally {
      restoring.value = false
    }
  }

  function clearRestoreError() {
    restoreError.value = null
  }

  return {
    versions,
    loading,
    hasMore,
    currentPage,
    restoring,
    restoreError,
    fetchVersions,
    loadMoreVersions,
    restoreVersion,
    clearRestoreError,
  }
})
