<template>
  <v-card class="wishlist-card">
    <!-- Preview photos grid -->
    <slot name="preview"></slot>

    <!-- Card Content -->
    <v-card-title class="d-flex justify-space-between align-center">
      <span class="text-truncate">{{ wishlist.name }}</span>
      <v-chip
        size="small"
        :color="getStatusColor(wishlist)"
      >
        {{ getItemCount(wishlist) }}
      </v-chip>
    </v-card-title>

    <v-card-subtitle>
      {{ wishlist.owner.full_name }}
    </v-card-subtitle>

    <!-- Actions -->
    <v-card-actions>
      <v-spacer />
      <slot name="actions"></slot>
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { WishList } from '@/services/wishlists'
import { useAppStore } from '@/stores/useAppStore'

const props = defineProps<{
  wishlist: WishList
}>()

const store = useAppStore()

function getItemCount(wishlist: WishList) {
  // If user is the owner, just show total items
  if (wishlist.owner.id === store.currentUser?.id) {
    return `${wishlist.items.length} items`
  }
  const total = wishlist.items.length
  const purchased = wishlist.items.filter(item => item.is_purchased).length
  return `${purchased}/${total} items`
}

function getStatusColor(wishlist: WishList) {
  const total = wishlist.items.length
  if (total === 0) return 'grey'
  
  // If user is the owner, always return primary color
  if (wishlist.owner.id === store.currentUser?.id) {
    return 'primary'
  }
  
  const purchased = wishlist.items.filter(item => item.is_purchased).length
  const percentage = (purchased / total) * 100
  
  if (percentage === 100) return 'success'
  if (percentage > 50) return 'warning'
  return 'primary'
}
</script>

<style scoped>
.wishlist-card {
  transition: transform 0.2s;
}

.wishlist-card:hover {
  transform: translateY(-4px);
}

/* Dark mode support */
:deep(.v-theme--dark) .preview-placeholder {
  background-color: rgba(255, 255, 255, 0.05);
}
</style> 