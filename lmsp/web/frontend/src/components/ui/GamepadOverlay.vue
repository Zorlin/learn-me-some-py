<script setup lang="ts">
/**
 * Gamepad Overlay Component
 * ==========================
 *
 * Shows context-aware gamepad button hints.
 * Automatically appears/hides based on input mode.
 * Reads hints from route meta or uses defaults.
 */

import { computed, onMounted, onUnmounted, ref, inject } from 'vue'
import { useRoute } from 'vue-router'
import { useGamepadStore } from '@/stores/gamepad'

// Hint definition type
export interface GamepadHint {
  button: 'A' | 'B' | 'X' | 'Y' | 'LB' | 'RB' | 'LT' | 'RT' | 'DPad' | 'LS' | 'RS'
  label: string
}

// Injectable hint context
const contextHints = inject<GamepadHint[] | null>('gamepadHints', null)

const gamepadStore = useGamepadStore()
const route = useRoute()

// Local input mode tracking
const inputMode = ref<'gamepad' | 'keyboard' | 'mouse'>('keyboard')
const showHints = ref(false)

// Default hints per route pattern
const defaultHintsByRoute: Record<string, GamepadHint[]> = {
  '/': [
    { button: 'A', label: 'Select' },
    { button: 'B', label: 'Back' },
    { button: 'DPad', label: 'Navigate' },
  ],
  '/challenges': [
    { button: 'A', label: 'Select' },
    { button: 'B', label: 'Back' },
    { button: 'DPad', label: 'Navigate' },
    { button: 'RS', label: 'Cursor' },
  ],
  '/challenge': [
    { button: 'A', label: 'Submit' },
    { button: 'B', label: 'Back' },
    { button: 'X', label: 'Run Tests' },
    { button: 'Y', label: 'Hint' },
    { button: 'LT', label: 'Frustrated' },
    { button: 'RT', label: 'Satisfied' },
  ],
  '/settings': [
    { button: 'A', label: 'Select' },
    { button: 'B', label: 'Home' },
    { button: 'DPad', label: 'Navigate' },
  ],
  '/progress': [
    { button: 'A', label: 'Select' },
    { button: 'B', label: 'Back' },
    { button: 'DPad', label: 'Navigate' },
  ],
}

// Get hints for current context
const hints = computed(() => {
  // 1. Use injected context hints if available
  if (contextHints && contextHints.length > 0) {
    return contextHints
  }

  // 2. Use route meta hints if defined
  if (route.meta?.gamepadHints) {
    return route.meta.gamepadHints as GamepadHint[]
  }

  // 3. Fall back to route pattern matching
  const path = route.path
  for (const [pattern, patternHints] of Object.entries(defaultHintsByRoute)) {
    if (path === pattern || path.startsWith(pattern + '/')) {
      return patternHints
    }
  }

  // 4. Default minimal hints
  return [
    { button: 'A', label: 'Select' },
    { button: 'B', label: 'Back' },
  ]
})

// Update body class based on input mode
function updateBodyClass() {
  document.body.classList.remove('gamepad-mode', 'keyboard-mode', 'mouse-mode')
  document.body.classList.add(`${inputMode.value}-mode`)
}

// Handle gamepad button press
function handleGamepadInput() {
  if (inputMode.value !== 'gamepad') {
    inputMode.value = 'gamepad'
    showHints.value = true
    updateBodyClass()
  }
}

// Handle keyboard input
function handleKeyboard(e: KeyboardEvent) {
  if (inputMode.value !== 'keyboard') {
    inputMode.value = 'keyboard'
    showHints.value = false
    updateBodyClass()
  }
}

// Handle mouse input
function handleMouse() {
  if (inputMode.value !== 'mouse') {
    inputMode.value = 'mouse'
    showHints.value = false
    updateBodyClass()
  }
}

// Get button color class
function buttonClass(btn: string): string {
  switch (btn) {
    case 'A': return 'btn-a'
    case 'B': return 'btn-b'
    case 'X': return 'btn-x'
    case 'Y': return 'btn-y'
    case 'LB':
    case 'RB': return 'btn-bumper'
    case 'LT':
    case 'RT': return 'btn-trigger'
    default: return 'btn-other'
  }
}

// Watch gamepad store for button presses
let pollInterval: number | null = null

onMounted(() => {
  window.addEventListener('keydown', handleKeyboard)
  window.addEventListener('mousemove', handleMouse)

  // Poll for gamepad input
  pollInterval = window.setInterval(() => {
    if (gamepadStore.connected) {
      // Check if any button is pressed or stick moved
      const { buttons, leftTrigger, rightTrigger, leftStick, rightStick } = gamepadStore
      const anyPressed = Object.values(buttons).some(b => b) ||
                         leftTrigger > 0.1 ||
                         rightTrigger > 0.1 ||
                         Math.abs(leftStick.x) > 0.3 ||
                         Math.abs(leftStick.y) > 0.3 ||
                         Math.abs(rightStick.x) > 0.3 ||
                         Math.abs(rightStick.y) > 0.3

      if (anyPressed) {
        handleGamepadInput()
      }
    }
  }, 100)

  updateBodyClass()
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyboard)
  window.removeEventListener('mousemove', handleMouse)
  if (pollInterval) {
    clearInterval(pollInterval)
  }
})
</script>

<template>
  <!-- Gamepad Hints (visible in gamepad mode) -->
  <Transition name="fade">
    <div
      v-if="inputMode === 'gamepad' && showHints && gamepadStore.connected"
      class="gamepad-hints-overlay"
    >
      <div class="gamepad-hints">
        <div
          v-for="hint in hints"
          :key="hint.button"
          class="gamepad-hint"
        >
          <span class="gamepad-hint-button" :class="buttonClass(hint.button)">
            {{ hint.button }}
          </span>
          <span class="hint-label">{{ hint.label }}</span>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.gamepad-hints-overlay {
  @apply fixed bottom-4 right-4 z-50;
  @apply px-3 py-2 rounded-lg;
  @apply bg-oled-black/80 backdrop-blur-sm border border-oled-border;
}

.gamepad-hints {
  @apply flex flex-wrap gap-3;
}

.gamepad-hint {
  @apply flex items-center gap-1.5;
}

.gamepad-hint-button {
  @apply w-6 h-6 rounded flex items-center justify-center;
  @apply text-xs font-bold;
}

.btn-a {
  @apply bg-green-600 text-white;
}

.btn-b {
  @apply bg-red-600 text-white;
}

.btn-x {
  @apply bg-blue-600 text-white;
}

.btn-y {
  @apply bg-yellow-500 text-black;
}

.btn-bumper {
  @apply bg-gray-600 text-white text-[10px];
}

.btn-trigger {
  @apply bg-gray-700 text-white text-[10px];
}

.btn-other {
  @apply bg-gray-600 text-white text-[10px];
}

.hint-label {
  @apply text-xs text-text-secondary;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
