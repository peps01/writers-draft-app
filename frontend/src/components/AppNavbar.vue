<template>
  <q-header class="wda-navbar bg-white">
    <div class="wda-navbar-inner">
      <div class="wda-navbar-left">
        <span class="wda-navbar-logo-wrapper">
          <img src="/icons/quill.svg" alt="✒️" class="wda-navbar-logo" />
          <span class="wda-wordmark">Writer's Draft</span>
        </span>
      </div>

      <div class="wda-navbar-center">
        <div class="search-bar-wrapper" ref="searchBarWrapperRef">
          <q-input
            v-model="searchQuery"
            :placeholder="isInProject ? 'Search manuscript...' : 'Select a project to search'"
            :disable="!isInProject"
            rounded
            outlined
            dense
            class="wda-search-bar"
            @update:model-value="onSearchInput"
            @focus="onSearchFocus"
            @blur="onSearchBlur"
            @keydown.escape="searchStore.clearSearch()"
            @keydown.enter="openFullResults"
            ref="searchInputRef"
          >
            <template #prepend>
              <q-icon name="search" :color="isInProject ? 'inherit' : 'grey-6'" />
            </template>
            <template #append v-if="searchQuery && isInProject">
              <q-icon name="close" class="cursor-pointer" @click="clearAllSearch" />
            </template>
          </q-input>
        </div>
      </div>

      <div class="wda-navbar-right">
        <button class="wda-navbar-dark-btn" @click="$q.dark.toggle()">
          <span class="material-icons">{{ $q.dark.isActive ? 'light_mode' : 'dark_mode' }}</span>
        </button>

        <button v-if="isProjectRoute" class="wda-navbar-icon-btn" @click="openExportDialog?.()">
          <span class="material-icons">file_download</span>
        </button>

        <button class="wda-navbar-icon-btn" @click="$router.push('/projects/new')">
          <span class="material-icons">add</span>
        </button>

        <button class="wda-navbar-icon-btn" @click="$router.push('/settings')">
          <span class="material-icons">settings</span>
        </button>

        <div class="wda-navbar-avatar" @click.stop>
          {{ userInitial }}
          <q-menu anchor="bottom end" self="top end" :offset="[0, 8]">
            <q-list dense style="min-width: 180px">
              <q-item>
                <q-item-section>
                  <div style="padding: 4px 0">
                    <div style="font-family: 'Inter', sans-serif; font-weight: 600; font-size: 14px; color: var(--wda-text);">
                      {{ authStore.user?.username || 'User' }}
                    </div>
                    <div style="font-family: 'Inter', sans-serif; font-size: 12px; color: var(--wda-text-muted); margin-top: 2px;">
                      {{ authStore.user?.email || '' }}
                    </div>
                  </div>
                </q-item-section>
              </q-item>
              <q-separator />
              <q-item clickable v-close-popup @click="handleLogout">
                <q-item-section>
                  <div class="row items-center q-gutter-xs" style="color: var(--wda-negative, #c75d3a)">
                    <q-icon name="logout" size="xs" />
                    <span style="font-family: 'Inter', sans-serif; font-size: 13px;">Log out</span>
                  </div>
                </q-item-section>
              </q-item>
            </q-list>
          </q-menu>
        </div>
      </div>
    </div>

    <!-- Search Dropdown — teleported to body -->
    <teleport to="body">
      <div
        v-if="searchStore.showDropdown && searchStore.results.length > 0"
        class="search-dropdown"
        :style="dropdownPosition"
      >
        <div class="search-dropdown-header">
          <span class="search-match-count">
            {{ searchStore.totalMatches }} matches in
            {{ searchStore.totalScenes }} scenes
          </span>
          <q-btn flat dense size="xs" label="See all results"
            color="primary" @click="openFullResults" />
        </div>

        <div class="search-dropdown-results">
          <div
            v-for="result in searchStore.results.slice(0, 4)"
            :key="result.scene_id"
            class="search-dropdown-item"
            @mousedown.prevent="navigateToScene(result.scene_id)"
          >
            <div class="search-item-title">{{ result.scene_title || 'Untitled Scene' }}</div>
            <div class="search-item-snippet"
              v-html="highlightSnippet(result.snippets[0]?.text, searchStore.lastQuery)" />
            <div class="search-item-count" v-if="result.match_count > 1">
              +{{ result.match_count - 1 }} more match{{ result.match_count > 2 ? 'es' : '' }}
            </div>
          </div>
        </div>

        <div class="search-dropdown-footer" v-if="searchStore.totalScenes > 4">
          <q-btn flat dense size="sm" color="primary"
            :label="`See all ${searchStore.totalScenes} scenes with results`"
            @click="openFullResults" />
        </div>
      </div>
    </teleport>

    <!-- Full Search Results Panel -->
    <!-- On WritePage: right-positioned dialog like AI/Tags/Notes panels -->
    <q-dialog
      v-if="isWritePage"
      v-model="searchStore.showFullPanel"
      position="right"
      maximized
    >
      <q-card :style="{ width: '480px', maxWidth: '90vw', height: '100%', display: 'flex', flexDirection: 'column', borderRadius: 0, background: 'var(--wda-surface)', border: 'none', borderLeft: '1px solid var(--wda-border)' }" flat>
        <search-full-panel
          :search-store="searchStore"
          :search-query="searchQuery"
          :current-project-id="currentProjectId"
          @update:search-query="searchQuery = $event"
          @search-input="onSearchInput"
          @navigate="navigateToScene"
          @close="searchStore.closeFullPanel()"
        />
      </q-card>
    </q-dialog>

    <!-- On other project pages: centered modal dialog -->
    <q-dialog
      v-else
      v-model="searchStore.showFullPanel"
      maximized
    >
      <q-card class="wda-card" :style="{ maxWidth: '600px', width: '90vw', maxHeight: '80vh' }">
        <search-full-panel
          :search-store="searchStore"
          :search-query="searchQuery"
          :current-project-id="currentProjectId"
          @update:search-query="searchQuery = $event"
          @search-input="onSearchInput"
          @navigate="navigateToScene"
          @close="searchStore.closeFullPanel()"
        />
      </q-card>
    </q-dialog>
  </q-header>
</template>

<script setup>
import { computed, ref, inject, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useSearchStore } from '@/stores/search'
import { useScenesStore } from '@/stores/scenes'
import { useProjectsStore } from '@/stores/projects'
import SearchFullPanel from '@/components/SearchFullPanel.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const searchStore = useSearchStore()
const scenesStore = useScenesStore()
const projectsStore = useProjectsStore()
const openExportDialog = inject('openExportDialog')

const searchQuery = ref('')
const searchInputRef = ref(null)
const searchBarWrapperRef = ref(null)

const userInitial = computed(() => {
  return authStore.user?.username?.charAt(0)?.toUpperCase() || 'U'
})

const isProjectRoute = computed(() => {
  return !!route.params.id
})

const currentProjectId = computed(() => {
  return route.params.id || projectsStore.selectedProjectId || null
})

const isInProject = computed(() => {
  return !!currentProjectId.value
})

const isWritePage = computed(() => {
  return route.path.includes('/write')
})

const dropdownPosition = computed(() => {
  if (!searchInputRef.value) return {}
  const el = searchInputRef.value.$el || searchInputRef.value
  const rect = el.getBoundingClientRect()
  return {
    position: 'fixed',
    top: `${rect.bottom + 4}px`,
    left: `${rect.left}px`,
    width: `${Math.max(rect.width, 360)}px`,
    zIndex: 9999,
  }
})

function onSearchInput(val) {
  if (!currentProjectId.value) return
  searchStore.debouncedSearch(currentProjectId.value, val)
}

function onSearchFocus() {
  if (searchStore.results.length > 0) {
    searchStore.showDropdown = true
  }
}

function onSearchBlur() {
  setTimeout(() => {
    searchStore.showDropdown = false
  }, 200)
}

function openFullResults() {
  if (!currentProjectId.value) return
  searchStore.openFullPanel()
}

function clearAllSearch() {
  searchQuery.value = ''
  searchStore.clearSearch()
}

function highlightSnippet(text, query) {
  if (!text || !query) return text
  const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const regex = new RegExp(`(${escaped})`, 'gi')
  return text.replace(regex,
    '<mark style="background: rgba(245,166,35,0.35); color: inherit; border-radius: 2px; padding: 0 1px;">$1</mark>'
  )
}

async function navigateToScene(sceneId) {
  searchStore.showDropdown = false
  if (route.path.includes('/write') && route.params.id === currentProjectId.value) {
    scenesStore.setActiveScene(sceneId)
  } else {
    await router.push({
      path: `/projects/${currentProjectId.value}/write`,
      query: { scene: sceneId },
    })
  }
  searchQuery.value = ''
  searchStore.clearSearch()
}

watch(currentProjectId, () => {
  searchQuery.value = ''
  searchStore.clearSearch()
})

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.search-bar-wrapper {
  position: relative;
  width: 280px;
  transition: width 0.2s ease;
}

.search-bar-wrapper:focus-within {
  width: 320px;
}
</style>

<style>
.search-dropdown {
  background: var(--wda-surface);
  border: 1px solid var(--wda-border);
  border-radius: var(--wda-radius);
  box-shadow: var(--wda-shadow-md);
  overflow: hidden;
  max-height: 400px;
  display: flex;
  flex-direction: column;
}

.search-dropdown-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 14px;
  border-bottom: 1px solid var(--wda-border);
  background: var(--wda-surface-2);
  font-size: 0.72rem;
  color: var(--wda-text-muted);
  flex-shrink: 0;
}

.search-dropdown-results {
  overflow-y: auto;
  flex: 1;
}

.search-dropdown-item {
  padding: 10px 14px;
  border-bottom: 1px solid var(--wda-border);
  cursor: pointer;
  transition: background 0.1s;
}

.search-dropdown-item:hover {
  background: var(--wda-surface-2);
}

.search-dropdown-item:last-child {
  border-bottom: none;
}

.search-item-title {
  font-family: var(--wda-font-heading);
  font-size: 0.83rem;
  font-weight: 600;
  margin-bottom: 4px;
  color: var(--wda-text);
}

.search-item-snippet {
  font-size: 0.78rem;
  color: var(--wda-text-muted);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.search-item-count {
  font-size: 0.68rem;
  color: var(--wda-primary);
  margin-top: 3px;
}

.search-dropdown-footer {
  padding: 6px 14px;
  border-top: 1px solid var(--wda-border);
  background: var(--wda-surface-2);
  text-align: center;
  flex-shrink: 0;
}

.wda-navbar-logo-wrapper {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.wda-navbar-logo {
  height: 20px;
  width: auto;
  vertical-align: middle;
}
</style>
