<script setup lang="ts">
import { onMounted, onUnmounted, ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { marked } from 'marked'
import { useGameStore } from '@/stores/game'
import { useGamepadStore } from '@/stores/gamepad'
import { useGamepadNav } from '@/composables/useGamepadNav'
import CodeEditor from '@/components/game/CodeEditor.vue'
import TestResults from '@/components/game/TestResults.vue'
import EmotionalFeedback from '@/components/input/EmotionalFeedback.vue'

const route = useRoute()
const router = useRouter()
const gameStore = useGameStore()
const gamepadStore = useGamepadStore()

// Timer display - updates every second
const displayedTime = ref(0)
let timerInterval: number | null = null

function updateTimerDisplay() {
  displayedTime.value = gameStore.getElapsedSeconds()
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
const currentHint = ref<string | null>(null)
const isViewingPreviousSolution = ref(false)

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
  currentHint.value = gameStore.useHint()
  showHint.value = true
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
    error: gameStore.validationResult.error,
  }
})

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
                <div class="ml-auto timer-display" :class="{ 'timer-paused': gameStore.timerPaused }">
                  ⏱️ {{ formatTime(displayedTime) }}
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

              <!-- Gamepad Controls -->
              <div v-if="gamepadStore.connected" class="border-t border-oled-border pt-4 mt-4">
                <div class="text-sm text-text-muted mb-2">Controls</div>
                <div class="grid grid-cols-2 gap-2 text-sm">
                  <div><span class="gamepad-button">X</span> Run Tests</div>
                  <div><span class="gamepad-button">Y</span> Hint</div>
                  <div><span class="gamepad-button">B</span> Back</div>
                </div>
              </div>

              <!-- Hint -->
              <div v-if="showHint && currentHint" class="mt-4 p-3 bg-accent-warning/10 border border-accent-warning/30 rounded-lg">
                <div class="text-sm text-accent-warning font-medium mb-1">💡 Hint</div>
                <div class="text-sm">{{ currentHint }}</div>
              </div>

              <!-- Action Buttons -->
              <div class="flex flex-col gap-2 mt-4">
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
            <CodeEditor
              :code="gameStore.code"
              :readonly="gameStore.phase === 'testing'"
              @update:code="gameStore.updateCode"
            />

            <!-- Test Results -->
            <TestResults
              v-if="testResultsForDisplay"
              :results="testResultsForDisplay"
              :challenge="challengeContext"
              class="mt-6"
            />
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
</style>
