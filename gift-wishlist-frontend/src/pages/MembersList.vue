<template>
  <div class="py-8">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h2 class="text-3xl font-bold text-primary mb-2">Members</h2>
        <p class="text-light-subtle dark:text-dark-subtle">
          Manage members and invitations
        </p>
      </div>
      <v-btn
        color="primary"
        class="px-6"
        prepend-icon="mdi-email-plus"
        @click="openInviteDialog"
      >
        Invite Member
      </v-btn>
    </div>

    <!-- Tabs -->
    <v-tabs v-model="activeTab" class="mb-6">
      <v-tab value="members">
        <v-icon icon="mdi-account-group" class="mr-2" />
        Members
      </v-tab>
      <v-tab value="invitations">
        <v-icon icon="mdi-email-outline" class="mr-2" />
        Invitations
      </v-tab>
    </v-tabs>

    <!-- Members Tab -->
    <v-window v-model="activeTab">
      <v-window-item value="members">
        <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <v-card
            v-for="user in users"
            :key="user.id"
            class="bg-light-surface dark:bg-dark-surface border border-accent/10"
            elevation="0"
          >
            <div class="p-6">
              <div class="flex items-center space-x-4">
                <v-avatar color="primary" size="48">
                  <span class="text-lg">{{ user.name.charAt(0).toUpperCase() }}</span>
                </v-avatar>
                <div class="flex-1 min-w-0">
                  <h3 class="text-xl font-semibold text-light-text dark:text-dark-text truncate">
                    {{ user.name }}
                  </h3>
                  <p class="text-light-subtle dark:text-dark-subtle truncate">
                    {{ user.email }}
                  </p>
                </div>
              </div>
              
              <!-- Member's Families -->
              <div class="mt-4">
                <p class="text-sm font-medium text-light-subtle dark:text-dark-subtle mb-2">
                  Families
                </p>
                <div class="flex flex-wrap gap-2">
                  <v-chip
                    v-for="familyId in getUserFamilies(user.id)"
                    :key="familyId"
                    size="small"
                    class="bg-primary/10 text-primary"
                  >
                    {{ getFamilyName(familyId) }}
                  </v-chip>
                </div>
              </div>
            </div>
          </v-card>
        </div>
      </v-window-item>

      <!-- Invitations Tab -->
      <v-window-item value="invitations">
        <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <v-card
            v-for="invitation in pendingInvitations"
            :key="invitation.id"
            class="bg-light-surface dark:bg-dark-surface border border-accent/10"
            elevation="0"
          >
            <div class="p-6">
              <div class="flex items-center justify-between mb-4">
                <div class="flex items-center space-x-3">
                  <v-icon icon="mdi-email-outline" size="large" class="text-primary" />
                  <div>
                    <p class="text-light-text dark:text-dark-text font-medium">
                      {{ invitation.email }}
                    </p>
                    <p class="text-sm text-light-subtle dark:text-dark-subtle">
                      Invited to {{ getFamilyName(invitation.familyId) }}
                    </p>
                  </div>
                </div>
                <v-chip
                  :color="getStatusColor(invitation.status)"
                  size="small"
                >
                  {{ invitation.status }}
                </v-chip>
              </div>
              
              <div class="text-sm text-light-subtle dark:text-dark-subtle">
                Sent {{ formatDate(invitation.createdAt) }}
              </div>
              
              <div class="mt-4 flex justify-end space-x-2" v-if="invitation.status === 'pending'">
                <v-btn
                  variant="text"
                  color="error"
                  size="small"
                  @click="cancelInvitation(invitation.id)"
                >
                  Cancel
                </v-btn>
                <v-btn
                  variant="text"
                  color="primary"
                  size="small"
                  @click="resendInvitation(invitation)"
                >
                  Resend
                </v-btn>
              </div>
            </div>
          </v-card>
        </div>
      </v-window-item>
    </v-window>

    <!-- Invite Dialog -->
    <v-dialog v-model="inviteDialog" max-width="500px">
      <v-card class="p-6">
        <h3 class="text-xl font-semibold mb-4">Invite New Member</h3>
        <v-form @submit.prevent="sendInvitation">
          <v-select
            v-model="inviteForm.familyId"
            :items="families"
            item-title="name"
            item-value="id"
            label="Select Family"
            required
          />
          <v-text-field
            v-model="inviteForm.email"
            label="Email Address"
            type="email"
            required
            :rules="[
              v => !!v || 'Email is required',
              v => /.+@.+\..+/.test(v) || 'Email must be valid'
            ]"
          />
          <div class="flex justify-end gap-3 mt-6">
            <v-btn
              variant="outlined"
              @click="inviteDialog = false"
            >
              Cancel
            </v-btn>
            <v-btn
              color="primary"
              type="submit"
              :loading="sending"
            >
              Send Invitation
            </v-btn>
          </div>
        </v-form>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAppStore } from '@/stores/useAppStore'
import { storeToRefs } from 'pinia'
import { format } from 'date-fns'

const store = useAppStore()
const { families, users, invitations } = storeToRefs(store)

const activeTab = ref('members')
const inviteDialog = ref(false)
const sending = ref(false)

const inviteForm = ref({
  familyId: null as number | null,
  email: ''
})

// Computed
const pendingInvitations = computed(() => 
  invitations.value.filter(i => i.status === 'pending')
)

// Methods
const getUserFamilies = (userId: number) => {
  return families.value
    .filter(f => f.members.includes(userId))
    .map(f => f.id)
}

const getFamilyName = (familyId: number) => {
  const family = families.value.find(f => f.id === familyId)
  return family?.name || 'Unknown Family'
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'pending': return 'warning'
    case 'accepted': return 'success'
    case 'declined': return 'error'
    default: return 'default'
  }
}

const formatDate = (date: Date) => {
  return format(new Date(date), 'MMM d, yyyy')
}

const openInviteDialog = () => {
  inviteForm.value = {
    familyId: null,
    email: ''
  }
  inviteDialog.value = true
}

const sendInvitation = async () => {
  if (!inviteForm.value.familyId || !inviteForm.value.email) return
  
  sending.value = true
  try {
    await store.inviteMemberByEmail(
      inviteForm.value.familyId,
      inviteForm.value.email
    )
    inviteDialog.value = false
  } catch (error) {
    console.error(error)
    // Handle error (show notification, etc.)
  } finally {
    sending.value = false
  }
}

const cancelInvitation = async (invitationId: number) => {
  try {
    await store.declineInvitation(invitationId)
  } catch (error) {
    console.error(error)
    // Handle error
  }
}

const resendInvitation = (invitation: any) => {
  // Implement email resend logic
  console.log('Resending invitation to:', invitation.email)
}
</script> 