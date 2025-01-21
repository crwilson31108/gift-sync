<template>
  <div class="loading-animation" :class="{ 'fade-out': isFadingOut }">
    <div class="animation-container">
      <LottieAnimation
        :animationData="loadingAnimation"
        :height="300"
        :width="300"
        :loop="true"
        :autoPlay="true"
      />
    </div>
    <div class="loading-text">
      <h2 class="title">{{ title }}</h2>
      <p class="message">{{ message }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { LottieAnimation } from 'lottie-web-vue'
import loadingAnimation from '@/assets/animations/loading.json'

defineProps<{
  message?: string
  title?: string
  isFadingOut?: boolean
}>()
</script>

<style scoped>
.loading-animation {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgb(var(--v-theme-background));
  z-index: 9999;
  opacity: 1;
  transition: opacity 0.5s ease-in-out;
}

.loading-animation.fade-out {
  opacity: 0;
}

.animation-container {
  margin-bottom: 2rem;
  transform: scale(1);
  transition: transform 0.3s ease;
}

.loading-animation:hover .animation-container {
  transform: scale(1.05);
}

.loading-text {
  text-align: center;
}

.title {
  font-size: 2rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: rgb(var(--v-theme-primary));
}

.message {
  font-size: 1.25rem;
  color: rgb(var(--v-theme-on-background));
  opacity: 0.87;
  font-weight: 500;
}

/* Dark theme adjustments */
:deep(.v-theme--dark) .message {
  color: rgba(255, 255, 255, 0.87);
}

:deep(.v-theme--dark) .title {
  color: rgb(var(--v-theme-primary));
}
</style> 