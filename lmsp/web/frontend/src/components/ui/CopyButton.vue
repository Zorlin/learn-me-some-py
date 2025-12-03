<script setup lang="ts">
/**
 * Copy to Clipboard Button
 * =========================
 *
 * "Help is a feature, not a bug"
 * Makes it easy to copy any content to clipboard for debugging with Claude Code.
 */

import { ref } from 'vue'

const props = defineProps<{
  content: string
  label?: string
}>()

const copied = ref(false)

async function copyToClipboard() {
  try {
    // Handle both string and computed ref content
    const text = typeof props.content === 'string' ? props.content : String(props.content || '')
    console.log('Copying to clipboard:', text.substring(0, 100) + '...')
    await navigator.clipboard.writeText(text)
    copied.value = true

    // Reset after 2 seconds
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (err) {
    console.error('Failed to copy:', err)
    // Fallback for older browsers or permission issues
    try {
      const textarea = document.createElement('textarea')
      textarea.value = typeof props.content === 'string' ? props.content : String(props.content || '')
      document.body.appendChild(textarea)
      textarea.select()
      document.execCommand('copy')
      document.body.removeChild(textarea)
      copied.value = true
      setTimeout(() => { copied.value = false }, 2000)
    } catch (fallbackErr) {
      console.error('Fallback copy also failed:', fallbackErr)
    }
  }
}
</script>

<template>
  <button
    class="copy-btn gamepad-focusable"
    :class="{ copied }"
    @click="copyToClipboard"
    :title="copied ? 'Copied!' : `Copy ${label || 'to clipboard'}`"
  >
    <span v-if="copied" class="copy-icon">✓</span>
    <span v-else class="copy-icon">📋</span>
    <span class="copy-label">{{ copied ? 'Copied!' : (label || 'Copy') }}</span>
  </button>
</template>

<style scoped>
.copy-btn {
  @apply flex items-center gap-1 px-2 py-1 rounded text-xs;
  @apply bg-oled-panel border border-oled-border;
  @apply text-text-secondary hover:text-white hover:border-accent-primary;
  @apply transition-all duration-200;
}

.copy-btn.copied {
  @apply bg-accent-primary/20 border-accent-primary text-accent-primary;
}

.copy-icon {
  @apply text-sm;
}

.copy-label {
  @apply hidden sm:inline;
}
</style>
