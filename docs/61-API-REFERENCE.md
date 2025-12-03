# API Reference

Complete API documentation for LMSP core modules.

---

## Overview

LMSP provides Python APIs for:
- **Emotional Input** - Analog emotional feedback via controller triggers
- **Adaptive Engine** - AI-powered learning personalization
- **Player-Zero Integration** - Multiplayer and AI player simulation
- **TAS System** - Tool-assisted learning (record, replay, rewind)
- **Introspection** - Screenshots, video, and state analysis

---

## Emotional Input API

Module: `lmsp.input.emotional`

### Classes

#### `EmotionalDimension`

Enum representing types of emotional input.

```python
from lmsp.input.emotional import EmotionalDimension

class EmotionalDimension(Enum):
    ENJOYMENT = "enjoyment"       # Right trigger: positive emotion
    FRUSTRATION = "frustration"   # Left trigger: negative emotion
    COMPLEX = "complex"           # Y button: needs text/selection
```

**Usage:**
```python
dimension = EmotionalDimension.ENJOYMENT
print(dimension.value)  # "enjoyment"
```

---

#### `EmotionalPrompt`

Interactive prompt for capturing emotional feedback via controller triggers.

**Constructor:**
```python
EmotionalPrompt(
    question: str,
    right_trigger: str = "Happy",
    left_trigger: str = "Frustrated",
    y_button: str | None = "More options"
)
```

**Parameters:**
- `question`: Text prompt to display to user
- `right_trigger`: Label for right trigger (positive emotion)
- `left_trigger`: Label for left trigger (negative emotion)
- `y_button`: Label for Y button (complex response), None to hide

**Attributes:**
```python
prompt.question: str                    # Current question
prompt.right_trigger: str               # RT label
prompt.left_trigger: str                # LT label
prompt.y_button: str | None             # Y button label
prompt.is_confirmed: bool               # True when A pressed
prompt.rt_value: float                  # Current RT pressure (0.0-1.0)
prompt.lt_value: float                  # Current LT pressure (0.0-1.0)
prompt.y_pressed: bool                  # True if Y pressed
```

**Methods:**

##### `update(rt: float, lt: float, y_pressed: bool, a_pressed: bool) -> None`

Update prompt state from controller input.

```python
# Example: Update from gamepad
prompt = EmotionalPrompt("How was that?")

while not prompt.is_confirmed:
    gamepad_state = get_gamepad()
    prompt.update(
        rt=gamepad_state.right_trigger,
        lt=gamepad_state.left_trigger,
        y_pressed=gamepad_state.y,
        a_pressed=gamepad_state.a
    )
    display(prompt.render())
```

**Parameters:**
- `rt`: Right trigger pressure (0.0 to 1.0)
- `lt`: Left trigger pressure (0.0 to 1.0)
- `y_pressed`: Y button state
- `a_pressed`: A button confirms selection

##### `render() -> str`

Render visual representation with progress bars.

```python
prompt = EmotionalPrompt(
    question="How satisfying was that?",
    right_trigger="Satisfying",
    left_trigger="Frustrating"
)
prompt.update(rt=0.7, lt=0.2, y_pressed=False, a_pressed=False)

print(prompt.render())
```

**Output:**
```
How satisfying was that?

  [RT ███████░░░] Satisfying
  [LT ██░░░░░░░░] Frustrating
  [Y] More options

  Press A to confirm
```

##### `get_response() -> tuple[EmotionalDimension, float]`

Get confirmed emotional response.

```python
prompt.update(rt=0.8, lt=0.0, y_pressed=False, a_pressed=True)

if prompt.is_confirmed:
    dimension, value = prompt.get_response()
    # dimension = EmotionalDimension.ENJOYMENT
    # value = 0.8
```

**Returns:** Tuple of (dimension, value)
- If RT > LT: (ENJOYMENT, rt_value)
- If LT > RT: (FRUSTRATION, lt_value)
- If Y pressed: (COMPLEX, 0.0)

**Raises:** `ValueError` if not confirmed

---

#### `EmotionalState`

Tracks emotional state over time and detects patterns.

**Constructor:**
```python
EmotionalState()
```

**Attributes:**
```python
state.history: list[EmotionalRecord]    # All recorded emotions
state.current_session_start: float      # Session start timestamp
```

**Methods:**

##### `record(dimension: EmotionalDimension, value: float, context: str = "") -> None`

Record an emotional response.

```python
state = EmotionalState()

state.record(EmotionalDimension.ENJOYMENT, 0.9, context="list_comprehensions")
state.record(EmotionalDimension.FRUSTRATION, 0.3, context="lambda_functions")
```

**Parameters:**
- `dimension`: Type of emotion
- `value`: Intensity (0.0 to 1.0)
- `context`: What triggered this emotion (concept name, challenge ID, etc.)

##### `get_recent(count: int = 5) -> list[EmotionalRecord]`

Get N most recent emotional records.

```python
recent = state.get_recent(count=3)
for record in recent:
    print(f"{record.timestamp}: {record.dimension.value} = {record.value}")
```

##### `is_in_flow() -> bool`

Detect if learner is in flow state.

```python
if state.is_in_flow():
    print("Flow detected! Auto-advancing to next challenge...")
```

**Flow criteria:**
- High enjoyment (>0.7) in recent records
- Low frustration (<0.3)
- Consistent pattern over time
- No complex responses

##### `needs_break() -> bool`

Detect if learner needs a break.

```python
if state.needs_break():
    print("High frustration detected. Suggesting break...")
```

**Break criteria:**
- High frustration (>0.6) in recent records
- Declining enjoyment over time
- Session duration >45 minutes
- Multiple complex responses

##### `get_average_enjoyment(context: str | None = None) -> float`

Get average enjoyment, optionally filtered by context.

```python
# Overall enjoyment
avg = state.get_average_enjoyment()

# Enjoyment for specific concept
avg = state.get_average_enjoyment(context="list_comprehensions")
```

##### `get_average_frustration(context: str | None = None) -> float`

Get average frustration, optionally filtered by context.

```python
frustration = state.get_average_frustration(context="lambda_functions")
if frustration > 0.5:
    print("Lambda functions are causing struggle")
```

**Complete Example:**
```python
from lmsp.input.emotional import EmotionalPrompt, EmotionalState, EmotionalDimension

# Track state over session
state = EmotionalState()

# After each challenge
prompt = EmotionalPrompt(
    question="How was that challenge?",
    right_trigger="Satisfying",
    left_trigger="Confusing"
)

# Collect input
while not prompt.is_confirmed:
    # Update from controller
    prompt.update(rt=gamepad.rt, lt=gamepad.lt, y_pressed=gamepad.y, a_pressed=gamepad.a)
    display(prompt.render())

# Record response
dimension, value = prompt.get_response()
state.record(dimension, value, context=current_challenge)

# Check for flow state
if state.is_in_flow():
    auto_advance_to_next_challenge()

# Check for break needed
if state.needs_break():
    suggest_break()
```

---

## Adaptive Engine API

Module: `lmsp.adaptive.engine`

### Classes

#### `AttemptRecord`

Records a single challenge attempt.

**Dataclass:**
```python
@dataclass
class AttemptRecord:
    concept: str              # Concept being practiced
    success: bool             # Passed all tests?
    time_seconds: float       # Time to complete
    hints_used: int           # Number of hints requested
    timestamp: float          # When attempt occurred
    emotion: EmotionalRecord | None  # Emotional feedback
```

---

#### `LearnerProfile`

Stores learner's progress and preferences.

**Constructor:**
```python
LearnerProfile(player_id: str)
```

**Attributes:**
```python
profile.player_id: str                          # Unique player identifier
profile.mastery: dict[str, int]                 # concept_id -> mastery level (0-4)
profile.attempts: list[AttemptRecord]           # All challenge attempts
profile.fun_profile: dict[str, float]           # Fun pattern preferences
profile.last_review: dict[str, float]           # concept_id -> last review timestamp
profile.weaknesses: dict[str, int]              # concept_id -> failure count
```

**Methods:**

##### `set_mastery(concept: str, level: int) -> None`

Set mastery level for a concept.

```python
profile = LearnerProfile("wings")
profile.set_mastery("list_comprehensions", 3)  # Mastered
```

##### `get_mastery(concept: str) -> int`

Get mastery level (0 if never seen).

```python
level = profile.get_mastery("lambda_functions")
# 0 = Not unlocked
# 1 = Unlocked
# 2 = Practiced
# 3 = Mastered
# 4 = Transcended
```

##### `add_attempt(record: AttemptRecord) -> None`

Record a challenge attempt.

```python
profile.add_attempt(AttemptRecord(
    concept="list_comprehensions",
    success=True,
    time_seconds=45.2,
    hints_used=1,
    timestamp=time.time(),
    emotion=None
))
```

##### `get_attempts_for_concept(concept: str) -> list[AttemptRecord]`

Get all attempts for a specific concept.

```python
attempts = profile.get_attempts_for_concept("lambda_functions")
success_rate = sum(a.success for a in attempts) / len(attempts)
```

##### `to_dict() -> dict`

Serialize to dictionary for JSON export.

```python
data = profile.to_dict()
with open("profile.json", "w") as f:
    json.dump(data, f, indent=2)
```

##### `from_dict(data: dict) -> LearnerProfile` (classmethod)

Deserialize from dictionary.

```python
with open("profile.json") as f:
    data = json.load(f)
profile = LearnerProfile.from_dict(data)
```

---

#### `Recommendation`

Represents a learning recommendation from the adaptive engine.

**Dataclass:**
```python
@dataclass
class Recommendation:
    action: str               # "challenge" | "review" | "break" | "project_step"
    concept: str | None       # Concept to work on (if applicable)
    reason: str               # Why this recommendation
    options: list[str]        # Alternative concepts (if action = "challenge")
    auto_advance: bool        # Skip menu, go directly to concept
```

**Example:**
```python
rec = Recommendation(
    action="challenge",
    concept="lambda_functions",
    reason="This brings you closer to: Discord bot",
    options=["lambda_functions", "comprehensions", "map_filter"],
    auto_advance=False
)
```

---

#### `AdaptiveEngine`

Core adaptive learning engine.

**Constructor:**
```python
AdaptiveEngine(profile: LearnerProfile)
```

**Methods:**

##### `observe_attempt(concept: str, success: bool, time_seconds: float, hints_used: int = 0) -> None`

Record a challenge attempt.

```python
engine = AdaptiveEngine(profile)

# After completing a challenge
engine.observe_attempt(
    concept="list_comprehensions",
    success=True,
    time_seconds=67.5,
    hints_used=2
)
```

##### `observe_emotion(dimension: EmotionalDimension, value: float, context: str = "") -> None`

Record emotional feedback.

```python
engine.observe_emotion(
    dimension=EmotionalDimension.ENJOYMENT,
    value=0.9,
    context="list_comprehensions"
)
```

##### `recommend_next() -> Recommendation`

Get next learning recommendation.

```python
rec = engine.recommend_next()

if rec.action == "break":
    print(f"Suggestion: {rec.reason}")
    await suggest_break()
elif rec.action == "challenge":
    if rec.auto_advance:
        # Flow state - go directly
        start_challenge(rec.concept)
    else:
        # Show options
        selected = show_concept_menu(rec.options)
        start_challenge(selected)
```

**Recommendation Priority:**
1. **Break needed?** - Session too long or frustration high
2. **Frustration recovery** - Offer flow-trigger concept
3. **Spaced repetition** - Concept due for review
4. **Project goal** - Next prerequisite for learner's goal
5. **Weakness drilling** - Resurface struggled concept
6. **Exploration** - Something new and fun

##### `get_unlockable_concepts(all_concepts: dict[str, Concept]) -> list[str]`

Get concepts that can be unlocked based on current mastery.

```python
concepts = load_all_concepts()
unlockable = engine.get_unlockable_concepts(concepts)
# Returns concepts where all prerequisites are mastered
```

##### `is_in_flow_state() -> bool`

Detect if learner is in flow state.

```python
if engine.is_in_flow_state():
    # Auto-advance to next challenge
    rec = engine.recommend_next()
    assert rec.auto_advance == True
```

##### `save(path: Path) -> None`

Save profile to JSON file.

```python
engine.save(Path("profiles/wings.json"))
```

##### `load(path: Path) -> AdaptiveEngine` (classmethod)

Load profile from JSON file.

```python
engine = AdaptiveEngine.load(Path("profiles/wings.json"))
```

**Complete Example:**
```python
from lmsp.adaptive import AdaptiveEngine, LearnerProfile
from lmsp.input.emotional import EmotionalDimension
from pathlib import Path

# Create or load profile
profile_path = Path("profiles/wings.json")
if profile_path.exists():
    engine = AdaptiveEngine.load(profile_path)
else:
    profile = LearnerProfile("wings")
    engine = AdaptiveEngine(profile)

# Main learning loop
while learning:
    # Get recommendation
    rec = engine.recommend_next()

    if rec.action == "break":
        print(f"Suggestion: {rec.reason}")
        if input("Take a break? (y/n) ") == "y":
            break
        continue

    # Select concept
    if rec.auto_advance:
        concept = rec.concept
    else:
        concept = show_menu(rec.options)

    # Run challenge
    result = run_challenge(concept)

    # Record attempt
    engine.observe_attempt(
        concept=concept,
        success=result.passed,
        time_seconds=result.duration,
        hints_used=result.hints
    )

    # Collect emotional feedback
    emotion = collect_emotion("How was that?")
    engine.observe_emotion(
        dimension=emotion.dimension,
        value=emotion.value,
        context=concept
    )

    # Save progress
    engine.save(profile_path)
```

---

## Player-Zero Integration API

Module: `lmsp.multiplayer.player_zero`

### Classes

#### `Player` (Protocol)

Base player interface.

```python
from typing import Protocol

class Player(Protocol):
    name: str
    player_id: str

    async def get_action(self, game_state: GameState) -> Action:
        """Get next action from player."""
        ...

    async def observe(self, event: GameEvent) -> None:
        """Observe an event in the game."""
        ...
```

---

#### `HumanPlayer`

Human player with controller/keyboard input.

**Constructor:**
```python
HumanPlayer(
    name: str,
    input_device: str = "keyboard"  # "keyboard" | "gamepad" | "touch"
)
```

**Methods:**

##### `async get_action(game_state: GameState) -> Action`

Wait for human input action.

```python
player = HumanPlayer(name="Wings", input_device="gamepad")

action = await player.get_action(game_state)
# Returns when player makes a move (keystroke, button press, etc.)
```

##### `async observe(event: GameEvent) -> None`

Show event to human player.

```python
await player.observe(GameEvent(
    type="suggestion",
    player_id="claude",
    content="Don't forget the colon!"
))
```

---

#### `ClaudePlayer`

AI player powered by Claude.

**Constructor:**
```python
ClaudePlayer(
    name: str,
    style: str = "encouraging",      # Teaching style
    skill_level: float = 0.5,        # 0.0 = beginner, 1.0 = expert
    personality: str | None = None   # Custom personality prompt
)
```

**Parameters:**
- `style`: "encouraging", "challenging", "analytical", "playful"
- `skill_level`: How skilled the AI should play (for balancing)
- `personality`: Custom system prompt for unique behavior

**Methods:**

##### `async get_action(game_state: GameState) -> Action`

Get AI's next action.

```python
claude = ClaudePlayer(name="Lief", style="encouraging", skill_level=0.7)

action = await claude.get_action(game_state)
# AI analyzes state and decides next move
```

##### `async observe(event: GameEvent) -> None`

AI observes game events (for awareness).

```python
await claude.observe(GameEvent(
    type="keystroke",
    player_id="wings",
    content="d"
))
# AI sees "Wings is typing 'def'..."
```

##### `set_goal(goal: str) -> None`

Set AI's goal/persona.

```python
claude.set_goal("Teach list comprehensions gently")
claude.set_goal("Find bugs in player's solution")
claude.set_goal("Complete challenge as fast as possible")
```

---

#### `CoopSession`

Cooperative multiplayer session.

**Constructor:**
```python
CoopSession(
    players: list[Player],
    challenge: str | None = None
)
```

**Methods:**

##### `set_challenge(challenge_id: str) -> None`

Set the challenge to work on together.

```python
session = CoopSession(players=[human, claude])
session.set_challenge("container_add_exists")
```

##### `async start() -> SessionResult`

Start cooperative session.

```python
result = await session.start()

# result contains:
#   - Final solution
#   - Who contributed what
#   - Time to completion
#   - Interaction transcript
```

##### `async broadcast(event: GameEvent) -> None`

Broadcast event to all players.

```python
await session.broadcast(GameEvent(
    type="test_result",
    player_id="wings",
    content={"passed": 3, "total": 5}
))
```

**Complete Example:**
```python
from lmsp.multiplayer.player_zero import HumanPlayer, ClaudePlayer, CoopSession

# Create players
wings = HumanPlayer(name="Wings", input_device="gamepad")
lief = ClaudePlayer(name="Lief", style="encouraging", skill_level=0.7)

# Start COOP session
session = CoopSession(players=[wings, lief])
session.set_challenge("container_add_exists")

result = await session.start()

print(f"Challenge completed in {result.time_seconds}s")
print(f"Wings contributed: {result.contributions['Wings']} lines")
print(f"Lief contributed: {result.contributions['Lief']} lines")
```

---

## TAS (Tool-Assisted Learning) API

Module: `lmsp.introspection.tas`

### Classes

#### `RecordedEvent`

Single recorded event.

**Dataclass:**
```python
@dataclass
class RecordedEvent:
    timestamp: float          # Time since recording start
    event: GameEvent          # The event that occurred
    game_state: GameState     # Full game state at this moment
```

---

#### `Recording`

Complete recording of a session.

**Dataclass:**
```python
@dataclass
class Recording:
    events: list[RecordedEvent]         # All recorded events
    checkpoints: dict[str, int]         # name -> event index
    duration: float                     # Total recording time
    metadata: dict[str, Any]            # Custom metadata
```

---

#### `Recorder`

Records game sessions for replay and analysis.

**Constructor:**
```python
Recorder()
```

**Methods:**

##### `start() -> None`

Start recording.

```python
recorder = Recorder()
recorder.start()
```

##### `record(event: GameEvent) -> None`

Record an event.

```python
recorder.record(GameEvent(
    type="keystroke",
    player_id="wings",
    content="d"
))
```

##### `checkpoint(name: str) -> None`

Save a named checkpoint.

```python
# Save state before attempting tricky part
recorder.checkpoint("before_loop")

# ... try loop logic ...

# Can rewind to this point later
```

##### `stop() -> Recording`

Stop recording and return the recording.

```python
recording = recorder.stop()

# Save to disk
with open("session.json", "w") as f:
    json.dump(recording.to_dict(), f)
```

##### `export(path: Path, format: str = "json") -> None`

Export recording to file.

```python
recorder.export(Path("recordings/session1.json"))
```

**Complete Example:**
```python
from lmsp.introspection.tas import Recorder

recorder = Recorder()
recorder.start()

# Play the game
while playing:
    event = get_game_event()
    recorder.record(event)

    # Save checkpoints at key moments
    if event.type == "test_pass":
        recorder.checkpoint(f"test_{event.test_number}_passed")

# Stop and save
recording = recorder.stop()
recorder.export(Path("my_session.json"))
```

---

#### `Replayer`

Replays recordings for analysis.

**Constructor:**
```python
Replayer(recording: Recording)
```

**Methods:**

##### `async replay(speed: float = 1.0) -> None`

Replay recording at specified speed.

```python
# Load recording
recording = Recording.load(Path("session.json"))

# Replay at 2x speed
replayer = Replayer(recording)
await replayer.replay(speed=2.0)
```

##### `async step() -> RecordedEvent`

Step forward one event.

```python
replayer = Replayer(recording)

while replayer.has_next():
    event = await replayer.step()
    display_event(event)
    await wait_for_input()  # Manual stepping
```

##### `async rewind(steps: int = 1) -> None`

Step backward in the recording.

```python
# Undo last 5 actions
await replayer.rewind(steps=5)
```

##### `restore_checkpoint(name: str) -> GameState`

Jump to a named checkpoint.

```python
state = replayer.restore_checkpoint("before_loop")
# Returns to that exact game state
```

##### `get_state() -> GameState`

Get current game state during replay.

```python
state = replayer.get_state()
print(f"Current code:\n{state.code}")
```

---

#### `Checkpoint`

State checkpoint system.

**Static Methods:**

##### `create(name: str, state: GameState) -> Checkpoint`

Create a checkpoint.

```python
checkpoint = Checkpoint.create("golden_solution", game_state)
```

##### `restore(checkpoint: Checkpoint) -> GameState`

Restore a checkpoint.

```python
state = Checkpoint.restore(checkpoint)
```

##### `diff(a: Checkpoint, b: Checkpoint) -> CheckpointDiff`

Compare two checkpoints.

```python
diff = Checkpoint.diff(before, after)

print("Code changes:")
print(diff.code_diff)

print("Events between:")
for event in diff.events:
    print(event)
```

**Complete Example:**
```python
from lmsp.introspection.tas import Recorder, Replayer, Checkpoint

# Record a session
recorder = Recorder()
recorder.start()

# ... play game ...
recorder.checkpoint("before_bug")
# ... introduce bug ...
recorder.checkpoint("after_bug")

recording = recorder.stop()

# Analyze what went wrong
replayer = Replayer(recording)
before = replayer.restore_checkpoint("before_bug")
after = replayer.restore_checkpoint("after_bug")

diff = Checkpoint.diff(before, after)
print("What changed:")
print(diff.code_diff)
```

---

## Introspection API

Module: `lmsp.introspection`

### Classes

#### `Screenshot`

Captures screen with full context metadata.

**Methods:**

##### `capture(game_state: GameState) -> ScreenshotBundle`

Capture screenshot with wireframe.

```python
from lmsp.introspection.screenshot import Screenshot

screenshot = Screenshot()
bundle = screenshot.capture(game_state)

# bundle contains:
#   - image: PIL Image
#   - wireframe: Full context metadata
#   - timestamp: When captured
```

##### `save(bundle: ScreenshotBundle, path: Path) -> None`

Save screenshot and metadata.

```python
screenshot.save(bundle, Path("screenshots/bug_found.png"))
# Also saves: screenshots/bug_found.json (metadata)
```

---

#### `Wireframe`

Complete context for a game state.

**Dataclass:**
```python
@dataclass
class Wireframe:
    # Code state
    code: str                           # Current code
    ast: ast.AST                        # Parsed AST
    cursor_position: tuple[int, int]    # (line, col)

    # Game state
    current_challenge: str              # Challenge ID
    tests_passing: int                  # Tests passed
    tests_total: int                    # Total tests

    # Player state
    player_id: str
    mastery_levels: dict[str, int]
    current_emotion: EmotionalRecord | None

    # Session state
    session_duration: float             # Seconds in session
    challenges_completed: int

    # Multiplayer state
    other_players: list[dict]           # Other players' summaries
```

---

#### `VideoRecorder`

Strategic video recording.

**Methods:**

##### `async record(duration: float, fps: int = 10) -> list[Image]`

Record video frames.

```python
from lmsp.introspection.video import VideoRecorder

recorder = VideoRecorder()
frames = await recorder.record(duration=30.0, fps=10)
# Records 300 frames (30s * 10fps)
```

---

#### `MosaicGenerator`

Generate frame mosaics for Claude vision API.

**Methods:**

##### `generate(frames: list[Image], grid: tuple[int, int] = (4, 4)) -> Image`

Compose frames into mosaic grid.

```python
from lmsp.introspection.mosaic import MosaicGenerator

generator = MosaicGenerator()

# Record 30 seconds
frames = await video_recorder.record(30.0, fps=10)

# Generate 4x4 mosaic (16 evenly-spaced frames)
mosaic = generator.generate(frames, grid=(4, 4))
mosaic.save("session_mosaic.png")
```

##### `generate_with_metadata(frames: list[Image], wireframes: list[Wireframe], grid: tuple[int, int]) -> tuple[Image, dict]`

Generate mosaic with associated metadata.

```python
mosaic, metadata = generator.generate_with_metadata(
    frames=frames,
    wireframes=wireframes,
    grid=(4, 4)
)

# Mosaic image + JSON metadata for each frame
```

**Complete Example:**
```python
from lmsp.introspection import Screenshot, VideoRecorder, MosaicGenerator

# Capture instant screenshot
screenshot = Screenshot()
bundle = screenshot.capture(game_state)
screenshot.save(bundle, Path("debug/current_state.png"))

# Record strategic video
video = VideoRecorder()
frames = await video.record(duration=60.0, fps=5)

# Generate mosaic for Claude analysis
mosaic_gen = MosaicGenerator()
mosaic = mosaic_gen.generate(frames, grid=(6, 5))  # 30 frames
mosaic.save("debug/session_overview.png")
```

---

## Utility Functions

### `load_concept(path: Path) -> Concept`

Load a concept from TOML file.

```python
from lmsp.python.concepts import load_concept

concept = load_concept(Path("concepts/level_2/lists.toml"))
print(concept.name)  # "Lists"
```

### `load_challenge(path: Path) -> Challenge`

Load a challenge from TOML file.

```python
from lmsp.python.challenges import load_challenge

challenge = load_challenge(Path("challenges/container_basics/add_exists.toml"))
print(challenge.name)  # "Container: Add & Exists"
```

### `validate_solution(code: str, tests: list[TestCase]) -> ValidationResult`

Validate a solution against test cases.

```python
from lmsp.python.validator import validate_solution

result = validate_solution(
    code=player_code,
    tests=challenge.tests
)

print(f"Passed: {result.passed}/{result.total}")
for i, test in enumerate(result.test_results):
    if not test.passed:
        print(f"Test {i}: Expected {test.expected}, got {test.actual}")
```

---

## Type Definitions

### `GameState`

```python
@dataclass
class GameState:
    code: str                           # Current code
    cursor: tuple[int, int]             # Cursor position
    challenge: str                      # Current challenge ID
    tests_passing: int
    tests_total: int
    player: Player
    session_duration: float
    challenges_completed: int
    other_players: list[Player]
```

### `GameEvent`

```python
@dataclass
class GameEvent:
    type: str                           # Event type
    player_id: str                      # Who triggered it
    content: Any                        # Event-specific data
    timestamp: float                    # When it occurred
```

**Event Types:**
- `"keystroke"` - Single character typed
- `"cursor_move"` - Cursor position changed
- `"test_result"` - Tests run, results available
- `"completion"` - Challenge completed
- `"emotion"` - Emotional feedback recorded
- `"suggestion"` - AI player makes suggestion
- `"thought"` - AI player shares thinking

---

## Error Handling

All APIs use standard Python exceptions:

```python
from lmsp.exceptions import (
    ConceptNotFoundError,
    ChallengeNotFoundError,
    ValidationError,
    SaveLoadError
)

try:
    concept = load_concept(path)
except ConceptNotFoundError:
    print(f"Concept not found: {path}")

try:
    result = validate_solution(code, tests)
except ValidationError as e:
    print(f"Validation failed: {e}")
```

---

## Performance Considerations

### Emotional State Recording

```python
# Good: Record after key events
state.record(dimension, value, context=concept)

# Bad: Record too frequently
for frame in range(1000):
    state.record(...)  # Will slow down game loop
```

### TAS Recording

```python
# Good: Record high-level events
recorder.record(GameEvent(type="line_complete", content=code))

# Bad: Record every keystroke in large sessions
for char in text:
    recorder.record(GameEvent(type="char", content=char))
# This creates huge recordings
```

### Profile Saving

```python
# Good: Save periodically
if challenge_count % 5 == 0:
    engine.save(profile_path)

# Bad: Save after every action
engine.observe_attempt(...)
engine.save(profile_path)  # Too frequent
```

---

## Async/Await Patterns

Many APIs are async for responsiveness:

```python
import asyncio

async def learning_session():
    # Concurrent emotional prompt and game update
    emotion_task = asyncio.create_task(collect_emotion())
    game_task = asyncio.create_task(update_game())

    emotion, game_state = await asyncio.gather(emotion_task, game_task)

# Run session
asyncio.run(learning_session())
```

---

## Integration Example: Full Learning Loop

```python
import asyncio
from pathlib import Path
from lmsp.adaptive import AdaptiveEngine, LearnerProfile
from lmsp.input.emotional import EmotionalPrompt, EmotionalState
from lmsp.python.concepts import load_all_concepts
from lmsp.python.challenges import load_challenge
from lmsp.python.validator import validate_solution
from lmsp.multiplayer.player_zero import HumanPlayer, ClaudePlayer, CoopSession

async def main():
    # Load or create profile
    profile_path = Path("profiles/wings.json")
    if profile_path.exists():
        engine = AdaptiveEngine.load(profile_path)
    else:
        profile = LearnerProfile("wings")
        engine = AdaptiveEngine(profile)

    # Create emotional tracker
    emotion_state = EmotionalState()

    # Load all concepts
    concepts = load_all_concepts(Path("concepts/"))

    # Main loop
    while True:
        # Get recommendation
        rec = engine.recommend_next()

        if rec.action == "break":
            print(f"\n{rec.reason}")
            if input("Take a break? (y/n): ") == "y":
                break
            continue

        # Select concept
        if rec.auto_advance:
            concept_id = rec.concept
            print(f"\nFlow detected! Auto-advancing to: {concepts[concept_id].name}")
        else:
            print(f"\n{rec.reason}")
            print("Options:")
            for i, opt in enumerate(rec.options, 1):
                print(f"  {i}. {concepts[opt].name}")
            choice = int(input("Choose: ")) - 1
            concept_id = rec.options[choice]

        # Load challenge
        concept = concepts[concept_id]
        challenge = load_challenge(Path(f"challenges/{concept.challenges.starter}.toml"))

        # Choose mode
        mode = input("Mode: (1) Solo, (2) COOP with AI: ")

        if mode == "2":
            # Multiplayer
            human = HumanPlayer(name="Wings", input_device="gamepad")
            ai = ClaudePlayer(name="Lief", style="encouraging", skill_level=0.7)
            session = CoopSession(players=[human, ai])
            session.set_challenge(challenge.id)
            result = await session.start()

            engine.observe_attempt(
                concept=concept_id,
                success=result.success,
                time_seconds=result.duration,
                hints_used=0
            )
        else:
            # Solo
            print(f"\n{challenge.name}")
            print(challenge.description.detailed)
            print(f"\nStarting code:\n{challenge.skeleton.code}")

            # Player writes code
            code = await get_player_code()

            # Validate
            result = validate_solution(code, challenge.tests)
            print(f"\nTests: {result.passed}/{result.total}")

            # Record attempt
            engine.observe_attempt(
                concept=concept_id,
                success=(result.passed == result.total),
                time_seconds=result.duration,
                hints_used=0
            )

        # Collect emotional feedback
        prompt = EmotionalPrompt(
            question="How was that challenge?",
            right_trigger="Satisfying",
            left_trigger="Frustrating"
        )
        emotion = await collect_emotion_input(prompt)
        engine.observe_emotion(emotion.dimension, emotion.value, concept_id)
        emotion_state.record(emotion.dimension, emotion.value, concept_id)

        # Save progress
        engine.save(profile_path)

        # Check flow state
        if emotion_state.is_in_flow():
            print("\n🔥 Flow state detected! Keeping momentum...")

        # Check break needed
        if emotion_state.needs_break():
            print("\n💤 High frustration detected. Consider taking a break.")

if __name__ == "__main__":
    asyncio.run(main())
```

---

*Complete API coverage enables full integration and extensibility.*
