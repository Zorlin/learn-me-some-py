"""
Wireframe - Mental Model of Game State

A wireframe captures the "mental context" behind what's visible on screen:
- The code being edited and its AST structure
- Game state (challenge, tests, progress)
- Player state (emotion, mastery)
- Session context (timing, checkpoints)

This enables deep analysis by Claude or other AI systems.

Self-teaching note:
This file demonstrates:
- AST (Abstract Syntax Tree) parsing (Level 6: metaprogramming)
- Dataclasses with optional fields (Level 5: @dataclass)
- Exception handling for invalid input (Level 3: try/except)
- Type annotations (Level 5: Optional, Any)
"""

from dataclasses import dataclass, field
from typing import Optional, Any
from datetime import datetime
import ast


@dataclass
class Wireframe:
    """
    Mental model of game state for AI analysis.

    A wireframe captures everything Claude needs to understand
    what's happening in the game, beyond just the visual screenshot.

    Usage:
        # From code string
        wf = Wireframe.from_code("def hello(): pass")

        # From full game state
        wf = Wireframe.from_game_state(game_state)

        # Export for analysis
        data = wf.to_dict()
    """

    # Code state
    code: str = ""
    ast_tree: Optional[ast.Module] = None
    parse_error: Optional[str] = None
    line_count: int = 0

    # Game context
    challenge_id: Optional[str] = None
    tests_passing: int = 0
    tests_total: int = 0
    hints_used: int = 0

    # Player context
    player_id: Optional[str] = None
    cursor_position: tuple[int, int] = (0, 0)
    mastery_levels: dict[str, int] = field(default_factory=dict)
    current_emotion: Optional[dict[str, Any]] = None

    # Session context
    session_duration: Optional[float] = None  # seconds
    challenges_completed: int = 0
    timestamp: datetime = field(default_factory=datetime.now)

    # Multiplayer context (if active)
    other_players: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_code(cls, code: str) -> "Wireframe":
        """
        Create a wireframe from code string.

        Args:
            code: Python code to analyze

        Returns:
            Wireframe with code analysis
        """
        wireframe = cls(code=code)
        wireframe.line_count = len(code.split("\n"))

        # Try to parse the AST
        try:
            wireframe.ast_tree = ast.parse(code)
            wireframe.parse_error = None
        except SyntaxError as e:
            wireframe.ast_tree = None
            wireframe.parse_error = str(e)

        return wireframe

    @classmethod
    def from_game_state(cls, state: Any) -> "Wireframe":
        """
        Create a wireframe from a GameState object.

        Args:
            state: GameState object with current game state

        Returns:
            Wireframe with full context
        """
        # Get code from state
        code = getattr(state, "current_code", "")

        # Create base wireframe from code
        wireframe = cls.from_code(code)

        # Add game context
        wireframe.challenge_id = getattr(state, "current_challenge", None)
        wireframe.tests_passing = getattr(state, "tests_passing", 0)
        wireframe.tests_total = getattr(state, "tests_total", 0)
        wireframe.hints_used = getattr(state, "hints_used", 0)

        # Add cursor position
        wireframe.cursor_position = getattr(state, "cursor_position", (0, 0))

        return wireframe

    def get_ast_summary(self) -> dict[str, list[str]]:
        """
        Get a summary of the AST structure.

        Returns:
            Dictionary with functions, classes, imports, etc.
        """
        summary: dict[str, list[str]] = {
            "functions": [],
            "classes": [],
            "imports": [],
            "variables": [],
        }

        if not self.ast_tree:
            return summary

        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.FunctionDef):
                summary["functions"].append(node.name)
            elif isinstance(node, ast.AsyncFunctionDef):
                summary["functions"].append(f"async {node.name}")
            elif isinstance(node, ast.ClassDef):
                summary["classes"].append(node.name)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    summary["imports"].append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    summary["imports"].append(f"{module}.{alias.name}")
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        summary["variables"].append(target.id)

        return summary

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize wireframe to dictionary.

        Returns:
            Dictionary representation for JSON export
        """
        return {
            "code": self.code,
            "line_count": self.line_count,
            "ast_summary": self.get_ast_summary(),
            "parse_error": self.parse_error,
            "challenge_id": self.challenge_id,
            "tests_passing": self.tests_passing,
            "tests_total": self.tests_total,
            "hints_used": self.hints_used,
            "player_id": self.player_id,
            "cursor_position": list(self.cursor_position),
            "mastery_levels": self.mastery_levels,
            "current_emotion": self.current_emotion,
            "session_duration": self.session_duration,
            "challenges_completed": self.challenges_completed,
            "timestamp": self.timestamp.isoformat(),
            "other_players": self.other_players,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Wireframe":
        """
        Deserialize wireframe from dictionary.

        Args:
            data: Dictionary representation

        Returns:
            Wireframe object
        """
        # Start with code analysis
        wireframe = cls.from_code(data.get("code", ""))

        # Restore other fields
        wireframe.challenge_id = data.get("challenge_id")
        wireframe.tests_passing = data.get("tests_passing", 0)
        wireframe.tests_total = data.get("tests_total", 0)
        wireframe.hints_used = data.get("hints_used", 0)
        wireframe.player_id = data.get("player_id")

        cursor = data.get("cursor_position", [0, 0])
        wireframe.cursor_position = tuple(cursor) if cursor else (0, 0)

        wireframe.mastery_levels = data.get("mastery_levels", {})
        wireframe.current_emotion = data.get("current_emotion")
        wireframe.session_duration = data.get("session_duration")
        wireframe.challenges_completed = data.get("challenges_completed", 0)

        if data.get("timestamp"):
            wireframe.timestamp = datetime.fromisoformat(data["timestamp"])

        wireframe.other_players = data.get("other_players", [])

        return wireframe

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"Wireframe(lines={self.line_count}, "
            f"tests={self.tests_passing}/{self.tests_total}, "
            f"error={bool(self.parse_error)})"
        )


# Self-teaching note:
#
# This file demonstrates:
# - AST (Abstract Syntax Tree) - Python's representation of code structure
# - dataclasses with field(default_factory=...) for mutable defaults
# - Optional types for nullable fields
# - classmethod for alternative constructors
# - getattr() for safe attribute access
# - Exception handling for parsing errors
# - Serialization patterns (to_dict/from_dict)
#
# Key concepts:
# 1. AST parsing - ast.parse() converts code to tree structure
# 2. ast.walk() - Iterate over all nodes in the tree
# 3. isinstance() checks - Identify different node types
# 4. Defensive programming - getattr with defaults
# 5. Factory methods - from_code, from_game_state, from_dict
#
# The learner will encounter this AFTER mastering:
# - Level 4: Advanced data structures
# - Level 5: Classes and dataclasses
# - Level 6: Metaprogramming concepts
