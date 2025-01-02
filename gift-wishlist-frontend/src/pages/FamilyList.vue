<!-- src/pages/FamilyList.vue -->
<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-light-text dark:text-dark-text">
        My Families
      </h1>
      <v-btn
        color="primary"
        prepend-icon="mdi-plus"
        @click="openCreateDialog"
      >
        New Family
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
      v-else-if="!families.length"
      class="text-center py-12"
    >
      <v-icon
        icon="mdi-account-group-outline"
        size="64"
        class="text-light-subtle dark:text-dark-subtle mb-4"
      />
      <h3 class="text-xl font-medium text-light-text dark:text-dark-text mb-2">
        No Families Yet
      </h3>
      <p class="text-light-subtle dark:text-dark-subtle mb-4">
        Create your first family to start managing wishlists together
      </p>
      <v-btn
        color="primary"
        prepend-icon="mdi-plus"
        @click="openCreateDialog"
      >
        Create Family
      </v-btn>
    </div>

    <!-- Families List -->
    <div 
      v-else 
      class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
    >
      <v-card
        v-for="family in families"
        :key="family.id"
        class="bg-light-surface dark:bg-dark-surface"
      >
        <v-card-title class="flex justify-between items-center">
          {{ family.name }}
          <v-menu location="bottom end">
            <template v-slot:activator="{ props }">
              <v-btn
                icon="mdi-dots-vertical"
                variant="text"
                v-bind="props"
              />
            </template>
            <v-list>
              <v-list-item
                prepend-icon="mdi-pencil"
                title="Edit"
                @click="openEditDialog(family)"
              />
              <v-list-item
                prepend-icon="mdi-delete"
                title="Delete"
                color="error"
                @click="confirmDelete(family)"
              />
            </v-list>
          </v-menu>
        </v-card-title>

        <v-card-text>
          <div class="flex items-center space-x-1 mb-2">
            <v-icon
              icon="mdi-account-multiple"
              size="small"
              class="text-light-subtle dark:text-dark-subtle"
            />
            <span class="text-sm text-light-subtle dark:text-dark-subtle">
              {{ family.members.length }} members
            </span>
          </div>
          <v-avatar-group max="3">
            <v-avatar
              v-for="member in family.members"
              :key="member.id"
              size="32"
              color="primary"
            >
              <v-img
                v-if="member.profile_picture"
                :src="member.profile_picture"
                :alt="member.username"
              />
              <span v-else class="text-sm">
                {{ member.username[0].toUpperCase() }}
              </span>
            </v-avatar>
          </v-avatar-group>
        </v-card-text>

        <v-card-actions>
          <v-btn
            variant="text"
            :to="`/families/${family.id}`"
          >
            View Details
          </v-btn>
        </v-card-actions>
      </v-card>
    </div>

    <!-- Create/Edit Dialog -->
    <v-dialog
      v-model="dialog.show"
      max-width="500"
    >
      <v-card>
        <v-card-title>
          {{ dialog.isEdit ? 'Edit Family' : 'Create New Family' }}
        </v-card-title>

        <v-card-text>
          <v-form @submit.prevent="handleSubmit">
            <v-text-field
              v-model="form.name"
              label="Family Name"
              required
              :error-messages="errors.name"
            />
            
            <v-autocomplete
              v-model="form.member_ids"
              :items="availableUsers"
              label="Add Members"
              item-title="username"
              item-value="id"
              multiple
              chips
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
            {{ dialog.isEdit ? 'Save Changes' : 'Create Family' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Confirmation Dialog -->
    <v-dialog
      v-model="deleteDialog.show"
      max-width="400"
    >
      <v-card>
        <v-card-title class="text-error">
          Delete Family
        </v-card-title>
        <v-card-text>
          Are you sure you want to delete "{{ deleteDialog.family?.name }}"? This action cannot be undone.
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
import { ref, onMounted } from 'vue'
import { familiesService, type Family } from '@/services/families'
import type { User } from '@/types'

const families = ref<Family[]>([])
const loading = ref(false)
const error = ref('')

const dialog = ref({
  show: false,
  isEdit: false,
  family: null as Family | null
})

const deleteDialog = ref({
  show: false,
  family: null as Family | null
})

const form = ref({
  name: '',
  member_ids: [] as number[]
})

const errors = ref({
  name: ''
})

const availableUsers = ref<User[]>([])

// Fetch families on mount
onMounted(async () => {
  try {
    loading.value = true
    families.value = await familiesService.getFamilies()
  } catch (err) {
    error.value = 'Failed to load families'
    console.error(err)
  } finally {
    loading.value = false
  }
})

function openCreateDialog() {
  dialog.value = {
    show: true,
    isEdit: false,
    family: null
  }
  form.value = {
    name: '',
    member_ids: []
  }
  errors.value.name = ''
}

function openEditDialog(family: Family) {
  dialog.value = {
    show: true,
    isEdit: true,
    family
  }
  form.value = {
    name: family.name,
    member_ids: family.members.map(m => m.id)
  }
  errors.value.name = ''
}

function confirmDelete(family: Family) {
  deleteDialog.value = {
    show: true,
    family
  }
}

async function handleSubmit() {
  try {
    loading.value = true
    errors.value.name = ''

    if (dialog.value.isEdit && dialog.value.family) {
      await familiesService.updateFamily(dialog.value.family.id, form.value)
    } else {
      await familiesService.createFamily(form.value)
    }

    // Refresh families list
    families.value = await familiesService.getFamilies()
    dialog.value.show = false
  } catch (err: any) {
    if (err.response?.data) {
      errors.value.name = err.response.data.name?.[0] || 'An error occurred'
    } else {
      errors.value.name = 'An error occurred'
    }
  } finally {
    loading.value = false
  }
}

async function handleDelete() {
  if (!deleteDialog.value.family) return

  try {
    loading.value = true
    await familiesService.deleteFamily(deleteDialog.value.family.id)
    families.value = families.value.filter(f => f.id !== deleteDialog.value.family?.id)
    deleteDialog.value.show = false
  } catch (err) {
    error.value = 'Failed to delete family'
    console.error(err)
  } finally {
    loading.value = false
  }
}
</script>
