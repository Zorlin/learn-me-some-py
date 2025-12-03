/**
 * Gamepad Module - Input Mapper
 * ==============================
 *
 * Maps raw gamepad input to unified canonical representation.
 * Handles axis normalization, deadzones, and button mapping.
 */

import type {
  ControllerProfile,
  AxisMapping,
  ButtonMapping,
  UnifiedGamepadState,
  CanonicalButton,
} from './types'
import { DEFAULT_DEADZONE, createEmptyState } from './types'

/**
 * Apply deadzone to an axis value.
 * Returns 0 if within deadzone, otherwise rescales to 0-1 range.
 */
export function applyDeadzone(value: number, deadzone: number): number {
  const absValue = Math.abs(value)
  if (absValue < deadzone) return 0

  const sign = Math.sign(value)
  // Rescale: deadzone..1 -> 0..1
  return sign * (absValue - deadzone) / (1 - deadzone)
}

/**
 * Normalize axis value based on its range type.
 */
export function normalizeAxisValue(raw: number, mapping: AxisMapping): number {
  let value = raw

  // Handle different range types
  switch (mapping.range) {
    case 'minusOneToOne':
      // Already normalized
      break
    case 'zeroToOne':
      // Convert 0..1 to -1..1 or keep as 0..1 for triggers
      break
    case 'negativeOneReleased':
      // -1 = released, +1 = pressed -> convert to 0..1
      value = (raw + 1) / 2
      break
  }

  // Apply inversion if needed
  if (mapping.inverted) {
    value = -value
  }

  return value
}

/**
 * Read a stick axis pair from raw gamepad.
 */
export function readStick(
  gamepad: Gamepad,
  xMapping: AxisMapping | null,
  yMapping: AxisMapping | null,
  deadzone: number = DEFAULT_DEADZONE.stick
): { x: number; y: number } {
  let x = 0
  let y = 0

  if (xMapping && gamepad.axes.length > xMapping.index) {
    const raw = gamepad.axes[xMapping.index]
    x = normalizeAxisValue(raw, xMapping)
  }

  if (yMapping && gamepad.axes.length > yMapping.index) {
    const raw = gamepad.axes[yMapping.index]
    y = normalizeAxisValue(raw, yMapping)
  }

  // Apply radial deadzone (treats stick as circle, not square)
  const magnitude = Math.sqrt(x * x + y * y)
  if (magnitude < deadzone) {
    return { x: 0, y: 0 }
  }

  // Rescale outside deadzone
  const scale = (magnitude - deadzone) / (1 - deadzone) / magnitude
  return { x: x * scale, y: y * scale }
}

/**
 * Read a trigger value from raw gamepad.
 * Checks both axis and button sources, returns higher value.
 */
export function readTrigger(
  gamepad: Gamepad,
  axisMapping: AxisMapping | null,
  buttonMapping: ButtonMapping | undefined,
  deadzone: number = DEFAULT_DEADZONE.trigger
): number {
  let value = 0

  // Try axis first
  if (axisMapping && gamepad.axes.length > axisMapping.index) {
    const raw = gamepad.axes[axisMapping.index]
    const axisDeadzone = axisMapping.deadzone ?? deadzone
    value = applyDeadzone(normalizeAxisValue(raw, axisMapping), axisDeadzone)
  }

  // Try button (may have analog value)
  if (buttonMapping && gamepad.buttons.length > buttonMapping.index) {
    const button = gamepad.buttons[buttonMapping.index]
    const buttonValue = button.value ?? (button.pressed ? 1 : 0)
    value = Math.max(value, applyDeadzone(buttonValue, deadzone))
  }

  return Math.min(1, Math.max(0, value))
}

/**
 * Read a button state from raw gamepad.
 */
export function readButton(
  gamepad: Gamepad,
  mapping: ButtonMapping | undefined
): boolean {
  if (!mapping || gamepad.buttons.length <= mapping.index) {
    return false
  }

  const button = gamepad.buttons[mapping.index]

  // For analog buttons (triggers), check threshold
  if (mapping.analogThreshold !== undefined) {
    return (button.value ?? 0) >= mapping.analogThreshold
  }

  return button.pressed
}

/**
 * Map raw gamepad state to unified representation.
 */
export function mapGamepad(
  gamepad: Gamepad,
  profile: ControllerProfile
): UnifiedGamepadState {
  const state = createEmptyState()
  state.connected = true
  state.id = gamepad.id
  state.profileName = profile.name
  state.timestamp = gamepad.timestamp

  // Map sticks
  state.leftStick = readStick(
    gamepad,
    profile.axes.leftStickX,
    profile.axes.leftStickY
  )
  state.rightStick = readStick(
    gamepad,
    profile.axes.rightStickX,
    profile.axes.rightStickY
  )

  // Map triggers
  state.leftTrigger = readTrigger(
    gamepad,
    profile.axes.leftTrigger,
    profile.buttons.LT
  )
  state.rightTrigger = readTrigger(
    gamepad,
    profile.axes.rightTrigger,
    profile.buttons.RT
  )

  // Map all buttons
  const buttonNames: CanonicalButton[] = [
    'A', 'B', 'X', 'Y',
    'LB', 'RB', 'LT', 'RT',
    'Back', 'Start',
    'L3', 'R3',
    'DPadUp', 'DPadDown', 'DPadLeft', 'DPadRight',
    'Home', 'Share', 'Touchpad',
  ]

  for (const name of buttonNames) {
    state.buttons[name] = readButton(gamepad, profile.buttons[name])
  }

  // Handle D-pad on axes quirk
  if (profile.quirks?.dpadOnAxes) {
    const { axisX, axisY } = profile.quirks.dpadOnAxes
    if (gamepad.axes.length > axisX) {
      const x = gamepad.axes[axisX]
      state.buttons.DPadLeft = x < -0.5
      state.buttons.DPadRight = x > 0.5
    }
    if (gamepad.axes.length > axisY) {
      const y = gamepad.axes[axisY]
      state.buttons.DPadUp = y < -0.5
      state.buttons.DPadDown = y > 0.5
    }
  }

  // Trigger buttons from analog trigger values
  if (!profile.quirks?.triggersAreButtons) {
    state.buttons.LT = state.leftTrigger > 0.5
    state.buttons.RT = state.rightTrigger > 0.5
  }

  return state
}

/**
 * Create a mapper function bound to a specific profile.
 */
export function createMapper(profile: ControllerProfile) {
  return (gamepad: Gamepad) => mapGamepad(gamepad, profile)
}
