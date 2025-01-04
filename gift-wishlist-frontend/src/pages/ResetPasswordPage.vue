<template>
  <div class="min-h-screen flex items-center justify-center bg-light-bg dark:bg-dark-bg py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <!-- Logo/Header -->
      <div class="text-center">
        <img 
          src="@/assets/logo/logo.png" 
          alt="Gift Sync Logo"
          class="mx-auto h-12 w-auto"
          @error="handleImageError"
        />
        <h2 class="mt-6 text-3xl font-bold text-light-text dark:text-dark-text">
          Set New Password
        </h2>
        <p class="mt-2 text-sm text-light-subtle dark:text-dark-subtle">
          Please enter your new password
        </p>
      </div>

      <!-- Reset Form -->
      <v-form @submit.prevent="handleSubmit" v-if="!resetComplete" class="mt-8">
        <div class="rounded-md shadow-sm space-y-4">
          <v-text-field
            v-model="newPassword"
            label="New Password"
            :type="showPassword ? 'text' : 'password'"
            required
            :rules="[passwordRules.required, passwordRules.min]"
            :error-messages="error"
            @input="error = ''"
            :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
            @click:append-inner="showPassword = !showPassword"
            :class="{'dark-theme': store.isDarkTheme}"
            :disabled="loading"
          />

          <v-text-field
            v-model="confirmPassword"
            label="Confirm Password"
            :type="showConfirmPassword ? 'text' : 'password'"
            required
            :rules="[passwordRules.required, passwordRules.match]"
            :error-messages="error"
            @input="error = ''"
            :append-inner-icon="showConfirmPassword ? 'mdi-eye-off' : 'mdi-eye'"
            @click:append-inner="showConfirmPassword = !showConfirmPassword"
            :class="{'dark-theme': store.isDarkTheme}"
            :disabled="loading"
          />
        </div>

        <v-btn
          type="submit"
          color="primary"
          block
          :loading="loading"
          size="large"
          class="mt-6"
        >
          Reset Password
        </v-btn>
      </v-form>

      <!-- Success Message -->
      <div v-else class="text-center mt-8">
        <v-icon
          icon="mdi-check-circle"
          color="success"
          size="64"
          class="mb-4"
        />
        <h3 class="text-xl font-semibold text-light-text dark:text-dark-text mb-2">
          Password Reset Successful
        </h3>
        <p class="text-light-subtle dark:text-dark-subtle mb-6">
          Your password has been successfully reset. You can now log in with your new password.
        </p>
        <v-btn
          color="primary"
          to="/login"
          class="mt-4"
        >
          Go to Login
        </v-btn>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores/useAppStore'
import { authService } from '@/services/auth'

const store = useAppStore()
const route = useRoute()
const router = useRouter()

const newPassword = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')
const resetComplete = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)

const handleImageError = (e: Event) => {
  const img = e.target as HTMLImageElement
  img.style.display = 'none'
}

const passwordRules = {
  required: (value: string) => !!value || 'Password is required',
  min: (value: string) => value.length >= 8 || 'Password must be at least 8 characters',
  match: (value: string) => value === newPassword.value || 'Passwords do not match'
}

async function handleSubmit() {
  if (!newPassword.value || !confirmPassword.value) return
  if (newPassword.value !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    return
  }
  if (newPassword.value.length < 8) {
    error.value = 'Password must be at least 8 characters'
    return
  }

  loading.value = true
  error.value = ''

  try {
    await authService.resetPassword(
      route.params.userId as string,
      route.params.token as string,
      newPassword.value
    )
    resetComplete.value = true
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to reset password. The link may be invalid or expired.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.dark-theme {
  --v-theme-surface: var(--v-theme-dark);
  color: rgba(255, 255, 255, 0.87);
}

.dark-theme :deep(.v-field__input),
.dark-theme :deep(.v-label) {
  color: rgba(255, 255, 255, 0.87);
}

.dark-theme :deep(.v-field) {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.12);
}
</style> 