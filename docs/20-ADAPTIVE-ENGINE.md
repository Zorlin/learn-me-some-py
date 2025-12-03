# Adaptive Learning Engine

**The brain that learns YOUR brain.**

---

## Overview

The adaptive learning engine is LMSP's secret sauce - it orchestrates spaced repetition, fun tracking, weakness detection, and project-driven curriculum generation to create a personalized learning experience.

This isn't a static algorithm. It's a relationship engine that gets better at teaching YOU over time.

## Core Components

### 1. LearnerProfile - Your Learning DNA

The `LearnerProfile` dataclass contains everything the system knows about how you learn:

```python
@dataclass
class LearnerProfile:
    """Everything we know about how YOU learn."""

    # Identity
    player_id: str

    # Learning patterns
    preferred_challenge_types: list[str] = field(default_factory=list)
    struggle_patterns: dict[str, int] = field(default_factory=dict)  # concept -> fail count
    mastery_levels: dict[str, int] = field(default_factory=dict)     # concept -> 0-4

    # Engagement patterns
    peak_focus_times: list[int] = field(default_factory=list)  # Hours of day
    session_duration_sweet_spot: int = 25  # minutes
    break_frequency_preference: int = 5    # challenges before suggesting break

    # Emotional patterns
    frustration_threshold: float = 0.6     # When to intervene
    flow_trigger_concepts: list[str] = field(default_factory=list)

    # Project goals
    current_goal: Optional[str] = None
    goal_concepts_needed: list[str] = field(default_factory=list)

    # Spaced repetition data
    concept_last_seen: dict[str, datetime] = field(default_factory=dict)
    concept_interval: dict[str, timedelta] = field(default_factory=dict)
```

**Key Fields:**

- **preferred_challenge_types**: Which types of challenges you enjoy (puzzle, speedrun, collection, creation)
- **struggle_patterns**: Concepts you've failed, tracked to detect genuine weakness vs bad luck
- **mastery_levels**: Your mastery of each concept (0-4: SEEN, UNLOCKED, PRACTICED, MASTERED, TRANSCENDED)
- **peak_focus_times**: Hours of day when you focus best
- **frustration_threshold**: How much frustration before intervention (adapts over time)
- **flow_trigger_concepts**: Concepts that reliably put you in flow state
- **current_goal**: Your project goal ("I want to build a Discord bot")
- **concept_last_seen**: When you last saw each concept (for spaced repetition)
- **concept_interval**: How long to wait before reviewing (Anki-style intervals)

### 2. AdaptiveEngine - The Core Loop

The `AdaptiveEngine` class orchestrates all adaptive learning features:

```python
class AdaptiveEngine:
    """The brain that learns your brain."""

    def __init__(self, profile: LearnerProfile):
        self.profile = profile
        self.emotional_state = EmotionalState()
        self._session_start = datetime.now()
        self._challenges_this_session = 0
```

**Main Methods:**

#### `observe_attempt(concept, success, time_seconds, hints_used)`

Records an attempt at a concept and updates the learning model:

```python
def observe_attempt(
    self,
    concept: str,
    success: bool,
    time_seconds: float,
    hints_used: int = 0
):
    """Record an attempt at a concept."""
    now = datetime.now()

    # Update last seen
    self.profile.concept_last_seen[concept] = now

    if success:
        # Increase mastery
        current = self.profile.mastery_levels.get(concept, 0)
        if hints_used == 0 and time_seconds < 60:
            # Quick, clean solve - big boost
            self.profile.mastery_levels[concept] = min(4, current + 1)
        else:
            # Slower or with hints - smaller boost
            self.profile.mastery_levels[concept] = min(4, current + 0.5)

        # Increase interval for spaced repetition
        current_interval = self.profile.concept_interval.get(
            concept, timedelta(hours=1)
        )
        self.profile.concept_interval[concept] = current_interval * 2

    else:
        # Record struggle
        self.profile.struggle_patterns[concept] = (
            self.profile.struggle_patterns.get(concept, 0) + 1
        )

        # Decrease interval - need to see this more often
        current_interval = self.profile.concept_interval.get(
            concept, timedelta(hours=1)
        )
        self.profile.concept_interval[concept] = current_interval / 2

    self._challenges_this_session += 1
```

**Mastery Boost Logic:**
- Quick solve (< 60s) with no hints: +1.0 mastery
- Slower or with hints: +0.5 mastery
- Failed attempt: No mastery change, but interval decreases

**Spaced Repetition Intervals:**
- Success: Double the interval (1h → 2h → 4h → 8h → ...)
- Failure: Halve the interval (8h → 4h → 2h → 1h)

#### `observe_emotion(dimension, value, context)`

Records emotional feedback to learn what makes you happy:

```python
def observe_emotion(self, dimension: EmotionalDimension, value: float, context: str = ""):
    """Record emotional feedback."""
    self.emotional_state.record(dimension, value, context)

    # Update profile based on patterns
    if dimension == EmotionalDimension.ENJOYMENT and value > 0.8:
        if context and context not in self.profile.flow_trigger_concepts:
            self.profile.flow_trigger_concepts.append(context)

    if dimension == EmotionalDimension.FRUSTRATION and value > 0.7:
        # Lower threshold for this player
        self.profile.frustration_threshold = max(
            0.3, self.profile.frustration_threshold - 0.05
        )
```

**Adaptive Emotional Thresholds:**
- High enjoyment (> 0.8) adds concept to flow triggers
- High frustration (> 0.7) lowers your frustration threshold by 0.05
- System becomes more protective if you get frustrated frequently

#### `recommend_next()` - The Decision Tree

The most important method - decides what you should do next:

```python
def recommend_next(self) -> AdaptiveRecommendation:
    """What should the player do next?"""

    # Priority 1: Do they need a break?
    if self._needs_break():
        return AdaptiveRecommendation(
            action="break",
            reason="You've been grinding hard. Take 5?"
        )

    # Priority 2: Are they frustrated? Offer something they're good at
    if self.emotional_state.get_frustration() > self.profile.frustration_threshold:
        flow_concept = self._find_flow_concept()
        if flow_concept:
            return AdaptiveRecommendation(
                action="challenge",
                concept=flow_concept,
                reason="Let's do something you enjoy to reset",
                confidence=0.8
            )

    # Priority 3: Spaced repetition - something due for review
    due_concept = self._find_due_for_review()
    if due_concept:
        return AdaptiveRecommendation(
            action="review",
            concept=due_concept,
            reason=f"Time to refresh {due_concept}",
            confidence=0.7
        )

    # Priority 4: Project goal - next step toward their goal
    if self.profile.current_goal:
        next_concept = self._find_next_for_goal()
        if next_concept:
            return AdaptiveRecommendation(
                action="project_step",
                concept=next_concept,
                reason=f"This brings you closer to: {self.profile.current_goal}",
                confidence=0.9
            )

    # Priority 5: Weakness drilling - something they struggle with
    weak_concept = self._find_weakness_to_drill()
    if weak_concept:
        return AdaptiveRecommendation(
            action="challenge",
            concept=weak_concept,
            reason="Let's strengthen this one",
            confidence=0.6
        )

    # Default: Something new and fun
    return AdaptiveRecommendation(
        action="challenge",
        reason="Explore something new!",
        confidence=0.5
    )
```

## The Priority System

### Priority 1: Break Detection

**Goal:** Prevent burnout and fatigue

```python
def _needs_break(self) -> bool:
    """Should we suggest a break?"""
    session_duration = (datetime.now() - self._session_start).total_seconds() / 60

    return (
        session_duration > self.profile.session_duration_sweet_spot or
        self._challenges_this_session >= self.profile.break_frequency_preference or
        self.emotional_state.needs_break()
    )
```

**Triggers:**
1. Session duration exceeds sweet spot (default: 25 minutes)
2. Completed too many challenges without break (default: 5)
3. Emotional state indicates burnout (frustration > 0.7 or enjoyment < 0.3)

**Recommendation:**
```
action: "break"
reason: "You've been grinding hard. Take 5?"
```

### Priority 2: Frustration Recovery

**Goal:** Reset emotional state with something enjoyable

```python
def _find_flow_concept(self) -> Optional[str]:
    """Find a concept that puts them in flow."""
    for concept in self.profile.flow_trigger_concepts:
        if self.profile.mastery_levels.get(concept, 0) >= 2:
            return concept
    return None
```

**Logic:**
- Check if frustration > threshold (default: 0.6, adapts down if player gets frustrated often)
- Find a concept from `flow_trigger_concepts` (tracked from high enjoyment readings)
- Must be at least PRACTICED (mastery >= 2) so they feel competent
- High confidence (0.8) because this is proven to work for this player

**Recommendation:**
```
action: "challenge"
concept: "list_comprehensions"  # (example: a concept they love)
reason: "Let's do something you enjoy to reset"
confidence: 0.8
```

### Priority 3: Spaced Repetition

**Goal:** Review concepts before they forget

```python
def _find_due_for_review(self) -> Optional[str]:
    """Find a concept due for spaced repetition review."""
    now = datetime.now()
    for concept, last_seen in self.profile.concept_last_seen.items():
        interval = self.profile.concept_interval.get(concept, timedelta(hours=1))
        if now - last_seen > interval:
            return concept
    return None
```

**Anki-Style Intervals:**

```
Success pattern:
  First success:  interval = 1 hour
  Second success: interval = 2 hours
  Third success:  interval = 4 hours
  Fourth success: interval = 8 hours
  ...continues doubling...

Failure pattern:
  First failure:  interval = 30 minutes
  Second failure: interval = 15 minutes
  Third failure:  interval = 7.5 minutes
  ...continues halving...
```

**Recommendation:**
```
action: "review"
concept: "for_loops"
reason: "Time to refresh for_loops"
confidence: 0.7
```

### Priority 4: Project-Driven Learning

**Goal:** Make progress toward learner's stated goal

```python
def _find_next_for_goal(self) -> Optional[str]:
    """Find the next concept needed for their project goal."""
    for concept in self.profile.goal_concepts_needed:
        if self.profile.mastery_levels.get(concept, 0) < 2:
            return concept
    return None
```

**How It Works:**

1. Learner states goal: "I want to build a Discord bot"
2. System (via Claude) analyzes goal → generates concept list:
   ```python
   goal_concepts_needed = [
       "variables",
       "functions",
       "async_await",
       "requests",
       "websockets",
       "event_handlers",
       ...
   ]
   ```
3. Engine recommends next unmastered concept from list
4. Highest confidence (0.9) because this directly serves learner's goal

**Recommendation:**
```
action: "project_step"
concept: "async_await"
reason: "This brings you closer to: Discord bot"
confidence: 0.9
```

### Priority 5: Weakness Drilling

**Goal:** Strengthen struggling concepts (gently)

```python
def _find_weakness_to_drill(self) -> Optional[str]:
    """Find a concept they struggle with that needs work."""
    # Sort by struggle count, pick the worst one they haven't mastered
    struggles = sorted(
        self.profile.struggle_patterns.items(),
        key=lambda x: x[1],
        reverse=True
    )
    for concept, count in struggles:
        if count >= 2 and self.profile.mastery_levels.get(concept, 0) < 3:
            return concept
    return None
```

**Gentle Drilling Logic:**
- Requires at least 2 failures (not just one bad day)
- Only drills if mastery < MASTERED (3)
- Sorts by struggle count, picks worst
- Lower confidence (0.6) because player may not be ready yet

**Recommendation:**
```
action: "challenge"
concept: "lambda_functions"
reason: "Let's strengthen this one"
confidence: 0.6
```

### Priority 6: Exploration (Default)

**Goal:** Keep learning fun and fresh

When no other priority applies, recommend something new:

```python
return AdaptiveRecommendation(
    action="challenge",
    reason="Explore something new!",
    confidence=0.5
)
```

**This happens when:**
- No break needed
- Not frustrated
- No reviews due
- No project goal set
- No significant weaknesses

## The AdaptiveRecommendation Type

```python
@dataclass
class AdaptiveRecommendation:
    """What the adaptive engine thinks you should do next."""
    action: str  # "challenge", "review", "break", "project_step"
    concept: Optional[str] = None
    challenge_id: Optional[str] = None
    reason: str = ""
    confidence: float = 0.5  # How confident are we this is right for you?
```

**Action Types:**

- **"challenge"**: Try a new challenge
- **"review"**: Review a previously learned concept
- **"break"**: Take a break
- **"project_step"**: Next step toward project goal

**Confidence Scores:**

- **0.9**: Project goal step (highest - directly serves stated goal)
- **0.8**: Flow concept (high - proven to work for this player)
- **0.7**: Spaced repetition (medium-high - scientifically proven)
- **0.6**: Weakness drilling (medium - might be ready, might not)
- **0.5**: Exploration (neutral - no strong signal)

## Persistence

The engine can save and load learner profiles:

```python
# Save profile
engine.save(Path("profile.json"))

# Load profile
engine = AdaptiveEngine.load(Path("profile.json"))
```

**Serialization Format:**

```json
{
  "player_id": "wings",
  "preferred_challenge_types": ["puzzle", "creation"],
  "struggle_patterns": {
    "lambda_functions": 3,
    "scope": 2
  },
  "mastery_levels": {
    "variables": 4,
    "for_loops": 3,
    "list_comprehensions": 2
  },
  "peak_focus_times": [9, 10, 14, 15, 20, 21],
  "session_duration_sweet_spot": 25,
  "break_frequency_preference": 5,
  "frustration_threshold": 0.55,
  "flow_trigger_concepts": ["list_comprehensions", "f_strings"],
  "current_goal": "Build a Discord bot",
  "goal_concepts_needed": [
    "async_await",
    "requests",
    "websockets"
  ],
  "concept_last_seen": {
    "variables": "2025-12-03T10:30:00",
    "for_loops": "2025-12-03T10:45:00"
  },
  "concept_interval": {
    "variables": 86400.0,
    "for_loops": 7200.0
  }
}
```

## Usage Example

```python
from lmsp.adaptive import AdaptiveEngine, LearnerProfile
from lmsp.input.emotional import EmotionalDimension

# Create profile
profile = LearnerProfile(player_id="wings")

# Create engine
engine = AdaptiveEngine(profile)

# Game loop
while learning:
    # Get recommendation
    rec = engine.recommend_next()

    if rec.action == "break":
        await suggest_break(rec.reason)
        continue

    # Run challenge
    result = await run_challenge(rec.concept)

    # Record attempt
    engine.observe_attempt(
        concept=rec.concept,
        success=result.passed,
        time_seconds=result.duration,
        hints_used=result.hints
    )

    # Get emotional feedback
    emotion = await emotional_prompt("How was that?")
    engine.observe_emotion(emotion.dimension, emotion.value, rec.concept)

    # Save progress
    engine.save(Path("profile.json"))
```

## Integration with FunTracker

The adaptive engine integrates with `FunTracker` (future implementation) to analyze engagement patterns:

```python
class FunTracker:
    """Tracks engagement patterns to understand what lights up YOUR brain."""

    def analyze_session(self, history: list[AttemptRecord]) -> FunProfile:
        """Build a profile of what this player enjoys."""

        patterns = {
            "puzzle": 0.0,      # Enjoys solving logic puzzles
            "speedrun": 0.0,    # Enjoys racing against time
            "collection": 0.0,  # Enjoys unlocking/collecting
            "creation": 0.0,    # Enjoys building things
            "competition": 0.0, # Enjoys competing with others
            "mastery": 0.0,     # Enjoys perfecting skills
        }

        for attempt in history:
            # High enjoyment + long session = found their thing
            if attempt.emotion.enjoyment > 0.7:
                time_weight = min(attempt.duration / 300, 2.0)  # Cap at 5 min

                # Map challenge type to fun pattern
                challenge_type = self.get_challenge_type(attempt.concept)
                patterns[challenge_type] += attempt.emotion.enjoyment * time_weight

        return FunProfile(patterns)
```

**Fun Pattern Detection:**
- High enjoyment (> 0.7) + long engagement (> 5 min) = strong signal
- Patterns tracked: puzzle, speedrun, collection, creation, competition, mastery
- Used to theme future challenges and select challenge types

## Integration with WeaknessDetector

```python
class WeaknessDetector:
    """Identifies struggle patterns and resurfaces concepts with support."""

    def detect_weakness(self, concept: str, history: list[AttemptRecord]) -> WeaknessSignal:
        """Analyze if this is a genuine weakness vs just a bad day."""

        failures = [a for a in history if a.concept == concept and not a.success]
        successes = [a for a in history if a.concept == concept and a.success]

        if len(failures) < 2:
            return None  # Not enough data

        # Check if failures are clustered or spread out
        if self.failures_are_clustered(failures):
            # Bad session, not genuine weakness
            return WeaknessSignal(
                concept=concept,
                severity="temporary",
                recommendation="Take a break, try tomorrow"
            )

        if len(failures) > len(successes) * 2:
            # Genuine struggle
            return WeaknessSignal(
                concept=concept,
                severity="needs_scaffolding",
                recommendation="Break into smaller pieces",
                prerequisites=self.get_unmastered_prereqs(concept)
            )
```

**Weakness Detection Logic:**
- Requires 2+ failures (one failure could be bad luck)
- Clustered failures = bad session, suggest break
- Failures > 2x successes = genuine weakness, needs scaffolding
- Checks for unmastered prerequisites to backtrack curriculum

## Integration with ProjectCurriculumGenerator

```python
class ProjectCurriculumGenerator:
    """
    "I want to build a Discord bot"
    → Generates curriculum backwards from goal
    → Themes all challenges around that goal
    """

    async def generate_curriculum(self, goal_description: str) -> Curriculum:
        """Use Claude to analyze goal and map to concepts."""

        # 1. Analyze what the goal requires
        analysis = await claude_analyze(f"""
        The user wants to build: {goal_description}

        What Python concepts are needed? Map to these levels:
        - Level 0: variables, types, print
        - Level 1: if/else, for, while, match
        - Level 2: lists, in operator, len, sorted
        - Level 3: functions, parameters, scope
        - Level 4: comprehensions, lambda, min/max key
        - Level 5: classes, self, methods
        - Level 6: patterns (container, median, dispatch)

        Also identify domain-specific concepts needed.
        """)

        # 2. Build learning path
        concepts_needed = self.parse_concepts(analysis)
        learning_path = self.topological_sort(concepts_needed)

        # 3. Theme challenges around the goal
        themed_challenges = []
        for concept in learning_path:
            themed_challenges.append(await self.theme_challenge(
                concept,
                goal=goal_description
            ))

        return Curriculum(
            goal=goal_description,
            path=learning_path,
            challenges=themed_challenges,
            estimated_time=self.estimate_time(learning_path)
        )
```

**Project-Driven Flow:**

1. Player states goal: "I want to build a Discord bot"
2. Claude analyzes goal → maps to concepts needed
3. System generates learning path (topologically sorted by prerequisites)
4. Challenges themed around Discord bot (e.g., "Parse Discord message" instead of "Parse string")
5. Learner builds toward concrete goal instead of abstract exercises

## Why This Matters

Traditional learning is **one-size-fits-all**:
- Same lessons in same order
- No adaptation to individual patterns
- No emotional awareness
- No project alignment

LMSP's adaptive engine is **personalized**:
- Learns YOUR dopamine patterns
- Adapts to YOUR frustration threshold
- Respects YOUR session duration preferences
- Aligns with YOUR project goals
- Reviews concepts on YOUR schedule

**Result:** Faster learning, better retention, more fun.

---

*Self-teaching note: This file demonstrates dataclasses with default_factory, type hints with Optional and dict, datetime/timedelta, JSON serialization patterns, and the Strategy pattern (implicit in recommend_next). The learner will encounter this after mastering classes (Level 5+).*
