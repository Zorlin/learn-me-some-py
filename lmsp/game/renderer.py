"""
TUI Renderer
============

Handles all visual output for the LMSP game using Rich for beautiful console UI.

This module provides:
- Renderer protocol (interface) for different rendering backends
- RichRenderer for beautiful, colorful console output
- MinimalRenderer for testing and simple text output
- Helper functions for formatting game elements

The renderer is responsible for ALL visual output - if it appears on screen,
it comes through here.
"""

from abc import ABC, abstractmethod
from typing import Protocol
from io import StringIO

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.progress import BarColumn, Progress
from rich.text import Text

from lmsp.python.challenges import Challenge
from lmsp.python.validator import ValidationResult, TestResult
from lmsp.input.emotional import EmotionalPrompt
from lmsp.adaptive.engine import AdaptiveRecommendation


class Renderer(Protocol):
    """
    Protocol defining the renderer interface.

    All renderers must implement these methods to be compatible with the game loop.
    This allows swapping rendering backends (Rich, Textual, plain text, etc.)
    """

    def render_challenge(self, challenge: Challenge) -> None:
        """Display a challenge to the player."""
        ...

    def render_code_editor(self, code: str, cursor: tuple[int, int]) -> None:
        """Display the code editor with current code and cursor position."""
        ...

    def render_test_results(self, results: ValidationResult) -> None:
        """Display test results after running code."""
        ...

    def render_emotional_prompt(self, prompt: EmotionalPrompt) -> None:
        """Display an emotional feedback prompt."""
        ...

    def render_recommendation(self, rec: AdaptiveRecommendation) -> None:
        """Display the adaptive engine's recommendation."""
        ...

    def show_message(self, msg: str, style: str = "info") -> None:
        """Show a message to the player."""
        ...

    def clear(self) -> None:
        """Clear the display."""
        ...


class RichRenderer:
    """
    Beautiful console renderer using Rich.

    This is the default renderer for LMSP, providing:
    - Syntax-highlighted code
    - Color-coded test results
    - Beautiful panels and tables
    - Progress bars for emotional input
    - Responsive layout that adapts to terminal width
    """

    def __init__(self, console: Console | None = None):
        """
        Initialize the Rich renderer.

        Args:
            console: Optional Rich Console instance. If None, creates a new one.
        """
        self.console = console or Console()

    def render_challenge(self, challenge: Challenge) -> None:
        """Display a challenge."""
        self.console.print()

        # Challenge header
        header = Panel(
            f"[bold cyan]{challenge.name}[/bold cyan]\n"
            f"[dim]Level {challenge.level} • {challenge.id}[/dim]",
            border_style="cyan"
        )
        self.console.print(header)

        # Brief description
        self.console.print(f"\n{challenge.description_brief}\n")

        # Detailed description in a panel
        if challenge.description_detailed:
            details = Panel(
                challenge.description_detailed,
                title="[bold]Details[/bold]",
                border_style="blue"
            )
            self.console.print(details)

        # Skeleton code
        self.console.print("\n[bold]Starter Code:[/bold]")
        syntax = Syntax(
            challenge.skeleton_code,
            "python",
            theme="monokai",
            line_numbers=True
        )
        self.console.print(syntax)
        self.console.print()

    def render_code_editor(self, code: str, cursor: tuple[int, int]) -> None:
        """Display the code editor."""
        row, col = cursor

        # Syntax-highlighted code
        syntax = Syntax(
            code,
            "python",
            theme="monokai",
            line_numbers=True,
            highlight_lines={row + 1}  # Highlight cursor line (1-indexed)
        )

        panel = Panel(
            syntax,
            title=f"[bold]Code Editor[/bold] [dim]Cursor: {row}:{col}[/dim]",
            border_style="green"
        )
        self.console.print(panel)

    def render_test_results(self, results: ValidationResult) -> None:
        """Display test results."""
        self.console.print()

        # Overall status
        if results.success:
            status = Text("✓ ALL TESTS PASSED!", style="bold green")
        elif results.error:
            status = Text(f"✗ ERROR: {results.error}", style="bold red")
        else:
            status = Text(
                f"✗ {results.tests_passing}/{results.tests_total} tests passing",
                style="bold yellow"
            )

        self.console.print(Panel(status, border_style="bold"))

        # Test results table
        if results.test_results:
            table = Table(show_header=True, header_style="bold")
            table.add_column("Test", style="cyan")
            table.add_column("Status", justify="center")
            table.add_column("Expected", style="dim")
            table.add_column("Actual", style="dim")

            for test in results.test_results:
                if test.passed:
                    status_icon = "[green]✓ PASS[/green]"
                    expected_str = str(test.expected)
                    actual_str = str(test.actual)
                else:
                    status_icon = "[red]✗ FAIL[/red]"
                    expected_str = f"[yellow]{test.expected}[/yellow]"
                    if test.error:
                        actual_str = f"[red]ERROR: {test.error}[/red]"
                    else:
                        actual_str = f"[red]{test.actual}[/red]"

                table.add_row(test.test_name, status_icon, expected_str, actual_str)

            self.console.print(table)

        # Output (if any)
        if results.output:
            output_panel = Panel(
                results.output,
                title="[bold]Output[/bold]",
                border_style="dim"
            )
            self.console.print(output_panel)

        # Timing
        self.console.print(f"\n[dim]Completed in {results.time_seconds:.2f}s[/dim]\n")

    def render_emotional_prompt(self, prompt: EmotionalPrompt) -> None:
        """Display an emotional feedback prompt."""
        self.console.print()

        # Question
        self.console.print(f"[bold cyan]{prompt.question}[/bold cyan]\n")

        # Right trigger (positive)
        rt_value = prompt._rt_value
        rt_bar = "█" * int(rt_value * 20)
        rt_empty = "░" * (20 - int(rt_value * 20))
        self.console.print(
            f"  [green]RT[/green] [{rt_bar}{rt_empty}] [dim]{prompt.right_trigger}[/dim]"
        )

        # Left trigger (negative)
        lt_value = prompt._lt_value
        lt_bar = "█" * int(lt_value * 20)
        lt_empty = "░" * (20 - int(lt_value * 20))
        self.console.print(
            f"  [red]LT[/red] [{lt_bar}{lt_empty}] [dim]{prompt.left_trigger}[/dim]"
        )

        # Y button (complex response)
        if prompt.y_button:
            self.console.print(f"\n  [yellow]Y[/yellow] {prompt.y_button}")

        # Confirm button
        self.console.print(f"\n  [cyan]A[/cyan] [dim]Confirm[/dim]\n")

    def render_recommendation(self, rec: AdaptiveRecommendation) -> None:
        """Display an adaptive recommendation."""
        self.console.print()

        # Action type styling
        action_styles = {
            "challenge": "cyan",
            "review": "yellow",
            "break": "magenta",
            "project_step": "green"
        }
        style = action_styles.get(rec.action, "white")

        # Content
        content = []
        content.append(f"[bold {style}]{rec.action.upper()}[/bold {style}]")

        if rec.concept:
            content.append(f"\nConcept: [cyan]{rec.concept}[/cyan]")

        if rec.challenge_id:
            content.append(f"Challenge: [dim]{rec.challenge_id}[/dim]")

        if rec.reason:
            content.append(f"\n{rec.reason}")

        # Confidence meter
        confidence_bar = "█" * int(rec.confidence * 10)
        confidence_empty = "░" * (10 - int(rec.confidence * 10))
        content.append(
            f"\n[dim]Confidence: [{confidence_bar}{confidence_empty}] "
            f"{rec.confidence * 100:.0f}%[/dim]"
        )

        panel = Panel(
            "\n".join(content),
            title="[bold]Recommended Next Step[/bold]",
            border_style=style
        )
        self.console.print(panel)
        self.console.print()

    def show_message(self, msg: str, style: str = "info") -> None:
        """Show a message."""
        style_map = {
            "info": ("blue", "ℹ"),
            "success": ("green", "✓"),
            "warning": ("yellow", "⚠"),
            "error": ("red", "✗")
        }

        color, icon = style_map.get(style, ("white", "•"))
        self.console.print(f"[{color}]{icon}[/{color}] {msg}")

    def clear(self) -> None:
        """Clear the console."""
        self.console.clear()


class MinimalRenderer:
    """
    Minimal text-only renderer for testing.

    This renderer outputs plain text without Rich formatting,
    making it useful for:
    - Unit tests (no ANSI codes to deal with)
    - Headless environments
    - Debugging
    - CI/CD pipelines
    """

    def __init__(self):
        """Initialize the minimal renderer."""
        self._buffer = StringIO()

    def render_challenge(self, challenge: Challenge) -> None:
        """Display a challenge (plain text)."""
        self._buffer.write("=" * 60 + "\n")
        self._buffer.write(f"CHALLENGE: {challenge.name}\n")
        self._buffer.write(f"Level {challenge.level} • {challenge.id}\n")
        self._buffer.write("=" * 60 + "\n\n")
        self._buffer.write(f"{challenge.description_brief}\n\n")

        if challenge.description_detailed:
            self._buffer.write("Details:\n")
            self._buffer.write(f"{challenge.description_detailed}\n\n")

        self._buffer.write("Starter Code:\n")
        self._buffer.write("-" * 60 + "\n")
        self._buffer.write(challenge.skeleton_code + "\n")
        self._buffer.write("-" * 60 + "\n\n")

    def render_code_editor(self, code: str, cursor: tuple[int, int]) -> None:
        """Display the code editor (plain text)."""
        row, col = cursor
        self._buffer.write("CODE EDITOR\n")
        self._buffer.write(f"Cursor: ({row}, {col})\n")
        self._buffer.write("-" * 60 + "\n")
        self._buffer.write(code + "\n")
        self._buffer.write("-" * 60 + "\n\n")

    def render_test_results(self, results: ValidationResult) -> None:
        """Display test results (plain text)."""
        self._buffer.write("\n")
        self._buffer.write("=" * 60 + "\n")

        if results.success:
            self._buffer.write("✓ ALL TESTS PASSED!\n")
        elif results.error:
            self._buffer.write(f"✗ ERROR: {results.error}\n")
        else:
            self._buffer.write(
                f"✗ {results.tests_passing}/{results.tests_total} tests passing\n"
            )

        self._buffer.write("=" * 60 + "\n\n")

        # Test results
        for test in results.test_results:
            formatted = format_test_result(test)
            self._buffer.write(formatted + "\n")

        # Output
        if results.output:
            self._buffer.write("\nOutput:\n")
            self._buffer.write(results.output + "\n")

        # Timing
        self._buffer.write(f"\nCompleted in {results.time_seconds:.2f}s\n\n")

    def render_emotional_prompt(self, prompt: EmotionalPrompt) -> None:
        """Display an emotional prompt (plain text)."""
        self._buffer.write("\n")
        self._buffer.write(f"{prompt.question}\n\n")

        rt_bar = "█" * int(prompt._rt_value * 10)
        self._buffer.write(f"  [RT {rt_bar:10}] {prompt.right_trigger}\n")

        lt_bar = "█" * int(prompt._lt_value * 10)
        self._buffer.write(f"  [LT {lt_bar:10}] {prompt.left_trigger}\n")

        if prompt.y_button:
            self._buffer.write(f"  [Y] {prompt.y_button}\n")

        self._buffer.write("\n  Press A to confirm\n\n")

    def render_recommendation(self, rec: AdaptiveRecommendation) -> None:
        """Display a recommendation (plain text)."""
        self._buffer.write("\n")
        self._buffer.write("=" * 60 + "\n")
        self._buffer.write(f"RECOMMENDED: {rec.action.upper()}\n")
        self._buffer.write("=" * 60 + "\n")

        if rec.concept:
            self._buffer.write(f"Concept: {rec.concept}\n")

        if rec.challenge_id:
            self._buffer.write(f"Challenge: {rec.challenge_id}\n")

        if rec.reason:
            self._buffer.write(f"\n{rec.reason}\n")

        confidence_bar = "█" * int(rec.confidence * 10)
        self._buffer.write(f"\nConfidence: [{confidence_bar:10}] {rec.confidence * 100:.0f}%\n\n")

    def show_message(self, msg: str, style: str = "info") -> None:
        """Show a message (plain text)."""
        prefix = {
            "info": "[INFO]",
            "success": "[SUCCESS]",
            "warning": "[WARNING]",
            "error": "[ERROR]"
        }
        self._buffer.write(f"{prefix.get(style, '[MSG]')} {msg}\n")

    def clear(self) -> None:
        """Clear the buffer."""
        self._buffer = StringIO()

    def get_output(self) -> str:
        """Get the accumulated output (for testing)."""
        return self._buffer.getvalue()


def format_test_result(result: TestResult) -> str:
    """
    Format a test result as a string.

    Args:
        result: TestResult to format

    Returns:
        Formatted string representation
    """
    if result.passed:
        return f"  ✓ PASS: {result.test_name}"
    elif result.error:
        return (
            f"  ✗ ERROR: {result.test_name}\n"
            f"    {result.error}"
        )
    else:
        return (
            f"  ✗ FAIL: {result.test_name}\n"
            f"    Expected: {result.expected}\n"
            f"    Actual: {result.actual}"
        )


def format_hint(hint: str, level: int) -> str:
    """
    Format a hint with level indicator.

    Args:
        hint: The hint text
        level: Hint level (1 = gentle nudge, 3 = explicit solution)

    Returns:
        Formatted hint string
    """
    indicators = {
        1: "💡",
        2: "🔍",
        3: "🎯"
    }
    indicator = indicators.get(level, "💭")
    return f"{indicator} Hint (Level {level}): {hint}"


# Self-teaching note:
#
# This file demonstrates:
# - Protocols for interface definitions (Level 6: Advanced typing)
# - Abstract base classes (ABC) vs Protocols (Level 6)
# - Dependency injection (passing Console instance)
# - Rich library for beautiful console output (External library)
# - String formatting with f-strings (Level 2)
# - Optional parameters with defaults (Level 3)
# - Buffer pattern (StringIO for testing)
# - Type hints with | for unions (Python 3.10+)
#
# The learner will encounter this after mastering:
# - Classes and methods (Level 5)
# - Type hints (Level 4+)
# - External libraries (Level 6)
#
# Key concepts demonstrated:
# 1. Protocol vs ABC - when to use each
# 2. Separation of concerns - rendering logic isolated from game logic
# 3. Testability - MinimalRenderer makes testing easy
# 4. Rich library patterns - Console, Panel, Table, Syntax
# 5. String formatting strategies (plain vs Rich markup)
#
# This is how we make the game BEAUTIFUL while keeping it testable.
