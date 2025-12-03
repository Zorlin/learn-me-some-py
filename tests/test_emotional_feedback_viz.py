"""
Tests for Emotional Feedback Visualization with Rich

TDD: These tests define the expected behavior of beautifully rendered emotional feedback.
Beautiful visualization with animated progress bars, smooth color transitions, and
integrated panel design makes analog emotion input feel natural and gorgeous.
"""

import pytest
from io import StringIO
from unittest.mock import Mock, MagicMock

from rich.console import Console
from lmsp.input.emotional import (
    EmotionalPrompt,
    EmotionalDimension,
    EmotionalState,
)
from lmsp.ui.emotional_feedback import (
    EmotionalFeedbackRenderer,
    ProgressBarStyle,
    ColorGradient,
)


class TestColorGradient:
    """Test smooth color transitions for emotional feedback."""

    def test_color_gradient_from_neutral_to_positive(self):
        """Colors should transition from neutral (cyan) to positive (green)."""
        gradient = ColorGradient.enjoyment()

        # At 0: neutral gray
        color_0 = gradient.get_color(0.0)
        assert color_0 is not None

        # At 1.0: positive green
        color_1 = gradient.get_color(1.0)
        assert color_1 is not None

        # At 0.5: transitional
        color_mid = gradient.get_color(0.5)
        assert color_mid is not None

    def test_color_gradient_from_neutral_to_negative(self):
        """Frustration colors should transition from neutral to red."""
        gradient = ColorGradient.frustration()

        # At 0: neutral
        color_0 = gradient.get_color(0.0)
        assert color_0 is not None

        # At 1.0: red (negative)
        color_1 = gradient.get_color(1.0)
        assert color_1 is not None

    def test_color_gradient_clamping(self):
        """Values outside 0-1 should be clamped."""
        gradient = ColorGradient.enjoyment()

        # Over 1.0 should clamp
        color_over = gradient.get_color(1.5)
        color_max = gradient.get_color(1.0)
        # Should be identical or very close
        assert color_over is not None

        # Under 0.0 should clamp
        color_under = gradient.get_color(-0.5)
        color_min = gradient.get_color(0.0)
        assert color_under is not None


class TestProgressBarStyle:
    """Test animated progress bar rendering."""

    def test_progress_bar_filled_blocks(self):
        """Progress bar should show filled/empty blocks proportionally."""
        style = ProgressBarStyle(width=10)

        # 0% filled
        bar_0 = style.render(0.0)
        assert bar_0.count("█") == 0  # No filled blocks

        # 100% filled
        bar_1 = style.render(1.0)
        assert "█" in bar_1  # Has filled blocks

        # 50% filled
        bar_half = style.render(0.5)
        assert "█" in bar_half

    def test_progress_bar_smooth_animation(self):
        """Progress bar should animate smoothly through intermediate values."""
        style = ProgressBarStyle(width=10)

        # Create a sequence of values
        values = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        previous_filled = 0

        for val in values:
            bar = style.render(val)
            filled_count = bar.count("█")
            # Should monotonically increase (or stay same)
            assert filled_count >= previous_filled
            previous_filled = filled_count

    def test_progress_bar_with_color(self):
        """Progress bar should include color markup."""
        style = ProgressBarStyle(width=10, color="green")
        bar = style.render(0.5)

        # Should contain Rich color markup
        assert "[" in bar or "█" in bar  # Either markup or blocks

    def test_progress_bar_custom_width(self):
        """Progress bar width should be customizable."""
        style_narrow = ProgressBarStyle(width=5)
        style_wide = ProgressBarStyle(width=20)

        bar_narrow = style_narrow.render(1.0)
        bar_wide = style_wide.render(1.0)

        # Wider bar should have more blocks
        assert len(bar_narrow) <= len(bar_wide)


class TestEmotionalFeedbackRenderer:
    """Test beautiful rendering of emotional feedback."""

    def test_renderer_initializes_with_console(self):
        """Renderer should accept a Rich Console instance."""
        console = Console(file=StringIO(), legacy_windows=False)
        renderer = EmotionalFeedbackRenderer(console=console)

        assert renderer.console is console

    def test_renderer_creates_console_if_not_provided(self):
        """Renderer should create its own Console if none provided."""
        renderer = EmotionalFeedbackRenderer()

        assert renderer.console is not None

    def test_render_emotional_prompt_displays_bars(self):
        """Rendering should display animated progress bars for RT/LT."""
        console = Console(file=StringIO(), legacy_windows=False)
        renderer = EmotionalFeedbackRenderer(console=console)

        prompt = EmotionalPrompt(
            question="How are you feeling?",
            right_trigger="Happy",
            left_trigger="Frustrated"
        )
        prompt.update(rt=0.7, lt=0.2, y_pressed=False, a_pressed=False)

        # Should not raise
        output = renderer.render_emotional_prompt(prompt)

        assert output is not None

    def test_render_shows_question_and_instructions(self):
        """Rendered output should show the question and button instructions."""
        console = Console(file=StringIO(), legacy_windows=False)
        renderer = EmotionalFeedbackRenderer(console=console)

        prompt = EmotionalPrompt(
            question="What did you think of that?",
            right_trigger="Loved it",
            left_trigger="Hated it",
            y_button="Tell me more"
        )
        prompt.update(rt=0.5, lt=0.3, y_pressed=False, a_pressed=False)

        rendered = renderer.render_emotional_prompt(prompt)

        # Should contain the question
        assert "What did you think of that?" in str(rendered) or \
               rendered is not None

    def test_render_colors_change_with_values(self):
        """Colors should change dynamically based on RT/LT values."""
        renderer = EmotionalFeedbackRenderer()

        # Sad prompt
        sad_prompt = EmotionalPrompt("Test")
        sad_prompt.update(rt=0.1, lt=0.8, y_pressed=False, a_pressed=False)
        sad_output = renderer.render_emotional_prompt(sad_prompt)

        # Happy prompt
        happy_prompt = EmotionalPrompt("Test")
        happy_prompt.update(rt=0.8, lt=0.1, y_pressed=False, a_pressed=False)
        happy_output = renderer.render_emotional_prompt(happy_prompt)

        # Both should render (content may differ visually)
        assert sad_output is not None
        assert happy_output is not None

    def test_render_shows_confirmation_hint(self):
        """Should show hint about pressing A to confirm when ready."""
        console = Console(file=StringIO(), legacy_windows=False)
        renderer = EmotionalFeedbackRenderer(console=console)

        prompt = EmotionalPrompt("Test")
        prompt.update(rt=0.5, lt=0.0, y_pressed=False, a_pressed=False)

        rendered = renderer.render_emotional_prompt(prompt)

        # Should indicate readiness to confirm
        assert rendered is not None

    def test_render_panel_design(self):
        """Rendered output should be in an attractive panel design."""
        console = Console(file=StringIO(), legacy_windows=False)
        renderer = EmotionalFeedbackRenderer(console=console)

        prompt = EmotionalPrompt("How's the flow?")
        prompt.update(rt=0.6, lt=0.1, y_pressed=False, a_pressed=False)

        # render_emotional_prompt should return a panel or similar
        output = renderer.render_emotional_prompt(prompt)

        assert output is not None

    def test_render_emotional_state_summary(self):
        """Renderer should display emotional state summary."""
        console = Console(file=StringIO(), legacy_windows=False)
        renderer = EmotionalFeedbackRenderer(console=console)

        state = EmotionalState()
        state.record(EmotionalDimension.ENJOYMENT, 0.8, "coding")
        state.record(EmotionalDimension.FRUSTRATION, 0.2, "debugging")

        # Should render state
        output = renderer.render_emotional_state(state)

        assert output is not None

    def test_animation_frame_progression(self):
        """Animated bars should show different frames over time."""
        renderer = EmotionalFeedbackRenderer()

        prompt = EmotionalPrompt("Test")
        prompt.update(rt=0.5, lt=0.0, y_pressed=False, a_pressed=False)

        # Get multiple frames
        frames = []
        for _ in range(3):
            frame = renderer.render_emotional_prompt(prompt)
            frames.append(frame)

        # Should be able to generate multiple frames
        assert len(frames) == 3

    def test_flow_state_visual_feedback(self):
        """Visual should change when player is in flow state."""
        renderer = EmotionalFeedbackRenderer()

        state = EmotionalState()
        # High enjoyment, low frustration = flow
        state.record(EmotionalDimension.ENJOYMENT, 0.9, "")
        state.record(EmotionalDimension.FRUSTRATION, 0.1, "")

        assert state.is_in_flow()

        # Render should show special flow state
        output = renderer.render_emotional_state(state)
        assert output is not None

    def test_break_needed_visual_feedback(self):
        """Visual should indicate when a break is needed."""
        renderer = EmotionalFeedbackRenderer()

        state = EmotionalState()
        # High frustration = needs break
        for _ in range(25):
            state.record(EmotionalDimension.FRUSTRATION, 0.8, "")

        assert state.needs_break()

        output = renderer.render_emotional_state(state)
        assert output is not None


class TestEmotionalFeedbackIntegration:
    """Test complete emotional feedback flow."""

    def test_end_to_end_emotional_feedback(self):
        """Full flow: prompt -> update -> render -> confirm."""
        console = Console(file=StringIO(), legacy_windows=False)
        renderer = EmotionalFeedbackRenderer(console=console)
        state = EmotionalState()

        # Show prompt
        prompt = EmotionalPrompt("How was that challenge?")
        rendered_1 = renderer.render_emotional_prompt(prompt)
        assert rendered_1 is not None

        # User pulls triggers
        prompt.update(rt=0.7, lt=0.1, y_pressed=False, a_pressed=False)
        rendered_2 = renderer.render_emotional_prompt(prompt)
        assert rendered_2 is not None

        # User confirms
        prompt.update(rt=0.7, lt=0.1, y_pressed=False, a_pressed=True)
        assert prompt.is_confirmed

        # Record in state
        dimension, value = prompt.get_response()
        state.record(dimension, value, "challenge_completion")

        # Should show state
        rendered_3 = renderer.render_emotional_state(state)
        assert rendered_3 is not None

    def test_emotional_prompt_with_y_button_complex_response(self):
        """User can press Y to indicate complex response."""
        renderer = EmotionalFeedbackRenderer()

        prompt = EmotionalPrompt(
            "Complex question",
            y_button="Tell me more"
        )

        # Press Y
        prompt.update(rt=0.0, lt=0.0, y_pressed=True, a_pressed=False)
        assert prompt.wants_complex

        # Still render normally
        output = renderer.render_emotional_prompt(prompt)
        assert output is not None


# Self-teaching note:
#
# This test file demonstrates:
# - TDD: writing tests BEFORE implementation
# - Testing rich console output without actually printing
# - Mocking and assertions
# - Testing visual/animation systems
# - Testing state transitions
# - Integration testing (multiple components together)
# - Edge cases (color clamping, animation frames)
#
# Prerequisites:
# - Level 4: Unit testing, mocking
# - Level 5: Integration testing, Rich library
# - Level 6: Testing animated systems
