"""
Tests for the Emotional Input System

TDD: These tests were written BEFORE the implementation.
They define the expected behavior of emotional input via controllers.
"""

import pytest
from lmsp.input.emotional import (
    EmotionalDimension,
    EmotionalSample,
    EmotionalState,
    EmotionalPrompt,
)


class TestEmotionalSample:
    """Test individual emotional samples."""

    def test_sample_clamps_value_to_valid_range(self):
        """Values should be clamped to 0.0-1.0"""
        sample = EmotionalSample(
            timestamp=1234567890.0,
            dimension=EmotionalDimension.ENJOYMENT,
            value=1.5,  # Over 1.0
            context="test"
        )
        assert sample.value == 1.0

    def test_sample_clamps_negative_to_zero(self):
        """Negative values should clamp to 0.0"""
        sample = EmotionalSample(
            timestamp=1234567890.0,
            dimension=EmotionalDimension.FRUSTRATION,
            value=-0.5,
            context="test"
        )
        assert sample.value == 0.0


class TestEmotionalState:
    """Test emotional state tracking."""

    def test_empty_state_has_neutral_enjoyment(self):
        """Empty state should return neutral (0.5) for enjoyment."""
        state = EmotionalState()
        assert state.get_enjoyment() == 0.5

    def test_empty_state_has_zero_frustration(self):
        """Empty state should return 0.0 for frustration."""
        state = EmotionalState()
        assert state.get_frustration() == 0.0

    def test_recording_updates_average(self):
        """Recording samples should update the rolling average."""
        state = EmotionalState()
        state.record(EmotionalDimension.ENJOYMENT, 0.8, "having_fun")
        assert state.get_enjoyment() == 0.8

    def test_multiple_recordings_average(self):
        """Multiple recordings should average together."""
        state = EmotionalState()
        state.record(EmotionalDimension.ENJOYMENT, 1.0, "")
        state.record(EmotionalDimension.ENJOYMENT, 0.5, "")
        assert state.get_enjoyment() == 0.75

    def test_flow_state_detection(self):
        """Flow = high enjoyment + low frustration."""
        state = EmotionalState()
        state.record(EmotionalDimension.ENJOYMENT, 0.9, "")
        state.record(EmotionalDimension.FRUSTRATION, 0.1, "")
        assert state.is_in_flow() is True

    def test_not_in_flow_when_frustrated(self):
        """Can't be in flow if frustrated."""
        state = EmotionalState()
        state.record(EmotionalDimension.ENJOYMENT, 0.9, "")
        state.record(EmotionalDimension.FRUSTRATION, 0.5, "")
        assert state.is_in_flow() is False

    def test_needs_break_when_frustrated(self):
        """Should suggest break when frustration is high."""
        state = EmotionalState()
        for _ in range(25):  # Need enough samples
            state.record(EmotionalDimension.FRUSTRATION, 0.8, "")
        assert state.needs_break() is True


class TestEmotionalPrompt:
    """Test the emotional prompt UI component."""

    def test_prompt_initializes_at_zero(self):
        """Prompt should start with no input."""
        prompt = EmotionalPrompt(
            question="How are you feeling?",
            right_trigger="Happy",
            left_trigger="Frustrated"
        )
        assert prompt._rt_value == 0.0
        assert prompt._lt_value == 0.0

    def test_prompt_updates_from_controller(self):
        """Prompt should update from controller state."""
        prompt = EmotionalPrompt(question="Test")
        prompt.update(rt=0.7, lt=0.2, y_pressed=False, a_pressed=False)
        assert prompt._rt_value == 0.7
        assert prompt._lt_value == 0.2

    def test_confirm_requires_input(self):
        """A press only confirms if there's trigger input."""
        prompt = EmotionalPrompt(question="Test")
        prompt.update(rt=0.0, lt=0.0, y_pressed=False, a_pressed=True)
        assert prompt.is_confirmed is False

        prompt.update(rt=0.5, lt=0.0, y_pressed=False, a_pressed=True)
        assert prompt.is_confirmed is True

    def test_get_response_returns_dominant_dimension(self):
        """Response should be whichever trigger was pulled more."""
        prompt = EmotionalPrompt(question="Test")
        prompt.update(rt=0.8, lt=0.3, y_pressed=False, a_pressed=False)

        dimension, value = prompt.get_response()
        assert dimension == EmotionalDimension.ENJOYMENT
        assert value == 0.8

    def test_y_button_requests_complex_input(self):
        """Y button should flag for complex response."""
        prompt = EmotionalPrompt(question="Test", y_button="More options")
        prompt.update(rt=0.0, lt=0.0, y_pressed=True, a_pressed=False)
        assert prompt.wants_complex is True

    def test_render_shows_trigger_bars(self):
        """Render should show visual bars for trigger values."""
        prompt = EmotionalPrompt(question="How's it going?")
        prompt.update(rt=0.5, lt=0.2, y_pressed=False, a_pressed=False)
        output = prompt.render()

        assert "How's it going?" in output
        assert "RT" in output
        assert "LT" in output


# Self-teaching note for tests:
#
# This test file demonstrates:
# - pytest test classes and methods
# - Descriptive test naming
# - Testing edge cases (negative values, empty state)
# - Testing state transitions
# - Property assertions
#
# Tests are documentation. A learner can read these to understand
# what the EmotionalInput system is SUPPOSED to do.
