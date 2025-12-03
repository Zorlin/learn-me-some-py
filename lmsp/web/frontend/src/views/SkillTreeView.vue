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
  type: 'concept' | 'challenge'  // Node type for filtering
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
  // Challenge-specific fields
  has_try_it?: boolean
  time_to_read?: number
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
    concepts: number
    challenges: number
    mastered: number
    learning: number
    available: number
    locked: number
  }
  levels: Record<number, number>
}

type FilterMode = 'both' | 'concepts' | 'challenges'

const router = useRouter()
const gamepadStore = useGamepadStore()

const treeData = ref<SkillTreeData | null>(null)
const selectedNodeIndex = ref(0)
const isLoading = ref(true)
const viewBox = ref({ x: 0, y: 0, width: 1600, height: 1200 })
const showDetails = ref(false)
const filterMode = ref<FilterMode>('both')

// Drag state
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })

// Hold-to-force-start state (for locked challenges)
const isHolding = ref(false)
const holdProgress = ref(0)
const holdStartTime = ref(0)
const HOLD_DURATION = 1500 // 1.5 seconds to force unlock
let holdAnimationFrame: number | null = null

// Right stick panning (No Man's Sky style - "fly around" the tree)
const RIGHT_STICK_PAN_SPEED = 20 // Pixels per frame at full deflection
const STICK_DEADZONE = 0.2
let panAnimationFrame: number | null = null

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

// Type colors for node border accent
const typeColors: Record<string, string> = {
  concept: '#a855f7',  // Purple for concepts (learning/theory)
  challenge: '#22c55e',  // Green for challenges (practice/action)
}

// Get node stroke color (combines state and type)
function getNodeStrokeColor(node: SkillNode): string {
  // Primary stroke is based on state
  return stateColors[node.state]
}

// Get node inner accent (based on type)
function getNodeTypeAccent(node: SkillNode): string {
  return typeColors[node.type] || '#666'
}

// Get node icon based on type
function getNodeIcon(node: SkillNode): string {
  return node.type === 'concept' ? '📚' : '🎮'
}

// Computed filtered nodes (based on filter mode) - MUST come before selectedNode and nodesByLevel
const filteredNodes = computed(() => {
  if (!treeData.value) return []
  if (filterMode.value === 'both') return treeData.value.nodes
  return treeData.value.nodes.filter(n => n.type === filterMode.value.slice(0, -1) as 'concept' | 'challenge')
})

// Computed filtered edges (only edges between visible nodes)
const filteredEdges = computed(() => {
  if (!treeData.value) return []
  const visibleIds = new Set(filteredNodes.value.map(n => n.id))
  return treeData.value.edges.filter(e => visibleIds.has(e.from) && visibleIds.has(e.to))
})

const selectedNode = computed(() => {
  if (filteredNodes.value.length === 0) return null
  return filteredNodes.value[selectedNodeIndex.value]
})

// Get nodes grouped by level for navigation
const nodesByLevel = computed(() => {
  if (filteredNodes.value.length === 0) return new Map<number, number[]>()
  const levels = new Map<number, number[]>()
  filteredNodes.value.forEach((node, index) => {
    if (!levels.has(node.level)) {
      levels.set(node.level, [])
    }
    levels.get(node.level)!.push(index)
  })
  // Sort each level by x position
  levels.forEach((indices) => {
    indices.sort((a, b) => {
      const nodeA = filteredNodes.value[a]
      const nodeB = filteredNodes.value[b]
      return nodeA.position.x - nodeB.position.x
    })
  })
  return levels
})

async function loadSkillTree() {
  isLoading.value = true
  try {
    const response = await api.get(`/api/skill-tree?include=${filterMode.value}`)
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

// Watch filter changes and reload
watch(filterMode, () => {
  loadSkillTree()
})

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

// Force start a locked challenge (after hold completes)
function forceStartChallenge() {
  if (!selectedNode.value) return
  if (selectedNode.value.challenges.starter) {
    router.push(`/challenge/${selectedNode.value.challenges.starter}`)
  }
}

// Hold-to-force-start logic
function startHold() {
  if (!selectedNode.value) return
  if (selectedNode.value.state !== 'locked') return
  if (!selectedNode.value.challenges.starter) return

  isHolding.value = true
  holdStartTime.value = performance.now()
  holdProgress.value = 0

  function updateHold() {
    if (!isHolding.value) return

    const elapsed = performance.now() - holdStartTime.value
    holdProgress.value = Math.min(100, (elapsed / HOLD_DURATION) * 100)

    if (elapsed >= HOLD_DURATION) {
      // Hold complete - force start!
      cancelHold()
      forceStartChallenge()
      return
    }

    holdAnimationFrame = requestAnimationFrame(updateHold)
  }

  holdAnimationFrame = requestAnimationFrame(updateHold)
}

function cancelHold() {
  isHolding.value = false
  holdProgress.value = 0
  if (holdAnimationFrame !== null) {
    cancelAnimationFrame(holdAnimationFrame)
    holdAnimationFrame = null
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

  // A button handling - different for locked vs unlocked
  if (buttons.A && !prev.A) {
    // A pressed
    if (showDetails.value && selectedNode.value) {
      if (selectedNode.value.state === 'locked' && selectedNode.value.challenges.starter) {
        // Start hold for locked challenge
        startHold()
      } else {
        // Normal start for unlocked
        startChallenge()
      }
    } else {
      selectCurrentNode()
    }
  } else if (!buttons.A && prev.A) {
    // A released - cancel hold if active
    if (isHolding.value) {
      cancelHold()
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
      if (showDetails.value && selectedNode.value) {
        if (selectedNode.value.state === 'locked' && selectedNode.value.challenges.starter) {
          // Start hold for locked challenge
          if (!isHolding.value) startHold()
        } else {
          startChallenge()
        }
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

function handleKeyup(e: KeyboardEvent) {
  if (e.key === 'Enter' || e.key === ' ') {
    if (isHolding.value) {
      cancelHold()
    }
  }
}

// Left stick navigation threshold tracking
const LEFT_STICK_NAV_THRESHOLD = 0.7
let prevLeftStickMag = 0

// Right stick panning loop - "fly around" the skill tree like No Man's Sky
// Also handles left stick as D-pad equivalent for node navigation
function updatePan() {
  const { rightStick, leftStick } = gamepadStore

  // === LEFT STICK: D-pad equivalent for node navigation ===
  const leftX = leftStick.x
  const leftY = leftStick.y
  const leftMag = Math.sqrt(leftX * leftX + leftY * leftY)

  // Edge detection: only navigate when crossing threshold
  if (leftMag >= LEFT_STICK_NAV_THRESHOLD && prevLeftStickMag < LEFT_STICK_NAV_THRESHOLD) {
    // Determine primary direction
    const absX = Math.abs(leftX)
    const absY = Math.abs(leftY)

    if (absX > absY) {
      // Horizontal dominant
      if (leftX > 0) navigateRight()
      else navigateLeft()
    } else {
      // Vertical dominant
      if (leftY > 0) navigateDown()
      else navigateUp()
    }
  }
  prevLeftStickMag = leftMag

  // === RIGHT STICK: Camera pan (fly around the tree) ===
  const stickX = rightStick.x
  const stickY = rightStick.y
  const magnitude = Math.sqrt(stickX * stickX + stickY * stickY)

  if (magnitude > STICK_DEADZONE) {
    // Remap magnitude past deadzone to 0-1
    const adjustedMag = (magnitude - STICK_DEADZONE) / (1 - STICK_DEADZONE)
    // Quadratic curve for smooth feel at low deflections, fast at high
    const speed = RIGHT_STICK_PAN_SPEED * adjustedMag * adjustedMag

    // Pan the viewBox (move the "camera")
    const normX = stickX / magnitude
    const normY = stickY / magnitude
    viewBox.value.x += normX * speed
    viewBox.value.y += normY * speed
  }

  panAnimationFrame = requestAnimationFrame(updatePan)
}

onMounted(() => {
  loadSkillTree()
  window.addEventListener('keydown', handleKeydown)
  window.addEventListener('keyup', handleKeyup)
  // Start right stick pan loop
  panAnimationFrame = requestAnimationFrame(updatePan)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  window.removeEventListener('keyup', handleKeyup)
  cancelHold() // Clean up any pending hold animation
  // Clean up pan animation
  if (panAnimationFrame !== null) {
    cancelAnimationFrame(panAnimationFrame)
  }
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

      <div class="tree-title-and-filter">
        <span class="text-2xl font-bold text-accent-primary">Skill Tree</span>
        <!-- Filter Slider -->
        <div class="filter-slider">
          <button
            class="filter-btn"
            :class="{ active: filterMode === 'concepts' }"
            @click="filterMode = 'concepts'"
          >
            <span class="filter-icon">📚</span>
            <span>Concepts</span>
            <span v-if="treeData" class="filter-count">{{ treeData.summary.concepts }}</span>
          </button>
          <button
            class="filter-btn both"
            :class="{ active: filterMode === 'both' }"
            @click="filterMode = 'both'"
          >
            <span>Both</span>
          </button>
          <button
            class="filter-btn"
            :class="{ active: filterMode === 'challenges' }"
            @click="filterMode = 'challenges'"
          >
            <span class="filter-icon">🎮</span>
            <span>Challenges</span>
            <span v-if="treeData" class="filter-count">{{ treeData.summary.challenges }}</span>
          </button>
        </div>
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
          v-for="(edge, i) in filteredEdges"
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
          v-for="(node, index) in filteredNodes"
          :key="node.id"
          :transform="`translate(${node.position.x}, ${node.position.y})`"
          class="skill-node"
          :class="{
            [node.state]: true,
            [node.type]: true,
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

          <!-- Type indicator ring (inner) -->
          <circle
            :r="getNodeRadius(node) + 3"
            fill="none"
            :stroke="typeColors[node.type]"
            stroke-width="2"
            stroke-opacity="0.5"
          />

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

          <!-- Type icon -->
          <text
            y="-10"
            text-anchor="middle"
            font-size="14"
          >
            {{ getNodeIcon(node) }}
          </text>

          <!-- Level badge -->
          <text
            y="8"
            text-anchor="middle"
            :fill="levelColors[node.level]"
            font-size="10"
            font-weight="bold"
          >
            L{{ node.level }}
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

        <!-- Action - Normal unlocked button -->
        <button
          v-if="selectedNode.state !== 'locked' && selectedNode.challenges.starter"
          class="start-btn mt-6"
          @click="startChallenge"
        >
          <span class="gamepad-hint-button a">A</span>
          Start Challenge
        </button>

        <!-- Action - Locked but available to force-start -->
        <div v-else-if="selectedNode.state === 'locked' && selectedNode.challenges.starter" class="mt-6">
          <button
            class="force-start-btn"
            @mousedown="startHold"
            @mouseup="cancelHold"
            @mouseleave="cancelHold"
            @touchstart.prevent="startHold"
            @touchend="cancelHold"
            @touchcancel="cancelHold"
          >
            <!-- Progress fill -->
            <div class="force-progress" :style="{ width: `${holdProgress}%` }" />
            <span class="force-content">
              <span class="gamepad-hint-button a">A</span>
              <span>{{ isHolding ? 'Hold...' : 'Try Anyway' }}</span>
            </span>
          </button>
          <div class="force-hint">
            Not recommended yet — but you can give it a go!
          </div>
        </div>

        <!-- No challenge available -->
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
  z-index: 50;  /* Above app header (z-40) */
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

.tree-title-and-filter {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.filter-slider {
  display: flex;
  gap: 0.25rem;
  padding: 0.25rem;
  background: var(--oled-panel);
  border: 1px solid var(--oled-border);
  border-radius: 0.5rem;
}

.filter-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  color: var(--text-muted);
  transition: all 0.15s;
}

.filter-btn:hover {
  background: var(--oled-muted);
  color: var(--text-secondary);
}

.filter-btn.active {
  background: var(--accent-primary);
  color: black;
  font-weight: 600;
}

.filter-btn.both.active {
  background: var(--accent-secondary);
}

.filter-icon {
  font-size: 1rem;
}

.filter-count {
  padding: 0.125rem 0.375rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 0.25rem;
  font-size: 0.625rem;
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

/* Force-start button for locked challenges - hollow with green border */
.force-start-btn {
  width: 100%;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.875rem;
  border-radius: 0.5rem;
  background: transparent;
  border: 2px solid var(--accent-primary);
  color: var(--accent-primary);
  font-weight: bold;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.force-start-btn:hover {
  background: rgba(0, 255, 136, 0.1);
}

.force-start-btn:active {
  transform: scale(0.98);
}

/* Progress fill that sweeps left to right */
.force-progress {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background: var(--accent-primary);
  opacity: 0.3;
  transition: width 0.05s linear;
  pointer-events: none;
}

.force-content {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.force-hint {
  margin-top: 0.5rem;
  text-align: center;
  font-size: 0.75rem;
  color: var(--text-muted);
  font-style: italic;
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
