<template>
  <q-page class="write-page">
    <!-- Left: Scene Board -->
    <div v-if="!fullscreen" class="scene-board">
      <div class="scene-board-header">Scenes</div>

      <div style="padding: 12px 16px">
        <q-btn
          label="New Scene"
          color="primary"
          icon="add"
          unelevated
          no-caps
          class="full-width"
          size="sm"
          @click="handleCreateScene"
          style="font-family: var(--wda-font-ui)"
        />
      </div>

      <div
        v-if="scenesStore.loading"
        class="text-center q-mt-lg"
        style="color: var(--wda-text-muted)"
      >
        <q-spinner size="md" color="primary" />
      </div>

      <div
        v-else-if="scenesStore.scenes.length === 0"
        style="
          padding: 16px;
          text-align: center;
          color: var(--wda-text-muted);
          font-size: 0.85rem;
        "
      >
        No scenes yet. Create one to start writing.
      </div>

      <div v-else ref="sceneListContainer" style="overflow-y: auto; flex: 1">
        <div v-for="scene in scenesStore.scenes" :key="scene.id" :data-id="scene.id">
          <div
            class="scene-card"
            :class="{ active: scenesStore.activeSceneId === scene.id }"
            @click="scenesStore.setActiveScene(scene.id)"
          >
            <div style="display: flex; align-items: center; gap: 8px">
              <q-icon
                name="drag_indicator"
                class="drag-handle cursor-grab"
                size="sm"
                style="color: var(--wda-text-muted); flex-shrink: 0; touch-action: none"
              />
              <div style="flex: 1; min-width: 0">
                <div class="scene-card-order">#{{ scene.order + 1 }}</div>
                <div class="scene-card-title">{{ scene.title || 'Untitled Scene' }}</div>
              </div>
              <q-btn flat dense round icon="more_vert" size="sm" @click.stop>
                <q-menu anchor="bottom end" self="top end">
                  <q-list dense style="min-width: 120px">
                    <q-item clickable v-close-popup @click.stop="confirmDeleteScene(scene)">
                      <q-item-section class="text-negative">Delete</q-item-section>
                    </q-item>
                  </q-list>
                </q-menu>
              </q-btn>
            </div>
          </div>
        </div>
      </div>

      <div
        v-if="reordering"
        style="
          padding: 8px 16px;
          display: flex;
          align-items: center;
          gap: 8px;
          color: var(--wda-primary);
          font-size: 0.8rem;
        "
      >
        <q-spinner size="sm" />
        Saving order...
      </div>
      <div
        v-else-if="scenesStore.error && scenesStore.scenes.length > 0"
        style="padding: 8px 16px; font-size: 0.8rem; color: var(--wda-negative, #c75d3a)"
      >
        {{ scenesStore.error }}
      </div>
    </div>

    <!-- Right: Editor Area -->
    <div class="editor-area">
      <!-- Top bar with actions -->
      <div
        style="
          display: flex;
          align-items: center;
          justify-content: flex-end;
          padding: 8px 16px;
          border-bottom: 1px solid var(--wda-border);
        "
      >
        <div style="display: flex; align-items: center; gap: 4px">
          <q-btn flat dense round icon="history" size="sm" @click="openHistoryDrawer">
            <q-tooltip>Version History</q-tooltip>
          </q-btn>
          <q-btn flat dense round icon="auto_awesome" size="sm" @click="openAiDrawer">
            <q-tooltip>AI Assistant</q-tooltip>
          </q-btn>
          <q-btn flat dense round icon="local_offer" size="sm" @click="openTagsDrawer">
            <q-tooltip>Story Bible Tags</q-tooltip>
            <q-badge v-if="totalTagCount > 0" floating color="primary" style="font-size: 0.6rem; min-width: 14px; height: 14px; line-height: 14px; padding: 0 4px">
              {{ totalTagCount }}
            </q-badge>
          </q-btn>

          <q-btn
            flat
            dense
            round
            :icon="fullscreen ? 'fullscreen_exit' : 'fullscreen'"
            size="sm"
            @click="toggleFullscreen"
          >
            <q-tooltip>{{ fullscreen ? 'Exit Fullscreen' : 'Fullscreen' }}</q-tooltip>
          </q-btn>
        </div>
      </div>

      <template v-if="!activeScene">
        <div
          class="empty-state"
          style="
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
          "
        >
          <q-icon
            name="edit_note"
            size="64px"
            style="color: var(--wda-text-muted); opacity: 0.4"
          />
          <p class="empty-state-title">Select a scene to start writing</p>
          <p class="empty-state-desc" style="margin-bottom: 0">or create a new one.</p>
        </div>
      </template>

      <template v-else>
        <!-- Title + Save Status -->
        <div
          v-if="showToolbar"
          style="
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
            border-bottom: 1px solid var(--wda-border);
          "
        >
          <q-input
            v-model="titleDraft"
            label="Scene title"
            dense
            outlined
            class="col"
            style="font-family: var(--wda-font-heading)"
            @blur="saveTitle"
            @keyup.enter="saveTitle"
          />
        </div>

        <div style="border-bottom: 1px solid var(--wda-border)">
          <div
            class="row items-center q-px-md q-py-sm"
            style="color: var(--wda-text-muted); user-select: none; cursor: pointer"
            @click="showToolbar = !showToolbar"
          >
            <q-icon :name="showToolbar ? 'expand_less' : 'expand_more'" size="sm" />
            <span class="text-caption q-ml-xs">Formatting</span>
            <span v-if="!showToolbar && titleDraft" class="text-caption q-ml-sm" style="opacity:0.6; flex: 1">— {{ titleDraft }}</span>
            <span v-else style="flex: 1" />
            <div :class="'save-status ' + saveStatusClass" @click.stop>
              <q-spinner v-if="scenesStore.saveStatus === 'saving'" size="xs" class="q-mr-xs" />
              {{ saveStatusText }}
            </div>
          </div>
          <template v-if="showToolbar">
            <EditorToolbar
              :editor="editorRef"
              :word-count="liveWordCount"
              :show-find-replace="showFindReplace"
              :font-size="fontSize"
              :font-family="fontFamily"
              @font-family-change="handleFontFamilyChange"
              @font-size-change="handleFontSizeChange"
              @toggle-find-replace="showFindReplace = !showFindReplace"
            />
          </template>
        </div>

        <FindReplaceBar
          v-if="showFindReplace"
          :editor="editorRef"
          @close="showFindReplace = false"
        />

        <div style="position: relative; flex: 1; display: flex; flex-direction: column; min-height: 0">
          <div
            class="text-caption"
            style="position: absolute; top: 6px; right: 14px; color: var(--wda-text-muted); z-index: 1; font-size: 0.7rem"
          >
            {{ liveWordCount }} {{ liveWordCount === 1 ? 'word' : 'words' }}
          </div>
          <RichTextEditor
            ref="richEditorRef"
            v-model="sceneContent"
            :font-size="fontSize"
            :font-family="fontFamily"
            :autocomplete-suggestions="getSuggestions"
            placeholder="Begin writing your scene..."
            @word-count-update="liveWordCount = $event"
            @ready="editorRef = $event"
          />
        </div>

        <div v-if="!fullscreen" class="tags-bar">
          <div class="tags-bar-inner cursor-pointer" @click="openTagsDrawer">
            <q-icon name="local_offer" size="sm" />
            <span class="text-caption q-ml-xs">Story Bible — {{ tagsSummary }}</span>
            <q-icon name="chevron_right" size="sm" class="q-ml-xs" />
          </div>
        </div>
      </template>
    </div>

    <!-- Delete Confirmation Dialog -->
    <q-dialog v-model="showDeleteDialog">
      <q-card class="wda-card" style="min-width: 350px">
        <q-card-section>
          <div class="text-h6" style="font-family: var(--wda-font-heading)">Delete Scene</div>
        </q-card-section>
        <q-card-section>
          <p>
            Are you sure you want to delete '<strong>{{
              deleteTarget?.title || 'Untitled Scene'
            }}</strong
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

    <!-- Restore Confirmation Dialog -->
    <q-dialog v-model="showRestoreDialog">
      <q-card class="wda-card" style="min-width: 400px">
        <q-card-section>
          <div class="text-h6" style="font-family: var(--wda-font-heading)">
            Restore Version
          </div>
        </q-card-section>
        <q-card-section>
          <div class="text-body2 q-mb-md" v-if="restoreVersionTarget">
            <strong>Version from {{ relativeTime(restoreVersionTarget.created_at) }}</strong>
          </div>
          <div class="text-caption q-mb-md" v-if="restoreVersionTarget">
            &ldquo;{{ previewText(restoreVersionTarget.content) }}&rdquo;
          </div>
          <div class="text-negative text-body2 q-mb-md">
            Restoring this version will replace your current scene content. A snapshot of your
            current content will be saved automatically before the restore.
          </div>
          <q-input
            v-model="restorePassword"
            type="password"
            label="Enter your password to confirm"
            outlined
            color="primary"
            dense
            :error="!!sceneVersionsStore.restoreError"
            :error-message="sceneVersionsStore.restoreError || ''"
          />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancel" no-caps @click="closeRestoreDialog" />
          <q-btn
            unelevated
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

    <!-- Reorder Confirmation Dialog -->
    <q-dialog v-model="showReorderConfirm" @hide="onReorderDialogHide">
      <q-card class="wda-card" style="min-width: 350px">
        <q-card-section class="row items-center q-gutter-sm">
          <q-icon name="swap_vert" size="md" color="primary" />
          <div>
            <div class="text-h6" style="font-family: var(--wda-font-heading)">
              Reorder Scenes
            </div>
            <div class="text-body2 text-grey">
              Are you sure you want to change the scene order?
            </div>
          </div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancel" no-caps @click="cancelReorder" />
          <q-btn
            unelevated
            color="primary"
            label="Save Order"
            no-caps
            @click="confirmReorder"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Tags Panel -->
    <q-dialog v-model="tagsDrawerOpen" position="right" maximized>
      <q-card class="drawer-card" :style="{ width: '380px', maxWidth: '90vw' }" flat>
        <div class="q-pa-md" style="height: 100%; display: flex; flex-direction: column">
          <div class="row items-center justify-between q-mb-md">
            <div class="text-h6 ellipsis" style="font-family: var(--wda-font-heading)">
              Story Bible Tags
            </div>
            <q-btn flat dense round icon="close" size="sm" @click="closeTagsDrawer" />
          </div>

          <div class="scroll" style="flex: 1; overflow-y: auto">
            <div v-if="characterOptions.length > 0 || placeOptions.length > 0 || timelineEventOptions.length > 0 || groupOptions.length > 0 || itemOptions.length > 0 || loreOptions.length > 0">
              <q-select
                v-model="selectedCharacters"
                :options="characterOptions"
                label="Characters"
                multiple
                use-chips
                dense
                outlined
                color="primary"
                clearable
                class="q-mb-md"
                @update:model-value="saveTags"
              />

              <q-select
                v-model="selectedPlaces"
                :options="placeOptions"
                label="Places"
                multiple
                use-chips
                dense
                outlined
                color="primary"
                clearable
                class="q-mb-md"
                @update:model-value="saveTags"
              />

              <q-select
                v-model="selectedTimelineEvents"
                :options="timelineEventOptions"
                label="Timeline Events"
                multiple
                use-chips
                dense
                outlined
                color="primary"
                clearable
                class="q-mb-md"
                @update:model-value="saveTags"
              />

              <q-select
                v-model="selectedGroups"
                :options="groupOptions"
                label="Groups"
                multiple
                use-chips
                dense
                outlined
                color="primary"
                clearable
                class="q-mb-md"
                @update:model-value="saveTags"
              />

              <q-select
                v-model="selectedItems"
                :options="itemOptions"
                label="Items"
                multiple
                use-chips
                dense
                outlined
                color="primary"
                clearable
                class="q-mb-md"
                @update:model-value="saveTags"
              />

              <q-select
                v-model="selectedLore"
                :options="loreOptions"
                label="Lore"
                multiple
                use-chips
                dense
                outlined
                color="primary"
                clearable
                @update:model-value="saveTags"
              />
            </div>
            <div v-else class="text-center q-mt-xl" style="color: var(--wda-text-muted)">
              <q-icon name="local_offer" size="48px" class="q-mb-sm" style="opacity: 0.4" />
              <p>Add entries to your Story Bible to tag them here</p>
              <router-link :to="`/projects/${projectId}/story-bible`" style="color: var(--wda-primary)">
                Go to Story Bible
              </router-link>
            </div>
          </div>
        </div>
      </q-card>
    </q-dialog>

    <!-- Right Panel: Version History / AI Assistant (replaces q-drawer) -->
    <q-dialog v-model="drawerOpen" position="right" maximized>
      <q-card class="drawer-card" :style="{ width: drawerWidth + 'px', maxWidth: '90vw' }" flat>
        <div class="q-pa-md" style="height: 100%; display: flex; flex-direction: column">
          <template v-if="drawerMode === 'history'">
            <div class="row items-center justify-between q-mb-md">
              <div class="text-h6 ellipsis" style="font-family: var(--wda-font-heading)">
                Version History &mdash; {{ activeScene?.title || 'Untitled Scene' }}
              </div>
              <q-btn flat dense round icon="close" size="sm" @click="closeDrawer" />
            </div>

            <div
              v-if="sceneVersionsStore.loading && sceneVersionsStore.versions.length === 0"
              class="text-center q-mt-lg"
              style="color: var(--wda-text-muted)"
            >
              <q-spinner size="md" color="primary" />
            </div>

            <div
              v-else-if="sceneVersionsStore.versions.length === 0"
              class="text-center q-mt-lg"
              style="color: var(--wda-text-muted)"
            >
              No versions yet.
            </div>

            <div v-else class="scroll" style="flex: 1; overflow-y: auto">
              <div v-for="version in sceneVersionsStore.versions" :key="version.id" class="q-mb-sm">
                <div class="wda-card" style="padding: 12px 16px">
                  <div class="row items-center justify-between no-wrap">
                    <div class="text-caption" style="color: var(--wda-text-muted)">
                      {{ relativeTime(version.created_at) }}
                    </div>
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
                  <div class="text-body2 q-mt-xs ellipsis-2-lines" style="color: var(--wda-text-muted)">
                    {{ previewText(version.content) }}
                  </div>
                </div>
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
          </template>

          <template v-else-if="drawerMode === 'ai'">
            <div class="row items-center justify-between q-mb-md">
              <div class="text-h6 ellipsis" style="font-family: var(--wda-font-heading)">
                AI Assistant &mdash; {{ activeScene?.title || 'Untitled Scene' }}
              </div>
              <div>
                <q-btn flat dense round :icon="drawerExpanded ? 'chevron_right' : 'chevron_left'" size="sm" @click="toggleDrawerExpand">
                  <q-tooltip>{{ drawerExpanded ? 'Collapse' : 'Expand' }}</q-tooltip>
                </q-btn>
                <q-btn flat dense round icon="close" size="sm" @click="closeDrawer" />
              </div>
            </div>

            <q-banner
              v-if="showFreeTierWarning"
              class="bg-warning text-warning q-mb-sm rounded-borders"
            >
              <template #avatar>
                <q-icon name="warning" color="warning" />
              </template>
              This AI assistant is running on a free-tier key. Your prompts may be used by Google to
              improve their models.
              <template #action>
                <q-btn
                  flat
                  color="warning"
                  label="Go to Settings"
                  no-caps
                  to="/settings"
                  @click="closeDrawer"
                />
                <q-btn
                  flat
                  color="warning"
                  label="I understand"
                  no-caps
                  @click="dismissFreeTierWarning"
                />
              </template>
            </q-banner>

            <q-banner
              v-if="activeScene && !hasStoryBibleTags"
              class="bg-info text-white q-mb-sm rounded-borders"
            >
              <div class="row items-center no-wrap">
                <q-icon name="lightbulb" color="white" size="sm" class="q-mr-sm" />
                <span>Tag Story Bible entries to this scene for more grounded AI feedback.</span>
              </div>
              <template #action>
                <q-btn
                  flat
                  color="white"
                  label="Story Bible"
                  no-caps
                  :to="`/projects/${projectId}/story-bible`"
                  @click="closeDrawer"
                />
              </template>
            </q-banner>

            <template v-if="showNoKeyState">
              <div class="text-center q-mt-lg text-negative">
                <q-icon name="error_outline" size="48px" />
                <div class="text-body1 q-mt-sm">{{ conversationsStore.error }}</div>
                <q-btn
                  flat
                  color="primary"
                  label="Go to Settings"
                  no-caps
                  to="/settings"
                  class="q-mt-sm"
                  @click="closeDrawer"
                />
              </div>
            </template>

            <q-banner
              v-else-if="conversationsStore.error && !showNoKeyState"
              class="bg-negative text-white q-mb-sm rounded-borders"
            >
              <template #avatar>
                <q-icon name="error_outline" color="white" />
              </template>
              {{ conversationsStore.error }}
            </q-banner>

            <template v-else>
              <div ref="messageListRef" class="scroll q-mb-sm" style="flex: 1; overflow-y: auto">
                <div
                  v-for="msg in conversationsStore.messages"
                  :key="msg.id"
                  class="q-mb-sm"
                >
                  <template v-if="msg.metadata?.type === 'contradiction_check'">
                    <div class="contradiction-card" style="max-width: 85%">
                      <div class="contradiction-header row items-center q-gutter-xs q-pa-sm">
                        <q-icon name="warning" size="sm" color="warning" />
                        <span class="text-weight-bold">Contradiction Check</span>
                        <span class="text-caption text-grey">{{ relativeTime(msg.created_at) }}</span>
                      </div>
                      <q-separator />
                      <div v-if="msg.metadata.has_contradictions" class="q-pa-sm">
                        <div class="text-negative text-weight-bold q-mb-sm">{{ msg.metadata.count }} issue(s) found</div>
                        <div v-for="(item, i) in msg.metadata.items" :key="i" class="q-mb-md">
                          <div class="row items-center q-gutter-xs q-mb-xs">
                            <q-badge :color="severityColor(item.severity)" class="text-uppercase">{{ item.severity }}</q-badge>
                            <span class="text-caption text-grey">{{ item.category }}</span>
                          </div>
                          <div class="text-body2 text-weight-bold q-mb-xs">{{ item.issue }}</div>
                          <div class="text-caption q-mb-xs">
                            <span class="text-grey">Story Bible says:</span>
                            <em>"{{ item.story_bible_says }}"</em>
                          </div>
                          <div class="text-caption q-mb-xs">
                            <span class="text-grey">Scene says:</span>
                            <em>"{{ item.scene_says }}"</em>
                          </div>
                          <q-separator v-if="i < msg.metadata.items.length - 1" class="q-my-sm" />
                        </div>
                      </div>
                      <div v-else class="q-pa-sm">
                        <q-badge color="positive">All clear</q-badge>
                        <span class="text-body2 q-ml-sm">No contradictions found. This scene is consistent with your Story Bible.</span>
                      </div>
                      <q-separator />
                      <div class="text-right q-pa-xs">
                        <q-btn flat dense no-caps color="primary" label="Run again →" size="sm" @click="handleCheckContradictions" />
                      </div>
                    </div>
                  </template>
                  <template v-else>
                    <div :class="msg.role === 'user' ? 'flex justify-end' : ''">
                      <q-card
                        flat
                        bordered
                        :class="msg.role === 'user' ? 'bg-primary text-white' : ''"
                        style="max-width: 85%; display: inline-block"
                      >
                        <q-card-section class="q-py-sm q-px-md">
                          <div class="text-body2 chat-message-content" v-html="renderMarkdown(msg.content)"></div>
                          <div
                            class="text-caption q-mt-xs"
                            :class="msg.role === 'user' ? 'text-white text-opacity-70' : 'text-grey'"
                          >
                            {{ relativeTime(msg.created_at) }}
                          </div>
                        </q-card-section>
                      </q-card>
                    </div>
                  </template>
                </div>

                <div v-if="conversationsStore.sending" class="flex justify-start q-mb-sm">
                  <q-card flat bordered style="max-width: 85%; display: inline-block">
                    <q-card-section class="q-py-sm q-px-md">
                      <q-spinner-dots size="sm" />
                      <span class="text-grey q-ml-sm">Thinking...</span>
                    </q-card-section>
                  </q-card>
                </div>

                <div v-if="conversationsStore.checkingContradictions" class="flex justify-start q-mb-sm">
                  <q-card flat bordered style="max-width: 85%; display: inline-block">
                    <q-card-section class="q-py-sm q-px-md">
                      <q-spinner-dots size="sm" />
                      <span class="text-grey q-ml-sm">Scanning your scene for contradictions...</span>
                    </q-card-section>
                  </q-card>
                </div>
              </div>

              <q-btn
                flat
                color="warning"
                icon="warning"
                label="Check for Contradictions"
                no-caps
                size="sm"
                class="full-width q-mb-sm"
                :disable="!activeScene || conversationsStore.sending || conversationsStore.checkingContradictions"
                :loading="conversationsStore.checkingContradictions"
                @click="handleCheckContradictions"
              />

              <div class="row items-end q-gutter-sm">
                <q-input
                  v-model="messageDraft"
                  type="textarea"
                  autogrow
                  placeholder="Ask the AI assistant..."
                  outlined
                  color="primary"
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
          </template>
        </div>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted, watch, onBeforeUnmount, nextTick, shallowRef, inject } from 'vue'
import { useRoute } from 'vue-router'
import { useScenesStore } from '@/stores/scenes'
import { useSceneVersionsStore } from '@/stores/sceneVersions'
import { useConversationsStore } from '@/stores/conversations'
import EditorToolbar from '@/components/EditorToolbar.vue'
import FindReplaceBar from '@/components/FindReplaceBar.vue'
import RichTextEditor from '@/components/RichTextEditor.vue'
import { useCharactersStore } from '@/stores/characters'
import { usePlacesStore } from '@/stores/places'
import { useTimelineEventsStore } from '@/stores/timelineEvents'
import { useGroupsStore } from '@/stores/groups'
import { useItemsStore } from '@/stores/items'
import { useLoreStore } from '@/stores/lore'
import Sortable from 'sortablejs'
import { renderMarkdown } from '@/utils/markdown'

const route = useRoute()
const projectId = route.params.id

const scenesStore = useScenesStore()
const sceneVersionsStore = useSceneVersionsStore()
const conversationsStore = useConversationsStore()
const charactersStore = useCharactersStore()
const placesStore = usePlacesStore()
const timelineEventsStore = useTimelineEventsStore()
const groupsStore = useGroupsStore()
const itemsStore = useItemsStore()
const loreStore = useLoreStore()

// ---- Editor state ----
const fullscreen = ref(false)
const layoutFullscreen = inject('layoutFullscreen', ref(false))
const fontSize = ref(localStorage.getItem('wda_font_size') || '1.1rem')
const fontFamily = ref(localStorage.getItem('wda_font_family') || 'serif')
const showToolbar = ref(true)
const showFindReplace = ref(false)
const liveWordCount = ref(0)
const editorRef = shallowRef(null)
const richEditorRef = ref(null)

watch(fontSize, (val) => {
  localStorage.setItem('wda_font_size', val)
})

watch(fontFamily, (val) => {
  localStorage.setItem('wda_font_family', val)
})

function handleFontFamilyChange(val) {
  fontFamily.value = val
}

function handleFontSizeChange(val) {
  fontSize.value = val
}

function toggleFullscreen() {
  fullscreen.value = !fullscreen.value
  layoutFullscreen.value = fullscreen.value
}

function onKeydown(e) {
  if (e.key === 'Escape') {
    if (showFindReplace.value) {
      showFindReplace.value = false
      return
    }
    if (fullscreen.value) {
      fullscreen.value = false
      layoutFullscreen.value = false
    }
  }
  if ((e.key === 'f' || e.key === 'F') && (e.ctrlKey || e.metaKey)) {
    e.preventDefault()
    showFindReplace.value = true
  }
}

const activeScene = computed(() => {
  if (scenesStore.activeSceneId === null) return null
  return scenesStore.scenes.find((s) => s.id === scenesStore.activeSceneId) || null
})

const hasStoryBibleTags = computed(() => {
  if (!activeScene.value) return false
  const s = activeScene.value
  return (
    (s.characters && s.characters.length > 0) ||
    (s.places && s.places.length > 0) ||
    (s.timeline_events && s.timeline_events.length > 0) ||
    (s.groups && s.groups.length > 0) ||
    (s.items && s.items.length > 0) ||
    (s.lore && s.lore.length > 0)
  )
})

const totalTagCount = computed(() => {
  if (!activeScene.value) return 0
  const s = activeScene.value
  return (
    (s.characters || []).length +
    (s.places || []).length +
    (s.timeline_events || []).length +
    (s.groups || []).length +
    (s.items || []).length +
    (s.lore || []).length
  )
})

const showNoKeyState = computed(() => {
  return (
    conversationsStore.error &&
    !conversationsStore.sending &&
    conversationsStore.messages.length === 0 &&
    conversationsStore.error.includes('not configured')
  )
})

// Save status helpers
const saveStatusClass = computed(() => {
  return scenesStore.saveStatus
})

const saveStatusText = computed(() => {
  switch (scenesStore.saveStatus) {
    case 'saving':
      return 'Saving...'
    case 'saved':
      return 'Saved'
    case 'error':
      return 'Error saving'
    default:
      return 'Ready'
  }
})

// ---- Data fetching ----
onMounted(async () => {
  await Promise.all([
    scenesStore.fetchScenes(projectId),
    charactersStore.fetchCharacters(projectId),
    placesStore.fetchPlaces(projectId),
    timelineEventsStore.fetchTimelineEvents(projectId),
    groupsStore.fetchGroups(projectId),
    itemsStore.fetchItems(projectId),
    loreStore.fetchLore(projectId),
  ])
  document.addEventListener('keydown', onKeydown)
})

// ---- Scene list drag reorder (SortableJS) ----
const sceneListContainer = ref(null)
const reordering = ref(false)
let sortableInstance = null
const showReorderConfirm = ref(false)
const pendingReorderIds = ref([])
let originalOrder = []

function initSortable() {
  if (!sceneListContainer.value) return
  destroySortable()
  sortableInstance = new Sortable(sceneListContainer.value, {
    animation: 200,
    handle: '.drag-handle',
    dataIdAttr: 'data-id',
    onStart: () => {
      originalOrder = scenesStore.scenes.map((s) => s.id)
    },
    onEnd: () => {
      pendingReorderIds.value = sortableInstance.toArray().map(Number)
      showReorderConfirm.value = true
    },
  })
}

function confirmReorder() {
  showReorderConfirm.value = false
  reordering.value = true
  const orderedIds = pendingReorderIds.value
  pendingReorderIds.value = []
  ;(async () => {
    try {
      await scenesStore.reorderScenes(projectId, orderedIds)
    } catch {
      // Store already refetched
    } finally {
      reordering.value = false
      nextTick(() => initSortable())
    }
  })()
}

function cancelReorder() {
  showReorderConfirm.value = false
  pendingReorderIds.value = []
  if (sortableInstance) {
    sortableInstance.sort(originalOrder.map(String))
  }
  originalOrder = []
}

function onReorderDialogHide() {
  if (pendingReorderIds.value.length > 0) {
    cancelReorder()
  }
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
  layoutFullscreen.value = false
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

watch(
  activeScene,
  (scene) => {
    if (scene) {
      titleDraft.value = scene.title
    } else {
      titleDraft.value = ''
    }
  },
  { immediate: true },
)

function saveTitle() {
  if (!activeScene.value) return
  const newTitle = titleDraft.value.trim()
  if (newTitle !== activeScene.value.title) {
    scenesStore.updateSceneMeta(projectId, activeScene.value.id, { title: newTitle })
  }
}

// ---- Content editing with debounced autosave ----
const sceneContent = ref('')
let saveTimer = null
let autoTagTimer = null
let isExternalUpdate = false

watch(
  activeScene,
  (scene) => {
    if (saveTimer) {
      clearTimeout(saveTimer)
      saveTimer = null
    }
    if (scene) {
      isExternalUpdate = true
      sceneContent.value = scene.content
      nextTick(() => {
        isExternalUpdate = false
      })
      liveWordCount.value = 0
    } else {
      sceneContent.value = ''
    }
  },
  { immediate: true },
)

watch(sceneContent, (newVal) => {
  if (isExternalUpdate) return
  if (saveTimer) clearTimeout(saveTimer)
  saveTimer = setTimeout(() => {
    if (activeScene.value && newVal !== activeScene.value.content) {
      scenesStore.updateSceneContent(projectId, activeScene.value.id, newVal)
    }
  }, 2500)
  if (autoTagTimer) clearTimeout(autoTagTimer)
  autoTagTimer = setTimeout(() => {
    autoTagScene(newVal)
  }, 3000)
})

onBeforeUnmount(() => {
  if (saveTimer) clearTimeout(saveTimer)
  if (autoTagTimer) clearTimeout(autoTagTimer)
})

function autoTagScene(content) {
  if (!activeScene.value || !content) return
  const text = content.replace(htmlTagRegex, '').toLowerCase()
  if (!text.trim()) return
  let changed = false
  for (const char of charactersStore.characters) {
    if (char.name.length < 3) continue
    if (selectedCharacters.value.some((s) => s.value === char.id)) continue
    if (text.includes(char.name.toLowerCase())) {
      selectedCharacters.value.push({ label: char.name, value: char.id })
      changed = true
    }
  }
  for (const place of placesStore.places) {
    if (place.name.length < 3) continue
    if (selectedPlaces.value.some((s) => s.value === place.id)) continue
    if (text.includes(place.name.toLowerCase())) {
      selectedPlaces.value.push({ label: place.name, value: place.id })
      changed = true
    }
  }
  for (const event of timelineEventsStore.timelineEvents) {
    if (event.title.length < 3) continue
    if (selectedTimelineEvents.value.some((s) => s.value === event.id)) continue
    if (text.includes(event.title.toLowerCase())) {
      selectedTimelineEvents.value.push({ label: event.title, value: event.id })
      changed = true
    }
  }
  for (const group of groupsStore.groups) {
    if (group.name.length < 3) continue
    if (selectedGroups.value.some((s) => s.value === group.id)) continue
    if (text.includes(group.name.toLowerCase())) {
      selectedGroups.value.push({ label: group.name, value: group.id })
      changed = true
    }
  }
  for (const item of itemsStore.items) {
    if (item.name.length < 3) continue
    if (selectedItems.value.some((s) => s.value === item.id)) continue
    if (text.includes(item.name.toLowerCase())) {
      selectedItems.value.push({ label: item.name, value: item.id })
      changed = true
    }
  }
  for (const l of loreStore.lore) {
    if (l.title.length < 3) continue
    if (selectedLore.value.some((s) => s.value === l.id)) continue
    if (text.includes(l.title.toLowerCase())) {
      selectedLore.value.push({ label: l.title, value: l.id })
      changed = true
    }
  }
  if (changed) saveTags()
}

// ---- Story Bible tagging ----
const selectedCharacters = ref([])
const selectedPlaces = ref([])
const selectedTimelineEvents = ref([])
const selectedGroups = ref([])
const selectedItems = ref([])
const selectedLore = ref([])

const tagsDrawerOpen = ref(false)

function openTagsDrawer() {
  tagsDrawerOpen.value = true
}

function closeTagsDrawer() {
  tagsDrawerOpen.value = false
}

const tagsSummary = computed(() => {
  const parts = []
  if (selectedCharacters.value.length)
    parts.push(
      `${selectedCharacters.value.length} character${selectedCharacters.value.length > 1 ? 's' : ''}`,
    )
  if (selectedPlaces.value.length)
    parts.push(`${selectedPlaces.value.length} place${selectedPlaces.value.length > 1 ? 's' : ''}`)
  if (selectedTimelineEvents.value.length)
    parts.push(
      `${selectedTimelineEvents.value.length} timeline event${selectedTimelineEvents.value.length > 1 ? 's' : ''}`,
    )
  if (selectedGroups.value.length)
    parts.push(`${selectedGroups.value.length} group${selectedGroups.value.length > 1 ? 's' : ''}`)
  if (selectedItems.value.length)
    parts.push(`${selectedItems.value.length} item${selectedItems.value.length > 1 ? 's' : ''}`)
  if (selectedLore.value.length)
    parts.push(`${selectedLore.value.length} lore entry${selectedLore.value.length > 1 ? 's' : ''}`)
  if (!parts.length) return 'No tags'
  return parts.join(', ')
})

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

const groupOptions = computed(() => {
  return groupsStore.groups.map((g) => ({
    label: g.name,
    value: g.id,
  }))
})

const itemOptions = computed(() => {
  return itemsStore.items.map((i) => ({
    label: i.name,
    value: i.id,
  }))
})

const loreOptions = computed(() => {
  return loreStore.lore.map((l) => ({
    label: l.title,
    value: l.id,
  }))
})

watch(
  activeScene,
  (scene) => {
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
      selectedGroups.value = (scene.groups || []).map((id) => {
        const g = groupsStore.groups.find((gr) => gr.id === id)
        return g ? { label: g.name, value: g.id } : { label: `#${id}`, value: id }
      })
      selectedItems.value = (scene.items || []).map((id) => {
        const i = itemsStore.items.find((it) => it.id === id)
        return i ? { label: i.name, value: i.id } : { label: `#${id}`, value: id }
      })
      selectedLore.value = (scene.lore || []).map((id) => {
        const l = loreStore.lore.find((lo) => lo.id === id)
        return l ? { label: l.title, value: l.id } : { label: `#${id}`, value: id }
      })
    } else {
      selectedCharacters.value = []
      selectedPlaces.value = []
      selectedTimelineEvents.value = []
      selectedGroups.value = []
      selectedItems.value = []
      selectedLore.value = []
    }
  },
  { immediate: true },
)

function saveTags() {
  if (!activeScene.value) return
  scenesStore.updateSceneMeta(projectId, activeScene.value.id, {
    characters: selectedCharacters.value.map((o) => o.value),
    places: selectedPlaces.value.map((o) => o.value),
    timeline_events: selectedTimelineEvents.value.map((o) => o.value),
    groups: selectedGroups.value.map((o) => o.value),
    items: selectedItems.value.map((o) => o.value),
    lore: selectedLore.value.map((o) => o.value),
  })
}

// ---- Version History ----
const showRestoreDialog = ref(false)
const restoreVersionTarget = ref(null)
const restorePassword = ref('')

function openHistoryDrawer() {
  drawerMode.value = 'history'
  drawerOpen.value = true
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
    drawerOpen.value = false
  }
}

const htmlTagRegex = /<[^>]*>/g
function previewText(content, maxLength = 100) {
  const text = content ? content.replace(htmlTagRegex, '') : ''
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}

// ---- Right Panel (AI Assistant / Version History) ----
const drawerOpen = ref(false)
const drawerMode = ref(null) // 'ai' | 'history' | null
const messageDraft = ref('')
const messageListRef = ref(null)
const showFreeTierWarning = ref(false)
const drawerExpanded = ref(false)

const drawerWidth = computed(() => {
  if (drawerMode.value === 'history') return 380
  if (drawerExpanded.value) return Math.floor(window.innerWidth * 0.5)
  return 400
})

function openAiDrawer() {
  drawerMode.value = 'ai'
  drawerOpen.value = true
  if (activeScene.value) {
    initAiConversation(activeScene.value)
  }
}

function toggleDrawerExpand() {
  drawerExpanded.value = !drawerExpanded.value
}

function closeDrawer() {
  drawerOpen.value = false
  drawerExpanded.value = false
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

async function handleCheckContradictions() {
  if (!activeScene.value || conversationsStore.sending || conversationsStore.checkingContradictions) return
  await conversationsStore.checkContradictions(projectId, activeScene.value.id)
  if (!conversationsStore.error) {
    await nextTick()
    scrollToBottom()
  }
}

function severityColor(severity) {
  if (severity === 'HIGH') return 'negative'
  if (severity === 'MEDIUM') return 'warning'
  return 'grey'
}

function scrollToBottom() {
  if (messageListRef.value) {
    messageListRef.value.scrollTop = messageListRef.value.scrollHeight
  }
}

watch(
  () => conversationsStore.messages.length,
  () => nextTick(() => scrollToBottom()),
)

watch(activeScene, (scene, oldScene) => {
  if (scene && drawerOpen.value && drawerMode.value === 'ai' && scene.id !== oldScene?.id) {
    conversationsStore.reset()
    initAiConversation(scene)
  }
})

const getSuggestions = () => [
  ...charactersStore.characters.map(c => c.name),
  ...placesStore.places.map(p => p.name),
  ...timelineEventsStore.timelineEvents.map(e => e.title),
  ...groupsStore.groups.map(g => g.name),
  ...itemsStore.items.map(i => i.name),
  ...loreStore.lore.map(l => l.title),
].filter(Boolean)

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
.drag-handle {
  touch-action: none;
}

.tags-bar {
  border-top: 1px solid var(--wda-border);
}

.tags-bar-inner {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  color: var(--wda-text-muted);
  user-select: none;
  transition: background 0.15s;
}

.tags-bar-inner:hover {
  background: var(--wda-surface-2);
}

.contradiction-card {
  background: var(--wda-surface);
  border: 1px solid var(--wda-border);
  border-radius: var(--wda-radius);
  box-shadow: var(--wda-shadow);
  display: inline-block;
  width: 100%;
}

.contradiction-header {
  border-radius: var(--wda-radius) var(--wda-radius) 0 0;
}

.drawer-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  border-radius: 0;
  background: var(--wda-surface);
  border: none;
  border-left: 1px solid var(--wda-border);
}

.scene-board {
  background: var(--wda-surface-2);
}

.body--dark .scene-board {
  background: var(--wda-bg);
}

.scene-card {
  transition: background .2s ease, border-color .2s ease;
}

.scene-card.active {
  border-left-color: var(--wda-primary);
}
</style>
