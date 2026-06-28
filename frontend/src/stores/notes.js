import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/boot/axios'

export const useNotesStore = defineStore('notes', () => {
  const notes = ref([])
  const loading = ref(false)
  const saving = ref(false)
  const error = ref(null)

  async function fetchNotes(projectId, sceneId) {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.get(`/projects/${projectId}/scenes/${sceneId}/notes/`)
      notes.value = data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to load notes.'
    } finally {
      loading.value = false
    }
  }

  async function createNote(projectId, sceneId, payload) {
    saving.value = true
    error.value = null
    try {
      const { data } = await api.post(`/projects/${projectId}/scenes/${sceneId}/notes/`, payload)
      notes.value.unshift(data)
      return data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to create note.'
      throw err
    } finally {
      saving.value = false
    }
  }

  async function updateNote(projectId, sceneId, noteId, payload) {
    saving.value = true
    error.value = null
    try {
      const { data } = await api.patch(`/projects/${projectId}/scenes/${sceneId}/notes/${noteId}/`, payload)
      const idx = notes.value.findIndex((n) => n.id === noteId)
      if (idx !== -1) {
        notes.value[idx] = data
      }
      return data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to update note.'
      throw err
    } finally {
      saving.value = false
    }
  }

  async function deleteNote(projectId, sceneId, noteId) {
    saving.value = true
    error.value = null
    try {
      await api.delete(`/projects/${projectId}/scenes/${sceneId}/notes/${noteId}/`)
      notes.value = notes.value.filter((n) => n.id !== noteId)
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to delete note.'
      throw err
    } finally {
      saving.value = false
    }
  }

  function clearNotes() {
    notes.value = []
    error.value = null
  }

  return {
    notes, loading, saving, error,
    fetchNotes, createNote, updateNote, deleteNote, clearNotes,
  }
})
