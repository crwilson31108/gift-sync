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
        <h2 class="mt-6 text-3xl font-bold text-primary">
          Welcome back
        </h2>
        <p class="mt-2 text-sm text-light-subtle dark:text-dark-subtle">
          Sign in to manage your wishlists
        </p>
      </div>

      <!-- Login Form -->
      <v-form @submit.prevent="handleSubmit" class="mt-8 space-y-6">
        <div class="rounded-md shadow-sm space-y-4">
          <v-text-field
            v-model="form.email"
            label="Email address"
            type="email"
            required
            :error-messages="errors.email"
            @input="errors.email = ''"
          />

          <v-text-field
            v-model="form.password"
            label="Password"
            :type="showPassword ? 'text' : 'password'"
            required
            :error-messages="errors.password"
            @input="errors.password = ''"
            :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
            @click:append-inner="showPassword = !showPassword"
          />
        </div>

        <v-btn
          type="submit"
          color="primary"
          block
          :loading="loading"
          size="large"
        >
          Sign in
        </v-btn>
      </v-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/useAppStore'
import { authService } from '@/services/auth'

const router = useRouter()
const store = useAppStore()

const form = reactive({
  email: '',
  password: ''
})

const errors = reactive({
  email: '',
  password: ''
})

const loading = ref(false)
const showPassword = ref(false)

const handleImageError = (e: Event) => {
  const img = e.target as HTMLImageElement
  img.style.display = 'none'
}

const handleSubmit = async () => {
  loading.value = true
  errors.email = ''
  errors.password = ''

  try {
    const response = await authService.login(form)
    store.setUser(response.user)
    const redirectPath = localStorage.getItem('redirectPath') || '/'
    localStorage.removeItem('redirectPath')
    router.push(redirectPath)
  } catch (error: any) {
    if (error.response?.data) {
      const { detail, email, password } = error.response.data
      if (detail) errors.email = detail
      if (email) errors.email = email[0]
      if (password) errors.password = password[0]
    } else {
      errors.email = 'An error occurred. Please try again.'
    }
  } finally {
    loading.value = false
  }
}
</script> 