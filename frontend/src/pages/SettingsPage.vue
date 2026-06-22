<template>
  <q-layout>
    <q-page-container>
      <q-page class="q-pa-md" style="max-width: 700px; margin: 0 auto">
        <q-btn flat icon="arrow_back" label="Back to Dashboard" to="/dashboard" no-caps class="q-mb-md" />

        <div class="text-h4 q-mb-lg">Settings</div>

        <div class="text-h6 q-mb-sm">AI Assistant Settings</div>
        <div class="text-body2 text-grey q-mb-md">
          By default, Writer's Draft App uses a shared free-tier Gemini API key. You can provide
          your own key for higher limits or data privacy.
        </div>

        <q-card flat bordered class="q-mb-md">
          <q-card-section>
            <div class="text-caption text-grey q-mb-sm">Current status:</div>
            <div class="text-body2">
              <template v-if="!authStore.hasGeminiKey">Using shared default key (free tier)</template>
              <template v-else-if="!authStore.isPaidTier">Using your own key (free tier)</template>
              <template v-else>Using your own key (paid tier)</template>
            </div>
          </q-card-section>
        </q-card>

        <q-card flat bordered>
          <q-card-section>
            <q-input
              v-model="geminiApiKey"
              :type="showKey ? 'text' : 'password'"
              label="Your Gemini API Key"
              placeholder="Leave blank to use the shared default key."
              outlined
              dense
              class="q-mb-md"
            >
              <template #append>
                <q-btn flat dense round :icon="showKey ? 'visibility_off' : 'visibility'" @click="showKey = !showKey" />
              </template>
            </q-input>

            <q-checkbox v-model="isPaidTier" label="I'm using a paid-tier key (my data won't be used for model training)." class="q-mb-md" />

            <div v-if="error" class="text-negative q-mb-md">{{ error }}</div>
            <div v-if="success" class="text-positive q-mb-md">{{ success }}</div>

            <div class="row q-gutter-sm">
              <q-btn color="primary" label="Save" no-caps :loading="saving" @click="saveSettings" />
              <q-btn flat color="negative" label="Clear key" no-caps :loading="saving" @click="clearKey" />
            </div>
          </q-card-section>
        </q-card>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const geminiApiKey = ref('')
const isPaidTier = ref(false)
const showKey = ref(false)
const saving = ref(false)
const error = ref('')
const success = ref('')

onMounted(() => {
  isPaidTier.value = authStore.isPaidTier
})

async function saveSettings() {
  error.value = ''
  success.value = ''
  saving.value = true
  try {
    await authStore.updateProfile(geminiApiKey.value, isPaidTier.value)
    success.value = 'Settings saved successfully.'
  } catch {
    error.value = 'Failed to save settings. Please try again.'
  } finally {
    saving.value = false
  }
}

async function clearKey() {
  error.value = ''
  success.value = ''
  saving.value = true
  try {
    await authStore.updateProfile('', isPaidTier.value)
    geminiApiKey.value = ''
    success.value = 'Key cleared. Using shared default key.'
  } catch {
    error.value = 'Failed to clear key. Please try again.'
  } finally {
    saving.value = false
  }
}
</script>
