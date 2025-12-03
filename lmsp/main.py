"""
LMSP Main Entry Point
=====================

The command-line interface and entry point for the game.

Usage:
    lmsp                                  # Start with keyboard, default player
    lmsp --input gamepad                  # Use gamepad
    lmsp --player-id Wings                # Set player name
    lmsp --challenge lists-basic-01       # Start specific challenge
    lmsp --multiplayer --mode coop        # Multiplayer cooperative mode
"""

import argparse
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from lmsp.adaptive.engine import AdaptiveEngine, LearnerProfile


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """
    Parse command-line arguments.

    Args:
        args: List of arguments to parse (defaults to sys.argv[1:])

    Returns:
        Parsed argument namespace
    """
    parser = argparse.ArgumentParser(
        prog="lmsp",
        description="Learn Me Some Py - The game that teaches you to build it",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  lmsp                              Start with keyboard
  lmsp --input gamepad              Use gamepad controller
  lmsp --player-id Wings            Set player name
  lmsp --challenge loops-01         Start specific challenge
  lmsp --multiplayer --mode coop    Play cooperatively
        """
    )

    parser.add_argument(
        "--input",
        choices=["keyboard", "gamepad"],
        default="keyboard",
        help="Input method (default: keyboard)"
    )

    parser.add_argument(
        "--player-id",
        type=str,
        default=None,
        help="Player name/ID for profile tracking"
    )

    parser.add_argument(
        "--challenge",
        type=str,
        default=None,
        help="Start with specific challenge ID"
    )

    parser.add_argument(
        "--multiplayer",
        action="store_true",
        help="Enable multiplayer mode"
    )

    parser.add_argument(
        "--mode",
        choices=["coop", "race", "teach", "spectate"],
        default="coop",
        help="Multiplayer mode (default: coop)"
    )

    return parser.parse_args(args)


def create_profile_path(player_id: str | None) -> Path:
    """
    Create the path to a player's profile file.

    Args:
        player_id: Player identifier (None for default)

    Returns:
        Path to profile JSON file
    """
    # Use default profile if no player ID
    if player_id is None:
        player_id = "default"

    # Sanitize player ID for filename (replace invalid chars with _)
    safe_id = "".join(c if c.isalnum() else "_" for c in player_id)

    # Profile directory: ~/.local/share/lmsp/profiles/
    profile_dir = Path.home() / ".local" / "share" / "lmsp" / "profiles"
    profile_dir.mkdir(parents=True, exist_ok=True)

    return profile_dir / f"{safe_id}.json"


def load_or_create_profile(profile_path: Path, player_id: str) -> LearnerProfile:
    """
    Load existing profile or create a new one.

    Args:
        profile_path: Path to profile file
        player_id: Player identifier

    Returns:
        LearnerProfile instance
    """
    if profile_path.exists():
        # Load existing profile
        profile_data = profile_path.read_text()
        profile = LearnerProfile.from_json(profile_data)
        return profile
    else:
        # Create new profile
        profile = LearnerProfile(player_id=player_id)
        # Save immediately
        profile_path.write_text(profile.to_json())
        return profile


def display_welcome(console: Console, profile: LearnerProfile, input_mode: str):
    """
    Display welcome message with Rich formatting.

    Args:
        console: Rich console for output
        profile: Player's learner profile
        input_mode: Input method being used
    """
    # Create welcome text
    welcome_text = Text()
    welcome_text.append("Welcome to ", style="bold cyan")
    welcome_text.append("LMSP", style="bold magenta")
    welcome_text.append("\n\n")
    welcome_text.append("The game that teaches you to build it", style="italic")

    # Player info
    player_info = Text()
    player_info.append(f"\nPlayer: ", style="bold")
    player_info.append(f"{profile.player_id}\n", style="bold yellow")
    player_info.append(f"Input: ", style="bold")
    player_info.append(f"{input_mode.capitalize()}\n", style="bold green")

    # Mastery stats
    if profile.mastery_levels:
        concepts_mastered = len([m for m in profile.mastery_levels.values() if m >= 3])
        player_info.append(f"Concepts Mastered: ", style="bold")
        player_info.append(f"{concepts_mastered}\n", style="bold blue")

    # Display in panel
    console.print(Panel(welcome_text, border_style="cyan"))
    console.print(player_info)


def main() -> int:
    """
    Main entry point for LMSP.

    Returns:
        Exit code (0 for success)
    """
    # Parse arguments
    args = parse_args()

    # Initialize Rich console
    console = Console()

    # Determine player ID
    player_id = args.player_id if args.player_id else "default"

    # Load or create profile
    profile_path = create_profile_path(args.player_id)
    profile = load_or_create_profile(profile_path, player_id)

    # Display welcome message
    display_welcome(console, profile, args.input)

    # Import GameEngine here to avoid circular imports
    from lmsp.game import GameEngine, GameConfig, KeyboardInputHandler
    from lmsp.game.renderer import RichRenderer

    # Create game configuration
    config = GameConfig(
        timeout_seconds=5,
        auto_save=True,
        debug_mode=False,
    )

    # Create input handler based on --input flag
    if args.input == "gamepad":
        try:
            from lmsp.input.gamepad import GamepadInputHandler
            input_handler = GamepadInputHandler()
        except ImportError:
            console.print("[yellow]Gamepad support not available, using keyboard[/yellow]")
            input_handler = KeyboardInputHandler()
    else:
        input_handler = KeyboardInputHandler()

    # Create game engine
    game_engine = GameEngine(
        profile=profile,
        config=config,
        renderer=RichRenderer(),
        input_handler=input_handler,
        console=console,
    )

    # Check for specific challenge
    if args.challenge:
        console.print(f"\n[bold cyan]Starting challenge:[/bold cyan] {args.challenge}")
        try:
            game_engine.start_challenge(args.challenge)
        except ValueError as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            return 1

    # Check for multiplayer
    if args.multiplayer:
        console.print(
            f"\n[bold magenta]Multiplayer mode:[/bold magenta] {args.mode.upper()}"
        )
        # TODO: Initialize multiplayer session
        console.print("[dim]Multiplayer support coming in Phase 4[/dim]")
        return 0

    # Run the game loop
    try:
        console.print("\n[bold yellow]Game loop starting...[/bold yellow]")
        console.print("[dim]Press Ctrl+C to exit[/dim]\n")
        game_engine.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]Game paused. See you next time![/yellow]")
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        if args.input == "gamepad":
            console.print("[dim]Try using keyboard mode for debugging[/dim]")
        return 1
    finally:
        # Save profile before exit
        profile_path.write_text(profile.to_json())

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        console = Console()
        console.print("\n[yellow]See you next time![/yellow]")
        sys.exit(0)


# Self-teaching note:
#
# This file demonstrates:
# - Command-line argument parsing with argparse (Level 2: Functions and modules)
# - Type hints with Optional and Union (Professional Python)
# - Path manipulation with pathlib (Standard library, Level 3+)
# - Rich console formatting for beautiful terminal output (Level 4+)
# - Entry point pattern with main() and __name__ == "__main__" (Level 2+)
# - Try/except for graceful error handling (Level 3: Error handling)
# - System integration (sys.exit, sys.argv) (Level 4+)
#
# Prerequisites:
# - Functions and arguments (Level 2)
# - Dictionaries and default values (Level 2)
# - File I/O (Level 3)
# - Object-oriented basics (Level 3-4)
#
# The learner will write this AFTER understanding these concepts,
# making this both the game's entry point AND a teaching moment.
