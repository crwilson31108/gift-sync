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

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: LoginPage,
    meta: { requiresAuth: false }
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
})

router.beforeEach(async (to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth !== false)
  const isAuthenticated = authService.isAuthenticated()

  if (requiresAuth && !isAuthenticated) {
    // Store the intended destination
    localStorage.setItem('redirectPath', to.fullPath)
    next('/login')
  } else if (to.path === '/login' && isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router
