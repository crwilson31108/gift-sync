<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-light-text dark:text-dark-text">
        Family Members
      </h1>
      <v-text-field
        v-model="search"
        prepend-inner-icon="mdi-magnify"
        label="Search members"
        single-line
        hide-details
        class="max-w-xs"
        @update:model-value="handleSearch"
      />
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
      v-else-if="!members.length"
      class="text-center py-12"
    >
      <v-icon
        icon="mdi-account-group-outline"
        size="64"
        class="text-light-subtle dark:text-dark-subtle mb-4"
      />
      <h3 class="text-xl font-medium text-light-text dark:text-dark-text mb-2">
        No Members Found
      </h3>
      <p class="text-light-subtle dark:text-dark-subtle">
        {{ search ? 'Try a different search term' : 'Join or create a family to see members' }}
      </p>
    </div>

    <!-- Members Grid -->
    <div 
      v-else 
      class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
    >
      <v-card
        v-for="member in members"
        :key="member.id"
        class="bg-light-surface dark:bg-dark-surface"
      >
        <div class="p-4 flex items-center space-x-4">
          <v-avatar
            size="56"
            color="primary"
          >
            <v-img
              v-if="member.profile_picture"
              :src="member.profile_picture"
              :alt="member.username"
            />
            <span v-else class="text-lg">
              {{ member.username[0].toUpperCase() }}
            </span>
          </v-avatar>

          <div class="flex-1 min-w-0">
            <h3 class="text-lg font-medium text-light-text dark:text-dark-text truncate">
              {{ member.username }}
            </h3>
            <p class="text-sm text-light-subtle dark:text-dark-subtle truncate">
              {{ member.email }}
            </p>
            <div class="flex items-center mt-1 space-x-2">
              <v-chip
                v-for="family in getMemberFamilies(member)"
                :key="family.id"
                size="small"
                class="text-xs"
              >
                {{ family.name }}
              </v-chip>
            </div>
          </div>
        </div>

        <v-divider />

        <v-card-actions>
          <v-btn
            variant="text"
            prepend-icon="mdi-gift"
            :to="`/wishlists?user=${member.id}`"
          >
            View Wishlists
          </v-btn>
        </v-card-actions>
      </v-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { usersService } from '@/services/users'
import { familiesService, type Family } from '@/services/families'
import type { User } from '@/types'
import { useDebounce } from '@/composables/useDebounce'

const members = ref<User[]>([])
const families = ref<Family[]>([])
const loading = ref(false)
const error = ref('')
const search = ref('')

// Debounce search input
const debouncedSearch = useDebounce(search, 300)

// Fetch initial data
onMounted(async () => {
  try {
    loading.value = true
    const [membersData, familiesData] = await Promise.all([
      usersService.getMembers(),
      familiesService.getFamilies()
    ])
    members.value = membersData
    families.value = familiesData
  } catch (err) {
    error.value = 'Failed to load members'
    console.error(err)
  } finally {
    loading.value = false
  }
})

// Handle search
async function handleSearch() {
  if (!debouncedSearch.value) {
    // Reset to all members if search is cleared
    const membersData = await usersService.getMembers()
    members.value = membersData
    return
  }

  try {
    loading.value = true
    error.value = ''
    members.value = await usersService.searchUsers(debouncedSearch.value)
  } catch (err) {
    error.value = 'Search failed'
    console.error(err)
  } finally {
    loading.value = false
  }
}

// Helper function to get families for a member
function getMemberFamilies(member: User) {
  return families.value.filter(f => 
    f.members.some(m => m.id === member.id)
  )
}
</script> 