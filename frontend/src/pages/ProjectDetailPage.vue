<template>
  <q-layout>
    <q-page-container>
      <q-page>
        <div class="wda-page">
          <div
            style="
              display: flex;
              align-items: center;
              justify-content: space-between;
              margin-bottom: 16px;
            "
          >
            <q-btn
              flat
              icon="arrow_back"
              label="Back to Dashboard"
              to="/dashboard"
              no-caps
              style="
                font-family: var(--wda-font-ui);
                font-size: 0.85rem;
                color: var(--wda-text-muted);
              "
            />
            <q-btn
              flat
              round
              :icon="$q.dark.isActive ? 'light_mode' : 'dark_mode'"
              @click="$q.dark.toggle()"
              size="sm"
            />
          </div>

          <div v-if="fetching" class="text-center q-mt-xl">
            <q-spinner size="lg" color="primary" />
          </div>

          <div v-else-if="notFound" class="empty-state">
            <q-icon name="error_outline" size="3rem" style="color: var(--wda-text-muted)" />
            <p class="empty-state-title">Project not found</p>
            <p class="empty-state-desc">
              This project doesn't exist or you don't have access to it.
            </p>
            <q-btn unelevated color="primary" label="Back to Dashboard" to="/dashboard" no-caps />
          </div>

          <div v-else-if="project">
            <div class="wda-page-title">{{ project.title }}</div>
            <div class="wda-page-subtitle">Created {{ relativeTime(project.created_at) }}</div>

            <div class="project-detail-grid">
              <div class="action-card" @click="goToWrite">
                <div class="action-icon">
                  <q-icon name="edit_note" size="2rem" color="primary" />
                </div>
                <div class="action-title">Start Writing</div>
                <div class="action-desc">Open the manuscript editor</div>
              </div>

              <div class="action-card" @click="goToStoryBible">
                <div class="action-icon">
                  <q-icon name="menu_book" size="2rem" color="primary" />
                </div>
                <div class="action-title">Story Bible</div>
                <div class="action-desc">Manage characters, places, and timeline</div>
              </div>

              <div class="action-card" @click="showExportDialog = true">
                <div class="action-icon">
                  <q-icon name="download" size="2rem" color="primary" />
                </div>
                <div class="action-title">Export EPUB</div>
                <div class="action-desc">Download your manuscript as an ebook</div>
              </div>

              <div class="action-card" @click="goToStatistics">
                <div class="action-icon">
                  <q-icon name="bar_chart" size="2rem" color="primary" />
                </div>
                <div class="action-title">Statistics</div>
                <div class="action-desc">Track your writing progress</div>
              </div>
            </div>
          </div>

          <ExportDialog
            v-model="showExportDialog"
            :project-id="project?.id"
            :project-title="project?.title"
            :scenes="scenes"
          />
        </div>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProjectsStore } from '@/stores/projects'
import { useScenesStore } from '@/stores/scenes'
import ExportDialog from '@/components/ExportDialog.vue'

const route = useRoute()
const router = useRouter()
const store = useProjectsStore()
const scenesStore = useScenesStore()

const project = ref(null)
const fetching = ref(true)
const notFound = ref(false)
const showExportDialog = ref(false)
const scenes = ref([])

function goToStoryBible() {
  router.push(`/projects/${project.value.id}/story-bible`)
}

function goToWrite() {
  router.push(`/projects/${project.value.id}/write`)
}

function goToStatistics() {
  router.push(`/projects/${project.value.id}/statistics`)
}

onMounted(async () => {
  try {
    project.value = await store.fetchProject(route.params.id)
    await scenesStore.fetchScenes(route.params.id)
    scenes.value = scenesStore.scenes
  } catch (err) {
    if (err.response?.status === 404) {
      notFound.value = true
    }
  } finally {
    fetching.value = false
  }
})

function relativeTime(dateStr) {
  if (!dateStr) return ''
  const now = Date.now()
  const then = new Date(dateStr).getTime()
  const diff = Math.floor((now - then) / 1000)

  if (diff < 60) return 'just now'
  if (diff < 3600) return `${Math.floor(diff / 60)} minute(s) ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)} hour(s) ago`
  if (diff < 2592000) return `${Math.floor(diff / 86400)} day(s) ago`
  if (diff < 31536000) return `${Math.floor(diff / 2592000)} month(s) ago`
  return `${Math.floor(diff / 31536000)} year(s) ago`
}
</script>
