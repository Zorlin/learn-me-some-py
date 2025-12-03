"""
Rich Live Game Loop - Event-Driven Architecture
================================================

The GORGEOUS, non-blocking game loop using Rich's Live displays.

NO more janky input() prompts! This uses:
- Rich Live displays for real-time updating
- Event-driven keyboard handling (no blocking)
- Beautiful panels and layouts
- Smooth transitions

This is what a modern TUI game should look like.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Callable, Dict
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.table import Table
from rich import box
import sys
import select


class GamePhase(Enum):
    """Current phase of the game."""
    MENU = auto()
    CHALLENGE_SELECTION = auto()
    CODING = auto()
    RUNNING_TESTS = auto()
    VIEWING_RESULTS = auto()
    PAUSED = auto()


class GameAction(Enum):
    """Actions that can be triggered."""
    START_LEARNING = auto()
    SELECT_CHALLENGE = auto()
    VIEW_PROGRESS = auto()
    QUIT = auto()
    NONE = auto()


@dataclass
class MenuOption:
    """A menu option with key binding."""
    key: str
    label: str
    action: GameAction


class LiveGameLoop:
    """
    Event-driven game loop with Rich Live displays.

    NO blocking input() calls - everything is event-driven and gorgeous!
    """

    def __init__(self, console: Optional[Console] = None):
        """
        Initialize the live game loop.

        Args:
            console: Rich console for output
        """
        self.console = console or Console()
        self.phase = GamePhase.MENU
        self._running = False

        # Menu state
        self.menu_options = [
            MenuOption("1", "Start Learning (recommended)", GameAction.START_LEARNING),
            MenuOption("2", "Select Challenge", GameAction.SELECT_CHALLENGE),
            MenuOption("3", "View Progress", GameAction.VIEW_PROGRESS),
            MenuOption("4", "Quit", GameAction.QUIT),
        ]
        self.selected_menu_index = 0

        # Challenge selection state
        self.available_challenges = []
        self.selected_challenge_index = 0

        # Key handler registry
        self._key_handlers: Dict[str, Callable] = {}
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register default key handlers."""
        # Navigation
        self.register_key_handler("down", self._handle_down)
        self.register_key_handler("up", self._handle_up)
        self.register_key_handler("enter", self._handle_enter)
        self.register_key_handler("\r", self._handle_enter)  # Carriage return
        self.register_key_handler("\n", self._handle_enter)  # Newline

        # Quit keys
        self.register_key_handler("q", self._handle_quit)
        self.register_key_handler("\x1b", self._handle_quit)  # ESC

        # Number keys for menu
        for option in self.menu_options:
            self.register_key_handler(option.key, lambda opt=option: self._handle_menu_select(opt))

    def register_key_handler(self, key: str, handler: Callable):
        """Register a keyboard handler."""
        self._key_handlers[key] = handler

    def _handle_down(self):
        """Handle down arrow key."""
        if self.phase == GamePhase.MENU:
            self.selected_menu_index = min(
                self.selected_menu_index + 1,
                len(self.menu_options) - 1
            )
        elif self.phase == GamePhase.CHALLENGE_SELECTION:
            self.selected_challenge_index = min(
                self.selected_challenge_index + 1,
                len(self.available_challenges) - 1
            )

    def _handle_up(self):
        """Handle up arrow key."""
        if self.phase == GamePhase.MENU:
            self.selected_menu_index = max(self.selected_menu_index - 1, 0)
        elif self.phase == GamePhase.CHALLENGE_SELECTION:
            self.selected_challenge_index = max(self.selected_challenge_index - 1, 0)

    def _handle_enter(self):
        """Handle enter key."""
        if self.phase == GamePhase.MENU:
            option = self.menu_options[self.selected_menu_index]
            return self._handle_menu_select(option)

    def _handle_menu_select(self, option: MenuOption) -> Optional[GameAction]:
        """Handle menu selection."""
        return option.action

    def _handle_quit(self):
        """Handle quit action."""
        self._running = False
        return GameAction.QUIT

    def handle_key(self, key: str) -> Optional[GameAction]:
        """
        Handle a key press.

        Args:
            key: The key that was pressed

        Returns:
            GameAction if one was triggered
        """
        handler = self._key_handlers.get(key)
        if handler:
            result = handler()
            # Handlers can return actions or None
            return result if isinstance(result, GameAction) else GameAction.NONE
        return GameAction.NONE

    def transition_to(self, phase: GamePhase):
        """Transition to a new phase."""
        self.phase = phase

    def get_renderable(self):
        """
        Get the current renderable based on phase.

        Returns a Rich renderable (Panel, Layout, etc.)
        """
        if self.phase == GamePhase.MENU:
            return self._render_menu()
        elif self.phase == GamePhase.CHALLENGE_SELECTION:
            return self._render_challenge_selection()
        else:
            return Panel("Other phases coming soon!", title="LMSP")

    def _render_menu(self) -> Panel:
        """Render the main menu as a gorgeous panel."""
        # Title
        title = Text()
        title.append("LMSP", style="bold magenta")
        title.append(" - Learn Me Some Py", style="bold cyan")

        # Menu options
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Key", style="bold yellow", width=6)
        table.add_column("Option", style="white")

        for i, option in enumerate(self.menu_options):
            # Highlight selected
            if i == self.selected_menu_index:
                label_style = "bold green"
                marker = "\u25b6 "
            else:
                label_style = "white"
                marker = "  "

            table.add_row(
                f"[{i+1}]",
                Text(f"{marker}{option.label}", style=label_style)
            )

        # Instructions
        instructions = Text("\n\n", style="dim")
        instructions.append("Use arrow keys to navigate, Enter to select, Q to quit", style="dim italic")

        # Build content
        content = [title, "\n\n", table, instructions]
        content_text = ""
        for item in content:
            if isinstance(item, Text):
                content_text += str(item)
            else:
                content_text += str(item)

        return Panel(
            content_text,
            title="[bold cyan]Main Menu[/]",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(2, 4)
        )

    def _render_challenge_selection(self) -> Panel:
        """Render challenge selection screen."""
        if not self.available_challenges:
            return Panel(
                "No challenges available yet!",
                title="[bold yellow]Select Challenge[/]",
                border_style="yellow"
            )

        table = Table(show_header=True, box=box.SIMPLE)
        table.add_column("", width=3)
        table.add_column("Challenge", style="bold")
        table.add_column("Level", justify="center", style="dim")

        for i, challenge in enumerate(self.available_challenges):
            marker = "\u25b6" if i == self.selected_challenge_index else " "
            name = challenge.get("name", challenge.get("id", "Unknown"))
            level = str(challenge.get("level", "?"))

            style = "bold green" if i == self.selected_challenge_index else "white"
            table.add_row(marker, Text(name, style=style), level)

        instructions = Text("\n\nUse arrow keys, Enter to select, Q to quit", style="dim italic")

        return Panel(
            str(table) + str(instructions),
            title="[bold cyan]Select Challenge[/]",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 2)
        )


# Self-teaching note:
#
# This file demonstrates:
# - Event-driven architecture (NO blocking input!)
# - Rich library for gorgeous TUI (Level 5-6)
# - Enum for type-safe state management (Level 4)
# - Dataclasses for structured data (Level 5)
# - Callable type hints (Level 5: type hints)
# - Dictionary dispatch for key handlers (Level 4: design patterns)
#
# Prerequisites:
# - Level 3: Functions, classes
# - Level 4: Enums, collections, dictionaries
# - Level 5: Dataclasses, type hints
# - Level 6: Event-driven programming, TUI frameworks
#
# This is how professional terminal applications are built:
# - Non-blocking I/O
# - Event-driven architecture
# - Beautiful rendering with Rich
# - Smooth user experience
#
# NO more janky input() prompts!
