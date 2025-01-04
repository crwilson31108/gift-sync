// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { authService } from '@/services/auth'

// Pages/Views
import HomePage from '../pages/HomePage.vue'
import FamilyList from '../pages/FamilyList.vue'
import FamilyDetail from '../pages/FamilyDetail.vue'
import WishlistList from '../pages/WishlistList.vue'
import WishlistDetail from '../pages/WishlistDetail.vue'
import NotificationsPage from '@/pages/NotificationsPage.vue'
import LoginPage from '@/pages/LoginPage.vue'
import RequestPasswordResetPage from '@/pages/RequestPasswordResetPage.vue'
import ResetPasswordPage from '@/pages/ResetPasswordPage.vue'

// Define public routes
const PUBLIC_ROUTES = [
  '/login',
  '/request-password-reset',
  '/reset-password'
]

// Helper function to check if route is public
const isPublicRoute = (path: string): boolean => {
  return PUBLIC_ROUTES.some(route => path.startsWith(route))
}

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: LoginPage,
    meta: { requiresAuth: false, public: true, layout: 'blank' }
  },
  {
    path: '/',
    name: 'home',
    component: HomePage,
    meta: { requiresAuth: true }
  },
  { 
    path: '/families', 
    name: 'Families', 
    component: FamilyList,
    meta: { requiresAuth: true }
  },
  { 
    path: '/families/:id', 
    name: 'FamilyDetail', 
    component: FamilyDetail,
    meta: { requiresAuth: true }
  },
  { 
    path: '/wishlists', 
    name: 'Wishlists', 
    component: WishlistList,
    meta: { requiresAuth: true }
  },
  { 
    path: '/wishlists/:id', 
    name: 'WishlistDetail', 
    component: WishlistDetail,
    meta: { requiresAuth: true }
  },
  {
    path: '/members',
    name: 'members',
    component: () => import('@/pages/MembersList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/notifications',
    name: 'notifications',
    component: NotificationsPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/request-password-reset',
    name: 'RequestPasswordReset',
    component: RequestPasswordResetPage,
    meta: { requiresAuth: false, public: true, layout: 'blank' }
  },
  {
    path: '/reset-password/:userId/:token',
    name: 'ResetPassword',
    component: ResetPasswordPage,
    meta: { requiresAuth: false, public: true, layout: 'blank' }
  },
  // Catch all route for 404
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/pages/NotFoundPage.vue'),
    meta: { requiresAuth: false }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { 
        top: 0,
        behavior: 'smooth'
      }
    }
  }
})

router.beforeEach(async (to, from, next) => {
  // Always allow public routes
  if (isPublicRoute(to.path)) {
    next()
    return
  }

  // For protected routes, check authentication
  const isAuthenticated = authService.isAuthenticated()
  if (!isAuthenticated) {
    // Store the intended destination
    localStorage.setItem('redirectPath', to.fullPath)
    next('/login')
    return
  }

  next()
})

export default router
