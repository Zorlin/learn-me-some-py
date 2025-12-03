"""
Session Sync - Multiplayer State Synchronization

Manages synchronized state across multiple players in real-time sessions.

Supports multiple session modes:
- COOP: Collaborative solving (shared cursor, turns)
- PAIR: Pair programming (split screen, different parts)
- RACE: Competitive racing (same challenge, first to finish)
- TEACH: Teaching mode (teacher + students)
- SPECTATOR: Watch and learn (AI solves, human watches)
- SWARM: Multiple AIs with different approaches

Self-teaching note:
This file demonstrates:
- Enum for session modes (Level 4: enums)
- Real-time state synchronization patterns (Level 6: distributed systems)
- Event-driven architecture (Level 5: callbacks and events)
- Thread-safe data structures (Level 6: threading)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Callable
import time
import threading


class SessionMode(Enum):
    """Multiplayer session modes."""

    COOP = "coop"                # Shared cursor, take turns
    PAIR = "pair"                # Split screen, different parts
    RACE = "race"                # Same problem, race to finish
    TEACH = "teach"              # Teacher explains to students
    SPECTATOR = "spectator"      # Watch AI solve
    SWARM = "swarm"              # Multiple AIs, different approaches


@dataclass
class SessionState:
    """Complete state of a multiplayer session."""

    session_id: str
    mode: SessionMode
    challenge_id: str

    # Players
    player_ids: List[str] = field(default_factory=list)
    player_states: Dict[str, dict] = field(default_factory=dict)

    # Code state
    shared_code: str = ""        # For COOP mode
    cursor_line: int = 0
    cursor_col: int = 0
    current_turn: Optional[str] = None  # Whose turn is it?

    # Test status
    tests_passed: int = 0
    tests_total: int = 0

    # Session metadata
    started_at: float = field(default_factory=time.time)
    is_active: bool = True

    def get_active_player_count(self) -> int:
        """Count of active players."""
        return len([p for p in self.player_states.values() if p.get("is_active", True)])

    def is_complete(self) -> bool:
        """Check if session is complete."""
        if self.mode == SessionMode.RACE:
            # Race complete when any player finishes
            return any(p.get("is_complete", False) for p in self.player_states.values())
        elif self.mode == SessionMode.COOP:
            # Coop complete when challenge is solved
            return self.tests_passed == self.tests_total
        else:
            # Other modes defined by specific logic
            return not self.is_active


class SessionSync:
    """
    Synchronizes state across multiplayer session.

    Features:
    - Real-time state broadcasting
    - Event-driven updates
    - Thread-safe operations
    - Turn management (for COOP mode)
    - Conflict resolution
    """

    def __init__(self, session_id: str, mode: SessionMode, challenge_id: str):
        self.state = SessionState(
            session_id=session_id,
            mode=mode,
            challenge_id=challenge_id,
        )

        # Thread safety
        self._lock = threading.Lock()

        # Event listeners
        self._event_listeners: List[Callable] = []

    def add_player(self, player_id: str) -> None:
        """Add a player to the session."""
        with self._lock:
            if player_id not in self.state.player_ids:
                self.state.player_ids.append(player_id)
                self.state.player_states[player_id] = {
                    "is_active": True,
                    "is_complete": False,
                    "code": "",
                    "cursor": (0, 0),
                    "tests_passed": 0,
                }

                self._broadcast_event({
                    "type": "player_joined",
                    "player_id": player_id,
                    "timestamp": time.time(),
                })

    def remove_player(self, player_id: str) -> None:
        """Remove a player from the session."""
        with self._lock:
            if player_id in self.state.player_ids:
                self.state.player_ids.remove(player_id)
                self.state.player_states[player_id]["is_active"] = False

                self._broadcast_event({
                    "type": "player_left",
                    "player_id": player_id,
                    "timestamp": time.time(),
                })

    def update_code(self, player_id: str, code: str, cursor: tuple[int, int]) -> None:
        """Update code for a player."""
        with self._lock:
            if self.state.mode == SessionMode.COOP:
                # In COOP mode, code is shared
                if self.state.current_turn == player_id or not self.state.current_turn:
                    self.state.shared_code = code
                    self.state.cursor_line, self.state.cursor_col = cursor
                else:
                    # Not their turn, ignore update
                    return
            else:
                # Other modes: each player has own code
                if player_id in self.state.player_states:
                    self.state.player_states[player_id]["code"] = code
                    self.state.player_states[player_id]["cursor"] = cursor

            self._broadcast_event({
                "type": "code_update",
                "player_id": player_id,
                "code": code,
                "cursor": cursor,
                "timestamp": time.time(),
            })

    def update_tests(self, player_id: str, passed: int, total: int) -> None:
        """Update test results for a player."""
        with self._lock:
            if self.state.mode == SessionMode.COOP:
                # Shared test results
                self.state.tests_passed = passed
                self.state.tests_total = total
            else:
                # Per-player test results
                if player_id in self.state.player_states:
                    self.state.player_states[player_id]["tests_passed"] = passed
                    self.state.player_states[player_id]["tests_total"] = total

            # Check for completion
            if passed == total and total > 0:
                if player_id in self.state.player_states:
                    self.state.player_states[player_id]["is_complete"] = True

                self._broadcast_event({
                    "type": "player_complete",
                    "player_id": player_id,
                    "timestamp": time.time(),
                })

    def pass_turn(self, current_player: str) -> Optional[str]:
        """Pass turn to next player (COOP mode)."""
        if self.state.mode != SessionMode.COOP:
            return None

        with self._lock:
            active_players = [
                pid for pid in self.state.player_ids
                if self.state.player_states.get(pid, {}).get("is_active", False)
            ]

            if not active_players:
                return None

            try:
                current_idx = active_players.index(current_player)
                next_idx = (current_idx + 1) % len(active_players)
                next_player = active_players[next_idx]
            except ValueError:
                # Current player not in list, start with first
                next_player = active_players[0]

            self.state.current_turn = next_player

            self._broadcast_event({
                "type": "turn_change",
                "previous_player": current_player,
                "current_player": next_player,
                "timestamp": time.time(),
            })

            return next_player

    def get_state_snapshot(self) -> SessionState:
        """Get a snapshot of current state (thread-safe)."""
        with self._lock:
            # Return a copy to avoid race conditions
            import copy
            return copy.deepcopy(self.state)

    def subscribe(self, callback: Callable[[dict], None]) -> None:
        """Subscribe to session events."""
        self._event_listeners.append(callback)

    def unsubscribe(self, callback: Callable[[dict], None]) -> None:
        """Unsubscribe from session events."""
        if callback in self._event_listeners:
            self._event_listeners.remove(callback)

    def _broadcast_event(self, event: dict) -> None:
        """Broadcast event to all listeners."""
        event["session_id"] = self.state.session_id

        for listener in self._event_listeners:
            try:
                listener(event)
            except Exception as e:
                # Don't let listener errors crash the sync
                print(f"Error in event listener: {e}")

    def end_session(self) -> None:
        """Mark session as ended."""
        with self._lock:
            self.state.is_active = False

            self._broadcast_event({
                "type": "session_ended",
                "timestamp": time.time(),
            })


# Self-teaching note:
#
# This file demonstrates:
# - Enum for type-safe mode selection (Level 4)
# - Dataclasses for structured state (Level 5)
# - Threading and locks for concurrent access (Level 6)
# - Observer pattern for event broadcasting (Level 6)
# - Deep copying to prevent race conditions (Level 5: copy module)
#
# The learner will encounter this after mastering:
# - Level 4: Enums, comprehensions
# - Level 5: Classes, dataclasses, modules
# - Level 6: Threading, distributed systems
#
# This is professional Python for real-time multiplayer systems!
