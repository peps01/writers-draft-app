<template>
  <q-header class="wda-navbar bg-white">
    <div class="wda-navbar-inner">
      <div class="wda-navbar-left">
        <span class="wda-wordmark">Writer's Draft</span>
      </div>

      <div class="wda-navbar-center">
        <q-input
          rounded
          outlined
          dense
          placeholder="Search"
          class="wda-search-bar"
        >
          <template #prepend>
            <q-icon name="search" />
          </template>
        </q-input>
      </div>

      <div class="wda-navbar-right">
        <button class="wda-navbar-dark-btn" @click="$q.dark.toggle()">
          <span class="material-icons">{{ $q.dark.isActive ? 'light_mode' : 'dark_mode' }}</span>
        </button>

        <button v-if="isProjectRoute" class="wda-navbar-icon-btn" @click="openExportDialog?.()">
          <span class="material-icons">file_download</span>
        </button>

        <button class="wda-navbar-icon-btn" @click="$router.push('/projects/new')">
          <span class="material-icons">add</span>
        </button>

        <button class="wda-navbar-icon-btn" @click="$router.push('/settings')">
          <span class="material-icons">settings</span>
        </button>

        <div class="wda-navbar-avatar" @click.stop>
          {{ userInitial }}
          <q-menu anchor="bottom end" self="top end" :offset="[0, 8]">
            <q-list dense style="min-width: 180px">
              <q-item>
                <q-item-section>
                  <div style="padding: 4px 0">
                    <div style="font-family: 'Inter', sans-serif; font-weight: 600; font-size: 14px; color: var(--wda-text);">
                      {{ authStore.user?.username || 'User' }}
                    </div>
                    <div style="font-family: 'Inter', sans-serif; font-size: 12px; color: var(--wda-text-muted); margin-top: 2px;">
                      {{ authStore.user?.email || '' }}
                    </div>
                  </div>
                </q-item-section>
              </q-item>
              <q-separator />
              <q-item clickable v-close-popup @click="handleLogout">
                <q-item-section>
                  <div class="row items-center q-gutter-xs" style="color: var(--wda-negative, #c75d3a)">
                    <q-icon name="logout" size="xs" />
                    <span style="font-family: 'Inter', sans-serif; font-size: 13px;">Log out</span>
                  </div>
                </q-item-section>
              </q-item>
            </q-list>
          </q-menu>
        </div>
      </div>
    </div>
  </q-header>
</template>

<script setup>
import { computed, inject } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const openExportDialog = inject('openExportDialog')

const userInitial = computed(() => {
  return authStore.user?.username?.charAt(0)?.toUpperCase() || 'U'
})

const isProjectRoute = computed(() => {
  return !!route.params.id
})

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}
</script>
