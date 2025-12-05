<script setup lang="ts">
/**
 * Profile Picker View
 * ===================
 *
 * Multi-user profile selection with gamepad combo quick-login.
 *
 * Features:
 * - Profile tiles with avatar, name, XP level
 * - Gamepad combo detection for instant login
 * - Optional security (passphrase) per profile
 * - Create new profile flow
 */

import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useGamepadStore } from '@/stores/gamepad'
import { useGamepadNav } from '@/composables/useGamepadNav'
import { api } from '@/api/client'

const router = useRouter()
const authStore = useAuthStore()
const gamepadStore = useGamepadStore()

// Enable gamepad navigation
useGamepadNav({ onBack: () => {} })

interface PlayerProfile {
  player_id: string
  display_name: string | null
  total_xp: number
  level: number  // Backend-provided, single source of truth
  created_at: string
  last_active: string
  has_password: boolean
  has_gamepad_combo: boolean
}

// State
const profiles = ref<PlayerProfile[]>([])
const loading = ref(true)
const selectedProfile = ref<PlayerProfile | null>(null)
const showPasswordPrompt = ref(false)
const passwordInput = ref('')
const passwordError = ref('')
const showCreateProfile = ref(false)
const newPlayerId = ref('')
const newDisplayName = ref('')
const createError = ref('')
const isImportMode = ref(false)  // When true, migrate from existing profile
const showFileImport = ref(false)  // File import wizard

// Check for existing profile to import (default profile with data)
const existingProfileToImport = computed(() => {
  // Find the 'default' profile if it exists and has XP (meaning it was used)
  return profiles.value.find(p => p.player_id === 'default' && p.total_xp > 0)
})

// Gamepad combo tracking
const comboBuffer = ref<string[]>([])
const comboTimeout = ref<number | null>(null)
const comboMatches = ref<string[]>([])
const showComboConflict = ref(false)

// Generate avatar color from player_id
function getAvatarColor(playerId: string): string {
  let hash = 0
  for (let i = 0; i < playerId.length; i++) {
    hash = playerId.charCodeAt(i) + ((hash << 5) - hash)
  }
  const hue = Math.abs(hash % 360)
  return `hsl(${hue}, 70%, 50%)`
}

// Get initials for avatar
function getInitials(profile: PlayerProfile): string {
  const name = profile.display_name || profile.player_id
  return name.substring(0, 2).toUpperCase()
}

// Load profiles
async function loadProfiles() {
  loading.value = true
  try {
    const response = await api.get('/api/players')
    profiles.value = response.data.players
  } catch (e) {
    console.error('Failed to load profiles:', e)
  } finally {
    loading.value = false
  }
}

// Select a profile
async function selectProfile(profile: PlayerProfile) {
  selectedProfile.value = profile

  if (profile.has_password) {
    // Show password prompt
    showPasswordPrompt.value = true
    passwordInput.value = ''
    passwordError.value = ''
  } else {
    // Direct login
    await loginAs(profile.player_id)
  }
}

// Login with password
async function submitPassword() {
  if (!selectedProfile.value) return

  passwordError.value = ''
  const success = await loginWithCredentials(
    selectedProfile.value.player_id,
    passwordInput.value
  )

  if (success) {
    showPasswordPrompt.value = false
    await loginAs(selectedProfile.value.player_id)
  } else {
    passwordError.value = 'Incorrect password'
  }
}

// Verify password
async function loginWithCredentials(playerId: string, password: string): Promise<boolean> {
  try {
    const response = await api.post('/api/auth/verify-password', {
      player_id: playerId,
      password,
    })
    return response.data.success
  } catch {
    return false
  }
}

// Perform actual login
async function loginAs(playerId: string) {
  // Set the player ID in the auth store (also persists to localStorage)
  authStore.setPlayerId(playerId)

  // Check auth status for this player
  await authStore.checkAuthStatus()

  // Navigate to home
  router.push('/')
}

// Create new profile (or import existing if isImportMode)
async function createProfile() {
  createError.value = ''

  if (!newPlayerId.value.trim()) {
    createError.value = 'Player ID is required'
    return
  }

  try {
    let response

    if (isImportMode.value && existingProfileToImport.value) {
      // Import mode: migrate from existing profile
      response = await api.post('/api/players/migrate', {
        from_player_id: existingProfileToImport.value.player_id,
        to_player_id: newPlayerId.value.trim().toLowerCase(),
        display_name: newDisplayName.value.trim() || null,
        delete_source: true,
      })
    } else {
      // Create mode: new profile
      response = await api.post('/api/players', {
        player_id: newPlayerId.value.trim().toLowerCase(),
        display_name: newDisplayName.value.trim() || null,
      })
    }

    if (response.data.success) {
      showCreateProfile.value = false
      newPlayerId.value = ''
      newDisplayName.value = ''
      isImportMode.value = false
      await loadProfiles()

      // Auto-select the new/imported profile
      const newProfile = profiles.value.find(
        p => p.player_id === response.data.player.player_id
      )
      if (newProfile) {
        await selectProfile(newProfile)
      }
    } else {
      createError.value = response.data.error || 'Failed to create profile'
    }
  } catch (e: any) {
    createError.value = e.response?.data?.error || 'Failed to create profile'
  }
}

// Handle import click - either migrate from default or show file import
function handleImportClick() {
  if (existingProfileToImport.value) {
    // Migrate from default profile
    isImportMode.value = true
    const existingProfile = existingProfileToImport.value
    if (existingProfile?.display_name) {
      newPlayerId.value = existingProfile.display_name.toLowerCase().replace(/[^a-z0-9_]/g, '')
      newDisplayName.value = existingProfile.display_name
    }
  } else {
    // No default profile - show file import wizard
    showCreateProfile.value = false
    showFileImport.value = true
  }
}

// Gamepad combo handling
function handleButtonPress(buttonName: string) {
  // Add to combo buffer
  comboBuffer.value.push(buttonName)

  // Reset timeout
  if (comboTimeout.value) {
    clearTimeout(comboTimeout.value)
  }

  // Check combo after brief pause (user might still be entering)
  comboTimeout.value = window.setTimeout(async () => {
    await checkCombo()
  }, 800)
}

async function checkCombo() {
  if (comboBuffer.value.length < 3) {
    comboBuffer.value = []
    return
  }

  try {
    const response = await api.post('/api/auth/identify-by-combo', {
      combo: comboBuffer.value,
    })

    if (response.data.count === 1) {
      // Single match - auto login!
      const playerId = response.data.matching_players[0]
      const profile = profiles.value.find(p => p.player_id === playerId)

      if (profile) {
        if (profile.has_password) {
          // Still needs password
          selectedProfile.value = profile
          showPasswordPrompt.value = true
        } else {
          await loginAs(playerId)
        }
      }
    } else if (response.data.count > 1) {
      // Conflict - highlight matching profiles
      comboMatches.value = response.data.matching_players
      showComboConflict.value = true
    }
    // 0 matches = invalid combo, just clear
  } catch (e) {
    console.error('Combo check failed:', e)
  }

  comboBuffer.value = []
}

// Watch for gamepad button presses
let lastButtons: Record<string, boolean> = {}

watch(
  () => gamepadStore.buttons,
  (buttons) => {
    if (!buttons) return

    // Detect newly pressed buttons
    for (const [name, pressed] of Object.entries(buttons)) {
      if (pressed && !lastButtons[name]) {
        handleButtonPress(name)
      }
    }
    lastButtons = { ...buttons }
  },
  { deep: true }
)

// Cancel dialogs
function cancelPasswordPrompt() {
  showPasswordPrompt.value = false
  selectedProfile.value = null
  passwordInput.value = ''
}

function cancelCreateProfile() {
  showCreateProfile.value = false
  newPlayerId.value = ''
  newDisplayName.value = ''
  createError.value = ''
  isImportMode.value = false
}

function cancelComboConflict() {
  showComboConflict.value = false
  comboMatches.value = []
}

onMounted(async () => {
  await loadProfiles()
  gamepadStore.startPolling()
})

onUnmounted(() => {
  if (comboTimeout.value) {
    clearTimeout(comboTimeout.value)
  }
})
</script>

<template>
  <div class="min-h-screen flex flex-col items-center justify-center p-8 bg-oled-black">
    <!-- Header -->
    <div class="text-center mb-12 animate-float">
      <h1 class="text-4xl md:text-5xl font-bold mb-2">
        <span class="text-accent-primary">LMSP</span>
      </h1>
      <p class="text-xl text-text-secondary">Who's playing?</p>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-text-muted">Loading profiles...</div>

    <!-- Profile Grid -->
    <div
      v-else
      class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 max-w-4xl"
    >
      <!-- Existing profiles -->
      <button
        v-for="profile in profiles"
        :key="profile.player_id"
        class="profile-tile gamepad-focusable"
        :class="{
          'ring-2 ring-accent-secondary': comboMatches.includes(profile.player_id),
        }"
        @click="selectProfile(profile)"
      >
        <!-- Avatar -->
        <div
          class="avatar"
          :style="{ backgroundColor: getAvatarColor(profile.player_id) }"
        >
          {{ getInitials(profile) }}
        </div>

        <!-- Name -->
        <div class="name">
          {{ profile.display_name || profile.player_id }}
        </div>

        <!-- Level badge -->
        <div class="level-badge">
          Lv. {{ profile.level }}
        </div>

        <!-- Security indicator -->
        <div v-if="profile.has_password || profile.has_gamepad_combo" class="security-badge">
          <span v-if="profile.has_password">🔒</span>
          <span v-if="profile.has_gamepad_combo">🎮</span>
        </div>
      </button>

      <!-- Add Profile tile -->
      <button
        class="profile-tile add-tile gamepad-focusable"
        @click="showCreateProfile = true"
      >
        <div class="avatar add-avatar">+</div>
        <div class="name">Add Profile</div>
      </button>
    </div>

    <!-- Gamepad hint -->
    <div v-if="gamepadStore.connected" class="mt-12 text-center">
      <div class="text-sm text-accent-primary mb-1">🎮 Gamepad detected!</div>
      <div class="text-xs text-text-muted">
        Enter your button combo to quick-login
      </div>
      <div v-if="comboBuffer.length > 0" class="mt-2 text-xs text-accent-secondary">
        Combo: {{ comboBuffer.join(' → ') }}
      </div>
    </div>

    <!-- Password Prompt Modal -->
    <div
      v-if="showPasswordPrompt"
      class="modal-overlay"
      @click.self="cancelPasswordPrompt"
    >
      <div class="modal-content oled-panel">
        <h2 class="text-xl font-bold mb-4">
          Enter Password for {{ selectedProfile?.display_name || selectedProfile?.player_id }}
        </h2>

        <input
          v-model="passwordInput"
          type="password"
          class="oled-input w-full mb-4"
          placeholder="Password"
          @keyup.enter="submitPassword"
          autofocus
        />

        <div v-if="passwordError" class="text-red-500 text-sm mb-4">
          {{ passwordError }}
        </div>

        <div class="flex gap-4">
          <button class="oled-button-secondary flex-1" @click="cancelPasswordPrompt">
            Cancel
          </button>
          <button class="oled-button-primary flex-1" @click="submitPassword">
            Login
          </button>
        </div>
      </div>
    </div>

    <!-- Create Profile Modal -->
    <div
      v-if="showCreateProfile"
      class="modal-overlay"
      @click.self="cancelCreateProfile"
    >
      <div class="modal-content oled-panel">
        <h2 class="text-xl font-bold mb-4">
          {{ isImportMode ? 'Import Profile' : 'Create New Profile' }}
        </h2>

        <!-- Import mode info -->
        <div v-if="isImportMode && existingProfileToImport" class="mb-4 p-3 bg-oled-near rounded-lg">
          <div class="text-xs text-text-muted mb-1">Importing progress:</div>
          <div class="text-sm">
            <span class="text-accent-primary">{{ existingProfileToImport.total_xp }} XP</span>
            <span class="text-text-muted"> · Lv. {{ existingProfileToImport.level }}</span>
          </div>
        </div>

        <div class="mb-4">
          <label class="block text-sm text-text-secondary mb-1">Player ID</label>
          <input
            v-model="newPlayerId"
            type="text"
            class="oled-input w-full"
            placeholder="e.g., cat, micha"
            autofocus
          />
          <div class="text-xs text-text-muted mt-1">
            2-20 characters, lowercase letters, numbers, underscores
          </div>
        </div>

        <div class="mb-4">
          <label class="block text-sm text-text-secondary mb-1">Display Name (optional)</label>
          <input
            v-model="newDisplayName"
            type="text"
            class="oled-input w-full"
            placeholder="e.g., Cat, Micha"
          />
        </div>

        <div v-if="createError" class="text-red-500 text-sm mb-4">
          {{ createError }}
        </div>

        <div class="flex gap-4">
          <button class="oled-button-secondary flex-1" @click="cancelCreateProfile">
            Cancel
          </button>
          <button class="oled-button-primary flex-1" @click="createProfile">
            {{ isImportMode ? 'Import' : 'Create' }}
          </button>
        </div>

        <!-- Import existing link (subtle, below buttons, right-aligned) -->
        <div
          v-if="!isImportMode"
          class="mt-4 text-right"
        >
          <button
            class="text-xs text-text-muted hover:text-text-secondary transition-colors"
            @click="handleImportClick"
          >
            Import existing profile
          </button>
        </div>
      </div>
    </div>

    <!-- File Import Wizard Modal -->
    <div
      v-if="showFileImport"
      class="modal-overlay"
      @click.self="showFileImport = false"
    >
      <div class="modal-content oled-panel">
        <h2 class="text-xl font-bold mb-4">Import Profile</h2>

        <p class="text-text-secondary mb-6">
          You can import an existing profile and all of your data and achievements here.
        </p>

        <div class="mb-6">
          <label
            class="flex flex-col items-center justify-center p-8 border-2 border-dashed border-oled-border rounded-lg cursor-pointer hover:border-accent-primary/50 transition-colors"
          >
            <div class="text-3xl mb-2">📁</div>
            <div class="text-sm text-text-secondary mb-1">Choose backup file</div>
            <div class="text-xs text-text-muted">.json or .lmsp</div>
            <input
              type="file"
              accept=".json,.lmsp"
              class="hidden"
              disabled
            />
          </label>
          <div class="text-xs text-text-muted mt-2 text-center">
            Coming soon - profile backup/restore
          </div>
        </div>

        <div class="flex gap-4">
          <button class="oled-button-secondary flex-1" @click="showFileImport = false">
            Cancel
          </button>
        </div>
      </div>
    </div>

    <!-- Combo Conflict Modal -->
    <div
      v-if="showComboConflict"
      class="modal-overlay"
      @click.self="cancelComboConflict"
    >
      <div class="modal-content oled-panel">
        <h2 class="text-xl font-bold mb-4">Multiple profiles matched!</h2>
        <p class="text-text-secondary mb-4">
          This combo is used by multiple profiles. Please select one:
        </p>

        <div class="flex flex-col gap-2 mb-4">
          <button
            v-for="playerId in comboMatches"
            :key="playerId"
            class="oled-button-secondary"
            @click="selectProfile(profiles.find(p => p.player_id === playerId)!); cancelComboConflict()"
          >
            {{ profiles.find(p => p.player_id === playerId)?.display_name || playerId }}
          </button>
        </div>

        <button class="oled-button w-full" @click="cancelComboConflict">
          Cancel
        </button>
      </div>
    </div>

  </div>
</template>

<style scoped>
.profile-tile {
  @apply flex flex-col items-center p-6 rounded-xl;
  @apply bg-oled-panel border border-oled-border;
  @apply transition-all duration-200;
  @apply hover:border-accent-primary/50 hover:scale-105;
  @apply focus:outline-none focus:ring-2 focus:ring-accent-primary;
  min-width: 140px;
}

.profile-tile:active {
  @apply scale-100;
}

.avatar {
  @apply w-20 h-20 rounded-full flex items-center justify-center;
  @apply text-2xl font-bold text-white mb-3;
  @apply shadow-lg;
}

.add-avatar {
  @apply bg-oled-near text-text-muted text-4xl;
  @apply border-2 border-dashed border-oled-border;
}

.add-tile:hover .add-avatar {
  @apply border-accent-primary text-accent-primary;
}

.name {
  @apply text-lg font-medium text-text-primary mb-1;
}

.level-badge {
  @apply text-xs text-accent-secondary;
}

.security-badge {
  @apply mt-2 text-sm;
}

.modal-overlay {
  @apply fixed inset-0 bg-black/80 flex items-center justify-center z-50;
  backdrop-filter: blur(4px);
}

.modal-content {
  @apply w-full max-w-md p-6 rounded-xl;
}

.oled-input {
  @apply bg-oled-near border border-oled-border rounded-lg px-4 py-3;
  @apply text-text-primary placeholder-text-muted;
  @apply focus:outline-none focus:border-accent-primary;
}
</style>
