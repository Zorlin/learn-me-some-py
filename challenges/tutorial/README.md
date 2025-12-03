# Tutorial Challenges (Level 0-1)

**Welcome to Python!** These challenges are your first steps into programming.

## Challenge Progression

### 1. hello_world.toml
**Concepts:** print(), string literals
**Goal:** Display "Hello, World!" on the screen
**XP:** 50 points
**Why it matters:** The traditional first program in any language

### 2. personal_greeting.toml
**Concepts:** Variables, assignment, string concatenation/f-strings
**Goal:** Store a name and create a personalized greeting
**XP:** 75 points
**Why it matters:** Learn to store and reuse data

### 3. simple_math.toml
**Concepts:** Arithmetic operators, numbers vs strings
**Goal:** Calculate 42 + 58 and display the result
**XP:** 75 points
**Why it matters:** Computers are powerful calculators

### 4. temperature_converter.toml
**Concepts:** Order of operations, parentheses, round() function
**Goal:** Convert Fahrenheit to Celsius
**XP:** 100 points
**Why it matters:** Build something actually useful!

### 5. name_length.toml
**Concepts:** Built-in functions, len(), function arguments
**Goal:** Find the length of a name
**XP:** 100 points
**Why it matters:** Discover Python's built-in superpowers

### 6. favorite_things.toml
**Concepts:** Multiple variables, type awareness, state management
**Goal:** Create a profile with name, age, and hobby
**XP:** 125 points
**Why it matters:** Manage complex data like real programs do

### 7. mad_libs.toml
**Concepts:** String manipulation, templates, creative coding
**Goal:** Generate silly stories by combining variables
**XP:** 125 points
**Why it matters:** Learn that code can be creative and fun

### 8. guess_my_number.toml
**Concepts:** input(), type conversion, if/else, comparison operators
**Goal:** Build an interactive guessing game
**XP:** 150 points
**Why it matters:** Your first interactive program!

## Design Philosophy

### Fun First
- **Controller-native** - Designed for gamepad use
- **Encouraging** - Positive, excited tone throughout
- **Creative** - Challenges let learners express themselves
- **Interactive** - Programs that respond to user input

### Progressive Disclosure
- **Level 0-1 only** - No loops, lists, or complex structures yet
- **Prerequisites** - Each challenge builds on the previous
- **Scaffolding** - Hints go from gentle to explicit
- **Self-teaching** - Every file teaches the concepts it uses

### Emotional Checkpoints
- **Analog triggers** - RT (happy), LT (frustrated), Y (complex)
- **After milestones** - Celebrate each achievement
- **Engagement tracking** - Detect flow states and struggles

### Real-World Connection
- **Practical utilities** - Temperature converter, not toy examples
- **Professional patterns** - State management, templates, interactivity
- **Project themes** - Connect to what learners want to build

## TOML Structure

Each challenge follows this format:

```toml
[challenge]
id = "unique_id"
name = "Human-Friendly Title"
level = 0 or 1
prerequisites = ["previous_challenge"]

[description]
brief = "One-line summary"
detailed = """Multi-line explanation"""

[skeleton]
code = '''Starter template'''

[tests]
[[tests.case]]
name = "test_name"
input = []
expected = ["output"]

[hints]
level_1 = "Gentle hint"
level_4 = "Complete solution"

[gamepad_hints]
easy_mode = "Controller-specific guidance"

[solution]
code = '''Reference implementation'''

[meta]
time_limit_seconds = 300
points = 100
next_challenge = "next_id"

[adaptive]
fun_factor = "category"
weakness_signals = ["common_errors"]
project_themes = ["real_world_applications"]

[emotional_checkpoints]
after_completion = "Celebration message with [RT]/[LT]/[Y] prompts"
```

## Usage

These challenges are loaded by LMSP's challenge system:

```python
from lmsp.python.challenges import ChallengeLoader

loader = ChallengeLoader()
tutorial = loader.load_directory("challenges/tutorial")
first_challenge = tutorial.get_challenge("hello_world")
```

## Testing

Each challenge includes:
- Multiple test cases
- Input/output validation
- Edge case coverage
- Progressive hints

## Next Steps

After completing all tutorial challenges, learners unlock:
- **Level 2** - Lists, loops, and collections
- **Container challenges** - Build data structures
- **Game challenges** - More complex interactive programs

---

**Built in The Forge. Powered by Palace. For the joy of learning.**
