# Implementation Phases

Detailed phase-by-phase implementation roadmap for LMSP.

---

## Overview

LMSP development is organized into six phases over 12 weeks:

```
Phase 1: MVP              (Week 1-2)  ✅ Foundation
Phase 2: Controller       (Week 3-4)  🎮 Feel like a game
Phase 3: Adaptive         (Week 5-6)  🧠 Learn the learner
Phase 4: Multiplayer      (Week 7-8)  👥 Play together
Phase 5: Introspection    (Week 9-10) 🔍 Deep analysis
Phase 6: Polish          (Week 11-12) ✨ Beautiful & complete
```

Each phase builds on the previous, with clear milestones and deliverables.

---

## Phase 1: MVP (Week 1-2)

**Goal:** Get something working - basic learning loop with keyboard input.

**Priority:** Core functionality, keyboard-only, essential features.

### Checklist

#### Project Structure
- [x] Create directory structure (`lmsp/`, `concepts/`, `challenges/`, `tests/`, `assets/`)
- [x] Set up `pyproject.toml` with dependencies
- [x] Configure Palace integration (`.palace/config.json`)
- [x] Create `CLAUDE.md` with project guidelines
- [x] Write comprehensive `README.md`
- [x] Write `ULTRASPEC.md` complete specification

#### Core Modules

**Emotional Input** (`lmsp/input/emotional.py`)
- [x] `EmotionalDimension` enum
- [x] `EmotionalPrompt` class with render/update/get_response
- [x] `EmotionalState` class with history tracking
- [x] Flow state detection (`is_in_flow()`)
- [x] Break detection (`needs_break()`)
- [x] Tests in `tests/test_emotional.py`

**Adaptive Engine** (`lmsp/adaptive/engine.py`)
- [x] `AttemptRecord` dataclass
- [x] `LearnerProfile` class with mastery tracking
- [x] `Recommendation` dataclass
- [x] `AdaptiveEngine` with observe/recommend
- [x] Save/load profile to JSON
- [x] Tests in `tests/test_adaptive.py`

**Concept System** (`lmsp/python/concepts.py`)
- [ ] `Concept` dataclass
- [ ] `load_concept()` function (TOML → Concept)
- [ ] `load_all_concepts()` function
- [ ] `ConceptRegistry` with DAG management
- [ ] `get_unlockable()` based on mastery
- [ ] Topological sort for learning paths
- [ ] Tests in `tests/test_concepts.py`

**Challenge System** (`lmsp/python/challenges.py`)
- [ ] `Challenge` dataclass
- [ ] `TestCase` dataclass
- [ ] `load_challenge()` function (TOML → Challenge)
- [ ] `load_all_challenges()` function
- [ ] Tests in `tests/test_challenges.py`

**Validation System** (`lmsp/python/validator.py`)
- [ ] `ValidationResult` dataclass
- [ ] `validate_solution()` function
- [ ] Safe Python execution in sandbox
- [ ] Test case comparison (expected vs actual)
- [ ] Detailed error reporting
- [ ] Tests in `tests/test_validator.py`

**Game Loop** (`lmsp/game/engine.py`)
- [ ] `GameState` dataclass
- [ ] `GameEngine` class
- [ ] Main loop: recommend → select → challenge → validate → feedback
- [ ] Integration with adaptive engine
- [ ] Integration with emotional input
- [ ] Tests in `tests/test_engine.py`

#### UI/UX

**TUI (Text User Interface)** (`lmsp/game/renderer.py`)
- [ ] Rich/Textual setup
- [ ] Challenge display (description, skeleton, tests)
- [ ] Code editor widget (syntax highlighting)
- [ ] Test result display
- [ ] Emotional prompt rendering
- [ ] Concept selection menu
- [ ] Tests in `tests/test_renderer.py`

**Keyboard Input** (`lmsp/input/keyboard.py`)
- [ ] Text input handling
- [ ] Arrow key navigation
- [ ] Keyboard shortcuts (Ctrl+R = run, Ctrl+H = hint)
- [ ] Tests in `tests/test_keyboard.py`

#### Content

**Level 0-1 Concepts** (`concepts/level_0/`, `concepts/level_1/`)
- [x] `lists.toml` (sample concept) ✅
- [ ] `variables.toml`
- [ ] `types.toml`
- [ ] `print.toml`
- [ ] `if_else.toml`
- [ ] `for_loops.toml`
- [ ] `while_loops.toml`

**Starter Challenges** (`challenges/`)
- [x] `container_basics/add_exists.toml` ✅
- [ ] `variable_basics/*.toml` (3 challenges)
- [ ] `loop_basics/*.toml` (3 challenges)

#### Testing & CI
- [ ] `pytest` configuration
- [ ] Test coverage >80% for core modules
- [ ] Palace strict mode passing (`pal test`)
- [ ] CI/CD pipeline (GitHub Actions)

### Deliverables

- [ ] Working game: `python -m lmsp`
- [ ] Player can:
  - [ ] Select a concept
  - [ ] See a challenge
  - [ ] Write code (keyboard)
  - [ ] Run tests
  - [ ] Get feedback
  - [ ] Provide emotional response
- [ ] Adaptive engine learns from attempts
- [ ] Progress saved to disk

### Dependencies

None - this is the foundation.

### Success Criteria

- [ ] Can complete 3 challenges end-to-end
- [ ] Tests pass: `pal test`
- [ ] Profile persists across sessions
- [ ] Emotional feedback influences recommendations
- [ ] No crashes during normal use

---

## Phase 2: Controller (Week 3-4)

**Goal:** Make it feel like a game - full controller support with radial typing.

**Priority:** Gamepad input, haptic feedback, radial menus, audio cues.

### Checklist

#### Gamepad Integration

**Gamepad Input** (`lmsp/input/gamepad.py`)
- [ ] Pygame gamepad initialization
- [ ] Button mapping (A/B/X/Y, bumpers, triggers, sticks)
- [ ] Analog trigger pressure (0.0-1.0)
- [ ] Stick position reading
- [ ] Button press/hold detection
- [ ] Haptic feedback API
- [ ] Tests with virtual gamepad

**Easy Mode** (`lmsp/input/easy_mode.py`)
- [ ] Button → Python verb mapping
  - [ ] A = `def` (prompts for function name)
  - [ ] B = `return` (prompts for value)
  - [ ] X = `if` (prompts for condition)
  - [ ] Y = `for` (prompts for iterator)
- [ ] LB = Undo
- [ ] RB = Smart-complete
- [ ] LT = Dedent
- [ ] RT = Indent
- [ ] D-Pad navigation
- [ ] Interactive prompts for completing statements
- [ ] Tests in `tests/test_easy_mode.py`

**Radial Typing** (`lmsp/input/radial.py`)
- [ ] Chord mapping system (L-stick + R-stick → text)
- [ ] Layout definitions in `assets/radial_layouts/python.json`
- [ ] Common chords:
  - [ ] L-Up + R-Up = "def"
  - [ ] L-Down + R-Down = newline + auto-indent
  - [ ] L-Left + R-Right = "if "
  - [ ] L-Center + R-Center = space
- [ ] Visual radial overlay
- [ ] Chord detection (threshold tuning)
- [ ] Training mode (shows chord as you hold sticks)
- [ ] Tests in `tests/test_radial.py`

**Radial Menu** (`lmsp/input/radial_menu.py`)
- [ ] 8-direction menu overlay
- [ ] Concept selection via thumbstick
- [ ] Challenge selection
- [ ] Hint access
- [ ] Settings access
- [ ] Visual feedback (highlight selection)
- [ ] Smooth animations
- [ ] Tests in `tests/test_radial_menu.py`

#### Emotional Input Integration

**Trigger-Based Prompts** (`lmsp/input/emotional.py` - enhance)
- [ ] Real-time trigger pressure display
- [ ] Visual bar graphs in TUI
- [ ] Confirm with A button
- [ ] Y button for complex response → text input
- [ ] Haptic pulse on confirmation

#### Audio Feedback

**Sound System** (`lmsp/game/audio.py`)
- [ ] Pygame mixer setup
- [ ] Sound effect library:
  - [ ] Test pass (`assets/sounds/test_pass.wav`)
  - [ ] Test fail (`assets/sounds/test_fail.wav`)
  - [ ] Challenge complete (`assets/sounds/complete.wav`)
  - [ ] Level up (`assets/sounds/levelup.wav`)
  - [ ] Hint unlock (`assets/sounds/hint.wav`)
  - [ ] Button press (`assets/sounds/button.wav`)
- [ ] Volume control
- [ ] Mute option
- [ ] Tests in `tests/test_audio.py`

#### UI Enhancements

**Controller-Native UI** (`lmsp/game/renderer.py` - enhance)
- [ ] Button prompts (show A/B/X/Y icons)
- [ ] Radial menu overlay
- [ ] Trigger pressure visualization
- [ ] Chord hint display (training wheels)
- [ ] Controller connection status
- [ ] Vibration settings

#### Content

**Gamepad Tutorials** (add to existing concepts)
- [ ] Update all Level 0-1 concepts with `[gamepad_tutorial]` sections
- [ ] Create "Controller Basics" tutorial challenge
- [ ] Create "Radial Typing Practice" mini-game

**Easy Mode Challenges** (add to existing challenges)
- [ ] Add `[gamepad_hints]` to all starter challenges
- [ ] Create Easy Mode-specific scaffolding

#### Configuration

**Input Settings** (`lmsp/config/input.py`)
- [ ] Input mode selection: keyboard/gamepad/both
- [ ] Radial typing: enabled/disabled/training
- [ ] Easy mode: enabled/disabled
- [ ] Haptic feedback: enabled/disabled
- [ ] Audio: enabled/disabled/volume
- [ ] Persistent config file

### Deliverables

- [ ] Full gamepad support
- [ ] Radial typing works (20+ WPM after practice)
- [ ] Easy mode for absolute beginners
- [ ] Audio feedback
- [ ] Haptic feedback
- [ ] Controller-native UI

### Dependencies

- Phase 1 complete (core game loop)

### Success Criteria

- [ ] Can complete challenge using only controller
- [ ] Radial typing: 20 WPM after 1 hour practice
- [ ] Easy mode: beginners can write simple functions
- [ ] Audio/haptic enhances experience
- [ ] Controller feels responsive (<50ms latency)

---

## Phase 3: Adaptive (Week 5-6)

**Goal:** Make it learn YOU - personalized curriculum and flow detection.

**Priority:** Spaced repetition, fun tracking, weakness detection, project-driven curriculum.

### Checklist

#### Spaced Repetition

**Anki-Style Scheduler** (`lmsp/adaptive/spaced.py`)
- [ ] `SpacedRepetitionScheduler` class
- [ ] Review intervals: 1h → 1d → 3d → 7d → 14d → 30d
- [ ] Interval adjustment based on success/failure
- [ ] Difficulty multiplier per concept
- [ ] `get_due_reviews()` method
- [ ] `schedule_next_review()` method
- [ ] Tests in `tests/test_spaced.py`

#### Fun Tracking

**Engagement Patterns** (`lmsp/adaptive/fun.py`)
- [ ] `FunProfile` dataclass
- [ ] `FunTracker` class
- [ ] Pattern detection:
  - [ ] Puzzle-solving enjoyment
  - [ ] Speedrun enjoyment
  - [ ] Collection enjoyment
  - [ ] Creation enjoyment
  - [ ] Competition enjoyment
  - [ ] Mastery enjoyment
- [ ] `analyze_session()` method
- [ ] `get_preferred_fun_types()` method
- [ ] Flow trigger identification
- [ ] Tests in `tests/test_fun.py`

#### Weakness Detection

**Struggle Patterns** (`lmsp/adaptive/weakness.py`)
- [ ] `WeaknessSignal` dataclass
- [ ] `WeaknessDetector` class
- [ ] Detect genuine weakness vs bad day
- [ ] Clustering analysis (failures bunched or spread?)
- [ ] Prerequisite gap detection
- [ ] `detect_weakness()` method
- [ ] `recommend_scaffolding()` method
- [ ] Gentle resurfacing (not punishment)
- [ ] Tests in `tests/test_weakness.py`

#### Project-Driven Curriculum

**Goal-Based Learning** (`lmsp/adaptive/project.py`)
- [ ] `ProjectGoal` dataclass
- [ ] `Curriculum` dataclass
- [ ] `ProjectCurriculumGenerator` class
- [ ] Claude integration for goal analysis
- [ ] Map goal → required concepts
- [ ] Generate concept prerequisites (topological sort)
- [ ] Theme challenges around goal
- [ ] `generate_curriculum()` async method
- [ ] `theme_challenge()` method (rewrite description for context)
- [ ] Tests in `tests/test_project.py`

**Example Goals:**
- [ ] "Discord bot"
- [ ] "Data analysis with pandas"
- [ ] "Simple web scraper"
- [ ] "Text-based game"
- [ ] "Automation script"

#### Adaptive Engine Enhancements

**Enhanced Recommendation** (`lmsp/adaptive/engine.py` - enhance)
- [ ] Integration with spaced repetition
- [ ] Integration with fun tracking
- [ ] Integration with weakness detection
- [ ] Integration with project curriculum
- [ ] Priority system:
  1. [ ] Break needed?
  2. [ ] Frustration recovery
  3. [ ] Spaced repetition due
  4. [ ] Project goal step
  5. [ ] Weakness drilling
  6. [ ] Exploration
- [ ] Flow state detection → auto-advance
- [ ] Session length tracking
- [ ] Fatigue detection

#### Profile Enhancements

**Extended Profile** (`lmsp/adaptive/engine.py` - enhance `LearnerProfile`)
- [ ] `fun_profile: FunProfile`
- [ ] `project_goals: list[ProjectGoal]`
- [ ] `review_schedule: dict[str, float]` (concept → next review time)
- [ ] `flow_triggers: list[str]` (concepts that induce flow)
- [ ] `session_history: list[SessionSummary]`

#### UI Integration

**Adaptive UI** (`lmsp/game/renderer.py` - enhance)
- [ ] Display "Why this?" for recommendations
- [ ] Show progress toward project goal
- [ ] Visualize mastery levels (concept tree)
- [ ] Show review schedule
- [ ] Fun profile visualization

### Deliverables

- [ ] Spaced repetition system
- [ ] Fun tracking and flow detection
- [ ] Weakness detection and scaffolding
- [ ] Project-driven curriculum generator
- [ ] Enhanced recommendations

### Dependencies

- Phase 1 complete (core adaptive engine)
- Phase 2 nice-to-have (emotional input via triggers)

### Success Criteria

- [ ] Concepts resurface before forgetting (30-day retention)
- [ ] Flow state auto-advances 80%+ of the time
- [ ] Weakness detection identifies struggles correctly
- [ ] Project curriculum generates valid learning paths
- [ ] Recommendations feel personalized and relevant

---

## Phase 4: Multiplayer (Week 7-8)

**Goal:** Play together - AI players, COOP, RACE, TEACH modes.

**Priority:** Player-Zero framework, stream-JSON protocol, session modes.

### Checklist

#### Player-Zero Core

**Player Framework** (`/mnt/castle/garage/player-zero/player_zero/`)
- [ ] `Player` protocol/ABC
- [ ] `HumanPlayer` implementation
- [ ] `ClaudePlayer` implementation
- [ ] `CompositePlayer` for multi-agent
- [ ] Player state tracking
- [ ] Tests in `tests/test_player.py`

**Session Management** (`player_zero/session/`)
- [ ] `Session` base class
- [ ] `CoopSession` (collaborative)
- [ ] `CompetitiveSession` (race mode)
- [ ] `TeachingSession` (one teaches, others learn)
- [ ] `SpectatorSession` (watch AI with commentary)
- [ ] `SwarmSession` (N AIs, different approaches)
- [ ] Tests in `tests/test_session.py`

**Stream-JSON Protocol** (`player_zero/stream/`)
- [ ] Event types:
  - [ ] `cursor_move`
  - [ ] `keystroke`
  - [ ] `thought` (AI internal state)
  - [ ] `suggestion`
  - [ ] `emotion`
  - [ ] `test_result`
  - [ ] `completion`
- [ ] `broadcast()` to all players
- [ ] Event serialization/deserialization
- [ ] stdin/stdout streaming
- [ ] Tests in `tests/test_stream.py`

#### AI Player Implementation

**Claude Player** (`player_zero/player/claude.py`)
- [ ] Claude API integration
- [ ] Context window management
- [ ] System prompt templates:
  - [ ] "encouraging" style
  - [ ] "challenging" style
  - [ ] "analytical" style
  - [ ] "playful" style
- [ ] Skill level tuning (0.0 = beginner, 1.0 = expert)
- [ ] Action generation from game state
- [ ] Thought/suggestion generation
- [ ] Tests with mock Claude API

**Human Player** (`player_zero/player/human.py`)
- [ ] Gamepad input integration
- [ ] Keyboard input integration
- [ ] Event emission on actions
- [ ] Tests in `tests/test_human.py`

#### LMSP Integration

**Multiplayer Module** (`lmsp/multiplayer/`)
- [ ] `player_zero_adapter.py` - LMSP → Player-Zero bridge
- [ ] `session.py` - Session management for LMSP
- [ ] `sync.py` - State synchronization
- [ ] Multi-player game loop
- [ ] Split-screen rendering (for RACE mode)
- [ ] Tests in `tests/test_multiplayer.py`

#### Session Modes

**COOP Mode** (`player_zero/session/coop.py`)
- [ ] Shared code buffer
- [ ] Turn-taking or simultaneous editing
- [ ] Real-time suggestions from AI
- [ ] Shared test results
- [ ] Victory celebration (both complete)
- [ ] Tests in `tests/test_coop.py`

**RACE Mode** (`player_zero/session/competitive.py`)
- [ ] Separate code buffers
- [ ] Side-by-side display
- [ ] Live test progress
- [ ] Timer
- [ ] Winner announcement
- [ ] Post-race analysis (compare approaches)
- [ ] Tests in `tests/test_competitive.py`

**TEACH Mode** (`player_zero/session/teaching.py`)
- [ ] Teacher role (AI or human)
- [ ] Student roles (multiple)
- [ ] Q&A system
- [ ] Scaffolded hints
- [ ] Progress tracking per student
- [ ] Tests in `tests/test_teaching.py`

**SPECTATOR Mode** (`player_zero/session/spectator.py`)
- [ ] Watch AI solve challenge
- [ ] AI narrates thinking
- [ ] Pause/resume
- [ ] Speed control (1x, 2x, 5x)
- [ ] Screenshot interesting moments
- [ ] Tests in `tests/test_spectator.py`

**SWARM Mode** (`player_zero/session/swarm.py`)
- [ ] Spawn N AI players
- [ ] Different strategies/styles
- [ ] Parallel execution
- [ ] Compare solutions:
  - [ ] Speed
  - [ ] Lines of code
  - [ ] Readability
  - [ ] Approach (brute force, elegant, optimized)
- [ ] Learn from best
- [ ] Tests in `tests/test_swarm.py`

#### UI for Multiplayer

**Multi-Player Renderer** (`lmsp/game/renderer.py` - enhance)
- [ ] Split-screen mode
- [ ] Player indicators
- [ ] Chat/thought bubble display
- [ ] Live test progress for all players
- [ ] Winner announcement animations

### Deliverables

- [ ] Player-Zero framework
- [ ] LMSP multiplayer integration
- [ ] 5 session modes working
- [ ] AI players play reasonably well
- [ ] Stream-JSON protocol working

### Dependencies

- Phase 1 complete (core game)
- Phase 2 nice-to-have (controller input)

### Success Criteria

- [ ] COOP mode: complete challenge together
- [ ] RACE mode: fun competitive experience
- [ ] TEACH mode: AI explains concepts clearly
- [ ] SPECTATOR mode: learn by watching AI
- [ ] SWARM mode: see multiple approaches
- [ ] Stream-JSON: <10ms latency between players

---

## Phase 5: Introspection (Week 9-10)

**Goal:** Deep analysis - screenshots, video, TAS, wireframes.

**Priority:** Recording system, replay, rewind, debugging tools.

### Checklist

#### TAS (Tool-Assisted Learning)

**Recording System** (`lmsp/introspection/tas/record.py`)
- [ ] `RecordedEvent` dataclass
- [ ] `Recording` dataclass
- [ ] `Recorder` class
- [ ] Event recording with timestamps
- [ ] Checkpoint system
- [ ] Full game state capture
- [ ] Export to JSON
- [ ] Compression for large recordings
- [ ] Tests in `tests/test_record.py`

**Playback System** (`lmsp/introspection/tas/playback.py`)
- [ ] `Replayer` class
- [ ] `replay()` at variable speed
- [ ] `step()` single-step forward
- [ ] `rewind()` step backward
- [ ] Checkpoint restoration
- [ ] Tests in `tests/test_playback.py`

**Diff System** (`lmsp/introspection/tas/diff.py`)
- [ ] `CheckpointDiff` dataclass
- [ ] Code diff between checkpoints
- [ ] Event list between checkpoints
- [ ] Semantic diff (AST-based)
- [ ] Compare approaches (different recordings)
- [ ] Tests in `tests/test_diff.py`

**Checkpoint System** (`lmsp/introspection/tas/checkpoint.py`)
- [ ] `Checkpoint` class
- [ ] `create()` - save state
- [ ] `restore()` - load state
- [ ] `diff()` - compare states
- [ ] Named checkpoints
- [ ] Auto-checkpoints (before test run, after hint)
- [ ] Tests in `tests/test_checkpoint.py`

#### Screenshot System

**Screenshot Capture** (`lmsp/introspection/screenshot.py`)
- [ ] `Screenshot` class
- [ ] `ScreenshotBundle` dataclass (image + metadata)
- [ ] Screen capture (PIL/pygame)
- [ ] Wireframe generation
- [ ] Metadata export (JSON sidecar)
- [ ] Tests in `tests/test_screenshot.py`

**Wireframe System** (`lmsp/introspection/wireframe.py`)
- [ ] `Wireframe` dataclass
- [ ] Code state capture
- [ ] AST generation
- [ ] Game state snapshot
- [ ] Player state
- [ ] Session state
- [ ] Multiplayer state (if active)
- [ ] JSON serialization
- [ ] Tests in `tests/test_wireframe.py`

#### Video System

**Video Recording** (`lmsp/introspection/video.py`)
- [ ] `VideoRecorder` class
- [ ] Frame capture at specified FPS
- [ ] Strategic recording (not continuous)
- [ ] Frame selection (evenly distributed)
- [ ] Tests in `tests/test_video.py`

**Mosaic Generation** (`lmsp/introspection/mosaic.py`)
- [ ] `MosaicGenerator` class
- [ ] Grid composition (4x4, 6x5, etc.)
- [ ] Frame selection algorithm
- [ ] WebP export (optimized for Claude vision)
- [ ] Metadata overlay (timestamps, events)
- [ ] Tests in `tests/test_mosaic.py`

#### Discovery Primitives

**Introspection Commands** (`lmsp/introspection/primitives.py`)
- [ ] Command registry system
- [ ] Progressive unlock based on level
- [ ] Available primitives:
  - [ ] Level 0: `/help`, `/screenshot`
  - [ ] Level 1: `/checkpoint`, `/restore`
  - [ ] Level 2: `/rewind`, `/step`, `/diff`
  - [ ] Level 3: `/video`, `/mosaic`, `/wireframe`
  - [ ] Level 4: `/trace`, `/profile`, `/explain`
  - [ ] Level 5: `/discover-new`, `/teach`, `/benchmark`
- [ ] Help system
- [ ] Tests in `tests/test_primitives.py`

#### UI Integration

**Introspection UI** (`lmsp/game/renderer.py` - enhance)
- [ ] Command palette (/ to open)
- [ ] Screenshot preview
- [ ] Checkpoint list
- [ ] Replay controls (play/pause/step/rewind)
- [ ] Video mosaic viewer
- [ ] Wireframe inspector

#### Palace Skill

**LMSP Introspection Skill** (`lmsp/introspection/palace_skill.py`)
- [ ] Load screenshot + wireframe
- [ ] Analyze code + state
- [ ] Suggest improvements
- [ ] Detect bugs
- [ ] Explain code
- [ ] Skill manifest (`SKILL.md`)

### Deliverables

- [ ] Full TAS system (record/replay/rewind)
- [ ] Screenshot with wireframes
- [ ] Video mosaic generation
- [ ] Discovery primitives (20+ commands)
- [ ] Palace skill for introspection

### Dependencies

- Phase 1 complete (core game)
- Phase 4 nice-to-have (multiplayer recordings)

### Success Criteria

- [ ] Can record full session
- [ ] Can replay at any speed
- [ ] Can rewind and compare checkpoints
- [ ] Screenshots capture full context
- [ ] Video mosaics useful for Claude analysis
- [ ] Primitives progressively unlock
- [ ] Palace skill provides useful analysis

---

## Phase 6: Polish (Week 11-12)

**Goal:** Make it beautiful - themes, achievements, touchscreen, community.

**Priority:** Visual polish, accessibility, content, public launch.

### Checklist

#### Visual Themes

**Theme System** (`lmsp/game/themes.py`)
- [ ] `Theme` dataclass
- [ ] Theme loader (JSON/TOML)
- [ ] Built-in themes:
  - [ ] "Dark Mode" (default)
  - [ ] "Light Mode"
  - [ ] "Dracula"
  - [ ] "Nord"
  - [ ] "Solarized"
  - [ ] "High Contrast"
- [ ] Custom theme support
- [ ] Theme preview
- [ ] Tests in `tests/test_themes.py`

**Visual Polish** (`lmsp/game/renderer.py` - enhance)
- [ ] Smooth animations
- [ ] Particle effects (on completion, level up)
- [ ] Transitions between screens
- [ ] Loading animations
- [ ] Easter eggs (Konami code?)

#### Achievement System

**Achievements** (`lmsp/game/achievements.py`)
- [ ] `Achievement` dataclass
- [ ] `AchievementTracker` class
- [ ] Achievement definitions:
  - [ ] "First Blood" (first challenge)
  - [ ] "Speed Demon" (beat speed run target)
  - [ ] "Flow Master" (10 challenges in flow state)
  - [ ] "Controller Warrior" (complete 50 challenges with gamepad)
  - [ ] "AI Friend" (complete 10 COOP challenges)
  - [ ] "Completionist" (100% mastery)
  - [ ] "Teacher" (unlock teaching mode)
  - [ ] "Bug Hunter" (find bug in LMSP itself)
- [ ] Unlock animations
- [ ] Achievement showcase
- [ ] Tests in `tests/test_achievements.py`

#### Progress Visualization

**Stats & Graphs** (`lmsp/game/stats.py`)
- [ ] Concept tree visualization (graphviz/networkx)
- [ ] Mastery heatmap
- [ ] Session history graph
- [ ] Fun profile radar chart
- [ ] XP progress bar
- [ ] Time tracking
- [ ] Tests in `tests/test_stats.py`

#### Touchscreen Support

**Touch Input** (`lmsp/input/touch.py`)
- [ ] Touch event handling
- [ ] On-screen keyboard
- [ ] Gesture controls (swipe, pinch, tap)
- [ ] Radial menu touch adaptation
- [ ] Emotional input (sliders)
- [ ] Tests in `tests/test_touch.py`

**Mobile UI** (`lmsp/game/renderer.py` - responsive)
- [ ] Responsive layout (desktop/tablet/phone)
- [ ] Touch-friendly buttons
- [ ] Portrait/landscape modes
- [ ] Keyboard slide-up

#### Content Completion

**All Concepts** (`concepts/`)
- [ ] Complete Level 0-6 concepts (60+ concepts)
- [ ] All concepts have 3 challenges
- [ ] All concepts have gamepad tutorials
- [ ] Fun factor tuned based on testing

**Challenge Library** (`challenges/`)
- [ ] 200+ challenges
- [ ] Themed challenge sets
- [ ] Community-contributed challenges

**Project Templates** (`lmsp/adaptive/projects/`)
- [ ] 20+ project goals with themed curricula
- [ ] Discord bot
- [ ] Web scraper
- [ ] Data analysis
- [ ] Game development
- [ ] Automation scripts

#### Community Features

**Content Creation** (`lmsp/community/`)
- [ ] Create custom concepts (UI)
- [ ] Create custom challenges (UI)
- [ ] Share to community repo
- [ ] Import community content
- [ ] Rating system
- [ ] Tests in `tests/test_community.py`

**Extension API** (`lmsp/extensions/`)
- [ ] Plugin system
- [ ] Custom input devices
- [ ] Custom themes
- [ ] Custom session modes
- [ ] Hook system for events
- [ ] Documentation

#### Accessibility

**A11y Features** (`lmsp/a11y/`)
- [ ] Screen reader support (TTS)
- [ ] Colorblind modes
- [ ] Font size adjustment
- [ ] High contrast themes
- [ ] Keyboard-only navigation
- [ ] Controller-only navigation
- [ ] Audio descriptions
- [ ] Tests in `tests/test_a11y.py`

#### Documentation

**User Docs** (`docs/`)
- [ ] Quickstart guide
- [ ] Controller setup guide
- [ ] Radial typing tutorial
- [ ] FAQ
- [ ] Troubleshooting
- [ ] Community guidelines

**Developer Docs** (`docs/`)
- [ ] Architecture overview
- [ ] API reference
- [ ] TOML schemas
- [ ] Extension development
- [ ] Contributing guide

#### Launch Prep

**Polish**
- [ ] Fix all known bugs
- [ ] Optimize performance
- [ ] Test on Windows/Mac/Linux
- [ ] Test with 10+ beta testers
- [ ] Collect feedback and iterate

**Marketing**
- [ ] Demo video
- [ ] Website/landing page
- [ ] Social media presence
- [ ] Blog post
- [ ] HN/Reddit launch post

**Release**
- [ ] Package for PyPI
- [ ] Docker image
- [ ] Windows/Mac installers
- [ ] Public GitHub release
- [ ] Announce on socials

### Deliverables

- [ ] Beautiful, polished UI
- [ ] Achievement system
- [ ] Touchscreen support
- [ ] 200+ challenges
- [ ] Community content system
- [ ] Full accessibility
- [ ] Public launch

### Dependencies

- All previous phases complete

### Success Criteria

- [ ] 100+ players in first week
- [ ] >4/5 satisfaction rating
- [ ] Zero crashes in normal use
- [ ] Accessible to all input methods
- [ ] Community creates first custom content
- [ ] Positive feedback on HN/Reddit

---

## Inter-Phase Dependencies

```
Phase 1 (MVP)
    ↓
    ├─→ Phase 2 (Controller)
    │       ↓
    ├─→ Phase 3 (Adaptive)
    │       ↓
    └─→ Phase 4 (Multiplayer)
            ↓
        Phase 5 (Introspection)
            ↓
        Phase 6 (Polish)
```

**Critical Path:**
- Phase 1 must complete before any other phase
- Phase 2, 3, 4 can partially overlap after Phase 1
- Phase 5 requires Phase 1 (core game), benefits from Phase 4 (multiplayer recordings)
- Phase 6 requires all previous phases

**Parallel Work:**
- Phase 2 (controller) and Phase 3 (adaptive) can be developed in parallel
- Content creation (concepts/challenges) can happen throughout all phases

---

## Milestone Tracking

### Week 1-2 (Phase 1)
- [ ] Day 3: Core modules complete (concepts, challenges, validator)
- [ ] Day 7: Game loop working
- [ ] Day 10: TUI complete
- [ ] Day 14: 10 challenges playable end-to-end

### Week 3-4 (Phase 2)
- [ ] Day 17: Gamepad input working
- [ ] Day 21: Easy mode complete
- [ ] Day 24: Radial typing prototype
- [ ] Day 28: Audio feedback complete

### Week 5-6 (Phase 3)
- [ ] Day 31: Spaced repetition working
- [ ] Day 35: Fun tracking complete
- [ ] Day 38: Weakness detection working
- [ ] Day 42: Project curriculum generator

### Week 7-8 (Phase 4)
- [ ] Day 45: Player-Zero core complete
- [ ] Day 49: COOP mode working
- [ ] Day 52: RACE mode working
- [ ] Day 56: All session modes complete

### Week 9-10 (Phase 5)
- [ ] Day 59: TAS recording working
- [ ] Day 63: Replay/rewind complete
- [ ] Day 66: Screenshot + wireframe
- [ ] Day 70: Discovery primitives complete

### Week 11-12 (Phase 6)
- [ ] Day 73: Visual themes complete
- [ ] Day 77: Achievement system
- [ ] Day 80: Touchscreen support
- [ ] Day 84: Public launch

---

## Risk Mitigation

### Technical Risks

**Risk:** Radial typing too difficult
- **Mitigation:** Extensive testing with beta users, tunable sensitivity, training mode
- **Fallback:** Easy mode always available

**Risk:** AI players not intelligent enough
- **Mitigation:** Claude API integration, multiple skill levels, extensive testing
- **Fallback:** Disable multiplayer if not working well

**Risk:** Performance issues with TAS recording
- **Mitigation:** Compression, selective event recording, async I/O
- **Fallback:** Optional feature, can be disabled

### Schedule Risks

**Risk:** Phases take longer than estimated
- **Mitigation:** Start with MVP, iterate based on learnings
- **Fallback:** Cut non-critical features from later phases

**Risk:** Scope creep
- **Mitigation:** Strict phase boundaries, prioritize ruthlessly
- **Fallback:** Move features to post-launch backlog

---

*Disciplined phasing ensures steady progress toward a complete, polished learning platform.*
