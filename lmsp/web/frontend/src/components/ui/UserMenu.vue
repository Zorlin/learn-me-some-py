<script setup lang="ts">
/**
 * User Menu Component
 * ===================
 *
 * Profile avatar with dropdown menu for:
 * - View Profile
 * - Switch User
 * - Logout
 */

import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { usePlayerStore } from '@/stores/player'
import { User, Users, LogOut } from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()
const playerStore = usePlayerStore()

const isOpen = ref(false)
const menuRef = ref<HTMLElement | null>(null)

// Get first letter of display name for avatar
const avatarLetter = computed(() => {
  const name = playerStore.displayName || playerStore.playerId || 'U'
  return name.charAt(0).toUpperCase()
})

// Generate a consistent color from the player ID
const avatarColor = computed(() => {
  const id = playerStore.playerId || 'default'
  let hash = 0
  for (let i = 0; i < id.length; i++) {
    hash = id.charCodeAt(i) + ((hash << 5) - hash)
  }
  const hue = Math.abs(hash % 360)
  return `hsl(${hue}, 70%, 50%)`
})

function toggleMenu() {
  isOpen.value = !isOpen.value
}

function closeMenu() {
  isOpen.value = false
}

function goToProfile() {
  closeMenu()
  router.push('/settings/profile')
}

function switchUser() {
  closeMenu()
  // Clear current player ID and redirect to profile picker
  authStore.setPlayerId('')
  authStore.logout()
  router.push('/profiles')
}

async function logout() {
  closeMenu()
  await authStore.logout()
  authStore.setPlayerId('')
  router.push('/profiles')
}

// Close menu when clicking outside
function handleClickOutside(event: MouseEvent) {
  if (menuRef.value && !menuRef.value.contains(event.target as Node)) {
    closeMenu()
  }
}

// Close menu on escape key
function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    closeMenu()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<template>
  <div ref="menuRef" class="relative">
    <!-- Avatar Button -->
    <button
      class="user-avatar gamepad-focusable w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold text-white transition-all hover:ring-2 hover:ring-accent-primary focus:ring-2 focus:ring-accent-primary"
      :style="{ backgroundColor: avatarColor }"
      @click.stop="toggleMenu"
      :title="playerStore.displayName || playerStore.playerId"
    >
      {{ avatarLetter }}
    </button>

    <!-- Dropdown Menu -->
    <Transition name="menu">
      <div
        v-if="isOpen"
        class="absolute right-0 mt-2 w-48 bg-oled-panel border border-oled-border rounded-lg shadow-xl overflow-hidden z-50"
      >
        <!-- User Info Header -->
        <div class="px-4 py-3 border-b border-oled-border">
          <p class="text-sm font-medium text-white truncate">
            {{ playerStore.displayName || playerStore.playerId }}
          </p>
          <p v-if="playerStore.displayName && playerStore.playerId !== playerStore.displayName" class="text-xs text-text-muted truncate">
            {{ playerStore.playerId }}
          </p>
        </div>

        <!-- Menu Items -->
        <div class="py-1">
          <button
            class="menu-item gamepad-focusable w-full px-4 py-2 text-left text-sm text-text-secondary hover:text-white hover:bg-oled-border/50 transition-colors flex items-center gap-3"
            @click="goToProfile"
          >
            <User :size="18" />
            Profile
          </button>

          <button
            class="menu-item gamepad-focusable w-full px-4 py-2 text-left text-sm text-text-secondary hover:text-white hover:bg-oled-border/50 transition-colors flex items-center gap-3"
            @click="switchUser"
          >
            <Users :size="18" />
            Switch User
          </button>

          <div class="border-t border-oled-border my-1"></div>

          <button
            class="menu-item gamepad-focusable w-full px-4 py-2 text-left text-sm text-red-400 hover:text-red-300 hover:bg-oled-border/50 transition-colors flex items-center gap-3"
            @click="logout"
          >
            <LogOut :size="18" />
            Logout
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.menu-enter-active,
.menu-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.menu-enter-from,
.menu-leave-to {
  opacity: 0;
  transform: translateY(-8px) scale(0.95);
}

.menu-enter-to,
.menu-leave-from {
  opacity: 1;
  transform: translateY(0) scale(1);
}
</style>
