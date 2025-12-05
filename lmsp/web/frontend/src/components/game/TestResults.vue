<script setup lang="ts">
/**
 * Test Results Component
 * =======================
 *
 * "Help is a feature, not a bug"
 * Shows test results with COPY BUTTONS for easy debugging with Claude Code.
 * Pytest output gets syntax highlighting!
 */

import { computed } from 'vue'
import CopyButton from '@/components/ui/CopyButton.vue'

interface TestResult {
  success: boolean
  passing: number
  total: number
  output?: string
  stdout?: string  // User print() output, separate from test output
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

// Highlight pytest output with colors
function highlightPytestOutput(text: string): string {
  if (!text) return ''

  // Escape HTML first
  let html = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')

  // PASSED - green
  html = html.replace(/\bPASSED\b/g, '<span class="pytest-passed">PASSED</span>')

  // FAILED - red
  html = html.replace(/\bFAILED\b/g, '<span class="pytest-failed">FAILED</span>')

  // ERROR - red
  html = html.replace(/\bERROR\b/g, '<span class="pytest-error">ERROR</span>')

  // Test names (test_something)
  html = html.replace(/\b(test_\w+)/g, '<span class="pytest-test-name">$1</span>')

  // AssertionError and other exceptions
  html = html.replace(/\b(AssertionError|ValueError|TypeError|KeyError|IndexError|AttributeError|NameError|SyntaxError|Exception)\b/g,
    '<span class="pytest-exception">$1</span>')

  // Expected/got patterns - highlight the quoted values
  html = html.replace(/Expected\s+&#39;([^&#]+)&#39;/g,
    'Expected <span class="pytest-expected">\'$1\'</span>')
  html = html.replace(/got\s+&#39;([^&#]+)&#39;/g,
    'got <span class="pytest-actual">\'$1\'</span>')

  // Also handle double quotes
  html = html.replace(/Expected\s+&quot;([^&]+)&quot;/g,
    'Expected <span class="pytest-expected">"$1"</span>')
  html = html.replace(/got\s+&quot;([^&]+)&quot;/g,
    'got <span class="pytest-actual">"$1"</span>')

  // Summary line: "X passed" in green, "X failed" in red
  html = html.replace(/(\d+)\s+passed/g, '<span class="pytest-passed">$1 passed</span>')
  html = html.replace(/(\d+)\s+failed/g, '<span class="pytest-failed">$1 failed</span>')
  html = html.replace(/(\d+)\s+error/g, '<span class="pytest-error">$1 error</span>')

  // File paths and line numbers (muted)
  html = html.replace(/([\/\w\-_.]+\.py):(\d+)/g,
    '<span class="pytest-file">$1</span>:<span class="pytest-line">$2</span>')

  // assert keyword
  html = html.replace(/\b(assert)\b/g, '<span class="pytest-keyword">$1</span>')

  // Arrows and markers
  html = html.replace(/(&gt;|&lt;|\|)/g, '<span class="pytest-marker">$1</span>')

  return html
}

const highlightedOutput = computed(() => {
  return highlightPytestOutput(props.results.output || '')
})

const highlightedError = computed(() => {
  return highlightPytestOutput(props.results.error || '')
})

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

  if (props.results.stdout) {
    text += `### Your Output (print statements)\n\`\`\`\n${props.results.stdout}\n\`\`\`\n\n`
  }

  if (props.results.output) {
    text += `### Test Output\n\`\`\`\n${props.results.output}\n\`\`\`\n`
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
      <pre class="output-pre error" v-html="highlightedError"></pre>
    </div>

    <!-- User STDOUT (print statements) -->
    <div v-if="results.stdout" class="stdout-section">
      <div class="section-header">
        <div class="section-label text-accent-secondary">Your Output</div>
        <CopyButton :content="results.stdout" label="Copy Output" />
      </div>
      <pre class="output-pre stdout">{{ results.stdout }}</pre>
    </div>

    <!-- Test Output -->
    <div v-if="results.output" class="output-section">
      <div class="section-header">
        <div class="section-label">Output</div>
        <CopyButton :content="results.output" label="Copy Output" />
      </div>
      <pre class="output-pre" v-html="highlightedOutput"></pre>
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
  background: rgba(239, 68, 68, 0.05);
}

.error-section,
.stdout-section,
.output-section {
  border-top: 1px solid var(--oled-border, #1a1a1a);
}

.output-pre.stdout {
  background: rgba(59, 130, 246, 0.05);
  color: var(--text-primary, #e5e7eb);
}

.success-message {
  padding: 2rem;
  text-align: center;
}

/* Pytest Syntax Highlighting */
:deep(.pytest-passed) {
  color: #22c55e;
  font-weight: 600;
}

:deep(.pytest-failed) {
  color: #ef4444;
  font-weight: 600;
}

:deep(.pytest-error) {
  color: #ef4444;
  font-weight: 600;
}

:deep(.pytest-test-name) {
  color: #60a5fa;
}

:deep(.pytest-exception) {
  color: #f472b6;
  font-weight: 600;
}

:deep(.pytest-expected) {
  color: #22c55e;
  background: rgba(34, 197, 94, 0.1);
  padding: 0 0.25em;
  border-radius: 0.125em;
}

:deep(.pytest-actual) {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
  padding: 0 0.25em;
  border-radius: 0.125em;
}

:deep(.pytest-file) {
  color: #6b7280;
}

:deep(.pytest-line) {
  color: #fbbf24;
}

:deep(.pytest-keyword) {
  color: #818cf8;
  font-weight: 600;
}

:deep(.pytest-marker) {
  color: #6b7280;
}
</style>
