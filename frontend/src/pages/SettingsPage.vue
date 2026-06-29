<template>
  <q-page class="settings-page">
    <div class="settings-header">
      <div>
        <div class="wda-page-title">Settings</div>
        <div class="settings-subtitle">Configure your writing experience</div>
      </div>
    </div>

    <div class="settings-card">
      <div class="settings-card-left">
        <div class="card-title q-mb-sm">AI Assistant Settings</div>
        <!-- <div class="text-description q-mb-md">
          By default, Writer's Draft App uses a shared free-tier Gemini API key. You can provide
          your own key for higher limits or data privacy.
        </div> -->

        <div class="settings-ai-content">
          <div class="wda-info-card q-mb-md">
            <div class="info-card-header">
              <q-icon name="key" size="sm" class="q-mr-xs" style="color: var(--wda-action)" />
              <span>Need an API key?</span>
            </div>
            <div class="info-card-body">
              Create a free Gemini API key at Google AI Studio to use your own account for higher limits and data privacy.
            </div>
            <q-btn
              type="a"
              href="https://aistudio.google.com/app/apikey"
              target="_blank"
              rel="noopener noreferrer"
              flat
              dense
              no-caps
              size="sm"
              icon="open_in_new"
              label="Get API Key"
              style="color: var(--wda-action); padding: 0; margin-top: 8px"
            />
          </div>

          <template v-if="keyUiState === 'empty'">
            <q-input
              v-model="keyInputValue"
              :type="showKey ? 'text' : 'password'"
              label="Your Gemini API Key"
              placeholder="Enter your Gemini API key"
              outlined
              color="primary"
              dense
              class="q-mb-md"
              :error="!!keyError"
              :error-message="keyError"
            >
              <template #append>
                <q-btn
                  flat
                  dense
                  round
                  :icon="showKey ? 'visibility_off' : 'visibility'"
                  @click="showKey = !showKey"
                />
              </template>
            </q-input>

            <q-checkbox
              v-model="isPaidTier"
              label="I'm using a paid-tier key (my data won't be used for model training)."
              class="q-mb-md"
            />

            <div class="row q-gutter-sm items-center">
              <q-btn
                unelevated
                color="primary"
                label="Save Key"
                no-caps
                :disable="!keyInputValue.trim()"
                :loading="keySaving"
                @click="saveKey"
              />
              <q-btn
                flat
                dense
                size="sm"
                label="Re-test connection"
                no-caps
                @click="runConnectionTest"
              />
            </div>
          </template>

          <template v-else-if="keyUiState === 'locked'">
            <q-input
              :model-value="maskedPreview"
              label="Your Gemini API Key"
              outlined
              color="primary"
              dense
              disable
              class="q-mb-md"
            >
              <template #append>
                <q-icon name="lock" color="primary" size="sm" class="q-mr-xs" />
                <q-btn
                  flat
                  dense
                  round
                  :icon="showKey ? 'visibility_off' : 'visibility'"
                  @click="showKey = !showKey"
                />
              </template>
            </q-input>

            <q-checkbox
              v-model="isPaidTier"
              label="I'm using a paid-tier key (my data won't be used for model training)."
              class="q-mb-md"
            />
            <q-btn
              v-if="paidTierDirty"
              flat
              dense
              size="sm"
              color="primary"
              label="Save"
              no-caps
              :loading="keySaving"
              @click="savePaidTier"
              class="q-mb-md"
            />

            <div class="row q-gutter-sm q-mb-md">
              <q-btn color="primary" label="Change Key" no-caps outline @click="startEditing" />
              <q-btn
                flat
                color="negative"
                label="Remove Key"
                no-caps
                @click="showRemoveDialog = true"
              />
              <q-btn
                flat
                dense
                size="sm"
                label="Re-test connection"
                no-caps
                @click="runConnectionTest"
              />
            </div>
          </template>

          <template v-else-if="keyUiState === 'editing'">
            <q-input
              v-model="keyInputValue"
              :type="showKey ? 'text' : 'password'"
              label="Your Gemini API Key"
              placeholder="Enter new Gemini API key"
              outlined
              color="primary"
              dense
              class="q-mb-md"
              :error="!!keyError"
              :error-message="keyError"
            >
              <template #append>
                <q-icon name="lock_open" color="orange" size="sm" class="q-mr-xs" />
                <q-btn
                  flat
                  dense
                  round
                  :icon="showKey ? 'visibility_off' : 'visibility'"
                  @click="showKey = !showKey"
                />
              </template>
            </q-input>

            <q-checkbox
              v-model="isPaidTier"
              label="I'm using a paid-tier key (my data won't be used for model training)."
              class="q-mb-md"
            />

            <div class="row q-gutter-sm items-center">
              <q-btn
                unelevated
                color="primary"
                label="Save Key"
                no-caps
                :disable="!keyInputValue.trim()"
                :loading="keySaving"
                @click="saveKey"
              />
              <q-btn flat label="Cancel" no-caps @click="cancelEditing" />
              <q-btn
                flat
                dense
                size="sm"
                label="Re-test connection"
                no-caps
                @click="runConnectionTest"
              />
            </div>
          </template>

          <q-banner
            v-if="connectionStatus"
            :class="connectionBannerClass"
            class="q-mt-md rounded-borders"
          >
            <template #avatar>
              <q-spinner v-if="connectionStatus.status === 'testing'" size="sm" />
              <q-icon v-else :name="connectionIcon" :color="connectionColor" />
            </template>
            <div class="text-body2">{{ connectionTitle }}</div>
            <div class="text-caption">{{ connectionSubtitle }}</div>
          </q-banner>
        </div>
      </div>

      <div class="settings-card-divider" />

      <div class="settings-card-right">
        <div class="card-title q-mb-sm">Writing Goal</div>
        <div class="text-description q-mb-md">
          Set a daily word count target to keep yourself motivated.
        </div>

        <q-toggle
          v-model="showWordGoal"
          label="Show daily word count goal"
          class="q-mb-md"
          color="primary"
        />

        <q-input
          v-if="showWordGoal"
          v-model.number="dailyWordGoal"
          type="number"
          label="Daily word goal"
          placeholder="e.g. 1000"
          outlined
          color="primary"
          dense
          :min="1"
          :max="10000"
          class="q-mb-md"
        />

        <div style="color: var(--wda-text-muted); font-size: 0.85rem; margin-bottom: 16px">
          <template v-if="!showWordGoal"> Goal tracking is off. </template>
          <template v-else>
            Goal: {{ formatNumber(dailyWordGoal || 1000) }} words/day &mdash; currently showing
            on Statistics page.
          </template>
        </div>

        <div v-if="goalError" class="text-negative q-mb-md">{{ goalError }}</div>
        <div v-if="goalSuccess" class="text-positive q-mb-md">{{ goalSuccess }}</div>

        <q-btn
          unelevated
          color="primary"
          label="Save"
          no-caps
          :loading="goalSaving"
          @click="saveGoal"
        />
      </div>
    </div>

    <q-dialog v-model="showRemoveDialog">
      <q-card class="wda-card" style="min-width: 400px">
        <q-card-section>
          <div class="text-h6" style="font-family: var(--wda-font-heading)">
            Remove API Key
          </div>
        </q-card-section>
        <q-card-section>
          <p>
            Remove your custom API key? The app will revert to using the shared default
            free-tier key.
          </p>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup no-caps />
          <q-btn
            unelevated
            color="negative"
            label="Remove"
            no-caps
            :loading="keySaving"
            @click="confirmRemoveKey"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const keyInputValue = ref('')
const showKey = ref(false)
const keySaving = ref(false)
const keyError = ref('')
const isPaidTier = ref(false)
const isEditing = ref(false)
const showRemoveDialog = ref(false)

const goalSaving = ref(false)
const showWordGoal = ref(false)
const dailyWordGoal = ref(null)
const goalError = ref('')
const goalSuccess = ref('')

const connectionStatus = ref(null)

const keyUiState = computed(() => {
  if (isEditing.value) return 'editing'
  if (authStore.hasGeminiKey) return 'locked'
  return 'empty'
})

const maskedPreview = computed(() => {
  const preview = authStore.geminiApiKeyPreview
  return preview
    ? '\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022' + preview
    : ''
})

const paidTierDirty = computed(() => {
  return isPaidTier.value !== authStore.isPaidTier
})

function formatNumber(n) {
  if (n == null) return '0'
  return n.toLocaleString()
}

const connectionBannerClass = computed(() => {
  if (!connectionStatus.value) return ''
  switch (connectionStatus.value.status) {
    case 'testing':
      return 'bg-grey-2 text-grey-8'
    case 'ok':
      return 'bg-positive text-white'
    case 'quota_exceeded':
      return 'bg-warning text-warning'
    case 'invalid_key':
      return 'bg-negative text-white'
    case 'not_configured':
      return 'bg-grey-3 text-grey-8'
    default:
      return 'bg-grey-2 text-grey-8'
  }
})

const connectionIcon = computed(() => {
  if (!connectionStatus.value) return ''
  switch (connectionStatus.value.status) {
    case 'ok':
      return 'check_circle'
    case 'quota_exceeded':
      return 'warning'
    case 'invalid_key':
      return 'cancel'
    case 'not_configured':
      return 'info'
    default:
      return ''
  }
})

const connectionColor = computed(() => {
  if (!connectionStatus.value) return ''
  switch (connectionStatus.value.status) {
    case 'ok':
      return 'white'
    case 'quota_exceeded':
      return 'warning'
    case 'invalid_key':
      return 'white'
    case 'not_configured':
      return 'grey-8'
    default:
      return ''
  }
})

const connectionTitle = computed(() => {
  if (!connectionStatus.value) return ''
  switch (connectionStatus.value.status) {
    case 'testing':
      return 'Testing connection...'
    case 'ok':
      return 'Connected'
    case 'quota_exceeded':
      return 'Quota exceeded'
    case 'invalid_key':
      return 'Invalid key'
    case 'not_configured':
      return 'Not configured'
    default:
      return ''
  }
})

const connectionSubtitle = computed(() => {
  if (!connectionStatus.value) return ''
  switch (connectionStatus.value.status) {
    case 'testing':
      return ''
    case 'ok':
      return connectionStatus.value.using === 'custom'
        ? 'Using your custom key.'
        : 'Using shared default key.'
    case 'quota_exceeded':
      return 'Your key has hit its daily limit. Try again tomorrow or enable billing.'
    case 'invalid_key':
      return 'This key is not valid. Check it and try again.'
    case 'not_configured':
      return 'No API key available. Add a key above or contact the app administrator.'
    default:
      return ''
  }
})

onMounted(() => {
  isPaidTier.value = authStore.isPaidTier
  showWordGoal.value = authStore.showWordGoal
  dailyWordGoal.value = authStore.dailyWordGoal
  runConnectionTest()
})

async function runConnectionTest() {
  connectionStatus.value = { status: 'testing' }
  try {
    const data = await authStore.testKey()
    connectionStatus.value = data
  } catch {
    connectionStatus.value = { status: 'not_configured' }
  }
}

async function saveKey() {
  keyError.value = ''
  const trimmed = keyInputValue.value.trim()
  if (!trimmed) {
    keyError.value = 'API key cannot be blank.'
    return
  }
  keySaving.value = true
  try {
    await authStore.updateProfile({
      geminiApiKey: trimmed,
      isPaidTier: isPaidTier.value,
      includeKey: true,
    })
    keyInputValue.value = ''
    isEditing.value = false
    runConnectionTest()
  } catch {
    keyError.value = 'Failed to save key. Please try again.'
  } finally {
    keySaving.value = false
  }
}

async function savePaidTier() {
  keySaving.value = true
  try {
    await authStore.updateProfile({
      isPaidTier: isPaidTier.value,
      includeKey: false,
    })
  } catch {
    keyError.value = 'Failed to save. Please try again.'
  } finally {
    keySaving.value = false
  }
}

function startEditing() {
  keyInputValue.value = ''
  keyError.value = ''
  isEditing.value = true
}

function cancelEditing() {
  keyInputValue.value = ''
  keyError.value = ''
  isEditing.value = false
  isPaidTier.value = authStore.isPaidTier
}

async function confirmRemoveKey() {
  keySaving.value = true
  try {
    await authStore.updateProfile({
      geminiApiKey: '',
      includeKey: true,
    })
    showRemoveDialog.value = false
    isEditing.value = false
    keyInputValue.value = ''
    runConnectionTest()
  } catch {
    keyError.value = 'Failed to remove key. Please try again.'
  } finally {
    keySaving.value = false
  }
}

async function saveGoal() {
  goalError.value = ''
  goalSuccess.value = ''
  goalSaving.value = true
  try {
    await authStore.updateProfile({
      showWordGoal: showWordGoal.value,
      dailyWordGoal: showWordGoal.value ? dailyWordGoal.value || 1000 : null,
      includeKey: false,
    })
    goalSuccess.value = 'Goal settings saved successfully.'
  } catch {
    goalError.value = 'Failed to save settings. Please try again.'
  } finally {
    goalSaving.value = false
  }
}
</script>

<style scoped>
.settings-page {
  min-height: 100vh;
  background: var(--wda-bg);
  display: flex;
  flex-direction: column;
  padding: 32px 40px;
}

.settings-header {
  margin-bottom: 24px;
  flex-shrink: 0;
}

.settings-subtitle {
  font-family: var(--wda-font-ui);
  font-size: 14px;
  color: var(--wda-text-muted);
  margin-bottom: 0;
}

.settings-card {
  flex: 1;
  display: flex;
  gap: 0;
  background: var(--wda-surface);
  border: 1px solid var(--wda-border);
  border-radius: var(--wda-radius);
  box-shadow: var(--wda-shadow);
  min-height: 0;
  overflow: hidden;
}

.settings-card-left {
  flex: 1;
  padding: 28px;
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow-y: auto;
}

.settings-card-right {
  width: 320px;
  flex-shrink: 0;
  padding: 28px;
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow-y: auto;
}

.settings-card-divider {
  width: 1px;
  flex-shrink: 0;
  background: var(--wda-border);
}

.settings-ai-content {
  flex: 1;
}

.wda-info-card {
  background: var(--wda-surface-2);
  border: 1px solid var(--wda-border);
  border-radius: var(--wda-radius-sm);
  padding: 16px;
}

.info-card-header {
  display: flex;
  align-items: center;
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--wda-text);
  margin-bottom: 6px;
}

.info-card-body {
  font-size: 0.85rem;
  color: var(--wda-text-muted);
  line-height: 1.5;
}
</style>
