/**
 * Vue Router Configuration
 * ========================
 *
 * SPA routing for LMSP.
 * - Public routes: accessible without login
 * - Guest routes: browsable without login (read-only, no code execution)
 * - Protected routes: require login
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
      // Invite link: /invite/CODE -> ProfilePicker with invite code pre-filled
      path: '/invite/:code',
      name: 'invite',
      component: () => import('@/views/ProfilePickerView.vue'),
      meta: { public: true },
    },
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
      // Home requires login - guests go to profile picker
    },
    {
      path: '/challenges',
      name: 'challenges',
      component: () => import('@/views/ChallengesView.vue'),
      meta: { guest: true }, // Guests can browse challenges
    },
    {
      path: '/challenge/:id',
      name: 'challenge',
      component: () => import('@/views/ChallengeView.vue'),
      meta: { guest: true }, // Guests can view (but not run code)
    },
    {
      path: '/concepts',
      name: 'concepts',
      component: () => import('@/views/ConceptsView.vue'),
      meta: { guest: true }, // Guests can browse concepts
    },
    {
      path: '/concept/:id',
      name: 'concept',
      component: () => import('@/views/ConceptLessonView.vue'),
      meta: { guest: true }, // Guests can view lessons
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
      // Requires login - progress is personal
    },
    {
      path: '/skill-tree',
      name: 'skill-tree',
      component: () => import('@/views/SkillTreeView.vue'),
      meta: { guest: true }, // Guests can view the skill tree
    },
    {
      path: '/settings/:tab?',
      name: 'settings',
      component: () => import('@/views/SettingsView.vue'),
      // Requires login - settings are personal
    },
    {
      path: '/achievements',
      name: 'achievements',
      component: () => import('@/views/AchievementsView.vue'),
      // Requires login - achievements are personal
    },
    {
      path: '/xp-analytics',
      name: 'xp-analytics',
      component: () => import('@/views/XpAnalyticsView.vue'),
      // Requires login - analytics are personal
    },
    {
      path: '/admin/:tab?',
      name: 'admin',
      component: () => import('@/views/AdminView.vue'),
      meta: { requiresAdmin: true },
    },
  ],
})

// Navigation guard: handle public, guest, and protected routes
router.beforeEach((to, _from, next) => {
  const playerId = localStorage.getItem('lmsp_player_id')

  // Public routes (profile picker) - always allow
  if (to.meta.public) {
    next()
    return
  }

  // Guest-accessible routes - allow without login
  if (to.meta.guest) {
    next()
    return
  }

  // Protected routes - require login
  if (!playerId) {
    next({ name: 'profiles' })
    return
  }

  // Logged in, continue
  next()
})

export default router
