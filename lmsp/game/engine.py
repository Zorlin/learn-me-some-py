"""
Game Engine
===========

The main game loop that ties everything together:
- Loads challenges and concepts
- Manages the code editor
- Runs validation
- Tracks progress
- Displays results

This is the heart of LMSP - where learning becomes playing.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, Protocol, Callable
from pathlib import Path

from rich.console import Console

from lmsp.game.state import GameState, GameSession, GameEvent
from lmsp.game.renderer import RichRenderer, MinimalRenderer, Renderer
from lmsp.python.concepts import ConceptDAG, Concept
from lmsp.python.challenges import ChallengeLoader, Challenge
from lmsp.python.validator import CodeValidator, ValidationResult
from lmsp.adaptive.engine import AdaptiveEngine, LearnerProfile
from lmsp.input.emotional import EmotionalState, EmotionalPrompt, EmotionalSample, EmotionalDimension
from lmsp.ui.emotional_feedback import EmotionalFeedbackRenderer


class GamePhase(Enum):
    """Current phase of the game loop."""
    MENU = auto()
    SELECTING_CHALLENGE = auto()
    CODING = auto()
    RUNNING_TESTS = auto()
    VIEWING_RESULTS = auto()
    EMOTIONAL_FEEDBACK = auto()
    COMPLETED = auto()
    PAUSED = auto()


class InputHandler(Protocol):
    """Protocol for input handlers (keyboard, gamepad, etc.)."""

    def get_line(self, prompt: str = "") -> str:
        """Get a line of input from the user."""
        ...

    def get_char(self) -> str:
        """Get a single character (for immediate input)."""
        ...


class KeyboardInputHandler:
    """Simple keyboard input using Python's input()."""

    def get_line(self, prompt: str = "") -> str:
        """Get a line of input."""
        return input(prompt)

    def get_char(self) -> str:
        """Get a line (single char not easily available in standard Python)."""
        return input()


@dataclass
class GameConfig:
    """Configuration for the game engine."""
    concepts_dir: Path = field(default_factory=lambda: Path("concepts"))
    challenges_dir: Path = field(default_factory=lambda: Path("challenges"))
    timeout_seconds: int = 5
    auto_save: bool = True
    debug_mode: bool = False


class GameEngine:
    """
    The main game engine orchestrating all LMSP systems.

    Usage:
        engine = GameEngine(profile=profile)
        engine.run()  # Start the game loop

    Or for programmatic control:
        engine = GameEngine(profile=profile)
        engine.start_challenge("lists_basics_01")
        result = engine.submit_code(code)
    """

    def __init__(
        self,
        profile: LearnerProfile,
        config: Optional[GameConfig] = None,
        renderer: Optional[Renderer] = None,
        input_handler: Optional[InputHandler] = None,
        console: Optional[Console] = None,
    ):
        """
        Initialize the game engine.

        Args:
            profile: The learner's profile for adaptive learning
            config: Game configuration (uses defaults if None)
            renderer: Renderer for display (uses RichRenderer if None)
            input_handler: Input handler (uses KeyboardInputHandler if None)
            console: Rich console (creates one if None)
        """
        self.profile = profile
        self.config = config or GameConfig()
        self.console = console or Console()
        self.renderer = renderer or RichRenderer(self.console)
        self.input_handler = input_handler or KeyboardInputHandler()

        # Core systems
        self.adaptive_engine = AdaptiveEngine(profile)
        self.validator = CodeValidator(timeout_seconds=self.config.timeout_seconds)
        self.emotional_feedback_renderer = EmotionalFeedbackRenderer(self.console)

        # Load concepts and challenges
        self.concept_dag: Optional[ConceptDAG] = None
        self.challenge_loader: Optional[ChallengeLoader] = None
        self._load_content()

        # Current session state
        self.session: Optional[GameSession] = None
        self.current_challenge: Optional[Challenge] = None
        self.phase = GamePhase.MENU
        self.emotional_state = EmotionalState()

        # Code editor state
        self.code_buffer: list[str] = []
        self.cursor_row: int = 0
        self.cursor_col: int = 0

        # Event callbacks
        self._on_challenge_complete: list[Callable[[Challenge, ValidationResult], None]] = []
        self._running = False

    def _load_content(self):
        """Load concepts and challenges from disk."""
        # Load concepts DAG
        if self.config.concepts_dir.exists():
            self.concept_dag = ConceptDAG(self.config.concepts_dir)
            self.concept_dag.load_all()

        # Load challenges
        if self.config.challenges_dir.exists():
            self.challenge_loader = ChallengeLoader(self.config.challenges_dir)

    def run(self):
        """
        Run the main game loop.

        This is the primary entry point for playing LMSP.
        """
        self._running = True
        self.renderer.clear()
        self._show_welcome()

        while self._running:
            try:
                self._game_tick()
            except KeyboardInterrupt:
                self._running = False
                self.renderer.show_message("\nGoodbye! Keep learning!", "info")
                break
            except Exception as e:
                self.renderer.show_message(f"Error: {e}", "error")
                if self.config.debug_mode:
                    raise

    def _game_tick(self):
        """Process one tick of the game loop."""
        if self.phase == GamePhase.MENU:
            self._handle_menu()
        elif self.phase == GamePhase.SELECTING_CHALLENGE:
            self._handle_challenge_selection()
        elif self.phase == GamePhase.CODING:
            self._handle_coding()
        elif self.phase == GamePhase.RUNNING_TESTS:
            self._handle_running_tests()
        elif self.phase == GamePhase.VIEWING_RESULTS:
            self._handle_viewing_results()
        elif self.phase == GamePhase.EMOTIONAL_FEEDBACK:
            self._handle_emotional_feedback()
        elif self.phase == GamePhase.COMPLETED:
            self._handle_completed()

    def _show_welcome(self):
        """Display welcome message."""
        self.renderer.show_message("Welcome to LMSP - Learn Me Some Py!", "success")
        self.renderer.show_message(f"Player: {self.profile.player_id}", "info")

        if self.concept_dag:
            total_concepts = len(self.concept_dag.concepts)
            mastered = len([k for k, v in self.profile.mastery_levels.items() if v >= 3])
            self.renderer.show_message(
                f"Progress: {mastered}/{total_concepts} concepts mastered",
                "info"
            )

    def _handle_menu(self):
        """Handle main menu."""
        self.console.print("\n[bold cyan]Main Menu[/bold cyan]")
        self.console.print("1. Start Learning (recommended challenge)")
        self.console.print("2. Select Challenge")
        self.console.print("3. View Progress")
        self.console.print("4. Quit")

        choice = self.input_handler.get_line("\nChoice: ").strip()

        if choice == "1":
            self._start_recommended()
        elif choice == "2":
            self.phase = GamePhase.SELECTING_CHALLENGE
        elif choice == "3":
            self._show_progress()
        elif choice == "4":
            self._running = False
        else:
            self.renderer.show_message("Invalid choice", "warning")

    def _start_recommended(self):
        """Start the recommended challenge from adaptive engine."""
        rec = self.adaptive_engine.recommend_next()
        self.renderer.render_recommendation(rec)

        if rec.challenge_id:
            self.start_challenge(rec.challenge_id)
        elif rec.concept:
            # Find a challenge for this concept
            if self.concept_dag:
                concept = self.concept_dag.get_concept(rec.concept)
                if concept and concept.challenge_starter:
                    self.start_challenge(concept.challenge_starter)
                else:
                    self.renderer.show_message(
                        f"No challenge found for concept: {rec.concept}",
                        "warning"
                    )
                    self.phase = GamePhase.SELECTING_CHALLENGE
        else:
            self.renderer.show_message(rec.reason or "No recommendation", "info")
            self.phase = GamePhase.SELECTING_CHALLENGE

    def _handle_challenge_selection(self):
        """Handle challenge selection screen."""
        self.console.print("\n[bold cyan]Select Challenge[/bold cyan]")

        if not self.challenge_loader:
            self.renderer.show_message("No challenges loaded", "error")
            self.phase = GamePhase.MENU
            return

        # List available challenges by level
        all_challenges = self.challenge_loader.list_challenges()

        if not all_challenges:
            self.renderer.show_message("No challenges available", "warning")
            self.phase = GamePhase.MENU
            return

        # Group by level
        by_level: dict[int, list[str]] = {}
        for cid in all_challenges:
            challenge = self.challenge_loader.load(cid)
            if challenge:
                level = challenge.level
                if level not in by_level:
                    by_level[level] = []
                by_level[level].append(cid)

        # Display grouped challenges
        for level in sorted(by_level.keys()):
            self.console.print(f"\n[bold]Level {level}:[/bold]")
            for cid in by_level[level][:5]:  # Show first 5 per level
                challenge = self.challenge_loader.load(cid)
                if challenge:
                    self.console.print(f"  - {cid}: {challenge.name}")
            if len(by_level[level]) > 5:
                self.console.print(f"  ... and {len(by_level[level]) - 5} more")

        self.console.print("\n[dim]Enter challenge ID or 'back' to return[/dim]")
        choice = self.input_handler.get_line("Challenge: ").strip()

        if choice.lower() == "back":
            self.phase = GamePhase.MENU
        elif choice in all_challenges:
            self.start_challenge(choice)
        else:
            self.renderer.show_message(f"Challenge not found: {choice}", "warning")

    def start_challenge(self, challenge_id: str):
        """
        Start a specific challenge.

        Args:
            challenge_id: ID of the challenge to start
        """
        if not self.challenge_loader:
            self.renderer.show_message("No challenge loader", "error")
            return

        challenge = self.challenge_loader.load(challenge_id)
        if not challenge:
            self.renderer.show_message(f"Challenge not found: {challenge_id}", "error")
            return

        self.current_challenge = challenge
        self.session = GameSession(
            player_id=self.profile.player_id,
            challenge_id=challenge_id
        )
        self.session.start()

        # Initialize code buffer with skeleton
        self.code_buffer = challenge.skeleton_code.split("\n")
        self.cursor_row = len(self.code_buffer) - 1
        self.cursor_col = 0

        # Display challenge
        self.renderer.render_challenge(challenge)
        self.phase = GamePhase.CODING

    def _handle_coding(self):
        """Handle the coding phase."""
        if not self.current_challenge or not self.session:
            self.phase = GamePhase.MENU
            return

        # Show current code
        current_code = "\n".join(self.code_buffer)
        self.renderer.render_code_editor(current_code, (self.cursor_row, self.cursor_col))

        self.console.print("\n[bold]Commands:[/bold]")
        self.console.print("  [cyan]edit[/cyan] - Edit code line by line")
        self.console.print("  [cyan]run[/cyan]  - Run tests")
        self.console.print("  [cyan]hint[/cyan] - Get a hint")
        self.console.print("  [cyan]quit[/cyan] - Return to menu")

        cmd = self.input_handler.get_line("\nCommand: ").strip().lower()

        if cmd == "edit":
            self._edit_code()
        elif cmd == "run":
            self.phase = GamePhase.RUNNING_TESTS
        elif cmd == "hint":
            self._show_hint()
        elif cmd == "quit":
            self.phase = GamePhase.MENU
        elif cmd.startswith("line "):
            # Quick line edit: "line 5 print('hello')"
            self._quick_line_edit(cmd)
        else:
            self.renderer.show_message(f"Unknown command: {cmd}", "warning")

    def _edit_code(self):
        """Enter line-by-line editing mode."""
        self.console.print("\n[bold]Line Editor[/bold]")
        self.console.print("[dim]Enter line number to edit, 'add' to add line, 'del N' to delete, 'done' to finish[/dim]")

        while True:
            # Show current code with line numbers
            for i, line in enumerate(self.code_buffer):
                self.console.print(f"  {i+1:3}: {line}")

            cmd = self.input_handler.get_line("\nLine: ").strip()

            if cmd.lower() == "done":
                break
            elif cmd.lower() == "add":
                new_line = self.input_handler.get_line("New line: ")
                self.code_buffer.append(new_line)
            elif cmd.lower().startswith("del "):
                try:
                    line_num = int(cmd[4:]) - 1
                    if 0 <= line_num < len(self.code_buffer):
                        del self.code_buffer[line_num]
                    else:
                        self.renderer.show_message("Invalid line number", "warning")
                except ValueError:
                    self.renderer.show_message("Invalid line number", "warning")
            else:
                try:
                    line_num = int(cmd) - 1
                    if 0 <= line_num < len(self.code_buffer):
                        self.console.print(f"Current: {self.code_buffer[line_num]}")
                        new_content = self.input_handler.get_line("New content: ")
                        self.code_buffer[line_num] = new_content
                    else:
                        self.renderer.show_message("Invalid line number", "warning")
                except ValueError:
                    self.renderer.show_message("Enter a line number or command", "warning")

        # Record the code change
        if self.session:
            current_code = "\n".join(self.code_buffer)
            self.session.state.current_code = current_code
            self.session.record_event(GameEvent.CODE_CHANGE, {"code": current_code})

    def _quick_line_edit(self, cmd: str):
        """Handle quick line edit: 'line N content'."""
        parts = cmd.split(" ", 2)
        if len(parts) < 3:
            self.renderer.show_message("Usage: line N content", "warning")
            return

        try:
            line_num = int(parts[1]) - 1
            content = parts[2]

            # Extend buffer if needed
            while len(self.code_buffer) <= line_num:
                self.code_buffer.append("")

            self.code_buffer[line_num] = content

            if self.session:
                current_code = "\n".join(self.code_buffer)
                self.session.state.current_code = current_code
                self.session.record_event(GameEvent.CODE_CHANGE, {"code": current_code})

        except ValueError:
            self.renderer.show_message("Invalid line number", "warning")

    def _show_hint(self):
        """Show a hint for the current challenge."""
        if not self.current_challenge or not self.session:
            return

        self.session.state.hints_used += 1
        hint_level = min(self.session.state.hints_used, 3)

        hint = self.current_challenge.hints.get(f"level_{hint_level}")
        if hint:
            self.console.print(f"\n[yellow]Hint {hint_level}:[/yellow] {hint}")
        else:
            self.console.print(f"\n[yellow]Hint:[/yellow] No more hints available")

        if self.session:
            self.session.record_event(GameEvent.HINT_USED, {"level": hint_level})

    def _handle_running_tests(self):
        """Run tests on the current code."""
        if not self.current_challenge or not self.session:
            self.phase = GamePhase.MENU
            return

        current_code = "\n".join(self.code_buffer)
        self.console.print("\n[bold cyan]Running tests...[/bold cyan]")

        # Validate the code
        result = self.validator.validate(current_code, self.current_challenge.test_cases)

        # Update session state
        self.session.state.tests_passing = result.tests_passing
        self.session.state.tests_total = result.tests_total
        self.session.record_event(
            GameEvent.TEST_PASS if result.success else GameEvent.TEST_FAIL,
            {"passing": result.tests_passing, "total": result.tests_total}
        )

        # Store result for next phase
        self._last_result = result
        self.phase = GamePhase.VIEWING_RESULTS

    def _handle_viewing_results(self):
        """Display test results."""
        result = getattr(self, "_last_result", None)
        if not result:
            self.phase = GamePhase.CODING
            return

        self.renderer.render_test_results(result)

        if result.success:
            self.console.print("\n[bold green]Challenge Complete![/bold green]")
            self.phase = GamePhase.EMOTIONAL_FEEDBACK
        else:
            self.console.print("\n[dim]Press Enter to continue editing[/dim]")
            self.input_handler.get_line()
            self.phase = GamePhase.CODING

    def _handle_emotional_feedback(self):
        """Gather emotional feedback after completing a challenge."""
        if not self.current_challenge or not self.session:
            self.phase = GamePhase.MENU
            return

        # Create emotional prompt
        prompt = EmotionalPrompt(
            question="How did that feel?",
            right_trigger="Satisfying / Fun",
            left_trigger="Frustrating / Confusing"
        )

        self.console.print("\n[bold]How was that challenge?[/bold]")
        self.console.print("Rate from 0-10:")
        self.console.print("  Enjoyment (0=frustrated, 10=loved it):")

        try:
            enjoyment_str = self.input_handler.get_line("  > ").strip()
            enjoyment = float(enjoyment_str) / 10.0 if enjoyment_str else 0.5
            enjoyment = max(0.0, min(1.0, enjoyment))
        except ValueError:
            enjoyment = 0.5

        self.console.print("  Difficulty (0=too easy, 10=too hard):")
        try:
            difficulty_str = self.input_handler.get_line("  > ").strip()
            difficulty = float(difficulty_str) / 10.0 if difficulty_str else 0.5
            difficulty = max(0.0, min(1.0, difficulty))
        except ValueError:
            difficulty = 0.5

        # Record emotional state
        self.emotional_state.record(EmotionalSample(enjoyment))
        if difficulty > 0.7:
            self.emotional_state.record(EmotionalSample(1.0 - difficulty, dimension="frustration"))

        # Update adaptive engine
        duration = self.session.get_duration().total_seconds()
        self.adaptive_engine.record_attempt(
            concept_id=self.current_challenge.prerequisites[0] if self.current_challenge.prerequisites else "general",
            success=True,
            time_seconds=duration,
            hints_used=self.session.state.hints_used,
            enjoyment=enjoyment
        )

        if self.session:
            self.session.record_event(
                GameEvent.EMOTION_RECORDED,
                {"enjoyment": enjoyment, "difficulty": difficulty}
            )
            self.session.record_event(GameEvent.CHALLENGE_COMPLETE)

        # Notify callbacks
        result = getattr(self, "_last_result", None)
        if result:
            for callback in self._on_challenge_complete:
                callback(self.current_challenge, result)

        self.phase = GamePhase.COMPLETED

    def _handle_completed(self):
        """Handle challenge completion."""
        rec = self.adaptive_engine.recommend_next()
        self.renderer.render_recommendation(rec)

        self.console.print("\n[bold]What's next?[/bold]")
        self.console.print("1. Next challenge")
        self.console.print("2. Return to menu")

        choice = self.input_handler.get_line("Choice: ").strip()

        if choice == "1":
            if rec.challenge_id:
                self.start_challenge(rec.challenge_id)
            else:
                self.phase = GamePhase.SELECTING_CHALLENGE
        else:
            self.phase = GamePhase.MENU

    def _show_progress(self):
        """Display player's progress."""
        self.console.print("\n[bold cyan]Your Progress[/bold cyan]")

        if not self.concept_dag:
            self.renderer.show_message("No concepts loaded", "warning")
            return

        # Show mastery by level
        for level in range(7):
            concepts = self.concept_dag.get_concepts_by_level(level)
            if not concepts:
                continue

            mastered = [c for c in concepts if self.profile.mastery_levels.get(c.id, 0) >= 3]
            self.console.print(
                f"  Level {level}: {len(mastered)}/{len(concepts)} concepts mastered"
            )

        # Show unlockable concepts
        mastered_ids = {k for k, v in self.profile.mastery_levels.items() if v >= 3}
        unlockable = self.concept_dag.get_unlockable(mastered_ids)

        if unlockable:
            self.console.print("\n[bold]Ready to Learn:[/bold]")
            for cid in unlockable[:5]:
                concept = self.concept_dag.get_concept(cid)
                if concept:
                    self.console.print(f"  - {concept.name}")

        self.console.print("\n[dim]Press Enter to continue[/dim]")
        self.input_handler.get_line()

    def submit_code(self, code: str) -> ValidationResult:
        """
        Submit code for validation (programmatic API).

        Args:
            code: Python code to validate

        Returns:
            ValidationResult with test outcomes
        """
        if not self.current_challenge:
            raise ValueError("No active challenge")

        return self.validator.validate(code, self.current_challenge.test_cases)

    def on_challenge_complete(self, callback: Callable[[Challenge, ValidationResult], None]):
        """Register a callback for challenge completion."""
        self._on_challenge_complete.append(callback)

    def stop(self):
        """Stop the game loop."""
        self._running = False


# Self-teaching note:
#
# This file demonstrates:
# - State machine pattern for game phases (GamePhase enum)
# - Dependency injection (renderer, input_handler, console)
# - Protocol for input abstraction (InputHandler)
# - Event callbacks for extensibility
# - Composition over inheritance (combining systems)
# - Dataclass for configuration (GameConfig)
# - Optional chaining and None handling
# - List comprehensions for filtering
# - Rich console integration
#
# The learner will encounter this after mastering:
# - Level 4: Enums, state machines
# - Level 5: Classes, dataclasses, protocols
# - Level 6: Design patterns, architecture
#
# Key concepts demonstrated:
# 1. Game loop pattern - tick-based update cycle
# 2. State machine - clean phase transitions
# 3. Separation of concerns - renderer, validator, engine are separate
# 4. Configuration object - centralized settings
# 5. Callback pattern - extensibility without inheritance
#
# This is the HEART of LMSP - where all systems come together.
