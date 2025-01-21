// src/main.ts
import { createApp } from 'vue'
import App from './App.vue'
import './assets/main.css'

// Pinia store
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

// Vue Router
import router from './router'

// Vuetify
import vuetify from './plugins/vuetify'

// Stores
import { useAppStore } from './stores/useAppStore'

// Initialize dark mode based on system preference
if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
  document.documentElement.classList.add('dark')
}

const app = createApp(App)

// Initialize Pinia with persistence
const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)
app.use(pinia)

// Install Vue Router
app.use(router)

// Install Vuetify
app.use(vuetify)

// Initialize store
const store = useAppStore()

// Setup navigation guards
router.beforeEach(async (to, from, next) => {
  // Wait for initial auth check if not completed
  if (store.loading) {
    await store.initializeApp()
  }

  const isAuthenticated = !!store.currentUser
  const requiresAuth = to.meta.requiresAuth !== false

  if (requiresAuth && !isAuthenticated) {
    // Save intended destination
    localStorage.setItem('redirectPath', to.fullPath)
    next('/login')
  } else if (to.path === '/login' && isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

// Mount app after initialization
store.initializeApp().then(() => {
  app.mount('#app')
})
