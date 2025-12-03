<script setup lang="ts">
/**
 * Code Editor Component
 * ======================
 *
 * Tab/Shift+Tab = Indentation (as it should be!)
 * Copy button for easy debugging
 */

import { ref, watch, onMounted } from 'vue'
import CopyButton from '@/components/ui/CopyButton.vue'

const props = defineProps<{
  code: string
  readonly?: boolean
}>()

const emit = defineEmits<{
  'update:code': [value: string]
}>()

const editorRef = ref<HTMLTextAreaElement | null>(null)
const lineNumbers = ref<string[]>([])

// Calculate line numbers
function updateLineNumbers() {
  const lines = props.code.split('\n')
  lineNumbers.value = lines.map((_, i) => String(i + 1))
}

watch(() => props.code, updateLineNumbers, { immediate: true })

function handleInput(event: Event) {
  const target = event.target as HTMLTextAreaElement
  emit('update:code', target.value)
}

function handleKeydown(event: KeyboardEvent) {
  const target = event.target as HTMLTextAreaElement
  const start = target.selectionStart
  const end = target.selectionEnd

  // Tab key inserts 4 spaces (indent)
  if (event.key === 'Tab' && !event.shiftKey) {
    event.preventDefault()
    const spaces = '    '
    const newValue = props.code.substring(0, start) + spaces + props.code.substring(end)
    emit('update:code', newValue)
    // Set cursor position after spaces
    requestAnimationFrame(() => {
      target.selectionStart = target.selectionEnd = start + spaces.length
    })
  }

  // Shift+Tab removes 4 spaces (dedent)
  if (event.key === 'Tab' && event.shiftKey) {
    event.preventDefault()

    // Find the start of the current line
    const beforeCursor = props.code.substring(0, start)
    const lineStart = beforeCursor.lastIndexOf('\n') + 1
    const lineIndent = props.code.substring(lineStart, start)

    // Check if line starts with spaces we can remove
    if (lineIndent.startsWith('    ')) {
      const newValue = props.code.substring(0, lineStart) +
                       props.code.substring(lineStart + 4)
      emit('update:code', newValue)
      requestAnimationFrame(() => {
        target.selectionStart = target.selectionEnd = Math.max(lineStart, start - 4)
      })
    }
  }

  // Enter key maintains current indentation
  if (event.key === 'Enter') {
    event.preventDefault()

    // Get the current line's indentation
    const beforeCursor = props.code.substring(0, start)
    const lineStart = beforeCursor.lastIndexOf('\n') + 1
    const currentLine = props.code.substring(lineStart, start)
    const indentMatch = currentLine.match(/^(\s*)/)
    const indent = indentMatch ? indentMatch[1] : ''

    // Add extra indent if line ends with ':'
    const trimmedLine = currentLine.trim()
    const extraIndent = trimmedLine.endsWith(':') ? '    ' : ''

    const newValue = props.code.substring(0, start) + '\n' + indent + extraIndent + props.code.substring(end)
    emit('update:code', newValue)

    requestAnimationFrame(() => {
      target.selectionStart = target.selectionEnd = start + 1 + indent.length + extraIndent.length
    })
  }
}

function handleScroll(event: Event) {
  const target = event.target as HTMLTextAreaElement
  const lineNumbersEl = document.querySelector('.line-numbers') as HTMLElement
  if (lineNumbersEl) {
    lineNumbersEl.scrollTop = target.scrollTop
  }
}

onMounted(() => {
  if (editorRef.value) {
    editorRef.value.focus()
  }
})
</script>

<template>
  <div class="code-editor oled-panel">
    <div class="editor-header">
      <div class="flex items-center gap-2">
        <span class="text-accent-primary font-mono text-sm">Python</span>
        <span v-if="readonly" class="text-xs text-text-muted">(Read Only)</span>
      </div>
      <div class="flex items-center gap-3">
        <span class="text-xs text-text-muted">{{ lineNumbers.length }} lines</span>
        <CopyButton :content="code" label="Copy Code" />
      </div>
    </div>

    <div class="editor-container">
      <!-- Line Numbers -->
      <div class="line-numbers">
        <div
          v-for="num in lineNumbers"
          :key="num"
          class="line-number"
        >
          {{ num }}
        </div>
      </div>

      <!-- Code Area -->
      <textarea
        ref="editorRef"
        :value="code"
        :readonly="readonly"
        class="code-textarea"
        spellcheck="false"
        autocomplete="off"
        autocorrect="off"
        autocapitalize="off"
        @input="handleInput"
        @keydown="handleKeydown"
        @scroll="handleScroll"
      />
    </div>
  </div>
</template>

<style scoped>
.code-editor {
  display: flex;
  flex-direction: column;
  height: 400px;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--oled-border, #1a1a1a);
}

.editor-container {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.line-numbers {
  display: flex;
  flex-direction: column;
  padding: 1rem 0.5rem;
  background: rgba(255, 255, 255, 0.02);
  border-right: 1px solid var(--oled-border, #1a1a1a);
  overflow: hidden;
  user-select: none;
}

.line-number {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 0.875rem;
  line-height: 1.5rem;
  color: rgba(255, 255, 255, 0.3);
  text-align: right;
  min-width: 2rem;
  padding-right: 0.5rem;
}

.code-textarea {
  flex: 1;
  padding: 1rem;
  background: transparent;
  border: none;
  outline: none;
  resize: none;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 0.875rem;
  line-height: 1.5rem;
  color: #e0e0e0;
  tab-size: 4;
}

.code-textarea:focus {
  outline: none;
}

.code-textarea::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

.code-textarea:read-only {
  opacity: 0.7;
  cursor: not-allowed;
}
</style>
