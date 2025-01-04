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
  const loading = ref(false)
  const itemOrder = ref<Record<number, number[]>>({})

  // Actions
  function setCurrentUser(user: User | null) {
    currentUser.value = user
  }

  function setDarkTheme(value: boolean) {
    isDarkTheme.value = value
    localStorage.setItem('theme', value ? 'dark' : 'light')
  }

  function toggleTheme() {
    setDarkTheme(!isDarkTheme.value)
  }

  async function fetchNotifications() {
    try {
      const data = await notificationsService.getNotifications()
      notifications.value = data
    } catch (error) {
      console.error('Failed to fetch notifications:', error)
    }
  }

  async function logout() {
    try {
      await authService.logout()
      currentUser.value = null
      notifications.value = []
      localStorage.removeItem('token')
    } catch (error) {
      console.error('Error during logout:', error)
      throw error
    }
  }

  return {
    currentUser,
    notifications,
    isDarkTheme,
    loading,
    itemOrder,
    setCurrentUser,
    setDarkTheme,
    toggleTheme,
    fetchNotifications,
    logout
  }
})
