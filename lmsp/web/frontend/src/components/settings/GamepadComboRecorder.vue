<script setup lang="ts">
/**
 * Gamepad Combo Recorder
 * ======================
 *
 * Records a custom gamepad button sequence for unlock.
 * Shows live feedback as buttons are pressed.
 */

import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useGamepadStore } from '@/stores/gamepad'

const emit = defineEmits<{
  (e: 'combo-recorded', combo: string[]): void
  (e: 'cancel'): void
}>()

const gamepadStore = useGamepadStore()

const recordedCombo = ref<string[]>([])
const isRecording = ref(true)
const holdingSticks = ref(false)
const holdStartTime = ref<number | null>(null)
const holdProgress = ref(0)

// Valid buttons for combo - keys MUST match gamepad store button names (no hyphens!)
const BUTTON_MAP: Record<string, string> = {
  'A': 'A',
  'B': 'B',
  'X': 'X',
  'Y': 'Y',
  'DPadUp': 'UP',
  'DPadDown': 'DOWN',
  'DPadLeft': 'LEFT',
  'DPadRight': 'RIGHT',
  'LB': 'L1',
  'RB': 'R1',
}

const MAX_COMBO_LENGTH = 8

// Track last button state to detect new presses
const lastButtons = ref<Record<string, boolean>>({})

// Watch for button presses
watch(() => gamepadStore.buttons, (buttons) => {
  if (!isRecording.value) return

  // Check for new button presses
  for (const [key, label] of Object.entries(BUTTON_MAP)) {
    const isPressed = buttons[key as keyof typeof buttons]
    const wasPressed = lastButtons.value[key]

    if (isPressed && !wasPressed && recordedCombo.value.length < MAX_COMBO_LENGTH) {
      recordedCombo.value.push(label)
    }
  }

  // Update last state
  lastButtons.value = { ...buttons }

  // Check for L3+R3 hold to confirm
  const bothSticksPressed = buttons.L3 && buttons.R3

  if (bothSticksPressed && !holdingSticks.value) {
    holdingSticks.value = true
    holdStartTime.value = Date.now()
  } else if (!bothSticksPressed) {
    holdingSticks.value = false
    holdStartTime.value = null
    holdProgress.value = 0
  }
}, { deep: true })

// Update hold progress
let holdInterval: number | null = null

onMounted(() => {
  holdInterval = window.setInterval(() => {
    if (holdingSticks.value && holdStartTime.value && recordedCombo.value.length >= 2) {
      const elapsed = Date.now() - holdStartTime.value
      holdProgress.value = Math.min(100, (elapsed / 1500) * 100)

      // After 1.5 seconds, confirm combo
      if (elapsed >= 1500) {
        confirmCombo()
      }
    }
  }, 50)
})

onUnmounted(() => {
  if (holdInterval) {
    clearInterval(holdInterval)
  }
})

function confirmCombo() {
  if (recordedCombo.value.length >= 2) {
    // Add L3+R3 as the confirmation step
    const finalCombo = [...recordedCombo.value, 'L3+R3']
    isRecording.value = false
    emit('combo-recorded', finalCombo)
  }
}

function clearCombo() {
  recordedCombo.value = []
}

function cancel() {
  emit('cancel')
}

// Button display helper
function getButtonClass(button: string): string {
  const colors: Record<string, string> = {
    'A': 'btn-a',
    'B': 'btn-b',
    'X': 'btn-x',
    'Y': 'btn-y',
    'UP': 'btn-dpad',
    'DOWN': 'btn-dpad',
    'LEFT': 'btn-dpad',
    'RIGHT': 'btn-dpad',
    'L1': 'btn-shoulder',
    'R1': 'btn-shoulder',
    'L3+R3': 'btn-stick',
  }
  return colors[button] || 'btn-default'
}
</script>

<template>
  <div class="combo-recorder">
    <div class="recorder-header">
      <h3>Record Gamepad Combo</h3>
      <p class="text-text-secondary text-sm">
        Press buttons to create your unlock sequence, then hold both sticks (L3+R3) to confirm.
      </p>
    </div>

    <!-- Recorded Combo Display -->
    <div class="combo-display">
      <div
        v-for="(button, index) in recordedCombo"
        :key="index"
        class="combo-button"
        :class="getButtonClass(button)"
      >
        {{ button }}
      </div>
      <div v-if="recordedCombo.length === 0" class="combo-placeholder">
        Press buttons...
      </div>
    </div>

    <!-- Status -->
    <div class="recorder-status">
      <div v-if="recordedCombo.length < 2" class="status-hint">
        Add at least 2 buttons to your combo
      </div>
      <div v-else-if="!holdingSticks" class="status-hint">
        Hold L3 + R3 together to confirm
      </div>
      <div v-else class="status-confirming">
        <div class="hold-progress">
          <div class="hold-bar" :style="{ width: `${holdProgress}%` }"></div>
        </div>
        <span>Hold to confirm... {{ Math.round(holdProgress) }}%</span>
      </div>
    </div>

    <!-- Actions -->
    <div class="recorder-actions">
      <button class="oled-button" @click="clearCombo" :disabled="recordedCombo.length === 0">
        Clear
      </button>
      <button class="oled-button" @click="cancel">
        Cancel
      </button>
    </div>

    <!-- Gamepad Visual Hint -->
    <div class="gamepad-hint">
      <div class="hint-row">
        <span class="hint-button btn-y">Y</span>
        <span class="hint-button btn-x">X</span>
        <span class="hint-button btn-b">B</span>
        <span class="hint-button btn-a">A</span>
        <span class="hint-label">Face Buttons</span>
      </div>
      <div class="hint-row">
        <span class="hint-button btn-dpad">↑↓←→</span>
        <span class="hint-label">D-Pad</span>
      </div>
      <div class="hint-row">
        <span class="hint-button btn-shoulder">L1/R1</span>
        <span class="hint-label">Shoulders</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.combo-recorder {
  @apply p-6 rounded-lg;
  background: var(--oled-panel);
  border: 1px solid var(--oled-border);
}

.recorder-header {
  @apply mb-4;
}

.recorder-header h3 {
  @apply text-lg font-semibold mb-1;
}

.combo-display {
  @apply flex flex-wrap gap-2 p-4 rounded-md min-h-[60px] mb-4;
  background: var(--oled-surface);
  border: 1px solid var(--oled-border);
}

.combo-button {
  @apply px-3 py-2 rounded-md font-mono text-sm font-bold;
  min-width: 40px;
  text-align: center;
}

.combo-placeholder {
  @apply text-text-muted italic;
}

.btn-a { @apply bg-green-600 text-white; }
.btn-b { @apply bg-red-600 text-white; }
.btn-x { @apply bg-blue-600 text-white; }
.btn-y { @apply bg-yellow-500 text-black; }
.btn-dpad { @apply bg-gray-600 text-white; }
.btn-shoulder { @apply bg-purple-600 text-white; }
.btn-stick { @apply bg-orange-500 text-white; }
.btn-default { @apply bg-gray-500 text-white; }

.recorder-status {
  @apply mb-4 text-center;
}

.status-hint {
  @apply text-text-secondary text-sm;
}

.status-confirming {
  color: var(--accent-success);
}

.hold-progress {
  @apply w-full h-2 rounded-full overflow-hidden mb-2;
  background: var(--oled-surface);
}

.hold-bar {
  @apply h-full rounded-full transition-all;
  background: var(--accent-success);
}

.recorder-actions {
  @apply flex gap-3 justify-center mb-4;
}

.gamepad-hint {
  @apply mt-4 pt-4 border-t border-oled-border;
}

.hint-row {
  @apply flex items-center gap-2 mb-2 text-sm;
}

.hint-button {
  @apply px-2 py-1 rounded text-xs font-bold;
  opacity: 0.7;
}

.hint-label {
  @apply text-text-muted;
}
</style>
