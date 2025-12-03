"""
Tests for Session Synchronization

TDD: These tests define expected behavior for multiplayer state sync.

Tests cover:
1. Session state initialization
2. Player add/remove
3. Code updates
4. Test result sync
5. Turn management (COOP mode)
6. Event broadcasting
7. Thread safety
"""

import pytest
from unittest.mock import Mock
import time

from lmsp.multiplayer.session_sync import (
    SessionMode,
    SessionState,
    SessionSync,
)


class TestSessionMode:
    """Test session mode enumeration."""

    def test_all_modes_defined(self):
        """All session modes should be defined."""
        assert SessionMode.COOP.value == "coop"
        assert SessionMode.PAIR.value == "pair"
        assert SessionMode.RACE.value == "race"
        assert SessionMode.TEACH.value == "teach"
        assert SessionMode.SPECTATOR.value == "spectator"
        assert SessionMode.SWARM.value == "swarm"


class TestSessionState:
    """Test session state dataclass."""

    def test_new_state_is_active(self):
        """New session should be active."""
        state = SessionState(
            session_id="test-session",
            mode=SessionMode.RACE,
            challenge_id="test-challenge",
        )

        assert state.is_active is True

    def test_get_active_player_count(self):
        """Should count active players."""
        state = SessionState(
            session_id="test",
            mode=SessionMode.RACE,
            challenge_id="test",
        )

        state.player_ids = ["player1", "player2", "player3"]
        state.player_states = {
            "player1": {"is_active": True},
            "player2": {"is_active": True},
            "player3": {"is_active": False},
        }

        assert state.get_active_player_count() == 2

    def test_is_complete_race_mode(self):
        """RACE mode completes when any player finishes."""
        state = SessionState(
            session_id="test",
            mode=SessionMode.RACE,
            challenge_id="test",
        )

        state.player_states = {
            "player1": {"is_complete": False},
            "player2": {"is_complete": True},
        }

        assert state.is_complete() is True

    def test_is_complete_coop_mode(self):
        """COOP mode completes when tests pass."""
        state = SessionState(
            session_id="test",
            mode=SessionMode.COOP,
            challenge_id="test",
        )

        state.tests_passed = 0
        state.tests_total = 5

        assert state.is_complete() is False

        state.tests_passed = 5
        assert state.is_complete() is True


class TestSessionSync:
    """Test session synchronization."""

    @pytest.fixture
    def sync(self):
        """Create a test session sync."""
        return SessionSync(
            session_id="test-session",
            mode=SessionMode.RACE,
            challenge_id="test-challenge",
        )

    def test_initialization(self, sync):
        """Should initialize with correct parameters."""
        assert sync.state.session_id == "test-session"
        assert sync.state.mode == SessionMode.RACE
        assert sync.state.challenge_id == "test-challenge"
        assert sync.state.is_active is True

    def test_add_player(self, sync):
        """Should add a player to the session."""
        sync.add_player("player1")

        assert "player1" in sync.state.player_ids
        assert "player1" in sync.state.player_states
        assert sync.state.player_states["player1"]["is_active"] is True

    def test_add_duplicate_player(self, sync):
        """Should not duplicate players."""
        sync.add_player("player1")
        sync.add_player("player1")

        assert sync.state.player_ids.count("player1") == 1

    def test_remove_player(self, sync):
        """Should remove a player from the session."""
        sync.add_player("player1")
        sync.remove_player("player1")

        assert "player1" not in sync.state.player_ids
        assert sync.state.player_states["player1"]["is_active"] is False

    def test_update_code_race_mode(self, sync):
        """In RACE mode, each player has their own code."""
        sync.add_player("player1")

        code = "def hello():\n    print('Hello')\n"
        cursor = (1, 4)

        sync.update_code("player1", code, cursor)

        assert sync.state.player_states["player1"]["code"] == code
        assert sync.state.player_states["player1"]["cursor"] == cursor

    def test_update_code_coop_mode(self):
        """In COOP mode, code is shared."""
        sync = SessionSync(
            session_id="test",
            mode=SessionMode.COOP,
            challenge_id="test",
        )

        sync.add_player("player1")
        sync.state.current_turn = "player1"

        code = "shared code"
        cursor = (0, 0)

        sync.update_code("player1", code, cursor)

        assert sync.state.shared_code == code
        assert sync.state.cursor_line == cursor[0]
        assert sync.state.cursor_col == cursor[1]

    def test_update_code_coop_not_your_turn(self):
        """In COOP mode, cannot edit if not your turn."""
        sync = SessionSync(
            session_id="test",
            mode=SessionMode.COOP,
            challenge_id="test",
        )

        sync.add_player("player1")
        sync.add_player("player2")
        sync.state.current_turn = "player1"
        sync.state.shared_code = "original"

        # Player 2 tries to edit (not their turn)
        sync.update_code("player2", "modified", (0, 0))

        # Code should not change
        assert sync.state.shared_code == "original"

    def test_update_tests(self, sync):
        """Should update test results."""
        sync.add_player("player1")

        sync.update_tests("player1", passed=3, total=5)

        assert sync.state.player_states["player1"]["tests_passed"] == 3
        assert sync.state.player_states["player1"]["tests_total"] == 5

    def test_update_tests_completion(self, sync):
        """Should mark player complete when all tests pass."""
        sync.add_player("player1")

        sync.update_tests("player1", passed=5, total=5)

        assert sync.state.player_states["player1"]["is_complete"] is True

    def test_pass_turn_coop(self):
        """Should pass turn to next player in COOP mode."""
        sync = SessionSync(
            session_id="test",
            mode=SessionMode.COOP,
            challenge_id="test",
        )

        sync.add_player("player1")
        sync.add_player("player2")
        sync.add_player("player3")

        # Start with player1
        sync.state.current_turn = "player1"

        # Pass turn
        next_player = sync.pass_turn("player1")

        assert next_player == "player2"
        assert sync.state.current_turn == "player2"

        # Pass again
        next_player = sync.pass_turn("player2")
        assert next_player == "player3"

        # Wraps around
        next_player = sync.pass_turn("player3")
        assert next_player == "player1"

    def test_pass_turn_non_coop(self, sync):
        """Should not pass turn in non-COOP modes."""
        result = sync.pass_turn("player1")

        assert result is None

    def test_get_state_snapshot(self, sync):
        """Should return a copy of state."""
        sync.add_player("player1")

        snapshot1 = sync.get_state_snapshot()
        snapshot2 = sync.get_state_snapshot()

        # Should be equal but not same object
        assert snapshot1.session_id == snapshot2.session_id
        assert snapshot1 is not snapshot2

    def test_event_subscription(self, sync):
        """Should allow subscribing to events."""
        received_events = []

        def listener(event):
            received_events.append(event)

        sync.subscribe(listener)
        sync.add_player("player1")

        # Should have received player_joined event
        assert len(received_events) > 0
        assert received_events[0]["type"] == "player_joined"

    def test_event_unsubscription(self, sync):
        """Should allow unsubscribing from events."""
        received_events = []

        def listener(event):
            received_events.append(event)

        sync.subscribe(listener)
        sync.unsubscribe(listener)

        sync.add_player("player1")

        # Should not have received events
        assert len(received_events) == 0

    def test_end_session(self, sync):
        """Should mark session as ended."""
        sync.end_session()

        assert sync.state.is_active is False


class TestThreadSafety:
    """Test thread-safe operations."""

    @pytest.fixture
    def sync(self):
        return SessionSync(
            session_id="test",
            mode=SessionMode.RACE,
            challenge_id="test",
        )

    def test_concurrent_player_adds(self, sync):
        """Should handle concurrent player additions safely."""
        import threading

        def add_players():
            for i in range(10):
                sync.add_player(f"player{i}")

        threads = [threading.Thread(target=add_players) for _ in range(3)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should have exactly 10 players (no duplicates despite concurrency)
        assert len(sync.state.player_ids) == 10

    def test_concurrent_code_updates(self, sync):
        """Should handle concurrent code updates safely."""
        import threading

        sync.add_player("player1")

        update_count = [0]

        def update_code():
            for _ in range(10):
                sync.update_code("player1", f"code{update_count[0]}", (0, 0))
                update_count[0] += 1
                time.sleep(0.001)

        threads = [threading.Thread(target=update_code) for _ in range(2)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should not crash - final code should be one of the updates
        assert sync.state.player_states["player1"]["code"].startswith("code")


class TestEventBroadcasting:
    """Test event broadcasting system."""

    @pytest.fixture
    def sync(self):
        return SessionSync(
            session_id="test",
            mode=SessionMode.RACE,
            challenge_id="test",
        )

    def test_broadcast_player_joined(self, sync):
        """Should broadcast player_joined event."""
        events = []
        sync.subscribe(lambda e: events.append(e))

        sync.add_player("player1")

        assert any(e["type"] == "player_joined" and e["player_id"] == "player1" for e in events)

    def test_broadcast_player_left(self, sync):
        """Should broadcast player_left event."""
        events = []
        sync.subscribe(lambda e: events.append(e))

        sync.add_player("player1")
        sync.remove_player("player1")

        assert any(e["type"] == "player_left" and e["player_id"] == "player1" for e in events)

    def test_broadcast_code_update(self, sync):
        """Should broadcast code_update event."""
        events = []
        sync.subscribe(lambda e: events.append(e))

        sync.add_player("player1")
        sync.update_code("player1", "test code", (0, 0))

        assert any(e["type"] == "code_update" and e["player_id"] == "player1" for e in events)

    def test_broadcast_player_complete(self, sync):
        """Should broadcast player_complete event."""
        events = []
        sync.subscribe(lambda e: events.append(e))

        sync.add_player("player1")
        sync.update_tests("player1", passed=5, total=5)

        assert any(e["type"] == "player_complete" and e["player_id"] == "player1" for e in events)

    def test_broadcast_turn_change(self):
        """Should broadcast turn_change event in COOP mode."""
        sync = SessionSync(
            session_id="test",
            mode=SessionMode.COOP,
            challenge_id="test",
        )

        events = []
        sync.subscribe(lambda e: events.append(e))

        sync.add_player("player1")
        sync.add_player("player2")
        sync.state.current_turn = "player1"

        sync.pass_turn("player1")

        assert any(
            e["type"] == "turn_change"
            and e["previous_player"] == "player1"
            and e["current_player"] == "player2"
            for e in events
        )

    def test_broadcast_session_ended(self, sync):
        """Should broadcast session_ended event."""
        events = []
        sync.subscribe(lambda e: events.append(e))

        sync.end_session()

        assert any(e["type"] == "session_ended" for e in events)

    def test_event_includes_session_id(self, sync):
        """All events should include session_id."""
        events = []
        sync.subscribe(lambda e: events.append(e))

        sync.add_player("player1")

        for event in events:
            assert event["session_id"] == "test-session"

    def test_listener_error_does_not_crash(self, sync):
        """Listener errors should not crash the sync."""
        def bad_listener(event):
            raise Exception("Listener error")

        sync.subscribe(bad_listener)

        # Should not crash
        sync.add_player("player1")

        # Session should still work
        assert "player1" in sync.state.player_ids


# Self-teaching note:
#
# This test file demonstrates:
# - Testing thread-safe operations
# - Testing event-driven systems
# - Testing observer pattern
# - pytest fixtures for test setup
# - Mocking and callbacks
#
# Prerequisites:
# - Level 3: Functions, classes
# - Level 4: Dictionaries, lists
# - Level 5: Threading basics
# - Level 6: Distributed systems patterns
