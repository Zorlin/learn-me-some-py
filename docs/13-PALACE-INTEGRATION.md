# PALACE INTEGRATION - Development Workflow

**Navigation:** [README](README.md) | [Architecture](10-ARCHITECTURE.md) | [LMSP Overview](11-LMSP-OVERVIEW.md) | [Player-Zero Overview](12-PLAYER-ZERO-OVERVIEW.md)

---

## What is Palace?

Palace is a **Recursive Honesty-Seeking Intelligence (RHSI) engine** that enforces test-driven development and guides iterative improvement. It's the development framework that powers LMSP and Player-Zero.

Think of it as **"AI-powered TDD enforcer meets task manager meets development oracle"**.

---

## Core Principles

### Test-Driven Development (TDD)

Palace enforces **strict TDD** by default:

1. **Write tests FIRST** - Before any implementation code
2. **Run tests** - Confirm they fail (red)
3. **Write minimal code** - Make tests pass (green)
4. **Refactor** - Clean up while keeping tests green
5. **Commit** - Only when tests pass

**In strict mode** (default for LMSP):
- Tests MUST pass before completing a session
- Cannot commit if tests fail
- Coverage metrics tracked
- No shortcuts allowed

**In YOLO mode** (exploration only):
- Tests can fail
- Commits allowed with failing tests
- Use sparingly for prototyping

---

## RHSI Loops

RHSI = **Recursive Honesty-Seeking Intelligence**

The core loop:
```
1. Analyze current state
   ↓
2. Identify gaps or issues
   ↓
3. Suggest improvement
   ↓
4. Implement improvement
   ↓
5. Validate improvement (tests)
   ↓
6. Log action (history)
   ↓
7. Recurse: Analyze new state
```

**Key insight:** Each iteration makes the system "more honest" by closing gaps between intent and reality.

**Example in LMSP:**
```
Iteration 1: "We need emotional input"
  → Create tests for EmotionalPrompt
  → Implement EmotionalPrompt
  → Tests pass ✓
  → Commit

Iteration 2: "Emotional input doesn't track state over time"
  → Create tests for EmotionalState
  → Implement EmotionalState
  → Tests pass ✓
  → Commit

Iteration 3: "Need to detect flow states from emotional data"
  → Create tests for flow detection
  → Implement is_in_flow() and needs_break()
  → Tests pass ✓
  → Commit
```

Each iteration builds on the previous, **recursively** improving the system.

---

## Mask System

Masks are **expert personas** that guide development in specific domains.

### Available Masks for LMSP

**game-designer** - Game mechanics expertise
- Understands fun, flow, engagement
- Suggests features that increase enjoyment
- Balances challenge vs frustration

**python-teacher** - Pedagogy expertise
- Knows how people learn Python
- Sequences concepts in optimal order
- Designs challenges that teach effectively

**accessibility-expert** - Controller UX expertise
- Optimizes gamepad ergonomics
- Ensures keyboard/touch fallbacks
- Tests for diverse input abilities

### Using Masks

```bash
# Use game-designer mask for new feature
pal next --mask game-designer -t --claude

# Use python-teacher mask for curriculum design
pal next --mask python-teacher -t --claude

# Use accessibility-expert for input UX
pal next --mask accessibility-expert -t --claude
```

**Masks inject specialized knowledge** into the AI's suggestions:

Without mask:
> "Add a function to track player progress"

With game-designer mask:
> "Add XP system with level-up dopamine hits. Track streak days for retention. Show progress bars for visual satisfaction. Consider achievements for milestone motivation."

---

## History Logging

Every action is logged to `.palace/history.jsonl`:

```jsonl
{"timestamp": "2025-03-15T10:30:00Z", "action": "test", "result": "pass", "tests_run": 12}
{"timestamp": "2025-03-15T10:31:00Z", "action": "commit", "message": "Add emotional input system", "files": ["lmsp/input/emotional.py", "tests/test_emotional.py"]}
{"timestamp": "2025-03-15T10:35:00Z", "action": "suggest", "mask": "game-designer", "suggestion": "Add haptic feedback on test pass"}
{"timestamp": "2025-03-15T10:40:00Z", "action": "implement", "feature": "haptic_feedback", "files": ["lmsp/game/audio.py"]}
```

**Benefits:**
- Full audit trail of development
- Context for AI suggestions
- Replay development history
- Debug "what changed when"

---

## Development Commands

### pal next

**Purpose:** Suggest and optionally execute next development task.

**Basic usage:**
```bash
# Suggest next task (interactive)
pal next

# Suggest and execute with Claude
pal next -t --claude

# Use specific mask
pal next --mask game-designer -t --claude

# Fast mode (skip explanations)
pal next --fast -t --claude
```

**What it does:**
1. Analyzes project state (files, tests, history)
2. Identifies gaps or next steps
3. Suggests task with rationale
4. Optionally executes task with permission
5. Runs tests to verify
6. Logs action to history

**Example session:**
```
$ pal next -t --claude

Analyzing project state...
- emotional.py: ✓ Implemented and tested
- adaptive/engine.py: ✓ Implemented and tested
- adaptive/spaced.py: ✗ Not implemented

Suggestion: Implement spaced repetition scheduler
Rationale: Adaptive engine needs spaced.py to schedule concept reviews

Proceed? [y/n]: y

Creating tests/test_spaced.py...
Implementing lmsp/adaptive/spaced.py...
Running tests... ✓ All pass (14/14)
Logged to .palace/history.jsonl
```

### pal test

**Purpose:** Run test suite with Palace validation.

**Usage:**
```bash
# Run all tests
pal test

# Run specific test file
pal test tests/test_emotional.py

# Run with coverage
pal test --coverage

# Fast mode (no coverage)
pal test --fast
```

**What it does:**
1. Runs pytest with project configuration
2. Collects coverage metrics
3. Reports pass/fail counts
4. In strict mode, exits non-zero if tests fail
5. Logs results to history

**Example output:**
```
$ pal test

Running tests...
tests/test_emotional.py::test_prompt_creation ✓
tests/test_emotional.py::test_trigger_update ✓
tests/test_emotional.py::test_confirmation ✓
tests/test_adaptive.py::test_profile_creation ✓
tests/test_adaptive.py::test_observe_attempt ✓
tests/test_adaptive.py::test_recommend_next ✓

14 passed in 2.3s
Coverage: 87%

✓ All tests pass
```

### pal build

**Purpose:** Build the project (compile, package, etc.).

**Usage:**
```bash
# Build project
pal build

# Build for release
pal build --release

# Build and install
pal build --install
```

**For LMSP (Python project):**
```bash
$ pal build

Building LMSP...
- Installing dependencies from pyproject.toml
- Building wheel
- Installing to .venv

✓ Build complete
```

### pal run

**Purpose:** Run the application.

**Usage:**
```bash
# Run with default config
pal run

# Run with arguments
pal run -- --input gamepad --player-zero

# Run specific entry point
pal run --entry lmsp.main
```

**Example:**
```
$ pal run -- --input gamepad

Starting LMSP...
Input device: Gamepad detected (Xbox Controller)
Loading concepts from concepts/
Loading challenges from challenges/
Adaptive engine initialized

Press START to begin
```

### pal commit

**Purpose:** Create well-formatted git commit.

**Usage:**
```bash
# Commit with Palace guidance
pal commit

# Commit with message
pal commit -m "Add emotional input system"

# Commit all changes
pal commit -a -m "Implement spaced repetition"
```

**What it does:**
1. Checks that tests pass (strict mode)
2. Analyzes staged changes
3. Suggests commit message (if not provided)
4. Creates commit
5. Logs to history

**Example:**
```
$ pal commit

Checking tests... ✓ All pass
Analyzing staged changes...
- Added: lmsp/input/emotional.py (95 lines)
- Added: tests/test_emotional.py (63 lines)

Suggested commit message:
"Add emotional input system with RT/LT triggers"

Accept? [y/n/edit]: y

Commit created: a3f7c9e
Logged to .palace/history.jsonl
```

### pal switch

**Purpose:** Sync development state across machines (Castle feature).

**Usage:**
```bash
# Push state to Castle
pal switch push

# Pull state from Castle
pal switch pull

# Sync both ways
pal switch sync
```

**What it does:**
- Syncs `.palace/history.jsonl` across machines
- Syncs git state (branch, uncommitted changes)
- Ensures you can seamlessly continue work on any machine

---

## TDD Enforcement

Palace makes TDD **mandatory** in strict mode:

### Rule 1: Tests Before Code

```bash
$ pal next -t --claude

Suggestion: Implement radial typing
Creating tests/test_radial.py...  # TESTS FIRST
Implementing lmsp/input/radial.py...  # THEN CODE
```

If you try to implement without tests:
```bash
$ pal next -t --claude

Suggestion: Implement radial typing
Error: No tests found for radial.py
Create tests/test_radial.py first
```

### Rule 2: Tests Must Pass

```bash
$ pal commit -m "Add radial typing"

Checking tests... ✗ 2 failures
Error: Cannot commit with failing tests (strict mode)
Fix tests or use --yolo flag
```

### Rule 3: Coverage Tracked

```bash
$ pal test --coverage

Coverage: 87%
Warning: Below target (90%)
Uncovered: lmsp/input/radial.py lines 45-52
```

### Overriding (Use Sparingly)

```bash
# YOLO mode: Allow commits with failing tests
pal commit --yolo -m "WIP: Exploring radial typing"

# Skip coverage checks
pal test --no-coverage
```

**Use YOLO mode only for:**
- Rapid prototyping
- Spike investigations
- Emergency fixes (with plan to add tests later)

---

## Palace Configuration for LMSP

`.palace/config.json`:

```json
{
  "project": {
    "name": "learn-me-some-py",
    "type": "python",
    "version": "0.1.0"
  },
  "strict_mode": true,
  "test": {
    "command": "pytest tests/ -v",
    "coverage_target": 90,
    "coverage_command": "pytest tests/ --cov=lmsp --cov-report=html"
  },
  "build": {
    "command": "python -m build"
  },
  "run": {
    "command": "python -m lmsp"
  },
  "masks": {
    "available": [
      "game-designer",
      "python-teacher",
      "accessibility-expert"
    ],
    "default": null
  },
  "history": {
    "enabled": true,
    "file": ".palace/history.jsonl",
    "max_size_mb": 100
  }
}
```

---

## Workflow Examples

### Adding a New Feature

**Scenario:** Add spaced repetition to adaptive engine

**Steps:**
```bash
# 1. Start development session
cd /mnt/castle/garage/learn-me-some-py
pal next -t --claude

# Palace suggests: "Implement spaced repetition scheduler"

# 2. Palace creates tests FIRST
# tests/test_spaced.py created with:
# - test_schedule_review()
# - test_calculate_interval()
# - test_due_dates()

# 3. Tests fail (red) - as expected
pytest tests/test_spaced.py
# 3 failed

# 4. Palace implements lmsp/adaptive/spaced.py
# Minimal code to pass tests

# 5. Tests pass (green)
pytest tests/test_spaced.py
# 3 passed

# 6. Refactor if needed
# Palace suggests improvements while keeping tests green

# 7. Commit
pal commit -m "Add spaced repetition scheduler"

# 8. History logged
cat .palace/history.jsonl | tail -1
# {"timestamp": "...", "action": "commit", "feature": "spaced_repetition", ...}
```

### Fixing a Bug

**Scenario:** Scope bug in validator.py

**Steps:**
```bash
# 1. Start with bug report
pal next -t --claude --prompt "Fix scope bug in validator.py"

# 2. Palace suggests: "Add test to reproduce scope bug"

# 3. Create failing test
# tests/test_validator.py:
def test_nested_function_scope():
    code = """
def outer():
    x = 1
    def inner():
        x = 2  # Should not affect outer x
    inner()
    return x
    """
    result = execute_sandboxed(code)
    assert result == 1  # Currently fails, returns 2

# 4. Run test - it fails (reproduces bug)
pytest tests/test_validator.py::test_nested_function_scope
# FAILED

# 5. Palace fixes validator.py
# Implements proper scope isolation

# 6. Test passes
pytest tests/test_validator.py::test_nested_function_scope
# PASSED

# 7. Run full test suite
pal test
# All pass ✓

# 8. Commit
pal commit -m "Fix scope bug in nested functions"
```

### Iterative Improvement

**Scenario:** Make adaptive engine smarter

**Iteration 1:**
```bash
pal next -t --claude --mask game-designer

# Suggestion: "Add flow state detection to adaptive engine"
# Tests + implementation + commit
```

**Iteration 2:**
```bash
pal next -t --claude --mask game-designer

# Suggestion: "Add break suggestions when flow state drops"
# Tests + implementation + commit
```

**Iteration 3:**
```bash
pal next -t --claude --mask game-designer

# Suggestion: "Add session length tracking for optimal breaks"
# Tests + implementation + commit
```

Each iteration:
- Builds on previous
- Maintains test coverage
- Leaves codebase in working state
- Logged to history

---

## Integration with Claude

Palace integrates with Claude Code for AI-powered development:

### Task Suggestions

```python
# Palace analyzes project
async def suggest_next_task(project_state: ProjectState) -> Task:
    """Use Claude to suggest next task."""
    prompt = f"""
    Project: {project_state.name}
    Completed: {project_state.completed_features}
    In progress: {project_state.in_progress}
    Test coverage: {project_state.coverage}%

    What should we work on next?
    Consider:
    - Missing tests
    - Incomplete features
    - Low coverage areas
    - Technical debt
    """

    response = await claude.complete(prompt)
    return parse_task(response)
```

### Code Review

```python
# Palace asks Claude to review changes
async def review_changes(diff: str) -> Review:
    """Use Claude to review code changes."""
    prompt = f"""
    Review this diff for:
    - Correctness
    - Test coverage
    - Code quality
    - Potential bugs

    Diff:
    {diff}
    """

    response = await claude.complete(prompt)
    return parse_review(response)
```

### Commit Messages

```python
# Palace generates commit message
async def generate_commit_message(diff: str) -> str:
    """Use Claude to generate commit message."""
    prompt = f"""
    Write a clear, concise commit message for:

    {diff}

    Format: <verb> <what> [optional context]
    Examples:
    - "Add emotional input system with RT/LT triggers"
    - "Fix scope bug in nested functions"
    - "Refactor adaptive engine for better performance"
    """

    return await claude.complete(prompt)
```

---

## Benefits for LMSP Development

### Enforced Quality

**Without Palace:**
```bash
# Developer writes code without tests
vim lmsp/input/radial.py
# ... 200 lines of complex code ...

# Commits without testing
git commit -m "Added radial typing"

# Breaks production
# No tests to catch bugs
# Technical debt accumulates
```

**With Palace:**
```bash
# Palace enforces tests first
pal next -t --claude

# Creates tests/test_radial.py FIRST
# Then implements lmsp/input/radial.py
# Tests must pass before commit
# Coverage tracked
# Quality maintained
```

### Guided Development

**Without Palace:**
```bash
# Developer unsure what to work on next
# Picks random task
# Spends time on low-priority items
# No clear progress
```

**With Palace:**
```bash
# Palace analyzes state
pal next

# Suggests highest-priority task
# Explains rationale
# Provides clear next step
# Ensures steady progress
```

### Knowledge Preservation

**Without Palace:**
```bash
# Developer implements feature
# No documentation of why
# Context lost over time
# Future developers confused
```

**With Palace:**
```bash
# Every action logged
# History shows decision rationale
# Context preserved in .palace/history.jsonl
# Future developers can replay history
```

---

## Advanced Features

### Parallel Development

```bash
# Multiple developers on same project
# Palace syncs via Castle

# Developer 1 (machine A)
pal next -t --claude
# Works on adaptive engine

# Developer 2 (machine B)
pal next -t --claude
# Works on input system

# Both push state
pal switch push

# Castle merges histories
# Conflict detection
# Coordinated development
```

### Replay History

```bash
# View development timeline
pal history

# Replay specific action
pal replay <action_id>

# Diff between states
pal diff <timestamp1> <timestamp2>
```

### Custom Workflows

```bash
# Define project-specific workflow
# .palace/workflows/feature.yml
steps:
  - create_tests
  - run_tests_expect_fail
  - implement_feature
  - run_tests_expect_pass
  - refactor
  - commit

# Run workflow
pal workflow feature
```

---

## Palace vs Other Tools

### vs Make/Cargo/npm scripts

**Make/Cargo/npm:**
- Just task runners
- No TDD enforcement
- No AI guidance
- No history tracking

**Palace:**
- Task runner + TDD enforcer + AI guide
- Enforces quality standards
- Suggests what to build next
- Preserves development context

### vs CI/CD (GitHub Actions, etc.)

**CI/CD:**
- Runs on remote server
- Validates after commit
- No local enforcement
- No task suggestions

**Palace:**
- Runs locally
- Validates before commit
- Enforces TDD workflow
- AI-powered suggestions

### vs IDE Features (VS Code, PyCharm)

**IDEs:**
- Static analysis
- Code completion
- Refactoring tools

**Palace:**
- Dynamic project analysis
- Task-level suggestions
- Development orchestration
- Quality enforcement

**Best used together:** Palace + modern IDE

---

## Future Palace Features

### Multi-Agent Development

```bash
# Spawn multiple AI agents
pal swarm --agents 5 --goal "Implement radial typing"

# Each agent works on different aspect
# Palace coordinates
# Merges results
```

### Predictive Suggestions

```bash
# Palace learns your patterns
pal predict

# "Based on your history, you typically work on tests next"
# "This feature usually requires 3-5 commits"
# "Estimated time: 2 hours"
```

### Automated Refactoring

```bash
# Palace suggests refactorings
pal refactor suggest

# "Extract common pattern in adaptive/*.py"
# "Reduce complexity in validator.py"
# "Consolidate test fixtures"

# Apply with tests
pal refactor apply --validate
```

---

**Summary:**

Palace is LMSP's development backbone:
- **Enforces TDD** - Tests first, always
- **Guides progress** - Suggests next steps
- **Preserves context** - Logs everything
- **Maintains quality** - Coverage, standards
- **Enables collaboration** - Sync across machines

Without Palace, LMSP would be "just another project". With Palace, it's a **self-improving learning system** that gets better with every iteration.

---

**See Also:**
- [Architecture](10-ARCHITECTURE.md) - How the three systems work together
- [Testing Strategy](18-TESTING-STRATEGY.md) - Palace's TDD approach
- [Palace Documentation](https://github.com/palace-project) - Full Palace docs
