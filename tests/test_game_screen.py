"""
Tests for Rich TUI Game Renderer

Tests the live updating game screen with:
- Challenge display
- Code editor with syntax highlighting
- Live test results
- Emotional feedback visualization
- Progress bars
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from rich.console import Console
from rich.panel import Panel
from io import StringIO

from lmsp.ui.game_screen import (
    GameScreen,
    GameState,
    TestResult,
    EmotionalState,
)


class TestGameState:
    """Test GameState dataclass."""

    def test_game_state_creation(self):
        """Test creating a GameState."""
        state = GameState(
            challenge_title="Hello World",
            challenge_description="Print hello world",
            current_code="print('hello')",
            test_results=[],
            emotional_state=EmotionalState(),
            xp=0,
            level=1,
            progress=0.0,
        )

        assert state.challenge_title == "Hello World"
        assert state.current_code == "print('hello')"
        assert state.level == 1

    def test_game_state_with_test_results(self):
        """Test GameState with test results."""
        results = [
            TestResult(name="test_hello", passed=True, message="OK"),
            TestResult(name="test_world", passed=False, message="Expected 'world'"),
        ]

        state = GameState(
            challenge_title="Test",
            challenge_description="Desc",
            current_code="code",
            test_results=results,
            emotional_state=EmotionalState(),
            xp=10,
            level=1,
            progress=0.5,
        )

        assert len(state.test_results) == 2
        assert state.test_results[0].passed is True
        assert state.test_results[1].passed is False


class TestEmotionalState:
    """Test EmotionalState dataclass."""

    def test_emotional_state_defaults(self):
        """Test EmotionalState with default values."""
        state = EmotionalState()

        assert state.enjoyment == 0.0
        assert state.frustration == 0.0
        assert state.recent_feedback == []

    def test_emotional_state_with_values(self):
        """Test EmotionalState with specific values."""
        state = EmotionalState(
            enjoyment=0.8,
            frustration=0.2,
            recent_feedback=["Great!", "Keep going!"]
        )

        assert state.enjoyment == 0.8
        assert state.frustration == 0.2
        assert len(state.recent_feedback) == 2


class TestGameScreen:
    """Test GameScreen renderer."""

    def test_game_screen_creation(self):
        """Test creating a GameScreen."""
        screen = GameScreen()

        assert screen is not None
        assert hasattr(screen, 'render')

    def test_render_challenge_panel(self):
        """Test rendering the challenge panel."""
        screen = GameScreen()
        state = GameState(
            challenge_title="Print Hello",
            challenge_description="Write a program that prints 'Hello, World!'",
            current_code="",
            test_results=[],
            emotional_state=EmotionalState(),
            xp=0,
            level=1,
            progress=0.0,
        )

        panel = screen._render_challenge_panel(state)

        assert panel is not None
        assert isinstance(panel, Panel)

    def test_render_code_editor_panel(self):
        """Test rendering code editor with syntax highlighting."""
        screen = GameScreen()
        state = GameState(
            challenge_title="Test",
            challenge_description="Desc",
            current_code="def hello():\n    print('world')",
            test_results=[],
            emotional_state=EmotionalState(),
            xp=0,
            level=1,
            progress=0.0,
        )

        panel = screen._render_code_editor_panel(state)

        assert panel is not None
        assert isinstance(panel, Panel)

    def test_render_test_results_panel(self):
        """Test rendering test results panel."""
        screen = GameScreen()
        results = [
            TestResult(name="test_1", passed=True, message="OK"),
            TestResult(name="test_2", passed=False, message="Failed: AssertionError"),
        ]
        state = GameState(
            challenge_title="Test",
            challenge_description="Desc",
            current_code="code",
            test_results=results,
            emotional_state=EmotionalState(),
            xp=0,
            level=1,
            progress=0.0,
        )

        panel = screen._render_test_results_panel(state)

        assert panel is not None
        assert isinstance(panel, Panel)

    def test_render_emotional_feedback_panel(self):
        """Test rendering emotional feedback visualization."""
        screen = GameScreen()
        emotional = EmotionalState(
            enjoyment=0.7,
            frustration=0.3,
            recent_feedback=["Good job!", "Keep going!"]
        )
        state = GameState(
            challenge_title="Test",
            challenge_description="Desc",
            current_code="code",
            test_results=[],
            emotional_state=emotional,
            xp=50,
            level=2,
            progress=0.5,
        )

        panel = screen._render_emotional_panel(state)

        assert panel is not None
        assert isinstance(panel, Panel)

    def test_render_progress_panel(self):
        """Test rendering progress bars."""
        screen = GameScreen()
        state = GameState(
            challenge_title="Test",
            challenge_description="Desc",
            current_code="code",
            test_results=[],
            emotional_state=EmotionalState(),
            xp=75,
            level=3,
            progress=0.75,
        )

        panel = screen._render_progress_panel(state)

        assert panel is not None
        assert isinstance(panel, Panel)

    def test_render_full_screen(self):
        """Test rendering the complete game screen."""
        screen = GameScreen()
        state = GameState(
            challenge_title="FizzBuzz",
            challenge_description="Write FizzBuzz for numbers 1-100",
            current_code="for i in range(1, 101):\n    print(i)",
            test_results=[
                TestResult(name="test_fizz", passed=False, message="Expected 'Fizz'"),
            ],
            emotional_state=EmotionalState(enjoyment=0.6, frustration=0.2),
            xp=120,
            level=4,
            progress=0.4,
        )

        layout = screen.render(state)

        assert layout is not None

    def test_update_state(self):
        """Test updating the game state triggers re-render."""
        screen = GameScreen()
        initial_state = GameState(
            challenge_title="Test 1",
            challenge_description="Desc",
            current_code="code1",
            test_results=[],
            emotional_state=EmotionalState(),
            xp=0,
            level=1,
            progress=0.0,
        )

        screen.update_state(initial_state)
        assert screen.current_state == initial_state

        new_state = GameState(
            challenge_title="Test 2",
            challenge_description="Desc",
            current_code="code2",
            test_results=[],
            emotional_state=EmotionalState(),
            xp=10,
            level=1,
            progress=0.1,
        )

        screen.update_state(new_state)
        assert screen.current_state == new_state
        assert screen.current_state.xp == 10


class TestTestResult:
    """Test TestResult dataclass."""

    def test_test_result_passed(self):
        """Test creating a passing test result."""
        result = TestResult(
            name="test_example",
            passed=True,
            message="All assertions passed"
        )

        assert result.name == "test_example"
        assert result.passed is True
        assert result.message == "All assertions passed"

    def test_test_result_failed(self):
        """Test creating a failing test result."""
        result = TestResult(
            name="test_example",
            passed=False,
            message="AssertionError: Expected 5, got 3",
            details="Line 10: assert foo() == 5"
        )

        assert result.passed is False
        assert "AssertionError" in result.message
        assert result.details is not None


class TestKeyboardHandling:
    """Test keyboard event handling."""

    def test_handle_key_event(self):
        """Test handling keyboard input events."""
        screen = GameScreen()

        # Mock keyboard event
        event = Mock()
        event.key = "a"

        handled = screen.handle_key(event)

        # Should handle the key
        assert handled is True

    def test_handle_special_keys(self):
        """Test handling special keys like arrows, enter."""
        screen = GameScreen()

        special_keys = ["up", "down", "left", "right", "enter", "escape"]

        for key in special_keys:
            event = Mock()
            event.key = key
            handled = screen.handle_key(event)
            assert handled is True

    def test_code_editing_with_keyboard(self):
        """Test editing code with keyboard input."""
        screen = GameScreen()
        state = GameState(
            challenge_title="Test",
            challenge_description="Desc",
            current_code="print(",
            test_results=[],
            emotional_state=EmotionalState(),
            xp=0,
            level=1,
            progress=0.0,
        )

        screen.update_state(state)

        # Simulate typing
        event = Mock()
        event.key = "'"
        screen.handle_key(event)

        # Code should be updated (we'll implement this)
        # For now, just check it doesn't crash
        assert True


# Self-teaching note:
#
# This file demonstrates:
# - Test-driven development (TDD) - write tests FIRST
# - Mocking external dependencies (Level 5+)
# - Testing UI components (Level 6+)
# - Dataclass testing (Level 5)
# - Event handling tests (Level 6)
#
# These tests define the behavior we want from our Rich TUI game screen:
# 1. Live updating display
# 2. Syntax-highlighted code editor
# 3. Real-time test results
# 4. Emotional feedback visualization
# 5. Progress tracking
# 6. Keyboard event handling
#
# Now we implement the code to make these tests pass!
