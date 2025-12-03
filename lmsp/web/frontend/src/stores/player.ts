/**
 * Player State Store
 * ===================
 *
 * Manages player profile, achievements, and progress.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api/client'

export interface Achievement {
  id: string
  name: string
  description: string
  tier: 'bronze' | 'silver' | 'gold' | 'platinum' | 'diamond'
  icon: string
  xp_reward: number
  unlocked: boolean
  progress?: number
  required?: number
}

export interface PlayerProfile {
  player_id: string
  mastery_levels: Record<string, number>
  xp: number
  level: number
  achievements_unlocked: number
  achievements_total: number
}

export const usePlayerStore = defineStore('player', () => {
  // State
  const profile = ref<PlayerProfile | null>(null)
  const achievements = ref<Achievement[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const totalXP = computed(() => profile.value?.xp || 0)
  const playerLevel = computed(() => profile.value?.level || 0)
  const unlockedAchievements = computed(() =>
    achievements.value.filter(a => a.unlocked)
  )
  const inProgressAchievements = computed(() =>
    achievements.value.filter(a => !a.unlocked && a.progress !== undefined)
  )

  // Actions
  async function loadProfile() {
    isLoading.value = true
    error.value = null

    try {
      const response = await api.get('/api/profile?player_id=default')
      profile.value = response.data
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Failed to load profile'
    } finally {
      isLoading.value = false
    }
  }

  async function loadAchievements() {
    isLoading.value = true
    error.value = null

    try {
      const response = await api.get('/api/achievements?player_id=default')
      achievements.value = [
        ...response.data.unlocked.map((a: Achievement) => ({ ...a, unlocked: true })),
        ...response.data.in_progress.map((a: Achievement) => ({ ...a, unlocked: false })),
      ]
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Failed to load achievements'
    } finally {
      isLoading.value = false
    }
  }

  async function recordEmotionalFeedback(trigger: 'RT' | 'LT', value: number, context: string) {
    try {
      await api.post('/api/emotional/record', {
        player_id: 'default',
        trigger,
        value,
        context,
      })
    } catch (e) {
      console.error('Failed to record emotional feedback:', e)
    }
  }

  return {
    // State
    profile,
    achievements,
    isLoading,
    error,

    // Computed
    totalXP,
    playerLevel,
    unlockedAchievements,
    inProgressAchievements,

    // Actions
    loadProfile,
    loadAchievements,
    recordEmotionalFeedback,
  }
})
