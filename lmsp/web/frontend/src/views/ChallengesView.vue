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
const allChallenges = ref<ChallengeItem[]>([])  // Full list for stats
const isLoading = ref(true)
const selectedLevel = ref<number | null>(null)

onMounted(async () => {
  await loadAllChallenges()
})

async function loadAllChallenges() {
  isLoading.value = true
  const response = await challengesApi.list()  // Always load all
  if (response.ok) {
    allChallenges.value = response.data
  }
  isLoading.value = false
}

// Filter challenges for display based on selected level
const challenges = computed(() => {
  if (selectedLevel.value === null) {
    return allChallenges.value
  }
  return allChallenges.value.filter(c => c.level === selectedLevel.value)
})

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

// Level stats for the filter buttons (always computed from ALL challenges)
interface LevelStats {
  total: number
  completed: number
  mastered: number
  needsReview: number
  avgRetention: number
}

const levelStats = computed(() => {
  const stats: Record<number, LevelStats> = {}

  // Initialize all levels 0-6
  for (let i = 0; i <= 6; i++) {
    stats[i] = { total: 0, completed: 0, mastered: 0, needsReview: 0, avgRetention: 0 }
  }

  // Accumulate stats
  for (const c of allChallenges.value) {
    const s = stats[c.level]
    s.total++
    if (c.progress) {
      s.completed++
      s.avgRetention += c.progress.retention
      if (c.progress.mastered) s.mastered++
      if (c.progress.needs_review) s.needsReview++
    }
  }

  // Calculate averages
  for (const level in stats) {
    const s = stats[level]
    if (s.completed > 0) {
      s.avgRetention = s.avgRetention / s.completed
    }
  }

  return stats
})

// Get color for level based on mastery state
function getLevelColor(level: number): string {
  const s = levelStats.value[level]
  if (!s || s.total === 0) return 'var(--oled-border)'
  if (s.mastered === s.total) return 'var(--accent-tertiary)'  // All mastered - purple
  if (s.needsReview > 0) return 'var(--accent-warning)'        // Some need review - warning
  if (s.completed === s.total) return 'var(--accent-success)'  // All completed - green
  if (s.completed > 0) return 'var(--accent-primary)'          // Some progress - neon green
  return 'var(--oled-border)'                                   // No progress
}

function selectChallenge(id: string) {
  router.push(`/challenge/${id}`)
}

function filterByLevel(level: number | null) {
  selectedLevel.value = level
  // No need to reload - filtering is done locally via computed
}
</script>

<template>
  <div class="responsive-container-wide py-responsive">
    <h1 class="text-responsive-title mb-6 3xl:mb-8">
      <span class="text-accent-primary">📚</span> Challenges
    </h1>

    <!-- Level Filter with Radial Progress -->
    <div class="level-filter-row">
      <button
        class="level-filter-btn"
        :class="{ 'active': selectedLevel === null }"
        @click="filterByLevel(null)"
      >
        <span class="level-filter-label">All</span>
      </button>
      <button
        v-for="level in 7"
        :key="level - 1"
        class="level-filter-btn"
        :class="{
          'active': selectedLevel === level - 1,
          'has-progress': levelStats[level - 1]?.completed > 0
        }"
        @click="filterByLevel(level - 1)"
      >
        <RadialProgress
          v-if="levelStats[level - 1]?.total > 0"
          :percent="levelStats[level - 1]?.avgRetention || 0"
          :size="36"
          :stroke-width="3"
          :animate="false"
        >
          <span class="level-number">{{ level - 1 }}</span>
        </RadialProgress>
        <span v-else class="level-number-empty">{{ level - 1 }}</span>
        <span class="level-stats-hint" v-if="levelStats[level - 1]?.total > 0">
          {{ levelStats[level - 1].completed }}/{{ levelStats[level - 1].total }}
        </span>
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
/* Level filter row */
.level-filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

@media (min-width: 1920px) {
  .level-filter-row {
    gap: 1rem;
    margin-bottom: 2rem;
  }
}

.level-filter-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  padding: 0.5rem 0.75rem;
  min-width: 3.5rem;
  border-radius: 0.5rem;
  background: var(--oled-panel);
  border: 2px solid var(--oled-border);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.level-filter-btn:hover {
  border-color: var(--text-muted);
  background: var(--oled-muted);
}

.level-filter-btn.active {
  border-color: var(--accent-primary);
  background: rgba(0, 255, 136, 0.1);
}

.level-filter-btn.active .level-number,
.level-filter-btn.active .level-filter-label {
  color: var(--accent-primary);
}

.level-filter-label {
  font-size: 0.875rem;
  font-weight: 600;
}

.level-number {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--text-secondary);
}

.level-number-empty {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-muted);
  border: 2px dashed var(--oled-border);
  border-radius: 50%;
}

.level-stats-hint {
  font-size: 0.6rem;
  color: var(--text-muted);
  white-space: nowrap;
}

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
