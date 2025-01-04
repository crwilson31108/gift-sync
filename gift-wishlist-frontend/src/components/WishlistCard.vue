<template>
  <v-card class="wishlist-card">
    <!-- Preview Image -->
    <div class="preview-container">
      <v-img
        v-if="firstItemWithImage"
        :src="firstItemWithImage.image_url"
        height="200"
        cover
        class="preview-image"
      >
        <template v-slot:placeholder>
          <div class="d-flex align-center justify-center fill-height">
            <v-progress-circular indeterminate color="primary" />
          </div>
        </template>
      </v-img>
      
      <!-- Fallback when no images -->
      <div v-else class="preview-placeholder d-flex align-center justify-center">
        <v-icon
          size="64"
          color="grey-lighten-1"
          icon="mdi-gift-outline"
        />
      </div>
    </div>

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

    <!-- Optional: Show a few item previews -->
    <v-card-text v-if="wishlist.items.length" class="item-preview">
      <div class="text-caption text-grey">
        Top items:
        <span v-for="(item, index) in previewItems" :key="item.id">
          {{ item.title }}{{ index < previewItems.length - 1 ? ', ' : '' }}
        </span>
      </div>
    </v-card-text>

    <!-- Actions -->
    <v-card-actions>
      <v-spacer />
      <slot name="actions"></slot>
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { WishList, WishListItem } from '@/services/wishlists'
import { useAppStore } from '@/stores/useAppStore'

const props = defineProps<{
  wishlist: WishList
}>()

const store = useAppStore()

// Find first item with an image
const firstItemWithImage = computed(() => {
  return props.wishlist.items.find(item => item.image_url)
})

// Get 3 items for preview
const previewItems = computed(() => {
  return props.wishlist.items.slice(0, 3)
})

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

.preview-container {
  height: 200px;
  background-color: rgb(var(--v-theme-surface-variant));
}

.preview-placeholder {
  height: 100%;
  background-color: rgb(var(--v-theme-surface-variant));
}

.item-preview {
  max-height: 50px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Dark mode support */
:deep(.v-theme--dark) .preview-placeholder {
  background-color: rgba(255, 255, 255, 0.05);
}
</style> 