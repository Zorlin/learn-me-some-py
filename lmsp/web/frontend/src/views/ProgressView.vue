<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePlayerStore } from '@/stores/player'
import { useGamepadNav } from '@/composables/useGamepadNav'

const router = useRouter()
const playerStore = usePlayerStore()

// Enable gamepad navigation
useGamepadNav({ onBack: () => router.push('/') })

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

function openSkillTree() {
  router.push('/skill-tree')
}
</script>

<template>
  <div class="max-w-6xl mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-6">
      <span class="text-accent-primary">📊</span> Your Progress
    </h1>

    <!-- Loading State -->
    <div v-if="playerStore.isLoading" class="text-center py-12 text-text-muted">
      Loading progress...
    </div>

    <template v-else>
      <!-- Player Stats -->
      <div v-if="playerStore.profile" class="oled-panel-glow mb-6">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div class="text-center">
            <div class="text-4xl font-bold text-accent-primary">
              {{ playerStore.profile.level }}
            </div>
            <div class="text-sm text-text-secondary">Level</div>
          </div>
          <button
            class="text-center stat-link gamepad-focusable rounded-lg p-2 -m-2"
            @click="router.push('/xp-analytics')"
          >
            <div class="text-4xl font-bold text-accent-secondary">
              {{ playerStore.profile.xp }}
            </div>
            <div class="text-sm text-text-secondary">XP</div>
          </button>
          <button
            class="text-center stat-link gamepad-focusable rounded-lg p-2 -m-2"
            @click="router.push('/achievements')"
          >
            <div class="text-4xl font-bold text-tier-gold">
              {{ playerStore.profile.achievements_unlocked }}
            </div>
            <div class="text-sm text-text-secondary">Achievements</div>
          </button>
          <div class="text-center">
            <div class="text-4xl font-bold">
              {{ Object.keys(playerStore.profile.mastery_levels).length }}
            </div>
            <div class="text-sm text-text-secondary">Concepts</div>
          </div>
        </div>
      </div>

      <!-- Skill Tree Link -->
      <button
        class="skill-tree-link gamepad-focusable mb-6"
        @click="openSkillTree"
      >
        <div class="link-icon">🌳</div>
        <div class="link-content">
          <div class="link-title">Open Skill Tree</div>
          <div class="link-desc">Full-screen view with gamepad navigation</div>
        </div>
        <div class="link-arrow">→</div>
      </button>

      <!-- Mastery Levels -->
      <div class="oled-panel mb-6">
        <h2 class="text-xl font-bold mb-4">Mastery Progress</h2>

        <div v-if="playerStore.profile?.mastery_levels && Object.keys(playerStore.profile.mastery_levels).length > 0" class="space-y-3">
          <div
            v-for="(level, concept) in playerStore.profile.mastery_levels"
            :key="concept"
            class="flex items-center gap-4"
          >
            <div class="w-32 text-sm text-text-secondary truncate">{{ concept }}</div>
            <div class="flex-1 progress-bar">
              <div
                class="progress-fill"
                :style="{ width: `${(level / 4) * 100}%` }"
              />
            </div>
            <div class="w-8 text-sm text-right">{{ level }}/4</div>
          </div>
        </div>

        <div v-else class="text-text-muted text-center py-4">
          No progress yet. Start a challenge!
        </div>
      </div>

      <!-- Achievements -->
      <div class="oled-panel">
        <h2 class="text-xl font-bold mb-4">Achievements</h2>

        <!-- Unlocked -->
        <div v-if="playerStore.unlockedAchievements.length > 0" class="mb-6">
          <h3 class="text-sm text-text-secondary mb-3">Unlocked</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div
              v-for="achievement in playerStore.unlockedAchievements"
              :key="achievement.id"
              class="p-4 rounded-lg border-2"
              :class="tierColors[achievement.tier] || tierColors.bronze"
            >
              <div class="flex items-center gap-3">
                <div class="text-3xl">{{ achievement.icon }}</div>
                <div>
                  <div class="font-bold">{{ achievement.name }}</div>
                  <div class="text-sm text-text-secondary">{{ achievement.description }}</div>
                  <div class="text-xs text-accent-primary mt-1">+{{ achievement.xp_reward }} XP</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- In Progress -->
        <div v-if="playerStore.inProgressAchievements.length > 0">
          <h3 class="text-sm text-text-secondary mb-3">In Progress</h3>
          <div class="space-y-4">
            <div
              v-for="achievement in playerStore.inProgressAchievements"
              :key="achievement.id"
              class="p-4 rounded-lg border border-oled-border"
            >
              <div class="flex items-center gap-3 mb-2">
                <div class="text-2xl opacity-50">{{ achievement.icon }}</div>
                <div class="flex-1">
                  <div class="font-bold">{{ achievement.name }}</div>
                  <div class="text-sm text-text-secondary">{{ achievement.description }}</div>
                </div>
                <div class="text-sm text-text-muted">
                  {{ achievement.progress }}/{{ achievement.required }}
                </div>
              </div>
              <div class="progress-bar">
                <div
                  class="progress-fill opacity-50"
                  :style="{ width: `${((achievement.progress || 0) / (achievement.required || 1)) * 100}%` }"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div
          v-if="playerStore.unlockedAchievements.length === 0 && playerStore.inProgressAchievements.length === 0"
          class="text-text-muted text-center py-8"
        >
          Complete challenges to unlock achievements!
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.skill-tree-link {
  @apply w-full p-6 rounded-lg;
  @apply flex items-center gap-4;
  @apply bg-oled-panel border-2 border-accent-primary/30;
  @apply hover:border-accent-primary hover:bg-accent-primary/5;
  @apply transition-all duration-200;
}

.skill-tree-link:hover {
  box-shadow: 0 0 30px rgba(0, 255, 136, 0.2);
}

.link-icon {
  @apply text-4xl;
}

.link-content {
  @apply flex-1 text-left;
}

.link-title {
  @apply text-xl font-bold text-accent-primary;
}

.link-desc {
  @apply text-sm text-text-secondary;
}

.link-arrow {
  @apply text-2xl text-accent-primary;
}

.stat-link {
  @apply transition-all duration-200 cursor-pointer;
  background: transparent;
  border: none;
}

.stat-link:hover {
  transform: scale(1.05);
}

.stat-link:nth-of-type(1):hover {
  @apply bg-accent-secondary/10;
}

.stat-link:nth-of-type(2):hover {
  @apply bg-tier-gold/10;
}
</style>
