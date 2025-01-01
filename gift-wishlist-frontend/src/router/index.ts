// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

// Pages/Views
import HomePage from '../pages/HomePage.vue'
import FamilyList from '../pages/FamilyList.vue'
import WishlistList from '../pages/WishlistList.vue'
import WishlistDetail from '../pages/WishlistDetail.vue'
import NotificationsPage from '@/pages/NotificationsPage.vue'

const routes: RouteRecordRaw[] = [
  { path: '/', name: 'Home', component: HomePage },
  { path: '/families', name: 'Families', component: FamilyList },
  { path: '/wishlists', name: 'Wishlists', component: WishlistList },
  { path: '/wishlists/:id', name: 'WishlistDetail', component: WishlistDetail },
  {
    path: '/members',
    name: 'members',
    component: () => import('@/pages/MembersList.vue')
  },
  {
    path: '/notifications',
    name: 'notifications',
    component: NotificationsPage
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
