<script setup lang="ts">
/**
 * Security Settings
 * =================
 *
 * Manage password and gamepad combo unlock options.
 */

import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
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

// Load auth status on mount
onMounted(() => {
  authStore.checkAuthStatus()
})

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
</style>
