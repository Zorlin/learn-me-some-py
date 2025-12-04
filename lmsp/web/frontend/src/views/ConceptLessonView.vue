<script setup lang="ts">
/**
 * Concept Lesson View
 * ===================
 *
 * MIRRORS ChallengeView layout exactly:
 * - Left panel: Title, description, controls, hints
 * - Right panel: Code editor + test results + lesson explainer
 */

import { onMounted, onUnmounted, ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { marked } from 'marked'
import { conceptsApi, type ConceptLesson } from '@/api/client'
import { useGamepadStore } from '@/stores/gamepad'
import { useGamepadNav } from '@/composables/useGamepadNav'
import CodeEditor from '@/components/game/CodeEditor.vue'
import TestResults from '@/components/game/TestResults.vue'
import EmotionalFeedback from '@/components/input/EmotionalFeedback.vue'

// Phase: same as ChallengeView for consistency
type LessonPhase = 'coding' | 'feedback' | 'complete'

const route = useRoute()
const router = useRouter()
const gamepadStore = useGamepadStore()
const lesson = ref<ConceptLesson | null>(null)
const isLoading = ref(true)
const tryItCode = ref('')

// Progressive hints
const showHint = ref(false)
const hintLevel = ref(0)
const maxHintLevel = 3
const viewedHints = ref<string[]>([])
const hintIndex = ref(0)

// LocalStorage helpers for code persistence (same pattern as challenges)
const STORAGE_PREFIX = 'lmsp_concept_'

function getSavedCode(lessonId: string): string | null {
  try {
    return localStorage.getItem(`${STORAGE_PREFIX}${lessonId}`)
  } catch {
    return null
  }
}

function saveCode(lessonId: string, codeToSave: string) {
  try {
    localStorage.setItem(`${STORAGE_PREFIX}${lessonId}`, codeToSave)
  } catch {
    // Ignore storage errors (quota, etc.)
  }
}

function clearSavedCode(lessonId: string) {
  try {
    localStorage.removeItem(`${STORAGE_PREFIX}${lessonId}`)
  } catch {
    // Ignore
  }
}

// Test state
const isRunning = ref(false)
const phase = ref<LessonPhase>('coding')
const testResult = ref<{
  success: boolean
  passing: number
  total: number
  output: string
  error?: string
  xp_earned?: number
  xp_reason?: string
  total_xp?: number
  test_results?: Array<{
    name: string
    passed: boolean
    expected?: unknown
    actual?: unknown
    error?: string
  }>
  director_intervention?: {
    type: string
    content: string
    reason: string
    confidence: number
    suggested_lessons?: Array<{
      id: string
      name: string
      level: number
      category: string
      time_to_read: number
      has_try_it: boolean
      item_type?: string
      depth?: number
    }>
  }
  suggested_lessons?: Array<{
    id: string
    name: string
    level: number
    category: string
    time_to_read: number
    has_try_it: boolean
    item_type?: string
    depth?: number
  }>
} | null>(null)

// Director intervention and suggestions (same pattern as ChallengeView)
const suggestedLessons = computed(() => {
  if (!testResult.value) return []

  // Check Director intervention first
  if (testResult.value.director_intervention?.suggested_lessons) {
    return testResult.value.director_intervention.suggested_lessons
  }

  // Check direct suggested_lessons (from repeated failures)
  if (testResult.value.suggested_lessons) {
    return testResult.value.suggested_lessons
  }

  return []
})

const directorIntervention = computed(() => {
  return testResult.value?.director_intervention ?? null
})

// Lesson explainer collapsed state
const showExplainer = ref(true)

// Timer display - updates every second
const displayedTime = ref(0)
let timerInterval: number | null = null
let startTime: number | null = null

function updateTimerDisplay() {
  if (startTime !== null) {
    displayedTime.value = Math.floor((Date.now() - startTime) / 1000)
  }
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

useGamepadNav({ onBack: () => router.push('/concepts') })

const conceptId = computed(() => route.params.id as string)

// Check if code has been modified from starter
const codeHasChanged = computed(() => {
  if (!lesson.value?.try_it) return false
  return tryItCode.value !== lesson.value.try_it.starter
})

// Check if real hints exist (from TOML [hints] section, not auto-generated)
// TODO: Load hints from API when we add hints field to ConceptLesson
const hasRealHints = computed(() => {
  // For now, no concepts have real hints - they're all auto-generated from solution
  return false
})

// No hints available message
const showNoHintsPanel = ref(false)
const isDev = import.meta.env.DEV

function showNoHintsMessage() {
  showNoHintsPanel.value = true
}

function createHintsPlaceholder() {
  // TODO: Palace integration - automatically generate hints for this lesson
  console.log(`[Palace] Create hints for lesson: ${lesson.value?.id}`)
  alert(`Palace hint generation coming soon!\n\nLesson: ${lesson.value?.id}`)
}

// Auto-save code to localStorage when it changes
watch(tryItCode, (newCode) => {
  if (lesson.value?.id) {
    saveCode(lesson.value.id, newCode)
  }
})

// Watch for gamepad button presses
watch(() => gamepadStore.buttons, (buttons) => {
  if (!lesson.value) return

  // X button = run tests
  if (buttons.X && lesson.value.try_it) {
    runTests()
  }

  // Y button = show hint (only if there's a solution to hint from)
  if (buttons.Y && lesson.value.try_it?.solution) {
    requestHint()
  }
}, { deep: true })

onMounted(async () => {
  await loadLesson()

  // Start timer display update interval
  startTime = Date.now()
  updateTimerDisplay()
  timerInterval = window.setInterval(updateTimerDisplay, 1000)
})

onUnmounted(() => {
  // Clean up timer interval
  if (timerInterval !== null) {
    clearInterval(timerInterval)
    timerInterval = null
  }
})

async function loadLesson() {
  isLoading.value = true
  try {
    const response = await conceptsApi.get(conceptId.value)
    if (response.ok) {
      lesson.value = response.data
      if (lesson.value?.try_it) {
        // Load saved code or fall back to starter
        const saved = getSavedCode(conceptId.value)
        tryItCode.value = saved ?? lesson.value.try_it.starter
      }
      await conceptsApi.markSeen(conceptId.value)
    }
  } catch (error) {
    console.error('Failed to load lesson:', error)
  }
  isLoading.value = false
}

// Progressive hint system
function requestHint() {
  if (hintLevel.value < maxHintLevel) {
    hintLevel.value++
    const hint = generateHint(hintLevel.value)
    if (hint && !viewedHints.value.includes(hint)) {
      viewedHints.value.push(hint)
      hintIndex.value = viewedHints.value.length - 1
    }
    showHint.value = true
  }
}

function generateHint(level: number): string | null {
  if (!lesson.value?.try_it) return null

  const solution = lesson.value.try_it.solution
  const lines = solution.split('\n').filter(l => l.trim())

  switch (level) {
    case 1:
      return `Look at the examples in the lesson. What pattern do you see?`
    case 2:
      if (lines.length > 0) {
        return `Start with:\n\`\`\`python\n${lines[0]}\n\`\`\``
      }
      return `Review the code examples and apply the same pattern.`
    case 3:
      return `**Solution:**\n\`\`\`python\n${solution}\`\`\``
    default:
      return null
  }
}

const currentHint = computed(() => {
  if (viewedHints.value.length === 0) return null
  return viewedHints.value[hintIndex.value] ?? null
})

const renderedHint = computed(() => {
  if (!currentHint.value) return ''
  try {
    return marked(currentHint.value)
  } catch {
    return currentHint.value
  }
})

function prevHint() {
  if (hintIndex.value > 0) hintIndex.value--
}

function nextHint() {
  if (hintIndex.value < viewedHints.value.length - 1) hintIndex.value++
}

// Run tests (uses /api/code/submit with lesson_id, same as challenges)
async function runTests() {
  if (!lesson.value?.try_it) return

  isRunning.value = true
  testResult.value = null

  try {
    const response = await fetch('/api/code/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        lesson_id: lesson.value.id,
        code: tryItCode.value,
      }),
    })

    const data = await response.json()

    testResult.value = {
      success: data.success,
      passing: data.tests_passing,
      total: data.tests_total,
      output: data.output || '',
      error: data.error,
      xp_earned: data.xp_earned,
      xp_reason: data.xp_reason,
      total_xp: data.total_xp,
      test_results: data.test_results,
      director_intervention: data.director_intervention,
      suggested_lessons: data.suggested_lessons,
    }
  } catch (error) {
    testResult.value = {
      success: false,
      passing: 0,
      total: 1,
      output: '',
      error: String(error),
    }
  }

  isRunning.value = false
}

function resetCode() {
  if (lesson.value?.try_it) {
    // Clear saved code and restore starter
    clearSavedCode(lesson.value.id)
    tryItCode.value = lesson.value.try_it.starter
    testResult.value = null
    phase.value = 'coding'
    // Reset timer
    startTime = Date.now()
    displayedTime.value = 0
  }
}

// Phase transitions (same pattern as ChallengeView)
function proceedToFeedback() {
  if (testResult.value?.success) {
    phase.value = 'feedback'
  }
}

function handleEmotionalConfirm() {
  phase.value = 'complete'
}

function nextConcept() {
  // Navigate to next concept in the list
  // For now, just go back to concepts list
  router.push('/concepts')
}

function returnToMenu() {
  router.push('/concepts')
}

function goToRelated(id: string) {
  router.push(`/concept/${id}`)
}

function goToChallenge(id: string) {
  router.push(`/challenge/${id}`)
}

function goToLesson(lessonId: string) {
  router.push(`/concept/${lessonId}`)
}

function formatCategory(category: string): string {
  return category.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
}

function formatConceptId(id: string): string {
  return id.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
}

const renderedDescription = computed(() => {
  if (!lesson.value?.description_detailed) return ''
  try {
    return marked(lesson.value.description_detailed)
  } catch {
    return `<pre>${lesson.value.description_detailed}</pre>`
  }
})

const renderedLesson = computed(() => {
  if (!lesson.value?.lesson) return ''
  try {
    return marked(lesson.value.lesson)
  } catch {
    return `<pre>${lesson.value.lesson}</pre>`
  }
})

// Context for "Copy All for Claude Code" button (same as ChallengeView)
const conceptContext = computed(() => {
  if (!lesson.value) return undefined
  return {
    name: `Concept: ${lesson.value.name}`,
    description: lesson.value.try_it?.prompt || 'Read the lesson content and apply the concepts.',
    code: tryItCode.value,
  }
})
</script>

<template>
  <div class="max-w-6xl mx-auto px-4 py-8">
    <!-- Loading State -->
    <div v-if="isLoading" class="text-center py-12 text-text-muted">
      Loading lesson...
    </div>

    <!-- Not Found -->
    <div v-else-if="!lesson" class="text-center py-12">
      <div class="text-4xl mb-4">🤷</div>
      <div class="text-text-secondary">Concept not found</div>
      <button
        class="mt-4 px-4 py-2 bg-accent-secondary text-white rounded-lg gamepad-focusable"
        @click="router.push('/concepts')"
      >
        Back to Concepts
      </button>
    </div>

    <!-- Lesson Content -->
    <template v-else>
      <!-- Coding Phase -->
      <template v-if="phase === 'coding'">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Left Panel: Info (like ChallengeView) -->
        <div class="lg:col-span-1">
          <div class="oled-panel sticky top-20">
            <!-- Header -->
            <div class="flex items-center gap-2 mb-2">
              <div class="level-badge">Level {{ lesson.level }}</div>
              <span class="category-tag">{{ formatCategory(lesson.category) }}</span>
              <span v-if="lesson.bonus" class="bonus-badge">⭐ Bonus</span>
              <!-- Timer -->
              <div class="ml-auto timer-display">
                <span>⏱️ {{ formatTime(displayedTime) }}</span>
              </div>
            </div>
            <h1 class="text-2xl font-bold mb-2">{{ lesson.name }}</h1>

            <!-- Brief description -->
            <p class="text-text-secondary mb-4">
              {{ lesson.description_brief || 'Learn this concept and practice it.' }}
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

            <!-- Hint Panel -->
            <div v-if="showHint && currentHint" class="mt-4 p-3 bg-accent-warning/10 border border-accent-warning/30 rounded-lg">
              <div class="flex items-center justify-between mb-1">
                <div class="text-sm text-accent-warning font-medium">💡 Hint</div>
                <div v-if="viewedHints.length > 1" class="flex items-center gap-1">
                  <button
                    class="hint-nav-btn"
                    :class="{ 'opacity-30': hintIndex === 0 }"
                    :disabled="hintIndex === 0"
                    @click="prevHint"
                  >‹</button>
                  <span class="text-xs text-text-muted">{{ hintIndex + 1 }}/{{ viewedHints.length }}</span>
                  <button
                    class="hint-nav-btn"
                    :class="{ 'opacity-30': hintIndex === viewedHints.length - 1 }"
                    :disabled="hintIndex === viewedHints.length - 1"
                    @click="nextHint"
                  >›</button>
                </div>
              </div>
              <div class="prose prose-invert prose-sm hint-content" v-html="renderedHint"></div>
            </div>

            <!-- XP Earned Banner -->
            <div v-if="testResult?.success && testResult?.xp_earned" class="mt-4 p-3 bg-accent-success/10 border border-accent-success/30 rounded-lg">
              <div class="text-sm text-accent-success font-medium">🎉 All tests passing!</div>
              <div class="text-accent-primary mt-1">+{{ testResult.xp_earned }} XP</div>
            </div>

            <!-- Action Buttons -->
            <div class="flex flex-col gap-2 mt-4">
              <!-- Success: Submit Solution (same as ChallengeView) -->
              <button
                v-if="testResult?.success"
                class="oled-button-success gamepad-focusable animate-pulse"
                @click="proceedToFeedback"
              >
                ✅ Submit Solution
              </button>

              <button
                v-if="lesson.try_it"
                class="oled-button-primary gamepad-focusable"
                :disabled="isRunning"
                @click="runTests"
              >
                {{ isRunning ? '⏳ Running...' : '▶ Run Tests' }}
              </button>

              <!-- Hint button: dimmed if no real hints -->
              <button
                v-if="lesson.try_it"
                class="oled-button gamepad-focusable"
                :class="{ 'opacity-50': !hasRealHints }"
                @click="hasRealHints ? requestHint() : showNoHintsMessage()"
              >
                <span :class="{ 'grayscale': !hasRealHints }">💡</span>
                {{ !hasRealHints ? 'No hints available' : hintLevel === 0 ? 'Need a hint?' : hintLevel === 2 ? 'Show solution' : 'Another hint' }}
              </button>

              <!-- No Hints Available Panel -->
              <div v-if="showNoHintsPanel" class="mt-2 p-3 bg-oled-muted border border-oled-border rounded-lg">
                <div class="flex items-center justify-between mb-2">
                  <span class="text-sm text-text-muted">💡 No hints yet</span>
                  <button
                    class="text-text-muted hover:text-text-secondary text-sm"
                    @click="showNoHintsPanel = false"
                  >✕</button>
                </div>
                <p class="text-sm text-text-secondary mb-2">
                  This concept doesn't have handcrafted hints yet.
                  The lesson content and examples should help guide you!
                </p>
                <div v-if="isDev" class="pt-2 border-t border-oled-border">
                  <p class="text-xs text-text-muted mb-2">🔧 Dev Mode</p>
                  <button
                    class="text-xs text-accent-secondary hover:text-accent-primary"
                    @click="createHintsPlaceholder"
                  >
                    + Create hints for this lesson
                  </button>
                </div>
              </div>

              <button
                v-if="codeHasChanged"
                class="oled-button text-accent-warning gamepad-focusable"
                @click="resetCode"
              >
                🔄 Reset to Start
              </button>

              <button
                class="oled-button gamepad-focusable"
                @click="router.push('/concepts')"
              >
                ← Back to Concepts
              </button>
            </div>

            <!-- Prerequisites -->
            <div v-if="lesson.connections?.prerequisites?.length" class="mt-6 pt-4 border-t border-oled-border">
              <div class="text-xs text-text-muted mb-2">📋 Prerequisites</div>
              <div class="flex flex-wrap gap-1">
                <button
                  v-for="prereq in lesson.connections.prerequisites"
                  :key="prereq"
                  class="connection-chip prereq gamepad-focusable"
                  @click="goToRelated(prereq)"
                >
                  {{ formatConceptId(prereq) }}
                </button>
              </div>
            </div>

            <!-- Connections -->
            <div v-if="lesson.connections?.enables?.length || lesson.connections?.used_in?.length" class="mt-4">
              <div v-if="lesson.connections?.enables?.length" class="mb-3">
                <div class="text-xs text-text-muted mb-1">➡️ Unlocks</div>
                <div class="flex flex-wrap gap-1">
                  <button
                    v-for="id in lesson.connections.enables"
                    :key="id"
                    class="connection-chip enables gamepad-focusable"
                    @click="goToRelated(id)"
                  >
                    {{ formatConceptId(id) }}
                  </button>
                </div>
              </div>

              <div v-if="lesson.connections?.used_in?.length">
                <div class="text-xs text-text-muted mb-1">🎮 Used in Challenges</div>
                <div class="flex flex-wrap gap-1">
                  <button
                    v-for="id in lesson.connections.used_in"
                    :key="id"
                    class="connection-chip challenge gamepad-focusable"
                    @click="goToChallenge(id)"
                  >
                    {{ formatConceptId(id) }}
                  </button>
                </div>
              </div>
            </div>

            <!-- Detailed Description (what this concept is) -->
            <div v-if="lesson.description_detailed" class="mt-4 pt-4 border-t border-oled-border">
              <div class="text-xs text-text-muted mb-2">📖 About This Concept</div>
              <div class="lesson-content prose prose-invert text-sm" v-html="renderedDescription"></div>
            </div>
          </div>
        </div>

        <!-- Right Panel: Editor + Results + Reference -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Code Editor (if has try_it) - FIRST -->
          <div v-if="lesson.try_it">
            <CodeEditor
              :code="tryItCode"
              :readonly="isRunning"
              @update:code="tryItCode = $event"
            />

            <!-- Test Results -->
            <TestResults
              v-if="testResult"
              :results="testResult"
              :challenge="conceptContext"
              class="mt-6"
            />

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
                <p class="text-text-secondary text-sm whitespace-pre-wrap" v-html="directorIntervention.content"></p>
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

          <!-- Lesson Content -->
          <div v-if="lesson.lesson" class="oled-panel">
            <div class="lesson-content prose prose-invert" v-html="renderedLesson"></div>
          </div>

          <!-- See Also -->
          <div v-if="lesson.connections?.see_also?.length" class="oled-panel">
            <div class="text-sm text-text-muted mb-2">📚 Related Concepts</div>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="id in lesson.connections.see_also"
                :key="id"
                class="connection-chip see-also gamepad-focusable"
                @click="goToRelated(id)"
              >
                {{ formatConceptId(id) }}
              </button>
            </div>
          </div>
        </div>
      </div>
      </template>

      <!-- Emotional Feedback Phase (same as ChallengeView) -->
      <template v-else-if="phase === 'feedback'">
        <div class="max-w-lg mx-auto py-12">
          <div class="text-center mb-8">
            <div class="text-6xl mb-4">🎉</div>
            <h1 class="text-3xl font-bold text-accent-primary">Concept Mastered!</h1>
            <p class="text-text-secondary mt-2">{{ lesson.name }}</p>
            <div v-if="testResult?.xp_earned" class="text-accent-primary mt-2">
              +{{ testResult.xp_earned }} XP
            </div>
          </div>

          <EmotionalFeedback
            :question="`How did '${lesson.name}' feel?`"
            :context="`concept:${lesson.id}`"
            :challenge-id="`concept:${lesson.id}`"
            @confirm="handleEmotionalConfirm"
          />
        </div>
      </template>

      <!-- Complete Phase (same as ChallengeView) -->
      <template v-else-if="phase === 'complete'">
        <div class="max-w-lg mx-auto py-12 text-center">
          <div class="text-6xl mb-4">✨</div>
          <h1 class="text-3xl font-bold mb-4">Great Job!</h1>
          <p class="text-text-secondary mb-8">
            You've mastered this concept. What's next?
          </p>

          <div class="flex flex-col gap-4">
            <button class="oled-button-primary py-4 text-lg gamepad-focusable" @click="nextConcept">
              🚀 Next Concept
            </button>
            <button class="oled-button py-3 gamepad-focusable" @click="returnToMenu">
              🏠 Return to Concepts
            </button>
          </div>
        </div>
      </template>
    </template>
  </div>
</template>

<style scoped>
.level-badge {
  @apply px-2 py-0.5 text-xs font-bold rounded;
  @apply text-accent-primary;
  background: rgba(0, 255, 136, 0.2);
  border: 1px solid rgba(0, 255, 136, 0.3);
}

.category-tag {
  @apply text-sm text-accent-secondary font-medium;
}

.bonus-badge {
  @apply px-2 py-0.5 text-xs font-bold rounded;
  @apply text-accent-tertiary;
  background: rgba(255, 0, 255, 0.2);
  border: 1px solid rgba(255, 0, 255, 0.3);
}

.gamepad-button {
  @apply inline-flex items-center justify-center;
  @apply w-6 h-6 rounded-md text-xs font-bold;
  @apply bg-oled-panel border border-oled-border;
}

/* Hint navigation */
.hint-nav-btn {
  @apply w-5 h-5 flex items-center justify-center;
  @apply text-text-muted hover:text-accent-warning;
  @apply rounded transition-colors text-sm font-medium;
}

.hint-nav-btn:not(:disabled):hover {
  @apply bg-accent-warning/10;
}

/* Hint content */
.hint-content :deep(p) {
  @apply m-0 text-sm;
}

.hint-content :deep(code) {
  @apply px-1.5 py-0.5 rounded text-xs font-mono;
  @apply bg-oled-panel text-accent-primary;
}

.hint-content :deep(pre) {
  @apply p-3 rounded-lg my-2 overflow-x-auto;
  @apply bg-oled-panel border border-oled-border;
}

.hint-content :deep(pre code) {
  @apply p-0 bg-transparent text-text-primary;
}

/* Connection chips */
.connection-chip {
  @apply px-2 py-1 text-xs rounded-full cursor-pointer transition-all;
}

.connection-chip.prereq {
  @apply text-accent-warning;
  background: rgba(234, 179, 8, 0.1);
  border: 1px solid rgba(234, 179, 8, 0.3);
}

.connection-chip.prereq:hover {
  background: rgba(234, 179, 8, 0.2);
}

.connection-chip.enables {
  @apply text-accent-primary;
  background: rgba(0, 255, 136, 0.1);
  border: 1px solid rgba(0, 255, 136, 0.3);
}

.connection-chip.enables:hover {
  background: rgba(0, 255, 136, 0.2);
}

.connection-chip.challenge {
  @apply text-accent-secondary;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.connection-chip.challenge:hover {
  background: rgba(59, 130, 246, 0.2);
}

.connection-chip.see-also {
  @apply bg-oled-muted text-text-secondary border border-oled-border;
}

.connection-chip.see-also:hover {
  @apply border-text-muted;
}

/* Lesson content */
.lesson-content {
  @apply text-text-primary leading-relaxed;
  max-height: 50vh;
  overflow-y: auto;
}

.lesson-content :deep(pre) {
  @apply bg-oled-near border border-oled-border rounded-lg p-4 my-4;
  @apply font-mono text-sm overflow-x-auto;
}

.lesson-content :deep(code) {
  @apply bg-oled-muted px-1.5 py-0.5 rounded text-accent-primary;
  @apply font-mono text-sm;
}

.lesson-content :deep(pre code) {
  @apply bg-transparent p-0 text-text-primary;
}

.lesson-content :deep(h2) {
  @apply text-xl font-bold text-text-primary mt-6 mb-3;
}

.lesson-content :deep(h3) {
  @apply text-lg font-bold text-text-primary mt-4 mb-2;
}

.lesson-content :deep(ul), .lesson-content :deep(ol) {
  @apply ml-5 my-3;
}

.lesson-content :deep(li) {
  @apply mb-2;
}

.lesson-content :deep(p) {
  @apply mb-3;
}

.timer-display {
  @apply px-3 py-1 text-sm font-mono;
  @apply bg-oled-panel border border-oled-border rounded-lg;
  @apply text-text-secondary;
  transition: all 0.2s ease;
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
</style>
