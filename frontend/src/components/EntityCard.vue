<template>
  <div class="entity-card">
    <div class="row items-center justify-between no-wrap">
      <div class="entity-name ellipsis">{{ entity.name }}</div>
      <q-btn flat dense round icon="more_vert" size="sm" @click.stop>
        <q-menu anchor="bottom end" self="top end">
          <q-list dense style="min-width: 120px">
            <q-item clickable v-close-popup @click.stop="$emit('edit', entity)">
              <q-item-section>Edit</q-item-section>
            </q-item>
            <q-item clickable v-close-popup @click.stop="$emit('delete', entity)">
              <q-item-section class="text-negative">Delete</q-item-section>
            </q-item>
          </q-list>
        </q-menu>
      </q-btn>
    </div>
    <div v-if="entity.description" class="entity-desc q-mt-sm">
      {{ entity.description }}
    </div>
    <div v-else class="entity-desc q-mt-sm" style="color: var(--wda-text-muted); opacity: 0.5">
      No description
    </div>
  </div>
</template>

<script setup>
defineProps({
  entity: { type: Object, required: true },
})

defineEmits(['edit', 'delete'])
</script>

<style scoped>
.entity-card {
  background: var(--wda-surface);
  border: 1px solid var(--wda-border);
  border-radius: var(--wda-radius);
  box-shadow: var(--wda-shadow);
  transition:
    box-shadow 0.2s ease,
    transform 0.15s ease;
  padding: 20px;
}
.entity-card:hover {
  box-shadow: var(--wda-shadow-md);
  transform: translateY(-1px);
}
.entity-card .entity-name {
  font-family: var(--wda-font-heading);
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 6px;
}
.entity-card .entity-desc {
  font-size: 0.85rem;
  color: var(--wda-text-muted);
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.5;
}
</style>
