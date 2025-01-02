import api from './api'
import type { User } from '@/types'

export interface Family {
  id: number
  name: string
  members: User[]
  created_at: string
  updated_at: string
}

export interface CreateFamilyData {
  name: string
  member_ids?: number[]
}

export const familiesService = {
  async getFamilies() {
    const response = await api.get<Family[]>('/families/')
    return response.data
  },

  async getFamily(id: number) {
    const response = await api.get<Family>(`/families/${id}/`)
    return response.data
  },

  async createFamily(data: CreateFamilyData) {
    const response = await api.post<Family>('/families/', data)
    return response.data
  },

  async updateFamily(id: number, data: Partial<CreateFamilyData>) {
    const response = await api.patch<Family>(`/families/${id}/`, data)
    return response.data
  },

  async deleteFamily(id: number) {
    await api.delete(`/families/${id}/`)
  },

  async addMember(familyId: number, userId: number) {
    const response = await api.post<Family>(`/families/${familyId}/add_member/`, {
      user_id: userId
    })
    return response.data
  },

  async removeMember(familyId: number, userId: number) {
    const response = await api.post<Family>(`/families/${familyId}/remove_member/`, {
      user_id: userId
    })
    return response.data
  }
} 