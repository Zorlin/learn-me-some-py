/**
 * Auth Store
 * ==========
 *
 * Manages authentication state, password, and gamepad combo unlock.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api/client'

// Helper functions for base64url encoding/decoding (WebAuthn)
function base64urlToBuffer(base64url: string): ArrayBuffer {
  const base64 = base64url.replace(/-/g, '+').replace(/_/g, '/')
  const padding = '='.repeat((4 - (base64.length % 4)) % 4)
  const binary = atob(base64 + padding)
  const bytes = new Uint8Array(binary.length)
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i)
  }
  return bytes.buffer
}

function bufferToBase64url(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer)
  let binary = ''
  for (let i = 0; i < bytes.length; i++) {
    binary += String.fromCharCode(bytes[i])
  }
  return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '')
}

export interface AuthStatus {
  player_id: string
  has_password: boolean
  has_gamepad_combo: boolean
  has_passkey: boolean
  needs_auth: boolean
}

export interface GamepadComboInfo {
  has_combo: boolean
  combo_length: number
  hint: string | null
}

export const useAuthStore = defineStore('auth', () => {
  // State - load playerId from localStorage if available
  const isAuthenticated = ref(false)
  const sessionId = ref<string | null>(null)
  const playerId = ref(localStorage.getItem('lmsp_player_id') || '')
  const authStatus = ref<AuthStatus | null>(null)
  const comboInfo = ref<GamepadComboInfo | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Combo enrollment state
  const isEnrollingCombo = ref(false)
  const enrollmentCombo = ref<string[]>([])

  // Computed
  const needsAuth = computed(() => authStatus.value?.needs_auth ?? false)
  const hasPassword = computed(() => authStatus.value?.has_password ?? false)
  const hasGamepadCombo = computed(() => authStatus.value?.has_gamepad_combo ?? false)
  const hasPasskey = computed(() => authStatus.value?.has_passkey ?? false)
  const hasProfile = computed(() => !!playerId.value)

  // Set player ID and persist to localStorage
  function setPlayerId(id: string) {
    playerId.value = id
    if (id) {
      localStorage.setItem('lmsp_player_id', id)
    } else {
      localStorage.removeItem('lmsp_player_id')
    }
  }

  // Actions
  async function checkAuthStatus() {
    isLoading.value = true
    error.value = null

    try {
      const response = await api.get(`/api/auth/status?player_id=${playerId.value}`)
      authStatus.value = response.data

      // If no auth required, auto-authenticate
      if (!response.data.needs_auth) {
        isAuthenticated.value = true
      }

      // Check for stored session
      const storedSession = localStorage.getItem('lmsp_session')
      if (storedSession) {
        const valid = await verifySession(storedSession)
        if (valid) {
          sessionId.value = storedSession
          isAuthenticated.value = true
        } else {
          localStorage.removeItem('lmsp_session')
        }
      }

      // Get combo info if has combo
      if (response.data.has_gamepad_combo) {
        await loadComboInfo()
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to check auth status'
    } finally {
      isLoading.value = false
    }
  }

  async function loadComboInfo() {
    try {
      const response = await api.get(`/api/auth/get-gamepad-combo?player_id=${playerId.value}`)
      comboInfo.value = response.data
    } catch (e) {
      console.error('Failed to load combo info:', e)
    }
  }

  async function verifySession(sid: string): Promise<boolean> {
    try {
      const response = await api.get(`/api/auth/session/${sid}`)
      return response.data.valid
    } catch {
      return false
    }
  }

  async function loginWithPassword(password: string): Promise<boolean> {
    isLoading.value = true
    error.value = null

    try {
      const response = await api.post('/api/auth/verify-password', {
        player_id: playerId.value,
        password,
      })

      if (response.data.success) {
        isAuthenticated.value = true
        if (response.data.session_id) {
          sessionId.value = response.data.session_id
          localStorage.setItem('lmsp_session', response.data.session_id)
        }
        return true
      }
      return false
    } catch (e: unknown) {
      const err = e as { response?: { data?: { error?: string } } }
      error.value = err?.response?.data?.error || 'Login failed'
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function loginWithGamepadCombo(combo: string[]): Promise<boolean> {
    isLoading.value = true
    error.value = null

    try {
      const response = await api.post('/api/auth/verify-gamepad-combo', {
        player_id: playerId.value,
        combo,
      })

      if (response.data.success) {
        isAuthenticated.value = true
        if (response.data.session_id) {
          sessionId.value = response.data.session_id
          localStorage.setItem('lmsp_session', response.data.session_id)
        }
        return true
      }
      return false
    } catch (e: unknown) {
      const err = e as { response?: { data?: { error?: string } } }
      error.value = err?.response?.data?.error || 'Combo verification failed'
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function loginWithPasskey(): Promise<boolean> {
    isLoading.value = true
    error.value = null

    try {
      // Step 1: Get authentication options from server
      const optionsResponse = await api.post('/api/auth/passkey/authenticate/begin', {
        player_id: playerId.value,
      })

      if (!optionsResponse.data) {
        throw new Error('Failed to start passkey authentication')
      }

      const options = optionsResponse.data

      // Convert base64url strings to ArrayBuffer
      const publicKeyOptions: PublicKeyCredentialRequestOptions = {
        challenge: base64urlToBuffer(options.challenge),
        timeout: options.timeout,
        rpId: options.rpId,
        allowCredentials: options.allowCredentials?.map((cred: { id: string; type: string }) => ({
          id: base64urlToBuffer(cred.id),
          type: cred.type,
        })),
        userVerification: options.userVerification,
      }

      // Step 2: Get credential from browser
      const credential = await navigator.credentials.get({
        publicKey: publicKeyOptions,
      }) as PublicKeyCredential

      if (!credential) {
        throw new Error('Passkey authentication cancelled')
      }

      const assertionResponse = credential.response as AuthenticatorAssertionResponse

      // Step 3: Verify with server
      const completeResponse = await api.post('/api/auth/passkey/authenticate/complete', {
        id: credential.id,
        rawId: bufferToBase64url(credential.rawId),
        type: credential.type,
        response: {
          clientDataJSON: bufferToBase64url(assertionResponse.clientDataJSON),
          authenticatorData: bufferToBase64url(assertionResponse.authenticatorData),
          signature: bufferToBase64url(assertionResponse.signature),
          userHandle: assertionResponse.userHandle ? bufferToBase64url(assertionResponse.userHandle) : null,
        },
      })

      if (completeResponse.data.success) {
        isAuthenticated.value = true
        if (completeResponse.data.session_id) {
          sessionId.value = completeResponse.data.session_id
          localStorage.setItem('lmsp_session', completeResponse.data.session_id)
        }
        return true
      }
      return false
    } catch (e: unknown) {
      const err = e as { message?: string; response?: { data?: { error?: string } } }
      error.value = err?.response?.data?.error || err?.message || 'Passkey authentication failed'
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function setPassword(password: string, currentPassword?: string): Promise<boolean> {
    isLoading.value = true
    error.value = null

    try {
      const response = await api.post('/api/auth/set-password', {
        player_id: playerId.value,
        password,
        current_password: currentPassword,
      })

      if (response.data.success) {
        await checkAuthStatus()
        return true
      }
      return false
    } catch (e: unknown) {
      const err = e as { response?: { data?: { error?: string } } }
      error.value = err?.response?.data?.error || 'Failed to set password'
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function removePassword(password: string): Promise<boolean> {
    isLoading.value = true
    error.value = null

    try {
      const response = await api.post('/api/auth/remove-password', {
        player_id: playerId.value,
        password,
      })

      if (response.data.success) {
        await checkAuthStatus()
        return true
      }
      return false
    } catch (e: unknown) {
      const err = e as { response?: { data?: { error?: string } } }
      error.value = err?.response?.data?.error || 'Failed to remove password'
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function setGamepadCombo(combo: string[], password?: string): Promise<boolean> {
    isLoading.value = true
    error.value = null

    try {
      const response = await api.post('/api/auth/set-gamepad-combo', {
        player_id: playerId.value,
        combo,
        password,
      })

      if (response.data.success) {
        await checkAuthStatus()
        await loadComboInfo()
        return true
      }
      return false
    } catch (e: unknown) {
      const err = e as { response?: { data?: { error?: string } } }
      error.value = err?.response?.data?.error || 'Failed to set gamepad combo'
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function removeGamepadCombo(password?: string): Promise<boolean> {
    isLoading.value = true
    error.value = null

    try {
      const response = await api.post('/api/auth/remove-gamepad-combo', {
        player_id: playerId.value,
        password,
      })

      if (response.data.success) {
        await checkAuthStatus()
        comboInfo.value = null
        return true
      }
      return false
    } catch (e: unknown) {
      const err = e as { response?: { data?: { error?: string } } }
      error.value = err?.response?.data?.error || 'Failed to remove gamepad combo'
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function logout() {
    if (sessionId.value) {
      try {
        await api.post('/api/auth/logout', { session_id: sessionId.value })
      } catch {
        // Ignore logout errors
      }
    }

    sessionId.value = null
    isAuthenticated.value = false
    localStorage.removeItem('lmsp_session')
  }

  // Combo enrollment helpers
  function startComboEnrollment() {
    isEnrollingCombo.value = true
    enrollmentCombo.value = []
  }

  function addToEnrollmentCombo(button: string) {
    if (enrollmentCombo.value.length < 10) {
      enrollmentCombo.value.push(button)
    }
  }

  function clearEnrollmentCombo() {
    enrollmentCombo.value = []
  }

  function cancelComboEnrollment() {
    isEnrollingCombo.value = false
    enrollmentCombo.value = []
  }

  return {
    // State
    isAuthenticated,
    sessionId,
    playerId,
    authStatus,
    comboInfo,
    isLoading,
    error,
    isEnrollingCombo,
    enrollmentCombo,

    // Computed
    needsAuth,
    hasPassword,
    hasGamepadCombo,
    hasPasskey,
    hasProfile,

    // Actions
    setPlayerId,
    checkAuthStatus,
    loginWithPassword,
    loginWithGamepadCombo,
    loginWithPasskey,
    setPassword,
    removePassword,
    setGamepadCombo,
    removeGamepadCombo,
    logout,
    startComboEnrollment,
    addToEnrollmentCombo,
    clearEnrollmentCombo,
    cancelComboEnrollment,
  }
})
