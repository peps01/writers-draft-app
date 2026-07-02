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
            <div v-if="loading"><q-spinner size="lg" color="primary" /></div>
            <template v-else-if="verified">
              <div style="font-size:48px;margin-bottom:16px;">✅</div>
              <div style="font-family:var(--wda-font-heading);font-size:1.5rem;font-weight:700;color:var(--wda-text);margin-bottom:8px;">Email verified!</div>
              <div style="font-family:var(--wda-font-ui);font-size:0.9rem;color:var(--wda-text-muted);margin-bottom:24px;">Redirecting to login in {{ countdown }}s...</div>
              <q-btn unelevated color="primary" label="Log in now" no-caps :to="'/login'" />
            </template>
            <template v-else>
              <div style="font-size:48px;margin-bottom:16px;">❌</div>
              <div style="font-family:var(--wda-font-heading);font-size:1.5rem;font-weight:700;color:var(--wda-text);margin-bottom:8px;">Invalid or expired link</div>
              <div style="font-family:var(--wda-font-ui);font-size:0.9rem;color:var(--wda-text-muted);margin-bottom:24px;">{{ errorMsg }}</div>
              <q-btn flat color="primary" label="Go to login" no-caps to="/login" />
            </template>
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
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/boot/axios'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const verified = ref(false)
const errorMsg = ref('')
const countdown = ref(5)

async function verify() {
  const token = route.query.token
  if (!token) {
    loading.value = false
    errorMsg.value = 'Missing verification token.'
    return
  }
  try {
    await api.get('/auth/verify-email/', { params: { token } })
    verified.value = true
    const timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(timer)
        router.push('/login')
      }
    }, 1000)
  } catch (err) {
    errorMsg.value = err.response?.data?.error || 'Verification failed.'
  } finally {
    loading.value = false
  }
}

onMounted(verify)
</script>
