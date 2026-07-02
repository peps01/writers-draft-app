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
            <div style="font-size:48px;margin-bottom:16px;">✉️</div>
            <div style="font-family:var(--wda-font-heading);font-size:1.5rem;font-weight:700;color:var(--wda-text);margin-bottom:8px;">Check your email</div>
            <div style="font-family:var(--wda-font-ui);font-size:0.9rem;color:var(--wda-text-muted);margin-bottom:4px;">We sent a verification link to</div>
            <div style="font-family:var(--wda-font-ui);font-size:0.95rem;font-weight:600;color:var(--wda-text);margin-bottom:24px;">{{ email }}</div>
            <q-btn flat color="primary" label="Resend email" no-caps :disable="cooldown > 0" @click="resend" />
            <div v-if="cooldown > 0" style="font-family:var(--wda-font-ui);font-size:0.8rem;color:var(--wda-text-muted);margin-top:8px;">Resend available in {{ cooldown }}s</div>
            <div v-if="resendMsg" style="font-family:var(--wda-font-ui);font-size:0.85rem;color:var(--wda-positive);margin-top:8px;">{{ resendMsg }}</div>
            <div class="text-center q-mt-lg">
              <q-btn flat to="/login" label="Back to login" no-caps style="font-family:var(--wda-font-ui);font-size:0.85rem" />
            </div>
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
import { api } from '@/boot/axios'

const route = useRoute()
const email = ref(route.query.email || 'your email address')
const cooldown = ref(0)
const resendMsg = ref('')

async function resend() {
  if (cooldown.value > 0) return
  try {
    await api.post('/auth/resend-verification/', { email: email.value })
    resendMsg.value = 'Verification email sent!'
    cooldown.value = 60
    const timer = setInterval(() => {
      cooldown.value--
      if (cooldown.value <= 0) clearInterval(timer)
    }, 1000)
  } catch {
    resendMsg.value = 'Failed to resend. Try again later.'
  }
}
</script>
