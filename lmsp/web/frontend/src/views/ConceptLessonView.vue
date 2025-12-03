<script setup lang="ts">
/**
 * Concept Lesson View
 * ===================
 *
 * MIRRORS ChallengeView layout exactly:
 * - Left panel: Title, description, controls, hints
 * - Right panel: Code editor + test results + lesson explainer
 */

import { onMounted, ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { marked } from 'marked'
import { conceptsApi, type ConceptLesson } from '@/api/client'
import { useGamepadStore } from '@/stores/gamepad'
import { useGamepadNav } from '@/composables/useGamepadNav'
import CodeEditor from '@/components/game/CodeEditor.vue'
import TestResults from '@/components/game/TestResults.vue'

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

// Test state
const isRunning = ref(false)
const testResult = ref<{
  success: boolean
  passing: number
  total: number
  output: string
  error?: string
} | null>(null)

// Lesson explainer collapsed state
const showExplainer = ref(true)

useGamepadNav({ onBack: () => router.push('/concepts') })

const conceptId = computed(() => route.params.id as string)

// Check if code has been modified from starter
const codeHasChanged = computed(() => {
  if (!lesson.value?.try_it) return false
  return tryItCode.value !== lesson.value.try_it.starter
})

// Watch for gamepad button presses
watch(() => gamepadStore.buttons, (buttons) => {
  if (!lesson.value) return

  // X button = run tests
  if (buttons.X && lesson.value.try_it) {
    runTests()
  }

  // Y button = show hint
  if (buttons.Y && lesson.value.try_it) {
    requestHint()
  }
}, { deep: true })

onMounted(async () => {
  await loadLesson()
})

async function loadLesson() {
  isLoading.value = true
  try {
    const response = await conceptsApi.get(conceptId.value)
    if (response.ok) {
      lesson.value = response.data
      if (lesson.value?.try_it) {
        tryItCode.value = lesson.value.try_it.starter
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

// Run tests (validates against solution pattern)
async function runTests() {
  if (!lesson.value?.try_it) return

  isRunning.value = true
  testResult.value = null

  try {
    const response = await fetch('/api/code/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        code: tryItCode.value,
        concept_id: lesson.value.id,
      }),
    })

    const data = await response.json()

    // Simple validation: code ran without errors
    const hasError = !!data.error
    testResult.value = {
      success: !hasError,
      passing: hasError ? 0 : 1,
      total: 1,
      output: data.output || '',
      error: data.error,
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
    tryItCode.value = lesson.value.try_it.starter
    testResult.value = null
  }
}

function markComplete() {
  conceptsApi.markUnderstood(conceptId.value)
  router.push('/concepts')
}

function goToRelated(id: string) {
  router.push(`/concept/${id}`)
}

function goToChallenge(id: string) {
  router.push(`/challenge/${id}`)
}

function formatCategory(category: string): string {
  return category.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
}

function formatConceptId(id: string): string {
  return id.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
}

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
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Left Panel: Info (like ChallengeView) -->
        <div class="lg:col-span-1">
          <div class="oled-panel sticky top-20">
            <!-- Header -->
            <div class="flex items-center gap-2 mb-2">
              <div class="level-badge">Level {{ lesson.level }}</div>
              <span class="category-tag">{{ formatCategory(lesson.category) }}</span>
              <span v-if="lesson.bonus" class="bonus-badge">⭐ Bonus</span>
            </div>
            <h1 class="text-2xl font-bold mb-2">{{ lesson.name }}</h1>

            <!-- Brief description / prompt -->
            <p v-if="lesson.try_it" class="text-text-secondary mb-4">
              {{ lesson.try_it.prompt }}
            </p>
            <p v-else class="text-text-secondary mb-4">
              Read through the lesson content and examples.
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

            <!-- Action Buttons -->
            <div class="flex flex-col gap-2 mt-4">
              <!-- Success: Mark Complete -->
              <button
                v-if="testResult?.success"
                class="oled-button-success gamepad-focusable animate-pulse"
                @click="markComplete"
              >
                ✅ Complete Lesson
              </button>

              <button
                v-if="lesson.try_it"
                class="oled-button-primary gamepad-focusable"
                :disabled="isRunning"
                @click="runTests"
              >
                {{ isRunning ? '⏳ Running...' : '▶ Run Tests' }}
              </button>

              <button
                v-if="lesson.try_it && hintLevel < maxHintLevel"
                class="oled-button gamepad-focusable"
                @click="requestHint"
              >
                💡 {{ hintLevel === 0 ? 'Need a hint?' : hintLevel === 2 ? 'Show solution' : 'Another hint' }}
              </button>

              <button
                v-if="codeHasChanged"
                class="oled-button text-accent-warning gamepad-focusable"
                @click="resetCode"
              >
                🔄 Reset Code
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
          </div>
        </div>

        <!-- Right Panel: Editor + Results + Lesson -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Code Editor (if has try_it) -->
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
          </div>

          <!-- No code exercise -->
          <div v-else class="oled-panel text-center py-8">
            <div class="text-4xl mb-4">📖</div>
            <div class="text-text-secondary">This is a reading lesson</div>
            <div class="text-text-muted text-sm mt-2">
              Study the content below, then continue to the next concept.
            </div>
          </div>

          <!-- Lesson Explainer (collapsible) -->
          <div class="oled-panel">
            <button
              class="w-full flex items-center justify-between text-left"
              @click="showExplainer = !showExplainer"
            >
              <div class="flex items-center gap-2">
                <span class="text-lg">📚</span>
                <span class="font-medium">Lesson Content</span>
                <span class="text-xs text-text-muted">({{ lesson.time_to_read }}s read)</span>
              </div>
              <span class="text-text-muted">{{ showExplainer ? '▼' : '▶' }}</span>
            </button>

            <div v-if="showExplainer" class="mt-4 pt-4 border-t border-oled-border">
              <div class="lesson-content prose prose-invert" v-html="renderedLesson"></div>
            </div>
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
  @apply text-xl font-bold text-accent-primary mt-6 mb-3;
}

.lesson-content :deep(h3) {
  @apply text-lg font-bold text-accent-secondary mt-4 mb-2;
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
</style>
