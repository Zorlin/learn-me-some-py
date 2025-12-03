# Stream-JSON Protocol - Multi-Agent Awareness in LMSP

**The 18-line magic that makes multiplayer AI collaboration work.**

---

## Table of Contents

1. [The Core Innovation](#the-core-innovation)
2. [The 18-Line Magic](#the-18-line-magic)
3. [Event Types](#event-types)
4. [Protocol Specification](#protocol-specification)
5. [Palace Pattern Adaptation](#palace-pattern-adaptation)
6. [Multi-Agent Awareness System](#multi-agent-awareness-system)
7. [JSON Event Format](#json-event-format)
8. [Implementation Guide](#implementation-guide)

---

## The Core Innovation

**The Problem:**
How do multiple AI players (Claude instances) stay aware of each other's actions in real-time without complex networking protocols, message queues, or coordination servers?

**The Solution:**
Stream-JSON via stdin/stdout. Each player process receives a stream of JSON events on stdin representing what other players are doing. Simple, fast, and requires no external infrastructure.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      STREAM-JSON ARCHITECTURE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                         ┌─────────────────┐                                 │
│                         │  Session        │                                 │
│                         │  Manager        │                                 │
│                         │                 │                                 │
│                         │  Event Bus      │                                 │
│                         └────────┬────────┘                                 │
│                                  │                                          │
│            ┌─────────────────────┼─────────────────────┐                    │
│            │                     │                     │                    │
│     ┌──────▼──────┐      ┌──────▼──────┐      ┌──────▼──────┐             │
│     │  Player 1   │      │  Player 2   │      │  Player N   │             │
│     │  Process    │      │  Process    │      │  Process    │             │
│     │             │      │             │      │             │             │
│     │  stdin ◄────┼──────┼─ Events ────┼──────┼─ Events    │             │
│     │  stdout ────┼──────┼──────────►  │      │            │             │
│     └─────────────┘      └─────────────┘      └────────────┘             │
│                                                                              │
│  Each player:                                                                │
│    - Reads JSON events from stdin (what others are doing)                  │
│    - Writes JSON events to stdout (what I am doing)                        │
│    - Session manager broadcasts stdout from one to stdin of others         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Why this works:**
- **Simple** - Standard stdin/stdout, no special protocols
- **Fast** - Direct process pipes, minimal latency
- **Portable** - Works anywhere processes can spawn
- **Observable** - Easy to log, debug, replay
- **Composable** - Can wrap/transform event streams easily

---

## The 18-Line Magic

This function is at the heart of all multiplayer sessions. It's adapted from Palace's multi-agent orchestration system:

```python
def _forward_to_other_agents(self, source_player_id, event_json, players, done_players):
    """
    Forward event to other players' stdin for shared awareness.

    The magic: When one player emits an event (cursor move, keystroke, thought),
    we write that JSON to every OTHER player's stdin so they know what happened.

    This creates real-time multi-agent awareness with zero networking complexity.
    """
    for player_id, player_info in players.items():
        # Don't echo back to sender
        if player_id == source_player_id:
            continue

        # Skip players who have finished/disconnected
        if player_id in done_players:
            continue

        # Write event JSON to this player's stdin
        try:
            player_info["process"].stdin.write(event_json + "\n")
            player_info["process"].stdin.flush()
        except BrokenPipeError:
            # Player process died - mark as done
            done_players.add(player_id)
        except Exception as e:
            # Log but don't crash
            logging.warning(f"Failed to forward to {player_id}: {e}")
```

### Why this is elegant

1. **One write, N reads** - Broadcast pattern with no message broker
2. **Fail-safe** - Broken pipes are caught, don't crash session
3. **Immediate** - Events arrive as fast as pipe write
4. **Order-preserving** - Events arrive in the order they're sent
5. **Backpressure-aware** - If a player can't keep up, pipe blocks naturally

### Palace Origins

This pattern comes from Palace's `pal swarm` command, which orchestrates multiple Claude instances working together on different tasks. Palace proved that:
- Claude can parse JSON events from stdin
- Claude can emit structured JSON to stdout
- Multiple Claudes can collaborate via this simple protocol

LMSP adapts this for learning games.

---

## Event Types

All events follow a consistent structure with a `type` field:

```python
class EventType(Enum):
    """All possible event types in stream-JSON protocol."""

    # Movement/Input Events
    CURSOR_MOVE = "cursor_move"
    KEYSTROKE = "keystroke"
    SELECTION = "selection"

    # Code Events
    CODE_UPDATE = "code_update"
    RUN_TESTS = "run_tests"
    TEST_RESULT = "test_result"

    # Cognitive Events
    THOUGHT = "thought"
    SUGGESTION = "suggestion"
    QUESTION = "question"
    ANSWER = "answer"

    # Emotional Events
    EMOTION = "emotion"
    FRUSTRATION = "frustration"
    ENJOYMENT = "enjoyment"

    # Session Control Events
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    TURN_START = "turn_start"
    TURN_END = "turn_end"
    PAUSE = "pause"
    RESUME = "resume"

    # Completion Events
    CHALLENGE_COMPLETE = "challenge_complete"
    PLAYER_COMPLETE = "player_complete"
    ALL_COMPLETE = "all_complete"

    # Meta Events
    CHECKPOINT = "checkpoint"
    REWIND = "rewind"
    STATE_SYNC = "state_sync"
```

### Event Categories

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          EVENT CATEGORIES                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  INPUT EVENTS (high frequency)                                              │
│    - cursor_move: Player moved cursor                                       │
│    - keystroke: Player typed character                                      │
│    - selection: Player selected text                                        │
│                                                                              │
│  CODE EVENTS (medium frequency)                                             │
│    - code_update: Code changed (debounced)                                  │
│    - run_tests: Player triggered test run                                   │
│    - test_result: Test results available                                    │
│                                                                              │
│  COGNITIVE EVENTS (low frequency, high value)                               │
│    - thought: Player's internal reasoning                                   │
│    - suggestion: Player suggests to others                                  │
│    - question: Player asks question                                         │
│    - answer: Response to question                                           │
│                                                                              │
│  EMOTIONAL EVENTS (triggered by prompts)                                    │
│    - emotion: Generic emotional state                                       │
│    - frustration: Player frustrated                                         │
│    - enjoyment: Player enjoying                                             │
│                                                                              │
│  CONTROL EVENTS (session lifecycle)                                         │
│    - session_start/end: Session boundaries                                  │
│    - turn_start/end: Turn-based control                                     │
│    - pause/resume: Playback control                                         │
│                                                                              │
│  COMPLETION EVENTS (achievements)                                           │
│    - challenge_complete: Tests passed                                       │
│    - player_complete: Player finished                                       │
│    - all_complete: Session done                                             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Protocol Specification

### Base Event Structure

All events must include:

```json
{
  "type": "event_type",
  "player": "player_name",
  "timestamp": 1699564832.123,
  "session_id": "uuid-string"
}
```

### Event-Specific Fields

Each event type adds its own fields:

#### cursor_move
```json
{
  "type": "cursor_move",
  "player": "Wings",
  "timestamp": 1699564832.123,
  "session_id": "abc-123",
  "line": 5,
  "col": 12,
  "file": "solution.py"
}
```

#### keystroke
```json
{
  "type": "keystroke",
  "player": "Lief",
  "timestamp": 1699564832.456,
  "session_id": "abc-123",
  "char": "d",
  "modifiers": ["shift"],
  "line": 5,
  "col": 12
}
```

#### code_update
```json
{
  "type": "code_update",
  "player": "Wings",
  "timestamp": 1699564832.789,
  "session_id": "abc-123",
  "code": "def solution(queries):\n    container = []\n",
  "cursor": [2, 19],
  "diff": {
    "added": [[2, "    container = []"]],
    "removed": []
  }
}
```

#### thought
```json
{
  "type": "thought",
  "player": "Lief",
  "timestamp": 1699564833.001,
  "session_id": "abc-123",
  "content": "I need to initialize a list to store values",
  "context": "defining_container",
  "visibility": "all"
}
```

#### suggestion
```json
{
  "type": "suggestion",
  "player": "Lief",
  "timestamp": 1699564833.234,
  "session_id": "abc-123",
  "content": "Don't forget the colon after the for loop!",
  "target_player": "Wings",
  "urgency": "medium"
}
```

#### test_result
```json
{
  "type": "test_result",
  "player": "Wings",
  "timestamp": 1699564835.567,
  "session_id": "abc-123",
  "passed": 3,
  "total": 5,
  "details": [
    {"name": "test_add", "passed": true, "time": 0.001},
    {"name": "test_exists", "passed": true, "time": 0.001},
    {"name": "test_remove", "passed": false, "error": "KeyError: 'value'"}
  ],
  "execution_time_ms": 12
}
```

#### emotion
```json
{
  "type": "emotion",
  "player": "Wings",
  "timestamp": 1699564836.890,
  "session_id": "abc-123",
  "dimension": "enjoyment",
  "value": 0.8,
  "context": "test_passing",
  "raw_input": {
    "rt": 0.8,
    "lt": 0.1
  }
}
```

#### player_complete
```json
{
  "type": "player_complete",
  "player": "Lief",
  "timestamp": 1699564840.123,
  "session_id": "abc-123",
  "completion_time": 145.5,
  "tests_passed": 5,
  "tests_total": 5,
  "hints_used": 0,
  "final_code": "def solution(queries): ..."
}
```

### Protocol Rules

1. **Line-delimited JSON** - Each event is a single line
2. **UTF-8 encoding** - All strings are UTF-8
3. **Monotonic timestamps** - Must be strictly increasing
4. **Required fields** - type, player, timestamp, session_id
5. **Forward compatibility** - Ignore unknown fields
6. **No nested sessions** - session_id is flat, no hierarchy

---

## Palace Pattern Adaptation

LMSP's stream-JSON protocol is adapted from Palace's swarm orchestration. Here's how:

### Palace Original (pal swarm)

Palace uses stream-JSON to coordinate multiple Claude instances working on different files:

```python
# Palace swarm: Multiple agents, different tasks
agents = [
    {"name": "docs", "task": "Update README.md"},
    {"name": "tests", "task": "Write tests for feature X"},
    {"name": "impl", "task": "Implement feature X"}
]

# Each agent writes events:
{"type": "file_edit", "agent": "docs", "file": "README.md", "status": "in_progress"}
{"type": "thought", "agent": "impl", "content": "Need to import typing module"}
{"type": "completion", "agent": "tests", "files": ["test_feature_x.py"]}

# Session manager broadcasts to others
# Agent "docs" sees that "impl" is working on feature X
# Agent "impl" sees that "tests" finished test file
# Coordination happens naturally through shared awareness
```

### LMSP Adaptation (Multiplayer)

LMSP uses the same pattern but for collaborative learning:

```python
# LMSP: Multiple players, same challenge
players = [
    {"name": "Wings", "type": "human", "device": "gamepad"},
    {"name": "Lief", "type": "claude", "style": "encouraging"}
]

# Players write events:
{"type": "keystroke", "player": "Wings", "char": "d"}
{"type": "thought", "player": "Lief", "content": "They're defining a function!"}
{"type": "suggestion", "player": "Lief", "content": "Don't forget the colon"}

# Session manager broadcasts cursor positions, thoughts, emotions
# Human player sees AI's thought process
# AI sees human's emotional state (via trigger input)
# Learning happens through observation and collaboration
```

### Key Differences

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PALACE vs LMSP COMPARISON                                 │
├─────────────────────┬───────────────────────────────────────────────────────┤
│ Aspect              │ Palace Swarm          │ LMSP Multiplayer             │
├─────────────────────┼───────────────────────┼──────────────────────────────┤
│ Players             │ AI agents only        │ Human + AI mix               │
│ Tasks               │ Different per agent   │ Same challenge for all       │
│ Coordination        │ Divide and conquer    │ Collaborate or compete       │
│ Events              │ File edits, builds    │ Keystrokes, emotions         │
│ Success metric      │ All tasks done        │ Tests pass, learning happens │
│ Awareness           │ Who's doing what      │ Who's struggling/enjoying    │
└─────────────────────┴───────────────────────┴──────────────────────────────┘
```

### Shared Primitives

Both Palace and LMSP use:
- `_forward_to_other_agents()` - Broadcast function
- Line-delimited JSON - Protocol format
- stdin/stdout pipes - Transport mechanism
- Process isolation - Security boundary
- Event-driven architecture - Coordination model

---

## Multi-Agent Awareness System

The stream-JSON protocol enables a sophisticated awareness system:

### Awareness Layers

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      MULTI-AGENT AWARENESS LAYERS                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Layer 1: PRESENCE                                                           │
│    └─ Who is in the session?                                                │
│    └─ Are they active or idle?                                              │
│    └─ Human or AI?                                                          │
│                                                                              │
│  Layer 2: ACTIVITY                                                           │
│    └─ What are they doing right now?                                        │
│    └─ Where is their cursor?                                                │
│    └─ What did they just type?                                              │
│                                                                              │
│  Layer 3: PROGRESS                                                           │
│    └─ How far have they gotten?                                             │
│    └─ How many tests passing?                                               │
│    └─ Are they ahead or behind?                                             │
│                                                                              │
│  Layer 4: COGNITION                                                          │
│    └─ What are they thinking?                                               │
│    └─ What's their strategy?                                                │
│    └─ Are they stuck?                                                       │
│                                                                              │
│  Layer 5: EMOTION                                                            │
│    └─ How are they feeling?                                                 │
│    └─ Frustrated or enjoying?                                               │
│    └─ In flow or struggling?                                                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Awareness State Machine

```python
class AwarenessTracker:
    """Track what each player knows about others."""

    def __init__(self, players: list[Player]):
        self.players = players

        # Per-player awareness state
        self.awareness: dict[str, dict[str, PlayerAwareness]] = {}

        for player in players:
            self.awareness[player.name] = {}
            for other in players:
                if other.name != player.name:
                    self.awareness[player.name][other.name] = PlayerAwareness(
                        presence=PresenceState.UNKNOWN,
                        last_seen=0,
                        last_activity=None,
                        progress=None,
                        emotion=None,
                        thoughts=[]
                    )

    def process_event(self, event: GameEvent):
        """Update awareness state based on event."""
        source = event.player

        # Update what everyone knows about source
        for observer in self.players:
            if observer.name == source:
                continue

            awareness = self.awareness[observer.name][source]

            # Update last_seen
            awareness.last_seen = event.timestamp

            # Update presence
            awareness.presence = PresenceState.ACTIVE

            # Update based on event type
            if event.type in ["cursor_move", "keystroke"]:
                awareness.last_activity = event.type
                awareness.activity_time = event.timestamp

            elif event.type == "thought":
                awareness.thoughts.append(event.content)
                # Keep only recent thoughts
                awareness.thoughts = awareness.thoughts[-5:]

            elif event.type == "emotion":
                awareness.emotion = EmotionalState(
                    dimension=event.dimension,
                    value=event.value,
                    timestamp=event.timestamp
                )

            elif event.type == "test_result":
                awareness.progress = ProgressState(
                    tests_passed=event.passed,
                    tests_total=event.total,
                    timestamp=event.timestamp
                )

    def get_awareness(self, observer: str, subject: str) -> PlayerAwareness:
        """Get what observer knows about subject."""
        return self.awareness[observer][subject]

    def summarize_for_player(self, player: str) -> str:
        """Generate human-readable summary of what player knows."""
        summary = []

        for other_name, awareness in self.awareness[player].items():
            summary.append(f"\n{other_name}:")

            # Presence
            if awareness.presence == PresenceState.ACTIVE:
                summary.append("  - Active")
            elif awareness.presence == PresenceState.IDLE:
                summary.append("  - Idle")

            # Activity
            if awareness.last_activity:
                elapsed = time.time() - awareness.activity_time
                summary.append(f"  - Last activity: {awareness.last_activity} ({elapsed:.0f}s ago)")

            # Progress
            if awareness.progress:
                summary.append(
                    f"  - Progress: {awareness.progress.tests_passed}/"
                    f"{awareness.progress.tests_total} tests"
                )

            # Emotion
            if awareness.emotion:
                summary.append(
                    f"  - Feeling: {awareness.emotion.dimension.value} "
                    f"({awareness.emotion.value:.1f})"
                )

            # Recent thoughts
            if awareness.thoughts:
                summary.append("  - Recent thoughts:")
                for thought in awareness.thoughts[-3:]:
                    summary.append(f"    - \"{thought}\"")

        return "\n".join(summary)
```

### Claude Integration

When a Claude player receives events, it can use them in prompts:

```python
class ClaudePlayer:
    """AI player that uses stream-JSON for awareness."""

    async def process_stdin_event(self, event_json: str):
        """Process incoming event from stdin."""
        event = json.loads(event_json)

        # Update internal awareness model
        self.awareness_tracker.process_event(event)

        # React to specific events
        if event["type"] == "emotion" and event["dimension"] == "frustration":
            if event["value"] > 0.7:
                # Other player is frustrated - offer help
                await self.send_suggestion(
                    f"I notice you might be stuck. Want a hint?"
                )

        elif event["type"] == "test_result":
            if event["passed"] > event["total"] // 2:
                # They're making progress!
                await self.send_thought(
                    f"{event['player']} is doing well - {event['passed']}/{event['total']} tests passing!"
                )

        elif event["type"] == "keystroke":
            # Track what they're typing
            self.track_typing_pattern(event)

    async def generate_next_action(self) -> GameEvent:
        """Generate next action using awareness."""
        # Build context from awareness
        context = self.build_awareness_context()

        # Query Claude with context
        response = await self.claude_query(
            prompt=f"""
You are playing a coding challenge cooperatively.

Current situation:
{context}

What should you do next? Reply with:
1. Code to write (if it's your turn)
2. Suggestion to make (if you have advice)
3. Question to ask (if you're confused)

Use JSON format.
            """,
            thinking=True
        )

        return self.parse_response_to_event(response)

    def build_awareness_context(self) -> str:
        """Build context string from awareness state."""
        context_parts = []

        # Who's in the session
        context_parts.append("Players:")
        for player in self.session.players:
            if player.name == self.name:
                context_parts.append(f"  - {player.name} (you)")
            else:
                awareness = self.awareness_tracker.get_awareness(self.name, player.name)
                context_parts.append(f"  - {player.name}")
                context_parts.append(f"    Progress: {awareness.progress}")
                context_parts.append(f"    Emotion: {awareness.emotion}")

        # Current code state
        context_parts.append(f"\nCurrent code:\n{self.session.current_code}")

        # Test status
        context_parts.append(f"\nTests: {self.session.tests_passed}/{self.session.tests_total}")

        return "\n".join(context_parts)
```

---

## JSON Event Format

### Event Schema Definition

```python
from typing import Literal, TypedDict, Union
from enum import Enum

class BaseEvent(TypedDict):
    """Base event structure."""
    type: str
    player: str
    timestamp: float
    session_id: str

class CursorMoveEvent(BaseEvent):
    """Cursor movement event."""
    type: Literal["cursor_move"]
    line: int
    col: int
    file: str | None

class KeystrokeEvent(BaseEvent):
    """Keystroke event."""
    type: Literal["keystroke"]
    char: str
    modifiers: list[str]  # ["shift", "ctrl", "alt"]
    line: int
    col: int

class CodeUpdateEvent(BaseEvent):
    """Code change event."""
    type: Literal["code_update"]
    code: str
    cursor: tuple[int, int]
    diff: dict[str, list]

class ThoughtEvent(BaseEvent):
    """Cognitive event - player's thought."""
    type: Literal["thought"]
    content: str
    context: str | None
    visibility: Literal["all", "self", "teacher"]

class SuggestionEvent(BaseEvent):
    """Player suggests to another."""
    type: Literal["suggestion"]
    content: str
    target_player: str | None  # None = all
    urgency: Literal["low", "medium", "high"]

class EmotionEvent(BaseEvent):
    """Emotional state update."""
    type: Literal["emotion"]
    dimension: str  # "enjoyment", "frustration", etc.
    value: float  # 0.0 to 1.0
    context: str | None
    raw_input: dict | None  # {"rt": 0.8, "lt": 0.1}

class TestResultEvent(BaseEvent):
    """Test execution results."""
    type: Literal["test_result"]
    passed: int
    total: int
    details: list[dict]
    execution_time_ms: float

# Union of all event types
GameEvent = Union[
    CursorMoveEvent,
    KeystrokeEvent,
    CodeUpdateEvent,
    ThoughtEvent,
    SuggestionEvent,
    EmotionEvent,
    TestResultEvent,
    # ... etc
]
```

### Schema Validation

```python
import jsonschema

EVENT_SCHEMAS = {
    "cursor_move": {
        "type": "object",
        "required": ["type", "player", "timestamp", "session_id", "line", "col"],
        "properties": {
            "type": {"const": "cursor_move"},
            "player": {"type": "string"},
            "timestamp": {"type": "number"},
            "session_id": {"type": "string"},
            "line": {"type": "integer", "minimum": 0},
            "col": {"type": "integer", "minimum": 0},
            "file": {"type": ["string", "null"]}
        }
    },
    "emotion": {
        "type": "object",
        "required": ["type", "player", "timestamp", "session_id", "dimension", "value"],
        "properties": {
            "type": {"const": "emotion"},
            "player": {"type": "string"},
            "timestamp": {"type": "number"},
            "session_id": {"type": "string"},
            "dimension": {
                "type": "string",
                "enum": ["enjoyment", "frustration", "engagement", "confusion"]
            },
            "value": {"type": "number", "minimum": 0.0, "maximum": 1.0},
            "context": {"type": ["string", "null"]},
            "raw_input": {"type": ["object", "null"]}
        }
    },
    # ... schemas for all event types
}

def validate_event(event_json: str) -> tuple[bool, str | None]:
    """Validate event against schema."""
    try:
        event = json.loads(event_json)
        event_type = event.get("type")

        if event_type not in EVENT_SCHEMAS:
            return False, f"Unknown event type: {event_type}"

        schema = EVENT_SCHEMAS[event_type]
        jsonschema.validate(event, schema)

        return True, None

    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"
    except jsonschema.ValidationError as e:
        return False, f"Schema validation failed: {e.message}"
```

---

## Implementation Guide

### Session Manager Implementation

```python
class StreamJsonSessionManager:
    """Manages stream-JSON multiplayer sessions."""

    def __init__(self):
        self.sessions: dict[str, SessionInfo] = {}

    async def create_session(
        self,
        session_id: str,
        players: list[PlayerConfig]
    ) -> Session:
        """Create and start a new session."""

        # Spawn player processes
        player_procs = {}
        for player_cfg in players:
            proc = await self.spawn_player_process(player_cfg)
            player_procs[player_cfg.name] = {
                "config": player_cfg,
                "process": proc,
                "done": False
            }

        # Create session info
        session_info = SessionInfo(
            session_id=session_id,
            players=player_procs,
            event_log=[],
            done_players=set()
        )

        self.sessions[session_id] = session_info

        # Start event forwarding loops
        for player_name, player_info in player_procs.items():
            asyncio.create_task(
                self.forward_player_events(
                    session_id,
                    player_name,
                    player_info["process"]
                )
            )

        return session_info

    async def spawn_player_process(self, player_cfg: PlayerConfig) -> subprocess.Process:
        """Spawn player process with stdin/stdout pipes."""

        if player_cfg.type == "claude":
            # Spawn Claude player
            cmd = [
                "python", "-m", "player_zero.player.claude",
                "--name", player_cfg.name,
                "--style", player_cfg.style
            ]

        elif player_cfg.type == "human":
            # Spawn human input handler
            cmd = [
                "python", "-m", "lmsp.input.handler",
                "--name", player_cfg.name,
                "--device", player_cfg.device
            ]

        # Spawn with pipes
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        return proc

    async def forward_player_events(
        self,
        session_id: str,
        player_name: str,
        process: subprocess.Process
    ):
        """Read events from player's stdout and forward to others."""

        session = self.sessions[session_id]

        while True:
            try:
                # Read line from stdout
                line = await process.stdout.readline()
                if not line:
                    break  # Process ended

                event_json = line.decode('utf-8').strip()

                # Validate event
                valid, error = validate_event(event_json)
                if not valid:
                    logging.warning(f"Invalid event from {player_name}: {error}")
                    continue

                # Log event
                session.event_log.append({
                    "source": player_name,
                    "event": event_json,
                    "timestamp": time.time()
                })

                # Forward to other players
                self._forward_to_other_agents(
                    source_player_id=player_name,
                    event_json=event_json,
                    players=session.players,
                    done_players=session.done_players
                )

            except Exception as e:
                logging.error(f"Error forwarding events from {player_name}: {e}")
                break

        # Player process ended
        session.done_players.add(player_name)

    def _forward_to_other_agents(
        self,
        source_player_id: str,
        event_json: str,
        players: dict,
        done_players: set
    ):
        """The 18-line magic - forward to all other players."""
        for player_id, player_info in players.items():
            if player_id == source_player_id:
                continue
            if player_id in done_players:
                continue

            try:
                player_info["process"].stdin.write((event_json + "\n").encode('utf-8'))
                player_info["process"].stdin.flush()
            except BrokenPipeError:
                done_players.add(player_id)
            except Exception as e:
                logging.warning(f"Failed to forward to {player_id}: {e}")
```

### Player Process Implementation

```python
class StreamJsonPlayer(ABC):
    """Base class for players that use stream-JSON."""

    def __init__(self, name: str, session_id: str):
        self.name = name
        self.session_id = session_id
        self.running = False

    async def run(self):
        """Main player loop."""
        self.running = True

        # Spawn two tasks:
        # 1. Read from stdin (events from others)
        # 2. Generate and write to stdout (my events)

        await asyncio.gather(
            self.stdin_loop(),
            self.action_loop()
        )

    async def stdin_loop(self):
        """Read events from stdin."""
        while self.running:
            try:
                # Read line from stdin
                line = await asyncio.get_event_loop().run_in_executor(
                    None,
                    sys.stdin.readline
                )

                if not line:
                    break

                event_json = line.strip()
                await self.process_event(event_json)

            except Exception as e:
                logging.error(f"Error reading stdin: {e}")
                break

    @abstractmethod
    async def action_loop(self):
        """Generate actions and write to stdout."""
        pass

    @abstractmethod
    async def process_event(self, event_json: str):
        """Process incoming event from stdin."""
        pass

    def emit_event(self, event: dict):
        """Write event to stdout."""
        event["player"] = self.name
        event["timestamp"] = time.time()
        event["session_id"] = self.session_id

        event_json = json.dumps(event)
        print(event_json, flush=True)
```

### Example: Claude Player

```python
class ClaudeStreamPlayer(StreamJsonPlayer):
    """Claude player using stream-JSON."""

    async def action_loop(self):
        """Generate actions via Claude."""
        while self.running:
            # Build context from awareness
            context = self.build_context()

            # Query Claude
            response = await self.query_claude(context)

            # Parse response to events
            events = self.parse_response(response)

            # Emit events
            for event in events:
                self.emit_event(event)

            # Wait before next action
            await asyncio.sleep(1.0)

    async def process_event(self, event_json: str):
        """Update awareness from incoming event."""
        event = json.loads(event_json)

        # Track in awareness model
        self.awareness.update(event)

        # React to specific events
        if event["type"] == "question" and event.get("target_player") == self.name:
            # Someone asked me a question
            answer = await self.answer_question(event["content"])
            self.emit_event({
                "type": "answer",
                "question": event["content"],
                "answer": answer
            })
```

---

## Summary

The stream-JSON protocol is the magic that makes LMSP multiplayer work:

- **18 lines** - Core broadcast function from Palace
- **stdin/stdout** - Simple, fast, portable transport
- **Line-delimited JSON** - Easy to parse, log, debug
- **Rich events** - Movement, cognition, emotion, progress
- **Multi-agent awareness** - Each player knows what others are doing
- **Claude-native** - Built for AI player integration

This protocol proves that complex multiplayer coordination doesn't require complex infrastructure. Just processes, pipes, and JSON.

---

*The simplest thing that could possibly work... and it does.*
