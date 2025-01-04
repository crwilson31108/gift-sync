import api from './api'
import type { User } from '@/types'

export interface WishListItem {
  id: number
  title: string
  description: string
  price: string
  link: string
  image: string | null    // For uploaded images
  image_url: string       // For scraped images
  size: string
  priority: number
  is_purchased: boolean
  purchased_by?: User
  purchased_at?: string
  created_at: string
  updated_at: string
  wishlist: number
}

export interface WishList {
  id: number
  name: string
  owner: User
  family: number
  items: WishListItem[]
  created_at: string
  updated_at: string
}

export interface CreateWishListData {
  name: string
  family: number
}

export interface CreateWishListItemData {
  title: string
  description?: string
  price: number
  link?: string
  image_url?: string
  size?: 'Small' | 'Medium' | 'Large'
  priority?: number
  wishlist: number
}

export const wishlistsService = {
  async getWishlists(params?: { family?: number, owner?: number }) {
    const response = await api.get<WishList[]>('/wishlists/', { params })
    return response.data
  },

  async getWishlist(id: number) {
    const response = await api.get<WishList>(`/wishlists/${id}/`)
    return response.data
  },

  async createWishlist(data: CreateWishListData) {
    const response = await api.post<WishList>('/wishlists/', data)
    return response.data
  },

  async updateWishlist(id: number, data: Partial<CreateWishListData>) {
    const response = await api.patch<WishList>(`/wishlists/${id}/`, data)
    return response.data
  },

  async deleteWishlist(id: number) {
    await api.delete(`/wishlists/${id}/`)
  },

  // Wishlist Items
  async createItem(data: FormData) {
    const response = await api.post<WishListItem>('/wishlist-items/', data, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  async updateItem(id: number, data: FormData) {
    const response = await api.patch<WishListItem>(`/wishlist-items/${id}/`, data, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  async deleteItem(id: number) {
    await api.delete(`/wishlist-items/${id}/`)
  },

  async purchaseItem(id: number) {
    const response = await api.post<WishListItem>(`/wishlist-items/${id}/purchase/`)
    return response.data
  },

  async unpurchaseItem(id: number) {
    const response = await api.post<WishListItem>(`/wishlist-items/${id}/unpurchase/`)
    return response.data
  },

  async scrapeUrl(url: string) {
    const response = await api.post<{
      title?: string
      description?: string
      price?: number
      image_url?: string
    }>('/wishlist-items/scrape_url/', { url })
    return response.data
  },

  async getStats() {
    const response = await api.get('/wishlists/stats/')
    return response.data
  },

  async getRecentActivity() {
    const response = await api.get('/wishlists/recent_activity/')
    return response.data
  },

  async updateItemsOrder(wishlistId: number, itemIds: number[]) {
    const response = await api.post(
      `/wishlist-items/reorder_items/`,
      { 
        wishlist_id: wishlistId,
        item_ids: itemIds 
      }
    )
    return response.data
  }
} 