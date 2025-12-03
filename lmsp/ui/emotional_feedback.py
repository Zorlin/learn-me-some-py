"""
Emotional Feedback Visualization with Rich

Renders gorgeous, animated displays for emotional input from controllers.
Shows RT (right trigger) and LT (left trigger) values as beautiful progress bars
with colors, animations, and integrated feedback.

When emotional prompts appear, they should feel integrated and beautiful,
not like a separate system bolted on.
"""

from dataclasses import dataclass
from typing import Optional, List
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.align import Align
from rich.progress import Progress, BarColumn, TextColumn
from rich import box

from lmsp.input.emotional import EmotionalPrompt, EmotionalState, EmotionalDimension


class ColorGradient:
    """Smooth color transitions for emotional feedback visualization."""

    def __init__(self, colors: List[str], name: str = "gradient"):
        """
        Initialize a color gradient.

        Args:
            colors: List of colors to interpolate between (hex or Rich color names)
            name: Name for the gradient
        """
        self.colors = colors
        self.name = name

    @staticmethod
    def enjoyment() -> "ColorGradient":
        """Create a gradient for enjoyment (neutral → green)."""
        return ColorGradient(
            ["dim", "yellow", "green"],
            "enjoyment"
        )

    @staticmethod
    def frustration() -> "ColorGradient":
        """Create a gradient for frustration (neutral → red)."""
        return ColorGradient(
            ["dim", "yellow", "red"],
            "frustration"
        )

    def get_color(self, value: float) -> str:
        """
        Get color at a specific value (0.0 to 1.0).

        Args:
            value: Value between 0.0 and 1.0

        Returns:
            Color name or hex code
        """
        # Clamp value to 0.0-1.0
        value = max(0.0, min(1.0, value))

        # Map value to color index
        if len(self.colors) == 1:
            return self.colors[0]

        # Interpolate between colors
        idx = value * (len(self.colors) - 1)
        lower_idx = int(idx)
        upper_idx = min(lower_idx + 1, len(self.colors) - 1)

        # For simplicity, just return the nearest color
        # In a real implementation, could do RGB interpolation
        if value < 0.5:
            return self.colors[lower_idx]
        else:
            return self.colors[upper_idx]


class ProgressBarStyle:
    """Styled progress bar rendering for emotional feedback."""

    def __init__(self, width: int = 30, color: str = "green"):
        """
        Initialize progress bar style.

        Args:
            width: Width of the bar in characters
            color: Color for filled portion (Rich color name)
        """
        self.width = width
        self.color = color

    def render(self, value: float) -> str:
        """
        Render a progress bar at a specific value.

        Args:
            value: Value between 0.0 and 1.0

        Returns:
            Styled progress bar string with Rich markup
        """
        # Clamp value to 0.0-1.0
        value = max(0.0, min(1.0, value))

        # Calculate filled/empty portions
        filled = int(value * self.width)
        empty = self.width - filled

        # Build bar with color markup
        if filled > 0:
            bar = f"[{self.color}]{'█' * filled}[/][dim]{'░' * empty}[/]"
        else:
            bar = f"[dim]{'░' * self.width}[/]"

        return bar


@dataclass
class TriggerBar:
    """Visual representation of a single trigger bar."""

    label: str  # "RT" or "LT"
    description: str  # "Happy", "Frustrated", etc.
    value: float  # 0.0 to 1.0

    def __post_init__(self):
        """Clamp value to valid range."""
        self.value = max(0.0, min(1.0, self.value))

    def render(self) -> str:
        """Render the trigger bar as a string with visual representation."""
        # Determine color based on trigger type
        if self.label == "RT":
            # Right trigger = positive emotions (enjoyment, happiness)
            color = "green" if self.value > 0.5 else "yellow" if self.value > 0.2 else "dim"
        else:
            # Left trigger = negative emotions (frustration, confusion)
            color = "red" if self.value > 0.5 else "yellow" if self.value > 0.2 else "dim"

        # Create bar visualization
        bar_width = 30
        filled = int(self.value * bar_width)
        empty = bar_width - filled

        if self.value > 0.0:
            bar = f"[{color}]{'█' * filled}[/][dim]{'░' * empty}[/]"
        else:
            bar = f"[dim]{'░' * bar_width}[/]"

        # Format: [LABEL description] [████░░░░░░░░░░░░] 0.7
        return f"  [{color}]{self.label}[/] {self.description:<15} {bar} {self.value:.1%}"


@dataclass
class FeedbackPanel:
    """A panel that displays emotional feedback beautifully."""

    question: str
    right_trigger_label: str = "Happy"
    left_trigger_label: str = "Frustrated"
    y_button_option: Optional[str] = None

    def render(self) -> str:
        """Render the entire feedback panel."""
        lines = [
            "",
            f"[bold cyan]{self.question}[/]",
            "",
            "[dim]─ Analog Emotional Input ─[/]",
            "",
        ]

        # Show trigger labels explicitly
        lines.append(f"  [bold green]RT:[/] {self.right_trigger_label}")
        lines.append(f"  [bold red]LT:[/] {self.left_trigger_label}")
        lines.append("")

        # Instructions
        lines.append("  Pull the [bold green]right trigger[/] to express happiness")
        lines.append("  Pull the [bold red]left trigger[/] to express frustration")

        if self.y_button_option:
            lines.append(f"  Press [bold]Y[/] for {self.y_button_option}")

        lines.append("  Press [bold]A[/] to confirm")
        lines.append("")

        return "\n".join(lines)


class EmotionalFeedbackRenderer:
    """
    Renders emotional feedback prompts gorgeously with Rich.

    Integrates with the game UI to show emotional input as part of
    the natural gameplay experience, not as a separate dialog.
    """

    # Emoji for feedback states
    HAPPY_EMOJI = ["😊", "😄", "🤩", "😍"]
    SAD_EMOJI = ["😞", "😤", "😠", "😤"]
    NEUTRAL_EMOJI = ["😐", "🤔", "😕"]

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()

    def render_emotional_prompt(
        self,
        prompt: EmotionalPrompt,
        title: str = "How are you feeling?",
    ) -> str:
        """
        Alias for render_prompt to match test expectations.

        Render an emotional prompt with trigger bars.

        Returns a formatted string that can be printed directly or
        integrated into a larger Rich display.
        """
        return self.render_prompt(prompt, title)

    def render_emotional_state(self, emotional_state: EmotionalState) -> str:
        """
        Alias for render_emotional_state_display to match test expectations.

        Returns a formatted string representation of the emotional state.
        """
        panel = self.render_emotional_state_display(emotional_state)
        # Convert panel to string for test compatibility
        from rich.console import Console as RichConsole
        from io import StringIO
        output = StringIO()
        temp_console = RichConsole(file=output)
        temp_console.print(panel)
        return output.getvalue()

    def render_prompt(
        self,
        prompt: EmotionalPrompt,
        title: Optional[str] = None,
    ) -> str:
        """
        Render an emotional prompt with trigger bars.

        Returns a formatted string that can be printed directly or
        integrated into a larger Rich display.
        """
        # Use prompt's question if no title provided
        display_title = title if title is not None else prompt.question

        lines = [
            "",
            f"[bold cyan]{display_title}[/]",
            "",
        ]

        # Create trigger bars
        rt_bar = TriggerBar(
            label="RT",
            description=prompt.right_trigger,
            value=prompt._rt_value,
        )

        lt_bar = TriggerBar(
            label="LT",
            description=prompt.left_trigger,
            value=prompt._lt_value,
        )

        lines.append(rt_bar.render())
        lines.append(lt_bar.render())
        lines.append("")

        # Show which dimension is active
        if prompt._rt_value > 0 or prompt._lt_value > 0:
            if prompt._rt_value > prompt._lt_value:
                lines.append(
                    f"[green]→ Expressing {EmotionalDimension.ENJOYMENT.value}[/]"
                )
            else:
                lines.append(
                    f"[red]← Expressing {EmotionalDimension.FRUSTRATION.value}[/]"
                )
        else:
            lines.append("[dim]← Pull triggers to express emotion →[/]")

        lines.append("")

        # Instructions
        if prompt.y_button and not prompt._complex_requested:
            lines.append(f"[dim]Press Y for {prompt.y_button}[/]")

        lines.append("[dim]Press A to confirm[/]")
        lines.append("")

        return "\n".join(lines)

    def render_prompt_panel(
        self,
        prompt: EmotionalPrompt,
        title: str = "Emotional Feedback",
    ) -> Panel:
        """
        Render emotional prompt as a Rich Panel.

        Perfect for integrating into a larger game UI display.
        """
        content = self.render_prompt(prompt, title)

        return Panel(
            content,
            title=title,
            border_style="cyan",
            box=box.ROUNDED,
            padding=(0, 2),
        )

    def render_with_animation(
        self,
        prompt: EmotionalPrompt,
        emotional_state: EmotionalState,
        title: str = "How are you feeling?",
    ) -> str:
        """
        Render emotional feedback with animation based on emotional state.

        Adds visual feedback based on the player's emotional patterns
        to encourage healthy engagement.
        """
        lines = []

        # Check emotional state
        enjoyment = emotional_state.get_enjoyment()
        frustration = emotional_state.get_frustration()
        in_flow = emotional_state.is_in_flow()
        needs_break = emotional_state.needs_break()

        # Header with emoji that changes based on state
        if in_flow:
            emoji = "🔥"  # In the zone!
            state_text = "[bold green]You're in flow![/]"
        elif needs_break:
            emoji = "😤"
            state_text = "[bold red]Consider taking a break[/]"
        elif enjoyment > 0.7:
            emoji = "😄"
            state_text = "[bold green]You're having fun![/]"
        elif frustration > 0.6:
            emoji = "😞"
            state_text = "[bold yellow]Feeling stuck? Ask for a hint![/]"
        else:
            emoji = "🤔"
            state_text = "[dim]How's it going?[/]"

        lines.append(f"\n{emoji} {state_text}\n")
        lines.append("[dim]─" * 20 + "[/]")

        # The prompt itself
        lines.append("")
        lines.append(self.render_prompt(prompt, title))

        return "\n".join(lines)

    def render_emotional_state_display(
        self,
        emotional_state: EmotionalState,
        title: str = "Your Emotional State",
    ) -> Panel:
        """
        Display the player's current emotional state.

        Shows rolling averages of enjoyment, frustration, and other dimensions.
        """
        lines = []

        enjoyment = emotional_state.get_enjoyment()
        frustration = emotional_state.get_frustration()
        in_flow = emotional_state.is_in_flow()
        needs_break = emotional_state.needs_break()

        # Enjoyment bar
        lines.append("[bold]Enjoyment[/]")
        enjoyment_bar = self._create_horizontal_bar(enjoyment, "green", width=40)
        lines.append(f"{enjoyment_bar} {enjoyment:.1%}")
        lines.append("")

        # Frustration bar
        lines.append("[bold]Frustration[/]")
        frustration_bar = self._create_horizontal_bar(frustration, "red", width=40)
        lines.append(f"{frustration_bar} {frustration:.1%}")
        lines.append("")

        # Status indicators
        lines.append("[bold]Status[/]")
        if in_flow:
            lines.append("  🔥 [green bold]In Flow State[/]")
        if needs_break:
            lines.append("  🛑 [red bold]Break Recommended[/]")
        if not in_flow and not needs_break:
            lines.append("  ✓ [dim]Comfortable[/]")

        content = "\n".join(lines)
        return Panel(
            content,
            title=title,
            border_style="magenta",
            box=box.ROUNDED,
            padding=(1, 2),
        )

    def _create_horizontal_bar(
        self,
        value: float,
        color: str,
        width: int = 30,
    ) -> str:
        """Create a horizontal progress bar."""
        value = max(0.0, min(1.0, value))
        filled = int(value * width)
        empty = width - filled

        if filled > 0:
            return f"[{color}]{'█' * filled}[/][dim]{'░' * empty}[/]"
        else:
            return f"[dim]{'░' * width}[/]"

    def render_combined_display(
        self,
        prompt: Optional[EmotionalPrompt] = None,
        emotional_state: Optional[EmotionalState] = None,
        challenge_title: Optional[str] = None,
    ) -> Panel:
        """
        Render a combined display with prompt, state, and context.

        Used when you want to show emotional feedback as part of
        the main game UI rather than in a popup.
        """
        lines = []

        if challenge_title:
            lines.append(f"[bold cyan]{challenge_title}[/]")
            lines.append("[dim]─" * 20 + "[/]")
            lines.append("")

        if emotional_state:
            enjoyment = emotional_state.get_enjoyment()
            frustration = emotional_state.get_frustration()
            lines.append("[bold]How you're feeling:[/]")
            lines.append(self._create_horizontal_bar(enjoyment, "green", width=20))
            lines.append(self._create_horizontal_bar(frustration, "red", width=20))
            lines.append("")

        if prompt:
            lines.append(self.render_prompt(prompt, "Feedback"))

        content = "\n".join(lines)
        return Panel(
            content,
            title="Emotional Feedback",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 2),
        )


# Self-teaching note:
#
# This file demonstrates:
# - Rich library for gorgeous terminal UI (Level 5+)
# - Panel, Text, and Table rendering (Level 5+)
# - Data classes for structured data (Level 5)
# - Dataclass post-init validation (Level 5: OOP patterns)
# - Responsive text rendering with colors (Level 4+)
# - Conditional logic for state-based display (Level 3+)
#
# Prerequisites:
# - Level 2: String formatting and colors
# - Level 3: Functions and conditional logic
# - Level 4: Classes and data structures
# - Level 5: Dataclasses and advanced OOP
# - Level 6: UI frameworks and design patterns
#
# The emotional feedback system is integrated into the game experience.
# When players see the progress bars and triggers, it should feel like
# a natural part of the game, not a separate system.
#
# Good UX is about making the experience feel integrated and whole,
# not bolted together from separate pieces.
