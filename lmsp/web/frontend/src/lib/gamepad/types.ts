/**
 * Gamepad Module - Type Definitions
 * ==================================
 *
 * Unified types for cross-controller gamepad input handling.
 * All controllers map to this canonical representation.
 */

/**
 * Canonical button names - the unified representation all controllers map to.
 * Based on Xbox layout naming (most common reference).
 */
export type CanonicalButton =
  | 'A' | 'B' | 'X' | 'Y'           // Face buttons
  | 'LB' | 'RB'                     // Bumpers
  | 'LT' | 'RT'                     // Triggers (digital press)
  | 'Back' | 'Start'                // Menu buttons
  | 'L3' | 'R3'                     // Stick clicks
  | 'DPadUp' | 'DPadDown' | 'DPadLeft' | 'DPadRight'
  | 'Home' | 'Share' | 'Touchpad'   // Special buttons

/**
 * Canonical axis names - unified stick/trigger representation.
 */
export type CanonicalAxis =
  | 'LeftStickX' | 'LeftStickY'
  | 'RightStickX' | 'RightStickY'
  | 'LeftTrigger' | 'RightTrigger'

/**
 * Unified gamepad state - what the application sees.
 * All controller-specific quirks are hidden behind this interface.
 */
export interface UnifiedGamepadState {
  connected: boolean
  id: string                        // Raw controller ID string
  profileName: string               // Detected profile name

  // Analog sticks (-1 to 1, with deadzone applied)
  leftStick: { x: number; y: number }
  rightStick: { x: number; y: number }

  // Analog triggers (0 to 1, with deadzone applied)
  leftTrigger: number
  rightTrigger: number

  // Digital button states
  buttons: Record<CanonicalButton, boolean>

  // Timestamp of last update
  timestamp: number
}

/**
 * Raw axis mapping - describes how a controller reports an axis.
 */
export interface AxisMapping {
  index: number                     // Gamepad.axes index
  inverted?: boolean                // Flip sign
  // Range conversion: some report -1..1, others 0..1
  range: 'minusOneToOne' | 'zeroToOne' | 'negativeOneReleased'
  deadzone?: number                 // Override default deadzone
}

/**
 * Raw button mapping - describes how a controller reports a button.
 */
export interface ButtonMapping {
  index: number                     // Gamepad.buttons index
  // Some triggers report as buttons with analog value
  analogThreshold?: number          // Treat as pressed above this value
}

/**
 * Controller profile - complete mapping for a specific controller type.
 */
export interface ControllerProfile {
  name: string
  // Patterns to match against Gamepad.id
  match: {
    patterns: RegExp[]
    // Vendor/product IDs (hex strings from Gamepad.id)
    vendorIds?: string[]
    productIds?: string[]
  }

  // Axis mappings (null means not available on this controller)
  axes: {
    leftStickX: AxisMapping | null
    leftStickY: AxisMapping | null
    rightStickX: AxisMapping | null
    rightStickY: AxisMapping | null
    leftTrigger: AxisMapping | null
    rightTrigger: AxisMapping | null
  }

  // Button mappings
  buttons: Partial<Record<CanonicalButton, ButtonMapping>>

  // Special handling flags
  quirks?: {
    // Some controllers swap X/Y button positions
    swapXY?: boolean
    // Some report triggers only as buttons, not axes
    triggersAreButtons?: boolean
    // D-pad reported as axes instead of buttons
    dpadOnAxes?: { axisX: number; axisY: number }
  }
}

/**
 * Default deadzones - can be overridden per-axis in profiles.
 */
export const DEFAULT_DEADZONE = {
  stick: 0.15,
  trigger: 0.05,
}

/**
 * Creates an empty unified state (all zeros, disconnected).
 */
export function createEmptyState(): UnifiedGamepadState {
  return {
    connected: false,
    id: '',
    profileName: 'None',
    leftStick: { x: 0, y: 0 },
    rightStick: { x: 0, y: 0 },
    leftTrigger: 0,
    rightTrigger: 0,
    buttons: {
      A: false, B: false, X: false, Y: false,
      LB: false, RB: false, LT: false, RT: false,
      Back: false, Start: false,
      L3: false, R3: false,
      DPadUp: false, DPadDown: false, DPadLeft: false, DPadRight: false,
      Home: false, Share: false, Touchpad: false,
    },
    timestamp: 0,
  }
}
