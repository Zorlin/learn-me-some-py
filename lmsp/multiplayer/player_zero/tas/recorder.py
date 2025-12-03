"""
TAS Recorder for Playtest Replay

Enhanced TAS recording system specifically designed for player-zero integration
and playtest analysis. Records every action during playtests to enable replay
and UX breakdown analysis.

This module provides:
- PlaytestRecorder: Main recording interface for AI playtest sessions
- PlaytestEvent: Event data structure with serialization
- Struggle detection: Identifies where players struggle
- UX issue identification: Finds potential UX problems
- Compact JSON storage: Efficient serialization for analysis

Self-teaching note:
This file demonstrates:
- Dataclasses for structured data (Level 5: dataclasses)
- Enum for type-safe constants (Level 5: enums)
- JSON serialization (Level 4-5: file I/O)
- State machine patterns (Level 5-6: complex state management)
- Time tracking and duration calculation (Level 4: datetime)
- Analysis algorithms (Level 6: complex algorithms)
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class EventType(Enum):
    """Types of events that can be recorded during playtest."""
    CODE_CHANGE = "code_change"
    TEST_RUN = "test_run"
    TEST_FAIL = "test_fail"
    HINT_USED = "hint_used"
    CHECKPOINT_CREATE = "checkpoint_create"
    CHECKPOINT_RESTORE = "checkpoint_restore"
    NAVIGATION = "navigation"
    PAUSE = "pause"
    RESUME = "resume"


class StruggleIndicator(Enum):
    """Types of struggle indicators detected during playtest."""
    RAPID_CHANGES = "rapid_changes"
    REPEATED_FAILURES = "repeated_failures"
    HINT_USAGE = "hint_usage"
    LONG_PAUSE = "long_pause"
    BACKTRACKING = "backtracking"


@dataclass
class PlaytestEvent:
    """
    A single event recorded during a playtest session.

    Attributes:
        event_type: Type of event (CODE_CHANGE, TEST_RUN, etc.)
        timestamp: When the event occurred
        frame_number: Sequential frame number for ordering
        code: Code content at this event (if applicable)
        cursor_position: (line, col) cursor position (if applicable)
        data: Additional event-specific data
        duration_ms: Time since previous event in milliseconds
    """
    event_type: EventType
    timestamp: datetime
    frame_number: int
    code: Optional[str] = None
    cursor_position: Optional[Tuple[int, int]] = None
    data: Optional[Dict[str, Any]] = None
    duration_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Serialize event to dictionary for JSON storage."""
        return {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "frame_number": self.frame_number,
            "code": self.code,
            "cursor_position": self.cursor_position,
            "data": self.data,
            "duration_ms": self.duration_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlaytestEvent":
        """Deserialize event from dictionary."""
        return cls(
            event_type=EventType(data["event_type"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            frame_number=data["frame_number"],
            code=data.get("code"),
            cursor_position=tuple(data["cursor_position"]) if data.get("cursor_position") else None,
            data=data.get("data"),
            duration_ms=data.get("duration_ms", 0.0),
        )


@dataclass
class StruggleEvent:
    """A detected struggle indicator during playtest."""
    indicator_type: StruggleIndicator
    timestamp: datetime
    frame_number: int
    description: str
    related_events: List[int] = field(default_factory=list)


@dataclass
class PlaytestSession:
    """
    Complete playtest session data.

    Attributes:
        session_name: Human-readable session name
        player_name: Name of the player (human or AI)
        challenge_id: ID of the challenge being attempted
        start_time: When recording started
        end_time: When recording stopped
        events: List of all recorded events
        struggles: Detected struggle indicators
        metadata: Additional session metadata
    """
    session_name: str
    player_name: str
    challenge_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    events: List[PlaytestEvent] = field(default_factory=list)
    struggles: List[StruggleEvent] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class PlaytestRecorder:
    """
    Records playtest sessions for replay and analysis.

    This recorder captures every action during a playtest, enabling:
    - Frame-by-frame replay of AI sessions
    - Identification of UX breakdown points
    - Struggle detection and analysis
    - Compact JSON export for debugging

    Example:
        recorder = PlaytestRecorder("session1", "claude", "hello_world")
        recorder.start_recording()
        recorder.record_event(EventType.CODE_CHANGE, code="print('hello')")
        recorder.record_event(EventType.TEST_RUN, data={"result": "pass"})
        recorder.stop_recording()
        recorder.save_to_json("session1.json")
    """

    def __init__(
        self,
        session_name: str,
        player_name: str,
        challenge_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new playtest recorder.

        Args:
            session_name: Human-readable name for this session
            player_name: Name of the player (human or AI)
            challenge_id: ID of the challenge being attempted
            metadata: Optional additional metadata
        """
        self.session_name = session_name
        self.player_name = player_name
        self.challenge_id = challenge_id
        self.events: List[PlaytestEvent] = []
        self.is_recording = False
        self._start_time: Optional[datetime] = None
        self._end_time: Optional[datetime] = None
        self._last_event_time: Optional[datetime] = None
        self._frame_counter = 0
        self.metadata = metadata or {}

    def start_recording(self) -> None:
        """Start recording events."""
        self.is_recording = True
        self._start_time = datetime.now()
        self._last_event_time = self._start_time
        self._frame_counter = 0

    def stop_recording(self) -> None:
        """Stop recording events."""
        self.is_recording = False
        self._end_time = datetime.now()

    def record_event(
        self,
        event_type: EventType,
        code: Optional[str] = None,
        cursor_position: Optional[Tuple[int, int]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record a single event.

        Args:
            event_type: Type of event to record
            code: Code content at this event (if applicable)
            cursor_position: (line, col) cursor position (if applicable)
            data: Additional event-specific data
        """
        if not self.is_recording:
            return

        now = datetime.now()
        duration_ms = 0.0

        if self._last_event_time:
            delta = now - self._last_event_time
            duration_ms = delta.total_seconds() * 1000.0

        event = PlaytestEvent(
            event_type=event_type,
            timestamp=now,
            frame_number=self._frame_counter,
            code=code,
            cursor_position=cursor_position,
            data=data,
            duration_ms=duration_ms,
        )

        self.events.append(event)
        self._last_event_time = now
        self._frame_counter += 1

    def analyze_struggles(self) -> List[StruggleEvent]:
        """
        Analyze recorded events to detect struggle indicators.

        Returns:
            List of detected struggle events
        """
        struggles = []

        # Detect rapid changes (5+ changes in same area quickly)
        code_changes = [e for e in self.events if e.event_type == EventType.CODE_CHANGE]
        for i in range(len(code_changes) - 4):
            window = code_changes[i:i+5]
            if all(e.cursor_position and e.cursor_position[0] == window[0].cursor_position[0]
                   for e in window if e.cursor_position and window[0].cursor_position):
                struggles.append(StruggleEvent(
                    indicator_type=StruggleIndicator.RAPID_CHANGES,
                    timestamp=window[0].timestamp,
                    frame_number=window[0].frame_number,
                    description=f"5 rapid changes at line {window[0].cursor_position[0] if window[0].cursor_position else 'unknown'}",
                    related_events=[e.frame_number for e in window]
                ))

        # Detect hint usage
        hint_events = [e for e in self.events if e.event_type == EventType.HINT_USED]
        for hint_event in hint_events:
            struggles.append(StruggleEvent(
                indicator_type=StruggleIndicator.HINT_USAGE,
                timestamp=hint_event.timestamp,
                frame_number=hint_event.frame_number,
                description=f"Hint used: {hint_event.data.get('hint_id', 'unknown') if hint_event.data else 'unknown'}",
                related_events=[hint_event.frame_number]
            ))

        # Detect repeated test failures
        test_fails = [e for e in self.events if e.event_type == EventType.TEST_FAIL]
        if len(test_fails) >= 3:
            struggles.append(StruggleEvent(
                indicator_type=StruggleIndicator.REPEATED_FAILURES,
                timestamp=test_fails[0].timestamp,
                frame_number=test_fails[0].frame_number,
                description=f"{len(test_fails)} test failures",
                related_events=[e.frame_number for e in test_fails]
            ))

        return struggles

    def identify_ux_issues(self) -> List[Dict[str, Any]]:
        """
        Identify potential UX issues from recorded session.

        Returns:
            List of identified UX issues with descriptions
        """
        issues = []

        # High test failure rate
        test_runs = [e for e in self.events if e.event_type == EventType.TEST_RUN]
        test_fails = [e for e in self.events if e.event_type == EventType.TEST_FAIL]
        if test_runs and len(test_fails) / len(test_runs) > 0.5:
            issues.append({
                "type": "high_failure_rate",
                "severity": "high",
                "description": f"High test failure rate: {len(test_fails)}/{len(test_runs)} tests failed",
                "frames": [e.frame_number for e in test_fails]
            })

        # Back and forth pattern (confusion)
        code_changes = [e for e in self.events if e.event_type == EventType.CODE_CHANGE]
        if len(code_changes) >= 4:
            # Simple heuristic: alternating between different approaches
            patterns = set()
            for i in range(len(code_changes) - 1):
                if code_changes[i].code and code_changes[i+1].code:
                    patterns.add((code_changes[i].code[:20], code_changes[i+1].code[:20]))

            if len(patterns) >= 3:
                issues.append({
                    "type": "confusion_pattern",
                    "severity": "medium",
                    "description": "Player appears to be trying multiple different approaches",
                    "frames": [e.frame_number for e in code_changes]
                })

        return issues

    def generate_report(self) -> str:
        """
        Generate human-readable playback report.

        Returns:
            Formatted report string
        """
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append(f"Playtest Session Report: {self.session_name}")
        report_lines.append("=" * 60)
        report_lines.append(f"Player: {self.player_name}")
        report_lines.append(f"Challenge: {self.challenge_id}")
        report_lines.append(f"Events: {len(self.events)}")

        if self._start_time and self._end_time:
            duration = self._end_time - self._start_time
            report_lines.append(f"Duration: {duration.total_seconds():.2f}s")

        report_lines.append("")
        report_lines.append("Event Summary:")
        event_counts = {}
        for event in self.events:
            event_type = event.event_type.value
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

        for event_type, count in sorted(event_counts.items()):
            report_lines.append(f"  {event_type}: {count}")

        struggles = self.analyze_struggles()
        if struggles:
            report_lines.append("")
            report_lines.append("Struggle Indicators:")
            for struggle in struggles:
                report_lines.append(f"  [{struggle.frame_number}] {struggle.indicator_type.value}: {struggle.description}")

        ux_issues = self.identify_ux_issues()
        if ux_issues:
            report_lines.append("")
            report_lines.append("UX Issues:")
            for issue in ux_issues:
                report_lines.append(f"  [{issue['severity']}] {issue['type']}: {issue['description']}")

        report_lines.append("=" * 60)
        return "\n".join(report_lines)

    def save_to_json(self, output_path: Path) -> None:
        """
        Save session to compact JSON file.

        Args:
            output_path: Path to save JSON file
        """
        session_data = {
            "session_name": self.session_name,
            "player_name": self.player_name,
            "challenge_id": self.challenge_id,
            "start_time": self._start_time.isoformat() if self._start_time else None,
            "end_time": self._end_time.isoformat() if self._end_time else None,
            "metadata": self.metadata,
            "events": [event.to_dict() for event in self.events],
        }

        with open(output_path, 'w') as f:
            json.dump(session_data, f, indent=2)

    @classmethod
    def load_from_json(cls, input_path: Path) -> "PlaytestRecorder":
        """
        Load session from JSON file.

        Args:
            input_path: Path to JSON file

        Returns:
            Loaded PlaytestRecorder instance
        """
        with open(input_path, 'r') as f:
            data = json.load(f)

        recorder = cls(
            session_name=data["session_name"],
            player_name=data["player_name"],
            challenge_id=data["challenge_id"],
            metadata=data.get("metadata", {})
        )

        recorder._start_time = datetime.fromisoformat(data["start_time"]) if data.get("start_time") else None
        recorder._end_time = datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None
        recorder.events = [PlaytestEvent.from_dict(e) for e in data["events"]]
        recorder._frame_counter = len(recorder.events)

        return recorder


# Self-teaching note:
#
# This file demonstrates:
# - Dataclasses for clean data structures (Level 5: dataclasses)
# - Enum for type-safe constants (Level 5: enums)
# - JSON serialization with custom to_dict/from_dict (Level 4-5: file I/O)
# - State machine pattern (is_recording, start/stop) (Level 5-6: state management)
# - Time duration calculation with datetime (Level 4: datetime)
# - Analysis algorithms (struggle detection) (Level 6: algorithms)
# - Optional types for flexibility (Level 5: type hints)
# - Class methods for alternative constructors (Level 5: advanced OOP)
#
# This recorder is used by player-zero to capture AI playtest sessions
# for replay and UX analysis. Every action is recorded as an event with
# timing information, enabling frame-by-frame debugging of where players
# struggle or where the UX breaks down.
#
# Prerequisites:
# - Level 4: File I/O, JSON, datetime, collections
# - Level 5: Dataclasses, enums, type hints, advanced OOP
# - Level 6: State machines, analysis algorithms
