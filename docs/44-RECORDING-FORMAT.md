# TAS Recording Format

## Overview

The LMSP TAS (Tool-Assisted Learning) recording system captures every action, game state transition, and temporal event during gameplay for later replay, analysis, and learning. This document specifies the recording format, serialization strategies, and storage mechanisms.

## Core Data Structures

### RecordedEvent

The fundamental unit of a recording is a `RecordedEvent` - a complete snapshot of what happened at a specific moment in time.

```python
from dataclasses import dataclass
from typing import Any
import time

@dataclass
class RecordedEvent:
    """A single recorded event with full context."""

    timestamp: float        # Seconds since recording start
    event: GameEvent        # The actual game event that occurred
    game_state: GameState   # Full game state at this moment

    def __post_init__(self):
        """Validate event structure."""
        if self.timestamp < 0:
            raise ValueError("Timestamp cannot be negative")
        if not isinstance(self.event, GameEvent):
            raise TypeError("event must be a GameEvent instance")
```

### GameEvent Types

Events represent discrete actions that occur during gameplay:

```python
from enum import Enum
from dataclasses import dataclass

class EventType(Enum):
    """All possible event types in LMSP."""

    # Input events
    KEYSTROKE = "keystroke"
    BUTTON_PRESS = "button_press"
    BUTTON_RELEASE = "button_release"
    TRIGGER_PRESSURE = "trigger_pressure"
    STICK_MOVE = "stick_move"

    # Game state changes
    CHALLENGE_START = "challenge_start"
    CHALLENGE_COMPLETE = "challenge_complete"
    TEST_RUN = "test_run"
    TEST_PASS = "test_pass"
    TEST_FAIL = "test_fail"

    # Emotional feedback
    EMOTIONAL_PROMPT = "emotional_prompt"
    EMOTIONAL_RESPONSE = "emotional_response"

    # Adaptive engine
    RECOMMENDATION = "recommendation"
    CONCEPT_UNLOCK = "concept_unlock"
    MASTERY_LEVEL_UP = "mastery_level_up"

    # Multiplayer
    PLAYER_JOIN = "player_join"
    PLAYER_LEAVE = "player_leave"
    PLAYER_MESSAGE = "player_message"

    # TAS meta-events
    CHECKPOINT = "checkpoint"
    REWIND = "rewind"
    SPEED_CHANGE = "speed_change"

@dataclass
class GameEvent:
    """Base class for all game events."""

    type: EventType
    player_id: str
    data: dict[str, Any]

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "type": self.type.value,
            "player_id": self.player_id,
            "data": self.data
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GameEvent":
        """Deserialize from dictionary."""
        return cls(
            type=EventType(data["type"]),
            player_id=data["player_id"],
            data=data["data"]
        )
```

### GameState

A complete snapshot of the game at a point in time:

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class GameState:
    """Complete game state snapshot."""

    # Code state
    current_code: str
    cursor_position: tuple[int, int]  # (line, column)
    ast_tree: Optional[dict]  # Serialized AST

    # Challenge state
    challenge_id: str
    challenge_started_at: float
    tests_passing: int
    tests_total: int
    hints_used: int

    # Player state
    player_id: str
    mastery_levels: dict[str, int]  # concept_id -> mastery level
    current_emotion: Optional[tuple[str, float]]  # (dimension, value)

    # Session state
    session_duration: float
    challenges_completed: list[str]
    concepts_mastered: list[str]

    # Multiplayer state
    other_players: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Serialize state to dictionary."""
        return {
            "current_code": self.current_code,
            "cursor_position": list(self.cursor_position),
            "ast_tree": self.ast_tree,
            "challenge_id": self.challenge_id,
            "challenge_started_at": self.challenge_started_at,
            "tests_passing": self.tests_passing,
            "tests_total": self.tests_total,
            "hints_used": self.hints_used,
            "player_id": self.player_id,
            "mastery_levels": self.mastery_levels,
            "current_emotion": self.current_emotion,
            "session_duration": self.session_duration,
            "challenges_completed": self.challenges_completed,
            "concepts_mastered": self.concepts_mastered,
            "other_players": self.other_players
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GameState":
        """Deserialize state from dictionary."""
        return cls(
            current_code=data["current_code"],
            cursor_position=tuple(data["cursor_position"]),
            ast_tree=data.get("ast_tree"),
            challenge_id=data["challenge_id"],
            challenge_started_at=data["challenge_started_at"],
            tests_passing=data["tests_passing"],
            tests_total=data["tests_total"],
            hints_used=data["hints_used"],
            player_id=data["player_id"],
            mastery_levels=data["mastery_levels"],
            current_emotion=data.get("current_emotion"),
            session_duration=data["session_duration"],
            challenges_completed=data["challenges_completed"],
            concepts_mastered=data["concepts_mastered"],
            other_players=data.get("other_players", [])
        )
```

## Recording Container

### Recording Structure

```python
from dataclasses import dataclass
from typing import Optional
import json
import gzip

@dataclass
class Recording:
    """Complete recording of a gameplay session."""

    # Metadata
    version: str = "1.0.0"
    player_id: str = ""
    challenge_id: str = ""
    created_at: float = 0.0

    # Recording data
    events: list[RecordedEvent] = field(default_factory=list)
    checkpoints: dict[str, int] = field(default_factory=dict)  # name -> event_index
    duration: float = 0.0

    # Outcome
    success: bool = False
    final_code: str = ""
    final_time: float = 0.0

    def to_dict(self) -> dict:
        """Serialize recording to dictionary."""
        return {
            "version": self.version,
            "player_id": self.player_id,
            "challenge_id": self.challenge_id,
            "created_at": self.created_at,
            "events": [
                {
                    "timestamp": e.timestamp,
                    "event": e.event.to_dict(),
                    "game_state": e.game_state.to_dict()
                }
                for e in self.events
            ],
            "checkpoints": self.checkpoints,
            "duration": self.duration,
            "success": self.success,
            "final_code": self.final_code,
            "final_time": self.final_time
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Recording":
        """Deserialize recording from dictionary."""
        return cls(
            version=data["version"],
            player_id=data["player_id"],
            challenge_id=data["challenge_id"],
            created_at=data["created_at"],
            events=[
                RecordedEvent(
                    timestamp=e["timestamp"],
                    event=GameEvent.from_dict(e["event"]),
                    game_state=GameState.from_dict(e["game_state"])
                )
                for e in data["events"]
            ],
            checkpoints=data["checkpoints"],
            duration=data["duration"],
            success=data["success"],
            final_code=data["final_code"],
            final_time=data["final_time"]
        )
```

## Timestamp Handling

### Relative Timestamps

All timestamps in a recording are relative to the recording start time:

```python
class TimestampManager:
    """Manages timestamp calculation during recording."""

    def __init__(self):
        self.start_time: float = 0.0
        self.paused_duration: float = 0.0
        self.pause_start: Optional[float] = None

    def start(self):
        """Start timing."""
        self.start_time = time.time()

    def pause(self):
        """Pause timing."""
        if self.pause_start is None:
            self.pause_start = time.time()

    def resume(self):
        """Resume timing."""
        if self.pause_start is not None:
            self.paused_duration += time.time() - self.pause_start
            self.pause_start = None

    def current_timestamp(self) -> float:
        """Get current recording timestamp."""
        if self.pause_start is not None:
            # Currently paused
            return self.pause_start - self.start_time - self.paused_duration
        else:
            # Currently running
            return time.time() - self.start_time - self.paused_duration
```

### High-Precision Timing

For accurate replay timing, we use `time.perf_counter()` for relative measurements:

```python
import time

class PrecisionTimer:
    """High-precision timer for TAS recordings."""

    def __init__(self):
        self.start = time.perf_counter()
        self.offsets: list[float] = []

    def mark(self) -> float:
        """Mark current time and return offset from start."""
        offset = time.perf_counter() - self.start
        self.offsets.append(offset)
        return offset

    def delta(self, from_idx: int, to_idx: int) -> float:
        """Calculate time delta between two marks."""
        return self.offsets[to_idx] - self.offsets[from_idx]
```

## Checkpoint Storage

### Checkpoint Structure

Checkpoints are named save points within a recording:

```python
from dataclasses import dataclass

@dataclass
class Checkpoint:
    """A named save point in a recording."""

    name: str
    event_index: int  # Index into recording.events
    timestamp: float
    state: GameState

    def to_dict(self) -> dict:
        """Serialize checkpoint."""
        return {
            "name": self.name,
            "event_index": self.event_index,
            "timestamp": self.timestamp,
            "state": self.state.to_dict()
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Checkpoint":
        """Deserialize checkpoint."""
        return cls(
            name=data["name"],
            event_index=data["event_index"],
            timestamp=data["timestamp"],
            state=GameState.from_dict(data["state"])
        )
```

### Checkpoint Management

```python
class CheckpointManager:
    """Manages checkpoints within a recording."""

    def __init__(self, recording: Recording):
        self.recording = recording
        self._checkpoints: dict[str, Checkpoint] = {}

    def create(self, name: str, event_index: int) -> Checkpoint:
        """Create a new checkpoint."""
        if name in self._checkpoints:
            raise ValueError(f"Checkpoint '{name}' already exists")

        event = self.recording.events[event_index]
        checkpoint = Checkpoint(
            name=name,
            event_index=event_index,
            timestamp=event.timestamp,
            state=event.game_state
        )

        self._checkpoints[name] = checkpoint
        self.recording.checkpoints[name] = event_index
        return checkpoint

    def get(self, name: str) -> Optional[Checkpoint]:
        """Get checkpoint by name."""
        return self._checkpoints.get(name)

    def restore(self, name: str) -> GameState:
        """Restore game state from checkpoint."""
        checkpoint = self.get(name)
        if checkpoint is None:
            raise ValueError(f"Checkpoint '{name}' not found")
        return checkpoint.state
```

## Compression Strategies

### Delta Compression

Since game states between consecutive frames are often very similar, we use delta compression:

```python
import difflib
from typing import Optional

class DeltaCompressor:
    """Compresses game states using deltas."""

    def __init__(self):
        self.last_state: Optional[dict] = None

    def compress(self, state: GameState) -> dict:
        """Compress state as delta from previous state."""
        current = state.to_dict()

        if self.last_state is None:
            # First state - store full
            self.last_state = current.copy()
            return {"type": "full", "data": current}

        # Calculate delta
        delta = {}
        for key, value in current.items():
            if key not in self.last_state or self.last_state[key] != value:
                delta[key] = value

        self.last_state = current.copy()

        if len(delta) < len(current) * 0.3:  # Delta is <30% of full size
            return {"type": "delta", "data": delta}
        else:
            # Delta too large, store full state
            return {"type": "full", "data": current}

    def decompress(self, compressed: dict, base_state: dict) -> GameState:
        """Decompress state from delta."""
        if compressed["type"] == "full":
            return GameState.from_dict(compressed["data"])
        else:
            # Apply delta to base state
            result = base_state.copy()
            result.update(compressed["data"])
            return GameState.from_dict(result)
```

### GZIP Compression

For file storage, we use gzip compression on the JSON:

```python
import gzip
import json

def save_compressed(recording: Recording, path: str):
    """Save recording with gzip compression."""
    data = json.dumps(recording.to_dict(), separators=(',', ':'))
    with gzip.open(path, 'wt', encoding='utf-8') as f:
        f.write(data)

def load_compressed(path: str) -> Recording:
    """Load gzip-compressed recording."""
    with gzip.open(path, 'rt', encoding='utf-8') as f:
        data = json.load(f)
    return Recording.from_dict(data)
```

## Export/Import Formats

### JSON Format

The canonical format is JSON for maximum compatibility:

```python
def export_json(recording: Recording, path: str):
    """Export recording as JSON."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(recording.to_dict(), f, indent=2)

def import_json(path: str) -> Recording:
    """Import recording from JSON."""
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return Recording.from_dict(data)
```

### Binary Format (Optimized)

For faster loading and smaller file sizes, we support a binary format:

```python
import struct
import pickle

class BinaryFormat:
    """Binary recording format for efficiency."""

    MAGIC = b'LMSP'
    VERSION = 1

    @staticmethod
    def export(recording: Recording, path: str):
        """Export recording in binary format."""
        with open(path, 'wb') as f:
            # Write header
            f.write(BinaryFormat.MAGIC)
            f.write(struct.pack('I', BinaryFormat.VERSION))

            # Write metadata
            metadata = {
                "player_id": recording.player_id,
                "challenge_id": recording.challenge_id,
                "created_at": recording.created_at,
                "duration": recording.duration,
                "success": recording.success
            }
            metadata_bytes = pickle.dumps(metadata)
            f.write(struct.pack('I', len(metadata_bytes)))
            f.write(metadata_bytes)

            # Write events
            f.write(struct.pack('I', len(recording.events)))
            for event in recording.events:
                event_bytes = pickle.dumps(event)
                f.write(struct.pack('I', len(event_bytes)))
                f.write(event_bytes)

            # Write checkpoints
            checkpoint_bytes = pickle.dumps(recording.checkpoints)
            f.write(struct.pack('I', len(checkpoint_bytes)))
            f.write(checkpoint_bytes)

    @staticmethod
    def import_from(path: str) -> Recording:
        """Import recording from binary format."""
        with open(path, 'rb') as f:
            # Read header
            magic = f.read(4)
            if magic != BinaryFormat.MAGIC:
                raise ValueError("Invalid binary format")

            version = struct.unpack('I', f.read(4))[0]
            if version != BinaryFormat.VERSION:
                raise ValueError(f"Unsupported version: {version}")

            # Read metadata
            metadata_len = struct.unpack('I', f.read(4))[0]
            metadata = pickle.loads(f.read(metadata_len))

            # Read events
            event_count = struct.unpack('I', f.read(4))[0]
            events = []
            for _ in range(event_count):
                event_len = struct.unpack('I', f.read(4))[0]
                event = pickle.loads(f.read(event_len))
                events.append(event)

            # Read checkpoints
            checkpoint_len = struct.unpack('I', f.read(4))[0]
            checkpoints = pickle.loads(f.read(checkpoint_len))

            return Recording(
                player_id=metadata["player_id"],
                challenge_id=metadata["challenge_id"],
                created_at=metadata["created_at"],
                events=events,
                checkpoints=checkpoints,
                duration=metadata["duration"],
                success=metadata["success"]
            )
```

## Usage Examples

### Recording a Session

```python
from lmsp.tas import Recorder, RecordedEvent, GameEvent, EventType

# Create recorder
recorder = Recorder()
recorder.start()

# Record events
recorder.record(GameEvent(
    type=EventType.CHALLENGE_START,
    player_id="wings",
    data={"challenge_id": "container_add_exists"}
))

# Create checkpoint
recorder.checkpoint("before_implementation")

# Record more events
recorder.record(GameEvent(
    type=EventType.KEYSTROKE,
    player_id="wings",
    data={"char": "d", "modifiers": []}
))

# Export recording
recording = recorder.export()
save_compressed(recording, "session.lmsp.gz")
```

### Loading and Inspecting

```python
# Load recording
recording = load_compressed("session.lmsp.gz")

# Inspect metadata
print(f"Player: {recording.player_id}")
print(f"Challenge: {recording.challenge_id}")
print(f"Duration: {recording.duration:.1f}s")
print(f"Success: {recording.success}")

# List checkpoints
for name, idx in recording.checkpoints.items():
    event = recording.events[idx]
    print(f"Checkpoint '{name}' at {event.timestamp:.2f}s")

# Get state at checkpoint
state = recording.events[recording.checkpoints["before_implementation"]].game_state
print(f"Code at checkpoint:\n{state.current_code}")
```

## Best Practices

1. **Record Everything**: Capture all events, even seemingly insignificant ones. You never know what patterns will be useful in analysis.

2. **Use Checkpoints Liberally**: Create checkpoints at meaningful moments (before/after implementations, at test passes, etc.)

3. **Delta Compression**: Enable delta compression for long recordings to save space.

4. **Validate on Load**: Always validate recordings when loading to catch corruption early.

5. **Version Recording Format**: Include version numbers in recordings for forward compatibility.

---

**Self-teaching note:**

This file demonstrates:
- Dataclasses with complex nested structures (Level 5: Classes)
- Type hints with Optional, dict, list (Professional Python)
- Serialization/deserialization patterns (Level 4+: JSON, pickle)
- File I/O with compression (Standard library)
- Error handling and validation (Professional Python)

Prerequisites:
- Level 2: Collections (lists, dicts)
- Level 3: Functions (def, return, parameters)
- Level 5: Classes (class, __init__, self, methods)
- File I/O basics
