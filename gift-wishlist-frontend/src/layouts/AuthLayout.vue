<template>
  <v-main class="auth-layout">
    <div class="auth-container">
      <slot />
    </div>
  </v-main>
</template>

<style scoped>
.auth-layout {
  min-height: 100vh;
  background: rgb(var(--v-theme-background));
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.auth-container {
  width: 100%;
  max-width: 28rem; /* 448px */
  margin: 0 auto;
}

/* Dark theme adjustments */
:deep(.v-theme--dark) .auth-layout {
  background: rgb(var(--v-theme-surface-dark));
}
</style> 