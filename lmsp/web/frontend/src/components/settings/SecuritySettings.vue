<script setup lang="ts">
/**
 * Security Settings
 * =================
 *
 * Manage password, gamepad combo, and passkey unlock options.
 */

import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/api/client'
import { Fingerprint, Key } from 'lucide-vue-next'
import GamepadComboRecorder from './GamepadComboRecorder.vue'

const authStore = useAuthStore()

// Form state
const newPassword = ref('')
const confirmPassword = ref('')
const currentPassword = ref('')
const passwordError = ref('')
const passwordSuccess = ref('')

// Combo recorder
const showComboRecorder = ref(false)
const comboSuccess = ref('')

// Passkey state
const passkeys = ref<Array<{ id: string; name: string; created_at: string }>>([])
const passkeySupported = ref(false)
const passkeyUnsupportedReason = ref('')
const registeringPasskey = ref(false)
const passkeyName = ref('')
const passkeyError = ref('')
const passkeySuccess = ref('')

// Load auth status on mount
onMounted(async () => {
  authStore.checkAuthStatus()

  // Check if WebAuthn is supported
  if (!window.isSecureContext) {
    passkeySupported.value = false
    passkeyUnsupportedReason.value = 'Passkeys require HTTPS. You\'re on an insecure connection.'
  } else if (!window.PublicKeyCredential) {
    passkeySupported.value = false
    passkeyUnsupportedReason.value = 'Your browser doesn\'t support passkeys. Try Chrome, Safari, or Edge.'
  } else {
    // WebAuthn API exists, should work
    passkeySupported.value = true
  }

  await loadPasskeys()
})

async function loadPasskeys() {
  if (!passkeySupported.value) return

  try {
    const response = await api.get<{
      passkeys: Array<{ id: string; name: string; created_at: string }>
    }>('/auth/passkeys')

    if (response.ok && response.data) {
      passkeys.value = response.data.passkeys
    }
  } catch {
    // Passkeys not set up yet, that's fine
  }
}

async function registerPasskey() {
  if (!passkeySupported.value) return

  registeringPasskey.value = true
  passkeyError.value = ''
  passkeySuccess.value = ''

  try {
    // Step 1: Get registration options from server
    const optionsResponse = await api.post<{
      challenge: string
      rp: { name: string; id: string }
      user: { id: string; name: string; displayName: string }
      pubKeyCredParams: Array<{ type: string; alg: number }>
      timeout: number
      authenticatorSelection: {
        authenticatorAttachment?: string
        requireResidentKey: boolean
        userVerification: string
      }
    }>('/auth/passkey/register/begin', {
      name: passkeyName.value || 'My Passkey',
    })

    if (!optionsResponse.ok || !optionsResponse.data) {
      throw new Error('Failed to start passkey registration')
    }

    const options = optionsResponse.data

    // Convert base64url strings to ArrayBuffer
    const publicKeyOptions: PublicKeyCredentialCreationOptions = {
      challenge: base64urlToBuffer(options.challenge),
      rp: options.rp,
      user: {
        id: base64urlToBuffer(options.user.id),
        name: options.user.name,
        displayName: options.user.displayName,
      },
      pubKeyCredParams: options.pubKeyCredParams as PublicKeyCredentialParameters[],
      timeout: options.timeout,
      authenticatorSelection: options.authenticatorSelection as AuthenticatorSelectionCriteria,
    }

    // Step 2: Create credential with browser API
    const credential = await navigator.credentials.create({
      publicKey: publicKeyOptions,
    }) as PublicKeyCredential

    if (!credential) {
      throw new Error('Passkey creation cancelled')
    }

    const attestationResponse = credential.response as AuthenticatorAttestationResponse

    // Step 3: Send credential to server
    const completeResponse = await api.post('/auth/passkey/register/complete', {
      id: credential.id,
      rawId: bufferToBase64url(credential.rawId),
      type: credential.type,
      response: {
        clientDataJSON: bufferToBase64url(attestationResponse.clientDataJSON),
        attestationObject: bufferToBase64url(attestationResponse.attestationObject),
      },
      name: passkeyName.value || 'My Passkey',
    })

    if (completeResponse.ok) {
      passkeySuccess.value = 'Passkey registered successfully!'
      passkeyName.value = ''
      await loadPasskeys()
    } else {
      throw new Error('Failed to complete passkey registration')
    }
  } catch (e) {
    passkeyError.value = e instanceof Error ? e.message : 'Failed to register passkey'
  } finally {
    registeringPasskey.value = false
  }
}

async function removePasskey(passkeyId: string) {
  try {
    const response = await api.delete(`/auth/passkey/${passkeyId}`)
    if (response.ok) {
      await loadPasskeys()
      passkeySuccess.value = 'Passkey removed'
      setTimeout(() => { passkeySuccess.value = '' }, 2000)
    }
  } catch (e) {
    passkeyError.value = e instanceof Error ? e.message : 'Failed to remove passkey'
  }
}

// Helper functions for base64url encoding/decoding
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

function formatDate(isoString: string): string {
  return new Date(isoString).toLocaleDateString()
}

// Password management
async function setPassword() {
  passwordError.value = ''
  passwordSuccess.value = ''

  if (newPassword.value.length < 4) {
    passwordError.value = 'Password must be at least 4 characters'
    return
  }

  if (newPassword.value !== confirmPassword.value) {
    passwordError.value = 'Passwords do not match'
    return
  }

  const success = await authStore.setPassword(
    newPassword.value,
    authStore.hasPassword ? currentPassword.value : undefined
  )

  if (success) {
    passwordSuccess.value = 'Password set successfully!'
    newPassword.value = ''
    confirmPassword.value = ''
    currentPassword.value = ''
  } else {
    passwordError.value = authStore.error || 'Failed to set password'
  }
}

async function removePassword() {
  if (!currentPassword.value) {
    passwordError.value = 'Enter current password to remove'
    return
  }

  const success = await authStore.removePassword(currentPassword.value)

  if (success) {
    passwordSuccess.value = 'Password removed'
    currentPassword.value = ''
  } else {
    passwordError.value = authStore.error || 'Failed to remove password'
  }
}

// Gamepad combo management
function startComboEnrollment() {
  showComboRecorder.value = true
  comboSuccess.value = ''
}

async function handleComboRecorded(combo: string[]) {
  showComboRecorder.value = false

  const success = await authStore.setGamepadCombo(
    combo,
    authStore.hasPassword ? currentPassword.value : undefined
  )

  if (success) {
    comboSuccess.value = `Gamepad combo set: ${combo.join(' → ')}`
  }
}

function cancelComboRecording() {
  showComboRecorder.value = false
}

async function removeCombo() {
  const success = await authStore.removeGamepadCombo(
    authStore.hasPassword ? currentPassword.value : undefined
  )

  if (success) {
    comboSuccess.value = 'Gamepad combo removed'
  }
}
</script>

<template>
  <div class="security-settings">
    <h2 class="text-xl font-bold mb-6">Security Settings</h2>

    <!-- Current Status -->
    <div class="status-card mb-6">
      <h3 class="font-semibold mb-3">Current Protection</h3>
      <div class="status-grid">
        <div class="status-item">
          <span class="status-icon" :class="authStore.hasPassword ? 'active' : 'inactive'">
            {{ authStore.hasPassword ? '🔐' : '🔓' }}
          </span>
          <span>Password: {{ authStore.hasPassword ? 'Enabled' : 'Not set' }}</span>
        </div>
        <div class="status-item">
          <span class="status-icon" :class="authStore.hasGamepadCombo ? 'active' : 'inactive'">
            {{ authStore.hasGamepadCombo ? '🎮' : '🎮' }}
          </span>
          <span>Gamepad Combo: {{ authStore.hasGamepadCombo ? 'Enabled' : 'Not set' }}</span>
        </div>
      </div>
      <p v-if="authStore.comboInfo?.hint" class="text-sm text-text-muted mt-2">
        Combo hint: {{ authStore.comboInfo.hint }}
      </p>
    </div>

    <!-- Password Section -->
    <div class="settings-section">
      <h3 class="font-semibold mb-3">Password Protection</h3>

      <!-- Current Password (if has one) -->
      <div v-if="authStore.hasPassword" class="form-group">
        <label>Current Password</label>
        <input
          v-model="currentPassword"
          type="password"
          class="oled-input"
          placeholder="Enter current password"
        />
      </div>

      <!-- New Password -->
      <div class="form-group">
        <label>{{ authStore.hasPassword ? 'New Password' : 'Set Password' }}</label>
        <input
          v-model="newPassword"
          type="password"
          class="oled-input"
          placeholder="Enter password (min 4 characters)"
        />
      </div>

      <!-- Confirm Password -->
      <div class="form-group">
        <label>Confirm Password</label>
        <input
          v-model="confirmPassword"
          type="password"
          class="oled-input"
          placeholder="Confirm password"
        />
      </div>

      <!-- Error/Success Messages -->
      <div v-if="passwordError" class="message error">{{ passwordError }}</div>
      <div v-if="passwordSuccess" class="message success">{{ passwordSuccess }}</div>

      <!-- Actions -->
      <div class="form-actions">
        <button class="oled-button-primary" @click="setPassword" :disabled="authStore.isLoading">
          {{ authStore.hasPassword ? 'Change Password' : 'Set Password' }}
        </button>
        <button
          v-if="authStore.hasPassword"
          class="oled-button"
          @click="removePassword"
          :disabled="authStore.isLoading"
        >
          Remove Password
        </button>
      </div>
    </div>

    <!-- Gamepad Combo Section -->
    <div class="settings-section">
      <h3 class="font-semibold mb-3">Gamepad Combo Unlock</h3>
      <p class="text-sm text-text-secondary mb-4">
        Set a custom button sequence to unlock with your gamepad.
        Perfect for couch gaming when you don't want to type a password!
      </p>

      <!-- Combo Recorder -->
      <GamepadComboRecorder
        v-if="showComboRecorder"
        @combo-recorded="handleComboRecorded"
        @cancel="cancelComboRecording"
      />

      <!-- Combo Actions -->
      <div v-else class="form-actions">
        <button class="oled-button-primary" @click="startComboEnrollment">
          {{ authStore.hasGamepadCombo ? 'Change Combo' : 'Set Gamepad Combo' }}
        </button>
        <button
          v-if="authStore.hasGamepadCombo"
          class="oled-button"
          @click="removeCombo"
          :disabled="authStore.isLoading"
        >
          Remove Combo
        </button>
      </div>

      <div v-if="comboSuccess" class="message success mt-3">{{ comboSuccess }}</div>
    </div>

    <!-- Passkey Section -->
    <div class="settings-section">
      <h3 class="font-semibold mb-3 flex items-center gap-2">
        <Fingerprint :size="18" class="text-accent-primary" />
        Passkeys
      </h3>
      <p class="text-sm text-text-secondary mb-4">
        Sign in securely using your device's biometrics (Touch ID, Face ID, Windows Hello) or a security key.
        No password needed!
      </p>

      <!-- Browser Support Warning -->
      <div v-if="!passkeySupported" class="warning-box mb-4">
        <div class="flex items-center gap-2">
          <span class="text-lg">⚠️</span>
          <span>{{ passkeyUnsupportedReason }}</span>
        </div>
      </div>

      <!-- Registered Passkeys -->
      <div v-if="passkeys.length > 0" class="mb-4">
        <div class="text-sm text-text-muted mb-2">Your Passkeys</div>
        <div class="space-y-2">
          <div
            v-for="passkey in passkeys"
            :key="passkey.id"
            class="passkey-item"
          >
            <div class="flex items-center gap-3">
              <Key :size="16" class="text-accent-primary" />
              <div>
                <div class="font-medium">{{ passkey.name }}</div>
                <div class="text-xs text-text-muted">Added {{ formatDate(passkey.created_at) }}</div>
              </div>
            </div>
            <button
              class="text-red-400 hover:text-red-300 text-sm"
              @click="removePasskey(passkey.id)"
            >
              Remove
            </button>
          </div>
        </div>
      </div>

      <!-- Register New Passkey -->
      <div v-if="passkeySupported" class="register-passkey">
        <div class="form-group">
          <label>Passkey Name (optional)</label>
          <input
            v-model="passkeyName"
            type="text"
            class="oled-input"
            placeholder="e.g., MacBook Touch ID"
          />
        </div>

        <div class="form-actions">
          <button
            class="oled-button-primary flex items-center gap-2"
            @click="registerPasskey"
            :disabled="registeringPasskey"
          >
            <Fingerprint :size="16" />
            {{ registeringPasskey ? 'Setting up...' : (passkeys.length > 0 ? 'Add Another Passkey' : 'Add Passkey') }}
          </button>
        </div>
      </div>

      <!-- Passkey Messages -->
      <div v-if="passkeyError" class="message error mt-3">{{ passkeyError }}</div>
      <div v-if="passkeySuccess" class="message success mt-3">{{ passkeySuccess }}</div>
    </div>

    <!-- Help Text -->
    <div class="help-section">
      <h4 class="font-medium mb-2">How Security Works</h4>
      <ul class="text-sm text-text-secondary space-y-1">
        <li>• <strong>No protection:</strong> Anyone can access your progress</li>
        <li>• <strong>Password only:</strong> Requires password to access</li>
        <li>• <strong>Gamepad combo only:</strong> Enter combo to unlock (great for couch gaming!)</li>
        <li>• <strong>Both:</strong> Either method works to unlock</li>
      </ul>
      <p class="text-sm text-text-muted mt-3">
        Tip: For casual home use, a gamepad combo is fun and easy.
        For shared computers, set a password too.
      </p>
    </div>
  </div>
</template>

<style scoped>
.security-settings {
  @apply max-w-2xl;
}

.status-card {
  @apply p-4 rounded-lg;
  background: var(--oled-panel);
  border: 1px solid var(--oled-border);
}

.status-grid {
  @apply grid grid-cols-2 gap-4;
}

.status-item {
  @apply flex items-center gap-2;
}

.status-icon {
  @apply text-xl;
}

.status-icon.active {
  opacity: 1;
}

.status-icon.inactive {
  opacity: 0.4;
}

.settings-section {
  @apply p-4 rounded-lg mb-6;
  background: var(--oled-panel);
  border: 1px solid var(--oled-border);
}

.form-group {
  @apply mb-4;
}

.form-group label {
  @apply block text-sm font-medium mb-1;
}

.oled-input {
  @apply w-full px-3 py-2 rounded-md;
  background: var(--oled-surface);
  border: 1px solid var(--oled-border);
  color: var(--text-primary);
}

.oled-input:focus {
  outline: none;
  border-color: var(--accent-primary);
}

.form-actions {
  @apply flex gap-3;
}

.message {
  @apply p-2 rounded-md text-sm mb-3;
}

.message.error {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #ef4444;
}

.message.success {
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.3);
  color: #22c55e;
}

.help-section {
  @apply p-4 rounded-lg;
  background: var(--oled-surface);
  border: 1px solid var(--oled-border);
}

.warning-box {
  @apply p-3 rounded-lg text-sm;
  background: rgba(234, 179, 8, 0.1);
  border: 1px solid rgba(234, 179, 8, 0.3);
  color: #eab308;
}

.passkey-item {
  @apply flex items-center justify-between p-3 rounded-lg;
  background: var(--oled-surface);
  border: 1px solid var(--oled-border);
}

.register-passkey {
  @apply p-3 rounded-lg;
  background: var(--oled-surface);
}
</style>
