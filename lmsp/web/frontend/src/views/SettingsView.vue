<script setup lang="ts">
import { ref } from 'vue'
import { useGamepadStore } from '@/stores/gamepad'
import SecuritySettings from '@/components/settings/SecuritySettings.vue'

const gamepadStore = useGamepadStore()

const inputMode = ref<'keyboard' | 'gamepad' | 'auto'>('auto')
const theme = ref<'dark' | 'oled'>('oled')
</script>

<template>
  <div class="max-w-2xl mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8">
      <span class="text-accent-primary">⚙️</span> Settings
    </h1>

    <!-- Input Settings -->
    <div class="oled-panel mb-6">
      <h2 class="text-xl font-bold mb-4">Input</h2>

      <div class="space-y-4">
        <div>
          <label class="text-sm text-text-secondary block mb-2">Input Mode</label>
          <div class="flex gap-2">
            <button
              class="oled-button flex-1"
              :class="{ 'border-accent-primary text-accent-primary': inputMode === 'keyboard' }"
              @click="inputMode = 'keyboard'"
            >
              ⌨️ Keyboard
            </button>
            <button
              class="oled-button flex-1"
              :class="{ 'border-accent-primary text-accent-primary': inputMode === 'gamepad' }"
              @click="inputMode = 'gamepad'"
            >
              🎮 Gamepad
            </button>
            <button
              class="oled-button flex-1"
              :class="{ 'border-accent-primary text-accent-primary': inputMode === 'auto' }"
              @click="inputMode = 'auto'"
            >
              ✨ Auto
            </button>
          </div>
        </div>

        <div v-if="gamepadStore.connected" class="p-4 bg-accent-primary/10 border border-accent-primary/30 rounded-lg">
          <div class="text-sm text-accent-primary font-medium mb-2">🎮 Gamepad Connected</div>
          <div class="text-sm text-text-secondary">
            Using analog triggers for emotional feedback
          </div>

          <!-- Trigger Test -->
          <div class="mt-4 grid grid-cols-2 gap-4">
            <div>
              <div class="text-xs text-text-muted mb-1">Left Trigger</div>
              <div class="trigger-bar">
                <div
                  class="trigger-fill-negative"
                  :style="{ width: `${gamepadStore.leftTrigger * 100}%` }"
                />
              </div>
            </div>
            <div>
              <div class="text-xs text-text-muted mb-1">Right Trigger</div>
              <div class="trigger-bar">
                <div
                  class="trigger-fill-positive"
                  :style="{ width: `${gamepadStore.rightTrigger * 100}%` }"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Theme Settings -->
    <div class="oled-panel mb-6">
      <h2 class="text-xl font-bold mb-4">Theme</h2>

      <div class="flex gap-2">
        <button
          class="oled-button flex-1 py-4"
          :class="{ 'border-accent-primary text-accent-primary': theme === 'oled' }"
          @click="theme = 'oled'"
        >
          <div class="text-2xl mb-2">🌑</div>
          <div>OLED Black</div>
          <div class="text-xs text-text-muted">Pure black (#000)</div>
        </button>
        <button
          class="oled-button flex-1 py-4"
          :class="{ 'border-accent-primary text-accent-primary': theme === 'dark' }"
          @click="theme = 'dark'"
        >
          <div class="text-2xl mb-2">🌙</div>
          <div>Dark</div>
          <div class="text-xs text-text-muted">Soft dark theme</div>
        </button>
      </div>
    </div>

    <!-- Security Settings -->
    <div class="oled-panel mb-6">
      <SecuritySettings />
    </div>

    <!-- About -->
    <div class="oled-panel">
      <h2 class="text-xl font-bold mb-4">About</h2>
      <div class="text-text-secondary">
        <p class="mb-2">
          <strong>LMSP</strong> - Learn Me Some Py
        </p>
        <p class="mb-4">
          The game that teaches you to build it.
        </p>
        <p class="text-sm text-text-muted">
          Built in The Forge. Powered by Palace. For the joy of learning.
        </p>
      </div>
    </div>
  </div>
</template>
