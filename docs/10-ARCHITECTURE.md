# ARCHITECTURE - The LMSP Ecosystem

**Navigation:** [README](README.md) | [LMSP Overview](11-LMSP-OVERVIEW.md) | [Player-Zero Overview](12-PLAYER-ZERO-OVERVIEW.md) | [Palace Integration](13-PALACE-INTEGRATION.md)

---

## The Big Picture

LMSP is not a monolithic application. It's three interlocking systems that work together to create an adaptive, multiplayer learning experience:

1. **LMSP (Learn Me Some Py)** - The Python learning game
2. **Player-Zero** - Universal app automation and AI player framework
3. **Palace** - RHSI development engine with TDD enforcement

Each system is valuable independently, but together they create something unprecedented: a learning environment that plays WITH you, learns from you, and helps you build it.

---

## Three Interlocking Systems

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         THE LMSP ECOSYSTEM                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐          │
│   │                 │   │                 │   │                 │          │
│   │  LEARN-ME-SOME  │◄──│   PLAYER-ZERO   │──►│   PALACE        │          │
│   │      -PY        │   │                 │   │                 │          │
│   │                 │   │                 │   │                 │          │
│   │  The Game       │   │  AI Players     │   │  RHSI Engine    │          │
│   │  Python Tutor   │   │  App Automation │   │  Development    │          │
│   │  Adaptive AI    │   │  Multi-Agent    │   │  TDD Enforcer   │          │
│   │                 │   │  TAS System     │   │                 │          │
│   └────────┬────────┘   └────────┬────────┘   └────────┬────────┘          │
│            │                     │                      │                   │
│            └─────────────────────┴──────────────────────┘                   │
│                                  │                                          │
│                         Stream-JSON Protocol                                │
│                         Shared State Awareness                              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## LMSP - The Game

**Purpose:** Teach Python through an adaptive, controller-native, multiplayer experience.

**What it does:**
- Presents Python challenges in a gameified format
- Adapts to individual learning styles using AI
- Tracks fun, engagement, and weaknesses
- Provides controller-first input (radial typing, emotional feedback)
- Manages progression through concept DAG
- Integrates with Player-Zero for multiplayer modes

**Key Capabilities:**
- **Adaptive Learning Engine** - Spaced repetition, fun tracking, weakness detection
- **Controller Input** - Radial thumbstick typing, emotional input via triggers
- **Progressive Disclosure** - DAG-based concept unlocking
- **Challenge Validation** - Execute Python code, verify outputs
- **State Management** - Track player progress, mastery levels, session data

**Primary Users:**
- Learners wanting to master Python through play
- Educators looking for engaging curriculum
- Developers building the game itself (meta-game)

**Location:** `/mnt/castle/garage/learn-me-some-py/`

---

## Player-Zero - Universal App Automation

**Purpose:** AI player simulation framework that automates and playtests ANY application.

**What it does:**
- Spawns AI players that interact with applications
- Records, replays, and analyzes interaction sessions
- Enables multiplayer modes (coop, competitive, teaching, swarm)
- Provides introspection tools (screenshots, video, TAS)
- Works with LMSP and far beyond it

**Supported Application Types:**
- **Python Games** - AI plays, finds bugs, tests edge cases, speedruns
- **Education Apps** - AI learns like a student, validates curriculum
- **Web Servers** - AI hits endpoints, validates behavior, fuzzes inputs
- **Browser Apps** - Playwright integration for visual testing
- **CLI Tools** - AI runs commands, validates outputs, tests flags
- **APIs** - AI generates test cases, validates schemas
- **Mobile Apps** - Via Appium integration, touch simulation

**Key Capabilities:**
- **AI Playtesting** - Claude plays your app like a user would
- **Bug Discovery** - AI explores edge cases humans miss
- **Demo Generation** - AI plays to generate marketing demos
- **Competitive Benchmarking** - Multiple AIs speedrun, compare approaches
- **Educational Content** - AI teaches by demonstrating
- **Accessibility Testing** - AI finds usability issues
- **Regression Testing** - AI replays sessions after changes
- **Load Testing** - Swarm of AIs simulate concurrent users

**Primary Users:**
- LMSP for multiplayer integration
- Developers playtesting their own applications
- QA teams automating test generation
- Content creators generating demos

**Location:** `/mnt/castle/garage/player-zero/`

---

## Palace - RHSI Development Engine

**Purpose:** Recursive Honesty-Seeking Intelligence engine that enforces TDD and guides development.

**What it does:**
- Enforces test-first development (strict mode)
- Provides AI-powered task suggestions
- Tracks development history
- Manages expert personas (masks)
- Orchestrates development workflows

**Key Features for LMSP:**
- **TDD Enforcement** - Tests must pass before session completion
- **RHSI Loops** - Recursive improvement through iteration
- **Mask System** - Expert personas (game designer, Python teacher, etc.)
- **History Logging** - Every action tracked in `.palace/history.jsonl`
- **Permission Handling** - Safe autonomous operation

**Development Commands:**
```bash
pal next -t --claude    # Suggest and execute next task
pal test               # Run tests
pal build              # Build project
pal run                # Execute application
```

**Primary Users:**
- LMSP developers building the game
- Any Palace-enabled project
- Teams wanting AI-guided TDD workflows

**Location:** `/mnt/castle/garage/palace-public/` (reference)

---

## Stream-JSON Protocol

The glue that connects all three systems: **stream-based JSON event broadcasting**.

### Core Concept

Every player (human or AI) emits a stream of JSON events to stdout. These events are broadcast to all other players in a session, creating **shared state awareness**.

### Event Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        EVENT BROADCAST                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Player A (Human)              Player B (AI - Claude)            │
│  ┌──────────────┐              ┌──────────────┐                 │
│  │ LMSP Game    │              │ Player-Zero  │                 │
│  │   Instance   │              │   Process    │                 │
│  └──────┬───────┘              └──────┬───────┘                 │
│         │                             │                         │
│         │ {"type": "keystroke",       │                         │
│         │  "player": "Wings",         │                         │
│         │  "char": "d"}               │                         │
│         ├─────────────────────────────►                         │
│         │                             │                         │
│         │     {"type": "thought",     │                         │
│         │◄─────"player": "Claude",    │                         │
│         │      "content": "Defining   │                         │
│         │       a function!"}         │                         │
│         │                             │                         │
│         │ {"type": "test_result",     │                         │
│         │  "player": "Wings",         │                         │
│         │  "passed": 3, "total": 5}   │                         │
│         ├─────────────────────────────►                         │
│         │                             │                         │
└─────────┴─────────────────────────────┴─────────────────────────┘
```

### Event Types

**Game Events:**
```json
{"type": "cursor_move", "player": "Wings", "line": 5, "col": 12}
{"type": "keystroke", "player": "Wings", "char": "d"}
{"type": "test_result", "player": "Wings", "passed": 3, "total": 5}
{"type": "completion", "player": "Lief", "time_seconds": 145}
```

**AI Events:**
```json
{"type": "thought", "player": "Lief", "content": "Defining a function!"}
{"type": "suggestion", "player": "Lief", "content": "Don't forget the colon"}
{"type": "hint_request", "player": "Lief", "concept": "scope"}
```

**Emotional Events:**
```json
{"type": "emotion", "player": "Wings", "dimension": "enjoyment", "value": 0.8}
{"type": "emotion", "player": "Wings", "dimension": "frustration", "value": 0.2}
```

**Session Events:**
```json
{"type": "session_start", "mode": "coop", "challenge": "container_add_exists"}
{"type": "player_join", "player": "Claude-2", "role": "helper"}
{"type": "checkpoint", "name": "before_bug", "state": {...}}
```

### Implementation (Palace Reference)

From Palace's multi-agent implementation:

```python
def _forward_to_other_agents(self, source_player_id, event_json, players, done_players):
    """Forward event to other players' stdin for shared awareness."""
    for player_id, player_info in players.items():
        if player_id == source_player_id:
            continue  # Don't forward to self
        if player_id in done_players:
            continue
        try:
            player_info["process"].stdin.write(event_json + "\n")
            player_info["process"].stdin.flush()
        except:
            pass
```

Each player:
1. Reads JSON events from stdin (other players' actions)
2. Processes events and updates internal state
3. Emits own events to stdout
4. Session manager broadcasts to all other players

### Benefits

**Shared Awareness:**
- AI sees exactly what human is typing
- Human sees AI's thought process
- Both understand session context

**Extensibility:**
- New event types can be added without breaking protocol
- Players can ignore unknown events
- Custom metadata in any event

**Debugging:**
- Full session replay from event log
- Checkpoint creation from any event
- Diff between any two states

**Multi-Agent:**
- N players, not just 2
- Swarm mode: 10 AIs tackling same problem
- Teaching mode: 1 teacher, 5 students
- Spectator mode: Watch without interfering

---

## Data Flow Between Systems

### LMSP → Player-Zero

**When:** Multiplayer session starts

**Flow:**
1. LMSP spawns Player-Zero process(es) via `player_zero.spawn()`
2. LMSP sends initial game state as JSON event
3. Player-Zero AI reads game state, starts playing
4. LMSP broadcasts every game event to Player-Zero stdin
5. Player-Zero sends actions back via stdout

**Data:**
- Challenge description and tests
- Current code state
- Player progress (mastery levels, XP)
- Session configuration (mode, rules)

### Player-Zero → LMSP

**When:** AI makes a move or observation

**Flow:**
1. Player-Zero AI decides on action
2. Emits action as JSON event to stdout
3. LMSP reads from Player-Zero stdout
4. LMSP applies action to game state
5. LMSP broadcasts result to all players

**Data:**
- Keystrokes (typing code)
- Thoughts (AI narration)
- Suggestions (hints to human)
- Emotions (AI's simulated engagement)

### Palace → LMSP

**When:** Development workflow (`pal next`, `pal test`, etc.)

**Flow:**
1. Developer runs `pal next -t --claude`
2. Palace analyzes LMSP project state
3. Palace suggests next task (via AI or rules)
4. Palace executes task (with permission)
5. Palace runs tests to verify
6. Palace logs action to `.palace/history.jsonl`

**Data:**
- Project files (code, tests, docs)
- Test results (pass/fail counts)
- History context (previous actions)
- Mask instructions (expert guidance)

### LMSP → Palace

**When:** Developer commits changes

**Flow:**
1. LMSP code changes are saved
2. Developer runs `pal test`
3. Palace executes test suite
4. Palace reports results
5. In strict mode, prevents commit if tests fail

**Data:**
- Modified files
- Test output
- Coverage metrics
- Build artifacts

---

## System Boundaries and Responsibilities

### LMSP Owns

**Game Logic:**
- Challenge presentation and validation
- Code execution (sandboxed Python)
- Progression tracking (mastery, XP, unlocks)
- UI rendering (TUI/GUI)

**Learning Engine:**
- Adaptive algorithm (spaced repetition, fun tracking)
- Concept graph (DAG of prerequisites)
- Emotional input processing
- Curriculum generation (project-driven)

**User State:**
- Player profiles
- Progress persistence
- Session history
- Preferences

### Player-Zero Owns

**AI Players:**
- Claude integration (API calls)
- Player personas (teaching, competitive, etc.)
- Action generation (what to type next)
- Strategy selection

**Session Management:**
- Mode orchestration (coop, race, swarm, etc.)
- Player synchronization
- Event broadcasting
- Turn management (if applicable)

**Introspection:**
- Screenshot capture + wireframes
- Video recording + mosaics
- TAS recording/replay/rewind
- Checkpoint/diff system

**Universal Automation:**
- Playwright adapter (web apps)
- CLI adapter (command-line tools)
- Generic stdin/stdout protocol
- Application-agnostic abstractions

### Palace Owns

**Development Workflow:**
- Task suggestion (AI-powered)
- Test orchestration
- Build management
- Commit validation

**TDD Enforcement:**
- Test-first verification
- Coverage tracking
- Strict mode (no commit without passing tests)

**History & Context:**
- Action logging (`.palace/history.jsonl`)
- Session replay
- Context building for AI

**Mask System:**
- Expert persona loading
- Specialized instructions
- Domain knowledge injection

---

## Why This Architecture?

### Separation of Concerns

Each system has a clear, focused purpose:
- **LMSP** - Learning experience
- **Player-Zero** - AI automation
- **Palace** - Development rigor

No system needs to understand the internals of others. Clean boundaries via stream-JSON protocol.

### Reusability

**Player-Zero** is not LMSP-specific:
- Use it to playtest web apps
- Use it to fuzz APIs
- Use it to generate demos
- Use it to automate CLI testing

**Palace** is not LMSP-specific:
- Any project can use `pal next`
- TDD enforcement works everywhere
- Masks adapt to any domain

### Extensibility

**Add new game modes** by extending LMSP's session types - Player-Zero adapts automatically.

**Add new app types** by creating Player-Zero adapters - no changes to LMSP needed.

**Add new development workflows** by creating Palace masks - works with any codebase.

### Testability

Each system can be tested in isolation:
- LMSP tests: Challenge logic, adaptive engine, progression
- Player-Zero tests: Event handling, AI interaction, recording
- Palace tests: Task generation, test running, history logging

Integration tests verify protocol compatibility.

### Multiplayer-First

The architecture was designed for multiplayer from day one:
- Stream-JSON enables N players
- LMSP doesn't care if player is human or AI
- Player-Zero can spawn multiple AI personas
- Session manager handles synchronization

Single-player mode is just "multiplayer with one player".

---

## Technical Stack

### LMSP
- **Language:** Python 3.12+
- **UI:** Rich/Textual (TUI), Pygame (GUI)
- **Input:** pygame gamepad, keyboard
- **Data:** TOML (configs), JSON (state)
- **Testing:** pytest

### Player-Zero
- **Language:** Python 3.12+
- **AI:** Anthropic Claude API
- **Automation:** Playwright (web), subprocess (CLI)
- **Recording:** JSON-based event log
- **Sandboxing:** Podman (rootless containers)

### Palace
- **Language:** Rust (CLI), Python (masks)
- **AI:** Claude API via MCP
- **History:** JSONL append-only log
- **Testing:** cargo test, pytest

### Protocol
- **Format:** JSON Lines (one event per line)
- **Transport:** stdin/stdout pipes
- **Schema:** Dynamic (versioned event types)

---

## Deployment Scenarios

### Local Single-Player
```
┌───────────────────┐
│   LMSP Process    │
│   (Python)        │
└───────────────────┘
```
LMSP runs standalone. No Player-Zero, no multiplayer.

### Local Multiplayer (1 Human + AI)
```
┌───────────────────┐      Stream-JSON      ┌───────────────────┐
│   LMSP Process    │◄─────────────────────►│ Player-Zero       │
│   (Human Player)  │                        │ (AI Player)       │
└───────────────────┘                        └───────────────────┘
```
LMSP spawns one Player-Zero process. Coop or competitive mode.

### Local Swarm (1 Human + N AIs)
```
                                  ┌───────────────────┐
                         ┌───────►│ Player-Zero (AI1) │
                         │        └───────────────────┘
┌───────────────────┐    │
│   LMSP Process    │◄───┼───────►┌───────────────────┐
│   (Human Player)  │    │        │ Player-Zero (AI2) │
└───────────────────┘    │        └───────────────────┘
                         │
                         └───────►┌───────────────────┐
                                  │ Player-Zero (AI3) │
                                  └───────────────────┘
```
LMSP spawns multiple Player-Zero processes. Swarm mode.

### Development with Palace
```
┌───────────────────┐
│   Developer       │
│   (runs pal next) │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐      Analyzes       ┌───────────────────┐
│   Palace          │─────────────────────►│   LMSP Codebase   │
│   (Rust CLI)      │                      │   (Python)        │
└───────────────────┘                      └───────────────────┘
         │
         │ Runs
         ▼
┌───────────────────┐
│   pytest          │
│   (Test Suite)    │
└───────────────────┘
```
Palace orchestrates development. Enforces TDD. Logs history.

---

## Future Extensions

### Network Multiplayer
```
┌───────────────────┐                        ┌───────────────────┐
│   LMSP Client 1   │◄──────┐       ┌───────►│   LMSP Client 2   │
│   (Human)         │       │       │        │   (Human)         │
└───────────────────┘       │       │        └───────────────────┘
                            │       │
                            ▼       ▼
                    ┌───────────────────┐
                    │  Session Server   │
                    │  (Broadcasts JSON)│
                    └───────────────────┘
                            ▲       ▲
                            │       │
┌───────────────────┐       │       │        ┌───────────────────┐
│   Player-Zero 1   │◄──────┘       └───────►│   Player-Zero 2   │
│   (AI)            │                        │   (AI)            │
└───────────────────┘                        └───────────────────┘
```
Central server broadcasts events to all connected players.

### Web-Based LMSP
```
┌───────────────────┐
│   Browser         │
│   (React + WASM)  │
└────────┬──────────┘
         │ WebSocket
         ▼
┌───────────────────┐      Stream-JSON      ┌───────────────────┐
│   LMSP Server     │◄─────────────────────►│   Player-Zero     │
│   (Python/FastAPI)│                        │   (AI Players)    │
└───────────────────┘                        └───────────────────┘
```
LMSP runs in browser via WebAssembly. Server handles AI players.

### Mobile App
```
┌───────────────────┐
│   Mobile App      │
│   (Touchscreen)   │
└────────┬──────────┘
         │ HTTP/WebSocket
         ▼
┌───────────────────┐      Stream-JSON      ┌───────────────────┐
│   LMSP Backend    │◄─────────────────────►│   Player-Zero     │
│   (Cloud)         │                        │   (Cloud AI)      │
└───────────────────┘                        └───────────────────┘
```
Native mobile app with cloud-based AI players.

---

## Key Design Decisions

### Why Stream-JSON?

**Alternatives Considered:**
- gRPC: Too heavyweight, requires code generation
- REST APIs: Doesn't fit stream paradigm
- WebSockets: Adds network layer unnecessarily
- Shared memory: Not portable, complex synchronization

**Why JSON Lines Won:**
- Human-readable (easy debugging)
- Language-agnostic (Python, Rust, JavaScript all support it)
- Stream-friendly (one event per line)
- Self-describing (each event contains type)
- Extensible (add fields without breaking protocol)
- Simple (no complex parsing, no schemas required)

### Why Python for LMSP?

Teaching Python BY BUILDING in Python creates meta-learning:
- Every file is both code AND lesson
- Learners read the game's source to understand concepts
- Contributing improves the tool that taught them
- Self-documenting ("This file demonstrates...")

### Why Separate Player-Zero?

**Could have been integrated into LMSP**, but:
- Player-Zero is useful beyond LMSP (web testing, CLI automation)
- Separation enables independent evolution
- Clean boundaries enforce protocol design
- Reusability across different learning games

### Why Palace Integration?

**Could have used standard tools (Make, pytest directly)**, but:
- Palace enforces TDD rigorously (prevents shortcuts)
- AI-powered task suggestions accelerate development
- History logging provides context for debugging
- Masks enable domain expertise (game design, Python pedagogy)

---

**Next:** [LMSP Overview](11-LMSP-OVERVIEW.md) - Deep dive into the game's structure

**See Also:**
- [Player-Zero Overview](12-PLAYER-ZERO-OVERVIEW.md) - Universal app automation
- [Palace Integration](13-PALACE-INTEGRATION.md) - Development workflow
- [Stream-JSON Protocol](docs/13-STREAM-JSON.md) - Event specification
