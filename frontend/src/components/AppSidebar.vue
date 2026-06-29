<template>
  <q-drawer
    v-if="!$q.fullscreen?.isActive"
    side="left"
    :width="220"
    bordered
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    class="wda-sidebar"
  >
    <div class="wda-sidebar-inner">
      <div class="wda-sidebar-header">
        <div class="wda-logo-badge">{{ authStore.user?.username?.charAt(0)?.toUpperCase() || '?' }}</div>
        <span class="wda-sidebar-header-label">{{ authStore.user?.username || 'User' }}</span>
        <q-btn flat dense round icon="close" size="sm" class="wda-sidebar-close-btn" @click="$emit('update:modelValue', false)" />
      </div>

      <div class="wda-sidebar-nav">
        <div
          v-for="item in navItems"
          :key="item.label"
          class="wda-nav-item"
          :class="{ active: isActive(item), disabled: item.disabled }"
          @click="navigate(item)"
        >
          <span class="material-icons">{{ item.icon }}</span>
          <span>{{ item.label }}</span>
        </div>
      </div>

      <div class="wda-sidebar-footer">
        <div class="wda-nav-item wda-nav-item--new-project" @click="$router.push('/projects/new')">
          <span class="material-icons">add</span>
          <span>New Project</span>
        </div>
      </div>
    </div>
  </q-drawer>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

defineProps({
  modelValue: { type: Boolean, default: true },
})

defineEmits(['update:modelValue'])
import { useAuthStore } from '@/stores/auth'
import { useProjectsStore } from '@/stores/projects'

const route = useRoute()
const router = useRouter()
const projectsStore = useProjectsStore()
const authStore = useAuthStore()

const projectId = computed(() => route.params.id || projectsStore.selectedProjectId || null)

const navItems = computed(() => [
  { label: 'Dashboard', icon: 'dashboard', to: '/dashboard', disabled: false, match: (path) => path === '/dashboard' },
  { label: 'Projects', icon: 'auto_stories', to: '/projects', disabled: false, match: (path) => path === '/projects' },
  {
    label: 'Story Bible',
    icon: 'menu_book',
    to: projectId.value ? `/projects/${projectId.value}/story-bible` : null,
    disabled: !projectId.value,
    match: (path) => path.includes('/story-bible'),
  },
  {
    label: 'Write',
    icon: 'edit_note',
    to: projectId.value ? `/projects/${projectId.value}/write` : null,
    disabled: !projectId.value,
    match: (path) => path.includes('/write'),
  },
  {
    label: 'Statistics',
    icon: 'bar_chart',
    to: projectId.value ? `/projects/${projectId.value}/statistics` : null,
    disabled: !projectId.value,
    match: (path) => path.includes('/statistics'),
  },
  { label: 'Settings', icon: 'settings', to: '/settings', disabled: false, match: (path) => path === '/settings' },
])

const isActive = (item) => {
  return item.match(route.path)
}

function navigate(item) {
  if (item.disabled || !item.to) return
  router.push(item.to)
}
</script>
