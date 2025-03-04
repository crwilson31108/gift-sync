// src/stores/useAppStore.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { notificationsService } from '@/services/notifications'
import { authService } from '@/services/auth'
import api from '@/services/api'

export interface User {
  id: number
  username: string
  email: string
  full_name?: string
  profile_picture?: string
  bio?: string
  avatar?: string
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
  const users = ref<User[]>([])
  const token = ref<string | null>(null)

  // Enhanced initialization function
  async function initializeApp() {
    if (initialized.value) return // Prevent multiple initializations
    
    loading.value = true
    try {
      // Check if we have a token
      const token = localStorage.getItem('token')
      
      if (token) {
        // Validate token by fetching current user
        try {
          const response = await api.get('/users/me/')
          currentUser.value = response.data
          this.token = token
        } catch (error) {
          // If token validation fails, clear everything
          console.error('Token validation failed:', error)
          await logout()
        }
      }
    } catch (error) {
      console.error('Error initializing app:', error)
    } finally {
      initialized.value = true
      loading.value = false
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
      token.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      initialized.value = false
    } catch (error) {
      console.error('Error during logout:', error)
    }
  }

  async function fetchUsers() {
    try {
      const response = await api.get('/users/')
      users.value = response.data
    } catch (error) {
      console.error('Failed to fetch users:', error)
    }
  }

  return {
    currentUser,
    notifications,
    isDarkTheme,
    loading,
    initialized,
    itemOrder,
    users,
    setCurrentUser,
    updateCurrentUser,
    setDarkTheme,
    toggleTheme,
    fetchNotifications,
    logout,
    setItemOrder,
    getItemOrder,
    initializeApp,
    fetchUsers
  }
}, {
  persist: {
    paths: ['isDarkTheme', 'itemOrder'],
    storage: localStorage
  }
})
