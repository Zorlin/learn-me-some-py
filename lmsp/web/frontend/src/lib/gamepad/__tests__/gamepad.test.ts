/**
 * Gamepad Module Tests
 * =====================
 *
 * Comprehensive tests for controller profile detection and input mapping.
 */

import { describe, it, expect } from 'vitest'
import { parseIds, profileMatches, detectProfile, debugDetection } from '../detector'
import { applyDeadzone, normalizeAxisValue, readTrigger, mapGamepad } from '../mapper'
import { createEmptyState } from '../types'
import {
  STANDARD_PROFILE,
  XBOX_PROFILE,
  PLAYSTATION_PROFILE,
  BITDO_XINPUT_PROFILE,
  GENERIC_PROFILE,
} from '../profiles'

// Mock gamepad factory
function createMockGamepad(overrides: Partial<Gamepad> = {}): Gamepad {
  return {
    id: 'Test Controller (Vendor: 0000 Product: 0000)',
    index: 0,
    connected: true,
    timestamp: Date.now(),
    mapping: 'standard',
    axes: [0, 0, 0, 0],
    buttons: Array(17).fill(null).map(() => ({
      pressed: false,
      touched: false,
      value: 0,
    })),
    hapticActuators: [],
    vibrationActuator: null,
    ...overrides,
  } as Gamepad
}

describe('Detector', () => {
  describe('parseIds', () => {
    it('parses Chrome format vendor/product IDs', () => {
      const result = parseIds('Xbox Controller (STANDARD GAMEPAD Vendor: 045e Product: 02fd)')
      expect(result.vendor).toBe('045e')
      expect(result.product).toBe('02fd')
    })

    it('parses Firefox format vendor/product IDs', () => {
      const result = parseIds('045e-02fd-Xbox Controller')
      expect(result.vendor).toBe('045e')
      expect(result.product).toBe('02fd')
    })

    it('handles lowercase', () => {
      const result = parseIds('Vendor: 054C Product: 09CC')
      expect(result.vendor).toBe('054c')
      expect(result.product).toBe('09cc')
    })

    it('returns empty for unknown format', () => {
      const result = parseIds('Generic USB Joystick')
      expect(result.vendor).toBeUndefined()
      expect(result.product).toBeUndefined()
    })
  })

  describe('profileMatches', () => {
    it('matches Xbox controller by pattern', () => {
      expect(profileMatches(XBOX_PROFILE, 'Xbox Controller (STANDARD GAMEPAD)')).toBe(true)
    })

    it('matches 8BitDo controller', () => {
      expect(profileMatches(
        BITDO_XINPUT_PROFILE,
        '8BitDo 8BitDo Ultimate 2C Wireless Controller (Vendor: 2dc8 Product: 310a)'
      )).toBe(true)
    })

    it('matches PlayStation controller', () => {
      expect(profileMatches(PLAYSTATION_PROFILE, 'DualSense Wireless Controller')).toBe(true)
      expect(profileMatches(PLAYSTATION_PROFILE, 'Sony DualShock 4')).toBe(true)
    })

    it('matches by vendor ID', () => {
      expect(profileMatches(XBOX_PROFILE, 'Unknown (Vendor: 045e Product: ffff)')).toBe(true)
    })

    it('generic matches anything', () => {
      expect(profileMatches(GENERIC_PROFILE, 'Random Controller XYZ')).toBe(true)
    })
  })

  describe('detectProfile', () => {
    it('detects Xbox controller', () => {
      const gp = createMockGamepad({ id: 'Xbox Wireless Controller' })
      const profile = detectProfile(gp)
      expect(profile.name).toBe('Xbox')
    })

    it('detects 8BitDo controller', () => {
      const gp = createMockGamepad({
        id: '8BitDo 8BitDo Ultimate 2C Wireless Controller (Vendor: 2dc8 Product: 310a)',
        axes: [0, 0, 0, 0, 0, 0, 0, 0],
      })
      const profile = detectProfile(gp)
      // Any 8BitDo profile is correct - specific model detection may vary
      expect(profile.name).toMatch(/8BitDo/)
    })

    it('detects PlayStation controller', () => {
      const gp = createMockGamepad({ id: 'DualSense Wireless Controller' })
      const profile = detectProfile(gp)
      expect(profile.name).toBe('PlayStation')
    })

    it('falls back to Generic for unknown', () => {
      const gp = createMockGamepad({ id: 'Totally Unknown Controller' })
      const profile = detectProfile(gp)
      expect(profile.name).toBe('Generic')
    })
  })

  describe('debugDetection', () => {
    it('shows all profile matches', () => {
      const results = debugDetection('Xbox Wireless Controller')
      const xboxResult = results.find(r => r.profile === 'Xbox')
      expect(xboxResult?.matched).toBe(true)

      const psResult = results.find(r => r.profile === 'PlayStation')
      expect(psResult?.matched).toBe(false)
    })
  })
})

describe('Mapper', () => {
  describe('applyDeadzone', () => {
    it('returns 0 for values within deadzone', () => {
      expect(applyDeadzone(0.1, 0.15)).toBe(0)
      expect(applyDeadzone(-0.1, 0.15)).toBe(0)
      expect(applyDeadzone(0, 0.15)).toBe(0)
    })

    it('rescales values outside deadzone', () => {
      // With 0.15 deadzone, value of 0.575 should map to ~0.5
      const result = applyDeadzone(0.575, 0.15)
      expect(result).toBeCloseTo(0.5, 1)
    })

    it('preserves full deflection', () => {
      expect(applyDeadzone(1, 0.15)).toBeCloseTo(1, 2)
      expect(applyDeadzone(-1, 0.15)).toBeCloseTo(-1, 2)
    })
  })

  describe('normalizeAxisValue', () => {
    it('handles minusOneToOne range', () => {
      const mapping = { index: 0, range: 'minusOneToOne' as const }
      expect(normalizeAxisValue(0.5, mapping)).toBe(0.5)
      expect(normalizeAxisValue(-0.5, mapping)).toBe(-0.5)
    })

    it('handles negativeOneReleased range (8BitDo triggers)', () => {
      const mapping = { index: 0, range: 'negativeOneReleased' as const }
      // -1 (released) -> 0
      expect(normalizeAxisValue(-1, mapping)).toBe(0)
      // +1 (pressed) -> 1
      expect(normalizeAxisValue(1, mapping)).toBe(1)
      // 0 (half pressed) -> 0.5
      expect(normalizeAxisValue(0, mapping)).toBe(0.5)
    })

    it('handles inverted axes', () => {
      const mapping = { index: 0, range: 'minusOneToOne' as const, inverted: true }
      expect(normalizeAxisValue(0.5, mapping)).toBe(-0.5)
    })
  })

  describe('readTrigger', () => {
    it('reads from axis when available', () => {
      const gp = createMockGamepad({ axes: [0, 0, 1, 0, 0, 0] })
      const axisMapping = { index: 2, range: 'negativeOneReleased' as const }
      const result = readTrigger(gp, axisMapping, undefined)
      expect(result).toBe(1)
    })

    it('reads from button when axis not available', () => {
      const buttons = Array(17).fill(null).map(() => ({
        pressed: false, touched: false, value: 0,
      }))
      buttons[6] = { pressed: true, touched: true, value: 0.75 }
      const gp = createMockGamepad({ buttons })

      const buttonMapping = { index: 6 }
      const result = readTrigger(gp, null, buttonMapping)
      expect(result).toBeCloseTo(0.75, 1)
    })

    it('uses higher value when both available', () => {
      const buttons = Array(17).fill(null).map(() => ({
        pressed: false, touched: false, value: 0,
      }))
      buttons[6] = { pressed: true, touched: true, value: 0.3 }
      const gp = createMockGamepad({
        axes: [0, 0, 0.5, 0], // Axis 2 = 0.5 after normalization
        buttons,
      })

      const axisMapping = { index: 2, range: 'zeroToOne' as const }
      const buttonMapping = { index: 6 }
      const result = readTrigger(gp, axisMapping, buttonMapping)
      expect(result).toBeCloseTo(0.5, 1) // Axis value wins
    })
  })

  describe('mapGamepad', () => {
    it('maps standard controller correctly', () => {
      const buttons = Array(17).fill(null).map(() => ({
        pressed: false, touched: false, value: 0,
      }))
      buttons[0] = { pressed: true, touched: true, value: 1 } // A
      buttons[12] = { pressed: true, touched: true, value: 1 } // DPadUp

      const gp = createMockGamepad({
        id: 'Standard Gamepad',
        axes: [0.5, -0.3, 0.2, 0.1],
        buttons,
      })

      const state = mapGamepad(gp, STANDARD_PROFILE)

      expect(state.connected).toBe(true)
      expect(state.profileName).toBe('Standard')
      expect(state.buttons.A).toBe(true)
      expect(state.buttons.DPadUp).toBe(true)
      expect(state.buttons.B).toBe(false)
    })

    it('maps 8BitDo triggers from axes correctly', () => {
      // 8BitDo: LT on axis 2, RT on axis 5
      // Range: -1 (released) to +1 (pressed)
      const gp = createMockGamepad({
        id: '8BitDo Controller',
        axes: [0, 0, 1, 0, 0, -1, 0, 0], // LT fully pressed (axis 2=1), RT released (axis 5=-1)
      })

      const state = mapGamepad(gp, BITDO_XINPUT_PROFILE)

      expect(state.leftTrigger).toBe(1)
      expect(state.rightTrigger).toBe(0)
    })

    it('maps 8BitDo trigger partial press', () => {
      // Axis 2 at 0 = half pressed (range -1 to 1)
      const gp = createMockGamepad({
        id: '8BitDo Controller',
        axes: [0, 0, 0, 0, 0, 0, 0, 0],
      })

      const state = mapGamepad(gp, BITDO_XINPUT_PROFILE)

      // 0 in range -1..1 normalizes to 0.5
      expect(state.leftTrigger).toBeCloseTo(0.5, 1)
    })
  })
})

describe('Types', () => {
  describe('createEmptyState', () => {
    it('creates disconnected state', () => {
      const state = createEmptyState()
      expect(state.connected).toBe(false)
    })

    it('has all buttons set to false', () => {
      const state = createEmptyState()
      expect(state.buttons.A).toBe(false)
      expect(state.buttons.B).toBe(false)
      expect(state.buttons.LT).toBe(false)
      expect(state.buttons.DPadUp).toBe(false)
    })

    it('has sticks at zero', () => {
      const state = createEmptyState()
      expect(state.leftStick.x).toBe(0)
      expect(state.leftStick.y).toBe(0)
      expect(state.rightStick.x).toBe(0)
      expect(state.rightStick.y).toBe(0)
    })

    it('has triggers at zero', () => {
      const state = createEmptyState()
      expect(state.leftTrigger).toBe(0)
      expect(state.rightTrigger).toBe(0)
    })
  })
})
