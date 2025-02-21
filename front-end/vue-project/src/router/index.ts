import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/map',
      name: 'airport',
      component: () => import('../views/AirportView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/summaries',
      name: 'summaries',
      component: () => import('../views/SummaryView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/create-warning',
      name: 'create-warning',
      component: () => import('../views/WarningCreationView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('../views/AdminView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue'),
    },
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue'),
    },
    {
      path: '/inspection',
      name: 'inspection',
      component: () => import('../views/InspectionView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    }
  ],
});

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();
  await authStore.checkUserAuthority();

  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!authStore.isLoggedIn) {
      next({ path: '/login' });
    } else if (to.matched.some(record => record.meta.requiresAdmin) && authStore.userAuthority !== 'Admin') {
      next({ path: '/' }); // Redirect to home if not admin
    } else {
      next();
    }
  } else {
    next();
  }
});

export default router;
