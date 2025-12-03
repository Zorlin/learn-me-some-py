# Concepts System Specification

## The Problem

Challenges are great for practice, but they assume you already know the building blocks.
Throwing someone into "Word Frequency Counter" when they've never seen `if key in dict` is overwhelming.

**Duolingo insight:** You learn words before sentences, letters before words.

## The Solution: Concepts

Bite-sized micro-lessons that teach ONE thing. No tests, no pressure, just understanding.

### Concept vs Challenge

| Aspect | Concept | Challenge |
|--------|---------|-----------|
| Goal | Understand ONE thing | Apply multiple things |
| Length | 30 seconds to read | 5-30 minutes to solve |
| Tests | None (maybe "try it" sandbox) | Real pytest tests |
| Pressure | Zero | Some (XP, timer, tests) |
| Format | Read → Example → Try → Done | Problem → Code → Test → Pass |

### Concept Structure

```toml
[concept]
id = "dict_key_check"
name = "Checking if a Key Exists"
level = 2
category = "dictionaries"

[content]
# The actual lesson - keep it SHORT
lesson = """
## Checking if a Key Exists

Before accessing a dictionary key, you often need to check if it exists.

```python
scores = {"alice": 95, "bob": 87}

# This CRASHES if the key doesn't exist:
print(scores["charlie"])  # KeyError!

# Check first with 'in':
if "charlie" in scores:
    print(scores["charlie"])
else:
    print("Not found")
```

The `in` keyword checks if a key exists. It returns `True` or `False`.
"""

# Optional "try it" - a tiny sandbox exercise
[content.try_it]
prompt = "Check if 'dog' is in the dictionary, print 'Found!' if yes"
starter = '''
animals = {"cat": 4, "dog": 4, "spider": 8}

# Your code here:
'''
solution = '''
if "dog" in animals:
    print("Found!")
'''

[connections]
# What this concept unlocks
enables = ["dict_get_method", "dict_iteration"]
# Challenges that use this concept
used_in = ["word_counter", "contact_book"]
# Related concepts to show
see_also = ["dict_basics", "if_statements"]

[meta]
time_to_read = 30  # seconds
difficulty = "beginner"
```

### Navigation Flow

```
┌─────────────────────────────────────────────────────────┐
│  LMSP                    [Concepts] [Challenges] [Tree] │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  📚 Concepts                                            │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ Variables   │  │ If/Else     │  │ Loops       │     │
│  │ ✓ 5/5      │  │ ✓ 4/4      │  │ ○ 2/6      │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ Lists       │  │ Dicts       │  │ Functions   │     │
│  │ ○ 3/8      │  │ ○ 1/6      │  │ ○ 0/7      │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│                                                         │
└─────────────────────────────────────────────────────────┘

Clicking "Dicts" expands:

┌─────────────────────────────────────────────────────────┐
│  📖 Dictionaries                              [Back]    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ✓ Creating a Dictionary         30s   [Review]        │
│  ✓ Accessing Values              30s   [Review]        │
│  → Checking if Key Exists        30s   [Learn]         │
│  ○ The .get() Method             45s   [Locked]        │
│  ○ Looping Through Dicts         60s   [Locked]        │
│  ○ Dictionary Comprehensions     90s   [Locked]        │
│                                                         │
│  ─────────────────────────────────────────────────      │
│  Ready to practice? Try these challenges:               │
│  • Word Frequency Counter (uses: key check, .get())     │
│  • Contact Book (uses: all dict concepts)               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Concept View (Single Concept)

```
┌─────────────────────────────────────────────────────────┐
│  ← Back to Dicts        Checking if Key Exists    2/6   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ## Checking if a Key Exists                            │
│                                                         │
│  Before accessing a dictionary key, check if it exists. │
│                                                         │
│  ┌────────────────────────────────────────────────┐     │
│  │ scores = {"alice": 95, "bob": 87}              │     │
│  │                                                │     │
│  │ # This CRASHES:                                │     │
│  │ print(scores["charlie"])  # KeyError!         │     │
│  │                                                │     │
│  │ # Check first:                                 │     │
│  │ if "charlie" in scores:                        │     │
│  │     print(scores["charlie"])                   │     │
│  │ else:                                          │     │
│  │     print("Not found")                         │     │
│  └────────────────────────────────────────────────┘     │
│                                                         │
│  The `in` keyword returns True or False.                │
│                                                         │
│  ┌────────────────────────────────────────────────┐     │
│  │ 🎮 TRY IT                                      │     │
│  │                                                │     │
│  │ animals = {"cat": 4, "dog": 4, "spider": 8}   │     │
│  │                                                │     │
│  │ # Check if 'dog' exists, print "Found!" if yes│     │
│  │ _                                              │     │
│  │                                                │     │
│  │                          [Run] [Show Answer]   │     │
│  └────────────────────────────────────────────────┘     │
│                                                         │
│  [← Previous]              [Got it! ✓]        [Next →]  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Tracking Progress

```python
# Database: concept_progress table
concept_progress:
  player_id: str
  concept_id: str
  status: "unseen" | "seen" | "understood"  # No "mastered" - that comes from challenges
  seen_at: datetime
  understood_at: datetime | null
```

- **unseen**: Haven't opened it
- **seen**: Opened and read (clicked through)
- **understood**: Clicked "Got it!" (self-reported)

Mastery comes from passing challenges that USE the concept, not from the concept itself.

### Integration with Challenges

When a player fails a challenge, The Director can:
1. Detect WHICH concept they're missing (from error patterns)
2. Suggest: "Want to review 'Checking if Key Exists' first?"
3. Link directly to that concept

When viewing a challenge:
- Show prerequisite concepts with status
- "This challenge uses: ✓ Dict Basics, ✓ Loops, ○ Key Checking"
- Clicking unlocks concept shows it inline or in modal

### File Structure

```
concepts/
├── level_1/
│   ├── variables.toml
│   ├── print_function.toml
│   ├── strings_basics.toml
│   └── numbers_basics.toml
├── level_2/
│   ├── if_statements.toml
│   ├── for_loops.toml
│   ├── while_loops.toml
│   ├── lists_basics.toml
│   ├── dict_basics.toml
│   ├── dict_key_check.toml      # NEW
│   ├── dict_get_method.toml     # NEW
│   └── dict_iteration.toml      # NEW
└── level_3/
    ├── functions_basics.toml
    ├── functions_return.toml
    └── list_comprehensions.toml
```

### API Endpoints

```
GET  /api/concepts                    # List all concepts (grouped by category)
GET  /api/concepts/:id                # Get single concept content
POST /api/concepts/:id/seen           # Mark as seen
POST /api/concepts/:id/understood     # Mark as understood
GET  /api/concepts/for-challenge/:id  # Get concepts needed for a challenge
```

### Priority Concepts to Create

For Word Frequency Counter specifically:
1. `dict_basics` - Creating and accessing dicts
2. `dict_key_check` - `if key in dict` pattern  ← THE MISSING PIECE
3. `dict_get_method` - `.get(key, default)` as shortcut
4. `for_loop_basics` - Looping through a list

These four concepts = everything needed for Stage 1 of Word Counter.

## Implementation Order

1. Define TOML format for concepts
2. Create 4-5 example concepts (dict family)
3. Add `/api/concepts` endpoints
4. Create ConceptsView.vue and ConceptView.vue
5. Add "Concepts" to nav
6. Wire Director to suggest concepts on failure
7. Show concept prerequisites on challenge view
