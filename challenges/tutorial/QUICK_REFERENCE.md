# Tutorial Challenges - Quick Reference

## Learning Path

```
Level 0 (Basics)
  ↓
hello_world.toml (50 XP)
  → Print "Hello, World!"
  → Concepts: print(), strings
  ↓
personal_greeting.toml (75 XP)
  → Print greeting with variable
  → Concepts: variables, f-strings
  ↓
simple_math.toml (75 XP)
  → Calculate 42 + 58
  → Concepts: arithmetic, numbers
  ↓
Level 1 (Intermediate)
  ↓
temperature_converter.toml (100 XP)
  → Convert F to C
  → Concepts: order of ops, round()
  ↓
name_length.toml (100 XP)
  → Find length of name
  → Concepts: len(), built-in functions
  ↓
favorite_things.toml (125 XP)
  → Create profile (name, age, hobby)
  → Concepts: multiple variables, types
  ↓
mad_libs.toml (125 XP)
  → Generate silly stories
  → Concepts: string templates, creativity
  ↓
guess_my_number.toml (150 XP)
  → Interactive guessing game
  → Concepts: input(), if/else, comparison
  ↓
Level 2+ (Coming Soon)
```

## Concept Map

### Level 0 Fundamentals
| Concept | Introduced In | Used In |
|---------|---------------|---------|
| `print()` | hello_world | all challenges |
| String literals | hello_world | all challenges |
| Variables | personal_greeting | all after |
| Assignment (`=`) | personal_greeting | all after |
| Arithmetic (`+`, `-`, `*`, `/`) | simple_math | all after |
| Numbers vs strings | simple_math | all after |

### Level 1 Expansion
| Concept | Introduced In | Used In |
|---------|---------------|---------|
| Order of operations | temperature_converter | all after |
| `round()` function | temperature_converter | - |
| `len()` function | name_length | - |
| Built-in functions | name_length | all after |
| Multiple variables | favorite_things | all after |
| f-strings | personal_greeting | all after |
| String concatenation | personal_greeting, mad_libs | - |
| `input()` function | guess_my_number | - |
| Type conversion (`int()`) | guess_my_number | - |
| Comparison (`==`) | guess_my_number | - |
| `if/else` | guess_my_number | - |

## XP Progression

```
Challenge                XP    Cumulative
─────────────────────────────────────────
hello_world              50         50
personal_greeting        75        125
simple_math              75        200
temperature_converter   100        300
name_length             100        400
favorite_things         125        525
mad_libs                125        650
guess_my_number         150        800
─────────────────────────────────────────
TOTAL                   800        800
```

## Speed Run Targets

For competitive players:

| Challenge | Time Limit | Speed Target | Difficulty |
|-----------|-----------|--------------|------------|
| hello_world | 5 min | 30s | ⭐ |
| personal_greeting | 5 min | 45s | ⭐ |
| simple_math | 5 min | 40s | ⭐ |
| temperature_converter | 6.7 min | 60s | ⭐⭐ |
| name_length | 5 min | 45s | ⭐⭐ |
| favorite_things | 6.7 min | 60s | ⭐⭐ |
| mad_libs | 6.7 min | 60s | ⭐⭐ |
| guess_my_number | 8.3 min | 90s | ⭐⭐⭐ |

## Test Coverage

Each challenge includes multiple test cases:

- **hello_world**: 1 test (exact output)
- **personal_greeting**: 3 tests (different names)
- **simple_math**: 1 test (arithmetic)
- **temperature_converter**: 3 tests (body temp, freezing, boiling)
- **name_length**: 3 tests (different name lengths)
- **favorite_things**: 3 tests (complete profiles)
- **mad_libs**: 3 tests (different story variations)
- **guess_my_number**: 3 tests (correct, wrong, another wrong)

**Total:** 20 test cases across 8 challenges

## Weakness Signals

Common errors the adaptive system watches for:

### Level 0
- `syntax_error` - Basic Python syntax mistakes
- `wrong_quotes` - Using wrong quote types
- `forgot_print` - Missing print() call
- `forgot_quotes` - Strings without quotes
- `concatenation_error` - Wrong string joining
- `variable_not_defined` - Using undefined variables
- `quotes_around_numbers` - Treating numbers as strings
- `no_calculation` - Not performing math
- `wrong_operator` - Using wrong operator

### Level 1
- `order_of_operations` - Wrong precedence
- `forgot_round` - Not rounding decimals
- `wrong_formula` - Incorrect calculation
- `forgot_len` - Not using len()
- `wrong_format_string` - f-string errors
- `hardcoded_number` - Not using variables
- `mixed_types` - Type confusion
- `forgot_variable` - Missing variable
- `forgot_int_conversion` - input() not converted
- `wrong_comparison_operator` - Using = instead of ==
- `indentation_error` - Python indentation mistakes

## Project Themes

Real-world applications these challenges connect to:

### CLI Tools & Automation
- hello_world → CLI tools
- personal_greeting → User interfaces
- simple_math → Calculators
- temperature_converter → Unit converters

### Interactive Apps
- name_length → Form validation
- favorite_things → User profiles
- mad_libs → Text generators
- guess_my_number → Games, quizzes

### Domain-Specific
- simple_math → Finance apps, game scores
- temperature_converter → Science apps, weather tools
- name_length → Password validators, tweet counters
- mad_libs → Chatbots, creative writing tools

## Emotional Checkpoints

All challenges include analog trigger feedback:

**RT (Right Trigger)** - Pull for happiness/satisfaction
- "I get it!"
- "This is fun!"
- "I love this!"

**LT (Left Trigger)** - Pull for frustration/confusion
- "Too easy"
- "Still confused"
- "More challenges!"

**Y Button** - Complex/mixed feelings
- "Tell me more"
- "Show me more"
- "What else can I build?"

## Integration Notes

### For Challenge Loader
```python
from lmsp.python.challenges import ChallengeLoader

loader = ChallengeLoader()
tutorials = loader.load_directory("challenges/tutorial")

# Get specific challenge
challenge = tutorials.get_challenge("hello_world")

# Get by level
level_0 = [c for c in tutorials if c.level == 0]
level_1 = [c for c in tutorials if c.level == 1]

# Get prerequisite chain
chain = tutorials.get_prerequisite_chain("guess_my_number")
# Returns: [hello_world, personal_greeting, simple_math, temperature_converter,
#           name_length, favorite_things, mad_libs, guess_my_number]
```

### For Test Runner
```python
from lmsp.python.test_runner import TestRunner

runner = TestRunner(challenge)
results = runner.run_all_tests(user_code)

for test in results:
    print(f"{test.name}: {'✓' if test.passed else '✗'}")
```

### For Adaptive System
```python
from lmsp.adaptive.learner import AdaptiveLearner

learner = AdaptiveLearner()

# Track completion
learner.complete_challenge("hello_world",
    time_spent=45,
    hints_used=1,
    attempts=2,
    emotion_rt=0.8,  # Happy!
    emotion_lt=0.1   # Not frustrated
)

# Get next suggestion
next_challenge = learner.suggest_next()
```

---

**Quick Reference Version 1.0**
*Agent 5 - LMSP Documentation Sprint*
