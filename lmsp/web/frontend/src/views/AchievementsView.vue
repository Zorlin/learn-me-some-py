<script setup lang="ts">
/**
 * Achievements View
 * =================
 *
 * Full-page view of all achievements - unlocked, in progress, and locked.
 */

import { onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { usePlayerStore } from '@/stores/player'
import { useGamepadNav } from '@/composables/useGamepadNav'

const router = useRouter()
const playerStore = usePlayerStore()

useGamepadNav({ onBack: () => router.push('/progress') })

onMounted(async () => {
  await Promise.all([
    playerStore.loadProfile(),
    playerStore.loadAchievements(),
  ])
})

const tierColors: Record<string, string> = {
  bronze: 'border-tier-bronze bg-tier-bronze/10',
  silver: 'border-tier-silver bg-tier-silver/10',
  gold: 'border-tier-gold bg-tier-gold/10',
  platinum: 'border-tier-platinum bg-tier-platinum/10',
  diamond: 'border-tier-diamond bg-tier-diamond/10',
}

const tierTextColors: Record<string, string> = {
  bronze: 'text-tier-bronze',
  silver: 'text-tier-silver',
  gold: 'text-tier-gold',
  platinum: 'text-tier-platinum',
  diamond: 'text-tier-diamond',
}

// Group achievements by tier
const achievementsByTier = computed(() => {
  const tiers: Record<string, typeof playerStore.unlockedAchievements> = {
    diamond: [],
    platinum: [],
    gold: [],
    silver: [],
    bronze: [],
  }

  for (const achievement of playerStore.unlockedAchievements) {
    const tier = achievement.tier || 'bronze'
    if (tiers[tier]) {
      tiers[tier].push(achievement)
    }
  }

  return tiers
})

const totalUnlocked = computed(() => playerStore.unlockedAchievements.length)
const totalInProgress = computed(() => playerStore.inProgressAchievements.length)
</script>

<template>
  <div class="max-w-6xl mx-auto px-4 py-8">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-3xl font-bold">
          <span class="text-tier-gold">🏆</span> Achievements
        </h1>
        <p class="text-text-secondary mt-1">
          {{ totalUnlocked }} unlocked
          <span v-if="totalInProgress > 0" class="text-text-muted">
            · {{ totalInProgress }} in progress
          </span>
        </p>
      </div>
      <button
        class="oled-button gamepad-focusable"
        @click="router.push('/progress')"
      >
        ← Back to Progress
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="playerStore.isLoading" class="text-center py-12 text-text-muted">
      Loading achievements...
    </div>

    <template v-else>
      <!-- Unlocked Achievements by Tier -->
      <div v-if="totalUnlocked > 0" class="mb-8">
        <template v-for="(achievements, tier) in achievementsByTier" :key="tier">
          <div v-if="achievements.length > 0" class="mb-8">
            <h2 class="text-lg font-bold mb-4 flex items-center gap-2" :class="tierTextColors[tier]">
              <span v-if="tier === 'diamond'">💎</span>
              <span v-else-if="tier === 'platinum'">🥇</span>
              <span v-else-if="tier === 'gold'">🥈</span>
              <span v-else-if="tier === 'silver'">🥉</span>
              <span v-else>🎖️</span>
              {{ tier.charAt(0).toUpperCase() + tier.slice(1) }} Tier
              <span class="text-sm text-text-muted font-normal">({{ achievements.length }})</span>
            </h2>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div
                v-for="achievement in achievements"
                :key="achievement.id"
                class="achievement-card gamepad-focusable p-4 rounded-lg border-2"
                :class="tierColors[achievement.tier] || tierColors.bronze"
              >
                <div class="flex items-start gap-3">
                  <div class="text-4xl">{{ achievement.icon }}</div>
                  <div class="flex-1 min-w-0">
                    <div class="font-bold">{{ achievement.name }}</div>
                    <div class="text-sm text-text-secondary mt-1">
                      {{ achievement.description }}
                    </div>
                    <div class="flex items-center gap-2 mt-2">
                      <span class="text-xs px-2 py-0.5 rounded bg-accent-primary/20 text-accent-primary">
                        +{{ achievement.xp_reward }} XP
                      </span>
                      <span
                        class="text-xs px-2 py-0.5 rounded capitalize"
                        :class="tierColors[achievement.tier]"
                      >
                        {{ achievement.tier }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- In Progress -->
      <div v-if="playerStore.inProgressAchievements.length > 0" class="mb-8">
        <h2 class="text-lg font-bold mb-4 text-accent-warning flex items-center gap-2">
          ⏳ In Progress
          <span class="text-sm text-text-muted font-normal">({{ playerStore.inProgressAchievements.length }})</span>
        </h2>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div
            v-for="achievement in playerStore.inProgressAchievements"
            :key="achievement.id"
            class="achievement-card gamepad-focusable p-4 rounded-lg border border-oled-border bg-oled-panel"
          >
            <div class="flex items-start gap-3 mb-3">
              <div class="text-3xl opacity-50">{{ achievement.icon }}</div>
              <div class="flex-1 min-w-0">
                <div class="font-bold">{{ achievement.name }}</div>
                <div class="text-sm text-text-secondary">{{ achievement.description }}</div>
              </div>
              <div class="text-sm text-text-muted whitespace-nowrap">
                {{ achievement.progress }}/{{ achievement.required }}
              </div>
            </div>
            <div class="progress-bar">
              <div
                class="progress-fill"
                :style="{ width: `${((achievement.progress || 0) / (achievement.required || 1)) * 100}%` }"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div
        v-if="totalUnlocked === 0 && totalInProgress === 0"
        class="oled-panel text-center py-12"
      >
        <div class="text-6xl mb-4">🏆</div>
        <div class="text-xl font-bold mb-2">No achievements yet!</div>
        <div class="text-text-secondary mb-6">
          Complete challenges to unlock achievements and earn bonus XP.
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
.achievement-card {
  transition: all 0.2s ease;
}

.achievement-card:hover {
  transform: translateY(-2px);
}
</style>
