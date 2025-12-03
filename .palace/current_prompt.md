# Palace Request
Analyze this project and suggest possible next actions.

USER GUIDANCE: # LMSP MEGA-REORGANIZATION - 20-Agent Swarm Execution

## MISSION
Transform 5,417 lines of ULTRASPEC into a progressive disclosure documentation structure AND scaffold the complete codebase for parallel development. This is a MASSIVE parallelization task designed for 20 agents, each spawning subagents.

## SOURCE FILES
- `/mnt/castle/garage/learn-me-some-py/ULTRASPEC.md` (1,542 lines)
- `/mnt/castle/garage/learn-me-some-py/ULTRASPEC-ALT.md` (3,875 lines)
- `/mnt/castle/garage/learn-me-some-py/lmsp/` (existing scaffold)
- `/mnt/castle/garage/player-zero/` (existing scaffold)

## EXECUTION MODEL
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    20-AGENT SWARM + SUBAGENTS                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  DOCUMENTATION AGENTS (1-8)           CODE AGENTS (9-16)                   │
│  ┌─────┬─────┬─────┬─────┐           ┌─────┬─────┬─────┬─────┐            │
│  │  1  │  2  │  3  │  4  │           │  9  │ 10  │ 11  │ 12  │            │
│  │ vis │arch │core │input│           │game │adpt │inpt │prog │            │
│  └──┬──┴──┬──┴──┬──┴──┬──┘           └──┬──┴──┬──┴──┬──┴──┬──┘            │
│     │     │     │     │                 │     │     │     │               │
│  ┌─────┬─────┬─────┬─────┐           ┌─────┬─────┬─────┬─────┐            │
│  │  5  │  6  │  7  │  8  │           │ 13  │ 14  │ 15  │ 16  │            │
│  │mult │ tas │intr │ ref │           │mult │ p-0 │test │intg │            │
│  └─────┴─────┴─────┴─────┘           └─────┴─────┴─────┴─────┘            │
│                                                                             │
│  ORCHESTRATION AGENTS (17-20)                                              │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐                │
│  │     17      │     18      │     19      │     20      │                │
│  │  validate   │   merge     │  cross-ref  │   final     │                │
│  └─────────────┴─────────────┴─────────────┴─────────────┘                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## AGENT 1: Vision & Philosophy Documentation
**Model:** sonnet (fast, good at synthesis)
**Spawn subagents:** YES - 2 subagents

### Primary Tasks:
1. Create `docs/00-VISION.md`
   - Extract philosophy from both ULTRASPECs
   - The Rocksmith insight
   - "Fun is the metric" philosophy
   - Why existing education fails
   - Target: 200-400 lines

2. Create `docs/01-QUICKSTART.md`
   - 5-minute setup guide
   - First challenge walkthrough
   - "Hello World" of LMSP
   - Target: 150-250 lines

### Subagent Tasks:
- **Subagent 1A:** Extract ALL philosophy quotes and insights from ULTRASPEC-ALT Part I
- **Subagent 1B:** Extract setup/quickstart content from both specs, merge

### Output Files:
```
docs/00-VISION.md
docs/01-QUICKSTART.md
```

---

## AGENT 2: Architecture Documentation
**Model:** sonnet
**Spawn subagents:** YES - 3 subagents

### Primary Tasks:
1. Create `docs/10-ARCHITECTURE.md`
   - Three systems diagram (preserve ASCII)
   - Data flow between systems
   - Stream-JSON overview
   - Target: 300-500 lines

2. Create `docs/11-LMSP-OVERVIEW.md`
   - Game structure
   - File layout
   - Module responsibilities
   - Target: 200-350 lines

3. Create `docs/12-PLAYER-ZERO-OVERVIEW.md`
   - Framework purpose
   - Universal app automation vision
   - Playwright connection
   - Target: 250-400 lines

4. Create `docs/13-PALACE-INTEGRATION.md`
   - TDD enforcement
   - RHSI loops
   - Mask system for LMSP
   - Target: 150-250 lines

### Subagent Tasks:
- **Subagent 2A:** Extract and merge ALL architecture diagrams from both specs
- **Subagent 2B:** Extract LMSP file structure details, expand with explanations
- **Subagent 2C:** Extract player-zero structure and capabilities

### Output Files:
```
docs/10-ARCHITECTURE.md
docs/11-LMSP-OVERVIEW.md
docs/12-PLAYER-ZERO-OVERVIEW.md
docs/13-PALACE-INTEGRATION.md
```

---

## AGENT 3: Core Systems Documentation
**Model:** sonnet
**Spawn subagents:** YES - 4 subagents

### Primary Tasks:
1. Create `docs/20-ADAPTIVE-ENGINE.md`
   - LearnerProfile structure
   - Recommendation engine
   - Spaced repetition algorithm
   - Fun tracking
   - Weakness detection
   - Project-driven curriculum
   - ALL code examples from specs
   - Target: 500-800 lines

2. Create `docs/21-EMOTIONAL-INPUT.md`
   - EmotionalSample/State/Prompt classes
   - Trigger-based feedback
   - Flow state detection
   - Integration with adaptive engine
   - Target: 300-450 lines

3. Create `docs/22-CONCEPT-DAG.md`
   - Full concept graph (all 6 levels)
   - Prerequisite relationships
   - Unlock conditions
   - Mastery levels (0-4)
   - Dynamic registration
   - Target: 400-600 lines

4. Create `docs/23-CHALLENGE-SYSTEM.md`
   - Challenge TOML format
   - Test case structure
   - Hint levels
   - Emotional checkpoints
   - Speed run targets
   - Target: 300-450 lines

### Subagent Tasks:
- **Subagent 3A:** Extract ALL adaptive engine code from both specs
- **Subagent 3B:** Extract emotional input system details + code
- **Subagent 3C:** Build complete concept DAG from both specs (merge Level definitions)
- **Subagent 3D:** Extract challenge system details, create comprehensive TOML examples

### Output Files:
```
docs/20-ADAPTIVE-ENGINE.md
docs/21-EMOTIONAL-INPUT.md
docs/22-CONCEPT-DAG.md
docs/23-CHALLENGE-SYSTEM.md
```

---

## AGENT 4: Input Systems Documentation
**Model:** sonnet
**Spawn subagents:** YES - 4 subagents

### Primary Tasks:
1. Create `docs/30-RADIAL-TYPING.md`
   - Full chord mapping system
   - Character frequency optimization
   - Visual feedback system
   - Learning curve progression
   - ALL ASCII diagrams
   - Target: 600-900 lines (this is comprehensive in ULTRASPEC-ALT)

2. Create `docs/31-EASY-MODE.md`
   - Button mapping table
   - Python verb shortcuts
   - Contextual smart-complete
   - Progression from easy to radial
   - Target: 250-400 lines

3. Create `docs/32-HAPTIC-FEEDBACK.md`
   - Vibration patterns
   - Feedback for different events
   - Controller-specific notes
   - Target: 150-250 lines

4. Create `docs/33-MULTI-INPUT.md`
   - Touchscreen mode
   - Keyboard fallback
   - Input abstraction layer
   - Target: 200-300 lines

### Subagent Tasks:
- **Subagent 4A:** Extract COMPLETE radial typing system from ULTRASPEC-ALT (it has the most detail)
- **Subagent 4B:** Extract easy mode mappings and create visual tables
- **Subagent 4C:** Extract haptic feedback patterns
- **Subagent 4D:** Design multi-input abstraction (less in specs, more design needed)

### Output Files:
```
docs/30-RADIAL-TYPING.md
docs/31-EASY-MODE.md
docs/32-HAPTIC-FEEDBACK.md
docs/33-MULTI-INPUT.md
```

---

## AGENT 5: Multiplayer Documentation
**Model:** sonnet
**Spawn subagents:** YES - 4 subagents

### Primary Tasks:
1. Create `docs/40-SESSION-MODES.md`
   - COOP mode (shared cursor)
   - RACE mode (competitive)
   - TEACH mode (one teaches)
   - SWARM mode (parallel AI)
   - SPECTATOR mode
   - ASCII diagrams for each
   - Target: 500-700 lines

2. Create `docs/41-STREAM-JSON.md`
   - The 18-line magic (_forward_to_other_agents)
   - Event types
   - Protocol specification
   - Palace pattern adaptation
   - Target: 300-450 lines

3. Create `docs/42-CLAUDE-PLAYER.md`
   - ClaudePlayer implementation
   - Teaching style configuration
   - Skill level calibration
   - Multi-Claude coordination
   - Target: 250-400 lines

4. Create `docs/43-TAS-SYSTEM.md`
   - Recording system
   - Replay system
   - Checkpoint/rewind
   - Diff system
   - Target: 350-500 lines

### Subagent Tasks:
- **Subagent 5A:** Extract all session mode descriptions and ASCII diagrams
- **Subagent 5B:** Extract stream-JSON protocol details, map to Palace patterns
- **Subagent 5C:** Extract Claude player specs
- **Subagent 5D:** Extract TAS system code and specifications

### Output Files:
```
docs/40-SESSION-MODES.md
docs/41-STREAM-JSON.md
docs/42-CLAUDE-PLAYER.md
docs/43-TAS-SYSTEM.md
```

---

## AGENT 6: TAS Deep Dive Documentation
**Model:** sonnet
**Spawn subagents:** YES - 3 subagents

### Primary Tasks:
1. Create `docs/44-RECORDING-FORMAT.md`
   - RecordedEvent structure
   - Game state serialization
   - Compression strategies
   - Target: 200-350 lines

2. Create `docs/45-REPLAY-ANALYSIS.md`
   - Speedrun comparison
   - Approach analysis
   - Learning from recordings
   - Target: 250-400 lines

3. Create `docs/46-CHECKPOINT-SYSTEM.md`
   - Named checkpoints
   - State restoration
   - Diff generation
   - Target: 200-300 lines

### Subagent Tasks:
- **Subagent 6A:** Extract recording format details
- **Subagent 6B:** Extract replay/analysis patterns
- **Subagent 6C:** Extract checkpoint system code

### Output Files:
```
docs/44-RECORDING-FORMAT.md
docs/45-REPLAY-ANALYSIS.md
docs/46-CHECKPOINT-SYSTEM.md
```

---

## AGENT 7: Introspection Documentation
**Model:** sonnet
**Spawn subagents:** YES - 3 subagents

### Primary Tasks:
1. Create `docs/50-SCREENSHOT-WIREFRAME.md`
   - ScreenshotBundle structure
   - Wireframe metadata
   - AST capture
   - Game state in wireframe
   - Target: 300-450 lines

2. Create `docs/51-VIDEO-MOSAIC.md`
   - MosaicRecorder implementation
   - Frame selection strategies
   - Grid composition
   - Claude vision optimization
   - Target: 250-400 lines

3. Create `docs/52-DISCOVERY-PRIMITIVES.md`
   - All primitives by level
   - Unlock conditions
   - Usage examples
   - Progressive disclosure of tools
   - Target: 300-450 lines

### Subagent Tasks:
- **Subagent 7A:** Extract screenshot/wireframe code and specs
- **Subagent 7B:** Extract video mosaic system
- **Subagent 7C:** Build complete primitives reference

### Output Files:
```
docs/50-SCREENSHOT-WIREFRAME.md
docs/51-VIDEO-MOSAIC.md
docs/52-DISCOVERY-PRIMITIVES.md
```

---

## AGENT 8: Reference Documentation
**Model:** sonnet
**Spawn subagents:** YES - 4 subagents

### Primary Tasks:
1. Create `docs/60-TOML-SCHEMAS.md`
   - Complete Concept TOML schema
   - Complete Challenge TOML schema
   - Validation rules
   - Example files
   - Target: 400-600 lines

2. Create `docs/61-API-REFERENCE.md`
   - All public classes
   - All public methods
   - Type signatures
   - Usage examples
   - Target: 500-800 lines

3. Create `docs/62-IMPLEMENTATION-PHASES.md`
   - Phase 1-6 breakdown
   - Dependencies between phases
   - Task checklist format
   - Target: 300-450 lines

4. Create `docs/63-SUCCESS-METRICS.md`
   - Learning efficacy metrics
   - Engagement metrics
   - Controller adoption metrics
   - Platform metrics
   - Target: 200-300 lines

### Subagent Tasks:
- **Subagent 8A:** Extract and expand TOML schemas with full documentation
- **Subagent 8B:** Build comprehensive API reference from code + specs
- **Subagent 8C:** Extract implementation phases, convert to actionable checklist
- **Subagent 8D:** Extract success metrics, add measurement strategies

### Output Files:
```
docs/60-TOML-SCHEMAS.md
docs/61-API-REFERENCE.md
docs/62-IMPLEMENTATION-PHASES.md
docs/63-SUCCESS-METRICS.md
```

---

## AGENT 9: Game Engine Code
**Model:** opus (complex code generation)
**Spawn subagents:** YES - 3 subagents

### Primary Tasks:
1. Implement `lmsp/game/engine.py`
   - Core game loop
   - State management
   - Event dispatch
   - TDD: Write tests first in `tests/test_engine.py`

2. Implement `lmsp/game/state.py`
   - GameState class
   - Serialization
   - State transitions

3. Implement `lmsp/game/renderer.py`
   - TUI rendering with Rich/Textual
   - Radial menu display
   - Challenge display

### Subagent Tasks:
- **Subagent 9A:** Write comprehensive tests for game engine
- **Subagent 9B:** Implement state management
- **Subagent 9C:** Implement renderer

### Output Files:
```
lmsp/game/engine.py
lmsp/game/state.py
lmsp/game/renderer.py
tests/test_engine.py
tests/test_state.py
tests/test_renderer.py
```

---

## AGENT 10: Adaptive Engine Code
**Model:** opus
**Spawn subagents:** YES - 4 subagents

### Primary Tasks:
1. Expand `lmsp/adaptive/engine.py` (already scaffolded)
   - Add missing methods
   - Full implementation per spec

2. Implement `lmsp/adaptive/spaced.py`
   - SpacedRepetitionScheduler
   - Anki-style intervals

3. Implement `lmsp/adaptive/fun.py`
   - FunTracker class
   - Pattern analysis

4. Implement `lmsp/adaptive/weakness.py`
   - WeaknessDetector
   - Scaffolding recommendations

5. Implement `lmsp/adaptive/project.py`
   - ProjectCurriculumGenerator
   - Claude integration for goal analysis

### Subagent Tasks:
- **Subagent 10A:** Implement spaced repetition with tests
- **Subagent 10B:** Implement fun tracking with tests
- **Subagent 10C:** Implement weakness detection with tests
- **Subagent 10D:** Implement project curriculum generator with tests

### Output Files:
```
lmsp/adaptive/spaced.py
lmsp/adaptive/fun.py
lmsp/adaptive/weakness.py
lmsp/adaptive/project.py
tests/test_spaced.py
tests/test_fun.py
tests/test_weakness.py
tests/test_project.py
```

---

## AGENT 11: Input Systems Code
**Model:** opus
**Spawn subagents:** YES - 4 subagents

### Primary Tasks:
1. Implement `lmsp/input/gamepad.py`
   - pygame controller integration
   - Event normalization
   - Deadzone handling

2. Implement `lmsp/input/radial.py`
   - RadialTypingSystem class
   - Chord mapping
   - Visual overlay generation

3. Implement `lmsp/input/touch.py`
   - Touchscreen input handling
   - Gesture recognition

4. Implement `lmsp/input/keyboard.py`
   - Keyboard fallback
   - Key mapping

### Subagent Tasks:
- **Subagent 11A:** Implement gamepad with tests
- **Subagent 11B:** Implement radial typing with tests (COMPLEX - may need sub-subagents)
- **Subagent 11C:** Implement touch with tests
- **Subagent 11D:** Implement keyboard with tests

### Output Files:
```
lmsp/input/gamepad.py
lmsp/input/radial.py
lmsp/input/touch.py
lmsp/input/keyboard.py
tests/test_gamepad.py
tests/test_radial.py
tests/test_touch.py
tests/test_keyboard.py
```

---

## AGENT 12: Progression System Code
**Model:** opus
**Spawn subagents:** YES - 4 subagents

### Primary Tasks:
1. Implement `lmsp/progression/tree.py`
   - ConceptDAG class
   - networkx integration
   - Topological operations

2. Implement `lmsp/progression/unlock.py`
   - Unlock condition evaluation
   - Prerequisite checking

3. Implement `lmsp/progression/xp.py`
   - Experience point system
   - Level calculations

4. Implement `lmsp/progression/mastery.py`
   - Mastery level tracking (0-4)
   - Transcendence conditions

### Subagent Tasks:
- **Subagent 12A:** Implement DAG with tests
- **Subagent 12B:** Implement unlock system with tests
- **Subagent 12C:** Implement XP system with tests
- **Subagent 12D:** Implement mastery tracking with tests

### Output Files:
```
lmsp/progression/tree.py
lmsp/progression/unlock.py
lmsp/progression/xp.py
lmsp/progression/mastery.py
tests/test_tree.py
tests/test_unlock.py
tests/test_xp.py
tests/test_mastery.py
```

---

## AGENT 13: Multiplayer Code
**Model:** opus
**Spawn subagents:** YES - 4 subagents

### Primary Tasks:
1. Implement `lmsp/multiplayer/session.py`
   - BaseSession class
   - Session lifecycle

2. Implement `lmsp/multiplayer/sync.py`
   - State synchronization
   - Conflict resolution

3. Implement `lmsp/multiplayer/modes/coop.py`
   - CoopSession implementation

4. Implement `lmsp/multiplayer/modes/race.py`
   - RaceSession implementation

5. Implement `lmsp/multiplayer/modes/teach.py`
   - TeachSession implementation

6. Implement `lmsp/multiplayer/modes/swarm.py`
   - SwarmSession implementation

### Subagent Tasks:
- **Subagent 13A:** Implement session base + sync with tests
- **Subagent 13B:** Implement coop mode with tests
- **Subagent 13C:** Implement race mode with tests
- **Subagent 13D:** Implement teach + swarm modes with tests

### Output Files:
```
lmsp/multiplayer/session.py
lmsp/multiplayer/sync.py
lmsp/multiplayer/modes/__init__.py
lmsp/multiplayer/modes/coop.py
lmsp/multiplayer/modes/race.py
lmsp/multiplayer/modes/teach.py
lmsp/multiplayer/modes/swarm.py
tests/test_session.py
tests/test_sync.py
tests/test_modes.py
```

---

## AGENT 14: Player-Zero Core
**Model:** opus
**Spawn subagents:** YES - 4 subagents

### Primary Tasks:
1. Implement `player_zero/player/base.py`
   - Player protocol/trait
   - Common interface

2. Implement `player_zero/player/claude.py`
   - ClaudePlayer implementation
   - MCP integration

3. Implement `player_zero/player/human.py`
   - HumanPlayer adapter

4. Implement `player_zero/stream/json.py`
   - Stream-JSON protocol
   - The 18-line magic

5. Implement `player_zero/stream/broadcast.py`
   - Multi-player broadcast

### Subagent Tasks:
- **Subagent 14A:** Implement player base + human with tests
- **Subagent 14B:** Implement Claude player with tests
- **Subagent 14C:** Implement stream-JSON with tests
- **Subagent 14D:** Implement broadcast with tests

### Output Files:
```
player_zero/player/base.py
player_zero/player/claude.py
player_zero/player/human.py
player_zero/stream/json.py
player_zero/stream/broadcast.py
player_zero/stream/sync.py
tests/test_player.py
tests/test_stream.py
```

---

## AGENT 15: Test Infrastructure
**Model:** sonnet (good at systematic coverage)
**Spawn subagents:** YES - 4 subagents

### Primary Tasks:
1. Create `tests/conftest.py`
   - Shared fixtures
   - Mock controllers
   - Test utilities

2. Create `tests/fixtures/` directory
   - Sample concepts (TOML)
   - Sample challenges (TOML)
   - Sample recordings
   - Sample profiles

3. Create integration test framework
   - `tests/integration/test_game_loop.py`
   - `tests/integration/test_adaptive_flow.py`
   - `tests/integration/test_multiplayer.py`

4. Create benchmark tests
   - `tests/benchmarks/test_performance.py`

### Subagent Tasks:
- **Subagent 15A:** Create conftest and shared fixtures
- **Subagent 15B:** Create sample TOML fixtures (concepts + challenges)
- **Subagent 15C:** Create integration tests
- **Subagent 15D:** Create benchmark tests

### Output Files:
```
tests/conftest.py
tests/fixtures/concepts/*.toml
tests/fixtures/challenges/*.toml
tests/fixtures/profiles/*.json
tests/integration/test_game_loop.py
tests/integration/test_adaptive_flow.py
tests/integration/test_multiplayer.py
tests/benchmarks/test_performance.py
```

---

## AGENT 16: Integration & Glue Code
**Model:** opus
**Spawn subagents:** YES - 3 subagents

### Primary Tasks:
1. Implement `lmsp/main.py`
   - CLI entry point
   - Argument parsing
   - Mode selection

2. Implement `lmsp/python/concepts.py`
   - TOML concept loader
   - Concept registry

3. Implement `lmsp/python/challenges.py`
   - TOML challenge loader
   - Challenge runner

4. Implement `lmsp/python/validator.py`
   - Python code execution
   - Test case validation
   - Sandboxed execution

### Subagent Tasks:
- **Subagent 16A:** Implement main + CLI with tests
- **Subagent 16B:** Implement concept/challenge loaders with tests
- **Subagent 16C:** Implement validator with sandboxing with tests

### Output Files:
```
lmsp/main.py
lmsp/python/concepts.py
lmsp/python/challenges.py
lmsp/python/validator.py
tests/test_main.py
tests/test_concepts.py
tests/test_challenges.py
tests/test_validator.py
```

---

## AGENT 17: Validation Agent
**Model:** sonnet
**Spawn subagents:** YES - 2 subagents

### Primary Tasks:
1. Validate all documentation
   - Check cross-references
   - Verify no content lost from specs
   - Check prerequisites/next headers

2. Validate all code
   - Run full test suite
   - Check import consistency
   - Verify TDD compliance

3. Generate validation report

### Subagent Tasks:
- **Subagent 17A:** Documentation validation
- **Subagent 17B:** Code validation

### Output Files:
```
reports/validation-report.md
```

---

## AGENT 18: Merge Agent
**Model:** sonnet
**Spawn subagents:** NO

### Primary Tasks:
1. Merge duplicate content if any
2. Resolve conflicts between agents
3. Ensure consistent formatting
4. Update all cross-references

### Output Files:
```
(modifications to existing files)
```

---

## AGENT 19: Cross-Reference Agent
**Model:** sonnet
**Spawn subagents:** YES - 2 subagents

### Primary Tasks:
1. Build link graph of all docs
2. Add missing cross-references
3. Create `docs/INDEX.md` with full map
4. Create `docs/READING-ORDER.md`

### Subagent Tasks:
- **Subagent 19A:** Build link graph, identify missing links
- **Subagent 19B:** Create index and reading order

### Output Files:
```
docs/INDEX.md
docs/READING-ORDER.md
```

---

## AGENT 20: Final Assembly Agent
**Model:** opus
**Spawn subagents:** NO

### Primary Tasks:
1. Final integration test
2. Update root README.md with new structure
3. Update CLAUDE.md with new structure
4. Create `.palace/DEVELOPMENT-READY.md` marker
5. Generate final report

### Output Files:
```
README.md (updated)
CLAUDE.md (updated)
.palace/DEVELOPMENT-READY.md
reports/final-assembly-report.md
```

---

## EXECUTION ORDER

### Phase 1: Documentation (Agents 1-8) - PARALLEL
All documentation agents run simultaneously. No dependencies.

### Phase 2: Core Code (Agents 9-12) - PARALLEL
Game, Adaptive, Input, Progression - run simultaneously.

### Phase 3: Integration Code (Agents 13-16) - PARALLEL
Multiplayer, Player-Zero, Tests, Glue - run simultaneously.
Wait for Phase 2 completion.

### Phase 4: Finalization (Agents 17-20) - SEQUENTIAL
17 → 18 → 19 → 20
Each depends on previous.

---

## GLOBAL RULES

1. **TDD MANDATORY** - Every code file needs tests FIRST
2. **PRESERVE ASCII** - All diagrams from specs must survive
3. **SELF-CONTAINED** - Each doc readable alone
4. **CODE EXAMPLES** - Include all code from specs
5. **VOICE** - Fun, direct, technical but not dry
6. **NO DUPLICATION** - Content in exactly one place
7. **SUBAGENTS** - Use them liberally for parallelization

---

## SUCCESS CRITERIA

```
□ 24 documentation files created
□ ~40 Python files created
□ ~50 test files created
□ All tests passing
□ No content lost from specs
□ Cross-references valid
□ Reading order defined
□ Development ready marker created
```

---

## ESTIMATED OUTPUT

- **Documentation:** ~8,000-12,000 lines
- **Code:** ~6,000-10,000 lines
- **Tests:** ~4,000-6,000 lines
- **Total:** ~18,000-28,000 lines

From 5,417 lines of spec to ~20,000+ lines of implementation-ready project.

---

*Let the swarm begin.* 🐝

Focus your suggestions on what the user has asked for above.
Check SPEC.md and ROADMAP.md if they exist for context.

Provide as many options as you see fit - there may be many valid paths forward.
Be concrete and actionable. The user will select which action(s) to execute.

## Project Context
```json
{
  "project_root": "/mnt/castle/garage/learn-me-some-py",
  "palace_version": "0.1.0",
  "files": {
    "README.md": {
      "exists": true,
      "size": 6106
    },
    "Cargo.toml": {
      "exists": true,
      "size": 1284
    }
  },
  "git_status": "?? .palace/current_prompt.md\n?? .palace/history.jsonl\n?? .palace/reorganize-docs.md\n?? .palace/skills/\n",
  "config": {
    "project_name": "learn-me-some-py",
    "project_type": "python",
    "version": "0.1.0",
    "test_framework": "pytest",
    "test_command": "pytest tests/ -v",
    "build_command": "pip install -e .",
    "lint_command": "ruff check .",
    "format_command": "ruff format .",
    "description": "The game that teaches you to build it - Learn Python with controller support and adaptive AI",
    "rhsi": {
      "enabled": true,
      "strict_mode": true,
      "masks": [
        "game-designer",
        "python-teacher",
        "accessibility-expert"
      ]
    },
    "development_priorities": [
      "tests_first",
      "adaptive_learning",
      "controller_native",
      "fun_over_completeness"
    ],
    "meta_learning": {
      "enabled": true,
      "note": "This project teaches Python BY being built in Python - every file is also a lesson"
    }
  },
  "recent_history": [
    {
      "timestamp": 1764727185.075752,
      "action": "permission_request",
      "details": {
        "request": {
          "tool_name": "Bash",
          "input": {
            "command": "ls -la /mnt/castle/garage/player-zero/ 2>&1 | head -20",
            "description": "Check player-zero directory"
          },
          "tool_use_id": "toolu_01TiEoPofWjcP14gCxy36WRU"
        }
      }
    },
    {
      "timestamp": 1764727188.9720151,
      "action": "permission_decision",
      "details": {
        "tool_name": "Bash",
        "behavior": "allow",
        "message": ""
      }
    },
    {
      "timestamp": 1764727232.64102,
      "action": "next",
      "details": {
        "session_id": "pal-17b509",
        "iteration": 1,
        "exit_code": 0,
        "selected_actions": [
          "Full Swarm Execution: All 20 Agents in 4 Phases"
        ]
      }
    }
  ]
}
```

## Instructions
You are operating within Palace, a self-improving Claude wrapper.
Use all your available tools to complete this task.
When done, you can call Palace commands via bash if needed.
