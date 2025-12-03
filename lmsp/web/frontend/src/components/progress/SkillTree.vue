<script setup lang="ts">
/**
 * Skill Tree Component
 * ====================
 *
 * Skyrim/WoW-style skill tree visualization.
 * Shows Python concepts as nodes in a DAG, with mastery levels.
 */

import { ref, onMounted, computed, watch } from 'vue'
import { api } from '@/api/client'

interface SkillNode {
  id: string
  name: string
  level: number
  mastery: number
  mastery_percent: number
  mastery_hint?: string  // 60-140 char hint for next mastery stage
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

const emit = defineEmits<{
  'select-node': [node: SkillNode]
}>()

const treeData = ref<SkillTreeData | null>(null)
const selectedNode = ref<SkillNode | null>(null)
const isLoading = ref(true)
const viewBox = ref({ x: 0, y: 0, width: 1600, height: 1200 })
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })

// Level colors
const levelColors: Record<number, string> = {
  0: '#00ff88', // Neon green - basics
  1: '#0088ff', // Electric blue
  2: '#00ffff', // Cyan
  3: '#ff00ff', // Magenta
  4: '#ffaa00', // Orange
  5: '#ff4444', // Red
  6: '#ffffff', // White - mastery
}

// State colors
const stateColors: Record<string, string> = {
  mastered: '#00ff88',
  learning: '#ffaa00',
  available: '#0088ff',
  locked: '#333333',
}

async function loadSkillTree() {
  isLoading.value = true
  try {
    const response = await api.get('/api/skill-tree')
    treeData.value = response.data

    // Recalculate positions for better layout
    if (treeData.value) {
      layoutNodes(treeData.value.nodes)
    }
  } catch (e) {
    console.error('Failed to load skill tree:', e)
  } finally {
    isLoading.value = false
  }
}

function layoutNodes(nodes: SkillNode[]) {
  // Group nodes by level
  const levels: Map<number, SkillNode[]> = new Map()
  for (const node of nodes) {
    if (!levels.has(node.level)) {
      levels.set(node.level, [])
    }
    levels.get(node.level)!.push(node)
  }

  // Layout each level horizontally
  const levelHeight = 180
  const nodeSpacing = 160
  const centerX = viewBox.value.width / 2

  for (const [level, levelNodes] of levels) {
    const totalWidth = (levelNodes.length - 1) * nodeSpacing
    const startX = centerX - totalWidth / 2

    levelNodes.forEach((node, i) => {
      node.position = {
        x: startX + i * nodeSpacing,
        y: 80 + level * levelHeight,
      }
    })
  }
}

function selectNode(node: SkillNode) {
  selectedNode.value = node
  emit('select-node', node)
}

function getNodeRadius(node: SkillNode): number {
  // Larger nodes for higher mastery
  return 30 + node.mastery * 5
}

function getEdgePath(edge: SkillEdge): string {
  if (!treeData.value) return ''

  const fromNode = treeData.value.nodes.find(n => n.id === edge.from)
  const toNode = treeData.value.nodes.find(n => n.id === edge.to)

  if (!fromNode || !toNode) return ''

  // Curved path from bottom of fromNode to top of toNode
  const fromRadius = getNodeRadius(fromNode)
  const toRadius = getNodeRadius(toNode)

  const x1 = fromNode.position.x
  const y1 = fromNode.position.y + fromRadius
  const x2 = toNode.position.x
  const y2 = toNode.position.y - toRadius

  // Control points for bezier curve
  const cy = (y1 + y2) / 2

  return `M ${x1} ${y1} C ${x1} ${cy}, ${x2} ${cy}, ${x2} ${y2}`
}

function getEdgeColor(edge: SkillEdge): string {
  if (!treeData.value) return '#333'

  const toNode = treeData.value.nodes.find(n => n.id === edge.to)
  if (!toNode) return '#333'

  return stateColors[toNode.state] || '#333'
}

// Pan handling
function handleMouseDown(e: MouseEvent) {
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

onMounted(() => {
  loadSkillTree()
})

const masteryPercent = computed(() => {
  if (!treeData.value) return 0
  return Math.round((treeData.value.summary.mastered / treeData.value.summary.total) * 100)
})
</script>

<template>
  <div class="skill-tree-container">
    <!-- Header Stats -->
    <div class="tree-header">
      <div class="tree-title">
        <span class="text-2xl font-bold text-accent-primary">Skill Tree</span>
        <span class="text-text-muted ml-2">Python Mastery Path</span>
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
        <div class="stat">
          <span class="stat-value text-text-muted">{{ treeData.summary.locked }}</span>
          <span class="stat-label">Locked</span>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-state">
      <div class="text-accent-primary animate-pulse">Loading skill tree...</div>
    </div>

    <!-- SVG Skill Tree -->
    <svg
      v-else-if="treeData"
      class="skill-tree-svg"
      :viewBox="`${viewBox.x} ${viewBox.y} ${viewBox.width} ${viewBox.height}`"
      @mousedown="handleMouseDown"
      @mousemove="handleMouseMove"
      @mouseup="handleMouseUp"
      @mouseleave="handleMouseUp"
      @wheel="handleWheel"
    >
      <!-- Background grid -->
      <defs>
        <pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse">
          <path d="M 50 0 L 0 0 0 50" fill="none" stroke="#1a1a1a" stroke-width="0.5"/>
        </pattern>

        <!-- Glow filter for mastered nodes -->
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
          :x="20"
          :y="80 + (level - 1) * 180"
          class="level-label"
          fill="#555"
          font-size="14"
        >
          Level {{ level - 1 }}
        </text>
      </g>

      <!-- Edges (drawn first, behind nodes) -->
      <g class="edges">
        <path
          v-for="(edge, i) in treeData.edges"
          :key="`edge-${i}`"
          :d="getEdgePath(edge)"
          :stroke="getEdgeColor(edge)"
          stroke-width="2"
          fill="none"
          stroke-opacity="0.4"
        />
      </g>

      <!-- Nodes -->
      <g class="nodes">
        <g
          v-for="node in treeData.nodes"
          :key="node.id"
          :transform="`translate(${node.position.x}, ${node.position.y})`"
          class="skill-node"
          :class="[node.state, { selected: selectedNode?.id === node.id }]"
          @click="selectNode(node)"
        >
          <!-- Node background circle -->
          <circle
            :r="getNodeRadius(node)"
            :fill="node.state === 'locked' ? '#111' : '#000'"
            :stroke="stateColors[node.state]"
            stroke-width="3"
            :filter="node.state === 'mastered' ? 'url(#glow)' : ''"
          />

          <!-- Mastery progress ring -->
          <circle
            v-if="node.mastery > 0 && node.state !== 'mastered'"
            :r="getNodeRadius(node) - 5"
            fill="none"
            :stroke="stateColors[node.state]"
            stroke-width="4"
            :stroke-dasharray="`${node.mastery_percent * 0.628} 100`"
            transform="rotate(-90)"
            stroke-linecap="round"
          />

          <!-- Level indicator -->
          <text
            y="-8"
            text-anchor="middle"
            :fill="levelColors[node.level]"
            font-size="10"
            font-weight="bold"
          >
            L{{ node.level }}
          </text>

          <!-- Mastery indicator -->
          <text
            y="8"
            text-anchor="middle"
            :fill="stateColors[node.state]"
            font-size="14"
            font-weight="bold"
          >
            {{ node.mastery }}/4
          </text>

          <!-- Node name (below) -->
          <text
            :y="getNodeRadius(node) + 16"
            text-anchor="middle"
            fill="#888"
            font-size="11"
            class="node-name"
          >
            {{ node.name.length > 18 ? node.name.substring(0, 16) + '...' : node.name }}
          </text>
        </g>
      </g>
    </svg>

    <!-- Selected Node Details -->
    <Transition name="slide">
      <div v-if="selectedNode" class="node-details oled-panel">
        <div class="details-header">
          <div class="flex items-center gap-3">
            <div
              class="level-badge"
              :style="{ borderColor: levelColors[selectedNode.level] }"
            >
              L{{ selectedNode.level }}
            </div>
            <div>
              <h3 class="text-lg font-bold">{{ selectedNode.name }}</h3>
              <div class="text-sm text-text-muted capitalize">{{ selectedNode.state }}</div>
            </div>
          </div>

          <button class="close-btn" @click="selectedNode = null">×</button>
        </div>

        <p class="text-text-secondary text-sm mt-3">
          {{ selectedNode.description }}
        </p>

        <!-- Mastery Progress -->
        <div class="mastery-progress mt-4">
          <div class="flex justify-between text-sm mb-1">
            <span class="text-text-muted">Mastery</span>
            <span :style="{ color: stateColors[selectedNode.state] }">
              {{ selectedNode.mastery }}/4 ({{ selectedNode.mastery_percent }}%)
            </span>
          </div>
          <div class="progress-bar">
            <div
              class="progress-fill"
              :style="{
                width: `${selectedNode.mastery_percent}%`,
                background: stateColors[selectedNode.state]
              }"
            />
          </div>

          <!-- Mastery Hint (60-140 char tip for next stage) -->
          <div v-if="selectedNode.mastery_hint" class="mastery-hint mt-2">
            <span class="hint-icon">💡</span>
            <span class="hint-text">{{ selectedNode.mastery_hint }}</span>
          </div>
        </div>

        <!-- Prerequisites -->
        <div v-if="selectedNode.prerequisites.length > 0" class="mt-4">
          <div class="text-sm text-text-muted mb-1">Prerequisites</div>
          <div class="flex flex-wrap gap-1">
            <span
              v-for="prereq in selectedNode.prerequisites"
              :key="prereq"
              class="prereq-tag"
            >
              {{ prereq }}
            </span>
          </div>
        </div>

        <!-- Unlocks -->
        <div v-if="selectedNode.unlocks.length > 0" class="mt-4">
          <div class="text-sm text-text-muted mb-1">Unlocks</div>
          <div class="flex flex-wrap gap-1">
            <span
              v-for="unlock in selectedNode.unlocks"
              :key="unlock"
              class="unlock-tag"
            >
              {{ unlock }}
            </span>
          </div>
        </div>

        <!-- Start Challenge Button -->
        <button
          v-if="selectedNode.state !== 'locked' && selectedNode.challenges.starter"
          class="oled-button-primary w-full mt-4"
          @click="$router.push(`/challenge/${selectedNode.challenges.starter}`)"
        >
          Start Challenge
        </button>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.skill-tree-container {
  @apply relative h-full min-h-[600px] bg-oled-black rounded-lg overflow-hidden;
}

.tree-header {
  @apply absolute top-0 left-0 right-0 z-10;
  @apply flex items-center justify-between p-4;
  @apply bg-gradient-to-b from-oled-black via-oled-black/90 to-transparent;
}

.tree-stats {
  @apply flex items-center gap-6;
}

.stat {
  @apply flex flex-col items-center;
}

.stat-value {
  @apply text-xl font-bold;
}

.stat-label {
  @apply text-xs text-text-muted;
}

.loading-state {
  @apply absolute inset-0 flex items-center justify-center;
}

.skill-tree-svg {
  @apply w-full h-full cursor-grab;
}

.skill-tree-svg:active {
  @apply cursor-grabbing;
}

.skill-node {
  @apply cursor-pointer;
}

.skill-node circle {
  @apply transition-all duration-150;
}

.skill-node:hover circle {
  /* Scale the circle, not the whole group (which has translate) */
  transform: scale(1.1);
  transform-origin: center;
}

.skill-node.selected circle {
  stroke-width: 5;
}

.skill-node.locked {
  @apply opacity-50;
}

.node-name {
  @apply pointer-events-none;
}

.node-details {
  @apply absolute bottom-4 right-4 w-80 z-20;
}

.details-header {
  @apply flex items-start justify-between;
}

.level-badge {
  @apply w-10 h-10 rounded-full flex items-center justify-center;
  @apply bg-oled-panel border-2 text-sm font-bold;
}

.close-btn {
  @apply w-8 h-8 rounded-full flex items-center justify-center;
  @apply bg-oled-muted hover:bg-oled-border text-text-muted hover:text-white;
  @apply text-xl leading-none;
}

.mastery-progress .progress-bar {
  @apply h-2 rounded-full bg-oled-panel overflow-hidden;
}

.mastery-progress .progress-fill {
  @apply h-full rounded-full transition-all duration-500;
}

.prereq-tag {
  @apply px-2 py-0.5 rounded text-xs;
  @apply bg-oled-muted text-text-secondary;
}

.unlock-tag {
  @apply px-2 py-0.5 rounded text-xs;
  @apply bg-accent-primary/20 text-accent-primary;
}

.mastery-hint {
  @apply flex items-start gap-2 p-2 rounded-md;
  @apply bg-accent-warning/10 border border-accent-warning/20;
  font-size: 0.75rem;
  line-height: 1.4;
}

.mastery-hint .hint-icon {
  @apply flex-shrink-0;
}

.mastery-hint .hint-text {
  @apply text-text-secondary;
}

/* Transitions */
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
