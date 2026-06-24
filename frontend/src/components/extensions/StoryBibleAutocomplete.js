import { Extension } from '@tiptap/core'
import { Plugin, PluginKey } from '@tiptap/pm/state'
import { Decoration, DecorationSet } from '@tiptap/pm/view'

const StoryBibleAutocomplete = Extension.create({
  name: 'storyBibleAutocomplete',

  addOptions() {
    return {
      getSuggestions: () => [],
      minChars: 4,
    }
  },

  addProseMirrorPlugins() {
    const extension = this

    return [
      new Plugin({
        key: new PluginKey('storyBibleAutocomplete'),

        state: {
          init() {
            return {
              decorations: DecorationSet.empty,
              suggestion: null,
            }
          },
          apply(tr, prev, oldState, newState) {
            const { selection } = newState
            const { $head } = selection

            if (!selection.empty) {
              return { decorations: DecorationSet.empty, suggestion: null }
            }

            const textBefore = newState.doc.textBetween(0, $head.pos)
            const lastWordMatch = textBefore.match(/(\S+)$/)
            const currentWord = lastWordMatch ? lastWordMatch[1] : ''

            if (currentWord.length < extension.options.minChars) {
              return { decorations: DecorationSet.empty, suggestion: null }
            }

            const suggestions = extension.options.getSuggestions()
            const matches = suggestions.filter(
              (s) =>
                s.toLowerCase().startsWith(currentWord.toLowerCase()) &&
                s.length > currentWord.length,
            )
            if (matches.length === 0) {
              return { decorations: DecorationSet.empty, suggestion: null }
            }
            const match = matches.sort((a, b) => a.length - b.length)[0]

            if (!match) {
              return { decorations: DecorationSet.empty, suggestion: null }
            }

            const completion = match.slice(currentWord.length)
            const suggestion = {
              from: $head.pos,
              to: $head.pos,
              text: currentWord,
              completion,
              fullMatch: match,
            }

            const ghostEl = document.createElement('span')
            ghostEl.className = 'autocomplete-ghost'
            ghostEl.textContent = completion
            ghostEl.style.cssText =
              'color: rgba(0,0,0,0.3); pointer-events: none; user-select: none; font-style: italic; white-space: pre;'

            const deco = Decoration.widget($head.pos, ghostEl, { side: 1 })
            const decorations = DecorationSet.create(newState.doc, [deco])

            return { decorations, suggestion }
          },
        },

        props: {
          decorations(state) {
            return this.getState(state).decorations
          },
          handleKeyDown(view, event) {
            const pluginState = this.getState(view.state)
            if (!pluginState.suggestion) return false

            if (event.key === 'Tab' || event.key === 'ArrowRight') {
              event.preventDefault()
              const { from, completion } = pluginState.suggestion
              const { tr } = view.state
              tr.insertText(completion, from)
              view.dispatch(tr)
              return true
            }

            if (
              event.key.length === 1 ||
              event.key === 'Backspace' ||
              event.key === 'Escape' ||
              event.key === 'Enter'
            ) {
              return false
            }

            return false
          },
        },
      }),
    ]
  },
})

export default StoryBibleAutocomplete
