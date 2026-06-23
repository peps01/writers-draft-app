<template>
  <div class="find-replace-bar row items-center q-gutter-xs q-px-sm q-py-xs">
    <q-input
      ref="findInputRef"
      v-model="findTerm"
      placeholder="Find..."
      dense
      outlined
      size="sm"
      style="min-width: 180px"
      class="col"
      @keydown.enter="findNext"
      @update:model-value="onFindChange"
    >
      <template #append>
        <span class="text-caption text-grey">{{ matchStatus }}</span>
      </template>
    </q-input>

    <q-input
      v-model="replaceTerm"
      placeholder="Replace with..."
      dense
      outlined
      size="sm"
      style="min-width: 150px"
      class="col"
      @keydown.enter="replace"
    />

    <q-btn flat dense size="sm" icon="keyboard_arrow_down" :disable="!findTerm" @click="findNext" title="Find Next (Enter)">
      <q-tooltip>Find Next</q-tooltip>
    </q-btn>

    <q-btn flat dense size="sm" label="Replace" :disable="!findTerm || matchCount === 0" no-caps @click="replace">
      <q-tooltip>Replace</q-tooltip>
    </q-btn>

    <q-btn flat dense size="sm" label="All" :disable="!findTerm || matchCount === 0" no-caps @click="replaceAll">
      <q-tooltip>Replace All</q-tooltip>
    </q-btn>

    <q-checkbox v-model="caseSensitive" dense size="sm" label="Aa" class="q-ml-xs" />

    <q-space />

    <q-btn flat dense round icon="close" size="sm" @click="handleClose" title="Close (Escape)">
      <q-tooltip>Close</q-tooltip>
    </q-btn>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'

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

const matchStatus = computed(() => {
  if (!findTerm.value) return ''
  if (matchCount.value === 0) return 'No matches'
  return `${currentMatchIndex.value + 1} of ${matchCount.value} matches`
})

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

function removeHighlights() {
  if (!props.editor) return
  const { schema } = props.editor.state
  const markType = schema.marks.highlight
  if (!markType) return
  const tr = props.editor.state.tr
  tr.removeMark(0, props.editor.state.doc.content.size, markType)
  props.editor.view.dispatch(tr)
}

function highlightMatches() {
  if (!props.editor || !findTerm.value) return
  const { schema } = props.editor.state
  const highlightType = schema.marks.highlight
  if (!highlightType) return

  const ranges = findInDoc(props.editor.state.doc, findTerm.value, caseSensitive.value)
  matchCount.value = ranges.length
  currentMatchIndex.value = ranges.length > 0 ? 0 : -1

  let tr = props.editor.state.tr
  tr.removeMark(0, props.editor.state.doc.content.size, highlightType)
  ranges.forEach(({ from, to }) => {
    try {
      tr = tr.addMark(from, to, highlightType.create())
    } catch (e) {
      console.error('addMark failed at', { from, to }, e)
    }
  })
  props.editor.view.dispatch(tr)

  if (ranges.length > 0) selectMatch(0)
}

function selectMatch(index) {
  if (!props.editor || matchCount.value === 0) return
  const ranges = findInDoc(props.editor.state.doc, findTerm.value, caseSensitive.value)
  if (index < 0 || index >= ranges.length) return
  const { from, to } = ranges[index]
  currentMatchIndex.value = index
  props.editor.commands.setTextSelection({ from, to })
  props.editor.commands.scrollIntoView()
}

function findNext() {
  if (!props.editor || matchCount.value === 0) return
  const next = (currentMatchIndex.value + 1) % matchCount.value
  selectMatch(next)
}

function replace() {
  if (!props.editor || matchCount.value === 0) return
  const { from, to } = props.editor.state.selection
  const ranges = findInDoc(props.editor.state.doc, findTerm.value, caseSensitive.value)
  const currentRange = ranges[currentMatchIndex.value]
  if (!currentRange) return
  if (from !== currentRange.from || to !== currentRange.to) {
    selectMatch(currentMatchIndex.value)
    return
  }
  props.editor
    .chain()
    .focus()
    .insertText(replaceTerm.value, from, to)
    .run()
  highlightMatches()
}

function replaceAll() {
  if (!props.editor || !findTerm.value) return
  const { schema } = props.editor.state
  const highlightType = schema.marks.highlight
  if (!highlightType) return

  const ranges = findInDoc(props.editor.state.doc, findTerm.value, caseSensitive.value)
  if (ranges.length === 0) return

  let tr = props.editor.state.tr
  tr.removeMark(0, props.editor.state.doc.content.size, highlightType)
  for (let i = ranges.length - 1; i >= 0; i--) {
    const { from, to } = ranges[i]
    tr = tr.insertText(replaceTerm.value, from, to)
  }
  props.editor.view.dispatch(tr)
  matchCount.value = 0
  currentMatchIndex.value = -1
}

function onFindChange() {
  if (!findTerm.value) {
    removeHighlights()
    matchCount.value = 0
    currentMatchIndex.value = -1
    return
  }
  highlightMatches()
}

function handleClose() {
  removeHighlights()
  findTerm.value = ''
  replaceTerm.value = ''
  matchCount.value = 0
  currentMatchIndex.value = -1
  emit('close')
}

watch(() => props.editor, (ed) => {
  if (ed) {
    nextTick(() => {
      findInputRef.value?.focus()
    })
  }
})

watch(caseSensitive, () => {
  if (findTerm.value) highlightMatches()
})

function onKeydown(e) {
  if (e.key === 'Escape') {
    handleClose()
  }
}

onMounted(() => {
  document.addEventListener('keydown', onKeydown)
  nextTick(() => findInputRef.value?.focus())
})

onBeforeUnmount(() => {
  document.removeEventListener('keydown', onKeydown)
  removeHighlights()
})
</script>

<style scoped>
.find-replace-bar {
  border-bottom: 1px solid var(--q-separator-color, rgba(0,0,0,0.12));
  background: var(--q-color-surface, transparent);
}
</style>
