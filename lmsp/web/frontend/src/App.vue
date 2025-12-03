<script setup lang="ts">
/**
 * Main App Component
 * ===================
 *
 * PRIORITY ZERO: The ENTIRE app is gamepad-navigable!
 * Real-time input mode detection (gamepad/keyboard/mouse)
 * Visual focus system that looks GORGEOUS
 */

import { onMounted, onUnmounted, ref } from 'vue'
import { useGamepadStore } from '@/stores/gamepad'
import GamepadStatus from '@/components/input/GamepadStatus.vue'
import AchievementPopup from '@/components/progress/AchievementPopup.vue'
import GamepadOverlay from '@/components/ui/GamepadOverlay.vue'

const gamepadStore = useGamepadStore()
const showAchievement = ref(false)
const currentAchievement = ref<{name: string, description: string, tier: string} | null>(null)

// Listen for gamepad connections
onMounted(() => {
  gamepadStore.startPolling()

  // Listen for achievement events
  window.addEventListener('lmsp:achievement', handleAchievement as EventListener)
})

onUnmounted(() => {
  gamepadStore.stopPolling()
  window.removeEventListener('lmsp:achievement', handleAchievement as EventListener)
})

function handleAchievement(event: CustomEvent) {
  currentAchievement.value = event.detail
  showAchievement.value = true

  // Auto-hide after 5 seconds
  setTimeout(() => {
    showAchievement.value = false
  }, 5000)
}
</script>

<template>
  <div class="app-layout min-h-screen bg-oled-black text-white flex flex-col">
    <!-- Header - sticky instead of fixed for proper full-page screenshots -->
    <header class="app-header sticky top-0 z-40 bg-oled-black/95 backdrop-blur-sm border-b border-oled-border flex-shrink-0">
      <div class="responsive-container-wide py-3 flex items-center justify-between">
        <router-link
          to="/"
          class="lmsp-logo flex items-center gap-2 gamepad-focusable rounded-lg px-2 py-1 -ml-2"
          tabindex="0"
        >
          <span class="text-2xl font-bold text-accent-primary">LMSP</span>
          <span class="text-sm text-text-secondary hidden sm:inline">Learn Me Some Py</span>
        </router-link>

        <nav class="flex items-center gap-2">
          <router-link
            to="/"
            class="nav-link gamepad-focusable px-3 py-2 rounded-lg text-text-secondary hover:text-white hover:bg-oled-panel transition-all"
            tabindex="0"
          >
            Home
          </router-link>
          <router-link
            to="/challenges"
            class="nav-link gamepad-focusable px-3 py-2 rounded-lg text-text-secondary hover:text-white hover:bg-oled-panel transition-all"
            tabindex="0"
          >
            Challenges
          </router-link>
          <router-link
            to="/progress"
            class="nav-link gamepad-focusable px-3 py-2 rounded-lg text-text-secondary hover:text-white hover:bg-oled-panel transition-all"
            tabindex="0"
          >
            Progress
          </router-link>
          <router-link
            to="/settings"
            class="nav-link gamepad-focusable px-3 py-2 rounded-lg text-text-secondary hover:text-white hover:bg-oled-panel transition-all"
            tabindex="0"
          >
            Settings
          </router-link>
          <GamepadStatus />
        </nav>
      </div>
    </header>

    <!-- Main Content - flex-grow ensures it fills available space -->
    <main class="app-main flex-grow">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- Achievement Popup -->
    <Transition name="slide">
      <AchievementPopup
        v-if="showAchievement && currentAchievement"
        :achievement="currentAchievement"
        @close="showAchievement = false"
      />
    </Transition>

    <!-- Gamepad Button Hints (visible in gamepad mode) -->
    <GamepadOverlay />

    <!-- Footer - flex-shrink-0 keeps it at natural size, not fixed for proper screenshots -->
    <footer class="app-footer flex-shrink-0 bg-oled-black border-t border-oled-border py-2">
      <div class="responsive-container-wide flex items-center justify-between text-xs text-text-muted">
        <span>The game that teaches you to build it</span>
        <span v-if="gamepadStore.connected" class="text-accent-primary">
          🎮 Gamepad Connected
        </span>
      </div>
    </footer>
  </div>
</template>
