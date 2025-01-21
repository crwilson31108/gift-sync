<template>
  <div class="loading-animation" :class="{ 'fade-out': isFadingOut }">
    <div class="animation-container">
      <LottieAnimation
        :animationData="loadingAnimation"
        :height="400"
        :width="400"
        :loop="true"
        :autoPlay="true"
        :speed="0.8"
        class="lottie-animation"
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
  width: min(90vw, 400px);
  height: min(90vw, 400px);
}

.lottie-animation {
  width: 100% !important;
  height: 100% !important;
}

.loading-animation:hover .animation-container {
  transform: scale(1.02);
}

.loading-text {
  text-align: center;
  max-width: 80%;
}

.title {
  font-size: clamp(1.5rem, 5vw, 2.5rem);
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: rgb(var(--v-theme-primary));
  line-height: 1.2;
}

.message {
  font-size: clamp(1rem, 3vw, 1.25rem);
  color: rgb(var(--v-theme-on-background));
  opacity: 0.87;
  font-weight: 500;
  line-height: 1.4;
}

/* Dark theme adjustments */
:deep(.v-theme--dark) .message {
  color: rgba(255, 255, 255, 0.87);
}

:deep(.v-theme--dark) .title {
  color: rgb(var(--v-theme-primary));
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .animation-container {
    margin-bottom: 1.5rem;
  }
}

@media (min-width: 1200px) {
  .animation-container {
    transform: scale(1.1);
  }
  
  .loading-animation:hover .animation-container {
    transform: scale(1.15);
  }
}
</style> 