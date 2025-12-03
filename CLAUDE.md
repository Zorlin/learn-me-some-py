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

## MANDATORY: Modern Pytest Validation Pattern

**ALL concept try_its and challenges MUST use pytest validation. NO legacy validation.**

### The Pattern

1. **TOML file** has a `[validation]` section:
```toml
[validation]
type = "pytest"
test_file = "test_concept_name.py"
```

2. **Test file** lives next to the TOML (e.g., `concepts/level_0/test_variables.py`):
```python
"""Pytest tests for [Concept Name] concept."""
import subprocess
import sys

def run_player_code(code: str) -> tuple[str, str, int]:
    """Execute player code and capture output."""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=5
    )
    return result.stdout, result.stderr, result.returncode

class TestConceptName:
    """Tests for the concept."""

    def test_no_syntax_errors(self, player_code: str):
        """Code should have no syntax errors."""
        try:
            compile(player_code, "<player>", "exec")
        except SyntaxError as e:
            raise AssertionError(f"Syntax error at line {e.lineno}: {e.msg}")

    def test_code_runs(self, player_code: str):
        """Code should execute without runtime errors."""
        stdout, stderr, returncode = run_player_code(player_code)
        assert returncode == 0, f"Code failed with error: {stderr}"

    def test_expected_output(self, player_code: str):
        """Output should match expected."""
        stdout, stderr, returncode = run_player_code(player_code)
        assert returncode == 0, f"Code failed: {stderr}"
        # Add specific assertions for expected output
        assert "expected" in stdout.strip()
```

3. **The `player_code` fixture** is automatically provided by the validator (see `lmsp/python/validator.py:PytestValidator`)

### NEVER DO THIS (Legacy Pattern - FORBIDDEN)

```python
# WRONG: Comparing stdout with solution output
result = code_validator.validate(code, [])  # Empty test cases = BROKEN

# WRONG: Using [[tests.case]] in TOML
[[tests.case]]
name = "basic"
input = [1, 2]
expected = 3
```

### Reference Example

See `concepts/level_0/basic_operators.toml` and `concepts/level_0/test_basic_operators.py` for the canonical implementation.

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

### The Director (`lmsp/adaptive/director.py`)

The invisible AI that watches the learner's journey and shapes their experience.

**When you encounter a common learner mistake:**
1. **Add a `StruggleType`** - enum value describing the pattern
2. **Add detection in `_analyze_failure()`** - regex/heuristics to spot it
3. **Add intervention in `_get_rule_based_intervention()`** - helpful micro-lesson

**Examples of Director-detected patterns:**
- `STRING_VS_IDENTIFIER` - `if op == add` instead of `if op == 'add'`
- `OPERATOR_ORDER_TYPO` - `health =- damage` instead of `health -= damage`
- `OUTPUT_FORMAT_MISMATCH` - printed `5` when expected `Your name has 5 letters`

**DO NOT hardcode error checks in pytest tests.** The Director provides intelligent, personalized feedback. Tests just validate correctness; The Director teaches.

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

## NO LEGACY - UPDATE EVERYTHING

**There is no such thing as "legacy". Do NOT keep "old styles" around.**

When you encounter old formats, old patterns, or outdated code:
- **UPDATE IT** to match current formats
- **DO NOT** preserve "old-style" anything
- **DO NOT** add compatibility shims for deprecated approaches
- **DO NOT** say "this is the legacy way" - there is only ONE way: the current way

If old curricula, tests, or code don't match current standards, FIX THEM.

## Challenge Test Format: PYTEST ONLY

**NEVER use the legacy inline TOML `[tests]` format. ALWAYS use pytest files.**

Every challenge MUST use:
```toml
[validation]
type = "pytest"
test_file = "test_challenge_name.py"
```

The pytest file goes in the same directory as the challenge TOML (e.g., `challenges/tutorial/test_simple_math.py`).

**If you encounter a challenge using the old `[[tests.case]]` format, FIX IT:**
1. Create a `test_*.py` file with proper pytest tests
2. Update the TOML to use `[validation] type = "pytest"`
3. Remove the old `[tests]` section

**Why pytest?**
- Allows personalized validation (extract user's values, check patterns)
- The Director handles teaching; tests just validate correctness
- Better error messages for learners
- Consistent with how real Python projects work

See `challenges/tutorial/test_favorite_things.py` for the pattern.

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

### INSTANT. RESPONSIVE. ZERO COOLDOWN.

**Input must feel INSTANT. No cooldowns. No artificial delays. No "debouncing" that makes the UI feel frozen.**

When the user presses a button or moves a stick:
- The response happens on the NEXT FRAME
- Not "after 133ms cooldown"
- Not "when the debounce timer expires"
- IMMEDIATELY

If something needs rate limiting (like network requests), do it at the ACTION level, not the INPUT level. The user should always feel their input was received and processed instantly.

**Edge detection is fine** - only triggering on button press (not hold) is correct behavior. But once the press is detected, the action is INSTANT.

This applies to:
- D-pad navigation
- Thumbstick navigation
- Button presses
- Cursor movement
- Everything

**If it feels sluggish, it's BROKEN.**

---

*Built in The Forge. Powered by Palace. For the joy of learning.*
