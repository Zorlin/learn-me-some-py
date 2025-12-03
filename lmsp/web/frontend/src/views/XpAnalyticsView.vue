<script setup lang="ts">
/**
 * XP Analytics View
 * =================
 *
 * Time-series sparkline graph of XP gains with solve time overlay.
 * Fully vector SVG rendering. Supports zoom levels and drag to pan.
 */

import { ref, onMounted, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { usePlayerStore } from '@/stores/player'
import { useGamepadNav } from '@/composables/useGamepadNav'

const router = useRouter()
const playerStore = usePlayerStore()

useGamepadNav({ onBack: () => router.push('/progress') })

// State
const isLoading = ref(true)
const selectedPeriod = ref<string>('hour')
const periods = [
  { value: 'hour', label: '1 Hour', ms: 60 * 60 * 1000 },
  { value: 'day', label: '24 Hours', ms: 24 * 60 * 60 * 1000 },
  { value: 'week', label: '7 Days', ms: 7 * 24 * 60 * 60 * 1000 },
  { value: 'month', label: '30 Days', ms: 30 * 24 * 60 * 60 * 1000 },
  { value: 'year', label: '1 Year', ms: 365 * 24 * 60 * 60 * 1000 },
]

interface XpEvent {
  xp_amount: number
  reason: string
  challenge_id: string | null
  solve_time: number | null
  timestamp: string
  cumulative_xp?: number
}

const allEvents = ref<XpEvent[]>([])
const totalXp = ref(0)
const totalEvents = ref(0)

// Get time window in ms for selected period
const selectedPeriodMs = computed(() => {
  const period = periods.find(p => p.value === selectedPeriod.value)
  return period?.ms || 24 * 60 * 60 * 1000
})

// Time bounds for ALL data (full range of all events)
const fullTimeRange = computed(() => {
  if (allEvents.value.length === 0) {
    const now = Date.now()
    return { min: now - selectedPeriodMs.value, max: now }
  }
  const timestamps = allEvents.value.map(e => new Date(e.timestamp).getTime())
  return {
    min: Math.min(...timestamps),
    max: Math.max(...timestamps),
  }
})

// Visible time window based on period selection (used for initial view)
const visibleTimeWindow = computed(() => {
  const now = Date.now()
  return {
    min: now - selectedPeriodMs.value,
    max: now,
  }
})

// SVG chart dimensions - use full width with minimal padding
const chartWidth = 1200
const chartHeight = 260
const padding = { top: 12, right: 40, bottom: 30, left: 40 }

// Pan/zoom state
const panOffset = ref(0)
const zoomLevel = ref(1)
const isDragging = ref(false)
const dragStartX = ref(0)
const dragStartOffset = ref(0)

// Legend toggle state
const showXp = ref(true)
const showSolveTime = ref(true)

// Chart data points - ALL events with real timestamps
const chartPoints = computed(() => {
  return allEvents.value.map((d) => ({
    time: new Date(d.timestamp).getTime(),
    xp: d.cumulative_xp || 0,
    xpDelta: d.xp_amount,
    solveTime: d.solve_time || 0,
    label: formatTimestamp(d.timestamp),
    timestamp: d.timestamp,
    challengeId: d.challenge_id,
    reason: d.reason,
  }))
})

// The viewable area width in pixels
const viewWidth = computed(() => chartWidth - padding.left - padding.right)

// Current viewport time range (what's visible in the chart)
const viewportTimeRange = computed(() => {
  const { min: fullMin, max: fullMax } = fullTimeRange.value
  const fullRange = fullMax - fullMin || 1

  // Calculate time per pixel at current zoom
  const msPerPixel = fullRange / (viewWidth.value * zoomLevel.value)

  // Viewport start/end based on pan offset
  const viewMin = fullMin + (panOffset.value * msPerPixel)
  const viewMax = viewMin + (viewWidth.value * msPerPixel)

  return { min: viewMin, max: viewMax }
})

// Scale functions - X axis maps timestamp to pixel position
const xScale = computed(() => {
  const { min: fullMin, max: fullMax } = fullTimeRange.value
  const fullRange = fullMax - fullMin || 1

  // Total width of all data at current zoom
  const totalWidth = viewWidth.value * zoomLevel.value

  return (timestamp: number) => {
    const normalized = (timestamp - fullMin) / fullRange
    const x = padding.left + (normalized * totalWidth) - panOffset.value
    return x
  }
})

const yScaleXp = computed(() => {
  const points = chartPoints.value
  const maxXp = Math.max(...points.map(p => p.xp), 1)
  const height = chartHeight - padding.top - padding.bottom
  return (val: number) => chartHeight - padding.bottom - (val / maxXp) * height
})

const yScaleSolveTime = computed(() => {
  const points = chartPoints.value
  const maxTime = Math.max(...points.map(p => p.solveTime), 1)
  const height = chartHeight - padding.top - padding.bottom
  return (val: number) => chartHeight - padding.bottom - (val / maxTime) * height
})

// Generate SVG path for XP line
const xpLinePath = computed(() => {
  const points = chartPoints.value
  if (points.length === 0) return ''

  return points.map((p, i) => {
    const x = xScale.value(p.time)
    const y = yScaleXp.value(p.xp)
    return `${i === 0 ? 'M' : 'L'} ${x} ${y}`
  }).join(' ')
})

// Generate SVG path for XP area fill
const xpAreaPath = computed(() => {
  const points = chartPoints.value
  if (points.length === 0) return ''

  const linePath = points.map((p, i) => {
    const x = xScale.value(p.time)
    const y = yScaleXp.value(p.xp)
    return `${i === 0 ? 'M' : 'L'} ${x} ${y}`
  }).join(' ')

  const lastPoint = points[points.length - 1]
  const firstPoint = points[0]
  const lastX = xScale.value(lastPoint.time)
  const firstX = xScale.value(firstPoint.time)
  const baseY = chartHeight - padding.bottom

  return `${linePath} L ${lastX} ${baseY} L ${firstX} ${baseY} Z`
})

// Generate SVG path for solve time line
const solveTimeLinePath = computed(() => {
  const points = chartPoints.value
  if (points.length === 0) return ''

  return points.map((p, i) => {
    const x = xScale.value(p.time)
    const y = yScaleSolveTime.value(p.solveTime)
    return `${i === 0 ? 'M' : 'L'} ${x} ${y}`
  }).join(' ')
})

// Data points for hover/interaction
const dataPointsForRender = computed(() => {
  return chartPoints.value.map((p) => ({
    cx: xScale.value(p.time),
    cyXp: yScaleXp.value(p.xp),
    cySolveTime: yScaleSolveTime.value(p.solveTime),
    ...p,
  }))
})

// Y-axis ticks for XP
const yAxisTicksXp = computed(() => {
  const points = chartPoints.value
  const maxXp = Math.max(...points.map(p => p.xp), 1)
  const ticks = []
  const step = Math.ceil(maxXp / 5)
  for (let i = 0; i <= maxXp; i += step) {
    ticks.push({
      value: i,
      y: yScaleXp.value(i),
    })
  }
  return ticks
})

// Y-axis ticks for solve time
const yAxisTicksSolveTime = computed(() => {
  const points = chartPoints.value
  const maxTime = Math.max(...points.map(p => p.solveTime), 1)
  const ticks = []
  const step = Math.ceil(maxTime / 5)
  for (let i = 0; i <= maxTime; i += step) {
    ticks.push({
      value: i,
      y: yScaleSolveTime.value(i),
    })
  }
  return ticks
})

// X-axis ticks with timestamps (based on visible viewport)
const xAxisTicks = computed(() => {
  const { min, max } = viewportTimeRange.value
  const range = max - min
  const ticks = []
  const numTicks = 6

  for (let i = 0; i <= numTicks; i++) {
    const time = min + (range * i / numTicks)
    ticks.push({
      time,
      x: xScale.value(time),
      label: formatTimeLabel(time),
    })
  }
  return ticks
})

// Format time label based on period
function formatTimeLabel(timestamp: number): string {
  const date = new Date(timestamp)
  const period = selectedPeriod.value

  if (period === 'hour') {
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  } else if (period === 'day') {
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
  } else if (period === 'week') {
    return date.toLocaleDateString('en-US', { weekday: 'short', hour: '2-digit' })
  } else if (period === 'month') {
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  } else {
    return date.toLocaleDateString('en-US', { month: 'short', year: '2-digit' })
  }
}

// Drag handlers for panning
function handleMouseDown(e: MouseEvent) {
  isDragging.value = true
  dragStartX.value = e.clientX
  dragStartOffset.value = panOffset.value
}

function handleMouseMove(e: MouseEvent) {
  if (!isDragging.value) return
  const dx = e.clientX - dragStartX.value
  panOffset.value = dragStartOffset.value - dx
}

function handleMouseUp() {
  isDragging.value = false
}

function handleWheel(e: WheelEvent) {
  e.preventDefault()
  const delta = e.deltaY > 0 ? 0.9 : 1.1
  // Allow zooming from 1x (show all) to 100x (very zoomed in)
  zoomLevel.value = Math.max(1, Math.min(100, zoomLevel.value * delta))
}

function resetView() {
  // Calculate zoom to show selected period window
  const { min: fullMin, max: fullMax } = fullTimeRange.value
  const fullRange = fullMax - fullMin || 1
  const periodMs = selectedPeriodMs.value

  // Zoom level = full range / period window
  // e.g., if full range is 7 days and period is 1 day, zoom = 7
  const newZoom = Math.max(1, fullRange / periodMs)
  zoomLevel.value = newZoom

  // Pan to show the most recent data (right side)
  // Total width at this zoom = viewWidth * zoomLevel
  // We want the rightmost portion to be visible
  const totalWidth = viewWidth.value * newZoom
  const visibleWidth = viewWidth.value
  panOffset.value = Math.max(0, totalWidth - visibleWidth)
}

// Fetch all XP events (raw, no aggregation)
async function fetchXpHistory() {
  isLoading.value = true
  try {
    // Always fetch raw events - no period param = no aggregation
    const response = await fetch('/api/xp/history')
    const data = await response.json()

    allEvents.value = data.data || []
    totalXp.value = data.total_xp
    totalEvents.value = data.total_events

    // Reset pan/zoom on data change
    resetView()
  } catch (error) {
    console.error('Failed to fetch XP history:', error)
  } finally {
    isLoading.value = false
  }
}

function formatTimestamp(ts: string): string {
  const date = new Date(ts)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// Reset view when period changes
watch(selectedPeriod, () => {
  resetView()
})

// Stats computed
const avgXpPerEvent = computed(() => {
  if (totalEvents.value === 0) return 0
  return Math.round(totalXp.value / totalEvents.value)
})

const recentEvents = computed(() => {
  return allEvents.value.slice(-10).reverse()
})

onMounted(async () => {
  await playerStore.loadProfile()
  await fetchXpHistory()
})
</script>

<template>
  <div class="max-w-6xl mx-auto px-4 py-8">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-3xl font-bold">
          <span class="text-accent-secondary">📈</span> XP Analytics
        </h1>
        <p class="text-text-secondary mt-1">
          {{ totalXp.toLocaleString() }} total XP from {{ totalEvents }} events
        </p>
      </div>
      <button
        class="oled-button gamepad-focusable"
        @click="router.push('/progress')"
      >
        ← Back to Progress
      </button>
    </div>

    <!-- Period Selector -->
    <div class="oled-panel mb-6">
      <div class="flex items-center gap-2 flex-wrap">
        <span class="text-text-secondary mr-2">View by:</span>
        <button
          v-for="period in periods"
          :key="period.value"
          class="period-button gamepad-focusable"
          :class="{ active: selectedPeriod === period.value }"
          @click="selectedPeriod = period.value"
        >
          {{ period.label }}
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="text-center py-12 text-text-muted">
      Loading XP history...
    </div>

    <template v-else>
      <!-- Stats Row -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div class="oled-panel text-center">
          <div class="text-3xl font-bold text-accent-secondary">
            {{ totalXp.toLocaleString() }}
          </div>
          <div class="text-sm text-text-secondary">Total XP</div>
        </div>
        <div class="oled-panel text-center">
          <div class="text-3xl font-bold text-accent-primary">
            {{ totalEvents }}
          </div>
          <div class="text-sm text-text-secondary">Events</div>
        </div>
        <div class="oled-panel text-center">
          <div class="text-3xl font-bold text-tier-gold">
            {{ avgXpPerEvent }}
          </div>
          <div class="text-sm text-text-secondary">Avg XP/Event</div>
        </div>
        <div class="oled-panel text-center">
          <div class="text-3xl font-bold">
            {{ playerStore.profile?.level || 1 }}
          </div>
          <div class="text-sm text-text-secondary">Level</div>
        </div>
      </div>

      <!-- SVG Chart -->
      <div class="oled-panel mb-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-bold">XP Over Time</h2>
          <button
            class="text-sm text-text-secondary hover:text-accent-primary transition-colors gamepad-focusable"
            @click="resetView"
          >
            Reset View
          </button>
        </div>

        <div
          class="chart-container"
          @mousedown="handleMouseDown"
          @mousemove="handleMouseMove"
          @mouseup="handleMouseUp"
          @mouseleave="handleMouseUp"
          @wheel="handleWheel"
        >
          <svg
            :viewBox="`0 0 ${chartWidth} ${chartHeight}`"
            class="w-full h-full"
            preserveAspectRatio="none"
          >
            <!-- Grid lines -->
            <g class="grid-lines">
              <line
                v-for="tick in yAxisTicksXp"
                :key="'grid-' + tick.value"
                :x1="padding.left"
                :x2="chartWidth - padding.right"
                :y1="tick.y"
                :y2="tick.y"
                stroke="rgba(255,255,255,0.05)"
                stroke-width="1"
              />
            </g>

            <!-- XP Area fill -->
            <path
              v-if="chartPoints.length > 0 && showXp"
              :d="xpAreaPath"
              fill="url(#xpGradient)"
              opacity="0.3"
            />

            <!-- XP Line -->
            <path
              v-if="chartPoints.length > 0 && showXp"
              :d="xpLinePath"
              fill="none"
              stroke="#00ff88"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            />

            <!-- Solve Time Line -->
            <path
              v-if="chartPoints.length > 0 && showSolveTime"
              :d="solveTimeLinePath"
              fill="none"
              stroke="#60a5fa"
              stroke-width="2"
              stroke-dasharray="5,5"
              stroke-linecap="round"
              stroke-linejoin="round"
              opacity="0.8"
            />

            <!-- Data points -->
            <g class="data-points">
              <template v-if="showXp">
                <circle
                  v-for="(point, i) in dataPointsForRender"
                  :key="'xp-' + i"
                  :cx="point.cx"
                  :cy="point.cyXp"
                  r="4"
                  fill="#00ff88"
                  class="data-point"
                >
                  <title>{{ point.label }}: {{ point.xp }} XP</title>
                </circle>
              </template>
              <template v-if="showSolveTime">
                <circle
                  v-for="(point, i) in dataPointsForRender"
                  :key="'time-' + i"
                  :cx="point.cx"
                  :cy="point.cySolveTime"
                  r="3"
                  fill="#60a5fa"
                  class="data-point"
                >
                  <title>{{ point.label }}: {{ point.solveTime.toFixed(1) }}s</title>
                </circle>
              </template>
            </g>

            <!-- Y-axis labels (XP - left) -->
            <g v-if="showXp" class="y-axis-xp">
              <text
                v-for="tick in yAxisTicksXp"
                :key="'yxp-' + tick.value"
                :x="padding.left - 10"
                :y="tick.y + 4"
                text-anchor="end"
                fill="#00ff88"
                font-size="12"
              >
                {{ tick.value }}
              </text>
            </g>

            <!-- Y-axis labels (Solve Time - right) -->
            <g v-if="showSolveTime" class="y-axis-time">
              <text
                v-for="tick in yAxisTicksSolveTime"
                :key="'ytime-' + tick.value"
                :x="chartWidth - padding.right + 10"
                :y="tick.y + 4"
                text-anchor="start"
                fill="#60a5fa"
                font-size="12"
              >
                {{ tick.value }}s
              </text>
            </g>

            <!-- X-axis labels (timestamps) -->
            <g class="x-axis">
              <line
                v-for="tick in xAxisTicks"
                :key="'xtick-' + tick.time"
                :x1="tick.x"
                :x2="tick.x"
                :y1="chartHeight - padding.bottom"
                :y2="chartHeight - padding.bottom + 5"
                stroke="rgba(255,255,255,0.3)"
                stroke-width="1"
              />
              <text
                v-for="tick in xAxisTicks"
                :key="'xlabel-' + tick.time"
                :x="tick.x"
                :y="chartHeight - padding.bottom + 20"
                text-anchor="middle"
                fill="rgba(255,255,255,0.6)"
                font-size="10"
              >
                {{ tick.label }}
              </text>
            </g>

            <!-- Axis labels -->
            <text
              v-if="showXp"
              :x="12"
              :y="chartHeight / 2"
              fill="#00ff88"
              font-size="11"
              text-anchor="middle"
              :transform="`rotate(-90, 12, ${chartHeight / 2})`"
            >
              XP
            </text>
            <text
              v-if="showSolveTime"
              :x="chartWidth - 12"
              :y="chartHeight / 2"
              fill="#60a5fa"
              font-size="11"
              text-anchor="middle"
              :transform="`rotate(90, ${chartWidth - 12}, ${chartHeight / 2})`"
            >
              Time (s)
            </text>

            <!-- Gradient definition -->
            <defs>
              <linearGradient id="xpGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#00ff88" stop-opacity="0.4" />
                <stop offset="100%" stop-color="#00ff88" stop-opacity="0" />
              </linearGradient>
            </defs>
          </svg>
        </div>

        <div class="flex items-center justify-center gap-4 mt-2 text-xs">
          <button
            class="legend-toggle"
            :class="{ active: showXp, inactive: !showXp }"
            @click="showXp = !showXp"
          >
            <span class="legend-dot bg-accent-primary" />
            <span>XP</span>
          </button>
          <button
            class="legend-toggle"
            :class="{ active: showSolveTime, inactive: !showSolveTime }"
            @click="showSolveTime = !showSolveTime"
          >
            <span class="legend-dot bg-blue-400" />
            <span>Solve Time</span>
          </button>
          <span class="text-text-muted opacity-60">Drag to pan • Scroll to zoom</span>
        </div>
      </div>

      <!-- Recent Events -->
      <div v-if="allEvents.length > 0" class="oled-panel">
        <h2 class="text-lg font-bold mb-4">Recent Events</h2>
        <div class="space-y-3">
          <div
            v-for="(event, idx) in recentEvents"
            :key="idx"
            class="flex items-center justify-between p-3 bg-oled-darker rounded-lg"
          >
            <div class="flex-1">
              <div class="font-medium">
                <span class="text-accent-secondary">+{{ event.xp_amount }} XP</span>
                <span v-if="event.challenge_id" class="text-text-muted ml-2">
                  {{ event.challenge_id }}
                </span>
              </div>
              <div class="text-sm text-text-secondary">{{ event.reason }}</div>
            </div>
            <div class="text-right text-sm">
              <div v-if="event.solve_time" class="text-blue-400">
                {{ event.solve_time.toFixed(1) }}s
              </div>
              <div class="text-text-muted">
                {{ formatTimestamp(event.timestamp) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div
        v-if="totalEvents === 0"
        class="oled-panel text-center py-12"
      >
        <div class="text-6xl mb-4">📊</div>
        <div class="text-xl font-bold mb-2">No XP data yet!</div>
        <div class="text-text-secondary mb-6">
          Complete challenges to start tracking your XP progress.
        </div>
        <button
          class="oled-button-primary gamepad-focusable"
          @click="router.push('/challenges')"
        >
          Start a Challenge
        </button>
      </div>
    </template>
  </div>
</template>

<style scoped>
.chart-container {
  height: 300px;
  position: relative;
  cursor: grab;
  user-select: none;
  margin: -0.5rem;
}

.chart-container:active {
  cursor: grabbing;
}

.period-button {
  @apply px-4 py-2 rounded-lg text-sm font-medium;
  @apply bg-oled-darker border border-oled-border;
  @apply transition-all duration-200;
}

.period-button:hover {
  @apply border-accent-primary/50;
}

.period-button.active {
  @apply bg-accent-primary/20 border-accent-primary text-accent-primary;
}

.oled-panel {
  @apply p-4 rounded-lg bg-oled-panel border border-oled-border;
}

.bg-oled-darker {
  background: rgba(0, 0, 0, 0.3);
}

.data-point {
  transition: r 0.15s ease;
}

.data-point:hover {
  r: 6;
}

svg text {
  font-family: ui-monospace, monospace;
}

.legend-toggle {
  @apply flex items-center gap-1.5 px-2 py-1 rounded;
  @apply transition-all duration-150 cursor-pointer;
  @apply border border-transparent;
}

.legend-toggle:hover {
  @apply bg-white/5;
}

.legend-toggle.active {
  @apply text-white;
}

.legend-toggle.inactive {
  @apply opacity-40;
}

.legend-toggle.inactive .legend-dot {
  @apply opacity-30;
}

.legend-dot {
  @apply w-2 h-2 rounded-full inline-block;
}
</style>
