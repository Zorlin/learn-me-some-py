# Emotional Input System

**"Pull the right trigger progressively until you feel you've communicated how happy you are."**

---

## Overview

LMSP's emotional input system replaces binary feedback (thumbs up/down) with **analog emotional gradients** via controller triggers.

This isn't a survey. This is real-time, granular, intuitive emotional expression.

## The Problem with Binary Feedback

Traditional learning apps ask:
- "Did you enjoy this?" → Yes/No
- "Was this helpful?" → Star rating
- "How do you feel?" → Pick emoji

**Problems:**
1. Binary choices lose nuance
2. Star ratings require conscious quantification
3. Emoji selection breaks flow
4. All require stopping to think about how to express emotion

## The Analog Solution

LMSP uses controller triggers as emotional gradient input:

```
"How are you feeling?"

  [RT ████████░░] Pull right for happiness
  [LT ██░░░░░░░░] Pull left for frustration
  [Y] Complex response

  Press A to confirm
```

**Why This Works:**
- **Analog**: 0.0 to 1.0 gradient, not binary
- **Fast**: Pull trigger, don't think
- **Intuitive**: Pressure = intensity
- **Flow-preserving**: Takes < 2 seconds
- **Honest**: Hard to overthink analog input

## Core Types

### EmotionalDimension

Enum defining the dimensions of emotion we track:

```python
class EmotionalDimension(Enum):
    """The dimensions of emotional feedback we track."""
    ENJOYMENT = "enjoyment"           # RT: How fun was that?
    FRUSTRATION = "frustration"       # LT: How frustrating?
    CONFIDENCE = "confidence"         # How sure are you?
    CURIOSITY = "curiosity"           # Want to explore more?
    FLOW = "flow"                     # Were you in the zone?
```

**Dimensions Explained:**

- **ENJOYMENT**: Dopamine hit, fun factor, satisfaction
- **FRUSTRATION**: Confusion, annoyance, stuck feeling
- **CONFIDENCE**: How sure you are in your understanding
- **CURIOSITY**: Desire to learn more about this topic
- **FLOW**: Were you in the zone, losing track of time?

**Usage:**
- Most prompts use ENJOYMENT (RT) vs FRUSTRATION (LT)
- CONFIDENCE used after solving to gauge understanding
- CURIOSITY used to suggest exploration vs drilling
- FLOW detected algorithmically (high enjoyment + low frustration)

### EmotionalSample

A single emotional reading at a moment in time:

```python
@dataclass
class EmotionalSample:
    """A single emotional reading at a moment in time."""
    timestamp: float
    dimension: EmotionalDimension
    value: float  # 0.0 to 1.0, analog from trigger
    context: str  # What were they doing when sampled?

    def __post_init__(self):
        self.value = max(0.0, min(1.0, self.value))
```

**Fields:**

- **timestamp**: `time.time()` when sample was recorded
- **dimension**: Which emotional dimension (ENJOYMENT, FRUSTRATION, etc.)
- **value**: Analog value from 0.0 (none) to 1.0 (maximum)
- **context**: What concept/challenge they were working on

**Value Clamping:**

The `__post_init__` method ensures value stays in [0.0, 1.0]:
```python
self.value = max(0.0, min(1.0, self.value))
```

This handles edge cases like controller drift or over-zealous pulls.

### EmotionalState

Tracks emotional state over time with rolling averages:

```python
@dataclass
class EmotionalState:
    """Current emotional state of the player."""
    samples: list[EmotionalSample] = field(default_factory=list)

    # Rolling averages per dimension
    _averages: dict[EmotionalDimension, float] = field(default_factory=dict)

    def record(self, dimension: EmotionalDimension, value: float, context: str = ""):
        """Record an emotional sample."""
        sample = EmotionalSample(
            timestamp=time.time(),
            dimension=dimension,
            value=value,
            context=context
        )
        self.samples.append(sample)
        self._update_average(dimension)

    def _update_average(self, dimension: EmotionalDimension):
        """Update rolling average for a dimension."""
        recent = [s for s in self.samples[-50:] if s.dimension == dimension]
        if recent:
            self._averages[dimension] = sum(s.value for s in recent) / len(recent)
```

**Rolling Average Logic:**

- Keeps last 50 samples per dimension
- Averages only matching dimension samples
- Updates on every `record()` call
- Prevents single outliers from skewing state

**Getter Methods:**

```python
def get_enjoyment(self) -> float:
    """How much are they enjoying this?"""
    return self._averages.get(EmotionalDimension.ENJOYMENT, 0.5)

def get_frustration(self) -> float:
    """How frustrated are they?"""
    return self._averages.get(EmotionalDimension.FRUSTRATION, 0.0)
```

**Default Values:**
- ENJOYMENT defaults to 0.5 (neutral) if no samples
- FRUSTRATION defaults to 0.0 (assume not frustrated until proven otherwise)

**State Detection:**

```python
def is_in_flow(self) -> bool:
    """Are they in a flow state? High enjoyment, low frustration."""
    return self.get_enjoyment() > 0.7 and self.get_frustration() < 0.3

def needs_break(self) -> bool:
    """Should we suggest a break?"""
    return self.get_frustration() > 0.7 or (
        self.get_enjoyment() < 0.3 and len(self.samples) > 20
    )
```

**Flow State Detection:**
- Enjoyment > 0.7 (having fun)
- Frustration < 0.3 (not struggling)
- When in flow, auto-advance without interrupting

**Break Detection:**
- Frustration > 0.7 (highly frustrated)
- OR enjoyment < 0.3 for 20+ samples (disengaged)

## EmotionalPrompt - The Interactive Prompt

The `EmotionalPrompt` class handles the interactive emotional input flow:

```python
class EmotionalPrompt:
    """
    A prompt that asks for emotional feedback via controller.

    Usage:
        prompt = EmotionalPrompt(
            question="How are you feeling?",
            right_trigger="Pull to show happiness",
            left_trigger="Pull to show frustration",
            y_button="Press for complex answer"
        )
        response = await prompt.show(controller)
    """

    def __init__(
        self,
        question: str,
        right_trigger: str = "Happy",
        left_trigger: str = "Frustrated",
        y_button: Optional[str] = "More options",
        on_complex: Optional[Callable] = None
    ):
        self.question = question
        self.right_trigger = right_trigger
        self.left_trigger = left_trigger
        self.y_button = y_button
        self.on_complex = on_complex

        self._rt_value = 0.0
        self._lt_value = 0.0
        self._confirmed = False
        self._complex_requested = False
```

**Parameters:**

- **question**: The prompt text ("How was that challenge?")
- **right_trigger**: Label for RT (default: "Happy")
- **left_trigger**: Label for LT (default: "Frustrated")
- **y_button**: Label for Y (default: "More options")
- **on_complex**: Callback for complex response (opens text/selection menu)

### State Management

```python
def update(self, rt: float, lt: float, y_pressed: bool, a_pressed: bool):
    """Update from controller state."""
    self._rt_value = rt
    self._lt_value = lt

    if y_pressed and self.y_button:
        self._complex_requested = True

    if a_pressed and (rt > 0.1 or lt > 0.1):
        self._confirmed = True
```

**Update Logic:**
- Called every frame with current controller state
- RT/LT values update continuously as player adjusts
- Y button flags complex response request
- A button confirms ONLY if RT or LT > 0.1 (prevents accidental empty confirms)

**Properties:**

```python
@property
def is_confirmed(self) -> bool:
    return self._confirmed

@property
def wants_complex(self) -> bool:
    return self._complex_requested
```

### Response Extraction

```python
def get_response(self) -> tuple[EmotionalDimension, float]:
    """Get the emotional response."""
    if self._rt_value > self._lt_value:
        return EmotionalDimension.ENJOYMENT, self._rt_value
    else:
        return EmotionalDimension.FRUSTRATION, self._lt_value
```

**Response Logic:**
- Whichever trigger is pulled harder wins
- Returns (dimension, value) tuple
- RT > LT → (ENJOYMENT, rt_value)
- LT >= RT → (FRUSTRATION, lt_value)

**Example:**
```python
# Player pulls RT to 0.8, LT to 0.2
dimension, value = prompt.get_response()
# Returns: (EmotionalDimension.ENJOYMENT, 0.8)
```

### Rendering

```python
def render(self) -> str:
    """Render the prompt for display."""
    lines = [
        self.question,
        "",
        f"  [RT {'█' * int(self._rt_value * 10):10}] {self.right_trigger}",
        f"  [LT {'█' * int(self._lt_value * 10):10}] {self.left_trigger}",
    ]
    if self.y_button:
        lines.append(f"  [Y] {self.y_button}")
    lines.append("")
    lines.append("  Press A to confirm")
    return "\n".join(lines)
```

**Example Output:**

```
How was that challenge?

  [RT ████████░░] Satisfying
  [LT ██░░░░░░░░] Frustrating
  [Y] More complex answer

  Press A to confirm
```

**Visual Feedback:**
- RT/LT bars show 10 blocks (█) based on value (0.0 to 1.0)
- `int(value * 10)` converts 0.8 → 8 blocks
- Bars update in real-time as player adjusts triggers

## Usage Patterns

### Simple Enjoyment Check

```python
prompt = EmotionalPrompt(
    question="How was that?",
    right_trigger="Satisfying",
    left_trigger="Frustrating"
)

while not prompt.is_confirmed:
    rt, lt, y, a = gamepad.get_state()
    prompt.update(rt, lt, y, a)
    screen.render(prompt.render())

dimension, value = prompt.get_response()
engine.observe_emotion(dimension, value, context="list_comprehensions")
```

### Confidence Check

```python
prompt = EmotionalPrompt(
    question="How confident are you in your understanding?",
    right_trigger="Very confident",
    left_trigger="Not confident"
)

# ... same loop ...

# Map to CONFIDENCE dimension
if dimension == EmotionalDimension.ENJOYMENT:
    dimension = EmotionalDimension.CONFIDENCE
engine.observe_emotion(dimension, value, context="lambda_functions")
```

### Complex Response

```python
prompt = EmotionalPrompt(
    question="How are you feeling?",
    right_trigger="Happy",
    left_trigger="Frustrated",
    y_button="It's complicated",
    on_complex=show_complex_menu
)

while not prompt.is_confirmed and not prompt.wants_complex:
    rt, lt, y, a = gamepad.get_state()
    prompt.update(rt, lt, y, a)
    screen.render(prompt.render())

if prompt.wants_complex:
    # Open text input or selection menu
    response = await prompt.on_complex()
else:
    dimension, value = prompt.get_response()
```

## Integration with Adaptive Engine

The emotional input system feeds directly into the adaptive engine:

```python
# In game loop
emotion_prompt = EmotionalPrompt("How was that?")
dimension, value = await get_emotion(emotion_prompt)

# Record emotional feedback
engine.observe_emotion(dimension, value, context=current_concept)

# Adaptive engine uses this to:
# 1. Detect flow state (auto-advance)
# 2. Detect frustration (offer break or flow concept)
# 3. Identify flow trigger concepts (high enjoyment)
# 4. Adjust frustration threshold over time
```

## Emotional Checkpoints

Challenges can define emotional checkpoints in their TOML:

```toml
[emotional_checkpoints]
after_first_test_pass = "How satisfying was that first green test?"
after_completion = "How do you feel about this challenge overall?"
after_speedrun = "That was fast! How did it feel?"
```

**Usage:**
```python
# After first test passes
if tests_passing == 1:
    emotion = await emotional_checkpoint(
        challenge.emotional_checkpoints.after_first_test_pass
    )
    engine.observe_emotion(emotion.dimension, emotion.value, context)
```

## Why Analog Triggers?

**Traditional Approach:**
```
How do you feel?
[ ] Happy
[ ] Neutral
[ ] Frustrated
```

**Problems:**
- Binary (3 options)
- Requires stopping to think
- Breaks flow
- Hard to express nuance ("I'm 70% happy, 20% frustrated")

**Analog Trigger Approach:**
```
[RT ███████░░░] Happy
[LT ██░░░░░░░░] Frustrated
```

**Advantages:**
- Infinite gradations (0.0 to 1.0)
- Intuitive (pressure = intensity)
- Fast (< 2 seconds)
- Honest (hard to overthink)
- Can express mixed emotions (RT=0.7, LT=0.3)

## Future Enhancements

### Haptic Feedback Integration

```python
def render_with_haptics(self):
    """Render with haptic feedback on triggers."""
    # Rumble RT proportional to enjoyment
    gamepad.rumble_rt(self._rt_value * 0.3)

    # Rumble LT proportional to frustration
    gamepad.rumble_lt(self._lt_value * 0.3)
```

### Speed-Based Engagement Detection

```python
def detect_engagement(self) -> float:
    """How quickly did they respond?"""
    time_to_confirm = self._confirmed_time - self._shown_time

    if time_to_confirm < 1.0:
        # Fast response = high engagement
        return 1.0
    elif time_to_confirm < 3.0:
        # Normal response
        return 0.7
    else:
        # Slow response = low engagement
        return 0.3
```

### Bimodal Emotion Detection

```python
def get_bimodal_response(self) -> tuple[EmotionalDimension, float, EmotionalDimension, float]:
    """Detect mixed emotions (both triggers pulled)."""
    if self._rt_value > 0.3 and self._lt_value > 0.3:
        # Mixed emotions
        return (
            EmotionalDimension.ENJOYMENT, self._rt_value,
            EmotionalDimension.FRUSTRATION, self._lt_value
        )
```

**Use Case:**
"That was satisfying to solve but also really frustrating!"
- RT: 0.8 (enjoyed the challenge)
- LT: 0.6 (but it was hard)

---

*Self-teaching note: This file demonstrates dataclasses (Level 5), enums (Level 2+), type hints (Professional Python), properties and methods (Level 5), and default_factory for mutable defaults (important gotcha!).*
