# LMSP Vue.js Frontend Architecture

## Stack

```
Frontend:
├── Vue.js 3 (Composition API)
├── TailwindCSS (OLED dark theme)
├── Pinia (State management)
├── Vue Router (SPA routing)
├── Three.js (3D visualizations - future)
└── WebGPU (Shader effects - future)

Backend:
├── FastAPI (JSON API)
└── WebSocket (Real-time gamepad/multiplayer)
```

## Directory Structure

```
frontend/
├── index.html
├── vite.config.ts
├── tailwind.config.js
├── package.json
├── tsconfig.json
├── src/
│   ├── main.ts
│   ├── App.vue
│   ├── router/
│   │   └── index.ts
│   ├── stores/
│   │   ├── game.ts           # Game state (current challenge, code)
│   │   ├── player.ts         # Player profile, achievements
│   │   └── gamepad.ts        # Gamepad connection state
│   ├── composables/
│   │   ├── useGamepad.ts     # Gamepad API integration
│   │   ├── useEmotional.ts   # RT/LT trigger feedback
│   │   └── useWebSocket.ts   # Real-time sync
│   ├── components/
│   │   ├── game/
│   │   │   ├── ChallengeView.vue
│   │   │   ├── CodeEditor.vue
│   │   │   ├── TestResults.vue
│   │   │   └── ChallengeList.vue
│   │   ├── input/
│   │   │   ├── GamepadStatus.vue
│   │   │   ├── EmotionalFeedback.vue
│   │   │   └── RadialMenu.vue
│   │   ├── progress/
│   │   │   ├── ProgressDashboard.vue
│   │   │   ├── ConceptTree.vue
│   │   │   └── AchievementPopup.vue
│   │   └── ui/
│   │       ├── OledPanel.vue
│   │       ├── AnimatedButton.vue
│   │       └── ConfettiEffect.vue
│   ├── views/
│   │   ├── HomeView.vue
│   │   ├── ChallengeView.vue
│   │   ├── ProgressView.vue
│   │   └── SettingsView.vue
│   ├── api/
│   │   ├── client.ts         # Axios/fetch wrapper
│   │   ├── challenges.ts     # Challenge API
│   │   ├── player.ts         # Profile API
│   │   └── emotional.ts      # Emotional feedback API
│   └── styles/
│       ├── main.css          # TailwindCSS imports
│       └── oled-theme.css    # OLED-specific styles
```

## OLED Dark Theme

**Core Principle:** Pure black (#000000) backgrounds for true OLED blacks

```css
:root {
  --bg-primary: #000000;      /* Pure black */
  --bg-secondary: #0a0a0a;    /* Near black */
  --bg-tertiary: #111111;     /* Panel backgrounds */
  --accent-primary: #00ff88;  /* Neon green */
  --accent-secondary: #0088ff; /* Electric blue */
  --text-primary: #ffffff;
  --text-secondary: #888888;
  --success: #00ff88;
  --warning: #ffaa00;
  --error: #ff4444;
}
```

## Key Components

### 1. ChallengeView.vue
- Displays challenge description
- Contains CodeEditor
- Shows test results
- Handles emotional feedback after completion

### 2. CodeEditor.vue
- Syntax-highlighted code editing
- Line numbers
- Auto-indent
- Gamepad-friendly (radial typing future)

### 3. EmotionalFeedback.vue
- Visual RT/LT pressure bars
- Animated gradient fills
- "How was that?" prompts
- Records to adaptive engine

### 4. GamepadStatus.vue
- Connection indicator
- Button mapping display
- Input mode switching (keyboard/gamepad/touch)

### 5. AchievementPopup.vue
- Beautiful unlock animations
- Confetti effects
- Tier-based styling
- Queue for sequential notifications

## State Management (Pinia)

### game.ts
```typescript
interface GameState {
  currentChallenge: Challenge | null;
  code: string;
  testResults: TestResult[];
  phase: 'menu' | 'coding' | 'testing' | 'feedback' | 'complete';
}
```

### player.ts
```typescript
interface PlayerState {
  playerId: string;
  profile: LearnerProfile;
  achievements: Achievement[];
  xp: number;
}
```

### gamepad.ts
```typescript
interface GamepadState {
  connected: boolean;
  leftTrigger: number;   // 0.0-1.0
  rightTrigger: number;  // 0.0-1.0
  buttons: Record<string, boolean>;
}
```

## API Integration

All API calls go through `/api/*` endpoints:
- `GET /api/challenges` - List challenges
- `GET /api/challenges/{id}` - Get challenge details
- `POST /api/code/submit` - Submit code for validation
- `GET /api/profile` - Get player profile
- `POST /api/emotional/record` - Record emotional feedback
- `GET /api/achievements` - Get achievements
- `GET /api/recommendations` - Get adaptive recommendations

## WebSocket (Future)

Real-time features via WebSocket:
- Gamepad input streaming
- Multiplayer sync (coop, race, teach)
- Live notifications

## Build & Deploy

```bash
# Development
cd lmsp/web/frontend
npm install
npm run dev

# Production build
npm run build
# Output to ../static/dist/
# FastAPI serves from there
```
