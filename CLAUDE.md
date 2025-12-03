# LMSP - Claude Code Integration

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

## Fun First

When in doubt:
- **Fun over complete** - A fun partial feature > boring complete one
- **Controller-first** - Design for gamepad, adapt for keyboard
- **Analog over binary** - Gradients over checkboxes
- **Play over study** - Gaming language over academic

---

*Built in The Forge. Powered by Palace. For the joy of learning.*
