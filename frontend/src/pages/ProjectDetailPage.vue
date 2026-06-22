<template>
  <q-layout>
    <q-page-container>
      <q-page class="q-pa-md">
        <div v-if="fetching" class="text-center q-mt-xl">
          <q-spinner size="lg" />
        </div>

        <div v-else-if="notFound" class="text-center q-mt-xl">
          <div class="text-h5 text-negative q-mb-sm">Project not found</div>
          <div class="text-grey q-mb-md">
            This project doesn't exist or you don't have access to it.
          </div>
          <q-btn label="Back to Dashboard" color="primary" to="/dashboard" no-caps />
        </div>

        <div v-else-if="project">
          <q-btn
            flat
            icon="arrow_back"
            label="Back to Dashboard"
            to="/dashboard"
            no-caps
            class="q-mb-md"
          />
          <div class="text-h4">{{ project.title }}</div>
          <div class="text-caption text-grey q-mb-lg">
            Created {{ relativeTime(project.created_at) }}
          </div>

          <div class="row q-col-gutter-md">
            <div class="col-12 col-sm-6 col-md-4">
              <q-card
                flat
                bordered
                class="cursor-pointer"
                @click="goToWrite"
              >
                <q-card-section class="text-center">
                  <q-icon name="edit_note" size="xl" color="primary" />
                  <div class="text-h6 q-mt-sm">Start Writing</div>
                  <div class="text-caption text-grey">Open the manuscript editor</div>
                </q-card-section>
              </q-card>
            </div>

            <div class="col-12 col-sm-6 col-md-4">
              <q-card
                flat
                bordered
                class="cursor-pointer"
                @click="goToStoryBible"
              >
                <q-card-section class="text-center">
                  <q-icon name="menu_book" size="xl" color="primary" />
                  <div class="text-h6 q-mt-sm">Story Bible</div>
                  <div class="text-caption text-grey">Manage characters, places, and timeline</div>
                </q-card-section>
              </q-card>
            </div>
          </div>
        </div>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProjectsStore } from '@/stores/projects'

const route = useRoute()
const router = useRouter()
const store = useProjectsStore()

const project = ref(null)
const fetching = ref(true)
const notFound = ref(false)

function goToStoryBible() {
  router.push(`/projects/${project.value.id}/story-bible`)
}

function goToWrite() {
  router.push(`/projects/${project.value.id}/write`)
}

onMounted(async () => {
  try {
    project.value = await store.fetchProject(route.params.id)
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
