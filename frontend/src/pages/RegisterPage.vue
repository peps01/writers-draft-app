<template>
  <q-layout>
    <q-page-container>
      <q-page class="flex flex-center">
        <q-card style="width: 400px; max-width: 90vw">
          <q-card-section>
            <div class="text-h5 text-center">Create an account</div>
          </q-card-section>

          <q-card-section>
            <q-form @submit="onSubmit" class="q-gutter-md">
              <q-input
                v-model="username"
                label="Username"
                outlined
                autocomplete="username"
                :disable="submitting"
              />
              <q-input
                v-model="email"
                label="Email"
                type="email"
                outlined
                autocomplete="email"
                :disable="submitting"
              />
              <q-input
                v-model="password"
                label="Password"
                type="password"
                outlined
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
              />
            </q-form>
          </q-card-section>

          <q-card-section class="text-center q-pt-none">
            <q-btn flat to="/login" label="Already have an account? Log in" no-caps />
          </q-card-section>
        </q-card>
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
