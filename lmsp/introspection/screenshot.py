"""
Screenshot Bundle - Visual Capture with Context

Captures a "screenshot" of the game state with rich metadata:
- The visual state (what the player sees)
- The wireframe (mental model of what's happening)
- Timing and session information

This enables Claude to analyze gameplay by seeing both the
visual output AND the underlying context.

Self-teaching note:
This file demonstrates:
- Composition (ScreenshotBundle contains Wireframe) (Level 5: classes)
- Dataclasses with complex fields (Level 5: @dataclass)
- Optional types and defaults (Level 5: Optional, field)
- Factory methods for different capture scenarios (Level 5+)
"""

from dataclasses import dataclass, field
from typing import Optional, Any
from datetime import datetime
import base64
import json

from lmsp.introspection.wireframe import Wireframe


@dataclass
class ScreenshotBundle:
    """
    A screenshot bundle captures visual state with context.

    Contains:
    - wireframe: The mental model (code, AST, game state)
    - visual_data: Optional raw visual capture (base64 PNG)
    - metadata: Additional context (timing, session info)

    Usage:
        # Capture from game state
        bundle = ScreenshotBundle.capture(game_state)

        # Export for analysis
        data = bundle.to_dict()

        # Save to file
        bundle.save("screenshot_001.json")
    """

    # Core data
    wireframe: Wireframe = field(default_factory=Wireframe)
    visual_data: Optional[str] = None  # Base64-encoded image

    # Capture metadata
    capture_time: datetime = field(default_factory=datetime.now)
    capture_id: str = ""
    frame_number: int = 0

    # Session context
    session_id: Optional[str] = None
    player_id: Optional[str] = None

    # Player info
    mastery_levels: dict[str, int] = field(default_factory=dict)
    current_emotion: Optional[dict[str, Any]] = None

    # Analysis hints
    focus_area: Optional[str] = None  # "code", "tests", "progress"
    annotation: Optional[str] = None  # Human/AI annotation

    @property
    def timestamp(self) -> datetime:
        """Alias for capture_time (for test compatibility)."""
        return self.capture_time

    @classmethod
    def capture(
        cls,
        state: Any,
        player_id: Optional[str] = None,
        mastery_levels: Optional[dict[str, int]] = None,
        current_emotion: Optional[dict[str, Any]] = None,
    ) -> "ScreenshotBundle":
        """
        Capture a screenshot from game state.

        Args:
            state: GameState or GameSession object
            player_id: Optional player identifier
            mastery_levels: Optional dict of concept mastery levels
            current_emotion: Optional emotional state dict

        Returns:
            ScreenshotBundle with wireframe and metadata
        """
        # Create wireframe from state
        wireframe = Wireframe.from_game_state(state)

        # Extract session info - use passed player_id or get from state
        session_id = getattr(state, "session_id", None)
        if player_id is None:
            player_id = getattr(state, "player_id", None)

        # Generate capture ID
        capture_id = f"cap_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        return cls(
            wireframe=wireframe,
            capture_id=capture_id,
            session_id=session_id,
            player_id=player_id,
            mastery_levels=mastery_levels or {},
            current_emotion=current_emotion,
        )

    @classmethod
    def from_code(cls, code: str) -> "ScreenshotBundle":
        """
        Create a minimal screenshot from just code.

        Args:
            code: Python code string

        Returns:
            ScreenshotBundle with code analysis
        """
        wireframe = Wireframe.from_code(code)
        capture_id = f"code_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        return cls(
            wireframe=wireframe,
            capture_id=capture_id,
            focus_area="code",
        )

    def set_visual(self, image_data: bytes, format: str = "png"):
        """
        Attach visual data to the bundle.

        Args:
            image_data: Raw image bytes
            format: Image format (png, jpg, webp)
        """
        # Encode as base64 with data URI prefix
        encoded = base64.b64encode(image_data).decode("utf-8")
        self.visual_data = f"data:image/{format};base64,{encoded}"

    def get_visual_bytes(self) -> Optional[bytes]:
        """
        Get visual data as raw bytes.

        Returns:
            Decoded image bytes, or None if no visual
        """
        if not self.visual_data:
            return None

        # Strip data URI prefix if present
        if self.visual_data.startswith("data:"):
            # Format: data:image/png;base64,<data>
            _, encoded = self.visual_data.split(",", 1)
        else:
            encoded = self.visual_data

        return base64.b64decode(encoded)

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize to dictionary.

        Returns:
            Dictionary representation for JSON export
        """
        return {
            "wireframe": self.wireframe.to_dict(),
            "visual_data": self.visual_data,
            "timestamp": self.capture_time.isoformat(),
            "capture_time": self.capture_time.isoformat(),
            "capture_id": self.capture_id,
            "frame_number": self.frame_number,
            "session_id": self.session_id,
            "player_id": self.player_id,
            "mastery_levels": self.mastery_levels,
            "current_emotion": self.current_emotion,
            "focus_area": self.focus_area,
            "annotation": self.annotation,
        }

    def to_json(self) -> str:
        """
        Serialize to JSON string.

        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ScreenshotBundle":
        """
        Deserialize from dictionary.

        Args:
            data: Dictionary representation

        Returns:
            ScreenshotBundle object
        """
        # Restore wireframe
        wireframe_data = data.get("wireframe", {})
        wireframe = Wireframe.from_dict(wireframe_data)

        # Restore capture time
        capture_time = datetime.now()
        if data.get("capture_time"):
            capture_time = datetime.fromisoformat(data["capture_time"])

        return cls(
            wireframe=wireframe,
            visual_data=data.get("visual_data"),
            capture_time=capture_time,
            capture_id=data.get("capture_id", ""),
            frame_number=data.get("frame_number", 0),
            session_id=data.get("session_id"),
            player_id=data.get("player_id"),
            focus_area=data.get("focus_area"),
            annotation=data.get("annotation"),
        )

    def save(self, filepath: str):
        """
        Save bundle to JSON file.

        Args:
            filepath: Path to save file
        """
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, filepath: str) -> "ScreenshotBundle":
        """
        Load bundle from JSON file.

        Args:
            filepath: Path to load from

        Returns:
            ScreenshotBundle object
        """
        with open(filepath, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def __repr__(self) -> str:
        """String representation."""
        has_visual = "visual" if self.visual_data else "no-visual"
        return (
            f"ScreenshotBundle(id={self.capture_id}, "
            f"lines={self.wireframe.line_count}, {has_visual})"
        )


# Self-teaching note:
#
# This file demonstrates:
# - Composition: ScreenshotBundle contains a Wireframe
# - Factory methods: capture(), from_code(), from_dict()
# - Base64 encoding for binary data in JSON
# - Data URI format for inline images
# - File I/O with context managers (with open...)
# - Optional chaining with getattr() defaults
#
# Key concepts:
# 1. Composition over inheritance - Bundle HAS-A Wireframe
# 2. Factory methods - Multiple ways to create objects
# 3. Serialization - Converting objects to/from JSON
# 4. Binary data handling - Base64 for images
# 5. Data URIs - Standard format for inline data
#
# The learner will encounter this AFTER mastering:
# - Level 4: File I/O, JSON
# - Level 5: Classes, dataclasses
# - Level 6: Design patterns, serialization
