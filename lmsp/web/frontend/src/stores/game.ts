/**
 * Game State Store
 * =================
 *
 * Manages current challenge, code, and game phase.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api/client'

export interface Challenge {
  id: string
  name: string
  level: number
  description_brief: string
  description_detailed: string
  skeleton_code: string
  test_cases: TestCase[]
  hints: Record<string, string>
  points: number
}

export interface TestCase {
  name: string
  input: unknown[]
  expected: unknown
}

export interface TestResult {
  name: string
  passed: boolean
  expected: unknown
  actual: unknown
}

export interface MasteryInfo {
  concept_id: string
  concept_name: string
  mastery_level: number
  mastery_percent: number
  next_hint: string
}

export interface ValidationResult {
  success: boolean
  tests_passing: number
  tests_total: number
  time_seconds: number
  output: string
  error?: string
  xp_earned?: number
  xp_reason?: string
  total_xp?: number
  mastery?: MasteryInfo
  achievement_unlocked?: {
    name: string
    description: string
    xp_reward: number
    icon: string
  }
}

export type GamePhase = 'menu' | 'selecting' | 'coding' | 'testing' | 'feedback' | 'complete'

export const useGameStore = defineStore('game', () => {
  // State
  const currentChallenge = ref<Challenge | null>(null)
  const code = ref('')
  const phase = ref<GamePhase>('menu')
  const testResults = ref<TestResult[]>([])
  const validationResult = ref<ValidationResult | null>(null)
  const isLoading = ref(false)        // Initial challenge load
  const isSubmitting = ref(false)     // Code submission in progress
  const error = ref<string | null>(null)
  const hintsUsed = ref(0)

  // Computed
  const testsPassingCount = computed(() =>
    testResults.value.filter(t => t.passed).length
  )

  const testsTotal = computed(() =>
    testResults.value.length
  )

  const allTestsPassing = computed(() =>
    testsPassingCount.value === testsTotal.value && testsTotal.value > 0
  )

  // Actions
  async function loadChallenge(challengeId: string) {
    isLoading.value = true
    error.value = null

    try {
      const response = await api.get(`/api/challenges/${challengeId}`)
      currentChallenge.value = response.data
      code.value = response.data.skeleton_code
      phase.value = 'coding'
      testResults.value = []
      validationResult.value = null
      hintsUsed.value = 0
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Failed to load challenge'
    } finally {
      isLoading.value = false
    }
  }

  async function submitCode() {
    if (!currentChallenge.value) return

    isSubmitting.value = true
    phase.value = 'testing'
    error.value = null

    try {
      const response = await api.post('/api/code/submit', {
        challenge_id: currentChallenge.value.id,
        code: code.value,
        player_id: 'default', // TODO: Get from player store
      })

      validationResult.value = response.data

      // Always return to coding phase after running tests
      // User can review their solution before submitting
      phase.value = 'coding'

      // Dispatch achievement event if unlocked (but don't auto-advance)
      if (response.data.success && response.data.achievement_unlocked) {
        window.dispatchEvent(new CustomEvent('lmsp:achievement', {
          detail: response.data.achievement_unlocked,
        }))
      }
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Submission failed'
      phase.value = 'coding'
    } finally {
      isSubmitting.value = false
    }
  }

  function useHint(): string | null {
    if (!currentChallenge.value) return null
    if (!currentChallenge.value.hints) return null

    // Hints are freely available - no artificial limits!
    // This isn't Duolingo. We want learners to succeed.
    hintsUsed.value++

    // Progressively reveal hints (more specific as you ask more)
    const hintKeys = Object.keys(currentChallenge.value.hints).sort()
    const hintIndex = Math.min(hintsUsed.value - 1, hintKeys.length - 1)
    const hintKey = hintKeys[hintIndex]

    return hintKey ? currentChallenge.value.hints[hintKey] : null
  }

  function getAllHints(): string[] {
    if (!currentChallenge.value?.hints) return []
    return Object.values(currentChallenge.value.hints)
  }

  function updateCode(newCode: string) {
    code.value = newCode
  }

  function proceedToFeedback() {
    // User explicitly wants to submit their solution
    if (validationResult.value?.success) {
      phase.value = 'feedback'
    }
  }

  function completeChallenge() {
    phase.value = 'complete'
  }

  function returnToMenu() {
    currentChallenge.value = null
    code.value = ''
    phase.value = 'menu'
    testResults.value = []
    validationResult.value = null
    hintsUsed.value = 0
  }

  return {
    // State
    currentChallenge,
    code,
    phase,
    testResults,
    validationResult,
    isLoading,
    isSubmitting,
    error,
    hintsUsed,

    // Computed
    testsPassingCount,
    testsTotal,
    allTestsPassing,

    // Actions
    loadChallenge,
    submitCode,
    useHint,
    getAllHints,
    updateCode,
    proceedToFeedback,
    completeChallenge,
    returnToMenu,
  }
})
