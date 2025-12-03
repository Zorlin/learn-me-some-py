"""
Video Recorder - Strategic Frame Recording

Records gameplay as a series of strategically-selected frames,
not continuous video. This enables efficient analysis without
overwhelming storage or API calls.

Strategy:
- Capture on significant events (code changes, test runs, emotions)
- Skip redundant frames (no change from previous)
- Compose into mosaics for Claude analysis

Self-teaching note:
This file demonstrates:
- Event-driven recording (Level 5: callbacks)
- State comparison for deduplication (Level 4: comparison)
- Queue-based buffering (Level 5: data structures)
- Context managers for resources (Level 5: with statements)
"""

from dataclasses import dataclass, field
from typing import Optional, Any, Callable
from datetime import datetime
from pathlib import Path
import json
from collections import deque

from lmsp.introspection.wireframe import Wireframe
from lmsp.introspection.mosaic import Mosaic, Frame, MosaicConfig


@dataclass
class RecordingConfig:
    """Configuration for video recording."""

    # Frame capture settings
    max_frames_in_memory: int = 100  # Buffer size
    mosaic_columns: int = 3
    mosaic_rows: int = 2

    # Event-based capture triggers
    capture_on_code_change: bool = True
    capture_on_test_run: bool = True
    capture_on_emotion: bool = True
    capture_on_hint: bool = True
    capture_on_checkpoint: bool = True

    # Deduplication
    min_change_threshold: int = 10  # Min chars changed to capture
    min_time_between_frames: float = 0.5  # seconds

    # Output settings
    output_dir: Optional[Path] = None
    output_format: str = "webp"


class VideoRecorder:
    """
    Strategic video recorder for gameplay analysis.

    Captures frames based on significant events, not continuously.
    Composes frames into mosaics for efficient Claude analysis.

    Usage:
        recorder = VideoRecorder()
        recorder.start()

        # During gameplay, capture significant moments
        recorder.capture_frame(wireframe, label="code_change")
        recorder.capture_frame(wireframe, label="test_run")

        # When mosaic is ready
        if recorder.has_mosaic_ready():
            mosaic = recorder.get_current_mosaic()
            # Send to Claude for analysis...

        recorder.stop()
    """

    def __init__(self, config: Optional[RecordingConfig] = None):
        """
        Create a video recorder.

        Args:
            config: Recording configuration
        """
        self.config = config or RecordingConfig()

        # Recording state
        self._is_recording = False
        self._start_time: Optional[datetime] = None
        self._frame_count = 0

        # Frame buffer (limited size, drops oldest)
        self._frames: deque[Frame] = deque(maxlen=self.config.max_frames_in_memory)

        # Current mosaic being built
        self._current_mosaic = Mosaic(
            columns=self.config.mosaic_columns,
            rows=self.config.mosaic_rows,
        )

        # Completed mosaics
        self._mosaics: list[Mosaic] = []

        # Last frame state for deduplication
        self._last_code: str = ""
        self._last_capture_time: float = 0

        # Event callbacks
        self._on_mosaic_complete: list[Callable[[Mosaic], None]] = []

    @property
    def is_recording(self) -> bool:
        """Check if recording is active."""
        return self._is_recording

    @property
    def frame_count(self) -> int:
        """Get total frames captured."""
        return self._frame_count

    @property
    def start_time(self) -> Optional[datetime]:
        """Get recording start time."""
        return self._start_time

    @property
    def frames(self) -> list[Frame]:
        """Get list of captured frames."""
        return list(self._frames)

    def start(self):
        """Start recording."""
        self._is_recording = True
        self._start_time = datetime.now()
        self._frame_count = 0

    def stop(self):
        """Stop recording."""
        self._is_recording = False

        # Finalize any partial mosaic
        if not self._current_mosaic.is_empty():
            self._mosaics.append(self._current_mosaic)
            self._current_mosaic = Mosaic(
                columns=self.config.mosaic_columns,
                rows=self.config.mosaic_rows,
            )

    def capture_frame(
        self,
        state_or_wireframe: Any = None,
        label: str = "",
        significance: float = 0.5,
        force: bool = False
    ) -> bool:
        """
        Capture a frame if conditions are met.

        Args:
            state_or_wireframe: GameState or Wireframe object
            label: Event type label
            significance: Importance 0-1
            force: Capture even if duplicate

        Returns:
            True if frame was captured
        """
        if not self._is_recording:
            return False

        # Handle different input types
        if state_or_wireframe is None:
            code = ""
            cursor_position = (0, 0)
            tests_passing = 0
            tests_total = 0
        elif isinstance(state_or_wireframe, Wireframe):
            code = state_or_wireframe.code
            cursor_position = state_or_wireframe.cursor_position
            tests_passing = state_or_wireframe.tests_passing
            tests_total = state_or_wireframe.tests_total
        else:
            # Assume it's a GameState
            code = getattr(state_or_wireframe, "current_code", "")
            cursor_position = getattr(state_or_wireframe, "cursor_position", (0, 0))
            tests_passing = getattr(state_or_wireframe, "tests_passing", 0)
            tests_total = getattr(state_or_wireframe, "tests_total", 0)

        # Check deduplication (unless forced)
        if not force:
            # Time-based throttling
            import time
            current_time = time.time()
            if current_time - self._last_capture_time < self.config.min_time_between_frames:
                return False

            # Content-based deduplication
            if self._is_duplicate(code):
                return False

        # Create frame
        frame = Frame(
            frame_number=self._frame_count,
            code_snapshot=code,
            cursor_position=cursor_position,
            tests_passing=tests_passing,
            tests_total=tests_total,
            label=label,
            significance=significance,
        )

        # Add to buffer
        self._frames.append(frame)

        # Add to current mosaic
        added = self._current_mosaic.add_frame(frame)

        # Check if mosaic is complete
        if self._current_mosaic.is_full():
            self._finalize_mosaic()

        # Update state
        self._frame_count += 1
        self._last_code = code
        import time
        self._last_capture_time = time.time()

        return True

    def to_mosaic(self, grid: tuple[int, int] = (3, 2)) -> Mosaic:
        """
        Convert recorded frames to a mosaic.

        Args:
            grid: (columns, rows) tuple for mosaic grid

        Returns:
            Mosaic with recorded frames
        """
        frames_list = list(self._frames)
        return Mosaic.from_frames(frames_list, grid=grid)

    def _is_duplicate(self, code: str) -> bool:
        """Check if code is too similar to last capture."""
        if not self._last_code:
            return False

        # Calculate change amount
        change = abs(len(code) - len(self._last_code))

        # Simple difference check
        if code == self._last_code:
            return True

        if change < self.config.min_change_threshold:
            # Small change - check if content is substantially different
            # Using simple character count for now
            return change < self.config.min_change_threshold

        return False

    def _finalize_mosaic(self):
        """Finalize current mosaic and start a new one."""
        self._mosaics.append(self._current_mosaic)

        # Notify callbacks
        for callback in self._on_mosaic_complete:
            callback(self._current_mosaic)

        # Start new mosaic
        self._current_mosaic = Mosaic(
            columns=self.config.mosaic_columns,
            rows=self.config.mosaic_rows,
        )

    def has_mosaic_ready(self) -> bool:
        """Check if there's a complete mosaic ready."""
        return len(self._mosaics) > 0

    def get_current_mosaic(self) -> Optional[Mosaic]:
        """
        Get the current (possibly incomplete) mosaic.

        Returns:
            Current mosaic or None if empty
        """
        if self._current_mosaic.is_empty():
            return None
        return self._current_mosaic

    def pop_completed_mosaic(self) -> Optional[Mosaic]:
        """
        Get and remove the oldest completed mosaic.

        Returns:
            Completed mosaic or None
        """
        if self._mosaics:
            return self._mosaics.pop(0)
        return None

    def get_all_mosaics(self) -> list[Mosaic]:
        """Get all completed mosaics."""
        return list(self._mosaics)

    def get_recent_frames(self, count: int = 10) -> list[Frame]:
        """
        Get most recent frames.

        Args:
            count: Number of frames to return

        Returns:
            List of recent frames (newest last)
        """
        frames = list(self._frames)
        return frames[-count:] if len(frames) > count else frames

    def on_mosaic_complete(self, callback: Callable[[Mosaic], None]):
        """
        Register callback for when a mosaic is completed.

        Args:
            callback: Function to call with completed mosaic
        """
        self._on_mosaic_complete.append(callback)

    def get_statistics(self) -> dict[str, Any]:
        """
        Get recording statistics.

        Returns:
            Dictionary with recording stats
        """
        return {
            "is_recording": self._is_recording,
            "frame_count": self._frame_count,
            "frames_in_buffer": len(self._frames),
            "completed_mosaics": len(self._mosaics),
            "current_mosaic_frames": len(self._current_mosaic),
            "start_time": self._start_time.isoformat() if self._start_time else None,
        }

    def save_session(self, filepath: Path):
        """
        Save recording session to file.

        Args:
            filepath: Path to save file
        """
        data = {
            "frame_count": self._frame_count,
            "start_time": self._start_time.isoformat() if self._start_time else None,
            "mosaics": [m.to_dict(include_images=False) for m in self._mosaics],
            "current_mosaic": self._current_mosaic.to_dict(include_images=False),
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load_session(cls, filepath: Path) -> "VideoRecorder":
        """
        Load recording session from file.

        Args:
            filepath: Path to load from

        Returns:
            VideoRecorder with restored state
        """
        with open(filepath, "r") as f:
            data = json.load(f)

        recorder = cls()
        recorder._frame_count = data.get("frame_count", 0)

        if data.get("start_time"):
            recorder._start_time = datetime.fromisoformat(data["start_time"])

        for mosaic_data in data.get("mosaics", []):
            recorder._mosaics.append(Mosaic.from_dict(mosaic_data))

        if data.get("current_mosaic"):
            recorder._current_mosaic = Mosaic.from_dict(data["current_mosaic"])

        return recorder

    def __repr__(self) -> str:
        """String representation."""
        status = "recording" if self._is_recording else "stopped"
        return f"VideoRecorder({status}, frames={self._frame_count})"


# Self-teaching note:
#
# This file demonstrates:
# - Event-driven architecture (capture on events)
# - Deduplication strategies (avoid redundant captures)
# - Double-ended queue (deque with maxlen)
# - Callback registration pattern (on_mosaic_complete)
# - Property decorators for computed values
# - Path objects for file handling
#
# Key concepts:
# 1. Strategic recording - capture important moments, not everything
# 2. Deduplication - skip frames that are too similar
# 3. Buffering - deque with max size drops oldest
# 4. Callbacks - notify when mosaic is complete
# 5. Serialization - save/load session state
#
# The learner will encounter this AFTER mastering:
# - Level 4: Collections, comparison
# - Level 5: Classes, callbacks, properties
# - Level 6: Design patterns, optimization
