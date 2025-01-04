<template>
  <div class="py-8">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h2 class="text-3xl font-bold text-primary mb-2">Notifications</h2>
        <p class="text-light-subtle dark:text-dark-subtle">
          Stay updated on family gift activities
        </p>
      </div>
      <v-btn
        v-if="unreadNotifications.length"
        variant="text"
        color="primary"
        @click="markAllRead"
      >
        Mark All Read
      </v-btn>
    </div>

    <!-- Notifications List -->
    <div class="space-y-4">
      <v-card
        v-for="notification in notifications"
        :key="notification.id"
        :class="[
          'bg-light-surface dark:bg-dark-surface border transition-all duration-200',
          notification.read ? 'border-accent/10' : 'border-primary'
        ]"
        elevation="0"
      >
        <div class="p-6">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-4">
              <v-avatar color="primary" size="40">
                <span class="text-sm">{{ getUserInitials(notification.user) }}</span>
              </v-avatar>
              <div>
                <p class="text-light-text dark:text-dark-text">
                  <span class="font-medium">{{ getUserName(notification.user) }}</span>
                  {{ getNotificationText(notification) }}
                </p>
                <p class="text-sm text-light-subtle dark:text-dark-subtle">
                  {{ formatDate(notification.created_at) }}
                </p>
              </div>
            </div>
            <div class="flex items-center space-x-2">
              <v-btn
                color="primary"
                variant="tonal"
                size="small"
                :to="getNotificationLink(notification)"
              >
                View
              </v-btn>
              <v-btn
                v-if="!notification.read"
                icon="mdi-check"
                variant="text"
                size="small"
                @click="() => markAsRead(notification.id)"
              />
            </div>
          </div>
        </div>
      </v-card>

      <div 
        v-if="!notifications.length" 
        class="text-center py-12 text-light-subtle dark:text-dark-subtle"
      >
        No notifications yet
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAppStore } from '@/stores/useAppStore'
import { format } from 'date-fns'
import type { Notification } from '@/types'

const store = useAppStore()

const notifications = computed<Notification[]>(() => 
  [...store.notifications]
    .sort((a, b) => 
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )
)

const unreadNotifications = computed(() => 
  notifications.value.filter(n => !n.read)
)

const getUserName = (userId: number) => {
  if (userId === store.currentUser?.id) return 'You'
  return store.currentUser?.full_name || 'Unknown'
}

const getUserInitials = (userId: number): string => {
  const name = getUserName(userId)
  return name
    .split(' ')
    .map((n: string) => n[0])
    .join('')
    .toUpperCase()
}

const formatDate = (date: string | null | undefined) => {
  if (!date) return ''
  try {
    return format(new Date(date), 'MMM d, yyyy')
  } catch (error) {
    console.error('Invalid date:', date)
    return ''
  }
}

const getNotificationText = (notification: Notification) => {
  switch (notification.type) {
    case 'new_item':
      return 'added a new item to their wishlist'
    case 'purchased':
      return 'purchased an item from a wishlist'
    case 'wishlist_created':
      return 'created a new wishlist'
    default:
      return ''
  }
}

const getNotificationLink = (notification: Notification) => {
  switch (notification.type) {
    case 'new_item':
    case 'wishlist_created':
      return `/wishlists/${notification.target_id}`
    case 'purchased':
      return `/wishlists/${notification.target_id}`
    default:
      return '/'
  }
}

const markAsRead = async (notificationId: number) => {
  try {
    await store.markNotificationRead(notificationId)
  } catch (error) {
    console.error('Failed to mark notification as read:', error)
  }
}

const markAllRead = async () => {
  try {
    await store.markAllNotificationsRead()
  } catch (error) {
    console.error('Failed to mark all notifications as read:', error)
  }
}
</script> 