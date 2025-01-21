<template>
  <v-card class="wishlist-card" :loading="loading">
    <!-- Loading skeleton -->
    <template v-if="loading">
      <v-skeleton-loader
        type="image, article"
        :loading="true"
      ></v-skeleton-loader>
    </template>

    <template v-else>
      <!-- Preview photos grid -->
      <div class="preview-container">
        <slot name="preview"></slot>
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
    </template>
  </v-card>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import type { WishList } from '@/services/wishlists'
import { useAppStore } from '@/stores/useAppStore'

const props = defineProps<{
  wishlist: WishList
}>()

const store = useAppStore()
const loading = ref(true)
const imagesLoaded = ref(0)
const totalImages = computed(() => props.wishlist.items.length)

// Track image loading
function handleImageLoad() {
  imagesLoaded.value++
  if (imagesLoaded.value >= totalImages.value) {
    loading.value = false
  }
}

// Reset loading state when wishlist changes
watch(() => props.wishlist, () => {
  loading.value = true
  imagesLoaded.value = 0
  
  // If no images, show content immediately
  if (totalImages.value === 0) {
    loading.value = false
  }
}, { immediate: true })

// Expose image load handler to parent
defineExpose({
  handleImageLoad
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
  min-height: 200px;
  display: flex;
  flex-direction: column;
}

.preview-container {
  aspect-ratio: 1;
  overflow: hidden;
}

.wishlist-card:hover {
  transform: translateY(-4px);
}

/* Dark mode support */
:deep(.v-theme--dark) .preview-placeholder {
  background-color: rgba(255, 255, 255, 0.05);
}

/* Skeleton loader styles */
:deep(.v-skeleton-loader__image) {
  aspect-ratio: 1;
  height: auto !important;
}

:deep(.v-skeleton-loader__article) {
  flex-grow: 1;
  padding: 16px;
}
</style> 