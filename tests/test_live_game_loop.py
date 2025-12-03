"""
Tests for Rich Live Game Loop - Event-Driven Architecture
==========================================================

Testing the gorgeous game loop that replaces input() prompts
with Rich Live displays and event-driven keyboard handling.
"""

import pytest
from io import StringIO
from unittest.mock import Mock, patch
from rich.console import Console

from lmsp.game.live_loop import LiveGameLoop, GamePhase, LiveGameState, MenuOption
from lmsp.game.live_input import LiveInputHandler


@pytest.fixture
def console():
    """Create a test console."""
    output = StringIO()
    return Console(file=output, width=80, legacy_windows=False)


class TestLiveGameLoop:
    """Test the Live game loop."""

    def test_engine_initialization(self, console):
        """Test that engine initializes correctly."""
        engine = LiveGameLoop(console=console)

        assert engine.console == console
        assert engine.state.phase == GamePhase.MENU
        assert engine.state.running is True  # Starts ready to run
        assert isinstance(engine.menu_options, list)
        assert len(engine.menu_options) >= 4

    def test_state_initialization(self):
        """Test that game state initializes correctly."""
        state = LiveGameState()

        assert state.phase == GamePhase.MENU
        assert state.running is True  # Ready to run by default
        assert state.menu_index == 0
        assert state.challenge_id is None
        assert state.code_lines == ['']
        assert state.cursor_line == 0
        assert state.cursor_col == 0

    def test_menu_options_structure(self, console):
        """Test that menu options are properly structured."""
        engine = LiveGameLoop(console=console)

        for option in engine.menu_options:
            assert isinstance(option, MenuOption)
            assert isinstance(option.key, str)
            assert isinstance(option.label, str)
            assert option.action is not None

    def test_phase_enum_values(self):
        """Test that all expected phases exist."""
        assert GamePhase.MENU
        assert GamePhase.CHALLENGE_SELECTION
        assert GamePhase.CODING
        assert GamePhase.RUNNING_TESTS
        assert GamePhase.EMOTIONAL_FEEDBACK

    def test_no_blocking_input_in_init(self, console):
        """Test that initialization never uses blocking input()."""
        with patch('builtins.input', side_effect=AssertionError("input() should not be called!")):
            # If we get here without AssertionError, no input() was called
            engine = LiveGameLoop(console=console)
            assert engine is not None


class TestLiveGameState:
    """Test the live game state."""

    def test_state_phase_changes(self):
        """Test that phase can be changed."""
        state = LiveGameState()

        assert state.phase == GamePhase.MENU
        state.phase = GamePhase.CHALLENGE_SELECTION
        assert state.phase == GamePhase.CHALLENGE_SELECTION

    def test_state_code_lines(self):
        """Test code lines manipulation."""
        state = LiveGameState()

        state.code_lines = ["def hello():", "    pass"]
        assert len(state.code_lines) == 2
        assert state.code_lines[0] == "def hello():"

    def test_state_cursor_position(self):
        """Test cursor position tracking."""
        state = LiveGameState()

        state.cursor_line = 5
        state.cursor_col = 10

        assert state.cursor_line == 5
        assert state.cursor_col == 10


class TestLiveInput:
    """Test the live input system."""

    def test_input_handler_initialization(self):
        """Test input handler creates successfully."""
        handler = LiveInputHandler()
        assert handler is not None

    def test_keyboard_event_handling(self):
        """Test that keyboard events are captured without blocking."""
        handler = LiveInputHandler()

        # Should be able to check for input without blocking
        key = handler.get_key_non_blocking()

        # Returns None if no key pressed (doesn't block)
        assert key is None or isinstance(key, str)

    def test_quit_key_handling(self):
        """Test that quit keys work."""
        handler = LiveInputHandler()

        # 'q' should be detected as quit
        assert handler.is_quit_key("q")

        # Ctrl+C should be detected as quit
        assert handler.is_quit_key("\x03")


class TestMenuOption:
    """Test the menu option dataclass."""

    def test_menu_option_creation(self):
        """Test creating a menu option."""
        from lmsp.game.live_loop import GameAction

        option = MenuOption(
            key="1",
            label="Test Option",
            action=GameAction.START_LEARNING
        )

        assert option.key == "1"
        assert option.label == "Test Option"
        assert option.action == GameAction.START_LEARNING


# Self-teaching note:
#
# This test file demonstrates:
# - Testing event-driven systems (no blocking I/O)
# - Testing state machines (phase transitions)
# - Testing data classes (MenuOption, LiveGameState)
# - Unit testing individual components
#
# Prerequisites:
# - Level 4: Testing frameworks (pytest)
# - Level 5: State machines and enums
# - Level 5: Event-driven programming
#
# The game loop avoids blocking I/O - that's the key innovation!
