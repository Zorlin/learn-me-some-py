# Learn Me Some Py (LMSP)

**The game that teaches you to build it.**

Learn Python by actually building this game - with full controller support, adaptive AI, and multiplayer.

## Vision

Traditional coding education is:
- Linear (everyone learns the same way)
- Boring (endless text tutorials)
- Disconnected (learn concepts, not projects)
- Lonely (solo grinding)

LMSP is:
- **Adaptive** - AI learns YOUR learning style, fun patterns, and weaknesses
- **Gameified** - Full controller support, achievements, progression trees
- **Project-driven** - Tell it what you want to build, it creates curriculum backwards
- **Social** - Multiplayer modes: coop, competitive, teaching, spectating

## Core Features

### Input Revolution

**Radial Thumbstick Typing**
- 8 directions per stick = 256 chord combinations
- Python tokens mapped to muscle memory
- Visual radial menu overlay
- `def` = L-Up + R-Right, `return` = L-Down + R-Left

**Easy Mode (Training Wheels)**
- A: Create function (`def ___():`)
- B: Return statement
- X: If statement
- Y: For loop
- LB: Undo
- RB: Smart-complete (context-aware)
- Start: Run code
- Select: Show hint

### Adaptive Learning Engine

**Spaced Repetition**
- Concepts resurface at optimal intervals
- Anki-style scheduling based on mastery

**Fun Tracking**
- Detects engagement patterns
- "You spent 40 mins on list comprehensions smiling" → more of that flavor
- Adjusts challenge types to your dopamine patterns

**Weakness Detection**
- Tracks failure patterns
- "Failed modulo 3 times" → gentle resurfacing
- Never punishing, always encouraging

**Project-Driven Curriculum**
```
You: "I want to build a Discord bot"
LMSP: "Cool! Here's what you need to learn:"
      - Level 2: Collections (for storing messages)
      - Level 3: Functions (for bot commands)
      - Level 4: Async (for Discord API)
      → Generates challenges THEMED around your goal
```

### Progressive Disclosure

Concepts unlock based on prerequisites (DAG, not linear):

```
Level 0 (Primitives)     Level 1 (Control)      Level 2 (Collections)
├─ Variables        ──→  ├─ if/else        ──→  ├─ Lists
├─ Types                 ├─ for loops           ├─ "in" operator
└─ Print                 ├─ while               └─ sorted()
                         └─ match/case
                                │
Level 3 (Functions)      Level 4 (Intermediate) Level 5 (Classes)
├─ def, return      ──→  ├─ Comprehensions ──→  ├─ class, __init__
├─ Parameters            ├─ Lambda              ├─ self
└─ Scope (THE BUG!)      ├─ min/max + key=      └─ Methods
                         └─ // and int()
```

### Multiplayer (via player-zero)

**Modes:**
- **COOP**: Shared cursor, take turns, solve together
- **PAIR**: Split screen, different parts of same problem
- **RACE**: Same problem, first to pass wins
- **TEACH**: One player explains to AI students
- **SWARM**: N Claudes tackle different approaches simultaneously

**AI Players:**
- Full Claude integration via stream-JSON
- AI can play WITH you, AGAINST you, or LEARN from you
- Spectator mode: Watch AI solve with real-time explanations

### Introspection System

**Screenshot Wireframes**
- Instant capture: `Ctrl+Shift+S` or gamepad `Start+Select`
- Includes full context: AST, game state, player positions
- Optimized for Claude vision analysis

**Strategic Video Recording**
- Configurable FPS (1-60) and duration
- Output as mosaic WebP tiles
- 4x4, 6x6, or 8x8 grid of frames
- Motion visible in single image

**TAS Capabilities**
- `/checkpoint <name>` - Save state
- `/restore <name>` - Load state
- `/rewind <n>` - Go back n steps
- `/step` - Single-step execution
- `/diff <a> <b>` - Compare checkpoints

## Architecture

```
learn-me-some-py/
├── src/
│   ├── game/           # Core game loop, state, rendering
│   ├── input/          # Gamepad, radial typing, touch, keyboard
│   ├── python/         # Concept graph, challenges, validation
│   ├── progression/    # Skill tree, XP, unlocks
│   ├── adaptive/       # Spaced repetition, fun tracking, weakness detection
│   ├── multiplayer/    # player-zero integration
│   └── introspection/  # Screenshot, video, wireframe, mosaic
├── concepts/           # TOML definitions for each level
├── challenges/         # Challenge sets themed by use case
└── assets/             # Radial layouts, sounds, themes
```

## Challenge Format

```toml
[challenge]
id = "container_add_exists"
name = "Container: Add and Exists"
level = 2
prerequisites = ["lists_basics", "functions_basics", "in_operator"]

[description]
brief = "Build a container that can add values and check if they exist"

[tests]
[[tests.case]]
input = [["ADD", "1"], ["EXISTS", "1"]]
expected = ["", "true"]

[hints]
level_1 = "You'll need a list to store values"
level_2 = "The 'in' operator checks membership"

[gamepad_hints]
easy_mode = "Press A to create solution function, Y to loop through queries"

[adaptive]
fun_factor = "puzzle"           # What type of fun is this?
weakness_signals = ["scope", "returns"]  # What weaknesses does failing reveal?
project_themes = ["api", "database", "game_state"]  # What projects use this?
```

## Getting Started

```bash
# Build
cargo build --release

# Run with keyboard
./target/release/lmsp

# Run with controller
./target/release/lmsp --input gamepad

# Run with AI player
./target/release/lmsp --player-zero

# Start multiplayer session
./target/release/lmsp --multiplayer --mode coop
```

## Philosophy

**Learning should feel like playing.**

We don't hide the difficulty - we make it FUN. The same brain chemicals that make games addictive can make learning addictive. The same flow states that speedrunners achieve can happen while mastering Python.

You're not studying. You're training. You're speedrunning. You're competing. You're creating.

And the AI is right there with you - not judging, not grading, but PLAYING.

---

*Built in The Forge. Powered by Palace.*
