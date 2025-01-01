// src/main.ts
import { createApp } from 'vue'
import App from './App.vue'
import './assets/main.css'

// Pinia store
import { createPinia } from 'pinia'

// Vue Router
import router from './router'

// Vuetify
import vuetify from './plugins/vuetify'

// Initialize dark mode based on system preference
if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
  document.documentElement.classList.add('dark')
}

const app = createApp(App)

// Install Pinia
app.use(createPinia())

// Install Vue Router
app.use(router)

// Install Vuetify
app.use(vuetify)

// Mount the app
app.mount('#app')
