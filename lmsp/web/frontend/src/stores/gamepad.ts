/**
 * Gamepad State Store
 * ====================
 *
 * Handles Gamepad API integration for controller input.
 * Supports analog triggers for emotional feedback.
 */

import { defineStore } from 'pinia'
import { ref, readonly } from 'vue'

export interface GamepadState {
  connected: boolean
  leftTrigger: number      // 0.0-1.0
  rightTrigger: number     // 0.0-1.0
  leftStick: { x: number; y: number }
  rightStick: { x: number; y: number }
  buttons: Record<string, boolean>
}

// Standard Gamepad button indices
const BUTTON_NAMES: Record<number, string> = {
  0: 'A',
  1: 'B',
  2: 'X',
  3: 'Y',
  4: 'LB',
  5: 'RB',
  6: 'LT', // Also available as axis
  7: 'RT', // Also available as axis
  8: 'Back',
  9: 'Start',
  10: 'L3',
  11: 'R3',
  12: 'DPadUp',
  13: 'DPadDown',
  14: 'DPadLeft',
  15: 'DPadRight',
}

export const useGamepadStore = defineStore('gamepad', () => {
  // State
  const connected = ref(false)
  const leftTrigger = ref(0)
  const rightTrigger = ref(0)
  const leftStick = ref({ x: 0, y: 0 })
  const rightStick = ref({ x: 0, y: 0 })
  const buttons = ref<Record<string, boolean>>({})
  const gamepadIndex = ref<number | null>(null)

  // Debug mode - toggle with gamepadStore.setDebug(true) in console
  const debugMode = ref(false)
  // Track previous state for change detection
  let prevButtons: Record<string, boolean> = {}
  let prevLeftTrigger = 0
  let prevRightTrigger = 0

  let animationFrameId: number | null = null

  // Actions
  function startPolling() {
    // Listen for gamepad connection
    window.addEventListener('gamepadconnected', onGamepadConnected)
    window.addEventListener('gamepaddisconnected', onGamepadDisconnected)

    // Check for already-connected gamepads
    const gamepads = navigator.getGamepads()
    for (const gp of gamepads) {
      if (gp) {
        onGamepadConnected({ gamepad: gp } as GamepadEvent)
        break
      }
    }

    // Start polling loop
    pollGamepad()
  }

  function stopPolling() {
    window.removeEventListener('gamepadconnected', onGamepadConnected)
    window.removeEventListener('gamepaddisconnected', onGamepadDisconnected)

    if (animationFrameId !== null) {
      cancelAnimationFrame(animationFrameId)
      animationFrameId = null
    }
  }

  function onGamepadConnected(event: GamepadEvent) {
    console.log('Gamepad connected:', event.gamepad.id)
    connected.value = true
    gamepadIndex.value = event.gamepad.index
  }

  function onGamepadDisconnected(event: GamepadEvent) {
    console.log('Gamepad disconnected:', event.gamepad.id)
    if (gamepadIndex.value === event.gamepad.index) {
      connected.value = false
      gamepadIndex.value = null
      resetState()
    }
  }

  function pollGamepad() {
    if (gamepadIndex.value !== null) {
      const gamepads = navigator.getGamepads()
      const gp = gamepads[gamepadIndex.value]

      if (gp) {
        updateState(gp)
      }
    }

    animationFrameId = requestAnimationFrame(pollGamepad)
  }

  // Deadzone for triggers (ignore values below this)
  const TRIGGER_DEADZONE = 0.05

  function applyDeadzone(value: number, deadzone: number): number {
    if (Math.abs(value) < deadzone) return 0
    // Remap value from deadzone..1 to 0..1
    const sign = Math.sign(value)
    const magnitude = Math.abs(value)
    return sign * (magnitude - deadzone) / (1 - deadzone)
  }

  function updateState(gp: Gamepad) {
    // Triggers are buttons 6/7 on standard controllers (Xbox, PS, etc.)
    // They provide analog values from 0.0 (unpressed) to 1.0 (fully pressed)
    const rawLeftTrigger = gp.buttons[6]?.value ?? 0
    const rawRightTrigger = gp.buttons[7]?.value ?? 0

    // Apply deadzone to prevent drift and ensure clean 0 at rest
    const newLeftTrigger = applyDeadzone(rawLeftTrigger, TRIGGER_DEADZONE)
    const newRightTrigger = applyDeadzone(rawRightTrigger, TRIGGER_DEADZONE)

    // Debug: Log trigger changes
    if (debugMode.value) {
      if (Math.abs(newLeftTrigger - prevLeftTrigger) > 0.01) {
        console.log(`🎮 LT: ${(newLeftTrigger * 100).toFixed(0)}%`)
        prevLeftTrigger = newLeftTrigger
      }
      if (Math.abs(newRightTrigger - prevRightTrigger) > 0.01) {
        console.log(`🎮 RT: ${(newRightTrigger * 100).toFixed(0)}%`)
        prevRightTrigger = newRightTrigger
      }
    }

    leftTrigger.value = newLeftTrigger
    rightTrigger.value = newRightTrigger

    // Update sticks (axes 0,1 = left stick, axes 2,3 = right stick)
    if (gp.axes.length >= 2) {
      leftStick.value = { x: gp.axes[0], y: gp.axes[1] }
    }
    if (gp.axes.length >= 4) {
      rightStick.value = { x: gp.axes[2], y: gp.axes[3] }
    }

    // Update buttons
    const newButtons: Record<string, boolean> = {}
    for (let i = 0; i < gp.buttons.length; i++) {
      const name = BUTTON_NAMES[i] || `Button${i}`
      newButtons[name] = gp.buttons[i].pressed

      // Debug: Log button state changes (only if previous state was known)
      if (debugMode.value && name in prevButtons && newButtons[name] !== prevButtons[name]) {
        if (newButtons[name]) {
          console.log(`🎮 ${name} pressed`)
        } else {
          console.log(`🎮 ${name} released`)
        }
      }
    }
    prevButtons = { ...newButtons }
    buttons.value = newButtons
  }

  function resetState() {
    leftTrigger.value = 0
    rightTrigger.value = 0
    leftStick.value = { x: 0, y: 0 }
    rightStick.value = { x: 0, y: 0 }
    buttons.value = {}
  }

  // Check if a button was just pressed (for edge detection, call externally)
  function isButtonPressed(buttonName: string): boolean {
    return buttons.value[buttonName] || false
  }

  // Debug mode toggle - call from browser console:
  // gamepadDebug.enable() or gamepadDebug.status()
  function setDebug(enabled: boolean) {
    debugMode.value = enabled
    if (enabled) {
      console.log('🎮 Gamepad debug mode ENABLED')
      console.log('   - Button presses/releases will be logged')
      console.log('   - Trigger values will be logged as they change')
      console.log('   - Call gamepadDebug.disable() to turn off')
      // Log immediate status
      console.log('🎮 Current state:', {
        connected: connected.value,
        leftTrigger: leftTrigger.value,
        rightTrigger: rightTrigger.value,
        buttons: Object.entries(buttons.value).filter(([_, v]) => v).map(([k]) => k),
      })
    } else {
      console.log('🎮 Gamepad debug mode disabled')
    }
  }

  // Continuous debug (logs every frame while held)
  function setVerboseDebug(enabled: boolean) {
    if (enabled) {
      debugMode.value = true
      console.log('🎮 VERBOSE debug mode - logging EVERY frame')
      const logFrame = () => {
        if (!debugMode.value) return
        console.log('🎮 Frame:', {
          LT: (leftTrigger.value * 100).toFixed(0) + '%',
          RT: (rightTrigger.value * 100).toFixed(0) + '%',
          buttons: Object.entries(buttons.value).filter(([_, v]) => v).map(([k]) => k).join(', ') || 'none',
        })
        if (debugMode.value) requestAnimationFrame(logFrame)
      }
      requestAnimationFrame(logFrame)
    } else {
      debugMode.value = false
    }
  }

  // Expose debug tools globally for console access
  if (typeof window !== 'undefined') {
    (window as any).gamepadDebug = {
      enable: () => setDebug(true),
      disable: () => setDebug(false),
      verbose: () => setVerboseDebug(true),
      status: () => {
        const state = {
          connected: connected.value,
          debugMode: debugMode.value,
          leftTrigger: leftTrigger.value,
          rightTrigger: rightTrigger.value,
          leftStick: leftStick.value,
          rightStick: rightStick.value,
          buttons: buttons.value,
          pressedButtons: Object.entries(buttons.value).filter(([_, v]) => v).map(([k]) => k),
        }
        console.log('🎮 Gamepad Status:', state)
        return state
      },
      raw: () => {
        // Show raw gamepad data from browser API
        const gp = navigator.getGamepads()[0]
        if (gp) {
          console.log('🎮 Raw gamepad data:')
          console.log('   Buttons:', gp.buttons.map((b, i) => `${i}:${b.value.toFixed(2)}`).join(' '))
          console.log('   Axes:', gp.axes.map((a, i) => `${i}:${a.toFixed(2)}`).join(' '))
        } else {
          console.log('🎮 No gamepad connected')
        }
      },
    }
    console.log('🎮 Gamepad debug available: gamepadDebug.enable(), gamepadDebug.verbose(), gamepadDebug.status(), gamepadDebug.raw()')
  }

  return {
    // State (readonly for external access)
    connected: readonly(connected),
    leftTrigger: readonly(leftTrigger),
    rightTrigger: readonly(rightTrigger),
    leftStick: readonly(leftStick),
    rightStick: readonly(rightStick),
    buttons: readonly(buttons),
    debugMode: readonly(debugMode),

    // Actions
    startPolling,
    stopPolling,
    isButtonPressed,
    setDebug,
    setVerboseDebug,
  }
})
