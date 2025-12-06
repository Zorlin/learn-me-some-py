<script setup lang="ts">
/**
 * Privacy Settings
 * ================
 *
 * Control visibility of stats and profile on shared devices.
 */

import { ref, onMounted } from 'vue'
import { api } from '@/api/client'
import { EyeOff, Eye, UserX, User } from 'lucide-vue-next'

// Privacy settings state
const hideFromLeaderboards = ref(false)
const hideFromPicker = ref(false)
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const success = ref('')

onMounted(async () => {
  await loadPrivacySettings()
})

async function loadPrivacySettings() {
  loading.value = true
  error.value = ''

  try {
    const response = await api.get<{
      hide_from_leaderboards: boolean
      hide_from_picker: boolean
    }>('/player/privacy')

    if (response.ok && response.data) {
      hideFromLeaderboards.value = response.data.hide_from_leaderboards
      hideFromPicker.value = response.data.hide_from_picker
    }
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Failed to load privacy settings'
  } finally {
    loading.value = false
  }
}

async function savePrivacySettings() {
  saving.value = true
  error.value = ''
  success.value = ''

  try {
    const response = await api.post('/player/privacy', {
      hide_from_leaderboards: hideFromLeaderboards.value,
      hide_from_picker: hideFromPicker.value,
    })

    if (response.ok) {
      success.value = 'Privacy settings saved!'
      setTimeout(() => { success.value = '' }, 2000)
    } else {
      error.value = 'Failed to save privacy settings'
    }
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Failed to save privacy settings'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="privacy-settings">
    <h2 class="text-xl font-bold mb-6">Privacy Settings</h2>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-8 text-text-muted">
      Loading privacy settings...
    </div>

    <template v-else>
      <!-- Visibility Settings -->
      <div class="settings-section mb-6">
        <h3 class="font-semibold mb-4 flex items-center gap-2">
          <EyeOff :size="18" class="text-accent-primary" />
          Visibility
        </h3>

        <!-- Hide from Leaderboards -->
        <label class="setting-toggle">
          <div class="setting-info">
            <div class="flex items-center gap-2">
              <component :is="hideFromLeaderboards ? EyeOff : Eye" :size="16" />
              <span class="font-medium">Hide from Leaderboards</span>
            </div>
            <p class="text-sm text-text-muted mt-1">
              Your stats won't appear on public leaderboards
            </p>
          </div>
          <button
            class="toggle-switch"
            :class="{ active: hideFromLeaderboards }"
            @click="hideFromLeaderboards = !hideFromLeaderboards; savePrivacySettings()"
            :disabled="saving"
          >
            <div class="toggle-knob" />
          </button>
        </label>

        <!-- Hide from User Picker -->
        <label class="setting-toggle mt-4">
          <div class="setting-info">
            <div class="flex items-center gap-2">
              <component :is="hideFromPicker ? UserX : User" :size="16" />
              <span class="font-medium">Hide from User Picker</span>
            </div>
            <p class="text-sm text-text-muted mt-1">
              Your profile won't show on the login screen. You can still sign in with your ID, password, passphrase, or gamepad combo.
            </p>
          </div>
          <button
            class="toggle-switch"
            :class="{ active: hideFromPicker }"
            @click="hideFromPicker = !hideFromPicker; savePrivacySettings()"
            :disabled="saving"
          >
            <div class="toggle-knob" />
          </button>
        </label>

        <!-- Messages -->
        <div v-if="error" class="message error mt-4">{{ error }}</div>
        <div v-if="success" class="message success mt-4">{{ success }}</div>
      </div>

      <!-- Help Text -->
      <div class="help-section">
        <h4 class="font-medium mb-2">About Privacy Settings</h4>
        <ul class="text-sm text-text-secondary space-y-1">
          <li>• <strong>Leaderboard hiding:</strong> Your XP and achievements are still tracked, just not shown publicly</li>
          <li>• <strong>Picker hiding:</strong> Great for shared devices where you don't want others to see your profile</li>
        </ul>
        <p class="text-sm text-text-muted mt-3">
          Looking for passkeys? They've moved to the <strong>Security</strong> tab!
        </p>
      </div>
    </template>
  </div>
</template>

<style scoped>
.privacy-settings {
  @apply max-w-2xl;
}

.settings-section {
  @apply p-4 rounded-lg;
  background: var(--oled-panel);
  border: 1px solid var(--oled-border);
}

.setting-toggle {
  @apply flex items-start justify-between gap-4 p-3 rounded-lg cursor-pointer;
  background: var(--oled-surface);
}

.setting-toggle:hover {
  background: rgba(255, 255, 255, 0.03);
}

.setting-info {
  @apply flex-1;
}

.toggle-switch {
  @apply relative w-12 h-7 rounded-full transition-colors flex-shrink-0;
  background: var(--oled-border);
}

.toggle-switch.active {
  background: var(--accent-primary);
}

.toggle-knob {
  @apply absolute top-1 w-5 h-5 bg-white rounded-full transition-transform;
  left: 4px;
}

.toggle-switch.active .toggle-knob {
  transform: translateX(20px);
}

.message {
  @apply p-2 rounded-md text-sm;
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
