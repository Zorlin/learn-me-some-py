<script setup lang="ts">
/**
 * Gamepad Overlay Component
 * ==========================
 *
 * Shows current input mode and gamepad button hints.
 * Automatically appears/hides based on input mode.
 */

import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useGamepadStore } from '@/stores/gamepad'

const gamepadStore = useGamepadStore()

// Local input mode tracking
const inputMode = ref<'gamepad' | 'keyboard' | 'mouse'>('keyboard')
const showHints = ref(false)

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

// Watch gamepad store for button presses
let pollInterval: number | null = null

onMounted(() => {
  window.addEventListener('keydown', handleKeyboard)
  window.addEventListener('mousemove', handleMouse)

  // Poll for gamepad input
  pollInterval = window.setInterval(() => {
    if (gamepadStore.connected) {
      // Check if any button is pressed
      const { buttons, leftTrigger, rightTrigger } = gamepadStore
      const anyPressed = Object.values(buttons).some(b => b) ||
                         leftTrigger > 0.1 ||
                         rightTrigger > 0.1

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

const modeIcon = computed(() => {
  switch (inputMode.value) {
    case 'gamepad': return '🎮'
    case 'keyboard': return '⌨️'
    case 'mouse': return '🖱️'
  }
})

const modeLabel = computed(() => {
  switch (inputMode.value) {
    case 'gamepad': return 'Gamepad'
    case 'keyboard': return 'Keyboard'
    case 'mouse': return 'Mouse'
  }
})
</script>

<template>
  <!-- Gamepad Hints (visible in gamepad mode) -->
  <Transition name="fade">
    <div
      v-if="inputMode === 'gamepad' && showHints"
      class="gamepad-hints-overlay"
    >
      <div class="gamepad-hints">
        <div class="gamepad-hint">
          <span class="gamepad-hint-button a">A</span>
          <span>Select</span>
        </div>
        <div class="gamepad-hint">
          <span class="gamepad-hint-button b">B</span>
          <span>Back</span>
        </div>
        <div class="gamepad-hint">
          <span class="gamepad-hint-button x">X</span>
          <span>Run</span>
        </div>
        <div class="gamepad-hint">
          <span class="gamepad-hint-button y">Y</span>
          <span>Hint</span>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.gamepad-hints-overlay {
  @apply fixed bottom-4 right-4 z-50;
  @apply px-4 py-2 rounded-lg;
  @apply bg-oled-panel/90 backdrop-blur-sm border border-oled-border;
}
</style>
