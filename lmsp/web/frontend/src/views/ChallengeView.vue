<script setup lang="ts">
import { onMounted, onUnmounted, ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { marked } from 'marked'
import { useGameStore } from '@/stores/game'
import { useGamepadStore } from '@/stores/gamepad'
import { usePlayerStore } from '@/stores/player'
import { useGamepadNav } from '@/composables/useGamepadNav'
import CodeEditor from '@/components/game/CodeEditor.vue'
import TestResults from '@/components/game/TestResults.vue'
import EmotionalFeedback from '@/components/input/EmotionalFeedback.vue'
import { LogIn } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const gameStore = useGameStore()
const gamepadStore = useGamepadStore()
const playerStore = usePlayerStore()

// Guest mode - user is browsing without logging in
const isGuest = computed(() => !playerStore.playerId)

// Timer display - updates every second
const displayedTime = ref(0)
const displayedStageTime = ref(0)
const showTimerTooltip = ref(false)
let timerInterval: number | null = null

function updateTimerDisplay() {
  displayedTime.value = gameStore.getElapsedSeconds()
  displayedStageTime.value = gameStore.getCurrentStageElapsed()
}

function formatTime(seconds: number): string {
  const hrs = Math.floor(seconds / 3600)
  const mins = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)

  if (hrs > 0) {
    return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

// Enable gamepad navigation for D-pad between buttons
useGamepadNav({ onBack: () => router.push('/challenges') })

const showHint = ref(false)
const viewedHints = ref<string[]>([])
const hintIndex = ref(0)
const isViewingPreviousSolution = ref(false)

// Current hint is based on index into viewed hints
const currentHint = computed(() => {
  if (viewedHints.value.length === 0) return null
  return viewedHints.value[hintIndex.value] ?? null
})

onMounted(async () => {
  const challengeId = route.params.id as string
  isViewingPreviousSolution.value = false
  await gameStore.loadChallenge(challengeId)

  // Start timer display update interval
  updateTimerDisplay()
  timerInterval = window.setInterval(updateTimerDisplay, 1000)
})

onUnmounted(() => {
  // Clean up timer interval
  if (timerInterval !== null) {
    clearInterval(timerInterval)
    timerInterval = null
  }
  // Pause timer when leaving (saves to localStorage)
  gameStore.pauseTimer()
})

// Watch for gamepad button presses
watch(() => gamepadStore.buttons, (buttons) => {
  if (!gameStore.currentChallenge) return

  // X button = run tests
  if (buttons.X && gameStore.phase === 'coding') {
    gameStore.submitCode()
  }

  // Y button = show hint
  if (buttons.Y && gameStore.phase === 'coding') {
    requestHint()
  }

  // B button = back
  if (buttons.B) {
    if (gameStore.phase === 'coding') {
      router.push('/challenges')
    }
  }
}, { deep: true })

function requestHint() {
  const newHint = gameStore.useHint()
  if (newHint && !viewedHints.value.includes(newHint)) {
    viewedHints.value.push(newHint)
    hintIndex.value = viewedHints.value.length - 1
  }
  showHint.value = true
}

function prevHint() {
  if (hintIndex.value > 0) {
    hintIndex.value--
  }
}

function nextHint() {
  if (hintIndex.value < viewedHints.value.length - 1) {
    hintIndex.value++
  }
}

function togglePreviousSolution() {
  gameStore.viewPreviousSolution()
  isViewingPreviousSolution.value = !isViewingPreviousSolution.value
}

function runTests() {
  gameStore.submitCode()
}

function confirmReset() {
  if (confirm('Reset your code to the starting template? Your changes will be lost.')) {
    gameStore.resetCode()
  }
}

function handleEmotionalConfirm(feedback: { enjoyment: number; frustration: number }) {
  // For stage completion, advance to next stage
  if (stageComplete.value && !challengeComplete.value && hasNextStage.value) {
    advanceStage()
    gameStore.phase = 'coding'  // Return to coding for next stage
  } else {
    // Full challenge completion
    gameStore.completeChallenge()
  }
}

function nextChallenge() {
  // TODO: Get next recommendation
  router.push('/challenges')
}

function returnToMenu() {
  gameStore.returnToMenu()
  router.push('/')
}

const testResultsForDisplay = computed(() => {
  if (!gameStore.validationResult) return null
  return {
    success: gameStore.validationResult.success,
    passing: gameStore.validationResult.tests_passing,
    total: gameStore.validationResult.tests_total,
    output: gameStore.validationResult.output,
    stdout: gameStore.validationResult.stdout,
    error: gameStore.validationResult.error,
  }
})

// Suggested lessons from Director intervention or repeated failures
const suggestedLessons = computed(() => {
  if (!gameStore.validationResult) return []

  // Check Director intervention first
  if (gameStore.validationResult.director_intervention?.suggested_lessons) {
    return gameStore.validationResult.director_intervention.suggested_lessons
  }

  // Check direct suggested_lessons (from repeated failures)
  if (gameStore.validationResult.suggested_lessons) {
    return gameStore.validationResult.suggested_lessons
  }

  return []
})

const directorIntervention = computed(() => {
  return gameStore.validationResult?.director_intervention ?? null
})

function goToLesson(lessonId: string) {
  router.push(`/concepts/${lessonId}`)
}

// Challenge context for "Copy All for Claude Code"
const challengeContext = computed(() => {
  if (!gameStore.currentChallenge) return undefined
  return {
    name: gameStore.currentChallenge.name,
    description: gameStore.currentChallenge.description_detailed || gameStore.currentChallenge.description_brief,
    code: gameStore.code,
  }
})

// Rendered description markdown
const renderedDescription = computed(() => {
  if (!gameStore.currentChallenge?.description_detailed) return ''
  return marked(gameStore.currentChallenge.description_detailed)
})

// Rendered hint markdown
const renderedHint = computed(() => {
  if (!currentHint.value) return ''
  return marked(currentHint.value)
})

// Multi-stage helpers
const isMultiStage = computed(() => gameStore.currentChallenge?.is_multi_stage ?? false)
const totalStages = computed(() => gameStore.currentChallenge?.stages?.length ?? 0)
const currentStageData = computed(() => {
  if (!isMultiStage.value || !gameStore.currentChallenge?.stages) return null
  // Stages array is 0-indexed, currentStage is 1-indexed
  return gameStore.currentChallenge.stages[gameStore.currentStage - 1] ?? null
})

// Stage description (rendered markdown)
const renderedStageDescription = computed(() => {
  if (!currentStageData.value?.description) return ''
  return marked(currentStageData.value.description)
})

// Check if current stage is complete (from validation result)
const stageComplete = computed(() => gameStore.validationResult?.stage_complete ?? false)
const challengeComplete = computed(() => gameStore.validationResult?.challenge_complete ?? false)
const hasNextStage = computed(() => gameStore.validationResult?.next_stage !== undefined)

function advanceStage() {
  gameStore.advanceToNextStage()
}
</script>

<template>
  <div class="max-w-6xl mx-auto px-4 py-8">
    <!-- Loading State (only for initial load, not during submission) -->
    <div v-if="gameStore.isLoading && !gameStore.currentChallenge" class="text-center py-12 text-text-muted">
      Loading challenge...
    </div>

    <!-- Error State -->
    <div v-else-if="gameStore.error" class="text-center py-12">
      <div class="text-4xl mb-4">❌</div>
      <div class="text-accent-error">{{ gameStore.error }}</div>
      <button class="oled-button mt-4 gamepad-focusable" @click="router.push('/challenges')">
        Back to Challenges
      </button>
    </div>

    <!-- Challenge Content -->
    <template v-else-if="gameStore.currentChallenge">
      <!-- Coding Phase -->
      <template v-if="gameStore.phase === 'coding' || gameStore.phase === 'testing'">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Challenge Info -->
          <div class="lg:col-span-1">
            <div class="oled-panel sticky top-20">
              <div class="flex items-center gap-2 mb-2">
                <div class="level-badge">Level {{ gameStore.currentChallenge.level }}</div>
                <!-- Stage indicator for multi-stage challenges -->
                <div v-if="isMultiStage" class="stage-badge">
                  Stage {{ gameStore.currentStage }}/{{ totalStages }}
                </div>
                <div v-if="gameStore.isReplayMode" class="px-2 py-0.5 text-xs font-medium bg-accent-primary/20 text-accent-primary border border-accent-primary/30 rounded">
                  🔄 Replay Mode
                </div>
                <!-- Timer with tooltip (hidden for guests) -->
                <div
                  v-if="!isGuest"
                  class="ml-auto timer-display relative"
                  :class="{ 'timer-paused': gameStore.timerPaused }"
                  @mouseenter="showTimerTooltip = true"
                  @mouseleave="showTimerTooltip = false"
                >
                  <span>⏱️ {{ formatTime(isMultiStage ? displayedStageTime : displayedTime) }}</span>
                  <!-- Timer tooltip -->
                  <div
                    v-if="showTimerTooltip && isMultiStage"
                    class="timer-tooltip"
                  >
                    <div class="text-xs font-semibold text-text-secondary mb-2 border-b border-oled-border pb-1">
                      Stage Times
                    </div>
                    <!-- Previous stages -->
                    <div
                      v-for="stage in (gameStore.currentStage - 1)"
                      :key="stage"
                      class="flex justify-between gap-4 text-xs mb-1"
                    >
                      <span class="text-text-muted">Stage {{ stage }}:</span>
                      <div class="flex gap-2">
                        <span class="text-accent-success">{{ formatTime(gameStore.stageTimes[stage] || 0) }}</span>
                        <span v-if="gameStore.bestStageTimes[stage]" class="text-text-muted">
                          (best: {{ formatTime(gameStore.bestStageTimes[stage]) }})
                        </span>
                      </div>
                    </div>
                    <!-- Current stage -->
                    <div class="flex justify-between gap-4 text-xs">
                      <span class="text-accent-primary font-medium">Stage {{ gameStore.currentStage }}:</span>
                      <div class="flex gap-2">
                        <span class="text-text-primary font-medium">{{ formatTime(displayedStageTime) }}</span>
                        <span v-if="gameStore.bestStageTimes[gameStore.currentStage]" class="text-text-muted">
                          (best: {{ formatTime(gameStore.bestStageTimes[gameStore.currentStage]) }})
                        </span>
                      </div>
                    </div>
                    <!-- Total -->
                    <div class="flex justify-between gap-4 text-xs mt-2 pt-1 border-t border-oled-border">
                      <span class="text-text-secondary">Total:</span>
                      <span class="text-text-primary">{{ formatTime(displayedTime) }}</span>
                    </div>
                  </div>
                  <!-- Single-stage tooltip (just show best time if exists) -->
                  <div
                    v-else-if="showTimerTooltip && !isMultiStage && gameStore.bestStageTimes[1]"
                    class="timer-tooltip"
                  >
                    <div class="flex justify-between gap-4 text-xs">
                      <span class="text-text-muted">Best time:</span>
                      <span class="text-accent-success">{{ formatTime(gameStore.bestStageTimes[1]) }}</span>
                    </div>
                  </div>
                </div>
              </div>
              <h1 class="text-2xl font-bold mb-2">{{ gameStore.currentChallenge.name }}</h1>
              <!-- Stage name for multi-stage challenges -->
              <div v-if="isMultiStage && currentStageData" class="text-lg text-accent-secondary font-medium mb-2">
                {{ currentStageData.name }}
              </div>
              <p class="text-text-secondary mb-4">
                {{ isMultiStage && currentStageData
                  ? currentStageData.description?.split('\n')[0]
                  : gameStore.currentChallenge.description_brief }}
              </p>

              <!-- Gamepad Controls (hidden for guests) -->
              <div v-if="gamepadStore.connected && !isGuest" class="border-t border-oled-border pt-4 mt-4">
                <div class="text-sm text-text-muted mb-2">Controls</div>
                <div class="grid grid-cols-2 gap-2 text-sm">
                  <div><span class="gamepad-button">X</span> Run Tests</div>
                  <div><span class="gamepad-button">Y</span> Hint</div>
                  <div><span class="gamepad-button">B</span> Back</div>
                </div>
              </div>

              <!-- Hint -->
              <div v-if="showHint && currentHint" class="mt-4 p-3 bg-accent-warning/10 border border-accent-warning/30 rounded-lg">
                <div class="flex items-center justify-between mb-1">
                  <div class="text-sm text-accent-warning font-medium">💡 Hint</div>
                  <!-- Hint navigation (only show if multiple hints viewed) -->
                  <div v-if="viewedHints.length > 1" class="flex items-center gap-1">
                    <button
                      class="hint-nav-btn"
                      :class="{ 'opacity-30 cursor-default': hintIndex === 0 }"
                      :disabled="hintIndex === 0"
                      @click="prevHint"
                    >‹</button>
                    <span class="text-xs text-text-muted px-1">{{ hintIndex + 1 }}/{{ viewedHints.length }}</span>
                    <button
                      class="hint-nav-btn"
                      :class="{ 'opacity-30 cursor-default': hintIndex === viewedHints.length - 1 }"
                      :disabled="hintIndex === viewedHints.length - 1"
                      @click="nextHint"
                    >›</button>
                  </div>
                </div>
                <div class="prose prose-invert prose-sm hint-content" v-html="renderedHint"></div>
              </div>

              <!-- Action Buttons -->
              <div class="flex flex-col gap-2 mt-4">
                <!-- Guest Mode: Sign in prompt -->
                <template v-if="isGuest">
                  <div class="p-4 bg-accent-primary/5 border border-accent-primary/20 rounded-lg">
                    <div class="flex items-center gap-2 mb-2">
                      <LogIn :size="18" class="text-accent-primary" />
                      <span class="font-medium text-text-primary">Want to try this challenge?</span>
                    </div>
                    <p class="text-sm text-text-secondary mb-3">
                      Sign in to run your code, track progress, and earn XP!
                    </p>
                    <button
                      class="oled-button-primary w-full gamepad-focusable"
                      @click="router.push('/profiles')"
                    >
                      Sign In to Start Coding
                    </button>
                  </div>
                  <button class="oled-button gamepad-focusable" @click="requestHint">
                    💡 Preview a hint
                  </button>
                </template>

                <!-- Logged In: Full action buttons -->
                <template v-else>
                  <!-- Stage complete: go to feedback then advance to next stage -->
                  <button
                    v-if="stageComplete && hasNextStage && !challengeComplete"
                    class="oled-button-success gamepad-focusable animate-pulse"
                    @click="gameStore.proceedToFeedback"
                  >
                    ✅ Continue to Stage {{ gameStore.validationResult?.next_stage }}
                  </button>

                  <!-- Challenge complete (single-stage or final stage) -->
                  <button
                    v-else-if="gameStore.validationResult?.success && (!isMultiStage || challengeComplete)"
                    class="oled-button-success gamepad-focusable"
                    @click="gameStore.proceedToFeedback"
                  >
                    ✅ Submit Solution
                  </button>

                  <button
                    class="oled-button-primary gamepad-focusable"
                    :disabled="gameStore.isSubmitting"
                    @click="runTests"
                  >
                    {{ gameStore.isSubmitting ? '⏳ Running...' : '▶ Run Tests' }}
                  </button>
                  <button class="oled-button gamepad-focusable" @click="requestHint">
                    💡 Need a hint?
                  </button>

                  <!-- View Previous Solution (only in replay mode) -->
                  <button
                    v-if="gameStore.isReplayMode"
                    class="oled-button gamepad-focusable"
                    :class="{ 'border-accent-primary text-accent-primary': isViewingPreviousSolution }"
                    @click="togglePreviousSolution"
                  >
                    {{ isViewingPreviousSolution ? '📝 Back to Current Work' : '👀 View Previous Solution' }}
                  </button>

                  <!-- Reset button (only show if code differs from skeleton) -->
                  <button
                    v-if="gameStore.hasSavedCode()"
                    class="oled-button text-accent-warning gamepad-focusable"
                    @click="confirmReset"
                  >
                    🔄 Reset to Start
                  </button>
                </template>
              </div>

              <!-- Stage completion message -->
              <div v-if="stageComplete && !challengeComplete" class="mt-4 p-3 bg-accent-success/10 border border-accent-success/30 rounded-lg">
                <div class="text-sm text-accent-success font-medium mb-1">🏔️ Keep pushing! Stage {{ gameStore.currentStage }} complete!</div>
                <div v-if="gameStore.validationResult?.next_stage_info" class="text-sm text-text-secondary">
                  Next: {{ gameStore.validationResult.next_stage_info.name }}
                </div>
                <div v-if="gameStore.validationResult?.xp_earned" class="text-sm text-accent-primary mt-1">
                  +{{ gameStore.validationResult.xp_earned }} XP
                </div>
              </div>

              <!-- Stage Instructions (for multi-stage) -->
              <div
                v-if="isMultiStage && renderedStageDescription"
                class="mt-6 pt-4 border-t border-oled-border"
              >
                <div class="text-sm text-text-muted mb-2">Stage {{ gameStore.currentStage }} Instructions</div>
                <div class="prose prose-invert prose-sm" v-html="renderedStageDescription"></div>
              </div>

              <!-- Detailed Description (for single-stage or general info) -->
              <div
                v-else-if="renderedDescription"
                class="mt-6 pt-4 border-t border-oled-border"
              >
                <div class="text-sm text-text-muted mb-2">Instructions</div>
                <div class="prose prose-invert prose-sm" v-html="renderedDescription"></div>
              </div>
            </div>
          </div>

          <!-- Code Editor -->
          <div class="lg:col-span-2">
            <!-- Guest Preview Banner -->
            <div v-if="isGuest" class="mb-4 p-3 bg-oled-panel border border-oled-border rounded-lg flex items-center gap-3">
              <div class="text-2xl">👀</div>
              <div>
                <div class="text-sm font-medium text-text-primary">Preview Mode</div>
                <div class="text-xs text-text-muted">Sign in to edit code and run tests</div>
              </div>
            </div>

            <CodeEditor
              :code="gameStore.code"
              :readonly="isGuest || gameStore.phase === 'testing'"
              @update:code="gameStore.updateCode"
            />

            <!-- Test Results (logged-in users only) -->
            <TestResults
              v-if="testResultsForDisplay && !isGuest"
              :results="testResultsForDisplay"
              :challenge="challengeContext"
              class="mt-6"
            />

            <!-- Sample Output Preview (guests only) -->
            <div v-if="isGuest" class="mt-6 oled-panel">
              <div class="flex items-center gap-2 mb-3">
                <span class="text-lg">📋</span>
                <span class="font-medium text-text-primary">Sample Output</span>
                <span class="text-xs text-text-muted ml-auto">What running code looks like</span>
              </div>
              <div class="bg-oled-black border border-oled-border rounded-lg p-4 font-mono text-sm">
                <div class="text-accent-success mb-2">✓ Test 1: Basic functionality... PASSED</div>
                <div class="text-accent-success mb-2">✓ Test 2: Edge cases... PASSED</div>
                <div class="text-text-muted text-xs mt-3 pt-3 border-t border-oled-border">
                  Sign in to run your own code and see real test results!
                </div>
              </div>
            </div>

            <!-- Director Intervention & Suggested Lessons -->
            <div
              v-if="directorIntervention || suggestedLessons.length > 0"
              class="mt-6 director-suggestion"
            >
              <!-- Director Message -->
              <div v-if="directorIntervention" class="intervention-card mb-4">
                <div class="flex items-center gap-2 mb-2">
                  <span class="text-lg">🎯</span>
                  <span class="font-medium text-accent-primary">Director's Guidance</span>
                </div>
                <p class="text-text-secondary text-sm">{{ directorIntervention.content }}</p>
              </div>

              <!-- Suggestions (struggles + concepts) -->
              <div v-if="suggestedLessons.length > 0" class="suggested-lessons">
                <div class="flex items-center gap-2 mb-3">
                  <span class="font-medium text-text-primary">Suggestions</span>
                  <span class="text-xs text-text-muted ml-auto">
                    {{ suggestedLessons.length }} item{{ suggestedLessons.length > 1 ? 's' : '' }}
                  </span>
                </div>

                <div class="lessons-grid">
                  <!-- Struggle items (detected issues) - shown first -->
                  <div
                    v-for="item in suggestedLessons.filter(i => i.item_type === 'struggle')"
                    :key="item.id"
                    class="struggle-card"
                  >
                    <div class="flex items-center gap-2">
                      <span class="text-lg">😤</span>
                      <span class="font-medium text-accent-warning text-sm">{{ item.name }}</span>
                    </div>
                  </div>

                  <!-- Concept items (lessons to review) -->
                  <button
                    v-for="item in suggestedLessons.filter(i => i.item_type !== 'struggle')"
                    :key="item.id"
                    class="lesson-card gamepad-focusable"
                    @click="goToLesson(item.id)"
                  >
                    <div class="flex items-center gap-2 mb-1">
                      <span class="level-badge-sm">L{{ item.level }}</span>
                      <span class="font-medium text-text-primary text-sm">{{ item.name }}</span>
                    </div>
                    <div class="flex items-center gap-3 text-xs text-text-muted">
                      <span>{{ item.category }}</span>
                      <span>~{{ Math.ceil(item.time_to_read / 60) }} min</span>
                      <span v-if="item.has_try_it" class="text-accent-success">✓ Interactive</span>
                    </div>
                    <div v-if="item.depth === 0" class="text-xs text-accent-primary mt-1">
                      ← This concept
                    </div>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- Emotional Feedback Phase -->
      <template v-else-if="gameStore.phase === 'feedback'">
        <div class="max-w-lg mx-auto py-12">
          <!-- Stage completion (not final stage) -->
          <div v-if="stageComplete && !challengeComplete" class="text-center mb-8">
            <div class="text-6xl mb-4">🏔️</div>
            <h1 class="text-3xl font-bold text-accent-secondary">Keep pushing!</h1>
            <h2 class="text-2xl font-semibold text-accent-primary mt-2">Stage {{ gameStore.currentStage }} Complete!</h2>
            <p class="text-text-secondary mt-2">{{ currentStageData?.name }}</p>
            <div v-if="gameStore.validationResult?.xp_earned" class="text-accent-primary mt-2">
              +{{ gameStore.validationResult.xp_earned }} XP
            </div>
          </div>
          <!-- Full challenge completion -->
          <div v-else class="text-center mb-8">
            <div class="text-6xl mb-4">🎉</div>
            <h1 class="text-3xl font-bold text-accent-primary">Challenge Complete!</h1>
            <p class="text-text-secondary mt-2">{{ gameStore.currentChallenge.name }}</p>
          </div>

          <EmotionalFeedback
            :question="stageComplete && !challengeComplete
              ? `How did Stage ${gameStore.currentStage}: '${currentStageData?.name}' feel?`
              : `How did '${gameStore.currentChallenge.name}' feel?`"
            :context="stageComplete && !challengeComplete
              ? `${gameStore.currentChallenge.id}_stage${gameStore.currentStage}`
              : gameStore.currentChallenge.id"
            :challenge-id="gameStore.currentChallenge.id"
            :stage="stageComplete && !challengeComplete ? gameStore.currentStage : undefined"
            @confirm="handleEmotionalConfirm"
          />
        </div>
      </template>

      <!-- Complete Phase -->
      <template v-else-if="gameStore.phase === 'complete'">
        <div class="max-w-lg mx-auto py-12 text-center">
          <div class="text-6xl mb-4">✨</div>
          <h1 class="text-3xl font-bold mb-4">Great Job!</h1>
          <p class="text-text-secondary mb-8">
            You've completed this challenge. What's next?
          </p>

          <div class="flex flex-col gap-4">
            <button class="oled-button-primary py-4 text-lg gamepad-focusable" @click="nextChallenge">
              🚀 Next Challenge
            </button>
            <button class="oled-button py-3 gamepad-focusable" @click="returnToMenu">
              🏠 Return to Menu
            </button>
          </div>
        </div>
      </template>
    </template>
  </div>
</template>

<style scoped>
.timer-display {
  @apply px-3 py-1 text-sm font-mono;
  @apply bg-oled-panel border border-oled-border rounded-lg;
  @apply text-text-secondary;
  transition: all 0.2s ease;
}

.timer-display.timer-paused {
  @apply text-text-muted opacity-60;
}

.stage-badge {
  @apply px-2 py-0.5 text-xs font-medium;
  @apply bg-accent-secondary/20 text-accent-secondary;
  @apply border border-accent-secondary/30 rounded;
}

.timer-tooltip {
  @apply absolute right-0 top-full mt-2;
  @apply border border-oled-border rounded-lg;
  @apply p-3 min-w-48 z-50;
  @apply shadow-xl;
  background: #0a0a0a;  /* Solid dark background, not transparent */
  animation: tooltipFadeIn 0.15s ease-out;
}

@keyframes tooltipFadeIn {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Hint content styling for markdown */
.hint-content :deep(p) {
  @apply m-0 text-sm;
}

.hint-content :deep(code) {
  @apply px-1.5 py-0.5 rounded text-xs font-mono;
  @apply bg-oled-panel text-accent-primary;
}

.hint-content :deep(pre) {
  @apply p-2 rounded-lg my-2 overflow-x-auto;
  @apply bg-oled-panel border border-oled-border;
}

.hint-content :deep(pre code) {
  @apply p-0 bg-transparent text-text-primary;
}

/* Hint navigation buttons */
.hint-nav-btn {
  @apply w-5 h-5 flex items-center justify-center;
  @apply text-text-muted hover:text-accent-warning;
  @apply rounded transition-colors text-sm font-medium;
}

.hint-nav-btn:not(:disabled):hover {
  @apply bg-accent-warning/10;
}

/* Director suggestion section */
.director-suggestion {
  @apply p-4 rounded-lg;
  @apply bg-oled-panel border border-oled-border;
}

.intervention-card {
  @apply p-3 rounded-lg;
  @apply bg-accent-primary/5 border border-accent-primary/20;
}

.suggested-lessons {
  @apply p-3 rounded-lg;
  background: rgba(10, 10, 10, 0.8);
}

.lessons-grid {
  @apply flex flex-col gap-2;
}

.lesson-card {
  @apply w-full text-left p-3 rounded-lg;
  @apply bg-oled-panel border border-oled-border;
  @apply transition-all duration-150;
}

.lesson-card:hover {
  @apply border-accent-primary/50;
  background: rgba(10, 10, 10, 0.9);
}

.lesson-card:focus {
  @apply outline-none ring-2 ring-accent-primary ring-offset-2;
  --tw-ring-offset-color: #000000;
}

.level-badge-sm {
  @apply px-1.5 py-0.5 text-xs font-medium;
  @apply bg-accent-secondary/20 text-accent-secondary;
  @apply border border-accent-secondary/30 rounded;
}

.struggle-card {
  @apply w-full p-3 rounded-lg;
  @apply bg-accent-warning/5 border border-accent-warning/30;
}

.struggle-badge {
  @apply text-sm;
}
</style>
