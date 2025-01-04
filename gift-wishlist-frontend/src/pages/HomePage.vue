<!-- src/pages/HomePage.vue -->
<template>
  <div>
    <!-- Hero Section -->
    <div class="hero-section text-center py-16 mb-8">
      <div class="hero-content">
        <!-- Logo/Icon -->
        <div class="hero-icon mb-6">
          <v-icon
            icon="mdi-gift-outline"
            size="64"
            color="white"
            class="hero-icon-inner"
          />
        </div>

        <!-- Title with highlight effect -->
        <h1 class="hero-title mb-4">
          Welcome to <span class="gradient-text">GiftSync</span>
        </h1>

        <!-- Subtitle with better typography -->
        <p class="hero-subtitle mb-8">
          Create and share wishlists with your family and friends.<br>
          <span class="hero-tagline">Never miss a perfect gift again.</span>
        </p>

        <!-- CTA Button -->
        <v-btn
          v-if="!currentUser"
          color="white"
          size="x-large"
          :to="{ name: 'Login' }"
          class="get-started-btn"
        >
          Get Started
          <v-icon end icon="mdi-arrow-right" class="ml-2" />
        </v-btn>
      </div>

      <!-- Decorative elements -->
      <div class="hero-shapes">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape shape-3"></div>
      </div>
    </div>

    <!-- Stats Section -->
    <div v-if="currentUser" class="stats-grid mb-12">
      <v-card 
        v-for="(value, key) in statsDisplay" 
        :key="key" 
        class="stat-card"
      >
        <v-card-text class="text-center">
          <div v-if="!statsLoading" class="text-h3 font-bold mb-2">
            {{ value.value }}
          </div>
          <v-skeleton-loader
            v-else
            type="heading"
            class="mb-2"
          />
          <div class="text-subtitle-1">{{ value.label }}</div>
        </v-card-text>
      </v-card>
    </div>

    <!-- Quick Actions -->
    <div v-if="currentUser" class="quick-actions mb-12">
      <h2 class="text-2xl font-bold mb-6">Quick Actions</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <v-card
          v-for="action in quickActions"
          :key="action.title"
          :to="action.to"
          class="action-card"
        >
          <v-card-text class="d-flex align-center">
            <v-icon
              :icon="action.icon"
              size="32"
              class="mr-4"
              :color="action.color"
            />
            <div>
              <div class="text-h6">{{ action.title }}</div>
              <div class="text-subtitle-2 text-light-subtle dark:text-dark-subtle">
                {{ action.description }}
              </div>
            </div>
          </v-card-text>
        </v-card>
      </div>
    </div>

    <!-- Recent Activity -->
    <div v-if="currentUser && recentActivity.length" class="recent-activity mb-12">
      <h2 class="text-2xl font-bold mb-6">Recent Activity</h2>
      <v-timeline density="compact">
        <v-timeline-item
          v-for="activity in recentActivity"
          :key="activity.id"
          :dot-color="activity.color"
          size="small"
        >
          <div class="text-subtitle-1">{{ activity.title }}</div>
          <div class="text-caption text-light-subtle dark:text-dark-subtle">
            {{ formatDate(activity.date) }}
          </div>
        </v-timeline-item>
      </v-timeline>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAppStore } from '@/stores/useAppStore'
import { format } from 'date-fns'
import { wishlistsService } from '@/services/wishlists'

const store = useAppStore()
const currentUser = computed(() => store.currentUser)

interface Stats {
  totalWishlists: number
  totalItems: number
  purchasedItems: number
  totalFamilies: number
}

const statsLoading = ref(true)

const stats = ref<Stats>({
  totalWishlists: 0,
  totalItems: 0,
  purchasedItems: 0,
  totalFamilies: 0
})

const statsDisplay = computed(() => ({
  wishlists: {
    value: stats.value.totalWishlists,
    label: 'Your Wishlists'
  },
  items: {
    value: stats.value.totalItems,
    label: 'Items Added'
  },
  purchased: {
    value: stats.value.purchasedItems,
    label: 'Items Purchased'
  },
  families: {
    value: stats.value.totalFamilies,
    label: 'Families Joined'
  }
}))

const quickActions = [
  {
    title: 'Create Wishlist',
    description: 'Start a new wishlist for yourself',
    icon: 'mdi-playlist-plus',
    color: 'primary',
    to: '/wishlists?action=create'
  },
  {
    title: 'Join Family',
    description: 'Connect with your family members',
    icon: 'mdi-account-group',
    color: 'success',
    to: '/families'
  },
  {
    title: 'Browse Wishlists',
    description: 'See what others are wishing for',
    icon: 'mdi-gift',
    color: 'info',
    to: '/wishlists'
  }
]

interface Activity {
  id: string
  title: string
  date: string
  color: string
  userId: number
  wishlistOwnerId: number
}

const recentActivity = ref<Activity[]>([])

onMounted(async () => {
  if (currentUser.value) {
    await loadStats()
    await loadRecentActivity()
  }
})

async function loadStats() {
  try {
    statsLoading.value = true
    const response = await wishlistsService.getStats()
    stats.value = response
  } catch (error) {
    console.error('Failed to load stats:', error)
  } finally {
    statsLoading.value = false
  }
}

async function loadRecentActivity() {
  try {
    const response = await wishlistsService.getRecentActivity()
    // No need to filter in frontend since backend handles it
    recentActivity.value = response
  } catch (error) {
    console.error('Failed to load recent activity:', error)
  }
}

function formatDate(date: string) {
  return format(new Date(date), 'MMM d, yyyy')
}
</script>

<style scoped>
.hero-section {
  background: linear-gradient(
    135deg,
    rgb(var(--v-theme-primary)) 0%,
    rgb(var(--v-theme-info)) 100%
  );
  color: white;
  border-radius: 1.5rem;
  margin: -1rem -1rem 2rem -1rem;
  position: relative;
  overflow: hidden;
  box-shadow: 0 10px 30px -10px rgba(var(--v-theme-primary), 0.3);
}

.hero-content {
  position: relative;
  z-index: 2;
  max-width: 800px;
  margin: 0 auto;
}

.hero-icon {
  background: rgba(255, 255, 255, 0.1);
  width: 100px;
  height: 100px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  backdrop-filter: blur(8px);
  border: 2px solid rgba(255, 255, 255, 0.1);
}

.hero-icon-inner {
  animation: float 3s ease-in-out infinite;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 700;
  letter-spacing: -0.5px;
  line-height: 1.2;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.gradient-text {
  background: linear-gradient(
    45deg,
    rgb(255, 255, 255) 30%,
    rgba(255, 255, 255, 0.8) 100%
  );
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 800;
}

.hero-subtitle {
  font-size: 1.5rem;
  font-weight: 400;
  opacity: 0.9;
  line-height: 1.6;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.hero-tagline {
  font-weight: 500;
  opacity: 0.95;
}

.get-started-btn {
  font-weight: 600;
  letter-spacing: 0.5px;
  padding: 0 2rem;
  height: 56px;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.9) !important;
  color: rgb(var(--v-theme-primary)) !important;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
}

.get-started-btn:hover {
  transform: translateY(-2px);
  background: white !important;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15) !important;
}

/* Decorative shapes */
.hero-shapes {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
  pointer-events: none;
}

.shape {
  position: absolute;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(5px);
  border-radius: 50%;
}

.shape-1 {
  width: 300px;
  height: 300px;
  top: -100px;
  right: -100px;
  animation: float 6s ease-in-out infinite;
}

.shape-2 {
  width: 200px;
  height: 200px;
  bottom: -50px;
  left: -50px;
  animation: float 8s ease-in-out infinite;
}

.shape-3 {
  width: 150px;
  height: 150px;
  bottom: 50px;
  right: 15%;
  animation: float 7s ease-in-out infinite;
}

@keyframes float {
  0% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-20px);
  }
  100% {
    transform: translateY(0px);
  }
}

/* Dark theme enhancements */
:deep(.v-theme--dark) {
  .hero-section {
    background: linear-gradient(
      135deg,
      rgba(var(--v-theme-primary), 0.9) 0%,
      rgba(var(--v-theme-info), 0.9) 100%
    );
    /* Darker shadow for better depth */
    box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
  }

  .hero-icon {
    /* Slightly lighter background for better contrast */
    background: rgba(255, 255, 255, 0.15);
    border-color: rgba(255, 255, 255, 0.2);
  }

  .gradient-text {
    /* Brighter gradient for dark mode */
    background: linear-gradient(
      45deg,
      rgb(255, 255, 255) 0%,
      rgba(255, 255, 255, 0.85) 100%
    );
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .hero-subtitle {
    /* Increased opacity for better readability */
    opacity: 0.95;
  }

  .get-started-btn {
    /* Darker text color for better contrast */
    color: rgba(var(--v-theme-primary), 0.95) !important;
    background: rgba(255, 255, 255, 0.95) !important;
    /* Darker shadow */
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2) !important;
  }

  .get-started-btn:hover {
    background: white !important;
    box-shadow: 0 6px 25px rgba(0, 0, 0, 0.25) !important;
  }

  .shape {
    /* Brighter shapes in dark mode */
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(8px);
  }

  /* Stats cards dark mode */
  .stat-card {
    background: rgba(var(--v-theme-surface-dark), 0.8) !important;
    border-color: rgba(var(--v-theme-primary), 0.1);
    /* Subtle glow effect */
    box-shadow: 0 4px 20px rgba(var(--v-theme-primary), 0.1) !important;
  }

  .stat-card:hover {
    border-color: rgba(var(--v-theme-primary), 0.2);
    box-shadow: 0 8px 30px rgba(var(--v-theme-primary), 0.15) !important;
  }

  /* Quick action cards dark mode */
  .action-card {
    background: rgba(var(--v-theme-surface-dark), 0.8) !important;
    border-color: rgba(var(--v-theme-primary), 0.1);
  }

  .action-card:hover {
    border-color: rgba(var(--v-theme-primary), 0.2);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2) !important;
  }

  /* Timeline dark mode adjustments */
  .recent-activity {
    .v-timeline-item__body {
      background: rgba(var(--v-theme-surface-dark), 0.8);
      border: 1px solid rgba(var(--v-theme-primary), 0.1);
      border-radius: 8px;
      padding: 12px;
    }
  }
}

/* Enhance stat cards for both themes */
.stat-card {
  background: rgb(var(--v-theme-surface)) !important;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  border: 1px solid rgba(var(--v-theme-on-surface), 0.12);
}

.action-card {
  background: rgb(var(--v-theme-surface)) !important;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  border: 1px solid rgba(var(--v-theme-on-surface), 0.12);
}

/* Timeline enhancements */
.recent-activity {
  .v-timeline-item {
    margin-bottom: 1rem;
  }

  .text-subtitle-1 {
    font-weight: 500;
  }

  .text-caption {
    opacity: 0.8;
  }
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }

  .hero-subtitle {
    font-size: 1.25rem;
  }

  .hero-section {
    padding-top: 3rem;
    padding-bottom: 3rem;
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.stat-card, .action-card {
  transition: transform 0.2s;
}

.stat-card:hover, .action-card:hover {
  transform: translateY(-4px);
}

.quick-actions {
  .v-card {
    cursor: pointer;
  }
}

/* Skeleton loader customization */
:deep(.v-skeleton-loader__heading) {
  max-width: 100px;
  margin: 0 auto;
  height: 48px !important;
}

/* Dark theme adjustments */
:deep(.v-theme--dark) .v-skeleton-loader__heading {
  background: rgba(255, 255, 255, 0.1) !important;
}
</style>
