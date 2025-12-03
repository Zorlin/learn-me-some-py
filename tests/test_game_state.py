"""
Tests for game state management module.

Following TDD: Write tests FIRST, then implement.
"""

import pytest
from datetime import datetime, timedelta
from lmsp.game.state import (
    GameState,
    GameSession,
    GameEvent,
)


class TestGameState:
    """Test the GameState dataclass."""

    def test_create_empty_game_state(self):
        """GameState can be created with minimal args."""
        state = GameState()
        assert state.current_challenge is None
        assert state.current_code == ""
        assert state.cursor_position == (0, 0)
        assert state.tests_passing == 0
        assert state.tests_total == 0
        assert state.hints_used == 0
        assert isinstance(state.start_time, datetime)
        assert isinstance(state.session_id, str)
        assert len(state.session_id) > 0

    def test_create_game_state_with_challenge(self):
        """GameState can track a specific challenge."""
        state = GameState(
            current_challenge="list_basics_001",
            current_code="def solution():\n    pass",
            cursor_position=(1, 8),
            tests_passing=2,
            tests_total=5,
            hints_used=1
        )
        assert state.current_challenge == "list_basics_001"
        assert state.current_code == "def solution():\n    pass"
        assert state.cursor_position == (1, 8)
        assert state.tests_passing == 2
        assert state.tests_total == 5
        assert state.hints_used == 1

    def test_game_state_session_id_is_unique(self):
        """Each GameState gets a unique session_id."""
        state1 = GameState()
        state2 = GameState()
        assert state1.session_id != state2.session_id


class TestGameSession:
    """Test the GameSession class."""

    def test_create_game_session(self):
        """GameSession can be created with player_id."""
        session = GameSession(player_id="test_player")
        assert session.player_id == "test_player"
        assert session.challenge_id is None
        assert session.state is not None

    def test_create_game_session_with_challenge(self):
        """GameSession can be created with a challenge."""
        session = GameSession(player_id="test_player", challenge_id="list_basics_001")
        assert session.player_id == "test_player"
        assert session.challenge_id == "list_basics_001"

    def test_start_session(self):
        """start() marks the session as started."""
        session = GameSession(player_id="test_player")
        session.start()
        assert session.is_running is True
        assert session.start_time is not None

    def test_pause_and_resume(self):
        """pause() and resume() control session state."""
        session = GameSession(player_id="test_player")
        session.start()
        assert session.is_running is True

        session.pause()
        assert session.is_running is False

        session.resume()
        assert session.is_running is True

    def test_get_duration_before_start(self):
        """get_duration() returns zero before start."""
        session = GameSession(player_id="test_player")
        duration = session.get_duration()
        assert duration == timedelta(0)

    def test_get_duration_after_start(self):
        """get_duration() returns time since start."""
        session = GameSession(player_id="test_player")
        session.start()
        # Small delay to ensure duration > 0
        import time
        time.sleep(0.01)
        duration = session.get_duration()
        assert duration > timedelta(0)

    def test_get_duration_excludes_paused_time(self):
        """get_duration() excludes paused time."""
        session = GameSession(player_id="test_player")
        session.start()
        import time
        time.sleep(0.01)
        session.pause()
        time.sleep(0.02)  # Paused longer
        session.resume()
        duration = session.get_duration()
        # Duration should be closer to 0.01 than 0.03
        assert duration.total_seconds() < 0.025

    def test_to_json_serialization(self):
        """to_json() produces valid JSON."""
        session = GameSession(player_id="test_player", challenge_id="test_001")
        session.start()
        session.state.current_code = "print('hello')"
        session.state.tests_passing = 3
        session.state.tests_total = 5

        json_str = session.to_json()
        assert isinstance(json_str, str)
        assert "test_player" in json_str
        assert "test_001" in json_str
        assert "hello" in json_str

    def test_from_json_deserialization(self):
        """from_json() restores a session."""
        session = GameSession(player_id="test_player", challenge_id="test_001")
        session.start()
        session.state.current_code = "x = 42"
        session.state.hints_used = 2

        json_str = session.to_json()
        restored = GameSession.from_json(json_str)

        assert restored.player_id == "test_player"
        assert restored.challenge_id == "test_001"
        assert restored.state.current_code == "x = 42"
        assert restored.state.hints_used == 2

    def test_checkpoint_saves_state(self):
        """checkpoint() saves current state."""
        session = GameSession(player_id="test_player")
        session.start()
        session.state.current_code = "before"

        session.checkpoint("save1")
        session.state.current_code = "after"

        # State has changed
        assert session.state.current_code == "after"
        # But we can verify checkpoint exists
        assert "save1" in session._checkpoints

    def test_restore_checkpoint(self):
        """restore() restores saved state."""
        session = GameSession(player_id="test_player")
        session.start()
        session.state.current_code = "original"
        session.state.tests_passing = 2

        session.checkpoint("save1")
        session.state.current_code = "modified"
        session.state.tests_passing = 3

        session.restore("save1")

        assert session.state.current_code == "original"
        assert session.state.tests_passing == 2

    def test_restore_nonexistent_checkpoint_raises(self):
        """restore() raises KeyError for nonexistent checkpoint."""
        session = GameSession(player_id="test_player")
        with pytest.raises(KeyError):
            session.restore("nonexistent")

    def test_record_event(self):
        """record_event() tracks game events."""
        session = GameSession(player_id="test_player")
        session.start()
        session.record_event(GameEvent.KEYSTROKE, data={"key": "a"})
        session.record_event(GameEvent.TEST_PASS)

        assert len(session.events) == 2
        assert session.events[0]["event"] == GameEvent.KEYSTROKE
        assert session.events[0]["data"] == {"key": "a"}
        assert session.events[1]["event"] == GameEvent.TEST_PASS


class TestGameEvent:
    """Test the GameEvent enum."""

    def test_game_event_values(self):
        """GameEvent has all required values."""
        assert GameEvent.KEYSTROKE
        assert GameEvent.CODE_CHANGE
        assert GameEvent.RUN_CODE
        assert GameEvent.TEST_PASS
        assert GameEvent.TEST_FAIL
        assert GameEvent.HINT_USED
        assert GameEvent.CHALLENGE_COMPLETE
        assert GameEvent.EMOTION_RECORDED

    def test_game_event_is_enum(self):
        """GameEvent values are distinct."""
        events = [
            GameEvent.KEYSTROKE,
            GameEvent.CODE_CHANGE,
            GameEvent.RUN_CODE,
            GameEvent.TEST_PASS,
            GameEvent.TEST_FAIL,
            GameEvent.HINT_USED,
            GameEvent.CHALLENGE_COMPLETE,
            GameEvent.EMOTION_RECORDED,
        ]
        assert len(events) == len(set(events))


class TestIntegration:
    """Integration tests for game state management."""

    def test_full_session_workflow(self):
        """Test a complete session workflow."""
        # Create and start session
        session = GameSession(player_id="alice", challenge_id="loops_001")
        session.start()

        # Record some activity
        session.record_event(GameEvent.CODE_CHANGE, data={"code": "for i in range(10):"})
        session.state.current_code = "for i in range(10):\n    print(i)"
        session.state.cursor_position = (1, 11)

        # Run tests
        session.record_event(GameEvent.RUN_CODE)
        session.state.tests_passing = 8
        session.state.tests_total = 10

        # Use a hint
        session.record_event(GameEvent.HINT_USED)
        session.state.hints_used = 1

        # Save checkpoint
        session.checkpoint("before_final")

        # Complete challenge
        session.state.tests_passing = 10
        session.record_event(GameEvent.TEST_PASS)
        session.record_event(GameEvent.CHALLENGE_COMPLETE)

        # Verify state
        assert session.state.tests_passing == 10
        assert session.state.tests_total == 10
        assert session.state.hints_used == 1
        assert len(session.events) >= 5

        # Serialize and restore
        json_str = session.to_json()
        restored = GameSession.from_json(json_str)

        assert restored.player_id == "alice"
        assert restored.challenge_id == "loops_001"
        assert restored.state.tests_passing == 10
        assert restored.state.hints_used == 1

    def test_session_with_pause_and_checkpoint(self):
        """Test session with pause, checkpoint, and restore."""
        session = GameSession(player_id="bob", challenge_id="dict_001")
        session.start()

        # Make some progress
        session.state.current_code = "my_dict = {}"
        session.state.tests_passing = 1
        session.checkpoint("checkpoint1")

        # More progress
        session.state.current_code = "my_dict = {'key': 'value'}"
        session.state.tests_passing = 2

        # Pause
        session.pause()
        assert not session.is_running

        # Try to restore
        session.restore("checkpoint1")
        assert session.state.current_code == "my_dict = {}"
        assert session.state.tests_passing == 1

        # Resume
        session.resume()
        assert session.is_running


# Self-teaching note:
#
# This test file demonstrates:
# - pytest structure and organization (Level 6: Testing)
# - Test classes for grouping related tests
# - Fixtures would go here if needed (pytest feature)
# - Assertion patterns (assert conditions)
# - Testing edge cases and error conditions
# - Integration tests vs unit tests
#
# The learner will write tests like this BEFORE implementing features.
# This is Test-Driven Development (TDD).
