"""
Rich TUI Game Screen Renderer

Real-time updating game screen with Rich's Live display.
Shows challenge, code editor, test results, emotional feedback, and progress.

NO input() loops - event-driven rendering only!
"""

from dataclasses import dataclass, field
from typing import List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.progress import Progress, BarColumn, TextColumn
from rich.layout import Layout
from rich.text import Text
from rich.live import Live


@dataclass
class CursorPosition:
    """Cursor position in the code editor."""

    line: int = 0
    col: int = 0


@dataclass
class TestResult:
    """Result from running a test."""

    name: str
    passed: bool
    message: str
    details: Optional[str] = None


@dataclass
class EmotionalState:
    """Emotional feedback state from gamepad triggers."""

    enjoyment: float = 0.0  # RT (right trigger) 0.0-1.0
    frustration: float = 0.0  # LT (left trigger) 0.0-1.0
    recent_feedback: List[str] = field(default_factory=list)


@dataclass
class GameState:
    """Complete game state for rendering."""

    challenge_title: str
    challenge_description: str
    current_code: str
    test_results: List[TestResult]
    emotional_state: EmotionalState
    xp: int
    level: int
    progress: float  # 0.0-1.0


class GameScreen:
    """Rich TUI game screen renderer with live updates."""

    def __init__(self, console: Optional[Console] = None):
        """
        Initialize the game screen renderer.

        Args:
            console: Optional Rich Console (creates default if None)
        """
        self.console = console or Console()
        self.current_state: Optional[GameState] = None
        self._live: Optional[Live] = None

    def update_state(self, state: GameState) -> None:
        """
        Update the game state and trigger re-render.

        Args:
            state: New game state to display
        """
        self.current_state = state

    def render(self, state: GameState) -> Layout:
        """
        Render the complete game screen.

        Args:
            state: Game state to render

        Returns:
            Rich Layout with all panels
        """
        # Create main layout
        layout = Layout()

        # Split into header, main, footer
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=5),
        )

        # Split main into left (code) and right (info)
        layout["main"].split_row(
            Layout(name="code", ratio=3),
            Layout(name="info", ratio=2),
        )

        # Split info into challenge, tests, emotional
        layout["info"].split_column(
            Layout(name="challenge"),
            Layout(name="tests"),
            Layout(name="emotional"),
        )

        # Populate each section
        layout["header"].update(self._render_header(state))
        layout["code"].update(self._render_code_editor_panel(state))
        layout["challenge"].update(self._render_challenge_panel(state))
        layout["tests"].update(self._render_test_results_panel(state))
        layout["emotional"].update(self._render_emotional_panel(state))
        layout["footer"].update(self._render_progress_panel(state))

        return layout

    def _render_header(self, state: GameState) -> Panel:
        """Render header with title and stats."""
        header_text = Text()
        header_text.append("LMSP", style="bold cyan")
        header_text.append(" | ", style="dim")
        header_text.append(f"Level {state.level}", style="bold yellow")
        header_text.append(" | ", style="dim")
        header_text.append(f"XP: {state.xp}", style="bold green")

        return Panel(
            header_text,
            style="cyan on black",
            box=None,
        )

    def _render_challenge_panel(self, state: GameState) -> Panel:
        """Render the current challenge information."""
        content = Text()
        content.append(state.challenge_title, style="bold yellow")
        content.append("\n\n")
        content.append(state.challenge_description, style="white")

        return Panel(
            content,
            title="[bold cyan]Challenge",
            border_style="cyan",
            padding=(1, 2),
        )

    def _render_code_editor_panel(self, state: GameState) -> Panel:
        """Render code editor with syntax highlighting."""
        # Use Rich Syntax for Python code highlighting
        if state.current_code.strip():
            syntax = Syntax(
                state.current_code,
                "python",
                theme="monokai",
                line_numbers=True,
                word_wrap=False,
                background_color="#000000",
            )
        else:
            syntax = Text("# Start typing your code here...", style="dim")

        return Panel(
            syntax,
            title="[bold green]Code Editor",
            border_style="green",
            padding=(1, 1),
        )

    def _render_test_results_panel(self, state: GameState) -> Panel:
        """Render test results with visual feedback."""
        if not state.test_results:
            content = Text("No tests run yet", style="dim")
        else:
            table = Table(show_header=False, box=None, padding=0)
            table.add_column("Status", width=3)
            table.add_column("Test")

            for result in state.test_results:
                icon = "✓" if result.passed else "✗"
                color = "green" if result.passed else "red"

                table.add_row(
                    Text(icon, style=f"bold {color}"),
                    Text(result.name, style=color),
                )

            content = table

        return Panel(
            content,
            title="[bold magenta]Test Results",
            border_style="magenta",
            padding=(1, 1),
        )

    def _render_emotional_panel(self, state: GameState) -> Panel:
        """Render emotional feedback visualization."""
        emotional = state.emotional_state

        # Create bars for RT (enjoyment) and LT (frustration)
        content = Text()

        # Enjoyment bar (RT)
        enjoyment_width = int(emotional.enjoyment * 20)
        enjoyment_bar = "█" * enjoyment_width + "░" * (20 - enjoyment_width)
        content.append("😊 ", style="green")
        content.append(enjoyment_bar, style="green")
        content.append(f" {emotional.enjoyment*100:.0f}%\n", style="dim green")

        # Frustration bar (LT)
        frustration_width = int(emotional.frustration * 20)
        frustration_bar = "█" * frustration_width + "░" * (20 - frustration_width)
        content.append("😤 ", style="red")
        content.append(frustration_bar, style="red")
        content.append(f" {emotional.frustration*100:.0f}%\n", style="dim red")

        # Recent feedback
        if emotional.recent_feedback:
            content.append("\n")
            for feedback in emotional.recent_feedback[-3:]:  # Last 3
                content.append(f"💬 {feedback}\n", style="cyan")

        return Panel(
            content,
            title="[bold yellow]Emotional Feedback",
            border_style="yellow",
            padding=(1, 1),
        )

    def _render_progress_panel(self, state: GameState) -> Panel:
        """Render progress bars."""
        # XP progress to next level
        xp_to_next = 100  # Simplified
        xp_percent = (state.xp % xp_to_next) / xp_to_next

        # Challenge progress
        challenge_percent = state.progress

        content = Text()

        # XP bar
        xp_width = int(xp_percent * 40)
        xp_bar = "█" * xp_width + "░" * (40 - xp_width)
        content.append("XP: ", style="bold yellow")
        content.append(xp_bar, style="yellow")
        content.append(f" {xp_percent*100:.0f}%\n", style="dim yellow")

        # Challenge progress bar
        progress_width = int(challenge_percent * 40)
        progress_bar = "█" * progress_width + "░" * (40 - progress_width)
        content.append("Challenge: ", style="bold cyan")
        content.append(progress_bar, style="cyan")
        content.append(f" {challenge_percent*100:.0f}%", style="dim cyan")

        return Panel(
            content,
            style="blue on black",
            padding=(0, 1),
        )

    def handle_key(self, event) -> bool:
        """
        Handle keyboard input events.

        Args:
            event: Keyboard event with .key attribute

        Returns:
            True if key was handled
        """
        # This is a placeholder for keyboard event handling
        # The actual implementation would integrate with the game loop
        # and update the current_state based on key presses

        # For now, just acknowledge we received the event
        return True


# Self-teaching note:
#
# This file demonstrates:
# - Rich Live display architecture (Level 6: Real-time UI)
# - Dataclasses for structured state (Level 5: Data modeling)
# - Layout management with Rich (Level 6: Advanced UI)
# - Syntax highlighting with Rich.Syntax (Level 6: Advanced features)
# - Event-driven architecture (Level 6: No blocking I/O)
# - Panel-based composition (Level 5: UI composition)
#
# Prerequisites:
# - Level 4: Classes and objects
# - Level 5: Dataclasses, type hints
# - Level 6: Rich library, event-driven programming
#
# Key insight: NO input() calls! Everything is event-driven.
# The game loop updates the GameState, and we re-render the display.
# This creates a smooth, responsive experience that FEELS GOOD.
#
# The learner will encounter this after mastering:
# - Basic Python syntax (variables, functions)
# - Classes and objects
# - Rich library basics
# - Event-driven programming concepts
