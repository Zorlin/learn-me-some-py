"""
Tests for main entry point
===========================

Tests CLI argument parsing and initialization logic.
"""

import sys
import argparse
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

# Need to add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lmsp.main import parse_args, create_profile_path, load_or_create_profile
from lmsp.adaptive.engine import LearnerProfile


class TestParseArgs:
    """Test CLI argument parsing."""

    def test_default_args(self):
        """Test default argument values."""
        args = parse_args([])
        assert args.input == "keyboard"
        assert args.player_id is None
        assert args.challenge is None
        assert args.multiplayer is False
        assert args.mode == "coop"

    def test_keyboard_input(self):
        """Test keyboard input selection."""
        args = parse_args(["--input", "keyboard"])
        assert args.input == "keyboard"

    def test_gamepad_input(self):
        """Test gamepad input selection."""
        args = parse_args(["--input", "gamepad"])
        assert args.input == "gamepad"

    def test_player_id(self):
        """Test player ID specification."""
        args = parse_args(["--player-id", "TestPlayer"])
        assert args.player_id == "TestPlayer"

    def test_challenge_id(self):
        """Test starting with specific challenge."""
        args = parse_args(["--challenge", "lists-basic-01"])
        assert args.challenge == "lists-basic-01"

    def test_multiplayer_flag(self):
        """Test multiplayer mode enabled."""
        args = parse_args(["--multiplayer"])
        assert args.multiplayer is True

    def test_multiplayer_modes(self):
        """Test different multiplayer modes."""
        for mode in ["coop", "race", "teach", "spectate"]:
            args = parse_args(["--multiplayer", "--mode", mode])
            assert args.mode == mode

    def test_combined_args(self):
        """Test multiple arguments together."""
        args = parse_args([
            "--input", "gamepad",
            "--player-id", "Wings",
            "--challenge", "functions-01",
            "--multiplayer",
            "--mode", "race"
        ])
        assert args.input == "gamepad"
        assert args.player_id == "Wings"
        assert args.challenge == "functions-01"
        assert args.multiplayer is True
        assert args.mode == "race"


class TestProfilePath:
    """Test profile path creation."""

    def test_default_profile_path(self):
        """Test default profile path when no player ID."""
        path = create_profile_path(None)
        assert path.name == "default.json"
        assert str(path).endswith("lmsp/profiles/default.json")

    def test_named_profile_path(self):
        """Test profile path with player ID."""
        path = create_profile_path("TestPlayer")
        assert path.name == "TestPlayer.json"
        assert str(path).endswith("lmsp/profiles/TestPlayer.json")

    def test_sanitized_profile_path(self):
        """Test profile path sanitization."""
        path = create_profile_path("Test Player!")
        # Should sanitize to valid filename
        assert path.name == "Test_Player_.json"


class TestLoadOrCreateProfile:
    """Test profile loading/creation."""

    def test_create_new_profile(self, tmp_path):
        """Test creating a new profile."""
        profile_path = tmp_path / "new_player.json"
        profile = load_or_create_profile(profile_path, "NewPlayer")

        assert profile.player_id == "NewPlayer"
        assert profile_path.exists()

    def test_load_existing_profile(self, tmp_path):
        """Test loading an existing profile."""
        profile_path = tmp_path / "existing.json"

        # Create a profile
        original = LearnerProfile(
            player_id="ExistingPlayer",
            mastery_levels={"loops": 3}
        )
        profile_path.write_text(original.to_json())

        # Load it
        loaded = load_or_create_profile(profile_path, "ExistingPlayer")

        assert loaded.player_id == "ExistingPlayer"
        assert loaded.mastery_levels["loops"] == 3

    def test_profile_persistence(self, tmp_path):
        """Test that profile data persists correctly."""
        profile_path = tmp_path / "persist.json"

        # Create and save
        profile1 = load_or_create_profile(profile_path, "Persistent")
        profile1.mastery_levels["strings"] = 4
        profile_path.write_text(profile1.to_json())

        # Load again
        profile2 = load_or_create_profile(profile_path, "Persistent")
        assert profile2.mastery_levels["strings"] == 4


class TestMainFunction:
    """Test main() entry point."""

    @patch("lmsp.main.Console")
    @patch("lmsp.main.load_or_create_profile")
    @patch("lmsp.main.AdaptiveEngine")
    def test_main_runs_without_error(self, mock_engine, mock_profile, mock_console):
        """Test that main() executes successfully."""
        from lmsp.main import main

        # Mock profile
        mock_profile.return_value = LearnerProfile(player_id="test")

        # Mock engine
        mock_engine_instance = Mock()
        mock_engine.return_value = mock_engine_instance

        # Mock console
        mock_console_instance = Mock()
        mock_console.return_value = mock_console_instance

        # Run main with test args
        with patch("sys.argv", ["lmsp", "--player-id", "TestPlayer"]):
            result = main()

        assert result == 0
        mock_profile.assert_called_once()
        mock_engine.assert_called_once()

    @patch("lmsp.main.Console")
    @patch("lmsp.main.load_or_create_profile")
    def test_main_with_challenge(self, mock_profile, mock_console):
        """Test main() with specific challenge."""
        from lmsp.main import main

        mock_profile.return_value = LearnerProfile(player_id="test")
        mock_console.return_value = Mock()

        with patch("sys.argv", ["lmsp", "--challenge", "test-01"]):
            result = main()

        assert result == 0


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
