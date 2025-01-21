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
          :color="isDragMode ? 'primary' : undefined"
          :variant="isDragMode ? 'flat' : 'outlined'"
          prepend-icon="mdi-drag"
          @click="toggleDragMode"
        >
          {{ isDragMode ? 'Exit Arrange Mode' : 'Arrange Items' }}
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
      v-if="error"
      type="error"
      class="mb-4"
    >
      {{ error }}
    </v-alert>

    <!-- Filters -->
    <div v-if="!loading && wishlist" class="mb-6">
      <v-expand-transition>
        <div v-show="showFilters">
          <v-card class="mb-4">
            <v-card-title class="d-flex align-center py-3 px-4">
              <v-icon icon="mdi-filter-variant" class="mr-2" />
              Filters
            </v-card-title>
            <v-divider />
            <v-card-text class="py-4">
              <!-- Search & Size Filters -->
              <div class="d-flex flex-wrap align-center gap-4">
                <v-text-field
                  v-model="filters.search"
                  label="Search items"
                  prepend-inner-icon="mdi-magnify"
                  density="comfortable"
                  hide-details
                  clearable
                  class="filter-field"
                />
                <v-select
                  v-model="filters.size"
                  :items="['All', 'Stocking', 'Small', 'Medium', 'Large']"
                  label="Size"
                  density="comfortable"
                  hide-details
                  class="filter-field"
                />
                <v-select
                  v-if="!isOwner"
                  v-model="filters.purchaseStatus"
                  :items="[
                    { title: 'All Items', value: 'all' },
                    { title: 'Available', value: 'available' },
                    { title: 'Purchased', value: 'purchased' }
                  ]"
                  item-title="title"
                  item-value="value"
                  label="Status"
                  density="comfortable"
                  hide-details
                  class="filter-field"
                />
              </div>

              <!-- Price Range Controls -->
              <v-divider class="my-4" />
              <div class="price-range-container">
                <div class="text-subtitle-2 mb-3">Price Range</div>
                <div class="d-flex flex-wrap align-center gap-4">
                  <div class="price-input-container">
                    <v-text-field
                      v-model="minPriceInput"
                      label="Min Price"
                      type="text"
                      prefix="$"
                      class="price-input"
                      density="comfortable"
                      hide-details
                      @input="handleMinPriceInput"
                    >
                      <template v-slot:append>
                        <div class="price-controls">
                          <v-btn
                            icon="mdi-chevron-up"
                            size="x-small"
                            variant="text"
                            density="comfortable"
                            @click="adjustPrice('min', 1)"
                          />
                          <v-btn
                            icon="mdi-chevron-down"
                            size="x-small"
                            variant="text"
                            density="comfortable"
                            @click="adjustPrice('min', -1)"
                          />
                        </div>
                      </template>
                    </v-text-field>
                  </div>

                  <span class="text-light-subtle dark:text-dark-subtle">to</span>

                  <div class="price-input-container">
                    <v-text-field
                      v-model="maxPriceInput"
                      label="Max Price"
                      type="text"
                      prefix="$"
                      class="price-input"
                      density="comfortable"
                      hide-details
                      @input="handleMaxPriceInput"
                    >
                      <template v-slot:append>
                        <div class="price-controls">
                          <v-btn
                            icon="mdi-chevron-up"
                            size="x-small"
                            variant="text"
                            density="comfortable"
                            @click="adjustPrice('max', 1)"
                          />
                          <v-btn
                            icon="mdi-chevron-down"
                            size="x-small"
                            variant="text"
                            density="comfortable"
                            @click="adjustPrice('max', -1)"
                          />
                        </div>
                      </template>
                    </v-text-field>
                  </div>

                  <v-btn
                    v-if="isPriceRangeActive"
                    icon="mdi-refresh"
                    size="small"
                    variant="text"
                    @click="resetPriceRange"
                    :disabled="loading"
                  />
                </div>
              </div>
            </v-card-text>
          </v-card>
        </div>
      </v-expand-transition>

      <!-- Filter Toggle Button -->
      <div class="d-flex align-center gap-2">
        <v-btn
          variant="text"
          :prepend-icon="showFilters ? 'mdi-filter-off' : 'mdi-filter'"
          @click="showFilters = !showFilters"
          size="small"
          :color="activeFiltersCount > 0 ? 'primary' : undefined"
        >
          {{ showFilters ? 'Hide Filters' : 'Show Filters' }}
          <template v-if="!showFilters && activeFiltersCount > 0">
            ({{ activeFiltersCount }})
          </template>
        </v-btn>
        <v-chip
          v-if="activeFiltersCount > 0"
          size="small"
          color="primary"
          variant="outlined"
          closable
          @click:close="resetFilters"
        >
          Clear All Filters
        </v-chip>
      </div>
    </div>

    <!-- Update the drag template -->
    <draggable
      v-if="isOwner && isDragMode"
      v-model="dragItems"
      class="items-grid"
      @end="handleDragEnd"
      item-key="id"
      handle=".drag-handle"
      :animation="200"
      ghost-class="ghost-item"
    >
      <template #item="{ element: item }">
        <div class="item-card">
          <div class="drag-handle">
            <v-icon icon="mdi-drag" />
          </div>
          <div class="item-image-container">
            <v-img
              :src="item.image_url || item.image || '/placeholder-gift.png'"
              :aspect-ratio="imageHeights[item.id] || 1"
              cover
              class="item-image"
              @load="onImageLoad($event, item.id)"
              @error="onImageError(item.id)"
            >
              <template v-slot:placeholder>
                <div class="d-flex align-center justify-center fill-height">
                  <v-progress-circular indeterminate color="primary" />
                </div>
              </template>
            </v-img>
            
            <!-- Add clickable overlay if link exists -->
            <a 
              v-if="item.link"
              :href="item.link"
              target="_blank"
              rel="noopener"
              class="image-link-overlay"
            >
              <v-icon
                icon="mdi-open-in-new"
                class="overlay-icon"
              />
            </a>
          </div>

          <div class="card-content">
            <div class="card-header">
              <span class="title">{{ item.title }}</span>
            </div>
            <div class="meta-info">
              <span>${{ item.price }}</span>
              <span>Size: {{ item.size }}</span>
            </div>
          </div>
        </div>
      </template>
    </draggable>

    <!-- Original masonry grid for non-drag mode -->
    <div v-else class="items-grid">
      <div
        v-for="item in dragItems"
        :key="item.id"
        class="item-card"
        :class="{ 'is-loading': !itemImagesLoaded[item.id] }"
      >
        <div class="item-image-container">
          <v-img
            :src="item.image_url || item.image || '/placeholder-gift.png'"
            :aspect-ratio="imageHeights[item.id] || 1"
            cover
            class="item-image"
            @load="onImageLoad($event, item.id)"
            @error="onImageError(item.id)"
          >
            <template v-slot:placeholder>
              <div class="d-flex align-center justify-center fill-height">
                <v-progress-circular indeterminate color="primary" />
              </div>
            </template>
          </v-img>
          
          <!-- Add clickable overlay if link exists -->
          <a 
            v-if="item.link"
            :href="item.link"
            target="_blank"
            rel="noopener"
            class="image-link-overlay"
          >
            <v-icon
              icon="mdi-open-in-new"
              class="overlay-icon"
            />
          </a>
        </div>

        <div class="card-content bg-light-surface dark:bg-dark-surface">
          <div class="card-header">
            <span class="title">{{ item.title }}</span>
            <v-chip
              v-if="!isOwner && item.is_purchased"
              color="success"
              size="small"
            >
              Purchased
            </v-chip>
          </div>

          <p class="description text-light-text dark:text-dark-text">
            {{ item.description }}
          </p>

          <div class="meta-info">
            <span>${{ item.price }}</span>
            <span>Size: {{ item.size }}</span>
          </div>

          <!-- Purchase Actions -->
          <div class="purchase-actions mt-3">
            <div v-if="!isOwner && item.is_purchased" class="purchased-info">
              Purchased by {{ item.purchased_by?.username }}
            </div>
            <v-btn
              v-else-if="!isOwner"
              block
              color="primary"
              size="small"
              :loading="loading"
              @click="handlePurchaseItem(item)"
            >
              Mark as Purchased
            </v-btn>
          </div>

          <div class="actions">
            <v-btn
              v-if="item.link"
              variant="text"
              prepend-icon="mdi-link"
              :href="item.link"
              target="_blank"
              class="text-truncate"
              max-width="200px"
            >
              <v-tooltip activator="parent" location="top">
                {{ item.link }}
              </v-tooltip>
              View Item
            </v-btn>
            <v-spacer />
            <template v-if="isOwner">
              <v-btn
                icon="mdi-pencil"
                variant="text"
                size="small"
                @click="openEditItemDialog(item)"
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
    </div>

    <!-- Dialogs -->
    <!-- ... item dialog, delete dialog, etc ... -->

    <!-- Item Dialog -->
    <v-dialog v-model="itemDialog.show" max-width="600px">
      <v-card class="d-flex flex-column" style="max-height: 90vh;">
        <v-card-title class="py-4 px-6">
          {{ itemDialog.mode === 'create' ? 'Add Item' : 'Edit Item' }}
        </v-card-title>

        <v-card-text class="flex-grow-1 overflow-y-auto px-6">
          <!-- Show tabs only in create mode -->
          <v-tabs v-if="itemDialog.mode === 'create'" v-model="activeTab">
            <v-tab value="auto">Auto-fill from URL</v-tab>
            <v-tab value="manual">Manual Entry</v-tab>
          </v-tabs>

          <v-window v-model="activeTab">
            <!-- Auto-fill tab (only shown in create mode) -->
            <v-window-item v-if="itemDialog.mode === 'create'" value="auto">
              <v-container class="pa-0">
                <v-form @submit.prevent="handleAutoFill">
                  <p class="text-body-1 mb-4">Enter a product URL to automatically fill the details</p>
                  <v-text-field
                    v-model="itemForm.link"
                    label="Product URL"
                    :error-messages="itemErrors.link"
                    @input="itemErrors.link = ''"
                    :disabled="scraping"
                    placeholder="https://example.com/product"
                    class="url-field"
                  >
                    <template v-slot:details v-if="itemForm.link">
                      <div class="text-truncate">
                        <v-tooltip activator="parent" location="bottom">
                          {{ itemForm.link }}
                        </v-tooltip>
                        {{ itemForm.link }}
                      </div>
                    </template>
                  </v-text-field>
                  
                  <!-- Replace the scraped data preview section in the auto-fill tab -->
                  <div v-if="hasScrapedData" class="mt-6">
                    <h3 class="text-h6 mb-4">Review & Edit Scraped Data</h3>
                    
                    <div class="scraped-data-preview">
                      <v-form>
                        <v-list>
                          <v-list-item>
                            <template v-slot:prepend>
                              <v-icon color="primary">mdi-format-title</v-icon>
                            </template>
                            <v-list-item-title>Title</v-list-item-title>
                            <v-text-field
                              v-model="itemForm.title"
                              variant="outlined"
                              density="compact"
                              hide-details
                              class="mt-2"
                            />
                          </v-list-item>

                          <v-list-item>
                            <template v-slot:prepend>
                              <v-icon color="primary">mdi-currency-usd</v-icon>
                            </template>
                            <v-list-item-title>Price</v-list-item-title>
                            <v-text-field
                              v-model="itemForm.price"
                              variant="outlined"
                              density="compact"
                              hide-details
                              type="number"
                              prefix="$"
                              class="mt-2"
                            />
                          </v-list-item>

                          <v-list-item>
                            <template v-slot:prepend>
                              <v-icon color="primary">mdi-text</v-icon>
                            </template>
                            <v-list-item-title>Description</v-list-item-title>
                            <v-textarea
                              v-model="itemForm.description"
                              variant="outlined"
                              density="compact"
                              hide-details
                              auto-grow
                              rows="3"
                              class="mt-2"
                            />
                          </v-list-item>

                          <v-list-item>
                            <template v-slot:prepend>
                              <v-icon color="primary">mdi-ruler</v-icon>
                            </template>
                            <v-list-item-title>Size</v-list-item-title>
                            <v-select
                              v-model="itemForm.size"
                              :items="['Stocking', 'Small', 'Medium', 'Large']"
                              variant="outlined"
                              density="compact"
                              hide-details
                              class="mt-2"
                            />
                          </v-list-item>

                          <!-- Image Selection -->
                          <v-list-item>
                            <template v-slot:prepend>
                              <v-icon color="primary">mdi-image</v-icon>
                            </template>
                            <v-list-item-title class="mb-2">Images</v-list-item-title>
                            
                            <!-- Selected Image Preview -->
                            <div v-if="selectedImagePreview" class="selected-image-preview mb-4">
                              <v-img
                                :src="selectedImagePreview"
                                height="200"
                                cover
                                class="rounded"
                              >
                                <template v-slot:placeholder>
                                  <div class="d-flex align-center justify-center fill-height">
                                    <v-progress-circular indeterminate color="primary" />
                                  </div>
                                </template>
                              </v-img>
                              <v-btn
                                color="error"
                                variant="text"
                                size="small"
                                class="mt-2"
                                @click="clearSelectedImage"
                                prepend-icon="mdi-close"
                              >
                                Clear Selected Image
                              </v-btn>
                            </div>

                            <!-- Available Images Grid -->
                            <div v-if="allImages.length">
                              <label class="text-subtitle-1 mb-2 d-block">Or select from scraped images:</label>
                              <div class="scraped-images-grid">
                                <div 
                                  v-for="(image, index) in filteredImages" 
                                  :key="index"
                                  class="scraped-image-item"
                                  :class="{ 'selected': image === itemForm.image_url }"
                                  @click="selectScrapedImage(image)"
                                >
                                  <v-img
                                    :src="image"
                                    :aspect-ratio="1"
                                    cover
                                    class="rounded"
                                    :class="{ 'v-img--selected': image === itemForm.image_url }"
                                    @load="checkImageQuality($event, image)"
                                  >
                                    <template v-slot:placeholder>
                                      <div class="d-flex align-center justify-center fill-height">
                                        <v-progress-circular indeterminate color="primary" />
                                      </div>
                                    </template>
                                  </v-img>
                                </div>
                              </div>
                            </div>

                            <!-- Manual Image Upload Option -->
                            <v-file-input
                              :model-value="itemForm.image"
                              @update:model-value="handleImageUpload"
                              accept="image/*"
                              label="Upload Image"
                              prepend-icon="mdi-camera"
                              :error-messages="itemErrors.image"
                              class="mt-4 file-input"
                              show-size
                              :truncate-length="30"
                            >
                              <template v-slot:selection="{ fileNames }">
                                <template v-for="fileName in fileNames" :key="fileName">
                                  <v-chip
                                    size="small"
                                    label
                                    color="primary"
                                    variant="outlined"
                                    class="text-truncate"
                                    style="max-width: 100%;"
                                  >
                                    <v-tooltip activator="parent" location="top">
                                      {{ fileName }}
                                    </v-tooltip>
                                    {{ fileName }}
                                  </v-chip>
                                </template>
                              </template>
                            </v-file-input>
                          </v-list-item>
                        </v-list>
                      </v-form>
                    </div>
                  </div>

                  <div class="d-flex gap-4 mt-6">
                    <v-btn
                      color="primary"
                      type="button"
                      @click="scrapeUrl"
                      :loading="scraping"
                      block
                    >
                      {{ hasScrapedData ? 'Rescrape URL' : 'Fill Auto-Magically' }}
                    </v-btn>
                    
                    <v-btn
                      v-if="hasScrapedData"
                      color="success"
                      type="submit"
                      block
                    >
                      Add to Wishlist
                    </v-btn>
                  </div>
                </v-form>
              </v-container>
            </v-window-item>

            <!-- Manual Entry / Edit Form -->
            <v-window-item value="manual">
              <v-container class="pa-0">
                <v-form @submit.prevent="handleItemSubmit">
                  <v-text-field
                    v-model="itemForm.title"
                    label="Title"
                    required
                    :error-messages="itemErrors.title"
                    @input="itemErrors.title = ''"
                    :disabled="!hasScrapedData && itemDialog.mode === 'create' && activeTab === 'auto'"
                  />

                  <v-textarea
                    v-model="itemForm.description"
                    label="Description"
                    :error-messages="itemErrors.description"
                    @input="itemErrors.description = ''"
                    :disabled="!hasScrapedData && itemDialog.mode === 'create' && activeTab === 'auto'"
                  />

                  <v-text-field
                    v-model="itemForm.price"
                    label="Price"
                    type="number"
                    required
                    prefix="$"
                    :error-messages="itemErrors.price"
                    @input="itemErrors.price = ''"
                    :disabled="!hasScrapedData && itemDialog.mode === 'create' && activeTab === 'auto'"
                  />

                  <v-select
                    v-model="itemForm.size"
                    :items="['Stocking', 'Small', 'Medium', 'Large']"
                    label="Size"
                    :disabled="!hasScrapedData && itemDialog.mode === 'create' && activeTab === 'auto'"
                  />

                  <!-- Show link field in edit mode -->
                  <v-text-field
                    v-if="itemDialog.mode === 'edit'"
                    v-model="itemForm.link"
                    label="Product URL"
                    :error-messages="itemErrors.link"
                    @input="itemErrors.link = ''"
                  />

                  <!-- Image Upload Section -->
                  <div class="mt-4">
                    <label class="text-subtitle-1 mb-2 d-block">Item Image</label>
                    
                    <!-- Image Upload -->
                    <div class="mb-4">
                      <v-file-input
                        :model-value="itemForm.image"
                        @update:model-value="handleImageUpload"
                        accept="image/*"
                        label="Upload Image"
                        prepend-icon="mdi-camera"
                        :error-messages="itemErrors.image"
                        class="mt-4 file-input"
                        show-size
                        :truncate-length="30"
                      >
                        <template v-slot:selection="{ fileNames }">
                          <template v-for="fileName in fileNames" :key="fileName">
                            <v-chip
                              size="small"
                              label
                              color="primary"
                              variant="outlined"
                              class="text-truncate"
                              style="max-width: 100%;"
                            >
                              <v-tooltip activator="parent" location="top">
                                {{ fileName }}
                              </v-tooltip>
                              {{ fileName }}
                            </v-chip>
                          </template>
                        </template>
                      </v-file-input>
                    </div>

                    <!-- Scraped Images (show only if available) -->
                    <div v-if="allImages.length">
                      <label class="text-subtitle-1 mb-2 d-block">Or select from scraped images:</label>
                      <div class="scraped-images-grid">
                        <div 
                          v-for="(image, index) in filteredImages" 
                          :key="index"
                          class="scraped-image-item"
                          :class="{ 'selected': image === itemForm.image_url }"
                          @click="selectScrapedImage(image)"
                        >
                          <v-img
                            :src="image"
                            :aspect-ratio="1"
                            cover
                            class="rounded"
                            :class="{ 'v-img--selected': image === itemForm.image_url }"
                            @load="checkImageQuality($event, image)"
                          >
                            <template v-slot:placeholder>
                              <div class="d-flex align-center justify-center fill-height">
                                <v-progress-circular indeterminate color="primary" />
                              </div>
                            </template>
                          </v-img>
                        </div>
                      </div>
                    </div>

                    <!-- Preview Selected Image -->
                    <div v-if="selectedImagePreview" class="mt-4">
                      <label class="text-subtitle-1 mb-2 d-block">Selected Image Preview:</label>
                      <div class="selected-image-preview">
                        <v-img
                          :src="selectedImagePreview"
                          height="200"
                          cover
                          class="rounded"
                        />
                      </div>
                    </div>
                  </div>
                </v-form>
              </v-container>
            </v-window-item>
          </v-window>
        </v-card-text>

        <v-divider></v-divider>
        
        <v-card-actions class="py-3 px-6">
          <v-spacer />
          <v-btn
            color="primary"
            @click="handleItemSubmit"
            :loading="loading"
            min-width="100"
            :disabled="!canSubmit"
          >
            {{ itemDialog.mode === 'create' ? 'Add' : 'Save Changes' }}
          </v-btn>
          <v-btn
            color="error"
            variant="text"
            @click="closeItemDialog"
            min-width="100"
            class="ml-3"
          >
            Cancel
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Edit Wishlist Dialog -->
    <v-dialog v-model="editDialog.show" max-width="500px">
      <v-card>
        <v-card-title>Edit Wishlist</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="editDialog.name"
            label="Wishlist Name"
            :error-messages="editDialog.error"
            @input="editDialog.error = ''"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn
            color="primary"
            @click="handleEditSubmit"
            :loading="loading"
          >
            Save
          </v-btn>
          <v-btn
            color="error"
            variant="text"
            @click="editDialog.show = false"
          >
            Cancel
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Item Dialog -->
    <v-dialog v-model="deleteItemDialog.show" max-width="400px">
      <v-card>
        <v-card-title>Delete Item</v-card-title>
        <v-card-text>
          Are you sure you want to delete this item?
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn
            color="error"
            @click="handleDeleteItem"
            :loading="loading"
          >
            Delete
          </v-btn>
          <v-btn
            variant="text"
            @click="deleteItemDialog.show = false"
          >
            Cancel
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { wishlistsService, type WishList, type WishListItem } from '@/services/wishlists'
import { useAppStore } from '@/stores/useAppStore'
import { format } from 'date-fns'
import draggable from 'vuedraggable'

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

const showFilters = ref(false)
const filters = ref({
  search: '',
  priceRange: [0, 1000] as [number, number],
  size: 'All',
  purchaseStatus: 'all'
})

const priceRange = computed(() => {
  if (!wishlist.value?.items.length) return { min: 0, max: 0 }
  const prices = wishlist.value.items
    .map(item => parseFloat(item.price) || 0)
    .filter(price => !isNaN(price))
  return {
    min: Math.min(...prices, 0),
    max: Math.max(...prices)
  }
})

const priceRangeFormatted = computed(() => ({
  min: filters.value.priceRange[0].toFixed(2),
  max: filters.value.priceRange[1].toFixed(2)
}))

// Add these new refs
const minPriceInput = ref('')
const maxPriceInput = ref('')

// Update price range watchers and handlers
function handleMinPriceInput(event: Event) {
  const input = event.target as HTMLInputElement
  const value = input.value.replace(/[^\d.]/g, '')
  const newMin = Math.max(Number(value) || 0, 0)
  const newMax = Math.max(filters.value.priceRange[1], newMin)
  filters.value.priceRange = [newMin, newMax]
  minPriceInput.value = newMin.toString()
}

function handleMaxPriceInput(event: Event) {
  const input = event.target as HTMLInputElement
  const value = input.value.replace(/[^\d.]/g, '')
  const newMax = Math.min(Number(value) || 0, priceRange.value.max)
  const newMin = Math.min(filters.value.priceRange[0], newMax)
  filters.value.priceRange = [newMin, newMax]
  maxPriceInput.value = newMax.toString()
}

function resetPriceRange() {
  filters.value.priceRange = [0, priceRange.value.max]
  minPriceInput.value = '0'
  maxPriceInput.value = priceRange.value.max.toString()
}

// Update the watch handler for wishlist
watch(() => wishlist.value, (newWishlist) => {
  if (newWishlist?.items.length) {
    const prices = newWishlist.items
      .map(item => parseFloat(item.price) || 0)
      .filter(price => !isNaN(price))
    const maxPrice = Math.max(...prices, 0)
    filters.value.priceRange = [0, maxPrice]
    minPriceInput.value = '0'
    maxPriceInput.value = maxPrice.toString()
  } else {
    filters.value.priceRange = [0, 0]
    minPriceInput.value = '0'
    maxPriceInput.value = '0'
  }
}, { immediate: true })

// Remove any slider-specific watchers and keep only this one
watch(() => filters.value.priceRange, () => {
  minPriceInput.value = filters.value.priceRange[0].toString()
  maxPriceInput.value = filters.value.priceRange[1].toString()
}, { deep: true })

const filteredItems = computed(() => {
  if (!wishlist.value?.items) return []
  
  return wishlist.value.items.filter(item => {
    // Search filter
    const searchMatch = !filters.value.search || 
      item.title.toLowerCase().includes(filters.value.search.toLowerCase()) ||
      item.description?.toLowerCase().includes(filters.value.search.toLowerCase())

    // Price range filter
    const price = Number(item.price) || 0
    const priceMatch = price >= filters.value.priceRange[0] && 
      price <= filters.value.priceRange[1]

    // Size filter
    const sizeMatch = filters.value.size === 'All' || 
      item.size === filters.value.size

    // Purchase status filter (for non-owners)
    let purchaseMatch = true
    if (!isOwner.value) {
      if (filters.value.purchaseStatus === 'available') {
        purchaseMatch = !item.is_purchased
      } else if (filters.value.purchaseStatus === 'purchased') {
        purchaseMatch = item.is_purchased
      }
    }

    return searchMatch && priceMatch && sizeMatch && purchaseMatch
  })
})

const itemImagesLoaded = ref<Record<number, boolean>>({})
const imageHeights = ref<Record<number, number>>({})

function onImageLoad(event: Event, itemId: number) {
  const img = event.target as HTMLImageElement
  if (img) {
    const aspectRatio = img.naturalWidth / img.naturalHeight
    imageHeights.value[itemId] = aspectRatio
    
    // Mark image as loaded
    itemImagesLoaded.value[itemId] = true
    
    // Add class based on aspect ratio
    const imageContainer = img.closest('.item-image-container')
    if (imageContainer) {
      if (aspectRatio > 1) {
        imageContainer.classList.add('landscape')
      } else {
        imageContainer.classList.add('portrait')
      }
    }
  }
}

function onImageError(itemId: number) {
  // Mark failed images as loaded to prevent infinite loading state
  itemImagesLoaded.value[itemId] = true
  // Set a default aspect ratio
  imageHeights.value[itemId] = 1
}

onMounted(async () => {
  await loadWishlist()
})

async function loadWishlist() {
  try {
    loading.value = true
    const wishlistId = Number(route.params.id)
    const data = await wishlistsService.getWishlist(wishlistId)
    
    // Sort items by priority before setting wishlist
    const sortedItems = [...data.items].sort((a, b) => a.priority - b.priority)
    
    // Update store with current order
    store.setItemOrder(wishlistId, sortedItems.map(item => item.id))
    
    // Set wishlist with sorted items
    wishlist.value = {
      ...data,
      items: sortedItems
    }
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
  
  // Reset form - remove priority from visible fields
  itemForm.value = {
    title: '',
    description: '',
    price: '',
    link: '',
    image_url: '',
    size: 'Medium',
    priority: 3, // Keep this as internal value
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
  selectedImagePreview.value = null
}

function openEditItemDialog(item: WishListItem) {
  itemDialog.value = {
    show: true,
    mode: 'edit',
    item
  }
  
  // Reset form with item data
  itemForm.value = {
    title: item.title,
    description: item.description || '',
    price: item.price,
    link: item.link || '',
    image_url: item.image_url || '',
    image: null, // Reset image file
    size: item.size || 'Medium',
    priority: item.priority || 3,
    wishlist: item.wishlist,
  }
  
  // Reset errors
  itemErrors.value = {
    title: '',
    description: '',
    price: '',
    link: '',
    image_url: '',
    image: '',
  }

  // Set image preview if exists
  selectedImagePreview.value = item.image_url || null
  
  // Enable form fields for editing
  hasScrapedData.value = true
  
  // Set to manual tab for editing
  activeTab.value = 'manual'
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
    
    // Create FormData for submission
    const formData = new FormData()
    formData.append('title', itemForm.value.title)
    formData.append('description', itemForm.value.description || '')
    formData.append('price', itemForm.value.price.toString())
    formData.append('link', itemForm.value.link || '')
    formData.append('size', itemForm.value.size)
    formData.append('wishlist', itemForm.value.wishlist.toString())
    
    // Preserve priority in edit mode, or use default in create mode
    const priority = itemDialog.value.mode === 'edit' && itemDialog.value.item 
      ? itemDialog.value.item.priority 
      : itemForm.value.priority
    formData.append('priority', priority.toString())
    
    // Handle image submission
    if (itemForm.value.image instanceof File) {
      formData.append('image', itemForm.value.image)
    } else if (itemForm.value.image_url) {
      formData.append('image_url', itemForm.value.image_url)
    }

    // For edit mode, explicitly handle image removal
    if (itemDialog.value.mode === 'edit' && !itemForm.value.image && !itemForm.value.image_url) {
      formData.append('image', '')
      formData.append('image_url', '')
    }

    if (itemDialog.value.mode === 'edit' && itemDialog.value.item) {
      await wishlistsService.updateItem(itemDialog.value.item.id, formData)
    } else {
      await wishlistsService.createItem(formData)
    }

    await loadWishlist()
    closeItemDialog()
    
  } catch (err: any) {
    if (err.response?.data) {
      itemErrors.value = {
        title: err.response.data.title?.[0] || '',
        description: '',
        price: err.response.data.price?.[0] || '',
        link: err.response.data.link?.[0] || '',
        image_url: err.response.data.image_url?.[0] || '',
        image: err.response.data.image?.[0] || ''
      }
    } else {
      error.value = 'Failed to save item'
      console.error('API Error:', err)
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
    imageQualities.value = {} // Reset image qualities
    
    // Clear previous data
    itemForm.value = {
      ...itemForm.value,
      title: '',
      description: '',
      price: '',
      image_url: '',
      size: 'Medium'
    }
    
    const response = await wishlistsService.scrapeUrl(itemForm.value.link)
    
    if (!response.title && !response.price) {
      throw new Error('Could not extract product information from URL')
    }
    
    // Update form with scraped data
    itemForm.value = {
      ...itemForm.value,
      title: response.title || '',
      description: response.description || '',
      price: response.price || '',
      image_url: response.image_url || ''
    }

    // Update size based on scraped price
    if (response.price) {
      updateSizeFromPrice(response.price)
    }

    // Update available images
    allImages.value = response.all_images || []
    
    // Enable form fields after successful scrape
    hasScrapedData.value = true
    
    // Select first image if available
    if (response.image_url) {
      selectScrapedImage(response.image_url)
    }
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : 'Failed to scrape URL'
    error.value = errorMessage
    console.error(err)
    hasScrapedData.value = false
  } finally {
    scraping.value = false
  }
}

function updateSizeFromPrice(price: number | string) {
  // Convert price to number if it's a string
  const numPrice = typeof price === 'string' ? parseFloat(price) : price
  
  if (!numPrice || isNaN(numPrice)) {
    itemForm.value.size = 'Medium' // Default size
    return
  }
  
  if (numPrice <= 25) {
    itemForm.value.size = 'Stocking'
  } else if (numPrice <= 50) {
    itemForm.value.size = 'Small'
  } else if (numPrice <= 100) {
    itemForm.value.size = 'Medium'
  } else {
    itemForm.value.size = 'Large'
  }
}

// Add a watcher for the price field
watch(() => itemForm.value.price, (newPrice) => {
  if (newPrice !== '') {
    updateSizeFromPrice(newPrice)
  }
})

const hasActiveFilters = computed(() => 
  filters.value.search || 
  filters.value.size !== 'All' || 
  isPriceRangeActive.value ||
  (!isOwner.value && filters.value.purchaseStatus !== 'all')
)

const isPriceRangeActive = computed(() => {
  if (!Array.isArray(filters.value.priceRange)) return false
  const [min, max] = filters.value.priceRange
  return min !== priceRange.value.min || max !== priceRange.value.max
})

const activeFiltersCount = computed(() => {
  let count = 0
  if (filters.value.search) count++
  if (filters.value.size !== 'All') count++
  if (isPriceRangeActive.value) count++
  if (!isOwner.value && filters.value.purchaseStatus !== 'all') count++
  return count
})

const getPurchaseStatusLabel = computed(() => {
  const statusMap = {
    all: 'All Items',
    available: 'Available',
    purchased: 'Purchased'
  }
  return statusMap[filters.value.purchaseStatus]
})

const selectedImagePreview = ref<string | null>(null)

function handleImageUpload(fileOrFiles: File | File[] | null) {
  // Handle single file upload
  const file = Array.isArray(fileOrFiles) ? fileOrFiles[0] : fileOrFiles

  if (!file) {
    itemForm.value.image = null
    itemForm.value.image_url = itemDialog.value.mode === 'edit' ? 
      itemDialog.value.item?.image_url || '' : ''
    selectedImagePreview.value = itemDialog.value.mode === 'edit' ? 
      itemDialog.value.item?.image_url || null : null
    return
  }

  // Validate file size
  if (file.size > 5 * 1024 * 1024) { // 5MB limit
    itemErrors.value.image = 'Image size should be less than 5MB'
    itemForm.value.image = null
    selectedImagePreview.value = null
    return
  }

  // Clear any existing image URL
  itemForm.value.image_url = ''
  itemForm.value.image = file

  // Revoke previous blob URL if exists
  if (selectedImagePreview.value?.startsWith('blob:')) {
    URL.revokeObjectURL(selectedImagePreview.value)
  }
  
  // Create new blob URL
  selectedImagePreview.value = URL.createObjectURL(file)
}

function selectScrapedImage(imageUrl: string) {
  itemForm.value.image_url = imageUrl
  itemForm.value.image = null  // Clear any uploaded file
  selectedImagePreview.value = imageUrl
}

// Clean up object URLs when dialog closes
watch(() => itemDialog.value.show, (show) => {
  if (!show && selectedImagePreview.value) {
    // Only revoke if it's a blob URL
    if (selectedImagePreview.value.startsWith('blob:')) {
      URL.revokeObjectURL(selectedImagePreview.value)
    }
    selectedImagePreview.value = null
  }
})

// Add these refs
const isDragMode = ref(false)
const dragItems = computed({
  get: () => {
    const orderedIds = store.getItemOrder(wishlist.value?.id || 0)
    if (orderedIds.length) {
      const orderedItems = orderedIds
        .map(id => filteredItems.value.find(item => item.id === id))
        .filter(Boolean) as WishListItem[]
      
      // Add any new items that aren't in the order yet
      const remainingItems = filteredItems.value.filter(
        item => !orderedIds.includes(item.id)
      )
      
      return [...orderedItems, ...remainingItems]
    }
    return [...filteredItems.value].sort((a, b) => a.priority - b.priority)
  },
  set: async (items) => {
    if (!wishlist.value?.id) return

    const itemIds = items.map(item => item.id)
    
    // Update store immediately for optimistic update
    store.setItemOrder(wishlist.value.id, itemIds)
    
    try {
      // Send to backend
      const updatedItems = await wishlistsService.updateItemsOrder(wishlist.value.id, itemIds)
      
      // Update the wishlist with the returned items
      if (wishlist.value) {
        wishlist.value = {
          ...wishlist.value,
          items: updatedItems
        }
      }
    } catch (error) {
      console.error('Failed to update items order:', error)
      await loadWishlist()
    }
  }
})

// Add these methods
function toggleDragMode() {
  isDragMode.value = !isDragMode.value
  
  // When exiting drag mode, update the wishlist items order
  if (!isDragMode.value && wishlist.value) {
    const orderedIds = store.getItemOrder(wishlist.value.id)
    if (orderedIds.length) {
      // Update the items array with the current order
      wishlist.value = {
        ...wishlist.value,
        items: orderedIds
          .map(id => wishlist.value!.items.find(item => item.id === id))
          .filter(Boolean) as WishListItem[]
      }
    }
  }
}

async function handleDragEnd(evt: any) {
  if (evt.oldIndex === evt.newIndex) return
  evt.preventDefault()
}

// Add these refs for edit dialog
const editDialog = ref({
  show: false,
  name: '',
  error: ''
})

// Add these methods
function openEditDialog() {
  if (!wishlist.value) return
  editDialog.value = {
    show: true,
    name: wishlist.value.name,
    error: ''
  }
}

async function handleEditSubmit() {
  if (!wishlist.value) return
  
  try {
    loading.value = true
    await wishlistsService.updateWishlist(wishlist.value.id, {
      name: editDialog.value.name,
      family: wishlist.value.family
    })
    await loadWishlist()
    editDialog.value.show = false
  } catch (err: any) {
    if (err.response?.data?.name) {
      editDialog.value.error = err.response.data.name[0]
    } else {
      error.value = 'Failed to update wishlist'
    }
    console.error(err)
  } finally {
    loading.value = false
  }
}

// Add these refs
const imageQualities = ref<Record<string, boolean>>({})
const minimumImageSize = 200 // Minimum width/height in pixels

// Add this computed property
const filteredImages = computed(() => 
  allImages.value.filter(image => imageQualities.value[image] !== false)
)

// Add this method
function checkImageQuality(event: Event, imageUrl: string) {
  const img = event.target as HTMLImageElement
  if (img) {
    // Check if image meets minimum size requirements
    const isGoodQuality = img.naturalWidth >= minimumImageSize && 
                         img.naturalHeight >= minimumImageSize &&
                         img.fileSize >= 500 * 1024; // Ensure image is 500KB or more
    imageQualities.value[imageUrl] = isGoodQuality
  }
}

function resetFilters() {
  filters.value = {
    search: '',
    priceRange: [priceRange.value.min, priceRange.value.max] as [number, number],
    size: 'All',
    purchaseStatus: 'all'
  }
  showFilters.value = false
}

// Add these watchers after the other watchers
watch(() => filters.value.priceRange[0], (newMin) => {
  // Ensure min doesn't exceed max
  if (newMin > filters.value.priceRange[1]) {
    filters.value.priceRange = [filters.value.priceRange[1], filters.value.priceRange[1]]
  }
  // Ensure min isn't negative
  if (newMin < 0) {
    filters.value.priceRange = [0, filters.value.priceRange[1]]
  }
})

watch(() => filters.value.priceRange[1], (newMax) => {
  // Ensure max isn't less than min
  if (newMax < filters.value.priceRange[0]) {
    filters.value.priceRange = [filters.value.priceRange[0], filters.value.priceRange[0]]
  }
  // Ensure max doesn't exceed the maximum allowed price
  if (newMax > priceRange.value.max) {
    filters.value.priceRange = [filters.value.priceRange[0], priceRange.value.max]
  }
})

// Update price range validation watchers
watch(() => filters.value.priceRange, (newRange) => {
  // Ensure values are numbers and within valid range
  let [min, max] = newRange.map(val => 
    Math.min(Math.max(Number(val) || 0, priceRange.value.min), priceRange.value.max)
  )
  
  // Ensure min doesn't exceed max
  if (min > max) {
    min = max
  }
  
  // Update if values were corrected
  if (min !== newRange[0] || max !== newRange[1]) {
    filters.value.priceRange = [min, max] as [number, number]
  }
}, { deep: true })

function adjustPrice(type: 'min' | 'max', delta: number) {
  if (type === 'min') {
    const newValue = Math.max(Number(minPriceInput.value) + delta, 0)
    handleMinPriceInput({ target: { value: newValue.toString() } } as any)
  } else {
    const newValue = Math.min(Number(maxPriceInput.value) + delta, priceRange.value.max)
    handleMaxPriceInput({ target: { value: newValue.toString() } } as any)
  }
}

// Add these new refs
const activeTab = ref('auto')
const canSubmit = computed(() => {
  if (itemDialog.value.mode === 'edit') {
    return !!itemForm.value.title && !!itemForm.value.price
  }
  
  if (activeTab.value === 'auto') {
    return hasScrapedData.value
  }
  
  return !!itemForm.value.title && !!itemForm.value.price
})

function closeItemDialog() {
  itemDialog.value.show = false
  activeTab.value = 'auto'
  hasScrapedData.value = false
  selectedImagePreview.value = null
  
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
  
  // Reset errors
  itemErrors.value = {
    title: '',
    description: '',
    price: '',
    link: '',
    image_url: '',
  }
  
  allImages.value = []
}

async function handleAutoFill(e: Event) {
  e.preventDefault()
  
  if (!hasScrapedData.value) {
    error.value = 'Please scrape a URL first'
    return
  }

  try {
    loading.value = true
    
    // Create FormData for submission
    const formData = new FormData()
    formData.append('title', itemForm.value.title)
    formData.append('description', itemForm.value.description || '')
    formData.append('price', itemForm.value.price.toString())
    formData.append('link', itemForm.value.link || '')
    formData.append('size', itemForm.value.size)
    formData.append('wishlist', route.params.id.toString())
    
    // Handle image
    if (itemForm.value.image_url) {
      formData.append('image_url', itemForm.value.image_url)
    }

    await wishlistsService.createItem(formData)
    await loadWishlist()
    closeItemDialog()
    
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
      error.value = 'Failed to add item'
    }
  } finally {
    loading.value = false
  }
}

// Update clearSelectedImage to handle edit mode
function clearSelectedImage() {
  itemForm.value.image_url = ''
  itemForm.value.image = null
  if (itemDialog.value.mode === 'edit') {
    // In edit mode, revert to original image if it exists
    itemForm.value.image_url = itemDialog.value.item?.image_url || ''
    selectedImagePreview.value = itemDialog.value.item?.image_url || null
  } else {
    selectedImagePreview.value = null
  }
}

</script>

<style scoped>
/* Update grid styles */
.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
  padding: 24px;
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
  background: rgb(var(--v-theme-background));
}

.item-card {
  position: relative;
  background: rgb(var(--v-theme-surface));
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease, opacity 0.3s ease;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.item-image-container {
  position: relative;
  width: 100%;
  padding-top: 100%;
  overflow: hidden;
  background: rgb(255, 255, 255);
  cursor: pointer;
}

/* Dark theme background */
:deep(.v-theme--dark) .item-image-container {
  background: rgb(18, 18, 18);
}

.item-image {
  position: absolute !important;
  top: 50% !important;
  left: 50% !important;
  transform: translate(-50%, -50%);
  width: 100% !important;
  height: 100% !important;
  z-index: 0; /* Ensure image stays behind overlay */
}

/* Remove filters and background from images */
:deep(.v-img__img) {
  object-fit: contain !important;
  background: none !important;
  filter: none !important;
}

/* Update card styles */
.card-content {
  padding: 1rem;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}

.title {
  font-weight: 600;
  font-size: 1.1rem;
  flex: 1;
  margin-right: 12px;
}

.description {
  font-size: 0.875rem;
  line-height: 1.4;
}

.meta-info {
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
  color: var(--v-theme-text-subtle);
  margin-top: 0.5rem;
}

.purchased-info {
  font-size: 0.875rem;
  color: var(--v-theme-success);
}

.actions {
  display: flex;
  align-items: center;
  margin-top: auto;
  padding-top: 12px;
  border-top: 1px solid rgba(var(--v-border-color), 0.12);
}

/* Ghost item styles */
.ghost-item {
  opacity: 0.5;
}

.sortable-ghost {
  opacity: 0.5;
}

.sortable-drag {
  cursor: grabbing;
}

/* Add styles for different aspect ratios */
.item-image-container.landscape .item-image :deep(.v-img__img) {
  height: auto !important;
  width: 100% !important;
}

.item-image-container.portrait .item-image :deep(.v-img__img) {
  width: auto !important;
  height: 100% !important;
}

/* Update responsive styles */
@media (max-width: 599px) {
  .items-grid,
  .drag-grid {
    grid-template-columns: 1fr;
    padding: 16px;
    gap: 16px;
  }

  .item-card,
  .drag-item {
    min-width: 100%;
  }

  .item-image-container {
    padding-top: 75%; /* Slightly shorter on mobile */
  }
}

/* Update drag-related styles */
.drag-handle {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 2;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(var(--v-theme-surface), 0.9);
  border-radius: 50%;
  cursor: move;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

:deep(.v-theme--dark) .drag-handle {
  background: rgba(var(--v-theme-surface), 0.9);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.ghost-item {
  opacity: 0.5;
}

.sortable-ghost {
  opacity: 0.5;
}

.sortable-drag {
  cursor: grabbing;
}

/* Remove old drag styles */
.drag-grid,
.drag-item,
.drag-content {
  /* Remove these style blocks if they exist */
}

/* Add these styles */
.image-link-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s ease;
  z-index: 1;
  text-decoration: none;
}

.overlay-icon {
  opacity: 0;
  transform: scale(0.8);
  transition: all 0.2s ease;
  color: white;
  font-size: 32px;
}

.image-link-overlay:hover {
  background: rgba(0, 0, 0, 0.3);
}

.image-link-overlay:hover .overlay-icon {
  opacity: 1;
  transform: scale(1);
}

/* Dark theme adjustments */
:deep(.v-theme--dark) .image-link-overlay:hover {
  background: rgba(0, 0, 0, 0.5);
}

.scraped-images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 16px;
}

.scraped-image-item {
  cursor: pointer;
  transition: transform 0.2s ease;
}

.scraped-image-item.selected {
  border: 2px solid var(--v-theme-primary);
  transform: scale(1.05);
}

.purchase-actions {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(var(--v-border-color), 0.12);
}

/* Filter Styles */
.filter-field {
  min-width: 180px;
  max-width: 220px;
}

.price-range-container {
  margin-top: 1rem;
}

.price-input-container {
  flex: 1;
  min-width: 160px;
  max-width: 180px;
}

.price-input {
  width: 100%;
}

.price-controls {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

/* Responsive adjustments */
@media (max-width: 599px) {
  .filter-field,
  .price-input-container {
    min-width: 100%;
    max-width: 100%;
  }
}
</style>
