/**
 * Gamepad Module
 * ===============
 *
 * Cross-controller gamepad input handling with automatic profile detection.
 *
 * Usage:
 * ```ts
 * import { GamepadManager } from '@/lib/gamepad'
 *
 * const manager = new GamepadManager()
 * manager.onStateChange((state) => {
 *   console.log('LT:', state.leftTrigger)
 *   console.log('A pressed:', state.buttons.A)
 * })
 * manager.start()
 * ```
 */

// Re-export types
export * from './types'
export type { ControllerProfile } from './types'

// Re-export profiles
export { PROFILES, STANDARD_PROFILE, XBOX_PROFILE, PLAYSTATION_PROFILE } from './profiles'

// Re-export detection
export { detectProfile, parseIds, listProfiles, debugDetection } from './detector'

// Re-export mapping
export { mapGamepad, applyDeadzone, createMapper } from './mapper'

import type { UnifiedGamepadState, ControllerProfile } from './types'
import { createEmptyState } from './types'
import { detectProfile, getProfileByName } from './detector'
import { mapGamepad } from './mapper'

export type StateChangeCallback = (state: UnifiedGamepadState) => void

/**
 * GamepadManager - Main interface for gamepad input.
 *
 * Handles connection events, polling, profile detection, and state mapping.
 */
export class GamepadManager {
  private state: UnifiedGamepadState = createEmptyState()
  private profile: ControllerProfile | null = null
  private gamepadIndex: number | null = null
  private animationFrameId: number | null = null
  private callbacks: Set<StateChangeCallback> = new Set()
  private profileOverride: string | null = null

  /** Current unified state (readonly) */
  get currentState(): Readonly<UnifiedGamepadState> {
    return this.state
  }

  /** Current detected profile (readonly) */
  get currentProfile(): Readonly<ControllerProfile> | null {
    return this.profile
  }

  /** Whether a gamepad is connected */
  get isConnected(): boolean {
    return this.state.connected
  }

  /**
   * Register a callback for state changes.
   * Called every frame when polling is active.
   */
  onStateChange(callback: StateChangeCallback): () => void {
    this.callbacks.add(callback)
    return () => this.callbacks.delete(callback)
  }

  /**
   * Override automatic profile detection with a specific profile.
   * Pass null to re-enable automatic detection.
   */
  setProfileOverride(profileName: string | null): void {
    this.profileOverride = profileName
    // Re-detect if connected
    if (this.gamepadIndex !== null) {
      const gp = navigator.getGamepads()[this.gamepadIndex]
      if (gp) {
        this.detectAndSetProfile(gp)
      }
    }
  }

  /**
   * Start listening for gamepad connections and begin polling.
   */
  start(): void {
    window.addEventListener('gamepadconnected', this.handleConnect)
    window.addEventListener('gamepaddisconnected', this.handleDisconnect)

    // Check for already-connected gamepads
    const gamepads = navigator.getGamepads()
    for (const gp of gamepads) {
      if (gp) {
        this.handleConnect({ gamepad: gp } as GamepadEvent)
        break
      }
    }

    this.poll()
  }

  /**
   * Stop polling and remove event listeners.
   */
  stop(): void {
    window.removeEventListener('gamepadconnected', this.handleConnect)
    window.removeEventListener('gamepaddisconnected', this.handleDisconnect)

    if (this.animationFrameId !== null) {
      cancelAnimationFrame(this.animationFrameId)
      this.animationFrameId = null
    }
  }

  /**
   * Get raw gamepad data for debugging.
   */
  getRawGamepad(): Gamepad | null {
    if (this.gamepadIndex === null) return null
    return navigator.getGamepads()[this.gamepadIndex] ?? null
  }

  // Private methods

  private handleConnect = (event: GamepadEvent): void => {
    const gp = event.gamepad
    console.log(`🎮 Gamepad connected: ${gp.id}`)
    console.log(`   Axes: ${gp.axes.length}, Buttons: ${gp.buttons.length}`)

    this.gamepadIndex = gp.index
    this.detectAndSetProfile(gp)

    console.log(`   Profile: ${this.profile?.name ?? 'Unknown'}`)
  }

  private handleDisconnect = (event: GamepadEvent): void => {
    if (this.gamepadIndex === event.gamepad.index) {
      console.log(`🎮 Gamepad disconnected: ${event.gamepad.id}`)
      this.gamepadIndex = null
      this.profile = null
      this.state = createEmptyState()
      this.notifyCallbacks()
    }
  }

  private detectAndSetProfile(gamepad: Gamepad): void {
    if (this.profileOverride) {
      const override = getProfileByName(this.profileOverride)
      if (override) {
        this.profile = override
        return
      }
      console.warn(`Unknown profile override: ${this.profileOverride}, using auto-detect`)
    }

    this.profile = detectProfile(gamepad)
  }

  private poll = (): void => {
    if (this.gamepadIndex !== null && this.profile) {
      const gamepads = navigator.getGamepads()
      const gp = gamepads[this.gamepadIndex]

      if (gp) {
        this.state = mapGamepad(gp, this.profile)
        this.notifyCallbacks()
      }
    }

    this.animationFrameId = requestAnimationFrame(this.poll)
  }

  private notifyCallbacks(): void {
    for (const callback of this.callbacks) {
      callback(this.state)
    }
  }
}

// Singleton instance for convenience
let defaultManager: GamepadManager | null = null

/**
 * Get the default GamepadManager instance.
 * Creates one if it doesn't exist.
 */
export function getGamepadManager(): GamepadManager {
  if (!defaultManager) {
    defaultManager = new GamepadManager()
  }
  return defaultManager
}
