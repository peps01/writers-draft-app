import { boot } from 'quasar/wrappers'
import { useAuthStore } from '@/stores/auth'

export default boot(async () => {
  const authStore = useAuthStore()
  await authStore.fetchCurrentUser()
})
