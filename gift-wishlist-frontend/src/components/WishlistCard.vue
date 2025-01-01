<template>
  <v-card
    class="bg-light-surface dark:bg-dark-surface border border-accent/10 hover:border-accent/30 transition-all duration-200"
    elevation="0"
  >
    <div class="p-6">
      <!-- Card Header -->
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center space-x-3">
          <v-avatar color="primary" size="40">
            <span class="text-sm">{{ getOwnerInitials }}</span>
          </v-avatar>
          <div>
            <h3 class="text-lg font-semibold text-light-text dark:text-dark-text">
              {{ wishlist.name }}
            </h3>
            <p class="text-sm text-light-subtle dark:text-dark-subtle">
              {{ getOwnerName }}
            </p>
          </div>
        </div>
        
        <!-- Actions Menu -->
        <div class="flex items-center space-x-2">
          <template v-if="editable">
            <v-menu location="bottom end">
              <template v-slot:activator="{ props }">
                <v-btn
                  icon="mdi-dots-vertical"
                  variant="text"
                  size="small"
                  v-bind="props"
                  class="text-light-subtle dark:text-dark-subtle"
                />
              </template>
              <v-list>
                <v-list-item
                  prepend-icon="mdi-pencil"
                  title="Edit"
                  @click="$emit('edit', wishlist)"
                />
                <v-list-item
                  prepend-icon="mdi-delete"
                  title="Delete"
                  color="error"
                  @click="$emit('delete', wishlist)"
                />
              </v-list>
            </v-menu>
          </template>
        </div>
      </div>

      <!-- Preview Grid -->
      <div class="grid grid-cols-3 gap-2 mb-4">
        <template v-if="wishlist.items.length">
          <div 
            v-for="item in previewItems" 
            :key="item.id"
            class="aspect-square rounded-lg overflow-hidden bg-accent/5"
          >
            <img 
              :src="item.imageUrl || 'https://via.placeholder.com/150'" 
              :alt="item.title"
              class="w-full h-full object-cover"
            />
          </div>
        </template>
        <template v-else>
          <div class="col-span-3 py-8 text-center text-light-subtle dark:text-dark-subtle">
            No items yet
          </div>
        </template>
      </div>

      <!-- Stats -->
      <div class="flex items-center justify-between text-sm text-light-subtle dark:text-dark-subtle mb-4">
        <span>{{ wishlist.items.length }} items</span>
        <span>{{ getPurchasedCount }} purchased</span>
      </div>

      <!-- Card Footer -->
      <div class="mt-auto">
        <v-btn
          block
          color="primary"
          variant="tonal"
          :to="`/wishlists/${wishlist.id}`"
          class="text-center"
        >
          <v-icon icon="mdi-eye" size="small" class="mr-2" />
          View Wishlist
        </v-btn>
      </div>
    </div>
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAppStore } from '@/stores/useAppStore'
import type { Wishlist } from '@/stores/useAppStore'

const props = defineProps<{
  wishlist: Wishlist
  editable?: boolean
}>()

defineEmits<{
  (e: 'edit', wishlist: Wishlist): void
  (e: 'delete', wishlist: Wishlist): void
}>()

const store = useAppStore()

const getOwnerName = computed(() => {
  const owner = store.users.find(u => u.id === props.wishlist.ownerId)
  return owner?.name || 'Unknown'
})

const getOwnerInitials = computed(() => {
  return getOwnerName.value
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
})

const previewItems = computed(() => 
  props.wishlist.items.slice(0, 3)
)

const getPurchasedCount = computed(() => 
  props.wishlist.items.filter(item => item.isPurchased).length
)
</script> 