<template>
  <v-app>
    <!-- Show loading state while initializing -->
    <div v-if="store.loading && !store.initialized" class="app-loading">
      <LoadingAnimation message="Getting things ready..." />
    </div>

    <!-- Show app content when initialized -->
    <template v-else>
      <component :is="layout">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </component>
    </template>
  </v-app>
</template>

<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { useAppStore } from '@/stores/useAppStore'
import { useRoute, useRouter } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'
import AuthLayout from '@/layouts/AuthLayout.vue'
import { useTheme } from 'vuetify'
import LoadingAnimation from '@/components/LoadingAnimation.vue'

const store = useAppStore()
const route = useRoute()
const theme = useTheme()

// Define public routes at the top level
const publicRoutes = ['/login', '/request-password-reset', '/reset-password']
const isPublicRoute = (path: string) => 
  publicRoutes.some(route => path.startsWith(route))

// Determine which layout to use
const layout = computed(() => {
  return isPublicRoute(route.path) ? AuthLayout : MainLayout
})

// Initialize on mount
onMounted(async () => {
  await store.initializeApp()
})

// Watch for theme changes
watch(() => store.isDarkTheme, (isDark) => {
  document.documentElement.classList.toggle('dark', isDark)
  theme.global.name.value = isDark ? 'dark' : 'light'
}, { immediate: true })
</script>

<style>
.loading-screen {
  @apply min-h-screen flex items-center justify-center bg-light-bg dark:bg-dark-bg;
}

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

/* Add to your existing styles */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.3s cubic-bezier(1, 0.5, 0.8, 1);
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateY(20px);
  opacity: 0;
}

/* Smooth page transitions */
.page-enter-active,
.page-leave-active {
  transition: opacity 0.5s ease;
}

.page-enter-from,
.page-leave-to {
  opacity: 0;
}

/* Ensure smooth theme transitions */
* {
  transition-property: color, background-color, border-color;
  transition-duration: 0.3s;
  transition-timing-function: ease;
}
</style>

<style scoped>
.app-loading {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgb(var(--v-theme-background));
  z-index: 9999;
}
</style>

