<!-- src/pages/FamilyList.vue -->
<template>
  <div class="py-8">
    <!-- Header with Add Button -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h2 class="text-3xl font-bold text-primary mb-2">Families</h2>
        <p class="text-light-subtle dark:text-dark-subtle">
          Manage your family groups and members
        </p>
      </div>
      <v-btn
        color="primary"
        class="px-6"
        prepend-icon="mdi-plus"
        @click="openAddDialog"
      >
        Add Family
      </v-btn>
    </div>

    <!-- Family Grid -->
    <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
      <!-- Family Cards -->
      <v-card
        v-for="family in families"
        :key="family.id"
        class="bg-light-surface dark:bg-dark-surface border border-accent/10 hover:border-accent/30 transition-all duration-200"
        elevation="0"
      >
        <div class="p-6">
          <!-- Family Header -->
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center">
              <v-icon
                icon="mdi-account-group"
                size="large"
                class="text-secondary mr-3"
              />
              <h3 class="text-xl font-semibold text-light-text dark:text-dark-text">
                {{ family.name }}
              </h3>
            </div>
            <!-- Card Menu -->
            <v-menu location="bottom end">
              <template v-slot:activator="{ props }">
                <v-btn
                  icon="mdi-dots-vertical"
                  variant="text"
                  v-bind="props"
                  size="small"
                  class="text-light-subtle dark:text-dark-subtle"
                />
              </template>
              <v-list>
                <v-list-item
                  prepend-icon="mdi-pencil"
                  title="Edit"
                  @click="openEditDialog(family)"
                />
                <v-list-item
                  prepend-icon="mdi-account-plus"
                  title="Add Member"
                  @click="openAddMemberDialog(family)"
                />
                <v-divider class="my-2" />
                <v-list-item
                  prepend-icon="mdi-delete"
                  title="Delete"
                  color="error"
                  @click="confirmDelete(family)"
                />
              </v-list>
            </v-menu>
          </div>

          <!-- Members List -->
          <div class="space-y-2">
            <p class="text-sm font-medium text-light-subtle dark:text-dark-subtle mb-3">
              Members ({{ family.members.length }})
            </p>
            <ul class="space-y-2 max-h-48 overflow-y-auto">
              <li
                v-for="memberId in family.members"
                :key="memberId"
                class="flex items-center justify-between group"
              >
                <div class="flex items-center">
                  <v-avatar size="32" color="primary" class="mr-2">
                    <span class="text-sm">{{ getMemberInitials(memberId) }}</span>
                  </v-avatar>
                  <span class="text-light-text dark:text-dark-text">
                    {{ getMemberName(memberId) }}
                  </span>
                </div>
                <v-btn
                  icon="mdi-close"
                  variant="text"
                  size="x-small"
                  color="error"
                  class="opacity-0 group-hover:opacity-100 transition-opacity"
                  @click="confirmRemoveMember(family, memberId)"
                />
              </li>
            </ul>
          </div>
        </div>
      </v-card>

      <!-- Add Family Card -->
      <v-card
        class="bg-light-surface dark:bg-dark-surface border-2 border-dashed border-accent/30 hover:border-accent/50 transition-all duration-200 cursor-pointer flex items-center justify-center"
        elevation="0"
        height="100%"
        @click="openAddDialog"
      >
        <div class="text-center p-6">
          <v-icon
            icon="mdi-plus-circle"
            size="large"
            class="text-accent mb-2"
          />
          <p class="text-light-subtle dark:text-dark-subtle font-medium">
            Add New Family
          </p>
        </div>
      </v-card>
    </div>

    <!-- Add/Edit Family Dialog -->
    <v-dialog v-model="dialogVisible" max-width="500px">
      <v-card class="p-6">
        <h3 class="text-xl font-semibold mb-4">
          {{ editingFamily ? 'Edit Family' : 'Add New Family' }}
        </h3>
        <v-form @submit.prevent="saveFamily">
          <v-text-field
            v-model="familyForm.name"
            label="Family Name"
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
              {{ editingFamily ? 'Save Changes' : 'Create Family' }}
            </v-btn>
          </div>
        </v-form>
      </v-card>
    </v-dialog>

    <!-- Add Member Dialog -->
    <v-dialog v-model="memberDialogVisible" max-width="500px">
      <v-card class="p-6">
        <h3 class="text-xl font-semibold mb-4">Add Family Member</h3>
        <v-form @submit.prevent="addMember">
          <v-select
            v-model="selectedMember"
            :items="availableMembers"
            item-title="name"
            item-value="id"
            label="Select Member"
            required
          />
          <div class="flex justify-end gap-3 mt-6">
            <v-btn
              variant="outlined"
              @click="memberDialogVisible = false"
            >
              Cancel
            </v-btn>
            <v-btn
              color="primary"
              type="submit"
              :loading="saving"
            >
              Add Member
            </v-btn>
          </div>
        </v-form>
      </v-card>
    </v-dialog>

    <!-- Confirm Delete Dialog -->
    <v-dialog v-model="deleteDialogVisible" max-width="400px">
      <v-card class="p-6">
        <h3 class="text-xl font-semibold mb-4">Confirm Delete</h3>
        <p class="mb-6">Are you sure you want to delete this family? This action cannot be undone.</p>
        <div class="flex justify-end gap-3">
          <v-btn
            variant="outlined"
            @click="deleteDialogVisible = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="error"
            @click="deleteFamily"
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
import type { Family } from '@/stores/useAppStore'

const store = useAppStore()
const { families, users } = storeToRefs(store)

// Dialog states
const dialogVisible = ref(false)
const memberDialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const saving = ref(false)
const deleting = ref(false)

// Form states
const editingFamily = ref<Family | null>(null)
const selectedFamily = ref<Family | null>(null)
const selectedMember = ref<number | null>(null)
const familyForm = ref({
  name: '',
})

// Computed
const availableMembers = computed(() => {
  if (!selectedFamily.value) return users.value
  return users.value.filter(user => 
    !selectedFamily.value?.members.includes(user.id)
  )
})

// Methods
const openAddDialog = () => {
  editingFamily.value = null
  familyForm.value.name = ''
  dialogVisible.value = true
}

const openEditDialog = (family: Family) => {
  editingFamily.value = family
  familyForm.value.name = family.name
  dialogVisible.value = true
}

const openAddMemberDialog = (family: Family) => {
  selectedFamily.value = family
  selectedMember.value = null
  memberDialogVisible.value = true
}

const saveFamily = async () => {
  saving.value = true
  try {
    if (editingFamily.value) {
      await store.updateFamily({
        ...editingFamily.value,
        name: familyForm.value.name,
      })
    } else {
      await store.createFamily({
        name: familyForm.value.name,
        members: [],
      })
    }
    dialogVisible.value = false
  } finally {
    saving.value = false
  }
}

const addMember = async () => {
  if (!selectedFamily.value || !selectedMember.value) return
  
  saving.value = true
  try {
    await store.addFamilyMember(selectedFamily.value.id, selectedMember.value)
    memberDialogVisible.value = false
  } finally {
    saving.value = false
  }
}

const confirmDelete = (family: Family) => {
  selectedFamily.value = family
  deleteDialogVisible.value = true
}

const deleteFamily = async () => {
  if (!selectedFamily.value) return
  
  deleting.value = true
  try {
    await store.deleteFamily(selectedFamily.value.id)
    deleteDialogVisible.value = false
  } finally {
    deleting.value = false
  }
}

const confirmRemoveMember = async (family: Family, memberId: number) => {
  if (confirm('Remove this member from the family?')) {
    await store.removeFamilyMember(family.id, memberId)
  }
}

const getMemberName = (id: number) => {
  const user = users.value.find(u => u.id === id)
  return user ? user.name : 'Unknown'
}

const getMemberInitials = (id: number) => {
  const name = getMemberName(id)
  return name
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
}
</script>
