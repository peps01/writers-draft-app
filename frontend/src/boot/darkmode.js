import { Dark } from 'quasar'

export default () => {
  const saved = localStorage.getItem('wda_dark_mode')
  if (saved === 'true') {
    Dark.set(true)
  }
}
