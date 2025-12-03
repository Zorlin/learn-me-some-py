<script setup lang="ts">
/**
 * Code Editor Component
 * ======================
 *
 * Prism.js syntax highlighting with textarea overlay
 * Tab/Shift+Tab = Indentation (as it should be!)
 */

import { ref, watch, onMounted, computed } from 'vue'
import Prism from 'prismjs'
import 'prismjs/components/prism-python'
import CopyButton from '@/components/ui/CopyButton.vue'

const props = defineProps<{
  code: string
  readonly?: boolean
}>()

const emit = defineEmits<{
  'update:code': [value: string]
}>()

const editorRef = ref<HTMLTextAreaElement | null>(null)
const highlightRef = ref<HTMLPreElement | null>(null)

// Calculate line numbers
const lineNumbers = computed(() => {
  const lines = props.code.split('\n')
  return lines.map((_, i) => String(i + 1))
})

// Highlighted code using Prism
const highlightedCode = computed(() => {
  // Add a space at end if code ends with newline to match textarea behavior
  let codeToHighlight = props.code
  if (codeToHighlight.endsWith('\n')) {
    codeToHighlight += ' '
  }
  return Prism.highlight(codeToHighlight, Prism.languages.python, 'python')
})

function handleInput(event: Event) {
  const target = event.target as HTMLTextAreaElement
  emit('update:code', target.value)
}

function scrollCursorIntoView(textarea: HTMLTextAreaElement) {
  // Create a temporary element to measure cursor position
  const lineHeight = 24 // 1.5rem = 24px
  const padding = 16 // 1rem padding

  // Get current line number from cursor position
  const textBeforeCursor = textarea.value.substring(0, textarea.selectionStart)
  const currentLine = textBeforeCursor.split('\n').length

  // Calculate desired scroll position to show cursor with some margin
  const cursorY = (currentLine - 1) * lineHeight
  const viewportHeight = textarea.clientHeight - padding * 2
  const currentScrollTop = textarea.scrollTop

  // If cursor is below visible area, scroll down
  if (cursorY > currentScrollTop + viewportHeight - lineHeight * 2) {
    textarea.scrollTop = cursorY - viewportHeight + lineHeight * 3
  }
  // If cursor is above visible area, scroll up
  else if (cursorY < currentScrollTop + lineHeight) {
    textarea.scrollTop = Math.max(0, cursorY - lineHeight)
  }

  // Sync the highlight and line numbers
  handleScroll({ target: textarea } as unknown as Event)
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
    requestAnimationFrame(() => {
      target.selectionStart = target.selectionEnd = start + spaces.length
    })
  }

  // Shift+Tab removes 4 spaces (dedent)
  if (event.key === 'Tab' && event.shiftKey) {
    event.preventDefault()
    const beforeCursor = props.code.substring(0, start)
    const lineStart = beforeCursor.lastIndexOf('\n') + 1
    const lineIndent = props.code.substring(lineStart, start)

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
    const beforeCursor = props.code.substring(0, start)
    const lineStart = beforeCursor.lastIndexOf('\n') + 1
    const currentLine = props.code.substring(lineStart, start)
    const indentMatch = currentLine.match(/^(\s*)/)
    const indent = indentMatch ? indentMatch[1] : ''
    const trimmedLine = currentLine.trim()
    const extraIndent = trimmedLine.endsWith(':') ? '    ' : ''

    const newValue = props.code.substring(0, start) + '\n' + indent + extraIndent + props.code.substring(end)
    emit('update:code', newValue)

    requestAnimationFrame(() => {
      target.selectionStart = target.selectionEnd = start + 1 + indent.length + extraIndent.length
      scrollCursorIntoView(target)
    })
  }
}

function handlePaste() {
  // After paste, scroll to cursor position
  requestAnimationFrame(() => {
    if (editorRef.value) {
      scrollCursorIntoView(editorRef.value)
    }
  })
}

function handleScroll(event: Event) {
  const target = event.target as HTMLTextAreaElement
  const lineNumbersEl = document.querySelector('.line-numbers') as HTMLElement
  if (lineNumbersEl) {
    lineNumbersEl.scrollTop = target.scrollTop
  }
  if (highlightRef.value) {
    highlightRef.value.scrollTop = target.scrollTop
    highlightRef.value.scrollLeft = target.scrollLeft
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

      <!-- Code Area with Syntax Highlighting -->
      <div class="code-area">
        <!-- Highlighted code (behind textarea) -->
        <pre
          ref="highlightRef"
          class="code-highlight"
          aria-hidden="true"
        ><code class="language-python" v-html="highlightedCode"></code></pre>

        <!-- Transparent textarea (captures input) -->
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
          @paste="handlePaste"
        />
      </div>
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

.code-area {
  position: relative;
  flex: 1;
  overflow: hidden;
}

.code-highlight {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  margin: 0;
  padding: 1rem;
  overflow: auto;
  pointer-events: none;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 0.875rem;
  line-height: 1.5rem;
  white-space: pre-wrap;
  word-wrap: break-word;
  background: transparent;
}

.code-highlight code {
  font-family: inherit;
  font-size: inherit;
  line-height: inherit;
  background: transparent;
}

.code-textarea {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  padding: 1rem;
  background: transparent;
  border: none;
  outline: none;
  resize: none;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 0.875rem;
  line-height: 1.5rem;
  color: transparent;
  caret-color: #fff;
  tab-size: 4;
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow: auto;
}

.code-textarea:focus {
  outline: none;
}

.code-textarea::selection {
  background: rgba(99, 102, 241, 0.4);
}

.code-textarea:read-only {
  caret-color: transparent;
  cursor: not-allowed;
}

/* Prism Theme - OLED Dark */
:deep(.token.comment),
:deep(.token.prolog),
:deep(.token.doctype),
:deep(.token.cdata) {
  color: #6b7280;
}

:deep(.token.punctuation) {
  color: #9ca3af;
}

:deep(.token.property),
:deep(.token.tag),
:deep(.token.boolean),
:deep(.token.number),
:deep(.token.constant),
:deep(.token.symbol) {
  color: #f472b6;
}

:deep(.token.selector),
:deep(.token.attr-name),
:deep(.token.string),
:deep(.token.char),
:deep(.token.builtin) {
  color: #a3e635;
}

:deep(.token.operator),
:deep(.token.entity),
:deep(.token.url),
:deep(.language-css .token.string),
:deep(.style .token.string) {
  color: #fbbf24;
}

:deep(.token.atrule),
:deep(.token.attr-value),
:deep(.token.keyword) {
  color: #818cf8;
}

:deep(.token.function),
:deep(.token.class-name) {
  color: #60a5fa;
}

:deep(.token.regex),
:deep(.token.important),
:deep(.token.variable) {
  color: #f472b6;
}
</style>
