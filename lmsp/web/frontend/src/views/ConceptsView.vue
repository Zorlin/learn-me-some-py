<script setup lang="ts">
/**
 * Concepts View - Duolingo-style Micro-lessons
 * =============================================
 *
 * Browse all concepts with dual filtering:
 * - By LEVEL (like Challenges page)
 * - By CATEGORY (dictionaries, loops, etc.)
 *
 * Beginners see Level 0-1, not Level 6 metaclasses.
 */

import { onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { conceptsApi, type ConceptSummary } from '@/api/client'
import { useGamepadNav } from '@/composables/useGamepadNav'
import RadialProgress from '@/components/ui/RadialProgress.vue'

interface ConceptWithCategory extends ConceptSummary {
  category: string
}

const router = useRouter()
const conceptsByCategory = ref<Record<string, ConceptSummary[]>>({})
const isLoading = ref(true)
const selectedLevel = ref<number | null>(null)
const selectedCategory = ref<string | null>(null)

useGamepadNav({ onBack: () => router.push('/') })

onMounted(async () => {
  await loadConcepts()
})

async function loadConcepts() {
  isLoading.value = true
  const response = await conceptsApi.list()
  if (response.ok) {
    conceptsByCategory.value = (response.data as any).categories || response.data
  }
  isLoading.value = false
}

// Flatten all concepts with their category attached
const allConcepts = computed(() => {
  const result: ConceptWithCategory[] = []
  for (const [category, concepts] of Object.entries(conceptsByCategory.value)) {
    for (const concept of concepts) {
      result.push({ ...concept, category })
    }
  }
  return result
})

// Get unique categories
const categories = computed(() => {
  const cats = new Set<string>()
  for (const concept of allConcepts.value) {
    cats.add(concept.category)
  }
  return Array.from(cats).sort()
})

// Get unique levels
const levels = computed(() => {
  const lvls = new Set<number>()
  for (const concept of allConcepts.value) {
    lvls.add(concept.level)
  }
  return Array.from(lvls).sort((a, b) => a - b)
})

// Categories that exist at the selected level (for filtering category buttons)
const categoriesAtSelectedLevel = computed(() => {
  if (selectedLevel.value === null) return new Set(categories.value)
  const cats = new Set<string>()
  for (const concept of allConcepts.value) {
    if (concept.level === selectedLevel.value) {
      cats.add(concept.category)
    }
  }
  return cats
})

// Levels that have the selected category (for greying out level buttons)
const levelsWithSelectedCategory = computed(() => {
  if (selectedCategory.value === null) return new Set(levels.value)
  const lvls = new Set<number>()
  for (const concept of allConcepts.value) {
    if (concept.category === selectedCategory.value) {
      lvls.add(concept.level)
    }
  }
  return lvls
})

// Filtered categories to display (only show relevant ones when level is selected)
const displayedCategories = computed(() => {
  if (selectedLevel.value === null) return categories.value
  return categories.value.filter(cat => categoriesAtSelectedLevel.value.has(cat))
})

// Stats per level (with retention tracking like Challenges)
const levelStats = computed(() => {
  const stats: Record<number, { total: number; completed: number; avgRetention: number }> = {}
  for (let i = 0; i <= 6; i++) {
    stats[i] = { total: 0, completed: 0, avgRetention: 0 }
  }
  for (const concept of allConcepts.value) {
    stats[concept.level].total++
    if (concept.progress) {
      stats[concept.level].completed++
      stats[concept.level].avgRetention += concept.progress.retention
    }
  }
  // Calculate averages
  for (let i = 0; i <= 6; i++) {
    if (stats[i].completed > 0) {
      stats[i].avgRetention = Math.round(stats[i].avgRetention / stats[i].completed)
    }
  }
  return stats
})

// Stats per category
const categoryStats = computed(() => {
  const stats: Record<string, number> = {}
  for (const concept of allConcepts.value) {
    stats[concept.category] = (stats[concept.category] || 0) + 1
  }
  return stats
})

// Apply both level and category filters
const filteredConcepts = computed(() => {
  return allConcepts.value.filter(c => {
    if (selectedLevel.value !== null && c.level !== selectedLevel.value) return false
    if (selectedCategory.value !== null && c.category !== selectedCategory.value) return false
    return true
  })
})

// Group filtered concepts by level, then category
const groupedConcepts = computed(() => {
  const groups: Record<number, Record<string, ConceptWithCategory[]>> = {}

  for (const concept of filteredConcepts.value) {
    if (!groups[concept.level]) groups[concept.level] = {}
    if (!groups[concept.level][concept.category]) groups[concept.level][concept.category] = []
    groups[concept.level][concept.category].push(concept)
  }

  return groups
})

const displayedLevels = computed(() =>
  Object.keys(groupedConcepts.value).map(Number).sort((a, b) => a - b)
)

function selectConcept(id: string) {
  router.push(`/concept/${id}`)
}

function filterByLevel(level: number | null) {
  // If clicking a level that doesn't have our selected category, reset category
  if (level !== null && selectedCategory.value !== null) {
    if (!levelsWithSelectedCategory.value.has(level)) {
      selectedCategory.value = null
    }
  }
  selectedLevel.value = level
}

function filterByCategory(category: string | null) {
  selectedCategory.value = category
}

// Check if a level has concepts in the currently selected category
function levelHasSelectedCategory(level: number): boolean {
  if (selectedCategory.value === null) return true
  return levelsWithSelectedCategory.value.has(level)
}

function formatCategory(category: string): string {
  return category
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

function getCategoryIcon(category: string): string {
  const icons: Record<string, string> = {
    variables: '📦',
    strings: '📝',
    numbers: '🔢',
    booleans: '✓',
    lists: '📋',
    dictionaries: '🗂️',
    loops: '🔁',
    conditionals: '🔀',
    functions: '⚡',
    classes: '🏗️',
    files: '📁',
    errors: '⚠️',
    modules: '📚',
    meta_programming: '🔮',
    async_programming: '⏳',
    data_structures: '🏗️',
    testing: '🧪',
  }
  return icons[category] || '📖'
}

function getLevelName(level: number): string {
  const names: Record<number, string> = {
    0: 'First Steps',
    1: 'Basics',
    2: 'Growing',
    3: 'Intermediate',
    4: 'Advanced',
    5: 'Expert',
    6: 'Master',
  }
  return names[level] || `Level ${level}`
}
</script>

<template>
  <div class="responsive-container-wide py-responsive">
    <h1 class="text-responsive-title mb-6 3xl:mb-8">
      <span class="text-accent-secondary">📖</span> Concepts
    </h1>

    <p class="text-text-secondary mb-6 text-lg max-w-2xl">
      Bite-sized lessons that teach ONE concept with no pressure.
      Filter by level or category to find what you need.
    </p>

    <!-- Level Filter (matching Challenges page style) -->
    <div class="level-filter-row">
      <button
        class="level-filter-btn gamepad-focusable"
        :class="{ 'active': selectedLevel === null }"
        @click="filterByLevel(null)"
      >
        <span class="level-filter-label">All</span>
      </button>
      <button
        v-for="level in 7"
        :key="level - 1"
        class="level-filter-btn gamepad-focusable"
        :class="{
          'active': selectedLevel === level - 1,
          'has-progress': levelStats[level - 1]?.total > 0,
          'dimmed': !levelHasSelectedCategory(level - 1)
        }"
        @click="filterByLevel(level - 1)"
      >
        <div class="level-btn-content">
          <span class="level-label">Level {{ level - 1 }}</span>
          <div class="level-progress-container" v-if="levelStats[level - 1]?.total > 0">
            <RadialProgress
              :percent="levelStats[level - 1]?.avgRetention || 0"
              :size="40"
              :stroke-width="4"
              :show-label="true"
            />
            <span class="level-stats-text">
              {{ levelStats[level - 1].completed }}/{{ levelStats[level - 1].total }}
            </span>
          </div>
          <div v-else class="level-empty-progress">
            <span class="level-empty-circle">○</span>
            <span class="level-stats-text">0/0</span>
          </div>
        </div>
      </button>
    </div>

    <!-- Category Filter -->
    <div class="category-filter-row">
      <button
        class="category-filter-btn gamepad-focusable"
        :class="{ 'active': selectedCategory === null }"
        @click="filterByCategory(null)"
      >
        <span class="category-icon">🌐</span>
        <span class="category-label">All Topics</span>
        <span v-if="selectedLevel !== null" class="category-count">{{ displayedCategories.length }}</span>
      </button>
      <button
        v-for="category in displayedCategories"
        :key="category"
        class="category-filter-btn gamepad-focusable"
        :class="{ 'active': selectedCategory === category }"
        @click="filterByCategory(category)"
      >
        <span class="category-icon">{{ getCategoryIcon(category) }}</span>
        <span class="category-label">{{ formatCategory(category) }}</span>
        <span class="category-count">{{ categoryStats[category] || 0 }}</span>
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="text-center py-12 text-text-muted">
      Loading concepts...
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredConcepts.length === 0" class="text-center py-12">
      <div class="text-4xl mb-4">📚</div>
      <div class="text-text-secondary">No concepts match your filters</div>
      <button
        class="mt-4 px-4 py-2 text-accent-primary border border-accent-primary rounded-lg gamepad-focusable"
        @click="selectedLevel = null; selectedCategory = null"
      >
        Clear Filters
      </button>
    </div>

    <!-- Concept List by Level, then Category -->
    <div v-else>
      <div
        v-for="level in displayedLevels"
        :key="level"
        class="level-section mb-10"
      >
        <!-- Level Header -->
        <div class="level-header mb-6">
          <h2 class="text-responsive-heading flex items-center gap-3">
            <span class="text-accent-primary">Level {{ level }}</span>
            <span class="text-text-secondary">{{ getLevelName(level) }}</span>
          </h2>
        </div>

        <!-- Categories within this level - multi-column layout -->
        <div class="categories-grid">
          <div
            v-for="(concepts, category) in groupedConcepts[level]"
            :key="category"
            class="category-section"
          >
            <h3 class="category-header mb-3 flex items-center gap-2">
              <span class="text-xl">{{ getCategoryIcon(category as string) }}</span>
              <span class="text-accent-secondary">{{ formatCategory(category as string) }}</span>
              <span class="text-text-muted text-sm">({{ concepts.length }})</span>
            </h3>

            <div class="category-concepts-grid">
              <div
                v-for="concept in concepts"
                :key="concept.id"
                class="concept-card cursor-pointer gamepad-focusable"
                :class="{ 'bonus': concept.bonus }"
                @click="selectConcept(concept.id)"
              >
                <div class="flex items-start justify-between">
                  <div class="flex-1">
                    <div class="flex items-center gap-2 mb-2">
                      <div v-if="concept.bonus" class="bonus-badge">Extra Credit</div>
                    </div>
                    <h3 class="font-bold text-lg mb-1">{{ concept.name }}</h3>
                    <div class="time-estimate">
                      <span class="time-icon">⏱️</span>
                      <span class="time-text">{{ concept.time_to_read }}s read</span>
                    </div>
                  </div>

                  <!-- Radial Progress Dial (same as Challenges) -->
                  <div class="progress-container">
                    <RadialProgress
                      v-if="concept.progress"
                      :percent="concept.progress.retention"
                      :size="48"
                      :stroke-width="4"
                      :show-label="true"
                    />
                    <div v-else class="empty-progress">
                      <span class="empty-icon">○</span>
                    </div>
                    <div
                      v-if="concept.progress"
                      class="progress-label"
                      :class="{
                        'needs-review': concept.progress.needs_review,
                        'mastered': concept.progress.mastered
                      }"
                    >
                      {{ concept.progress.mastered ? 'Mastered!' : concept.progress.needs_review ? 'Review!' : concept.progress.days_since < 1 ? 'Fresh!' : `${Math.round(concept.progress.days_since)}d ago` }}
                    </div>
                  </div>
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
/* Level filter row - matches ChallengesView */
.level-filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

@media (min-width: 1920px) {
  .level-filter-row {
    gap: 1rem;
  }
}

.level-filter-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  padding: 0.75rem 1rem;
  min-width: 5rem;
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

.level-filter-btn.active .level-label,
.level-filter-btn.active .level-filter-label {
  color: var(--accent-primary);
}

/* Dimmed state for levels without selected category */
.level-filter-btn.dimmed {
  opacity: 0.4;
  border-style: dashed;
}

.level-filter-btn.dimmed:hover {
  opacity: 0.7;
  border-color: var(--text-muted);
}

.level-filter-label {
  font-size: 0.875rem;
  font-weight: 600;
}

.level-btn-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.level-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary);
  white-space: nowrap;
}

.level-progress-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.level-stats-text {
  font-size: 0.6rem;
  color: var(--text-muted);
  white-space: nowrap;
}

.level-empty-progress {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.level-empty-circle {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: var(--text-muted);
  border: 2px dashed var(--oled-border);
  border-radius: 50%;
  opacity: 0.5;
}

/* Category filter row */
.category-filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--oled-border);
}

.category-filter-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.75rem;
  border-radius: 9999px;
  background: var(--oled-panel);
  border: 1px solid var(--oled-border);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.875rem;
}

.category-filter-btn:hover {
  border-color: var(--accent-secondary);
  background: var(--oled-muted);
}

.category-filter-btn.active {
  border-color: var(--accent-secondary);
  background: rgba(59, 130, 246, 0.15);
}

.category-filter-btn.active .category-label {
  color: var(--accent-secondary);
}

.category-icon {
  font-size: 1rem;
}

.category-label {
  font-weight: 500;
}

.category-count {
  font-size: 0.625rem;
  padding: 0.125rem 0.375rem;
  background: var(--oled-muted);
  border-radius: 9999px;
  color: var(--text-muted);
}

/* Level sections */
.level-section {
  border-bottom: 1px solid var(--oled-border);
  padding-bottom: 2rem;
}

.level-section:last-child {
  border-bottom: none;
}

.level-header {
  padding-left: 0.5rem;
  border-left: 4px solid var(--accent-primary);
}

/* Multi-column categories grid */
.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 2rem;
  align-items: start;
}

@media (min-width: 1920px) {
  .categories-grid {
    grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  }
}

/* Category sections within levels */
.category-section {
  /* No extra styling needed - just a container */
}

.category-header {
  font-size: 1rem;
  font-weight: 600;
}

/* Grid for concepts within a category */
.category-concepts-grid {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

/* Concept cards */
.concept-card {
  background: var(--oled-panel);
  border: 2px solid var(--oled-border);
  border-radius: 0.75rem;
  padding: 1.25rem;
  transition: all 0.2s ease;
}

.concept-card:hover {
  border-color: var(--accent-secondary);
  background: var(--oled-muted);
  transform: translateY(-2px);
}

.concept-card.bonus {
  border-color: var(--accent-tertiary);
  background: linear-gradient(135deg, var(--oled-panel), rgba(255, 0, 255, 0.05));
}

.concept-card.bonus:hover {
  border-color: var(--accent-tertiary);
  background: linear-gradient(135deg, var(--oled-muted), rgba(255, 0, 255, 0.1));
}

/* Bonus badge */
.bonus-badge {
  background: linear-gradient(135deg, var(--accent-tertiary), #ff66ff);
  color: #fff;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.625rem;
  font-weight: 700;
  text-transform: uppercase;
}

/* Time estimate */
.time-estimate {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  color: var(--text-muted);
  font-size: 0.875rem;
}

.time-icon {
  font-size: 0.875rem;
}

.time-text {
  font-family: monospace;
}

/* Progress container (same as Challenges) */
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
</style>
