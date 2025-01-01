// src/stores/useAppStore.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// Data Models
export interface User {
  id: number
  name: string
  email: string
  avatar?: string | null
}

export interface GiftItem {
  id: number
  title: string
  link: string
  size: 'Small' | 'Medium' | 'Large'
  price: number
  isPurchased: boolean
  purchasedBy?: number  // User ID of who purchased it
  purchasedAt?: Date
  imageUrl?: string | undefined | null
}

export interface Wishlist {
  id: number
  ownerId: number
  familyId: number
  name: string
  items: GiftItem[]
}

export interface Family {
  id: number
  name: string
  members: number[]  // Array of user IDs
}

export interface Invitation {
  id: number
  email: string
  familyId: number
  status: 'pending' | 'accepted' | 'declined'
  createdAt: Date
}

export interface WishlistFilters {
  familyId?: number
  ownerId?: number
  status?: 'all' | 'active' | 'completed'
}

export interface Notification {
  id: number
  type: 'new_item' | 'purchased' | 'wishlist_created'
  userId: number // who triggered the notification
  targetId: number // wishlist or item id
  read: boolean
  createdAt: Date
}

export const useAppStore = defineStore('appStore', () => {
  // Mock data
  const families = ref<Family[]>([
    {
      id: 1,
      name: 'Estakhri-Valdez-Wilson',
      members: [101, 102, 103, 104, 105],
    }
  ])

  const users = ref<User[]>([
    { 
      id: 101, 
      name: 'Casey Wilson',
      email: 'casey.wilson@example.com',
      avatar: null
    },
    { 
      id: 102, 
      name: 'Meriah Estakhri',
      email: 'meriah.estakhri@example.com',
      avatar: null
    },
    { 
      id: 103, 
      name: 'Pej Estakhri',
      email: 'pej.estakhri@example.com',
      avatar: null
    },
    { 
      id: 104, 
      name: 'Yvonne Wilson',
      email: 'yvonne.wilson@example.com',
      avatar: null
    },
    { 
      id: 105, 
      name: 'Blanca Valdes',
      email: 'blanca.valdes@example.com',
      avatar: null
    }
  ])

  const wishlists = ref<Wishlist[]>([
    {
      id: 1,
      ownerId: 102, // Meriah's wishlist
      familyId: 1,
      name: "Meriah's Christmas Wishlist",
      items: [
        {
          id: 1,
          title: "Running Shoes",
          price: 129.99,
          size: "Large",
          link: "https://example.com/shoes",
          imageUrl: "https://encrypted-tbn3.gstatic.com/shopping?q=tbn:ANd9GcTz3IlFj--MWNfpfUqe0ndKgXwXcY2hKmZK5itIcfDSYRsVqyYgdTeBcdbPq1WPBqG8DbU1dGrV8ChVkdfT7fha-i4niddI2Fb-9Q-EIR6c4n6muqSEzgpsBy4",
          isPurchased: true,
          purchasedBy: 103, // Pej
          purchasedAt: new Date('2024-03-15')
        },
        {
          id: 2,
          title: "Bluetooth Headphones",
          price: 199.99,
          size: "Large",
          link: "https://example.com/headphones",
          imageUrl: "https://encrypted-tbn2.gstatic.com/shopping?q=tbn:ANd9GcQ-jhxxU2nmeekRkOnEfshNkURBGsXLXh9gjMT_J1cqomt23clThSKxXxOHNzUg0ymp30eNhwnLmbZKUXxgo6MKVLFcM4fBLLWAOtEQpcbWZTRvMUBBhY2y",
          isPurchased: false
        }
      ]
    },
    {
      id: 2,
      ownerId: 101, // Casey's wishlist
      familyId: 1,
      name: "Casey's Christmas Wishlist",
      items: [
        {
          id: 1,
          title: "Running Shoes",
          price: 129.99,
          size: "Large",
          link: "https://example.com/shoes",
          imageUrl: "https://encrypted-tbn3.gstatic.com/shopping?q=tbn:ANd9GcTz3IlFj--MWNfpfUqe0ndKgXwXcY2hKmZK5itIcfDSYRsVqyYgdTeBcdbPq1WPBqG8DbU1dGrV8ChVkdfT7fha-i4niddI2Fb-9Q-EIR6c4n6muqSEzgpsBy4",
          isPurchased: false
        },
        {
          id: 2,
          title: "Bluetooth Headphones",
          price: 199.99,
          size: "Large",
          link: "https://example.com/headphones",
          imageUrl: "https://encrypted-tbn2.gstatic.com/shopping?q=tbn:ANd9GcQ-jhxxU2nmeekRkOnEfshNkURBGsXLXh9gjMT_J1cqomt23clThSKxXxOHNzUg0ymp30eNhwnLmbZKUXxgo6MKVLFcM4fBLLWAOtEQpcbWZTRvMUBBhY2y",
          isPurchased: false
        }
      ]
    }
  ])

  // Set current user to Casey Wilson
  const currentUserId = ref<number>(101) // Casey Wilson

  // Getters
  const currentUser = computed(() => {
    return users.value.find((u) => u.id === currentUserId.value)
  })

  const getFamilyById = (id: number) => {
    return families.value.find((fam) => fam.id === id)
  }

  const getWishlistById = (id: number) => {
    return wishlists.value.find((wl) => wl.id === id)
  }

  // Actions
  function markItemPurchased(wishlistId: number, itemId: number) {
    const wishlist = wishlists.value.find((wl) => wl.id === wishlistId)
    if (!wishlist) return
    const item = wishlist.items.find((i) => i.id === itemId)
    if (item) {
      item.isPurchased = true
    }
  }

  // Get initial theme from localStorage, fallback to system preference
  const getInitialTheme = (): boolean => {
    const stored = localStorage.getItem('theme')
    if (stored !== null) {
      return stored === 'dark'
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches
  }

  // Initialize theme state with stored preference
  const isDarkTheme = ref(getInitialTheme())

  // Update theme in both DOM and localStorage
  function setTheme(dark: boolean) {
    isDarkTheme.value = dark
    localStorage.setItem('theme', dark ? 'dark' : 'light')
    document.documentElement.classList.toggle('dark', dark)
  }

  // Modified theme toggle to use setTheme
  function toggleTheme() {
    setTheme(!isDarkTheme.value)
  }

  // Watch system theme changes
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    // Only update if user hasn't set a preference
    if (localStorage.getItem('theme') === null) {
      setTheme(e.matches)
    }
  })

  // Initialize theme on store creation
  setTheme(isDarkTheme.value)

  // Add to your actions
  function createFamily(familyData: Omit<Family, 'id'>) {
    const newId = Math.max(0, ...families.value.map(f => f.id)) + 1
    const newFamily: Family = {
      id: newId,
      name: familyData.name,
      members: familyData.members || []
    }
    families.value.push(newFamily)
    return newFamily
  }

  function updateFamily(updatedFamily: Family) {
    const index = families.value.findIndex(f => f.id === updatedFamily.id)
    if (index !== -1) {
      families.value[index] = {
        ...families.value[index],
        ...updatedFamily
      }
      return families.value[index]
    }
    throw new Error('Family not found')
  }

  function deleteFamily(id: number) {
    const index = families.value.findIndex(f => f.id === id)
    if (index !== -1) {
      // Remove associated wishlists
      wishlists.value = wishlists.value.filter(w => w.familyId !== id)
      // Remove the family
      families.value.splice(index, 1)
      return true
    }
    return false
  }

  function addFamilyMember(familyId: number, memberId: number) {
    const family = families.value.find(f => f.id === familyId)
    if (!family) throw new Error('Family not found')
    
    // Check if user exists
    const userExists = users.value.some(u => u.id === memberId)
    if (!userExists) throw new Error('User not found')
    
    // Check if member is already in family
    if (family.members.includes(memberId)) {
      throw new Error('Member already in family')
    }
    
    family.members.push(memberId)
    return family
  }

  function removeFamilyMember(familyId: number, memberId: number) {
    const family = families.value.find(f => f.id === familyId)
    if (!family) throw new Error('Family not found')
    
    const memberIndex = family.members.indexOf(memberId)
    if (memberIndex === -1) throw new Error('Member not in family')
    
    // Remove member from family
    family.members.splice(memberIndex, 1)
    
    // Remove their wishlists associated with this family
    wishlists.value = wishlists.value.filter(w => 
      !(w.familyId === familyId && w.ownerId === memberId)
    )
    
    return family
  }

  // Add new state
  const invitations = ref<Invitation[]>([])
  
  // Add new actions
  function inviteMemberByEmail(familyId: number, email: string) {
    const family = families.value.find(f => f.id === familyId)
    if (!family) throw new Error('Family not found')
    
    // Check if invitation already exists
    const existingInvite = invitations.value.find(
      i => i.familyId === familyId && i.email === email && i.status === 'pending'
    )
    if (existingInvite) throw new Error('Invitation already sent')
    
    // Check if user with email already exists
    const existingUser = users.value.find(u => u.email === email)
    if (existingUser && family.members.includes(existingUser.id)) {
      throw new Error('User is already a member')
    }
    
    const newId = Math.max(0, ...invitations.value.map(i => i.id)) + 1
    const invitation: Invitation = {
      id: newId,
      email,
      familyId,
      status: 'pending',
      createdAt: new Date()
    }
    
    invitations.value.push(invitation)
    return invitation
  }
  
  function acceptInvitation(invitationId: number) {
    const invitation = invitations.value.find(i => i.id === invitationId)
    if (!invitation) throw new Error('Invitation not found')
    if (invitation.status !== 'pending') throw new Error('Invitation is not pending')
    
    // Create user if doesn't exist
    let userId: number
    const existingUser = users.value.find(u => u.email === invitation.email)
    if (existingUser) {
      userId = existingUser.id
    } else {
      // Create new user
      const newId = Math.max(0, ...users.value.map(u => u.id)) + 1
      const newUser = {
        id: newId,
        name: invitation.email.split('@')[0], // Temporary name from email
        email: invitation.email
      }
      users.value.push(newUser)
      userId = newUser.id
    }
    
    // Add to family
    addFamilyMember(invitation.familyId, userId)
    
    // Update invitation status
    invitation.status = 'accepted'
    return invitation
  }
  
  function declineInvitation(invitationId: number) {
    const invitation = invitations.value.find(i => i.id === invitationId)
    if (!invitation) throw new Error('Invitation not found')
    if (invitation.status !== 'pending') throw new Error('Invitation is not pending')
    
    invitation.status = 'declined'
    return invitation
  }

  function createWishlist(wishlistData: Omit<Wishlist, 'id' | 'items'>) {
    const newId = Math.max(0, ...wishlists.value.map(w => w.id)) + 1
    const newWishlist: Wishlist = {
      id: newId,
      items: [],
      ...wishlistData
    }
    wishlists.value.push(newWishlist)
    return newWishlist
  }

  function updateWishlist(wishlistId: number, data: Partial<Wishlist>) {
    const index = wishlists.value.findIndex(w => w.id === wishlistId)
    if (index === -1) throw new Error('Wishlist not found')
    
    wishlists.value[index] = {
      ...wishlists.value[index],
      ...data
    }
    return wishlists.value[index]
  }

  function deleteWishlist(wishlistId: number) {
    const index = wishlists.value.findIndex(w => w.id === wishlistId)
    if (index === -1) return false
    wishlists.value.splice(index, 1)
    return true
  }

  function addWishlistItem(wishlistId: number, item: Omit<GiftItem, 'id'>) {
    const wishlist = wishlists.value.find(w => w.id === wishlistId)
    if (!wishlist) throw new Error('Wishlist not found')
    
    const newId = Math.max(0, ...wishlist.items.map(i => i.id)) + 1
    const newItem: GiftItem = {
      id: newId,
      ...item,
      isPurchased: false
    }
    
    wishlist.items.push(newItem)
    return newItem
  }

  function updateWishlistItem(wishlistId: number, itemId: number, data: Partial<GiftItem>) {
    const wishlist = wishlists.value.find(w => w.id === wishlistId)
    if (!wishlist) throw new Error('Wishlist not found')
    
    const itemIndex = wishlist.items.findIndex(i => i.id === itemId)
    if (itemIndex === -1) throw new Error('Item not found')
    
    wishlist.items[itemIndex] = {
      ...wishlist.items[itemIndex],
      ...data
    }
    return wishlist.items[itemIndex]
  }

  function deleteWishlistItem(wishlistId: number, itemId: number) {
    const wishlist = wishlists.value.find(w => w.id === wishlistId)
    if (!wishlist) throw new Error('Wishlist not found')
    
    const itemIndex = wishlist.items.findIndex(i => i.id === itemId)
    if (itemIndex === -1) throw new Error('Item not found')
    
    wishlist.items.splice(itemIndex, 1)
    return true
  }

  const myWishlists = computed(() => 
    wishlists.value.filter(w => w.ownerId === currentUserId.value)
  )

  const familyWishlists = computed(() => {
    const myFamilies = families.value
      .filter(f => f.members.includes(currentUserId.value))
      .map(f => f.id)
      
    return wishlists.value.filter(w => 
      myFamilies.includes(w.familyId) && w.ownerId !== currentUserId.value
    )
  })

  // Add to store state
  const notifications = ref<Notification[]>([
    {
      id: 1,
      type: 'new_item',
      userId: 102, // Meriah
      targetId: 1, // Wishlist ID
      read: false,
      createdAt: new Date('2024-03-10')
    },
    {
      id: 2,
      type: 'purchased',
      userId: 103, // Pej
      targetId: 1, // Item ID (Running Shoes)
      read: false,
      createdAt: new Date('2024-03-15')
    }
  ])

  // Add notification methods
  function markNotificationRead(notificationId: number) {
    const notification = notifications.value.find(n => n.id === notificationId)
    if (notification) {
      notification.read = true
    }
  }

  function markAllNotificationsRead() {
    notifications.value.forEach(notification => {
      notification.read = true
    })
  }

  function addNotification(notification: Omit<Notification, 'id' | 'read' | 'createdAt'>) {
    const newId = Math.max(0, ...notifications.value.map(n => n.id)) + 1
    notifications.value.push({
      id: newId,
      read: false,
      createdAt: new Date(),
      ...notification
    })
  }

  function logout() {
    // Add logout logic here
    console.log('User logged out')
  }

  return {
    families,
    users,
    wishlists,
    currentUserId,
    currentUser,
    getFamilyById,
    getWishlistById,
    markItemPurchased,
    isDarkTheme,
    toggleTheme,
    createFamily,
    updateFamily,
    deleteFamily,
    addFamilyMember,
    removeFamilyMember,
    invitations,
    inviteMemberByEmail,
    acceptInvitation,
    declineInvitation,
    createWishlist,
    updateWishlist,
    deleteWishlist,
    addWishlistItem,
    updateWishlistItem,
    deleteWishlistItem,
    myWishlists,
    familyWishlists,
    notifications,
    markNotificationRead,
    markAllNotificationsRead,
    addNotification,
    logout,
  }
})
