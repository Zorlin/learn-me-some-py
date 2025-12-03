/**
 * Gamepad Navigation System
 * ==========================
 *
 * PRIORITY ZERO: Full gamepad navigation for the ENTIRE WebUI.
 *
 * This is how we make the game feel like a GAME, not a janky website.
 * The entire experience should be navigable with a gamepad.
 *
 * Controls:
 * - D-pad / Left Stick: Navigate between focusable elements
 * - A button: Select / Confirm / Activate
 * - B button: Back / Cancel / Close
 * - X button: Run tests / Secondary action
 * - Y button: Hint / Help / Tertiary action
 * - LT/RT: Scroll / Emotional feedback (analog)
 * - Start: Pause menu
 * - Select: Quick actions
 */

import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'

export interface FocusableElement {
  id: string
  element: HTMLElement
  group?: string
  onSelect?: () => void
  onBack?: () => void
}

// Input mode - automatically switches based on last input
export type InputMode = 'gamepad' | 'keyboard' | 'mouse'

// Global state
const inputMode = ref<InputMode>('keyboard')
const focusedId = ref<string | null>(null)
const focusableElements = ref<Map<string, FocusableElement>>(new Map())
const currentGroup = ref<string | null>(null)
const gamepadConnected = ref(false)

// Analog values from triggers
const leftTrigger = ref(0)
const rightTrigger = ref(0)

// Button states (for detecting press vs hold)
const buttonStates = ref({
  A: false,
  B: false,
  X: false,
  Y: false,
  UP: false,
  DOWN: false,
  LEFT: false,
  RIGHT: false,
  START: false,
  SELECT: false,
  LB: false,
  RB: false,
})

// Previous button states for edge detection
let prevButtonStates = { ...buttonStates.value }

// Navigation repeat timing
let lastNavTime = 0
const NAV_REPEAT_DELAY = 200 // ms between repeat navigations

export function useGamepadNavigation() {
  const router = useRouter()
  let animationFrameId: number | null = null

  /**
   * Register a focusable element
   */
  function registerFocusable(element: FocusableElement) {
    focusableElements.value.set(element.id, element)

    // If nothing is focused, focus this element
    if (!focusedId.value && inputMode.value === 'gamepad') {
      focusedId.value = element.id
    }
  }

  /**
   * Unregister a focusable element
   */
  function unregisterFocusable(id: string) {
    focusableElements.value.delete(id)

    // If the removed element was focused, focus the next one
    if (focusedId.value === id) {
      const elements = Array.from(focusableElements.value.keys())
      focusedId.value = elements[0] || null
    }
  }

  /**
   * Focus a specific element by ID
   */
  function focusElement(id: string) {
    if (focusableElements.value.has(id)) {
      focusedId.value = id
      const element = focusableElements.value.get(id)
      element?.element?.focus?.()
    }
  }

  /**
   * Get elements in the current group, sorted by position
   */
  function getGroupElements(group?: string): FocusableElement[] {
    const elements = Array.from(focusableElements.value.values())
      .filter(el => !group || el.group === group)

    // Sort by visual position (top-left to bottom-right)
    return elements.sort((a, b) => {
      const rectA = a.element.getBoundingClientRect()
      const rectB = b.element.getBoundingClientRect()

      // First sort by row (Y position)
      if (Math.abs(rectA.top - rectB.top) > 30) {
        return rectA.top - rectB.top
      }
      // Then by column (X position)
      return rectA.left - rectB.left
    })
  }

  /**
   * Navigate to next element in direction
   */
  function navigate(direction: 'UP' | 'DOWN' | 'LEFT' | 'RIGHT') {
    const elements = getGroupElements(currentGroup.value || undefined)
    if (elements.length === 0) return

    const currentIndex = elements.findIndex(el => el.id === focusedId.value)
    if (currentIndex === -1) {
      focusElement(elements[0].id)
      return
    }

    let nextIndex = currentIndex

    switch (direction) {
      case 'UP':
        nextIndex = Math.max(0, currentIndex - 1)
        break
      case 'DOWN':
        nextIndex = Math.min(elements.length - 1, currentIndex + 1)
        break
      case 'LEFT':
        // Find element to the left in same row
        const currentRect = elements[currentIndex].element.getBoundingClientRect()
        const leftElements = elements.filter((el, i) => {
          const rect = el.element.getBoundingClientRect()
          return rect.left < currentRect.left &&
                 Math.abs(rect.top - currentRect.top) < 30
        })
        if (leftElements.length > 0) {
          nextIndex = elements.indexOf(leftElements[leftElements.length - 1])
        }
        break
      case 'RIGHT':
        // Find element to the right in same row
        const currRect = elements[currentIndex].element.getBoundingClientRect()
        const rightElements = elements.filter((el, i) => {
          const rect = el.element.getBoundingClientRect()
          return rect.left > currRect.left &&
                 Math.abs(rect.top - currRect.top) < 30
        })
        if (rightElements.length > 0) {
          nextIndex = elements.indexOf(rightElements[0])
        }
        break
    }

    if (nextIndex !== currentIndex) {
      focusElement(elements[nextIndex].id)
    }
  }

  /**
   * Activate the currently focused element
   */
  function activateFocused() {
    if (!focusedId.value) return

    const element = focusableElements.value.get(focusedId.value)
    if (element?.onSelect) {
      element.onSelect()
    } else if (element?.element) {
      element.element.click()
    }
  }

  /**
   * Go back / cancel
   */
  function goBack() {
    const element = focusableElements.value.get(focusedId.value || '')
    if (element?.onBack) {
      element.onBack()
    } else {
      router.back()
    }
  }

  /**
   * Check if a button was just pressed (edge detection)
   */
  function wasJustPressed(button: keyof typeof buttonStates.value): boolean {
    return buttonStates.value[button] && !prevButtonStates[button]
  }

  /**
   * Main gamepad polling loop
   */
  function pollGamepad() {
    const gamepads = navigator.getGamepads()
    const gamepad = gamepads[0] // Use first connected gamepad

    if (gamepad) {
      gamepadConnected.value = true

      // Read analog triggers (usually axes 2 and 5, or buttons 6 and 7)
      leftTrigger.value = gamepad.buttons[6]?.value ?? 0
      rightTrigger.value = gamepad.buttons[7]?.value ?? 0

      // Read buttons
      const newStates = {
        A: gamepad.buttons[0]?.pressed ?? false,
        B: gamepad.buttons[1]?.pressed ?? false,
        X: gamepad.buttons[2]?.pressed ?? false,
        Y: gamepad.buttons[3]?.pressed ?? false,
        LB: gamepad.buttons[4]?.pressed ?? false,
        RB: gamepad.buttons[5]?.pressed ?? false,
        SELECT: gamepad.buttons[8]?.pressed ?? false,
        START: gamepad.buttons[9]?.pressed ?? false,
        UP: gamepad.buttons[12]?.pressed ?? false,
        DOWN: gamepad.buttons[13]?.pressed ?? false,
        LEFT: gamepad.buttons[14]?.pressed ?? false,
        RIGHT: gamepad.buttons[15]?.pressed ?? false,
      }

      // Also check analog stick for navigation
      const leftStickX = gamepad.axes[0] ?? 0
      const leftStickY = gamepad.axes[1] ?? 0
      const STICK_THRESHOLD = 0.5

      if (leftStickY < -STICK_THRESHOLD) newStates.UP = true
      if (leftStickY > STICK_THRESHOLD) newStates.DOWN = true
      if (leftStickX < -STICK_THRESHOLD) newStates.LEFT = true
      if (leftStickX > STICK_THRESHOLD) newStates.RIGHT = true

      // Store previous state before updating
      prevButtonStates = { ...buttonStates.value }
      buttonStates.value = newStates

      // If any button pressed, switch to gamepad mode
      if (Object.values(newStates).some(v => v)) {
        if (inputMode.value !== 'gamepad') {
          inputMode.value = 'gamepad'
          document.body.classList.add('gamepad-mode')
          document.body.classList.remove('keyboard-mode', 'mouse-mode')
        }
      }

      // Handle navigation with repeat delay
      const now = Date.now()
      if (now - lastNavTime > NAV_REPEAT_DELAY) {
        if (wasJustPressed('UP') || (buttonStates.value.UP && now - lastNavTime > NAV_REPEAT_DELAY * 2)) {
          navigate('UP')
          lastNavTime = now
        } else if (wasJustPressed('DOWN') || (buttonStates.value.DOWN && now - lastNavTime > NAV_REPEAT_DELAY * 2)) {
          navigate('DOWN')
          lastNavTime = now
        } else if (wasJustPressed('LEFT') || (buttonStates.value.LEFT && now - lastNavTime > NAV_REPEAT_DELAY * 2)) {
          navigate('LEFT')
          lastNavTime = now
        } else if (wasJustPressed('RIGHT') || (buttonStates.value.RIGHT && now - lastNavTime > NAV_REPEAT_DELAY * 2)) {
          navigate('RIGHT')
          lastNavTime = now
        }
      }

      // Handle button presses (edge detection for single-fire actions)
      if (wasJustPressed('A')) {
        activateFocused()
      }
      if (wasJustPressed('B')) {
        goBack()
      }

      // Emit events for X, Y, Start, Select
      if (wasJustPressed('X')) {
        window.dispatchEvent(new CustomEvent('gamepad:x'))
      }
      if (wasJustPressed('Y')) {
        window.dispatchEvent(new CustomEvent('gamepad:y'))
      }
      if (wasJustPressed('START')) {
        window.dispatchEvent(new CustomEvent('gamepad:start'))
      }
      if (wasJustPressed('SELECT')) {
        window.dispatchEvent(new CustomEvent('gamepad:select'))
      }
    } else {
      gamepadConnected.value = false
    }

    animationFrameId = requestAnimationFrame(pollGamepad)
  }

  /**
   * Handle keyboard events
   */
  function handleKeydown(event: KeyboardEvent) {
    // Switch to keyboard mode
    if (inputMode.value !== 'keyboard') {
      inputMode.value = 'keyboard'
      document.body.classList.add('keyboard-mode')
      document.body.classList.remove('gamepad-mode', 'mouse-mode')
    }

    // Navigation keys
    switch (event.key) {
      case 'ArrowUp':
        event.preventDefault()
        navigate('UP')
        break
      case 'ArrowDown':
        event.preventDefault()
        navigate('DOWN')
        break
      case 'ArrowLeft':
        event.preventDefault()
        navigate('LEFT')
        break
      case 'ArrowRight':
        event.preventDefault()
        navigate('RIGHT')
        break
      case 'Enter':
      case ' ':
        event.preventDefault()
        activateFocused()
        break
      case 'Escape':
        event.preventDefault()
        goBack()
        break
    }
  }

  /**
   * Handle mouse events
   */
  function handleMouseMove() {
    if (inputMode.value !== 'mouse') {
      inputMode.value = 'mouse'
      document.body.classList.add('mouse-mode')
      document.body.classList.remove('gamepad-mode', 'keyboard-mode')
    }
  }

  // Lifecycle
  onMounted(() => {
    animationFrameId = requestAnimationFrame(pollGamepad)
    window.addEventListener('keydown', handleKeydown)
    window.addEventListener('mousemove', handleMouseMove)

    // Listen for gamepad connect/disconnect
    window.addEventListener('gamepadconnected', () => {
      gamepadConnected.value = true
      console.log('🎮 Gamepad connected!')
    })
    window.addEventListener('gamepaddisconnected', () => {
      gamepadConnected.value = false
      console.log('🎮 Gamepad disconnected')
    })
  })

  onUnmounted(() => {
    if (animationFrameId) {
      cancelAnimationFrame(animationFrameId)
    }
    window.removeEventListener('keydown', handleKeydown)
    window.removeEventListener('mousemove', handleMouseMove)
  })

  return {
    // State
    inputMode,
    focusedId,
    gamepadConnected,
    leftTrigger,
    rightTrigger,
    buttonStates,

    // Methods
    registerFocusable,
    unregisterFocusable,
    focusElement,
    navigate,
    activateFocused,
    goBack,

    // Computed
    isGamepadMode: computed(() => inputMode.value === 'gamepad'),
    isKeyboardMode: computed(() => inputMode.value === 'keyboard'),
    isMouseMode: computed(() => inputMode.value === 'mouse'),
  }
}

/**
 * Directive for making elements focusable via gamepad
 *
 * Usage:
 *   <button v-focusable="{ id: 'btn-1', group: 'menu', onSelect: handleClick }">
 */
export const vFocusable = {
  mounted(el: HTMLElement, binding: any) {
    const { id, group, onSelect, onBack } = binding.value || {}
    const elementId = id || `focusable-${Math.random().toString(36).slice(2)}`

    el.dataset.focusableId = elementId
    el.setAttribute('tabindex', '0')

    // Add focus classes
    el.classList.add('gamepad-focusable')

    // Register with navigation system
    const { registerFocusable } = useGamepadNavigation()
    registerFocusable({
      id: elementId,
      element: el,
      group,
      onSelect,
      onBack,
    })
  },

  unmounted(el: HTMLElement) {
    const elementId = el.dataset.focusableId
    if (elementId) {
      const { unregisterFocusable } = useGamepadNavigation()
      unregisterFocusable(elementId)
    }
  }
}
