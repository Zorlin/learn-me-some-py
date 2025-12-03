"""
Tests for Rich Live Game Loop

This tests the event-driven, gorgeous game loop that replaces janky input() prompts.
"""

import pytest
from rich.console import Console
from io import StringIO
from lmsp.game.live_loop import LiveGameLoop, GamePhase, GameAction


class TestLiveGameLoop:
    """Test the event-driven Rich Live game loop."""

    def test_create_loop(self):
        """Can create a LiveGameLoop instance."""
        console = Console(file=StringIO())
        loop = LiveGameLoop(console=console)
        assert loop is not None
        assert loop.phase == GamePhase.MENU

    def test_menu_navigation(self):
        """Can navigate menu with keys."""
        console = Console(file=StringIO())
        loop = LiveGameLoop(console=console)

        # Simulate down arrow key
        action = loop.handle_key("down")
        assert loop.selected_menu_index == 1

        # Simulate up arrow key
        action = loop.handle_key("up")
        assert loop.selected_menu_index == 0

    def test_menu_selection(self):
        """Can select menu items with Enter."""
        console = Console(file=StringIO())
        loop = LiveGameLoop(console=console)

        # Select first menu item (Start Learning)
        loop.selected_menu_index = 0
        action = loop.handle_key("enter")
        assert action == GameAction.START_LEARNING

    def test_render_menu(self):
        """Can render beautiful menu."""
        output = StringIO()
        console = Console(file=output, force_terminal=True, width=80)
        loop = LiveGameLoop(console=console)

        # Get renderable for menu
        renderable = loop.get_renderable()
        console.print(renderable)

        output_text = output.getvalue()
        assert "Main Menu" in output_text
        assert "Start Learning" in output_text

    def test_quit_action(self):
        """Can quit with 'q' key."""
        console = Console(file=StringIO())
        loop = LiveGameLoop(console=console)

        action = loop.handle_key("q")
        assert action == GameAction.QUIT

    def test_phase_transitions(self):
        """Can transition between phases."""
        console = Console(file=StringIO())
        loop = LiveGameLoop(console=console)

        # Start in MENU
        assert loop.phase == GamePhase.MENU

        # Transition to CHALLENGE_SELECTION
        loop.transition_to(GamePhase.CHALLENGE_SELECTION)
        assert loop.phase == GamePhase.CHALLENGE_SELECTION

    def test_render_challenge_list(self):
        """Can render challenge selection screen."""
        output = StringIO()
        console = Console(file=output, force_terminal=True, width=80)
        loop = LiveGameLoop(console=console)
        loop.transition_to(GamePhase.CHALLENGE_SELECTION)

        # Mock some challenges
        loop.available_challenges = [
            {"id": "hello_world", "name": "Hello World", "level": 1},
            {"id": "variables", "name": "Variables", "level": 2},
        ]

        renderable = loop.get_renderable()
        console.print(renderable)

        output_text = output.getvalue()
        assert "Select Challenge" in output_text
        assert "Hello World" in output_text


# Self-teaching note:
#
# This test file demonstrates:
# - Testing UI without actually blocking on input() (Level 5: Testing)
# - Mocking console output with StringIO (Level 5: Testing)
# - Event-driven architecture testing (Level 6: Architecture)
# - Testing state transitions (Level 4: State machines)
#
# We test the interactive experience WITHOUT needing real keyboard input!
# This is how professional games test their UI - simulate events, check state.
