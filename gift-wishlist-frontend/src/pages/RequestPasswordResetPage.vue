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
          Reset Password
        </h2>
        <p class="mt-2 text-sm text-light-subtle dark:text-dark-subtle">
          Enter your email to receive password reset instructions
        </p>
      </div>

      <!-- Reset Form -->
      <v-form @submit.prevent="handleSubmit" v-if="!emailSent" class="mt-8">
        <div class="rounded-md shadow-sm space-y-4">
          <v-text-field
            v-model="email"
            label="Email address"
            type="email"
            required
            :error-messages="error"
            @input="error = ''"
            :class="{'dark-theme': store.isDarkTheme}"
            :disabled="loading"
          />
        </div>

        <div class="mt-6 space-y-4">
          <v-btn
            type="submit"
            color="primary"
            block
            :loading="loading"
            size="large"
          >
            Send Reset Link
          </v-btn>

          <div class="text-center">
            <router-link 
              to="/login" 
              class="text-sm text-primary hover:text-primary-dark transition-colors"
            >
              Back to Login
            </router-link>
          </div>
        </div>
      </v-form>

      <!-- Success Message -->
      <div v-else class="text-center mt-8">
        <v-icon
          icon="mdi-email-check"
          color="success"
          size="64"
          class="mb-4"
        />
        <h3 class="text-xl font-semibold text-light-text dark:text-dark-text mb-2">
          Check Your Email
        </h3>
        <p class="text-light-subtle dark:text-dark-subtle mb-6">
          If an account exists with {{ email }}, you will receive password reset instructions.
        </p>
        <v-btn
          color="primary"
          variant="text"
          to="/login"
          class="mt-4"
        >
          Return to Login
        </v-btn>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAppStore } from '@/stores/useAppStore'
import { authService } from '@/services/auth'

const store = useAppStore()
const email = ref('')
const loading = ref(false)
const emailSent = ref(false)
const error = ref('')

const handleImageError = (e: Event) => {
  const img = e.target as HTMLImageElement
  img.style.display = 'none'
}

async function handleSubmit() {
  if (!email.value) return

  loading.value = true
  error.value = ''

  try {
    await authService.requestPasswordReset(email.value)
    emailSent.value = true
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to send reset link. Please try again.'
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