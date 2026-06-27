<template>
  <q-page>
    <div class="wda-page wda-page--full">
      <q-tabs v-model="tab" @update:model-value="onTabChange">
        <q-tab name="characters" icon="person" :label="`Characters (${charactersStore.characters.length})`" />
        <q-tab name="places" icon="location_on" :label="`Places (${placesStore.places.length})`" />
        <q-tab name="timeline" icon="timeline" :label="`Timeline (${timelineEventsStore.timelineEvents.length})`" />
        <q-tab name="groups" icon="groups" :label="`Groups (${groupsStore.groups.length})`" />
        <q-tab name="items" icon="inventory_2" :label="`Items (${itemsStore.items.length})`" />
        <q-tab name="lore" icon="auto_stories" :label="`Lore (${loreStore.lore.length})`" />
      </q-tabs>

      <q-tab-panels v-model="tab" animated>
        <!-- Characters -->
        <q-tab-panel name="characters">
          <div class="tab-header">
            <q-input v-model="searchChar" placeholder="Search characters..." dense outlined clearable class="tab-search">
              <template #prepend><q-icon name="search" /></template>
            </q-input>
            <div class="tab-actions">
              <q-btn-toggle v-model="viewModeChar" flat dense :options="[{ value: 'grid', icon: 'grid_view' }, { value: 'list', icon: 'list' }]" @update:model-value="persistViewMode('characters', $event)" />
              <q-btn unelevated dense icon="add" label="Add Character" color="primary" no-caps @click="openCreateEntity('characters')" style="font-family: var(--wda-font-ui); font-size: 0.85rem" />
            </div>
          </div>

          <div v-if="charactersStore.loading" class="entity-grid">
            <div v-for="n in 6" :key="n" class="wda-card" style="padding: 20px">
              <q-skeleton type="text" class="text-h6" />
              <q-skeleton type="text" width="60%" />
              <q-skeleton type="text" width="40%" />
            </div>
          </div>

          <div v-else-if="charactersStore.error && filteredCharacters.length === 0" class="empty-state">
            <q-icon name="error_outline" size="3rem" style="color: var(--wda-text-muted)" />
            <p class="empty-state-title">Could not load characters</p>
            <p class="empty-state-desc">{{ charactersStore.error }}</p>
            <q-btn unelevated color="primary" label="Retry" @click="charactersStore.fetchCharacters(projectId)" no-caps />
          </div>

          <div v-else-if="filteredCharacters.length === 0" class="empty-state">
            <q-icon name="person" size="3rem" style="color: var(--wda-text-muted)" />
            <p class="empty-state-title">{{ searchChar ? 'No characters match your search' : 'No characters yet' }}</p>
            <p class="empty-state-desc">{{ searchChar ? 'Try a different search term.' : 'Every great story has characters worth remembering.' }}</p>
            <q-btn v-if="!searchChar" unelevated color="primary" label="Add your first character" icon="add" @click="openCreateEntity('characters')" no-caps />
          </div>

          <div v-else-if="viewModeChar === 'list'" class="entity-list-view">
            <div v-for="char in filteredCharacters" :key="char.id" class="entity-list-item">
              <div class="entity-list-name">{{ char.name }}</div>
              <div class="entity-list-desc">{{ char.description || 'No description' }}</div>
              <div class="entity-list-actions">
                <q-btn flat dense round icon="edit" size="sm" @click="openEditEntity('characters', char)" />
                <q-btn flat dense round icon="delete" size="sm" color="negative" @click="openDelete('characters', char)" />
              </div>
            </div>
          </div>

          <div v-else class="entity-grid">
            <div v-for="char in filteredCharacters" :key="char.id" class="entity-grid-card" style="--entity-color: #F5A623">
              <div class="card-stripe"></div>
              <div class="card-body">
                <div class="card-name">{{ char.name }}</div>
                <div class="card-desc">{{ char.description || 'No description' }}</div>
              </div>
              <div class="card-footer">
                <q-btn flat dense round icon="edit" size="sm" @click="openEditEntity('characters', char)" />
                <q-btn flat dense round icon="delete" size="sm" color="negative" @click="openDelete('characters', char)" />
              </div>
            </div>
          </div>
        </q-tab-panel>

        <!-- Places -->
        <q-tab-panel name="places">
          <div class="tab-header">
            <q-input v-model="searchPlace" placeholder="Search places..." dense outlined clearable class="tab-search">
              <template #prepend><q-icon name="search" /></template>
            </q-input>
            <div class="tab-actions">
              <q-btn-toggle v-model="viewModePlace" flat dense :options="[{ value: 'grid', icon: 'grid_view' }, { value: 'list', icon: 'list' }]" @update:model-value="persistViewMode('places', $event)" />
              <q-btn unelevated dense icon="add" label="Add Place" color="primary" no-caps @click="openCreateEntity('places')" style="font-family: var(--wda-font-ui); font-size: 0.85rem" />
            </div>
          </div>

          <div v-if="placesStore.loading" class="entity-grid">
            <div v-for="n in 6" :key="n" class="wda-card" style="padding: 20px">
              <q-skeleton type="text" class="text-h6" />
              <q-skeleton type="text" width="60%" />
              <q-skeleton type="text" width="40%" />
            </div>
          </div>

          <div v-else-if="placesStore.error && filteredPlaces.length === 0" class="empty-state">
            <q-icon name="error_outline" size="3rem" style="color: var(--wda-text-muted)" />
            <p class="empty-state-title">Could not load places</p>
            <p class="empty-state-desc">{{ placesStore.error }}</p>
            <q-btn unelevated color="primary" label="Retry" @click="placesStore.fetchPlaces(projectId)" no-caps />
          </div>

          <div v-else-if="filteredPlaces.length === 0" class="empty-state">
            <q-icon name="location_on" size="3rem" style="color: var(--wda-text-muted)" />
            <p class="empty-state-title">{{ searchPlace ? 'No places match your search' : 'No places yet' }}</p>
            <p class="empty-state-desc">{{ searchPlace ? 'Try a different search term.' : 'Every world needs somewhere to call home.' }}</p>
            <q-btn v-if="!searchPlace" unelevated color="primary" label="Add your first place" icon="add" @click="openCreateEntity('places')" no-caps />
          </div>

          <div v-else-if="viewModePlace === 'list'" class="entity-list-view">
            <div v-for="place in filteredPlaces" :key="place.id" class="entity-list-item">
              <div class="entity-list-name">{{ place.name }}</div>
              <div class="entity-list-desc">{{ place.description || 'No description' }}</div>
              <div class="entity-list-actions">
                <q-btn flat dense round icon="edit" size="sm" @click="openEditEntity('places', place)" />
                <q-btn flat dense round icon="delete" size="sm" color="negative" @click="openDelete('places', place)" />
              </div>
            </div>
          </div>

          <div v-else class="entity-grid">
            <div v-for="place in filteredPlaces" :key="place.id" class="entity-grid-card" style="--entity-color: #4A90D9">
              <div class="card-stripe"></div>
              <div class="card-body">
                <div class="card-name">{{ place.name }}</div>
                <div class="card-desc">{{ place.description || 'No description' }}</div>
              </div>
              <div class="card-footer">
                <q-btn flat dense round icon="edit" size="sm" @click="openEditEntity('places', place)" />
                <q-btn flat dense round icon="delete" size="sm" color="negative" @click="openDelete('places', place)" />
              </div>
            </div>
          </div>
        </q-tab-panel>

        <!-- Timeline -->
        <q-tab-panel name="timeline">
          <div class="tab-header">
            <q-input v-model="searchTimeline" placeholder="Search timeline events..." dense outlined clearable class="tab-search">
              <template #prepend><q-icon name="search" /></template>
            </q-input>
            <div class="tab-actions">
              <q-btn unelevated dense icon="add" label="Add Event" color="primary" no-caps @click="openCreateTimelineEvent" style="font-family: var(--wda-font-ui); font-size: 0.85rem" />
            </div>
          </div>

          <div v-if="timelineEventsStore.loading" class="text-center q-mt-xl">
            <q-spinner size="lg" color="primary" />
          </div>

          <div v-else-if="timelineEventsStore.error && filteredTimelineEvents.length === 0" class="empty-state">
            <q-icon name="error_outline" size="3rem" style="color: var(--wda-text-muted)" />
            <p class="empty-state-title">Could not load timeline</p>
            <p class="empty-state-desc">{{ timelineEventsStore.error }}</p>
            <q-btn unelevated color="primary" label="Retry" @click="timelineEventsStore.fetchTimelineEvents(projectId)" no-caps />
          </div>

          <div v-else-if="filteredTimelineEvents.length === 0" class="empty-state">
            <q-icon name="timeline" size="3rem" style="color: var(--wda-text-muted)" />
            <p class="empty-state-title">{{ searchTimeline ? 'No events match your search' : 'No timeline events yet' }}</p>
            <p class="empty-state-desc">{{ searchTimeline ? 'Try a different search term.' : 'Chart the course of your story, one event at a time.' }}</p>
            <q-btn v-if="!searchTimeline" unelevated color="primary" label="Add your first event" icon="add" @click="openCreateTimelineEvent" no-caps />
          </div>

          <div v-else ref="timelineContainer">
            <div v-if="reordering" style="display: flex; align-items: center; gap: 8px; color: var(--wda-primary); margin-bottom: 12px; font-size: 0.85rem">
              <q-spinner size="sm" /> Saving order...
            </div>
            <div v-else-if="timelineEventsStore.error" style="color: var(--wda-negative, #c75d3a); margin-bottom: 12px; font-size: 0.85rem">
              {{ timelineEventsStore.error }}
            </div>

            <div v-for="event in filteredTimelineEvents" :key="event.id" :data-id="event.id" class="timeline-item">
              <div class="timeline-order">{{ event.order + 1 }}</div>
              <div style="flex: 1; min-width: 0">
                <div style="font-weight: 600; font-family: var(--wda-font-heading)">{{ event.title }}</div>
                <div v-if="event.description" style="font-size: 0.85rem; color: var(--wda-text-muted); margin-top: 4px; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical">{{ event.description }}</div>
              </div>
              <q-icon name="drag_indicator" class="drag-handle cursor-grab" size="sm" style="color: var(--wda-text-muted); flex-shrink: 0" />
              <q-btn flat dense round icon="more_vert" size="sm" @click.stop>
                <q-menu anchor="bottom end" self="top end">
                  <q-list dense style="min-width: 120px">
                    <q-item clickable v-close-popup @click.stop="openEditTimelineEvent(event)"><q-item-section>Edit</q-item-section></q-item>
                    <q-item clickable v-close-popup @click.stop="openDelete('timeline', event)"><q-item-section class="text-negative">Delete</q-item-section></q-item>
                  </q-list>
                </q-menu>
              </q-btn>
            </div>
          </div>
        </q-tab-panel>

        <!-- Groups -->
        <q-tab-panel name="groups">
          <div class="tab-header">
            <q-input v-model="searchGroup" placeholder="Search groups..." dense outlined clearable class="tab-search">
              <template #prepend><q-icon name="search" /></template>
            </q-input>
            <div class="tab-actions">
              <q-btn-toggle v-model="viewModeGroup" flat dense :options="[{ value: 'grid', icon: 'grid_view' }, { value: 'list', icon: 'list' }]" @update:model-value="persistViewMode('groups', $event)" />
              <q-btn unelevated dense icon="add" label="Add Group" color="primary" no-caps @click="openEntityTypeForm('groups')" style="font-family: var(--wda-font-ui); font-size: 0.85rem" />
            </div>
          </div>

          <div v-if="groupsStore.loading" class="entity-grid">
            <div v-for="n in 6" :key="n" class="wda-card" style="padding: 20px">
              <q-skeleton type="text" class="text-h6" />
              <q-skeleton type="text" width="60%" />
              <q-skeleton type="text" width="40%" />
            </div>
          </div>

          <div v-else-if="groupsStore.error && filteredGroups.length === 0" class="empty-state">
            <q-icon name="error_outline" size="3rem" style="color: var(--wda-text-muted)" />
            <p class="empty-state-title">Could not load groups</p>
            <p class="empty-state-desc">{{ groupsStore.error }}</p>
            <q-btn unelevated color="primary" label="Retry" @click="groupsStore.fetchGroups(projectId)" no-caps />
          </div>

          <div v-else-if="filteredGroups.length === 0" class="empty-state">
            <q-icon name="groups" size="3rem" style="color: var(--wda-text-muted)" />
            <p class="empty-state-title">{{ searchGroup ? 'No groups match your search' : 'No groups yet' }}</p>
            <p class="empty-state-desc">{{ searchGroup ? 'Try a different search term.' : 'Organize your factions, organizations, and guilds.' }}</p>
            <q-btn v-if="!searchGroup" unelevated color="primary" label="Add your first group" icon="add" @click="openEntityTypeForm('groups')" no-caps />
          </div>

          <div v-else-if="viewModeGroup === 'list'" class="entity-list-view">
            <div v-for="entry in filteredGroups" :key="entry.id" class="entity-list-item">
              <div class="entity-list-name">{{ entry.name }} <span v-if="entry.group_type" class="entity-type-badge">{{ entry.group_type }}</span></div>
              <div class="entity-list-desc">{{ entry.description || 'No description' }}</div>
              <div class="entity-list-actions">
                <q-btn flat dense round icon="edit" size="sm" @click="openEditEntityType('groups', entry)" />
                <q-btn flat dense round icon="delete" size="sm" color="negative" @click="openDelete('groups', entry)" />
              </div>
            </div>
          </div>

          <div v-else class="entity-grid">
            <div v-for="entry in filteredGroups" :key="entry.id" class="entity-grid-card" style="--entity-color: #2D6A4F">
              <div class="card-stripe"></div>
              <div class="card-body">
                <div class="card-name">{{ entry.name }}</div>
                <div v-if="entry.group_type" class="card-type-badge entity-type-badge">{{ entry.group_type }}</div>
                <div class="card-desc">{{ entry.description || 'No description' }}</div>
              </div>
              <div class="card-footer">
                <q-btn flat dense round icon="edit" size="sm" @click="openEditEntityType('groups', entry)" />
                <q-btn flat dense round icon="delete" size="sm" color="negative" @click="openDelete('groups', entry)" />
              </div>
            </div>
          </div>
        </q-tab-panel>

        <!-- Items -->
        <q-tab-panel name="items">
          <div class="tab-header">
            <q-input v-model="searchItem" placeholder="Search items..." dense outlined clearable class="tab-search">
              <template #prepend><q-icon name="search" /></template>
            </q-input>
            <div class="tab-actions">
              <q-btn-toggle v-model="viewModeItem" flat dense :options="[{ value: 'grid', icon: 'grid_view' }, { value: 'list', icon: 'list' }]" @update:model-value="persistViewMode('items', $event)" />
              <q-btn unelevated dense icon="add" label="Add Item" color="primary" no-caps @click="openEntityTypeForm('items')" style="font-family: var(--wda-font-ui); font-size: 0.85rem" />
            </div>
          </div>

          <div v-if="itemsStore.loading" class="entity-grid">
            <div v-for="n in 6" :key="n" class="wda-card" style="padding: 20px">
              <q-skeleton type="text" class="text-h6" />
              <q-skeleton type="text" width="60%" />
              <q-skeleton type="text" width="40%" />
            </div>
          </div>

          <div v-else-if="itemsStore.error && filteredItems.length === 0" class="empty-state">
            <q-icon name="error_outline" size="3rem" style="color: var(--wda-text-muted)" />
            <p class="empty-state-title">Could not load items</p>
            <p class="empty-state-desc">{{ itemsStore.error }}</p>
            <q-btn unelevated color="primary" label="Retry" @click="itemsStore.fetchItems(projectId)" no-caps />
          </div>

          <div v-else-if="filteredItems.length === 0" class="empty-state">
            <q-icon name="inventory_2" size="3rem" style="color: var(--wda-text-muted)" />
            <p class="empty-state-title">{{ searchItem ? 'No items match your search' : 'No items yet' }}</p>
            <p class="empty-state-desc">{{ searchItem ? 'Try a different search term.' : 'Artifacts, weapons, and objects of power await.' }}</p>
            <q-btn v-if="!searchItem" unelevated color="primary" label="Add your first item" icon="add" @click="openEntityTypeForm('items')" no-caps />
          </div>

          <div v-else-if="viewModeItem === 'list'" class="entity-list-view">
            <div v-for="entry in filteredItems" :key="entry.id" class="entity-list-item">
              <div class="entity-list-name">{{ entry.name }} <span v-if="entry.item_type" class="entity-type-badge">{{ entry.item_type }}</span></div>
              <div class="entity-list-desc">{{ entry.description || 'No description' }}</div>
              <div class="entity-list-actions">
                <q-btn flat dense round icon="edit" size="sm" @click="openEditEntityType('items', entry)" />
                <q-btn flat dense round icon="delete" size="sm" color="negative" @click="openDelete('items', entry)" />
              </div>
            </div>
          </div>

          <div v-else class="entity-grid">
            <div v-for="entry in filteredItems" :key="entry.id" class="entity-grid-card" style="--entity-color: #C75D3A">
              <div class="card-stripe"></div>
              <div class="card-body">
                <div class="card-name">{{ entry.name }}</div>
                <div v-if="entry.item_type" class="card-type-badge entity-type-badge">{{ entry.item_type }}</div>
                <div class="card-desc">{{ entry.description || 'No description' }}</div>
              </div>
              <div class="card-footer">
                <q-btn flat dense round icon="edit" size="sm" @click="openEditEntityType('items', entry)" />
                <q-btn flat dense round icon="delete" size="sm" color="negative" @click="openDelete('items', entry)" />
              </div>
            </div>
          </div>
        </q-tab-panel>

        <!-- Lore -->
        <q-tab-panel name="lore">
          <div class="tab-header">
            <q-input v-model="searchLore" placeholder="Search lore..." dense outlined clearable class="tab-search">
              <template #prepend><q-icon name="search" /></template>
            </q-input>
            <div class="tab-actions">
              <q-btn-toggle v-model="viewModeLore" flat dense :options="[{ value: 'grid', icon: 'grid_view' }, { value: 'list', icon: 'list' }]" @update:model-value="persistViewMode('lore', $event)" />
              <q-btn unelevated dense icon="add" label="Add Lore" color="primary" no-caps @click="openEntityTypeForm('lore')" style="font-family: var(--wda-font-ui); font-size: 0.85rem" />
            </div>
          </div>

          <div v-if="loreStore.loading" class="entity-grid">
            <div v-for="n in 6" :key="n" class="wda-card" style="padding: 20px">
              <q-skeleton type="text" class="text-h6" />
              <q-skeleton type="text" width="60%" />
              <q-skeleton type="text" width="40%" />
            </div>
          </div>

          <div v-else-if="loreStore.error && filteredLore.length === 0" class="empty-state">
            <q-icon name="error_outline" size="3rem" style="color: var(--wda-text-muted)" />
            <p class="empty-state-title">Could not load lore</p>
            <p class="empty-state-desc">{{ loreStore.error }}</p>
            <q-btn unelevated color="primary" label="Retry" @click="loreStore.fetchLore(projectId)" no-caps />
          </div>

          <div v-else-if="filteredLore.length === 0" class="empty-state">
            <q-icon name="auto_stories" size="3rem" style="color: var(--wda-text-muted)" />
            <p class="empty-state-title">{{ searchLore ? 'No lore entries match your search' : 'No lore yet' }}</p>
            <p class="empty-state-desc">{{ searchLore ? 'Try a different search term.' : 'Build your world with magic, history, and myth.' }}</p>
            <q-btn v-if="!searchLore" unelevated color="primary" label="Add your first lore entry" icon="add" @click="openEntityTypeForm('lore')" no-caps />
          </div>

          <div v-else-if="viewModeLore === 'list'" class="entity-list-view">
            <div v-for="entry in filteredLore" :key="entry.id" class="entity-list-item">
              <div class="entity-list-name">{{ entry.title }} <span v-if="entry.lore_type" class="entity-type-badge">{{ entry.lore_type }}</span></div>
              <div class="entity-list-desc">{{ entry.description || 'No description' }}</div>
              <div class="entity-list-actions">
                <q-btn flat dense round icon="edit" size="sm" @click="openEditEntityType('lore', entry)" />
                <q-btn flat dense round icon="delete" size="sm" color="negative" @click="openDelete('lore', entry)" />
              </div>
            </div>
          </div>

          <div v-else class="entity-grid">
            <div v-for="entry in filteredLore" :key="entry.id" class="entity-grid-card" style="--entity-color: #5B8DB8">
              <div class="card-stripe"></div>
              <div class="card-body">
                <div class="card-name">{{ entry.title }}</div>
                <div v-if="entry.lore_type" class="card-type-badge entity-type-badge">{{ entry.lore_type }}</div>
                <div class="card-desc">{{ entry.description || 'No description' }}</div>
              </div>
              <div class="card-footer">
                <q-btn flat dense round icon="edit" size="sm" @click="openEditEntityType('lore', entry)" />
                <q-btn flat dense round icon="delete" size="sm" color="negative" @click="openDelete('lore', entry)" />
              </div>
            </div>
          </div>
        </q-tab-panel>
      </q-tab-panels>

      <!-- Entity Form Dialog (Characters / Places) -->
      <EntityFormDialog v-model="showEntityDialog" :entity="editingEntity" :entity-label="activeEntityLabel" name-label="Name" :saving="entitySaving" :error-text="entityError" @save="onEntitySave" />

      <!-- Entity Type Dialog (Groups / Items / Lore) -->
      <q-dialog v-model="showEntityTypeDialog" @before-hide="resetEntityTypeForm">
        <q-card class="wda-card" style="min-width: 400px">
          <q-card-section>
            <div class="text-h6" style="font-family: var(--wda-font-heading)">{{ editingEntityType ? 'Edit' : 'Add' }} {{ entityTypeLabel }}</div>
          </q-card-section>
          <q-card-section>
            <q-input v-model="entityTypeForm.name" :label="entityTypeNameLabel" autofocus outlined color="primary" :error="!!entityTypeNameError" :error-message="entityTypeNameError" @keyup.enter="submitEntityType" />
            <q-input v-model="entityTypeForm.type" :label="entityTypeTypeLabel" outlined color="primary" class="q-mt-md" placeholder="e.g. Faction, Organization, Guild..." />
            <q-input v-model="entityTypeForm.description" label="Description (optional)" type="textarea" :rows="4" outlined color="primary" class="q-mt-md" />
            <div v-if="entityTypeError" class="text-negative q-mt-sm">{{ entityTypeError }}</div>
          </q-card-section>
          <q-card-actions align="right">
            <q-btn flat label="Cancel" v-close-popup no-caps />
            <q-btn unelevated color="primary" label="Save" :loading="entityTypeSaving" no-caps @click="submitEntityType" />
          </q-card-actions>
        </q-card>
      </q-dialog>

      <!-- Timeline Event Dialog -->
      <q-dialog v-model="showTimelineDialog" @before-hide="resetTimelineForm">
        <q-card class="wda-card" style="min-width: 400px">
          <q-card-section>
            <div class="text-h6" style="font-family: var(--wda-font-heading)">{{ editingTimelineEvent ? 'Edit' : 'Add' }} Timeline Event</div>
          </q-card-section>
          <q-card-section>
            <q-input v-model="timelineForm.title" label="Title" autofocus outlined color="primary" :error="!!timelineTitleError" :error-message="timelineTitleError" @keyup.enter="submitTimelineEvent" />
            <q-input v-model="timelineForm.description" label="Description (optional)" type="textarea" :rows="4" outlined color="primary" class="q-mt-md" />
            <div v-if="timelineError" class="text-negative q-mt-sm">{{ timelineError }}</div>
          </q-card-section>
          <q-card-actions align="right">
            <q-btn flat label="Cancel" v-close-popup no-caps />
            <q-btn unelevated color="primary" label="Save" :loading="timelineSaving" no-caps @click="submitTimelineEvent" />
          </q-card-actions>
        </q-card>
      </q-dialog>

      <!-- Delete Confirmation Dialog -->
      <q-dialog v-model="showDeleteDialog">
        <q-card class="wda-card" style="min-width: 350px">
          <q-card-section>
            <div class="text-h6" style="font-family: var(--wda-font-heading)">Delete {{ deleteTargetLabel }}</div>
          </q-card-section>
          <q-card-section>
            <p>Are you sure you want to delete '<strong>{{ deleteTargetName }}</strong>'? This cannot be undone.</p>
            <div v-if="deleteError" class="text-negative">{{ deleteError }}</div>
          </q-card-section>
          <q-card-actions align="right">
            <q-btn flat label="Cancel" v-close-popup no-caps />
            <q-btn unelevated color="negative" label="Delete" :loading="deleting" no-caps @click="submitDelete" />
          </q-card-actions>
        </q-card>
      </q-dialog>
    </div>
  </q-page>
</template>

<script setup>
import { ref, watch, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useCharactersStore } from '@/stores/characters'
import { usePlacesStore } from '@/stores/places'
import { useTimelineEventsStore } from '@/stores/timelineEvents'
import { useGroupsStore } from '@/stores/groups'
import { useItemsStore } from '@/stores/items'
import { useLoreStore } from '@/stores/lore'
import Sortable from 'sortablejs'
import EntityFormDialog from '@/components/EntityFormDialog.vue'

const route = useRoute()
const projectId = route.params.id

const charactersStore = useCharactersStore()
const placesStore = usePlacesStore()
const timelineEventsStore = useTimelineEventsStore()
const groupsStore = useGroupsStore()
const itemsStore = useItemsStore()
const loreStore = useLoreStore()

const tab = ref('characters')
const tabsFetched = ref({ characters: false, places: false, timeline: false, groups: false, items: false, lore: false })

// Search queries per tab
const searchChar = ref('')
const searchPlace = ref('')
const searchTimeline = ref('')
const searchGroup = ref('')
const searchItem = ref('')
const searchLore = ref('')

// Filtered computed
const filteredCharacters = computed(() => {
  if (!searchChar.value) return charactersStore.characters
  const q = searchChar.value.toLowerCase()
  return charactersStore.characters.filter(c => c.name.toLowerCase().includes(q))
})
const filteredPlaces = computed(() => {
  if (!searchPlace.value) return placesStore.places
  const q = searchPlace.value.toLowerCase()
  return placesStore.places.filter(p => p.name.toLowerCase().includes(q))
})
const filteredTimelineEvents = computed(() => {
  if (!searchTimeline.value) return timelineEventsStore.timelineEvents
  const q = searchTimeline.value.toLowerCase()
  return timelineEventsStore.timelineEvents.filter(e => e.title.toLowerCase().includes(q))
})
const filteredGroups = computed(() => {
  if (!searchGroup.value) return groupsStore.groups
  const q = searchGroup.value.toLowerCase()
  return groupsStore.groups.filter(g => g.name.toLowerCase().includes(q))
})
const filteredItems = computed(() => {
  if (!searchItem.value) return itemsStore.items
  const q = searchItem.value.toLowerCase()
  return itemsStore.items.filter(i => i.name.toLowerCase().includes(q))
})
const filteredLore = computed(() => {
  if (!searchLore.value) return loreStore.lore
  const q = searchLore.value.toLowerCase()
  return loreStore.lore.filter(l => l.title.toLowerCase().includes(q))
})

// Reset search when switching tabs
watch(tab, () => {
  searchChar.value = ''
  searchPlace.value = ''
  searchTimeline.value = ''
  searchGroup.value = ''
  searchItem.value = ''
  searchLore.value = ''
})

// View modes with localStorage persistence
const viewModeChar = ref(localStorage.getItem('wda_storybible_view_characters') || 'grid')
const viewModePlace = ref(localStorage.getItem('wda_storybible_view_places') || 'grid')
const viewModeGroup = ref(localStorage.getItem('wda_storybible_view_groups') || 'grid')
const viewModeItem = ref(localStorage.getItem('wda_storybible_view_items') || 'grid')
const viewModeLore = ref(localStorage.getItem('wda_storybible_view_lore') || 'grid')

function persistViewMode(tabName, val) {
  localStorage.setItem(`wda_storybible_view_${tabName}`, val)
}

function onTabChange(val) {
  if (!tabsFetched.value[val]) {
    tabsFetched.value[val] = true
    if (val === 'places') placesStore.fetchPlaces(projectId)
    else if (val === 'timeline') timelineEventsStore.fetchTimelineEvents(projectId)
    else if (val === 'groups') groupsStore.fetchGroups(projectId)
    else if (val === 'items') itemsStore.fetchItems(projectId)
    else if (val === 'lore') loreStore.fetchLore(projectId)
  }
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

// ---- Entity Type Dialog (Groups / Items / Lore) ----
const showEntityTypeDialog = ref(false)
const entityTypeFormType = ref('groups')
const editingEntityType = ref(null)
const entityTypeForm = ref({ name: '', type: '', description: '' })
const entityTypeNameError = ref('')
const entityTypeError = ref('')
const entityTypeSaving = ref(false)

const entityTypeLabel = computed(() => {
  if (entityTypeFormType.value === 'groups') return 'Group'
  if (entityTypeFormType.value === 'items') return 'Item'
  return 'Lore Entry'
})

const entityTypeNameLabel = computed(() => {
  return entityTypeFormType.value === 'lore' ? 'Title' : 'Name'
})

const entityTypeTypeLabel = computed(() => {
  if (entityTypeFormType.value === 'groups') return 'Group Type'
  if (entityTypeFormType.value === 'items') return 'Item Type'
  return 'Lore Type'
})

function resetEntityTypeForm() {
  entityTypeForm.value = { name: '', type: '', description: '' }
  entityTypeNameError.value = ''
  entityTypeError.value = ''
  entityTypeSaving.value = false
}

function openEntityTypeForm(type) {
  entityTypeFormType.value = type
  editingEntityType.value = null
  resetEntityTypeForm()
  showEntityTypeDialog.value = true
}

function openEditEntityType(type, entity) {
  entityTypeFormType.value = type
  editingEntityType.value = entity
  entityTypeForm.value = {
    name: entity.name || entity.title || '',
    type: entity.group_type || entity.item_type || entity.lore_type || '',
    description: entity.description || '',
  }
  entityTypeNameError.value = ''
  entityTypeError.value = ''
  entityTypeSaving.value = false
  showEntityTypeDialog.value = true
}

async function submitEntityType() {
  if (!entityTypeForm.value.name.trim()) {
    entityTypeNameError.value = `${entityTypeNameLabel.value} cannot be empty.`
    return
  }
  entityTypeNameError.value = ''
  entityTypeError.value = ''
  entityTypeSaving.value = true
  try {
    const payload = { description: entityTypeForm.value.description }
    if (entityTypeFormType.value === 'lore') {
      payload.title = entityTypeForm.value.name.trim()
      payload.lore_type = entityTypeForm.value.type.trim()
    } else {
      payload.name = entityTypeForm.value.name.trim()
      if (entityTypeFormType.value === 'groups') payload.group_type = entityTypeForm.value.type.trim()
      else payload.item_type = entityTypeForm.value.type.trim()
    }
    if (editingEntityType.value) {
      if (entityTypeFormType.value === 'groups') {
        await groupsStore.updateGroup(projectId, editingEntityType.value.id, payload)
      } else if (entityTypeFormType.value === 'items') {
        await itemsStore.updateItem(projectId, editingEntityType.value.id, payload)
      } else {
        await loreStore.updateLore(projectId, editingEntityType.value.id, payload)
      }
    } else {
      if (entityTypeFormType.value === 'groups') {
        await groupsStore.createGroup(projectId, payload)
      } else if (entityTypeFormType.value === 'items') {
        await itemsStore.createItem(projectId, payload)
      } else {
        await loreStore.createLore(projectId, payload)
      }
    }
    showEntityTypeDialog.value = false
  } catch {
    const store = entityTypeFormType.value === 'groups' ? groupsStore : entityTypeFormType.value === 'items' ? itemsStore : loreStore
    entityTypeError.value = store.error || `Failed to save ${entityTypeLabel.value.toLowerCase()}.`
  } finally {
    entityTypeSaving.value = false
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
  resetTimelineForm()
  showTimelineDialog.value = true
}

function openEditTimelineEvent(event) {
  editingTimelineEvent.value = event
  timelineForm.value = { title: event.title, description: event.description || '' }
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
      const maxOrder = timelineEventsStore.timelineEvents.reduce((max, e) => Math.max(max, e.order), -1)
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
  () => timelineEventsStore.timelineEvents.length,
  (len) => {
    if (len > 0) nextTick(() => initSortable())
    else destroySortable()
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
  const labels = { characters: 'Character', places: 'Place', timeline: 'Timeline Event', groups: 'Group', items: 'Item', lore: 'Lore Entry' }
  return labels[deleteType.value] || 'Entry'
})

const deleteTargetName = computed(() => {
  if (!deleteTarget.value) return ''
  if (deleteType.value === 'timeline' || deleteType.value === 'lore') return deleteTarget.value.title
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
    } else if (deleteType.value === 'timeline') {
      await timelineEventsStore.deleteTimelineEvent(projectId, deleteTarget.value.id)
    } else if (deleteType.value === 'groups') {
      await groupsStore.deleteGroup(projectId, deleteTarget.value.id)
    } else if (deleteType.value === 'items') {
      await itemsStore.deleteItem(projectId, deleteTarget.value.id)
    } else if (deleteType.value === 'lore') {
      await loreStore.deleteLore(projectId, deleteTarget.value.id)
    }
    showDeleteDialog.value = false
  } catch {
    const store = deleteType.value === 'characters' ? charactersStore : deleteType.value === 'places' ? placesStore : deleteType.value === 'timeline' ? timelineEventsStore : deleteType.value === 'groups' ? groupsStore : deleteType.value === 'items' ? itemsStore : loreStore
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
