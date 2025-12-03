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
  display_name: string | null
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
  const playerId = computed(() => profile.value?.player_id || 'default')
  const totalXP = computed(() => profile.value?.xp || 0)
  const playerLevel = computed(() => profile.value?.level || 0)
  const displayName = computed(() => profile.value?.display_name || profile.value?.player_id || 'Player')
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
    // Legacy method - prefer recordSatisfaction for new code
    try {
      await api.post('/api/emotional/record', {
        player_id: 'default',
        enjoyment: trigger === 'RT' ? value : 0,
        frustration: trigger === 'LT' ? value : 0,
        context,
        interacted: value > 0,
      })
    } catch (e) {
      console.error('Failed to record emotional feedback:', e)
    }
  }

  /**
   * Record satisfaction feedback with full context.
   *
   * @param enjoyment - 0.0-1.0 satisfaction/fun rating
   * @param frustration - 0.0-1.0 frustration/confusion rating
   * @param challengeId - Challenge this feedback is for
   * @param stage - Stage number (for multi-stage challenges)
   * @param interacted - True if user actually interacted with controls
   *                     If false and both values are 0, backend treats as "skipped"
   */
  async function recordSatisfaction(
    enjoyment: number,
    frustration: number,
    challengeId?: string,
    stage?: number,
    interacted: boolean = true
  ): Promise<{ skipped: boolean; mastery_factor?: number }> {
    try {
      const response = await api.post('/api/emotional/record', {
        player_id: 'default',
        enjoyment,
        frustration,
        challenge_id: challengeId,
        stage,
        context: challengeId ? `challenge:${challengeId}` : 'general',
        interacted,
      })
      return {
        skipped: response.data.skipped,
        mastery_factor: response.data.mastery_factor,
      }
    } catch (e) {
      console.error('Failed to record satisfaction:', e)
      return { skipped: false }
    }
  }

  async function setDisplayName(newName: string): Promise<boolean> {
    try {
      const response = await api.post('/api/profile/display-name', {
        player_id: 'default',
        display_name: newName,
      })
      if (response.data.success && profile.value) {
        profile.value.display_name = response.data.display_name
      }
      return response.data.success
    } catch (e) {
      console.error('Failed to set display name:', e)
      return false
    }
  }

  return {
    // State
    profile,
    achievements,
    isLoading,
    error,

    // Computed
    playerId,
    totalXP,
    playerLevel,
    displayName,
    unlockedAchievements,
    inProgressAchievements,

    // Actions
    loadProfile,
    loadAchievements,
    recordEmotionalFeedback,
    recordSatisfaction,
    setDisplayName,
  }
})
