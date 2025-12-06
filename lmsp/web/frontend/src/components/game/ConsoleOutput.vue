<script setup lang="ts">
/**
 * Console Output Component
 * ========================
 *
 * Displays player's print() output in a separate panel above test results.
 * Styling matches TestResults for visual consistency.
 */

import { computed, ref } from 'vue'
import { ChevronDown, ChevronUp, Terminal } from 'lucide-vue-next'
import CopyButton from '@/components/ui/CopyButton.vue'

const props = defineProps<{
  stdout: string
}>()

// Console output expand/collapse state
const expanded = ref(false)
const MAX_COLLAPSED_LINES = 3
const MAX_VISIBLE_LINES = 20

const lines = computed(() => {
  if (!props.stdout) return []
  return props.stdout.split('\n')
})

const lineCount = computed(() => lines.value.length)

const needsExpansion = computed(() => lineCount.value > MAX_COLLAPSED_LINES)

const visibleContent = computed(() => {
  if (!props.stdout) return ''
  if (expanded.value) {
    return props.stdout
  }
  return lines.value.slice(0, MAX_COLLAPSED_LINES).join('\n')
})

const contentHeight = computed(() => {
  if (!props.stdout) return 'auto'
  const visibleLines = expanded.value
    ? Math.min(lineCount.value, MAX_VISIBLE_LINES)
    : Math.min(lineCount.value, MAX_COLLAPSED_LINES)
  return `${Math.max(visibleLines * 1.5 + 1.5, 3)}rem`
})

function toggle() {
  expanded.value = !expanded.value
}
</script>

<template>
  <div class="console-output oled-panel">
    <!-- Header matching TestResults style -->
    <div class="console-header">
      <div class="section-label">
        <Terminal :size="12" class="inline mr-1.5 opacity-70" />
        Console Output
        <span class="line-count">({{ lineCount }} line{{ lineCount !== 1 ? 's' : '' }})</span>
      </div>
      <div class="header-actions">
        <CopyButton :content="stdout" label="Copy Output" />
        <button v-if="needsExpansion" class="expand-btn" @click="toggle">
          <ChevronUp v-if="expanded" :size="16" />
          <ChevronDown v-else :size="16" />
        </button>
      </div>
    </div>

    <!-- Content area -->
    <div
      class="console-content"
      :class="{ 'expanded': expanded }"
      :style="{ maxHeight: contentHeight }"
    >
      <pre class="output-pre">{{ visibleContent }}</pre>
    </div>

    <!-- Show more indicator -->
    <div v-if="needsExpansion && !expanded" class="show-more-bar" @click="toggle">
      <span class="show-more-text">Show {{ lineCount - MAX_COLLAPSED_LINES }} more lines...</span>
    </div>
  </div>
</template>

<style scoped>
.console-output {
  overflow: hidden;
}

.console-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-right: 1rem;
  border-bottom: 1px solid var(--oled-border, #1a1a1a);
}

.section-label {
  display: flex;
  align-items: center;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 0.75rem 1rem;
  color: var(--accent-secondary, #3b82f6);
}

.line-count {
  font-weight: 400;
  text-transform: none;
  letter-spacing: normal;
  color: var(--text-muted, #6b7280);
  margin-left: 0.5rem;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.expand-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 0.25rem;
  color: var(--text-muted, #6b7280);
  transition: all 0.15s ease;
}

.expand-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary, #e5e7eb);
}

.console-content {
  position: relative;
  overflow: hidden;
  transition: max-height 0.2s ease;
}

.console-content.expanded {
  overflow-y: auto;
}

.output-pre {
  margin: 0;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.3);
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 0.75rem;
  line-height: 1.5;
  color: var(--text-primary, #e5e7eb);
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-word;
}

.show-more-bar {
  padding: 0.5rem 1rem;
  text-align: center;
  cursor: pointer;
  border-top: 1px solid var(--oled-border, #1a1a1a);
  background: rgba(0, 0, 0, 0.2);
  transition: background 0.15s ease;
}

.show-more-bar:hover {
  background: rgba(255, 255, 255, 0.02);
}

.show-more-text {
  font-size: 0.7rem;
  color: var(--accent-secondary, #3b82f6);
}
</style>
