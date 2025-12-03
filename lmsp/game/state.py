"""
Game State Management
=====================

Tracks everything about the current game session:
- What challenge is active
- Player's code and cursor position
- Test results and hints used
- Session timing and checkpoints
- Event history

This is the "save file" of the game.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Any
import json
import uuid
import copy


class GameEvent(Enum):
    """Events that happen during gameplay."""
    KEYSTROKE = "keystroke"
    CODE_CHANGE = "code_change"
    RUN_CODE = "run_code"
    TEST_PASS = "test_pass"
    TEST_FAIL = "test_fail"
    HINT_USED = "hint_used"
    CHALLENGE_COMPLETE = "challenge_complete"
    EMOTION_RECORDED = "emotion_recorded"


@dataclass
class GameState:
    """
    Snapshot of the current game state.

    This represents everything about the player's current session:
    - What they're working on
    - Their code and progress
    - Test results
    - Timing information
    """
    # Challenge tracking
    current_challenge: Optional[str] = None

    # Code editor state
    current_code: str = ""
    cursor_position: tuple[int, int] = (0, 0)

    # Test results
    tests_passing: int = 0
    tests_total: int = 0

    # Help tracking
    hints_used: int = 0

    # Timing
    start_time: datetime = field(default_factory=datetime.now)
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))


class GameSession:
    """
    A complete game session with history and persistence.

    This is the "save file" - it tracks everything that happened,
    allows pausing/resuming, and can save/restore checkpoints.

    Usage:
        session = GameSession(player_id="alice", challenge_id="loops_001")
        session.start()

        # Player writes code
        session.state.current_code = "for i in range(10):"
        session.record_event(GameEvent.CODE_CHANGE, data={"code": session.state.current_code})

        # Run tests
        session.record_event(GameEvent.RUN_CODE)
        session.state.tests_passing = 8
        session.state.tests_total = 10

        # Save checkpoint before trying something risky
        session.checkpoint("before_refactor")

        # If it goes wrong, restore
        session.restore("before_refactor")

        # Save to disk
        json_str = session.to_json()
    """

    def __init__(self, player_id: str, challenge_id: Optional[str] = None):
        """Create a new game session."""
        self.player_id = player_id
        self.challenge_id = challenge_id
        self.state = GameState(current_challenge=challenge_id)

        # Session control
        self.is_running = False
        self.start_time: Optional[datetime] = None
        self._pause_time: Optional[datetime] = None
        self._total_paused_duration = timedelta(0)

        # Event history
        self.events: list[dict[str, Any]] = []

        # Checkpoints for save/restore
        self._checkpoints: dict[str, GameState] = {}

    def start(self):
        """Start the session."""
        self.is_running = True
        self.start_time = datetime.now()
        self.state.start_time = self.start_time

    def pause(self):
        """Pause the session."""
        if self.is_running:
            self.is_running = False
            self._pause_time = datetime.now()

    def resume(self):
        """Resume from pause."""
        if not self.is_running and self._pause_time is not None:
            # Add the paused duration to our total
            pause_duration = datetime.now() - self._pause_time
            self._total_paused_duration += pause_duration
            self._pause_time = None
            self.is_running = True

    def get_duration(self) -> timedelta:
        """
        Get the total active duration (excluding paused time).

        Returns:
            timedelta of active session time
        """
        if self.start_time is None:
            return timedelta(0)

        if self.is_running:
            # Currently running - calculate up to now
            total = datetime.now() - self.start_time
        else:
            # Not running - calculate up to when we paused
            if self._pause_time is not None:
                total = self._pause_time - self.start_time
            else:
                # Never started properly
                return timedelta(0)

        # Subtract paused time
        return total - self._total_paused_duration

    def record_event(self, event: GameEvent, data: Optional[dict[str, Any]] = None):
        """
        Record a game event in the history.

        Args:
            event: The type of event that occurred
            data: Optional additional data about the event
        """
        self.events.append({
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "data": data or {},
        })

    def checkpoint(self, name: str):
        """
        Save a checkpoint of the current state.

        Args:
            name: Name for this checkpoint
        """
        # Deep copy the state so future changes don't affect the checkpoint
        self._checkpoints[name] = copy.deepcopy(self.state)

    def restore(self, name: str):
        """
        Restore from a saved checkpoint.

        Args:
            name: Name of the checkpoint to restore

        Raises:
            KeyError: If checkpoint doesn't exist
        """
        if name not in self._checkpoints:
            raise KeyError(f"Checkpoint '{name}' not found")

        # Deep copy to avoid aliasing issues
        self.state = copy.deepcopy(self._checkpoints[name])

    def to_json(self) -> str:
        """
        Serialize the session to JSON.

        Returns:
            JSON string representation of the session
        """
        # Convert events to JSON-serializable format
        serializable_events = []
        for event in self.events:
            serializable_event = event.copy()
            # Convert GameEvent enum to its value
            if isinstance(serializable_event.get("event"), GameEvent):
                serializable_event["event"] = serializable_event["event"].value
            serializable_events.append(serializable_event)

        data = {
            "player_id": self.player_id,
            "challenge_id": self.challenge_id,
            "is_running": self.is_running,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "total_paused_duration": self._total_paused_duration.total_seconds(),
            "state": {
                "current_challenge": self.state.current_challenge,
                "current_code": self.state.current_code,
                "cursor_position": list(self.state.cursor_position),
                "tests_passing": self.state.tests_passing,
                "tests_total": self.state.tests_total,
                "hints_used": self.state.hints_used,
                "start_time": self.state.start_time.isoformat(),
                "session_id": self.state.session_id,
            },
            "events": serializable_events,
        }
        return json.dumps(data, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "GameSession":
        """
        Deserialize a session from JSON.

        Args:
            json_str: JSON string representation

        Returns:
            Restored GameSession
        """
        data = json.loads(json_str)

        # Create new session
        session = cls(
            player_id=data["player_id"],
            challenge_id=data.get("challenge_id")
        )

        # Restore session control
        session.is_running = data["is_running"]
        if data.get("start_time"):
            session.start_time = datetime.fromisoformat(data["start_time"])
        session._total_paused_duration = timedelta(seconds=data.get("total_paused_duration", 0))

        # Restore state
        state_data = data["state"]
        session.state = GameState(
            current_challenge=state_data.get("current_challenge"),
            current_code=state_data["current_code"],
            cursor_position=tuple(state_data["cursor_position"]),
            tests_passing=state_data["tests_passing"],
            tests_total=state_data["tests_total"],
            hints_used=state_data["hints_used"],
            start_time=datetime.fromisoformat(state_data["start_time"]),
            session_id=state_data["session_id"],
        )

        # Restore events
        session.events = data.get("events", [])

        return session


# Self-teaching note:
#
# This file demonstrates:
# - Dataclasses with field(default_factory=...) (Level 5+: Classes)
# - Enums for typed constants (Level 2: Collections, advanced)
# - Type hints with Optional, Any, list, dict (Professional Python)
# - UUID generation for unique IDs (stdlib: uuid)
# - datetime and timedelta for time tracking (stdlib: datetime)
# - JSON serialization patterns (to_json/from_json)
# - Deep copying to avoid aliasing bugs (copy.deepcopy)
# - Properties and methods for encapsulation
# - Class methods (@classmethod) for factory patterns
#
# The learner will encounter this AFTER mastering classes and type hints,
# so they can understand how to manage complex state in a game.
#
# Key concepts demonstrated:
# 1. Mutable default gotcha - NEVER use [] or {} as defaults!
#    Use field(default_factory=list) instead.
# 2. Deep copy vs shallow copy - why we need deepcopy for checkpoints
# 3. ISO format for datetime serialization - the standard way
# 4. Factory pattern with @classmethod - clean deserialization
# 5. UUID for unique session IDs - guaranteed uniqueness
