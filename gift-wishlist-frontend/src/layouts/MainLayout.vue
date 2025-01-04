<template>
  <v-app :theme="store.isDarkTheme ? 'dark' : 'light'" class="min-h-screen">
    <!-- Main Sidebar -->
    <v-navigation-drawer
      v-if="!$vuetify.display.mobile"
      v-model="showSidebar"
      :rail="sidebarMini"
      permanent
      :class="[
        store.isDarkTheme ? 'bg-dark-surface border-dark-border' : 'bg-light-surface border-light-border',
        'border-r border-opacity-10 h-screen'
      ]"
      :rail-width="80"
      width="280"
    >
      <!-- Logo Section -->
      <div class="px-4 py-3">
        <div :class="sidebarMini ? 'flex flex-col items-center' : 'flex items-center justify-between'">
          <template v-if="sidebarMini">
            <img 
              src="@/assets/logo/logo-mini.png" 
              alt="Gift Sync"
              class="w-12 h-12 object-contain object-center mb-2"
              @error="handleImageError"
            />
            <v-btn
              icon
              variant="text"
              size="small"
              class="text-light-subtle dark:text-dark-subtle mt-2"
              @click.stop="sidebarMini = !sidebarMini"
            >
              <v-icon>mdi-chevron-right</v-icon>
            </v-btn>
          </template>
          <template v-else>
            <img 
              src="@/assets/logo/logo.png" 
              alt="Gift Sync Logo"
              class="w-40 h-auto object-contain object-center"
              @error="handleImageError"
            />
            <v-btn
              icon
              variant="text"
              size="small"
              class="text-light-subtle dark:text-dark-subtle"
              @click.stop="sidebarMini = !sidebarMini"
            >
              <v-icon>mdi-chevron-left</v-icon>
            </v-btn>
          </template>
        </div>
      </div>

      <v-divider class="border-accent/10 my-2" />

      <!-- Navigation Links -->
      <v-list class="px-2">
        <v-list-item
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          :value="item.path"
          :exact="item.path === '/'"
          class="mb-1 rounded-lg text-light-text dark:text-dark-text hover:bg-light-surface/80 dark:hover:bg-dark-surface/80"
          active-class="bg-primary/10 text-primary dark:text-primary"
        >
          <template v-slot:prepend>
            <v-icon 
              :icon="item.icon" 
              class="text-light-subtle dark:text-dark-subtle"
              :class="{ 'text-primary dark:text-primary': $route.path === item.path }"
            />
          </template>
          <v-list-item-title>{{ item.title }}</v-list-item-title>
        </v-list-item>
      </v-list>

      <!-- Bottom Actions -->
      <template v-slot:append>
        <div class="px-4 py-3">
          <v-divider class="border-accent/10 mb-3" />
          <div class="flex items-center space-x-3">
            <v-avatar
              :size="sidebarMini ? 40 : 45"
              color="primary"
            >
              <v-img
                v-if="store.currentUser?.avatar"
                :src="store.currentUser.avatar"
                alt="User Avatar"
              />
              <span v-else class="text-white text-lg">
                {{ userInitials }}
              </span>
            </v-avatar>
            <div v-if="!sidebarMini" class="flex-1 min-w-0">
              <p class="text-sm font-medium text-light-text dark:text-dark-text truncate">
                {{ store.currentUser?.username ?? 'User' }}
              </p>
              <p class="text-xs text-light-subtle dark:text-dark-subtle truncate">
                {{ store.currentUser?.email ?? 'user@example.com' }}
              </p>
            </div>
            <v-menu
              location="top"
              offset="10"
            >
              <template v-slot:activator="{ props }">
                <v-btn
                  icon="mdi-dots-vertical"
                  variant="text"
                  size="small"
                  v-bind="props"
                  class="text-light-subtle dark:text-dark-subtle"
                />
              </template>
              <v-list width="200" class="py-2">
                <v-list-item
                  prepend-icon="mdi-account-outline"
                  title="Profile"
                  to="/profile"
                />
                <v-divider class="my-2" />
                <v-list-item
                  prepend-icon="mdi-logout"
                  title="Sign Out"
                  @click="handleLogout"
                />
              </v-list>
            </v-menu>
          </div>
        </div>
      </template>
    </v-navigation-drawer>

    <!-- Top App Bar -->
    <v-app-bar
      v-if="!$vuetify.display.mobile"
      :class="[
        store.isDarkTheme ? 'bg-dark-surface border-dark-border' : 'bg-light-surface border-light-border',
        'border-b border-opacity-10'
      ]"
      flat
    >
      <v-container class="max-w-7xl mx-auto px-4 py-2">
        <div class="flex items-center justify-between w-full">
          <!-- Breadcrumbs -->
          <v-breadcrumbs
            :items="breadcrumbs"
            class="px-0"
          >
            <template v-slot:divider>
              <v-icon icon="mdi-chevron-right" size="small"></v-icon>
            </template>
            <template v-slot:title="{ item }">
              <span class="text-light-text dark:text-dark-text">{{ item.title }}</span>
            </template>
          </v-breadcrumbs>
          
          <!-- Right Actions -->
          <div class="flex items-center space-x-4">
            <!-- Notifications -->
            <v-menu location="bottom end">
              <template v-slot:activator="{ props }">
                <v-btn
                  icon
                  v-bind="props"
                  class="text-light-subtle dark:text-dark-subtle"
                >
                  <v-badge
                    :content="unreadNotificationsCount"
                    :model-value="unreadNotificationsCount > 0"
                    color="primary"
                  >
                    <v-icon>mdi-bell</v-icon>
                  </v-badge>
                </v-btn>
              </template>
              <v-list width="320" class="py-2">
                <v-list-subheader>Notifications</v-list-subheader>
                <template v-if="recentNotifications.length">
                  <v-list-item
                    v-for="notification in recentNotifications"
                    :key="notification.id"
                    :to="getNotificationLink(notification)"
                    :class="{ 'bg-primary/5': !notification.read }"
                  >
                    <template v-slot:prepend>
                      <v-avatar color="primary" size="32">
                        <span class="text-xs">{{ getUserInitials(notification.user) }}</span>
                      </v-avatar>
                    </template>
                    <v-list-item-title class="text-sm">
                      {{ getUserName(notification.user) }}
                      {{ getNotificationText(notification) }}
                    </v-list-item-title>
                    <v-list-item-subtitle class="text-xs">
                      {{ formatDate(notification.created_at) }}
                    </v-list-item-subtitle>
                  </v-list-item>
                  <v-divider class="my-2" />
                </template>
                <v-list-item
                  to="/notifications"
                  prepend-icon="mdi-bell-outline"
                >
                  View All Notifications
                </v-list-item>
              </v-list>
            </v-menu>
            
            <!-- Theme Toggle -->
            <v-btn
              icon
              @click="handleThemeToggle"
              class="text-light-subtle dark:text-dark-subtle"
            >
              <v-icon>{{ store.isDarkTheme ? 'mdi-weather-night' : 'mdi-weather-sunny' }}</v-icon>
            </v-btn>
          </div>
        </div>
      </v-container>
    </v-app-bar>

    <!-- Mobile Top Bar -->
    <v-app-bar
      v-if="$vuetify.display.mobile"
      :class="[
        store.isDarkTheme ? 'bg-dark-surface border-dark-border' : 'bg-light-surface border-light-border',
        'border-b border-opacity-10'
      ]"
      flat
    >
      <v-app-bar-title class="text-primary font-bold">Gift Sync</v-app-bar-title>
      <div class="flex items-center space-x-2">
        <!-- Notifications -->
        <v-btn
          icon
          class="text-light-subtle dark:text-dark-subtle"
        >
          <v-badge
            :content="unreadNotificationsCount"
            color="primary"
            offset-x="3"
            offset-y="3"
          >
            <v-icon>mdi-bell-outline</v-icon>
          </v-badge>
        </v-btn>
        <!-- Theme Toggle -->
        <v-btn
          icon
          variant="text"
          @click="handleThemeToggle"
          class="text-light-subtle dark:text-dark-subtle"
        >
          <v-icon>{{ store.isDarkTheme ? 'mdi-weather-sunny' : 'mdi-weather-night' }}</v-icon>
        </v-btn>
      </div>
    </v-app-bar>

    <!-- Mobile Bottom Navigation -->
    <v-bottom-navigation
      v-if="$vuetify.display.mobile"
      v-model="currentRoute"
      :class="[
        store.isDarkTheme ? 'bg-dark-surface border-dark-border' : 'bg-light-surface border-light-border',
        'border-t border-opacity-10'
      ]"
      grow
    >
      <v-btn
        v-for="item in menuItems.slice(0, 5)"
        :key="item.path"
        :to="item.path"
        :value="item.path"
        class="text-light-subtle dark:text-dark-subtle"
        :class="{ 'text-primary dark:text-primary': $route.path === item.path }"
      >
        <v-icon :icon="item.icon" />
        <span class="text-xs mt-1">{{ item.title }}</span>
      </v-btn>
    </v-bottom-navigation>

    <!-- Main Content -->
    <v-main 
      :class="store.isDarkTheme ? 'bg-dark-bg' : 'bg-light-bg'"
      ref="mainContent"
    >
      <div 
        :class="[
          'max-w-7xl mx-auto px-4 py-6 min-h-screen pb-16 md:pb-6',
          store.isDarkTheme ? 'bg-dark-bg' : 'bg-light-bg'
        ]"
      >
        <slot />
      </div>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useAppStore } from '@/stores/useAppStore'
import { useRoute, useRouter } from 'vue-router'
import { format } from 'date-fns'

const store = useAppStore()
const route = useRoute()
const router = useRouter()
const currentRoute = ref(route.path)

const showSidebar = ref(true)
const sidebarMini = ref(false)

const menuItems = [
  { title: 'Home', path: '/', icon: 'mdi-home' },
  { title: 'Families', path: '/families', icon: 'mdi-account-group' },
  { title: 'Members', path: '/members', icon: 'mdi-account-multiple' },
  { title: 'Wishlists', path: '/wishlists', icon: 'mdi-gift' }
]

// Computed properties for user info
const userInitials = computed(() => {
  if (!store.currentUser) return ''
  return store.currentUser.username
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
})

// Computed properties for notifications
const unreadNotificationsCount = computed(() => 
  store.notifications.filter(n => !n.read).length
)

// First, let's add proper typing for notifications
interface Notification {
  id: number
  user: number // The user who triggered the notification
  type: 'new_item' | 'purchased' | 'wishlist_created'
  target_id: number
  read: boolean
  created_at: string
}

const recentNotifications = computed(() => 
  [...store.notifications]
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 5)
)

// Helper functions
function getUserName(userId: number) {
  if (userId === store.currentUser?.id) return 'You'
  const user = store.users?.find(u => u.id === userId)
  return user?.full_name || 'Unknown'
}

function getUserInitials(userId: number): string {
  const name = getUserName(userId)
  return name
    .split(' ')
    .map((n: string) => n[0])
    .join('')
    .toUpperCase()
}

function getNotificationText(notification: any) {
  switch (notification.type) {
    case 'new_item':
      return 'added a new item to their wishlist'
    case 'purchased':
      return 'purchased an item from wishlist'
    case 'wishlist_created':
      return 'created a new wishlist'
    default:
      return ''
  }
}

function getNotificationLink(notification: Notification) {
  switch (notification.type) {
    case 'new_item':
    case 'wishlist_created':
      return `/wishlists/${notification.target_id}`
    case 'purchased':
      return `/wishlists/${notification.target_id}`
    default:
      return '/'
  }
}

// Compute breadcrumbs based on current route
const breadcrumbs = computed(() => {
  const pathParts = route.path.split('/').filter(Boolean)
  const items = [
    {
      title: 'Home',
      disabled: false,
      to: '/',
    }
  ]
  
  let path = ''
  pathParts.forEach(part => {
    path += `/${part}`
    items.push({
      title: part.charAt(0).toUpperCase() + part.slice(1),
      disabled: path === route.path,
      to: path,
    })
  })
  
  return items
})

function formatDate(date: string | null | undefined) {
  if (!date) return ''
  try {
    return format(new Date(date), 'MMM d, yyyy')
  } catch (error) {
    console.error('Invalid date:', date)
    return ''
  }
}

function handleImageError(e: Event) {
  const img = e.target as HTMLImageElement
  img.style.display = 'none'
  console.error('Failed to load logo')
}

// Add this computed property
const currentTheme = computed(() => store.isDarkTheme ? 'dark' : 'light')

function handleThemeToggle() {
  console.log('Theme toggle clicked')
  store.toggleTheme()
}

// Add a watch on the route to scroll to top on route change
watch(
  () => route.path,
  () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    })
    
    // If using v-main, also reset its scroll position
    const mainContent = document.querySelector('.v-main__wrap')
    if (mainContent) {
      mainContent.scrollTop = 0
    }
  }
)

async function handleLogout() {
  try {
    await store.logout()
    router.push('/login')
  } catch (error) {
    console.error('Logout failed:', error)
    // Optionally add error handling/user notification here
  }
}
</script> 

<style>
/* Add these theme utility classes */
.bg-light-surface {
  background-color: #FFFFFF;
}

.bg-dark-surface {
  background-color: #1E1E1E;
}

.bg-light-bg {
  background-color: #F5F5F5;
}

.bg-dark-bg {
  background-color: #121212;
}

.border-light-border {
  border-color: rgba(0, 0, 0, 0.12);
}

.border-dark-border {
  border-color: rgba(255, 255, 255, 0.12);
}

/* Add transition for smooth theme switching */
.v-application {
  transition: background-color 0.3s ease;
}

.v-main {
  transition: background-color 0.3s ease;
}

/* Add these new styles */
.v-navigation-drawer {
  height: 100vh !important;
  position: fixed !important;
}

.v-main {
  margin-left: var(--v-navigation-drawer-width) !important;
  min-height: 100vh !important;
}

@media (max-width: 960px) {
  .v-main {
    margin-left: 0 !important;
  }
}
</style> 

<style scoped>
/* Add these styles */
.v-main {
  overflow-y: auto;
  overflow-x: hidden;
}

.v-main__wrap {
  scroll-behavior: smooth;
}
  
</style> 