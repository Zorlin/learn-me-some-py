<script setup lang="ts">
/**
 * Admin Panel
 * ===========
 *
 * Node administration for LMSP instances.
 * - User management (list, edit, delete)
 * - Node statistics
 * - Registration settings
 * - Invite code management
 */

import { ref, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useGamepadNav } from '@/composables/useGamepadNav'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/api/client'
import { Users, BarChart3, Settings, Ticket, Trash2, Shield, ShieldOff, Copy, Check, X, AlertCircle, CheckCircle, Plus, Archive } from 'lucide-vue-next'

const authStore = useAuthStore()

// Toast notification system
interface Toast {
  id: number
  type: 'success' | 'error'
  message: string
}
const toasts = ref<Toast[]>([])
let toastId = 0

function showToast(type: 'success' | 'error', message: string) {
  const id = ++toastId
  toasts.value.push({ id, type, message })
  setTimeout(() => {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }, 4000)
}

function dismissToast(id: number) {
  toasts.value = toasts.value.filter(t => t.id !== id)
}

const router = useRouter()
const route = useRoute()

// Enable gamepad navigation
useGamepadNav({ onBack: () => router.push('/') })

// Active tab
type TabId = 'users' | 'stats' | 'settings' | 'invites'
const activeTab = ref<TabId>('users')

// Map URL slugs to tab IDs
const urlToTab: Record<string, TabId> = {
  users: 'users',
  stats: 'stats',
  settings: 'settings',
  invites: 'invites',
}

const tabToUrl: Record<TabId, string> = {
  users: 'users',
  stats: 'stats',
  settings: 'settings',
  invites: 'invites',
}

const tabs = [
  { id: 'users' as const, label: 'Users', icon: Users },
  { id: 'stats' as const, label: 'Stats', icon: BarChart3 },
  { id: 'settings' as const, label: 'Settings', icon: Settings },
  { id: 'invites' as const, label: 'Invites', icon: Ticket },
]

// Update URL when tab changes
watch(activeTab, (newTab) => {
  const urlSlug = tabToUrl[newTab]
  if (route.params.tab !== urlSlug) {
    router.replace(`/admin/${urlSlug}`)
  }
})

// Update tab when URL changes
watch(() => route.params.tab, (urlTab) => {
  if (urlTab && typeof urlTab === 'string') {
    const tabId = urlToTab[urlTab]
    if (tabId && activeTab.value !== tabId) {
      activeTab.value = tabId
    }
  }
})

// ====================
// Users Tab
// ====================

interface User {
  player_id: string
  display_name: string | null
  created_at: string
  is_admin: boolean
  has_password: boolean
  has_gamepad_combo: boolean
  total_xp: number
  challenges_completed: number
  invited_by_code: string | null
}

const users = ref<User[]>([])
const usersLoading = ref(false)
const usersError = ref<string | null>(null)

// Delete confirmation
const deleteConfirm = ref<string | null>(null)
const deleting = ref(false)

// Edit user modal
const editingUser = ref<User | null>(null)
const editDisplayName = ref('')
const editIsAdmin = ref(false)
const saving = ref(false)

async function fetchUsers() {
  usersLoading.value = true
  usersError.value = null
  try {
    const response = await api.get<{ users: User[] }>('/admin/users')
    users.value = response.data.users
  } catch (e: any) {
    if (e.response?.status === 403) {
      usersError.value = 'Admin access required'
    } else {
      usersError.value = e.message || 'Failed to load users'
    }
  } finally {
    usersLoading.value = false
  }
}

function startEdit(user: User) {
  editingUser.value = user
  editDisplayName.value = user.display_name || ''
  editIsAdmin.value = user.is_admin
}

function cancelEdit() {
  editingUser.value = null
}

async function saveUser() {
  if (!editingUser.value) return
  saving.value = true
  try {
    await api.put(`/admin/users/${editingUser.value.player_id}`, {
      display_name: editDisplayName.value || null,
      is_admin: editIsAdmin.value,
    })
    showToast('success', `Updated ${editingUser.value.player_id}`)
    editingUser.value = null
    await fetchUsers()
  } catch (e: any) {
    const detail = e.response?.data?.detail
    if (detail) {
      showToast('error', detail)
    } else {
      showToast('error', 'Failed to save user. Check your connection.')
    }
  } finally {
    saving.value = false
  }
}

async function deleteUser(playerId: string) {
  deleting.value = true
  try {
    await api.delete(`/admin/users/${playerId}`)
    showToast('success', `Deleted user ${playerId}`)
    deleteConfirm.value = null
    await fetchUsers()
  } catch (e: any) {
    const detail = e.response?.data?.detail
    if (detail) {
      showToast('error', detail)
    } else {
      showToast('error', 'Failed to delete user. Check your connection.')
    }
  } finally {
    deleting.value = false
  }
}

// ====================
// Stats Tab
// ====================

interface NodeStats {
  total_players: number
  total_completions: number
  total_xp_earned: number
  players_with_password: number
  players_with_gamepad: number
  players_secured: number  // Has password OR gamepad (no double-counting)
  challenges_completed_last_7_days: number
  active_players_last_7_days: number
}

const stats = ref<NodeStats | null>(null)
const statsLoading = ref(false)
const statsError = ref<string | null>(null)

async function fetchStats() {
  statsLoading.value = true
  statsError.value = null
  try {
    const response = await api.get<NodeStats>('/admin/stats')
    stats.value = response.data
  } catch (e: any) {
    statsError.value = e.message || 'Failed to load stats'
  } finally {
    statsLoading.value = false
  }
}

// ====================
// Settings Tab
// ====================

type RegistrationMode = 'open' | 'invite_only' | 'closed'

const registrationMode = ref<RegistrationMode>('open')
const settingsLoading = ref(false)
const settingsSaving = ref(false)

async function fetchSettings() {
  settingsLoading.value = true
  try {
    const response = await api.get<{ registration_mode: RegistrationMode }>('/admin/settings')
    registrationMode.value = response.data.registration_mode
  } catch (e: any) {
    console.error('Failed to load settings:', e)
  } finally {
    settingsLoading.value = false
  }
}

async function saveRegistrationMode(mode: RegistrationMode) {
  settingsSaving.value = true
  try {
    await api.put('/admin/settings', { registration_mode: mode })
    registrationMode.value = mode
    showToast('success', `Registration mode set to ${mode.replace('_', ' ')}`)
  } catch (e: any) {
    const detail = e.response?.data?.detail
    if (detail) {
      showToast('error', detail)
    } else {
      showToast('error', 'Failed to save settings. Check your connection.')
    }
  } finally {
    settingsSaving.value = false
  }
}

// ====================
// Invites Tab
// ====================

interface InviteCode {
  code: string
  created_by: string
  created_at: string
  expires_at: string | null
  max_uses: number
  uses: number
  note: string | null
  active: boolean
}

const invites = ref<InviteCode[]>([])
const invitesLoading = ref(false)
const showInactive = ref(false)

// New invite form
const newInviteMaxUses = ref(1)
const newInviteExpiresDays = ref<number | null>(null)
const newInviteNote = ref('')
const creatingInvite = ref(false)

// Copied indicator
const copiedCode = ref<string | null>(null)

async function fetchInvites() {
  invitesLoading.value = true
  try {
    const response = await api.get<{ invites: InviteCode[] }>(`/admin/invites?include_inactive=${showInactive.value}`)
    invites.value = response.data.invites
  } catch (e: any) {
    console.error('Failed to load invites:', e)
  } finally {
    invitesLoading.value = false
  }
}

async function createInvite() {
  creatingInvite.value = true
  try {
    const response = await api.post<{ code: string }>('/admin/invites', {
      max_uses: newInviteMaxUses.value,
      expires_in_days: newInviteExpiresDays.value || null,
      note: newInviteNote.value || null,
    })
    // Reset form
    newInviteMaxUses.value = 1
    newInviteExpiresDays.value = null
    newInviteNote.value = ''
    // Copy to clipboard
    await copyToClipboard(response.data.code)
    showToast('success', `Invite code ${response.data.code} created and copied!`)
    // Refresh list
    await fetchInvites()
  } catch (e: any) {
    console.error('Create invite error:', e)
    const detail = e.response?.data?.detail
    if (detail) {
      showToast('error', detail)
    } else if (e.response?.status === 403) {
      showToast('error', 'Admin access required to create invites')
    } else {
      showToast('error', 'Failed to create invite. Check your connection.')
    }
  } finally {
    creatingInvite.value = false
  }
}

async function deactivateInvite(code: string) {
  try {
    await api.delete(`/admin/invites/${code}`)
    showToast('success', `Invite code ${code} archived`)
    await fetchInvites()
  } catch (e: any) {
    const detail = e.response?.data?.detail
    if (detail) {
      showToast('error', detail)
    } else {
      showToast('error', 'Failed to archive invite. Check your connection.')
    }
  }
}

async function addInviteUses(code: string, uses: number = 1) {
  try {
    await api.post(`/admin/invites/${code}/add-uses`, { uses })
    showToast('success', `Added ${uses} use(s) to ${code}`)
    await fetchInvites()
  } catch (e: any) {
    const detail = e.response?.data?.detail
    if (detail) {
      showToast('error', detail)
    } else {
      showToast('error', 'Failed to add uses. Check your connection.')
    }
  }
}

async function copyToClipboard(code: string) {
  try {
    await navigator.clipboard.writeText(code)
    copiedCode.value = code
    setTimeout(() => { copiedCode.value = null }, 2000)
  } catch (e) {
    // Fallback for older browsers
    const input = document.createElement('input')
    input.value = code
    document.body.appendChild(input)
    input.select()
    document.execCommand('copy')
    document.body.removeChild(input)
    copiedCode.value = code
    setTimeout(() => { copiedCode.value = null }, 2000)
  }
}

// Format date helper
function formatDate(isoString: string): string {
  const date = new Date(isoString)
  return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
}

function formatDateTime(isoString: string): string {
  const date = new Date(isoString)
  return date.toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// Watch showInactive to refetch
watch(showInactive, () => {
  fetchInvites()
})

// Load data on mount
onMounted(() => {
  // Read tab from URL, fallback to users
  const urlTab = route.params.tab
  if (urlTab && typeof urlTab === 'string' && urlToTab[urlTab]) {
    activeTab.value = urlToTab[urlTab]
  } else {
    router.replace('/admin/users')
  }

  // Fetch initial data
  fetchUsers()
  fetchStats()
  fetchSettings()
  fetchInvites()
})

// Computed stats
const securityRate = computed(() => {
  if (!stats.value || stats.value.total_players === 0) return 0
  // Use players_secured (has password OR gamepad) - no double-counting
  return Math.round((stats.value.players_secured / stats.value.total_players) * 100)
})
</script>

<template>
  <div class="h-full flex flex-col lg:flex-row">
    <!-- Vertical Tabs (left side on large screens, top on small) -->
    <nav class="admin-nav shrink-0 border-b lg:border-b-0 lg:border-r border-oled-border bg-oled-panel/30">
      <!-- Mobile: horizontal scroll -->
      <div class="flex lg:flex-col overflow-x-auto lg:overflow-visible p-2 lg:p-4 gap-1 lg:gap-2 lg:w-56">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          class="admin-tab gamepad-focusable whitespace-nowrap"
          :class="{ active: activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          <component :is="tab.icon" :size="20" class="shrink-0" />
          <span class="hidden sm:inline lg:inline">{{ tab.label }}</span>
        </button>
      </div>
    </nav>

    <!-- Content Area -->
    <main class="flex-1 overflow-y-auto p-4 lg:p-8">
      <div class="max-w-4xl mx-auto">

        <!-- Users Tab -->
        <section v-if="activeTab === 'users'" class="admin-section">
          <h1 class="text-2xl lg:text-3xl font-bold mb-6 flex items-center gap-3">
            <Users class="text-accent-primary" :size="28" />
            User Management
          </h1>

          <!-- Loading -->
          <div v-if="usersLoading && users.length === 0" class="oled-panel text-center py-8">
            <div class="animate-pulse text-4xl mb-3">👥</div>
            <p class="text-text-muted">Loading users...</p>
          </div>

          <!-- Error -->
          <div v-else-if="usersError" class="oled-panel border-red-500/30">
            <div class="text-center py-8 text-red-400">
              <div class="text-4xl mb-3">⚠️</div>
              <p>{{ usersError }}</p>
              <button class="oled-button mt-4 gamepad-focusable" @click="fetchUsers">Retry</button>
            </div>
          </div>

          <!-- Users List -->
          <div v-else class="space-y-3">
            <div
              v-for="user in users"
              :key="user.player_id"
              class="oled-panel"
            >
              <div class="flex items-start justify-between gap-4">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 mb-1">
                    <span class="font-semibold text-text-primary truncate">
                      {{ user.display_name || user.player_id }}
                    </span>
                    <span
                      v-if="user.is_admin"
                      class="px-2 py-0.5 text-xs rounded bg-accent-primary/20 text-accent-primary font-medium"
                    >
                      Admin
                    </span>
                  </div>
                  <div v-if="user.display_name" class="text-sm text-text-muted truncate mb-2">
                    @{{ user.player_id }}
                  </div>
                  <div class="flex flex-wrap gap-x-4 gap-y-1 text-sm text-text-secondary">
                    <span>{{ user.total_xp.toLocaleString() }} XP</span>
                    <span>{{ user.challenges_completed }} challenges</span>
                    <span v-if="user.has_password" class="text-accent-success">Password</span>
                    <span v-if="user.has_gamepad_combo" class="text-accent-primary">Gamepad</span>
                  </div>
                  <div class="text-xs text-text-muted mt-2">
                    Joined {{ formatDate(user.created_at) }}
                    <span v-if="user.invited_by_code" class="ml-2">
                      via invite
                    </span>
                  </div>
                </div>

                <!-- Actions -->
                <div class="flex items-center gap-2 shrink-0">
                  <button
                    class="oled-button px-3 py-2 gamepad-focusable"
                    @click="startEdit(user)"
                    title="Edit user"
                  >
                    Edit
                  </button>
                  <button
                    v-if="deleteConfirm !== user.player_id"
                    class="oled-button px-3 py-2 text-red-400 hover:text-red-300 gamepad-focusable"
                    @click="deleteConfirm = user.player_id"
                    title="Delete user"
                  >
                    <Trash2 :size="18" />
                  </button>
                  <div v-else class="flex items-center gap-2">
                    <button
                      class="oled-button px-3 py-2 border-red-500 text-red-400 gamepad-focusable"
                      :disabled="deleting"
                      @click="deleteUser(user.player_id)"
                    >
                      {{ deleting ? 'Deleting...' : 'Confirm' }}
                    </button>
                    <button
                      class="oled-button px-3 py-2 gamepad-focusable"
                      @click="deleteConfirm = null"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="users.length === 0" class="oled-panel text-center py-8 text-text-muted">
              <div class="text-4xl mb-3">👻</div>
              <p>No users yet</p>
            </div>
          </div>
        </section>

        <!-- Stats Tab -->
        <section v-if="activeTab === 'stats'" class="admin-section">
          <h1 class="text-2xl lg:text-3xl font-bold mb-6 flex items-center gap-3">
            <BarChart3 class="text-accent-primary" :size="28" />
            Node Statistics
          </h1>

          <!-- Loading -->
          <div v-if="statsLoading && !stats" class="oled-panel text-center py-8">
            <div class="animate-pulse text-4xl mb-3">📊</div>
            <p class="text-text-muted">Loading statistics...</p>
          </div>

          <!-- Stats Grid -->
          <div v-else-if="stats" class="space-y-6">
            <!-- Overview -->
            <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <div class="oled-panel text-center">
                <div class="text-3xl font-bold text-accent-primary mb-1">
                  {{ stats.total_players }}
                </div>
                <div class="text-sm text-text-muted">Total Players</div>
              </div>
              <div class="oled-panel text-center">
                <div class="text-3xl font-bold text-accent-success mb-1">
                  {{ stats.total_completions.toLocaleString() }}
                </div>
                <div class="text-sm text-text-muted">Total Completions</div>
              </div>
              <div class="oled-panel text-center">
                <div class="text-3xl font-bold text-yellow-400 mb-1">
                  {{ stats.total_xp_earned.toLocaleString() }}
                </div>
                <div class="text-sm text-text-muted">Total XP Earned</div>
              </div>
              <div class="oled-panel text-center">
                <div class="text-3xl font-bold text-purple-400 mb-1">
                  {{ securityRate }}%
                </div>
                <div class="text-sm text-text-muted">Secured Accounts</div>
              </div>
            </div>

            <!-- Activity -->
            <div class="oled-panel">
              <h2 class="text-lg font-semibold mb-4">Last 7 Days</h2>
              <div class="grid grid-cols-2 gap-4">
                <div class="bg-oled-black rounded-lg p-4 border border-oled-border">
                  <div class="text-2xl font-bold text-text-primary mb-1">
                    {{ stats.active_players_last_7_days }}
                  </div>
                  <div class="text-sm text-text-muted">Active Players</div>
                </div>
                <div class="bg-oled-black rounded-lg p-4 border border-oled-border">
                  <div class="text-2xl font-bold text-text-primary mb-1">
                    {{ stats.challenges_completed_last_7_days }}
                  </div>
                  <div class="text-sm text-text-muted">Challenges Completed</div>
                </div>
              </div>
            </div>

            <!-- Security Breakdown -->
            <div class="oled-panel">
              <h2 class="text-lg font-semibold mb-4">Security Breakdown</h2>
              <div class="space-y-3">
                <div class="flex items-center justify-between">
                  <span class="text-text-secondary">Password Protected</span>
                  <span class="font-medium">{{ stats.players_with_password }} / {{ stats.total_players }}</span>
                </div>
                <div class="h-2 bg-oled-border rounded-full overflow-hidden">
                  <div
                    class="h-full bg-accent-success transition-all"
                    :style="{ width: stats.total_players > 0 ? `${(stats.players_with_password / stats.total_players) * 100}%` : '0%' }"
                  />
                </div>

                <div class="flex items-center justify-between mt-4">
                  <span class="text-text-secondary">Gamepad Combo</span>
                  <span class="font-medium">{{ stats.players_with_gamepad }} / {{ stats.total_players }}</span>
                </div>
                <div class="h-2 bg-oled-border rounded-full overflow-hidden">
                  <div
                    class="h-full bg-accent-primary transition-all"
                    :style="{ width: stats.total_players > 0 ? `${(stats.players_with_gamepad / stats.total_players) * 100}%` : '0%' }"
                  />
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Settings Tab -->
        <section v-if="activeTab === 'settings'" class="admin-section">
          <h1 class="text-2xl lg:text-3xl font-bold mb-6 flex items-center gap-3">
            <Settings class="text-accent-primary" :size="28" />
            Node Settings
          </h1>

          <div class="oled-panel">
            <h2 class="text-lg font-semibold mb-4">Registration Mode</h2>
            <p class="text-sm text-text-muted mb-4">
              Control who can create accounts on this node.
            </p>

            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <button
                class="oled-button py-4 gamepad-focusable text-center relative"
                :class="{
                  'border-accent-success text-accent-success': registrationMode === 'open',
                  'opacity-50': settingsSaving
                }"
                :disabled="settingsSaving"
                @click="saveRegistrationMode('open')"
              >
                <div class="text-2xl mb-1">🌍</div>
                <div class="font-medium">Open</div>
                <div class="text-xs text-text-muted mt-1">Anyone can register</div>
              </button>

              <button
                class="oled-button py-4 gamepad-focusable text-center relative"
                :class="{
                  'border-accent-primary text-accent-primary': registrationMode === 'invite_only',
                  'opacity-50': settingsSaving
                }"
                :disabled="settingsSaving"
                @click="saveRegistrationMode('invite_only')"
              >
                <div class="text-2xl mb-1">🎟️</div>
                <div class="font-medium">Invite Only</div>
                <div class="text-xs text-text-muted mt-1">Requires invite code</div>
              </button>

              <button
                class="oled-button py-4 gamepad-focusable text-center relative"
                :class="{
                  'border-red-500 text-red-400': registrationMode === 'closed',
                  'opacity-50': settingsSaving
                }"
                :disabled="settingsSaving"
                @click="saveRegistrationMode('closed')"
              >
                <div class="text-2xl mb-1">🔒</div>
                <div class="font-medium">Closed</div>
                <div class="text-xs text-text-muted mt-1">No new registrations</div>
              </button>
            </div>

            <div v-if="registrationMode === 'invite_only'" class="mt-4 p-3 bg-accent-primary/5 border border-accent-primary/20 rounded-lg">
              <p class="text-sm text-text-secondary">
                <span class="text-accent-primary font-medium">Tip:</span> Go to the Invites tab to create and manage invite codes.
              </p>
            </div>
          </div>
        </section>

        <!-- Invites Tab -->
        <section v-if="activeTab === 'invites'" class="admin-section">
          <h1 class="text-2xl lg:text-3xl font-bold mb-6 flex items-center gap-3">
            <Ticket class="text-accent-primary" :size="28" />
            Invite Codes
          </h1>

          <!-- Create New Invite -->
          <div class="oled-panel mb-6">
            <h2 class="text-lg font-semibold mb-4">Create New Invite</h2>

            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
              <div>
                <label class="text-sm text-text-muted block mb-2">Max Uses</label>
                <input
                  v-model.number="newInviteMaxUses"
                  type="number"
                  min="1"
                  class="w-full px-4 py-2 bg-oled-black border border-oled-border rounded-lg text-text-primary focus:border-accent-primary focus:outline-none"
                />
              </div>
              <div>
                <label class="text-sm text-text-muted block mb-2">Expires in</label>
                <div class="relative">
                  <input
                    v-model.number="newInviteExpiresDays"
                    type="number"
                    min="1"
                    placeholder="never"
                    class="w-full px-4 py-2 pr-14 bg-oled-black border border-oled-border rounded-lg text-text-primary placeholder-text-muted focus:border-accent-primary focus:outline-none"
                  />
                  <span
                    v-if="newInviteExpiresDays"
                    class="absolute right-4 top-1/2 -translate-y-1/2 text-text-muted pointer-events-none"
                  >
                    days
                  </span>
                </div>
              </div>
              <div>
                <label class="text-sm text-text-muted block mb-2">Note (optional)</label>
                <input
                  v-model="newInviteNote"
                  type="text"
                  placeholder="e.g., For Eve"
                  class="w-full px-4 py-2 bg-oled-black border border-oled-border rounded-lg text-text-primary placeholder-text-muted focus:border-accent-primary focus:outline-none"
                />
              </div>
            </div>

            <button
              class="oled-button px-6 py-2 border-accent-primary text-accent-primary gamepad-focusable"
              :disabled="creatingInvite"
              @click="createInvite"
            >
              {{ creatingInvite ? 'Creating...' : 'Create Invite Code' }}
            </button>
          </div>

          <!-- Existing Invites -->
          <div class="oled-panel">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-semibold">Existing Codes</h2>
              <label class="flex items-center gap-2 text-sm text-text-muted cursor-pointer">
                <input
                  v-model="showInactive"
                  type="checkbox"
                  class="rounded"
                />
                Show inactive
              </label>
            </div>

            <!-- Loading -->
            <div v-if="invitesLoading && invites.length === 0" class="text-center py-8 text-text-muted">
              <div class="animate-pulse">Loading...</div>
            </div>

            <!-- Invites List -->
            <div v-else-if="invites.length > 0" class="space-y-3">
              <div
                v-for="invite in invites"
                :key="invite.code"
                class="bg-oled-black rounded-lg p-4 border border-oled-border"
                :class="{ 'opacity-50': !invite.active || invite.uses >= invite.max_uses }"
              >
                <div class="flex items-start justify-between gap-4">
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2 mb-2">
                      <code
                        class="font-mono text-lg"
                        :class="invite.active && invite.uses < invite.max_uses ? 'text-accent-primary' : 'text-text-muted'"
                      >{{ invite.code }}</code>
                      <button
                        class="p-1 rounded hover:bg-oled-panel transition-colors"
                        @click="copyToClipboard(invite.code)"
                        :title="copiedCode === invite.code ? 'Copied!' : 'Copy to clipboard'"
                      >
                        <Check v-if="copiedCode === invite.code" :size="16" class="text-accent-success" />
                        <Copy v-else :size="16" class="text-text-muted" />
                      </button>
                      <span
                        v-if="invite.uses >= invite.max_uses"
                        class="px-2 py-0.5 text-xs rounded bg-gray-500/20 text-gray-400"
                      >
                        Exhausted
                      </span>
                      <span
                        v-else-if="!invite.active"
                        class="px-2 py-0.5 text-xs rounded bg-red-500/20 text-red-400"
                      >
                        Inactive
                      </span>
                    </div>
                    <div class="flex flex-wrap gap-x-4 gap-y-1 text-sm text-text-secondary">
                      <span :class="{ 'text-gray-500': invite.uses >= invite.max_uses }">
                        {{ invite.uses }} / {{ invite.max_uses }} uses
                      </span>
                      <span v-if="invite.expires_at">Expires {{ formatDate(invite.expires_at) }}</span>
                      <span v-else>Never expires</span>
                    </div>
                    <div class="text-xs text-text-muted mt-2">
                      Created {{ formatDateTime(invite.created_at) }}
                      <span v-if="invite.note" class="ml-2 text-text-secondary">• {{ invite.note }}</span>
                    </div>
                  </div>

                  <div class="flex items-center gap-2">
                    <!-- Add uses button (for exhausted codes) -->
                    <button
                      v-if="invite.uses >= invite.max_uses"
                      class="oled-button px-3 py-2 text-accent-success hover:text-green-300 gamepad-focusable"
                      @click="addInviteUses(invite.code, 1)"
                      title="Add 1 more use"
                    >
                      <Plus :size="18" />
                    </button>
                    <!-- Archive button (for exhausted codes) -->
                    <button
                      v-if="invite.active && invite.uses >= invite.max_uses"
                      class="oled-button px-3 py-2 text-text-muted hover:text-text-secondary gamepad-focusable"
                      @click="deactivateInvite(invite.code)"
                      title="Archive"
                    >
                      <Archive :size="18" />
                    </button>
                    <!-- Deactivate button (for active codes with remaining uses) -->
                    <button
                      v-if="invite.active && invite.uses < invite.max_uses"
                      class="oled-button px-3 py-2 text-red-400 hover:text-red-300 gamepad-focusable"
                      @click="deactivateInvite(invite.code)"
                      title="Archive"
                    >
                      <X :size="18" />
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div v-else class="text-center py-8 text-text-muted">
              <div class="text-4xl mb-3">🎟️</div>
              <p>No invite codes yet</p>
              <p class="text-sm mt-2">Create one above to get started</p>
            </div>
          </div>
        </section>

      </div>
    </main>

    <!-- Toast Notifications -->
    <Teleport to="body">
      <div class="fixed top-4 right-4 z-[100] flex flex-col gap-2 max-w-sm">
        <TransitionGroup name="toast">
          <div
            v-for="toast in toasts"
            :key="toast.id"
            class="flex items-center gap-3 px-4 py-3 rounded-lg shadow-xl border backdrop-blur-sm"
            :class="{
              'bg-accent-success/10 border-accent-success/30 text-accent-success': toast.type === 'success',
              'bg-red-500/10 border-red-500/30 text-red-400': toast.type === 'error'
            }"
          >
            <CheckCircle v-if="toast.type === 'success'" :size="20" />
            <AlertCircle v-else :size="20" />
            <span class="flex-1 text-sm">{{ toast.message }}</span>
            <button
              class="p-1 hover:opacity-70 transition-opacity"
              @click="dismissToast(toast.id)"
            >
              <X :size="16" />
            </button>
          </div>
        </TransitionGroup>
      </div>
    </Teleport>

    <!-- Edit User Modal -->
    <Teleport to="body">
      <div
        v-if="editingUser"
        class="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4"
        @click.self="cancelEdit"
      >
        <div class="bg-oled-panel border border-oled-border rounded-lg p-6 w-full max-w-md">
          <h2 class="text-xl font-bold mb-4">Edit User</h2>

          <div class="space-y-4">
            <div>
              <label class="text-sm text-text-muted block mb-2">Player ID</label>
              <div class="px-4 py-2 bg-oled-black border border-oled-border rounded-lg text-text-muted">
                {{ editingUser.player_id }}
              </div>
            </div>

            <div>
              <label class="text-sm text-text-muted block mb-2">Display Name</label>
              <input
                v-model="editDisplayName"
                type="text"
                placeholder="Enter display name..."
                class="w-full px-4 py-2 bg-oled-black border border-oled-border rounded-lg text-text-primary placeholder-text-muted focus:border-accent-primary focus:outline-none"
              />
            </div>

            <label class="flex items-center gap-3 p-3 rounded-lg hover:bg-oled-black/50 cursor-pointer">
              <button
                class="w-12 h-7 rounded-full transition-colors relative"
                :class="editIsAdmin ? 'bg-accent-primary' : 'bg-oled-border'"
                @click="editIsAdmin = !editIsAdmin"
              >
                <div
                  class="absolute top-1 w-5 h-5 bg-white rounded-full transition-transform"
                  :class="editIsAdmin ? 'translate-x-6' : 'translate-x-1'"
                />
              </button>
              <div class="flex items-center gap-2">
                <Shield v-if="editIsAdmin" :size="18" class="text-accent-primary" />
                <ShieldOff v-else :size="18" class="text-text-muted" />
                <span>Admin privileges</span>
              </div>
            </label>
          </div>

          <div class="flex justify-end gap-3 mt-6">
            <button
              class="oled-button px-4 py-2 gamepad-focusable"
              @click="cancelEdit"
            >
              Cancel
            </button>
            <button
              class="oled-button px-4 py-2 border-accent-primary text-accent-primary gamepad-focusable"
              :disabled="saving"
              @click="saveUser"
            >
              {{ saving ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
/* Pure OLED black nav - no grey backgrounds */
.admin-nav {
  background: transparent;
}

.admin-tab {
  @apply flex items-center gap-3 px-4 py-3 rounded-lg text-text-secondary transition-all;
}

.admin-tab:hover {
  @apply text-text-primary;
  background: rgba(255, 255, 255, 0.03);
}

.admin-tab.active {
  @apply text-accent-primary border-l-2 border-accent-primary;
  background: rgba(0, 255, 136, 0.05);
}

@media (max-width: 1023px) {
  .admin-tab.active {
    @apply border-l-0 border-b-2;
  }
}

.admin-section {
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Toast transitions */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.toast-move {
  transition: transform 0.3s ease;
}
</style>
