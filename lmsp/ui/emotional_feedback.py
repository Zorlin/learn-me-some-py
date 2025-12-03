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
class FeedbackPanel:\n    \"\"\"A panel that displays emotional feedback beautifully.\"\"\"\n\n    question: str\n    right_trigger_label: str = \"Happy\"\n    left_trigger_label: str = \"Frustrated\"\n    y_button_option: Optional[str] = None\n\n    def render(self) -> str:\n        \"\"\"Render the entire feedback panel.\"\"\"\n        lines = [\n            \"\",\n            f\"[bold cyan]{self.question}[/]\",\n            \"\",\n            \"[dim]─ Analog Emotional Input ─[/]\",\n            \"\",\n        ]\n\n        # Instructions\n        lines.append(\"  Pull the [bold green]right trigger[/] to express happiness\")\n        lines.append(\"  Pull the [bold red]left trigger[/] to express frustration\")\n\n        if self.y_button_option:\n            lines.append(f\"  Press [bold]Y[/] for {self.y_button_option}\")\n\n        lines.append(\"  Press [bold]A[/] to confirm\")\n        lines.append(\"\")\n\n        return \"\\n\".join(lines)\n\n\nclass EmotionalFeedbackRenderer:\n    \"\"\"\n    Renders emotional feedback prompts gorgeously with Rich.\n\n    Integrates with the game UI to show emotional input as part of\n    the natural gameplay experience, not as a separate dialog.\n    \"\"\"\n\n    # Emoji for feedback states\n    HAPPY_EMOJI = [\"😊\", \"😄\", \"🤩\", \"😍\"]\n    SAD_EMOJI = [\"😞\", \"😤\", \"😠\", \"😤\"]\n    NEUTRAL_EMOJI = [\"😐\", \"🤔\", \"😕\"]\n\n    def __init__(self, console: Optional[Console] = None):\n        self.console = console or Console()\n\n    def render_prompt(\n        self,\n        prompt: EmotionalPrompt,\n        title: str = \"How are you feeling?\",\n    ) -> str:\n        \"\"\"\n        Render an emotional prompt with trigger bars.\n\n        Returns a formatted string that can be printed directly or\n        integrated into a larger Rich display.\n        \"\"\"\n        lines = [\n            \"\",\n            f\"[bold cyan]{title}[/]\",\n            \"\",\n        ]\n\n        # Create trigger bars\n        rt_bar = TriggerBar(\n            label=\"RT\",\n            description=prompt.right_trigger,\n            value=prompt._rt_value,\n        )\n\n        lt_bar = TriggerBar(\n            label=\"LT\",\n            description=prompt.left_trigger,\n            value=prompt._lt_value,\n        )\n\n        lines.append(rt_bar.render())\n        lines.append(lt_bar.render())\n        lines.append(\"\")\n\n        # Show which dimension is active\n        if prompt._rt_value > 0 or prompt._lt_value > 0:\n            if prompt._rt_value > prompt._lt_value:\n                lines.append(\n                    f\"[green]→ Expressing {EmotionalDimension.ENJOYMENT.value}[/]\"\n                )\n            else:\n                lines.append(\n                    f\"[red]← Expressing {EmotionalDimension.FRUSTRATION.value}[/]\"\n                )\n        else:\n            lines.append(\"[dim]← Pull triggers to express emotion →[/]\")\n\n        lines.append(\"\")\n\n        # Instructions\n        if prompt.y_button and not prompt._complex_requested:\n            lines.append(f\"[dim]Press Y for {prompt.y_button}[/]\")\n\n        lines.append(\"[dim]Press A to confirm[/]\")\n        lines.append(\"\")\n\n        return \"\\n\".join(lines)\n\n    def render_prompt_panel(\n        self,\n        prompt: EmotionalPrompt,\n        title: str = \"Emotional Feedback\",\n    ) -> Panel:\n        \"\"\"\n        Render emotional prompt as a Rich Panel.\n\n        Perfect for integrating into a larger game UI display.\n        \"\"\"\n        content = self.render_prompt(prompt, title)\n\n        return Panel(\n            content,\n            title=title,\n            border_style=\"cyan\",\n            box=box.ROUNDED,\n            padding=(0, 2),\n        )\n\n    def render_with_animation(\n        self,\n        prompt: EmotionalPrompt,\n        emotional_state: EmotionalState,\n        title: str = \"How are you feeling?\",\n    ) -> str:\n        \"\"\"\n        Render emotional feedback with animation based on emotional state.\n\n        Adds visual feedback based on the player's emotional patterns\n        to encourage healthy engagement.\n        \"\"\"\n        lines = []\n\n        # Check emotional state\n        enjoyment = emotional_state.get_enjoyment()\n        frustration = emotional_state.get_frustration()\n        in_flow = emotional_state.is_in_flow()\n        needs_break = emotional_state.needs_break()\n\n        # Header with emoji that changes based on state\n        if in_flow:\n            emoji = \"🔥\"  # In the zone!\n            state_text = \"[bold green]You're in flow![/]\"\n        elif needs_break:\n            emoji = \"😤\"\n            state_text = \"[bold red]Consider taking a break[/]\"\n        elif enjoyment > 0.7:\n            emoji = \"😄\"\n            state_text = \"[bold green]You're having fun![/]\"\n        elif frustration > 0.6:\n            emoji = \"😞\"\n            state_text = \"[bold yellow]Feeling stuck? Ask for a hint![/]\"\n        else:\n            emoji = \"🤔\"\n            state_text = \"[dim]How's it going?[/]\"\n\n        lines.append(f\"\\n{emoji} {state_text}\\n\")\n        lines.append(\"[dim]─\" * 20 + \"[/]\")\n\n        # The prompt itself\n        lines.append(\"\")\n        lines.append(self.render_prompt(prompt, title))\n\n        return \"\\n\".join(lines)\n\n    def render_emotional_state_display(\n        self,\n        emotional_state: EmotionalState,\n        title: str = \"Your Emotional State\",\n    ) -> Panel:\n        \"\"\"\n        Display the player's current emotional state.\n\n        Shows rolling averages of enjoyment, frustration, and other dimensions.\n        \"\"\"\n        lines = []\n\n        enjoyment = emotional_state.get_enjoyment()\n        frustration = emotional_state.get_frustration()\n        in_flow = emotional_state.is_in_flow()\n        needs_break = emotional_state.needs_break()\n\n        # Enjoyment bar\n        lines.append(\"[bold]Enjoyment[/]\")\n        enjoyment_bar = self._create_horizontal_bar(enjoyment, \"green\", width=40)\n        lines.append(f\"{enjoyment_bar} {enjoyment:.1%}\")\n        lines.append(\"\")\n\n        # Frustration bar\n        lines.append(\"[bold]Frustration[/]\")\n        frustration_bar = self._create_horizontal_bar(frustration, \"red\", width=40)\n        lines.append(f\"{frustration_bar} {frustration:.1%}\")\n        lines.append(\"\")\n\n        # Status indicators\n        lines.append(\"[bold]Status[/]\")\n        if in_flow:\n            lines.append(\"  🔥 [green bold]In Flow State[/]\")\n        if needs_break:\n            lines.append(\"  🛑 [red bold]Break Recommended[/]\")\n        if not in_flow and not needs_break:\n            lines.append(\"  ✓ [dim]Comfortable[/]\")\n\n        content = \"\\n\".join(lines)\n        return Panel(\n            content,\n            title=title,\n            border_style=\"magenta\",\n            box=box.ROUNDED,\n            padding=(1, 2),\n        )\n\n    def _create_horizontal_bar(\n        self,\n        value: float,\n        color: str,\n        width: int = 30,\n    ) -> str:\n        \"\"\"Create a horizontal progress bar.\"\"\"\n        value = max(0.0, min(1.0, value))\n        filled = int(value * width)\n        empty = width - filled\n\n        if filled > 0:\n            return f\"[{color}]{'█' * filled}[/][dim]{'░' * empty}[/]\"\n        else:\n            return f\"[dim]{'░' * width}[/]\"\n\n    def render_combined_display(\n        self,\n        prompt: Optional[EmotionalPrompt] = None,\n        emotional_state: Optional[EmotionalState] = None,\n        challenge_title: Optional[str] = None,\n    ) -> Panel:\n        \"\"\"\n        Render a combined display with prompt, state, and context.\n\n        Used when you want to show emotional feedback as part of\n        the main game UI rather than in a popup.\n        \"\"\"\n        lines = []\n\n        if challenge_title:\n            lines.append(f\"[bold cyan]{challenge_title}[/]\")\n            lines.append(\"[dim]─\" * 20 + \"[/]\")\n            lines.append(\"\")\n\n        if emotional_state:\n            enjoyment = emotional_state.get_enjoyment()\n            frustration = emotional_state.get_frustration()\n            lines.append(\"[bold]How you're feeling:[/]\")\n            lines.append(self._create_horizontal_bar(enjoyment, \"green\", width=20))\n            lines.append(self._create_horizontal_bar(frustration, \"red\", width=20))\n            lines.append(\"\")\n\n        if prompt:\n            lines.append(self.render_prompt(prompt, \"Feedback\"))\n\n        content = \"\\n\".join(lines)\n        return Panel(\n            content,\n            title=\"Emotional Feedback\",\n            border_style=\"cyan\",\n            box=box.ROUNDED,\n            padding=(1, 2),\n        )\n\n\n# Self-teaching note:\n#\n# This file demonstrates:\n# - Rich library for gorgeous terminal UI (Level 5+)\n# - Panel, Text, and Table rendering (Level 5+)\n# - Data classes for structured data (Level 5)\n# - Dataclass post-init validation (Level 5: OOP patterns)\n# - Responsive text rendering with colors (Level 4+)\n# - Conditional logic for state-based display (Level 3+)\n#\n# Prerequisites:\n# - Level 2: String formatting and colors\n# - Level 3: Functions and conditional logic\n# - Level 4: Classes and data structures\n# - Level 5: Dataclasses and advanced OOP\n# - Level 6: UI frameworks and design patterns\n#\n# The emotional feedback system is integrated into the game experience.\n# When players see the progress bars and triggers, it should feel like\n# a natural part of the game, not a separate system.\n#\n# Good UX is about making the experience feel integrated and whole,\n# not bolted together from separate pieces.\n"