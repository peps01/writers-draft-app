<template>
  <q-dialog v-model="show" persistent>
    <q-card style="min-width: 450px; max-width: 550px">
      <q-card-section class="row items-center justify-between">
        <div class="text-h6">Export to EPUB</div>
        <q-btn flat dense round icon="close" v-close-popup />
      </q-card-section>

      <q-card-section class="q-pt-none">
        <div class="text-body2 text-grey q-mb-sm">
          Book: <strong>{{ projectTitle }}</strong>
        </div>
        <div class="text-caption text-grey q-mb-md">
          Select the scenes to include in the ebook.
        </div>

        <div v-if="loading" class="text-center q-my-md">
          <q-spinner size="sm" />
        </div>

        <template v-else>
          <div class="row items-center q-mb-sm q-gutter-xs">
            <q-btn flat dense size="sm" label="Select All" no-caps @click="selectAll" />
            <q-btn flat dense size="sm" label="Deselect All" no-caps @click="deselectAll" />
            <q-space />
            <span class="text-caption text-grey">{{ selectedCount }} / {{ scenes.length }} selected</span>
          </div>

          <q-list bordered separator dense style="max-height: 300px; overflow-y: auto">
            <q-item
              v-for="scene in scenes"
              :key="scene.id"
              tag="label"
              v-ripple
              clickable
            >
              <q-item-section side>
                <q-checkbox v-model="selectedIds" :val="scene.id" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{ scene.title || 'Untitled Scene' }}</q-item-label>
                <q-item-label caption>Scene {{ scene.order + 1 }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>

          <div v-if="error" class="text-negative text-caption q-mt-sm">{{ error }}</div>
        </template>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Cancel" v-close-popup no-caps />
        <q-btn
          color="primary"
          label="Export"
          :loading="exporting"
          :disable="selectedIds.length === 0 || loading"
          no-caps
          @click="handleExport"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { api } from '@/boot/axios'

const props = defineProps({
  modelValue: Boolean,
  projectId: { type: String, required: true },
  projectTitle: { type: String, default: '' },
  scenes: { type: Array, default: () => [] },
})

const emit = defineEmits(['update:modelValue'])

const show = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

const selectedIds = ref([])
const exporting = ref(false)
const error = ref('')
const loading = ref(false)

const selectedCount = computed(() => selectedIds.value.length)

watch(show, (val) => {
  if (val) {
    selectedIds.value = props.scenes.map((s) => s.id)
    error.value = ''
  }
})

function selectAll() {
  selectedIds.value = props.scenes.map((s) => s.id)
}

function deselectAll() {
  selectedIds.value = []
}

async function handleExport() {
  if (selectedIds.value.length === 0) return
  exporting.value = true
  error.value = ''
  try {
    const { data } = await api.post(
      `/projects/${props.projectId}/export/epub/`,
      { scene_ids: selectedIds.value },
      { responseType: 'blob' },
    )
    const url = window.URL.createObjectURL(new Blob([data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `${props.projectTitle || 'export'}.epub`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    show.value = false
  } catch (err) {
    error.value = err.response?.data?.error || 'Export failed. Try again.'
  } finally {
    exporting.value = false
  }
}
</script>
