import { Extension } from '@tiptap/core'
import { Plugin, PluginKey } from '@tiptap/pm/state'

function normalizeSuggestions(items) {
  return items.map((item) =>
    typeof item === 'string'
      ? { label: item, type: 'general', insertText: item }
      : item,
  )
}

function insertSuggestion(from, insertText, view) {
  const { tr } = view.state
  const textBefore = view.state.doc.textBetween(
    Math.max(0, from),
    view.state.selection.$head.pos,
  )
  const wordMatch = textBefore.match(/(\S+)$/)
  const word = wordMatch ? wordMatch[1] : ''
  tr.insertText(insertText, from + textBefore.length - word.length, view.state.selection.$head.pos)
  view.dispatch(tr)
  view.focus()
}

const StoryBibleAutocomplete = Extension.create({
  name: 'storyBibleAutocomplete',

  addOptions() {
    return {
      getSuggestions: () => [],
      minChars: 1,
    }
  },

  addProseMirrorPlugins() {
    const extension = this
    const pluginKey = new PluginKey('storyBibleAutocomplete')
    let popupEl = null
    let editorView = null

    return [
      new Plugin({
        key: pluginKey,

        state: {
          init() {
            return {
              suggestions: [],
              selectedIndex: 0,
              from: null,
              show: false,
            }
          },
          apply(tr, prev, oldState, newState) {
            const selectMeta = tr.getMeta('autocomplete_select')
            if (selectMeta !== undefined) {
              return { ...prev, selectedIndex: selectMeta }
            }
            if (tr.getMeta('autocomplete_close')) {
              return { suggestions: [], selectedIndex: 0, from: null, show: false }
            }

            const { selection } = newState
            const { $head } = selection

            if (!selection.empty) {
              return { suggestions: [], selectedIndex: 0, from: null, show: false }
            }

            const textBefore = newState.doc.textBetween(
              $head.start(Math.max(1, $head.depth - 1)),
              $head.pos,
            )
            const lastWordMatch = textBefore.match(/(\S+)$/)
            const currentWord = lastWordMatch ? lastWordMatch[1] : ''

            if (currentWord.length < extension.options.minChars) {
              return { suggestions: [], selectedIndex: 0, from: null, show: false }
            }

            const raw = extension.options.getSuggestions()
            const all = normalizeSuggestions(raw)
            const matches = all.filter(
              (s) =>
                s.insertText.toLowerCase().startsWith(currentWord.toLowerCase()) &&
                s.insertText.length > currentWord.length,
            )

            if (matches.length === 0) {
              return { suggestions: [], selectedIndex: 0, from: null, show: false }
            }

            return {
              suggestions: matches,
              selectedIndex: prev.selectedIndex >= matches.length ? 0 : prev.selectedIndex,
              from: $head.pos - currentWord.length,
              show: true,
            }
          },
        },

        view(editorView_) {
          editorView = editorView_
          popupEl = document.createElement('div')
          popupEl.className = 'autocomplete-popup'
          popupEl.style.display = 'none'

          document.body.appendChild(popupEl)

          function closePopup() {
            editorView.dispatch(editorView.state.tr.setMeta('autocomplete_close', true))
          }

          function onDocumentMouseDown(e) {
            if (popupEl && !popupEl.contains(e.target)) {
              const pluginState = pluginKey.getState(editorView.state)
              if (pluginState?.show) {
                closePopup()
              }
            }
          }
          document.addEventListener('mousedown', onDocumentMouseDown, true)

          function render(state) {
            if (!state.show || state.suggestions.length === 0) {
              popupEl.style.display = 'none'
              return
            }
            popupEl.style.display = ''

            const grouped = {}
            for (const s of state.suggestions) {
              if (!grouped[s.type]) grouped[s.type] = []
              grouped[s.type].push(s)
            }

            let html = ''
            let globalIndex = 0
            for (const [type, items] of Object.entries(grouped)) {
              const label = type.charAt(0).toUpperCase() + type.slice(1) + (items.length > 1 ? 's' : '')
              html += `<div class="autocomplete-popup__header">${label}</div>`
              for (const item of items) {
                const active = globalIndex === state.selectedIndex ? ' autocomplete-popup__item--active' : ''
                html += `<div class="autocomplete-popup__item${active}" data-index="${globalIndex}">${item.label}</div>`
                globalIndex++
              }
            }
            popupEl.innerHTML = html

            const coords = editorView.coordsAtPos(editorView.state.selection.$head.pos)
            if (coords) {
              popupEl.style.left = `${coords.left}px`
              popupEl.style.top = `${coords.bottom + 4}px`
            }

            popupEl.querySelectorAll('.autocomplete-popup__item').forEach((el) => {
              el.addEventListener('mousedown', (e) => {
                e.preventDefault()
                const idx = parseInt(el.dataset.index, 10)
                const suggestion = state.suggestions[idx]
                if (suggestion) {
                  insertSuggestion(state.from, suggestion.insertText, editorView)
                }
              })
            })
          }

          return {
            update(view) {
              const pluginState = pluginKey.getState(view.state)
              if (pluginState) {
                render(pluginState)
              }
            },
            destroy() {
              document.removeEventListener('mousedown', onDocumentMouseDown, true)
              if (popupEl && popupEl.parentElement) {
                popupEl.parentElement.removeChild(popupEl)
              }
            },
          }
        },

        props: {
          handleKeyDown(view, event) {
            const pluginState = pluginKey.getState(view.state)
            if (!pluginState?.show || pluginState.suggestions.length === 0) return false

            const { suggestions, selectedIndex, from } = pluginState

            if (event.key === 'ArrowDown') {
              event.preventDefault()
              const next = (selectedIndex + 1) % suggestions.length
              view.dispatch(view.state.tr.setMeta('autocomplete_select', next))
              return true
            }

            if (event.key === 'ArrowUp') {
              event.preventDefault()
              const prev = (selectedIndex - 1 + suggestions.length) % suggestions.length
              view.dispatch(view.state.tr.setMeta('autocomplete_select', prev))
              return true
            }

            if (event.key === 'Enter' || event.key === 'Tab') {
              event.preventDefault()
              const suggestion = suggestions[selectedIndex]
              if (suggestion) {
                insertSuggestion(from, suggestion.insertText, view)
              }
              return true
            }

            if (event.key === 'Escape') {
              event.preventDefault()
              view.dispatch(view.state.tr.setMeta('autocomplete_close', true))
              return true
            }

            return false
          },
        },
      }),
    ]
  },
})

export default StoryBibleAutocomplete
