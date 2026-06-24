<template>
  <router-view />
</template>

<script setup>
import { watch } from 'vue'
import { useQuasar } from 'quasar'

const $q = useQuasar()

watch(
  () => $q.dark.isActive,
  (val) => {
    localStorage.setItem('wda_dark_mode', val)
  },
)
</script>
