<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useGamepadStore } from '@/stores/gamepad'
import { useGamepadNav } from '@/composables/useGamepadNav'
import SecuritySettings from '@/components/settings/SecuritySettings.vue'

const router = useRouter()
const gamepadStore = useGamepadStore()

// Enable gamepad navigation
useGamepadNav({ onBack: () => router.push('/') })

const inputMode = ref<'keyboard' | 'gamepad' | 'auto'>('auto')
const theme = ref<'dark' | 'oled'>('oled')

// Player profile
const playerName = ref('')
const nameSaved = ref(false)

onMounted(() => {
  // Load saved name from localStorage
  const savedName = localStorage.getItem('lmsp_player_name')
  if (savedName) {
    playerName.value = savedName
  }
})

function saveName() {
  localStorage.setItem('lmsp_player_name', playerName.value.trim())
  nameSaved.value = true
  setTimeout(() => { nameSaved.value = false }, 2000)
}
</script>

<template>
  <div class="max-w-2xl mx-auto px-4 py-8">
    <!-- Header with player name -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
      <h1 class="text-3xl font-bold">
        <span class="text-accent-primary">⚙️</span> Settings
      </h1>
      <div class="flex items-center gap-2">
        <input
          id="player-name"
          v-model="playerName"
          type="text"
          placeholder="Your name..."
          class="w-40 sm:w-48 px-3 py-1.5 text-sm bg-oled-bg border border-oled-border rounded-lg text-text-primary placeholder-text-muted focus:border-accent-primary focus:outline-none"
          @blur="saveName"
          @keyup.enter="($event.target as HTMLInputElement).blur()"
        />
        <span v-if="nameSaved" class="text-accent-success text-sm">✓</span>
      </div>
    </div>

    <!-- Input Settings -->
    <div class="oled-panel mb-6">
      <h2 class="text-xl font-bold mb-4">Input</h2>

      <div class="space-y-4">
        <div>
          <label class="text-sm text-text-secondary block mb-2">Input Mode</label>
          <div class="flex gap-2">
            <button
              class="oled-button flex-1 gamepad-focusable"
              :class="{ 'border-accent-primary text-accent-primary': inputMode === 'keyboard' }"
              @click="inputMode = 'keyboard'"
            >
              ⌨️ Keyboard
            </button>
            <button
              class="oled-button flex-1 gamepad-focusable"
              :class="{ 'border-accent-primary text-accent-primary': inputMode === 'gamepad' }"
              @click="inputMode = 'gamepad'"
            >
              🎮 Gamepad
            </button>
            <button
              class="oled-button flex-1 gamepad-focusable"
              :class="{ 'border-accent-primary text-accent-primary': inputMode === 'auto' }"
              @click="inputMode = 'auto'"
            >
              ✨ Auto
            </button>
          </div>
        </div>

        <div v-if="gamepadStore.connected" class="p-4 bg-accent-primary/10 border border-accent-primary/30 rounded-lg">
          <div class="text-sm text-accent-primary font-medium mb-1">🎮 Gamepad Connected</div>
          <div class="text-xs text-text-muted mb-2 font-mono truncate" :title="gamepadStore.controllerName">
            {{ gamepadStore.profileName }} profile
          </div>
          <div class="text-sm text-text-secondary">
            Using analog triggers for emotional feedback
          </div>

          <!-- Analog Triggers -->
          <div class="mt-4 grid grid-cols-2 gap-4">
            <div>
              <div class="flex justify-between text-xs text-text-muted mb-1">
                <span>LT (Left Trigger)</span>
                <span class="font-mono">{{ Math.round(gamepadStore.leftTrigger * 100) }}%</span>
              </div>
              <div class="trigger-bar">
                <div
                  class="trigger-fill-negative"
                  :style="{ width: `${gamepadStore.leftTrigger * 100}%` }"
                />
              </div>
            </div>
            <div>
              <div class="flex justify-between text-xs text-text-muted mb-1">
                <span>RT (Right Trigger)</span>
                <span class="font-mono">{{ Math.round(gamepadStore.rightTrigger * 100) }}%</span>
              </div>
              <div class="trigger-bar">
                <div
                  class="trigger-fill-positive"
                  :style="{ width: `${gamepadStore.rightTrigger * 100}%` }"
                />
              </div>
            </div>
          </div>

          <!-- Analog Sticks -->
          <div class="mt-4 grid grid-cols-2 gap-4">
            <div>
              <div class="text-xs text-text-muted mb-2">Left Stick</div>
              <div class="relative w-20 h-20 mx-auto bg-oled-panel rounded-full border border-oled-border">
                <!-- Crosshair -->
                <div class="absolute top-1/2 left-0 right-0 h-px bg-oled-border"></div>
                <div class="absolute left-1/2 top-0 bottom-0 w-px bg-oled-border"></div>
                <!-- Stick position -->
                <div
                  class="absolute w-4 h-4 bg-accent-primary rounded-full -translate-x-1/2 -translate-y-1/2 transition-all duration-75"
                  :style="{
                    left: `${50 + gamepadStore.leftStick.x * 40}%`,
                    top: `${50 + gamepadStore.leftStick.y * 40}%`
                  }"
                />
              </div>
              <div class="text-xs text-text-muted text-center mt-1 font-mono">
                {{ gamepadStore.leftStick.x.toFixed(2) }}, {{ gamepadStore.leftStick.y.toFixed(2) }}
              </div>
            </div>
            <div>
              <div class="text-xs text-text-muted mb-2">Right Stick</div>
              <div class="relative w-20 h-20 mx-auto bg-oled-panel rounded-full border border-oled-border">
                <!-- Crosshair -->
                <div class="absolute top-1/2 left-0 right-0 h-px bg-oled-border"></div>
                <div class="absolute left-1/2 top-0 bottom-0 w-px bg-oled-border"></div>
                <!-- Stick position -->
                <div
                  class="absolute w-4 h-4 bg-accent-secondary rounded-full -translate-x-1/2 -translate-y-1/2 transition-all duration-75"
                  :style="{
                    left: `${50 + gamepadStore.rightStick.x * 40}%`,
                    top: `${50 + gamepadStore.rightStick.y * 40}%`
                  }"
                />
              </div>
              <div class="text-xs text-text-muted text-center mt-1 font-mono">
                {{ gamepadStore.rightStick.x.toFixed(2) }}, {{ gamepadStore.rightStick.y.toFixed(2) }}
              </div>
            </div>
          </div>

          <!-- Active Buttons -->
          <div class="mt-4">
            <div class="text-xs text-text-muted mb-2">Buttons</div>
            <div class="flex flex-wrap gap-1">
              <span
                v-for="(pressed, name) in gamepadStore.buttons"
                :key="name"
                class="px-2 py-1 text-xs rounded font-mono"
                :class="pressed ? 'bg-accent-primary text-oled-bg' : 'bg-oled-panel text-text-muted'"
              >
                {{ name }}
              </span>
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
          class="oled-button flex-1 py-4 gamepad-focusable"
          :class="{ 'border-accent-primary text-accent-primary': theme === 'oled' }"
          @click="theme = 'oled'"
        >
          <div class="text-2xl mb-2">🌑</div>
          <div>OLED Black</div>
          <div class="text-xs text-text-muted">Pure black (#000)</div>
        </button>
        <button
          class="oled-button flex-1 py-4 gamepad-focusable"
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
