/**
 * Vue Router Configuration
 * ========================
 *
 * SPA routing for LMSP.
 * Includes profile picker as entry point for multi-user support.
 */

import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/profiles',
      name: 'profiles',
      component: () => import('@/views/ProfilePickerView.vue'),
      meta: { public: true },
    },
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
    },
    {
      path: '/challenges',
      name: 'challenges',
      component: () => import('@/views/ChallengesView.vue'),
    },
    {
      path: '/challenge/:id',
      name: 'challenge',
      component: () => import('@/views/ChallengeView.vue'),
    },
    {
      path: '/concepts',
      name: 'concepts',
      component: () => import('@/views/ConceptsView.vue'),
    },
    {
      path: '/concept/:id',
      name: 'concept',
      component: () => import('@/views/ConceptLessonView.vue'),
    },
    {
      // Alias: /concepts/foo -> /concept/foo (common typo)
      path: '/concepts/:id',
      redirect: to => `/concept/${to.params.id}`,
    },
    {
      path: '/progress',
      name: 'progress',
      component: () => import('@/views/ProgressView.vue'),
    },
    {
      path: '/skill-tree',
      name: 'skill-tree',
      component: () => import('@/views/SkillTreeView.vue'),
    },
    {
      path: '/settings/:tab?',
      name: 'settings',
      component: () => import('@/views/SettingsView.vue'),
    },
    {
      path: '/achievements',
      name: 'achievements',
      component: () => import('@/views/AchievementsView.vue'),
    },
    {
      path: '/xp-analytics',
      name: 'xp-analytics',
      component: () => import('@/views/XpAnalyticsView.vue'),
    },
    {
      path: '/admin/:tab?',
      name: 'admin',
      component: () => import('@/views/AdminView.vue'),
      meta: { requiresAdmin: true },
    },
  ],
})

// Navigation guard: redirect to profile picker if no profile selected
router.beforeEach((to, _from, next) => {
  const playerId = localStorage.getItem('lmsp_player_id')

  // If going to public route (profile picker), allow
  if (to.meta.public) {
    next()
    return
  }

  // If no profile selected, redirect to profile picker
  if (!playerId) {
    next({ name: 'profiles' })
    return
  }

  // Profile selected, continue
  next()
})

export default router
