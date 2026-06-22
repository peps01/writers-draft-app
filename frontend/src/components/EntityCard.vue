<template>
  <q-card flat bordered>
    <q-card-section>
      <div class="row items-center justify-between no-wrap">
        <div class="text-h6 ellipsis">{{ entity.name }}</div>
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
      <div v-if="entity.description" class="text-body2 text-grey q-mt-sm description-preview">
        {{ entity.description }}
      </div>
      <div v-else class="text-body2 text-grey-4 q-mt-sm">No description</div>
    </q-card-section>
  </q-card>
</template>

<script setup>
defineProps({
  entity: { type: Object, required: true },
})

defineEmits(['edit', 'delete'])
</script>

<style scoped>
.description-preview {
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}
</style>
