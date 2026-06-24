<template>
  <div class="find-replace-bar">
    <div class="row items-center q-gutter-xs q-px-sm q-py-xs">
      <q-input
        ref="findInputRef"
        v-model="findTerm"
        placeholder="Find..."
        dense
        outlined
        size="sm"
        style="min-width: 160px"
        class="col"
        @keydown="onFindKeydown"
        @keyup.stop
        @keypress.stop
        @update:model-value="onFindChange"
      >
        <template #append>
          <span
            v-if="findTerm.length >= 2"
            class="text-caption"
            :class="matchCount === 0 ? 'text-negative' : 'text-grey'"
          >
            {{ matchCount === 0 ? 'No results' : `${currentMatchIndex + 1} of ${matchCount}` }}
          </span>
        </template>
      </q-input>

      <q-btn
        flat
        dense
        size="sm"
        icon="keyboard_arrow_up"
        :disable="!findTerm || matchCount === 0"
        @click="findPrevious"
        title="Find Previous (Shift+Enter)"
      >
        <q-tooltip>Find Previous</q-tooltip>
      </q-btn>

      <q-btn
        flat
        dense
        size="sm"
        icon="keyboard_arrow_down"
        :disable="!findTerm || matchCount === 0"
        @click="findNext"
        title="Find Next (Enter)"
      >
        <q-tooltip>Find Next</q-tooltip>
      </q-btn>

      <q-checkbox v-model="caseSensitive" dense size="sm" label="Aa" class="q-ml-xs" />

      <q-btn flat dense round icon="close" size="sm" @click="handleClose" title="Close (Escape)">
        <q-tooltip>Close</q-tooltip>
      </q-btn>
    </div>

    <div v-if="showReplaceRow" class="row items-center q-gutter-xs q-px-sm q-py-xs">
      <q-input
        v-model="replaceTerm"
        placeholder="Replace with..."
        dense
        outlined
        size="sm"
        style="min-width: 160px"
        class="col"
        @keydown="onReplaceKeydown"
        @keyup.stop
        @keypress.stop
      />
      <q-btn
        flat
        dense
        size="sm"
        label="Replace"
        :disable="!findTerm || matchCount === 0"
        no-caps
        @click="replace"
      >
        <q-tooltip>Replace</q-tooltip>
      </q-btn>
      <q-btn
        flat
        dense
        size="sm"
        label="All"
        :disable="!findTerm || matchCount === 0"
        no-caps
        @click="replaceAll"
      >
        <q-tooltip>Replace All</q-tooltip>
      </q-btn>
    </div>

    <div v-if="replaceMessage" class="row q-px-sm q-pb-xs">
      <span class="text-positive text-caption">{{ replaceMessage }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { TextSelection } from '@tiptap/pm/state'
import { findReplaceKey } from '@/components/extensions/findReplacePlugin'

const props = defineProps({
  editor: { type: Object, default: null },
})

const emit = defineEmits(['close'])

const findTerm = ref('')
const replaceTerm = ref('')
const caseSensitive = ref(false)
const findInputRef = ref(null)
const currentMatchIndex = ref(0)
const matchCount = ref(0)
const replaceMessage = ref('')
let replaceMessageTimer = null

const showReplaceRow = ref(true)

function findInDoc(doc, term, cs) {
  if (!term) return []
  const flags = cs ? 'g' : 'gi'
  const escaped = term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const regex = new RegExp(escaped, flags)
  const ranges = []

  doc.descendants((node, pos) => {
    if (node.isText) {
      const text = node.text
      let match
      while ((match = regex.exec(text)) !== null) {
        ranges.push({ from: pos + match.index, to: pos + match.index + match[0].length })
      }
    }
  })

  return ranges
}

function clearDecorations() {
  if (!props.editor) return
  props.editor.view.dispatch(props.editor.state.tr.setMeta(findReplaceKey, []))
}

function onFindChange() {
  if (findTerm.value.length < 2) {
    clearDecorations()
    matchCount.value = 0
    currentMatchIndex.value = -1
    return
  }
  if (!props.editor) return
  const ranges = findInDoc(props.editor.state.doc, findTerm.value, caseSensitive.value)
  matchCount.value = ranges.length
  if (ranges.length > 0) {
    selectMatch(ranges, 0)
  } else {
    clearDecorations()
    currentMatchIndex.value = -1
  }
}

function selectMatch(ranges, index) {
  if (!props.editor || !ranges || ranges.length === 0) return
  if (index < 0 || index >= ranges.length) return
  const { from, to } = ranges[index]
  currentMatchIndex.value = index
  const meta = ranges.map((r, i) => ({
    from: r.from,
    to: r.to,
    current: i === index,
  }))
  const tr = props.editor.state.tr
  tr.setMeta(findReplaceKey, meta)
  tr.setSelection(TextSelection.create(props.editor.state.doc, from, to))
  props.editor.view.dispatch(tr)
  requestAnimationFrame(() => {
    const el = props.editor?.view?.dom.querySelector('.search-result-current')
    if (el) {
      el.scrollIntoView({ block: 'center' })
    }
  })
}

function findNext() {
  if (!props.editor || matchCount.value === 0) return
  const ranges = findInDoc(props.editor.state.doc, findTerm.value, caseSensitive.value)
  if (ranges.length === 0) return
  matchCount.value = ranges.length
  const next = (currentMatchIndex.value + 1) % ranges.length
  selectMatch(ranges, next)
  findInputRef.value?.focus()
}

function findPrevious() {
  if (!props.editor || matchCount.value === 0) return
  const ranges = findInDoc(props.editor.state.doc, findTerm.value, caseSensitive.value)
  if (ranges.length === 0) return
  matchCount.value = ranges.length
  const prev = (currentMatchIndex.value - 1 + ranges.length) % ranges.length
  selectMatch(ranges, prev)
  findInputRef.value?.focus()
}

function replace() {
  if (!props.editor || matchCount.value === 0) return
  const ranges = findInDoc(props.editor.state.doc, findTerm.value, caseSensitive.value)
  if (ranges.length === 0 || currentMatchIndex.value >= ranges.length) return
  const { from, to } = ranges[currentMatchIndex.value]
  const tr = props.editor.state.tr
  tr.insertText(replaceTerm.value, from, to)
  props.editor.view.dispatch(tr)
  onFindChange()
  findInputRef.value?.focus()
}

function replaceAll() {
  if (!props.editor || !findTerm.value) return
  const ranges = findInDoc(props.editor.state.doc, findTerm.value, caseSensitive.value)
  if (ranges.length === 0) return

  clearDecorations()

  let tr = props.editor.state.tr
  for (let i = ranges.length - 1; i >= 0; i--) {
    const { from, to } = ranges[i]
    tr = tr.insertText(replaceTerm.value, from, to)
  }
  props.editor.view.dispatch(tr)

  matchCount.value = 0
  currentMatchIndex.value = -1
  findTerm.value = ''
  replaceMessage.value = `Replaced ${ranges.length} occurrence${ranges.length === 1 ? '' : 's'}`
  if (replaceMessageTimer) clearTimeout(replaceMessageTimer)
  replaceMessageTimer = setTimeout(() => {
    replaceMessage.value = ''
  }, 3000)

  findInputRef.value?.focus()
}

function onFindKeydown(e) {
  e.stopPropagation()
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    findNext()
  } else if (e.key === 'Enter' && e.shiftKey) {
    e.preventDefault()
    findPrevious()
  }
}

function onReplaceKeydown(e) {
  e.stopPropagation()
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    replace()
  }
}

function handleClose() {
  clearDecorations()
  findTerm.value = ''
  replaceTerm.value = ''
  replaceMessage.value = ''
  matchCount.value = 0
  currentMatchIndex.value = -1
  if (props.editor) {
    props.editor.chain().focus().run()
  }
  emit('close')
}

function onDocumentKeydown(e) {
  if (e.key === 'Escape') {
    handleClose()
  }
}

onMounted(() => {
  document.addEventListener('keydown', onDocumentKeydown)
  nextTick(() => findInputRef.value?.focus())
})

onBeforeUnmount(() => {
  document.removeEventListener('keydown', onDocumentKeydown)
  clearDecorations()
  if (replaceMessageTimer) clearTimeout(replaceMessageTimer)
})

watch(caseSensitive, () => {
  if (findTerm.value.length >= 2) onFindChange()
})
</script>

<style scoped>
.find-replace-bar {
  border-bottom: 1px solid var(--q-separator-color, rgba(0, 0, 0, 0.12));
  background: var(--q-color-surface, transparent);
}
</style>
