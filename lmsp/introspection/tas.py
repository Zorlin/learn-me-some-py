"""
TAS - Tool-Assisted Learning (Speedrun-style)

Provides "save state" features for learning:
- Checkpoint: Save state at any point
- Restore: Return to any saved state
- Rewind: Step backward through history
- Step: Move forward one action at a time
- Diff: See what changed between states

Inspired by TAS (Tool-Assisted Speedrun) techniques,
adapted for educational purposes.

Self-teaching note:
This file demonstrates:
- Snapshot pattern (Level 5: deep copy)
- Command history with undo (Level 5: stacks)
- Diffing algorithms (Level 6: comparison)
- Enum for event types (Level 4: enums)
- Context managers for checkpoints (Level 5: with)
"""

from dataclasses import dataclass, field
from typing import Optional, Any, Iterator
from datetime import datetime
from enum import Enum, auto
import copy
import json
from difflib import unified_diff


class TASEventType(Enum):
    """Types of recordable events."""
    KEYSTROKE = auto()
    CODE_CHANGE = auto()
    CURSOR_MOVE = auto()
    TEST_RUN = auto()
    TEST_PASS = auto()
    TEST_FAIL = auto()
    HINT_USED = auto()
    CHECKPOINT = auto()
    RESTORE = auto()
    EMOTION = auto()


@dataclass
class TASEvent:
    """
    A single recordable event in the TAS history.

    Events form the "tape" that can be replayed, rewound, or analyzed.
    """

    # Event type can be string or TASEventType for flexibility
    event_type: Any = None  # str or TASEventType
    timestamp: datetime = field(default_factory=datetime.now)
    frame_number: int = 0

    # Code state at this event
    code: str = ""
    cursor_position: tuple[int, int] = (0, 0)

    # Event-specific data
    data: dict[str, Any] = field(default_factory=dict)

    # Game state (for test compatibility)
    game_state: Any = field(default=None)

    # For replay
    duration_ms: float = 0.0  # Time since last event

    def __post_init__(self):
        """Handle game_state initialization."""
        if self.game_state is not None:
            # Extract game_state into data if it's not a dict already
            if isinstance(self.game_state, dict):
                self.data = {**self.data, **self.game_state}
            else:
                # It's a GameState object
                self.code = getattr(self.game_state, "current_code", self.code)
                self.cursor_position = getattr(self.game_state, "cursor_position", self.cursor_position)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        event_type_str = self.event_type
        if isinstance(self.event_type, TASEventType):
            event_type_str = self.event_type.name

        return {
            "event_type": event_type_str,
            "timestamp": self.timestamp.isoformat(),
            "frame_number": self.frame_number,
            "code": self.code,
            "cursor_position": list(self.cursor_position),
            "data": self.data,
            "duration_ms": self.duration_ms,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TASEvent":
        """Deserialize from dictionary."""
        event_type = data.get("event_type", "")
        # Try to convert to TASEventType if it's a valid enum name
        try:
            if isinstance(event_type, str) and event_type in TASEventType.__members__:
                event_type = TASEventType[event_type]
        except (KeyError, ValueError):
            pass  # Keep as string

        return cls(
            event_type=event_type,
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else datetime.now(),
            frame_number=data.get("frame_number", 0),
            code=data.get("code", ""),
            cursor_position=tuple(data.get("cursor_position", [0, 0])),
            data=data.get("data", {}),
            duration_ms=data.get("duration_ms", 0.0),
        )


@dataclass
class TASCheckpoint:
    """
    A saved state that can be restored.

    Checkpoints capture the complete state at a moment in time.
    """

    name: str
    frame_number: int = 0
    timestamp: datetime = field(default_factory=datetime.now)

    # Complete state snapshot
    code: str = ""
    cursor_position: tuple[int, int] = (0, 0)
    tests_passing: int = 0
    tests_total: int = 0
    hints_used: int = 0

    # Additional context
    notes: str = ""
    auto_saved: bool = False

    @property
    def current_code(self) -> str:
        """Alias for code (test compatibility)."""
        return self.code

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "name": self.name,
            "frame_number": self.frame_number,
            "timestamp": self.timestamp.isoformat(),
            "code": self.code,
            "cursor_position": list(self.cursor_position),
            "tests_passing": self.tests_passing,
            "tests_total": self.tests_total,
            "hints_used": self.hints_used,
            "notes": self.notes,
            "auto_saved": self.auto_saved,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TASCheckpoint":
        """Deserialize from dictionary."""
        return cls(
            name=data["name"],
            frame_number=data.get("frame_number", 0),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            code=data.get("code", ""),
            cursor_position=tuple(data.get("cursor_position", [0, 0])),
            tests_passing=data.get("tests_passing", 0),
            tests_total=data.get("tests_total", 0),
            hints_used=data.get("hints_used", 0),
            notes=data.get("notes", ""),
            auto_saved=data.get("auto_saved", False),
        )


class TASRecorder:
    """
    Tool-Assisted Learning recorder.

    Records gameplay events and provides checkpoint/restore capabilities.

    Usage:
        recorder = TASRecorder()
        recorder.start()

        # During gameplay
        recorder.record_event(TASEventType.KEYSTROKE, code="x = 1", data={"char": "x"})
        recorder.checkpoint("before_refactor")

        # Try something risky
        recorder.record_event(TASEventType.CODE_CHANGE, code="x = complicated()")

        # If it fails, restore
        recorder.restore("before_refactor")

        # Step through history
        recorder.rewind(steps=5)
        recorder.step_forward()
    """

    def __init__(self, max_events: int = 10000):
        """
        Create a TAS recorder.

        Args:
            max_events: Maximum events to keep in history
        """
        self.max_events = max_events

        # Event history
        self._events: list[TASEvent] = []
        self._current_frame: int = 0

        # Checkpoints
        self._checkpoints: dict[str, TASCheckpoint] = {}

        # Current state
        self._code: str = ""
        self._cursor: tuple[int, int] = (0, 0)
        self._tests_passing: int = 0
        self._tests_total: int = 0
        self._hints_used: int = 0

        # Recording state
        self._is_recording: bool = False
        self._playback_position: int = -1  # -1 = live (not in playback)
        self.playback_index: int = 0  # For test compatibility

        # Timing
        self._last_event_time: Optional[datetime] = None
        self._start_time: Optional[datetime] = None

    @property
    def is_recording(self) -> bool:
        """Check if recording is active."""
        return self._is_recording

    @property
    def is_playing_back(self) -> bool:
        """Check if in playback mode."""
        return self._playback_position >= 0

    @property
    def event_count(self) -> int:
        """Get total events recorded."""
        return len(self._events)

    @property
    def current_frame(self) -> int:
        """Get current frame number."""
        return self._current_frame

    @property
    def events(self) -> list[TASEvent]:
        """Get list of all events."""
        return self._events

    @property
    def checkpoints(self) -> dict[str, TASCheckpoint]:
        """Get all checkpoints."""
        return self._checkpoints

    def start(self):
        """Start recording."""
        self._is_recording = True
        self._start_time = datetime.now()
        self._last_event_time = datetime.now()

    def stop(self):
        """Stop recording."""
        self._is_recording = False

    def record(self, event: TASEvent) -> TASEvent:
        """
        Record a pre-constructed TASEvent.

        Args:
            event: TASEvent to record

        Returns:
            The recorded event (with frame_number updated)
        """
        if not self._is_recording:
            # Auto-start if not recording
            self.start()

        # Calculate time since last event
        now = datetime.now()
        duration_ms = 0.0
        if self._last_event_time:
            duration_ms = (now - self._last_event_time).total_seconds() * 1000

        # Update event with frame info
        event.frame_number = self._current_frame
        event.timestamp = now
        event.duration_ms = duration_ms

        # Update internal state from event
        if event.code:
            self._code = event.code
        if event.cursor_position != (0, 0):
            self._cursor = event.cursor_position

        # Add to history
        self._events.append(event)
        self._current_frame += 1
        self._last_event_time = now

        # Trim if over limit
        if len(self._events) > self.max_events:
            self._events = self._events[-self.max_events:]

        return event

    def record_event(
        self,
        event_type: TASEventType,
        code: Optional[str] = None,
        cursor: Optional[tuple[int, int]] = None,
        data: Optional[dict[str, Any]] = None
    ) -> TASEvent:
        """
        Record an event.

        Args:
            event_type: Type of event
            code: Current code state (uses last known if None)
            cursor: Current cursor position (uses last known if None)
            data: Additional event data

        Returns:
            The recorded event
        """
        if not self._is_recording:
            raise RuntimeError("Recording not started")

        # Calculate time since last event
        now = datetime.now()
        duration_ms = 0.0
        if self._last_event_time:
            duration_ms = (now - self._last_event_time).total_seconds() * 1000

        # Update state if provided
        if code is not None:
            self._code = code
        if cursor is not None:
            self._cursor = cursor

        # Create event
        event = TASEvent(
            event_type=event_type,
            timestamp=now,
            frame_number=self._current_frame,
            code=self._code,
            cursor_position=self._cursor,
            data=data or {},
            duration_ms=duration_ms,
        )

        # Add to history
        self._events.append(event)
        self._current_frame += 1
        self._last_event_time = now

        # Trim if over limit
        if len(self._events) > self.max_events:
            self._events = self._events[-self.max_events:]

        return event

    def checkpoint(
        self,
        name: str,
        state: Any = None,
        notes: str = "",
        auto_saved: bool = False
    ) -> TASCheckpoint:
        """
        Save a checkpoint at current state.

        Args:
            name: Checkpoint name (overwrites if exists)
            state: Optional GameState to capture (uses internal state if None)
            notes: Optional notes about this checkpoint
            auto_saved: True if system-generated

        Returns:
            The created checkpoint
        """
        # Extract state from GameState if provided
        code = self._code
        cursor = self._cursor
        tests_passing = self._tests_passing
        tests_total = self._tests_total
        hints_used = self._hints_used

        if state is not None:
            code = getattr(state, "current_code", code)
            cursor = getattr(state, "cursor_position", cursor)
            tests_passing = getattr(state, "tests_passing", tests_passing)
            tests_total = getattr(state, "tests_total", tests_total)
            hints_used = getattr(state, "hints_used", hints_used)
            # Update internal state too
            self._code = code
            self._cursor = cursor
            self._tests_passing = tests_passing
            self._tests_total = tests_total
            self._hints_used = hints_used

        checkpoint = TASCheckpoint(
            name=name,
            frame_number=self._current_frame,
            code=code,
            cursor_position=cursor,
            tests_passing=tests_passing,
            tests_total=tests_total,
            hints_used=hints_used,
            notes=notes,
            auto_saved=auto_saved,
        )

        self._checkpoints[name] = checkpoint

        # Record checkpoint event
        if self._is_recording:
            self.record_event(
                TASEventType.CHECKPOINT,
                data={"checkpoint_name": name}
            )

        return checkpoint

    def restore(self, name: str) -> TASCheckpoint:
        """
        Restore state from a checkpoint.

        Args:
            name: Checkpoint name

        Returns:
            The restored checkpoint

        Raises:
            KeyError: If checkpoint not found
        """
        if name not in self._checkpoints:
            raise KeyError(f"Checkpoint '{name}' not found")

        checkpoint = self._checkpoints[name]

        # Restore state
        self._code = checkpoint.code
        self._cursor = checkpoint.cursor_position
        self._tests_passing = checkpoint.tests_passing
        self._tests_total = checkpoint.tests_total
        self._hints_used = checkpoint.hints_used

        # Record restore event
        if self._is_recording:
            self.record_event(
                TASEventType.RESTORE,
                data={"checkpoint_name": name, "restored_to_frame": checkpoint.frame_number}
            )

        return checkpoint

    def get_checkpoint(self, name: str) -> Optional[TASCheckpoint]:
        """Get a checkpoint by name."""
        return self._checkpoints.get(name)

    def list_checkpoints(self) -> list[str]:
        """Get list of checkpoint names."""
        return list(self._checkpoints.keys())

    def delete_checkpoint(self, name: str):
        """Delete a checkpoint."""
        if name in self._checkpoints:
            del self._checkpoints[name]

    def rewind(self, steps: int = 1) -> Optional[TASEvent]:
        """
        Rewind history by N steps.

        Args:
            steps: Number of steps to go back

        Returns:
            Event at new position, or None if at beginning
        """
        # Enter playback mode if not already
        if self._playback_position < 0:
            self._playback_position = len(self._events) - 1

        # Calculate new position
        new_pos = max(0, self._playback_position - steps)
        self._playback_position = new_pos

        # Restore state from that event
        if self._events and new_pos < len(self._events):
            event = self._events[new_pos]
            self._code = event.code
            self._cursor = event.cursor_position
            return event

        return None

    def step_forward(self) -> Optional[TASEvent]:
        """
        Step forward one event.

        Returns:
            Event at new position, or None if at end
        """
        # Start from beginning if not in playback mode
        if self._playback_position < 0:
            self._playback_position = -1
            new_pos = 0
        else:
            new_pos = self._playback_position + 1

        if new_pos >= len(self._events):
            # Reached end, exit playback
            self._playback_position = -1
            return None

        self._playback_position = new_pos
        self.playback_index = new_pos
        event = self._events[new_pos]

        # Restore state from event
        self._code = event.code
        self._cursor = event.cursor_position

        return event

    def step_backward(self) -> Optional[TASEvent]:
        """
        Step backward one event.

        Returns:
            Event at previous position, or None if at beginning
        """
        # Enter playback mode at end if not already
        if self._playback_position < 0:
            self._playback_position = len(self._events)
            self.playback_index = self._playback_position

        new_pos = self._playback_position - 1

        if new_pos < 0:
            # At beginning
            return None

        self._playback_position = new_pos
        self.playback_index = new_pos
        event = self._events[new_pos]

        # Restore state from event
        self._code = event.code
        self._cursor = event.cursor_position

        return event

    def reset_playback(self):
        """Reset playback to beginning."""
        self._playback_position = -1
        self.playback_index = 0

    def rewind_to(self, checkpoint_name: str) -> TASCheckpoint:
        """
        Rewind to a named checkpoint.

        Args:
            checkpoint_name: Name of checkpoint to rewind to

        Returns:
            The checkpoint that was restored

        Raises:
            KeyError: If checkpoint not found
        """
        return self.restore(checkpoint_name)

    def exit_playback(self):
        """Exit playback mode, return to live state."""
        if self._events:
            # Restore to latest state
            last_event = self._events[-1]
            self._code = last_event.code
            self._cursor = last_event.cursor_position

        self._playback_position = -1

    def diff(self, from_frame: int, to_frame: int) -> list[str]:
        """
        Get diff between two frames.

        Args:
            from_frame: Starting frame number
            to_frame: Ending frame number

        Returns:
            List of diff lines (unified diff format)
        """
        # Find events at those frames
        from_event = self._get_event_at_frame(from_frame)
        to_event = self._get_event_at_frame(to_frame)

        if not from_event or not to_event:
            return []

        # Generate unified diff
        from_lines = from_event.code.splitlines(keepends=True)
        to_lines = to_event.code.splitlines(keepends=True)

        diff_lines = list(unified_diff(
            from_lines,
            to_lines,
            fromfile=f"frame_{from_frame}",
            tofile=f"frame_{to_frame}",
        ))

        return diff_lines

    def diff_from_checkpoint(self, checkpoint_name: str) -> list[str]:
        """
        Get diff from a checkpoint to current state.

        Args:
            checkpoint_name: Name of checkpoint

        Returns:
            List of diff lines
        """
        checkpoint = self._checkpoints.get(checkpoint_name)
        if not checkpoint:
            return []

        # Generate diff
        from_lines = checkpoint.code.splitlines(keepends=True)
        to_lines = self._code.splitlines(keepends=True)

        diff_lines = list(unified_diff(
            from_lines,
            to_lines,
            fromfile=f"checkpoint:{checkpoint_name}",
            tofile="current",
        ))

        return diff_lines

    def diff_checkpoints(self, name1: str, name2: str) -> dict[str, Any]:
        """
        Compare two checkpoints and return structured diff.

        Args:
            name1: First checkpoint name
            name2: Second checkpoint name

        Returns:
            Dictionary with diff info:
            - code_changed: bool
            - tests_passing_diff: int (positive means more tests passing)
            - diff_lines: list of unified diff lines
        """
        cp1 = self._checkpoints.get(name1)
        cp2 = self._checkpoints.get(name2)

        if not cp1 or not cp2:
            return {
                "code_changed": False,
                "tests_passing_diff": 0,
                "diff_lines": [],
            }

        # Check if code changed
        code_changed = cp1.code != cp2.code

        # Calculate test diff
        tests_passing_diff = cp2.tests_passing - cp1.tests_passing

        # Generate diff lines
        from_lines = cp1.code.splitlines(keepends=True)
        to_lines = cp2.code.splitlines(keepends=True)

        diff_lines = list(unified_diff(
            from_lines,
            to_lines,
            fromfile=f"checkpoint:{name1}",
            tofile=f"checkpoint:{name2}",
        ))

        return {
            "code_changed": code_changed,
            "tests_passing_diff": tests_passing_diff,
            "diff_lines": diff_lines,
        }

    def export(self) -> str:
        """
        Export recording to JSON string.

        Returns:
            JSON string representation
        """
        # Calculate duration
        duration = 0.0
        if self._start_time:
            end_time = datetime.now()
            duration = (end_time - self._start_time).total_seconds()

        data = {
            "events": [e.to_dict() for e in self._events],
            "checkpoints": {
                name: cp.to_dict()
                for name, cp in self._checkpoints.items()
            },
            "current_frame": self._current_frame,
            "duration": duration,
            "state": self.get_state(),
        }

        return json.dumps(data, indent=2)

    def _get_event_at_frame(self, frame_number: int) -> Optional[TASEvent]:
        """Get event at specific frame number."""
        for event in self._events:
            if event.frame_number == frame_number:
                return event
        return None

    def get_events(
        self,
        event_type: Optional[TASEventType] = None,
        from_frame: Optional[int] = None,
        to_frame: Optional[int] = None
    ) -> Iterator[TASEvent]:
        """
        Get events with optional filtering.

        Args:
            event_type: Filter by event type
            from_frame: Starting frame (inclusive)
            to_frame: Ending frame (inclusive)

        Yields:
            Matching events
        """
        for event in self._events:
            # Filter by type
            if event_type and event.event_type != event_type:
                continue

            # Filter by frame range
            if from_frame is not None and event.frame_number < from_frame:
                continue
            if to_frame is not None and event.frame_number > to_frame:
                continue

            yield event

    def get_state(self) -> dict[str, Any]:
        """Get current state."""
        return {
            "code": self._code,
            "cursor_position": self._cursor,
            "tests_passing": self._tests_passing,
            "tests_total": self._tests_total,
            "hints_used": self._hints_used,
            "current_frame": self._current_frame,
            "is_recording": self._is_recording,
            "is_playing_back": self.is_playing_back,
        }

    def set_state(
        self,
        code: Optional[str] = None,
        cursor: Optional[tuple[int, int]] = None,
        tests_passing: Optional[int] = None,
        tests_total: Optional[int] = None,
        hints_used: Optional[int] = None
    ):
        """Update current state."""
        if code is not None:
            self._code = code
        if cursor is not None:
            self._cursor = cursor
        if tests_passing is not None:
            self._tests_passing = tests_passing
        if tests_total is not None:
            self._tests_total = tests_total
        if hints_used is not None:
            self._hints_used = hints_used

    def save(self, filepath: str):
        """Save recording to file."""
        data = {
            "events": [e.to_dict() for e in self._events],
            "checkpoints": {
                name: cp.to_dict()
                for name, cp in self._checkpoints.items()
            },
            "current_frame": self._current_frame,
            "state": self.get_state(),
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, filepath: str) -> "TASRecorder":
        """Load recording from file."""
        with open(filepath, "r") as f:
            data = json.load(f)

        recorder = cls()

        # Restore events
        for event_data in data.get("events", []):
            recorder._events.append(TASEvent.from_dict(event_data))

        # Restore checkpoints
        for name, cp_data in data.get("checkpoints", {}).items():
            recorder._checkpoints[name] = TASCheckpoint.from_dict(cp_data)

        # Restore state
        recorder._current_frame = data.get("current_frame", 0)
        state = data.get("state", {})
        recorder._code = state.get("code", "")
        recorder._cursor = tuple(state.get("cursor_position", [0, 0]))
        recorder._tests_passing = state.get("tests_passing", 0)
        recorder._tests_total = state.get("tests_total", 0)
        recorder._hints_used = state.get("hints_used", 0)

        return recorder

    def __repr__(self) -> str:
        """String representation."""
        status = "recording" if self._is_recording else "stopped"
        playback = f", playback@{self._playback_position}" if self.is_playing_back else ""
        return (
            f"TASRecorder({status}, events={len(self._events)}, "
            f"checkpoints={len(self._checkpoints)}{playback})"
        )


# Self-teaching note:
#
# This file demonstrates:
# - Snapshot/memento pattern (checkpoints)
# - Command pattern (events as recordable actions)
# - Undo/redo via rewind/step_forward
# - Diffing with difflib.unified_diff
# - State machine (recording, playback, live)
# - Iterator protocol (get_events generator)
#
# Key concepts:
# 1. Checkpoints - save complete state for restore
# 2. Event recording - capture actions as they happen
# 3. Rewind/step - navigate through history
# 4. Diffing - see what changed between states
# 5. Serialization - save/load recordings
#
# The learner will encounter this AFTER mastering:
# - Level 4: Enums, dictionaries, iteration
# - Level 5: Classes, generators, context managers
# - Level 6: Design patterns, deep copy, difflib
