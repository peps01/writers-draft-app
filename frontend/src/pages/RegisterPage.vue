<template>
  <q-layout>
    <q-page-container>
      <q-page>
        <div class="auth-page">
          <div class="auth-brand">
            <h1 class="auth-logo">Writer's Draft</h1>
            <p class="auth-tagline">Your story. Your world. All in one place.</p>
          </div>
          <div
            class="auth-form-card"
            style="
              background: var(--wda-surface);
              border: 1px solid var(--wda-border);
              border-radius: var(--wda-radius);
              box-shadow: var(--wda-shadow);
            "
          >
            <div style="text-align: center; margin-bottom: 24px">
              <div
                style="
                  font-family: var(--wda-font-heading);
                  font-size: 1.5rem;
                  font-weight: 700;
                  color: var(--wda-text);
                "
              >
                Create your account
              </div>
              <div
                style="
                  font-family: var(--wda-font-ui);
                  font-size: 0.9rem;
                  color: var(--wda-text-muted);
                  margin-top: 4px;
                "
              >
                Join the writers' community
              </div>
            </div>
            <q-form @submit="onSubmit" class="q-gutter-md">
              <q-input
                v-model="username"
                label="Username"
                outlined
                color="primary"
                autocomplete="username"
                :disable="submitting"
              />
              <q-input
                v-model="email"
                label="Email"
                type="email"
                outlined
                color="primary"
                autocomplete="email"
                :disable="submitting"
              />
              <q-input
                v-model="password"
                label="Password"
                type="password"
                outlined
                color="primary"
                autocomplete="new-password"
                :disable="submitting"
              />

              <q-banner v-if="error" class="bg-negative text-white q-mb-md" rounded>
                {{ error }}
              </q-banner>

              <q-btn
                type="submit"
                label="Register"
                color="primary"
                class="full-width"
                :loading="submitting"
                no-caps
                style="font-family: var(--wda-font-heading); font-size: 1rem; padding: 10px 0"
              />
            </q-form>

            <div class="text-center q-mt-lg">
              <q-btn
                flat
                to="/login"
                label="Already have an account? Log in"
                no-caps
                style="font-family: var(--wda-font-ui); font-size: 0.85rem"
              />
            </div>
          </div>
        </div>
        <div style="position: fixed; top: 16px; right: 16px; z-index: 9999">
          <q-btn
            flat
            round
            :icon="$q.dark.isActive ? 'light_mode' : 'dark_mode'"
            @click="$q.dark.toggle()"
            size="sm"
          />
        </div>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const email = ref('')
const password = ref('')
const error = ref('')
const submitting = ref(false)

async function onSubmit() {
  error.value = ''
  submitting.value = true
  try {
    await authStore.register(username.value, email.value, password.value)
    router.push('/dashboard')
  } catch (err) {
    const data = err.response?.data
    if (data?.error) {
      error.value = Array.isArray(data.error) ? data.error.join('; ') : data.error
    } else {
      error.value = 'Registration failed. Please try again.'
    }
  } finally {
    submitting.value = false
  }
}
</script>
