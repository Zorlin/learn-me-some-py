# Concept DAG (Directed Acyclic Graph)

**Learning isn't linear. It's a web of prerequisites.**

---

## Overview

LMSP organizes Python concepts as a **Directed Acyclic Graph (DAG)**, not a linear progression. This reflects how real learning works: some concepts depend on others, but many can be learned in parallel.

## The Full Concept Graph

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
    │ │   for_loops   │◄┼──┘   │  │ │ in_operator │ │
    │ └───────┬───────┘ │       │  │ └──────┬──────┘ │
    │         │         │       │  │        │        │
    │ ┌───────▼───────┐ │       │  │ ┌──────▼──────┐ │
    │ │ while_loops   │ │       │  │ │     len     │ │
    │ └───────────────┘ │       │  │ └──────┬──────┘ │
    │         │         │       │  │        │        │
    │ ┌───────▼───────┐ │       │  │ ┌──────▼──────┐ │
    │ │  match_case   │ │       │  │ │   sorted    │ │
    │ └───────────────┘ │       │  │ └─────────────┘ │
    └───────────────────┘       │  └─────────────────┘
                                │           │
                    ┌───────────┴───────────┘
                    │
          ┌─────────▼─────────┐
          │     Level 3       │
          │ ┌───────────────┐ │
          │ │ def_return    │ │
          │ └───────┬───────┘ │
          │         │         │
          │ ┌───────▼───────┐ │
          │ │  parameters   │ │
          │ └───────┬───────┘ │
          │         │         │
          │ ┌───────▼───────┐ │
          │ │     scope     │ │  ← THE BUG (global state leak)
          │ └───────────────┘ │
          └───────┬───────────┘
                  │
        ┌─────────┼─────────┐
        │         │         │
  ┌─────▼─────┐ ┌─▼──────┐ ┌─▼─────────┐
  │  Level 4  │ │        │ │  Level 5  │
  │ ┌────────┐│ │        │ │ ┌────────┐│
  │ │  comp  ││ │        │ │ │ class  ││
  │ │rehens  ││ │        │ │ │ _init  ││
  │ │ ions   ││ │        │ │ └───┬────┘│
  │ └───┬────┘│ │        │ │     │     │
  │     │     │ │        │ │ ┌───▼────┐│
  │ ┌───▼────┐│ │        │ │ │  self  ││
  │ │ lambda ││ │        │ │ └───┬────┘│
  │ └───┬────┘│ │        │ │     │     │
  │     │     │ │        │ │ ┌───▼────┐│
  │ ┌───▼────┐│ │        │ │ │methods ││
  │ │min_max ││ │        │ │ └────────┘│
  │ │  _key  ││ │        │ └───────────┘
  │ └────────┘│ │        │       │
  └───────────┘ └────────┘       │
        │                        │
        └────────────┬───────────┘
                     │
           ┌─────────▼─────────┐
           │     Level 6       │
           │ ┌───────────────┐ │
           │ │  container_   │ │
           │ │   pattern     │ │
           │ └───────┬───────┘ │
           │         │         │
           │ ┌───────▼───────┐ │
           │ │    median_    │ │
           │ │    pattern    │ │
           │ └───────┬───────┘ │
           │         │         │
           │ ┌───────▼───────┐ │
           │ │   dispatch_   │ │
           │ │    pattern    │ │
           │ └───────────────┘ │
           └───────────────────┘
```

## Level Breakdown

### Level 0: Primitives

**Foundation concepts - start here.**

```python
# variables
x = 5
name = "Wings"

# types
int, str, float, bool

# print
print("Hello, world!")
```

**Prerequisites:** None
**Unlocks:** Everything else

### Level 1: Control Flow

**Making decisions and repeating actions.**

```python
# if_else
if x > 5:
    print("big")
else:
    print("small")

# for_loops
for i in range(10):
    print(i)

# while_loops
while x < 100:
    x = x * 2

# match_case (Python 3.10+)
match command:
    case "start":
        game.start()
    case "quit":
        game.quit()
```

**Prerequisites:** variables, types
**Unlocks:** Functions, collections

### Level 2: Collections

**Working with groups of data.**

```python
# lists
items = [1, 2, 3, 4, 5]

# in operator
if "apple" in fruits:
    print("We have apples!")

# len
count = len(items)

# sorted
ordered = sorted(items, reverse=True)
```

**Prerequisites:** variables, types
**Unlocks:** Functions, comprehensions

**Note:** Lists and for_loops can be learned in parallel (both depend on Level 0, not each other).

### Level 3: Functions

**Organizing code into reusable pieces.**

```python
# def_return
def add(a, b):
    return a + b

# parameters
def greet(name, excited=False):
    if excited:
        return f"Hello, {name}!!!"
    return f"Hello, {name}"

# scope (THE BUG)
global_var = 10

def modify():
    global global_var  # Explicit global needed
    global_var = 20
```

**Prerequisites:** variables, types, control flow, collections
**Unlocks:** Classes, comprehensions, lambda

**THE BUG:** The `scope` concept introduces the classic Python gotcha about global vs local scope. This is intentional - it's a bug the player discovers and fixes as part of the learning journey.

### Level 4: Intermediate Patterns

**Python-specific idioms and patterns.**

```python
# comprehensions
squares = [x**2 for x in range(10)]
evens = [x for x in numbers if x % 2 == 0]

# lambda
add = lambda a, b: a + b
sorted_by_name = sorted(people, key=lambda p: p.name)

# min/max with key
oldest = max(people, key=lambda p: p.age)
shortest_name = min(names, key=len)

# integer_division
half = 10 // 2  # 5, not 5.0
```

**Prerequisites:** functions
**Unlocks:** Advanced patterns

### Level 5: Classes

**Object-oriented programming.**

```python
# class_init
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

# self
class Counter:
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1  # self refers to the instance

# methods
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height
```

**Prerequisites:** functions
**Unlocks:** Advanced patterns, building LMSP features

### Level 6: Design Patterns

**Professional patterns for complex problems.**

```python
# container_pattern
class Container:
    def __init__(self):
        self.items = []

    def add(self, item):
        if item not in self.items:
            self.items.append(item)
            return True
        return False

    def exists(self, item):
        return item in self.items

# median_pattern
def median(numbers):
    sorted_nums = sorted(numbers)
    n = len(sorted_nums)
    mid = n // 2
    if n % 2 == 0:
        return (sorted_nums[mid-1] + sorted_nums[mid]) / 2
    return sorted_nums[mid]

# dispatch_pattern
COMMANDS = {
    "add": lambda container, value: container.add(value),
    "exists": lambda container, value: container.exists(value),
    "remove": lambda container, value: container.remove(value),
}

def dispatch(command, container, value):
    if command in COMMANDS:
        return COMMANDS[command](container, value)
```

**Prerequisites:** classes, comprehensions, lambda
**Unlocks:** Building real applications

## Mastery Levels

Each concept has **5 mastery levels**:

### Level 0: SEEN

```
Status: Locked
Visual: 🔒

"You'll learn this after mastering: [prerequisites]"
```

**Characteristics:**
- Concept appears in tree but is grayed out
- Shows prerequisites needed to unlock
- Can't attempt challenges yet

**Example:**
```
🔒 lambda_functions
   Prerequisites: functions, parameters
   Status: Learn functions first
```

### Level 1: UNLOCKED

```
Status: Available
Visual: ○

"Ready to learn! Take your time."
```

**Characteristics:**
- Can attempt challenges
- All hint levels available (1-4)
- No time pressure
- Infinite retries

**Example:**
```
○ lambda_functions
   Status: UNLOCKED
   Challenges: 0/3 completed
   Next: "Lambda Basics"
```

### Level 2: PRACTICED

```
Status: Practiced
Visual: ◐

"You're getting it! Keep going."
```

**Characteristics:**
- Completed 3+ challenges
- Hints still available but discouraged
- Gentle time suggestions ("Most people solve this in 5 minutes")
- Tracking time for speedrun targets

**Requirements:**
- Complete at least 3 challenges with this concept
- OR complete same challenge 3 times

**Example:**
```
◐ lambda_functions
   Status: PRACTICED
   Challenges: 3/5 completed
   Next: "Lambda with Sorting"
```

### Level 3: MASTERED

```
Status: Mastered
Visual: ●

"You've got this! Ready to use in advanced challenges."
```

**Characteristics:**
- Completed all challenges
- Achieved speedrun target on at least one
- Can use this concept in higher-level challenges
- Concept unlocks its dependents

**Requirements:**
- Complete all challenges for this concept
- Achieve speedrun target on 1+ challenges
- No failures in last 5 attempts

**Example:**
```
● lambda_functions
   Status: MASTERED
   Challenges: 5/5 completed
   Best time: 45s (target: 60s)
   Unlocks: comprehensions, min_max_key
```

### Level 4: TRANSCENDED

```
Status: Transcended
Visual: ✨

"You can teach this now!"
```

**Characteristics:**
- Can explain concept to AI students (teaching mode)
- Unlocks ability to create community challenges
- Appears as expert in that concept
- Gets notified when others struggle with this concept

**Requirements:**
- Mastered (Level 3)
- Successfully teach concept to 3+ AI students
- OR create community challenge that others complete
- OR contribute to LMSP codebase using this concept

**Example:**
```
✨ lambda_functions
   Status: TRANSCENDED
   Students taught: 7
   Community challenges: 2
   You are an expert in this concept!
```

## Dynamic Concept Registration

The concept system is **extensible** - new concepts can be added dynamically:

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
```

**Features:**

1. **Dynamic Registration**: Add concepts at runtime
2. **Prerequisite Validation**: Ensures prerequisites exist
3. **Cycle Detection**: Prevents circular dependencies
4. **NetworkX Integration**: Uses `networkx` for graph operations

### Example: Adding a Custom Concept

```python
registry = ConceptRegistry()

# Register base concepts
registry.register(Concept(id="variables", level=0, prerequisites=[]))
registry.register(Concept(id="functions", level=3, prerequisites=["variables"]))

# Add custom concept
registry.register(Concept(
    id="decorators",
    level=4,
    prerequisites=["functions", "lambda"],
    description="Functions that modify other functions"
))
```

### Getting Unlockable Concepts

```python
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

**Logic:**
1. Skip concepts already mastered
2. Check if ALL prerequisites are mastered
3. Return list of unlockable concepts

**Example:**
```python
# Player has mastered: variables, types, if_else, for_loops, lists
mastered = {"variables", "types", "if_else", "for_loops", "lists"}

# Get unlockable concepts
unlockable = registry.get_unlockable(mastered)
# Returns: [functions, while_loops, in_operator, len, sorted]
```

## Concept Dependencies (Prerequisites)

**Key Insight:** Not all concepts at the same level have the same prerequisites.

### Parallel Paths

These can be learned in ANY order:

```
Level 1 Control Flow:
  - if_else → for_loops → while_loops → match_case (sequential)

Level 2 Collections:
  - lists → in_operator → len → sorted (sequential)

if_else and lists are INDEPENDENT (both depend only on Level 0)
```

### Convergence Points

Multiple paths converge at **functions** (Level 3):

```
variables → types → if_else → for_loops ─┐
                                          ├─→ functions
variables → types → lists → in_operator ─┘
```

**Why:** Functions need both control flow AND collections to be useful.

### THE BUG - The Intentional Gotcha

The `scope` concept at Level 3 contains an intentional bug:

```python
# THE BUG - global state leaking
total = 0

def add_to_total(x):
    total = total + x  # UnboundLocalError!
    return total
```

**The Learning Journey:**

1. Player writes code using global variables
2. Code fails with `UnboundLocalError`
3. Player confused - "Why doesn't this work?"
4. Emotional input: High frustration
5. Adaptive engine offers hint
6. Player learns about `global` keyword and scope rules
7. Emotional input: High satisfaction (the "aha!" moment)

**This is meta-teaching:**
- The bug is intentional
- It's a common Python gotcha
- The frustration → understanding → satisfaction cycle creates strong memory
- Players remember this lesson because they FELT it

## NetworkX Integration

LMSP uses `networkx` for graph operations:

```python
import networkx as nx

# Build concept graph
G = nx.DiGraph()
G.add_edge("variables", "if_else")
G.add_edge("variables", "lists")
G.add_edge("if_else", "functions")
G.add_edge("lists", "functions")

# Topological sort (learning order)
learning_order = list(nx.topological_sort(G))
# ['variables', 'types', 'if_else', 'lists', 'functions', ...]

# Find all prerequisites for a concept
prerequisites = nx.ancestors(G, "functions")
# {'variables', 'types', 'if_else', 'lists'}

# Find what this concept unlocks
unlocks = nx.descendants(G, "functions")
# {'comprehensions', 'lambda', 'classes', ...}

# Check for cycles (should never happen)
assert nx.is_directed_acyclic_graph(G)
```

## TOML Concept Definitions

Concepts are defined in TOML files:

```toml
# concepts/level_2/lists.toml

[concept]
id = "lists"
name = "Lists"
level = 2
prerequisites = ["variables", "types"]

[description]
brief = "Collections of items in order"
detailed = """
Lists are Python's most versatile collection type. They can hold
any type of data, can grow and shrink, and maintain order.
"""

[methods]
append = "Add item to end"
extend = "Add multiple items to end"
insert = "Add item at specific position"
remove = "Remove first occurrence of item"
pop = "Remove and return item at index"
index = "Find position of item"
count = "Count occurrences of item"

[gotchas]
mutable = """
Lists are mutable - changes affect all references!

    a = [1, 2, 3]
    b = a
    b.append(4)
    print(a)  # [1, 2, 3, 4] - SURPRISE!

Use a.copy() to avoid this.
"""

[challenges]
starter = "list_basics"
intermediate = "list_manipulation"
mastery = "list_algorithms"

[adaptive]
weakness_signals = [
    "Confusion about mutability",
    "Index out of range errors",
    "Not using list methods"
]
strength_indicators = [
    "Fast list comprehensions",
    "Correct use of methods",
    "Handling edge cases"
]
```

## Visualization

The concept tree can be visualized in-game:

```
📚 Your Learning Journey

Level 0 ✓ MASTERED
  ● variables
  ● types
  ● print

Level 1 ◐ PRACTICED
  ● if_else
  ● for_loops
  ◐ while_loops
  ○ match_case

Level 2 ○ UNLOCKED
  ● lists
  ◐ in_operator
  ○ len
  ○ sorted

Level 3 🔒 LOCKED
  🔒 functions (Need: for_loops, lists)

[Press X to view full tree]
```

---

*Self-teaching note: This file demonstrates graph theory concepts, NetworkX usage, TOML parsing, and the concept of progressive disclosure. Understanding this requires mastery of collections (Level 2), functions (Level 3), and classes (Level 5).*
