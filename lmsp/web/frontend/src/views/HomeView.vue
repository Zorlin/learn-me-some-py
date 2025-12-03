<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { usePlayerStore } from '@/stores/player'
import { useGamepadStore } from '@/stores/gamepad'
import { useGamepadNav } from '@/composables/useGamepadNav'
import { playerApi } from '@/api/client'

const router = useRouter()
const playerStore = usePlayerStore()
const gamepadStore = useGamepadStore()

// Enable gamepad navigation
useGamepadNav({ onBack: () => {} }) // No back action on home

interface FlowState {
  momentum: number
  velocity: number
  frustration: number
  difficulty_target: string
}

interface Alternative {
  id: string
  concept: string
  score: number
}

interface Recommendation {
  concept: string
  reason: string
  challenge_id: string
  confidence: number
  flow?: FlowState
  alternatives?: Alternative[]
}

const recommendation = ref<Recommendation | null>(null)

// Flow state indicators
const flowEmoji = computed(() => {
  if (!recommendation.value?.flow) return '✨'
  const { momentum, velocity, frustration } = recommendation.value.flow
  if (frustration > 0.5) return '🌊' // Ease off
  if (momentum > 0.7 && velocity > 0.1) return '🔥' // On fire
  if (momentum > 0.5) return '⚡' // Good momentum
  if (velocity > 0) return '📈' // Improving
  return '✨' // Neutral
})

const flowLabel = computed(() => {
  if (!recommendation.value?.flow) return ''
  const { difficulty_target } = recommendation.value.flow
  switch (difficulty_target) {
    case 'slightly_harder': return 'Challenge Mode'
    case 'easier': return 'Building Momentum'
    case 'easy_win': return 'Confidence Boost'
    default: return 'Flow Zone'
  }
})

const confidencePercent = computed(() => {
  if (!recommendation.value) return 0
  return Math.round(recommendation.value.confidence * 100)
})

onMounted(async () => {
  await playerStore.loadProfile()

  // Get recommendation
  const response = await playerApi.getRecommendations()
  console.log('Recommendations response:', response)
  if (response.ok) {
    recommendation.value = response.data as Recommendation
    console.log('Recommendation set:', recommendation.value)
  }
})

function startRecommended() {
  console.log('startRecommended called, recommendation:', recommendation.value)
  if (recommendation.value?.challenge_id) {
    console.log('Navigating to challenge:', recommendation.value.challenge_id)
    router.push(`/challenge/${recommendation.value.challenge_id}`)
  } else {
    console.log('No challenge_id, going to challenges list')
    router.push('/challenges')
  }
}

function browseChallenges() {
  router.push('/challenges')
}

function viewProgress() {
  router.push('/progress')
}
</script>

<template>
  <div class="min-h-screen flex flex-col items-center justify-center p-8">
    <!-- Hero Section -->
    <div class="text-center mb-12 animate-float">
      <h1 class="text-5xl md:text-7xl font-bold mb-4">
        <span class="text-accent-primary">LMSP</span>
      </h1>
      <p class="text-xl text-text-secondary mb-2">
        Learn Me Some Py
      </p>
      <p class="text-lg text-text-muted">
        The game that teaches you to build it
      </p>
    </div>

    <!-- Player Stats -->
    <div v-if="playerStore.profile" class="oled-panel mb-8 w-full max-w-md">
      <div class="flex items-center justify-between">
        <div>
          <div class="text-sm text-text-secondary">Welcome back,</div>
          <div class="text-xl font-bold">{{ playerStore.displayName }}</div>
        </div>
        <div class="text-right">
          <div class="text-sm text-text-secondary">Level</div>
          <div class="text-3xl font-bold text-accent-primary">{{ playerStore.profile.level }}</div>
        </div>
      </div>

      <div class="mt-4 progress-bar">
        <div
          class="progress-fill"
          :style="{ width: `${(playerStore.profile.xp % 100)}%` }"
        />
      </div>
      <div class="text-xs text-text-muted mt-1">
        {{ playerStore.profile.xp }} XP
      </div>
    </div>

    <!-- Recommendation - Enhanced with Flow State -->
    <div
      v-if="recommendation"
      class="recommendation-card oled-panel-glow mb-8 w-full max-w-md cursor-pointer"
      @click="startRecommended"
    >
      <!-- Header with flow state indicator -->
      <div class="flex items-center justify-between mb-3">
        <div class="text-sm text-accent-secondary">Recommended for you</div>
        <div v-if="flowLabel" class="flex items-center gap-1 text-xs">
          <span>{{ flowEmoji }}</span>
          <span class="text-text-muted">{{ flowLabel }}</span>
        </div>
      </div>

      <!-- Main recommendation -->
      <div class="font-bold text-lg mb-1">{{ recommendation.concept }}</div>
      <div class="text-sm text-text-secondary mb-3">{{ recommendation.reason }}</div>

      <!-- Confidence bar -->
      <div class="flex items-center gap-2 text-xs text-text-muted">
        <span>Match</span>
        <div class="flex-1 h-1 bg-oled-near rounded-full overflow-hidden">
          <div
            class="h-full bg-accent-primary transition-all duration-500"
            :style="{ width: `${confidencePercent}%` }"
          />
        </div>
        <span>{{ confidencePercent }}%</span>
      </div>

      <!-- Alternatives -->
      <div v-if="recommendation.alternatives?.length" class="mt-3 pt-3 border-t border-oled-border">
        <div class="text-xs text-text-muted mb-2">Also consider:</div>
        <div class="flex flex-wrap gap-2" @click.stop>
          <button
            v-for="alt in recommendation.alternatives"
            :key="alt.id"
            class="alt-chip"
            @click="router.push(`/challenge/${alt.id}`)"
          >
            {{ alt.concept }}
          </button>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="flex flex-col sm:flex-row gap-4 w-full max-w-md">
      <button
        class="oled-button-primary gamepad-focusable flex-1 py-4 text-lg"
        @click="startRecommended"
      >
        🚀 Start Learning
      </button>
      <button
        class="oled-button-secondary gamepad-focusable flex-1 py-4 text-lg"
        @click="browseChallenges"
      >
        📚 Browse Challenges
      </button>
    </div>

    <button
      class="oled-button gamepad-focusable mt-4 w-full max-w-md py-3"
      @click="viewProgress"
    >
      📊 View Progress
    </button>

    <!-- Gamepad Hint -->
    <div v-if="gamepadStore.connected" class="mt-8 text-center text-sm text-accent-primary">
      🎮 Gamepad detected! Use triggers for emotional feedback.
    </div>
    <div v-else class="mt-8 text-center text-sm text-text-muted">
      Connect a gamepad for the full experience
    </div>
  </div>
</template>

<style scoped>
.recommendation-card {
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.recommendation-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 20px rgba(99, 102, 241, 0.15);
}

.recommendation-card:active {
  transform: translateY(0);
}

.alt-chip {
  @apply text-xs px-3 py-1.5 rounded-full;
  @apply bg-oled-near;
  @apply border border-transparent;
  @apply transition-all duration-150;
}

.alt-chip:hover {
  @apply border-text-muted/30;
  @apply bg-oled-panel;
}

.alt-chip:active {
  @apply border-accent-primary/50;
}
</style>
