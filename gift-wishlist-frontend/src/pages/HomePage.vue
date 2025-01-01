<!-- src/pages/HomePage.vue -->
<template>
  <div class="min-h-[80vh] flex flex-col items-center justify-center py-12 px-4">
    <!-- Hero Section -->
    <div class="text-center max-w-3xl mx-auto">
      <h1 class="text-4xl md:text-5xl font-bold text-primary mb-6">
        Gift Sync
      </h1>
      <p class="text-xl text-light-text dark:text-dark-text mb-12 max-w-2xl mx-auto">
        Organize your family's gift-giving with ease. Create wishlists, share with family, 
        and make holiday coordination seamless.
      </p>
      
      <!-- Action Buttons -->
      <div class="flex flex-col sm:flex-row gap-4 justify-center">
        <router-link 
          to="/families" 
          class="inline-flex items-center px-6 py-3 rounded-lg bg-primary text-white hover:bg-primary/90 transition-colors duration-200"
        >
          <v-icon icon="mdi-account-group" size="small" class="mr-2" />
          View Families
        </router-link>
        <router-link 
          to="/wishlists" 
          class="inline-flex items-center px-6 py-3 rounded-lg bg-secondary text-white hover:bg-secondary/90 transition-colors duration-200"
        >
          <v-icon icon="mdi-gift" size="small" class="mr-2" />
          View Wishlists
        </router-link>
      </div>
    </div>

    <!-- Features Section -->
    <div class="mt-24 grid md:grid-cols-3 gap-8 w-full max-w-5xl mx-auto">
      <div class="text-center p-6">
        <v-icon icon="mdi-gift-outline" size="large" class="text-primary mb-4" />
        <h3 class="text-xl font-semibold text-light-text dark:text-dark-text mb-2">
          Create Wishlists
        </h3>
        <p class="text-light-subtle dark:text-dark-subtle">
          Easily create and manage your gift wishlists
        </p>
      </div>

      <div class="text-center p-6">
        <v-icon 
          icon="mdi-account-group-outline" 
          size="large" 
          class="text-secondary mb-4"
        />
        <h3 class="text-xl font-semibold text-light-text dark:text-dark-text mb-2">
          Family Groups
        </h3>
        <p class="text-light-subtle dark:text-dark-subtle">
          Organize wishlists by family groups
        </p>
      </div>

      <div class="text-center p-6">
        <v-icon 
          icon="mdi-check-circle-outline" 
          size="large" 
          class="text-accent mb-4"
        />
        <h3 class="text-xl font-semibold text-light-text dark:text-dark-text mb-2">
          Track Purchases
        </h3>
        <p class="text-light-subtle dark:text-dark-subtle">
          Avoid duplicate gifts with purchase tracking
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// No additional logic needed
</script>

<style scoped>
/* optional styles */
</style>
