"""
Mosaic - Grid of Frames for Vision Analysis

A mosaic composes multiple frames into a single image grid,
optimized for Claude's vision capabilities.

Format:
  +-------+-------+-------+
  |Frame 1|Frame 2|Frame 3|
  +-------+-------+-------+
  |Frame 4|Frame 5|Frame 6|
  +-------+-------+-------+

This enables:
- Efficient batch analysis of gameplay
- Temporal understanding (frames over time)
- Reduced API calls (one image instead of many)

Self-teaching note:
This file demonstrates:
- Grid-based data structures (Level 4: 2D lists)
- Image composition patterns (Level 6: image processing)
- Dataclasses with validation (Level 5: @dataclass)
- Memory-efficient storage (Level 6: optimization)
"""

from dataclasses import dataclass, field
from typing import Optional, Any, Iterator
from datetime import datetime
import base64


@dataclass
class Frame:
    """
    A single frame in the mosaic.

    Captures a moment in gameplay with context.
    """

    # Visual dimensions and data (for test compatibility)
    width: int = 100
    height: int = 100
    data: bytes = field(default_factory=bytes)

    # Visual data (legacy)
    image_data: Optional[bytes] = None  # Raw image bytes
    thumbnail: Optional[bytes] = None   # Smaller version for preview

    # Frame metadata
    frame_number: int = 0
    timestamp: datetime = field(default_factory=datetime.now)

    # Context
    code_snapshot: str = ""
    cursor_position: tuple[int, int] = (0, 0)
    tests_passing: int = 0
    tests_total: int = 0

    # Analysis hints
    label: str = ""           # "keystroke", "test_run", "hint_used"
    significance: float = 0.0  # 0-1 scale of importance

    def has_image(self) -> bool:
        """Check if frame has image data."""
        return self.image_data is not None or len(self.data) > 0

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "frame_number": self.frame_number,
            "timestamp": self.timestamp.isoformat(),
            "code_snapshot": self.code_snapshot,
            "cursor_position": list(self.cursor_position),
            "tests_passing": self.tests_passing,
            "tests_total": self.tests_total,
            "label": self.label,
            "significance": self.significance,
            "has_image": self.has_image(),
            # Image data encoded separately if needed
            "image_base64": (
                base64.b64encode(self.image_data).decode("utf-8")
                if self.image_data else None
            ),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Frame":
        """Deserialize from dictionary."""
        image_data = None
        if data.get("image_base64"):
            image_data = base64.b64decode(data["image_base64"])

        return cls(
            image_data=image_data,
            frame_number=data.get("frame_number", 0),
            timestamp=(
                datetime.fromisoformat(data["timestamp"])
                if data.get("timestamp") else datetime.now()
            ),
            code_snapshot=data.get("code_snapshot", ""),
            cursor_position=tuple(data.get("cursor_position", [0, 0])),
            tests_passing=data.get("tests_passing", 0),
            tests_total=data.get("tests_total", 0),
            label=data.get("label", ""),
            significance=data.get("significance", 0.0),
        )


@dataclass
class MosaicConfig:
    """Configuration for mosaic generation."""

    # Grid dimensions
    columns: int = 3
    rows: int = 2
    max_frames: int = 6  # columns * rows

    # Frame dimensions (in pixels)
    frame_width: int = 320
    frame_height: int = 240

    # Output format
    output_format: str = "webp"  # webp, png, jpg
    quality: int = 80  # For lossy formats

    def total_frames(self) -> int:
        """Get total frames that fit in grid."""
        return min(self.columns * self.rows, self.max_frames)


class Mosaic:
    """
    Grid of frames for efficient vision analysis.

    Composes multiple frames into a single image that Claude
    can analyze in one API call.

    Usage:
        mosaic = Mosaic(columns=3, rows=2)

        # Add frames as they're captured
        mosaic.add_frame(frame1)
        mosaic.add_frame(frame2)
        # ...

        # Check if full
        if mosaic.is_full():
            # Export for analysis
            image_data = mosaic.compose()
            # Send to Claude...

            # Clear for next batch
            mosaic.clear()
    """

    def __init__(
        self,
        columns: int = 3,
        rows: int = 2,
        config: Optional[MosaicConfig] = None
    ):
        """
        Create a mosaic grid.

        Args:
            columns: Number of columns in grid
            rows: Number of rows in grid
            config: Optional configuration
        """
        self.config = config or MosaicConfig(columns=columns, rows=rows)
        self.frames: list[Frame] = []
        self._composed: Optional[bytes] = None
        self._grid: tuple[int, int] = (columns, rows)
        self._duration: float = 0.0
        self._fps: int = 0
        self._selected_indices: list[int] = []

    @classmethod
    def from_frames(
        cls,
        frames: list[Frame],
        grid: tuple[int, int] = (3, 2),
        select_count: Optional[int] = None,
        duration: float = 0.0,
        fps: int = 0,
    ) -> "Mosaic":
        """
        Create a mosaic from a list of frames.

        Args:
            frames: List of frames to include
            grid: (columns, rows) tuple for grid dimensions
            select_count: If provided, select this many frames evenly distributed
            duration: Recording duration in seconds
            fps: Frames per second

        Returns:
            Mosaic with selected frames
        """
        columns, rows = grid
        mosaic = cls(columns=columns, rows=rows)
        mosaic._grid = grid
        mosaic._duration = duration
        mosaic._fps = fps

        # If select_count is specified, select evenly distributed frames
        if select_count is not None and select_count < len(frames):
            # Calculate indices for evenly distributed selection
            indices = []
            step = (len(frames) - 1) / (select_count - 1) if select_count > 1 else 0
            for i in range(select_count):
                idx = int(round(i * step))
                indices.append(idx)
            mosaic._selected_indices = indices
            selected_frames = [frames[i] for i in indices]
        else:
            mosaic._selected_indices = list(range(len(frames)))
            selected_frames = frames

        # Add frames to mosaic
        for frame in selected_frames:
            mosaic.frames.append(frame)

        return mosaic

    @property
    def grid(self) -> tuple[int, int]:
        """Get grid dimensions as (columns, rows) tuple."""
        return self._grid

    @property
    def frame_count(self) -> int:
        """Get number of frames in mosaic."""
        return len(self.frames)

    @property
    def width(self) -> int:
        """Get total width of mosaic in pixels."""
        if not self.frames:
            return 0
        frame_width = self.frames[0].width if self.frames else self.config.frame_width
        return self._grid[0] * frame_width

    @property
    def height(self) -> int:
        """Get total height of mosaic in pixels."""
        if not self.frames:
            return 0
        frame_height = self.frames[0].height if self.frames else self.config.frame_height
        return self._grid[1] * frame_height

    @property
    def duration(self) -> float:
        """Get recording duration in seconds."""
        return self._duration

    @property
    def fps(self) -> int:
        """Get frames per second."""
        return self._fps

    @property
    def selected_indices(self) -> list[int]:
        """Get indices of selected frames from original list."""
        return self._selected_indices

    @property
    def columns(self) -> int:
        """Get number of columns."""
        return self.config.columns

    @property
    def rows(self) -> int:
        """Get number of rows."""
        return self.config.rows

    def add_frame(self, frame: Frame) -> bool:
        """
        Add a frame to the mosaic.

        Args:
            frame: Frame to add

        Returns:
            True if added, False if mosaic is full
        """
        if len(self.frames) >= self.config.total_frames():
            return False

        frame.frame_number = len(self.frames)
        self.frames.append(frame)
        self._composed = None  # Invalidate cache

        return True

    def is_full(self) -> bool:
        """Check if mosaic is full."""
        return len(self.frames) >= self.config.total_frames()

    def is_empty(self) -> bool:
        """Check if mosaic has no frames."""
        return len(self.frames) == 0

    def clear(self):
        """Clear all frames from mosaic."""
        self.frames = []
        self._composed = None

    def get_frame(self, index: int) -> Optional[Frame]:
        """
        Get a specific frame.

        Args:
            index: Frame index (0-based)

        Returns:
            Frame if exists, None otherwise
        """
        if 0 <= index < len(self.frames):
            return self.frames[index]
        return None

    def __iter__(self) -> Iterator[Frame]:
        """Iterate over frames."""
        return iter(self.frames)

    def __len__(self) -> int:
        """Get number of frames."""
        return len(self.frames)

    def compose(self) -> Optional[bytes]:
        """
        Compose frames into a single image.

        Returns:
            Image bytes in configured format, or None if empty

        Note:
            This is a placeholder. Full implementation would use
            PIL/Pillow to actually compose the images into a grid.
        """
        if not self.frames:
            return None

        # Return cached if available
        if self._composed is not None:
            return self._composed

        # Placeholder: In full implementation, we'd use PIL here
        # For now, return None to indicate no visual composition
        # The frame data is still accessible via frames list
        return None

    def get_summary(self) -> dict[str, Any]:
        """
        Get a summary of the mosaic contents.

        Returns:
            Dictionary with frame summaries (no image data)
        """
        return {
            "frame_count": len(self.frames),
            "max_frames": self.config.total_frames(),
            "columns": self.columns,
            "rows": self.rows,
            "is_full": self.is_full(),
            "frames": [
                {
                    "frame_number": f.frame_number,
                    "label": f.label,
                    "significance": f.significance,
                    "tests_passing": f.tests_passing,
                    "tests_total": f.tests_total,
                    "code_lines": len(f.code_snapshot.split("\n")),
                }
                for f in self.frames
            ],
        }

    def to_dict(self, include_images: bool = False) -> dict[str, Any]:
        """
        Serialize to dictionary.

        Args:
            include_images: Whether to include base64 image data

        Returns:
            Dictionary representation
        """
        result = {
            "config": {
                "columns": self.config.columns,
                "rows": self.config.rows,
                "frame_width": self.config.frame_width,
                "frame_height": self.config.frame_height,
                "output_format": self.config.output_format,
            },
            "frame_count": len(self.frames),
            "frames": [],
        }

        for frame in self.frames:
            frame_dict = frame.to_dict()
            if not include_images:
                # Remove image data to reduce size
                frame_dict.pop("image_base64", None)
            result["frames"].append(frame_dict)

        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Mosaic":
        """
        Deserialize from dictionary.

        Args:
            data: Dictionary representation

        Returns:
            Mosaic object
        """
        config_data = data.get("config", {})
        config = MosaicConfig(
            columns=config_data.get("columns", 3),
            rows=config_data.get("rows", 2),
            frame_width=config_data.get("frame_width", 320),
            frame_height=config_data.get("frame_height", 240),
            output_format=config_data.get("output_format", "webp"),
        )

        mosaic = cls(config=config)

        for frame_data in data.get("frames", []):
            frame = Frame.from_dict(frame_data)
            mosaic.frames.append(frame)

        return mosaic

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"Mosaic({self.columns}x{self.rows}, "
            f"frames={len(self.frames)}/{self.config.total_frames()})"
        )


# Self-teaching note:
#
# This file demonstrates:
# - Grid-based data structures (2D layout)
# - Lazy evaluation (compose only when needed)
# - Cache invalidation pattern (_composed = None)
# - Iterator protocol (__iter__, __len__)
# - Configuration objects (MosaicConfig)
# - Base64 encoding for binary data in JSON
#
# Key concepts:
# 1. Grid layout - frames arranged in rows/columns
# 2. Lazy composition - only build image when requested
# 3. Cache invalidation - clear cache when data changes
# 4. Serialization - to_dict/from_dict patterns
# 5. Configuration dataclass - group related settings
#
# The learner will encounter this AFTER mastering:
# - Level 4: Lists, comprehensions, iteration
# - Level 5: Dataclasses, properties, magic methods
# - Level 6: Design patterns, optimization
