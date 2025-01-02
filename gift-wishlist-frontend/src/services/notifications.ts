import api from './api'
import type { Notification } from '@/types'

export const notificationsService = {
  async getNotifications() {
    const response = await api.get<Notification[]>('/notifications/')
    return response.data
  },

  async markAllAsRead() {
    await api.post('/notifications/mark_all_read/')
  }
} 