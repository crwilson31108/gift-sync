<template>
  <div>
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold text-light-text dark:text-dark-text">
          {{ family?.name || 'Family Details' }}
        </h1>
        <p class="text-sm text-light-subtle dark:text-dark-subtle mt-1">
          Created {{ family?.created_at ? formatDate(family.created_at) : '' }}
        </p>
      </div>
      <div class="flex gap-2">
        <v-btn
          color="primary"
          prepend-icon="mdi-account-plus"
          @click="openAddMemberDialog"
        >
          Add Member
        </v-btn>
        <v-btn
          color="primary"
          variant="outlined"
          prepend-icon="mdi-pencil"
          @click="openEditDialog"
        >
          Edit Family
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

    <!-- Family Details -->
    <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- Members Card -->
      <v-card class="bg-light-surface dark:bg-dark-surface">
        <v-card-title class="flex justify-between items-center">
          <span>Members</span>
          <span class="text-sm text-light-subtle dark:text-dark-subtle">
            {{ family?.members.length || 0 }} total
          </span>
        </v-card-title>
        <v-card-text>
          <div class="space-y-4">
            <div
              v-for="member in family?.members"
              :key="member.id"
              class="flex items-center justify-between"
            >
              <div class="flex items-center space-x-3">
                <v-avatar
                  size="40"
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
                <div>
                  <p class="font-medium text-light-text dark:text-dark-text">
                    {{ member.username }}
                  </p>
                  <p class="text-sm text-light-subtle dark:text-dark-subtle">
                    {{ member.email }}
                  </p>
                </div>
              </div>
              <v-btn
                v-if="member.id !== currentUser?.id"
                icon="mdi-close"
                variant="text"
                size="small"
                color="error"
                @click="confirmRemoveMember(member)"
              />
            </div>
          </div>
        </v-card-text>
      </v-card>

      <!-- Add Member Dialog -->
      <v-dialog
        v-model="addMemberDialog.show"
        max-width="500"
      >
        <v-card>
          <v-card-title>Add Member</v-card-title>
          <v-card-text>
            <v-autocomplete
              v-model="addMemberDialog.selectedUser"
              :items="availableUsers"
              label="Search users"
              item-title="username"
              item-value="id"
              :loading="searchLoading"
              @update:search="searchUsers"
            />
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn
              variant="text"
              @click="addMemberDialog.show = false"
            >
              Cancel
            </v-btn>
            <v-btn
              color="primary"
              :loading="loading"
              :disabled="!addMemberDialog.selectedUser"
              @click="handleAddMember"
            >
              Add Member
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Remove Member Confirmation -->
      <v-dialog
        v-model="removeMemberDialog.show"
        max-width="400"
      >
        <v-card>
          <v-card-title class="text-error">
            Remove Member
          </v-card-title>
          <v-card-text>
            Are you sure you want to remove {{ removeMemberDialog.member?.username }} from this family?
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn
              variant="text"
              @click="removeMemberDialog.show = false"
            >
              Cancel
            </v-btn>
            <v-btn
              color="error"
              :loading="loading"
              @click="handleRemoveMember"
            >
              Remove
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { familiesService, type Family } from '@/services/families'
import { usersService } from '@/services/users'
import { useAppStore } from '@/stores/useAppStore'
import type { User } from '@/types'
import { format } from 'date-fns'

const route = useRoute()
const store = useAppStore()
const currentUser = computed(() => store.currentUser)

const family = ref<Family | null>(null)
const loading = ref(false)
const error = ref('')
const searchLoading = ref(false)
const availableUsers = ref<User[]>([])

const addMemberDialog = ref({
  show: false,
  selectedUser: null as number | null
})

const removeMemberDialog = ref({
  show: false,
  member: null as User | null
})

onMounted(async () => {
  await loadFamily()
})

async function loadFamily() {
  try {
    loading.value = true
    const familyId = Number(route.params.id)
    family.value = await familiesService.getFamily(familyId)
  } catch (err) {
    error.value = 'Failed to load family details'
    console.error(err)
  } finally {
    loading.value = false
  }
}

function openAddMemberDialog() {
  addMemberDialog.value = {
    show: true,
    selectedUser: null
  }
}

function confirmRemoveMember(member: User) {
  removeMemberDialog.value = {
    show: true,
    member
  }
}

async function searchUsers(query: string) {
  if (query.length < 3) return

  try {
    searchLoading.value = true
    const users = await usersService.searchUsers(query)
    // Filter out existing members
    availableUsers.value = users.filter(user => 
      !family.value?.members.some(member => member.id === user.id)
    )
  } catch (err) {
    console.error('Failed to search users:', err)
  } finally {
    searchLoading.value = false
  }
}

async function handleAddMember() {
  if (!family.value || !addMemberDialog.value.selectedUser) return

  try {
    loading.value = true
    await familiesService.addMember(
      family.value.id,
      addMemberDialog.value.selectedUser
    )
    await loadFamily()
    addMemberDialog.value.show = false
  } catch (err) {
    console.error('Failed to add member:', err)
  } finally {
    loading.value = false
  }
}

async function handleRemoveMember() {
  if (!family.value || !removeMemberDialog.value.member) return

  try {
    loading.value = true
    await familiesService.removeMember(
      family.value.id,
      removeMemberDialog.value.member.id
    )
    await loadFamily()
    removeMemberDialog.value.show = false
  } catch (err) {
    console.error('Failed to remove member:', err)
  } finally {
    loading.value = false
  }
}

function formatDate(date: string) {
  return format(new Date(date), 'MMM d, yyyy')
}
</script> 