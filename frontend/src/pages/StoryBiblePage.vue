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
              label="Back to Project"
              :to="`/projects/${projectId}`"
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

          <q-tabs v-model="tab" @update:model-value="onTabChange">
            <q-tab name="characters" label="Characters" icon="people" />
            <q-tab name="places" label="Places" icon="place" />
            <q-tab name="timeline" label="Timeline" icon="timeline" />
          </q-tabs>

          <q-tab-panels v-model="tab" animated>
            <!-- Characters -->
            <q-tab-panel name="characters">
              <div class="tab-header">
                <div class="tab-title">Characters</div>
                <div class="tab-actions">
                  <q-btn-toggle
                    v-model="viewModeChar"
                    flat
                    dense
                    :options="[
                      { value: 'grid', icon: 'grid_view' },
                      { value: 'list', icon: 'list' },
                    ]"
                    @update:model-value="persistViewMode('characters', $event)"
                  />
                  <q-btn
                    unelevated
                    dense
                    icon="add"
                    label="Add Character"
                    color="primary"
                    no-caps
                    @click="openCreateEntity('characters')"
                    style="font-family: var(--wda-font-ui); font-size: 0.85rem"
                  />
                </div>
              </div>

              <div v-if="charactersStore.loading" class="entity-grid">
                <div v-for="n in 6" :key="n" class="wda-card" style="padding: 20px">
                  <q-skeleton type="text" class="text-h6" />
                  <q-skeleton type="text" width="60%" />
                  <q-skeleton type="text" width="40%" />
                </div>
              </div>

              <div
                v-else-if="charactersStore.error && charactersStore.characters.length === 0"
                class="empty-state"
              >
                <q-icon name="error_outline" size="3rem" style="color: var(--wda-text-muted)" />
                <p class="empty-state-title">Could not load characters</p>
                <p class="empty-state-desc">{{ charactersStore.error }}</p>
                <q-btn
                  unelevated
                  color="primary"
                  label="Retry"
                  @click="charactersStore.fetchCharacters(projectId)"
                  no-caps
                />
              </div>

              <div v-else-if="charactersStore.characters.length === 0" class="empty-state">
                <q-icon name="people" size="3rem" style="color: var(--wda-text-muted)" />
                <p class="empty-state-title">No characters yet</p>
                <p class="empty-state-desc">Every great story has characters worth remembering.</p>
                <q-btn
                  unelevated
                  color="primary"
                  label="Add your first character"
                  icon="add"
                  @click="openCreateEntity('characters')"
                  no-caps
                />
              </div>

              <div v-else-if="viewModeChar === 'list'" class="entity-list-view">
                <div
                  v-for="char in charactersStore.characters"
                  :key="char.id"
                  class="entity-list-item"
                >
                  <div class="entity-list-name">{{ char.name }}</div>
                  <div class="entity-list-desc">{{ char.description || 'No description' }}</div>
                  <q-btn
                    flat
                    dense
                    round
                    icon="edit"
                    size="sm"
                    @click="openEditEntity('characters', char)"
                  />
                  <q-btn
                    flat
                    dense
                    round
                    icon="delete"
                    size="sm"
                    color="negative"
                    @click="openDelete('characters', char)"
                  />
                </div>
              </div>

              <div v-else class="entity-grid">
                <div v-for="char in charactersStore.characters" :key="char.id">
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
              <div class="tab-header">
                <div class="tab-title">Places</div>
                <div class="tab-actions">
                  <q-btn-toggle
                    v-model="viewModePlace"
                    flat
                    dense
                    :options="[
                      { value: 'grid', icon: 'grid_view' },
                      { value: 'list', icon: 'list' },
                    ]"
                    @update:model-value="persistViewMode('places', $event)"
                  />
                  <q-btn
                    unelevated
                    dense
                    icon="add"
                    label="Add Place"
                    color="primary"
                    no-caps
                    @click="openCreateEntity('places')"
                    style="font-family: var(--wda-font-ui); font-size: 0.85rem"
                  />
                </div>
              </div>

              <div v-if="placesStore.loading" class="entity-grid">
                <div v-for="n in 6" :key="n" class="wda-card" style="padding: 20px">
                  <q-skeleton type="text" class="text-h6" />
                  <q-skeleton type="text" width="60%" />
                  <q-skeleton type="text" width="40%" />
                </div>
              </div>

              <div
                v-else-if="placesStore.error && placesStore.places.length === 0"
                class="empty-state"
              >
                <q-icon name="error_outline" size="3rem" style="color: var(--wda-text-muted)" />
                <p class="empty-state-title">Could not load places</p>
                <p class="empty-state-desc">{{ placesStore.error }}</p>
                <q-btn
                  unelevated
                  color="primary"
                  label="Retry"
                  @click="placesStore.fetchPlaces(projectId)"
                  no-caps
                />
              </div>

              <div v-else-if="placesStore.places.length === 0" class="empty-state">
                <q-icon name="place" size="3rem" style="color: var(--wda-text-muted)" />
                <p class="empty-state-title">No places yet</p>
                <p class="empty-state-desc">Every world needs somewhere to call home.</p>
                <q-btn
                  unelevated
                  color="primary"
                  label="Add your first place"
                  icon="add"
                  @click="openCreateEntity('places')"
                  no-caps
                />
              </div>

              <div v-else-if="viewModePlace === 'list'" class="entity-list-view">
                <div v-for="place in placesStore.places" :key="place.id" class="entity-list-item">
                  <div class="entity-list-name">{{ place.name }}</div>
                  <div class="entity-list-desc">{{ place.description || 'No description' }}</div>
                  <q-btn
                    flat
                    dense
                    round
                    icon="edit"
                    size="sm"
                    @click="openEditEntity('places', place)"
                  />
                  <q-btn
                    flat
                    dense
                    round
                    icon="delete"
                    size="sm"
                    color="negative"
                    @click="openDelete('places', place)"
                  />
                </div>
              </div>

              <div v-else class="entity-grid">
                <div v-for="place in placesStore.places" :key="place.id">
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
              <div class="tab-header">
                <div class="tab-title">Timeline Events</div>
                <div class="tab-actions">
                  <q-btn
                    unelevated
                    dense
                    icon="add"
                    label="Add Event"
                    color="primary"
                    no-caps
                    @click="openCreateTimelineEvent"
                    style="font-family: var(--wda-font-ui); font-size: 0.85rem"
                  />
                </div>
              </div>

              <div v-if="timelineEventsStore.loading" class="text-center q-mt-xl">
                <q-spinner size="lg" color="primary" />
              </div>

              <div
                v-else-if="
                  timelineEventsStore.error && timelineEventsStore.timelineEvents.length === 0
                "
                class="empty-state"
              >
                <q-icon name="error_outline" size="3rem" style="color: var(--wda-text-muted)" />
                <p class="empty-state-title">Could not load timeline</p>
                <p class="empty-state-desc">{{ timelineEventsStore.error }}</p>
                <q-btn
                  unelevated
                  color="primary"
                  label="Retry"
                  @click="timelineEventsStore.fetchTimelineEvents(projectId)"
                  no-caps
                />
              </div>

              <div v-else-if="timelineEventsStore.timelineEvents.length === 0" class="empty-state">
                <q-icon name="timeline" size="3rem" style="color: var(--wda-text-muted)" />
                <p class="empty-state-title">No timeline events yet</p>
                <p class="empty-state-desc">Chart the course of your story, one event at a time.</p>
                <q-btn
                  unelevated
                  color="primary"
                  label="Add your first event"
                  icon="add"
                  @click="openCreateTimelineEvent"
                  no-caps
                />
              </div>

              <div v-else ref="timelineContainer">
                <div
                  v-if="reordering"
                  style="
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    color: var(--wda-primary);
                    margin-bottom: 12px;
                    font-size: 0.85rem;
                  "
                >
                  <q-spinner size="sm" />
                  Saving order...
                </div>
                <div
                  v-else-if="timelineEventsStore.error"
                  style="
                    color: var(--wda-negative, #c75d3a);
                    margin-bottom: 12px;
                    font-size: 0.85rem;
                  "
                >
                  {{ timelineEventsStore.error }}
                </div>

                <div
                  v-for="event in timelineEventsStore.timelineEvents"
                  :key="event.id"
                  :data-id="event.id"
                  class="timeline-item"
                >
                  <div class="timeline-order">{{ event.order + 1 }}</div>
                  <div style="flex: 1; min-width: 0">
                    <div style="font-weight: 600; font-family: var(--wda-font-heading)">
                      {{ event.title }}
                    </div>
                    <div
                      v-if="event.description"
                      style="
                        font-size: 0.85rem;
                        color: var(--wda-text-muted);
                        margin-top: 4px;
                        overflow: hidden;
                        text-overflow: ellipsis;
                        display: -webkit-box;
                        -webkit-line-clamp: 2;
                        -webkit-box-orient: vertical;
                      "
                    >
                      {{ event.description }}
                    </div>
                  </div>
                  <q-icon
                    name="drag_indicator"
                    class="drag-handle cursor-grab"
                    size="sm"
                    style="color: var(--wda-text-muted); flex-shrink: 0"
                  />
                  <q-btn flat dense round icon="more_vert" size="sm" @click.stop>
                    <q-menu anchor="bottom end" self="top end">
                      <q-list dense style="min-width: 120px">
                        <q-item clickable v-close-popup @click.stop="openEditTimelineEvent(event)">
                          <q-item-section>Edit</q-item-section>
                        </q-item>
                        <q-item clickable v-close-popup @click.stop="openDelete('timeline', event)">
                          <q-item-section class="text-negative">Delete</q-item-section>
                        </q-item>
                      </q-list>
                    </q-menu>
                  </q-btn>
                </div>
              </div>
            </q-tab-panel>
          </q-tab-panels>

          <!-- Entity Form Dialog -->
          <EntityFormDialog
            v-model="showEntityDialog"
            :entity="editingEntity"
            :entity-label="activeEntityLabel"
            name-label="Name"
            :saving="entitySaving"
            :error-text="entityError"
            @save="onEntitySave"
          />

          <!-- Timeline Event Dialog -->
          <q-dialog v-model="showTimelineDialog" @before-hide="resetTimelineForm">
            <q-card class="wda-card" style="min-width: 400px">
              <q-card-section>
                <div class="text-h6" style="font-family: var(--wda-font-heading)">
                  {{ editingTimelineEvent ? 'Edit' : 'Add' }} Timeline Event
                </div>
              </q-card-section>
              <q-card-section>
                <q-input
                  v-model="timelineForm.title"
                  label="Title"
                  autofocus
                  outlined
                  color="primary"
                  :error="!!timelineTitleError"
                  :error-message="timelineTitleError"
                  @keyup.enter="submitTimelineEvent"
                />
                <q-input
                  v-model="timelineForm.description"
                  label="Description (optional)"
                  type="textarea"
                  :rows="4"
                  outlined
                  color="primary"
                  class="q-mt-md"
                />
                <div v-if="timelineError" class="text-negative q-mt-sm">{{ timelineError }}</div>
              </q-card-section>
              <q-card-actions align="right">
                <q-btn flat label="Cancel" v-close-popup no-caps />
                <q-btn
                  unelevated
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
            <q-card class="wda-card" style="min-width: 350px">
              <q-card-section>
                <div class="text-h6" style="font-family: var(--wda-font-heading)">
                  Delete {{ deleteTargetLabel }}
                </div>
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
        </div>
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

// View modes with localStorage persistence
const viewModeChar = ref(localStorage.getItem('wda_storybible_view_characters') || 'grid')
const viewModePlace = ref(localStorage.getItem('wda_storybible_view_places') || 'grid')

function onTabChange(val) {
  if (!tabsFetched.value[val]) {
    tabsFetched.value[val] = true
    if (val === 'places') {
      placesStore.fetchPlaces(projectId)
    } else if (val === 'timeline') {
      timelineEventsStore.fetchTimelineEvents(projectId)
    }
  }
}

function persistViewMode(tabName, val) {
  localStorage.setItem(`wda_storybible_view_${tabName}`, val)
}

onMounted(() => {
  tabsFetched.value.characters = true
  charactersStore.fetchCharacters(projectId)
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
.drag-handle {
  touch-action: none;
}
</style>
