<!-- src/pages/WishlistDetail.vue -->
<template>
  <div>
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold text-light-text dark:text-dark-text">
          {{ wishlist?.name || 'Wishlist' }}
        </h1>
        <p class="text-sm text-light-subtle dark:text-dark-subtle mt-1">
          Created by {{ wishlist?.owner.username }} on {{ wishlist?.created_at ? formatDate(wishlist.created_at) : '' }}
        </p>
      </div>
      <div class="flex gap-2">
        <v-btn
          v-if="isOwner"
          color="primary"
          prepend-icon="mdi-plus"
          @click="openCreateItemDialog"
        >
          Add Item
        </v-btn>
        <v-btn
          v-if="isOwner"
          color="primary"
          variant="outlined"
          prepend-icon="mdi-pencil"
          @click="openEditDialog"
        >
          Edit Wishlist
        </v-btn>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center py-8">
      <v-progress-circular indeterminate color="primary" />
    </div>

    <!-- Error State -->
    <v-alert
      v-else-if="error"
      type="error"
      class="mb-4"
    >
      {{ error }}
    </v-alert>

    <!-- Empty State -->
    <div 
      v-else-if="!wishlist?.items.length"
      class="text-center py-12"
    >
      <v-icon
        icon="mdi-gift-outline"
        size="64"
        class="text-light-subtle dark:text-dark-subtle mb-4"
      />
      <h3 class="text-xl font-medium text-light-text dark:text-dark-text mb-2">
        No Items Yet
      </h3>
      <p class="text-light-subtle dark:text-dark-subtle mb-4">
        {{ isOwner ? 'Add your first item to your wishlist' : 'This wishlist is empty' }}
      </p>
      <v-btn
        v-if="isOwner"
        color="primary"
        prepend-icon="mdi-plus"
        @click="openCreateItemDialog"
      >
        Add Item
      </v-btn>
    </div>

    <!-- Items Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <v-card
        v-for="item in wishlist?.items"
        :key="item.id"
        :class="[
          'bg-light-surface dark:bg-dark-surface',
          { 'opacity-50': item.is_purchased && !isOwner }
        ]"
      >
        <v-img
          v-if="item.image_url"
          :src="item.image_url"
          height="200"
          cover
          class="bg-light-subtle dark:bg-dark-subtle"
        />

        <v-card-title class="flex justify-between items-center">
          <span>{{ item.title }}</span>
          <v-chip
            :color="item.is_purchased ? 'success' : getPriorityColor(item.priority)"
            size="small"
          >
            {{ item.is_purchased ? 'Purchased' : `Priority ${item.priority}` }}
          </v-chip>
        </v-card-title>

        <v-card-text>
          <p class="text-light-text dark:text-dark-text mb-2">
            {{ item.description }}
          </p>
          <div class="flex items-center justify-between text-sm text-light-subtle dark:text-dark-subtle">
            <span>${{ item.price }}</span>
            <span>Size: {{ item.size }}</span>
          </div>
          
          <div v-if="item.is_purchased" class="mt-2 text-sm text-success">
            Purchased by {{ item.purchased_by?.username }}
          </div>
        </v-card-text>

        <v-divider />

        <v-card-actions>
          <v-btn
            v-if="item.link"
            variant="text"
            prepend-icon="mdi-link"
            :href="item.link"
            target="_blank"
          >
            View Item
          </v-btn>
          <v-spacer />
          <template v-if="!isOwner">
            <v-btn
              v-if="!item.is_purchased"
              color="success"
              variant="text"
              prepend-icon="mdi-cart"
              @click="handlePurchase(item)"
            >
              Purchase
            </v-btn>
            <v-btn
              v-else-if="item.purchased_by?.id === currentUser?.id"
              color="error"
              variant="text"
              prepend-icon="mdi-cart-off"
              @click="handleUnpurchase(item)"
            >
              Unpurchase
            </v-btn>
          </template>
          <template v-else>
            <v-btn
              icon="mdi-pencil"
              variant="text"
              @click="openEditItemDialog(item)"
            />
            <v-btn
              icon="mdi-delete"
              variant="text"
              color="error"
              @click="confirmDeleteItem(item)"
            />
          </template>
        </v-card-actions>
      </v-card>
    </div>

    <!-- Create/Edit Item Dialog -->
    <v-dialog
      v-model="itemDialog.show"
      max-width="600"
    >
      <v-card>
        <v-card-title>
          {{ itemDialog.mode === 'create' ? 'Add Item' : 'Edit Item' }}
        </v-card-title>

        <v-card-text>
          <v-form @submit.prevent="handleItemSubmit" ref="form">
            <v-text-field
              v-model="itemForm.link"
              label="Link to Item*" 
              type="url"
              :loading="scraping"
              :error-messages="itemErrors.link"
              required
              @keyup.enter="scrapeUrl"
            >
              <template v-slot:append>
                <v-btn
                  icon
                  :loading="scraping"
                  @click="scrapeUrl"
                  :disabled="!itemForm.link"
                >
                  <v-icon>mdi-magnify</v-icon>
                </v-btn>
              </template>
            </v-text-field>

            <!-- Other form fields should be disabled until scraping is done -->
            <v-text-field
              v-model="itemForm.title"
              label="Item Name*"
              required
              :error-messages="itemErrors.title"
              :disabled="!hasScrapedData"
            />
            
            <v-textarea
              v-model="itemForm.description"
              label="Description"
              rows="3"
              :disabled="!hasScrapedData"
            />

            <div class="grid grid-cols-1">
              <v-text-field
                v-model.number="itemForm.price"
                label="Price"
                type="number"
                required
                prefix="$"
                :error-messages="itemErrors.price"
                :disabled="!hasScrapedData"
                @input="updateSizeFromPrice"
              />
            </div>

            <div v-if="allImages.length" class="mt-4">
              <label class="text-subtitle-1 mb-2 d-block">Select Image</label>
              <div class="image-grid">
                <div 
                  v-for="(image, index) in allImages" 
                  :key="index"
                  class="image-item"
                  :class="{ 'selected': image === itemForm.image_url }"
                  @click="itemForm.image_url = image"
                >
                  <v-img
                    :src="image"
                    aspect-ratio="1"
                    cover
                    class="rounded"
                    :class="{ 'v-img--selected': image === itemForm.image_url }"
                  >
                    <template v-slot:placeholder>
                      <div class="d-flex align-center justify-center fill-height">
                        <v-progress-circular
                          indeterminate
                          color="primary"
                        ></v-progress-circular>
                      </div>
                    </template>
                  </v-img>
                </div>
              </div>
            </div>
          </v-form>
        </v-card-text>

        <v-card-actions>
          <v-spacer />
          <v-btn
            variant="text"
            @click="itemDialog.show = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="primary"
            :loading="loading"
            :disabled="!hasScrapedData"
            @click="handleItemSubmit"
          >
            {{ itemDialog.mode === 'create' ? 'Add Item' : 'Save Changes' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Item Confirmation -->
    <v-dialog
      v-model="deleteItemDialog.show"
      max-width="400"
    >
      <v-card>
        <v-card-title class="text-error">
          Delete Item
        </v-card-title>
        <v-card-text>
          Are you sure you want to delete "{{ deleteItemDialog.item?.title }}"?
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn
            variant="text"
            @click="deleteItemDialog.show = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="error"
            :loading="loading"
            @click="handleDeleteItem"
          >
            Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { wishlistsService, type WishList, type WishListItem } from '@/services/wishlists'
import { useAppStore } from '@/stores/useAppStore'
import { format } from 'date-fns'

const route = useRoute()
const router = useRouter()
const store = useAppStore()
const currentUser = computed(() => store.currentUser)

const wishlist = ref<WishList | null>(null)
const loading = ref(false)
const error = ref('')

const isOwner = computed(() => 
  wishlist.value?.owner.id === currentUser.value?.id
)

// Item dialog state
const itemDialog = ref({
  show: false,
  mode: 'create',
  item: null,
})

const itemForm = ref({
  title: '',
  description: '',
  price: '',
  link: '',
  image_url: '',
  size: 'Medium',
  priority: 3,
  wishlist: null,
})

const itemErrors = ref({
  title: '',
  description: '',
  price: '',
  link: '',
  image_url: '',
})

const deleteItemDialog = ref({
  show: false,
  item: null as WishListItem | null
})

const scraping = ref(false)
const allImages = ref([])
const hasScrapedData = ref(false)

onMounted(async () => {
  await loadWishlist()
})

async function loadWishlist() {
  try {
    loading.value = true
    const wishlistId = Number(route.params.id)
    wishlist.value = await wishlistsService.getWishlist(wishlistId)
  } catch (err) {
    error.value = 'Failed to load wishlist'
    console.error(err)
  } finally {
    loading.value = false
  }
}

function openCreateItemDialog() {
  itemDialog.value = {
    show: true,
    mode: 'create',
    item: null,
  }
  
  // Reset form
  itemForm.value = {
    title: '',
    description: '',
    price: '',
    link: '',
    image_url: '',
    size: 'Medium',
    priority: 3,
    wishlist: route.params.id,
  }
  
  // Reset errors and images
  itemErrors.value = {
    title: '',
    description: '',
    price: '',
    link: '',
    image_url: '',
  }
  allImages.value = []
  hasScrapedData.value = false
}

function openEditItemDialog(item: WishListItem) {
  itemDialog.value = {
    show: true,
    mode: 'edit',
    item
  }
  itemForm.value = {
    ...item,
    wishlist: item.wishlist
  }
  itemErrors.value = {
    title: '',
    price: '',
    image: ''
  }
}

function confirmDeleteItem(item: WishListItem) {
  deleteItemDialog.value = {
    show: true,
    item
  }
}

async function handleItemSubmit() {
  try {
    loading.value = true
    itemErrors.value = { title: '', price: '', image: '' }

    // Create FormData for submission
    const formData = new FormData()
    formData.append('title', itemForm.value.title)
    formData.append('description', itemForm.value.description || '')
    formData.append('price', itemForm.value.price.toString())
    formData.append('link', itemForm.value.link || '')
    formData.append('size', itemForm.value.size)
    formData.append('priority', itemForm.value.priority.toString())
    formData.append('wishlist', itemForm.value.wishlist.toString())
    
    // Add image_url if it exists
    if (itemForm.value.image_url) {
      formData.append('image_url', itemForm.value.image_url)
    }

    if (itemDialog.value.item) {
      await wishlistsService.updateItem(itemDialog.value.item.id, formData)
    } else {
      await wishlistsService.createItem(formData)
    }

    await loadWishlist()
    itemDialog.value.show = false
  } catch (err: any) {
    if (err.response?.data) {
      itemErrors.value = {
        title: err.response.data.title?.[0] || '',
        description: '',
        price: err.response.data.price?.[0] || '',
        link: err.response.data.link?.[0] || '',
        image_url: err.response.data.image_url?.[0] || ''
      }
    } else {
      error.value = 'An error occurred'
    }
  } finally {
    loading.value = false
  }
}

async function handleDeleteItem() {
  if (!deleteItemDialog.value.item) return

  try {
    loading.value = true
    await wishlistsService.deleteItem(deleteItemDialog.value.item.id)
    await loadWishlist()
    deleteItemDialog.value.show = false
  } catch (err) {
    error.value = 'Failed to delete item'
    console.error(err)
  } finally {
    loading.value = false
  }
}

async function handlePurchase(item: WishListItem) {
  try {
    loading.value = true
    await wishlistsService.purchaseItem(item.id)
    await loadWishlist()
  } catch (err) {
    error.value = 'Failed to mark item as purchased'
    console.error(err)
  } finally {
    loading.value = false
  }
}

async function handleUnpurchase(item: WishListItem) {
  try {
    loading.value = true
    await wishlistsService.unpurchaseItem(item.id)
    await loadWishlist()
  } catch (err) {
    error.value = 'Failed to mark item as unpurchased'
    console.error(err)
  } finally {
    loading.value = false
  }
}

function getPriorityColor(priority: number) {
  switch (priority) {
    case 1: return 'info'
    case 2: return 'success'
    case 3: return 'warning'
    case 4: return 'error'
    case 5: return 'error'
    default: return 'primary'
  }
}

function formatDate(date: string) {
  return format(new Date(date), 'MMM d, yyyy')
}

function handleImageChange(file: File | null) {
  if (file && file.size > 5 * 1024 * 1024) { // 5MB limit
    itemErrors.value.image = 'Image size should be less than 5MB'
    itemForm.value.image = null
    return
  }
  itemForm.value.image = file
}

async function scrapeUrl() {
  if (!itemForm.value.link) {
    itemErrors.value.link = 'Please enter a valid URL'
    return
  }

  try {
    scraping.value = true
    const response = await wishlistsService.scrapeUrl(itemForm.value.link)
    
    // Update form with scraped data
    itemForm.value = {
      ...itemForm.value,
      title: response.title || itemForm.value.title,
      description: response.description || itemForm.value.description,
      price: response.price || itemForm.value.price,
      image_url: response.image_url || itemForm.value.image_url
    }

    // Set size based on scraped price
    if (response.price) {
      updateSizeFromPrice(response.price)
    }

    // Update available images
    allImages.value = response.all_images || []
    
    // Enable form fields after successful scrape
    hasScrapedData.value = true
  } catch (err) {
    error.value = 'Failed to scrape URL'
    console.error(err)
    hasScrapedData.value = false
  } finally {
    scraping.value = false
  }
}

function updateSizeFromPrice(price: number) {
  if (!price) {
    itemForm.value.size = 'Medium'
    return
  }
  
  if (price <= 25) {
    itemForm.value.size = 'Stocking'
  } else if (price <= 50) {
    itemForm.value.size = 'Small'
  } else if (price <= 100) {
    itemForm.value.size = 'Medium'
  } else {
    itemForm.value.size = 'Large'
  }
}
</script>

<style scoped>
.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 8px;
  max-height: 300px;
  overflow-y: auto;
  padding: 8px;
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 4px;
}

.image-item {
  cursor: pointer;
  border: 2px solid transparent;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.image-item:hover {
  transform: scale(1.05);
}

.image-item.selected {
  border-color: rgb(var(--v-theme-primary));
}

.v-img--selected {
  box-shadow: 0 0 0 2px rgb(var(--v-theme-primary));
}

/* Dark mode support */
:deep(.v-theme--dark) .image-grid {
  border-color: rgba(255, 255, 255, 0.12);
}
</style>
