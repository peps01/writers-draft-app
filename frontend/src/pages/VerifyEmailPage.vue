<template>
  <q-layout>
    <q-page-container>
      <q-page>
        <div class="auth-page">
          <div class="auth-brand">
            <h1 class="auth-logo">Writer's Draft</h1>
            <p class="auth-tagline">Your story. Your world. All in one place.</p>
          </div>
          <div class="auth-form-card" style="background:var(--wda-surface);border:1px solid var(--wda-border);border-radius:var(--wda-radius);box-shadow:var(--wda-shadow);text-align:center;">
            <div v-if="!errorMsg">
              <div style="font-size:48px;margin-bottom:16px;">❌</div>
              <div style="font-family:var(--wda-font-heading);font-size:1.5rem;font-weight:700;color:var(--wda-text);margin-bottom:8px;">Verification failed</div>
              <div style="font-family:var(--wda-font-ui);font-size:0.9rem;color:var(--wda-text-muted);margin-bottom:24px;">No verification data found.</div>
            </div>
            <template v-else>
              <div style="font-size:48px;margin-bottom:16px;">❌</div>
              <div style="font-family:var(--wda-font-heading);font-size:1.5rem;font-weight:700;color:var(--wda-text);margin-bottom:8px;">{{ title }}</div>
              <div style="font-family:var(--wda-font-ui);font-size:0.9rem;color:var(--wda-text-muted);margin-bottom:24px;">{{ errorMsg }}</div>
            </template>
            <q-btn flat color="primary" label="Go to login" no-caps to="/login" />
          </div>
        </div>
        <div style="position:fixed;top:16px;right:16px;z-index:9999">
          <q-btn flat round :icon="$q.dark.isActive ? 'light_mode' : 'dark_mode'" @click="$q.dark.toggle()" size="sm" />
        </div>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const errorMap = {
  missing_token: { title: 'Invalid link', msg: 'No verification token provided.' },
  expired: { title: 'Link expired', msg: 'This verification link has expired. Request a new one from the login page.' },
  invalid: { title: 'Invalid link', msg: 'This verification link is not valid.' },
  not_found: { title: 'User not found', msg: 'No account found for this verification link.' },
}

const error = route.query.error
const errorData = errorMap[error] || null
const errorMsg = ref(errorData ? errorData.msg : (error ? 'Unknown error.' : ''))
const title = ref(errorData ? errorData.title : 'Verification failed')
</script>
