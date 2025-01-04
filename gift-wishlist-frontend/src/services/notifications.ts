import api from '@/services/api'
import type { Notification } from '@/types'

export const notificationsService = {
  async getNotifications() {
    const { data } = await api.get<Notification[]>('/notifications/')
    return data
  },

  async markAsRead(notificationId: number) {
    const { data } = await api.patch(`/notifications/${notificationId}/read/`)
    return data
  },

  async markAllAsRead() {
    const { data } = await api.patch('/notifications/mark-all-read/')
    return data
  }
} 