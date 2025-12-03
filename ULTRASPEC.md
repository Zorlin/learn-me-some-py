# LEARN ME SOME PY (LMSP) - ULTRASPEC

## "The game that teaches you to build it."

### A Complete Technical Specification for Palace-Driven Development

---

## PART I: VISION

### 1.1 The Problem

Traditional coding education is fundamentally broken:

- **Linear** - Everyone learns the same way, in the same order
- **Boring** - Endless text tutorials, no dopamine, no flow
- **Disconnected** - Learn abstract concepts, never build what you want
- **Lonely** - Solo grinding with no collaboration or competition
- **Passive** - Click-through lessons that don't require real engagement
- **Forgetful** - No spaced repetition, concepts fade within days
- **Binary** - Pass/fail feedback, no emotional nuance

### 1.2 The Solution

LMSP is a **learning relationship engine** disguised as a game:

- **Adaptive** - AI learns YOUR learning style, YOUR dopamine patterns, YOUR frustration threshold
- **Fun-first** - Full controller support, achievements, flow states, competitive modes
- **Project-driven** - Tell it what you want to build, it generates curriculum BACKWARDS
- **Social** - Multiplayer AI: coop, competitive, teaching, spectating
- **Active** - Analog emotional input via controller triggers
- **Remembering** - Spaced repetition surfaces concepts before you forget
- **Meta** - Building the game teaches the language; the curriculum IS the codebase

### 1.3 The Core Innovation

**Analog Emotional Feedback via Controller Triggers**

```
"How are you feeling?"

  [RT ████████░░] Pull right for happiness
  [LT ██░░░░░░░░] Pull left for frustration
  [Y] Complex response

  Press A to confirm
```

This isn't a survey. This is **real-time biometric-style input**:
- RT pressure = happiness gradient (0.0 to 1.0)
- LT pressure = frustration gradient
- Speed of response = engagement level
- Combined patterns = flow state detection

The game FEELS you. Not through invasive monitoring - through natural, intuitive input that happens to be emotionally granular.

---

## PART II: ARCHITECTURE

### 2.1 Three Interlocking Systems

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

### 2.2 LMSP (Learn Me Some Py) - The Game

**Purpose:** Teach Python through an adaptive, controller-native, multiplayer experience.

**File Structure:**
```
/mnt/castle/garage/learn-me-some-py/
├── .palace/                      # Palace integration
│   ├── config.json               # Project configuration
│   ├── history.jsonl             # Action log
│   └── masks/                    # Expert personas
├── lmsp/                         # Main Python package
│   ├── __init__.py
│   ├── main.py                   # Entry point
│   ├── game/
│   │   ├── __init__.py
│   │   ├── engine.py             # Core game loop
│   │   ├── state.py              # Game state management
│   │   ├── renderer.py           # Display (TUI/GUI)
│   │   └── audio.py              # Sound feedback
│   ├── input/
│   │   ├── __init__.py
│   │   ├── emotional.py          # RT/LT emotional input ✓ DONE
│   │   ├── gamepad.py            # Controller handling
│   │   ├── radial.py             # Radial thumbstick typing
│   │   ├── touch.py              # Touchscreen input
│   │   └── keyboard.py           # Fallback keyboard
│   ├── python/
│   │   ├── __init__.py
│   │   ├── concepts.py           # Concept DAG
│   │   ├── challenges.py         # Challenge loader
│   │   ├── verbs.py              # Python verb mappings
│   │   └── validator.py          # Code execution & validation
│   ├── progression/
│   │   ├── __init__.py
│   │   ├── tree.py               # Skill tree (DAG)
│   │   ├── unlock.py             # Unlock conditions
│   │   ├── xp.py                 # Experience system
│   │   └── mastery.py            # Mastery levels (0-4)
│   ├── adaptive/
│   │   ├── __init__.py
│   │   ├── engine.py             # Core adaptive AI ✓ DONE
│   │   ├── spaced.py             # Spaced repetition (Anki-style)
│   │   ├── fun.py                # Fun/engagement tracking
│   │   ├── weakness.py           # Weakness detection & drilling
│   │   └── project.py            # Project-driven curriculum generator
│   ├── multiplayer/
│   │   ├── __init__.py
│   │   ├── session.py            # Game session management
│   │   ├── sync.py               # State synchronization
│   │   └── player_zero.py        # player-zero integration
│   └── introspection/
│       ├── __init__.py
│       ├── screenshot.py         # Instant capture + metadata
│       ├── video.py              # Strategic recording
│       ├── wireframe.py          # Mental wireframe (AST + state)
│       └── mosaic.py             # WebP mosaic generation
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
├── challenges/                   # Challenge definitions
│   ├── container_basics/
│   │   ├── add_exists.toml       ✓ DONE
│   │   ├── remove.toml
│   │   └── get_next.toml
│   ├── median_finder/
│   ├── pyramid_builder/
│   └── query_dispatcher/
├── tests/                        # TDD - tests first
│   ├── __init__.py
│   ├── test_emotional.py         ✓ DONE
│   ├── test_adaptive.py          ✓ DONE
│   └── ...
├── assets/
│   ├── radial_layouts/           # Radial menu configs
│   ├── sounds/                   # Audio feedback
│   └── themes/                   # Visual themes
├── pyproject.toml                ✓ DONE
├── CLAUDE.md                     ✓ DONE
├── README.md                     ✓ DONE
└── ULTRASPEC.md                  # This document
```

### 2.3 Player-Zero - Universal App Automation

**Purpose:** AI player simulation framework that goes FAR beyond LMSP.

Player-Zero is a **universal app automation platform** that can playtest, analyze, and automate ANY application:

**Application Types:**
- **Python Games** → AI plays, finds bugs, tests edge cases, speedruns
- **Education Apps** → AI learns like a student, validates curriculum effectiveness
- **Web Servers** → AI hits endpoints, validates behavior, fuzzes inputs
- **Browser Apps** → Playwright integration for full visual testing
- **CLI Tools** → AI runs commands, validates outputs, tests flags
- **APIs** → AI generates test cases, validates schemas, stress tests
- **Mobile Apps** → Via Appium integration, touch simulation

**Capabilities:**
- **AI Playtesting** - Claude plays your app like a user would
- **Bug Discovery** - AI explores edge cases humans miss
- **Demo Generation** - AI plays your app to generate marketing demos
- **Competitive Benchmarking** - Multiple AIs speedrun, compare approaches
- **Educational Content** - AI teaches by demonstrating
- **Accessibility Testing** - AI finds usability and a11y issues
- **Regression Testing** - AI replays sessions after changes
- **Load Testing** - Swarm of AIs simulate concurrent users

**The Playwright Connection:**
```python
from player_zero import ClaudePlayer
from player_zero.browsers import PlaywrightAdapter

# AI playtests a web app
async with PlaywrightAdapter() as browser:
    player = ClaudePlayer(name="Tester")
    session = PlaytestSession(
        player=player,
        target=browser,
        goal="Find bugs in the checkout flow"
    )

    report = await session.run(
        max_duration=300,
        screenshot_interval=5,
        record_video=True
    )

    # report contains:
    # - All actions taken
    # - Screenshots with wireframes
    # - Video mosaic
    # - Bugs discovered
    # - Suggestions for improvement
```

**File Structure:**
```
/mnt/castle/garage/player-zero/
├── .palace/                      # Palace integration
├── player_zero/                  # Main Python package
│   ├── __init__.py
│   ├── main.py                   # CLI entry
│   ├── player/
│   │   ├── __init__.py
│   │   ├── base.py               # Player trait/protocol
│   │   ├── claude.py             # Claude player implementation
│   │   ├── human.py              # Human player adapter
│   │   └── composite.py          # Multi-player wrapper
│   ├── session/
│   │   ├── __init__.py
│   │   ├── base.py               # Session protocol
│   │   ├── coop.py               # Cooperative mode
│   │   ├── competitive.py        # Racing/competitive mode
│   │   ├── teaching.py           # One teaches, others learn
│   │   ├── spectator.py          # Watch AI with commentary
│   │   └── swarm.py              # N AIs, different approaches
│   ├── stream/
│   │   ├── __init__.py
│   │   ├── json.py               # Stream-JSON protocol
│   │   ├── broadcast.py          # Multi-player broadcast
│   │   └── sync.py               # State synchronization
│   ├── tas/
│   │   ├── __init__.py
│   │   ├── record.py             # Recording actions
│   │   ├── playback.py           # Replaying actions
│   │   ├── rewind.py             # Step backward
│   │   ├── checkpoint.py         # Save states
│   │   └── diff.py               # Compare checkpoints
│   ├── sandbox/
│   │   ├── __init__.py
│   │   ├── podman.py             # Rootless Podman integration
│   │   └── cgroups.py            # Direct cgroups (fallback)
│   └── introspection/
│       ├── __init__.py
│       ├── screenshot.py         # Capture + wireframe
│       ├── video.py              # Strategic recording
│       └── mosaic.py             # Frame mosaic for Claude vision
├── protocols/
│   ├── player.proto              # Player state protocol
│   └── game.proto                # Game state protocol
├── tests/
├── pyproject.toml
├── CLAUDE.md
└── README.md                     ✓ DONE
```

### 2.4 Palace Integration

LMSP and Player-Zero are both **Palace-native projects**:

```bash
cd /mnt/castle/garage/learn-me-some-py
pal next -t --claude              # Iterative development
pal test                          # Run tests
pal build                         # Build project
```

**Key Palace Features Used:**
- **TDD Enforcement** - Strict mode requires tests pass
- **RHSI Loops** - Recursive improvement through iteration
- **Mask System** - Expert personas for different aspects
- **History Logging** - Track all development actions
- **Permission Handling** - Safe autonomous operation

---

## PART III: THE ADAPTIVE LEARNING ENGINE

### 3.1 Core Loop

```python
async def adaptive_learning_loop():
    while learning:
        # 1. What should we learn next?
        strategy = engine.recommend_next()

        if strategy.action == "break":
            await suggest_break(strategy.reason)
            continue

        if strategy.action == "auto_advance":  # Flow state - keep momentum
            concept = strategy.concept
        else:
            # Present options via radial menu
            concept = await gamepad_select(strategy.options)

        # 2. Run the challenge
        result = await run_challenge(concept)

        # 3. Capture emotional feedback
        emotion = await emotional_prompt(
            "How was that?",
            right_trigger="Satisfying",
            left_trigger="Frustrating"
        )

        # 4. Update adaptive model
        engine.observe_attempt(
            concept=concept,
            success=result.passed,
            time_seconds=result.duration,
            hints_used=result.hints
        )
        engine.observe_emotion(emotion.dimension, emotion.value, concept)

        # 5. If multiplayer, sync state
        if player_zero.active:
            await player_zero.broadcast(GameEvent(
                type="attempt_complete",
                player=me,
                concept=concept,
                result=result,
                emotion=emotion
            ))
```

### 3.2 Recommendation Engine

The adaptive engine uses multiple signals to decide what to teach next:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        RECOMMENDATION PRIORITY                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. BREAK NEEDED?                                                            │
│     └─► Session too long? Frustration high? → Suggest break                 │
│                                                                              │
│  2. FRUSTRATION RECOVERY                                                     │
│     └─► High frustration detected → Offer flow-trigger concept              │
│         (Something they're good at and enjoy)                                │
│                                                                              │
│  3. SPACED REPETITION                                                        │
│     └─► Concept due for review? → Schedule review                           │
│         (Anki-style intervals: 1h → 1d → 3d → 7d → 14d → 30d)               │
│                                                                              │
│  4. PROJECT GOAL                                                             │
│     └─► Working toward a goal? → Next prereq for that goal                  │
│         "You want Discord bot? Next: async/await"                           │
│                                                                              │
│  5. WEAKNESS DRILLING                                                        │
│     └─► Failed 2+ times? → Gentle resurface with scaffolding                │
│         (Not punishment - support)                                           │
│                                                                              │
│  6. EXPLORATION                                                              │
│     └─► Nothing urgent → Something new and fun                              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.3 Fun Tracking

The game learns what YOU find fun:

```python
class FunTracker:
    """
    Tracks engagement patterns to understand what lights up YOUR brain.
    """

    def analyze_session(self, history: list[AttemptRecord]) -> FunProfile:
        """Build a profile of what this player enjoys."""

        patterns = {
            "puzzle": 0.0,      # Enjoys solving logic puzzles
            "speedrun": 0.0,    # Enjoys racing against time
            "collection": 0.0, # Enjoys unlocking/collecting
            "creation": 0.0,   # Enjoys building things
            "competition": 0.0, # Enjoys competing with others
            "mastery": 0.0,    # Enjoys perfecting skills
        }

        for attempt in history:
            # High enjoyment + long session = found their thing
            if attempt.emotion.enjoyment > 0.7:
                time_weight = min(attempt.duration / 300, 2.0)  # Cap at 5 min

                # Map challenge type to fun pattern
                challenge_type = self.get_challenge_type(attempt.concept)
                patterns[challenge_type] += attempt.emotion.enjoyment * time_weight

        return FunProfile(patterns)
```

### 3.4 Weakness Detection

Gentle, non-punishing weakness tracking:

```python
class WeaknessDetector:
    """
    Identifies struggle patterns and resurfaces concepts with support.
    """

    def detect_weakness(self, concept: str, history: list[AttemptRecord]) -> WeaknessSignal:
        """Analyze if this is a genuine weakness vs just a bad day."""

        failures = [a for a in history if a.concept == concept and not a.success]
        successes = [a for a in history if a.concept == concept and a.success]

        if len(failures) < 2:
            return None  # Not enough data

        # Check if failures are clustered or spread out
        if self.failures_are_clustered(failures):
            # Bad session, not genuine weakness
            return WeaknessSignal(
                concept=concept,
                severity="temporary",
                recommendation="Take a break, try tomorrow"
            )

        if len(failures) > len(successes) * 2:
            # Genuine struggle
            return WeaknessSignal(
                concept=concept,
                severity="needs_scaffolding",
                recommendation="Break into smaller pieces",
                prerequisites=self.get_unmastered_prereqs(concept)
            )
```

### 3.5 Project-Driven Curriculum

The killer feature: learning what you WANT to build.

```python
class ProjectCurriculumGenerator:
    """
    "I want to build a Discord bot"
    → Generates curriculum backwards from goal
    → Themes all challenges around that goal
    """

    async def generate_curriculum(self, goal_description: str) -> Curriculum:
        """Use Claude to analyze goal and map to concepts."""

        # 1. Analyze what the goal requires
        analysis = await claude_analyze(f"""
        The user wants to build: {goal_description}

        What Python concepts are needed? Map to these levels:
        - Level 0: variables, types, print
        - Level 1: if/else, for, while, match
        - Level 2: lists, in operator, len, sorted
        - Level 3: functions, parameters, scope
        - Level 4: comprehensions, lambda, min/max key
        - Level 5: classes, self, methods
        - Level 6: patterns (container, median, dispatch)

        Also identify domain-specific concepts needed.
        """)

        # 2. Build learning path
        concepts_needed = self.parse_concepts(analysis)
        learning_path = self.topological_sort(concepts_needed)

        # 3. Theme challenges around the goal
        themed_challenges = []
        for concept in learning_path:
            themed_challenges.append(await self.theme_challenge(
                concept,
                goal=goal_description
            ))

        return Curriculum(
            goal=goal_description,
            path=learning_path,
            challenges=themed_challenges,
            estimated_time=self.estimate_time(learning_path)
        )
```

---

## PART IV: INPUT SYSTEMS

### 4.1 Radial Thumbstick Typing

**The Innovation:** Two thumbsticks = 256 chord combinations = fast text input.

```
         ╭───────────╮                    ╭───────────╮
         │     ↑     │                    │     ↑     │
         │   (def)   │                    │  (space)  │
         │           │                    │           │
     ╭───┼───────────┼───╮            ╭───┼───────────┼───╮
     │ ← │     ●     │ → │            │ ← │     ●     │ → │
     │(if)│ L-STICK  │(in)│            │(:) │ R-STICK  │(=) │
     │   │           │   │            │   │           │   │
     ╰───┼───────────┼───╯            ╰───┼───────────┼───╯
         │     ↓     │                    │     ↓     │
         │ (return)  │                    │  (enter)  │
         ╰───────────╯                    ╰───────────╯

CHORD EXAMPLES:
  L-Up + R-Up       = "def"
  L-Up + R-Right    = "def "
  L-Left + R-Right  = "if "
  L-Down + R-Down   = newline + auto-indent
  L-Center + R-Center = space
```

**Chord Mapping Priority:**
1. Python keywords (def, if, for, while, return, class, etc.)
2. Operators (=, ==, !=, <, >, <=, >=, +, -, *, /)
3. Brackets/delimiters ((, ), [, ], {, }, :, ,)
4. Common variable names (i, j, x, n, self, value)
5. Alphabet (for custom identifiers)

### 4.2 Easy Mode (Training Wheels)

For absolute beginners - Python verbs as single button presses:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        EASY MODE GAMEPAD MAPPING                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Face Buttons:                                                              │
│     A  → def (create function) → prompts for name                           │
│     B  → return → prompts for value                                         │
│     X  → if → prompts for condition                                         │
│     Y  → for → prompts for iterator                                         │
│                                                                              │
│   Bumpers:                                                                   │
│     LB → Undo last action                                                   │
│     RB → Smart-complete (context-aware suggestion)                          │
│                                                                              │
│   Triggers:                                                                  │
│     LT → Dedent (decrease indentation)                                      │
│     RT → Indent (increase indentation)                                      │
│                                                                              │
│   Stick Clicks:                                                              │
│     L-Click → Run code                                                      │
│     R-Click → Validate (check without running)                              │
│                                                                              │
│   D-Pad:                                                                     │
│     Up/Down   → Navigate through code lines                                 │
│     Left/Right → Move cursor within line                                    │
│                                                                              │
│   Start  → Show hint                                                        │
│   Select → Open radial menu for advanced input                              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 Emotional Input (Trigger-Based)

The controller triggers become emotional gradient input:

```python
class EmotionalPrompt:
    """
    "Pull the right trigger progressively until you feel you've
     communicated how happy you are"
    """

    def __init__(
        self,
        question: str,
        right_trigger: str = "Happy",
        left_trigger: str = "Frustrated",
        y_button: str | None = "More options"
    ):
        self.question = question
        self.right_trigger = right_trigger
        self.left_trigger = left_trigger
        self.y_button = y_button

    def render(self) -> str:
        """Visual feedback showing trigger pressure."""
        rt_bar = "█" * int(self._rt_value * 10)
        lt_bar = "█" * int(self._lt_value * 10)

        return f"""
{self.question}

  [RT {rt_bar:10}] {self.right_trigger}
  [LT {lt_bar:10}] {self.left_trigger}
  {"[Y] " + self.y_button if self.y_button else ""}

  Press A to confirm
"""
```

---

## PART V: MULTIPLAYER (Player-Zero Integration)

### 5.1 Session Modes

**COOP Mode:**
```
┌──────────────────────────────────────────────────────────────┐
│                      COOP SESSION                             │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Challenge: Container Add/Exists                              │
│                                                               │
│  def solution(queries):                                       │
│      container = []  ← Wings                                  │
│      results = []                                             │
│      for command, value in queries:  ← Lief                  │
│          █                                                    │
│                                                               │
│  Wings is typing...                                           │
│  Lief: "Don't forget the colon!"                             │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

**RACE Mode:**
```
┌────────────────────────────┬────────────────────────────┐
│         WINGS              │          LIEF              │
├────────────────────────────┼────────────────────────────┤
│ def solution(queries):     │ def solution(queries):     │
│     container = []         │     c = []                 │
│     for q in queries:      │     r = []                 │
│         █                  │     for cmd, v in queries: │
│                            │         match cmd:         │
│ Tests: 2/5 passing         │ Tests: 4/5 passing         │
│ Time: 2:34                 │ Time: 2:12                 │
└────────────────────────────┴────────────────────────────┘
```

**TEACH Mode:**
```
┌──────────────────────────────────────────────────────────────┐
│                      TEACH SESSION                            │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Teacher: Lief (AI)                                          │
│  Students: Wings, Claude-2, Claude-3                          │
│                                                               │
│  Lief: "Let's build a container. First, we need              │
│         somewhere to store values. What data structure        │
│         would you use?"                                       │
│                                                               │
│  [Claude-2]: "A list!"                                       │
│  [Wings]: types "dictionary?"                                │
│                                                               │
│  Lief: "Both could work! Let's start with a list since       │
│         it's simpler. Wings, can you tell me why a           │
│         dictionary might also work?"                          │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

**SWARM Mode:**
```
┌──────────────────────────────────────────────────────────────┐
│                      SWARM SESSION                            │
│                 "Find the best solution"                      │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Claude-1 (brute_force): 45 lines, 12ms, all tests passing  │
│  Claude-2 (elegant):     23 lines, 8ms,  all tests passing   │
│  Claude-3 (fast):        31 lines, 3ms,  all tests passing   │
│  Claude-4 (readable):    52 lines, 15ms, all tests passing  │
│                                                               │
│  Analysis:                                                    │
│  - Claude-3's solution is fastest (optimized for speed)      │
│  - Claude-2's solution is most elegant (list comprehension)  │
│  - Claude-4's solution is most readable (verbose but clear)  │
│                                                               │
│  [View All] [Compare] [Learn From Best] [Hybrid]             │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### 5.2 Stream-JSON Protocol

The core of multi-agent awareness (from Palace):

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

**Event Types:**
```json
{"type": "cursor_move", "player": "Wings", "line": 5, "col": 12}
{"type": "keystroke", "player": "Wings", "char": "d"}
{"type": "thought", "player": "Lief", "content": "Defining a function!"}
{"type": "suggestion", "player": "Lief", "content": "Don't forget the colon"}
{"type": "emotion", "player": "Wings", "dimension": "enjoyment", "value": 0.8}
{"type": "test_result", "player": "Wings", "passed": 3, "total": 5}
{"type": "completion", "player": "Lief", "time_seconds": 145}
```

---

## PART VI: TAS (Tool-Assisted Learning)

### 6.1 Recording System

```python
class Recorder:
    """Record every action for replay and analysis."""

    def __init__(self):
        self.events: list[RecordedEvent] = []
        self.start_time: float = 0
        self.checkpoints: dict[str, int] = {}

    def record(self, event: GameEvent):
        """Record an event with timestamp."""
        self.events.append(RecordedEvent(
            timestamp=time.time() - self.start_time,
            event=event,
            game_state=self.capture_state()
        ))

    def checkpoint(self, name: str):
        """Save a named checkpoint."""
        self.checkpoints[name] = len(self.events)

    def rewind_to(self, name: str) -> GameState:
        """Restore state from checkpoint."""
        idx = self.checkpoints[name]
        return self.events[idx].game_state

    def export(self) -> Recording:
        """Export recording for sharing/analysis."""
        return Recording(
            events=self.events,
            checkpoints=self.checkpoints,
            duration=time.time() - self.start_time
        )
```

### 6.2 Replay System

```python
class Replayer:
    """Replay recordings for learning and analysis."""

    async def replay(self, recording: Recording, speed: float = 1.0):
        """Replay recording at given speed."""
        for i, event in enumerate(recording.events):
            # Wait appropriate time
            if i > 0:
                delay = (event.timestamp - recording.events[i-1].timestamp) / speed
                await asyncio.sleep(delay)

            # Apply event
            self.apply_event(event)

            # Render
            self.render(event, recording)

    async def step(self):
        """Single-step through recording."""
        self.current_idx += 1
        event = self.recording.events[self.current_idx]
        self.apply_event(event)
        return event

    async def rewind(self, steps: int = 1):
        """Step backward through recording."""
        self.current_idx = max(0, self.current_idx - steps)
        self.restore_state(self.recording.events[self.current_idx].game_state)
```

### 6.3 Diff System

```python
class Differ:
    """Compare checkpoints or recordings."""

    def diff_checkpoints(self, a: str, b: str) -> Diff:
        """Show what changed between checkpoints."""
        state_a = self.recording.get_state_at(a)
        state_b = self.recording.get_state_at(b)

        return Diff(
            code_changes=self.diff_code(state_a.code, state_b.code),
            test_changes=self.diff_tests(state_a.tests, state_b.tests),
            events_between=self.get_events_between(a, b)
        )

    def diff_approaches(self, recording_a: Recording, recording_b: Recording) -> ApproachDiff:
        """Compare two different approaches to same problem."""
        return ApproachDiff(
            time_difference=recording_a.duration - recording_b.duration,
            code_difference=self.semantic_diff(
                recording_a.final_code,
                recording_b.final_code
            ),
            approach_analysis=self.analyze_approaches(recording_a, recording_b)
        )
```

---

## PART VII: INTROSPECTION SYSTEM

### 7.1 Screenshot Wireframes

Every screenshot includes a "mental wireframe" - the full context behind what's visible:

```python
class Screenshot:
    """Capture screen state with full context metadata."""

    def capture(self) -> ScreenshotBundle:
        """Capture screenshot + wireframe."""
        return ScreenshotBundle(
            image=self.capture_screen(),
            wireframe=Wireframe(
                # Current code state
                code=self.game.current_code,
                ast=ast.parse(self.game.current_code),
                cursor_position=self.game.cursor,

                # Game state
                current_challenge=self.game.challenge,
                tests_passing=self.game.tests_passing,
                tests_total=self.game.tests_total,

                # Player state
                player_id=self.game.player.id,
                mastery_levels=self.game.player.mastery,
                current_emotion=self.game.player.last_emotion,

                # Session state
                session_duration=self.game.session_duration,
                challenges_completed=self.game.challenges_completed,

                # Multiplayer state (if active)
                other_players=[p.summary() for p in self.game.other_players]
            ),
            timestamp=time.time()
        )
```

### 7.2 Video Mosaics

Strategic video recording as mosaic tiles for Claude vision:

```python
class MosaicRecorder:
    """Record video as mosaic tiles optimized for Claude analysis."""

    async def record(
        self,
        duration_seconds: float,
        fps: int = 10,
        grid: tuple[int, int] = (4, 4)
    ) -> Mosaic:
        """Record video as mosaic."""
        frames = []
        interval = 1.0 / fps

        for _ in range(int(duration_seconds * fps)):
            frame = await self.capture_frame()
            frames.append(frame)
            await asyncio.sleep(interval)

        # Select frames for mosaic (evenly distributed)
        grid_size = grid[0] * grid[1]
        selected_frames = self.select_frames(frames, grid_size)

        # Compose into single image
        mosaic = self.compose_mosaic(selected_frames, grid)

        return Mosaic(
            image=mosaic,
            frame_count=len(frames),
            selected_indices=[frames.index(f) for f in selected_frames],
            duration=duration_seconds,
            fps=fps,
            grid=grid
        )

    def compose_mosaic(self, frames: list[Image], grid: tuple[int, int]) -> Image:
        """Compose frames into grid mosaic."""
        rows, cols = grid
        frame_w, frame_h = frames[0].size

        mosaic = Image.new('RGB', (cols * frame_w, rows * frame_h))

        for i, frame in enumerate(frames):
            row = i // cols
            col = i % cols
            mosaic.paste(frame, (col * frame_w, row * frame_h))

        return mosaic
```

### 7.3 Discovery Primitives

Progressive disclosure of introspection tools:

```python
PRIMITIVES = {
    # Level 0 - Always available
    "/help": "Show available commands",
    "/screenshot": "Capture current state",

    # Level 1 - After first challenge
    "/checkpoint <name>": "Save current state",
    "/restore <name>": "Restore saved state",

    # Level 2 - After 5 challenges
    "/rewind <n>": "Go back n steps",
    "/step": "Single-step forward",
    "/diff <a> <b>": "Compare checkpoints",

    # Level 3 - After completing a level
    "/video <duration>": "Record strategic video",
    "/mosaic <grid>": "Generate frame mosaic",
    "/wireframe": "Dump full context",

    # Level 4 - After teaching mode
    "/trace <function>": "Follow execution path",
    "/profile": "Performance analysis",
    "/explain": "AI explanation of current state",

    # Level 5 - After contributing
    "/discover-new": "List recently unlocked tools",
    "/teach <concept>": "Enter teaching mode",
    "/benchmark": "Compare your approach to others",

    # Meta
    "/discover": "List all available primitives",
}

def get_available_primitives(player: Player) -> list[str]:
    """Get primitives available to this player based on progress."""
    level = player.primitive_level
    return [p for p, info in PRIMITIVES.items() if info.unlock_level <= level]
```

---

## PART VIII: PROGRESSIVE DISCLOSURE

### 8.1 Concept DAG

Concepts are organized as a Directed Acyclic Graph, not a linear list:

```
                    ┌─────────────────┐
                    │   Level 0       │
                    │  ┌───────────┐  │
                    │  │ variables │  │
                    │  └─────┬─────┘  │
                    │        │        │
                    │  ┌─────┴─────┐  │
                    │  │   types   │  │
                    │  └─────┬─────┘  │
                    │        │        │
                    │  ┌─────┴─────┐  │
                    │  │   print   │  │
                    │  └───────────┘  │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
    ┌─────────▼─────────┐  ┌─▼─┐  ┌────────▼────────┐
    │     Level 1       │  │   │  │    Level 2      │
    │ ┌───────────────┐ │  │   │  │ ┌─────────────┐ │
    │ │    if_else    │ │  │   │  │ │    lists    │ │
    │ └───────┬───────┘ │  │   │  │ └──────┬──────┘ │
    │         │         │  │   │  │        │        │
    │ ┌───────▼───────┐ │  │   │  │ ┌──────▼──────┐ │
    │ │   for_loops   │ │  │   │  │ │ in_operator │ │
    │ └───────────────┘ │  │   │  │ └─────────────┘ │
    └───────────────────┘  └───┘  └─────────────────┘
                                           │
                    ┌──────────────────────┘
                    │
          ┌─────────▼─────────┐
          │     Level 3       │
          │ ┌───────────────┐ │
          │ │   functions   │ │
          │ └───────┬───────┘ │
          │         │         │
          │ ┌───────▼───────┐ │
          │ │     scope     │ │  ← THE BUG (global state leak)
          │ └───────────────┘ │
          └───────────────────┘
                    │
          ┌─────────▼─────────┐
          │     Level 4       │
          │ ┌───────────────┐ │
          │ │comprehensions │ │
          │ └───────┬───────┘ │
          │         │         │
          │ ┌───────▼───────┐ │
          │ │    lambda     │ │
          │ └───────────────┘ │
          └───────────────────┘
```

### 8.2 Mastery Levels

Each concept has 5 mastery levels:

```
Level 0: SEEN
  └─ Concept appears in tree but is locked
  └─ "You'll learn this after mastering: [prerequisites]"

Level 1: UNLOCKED
  └─ Can attempt challenges
  └─ Hints available at all levels
  └─ No time pressure

Level 2: PRACTICED
  └─ Completed 3+ challenges
  └─ Hints available but discouraged
  └─ Gentle time suggestions

Level 3: MASTERED
  └─ Completed all challenges
  └─ Achieved speed run time on at least one
  └─ Can use in higher-level challenges

Level 4: TRANSCENDED
  └─ Can explain to AI students (teaching mode)
  └─ Unlocks ability to teach this concept
  └─ Community content creation unlocked
```

### 8.3 Dynamic Concept Registration

The system is extensible - new concepts can plug in:

```python
class ConceptRegistry:
    """Dynamic concept registration for extensibility."""

    def __init__(self):
        self.concepts: dict[str, Concept] = {}
        self.dag: nx.DiGraph = nx.DiGraph()

    def register(self, concept: Concept):
        """Register a new concept into the DAG."""
        self.concepts[concept.id] = concept
        self.dag.add_node(concept.id)

        for prereq in concept.prerequisites:
            if prereq in self.concepts:
                self.dag.add_edge(prereq, concept.id)
            else:
                raise ValueError(f"Unknown prerequisite: {prereq}")

        # Validate DAG is still acyclic
        if not nx.is_directed_acyclic_graph(self.dag):
            self.dag.remove_node(concept.id)
            raise ValueError("Adding concept would create cycle")

    def get_unlockable(self, mastered: set[str]) -> list[Concept]:
        """Get concepts that can be unlocked given current mastery."""
        unlockable = []
        for concept_id, concept in self.concepts.items():
            if concept_id in mastered:
                continue
            if all(p in mastered for p in concept.prerequisites):
                unlockable.append(concept)
        return unlockable
```

---

## PART IX: IMPLEMENTATION PHASES

### Phase 1: MVP (Week 1-2)
```
Priority: Get something working

✅ = Done in scaffold
⏳ = In progress
⬜ = Not started

✅ Project structure
✅ Palace integration
✅ Emotional input system
✅ Adaptive engine core
✅ Tests for emotional/adaptive
✅ Sample concept (lists)
✅ Sample challenge (container_add_exists)
⬜ Basic game loop (keyboard only)
⬜ Challenge validation (run Python, check output)
⬜ Simple TUI with Rich/Textual
⬜ Concept DAG loading from TOML
```

### Phase 2: Controller (Week 3-4)
```
Priority: Make it feel like a game

⬜ Gamepad input with pygame
⬜ Easy mode button mappings
⬜ Radial typing prototype
⬜ Visual radial menu overlay
⬜ Haptic feedback integration
⬜ Audio feedback (success/fail sounds)
```

### Phase 3: Adaptive (Week 5-6)
```
Priority: Make it learn YOU

⬜ Spaced repetition scheduler
⬜ Fun tracking implementation
⬜ Weakness detection
⬜ Project-driven curriculum generator
⬜ Flow state detection and auto-advance
```

### Phase 4: Multiplayer (Week 7-8)
```
Priority: Play together

⬜ player-zero core framework
⬜ Stream-JSON protocol
⬜ Claude player implementation
⬜ COOP mode
⬜ RACE mode
⬜ Spectator mode
```

### Phase 5: Introspection (Week 9-10)
```
Priority: Deep analysis

⬜ Screenshot + wireframe
⬜ Video recording
⬜ Mosaic generation
⬜ TAS: record/replay/rewind
⬜ Discovery primitives
⬜ Palace Skill for introspection
```

### Phase 6: Polish (Week 11-12)
```
Priority: Make it beautiful

⬜ Visual themes
⬜ Achievement system
⬜ Progress visualization
⬜ Touchscreen mode
⬜ Community content support
⬜ Public beta
```

---

## PART X: SUCCESS METRICS

### Learning Efficacy
- **Concept retention**: >80% recall at 30 days (vs ~40% for passive learning)
- **Time to proficiency**: 50% faster than traditional courses
- **Flow state frequency**: >30% of session time in flow

### Engagement
- **Session length**: Average 25+ minutes (sweet spot)
- **Return rate**: >60% next-day return
- **Completion rate**: >70% complete chosen curriculum

### Controller Adoption
- **Easy mode graduation**: 80% move to radial typing within 10 hours
- **Radial typing speed**: 20+ WPM after 5 hours practice
- **Emotional input usage**: >90% use triggers for feedback

### Multiplayer
- **AI interaction quality**: >4/5 satisfaction with AI teaching
- **COOP completion**: >80% complete challenges in COOP mode
- **RACE engagement**: >60% try competitive mode

### Platform
- **Test coverage**: >90% (enforced by Palace)
- **Build reliability**: 100% (strict mode)
- **Extension adoption**: Community concepts used by >20% of players

---

## PART XI: THE META-GAME

### 11.1 Building LMSP Teaches Python

Every component of LMSP maps to Python concepts:

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                    THE META-CURRICULUM                                         │
├───────────────────────┬───────────────────────────────────────────────────────┤
│ LMSP Component        │ Python Concepts Taught                                │
├───────────────────────┼───────────────────────────────────────────────────────┤
│ Game state management │ Variables, dictionaries, state machines              │
│ Challenge loader      │ File I/O, TOML parsing, data structures              │
│ Emotional input       │ Classes, dataclasses, enums, properties              │
│ Adaptive engine       │ Algorithms, datetime, JSON serialization             │
│ Concept DAG           │ Graph theory, topological sort, recursion            │
│ Radial typing         │ Coordinate systems, trigonometry, mappings           │
│ Multiplayer sync      │ Async/await, networking, protocols                   │
│ TAS recording         │ Serialization, state management, compression         │
│ Introspection         │ AST, reflection, metaprogramming                     │
└───────────────────────┴───────────────────────────────────────────────────────┘
```

### 11.2 Self-Teaching Code Comments

Every source file ends with a self-teaching note:

```python
# Self-teaching note:
#
# This file demonstrates:
# - Dataclasses with default_factory (Level 5: Classes)
# - Type hints with Optional and dict (Professional Python)
# - datetime and timedelta (Standard library)
# - JSON serialization patterns (Level 4: Intermediate)
#
# Prerequisites to understand this file:
# - Level 2: Collections (lists, dicts)
# - Level 3: Functions (def, return, parameters)
# - Level 5: Classes (class, __init__, self)
#
# The learner will encounter this file AFTER mastering prerequisites.
```

### 11.3 Recursive Improvement

As players learn, they can IMPROVE LMSP itself:

1. **Complete challenges** → Understand patterns
2. **Read source code** → See patterns in action
3. **Find improvements** → Suggest or implement
4. **Contribute** → Code gets reviewed by AI + humans
5. **See contribution used** → Meta-satisfaction
6. **Help others** → Teaching mode unlocked

This creates a community of learner-contributors who improve the system that taught them.

---

## APPENDIX A: TOML SCHEMAS

### Concept Schema
```toml
[concept]
id = "string"                    # Unique identifier
name = "string"                  # Display name
level = 0                        # 0-6
prerequisites = ["concept_ids"]  # Must master before unlocking

[description]
brief = "string"                 # One-liner
detailed = """string"""          # Full explanation with examples

[methods]                        # For concepts that introduce methods
method_name = "description"

[gotchas]                        # Common mistakes
gotcha_name = """explanation"""

[gamepad_tutorial]
text = """how to use with controller"""

[challenges]
starter = "challenge_id"
intermediate = "challenge_id"
mastery = "challenge_id"

[fun_factor]
type = "puzzle|speedrun|collection|creation|competition|mastery"
description = "why this is fun"
examples = ["real-world uses"]

[adaptive]
weakness_signals = ["patterns that indicate struggle"]
strength_indicators = ["patterns that indicate mastery"]
```

### Challenge Schema
```toml
[challenge]
id = "string"
name = "string"
level = 0
prerequisites = ["concept_ids"]

[description]
brief = "string"
detailed = """string"""

[skeleton]
code = """starting code"""

[tests]
[[tests.case]]
name = "string"
input = [any]
expected = any

[hints]
level_1 = "gentle hint"
level_2 = "more specific"
level_3 = "almost solution"
level_4 = """pattern with code"""

[gamepad_hints]
easy_mode = """controller-specific tips"""

[solution]
code = """reference solution (hidden from player)"""

[meta]
time_limit_seconds = 300
speed_run_target = 60
points = 100
next_challenge = "challenge_id"

[adaptive]
fun_factor = "type"
weakness_signals = ["what failing reveals"]
project_themes = ["projects this applies to"]

[emotional_checkpoints]
after_first_test_pass = """feedback prompt"""
after_completion = """feedback prompt"""
```

---

## APPENDIX B: API REFERENCE

### Emotional Input
```python
from lmsp.input.emotional import EmotionalPrompt, EmotionalState, EmotionalDimension

# Create prompt
prompt = EmotionalPrompt(
    question="How was that?",
    right_trigger="Satisfying",
    left_trigger="Frustrating",
    y_button="Complex feelings"
)

# Update from controller
prompt.update(rt=0.7, lt=0.2, y_pressed=False, a_pressed=True)

# Get response
if prompt.is_confirmed:
    dimension, value = prompt.get_response()
    # dimension: EmotionalDimension.ENJOYMENT
    # value: 0.7

# Track state over time
state = EmotionalState()
state.record(EmotionalDimension.ENJOYMENT, 0.8, context="list_comprehensions")
state.is_in_flow()  # True if high enjoyment + low frustration
state.needs_break()  # True if frustrated or disengaged
```

### Adaptive Engine
```python
from lmsp.adaptive import AdaptiveEngine, LearnerProfile

# Create profile
profile = LearnerProfile(player_id="wings")

# Create engine
engine = AdaptiveEngine(profile)

# Record attempt
engine.observe_attempt(
    concept="list_comprehensions",
    success=True,
    time_seconds=45,
    hints_used=0
)

# Record emotion
engine.observe_emotion(EmotionalDimension.ENJOYMENT, 0.9, "list_comprehensions")

# Get recommendation
rec = engine.recommend_next()
# rec.action: "challenge" | "review" | "break" | "project_step"
# rec.concept: "lambda_functions"
# rec.reason: "This brings you closer to: Discord bot"

# Save/load
engine.save(Path("profile.json"))
engine = AdaptiveEngine.load(Path("profile.json"))
```

### Player-Zero
```python
from player_zero import ClaudePlayer, HumanPlayer, CoopSession

# Create players
human = HumanPlayer(name="Wings", input_device="gamepad")
claude = ClaudePlayer(name="Lief", style="encouraging", skill_level=0.7)

# Start session
session = CoopSession(players=[human, claude])
session.set_challenge("container_add_exists")
await session.start()

# TAS features
from player_zero.tas import Recorder, Checkpoint

recorder = Recorder()
recorder.start()
# ... play ...
recording = recorder.stop()

checkpoint = Checkpoint.create("before_bug")
session.rewind(steps=5)
diff = Checkpoint.diff("before_bug", "after_fix")
```

---

## APPENDIX C: DEVELOPMENT COMMANDS

```bash
# Setup
cd /mnt/castle/garage/learn-me-some-py
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Development with Palace
pal next -t --claude      # Iterative development
pal test                  # Run tests
pal build                 # Build project

# Testing
pytest tests/ -v          # Run all tests
pytest tests/test_emotional.py -v  # Specific test file
pytest --cov=lmsp --cov-report=html  # Coverage report

# Running
python -m lmsp            # Start game
python -m lmsp --input gamepad  # With controller
python -m lmsp --player-zero    # With AI player
python -m lmsp --multiplayer --mode coop  # Multiplayer

# Player-Zero
cd /mnt/castle/garage/player-zero
python -m player_zero spawn --players 4 --mode swarm
python -m player_zero replay recording.json --speed 2.0
```

---

## CLOSING THOUGHTS

LMSP is not just a Python tutorial. It's:

1. **A learning relationship** - The AI knows YOU
2. **A game** - Fun is the primary metric
3. **A platform** - Extensible for any subject
4. **A meta-game** - Building it teaches it
5. **A community** - Learners become contributors
6. **A research project** - Exploring adaptive education

The goal: **Master Python in an hour** (for the right brain, with the right system).

The method: **Make learning indistinguishable from playing**.

The outcome: **A generation of programmers who learned through joy**.

---

*Built in The Forge. Powered by Palace. For the love of learning.*

🔥🎮📚
