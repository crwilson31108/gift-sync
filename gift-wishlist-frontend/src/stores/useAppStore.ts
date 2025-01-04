// src/stores/useAppStore.ts
import { defineStore } from 'pinia'
import type { User, Notification } from '@/types'
import { authService } from '@/services/auth'
import { notificationsService } from '@/services/notifications'

interface AppState {
  currentUser: User | null
  notifications: Notification[]
  isDarkTheme: boolean
  loading: boolean
  itemOrder: Record<number, number[]>
}

export const useAppStore = defineStore('app', {
  state: (): AppState => ({
    currentUser: null,
    notifications: [],
    isDarkTheme: localStorage.getItem('theme') === 'dark',
    loading: false,
    itemOrder: {}
  }),

  getters: {
    unreadNotificationsCount: (state) => 
      state.notifications.filter(n => !n.read).length
  },

  actions: {
    setCurrentUser(user: User) {
      this.currentUser = user
    },

    toggleTheme(value?: boolean) {
      this.isDarkTheme = value ?? !this.isDarkTheme
      localStorage.setItem('theme', this.isDarkTheme ? 'dark' : 'light')
    },

    async logout() {
      try {
        await authService.logout()
        this.currentUser = null
        this.notifications = []
        localStorage.removeItem('token')
      } catch (error) {
        console.error('Logout error:', error)
      }
    },

    async fetchNotifications() {
      try {
        const response = await notificationsService.getNotifications()
        this.notifications = response
      } catch (error) {
        console.error('Failed to fetch notifications:', error)
      }
    },

    // Item ordering actions
    setItemOrder(wishlistId: number, itemIds: number[]) {
      this.itemOrder[wishlistId] = itemIds
    },

    getItemOrder(wishlistId: number) {
      return this.itemOrder[wishlistId] || []
    }
  },

  persist: {
    key: 'gift-wishlist-store',
    storage: localStorage,
    paths: ['isDarkTheme']
  }
})
