/**
 * API Client
 * ==========
 *
 * Wrapper for API calls to the FastAPI backend.
 */

const BASE_URL = '/api'

interface ApiResponse<T> {
  data: T
  status: number
  ok: boolean
}

async function request<T>(
  method: string,
  path: string,
  body?: unknown
): Promise<ApiResponse<T>> {
  const url = path.startsWith('/api') ? path : `${BASE_URL}${path}`

  // Build headers - always include session for auth
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }

  // Add session token if available (for server-side player_id lookup)
  const sessionId = localStorage.getItem('lmsp_session')
  if (sessionId) {
    headers['X-Session-ID'] = sessionId
  }

  // Also send player_id header as fallback for profiles without passwords
  const playerId = localStorage.getItem('lmsp_player_id')
  if (playerId) {
    headers['X-Player-ID'] = playerId
  }

  const options: RequestInit = {
    method,
    headers,
  }

  if (body) {
    options.body = JSON.stringify(body)
  }

  const response = await fetch(url, options)
  const data = await response.json()

  return {
    data,
    status: response.status,
    ok: response.ok,
  }
}

export const api = {
  get: <T>(path: string) => request<T>('GET', path),
  post: <T>(path: string, body?: unknown) => request<T>('POST', path, body),
  put: <T>(path: string, body?: unknown) => request<T>('PUT', path, body),
  delete: <T>(path: string) => request<T>('DELETE', path),
}

// Challenge API
export const challengesApi = {
  list: (level?: number) => {
    const path = level !== undefined ? `/challenges?level=${level}` : '/challenges'
    return api.get<{ id: string; name: string; level: number; points: number }[]>(path)
  },
  get: (id: string) => api.get(`/challenges/${id}`),
  submit: (challengeId: string, code: string, playerId: string = 'default') =>
    api.post('/code/submit', { challenge_id: challengeId, code, player_id: playerId }),
}

// Player API
export const playerApi = {
  getProfile: (playerId: string = 'default') =>
    api.get(`/profile?player_id=${playerId}`),
  getAchievements: (playerId: string = 'default') =>
    api.get(`/achievements?player_id=${playerId}`),
  recordEmotional: (trigger: 'RT' | 'LT', value: number, context: string, playerId: string = 'default') =>
    api.post('/emotional/record', { player_id: playerId, trigger, value, context }),
  getRecommendations: (playerId: string = 'default') =>
    api.get(`/recommendations?player_id=${playerId}`),
}

// Concept Lessons API
export interface TryIt {
  prompt: string
  starter: string
  solution: string
}

export interface ConceptConnections {
  prerequisites: string[]
  enables: string[]
  used_in: string[]
  see_also: string[]
}

export interface ConceptLesson {
  id: string
  name: string
  level: number
  category: string
  description_brief: string
  description_detailed: string
  lesson: string  // Reference content (collapsible)
  try_it: TryIt | null
  connections: ConceptConnections
  time_to_read: number
  difficulty: string
  bonus: boolean
  status: string
}

export interface ConceptSummary {
  id: string
  name: string
  level: number
  time_to_read: number
  bonus: boolean
}

export const conceptsApi = {
  list: () => api.get<Record<string, ConceptSummary[]>>('/lessons'),
  get: (id: string) => api.get<ConceptLesson>(`/lessons/${id}`),
  getSolution: (id: string) => api.get<{ solution: string }>(`/lessons/${id}/solution`),
  markSeen: (id: string, playerId: string = 'default') =>
    api.post(`/lessons/${id}/mark-seen`, { player_id: playerId }),
  markUnderstood: (id: string, playerId: string = 'default') =>
    api.post(`/lessons/${id}/mark-understood`, { player_id: playerId }),
  forChallenge: (challengeId: string) =>
    api.get<ConceptSummary[]>(`/lessons/for-challenge/${challengeId}`),
}
