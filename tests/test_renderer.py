"""
Tests for the TUI Renderer
===========================

Tests both RichRenderer (integration tests) and MinimalRenderer (unit tests).
"""
import pytest
from io import StringIO

from lmsp.game.renderer import Renderer, RichRenderer, MinimalRenderer, format_test_result, format_hint
from lmsp.python.challenges import Challenge, TestCase
from lmsp.python.validator import ValidationResult, TestResult
from lmsp.input.emotional import EmotionalPrompt
from lmsp.adaptive.engine import AdaptiveRecommendation


@pytest.fixture
def sample_challenge():
    """Create a sample challenge for testing."""
    return Challenge(
        id="test_001",
        name="Test Challenge",
        level=1,
        prerequisites=[],
        description_brief="A simple test",
        description_detailed="A more detailed description of the test challenge",
        skeleton_code="def solution():\n    pass",
        test_cases=[
            TestCase(name="basic", input=None, expected=42),
            TestCase(name="edge", input=None, expected=0),
        ],
        hints={
            1: "This is hint level 1",
            2: "This is hint level 2",
        }
    )


@pytest.fixture
def sample_validation_result():
    """Create a sample validation result."""
    return ValidationResult(
        success=True,
        output="Hello, world!",
        error=None,
        time_seconds=0.5,
        test_results=[
            TestResult(test_name="basic", passed=True, expected=42, actual=42),
            TestResult(test_name="edge", passed=False, expected=0, actual=1, error=None),
        ]
    )


@pytest.fixture
def sample_emotional_prompt():
    """Create a sample emotional prompt."""
    return EmotionalPrompt(
        question="How are you feeling?",
        right_trigger="Happy",
        left_trigger="Frustrated",
        y_button="More options"
    )


@pytest.fixture
def sample_recommendation():
    """Create a sample recommendation."""
    return AdaptiveRecommendation(
        action="challenge",
        concept="list_comprehensions",
        challenge_id="lists_003",
        reason="Let's strengthen this one",
        confidence=0.8
    )


class TestMinimalRenderer:
    """Test the minimal text-only renderer."""

    def test_render_challenge(self, sample_challenge):
        """Test rendering a challenge."""
        renderer = MinimalRenderer()
        renderer.render_challenge(sample_challenge)
        output = renderer.get_output()

        assert "Test Challenge" in output
        assert "A simple test" in output
        assert "def solution():" in output

    def test_render_code_editor(self):
        """Test rendering the code editor."""
        renderer = MinimalRenderer()
        code = "def solution():\n    return 42"
        renderer.render_code_editor(code, (1, 4))
        output = renderer.get_output()

        assert "def solution():" in output
        assert "return 42" in output
        assert "Cursor: (1, 4)" in output

    def test_render_test_results_success(self, sample_validation_result):
        """Test rendering successful test results."""
        renderer = MinimalRenderer()
        renderer.render_test_results(sample_validation_result)
        output = renderer.get_output()

        assert "PASS" in output
        assert "basic" in output
        assert "1/2" in output  # 1 passing out of 2

    def test_render_test_results_failure(self):
        """Test rendering failed test results."""
        renderer = MinimalRenderer()
        result = ValidationResult(
            success=False,
            output="",
            error="Syntax Error: invalid syntax",
            time_seconds=0.1,
            test_results=[]
        )
        renderer.render_test_results(result)
        output = renderer.get_output()

        assert "ERROR" in output
        assert "Syntax Error" in output

    def test_render_emotional_prompt(self, sample_emotional_prompt):
        """Test rendering an emotional prompt."""
        renderer = MinimalRenderer()
        renderer.render_emotional_prompt(sample_emotional_prompt)
        output = renderer.get_output()

        assert "How are you feeling?" in output
        assert "Happy" in output
        assert "Frustrated" in output

    def test_render_recommendation(self, sample_recommendation):
        """Test rendering a recommendation."""
        renderer = MinimalRenderer()
        renderer.render_recommendation(sample_recommendation)
        output = renderer.get_output()

        assert "challenge" in output
        assert "list_comprehensions" in output
        assert "Let's strengthen this one" in output

    def test_show_message(self):
        """Test showing different message types."""
        renderer = MinimalRenderer()

        renderer.show_message("Info message", "info")
        output = renderer.get_output()
        assert "INFO" in output
        assert "Info message" in output

        renderer.show_message("Error message", "error")
        output = renderer.get_output()
        assert "ERROR" in output
        assert "Error message" in output

    def test_clear_resets_buffer(self):
        """Test that clearing resets the output buffer."""
        renderer = MinimalRenderer()
        renderer.show_message("Test")
        assert "Test" in renderer.get_output()

        renderer.clear()
        assert renderer.get_output() == ""


class TestRichRenderer:
    """Test the Rich-based renderer (integration tests)."""

    def test_render_challenge(self, sample_challenge):
        """Test rendering a challenge with Rich."""
        renderer = RichRenderer()
        # Should not raise
        renderer.render_challenge(sample_challenge)

    def test_render_code_editor(self):
        """Test rendering code editor with Rich."""
        renderer = RichRenderer()
        code = "def solution():\n    return 42"
        # Should not raise
        renderer.render_code_editor(code, (1, 4))

    def test_render_test_results(self, sample_validation_result):
        """Test rendering test results with Rich."""
        renderer = RichRenderer()
        # Should not raise
        renderer.render_test_results(sample_validation_result)

    def test_render_emotional_prompt(self, sample_emotional_prompt):
        """Test rendering emotional prompt with Rich."""
        renderer = RichRenderer()
        # Should not raise
        renderer.render_emotional_prompt(sample_emotional_prompt)

    def test_render_recommendation(self, sample_recommendation):
        """Test rendering recommendation with Rich."""
        renderer = RichRenderer()
        # Should not raise
        renderer.render_recommendation(sample_recommendation)

    def test_show_message(self):
        """Test showing messages with Rich."""
        renderer = RichRenderer()
        # Should not raise
        renderer.show_message("Test message", "info")
        renderer.show_message("Error message", "error")
        renderer.show_message("Success message", "success")
        renderer.show_message("Warning message", "warning")


class TestHelperFunctions:
    """Test helper formatting functions."""

    def test_format_test_result_pass(self):
        """Test formatting a passing test result."""
        result = TestResult(
            test_name="basic",
            passed=True,
            expected=42,
            actual=42
        )
        formatted = format_test_result(result)
        assert "PASS" in formatted
        assert "basic" in formatted

    def test_format_test_result_fail(self):
        """Test formatting a failing test result."""
        result = TestResult(
            test_name="edge",
            passed=False,
            expected=0,
            actual=1
        )
        formatted = format_test_result(result)
        assert "FAIL" in formatted
        assert "edge" in formatted
        assert "Expected: 0" in formatted
        assert "Actual: 1" in formatted

    def test_format_test_result_error(self):
        """Test formatting a test result with error."""
        result = TestResult(
            test_name="error_case",
            passed=False,
            expected=42,
            actual=None,
            error="ZeroDivisionError: division by zero"
        )
        formatted = format_test_result(result)
        assert "ERROR" in formatted
        assert "ZeroDivisionError" in formatted

    def test_format_hint_levels(self):
        """Test formatting hints with different levels."""
        hint1 = format_hint("Think about loops", 1)
        hint2 = format_hint("Consider using a for loop", 2)
        hint3 = format_hint("Try: for i in range(10)", 3)

        assert "Think about loops" in hint1
        assert "Consider using a for loop" in hint2
        assert "Try: for i in range(10)" in hint3

        # Different levels should have different indicators
        assert hint1 != hint2


# Self-teaching note:
#
# This file demonstrates:
# - pytest fixtures for test data setup (Level 6: Testing)
# - Test organization with classes (Level 5: Classes)
# - Unit tests vs integration tests (Testing best practices)
# - Mocking and test isolation (Professional Python)
# - Assertions with pytest (Level 6: Testing)
#
# The learner will write these tests BEFORE implementing the renderer,
# experiencing TDD (Test-Driven Development) first-hand.
