<template>
  <q-layout>
    <q-page-container>
      <q-page>
        <div class="wda-page">
          <div class="dashboard-header">
            <div>
              <div class="wda-page-title">My Projects</div>
              <div class="wda-page-subtitle" style="margin-bottom: 0">
                Continue your writing journey
              </div>
            </div>
            <div class="row items-center q-gutter-sm">
              <q-btn
                flat
                round
                :icon="$q.dark.isActive ? 'light_mode' : 'dark_mode'"
                @click="$q.dark.toggle()"
                size="sm"
              />
              <span
                v-if="authStore.user"
                class="text-caption"
                style="color: var(--wda-text-muted)"
                >{{ authStore.user.username }}</span
              >
              <q-btn
                flat
                dense
                icon="settings"
                label="Settings"
                no-caps
                to="/settings"
                style="font-family: var(--wda-font-ui); font-size: 0.85rem"
              />
              <q-btn
                flat
                dense
                icon="logout"
                label="Logout"
                no-caps
                @click="handleLogout"
                style="font-family: var(--wda-font-ui); font-size: 0.85rem"
              />
              <q-btn
                label="New Project"
                color="primary"
                icon="add"
                unelevated
                @click="showCreateDialog = true"
                no-caps
                style="font-family: var(--wda-font-heading); font-size: 0.9rem"
              />
            </div>
          </div>

          <div v-if="store.loading" class="project-grid">
            <div v-for="n in 6" :key="n" class="wda-card" style="padding: 24px">
              <q-skeleton type="text" class="text-h6" />
              <q-skeleton type="text" width="60%" />
            </div>
          </div>

          <div v-else-if="store.error && store.projects.length === 0" class="empty-state">
            <q-icon name="error_outline" size="3rem" style="color: var(--wda-text-muted)" />
            <p class="empty-state-title">Something went wrong</p>
            <p class="empty-state-desc">{{ store.error }}</p>
            <q-btn
              unelevated
              color="primary"
              label="Retry"
              @click="store.fetchProjects()"
              no-caps
            />
          </div>

          <div v-else-if="store.projects.length === 0" class="empty-state">
            <q-icon name="auto_stories" size="3rem" style="color: var(--wda-text-muted)" />
            <p class="empty-state-title">Your story starts here</p>
            <p class="empty-state-desc">Every masterpiece begins with a single word.</p>
            <q-btn
              unelevated
              color="primary"
              label="Create your first project"
              icon="add"
              @click="showCreateDialog = true"
              no-caps
              style="font-family: var(--wda-font-heading)"
            />
          </div>

          <div v-else class="project-grid">
            <div
              v-for="project in store.projects"
              :key="project.id"
              class="project-card"
              @click="goToProject(project.id)"
              :style="{ borderTopColor: accentColors[project.id % accentColors.length] }"
            >
              <div class="row items-center justify-between no-wrap">
                <div class="project-card-title ellipsis">{{ project.title }}</div>
                <q-btn flat dense round icon="more_vert" size="sm" @click.stop>
                  <q-menu anchor="bottom-end" self="top-end">
                    <q-list dense style="min-width: 120px">
                      <q-item clickable v-close-popup @click.stop="openRename(project)">
                        <q-item-section>Rename</q-item-section>
                      </q-item>
                      <q-item clickable v-close-popup @click.stop="openDelete(project)">
                        <q-item-section class="text-negative">Delete</q-item-section>
                      </q-item>
                    </q-list>
                  </q-menu>
                </q-btn>
              </div>
              <div v-if="projectStats[project.id]" class="project-card-meta q-mb-sm">
                ~{{ formatNumber(projectStats[project.id].total_words) }} words &middot;
                {{ projectStats[project.id].total_scenes }} scenes
              </div>
              <div class="project-card-meta">Edited {{ relativeTime(project.updated_at) }}</div>
            </div>
          </div>
        </div>

        <!-- Dialogs -->
        <q-dialog v-model="showCreateDialog" @before-hide="resetCreateForm">
          <q-card class="wda-card" style="min-width: 350px">
            <q-card-section>
              <div class="text-h6" style="font-family: var(--wda-font-heading)">New Project</div>
            </q-card-section>
            <q-card-section>
              <q-input
                v-model="createTitle"
                label="Project title"
                autofocus
                outlined
                color="primary"
                :error="!!createError"
                :error-message="createError"
                @keyup.enter="submitCreate"
              />
            </q-card-section>
            <q-card-actions align="right">
              <q-btn flat label="Cancel" v-close-popup no-caps />
              <q-btn
                unelevated
                color="primary"
                label="Create"
                :loading="creating"
                no-caps
                @click="submitCreate"
              />
            </q-card-actions>
          </q-card>
        </q-dialog>

        <q-dialog v-model="showRenameDialog">
          <q-card class="wda-card" style="min-width: 350px">
            <q-card-section>
              <div class="text-h6" style="font-family: var(--wda-font-heading)">Rename Project</div>
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
              <q-btn
                unelevated
                color="primary"
                label="Save"
                :loading="renaming"
                no-caps
                @click="submitRename"
              />
            </q-card-actions>
          </q-card>
        </q-dialog>

        <q-dialog v-model="showDeleteDialog">
          <q-card class="wda-card" style="min-width: 350px">
            <q-card-section>
              <div class="text-h6" style="font-family: var(--wda-font-heading)">Delete Project</div>
            </q-card-section>
            <q-card-section>
              <p>
                Are you sure you want to delete '<strong>{{ deleteTarget?.title }}</strong
                >'? This cannot be undone.
              </p>
              <div v-if="deleteError" class="text-negative">{{ deleteError }}</div>
            </q-card-section>
            <q-card-actions align="right">
              <q-btn flat label="Cancel" v-close-popup no-caps />
              <q-btn
                unelevated
                color="negative"
                label="Delete"
                :loading="deleting"
                no-caps
                @click="submitDelete"
              />
            </q-card-actions>
          </q-card>
        </q-dialog>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useProjectsStore } from '@/stores/projects'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/boot/axios'

const router = useRouter()
const store = useProjectsStore()
const authStore = useAuthStore()

const projectStats = ref({})

const accentColors = ['#1B3A6B', '#C9A84C', '#2D6A4F', '#C75D3A', '#7B5EA7']

function formatNumber(n) {
  if (n == null) return '0'
  return n.toLocaleString()
}

async function fetchProjectStats() {
  const fetches = store.projects.map(async (p) => {
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
  await store.fetchProjects()
  if (store.projects.length > 0) {
    fetchProjectStats()
  }
})

watch(
  () => store.projects.length,
  (len) => {
    if (len > 0 && Object.keys(projectStats.value).length === 0) {
      fetchProjectStats()
    }
  },
)

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

function goToProject(id) {
  router.push(`/projects/${id}`)
}

async function handleLogout() {
  try {
    await authStore.logout()
    router.push('/login')
  } catch {
    // error is on store
  }
}

const showCreateDialog = ref(false)
const createTitle = ref('')
const createError = ref('')
const creating = ref(false)

function resetCreateForm() {
  createTitle.value = ''
  createError.value = ''
  creating.value = false
}

async function submitCreate() {
  if (!createTitle.value.trim()) {
    createError.value = 'Title cannot be empty.'
    return
  }
  createError.value = ''
  creating.value = true
  try {
    const project = await store.createProject(createTitle.value.trim())
    showCreateDialog.value = false
    router.push(`/projects/${project.id}`)
  } catch {
    createError.value = store.error || 'Failed to create project.'
  } finally {
    creating.value = false
  }
}

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
    await store.renameProject(renameTarget.value.id, renameTitle.value.trim())
    showRenameDialog.value = false
  } catch {
    renameError.value = store.error || 'Failed to rename project.'
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
    await store.deleteProject(deleteTarget.value.id)
    showDeleteDialog.value = false
  } catch {
    deleteError.value = store.error || 'Failed to delete project.'
  } finally {
    deleting.value = false
  }
}
</script>
