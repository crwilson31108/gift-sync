<template>
  <v-card class="wishlist-card" :loading="loading">
    <!-- Preview photos grid -->
    <div class="preview-container">
      <template v-if="wishlist.items.length > 0">
        <slot name="preview"></slot>
      </template>
      <template v-else>
        <div class="empty-preview">
          <v-icon
            icon="mdi-gift-outline"
            size="32"
            class="mr-2"
          />
          No items yet
        </div>
      </template>
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

    <!-- Actions -->
    <v-card-actions>
      <v-spacer />
      <slot name="actions"></slot>
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { WishList } from '@/services/wishlists'
import { useAppStore } from '@/stores/useAppStore'

const props = defineProps<{
  wishlist: WishList
}>()

const store = useAppStore()
const loading = ref(false)

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
  display: flex;
  flex-direction: column;
  background: rgb(var(--v-theme-surface));
  border: 1px solid rgba(var(--v-border-color), 0.12);
  height: 100%;
}

.preview-container {
  /* Remove aspect-ratio and other constraints */
  width: 100%;
  flex-shrink: 0; /* Prevent container from shrinking */
  background: rgba(var(--v-theme-surface-variant), 0.12);
}

/* Update image styles */
:deep(.v-img) {
  border-radius: 4px;
  overflow: hidden;
  background: rgb(var(--v-theme-surface));
  border: 1px solid rgba(var(--v-border-color), 0.08);
}

:deep(.v-img__img) {
  object-fit: cover !important;
  transition: transform 0.3s ease;
}

/* Hover effect for images */
:deep(.v-img:hover .v-img__img) {
  transform: scale(1.05);
}

/* Loading state styles */
.preview-container :deep(.v-img.v-img--loading) {
  background: rgba(var(--v-theme-surface-variant), 0.12);
}

/* Skeleton loader styles */
:deep(.v-skeleton-loader__image) {
  aspect-ratio: 1;
  height: auto !important;
  background: rgba(var(--v-theme-surface-variant), 0.12) !important;
}

:deep(.v-skeleton-loader__article) {
  flex-grow: 1;
  padding: 16px;
}

/* Dark theme adjustments */
:deep(.v-theme--dark) .preview-container {
  background: rgba(255, 255, 255, 0.05);
}

:deep(.v-theme--dark) .v-img {
  border-color: rgba(255, 255, 255, 0.1);
}

/* Empty state placeholder */
.empty-preview {
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(var(--v-theme-surface-variant), 0.12);
  color: rgba(var(--v-theme-on-surface), 0.6);
  font-size: 0.875rem;
}

/* Card content styles */
.card-content {
  padding: 16px;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.card-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.title-text {
  font-weight: 600;
  font-size: 1.1rem;
  color: rgb(var(--v-theme-on-surface));
}

/* Responsive adjustments */
@media (max-width: 600px) {
  .preview-container {
    gap: 1px;
    padding: 1px;
  }
}
</style> 