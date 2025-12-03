<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { usePlayerStore } from '@/stores/player'
import SkillTree from '@/components/progress/SkillTree.vue'

const playerStore = usePlayerStore()
const activeTab = ref<'tree' | 'achievements'>('tree')

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
</script>

<template>
  <div class="max-w-6xl mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-6">
      <span class="text-accent-primary">📊</span> Your Progress
    </h1>

    <!-- Tab Navigation -->
    <div class="flex gap-2 mb-6">
      <button
        class="tab-btn gamepad-focusable"
        :class="{ active: activeTab === 'tree' }"
        @click="activeTab = 'tree'"
      >
        🌳 Skill Tree
      </button>
      <button
        class="tab-btn gamepad-focusable"
        :class="{ active: activeTab === 'achievements' }"
        @click="activeTab = 'achievements'"
      >
        🏆 Achievements
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="playerStore.isLoading" class="text-center py-12 text-text-muted">
      Loading progress...
    </div>

    <template v-else>
      <!-- Skill Tree Tab -->
      <div v-if="activeTab === 'tree'" class="space-y-6">
        <!-- Player Stats (compact) -->
        <div v-if="playerStore.profile" class="oled-panel">
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="text-center">
              <div class="text-2xl font-bold text-accent-primary">
                {{ playerStore.profile.level }}
              </div>
              <div class="text-xs text-text-secondary">Level</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-accent-secondary">
                {{ playerStore.profile.xp }}
              </div>
              <div class="text-xs text-text-secondary">XP</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-tier-gold">
                {{ playerStore.profile.achievements_unlocked }}
              </div>
              <div class="text-xs text-text-secondary">Achievements</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold">
                {{ Object.keys(playerStore.profile.mastery_levels).length }}
              </div>
              <div class="text-xs text-text-secondary">Concepts</div>
            </div>
          </div>
        </div>

        <!-- Skill Tree Visualization -->
        <div class="skill-tree-wrapper">
          <SkillTree />
        </div>
      </div>

      <!-- Achievements Tab -->
      <div v-if="activeTab === 'achievements'" class="space-y-6">
        <!-- Player Stats -->
        <div v-if="playerStore.profile" class="oled-panel-glow">
          <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div class="text-center">
              <div class="text-4xl font-bold text-accent-primary">
                {{ playerStore.profile.level }}
              </div>
              <div class="text-sm text-text-secondary">Level</div>
            </div>
            <div class="text-center">
              <div class="text-4xl font-bold text-accent-secondary">
                {{ playerStore.profile.xp }}
              </div>
              <div class="text-sm text-text-secondary">XP</div>
            </div>
            <div class="text-center">
              <div class="text-4xl font-bold text-tier-gold">
                {{ playerStore.profile.achievements_unlocked }}
              </div>
              <div class="text-sm text-text-secondary">Achievements</div>
            </div>
            <div class="text-center">
              <div class="text-4xl font-bold">
                {{ Object.keys(playerStore.profile.mastery_levels).length }}
              </div>
              <div class="text-sm text-text-secondary">Concepts</div>
            </div>
          </div>
        </div>

        <!-- Mastery Levels -->
        <div class="oled-panel">
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
      </div>
    </template>
  </div>
</template>

<style scoped>
.tab-btn {
  @apply px-4 py-2 rounded-lg font-medium transition-all duration-200;
  @apply bg-oled-panel border border-oled-border text-text-secondary;
}

.tab-btn:hover {
  @apply border-accent-primary/50 text-white;
}

.tab-btn.active {
  @apply bg-accent-primary/20 border-accent-primary text-accent-primary;
}

.skill-tree-wrapper {
  @apply h-[700px] rounded-lg overflow-hidden border border-oled-border;
}
</style>
