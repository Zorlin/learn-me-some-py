# LMSP: Learn Me Some Python
## The Ultimate Python Learning System Specification

**Version**: 1.0.0-ultrathink
**Codename**: Project Dopamine
**Philosophy**: *Learning should feel like playing your favorite game*

---

# Part I: Vision & Philosophy

## 1.1 The Problem with Coding Education

Every existing coding education platform makes the same fundamental mistake: they treat learning as work to be endured rather than play to be enjoyed. Codecademy, freeCodeCamp, LeetCode - they all share the same dreary paradigm:

- Linear progression through arbitrary content
- No emotional feedback loop
- One-size-fits-all difficulty
- Keyboard-only input (excluding millions of potential learners)
- Passive consumption masquerading as active learning
- Zero multiplayer, zero collaboration, zero competition
- No connection between what you're learning and what you want to build

**LMSP rejects all of this.**

## 1.2 The LMSP Philosophy

### Core Tenets

1. **Fun is the Metric** - If a learner isn't enjoying themselves, the system has failed, not the learner. We measure dopamine, not just correctness.

2. **Input Freedom** - Learning Python shouldn't require a keyboard. Gamepad, touchscreen, tablet, voice - every input modality unlocks new learners.

3. **Adaptive Intelligence** - The system learns YOU faster than you learn Python. Your frustration patterns, flow states, preferred challenge types, optimal session lengths.

4. **Social by Default** - Humans learn better together. 1-4 players, AI companions, teachers, competitors - learning is multiplayer.

5. **Build What You Want** - "I want to make a Discord bot" → Here's your personalized curriculum, generated backwards from your goal.

6. **Recursive Self-Improvement** - LMSP is written in Python. You learn Python by building the system that teaches Python. The curriculum IS the product.

### The Rocksmith Insight

Rocksmith 2014 proved that you can learn a genuinely difficult skill (guitar) through pure play. No theory sections. No "watch this video." Just: plug in your guitar, play along, get better. The game adapts to you in real-time, making songs easier or harder measure by measure.

LMSP applies this insight to programming:
- Real code, real execution, real results
- Difficulty adapts in real-time to your performance
- Multiplayer where you code alongside friends
- The feedback loop is tight enough to induce flow

## 1.3 Target Outcomes

### Primary Goal: CodeSignal Mastery
LMSP is specifically designed to prepare learners for CodeSignal-style automated technical screens:

- Container operations (add, remove, exists, get_next)
- List comprehensions and filtering
- Lambda functions with key= parameters
- Integer division, modulo, type conversion
- Match/case dispatch patterns
- Class syntax with self
- Progressive difficulty across 4 levels
- 90-minute time pressure simulation

### Secondary Goals
- Joy in programming
- Foundation for any Python career path
- Community of learners who help each other
- Open source contributions to LMSP itself (you graduate by improving the system)

---

# Part II: Input Systems

## 2.1 Radial Thumbstick Typing

The crown jewel of LMSP's input innovation. A novel text input system designed for gamepads that makes coding feel like casting spells.

### Core Concept

Each thumbstick has 8 directional zones plus center (9 positions). With two thumbsticks:
- 9 × 9 = 81 unique chord combinations
- With modifier buttons (LB, RB): 81 × 4 = 324 combinations
- More than enough for all Python syntax

### Layout Design

```
        UP                              UP
    ╱       ╲                      ╱       ╲
  UL   [L]   UR                  UL   [R]   UR
  |  CENTER  |                   |  CENTER  |
  DL   [L]   DR                  DL   [R]   DR
    ╲       ╱                      ╲       ╱
       DOWN                          DOWN

L-Stick: Primary character selection
R-Stick: Secondary character / modifier

Examples:
  L-UP + R-UP     = 'd'
  L-UP + R-RIGHT  = 'e'
  L-UP + R-DOWN   = 'f'
  
  Combined: L-UP→R-UP→R-RIGHT→R-DOWN = "def"
```

### Character Mapping (Frequency-Optimized)

**Tier 1: Most Common (Single stick movement)**
```
L-CENTER + R-CENTER = SPACE
L-UP + R-CENTER     = 'e' (most common letter)
L-RIGHT + R-CENTER  = 't'
L-DOWN + R-CENTER   = 'a'
L-LEFT + R-CENTER   = 'o'
L-CENTER + R-UP     = 'i'
L-CENTER + R-RIGHT  = 'n'
L-CENTER + R-DOWN   = 's'
L-CENTER + R-LEFT   = 'r'
```

**Tier 2: Common (Diagonal combinations)**
```
L-UP + R-UP         = 'd'
L-UP + R-RIGHT      = 'l'
L-UP + R-DOWN       = 'c'
L-UP + R-LEFT       = 'u'
L-RIGHT + R-UP      = 'm'
L-RIGHT + R-RIGHT   = 'p'
... (full mapping in data/radial_layout.toml)
```

**Tier 3: Python-Specific Tokens (With RB modifier)**
```
RB + L-UP           = 'def '
RB + L-RIGHT        = 'return '
RB + L-DOWN         = 'if '
RB + L-LEFT         = 'else:'
RB + L-UP-RIGHT     = 'for '
RB + L-DOWN-RIGHT   = 'while '
RB + L-DOWN-LEFT    = 'class '
RB + L-UP-LEFT      = 'import '
```

**Tier 4: Symbols (With LB modifier)**
```
LB + L-UP           = '('
LB + L-DOWN         = ')'
LB + L-RIGHT        = '['
LB + L-LEFT         = ']'
LB + L-UP + R-UP    = '{'
LB + L-DOWN + R-DOWN = '}'
LB + L-CENTER       = ':'
LB + R-CENTER       = '='
LB + L-UP + R-CENTER = '=='
```

### Visual Feedback

```
┌─────────────────────────────────────────┐
│                                          │
│     [Current Input Display]              │
│     def calculate_sum                    │
│         ▲                                │
│         │ cursor                         │
│                                          │
│  ┌─────────┐          ┌─────────┐       │
│  │    d    │          │  SPACE  │       │
│  │  u   e  │          │  i   n  │       │
│  │    f    │          │    s    │       │
│  │  c   l  │          │  r   _  │       │
│  └─────────┘          └─────────┘       │
│   L-STICK              R-STICK          │
│                                          │
│  [RB]: Python keywords  [LB]: Symbols   │
└─────────────────────────────────────────┘
```

### Haptic Feedback

- **Valid chord**: Light pulse confirming character input
- **Invalid chord**: Double buzz indicating no mapping
- **Word completion**: Rolling wave (like typing "return" completes)
- **Line completion**: Strong pulse
- **Syntax error detected**: Rapid triple buzz
- **Syntax valid**: Smooth confirmation wave

### Learning Curve Progression

1. **Day 1**: Hunt-and-peck with visual overlay always visible
2. **Week 1**: Common letters without looking, overlay for symbols
3. **Week 2**: Full alphabet fluent, Python keywords by muscle memory
4. **Month 1**: 15-20 WPM, competitive with phone typing
5. **Month 3**: 30+ WPM, full coding fluency

### Accessibility Features

- **One-handed mode**: Single stick with time-based disambiguation
- **Eye tracking integration**: Gaze selects from radial menu
- **Voice hybrid**: "def" spoken + thumbstick for variable names
- **Customizable layouts**: Remap any chord to any character

## 2.2 Easy Mode (Python Verbs as Buttons)

For learners who aren't ready for full typing, Easy Mode maps Python concepts directly to gamepad buttons.

### Button Mapping

```
┌─────────────────────────────────────────────────────────┐
│                         EASY MODE                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│     [LB] Previous          [RB] Smart Complete           │
│      Undo last             Context-aware fill            │
│                                                          │
│              [Y] For Loop                                │
│         Creates: for ___ in ___:                         │
│                                                          │
│   [X] If Statement              [B] Return               │
│   Creates: if ___:              Creates: return ___      │
│                                                          │
│              [A] Function                                │
│         Creates: def ___():                              │
│                                                          │
│   [D-PAD UP/DOWN] Navigate suggestions                   │
│   [D-PAD LEFT/RIGHT] Navigate code                       │
│                                                          │
│   [L-STICK] Scroll code    [R-STICK] Select from radial │
│   [LT] Dedent              [RT] Indent                   │
│   [START] Run Code         [SELECT] Show Hint            │
│   [L-CLICK] Validate       [R-CLICK] Toggle overlay      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Smart Complete (RB) Intelligence

RB doesn't just autocomplete - it predicts what you need:

```python
# Context: Empty function body
def calculate_sum(numbers):
    |  # cursor here
    
# RB pressed → suggests:
# 1. total = 0          (accumulator pattern detected)
# 2. result = []        (list building pattern)
# 3. for item in numbers:  (iteration likely)

# Context: Inside a for loop with accumulator
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        |  # cursor here

# RB pressed → suggests:
# 1. total += num       (accumulator update)
# 2. if num > 0:        (conditional accumulation)
# 3. total = total + num (explicit version)
```

### Easy Mode Progression

**Stage 1: Button-Only**
- All code generated via button presses
- User fills in blanks with D-pad selection
- Focus: Understanding structure

**Stage 2: Hybrid**
- Buttons for structure (def, if, for)
- Radial typing for names and values
- Focus: Bridging to real typing

**Stage 3: Radial-Primary**
- Easy mode buttons for speed
- Radial typing for everything else
- Focus: Efficiency

**Stage 4: Full Radial**
- Easy mode disabled (or optional shortcuts)
- Full radial typing fluency
- Focus: Mastery

## 2.3 Touchscreen Mode (Duolingo-Style)

For mobile/tablet learners who want bite-sized lessons.

### Interaction Patterns

**Drag-and-Drop Code Construction**
```
┌─────────────────────────────────────────┐
│  Build the function:                     │
│                                          │
│  ┌─────────────────────────────────────┐│
│  │  def greet(name):                   ││
│  │      [         DROP ZONE          ] ││
│  │                                     ││
│  └─────────────────────────────────────┘│
│                                          │
│  Available pieces:                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │ return   │ │ "Hello"  │ │    +     │ │
│  └──────────┘ └──────────┘ └──────────┘ │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │  name    │ │   ", "   │ │  print   │ │
│  └──────────┘ └──────────┘ └──────────┘ │
└─────────────────────────────────────────┘
```

**Swipe-to-Indent**
- Swipe right to indent
- Swipe left to dedent
- Visual guides show Python's block structure

**Tap-to-Transform**
```
Tap on: numbers
Options appear:
  [len(numbers)]  [sorted(numbers)]  [numbers[0]]  [numbers[-1]]
```

**Gesture-Based Operators**
```
Draw ↑ on two items     = addition
Draw ✕ on two items     = multiplication
Draw circle around item = parenthesize
Draw line through item  = delete
```

## 2.4 Tablet Advanced Mode

For learners with larger screens who want more power.

### Split-View Interface

```
┌─────────────────────────────────────────────────────────────────────────┐
│  ┌─────────────────────────┐  ┌─────────────────────────────────────┐  │
│  │                          │  │                                     │  │
│  │      CODE EDITOR         │  │      VISUALIZATION PANEL            │  │
│  │                          │  │                                     │  │
│  │  def find_median(lst):   │  │   [3, 1, 4, 1, 5] │ sorted          │  │
│  │      sorted_lst = ...    │  │        ↓         │                  │  │
│  │      mid = len(...) // 2 │  │   [1, 1, 3, 4, 5] │ mid = 2         │  │
│  │      return sorted_lst.. │  │        ↓         │                  │  │
│  │                          │  │       [3]        │ result           │  │
│  │                          │  │                                     │  │
│  └─────────────────────────┘  └─────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │                        TEST CASES & OUTPUT                          ││
│  │  ✓ find_median([1,2,3]) = 2                                         ││
│  │  ✓ find_median([1,2,3,4,5]) = 3                                     ││
│  │  ✗ find_median([1,2]) = 1.5  (got: 1)  ← HINT: Integer division?    ││
│  └─────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────┘
```

### Advanced Debugging Tools

- **Step-through execution** with visual state
- **Variable inspector** with type information
- **Call stack visualization**
- **Memory model** showing object references
- **Time-travel debugging** (step backwards)

---

# Part III: Learning System

## 3.1 The Concept Graph (Progressive Disclosure DAG)

Unlike linear curricula, LMSP uses a Directed Acyclic Graph where concepts unlock based on demonstrated mastery of prerequisites.

### Graph Structure

```
                    ┌─────────────┐
                    │  VARIABLES  │ Level 0
                    └──────┬──────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────▼─────┐   ┌─────▼─────┐   ┌─────▼─────┐
    │   TYPES   │   │   PRINT   │   │   INPUT   │ Level 0
    └─────┬─────┘   └─────┬─────┘   └─────┬─────┘
          │               │               │
          └───────────────┼───────────────┘
                          │
                    ┌─────▼─────┐
                    │ OPERATORS │ Level 1
                    └─────┬─────┘
                          │
     ┌────────────────────┼────────────────────┐
     │                    │                    │
┌────▼────┐         ┌────▼────┐         ┌────▼────┐
│ IF/ELSE │         │   FOR   │         │  WHILE  │ Level 1
└────┬────┘         └────┬────┘         └────┬────┘
     │                   │                   │
     │              ┌────▼────┐              │
     │              │  LISTS  │──────────────┤
     │              └────┬────┘              │
     │                   │                   │
     │    ┌──────────────┼──────────────┐    │
     │    │              │              │    │
     │ ┌──▼───┐     ┌───▼───┐     ┌───▼──┐ │
     │ │  IN  │     │ RANGE │     │ LEN  │ │ Level 2
     │ └──┬───┘     └───┬───┘     └───┬──┘ │
     │    │             │             │    │
     │    └─────────────┼─────────────┘    │
     │                  │                  │
     │           ┌──────▼──────┐           │
     └───────────▶  FUNCTIONS  ◀───────────┘ Level 3
                 └──────┬──────┘
                        │
    ┌───────────────────┼───────────────────┐
    │                   │                   │
┌───▼───┐          ┌───▼───┐          ┌───▼───┐
│PARAMS │          │RETURN │          │ SCOPE │ Level 3
└───┬───┘          └───┬───┘          └───┬───┘
    │                  │                  │
    └──────────────────┼──────────────────┘
                       │
           ┌───────────┼───────────┐
           │           │           │
     ┌─────▼─────┐ ┌──▼──┐ ┌─────▼─────┐
     │  LAMBDA   │ │LIST │ │  SORTED   │ Level 4
     │           │ │COMP │ │  + KEY=   │
     └─────┬─────┘ └──┬──┘ └─────┬─────┘
           │          │          │
           └──────────┼──────────┘
                      │
              ┌───────▼───────┐
              │    CLASSES    │ Level 5
              └───────┬───────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
   ┌────▼────┐  ┌────▼────┐  ┌────▼────┐
   │ __INIT__│  │  SELF   │  │ METHODS │ Level 5
   └────┬────┘  └────┬────┘  └────┬────┘
        │            │            │
        └────────────┼────────────┘
                     │
             ┌───────▼───────┐
             │   PATTERNS    │ Level 6
             └───────┬───────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
┌───▼────┐     ┌────▼────┐     ┌────▼────┐
│CONTAINER│    │ MEDIAN  │    │ DISPATCH │
│  OPS   │    │ FINDING │    │ PATTERN  │ Level 6
└────────┘    └─────────┘    └──────────┘
```

### Concept Data Structure

```toml
# concepts/level_2/lists.toml

[concept]
id = "lists"
name = "Python Lists"
level = 2
category = "collections"

[prerequisites]
required = ["variables", "types"]
recommended = ["for_loops"]  # Helpful but not required

[description]
brief = "Store multiple values in a single variable"
detailed = """
Lists are Python's most versatile data structure. They can hold
any type of data, grow and shrink dynamically, and are the
foundation for most Python programming.
"""

[learning_objectives]
must_demonstrate = [
    "Create a list with initial values",
    "Access elements by index (positive and negative)",
    "Modify list elements",
    "Use append() to add elements",
    "Use len() to get list size",
    "Check membership with 'in' operator"
]

[challenges]
introductory = ["list_creation", "list_indexing"]
core = ["list_modification", "list_append", "list_membership"]
advanced = ["list_slicing", "nested_lists"]
mastery = ["list_comprehension_preview"]

[common_mistakes]
index_off_by_one = "Remember: Python lists are 0-indexed"
mutating_while_iterating = "Don't modify a list while looping over it"
forgetting_brackets = "Lists use square brackets [], not parentheses"

[connections]
leads_to = ["in_operator", "len_function", "list_methods", "list_comprehensions"]
relates_to = ["strings", "tuples", "dictionaries"]

[gamepad_hints]
easy_mode = "Press Y to create a for loop over your list"
radial_shortcut = "LB+RIGHT types '[]' for you"

[spaced_repetition]
initial_interval_hours = 4
difficulty_multiplier = 1.5
max_interval_days = 30
```

## 3.2 Mastery Levels

Each concept progresses through five mastery stages:

### Stage 0: SEEN (🔒)
- Concept visible in skill tree but locked
- Grayed out, shows prerequisites needed
- Builds anticipation and goal-setting

### Stage 1: UNLOCKED (🔓)
- All prerequisites met
- Can attempt introductory challenges
- Full concept explanation available
- Estimated time to practice shown

### Stage 2: PRACTICED (📝)
- Completed 3+ challenges
- May still make mistakes
- Hints available on demand
- Spaced repetition begins

### Stage 3: MASTERED (✅)
- Completed all core challenges
- Speed run under time limit
- Minimal hints used
- Can explain concept (teaching mode unlocked)

### Stage 4: TRANSCENDED (🌟)
- Completed advanced/mastery challenges
- Can teach AI students
- Contributed improvements to challenges
- Concept permanently retained (no more spaced repetition)

### Visual Representation

```
┌─────────────────────────────────────────────────────────────┐
│                     YOUR SKILL TREE                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│     🌟 Variables ─────────┬───────── 🌟 Types               │
│            │              │              │                   │
│            │              │              │                   │
│     ✅ Operators ◄────────┴──────► ✅ Print                  │
│            │                             │                   │
│            │                             │                   │
│     ✅ If/Else ◄─────────────────► 📝 For Loops             │
│            │                             │                   │
│            │         ┌───────────────────┤                   │
│            │         │                   │                   │
│     📝 Functions ◄───┴───► 🔓 Lists ◄───┘                    │
│            │                   │                             │
│            │                   │                             │
│     🔒 Lambda          🔒 List Comprehensions                │
│            │                   │                             │
│            └───────────────────┤                             │
│                                │                             │
│                         🔒 Classes                           │
│                                                              │
│  Legend: 🔒 Locked  🔓 Unlocked  📝 Practicing               │
│          ✅ Mastered  🌟 Transcended                         │
└─────────────────────────────────────────────────────────────┘
```

## 3.3 Adaptive Learning Engine

The heart of LMSP: an AI that learns your learning patterns.

### Emotional State Tracking

```python
@dataclass
class EmotionalState:
    """Real-time emotional state from input patterns"""
    
    # From trigger feedback
    happiness: float      # 0.0-1.0, RT pull depth
    frustration: float    # 0.0-1.0, LT pull depth
    
    # From behavioral signals
    engagement: float     # 0.0-1.0, inverse of hesitation time
    confidence: float     # 0.0-1.0, how quickly selections made
    fatigue: float        # 0.0-1.0, increasing errors over time
    
    # Derived states
    @property
    def flow_state(self) -> bool:
        """True if learner is in optimal learning zone"""
        return (
            self.happiness > 0.6 and
            self.frustration < 0.3 and
            self.engagement > 0.7 and
            self.confidence > 0.5
        )
    
    @property
    def struggle_state(self) -> bool:
        """True if learner needs easier content"""
        return (
            self.frustration > 0.6 or
            self.confidence < 0.3 or
            self.fatigue > 0.7
        )
    
    @property
    def bored_state(self) -> bool:
        """True if learner needs harder content"""
        return (
            self.happiness < 0.3 and
            self.engagement < 0.4 and
            self.confidence > 0.8
        )
```

### The Trigger Feedback System

After each challenge, the learner gives emotional feedback via progressive trigger pulls:

```
┌─────────────────────────────────────────────────────────────┐
│                     HOW DID THAT FEEL?                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ◄─────────────────────────────────────────────────────►   │
│   FRUSTRATING                              ENJOYED IT        │
│                                                              │
│   [LT ████░░░░░░]                    [RT ░░░░░░████████]    │
│      30% pull                              80% pull          │
│                                                              │
│   Press [Y] for detailed feedback                            │
│   Press [A] to continue                                      │
│                                                              │
│   ─────────────────────────────────────────────────────────  │
│   Your input: 😊 Pretty good! (Net: +50%)                    │
└─────────────────────────────────────────────────────────────┘
```

### Learner Profile

```python
@dataclass
class LearnerProfile:
    """Persistent profile that improves over time"""
    
    # Identity
    learner_id: str
    created_at: datetime
    
    # Learning style (discovered over time)
    preferred_input_mode: str  # "radial", "easy", "touch", "keyboard"
    optimal_session_length_minutes: int
    best_time_of_day: str  # "morning", "afternoon", "evening", "night"
    challenge_type_preferences: Dict[str, float]  # e.g., {"puzzle": 0.8, "speed": 0.3}
    
    # Cognitive patterns
    visual_learner_score: float      # Prefers diagrams, animations
    verbal_learner_score: float      # Prefers text explanations
    kinesthetic_learner_score: float # Prefers doing, minimal reading
    
    # Performance patterns
    concepts_mastered: Set[str]
    concepts_struggling: Dict[str, int]  # concept -> failure_count
    average_time_per_concept: Dict[str, timedelta]
    
    # Emotional history
    session_enjoyment_history: List[float]  # Last 100 sessions
    frustration_triggers: List[str]  # Concepts that cause frustration
    flow_triggers: List[str]  # Concepts that induce flow
    
    # Spaced repetition
    review_queue: List[Tuple[str, datetime]]  # (concept, next_review)
    retention_curve: Dict[str, float]  # concept -> retention_rate
    
    # Goals
    target_goal: Optional[str]  # "Build a Discord bot", "Pass CodeSignal"
    custom_curriculum: Optional[List[str]]  # Generated from goal
```

### Adaptive Difficulty Algorithm

```python
class AdaptiveDifficultyEngine:
    """Real-time difficulty adjustment"""
    
    def select_next_challenge(
        self,
        learner: LearnerProfile,
        current_concept: str,
        emotional_state: EmotionalState,
        session_context: SessionContext
    ) -> Challenge:
        """Select optimal next challenge based on all factors"""
        
        # Get available challenges for this concept
        challenges = self.challenge_pool.get_for_concept(current_concept)
        
        # Filter by already completed
        challenges = [c for c in challenges if c.id not in learner.completed_challenges]
        
        # Score each challenge
        scored = []
        for challenge in challenges:
            score = self._score_challenge(challenge, learner, emotional_state, session_context)
            scored.append((score, challenge))
        
        # Select with weighted randomness (avoid pure optimization)
        scored.sort(reverse=True)
        top_challenges = scored[:5]  # Top 5 candidates
        
        # Weighted random selection (higher scored = more likely)
        weights = [s[0] for s in top_challenges]
        selected = random.choices(top_challenges, weights=weights, k=1)[0]
        
        return selected[1]
    
    def _score_challenge(
        self,
        challenge: Challenge,
        learner: LearnerProfile,
        emotional: EmotionalState,
        session: SessionContext
    ) -> float:
        """Score challenge suitability (higher = better fit)"""
        
        score = 0.0
        
        # Difficulty match
        target_difficulty = self._calculate_target_difficulty(learner, emotional)
        difficulty_match = 1.0 - abs(challenge.difficulty - target_difficulty)
        score += difficulty_match * 30  # 30% weight
        
        # Learning style match
        style_match = self._calculate_style_match(challenge, learner)
        score += style_match * 20  # 20% weight
        
        # Spaced repetition priority
        if challenge.concept in learner.review_queue:
            review_urgency = self._calculate_review_urgency(challenge.concept, learner)
            score += review_urgency * 25  # 25% weight
        
        # Fun factor (based on similar challenge history)
        predicted_enjoyment = self._predict_enjoyment(challenge, learner)
        score += predicted_enjoyment * 15  # 15% weight
        
        # Session variety (avoid repetition)
        variety_score = self._calculate_variety(challenge, session)
        score += variety_score * 10  # 10% weight
        
        return score
    
    def _calculate_target_difficulty(
        self,
        learner: LearnerProfile,
        emotional: EmotionalState
    ) -> float:
        """Calculate ideal difficulty level (0.0-1.0)"""
        
        # Base difficulty from learner history
        base = learner.average_success_rate
        
        # Adjust based on emotional state
        if emotional.flow_state:
            # In flow - gradually increase
            return min(base + 0.1, 0.9)
        elif emotional.struggle_state:
            # Struggling - decrease significantly
            return max(base - 0.2, 0.2)
        elif emotional.bored_state:
            # Bored - increase significantly
            return min(base + 0.2, 0.95)
        else:
            # Normal - slight increase (growth mindset)
            return min(base + 0.05, 0.85)
```

## 3.4 Spaced Repetition with Emotional Weighting

LMSP's spaced repetition system considers not just memory, but enjoyment.

### The LMSP-7 Algorithm

Based on SM-2 but with emotional factors:

```python
def calculate_next_review(
    concept: str,
    performance: float,      # 0.0-1.0, how well they did
    enjoyment: float,        # 0.0-1.0, how much they enjoyed it
    previous_interval: timedelta,
    repetition_number: int
) -> timedelta:
    """Calculate next review interval with emotional weighting"""
    
    # Base easiness factor (SM-2 style)
    ef = 2.5 + (0.1 - (5 - performance * 5) * (0.08 + (5 - performance * 5) * 0.02))
    ef = max(1.3, ef)
    
    # Emotional modifier
    # High enjoyment = can wait longer (positive associations help retention)
    # Low enjoyment = review sooner (need to build positive associations)
    emotional_modifier = 0.8 + (enjoyment * 0.4)  # Range: 0.8 to 1.2
    
    # Calculate interval
    if repetition_number == 0:
        interval = timedelta(hours=4)
    elif repetition_number == 1:
        interval = timedelta(days=1)
    elif repetition_number == 2:
        interval = timedelta(days=3)
    else:
        interval = previous_interval * ef * emotional_modifier
    
    # Cap at max interval
    max_interval = timedelta(days=60)
    return min(interval, max_interval)
```

### Review Session Design

When it's time for spaced repetition:

```
┌─────────────────────────────────────────────────────────────┐
│                    🔄 REVIEW TIME                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   You have 5 concepts ready for review:                      │
│                                                              │
│   1. 📝 List Comprehensions (due 2 hours ago)               │
│   2. 📝 Lambda Functions (due now)                          │
│   3. 📝 String Slicing (due in 1 hour)                      │
│   4. 📝 Dictionary Methods (due in 3 hours)                 │
│   5. 📝 Exception Handling (due in 6 hours)                 │
│                                                              │
│   Estimated time: 12 minutes                                 │
│                                                              │
│   [A] Start Review    [B] Customize    [Y] Skip for now     │
│                                                              │
│   💡 Tip: Reviewing now is 3x more effective than later!    │
└─────────────────────────────────────────────────────────────┘
```

### Fun-Weighted Review Selection

```python
def select_review_challenges(
    due_concepts: List[str],
    learner: LearnerProfile,
    available_time_minutes: int
) -> List[Challenge]:
    """Select review challenges, prioritizing fun ones first"""
    
    challenges = []
    time_remaining = available_time_minutes
    
    # Sort by: urgency (past due first), then enjoyment (fun first)
    def priority_key(concept):
        urgency = learner.get_overdue_hours(concept)
        enjoyment = learner.concept_enjoyment_history.get(concept, 0.5)
        # Urgency is primary, enjoyment is tiebreaker
        # Higher enjoyment = do first (positive momentum)
        return (urgency, -enjoyment)
    
    due_concepts.sort(key=priority_key, reverse=True)
    
    for concept in due_concepts:
        challenge = select_review_challenge_for_concept(concept, learner)
        if challenge.estimated_minutes <= time_remaining:
            challenges.append(challenge)
            time_remaining -= challenge.estimated_minutes
    
    # Always start with the most enjoyable challenge (warm-up)
    challenges.sort(key=lambda c: learner.challenge_enjoyment.get(c.id, 0.5), reverse=True)
    
    return challenges
```

## 3.5 Goal-Directed Curriculum Generation

The killer feature: "What do you want to build?" → personalized curriculum.

### Goal Analysis

```python
class GoalAnalyzer:
    """Uses Claude to analyze learner goals and generate curriculum"""
    
    ANALYSIS_PROMPT = """
    Analyze this learning goal and identify ALL Python concepts required.
    
    Goal: {goal}
    
    For each concept:
    1. Why it's needed for this goal
    2. How it will be used in the final project
    3. Difficulty level (1-10)
    4. Dependencies (what must be learned first)
    
    Also identify:
    - Milestone projects (smaller projects that build toward the goal)
    - Estimated total learning time
    - Potential challenges/gotchas
    
    Return as structured JSON.
    """
    
    async def analyze_goal(self, goal: str) -> GoalAnalysis:
        """Analyze a learning goal and generate curriculum"""
        
        response = await self.claude.complete(
            self.ANALYSIS_PROMPT.format(goal=goal)
        )
        
        analysis = self._parse_response(response)
        
        # Build curriculum graph
        curriculum = self._build_curriculum_graph(analysis)
        
        # Estimate timeline
        timeline = self._estimate_timeline(curriculum)
        
        return GoalAnalysis(
            goal=goal,
            required_concepts=analysis.concepts,
            curriculum=curriculum,
            milestones=analysis.milestones,
            estimated_hours=timeline,
            challenges=analysis.challenges
        )
    
    def _build_curriculum_graph(self, analysis: dict) -> CurriculumGraph:
        """Build optimized learning path from analysis"""
        
        # Start with all LMSP concepts
        full_graph = self.concept_graph.clone()
        
        # Mark required concepts
        for concept in analysis['concepts']:
            full_graph.mark_required(concept['id'])
        
        # Find minimal spanning subgraph
        # (includes only required concepts and their dependencies)
        minimal = full_graph.minimal_spanning_subgraph()
        
        # Optimize learning order
        # (topological sort with enjoyment weighting)
        ordered = minimal.topological_sort_optimized()
        
        return CurriculumGraph(
            concepts=ordered,
            total_concepts=len(ordered),
            estimated_challenges=sum(c.challenge_count for c in ordered)
        )
```

### Example Goal Analysis

**User Goal**: "I want to build a Discord bot that tracks my Jellyfin watch history"

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    📎 CURRICULUM GENERATED                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Goal: Discord bot for Jellyfin watch tracking                          │
│  Estimated time: 28 hours (2-3 weeks at 2hr/day)                        │
│                                                                          │
│  ═══════════════════════════════════════════════════════════════════    │
│                                                                          │
│  PHASE 1: Python Fundamentals (8 hours)                                  │
│  ├── Variables & Types ──────────── For storing watch data              │
│  ├── Lists & Dictionaries ───────── Organizing episode info             │
│  ├── Functions ──────────────────── Reusable bot commands               │
│  └── Classes ────────────────────── Discord bot structure               │
│                                                                          │
│  MILESTONE 1: Simple data organizer                                      │
│  Build a program that reads a list of movies and organizes them         │
│                                                                          │
│  ═══════════════════════════════════════════════════════════════════    │
│                                                                          │
│  PHASE 2: APIs & Web (10 hours)                                          │
│  ├── HTTP Requests ──────────────── Talking to Jellyfin API             │
│  ├── JSON Parsing ───────────────── Reading API responses               │
│  ├── Error Handling ─────────────── Graceful failures                   │
│  └── Async/Await ────────────────── Discord.py requires this            │
│                                                                          │
│  MILESTONE 2: Jellyfin data fetcher                                      │
│  CLI tool that fetches your watch history from Jellyfin                 │
│                                                                          │
│  ═══════════════════════════════════════════════════════════════════    │
│                                                                          │
│  PHASE 3: Discord Bot (10 hours)                                         │
│  ├── Discord.py Basics ──────────── Bot structure                       │
│  ├── Commands ───────────────────── User interactions                   │
│  ├── Embeds ─────────────────────── Pretty output                       │
│  └── Background Tasks ───────────── Periodic updates                    │
│                                                                          │
│  FINAL PROJECT: Your Jellyfin Discord bot! 🎉                           │
│                                                                          │
│  ═══════════════════════════════════════════════════════════════════    │
│                                                                          │
│  [A] Start Learning    [B] Customize Path    [Y] Different Goal         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

# Part IV: Challenge System

## 4.1 Challenge Types

### Type 1: Code Completion

Fill in the blanks in existing code.

```python
# Challenge: Complete the function to find the median
def find_median(numbers):
    sorted_nums = _____(numbers)
    mid = len(sorted_nums) _____ 2
    return sorted_nums[_____]

# Blanks:
# 1. sorted
# 2. //
# 3. mid
```

**Gamepad Interaction**:
- D-pad navigates between blanks
- RB shows suggestions for current blank
- A confirms selection
- Y runs test cases

### Type 2: Bug Fix

Find and fix the bug.

```python
# Challenge: This function should return the sum, but it's broken
def sum_numbers(numbers):
    total = 0
    for num in numbers:
        total = num  # BUG: Should be total += num
    return total

# Test case: sum_numbers([1, 2, 3]) should return 6, but returns 3
```

**Gamepad Interaction**:
- Navigate to buggy line
- X opens "fix menu" with options
- Select correct fix from multiple choice

### Type 3: Build from Scratch

Write code to meet a specification.

```python
# Challenge: Implement a container with ADD, EXISTS, REMOVE operations
# 
# Input: List of operations like [["ADD", "1"], ["EXISTS", "1"], ["REMOVE", "1"]]
# Output: List of results ["", "true", ""]
#
# Your code:
def process_operations(operations):
    # Your code here
    pass
```

**Gamepad Interaction**:
- Full radial typing
- Easy mode buttons for structure
- RB for smart suggestions

### Type 4: Code Golf

Solve in fewest characters.

```python
# Challenge: Sum all even numbers in a list
# Your solution must be under 40 characters
# 
# Example: golf_sum([1,2,3,4,5,6]) = 12

# Current best: 28 chars
# Your attempt: _____
```

**Leaderboard integration** - compete with other learners!

### Type 5: Speed Run

Complete quickly under time pressure.

```
┌─────────────────────────────────────────────────────────────┐
│  ⏱️ SPEED RUN: Container Operations                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Time remaining: 02:34                                       │
│  Target time: 03:00                                          │
│  Your best: 02:15                                            │
│                                                              │
│  Progress: ████████░░░░░░░░ 4/7 test cases                   │
│                                                              │
│  [Current code displayed]                                    │
│                                                              │
│  💡 Speed tip: Use 'in' operator for EXISTS checks          │
└─────────────────────────────────────────────────────────────┘
```

### Type 6: Teaching Mode

Explain a concept to an AI student (unlocked at MASTERED level).

```
┌─────────────────────────────────────────────────────────────┐
│  🎓 TEACHING MODE: Explain List Comprehensions              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Your AI student says:                                       │
│  "I don't understand why we need list comprehensions.        │
│   Can't we just use a for loop?"                             │
│                                                              │
│  Your response options:                                      │
│                                                              │
│  1. "List comprehensions are faster" (partially correct)     │
│  2. "They're more readable for simple transformations"  ✓    │
│  3. "For loops are actually better" (incorrect)              │
│  4. [Write custom explanation]                               │
│                                                              │
│  Teaching effectiveness: Builds your TRANSCENDED mastery    │
└─────────────────────────────────────────────────────────────┘
```

## 4.2 Challenge Definition Format

```toml
# challenges/container_operations/level_1.toml

[challenge]
id = "container_ops_basic"
name = "Container: Add and Exists"
type = "build_from_scratch"
concept = "patterns_container"
difficulty = 0.4  # 0.0-1.0
estimated_minutes = 8

[description]
brief = "Implement ADD and EXISTS operations for a container"
detailed = """
You're building a simple container that supports two operations:
- ADD <value>: Add the value to the container. Return empty string.
- EXISTS <value>: Check if value exists. Return "true" or "false".

The container should handle duplicates (adding same value twice is fine).
"""

[template]
code = """
def process_operations(operations):
    # operations is a list of [command, value] pairs
    # Return a list of results
    pass
"""

[tests]
[[tests.case]]
name = "basic_add_exists"
input = [[["ADD", "1"], ["EXISTS", "1"]]]
expected = [["", "true"]]
hidden = false

[[tests.case]]
name = "not_exists"
input = [[["EXISTS", "999"]]]
expected = [["false"]]
hidden = false

[[tests.case]]
name = "multiple_operations"
input = [[["ADD", "a"], ["ADD", "b"], ["EXISTS", "a"], ["EXISTS", "c"]]]
expected = [["", "", "true", "false"]]
hidden = false

[[tests.case]]
name = "edge_case_empty_value"
input = [[["ADD", ""], ["EXISTS", ""]]]
expected = [["", "true"]]
hidden = true  # Hidden test case

[hints]
level_1 = "You'll need a data structure to store the values"
level_2 = "A Python list would work. What method adds to a list?"
level_3 = "Use 'append()' to add, and 'in' operator to check existence"
level_4 = "Don't forget: EXISTS should return strings 'true'/'false', not booleans"

[solutions]
optimal = """
def process_operations(operations):
    container = []
    results = []
    for op, val in operations:
        if op == "ADD":
            container.append(val)
            results.append("")
        elif op == "EXISTS":
            results.append("true" if val in container else "false")
    return results
"""

alternative_set = """
def process_operations(operations):
    container = set()  # O(1) lookups!
    results = []
    for op, val in operations:
        if op == "ADD":
            container.add(val)
            results.append("")
        elif op == "EXISTS":
            results.append("true" if val in container else "false")
    return results
"""

[gamepad_hints]
easy_mode = """
1. Press [A] to create the function skeleton
2. Press [Y] to add a for loop over operations
3. Press [X] to add if/elif for each operation type
4. Press [RB] to auto-complete common patterns
"""

[scoring]
points_base = 100
points_speed_bonus = 50  # Under par time
points_no_hints = 25
points_optimal_solution = 25

[metadata]
tags = ["container", "list", "membership", "codesignal-prep"]
author = "lmsp-curriculum"
version = "1.0"
```

## 4.3 Challenge Generation (AI-Powered)

For infinite variety, LMSP can generate new challenges using Claude:

```python
class ChallengeGenerator:
    """Generate new challenges using Claude"""
    
    GENERATION_PROMPT = """
    Generate a coding challenge for the concept: {concept}
    
    Requirements:
    - Difficulty level: {difficulty} (0.0-1.0)
    - Should take approximately {minutes} minutes
    - Must have at least 4 test cases (2 visible, 2 hidden)
    - Include 4 progressive hints
    - Provide optimal solution and one alternative
    
    Theme/Context (optional): {theme}
    
    Output as TOML in the LMSP challenge format.
    """
    
    async def generate_challenge(
        self,
        concept: str,
        difficulty: float,
        minutes: int = 10,
        theme: Optional[str] = None
    ) -> Challenge:
        """Generate a new challenge"""
        
        prompt = self.GENERATION_PROMPT.format(
            concept=concept,
            difficulty=difficulty,
            minutes=minutes,
            theme=theme or "general programming"
        )
        
        response = await self.claude.complete(prompt)
        challenge_toml = self._extract_toml(response)
        
        # Validate the challenge
        challenge = Challenge.from_toml(challenge_toml)
        await self._validate_challenge(challenge)
        
        return challenge
    
    async def _validate_challenge(self, challenge: Challenge):
        """Ensure generated challenge is solvable and correct"""
        
        # Run optimal solution against all test cases
        for test in challenge.tests:
            result = await self._execute_solution(
                challenge.solutions.optimal,
                test.input
            )
            assert result == test.expected, f"Optimal solution failed: {test.name}"
        
        # Ensure difficulty is appropriate
        # (measure time to solve with hints)
        await self._calibrate_difficulty(challenge)
```

## 4.4 Dynamic Difficulty Adjustment

Challenges adapt in real-time based on performance:

```python
class DynamicChallenge:
    """A challenge that adapts during execution"""
    
    def __init__(self, base_challenge: Challenge):
        self.base = base_challenge
        self.current_hints_shown = 0
        self.time_elapsed = timedelta(0)
        self.attempts = 0
        self.partial_completions = []
    
    def get_current_difficulty(self) -> float:
        """Calculate current effective difficulty"""
        
        base_difficulty = self.base.difficulty
        
        # Reduce difficulty for:
        # - Each hint shown (-0.05 per hint)
        # - Time over par (-0.01 per minute over)
        # - Multiple attempts (-0.03 per attempt)
        
        adjustments = 0.0
        adjustments -= self.current_hints_shown * 0.05
        adjustments -= max(0, self.minutes_over_par) * 0.01
        adjustments -= self.attempts * 0.03
        
        return max(0.1, base_difficulty + adjustments)
    
    def maybe_offer_hint(self) -> Optional[str]:
        """Offer hints based on struggle detection"""
        
        if self.time_elapsed > self.base.par_time * 1.5:
            if self.current_hints_shown < len(self.base.hints):
                hint = self.base.hints[self.current_hints_shown]
                self.current_hints_shown += 1
                return hint
        
        return None
    
    def maybe_simplify(self) -> Optional[Challenge]:
        """Generate simplified version if struggling too much"""
        
        if self.attempts > 5 and self.current_hints_shown == len(self.base.hints):
            # Generate easier variant
            return self._generate_simplified()
        
        return None
```

---

# Part V: Multiplayer System (player-zero)

## 5.1 Architecture Overview

player-zero is a standalone framework for multi-Claude gaming/learning sessions.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        PLAYER-ZERO ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────┐     ┌─────────────────────────────────────┐            │
│  │   Player 1  │     │         SESSION MANAGER              │            │
│  │  (Human)    │────▶│                                     │            │
│  │  Controller │     │  - Spawns Claude instances          │            │
│  └─────────────┘     │  - Routes stream-json events        │            │
│                      │  - Manages shared game state        │            │
│  ┌─────────────┐     │  - Handles player join/leave        │            │
│  │   Player 2  │────▶│  - Coordinates turn-taking (if any) │            │
│  │  (Claude)   │     │                                     │            │
│  │  AI Agent   │     └──────────────┬──────────────────────┘            │
│  └─────────────┘                    │                                   │
│                                     │                                   │
│  ┌─────────────┐     ┌──────────────▼──────────────────────┐            │
│  │   Player 3  │────▶│         GAME STATE                   │            │
│  │  (Claude)   │     │                                     │            │
│  │  AI Agent   │     │  - Current challenge                │            │
│  └─────────────┘     │  - Each player's code/progress      │            │
│                      │  - Shared context/history           │            │
│  ┌─────────────┐     │  - Scores/rankings                  │            │
│  │   Player 4  │────▶│  - Event log                        │            │
│  │  (Human)    │     │                                     │            │
│  │  Controller │     └──────────────────────────────────────┘            │
│  └─────────────┘                                                         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## 5.2 Player Types

### Human Player
```python
@dataclass
class HumanPlayer:
    """A human player with physical input device"""
    
    player_id: str
    name: str
    controller_index: int  # 0-3 for gamepads
    input_mode: str  # "radial", "easy", "keyboard"
    profile: LearnerProfile
    
    # State
    current_code: str = ""
    cursor_position: int = 0
    last_input_time: datetime = None
    
    async def get_input(self) -> InputEvent:
        """Get next input from human controller"""
        return await self.controller.wait_for_input()
    
    def apply_input(self, event: InputEvent):
        """Apply input to current code"""
        # Handle radial typing, easy mode, etc.
        pass
```

### Claude Player
```python
@dataclass
class ClaudePlayer:
    """An AI player powered by Claude"""
    
    player_id: str
    name: str
    model: str  # "claude-sonnet-4-5-20250929", etc.
    personality: str  # "helpful", "competitive", "teacher"
    skill_level: float  # 0.0-1.0, controls how "good" it plays
    
    # Process management
    process: subprocess.Popen = None
    stdin_queue: asyncio.Queue = None
    stdout_queue: asyncio.Queue = None
    
    # State
    current_code: str = ""
    thinking: str = ""  # What Claude is "thinking" (shown to spectators)
    
    SYSTEM_PROMPT = """
    You are playing LMSP (Learn Me Some Python) as Player {player_id}: {name}.
    
    Your personality: {personality}
    Your skill level: {skill_level}/1.0 (play accordingly - make realistic mistakes if lower)
    
    Game mode: {game_mode}
    
    You will receive:
    - The current challenge
    - Other players' progress (via stream-json events)
    - Your turn notifications
    
    Output your actions as stream-json events.
    
    Remember: This is for LEARNING. If you're helping, explain your thinking.
    If you're competing, be a good sport. If you're teaching, be patient.
    """
    
    async def spawn(self, session: GameSession):
        """Spawn Claude process for this player"""
        
        system_prompt = self.SYSTEM_PROMPT.format(
            player_id=self.player_id,
            name=self.name,
            personality=self.personality,
            skill_level=self.skill_level,
            game_mode=session.mode
        )
        
        cmd = [
            "claude",
            "-p", session.initial_prompt,
            "--system", system_prompt,
            "--output-format", "stream-json"
        ]
        
        self.process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        # Start reader task
        asyncio.create_task(self._read_stdout())
    
    async def send_event(self, event: dict):
        """Send event to Claude's stdin"""
        line = json.dumps(event) + "\n"
        self.process.stdin.write(line)
        self.process.stdin.flush()
    
    async def _read_stdout(self):
        """Read and queue Claude's outputs"""
        while True:
            line = await asyncio.get_event_loop().run_in_executor(
                None, self.process.stdout.readline
            )
            if not line:
                break
            await self.stdout_queue.put(json.loads(line))
```

## 5.3 Game Modes

### Mode 1: COOP (Cooperative)

All players work together on the same challenge.

```python
class CoopMode(GameMode):
    """Players collaborate on a single solution"""
    
    name = "coop"
    min_players = 2
    max_players = 4
    
    def __init__(self):
        self.shared_code = ""
        self.cursor_owners = {}  # region -> player_id
    
    async def on_player_input(self, player: Player, event: InputEvent):
        """Handle input in coop mode"""
        
        # Acquire cursor lock for the region being edited
        region = self._get_region(event.position)
        
        if region in self.cursor_owners and self.cursor_owners[region] != player.player_id:
            # Someone else is editing this region
            await self._notify_conflict(player, region)
            return
        
        # Apply the edit
        self.cursor_owners[region] = player.player_id
        self.shared_code = self._apply_edit(self.shared_code, event)
        
        # Broadcast to all players
        await self.broadcast_state()
    
    async def on_player_submit(self, player: Player):
        """Handle submission (any player can submit)"""
        
        results = await self._run_tests(self.shared_code)
        
        if results.all_passed:
            # Everyone wins!
            await self.broadcast_victory(results)
        else:
            # Show which tests failed
            await self.broadcast_test_results(results)
```

### Mode 2: COMPETITIVE (Racing)

First player to solve wins.

```python
class CompetitiveMode(GameMode):
    """Players race to solve first"""
    
    name = "competitive"
    min_players = 2
    max_players = 4
    
    def __init__(self):
        self.player_code = {}  # player_id -> code
        self.player_progress = {}  # player_id -> tests_passed
        self.finished_order = []
    
    async def on_player_input(self, player: Player, event: InputEvent):
        """Handle input in competitive mode"""
        
        # Each player has their own code
        if player.player_id not in self.player_code:
            self.player_code[player.player_id] = ""
        
        self.player_code[player.player_id] = self._apply_edit(
            self.player_code[player.player_id],
            event
        )
        
        # Broadcast progress (how many tests passing)
        progress = await self._check_progress(player.player_id)
        self.player_progress[player.player_id] = progress
        await self.broadcast_standings()
    
    async def on_player_submit(self, player: Player):
        """Handle submission attempt"""
        
        code = self.player_code.get(player.player_id, "")
        results = await self._run_tests(code)
        
        if results.all_passed:
            # This player finished!
            place = len(self.finished_order) + 1
            self.finished_order.append(player.player_id)
            
            await self.broadcast_finish(player, place, results.time)
            
            if len(self.finished_order) == len(self.players):
                await self.broadcast_final_standings()
        else:
            # Failed submission - show errors to this player only
            await player.send_event({
                "type": "test_failure",
                "results": results.to_dict()
            })
```

### Mode 3: PAIR (Split Problem)

Two players each solve half the problem.

```python
class PairMode(GameMode):
    """Two players solve different parts"""
    
    name = "pair"
    min_players = 2
    max_players = 2
    
    def __init__(self, challenge: Challenge):
        # Split challenge into two parts
        self.part_a, self.part_b = self._split_challenge(challenge)
        self.code_a = ""
        self.code_b = ""
        self.player_assignments = {}
    
    def _split_challenge(self, challenge: Challenge) -> Tuple[ChallengePart, ChallengePart]:
        """Split challenge intelligently"""
        
        # Example: Container operations
        # Part A: Implement ADD and EXISTS
        # Part B: Implement REMOVE and GET_NEXT
        
        # Or: One player writes tests, other writes implementation
        # Or: One writes function signature, other fills in body
        
        return challenge.generate_split()
    
    async def on_both_complete(self):
        """When both players finish their parts"""
        
        # Combine the code
        combined = self._merge_code(self.code_a, self.code_b)
        
        # Run full test suite
        results = await self._run_tests(combined)
        
        if results.all_passed:
            await self.broadcast_victory(results)
        else:
            # Figure out which part has the bug
            diagnosis = await self._diagnose_failure(results)
            await self.broadcast_diagnosis(diagnosis)
```

### Mode 4: TEACH (One teaches AI students)

A human player explains concepts to Claude students.

```python
class TeachMode(GameMode):
    """Human teaches AI students"""
    
    name = "teach"
    min_players = 1  # Just the teacher
    max_players = 1
    ai_students = 3  # Claude instances as students
    
    def __init__(self, concept: str):
        self.concept = concept
        self.students = []
        self.teaching_score = 0.0
    
    async def setup(self):
        """Spawn AI students with different skill levels"""
        
        self.students = [
            ClaudePlayer(
                name="Alex",
                personality="eager beginner, asks lots of questions",
                skill_level=0.2
            ),
            ClaudePlayer(
                name="Jordan",
                personality="quiet learner, needs examples",
                skill_level=0.4
            ),
            ClaudePlayer(
                name="Sam",
                personality="skeptical, wants to understand why",
                skill_level=0.6
            )
        ]
        
        for student in self.students:
            await student.spawn(self)
    
    async def process_teacher_explanation(self, explanation: str):
        """Teacher provides an explanation"""
        
        # Send to all students
        for student in self.students:
            await student.send_event({
                "type": "teacher_explanation",
                "content": explanation
            })
        
        # Wait for student responses
        responses = await self._collect_student_responses()
        
        # Students ask questions based on comprehension
        for response in responses:
            if response.get("has_question"):
                await self.broadcast_question(response)
    
    async def assess_teaching(self) -> TeachingAssessment:
        """Assess how well the teacher did"""
        
        # Give students a quiz
        quiz_results = []
        for student in self.students:
            result = await self._quiz_student(student)
            quiz_results.append(result)
        
        # Calculate teaching effectiveness
        avg_score = sum(r.score for r in quiz_results) / len(quiz_results)
        
        return TeachingAssessment(
            average_student_score=avg_score,
            questions_answered=self.questions_answered,
            examples_given=self.examples_given,
            teaching_effectiveness=self._calculate_effectiveness(quiz_results)
        )
```

### Mode 5: SPECTATE (Watch AI solve with explanations)

Learn by watching Claude solve problems.

```python
class SpectateMode(GameMode):
    """Watch AI solve with commentary"""
    
    name = "spectate"
    
    def __init__(self, challenge: Challenge, speed: float = 1.0):
        self.challenge = challenge
        self.speed = speed  # 0.5 = half speed, 2.0 = double speed
        self.commentator = None
    
    async def setup(self):
        """Setup AI solver and commentator"""
        
        self.solver = ClaudePlayer(
            name="Solver",
            personality="expert programmer",
            skill_level=1.0  # Perfect play
        )
        
        self.commentator = ClaudePlayer(
            name="Commentator",
            personality="friendly teacher explaining each step",
            skill_level=1.0
        )
        
        await self.solver.spawn(self)
        await self.commentator.spawn(self)
    
    async def run(self):
        """Run the spectate session"""
        
        while not self.challenge_complete:
            # Get next action from solver
            action = await self.solver.stdout_queue.get()
            
            # Get commentary
            commentary = await self.commentator.explain_action(action)
            
            # Display with timing
            await self.display_action_with_commentary(
                action,
                commentary,
                delay=self.speed
            )
            
            # Allow spectator to pause/rewind
            if self.spectator_paused:
                await self.wait_for_unpause()
```

## 5.4 Stream-JSON Protocol

The protocol for real-time multiplayer awareness.

### Event Types

```python
# Player input events
{
    "type": "code_edit",
    "player_id": "player-1",
    "position": {"line": 5, "col": 12},
    "action": "insert",
    "content": "for item in items:",
    "timestamp": "2025-01-15T10:30:00Z"
}

# Player progress events  
{
    "type": "test_progress",
    "player_id": "player-2",
    "tests_passed": 3,
    "tests_total": 5,
    "current_output": "Traceback...",
    "timestamp": "2025-01-15T10:30:05Z"
}

# Player communication
{
    "type": "player_message",
    "player_id": "player-1",
    "content": "I think we need a dictionary here",
    "message_type": "suggestion",  # or "question", "celebration", etc.
    "timestamp": "2025-01-15T10:30:10Z"
}

# Game state events
{
    "type": "game_state",
    "challenge_id": "container_ops_basic",
    "time_elapsed_seconds": 180,
    "standings": [
        {"player_id": "player-1", "progress": 0.6},
        {"player_id": "player-2", "progress": 0.4}
    ],
    "timestamp": "2025-01-15T10:30:15Z"
}

# Hint/assistance events
{
    "type": "hint_given",
    "player_id": "player-2",  # Who received the hint
    "hint_level": 2,
    "hint_content": "Try using the 'in' operator",
    "timestamp": "2025-01-15T10:30:20Z"
}
```

### Forwarding Logic

The core of multiplayer awareness (from Palace):

```python
async def forward_to_other_players(
    source_player_id: str,
    event: dict,
    all_players: Dict[str, Player]
):
    """Forward event to all other players for shared awareness"""
    
    for player_id, player in all_players.items():
        if player_id == source_player_id:
            continue  # Don't forward to self
        
        if not player.is_active:
            continue  # Don't forward to disconnected players
        
        try:
            if isinstance(player, ClaudePlayer):
                # Forward to Claude's stdin
                await player.send_event({
                    "type": "peer_event",
                    "source": source_player_id,
                    "event": event
                })
            else:
                # Forward to human's display
                await player.display_peer_event(event)
        except Exception as e:
            logger.warning(f"Failed to forward to {player_id}: {e}")
```

---

# Part VI: TAS & Introspection System

## 6.1 Time-Travel Debugging

Full pause/rewind/step-through capabilities.

### State Snapshots

```python
@dataclass
class ExecutionState:
    """Complete state at a point in time"""
    
    timestamp: datetime
    code: str
    cursor_position: int
    variables: Dict[str, Any]
    call_stack: List[StackFrame]
    output_so_far: str
    test_results_so_far: List[TestResult]
    
    # For restoration
    random_state: bytes
    
    def to_bytes(self) -> bytes:
        """Serialize for storage"""
        return pickle.dumps(self)
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'ExecutionState':
        """Deserialize from storage"""
        return pickle.loads(data)

class TimeTravel:
    """Time-travel debugging manager"""
    
    def __init__(self, max_snapshots: int = 1000):
        self.snapshots: List[ExecutionState] = []
        self.current_index: int = -1
        self.max_snapshots = max_snapshots
    
    def capture(self, state: ExecutionState):
        """Capture current state"""
        
        # Truncate future if we've rewound and made changes
        if self.current_index < len(self.snapshots) - 1:
            self.snapshots = self.snapshots[:self.current_index + 1]
        
        self.snapshots.append(state)
        self.current_index = len(self.snapshots) - 1
        
        # Enforce max snapshots
        if len(self.snapshots) > self.max_snapshots:
            self.snapshots.pop(0)
            self.current_index -= 1
    
    def step_back(self) -> Optional[ExecutionState]:
        """Go back one step"""
        if self.current_index > 0:
            self.current_index -= 1
            return self.snapshots[self.current_index]
        return None
    
    def step_forward(self) -> Optional[ExecutionState]:
        """Go forward one step"""
        if self.current_index < len(self.snapshots) - 1:
            self.current_index += 1
            return self.snapshots[self.current_index]
        return None
    
    def rewind_to(self, timestamp: datetime) -> Optional[ExecutionState]:
        """Rewind to specific timestamp"""
        for i, state in enumerate(self.snapshots):
            if state.timestamp >= timestamp:
                self.current_index = max(0, i - 1)
                return self.snapshots[self.current_index]
        return None
    
    def create_checkpoint(self, name: str):
        """Create named checkpoint"""
        self.checkpoints[name] = self.current_index
    
    def restore_checkpoint(self, name: str) -> Optional[ExecutionState]:
        """Restore named checkpoint"""
        if name in self.checkpoints:
            self.current_index = self.checkpoints[name]
            return self.snapshots[self.current_index]
        return None
```

## 6.2 Screenshot System with Mental Wireframe

Capture screen state plus complete execution context.

```python
@dataclass
class MentalWireframe:
    """The 'mental model' behind a screenshot"""
    
    # Code state
    source_code: str
    current_line: int
    cursor_position: Tuple[int, int]
    syntax_errors: List[SyntaxError]
    
    # Execution state
    variables: Dict[str, Any]
    variable_types: Dict[str, str]
    call_stack: List[StackFrame]
    current_scope: str
    
    # Test state
    tests_run: int
    tests_passed: int
    current_test_input: Any
    current_test_expected: Any
    current_test_actual: Any
    
    # Learner state
    hints_used: int
    time_elapsed: timedelta
    emotional_state: EmotionalState
    recent_actions: List[InputEvent]
    
    # Game state (if multiplayer)
    other_players_progress: Dict[str, float]
    game_mode: str
    
    def to_json(self) -> str:
        """Serialize for Claude analysis"""
        return json.dumps(asdict(self), default=str, indent=2)

class ScreenshotCapture:
    """Capture screenshots with full context"""
    
    def __init__(self, game: 'LMSP'):
        self.game = game
        self.capture_dir = Path("~/.lmsp/captures").expanduser()
        self.capture_dir.mkdir(parents=True, exist_ok=True)
    
    async def capture(self, trigger: str = "manual") -> Screenshot:
        """Capture current screen with wireframe"""
        
        timestamp = datetime.now()
        
        # Capture visual
        visual = await self._capture_screen()
        
        # Build wireframe
        wireframe = MentalWireframe(
            source_code=self.game.current_code,
            current_line=self.game.cursor_line,
            cursor_position=self.game.cursor_position,
            syntax_errors=self.game.syntax_errors,
            variables=self.game.debugger.get_variables(),
            variable_types=self.game.debugger.get_types(),
            call_stack=self.game.debugger.get_call_stack(),
            current_scope=self.game.debugger.current_scope,
            tests_run=self.game.tests_run,
            tests_passed=self.game.tests_passed,
            current_test_input=self.game.current_test.input if self.game.current_test else None,
            current_test_expected=self.game.current_test.expected if self.game.current_test else None,
            current_test_actual=self.game.last_output,
            hints_used=self.game.hints_used,
            time_elapsed=self.game.elapsed_time,
            emotional_state=self.game.learner.emotional_state,
            recent_actions=self.game.recent_actions[-20:],
            other_players_progress=self.game.get_other_players_progress(),
            game_mode=self.game.mode.name
        )
        
        # Save
        screenshot_id = f"{timestamp.isoformat()}_{trigger}"
        screenshot = Screenshot(
            id=screenshot_id,
            timestamp=timestamp,
            trigger=trigger,
            visual_path=self.capture_dir / f"{screenshot_id}.png",
            wireframe=wireframe
        )
        
        await self._save_screenshot(screenshot, visual)
        
        return screenshot
    
    async def capture_instant(self) -> Screenshot:
        """Zero-latency capture (pre-buffered)"""
        # Uses a ring buffer of pre-rendered frames
        return await self._capture_from_buffer()
```

## 6.3 Strategic Video Recording

Record sessions as mosaic tiles optimized for Claude vision analysis.

```python
class VideoRecorder:
    """Strategic video recording with mosaic output"""
    
    def __init__(
        self,
        fps: int = 5,  # Low FPS for manageable file sizes
        duration_seconds: int = 60,
        mosaic_grid: Tuple[int, int] = (6, 6)  # 36 frames
    ):
        self.fps = fps
        self.duration = duration_seconds
        self.grid = mosaic_grid
        self.frames: List[Frame] = []
        self.recording = False
    
    async def start_recording(self):
        """Start recording frames"""
        self.recording = True
        self.frames = []
        
        while self.recording and len(self.frames) < self.fps * self.duration:
            frame = await self._capture_frame()
            self.frames.append(frame)
            await asyncio.sleep(1.0 / self.fps)
    
    def stop_recording(self):
        """Stop recording"""
        self.recording = False
    
    async def generate_mosaic(self) -> Path:
        """Generate mosaic image from recorded frames"""
        
        # Select frames evenly distributed
        total_frames = self.grid[0] * self.grid[1]
        indices = [int(i * len(self.frames) / total_frames) for i in range(total_frames)]
        selected_frames = [self.frames[i] for i in indices]
        
        # Calculate tile size
        # Optimize for Claude's vision (max 1568px on any side)
        tile_width = 1568 // self.grid[0]
        tile_height = 1568 // self.grid[1]
        
        # Create mosaic
        mosaic_width = tile_width * self.grid[0]
        mosaic_height = tile_height * self.grid[1]
        mosaic = Image.new('RGB', (mosaic_width, mosaic_height))
        
        for idx, frame in enumerate(selected_frames):
            row = idx // self.grid[0]
            col = idx % self.grid[0]
            
            # Resize frame to tile size
            tile = frame.image.resize((tile_width, tile_height))
            
            # Paste into mosaic
            x = col * tile_width
            y = row * tile_height
            mosaic.paste(tile, (x, y))
            
            # Add frame number overlay
            draw = ImageDraw.Draw(mosaic)
            draw.text((x + 5, y + 5), f"F{idx+1}", fill='white')
        
        # Save as WebP (lossless, good compression)
        output_path = self.capture_dir / f"mosaic_{datetime.now().isoformat()}.webp"
        mosaic.save(output_path, 'WEBP', lossless=True)
        
        return output_path
    
    async def analyze_with_claude(self, mosaic_path: Path) -> Analysis:
        """Send mosaic to Claude for analysis"""
        
        with open(mosaic_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode()
        
        response = await self.claude.complete(
            prompt="""
            Analyze this learning session recording.
            
            The mosaic shows {total_frames} frames from a {duration} second session.
            Frames are numbered F1-F{total_frames}, reading left-to-right, top-to-bottom.
            
            Analyze:
            1. Learning progression - what concepts were practiced?
            2. Struggle points - where did the learner get stuck?
            3. Flow moments - where was the learner in a good rhythm?
            4. Recommendations - what should be done differently?
            """.format(
                total_frames=self.grid[0] * self.grid[1],
                duration=self.duration
            ),
            images=[{"type": "image", "data": image_data, "media_type": "image/webp"}]
        )
        
        return self._parse_analysis(response)
```

## 6.4 Introspection Primitives

Progressive discovery of debugging tools.

```python
class IntrospectionPrimitives:
    """
    Discoverable introspection tools.
    New tools unlock as learner progresses.
    """
    
    # Tool definitions with unlock conditions
    TOOLS = {
        # Always available
        "help": {
            "description": "List available tools",
            "unlock_level": 0,
            "usage": "/help [tool_name]"
        },
        "screenshot": {
            "description": "Capture current state with full context",
            "unlock_level": 0,
            "usage": "/screenshot [name]"
        },
        
        # Unlocked at Level 1
        "variables": {
            "description": "Show all variables and their values",
            "unlock_level": 1,
            "usage": "/variables"
        },
        "step": {
            "description": "Execute one line and pause",
            "unlock_level": 1,
            "usage": "/step"
        },
        
        # Unlocked at Level 2
        "rewind": {
            "description": "Go back N steps",
            "unlock_level": 2,
            "usage": "/rewind [N]"
        },
        "checkpoint": {
            "description": "Save/restore named checkpoints",
            "unlock_level": 2,
            "usage": "/checkpoint save <name> | /checkpoint restore <name>"
        },
        
        # Unlocked at Level 3
        "trace": {
            "description": "Trace execution of a function",
            "unlock_level": 3,
            "usage": "/trace <function_name>"
        },
        "diff": {
            "description": "Compare two checkpoints",
            "unlock_level": 3,
            "usage": "/diff <checkpoint1> <checkpoint2>"
        },
        
        # Unlocked at Level 4
        "profile": {
            "description": "Performance profiling",
            "unlock_level": 4,
            "usage": "/profile"
        },
        "record": {
            "description": "Start video recording",
            "unlock_level": 4,
            "usage": "/record [fps] [duration]"
        },
        "mosaic": {
            "description": "Generate mosaic from recording",
            "unlock_level": 4,
            "usage": "/mosaic [grid_size]"
        },
        
        # Unlocked at Level 5
        "explain": {
            "description": "Get AI explanation of current state",
            "unlock_level": 5,
            "usage": "/explain [what]"
        },
        "suggest": {
            "description": "Get AI suggestions for next steps",
            "unlock_level": 5,
            "usage": "/suggest"
        },
        
        # Unlocked at Level 6 (Mastery)
        "teach": {
            "description": "Enter teaching mode",
            "unlock_level": 6,
            "usage": "/teach <concept>"
        },
        "speedrun": {
            "description": "Start speed run timer",
            "unlock_level": 6,
            "usage": "/speedrun <challenge>"
        }
    }
    
    def __init__(self, learner: LearnerProfile):
        self.learner = learner
    
    def get_available_tools(self) -> List[str]:
        """Get tools available at current level"""
        level = self._calculate_level()
        return [
            name for name, tool in self.TOOLS.items()
            if tool["unlock_level"] <= level
        ]
    
    def get_newly_unlocked(self) -> List[str]:
        """Get tools unlocked since last check"""
        level = self._calculate_level()
        previous_level = self.learner.last_checked_level
        
        newly_unlocked = [
            name for name, tool in self.TOOLS.items()
            if previous_level < tool["unlock_level"] <= level
        ]
        
        self.learner.last_checked_level = level
        return newly_unlocked
    
    async def execute(self, command: str) -> str:
        """Execute an introspection command"""
        
        parts = command.strip().split()
        tool_name = parts[0].lstrip('/')
        args = parts[1:]
        
        if tool_name not in self.get_available_tools():
            return f"Tool '{tool_name}' not available. Use /help to see available tools."
        
        # Execute the tool
        handler = getattr(self, f"_do_{tool_name}", None)
        if handler:
            return await handler(*args)
        else:
            return f"Tool '{tool_name}' is defined but not implemented yet."
    
    async def _do_help(self, tool_name: str = None) -> str:
        """Help command"""
        if tool_name:
            if tool_name in self.TOOLS:
                tool = self.TOOLS[tool_name]
                return f"**{tool_name}**\n{tool['description']}\nUsage: `{tool['usage']}`"
            else:
                return f"Unknown tool: {tool_name}"
        else:
            available = self.get_available_tools()
            lines = ["**Available Tools:**"]
            for name in available:
                tool = self.TOOLS[name]
                lines.append(f"  /{name} - {tool['description']}")
            
            # Show locked tools as teaser
            locked = [n for n in self.TOOLS if n not in available]
            if locked:
                lines.append(f"\n🔒 {len(locked)} more tools to unlock!")
            
            return "\n".join(lines)
```

## 6.5 Sandboxing

Safe code execution using rootless Podman.

```python
class Sandbox:
    """Isolated execution environment"""
    
    def __init__(self, learner_id: str):
        self.learner_id = learner_id
        self.container_name = f"lmsp-sandbox-{learner_id}"
        self.container_id = None
    
    async def setup(self):
        """Create sandbox container"""
        
        # Create rootless Podman container
        result = await asyncio.create_subprocess_exec(
            "podman", "create",
            "--name", self.container_name,
            "--user", "1000:1000",  # Non-root
            "--memory", "512m",
            "--cpus", "1",
            "--network", "none",  # No network access
            "--read-only",
            "--tmpfs", "/tmp:rw,size=64m",
            "--security-opt", "no-new-privileges",
            "python:3.11-slim",
            "sleep", "infinity",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await result.communicate()
        self.container_id = stdout.decode().strip()
        
        # Start container
        await asyncio.create_subprocess_exec(
            "podman", "start", self.container_name
        )
    
    async def execute(
        self,
        code: str,
        test_input: Any,
        timeout_seconds: int = 10
    ) -> ExecutionResult:
        """Execute code safely in sandbox"""
        
        # Write code to temp file in container
        code_escaped = code.replace("'", "'\\''")
        await self._exec_in_container(f"echo '{code_escaped}' > /tmp/code.py")
        
        # Write test input
        input_json = json.dumps(test_input)
        await self._exec_in_container(f"echo '{input_json}' > /tmp/input.json")
        
        # Execute with timeout
        try:
            result = await asyncio.wait_for(
                self._exec_in_container(
                    "python /tmp/code.py < /tmp/input.json"
                ),
                timeout=timeout_seconds
            )
            return ExecutionResult(
                success=result.returncode == 0,
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode,
                timed_out=False
            )
        except asyncio.TimeoutError:
            # Kill runaway process
            await self._exec_in_container("pkill -9 python")
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="Execution timed out",
                exit_code=-1,
                timed_out=True
            )
    
    async def _exec_in_container(self, cmd: str) -> subprocess.CompletedProcess:
        """Execute command in sandbox container"""
        proc = await asyncio.create_subprocess_exec(
            "podman", "exec", self.container_name,
            "sh", "-c", cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=proc.returncode,
            stdout=stdout.decode(),
            stderr=stderr.decode()
        )
    
    async def cleanup(self):
        """Remove sandbox container"""
        await asyncio.create_subprocess_exec(
            "podman", "rm", "-f", self.container_name
        )
```

---

# Part VII: Game Mechanics & Progression

## 7.1 Experience Points & Leveling

### XP Sources

```python
XP_REWARDS = {
    # Challenge completion
    "challenge_complete": 100,
    "challenge_complete_no_hints": 150,
    "challenge_complete_speed_bonus": 50,  # Under par time
    "challenge_complete_first_try": 75,
    "challenge_complete_optimal_solution": 50,
    
    # Learning milestones
    "concept_unlocked": 200,
    "concept_practiced": 100,  # 3+ challenges
    "concept_mastered": 500,
    "concept_transcended": 1000,
    
    # Social
    "helped_another_player": 150,
    "taught_ai_student": 200,
    "won_competitive_match": 300,
    "completed_coop_challenge": 250,
    
    # Streaks
    "daily_streak_maintained": 50,  # Per day
    "weekly_goal_achieved": 500,
    "flow_state_achieved": 100,  # Per minute in flow
    
    # Discovery
    "tool_discovered": 50,
    "easter_egg_found": 200,
    "bug_reported": 300,
    "improvement_contributed": 1000
}
```

### Level Thresholds

```python
def xp_for_level(level: int) -> int:
    """XP required to reach a level"""
    # Exponential curve with diminishing returns
    if level <= 1:
        return 0
    return int(100 * (1.5 ** (level - 1)))

# Level 1:    0 XP
# Level 2:    100 XP
# Level 3:    150 XP
# Level 5:    337 XP
# Level 10:   2,562 XP
# Level 20:   97,656 XP
# Level 50:   ~25 million XP

LEVEL_TITLES = {
    1: "Blank Slate",
    5: "Novice Coder",
    10: "Apprentice",
    15: "Practitioner",
    20: "Journeyman",
    25: "Expert",
    30: "Master",
    40: "Grandmaster",
    50: "Legend"
}
```

## 7.2 Achievements & Trophies

```python
ACHIEVEMENTS = {
    # Beginner milestones
    "first_steps": {
        "name": "First Steps",
        "description": "Complete your first challenge",
        "icon": "🐣",
        "xp_reward": 100
    },
    "hello_world": {
        "name": "Hello, World!",
        "description": "Write your first Python program",
        "icon": "👋",
        "xp_reward": 100
    },
    
    # Progress milestones
    "level_10": {
        "name": "Getting Serious",
        "description": "Reach level 10",
        "icon": "📈",
        "xp_reward": 500
    },
    "concept_collector": {
        "name": "Concept Collector",
        "description": "Master 10 different concepts",
        "icon": "🎓",
        "xp_reward": 1000
    },
    
    # Skill achievements
    "speed_demon": {
        "name": "Speed Demon",
        "description": "Complete a challenge in under 60 seconds",
        "icon": "⚡",
        "xp_reward": 300
    },
    "perfectionist": {
        "name": "Perfectionist",
        "description": "Complete 10 challenges without any hints",
        "icon": "💎",
        "xp_reward": 500
    },
    "code_golfer": {
        "name": "Code Golfer",
        "description": "Achieve optimal solution length on 5 challenges",
        "icon": "⛳",
        "xp_reward": 400
    },
    
    # Social achievements
    "team_player": {
        "name": "Team Player",
        "description": "Complete 5 coop challenges",
        "icon": "🤝",
        "xp_reward": 400
    },
    "fierce_competitor": {
        "name": "Fierce Competitor",
        "description": "Win 10 competitive matches",
        "icon": "🏆",
        "xp_reward": 600
    },
    "patient_teacher": {
        "name": "Patient Teacher",
        "description": "Successfully teach 3 AI students",
        "icon": "📚",
        "xp_reward": 700
    },
    
    # Streak achievements
    "dedicated": {
        "name": "Dedicated",
        "description": "Maintain a 7-day streak",
        "icon": "🔥",
        "xp_reward": 400
    },
    "unstoppable": {
        "name": "Unstoppable",
        "description": "Maintain a 30-day streak",
        "icon": "🌟",
        "xp_reward": 2000
    },
    
    # Hidden/Easter eggs
    "flow_master": {
        "name": "Flow Master",
        "description": "Spend 30 minutes in flow state",
        "icon": "🧘",
        "xp_reward": 500,
        "hidden": True
    },
    "night_owl": {
        "name": "Night Owl",
        "description": "Code between 2am and 5am",
        "icon": "🦉",
        "xp_reward": 200,
        "hidden": True
    },
    "the_recursion": {
        "name": "The Recursion",
        "description": "Write a recursive function that works correctly",
        "icon": "🔄",
        "xp_reward": 300,
        "hidden": True
    }
}
```

## 7.3 Streaks & Daily Goals

```python
@dataclass
class DailyGoals:
    """Daily goals system"""
    
    # Standard daily goals
    challenges_to_complete: int = 3
    minutes_to_practice: int = 30
    concepts_to_review: int = 2
    
    # Progress
    challenges_completed: int = 0
    minutes_practiced: int = 0
    concepts_reviewed: int = 0
    
    @property
    def completion_percentage(self) -> float:
        """How much of daily goals completed"""
        return (
            (self.challenges_completed / self.challenges_to_complete) +
            (self.minutes_practiced / self.minutes_to_practice) +
            (self.concepts_reviewed / self.concepts_to_review)
        ) / 3.0
    
    @property
    def is_complete(self) -> bool:
        """All goals met"""
        return (
            self.challenges_completed >= self.challenges_to_complete and
            self.minutes_practiced >= self.minutes_to_practice and
            self.concepts_reviewed >= self.concepts_to_review
        )

@dataclass
class Streak:
    """Streak tracking"""
    
    current_streak: int = 0
    longest_streak: int = 0
    last_activity_date: Optional[date] = None
    
    def record_activity(self):
        """Record activity for today"""
        today = date.today()
        
        if self.last_activity_date is None:
            # First ever activity
            self.current_streak = 1
        elif self.last_activity_date == today:
            # Already recorded today
            pass
        elif self.last_activity_date == today - timedelta(days=1):
            # Consecutive day
            self.current_streak += 1
        else:
            # Streak broken
            self.current_streak = 1
        
        self.last_activity_date = today
        self.longest_streak = max(self.longest_streak, self.current_streak)
    
    def is_at_risk(self) -> bool:
        """True if streak will break if no activity today"""
        if self.last_activity_date is None:
            return False
        return self.last_activity_date < date.today()
```

## 7.4 Sound Design

### Sound Categories

```python
SOUND_EFFECTS = {
    # Input feedback
    "key_press": "gentle click, typewriter-inspired",
    "chord_complete": "soft chime, indicating valid input",
    "word_complete": "ascending tones, rewarding",
    "line_complete": "satisfying whoosh",
    
    # Success sounds
    "test_pass": "bright ding, video-game-like",
    "all_tests_pass": "triumphant fanfare, short",
    "challenge_complete": "achievement unlocked sound",
    "level_up": "epic ascending orchestral hit",
    "achievement_unlock": "special magical sound",
    
    # Error/feedback sounds
    "syntax_error": "soft buzz, not punishing",
    "test_fail": "low tone, encouraging retry",
    "hint_revealed": "soft bell, helpful",
    
    # Progress sounds
    "xp_gain": "coin collect sound",
    "streak_maintained": "fire crackling",
    "flow_state_entered": "ambient transition to focused mode",
    
    # Multiplayer sounds
    "player_joined": "welcome chime",
    "player_finished": "notification",
    "race_countdown": "beeps, then GO",
    "victory": "celebration",
    "defeat": "encouraging, not sad"
}

# Adaptive music system
MUSIC_STATES = {
    "menu": "calm, inviting",
    "learning": "focused, minimal",
    "flow_state": "energetic but not distracting",
    "challenge": "tension building",
    "victory": "triumphant",
    "multiplayer": "competitive energy"
}
```

### Haptic Patterns

```python
HAPTIC_PATTERNS = {
    # Input confirmation
    "valid_input": {"type": "pulse", "intensity": 0.3, "duration_ms": 50},
    "invalid_input": {"type": "double_pulse", "intensity": 0.5, "duration_ms": 100},
    
    # Success
    "test_pass": {"type": "wave", "intensity": 0.4, "duration_ms": 200},
    "challenge_complete": {"type": "celebration", "intensity": 0.8, "duration_ms": 500},
    
    # Error
    "syntax_error": {"type": "triple_buzz", "intensity": 0.6, "duration_ms": 150},
    "runtime_error": {"type": "rumble", "intensity": 0.5, "duration_ms": 300},
    
    # Flow state
    "flow_heartbeat": {"type": "pulse", "intensity": 0.2, "duration_ms": 50, "repeat_ms": 2000},
    
    # Multiplayer
    "player_nearby": {"type": "gentle_pulse", "intensity": 0.2, "duration_ms": 100},
    "race_start": {"type": "countdown", "pattern": [500, 500, 500, 1000]}
}
```

## 7.5 Visual Themes

```python
THEMES = {
    "default": {
        "name": "LMSP Classic",
        "background": "#1a1a2e",
        "foreground": "#eee",
        "accent": "#00d4ff",
        "success": "#00ff88",
        "error": "#ff4444",
        "warning": "#ffaa00"
    },
    "forest": {
        "name": "Forest Glade",
        "background": "#1a2f1a",
        "foreground": "#e0ffe0",
        "accent": "#88ff88",
        "success": "#00ff00",
        "error": "#ff6666",
        "warning": "#ffcc00"
    },
    "ocean": {
        "name": "Deep Ocean",
        "background": "#0a1628",
        "foreground": "#e0f0ff",
        "accent": "#00aaff",
        "success": "#00ffcc",
        "error": "#ff6688",
        "warning": "#ffbb33"
    },
    "sunset": {
        "name": "Sunset",
        "background": "#2a1a1a",
        "foreground": "#ffe0d0",
        "accent": "#ff6644",
        "success": "#ffaa00",
        "error": "#ff4444",
        "warning": "#ffdd00"
    },
    "high_contrast": {
        "name": "High Contrast",
        "background": "#000000",
        "foreground": "#ffffff",
        "accent": "#ffff00",
        "success": "#00ff00",
        "error": "#ff0000",
        "warning": "#ff8800"
    },
    "light": {
        "name": "Light Mode",
        "background": "#f5f5f5",
        "foreground": "#1a1a1a",
        "accent": "#0066cc",
        "success": "#008800",
        "error": "#cc0000",
        "warning": "#cc6600"
    }
}
```

---

# Part VIII: Data Architecture

## 8.1 Core Data Models

```python
# models/learner.py

@dataclass
class Learner:
    """Complete learner data model"""
    
    # Identity
    id: str
    username: str
    email: Optional[str]
    created_at: datetime
    last_seen: datetime
    
    # Profile
    profile: LearnerProfile
    preferences: LearnerPreferences
    
    # Progress
    xp: int
    level: int
    concepts: Dict[str, ConceptProgress]  # concept_id -> progress
    challenges_completed: Set[str]
    achievements: Set[str]
    
    # Statistics
    total_time_practiced: timedelta
    total_challenges_attempted: int
    total_challenges_completed: int
    average_completion_time: timedelta
    
    # Streaks
    streak: Streak
    daily_goals: DailyGoals
    
    # Social
    friends: List[str]  # learner_ids
    multiplayer_stats: MultiplayerStats
    
    # Spaced repetition
    review_queue: List[ReviewItem]
    retention_stats: Dict[str, float]  # concept_id -> retention

@dataclass
class ConceptProgress:
    """Progress on a single concept"""
    
    concept_id: str
    mastery_level: int  # 0-4
    first_seen: datetime
    last_practiced: datetime
    
    challenges_attempted: int
    challenges_completed: int
    total_time_spent: timedelta
    
    hints_used: int
    mistakes_made: int
    
    # For spaced repetition
    easiness_factor: float
    interval: timedelta
    next_review: datetime
    
    # Emotional history
    enjoyment_scores: List[float]  # Last 10 sessions
    frustration_scores: List[float]

@dataclass
class Session:
    """A learning session"""
    
    id: str
    learner_id: str
    started_at: datetime
    ended_at: Optional[datetime]
    
    # What was practiced
    concept_id: str
    challenges_attempted: List[str]
    challenges_completed: List[str]
    
    # Performance
    time_spent: timedelta
    xp_earned: int
    achievements_unlocked: List[str]
    
    # Emotional data
    emotional_samples: List[EmotionalState]
    flow_state_duration: timedelta
    
    # Multiplayer
    mode: Optional[str]
    other_players: List[str]
    match_result: Optional[str]  # "win", "loss", "draw"
```

## 8.2 Storage Schema

### SQLite Schema (Local)

```sql
-- Learner data
CREATE TABLE learners (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP,
    xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    profile_json TEXT,
    preferences_json TEXT
);

-- Concept progress
CREATE TABLE concept_progress (
    learner_id TEXT REFERENCES learners(id),
    concept_id TEXT NOT NULL,
    mastery_level INTEGER DEFAULT 0,
    first_seen TIMESTAMP,
    last_practiced TIMESTAMP,
    challenges_attempted INTEGER DEFAULT 0,
    challenges_completed INTEGER DEFAULT 0,
    total_time_seconds INTEGER DEFAULT 0,
    hints_used INTEGER DEFAULT 0,
    easiness_factor REAL DEFAULT 2.5,
    interval_seconds INTEGER DEFAULT 0,
    next_review TIMESTAMP,
    PRIMARY KEY (learner_id, concept_id)
);

-- Challenge completions
CREATE TABLE challenge_completions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    learner_id TEXT REFERENCES learners(id),
    challenge_id TEXT NOT NULL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    time_taken_seconds INTEGER,
    hints_used INTEGER,
    attempts INTEGER,
    code_submitted TEXT,
    xp_earned INTEGER
);

-- Sessions
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    learner_id TEXT REFERENCES learners(id),
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    concept_id TEXT,
    time_spent_seconds INTEGER,
    xp_earned INTEGER,
    mode TEXT,
    emotional_data_json TEXT
);

-- Achievements
CREATE TABLE achievements_earned (
    learner_id TEXT REFERENCES learners(id),
    achievement_id TEXT NOT NULL,
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (learner_id, achievement_id)
);

-- Streaks
CREATE TABLE streaks (
    learner_id TEXT PRIMARY KEY REFERENCES learners(id),
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_activity_date DATE
);

-- Review queue (spaced repetition)
CREATE TABLE review_queue (
    learner_id TEXT REFERENCES learners(id),
    concept_id TEXT NOT NULL,
    scheduled_for TIMESTAMP,
    priority INTEGER DEFAULT 0,
    PRIMARY KEY (learner_id, concept_id)
);

-- Multiplayer matches
CREATE TABLE matches (
    id TEXT PRIMARY KEY,
    mode TEXT NOT NULL,
    challenge_id TEXT NOT NULL,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    winner_id TEXT REFERENCES learners(id)
);

CREATE TABLE match_participants (
    match_id TEXT REFERENCES matches(id),
    learner_id TEXT REFERENCES learners(id),
    place INTEGER,
    xp_earned INTEGER,
    PRIMARY KEY (match_id, learner_id)
);

-- Indexes
CREATE INDEX idx_concept_progress_next_review ON concept_progress(next_review);
CREATE INDEX idx_sessions_learner ON sessions(learner_id);
CREATE INDEX idx_challenge_completions_learner ON challenge_completions(learner_id);
```

### File Structure

```
~/.lmsp/
├── config.toml              # User configuration
├── profile.db               # SQLite database
├── captures/                # Screenshots and recordings
│   ├── screenshots/
│   └── recordings/
├── cache/                   # Cached data
│   ├── challenges/          # Downloaded challenges
│   └── assets/              # Cached images/sounds
├── logs/                    # Session logs
│   └── sessions/
└── sandbox/                 # Podman sandbox data
    └── volumes/
```

## 8.3 API Contracts

### REST API (for cloud sync)

```yaml
openapi: 3.0.0
info:
  title: LMSP API
  version: 1.0.0

paths:
  /learners/{id}:
    get:
      summary: Get learner profile
      responses:
        200:
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Learner'
    
    put:
      summary: Update learner profile
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/LearnerUpdate'

  /learners/{id}/progress:
    get:
      summary: Get learning progress
      responses:
        200:
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/ConceptProgress'

  /challenges:
    get:
      summary: List available challenges
      parameters:
        - name: concept
          in: query
          schema:
            type: string
        - name: difficulty_min
          in: query
          schema:
            type: number
        - name: difficulty_max
          in: query
          schema:
            type: number
      responses:
        200:
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Challenge'

  /challenges/{id}/submit:
    post:
      summary: Submit challenge solution
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                code:
                  type: string
                time_taken_seconds:
                  type: integer
      responses:
        200:
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SubmissionResult'

  /multiplayer/matchmake:
    post:
      summary: Find a multiplayer match
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                mode:
                  type: string
                  enum: [coop, competitive, pair]
                skill_level:
                  type: number
      responses:
        200:
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Match'

components:
  schemas:
    Learner:
      type: object
      properties:
        id:
          type: string
        username:
          type: string
        xp:
          type: integer
        level:
          type: integer
        # ... etc

    ConceptProgress:
      type: object
      properties:
        concept_id:
          type: string
        mastery_level:
          type: integer
        # ... etc

    Challenge:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        concept:
          type: string
        difficulty:
          type: number
        # ... etc
```

---

# Part IX: Architecture Overview

## 9.1 System Components

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              LMSP SYSTEM ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────┐│
│  │                              USER INTERFACE LAYER                            ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ ││
│  │  │   Gamepad   │  │ Touchscreen │  │   Tablet    │  │      Keyboard       │ ││
│  │  │   Input     │  │   Input     │  │   Input     │  │      Fallback       │ ││
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ ││
│  │         │                │                │                    │            ││
│  │         └────────────────┴────────────────┴────────────────────┘            ││
│  │                                    │                                        ││
│  │                           ┌────────▼────────┐                               ││
│  │                           │  Input Manager  │                               ││
│  │                           └────────┬────────┘                               ││
│  └─────────────────────────────────────┼───────────────────────────────────────┘│
│                                        │                                        │
│  ┌─────────────────────────────────────┼───────────────────────────────────────┐│
│  │                              GAME ENGINE LAYER                               ││
│  │                                     │                                        ││
│  │  ┌──────────────┐    ┌──────────────▼──────────────┐    ┌──────────────┐    ││
│  │  │   Renderer   │◄───│       Game State Manager    │───►│    Audio     │    ││
│  │  │  (Terminal/  │    │                             │    │   Engine     │    ││
│  │  │     GUI)     │    │  - Current challenge        │    │              │    ││
│  │  └──────────────┘    │  - Player state             │    └──────────────┘    ││
│  │                      │  - Code editor state        │                        ││
│  │                      │  - Test results             │                        ││
│  │                      └──────────────┬──────────────┘                        ││
│  │                                     │                                        ││
│  └─────────────────────────────────────┼───────────────────────────────────────┘│
│                                        │                                        │
│  ┌─────────────────────────────────────┼───────────────────────────────────────┐│
│  │                              LEARNING ENGINE LAYER                           ││
│  │                                     │                                        ││
│  │  ┌───────────────┐  ┌──────────────▼──────────────┐  ┌───────────────┐      ││
│  │  │   Concept     │  │      Adaptive Learning      │  │    Spaced     │      ││
│  │  │    Graph      │◄─│         Engine              │─►│  Repetition   │      ││
│  │  │               │  │                             │  │               │      ││
│  │  └───────────────┘  │  - Difficulty adjustment    │  └───────────────┘      ││
│  │                      │  - Emotional tracking       │                        ││
│  │  ┌───────────────┐  │  - Goal analysis            │  ┌───────────────┐      ││
│  │  │   Challenge   │  │  - Curriculum generation    │  │   Progress    │      ││
│  │  │   Manager     │◄─│                             │─►│   Tracker     │      ││
│  │  │               │  └──────────────┬──────────────┘  │               │      ││
│  │  └───────────────┘                 │                 └───────────────┘      ││
│  │                                    │                                        ││
│  └────────────────────────────────────┼────────────────────────────────────────┘│
│                                       │                                         │
│  ┌────────────────────────────────────┼────────────────────────────────────────┐│
│  │                              EXECUTION LAYER                                 ││
│  │                                    │                                         ││
│  │  ┌──────────────┐    ┌─────────────▼─────────────┐    ┌──────────────┐      ││
│  │  │   Sandbox    │◄───│      Code Executor        │───►│  Debugger/   │      ││
│  │  │  (Podman)    │    │                           │    │  Time Travel │      ││
│  │  │              │    │  - Syntax validation      │    │              │      ││
│  │  └──────────────┘    │  - Test execution         │    └──────────────┘      ││
│  │                      │  - Performance profiling   │                         ││
│  │                      └───────────────────────────┘                          ││
│  │                                                                              ││
│  └──────────────────────────────────────────────────────────────────────────────┘│
│                                                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────────┐│
│  │                              MULTIPLAYER LAYER (player-zero)                  ││
│  │                                                                              ││
│  │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌────────────┐ ││
│  │  │   Session    │    │   Claude     │    │   Stream-    │    │   Match    │ ││
│  │  │   Manager    │◄──►│   Players    │◄──►│   JSON Bus   │◄──►│   Making   │ ││
│  │  │              │    │              │    │              │    │            │ ││
│  │  └──────────────┘    └──────────────┘    └──────────────┘    └────────────┘ ││
│  │                                                                              ││
│  └──────────────────────────────────────────────────────────────────────────────┘│
│                                                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────────┐│
│  │                              INTROSPECTION LAYER                              ││
│  │                                                                              ││
│  │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌────────────┐ ││
│  │  │  Screenshot  │    │    Video     │    │   Mosaic     │    │   Claude   │ ││
│  │  │   Capture    │    │   Recorder   │    │  Generator   │    │  Analysis  │ ││
│  │  │              │    │              │    │              │    │            │ ││
│  │  └──────────────┘    └──────────────┘    └──────────────┘    └────────────┘ ││
│  │                                                                              ││
│  └──────────────────────────────────────────────────────────────────────────────┘│
│                                                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────────┐│
│  │                              PERSISTENCE LAYER                                ││
│  │                                                                              ││
│  │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌────────────┐ ││
│  │  │   SQLite     │    │    File      │    │   Cloud      │    │   Config   │ ││
│  │  │   Database   │    │   Storage    │    │    Sync      │    │   Manager  │ ││
│  │  │              │    │              │    │  (optional)  │    │            │ ││
│  │  └──────────────┘    └──────────────┘    └──────────────┘    └────────────┘ ││
│  │                                                                              ││
│  └──────────────────────────────────────────────────────────────────────────────┘│
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 9.2 Module Structure

```
lmsp/
├── __init__.py
├── __main__.py              # Entry point
├── app.py                   # Main application
│
├── input/                   # Input handling
│   ├── __init__.py
│   ├── manager.py           # Input manager (coordinates all input modes)
│   ├── gamepad.py           # Gamepad input handling
│   ├── radial.py            # Radial thumbstick typing
│   ├── easy_mode.py         # Easy mode button mappings
│   ├── touch.py             # Touchscreen input
│   └── keyboard.py          # Keyboard fallback
│
├── game/                    # Game engine
│   ├── __init__.py
│   ├── engine.py            # Main game loop
│   ├── state.py             # Game state management
│   ├── renderer.py          # Display rendering
│   ├── audio.py             # Sound and music
│   └── haptics.py           # Haptic feedback
│
├── learning/                # Learning system
│   ├── __init__.py
│   ├── concepts.py          # Concept graph
│   ├── challenges.py        # Challenge management
│   ├── adaptive.py          # Adaptive difficulty
│   ├── spaced_rep.py        # Spaced repetition
│   ├── goals.py             # Goal analysis & curriculum generation
│   └── progress.py          # Progress tracking
│
├── execution/               # Code execution
│   ├── __init__.py
│   ├── sandbox.py           # Podman sandboxing
│   ├── executor.py          # Code execution
│   ├── validator.py         # Syntax validation
│   └── debugger.py          # Debugging support
│
├── multiplayer/             # Multiplayer (player-zero)
│   ├── __init__.py
│   ├── session.py           # Session management
│   ├── players.py           # Player types (human, claude)
│   ├── modes.py             # Game modes (coop, competitive, etc.)
│   ├── stream.py            # Stream-JSON protocol
│   └── matchmaking.py       # Matchmaking
│
├── introspection/           # TAS & debugging
│   ├── __init__.py
│   ├── screenshot.py        # Screenshot capture
│   ├── video.py             # Video recording
│   ├── mosaic.py            # Mosaic generation
│   ├── timetravel.py        # Time-travel debugging
│   ├── primitives.py        # Introspection commands
│   └── analysis.py          # Claude analysis
│
├── data/                    # Data management
│   ├── __init__.py
│   ├── models.py            # Data models
│   ├── database.py          # SQLite operations
│   ├── storage.py           # File storage
│   ├── sync.py              # Cloud sync
│   └── config.py            # Configuration
│
├── ui/                      # User interface components
│   ├── __init__.py
│   ├── menu.py              # Menu systems
│   ├── skill_tree.py        # Skill tree visualization
│   ├── challenge_view.py    # Challenge display
│   ├── code_editor.py       # Code editor widget
│   └── themes.py            # Visual themes
│
└── assets/                  # Static assets
    ├── sounds/              # Sound effects
    ├── music/               # Background music
    ├── radial_layouts/      # Radial typing layouts
    └── challenges/          # Challenge definitions (TOML)

player_zero/                 # Standalone multiplayer framework
├── __init__.py
├── core.py                  # Core framework
├── players/
│   ├── __init__.py
│   ├── human.py
│   └── claude.py
├── modes/
│   ├── __init__.py
│   ├── coop.py
│   ├── competitive.py
│   ├── pair.py
│   ├── teach.py
│   └── spectate.py
├── protocol.py              # Stream-JSON protocol
└── examples/                # Usage examples

radial/                      # Standalone radial typing library
├── __init__.py
├── core.py                  # Core radial system
├── layouts.py               # Layout definitions
├── learning.py              # Typing training
└── visualization.py         # Visual overlay
```

## 9.3 Key Interfaces

```python
# Core interfaces that tie the system together

class IInputProvider(Protocol):
    """Interface for input sources"""
    
    async def get_input(self) -> InputEvent:
        """Get next input event"""
        ...
    
    def get_input_mode(self) -> str:
        """Get current input mode name"""
        ...

class IChallenge(Protocol):
    """Interface for challenges"""
    
    @property
    def id(self) -> str: ...
    
    @property
    def concept(self) -> str: ...
    
    @property
    def difficulty(self) -> float: ...
    
    def get_template(self) -> str: ...
    
    def get_tests(self) -> List[TestCase]: ...
    
    def get_hints(self) -> List[str]: ...
    
    def validate_solution(self, code: str) -> ValidationResult: ...

class IPlayer(Protocol):
    """Interface for players (human or AI)"""
    
    @property
    def player_id(self) -> str: ...
    
    @property
    def name(self) -> str: ...
    
    @property
    def is_ai(self) -> bool: ...
    
    async def get_action(self) -> PlayerAction: ...
    
    async def receive_event(self, event: GameEvent): ...

class IGameMode(Protocol):
    """Interface for multiplayer game modes"""
    
    @property
    def name(self) -> str: ...
    
    @property
    def min_players(self) -> int: ...
    
    @property
    def max_players(self) -> int: ...
    
    async def setup(self, players: List[IPlayer], challenge: IChallenge): ...
    
    async def run(self) -> GameResult: ...
    
    async def on_player_action(self, player: IPlayer, action: PlayerAction): ...

class IExecutor(Protocol):
    """Interface for code execution"""
    
    async def execute(
        self,
        code: str,
        test_input: Any,
        timeout: int = 10
    ) -> ExecutionResult: ...
    
    async def validate_syntax(self, code: str) -> SyntaxResult: ...

class ILearningEngine(Protocol):
    """Interface for adaptive learning"""
    
    def get_next_challenge(
        self,
        learner: Learner,
        emotional_state: EmotionalState
    ) -> IChallenge: ...
    
    def update_progress(
        self,
        learner: Learner,
        challenge: IChallenge,
        result: ChallengeResult
    ): ...
    
    def generate_curriculum(
        self,
        learner: Learner,
        goal: str
    ) -> Curriculum: ...
```

---

# Part X: Implementation Plan

## 10.1 Phase 1: Core Foundation (Week 1-2)

### Goals
- Basic game loop running
- Keyboard input working
- Single challenge completable
- Local storage functioning

### Tasks
```
□ Project setup
  □ Create Python project structure
  □ Set up dependencies (pytest, rich, pygame, etc.)
  □ Create initial configuration system
  
□ Core data models
  □ Implement Learner model
  □ Implement Challenge model
  □ Implement ConceptProgress model
  □ Create SQLite schema
  
□ Basic game engine
  □ Terminal-based renderer
  □ Simple game state manager
  □ Keyboard input handler
  
□ Challenge system
  □ TOML challenge loader
  □ Test runner (sandboxed)
  □ Basic validation
  
□ First challenges
  □ Create 10 introductory challenges
  □ Variables concept
  □ Basic operators
```

### Success Criteria
- Can complete "Hello World" challenge
- Progress saved to database
- Tests run in sandbox

## 10.2 Phase 2: Gamepad & Radial (Week 3-4)

### Goals
- Gamepad input working
- Radial typing functional
- Easy mode implemented

### Tasks
```
□ Gamepad input
  □ Integrate pygame/SDL for gamepad
  □ Button mapping system
  □ Haptic feedback
  
□ Radial typing
  □ Core radial input system
  □ Visual overlay
  □ Character mapping
  □ Python token shortcuts
  
□ Easy mode
  □ Button-to-code mapping
  □ Smart completion
  □ Contextual suggestions
  
□ Input manager
  □ Mode switching
  □ Unified input events
  □ Training mode for radial
```

### Success Criteria
- Can complete challenge using only gamepad
- Radial typing at 10+ WPM after practice
- Easy mode generates correct Python code

## 10.3 Phase 3: Learning Engine (Week 5-6)

### Goals
- Adaptive difficulty working
- Spaced repetition active
- Concept graph navigable

### Tasks
```
□ Concept graph
  □ TOML concept definitions
  □ DAG traversal
  □ Unlock system
  
□ Adaptive engine
  □ Emotional state tracking
  □ Difficulty calculation
  □ Challenge selection
  
□ Spaced repetition
  □ Review scheduling
  □ Retention tracking
  □ Review sessions
  
□ Visual skill tree
  □ Graph visualization
  □ Progress display
  □ Navigation
```

### Success Criteria
- Difficulty adjusts based on performance
- Reviews appear at correct intervals
- Skill tree shows accurate progress

## 10.4 Phase 4: Multiplayer (Week 7-8)

### Goals
- 2-player coop working
- Claude player functional
- Stream-JSON protocol working

### Tasks
```
□ player-zero core
  □ Session manager
  □ Player base class
  □ Stream-JSON protocol
  
□ Human player
  □ Input routing
  □ State synchronization
  □ Display coordination
  
□ Claude player
  □ Process spawning
  □ System prompt design
  □ Event handling
  
□ Game modes
  □ Coop mode
  □ Competitive mode (basic)
  □ Spectate mode
```

### Success Criteria
- Two humans can solve challenge together
- Claude can play as partner
- Real-time state sharing works

## 10.5 Phase 5: Introspection (Week 9-10)

### Goals
- Screenshot with wireframe
- Time-travel debugging
- Video mosaic working

### Tasks
```
□ State capture
  □ Execution state snapshots
  □ Mental wireframe generation
  □ JSON serialization
  
□ Time travel
  □ State restoration
  □ Step back/forward
  □ Checkpoints
  
□ Recording
  □ Frame capture
  □ Mosaic generation
  □ WebP output
  
□ Analysis
  □ Claude integration
  □ Session analysis
  □ Recommendations
```

### Success Criteria
- Can rewind to any point in session
- Mosaic accurately represents session
- Claude can analyze and give feedback

## 10.6 Phase 6: Polish & Content (Week 11-12)

### Goals
- Full concept coverage
- Sound & visuals complete
- Production ready

### Tasks
```
□ Content
  □ All 6 concept levels
  □ 100+ challenges
  □ Achievement definitions
  
□ Audio
  □ Sound effects
  □ Background music
  □ Adaptive music system
  
□ Visuals
  □ Theme system
  □ Animations
  □ Particle effects
  
□ Polish
  □ Performance optimization
  □ Bug fixing
  □ Documentation
```

### Success Criteria
- All CodeSignal concepts covered
- Smooth 60fps gameplay
- <100ms input latency

---

# Part XI: Success Metrics

## 11.1 Learning Effectiveness

| Metric | Target | Measurement |
|--------|--------|-------------|
| Concept retention at 30 days | >80% | Quiz accuracy on concepts learned 30 days ago |
| Time to proficiency | <20 hours | Time to pass simulated CodeSignal test |
| Learner engagement | >70% return rate | Percentage returning within 7 days |
| Daily session length | 25-45 minutes | Average time per session |
| Flow state frequency | >30% of time | Detected flow state duration |

## 11.2 Input System Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| Radial typing speed | 20+ WPM @ 30 days | Words per minute after 30 days practice |
| Easy mode accuracy | >95% | Correct code generation rate |
| Input latency | <50ms | Time from button press to display |
| Accessibility coverage | 90%+ | Percentage of users who can use at least one mode |

## 11.3 Multiplayer Quality

| Metric | Target | Measurement |
|--------|--------|-------------|
| Matchmaking time | <30 seconds | Time to find match |
| State synchronization | <100ms | Latency between players |
| Claude player quality | "Human-like" | Blind test - can users tell? |
| Coop completion rate | >80% | Percentage of coop sessions completed |

## 11.4 System Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| Startup time | <2 seconds | Cold start to interactive |
| Memory usage | <500MB | Peak memory during gameplay |
| Sandbox overhead | <100ms | Time to execute code in sandbox |
| Database operations | <10ms | Average query time |

---

# Part XII: Appendices

## A. Radial Layout Specification

Full character mapping for radial thumbstick typing.

## B. Challenge Template Library

Complete set of challenge templates for each concept.

## C. Claude System Prompts

System prompts for different AI player personalities.

## D. Sound Design Guidelines

Detailed specifications for audio feedback.

## E. Accessibility Guidelines

Comprehensive accessibility requirements and solutions.

## F. API Reference

Complete API documentation for all modules.

---

# Conclusion

LMSP is not just a learning platform - it's a complete reimagining of how humans can learn to code. By combining:

- **Innovative input** (radial typing, easy mode, gamepad-native)
- **Adaptive intelligence** (emotional tracking, personalized difficulty)
- **Social learning** (multiplayer, AI companions, teaching mode)
- **Powerful introspection** (TAS capabilities, Claude analysis)
- **Recursive bootstrapping** (learn Python by building the Python learning game)

...we create a system that makes learning Python genuinely fun, accessible to everyone regardless of physical ability or prior experience, and effective at preparing learners for real-world coding challenges.

The goal is simple: **Never let another person give up on learning to code because it was boring.**

---

*Document generated for Palace autonomous development*
*Version: 1.0.0-ultrathink*
*Ready for implementation*
