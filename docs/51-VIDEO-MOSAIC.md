# Video Mosaics - Strategic Recording for Claude Vision

## Overview

Traditional video recordings of gameplay are too large for Claude's vision API. A 5-minute session at 30fps = 9,000 frames, which is impractical to analyze.

**Solution:** Strategic video recording as **mosaic tiles**.

Instead of sending thousands of frames, we:
1. Record at strategic intervals (e.g., 10 fps)
2. Select evenly distributed frames
3. Compose them into a single grid image (mosaic)
4. Optimize for Claude vision analysis

A **4x4 mosaic** (16 frames) tells the story of a session in one image. An **8x8 mosaic** (64 frames) provides detailed analysis. Claude can see the entire progression at a glance.

---

## MosaicRecorder Implementation

The core recorder that captures and composes mosaics:

```python
import asyncio
import io
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Callable
from PIL import Image
import time


@dataclass
class MosaicConfig:
    """Configuration for mosaic recording."""

    duration_seconds: float = 60.0
    fps: int = 10  # Frames per second to capture
    grid: tuple[int, int] = (4, 4)  # Rows x Columns
    frame_size: tuple[int, int] = (400, 300)  # Resize each frame to this
    output_format: str = "webp"  # WebP for smaller size
    quality: int = 85  # WebP quality (0-100)


@dataclass
class Frame:
    """A single captured frame."""

    image: Image.Image
    timestamp: float
    metadata: dict  # Wireframe-style metadata


@dataclass
class Mosaic:
    """A composed mosaic of frames."""

    image: Image.Image
    frames: list[Frame]
    selected_indices: list[int]
    config: MosaicConfig
    start_time: float
    end_time: float

    @property
    def duration(self) -> float:
        return self.end_time - self.start_time

    @property
    def total_frames(self) -> int:
        return len(self.frames)

    @property
    def selected_count(self) -> int:
        return len(self.selected_indices)

    def save(self, path: Path):
        """Save mosaic and metadata."""
        # Save mosaic image
        if self.config.output_format == "webp":
            self.image.save(
                path.with_suffix(".webp"),
                format="WEBP",
                quality=self.config.quality,
            )
        else:
            self.image.save(path.with_suffix(".png"), format="PNG")

        # Save metadata
        metadata = {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "total_frames": self.total_frames,
            "selected_count": self.selected_count,
            "selected_indices": self.selected_indices,
            "grid": self.config.grid,
            "fps": self.config.fps,
            "frames": [
                {
                    "index": idx,
                    "timestamp": self.frames[idx].timestamp,
                    "metadata": self.frames[idx].metadata,
                }
                for idx in self.selected_indices
            ],
        }

        import json
        with open(path.with_suffix(".json"), "w") as f:
            json.dump(metadata, f, indent=2)


class MosaicRecorder:
    """Record video as mosaic tiles optimized for Claude analysis."""

    def __init__(
        self,
        capture_func: Callable[[], tuple[Image.Image, dict]],
        config: Optional[MosaicConfig] = None,
    ):
        """
        Initialize recorder.

        Args:
            capture_func: Function that returns (image, metadata) for current frame
            config: Mosaic configuration (uses defaults if None)
        """
        self.capture_func = capture_func
        self.config = config or MosaicConfig()
        self.frames: list[Frame] = []
        self.recording = False
        self.start_time = 0.0

    async def record(self) -> Mosaic:
        """Record for configured duration and return mosaic."""
        self.frames = []
        self.recording = True
        self.start_time = time.time()

        interval = 1.0 / self.config.fps
        end_time = self.start_time + self.config.duration_seconds

        while time.time() < end_time and self.recording:
            # Capture frame
            image, metadata = self.capture_func()

            # Resize to configured size
            image = image.resize(self.config.frame_size, Image.Resampling.LANCZOS)

            # Store frame
            self.frames.append(Frame(
                image=image,
                timestamp=time.time() - self.start_time,
                metadata=metadata,
            ))

            # Wait for next frame
            await asyncio.sleep(interval)

        self.recording = False
        end_time_actual = time.time()

        # Compose mosaic
        mosaic_image = self._compose_mosaic()

        # Determine selected indices
        grid_size = self.config.grid[0] * self.config.grid[1]
        selected_indices = self._select_frames(len(self.frames), grid_size)

        return Mosaic(
            image=mosaic_image,
            frames=self.frames,
            selected_indices=selected_indices,
            config=self.config,
            start_time=self.start_time,
            end_time=end_time_actual,
        )

    def stop(self):
        """Stop recording early."""
        self.recording = False

    def _select_frames(self, total: int, count: int) -> list[int]:
        """Select evenly distributed frame indices."""
        if total <= count:
            return list(range(total))

        # Evenly distributed indices
        step = total / count
        return [int(i * step) for i in range(count)]

    def _compose_mosaic(self) -> Image.Image:
        """Compose frames into grid mosaic."""
        rows, cols = self.config.grid
        grid_size = rows * cols

        # Select frames
        selected_indices = self._select_frames(len(self.frames), grid_size)
        selected_frames = [self.frames[i] for i in selected_indices]

        # Get frame dimensions
        if not selected_frames:
            return Image.new('RGB', (800, 600), color='black')

        frame_w, frame_h = self.config.frame_size

        # Create mosaic canvas
        mosaic_w = cols * frame_w
        mosaic_h = rows * frame_h
        mosaic = Image.new('RGB', (mosaic_w, mosaic_h))

        # Paste frames into grid
        for i, frame in enumerate(selected_frames):
            row = i // cols
            col = i % cols
            x = col * frame_w
            y = row * frame_h
            mosaic.paste(frame.image, (x, y))

        return mosaic
```

---

## Frame Selection Strategies

Different strategies for selecting which frames to include:

```python
from typing import Protocol

class FrameSelector(Protocol):
    """Protocol for frame selection strategies."""

    def select(self, frames: list[Frame], count: int) -> list[int]:
        """Select frame indices to include in mosaic."""
        ...


class EvenlyDistributedSelector:
    """Select frames evenly distributed across time (default)."""

    def select(self, frames: list[Frame], count: int) -> list[int]:
        """Select evenly spaced frames."""
        total = len(frames)
        if total <= count:
            return list(range(total))

        step = total / count
        return [int(i * step) for i in range(count)]


class KeyMomentSelector:
    """Select frames at key moments (tests passing, errors, completions)."""

    def select(self, frames: list[Frame], count: int) -> list[int]:
        """Select frames at important moments."""
        # Find frames with significant events
        key_indices = []

        for i, frame in enumerate(frames):
            meta = frame.metadata

            # Key moments:
            # - First frame
            if i == 0:
                key_indices.append(i)

            # - Test state changes
            if i > 0:
                prev_meta = frames[i - 1].metadata
                if meta.get("tests_passing") != prev_meta.get("tests_passing"):
                    key_indices.append(i)

            # - Errors appear/disappear
            if meta.get("has_error") and (i == 0 or not frames[i - 1].metadata.get("has_error")):
                key_indices.append(i)

            # - Completion
            if meta.get("completed"):
                key_indices.append(i)

            # - Last frame
            if i == len(frames) - 1:
                key_indices.append(i)

        # If we have enough key moments, use them
        if len(key_indices) >= count:
            # Take evenly from key moments
            step = len(key_indices) / count
            return [key_indices[int(i * step)] for i in range(count)]

        # Otherwise, mix key moments + evenly distributed
        remaining = count - len(key_indices)
        evenly = EvenlyDistributedSelector().select(frames, count)

        # Combine and sort
        combined = list(set(key_indices + evenly[:remaining]))
        combined.sort()
        return combined[:count]


class AdaptiveSelector:
    """Select more frames during active periods, fewer during idle."""

    def select(self, frames: list[Frame], count: int) -> list[int]:
        """Select frames weighted by activity level."""
        # Calculate activity score for each frame
        activity_scores = []

        for i, frame in enumerate(frames):
            score = 0.0
            meta = frame.metadata

            # Activity indicators:
            # - Code changed
            if meta.get("code_changed"):
                score += 2.0

            # - Tests running
            if meta.get("tests_running"):
                score += 3.0

            # - Test state changed
            if i > 0 and meta.get("tests_passing") != frames[i - 1].metadata.get("tests_passing"):
                score += 5.0

            # - Cursor moved significantly
            if i > 0:
                prev_cursor = frames[i - 1].metadata.get("cursor", [0, 0])
                curr_cursor = meta.get("cursor", [0, 0])
                line_diff = abs(curr_cursor[0] - prev_cursor[0])
                if line_diff > 2:
                    score += 1.0

            # - Emotional input
            if meta.get("emotion"):
                score += 1.5

            activity_scores.append(score)

        # Normalize scores
        max_score = max(activity_scores) if activity_scores else 1.0
        normalized = [s / max_score for s in activity_scores]

        # Select frames weighted by activity
        selected = []
        total_activity = sum(normalized)

        for i in range(count):
            # Each frame "owns" a portion of the total activity
            target = (i + 0.5) * total_activity / count

            # Find frame closest to this target
            cumsum = 0.0
            for idx, score in enumerate(normalized):
                cumsum += score
                if cumsum >= target:
                    selected.append(idx)
                    break

        return sorted(set(selected))[:count]
```

---

## Grid Composition

Different grid sizes for different analysis needs:

```python
class GridComposer:
    """Compose frames into various grid layouts."""

    @staticmethod
    def compose_4x4(frames: list[Frame], frame_size: tuple[int, int]) -> Image.Image:
        """4x4 grid - good for quick overview (16 frames)."""
        return GridComposer._compose_grid(frames, (4, 4), frame_size)

    @staticmethod
    def compose_6x6(frames: list[Frame], frame_size: tuple[int, int]) -> Image.Image:
        """6x6 grid - balanced detail (36 frames)."""
        return GridComposer._compose_grid(frames, (6, 6), frame_size)

    @staticmethod
    def compose_8x8(frames: list[Frame], frame_size: tuple[int, int]) -> Image.Image:
        """8x8 grid - detailed analysis (64 frames)."""
        return GridComposer._compose_grid(frames, (8, 8), frame_size)

    @staticmethod
    def compose_timeline(frames: list[Frame], frame_size: tuple[int, int]) -> Image.Image:
        """Single row timeline - horizontal progression."""
        cols = len(frames)
        return GridComposer._compose_grid(frames, (1, cols), frame_size)

    @staticmethod
    def compose_comparison(
        frames_a: list[Frame],
        frames_b: list[Frame],
        frame_size: tuple[int, int]
    ) -> Image.Image:
        """Two-row comparison - useful for race mode."""
        cols = max(len(frames_a), len(frames_b))

        # Pad shorter list
        while len(frames_a) < cols:
            frames_a.append(Frame(
                image=Image.new('RGB', frame_size, color='black'),
                timestamp=0.0,
                metadata={},
            ))
        while len(frames_b) < cols:
            frames_b.append(Frame(
                image=Image.new('RGB', frame_size, color='black'),
                timestamp=0.0,
                metadata={},
            ))

        # Interleave frames
        combined = []
        for a, b in zip(frames_a, frames_b):
            combined.append(a)
            combined.append(b)

        return GridComposer._compose_grid(combined, (2, cols), frame_size)

    @staticmethod
    def _compose_grid(
        frames: list[Frame],
        grid: tuple[int, int],
        frame_size: tuple[int, int]
    ) -> Image.Image:
        """Generic grid composition."""
        rows, cols = grid
        frame_w, frame_h = frame_size

        mosaic_w = cols * frame_w
        mosaic_h = rows * frame_h
        mosaic = Image.new('RGB', (mosaic_w, mosaic_h))

        for i, frame in enumerate(frames[:rows * cols]):
            row = i // cols
            col = i % cols
            x = col * frame_w
            y = row * frame_h
            mosaic.paste(frame.image, (x, y))

        return mosaic
```

---

## Mosaic Composition Method

The `compose_mosaic()` method with various options:

```python
class MosaicComposer:
    """Advanced mosaic composition with annotations."""

    @staticmethod
    def compose_basic(frames: list[Frame], config: MosaicConfig) -> Image.Image:
        """Basic grid composition (no annotations)."""
        rows, cols = config.grid
        frame_w, frame_h = config.frame_size

        mosaic = Image.new('RGB', (cols * frame_w, rows * frame_h))

        for i, frame in enumerate(frames):
            row = i // cols
            col = i % cols
            mosaic.paste(frame.image, (col * frame_w, row * frame_h))

        return mosaic

    @staticmethod
    def compose_annotated(frames: list[Frame], config: MosaicConfig) -> Image.Image:
        """Mosaic with timestamp and test count annotations."""
        from PIL import ImageDraw, ImageFont

        rows, cols = config.grid
        frame_w, frame_h = config.frame_size

        # Create base mosaic
        mosaic = MosaicComposer.compose_basic(frames, config)

        # Draw annotations
        draw = ImageDraw.Draw(mosaic)

        try:
            # Try to use a nice font
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        except:
            font = ImageFont.load_default()

        for i, frame in enumerate(frames):
            row = i // cols
            col = i % cols
            x = col * frame_w
            y = row * frame_h

            # Draw timestamp
            timestamp = f"{frame.timestamp:.1f}s"
            draw.text((x + 5, y + 5), timestamp, fill='yellow', font=font)

            # Draw test count if available
            meta = frame.metadata
            if "tests_passing" in meta and "tests_total" in meta:
                tests = f"{meta['tests_passing']}/{meta['tests_total']}"
                draw.text((x + 5, y + frame_h - 20), tests, fill='lime', font=font)

        return mosaic

    @staticmethod
    def compose_highlighted(frames: list[Frame], config: MosaicConfig) -> Image.Image:
        """Mosaic with key frames highlighted."""
        from PIL import ImageDraw

        # Create annotated base
        mosaic = MosaicComposer.compose_annotated(frames, config)

        rows, cols = config.grid
        frame_w, frame_h = config.frame_size

        draw = ImageDraw.Draw(mosaic)

        for i, frame in enumerate(frames):
            meta = frame.metadata

            # Highlight key moments
            color = None

            if meta.get("completed"):
                color = 'lime'  # Green for completion
            elif meta.get("has_error"):
                color = 'red'  # Red for errors
            elif meta.get("tests_running"):
                color = 'yellow'  # Yellow for active testing

            if color:
                row = i // cols
                col = i % cols
                x = col * frame_w
                y = row * frame_h

                # Draw border
                draw.rectangle(
                    [(x, y), (x + frame_w - 1, y + frame_h - 1)],
                    outline=color,
                    width=3,
                )

        return mosaic
```

---

## Claude Vision Optimization

Optimizing mosaics specifically for Claude's vision API:

```python
class ClaudeVisionOptimizer:
    """Optimize mosaics for Claude vision analysis."""

    @staticmethod
    def optimize_for_claude(mosaic: Mosaic) -> dict:
        """Prepare mosaic for Claude API."""

        # Convert image to bytes
        buffer = io.BytesIO()
        mosaic.image.save(buffer, format="WEBP", quality=85)
        image_bytes = buffer.getvalue()

        # Build context
        context = {
            "type": "mosaic",
            "duration": round(mosaic.duration, 1),
            "total_frames": mosaic.total_frames,
            "selected_frames": mosaic.selected_count,
            "grid": f"{mosaic.config.grid[0]}x{mosaic.config.grid[1]}",
            "timeline": [
                {
                    "position": f"Row {idx // mosaic.config.grid[1]}, Col {idx % mosaic.config.grid[1]}",
                    "timestamp": f"{mosaic.frames[i].timestamp:.1f}s",
                    "tests": f"{mosaic.frames[i].metadata.get('tests_passing', '?')}/{mosaic.frames[i].metadata.get('tests_total', '?')}",
                    "event": ClaudeVisionOptimizer._detect_event(mosaic.frames[i].metadata),
                }
                for idx, i in enumerate(mosaic.selected_indices)
            ],
        }

        return {
            "image": image_bytes,
            "context": context,
        }

    @staticmethod
    def _detect_event(metadata: dict) -> str:
        """Detect what happened in this frame."""
        if metadata.get("completed"):
            return "✓ Completed"
        if metadata.get("has_error"):
            return "✗ Error"
        if metadata.get("tests_running"):
            return "⚙ Testing"
        if metadata.get("code_changed"):
            return "✎ Coding"
        return "—"

    @staticmethod
    def generate_claude_prompt(mosaic: Mosaic, question: str) -> str:
        """Generate Claude prompt for mosaic analysis."""
        opt = ClaudeVisionOptimizer.optimize_for_claude(mosaic)
        ctx = opt["context"]

        timeline_str = "\n".join(
            f"{t['position']} @ {t['timestamp']} - Tests: {t['tests']} - {t['event']}"
            for t in ctx["timeline"]
        )

        return f"""You're analyzing a mosaic of {ctx['selected_frames']} frames from a {ctx['duration']}s LMSP session.

**Mosaic Layout:** {ctx['grid']} grid
**Total Recorded:** {ctx['total_frames']} frames
**Selected for Analysis:** {ctx['selected_frames']} frames

**Timeline:**
{timeline_str}

**Question:** {question}

Please analyze the progression shown in the mosaic and provide insights based on the visual changes and metadata.
"""
```

---

## WebP Output Format

WebP-specific optimization:

```python
class WebPOptimizer:
    """WebP-specific optimization for mosaic output."""

    @staticmethod
    def save_webp(image: Image.Image, path: Path, quality: int = 85) -> int:
        """
        Save as optimized WebP.

        Returns: File size in bytes
        """
        image.save(
            path,
            format="WEBP",
            quality=quality,
            method=6,  # Slowest but best compression
        )

        return path.stat().st_size

    @staticmethod
    def compare_formats(image: Image.Image) -> dict:
        """Compare file sizes across formats."""
        sizes = {}

        # PNG
        png_buffer = io.BytesIO()
        image.save(png_buffer, format="PNG", optimize=True)
        sizes["png"] = len(png_buffer.getvalue())

        # JPEG
        jpg_buffer = io.BytesIO()
        image.save(jpg_buffer, format="JPEG", quality=85)
        sizes["jpeg"] = len(jpg_buffer.getvalue())

        # WebP (various qualities)
        for quality in [70, 85, 95]:
            webp_buffer = io.BytesIO()
            image.save(webp_buffer, format="WEBP", quality=quality)
            sizes[f"webp_{quality}"] = len(webp_buffer.getvalue())

        return sizes
```

---

## Usage Examples

```python
# Basic mosaic recording
from lmsp.introspection.mosaic import MosaicRecorder, MosaicConfig

def capture_frame():
    """Capture current game state."""
    img = game.render_to_image()
    metadata = {
        "tests_passing": game.tests_passing,
        "tests_total": game.tests_total,
        "cursor": [game.cursor.line, game.cursor.column],
        "code_changed": game.code_dirty,
    }
    return img, metadata

config = MosaicConfig(
    duration_seconds=60.0,
    fps=10,
    grid=(4, 4),
    output_format="webp",
)

recorder = MosaicRecorder(capture_frame, config)
mosaic = await recorder.record()

# Save
mosaic.save(Path("~/.lmsp/mosaics/session_001").expanduser())

# Analyze with Claude
from lmsp.introspection.mosaic import ClaudeVisionOptimizer

prompt = ClaudeVisionOptimizer.generate_claude_prompt(
    mosaic,
    question="What was the learner's strategy? Did they struggle with anything?"
)

response = claude_api.analyze(prompt, images=[mosaic.image])

# Try different grid sizes
for grid in [(4, 4), (6, 6), (8, 8)]:
    config.grid = grid
    # ... record and compare

# Use adaptive selection
from lmsp.introspection.mosaic import AdaptiveSelector

selector = AdaptiveSelector()
selected = selector.select(recorder.frames, 16)
print(f"Adaptive selection: {selected}")
```

---

## Integration with Discovery Primitives

```python
# /video command (Level 3)
@command("/video <duration>", unlock_level=3)
async def cmd_video(game, duration: float = 60.0):
    """Record strategic video."""
    from lmsp.introspection.mosaic import MosaicRecorder, MosaicConfig

    config = MosaicConfig(duration_seconds=duration)
    recorder = MosaicRecorder(game.capture_frame, config)

    print(f"Recording {duration}s mosaic...")
    mosaic = await recorder.record()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = Path(f"~/.lmsp/mosaics/{game.player.id}/{timestamp}").expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)

    mosaic.save(path)

    print(f"Mosaic saved: {path}.webp ({mosaic.selected_count} frames)")
    print(f"Duration: {mosaic.duration:.1f}s")

    return mosaic

# /mosaic command (Level 3)
@command("/mosaic <grid>", unlock_level=3)
async def cmd_mosaic(game, grid: str = "4x4"):
    """Generate frame mosaic."""
    rows, cols = map(int, grid.split("x"))

    config = MosaicConfig(grid=(rows, cols))
    # ... same as /video
```

---

## Self-Teaching Note

This file demonstrates:
- **Async/await** (Level 6+: Async programming) - Asynchronous recording
- **PIL/Image** (Standard library) - Advanced image manipulation
- **Dataclasses** (Level 5: Classes) - Clean data structures
- **Protocols** (Professional Python) - Type-safe strategy pattern
- **List comprehensions** (Level 4: Intermediate) - Efficient data transformation
- **IO operations** (Level 4+: Files and buffers) - In-memory image buffers

Prerequisites to understand this file:
- Level 2: Collections (lists, dicts)
- Level 3: Functions (def, return, async/await)
- Level 4: Comprehensions, lambda
- Level 5: Classes (@dataclass, __init__)

The learner will encounter this file when building the video mosaic system for LMSP.
