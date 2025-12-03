/**
 * Gamepad State Store
 * ====================
 *
 * Pinia store wrapping the gamepad module for Vue reactivity.
 * Uses the clean gamepad library for cross-controller support.
 */

import { defineStore } from 'pinia'
import { ref, readonly, computed } from 'vue'
import {
  GamepadManager,
  type UnifiedGamepadState,
  type ControllerProfile,
  createEmptyState,
  listProfiles,
  debugDetection,
} from '@/lib/gamepad'

export const useGamepadStore = defineStore('gamepad', () => {
  // Internal state
  const state = ref<UnifiedGamepadState>(createEmptyState())
  const manager = new GamepadManager()

  // Debug mode
  const debugMode = ref(false)
  let prevState: UnifiedGamepadState | null = null

  // Computed getters for common values
  const connected = computed(() => state.value.connected)
  const controllerName = computed(() => state.value.id)
  const profileName = computed(() => state.value.profileName)

  // Sticks
  const leftStick = computed(() => state.value.leftStick)
  const rightStick = computed(() => state.value.rightStick)

  // Triggers
  const leftTrigger = computed(() => state.value.leftTrigger)
  const rightTrigger = computed(() => state.value.rightTrigger)

  // Buttons - transform to simple record for compatibility
  const buttons = computed(() => state.value.buttons as Record<string, boolean>)

  // Start polling
  function startPolling() {
    manager.onStateChange((newState) => {
      state.value = newState

      // Debug logging
      if (debugMode.value && prevState) {
        logChanges(prevState, newState)
      }
      prevState = { ...newState, buttons: { ...newState.buttons } }
    })
    manager.start()
  }

  function stopPolling() {
    manager.stop()
  }

  function setDebug(enabled: boolean) {
    debugMode.value = enabled
    if (enabled) {
      console.log('🎮 Gamepad debug mode ENABLED')
      console.log('   Profile:', state.value.profileName)
      console.log('   Controller:', state.value.id)
    } else {
      console.log('🎮 Gamepad debug mode disabled')
    }
  }

  function setVerboseDebug(enabled: boolean) {
    debugMode.value = enabled
    if (enabled) {
      console.log('🎮 VERBOSE debug mode - logging every frame')
      const logFrame = () => {
        if (!debugMode.value) return
        console.log('🎮 Frame:', {
          LT: `${Math.round(state.value.leftTrigger * 100)}%`,
          RT: `${Math.round(state.value.rightTrigger * 100)}%`,
          LS: `${state.value.leftStick.x.toFixed(2)},${state.value.leftStick.y.toFixed(2)}`,
          RS: `${state.value.rightStick.x.toFixed(2)},${state.value.rightStick.y.toFixed(2)}`,
          buttons: Object.entries(state.value.buttons)
            .filter(([_, v]) => v)
            .map(([k]) => k)
            .join(', ') || 'none',
        })
        if (debugMode.value) requestAnimationFrame(logFrame)
      }
      requestAnimationFrame(logFrame)
    }
  }

  function logChanges(prev: UnifiedGamepadState, curr: UnifiedGamepadState) {
    // Log trigger changes
    if (Math.abs(curr.leftTrigger - prev.leftTrigger) > 0.01) {
      console.log(`🎮 LT: ${Math.round(curr.leftTrigger * 100)}%`)
    }
    if (Math.abs(curr.rightTrigger - prev.rightTrigger) > 0.01) {
      console.log(`🎮 RT: ${Math.round(curr.rightTrigger * 100)}%`)
    }

    // Log button changes
    for (const [name, pressed] of Object.entries(curr.buttons)) {
      const wasPressed = prev.buttons[name as keyof typeof prev.buttons]
      if (pressed !== wasPressed) {
        console.log(`🎮 ${name} ${pressed ? 'pressed' : 'released'}`)
      }
    }
  }

  function isButtonPressed(buttonName: string): boolean {
    return state.value.buttons[buttonName as keyof typeof state.value.buttons] ?? false
  }

  // Override profile manually
  function setProfileOverride(profileName: string | null) {
    manager.setProfileOverride(profileName)
  }

  // Expose debug tools globally
  if (typeof window !== 'undefined') {
    (window as any).gamepadDebug = {
      enable: () => setDebug(true),
      disable: () => setDebug(false),
      verbose: () => setVerboseDebug(true),
      status: () => {
        const s = state.value
        console.log('🎮 Gamepad Status:', {
          connected: s.connected,
          profile: s.profileName,
          controller: s.id,
          leftTrigger: s.leftTrigger,
          rightTrigger: s.rightTrigger,
          leftStick: s.leftStick,
          rightStick: s.rightStick,
          pressedButtons: Object.entries(s.buttons)
            .filter(([_, v]) => v)
            .map(([k]) => k),
        })
        return s
      },
      raw: () => {
        const gp = manager.getRawGamepad()
        if (gp) {
          console.log('🎮 Raw gamepad:')
          console.log('   ID:', gp.id)
          console.log('   Buttons:', gp.buttons.map((b, i) => `${i}:${b.value.toFixed(2)}`).join(' '))
          console.log('   Axes:', gp.axes.map((a, i) => `${i}:${a.toFixed(2)}`).join(' '))
        } else {
          console.log('🎮 No gamepad connected')
        }
      },
      profiles: () => {
        console.log('🎮 Available profiles:', listProfiles())
      },
      testId: (id: string) => {
        console.log('🎮 Testing ID:', id)
        console.log('   Matches:', debugDetection(id))
      },
      setProfile: (name: string) => {
        manager.setProfileOverride(name)
        console.log(`🎮 Profile override: ${name}`)
      },
      autoProfile: () => {
        manager.setProfileOverride(null)
        console.log('🎮 Auto profile detection enabled')
      },
    }
    console.log('🎮 Gamepad debug: gamepadDebug.enable(), .status(), .raw(), .profiles(), .testId(id)')
  }

  return {
    // State (readonly)
    connected,
    controllerName,
    profileName,
    leftTrigger,
    rightTrigger,
    leftStick,
    rightStick,
    buttons,
    debugMode: readonly(debugMode),

    // Full state access
    state: readonly(state),

    // Actions
    startPolling,
    stopPolling,
    isButtonPressed,
    setDebug,
    setVerboseDebug,
    setProfileOverride,
  }
})
