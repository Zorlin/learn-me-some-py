/**
 * Gamepad Module - Controller Profiles
 * =====================================
 *
 * Database of controller profiles mapping raw inputs to canonical form.
 * Each profile describes how a specific controller type reports its inputs.
 *
 * References:
 * - https://github.com/nicmeo/gamepad-viewer (visual diagrams)
 * - https://gamepad-tester.com/ (for testing raw values)
 * - W3C Gamepad spec: https://w3c.github.io/gamepad/#remapping
 */

import type { ControllerProfile, AxisMapping, ButtonMapping } from './types'

// Standard W3C mapping indices (reference)
// Buttons: 0=A, 1=B, 2=X, 3=Y, 4=LB, 5=RB, 6=LT, 7=RT, 8=Back, 9=Start, 10=L3, 11=R3, 12-15=DPad, 16=Home
// Axes: 0=LS_X, 1=LS_Y, 2=RS_X, 3=RS_Y

/**
 * Standard profile - W3C standard gamepad mapping.
 * Used as fallback and for compliant controllers.
 */
export const STANDARD_PROFILE: ControllerProfile = {
  name: 'Standard',
  match: {
    patterns: [/standard/i],
  },
  axes: {
    leftStickX: { index: 0, range: 'minusOneToOne' },
    leftStickY: { index: 1, range: 'minusOneToOne' },
    rightStickX: { index: 2, range: 'minusOneToOne' },
    rightStickY: { index: 3, range: 'minusOneToOne' },
    leftTrigger: null,  // Standard uses buttons for triggers
    rightTrigger: null,
  },
  buttons: {
    A: { index: 0 },
    B: { index: 1 },
    X: { index: 2 },
    Y: { index: 3 },
    LB: { index: 4 },
    RB: { index: 5 },
    LT: { index: 6, analogThreshold: 0.5 },
    RT: { index: 7, analogThreshold: 0.5 },
    Back: { index: 8 },
    Start: { index: 9 },
    L3: { index: 10 },
    R3: { index: 11 },
    DPadUp: { index: 12 },
    DPadDown: { index: 13 },
    DPadLeft: { index: 14 },
    DPadRight: { index: 15 },
    Home: { index: 16 },
  },
  quirks: {
    triggersAreButtons: true,
  },
}

/**
 * Xbox One / Series X|S controllers (XInput).
 * Triggers are on axes, not buttons.
 */
export const XBOX_PROFILE: ControllerProfile = {
  name: 'Xbox',
  match: {
    patterns: [/xbox/i, /xinput/i, /microsoft/i],
    vendorIds: ['045e', '0e6f', '0f0d', '1430', '146b', '1532', '1bad', '24c6'],
  },
  axes: {
    leftStickX: { index: 0, range: 'minusOneToOne' },
    leftStickY: { index: 1, range: 'minusOneToOne' },
    rightStickX: { index: 2, range: 'minusOneToOne' },
    rightStickY: { index: 3, range: 'minusOneToOne' },
    // Xbox triggers are buttons with analog values, not axes
    leftTrigger: null,
    rightTrigger: null,
  },
  buttons: {
    A: { index: 0 },
    B: { index: 1 },
    X: { index: 2 },
    Y: { index: 3 },
    LB: { index: 4 },
    RB: { index: 5 },
    LT: { index: 6, analogThreshold: 0.1 },
    RT: { index: 7, analogThreshold: 0.1 },
    Back: { index: 8 },
    Start: { index: 9 },
    L3: { index: 10 },
    R3: { index: 11 },
    DPadUp: { index: 12 },
    DPadDown: { index: 13 },
    DPadLeft: { index: 14 },
    DPadRight: { index: 15 },
    Home: { index: 16 },
    Share: { index: 17 },
  },
  quirks: {
    triggersAreButtons: true,
  },
}

/**
 * 8BitDo controllers in XInput mode.
 * These report triggers on AXES, not buttons!
 *
 * From user testing: "8BitDo Ultimate 2C Wireless" has 8 axes, 11 buttons
 * Axis layout (confirmed via user testing):
 *   0 = Left Stick X
 *   1 = Left Stick Y
 *   2 = Left Trigger (-1 released, +1 pressed)
 *   3 = Right Stick X
 *   4 = Right Stick Y
 *   5 = Right Trigger (-1 released, +1 pressed)
 *   6,7 = D-pad or unused
 */
export const BITDO_XINPUT_PROFILE: ControllerProfile = {
  name: '8BitDo XInput',
  match: {
    patterns: [/8bitdo/i, /8bit.*do/i],
    vendorIds: ['2dc8', '2dc9'],
  },
  axes: {
    leftStickX: { index: 0, range: 'minusOneToOne' },
    leftStickY: { index: 1, range: 'minusOneToOne' },
    rightStickX: { index: 3, range: 'minusOneToOne' },
    rightStickY: { index: 4, range: 'minusOneToOne' },
    leftTrigger: { index: 2, range: 'negativeOneReleased' },
    rightTrigger: { index: 5, range: 'negativeOneReleased' },
  },
  buttons: {
    A: { index: 0 },
    B: { index: 1 },
    X: { index: 2 },
    Y: { index: 3 },
    LB: { index: 4 },
    RB: { index: 5 },
    // LT/RT as buttons might not have analog - axes are primary
    LT: { index: 6 },
    RT: { index: 7 },
    Back: { index: 8 },
    Start: { index: 9 },
    L3: { index: 10 },
    R3: { index: 11 },
    DPadUp: { index: 12 },
    DPadDown: { index: 13 },
    DPadLeft: { index: 14 },
    DPadRight: { index: 15 },
    Home: { index: 16 },
  },
}

/**
 * 8BitDo Pro 2 - same layout as other 8BitDo XInput controllers.
 */
export const BITDO_PRO2_PROFILE: ControllerProfile = {
  name: '8BitDo Pro 2',
  match: {
    patterns: [/8bitdo.*pro\s*2/i, /pro\s*2.*8bitdo/i],
    vendorIds: ['2dc8'],
    productIds: ['6003'],
  },
  axes: {
    leftStickX: { index: 0, range: 'minusOneToOne' },
    leftStickY: { index: 1, range: 'minusOneToOne' },
    rightStickX: { index: 3, range: 'minusOneToOne' },
    rightStickY: { index: 4, range: 'minusOneToOne' },
    leftTrigger: { index: 2, range: 'negativeOneReleased' },
    rightTrigger: { index: 5, range: 'negativeOneReleased' },
  },
  buttons: {
    A: { index: 0 },
    B: { index: 1 },
    X: { index: 2 },
    Y: { index: 3 },
    LB: { index: 4 },
    RB: { index: 5 },
    LT: { index: 6 },
    RT: { index: 7 },
    Back: { index: 8 },
    Start: { index: 9 },
    L3: { index: 10 },
    R3: { index: 11 },
    DPadUp: { index: 12 },
    DPadDown: { index: 13 },
    DPadLeft: { index: 14 },
    DPadRight: { index: 15 },
    Home: { index: 16 },
  },
}

/**
 * PlayStation DualShock 4 / DualSense.
 * Has touchpad button and triggers as analog buttons.
 */
export const PLAYSTATION_PROFILE: ControllerProfile = {
  name: 'PlayStation',
  match: {
    patterns: [/playstation/i, /dualshock/i, /dualsense/i, /ps[345]/i, /sony/i],
    vendorIds: ['054c'],
  },
  axes: {
    leftStickX: { index: 0, range: 'minusOneToOne' },
    leftStickY: { index: 1, range: 'minusOneToOne' },
    rightStickX: { index: 2, range: 'minusOneToOne' },
    rightStickY: { index: 3, range: 'minusOneToOne' },
    leftTrigger: null,  // PS uses buttons with analog value
    rightTrigger: null,
  },
  buttons: {
    // PS layout: Cross=A, Circle=B, Square=X, Triangle=Y
    A: { index: 0 },      // Cross
    B: { index: 1 },      // Circle
    X: { index: 2 },      // Square
    Y: { index: 3 },      // Triangle
    LB: { index: 4 },     // L1
    RB: { index: 5 },     // R1
    LT: { index: 6, analogThreshold: 0.1 },  // L2
    RT: { index: 7, analogThreshold: 0.1 },  // R2
    Back: { index: 8 },   // Share/Create
    Start: { index: 9 },  // Options
    L3: { index: 10 },
    R3: { index: 11 },
    DPadUp: { index: 12 },
    DPadDown: { index: 13 },
    DPadLeft: { index: 14 },
    DPadRight: { index: 15 },
    Home: { index: 16 },  // PS button
    Touchpad: { index: 17 },
  },
  quirks: {
    triggersAreButtons: true,
  },
}

/**
 * Nintendo Switch Pro Controller.
 * Button layout differs from Xbox (A/B and X/Y swapped physically).
 */
export const NINTENDO_PRO_PROFILE: ControllerProfile = {
  name: 'Nintendo Pro',
  match: {
    patterns: [/nintendo/i, /switch.*pro/i, /pro.*controller/i],
    vendorIds: ['057e'],
  },
  axes: {
    leftStickX: { index: 0, range: 'minusOneToOne' },
    leftStickY: { index: 1, range: 'minusOneToOne' },
    rightStickX: { index: 2, range: 'minusOneToOne' },
    rightStickY: { index: 3, range: 'minusOneToOne' },
    leftTrigger: null,  // Digital triggers
    rightTrigger: null,
  },
  buttons: {
    // Nintendo physical layout is different but W3C maps to Xbox positions
    // So index 0 is still "A" (East button), etc.
    A: { index: 0 },
    B: { index: 1 },
    X: { index: 2 },
    Y: { index: 3 },
    LB: { index: 4 },   // L
    RB: { index: 5 },   // R
    LT: { index: 6 },   // ZL (digital)
    RT: { index: 7 },   // ZR (digital)
    Back: { index: 8 }, // Minus
    Start: { index: 9 }, // Plus
    L3: { index: 10 },
    R3: { index: 11 },
    DPadUp: { index: 12 },
    DPadDown: { index: 13 },
    DPadLeft: { index: 14 },
    DPadRight: { index: 15 },
    Home: { index: 16 },
    Share: { index: 17 }, // Capture
  },
}

/**
 * Generic / Unknown controllers.
 * Falls back to W3C standard mapping.
 */
export const GENERIC_PROFILE: ControllerProfile = {
  ...STANDARD_PROFILE,
  name: 'Generic',
  match: {
    patterns: [/.*/],  // Matches anything (lowest priority)
  },
}

/**
 * All profiles in priority order (most specific first).
 */
export const PROFILES: ControllerProfile[] = [
  BITDO_PRO2_PROFILE,     // Specific 8BitDo model
  BITDO_XINPUT_PROFILE,   // General 8BitDo
  XBOX_PROFILE,
  PLAYSTATION_PROFILE,
  NINTENDO_PRO_PROFILE,
  STANDARD_PROFILE,
  GENERIC_PROFILE,        // Fallback (always last)
]
