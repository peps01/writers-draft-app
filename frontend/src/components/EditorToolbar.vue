<template>
  <div class="editor-toolbar">
    <!-- Text formatting -->
    <q-btn
      v-if="editor"
      flat
      dense
      icon="format_bold"
      size="sm"
      :color="editor.isActive('bold') ? 'primary' : ''"
      @click="editor.chain().focus().toggleBold().run()"
      title="Bold (Ctrl+B)"
    >
      <q-tooltip>Bold</q-tooltip>
    </q-btn>
    <q-btn
      v-if="editor"
      flat
      dense
      icon="format_italic"
      size="sm"
      :color="editor.isActive('italic') ? 'primary' : ''"
      @click="editor.chain().focus().toggleItalic().run()"
      title="Italic (Ctrl+I)"
    >
      <q-tooltip>Italic</q-tooltip>
    </q-btn>
    <q-btn
      v-if="editor"
      flat
      dense
      icon="format_underline"
      size="sm"
      :color="editor.isActive('underline') ? 'primary' : ''"
      @click="editor.chain().focus().toggleUnderline().run()"
      title="Underline (Ctrl+U)"
    >
      <q-tooltip>Underline</q-tooltip>
    </q-btn>
    <q-btn
      v-if="editor"
      flat
      dense
      icon="highlight"
      size="sm"
      :color="editor.isActive('highlight') ? 'primary' : ''"
      @click="editor.chain().focus().toggleHighlight().run()"
      title="Highlight"
    >
      <q-tooltip>Highlight</q-tooltip>
    </q-btn>

    <q-separator vertical class="q-mx-xs" />

    <!-- Headings -->
    <q-btn
      v-if="editor"
      flat
      dense
      label="H1"
      size="sm"
      :color="editor.isActive('heading', { level: 1 }) ? 'primary' : ''"
      @click="editor.chain().focus().toggleHeading({ level: 1 }).run()"
    />
    <q-btn
      v-if="editor"
      flat
      dense
      label="H2"
      size="sm"
      :color="editor.isActive('heading', { level: 2 }) ? 'primary' : ''"
      @click="editor.chain().focus().toggleHeading({ level: 2 }).run()"
    />
    <q-btn
      v-if="editor"
      flat
      dense
      label="H3"
      size="sm"
      :color="editor.isActive('heading', { level: 3 }) ? 'primary' : ''"
      @click="editor.chain().focus().toggleHeading({ level: 3 }).run()"
    />

    <q-separator vertical class="q-mx-xs" />

    <!-- Insert -->
    <q-btn
      v-if="editor"
      flat
      dense
      icon="horizontal_rule"
      size="sm"
      @click="editor.chain().focus().setHorizontalRule().run()"
      title="Scene Break (Horizontal Rule)"
    >
      <q-tooltip>Scene Break</q-tooltip>
    </q-btn>
    <q-btn
      v-if="editor"
      flat
      dense
      icon="format_quote"
      size="sm"
      :color="editor.isActive('blockquote') ? 'primary' : ''"
      @click="editor.chain().focus().toggleBlockquote().run()"
      title="Blockquote"
    >
      <q-tooltip>Blockquote</q-tooltip>
    </q-btn>

    <q-separator vertical class="q-mx-xs" />

    <!-- History -->
    <q-btn
      v-if="editor"
      flat
      dense
      icon="undo"
      size="sm"
      @click="editor.chain().focus().undo().run()"
      title="Undo (Ctrl+Z)"
    >
      <q-tooltip>Undo</q-tooltip>
    </q-btn>
    <q-btn
      v-if="editor"
      flat
      dense
      icon="redo"
      size="sm"
      @click="editor.chain().focus().redo().run()"
      title="Redo (Ctrl+Shift+Z)"
    >
      <q-tooltip>Redo</q-tooltip>
    </q-btn>

    <q-separator vertical class="q-mx-xs" />

    <!-- Font Family -->
    <q-select
      v-model="fontFamilyModel"
      :options="fontOptions"
      dense
      flat
      size="sm"
      style="min-width: 100px"
      borderless
      @update:model-value="emitFontFamilyChange"
    />

    <!-- Font Size -->
    <q-btn-toggle
      v-model="fontSizeModel"
      flat
      dense
      no-caps
      size="sm"
      :options="fontSizeOptions"
      @update:model-value="emitFontSizeChange"
    />

    <q-separator vertical class="q-mx-xs" />

    <!-- Find & Replace Toggle -->
    <q-btn
      flat
      dense
      icon="find_replace"
      size="sm"
      :color="showFindReplace ? 'primary' : ''"
      @click="$emit('toggleFindReplace')"
      title="Find & Replace (Ctrl+F)"
    >
      <q-tooltip>Find & Replace</q-tooltip>
    </q-btn>

    <q-space />

    <!-- Stats -->
    <div
      v-if="wordCount !== undefined"
      class="text-caption q-mr-sm"
      style="white-space: nowrap; color: var(--wda-text-muted)"
    >
      {{ wordCount }} words
      <span class="q-ml-xs">&middot; ~{{ readingTime }} min read</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  editor: { type: Object, default: null },
  wordCount: { type: Number, default: 0 },
  showFindReplace: { type: Boolean, default: false },
  fontSize: { type: String, default: '1.1rem' },
  fontFamily: { type: String, default: 'serif' },
})

const emit = defineEmits(['fontFamilyChange', 'fontSizeChange', 'toggleFindReplace'])

const fontFamilyModel = ref(props.fontFamily)
const fontSizeModel = ref(props.fontSize)

watch(
  () => props.fontFamily,
  (val) => {
    fontFamilyModel.value = val
  },
)
watch(
  () => props.fontSize,
  (val) => {
    fontSizeModel.value = val
  },
)

const fontOptions = [
  { label: 'Serif', value: 'serif' },
  { label: 'Sans-serif', value: 'sans-serif' },
  { label: 'Monospace', value: 'monospace' },
]

const fontSizeOptions = [
  { label: 'S', value: '0.9rem', tooltip: 'Small' },
  { label: 'M', value: '1.1rem', tooltip: 'Normal' },
  { label: 'L', value: '1.3rem', tooltip: 'Large' },
  { label: 'XL', value: '1.5rem', tooltip: 'Extra Large' },
]

const readingTime = computed(() => {
  if (!props.wordCount || props.wordCount === 0) return '< 1'
  const min = Math.ceil(props.wordCount / 200)
  return min < 1 ? '< 1' : min
})

function emitFontFamilyChange(val) {
  emit('fontFamilyChange', val)
}

function emitFontSizeChange(val) {
  emit('fontSizeChange', val)
}
</script>
