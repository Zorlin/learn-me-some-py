/**
 * Gamepad Navigation Composable v2
 * =================================
 *
 * Full NESW + diagonal navigation with:
 * - D-pad: Digital 8-direction navigation
 * - Left stick: Analog D-pad equivalent
 * - Right stick: No Man's Sky style cursor (speed-sensitive)
 * - A/B buttons: Activate/Back
 *
 * Smart 2D grid navigation based on element positions.
 */

import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useGamepadStore } from '@/stores/gamepad'

export interface GamepadNavOptions {
  // Custom back action (default: router.back())
  onBack?: () => void
  // Selector for focusable elements (default: '.gamepad-focusable')
  selector?: string
  // Enable wrap-around navigation
  wrap?: boolean
  // Enable cursor mode (right stick)
  enableCursor?: boolean
  // Cursor speed multiplier
  cursorSpeed?: number
}

interface ElementPosition {
  index: number
  el: HTMLElement
  rect: DOMRect
  centerX: number
  centerY: number
}

// Stick deadzone
const STICK_DEADZONE = 0.3
const STICK_NAV_THRESHOLD = 0.7 // Threshold for triggering navigation
const CURSOR_BASE_SPEED = 15 // Base pixels per frame at full deflection

// NO COOLDOWN. INSTANT. RESPONSIVE. (see CLAUDE.md)

export function useGamepadNav(options: GamepadNavOptions = {}) {
  const {
    onBack,
    selector = '.gamepad-focusable',
    wrap = true,
    enableCursor = true,
    cursorSpeed = 1.0,
  } = options

  const router = useRouter()
  const gamepadStore = useGamepadStore()

  const focusedIndex = ref(-1)
  const prevButtons = ref<Record<string, boolean>>({})
  const prevLeftStick = ref({ x: 0, y: 0 })

  // Cursor state
  const cursorX = ref(window.innerWidth / 2)
  const cursorY = ref(window.innerHeight / 2)
  const cursorVisible = ref(false)
  const cursorElement = ref<HTMLElement | null>(null)

  // Animation frame for cursor
  let animationFrameId: number | null = null

  // Get all focusable elements with their positions
  function getFocusableElements(): ElementPosition[] {
    const elements = Array.from(document.querySelectorAll(selector)) as HTMLElement[]
    return elements.map((el, index) => {
      const rect = el.getBoundingClientRect()
      return {
        index,
        el,
        rect,
        centerX: rect.left + rect.width / 2,
        centerY: rect.top + rect.height / 2,
      }
    })
  }

  // Update visual focus
  function updateFocus(index: number) {
    const positions = getFocusableElements()
    if (positions.length === 0) return

    // Remove focus from all
    positions.forEach(p => p.el.classList.remove('gamepad-focused'))

    // Clamp or wrap index
    if (wrap) {
      index = ((index % positions.length) + positions.length) % positions.length
    } else {
      index = Math.max(0, Math.min(positions.length - 1, index))
    }

    focusedIndex.value = index

    // Add focus to current
    const pos = positions[index]
    if (pos) {
      pos.el.classList.add('gamepad-focused')
      pos.el.scrollIntoView({ behavior: 'smooth', block: 'nearest' })

      // Hide cursor when using D-pad/stick navigation
      cursorVisible.value = false
    }
  }

  // Find nearest element in a direction (NESW + diagonals)
  // Smart grid-aware: horizontal moves prefer same row, vertical moves prefer same column
  function findNearest(
    current: ElementPosition,
    all: ElementPosition[],
    dirX: number,
    dirY: number
  ): number | null {
    // Normalize direction
    const mag = Math.sqrt(dirX * dirX + dirY * dirY)
    if (mag < 0.1) return null
    const normX = dirX / mag
    const normY = dirY / mag

    // Determine if this is primarily horizontal or vertical movement
    const isHorizontal = Math.abs(normX) > Math.abs(normY)
    const isVertical = Math.abs(normY) > Math.abs(normX)

    // SPECIAL CASE: Logo - Right goes to nav-links only, Left is wall
    const isLogo = current.el.classList.contains('lmsp-logo')
    if (isLogo) {
      if (isHorizontal && normX > 0) {
        // Right: ONLY consider nav-links
        let bestIndex: number | null = null
        let bestDist = Infinity
        for (const pos of all) {
          if (pos.index === current.index) continue
          if (!pos.el.classList.contains('nav-link')) continue
          const dx = pos.centerX - current.centerX
          if (dx <= 0) continue // Must be to the right
          if (dx < bestDist) {
            bestDist = dx
            bestIndex = pos.index
          }
        }
        return bestIndex !== null ? bestIndex : current.index
      }
      if (isHorizontal && normX < 0) {
        // Left: wall (nothing to the left of logo)
        return current.index
      }
      if (isVertical) {
        // Down: nearest non-header element below
        let bestIndex: number | null = null
        let bestDist = Infinity
        for (const pos of all) {
          if (pos.index === current.index) continue
          if (pos.el.classList.contains('nav-link')) continue
          if (pos.el.classList.contains('lmsp-logo')) continue
          const dy = pos.centerY - current.centerY
          if (normY > 0 && dy <= 0) continue
          if (normY < 0 && dy >= 0) continue
          const dx = pos.centerX - current.centerX
          const dist = Math.sqrt(dx * dx + dy * dy)
          if (dist < bestDist) {
            bestDist = dist
            bestIndex = pos.index
          }
        }
        return bestIndex !== null ? bestIndex : current.index
      }
    }

    // SPECIAL CASE: Nav-links are 1D horizontal row
    const isNavLink = current.el.classList.contains('nav-link')
    if (isNavLink) {
      if (isHorizontal) {
        // Left/Right: only consider other nav-links OR logo (for leftmost)
        let bestIndex: number | null = null
        let bestDist = Infinity
        for (const pos of all) {
          if (pos.index === current.index) continue
          // Allow nav-links and logo
          if (!pos.el.classList.contains('nav-link') && !pos.el.classList.contains('lmsp-logo')) continue
          const dx = pos.centerX - current.centerX
          if (normX > 0 && dx <= 0) continue
          if (normX < 0 && dx >= 0) continue
          if (Math.abs(dx) < bestDist) {
            bestDist = Math.abs(dx)
            bestIndex = pos.index
          }
        }
        return bestIndex !== null ? bestIndex : current.index
      }
      if (isVertical) {
        // Down: nearest non-header element
        let bestIndex: number | null = null
        let bestDist = Infinity
        for (const pos of all) {
          if (pos.index === current.index) continue
          if (pos.el.classList.contains('nav-link')) continue
          if (pos.el.classList.contains('lmsp-logo')) continue
          const dy = pos.centerY - current.centerY
          if (normY > 0 && dy <= 0) continue
          if (normY < 0 && dy >= 0) continue
          const dx = pos.centerX - current.centerX
          const dist = Math.sqrt(dx * dx + dy * dy)
          if (dist < bestDist) {
            bestDist = dist
            bestIndex = pos.index
          }
        }
        return bestIndex !== null ? bestIndex : current.index
      }
    }

    // SPECIAL CASE: Filter row is 1D horizontal
    const isFilterButton = current.el.classList.contains('level-filter-btn')
    if (isFilterButton) {
      if (isVertical) {
        // Vertical: find nearest NON-filter element
        let bestIndex: number | null = null
        let bestDist = Infinity
        for (const pos of all) {
          if (pos.index === current.index) continue
          // EXCLUDE other filter buttons - they're on the same row!
          if (pos.el.classList.contains('level-filter-btn')) continue
          const dy = pos.centerY - current.centerY
          // Must be in the correct vertical direction
          if (normY > 0 && dy <= 0) continue
          if (normY < 0 && dy >= 0) continue
          const dx = pos.centerX - current.centerX
          const dist = Math.sqrt(dx * dx + dy * dy)
          if (dist < bestDist) {
            bestDist = dist
            bestIndex = pos.index
          }
        }
        return bestIndex
      }
      if (isHorizontal) {
        // Horizontal: ONLY consider other filter buttons, stay put if none (wall)
        let bestIndex: number | null = null
        let bestDist = Infinity
        for (const pos of all) {
          if (pos.index === current.index) continue
          // ONLY other filter buttons
          if (!pos.el.classList.contains('level-filter-btn')) continue
          const dx = pos.centerX - current.centerX
          // Must be in the correct horizontal direction
          if (normX > 0 && dx <= 0) continue
          if (normX < 0 && dx >= 0) continue
          const dist = Math.abs(dx)
          if (dist < bestDist) {
            bestDist = dist
            bestIndex = pos.index
          }
        }
        // Return current index if no filter button in that direction (wall - stay put)
        return bestIndex !== null ? bestIndex : current.index
      }
    }

    // Row tolerance: elements within this Y distance are considered "same row"
    const ROW_TOLERANCE = current.rect.height * 0.8
    // Column tolerance: use larger of current or typical card width for better cross-row navigation
    const COL_TOLERANCE = Math.max(current.rect.width * 1.5, 150)

    // Collect candidates in the correct direction
    const candidates: { index: number; score: number }[] = []

    for (const pos of all) {
      if (pos.index === current.index) continue

      // Vector from current to candidate
      const dx = pos.centerX - current.centerX
      const dy = pos.centerY - current.centerY
      const dist = Math.sqrt(dx * dx + dy * dy)
      if (dist < 1) continue

      // For horizontal movement, candidate must be in the correct horizontal direction
      if (isHorizontal) {
        if (normX > 0 && dx <= 0) continue // Moving right but candidate is left/same
        if (normX < 0 && dx >= 0) continue // Moving left but candidate is right/same
      }

      // For vertical movement, candidate must be in the correct vertical direction
      if (isVertical) {
        if (normY > 0 && dy <= 0) continue // Moving down but candidate is up/same
        if (normY < 0 && dy >= 0) continue // Moving up but candidate is down/same
      }

      // Calculate base score (distance)
      let score = dist

      // STRONG preference for same row when moving horizontally
      if (isHorizontal) {
        const yDiff = Math.abs(dy)
        if (yDiff <= ROW_TOLERANCE) {
          // Same row - big bonus
          score -= 500
        } else {
          // Different row - penalty
          score += yDiff * 3
        }
      }

      // Preference for same column when moving vertically, but not as strict
      if (isVertical) {
        const xDiff = Math.abs(dx)
        if (xDiff <= COL_TOLERANCE) {
          // Same column - bonus (smaller than horizontal to allow cross-column movement)
          score -= 300
        } else {
          // Different column - mild penalty (still allow movement to nearest)
          score += xDiff * 0.5
        }
      }

      candidates.push({ index: pos.index, score })
    }

    // If no candidates found, return null
    if (candidates.length === 0) return null

    // Sort by score and return best
    candidates.sort((a, b) => a.score - b.score)
    return candidates[0].index
  }

  // Navigate in a direction (supports 8 directions)
  function navigate(dirX: number, dirY: number) {
    const positions = getFocusableElements()
    if (positions.length === 0) return

    // Initialize focus if not set
    if (focusedIndex.value < 0 || focusedIndex.value >= positions.length) {
      updateFocus(0)
      return
    }

    const current = positions[focusedIndex.value]
    if (!current) {
      updateFocus(0)
      return
    }

    const nearest = findNearest(current, positions, dirX, dirY)
    if (nearest !== null) {
      updateFocus(nearest)
    } else if (wrap) {
      // Wrap around if no element found in direction
      // For horizontal: wrap to opposite side
      // For vertical: wrap to top/bottom
      if (Math.abs(dirX) > Math.abs(dirY)) {
        // Mostly horizontal
        if (dirX > 0) {
          // Moving right, wrap to leftmost
          const leftmost = positions.reduce((best, p) =>
            p.centerX < best.centerX ? p : best, positions[0])
          updateFocus(leftmost.index)
        } else {
          // Moving left, wrap to rightmost
          const rightmost = positions.reduce((best, p) =>
            p.centerX > best.centerX ? p : best, positions[0])
          updateFocus(rightmost.index)
        }
      } else {
        // Mostly vertical
        if (dirY > 0) {
          // Moving down, wrap to topmost
          const topmost = positions.reduce((best, p) =>
            p.centerY < best.centerY ? p : best, positions[0])
          updateFocus(topmost.index)
        } else {
          // Moving up, wrap to bottommost
          const bottommost = positions.reduce((best, p) =>
            p.centerY > best.centerY ? p : best, positions[0])
          updateFocus(bottommost.index)
        }
      }
    }
  }

  // Activate focused element
  function activateFocused() {
    const positions = getFocusableElements()
    if (focusedIndex.value >= 0 && focusedIndex.value < positions.length) {
      const pos = positions[focusedIndex.value]
      pos.el.click()
    }
  }

  // Activate element under cursor
  function activateUnderCursor() {
    const element = document.elementFromPoint(cursorX.value, cursorY.value)
    if (element) {
      // Find the nearest focusable parent or the element itself
      const focusable = element.closest(selector) as HTMLElement
      if (focusable) {
        focusable.click()
      } else {
        // Click whatever is under the cursor
        (element as HTMLElement).click?.()
      }
    }
  }

  // Go back
  function goBack() {
    if (onBack) {
      onBack()
    } else {
      router.back()
    }
  }

  // Create cursor element (No Man's Sky style - circle with center dot)
  function createCursor() {
    if (cursorElement.value) return

    const cursor = document.createElement('div')
    cursor.id = 'gamepad-cursor'
    cursor.innerHTML = `
      <svg width="28" height="28" viewBox="0 0 28 28">
        <circle cx="14" cy="14" r="12" fill="none" stroke="rgba(0, 255, 136, 0.7)" stroke-width="2.5"/>
        <circle cx="14" cy="14" r="2.5" fill="rgba(0, 255, 136, 0.9)"/>
      </svg>
    `
    cursor.style.cssText = `
      position: fixed;
      pointer-events: none;
      z-index: 99999;
      transform: translate(-50%, -50%);
      transition: opacity 0.15s ease;
      filter: drop-shadow(0 0 6px rgba(0, 255, 136, 0.5));
    `
    document.body.appendChild(cursor)
    cursorElement.value = cursor
  }

  // Update cursor position and visibility
  function updateCursor() {
    if (!cursorElement.value) return

    cursorElement.value.style.left = `${cursorX.value}px`
    cursorElement.value.style.top = `${cursorY.value}px`
    cursorElement.value.style.opacity = cursorVisible.value ? '1' : '0'

    // Highlight element under cursor
    if (cursorVisible.value) {
      const element = document.elementFromPoint(cursorX.value, cursorY.value)
      const focusable = element?.closest(selector) as HTMLElement

      // Update focus to element under cursor
      if (focusable) {
        const positions = getFocusableElements()
        const idx = positions.findIndex(p => p.el === focusable)
        if (idx !== -1 && idx !== focusedIndex.value) {
          // Remove old focus
          positions.forEach(p => p.el.classList.remove('gamepad-focused'))
          // Add new focus
          focusable.classList.add('gamepad-focused')
          focusedIndex.value = idx
        }
      }
    }
  }

  // Main update loop
  function updateLoop() {
    const { leftStick, rightStick, buttons } = gamepadStore
    const prev = prevButtons.value
    const prevStick = prevLeftStick.value

    // === D-PAD NAVIGATION ===
    // Check for D-pad with edge detection
    let dpadX = 0
    let dpadY = 0

    if (buttons.DPadRight && !prev.DPadRight) dpadX = 1
    if (buttons.DPadLeft && !prev.DPadLeft) dpadX = -1
    if (buttons.DPadDown && !prev.DPadDown) dpadY = 1
    if (buttons.DPadUp && !prev.DPadUp) dpadY = -1

    // Diagonals from D-pad (held state)
    if (dpadX === 0 && dpadY === 0) {
      // Check for diagonal combinations on button press
      if (buttons.DPadRight && buttons.DPadUp && (!prev.DPadRight || !prev.DPadUp)) {
        dpadX = 1; dpadY = -1
      } else if (buttons.DPadRight && buttons.DPadDown && (!prev.DPadRight || !prev.DPadDown)) {
        dpadX = 1; dpadY = 1
      } else if (buttons.DPadLeft && buttons.DPadUp && (!prev.DPadLeft || !prev.DPadUp)) {
        dpadX = -1; dpadY = -1
      } else if (buttons.DPadLeft && buttons.DPadDown && (!prev.DPadLeft || !prev.DPadDown)) {
        dpadX = -1; dpadY = 1
      }
    }

    if ((dpadX !== 0 || dpadY !== 0)) {
      navigate(dpadX, dpadY)
    }

    // === LEFT STICK NAVIGATION (D-pad equivalent) ===
    const stickX = leftStick.x
    const stickY = leftStick.y
    const stickMag = Math.sqrt(stickX * stickX + stickY * stickY)

    // Check if stick just crossed threshold (edge detection for stick)
    const prevMag = Math.sqrt(prevStick.x * prevStick.x + prevStick.y * prevStick.y)
    const justCrossedThreshold = stickMag >= STICK_NAV_THRESHOLD && prevMag < STICK_NAV_THRESHOLD

    // INSTANT navigation when threshold crossed - no cooldown!
    if (justCrossedThreshold) {
      const normX = stickX / stickMag
      const normY = stickY / stickMag
      navigate(normX, normY)
    }

    // === RIGHT STICK CURSOR (No Man's Sky style) ===
    if (enableCursor) {
      const cursorStickX = rightStick.x
      const cursorStickY = rightStick.y
      const cursorMag = Math.sqrt(cursorStickX * cursorStickX + cursorStickY * cursorStickY)

      if (cursorMag > STICK_DEADZONE) {
        // Show cursor when right stick is used
        cursorVisible.value = true

        // Speed is proportional to deflection (with deadzone remapping)
        const adjustedMag = (cursorMag - STICK_DEADZONE) / (1 - STICK_DEADZONE)
        const speed = CURSOR_BASE_SPEED * adjustedMag * adjustedMag * cursorSpeed // Quadratic for better feel

        // Move cursor
        cursorX.value = Math.max(0, Math.min(window.innerWidth,
          cursorX.value + (cursorStickX / cursorMag) * speed * adjustedMag))
        cursorY.value = Math.max(0, Math.min(window.innerHeight,
          cursorY.value + (cursorStickY / cursorMag) * speed * adjustedMag))

        updateCursor()
      }
    }

    // === A BUTTON: Activate ===
    if (buttons.A && !prev.A) {
      if (cursorVisible.value) {
        activateUnderCursor()
      } else {
        activateFocused()
      }
    }

    // === B BUTTON: Back ===
    if (buttons.B && !prev.B) {
      goBack()
    }

    // Store previous state
    prevButtons.value = { ...buttons }
    prevLeftStick.value = { x: stickX, y: stickY }

    // Continue loop
    animationFrameId = requestAnimationFrame(updateLoop)
  }

  // Keyboard support
  function handleKeydown(e: KeyboardEvent) {
    // Don't interfere with typing in inputs
    if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
      return
    }

    switch (e.key) {
      case 'ArrowUp':
      case 'w':
      case 'W':
        e.preventDefault()
        navigate(0, -1)
        break
      case 'ArrowDown':
      case 's':
      case 'S':
        e.preventDefault()
        navigate(0, 1)
        break
      case 'ArrowLeft':
      case 'a':
      case 'A':
        e.preventDefault()
        navigate(-1, 0)
        break
      case 'ArrowRight':
      case 'd':
      case 'D':
        e.preventDefault()
        navigate(1, 0)
        break
      case 'Enter':
      case ' ':
        e.preventDefault()
        activateFocused()
        break
      case 'Escape':
        e.preventDefault()
        goBack()
        break
    }
  }

  onMounted(() => {
    window.addEventListener('keydown', handleKeydown)

    // Create cursor element
    if (enableCursor) {
      createCursor()
    }

    // Start update loop
    animationFrameId = requestAnimationFrame(updateLoop)

    // Initialize focus on first element after a tick
    nextTick(() => {
      const positions = getFocusableElements()
      if (positions.length > 0) {
        updateFocus(0)
      }
    })
  })

  onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown)

    // Clean up animation frame
    if (animationFrameId !== null) {
      cancelAnimationFrame(animationFrameId)
    }

    // Clean up cursor
    if (cursorElement.value) {
      cursorElement.value.remove()
      cursorElement.value = null
    }

    // Clean up focus classes
    const positions = getFocusableElements()
    positions.forEach(p => p.el.classList.remove('gamepad-focused'))
  })

  return {
    focusedIndex,
    cursorX,
    cursorY,
    cursorVisible,
    navigate,
    activateFocused,
    goBack,
    updateFocus,
  }
}
