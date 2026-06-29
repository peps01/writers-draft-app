<template>
  <q-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    @before-hide="resetForm"
    :maximized="maximized"
  >
    <q-card class="wda-card" :style="{ minWidth: maximized ? '100%' : '400px' }">
      <q-card-section>
        <div class="text-h6" style="font-family: var(--wda-font-heading)">
          {{ entity ? 'Edit' : 'Add' }} {{ entityLabel }}
        </div>
      </q-card-section>
      <q-card-section>
        <q-input
          v-model="form.name"
          :label="nameLabel"
          autofocus
          outlined
          color="primary"
          :error="!!nameError"
          :error-message="nameError"
          @keyup.enter="submit"
        />
        <q-input
          v-model="form.description"
          label="Description (optional)"
          type="textarea"
          :rows="4"
          outlined
          color="primary"
          class="q-mt-md"
        />
        <div v-if="errorText" class="text-negative q-mt-sm">{{ errorText }}</div>
      </q-card-section>
      <q-card-actions align="right">
        <q-btn flat label="Cancel" v-close-popup no-caps />
        <q-btn unelevated color="primary" label="Save" :loading="saving" no-caps @click="submit" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, required: true },
  entity: { type: Object, default: null },
  saving: { type: Boolean, default: false },
  errorText: { type: String, default: '' },
  entityLabel: { type: String, default: 'Entity' },
  nameLabel: { type: String, default: 'Name' },
  maximized: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'save'])

const form = ref({ name: '', description: '' })
const nameError = ref('')

watch(
  () => props.modelValue,
  (val) => {
    if (val) {
      form.value = {
        name: props.entity?.name || '',
        description: props.entity?.description || '',
      }
      nameError.value = ''
    }
  },
)

function resetForm() {
  form.value = { name: '', description: '' }
  nameError.value = ''
}

function submit() {
  if (!form.value.name.trim()) {
    nameError.value = `${props.nameLabel} cannot be empty.`
    return
  }
  nameError.value = ''
  emit('save', { name: form.value.name.trim(), description: form.value.description })
}
</script>
