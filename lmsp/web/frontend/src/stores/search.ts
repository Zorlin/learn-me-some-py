/**
 * Universal Search Store
 * ======================
 *
 * FlexSearch-powered search across:
 * - Concepts (lessons)
 * - Challenges (all stages)
 * - Code examples
 *
 * Indexes on first use, then searches instantly.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import FlexSearch from 'flexsearch'
import { api } from '@/api/client'

export interface SearchResult {
  id: string
  type: 'concept' | 'challenge' | 'stage' | 'code'
  title: string
  subtitle: string
  level: number
  category?: string
  matchedIn: string  // Where the match was found
  snippet: string    // Preview of matched content
  route: string      // Where to navigate
  score?: number
}

interface IndexedItem {
  id: string
  type: 'concept' | 'challenge' | 'stage' | 'code'
  title: string
  subtitle: string
  level: number
  category?: string
  content: string
  route: string
}

export const useSearchStore = defineStore('search', () => {
  const isIndexing = ref(false)
  const isIndexed = ref(false)
  const isOpen = ref(false)
  const query = ref('')
  const results = ref<SearchResult[]>([])
  const indexedItems = ref<Map<string, IndexedItem>>(new Map())

  // FlexSearch index with fuzzy matching
  const index = new FlexSearch.Index({
    tokenize: 'forward',
    resolution: 9,
    cache: true,
  })

  async function buildIndex() {
    if (isIndexed.value || isIndexing.value) return

    isIndexing.value = true

    try {
      // Fetch all concepts
      const conceptsRes = await api.get<any>('/lessons')
      if (conceptsRes.ok) {
        const data = conceptsRes.data
        const categories = data.categories || data

        for (const [category, concepts] of Object.entries(categories)) {
          for (const concept of concepts as any[]) {
            // Fetch full concept content
            const fullRes = await api.get<any>(`/lessons/${concept.id}`)
            if (fullRes.ok) {
              const full = fullRes.data
              const item: IndexedItem = {
                id: `concept:${concept.id}`,
                type: 'concept',
                title: concept.name,
                subtitle: `Level ${concept.level} · ${formatCategory(category)}`,
                level: concept.level,
                category: category,
                content: `${concept.name} ${full.lesson || ''} ${full.try_it?.starter || ''} ${full.try_it?.solution || ''}`.toLowerCase(),
                route: `/concept/${concept.id}`,
              }
              indexedItems.value.set(item.id, item)
              index.add(item.id, item.content)
            }
          }
        }
      }

      // Fetch all challenges
      const challengesRes = await api.get<any[]>('/challenges')
      if (challengesRes.ok) {
        const challenges = challengesRes.data

        for (const challenge of challenges) {
          // Fetch full challenge content
          const fullRes = await api.get<any>(`/challenges/${challenge.id}`)
          if (fullRes.ok) {
            const full = fullRes.data

            // Index the main challenge
            const item: IndexedItem = {
              id: `challenge:${challenge.id}`,
              type: 'challenge',
              title: challenge.name,
              subtitle: `Level ${challenge.level} · ${full.points || 0} pts`,
              level: challenge.level,
              category: full.category,
              content: `${challenge.name} ${full.description || ''} ${full.skeleton || ''}`.toLowerCase(),
              route: `/challenge/${challenge.id}`,
            }
            indexedItems.value.set(item.id, item)
            index.add(item.id, item.content)

            // Index each stage separately
            if (full.stages) {
              for (const [stageId, stage] of Object.entries(full.stages as Record<string, any>)) {
                const stageItem: IndexedItem = {
                  id: `stage:${challenge.id}:${stageId}`,
                  type: 'stage',
                  title: `${challenge.name} → ${stage.name || stageId}`,
                  subtitle: `Stage · Level ${challenge.level}`,
                  level: challenge.level,
                  category: full.category,
                  content: `${stage.name || ''} ${stage.description || ''} ${stage.skeleton_code || ''}`.toLowerCase(),
                  route: `/challenge/${challenge.id}`,
                }
                indexedItems.value.set(stageItem.id, stageItem)
                index.add(stageItem.id, stageItem.content)
              }
            }

            // Index code examples (skeleton, solution)
            if (full.skeleton) {
              const codeItem: IndexedItem = {
                id: `code:${challenge.id}:skeleton`,
                type: 'code',
                title: `${challenge.name} (starter code)`,
                subtitle: `Code · Level ${challenge.level}`,
                level: challenge.level,
                category: full.category,
                content: full.skeleton.toLowerCase(),
                route: `/challenge/${challenge.id}`,
              }
              indexedItems.value.set(codeItem.id, codeItem)
              index.add(codeItem.id, codeItem.content)
            }

            if (full.solution) {
              const codeItem: IndexedItem = {
                id: `code:${challenge.id}:solution`,
                type: 'code',
                title: `${challenge.name} (solution)`,
                subtitle: `Code · Level ${challenge.level}`,
                level: challenge.level,
                category: full.category,
                content: full.solution.toLowerCase(),
                route: `/challenge/${challenge.id}`,
              }
              indexedItems.value.set(codeItem.id, codeItem)
              index.add(codeItem.id, codeItem.content)
            }
          }
        }
      }

      isIndexed.value = true
    } catch (err) {
      console.error('Failed to build search index:', err)
    } finally {
      isIndexing.value = false
    }
  }

  function search(q: string): SearchResult[] {
    if (!q.trim() || !isIndexed.value) return []

    const searchResults = index.search(q.toLowerCase(), { limit: 20 })
    const mapped: SearchResult[] = []

    for (const id of searchResults) {
      const item = indexedItems.value.get(id as string)
      if (item) {
        // Find snippet around match
        const snippet = findSnippet(item.content, q.toLowerCase())

        mapped.push({
          id: item.id,
          type: item.type,
          title: item.title,
          subtitle: item.subtitle,
          level: item.level,
          category: item.category,
          matchedIn: getMatchLocation(item.content, q.toLowerCase()),
          snippet,
          route: item.route,
        })
      }
    }

    return mapped
  }

  function findSnippet(content: string, query: string): string {
    const idx = content.indexOf(query.toLowerCase())
    if (idx === -1) return content.slice(0, 100) + '...'

    const start = Math.max(0, idx - 40)
    const end = Math.min(content.length, idx + query.length + 60)
    let snippet = content.slice(start, end)

    if (start > 0) snippet = '...' + snippet
    if (end < content.length) snippet = snippet + '...'

    return snippet
  }

  function getMatchLocation(content: string, query: string): string {
    // Determine if match is in title, description, or code
    if (content.includes('def ') || content.includes('class ') || content.includes('import ')) {
      return 'code'
    }
    return 'content'
  }

  function open() {
    isOpen.value = true
    buildIndex() // Start indexing if not already done
  }

  function close() {
    isOpen.value = false
    query.value = ''
    results.value = []
  }

  function updateQuery(q: string) {
    query.value = q
    results.value = search(q)
  }

  return {
    isIndexing,
    isIndexed,
    isOpen,
    query,
    results,
    buildIndex,
    search,
    open,
    close,
    updateQuery,
  }
})

function formatCategory(category: string): string {
  return category
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}
