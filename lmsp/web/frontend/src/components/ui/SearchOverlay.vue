<script setup lang="ts">
/**
 * Universal Search Overlay
 * ========================
 *
 * Full-screen search with rich result rendering.
 * Keyboard shortcut: Cmd/Ctrl + K
 */

import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useSearchStore, type SearchResult } from '@/stores/search'
import { useGamepadNav } from '@/composables/useGamepadNav'

const router = useRouter()
const searchStore = useSearchStore()
const inputRef = ref<HTMLInputElement | null>(null)
const selectedIndex = ref(0)

useGamepadNav({
  onBack: () => searchStore.close(),
})

// Focus input when overlay opens
watch(() => searchStore.isOpen, async (open) => {
  if (open) {
    await nextTick()
    inputRef.value?.focus()
    selectedIndex.value = 0
  }
})

// Keyboard navigation
function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    selectedIndex.value = Math.min(selectedIndex.value + 1, searchStore.results.length - 1)
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    selectedIndex.value = Math.max(selectedIndex.value - 1, 0)
  } else if (e.key === 'Enter') {
    e.preventDefault()
    selectResult(searchStore.results[selectedIndex.value])
  } else if (e.key === 'Escape') {
    searchStore.close()
  }
}

function selectResult(result: SearchResult) {
  if (result) {
    router.push(result.route)
    searchStore.close()
  }
}

function highlightMatch(text: string, query: string): string {
  if (!query) return escapeHtml(text)
  const regex = new RegExp(`(${escapeRegex(query)})`, 'gi')
  return escapeHtml(text).replace(regex, '<mark class="search-highlight">$1</mark>')
}

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}

function escapeRegex(str: string): string {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

function getTypeIcon(type: string): string {
  const icons: Record<string, string> = {
    concept: '📖',
    challenge: '🎮',
    stage: '📋',
    code: '💻',
  }
  return icons[type] || '📄'
}

function getTypeColor(type: string): string {
  const colors: Record<string, string> = {
    concept: 'var(--accent-secondary)',
    challenge: 'var(--accent-primary)',
    stage: 'var(--accent-warning)',
    code: 'var(--accent-tertiary)',
  }
  return colors[type] || 'var(--text-muted)'
}

// Global keyboard shortcut
function handleGlobalKeydown(e: KeyboardEvent) {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault()
    searchStore.open()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleGlobalKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleGlobalKeydown)
})
</script>

<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="searchStore.isOpen"
        class="search-overlay"
        @click.self="searchStore.close()"
      >
        <div class="search-modal">
          <!-- Search Input -->
          <div class="search-input-container">
            <span class="search-icon">🔍</span>
            <input
              ref="inputRef"
              type="text"
              class="search-input"
              placeholder="Search concepts, challenges, code..."
              :value="searchStore.query"
              @input="searchStore.updateQuery(($event.target as HTMLInputElement).value)"
              @keydown="handleKeydown"
            />
            <kbd class="search-shortcut">ESC</kbd>
          </div>

          <!-- Loading State -->
          <div v-if="searchStore.isIndexing" class="search-loading">
            <span class="loading-spinner"></span>
            <span>Building search index...</span>
          </div>

          <!-- Results -->
          <div v-else-if="searchStore.results.length > 0" class="search-results">
            <div
              v-for="(result, idx) in searchStore.results"
              :key="result.id"
              class="search-result gamepad-focusable"
              :class="{ 'selected': idx === selectedIndex }"
              @click="selectResult(result)"
              @mouseenter="selectedIndex = idx"
            >
              <div class="result-icon" :style="{ color: getTypeColor(result.type) }">
                {{ getTypeIcon(result.type) }}
              </div>
              <div class="result-content">
                <div class="result-title">
                  <span v-html="highlightMatch(result.title, searchStore.query)"></span>
                  <span class="result-level">Lv.{{ result.level }}</span>
                </div>
                <div class="result-subtitle">{{ result.subtitle }}</div>
                <div
                  class="result-snippet"
                  v-html="highlightMatch(result.snippet, searchStore.query)"
                ></div>
              </div>
              <div class="result-type-badge" :style="{ borderColor: getTypeColor(result.type) }">
                {{ result.type }}
              </div>
            </div>
          </div>

          <!-- Empty State -->
          <div v-else-if="searchStore.query && searchStore.isIndexed" class="search-empty">
            <span class="empty-icon">🔎</span>
            <span>No results for "{{ searchStore.query }}"</span>
          </div>

          <!-- Initial State -->
          <div v-else-if="searchStore.isIndexed" class="search-hints">
            <div class="hint-title">Quick Search</div>
            <div class="hint-examples">
              <span class="hint-tag" @click="searchStore.updateQuery('dictionary')">dictionary</span>
              <span class="hint-tag" @click="searchStore.updateQuery('for loop')">for loop</span>
              <span class="hint-tag" @click="searchStore.updateQuery('def ')">def</span>
              <span class="hint-tag" @click="searchStore.updateQuery('KeyError')">KeyError</span>
            </div>
            <div class="hint-shortcuts">
              <div><kbd>↑</kbd><kbd>↓</kbd> Navigate</div>
              <div><kbd>Enter</kbd> Select</div>
              <div><kbd>Esc</kbd> Close</div>
            </div>
          </div>

          <!-- Footer -->
          <div class="search-footer">
            <span class="footer-hint">
              <kbd>⌘K</kbd> to search anywhere
            </span>
            <span class="footer-stats" v-if="searchStore.isIndexed">
              {{ searchStore.results.length }} results
            </span>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.search-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(8px);
  z-index: 100;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 10vh;
}

.search-modal {
  width: 100%;
  max-width: 640px;
  background: var(--oled-panel);
  border: 1px solid var(--oled-border);
  border-radius: 1rem;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

/* Search Input */
.search-input-container {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--oled-border);
}

.search-icon {
  font-size: 1.25rem;
  opacity: 0.6;
}

.search-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  font-size: 1.125rem;
  color: var(--text-primary);
}

.search-input::placeholder {
  color: var(--text-muted);
}

.search-shortcut {
  padding: 0.25rem 0.5rem;
  background: var(--oled-muted);
  border-radius: 0.25rem;
  font-size: 0.75rem;
  color: var(--text-muted);
}

/* Loading */
.search-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 2rem;
  color: var(--text-muted);
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--oled-border);
  border-top-color: var(--accent-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Results */
.search-results {
  max-height: 60vh;
  overflow-y: auto;
}

.search-result {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.875rem 1.25rem;
  cursor: pointer;
  transition: background 0.15s;
  border-bottom: 1px solid var(--oled-border);
}

.search-result:last-child {
  border-bottom: none;
}

.search-result:hover,
.search-result.selected {
  background: var(--oled-muted);
}

.result-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
  width: 2rem;
  text-align: center;
}

.result-content {
  flex: 1;
  min-width: 0;
}

.result-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: var(--text-primary);
}

.result-level {
  font-size: 0.625rem;
  padding: 0.125rem 0.375rem;
  background: var(--oled-muted);
  border-radius: 0.25rem;
  color: var(--text-muted);
  font-family: monospace;
}

.result-subtitle {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 0.125rem;
}

.result-snippet {
  font-size: 0.8125rem;
  color: var(--text-secondary);
  margin-top: 0.375rem;
  line-height: 1.4;
  font-family: 'Fira Code', monospace;
  white-space: pre-wrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-height: 2.8em;
}

.result-type-badge {
  font-size: 0.625rem;
  padding: 0.125rem 0.375rem;
  border: 1px solid;
  border-radius: 0.25rem;
  text-transform: uppercase;
  color: var(--text-muted);
  flex-shrink: 0;
}

:deep(.search-highlight) {
  background: rgba(0, 255, 136, 0.3);
  color: var(--accent-primary);
  padding: 0 0.125rem;
  border-radius: 0.125rem;
}

/* Empty State */
.search-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 2rem;
  color: var(--text-muted);
}

.empty-icon {
  font-size: 2rem;
  opacity: 0.5;
}

/* Hints */
.search-hints {
  padding: 1.5rem;
}

.hint-title {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
  margin-bottom: 0.75rem;
}

.hint-examples {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.hint-tag {
  padding: 0.375rem 0.75rem;
  background: var(--oled-muted);
  border: 1px solid var(--oled-border);
  border-radius: 9999px;
  font-size: 0.875rem;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.15s;
}

.hint-tag:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.hint-shortcuts {
  display: flex;
  gap: 1.5rem;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.hint-shortcuts kbd {
  padding: 0.125rem 0.375rem;
  background: var(--oled-muted);
  border-radius: 0.25rem;
  margin-right: 0.25rem;
}

/* Footer */
.search-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1.25rem;
  border-top: 1px solid var(--oled-border);
  background: var(--oled-black);
}

.footer-hint {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.footer-hint kbd {
  padding: 0.125rem 0.375rem;
  background: var(--oled-muted);
  border-radius: 0.25rem;
  margin-right: 0.25rem;
}

.footer-stats {
  font-size: 0.75rem;
  color: var(--text-muted);
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
