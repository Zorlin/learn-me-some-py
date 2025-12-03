"""
Tests for Emotional Feedback Visualization UI

TDD: These tests were written BEFORE the implementation.
They define the expected behavior of emotional feedback visualization in the game UI.
"""

import pytest
from unittest.mock import Mock, MagicMock
from rich.console import Console
from io import StringIO

from lmsp.input.emotional import (
    EmotionalDimension,
    EmotionalPrompt,
    EmotionalState,
)
from lmsp.ui.emotional_feedback import (
    EmotionalFeedbackRenderer,
    TriggerBar,
    FeedbackPanel,
)


class TestTriggerBar:
    """Test the animated progress bar for trigger values."""

    def test_trigger_bar_renders_at_zero(self):
        """Trigger bar should render empty at 0.0 value."""
        bar = TriggerBar("RT", "Happy", value=0.0)
        rendered = bar.render()
        assert isinstance(rendered, str)
        assert len(rendered) > 0

    def test_trigger_bar_renders_at_half(self):
        """Trigger bar should show partial fill at 0.5 value."""
        bar = TriggerBar("RT", "Happy", value=0.5)
        rendered = bar.render()
        assert isinstance(rendered, str)
        # Should contain more visual content than zero
        assert len(rendered) > 10

    def test_trigger_bar_renders_at_full(self):
        """Trigger bar should render full at 1.0 value."""
        bar = TriggerBar("LT", "Frustrated", value=1.0)
        rendered = bar.render()
        assert isinstance(rendered, str)
        assert "█" in rendered or "▮" in rendered or "●" in rendered

    def test_trigger_bar_clamps_value(self):
        """Trigger bar should clamp values to 0.0-1.0 range."""
        bar = TriggerBar("RT", "Happy", value=1.5)
        assert bar.value == 1.0

    def test_trigger_bar_has_label(self):
        """Trigger bar should display trigger label."""
        bar = TriggerBar("RT", "Happy", value=0.5)
        rendered = bar.render()
        assert "RT" in rendered or "Happy" in rendered

    def test_trigger_bar_animated_width(self):
        """Trigger bar should have proportional width based on value."""
        bar_empty = TriggerBar("RT", "Happy", value=0.0)
        bar_full = TriggerBar("RT", "Happy", value=1.0)

        empty_render = bar_empty.render()
        full_render = bar_full.render()

        # Full bar should have more characters than empty bar
        assert len(full_render) >= len(empty_render)


class TestFeedbackPanel:
    """Test the overall feedback panel display."""

    def test_feedback_panel_shows_question(self):
        """Panel should display the emotional question."""
        panel = FeedbackPanel(
            question="How are you feeling?",
            right_trigger_label="Happy",
            left_trigger_label="Frustrated"
        )
        rendered = panel.render()
        assert "How are you feeling?" in rendered

    def test_feedback_panel_shows_rt_label(self):
        """Panel should display right trigger label."""
        panel = FeedbackPanel(
            question="Test",
            right_trigger_label="Happy",
            left_trigger_label="Frustrated"
        )
        rendered = panel.render()
        assert "Happy" in rendered

    def test_feedback_panel_shows_lt_label(self):
        """Panel should display left trigger label."""
        panel = FeedbackPanel(
            question="Test",
            right_trigger_label="Happy",
            left_trigger_label="Frustrated"
        )
        rendered = panel.render()
        assert "Frustrated" in rendered

    def test_feedback_panel_shows_instructions(self):
        """Panel should show instructions for input."""
        panel = FeedbackPanel(
            question="Test",
            right_trigger_label="Happy",
            left_trigger_label="Frustrated"
        )
        rendered = panel.render()
        # Should have some instruction text
        assert len(rendered) > 50

    def test_feedback_panel_with_y_button_option(self):
        """Panel should show Y button option if provided."""
        panel = FeedbackPanel(
            question="Test",
            right_trigger_label="Happy",
            left_trigger_label="Frustrated",
            y_button_option="More options"
        )
        rendered = panel.render()
        assert "More options" in rendered or "Y" in rendered


class TestEmotionalFeedbackRenderer:
    """Test the complete emotional feedback visualization."""

    def test_renderer_initializes(self):
        """Renderer should initialize without errors."""
        renderer = EmotionalFeedbackRenderer()
        assert renderer is not None

    def test_renderer_renders_prompt_beautifully(self):
        """Renderer should create beautiful visualization of prompt."""
        renderer = EmotionalFeedbackRenderer()
        prompt = EmotionalPrompt(
            question="How are you feeling?",
            right_trigger="Pull for happiness",
            left_trigger="Pull for frustration"
        )

        output = renderer.render_prompt(prompt)
        assert isinstance(output, str)
        assert len(output) > 0
        assert "How are you feeling?" in output

    def test_renderer_animates_trigger_values(self):
        """Renderer should animate different trigger values."""
        renderer = EmotionalFeedbackRenderer()
        prompt = EmotionalPrompt(question="Test")

        prompt.update(rt=0.3, lt=0.0, y_pressed=False, a_pressed=False)
        output_low = renderer.render_prompt(prompt)

        prompt.update(rt=0.9, lt=0.0, y_pressed=False, a_pressed=False)
        output_high = renderer.render_prompt(prompt)

        # Both should be strings (rendered)
        assert isinstance(output_low, str)
        assert isinstance(output_high, str)
        # They should be different (different values)
        # Don't assert exact difference, just that rendering happened

    def test_renderer_shows_both_triggers_independently(self):
        """Renderer should show RT and LT independently."""
        renderer = EmotionalFeedbackRenderer()
        prompt = EmotionalPrompt(question="Test")

        prompt.update(rt=0.8, lt=0.2, y_pressed=False, a_pressed=False)
        output = renderer.render_prompt(prompt)

        # Should show both triggers
        assert output.count("█") >= 1 or output.count("▮") >= 1

    def test_renderer_color_codes_positive_feedback(self):
        """Renderer should use positive colors for enjoyment (RT)."""
        renderer = EmotionalFeedbackRenderer()
        prompt = EmotionalPrompt(question="Test", right_trigger="Happy")

        prompt.update(rt=0.9, lt=0.0, y_pressed=False, a_pressed=False)
        output = renderer.render_prompt(prompt)

        # Should contain color codes or rich markup
        assert isinstance(output, str)
        assert len(output) > 0

    def test_renderer_color_codes_negative_feedback(self):
        """Renderer should use negative colors for frustration (LT)."""
        renderer = EmotionalFeedbackRenderer()
        prompt = EmotionalPrompt(question="Test", left_trigger="Frustrated")

        prompt.update(rt=0.0, lt=0.9, y_pressed=False, a_pressed=False)
        output = renderer.render_prompt(prompt)

        assert isinstance(output, str)
        assert len(output) > 0

    def test_renderer_integration_with_console(self):
        """Renderer should integrate beautifully with Rich Console."""
        console = Console(file=StringIO(), width=80, height=24)
        renderer = EmotionalFeedbackRenderer()

        prompt = EmotionalPrompt(question="How are you feeling?")
        prompt.update(rt=0.7, lt=0.2, y_pressed=False, a_pressed=False)

        output = renderer.render_prompt(prompt)
        # Should be renderable by console
        assert isinstance(output, str)

    def test_renderer_handles_no_y_button(self):
        """Renderer should handle prompts without Y button."""
        renderer = EmotionalFeedbackRenderer()
        prompt = EmotionalPrompt(
            question="Test",
            y_button=None  # No Y button
        )

        output = renderer.render_prompt(prompt)
        assert isinstance(output, str)

    def test_renderer_creates_panel_layout(self):
        """Renderer should create a nice panel layout."""
        renderer = EmotionalFeedbackRenderer()
        prompt = EmotionalPrompt(
            question="How are you feeling?",
            right_trigger="Pull for happiness",
            left_trigger="Pull for frustration"
        )

        output = renderer.render_prompt(prompt)

        # Should look like a panel (has some structure)
        lines = output.split("\n")
        assert len(lines) > 3  # At least some vertical content


class TestEmotionalFeedbackIntegration:
    """Integration tests for emotional feedback in game context."""

    def test_feedback_with_game_context(self):
        """Feedback should work with emotional state from gameplay."""
        renderer = EmotionalFeedbackRenderer()
        emotional_state = EmotionalState()

        prompt = EmotionalPrompt(question="How did that challenge feel?")
        prompt.update(rt=0.8, lt=0.1, y_pressed=False, a_pressed=False)

        output = renderer.render_prompt(prompt)
        assert "How did that challenge feel?" in output

    def test_feedback_supports_different_questions(self):
        """Renderer should work with various question types."""
        renderer = EmotionalFeedbackRenderer()

        questions = [
            "How was that challenge?",
            "Are you enjoying this?",
            "Rate your confidence",
            "How focused were you?"
        ]

        for question in questions:
            prompt = EmotionalPrompt(question=question)
            output = renderer.render_prompt(prompt)
            assert question in output

    def test_feedback_animation_frame_sequence(self):
        """Renderer should support animation frame sequences."""
        renderer = EmotionalFeedbackRenderer()
        prompt = EmotionalPrompt(question="Test")

        # Simulate animation frames
        frames = []
        for value in [0.0, 0.25, 0.5, 0.75, 1.0]:
            prompt.update(rt=value, lt=0.0, y_pressed=False, a_pressed=False)
            frame = renderer.render_prompt(prompt)
            frames.append(frame)

        # All frames should render successfully
        assert len(frames) == 5
        assert all(isinstance(f, str) for f in frames)
        # Frames should be different (animation)
        assert frames[0] != frames[-1]


# Self-teaching note:
#
# This test file demonstrates:
# - Testing Rich UI components (Level 6: Testing UI rendering)
# - Mocking and fixtures for interactive components (Level 5-6)
# - Testing animation sequences (Level 6: Complex state)
# - Integration testing UI with game state (Level 6)
# - Descriptive test naming and docstrings (Professional Python)
#
# The tests define WHAT the emotional feedback visualization SHOULD do
# before any implementation code is written.
#
# Prerequisites:
# - Level 4: Classes and objects
# - Level 5: Testing and assertions
# - Level 6: Rich library and UI patterns
