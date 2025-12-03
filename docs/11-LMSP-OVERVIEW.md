# LMSP OVERVIEW - The Python Learning Game

**Navigation:** [README](README.md) | [Architecture](10-ARCHITECTURE.md) | [Player-Zero](12-PLAYER-ZERO-OVERVIEW.md) | [Palace Integration](13-PALACE-INTEGRATION.md)

---

## What is LMSP?

LMSP (Learn Me Some Py) is an **adaptive Python learning game** that teaches by playing. It combines:

- **Game mechanics** - Controllers, progression, achievements, flow states
- **Adaptive AI** - Learns YOUR learning style, fun patterns, frustration triggers
- **Project-driven curriculum** - "I want to build X" → generates themed challenges
- **Multiplayer** - Play WITH AI, AGAINST AI, TEACH AI, or watch AI play
- **Meta-learning** - Building LMSP teaches Python (the game IS the curriculum)

Traditional education gives everyone the same linear path. LMSP adapts to YOU - your pace, your interests, your dopamine patterns.

---

## File Structure

```
/mnt/castle/garage/learn-me-some-py/
├── .palace/                      # Palace integration
│   ├── config.json               # Project configuration
│   ├── history.jsonl             # Action log (append-only)
│   └── masks/                    # Expert personas for development
│       ├── game-designer/        # Game mechanics expertise
│       ├── python-teacher/       # Pedagogy expertise
│       └── accessibility-expert/ # Controller UX expertise
│
├── lmsp/                         # Main Python package
│   ├── __init__.py
│   ├── main.py                   # Entry point, CLI parsing
│   │
│   ├── game/                     # Core game loop
│   │   ├── __init__.py
│   │   ├── engine.py             # Main game loop, event handling
│   │   ├── state.py              # Game state management
│   │   ├── renderer.py           # Display (TUI/GUI)
│   │   └── audio.py              # Sound feedback (success, fail, etc.)
│   │
│   ├── input/                    # All input methods
│   │   ├── __init__.py
│   │   ├── emotional.py          # RT/LT emotional input ✓ DONE
│   │   ├── gamepad.py            # Controller handling (pygame)
│   │   ├── radial.py             # Radial thumbstick typing
│   │   ├── touch.py              # Touchscreen input
│   │   └── keyboard.py           # Fallback keyboard
│   │
│   ├── python/                   # Python concepts and validation
│   │   ├── __init__.py
│   │   ├── concepts.py           # Concept DAG loader/manager
│   │   ├── challenges.py         # Challenge loader from TOML
│   │   ├── verbs.py              # Python verb mappings (for Easy Mode)
│   │   └── validator.py          # Code execution & validation (sandboxed)
│   │
│   ├── progression/              # Skill tree and progression
│   │   ├── __init__.py
│   │   ├── tree.py               # Skill tree (DAG traversal)
│   │   ├── unlock.py             # Unlock conditions
│   │   ├── xp.py                 # Experience system
│   │   └── mastery.py            # Mastery levels (0-4)
│   │
│   ├── adaptive/                 # Adaptive learning engine
│   │   ├── __init__.py
│   │   ├── engine.py             # Core adaptive AI ✓ DONE
│   │   ├── spaced.py             # Spaced repetition (Anki-style)
│   │   ├── fun.py                # Fun/engagement tracking
│   │   ├── weakness.py           # Weakness detection & drilling
│   │   └── project.py            # Project-driven curriculum generator
│   │
│   ├── multiplayer/              # Player-Zero integration
│   │   ├── __init__.py
│   │   ├── session.py            # Game session management
│   │   ├── sync.py               # State synchronization
│   │   └── player_zero.py        # Player-Zero spawn/communication
│   │
│   └── introspection/            # Screenshot, video, TAS
│       ├── __init__.py
│       ├── screenshot.py         # Instant capture + metadata
│       ├── video.py              # Strategic recording
│       ├── wireframe.py          # Mental wireframe (AST + state)
│       └── mosaic.py             # WebP mosaic generation
│
├── concepts/                     # TOML concept definitions
│   ├── level_0/                  # Primitives
│   │   ├── variables.toml
│   │   ├── types.toml
│   │   └── print.toml
│   ├── level_1/                  # Control Flow
│   │   ├── if_else.toml
│   │   ├── for_loops.toml
│   │   ├── while_loops.toml
│   │   └── match_case.toml
│   ├── level_2/                  # Collections
│   │   ├── lists.toml            ✓ DONE
│   │   ├── in_operator.toml
│   │   ├── len.toml
│   │   └── sorted.toml
│   ├── level_3/                  # Functions
│   │   ├── def_return.toml
│   │   ├── parameters.toml
│   │   └── scope.toml            # THE BUG - global vs local
│   ├── level_4/                  # Intermediate
│   │   ├── comprehensions.toml
│   │   ├── lambda.toml
│   │   ├── min_max_key.toml
│   │   └── integer_division.toml
│   ├── level_5/                  # Classes
│   │   ├── class_init.toml
│   │   ├── self.toml
│   │   └── methods.toml
│   └── level_6/                  # Patterns
│       ├── container_pattern.toml
│       ├── median_pattern.toml
│       └── dispatch_pattern.toml
│
├── challenges/                   # Challenge definitions (TOML)
│   ├── container_basics/
│   │   ├── add_exists.toml       ✓ DONE
│   │   ├── remove.toml
│   │   └── get_next.toml
│   ├── median_finder/
│   │   ├── add_number.toml
│   │   ├── find_median.toml
│   │   └── optimized.toml
│   ├── pyramid_builder/
│   │   └── ...
│   └── query_dispatcher/
│       └── ...
│
├── tests/                        # TDD - tests first, always
│   ├── __init__.py
│   ├── test_emotional.py         ✓ DONE
│   ├── test_adaptive.py          ✓ DONE
│   ├── test_concepts.py
│   ├── test_challenges.py
│   ├── test_validator.py
│   ├── test_progression.py
│   ├── test_spaced.py
│   ├── test_fun.py
│   └── ...
│
├── assets/                       # Non-code resources
│   ├── radial_layouts/           # Radial menu configs (JSON)
│   │   ├── python_keywords.json
│   │   ├── operators.json
│   │   └── alphabet.json
│   ├── sounds/                   # Audio feedback
│   │   ├── success.wav
│   │   ├── fail.wav
│   │   ├── hint.wav
│   │   └── level_up.wav
│   └── themes/                   # Visual themes (JSON)
│       ├── dark.json
│       ├── light.json
│       └── cyberpunk.json
│
├── docs/                         # Documentation
│   └── (generated by swarm)
│
├── pyproject.toml                ✓ DONE
├── CLAUDE.md                     ✓ DONE (project instructions)
├── README.md                     ✓ DONE
└── ULTRASPEC.md                  # Complete technical spec
```

---

## Module Responsibilities

### game/ - Core Game Loop

**Purpose:** The beating heart of LMSP. Main loop, state management, rendering.

**Key Files:**

- **engine.py** - Main game loop
  - Event handling (input, AI, timers)
  - State transitions
  - Rendering orchestration
  - Multiplayer event routing

- **state.py** - Game state management
  - Current challenge
  - Code being written
  - Test results
  - Player position (line, column)
  - Session metadata (time, attempts)

- **renderer.py** - Display logic
  - TUI mode (Rich/Textual)
  - GUI mode (Pygame)
  - Code editor view
  - Test result panel
  - Progress indicators

- **audio.py** - Sound feedback
  - Success sounds (test pass, level up)
  - Fail sounds (test fail, error)
  - Ambient (flow state music)
  - Haptic integration (controller rumble)

**Example Flow:**
```python
# game/engine.py (simplified)
class GameEngine:
    def __init__(self):
        self.state = GameState()
        self.renderer = Renderer()
        self.adaptive = AdaptiveEngine()
        self.multiplayer = MultiplayerSession()

    async def run(self):
        """Main game loop."""
        while self.state.running:
            # 1. Process input (human or AI)
            events = await self.input.poll()

            # 2. Update state
            for event in events:
                self.handle_event(event)

            # 3. Broadcast to multiplayer (if active)
            if self.multiplayer.active:
                await self.multiplayer.broadcast(events)

            # 4. Render
            self.renderer.draw(self.state)

            # 5. Check for state transitions
            if self.state.challenge_complete:
                await self.handle_completion()
```

---

### input/ - All Input Methods

**Purpose:** Abstraction layer for all input devices. Controller-first design.

**Key Files:**

- **emotional.py** ✓ DONE - Analog emotional input via triggers
  - RT = enjoyment (0.0 to 1.0)
  - LT = frustration (0.0 to 1.0)
  - Y = complex response
  - Tracks state over time for flow detection

- **gamepad.py** - Controller handling
  - Pygame joystick integration
  - Button mapping (A/B/X/Y, bumpers, triggers)
  - Thumbstick reading (radial typing)
  - Haptic feedback (rumble)

- **radial.py** - Radial thumbstick typing
  - 8 directions per stick = 64 chords
  - Python keyword mapping (def, if, for, return)
  - Visual overlay (radial menu)
  - Learning mode (show hints)

- **touch.py** - Touchscreen input
  - Mobile support
  - Gesture recognition (swipe, pinch)
  - On-screen keyboard fallback

- **keyboard.py** - Keyboard fallback
  - Standard text input
  - Keyboard shortcuts
  - Vim-style navigation (optional)

**Example Emotional Input:**
```python
# input/emotional.py
from lmsp.input.emotional import EmotionalPrompt

prompt = EmotionalPrompt(
    question="How was that?",
    right_trigger="Satisfying",
    left_trigger="Frustrating"
)

# Update from controller
prompt.update(rt=0.7, lt=0.2, y_pressed=False, a_pressed=True)

# Get response when confirmed
if prompt.is_confirmed:
    dimension, value = prompt.get_response()
    # dimension: EmotionalDimension.ENJOYMENT
    # value: 0.7
```

---

### python/ - Concept System

**Purpose:** Load, manage, and validate Python concepts and challenges.

**Key Files:**

- **concepts.py** - Concept DAG
  - Load from TOML files
  - Build prerequisite graph
  - Topological sort for learning paths
  - Unlockable detection

- **challenges.py** - Challenge loader
  - Parse TOML challenge definitions
  - Skeleton code generation
  - Test case loading
  - Hint management

- **verbs.py** - Python verb mappings
  - Map gamepad buttons to Python keywords
  - Easy Mode: A → `def`, X → `if`, etc.
  - Context-aware suggestions

- **validator.py** - Code execution & validation
  - Sandboxed Python execution
  - Test running (compare expected vs actual)
  - Error handling (syntax, runtime)
  - Security (no file I/O, no network)

**Example Concept Loading:**
```python
# python/concepts.py
from lmsp.python.concepts import ConceptRegistry

registry = ConceptRegistry()
registry.load_from_directory("concepts/")

# Get unlockable concepts given current mastery
mastered = {"variables", "types", "print", "if_else"}
unlockable = registry.get_unlockable(mastered)
# Returns: [Concept("for_loops"), Concept("lists"), ...]
```

---

### progression/ - Skill Tree

**Purpose:** Track player progress, XP, unlocks, mastery levels.

**Key Files:**

- **tree.py** - Skill tree (DAG traversal)
  - Display available concepts
  - Show locked concepts with prerequisites
  - Path to specific concept

- **unlock.py** - Unlock conditions
  - Check prerequisites met
  - Handle special unlocks (achievements, events)

- **xp.py** - Experience system
  - XP per challenge completed
  - Bonus XP for speed, hints not used
  - Level thresholds

- **mastery.py** - Mastery levels (0-4)
  - Level 0: SEEN (locked)
  - Level 1: UNLOCKED (can attempt)
  - Level 2: PRACTICED (3+ completions)
  - Level 3: MASTERED (all challenges, speedrun)
  - Level 4: TRANSCENDED (can teach)

**Example Progression:**
```python
# progression/tree.py
from lmsp.progression import SkillTree, Mastery

tree = SkillTree()
tree.load_concepts(registry)

# Check if concept is unlocked
if tree.is_unlocked("for_loops", player.mastery):
    challenge = tree.get_challenge("for_loops")

# Record completion
tree.record_completion(
    concept="for_loops",
    player=player,
    time_seconds=45,
    hints_used=0
)

# Check mastery level
if player.mastery["for_loops"] >= Mastery.MASTERED:
    tree.unlock_advanced_challenges("for_loops")
```

---

### adaptive/ - Learning Engine

**Purpose:** The AI that learns YOU. Spaced repetition, fun tracking, weakness detection.

**Key Files:**

- **engine.py** ✓ DONE - Core adaptive AI
  - Recommendation logic (what to learn next)
  - Observation recording (attempts, emotions)
  - Profile management (save/load)

- **spaced.py** - Spaced repetition
  - Anki-style intervals (1h → 1d → 3d → 7d → 14d → 30d)
  - Due dates for review
  - Forgetting curve modeling

- **fun.py** - Fun/engagement tracking
  - Pattern detection (puzzle vs speedrun vs creation)
  - Flow state detection (high enjoyment + low frustration)
  - Break suggestions (fatigue detection)

- **weakness.py** - Weakness detection & drilling
  - Failure pattern analysis
  - Prerequisite gap identification
  - Gentle resurfacing (not punishment)

- **project.py** - Project-driven curriculum generator
  - Goal parsing ("I want to build a Discord bot")
  - Concept mapping (what's needed)
  - Challenge theming (all challenges fit goal)

**Example Adaptive Flow:**
```python
# adaptive/engine.py
from lmsp.adaptive import AdaptiveEngine, LearnerProfile

profile = LearnerProfile(player_id="wings")
engine = AdaptiveEngine(profile)

# Record attempt
engine.observe_attempt(
    concept="list_comprehensions",
    success=True,
    time_seconds=45,
    hints_used=0
)

# Record emotion
engine.observe_emotion(
    dimension=EmotionalDimension.ENJOYMENT,
    value=0.9,
    context="list_comprehensions"
)

# Get recommendation
rec = engine.recommend_next()
# rec.action: "challenge" | "review" | "break" | "project_step"
# rec.concept: "lambda_functions"
# rec.reason: "This brings you closer to: Discord bot"
```

---

### multiplayer/ - Player-Zero Integration

**Purpose:** Spawn AI players, synchronize state, manage multiplayer sessions.

**Key Files:**

- **session.py** - Game session management
  - Mode selection (coop, race, swarm, teach)
  - Player roster
  - Turn management (if applicable)
  - Win conditions

- **sync.py** - State synchronization
  - Event broadcasting to all players
  - State reconciliation (if desync)
  - Checkpoint creation for replay

- **player_zero.py** - Player-Zero spawn/communication
  - Spawn Player-Zero process(es)
  - Send game state as JSON events
  - Receive AI actions from stdout
  - Handle player disconnect/reconnect

**Example Multiplayer Session:**
```python
# multiplayer/session.py
from lmsp.multiplayer import MultiplayerSession, SessionMode
from player_zero import ClaudePlayer

# Create session
session = MultiplayerSession(mode=SessionMode.COOP)
session.add_human_player("Wings")
session.add_ai_player(ClaudePlayer(name="Lief", style="encouraging"))

# Start session
await session.start(challenge="container_add_exists")

# Broadcast event to all players
await session.broadcast({
    "type": "test_result",
    "player": "Wings",
    "passed": 3,
    "total": 5
})
```

---

### introspection/ - Screenshot, Video, TAS

**Purpose:** Deep visibility into game state for analysis and replay.

**Key Files:**

- **screenshot.py** - Instant capture + metadata
  - Capture screen image
  - Include wireframe (AST, state, players)
  - Optimized for Claude vision

- **video.py** - Strategic recording
  - Configurable FPS (1-60)
  - Duration-based capture
  - Frame selection for mosaic

- **wireframe.py** - Mental wireframe
  - AST of current code
  - Game state snapshot
  - Player state (mastery, emotion)
  - Session context

- **mosaic.py** - WebP mosaic generation
  - Compose frames into grid (4x4, 6x6, 8x8)
  - Show motion in single image
  - Optimized for Claude vision analysis

**Example Screenshot with Wireframe:**
```python
# introspection/screenshot.py
from lmsp.introspection import Screenshot

screenshot = Screenshot()
bundle = screenshot.capture()

# bundle.image: PIL Image
# bundle.wireframe: Wireframe object containing:
#   - code: Current code as string
#   - ast: Parsed AST
#   - cursor: (line, column)
#   - tests_passing: 3
#   - tests_total: 5
#   - player_id: "Wings"
#   - mastery_levels: {"lists": 2, "functions": 1, ...}
#   - current_emotion: EmotionalState(enjoyment=0.7, frustration=0.2)
```

---

## Key Files and Their Purposes

### Configuration Files

**pyproject.toml** - Python project configuration
- Dependencies (pygame, rich, anthropic, etc.)
- Entry points (`lmsp` command)
- Development dependencies (pytest, black, mypy)

**.palace/config.json** - Palace project configuration
- Strict mode enabled (TDD enforcement)
- Test command: `pytest tests/`
- Build command: `python -m build`

**concepts/\*/\*.toml** - Concept definitions
- Each concept has prerequisites, challenges, gotchas
- Used by ConceptRegistry to build DAG

**challenges/\*/\*.toml** - Challenge definitions
- Skeleton code, tests, hints, solutions
- Used by ChallengeLoader to present problems

---

## Development Workflow

### Adding a New Concept

1. **Create concept TOML** in `concepts/level_N/concept_name.toml`
2. **Define prerequisites** (must exist in DAG)
3. **Create challenges** in `challenges/concept_name/`
4. **Write tests FIRST** in `tests/test_concept_name.py`
5. **Implement validation logic** if needed (validator.py)
6. **Test with** `pal test`
7. **Commit** with `pal commit`

### Adding a New Input Method

1. **Create input module** in `lmsp/input/new_method.py`
2. **Inherit from InputDevice** protocol
3. **Implement** `poll()`, `render_overlay()`, `get_help()`
4. **Write tests FIRST** in `tests/test_new_method.py`
5. **Integrate** into `game/engine.py`
6. **Test** with `pal test`

### Adding a New Game Mode

1. **Define mode** in `multiplayer/session.py` (enum)
2. **Implement mode logic** (turn management, win conditions)
3. **Write tests FIRST** for mode
4. **Integrate** with Player-Zero communication
5. **Test** locally with AI player
6. **Document** in README

---

## Entry Points

### CLI Entry Point

```bash
# Single-player with keyboard
python -m lmsp

# Single-player with gamepad
python -m lmsp --input gamepad

# Multiplayer coop with AI
python -m lmsp --player-zero --mode coop

# Multiplayer race
python -m lmsp --player-zero --mode race --ai-count 2

# Swarm mode (N AIs)
python -m lmsp --mode swarm --ai-count 5
```

### Programmatic Entry Point

```python
from lmsp import LMSP
from lmsp.input import GamepadInput
from lmsp.multiplayer import MultiplayerSession, SessionMode

# Create game instance
game = LMSP(input_device=GamepadInput())

# Start single-player
await game.run()

# Or start multiplayer
session = MultiplayerSession(mode=SessionMode.COOP)
session.add_human_player("Wings")
session.add_ai_player_from_player_zero()
await session.start()
```

---

## Data Flow Within LMSP

### Challenge Flow

```
1. Adaptive Engine recommends concept
   ↓
2. SkillTree fetches challenge for concept
   ↓
3. ChallengeLoader loads TOML, creates Challenge object
   ↓
4. GameState updates with new challenge (skeleton code, tests)
   ↓
5. Renderer displays challenge and code editor
   ↓
6. Player writes code (via gamepad/keyboard)
   ↓
7. Player runs code (stick click or Enter)
   ↓
8. Validator executes code in sandbox, runs tests
   ↓
9. GameState updates with test results
   ↓
10. Renderer shows results (pass/fail, errors)
   ↓
11. If all tests pass:
    a. Emotional prompt appears
    b. Player gives feedback via triggers
    c. Adaptive Engine records attempt + emotion
    d. SkillTree updates mastery
    e. Multiplayer broadcasts completion
   ↓
12. Adaptive Engine recommends next concept (loop)
```

### Multiplayer Event Flow

```
1. Human types code
   ↓
2. GameEngine emits event: {"type": "keystroke", "player": "Wings", "char": "d"}
   ↓
3. MultiplayerSession broadcasts to all players
   ↓
4. Player-Zero AI reads event from stdin
   ↓
5. Player-Zero AI updates internal model
   ↓
6. Player-Zero AI decides on action
   ↓
7. Player-Zero emits: {"type": "thought", "player": "Lief", "content": "Defining a function!"}
   ↓
8. GameEngine reads from Player-Zero stdout
   ↓
9. GameEngine updates UI (show AI thought bubble)
   ↓
10. Renderer displays AI thought to human
```

---

## Testing Strategy

### Unit Tests

Each module has corresponding test file:
- `lmsp/adaptive/engine.py` → `tests/test_adaptive.py`
- `lmsp/input/emotional.py` → `tests/test_emotional.py`

**Coverage target:** 90%+ (enforced by Palace)

### Integration Tests

Test interactions between modules:
- `tests/integration/test_game_loop.py` - Full game loop
- `tests/integration/test_multiplayer.py` - Multiplayer session

### End-to-End Tests

Test full workflows:
- Complete a challenge from start to finish
- Multiplayer session with AI player
- Adaptive engine recommendation cycle

### Test Fixtures

Common fixtures in `tests/conftest.py`:
- Mock player profiles
- Sample challenges
- Fake input events

---

## Performance Considerations

### Code Validation

**Challenge:** Executing arbitrary Python code is slow and risky.

**Solution:**
- Sandbox execution (no file I/O, no network, no imports)
- Timeout limits (5 seconds max per test)
- AST parsing before execution (catch syntax errors early)

### Adaptive Engine

**Challenge:** Recommendation algorithm runs on every loop iteration.

**Solution:**
- Cache recommendations (invalidate on state change)
- Lazy loading of player history
- Profile stored as JSON (fast serialization)

### Multiplayer

**Challenge:** Broadcasting events to N players can be slow.

**Solution:**
- Async event broadcasting (don't block on slow players)
- Drop events if player can't keep up (best-effort delivery)
- Compress event stream (JSON minification)

### Rendering

**Challenge:** Re-rendering entire UI on every frame.

**Solution:**
- Dirty rectangle detection (only redraw changed areas)
- Double buffering (no flicker)
- FPS limiting (30 FPS is plenty for coding)

---

## Security Considerations

### Code Execution Sandbox

**Restrictions:**
- No file I/O (`open()` disabled)
- No network (`socket` disabled)
- No subprocess (`os.system()` disabled)
- No imports (except safe builtins)
- Memory limit (100MB)
- CPU limit (5 seconds)

**Implementation:**
```python
# python/validator.py
import ast
import builtins

def execute_sandboxed(code: str, test_input: Any) -> Any:
    """Execute code in restricted environment."""
    # Parse AST first (catch syntax errors)
    tree = ast.parse(code)

    # Build restricted globals
    safe_globals = {
        "__builtins__": {
            k: v for k, v in builtins.__dict__.items()
            if k in SAFE_BUILTINS
        }
    }

    # Execute with timeout
    exec(compile(tree, "<sandbox>", "exec"), safe_globals)

    # Call solution function
    return safe_globals["solution"](test_input)
```

### Player-Zero Communication

**Risks:**
- Malicious AI could send exploit payloads
- Infinite event loops

**Mitigations:**
- Schema validation for all events
- Rate limiting (max events per second)
- Drop unknown event types
- Timeout on AI response

---

**Next:** [Player-Zero Overview](12-PLAYER-ZERO-OVERVIEW.md) - Universal app automation framework

**See Also:**
- [Adaptive Engine](02-ADAPTIVE-ENGINE.md) - Deep dive into recommendation algorithm
- [Input Systems](03-INPUT-SYSTEMS.md) - Controller, radial typing, emotional input
- [Concept DAG](04-CONCEPT-DAG.md) - Prerequisite graph and unlocking
