<template>
  <q-layout>
    <q-page-container>
      <q-page class="q-pa-md">
        <div class="row items-center justify-between q-mb-md">
          <div class="text-h5">My Projects</div>
          <q-btn label="New Project" color="primary" icon="add" @click="showCreateDialog = true" no-caps />
        </div>

        <div v-if="store.loading" class="row q-col-gutter-md">
          <div v-for="n in 6" :key="n" class="col-12 col-sm-6 col-md-4">
            <q-card flat bordered>
              <q-card-section>
                <q-skeleton type="text" class="text-h6" />
                <q-skeleton type="text" width="60%" />
              </q-card-section>
            </q-card>
          </div>
        </div>

        <div v-else-if="store.error && store.projects.length === 0" class="text-center q-mt-xl">
          <div class="text-negative q-mb-md">{{ store.error }}</div>
          <q-btn label="Retry" color="primary" @click="store.fetchProjects()" no-caps />
        </div>

        <div v-else-if="store.projects.length === 0" class="text-center q-mt-xl">
          <div class="text-h6 q-mb-sm">No projects yet</div>
          <div class="text-grey q-mb-md">Create your first project to get started.</div>
          <q-btn label="Create your first project" color="primary" icon="add" @click="showCreateDialog = true" no-caps />
        </div>

        <div v-else class="row q-col-gutter-md">
          <div v-for="project in store.projects" :key="project.id" class="col-12 col-sm-6 col-md-4">
            <q-card flat bordered class="cursor-pointer" @click="goToProject(project.id)">
              <q-card-section>
                <div class="row items-center justify-between no-wrap">
                  <div class="text-h6 ellipsis">{{ project.title }}</div>
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
                <div class="text-caption text-grey">Updated {{ relativeTime(project.updated_at) }}</div>
              </q-card-section>
            </q-card>
          </div>
        </div>

        <q-dialog v-model="showCreateDialog" @before-hide="resetCreateForm">
          <q-card style="min-width: 350px">
            <q-card-section>
              <div class="text-h6">New Project</div>
            </q-card-section>
            <q-card-section>
              <q-input v-model="createTitle" label="Project title" autofocus :error="!!createError" :error-message="createError" @keyup.enter="submitCreate" />
            </q-card-section>
            <q-card-actions align="right">
              <q-btn flat label="Cancel" v-close-popup no-caps />
              <q-btn color="primary" label="Create" :loading="creating" no-caps @click="submitCreate" />
            </q-card-actions>
          </q-card>
        </q-dialog>

        <q-dialog v-model="showRenameDialog">
          <q-card style="min-width: 350px">
            <q-card-section>
              <div class="text-h6">Rename Project</div>
            </q-card-section>
            <q-card-section>
              <q-input v-model="renameTitle" label="Project title" autofocus :error="!!renameError" :error-message="renameError" @keyup.enter="submitRename" />
            </q-card-section>
            <q-card-actions align="right">
              <q-btn flat label="Cancel" v-close-popup no-caps />
              <q-btn color="primary" label="Save" :loading="renaming" no-caps @click="submitRename" />
            </q-card-actions>
          </q-card>
        </q-dialog>

        <q-dialog v-model="showDeleteDialog">
          <q-card style="min-width: 350px">
            <q-card-section>
              <div class="text-h6">Delete Project</div>
            </q-card-section>
            <q-card-section>
              <p>Are you sure you want to delete '<strong>{{ deleteTarget?.title }}</strong>'? This cannot be undone.</p>
              <div v-if="deleteError" class="text-negative">{{ deleteError }}</div>
            </q-card-section>
            <q-card-actions align="right">
              <q-btn flat label="Cancel" v-close-popup no-caps />
              <q-btn color="negative" label="Delete" :loading="deleting" no-caps @click="submitDelete" />
            </q-card-actions>
          </q-card>
        </q-dialog>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProjectsStore } from '@/stores/projects'
const router = useRouter()
const store = useProjectsStore()

onMounted(() => {
  store.fetchProjects()
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

function goToProject(id) {
  router.push(`/projects/${id}`)
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
