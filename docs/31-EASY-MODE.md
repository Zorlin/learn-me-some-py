# Easy Mode - Training Wheels for Python

**The friendly introduction:** Python verbs as single button presses.

---

## The Vision

Before players graduate to radial thumbstick typing, they need **training wheels** - a simpler input mode that teaches Python fundamentals without overwhelming them with 256 chord combinations.

Easy Mode maps **Python keywords to face buttons**, making it feel like playing a game rather than typing. Each button press inserts a Python verb and prompts for the details.

**Goal:** Get absolute beginners writing working Python code in the first 5 minutes.

---

## Core Philosophy

Easy Mode is designed around these principles:

1. **One button = One Python verb** - A button means "define a function", not "insert text 'd'"
2. **Prompts for context** - After button press, ask "What should we name this?"
3. **Smart defaults** - If they skip prompts, fill in reasonable defaults
4. **Progressive disclosure** - Start with 4 buttons, unlock more as they learn
5. **Celebrate immediately** - First code runs within 5 minutes

This mode is NOT trying to be fast. It's trying to be **confidence-building**.

---

## Complete Button Mapping

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        EASY MODE GAMEPAD MAPPING                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Face Buttons:                                                              │
│     A  → def (create function) → prompts for name                           │
│     B  → return → prompts for value                                         │
│     X  → if → prompts for condition                                         │
│     Y  → for → prompts for iterator                                         │
│                                                                              │
│   Bumpers:                                                                   │
│     LB → Undo last action                                                   │
│     RB → Smart-complete (context-aware suggestion)                          │
│                                                                              │
│   Triggers:                                                                  │
│     LT → Dedent (decrease indentation)                                      │
│     RT → Indent (increase indentation)                                      │
│                                                                              │
│   Stick Clicks:                                                              │
│     L-Click → Run code                                                      │
│     R-Click → Validate (check without running)                              │
│                                                                              │
│   D-Pad:                                                                     │
│     Up/Down   → Navigate through code lines                                 │
│     Left/Right → Move cursor within line                                    │
│                                                                              │
│   Start  → Show hint                                                        │
│   Select → Open radial menu for advanced input                              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Face Buttons (Python Verbs)

The face buttons represent the **four most common Python operations** beginners need.

### A Button: `def` (Define Function)

**Press A** → System prompts:

```
┌──────────────────────────────────────────────────────────┐
│  Creating a function!                                     │
│                                                           │
│  What should we name it?                                 │
│  (Use D-Pad + face buttons to type, or RB for default)  │
│                                                           │
│  Name: hello_                                            │
│        ^^^^^                                             │
│                                                           │
│  [A] Confirm  [B] Cancel  [RB] Use "my_function"         │
└──────────────────────────────────────────────────────────┘
```

**After naming** → System asks:

```
┌──────────────────────────────────────────────────────────┐
│  Function "hello" needs parameters.                       │
│                                                           │
│  Does it take any inputs?                                │
│                                                           │
│  [A] Yes, add parameters                                 │
│  [B] No, no parameters                                   │
│  [RB] Smart default (name)                               │
└──────────────────────────────────────────────────────────┘
```

**Result:**
```python
def hello(name):
    █  # Cursor positioned in function body, indented
```

**Smart defaults:**
- If function name suggests parameters (like `greet_person`), offer `person` as param
- If no name given, use `my_function`
- Auto-indent body after colon

### B Button: `return` (Return Value)

**Press B** → System prompts:

```
┌──────────────────────────────────────────────────────────┐
│  Returning from function!                                 │
│                                                           │
│  What value should we return?                            │
│                                                           │
│  [A] Return a value (prompts for input)                  │
│  [B] Return nothing (bare return)                        │
│  [X] Return True                                         │
│  [Y] Return False                                        │
│  [RB] Return None                                        │
└──────────────────────────────────────────────────────────┘
```

**If they choose A:**
```
┌──────────────────────────────────────────────────────────┐
│  What value should we return?                            │
│                                                           │
│  Return: result_                                         │
│          ^^^^^^^                                         │
│                                                           │
│  [A] Confirm  [B] Cancel  [RB] Smart suggest             │
└──────────────────────────────────────────────────────────┘
```

**Result:**
```python
def hello(name):
    return name█
```

**Smart defaults:**
- If there's a variable called `result` in scope, suggest it
- If function name is `is_*` or `has_*`, suggest `True`/`False`
- If no input, return `None`

### X Button: `if` (Conditional)

**Press X** → System prompts:

```
┌──────────────────────────────────────────────────────────┐
│  Creating a conditional!                                  │
│                                                           │
│  What condition should we check?                         │
│                                                           │
│  [A] Check if variable exists                            │
│  [B] Compare two values                                  │
│  [X] Check if True/False                                 │
│  [Y] Custom condition (type it)                          │
│  [RB] Smart suggest from context                         │
└──────────────────────────────────────────────────────────┘
```

**If they choose A (check if variable exists):**
```
┌──────────────────────────────────────────────────────────┐
│  Which variable should we check?                         │
│                                                           │
│  Variables in scope:                                     │
│    1. name                                               │
│    2. age                                                │
│    3. data                                               │
│                                                           │
│  [D-Pad] Select  [A] Confirm  [Y] Type custom            │
└──────────────────────────────────────────────────────────┘
```

**Result:**
```python
def hello(name):
    if name:
        █  # Cursor positioned in if block, indented
```

**Smart defaults:**
- If last statement assigned a variable, suggest checking it
- If function has parameter, suggest checking parameter
- Auto-indent if block

### Y Button: `for` (Loop)

**Press Y** → System prompts:

```
┌──────────────────────────────────────────────────────────┐
│  Creating a loop!                                         │
│                                                           │
│  What should we loop through?                            │
│                                                           │
│  [A] Loop through a list                                 │
│  [B] Loop through a range of numbers                     │
│  [X] Loop through dictionary                             │
│  [Y] Custom loop (type it)                               │
│  [RB] Smart suggest from context                         │
└──────────────────────────────────────────────────────────┘
```

**If they choose A (loop through list):**
```
┌──────────────────────────────────────────────────────────┐
│  Which list should we loop through?                      │
│                                                           │
│  Lists in scope:                                         │
│    1. data                                               │
│    2. items                                              │
│    3. numbers                                            │
│                                                           │
│  [D-Pad] Select  [A] Confirm  [Y] Type custom            │
└──────────────────────────────────────────────────────────┘
```

**Then ask for loop variable:**
```
┌──────────────────────────────────────────────────────────┐
│  What should we call each item?                          │
│                                                           │
│  Loop variable name: item_                               │
│                      ^^^^^                               │
│                                                           │
│  [A] Confirm  [B] Cancel  [RB] Use default "item"        │
└──────────────────────────────────────────────────────────┘
```

**Result:**
```python
for item in data:
    █  # Cursor positioned in loop body, indented
```

**Smart defaults:**
- If looping through `items`, suggest `item` as variable
- If looping through `numbers`, suggest `n` or `num`
- If list name is plural, suggest singular form
- Auto-indent loop body

---

## Bumpers (Edit Operations)

### LB: Undo

**Press LB** → Undo last action (statement, not character).

```
Before:
def hello():
    return "Hi"█

Press LB →

After:
def hello():
    █
```

**Undo granularity:**
- Undoes entire statements, not individual characters
- Maintains indent levels
- Preserves cursor position contextually
- Shows brief flash: "Undid: return statement"

**Undo stack:**
- Unlimited undo (until start of challenge)
- Cannot undo past challenge start
- Shows count: "Undo (3 actions available)"

### RB: Smart Complete

**Press RB** → Context-aware completion suggestion.

The system analyzes:
- Current cursor position
- Function context
- Variable scope
- Challenge requirements

And suggests the **most likely next statement**.

**Example 1: Inside empty function**
```python
def calculate():
    █

Press RB →

┌──────────────────────────────────────────────────────────┐
│  Smart Suggestion:                                        │
│                                                           │
│  result = 0                                              │
│                                                           │
│  [A] Accept  [B] Decline  [X] See alternatives           │
└──────────────────────────────────────────────────────────┘
```

**Example 2: After creating variable**
```python
def calculate(numbers):
    total = 0█

Press RB →

┌──────────────────────────────────────────────────────────┐
│  Smart Suggestion:                                        │
│                                                           │
│  for num in numbers:                                     │
│                                                           │
│  [A] Accept  [B] Decline  [X] See alternatives           │
└──────────────────────────────────────────────────────────┘
```

**Example 3: Missing return**
```python
def calculate(numbers):
    total = 0
    for num in numbers:
        total += num
    █  # Smart complete knows you need return

Press RB →

┌──────────────────────────────────────────────────────────┐
│  Smart Suggestion:                                        │
│                                                           │
│  return total                                            │
│                                                           │
│  [A] Accept  [B] Decline  [X] See alternatives           │
└──────────────────────────────────────────────────────────┘
```

**Alternative suggestions (press X):**
```
┌──────────────────────────────────────────────────────────┐
│  Other suggestions:                                       │
│                                                           │
│  1. return total          (90% confidence)               │
│  2. return total / len()  (60% confidence)               │
│  3. return None           (20% confidence)               │
│                                                           │
│  [D-Pad] Select  [A] Accept  [B] Cancel                  │
└──────────────────────────────────────────────────────────┘
```

---

## Triggers (Indentation)

Python is whitespace-sensitive. The triggers handle indentation intuitively.

### RT: Indent (Increase Indentation)

**Press RT** → Increase indent by one level (4 spaces).

```
Before:
def hello():
return "Hi"█

Press RT →

After:
def hello():
    return "Hi"█
```

**Visual feedback:**
- Indent guides show nesting level
- Flash animation on indent change
- Show current indent level: "Indent: Level 1"

### LT: Dedent (Decrease Indentation)

**Press LT** → Decrease indent by one level.

```
Before:
def hello():
    return "Hi"
    █

Press LT →

After:
def hello():
    return "Hi"
█
```

**Smart dedent:**
- Cannot dedent below level 0
- Auto-dedent after `return` (press Y to override)
- Warning if dedent creates syntax error

**Indent visualization:**
```
def hello():
│   if True:
│   │   return "Hi"
│   █
└───┴─── Indent guides
```

---

## Stick Clicks (Code Actions)

### L-Click: Run Code

**Press L-Click** → Execute current code and show results.

```
┌──────────────────────────────────────────────────────────┐
│  Running your code...                                     │
│                                                           │
│  def hello(name):                                        │
│      if name:                                            │
│          return f"Hello {name}"                          │
│      return "Hi"                                         │
│                                                           │
│  Test 1: hello("World")                                  │
│  ✓ Expected: "Hello World"                               │
│  ✓ Got: "Hello World"                                    │
│                                                           │
│  Test 2: hello("")                                       │
│  ✓ Expected: "Hi"                                        │
│  ✓ Got: "Hi"                                             │
│                                                           │
│  All tests passed! 🎉                                    │
│                                                           │
│  [A] Continue  [Y] See details                           │
└──────────────────────────────────────────────────────────┘
```

**If tests fail:**
```
┌──────────────────────────────────────────────────────────┐
│  Running your code...                                     │
│                                                           │
│  Test 1: hello("World")                                  │
│  ✓ Passed                                                │
│                                                           │
│  Test 2: hello(None)                                     │
│  ✗ Failed                                                │
│    Expected: "Hi"                                        │
│    Got: AttributeError: 'NoneType' object has no...     │
│                                                           │
│  [A] Continue  [Start] Show hint  [X] See error details  │
└──────────────────────────────────────────────────────────┘
```

**Haptic feedback:**
- Success: Double pulse (brrr-brrr)
- Failure: Long pulse (brrrrr)
- Each test: Short tick (brr)

### R-Click: Validate (Check Syntax)

**Press R-Click** → Check syntax without running.

```
┌──────────────────────────────────────────────────────────┐
│  Validating syntax...                                     │
│                                                           │
│  ✓ No syntax errors                                      │
│  ✓ All blocks properly indented                          │
│  ✓ All brackets closed                                   │
│                                                           │
│  Ready to run! (Press L-Click)                           │
│                                                           │
│  [A] Continue                                            │
└──────────────────────────────────────────────────────────┘
```

**If syntax errors:**
```
┌──────────────────────────────────────────────────────────┐
│  Syntax Error Found                                       │
│                                                           │
│  Line 3: Missing colon                                   │
│                                                           │
│  def hello()                                             │
│              ^ Expected ":" here                         │
│                                                           │
│  [A] Jump to error  [B] Cancel  [Start] Show hint        │
└──────────────────────────────────────────────────────────┘
```

**Validation checks:**
- Syntax errors (missing colons, brackets, etc.)
- Indentation errors
- Undefined variables (warnings, not errors)
- Unreachable code (warnings)
- Unused variables (hints)

---

## D-Pad (Navigation)

The D-Pad provides precise cursor control.

### Up/Down: Navigate Lines

**Press Up** → Move cursor to previous line (maintain column if possible).
**Press Down** → Move cursor to next line (maintain column if possible).

```
Before (cursor on line 2):
def hello():
    return "Hi"█

Press Up →

After (cursor on line 1):
def hello():█
    return "Hi"
```

**Smart line navigation:**
- Skip empty lines (hold LB to stop on empty)
- Jump to end of line if column doesn't exist
- Show line numbers: "Line 2/5"

### Left/Right: Move Cursor Within Line

**Press Left** → Move cursor one character left.
**Press Right** → Move cursor one character right.

```
Before:
def hello():█

Press Left (4x) →

After:
def █hello():
```

**Enhanced navigation:**
- **Hold LB + Left/Right:** Jump by word
- **Hold RB + Left/Right:** Jump to line start/end
- Wrap to previous/next line at boundaries

---

## Start/Select (Meta Actions)

### Start: Show Hint

**Press Start** → Get contextual help.

```
┌──────────────────────────────────────────────────────────┐
│  Hint                                                     │
│                                                           │
│  You need to return a value from your function.          │
│                                                           │
│  Try pressing [B] to add a return statement!             │
│                                                           │
│  [A] Thanks!  [Y] Show me an example                     │
└──────────────────────────────────────────────────────────┘
```

**Hint levels:**
- Level 1: Gentle nudge ("You need to return something")
- Level 2: More specific ("Try returning the variable 'result'")
- Level 3: Almost solution ("Use: return result")
- Level 4: Show solution (discouraged, loses points)

**If they press Y (show example):**
```
┌──────────────────────────────────────────────────────────┐
│  Example                                                  │
│                                                           │
│  def add(a, b):                                          │
│      result = a + b                                      │
│      return result  ← Like this!                         │
│                                                           │
│  [A] Got it!                                             │
└──────────────────────────────────────────────────────────┘
```

**Hint availability:**
- Unlimited hints (learning is the goal, not gatekeeping)
- Hints reduce XP slightly (but still progress)
- "Try without hints" achievements

### Select: Open Radial Menu

**Press Select** → Open radial menu for advanced input.

```
┌──────────────────────────────────────────────────────────┐
│                    RADIAL MENU                            │
│                                                           │
│         ╭───────────╮                                     │
│         │   while   │                                     │
│         │           │                                     │
│     ╭───┼───────────┼───╮                                 │
│     │ = │     ●     │ + │                                 │
│     │   │ L-STICK  │   │                                 │
│     ╰───┼───────────┼───╯                                 │
│         │   else    │                                     │
│         ╰───────────╯                                     │
│                                                           │
│  Move L-Stick to select, release Select to confirm       │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

**Radial menu contents:**
- Keywords not on face buttons (while, else, elif, pass, break, etc.)
- Operators (=, +, -, *, /, ==, !=, <, >, etc.)
- Special characters (brackets, quotes, colons, commas)

**Progressive unlock:**
- Start with 8 items (most basic)
- Unlock more as concepts are learned
- Current level shown: "Radial Level 2/5"

---

## Complete Workflow Example

Let's walk through creating a complete function using Easy Mode:

### Challenge: Create a function that sums a list of numbers

**Step 1: Create function**
- Press **A** (def)
- Type name: "sum_list" (using D-Pad/radial)
- Confirm
- Press **A** for parameters
- Type: "numbers"
- Confirm

```python
def sum_list(numbers):
    █
```

**Step 2: Initialize result**
- Press **RB** (smart complete)
- Suggests: "result = 0"
- Press **A** (accept)

```python
def sum_list(numbers):
    result = 0
    █
```

**Step 3: Loop through numbers**
- Press **Y** (for loop)
- Choose [A] (loop through list)
- Select "numbers" from scope
- Loop variable: "num" (or press RB for default)
- Confirm

```python
def sum_list(numbers):
    result = 0
    for num in numbers:
        █
```

**Step 4: Add to result**
- Type "result" (D-Pad + radial, or RB suggest)
- Press **Select** → Radial menu
- Select "+="
- Type "num"
- Press **LT** (dedent - exit loop)

```python
def sum_list(numbers):
    result = 0
    for num in numbers:
        result += num
    █
```

**Step 5: Return result**
- Press **B** (return)
- Choose [A] (return value)
- Type "result" (or RB suggests it)
- Confirm

```python
def sum_list(numbers):
    result = 0
    for num in numbers:
        result += num
    return result█
```

**Step 6: Test**
- Press **L-Click** (run)
- All tests pass!
- Celebrate! 🎉

**Total actions:** ~15 button presses (vs ~80 for typing on keyboard)

---

## Progression to Radial Mode

Easy Mode is explicitly **training wheels** - designed to be outgrown.

### Unlock Conditions for Radial Mode

After completing certain milestones:

**Milestone 1: Completed 5 challenges**
```
┌──────────────────────────────────────────────────────────┐
│  Achievement Unlocked!                                    │
│                                                           │
│  You've completed 5 challenges in Easy Mode!             │
│                                                           │
│  Radial Typing is now available.                         │
│                                                           │
│  Radial typing is MUCH faster once you learn it.         │
│  Want to try the tutorial?                               │
│                                                           │
│  [A] Yes, let's learn!  [B] Not yet, stay in Easy Mode   │
└──────────────────────────────────────────────────────────┘
```

**Milestone 2: Completed 10 challenges (gentle push)**
```
┌──────────────────────────────────────────────────────────┐
│  You're getting really good at Easy Mode!                │
│                                                           │
│  Radial typing would let you code 3x faster.             │
│  Plus it's super satisfying once you get it.             │
│                                                           │
│  Try just ONE challenge in Radial Mode?                  │
│                                                           │
│  [A] Okay, one challenge  [B] Not yet                    │
└──────────────────────────────────────────────────────────┘
```

**Milestone 3: Completed 20 challenges (stronger push)**
```
┌──────────────────────────────────────────────────────────┐
│  You've mastered Easy Mode!                              │
│                                                           │
│  But Easy Mode is designed to be slow and clear.         │
│  You're ready for Radial Mode now.                       │
│                                                           │
│  Let's graduate! (You can always switch back)            │
│                                                           │
│  [A] Let's do this!  [B] Just a few more in Easy Mode    │
└──────────────────────────────────────────────────────────┘
```

### Switching Between Modes

**Anytime:** Press **Select + Start** simultaneously to toggle modes.

```
┌──────────────────────────────────────────────────────────┐
│  Switch Input Mode?                                       │
│                                                           │
│  Current: Easy Mode                                      │
│                                                           │
│  [A] Switch to Radial Mode                               │
│  [B] Stay in Easy Mode                                   │
│  [X] Try Radial for just this challenge                  │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

**Per-challenge mode:**
- Can switch mid-challenge (progress preserved)
- Mode preference saved per-player
- Statistics tracked separately for each mode

---

## Accessibility Features

### Colorblind Support

Alternative visual indicators:
- Icons instead of colors for button prompts
- High contrast text
- Pattern-coded buttons

### Motor Assistance

For players with limited dexterity:
- Slower button repeat rate (hold to repeat)
- Sticky modifiers (tap LB/RB to toggle instead of hold)
- One-handed mode (remap buttons to triggers)

### Cognitive Support

For players new to programming:
- "Explain this" option on every prompt
- Visual code flow diagrams
- Glossary of terms (press Start + Select)

---

## Learning Metrics

### Success Indicators

Players are ready to graduate from Easy Mode when:

| Metric                          | Target        | Why Important                     |
|---------------------------------|---------------|-----------------------------------|
| Challenges completed            | 15+           | Familiarity with Python concepts  |
| Average time per challenge      | <5 min        | Not overthinking each action      |
| Hints used per challenge        | <2            | Understanding concepts            |
| Undo actions per challenge      | <5            | Making intentional choices        |
| Smart complete acceptance rate  | >50%          | Understanding suggestions         |
| Syntax errors per challenge     | <3            | Understanding Python structure    |

### Common Learning Patterns

**Week 1:**
- Heavy button mashing (exploration)
- Many undos (trial and error)
- Lots of hints (learning)
- Slow but steady progress

**Week 2:**
- Intentional button presses
- Fewer undos (thinking first)
- Fewer hints (remembering concepts)
- Faster completion times

**Week 3:**
- Muscle memory forming
- Smart complete feels intuitive
- Ready for Radial Mode

---

## Implementation Notes

### Button State Machine

```python
class EasyModeController:
    def __init__(self):
        self.state = ControllerState.WAITING_INPUT
        self.prompt_stack = []
        self.code_buffer = []

    def handle_button(self, button: Button):
        """Route button press to appropriate handler."""
        if self.state == ControllerState.IN_PROMPT:
            return self.handle_prompt_input(button)

        match button:
            case Button.A:
                return self.handle_def()
            case Button.B:
                return self.handle_return()
            case Button.X:
                return self.handle_if()
            case Button.Y:
                return self.handle_for()
            case Button.LB:
                return self.handle_undo()
            case Button.RB:
                return self.handle_smart_complete()
            # ... etc

    def handle_def(self):
        """Handle function definition (A button)."""
        prompt = PromptDialog(
            question="What should we name the function?",
            default="my_function",
            suggestions=self.get_smart_suggestions("function_name")
        )
        self.prompt_stack.append(prompt)
        self.state = ControllerState.IN_PROMPT
```

### Smart Completion Engine

```python
class SmartCompleter:
    def __init__(self, claude_api):
        self.claude = claude_api

    def suggest_next(self, context: CodeContext) -> list[Suggestion]:
        """Generate smart suggestions based on context."""
        # Analyze current code state
        analysis = self.analyze_context(context)

        # Get Claude's suggestions
        suggestions = self.claude.complete(
            code=context.code,
            cursor=context.cursor,
            challenge=context.challenge
        )

        # Rank by confidence
        ranked = self.rank_suggestions(suggestions, analysis)

        return ranked[:3]  # Top 3
```

---

## Summary

Easy Mode makes Python coding **accessible and fun** for absolute beginners:

- **One button = One Python verb** - Clear mental model
- **Smart defaults** - Reasonable choices without overwhelm
- **Progressive prompts** - Guide without overwhelming
- **Immediate feedback** - Run code in 5 minutes
- **Training wheels** - Designed to be outgrown

It's not fast. It's not for experts. It's for **confidence building** - proving that YOU can write code, even if you've never seen Python before.

And when you're ready, Radial Mode awaits with 3x the speed and the satisfaction of true mastery.

---

*Part of the LMSP Input Systems documentation.*
