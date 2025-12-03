# TAS Replay and Analysis

## Overview

The LMSP replay system enables playback of recorded sessions for learning, comparison, and analysis. This document covers the replay engine, speedrun comparison tools, approach analysis, and interactive replay features.

## Replay Engine

### Basic Replay

The core replayer applies recorded events to recreate a gameplay session:

```python
import asyncio
from typing import Optional
from dataclasses import dataclass

class Replayer:
    """Replay recordings for learning and analysis."""

    def __init__(self, recording: Recording):
        self.recording = recording
        self.current_idx: int = 0
        self.current_state: Optional[GameState] = None
        self.speed: float = 1.0
        self.paused: bool = False

    async def replay(self, speed: float = 1.0, on_event=None):
        """
        Replay recording at given speed.

        Args:
            speed: Playback speed multiplier (1.0 = real-time, 2.0 = 2x speed)
            on_event: Callback function called for each event
        """
        self.speed = speed
        self.current_idx = 0

        if not self.recording.events:
            return

        # Apply first event immediately
        self.current_state = self.recording.events[0].game_state
        if on_event:
            await on_event(self.recording.events[0])

        # Replay subsequent events with timing
        for i in range(1, len(self.recording.events)):
            if self.paused:
                while self.paused:
                    await asyncio.sleep(0.1)

            event = self.recording.events[i]
            prev_event = self.recording.events[i-1]

            # Calculate delay
            delay = (event.timestamp - prev_event.timestamp) / self.speed
            if delay > 0:
                await asyncio.sleep(delay)

            # Apply event
            self.current_idx = i
            self.current_state = event.game_state

            # Callback
            if on_event:
                await on_event(event)

    def pause(self):
        """Pause playback."""
        self.paused = True

    def resume(self):
        """Resume playback."""
        self.paused = False

    def set_speed(self, speed: float):
        """Change playback speed."""
        self.speed = max(0.1, min(10.0, speed))  # Clamp to [0.1, 10.0]
```

### Interactive Replay

Support for stepping, rewinding, and jumping:

```python
class InteractiveReplayer(Replayer):
    """Replayer with interactive controls."""

    async def step(self, forward: bool = True) -> RecordedEvent:
        """
        Single-step through recording.

        Args:
            forward: If True, step forward; if False, step backward

        Returns:
            The event at the new position
        """
        if forward:
            if self.current_idx < len(self.recording.events) - 1:
                self.current_idx += 1
        else:
            if self.current_idx > 0:
                self.current_idx -= 1

        event = self.recording.events[self.current_idx]
        self.current_state = event.game_state
        return event

    async def jump_to(self, timestamp: float) -> RecordedEvent:
        """
        Jump to specific timestamp in recording.

        Args:
            timestamp: Target timestamp in seconds

        Returns:
            The event at or just before the timestamp
        """
        # Binary search for event closest to timestamp
        left, right = 0, len(self.recording.events) - 1

        while left < right:
            mid = (left + right + 1) // 2
            if self.recording.events[mid].timestamp <= timestamp:
                left = mid
            else:
                right = mid - 1

        self.current_idx = left
        event = self.recording.events[self.current_idx]
        self.current_state = event.game_state
        return event

    async def jump_to_checkpoint(self, name: str) -> RecordedEvent:
        """
        Jump to a named checkpoint.

        Args:
            name: Checkpoint name

        Returns:
            The event at the checkpoint
        """
        if name not in self.recording.checkpoints:
            raise ValueError(f"Checkpoint '{name}' not found")

        idx = self.recording.checkpoints[name]
        self.current_idx = idx
        event = self.recording.events[idx]
        self.current_state = event.game_state
        return event

    async def rewind(self, steps: int = 1) -> RecordedEvent:
        """
        Step backward through recording.

        Args:
            steps: Number of steps to rewind

        Returns:
            The event at the new position
        """
        self.current_idx = max(0, self.current_idx - steps)
        event = self.recording.events[self.current_idx]
        self.current_state = event.game_state
        return event

    def get_progress(self) -> float:
        """Get playback progress as percentage (0.0 to 1.0)."""
        if not self.recording.events:
            return 0.0
        return self.current_idx / (len(self.recording.events) - 1)
```

## Speedrun Comparison

### Recording Comparison

Compare two recordings of the same challenge:

```python
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class ComparisonMetrics:
    """Metrics comparing two recordings."""

    time_difference: float  # Seconds (positive = recording_a was slower)
    event_count_difference: int  # Number of events
    keystrokes_difference: int  # Keystroke count
    hints_used_difference: int  # Hint usage
    approach_similarity: float  # 0.0 to 1.0

    winner: str  # "a", "b", or "tie"

    def summary(self) -> str:
        """Generate human-readable summary."""
        lines = []

        if self.winner == "tie":
            lines.append("RESULT: Tie")
        else:
            lines.append(f"WINNER: Recording {self.winner.upper()}")

        lines.append(f"Time difference: {abs(self.time_difference):.2f}s")
        lines.append(f"Event difference: {abs(self.event_count_difference)}")
        lines.append(f"Keystroke difference: {abs(self.keystrokes_difference)}")
        lines.append(f"Approach similarity: {self.approach_similarity:.1%}")

        return "\n".join(lines)

class RecordingComparator:
    """Compare two recordings of the same challenge."""

    def compare(
        self,
        recording_a: Recording,
        recording_b: Recording
    ) -> ComparisonMetrics:
        """
        Compare two recordings and generate metrics.

        Args:
            recording_a: First recording
            recording_b: Second recording

        Returns:
            Comparison metrics
        """
        # Validate same challenge
        if recording_a.challenge_id != recording_b.challenge_id:
            raise ValueError("Recordings are for different challenges")

        # Calculate time difference
        time_diff = recording_a.duration - recording_b.duration

        # Count events
        event_diff = len(recording_a.events) - len(recording_b.events)

        # Count keystrokes
        keystrokes_a = self._count_keystrokes(recording_a)
        keystrokes_b = self._count_keystrokes(recording_b)
        keystroke_diff = keystrokes_a - keystrokes_b

        # Count hints
        hints_a = self._count_hints(recording_a)
        hints_b = self._count_hints(recording_b)
        hint_diff = hints_a - hints_b

        # Calculate approach similarity
        similarity = self._calculate_similarity(recording_a, recording_b)

        # Determine winner
        winner = self._determine_winner(recording_a, recording_b)

        return ComparisonMetrics(
            time_difference=time_diff,
            event_count_difference=event_diff,
            keystrokes_difference=keystroke_diff,
            hints_used_difference=hint_diff,
            approach_similarity=similarity,
            winner=winner
        )

    def _count_keystrokes(self, recording: Recording) -> int:
        """Count keystroke events in recording."""
        return sum(
            1 for event in recording.events
            if event.event.type == EventType.KEYSTROKE
        )

    def _count_hints(self, recording: Recording) -> int:
        """Count hint usage in recording."""
        # Check final state or count hint request events
        if recording.events:
            return recording.events[-1].game_state.hints_used
        return 0

    def _calculate_similarity(
        self,
        recording_a: Recording,
        recording_b: Recording
    ) -> float:
        """
        Calculate code similarity between final solutions.

        Uses difflib.SequenceMatcher for similarity ratio.
        """
        import difflib

        code_a = recording_a.final_code
        code_b = recording_b.final_code

        matcher = difflib.SequenceMatcher(None, code_a, code_b)
        return matcher.ratio()

    def _determine_winner(
        self,
        recording_a: Recording,
        recording_b: Recording
    ) -> str:
        """
        Determine winner based on multiple criteria.

        Priority:
        1. Success (passed all tests)
        2. Time (faster is better)
        3. Hints (fewer is better)
        """
        # Both must succeed to have a winner
        if recording_a.success != recording_b.success:
            if recording_a.success:
                return "a"
            else:
                return "b"

        # Neither succeeded
        if not recording_a.success and not recording_b.success:
            return "tie"

        # Compare time (allow 0.5s tolerance for ties)
        time_diff = abs(recording_a.duration - recording_b.duration)
        if time_diff < 0.5:
            return "tie"

        if recording_a.duration < recording_b.duration:
            return "a"
        else:
            return "b"
```

### Speedrun Leaderboard

Track best times across multiple recordings:

```python
from typing import List
from dataclasses import dataclass

@dataclass
class LeaderboardEntry:
    """Single leaderboard entry."""

    rank: int
    player_id: str
    time: float
    hints_used: int
    recording_path: str
    created_at: float

class SpeedrunLeaderboard:
    """Track speedrun times for a challenge."""

    def __init__(self, challenge_id: str):
        self.challenge_id = challenge_id
        self.entries: List[LeaderboardEntry] = []

    def add_recording(self, recording: Recording, path: str):
        """Add recording to leaderboard."""
        if recording.challenge_id != self.challenge_id:
            raise ValueError("Recording is for different challenge")

        if not recording.success:
            # Only successful runs make the leaderboard
            return

        # Create entry
        entry = LeaderboardEntry(
            rank=0,  # Will be calculated
            player_id=recording.player_id,
            time=recording.duration,
            hints_used=recording.events[-1].game_state.hints_used if recording.events else 0,
            recording_path=path,
            created_at=recording.created_at
        )

        # Add and re-sort
        self.entries.append(entry)
        self._update_ranks()

    def _update_ranks(self):
        """Sort entries and update ranks."""
        # Sort by time (ascending), then hints (ascending)
        self.entries.sort(key=lambda e: (e.time, e.hints_used))

        # Update ranks
        for i, entry in enumerate(self.entries):
            entry.rank = i + 1

    def get_top_n(self, n: int = 10) -> List[LeaderboardEntry]:
        """Get top N entries."""
        return self.entries[:n]

    def get_player_rank(self, player_id: str) -> Optional[LeaderboardEntry]:
        """Get best entry for a player."""
        player_entries = [e for e in self.entries if e.player_id == player_id]
        if not player_entries:
            return None
        return player_entries[0]  # Already sorted

    def display(self, top_n: int = 10) -> str:
        """Generate leaderboard display."""
        lines = [
            f"=== SPEEDRUN LEADERBOARD: {self.challenge_id} ===",
            ""
        ]

        for entry in self.get_top_n(top_n):
            lines.append(
                f"{entry.rank:2d}. {entry.player_id:20s} "
                f"{entry.time:6.2f}s "
                f"({entry.hints_used} hints)"
            )

        return "\n".join(lines)
```

## Approach Analysis

### Code Evolution Tracking

Track how code changes throughout a session:

```python
from typing import List
from dataclasses import dataclass

@dataclass
class CodeSnapshot:
    """Snapshot of code at a point in time."""

    timestamp: float
    code: str
    tests_passing: int
    tests_total: int
    event_index: int

class CodeEvolutionAnalyzer:
    """Analyze how code evolves during a recording."""

    def analyze(self, recording: Recording) -> List[CodeSnapshot]:
        """
        Extract code snapshots showing evolution.

        Returns snapshots whenever code changes significantly.
        """
        snapshots = []
        last_code = ""

        for i, event in enumerate(recording.events):
            current_code = event.game_state.current_code

            # Significant change detection
            if self._is_significant_change(last_code, current_code):
                snapshots.append(CodeSnapshot(
                    timestamp=event.timestamp,
                    code=current_code,
                    tests_passing=event.game_state.tests_passing,
                    tests_total=event.game_state.tests_total,
                    event_index=i
                ))
                last_code = current_code

        return snapshots

    def _is_significant_change(self, old_code: str, new_code: str) -> bool:
        """Determine if code change is significant enough to snapshot."""
        if not old_code and new_code:
            return True  # First code written

        if not new_code:
            return False  # Cleared

        # Count line difference
        old_lines = old_code.split('\n')
        new_lines = new_code.split('\n')

        if len(new_lines) != len(old_lines):
            return True  # Line count changed

        # Check for substantial edits (>20% lines changed)
        changed_lines = sum(
            1 for old, new in zip(old_lines, new_lines)
            if old != new
        )

        return changed_lines > len(old_lines) * 0.2

    def visualize_evolution(self, snapshots: List[CodeSnapshot]) -> str:
        """Generate visual timeline of code evolution."""
        lines = ["=== CODE EVOLUTION TIMELINE ===", ""]

        for i, snapshot in enumerate(snapshots):
            lines.append(
                f"[{snapshot.timestamp:6.1f}s] "
                f"Tests: {snapshot.tests_passing}/{snapshot.tests_total}"
            )
            lines.append("-" * 50)
            lines.append(snapshot.code)
            lines.append("")

        return "\n".join(lines)
```

### Pattern Detection

Identify common patterns in how players solve challenges:

```python
from collections import Counter
from typing import Dict, List

@dataclass
class ApproachPattern:
    """Identified pattern in solving approach."""

    name: str
    description: str
    frequency: float  # How often this pattern appears (0.0 to 1.0)
    examples: List[str]  # Example recordings showing this pattern

class PatternDetector:
    """Detect patterns in solving approaches."""

    PATTERNS = {
        "test_first": {
            "name": "Test-First",
            "description": "Runs tests before writing code",
            "detect": lambda events: any(
                e.event.type == EventType.TEST_RUN
                for e in events[:5]  # In first 5 events
            )
        },
        "incremental": {
            "name": "Incremental",
            "description": "Tests after each small change",
            "detect": lambda events: (
                sum(1 for e in events if e.event.type == EventType.TEST_RUN)
                > len(events) / 50  # Test every ~50 events
            )
        },
        "big_bang": {
            "name": "Big Bang",
            "description": "Writes all code then tests once",
            "detect": lambda events: (
                sum(1 for e in events if e.event.type == EventType.TEST_RUN) < 3
            )
        },
        "hint_heavy": {
            "name": "Hint Heavy",
            "description": "Uses many hints",
            "detect": lambda events: (
                events[-1].game_state.hints_used > 3 if events else False
            )
        },
        "speedrunner": {
            "name": "Speedrunner",
            "description": "Very fast, few mistakes",
            "detect": lambda events: (
                len([e for e in events if e.event.type == EventType.TEST_FAIL]) < 2
            )
        }
    }

    def detect(self, recording: Recording) -> List[ApproachPattern]:
        """Detect patterns in recording."""
        detected = []

        for pattern_id, pattern_def in self.PATTERNS.items():
            if pattern_def["detect"](recording.events):
                detected.append(ApproachPattern(
                    name=pattern_def["name"],
                    description=pattern_def["description"],
                    frequency=1.0,  # Single recording
                    examples=[recording.player_id]
                ))

        return detected

    def analyze_corpus(
        self,
        recordings: List[Recording]
    ) -> Dict[str, ApproachPattern]:
        """Analyze patterns across many recordings."""
        pattern_counts = Counter()
        pattern_examples = {}

        for recording in recordings:
            patterns = self.detect(recording)
            for pattern in patterns:
                pattern_counts[pattern.name] += 1
                if pattern.name not in pattern_examples:
                    pattern_examples[pattern.name] = []
                pattern_examples[pattern.name].append(recording.player_id)

        # Calculate frequencies
        total = len(recordings)
        results = {}

        for pattern_id, pattern_def in self.PATTERNS.items():
            name = pattern_def["name"]
            if name in pattern_counts:
                results[name] = ApproachPattern(
                    name=name,
                    description=pattern_def["description"],
                    frequency=pattern_counts[name] / total,
                    examples=pattern_examples[name][:5]  # Top 5 examples
                )

        return results
```

## Learning from Recordings

### Insight Extraction

Extract learning insights from recordings:

```python
@dataclass
class LearningInsight:
    """Insight extracted from recording analysis."""

    type: str  # "success_factor", "common_mistake", "efficiency_tip"
    title: str
    description: str
    examples: List[str]  # Recording IDs demonstrating this

class InsightExtractor:
    """Extract learning insights from recordings."""

    def extract_success_factors(
        self,
        successful: List[Recording],
        failed: List[Recording]
    ) -> List[LearningInsight]:
        """
        Compare successful vs failed attempts to find success factors.
        """
        insights = []

        # Analyze hint usage
        avg_hints_success = sum(
            r.events[-1].game_state.hints_used for r in successful if r.events
        ) / len(successful) if successful else 0

        avg_hints_failed = sum(
            r.events[-1].game_state.hints_used for r in failed if r.events
        ) / len(failed) if failed else 0

        if avg_hints_success < avg_hints_failed:
            insights.append(LearningInsight(
                type="success_factor",
                title="Use Hints Wisely",
                description=(
                    f"Successful attempts used {avg_hints_success:.1f} hints on average, "
                    f"while failed attempts used {avg_hints_failed:.1f}. "
                    "Don't be afraid to ask for help early!"
                ),
                examples=[r.player_id for r in successful[:3]]
            ))

        return insights

    def extract_common_mistakes(
        self,
        recordings: List[Recording]
    ) -> List[LearningInsight]:
        """Identify common mistakes across recordings."""
        insights = []

        # Look for common test failures
        failure_patterns = Counter()

        for recording in recordings:
            for event in recording.events:
                if event.event.type == EventType.TEST_FAIL:
                    # Extract failure reason from event data
                    reason = event.event.data.get("reason", "unknown")
                    failure_patterns[reason] += 1

        # Report most common failures
        for reason, count in failure_patterns.most_common(3):
            insights.append(LearningInsight(
                type="common_mistake",
                title=f"Common Issue: {reason}",
                description=f"This mistake appeared in {count} recordings.",
                examples=[]
            ))

        return insights
```

## Usage Examples

### Basic Replay

```python
# Load and replay recording
recording = load_compressed("session.lmsp.gz")
replayer = Replayer(recording)

async def on_event(event: RecordedEvent):
    """Callback for each event."""
    print(f"[{event.timestamp:6.2f}s] {event.event.type.value}")
    if event.event.type == EventType.TEST_PASS:
        print(f"  Tests passing: {event.game_state.tests_passing}/{event.game_state.tests_total}")

await replayer.replay(speed=2.0, on_event=on_event)
```

### Interactive Replay

```python
# Interactive replay with controls
replayer = InteractiveReplayer(recording)

# Jump to checkpoint
await replayer.jump_to_checkpoint("before_implementation")

# Step through implementation
for _ in range(10):
    event = await replayer.step(forward=True)
    print(f"Code: {event.game_state.current_code}")

# Rewind to see mistake again
await replayer.rewind(steps=5)
```

### Speedrun Comparison

```python
# Compare two speedruns
recording_a = load_compressed("player_a.lmsp.gz")
recording_b = load_compressed("player_b.lmsp.gz")

comparator = RecordingComparator()
metrics = comparator.compare(recording_a, recording_b)

print(metrics.summary())
```

---

**Self-teaching note:**

This file demonstrates:
- Async/await patterns (Level 6+: Async programming)
- Dataclasses for structured data (Level 5: Classes)
- Callback functions (Level 4: Higher-order functions)
- Binary search algorithm (Level 4: Algorithms)
- Statistical analysis with Counter (Level 4+: Collections)

Prerequisites:
- Level 3: Functions and parameters
- Level 4: Lambda functions, comprehensions
- Level 5: Classes and methods
- Async/await basics
