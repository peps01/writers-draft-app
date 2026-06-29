<template>
  <q-layout view="hHh LpR lFf" class="wda-dashboard-page" :class="{ 'wda-layout--fullscreen': layoutFullscreen }">
    <AppNavbar v-if="!layoutFullscreen" />
    <AppSidebar v-if="!layoutFullscreen" v-model="sidebarOpen" />
    <button v-if="!layoutFullscreen && !sidebarOpen && $q.screen.gt.sm" class="wda-sidebar-toggle" @click="sidebarOpen = true">
      <span class="material-icons">chevron_right</span>
    </button>
    <AppBottomNav v-if="!layoutFullscreen && $q.screen.lt.md" />
    <q-page-container :class="{ 'with-bottom-nav': $q.screen.lt.md && !bottomNavHidden, 'with-bottom-nav-hidden': $q.screen.lt.md && bottomNavHidden }">
      <router-view />
    </q-page-container>

    <ExportDialog
      v-if="currentProjectId"
      v-model="showExportDialog"
      :project-id="currentProjectId"
      :project-title="currentProjectTitle"
      :scenes="scenesStore.scenes"
    />
  </q-layout>
</template>

<script setup>
import { ref, computed, watch, provide } from 'vue'
import { useQuasar } from 'quasar'
import { useRoute } from 'vue-router'
import { useScenesStore } from '@/stores/scenes'
import { useProjectsStore } from '@/stores/projects'
import AppNavbar from '@/components/AppNavbar.vue'
import AppSidebar from '@/components/AppSidebar.vue'
import AppBottomNav from '@/components/AppBottomNav.vue'
import ExportDialog from '@/components/ExportDialog.vue'

const $q = useQuasar()
const route = useRoute()
const scenesStore = useScenesStore()
const projectsStore = useProjectsStore()

const showExportDialog = ref(false)
const layoutFullscreen = ref(false)
const sidebarOpen = ref($q.screen.gt.sm)
const bottomNavHidden = ref(localStorage.getItem('wda_bottom_nav_hidden') === 'true')

watch(bottomNavHidden, (val) => {
  localStorage.setItem('wda_bottom_nav_hidden', val ? 'true' : '')
})

provide('layoutFullscreen', layoutFullscreen)
provide('bottomNavHidden', bottomNavHidden)

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
