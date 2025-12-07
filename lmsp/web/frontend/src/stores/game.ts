/**
 * Game State Store
 * =================
 *
 * Manages current challenge, code, and game phase.
 */

import { defineStore, storeToRefs } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api/client'
import { useAuthStore } from '@/stores/auth'

export interface ChallengeStage {
  stage_number: number
  name: string
  description: string
  skeleton_code: string | null
  test_count: number
  hints: Record<string, string>
}

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
  // Time attack and multi-stage fields
  challenge_mode: 'standard' | 'time_attack' | 'speed_run'
  time_limit_seconds: number
  speed_run_target: number
  stages: ChallengeStage[] | null
  is_multi_stage: boolean
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

export interface SuggestedLesson {
  id: string
  name: string
  level: number
  category: string
  time_to_read: number
  has_try_it: boolean
  depth: number
}

export interface DirectorIntervention {
  type: string
  content: string
  reason: string
  confidence: number
  suggested_lessons?: SuggestedLesson[]
}

export interface ValidationResult {
  success: boolean
  tests_passing: number
  tests_total: number
  time_seconds: number
  output: string
  stdout?: string  // User print() output, separate from test output
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
  // Multi-stage challenge fields
  is_multi_stage?: boolean
  total_stages?: number
  current_stage?: number
  stage_complete?: boolean
  challenge_complete?: boolean
  next_stage?: number
  next_stage_info?: {
    stage_number: number
    name: string
    description: string
  }
  // Director intervention fields
  director_intervention?: DirectorIntervention
  suggested_lessons?: SuggestedLesson[]
  suggestion_reason?: string
}

export type GamePhase = 'menu' | 'selecting' | 'coding' | 'testing' | 'feedback' | 'complete'

export const useGameStore = defineStore('game', () => {
  // Get player ID from auth store (multi-user support)
  const authStore = useAuthStore()
  const { playerId } = storeToRefs(authStore)

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

  // Replay mode: when replaying a completed challenge for spaced repetition
  const isReplayMode = ref(false)
  const previousSolution = ref<string | null>(null)

  // Multi-stage challenge state
  const currentStage = ref(1)
  const stageCompletedCode = ref<Record<number, string>>({})  // Code from completed stages
  const stageTimes = ref<Record<number, number>>({})          // Time spent on each stage (current run)
  const bestStageTimes = ref<Record<number, number>>({})      // Personal best times per stage
  const stageStartTime = ref<number | null>(null)             // When current stage started

  // Timer state - tracks wall-clock coding time
  const timerStartedAt = ref<number | null>(null)     // Timestamp when timer started
  const timerAccumulated = ref(0)                      // Accumulated seconds from previous sessions
  const timerPaused = ref(false)                       // Timer paused state
  const TIMER_PREFIX = 'lmsp_timer_'

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

  // Elapsed time in seconds (computed from start time + accumulated)
  const elapsedSeconds = computed(() => {
    if (timerPaused.value || !timerStartedAt.value) {
      return timerAccumulated.value
    }
    const now = Date.now()
    const sessionSeconds = (now - timerStartedAt.value) / 1000
    return timerAccumulated.value + sessionSeconds
  })

  // LocalStorage helpers for Save/Load
  const STORAGE_PREFIX = 'lmsp_challenge_'
  const COMPLETED_PREFIX = 'lmsp_completed_'
  const STAGE_PREFIX = 'lmsp_stage_'

  function getSavedCode(challengeId: string): string | null {
    try {
      return localStorage.getItem(`${STORAGE_PREFIX}${challengeId}`)
    } catch {
      return null
    }
  }

  function saveCode(challengeId: string, codeToSave: string) {
    try {
      localStorage.setItem(`${STORAGE_PREFIX}${challengeId}`, codeToSave)
    } catch {
      // Ignore storage errors (quota, etc.)
    }
  }

  function clearSavedCode(challengeId: string) {
    try {
      localStorage.removeItem(`${STORAGE_PREFIX}${challengeId}`)
    } catch {
      // Ignore
    }
  }

  function isCompleted(challengeId: string): boolean {
    try {
      return localStorage.getItem(`${COMPLETED_PREFIX}${challengeId}`) === 'true'
    } catch {
      return false
    }
  }

  function markCompleted(challengeId: string) {
    try {
      localStorage.setItem(`${COMPLETED_PREFIX}${challengeId}`, 'true')
    } catch {
      // Ignore
    }
  }

  // Stage persistence helpers
  function getSavedStage(challengeId: string): number {
    try {
      const saved = localStorage.getItem(`${STAGE_PREFIX}${challengeId}`)
      return saved ? parseInt(saved, 10) : 1
    } catch {
      return 1
    }
  }

  function saveStage(challengeId: string, stage: number) {
    try {
      localStorage.setItem(`${STAGE_PREFIX}${challengeId}`, stage.toString())
    } catch {
      // Ignore
    }
  }

  function clearSavedStage(challengeId: string) {
    try {
      localStorage.removeItem(`${STAGE_PREFIX}${challengeId}`)
    } catch {
      // Ignore
    }
  }

  // Timer localStorage helpers
  function getSavedTimer(challengeId: string): number {
    try {
      const saved = localStorage.getItem(`${TIMER_PREFIX}${challengeId}`)
      return saved ? parseFloat(saved) : 0
    } catch {
      return 0
    }
  }

  function saveTimer(challengeId: string, seconds: number) {
    try {
      localStorage.setItem(`${TIMER_PREFIX}${challengeId}`, seconds.toString())
    } catch {
      // Ignore
    }
  }

  function clearSavedTimer(challengeId: string) {
    try {
      localStorage.removeItem(`${TIMER_PREFIX}${challengeId}`)
    } catch {
      // Ignore
    }
  }

  // Best stage times helpers
  const STAGE_TIMES_PREFIX = 'lmsp_stage_times_'

  function getSavedBestStageTimes(challengeId: string): Record<number, number> {
    try {
      const saved = localStorage.getItem(`${STAGE_TIMES_PREFIX}${challengeId}`)
      return saved ? JSON.parse(saved) : {}
    } catch {
      return {}
    }
  }

  function saveBestStageTimes(challengeId: string, times: Record<number, number>) {
    try {
      localStorage.setItem(`${STAGE_TIMES_PREFIX}${challengeId}`, JSON.stringify(times))
    } catch {
      // Ignore
    }
  }

  function recordStageTime(stageNumber: number) {
    // Record time for the completed stage
    if (stageStartTime.value === null) return

    const stageElapsed = (Date.now() - stageStartTime.value) / 1000
    stageTimes.value[stageNumber] = stageElapsed

    // Update best time if this is faster (or first time)
    if (currentChallenge.value) {
      const challengeId = currentChallenge.value.id
      const currentBest = bestStageTimes.value[stageNumber]

      if (currentBest === undefined || stageElapsed < currentBest) {
        bestStageTimes.value[stageNumber] = stageElapsed
        saveBestStageTimes(challengeId, bestStageTimes.value)
      }
    }
  }

  function startStageTimer() {
    stageStartTime.value = Date.now()
  }

  function getCurrentStageElapsed(): number {
    if (stageStartTime.value === null) return 0
    return (Date.now() - stageStartTime.value) / 1000
  }

  // Timer control functions
  function startTimer() {
    if (!timerPaused.value && timerStartedAt.value) return // Already running
    timerStartedAt.value = Date.now()
    timerPaused.value = false
  }

  function pauseTimer() {
    if (timerPaused.value || !timerStartedAt.value) return
    // Accumulate current session time
    const sessionSeconds = (Date.now() - timerStartedAt.value) / 1000
    timerAccumulated.value += sessionSeconds
    timerStartedAt.value = null
    timerPaused.value = true
    // Persist to localStorage
    if (currentChallenge.value) {
      saveTimer(currentChallenge.value.id, timerAccumulated.value)
    }
  }

  function resetTimer() {
    timerStartedAt.value = null
    timerAccumulated.value = 0
    timerPaused.value = false
    if (currentChallenge.value) {
      clearSavedTimer(currentChallenge.value.id)
    }
  }

  function getElapsedSeconds(): number {
    if (timerPaused.value || !timerStartedAt.value) {
      return timerAccumulated.value
    }
    const sessionSeconds = (Date.now() - timerStartedAt.value) / 1000
    return timerAccumulated.value + sessionSeconds
  }

  // Actions
  async function loadChallenge(challengeId: string) {
    isLoading.value = true
    error.value = null

    try {
      const response = await api.get(`/api/challenges/${challengeId}`)
      currentChallenge.value = response.data

      // Check if this is a replay of a completed challenge
      const saved = getSavedCode(challengeId)
      const wasCompleted = isCompleted(challengeId)

      if (wasCompleted && saved) {
        // Replay mode: store previous solution, start fresh with skeleton
        isReplayMode.value = true
        previousSolution.value = saved
        code.value = response.data.skeleton_code
        // Reset timer for replay mode - fresh start
        timerAccumulated.value = 0
        clearSavedTimer(challengeId)
      } else {
        // Normal mode: load saved code or skeleton
        isReplayMode.value = false
        previousSolution.value = null
        code.value = saved ?? response.data.skeleton_code
        // Restore accumulated time from previous session
        timerAccumulated.value = getSavedTimer(challengeId)
      }

      // Start the timer
      timerStartedAt.value = Date.now()
      timerPaused.value = false

      phase.value = 'coding'
      testResults.value = []
      validationResult.value = null
      hintsUsed.value = 0

      // Restore multi-stage state
      const savedStage = getSavedStage(challengeId)
      currentStage.value = response.data.is_multi_stage ? savedStage : 1
      stageCompletedCode.value = {}
      stageTimes.value = {}

      // Load best stage times for this challenge
      bestStageTimes.value = getSavedBestStageTimes(challengeId)

      // Start stage timer (for multi-stage, tracks time per stage)
      stageStartTime.value = Date.now()
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
      // Capture current solve time BEFORE pausing (in case tests pass)
      const currentSolveTime = getElapsedSeconds()

      // Build submit payload - include stage for multi-stage challenges
      const payload: Record<string, unknown> = {
        challenge_id: currentChallenge.value.id,
        code: code.value,
        player_id: playerId.value,
        solve_time: currentSolveTime, // Send wall-clock coding time to backend
      }

      // For multi-stage challenges, include current stage
      if (currentChallenge.value.is_multi_stage) {
        payload.stage = currentStage.value
      }

      // Quick run to get stdout immediately (non-blocking)
      api.post('/api/code/run', { code: code.value }).then(runResponse => {
        // Show console output immediately while tests are still running
        if (runResponse.data.stdout && !validationResult.value) {
          validationResult.value = {
            success: false,
            tests_passing: 0,
            tests_total: 0,
            time_seconds: 0,
            output: '',
            stdout: runResponse.data.stdout,
          }
        }
      }).catch(() => {
        // Ignore errors from quick run - tests will still work
      })

      const response = await api.post('/api/code/submit', payload)

      validationResult.value = response.data

      // Freeze timer the instant all tests pass - captures exact solve time
      if (response.data.success) {
        pauseTimer()
      }

      // Always return to coding phase after running tests
      // User can review their solution before submitting
      phase.value = 'coding'

      // Handle multi-stage completion
      if (response.data.is_multi_stage && response.data.stage_complete) {
        // Record time for this stage
        recordStageTime(currentStage.value)

        // Store completed stage's code
        stageCompletedCode.value[currentStage.value] = code.value

        if (response.data.challenge_complete) {
          // All stages done - mark challenge as completed
          if (currentChallenge.value) {
            markCompleted(currentChallenge.value.id)
            clearSavedStage(currentChallenge.value.id)  // Reset for next playthrough
          }
        }
        // Note: Don't auto-advance - let the UI show the stage complete message
        // and user can click to advance
      } else if (response.data.success && currentChallenge.value && !response.data.is_multi_stage) {
        // Single-stage challenge - record as stage 1
        recordStageTime(1)
        // Single-stage challenge completed
        markCompleted(currentChallenge.value.id)
        // In replay mode, update the previous solution with the new one
        if (isReplayMode.value) {
          previousSolution.value = code.value
        }
      }

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

  function advanceToNextStage() {
    if (!validationResult.value?.next_stage) return

    // Advance to next stage
    currentStage.value = validationResult.value.next_stage
    validationResult.value = null

    // Persist stage to localStorage
    if (currentChallenge.value) {
      saveStage(currentChallenge.value.id, currentStage.value)
    }

    // Start fresh stage timer for the new stage
    stageStartTime.value = Date.now()

    // Resume main timer (it was paused when previous stage completed)
    timerStartedAt.value = Date.now()
    timerPaused.value = false

    // Keep the current code (code carries forward in multi-stage challenges)
    // The learner builds on their previous work
  }

  function useHint(): string | null {
    if (!currentChallenge.value) return null

    // For multi-stage challenges, use stage-specific hints
    let hints = currentChallenge.value.hints
    if (currentChallenge.value.is_multi_stage && currentChallenge.value.stages) {
      const stageData = currentChallenge.value.stages[currentStage.value - 1]
      if (stageData?.hints) {
        hints = stageData.hints
      }
    }

    if (!hints) return null

    // Hints are freely available - no artificial limits!
    // This isn't Duolingo. We want learners to succeed.
    hintsUsed.value++

    // Progressively reveal hints (more specific as you ask more)
    const hintKeys = Object.keys(hints).sort()
    const hintIndex = Math.min(hintsUsed.value - 1, hintKeys.length - 1)
    const hintKey = hintKeys[hintIndex]

    return hintKey ? hints[hintKey] : null
  }

  function getAllHints(): string[] {
    if (!currentChallenge.value) return []

    // For multi-stage challenges, use stage-specific hints
    let hints = currentChallenge.value.hints
    if (currentChallenge.value.is_multi_stage && currentChallenge.value.stages) {
      const stageData = currentChallenge.value.stages[currentStage.value - 1]
      if (stageData?.hints) {
        hints = stageData.hints
      }
    }

    if (!hints) return []
    return Object.values(hints)
  }

  function updateCode(newCode: string) {
    code.value = newCode
    // Auto-save to localStorage
    if (currentChallenge.value) {
      saveCode(currentChallenge.value.id, newCode)
    }
  }

  function resetCode() {
    // Clear saved code and restore skeleton
    if (currentChallenge.value) {
      clearSavedCode(currentChallenge.value.id)
      code.value = currentChallenge.value.skeleton_code
      validationResult.value = null
      hintsUsed.value = 0
      // Reset timer on code reset - fresh start
      resetTimer()
      startTimer()
    }
  }

  function hasSavedCode(): boolean {
    if (!currentChallenge.value) return false
    const saved = getSavedCode(currentChallenge.value.id)
    return saved !== null && saved !== currentChallenge.value.skeleton_code
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
    // Save timer state before leaving
    pauseTimer()

    currentChallenge.value = null
    code.value = ''
    phase.value = 'menu'
    testResults.value = []
    validationResult.value = null
    hintsUsed.value = 0
    timerStartedAt.value = null
    timerAccumulated.value = 0
    timerPaused.value = false
  }

  function viewPreviousSolution() {
    // Swap current code with previous solution
    if (previousSolution.value && currentChallenge.value) {
      const currentCode = code.value
      code.value = previousSolution.value
      previousSolution.value = currentCode
    }
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
    isReplayMode,
    previousSolution,

    // Timer state
    timerPaused,

    // Multi-stage state
    currentStage,
    stageCompletedCode,
    stageTimes,
    bestStageTimes,

    // Computed
    testsPassingCount,
    testsTotal,
    allTestsPassing,
    elapsedSeconds,

    // Actions
    loadChallenge,
    submitCode,
    useHint,
    getAllHints,
    updateCode,
    resetCode,
    hasSavedCode,
    proceedToFeedback,
    completeChallenge,
    returnToMenu,
    viewPreviousSolution,

    // Timer actions
    startTimer,
    pauseTimer,
    resetTimer,
    getElapsedSeconds,

    // Multi-stage actions
    advanceToNextStage,
    getCurrentStageElapsed,
  }
})
