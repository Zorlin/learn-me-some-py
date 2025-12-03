<script setup lang="ts">
/**
 * Radial Progress Dial
 * ====================
 *
 * A satisfying circular progress indicator that shows
 * challenge completion/retention percentage.
 *
 * Features:
 * - Smooth SVG arc animation
 * - Subtle glow effect when high percentage
 * - Color gradient based on percentage
 * - Optional pulse animation for 100%
 */

import { computed } from 'vue'

const props = withDefaults(defineProps<{
  percent: number         // 0-100
  size?: number          // Diameter in pixels
  strokeWidth?: number   // Ring thickness
  showLabel?: boolean    // Show percentage text
  animate?: boolean      // Enable animations
}>(), {
  size: 40,
  strokeWidth: 4,
  showLabel: false,
  animate: true,
})

// SVG calculations
const radius = computed(() => (props.size - props.strokeWidth) / 2)
const circumference = computed(() => 2 * Math.PI * radius.value)
const strokeDashoffset = computed(() => {
  const percent = Math.max(0, Math.min(100, props.percent))
  return circumference.value * (1 - percent / 100)
})

// Color based on percentage (purple when mastered, then green -> yellow -> red as it decays)
const progressColor = computed(() => {
  const p = props.percent
  if (p >= 100) return 'var(--accent-tertiary)'    // Purple - mastered!
  if (p >= 80) return 'var(--accent-success)'      // Green - fresh
  if (p >= 60) return 'var(--accent-primary)'      // Neon green - good
  if (p >= 40) return 'var(--accent-warning)'      // Yellow - needs review
  if (p >= 20) return '#f97316'                     // Orange - stale
  return 'var(--accent-error)'                     // Red - forgotten
})
</script>

<template>
  <div
    class="radial-progress"
    :style="{
      width: `${size}px`,
      height: `${size}px`,
    }"
  >
    <svg
      :width="size"
      :height="size"
      :viewBox="`0 0 ${size} ${size}`"
      class="radial-svg"
    >
      <!-- Background ring -->
      <circle
        class="radial-bg"
        :cx="size / 2"
        :cy="size / 2"
        :r="radius"
        fill="none"
        :stroke-width="strokeWidth"
      />

      <!-- Progress ring -->
      <circle
        class="radial-progress-ring"
        :class="{ 'animate-ring': animate }"
        :cx="size / 2"
        :cy="size / 2"
        :r="radius"
        fill="none"
        :stroke="progressColor"
        :stroke-width="strokeWidth"
        :stroke-dasharray="circumference"
        :stroke-dashoffset="strokeDashoffset"
        stroke-linecap="round"
        :transform="`rotate(-90 ${size / 2} ${size / 2})`"
      />
    </svg>

    <!-- Center content -->
    <div class="radial-center">
      <slot>
        <span v-if="showLabel" class="radial-label">
          {{ Math.round(percent) }}
        </span>
      </slot>
    </div>
  </div>
</template>

<style scoped>
.radial-progress {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.radial-svg {
  position: absolute;
  top: 0;
  left: 0;
}

.radial-bg {
  stroke: var(--oled-muted, #333333);
  opacity: 0.5;
}

.radial-progress-ring {
  transition: stroke-dashoffset 0.6s ease-out, stroke 0.3s ease;
}

.radial-progress-ring.animate-ring {
  animation: radial-appear 0.8s ease-out;
}

@keyframes radial-appear {
  from {
    stroke-dashoffset: v-bind(circumference + 'px');
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.radial-center {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.radial-label {
  font-size: 0.6em;
  font-weight: 600;
  color: var(--text-secondary);
}

/* Subtle scale on hover */
.radial-progress {
  transition: transform 0.2s ease;
}

.radial-progress:hover {
  transform: scale(1.05);
}
</style>
