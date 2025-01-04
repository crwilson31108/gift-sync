<template>
  <div class="max-w-3xl mx-auto">
    <h1 class="text-2xl font-bold mb-6">Profile Settings</h1>
    
    <!-- Profile Info Section -->
    <v-card class="mb-6">
      <v-card-title>Profile Information</v-card-title>
      <v-card-text>
        <v-form @submit.prevent="updateProfile">
          <v-text-field
            v-model="profile.username"
            label="Username"
            :readonly="true"
            variant="outlined"
            class="mb-4"
          />
          <v-text-field
            v-model="profile.email"
            label="Email"
            :readonly="true"
            variant="outlined"
            class="mb-4"
          />
          <v-text-field
            v-model="profile.full_name"
            label="Full Name"
            variant="outlined"
            class="mb-4"
          />
          <v-textarea
            v-model="profile.bio"
            label="Bio"
            variant="outlined"
            class="mb-4"
            rows="3"
            placeholder="Tell us a little about yourself..."
          />
          <v-btn
            color="primary"
            type="submit"
            :loading="isUpdating"
            :disabled="isUpdating"
          >
            Update Profile
          </v-btn>
        </v-form>
      </v-card-text>
    </v-card>

    <!-- Change Password Section -->
    <v-card>
      <v-card-title>Change Password</v-card-title>
      <v-card-text>
        <v-form @submit.prevent="changePassword">
          <v-text-field
            v-model="passwordForm.current_password"
            label="Current Password"
            :type="showCurrentPassword ? 'text' : 'password'"
            variant="outlined"
            class="mb-4"
            :append-inner-icon="showCurrentPassword ? 'mdi-eye-off' : 'mdi-eye'"
            @click:append-inner="showCurrentPassword = !showCurrentPassword"
          />
          <v-text-field
            v-model="passwordForm.new_password"
            label="New Password"
            :type="showNewPassword ? 'text' : 'password'"
            variant="outlined"
            class="mb-4"
            :append-inner-icon="showNewPassword ? 'mdi-eye-off' : 'mdi-eye'"
            @click:append-inner="showNewPassword = !showNewPassword"
          />
          <v-text-field
            v-model="passwordForm.confirm_password"
            label="Confirm New Password"
            :type="showConfirmPassword ? 'text' : 'password'"
            variant="outlined"
            class="mb-4"
            :error-messages="passwordMatchError"
            :append-inner-icon="showConfirmPassword ? 'mdi-eye-off' : 'mdi-eye'"
            @click:append-inner="showConfirmPassword = !showConfirmPassword"
          />
          <v-btn
            color="primary"
            type="submit"
            :loading="isChangingPassword"
            :disabled="!canSubmitPassword || isChangingPassword"
          >
            Change Password
          </v-btn>
        </v-form>
      </v-card-text>
    </v-card>

    <!-- Snackbar -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="snackbar.timeout"
    >
      {{ snackbar.message }}
      
      <template v-slot:actions>
        <v-btn
          variant="text"
          @click="snackbar.show = false"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAppStore } from '@/stores/useAppStore'
import api from '@/services/api'

const store = useAppStore()

// Separate visibility toggles for each password field
const showCurrentPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

// Snackbar state
const snackbar = ref({
  show: false,
  message: '',
  color: 'success',
  timeout: 3000
})

// Helper functions for snackbar
const showSuccess = (message: string) => {
  snackbar.value = {
    show: true,
    message,
    color: 'success',
    timeout: 3000
  }
}

const showError = (message: string) => {
  snackbar.value = {
    show: true,
    message,
    color: 'error',
    timeout: 3000
  }
}

const profile = ref({
  username: store.currentUser?.username || '',
  email: store.currentUser?.email || '',
  full_name: store.currentUser?.full_name || '',
  bio: store.currentUser?.bio || ''
})

const passwordForm = ref({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

const isUpdating = ref(false)
const isChangingPassword = ref(false)

// Computed properties for password validation
const passwordMatchError = computed(() => {
  if (passwordForm.value.confirm_password && 
      passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    return ['Passwords do not match']
  }
  return []
})

const canSubmitPassword = computed(() => {
  return passwordForm.value.current_password &&
         passwordForm.value.new_password &&
         passwordForm.value.confirm_password &&
         passwordForm.value.new_password === passwordForm.value.confirm_password
})

// Update profile information
async function updateProfile() {
  if (isUpdating.value) return
  
  isUpdating.value = true
  try {
    const response = await api.patch('/users/me/', {
      full_name: profile.value.full_name,
      bio: profile.value.bio
    })
    
    await store.updateCurrentUser(response.data)
    showSuccess('Profile updated successfully')
  } catch (error) {
    showError('Failed to update profile')
    console.error('Profile update error:', error)
  } finally {
    isUpdating.value = false
  }
}

// Change password
async function changePassword() {
  if (isChangingPassword.value || !canSubmitPassword.value) return
  
  isChangingPassword.value = true
  try {
    await api.post('/users/change_password/', {
      current_password: passwordForm.value.current_password,
      new_password: passwordForm.value.new_password
    })
    
    showSuccess('Password changed successfully')
    passwordForm.value = {
      current_password: '',
      new_password: '',
      confirm_password: ''
    }
  } catch (error: any) {
    const errorMessage = error.response?.data?.detail || 'Failed to change password'
    showError(errorMessage)
    console.error('Password change error:', error)
  } finally {
    isChangingPassword.value = false
  }
}
</script>

<style scoped>
.v-card {
  border-radius: 8px;
}

.v-card-title {
  font-size: 1.25rem;
  font-weight: 600;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid rgba(var(--v-border-color), 0.12);
}

.v-card-text {
  padding: 1.5rem;
}

.v-btn {
  text-transform: none;
}
</style>