"""
Radial Thumbstick Typing System
================================

The innovation: Two thumbsticks = 256 chord combinations = fast text input.

         ╭───────────╮                    ╭───────────╮
         │     ↑     │                    │     ↑     │
         │   (def)   │                    │  (space)  │
         │           │                    │           │
     ╭───┼───────────┼───╮            ╭───┼───────────┼───╮
     │ ← │     ●     │ → │            │ ← │     ●     │ → │
     │(if)│ L-STICK  │(in)│            │(:) │ R-STICK  │(=) │
     │   │           │   │            │   │           │   │
     ╰───┼───────────┼───╯            ╰───┼───────────┼───╯
         │     ↓     │                    │     ↓     │
         │ (return)  │                    │  (enter)  │
         ╰───────────╯                    ╰───────────╯

CHORD EXAMPLES:
  L-Up + R-Up       = "def "
  L-Up + R-Right    = "def "
  L-Left + R-Right  = "if "
  L-Down + R-Down   = newline + auto-indent
  L-Center + R-Center = space
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, Dict, List, Callable
import math
import time


class Direction(Enum):
    """8-direction + center for thumbstick position."""
    CENTER = auto()
    UP = auto()
    UP_RIGHT = auto()
    RIGHT = auto()
    DOWN_RIGHT = auto()
    DOWN = auto()
    DOWN_LEFT = auto()
    LEFT = auto()
    UP_LEFT = auto()


class RenderMode(Enum):
    """Rendering modes for radial menu."""
    ASCII = auto()
    RICH = auto()


class TrainingDifficulty(Enum):
    """Difficulty levels for muscle memory training."""
    BEGINNER = auto()
    INTERMEDIATE = auto()
    ADVANCED = auto()
    EXPERT = auto()


def detect_direction(x: float, y: float, deadzone: float = 0.3) -> Direction:
    """
    Detect direction from thumbstick X/Y values.

    Args:
        x: Horizontal axis (-1.0 to 1.0)
        y: Vertical axis (-1.0 to 1.0)
        deadzone: Minimum magnitude to register (default 0.3)

    Returns:
        Direction enum value
    """
    # Check if within deadzone
    magnitude = math.sqrt(x * x + y * y)
    if magnitude < deadzone:
        return Direction.CENTER

    # Calculate angle in degrees (0 = right, 90 = up)
    angle = math.degrees(math.atan2(y, x))

    # Normalize angle to 0-360
    if angle < 0:
        angle += 360

    # Map angle to direction (8 segments of 45 degrees each)
    # Each direction covers 45 degrees, centered on its axis
    if 337.5 <= angle or angle < 22.5:
        return Direction.RIGHT
    elif 22.5 <= angle < 67.5:
        return Direction.UP_RIGHT
    elif 67.5 <= angle < 112.5:
        return Direction.UP
    elif 112.5 <= angle < 157.5:
        return Direction.UP_LEFT
    elif 157.5 <= angle < 202.5:
        return Direction.LEFT
    elif 202.5 <= angle < 247.5:
        return Direction.DOWN_LEFT
    elif 247.5 <= angle < 292.5:
        return Direction.DOWN
    elif 292.5 <= angle < 337.5:
        return Direction.DOWN_RIGHT

    return Direction.CENTER


@dataclass(frozen=True)
class Chord:
    """
    A chord is a combination of left and right stick directions.

    Frozen dataclass makes it hashable for use as dict keys.
    """
    left: Direction
    right: Direction

    def __hash__(self):
        return hash((self.left, self.right))

    def __eq__(self, other):
        if not isinstance(other, Chord):
            return False
        return self.left == other.left and self.right == other.right


def get_keyword_mappings() -> Dict[Chord, str]:
    """
    Get the default chord-to-keyword mappings.

    Priority:
    1. Python keywords (def, if, for, while, return, class, etc.)
    2. Operators (=, ==, !=, <, >, <=, >=, +, -, *, /)
    3. Brackets/delimiters ((, ), [, ], {, }, :, ,)
    4. Common variable names (i, j, x, n, self, value)
    5. Special (space, newline, tab)
    """
    D = Direction  # Shorthand

    mappings = {
        # ========== Python Keywords (L-stick dominant) ==========
        # L-Up combinations = definition keywords
        Chord(D.UP, D.UP): "def ",
        Chord(D.UP, D.RIGHT): "class ",
        Chord(D.UP, D.DOWN): "class ",
        Chord(D.UP, D.LEFT): "async ",

        # L-Down combinations = flow control
        Chord(D.DOWN, D.CENTER): "return ",
        Chord(D.DOWN, D.UP): "for ",
        Chord(D.DOWN, D.DOWN): "while ",
        Chord(D.DOWN, D.RIGHT): "break",
        Chord(D.DOWN, D.LEFT): "continue",

        # L-Left combinations = conditionals
        Chord(D.LEFT, D.RIGHT): "if ",
        Chord(D.LEFT, D.CENTER): "elif ",
        Chord(D.LEFT, D.LEFT): "else:",
        Chord(D.LEFT, D.UP): "try:",
        Chord(D.LEFT, D.DOWN): "except ",

        # L-Right combinations = logical/import
        Chord(D.RIGHT, D.LEFT): "in ",
        Chord(D.RIGHT, D.RIGHT): "import ",
        Chord(D.RIGHT, D.UP): "from ",
        Chord(D.RIGHT, D.DOWN): "as ",
        Chord(D.RIGHT, D.CENTER): "and ",

        # ========== Operators (R-stick dominant) ==========
        # Center L + R direction = operators
        Chord(D.CENTER, D.RIGHT): "=",
        Chord(D.CENTER, D.LEFT): ":",
        Chord(D.CENTER, D.UP): "+",
        Chord(D.CENTER, D.DOWN): "-",

        # Diagonals for comparison
        Chord(D.UP_RIGHT, D.UP_RIGHT): "==",
        Chord(D.UP_LEFT, D.UP_LEFT): "!=",
        Chord(D.DOWN_RIGHT, D.DOWN_RIGHT): ">=",
        Chord(D.DOWN_LEFT, D.DOWN_LEFT): "<=",
        Chord(D.UP_RIGHT, D.DOWN_RIGHT): ">",
        Chord(D.UP_LEFT, D.DOWN_LEFT): "<",

        # Math operators
        Chord(D.UP_RIGHT, D.UP): "*",
        Chord(D.UP_RIGHT, D.DOWN): "/",
        Chord(D.UP_RIGHT, D.LEFT): "%",
        Chord(D.UP_RIGHT, D.RIGHT): "**",

        # ========== Brackets/Delimiters ==========
        Chord(D.DOWN_RIGHT, D.UP): "(",
        Chord(D.DOWN_RIGHT, D.DOWN): ")",
        Chord(D.DOWN_RIGHT, D.LEFT): "[",
        Chord(D.DOWN_RIGHT, D.RIGHT): "]",
        Chord(D.DOWN_LEFT, D.UP): "{",
        Chord(D.DOWN_LEFT, D.DOWN): "}",
        Chord(D.DOWN_LEFT, D.LEFT): ",",
        Chord(D.DOWN_LEFT, D.RIGHT): ".",

        # ========== Common Variables ==========
        Chord(D.UP_LEFT, D.RIGHT): "self",
        Chord(D.UP_LEFT, D.UP): "None",
        Chord(D.UP_LEFT, D.DOWN): "True",
        Chord(D.UP_LEFT, D.LEFT): "False",
        Chord(D.UP_LEFT, D.CENTER): "not ",

        # ========== Special Characters ==========
        # Center-Center = space
        Chord(D.CENTER, D.CENTER): " ",

        # Newline (enter)
        Chord(D.CENTER, D.DOWN_RIGHT): "\n",

        # Tab (indent)
        Chord(D.CENTER, D.DOWN_LEFT): "    ",  # 4 spaces

        # Common patterns
        Chord(D.UP, D.CENTER): "print(",
        Chord(D.RIGHT, D.UP_RIGHT): "len(",
        Chord(D.RIGHT, D.DOWN_RIGHT): "range(",
        Chord(D.RIGHT, D.UP_LEFT): "str(",
        Chord(D.RIGHT, D.DOWN_LEFT): "int(",

        # Or/and
        Chord(D.LEFT, D.UP_RIGHT): "or ",
        Chord(D.LEFT, D.UP_LEFT): "and ",

        # Lambda and comprehension helpers
        Chord(D.UP, D.UP_RIGHT): "lambda ",
        Chord(D.UP, D.UP_LEFT): " in ",
    }

    return mappings


@dataclass
class RadialSegment:
    """A segment of the radial menu."""
    direction: Direction
    label: str
    shortcut: str = ""


class RadialMenu:
    """
    Visual radial menu overlay for one thumbstick.

    Shows the 8 directions with labels for what each produces.
    """

    def __init__(self, render_mode: RenderMode = RenderMode.ASCII):
        self.render_mode = render_mode
        self.highlighted: Direction = Direction.CENTER
        self.segments = self._create_segments()

    def _create_segments(self) -> List[RadialSegment]:
        """Create the 8 directional segments."""
        return [
            RadialSegment(Direction.UP, "↑", "def"),
            RadialSegment(Direction.UP_RIGHT, "↗", "=="),
            RadialSegment(Direction.RIGHT, "→", "import"),
            RadialSegment(Direction.DOWN_RIGHT, "↘", "()"),
            RadialSegment(Direction.DOWN, "↓", "return"),
            RadialSegment(Direction.DOWN_LEFT, "↙", "{}"),
            RadialSegment(Direction.LEFT, "←", "if"),
            RadialSegment(Direction.UP_LEFT, "↖", "!="),
        ]

    def highlight(self, direction: Direction):
        """Set the highlighted direction."""
        self.highlighted = direction

    def render(self) -> str:
        """Render the radial menu as text."""
        if self.render_mode == RenderMode.RICH:
            return self._render_rich()
        return self._render_ascii()

    def _render_ascii(self) -> str:
        """Render as ASCII art."""
        hl = self.highlighted

        # Create visual indicator for highlighted direction
        def mark(d: Direction, label: str) -> str:
            return f"[{label}]" if d == hl else f" {label} "

        lines = [
            "         ╭───────────╮",
            f"         │{mark(Direction.UP, '  ↑  ')}│",
            f"   {mark(Direction.UP_LEFT, '↖')}    │           │    {mark(Direction.UP_RIGHT, '↗')}",
            "     ╭───┼───────────┼───╮",
            f"  {mark(Direction.LEFT, '←')}│     ●     │{mark(Direction.RIGHT, '→')}",
            "     ╰───┼───────────┼───╯",
            f"   {mark(Direction.DOWN_LEFT, '↙')}    │           │    {mark(Direction.DOWN_RIGHT, '↘')}",
            f"         │{mark(Direction.DOWN, '  ↓  ')}│",
            "         ╰───────────╯",
        ]

        return "\n".join(lines)

    def _render_rich(self) -> str:
        """Render using Rich library formatting."""
        # For now, return ASCII. Rich rendering would use Panel and Color.
        return self._render_ascii()


class RadialMenuPair:
    """
    Pair of radial menus for left and right sticks.

    Shows both sticks with their current directions and
    the resulting chord output.
    """

    def __init__(self, render_mode: RenderMode = RenderMode.ASCII):
        self.left = RadialMenu(render_mode)
        self.right = RadialMenu(render_mode)
        self._mappings = get_keyword_mappings()

    def set_pending_chord(self, left_dir: Direction, right_dir: Direction):
        """Set both directions for pending chord."""
        self.left.highlight(left_dir)
        self.right.highlight(right_dir)

    def render(self) -> str:
        """Render both menus side by side with chord preview."""
        left_render = self.left.render()
        right_render = self.right.render()

        # Get pending chord output
        chord = Chord(self.left.highlighted, self.right.highlighted)
        output = self._mappings.get(chord, "")

        # Display output as preview
        if output == "\n":
            output_display = "NEWLINE"
        elif output == " ":
            output_display = "SPACE"
        elif output == "    ":
            output_display = "TAB"
        else:
            output_display = output if output else "?"

        # Combine side by side
        left_lines = left_render.split("\n")
        right_lines = right_render.split("\n")

        combined = []
        combined.append("       L-STICK                    R-STICK")
        combined.append("")

        max_lines = max(len(left_lines), len(right_lines))
        for i in range(max_lines):
            left_line = left_lines[i] if i < len(left_lines) else ""
            right_line = right_lines[i] if i < len(right_lines) else ""
            combined.append(f"{left_line:30s}  {right_line}")

        combined.append("")
        combined.append(f"  CHORD OUTPUT: {output_display}")

        return "\n".join(combined)


@dataclass
class RadialConfig:
    """Configuration for radial input."""
    deadzone: float = 0.3
    confirm_button: str = "A"
    cancel_button: str = "B"

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "deadzone": self.deadzone,
            "confirm_button": self.confirm_button,
            "cancel_button": self.cancel_button,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RadialConfig":
        """Deserialize from dictionary."""
        return cls(
            deadzone=data.get("deadzone", 0.3),
            confirm_button=data.get("confirm_button", "A"),
            cancel_button=data.get("cancel_button", "B"),
        )


class RadialInputHandler:
    """
    Main handler for radial thumbstick input.

    Processes raw stick values and produces text output.

    Usage:
        handler = RadialInputHandler()

        # Each frame, provide stick values
        result = handler.process(
            left_x=controller.left_stick_x,
            left_y=controller.left_stick_y,
            right_x=controller.right_stick_x,
            right_y=controller.right_stick_y,
            confirm=controller.button_a_pressed,
        )

        if result:
            editor.insert_text(result)
    """

    def __init__(
        self,
        deadzone: float = 0.3,
        custom_mappings: Optional[Dict[Chord, str]] = None
    ):
        self.deadzone = deadzone
        self._mappings = custom_mappings if custom_mappings else get_keyword_mappings()
        self.current_chord = Chord(Direction.CENTER, Direction.CENTER)
        self.menu_pair = RadialMenuPair()

    def process(
        self,
        left_x: float,
        left_y: float,
        right_x: float,
        right_y: float,
        confirm: bool = False
    ) -> Optional[str]:
        """
        Process stick input and return text if confirmed.

        Args:
            left_x: Left stick X axis (-1.0 to 1.0)
            left_y: Left stick Y axis (-1.0 to 1.0)
            right_x: Right stick X axis (-1.0 to 1.0)
            right_y: Right stick Y axis (-1.0 to 1.0)
            confirm: True if confirm button pressed

        Returns:
            Text to insert if confirmed, None otherwise
        """
        # Detect directions
        left_dir = detect_direction(left_x, left_y, self.deadzone)
        right_dir = detect_direction(right_x, right_y, self.deadzone)

        # Update current chord
        self.current_chord = Chord(left_dir, right_dir)

        # Update menu visuals
        self.menu_pair.set_pending_chord(left_dir, right_dir)

        # If confirmed, output the mapped text
        if confirm:
            output = self._mappings.get(self.current_chord)

            # Reset to center after confirm
            self.current_chord = Chord(Direction.CENTER, Direction.CENTER)

            return output if output else None

        return None

    def get_text_input(self) -> str:
        """Compatibility method for InputDevice protocol."""
        # This would be called in a loop until user confirms
        return ""

    def get_current_preview(self) -> str:
        """Get preview of what current chord would produce."""
        return self._mappings.get(self.current_chord, "")

    def render_menu(self) -> str:
        """Render the current menu state."""
        return self.menu_pair.render()


# ============================================================================
# MUSCLE MEMORY TRAINER
# ============================================================================

@dataclass
class TrainingChallenge:
    """A muscle memory training challenge."""
    target_keyword: str
    target_chord: Chord
    hint: str = ""


@dataclass
class AttemptResult:
    """Result of a training attempt."""
    correct: bool
    expected_chord: Chord
    actual_chord: Chord
    response_time_ms: float = 0.0


class MuscleMemoryTrainer:
    """
    Muscle memory training mode for learning chord combinations.

    Shows a keyword and challenges the player to input the correct chord.
    Tracks accuracy and focuses on weak areas.
    """

    # Simple keywords for beginners
    BEGINNER_KEYWORDS = {"def ", "if ", "for ", "return ", "class ", "print("}

    # Intermediate keywords
    INTERMEDIATE_KEYWORDS = {
        "def ", "if ", "for ", "return ", "class ", "print(",
        "while ", "elif ", "else:", "import ", "from ",
        "and ", "or ", "not ", "in ", "True", "False", "None"
    }

    # All keywords for advanced
    ADVANCED_KEYWORDS = None  # Uses all mappings

    def __init__(
        self,
        difficulty: TrainingDifficulty = TrainingDifficulty.BEGINNER
    ):
        self.difficulty = difficulty
        self._mappings = get_keyword_mappings()
        self._reverse_mappings = {v: k for k, v in self._mappings.items()}

        # Filter keywords based on difficulty
        self._available_keywords = self._get_keywords_for_difficulty()

        # Stats tracking
        self._attempts: List[tuple[Chord, Chord, bool]] = []  # (target, actual, correct)
        self._weakness_counts: Dict[Chord, int] = {}  # Chord -> failure count

        # Current challenge state
        self._current_challenge: Optional[TrainingChallenge] = None
        self._challenge_start_time: float = 0.0

    def _get_keywords_for_difficulty(self) -> set:
        """Get allowed keywords for current difficulty."""
        if self.difficulty == TrainingDifficulty.BEGINNER:
            return self.BEGINNER_KEYWORDS
        elif self.difficulty == TrainingDifficulty.INTERMEDIATE:
            return self.INTERMEDIATE_KEYWORDS
        else:
            # Advanced/Expert: all keywords
            return set(self._mappings.values())

    def next_challenge(self) -> TrainingChallenge:
        """Generate the next training challenge."""
        import random

        # Filter to available keywords that have mappings
        available = [
            kw for kw in self._available_keywords
            if kw in self._reverse_mappings
        ]

        if not available:
            # Fallback to all mappings
            available = list(self._mappings.values())

        # Prioritize weak areas (30% chance to pick a weakness)
        weak_chords = list(self._weakness_counts.keys())
        if weak_chords and random.random() < 0.3:
            weak_chord = random.choice(weak_chords)
            keyword = self._mappings.get(weak_chord)
            if keyword:
                available = [keyword]

        # Pick random keyword
        keyword = random.choice(available)
        chord = self._reverse_mappings[keyword]

        self._current_challenge = TrainingChallenge(
            target_keyword=keyword,
            target_chord=chord,
            hint=f"L:{chord.left.name} + R:{chord.right.name}"
        )
        self._challenge_start_time = time.time()

        return self._current_challenge

    def attempt(self, chord: Chord) -> AttemptResult:
        """
        Submit an attempt for the current challenge.

        Args:
            chord: The chord the player input

        Returns:
            AttemptResult with correctness and timing
        """
        if not self._current_challenge:
            raise ValueError("No active challenge. Call next_challenge() first.")

        target = self._current_challenge.target_chord
        correct = (chord == target)

        # Calculate response time
        response_time = (time.time() - self._challenge_start_time) * 1000  # ms

        # Record the attempt
        self._record_attempt(target, chord)

        return AttemptResult(
            correct=correct,
            expected_chord=target,
            actual_chord=chord,
            response_time_ms=response_time
        )

    def _record_attempt(self, target: Chord, actual: Chord):
        """Record an attempt for stats."""
        correct = (target == actual)
        self._attempts.append((target, actual, correct))

        if not correct:
            # Track weakness
            self._weakness_counts[target] = self._weakness_counts.get(target, 0) + 1
        else:
            # Reduce weakness count on success
            if target in self._weakness_counts:
                self._weakness_counts[target] = max(0, self._weakness_counts[target] - 1)
                if self._weakness_counts[target] == 0:
                    del self._weakness_counts[target]

    def get_stats(self) -> dict:
        """Get training statistics."""
        total = len(self._attempts)
        correct = sum(1 for _, _, c in self._attempts if c)

        return {
            "total_attempts": total,
            "correct_count": correct,
            "accuracy": correct / max(total, 1),
            "weakness_count": len(self._weakness_counts),
        }

    def get_weakness_focus(self) -> List[Chord]:
        """Get chords that need more practice."""
        # Sort by failure count, return top weaknesses
        sorted_weaknesses = sorted(
            self._weakness_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [chord for chord, _ in sorted_weaknesses[:5]]


# Self-teaching note:
#
# This file demonstrates:
# - Enums for type-safe constants (Level 2: collections)
# - Dataclasses for structured data (Level 5: @dataclass)
# - Frozen dataclasses for hashable objects (Level 6: patterns)
# - Math functions (trigonometry for direction detection)
# - Dictionary comprehensions and filtering (Level 4)
# - Type hints with Optional, Dict, List (Level 5)
# - Class design patterns (Level 5+)
#
# The radial typing system is a game input innovation:
# - Two thumbsticks give 9x9 = 81 chord combinations
# - Chords map to Python keywords and operators
# - Visual feedback shows current selection
# - Muscle memory training reinforces learning
#
# The learner will encounter this AFTER mastering:
# - Level 3: Functions and classes
# - Level 4: Comprehensions and lambda
# - Level 5: Type hints and dataclasses
# - Level 6: Design patterns
