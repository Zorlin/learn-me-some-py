/**
 * Gamepad Module - Profile Detection
 * ====================================
 *
 * Detects the correct profile for a connected gamepad.
 * Uses pattern matching on controller ID string and vendor/product IDs.
 */

import type { ControllerProfile } from './types'
import { PROFILES, GENERIC_PROFILE } from './profiles'

/**
 * Parse vendor/product IDs from gamepad ID string.
 * Format varies by browser:
 * - Chrome: "Xbox Controller (STANDARD GAMEPAD Vendor: 045e Product: 02fd)"
 * - Firefox: "045e-02fd-Xbox Controller"
 */
export function parseIds(gamepadId: string): { vendor?: string; product?: string } {
  // Chrome format: "Vendor: XXXX Product: XXXX"
  const chromeMatch = gamepadId.match(/vendor:\s*([0-9a-f]{4})\s*product:\s*([0-9a-f]{4})/i)
  if (chromeMatch) {
    return { vendor: chromeMatch[1].toLowerCase(), product: chromeMatch[2].toLowerCase() }
  }

  // Firefox format: "XXXX-XXXX-Name"
  const firefoxMatch = gamepadId.match(/^([0-9a-f]{4})-([0-9a-f]{4})-/i)
  if (firefoxMatch) {
    return { vendor: firefoxMatch[1].toLowerCase(), product: firefoxMatch[2].toLowerCase() }
  }

  return {}
}

/**
 * Check if a profile matches a gamepad.
 */
export function profileMatches(profile: ControllerProfile, gamepadId: string): boolean {
  const { vendor, product } = parseIds(gamepadId)

  // Check pattern matches
  for (const pattern of profile.match.patterns) {
    if (pattern.test(gamepadId)) {
      return true
    }
  }

  // Check vendor ID
  if (vendor && profile.match.vendorIds?.includes(vendor)) {
    return true
  }

  // Check product ID (only if vendor also matches)
  if (product && profile.match.productIds?.includes(product)) {
    if (vendor && profile.match.vendorIds?.includes(vendor)) {
      return true
    }
  }

  return false
}

/**
 * Detect the best matching profile for a gamepad.
 * Returns the first matching profile (profiles are ordered by priority).
 */
export function detectProfile(gamepad: Gamepad): ControllerProfile {
  const id = gamepad.id

  // Try each profile in priority order
  for (const profile of PROFILES) {
    if (profileMatches(profile, id)) {
      return profile
    }
  }

  // Should never reach here (GENERIC_PROFILE matches everything)
  return GENERIC_PROFILE
}

/**
 * Get profile by name (for manual override).
 */
export function getProfileByName(name: string): ControllerProfile | null {
  return PROFILES.find(p => p.name.toLowerCase() === name.toLowerCase()) ?? null
}

/**
 * List all available profile names.
 */
export function listProfiles(): string[] {
  return PROFILES.map(p => p.name)
}

/**
 * Debug: Test a gamepad ID against all profiles and show matches.
 */
export function debugDetection(gamepadId: string): { profile: string; matched: boolean }[] {
  return PROFILES.map(profile => ({
    profile: profile.name,
    matched: profileMatches(profile, gamepadId),
  }))
}
