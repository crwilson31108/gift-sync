<!-- src/pages/WishlistList.vue -->
<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-light-text dark:text-dark-text">
        Wishlists
      </h1>
      <v-btn
        color="primary"
        prepend-icon="mdi-plus"
        @click="openCreateDialog"
      >
        New Wishlist
      </v-btn>
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
      v-else-if="!allWishlists.length"
      class="text-center py-12"
    >
      <v-icon
        icon="mdi-gift-outline"
        size="64"
        class="text-light-subtle dark:text-dark-subtle mb-4"
      />
      <h3 class="text-xl font-medium text-light-text dark:text-dark-text mb-2">
        No Wishlists Yet
      </h3>
      <p class="text-light-subtle dark:text-dark-subtle mb-4">
        Create your first wishlist to start adding items
      </p>
      <v-btn
        color="primary"
        prepend-icon="mdi-plus"
        @click="openCreateDialog"
      >
        Create Wishlist
      </v-btn>
    </div>

    <div v-else>
      <!-- Tabs -->
      <v-tabs
        v-model="activeTab"
        color="primary"
        class="mb-6"
      >
        <v-tab value="my" class="tab-with-badge">
          <span class="tab-label">My Wishlists</span>
          <v-badge
            :content="myWishlists.length.toString()"
            :model-value="myWishlists.length > 0"
            color="primary"
            class="ml-4"
            location="end center"
          />
        </v-tab>
        <v-tab value="others" class="tab-with-badge">
          <span class="tab-label">Others' Wishlists</span>
          <v-badge
            :content="othersWishlists.length.toString()"
            :model-value="othersWishlists.length > 0"
            color="primary"
            class="ml-4"
            location="end center"
          />
        </v-tab>
      </v-tabs>

      <!-- Tab Content -->
      <v-window v-model="activeTab">
        <!-- My Wishlists Tab -->
        <v-window-item value="my">
          <div v-if="myWishlists.length" class="wishlist-grid">
            <WishlistCard
              v-for="wishlist in sortedMyWishlists"
              :key="wishlist.id"
              :wishlist="wishlist"
              ref="wishlistCards"
              @edit="openEditDialog"
              @delete="confirmDelete"
            >
              <template #preview>
                <div class="grid grid-cols-2 gap-1 mb-2">
                  <v-img
                    v-for="item in getTopPriorityItems(wishlist.items, 4)"
                    :key="item.id"
                    :src="getItemImage(item)"
                    :alt="item.title"
                    cover
                    class="rounded"
                    height="96"
                    @load="handleImageLoad(wishlist.id)"
                    @error="handleImageError(wishlist.id)"
                  >
                    <template v-slot:placeholder>
                      <div class="d-flex align-center justify-center fill-height">
                        <v-progress-circular indeterminate color="primary" />
                      </div>
                    </template>
                  </v-img>
                </div>
              </template>
              <template #actions>
                <v-btn
                  variant="text"
                  color="primary"
                  :to="`/wishlists/${wishlist.id}`"
                >
                  View
                </v-btn>
              </template>
            </WishlistCard>
          </div>
          <div 
            v-else 
            class="text-center py-12 text-light-subtle dark:text-dark-subtle"
          >
            You haven't created any wishlists yet
          </div>
        </v-window-item>

        <!-- Others' Wishlists Tab -->
        <v-window-item value="others">
          <div v-if="othersWishlists.length" class="wishlist-grid">
            <WishlistCard
              v-for="wishlist in sortedOthersWishlists"
              :key="wishlist.id"
              :wishlist="wishlist"
              ref="wishlistCards"
            >
              <template #preview>
                <div class="grid grid-cols-2 gap-1 mb-2">
                  <v-img
                    v-for="item in getTopPriorityItems(wishlist.items, 4)"
                    :key="item.id"
                    :src="getItemImage(item)"
                    :alt="item.title"
                    cover
                    class="rounded"
                    height="96"
                    @load="handleImageLoad(wishlist.id)"
                    @error="handleImageError(wishlist.id)"
                  >
                    <template v-slot:placeholder>
                      <div class="d-flex align-center justify-center fill-height">
                        <v-progress-circular indeterminate color="primary" />
                      </div>
                    </template>
                  </v-img>
                </div>
              </template>
              <template #actions>
                <v-btn
                  variant="text"
                  color="primary"
                  :to="`/wishlists/${wishlist.id}`"
                >
                  View
                </v-btn>
              </template>
            </WishlistCard>
          </div>
          <div 
            v-else 
            class="text-center py-12 text-light-subtle dark:text-dark-subtle"
          >
            No wishlists from other users yet
          </div>
        </v-window-item>
      </v-window>
    </div>

    <!-- Create/Edit Dialog -->
    <v-dialog
      v-model="dialog.show"
      max-width="500"
    >
      <v-card>
        <v-card-title>
          {{ dialog.isEdit ? 'Edit Wishlist' : 'Create Wishlist' }}
        </v-card-title>

        <v-card-text>
          <v-form @submit.prevent="handleSubmit">
            <v-text-field
              v-model="form.name"
              label="Wishlist Name"
              required
              :error-messages="errors.name"
            />
            
            <v-select
              v-model="form.family"
              :items="families"
              label="Select Family"
              item-title="name"
              item-value="id"
              required
              :error-messages="errors.family"
            />
          </v-form>
        </v-card-text>

        <v-card-actions>
          <v-spacer />
          <v-btn
            variant="text"
            @click="dialog.show = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="primary"
            :loading="loading"
            @click="handleSubmit"
          >
            {{ dialog.isEdit ? 'Save Changes' : 'Create' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Confirmation -->
    <v-dialog
      v-model="deleteDialog.show"
      max-width="400"
    >
      <v-card>
        <v-card-title class="text-error">
          Delete Wishlist
        </v-card-title>
        <v-card-text>
          Are you sure you want to delete "{{ deleteDialog.wishlist?.name }}"? This action cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn
            variant="text"
            @click="deleteDialog.show = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="error"
            :loading="loading"
            @click="handleDelete"
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
import { useRoute } from 'vue-router'
import { useAppStore } from '@/stores/useAppStore'
import { wishlistsService, type WishList } from '@/services/wishlists'
import { familiesService, type Family } from '@/services/families'
import WishlistCard from '@/components/WishlistCard.vue'

const store = useAppStore()
const route = useRoute()
const allWishlists = ref<WishList[]>([])
const families = ref<Family[]>([])
const loading = ref(false)
const error = ref('')

// Computed properties for filtered wishlists
const myWishlists = computed(() => 
  allWishlists.value.filter(wishlist => 
    wishlist.owner.id === store.currentUser?.id
  )
)

const othersWishlists = computed(() => 
  allWishlists.value.filter(wishlist => 
    wishlist.owner.id !== store.currentUser?.id
  )
)

const dialog = ref({
  show: false,
  isEdit: false,
  wishlist: null as WishList | null
})

const form = ref({
  name: '',
  family: null as number | null
})

const errors = ref({
  name: '',
  family: ''
})

const deleteDialog = ref({
  show: false,
  wishlist: null as WishList | null
})

// Add refs for card management
const wishlistCards = ref<InstanceType<typeof WishlistCard>[]>([])

// Add computed properties for sorted wishlists
const sortedMyWishlists = computed(() => 
  [...myWishlists.value].sort((a, b) => {
    // Sort by creation date, newest first
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  })
)

const sortedOthersWishlists = computed(() => 
  [...othersWishlists.value].sort((a, b) => {
    // Sort by creation date, newest first
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  })
)

// Fetch initial data
onMounted(async () => {
  try {
    loading.value = true
    const [wishlistsData, familiesData] = await Promise.all([
      wishlistsService.getWishlists({
        family: Number(route.query.family) || undefined,
        owner: Number(route.query.owner) || undefined
      }),
      familiesService.getFamilies()
    ])
    allWishlists.value = wishlistsData
    families.value = familiesData
  } catch (err) {
    error.value = 'Failed to load wishlists'
    console.error(err)
  } finally {
    loading.value = false
  }
})

function openCreateDialog() {
  dialog.value = {
    show: true,
    isEdit: false,
    wishlist: null
  }
  form.value = {
    name: '',
    family: null
  }
  errors.value = {
    name: '',
    family: ''
  }
}

function openEditDialog(wishlist: WishList) {
  dialog.value = {
    show: true,
    isEdit: true,
    wishlist
  }
  form.value = {
    name: wishlist.name,
    family: wishlist.family
  }
  errors.value = {
    name: '',
    family: ''
  }
}

function confirmDelete(wishlist: WishList) {
  deleteDialog.value = {
    show: true,
    wishlist
  }
}

async function handleSubmit() {
  if (!form.value.family) {
    errors.value.family = 'Please select a family'
    return
  }

  try {
    loading.value = true
    errors.value = { name: '', family: '' }

    if (dialog.value.isEdit && dialog.value.wishlist) {
      await wishlistsService.updateWishlist(dialog.value.wishlist.id, form.value)
    } else {
      await wishlistsService.createWishlist(form.value as Required<typeof form.value>)
    }

    // Refresh wishlists list
    allWishlists.value = await wishlistsService.getWishlists({
      family: Number(route.query.family) || undefined,
      owner: Number(route.query.owner) || undefined
    })
    dialog.value.show = false
  } catch (err: any) {
    if (err.response?.data) {
      errors.value.name = err.response.data.name?.[0] || ''
      errors.value.family = err.response.data.family?.[0] || ''
    } else {
      error.value = 'An error occurred'
    }
  } finally {
    loading.value = false
  }
}

async function handleDelete() {
  if (!deleteDialog.value.wishlist) return

  try {
    loading.value = true
    await wishlistsService.deleteWishlist(deleteDialog.value.wishlist.id)
    allWishlists.value = allWishlists.value.filter(w => w.id !== deleteDialog.value.wishlist?.id)
    deleteDialog.value.show = false
  } catch (err) {
    error.value = 'Failed to delete wishlist'
    console.error(err)
  } finally {
    loading.value = false
  }
}

// Add this with other refs
const activeTab = ref('my')

function getTopPriorityItems(items: any[], count: number = 4) {
  return (items || [])
    .sort((a, b) => {
      // First by priority
      const priorityDiff = (a.priority || 0) - (b.priority || 0)
      if (priorityDiff !== 0) return priorityDiff
      // Then by creation date if priorities are equal
      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    })
    .slice(0, count)
}

// Add image handling functions
function handleImageLoad(wishlistId: number) {
  const card = wishlistCards.value.find(
    card => card.$props.wishlist.id === wishlistId
  )
  if (card) {
    card.handleImageLoad()
  }
}

function handleImageError(wishlistId: number) {
  // Count errors as loaded to prevent infinite loading state
  handleImageLoad(wishlistId)
}

// Update getItemImage to handle errors better
function getItemImage(item: any): string {
  if (item.image_url) return item.image_url
  if (item.image) return item.image
  return '/placeholder-gift.png' // Make sure this placeholder exists in public folder
}
</script>

<style scoped>
/* Optional: Custom styling for the tabs */
:deep(.v-tabs) {
  border-bottom: 1px solid rgba(var(--v-border-color), 0.12);
}

:deep(.v-tab) {
  text-transform: none;
  font-weight: 500;
  padding: 0 24px;
  min-width: 180px;
}

:deep(.tab-with-badge) {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

:deep(.tab-label) {
  margin-right: 8px;
}

:deep(.v-tab--selected) {
  font-weight: 600;
}

:deep(.v-badge__badge) {
  font-size: 12px;
  min-width: 20px;
  height: 20px;
  margin-left: 4px;
}

/* Update grid styles */
.wishlist-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  grid-auto-flow: row dense; /* Ensures dense packing */
  padding: 16px;
}

/* Ensure consistent card heights */
:deep(.v-card) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

:deep(.v-card__text) {
  flex-grow: 1;
}

/* Preview grid styles */
.preview-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  grid-template-rows: repeat(2, 1fr);
  gap: 4px;
  aspect-ratio: 1;
}

.preview-grid :deep(.v-img) {
  aspect-ratio: 1;
  width: 100%;
  height: 100%;
}
</style>
