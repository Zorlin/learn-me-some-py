<script setup lang="ts">
import { onMounted, ref } from 'vue'
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

const recommendation = ref<{ concept: string; reason: string; challenge_id: string } | null>(null)

onMounted(async () => {
  await playerStore.loadProfile()

  // Get recommendation
  const response = await playerApi.getRecommendations()
  console.log('Recommendations response:', response)
  if (response.ok) {
    recommendation.value = response.data as { concept: string; reason: string; challenge_id: string }
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
          <div class="text-xl font-bold">{{ playerStore.profile.player_id }}</div>
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

    <!-- Recommendation -->
    <div v-if="recommendation" class="oled-panel-glow mb-8 w-full max-w-md">
      <div class="text-sm text-accent-secondary mb-2">Recommended for you</div>
      <div class="font-bold text-lg">{{ recommendation.concept }}</div>
      <div class="text-sm text-text-secondary">{{ recommendation.reason }}</div>
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
