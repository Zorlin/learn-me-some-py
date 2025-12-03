# LMSP Quickstart Guide

**Time to completion:** 5-10 minutes

**Prerequisites:** Python 3.10+ installed

**Next:** [Vision & Philosophy](00-VISION.md)

---

## What You'll Learn

In this quickstart, you'll:
1. Set up LMSP on your machine
2. Complete your first Python challenge
3. Experience the adaptive learning engine
4. (Optional) Try controller input

By the end, you'll understand how LMSP feels different from traditional coding tutorials.

---

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/palace/learn-me-some-py.git
cd learn-me-some-py
```

### Step 2: Create a Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### Step 3: Install Dependencies

```bash
pip install -e ".[dev]"
```

This installs LMSP in "editable" mode so you can modify the code later (that's part of the learning!).

The `[dev]` suffix includes development tools like pytest for running tests.

---

## Your First Challenge

### Launch LMSP

```bash
python -m lmsp
```

You'll see a welcome screen:

```
╔════════════════════════════════════════╗
║  Learn Me Some Py - v0.1.0             ║
║  The game that teaches you to build it ║
╚════════════════════════════════════════╝

Welcome! Creating your profile...
Player ID: default

What would you like to learn today?
```

### Challenge: Container Add/Exists

**The Game Says:**

```
Challenge: Container - Add and Exists
Level: 2 (Beginner)
Points: 100
Prerequisites: lists, in operator

Build a container that can:
  - Add values
  - Check if values exist

Example:
  queries = [["ADD", "1"], ["EXISTS", "1"]]
  → ["", "true"]

Press Enter to start, or type 'hint' for help.
```

**Your Turn:**

The game presents skeleton code:

```python
def solution(queries):
    # Your code here
    pass
```

Let's solve it step by step:

```python
def solution(queries):
    container = []  # Create empty list
    results = []     # Store results

    for command, value in queries:
        if command == "ADD":
            container.append(value)
            results.append("")
        elif command == "EXISTS":
            if value in container:
                results.append("true")
            else:
                results.append("false")

    return results
```

**Hit Run** (Enter key or gamepad Start button)

### What Happens Next

The game runs your code against test cases:

```
Running tests...

✓ Test 1: [["ADD", "1"], ["EXISTS", "1"]] - PASSED
✓ Test 2: [["ADD", "1"], ["ADD", "2"], ["EXISTS", "3"]] - PASSED
✓ Test 3: [["EXISTS", "1"], ["ADD", "1"], ["EXISTS", "1"]] - PASSED

🎉 Challenge Complete! +100 XP

Time: 2:34
Hints used: 0

Mastery: UNLOCKED → PRACTICED (1/3 challenges)
```

### Emotional Feedback

Now comes the magic. The game asks:

```
How did that feel?

[RT ░░░░░░░░░░] Pull right for happiness
[LT ░░░░░░░░░░] Pull left for frustration
[Y] Complex response

Press A to confirm
```

**On Keyboard:** Use arrow keys (right = happy, left = frustrated)

**On Gamepad:** Actually pull the triggers!

Let's say you pull RT about 70% (you enjoyed it):

```
[RT ███████░░░] 0.7 - Pretty satisfying!

Recorded. The adaptive engine learns you enjoyed this.
```

The game now knows you like this TYPE of challenge. It will suggest similar ones.

---

## What Just Happened?

### 1. You Wrote Real Code

Not multiple choice. Not drag-and-drop. **Real Python** that executed and passed tests.

### 2. Instant Feedback

You saw immediately if your code worked. No waiting for a tutor to grade it.

### 3. Emotional Input

The game captured a continuous measure (0.7) not binary (like/dislike). This helps it learn YOUR preferences.

### 4. XP & Progression

You earned 100 XP and increased mastery of "lists" and "in operator". This opens new challenges.

---

## The Adaptive Engine at Work

After completing a challenge, check what's recommended:

```bash
lmsp --profile
```

You'll see:

```
Player Profile: default
===================

XP: 100
Level: 2
Session time: 2:34

Concept Mastery:
  lists: ██░░░ PRACTICED (1/4 challenges)
  in_operator: ██░░░ PRACTICED (1/4)
  functions: █░░░░ UNLOCKED (0/4)

Fun Profile:
  Enjoys: puzzle challenges (0.70)
  Flow triggers: quick feedback, clear goals
  Optimal session: 20-25 minutes

Next Recommended: container_remove
Reason: Continue the container pattern, matches fun profile
```

The adaptive engine has learned:
- You like puzzles (based on 0.7 enjoyment)
- You enjoy quick feedback loops (fast completion)
- Your optimal session length is 20-25 min
- You're ready for the next container challenge

**This personalization happens automatically.**

---

## Controller Input (Optional)

If you have an Xbox/PlayStation/Switch Pro controller:

```bash
python -m lmsp --input gamepad
```

You'll see:

```
Gamepad detected: Xbox Series Controller

Tutorial: Easy Mode
===================

Face Buttons:
  A: Create function (def ___():)
  B: Return statement
  X: If statement
  Y: For loop

Bumpers:
  LB: Undo
  RB: Smart complete

Triggers:
  LT: Dedent (decrease indentation)
  RT: Indent (increase indentation)

Start: Run code
Select: Hint

Ready? Press Start.
```

### Easy Mode Example

**Try solving the same challenge with controller:**

1. Press `A` → Creates `def solution(queries):`
2. Press `Y` → Starts a for loop
3. Use D-pad to navigate and fill in details
4. Press `RB` (smart complete) → Suggests common patterns
5. Press `Start` to run

It feels like playing a game, not writing code!

### Radial Typing (Advanced)

After a few challenges, you can enable radial typing:

```
         ╭───────────╮                    ╭───────────╮
         │     ↑     │                    │     ↑     │
         │   (def)   │                    │  (space)  │
         │           │                    │           │
     ╭───┼───────────┼───╮            ╭───┼───────────┼───╮
     │ ← │     ●     │ → │            │ ← │     ●     │ → │
     │(if)│ L-STICK  │(in)│            │(:) │ R-STICK  │(=) │
     │   │           │   │            │   │           │   │
     ╰───┼───────────┼───╯            ╰───┼───────────┼───╯
         │     ↓     │                    │     ↓     │
         │ (return)  │                    │  (enter)  │
         ╰───────────╯                    ╰───────────╯

CHORD EXAMPLES:
  L-Up + R-Up       = "def"
  L-Up + R-Right    = "def "
  L-Left + R-Right  = "if "
  L-Down + R-Down   = newline + auto-indent
```

This allows fast Python input using muscle memory!

---

## Understanding Progression

LMSP uses a Directed Acyclic Graph (DAG) for concept progression:

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
    │ │   for_loops   │ │  │   │  │ │ in_operator │ │
    │ └───────────────┘ │  │   │  │ └─────────────┘ │
    └───────────────────┘  └───┘  └─────────────────┘
                                           │
                    ┌──────────────────────┘
                    │
          ┌─────────▼─────────┐
          │     Level 3       │
          │ ┌───────────────┐ │
          │ │   functions   │ │
          │ └───────┬───────┘ │
          │         │         │
          │ ┌───────▼───────┐ │
          │ │     scope     │ │
          │ └───────────────┘ │
          └───────────────────┘
```

Concepts unlock based on prerequisites, not linear order. This means:
- You can learn at your own pace
- Skip what you already know
- Focus on what you need for your project

---

## Mastery Levels

Each concept has 5 mastery levels:

```
Level 0: SEEN
  └─ Concept appears in tree but is locked
  └─ "You'll learn this after mastering: [prerequisites]"

Level 1: UNLOCKED
  └─ Can attempt challenges
  └─ Hints available at all levels
  └─ No time pressure

Level 2: PRACTICED
  └─ Completed 3+ challenges
  └─ Hints available but discouraged
  └─ Gentle time suggestions

Level 3: MASTERED
  └─ Completed all challenges
  └─ Achieved speed run time on at least one
  └─ Can use in higher-level challenges

Level 4: TRANSCENDED
  └─ Can explain to AI students (teaching mode)
  └─ Unlocks ability to teach this concept
  └─ Community content creation unlocked
```

---

## Project-Driven Learning

Want to learn for a specific goal? Tell the game!

```bash
python -m lmsp --project "Discord bot"
```

It will analyze what concepts you need and generate a personalized curriculum:

```
Project: Discord bot
==================

Required Concepts:
  Level 2: Lists, Dicts (for storing data)
  Level 3: Functions (for bot commands)
  Level 4: Async/await (for Discord API)
  Level 5: Classes (for bot structure)

Generating themed challenges...
✓ 15 challenges created around Discord bots
✓ Curriculum ready

Estimated time: 12-15 hours over 2-3 weeks

[Press Enter to start]
```

All challenges will be themed around Discord bots:
- "Store bot commands in a list"
- "Check if user has permission"
- "Parse command arguments"

You're not learning abstract concepts - you're building toward YOUR goal.

---

## Common First Reactions

### "This is fun!"

Perfect! That's the whole point. Learning should feel like playing.

### "I'm stuck on a challenge"

Hit `Select` (or type `hint`). You'll get progressive hints:

```
Hint 1/4: You'll need to use a list to store values
Hint 2/4: The 'in' operator checks membership in a list
Hint 3/4: Try: if value in container:
Hint 4/4: [Full solution revealed]
```

The adaptive engine tracks how many hints you use and adjusts future difficulty.

### "The controller feels weird"

That's normal! Radial typing has a learning curve. Stick with "Easy Mode" (button-based) for the first few challenges. Most players transition naturally after 5-10 challenges.

### "I want to skip basics"

Use the skip command:

```bash
python -m lmsp --skip-to level:3
```

This marks all Level 0-2 concepts as MASTERED and starts you at functions.

---

## What Makes LMSP Different?

### Traditional Tutorial:

```
1. Read about lists
2. Read about syntax
3. Read about the 'in' operator
4. Try an exercise (maybe)
5. Move to next topic whether you understood or not
```

**Result:** Passive, boring, no feedback on whether you're enjoying it.

### LMSP:

```
1. Try to solve a challenge
2. Get immediate feedback (tests pass/fail)
3. Express how it felt (analog emotional input)
4. Game adapts to you
5. Suggests what's next based on your progress AND enjoyment
```

**Result:** Active, engaging, personalized to YOUR brain.

---

## Troubleshooting

### Game won't launch

```bash
# Check Python version (need 3.10+)
python --version

# Reinstall dependencies
pip install --force-reinstall -e ".[dev]"
```

### Controller not detected

```bash
# Install pygame for gamepad support
pip install pygame

# Test detection
python -m lmsp --input gamepad --test-controller
```

### Tests failing unexpectedly

Some challenges expect specific output format. Read the test case carefully:

```
Expected: ["", "true"]
Your output: ["", True]
           ↑ String "true", not boolean True!
```

LMSP teaches precise Python - string vs boolean matters!

### Want to reset progress

```bash
# Reset your profile (WARNING: deletes all progress)
python -m lmsp --reset

# Or start a new profile
python -m lmsp --profile mynewprofile
```

---

## Next Steps

### Keep Playing

The best way to learn is to keep solving challenges. The game will guide you through:

- **Level 0:** Print, variables, strings
- **Level 1:** If/else, loops, match/case
- **Level 2:** Lists, in operator, sorted
- **Level 3:** Functions, parameters, scope
- **Level 4:** Comprehensions, lambda, min/max
- **Level 5:** Classes, methods, self
- **Level 6:** Advanced patterns

### Try Multiplayer

Once you're comfortable:

```bash
python -m lmsp --multiplayer --mode coop
```

Solve challenges collaboratively with AI or human players.

**Available modes:**
- **COOP:** Shared cursor, solve together
- **RACE:** Same problem, first to pass wins
- **TEACH:** Teach AI students (best way to solidify learning)
- **SWARM:** Watch multiple AIs solve different ways
- **SPECTATE:** Watch AI solve with real-time explanations

### Read the Docs

- **[Vision & Philosophy](00-VISION.md)** - Why LMSP exists
- **[ULTRASPEC.md](/mnt/castle/garage/learn-me-some-py/ULTRASPEC.md)** - Complete technical specification

### Build LMSP

Remember: LMSP is written in Python. As you progress, you'll read the source code of the game that taught you. Eventually, you can contribute improvements!

```bash
# View the source of the adaptive engine
cat lmsp/adaptive/engine.py

# Run the test suite
pytest tests/

# Make a change and test it
pytest tests/test_adaptive.py -v
```

This is the meta-game: learning Python by building the Python learning game.

---

## The First Session Goal

**Don't try to "complete" anything.** Just play for 20-30 minutes and see how it feels.

Success = You enjoyed it and learned something.

If you looked up and 30 minutes had passed without you noticing, **the game is working**.

---

## Development Commands (For Contributors)

If you want to contribute to LMSP itself:

```bash
# Setup
cd /mnt/castle/garage/learn-me-some-py
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Testing
pytest tests/ -v                        # Run all tests
pytest tests/test_emotional.py -v      # Specific test file
pytest --cov=lmsp --cov-report=html    # Coverage report

# Running
python -m lmsp                         # Start game
python -m lmsp --input gamepad         # With controller
python -m lmsp --multiplayer --mode coop  # Multiplayer
```

---

**Prerequisites:** Python 3.10+ installed

**Next:** [Vision & Philosophy](00-VISION.md) - Understand the philosophy

---

*Built in The Forge. Powered by Palace. For the joy of learning.*

**Ready to begin? Run `python -m lmsp` and let's play.**
