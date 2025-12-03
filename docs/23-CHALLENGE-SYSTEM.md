# Challenge System

**Code challenges with scaffolding, hints, and emotional checkpoints.**

---

## Overview

Challenges are the core learning mechanism in LMSP. Each challenge:
- Tests a specific concept or pattern
- Provides skeleton code to guide structure
- Offers 4 levels of hints
- Includes emotional checkpoints
- Has speedrun targets for mastery

## Challenge TOML Format

Challenges are defined in TOML files under `challenges/`:

```toml
# challenges/container_basics/add_exists.toml

[challenge]
id = "container_add_exists"
name = "Container: Add & Exists"
level = 2
prerequisites = ["lists", "in_operator"]

[description]
brief = "Build a container that tracks items"
detailed = """
You're building a container class that can:
- Add items (only if not already present)
- Check if items exist

This teaches the fundamentals of collections and lookups.
"""

[skeleton]
code = """
def solution(queries):
    container = []
    results = []

    for command, value in queries:
        # YOUR CODE HERE
        pass

    return results
"""

[tests]
[[tests.case]]
name = "Basic add and exists"
input = [["add", 1], ["exists", 1], ["exists", 2]]
expected = [true, true, false]

[[tests.case]]
name = "Duplicate add"
input = [["add", 1], ["add", 1], ["exists", 1]]
expected = [true, false, true]

[[tests.case]]
name = "Empty container"
input = [["exists", 1]]
expected = [false]

[[tests.case]]
name = "Multiple items"
input = [
    ["add", 1],
    ["add", 2],
    ["add", 3],
    ["exists", 2],
    ["exists", 4]
]
expected = [true, true, true, true, false]

[hints]
level_1 = "Think about what data structure to use for the container"
level_2 = "Use a list and check if item is already in it before adding"
level_3 = "For 'add': check 'if value not in container', then append"
level_4 = """
Pattern:
    if command == "add":
        if value not in container:
            container.append(value)
            results.append(True)
        else:
            results.append(False)
    elif command == "exists":
        results.append(value in container)
"""

[gamepad_hints]
easy_mode = """
Easy Mode Controls:
  A button: if
  B button: return
  X button: append
  Y button: in operator
  RT: Indent
  LT: Dedent
"""

[solution]
code = """
def solution(queries):
    container = []
    results = []

    for command, value in queries:
        if command == "add":
            if value not in container:
                container.append(value)
                results.append(True)
            else:
                results.append(False)
        elif command == "exists":
            results.append(value in container)

    return results
"""

[meta]
time_limit_seconds = 300
speed_run_target = 60
points = 100
next_challenge = "container_remove"

[adaptive]
fun_factor = "puzzle"
weakness_signals = [
    "Not checking for duplicates",
    "Wrong return type",
    "Forgetting to append to results"
]
project_themes = [
    "Inventory systems",
    "User management",
    "Cache implementation"
]

[emotional_checkpoints]
after_first_test_pass = "Nice! How does it feel to see that first green test?"
after_completion = "You did it! How satisfied are you with your solution?"
after_speedrun = "That was FAST! How did speedrunning feel?"
```

## TOML Schema Breakdown

### [challenge] Section

```toml
[challenge]
id = "string"                    # Unique identifier
name = "string"                  # Display name
level = 0-6                      # Difficulty level
prerequisites = ["concept_ids"]  # Must master before attempting
```

**Fields:**
- **id**: Machine-readable identifier (used in code)
- **name**: Human-readable name (shown in UI)
- **level**: Maps to concept level (0-6)
- **prerequisites**: List of concept IDs that must be mastered first

### [description] Section

```toml
[description]
brief = "string"                 # One-liner summary
detailed = """string"""          # Full explanation with context
```

**Usage:**
- **brief**: Shown in challenge selection menu
- **detailed**: Shown when challenge is opened, before attempting

### [skeleton] Section

```toml
[skeleton]
code = """starting code"""
```

Provides starting code to guide structure. Player fills in the logic.

**Good Skeleton Code:**
- Sets up overall structure
- Shows expected function signature
- Indicates where player should write code (`# YOUR CODE HERE`)
- Compiles but doesn't pass tests yet

**Example:**
```python
def solution(queries):
    container = []
    results = []

    for command, value in queries:
        # YOUR CODE HERE
        pass

    return results
```

### [tests] Section

Test cases define expected behavior:

```toml
[tests]
[[tests.case]]
name = "string"
input = [any]
expected = any

[[tests.case]]
name = "string"
input = [any]
expected = any
```

**Test Case Structure:**

Each `[[tests.case]]` defines one test:
- **name**: Descriptive name for the test
- **input**: Argument(s) passed to solution function
- **expected**: Expected return value

**Types Supported:**

```toml
# Primitives
input = 5
expected = 10

# Lists
input = [1, 2, 3]
expected = [2, 4, 6]

# Nested lists
input = [[1, 2], [3, 4]]
expected = [[2, 4], [6, 8]]

# Mixed types
input = [["add", 1], ["exists", 1]]
expected = [true, true]

# Strings
input = "hello"
expected = "HELLO"
```

**Test Execution:**

```python
# For each test case:
result = solution(*test.input)  # Unpack input as args
passed = result == test.expected

# Track results
tests_passing = sum(1 for t in tests if t.passed)
tests_total = len(tests)
```

### [hints] Section

Four levels of hints, progressively more specific:

```toml
[hints]
level_1 = "Gentle nudge in right direction"
level_2 = "More specific guidance"
level_3 = "Almost the full solution"
level_4 = """Code pattern with blanks"""
```

**Hint Philosophy:**

- **Level 1**: Conceptual hint ("What data structure would work here?")
- **Level 2**: Approach hint ("Use a list and check membership")
- **Level 3**: Logic hint ("Check if value not in container before adding")
- **Level 4**: Pattern hint (shows code structure with blanks)

**Example Progression:**

```toml
[hints]
level_1 = "Think about what data structure stores unique items"

level_2 = "A list can work, but you'll need to check if an item exists before adding"

level_3 = "Use 'if value not in container' before calling container.append(value)"

level_4 = """
Pattern for add command:
    if command == "add":
        if value not in container:
            container.append(value)
            results.append(True)
        else:
            results.append(False)
"""
```

**Hint Access:**

- **UNLOCKED** (mastery 1): All hints available immediately
- **PRACTICED** (mastery 2): Hints available but discouraged ("Try without hints first!")
- **MASTERED** (mastery 3): Hints disabled for speedrun attempts

### [gamepad_hints] Section

Controller-specific guidance for easy mode:

```toml
[gamepad_hints]
easy_mode = """
Easy Mode Controls:
  A: if statement
  B: return
  X: append to list
  Y: in operator
  Start: Show hint
"""
```

**Purpose:**
- Remind players of controller mappings
- Specific to easy mode (button = Python verb)
- Shown when player opens hints

### [solution] Section

Reference solution (hidden from player):

```toml
[solution]
code = """
def solution(queries):
    container = []
    results = []

    for command, value in queries:
        if command == "add":
            if value not in container:
                container.append(value)
                results.append(True)
            else:
                results.append(False)
        elif command == "exists":
            results.append(value in container)

    return results
"""
```

**Uses:**
- Validates test cases (solution must pass all tests)
- Provides comparison for AI teaching mode
- Used for code review hints ("Your solution works, but consider this approach...")

### [meta] Section

Challenge metadata:

```toml
[meta]
time_limit_seconds = 300        # Soft limit (not enforced, just shown)
speed_run_target = 60           # Target time for mastery
points = 100                    # XP awarded
next_challenge = "challenge_id" # Suggested next challenge
```

**Fields:**
- **time_limit_seconds**: Soft time limit (shows timer, but doesn't fail)
- **speed_run_target**: Time needed to achieve speedrun badge
- **points**: XP awarded on completion
- **next_challenge**: Recommended follow-up challenge

### [adaptive] Section

Integration with adaptive engine:

```toml
[adaptive]
fun_factor = "puzzle|speedrun|collection|creation|competition|mastery"
weakness_signals = ["patterns that indicate struggle"]
project_themes = ["real-world applications"]
```

**fun_factor Values:**
- **puzzle**: Logic puzzles, problem-solving
- **speedrun**: Racing against time
- **collection**: Unlocking achievements
- **creation**: Building something
- **competition**: Competing with others
- **mastery**: Perfecting technique

**weakness_signals:**
List of common mistakes that indicate conceptual weakness:
```toml
weakness_signals = [
    "Not checking for duplicates",
    "Wrong return type",
    "Forgetting to append to results",
    "Off-by-one errors"
]
```

**project_themes:**
Real-world applications of this challenge:
```toml
project_themes = [
    "Inventory systems",
    "User management",
    "Cache implementation",
    "Database operations"
]
```

### [emotional_checkpoints] Section

When to ask for emotional feedback:

```toml
[emotional_checkpoints]
after_first_test_pass = "Nice! How does it feel to see that first green test?"
after_completion = "You did it! How satisfied are you with your solution?"
after_speedrun = "That was FAST! How did speedrunning feel?"
```

**Checkpoint Triggers:**

- **after_first_test_pass**: When first test goes from red to green
- **after_completion**: When all tests pass
- **after_speedrun**: When completed under speedrun target
- **after_hint_used**: After requesting a hint
- **after_retry**: After failing and trying again

**Purpose:**
- Capture emotional feedback at key moments
- Build emotional profile for adaptive engine
- Detect frustration vs satisfaction patterns

## Challenge Execution Flow

```python
async def run_challenge(challenge_id: str):
    """Run a challenge to completion."""

    # 1. Load challenge
    challenge = load_challenge(challenge_id)

    # 2. Show description
    await show_description(challenge.description)

    # 3. Load skeleton code
    code = challenge.skeleton.code

    # 4. Enter coding loop
    while not all_tests_passed:
        # Edit code (gamepad or keyboard)
        code = await edit_code(code)

        # Run tests
        results = run_tests(code, challenge.tests)

        # Show results
        await show_test_results(results)

        # Emotional checkpoint?
        if results.first_test_just_passed:
            emotion = await emotional_prompt(
                challenge.emotional_checkpoints.after_first_test_pass
            )
            engine.observe_emotion(emotion.dimension, emotion.value, challenge_id)

        # Offer hint?
        if player_stuck:
            hint = await offer_hint(challenge.hints)

    # 5. All tests pass!
    duration = time.time() - start_time

    # 6. Final emotional checkpoint
    emotion = await emotional_prompt(
        challenge.emotional_checkpoints.after_completion
    )
    engine.observe_emotion(emotion.dimension, emotion.value, challenge_id)

    # 7. Check speedrun
    if duration < challenge.meta.speed_run_target:
        emotion = await emotional_prompt(
            challenge.emotional_checkpoints.after_speedrun
        )
        # Award speedrun badge

    # 8. Record attempt
    engine.observe_attempt(
        concept=challenge_id,
        success=True,
        time_seconds=duration,
        hints_used=hints_used
    )

    # 9. Award XP
    player.xp += challenge.meta.points

    # 10. Suggest next
    if challenge.meta.next_challenge:
        await suggest_challenge(challenge.meta.next_challenge)
```

## Test Validation

Before accepting a challenge TOML, validate that the solution passes all tests:

```python
def validate_challenge(challenge: Challenge):
    """Ensure solution passes all tests."""

    # Load solution code
    solution_fn = load_solution_code(challenge.solution.code)

    # Run all tests
    for test_case in challenge.tests:
        result = solution_fn(*test_case.input)

        if result != test_case.expected:
            raise ValueError(
                f"Solution fails test '{test_case.name}'\n"
                f"  Input: {test_case.input}\n"
                f"  Expected: {test_case.expected}\n"
                f"  Got: {result}"
            )

    print(f"✓ Challenge '{challenge.name}' validated")
```

## Skeleton Code Philosophy

**Good skeleton code:**

```python
def solution(queries):
    container = []  # Setup done
    results = []

    for command, value in queries:  # Structure shown
        # YOUR CODE HERE  # Player fills logic
        pass

    return results  # Expected return shown
```

**Bad skeleton code:**

```python
# Too minimal - no guidance
def solution(queries):
    pass
```

```python
# Too complete - nothing to learn
def solution(queries):
    container = []
    results = []
    for command, value in queries:
        if command == "add":
            if value not in container:
                container.append(value)
                results.append(True)
            else:
                results.append(False)
        elif command == "exists":
            results.append(value in container)
    return results
```

**The Goldilocks Zone:**
- Shows overall structure
- Indicates where logic goes
- Leaves core learning objective for player

## Directory Structure

```
challenges/
├── container_basics/          # Challenge category
│   ├── add_exists.toml        # Individual challenge
│   ├── remove.toml
│   └── get_next.toml
├── median_finder/
│   ├── basic_median.toml
│   └── streaming_median.toml
├── pyramid_builder/
│   └── ascii_pyramid.toml
└── query_dispatcher/
    ├── simple_dispatch.toml
    └── lambda_dispatch.toml
```

**Naming Convention:**
- Folder: concept or pattern name
- File: specific challenge variant

## Community Challenges

Players at TRANSCENDED mastery can create community challenges:

```python
@requires_mastery(level=4)
def create_community_challenge(concept_id: str, author_id: str):
    """Create a new challenge for the community."""

    challenge = {
        "id": f"community_{uuid4()}",
        "name": input("Challenge name: "),
        "level": CONCEPTS[concept_id].level,
        "prerequisites": [concept_id],
        "author": author_id,
        "community": True,
    }

    # Guide through TOML creation
    challenge["description"] = await prompt_description()
    challenge["skeleton"] = await prompt_skeleton()
    challenge["tests"] = await prompt_tests()
    challenge["hints"] = await prompt_hints()
    challenge["solution"] = await prompt_solution()

    # Validate
    validate_challenge(challenge)

    # Submit for review
    submit_to_community(challenge)
```

---

*Self-teaching note: This file demonstrates TOML parsing, validation patterns, test-driven development, and the concept of progressive disclosure through hints. Understanding this requires mastery of collections (Level 2), functions (Level 3), and testing patterns (professional Python).*
