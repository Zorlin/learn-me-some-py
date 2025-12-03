# LMSP - Claude Code Integration

## Ecosystem Paths

**This project is part of the LMSP ecosystem:**

```
/mnt/castle/garage/learn-me-some-py/   # This repo - The game
/mnt/castle/garage/player-zero/         # AI player simulation framework
/mnt/castle/garage/palace-public/       # Palace - RHSI engine (reference)
```

When working on LMSP, you should be aware of player-zero's capabilities and architecture. Read `/mnt/castle/garage/player-zero/README.md` for the multiplayer/TAS integration patterns.

The full technical specification is in `/mnt/castle/garage/learn-me-some-py/ULTRASPEC.md`.

---

## The Meta-Game

**This project is its own test case.**

LMSP teaches Python by having learners BUILD LMSP. Every file is both:
1. Part of the game
2. A lesson in the concept it implements

When working on this codebase:
- **Read the self-teaching comments** at the bottom of each file
- **Understand the prerequisite concepts** before modifying advanced files
- **Write tests first** (TDD is mandatory)

## Project Structure

```
learn-me-some-py/
├── lmsp/                     # Main package
│   ├── game/                 # Core game loop (Level 3+: classes)
│   ├── input/                # Controller handling (Level 2+: collections)
│   │   └── emotional.py      # Analog emotional input (Level 5: dataclasses)
│   ├── python/               # Concept & challenge system
│   ├── progression/          # Skill tree, XP (Level 4: DAGs)
│   ├── adaptive/             # AI learning engine (Level 5+: complex classes)
│   ├── multiplayer/          # player-zero integration
│   └── introspection/        # Screenshot, video, TAS features
├── concepts/                 # TOML definitions (no code)
├── challenges/               # Challenge definitions (TOML)
├── tests/                    # pytest tests (MUST exist before code)
└── assets/                   # Non-code resources
```

## Virtual Environment

**Use `.venv` - this is the ONLY venv for this project.**

```bash
cd /mnt/castle/garage/learn-me-some-py
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Run the game
python -m lmsp

# Run tests
pytest tests/ -v
```

All swarm agents should use `.venv`. Do NOT create `venv/` or other virtual environments.

---

## Development with Palace

### Quick Iteration
```bash
cd /mnt/castle/garage/learn-me-some-py
pal next -t --claude
```

This will:
1. Analyze project state
2. Suggest next action
3. Execute with Claude
4. Validate tests pass

### Strict Mode (Default)
- Tests MUST pass before completing any session
- Use `--yolo` only for exploration
- Every feature needs tests FIRST

### Using Masks
```bash
pal next --mask game-designer  # For game mechanics
pal next --mask python-teacher # For educational content
pal next --mask accessibility-expert # For controller/input UX
```

## Key Concepts

### Adaptive Learning Engine (`lmsp/adaptive/`)

The brain that learns the player's brain:
- **Spaced repetition** - Anki-style scheduling
- **Fun tracking** - Detects engagement patterns
- **Weakness drilling** - Gently resurfaces struggles
- **Project-driven** - Curriculum generated from goals

### Emotional Input (`lmsp/input/emotional.py`)

Analog triggers for emotional feedback:
- RT: Positive (enjoyment, satisfaction)
- LT: Negative (frustration, confusion)
- Y: Complex response (opens text/selection)

### Progressive Disclosure

Concepts unlock based on prerequisites (DAG, not linear):
- Level 0-2: Basics learners can understand
- Level 3-4: Intermediate patterns
- Level 5-6: Advanced (building game features)

## Self-Teaching Pattern

Every file should end with:
```python
# Self-teaching note:
#
# This file demonstrates:
# - Concept A (prerequisite: Level X)
# - Concept B (prerequisite: Level Y)
# - Pattern Z (professional Python)
#
# The learner will encounter this AFTER mastering prerequisites.
```

## TDD Requirements

1. Write test FIRST (in `tests/`)
2. Run test, confirm it fails
3. Implement minimal code to pass
4. Refactor if needed
5. Test file name must match: `foo.py` → `tests/test_foo.py`

## PRIORITY ZERO: THE EXPERIENCE MUST FEEL GOOD

**A gamified experience that FUCKING FEELS GOOD is the ONLY priority zero.**

Not "working code". Not "feature complete". Not "tests pass".

If it doesn't feel like a GAME - if there's janky text menus, if there's `input()` prompts, if it crashes into a shitty manual fallback - **IT IS BROKEN**.

The Rich panel welcome is the START of the experience, not the whole thing. The ENTIRE interaction must feel polished, responsive, and FUN.

### Primary Control Surfaces

We want a **Primary Control Surface** for every context:

**WebUI Experience:**
- Full gamepad support with smooth, responsive buttons
- Rich, graphical interface designed for couch gaming
- **OLED-inky-black dark theme** - gorgeous, understated, easy on the eyes
- **Gorgeous understated light theme** - equally polished
- Works on TV/console/laptop/tablet/browser
- Progressive transformation across input devices

### WebUI Tech Stack (MANDATORY)

**Stack: Vue.js + TailwindCSS + Three.js/WebGPU**

```
Frontend:
├── Vue.js 3         # Progressive SPA framework (Composition API)
├── TailwindCSS      # Utility-first CSS (dark mode, responsive)
├── Three.js         # 3D graphics, visualizations
└── WebGPU           # Hardware-accelerated rendering (with fallback)

Backend:
├── FastAPI          # Python API server
└── WebSockets       # Real-time gamepad/multiplayer sync
```

**REFACTOR AWAY FROM HTMX** - The current HTMX implementation was a prototype.
We are migrating to Vue.js for:
- Proper SPA routing and state management
- Reactive gamepad input handling
- 3D visualizations (concept DAG, achievements, progress)
- WebGPU shader effects for that premium gaming feel
- Better TypeScript support

**DO NOT add more HTMX code.** All new WebUI work should use Vue.js.

**Touchscreen UI:**
- Optimized for finger interaction when touchscreen detected
- Drag and drop with your finger
- Pinch zoom for code/content
- Three finger scroll
- Five finger home gesture (the "FU Salute" internally, but don't call it that publicly)

**Terminal UI (Rich):**
- Use the ENTIRE full power of Rich - it can do **quarter character pixel rendering** in full colour!
- This is a GREAT place to prototype and start
- Not a fallback - a first-class experience
- Terminal is cozy, fast, and beautiful when done right

**Input Device Transformation:**
- UI magically transforms based on detected input (like Baldur's Gate 3)
- Press a gamepad button → UI shifts to gamepad-optimized layout
- Touch the screen → UI shifts to touch-optimized layout
- Type on keyboard → UI shifts to keyboard-optimized layout
- Seamless, automatic, delightful

When in doubt:
- **Fun over complete** - A fun partial feature > boring complete one
- **Controller-first** - Design for gamepad, adapt for keyboard
- **Analog over binary** - Gradients over checkboxes
- **Play over study** - Gaming language over academic
- **NO FALLBACKS TO JANKY TEXT UI** - If the nice UI breaks, FIX IT, don't fall back

---

*Built in The Forge. Powered by Palace. For the joy of learning.*
