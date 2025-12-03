"""
Tests for Rich Live Game Loop - Event-Driven Architecture
==========================================================

Testing the new gorgeous game loop that replaces input() prompts
with Rich Live displays and event-driven keyboard handling.
"""

import pytest
from io import StringIO
from unittest.mock import Mock, patch
from rich.console import Console

from lmsp.game.live_engine import LiveGameEngine, GamePhase
from lmsp.adaptive.engine import LearnerProfile


@pytest.fixture
def mock_profile():
    """Create a mock learner profile for testing."""
    return LearnerProfile(player_id="test_player")


@pytest.fixture
def console():
    """Create a test console."""
    output = StringIO()
    return Console(file=output, width=80, legacy_windows=False)


class TestLiveGameEngine:
    """Test the new Live game engine."""

    def test_engine_initialization(self, mock_profile, console):
        """Test that engine initializes correctly."""
        engine = LiveGameEngine(profile=mock_profile, console=console)

        assert engine.profile == mock_profile
        assert engine.phase == GamePhase.MENU
        assert engine._running == False
        assert engine.console == console

    def test_render_menu(self, mock_profile, console):
        """Test that menu renders without blocking input()."""
        engine = LiveGameEngine(profile=mock_profile, console=console)

        # Menu should render using Rich panels and not block
        menu_content = engine._render_menu_screen()

        assert "LMSP" in menu_content or "Main Menu" in str(menu_content)
        # Should not use input() - verify by checking no stdin access needed

    def test_key_handler_registration(self, mock_profile, console):
        """Test that keyboard handlers register correctly."""
        engine = LiveGameEngine(profile=mock_profile, console=console)

        # Register a test key handler
        called = []
        def test_handler():
            called.append(True)

        engine.register_key_handler("1", test_handler)

        # Simulate key press
        engine._handle_key_press("1")

        assert len(called) == 1

    def test_phase_transitions(self, mock_profile, console):
        """Test that phase transitions work."""
        engine = LiveGameEngine(profile=mock_profile, console=console)

        assert engine.phase == GamePhase.MENU

        engine._transition_to(GamePhase.SELECTING_CHALLENGE)
        assert engine.phase == GamePhase.SELECTING_CHALLENGE

    def test_no_blocking_io(self, mock_profile, console):
        """Test that game loop never uses blocking input()."""
        engine = LiveGameEngine(profile=mock_profile, console=console)

        # This should not block - it should use event-driven input
        with patch('builtins.input', side_effect=AssertionError("input() should not be called!")):
            menu_content = engine._render_menu_screen()

            # If we get here, no input() was called
            assert True


class TestLiveInput:
    """Test the live input system."""

    def test_keyboard_event_handling(self):
        """Test that keyboard events are captured without blocking."""
        from lmsp.game.live_input import LiveInputHandler

        handler = LiveInputHandler()

        # Should be able to check for input without blocking
        key = handler.get_key_non_blocking()

        # Returns None if no key pressed (doesn't block)
        assert key is None or isinstance(key, str)

    def test_quit_key_handling(self):
        """Test that quit keys (q, ESC, Ctrl+C) work."""
        from lmsp.game.live_input import LiveInputHandler

        handler = LiveInputHandler()

        # These keys should be detected as quit signals
        assert handler.is_quit_key("q")
        assert handler.is_quit_key("\x1b")  # ESC
        assert handler.is_quit_key("\x03")  # Ctrl+C


class TestRichLiveDisplay:
    """Test Rich Live display updates."""

    def test_live_menu_update(self, mock_profile, console):
        """Test that menu updates in Rich Live context."""
        engine = LiveGameEngine(profile=mock_profile, console=console)

        # Should create a Rich Live display
        live_display = engine._create_live_display()

        assert live_display is not None
        # Live should support update() method
        assert hasattr(live_display, 'update')

    def test_code_editor_live_update(self, mock_profile, console):
        """Test that code editor updates live."""
        engine = LiveGameEngine(profile=mock_profile, console=console)

        engine.code_buffer = ["def hello():", "    print('world')"]

        # Should render code with syntax highlighting
        rendered = engine._render_code_editor()

        assert rendered is not None
        # Should be a Rich renderable
        assert hasattr(rendered, '__rich__') or hasattr(rendered, '__rich_console__')


# Self-teaching note:
#
# This test file demonstrates:
# - Testing event-driven systems (no blocking I/O)
# - Mocking and patching (preventing actual input() calls)
# - Testing Rich console output (StringIO capture)
# - Testing state machines (phase transitions)
# - Testing keyboard event handling
#
# Prerequisites:
# - Level 4: Testing frameworks (pytest)
# - Level 5: Mocking and patching
# - Level 5: Event-driven programming
# - Level 6: TUI testing patterns
#
# These tests MUST pass before implementing the live game loop!
