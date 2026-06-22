<template>
  <q-layout>
    <q-page-container>
      <q-page class="q-pa-md" :style="{ '--editor-font-size': fontSize }">
        <q-btn
          v-if="!fullscreen"
          flat
          icon="arrow_back"
          label="Back to Project"
          :to="`/projects/${projectId}`"
          no-caps
          class="q-mb-md"
        />

        <div class="row" style="height: calc(100vh - 120px)">
          <!-- Left Panel: Scene Board -->
          <div v-if="!fullscreen" class="col-4 col-sm-3 q-pr-md" style="display: flex; flex-direction: column">
            <q-btn
              label="New Scene"
              color="primary"
              icon="add"
              no-caps
              class="q-mb-sm"
              @click="handleCreateScene"
            />

            <div
              v-if="scenesStore.loading"
              class="text-center q-mt-lg"
            >
              <q-spinner size="md" />
            </div>

            <div
              v-else-if="scenesStore.scenes.length === 0"
              class="text-center q-mt-lg text-grey"
            >
              No scenes yet. Create one to start writing.
            </div>

            <div
              v-else
              ref="sceneListContainer"
              class="scene-list"
            >
              <div
                v-for="scene in scenesStore.scenes"
                :key="scene.id"
                :data-id="scene.id"
                class="scene-card-wrapper q-mb-sm"
              >
                <q-card
                  flat
                  bordered
                  :class="{ 'selected-scene': scenesStore.activeSceneId === scene.id }"
                  class="cursor-pointer"
                  @click="scenesStore.setActiveScene(scene.id)"
                >
                  <q-card-section class="row items-center no-wrap q-py-sm q-px-sm">
                    <q-icon
                      name="drag_indicator"
                      class="drag-handle cursor-grab q-mr-sm"
                      size="sm"
                      color="grey-5"
                    />
                    <div class="col q-ml-xs" style="min-width: 0">
                      <div class="text-body2 ellipsis">
                        {{ scene.title || 'Untitled Scene' }}
                      </div>
                      <div class="text-caption text-grey">#{{ scene.order + 1 }}</div>
                    </div>
                    <q-btn
                      flat
                      dense
                      round
                      icon="more_vert"
                      size="sm"
                      @click.stop
                    >
                      <q-menu anchor="bottom end" self="top end">
                        <q-list dense style="min-width: 120px">
                          <q-item
                            clickable
                            v-close-popup
                            @click.stop="confirmDeleteScene(scene)"
                          >
                            <q-item-section class="text-negative">Delete</q-item-section>
                          </q-item>
                        </q-list>
                      </q-menu>
                    </q-btn>
                  </q-card-section>
                </q-card>
              </div>
            </div>

            <div v-if="reordering" class="text-primary q-mt-sm">
              <q-spinner size="sm" class="q-mr-xs" />
              Saving order...
            </div>
            <div v-else-if="scenesStore.error && scenesStore.scenes.length > 0" class="text-negative q-mt-sm text-caption">
              {{ scenesStore.error }}
            </div>
          </div>

          <!-- Right Panel: Editor -->
          <div :class="fullscreen ? 'col-12' : 'col-8 col-sm-9'" style="display: flex; flex-direction: column">
            <template v-if="!activeScene">
              <div class="text-center text-grey q-mt-xl">
                <q-icon name="edit_note" size="64px" color="grey-4" />
                <div class="text-h6 q-mt-md">Select a scene to start writing</div>
                <div class="text-body1">or create a new one.</div>
              </div>
            </template>

            <template v-else>
              <div class="row items-center q-mb-sm">
                <q-input
                  v-model="titleDraft"
                  label="Scene title"
                  dense
                  outlined
                  class="col"
                  @blur="saveTitle"
                  @keyup.enter="saveTitle"
                />
                <div class="q-ml-sm text-caption" style="min-width: 80px; text-align: right">
                  <q-spinner
                    v-if="scenesStore.saveStatus === 'saving'"
                    size="sm"
                    class="q-mr-xs"
                  />
                  <span
                    :class="{
                      'text-primary': scenesStore.saveStatus === 'saving',
                      'text-positive': scenesStore.saveStatus === 'saved',
                      'text-negative': scenesStore.saveStatus === 'error',
                      'text-grey': scenesStore.saveStatus === 'idle',
                    }"
                  >
                    <template v-if="scenesStore.saveStatus === 'saving'">Saving...</template>
                    <template v-else-if="scenesStore.saveStatus === 'saved'">Saved</template>
                    <template v-else-if="scenesStore.saveStatus === 'error'">Error saving</template>
                    <template v-else>Ready</template>
                  </span>
                  <q-btn
                    flat
                    dense
                    round
                    icon="history"
                    size="sm"
                    class="q-ml-xs"
                    @click="openHistoryDrawer"
                  />
                  <q-btn
                    flat
                    dense
                    round
                    icon="auto_awesome"
                    size="sm"
                    class="q-ml-xs"
                    @click="openAiDrawer"
                  />
                  <q-btn
                    flat
                    dense
                    round
                    icon="download"
                    size="sm"
                    class="q-ml-xs"
                    @click="showExportDialog = true"
                  />
                  <q-btn
                    flat
                    dense
                    round
                    :icon="fullscreen ? 'fullscreen_exit' : 'fullscreen'"
                    size="sm"
                    class="q-ml-xs"
                    @click="toggleFullscreen"
                  />
                </div>
              </div>

              <!-- Toolbar: formatting + font size -->
              <div v-if="fullscreen" class="row items-center q-mb-sm q-gutter-xs">
                <q-btn flat dense icon="format_bold" size="sm" @click="wrapBold" title="Bold (Ctrl+B)">
                  <q-tooltip>Bold</q-tooltip>
                </q-btn>
                <q-btn flat dense icon="format_italic" size="sm" @click="wrapItalic" title="Italic (Ctrl+I)">
                  <q-tooltip>Italic</q-tooltip>
                </q-btn>
                <q-separator vertical class="q-mx-xs" />
                <q-btn-toggle
                  v-model="fontSize"
                  flat
                  dense
                  no-caps
                  size="sm"
                  :options="[
                    { label: 'S', value: '0.9rem', tooltip: 'Small' },
                    { label: 'M', value: '1.1rem', tooltip: 'Normal' },
                    { label: 'L', value: '1.3rem', tooltip: 'Large' },
                    { label: 'XL', value: '1.5rem', tooltip: 'Extra Large' },
                  ]"
                />
              </div>

              <q-input
                v-model="contentDraft"
                type="textarea"
                ref="editorRef"
                placeholder="Start writing..."
                :class="['q-mb-sm editor-textarea', fullscreen ? 'fullscreen-textarea' : 'col']"
                outlined
                hide-bottom-space
                @update:model-value="onContentChange"
              />

              <div v-if="!fullscreen" class="row q-gutter-md q-mt-sm items-start">
                <q-select
                  v-model="selectedCharacters"
                  :options="characterOptions"
                  label="Characters"
                  multiple
                  use-chips
                  dense
                  outlined
                  clearable
                  class="col"
                  @update:model-value="saveTags"
                >
                  <template v-if="characterOptions.length === 0" #append>
                    <q-icon name="info" size="sm" color="grey" />
                  </template>
                </q-select>

                <q-select
                  v-model="selectedPlaces"
                  :options="placeOptions"
                  label="Places"
                  multiple
                  use-chips
                  dense
                  outlined
                  clearable
                  class="col"
                  @update:model-value="saveTags"
                >
                  <template v-if="placeOptions.length === 0" #append>
                    <q-icon name="info" size="sm" color="grey" />
                  </template>
                </q-select>

                <q-select
                  v-model="selectedTimelineEvents"
                  :options="timelineEventOptions"
                  label="Timeline Events"
                  multiple
                  use-chips
                  dense
                  outlined
                  clearable
                  class="col"
                  @update:model-value="saveTags"
                >
                  <template v-if="timelineEventOptions.length === 0" #append>
                    <q-icon name="info" size="sm" color="grey" />
                  </template>
                </q-select>
              </div>

              <div
                v-if="!fullscreen && characterOptions.length === 0 && placeOptions.length === 0 && timelineEventOptions.length === 0"
                class="text-caption text-grey q-mt-xs"
              >
                No characters, places, or timeline events yet.
                <router-link :to="`/projects/${projectId}/story-bible`">
                  Add some to your Story Bible
                </router-link>
                to tag them to scenes.
              </div>
            </template>
          </div>
        </div>

        <!-- Delete Confirmation Dialog -->
        <q-dialog v-model="showDeleteDialog">
          <q-card style="min-width: 350px">
            <q-card-section>
              <div class="text-h6">Delete Scene</div>
            </q-card-section>
            <q-card-section>
              <p>
                Are you sure you want to delete '<strong>{{ deleteTarget?.title || 'Untitled Scene' }}</strong
                >'? This cannot be undone.
              </p>
              <div v-if="deleteError" class="text-negative">{{ deleteError }}</div>
            </q-card-section>
            <q-card-actions align="right">
              <q-btn flat label="Cancel" v-close-popup no-caps />
              <q-btn
                color="negative"
                label="Delete"
                :loading="deleting"
                no-caps
                @click="submitDelete"
              />
            </q-card-actions>
          </q-card>
        </q-dialog>

        <!-- Restore Confirmation Dialog -->
        <q-dialog v-model="showRestoreDialog">
          <q-card style="min-width: 400px">
            <q-card-section>
              <div class="text-h6">Restore Version</div>
            </q-card-section>
            <q-card-section>
              <div class="text-body2 q-mb-md" v-if="restoreVersionTarget">
                <strong>Version from {{ relativeTime(restoreVersionTarget.created_at) }}</strong>
              </div>
              <div class="text-caption q-mb-md" v-if="restoreVersionTarget">
                &ldquo;{{ restoreVersionTarget.content.substring(0, 100) }}{{ restoreVersionTarget.content.length > 100 ? '...' : '' }}&rdquo;
              </div>
              <div class="text-negative text-body2 q-mb-md">
                Restoring this version will replace your current scene content. A snapshot of your current content will be saved automatically before the restore.
              </div>
              <q-input
                v-model="restorePassword"
                type="password"
                label="Enter your password to confirm"
                outlined
                dense
                :error="!!sceneVersionsStore.restoreError"
                :error-message="sceneVersionsStore.restoreError || ''"
              />
            </q-card-section>
            <q-card-actions align="right">
              <q-btn flat label="Cancel" no-caps @click="closeRestoreDialog" />
              <q-btn
                color="primary"
                label="Restore"
                :disable="!restorePassword"
                :loading="sceneVersionsStore.restoring"
                no-caps
                @click="handleRestore"
              />
            </q-card-actions>
          </q-card>
        </q-dialog>
      <ExportDialog
        v-model="showExportDialog"
        :project-id="projectId"
        :project-title="activeScene?.title || projectId"
        :scenes="scenesStore.scenes"
      />
      </q-page>
    </q-page-container>

    <!-- Version History Drawer -->
    <q-drawer
      v-model="showHistoryDrawer"
      side="right"
      behavior="mobile"
      bordered
      :width="380"
    >
      <div class="q-pa-md" style="height: 100%; display: flex; flex-direction: column">
        <div class="text-h6 q-mb-md ellipsis">
          Version History &mdash; {{ activeScene?.title || 'Untitled Scene' }}
        </div>

        <div v-if="sceneVersionsStore.loading && sceneVersionsStore.versions.length === 0" class="text-center q-mt-lg">
          <q-spinner size="md" />
        </div>

        <div v-else-if="sceneVersionsStore.versions.length === 0" class="text-center q-mt-lg text-grey">
          No versions yet.
        </div>

        <div v-else class="scroll" style="flex: 1; overflow-y: auto">
          <div v-for="version in sceneVersionsStore.versions" :key="version.id" class="q-mb-sm">
            <q-card flat bordered>
              <q-card-section class="q-py-sm q-px-md">
                <div class="row items-center justify-between no-wrap">
                  <div class="text-caption text-grey">{{ relativeTime(version.created_at) }}</div>
                  <q-btn
                    flat
                    dense
                    color="primary"
                    label="Restore"
                    size="sm"
                    no-caps
                    @click="confirmRestore(version)"
                  />
                </div>
                <div class="text-body2 q-mt-xs ellipsis-2-lines">
                  {{ version.content.substring(0, 100) }}{{ version.content.length > 100 ? '...' : '' }}
                </div>
              </q-card-section>
            </q-card>
          </div>

          <div v-if="sceneVersionsStore.hasMore" class="text-center q-mt-sm">
            <q-btn
              flat
              color="primary"
              label="Load more"
              no-caps
              :loading="sceneVersionsStore.loading"
              @click="sceneVersionsStore.loadMoreVersions(projectId, activeScene.id)"
            />
          </div>
        </div>
      </div>
    </q-drawer>

    <!-- AI Assistant Drawer -->
    <q-drawer
      v-model="showAiDrawer"
      side="right"
      behavior="mobile"
      bordered
      :width="400"
    >
      <div class="q-pa-md" style="height: 100%; display: flex; flex-direction: column">
        <div class="row items-center justify-between q-mb-md">
          <div class="text-h6 ellipsis">AI Assistant &mdash; {{ activeScene?.title || 'Untitled Scene' }}</div>
          <q-btn flat dense round icon="close" size="sm" @click="closeAiDrawer" />
        </div>

        <!-- Free-tier warning -->
        <q-banner
          v-if="showFreeTierWarning"
          class="bg-warning text-warning q-mb-sm rounded-borders"
        >
          <template #avatar>
            <q-icon name="warning" color="warning" />
          </template>
          This AI assistant is running on a free-tier key. Your prompts may be used by Google to improve their models.
          <template #action>
            <q-btn flat color="warning" label="Go to Settings" no-caps to="/settings" @click="closeAiDrawer" />
            <q-btn flat color="warning" label="I understand" no-caps @click="dismissFreeTierWarning" />
          </template>
        </q-banner>

        <!-- Empty tagging note -->
        <q-banner
          v-if="activeScene && !hasStoryBibleTags"
          class="bg-info text-info q-mb-sm rounded-borders"
        >
          <template #avatar>
            <q-icon name="lightbulb" color="info" />
          </template>
          Tag characters, places, and timeline events to this scene for more grounded AI feedback.
          <template #action>
            <q-btn flat color="info" label="Story Bible" no-caps :to="`/projects/${projectId}/story-bible`" @click="closeAiDrawer" />
          </template>
        </q-banner>

        <!-- No key configured state -->
        <template v-if="showNoKeyState">
          <div class="text-center q-mt-lg text-negative">
            <q-icon name="error_outline" size="48px" />
            <div class="text-body1 q-mt-sm">{{ conversationsStore.error }}</div>
            <q-btn flat color="primary" label="Go to Settings" no-caps to="/settings" class="q-mt-sm" @click="closeAiDrawer" />
          </div>
        </template>

        <!-- General error banner (quota, etc.) -->
        <q-banner
          v-else-if="conversationsStore.error && !showNoKeyState"
          class="bg-negative text-white q-mb-sm rounded-borders"
        >
          <template #avatar>
            <q-icon name="error_outline" color="white" />
          </template>
          {{ conversationsStore.error }}
        </q-banner>

        <!-- Message list -->
        <template v-else>
          <div
            ref="messageListRef"
            class="scroll q-mb-sm"
            style="flex: 1; overflow-y: auto"
          >
            <div
              v-for="msg in conversationsStore.messages"
              :key="msg.id"
              class="q-mb-sm"
              :class="msg.role === 'user' ? 'flex justify-end' : ''"
            >
              <q-card
                flat
                bordered
                :class="msg.role === 'user' ? 'bg-primary text-white' : ''"
                style="max-width: 85%; display: inline-block"
              >
                <q-card-section class="q-py-sm q-px-md">
                  <div class="text-body2" style="white-space: pre-wrap">{{ msg.content }}</div>
                  <div class="text-caption q-mt-xs" :class="msg.role === 'user' ? 'text-white text-opacity-70' : 'text-grey'">
                    {{ relativeTime(msg.created_at) }}
                  </div>
                </q-card-section>
              </q-card>
            </div>

            <!-- Loading indicator -->
            <div v-if="conversationsStore.sending" class="flex justify-start q-mb-sm">
              <q-card flat bordered style="max-width: 85%; display: inline-block">
                <q-card-section class="q-py-sm q-px-md">
                  <q-spinner-dots size="sm" />
                  <span class="text-grey q-ml-sm">Thinking...</span>
                </q-card-section>
              </q-card>
            </div>
          </div>

          <!-- Message input -->
          <div class="row items-end q-gutter-sm">
            <q-input
              v-model="messageDraft"
              type="textarea"
              autogrow
              placeholder="Ask the AI assistant..."
              outlined
              dense
              class="col"
              :disable="conversationsStore.sending"
              @keydown.enter.exact="handleSendMessage"
              @keydown.shift.enter.prevent
            />
            <q-btn
              round
              dense
              color="primary"
              icon="send"
              :disable="!messageDraft.trim() || conversationsStore.sending"
              @click="handleSendMessage"
            />
          </div>
        </template>
      </div>
    </q-drawer>
  </q-layout>
</template>

<script setup>
import { ref, computed, onMounted, watch, onBeforeUnmount, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useScenesStore } from '@/stores/scenes'
import { useSceneVersionsStore } from '@/stores/sceneVersions'
import { useConversationsStore } from '@/stores/conversations'
import ExportDialog from '@/components/ExportDialog.vue'
import { useCharactersStore } from '@/stores/characters'
import { usePlacesStore } from '@/stores/places'
import { useTimelineEventsStore } from '@/stores/timelineEvents'
import Sortable from 'sortablejs'

const route = useRoute()
const projectId = route.params.id

const scenesStore = useScenesStore()
const sceneVersionsStore = useSceneVersionsStore()
const conversationsStore = useConversationsStore()
const charactersStore = useCharactersStore()
const placesStore = usePlacesStore()
const timelineEventsStore = useTimelineEventsStore()

// ---- Fullscreen, font size, markdown formatting ----
const fullscreen = ref(false)
const fontSize = ref(localStorage.getItem('wda_font_size') || '1.1rem')
const editorRef = ref(null)

watch(fontSize, (val) => {
  localStorage.setItem('wda_font_size', val)
})

function toggleFullscreen() {
  fullscreen.value = !fullscreen.value
}

function onKeydown(e) {
  if (e.key === 'Escape' && fullscreen.value) {
    fullscreen.value = false
  }
  if (e.key === 'b' && (e.ctrlKey || e.metaKey) && fullscreen.value) {
    e.preventDefault()
    wrapBold()
  }
  if (e.key === 'i' && (e.ctrlKey || e.metaKey) && fullscreen.value) {
    e.preventDefault()
    wrapItalic()
  }
}

function getTextarea() {
  const ta = document.querySelector('.editor-textarea textarea, .fullscreen-textarea textarea')
  return ta
}

function wrapBold() {
  const ta = getTextarea()
  if (!ta) return
  const start = ta.selectionStart
  const end = ta.selectionEnd
  const val = contentDraft.value
  if (start === end) {
    const wrapped = val.substring(0, start) + '****' + val.substring(end)
    contentDraft.value = wrapped
    onContentChange()
    nextTick(() => {
      ta.focus()
      ta.setSelectionRange(start + 2, start + 2, 'none')
    })
    return
  }
  const selected = val.substring(start, end)
  const wrapped = val.substring(0, start) + '**' + selected + '**' + val.substring(end)
  contentDraft.value = wrapped
  onContentChange()
  nextTick(() => {
    ta.focus()
    ta.setSelectionRange(end + 4, end + 4, 'none')
  })
}

function wrapItalic() {
  const ta = getTextarea()
  if (!ta) return
  const start = ta.selectionStart
  const end = ta.selectionEnd
  const val = contentDraft.value
  if (start === end) {
    const wrapped = val.substring(0, start) + '**' + val.substring(end)
    contentDraft.value = wrapped
    onContentChange()
    nextTick(() => {
      ta.focus()
      ta.setSelectionRange(start + 1, start + 1, 'none')
    })
    return
  }
  const selected = val.substring(start, end)
  const wrapped = val.substring(0, start) + '*' + selected + '*' + val.substring(end)
  contentDraft.value = wrapped
  onContentChange()
  nextTick(() => {
    ta.focus()
    ta.setSelectionRange(end + 2, end + 2, 'none')
  })
}



const activeScene = computed(() => {
  if (scenesStore.activeSceneId === null) return null
  return scenesStore.scenes.find((s) => s.id === scenesStore.activeSceneId) || null
})

const hasStoryBibleTags = computed(() => {
  if (!activeScene.value) return false
  const s = activeScene.value
  return (s.characters && s.characters.length > 0) ||
    (s.places && s.places.length > 0) ||
    (s.timeline_events && s.timeline_events.length > 0)
})

const showNoKeyState = computed(() => {
  return (
    conversationsStore.error &&
    !conversationsStore.sending &&
    conversationsStore.messages.length === 0 &&
    conversationsStore.error.includes('not configured')
  )
})

// ---- Data fetching ----
onMounted(async () => {
  await Promise.all([
    scenesStore.fetchScenes(projectId),
    charactersStore.fetchCharacters(projectId),
    placesStore.fetchPlaces(projectId),
    timelineEventsStore.fetchTimelineEvents(projectId),
  ])
  document.addEventListener('keydown', onKeydown)
})

// ---- Scene list drag reorder (SortableJS) ----
const sceneListContainer = ref(null)
const reordering = ref(false)
let sortableInstance = null

function initSortable() {
  if (!sceneListContainer.value) return
  destroySortable()
  sortableInstance = new Sortable(sceneListContainer.value, {
    animation: 200,
    handle: '.drag-handle',
    dataIdAttr: 'data-id',
    onEnd: async () => {
      reordering.value = true
      const orderedIds = sortableInstance.toArray().map(Number)
      try {
        await scenesStore.reorderScenes(projectId, orderedIds)
      } catch {
        // Store already refetched
      } finally {
        reordering.value = false
        nextTick(() => initSortable())
      }
    },
  })
}

function destroySortable() {
  if (sortableInstance) {
    sortableInstance.destroy()
    sortableInstance = null
  }
}

watch(
  () => scenesStore.scenes.length,
  (len) => {
    if (len > 0) {
      nextTick(() => initSortable())
    } else {
      destroySortable()
    }
  },
)

onBeforeUnmount(destroySortable)
onBeforeUnmount(() => {
  document.removeEventListener('keydown', onKeydown)
})

// ---- Create scene ----
async function handleCreateScene() {
  try {
    const scene = await scenesStore.createScene(projectId, { title: '' })
    scenesStore.setActiveScene(scene.id)
  } catch {
    // error is on store
  }
}

// ---- Delete scene ----
const showDeleteDialog = ref(false)
const deleteTarget = ref(null)
const deleteError = ref('')
const deleting = ref(false)

function confirmDeleteScene(scene) {
  deleteTarget.value = scene
  deleteError.value = ''
  deleting.value = false
  showDeleteDialog.value = true
}

async function submitDelete() {
  deleteError.value = ''
  deleting.value = true
  try {
    await scenesStore.deleteScene(projectId, deleteTarget.value.id)
    showDeleteDialog.value = false
  } catch {
    deleteError.value = scenesStore.error || 'Failed to delete scene.'
  } finally {
    deleting.value = false
  }
}

// ---- Title editing ----
const titleDraft = ref('')

watch(activeScene, (scene) => {
  if (scene) {
    titleDraft.value = scene.title
  } else {
    titleDraft.value = ''
  }
}, { immediate: true })

function saveTitle() {
  if (!activeScene.value) return
  const newTitle = titleDraft.value.trim()
  if (newTitle !== activeScene.value.title) {
    scenesStore.updateSceneMeta(projectId, activeScene.value.id, { title: newTitle })
  }
}

// ---- Content editing with debounced autosave ----
const contentDraft = ref('')
let saveTimer = null

watch(activeScene, (scene) => {
  if (scene) {
    contentDraft.value = scene.content
  } else {
    contentDraft.value = ''
  }
}, { immediate: true })

function onContentChange() {
  if (saveTimer) clearTimeout(saveTimer)
  saveTimer = setTimeout(() => {
    if (activeScene.value && contentDraft.value !== activeScene.value.content) {
      scenesStore.updateSceneContent(projectId, activeScene.value.id, contentDraft.value)
    }
  }, 2500)
}

onBeforeUnmount(() => {
  if (saveTimer) clearTimeout(saveTimer)
})

// ---- Character/Place/TimelineEvent tagging ----
const selectedCharacters = ref([])
const selectedPlaces = ref([])
const selectedTimelineEvents = ref([])

const characterOptions = computed(() => {
  return charactersStore.characters.map((c) => ({
    label: c.name,
    value: c.id,
  }))
})

const placeOptions = computed(() => {
  return placesStore.places.map((p) => ({
    label: p.name,
    value: p.id,
  }))
})

const timelineEventOptions = computed(() => {
  return timelineEventsStore.timelineEvents.map((e) => ({
    label: e.title,
    value: e.id,
  }))
})

watch(activeScene, (scene) => {
  if (scene) {
    selectedCharacters.value = (scene.characters || []).map((id) => {
      const c = charactersStore.characters.find((ch) => ch.id === id)
      return c ? { label: c.name, value: c.id } : { label: `#${id}`, value: id }
    })
    selectedPlaces.value = (scene.places || []).map((id) => {
      const p = placesStore.places.find((pl) => pl.id === id)
      return p ? { label: p.name, value: p.id } : { label: `#${id}`, value: id }
    })
    selectedTimelineEvents.value = (scene.timeline_events || []).map((id) => {
      const e = timelineEventsStore.timelineEvents.find((ev) => ev.id === id)
      return e ? { label: e.title, value: e.id } : { label: `#${id}`, value: id }
    })
  } else {
    selectedCharacters.value = []
    selectedPlaces.value = []
    selectedTimelineEvents.value = []
  }
}, { immediate: true })

function saveTags() {
  if (!activeScene.value) return
  scenesStore.updateSceneMeta(projectId, activeScene.value.id, {
    characters: selectedCharacters.value.map((o) => o.value),
    places: selectedPlaces.value.map((o) => o.value),
    timeline_events: selectedTimelineEvents.value.map((o) => o.value),
  })
}

// ---- Version History ----
const showHistoryDrawer = ref(false)
const showRestoreDialog = ref(false)
const restoreVersionTarget = ref(null)
const restorePassword = ref('')

function openHistoryDrawer() {
  showAiDrawer.value = false
  showHistoryDrawer.value = true
  if (activeScene.value) {
    sceneVersionsStore.fetchVersions(projectId, activeScene.value.id)
  }
}

function confirmRestore(version) {
  restoreVersionTarget.value = version
  restorePassword.value = ''
  sceneVersionsStore.clearRestoreError()
  showRestoreDialog.value = true
}

function closeRestoreDialog() {
  showRestoreDialog.value = false
  sceneVersionsStore.clearRestoreError()
}

async function handleRestore() {
  if (!restoreVersionTarget.value || !activeScene.value) return
  await sceneVersionsStore.restoreVersion(
    projectId,
    activeScene.value.id,
    restoreVersionTarget.value.id,
    restorePassword.value,
  )
  if (!sceneVersionsStore.restoreError) {
    showRestoreDialog.value = false
    showHistoryDrawer.value = false
  }
}

// ---- AI Assistant ----
const showAiDrawer = ref(false)
const messageDraft = ref('')
const messageListRef = ref(null)
const showFreeTierWarning = ref(false)
const showExportDialog = ref(false)

function openAiDrawer() {
  showHistoryDrawer.value = false
  showAiDrawer.value = true
  if (activeScene.value) {
    initAiConversation(activeScene.value)
  }
}

function closeAiDrawer() {
  showAiDrawer.value = false
}

function dismissFreeTierWarning() {
  showFreeTierWarning.value = false
  try {
    sessionStorage.setItem('wda_free_tier_warned', '1')
  } catch {
    // sessionStorage may not be available
  }
}

async function initAiConversation(scene) {
  await conversationsStore.fetchOrCreateConversation(projectId, scene.id)
  await conversationsStore.fetchMessages(projectId)
  await nextTick()
  scrollToBottom()
}

async function handleSendMessage() {
  const text = messageDraft.value.trim()
  if (!text || conversationsStore.sending) return
  messageDraft.value = ''
  await conversationsStore.sendMessage(projectId, text)
  if (!conversationsStore.error) {
    await nextTick()
    scrollToBottom()
    if (conversationsStore.isFreeTier && !sessionStorage.getItem('wda_free_tier_warned')) {
      showFreeTierWarning.value = true
    }
  }
}

function scrollToBottom() {
  if (messageListRef.value) {
    messageListRef.value.scrollTop = messageListRef.value.scrollHeight
  }
}

// Watch for scene changes to reinitialize AI conversation
watch(activeScene, (scene, oldScene) => {
  if (scene && showAiDrawer.value && scene.id !== oldScene?.id) {
    conversationsStore.reset()
    initAiConversation(scene)
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

<style scoped>
.scene-list {
  overflow-y: auto;
  flex: 1;
}

.scene-list :deep(.sortable-ghost) {
  opacity: 0.4;
}

.selected-scene {
  border-color: var(--q-primary);
  border-width: 2px;
}

.editor-textarea :deep(textarea) {
  min-height: 300px;
  font-size: var(--editor-font-size, 1.1rem);
  line-height: 1.7;
  font-family: 'Georgia', serif;
  resize: vertical;
}

.fullscreen-textarea :deep(textarea) {
  min-height: calc(100vh - 280px);
  font-size: var(--editor-font-size, 1.1rem);
  line-height: 1.7;
  font-family: 'Georgia', serif;
  resize: vertical;
}
</style>
