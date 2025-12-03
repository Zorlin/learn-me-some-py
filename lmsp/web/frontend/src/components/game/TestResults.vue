<script setup lang="ts">
/**
 * Test Results Component
 * =======================
 *
 * "Help is a feature, not a bug"
 * Shows test results with COPY BUTTONS for easy debugging with Claude Code.
 */

import { computed } from 'vue'
import CopyButton from '@/components/ui/CopyButton.vue'

interface TestResult {
  success: boolean
  passing: number
  total: number
  output?: string
  error?: string
}

interface ChallengeContext {
  name: string
  description: string
  code: string
}

const props = defineProps<{
  results: TestResult
  challenge?: ChallengeContext
}>()

// Format for copying - includes full context for Claude Code
const formatForClaude = computed(() => {
  let text = ''

  // Include challenge context if available
  if (props.challenge) {
    text += `# Challenge: ${props.challenge.name}\n\n`
    text += `## Description\n${props.challenge.description}\n\n`
    text += `## My Code\n\`\`\`python\n${props.challenge.code}\n\`\`\`\n\n`
  }

  text += `## Test Results\n`
  text += `- **Status:** ${props.results.success ? 'PASSED ✅' : 'FAILED ❌'}\n`
  text += `- **Tests:** ${props.results.passing}/${props.results.total} passing\n\n`

  if (props.results.error) {
    text += `### Error\n\`\`\`\n${props.results.error}\n\`\`\`\n\n`
  }

  if (props.results.output) {
    text += `### Output\n\`\`\`\n${props.results.output}\n\`\`\`\n`
  }

  return text
})

const passPercentage = computed(() => {
  if (props.results.total === 0) return 0
  return Math.round((props.results.passing / props.results.total) * 100)
})

const statusIcon = computed(() => {
  if (props.results.success) return '✅'
  if (props.results.passing > 0) return '🔶'
  return '❌'
})

const statusColor = computed(() => {
  if (props.results.success) return 'text-accent-primary'
  if (props.results.passing > 0) return 'text-accent-warning'
  return 'text-accent-error'
})
</script>

<template>
  <div class="test-results oled-panel">
    <!-- Header -->
    <div class="results-header">
      <div class="flex items-center gap-3">
        <span class="text-2xl">{{ statusIcon }}</span>
        <div>
          <div class="font-bold" :class="statusColor">
            {{ results.success ? 'All Tests Passed!' : 'Tests Failed' }}
          </div>
          <div class="text-sm text-text-secondary">
            {{ results.passing }}/{{ results.total }} tests passing
          </div>
        </div>
      </div>

      <!-- Progress Ring -->
      <div class="progress-ring-container">
        <svg class="progress-ring" viewBox="0 0 36 36">
          <path
            class="progress-ring-bg"
            d="M18 2.0845
              a 15.9155 15.9155 0 0 1 0 31.831
              a 15.9155 15.9155 0 0 1 0 -31.831"
          />
          <path
            class="progress-ring-fill"
            :class="statusColor"
            :stroke-dasharray="`${passPercentage}, 100`"
            d="M18 2.0845
              a 15.9155 15.9155 0 0 1 0 31.831
              a 15.9155 15.9155 0 0 1 0 -31.831"
          />
        </svg>
        <div class="progress-ring-text">{{ passPercentage }}%</div>
      </div>
    </div>

    <!-- Error Output -->
    <div v-if="results.error" class="error-section">
      <div class="section-header">
        <div class="section-label text-accent-error">Error</div>
        <CopyButton :content="results.error" label="Copy Error" />
      </div>
      <pre class="output-pre error">{{ results.error }}</pre>
    </div>

    <!-- Test Output -->
    <div v-if="results.output" class="output-section">
      <div class="section-header">
        <div class="section-label">Output</div>
        <CopyButton :content="results.output" label="Copy Output" />
      </div>
      <pre class="output-pre">{{ results.output }}</pre>
    </div>

    <!-- Copy All Button -->
    <div class="copy-all-section">
      <CopyButton
        :content="formatForClaude"
        label="Copy All for Claude Code"
      />
    </div>

    <!-- Empty State -->
    <div v-if="!results.output && !results.error && results.success" class="success-message">
      <div class="text-accent-primary font-bold">Perfect!</div>
      <div class="text-text-secondary text-sm">Your code passed all tests.</div>
    </div>
  </div>
</template>

<style scoped>
.test-results {
  overflow: hidden;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--oled-border, #1a1a1a);
}

.progress-ring-container {
  position: relative;
  width: 48px;
  height: 48px;
}

.progress-ring {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.progress-ring-bg {
  fill: none;
  stroke: rgba(255, 255, 255, 0.1);
  stroke-width: 3;
}

.progress-ring-fill {
  fill: none;
  stroke: currentColor;
  stroke-width: 3;
  stroke-linecap: round;
  transition: stroke-dasharray 0.3s ease;
}

.progress-ring-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 0.625rem;
  font-weight: bold;
  color: var(--text-secondary, #9ca3af);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-right: 1rem;
}

.section-label {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 0.75rem 1rem 0.5rem;
  color: var(--text-muted, #6b7280);
}

.copy-all-section {
  display: flex;
  justify-content: flex-end;
  padding: 0.75rem 1rem;
  border-top: 1px solid var(--oled-border, #1a1a1a);
}

.output-pre {
  margin: 0;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.3);
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 0.75rem;
  line-height: 1.5;
  color: var(--text-secondary, #9ca3af);
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-word;
}

.output-pre.error {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.05);
}

.error-section,
.output-section {
  border-top: 1px solid var(--oled-border, #1a1a1a);
}

.success-message {
  padding: 2rem;
  text-align: center;
}
</style>
