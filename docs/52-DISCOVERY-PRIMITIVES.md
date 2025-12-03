# Discovery Primitives - Progressive Introspection Tools

## Overview

Discovery primitives are introspection commands that unlock progressively as the player advances through LMSP. They provide increasingly powerful tools for understanding, analyzing, and debugging code.

**Philosophy:** Don't overwhelm beginners with complex tools. Unlock capabilities as they gain competence.

- **Level 0:** Basic help and screenshots
- **Level 1:** Checkpoints and restore
- **Level 2:** Time travel (rewind/step/diff)
- **Level 3:** Advanced capture (video/mosaic/wireframe)
- **Level 4:** Deep analysis (trace/profile/explain)
- **Level 5:** Meta tools (discovery/teaching/benchmarking)

Each primitive is both:
1. **A useful tool** for learning
2. **A lesson** in the concept it demonstrates

---

## Complete Primitive Reference

### Level 0: Always Available

These are available from the first moment:

#### `/help`

Show available commands based on current unlock level.

```python
@command("/help", unlock_level=0)
def cmd_help(game) -> None:
    """Show available commands."""
    player = game.player
    available = get_available_primitives(player)

    print("Available Commands:")
    print("=" * 60)

    for level in range(player.primitive_level + 1):
        level_primitives = [
            (name, info) for name, info in PRIMITIVES.items()
            if info.unlock_level == level
        ]

        if level_primitives:
            print(f"\n[Level {level}]")
            for name, info in level_primitives:
                print(f"  {name:30} {info.description}")

    next_level = player.primitive_level + 1
    if next_level <= 5:
        print(f"\n[Level {next_level} - Locked]")
        locked = [
            (name, info) for name, info in PRIMITIVES.items()
            if info.unlock_level == next_level
        ]
        for name, info in locked[:3]:  # Show first 3
            print(f"  {name:30} 🔒 {info.unlock_condition}")
```

**Example Output:**
```
Available Commands:
============================================================

[Level 0]
  /help                          Show available commands
  /screenshot                    Capture current state

[Level 1 - Locked]
  /checkpoint <name>             🔒 Complete first challenge
  /restore <name>                🔒 Complete first challenge
```

#### `/screenshot`

Capture current state with wireframe metadata.

```python
@command("/screenshot", unlock_level=0)
def cmd_screenshot(game) -> ScreenshotBundle:
    """Capture current state."""
    from lmsp.introspection.screenshot import Screenshot
    from datetime import datetime

    screenshot = Screenshot(game)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = Path(f"~/.lmsp/screenshots/{game.player.id}/{timestamp}").expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)

    bundle = screenshot.capture_and_save(path)

    print(f"📸 Screenshot saved: {path}.png")
    print(f"📋 Wireframe saved: {path}.json")
    print(f"\nCurrent State:")
    print(f"  Challenge: {bundle.wireframe.current_challenge}")
    print(f"  Tests: {bundle.wireframe.tests_passing}/{bundle.wireframe.tests_total}")
    print(f"  Session: {round(bundle.wireframe.session_duration / 60, 1)} minutes")

    if bundle.wireframe.current_emotion:
        emotion = bundle.wireframe.current_emotion
        print(f"  Emotion: {emotion.get('dimension')} = {emotion.get('value'):.2f}")

    return bundle
```

**Example Output:**
```
📸 Screenshot saved: /home/wings/.lmsp/screenshots/wings/20250612_143022.png
📋 Wireframe saved: /home/wings/.lmsp/screenshots/wings/20250612_143022.json

Current State:
  Challenge: container_add_exists
  Tests: 2/5
  Session: 8.3 minutes
  Emotion: enjoyment = 0.75
```

---

### Level 1: After First Challenge

Unlocked after completing the first challenge:

#### `/checkpoint <name>`

Save current state with a named checkpoint.

```python
@command("/checkpoint <name>", unlock_level=1)
def cmd_checkpoint(game, name: str) -> Checkpoint:
    """Save current state."""
    from lmsp.introspection.checkpoint import Checkpoint

    checkpoint = Checkpoint.create(
        name=name,
        code=game.current_code,
        cursor=game.cursor,
        tests=game.test_results,
        metadata={
            "challenge": game.current_challenge.id,
            "timestamp": time.time(),
            "player": game.player.id,
        }
    )

    game.checkpoints[name] = checkpoint

    print(f"✓ Checkpoint '{name}' saved")
    print(f"  Lines of code: {len(game.current_code.splitlines())}")
    print(f"  Tests passing: {checkpoint.tests_passing}/{checkpoint.tests_total}")

    return checkpoint
```

**Usage:**
```python
# Save before trying risky change
/checkpoint before_refactor

# Later, if things go wrong:
/restore before_refactor
```

#### `/restore <name>`

Restore from a named checkpoint.

```python
@command("/restore <name>", unlock_level=1)
def cmd_restore(game, name: str) -> None:
    """Restore saved state."""
    if name not in game.checkpoints:
        print(f"❌ Checkpoint '{name}' not found")
        print(f"\nAvailable checkpoints:")
        for cp_name in game.checkpoints.keys():
            print(f"  - {cp_name}")
        return

    checkpoint = game.checkpoints[name]

    # Restore state
    game.current_code = checkpoint.code
    game.cursor = checkpoint.cursor
    game.test_results = checkpoint.tests

    print(f"✓ Restored to checkpoint '{name}'")
    print(f"  Time: {checkpoint.metadata.get('timestamp')}")
    print(f"  Tests: {checkpoint.tests_passing}/{checkpoint.tests_total}")

    # Re-render
    game.render()
```

**Example Output:**
```
✓ Restored to checkpoint 'before_refactor'
  Time: 1686585022.4
  Tests: 3/5
```

---

### Level 2: After 5 Challenges

Unlocked after completing 5 challenges (time travel features):

#### `/rewind <n>`

Go back n steps in history.

```python
@command("/rewind <n>", unlock_level=2)
def cmd_rewind(game, n: int = 1) -> None:
    """Go back n steps."""
    from lmsp.introspection.tas import Recorder

    if not hasattr(game, 'recorder') or not game.recorder:
        print("❌ No recording active. Start a challenge to enable recording.")
        return

    recorder: Recorder = game.recorder

    if n > len(recorder.events):
        print(f"❌ Can't rewind {n} steps (only {len(recorder.events)} recorded)")
        return

    # Rewind
    target_idx = max(0, recorder.current_idx - n)
    event = recorder.events[target_idx]

    # Restore state
    game.restore_state(event.game_state)
    recorder.current_idx = target_idx

    print(f"⏪ Rewound {n} step(s)")
    print(f"  Position: {target_idx}/{len(recorder.events)}")
    print(f"  Timestamp: {event.timestamp:.1f}s")

    game.render()
```

**Usage:**
```python
# Oops, that broke everything
/rewind 5

# Now I'm back before the mistake
```

#### `/step`

Single-step forward through history.

```python
@command("/step", unlock_level=2)
def cmd_step(game) -> None:
    """Single-step forward."""
    from lmsp.introspection.tas import Recorder

    if not hasattr(game, 'recorder') or not game.recorder:
        print("❌ No recording active")
        return

    recorder: Recorder = game.recorder

    if recorder.current_idx >= len(recorder.events) - 1:
        print("❌ Already at latest event")
        return

    # Step forward
    recorder.current_idx += 1
    event = recorder.events[recorder.current_idx]

    # Apply event
    game.restore_state(event.game_state)

    print(f"⏩ Stepped forward")
    print(f"  Position: {recorder.current_idx}/{len(recorder.events)}")
    print(f"  Event: {event.event.type}")

    game.render()
```

#### `/diff <a> <b>`

Compare two checkpoints.

```python
@command("/diff <a> <b>", unlock_level=2)
def cmd_diff(game, a: str, b: str) -> None:
    """Compare checkpoints."""
    from lmsp.introspection.checkpoint import Checkpoint
    import difflib

    if a not in game.checkpoints or b not in game.checkpoints:
        print("❌ One or both checkpoints not found")
        return

    cp_a = game.checkpoints[a]
    cp_b = game.checkpoints[b]

    # Code diff
    diff = difflib.unified_diff(
        cp_a.code.splitlines(),
        cp_b.code.splitlines(),
        fromfile=a,
        tofile=b,
        lineterm='',
    )

    print(f"Diff: {a} → {b}")
    print("=" * 60)

    for line in diff:
        if line.startswith('+'):
            print(f"\033[92m{line}\033[0m")  # Green
        elif line.startswith('-'):
            print(f"\033[91m{line}\033[0m")  # Red
        elif line.startswith('@@'):
            print(f"\033[94m{line}\033[0m")  # Blue
        else:
            print(line)

    # Test diff
    print(f"\nTests: {cp_a.tests_passing}/{cp_a.tests_total} → {cp_b.tests_passing}/{cp_b.tests_total}")

    if cp_b.tests_passing > cp_a.tests_passing:
        print("✓ Progress: More tests passing")
    elif cp_b.tests_passing < cp_a.tests_passing:
        print("⚠ Regression: Fewer tests passing")
```

**Example Output:**
```
Diff: before_refactor → after_refactor
============================================================
@@ -3,7 +3,5 @@
 def solution(queries):
-    container = []
-    results = []
-    for cmd, val in queries:
-        if cmd == "add":
-            container.append(val)
+    return [
+        val in container if cmd == "exists" else container.append(val)
+        for cmd, val in queries
+    ]

Tests: 3/5 → 5/5
✓ Progress: More tests passing
```

---

### Level 3: After Completing a Level

Unlocked after completing an entire level (all challenges in a level):

#### `/video <duration>`

Record strategic video as mosaic.

```python
@command("/video <duration>", unlock_level=3)
async def cmd_video(game, duration: float = 60.0) -> Mosaic:
    """Record strategic video."""
    from lmsp.introspection.mosaic import MosaicRecorder, MosaicConfig

    config = MosaicConfig(
        duration_seconds=duration,
        fps=10,
        grid=(4, 4),
    )

    recorder = MosaicRecorder(game.capture_frame, config)

    print(f"🎥 Recording {duration}s mosaic...")
    print("(Continue playing normally)")

    mosaic = await recorder.record()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = Path(f"~/.lmsp/mosaics/{game.player.id}/{timestamp}").expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)

    mosaic.save(path)

    print(f"✓ Mosaic saved: {path}.webp")
    print(f"  Frames: {mosaic.selected_count} of {mosaic.total_frames}")
    print(f"  Duration: {mosaic.duration:.1f}s")
    print(f"  Grid: {mosaic.config.grid[0]}x{mosaic.config.grid[1]}")

    return mosaic
```

#### `/mosaic <grid>`

Generate frame mosaic with custom grid.

```python
@command("/mosaic <grid>", unlock_level=3)
async def cmd_mosaic(game, grid: str = "4x4") -> Mosaic:
    """Generate frame mosaic."""
    from lmsp.introspection.mosaic import MosaicRecorder, MosaicConfig

    try:
        rows, cols = map(int, grid.split("x"))
    except ValueError:
        print("❌ Invalid grid format. Use format like '4x4' or '6x6'")
        return

    config = MosaicConfig(
        duration_seconds=60.0,
        fps=10,
        grid=(rows, cols),
    )

    # Same as /video but with custom grid
    # ... (implementation same as cmd_video)
```

**Usage:**
```python
# Record 2 minutes with 6x6 grid
/mosaic 6x6

# Quick 30s recording
/video 30
```

#### `/wireframe`

Dump full context as JSON.

```python
@command("/wireframe", unlock_level=3)
def cmd_wireframe(game) -> dict:
    """Dump full context."""
    from lmsp.introspection.screenshot import Screenshot
    import json

    screenshot = Screenshot(game)
    bundle = screenshot.capture()

    wireframe_json = bundle.to_json()

    print("Current Wireframe:")
    print("=" * 60)
    print(json.dumps(wireframe_json, indent=2))

    # Also save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = Path(f"~/.lmsp/wireframes/{game.player.id}/{timestamp}.json").expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w") as f:
        json.dump(wireframe_json, f, indent=2)

    print(f"\n✓ Saved to: {path}")

    return wireframe_json
```

**Example Output:**
```json
{
  "timestamp": 1686585123.4,
  "wireframe": {
    "code": "def solution(queries):\n    ...",
    "ast": "Module(...)",
    "cursor": [5, 12],
    "challenge": "container_add_exists",
    "tests": "3/5",
    "player": "wings",
    "mastery": {
      "lists": 3,
      "in_operator": 2
    },
    ...
  }
}
```

---

### Level 4: After Teaching Mode

Unlocked after successfully teaching in teaching mode:

#### `/trace <function>`

Follow execution path of a function.

```python
@command("/trace <function>", unlock_level=4)
def cmd_trace(game, function: str = "solution") -> None:
    """Trace function execution."""
    import sys
    from collections import defaultdict

    # Set up tracer
    trace_data = defaultdict(int)

    def trace_calls(frame, event, arg):
        if event == 'line':
            # Track line execution
            filename = frame.f_code.co_filename
            lineno = frame.f_lineno

            # Only trace our code
            if '<challenge>' in filename:
                trace_data[lineno] += 1

        return trace_calls

    # Run with tracing
    print(f"🔍 Tracing function: {function}")

    sys.settrace(trace_calls)
    try:
        game.run_tests()
    finally:
        sys.settrace(None)

    # Display trace
    code_lines = game.current_code.splitlines()

    print("\nExecution Trace:")
    print("=" * 60)

    for lineno, count in sorted(trace_data.items()):
        line = code_lines[lineno - 1] if lineno <= len(code_lines) else ""
        print(f"{lineno:4} ({count:3}x)  {line}")
```

**Example Output:**
```
🔍 Tracing function: solution

Execution Trace:
============================================================
   1 (  1x)  def solution(queries):
   2 (  1x)      container = []
   3 (  1x)      results = []
   4 ( 10x)      for cmd, val in queries:
   5 ( 10x)          if cmd == "add":
   6 (  6x)              container.append(val)
   7 (  4x)          elif cmd == "exists":
   8 (  4x)              results.append(val in container)
```

#### `/profile`

Performance analysis.

```python
@command("/profile", unlock_level=4)
def cmd_profile(game) -> None:
    """Profile code performance."""
    import cProfile
    import pstats
    import io

    print("📊 Profiling code...")

    profiler = cProfile.Profile()
    profiler.enable()

    # Run tests
    game.run_tests()

    profiler.disable()

    # Analyze results
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s)
    ps.strip_dirs()
    ps.sort_stats('cumulative')
    ps.print_stats(10)  # Top 10

    print(s.getvalue())
```

#### `/explain`

AI explanation of current state.

```python
@command("/explain", unlock_level=4)
async def cmd_explain(game) -> str:
    """Get AI explanation of current state."""
    from lmsp.introspection.screenshot import Screenshot, ClaudeOptimizedWireframe

    # Capture current state
    screenshot = Screenshot(game)
    bundle = screenshot.capture()

    # Generate prompt
    prompt = ClaudeOptimizedWireframe.generate_prompt(
        bundle,
        question="Explain what's happening in this code. What's working? What's not? What should the learner try next?"
    )

    print("🤔 Asking Claude for explanation...")

    # Call Claude API (this would be the actual API call)
    # For now, placeholder
    explanation = await game.claude_api.explain(prompt, bundle.image)

    print("\n" + "=" * 60)
    print("Claude's Explanation:")
    print("=" * 60)
    print(explanation)

    return explanation
```

---

### Level 5: After Contributing

Unlocked after contributing new content or teaching successfully:

#### `/discover-new`

List recently unlocked tools.

```python
@command("/discover-new", unlock_level=5)
def cmd_discover_new(game) -> list[str]:
    """List recently unlocked primitives."""
    player = game.player

    # Get primitives unlocked in last level
    current_level = player.primitive_level
    newly_unlocked = [
        (name, info) for name, info in PRIMITIVES.items()
        if info.unlock_level == current_level
    ]

    print(f"🎉 Newly Unlocked (Level {current_level}):")
    print("=" * 60)

    for name, info in newly_unlocked:
        print(f"\n{name}")
        print(f"  {info.description}")
        print(f"  Try: {info.example}")

    return [name for name, _ in newly_unlocked]
```

#### `/teach <concept>`

Enter teaching mode for a concept.

```python
@command("/teach <concept>", unlock_level=5)
async def cmd_teach(game, concept: str) -> None:
    """Enter teaching mode."""
    from lmsp.multiplayer.session import TeachingSession

    # Check mastery
    if game.player.mastery_levels.get(concept, 0) < 4:
        print(f"❌ You must TRANSCEND '{concept}' before teaching it")
        print(f"   Current mastery: {game.player.mastery_levels.get(concept, 0)}/4")
        return

    print(f"👨‍🏫 Starting teaching session: {concept}")

    # Create AI students
    students = [
        game.create_ai_player(f"Student_{i}", skill_level=0.3)
        for i in range(3)
    ]

    session = TeachingSession(
        teacher=game.player,
        students=students,
        concept=concept,
    )

    await session.start()
```

#### `/benchmark`

Compare approach to others.

```python
@command("/benchmark", unlock_level=5)
async def cmd_benchmark(game) -> dict:
    """Compare your solution to others."""
    from lmsp.multiplayer.session import SwarmSession

    challenge = game.current_challenge

    print(f"🏁 Benchmarking: {challenge.name}")
    print("   Spawning AI players with different strategies...")

    # Create AI players with different strategies
    ai_players = [
        game.create_ai_player("Brute Force", strategy="brute_force"),
        game.create_ai_player("Elegant", strategy="elegant"),
        game.create_ai_player("Fast", strategy="fast"),
        game.create_ai_player("Readable", strategy="readable"),
    ]

    # Run swarm
    session = SwarmSession(
        players=ai_players,
        challenge=challenge,
        goal="Find best solution",
    )

    results = await session.run(max_duration=60)

    # Display comparison
    print("\nResults:")
    print("=" * 60)

    for result in results:
        print(f"\n{result.player.name} ({result.strategy}):")
        print(f"  Lines: {result.lines}")
        print(f"  Time: {result.time}ms")
        print(f"  Tests: {result.tests_passing}/{result.tests_total}")
        print(f"  Rating: {result.rating}/10")

    # Compare to player's solution
    player_result = game.benchmark_current_solution()

    print(f"\nYour Solution:")
    print(f"  Lines: {player_result.lines}")
    print(f"  Time: {player_result.time}ms")
    print(f"  Tests: {player_result.tests_passing}/{player_result.tests_total}")

    return results
```

---

## Unlock Conditions

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class PrimitiveInfo:
    """Information about a discovery primitive."""

    unlock_level: int
    description: str
    unlock_condition: str
    example: str


PRIMITIVES = {
    # Level 0 - Always available
    "/help": PrimitiveInfo(
        unlock_level=0,
        description="Show available commands",
        unlock_condition="Always available",
        example="/help",
    ),
    "/screenshot": PrimitiveInfo(
        unlock_level=0,
        description="Capture current state",
        unlock_condition="Always available",
        example="/screenshot",
    ),

    # Level 1 - After first challenge
    "/checkpoint <name>": PrimitiveInfo(
        unlock_level=1,
        description="Save current state",
        unlock_condition="Complete first challenge",
        example="/checkpoint before_refactor",
    ),
    "/restore <name>": PrimitiveInfo(
        unlock_level=1,
        description="Restore saved state",
        unlock_condition="Complete first challenge",
        example="/restore before_refactor",
    ),

    # Level 2 - After 5 challenges
    "/rewind <n>": PrimitiveInfo(
        unlock_level=2,
        description="Go back n steps",
        unlock_condition="Complete 5 challenges",
        example="/rewind 3",
    ),
    "/step": PrimitiveInfo(
        unlock_level=2,
        description="Single-step forward",
        unlock_condition="Complete 5 challenges",
        example="/step",
    ),
    "/diff <a> <b>": PrimitiveInfo(
        unlock_level=2,
        description="Compare checkpoints",
        unlock_condition="Complete 5 challenges",
        example="/diff start end",
    ),

    # Level 3 - After completing a level
    "/video <duration>": PrimitiveInfo(
        unlock_level=3,
        description="Record strategic video",
        unlock_condition="Complete entire level",
        example="/video 60",
    ),
    "/mosaic <grid>": PrimitiveInfo(
        unlock_level=3,
        description="Generate frame mosaic",
        unlock_condition="Complete entire level",
        example="/mosaic 6x6",
    ),
    "/wireframe": PrimitiveInfo(
        unlock_level=3,
        description="Dump full context",
        unlock_condition="Complete entire level",
        example="/wireframe",
    ),

    # Level 4 - After teaching mode
    "/trace <function>": PrimitiveInfo(
        unlock_level=4,
        description="Follow execution path",
        unlock_condition="Successfully teach concept",
        example="/trace solution",
    ),
    "/profile": PrimitiveInfo(
        unlock_level=4,
        description="Performance analysis",
        unlock_condition="Successfully teach concept",
        example="/profile",
    ),
    "/explain": PrimitiveInfo(
        unlock_level=4,
        description="AI explanation of current state",
        unlock_condition="Successfully teach concept",
        example="/explain",
    ),

    # Level 5 - After contributing
    "/discover-new": PrimitiveInfo(
        unlock_level=5,
        description="List recently unlocked tools",
        unlock_condition="Contribute content or teach successfully",
        example="/discover-new",
    ),
    "/teach <concept>": PrimitiveInfo(
        unlock_level=5,
        description="Enter teaching mode",
        unlock_condition="Transcend a concept (mastery level 4)",
        example="/teach lists",
    ),
    "/benchmark": PrimitiveInfo(
        unlock_level=5,
        description="Compare your approach to others",
        unlock_condition="Contribute content",
        example="/benchmark",
    ),
}


def get_available_primitives(player) -> list[str]:
    """Get primitives available to this player based on progress."""
    level = player.primitive_level
    return [
        name for name, info in PRIMITIVES.items()
        if info.unlock_level <= level
    ]


def get_primitive_info(name: str) -> Optional[PrimitiveInfo]:
    """Get info about a specific primitive."""
    return PRIMITIVES.get(name)
```

---

## Progressive Disclosure Philosophy

The primitive system follows these principles:

### 1. Don't Overwhelm Beginners

New learners see only `/help` and `/screenshot`. As they gain competence, more tools unlock.

```python
# Beginner (Level 0):
Available: /help, /screenshot

# After 1 challenge (Level 1):
Available: + /checkpoint, /restore

# After 5 challenges (Level 2):
Available: + /rewind, /step, /diff

# And so on...
```

### 2. Unlock Based on Demonstrated Competence

Primitives unlock when the player proves they can handle them:

- **Level 1:** Complete first challenge → Checkpoints (they understand code state)
- **Level 2:** Complete 5 challenges → Time travel (they understand progression)
- **Level 3:** Complete a level → Advanced capture (they're serious learners)
- **Level 4:** Teach successfully → Deep analysis (they understand deeply)
- **Level 5:** Contribute → Meta tools (they're community members)

### 3. Each Primitive Teaches Something

Every primitive is also a lesson:

- `/checkpoint` → State management
- `/diff` → Version control concepts
- `/trace` → Execution flow
- `/profile` → Performance analysis
- `/benchmark` → Comparative thinking

### 4. Gamified Discovery

```python
# When unlocking new level
print("🎉 LEVEL UP!")
print(f"\nYou've unlocked {len(new_primitives)} new tools:")
for primitive in new_primitives:
    print(f"  ✨ {primitive}")
print("\nType /discover-new to learn about them!")
```

---

## Implementation

```python
class PrimitiveManager:
    """Manage discovery primitives and unlock conditions."""

    def __init__(self, player):
        self.player = player
        self.primitives = PRIMITIVES

    def check_unlock(self, primitive_name: str) -> bool:
        """Check if player has unlocked this primitive."""
        info = self.primitives.get(primitive_name)
        if not info:
            return False

        return info.unlock_level <= self.player.primitive_level

    def update_level(self):
        """Update player's primitive level based on progress."""
        old_level = self.player.primitive_level

        # Determine new level
        if self.player.has_contributed:
            new_level = 5
        elif self.player.has_taught_successfully:
            new_level = 4
        elif self.player.levels_completed > 0:
            new_level = 3
        elif self.player.challenges_completed >= 5:
            new_level = 2
        elif self.player.challenges_completed >= 1:
            new_level = 1
        else:
            new_level = 0

        # If leveled up, notify
        if new_level > old_level:
            self.player.primitive_level = new_level
            self._notify_unlock(old_level, new_level)

    def _notify_unlock(self, old_level: int, new_level: int):
        """Notify player of newly unlocked primitives."""
        newly_unlocked = [
            (name, info) for name, info in self.primitives.items()
            if old_level < info.unlock_level <= new_level
        ]

        if newly_unlocked:
            print("\n" + "=" * 60)
            print("🎉 NEW TOOLS UNLOCKED!")
            print("=" * 60)

            for name, info in newly_unlocked:
                print(f"\n✨ {name}")
                print(f"   {info.description}")
                print(f"   Example: {info.example}")

            print("\nType /help to see all available commands")
            print("=" * 60 + "\n")
```

---

## Usage Examples

```python
# Check available primitives
primitives = get_available_primitives(player)
print(f"You have {len(primitives)} primitives unlocked")

# Use a primitive
if "/screenshot" in primitives:
    bundle = cmd_screenshot(game)

# Check what's next
manager = PrimitiveManager(player)
next_level = player.primitive_level + 1
print(f"Complete {5 - player.challenges_completed} more challenges to unlock Level {next_level} tools!")

# Discover newly unlocked
newly_unlocked = cmd_discover_new(game)
```

---

## Self-Teaching Note

This file demonstrates:
- **Progressive disclosure** (UX pattern) - Reveal complexity gradually
- **Command pattern** (Design pattern) - Encapsulate operations as objects
- **Decorator pattern** (Design pattern) - @command decorator for primitives
- **Dataclasses** (Level 5: Classes) - PrimitiveInfo structure
- **Dictionaries as registries** (Level 2+: Collections) - PRIMITIVES lookup
- **Conditional logic** (Level 1: Control flow) - Unlock conditions

Prerequisites to understand this file:
- Level 1: Control flow (if/else)
- Level 2: Collections (dicts, lists)
- Level 3: Functions (def, decorators)
- Level 5: Classes (@dataclass)

The learner will encounter this file when building the discovery primitive system for LMSP.
