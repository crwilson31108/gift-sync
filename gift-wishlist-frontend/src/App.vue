<template>
  <component :is="layout">
    <router-view v-slot="{ Component }">
      <transition 
        name="fade"
        mode="out-in"
      >
        <component :is="Component" class="w-full" />
      </transition>
    </router-view>
  </component>
</template>

<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { useAppStore } from '@/stores/useAppStore'
import { useRoute, useRouter } from 'vue-router'
import { authService } from '@/services/auth'
import api from '@/services/api'
import MainLayout from '@/layouts/MainLayout.vue'
import AuthLayout from '@/layouts/AuthLayout.vue'
import { useTheme } from 'vuetify'

const store = useAppStore()
const route = useRoute()
const router = useRouter()
const theme = useTheme()

// Determine which layout to use
const layout = computed(() => 
  route.path === '/login' ? AuthLayout : MainLayout
)

// Check authentication and theme on mount
onMounted(async () => {
  // Check authentication
  const token = localStorage.getItem('token')
  if (token) {
    try {
      const response = await api.get('/users/me/')
      store.setUser(response.data)
      await store.fetchNotifications()
    } catch (error) {
      console.error('Auth error:', error)
      await store.logout()
      router.push('/login')
    }
  } else if (route.path !== '/login') {
    router.push('/login')
  }

  // Initialize theme from storage
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme) {
    store.toggleTheme(savedTheme === 'dark')
  } else {
    // Use system preference as default
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    store.toggleTheme(prefersDark)
  }
})

// Watch for theme changes
watch(() => store.isDarkTheme, (isDark) => {
  console.log('Theme watcher triggered:', isDark)
  // Update HTML class for Tailwind
  document.documentElement.classList.toggle('dark', isDark)
  console.log('Dark class:', document.documentElement.classList.contains('dark'))
  
  // Update Vuetify theme
  theme.global.name.value = isDark ? 'dark' : 'light'
  console.log('Vuetify theme set to:', theme.global.name.value)
}, { immediate: true })
</script>

<style>
/* Ensure content doesn't overflow during transitions */
.v-main {
  @apply overflow-x-hidden;
}

/* Simple fade transition */
.fade-enter-active,
.fade-leave-active {
  @apply transition-opacity duration-150 ease-linear;
}

.fade-enter-from,
.fade-leave-to {
  @apply opacity-0;
}

/* Prevent interaction during transition */
.fade-enter-active *,
.fade-leave-active * {
  pointer-events: none;
}

/* Custom scrollbar */
::-webkit-scrollbar {
  @apply w-2;
}

::-webkit-scrollbar-track {
  @apply bg-light-surface dark:bg-dark-surface;
}

::-webkit-scrollbar-thumb {
  @apply bg-light-border dark:bg-dark-border rounded hover:bg-light-subtle dark:hover:bg-dark-subtle transition-colors;
}

/* Optimize performance */
* {
  @apply subpixel-antialiased;
}

/* Improved transitions */
.v-navigation-drawer {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Global theme transitions */
body,
.v-application {
  transition: background-color 0.3s ease, color 0.3s ease;
}

/* Theme-specific styles */
:root {
  color-scheme: light dark;
}

.v-theme--light {
  --v-theme-overlay-multiplier: 0.8;
}

.v-theme--dark {
  --v-theme-overlay-multiplier: 0.9;
}
</style>
