<script setup lang="ts">
import { onMounted, ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGameStore } from '@/stores/game'
import { useGamepadStore } from '@/stores/gamepad'
import CodeEditor from '@/components/game/CodeEditor.vue'
import TestResults from '@/components/game/TestResults.vue'
import EmotionalFeedback from '@/components/input/EmotionalFeedback.vue'

const route = useRoute()
const router = useRouter()
const gameStore = useGameStore()
const gamepadStore = useGamepadStore()

const showHint = ref(false)
const currentHint = ref<string | null>(null)

onMounted(async () => {
  const challengeId = route.params.id as string
  await gameStore.loadChallenge(challengeId)
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

function runTests() {
  gameStore.submitCode()
}

function handleEmotionalConfirm(feedback: { enjoyment: number; frustration: number }) {
  gameStore.completeChallenge()
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
      <button class="oled-button mt-4" @click="router.push('/challenges')">
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
              <div class="level-badge mb-2">Level {{ gameStore.currentChallenge.level }}</div>
              <h1 class="text-2xl font-bold mb-4">{{ gameStore.currentChallenge.name }}</h1>
              <p class="text-text-secondary mb-4">
                {{ gameStore.currentChallenge.description_brief }}
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
                <!-- Submit Solution (only when tests pass) -->
                <button
                  v-if="gameStore.validationResult?.success"
                  class="oled-button-success"
                  @click="gameStore.proceedToFeedback"
                >
                  ✅ Submit Solution
                </button>

                <button
                  class="oled-button-primary"
                  :disabled="gameStore.isSubmitting"
                  @click="runTests"
                >
                  {{ gameStore.isSubmitting ? '⏳ Running...' : '▶ Run Tests' }}
                </button>
                <button class="oled-button" @click="requestHint">
                  💡 Need a hint?
                </button>
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
          <div class="text-center mb-8">
            <div class="text-6xl mb-4">🎉</div>
            <h1 class="text-3xl font-bold text-accent-primary">Challenge Complete!</h1>
            <p class="text-text-secondary mt-2">{{ gameStore.currentChallenge.name }}</p>
          </div>

          <EmotionalFeedback
            :question="`How did '${gameStore.currentChallenge.name}' feel?`"
            :context="gameStore.currentChallenge.id"
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
            <button class="oled-button-primary py-4 text-lg" @click="nextChallenge">
              🚀 Next Challenge
            </button>
            <button class="oled-button py-3" @click="returnToMenu">
              🏠 Return to Menu
            </button>
          </div>
        </div>
      </template>
    </template>
  </div>
</template>
