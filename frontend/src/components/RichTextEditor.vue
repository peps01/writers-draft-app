<template>
  <div ref="editorWrapper" class="rich-text-editor-wrapper" :style="editorInlineStyle">
    <editor-content :editor="editor" class="editor-content" />
  </div>
</template>

<script setup>
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Underline from '@tiptap/extension-underline'
import CharacterCount from '@tiptap/extension-character-count'
import Placeholder from '@tiptap/extension-placeholder'
import { TextStyle } from '@tiptap/extension-text-style'
import FontFamily from '@tiptap/extension-font-family'
import Highlight from '@tiptap/extension-highlight'
import { watch, ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { FindReplaceExtension } from '@/components/extensions/findReplacePlugin'

const props = defineProps({
  modelValue: { type: String, default: '' },
  editable: { type: Boolean, default: true },
  placeholder: { type: String, default: 'Begin writing your scene...' },
  fontSize: { type: String, default: '1.1rem' },
  fontFamily: { type: String, default: 'serif' },
})

const emit = defineEmits(['update:modelValue', 'wordCountUpdate', 'ready'])

const editorWrapper = ref(null)

function migrateContentIfNeeded(content) {
  if (!content || content.trim() === '') return '<p></p>'
  if (content.trim().startsWith('<')) return content
  let html = content
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>')
  const paragraphs = html.split(/\n\n+/)
  return paragraphs
    .map((p) => p.trim())
    .filter((p) => p)
    .map((p) => `<p>${p.replace(/\n/g, '<br>')}</p>`)
    .join('')
}

const sanitizedInitial = migrateContentIfNeeded(props.modelValue)

const editor = useEditor({
  content: sanitizedInitial,
  editable: props.editable,
  extensions: [
    StarterKit,
    Underline,
    CharacterCount,
    Placeholder.configure({ placeholder: props.placeholder }),
    TextStyle,
    FontFamily,
    Highlight.configure({ multicolor: false }),
    FindReplaceExtension,
  ],
  onUpdate: ({ editor }) => {
    const html = editor.getHTML()
    emit('update:modelValue', html)
    const words = editor.storage.characterCount?.words?.() || 0
    emit('wordCountUpdate', words)
  },
})

const fontFamilyCSS = computed(() => {
  switch (props.fontFamily) {
    case 'monospace':
      return "'Courier New', Courier, monospace"
    case 'sans-serif':
    case 'sans':
      return 'Arial, Helvetica, sans-serif'
    default:
      return 'Georgia, "Times New Roman", serif'
  }
})

const editorInlineStyle = computed(() => ({
  '--editor-font-size': props.fontSize,
  '--editor-font-family': fontFamilyCSS.value,
}))

if (sanitizedInitial !== props.modelValue) {
  onMounted(() => {
    emit('update:modelValue', sanitizedInitial)
    if (editor.value) {
      const words = editor.value.storage.characterCount?.words?.() || 0
      emit('wordCountUpdate', words)
      emit('ready', editor.value)
    }
  })
} else {
  onMounted(() => {
    if (editor.value) {
      emit('ready', editor.value)
    }
  })
}

watch(
  () => props.modelValue,
  (newVal) => {
    if (!editor.value) return
    const current = editor.value.getHTML()
    if (newVal !== current) {
      editor.value.commands.setContent(newVal || '<p></p>', false)
    }
  },
)

watch(
  () => props.editable,
  (val) => {
    if (editor.value) {
      editor.value.setEditable(val)
    }
  },
)

watch(
  () => props.placeholder,
  (val) => {
    if (editor.value) {
      editor.value.extensionManager.extensions
        .filter((ext) => ext.name === 'placeholder')
        .forEach((ext) => {
          ext.options.placeholder = val
        })
      editor.value.view.dispatch(editor.value.state.tr)
    }
  },
)

onBeforeUnmount(() => {
  if (editor.value) {
    editor.value.destroy()
  }
})
</script>

<style>
.rich-text-editor-wrapper {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.rich-text-editor-wrapper .editor-content {
  flex: 1;
  min-height: 0;
}

.rich-text-editor-wrapper .ProseMirror p.is-editor-empty:first-child::before {
  color: #adb5bd;
  content: attr(data-placeholder);
  float: left;
  height: 0;
  pointer-events: none;
}

.rich-text-editor-wrapper .ProseMirror mark {
  background-color: #fef08a;
  padding: 0.1em 0.2em;
  border-radius: 2px;
}

.rich-text-editor-wrapper .search-result {
  background-color: rgba(255, 213, 0, 0.4);
  border-radius: 2px;
}

.rich-text-editor-wrapper .search-result-current {
  background-color: rgba(255, 140, 0, 0.6);
  border-radius: 2px;
}

.rich-text-editor-wrapper .ProseMirror s {
  text-decoration: line-through;
}

.rich-text-editor-wrapper .ProseMirror ul,
.rich-text-editor-wrapper .ProseMirror ol {
  padding-left: 1.5em;
}

.rich-text-editor-wrapper .ProseMirror li {
  margin: 0.25em 0;
}
</style>
