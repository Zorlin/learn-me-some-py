# TAS Checkpoint System

## Overview

The LMSP checkpoint system enables named save points within recordings, allowing players to save, restore, and compare game states. This document covers checkpoint creation, state restoration, diff generation, and practical use cases.

## Named Checkpoints

### Checkpoint Creation

Checkpoints are named save points that capture the complete game state at a specific moment:

```python
from dataclasses import dataclass
from typing import Optional
import time

class Recorder:
    """Record every action for replay and analysis."""

    def __init__(self):
        self.events: list[RecordedEvent] = []
        self.start_time: float = 0
        self.checkpoints: dict[str, int] = {}  # name -> event_index
        self._recording: bool = False

    def start(self):
        """Start recording."""
        self.start_time = time.time()
        self._recording = True

    def record(self, event: GameEvent):
        """Record an event with timestamp."""
        if not self._recording:
            raise RuntimeError("Recorder not started")

        self.events.append(RecordedEvent(
            timestamp=time.time() - self.start_time,
            event=event,
            game_state=self.capture_state()
        ))

    def checkpoint(self, name: str):
        """
        Save a named checkpoint.

        Args:
            name: Unique checkpoint name

        Raises:
            ValueError: If checkpoint name already exists
        """
        if name in self.checkpoints:
            raise ValueError(f"Checkpoint '{name}' already exists")

        # Checkpoint points to the current event index
        self.checkpoints[name] = len(self.events) - 1

    def capture_state(self) -> GameState:
        """Capture current game state (to be implemented by game engine)."""
        # This would be implemented by the actual game engine
        # For now, return a placeholder
        raise NotImplementedError("Game engine must implement capture_state")

    def export(self) -> Recording:
        """Export recording for sharing/analysis."""
        return Recording(
            events=self.events,
            checkpoints=self.checkpoints,
            duration=time.time() - self.start_time
        )
```

### Checkpoint Naming Conventions

Use descriptive names that capture the moment's significance:

```python
class CheckpointNamer:
    """Helper for generating meaningful checkpoint names."""

    @staticmethod
    def auto_name(context: dict) -> str:
        """
        Generate automatic checkpoint name based on context.

        Args:
            context: Dictionary with context information

        Returns:
            Descriptive checkpoint name
        """
        if context.get("test_passed"):
            test_num = context.get("tests_passing", 0)
            return f"test_{test_num}_passed"

        if context.get("test_failed"):
            return f"test_failure_{context.get('failure_count', 0)}"

        if context.get("hint_used"):
            hint_level = context.get("hint_level", 1)
            return f"hint_{hint_level}_requested"

        if context.get("code_changed"):
            return f"edit_{context.get('edit_count', 0)}"

        return f"checkpoint_{context.get('index', 0)}"

    @staticmethod
    def user_checkpoint(description: str) -> str:
        """
        Generate checkpoint name from user description.

        Sanitizes user input to create valid checkpoint names.
        """
        # Remove special characters, replace spaces with underscores
        safe_name = "".join(
            c if c.isalnum() or c in "_-" else "_"
            for c in description
        )

        # Limit length
        safe_name = safe_name[:50]

        # Add timestamp to ensure uniqueness
        timestamp = int(time.time())
        return f"{safe_name}_{timestamp}"

# Usage examples
namer = CheckpointNamer()

# Auto-generated names
checkpoint_name = namer.auto_name({"test_passed": True, "tests_passing": 3})
# Returns: "test_3_passed"

checkpoint_name = namer.auto_name({"hint_used": True, "hint_level": 2})
# Returns: "hint_2_requested"

# User-provided names
checkpoint_name = namer.user_checkpoint("before bug fix")
# Returns: "before_bug_fix_1638360000"
```

## State Restoration

### Restoration Mechanism

Restore game state from a checkpoint:

```python
class StateRestorer:
    """Restore game state from checkpoints."""

    def __init__(self, recording: Recording):
        self.recording = recording

    def restore(self, checkpoint_name: str) -> GameState:
        """
        Restore game state from named checkpoint.

        Args:
            checkpoint_name: Name of checkpoint to restore

        Returns:
            Game state at checkpoint

        Raises:
            ValueError: If checkpoint doesn't exist
        """
        if checkpoint_name not in self.recording.checkpoints:
            available = ", ".join(self.recording.checkpoints.keys())
            raise ValueError(
                f"Checkpoint '{checkpoint_name}' not found. "
                f"Available: {available}"
            )

        event_idx = self.recording.checkpoints[checkpoint_name]
        return self.recording.events[event_idx].game_state

    def restore_to_index(self, event_index: int) -> GameState:
        """
        Restore state at specific event index.

        Args:
            event_index: Index into recording.events

        Returns:
            Game state at that index
        """
        if event_index < 0 or event_index >= len(self.recording.events):
            raise IndexError(
                f"Event index {event_index} out of range "
                f"(0 to {len(self.recording.events) - 1})"
            )

        return self.recording.events[event_index].game_state

    def list_checkpoints(self) -> list[tuple[str, float]]:
        """
        List all checkpoints with their timestamps.

        Returns:
            List of (name, timestamp) tuples
        """
        checkpoints = []
        for name, idx in self.recording.checkpoints.items():
            timestamp = self.recording.events[idx].timestamp
            checkpoints.append((name, timestamp))

        # Sort by timestamp
        checkpoints.sort(key=lambda x: x[1])
        return checkpoints
```

### Applying Restored State

Apply a restored state to the game:

```python
class GameEngine:
    """Game engine with state restoration support."""

    def __init__(self):
        self.current_state: Optional[GameState] = None
        self.restorer: Optional[StateRestorer] = None

    def load_recording(self, recording: Recording):
        """Load recording for potential restoration."""
        self.restorer = StateRestorer(recording)

    def rewind_to(self, checkpoint_name: str):
        """
        Rewind game to checkpoint.

        Args:
            checkpoint_name: Name of checkpoint to restore
        """
        if not self.restorer:
            raise RuntimeError("No recording loaded")

        # Restore state
        restored_state = self.restorer.restore(checkpoint_name)

        # Apply to game
        self.apply_state(restored_state)

    def apply_state(self, state: GameState):
        """
        Apply game state to engine.

        This resets all game variables to match the state.
        """
        self.current_state = state

        # Apply code
        self.editor.set_code(state.current_code)
        self.editor.set_cursor(state.cursor_position)

        # Apply challenge state
        self.challenge_id = state.challenge_id
        self.tests_passing = state.tests_passing
        self.tests_total = state.tests_total
        self.hints_used = state.hints_used

        # Apply player state
        self.mastery_levels = state.mastery_levels.copy()
        self.current_emotion = state.current_emotion

        # Apply session state
        self.session_duration = state.session_duration
        self.challenges_completed = state.challenges_completed.copy()
        self.concepts_mastered = state.concepts_mastered.copy()
```

## Diff Generation

### Checkpoint Comparison

Generate diffs between two checkpoints:

```python
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class StateDiff:
    """Difference between two game states."""

    # Code changes
    code_added: List[str]  # Lines added
    code_removed: List[str]  # Lines removed
    code_changed: List[Tuple[str, str]]  # (old_line, new_line) pairs

    # Test progress
    tests_changed: int  # Change in passing tests

    # Other changes
    hints_used: int  # Additional hints used
    time_elapsed: float  # Time between states

    # Mastery changes
    concepts_learned: List[str]  # New concepts mastered
    mastery_increased: dict[str, Tuple[int, int]]  # concept -> (old, new) level

class CheckpointDiffer:
    """Generate diffs between checkpoints."""

    def diff(
        self,
        recording: Recording,
        checkpoint_a: str,
        checkpoint_b: str
    ) -> StateDiff:
        """
        Generate diff between two checkpoints.

        Args:
            recording: Recording containing checkpoints
            checkpoint_a: Earlier checkpoint
            checkpoint_b: Later checkpoint

        Returns:
            StateDiff showing changes
        """
        restorer = StateRestorer(recording)

        state_a = restorer.restore(checkpoint_a)
        state_b = restorer.restore(checkpoint_b)

        # Calculate code diff
        code_diff = self._diff_code(state_a.current_code, state_b.current_code)

        # Calculate test progress
        tests_changed = state_b.tests_passing - state_a.tests_passing

        # Calculate time elapsed
        idx_a = recording.checkpoints[checkpoint_a]
        idx_b = recording.checkpoints[checkpoint_b]
        time_elapsed = (
            recording.events[idx_b].timestamp -
            recording.events[idx_a].timestamp
        )

        # Calculate hint usage
        hints_used = state_b.hints_used - state_a.hints_used

        # Calculate mastery changes
        concepts_learned = [
            c for c in state_b.concepts_mastered
            if c not in state_a.concepts_mastered
        ]

        mastery_increased = {}
        for concept, level_b in state_b.mastery_levels.items():
            level_a = state_a.mastery_levels.get(concept, 0)
            if level_b > level_a:
                mastery_increased[concept] = (level_a, level_b)

        return StateDiff(
            code_added=code_diff["added"],
            code_removed=code_diff["removed"],
            code_changed=code_diff["changed"],
            tests_changed=tests_changed,
            hints_used=hints_used,
            time_elapsed=time_elapsed,
            concepts_learned=concepts_learned,
            mastery_increased=mastery_increased
        )

    def _diff_code(self, code_a: str, code_b: str) -> dict:
        """
        Generate line-by-line code diff.

        Returns:
            Dictionary with "added", "removed", "changed" lists
        """
        import difflib

        lines_a = code_a.split('\n')
        lines_b = code_b.split('\n')

        diff = difflib.unified_diff(lines_a, lines_b, lineterm='')

        added = []
        removed = []
        changed = []

        for line in diff:
            if line.startswith('+') and not line.startswith('+++'):
                added.append(line[1:])
            elif line.startswith('-') and not line.startswith('---'):
                removed.append(line[1:])

        return {
            "added": added,
            "removed": removed,
            "changed": changed  # Could be calculated from added/removed
        }

    def format_diff(self, diff: StateDiff) -> str:
        """Format diff as human-readable text."""
        lines = [
            "=== CHECKPOINT DIFF ===",
            f"Time elapsed: {diff.time_elapsed:.1f}s",
            ""
        ]

        # Code changes
        if diff.code_added or diff.code_removed:
            lines.append("Code changes:")
            for line in diff.code_removed:
                lines.append(f"  - {line}")
            for line in diff.code_added:
                lines.append(f"  + {line}")
            lines.append("")

        # Test progress
        if diff.tests_changed != 0:
            sign = "+" if diff.tests_changed > 0 else ""
            lines.append(f"Tests: {sign}{diff.tests_changed}")
            lines.append("")

        # Hints
        if diff.hints_used > 0:
            lines.append(f"Hints used: {diff.hints_used}")
            lines.append("")

        # Mastery
        if diff.concepts_learned:
            lines.append("Concepts learned:")
            for concept in diff.concepts_learned:
                lines.append(f"  - {concept}")
            lines.append("")

        if diff.mastery_increased:
            lines.append("Mastery increased:")
            for concept, (old, new) in diff.mastery_increased.items():
                lines.append(f"  - {concept}: {old} -> {new}")
            lines.append("")

        return "\n".join(lines)
```

### ApproachDiff Structure

Compare different approaches to the same problem:

```python
@dataclass
class ApproachDiff:
    """Comparison of different solving approaches."""

    # Timing
    time_difference: float  # Seconds

    # Code comparison
    code_similarity: float  # 0.0 to 1.0
    code_length_diff: int  # Lines

    # Approach characteristics
    approach_a_pattern: str  # E.g., "incremental"
    approach_b_pattern: str  # E.g., "big_bang"

    # Efficiency
    events_diff: int  # Total events
    keystrokes_diff: int  # Keystroke count

    # Learning insights
    recommended_approach: str  # "a" or "b"
    reasoning: str  # Why one is better

class ApproachComparator:
    """Compare different approaches to solving."""

    def compare_approaches(
        self,
        recording_a: Recording,
        recording_b: Recording
    ) -> ApproachDiff:
        """
        Compare two different approaches to same challenge.

        Args:
            recording_a: First approach
            recording_b: Second approach

        Returns:
            Detailed comparison
        """
        # Validate same challenge
        if recording_a.challenge_id != recording_b.challenge_id:
            raise ValueError("Recordings must be for same challenge")

        # Calculate timing
        time_diff = recording_a.duration - recording_b.duration

        # Compare code
        similarity = self._code_similarity(
            recording_a.final_code,
            recording_b.final_code
        )

        length_diff = (
            len(recording_a.final_code.split('\n')) -
            len(recording_b.final_code.split('\n'))
        )

        # Detect patterns
        pattern_a = self._detect_pattern(recording_a)
        pattern_b = self._detect_pattern(recording_b)

        # Count events
        events_diff = len(recording_a.events) - len(recording_b.events)

        keystrokes_a = sum(
            1 for e in recording_a.events
            if e.event.type == EventType.KEYSTROKE
        )
        keystrokes_b = sum(
            1 for e in recording_b.events
            if e.event.type == EventType.KEYSTROKE
        )
        keystrokes_diff = keystrokes_a - keystrokes_b

        # Determine recommendation
        recommended, reasoning = self._recommend_approach(
            recording_a, recording_b, time_diff
        )

        return ApproachDiff(
            time_difference=time_diff,
            code_similarity=similarity,
            code_length_diff=length_diff,
            approach_a_pattern=pattern_a,
            approach_b_pattern=pattern_b,
            events_diff=events_diff,
            keystrokes_diff=keystrokes_diff,
            recommended_approach=recommended,
            reasoning=reasoning
        )

    def _code_similarity(self, code_a: str, code_b: str) -> float:
        """Calculate code similarity (0.0 to 1.0)."""
        import difflib
        return difflib.SequenceMatcher(None, code_a, code_b).ratio()

    def _detect_pattern(self, recording: Recording) -> str:
        """Detect solving pattern."""
        test_count = sum(
            1 for e in recording.events
            if e.event.type == EventType.TEST_RUN
        )

        if test_count > len(recording.events) / 50:
            return "incremental"
        elif test_count < 3:
            return "big_bang"
        else:
            return "balanced"

    def _recommend_approach(
        self,
        recording_a: Recording,
        recording_b: Recording,
        time_diff: float
    ) -> Tuple[str, str]:
        """Determine which approach to recommend."""
        # Prefer successful approach
        if recording_a.success and not recording_b.success:
            return ("a", "Approach A succeeded while B failed")
        if recording_b.success and not recording_a.success:
            return ("b", "Approach B succeeded while A failed")

        # If both succeeded or both failed, prefer faster
        if abs(time_diff) > 5.0:  # Significant time difference
            if time_diff < 0:
                return ("a", f"Approach A was {-time_diff:.1f}s faster")
            else:
                return ("b", f"Approach B was {time_diff:.1f}s faster")

        # Similar performance
        return ("tie", "Both approaches performed similarly")
```

## Semantic Diff for Code

### AST-Based Comparison

Compare code semantically, not just textually:

```python
import ast
from typing import List, Dict

class SemanticDiffer:
    """Compare code at semantic/AST level."""

    def semantic_diff(self, code_a: str, code_b: str) -> Dict[str, List[str]]:
        """
        Generate semantic diff between two code snippets.

        Returns:
            Dictionary with semantic differences
        """
        try:
            tree_a = ast.parse(code_a)
            tree_b = ast.parse(code_b)
        except SyntaxError:
            # Fallback to textual diff if parsing fails
            return {"error": ["Code contains syntax errors"]}

        # Extract semantic elements
        elements_a = self._extract_elements(tree_a)
        elements_b = self._extract_elements(tree_b)

        # Compare
        diff = {
            "functions_added": list(elements_b["functions"] - elements_a["functions"]),
            "functions_removed": list(elements_a["functions"] - elements_b["functions"]),
            "variables_added": list(elements_b["variables"] - elements_a["variables"]),
            "variables_removed": list(elements_a["variables"] - elements_b["variables"]),
            "calls_added": list(elements_b["calls"] - elements_a["calls"]),
            "calls_removed": list(elements_a["calls"] - elements_b["calls"])
        }

        return diff

    def _extract_elements(self, tree: ast.AST) -> Dict[str, set]:
        """Extract semantic elements from AST."""
        elements = {
            "functions": set(),
            "variables": set(),
            "calls": set()
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                elements["functions"].add(node.name)
            elif isinstance(node, ast.Name):
                elements["variables"].add(node.id)
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    elements["calls"].add(node.func.id)

        return elements
```

## Use Cases and Examples

### Use Case 1: Before/After Bug Fix

```python
# During gameplay
recorder = Recorder()
recorder.start()

# ... player writes buggy code ...
recorder.checkpoint("before_bug_fix")

# ... player debugs and fixes ...
recorder.checkpoint("after_bug_fix")

# Later analysis
recording = recorder.export()
differ = CheckpointDiffer()
diff = differ.diff(recording, "before_bug_fix", "after_bug_fix")

print(differ.format_diff(diff))
# Shows exactly what changed to fix the bug
```

### Use Case 2: Speedrun Comparison

```python
# Load two speedruns
recording_1 = load_compressed("speedrun_1.lmsp.gz")
recording_2 = load_compressed("speedrun_2.lmsp.gz")

# Compare approaches
comparator = ApproachComparator()
approach_diff = comparator.compare_approaches(recording_1, recording_2)

print(f"Time difference: {approach_diff.time_difference:.2f}s")
print(f"Approach 1: {approach_diff.approach_a_pattern}")
print(f"Approach 2: {approach_diff.approach_b_pattern}")
print(f"Recommendation: {approach_diff.recommended_approach}")
print(f"Reasoning: {approach_diff.reasoning}")
```

### Use Case 3: Learning from AI

```python
# AI completes challenge with checkpoints
ai_recording = load_compressed("ai_solution.lmsp.gz")

# Student rewinds to key moments
restorer = StateRestorer(ai_recording)

# List all checkpoints
checkpoints = restorer.list_checkpoints()
print("Key moments in AI's solution:")
for name, timestamp in checkpoints:
    print(f"  [{timestamp:6.1f}s] {name}")

# Jump to interesting moment
state = restorer.restore("before_list_comprehension")
print(f"AI's code at this point:\n{state.current_code}")

# See what changed
differ = CheckpointDiffer()
diff = differ.diff(
    ai_recording,
    "before_list_comprehension",
    "after_list_comprehension"
)
print(differ.format_diff(diff))
```

### Use Case 4: Teaching Mode

```python
# Teacher creates annotated recording
recorder = Recorder()
recorder.start()

# Teacher demonstrates concept step by step
recorder.checkpoint("1_setup_container")
# ... writes container = [] ...

recorder.checkpoint("2_iterate_queries")
# ... writes for loop ...

recorder.checkpoint("3_match_commands")
# ... writes match statement ...

recorder.checkpoint("4_handle_add")
# ... implements add command ...

recorder.checkpoint("5_handle_exists")
# ... implements exists command ...

recorder.checkpoint("6_complete_solution")
# ... final code ...

# Export for students
teaching_recording = recorder.export()
save_compressed(teaching_recording, "teaching_session.lmsp.gz")

# Students can:
# - Replay at their own pace
# - Jump between checkpoints
# - Compare their approach to teacher's
```

## Best Practices

1. **Checkpoint Frequently at Key Moments**:
   - Before implementing new logic
   - After each test passes
   - Before and after bug fixes
   - At emotional checkpoints (frustration, breakthrough)

2. **Use Descriptive Names**:
   - "before_list_comprehension" not "checkpoint_1"
   - "first_test_passing" not "test_1"
   - "aha_moment" for breakthroughs

3. **Diff Before Committing**:
   - Review what changed between checkpoints
   - Ensure understanding of each modification
   - Learn from differences

4. **Compare Approaches**:
   - Your first attempt vs. successful attempt
   - Your solution vs. AI solution
   - Slow approach vs. fast approach

5. **Restore for Learning**:
   - Go back to moments of confusion
   - See what you knew at different points
   - Track your learning progression

---

**Self-teaching note:**

This file demonstrates:
- Advanced error handling and validation (Professional Python)
- Set operations for semantic comparison (Level 2+: Collections)
- AST manipulation for code analysis (Level 6+: Metaprogramming)
- Dataclasses with complex relationships (Level 5: Classes)
- Difflib for text comparison (Standard library)

Prerequisites:
- Level 2: Collections (sets, lists, dicts)
- Level 3: Functions and exception handling
- Level 5: Classes, dataclasses
- AST module familiarity
- Understanding of diffs and version control concepts
