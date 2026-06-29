import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/boot/axios'

export const useSearchStore = defineStore('search', () => {
  const query = ref('')
  const results = ref([])
  const loading = ref(false)
  const error = ref(null)
  const totalMatches = ref(0)
  const totalScenes = ref(0)
  const hasMore = ref(false)
  const showDropdown = ref(false)
  const showFullPanel = ref(false)
  const lastQuery = ref('')
  const currentLimit = ref(20)
  const currentOffset = ref(0)

  let searchTimeout = null

  function debouncedSearch(projectId, q) {
    clearTimeout(searchTimeout)
    query.value = q
    if (q.length < 3) {
      results.value = []
      showDropdown.value = false
      loading.value = false
      currentOffset.value = 0
      return
    }
    loading.value = true
    currentOffset.value = 0
    searchTimeout = setTimeout(async () => {
      try {
        const { data } = await api.get(`/projects/${projectId}/search/`, {
          params: { q, limit: currentLimit.value, offset: 0 },
        })
        results.value = data.results
        totalMatches.value = data.total_matches
        totalScenes.value = data.total_scenes
        hasMore.value = data.has_more
        lastQuery.value = q
        currentOffset.value = data.results.length
        showDropdown.value = data.results.length > 0
        error.value = null
      } catch {
        error.value = 'Search failed. Try again.'
      } finally {
        loading.value = false
      }
    }, 400)
  }

  async function loadMore(projectId) {
    if (loading.value || !hasMore.value) return
    loading.value = true
    try {
      const { data } = await api.get(`/projects/${projectId}/search/`, {
        params: { q: lastQuery.value, limit: currentLimit.value, offset: currentOffset.value },
      })
      results.value = [...results.value, ...data.results]
      totalMatches.value = data.total_matches
      totalScenes.value = data.total_scenes
      hasMore.value = data.has_more
      currentOffset.value += data.results.length
      error.value = null
    } catch {
      error.value = 'Search failed. Try again.'
    } finally {
      loading.value = false
    }
  }

  function clearSearch() {
    clearTimeout(searchTimeout)
    query.value = ''
    results.value = []
    loading.value = false
    error.value = null
    totalMatches.value = 0
    totalScenes.value = 0
    hasMore.value = false
    showDropdown.value = false
    showFullPanel.value = false
    lastQuery.value = ''
    currentOffset.value = 0
  }

  function openFullPanel() {
    showDropdown.value = false
    showFullPanel.value = true
  }

  function closeFullPanel() {
    showFullPanel.value = false
  }

  return {
    query,
    results,
    loading,
    error,
    totalMatches,
    totalScenes,
    hasMore,
    showDropdown,
    showFullPanel,
    lastQuery,
    debouncedSearch,
    loadMore,
    clearSearch,
    openFullPanel,
    closeFullPanel,
  }
})
