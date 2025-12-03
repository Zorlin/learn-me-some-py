<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { challengesApi } from '@/api/client'
import RadialProgress from '@/components/ui/RadialProgress.vue'

interface ChallengeProgress {
  retention: number
  needs_review: boolean
  days_since: number
  performance_grade: string
  completion_count: number
  mastery_factor: number
  mastered: boolean
}

interface ChallengeItem {
  id: string
  name: string
  level: number
  points: number
  progress: ChallengeProgress | null
}

const router = useRouter()
const challenges = ref<ChallengeItem[]>([])
const isLoading = ref(true)
const selectedLevel = ref<number | null>(null)

onMounted(async () => {
  await loadChallenges()
})

async function loadChallenges() {
  isLoading.value = true
  const response = await challengesApi.list(selectedLevel.value ?? undefined)
  if (response.ok) {
    challenges.value = response.data
  }
  isLoading.value = false
}

const groupedByLevel = computed(() => {
  const groups: Record<number, ChallengeItem[]> = {}
  for (const c of challenges.value) {
    if (!groups[c.level]) {
      groups[c.level] = []
    }
    groups[c.level].push(c)
  }
  return groups
})

const levels = computed(() =>
  Object.keys(groupedByLevel.value).map(Number).sort()
)

function selectChallenge(id: string) {
  router.push(`/challenge/${id}`)
}

function filterByLevel(level: number | null) {
  selectedLevel.value = level
  loadChallenges()
}
</script>

<template>
  <div class="responsive-container-wide py-responsive">
    <h1 class="text-responsive-title mb-6 3xl:mb-8">
      <span class="text-accent-primary">📚</span> Challenges
    </h1>

    <!-- Level Filter -->
    <div class="flex flex-wrap gap-responsive mb-6 3xl:mb-8">
      <button
        class="oled-button"
        :class="{ 'border-accent-primary text-accent-primary': selectedLevel === null }"
        @click="filterByLevel(null)"
      >
        All Levels
      </button>
      <button
        v-for="level in 7"
        :key="level - 1"
        class="oled-button"
        :class="{ 'border-accent-primary text-accent-primary': selectedLevel === level - 1 }"
        @click="filterByLevel(level - 1)"
      >
        Level {{ level - 1 }}
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="text-center py-12 text-text-muted">
      Loading challenges...
    </div>

    <!-- Empty State -->
    <div v-else-if="challenges.length === 0" class="text-center py-12">
      <div class="text-4xl mb-4">🏗️</div>
      <div class="text-text-secondary">No challenges available yet</div>
    </div>

    <!-- Challenge List -->
    <div v-else>
      <div
        v-for="level in levels"
        :key="level"
        class="mb-8"
      >
        <h2 class="text-responsive-heading mb-4 text-accent-secondary">
          Level {{ level }}
        </h2>

        <div class="responsive-grid">
          <div
            v-for="challenge in groupedByLevel[level]"
            :key="challenge.id"
            class="challenge-card cursor-pointer"
            :class="{
              'needs-review': challenge.progress?.needs_review,
              'mastered': challenge.progress?.mastered,
              'completed': challenge.progress && !challenge.progress.needs_review && !challenge.progress.mastered,
            }"
            @click="selectChallenge(challenge.id)"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-2">
                  <div class="level-badge">Lv.{{ challenge.level }}</div>
                  <div
                    v-if="challenge.progress?.performance_grade && challenge.progress.performance_grade !== '-'"
                    class="grade-badge"
                    :class="`grade-${challenge.progress.performance_grade.toLowerCase()}`"
                  >
                    {{ challenge.progress.performance_grade }}
                  </div>
                </div>
                <h3 class="font-bold text-lg">{{ challenge.name }}</h3>
                <div class="text-accent-primary font-mono text-sm mt-1">
                  {{ challenge.points }} pts
                </div>
              </div>

              <!-- Radial Progress Dial -->
              <div class="progress-container">
                <RadialProgress
                  v-if="challenge.progress"
                  :percent="challenge.progress.retention"
                  :size="48"
                  :stroke-width="4"
                  :show-label="true"
                />
                <div v-else class="empty-progress">
                  <span class="empty-icon">○</span>
                </div>
                <div
                  v-if="challenge.progress"
                  class="progress-label"
                  :class="{
                    'needs-review': challenge.progress.needs_review,
                    'mastered': challenge.progress.mastered
                  }"
                >
                  {{ challenge.progress.mastered ? 'Mastered!' : challenge.progress.needs_review ? 'Review!' : challenge.progress.days_since < 1 ? 'Fresh!' : `${Math.round(challenge.progress.days_since)}d ago` }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Challenge card states */
.challenge-card.needs-review {
  border-color: var(--accent-warning);
  background: linear-gradient(135deg, var(--oled-panel), rgba(234, 179, 8, 0.05));
}

.challenge-card.completed {
  border-color: var(--accent-success);
  background: linear-gradient(135deg, var(--oled-panel), rgba(34, 197, 94, 0.03));
}

.challenge-card.mastered {
  border-color: var(--accent-tertiary);
  background: linear-gradient(135deg, var(--oled-panel), rgba(255, 0, 255, 0.05));
}

/* Progress container */
.progress-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  min-width: 56px;
}

.progress-label {
  font-size: 0.65rem;
  color: var(--text-muted);
  text-align: center;
  white-space: nowrap;
}

.progress-label.needs-review {
  color: var(--accent-warning);
  font-weight: 600;
  animation: pulse-review 2s ease-in-out infinite;
}

.progress-label.mastered {
  color: var(--accent-tertiary);
  font-weight: 600;
}

@keyframes pulse-review {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

/* Empty progress state */
.empty-progress {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px dashed var(--oled-border);
  border-radius: 50%;
  opacity: 0.3;
}

.empty-icon {
  font-size: 1.5rem;
  color: var(--text-muted);
}

/* Performance grade badges */
.grade-badge {
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-size: 0.625rem;
  font-weight: 700;
  text-transform: uppercase;
}

.grade-s {
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  color: #000;
  animation: shimmer 2s ease-in-out infinite;
}

.grade-a {
  background: var(--accent-success);
  color: #000;
}

.grade-b {
  background: var(--accent-primary);
  color: #fff;
}

.grade-c {
  background: var(--accent-warning);
  color: #000;
}

.grade-d {
  background: #f97316;
  color: #000;
}

.grade-f {
  background: var(--accent-error);
  color: #fff;
}

@keyframes shimmer {
  0%, 100% {
    filter: brightness(1) drop-shadow(0 0 2px #fbbf24);
  }
  50% {
    filter: brightness(1.2) drop-shadow(0 0 6px #fbbf24);
  }
}
</style>
