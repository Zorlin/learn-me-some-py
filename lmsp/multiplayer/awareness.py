"""
Awareness Tracker - Multi-player State Awareness

Tracks the state of all players in a session to enable:
- Player-aware suggestions
- Turn-based coordination
- Emotional resonance
- Collaborative problem-solving

Self-teaching note:
This file demonstrates:
- Dataclasses for structured data (Level 5: @dataclass)
- Type hints for complex types (Level 5: typing.Dict, List, Optional)
- Dictionary management (Level 2: dict operations)
- Time-based tracking (Level 6: time module)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
import time


class EmotionDimension(Enum):
    """Emotional dimensions tracked via analog input."""

    ENJOYMENT = "enjoyment"         # RT trigger
    FRUSTRATION = "frustration"     # LT trigger
    ENGAGEMENT = "engagement"       # Speed of response
    FLOW = "flow"                   # Combined pattern


@dataclass
class PlayerState:
    """Current state of a single player."""

    name: str
    progress: float = 0.0                    # 0.0 to 1.0 challenge completion
    emotion: Dict[str, float] = field(default_factory=dict)  # Dimension -> value
    last_activity: str = ""                  # Description of last action
    last_activity_time: float = field(default_factory=time.time)

    # Code state
    code_buffer: str = ""
    cursor_position: tuple[int, int] = (0, 0)

    # Thoughts and communication
    recent_thoughts: List[str] = field(default_factory=list)
    recent_suggestions: List[str] = field(default_factory=list)

    # Challenge status
    tests_passed: int = 0
    tests_total: int = 0
    is_complete: bool = False

    # Turn tracking (for coop mode)
    has_turn: bool = False

    def idle_time(self) -> float:
        """How long since last activity."""
        return time.time() - self.last_activity_time

    def appears_stuck(self, threshold: float = 15.0) -> bool:
        """Returns True if player has been idle too long."""
        return self.idle_time() > threshold and not self.is_complete

    def is_frustrated(self, threshold: float = 0.7) -> bool:
        """Returns True if player frustration is high."""
        return self.emotion.get("frustration", 0.0) > threshold

    def is_in_flow(self) -> bool:
        """Returns True if player is in flow state."""
        engagement = self.emotion.get("engagement", 0.0)
        enjoyment = self.emotion.get("enjoyment", 0.0)
        frustration = self.emotion.get("frustration", 0.0)

        # Flow: high engagement + enjoyment, low frustration
        return engagement > 0.7 and enjoyment > 0.6 and frustration < 0.3


class AwarenessTracker:
    """
    Tracks all players in a session.

    Maintains real-time awareness of:
    - Who's doing what
    - Who's stuck
    - Who's frustrated
    - Who's in flow
    - Turn order
    - Test status
    """

    def __init__(self):
        self.players: Dict[str, PlayerState] = {}
        self.current_turn: Optional[str] = None
        self.session_start: float = time.time()
        self.test_results: Optional[Dict] = None

    def register_player(self, name: str) -> PlayerState:
        """Add a new player to tracking."""
        state = PlayerState(name=name)
        self.players[name] = state
        return state

    def update(self, event: dict):
        """
        Process an event and update player state.

        Events come from the stream-JSON protocol.
        """
        player_name = event.get("player")
        if not player_name:
            return

        # Ensure player exists
        if player_name not in self.players:
            self.register_player(player_name)

        player = self.players[player_name]
        player.last_activity_time = time.time()

        event_type = event.get("type")

        if event_type == "keystroke":
            player.last_activity = f"Typed '{event.get('char', '')}'"
            # Update code buffer and cursor
            self._update_code_buffer(player, event)

        elif event_type == "code_update":
            player.code_buffer = event.get("code", "")
            player.cursor_position = event.get("cursor", (0, 0))
            player.last_activity = "Updated code"

        elif event_type == "thought":
            thought = event.get("content", "")
            player.recent_thoughts.append(thought)
            if len(player.recent_thoughts) > 10:
                player.recent_thoughts = player.recent_thoughts[-10:]
            player.last_activity = f"Thinking: {thought[:50]}..."

        elif event_type == "suggestion":
            suggestion = event.get("content", "")
            player.recent_suggestions.append(suggestion)
            if len(player.recent_suggestions) > 5:
                player.recent_suggestions = player.recent_suggestions[-5:]
            player.last_activity = f"Suggested: {suggestion[:50]}..."

        elif event_type == "emotion":
            dimension = event.get("dimension")
            value = event.get("value", 0.0)
            player.emotion[dimension] = value
            player.last_activity = f"Feeling {dimension}: {value:.2f}"

        elif event_type == "test_result":
            player.tests_passed = event.get("passed", 0)
            player.tests_total = event.get("total", 0)
            player.progress = player.tests_passed / max(player.tests_total, 1)
            player.last_activity = f"Tests: {player.tests_passed}/{player.tests_total}"

        elif event_type == "player_complete":
            player.is_complete = True
            player.last_activity = "Challenge complete!"

        elif event_type == "turn_start":
            player.has_turn = True
            self.current_turn = player_name
            player.last_activity = "Turn started"

        elif event_type == "turn_end":
            player.has_turn = False
            player.last_activity = "Turn ended"

    def _update_code_buffer(self, player: PlayerState, event: dict):
        """Update code buffer based on keystroke event."""
        char = event.get("char", "")
        line, col = player.cursor_position

        lines = player.code_buffer.split('\n')

        # Ensure we have enough lines
        while len(lines) <= line:
            lines.append("")

        # Insert character at cursor
        current_line = lines[line]
        if char == '\n':
            # Split line at cursor
            lines = lines[:line] + [
                current_line[:col],
                current_line[col:]
            ] + lines[line+1:]
            player.cursor_position = (line + 1, 0)
        elif char == '\b':  # Backspace
            if col > 0:
                lines[line] = current_line[:col-1] + current_line[col:]
                player.cursor_position = (line, col - 1)
        else:
            lines[line] = current_line[:col] + char + current_line[col:]
            player.cursor_position = (line, col + 1)

        player.code_buffer = '\n'.join(lines)

    def get_player_state(self, name: str) -> Optional[PlayerState]:
        """Get state for a specific player."""
        return self.players.get(name)

    def get_player_names(self) -> List[str]:
        """Get list of all player names."""
        return list(self.players.keys())

    def is_my_turn(self, player_name: str) -> bool:
        """Check if it's a specific player's turn."""
        return self.current_turn == player_name

    def am_i_complete(self, player_name: str) -> bool:
        """Check if a specific player is complete."""
        player = self.players.get(player_name)
        return player.is_complete if player else False

    def needs_teaching_input(self) -> bool:
        """Check if any student needs teaching input."""
        for player in self.players.values():
            if player.appears_stuck() or player.is_frustrated():
                return True
        return False

    def other_player_idle_time(self, exclude_player: str) -> float:
        """Get max idle time of other players."""
        max_idle = 0.0
        for name, player in self.players.items():
            if name != exclude_player:
                max_idle = max(max_idle, player.idle_time())
        return max_idle

    def get_frustrated_players(self, threshold: float = 0.7) -> List[str]:
        """Get list of players who are frustrated."""
        return [
            name for name, player in self.players.items()
            if player.is_frustrated(threshold)
        ]

    def get_stuck_players(self, threshold: float = 15.0) -> List[str]:
        """Get list of players who appear stuck."""
        return [
            name for name, player in self.players.items()
            if player.appears_stuck(threshold)
        ]

    def get_flow_players(self) -> List[str]:
        """Get list of players in flow state."""
        return [
            name for name, player in self.players.items()
            if player.is_in_flow()
        ]

    def session_duration(self) -> float:
        """Get session duration in seconds."""
        return time.time() - self.session_start

    def get_leaderboard(self) -> List[tuple[str, float]]:
        """
        Get players sorted by progress.

        Returns list of (name, progress) tuples, highest first.
        """
        return sorted(
            [(name, player.progress) for name, player in self.players.items()],
            key=lambda x: x[1],
            reverse=True
        )


# Self-teaching note:
#
# This file demonstrates:
# - Dataclasses (@dataclass) - Clean way to create classes that mainly hold data
# - Type hints - Making code self-documenting and enabling IDE autocomplete
# - Enum - Type-safe constants
# - Dictionary management - Tracking multiple entities by name
# - Time tracking - Using time.time() for duration calculations
# - List slicing - Keeping recent history with [-10:]
# - Default factories - Using field(default_factory=list) for mutable defaults
#
# The learner will encounter this AFTER mastering:
# - Level 2: Collections (lists, dicts)
# - Level 3: Functions and classes
# - Level 5: Dataclasses and type hints
