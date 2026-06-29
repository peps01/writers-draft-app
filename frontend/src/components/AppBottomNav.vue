<template>
  <div class="app-bottom-nav" :class="{ 'app-bottom-nav--hidden': hidden }">
    <button class="app-bottom-nav__toggle" @click="toggle">
      <span class="material-icons app-bottom-nav__toggle-icon">keyboard_arrow_down</span>
    </button>
    <div class="app-bottom-nav__body">
      <router-link
        v-for="item in navItems"
        :key="item.route"
        :to="item.to || ''"
        class="app-bottom-nav__item"
        :class="{ 'app-bottom-nav__item--active': isActive(item), 'app-bottom-nav__item--disabled': !item.to }"
        @click.prevent="navigate(item)"
      >
        <q-icon :name="item.icon" size="22px" />
        <span class="app-bottom-nav__label">{{ item.label }}</span>
      </router-link>
    </div>
  </div>
  <button v-if="hidden" class="app-bottom-nav__reveal" @click="toggle">
    <span class="material-icons">keyboard_arrow_up</span>
  </button>
</template>

<script setup>
import { computed, inject } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProjectsStore } from '@/stores/projects'

const route = useRoute()
const router = useRouter()
const projectsStore = useProjectsStore()

const hidden = inject('bottomNavHidden')

const projectId = computed(() => route.params.id || projectsStore.selectedProjectId || null)

const navItems = computed(() => [
  { label: 'Dashboard', icon: 'dashboard', to: '/dashboard', match: (path) => path === '/dashboard' },
  {
    label: 'Story Bible',
    icon: 'menu_book',
    to: projectId.value ? `/projects/${projectId.value}/story-bible` : null,
    match: (path) => path.includes('/story-bible'),
  },
  {
    label: 'Write',
    icon: 'edit_note',
    to: projectId.value ? `/projects/${projectId.value}/write` : null,
    match: (path) => path.includes('/write'),
  },
  {
    label: 'Stats',
    icon: 'bar_chart',
    to: projectId.value ? `/projects/${projectId.value}/statistics` : null,
    match: (path) => path.includes('/statistics'),
  },
  { label: 'Settings', icon: 'settings', to: '/settings', match: (path) => path === '/settings' },
])

const isActive = (item) => {
  return item.match(route.path)
}

function navigate(item) {
  if (!item.to) return
  router.push(item.to)
}

function toggle() {
  hidden.value = !hidden.value
}
</script>
