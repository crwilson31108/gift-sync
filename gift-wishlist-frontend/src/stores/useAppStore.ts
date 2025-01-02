// src/stores/useAppStore.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User, Notification } from '@/types'
import { authService } from '@/services/auth'
import { notificationsService } from '@/services/notifications'

export const useAppStore = defineStore('app', () => {
  const currentUser = ref<User | null>(null)
  const notifications = ref<Notification[]>([])
  const isDarkTheme = ref(localStorage.getItem('theme') === 'dark')
  const loading = ref(false)

  function setUser(user: User | null) {
    currentUser.value = user
  }

  function toggleTheme(value?: boolean) {
    console.log('Previous theme state:', isDarkTheme.value)
    // If value is provided, use it; otherwise toggle current value
    isDarkTheme.value = value ?? !isDarkTheme.value
    console.log('New theme state:', isDarkTheme.value)
    // Store the preference
    localStorage.setItem('theme', isDarkTheme.value ? 'dark' : 'light')
    console.log('Theme saved to localStorage:', localStorage.getItem('theme'))
  }

  async function logout() {
    try {
      await authService.logout()
      currentUser.value = null
      notifications.value = []
      localStorage.removeItem('token')
    } catch (error) {
      console.error('Logout error:', error)
    }
  }

  async function fetchNotifications() {
    try {
      const response = await notificationsService.getNotifications()
      notifications.value = response
    } catch (error) {
      console.error('Failed to fetch notifications:', error)
    }
  }

  return {
    currentUser,
    notifications,
    isDarkTheme,
    loading,
    setUser,
    toggleTheme,
    logout,
    fetchNotifications
  }
}, {
  persist: {
    key: 'gift-wishlist-store',
    storage: localStorage,
    paths: ['isDarkTheme']
  }
})
