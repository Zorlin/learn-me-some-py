<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

const props = defineProps<{
  achievement: {
    name: string
    description: string
    tier?: string
    icon?: string
    xp_reward?: number
  }
}>()

const emit = defineEmits<{
  close: []
}>()

const showConfetti = ref(false)

const tierColors = {
  bronze: 'border-tier-bronze text-tier-bronze',
  silver: 'border-tier-silver text-tier-silver',
  gold: 'border-tier-gold text-tier-gold',
  platinum: 'border-tier-platinum text-tier-platinum',
  diamond: 'border-tier-diamond text-tier-diamond',
}

const tierClass = computed(() => {
  const tier = props.achievement.tier || 'gold'
  return tierColors[tier as keyof typeof tierColors] || tierColors.gold
})

onMounted(() => {
  // Trigger confetti after a short delay
  setTimeout(() => {
    showConfetti.value = true
  }, 200)
})

function close() {
  emit('close')
}
</script>

<template>
  <div
    class="achievement-popup p-4 min-w-[280px]"
    :class="tierClass"
    @click="close"
  >
    <!-- Confetti Effect -->
    <div v-if="showConfetti" class="absolute inset-0 pointer-events-none overflow-hidden">
      <div
        v-for="i in 20"
        :key="i"
        class="confetti-particle"
        :style="{
          left: `${Math.random() * 100}%`,
          backgroundColor: ['#ffd700', '#00ff88', '#0088ff', '#ff00ff'][Math.floor(Math.random() * 4)],
          animationDelay: `${Math.random() * 0.5}s`,
        }"
      />
    </div>

    <!-- Content -->
    <div class="relative flex items-start gap-3">
      <!-- Icon -->
      <div class="text-3xl animate-float">
        {{ achievement.icon || '🏆' }}
      </div>

      <!-- Text -->
      <div class="flex-1">
        <div class="text-xs text-text-secondary uppercase tracking-wide">
          Achievement Unlocked!
        </div>
        <div class="font-bold text-lg">
          {{ achievement.name }}
        </div>
        <div class="text-sm text-text-secondary">
          {{ achievement.description }}
        </div>
        <div v-if="achievement.xp_reward" class="text-xs text-accent-primary mt-1">
          +{{ achievement.xp_reward }} XP
        </div>
      </div>

      <!-- Close button -->
      <button
        class="text-text-muted hover:text-white transition-colors"
        @click.stop="close"
      >
        ✕
      </button>
    </div>
  </div>
</template>
