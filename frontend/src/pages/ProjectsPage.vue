<template>
  <q-page class="wda-page">
    <div class="projects-page-header">
      <div>
        <div class="wda-page-title">My Projects</div>
        <div class="projects-page-count">{{ projectsStore.projects.length }} projects</div>
      </div>
      <q-btn unelevated color="primary" label="+ New Project" to="/projects/new" no-caps />
    </div>

    <template v-if="projectsStore.loading && projectsStore.projects.length === 0">
      <div class="projects-page-grid">
        <div v-for="n in 6" :key="n" class="projects-page-card" style="cursor: default">
          <q-skeleton class="card-cover" square />
          <div class="card-info">
            <q-skeleton type="text" />
            <q-skeleton type="text" width="60%" />
          </div>
        </div>
      </div>
    </template>

    <div v-else-if="projectsStore.projects.length === 0" class="empty-state">
      <q-icon name="auto_stories" size="4rem" style="color: var(--wda-text-muted); opacity: 0.4" />
      <p class="empty-state-title">No projects yet</p>
      <p class="empty-state-desc">Every great novel starts with a single chapter.</p>
      <q-btn unelevated color="primary" label="Create your first project" to="/projects/new" />
    </div>

    <div v-else class="projects-page-grid">
      <div
        v-for="project in projectsStore.projects"
        :key="project.id"
        class="projects-page-card"
        @click="openProject(project)"
      >
        <div class="card-cover">
          <img v-if="project.cover_image" :src="project.cover_image" />
          <span v-else class="card-cover-fallback">{{ project.title?.charAt(0)?.toUpperCase() || 'P' }}</span>
        </div>
        <div class="card-info">
          <div class="card-title">{{ project.title }}</div>
          <div class="card-meta">
            <span>{{ formatWordCount(projectStats[project.id]?.total_words) }} &middot; {{ projectStats[project.id]?.scene_count || 0 }} scenes</span>
            <span>{{ lastEdited(project.created_at) }}</span>
          </div>
        </div>
        <div class="card-accent" :style="{ background: accentColors[project.id % accentColors.length] }"></div>
        <div class="card-menu" @click.stop>
          <q-btn flat dense round icon="more_vert" size="sm">
            <q-menu anchor="bottom end" self="top end" :offset="[0, 4]">
              <q-list dense style="min-width: 140px">
                <q-item clickable v-close-popup @click.stop="openEdit(project)">
                  <q-item-section>
                    <div class="row items-center q-gutter-xs">
                      <q-icon name="edit" size="xs" />
                      <span>Edit</span>
                    </div>
                  </q-item-section>
                </q-item>
                <q-item clickable v-close-popup @click.stop="openRename(project)">
                  <q-item-section>
                    <div class="row items-center q-gutter-xs">
                      <q-icon name="drive_file_rename_outline" size="xs" />
                      <span>Rename</span>
                    </div>
                  </q-item-section>
                </q-item>
                <q-separator />
                <q-item clickable v-close-popup @click.stop="openDelete(project)">
                  <q-item-section class="text-negative">
                    <div class="row items-center q-gutter-xs">
                      <q-icon name="delete" size="xs" />
                      <span>Delete</span>
                    </div>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-menu>
          </q-btn>
        </div>
      </div>
    </div>

    <q-dialog v-model="showRenameDialog">
      <q-card class="wda-card" style="min-width: 350px">
        <q-card-section>
          <div class="text-h6" style="font-family: 'Playfair Display', serif">Rename Project</div>
        </q-card-section>
        <q-card-section>
          <q-input
            v-model="renameTitle"
            label="Project title"
            autofocus
            outlined
            color="primary"
            :error="!!renameError"
            :error-message="renameError"
            @keyup.enter="submitRename"
          />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup no-caps />
          <q-btn unelevated color="primary" label="Save" :loading="renaming" no-caps @click="submitRename" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="showDeleteDialog">
      <q-card class="wda-card" style="min-width: 350px">
        <q-card-section>
          <div class="text-h6" style="font-family: 'Playfair Display', serif">Delete Project</div>
        </q-card-section>
        <q-card-section>
          <p>Are you sure you want to delete '<strong>{{ deleteTarget?.title }}</strong>'? This cannot be undone.</p>
          <div v-if="deleteError" class="text-negative">{{ deleteError }}</div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup no-caps />
          <q-btn unelevated color="negative" label="Delete" :loading="deleting" no-caps @click="submitDelete" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProjectsStore } from '@/stores/projects'
import { api } from '@/boot/axios'

const router = useRouter()
const projectsStore = useProjectsStore()

const projectStats = ref({})

const accentColors = ['#F4A825', '#E55A2B', '#2D6A4F', '#4A6FA5', '#9B59B6']

function openProject(project) {
  router.push(`/projects/${project.id}/write`)
}

function openEdit(project) {
  router.push(`/projects/${project.id}/edit`)
}

function formatWordCount(words) {
  if (!words) return '~0 words'
  if (words >= 1000) return `~${(words / 1000).toFixed(1)}k words`
  return `~${words} words`
}

function lastEdited(dateStr) {
  if (!dateStr) return ''
  const seconds = Math.floor((Date.now() - new Date(dateStr).getTime()) / 1000)
  if (seconds < 60) return 'just now'
  const minutes = Math.floor(seconds / 60)
  if (minutes === 1) return '1 minute ago'
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours === 1) return '1 hour ago'
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  const remainingHours = hours % 24
  if (days < 7) {
    if (remainingHours === 0) return days === 1 ? '1 day ago' : `${days} days ago`
    const dayLabel = days === 1 ? '1 day' : `${days} days`
    return `${dayLabel} and ${remainingHours}h ago`
  }
  const weeks = Math.floor(days / 7)
  const remainingDays = days % 7
  if (weeks < 4) {
    if (remainingDays === 0) return weeks === 1 ? '1 week ago' : `${weeks} weeks ago`
    return `${weeks} week${weeks > 1 ? 's' : ''} and ${remainingDays}d ago`
  }
  const months = Math.floor(days / 30)
  if (months < 12) return months === 1 ? '1 month ago' : `${months}mo ago`
  const years = Math.floor(days / 365)
  return years === 1 ? '1 year ago' : `${years}y ago`
}

async function fetchProjectStats() {
  const fetches = projectsStore.projects.map(async (p) => {
    try {
      const { data } = await api.get(`/projects/${p.id}/statistics/`)
      projectStats.value[p.id] = data
    } catch {
      // silently ignore
    }
  })
  await Promise.allSettled(fetches)
}

onMounted(async () => {
  await projectsStore.fetchProjects()
  await fetchProjectStats()
})

// ---- Dialogs ----
const showRenameDialog = ref(false)
const renameTarget = ref(null)
const renameTitle = ref('')
const renameError = ref('')
const renaming = ref(false)

function openRename(project) {
  renameTarget.value = project
  renameTitle.value = project.title
  renameError.value = ''
  renaming.value = false
  showRenameDialog.value = true
}

async function submitRename() {
  if (!renameTitle.value.trim()) {
    renameError.value = 'Title cannot be empty.'
    return
  }
  renameError.value = ''
  renaming.value = true
  try {
    await projectsStore.renameProject(renameTarget.value.id, renameTitle.value.trim())
    showRenameDialog.value = false
    await fetchProjectStats()
  } catch {
    renameError.value = projectsStore.error || 'Failed to rename project.'
  } finally {
    renaming.value = false
  }
}

const showDeleteDialog = ref(false)
const deleteTarget = ref(null)
const deleteError = ref('')
const deleting = ref(false)

function openDelete(project) {
  deleteTarget.value = project
  deleteError.value = ''
  deleting.value = false
  showDeleteDialog.value = true
}

async function submitDelete() {
  deleteError.value = ''
  deleting.value = true
  try {
    await projectsStore.deleteProject(deleteTarget.value.id)
    showDeleteDialog.value = false
    await fetchProjectStats()
  } catch {
    deleteError.value = projectsStore.error || 'Failed to delete project.'
  } finally {
    deleting.value = false
  }
}
</script>

<style scoped>
.projects-page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.projects-page-count {
  font-size: 14px;
  color: var(--wda-text-muted);
  margin-top: 2px;
}

.projects-page-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
  margin-top: 24px;
}

.projects-page-card {
  background: var(--wda-surface);
  border: 1px solid var(--wda-border);
  border-radius: var(--wda-radius);
  overflow: hidden;
  cursor: pointer;
  transition: box-shadow 0.2s ease, transform 0.15s ease;
  position: relative;

  &:hover {
    box-shadow: var(--wda-shadow-md);
    transform: translateY(-2px);

    .card-menu { opacity: 1; }
  }
}

.card-cover {
  width: 100%;
  aspect-ratio: 2/3;
  background: var(--wda-surface-2);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

.card-cover-fallback {
  font-family: var(--wda-font-heading);
  font-size: 4rem;
  font-weight: 700;
  color: var(--wda-primary);
  opacity: 0.4;
}

.card-info {
  padding: 14px 16px;
  border-top: 1px solid var(--wda-border);
}

.card-title {
  font-family: var(--wda-font-heading);
  font-size: 1rem;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 4px;
}

.card-meta {
  font-size: 0.75rem;
  color: var(--wda-text-muted);
  display: flex;
  justify-content: space-between;
}

.card-accent {
  height: 3px;
  background: var(--wda-primary);
}

.card-menu {
  position: absolute;
  top: 8px;
  right: 8px;
  opacity: 0;
  transition: opacity 0.15s ease;
}
</style>
