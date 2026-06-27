<template>
  <q-layout view="hHh LpR lFf" class="wda-dashboard-page" :class="{ 'wda-layout--fullscreen': layoutFullscreen }">
    <AppNavbar v-if="!layoutFullscreen" />
    <AppSidebar v-if="!layoutFullscreen" />
    <q-page-container>
      <router-view />
    </q-page-container>

    <ExportDialog
      v-model="showExportDialog"
      :project-id="currentProjectId"
      :project-title="currentProjectTitle"
      :scenes="scenesStore.scenes"
    />
  </q-layout>
</template>

<script setup>
import { ref, computed, watch, provide } from 'vue'
import { useRoute } from 'vue-router'
import { useScenesStore } from '@/stores/scenes'
import { useProjectsStore } from '@/stores/projects'
import AppNavbar from '@/components/AppNavbar.vue'
import AppSidebar from '@/components/AppSidebar.vue'
import ExportDialog from '@/components/ExportDialog.vue'

const route = useRoute()
const scenesStore = useScenesStore()
const projectsStore = useProjectsStore()

const showExportDialog = ref(false)
const layoutFullscreen = ref(false)

provide('layoutFullscreen', layoutFullscreen)

const currentProjectId = computed(() => {
  return route.params.id || null
})

const currentProjectTitle = computed(() => {
  if (!currentProjectId.value) return ''
  const project = projectsStore.projects.find((p) => p.id === currentProjectId.value)
  return project?.title || ''
})

async function openExportDialog() {
  const pid = currentProjectId.value
  if (!pid) return
  await scenesStore.fetchScenes(pid)
  showExportDialog.value = true
}

provide('openExportDialog', openExportDialog)

watch(
  () => route.params.id,
  () => {
    if (showExportDialog.value) {
      showExportDialog.value = false
    }
  },
)
</script>
