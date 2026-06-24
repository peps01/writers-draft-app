import { Plugin, PluginKey } from '@tiptap/pm/state'
import { Decoration, DecorationSet } from '@tiptap/pm/view'
import { Extension } from '@tiptap/core'

export const findReplaceKey = new PluginKey('find-replace')

function createFindReplacePlugin() {
  return new Plugin({
    key: findReplaceKey,
    state: {
      init() {
        return DecorationSet.empty
      },
      apply(tr, old) {
        const meta = tr.getMeta(findReplaceKey)
        if (meta !== undefined) {
          if (meta.length === 0) {
            return DecorationSet.empty
          }
          const decorations = meta.map((r) =>
            Decoration.inline(r.from, r.to, {
              class: r.current ? 'search-result-current' : 'search-result',
            }),
          )
          return DecorationSet.create(tr.doc, decorations)
        }
        return old.map(tr.mapping, tr.doc)
      },
    },
    props: {
      decorations(state) {
        return findReplaceKey.getState(state)
      },
    },
  })
}

export const FindReplaceExtension = Extension.create({
  name: 'findReplace',
  addProseMirrorPlugins() {
    return [createFindReplacePlugin()]
  },
})
