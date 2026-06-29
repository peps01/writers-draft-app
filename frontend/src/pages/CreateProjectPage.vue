<template>
  <q-page class="create-project-page">
    <div class="create-project-header">
      <div>
        <div class="wda-page-title">{{ isEdit ? 'Edit Project' : 'New Project' }}</div>
        <div class="create-project-subtitle">
          {{ isEdit ? 'Update your project details' : 'Create a new writing project' }}
        </div>
      </div>
      <q-btn flat label="Cancel" no-caps :to="cancelRoute" />
    </div>

    <div v-if="loading" class="create-project-loading">
      <q-spinner size="lg" color="primary" />
    </div>

    <div v-else class="create-project-card">
      <div class="create-project-cover-col">
        <div class="card-title q-mb-sm">Cover Photo</div>
        <div class="text-description q-mb-md">Upload a cover image for your project. Recommended size: 1200×1600px.</div>

        <div
          class="cover-upload-area"
          :class="{ 'cover-upload-area--has-image': coverPreview }"
          @click="triggerFilePicker"
          @dragover.prevent="dragOver = true"
          @dragleave.prevent="dragOver = false"
          @drop.prevent="handleDrop"
        >
          <input
            ref="fileInput"
            type="file"
            accept="image/*"
            style="display: none"
            @change="handleFileChange"
          />

          <template v-if="coverPreview">
            <img :src="coverPreview" class="cover-upload-area__preview" />
            <div class="cover-upload-area__overlay">
              <span class="material-icons">photo_camera</span>
              <span>{{ existingCover ? 'Change cover photo' : 'Upload cover photo' }}</span>
            </div>
          </template>

          <template v-else>
            <div class="cover-upload-area__placeholder">
              <span class="material-icons" style="font-size: 40px">cloud_upload</span>
              <div class="cover-upload-area__text">Click to upload a cover photo</div>
              <div class="text-small">or drag and drop an image here</div>
            </div>
          </template>
        </div>

        <div v-if="coverFile || existingCover" class="row items-center q-mt-sm q-gutter-sm">
          <q-btn flat dense size="sm" icon="close" label="Remove" no-caps @click="removeCover" />
          <span class="text-small">{{ coverFile ? coverFile.name : (existingCover ? 'Current cover image' : '') }}</span>
        </div>
      </div>

      <div class="create-project-form-col">
        <q-input
          v-model="form.title"
          label="Project Title *"
          outlined
          color="primary"
          dense
          :error="!!errors.title"
          :error-message="errors.title"
          autofocus
        />

        <q-input
          v-model="form.genre"
          label="Genre"
          outlined
          color="primary"
          dense
          placeholder="e.g. Fantasy, Mystery, Romance..."
        />

        <q-input
          v-model="form.synopsis"
          label="Synopsis"
          outlined
          color="primary"
          type="textarea"
          dense
          rows="4"
          :maxlength="2000"
          :hint="`${form.synopsis.length} / 2000`"
        />

        <div class="create-project-actions">
          <q-btn
            unelevated
            color="primary"
            :label="isEdit ? 'Update Project' : 'Create Project'"
            no-caps
            :loading="submitting"
            @click="handleSubmit"
          />
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProjectsStore } from '@/stores/projects'

const route = useRoute()
const router = useRouter()
const projectsStore = useProjectsStore()

const projectId = computed(() => route.params.id || null)
const isEdit = computed(() => !!projectId.value)
const cancelRoute = computed(() => isEdit.value ? `/projects/${projectId.value}/write` : '/dashboard')

const fileInput = ref(null)
const coverFile = ref(null)
const coverPreview = ref('')
const existingCover = ref('')
const dragOver = ref(false)
const submitting = ref(false)
const loading = ref(false)
const errors = reactive({ title: '' })

const form = reactive({
  title: '',
  genre: '',
  synopsis: '',
})

onMounted(async () => {
  if (isEdit.value) {
    loading.value = true
    try {
      const project = await projectsStore.fetchProject(projectId.value)
      form.title = project.title || ''
      form.genre = project.genre || ''
      form.synopsis = project.synopsis || ''
      if (project.cover_image) {
        existingCover.value = project.cover_image
        coverPreview.value = project.cover_image
      }
    } catch {
      router.push('/dashboard')
    } finally {
      loading.value = false
    }
  }
})

function triggerFilePicker() {
  fileInput.value?.click()
}

function handleFileChange(e) {
  const file = e.target.files?.[0]
  if (file) setCoverFile(file)
}

function handleDrop(e) {
  dragOver.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) setCoverFile(file)
}

function setCoverFile(file) {
  if (!file.type.startsWith('image/')) return
  coverFile.value = file
  existingCover.value = ''
  const reader = new FileReader()
  reader.onload = (e) => {
    coverPreview.value = e.target.result
  }
  reader.readAsDataURL(file)
}

function removeCover() {
  coverFile.value = null
  coverPreview.value = existingCover.value ? '' : ''
  existingCover.value = ''
  if (fileInput.value) fileInput.value.value = ''
}

async function handleSubmit() {
  errors.title = ''

  if (!form.title.trim()) {
    errors.title = 'Title is required.'
    return
  }

  submitting.value = true

  const fd = new FormData()
  fd.append('title', form.title.trim())
  fd.append('genre', form.genre.trim())
  fd.append('synopsis', form.synopsis.trim())
  fd.append('remove_cover', existingCover.value ? '' : 'true')

  if (coverFile.value) {
    fd.append('cover_image', coverFile.value)
  } else if (existingCover.value && !coverFile.value) {
    fd.delete('remove_cover')
  }

  try {
    if (isEdit.value) {
      await projectsStore.updateProject(projectId.value, fd)
      router.push(`/projects/${projectId.value}/write`)
    } else {
      const project = await projectsStore.createProject(fd)
      router.push(`/projects/${project.id}/write`)
    }
  } catch {
    errors.title = projectsStore.error || 'Failed to save project.'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.create-project-page {
  min-height: 100vh;
  background: var(--wda-bg);
  display: flex;
  flex-direction: column;
  padding: 32px 40px;
}

.create-project-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 24px;
  flex-shrink: 0;
}

.create-project-subtitle {
  font-family: var(--wda-font-ui);
  font-size: 14px;
  color: var(--wda-text-muted);
  margin-bottom: 0;
}

.create-project-loading {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.create-project-card {
  flex: 1;
  display: flex;
  gap: 32px;
  background: var(--wda-surface);
  border: 1px solid var(--wda-border);
  border-radius: var(--wda-radius);
  box-shadow: var(--wda-shadow);
  padding: 32px;
  min-height: 0;
}

.create-project-cover-col {
  width: 220px;
  flex-shrink: 0;
}

.create-project-form-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-width: 0;
}

.create-project-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: auto;
  padding-top: 16px;
}

.cover-upload-area {
  position: relative;
  width: 100%;
  aspect-ratio: 3 / 4;
  border: 2px dashed var(--wda-border-strong);
  border-radius: var(--wda-radius);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  transition: border-color .2s ease, background .2s ease;
  background: var(--wda-surface-2);
}

.cover-upload-area:hover {
  border-color: var(--wda-primary);
  background: var(--wda-surface);
}

.cover-upload-area--has-image {
  border-style: solid;
  border-color: var(--wda-border);
}

.cover-upload-area__placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: var(--wda-text-muted);
  padding: 24px;
  text-align: center;
}

.cover-upload-area__text {
  font-size: 14px;
  font-weight: 500;
  color: var(--wda-text-secondary);
}

.cover-upload-area__preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.cover-upload-area__overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  background: rgba(0, 0, 0, 0.55);
  color: #fff;
  opacity: 0;
  transition: opacity .2s ease;
  font-size: 13px;
}

.cover-upload-area:hover .cover-upload-area__overlay {
  opacity: 1;
}

.body--dark .cover-upload-area {
  background: var(--wda-surface-2);
}

.body--dark .cover-upload-area:hover {
  background: var(--wda-bg);
}

@media (max-width: 600px) {
  .create-project-page {
    padding: 16px;
  }

  .create-project-header {
    flex-direction: column;
    gap: 12px;
  }

  .create-project-header .q-btn {
    align-self: flex-start;
  }

  .create-project-card {
    flex-direction: column;
    gap: 24px;
    padding: 20px;
  }

  .create-project-cover-col {
    width: 100%;
  }

  .cover-upload-area {
    aspect-ratio: 16 / 9;
    max-height: 250px;
  }

  .create-project-actions .q-btn {
    width: 100%;
  }
}
</style>
