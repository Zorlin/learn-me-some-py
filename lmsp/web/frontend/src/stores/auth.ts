/**
 * Auth Store
 * ==========
 *
 * Manages authentication state, password, and gamepad combo unlock.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api/client'

export interface AuthStatus {
  player_id: string
  has_password: boolean
  has_gamepad_combo: boolean
  needs_auth: boolean
}

export interface GamepadComboInfo {
  has_combo: boolean
  combo_length: number
  hint: string | null
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const isAuthenticated = ref(false)
  const sessionId = ref<string | null>(null)
  const playerId = ref('default')
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

    // Actions
    checkAuthStatus,
    loginWithPassword,
    loginWithGamepadCombo,
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
