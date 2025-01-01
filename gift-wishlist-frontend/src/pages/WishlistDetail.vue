<!-- src/pages/WishlistDetail.vue -->
<template>
  <div class="py-8">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div class="flex items-center space-x-4">
        <v-avatar color="primary" size="56">
          <span class="text-lg">{{ getOwnerInitials }}</span>
        </v-avatar>
        <div>
          <h2 class="text-3xl font-bold text-primary mb-1">{{ wishlist?.name }}</h2>
          <p class="text-light-subtle dark:text-dark-subtle flex items-center">
            <v-icon icon="mdi-account" size="small" class="mr-1" />
            {{ getOwnerName }}
            <span class="mx-2">•</span>
            <v-icon icon="mdi-account-group" size="small" class="mr-1" />
            {{ getFamilyName }}
          </p>
        </div>
      </div>
      
      <div class="flex items-center space-x-3">
        <template v-if="isOwner">
          <v-btn
            color="primary"
            prepend-icon="mdi-plus"
            @click="openAddItemDialog"
          >
            Add Item
          </v-btn>
        </template>
        <v-btn
          icon
          variant="text"
          class="text-light-subtle dark:text-dark-subtle"
          @click="$router.back()"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="mb-6 p-4 bg-light-surface dark:bg-dark-surface rounded-lg border border-accent/10">
      <!-- Filter Summary -->
      <div v-if="filterStats.isFiltered" class="mb-4 flex items-center justify-between">
        <p class="text-sm text-light-subtle dark:text-dark-subtle">
          Showing {{ filterStats.filtered }} of {{ filterStats.total }} items
        </p>
        <v-btn
          size="small"
          variant="text"
          color="primary"
          @click="clearFilters"
        >
          Clear Filters
        </v-btn>
      </div>

      <div class="flex flex-wrap gap-4">
        <!-- Search -->
        <v-text-field
          v-model="filters.search"
          label="Search items"
          prepend-inner-icon="mdi-magnify"
          variant="outlined"
          density="comfortable"
          hide-details
          class="max-w-xs"
        />
        
        <!-- Size Filter -->
        <v-select
          v-model="filters.size"
          :items="['All', 'Small', 'Medium', 'Large']"
          label="Size"
          prepend-inner-icon="mdi-resize"
          variant="outlined"
          density="comfortable"
          hide-details
          class="max-w-[150px]"
        />

        <!-- Price Range -->
        <v-range-slider
          v-model="filters.priceRange"
          :min="0"
          :max="200"
          :step="10"
          label="Price Range"
          prepend-inner-icon="mdi-currency-usd"
          variant="outlined"
          density="comfortable"
          hide-details
          class="max-w-xs px-3"
        >
          <template v-slot:prepend>
            <span class="text-sm text-light-subtle dark:text-dark-subtle">
              ${{ filters.priceRange[0] }}
            </span>
          </template>
          <template v-slot:append>
            <span class="text-sm text-light-subtle dark:text-dark-subtle">
              ${{ filters.priceRange[1] }}
            </span>
          </template>
        </v-range-slider>

        <!-- Purchase Status -->
        <v-select
          v-model="filters.status"
          :items="['All', 'Available', 'Purchased']"
          label="Status"
          prepend-inner-icon="mdi-gift-outline"
          variant="outlined"
          density="comfortable"
          hide-details
          class="max-w-[150px]"
        />
      </div>
    </div>

    <!-- Grid View -->
    <TransitionGroup
      name="masonry-item"
      tag="div"
      class="masonry-grid relative"
    >
      <vue-draggable
        v-model="items"
        :disabled="!isOwner"
        item-key="id"
        animation="300"
        :delay="50"
        ghost-class="ghost-item"
        chosen-class="chosen-item"
        drag-class="drag-item"
        @end="handleDragEnd"
      >
      <template #item="{ element: item }">
        <div class="masonry-item" :key="item.id">
          <v-card
            class="bg-light-surface dark:bg-dark-surface border border-accent/10 hover:border-accent/30 transition-all duration-200"
            elevation="0"
          >
            <!-- Item Image -->
            <div class="relative overflow-hidden">
              <img 
                :src="item.imageUrl" 
                :alt="item.title"
                class="w-full object-contain"
                @load="handleImageLoad"
              />
              <div 
                v-if="item.isPurchased"
                class="absolute inset-0 bg-black/50 flex flex-col items-center justify-center p-4"
              >
                <v-icon
                  icon="mdi-gift-outline"
                  size="large"
                  class="text-white mb-2"
                />
                <template v-if="!isOwner">
                  <p class="text-white text-center text-sm">
                    Purchased by {{ getPurchaserName(item.purchasedBy) }}
                    <br>
                    <span class="text-xs opacity-75">
                      {{ formatPurchaseDate(item.purchasedAt) }}
                    </span>
                  </p>
                </template>
                <template v-else>
                  <p class="text-white text-center">
                    Purchased
                  </p>
                </template>
              </div>
            </div>

            <!-- Item Details -->
            <div class="p-4">
              <h3 class="text-lg font-semibold text-light-text dark:text-dark-text mb-2">
                {{ item.title }}
              </h3>
              <p class="text-light-subtle dark:text-dark-subtle mb-4">
                ${{ item.price }}
              </p>
              
              <!-- Actions -->
              <div class="flex items-center justify-between">
                <v-chip
                  :color="item.isPurchased ? 'success' : item.size === 'Large' ? 'error' : item.size === 'Medium' ? 'warning' : 'info'"
                  size="small"
                >
                  {{ item.isPurchased ? 'Purchased' : `${item.size} ($${item.price})` }}
                </v-chip>
                
                <div class="flex items-center space-x-2">
                  <v-btn
                    v-if="!isOwner && !item.isPurchased"
                    variant="tonal"
                    size="small"
                    color="primary"
                    class="px-4"
                    @click="initiatePurchase(item)"
                  >
                    <v-icon icon="mdi-gift" size="small" class="mr-2" />
                    Mark as Purchased
                  </v-btn>
                  <template v-if="isOwner">
                    <v-btn
                      icon="mdi-pencil"
                      variant="text"
                      size="small"
                      class="text-light-subtle dark:text-dark-subtle"
                      @click="editItem(item)"
                    />
                    <v-btn
                      icon="mdi-delete"
                      variant="text"
                      size="small"
                      color="error"
                      @click="confirmDeleteItem(item)"
                    />
                  </template>
                </div>
              </div>
            </div>
          </v-card>
        </div>
      </template>
      </vue-draggable>
    </TransitionGroup>

    <!-- Add/Edit Item Dialog -->
    <v-dialog v-model="itemDialogVisible" max-width="500px">
      <v-card class="p-6">
        <h3 class="text-xl font-semibold mb-4">
          {{ editingItem ? 'Edit Item' : 'Add Item' }}
        </h3>
        
        <v-form @submit.prevent="saveItem">
          <v-text-field
            v-model="itemForm.title"
            label="Title"
            required
            class="mb-4"
          />
          
          <v-text-field
            v-model.number="itemForm.price"
            label="Price"
            type="number"
            required
            class="mb-4"
            @input="itemForm.size = calculateSize($event.target.value)"
          />
          
          <v-text-field
            v-model="itemForm.link"
            label="Link"
            required
            class="mb-4"
          />
          
          <div class="mb-4">
            <label class="block text-sm font-medium mb-2">Image</label>
            <div class="flex gap-4">
              <v-file-input
                @change="handleImageInput"
                accept="image/*"
                label="Upload Image"
                class="flex-1"
              />
              <span class="text-center py-2">or</span>
              <v-text-field
                v-model="itemForm.image"
                label="Image URL"
                class="flex-1"
                @input="handleImageUrl($event.target.value)"
              />
            </div>
          </div>
          
          <div class="mb-4">
            <label class="block text-sm font-medium mb-2">Size Category</label>
            <v-chip-group
              v-model="itemForm.size"
              mandatory
              selected-class="!bg-primary text-white"
            >
              <v-chip
                value="Small"
                :disabled="itemForm.price > 50"
                :class="{ 'opacity-50': itemForm.price > 50 }"
              >
                Small ($25-50)
              </v-chip>
              <v-chip
                value="Medium"
                :disabled="itemForm.price <= 50 || itemForm.price > 100"
                :class="{ 'opacity-50': itemForm.price <= 50 || itemForm.price > 100 }"
              >
                Medium ($51-100)
              </v-chip>
              <v-chip
                value="Large"
                :disabled="itemForm.price <= 100"
                :class="{ 'opacity-50': itemForm.price <= 100 }"
              >
                Large ($100+)
              </v-chip>
            </v-chip-group>
          </div>
          
          <div class="flex justify-end gap-3">
            <v-btn
              variant="outlined"
              @click="itemDialogVisible = false"
            >
              Cancel
            </v-btn>
            <v-btn
              color="primary"
              type="submit"
              :loading="saving"
            >
              {{ editingItem ? 'Save' : 'Add' }}
            </v-btn>
          </div>
        </v-form>
      </v-card>
    </v-dialog>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="deleteDialogVisible" max-width="400px">
      <v-card class="p-6">
        <h3 class="text-xl font-semibold mb-4">Confirm Delete</h3>
        <p class="mb-6">Are you sure you want to delete this item?</p>
        <div class="flex justify-end gap-3">
          <v-btn
            variant="outlined"
            @click="deleteDialogVisible = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="error"
            @click="deleteItem"
            :loading="deleting"
          >
            Delete
          </v-btn>
        </div>
      </v-card>
    </v-dialog>

    <!-- Purchase Confirmation Dialog -->
    <v-dialog v-model="purchaseDialogVisible" max-width="400px">
      <v-card class="p-6">
        <h3 class="text-xl font-semibold mb-4">Confirm Purchase</h3>
        <p class="mb-6">
          Are you sure you want to mark this item as purchased? 
          This will let others know you're buying this gift.
        </p>
        <div class="flex justify-end gap-3">
          <v-btn
            variant="outlined"
            @click="purchaseDialogVisible = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="primary"
            @click="confirmPurchase"
            :loading="purchasing"
          >
            Confirm Purchase
          </v-btn>
        </div>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/stores/useAppStore'
import type { GiftItem } from '@/stores/useAppStore'
import VueDraggable from 'vuedraggable'

const route = useRoute()
const store = useAppStore()

const wishlistId = parseInt(route.params.id as string, 10)

// State
const itemDialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const saving = ref(false)
const deleting = ref(false)
const editingItem = ref<GiftItem | null>(null)
const selectedItem = ref<GiftItem | null>(null)
const purchaseDialogVisible = ref(false)
const purchasing = ref(false)
const selectedForPurchase = ref<GiftItem | null>(null)

const itemForm = ref({
  title: '',
  price: 0,
  link: '',
  image: null as File | string | null,
  size: 'Medium' as 'Small' | 'Medium' | 'Large'
})

const filters = ref({
  search: '',
  size: 'All',
  priceRange: [0, 200],
  status: 'All'
})

// Computed
const wishlist = computed(() => 
  store.wishlists.find(w => w.id === wishlistId)
)

const items = computed({
  get: () => {
    let filteredItems = wishlist.value?.items || []
    
    // Apply search filter
    if (filters.value.search) {
      const searchTerm = filters.value.search.toLowerCase()
      filteredItems = filteredItems.filter(item => 
        item.title.toLowerCase().includes(searchTerm)
      )
    }
    
    // Apply size filter
    if (filters.value.size !== 'All') {
      filteredItems = filteredItems.filter(item => 
        item.size === filters.value.size
      )
    }
    
    // Apply price range filter
    filteredItems = filteredItems.filter(item => 
      item.price >= filters.value.priceRange[0] && 
      item.price <= filters.value.priceRange[1]
    )
    
    // Apply status filter
    if (filters.value.status !== 'All') {
      const isPurchased = filters.value.status === 'Purchased'
      filteredItems = filteredItems.filter(item => 
        item.isPurchased === isPurchased
      )
    }
    
    return filteredItems
  },
  set: (newItems) => {
    if (wishlist.value) {
      store.updateWishlist(wishlistId, {
        ...wishlist.value,
        items: newItems
      })
    }
  }
})

const filterStats = computed(() => {
  const total = wishlist.value?.items.length || 0
  const filtered = items.value.length
  return {
    total,
    filtered,
    isFiltered: filtered !== total
  }
})

const isOwner = computed(() => 
  wishlist.value?.ownerId === store.currentUserId
)

const getOwnerName = computed(() => {
  if (!wishlist.value) return ''
  const owner = store.users.find(u => u.id === wishlist.value?.ownerId)
  return owner?.name || 'Unknown'
})

const getOwnerInitials = computed(() => {
  return getOwnerName.value
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
})

const getFamilyName = computed(() => {
  if (!wishlist.value) return ''
  const family = store.families.find(f => f.id === wishlist.value?.familyId)
  return family?.name || 'Unknown Family'
})

const isMyWishlist = computed(() => 
  wishlist.value?.ownerId === store.currentUserId
)

// Methods
const openAddItemDialog = () => {
  editingItem.value = null
  itemForm.value = {
    title: '',
    price: 0,
    link: '',
    image: null,
    size: 'Medium'
  }
  itemDialogVisible.value = true
}

const editItem = (item: GiftItem) => {
  editingItem.value = item
  itemForm.value = {
    title: item.title,
    price: item.price,
    link: item.link,
    image: null,
    size: item.size
  }
  itemDialogVisible.value = true
}

const handleImageInput = (event: Event) => {
  const input = event.target as HTMLInputElement
  if (input.files && input.files[0]) {
    itemForm.value.image = input.files[0]
  }
}

const handleImageUrl = (url: string) => {
  itemForm.value.image = url
}

const saveItem = async () => {
  if (!itemForm.value.image) return
  
  saving.value = true
  try {
    let imageUrl: string
    
    if (typeof itemForm.value.image === 'string') {
      imageUrl = itemForm.value.image
    } else {
      // In a real app, we'd upload the file to a server
      imageUrl = URL.createObjectURL(itemForm.value.image)
    }
    
    const itemData = {
      title: itemForm.value.title,
      price: itemForm.value.price,
      link: itemForm.value.link,
      size: itemForm.value.size,
      imageUrl,
      isPurchased: false
    }
    
    if (editingItem.value) {
      await store.updateWishlistItem(wishlistId, editingItem.value.id, itemData)
    } else {
      await store.addWishlistItem(wishlistId, itemData)
    }
    itemDialogVisible.value = false
  } finally {
    saving.value = false
  }
}

const confirmDeleteItem = (item: GiftItem) => {
  selectedItem.value = item
  deleteDialogVisible.value = true
}

const deleteItem = async () => {
  if (!selectedItem.value) return
  
  deleting.value = true
  try {
    await store.deleteWishlistItem(wishlistId, selectedItem.value.id)
    deleteDialogVisible.value = false
  } finally {
    deleting.value = false
  }
}

const initiatePurchase = (item: GiftItem) => {
  selectedForPurchase.value = item
  purchaseDialogVisible.value = true
}

const confirmPurchase = async () => {
  if (!selectedForPurchase.value) return
  
  purchasing.value = true
  try {
    await store.updateWishlistItem(wishlistId, selectedForPurchase.value.id, {
      isPurchased: true,
      purchasedBy: store.currentUserId,
      purchasedAt: new Date()
    })
    purchaseDialogVisible.value = false
  } finally {
    purchasing.value = false
    selectedForPurchase.value = null
  }
}

const getPurchaserName = (userId?: number) => {
  if (!userId) return 'Unknown'
  const user = store.users.find(u => u.id === userId)
  return user?.name || 'Unknown'
}

const formatPurchaseDate = (date?: Date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const handleDragEnd = () => {
  // Handle drag end if needed
  // Currently the v-model handles the reordering automatically
}

const handleImageLoad = (event: Event) => {
  const img = event.target as HTMLImageElement
  const container = img.parentElement
  if (container) {
    const ratio = img.naturalHeight / img.naturalWidth
    container.style.paddingTop = `${ratio * 100}%`
    img.style.position = 'absolute'
    img.style.top = '0'
    img.style.left = '0'
    img.style.width = '100%'
    img.style.height = '100%'
  }
}

const copyToMyWishlist = async () => {
  if (!wishlist.value) return
  
  // Find or create my wishlist
  let myWishlist = store.myWishlists[0]
  if (!myWishlist) {
    myWishlist = await store.createWishlist({
      name: `${store.currentUser?.name}'s Wishlist`,
      ownerId: store.currentUserId,
      familyId: wishlist.value.familyId
    })
  }
  
  // Get the selected item
  const selectedItem = wishlist.value.items.find(i => !i.isPurchased)
  if (!selectedItem) return
  
  // Add to my wishlist
  await store.addWishlistItem(myWishlist.id, {
    title: selectedItem.title,
    price: selectedItem.price,
    link: selectedItem.link,
    size: selectedItem.size,
    imageUrl: selectedItem.imageUrl,
    isPurchased: false
  })
  
  // Show success message (you'll need to implement this)
  // showNotification('Item added to your wishlist')
}

const calculateSize = (price: number) => {
  if (price <= 50) return 'Small'
  if (price <= 100) return 'Medium'
  return 'Large'
}

const clearFilters = () => {
  filters.value = {
    search: '',
    size: 'All',
    priceRange: [0, 200],
    status: 'All'
  }
}
</script>

<style>
.masonry-grid {
  columns: 1 300px;
  column-gap: 1.5rem;
}

.masonry-item {
  break-inside: avoid;
  margin-bottom: 1.5rem;
  opacity: 1;
  transform: translateY(0);
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Enter animation */
.masonry-item-enter-active {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.masonry-item-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

/* Leave animation */
.masonry-item-leave-active {
  position: absolute;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.masonry-item-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* Image container */
.relative.overflow-hidden {
  position: relative;
  background: #f5f5f5;
}

/* Drag and drop states */
.ghost-item {
  opacity: 0.5;
  background: #f0f0f0;
  border: 2px dashed var(--v-primary-base) !important;
}

.chosen-item {
  cursor: grabbing !important;
}

.drag-item {
  opacity: 0.8;
  transform: scale(1.05);
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

/* Smooth transitions */
.masonry-item {
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

@media (min-width: 640px) {
  .masonry-grid {
    columns: 2 300px;
  }
}

@media (min-width: 1024px) {
  .masonry-grid {
    columns: 3 300px;
  }
}

@media (min-width: 1280px) {
  .masonry-grid {
    columns: 4 300px;
  }
}

/* Add smooth animation for items */
.v-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.v-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
</style>
