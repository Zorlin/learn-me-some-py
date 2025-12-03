<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useGamepadStore } from '@/stores/gamepad'
import { usePlayerStore } from '@/stores/player'

const props = defineProps<{
  question?: string
  context?: string
}>()

const emit = defineEmits<{
  confirm: [{ enjoyment: number; frustration: number }]
}>()

const gamepadStore = useGamepadStore()
const playerStore = usePlayerStore()

// Simulated values for keyboard input
const manualEnjoyment = ref(0)
const manualFrustration = ref(0)
const confirmed = ref(false)

// Use gamepad values if connected, otherwise manual
const enjoyment = ref(0)
const frustration = ref(0)

// Watch gamepad triggers
watch(() => gamepadStore.rightTrigger, (val) => {
  if (gamepadStore.connected) {
    enjoyment.value = val
  }
})

watch(() => gamepadStore.leftTrigger, (val) => {
  if (gamepadStore.connected) {
    frustration.value = val
  }
})

// Watch manual inputs
watch(manualEnjoyment, (val) => {
  if (!gamepadStore.connected) {
    enjoyment.value = val
  }
})

watch(manualFrustration, (val) => {
  if (!gamepadStore.connected) {
    frustration.value = val
  }
})

// Confirm and submit feedback
function confirmFeedback() {
  confirmed.value = true

  // Record to backend
  if (enjoyment.value > 0.1) {
    playerStore.recordEmotionalFeedback('RT', enjoyment.value, props.context || 'challenge')
  }
  if (frustration.value > 0.1) {
    playerStore.recordEmotionalFeedback('LT', frustration.value, props.context || 'challenge')
  }

  emit('confirm', {
    enjoyment: enjoyment.value,
    frustration: frustration.value,
  })
}

// Listen for gamepad A button
let pollInterval: number | null = null

onMounted(() => {
  pollInterval = window.setInterval(() => {
    if (gamepadStore.connected && gamepadStore.isButtonPressed('A') && !confirmed.value) {
      confirmFeedback()
    }
  }, 100)
})

onUnmounted(() => {
  if (pollInterval) {
    clearInterval(pollInterval)
  }
})
</script>

<template>
  <div class="oled-panel-glow p-6 max-w-md mx-auto">
    <h3 class="text-xl font-bold text-center mb-6">
      {{ question || 'How was that?' }}
    </h3>

    <!-- Gamepad Mode Indicator -->
    <div v-if="gamepadStore.connected" class="text-center text-sm text-accent-primary mb-4">
      🎮 Use triggers to express your feelings
    </div>

    <!-- Enjoyment (RT) -->
    <div class="mb-6">
      <div class="flex items-center justify-between mb-2">
        <span class="text-sm text-text-secondary">Satisfying / Fun</span>
        <span class="text-accent-primary font-mono">{{ Math.round(enjoyment * 100) }}%</span>
      </div>
      <div class="trigger-bar">
        <div
          class="trigger-fill-positive"
          :style="{ width: `${enjoyment * 100}%` }"
        />
      </div>
      <!-- Keyboard input for non-gamepad -->
      <input
        v-if="!gamepadStore.connected"
        type="range"
        v-model.number="manualEnjoyment"
        min="0"
        max="1"
        step="0.05"
        class="w-full mt-2 accent-accent-primary"
      />
      <div v-else class="text-xs text-text-muted mt-1 text-center">
        Pull RT (Right Trigger)
      </div>
    </div>

    <!-- Frustration (LT) -->
    <div class="mb-6">
      <div class="flex items-center justify-between mb-2">
        <span class="text-sm text-text-secondary">Frustrating / Confusing</span>
        <span class="text-accent-error font-mono">{{ Math.round(frustration * 100) }}%</span>
      </div>
      <div class="trigger-bar">
        <div
          class="trigger-fill-negative"
          :style="{ width: `${frustration * 100}%` }"
        />
      </div>
      <!-- Keyboard input for non-gamepad -->
      <input
        v-if="!gamepadStore.connected"
        type="range"
        v-model.number="manualFrustration"
        min="0"
        max="1"
        step="0.05"
        class="w-full mt-2 accent-accent-error"
      />
      <div v-else class="text-xs text-text-muted mt-1 text-center">
        Pull LT (Left Trigger)
      </div>
    </div>

    <!-- Confirm Button -->
    <button
      v-if="!confirmed"
      class="oled-button-primary w-full py-3 text-lg"
      @click="confirmFeedback"
    >
      {{ gamepadStore.connected ? 'Press A to Confirm' : 'Confirm' }}
    </button>

    <div v-else class="text-center text-accent-primary">
      ✓ Feedback recorded
    </div>
  </div>
</template>
