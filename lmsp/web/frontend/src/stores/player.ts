/**
 * Player State Store
 * ===================
 *
 * Manages player profile, achievements, and progress.
 * Uses auth store for player ID (multi-user support).
 */

import { defineStore, storeToRefs } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api/client'
import { useAuthStore } from '@/stores/auth'

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
  // Get player ID from auth store
  const authStore = useAuthStore()
  const { playerId: authPlayerId } = storeToRefs(authStore)

  // State
  const profile = ref<PlayerProfile | null>(null)
  const achievements = ref<Achievement[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const playerId = computed(() => authPlayerId.value || profile.value?.player_id || '')
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
    if (!playerId.value) {
      console.warn('No player ID set, cannot load profile')
      return
    }

    isLoading.value = true
    error.value = null

    try {
      const response = await api.get(`/api/profile?player_id=${playerId.value}`)
      profile.value = response.data
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Failed to load profile'
    } finally {
      isLoading.value = false
    }
  }

  async function loadAchievements() {
    if (!playerId.value) {
      console.warn('No player ID set, cannot load achievements')
      return
    }

    isLoading.value = true
    error.value = null

    try {
      const response = await api.get(`/api/achievements?player_id=${playerId.value}`)
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
    if (!playerId.value) return

    // Legacy method - prefer recordSatisfaction for new code
    // player_id comes from headers (set by api client)
    try {
      await api.post('/api/emotional/record', {
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
    if (!playerId.value) return { skipped: false }

    try {
      // player_id comes from headers (set by api client)
      const response = await api.post('/api/emotional/record', {
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
    if (!playerId.value) return false

    try {
      const response = await api.post('/api/profile/display-name', {
        player_id: playerId.value,
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
