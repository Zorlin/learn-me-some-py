"""
Tests for LMSP Database
=======================

Tests for SQLite persistence layer.
"""

import pytest
import tempfile
from pathlib import Path

from lmsp.web.database import LMSPDatabase


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_lmsp.db"
        db = LMSPDatabase(db_path)
        yield db


class TestPlayerManagement:
    """Tests for player creation and management."""

    def test_create_player(self, temp_db):
        """Test creating a new player."""
        player = temp_db.get_or_create_player("test_player")
        assert player.player_id == "test_player"
        assert player.total_xp == 0

    def test_get_existing_player(self, temp_db):
        """Test retrieving an existing player."""
        temp_db.get_or_create_player("existing_player")
        player = temp_db.get_or_create_player("existing_player")
        assert player.player_id == "existing_player"

    def test_add_xp(self, temp_db):
        """Test adding XP to a player."""
        temp_db.get_or_create_player("xp_player")
        new_xp = temp_db.add_player_xp("xp_player", 100)
        assert new_xp == 100

        new_xp = temp_db.add_player_xp("xp_player", 50)
        assert new_xp == 150

    def test_get_player_xp(self, temp_db):
        """Test getting player XP."""
        temp_db.get_or_create_player("xp_test")
        temp_db.add_player_xp("xp_test", 200)
        xp = temp_db.get_player_xp("xp_test")
        assert xp == 200


class TestPasswordAuthentication:
    """Tests for password-based authentication."""

    def test_set_password(self, temp_db):
        """Test setting a password."""
        temp_db.get_or_create_player("password_user")
        result = temp_db.set_password("password_user", "secret123")
        assert result is True

    def test_verify_correct_password(self, temp_db):
        """Test verifying a correct password."""
        temp_db.get_or_create_player("verify_user")
        temp_db.set_password("verify_user", "mypassword")
        result = temp_db.verify_password("verify_user", "mypassword")
        assert result is True

    def test_verify_incorrect_password(self, temp_db):
        """Test verifying an incorrect password."""
        temp_db.get_or_create_player("wrong_pw_user")
        temp_db.set_password("wrong_pw_user", "correctpass")
        result = temp_db.verify_password("wrong_pw_user", "wrongpass")
        assert result is False

    def test_has_password(self, temp_db):
        """Test checking if player has a password."""
        temp_db.get_or_create_player("has_pw_user")
        assert temp_db.has_password("has_pw_user") is False

        temp_db.set_password("has_pw_user", "password")
        assert temp_db.has_password("has_pw_user") is True

    def test_remove_password(self, temp_db):
        """Test removing a password."""
        temp_db.get_or_create_player("remove_pw_user")
        temp_db.set_password("remove_pw_user", "password")
        assert temp_db.has_password("remove_pw_user") is True

        temp_db.remove_password("remove_pw_user")
        assert temp_db.has_password("remove_pw_user") is False


class TestGamepadCombo:
    """Tests for gamepad combo unlock."""

    def test_set_gamepad_combo(self, temp_db):
        """Test setting a gamepad combo."""
        temp_db.get_or_create_player("combo_user")
        result = temp_db.set_gamepad_combo(
            "combo_user",
            ["A", "B", "A", "A", "L3+R3"]
        )
        assert result is True

    def test_get_gamepad_combo(self, temp_db):
        """Test getting a gamepad combo."""
        temp_db.get_or_create_player("get_combo_user")
        temp_db.set_gamepad_combo("get_combo_user", ["X", "Y", "L3+R3"])
        combo = temp_db.get_gamepad_combo("get_combo_user")
        assert combo == ["X", "Y", "L3+R3"]

    def test_verify_correct_combo(self, temp_db):
        """Test verifying a correct combo."""
        temp_db.get_or_create_player("verify_combo_user")
        temp_db.set_gamepad_combo("verify_combo_user", ["A", "B", "A"])
        result = temp_db.verify_gamepad_combo("verify_combo_user", ["A", "B", "A"])
        assert result is True

    def test_verify_incorrect_combo(self, temp_db):
        """Test verifying an incorrect combo."""
        temp_db.get_or_create_player("wrong_combo_user")
        temp_db.set_gamepad_combo("wrong_combo_user", ["A", "B", "A"])
        result = temp_db.verify_gamepad_combo("wrong_combo_user", ["A", "A", "A"])
        assert result is False

    def test_no_combo_set(self, temp_db):
        """Test getting combo when none is set."""
        temp_db.get_or_create_player("no_combo_user")
        combo = temp_db.get_gamepad_combo("no_combo_user")
        assert combo is None


class TestCompletions:
    """Tests for challenge completion tracking."""

    def test_record_first_completion(self, temp_db):
        """Test recording a first completion."""
        temp_db.get_or_create_player("complete_user")
        completion = temp_db.record_completion("complete_user", "hello_world", 5.5)
        assert completion.challenge_id == "hello_world"
        assert completion.count == 1
        assert completion.times == [5.5]
        assert completion.best_time == 5.5

    def test_record_multiple_completions(self, temp_db):
        """Test recording multiple completions."""
        temp_db.get_or_create_player("multi_user")
        temp_db.record_completion("multi_user", "test_challenge", 10.0)
        temp_db.record_completion("multi_user", "test_challenge", 8.0)
        completion = temp_db.record_completion("multi_user", "test_challenge", 12.0)

        assert completion.count == 3
        assert len(completion.times) == 3
        assert completion.best_time == 8.0

    def test_get_completions(self, temp_db):
        """Test getting all completions for a player."""
        temp_db.get_or_create_player("get_complete_user")
        temp_db.record_completion("get_complete_user", "challenge1", 5.0)
        temp_db.record_completion("get_complete_user", "challenge2", 7.0)

        completions = temp_db.get_completions("get_complete_user")
        assert len(completions) == 2
        assert "challenge1" in completions
        assert "challenge2" in completions

    def test_get_completion_count(self, temp_db):
        """Test getting completion count for a specific challenge."""
        temp_db.get_or_create_player("count_user")
        temp_db.record_completion("count_user", "counted", 5.0)
        temp_db.record_completion("count_user", "counted", 6.0)

        count = temp_db.get_completion_count("count_user", "counted")
        assert count == 2


class TestMastery:
    """Tests for mastery level tracking."""

    def test_set_mastery_level(self, temp_db):
        """Test setting a mastery level."""
        temp_db.get_or_create_player("mastery_user")
        level = temp_db.set_mastery_level("mastery_user", "print_function", 2.0)
        assert level == 2.0

    def test_get_mastery_levels(self, temp_db):
        """Test getting all mastery levels."""
        temp_db.get_or_create_player("all_mastery_user")
        temp_db.set_mastery_level("all_mastery_user", "concept1", 1.0)
        temp_db.set_mastery_level("all_mastery_user", "concept2", 3.5)

        levels = temp_db.get_mastery_levels("all_mastery_user")
        assert levels["concept1"] == 1.0
        assert levels["concept2"] == 3.5

    def test_increment_mastery(self, temp_db):
        """Test incrementing mastery level."""
        temp_db.get_or_create_player("increment_user")
        temp_db.set_mastery_level("increment_user", "test_concept", 1.0)

        new_level = temp_db.increment_mastery("increment_user", "test_concept", 0.5)
        assert new_level == 1.5

    def test_increment_mastery_capped(self, temp_db):
        """Test that mastery is capped at 4.0."""
        temp_db.get_or_create_player("cap_user")
        temp_db.set_mastery_level("cap_user", "cap_concept", 3.8)

        new_level = temp_db.increment_mastery("cap_user", "cap_concept", 1.0)
        assert new_level == 4.0


class TestSessions:
    """Tests for session management."""

    def test_create_session(self, temp_db):
        """Test creating a session."""
        temp_db.get_or_create_player("session_user")
        session_id = temp_db.create_session("session_user")
        assert session_id is not None
        assert len(session_id) > 20

    def test_verify_valid_session(self, temp_db):
        """Test verifying a valid session."""
        temp_db.get_or_create_player("verify_session_user")
        session_id = temp_db.create_session("verify_session_user")
        player_id = temp_db.verify_session(session_id)
        assert player_id == "verify_session_user"

    def test_verify_invalid_session(self, temp_db):
        """Test verifying an invalid session."""
        player_id = temp_db.verify_session("invalid_session_id")
        assert player_id is None

    def test_delete_session(self, temp_db):
        """Test deleting a session."""
        temp_db.get_or_create_player("delete_session_user")
        session_id = temp_db.create_session("delete_session_user")
        temp_db.delete_session(session_id)
        player_id = temp_db.verify_session(session_id)
        assert player_id is None


class TestPlayerStats:
    """Tests for player statistics."""

    def test_get_player_stats(self, temp_db):
        """Test getting comprehensive player stats."""
        temp_db.get_or_create_player("stats_user")
        temp_db.add_player_xp("stats_user", 150)
        temp_db.record_completion("stats_user", "challenge1", 5.0)
        temp_db.set_mastery_level("stats_user", "concept1", 4.0)
        temp_db.set_password("stats_user", "password")
        temp_db.set_gamepad_combo("stats_user", ["A", "B"])

        stats = temp_db.get_player_stats("stats_user")
        assert stats["total_xp"] == 150
        assert stats["level"] == 2  # 100-249 XP = level 2
        assert stats["unique_challenges"] == 1
        assert stats["mastered_concepts"] == 1
        assert stats["has_password"] is True
        assert stats["has_gamepad_combo"] is True
