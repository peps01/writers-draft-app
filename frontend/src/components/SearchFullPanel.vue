<template>
  <div class="search-full-panel" style="height: 100%; display: flex; flex-direction: column; overflow: hidden;">
    <!-- Panel header -->
    <div class="panel-header">
      <q-icon name="search" size="sm" />
      <span class="panel-title">
        Results for "{{ searchStore.lastQuery }}"
      </span>
      <span class="search-summary" style="font-size: 0.75rem; color: var(--wda-text-muted); margin-left: 8px;">
        {{ searchStore.totalMatches }} matches ·
        {{ searchStore.totalScenes }} scenes
      </span>
      <q-space />
      <q-btn flat round dense icon="close" @click="$emit('close')" />
    </div>

    <!-- Search input (refinement) -->
    <div class="panel-search-refine">
      <q-input
        :model-value="searchQuery"
        placeholder="Refine search..."
        dense
        outlined
        @update:model-value="$emit('update:search-query', $event); $emit('search-input', $event)"
      >
        <template #prepend><q-icon name="search" /></template>
      </q-input>
    </div>

    <!-- Loading state -->
    <div v-if="searchStore.loading" class="panel-loading">
      <q-spinner color="primary" size="24px" />
      <span>Searching...</span>
    </div>

    <!-- Empty state -->
    <div v-else-if="searchStore.results.length === 0 && searchStore.lastQuery"
      class="panel-empty">
      <q-icon name="search_off" size="2rem" color="grey-5" />
      <p>No results for "{{ searchStore.lastQuery }}"</p>
      <p class="empty-hint">Try a different word or check the spelling.</p>
    </div>

    <!-- Results list -->
    <div v-else class="panel-results-list">
      <div
        v-for="result in searchStore.results"
        :key="result.scene_id"
        class="panel-result-group"
      >
        <!-- Scene header -->
        <div class="result-scene-header">
          <span class="result-scene-number">#{{ result.scene_order }}</span>
          <span class="result-scene-title">
            {{ result.scene_title || 'Untitled Scene' }}
          </span>
          <span class="result-match-badge">
            {{ result.match_count }} match{{ result.match_count !== 1 ? 'es' : '' }}
          </span>
          <q-btn flat dense size="xs" icon="edit" color="primary"
            @click="$emit('navigate', result.scene_id)"
            title="Open scene" />
        </div>

        <!-- Snippets for this scene -->
        <div
          v-for="(snippet, idx) in result.snippets"
          :key="idx"
          class="result-snippet"
          @click="$emit('navigate', result.scene_id)"
        >
          <span v-html="highlightSnippet(snippet.text, searchStore.lastQuery)" />
        </div>
      </div>

      <!-- Load more -->
      <div v-if="searchStore.hasMore" class="panel-load-more">
        <q-btn flat color="primary" label="Load more results"
          :loading="searchStore.loading"
          @click="searchStore.loadMore(currentProjectId)" />
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  searchStore: { type: Object, required: true },
  searchQuery: { type: String, default: '' },
  currentProjectId: { type: [String, Number], default: null },
})

defineEmits(['update:search-query', 'search-input', 'navigate', 'close'])

function highlightSnippet(text, query) {
  if (!text || !query) return text
  const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const regex = new RegExp(`(${escaped})`, 'gi')
  return text.replace(regex,
    '<mark style="background: rgba(245,166,35,0.35); color: inherit; border-radius: 2px; padding: 0 1px;">$1</mark>'
  )
}
</script>

<style scoped>
.panel-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px 14px;
  border-bottom: 1px solid var(--wda-border);
  flex-shrink: 0;
}

.panel-title {
  font-family: var(--wda-font-heading);
  font-size: 0.95rem;
  font-weight: 600;
}

.panel-search-refine {
  padding: 10px 14px;
  border-bottom: 1px solid var(--wda-border);
  flex-shrink: 0;
}

.panel-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 40px;
  color: var(--wda-text-muted);
  font-size: 0.85rem;
}

.panel-empty {
  text-align: center;
  padding: 60px 24px;
  color: var(--wda-text-muted);
}

.panel-empty p {
  margin: 8px 0;
  font-size: 0.85rem;
}

.panel-empty .empty-hint {
  font-size: 0.75rem;
  opacity: 0.7;
}

.panel-results-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.panel-result-group {
  margin-bottom: 4px;
  border-bottom: 1px solid var(--wda-border);
  padding-bottom: 4px;
}

.panel-result-group:last-child {
  border-bottom: none;
}

.result-scene-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px 6px;
  position: sticky;
  top: 0;
  background: var(--wda-surface-2);
  z-index: 1;
}

.result-scene-number {
  font-size: 0.68rem;
  color: var(--wda-text-muted);
  font-weight: 600;
  flex-shrink: 0;
}

.result-scene-title {
  font-family: var(--wda-font-heading);
  font-size: 0.85rem;
  font-weight: 600;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.result-match-badge {
  font-size: 0.68rem;
  padding: 1px 6px;
  border-radius: 8px;
  background: rgba(245, 166, 35, 0.15);
  color: var(--wda-primary);
  font-weight: 600;
  flex-shrink: 0;
}

.result-snippet {
  padding: 6px 14px 6px 28px;
  font-size: 0.78rem;
  color: var(--wda-text-muted);
  line-height: 1.5;
  cursor: pointer;
  transition: background 0.1s;
  border-left: 2px solid transparent;
}

.result-snippet:hover {
  background: var(--wda-surface-2);
  border-left-color: var(--wda-primary);
  color: var(--wda-text);
}

.panel-load-more {
  text-align: center;
  padding: 16px;
}
</style>
