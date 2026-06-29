<template>
  <q-page class="wda-dashboard-page" style="display: flex; flex-direction: column; min-height: 0; flex: 1">
    <!-- Top Row: Projects + AI Tabs -->
    <div class="wda-dashboard-top-row">
      <div class="wda-dashboard-top-row__left">
        <div class="wda-projects-section">
          <div class="row items-center justify-between q-mb-sm">
            <div class="wda-projects-section__title" style="margin-bottom: 0">My Projects</div>
            <q-btn flat dense no-caps icon="add" label="New Project" size="sm" to="/projects/new" />
          </div>
          <div
            class="wda-projects-strip"
            ref="stripRef"
            @mousedown="onStripMouseDown"
            @mousemove="onStripMouseMove"
            @mouseup="onStripMouseUp"
            @mouseleave="onStripMouseUp"
          >
            <div
              v-for="project in projectsStore.projects"
              :key="project.id"
              class="wda-project-card"
              :class="{ 'wda-project-card--active': projectsStore.selectedProjectId === project.id }"
              @click="selectProject(project.id)"
            >
              <div class="wda-project-card__cover">
                <template v-if="project.cover_image">
                  <img :src="project.cover_image" class="wda-project-card__cover-img" />
                </template>
                <span v-else class="wda-project-card__initial">{{ project.title?.charAt(0)?.toUpperCase() || 'P' }}</span>
              </div>
              <div class="wda-project-card__body">
                <div class="wda-project-card__header">
                  <div class="wda-project-card__title ellipsis">{{ project.title }}</div>
                  <q-btn flat dense round icon="more_vert" size="sm" class="wda-project-card__menu-btn" @click.stop>
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
                <div class="wda-project-card__subtitle">{{ project.genre || project.description || 'Novel' }}</div>
                <q-linear-progress
                  :value="progressValue(project.id)"
                  class="wda-project-card__progress"
                  size="4px"
                />
                <div class="wda-project-card__meta">
                  <span>Created: {{ lastEdited(project.created_at) }}</span>
                </div>
              </div>
            </div>

            <!-- Loading skeleton for projects -->
            <template v-if="projectsStore.loading">
              <div v-for="n in 2" :key="'skeleton-' + n" class="wda-project-card">
                <q-skeleton class="wda-project-card__cover" square />
                <div class="wda-project-card__body">
                  <q-skeleton type="text" width="80%" height="20px" />
                  <q-skeleton type="text" width="50%" height="14px" />
                  <q-skeleton type="text" width="60%" height="8px" style="margin-top: 8px" />
                </div>
              </div>
            </template>
          </div>
        </div>
      </div>
      <div class="wda-dashboard-top-row__right" v-if="$q.screen.gt.xs">
        <!-- Panel A: AI / Version Tabs -->
        <div class="wda-right-tab-panel">
          <div class="wda-right-tab-panel__tabs">
            <div
              class="wda-right-tab-panel__tab"
              :class="{ 'wda-right-tab-panel__tab--active': rightTab === 'ai' }"
              @click="onTabChange('ai')"
            >AI Assistant</div>
            <div
              class="wda-right-tab-panel__tab"
              :class="{ 'wda-right-tab-panel__tab--active': rightTab === 'history' }"
              @click="onTabChange('history')"
            >Version History</div>
          </div>

          <div class="wda-right-tab-panel__content">
            <template v-if="rightTab === 'ai'">
              <template v-if="!selectedSceneId">
                <div class="wda-right-tab-panel__empty">Select a scene to view AI history</div>
              </template>

              <template v-else-if="conversationsStore.loading && conversationsStore.messages.length === 0">
                <div>
                  <q-skeleton type="text" width="80%" height="12px" style="margin-bottom: 6px" />
                  <q-skeleton type="text" width="60%" height="12px" style="margin-bottom: 6px" />
                  <q-skeleton type="text" width="70%" height="12px" />
                </div>
              </template>

              <template v-else-if="conversationsStore.messages.length === 0">
                <div class="wda-right-tab-panel__empty">No AI conversations yet</div>
              </template>

              <template v-else>
                <div style="cursor: pointer" @click="goToWritePage">
                  <div v-for="msg in conversationsStore.messages" :key="msg.id" class="q-mb-sm">
                    <template v-if="msg.metadata?.type === 'contradiction_check'">
                      <div style="font-size: 11px; color: var(--wda-text-secondary); background: var(--wda-surface-2); border-radius: 8px; padding: 6px 10px; margin-bottom: 8px">
                        <div style="font-weight: 600; color: var(--wda-text); margin-bottom: 2px">
                          <span class="material-icons" style="font-size: 14px; vertical-align: middle">warning</span>
                          Contradiction Check
                        </div>
                        <template v-if="msg.metadata.has_contradictions">
                          <span style="color: var(--wda-negative, #c75d3a)">{{ msg.metadata.count }} issue(s) found</span>
                        </template>
                        <template v-else>
                          <span style="color: var(--wda-positive, #2d6a4f)">All clear</span>
                        </template>
                      </div>
                    </template>

                    <template v-else>
                      <div class="wda-ai-response">
                        <span class="chat-message-content" v-html="renderMarkdown(msg.content)"></span>
                      </div>
                    </template>
                  </div>
                </div>
              </template>
            </template>

            <template v-else>
              <template v-if="!selectedSceneId">
                <div class="wda-right-tab-panel__empty">Select a scene to view version history</div>
              </template>

              <template v-else-if="sceneVersionsStore.loading && sceneVersionsStore.versions.length === 0">
                <div>
                  <q-skeleton type="text" width="90%" height="12px" style="margin-bottom: 6px" />
                  <q-skeleton type="text" width="70%" height="12px" style="margin-bottom: 6px" />
                  <q-skeleton type="text" width="80%" height="12px" />
                </div>
              </template>

              <template v-else-if="sceneVersionsStore.versions.length === 0">
                <div class="wda-right-tab-panel__empty">No versions yet.</div>
              </template>

              <template v-else>
                <div v-for="version in sceneVersionsStore.versions" :key="version.id" class="wda-version-item">
                  <span class="wda-version-item__time">{{ relativeTimeShort(version.created_at) }}</span>
                  <span class="wda-version-item__preview">{{ previewText(version.content) }}</span>
                  <button class="wda-version-item__action" @click="openInWritePage">Open →</button>
                </div>
                <div v-if="sceneVersionsStore.hasMore" class="wda-load-more" @click="loadMoreVersions">Load more</div>
              </template>
            </template>
          </div>
        </div>
      </div>
    </div>

    <!-- Selected Project Workspace -->
    <div class="wda-workspace-section" v-if="projectsStore.selectedProjectId">
      <div class="wda-workspace-section__title">Selected Project Workspace</div>

      <div class="wda-workspace-row">
        <!-- Scenes Panel -->
        <div class="wda-scenes-panel" v-if="$q.screen.gt.xs">
          <div class="wda-scenes-panel__header workspace-section-header">Scenes</div>

          <div class="wda-scenes-panel__list">
            <template v-if="scenesStore.loading">
              <div v-for="n in 5" :key="'scene-sk-' + n" class="wda-scene-item" style="border: none">
                <q-skeleton type="text" style="width: 100%" />
              </div>
            </template>

            <template v-else-if="scenesStore.scenes.length === 0">
              <div class="wda-scenes-panel__empty">
                <p>No scenes yet.</p>
                <router-link :to="`/projects/${projectsStore.selectedProjectId}/write`" style="color: var(--wda-action); font-size: 12px">
                  Create one in Write page
                </router-link>
              </div>
            </template>

            <template v-else>
              <q-virtual-scroll
                :items="scenesStore.scenes"
                virtual-scroll-item-size="48"
                virtual-scroll-slice-size="20"
                style="height: 100%"
              >
                <template v-slot:default="{ item }">
                  <div
                    :key="item.id"
                    class="wda-scene-item"
                    :class="{ 'wda-scene-item--active': selectedSceneId === item.id }"
                    @click="selectScene(item.id)"
                  >
                    <span class="wda-scene-item__title ellipsis">{{ item.title || 'Untitled Scene' }}</span>
                  </div>
                </template>
              </q-virtual-scroll>
            </template>
          </div>
        </div>

        <!-- Scene Preview Panel -->
        <div
          class="wda-scene-preview"
          :class="{ 'wda-scene-preview--empty': !selectedSceneId || !activeScene?.content }"
          @click="openInWritePage"
        >
          <template v-if="!selectedSceneId">
            <div class="wda-scene-preview__empty">
              <span class="material-icons" style="font-size: 32px; opacity: 0.3">edit_note</span>
              <p>Select a scene to preview</p>
            </div>
          </template>

          <template v-else-if="!activeScene">
            <div class="wda-scene-preview__loading">
              <q-spinner size="32px" color="#1B2A4A" />
            </div>
          </template>

          <template v-else>
            <div class="wda-scene-preview__nav" v-if="$q.screen.xs">
              <button class="wda-scene-nav-btn" :disabled="currentSceneIndex <= 0" @click.stop="prevScene">
                <span class="material-icons">chevron_left</span>
              </button>
              <div class="wda-scene-preview__nav-info">
                <div class="wda-scene-preview__nav-title ellipsis">{{ activeScene.title || 'Untitled Scene' }}</div>
                <div class="wda-scene-preview__nav-count">{{ currentSceneIndex + 1 }} / {{ scenesStore.scenes.length }}</div>
              </div>
              <button class="wda-scene-nav-btn" :disabled="currentSceneIndex >= scenesStore.scenes.length - 1" @click.stop="nextScene">
                <span class="material-icons">chevron_right</span>
              </button>
            </div>
            <div class="wda-scene-preview__title" :class="{ 'with-nav': $q.screen.xs }">{{ activeScene.title || 'Untitled Scene' }}</div>
            <div class="wda-scene-preview__edited">Last Edited: {{ lastEdited(activeScene.updated_at || activeScene.created_at) }}</div>

            <div v-if="!activeScene.content" class="wda-scene-preview__empty" style="height: auto; padding: 20px 0">
              <p>This scene is empty</p>
            </div>

            <div v-else class="wda-scene-preview__content" v-html="activeScene.content" />

            <div class="wda-scene-preview__fab" @click.stop="openInWritePage">
              <span class="material-icons">edit</span>
            </div>
          </template>
        </div>

        <!-- Right Column -->
        <div class="wda-right-column" v-if="$q.screen.gt.xs">
          <!-- Panel A: Story Bible Tags -->
          <div class="wda-tags-panel">
            <div class="wda-tags-panel__title workspace-section-header">Story Bible Tags</div>
            <template v-if="!selectedSceneId">
              <div class="wda-tags-panel__empty">Select a scene to see tags</div>
            </template>
            <template v-else-if="activeScene">
              <div v-if="tagChips.length === 0" class="wda-tags-panel__empty">No tags on this scene</div>
              <div v-else class="wda-tags-panel__chips">
                <span
                  v-for="chip in tagChips"
                  :key="chip.type + '-' + chip.id"
                  class="wda-tag-chip"
                >{{ chip.label }}</span>
              </div>
            </template>
          </div>

          <!-- Panel B: Statistics -->
          <div class="wda-stats-panel">
            <div class="wda-stats-panel__title workspace-section-header">Statistics</div>
            <template v-if="!projectsStore.selectedProjectId">
              <div class="wda-stats-panel__empty">Select a project to view stats</div>
            </template>
            <template v-else-if="statisticsStore.loading">
              <q-skeleton type="rect" height="80px" square style="flex: 1" />
            </template>
            <template v-else-if="statisticsStore.stats?.daily_words">
              <div class="wda-stats-panel__chart">
                <canvas ref="chartCanvas"></canvas>
              </div>
            </template>
            <template v-else>
              <div class="wda-stats-panel__empty">No stats available</div>
            </template>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty state when no projects exist -->
    <div v-else-if="!projectsStore.loading && projectsStore.projects.length === 0" class="wda-dashboard-empty">
      <span class="material-icons" style="font-size: 48px; color: var(--wda-text-muted)">auto_stories</span>
      <p class="wda-dashboard-empty__title">Your story starts here</p>
      <q-btn unelevated color="primary" label="Create your first project" icon="add" to="/projects/new" no-caps />
    </div>

    <!-- Mobile FAB for new project — moved to navbar -->

    <!-- Dialogs -->
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
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { debounce } from 'quasar'
import { useRouter } from 'vue-router'
import { useProjectsStore } from '@/stores/projects'
import { useScenesStore } from '@/stores/scenes'
import { useConversationsStore } from '@/stores/conversations'
import { useSceneVersionsStore } from '@/stores/sceneVersions'
import { useStatisticsStore } from '@/stores/statistics'
import { useCharactersStore } from '@/stores/characters'
import { usePlacesStore } from '@/stores/places'
import { useTimelineEventsStore } from '@/stores/timelineEvents'
import { useGroupsStore } from '@/stores/groups'
import { useItemsStore } from '@/stores/items'
import { useLoreStore } from '@/stores/lore'
import { api } from '@/boot/axios'
import { Chart, registerables } from 'chart.js'
import { renderMarkdown } from '@/utils/markdown'

Chart.register(...registerables)

const router = useRouter()
const projectsStore = useProjectsStore()
const scenesStore = useScenesStore()
const conversationsStore = useConversationsStore()
const sceneVersionsStore = useSceneVersionsStore()
const statisticsStore = useStatisticsStore()
const charactersStore = useCharactersStore()
const placesStore = usePlacesStore()
const timelineEventsStore = useTimelineEventsStore()
const groupsStore = useGroupsStore()
const itemsStore = useItemsStore()
const loreStore = useLoreStore()

const stripRef = ref(null)
const chartCanvas = ref(null)
let chartInstance = null

const tabsFetched = ref({ ai: false, history: false })

const isDragging = ref(false)
const dragStartX = ref(0)
const dragScrollLeft = ref(0)

function onStripMouseDown(e) {
  isDragging.value = true
  dragStartX.value = e.pageX - (stripRef.value?.offsetLeft || 0)
  dragScrollLeft.value = stripRef.value?.scrollLeft || 0
  stripRef.value?.classList.add('wda-projects-strip--dragging')
}

function onStripMouseMove(e) {
  if (!isDragging.value) return
  e.preventDefault()
  const x = e.pageX - (stripRef.value?.offsetLeft || 0)
  const walk = (x - dragStartX.value) * 1.5
  if (stripRef.value) {
    stripRef.value.scrollLeft = dragScrollLeft.value - walk
  }
}

function onStripMouseUp() {
  isDragging.value = false
  stripRef.value?.classList.remove('wda-projects-strip--dragging')
}

// ---- Lazy tab data loading ----
async function loadTabData(tab) {
  if (!selectedSceneId.value || !projectsStore.selectedProjectId) return
  if (tab === 'ai' && !tabsFetched.value.ai) {
    await conversationsStore.fetchOrCreateConversation(projectsStore.selectedProjectId, selectedSceneId.value)
    await conversationsStore.fetchMessages(projectsStore.selectedProjectId)
    tabsFetched.value.ai = true
  }
  if (tab === 'history' && !tabsFetched.value.history) {
    await sceneVersionsStore.fetchVersions(projectsStore.selectedProjectId, selectedSceneId.value)
    tabsFetched.value.history = true
  }
}

function onTabChange(tab) {
  rightTab.value = tab
  loadTabData(tab)
}

const debouncedLoadProjectData = debounce(async (projectId) => {
  await scenesStore.fetchScenes(projectId)
  await statisticsStore.fetchStatistics(projectId)
  await charactersStore.fetchCharacters(projectId)
  await placesStore.fetchPlaces(projectId)
  await timelineEventsStore.fetchTimelineEvents(projectId)
  await groupsStore.fetchGroups(projectId)
  await itemsStore.fetchItems(projectId)
  await loreStore.fetchLore(projectId)
  if (scenesStore.scenes.length > 0) {
    selectScene(scenesStore.scenes[0].id)
  }
}, 200)

const selectedSceneId = ref(null)
const rightTab = ref('ai')
const projectStats = ref({})

const activeScene = computed(() => {
  if (!selectedSceneId.value) return null
  return scenesStore.scenes.find((s) => s.id === selectedSceneId.value) || null
})

const currentSceneIndex = computed(() => {
  if (!selectedSceneId.value) return -1
  return scenesStore.scenes.findIndex((s) => s.id === selectedSceneId.value)
})

function prevScene() {
  const idx = currentSceneIndex.value
  if (idx > 0) selectScene(scenesStore.scenes[idx - 1].id)
}

function nextScene() {
  const idx = currentSceneIndex.value
  if (idx < scenesStore.scenes.length - 1) selectScene(scenesStore.scenes[idx + 1].id)
}

const tagChips = computed(() => {
  if (!activeScene.value) return []
  const chips = []
  const scene = activeScene.value
  if (scene.characters) {
    for (const id of scene.characters) {
      const c = charactersStore.characters.find((ch) => ch.id === id)
      if (c) chips.push({ type: 'character', id: c.id, label: `Character: ${c.name}` })
    }
  }
  if (scene.places) {
    for (const id of scene.places) {
      const p = placesStore.places.find((pl) => pl.id === id)
      if (p) chips.push({ type: 'place', id: p.id, label: `Place: ${p.name}` })
    }
  }
  if (scene.timeline_events) {
    for (const id of scene.timeline_events) {
      const e = timelineEventsStore.timelineEvents.find((ev) => ev.id === id)
      if (e) chips.push({ type: 'event', id: e.id, label: `Event: ${e.title}` })
    }
  }
  if (scene.groups) {
    for (const id of scene.groups) {
      const g = groupsStore.groups.find((gr) => gr.id === id)
      if (g) chips.push({ type: 'group', id: g.id, label: `Group: ${g.name}` })
    }
  }
  if (scene.items) {
    for (const id of scene.items) {
      const i = itemsStore.items.find((it) => it.id === id)
      if (i) chips.push({ type: 'item', id: i.id, label: `Item: ${i.name}` })
    }
  }
  if (scene.lore) {
    for (const id of scene.lore) {
      const l = loreStore.lore.find((lo) => lo.id === id)
      if (l) chips.push({ type: 'lore', id: l.id, label: `Lore: ${l.title}` })
    }
  }
  return chips
})

function progressValue(projectId) {
  const stats = projectStats.value[projectId]
  if (!stats) return 0
  const target = 80000
  return Math.min(1, (stats.total_words || 0) / target)
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

function relativeTimeShort(dateStr) {
  return lastEdited(dateStr)
}

const htmlTagRegex = /<[^>]*>/g
function previewText(content, maxLength = 100) {
  const text = content ? content.replace(htmlTagRegex, '') : ''
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}

async function selectProject(projectId) {
  if (projectsStore.selectedProjectId === projectId) return
  projectsStore.selectedProjectId = projectId
  selectedSceneId.value = null
  rightTab.value = 'ai'
  tabsFetched.value = { ai: false, history: false }
  conversationsStore.reset()
  sceneVersionsStore.versions = []
  debouncedLoadProjectData(projectId)
}

async function selectScene(sceneId) {
  if (selectedSceneId.value === sceneId) return
  selectedSceneId.value = sceneId
  tabsFetched.value = { ai: false, history: false }
  loadTabData(rightTab.value)
}

function loadMoreVersions() {
  sceneVersionsStore.loadMoreVersions(projectsStore.selectedProjectId, selectedSceneId.value)
}

function goToWritePage() {
  if (!projectsStore.selectedProjectId) return
  if (selectedSceneId.value) {
    scenesStore.setActiveScene(selectedSceneId.value)
  }
  router.push(`/projects/${projectsStore.selectedProjectId}/write`)
}

function openInWritePage() {
  if (!projectsStore.selectedProjectId || !selectedSceneId.value) return
  scenesStore.setActiveScene(selectedSceneId.value)
  router.push(`/projects/${projectsStore.selectedProjectId}/write`)
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
  if (projectsStore.projects.length > 0) {
    await fetchProjectStats()
    selectProject(projectsStore.projects[0].id)
  }
})

watch(
  () => statisticsStore.stats,
  () => {
    if (statisticsStore.stats?.daily_words) {
      nextTick(buildChart)
    }
  },
)

function buildChart() {
  if (!chartCanvas.value || !statisticsStore.stats?.daily_words) return
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
  const primaryColor = getComputedStyle(document.body).getPropertyValue('--wda-primary').trim() || '#F4A825'
  const data = statisticsStore.stats.daily_words.slice(-7)
  const labels = data.map((d) => {
    const date = new Date(d.date + 'T00:00:00Z')
    return date.toLocaleDateString('en-US', { weekday: 'short', timeZone: 'UTC' })
  })
  const values = data.map((d) => d.words)
  chartInstance = new Chart(chartCanvas.value, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: values.map((v) => (v > 0 ? primaryColor : '#E8E2D9')),
        borderWidth: 0,
        borderRadius: 2,
        barThickness: 12,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: {
          grid: { display: false },
          ticks: { font: { size: 10, family: 'Inter' }, color: '#9E9587', maxRotation: 0 },
        },
        y: {
          beginAtZero: true,
          grid: { display: false },
          ticks: { font: { size: 10, family: 'Inter' }, color: '#9E9587' },
        },
      },
    },
  })
}

// ---- Dialog state & logic ----
function openEdit(project) {
  router.push(`/projects/${project.id}/edit`)
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
    await projectsStore.renameProject(renameTarget.value.id, renameTitle.value.trim())
    showRenameDialog.value = false
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
    if (projectsStore.selectedProjectId === deleteTarget.value.id) {
      projectsStore.selectedProjectId = null
      selectedSceneId.value = null
      if (projectsStore.projects.length > 0) {
        await fetchProjectStats()
        selectProject(projectsStore.projects[0].id)
      }
    }
  } catch {
    deleteError.value = projectsStore.error || 'Failed to delete project.'
  } finally {
    deleting.value = false
  }
}
</script>

<style scoped>
.wda-scene-nav-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid var(--wda-border);
  background: var(--wda-surface);
  color: var(--wda-text);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
  transition: background .15s, border-color .15s;
}

.wda-scene-nav-btn:hover:not(:disabled) {
  background: var(--wda-surface-2);
  border-color: var(--wda-primary);
}

.wda-scene-nav-btn:disabled {
  opacity: 0.35;
  cursor: default;
}

.wda-scene-nav-btn .material-icons {
  font-size: 20px;
}

.wda-scene-preview__nav {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0 12px;
  border-bottom: 1px solid var(--wda-border);
  margin-bottom: 12px;
}

.wda-scene-preview__nav-info {
  flex: 1;
  min-width: 0;
}

.wda-scene-preview__nav-title {
  font-family: var(--wda-font-ui);
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--wda-text);
}

.wda-scene-preview__nav-count {
  font-size: 0.72rem;
  color: var(--wda-text-muted);
  margin-top: 1px;
}

.chat-message-content {
  line-height: 1.6;
  p { margin: 0 0 0.5em; &:last-child { margin-bottom: 0; } }
  strong { font-weight: 700; }
  em { font-style: italic; }
  ul, ol { margin: 0.3em 0; padding-left: 1.5em; }
  li { margin-bottom: 0.2em; }
  code { font-family: monospace; background: rgba(128, 128, 128, 0.15); border-radius: 3px; padding: 1px 4px; font-size: 0.9em; }
}
</style>
