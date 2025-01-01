<!-- src/pages/WishlistList.vue -->
<template>
  <div class="py-8">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h2 class="text-3xl font-bold text-primary mb-2">Wishlists</h2>
        <p class="text-light-subtle dark:text-dark-subtle">
          Manage and view wishlists
        </p>
      </div>
      <v-btn
        color="primary"
        class="px-6"
        prepend-icon="mdi-plus"
        @click="openCreateDialog"
      >
        New Wishlist
      </v-btn>
    </div>

    <!-- Tabs -->
    <v-tabs v-model="activeTab" class="mb-6">
      <v-tab value="my">
        <v-icon icon="mdi-account" class="mr-2" />
        My Wishlists
      </v-tab>
      <v-tab value="family">
        <v-icon icon="mdi-account-group" class="mr-2" />
        Family Wishlists
      </v-tab>
    </v-tabs>

    <v-window v-model="activeTab">
      <!-- My Wishlists -->
      <v-window-item value="my">
        <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <WishlistCard
            v-for="wishlist in store.myWishlists"
            :key="wishlist.id"
            :wishlist="wishlist"
            :editable="true"
            @edit="editWishlist"
            @delete="confirmDelete"
          />
          
          <!-- Add Wishlist Card -->
          <v-card
            class="border-2 border-dashed border-accent/30 hover:border-accent/50 transition-all duration-200 cursor-pointer flex items-center justify-center"
            elevation="0"
            height="100%"
            @click="openCreateDialog"
          >
            <div class="text-center p-6">
              <v-icon
                icon="mdi-plus-circle"
                size="large"
                class="text-accent mb-2"
              />
              <p class="text-light-subtle dark:text-dark-subtle font-medium">
                Create New Wishlist
              </p>
            </div>
          </v-card>
        </div>
      </v-window-item>

      <!-- Family Wishlists -->
      <v-window-item value="family">
        <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <WishlistCard
            v-for="wishlist in store.familyWishlists"
            :key="wishlist.id"
            :wishlist="wishlist"
            :editable="false"
          />
        </div>
      </v-window-item>
    </v-window>

    <!-- Create/Edit Dialog -->
    <v-dialog v-model="dialogVisible" max-width="500px">
      <v-card class="p-6">
        <h3 class="text-xl font-semibold mb-4">
          {{ editingWishlist ? 'Edit Wishlist' : 'Create New Wishlist' }}
        </h3>
        <v-form @submit.prevent="saveWishlist">
          <v-select
            v-model="wishlistForm.familyId"
            :items="userFamilies"
            item-title="name"
            item-value="id"
            label="Select Family"
            required
          />
          <v-text-field
            v-model="wishlistForm.name"
            label="Wishlist Name"
            required
            :rules="[v => !!v || 'Name is required']"
          />
          <div class="flex justify-end gap-3 mt-6">
            <v-btn
              variant="outlined"
              @click="dialogVisible = false"
            >
              Cancel
            </v-btn>
            <v-btn
              color="primary"
              type="submit"
              :loading="saving"
            >
              {{ editingWishlist ? 'Save Changes' : 'Create Wishlist' }}
            </v-btn>
          </div>
        </v-form>
      </v-card>
    </v-dialog>

    <!-- Confirm Delete Dialog -->
    <v-dialog v-model="deleteDialogVisible" max-width="400px">
      <v-card class="p-6">
        <h3 class="text-xl font-semibold mb-4">Confirm Delete</h3>
        <p class="mb-6">Are you sure you want to delete this wishlist? This action cannot be undone.</p>
        <div class="flex justify-end gap-3">
          <v-btn
            variant="outlined"
            @click="deleteDialogVisible = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="error"
            @click="deleteWishlist"
            :loading="deleting"
          >
            Delete
          </v-btn>
        </div>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAppStore } from '@/stores/useAppStore'
import { storeToRefs } from 'pinia'
import type { Wishlist } from '@/stores/useAppStore'
import WishlistCard from '@/components/WishlistCard.vue'

const store = useAppStore()
const { families } = storeToRefs(store)

const activeTab = ref('my')
const dialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const saving = ref(false)
const deleting = ref(false)

const editingWishlist = ref<Wishlist | null>(null)
const selectedWishlist = ref<Wishlist | null>(null)

const wishlistForm = ref({
  familyId: null as number | null,
  name: ''
})

// Computed
const userFamilies = computed(() => 
  families.value.filter(f => f.members.includes(store.currentUserId))
)

// Methods
const openCreateDialog = () => {
  editingWishlist.value = null
  wishlistForm.value = {
    familyId: null,
    name: ''
  }
  dialogVisible.value = true
}

const editWishlist = (wishlist: Wishlist) => {
  editingWishlist.value = wishlist
  wishlistForm.value = {
    familyId: wishlist.familyId,
    name: wishlist.name
  }
  dialogVisible.value = true
}

const saveWishlist = async () => {
  if (!wishlistForm.value.familyId) return
  
  saving.value = true
  try {
    if (editingWishlist.value) {
      await store.updateWishlist(editingWishlist.value.id, {
        name: wishlistForm.value.name,
        familyId: wishlistForm.value.familyId
      })
    } else {
      await store.createWishlist({
        name: wishlistForm.value.name,
        familyId: wishlistForm.value.familyId,
        ownerId: store.currentUserId
      })
    }
    dialogVisible.value = false
  } finally {
    saving.value = false
  }
}

const confirmDelete = (wishlist: Wishlist) => {
  selectedWishlist.value = wishlist
  deleteDialogVisible.value = true
}

const deleteWishlist = async () => {
  if (!selectedWishlist.value) return
  
  deleting.value = true
  try {
    await store.deleteWishlist(selectedWishlist.value.id)
    deleteDialogVisible.value = false
  } finally {
    deleting.value = false
  }
}
</script>
