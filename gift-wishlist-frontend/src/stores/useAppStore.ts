// src/stores/useAppStore.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { notificationsService } from '@/services/notifications'
import { authService } from '@/services/auth'

export interface User {
  id: number
  username: string
  email: string
  full_name?: string
  profile_picture?: string
  bio?: string
}

export interface Notification {
  id: number
  type: string
  target_id: number
  read: boolean
  created_at: string
}

export const useAppStore = defineStore('app', () => {
  const currentUser = ref<User | null>(null)
  const notifications = ref<Notification[]>([])
  const isDarkTheme = ref(false)
  const loading = ref(true)
  const initialized = ref(false)
  const itemOrder = ref<Record<number, number[]>>({})

  // Enhanced initialization function
  async function initializeApp() {
    if (initialized.value) return // Prevent multiple initializations
    
    loading.value = true
    try {
      // Setup API with token if exists
      authService.setupApiWithToken()
      
      // Check for stored auth token and validate
      const token = authService.getToken()
      if (token) {
        try {
          const user = await authService.validateToken()
          currentUser.value = user
          // Optionally fetch notifications here if needed
          await fetchNotifications()
        } catch (error) {
          console.error('Token validation failed:', error)
          await logout()
        }
      }
    } catch (error) {
      console.error('App initialization error:', error)
      await logout()
    } finally {
      loading.value = false
      initialized.value = true // Set initialized to true when done
    }
  }

  // Actions
  function setCurrentUser(user: User | null) {
    currentUser.value = user
  }

  async function updateCurrentUser(userData: Partial<User>) {
    if (currentUser.value) {
      currentUser.value = { ...currentUser.value, ...userData }
    }
  }

  function setDarkTheme(value: boolean) {
    isDarkTheme.value = value
    localStorage.setItem('theme', value ? 'dark' : 'light')
  }

  function toggleTheme() {
    setDarkTheme(!isDarkTheme.value)
  }

  // Add these functions for item order management
  function setItemOrder(wishlistId: number, ids: number[]) {
    itemOrder.value[wishlistId] = ids
  }

  function getItemOrder(wishlistId: number): number[] {
    return itemOrder.value[wishlistId] || []
  }

  async function fetchNotifications() {
    try {
      const data = await notificationsService.getNotifications()
      notifications.value = data
    } catch (error) {
      console.error('Failed to fetch notifications:', error)
    }
  }

  // Enhanced logout function
  async function logout() {
    try {
      await authService.logout()
      currentUser.value = null
      notifications.value = []
    } catch (error) {
      console.error('Error during logout:', error)
    }
  }

  return {
    currentUser,
    notifications,
    isDarkTheme,
    loading,
    initialized,
    itemOrder,
    setCurrentUser,
    updateCurrentUser,
    setDarkTheme,
    toggleTheme,
    fetchNotifications,
    logout,
    setItemOrder,
    getItemOrder,
    initializeApp
  }
}, {
  persist: {
    paths: ['isDarkTheme', 'itemOrder'],
    storage: localStorage
  }
})
