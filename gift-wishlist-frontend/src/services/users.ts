import api from './api'
import type { User } from '@/types'

export const usersService = {
  async getMembers() {
    const response = await api.get<User[]>('/users/')
    return response.data
  },

  async searchUsers(query: string) {
    const response = await api.get<User[]>(`/users/search/?q=${query}`)
    return response.data
  },

  async getCurrentUser() {
    const response = await api.get<User>('/users/me/')
    return response.data
  }
} 