"""
Progressive Discovery Primitives

Implements the discovery system where features unlock based on player progress.

Primitives:
- /help - Always available, shows current unlocks
- /checkpoint - Available at Level 2+
- /video - Available at Level 4+
- /rewind - Available at Level 5+
- /diff - Available at Level 6

These map to TAS and introspection features, revealed progressively
as the player advances through concepts.

Self-teaching note:
This file demonstrates:
- Enum for primitive types (Level 4)
- Dataclasses with validation (Level 5)
- Registry pattern (Level 5+)
- Level-gated access control (Level 4: conditionals)
"""

from dataclasses import dataclass, field
from typing import Optional, Any, Callable
from enum import Enum, auto


class PrimitiveType(Enum):
    """Types of discovery primitives."""
    HELP = auto()
    CHECKPOINT = auto()
    RESTORE = auto()
    REWIND = auto()
    STEP = auto()
    DIFF = auto()
    VIDEO = auto()
    SCREENSHOT = auto()
    WIREFRAME = auto()


@dataclass
class Primitive:
    """
    A discoverable primitive/command.

    Primitives are features that unlock as the player progresses.
    """

    name: str
    primitive_type: PrimitiveType
    description: str
    usage: str
    examples: list[str] = field(default_factory=list)

    # Unlock requirements
    min_level: int = 0  # Player must be at least this level
    required_concepts: list[str] = field(default_factory=list)  # Concepts must be mastered

    # Display
    icon: str = ""
    hidden: bool = False  # If True, don't show until unlocked


@dataclass
class PrimitiveContext:
    """
    Context for executing a primitive.

    Contains all the state needed to execute primitive commands.
    """

    # Player state
    player_id: str = ""
    player_level: int = 0
    mastered_concepts: set[str] = field(default_factory=set)

    # Game state (from GameState object or direct fields)
    game_state: Any = None  # GameState object
    current_code: str = ""
    cursor_position: tuple[int, int] = (0, 0)
    challenge_id: Optional[str] = None

    # Session state
    session_id: Optional[str] = None
    checkpoints: dict[str, Any] = field(default_factory=dict)

    # TAS recorder for checkpoint/restore
    tas_recorder: Any = None


@dataclass
class PrimitiveResult:
    """Result of executing a primitive."""

    success: bool
    message: str = ""
    data: Optional[Any] = None

    # For display
    output_lines: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)

    @property
    def output(self) -> str:
        """Get formatted output string."""
        lines = []
        if self.message:
            lines.append(self.message)
        lines.extend(self.output_lines)
        return "\n".join(lines)


# Primitive definitions
_PRIMITIVES: dict[str, Primitive] = {}


def _register_primitives():
    """Register all built-in primitives."""
    global _PRIMITIVES

    # /help - Always available (Level 0)
    _PRIMITIVES["help"] = Primitive(
        name="help",
        primitive_type=PrimitiveType.HELP,
        description="Show available commands and features",
        usage="/help [topic]",
        examples=["/help", "/help checkpoint", "/help concepts"],
        min_level=0,
        icon="?",
    )

    # /screenshot - Level 0 (basic capture)
    _PRIMITIVES["screenshot"] = Primitive(
        name="screenshot",
        primitive_type=PrimitiveType.SCREENSHOT,
        description="Capture current state",
        usage="/screenshot [name]",
        examples=["/screenshot", "/screenshot my_solution"],
        min_level=0,
        icon="📸",
    )

    # /checkpoint - Level 1+
    _PRIMITIVES["checkpoint"] = Primitive(
        name="checkpoint",
        primitive_type=PrimitiveType.CHECKPOINT,
        description="Save your current progress",
        usage="/checkpoint [name]",
        examples=["/checkpoint", "/checkpoint before_refactor"],
        min_level=1,
        icon="💾",
    )

    # /restore - Level 1+
    _PRIMITIVES["restore"] = Primitive(
        name="restore",
        primitive_type=PrimitiveType.RESTORE,
        description="Restore to a saved checkpoint",
        usage="/restore <name>",
        examples=["/restore before_refactor"],
        min_level=1,
        icon="↩",
    )

    # /rewind - Level 2+
    _PRIMITIVES["rewind"] = Primitive(
        name="rewind",
        primitive_type=PrimitiveType.REWIND,
        description="Step back through your history",
        usage="/rewind [steps]",
        examples=["/rewind", "/rewind 5"],
        min_level=2,
        icon="⏪",
    )

    # /step - Level 2+
    _PRIMITIVES["step"] = Primitive(
        name="step",
        primitive_type=PrimitiveType.STEP,
        description="Step forward one action",
        usage="/step",
        examples=["/step"],
        min_level=2,
        icon="⏩",
    )

    # /diff - Level 2+
    _PRIMITIVES["diff"] = Primitive(
        name="diff",
        primitive_type=PrimitiveType.DIFF,
        description="See what changed between states",
        usage="/diff [checkpoint]",
        examples=["/diff", "/diff before_refactor"],
        min_level=2,
        icon="📊",
    )

    # /video - Level 3+
    _PRIMITIVES["video"] = Primitive(
        name="video",
        primitive_type=PrimitiveType.VIDEO,
        description="Start/stop recording your session",
        usage="/video [start|stop]",
        examples=["/video start", "/video stop"],
        min_level=3,
        icon="🎬",
    )

    # /mosaic - Level 3+
    _PRIMITIVES["mosaic"] = Primitive(
        name="mosaic",
        primitive_type=PrimitiveType.VIDEO,  # Reusing VIDEO type for now
        description="Create frame grid from recording",
        usage="/mosaic [count]",
        examples=["/mosaic", "/mosaic 6"],
        min_level=3,
        icon="🖼",
    )

    # /wireframe - Level 3+
    _PRIMITIVES["wireframe"] = Primitive(
        name="wireframe",
        primitive_type=PrimitiveType.WIREFRAME,
        description="Show code structure analysis",
        usage="/wireframe",
        examples=["/wireframe"],
        min_level=3,
        icon="🔍",
    )

    # /discover - Level 4+ (show what features exist)
    _PRIMITIVES["discover"] = Primitive(
        name="discover",
        primitive_type=PrimitiveType.HELP,
        description="Discover new features and commands",
        usage="/discover",
        examples=["/discover"],
        min_level=4,
        icon="🔮",
    )

    # /teach - Level 5+ (explain what you're doing)
    _PRIMITIVES["teach"] = Primitive(
        name="teach",
        primitive_type=PrimitiveType.HELP,
        description="Get detailed explanations",
        usage="/teach [topic]",
        examples=["/teach loops", "/teach functions"],
        min_level=5,
        icon="🎓",
    )


# Initialize primitives
_register_primitives()


def get_available_primitives(primitive_level: int = 0) -> list[str]:
    """
    Get names of primitives available at a given level.

    Args:
        primitive_level: Player level (0-6)

    Returns:
        List of primitive names (without slash, e.g., "help", "checkpoint")
    """
    available = []

    for primitive in _PRIMITIVES.values():
        # Check level requirement
        if primitive_level >= primitive.min_level:
            available.append("/" + primitive.name)

    return sorted(available)


def get_available_primitives_old(context: PrimitiveContext) -> list[Primitive]:
    """
    Get primitives available to a player based on their progress.

    Args:
        context: Player's current context

    Returns:
        List of available primitives
    """
    available = []

    for primitive in _PRIMITIVES.values():
        # Check level requirement
        if context.player_level < primitive.min_level:
            continue

        # Check concept requirements
        if primitive.required_concepts:
            if not all(c in context.mastered_concepts for c in primitive.required_concepts):
                continue

        available.append(primitive)

    return available


def get_primitive_info(name: str) -> Optional[dict[str, Any]]:
    """
    Get information about a primitive by name.

    Args:
        name: Primitive name (with or without slash, e.g., "checkpoint" or "/checkpoint")

    Returns:
        Dict with keys: description, usage, level
        None if not found
    """
    # Remove leading slash if present
    clean_name = name.lstrip('/').lower()
    primitive = _PRIMITIVES.get(clean_name)

    if not primitive:
        return None

    return {
        "description": primitive.description,
        "usage": primitive.usage,
        "level": primitive.min_level,
    }


def get_newly_unlocked(
    old_level: int,
    new_level: int,
) -> list[str]:
    """
    Get names of primitives newly unlocked by leveling up.

    Args:
        old_level: Previous player level
        new_level: New player level

    Returns:
        List of newly unlocked primitive names (strings like "/checkpoint", "/help")
    """
    newly_unlocked = []

    for primitive in _PRIMITIVES.values():
        # Skip if already was available
        if old_level >= primitive.min_level:
            continue

        # Check if now available
        if new_level >= primitive.min_level:
            newly_unlocked.append("/" + primitive.name)

    return sorted(newly_unlocked)


def execute_primitive(
    command: str,
    primitive_level: int = 0,
    game_state: Any = None,
    context: Optional[PrimitiveContext] = None,
) -> PrimitiveResult:
    """
    Execute a primitive command.

    Args:
        command: Command string (e.g., "/help" or "/checkpoint my_save")
        primitive_level: Player level for access control
        game_state: Optional GameState for context
        context: Optional PrimitiveContext

    Returns:
        Result of execution
    """
    # Parse command string
    parts = command.strip().split()
    name = parts[0].lstrip('/')
    args = parts[1:] if len(parts) > 1 else []

    # Create or update context
    if context is None:
        context = PrimitiveContext(
            player_level=primitive_level,
        )
    else:
        context.player_level = primitive_level

    # Add game_state to context if provided
    if game_state is not None:
        context.game_state = game_state
        context.current_code = getattr(game_state, 'current_code', '')
        context.cursor_position = getattr(game_state, 'cursor_position', (0, 0))

    # Get primitive
    primitive = _PRIMITIVES.get(name.lower())
    if not primitive:
        return PrimitiveResult(
            success=False,
            message=f"Unknown command: /{name}",
            suggestions=["Type /help to see available commands"],
        )

    # Check if available
    if context.player_level < primitive.min_level:
        return PrimitiveResult(
            success=False,
            message=f"/{name} unlocks at Level {primitive.min_level}",
            output_lines=[
                f"You are Level {context.player_level}.",
                f"Keep learning to unlock /{name}!",
            ],
        )

    # Check concept requirements
    if primitive.required_concepts:
        missing = [c for c in primitive.required_concepts if c not in context.mastered_concepts]
        if missing:
            return PrimitiveResult(
                success=False,
                message=f"/{name} requires mastering: {', '.join(missing)}",
                output_lines=[
                    "Complete these concepts to unlock this feature:",
                ] + [f"  - {c}" for c in missing],
            )

    # Execute based on type
    if primitive.primitive_type == PrimitiveType.HELP:
        return _execute_help(args, context)

    elif primitive.primitive_type == PrimitiveType.CHECKPOINT:
        return _execute_checkpoint(args, context)

    elif primitive.primitive_type == PrimitiveType.RESTORE:
        return _execute_restore(args, context)

    elif primitive.primitive_type == PrimitiveType.REWIND:
        return _execute_rewind(args, context)

    elif primitive.primitive_type == PrimitiveType.STEP:
        return _execute_step(args, context)

    elif primitive.primitive_type == PrimitiveType.DIFF:
        return _execute_diff(args, context)

    elif primitive.primitive_type == PrimitiveType.VIDEO:
        return _execute_video(args, context)

    elif primitive.primitive_type == PrimitiveType.SCREENSHOT:
        return _execute_screenshot(args, context)

    elif primitive.primitive_type == PrimitiveType.WIREFRAME:
        return _execute_wireframe(args, context)

    return PrimitiveResult(
        success=False,
        message=f"/{name} is not yet implemented",
    )


def _execute_help(args: list[str], context: PrimitiveContext) -> PrimitiveResult:
    """Execute /help command."""
    available = get_available_primitives(context.player_level)

    if args:
        # Help for specific topic
        topic = args[0].lower()
        primitive = _PRIMITIVES.get(topic)

        if primitive:
            lines = [
                f"/{primitive.name} - {primitive.description}",
                "",
                f"Usage: {primitive.usage}",
                "",
                "Examples:",
            ] + [f"  {ex}" for ex in primitive.examples]

            if primitive.min_level > context.player_level:
                lines.append("")
                lines.append(f"⚠️ Unlocks at Level {primitive.min_level}")

            return PrimitiveResult(
                success=True,
                message=f"Help for /{topic}",
                output_lines=lines,
            )

        return PrimitiveResult(
            success=False,
            message=f"No help available for: {topic}",
        )

    # General help - available is now a list of strings like ["/help", "/screenshot"]
    lines = ["Available commands:", ""]

    # Get Primitive objects for available commands
    for prim_name in sorted(available):
        prim = _PRIMITIVES.get(prim_name.lstrip('/'))
        if prim:
            icon = prim.icon or "•"
            lines.append(f"  {icon} {prim_name} - {prim.description}")

    # Show locked commands hint
    all_primitives = set(f"/{p.name}" for p in _PRIMITIVES.values() if not p.hidden)
    locked_count = len(all_primitives - set(available))
    if locked_count:
        lines.append("")
        lines.append(f"🔒 {locked_count} more commands unlock as you progress")

    return PrimitiveResult(
        success=True,
        message="Available commands",
        output_lines=lines,
    )


def _execute_checkpoint(args: list[str], context: PrimitiveContext) -> PrimitiveResult:
    """Execute /checkpoint command."""
    name = args[0] if args else "auto"

    # Store checkpoint (in real implementation, this would call TASRecorder)
    context.checkpoints[name] = {
        "code": context.current_code,
        "cursor": context.cursor_position,
    }

    return PrimitiveResult(
        success=True,
        message=f"Checkpoint '{name}' saved",
        data={"checkpoint_name": name},
        output_lines=[
            f"💾 Saved checkpoint: {name}",
            f"   Code: {len(context.current_code)} characters",
            "",
            "Use /restore to return to this point.",
        ],
    )


def _execute_restore(args: list[str], context: PrimitiveContext) -> PrimitiveResult:
    """Execute /restore command."""
    if not args:
        # List available checkpoints
        if not context.checkpoints:
            return PrimitiveResult(
                success=False,
                message="No checkpoints saved",
                suggestions=["Use /checkpoint to save first"],
            )

        lines = ["Available checkpoints:"]
        for name in context.checkpoints:
            lines.append(f"  • {name}")

        return PrimitiveResult(
            success=True,
            message="Select a checkpoint to restore",
            output_lines=lines,
        )

    name = args[0]
    if name not in context.checkpoints:
        return PrimitiveResult(
            success=False,
            message=f"Checkpoint '{name}' not found",
        )

    # Restore (in real implementation, would update game state)
    checkpoint = context.checkpoints[name]

    return PrimitiveResult(
        success=True,
        message=f"Restored to '{name}'",
        data={"checkpoint_name": name, "restored": checkpoint},
        output_lines=[
            f"↩ Restored checkpoint: {name}",
            "",
            "Your code has been restored to this point.",
        ],
    )


def _execute_rewind(args: list[str], context: PrimitiveContext) -> PrimitiveResult:
    """Execute /rewind command."""
    steps = int(args[0]) if args else 1

    return PrimitiveResult(
        success=True,
        message=f"Rewound {steps} steps",
        data={"steps": steps},
        output_lines=[
            f"⏪ Rewound {steps} step(s)",
            "",
            "Use /step to move forward, or continue coding.",
        ],
    )


def _execute_step(args: list[str], context: PrimitiveContext) -> PrimitiveResult:
    """Execute /step command."""
    return PrimitiveResult(
        success=True,
        message="Stepped forward",
        output_lines=[
            "⏩ Stepped forward 1 action",
            "",
            "Use /step again or continue coding.",
        ],
    )


def _execute_diff(args: list[str], context: PrimitiveContext) -> PrimitiveResult:
    """Execute /diff command."""
    if args:
        checkpoint_name = args[0]
        if checkpoint_name not in context.checkpoints:
            return PrimitiveResult(
                success=False,
                message=f"Checkpoint '{checkpoint_name}' not found",
            )
    else:
        checkpoint_name = "last save"

    return PrimitiveResult(
        success=True,
        message=f"Diff from {checkpoint_name}",
        output_lines=[
            f"📊 Changes since {checkpoint_name}:",
            "",
            "  (Diff output would appear here)",
            "",
            "Green (+) = added, Red (-) = removed",
        ],
    )


def _execute_video(args: list[str], context: PrimitiveContext) -> PrimitiveResult:
    """Execute /video command."""
    action = args[0].lower() if args else "status"

    if action == "start":
        return PrimitiveResult(
            success=True,
            message="Recording started",
            output_lines=[
                "🎬 Recording started",
                "",
                "Your session is being recorded for analysis.",
                "Use /video stop to finish.",
            ],
        )

    elif action == "stop":
        return PrimitiveResult(
            success=True,
            message="Recording stopped",
            output_lines=[
                "⏹️ Recording stopped",
                "",
                "Your session has been saved.",
            ],
        )

    else:
        return PrimitiveResult(
            success=True,
            message="Video status",
            output_lines=[
                "🎬 Video recording",
                "",
                "Commands:",
                "  /video start - Begin recording",
                "  /video stop  - Stop recording",
            ],
        )


def _execute_screenshot(args: list[str], context: PrimitiveContext) -> PrimitiveResult:
    """Execute /screenshot command."""
    name = args[0] if args else "screenshot"

    return PrimitiveResult(
        success=True,
        message=f"Screenshot '{name}' captured",
        data={"screenshot_name": name},
        output_lines=[
            f"📸 Screenshot saved: {name}",
            "",
            "Current state captured with code and context.",
        ],
    )


def _execute_wireframe(args: list[str], context: PrimitiveContext) -> PrimitiveResult:
    """Execute /wireframe command."""
    return PrimitiveResult(
        success=True,
        message="Wireframe analysis",
        output_lines=[
            "🔍 Code Structure Analysis",
            "",
            "(AST analysis would appear here)",
            "",
            "Functions: 0",
            "Classes: 0",
            "Imports: 0",
            "Variables: 0",
        ],
    )


# Self-teaching note:
#
# This file demonstrates:
# - Registry pattern (global _PRIMITIVES dict)
# - Progressive disclosure (level-gated features)
# - Command pattern (execute_primitive)
# - Dataclasses for structured data
# - Enum for type safety
# - Function dispatch based on type
#
# Key concepts:
# 1. Progressive disclosure - reveal features as players advance
# 2. Registry pattern - central storage for all primitives
# 3. Command pattern - execute commands by name
# 4. Level gating - require minimum level to access
# 5. Concept gating - require mastered concepts
#
# The learner will encounter this AFTER mastering:
# - Level 4: Enums, conditionals, dictionaries
# - Level 5: Dataclasses, functions as data
# - Level 6: Design patterns
