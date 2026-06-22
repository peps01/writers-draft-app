<template>
  <q-layout>
    <q-page-container>
      <q-page class="q-pa-md">
        <q-btn
          flat
          icon="arrow_back"
          label="Back to Project"
          :to="`/projects/${projectId}`"
          no-caps
          class="q-mb-md"
        />

        <q-tabs v-model="tab" class="q-mb-md">
          <q-tab name="characters" label="Characters" icon="people" />
          <q-tab name="places" label="Places" icon="place" />
          <q-tab name="timeline" label="Timeline" icon="timeline" />
        </q-tabs>

        <q-tab-panels v-model="tab" animated>
          <!-- Characters -->
          <q-tab-panel name="characters">
            <div class="row items-center justify-between q-mb-md">
              <div class="text-h6">Characters</div>
              <q-btn
                label="Add Character"
                color="primary"
                icon="add"
                @click="openCreateEntity('characters')"
                no-caps
              />
            </div>

            <div v-if="charactersStore.loading" class="row q-col-gutter-md">
              <div v-for="n in 6" :key="n" class="col-12 col-sm-6 col-md-4">
                <q-card flat bordered>
                  <q-card-section>
                    <q-skeleton type="text" class="text-h6" />
                    <q-skeleton type="text" width="60%" />
                    <q-skeleton type="text" width="40%" />
                  </q-card-section>
                </q-card>
              </div>
            </div>

            <div
              v-else-if="charactersStore.error && charactersStore.characters.length === 0"
              class="text-center q-mt-xl"
            >
              <div class="text-negative q-mb-md">{{ charactersStore.error }}</div>
              <q-btn
                label="Retry"
                color="primary"
                @click="charactersStore.fetchCharacters(projectId)"
                no-caps
              />
            </div>

            <div v-else-if="charactersStore.characters.length === 0" class="text-center q-mt-xl">
              <div class="text-h6 q-mb-sm">No characters yet</div>
              <div class="text-grey q-mb-md">
                Create your first character to populate your story bible.
              </div>
              <q-btn
                label="Add Character"
                color="primary"
                icon="add"
                @click="openCreateEntity('characters')"
                no-caps
              />
            </div>

            <div v-else class="row q-col-gutter-md">
              <div
                v-for="char in charactersStore.characters"
                :key="char.id"
                class="col-12 col-sm-6 col-md-4"
              >
                <EntityCard
                  :entity="char"
                  @edit="openEditEntity('characters', char)"
                  @delete="openDelete('characters', char)"
                />
              </div>
            </div>
          </q-tab-panel>

          <!-- Places -->
          <q-tab-panel name="places">
            <div class="row items-center justify-between q-mb-md">
              <div class="text-h6">Places</div>
              <q-btn
                label="Add Place"
                color="primary"
                icon="add"
                @click="openCreateEntity('places')"
                no-caps
              />
            </div>

            <div v-if="placesStore.loading" class="row q-col-gutter-md">
              <div v-for="n in 6" :key="n" class="col-12 col-sm-6 col-md-4">
                <q-card flat bordered>
                  <q-card-section>
                    <q-skeleton type="text" class="text-h6" />
                    <q-skeleton type="text" width="60%" />
                    <q-skeleton type="text" width="40%" />
                  </q-card-section>
                </q-card>
              </div>
            </div>

            <div
              v-else-if="placesStore.error && placesStore.places.length === 0"
              class="text-center q-mt-xl"
            >
              <div class="text-negative q-mb-md">{{ placesStore.error }}</div>
              <q-btn
                label="Retry"
                color="primary"
                @click="placesStore.fetchPlaces(projectId)"
                no-caps
              />
            </div>

            <div v-else-if="placesStore.places.length === 0" class="text-center q-mt-xl">
              <div class="text-h6 q-mb-sm">No places yet</div>
              <div class="text-grey q-mb-md">
                Create your first place to populate your story bible.
              </div>
              <q-btn
                label="Add Place"
                color="primary"
                icon="add"
                @click="openCreateEntity('places')"
                no-caps
              />
            </div>

            <div v-else class="row q-col-gutter-md">
              <div
                v-for="place in placesStore.places"
                :key="place.id"
                class="col-12 col-sm-6 col-md-4"
              >
                <EntityCard
                  :entity="place"
                  @edit="openEditEntity('places', place)"
                  @delete="openDelete('places', place)"
                />
              </div>
            </div>
          </q-tab-panel>

          <!-- Timeline -->
          <q-tab-panel name="timeline">
            <div class="row items-center justify-between q-mb-md">
              <div class="text-h6">Timeline Events</div>
              <q-btn
                label="Add Event"
                color="primary"
                icon="add"
                @click="openCreateTimelineEvent"
                no-caps
              />
            </div>

            <div v-if="timelineEventsStore.loading" class="text-center q-mt-xl">
              <q-spinner size="lg" />
            </div>

            <div
              v-else-if="
                timelineEventsStore.error && timelineEventsStore.timelineEvents.length === 0
              "
              class="text-center q-mt-xl"
            >
              <div class="text-negative q-mb-md">{{ timelineEventsStore.error }}</div>
              <q-btn
                label="Retry"
                color="primary"
                @click="timelineEventsStore.fetchTimelineEvents(projectId)"
                no-caps
              />
            </div>

            <div
              v-else-if="timelineEventsStore.timelineEvents.length === 0"
              class="text-center q-mt-xl"
            >
              <div class="text-h6 q-mb-sm">No timeline events yet</div>
              <div class="text-grey q-mb-md">
                Create your first event to build your story's timeline.
              </div>
              <q-btn
                label="Add Event"
                color="primary"
                icon="add"
                @click="openCreateTimelineEvent"
                no-caps
              />
            </div>

            <div v-else ref="timelineContainer" class="timeline-list">
              <div v-if="reordering" class="text-primary q-mb-sm">
                <q-spinner size="sm" class="q-mr-xs" />
                Saving order...
              </div>
              <div v-else-if="timelineEventsStore.error" class="text-negative q-mb-sm">
                {{ timelineEventsStore.error }}
              </div>

              <div
                v-for="event in timelineEventsStore.timelineEvents"
                :key="event.id"
                :data-id="event.id"
                class="timeline-item q-mb-sm"
              >
                <q-card flat bordered>
                  <q-card-section class="row items-center no-wrap q-py-sm">
                    <q-icon
                      name="drag_indicator"
                      class="drag-handle cursor-grab q-mr-md"
                      size="md"
                      color="grey-5"
                    />
                    <div class="col">
                      <div class="text-subtitle1">{{ event.title }}</div>
                      <div
                        v-if="event.description"
                        class="text-body2 text-grey description-preview"
                      >
                        {{ event.description }}
                      </div>
                    </div>
                    <q-btn flat dense round icon="more_vert" size="sm" @click.stop>
                      <q-menu anchor="bottom end" self="top end">
                        <q-list dense style="min-width: 120px">
                          <q-item
                            clickable
                            v-close-popup
                            @click.stop="openEditTimelineEvent(event)"
                          >
                            <q-item-section>Edit</q-item-section>
                          </q-item>
                          <q-item
                            clickable
                            v-close-popup
                            @click.stop="openDelete('timeline', event)"
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
          </q-tab-panel>
        </q-tab-panels>

        <!-- Entity Form Dialog (Characters / Places) -->
        <EntityFormDialog
          v-model="showEntityDialog"
          :entity="editingEntity"
          :entity-label="activeEntityLabel"
          name-label="Name"
          :saving="entitySaving"
          :error-text="entityError"
          @save="onEntitySave"
        />

        <!-- Timeline Event Form Dialog -->
        <q-dialog v-model="showTimelineDialog" @before-hide="resetTimelineForm">
          <q-card style="min-width: 400px">
            <q-card-section>
              <div class="text-h6">{{ editingTimelineEvent ? 'Edit' : 'Add' }} Timeline Event</div>
            </q-card-section>
            <q-card-section>
              <q-input
                v-model="timelineForm.title"
                label="Title"
                autofocus
                :error="!!timelineTitleError"
                :error-message="timelineTitleError"
                @keyup.enter="submitTimelineEvent"
              />
              <q-input
                v-model="timelineForm.description"
                label="Description (optional)"
                type="textarea"
                :rows="4"
                class="q-mt-md"
              />
              <div v-if="timelineError" class="text-negative q-mt-sm">{{ timelineError }}</div>
            </q-card-section>
            <q-card-actions align="right">
              <q-btn flat label="Cancel" v-close-popup no-caps />
              <q-btn
                color="primary"
                label="Save"
                :loading="timelineSaving"
                no-caps
                @click="submitTimelineEvent"
              />
            </q-card-actions>
          </q-card>
        </q-dialog>

        <!-- Delete Confirmation Dialog -->
        <q-dialog v-model="showDeleteDialog">
          <q-card style="min-width: 350px">
            <q-card-section>
              <div class="text-h6">Delete {{ deleteTargetLabel }}</div>
            </q-card-section>
            <q-card-section>
              <p>
                Are you sure you want to delete '<strong>{{ deleteTargetName }}</strong
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
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref, watch, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useCharactersStore } from '@/stores/characters'
import { usePlacesStore } from '@/stores/places'
import { useTimelineEventsStore } from '@/stores/timelineEvents'
import Sortable from 'sortablejs'
import EntityCard from '@/components/EntityCard.vue'
import EntityFormDialog from '@/components/EntityFormDialog.vue'

const route = useRoute()
const projectId = route.params.id

const charactersStore = useCharactersStore()
const placesStore = usePlacesStore()
const timelineEventsStore = useTimelineEventsStore()

const tab = ref('characters')
const tabsFetched = ref({ characters: false, places: false, timeline: false })

onMounted(() => {
  tabsFetched.value.characters = true
  charactersStore.fetchCharacters(projectId)
})

watch(tab, (newTab) => {
  if (!tabsFetched.value[newTab]) {
    tabsFetched.value[newTab] = true
    if (newTab === 'places') {
      placesStore.fetchPlaces(projectId)
    } else if (newTab === 'timeline') {
      timelineEventsStore.fetchTimelineEvents(projectId)
    }
  }
})

// ---- Entity Dialog (Characters / Places) ----
const entityType = ref('characters')
const showEntityDialog = ref(false)
const editingEntity = ref(null)
const entitySaving = ref(false)
const entityError = ref('')

const activeEntityLabel = computed(() => {
  return entityType.value === 'characters' ? 'Character' : 'Place'
})

function openCreateEntity(type) {
  entityType.value = type
  editingEntity.value = null
  entityError.value = ''
  entitySaving.value = false
  showEntityDialog.value = true
}

function openEditEntity(type, entity) {
  entityType.value = type
  editingEntity.value = entity
  entityError.value = ''
  entitySaving.value = false
  showEntityDialog.value = true
}

async function onEntitySave(payload) {
  entityError.value = ''
  entitySaving.value = true
  try {
    if (entityType.value === 'characters') {
      if (editingEntity.value) {
        await charactersStore.updateCharacter(projectId, editingEntity.value.id, payload)
      } else {
        await charactersStore.createCharacter(projectId, payload)
      }
    } else {
      if (editingEntity.value) {
        await placesStore.updatePlace(projectId, editingEntity.value.id, payload)
      } else {
        await placesStore.createPlace(projectId, payload)
      }
    }
    showEntityDialog.value = false
  } catch {
    const store = entityType.value === 'characters' ? charactersStore : placesStore
    entityError.value = store.error || `Failed to save ${activeEntityLabel.value.toLowerCase()}.`
  } finally {
    entitySaving.value = false
  }
}

// ---- Timeline Dialog ----
const showTimelineDialog = ref(false)
const editingTimelineEvent = ref(null)
const timelineForm = ref({ title: '', description: '' })
const timelineTitleError = ref('')
const timelineError = ref('')
const timelineSaving = ref(false)

function resetTimelineForm() {
  timelineForm.value = { title: '', description: '' }
  timelineTitleError.value = ''
  timelineError.value = ''
  timelineSaving.value = false
}

function openCreateTimelineEvent() {
  editingTimelineEvent.value = null
  timelineForm.value = {
    title: '',
    description: '',
  }
  timelineTitleError.value = ''
  timelineError.value = ''
  timelineSaving.value = false
  showTimelineDialog.value = true
}

function openEditTimelineEvent(event) {
  editingTimelineEvent.value = event
  timelineForm.value = {
    title: event.title,
    description: event.description || '',
  }
  timelineTitleError.value = ''
  timelineError.value = ''
  timelineSaving.value = false
  showTimelineDialog.value = true
}

async function submitTimelineEvent() {
  if (!timelineForm.value.title.trim()) {
    timelineTitleError.value = 'Title cannot be empty.'
    return
  }
  timelineTitleError.value = ''
  timelineError.value = ''
  timelineSaving.value = true
  try {
    if (editingTimelineEvent.value) {
      await timelineEventsStore.updateTimelineEvent(projectId, editingTimelineEvent.value.id, {
        title: timelineForm.value.title.trim(),
        description: timelineForm.value.description,
      })
    } else {
      const maxOrder = timelineEventsStore.timelineEvents.reduce(
        (max, e) => Math.max(max, e.order),
        -1,
      )
      await timelineEventsStore.createTimelineEvent(projectId, {
        title: timelineForm.value.title.trim(),
        description: timelineForm.value.description,
        order: maxOrder + 1,
      })
    }
    showTimelineDialog.value = false
  } catch {
    timelineError.value = timelineEventsStore.error || 'Failed to save timeline event.'
  } finally {
    timelineSaving.value = false
  }
}

// ---- Timeline Drag Reorder (SortableJS) ----
const timelineContainer = ref(null)
const reordering = ref(false)
let sortableInstance = null

function initSortable() {
  if (!timelineContainer.value) return
  destroySortable()
  sortableInstance = new Sortable(timelineContainer.value, {
    animation: 200,
    handle: '.drag-handle',
    dataIdAttr: 'data-id',
    onEnd: async () => {
      reordering.value = true
      const orderedIds = sortableInstance.toArray().map(Number)
      try {
        await timelineEventsStore.reorderTimelineEvents(projectId, orderedIds)
      } catch {
        // Store already refetched and set error; just display it
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
  () => timelineEventsStore.timelineEvents.length,
  (len) => {
    if (len > 0) {
      nextTick(() => initSortable())
    } else {
      destroySortable()
    }
  },
)

onBeforeUnmount(destroySortable)

// ---- Delete Dialog ----
const showDeleteDialog = ref(false)
const deleteTarget = ref(null)
const deleteType = ref('characters')
const deleteError = ref('')
const deleting = ref(false)

const deleteTargetLabel = computed(() => {
  if (deleteType.value === 'characters') return 'Character'
  if (deleteType.value === 'places') return 'Place'
  return 'Timeline Event'
})

const deleteTargetName = computed(() => {
  if (!deleteTarget.value) return ''
  if (deleteType.value === 'timeline') return deleteTarget.value.title
  return deleteTarget.value.name
})

function openDelete(type, entity) {
  deleteType.value = type
  deleteTarget.value = entity
  deleteError.value = ''
  deleting.value = false
  showDeleteDialog.value = true
}

async function submitDelete() {
  deleteError.value = ''
  deleting.value = true
  try {
    if (deleteType.value === 'characters') {
      await charactersStore.deleteCharacter(projectId, deleteTarget.value.id)
    } else if (deleteType.value === 'places') {
      await placesStore.deletePlace(projectId, deleteTarget.value.id)
    } else {
      await timelineEventsStore.deleteTimelineEvent(projectId, deleteTarget.value.id)
    }
    showDeleteDialog.value = false
  } catch {
    const store =
      deleteType.value === 'characters'
        ? charactersStore
        : deleteType.value === 'places'
          ? placesStore
          : timelineEventsStore
    deleteError.value = store.error || 'Failed to delete.'
  } finally {
    deleting.value = false
  }
}
</script>

<style scoped>
.timeline-list {
  max-width: 700px;
  margin: 0 auto;
}

.timeline-item .drag-handle {
  touch-action: none;
}

.description-preview {
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
