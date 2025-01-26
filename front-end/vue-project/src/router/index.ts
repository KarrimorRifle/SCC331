import { createRouter, createWebHistory } from 'vue-router'
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'airport',
      component: () => import('../views/AirportView.vue'),
    },
  ],
})

export default router
