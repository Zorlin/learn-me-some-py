<script setup lang="ts">
import { useGamepadStore } from '@/stores/gamepad'

const gamepadStore = useGamepadStore()
</script>

<template>
  <div class="flex items-center gap-2">
    <div
      class="w-3 h-3 rounded-full transition-colors duration-300"
      :class="gamepadStore.connected ? 'bg-accent-primary animate-pulse' : 'bg-oled-border'"
    />
    <span class="text-xs text-text-secondary">
      {{ gamepadStore.connected ? 'Gamepad' : 'No Gamepad' }}
    </span>
  </div>
</template>
