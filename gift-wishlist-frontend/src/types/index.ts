export interface User {
  id: number
  username: string
  email: string
  profile_picture?: string | null
  bio?: string
}

export interface Notification {
  id: number
  user: number
  type: 'new_item' | 'purchased' | 'wishlist_created'
  target_id: number
  read: boolean
  created_at: string
} 