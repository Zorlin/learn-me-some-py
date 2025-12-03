# TOML Schemas

Complete schema documentation for LMSP concept and challenge definitions.

---

## Overview

LMSP uses TOML files to define:
- **Concepts** - Python concepts organized in a DAG (Directed Acyclic Graph)
- **Challenges** - Programming exercises that teach concepts

Both schemas support the adaptive learning engine with rich metadata for personalization.

---

## Concept Schema

### Location

Concepts are organized by level in `concepts/level_N/`:

```
concepts/
├── level_0/          # Primitives (variables, types, print)
│   ├── variables.toml
│   ├── types.toml
│   └── print.toml
├── level_1/          # Control flow (if, for, while, match)
├── level_2/          # Collections (lists, dicts, tuples)
├── level_3/          # Functions (def, parameters, scope)
├── level_4/          # Intermediate (comprehensions, lambda)
├── level_5/          # Classes (class, init, self, methods)
└── level_6/          # Patterns (professional patterns)
```

### Full Schema

```toml
# ========================================
# CONCEPT METADATA
# ========================================

[concept]
id = "string"                    # Unique identifier (snake_case)
                                 # Example: "list_comprehensions"

name = "string"                  # Display name (Title Case)
                                 # Example: "List Comprehensions"

level = 0                        # Difficulty level (0-6)
                                 # 0 = Absolute beginner
                                 # 6 = Professional patterns

prerequisites = ["concept_ids"]  # Concepts that must be mastered first
                                 # Empty array = no prerequisites
                                 # Example: ["lists", "for_loops"]

# ========================================
# LEARNING CONTENT
# ========================================

[description]
brief = "string"                 # One-line summary (max 80 chars)
                                 # Used in menus and quick reference

detailed = """string"""          # Full explanation with examples
                                 # Multi-line string
                                 # Include:
                                 #   - What it is
                                 #   - When to use it
                                 #   - Code examples
                                 #   - Visual diagrams if helpful

# ========================================
# METHODS/OPERATIONS (optional)
# ========================================

[methods]
# For concepts that introduce multiple methods/operations
# Key = method name
# Value = description
# Example for lists:
append = "Add an item to the end of the list"
remove = "Remove first occurrence of a value"
pop = "Remove and return item at index (default: last)"
index = "Find position of first occurrence"
count = "Count occurrences of a value"
sort = "Sort list in place"
reverse = "Reverse list in place"

# ========================================
# COMMON MISTAKES
# ========================================

[gotchas]
# Key = gotcha name (snake_case)
# Value = explanation with examples
# Used to preempt common mistakes

off_by_one = """
Lists are zero-indexed in Python!
The first item is at index 0, not 1.

BAD:  my_list[1] to get first item
GOOD: my_list[0] to get first item
"""

mutation = """
Some methods modify the list in-place (append, sort),
others return a new value (sorted, reversed).

numbers = [3, 1, 2]
numbers.sort()      # Returns None, modifies numbers
sorted(numbers)     # Returns new list, doesn't modify
"""

# ========================================
# CONTROLLER TUTORIAL (optional)
# ========================================

[gamepad_tutorial]
text = """
How to use this concept with the controller:

Easy Mode:
  - A button: def (define function)
  - B button: return
  - X button: if
  - Y button: for

Radial Mode:
  - L-Up + R-Right: "for"
  - L-Down + R-Down: newline + indent
  - L-Center + R-Up: "in"

Practice typing 'for item in items:' using only the controller!
"""

# ========================================
# CHALLENGE PROGRESSION
# ========================================

[challenges]
# Three difficulty tiers for each concept
starter = "challenge_id"         # Gentle introduction
                                 # Scaffolded, hints available

intermediate = "challenge_id"    # Apply understanding
                                 # Less scaffolding

mastery = "challenge_id"         # Demonstrate mastery
                                 # Minimal scaffolding
                                 # Speed run target

# ========================================
# FUN FACTOR (for adaptive engine)
# ========================================

[fun_factor]
type = "puzzle"                  # Primary fun type:
                                 # - puzzle: Logic challenges
                                 # - speedrun: Time pressure
                                 # - collection: Unlock/gather
                                 # - creation: Build something
                                 # - competition: Compete with others
                                 # - mastery: Perfect a skill

description = "string"           # Why this concept is fun/useful
                                 # Make it compelling!

examples = [                     # Real-world applications
    "Discord bots",
    "Data analysis",
    "Game development"
]

# ========================================
# ADAPTIVE SIGNALS (optional)
# ========================================

[adaptive]
# Signals that help the adaptive engine personalize learning

weakness_signals = [
    "Confuses append vs extend",
    "Forgets zero-indexing",
    "Tries to modify during iteration"
]

strength_indicators = [
    "Uses list comprehensions naturally",
    "Remembers method vs function distinction",
    "Completes challenges without hints"
]

# Spaced repetition tuning (optional)
initial_interval_hours = 1       # First review after N hours
max_interval_days = 30           # Cap review interval
difficulty_multiplier = 1.0      # 0.5 = easier, 2.0 = harder
```

### Minimal Example

```toml
[concept]
id = "variables"
name = "Variables"
level = 0
prerequisites = []

[description]
brief = "Store and reuse values with names"
detailed = """
Variables let you store values and give them names.

Example:
  name = "Alice"
  age = 25
  print(f"Hello, {name}! You are {age}.")

Variables can hold any type of value and can be reassigned.
"""

[challenges]
starter = "variable_basics"
intermediate = "variable_reassignment"
mastery = "variable_swapping"

[fun_factor]
type = "creation"
description = "Foundation for building anything in Python"
examples = ["Every program uses variables"]
```

### Validation Rules

1. **ID Format**: Snake_case, alphanumeric + underscores only
2. **Level Range**: 0-6 inclusive
3. **Prerequisites**: All referenced IDs must exist
4. **No Cycles**: Prerequisites must form a DAG (Directed Acyclic Graph)
5. **Challenge References**: All challenge IDs should exist
6. **Fun Type**: Must be one of the six defined types

---

## Challenge Schema

### Location

Challenges are organized by theme in `challenges/theme_name/`:

```
challenges/
├── container_basics/
│   ├── add_exists.toml
│   ├── remove.toml
│   └── get_next.toml
├── median_finder/
│   └── median.toml
├── pyramid_builder/
│   └── pyramid.toml
└── query_dispatcher/
    └── dispatch.toml
```

### Full Schema

```toml
# ========================================
# CHALLENGE METADATA
# ========================================

[challenge]
id = "string"                    # Unique identifier (snake_case)
                                 # Example: "container_add_exists"

name = "string"                  # Display name (Title Case)
                                 # Example: "Container: Add & Exists"

level = 0                        # Difficulty level (0-6)
                                 # Should match concept level

prerequisites = ["concept_ids"]  # Concepts needed to solve this
                                 # Example: ["lists", "for_loops", "if_else"]

# ========================================
# CHALLENGE DESCRIPTION
# ========================================

[description]
brief = "string"                 # One-line summary
                                 # "Build a container that supports ADD and EXISTS"

detailed = """string"""          # Full problem statement
                                 # Multi-line string
                                 # Include:
                                 #   - What to build
                                 #   - Constraints
                                 #   - Examples
                                 #   - Edge cases

# Example detailed description:
detailed = """
Build a function that processes container queries.

Your function receives a list of queries:
  [("ADD", 5), ("EXISTS", 5), ("ADD", 10), ("EXISTS", 3)]

For each query:
  - ADD x: Add x to the container, return None
  - EXISTS x: Return True if x is in container, False otherwise

Return a list of results (None for ADD, bool for EXISTS):
  [None, True, None, False]

Example:
  Input:  [("ADD", 1), ("EXISTS", 1), ("EXISTS", 2)]
  Output: [None, True, False]

Edge cases:
  - Adding duplicate values is allowed
  - EXISTS before any ADD should return False
  - Empty query list returns empty result list
"""

# ========================================
# STARTING CODE
# ========================================

[skeleton]
code = """def solution(queries):
    # Your code here
    pass
"""

# Skeleton can include:
#   - Function signature
#   - Docstring
#   - Type hints
#   - TODO comments
#   - Partial structure

# Example with scaffolding:
code = """def solution(queries):
    \"\"\"Process container queries.

    Args:
        queries: List of (command, value) tuples

    Returns:
        List of results (None for ADD, bool for EXISTS)
    \"\"\"
    container = []  # TODO: Use this to store values
    results = []    # TODO: Collect results here

    for command, value in queries:
        # TODO: Handle ADD and EXISTS
        pass

    return results
"""

# ========================================
# TEST CASES
# ========================================

[[tests.case]]
name = "Basic add and exists"
input = [[["ADD", 5], ["EXISTS", 5]]]
expected = [None, True]

[[tests.case]]
name = "Exists before add"
input = [[["EXISTS", 5], ["ADD", 5], ["EXISTS", 5]]]
expected = [False, None, True]

[[tests.case]]
name = "Multiple values"
input = [[["ADD", 1], ["ADD", 2], ["ADD", 3], ["EXISTS", 2], ["EXISTS", 4]]]
expected = [None, None, None, True, False]

[[tests.case]]
name = "Empty queries"
input = [[]]
expected = []

[[tests.case]]
name = "Duplicates allowed"
input = [[["ADD", 5], ["ADD", 5], ["EXISTS", 5]]]
expected = [None, None, True]

# Test case structure:
#   name: Descriptive name shown to player
#   input: List of arguments to function
#          Outer list = arguments, inner values = actual args
#   expected: Expected return value
#            Must be JSON-serializable

# ========================================
# PROGRESSIVE HINTS
# ========================================

[hints]
# Four levels of hints, increasingly specific

level_1 = """
Think about what data structure you need to store values.
What collection type can hold items and check if something exists?
"""

level_2 = """
Use a list to store values.
When you see ADD, append to the list.
When you see EXISTS, use 'in' to check if value is in list.
"""

level_3 = """
Structure your loop like this:
  for command, value in queries:
      if command == "ADD":
          # Add value to container
      elif command == "EXISTS":
          # Check if value in container
"""

level_4 = """
Almost there! The pattern is:

container = []
results = []
for cmd, val in queries:
    if cmd == "ADD":
        container.append(val)
        results.append(None)
    elif cmd == "EXISTS":
        results.append(val in container)
return results
"""

# ========================================
# CONTROLLER HINTS (optional)
# ========================================

[gamepad_hints]
easy_mode = """
Using Easy Mode controls:

1. Press Y (for) to start the loop
2. Press X (if) for the condition
3. Press A (def) if you need a helper function
4. Use RT to indent, LT to dedent
5. L-Click to run and test

The radial menu (Select button) has shortcuts for:
  - "in" operator
  - "append"
  - "return"
"""

# ========================================
# REFERENCE SOLUTION (hidden from player)
# ========================================

[solution]
code = """def solution(queries):
    container = []
    results = []

    for command, value in queries:
        if command == "ADD":
            container.append(value)
            results.append(None)
        elif command == "EXISTS":
            results.append(value in container)

    return results
"""

# Solutions are:
#   - Never shown to player directly
#   - Used for validation
#   - Can be analyzed by adaptive engine
#   - Compared in SWARM mode

# ========================================
# META INFORMATION
# ========================================

[meta]
time_limit_seconds = 300         # Total time limit (5 minutes)
                                 # Soft limit, just for stats

speed_run_target = 60            # Target time for speed runners
                                 # Achieving this unlocks badge

points = 100                     # XP awarded on completion
                                 # Scales with difficulty

next_challenge = "container_remove"  # Suggested next challenge
                                     # Optional, for linear paths

# ========================================
# ADAPTIVE METADATA
# ========================================

[adaptive]
fun_factor = "puzzle"            # Primary fun type (same as concept)

weakness_signals = [
    "Forgets to return results",
    "Confuses append with extend",
    "Doesn't handle both commands"
]

project_themes = [
    "Discord bot: Managing user lists",
    "Game: Inventory system",
    "Data analysis: Set operations"
]

# Project themes connect challenges to real-world goals
# Used by project-driven curriculum generator

# ========================================
# EMOTIONAL CHECKPOINTS (optional)
# ========================================

[emotional_checkpoints]
# Prompts shown at key moments to capture emotional feedback

after_first_test_pass = """
You got the first test passing! How does that feel?

  [RT ████░░░░░░] Exciting
  [LT ░░░░░░░░░░] Still confused
  [Y] I want to explain my thinking

Press A to continue
"""

after_completion = """
All tests passing! Challenge complete!

How satisfied do you feel with your solution?

  [RT ████████░░] Very satisfied
  [LT ██░░░░░░░░] It works but feels messy
  [Y] I want to see other solutions

Press A to continue
"""

# Emotional checkpoints:
#   - Capture feelings at key moments
#   - Feed adaptive engine
#   - Build emotional profile
#   - Detect flow states
```

### Minimal Example

```toml
[challenge]
id = "hello_world"
name = "Hello, World!"
level = 0
prerequisites = ["print"]

[description]
brief = "Print a greeting"
detailed = """
Write a function that returns the string "Hello, World!".

Example:
  Input:  (no arguments)
  Output: "Hello, World!"
"""

[skeleton]
code = """def solution():
    # Your code here
    pass
"""

[[tests.case]]
name = "Returns correct greeting"
input = []
expected = "Hello, World!"

[hints]
level_1 = "Use the return keyword"
level_2 = "Return a string with the exact text"
level_3 = "return \"Hello, World!\""

[solution]
code = """def solution():
    return "Hello, World!"
"""

[meta]
time_limit_seconds = 60
speed_run_target = 10
points = 10
```

### Validation Rules

1. **ID Format**: Snake_case, alphanumeric + underscores only
2. **Level Range**: 0-6 inclusive
3. **Prerequisites**: All referenced concept IDs must exist
4. **Test Cases**: At least 3 test cases required
5. **Test Coverage**: Tests should cover edge cases
6. **Hint Progression**: Each level should be more specific
7. **Solution Validity**: Solution must pass all tests
8. **Fun Factor**: Must match a defined type

---

## Schema Evolution

### Adding Custom Fields

Both schemas support custom fields for extensions:

```toml
[custom]
author = "Wings"
created = 2025-01-15
difficulty_rating = 7.5
community_upvotes = 142
tags = ["container", "iteration", "conditionals"]
```

Custom fields are:
- Ignored by core engine
- Available to extensions
- Preserved on load/save
- Namespaced under `[custom]`

### Versioning

Schemas are versioned:

```toml
[meta]
schema_version = "1.0"
```

Future versions maintain backward compatibility:
- New optional fields can be added
- Required fields never removed
- Deprecated fields trigger warnings
- Migration tools provided

---

## Loading Examples

### Loading a Concept

```python
import tomli
from pathlib import Path

def load_concept(path: Path) -> dict:
    with open(path, "rb") as f:
        return tomli.load(f)

concept = load_concept(Path("concepts/level_2/lists.toml"))

print(concept["concept"]["name"])           # "Lists"
print(concept["concept"]["prerequisites"])  # ["variables", "types"]
print(concept["description"]["brief"])      # "Ordered collection..."
print(concept["challenges"]["starter"])     # "list_basics"
```

### Loading a Challenge

```python
challenge = load_challenge(Path("challenges/container_basics/add_exists.toml"))

print(challenge["challenge"]["name"])       # "Container: Add & Exists"
print(challenge["skeleton"]["code"])        # "def solution(queries):..."
print(len(challenge["tests"]["case"]))      # 5 test cases
print(challenge["hints"]["level_1"])        # First hint
```

### Validating a Concept DAG

```python
import networkx as nx

def build_concept_dag(concepts_dir: Path) -> nx.DiGraph:
    dag = nx.DiGraph()

    # Load all concepts
    for toml_file in concepts_dir.rglob("*.toml"):
        concept = load_concept(toml_file)
        concept_id = concept["concept"]["id"]

        # Add node
        dag.add_node(concept_id)

        # Add edges from prerequisites
        for prereq in concept["concept"]["prerequisites"]:
            dag.add_edge(prereq, concept_id)

    # Validate DAG is acyclic
    if not nx.is_directed_acyclic_graph(dag):
        cycles = list(nx.simple_cycles(dag))
        raise ValueError(f"Concept DAG contains cycles: {cycles}")

    return dag

# Build DAG
dag = build_concept_dag(Path("concepts/"))

# Get unlockable concepts (no prerequisites)
roots = [n for n in dag.nodes() if dag.in_degree(n) == 0]
print(f"Starting concepts: {roots}")

# Topological sort (valid learning order)
learning_order = list(nx.topological_sort(dag))
print(f"One valid learning path: {learning_order}")
```

---

## Best Practices

### Concept Design

1. **One Concept, One File** - Don't combine unrelated concepts
2. **Clear Prerequisites** - Only list direct dependencies
3. **Progressive Examples** - Start simple, build complexity
4. **Visual Diagrams** - Use ASCII art in descriptions
5. **Relatable Analogies** - Connect to real-world concepts

### Challenge Design

1. **Test-Driven** - Write tests before solution
2. **Edge Cases** - Include boundary conditions
3. **Clear Specs** - Unambiguous requirements
4. **Incremental Hints** - Each level adds information
5. **Multiple Solutions** - Allow different approaches

### Adaptive Tuning

1. **Observe Learners** - Update signals based on real data
2. **Fun Factor** - Be honest about what's engaging
3. **Project Themes** - Connect to learner goals
4. **Emotional Checkpoints** - Don't overuse, key moments only

### Accessibility

1. **Controller-Friendly** - Test with gamepad
2. **Screen Reader** - Test with text-to-speech
3. **Colorblind Safe** - Don't rely on color alone
4. **Multiple Modalities** - Support keyboard, controller, touch

---

## Tooling

### Validation Script

```bash
# Validate all TOML files
python -m lmsp.tools.validate concepts/
python -m lmsp.tools.validate challenges/

# Check for common issues
python -m lmsp.tools.lint concepts/level_2/lists.toml
```

### Concept Graph Visualization

```bash
# Generate DAG visualization
python -m lmsp.tools.graph concepts/ --output concept-dag.png

# Show unlockable concepts
python -m lmsp.tools.graph concepts/ --unlockable --mastered "variables,types"
```

### Challenge Testing

```bash
# Test a challenge's solution
python -m lmsp.tools.test challenges/container_basics/add_exists.toml

# Run all tests for a challenge
pytest tests/challenges/test_container_add_exists.py -v
```

---

## Migration Guide

### From v0.9 to v1.0

Changes:
- Added `[adaptive]` section (optional)
- Added `[emotional_checkpoints]` (optional)
- Renamed `difficulty` to `level`
- Split `description` into `brief` and `detailed`

Migration:
```python
def migrate_concept_v0_to_v1(old_concept: dict) -> dict:
    new_concept = old_concept.copy()

    # Rename difficulty to level
    if "difficulty" in new_concept["concept"]:
        new_concept["concept"]["level"] = new_concept["concept"].pop("difficulty")

    # Split description
    if isinstance(new_concept.get("description"), str):
        desc = new_concept["description"]
        lines = desc.split("\n", 1)
        new_concept["description"] = {
            "brief": lines[0],
            "detailed": lines[1] if len(lines) > 1 else lines[0]
        }

    # Add schema version
    if "meta" not in new_concept:
        new_concept["meta"] = {}
    new_concept["meta"]["schema_version"] = "1.0"

    return new_concept
```

---

*Complete, validated schemas enable the full adaptive learning experience.*
