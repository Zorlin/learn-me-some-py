<script setup lang="ts">
/**
 * Full-Page Skill Tree View
 * =========================
 *
 * Uses the WHOLE page. Full gamepad navigation.
 * Click-to-drag panning. Floating details panel.
 */

import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api/client'
import { useGamepadStore } from '@/stores/gamepad'

interface SkillNode {
  id: string
  name: string
  level: number
  mastery: number
  mastery_percent: number
  mastery_hint?: string
  description: string
  prerequisites: string[]
  unlocks: string[]
  challenges: {
    starter: string | null
    intermediate: string | null
    mastery: string | null
  }
  position: { x: number; y: number }
  state: 'mastered' | 'learning' | 'available' | 'locked'
}

interface SkillEdge {
  from: string
  to: string
}

interface SkillTreeData {
  nodes: SkillNode[]
  edges: SkillEdge[]
  summary: {
    total: number
    mastered: number
    learning: number
    available: number
    locked: number
  }
  levels: Record<number, number>
}

const router = useRouter()
const gamepadStore = useGamepadStore()

const treeData = ref<SkillTreeData | null>(null)
const selectedNodeIndex = ref(0)
const isLoading = ref(true)
const viewBox = ref({ x: 0, y: 0, width: 1600, height: 1200 })
const showDetails = ref(false)

// Drag state
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })

// Level colors
const levelColors: Record<number, string> = {
  0: '#00ff88',
  1: '#0088ff',
  2: '#00ffff',
  3: '#ff00ff',
  4: '#ffaa00',
  5: '#ff4444',
  6: '#ffffff',
}

// State colors
const stateColors: Record<string, string> = {
  mastered: '#00ff88',
  learning: '#ffaa00',
  available: '#0088ff',
  locked: '#333333',
}

const selectedNode = computed(() => {
  if (!treeData.value || treeData.value.nodes.length === 0) return null
  return treeData.value.nodes[selectedNodeIndex.value]
})

// Get nodes grouped by level for navigation
const nodesByLevel = computed(() => {
  if (!treeData.value) return new Map<number, number[]>()
  const levels = new Map<number, number[]>()
  treeData.value.nodes.forEach((node, index) => {
    if (!levels.has(node.level)) {
      levels.set(node.level, [])
    }
    levels.get(node.level)!.push(index)
  })
  // Sort each level by x position
  levels.forEach((indices) => {
    indices.sort((a, b) => {
      const nodeA = treeData.value!.nodes[a]
      const nodeB = treeData.value!.nodes[b]
      return nodeA.position.x - nodeB.position.x
    })
  })
  return levels
})

async function loadSkillTree() {
  isLoading.value = true
  try {
    const response = await api.get('/api/skill-tree')
    treeData.value = response.data
    if (treeData.value) {
      layoutNodes(treeData.value.nodes)
      centerOnNode(0)
    }
  } catch (e) {
    console.error('Failed to load skill tree:', e)
  } finally {
    isLoading.value = false
  }
}

function layoutNodes(nodes: SkillNode[]) {
  const levels: Map<number, SkillNode[]> = new Map()
  for (const node of nodes) {
    if (!levels.has(node.level)) {
      levels.set(node.level, [])
    }
    levels.get(node.level)!.push(node)
  }

  const levelHeight = 200
  const nodeSpacing = 180
  const centerX = viewBox.value.width / 2

  for (const [level, levelNodes] of levels) {
    const totalWidth = (levelNodes.length - 1) * nodeSpacing
    const startX = centerX - totalWidth / 2

    levelNodes.forEach((node, i) => {
      node.position = {
        x: startX + i * nodeSpacing,
        y: 120 + level * levelHeight,
      }
    })
  }
}

function centerOnNode(index: number) {
  if (!treeData.value) return
  const node = treeData.value.nodes[index]
  if (!node) return

  viewBox.value.x = node.position.x - viewBox.value.width / 2
  viewBox.value.y = node.position.y - viewBox.value.height / 2
}

function getNodeRadius(node: SkillNode): number {
  return 35 + node.mastery * 5
}

function getEdgePath(edge: SkillEdge): string {
  if (!treeData.value) return ''
  const fromNode = treeData.value.nodes.find(n => n.id === edge.from)
  const toNode = treeData.value.nodes.find(n => n.id === edge.to)
  if (!fromNode || !toNode) return ''

  const fromRadius = getNodeRadius(fromNode)
  const toRadius = getNodeRadius(toNode)
  const x1 = fromNode.position.x
  const y1 = fromNode.position.y + fromRadius
  const x2 = toNode.position.x
  const y2 = toNode.position.y - toRadius
  const cy = (y1 + y2) / 2

  return `M ${x1} ${y1} C ${x1} ${cy}, ${x2} ${cy}, ${x2} ${y2}`
}

function getEdgeColor(edge: SkillEdge): string {
  if (!treeData.value) return '#333'
  const toNode = treeData.value.nodes.find(n => n.id === edge.to)
  if (!toNode) return '#333'
  return stateColors[toNode.state] || '#333'
}

// Pan handling - click to drag
function handleMouseDown(e: MouseEvent) {
  // Don't start drag if clicking on a node
  if ((e.target as Element).closest('.skill-node')) return
  isDragging.value = true
  dragStart.value = { x: e.clientX, y: e.clientY }
}

function handleMouseMove(e: MouseEvent) {
  if (!isDragging.value) return

  const dx = e.clientX - dragStart.value.x
  const dy = e.clientY - dragStart.value.y

  viewBox.value.x -= dx * 2
  viewBox.value.y -= dy * 2

  dragStart.value = { x: e.clientX, y: e.clientY }
}

function handleMouseUp() {
  isDragging.value = false
}

// Zoom handling
function handleWheel(e: WheelEvent) {
  e.preventDefault()
  const scale = e.deltaY > 0 ? 1.1 : 0.9
  viewBox.value.width *= scale
  viewBox.value.height *= scale
}

// Gamepad navigation - uses CORRECT button names from store
function navigateUp() {
  if (!treeData.value || !selectedNode.value) return
  const currentLevel = selectedNode.value.level
  if (currentLevel <= 0) return

  const aboveIndices = nodesByLevel.value.get(currentLevel - 1)
  if (!aboveIndices || aboveIndices.length === 0) return

  const currentX = selectedNode.value.position.x
  let closestIndex = aboveIndices[0]
  let closestDist = Infinity

  for (const idx of aboveIndices) {
    const node = treeData.value.nodes[idx]
    const dist = Math.abs(node.position.x - currentX)
    if (dist < closestDist) {
      closestDist = dist
      closestIndex = idx
    }
  }

  selectedNodeIndex.value = closestIndex
  centerOnNode(closestIndex)
}

function navigateDown() {
  if (!treeData.value || !selectedNode.value) return
  const currentLevel = selectedNode.value.level
  const maxLevel = Math.max(...Array.from(nodesByLevel.value.keys()))
  if (currentLevel >= maxLevel) return

  const belowIndices = nodesByLevel.value.get(currentLevel + 1)
  if (!belowIndices || belowIndices.length === 0) return

  const currentX = selectedNode.value.position.x
  let closestIndex = belowIndices[0]
  let closestDist = Infinity

  for (const idx of belowIndices) {
    const node = treeData.value.nodes[idx]
    const dist = Math.abs(node.position.x - currentX)
    if (dist < closestDist) {
      closestDist = dist
      closestIndex = idx
    }
  }

  selectedNodeIndex.value = closestIndex
  centerOnNode(closestIndex)
}

function navigateLeft() {
  if (!treeData.value || !selectedNode.value) return
  const currentLevel = selectedNode.value.level
  const levelIndices = nodesByLevel.value.get(currentLevel)
  if (!levelIndices || levelIndices.length <= 1) return

  const currentPosInLevel = levelIndices.indexOf(selectedNodeIndex.value)
  if (currentPosInLevel > 0) {
    selectedNodeIndex.value = levelIndices[currentPosInLevel - 1]
    centerOnNode(selectedNodeIndex.value)
  }
}

function navigateRight() {
  if (!treeData.value || !selectedNode.value) return
  const currentLevel = selectedNode.value.level
  const levelIndices = nodesByLevel.value.get(currentLevel)
  if (!levelIndices || levelIndices.length <= 1) return

  const currentPosInLevel = levelIndices.indexOf(selectedNodeIndex.value)
  if (currentPosInLevel < levelIndices.length - 1) {
    selectedNodeIndex.value = levelIndices[currentPosInLevel + 1]
    centerOnNode(selectedNodeIndex.value)
  }
}

function selectCurrentNode() {
  showDetails.value = true
}

function startChallenge() {
  if (!selectedNode.value) return
  if (selectedNode.value.state === 'locked') return
  if (selectedNode.value.challenges.starter) {
    router.push(`/challenge/${selectedNode.value.challenges.starter}`)
  }
}

function goBack() {
  if (showDetails.value) {
    showDetails.value = false
  } else {
    router.push('/progress')
  }
}

function clickNode(index: number) {
  selectedNodeIndex.value = index
  showDetails.value = true
}

// Track previous button state for edge detection
const prevButtonState = ref<Record<string, boolean>>({})

// Watch gamepad buttons - CORRECT NAMES: DPadUp, DPadDown, DPadLeft, DPadRight (NO HYPHENS)
watch(() => gamepadStore.buttons, (buttons) => {
  if (isLoading.value) return

  const prev = prevButtonState.value

  // D-pad navigation - edge detection (only trigger on button down)
  if (buttons.DPadUp && !prev.DPadUp) navigateUp()
  if (buttons.DPadDown && !prev.DPadDown) navigateDown()
  if (buttons.DPadLeft && !prev.DPadLeft) navigateLeft()
  if (buttons.DPadRight && !prev.DPadRight) navigateRight()

  // A to select/confirm
  if (buttons.A && !prev.A) {
    if (showDetails.value) {
      startChallenge()
    } else {
      selectCurrentNode()
    }
  }

  // B to go back
  if (buttons.B && !prev.B) {
    goBack()
  }

  // Update previous state
  prevButtonState.value = { ...buttons }
}, { deep: true })

// Keyboard navigation
function handleKeydown(e: KeyboardEvent) {
  if (isLoading.value) return

  switch (e.key) {
    case 'ArrowUp':
    case 'w':
    case 'W':
      e.preventDefault()
      navigateUp()
      break
    case 'ArrowDown':
    case 's':
    case 'S':
      e.preventDefault()
      navigateDown()
      break
    case 'ArrowLeft':
    case 'a':
    case 'A':
      e.preventDefault()
      navigateLeft()
      break
    case 'ArrowRight':
    case 'd':
    case 'D':
      e.preventDefault()
      navigateRight()
      break
    case 'Enter':
    case ' ':
      e.preventDefault()
      if (showDetails.value) {
        startChallenge()
      } else {
        selectCurrentNode()
      }
      break
    case 'Escape':
      e.preventDefault()
      goBack()
      break
  }
}

onMounted(() => {
  loadSkillTree()
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<template>
  <div class="skill-tree-fullpage">
    <!-- Header -->
    <div class="tree-header">
      <button class="back-btn" @click="goBack">
        <span class="gamepad-hint-button b">B</span>
        Back
      </button>

      <div class="tree-title">
        <span class="text-2xl font-bold text-accent-primary">Skill Tree</span>
      </div>

      <div v-if="treeData" class="tree-stats">
        <div class="stat">
          <span class="stat-value text-accent-primary">{{ treeData.summary.mastered }}</span>
          <span class="stat-label">Mastered</span>
        </div>
        <div class="stat">
          <span class="stat-value text-accent-warning">{{ treeData.summary.learning }}</span>
          <span class="stat-label">Learning</span>
        </div>
        <div class="stat">
          <span class="stat-value text-accent-secondary">{{ treeData.summary.available }}</span>
          <span class="stat-label">Available</span>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="loading-state">
      <div class="text-accent-primary animate-pulse text-xl">Loading skill tree...</div>
    </div>

    <!-- SVG Tree -->
    <svg
      v-else-if="treeData"
      class="skill-tree-svg"
      :class="{ dragging: isDragging }"
      :viewBox="`${viewBox.x} ${viewBox.y} ${viewBox.width} ${viewBox.height}`"
      preserveAspectRatio="xMidYMid meet"
      @mousedown="handleMouseDown"
      @mousemove="handleMouseMove"
      @mouseup="handleMouseUp"
      @mouseleave="handleMouseUp"
      @wheel="handleWheel"
    >
      <defs>
        <pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse">
          <path d="M 50 0 L 0 0 0 50" fill="none" stroke="#1a1a1a" stroke-width="0.5"/>
        </pattern>
        <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>

      <rect x="-5000" y="-5000" width="10000" height="10000" fill="url(#grid)"/>

      <!-- Level labels -->
      <g class="level-labels">
        <text
          v-for="level in 7"
          :key="`level-${level - 1}`"
          :x="viewBox.x + 30"
          :y="120 + (level - 1) * 200"
          fill="#444"
          font-size="16"
          font-weight="bold"
        >
          Level {{ level - 1 }}
        </text>
      </g>

      <!-- Edges -->
      <g class="edges">
        <path
          v-for="(edge, i) in treeData.edges"
          :key="`edge-${i}`"
          :d="getEdgePath(edge)"
          :stroke="getEdgeColor(edge)"
          stroke-width="3"
          fill="none"
          stroke-opacity="0.5"
        />
      </g>

      <!-- Nodes -->
      <g class="nodes">
        <g
          v-for="(node, index) in treeData.nodes"
          :key="node.id"
          :transform="`translate(${node.position.x}, ${node.position.y})`"
          class="skill-node"
          :class="{
            [node.state]: true,
            selected: index === selectedNodeIndex
          }"
          @click.stop="clickNode(index)"
        >
          <!-- Selection ring -->
          <circle
            v-if="index === selectedNodeIndex"
            :r="getNodeRadius(node) + 10"
            fill="none"
            stroke="#ffffff"
            stroke-width="2"
            stroke-dasharray="6 4"
          >
            <animateTransform
              attributeName="transform"
              type="rotate"
              from="0"
              to="360"
              dur="8s"
              repeatCount="indefinite"
            />
          </circle>

          <!-- Node circle -->
          <circle
            :r="getNodeRadius(node)"
            :fill="node.state === 'locked' ? '#111' : '#000'"
            :stroke="stateColors[node.state]"
            stroke-width="4"
            :filter="node.state === 'mastered' ? 'url(#glow)' : ''"
          />

          <!-- Mastery ring -->
          <circle
            v-if="node.mastery > 0 && node.state !== 'mastered'"
            :r="getNodeRadius(node) - 6"
            fill="none"
            :stroke="stateColors[node.state]"
            stroke-width="5"
            :stroke-dasharray="`${node.mastery_percent * 0.628} 100`"
            transform="rotate(-90)"
            stroke-linecap="round"
          />

          <!-- Level -->
          <text
            y="-10"
            text-anchor="middle"
            :fill="levelColors[node.level]"
            font-size="12"
            font-weight="bold"
          >
            L{{ node.level }}
          </text>

          <!-- Mastery -->
          <text
            y="10"
            text-anchor="middle"
            :fill="stateColors[node.state]"
            font-size="16"
            font-weight="bold"
          >
            {{ node.mastery }}/4
          </text>

          <!-- Name -->
          <text
            :y="getNodeRadius(node) + 20"
            text-anchor="middle"
            fill="#aaa"
            font-size="13"
            font-weight="500"
          >
            {{ node.name.length > 16 ? node.name.substring(0, 14) + '...' : node.name }}
          </text>
        </g>
      </g>
    </svg>

    <!-- Floating Details Panel (right side) -->
    <Transition name="slide">
      <div v-if="showDetails && selectedNode" class="node-details oled-panel">
        <div class="details-header">
          <div class="flex items-center gap-3">
            <div
              class="level-badge"
              :style="{ borderColor: levelColors[selectedNode.level], color: levelColors[selectedNode.level] }"
            >
              L{{ selectedNode.level }}
            </div>
            <div>
              <h3 class="text-lg font-bold">{{ selectedNode.name }}</h3>
              <div class="text-sm capitalize" :style="{ color: stateColors[selectedNode.state] }">
                {{ selectedNode.state }}
              </div>
            </div>
          </div>
          <button class="close-btn" @click="showDetails = false">×</button>
        </div>

        <p class="text-text-secondary text-sm mt-3">{{ selectedNode.description }}</p>

        <!-- Mastery -->
        <div class="mastery-section mt-4">
          <div class="flex justify-between text-sm mb-2">
            <span class="text-text-muted">Mastery Progress</span>
            <span :style="{ color: stateColors[selectedNode.state] }">
              {{ selectedNode.mastery }}/4 ({{ selectedNode.mastery_percent }}%)
            </span>
          </div>
          <div class="progress-bar">
            <div
              class="progress-fill"
              :style="{ width: `${selectedNode.mastery_percent}%`, background: stateColors[selectedNode.state] }"
            />
          </div>
          <div v-if="selectedNode.mastery_hint" class="mastery-hint mt-3">
            <span class="hint-icon">💡</span>
            <span>{{ selectedNode.mastery_hint }}</span>
          </div>
        </div>

        <!-- Prerequisites -->
        <div v-if="selectedNode.prerequisites.length > 0" class="mt-4">
          <div class="text-sm text-text-muted mb-2">Prerequisites</div>
          <div class="flex flex-wrap gap-2">
            <span v-for="prereq in selectedNode.prerequisites" :key="prereq" class="prereq-tag">
              {{ prereq }}
            </span>
          </div>
        </div>

        <!-- Unlocks -->
        <div v-if="selectedNode.unlocks.length > 0" class="mt-4">
          <div class="text-sm text-text-muted mb-2">Unlocks</div>
          <div class="flex flex-wrap gap-2">
            <span v-for="unlock in selectedNode.unlocks" :key="unlock" class="unlock-tag">
              {{ unlock }}
            </span>
          </div>
        </div>

        <!-- Action -->
        <button
          v-if="selectedNode.state !== 'locked' && selectedNode.challenges.starter"
          class="start-btn mt-6"
          @click="startChallenge"
        >
          <span class="gamepad-hint-button a">A</span>
          Start Challenge
        </button>
        <div v-else-if="selectedNode.state === 'locked'" class="locked-msg mt-6">
          Complete prerequisites to unlock
        </div>
      </div>
    </Transition>

    <!-- Controls Hint -->
    <div class="controls-hint">
      <div class="hint-item">
        <span class="hint-key">D-Pad</span>
        <span>Navigate</span>
      </div>
      <div class="hint-item">
        <span class="gamepad-hint-button a">A</span>
        <span>Select</span>
      </div>
      <div class="hint-item">
        <span class="gamepad-hint-button b">B</span>
        <span>Back</span>
      </div>
      <div class="hint-item">
        <span class="hint-key">Drag</span>
        <span>Pan</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.skill-tree-fullpage {
  position: fixed;
  inset: 0;
  background: #000;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.tree-header {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  background: linear-gradient(to bottom, #000 0%, #000 60%, transparent 100%);
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  background: var(--oled-panel);
  border: 1px solid var(--oled-border);
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.back-btn:hover {
  border-color: var(--accent-primary);
  color: white;
}

.tree-stats {
  display: flex;
  gap: 2rem;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: bold;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.loading-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.skill-tree-svg {
  flex: 1;
  width: 100%;
  height: 100%;
  cursor: grab;
}

.skill-tree-svg.dragging {
  cursor: grabbing;
}

.skill-node {
  cursor: pointer;
}

.skill-node circle {
  transition: all 0.2s ease;
}

.skill-node:hover circle {
  transform: scale(1.05);
}

.skill-node.selected circle {
  stroke-width: 5;
}

.skill-node.locked {
  opacity: 0.5;
}

/* Floating details panel - RIGHT SIDE */
.node-details {
  position: absolute;
  bottom: 5rem;
  right: 1.5rem;
  width: 20rem;
  z-index: 30;
  max-height: calc(100vh - 10rem);
  overflow-y: auto;
}

.details-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.level-badge {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--oled-black);
  border: 3px solid;
  font-weight: bold;
  font-size: 0.75rem;
}

.close-btn {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--oled-muted);
  color: var(--text-muted);
  font-size: 1.25rem;
  line-height: 1;
}

.close-btn:hover {
  background: var(--oled-border);
  color: white;
}

.progress-bar {
  height: 0.5rem;
  border-radius: 9999px;
  background: var(--oled-muted);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 9999px;
  transition: width 0.5s ease;
}

.mastery-hint {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.75rem;
  border-radius: 0.5rem;
  background: rgba(255, 170, 0, 0.1);
  border: 1px solid rgba(255, 170, 0, 0.2);
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.hint-icon {
  flex-shrink: 0;
}

.prereq-tag {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  background: var(--oled-muted);
  color: var(--text-secondary);
  font-size: 0.75rem;
}

.unlock-tag {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  background: rgba(0, 255, 136, 0.2);
  color: var(--accent-primary);
  font-size: 0.75rem;
}

.start-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 0.875rem;
  border-radius: 0.5rem;
  background: var(--accent-primary);
  color: #000;
  font-weight: bold;
  font-size: 1rem;
}

.start-btn:hover {
  filter: brightness(1.1);
}

.locked-msg {
  text-align: center;
  padding: 0.875rem;
  color: var(--text-muted);
  font-style: italic;
  font-size: 0.875rem;
}

.controls-hint {
  position: absolute;
  bottom: 1rem;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
  display: flex;
  gap: 2rem;
  padding: 0.75rem 1.5rem;
  border-radius: 9999px;
  background: rgba(0, 0, 0, 0.8);
  border: 1px solid var(--oled-border);
}

.hint-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-muted);
}

.hint-key {
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  background: var(--oled-muted);
  font-size: 0.75rem;
  font-weight: bold;
}

.gamepad-hint-button {
  width: 1.5rem;
  height: 1.5rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: bold;
  background: var(--oled-panel);
  border: 1px solid var(--oled-border);
}

.gamepad-hint-button.a {
  color: #22c55e;
  border-color: rgba(34, 197, 94, 0.5);
}

.gamepad-hint-button.b {
  color: #ef4444;
  border-color: rgba(239, 68, 68, 0.5);
}

/* Transitions - slide from right */
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(20px);
  opacity: 0;
}
</style>
