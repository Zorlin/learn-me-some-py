<script setup lang="ts">
import { ref, onMounted, computed, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useGamepadStore } from '@/stores/gamepad'
import { useGamepadNav } from '@/composables/useGamepadNav'
import { usePlayerStore } from '@/stores/player'
import { api } from '@/api/client'
import SecuritySettings from '@/components/settings/SecuritySettings.vue'

const router = useRouter()
const gamepadStore = useGamepadStore()
const playerStore = usePlayerStore()

// Enable gamepad navigation
useGamepadNav({ onBack: () => router.push('/') })

// Active tab
type TabId = 'profile' | 'input' | 'security' | 'difficulty' | 'ai'
const activeTab = ref<TabId>('profile')

const tabs = [
  { id: 'profile' as const, label: 'Profile', icon: '👤' },
  { id: 'input' as const, label: 'Input', icon: '🎮' },
  { id: 'security' as const, label: 'Security', icon: '🔒' },
  { id: 'difficulty' as const, label: 'Difficulty', icon: '⚡' },
  { id: 'ai' as const, label: 'The Director', icon: '🧠' },
]

// Persist active tab to localStorage
watch(activeTab, (newTab) => {
  localStorage.setItem('lmsp_settings_tab', newTab)
})

// Director state
interface DirectorStruggle {
  type: string
  description: string
  frequency: number
  first_seen: string
  last_seen: string
}

interface MasteryEntry {
  concept: string
  score: number
  streak?: number
  failures?: number
}

interface ShadowAdjustments {
  difficulty_bias: number
  avoid_concepts: string[]
  prefer_concepts: string[]
  micro_challenge_candidates: string[]
  reason: string
}

interface DifficultySuggestion {
  direction: 'easier' | 'harder'
  reason: string
  confidence: number
  suggested_difficulty: string
  suggested_hints: string
}

interface DirectorState {
  player_id: string
  frustration_level: number
  momentum: number
  observation_count: number
  active_struggles: number
  should_intervene: boolean
  struggles: DirectorStruggle[]
  // New mastery-based insights
  learning_velocity: number
  total_successes: number
  total_failures: number
  first_try_rate: number
  mastered_concepts: MasteryEntry[]
  struggling_concepts: MasteryEntry[]
  concepts_tracked: number
  shadow_adjustments?: ShadowAdjustments
  difficulty_suggestion?: DifficultySuggestion
}

const directorState = ref<DirectorState | null>(null)
const directorLoading = ref(false)
const directorError = ref<string | null>(null)
let directorPollInterval: ReturnType<typeof setInterval> | null = null

async function fetchDirectorState() {
  directorLoading.value = true
  directorError.value = null
  try {
    const response = await api.get<DirectorState>('/director/state')
    directorState.value = response.data
  } catch (e) {
    directorError.value = e instanceof Error ? e.message : 'Unknown error'
  } finally {
    directorLoading.value = false
  }
}

// Format struggle type for display
function formatStruggleType(type: string): string {
  const labels: Record<string, string> = {
    syntax_error: 'Syntax Error',
    type_error: 'Type Error',
    logic_error: 'Logic Error',
    concept_gap: 'Concept Gap',
    pattern: 'Unfamiliar Pattern',
    tooling: 'Tooling Confusion',
    frustration: 'Frustration Spiral',
  }
  return labels[type] || type
}

// Get color class for struggle type
function struggleColor(type: string): string {
  const colors: Record<string, string> = {
    syntax_error: 'text-red-400',
    type_error: 'text-orange-400',
    logic_error: 'text-yellow-400',
    concept_gap: 'text-blue-400',
    pattern: 'text-purple-400',
    tooling: 'text-gray-400',
    frustration: 'text-pink-400',
  }
  return colors[type] || 'text-text-secondary'
}

// Time ago helper
function timeAgo(isoString: string): string {
  const date = new Date(isoString)
  const now = new Date()
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000)

  if (seconds < 60) return 'just now'
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`
  return `${Math.floor(seconds / 86400)}d ago`
}

// Profile settings
const playerName = ref('')
const nameSaved = ref(false)

// Input settings
const inputMode = ref<'keyboard' | 'gamepad' | 'auto'>('auto')

// Theme settings
const theme = ref<'dark' | 'oled'>('oled')

// Difficulty settings
const difficulty = ref<'easy' | 'normal' | 'hard'>('normal')
const hintLevel = ref<'full' | 'partial' | 'none'>('partial')
const autoAdvance = ref(true)

// Auto-suggestion settings
const autoSuggestionsEnabled = ref(true)
const suggestionDismissedAt = ref<string | null>(null)  // ISO timestamp when dismissed

// Check if we should show a difficulty suggestion
const shouldShowSuggestion = computed(() => {
  if (!autoSuggestionsEnabled.value) return false
  if (!directorState.value?.difficulty_suggestion) return false

  // If dismissed recently (within 30 minutes), don't show
  if (suggestionDismissedAt.value) {
    const dismissedTime = new Date(suggestionDismissedAt.value).getTime()
    const now = Date.now()
    const thirtyMinutes = 30 * 60 * 1000
    if (now - dismissedTime < thirtyMinutes) return false
  }

  return true
})

function dismissSuggestion(permanent: boolean = false) {
  if (permanent) {
    autoSuggestionsEnabled.value = false
    localStorage.setItem('lmsp_auto_suggestions', 'false')
  } else {
    suggestionDismissedAt.value = new Date().toISOString()
    localStorage.setItem('lmsp_suggestion_dismissed_at', suggestionDismissedAt.value)
  }
}

function applySuggestion() {
  const suggestion = directorState.value?.difficulty_suggestion
  if (!suggestion) return

  // Apply suggested settings
  saveDifficulty(suggestion.suggested_difficulty)
  saveHintLevel(suggestion.suggested_hints)

  // Clear the dismissed state so we can show future suggestions
  suggestionDismissedAt.value = null
  localStorage.removeItem('lmsp_suggestion_dismissed_at')
}

function toggleAutoSuggestions() {
  autoSuggestionsEnabled.value = !autoSuggestionsEnabled.value
  localStorage.setItem('lmsp_auto_suggestions', String(autoSuggestionsEnabled.value))

  // Clear dismissed state when re-enabling
  if (autoSuggestionsEnabled.value) {
    suggestionDismissedAt.value = null
    localStorage.removeItem('lmsp_suggestion_dismissed_at')
  }
}

onMounted(() => {
  // Restore active tab
  const savedTab = localStorage.getItem('lmsp_settings_tab')
  if (savedTab && tabs.some(t => t.id === savedTab)) {
    activeTab.value = savedTab as TabId
  }

  const savedDifficulty = localStorage.getItem('lmsp_difficulty')
  if (savedDifficulty) difficulty.value = savedDifficulty as any

  const savedHints = localStorage.getItem('lmsp_hint_level')
  if (savedHints) hintLevel.value = savedHints as any

  const savedAutoAdvance = localStorage.getItem('lmsp_auto_advance')
  if (savedAutoAdvance !== null) autoAdvance.value = savedAutoAdvance === 'true'

  // Load auto-suggestion settings
  const savedAutoSuggestions = localStorage.getItem('lmsp_auto_suggestions')
  if (savedAutoSuggestions !== null) autoSuggestionsEnabled.value = savedAutoSuggestions === 'true'

  const savedDismissedAt = localStorage.getItem('lmsp_suggestion_dismissed_at')
  if (savedDismissedAt) suggestionDismissedAt.value = savedDismissedAt

  // Load profile first to get display name and player ID, then fetch Director state
  playerStore.loadProfile().then(() => {
    // Load display name from backend
    if (playerStore.profile?.display_name) {
      playerName.value = playerStore.profile.display_name
    }
    fetchDirectorState()
  })

  // Poll Director state every 5 seconds when on AI tab or difficulty tab
  directorPollInterval = setInterval(() => {
    if (activeTab.value === 'ai' || activeTab.value === 'difficulty') {
      fetchDirectorState()
    }
  }, 5000)
})

onUnmounted(() => {
  if (directorPollInterval) {
    clearInterval(directorPollInterval)
  }
})

async function saveName() {
  const trimmedName = playerName.value.trim()
  if (!trimmedName) return

  const success = await playerStore.setDisplayName(trimmedName)
  if (success) {
    nameSaved.value = true
    setTimeout(() => { nameSaved.value = false }, 2000)
  }
}

function saveDifficulty(value: 'easy' | 'normal' | 'hard') {
  difficulty.value = value
  localStorage.setItem('lmsp_difficulty', value)
}

function saveHintLevel(value: 'full' | 'partial' | 'none') {
  hintLevel.value = value
  localStorage.setItem('lmsp_hint_level', value)
}

function saveAutoAdvance(value: boolean) {
  autoAdvance.value = value
  localStorage.setItem('lmsp_auto_advance', String(value))
}

async function practiceConcept(concept: string) {
  // Find a challenge that teaches this concept and navigate to it
  try {
    const response = await api.get<{ found: boolean; challenge_id?: string }>(`/director/practice-challenge?concept=${encodeURIComponent(concept)}`)
    const data = response.data

    if (data.found && data.challenge_id) {
      router.push(`/challenge/${data.challenge_id}`)
    } else {
      // No specific challenge found, go to challenges list
      // The concept might be a challenge_id itself
      router.push(`/challenge/${concept}`)
    }
  } catch (e) {
    // Fallback: try navigating directly to the concept as a challenge
    router.push(`/challenge/${concept}`)
  }
}
</script>

<template>
  <div class="h-full flex flex-col lg:flex-row">
    <!-- Vertical Tabs (left side on large screens, top on small) -->
    <nav class="settings-nav shrink-0 border-b lg:border-b-0 lg:border-r border-oled-border bg-oled-panel/30">
      <!-- Mobile: horizontal scroll -->
      <div class="flex lg:flex-col overflow-x-auto lg:overflow-visible p-2 lg:p-4 gap-1 lg:gap-2 lg:w-56">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          class="settings-tab gamepad-focusable whitespace-nowrap"
          :class="{ active: activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          <span class="text-lg lg:text-xl">{{ tab.icon }}</span>
          <span class="hidden sm:inline lg:inline">{{ tab.label }}</span>
        </button>
      </div>
    </nav>

    <!-- Content Area -->
    <main class="flex-1 overflow-y-auto p-4 lg:p-8">
      <div class="max-w-4xl mx-auto">

        <!-- Profile Tab -->
        <section v-if="activeTab === 'profile'" class="settings-section">
          <h1 class="text-2xl lg:text-3xl font-bold mb-6">
            <span class="text-accent-primary">👤</span> Profile
          </h1>

          <div class="oled-panel mb-6">
            <h2 class="text-lg font-semibold mb-4">Player Identity</h2>

            <div class="space-y-4">
              <div>
                <label for="player-name" class="text-sm text-text-secondary block mb-2">
                  Display Name
                </label>
                <div class="flex items-center gap-3">
                  <input
                    id="player-name"
                    v-model="playerName"
                    type="text"
                    placeholder="Enter your name..."
                    class="flex-1 max-w-xs px-4 py-2 bg-oled-black border border-oled-border rounded-lg text-text-primary placeholder-text-muted focus:border-accent-primary focus:outline-none"
                    @blur="saveName"
                    @keyup.enter="($event.target as HTMLInputElement).blur()"
                  />
                  <span v-if="nameSaved" class="text-accent-success text-sm animate-pulse">Saved ✓</span>
                </div>
                <p class="text-xs text-text-muted mt-2">Used for achievements and leaderboards</p>
              </div>
            </div>
          </div>

          <div class="oled-panel">
            <h2 class="text-lg font-semibold mb-4">Theme</h2>

            <div class="grid grid-cols-2 gap-3">
              <button
                class="oled-button py-6 gamepad-focusable text-center"
                :class="{ 'border-accent-primary text-accent-primary': theme === 'oled' }"
                @click="theme = 'oled'"
              >
                <div class="text-3xl mb-2">🌑</div>
                <div class="font-medium">OLED Black</div>
                <div class="text-xs text-text-muted mt-1">Pure black (#000)</div>
              </button>
              <button
                class="oled-button py-6 gamepad-focusable text-center"
                :class="{ 'border-accent-primary text-accent-primary': theme === 'dark' }"
                @click="theme = 'dark'"
              >
                <div class="text-3xl mb-2">🌙</div>
                <div class="font-medium">Dark</div>
                <div class="text-xs text-text-muted mt-1">Soft dark theme</div>
              </button>
            </div>
          </div>
        </section>

        <!-- Input Tab -->
        <section v-if="activeTab === 'input'" class="settings-section">
          <h1 class="text-2xl lg:text-3xl font-bold mb-6">
            <span class="text-accent-primary">🎮</span> Input
          </h1>

          <div class="oled-panel mb-6">
            <h2 class="text-lg font-semibold mb-4">Input Mode</h2>

            <div class="grid grid-cols-3 gap-2">
              <button
                class="oled-button py-3 gamepad-focusable"
                :class="{ 'border-accent-primary text-accent-primary': inputMode === 'keyboard' }"
                @click="inputMode = 'keyboard'"
              >
                ⌨️ Keyboard
              </button>
              <button
                class="oled-button py-3 gamepad-focusable"
                :class="{ 'border-accent-primary text-accent-primary': inputMode === 'gamepad' }"
                @click="inputMode = 'gamepad'"
              >
                🎮 Gamepad
              </button>
              <button
                class="oled-button py-3 gamepad-focusable"
                :class="{ 'border-accent-primary text-accent-primary': inputMode === 'auto' }"
                @click="inputMode = 'auto'"
              >
                ✨ Auto
              </button>
            </div>
          </div>

          <!-- Gamepad Status -->
          <div v-if="gamepadStore.connected" class="oled-panel">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-semibold">Gamepad Connected</h2>
              <span class="px-2 py-1 text-xs bg-accent-success/20 text-accent-success rounded-full">
                {{ gamepadStore.profileName }}
              </span>
            </div>

            <p class="text-sm text-text-muted mb-4 font-mono truncate" :title="gamepadStore.controllerName">
              {{ gamepadStore.controllerName }}
            </p>

            <!-- Triggers -->
            <div class="grid grid-cols-2 gap-6 mb-6">
              <div>
                <div class="flex justify-between text-sm text-text-muted mb-2">
                  <span>LT (Frustration)</span>
                  <span class="font-mono">{{ Math.round(gamepadStore.leftTrigger * 100) }}%</span>
                </div>
                <div class="trigger-bar h-3">
                  <div
                    class="trigger-fill-negative h-full"
                    :style="{ width: `${gamepadStore.leftTrigger * 100}%` }"
                  />
                </div>
              </div>
              <div>
                <div class="flex justify-between text-sm text-text-muted mb-2">
                  <span>RT (Satisfaction)</span>
                  <span class="font-mono">{{ Math.round(gamepadStore.rightTrigger * 100) }}%</span>
                </div>
                <div class="trigger-bar h-3">
                  <div
                    class="trigger-fill-positive h-full"
                    :style="{ width: `${gamepadStore.rightTrigger * 100}%` }"
                  />
                </div>
              </div>
            </div>

            <!-- Sticks -->
            <div class="grid grid-cols-2 gap-6 mb-6">
              <div class="text-center">
                <div class="text-sm text-text-muted mb-2">Left Stick</div>
                <div class="relative w-24 h-24 mx-auto bg-oled-black rounded-full border border-oled-border">
                  <div class="absolute top-1/2 left-0 right-0 h-px bg-oled-border/50"></div>
                  <div class="absolute left-1/2 top-0 bottom-0 w-px bg-oled-border/50"></div>
                  <div
                    class="absolute w-5 h-5 bg-accent-primary rounded-full -translate-x-1/2 -translate-y-1/2 shadow-lg transition-all duration-75"
                    :style="{
                      left: `${50 + gamepadStore.leftStick.x * 40}%`,
                      top: `${50 + gamepadStore.leftStick.y * 40}%`
                    }"
                  />
                </div>
                <div class="text-xs text-text-muted mt-2 font-mono">
                  {{ gamepadStore.leftStick.x.toFixed(2) }}, {{ gamepadStore.leftStick.y.toFixed(2) }}
                </div>
              </div>
              <div class="text-center">
                <div class="text-sm text-text-muted mb-2">Right Stick</div>
                <div class="relative w-24 h-24 mx-auto bg-oled-black rounded-full border border-oled-border">
                  <div class="absolute top-1/2 left-0 right-0 h-px bg-oled-border/50"></div>
                  <div class="absolute left-1/2 top-0 bottom-0 w-px bg-oled-border/50"></div>
                  <div
                    class="absolute w-5 h-5 bg-accent-secondary rounded-full -translate-x-1/2 -translate-y-1/2 shadow-lg transition-all duration-75"
                    :style="{
                      left: `${50 + gamepadStore.rightStick.x * 40}%`,
                      top: `${50 + gamepadStore.rightStick.y * 40}%`
                    }"
                  />
                </div>
                <div class="text-xs text-text-muted mt-2 font-mono">
                  {{ gamepadStore.rightStick.x.toFixed(2) }}, {{ gamepadStore.rightStick.y.toFixed(2) }}
                </div>
              </div>
            </div>

            <!-- Buttons -->
            <div>
              <div class="text-sm text-text-muted mb-2">Buttons</div>
              <div class="flex flex-wrap gap-1">
                <span
                  v-for="(pressed, name) in gamepadStore.buttons"
                  :key="name"
                  class="px-2 py-1 text-xs rounded font-mono transition-colors"
                  :class="pressed ? 'bg-accent-primary text-oled-black' : 'bg-oled-black text-text-muted'"
                >
                  {{ name }}
                </span>
              </div>
            </div>
          </div>

          <div v-else class="oled-panel">
            <div class="text-center py-8 text-text-muted">
              <div class="text-4xl mb-3">🎮</div>
              <p>No gamepad connected</p>
              <p class="text-sm mt-2">Connect a controller and press any button</p>
            </div>
          </div>
        </section>

        <!-- Security Tab -->
        <section v-if="activeTab === 'security'" class="settings-section">
          <h1 class="text-2xl lg:text-3xl font-bold mb-6">
            <span class="text-accent-primary">🔒</span> Security
          </h1>

          <div class="oled-panel">
            <SecuritySettings />
          </div>
        </section>

        <!-- Difficulty Tab -->
        <section v-if="activeTab === 'difficulty'" class="settings-section">
          <h1 class="text-2xl lg:text-3xl font-bold mb-6">
            <span class="text-accent-primary">⚡</span> Difficulty & Progression
          </h1>

          <!-- AI Suggestion Prompt -->
          <div
            v-if="shouldShowSuggestion && directorState?.difficulty_suggestion"
            class="oled-panel mb-6 border-accent-primary/50"
          >
            <div class="flex items-start gap-4">
              <div class="text-3xl">
                {{ directorState.difficulty_suggestion.direction === 'harder' ? '🚀' : '💚' }}
              </div>
              <div class="flex-1">
                <div class="font-semibold text-accent-primary mb-1">
                  {{ directorState.difficulty_suggestion.direction === 'harder'
                    ? 'Ready for a Challenge?'
                    : 'The Director Has a Suggestion' }}
                </div>
                <p class="text-text-secondary text-sm mb-3">
                  {{ directorState.difficulty_suggestion.reason }}
                </p>
                <div class="flex flex-wrap gap-2">
                  <button
                    class="oled-button px-4 py-2 border-accent-primary text-accent-primary gamepad-focusable"
                    @click="applySuggestion"
                  >
                    {{ directorState.difficulty_suggestion.direction === 'harder'
                      ? 'Bring It On!'
                      : 'Sounds Good' }}
                  </button>
                  <button
                    class="oled-button px-4 py-2 gamepad-focusable"
                    @click="dismissSuggestion(false)"
                  >
                    Not Now
                  </button>
                  <button
                    class="text-xs text-text-muted hover:text-text-secondary px-2"
                    @click="dismissSuggestion(true)"
                    title="Stop showing suggestions"
                  >
                    Don't ask again
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div class="oled-panel mb-6">
            <h2 class="text-lg font-semibold mb-4">Difficulty Level</h2>

            <div class="grid grid-cols-3 gap-3">
              <button
                class="oled-button py-4 gamepad-focusable text-center"
                :class="{ 'border-accent-success text-accent-success': difficulty === 'easy' }"
                @click="saveDifficulty('easy')"
              >
                <div class="text-2xl mb-1">🌱</div>
                <div class="font-medium">Easy</div>
                <div class="text-xs text-text-muted mt-1">More hints, slower pace</div>
              </button>
              <button
                class="oled-button py-4 gamepad-focusable text-center"
                :class="{ 'border-accent-primary text-accent-primary': difficulty === 'normal' }"
                @click="saveDifficulty('normal')"
              >
                <div class="text-2xl mb-1">⚖️</div>
                <div class="font-medium">Normal</div>
                <div class="text-xs text-text-muted mt-1">Balanced experience</div>
              </button>
              <button
                class="oled-button py-4 gamepad-focusable text-center"
                :class="{ 'border-accent-warning text-accent-warning': difficulty === 'hard' }"
                @click="saveDifficulty('hard')"
              >
                <div class="text-2xl mb-1">🔥</div>
                <div class="font-medium">Hard</div>
                <div class="text-xs text-text-muted mt-1">Minimal hints, faster</div>
              </button>
            </div>
          </div>

          <div class="oled-panel mb-6">
            <h2 class="text-lg font-semibold mb-4">Hint Level</h2>

            <div class="grid grid-cols-3 gap-3">
              <button
                class="oled-button py-3 gamepad-focusable"
                :class="{ 'border-accent-primary text-accent-primary': hintLevel === 'full' }"
                @click="saveHintLevel('full')"
              >
                <div class="font-medium">Full Hints</div>
                <div class="text-xs text-text-muted mt-1">Complete guidance</div>
              </button>
              <button
                class="oled-button py-3 gamepad-focusable"
                :class="{ 'border-accent-primary text-accent-primary': hintLevel === 'partial' }"
                @click="saveHintLevel('partial')"
              >
                <div class="font-medium">Partial</div>
                <div class="text-xs text-text-muted mt-1">Nudges only</div>
              </button>
              <button
                class="oled-button py-3 gamepad-focusable"
                :class="{ 'border-accent-primary text-accent-primary': hintLevel === 'none' }"
                @click="saveHintLevel('none')"
              >
                <div class="font-medium">No Hints</div>
                <div class="text-xs text-text-muted mt-1">Figure it out</div>
              </button>
            </div>
          </div>

          <div class="oled-panel mb-6">
            <h2 class="text-lg font-semibold mb-4">Progression</h2>

            <label class="flex items-center justify-between p-3 rounded-lg hover:bg-oled-panel/50 cursor-pointer">
              <div>
                <div class="font-medium">Auto-advance on completion</div>
                <div class="text-sm text-text-muted">Automatically move to next challenge</div>
              </div>
              <button
                class="w-12 h-7 rounded-full transition-colors relative gamepad-focusable"
                :class="autoAdvance ? 'bg-accent-primary' : 'bg-oled-border'"
                @click="saveAutoAdvance(!autoAdvance)"
              >
                <div
                  class="absolute top-1 w-5 h-5 bg-white rounded-full transition-transform"
                  :class="autoAdvance ? 'translate-x-6' : 'translate-x-1'"
                />
              </button>
            </label>
          </div>

          <!-- AI Difficulty Suggestions -->
          <div class="oled-panel">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-semibold">AI Difficulty Suggestions</h2>
              <button
                class="p-2 rounded-lg hover:bg-oled-panel/50 transition-colors gamepad-focusable"
                :class="autoSuggestionsEnabled ? 'text-accent-primary' : 'text-text-muted'"
                @click="toggleAutoSuggestions"
                :title="autoSuggestionsEnabled ? 'Click to disable suggestions' : 'Click to enable suggestions'"
              >
                <span class="text-xl">{{ autoSuggestionsEnabled ? '🔓' : '🔒' }}</span>
              </button>
            </div>

            <div
              class="p-3 rounded-lg"
              :class="autoSuggestionsEnabled ? 'bg-accent-primary/5 border border-accent-primary/20' : 'bg-oled-black border border-oled-border'"
            >
              <div class="flex items-start gap-3">
                <span class="text-lg">{{ autoSuggestionsEnabled ? '🧠' : '🤫' }}</span>
                <div class="text-sm">
                  <div class="font-medium mb-1" :class="autoSuggestionsEnabled ? 'text-accent-primary' : 'text-text-muted'">
                    {{ autoSuggestionsEnabled ? 'Suggestions Enabled' : 'Suggestions Disabled' }}
                  </div>
                  <p class="text-text-secondary">
                    <template v-if="autoSuggestionsEnabled">
                      The Director will gently suggest difficulty changes based on your performance.
                      You're always in control - suggestions are just that, suggestions.
                    </template>
                    <template v-else>
                      The Director won't prompt you about difficulty changes.
                      It will still silently optimize challenge recommendations for your skill level.
                    </template>
                  </p>
                </div>
              </div>
            </div>

            <p class="text-xs text-text-muted mt-3">
              Note: Even with suggestions disabled, The Director still works behind the scenes to give you
              the best experience - it just won't ask to change your settings.
            </p>
          </div>
        </section>

        <!-- The Director (AI) Tab -->
        <section v-if="activeTab === 'ai'" class="settings-section">
          <h1 class="text-2xl lg:text-3xl font-bold mb-2">
            <span class="text-accent-primary">🧠</span> The Director
          </h1>
          <p class="text-text-muted mb-6">
            The Director is an AI system that watches your learning journey and helps when you're stuck.
            This is YOUR data - we believe in full transparency.
          </p>

          <!-- Loading state -->
          <div v-if="directorLoading && !directorState" class="oled-panel text-center py-8">
            <div class="animate-pulse text-4xl mb-3">🧠</div>
            <p class="text-text-muted">Loading Director state...</p>
          </div>

          <!-- Error state -->
          <div v-else-if="directorError" class="oled-panel border-red-500/30">
            <div class="text-center py-8 text-red-400">
              <div class="text-4xl mb-3">⚠️</div>
              <p>{{ directorError }}</p>
              <button class="oled-button mt-4" @click="fetchDirectorState">Retry</button>
            </div>
          </div>

          <!-- Director State -->
          <template v-else-if="directorState">
            <!-- Status Overview -->
            <div class="oled-panel mb-6">
              <div class="flex items-center justify-between mb-4">
                <h2 class="text-lg font-semibold">Current Status</h2>
                <span
                  class="px-3 py-1 text-sm rounded-full"
                  :class="directorState.should_intervene
                    ? 'bg-accent-warning/20 text-accent-warning'
                    : 'bg-accent-success/20 text-accent-success'"
                >
                  {{ directorState.should_intervene ? 'Wants to Help' : 'Observing' }}
                </span>
              </div>

              <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <!-- Momentum -->
                <div class="bg-oled-black rounded-lg p-4 border border-oled-border">
                  <div class="text-sm text-text-muted mb-2">Momentum</div>
                  <div class="text-2xl font-bold text-accent-primary">
                    {{ Math.round(directorState.momentum * 100) }}%
                  </div>
                  <div class="mt-2 h-2 bg-oled-border rounded-full overflow-hidden">
                    <div
                      class="h-full bg-accent-primary transition-all"
                      :style="{ width: `${directorState.momentum * 100}%` }"
                    />
                  </div>
                </div>

                <!-- Frustration -->
                <div class="bg-oled-black rounded-lg p-4 border border-oled-border">
                  <div class="text-sm text-text-muted mb-2">Frustration</div>
                  <div
                    class="text-2xl font-bold"
                    :class="directorState.frustration_level > 0.7 ? 'text-red-400' : directorState.frustration_level > 0.4 ? 'text-yellow-400' : 'text-accent-success'"
                  >
                    {{ Math.round(directorState.frustration_level * 100) }}%
                  </div>
                  <div class="mt-2 h-2 bg-oled-border rounded-full overflow-hidden">
                    <div
                      class="h-full transition-all"
                      :class="directorState.frustration_level > 0.7 ? 'bg-red-400' : directorState.frustration_level > 0.4 ? 'bg-yellow-400' : 'bg-accent-success'"
                      :style="{ width: `${directorState.frustration_level * 100}%` }"
                    />
                  </div>
                </div>

                <!-- Observations -->
                <div class="bg-oled-black rounded-lg p-4 border border-oled-border">
                  <div class="text-sm text-text-muted mb-2">Code Submissions</div>
                  <div class="text-2xl font-bold text-text-primary">
                    {{ directorState.observation_count }}
                  </div>
                  <div class="text-xs text-text-muted mt-2">Total observed</div>
                </div>

                <!-- Active Struggles -->
                <div class="bg-oled-black rounded-lg p-4 border border-oled-border">
                  <div class="text-sm text-text-muted mb-2">Active Struggles</div>
                  <div
                    class="text-2xl font-bold"
                    :class="directorState.active_struggles > 0 ? 'text-accent-warning' : 'text-accent-success'"
                  >
                    {{ directorState.active_struggles }}
                  </div>
                  <div class="text-xs text-text-muted mt-2">Being tracked</div>
                </div>
              </div>
            </div>

            <!-- Learning Stats -->
            <div class="oled-panel mb-6">
              <h2 class="text-lg font-semibold mb-4">Learning Stats</h2>

              <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <!-- Success/Fail -->
                <div class="bg-oled-black rounded-lg p-4 border border-oled-border">
                  <div class="text-sm text-text-muted mb-2">Success Rate</div>
                  <div class="text-2xl font-bold text-accent-success">
                    {{ directorState.total_successes + directorState.total_failures > 0
                      ? Math.round(directorState.total_successes / (directorState.total_successes + directorState.total_failures) * 100)
                      : 0 }}%
                  </div>
                  <div class="text-xs text-text-muted mt-2">
                    {{ directorState.total_successes }} / {{ directorState.total_successes + directorState.total_failures }}
                  </div>
                </div>

                <!-- First Try Rate -->
                <div class="bg-oled-black rounded-lg p-4 border border-oled-border">
                  <div class="text-sm text-text-muted mb-2">First Try Rate</div>
                  <div class="text-2xl font-bold text-accent-primary">
                    {{ Math.round(directorState.first_try_rate * 100) }}%
                  </div>
                  <div class="text-xs text-text-muted mt-2">Solved on first attempt</div>
                </div>

                <!-- Learning Velocity -->
                <div class="bg-oled-black rounded-lg p-4 border border-oled-border">
                  <div class="text-sm text-text-muted mb-2">Learning Velocity</div>
                  <div
                    class="text-2xl font-bold"
                    :class="{
                      'text-accent-success': directorState.learning_velocity > 0,
                      'text-accent-warning': directorState.learning_velocity < 0,
                      'text-text-muted': directorState.learning_velocity === 0
                    }"
                  >
                    {{ directorState.learning_velocity > 0 ? '↑' : directorState.learning_velocity < 0 ? '↓' : '→' }}
                    {{ Math.abs(directorState.learning_velocity * 100).toFixed(0) }}%
                  </div>
                  <div class="text-xs text-text-muted mt-2">
                    {{ directorState.learning_velocity > 0.2 ? 'Improving fast!' :
                       directorState.learning_velocity > 0 ? 'Getting better' :
                       directorState.learning_velocity < -0.2 ? 'Hit a rough patch' :
                       directorState.learning_velocity < 0 ? 'Slight slowdown' : 'Steady pace' }}
                  </div>
                </div>

                <!-- Concepts Tracked -->
                <div class="bg-oled-black rounded-lg p-4 border border-oled-border">
                  <div class="text-sm text-text-muted mb-2">Concepts Tracked</div>
                  <div class="text-2xl font-bold text-text-primary">
                    {{ directorState.concepts_tracked }}
                  </div>
                  <div class="text-xs text-text-muted mt-2">Mastery entries</div>
                </div>
              </div>
            </div>

            <!-- Concept Mastery - Side by side: Needs Work + Recent Wins -->
            <div class="oled-panel mb-6">
              <h2 class="text-lg font-semibold mb-4">Your Learning Journey</h2>

              <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- Needs Work (clickable!) -->
                <div>
                  <div class="text-sm text-accent-warning font-medium mb-3">📚 Needs Practice</div>

                  <!-- Has struggles - show clickable list -->
                  <template v-if="directorState.struggling_concepts?.length">
                    <p class="text-xs text-text-muted mb-3">Click to practice!</p>
                    <div class="space-y-2">
                      <button
                        v-for="entry in directorState.struggling_concepts"
                        :key="entry.concept"
                        class="w-full text-left bg-accent-warning/5 border border-accent-warning/20 rounded-lg p-3 hover:bg-accent-warning/10 hover:border-accent-warning/40 transition-colors cursor-pointer gamepad-focusable"
                        @click="practiceConcept(entry.concept)"
                      >
                        <div class="flex items-center justify-between">
                          <span class="text-text-primary font-medium">{{ entry.concept }}</span>
                          <div class="flex items-center gap-2">
                            <span class="text-accent-warning font-bold">{{ Math.round(entry.score * 100) }}%</span>
                            <span class="text-accent-warning text-sm">→</span>
                          </div>
                        </div>
                        <div v-if="entry.failures && entry.failures > 1" class="text-xs text-text-muted mt-1">
                          {{ entry.failures }} attempts so far - you've got this!
                        </div>
                      </button>
                    </div>
                  </template>

                  <!-- No struggles - crushing it! -->
                  <template v-else>
                    <div class="bg-accent-success/5 border border-accent-success/20 rounded-lg p-4 text-center">
                      <div class="text-2xl mb-2">✨</div>
                      <p class="text-sm text-accent-success font-medium">Nothing at the moment!</p>
                      <p class="text-xs text-text-muted mt-1">You're absolutely crushing it.</p>
                    </div>
                  </template>
                </div>

                <!-- Recent Wins (motivational!) -->
                <div v-if="directorState.mastered_concepts?.length">
                  <div class="text-sm text-accent-success font-medium mb-3">🎉 Recent Wins</div>
                  <p class="text-xs text-text-muted mb-3">Look how far you've come!</p>
                  <div class="space-y-2">
                    <div
                      v-for="entry in directorState.mastered_concepts"
                      :key="entry.concept"
                      class="bg-accent-success/5 border border-accent-success/20 rounded-lg p-3"
                    >
                      <div class="flex items-center justify-between">
                        <span class="text-text-primary font-medium">{{ entry.concept }}</span>
                        <span class="text-accent-success font-bold">{{ Math.round(entry.score * 100) }}%</span>
                      </div>
                      <div v-if="entry.streak && entry.streak > 1" class="text-xs text-accent-success mt-1">
                        🔥 {{ entry.streak }} in a row!
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Encouragement when only struggling -->
                <div v-if="!directorState.mastered_concepts?.length && directorState.struggling_concepts?.length" class="lg:col-span-1">
                  <div class="bg-accent-primary/5 border border-accent-primary/20 rounded-lg p-4 text-center">
                    <div class="text-2xl mb-2">💪</div>
                    <p class="text-sm text-text-secondary">
                      Every expert was once a beginner. You're building your wins right now!
                    </p>
                  </div>
                </div>
              </div>

            </div>

            <!-- What The Director Sees -->
            <div class="oled-panel mb-6">
              <h2 class="text-lg font-semibold mb-4">What The Director Sees</h2>

              <div v-if="directorState.struggles.length === 0" class="text-center py-8 text-text-muted">
                <div class="text-4xl mb-3">✨</div>
                <p>No struggles detected - you're doing great!</p>
                <p class="text-sm mt-2">The Director is quietly watching and will help if needed.</p>
              </div>

              <div v-else class="space-y-3">
                <div
                  v-for="(struggle, idx) in directorState.struggles"
                  :key="idx"
                  class="bg-oled-black rounded-lg p-4 border border-oled-border"
                >
                  <div class="flex items-start justify-between gap-4">
                    <div class="flex-1">
                      <div class="flex items-center gap-2 mb-1">
                        <span
                          class="px-2 py-0.5 text-xs rounded font-medium"
                          :class="struggleColor(struggle.type)"
                        >
                          {{ formatStruggleType(struggle.type) }}
                        </span>
                        <span class="text-xs text-text-muted">
                          {{ struggle.frequency }}x
                        </span>
                      </div>
                      <p class="text-text-primary">{{ struggle.description }}</p>
                      <p class="text-xs text-text-muted mt-1">
                        First seen {{ timeAgo(struggle.first_seen) }} · Last seen {{ timeAgo(struggle.last_seen) }}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Shadow Adjustments (Silent Optimization) -->
            <div v-if="directorState.shadow_adjustments" class="oled-panel mb-6">
              <h2 class="text-lg font-semibold mb-4">
                Silent Optimization
                <span class="text-xs font-normal text-text-muted ml-2">(what The Director is doing behind the scenes)</span>
              </h2>

              <div class="space-y-4">
                <!-- Difficulty Bias -->
                <div class="flex items-center gap-4">
                  <div class="w-32 text-sm text-text-muted">Difficulty Bias</div>
                  <div class="flex-1">
                    <div class="h-2 bg-oled-border rounded-full overflow-hidden relative">
                      <!-- Center marker -->
                      <div class="absolute left-1/2 top-0 bottom-0 w-px bg-text-muted/30"></div>
                      <!-- Bias indicator -->
                      <div
                        class="absolute top-0 bottom-0 transition-all"
                        :class="directorState.shadow_adjustments.difficulty_bias < 0 ? 'bg-accent-success' : 'bg-accent-warning'"
                        :style="{
                          left: directorState.shadow_adjustments.difficulty_bias < 0
                            ? `${50 + directorState.shadow_adjustments.difficulty_bias * 50}%`
                            : '50%',
                          width: `${Math.abs(directorState.shadow_adjustments.difficulty_bias) * 50}%`
                        }"
                      />
                    </div>
                    <div class="flex justify-between text-xs text-text-muted mt-1">
                      <span>Easier</span>
                      <span>{{ directorState.shadow_adjustments.difficulty_bias > 0 ? '+' : '' }}{{ (directorState.shadow_adjustments.difficulty_bias * 100).toFixed(0) }}%</span>
                      <span>Harder</span>
                    </div>
                  </div>
                </div>

                <!-- Current Action -->
                <div class="p-3 bg-oled-black rounded-lg border border-oled-border">
                  <div class="text-sm text-text-muted mb-1">Current Action</div>
                  <div class="text-text-primary">
                    {{ directorState.shadow_adjustments.reason || 'No adjustments needed' }}
                  </div>
                </div>

                <!-- Avoiding/Preferring -->
                <div class="grid grid-cols-2 gap-4" v-if="directorState.shadow_adjustments.avoid_concepts?.length || directorState.shadow_adjustments.prefer_concepts?.length">
                  <div v-if="directorState.shadow_adjustments.avoid_concepts?.length">
                    <div class="text-sm text-text-muted mb-2">Temporarily Avoiding</div>
                    <div class="flex flex-wrap gap-1">
                      <span
                        v-for="concept in directorState.shadow_adjustments.avoid_concepts"
                        :key="concept"
                        class="px-2 py-0.5 text-xs rounded bg-red-500/20 text-red-400"
                      >
                        {{ concept }}
                      </span>
                    </div>
                  </div>
                  <div v-if="directorState.shadow_adjustments.prefer_concepts?.length">
                    <div class="text-sm text-text-muted mb-2">Building Momentum With</div>
                    <div class="flex flex-wrap gap-1">
                      <span
                        v-for="concept in directorState.shadow_adjustments.prefer_concepts"
                        :key="concept"
                        class="px-2 py-0.5 text-xs rounded bg-accent-success/20 text-accent-success"
                      >
                        {{ concept }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- How The Director Works -->
            <div class="oled-panel">
              <h2 class="text-lg font-semibold mb-4">How It Works</h2>

              <div class="space-y-4 text-sm text-text-secondary">
                <div class="flex gap-3">
                  <span class="text-lg">👀</span>
                  <div>
                    <div class="font-medium text-text-primary">Observes Submissions</div>
                    <p>Every time you submit code, The Director analyzes what happened.</p>
                  </div>
                </div>

                <div class="flex gap-3">
                  <span class="text-lg">🔍</span>
                  <div>
                    <div class="font-medium text-text-primary">Detects Patterns</div>
                    <p>If you're struggling with the same concept repeatedly, it notices.</p>
                  </div>
                </div>

                <div class="flex gap-3">
                  <span class="text-lg">💡</span>
                  <div>
                    <div class="font-medium text-text-primary">Offers Help</div>
                    <p>When frustration gets high or you're stuck, it can offer hints or suggest easier challenges.</p>
                  </div>
                </div>

                <div class="flex gap-3">
                  <span class="text-lg">🎯</span>
                  <div>
                    <div class="font-medium text-text-primary">Creates Content</div>
                    <p>If existing challenges don't address your specific gap, it can generate new ones just for you.</p>
                  </div>
                </div>
              </div>

              <div class="mt-6 p-4 bg-accent-primary/5 border border-accent-primary/20 rounded-lg">
                <div class="flex items-start gap-3">
                  <span class="text-lg">💚</span>
                  <div class="text-sm">
                    <div class="font-medium text-accent-primary mb-1">Your Data, Your Control</div>
                    <p class="text-text-secondary">
                      LMSP is MIT-licensed and open source. The Director works for YOU, not advertisers.
                      Everything it knows is shown right here. No hidden profiles, no dark patterns.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </section>

      </div>
    </main>
  </div>
</template>

<style scoped>
/* Pure OLED black nav - no grey backgrounds */
.settings-nav {
  background: transparent;
}

.settings-tab {
  @apply flex items-center gap-3 px-4 py-3 rounded-lg text-text-secondary transition-all;
}

.settings-tab:hover {
  @apply text-text-primary;
  background: rgba(255, 255, 255, 0.03);
}

.settings-tab.active {
  @apply text-accent-primary border-l-2 border-accent-primary;
  background: rgba(0, 255, 136, 0.05);
}

@media (max-width: 1023px) {
  .settings-tab.active {
    @apply border-l-0 border-b-2;
  }
}

.settings-section {
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
