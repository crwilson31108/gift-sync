<template>
  <div class="min-h-screen flex items-center justify-center bg-light-bg dark:bg-dark-bg py-12 px-4 sm:px-6 lg:px-8">
    <!-- Show loading animation when logging in -->
    <LoadingAnimation 
      v-if="isLoggingIn"
      title="Welcome Back!"
      message="Getting everything ready..."
      :isFadingOut="isFadingOut"
    />

    <!-- Login form -->
    <div v-else class="max-w-md w-full space-y-8">
      <!-- Logo/Header -->
      <div class="text-center">
        <img 
          src="@/assets/logo/logo.png" 
          alt="Gift Sync Logo"
          class="mx-auto h-12 w-auto"
          @error="handleImageError"
        />
        <h2 class="mt-6 text-3xl font-bold text-light-text dark:text-dark-text">
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
            :class="{'dark-theme': store.isDarkTheme}"
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
            :class="{'dark-theme': store.isDarkTheme}"
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

      <!-- Added a subtle text at the bottom -->
      <div class="mt-4 text-center text-xs text-light-subtle dark:text-dark-subtle">
        Having trouble? Contact your family administrator
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/useAppStore'
import { authService } from '@/services/auth'
import LoadingAnimation from '@/components/LoadingAnimation.vue'

const router = useRouter()
const store = useAppStore()
const isLoggingIn = ref(false)
const isFadingOut = ref(false)

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

interface User {
  id: number
  username: string
  email: string
  full_name?: string
  profile_picture?: string
  bio?: string
}

const handleSubmit = async () => {
  loading.value = true
  isLoggingIn.value = true
  errors.email = ''
  errors.password = ''

  try {
    const response = await authService.login(form)
    const user: User = {
      ...response.user,
      full_name: response.user.username
    }
    store.setCurrentUser(user)
    
    // Add a longer delay and fade out
    await new Promise(resolve => setTimeout(resolve, 2000))
    isFadingOut.value = true
    
    // Wait for fade out before redirecting
    await new Promise(resolve => setTimeout(resolve, 500))
    
    const redirectPath = localStorage.getItem('redirectPath') || '/'
    localStorage.removeItem('redirectPath')
    router.push(redirectPath)
  } catch (error: any) {
    isLoggingIn.value = false
    isFadingOut.value = false
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

onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme) {
    store.setDarkTheme(savedTheme === 'dark')
  }
})
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