import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/boot/axios'

export const useProjectsStore = defineStore('projects', () => {
  const projects = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function fetchProjects() {
    error.value = null
    loading.value = true
    try {
      const { data } = await api.get('/projects/')
      projects.value = data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to load projects.'
    } finally {
      loading.value = false
    }
  }

  async function fetchProject(id) {
    error.value = null
    loading.value = true
    try {
      const { data } = await api.get(`/projects/${id}/`)
      return data
    } catch (err) {
      if (err.response?.status === 404) {
        error.value = 'Project not found.'
      } else {
        error.value = err.response?.data?.detail || 'Failed to load project.'
      }
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createProject(title) {
    error.value = null
    try {
      const { data } = await api.post('/projects/', { title })
      projects.value.push(data)
      return data
    } catch (err) {
      error.value =
        err.response?.data?.title?.[0] || err.response?.data?.detail || 'Failed to create project.'
      throw err
    }
  }

  async function renameProject(id, newTitle) {
    error.value = null
    try {
      const { data } = await api.patch(`/projects/${id}/`, { title: newTitle })
      const idx = projects.value.findIndex((p) => p.id === id)
      if (idx !== -1) {
        projects.value[idx] = data
      }
      return data
    } catch (err) {
      error.value =
        err.response?.data?.title?.[0] || err.response?.data?.detail || 'Failed to rename project.'
      throw err
    }
  }

  async function deleteProject(id) {
    error.value = null
    try {
      await api.delete(`/projects/${id}/`)
      projects.value = projects.value.filter((p) => p.id !== id)
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to delete project.'
      throw err
    }
  }

  function clearError() {
    error.value = null
  }

  return {
    projects,
    loading,
    error,
    fetchProjects,
    fetchProject,
    createProject,
    renameProject,
    deleteProject,
    clearError,
  }
})
