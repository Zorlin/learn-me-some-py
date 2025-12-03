# Screenshot Wireframes - Mental Context Capture

## Overview

Every screenshot in LMSP includes a "mental wireframe" - the full context behind what's visible on screen. This is not just a pixel capture, but a **complete snapshot of game state, player state, code state, and multiplayer context**.

The wireframe enables Claude and other AI systems to understand:
- **What** the player is doing
- **Why** they're doing it
- **Where** they are in their learning journey
- **How** they're feeling about it
- **Who** else is involved (in multiplayer)

This transforms screenshots from static images into rich, analyzable data bundles.

---

## ScreenshotBundle Structure

The core data structure that combines visual and contextual data:

```python
from dataclasses import dataclass, field
from typing import Optional
import time
import ast

@dataclass
class Wireframe:
    """The mental context behind a screenshot."""

    # Code state
    code: str
    ast_dump: str  # Serialized AST
    cursor_position: tuple[int, int]  # (line, column)

    # Game state
    current_challenge: str
    tests_passing: int
    tests_total: int

    # Player state
    player_id: str
    mastery_levels: dict[str, int]
    current_emotion: Optional[dict]

    # Session state
    session_duration: float  # seconds
    challenges_completed: int

    # Multiplayer state (if active)
    other_players: list[dict] = field(default_factory=list)


@dataclass
class ScreenshotBundle:
    """Screenshot + wireframe = complete context."""

    image: bytes  # PNG or WebP bytes
    wireframe: Wireframe
    timestamp: float

    def to_json(self) -> dict:
        """Serialize for storage or transmission."""
        return {
            "timestamp": self.timestamp,
            "wireframe": {
                "code": self.wireframe.code,
                "ast": self.wireframe.ast_dump,
                "cursor": self.wireframe.cursor_position,
                "challenge": self.wireframe.current_challenge,
                "tests": f"{self.wireframe.tests_passing}/{self.wireframe.tests_total}",
                "player": self.wireframe.player_id,
                "mastery": self.wireframe.mastery_levels,
                "emotion": self.wireframe.current_emotion,
                "session": {
                    "duration": self.wireframe.session_duration,
                    "completed": self.wireframe.challenges_completed,
                },
                "multiplayer": self.wireframe.other_players,
            }
        }

    def save(self, path: Path):
        """Save screenshot and wireframe separately."""
        # Save image
        with open(path.with_suffix(".png"), "wb") as f:
            f.write(self.image)

        # Save wireframe as JSON
        with open(path.with_suffix(".json"), "w") as f:
            json.dump(self.to_json(), f, indent=2)
```

---

## AST Capture

The Abstract Syntax Tree provides structural understanding of the code:

```python
import ast
from typing import Optional

class ASTCapture:
    """Capture and serialize Python AST."""

    @staticmethod
    def capture(code: str) -> Optional[str]:
        """Parse code and return AST dump."""
        try:
            tree = ast.parse(code)
            return ast.dump(tree, indent=2)
        except SyntaxError as e:
            # Return error info instead
            return f"SyntaxError: {e.msg} at line {e.lineno}, col {e.offset}"

    @staticmethod
    def extract_structure(code: str) -> dict:
        """Extract key structural elements."""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return {"error": "syntax_error"}

        structure = {
            "functions": [],
            "classes": [],
            "variables": [],
            "imports": [],
            "control_flow": [],
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                structure["functions"].append({
                    "name": node.name,
                    "args": [arg.arg for arg in node.args.args],
                    "lineno": node.lineno,
                })
            elif isinstance(node, ast.ClassDef):
                structure["classes"].append({
                    "name": node.name,
                    "lineno": node.lineno,
                })
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        structure["variables"].append({
                            "name": target.id,
                            "lineno": node.lineno,
                        })
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        structure["imports"].append(alias.name)
                else:
                    structure["imports"].append(node.module)
            elif isinstance(node, (ast.If, ast.For, ast.While, ast.Match)):
                structure["control_flow"].append({
                    "type": node.__class__.__name__,
                    "lineno": node.lineno,
                })

        return structure

    @staticmethod
    def analyze_complexity(code: str) -> dict:
        """Analyze code complexity metrics."""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return {"error": "syntax_error"}

        complexity = {
            "total_nodes": 0,
            "depth": 0,
            "branches": 0,
            "loops": 0,
        }

        def walk_depth(node, depth=0):
            complexity["total_nodes"] += 1
            complexity["depth"] = max(complexity["depth"], depth)

            if isinstance(node, (ast.If, ast.Match)):
                complexity["branches"] += 1
            elif isinstance(node, (ast.For, ast.While)):
                complexity["loops"] += 1

            for child in ast.iter_child_nodes(node):
                walk_depth(child, depth + 1)

        walk_depth(tree)
        return complexity
```

---

## Game State in Wireframe

Capturing the current challenge context:

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class GameState:
    """Current game state for wireframe."""

    current_challenge: str
    challenge_level: int
    tests_passing: int
    tests_total: int
    hints_used: int
    time_elapsed: float

    # Challenge context
    skeleton_code: str
    current_code: str

    # Test results
    test_results: list[dict]  # [{name, passed, expected, actual}]

    # Progress
    cursor_line: int
    cursor_column: int
    code_changed_since_last_run: bool

    def summary(self) -> dict:
        """Summarize state for wireframe."""
        return {
            "challenge": self.current_challenge,
            "level": self.challenge_level,
            "tests": f"{self.tests_passing}/{self.tests_total}",
            "hints": self.hints_used,
            "time": round(self.time_elapsed, 1),
            "cursor": [self.cursor_line, self.cursor_column],
            "changed": self.code_changed_since_last_run,
        }

    def test_summary(self) -> list[dict]:
        """Summarize test results."""
        return [
            {
                "name": t["name"],
                "passed": t["passed"],
                **({"error": t["actual"]} if not t["passed"] else {}),
            }
            for t in self.test_results
        ]


class GameStateCapture:
    """Capture current game state for wireframes."""

    def __init__(self, game):
        self.game = game

    def capture(self) -> GameState:
        """Capture current game state."""
        return GameState(
            current_challenge=self.game.current_challenge.id,
            challenge_level=self.game.current_challenge.level,
            tests_passing=sum(1 for t in self.game.test_results if t.passed),
            tests_total=len(self.game.test_results),
            hints_used=self.game.hints_used,
            time_elapsed=self.game.session_duration,
            skeleton_code=self.game.current_challenge.skeleton_code,
            current_code=self.game.current_code,
            test_results=[
                {
                    "name": t.name,
                    "passed": t.passed,
                    "expected": t.expected,
                    "actual": t.actual,
                }
                for t in self.game.test_results
            ],
            cursor_line=self.game.cursor.line,
            cursor_column=self.game.cursor.column,
            code_changed_since_last_run=self.game.code_dirty,
        )
```

---

## Player State in Wireframe

Capturing learner progress and emotional state:

```python
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class PlayerState:
    """Current player state for wireframe."""

    player_id: str

    # Mastery levels
    mastery_levels: dict[str, int]  # {concept_id: 0-4}
    concepts_unlocked: list[str]

    # Session info
    session_start: datetime
    session_duration: float
    challenges_completed_today: int

    # Emotional state
    current_emotion: Optional[dict]  # Latest emotional reading
    flow_state: bool

    # Learning metrics
    streak_days: int
    total_challenges: int
    favorite_concepts: list[str]

    def summary(self) -> dict:
        """Summarize for wireframe."""
        return {
            "id": self.player_id,
            "mastery": {
                k: v for k, v in self.mastery_levels.items()
                if v > 0  # Only show concepts with progress
            },
            "unlocked": len(self.concepts_unlocked),
            "emotion": self.current_emotion,
            "flow": self.flow_state,
            "streak": self.streak_days,
            "total": self.total_challenges,
        }


class PlayerStateCapture:
    """Capture current player state."""

    def __init__(self, player, adaptive_engine):
        self.player = player
        self.engine = adaptive_engine

    def capture(self) -> PlayerState:
        """Capture current player state."""
        profile = self.engine.profile

        return PlayerState(
            player_id=self.player.id,
            mastery_levels=profile.mastery_levels.copy(),
            concepts_unlocked=profile.unlocked_concepts.copy(),
            session_start=self.player.session_start,
            session_duration=(datetime.now() - self.player.session_start).total_seconds(),
            challenges_completed_today=self.player.challenges_today,
            current_emotion=self.player.last_emotion,
            flow_state=self.engine.emotional_state.is_in_flow(),
            streak_days=profile.streak_days,
            total_challenges=profile.total_challenges,
            favorite_concepts=self.engine.fun_tracker.get_favorites(top_n=3),
        )
```

---

## Session State in Wireframe

Capturing overall session context:

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class SessionState:
    """Current session state for wireframe."""

    session_id: str
    start_time: datetime
    duration: float

    # Progress
    challenges_attempted: int
    challenges_completed: int
    concepts_practiced: list[str]

    # Adaptive tracking
    recommendations_followed: int
    recommendations_ignored: int
    breaks_taken: int

    # Performance
    average_completion_time: float
    hints_per_challenge: float
    test_pass_rate: float

    def summary(self) -> dict:
        """Summarize for wireframe."""
        return {
            "id": self.session_id,
            "duration": round(self.duration, 1),
            "completed": f"{self.challenges_completed}/{self.challenges_attempted}",
            "concepts": len(self.concepts_practiced),
            "avg_time": round(self.average_completion_time, 1),
            "hints_avg": round(self.hints_per_challenge, 2),
            "pass_rate": round(self.test_pass_rate, 2),
        }
```

---

## Multiplayer State in Wireframe

Capturing other players' context in multiplayer sessions:

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class OtherPlayerState:
    """State of another player in multiplayer."""

    player_id: str
    player_type: str  # "human" or "ai"

    # Current activity
    current_line: Optional[int]
    current_column: Optional[int]
    last_action: Optional[str]
    last_action_time: float

    # Progress
    tests_passing: int
    tests_total: int
    completion_percentage: float

    # AI-specific
    ai_strategy: Optional[str]  # For AI players
    ai_thought: Optional[str]   # Latest thought

    def summary(self) -> dict:
        """Summarize for wireframe."""
        return {
            "id": self.player_id,
            "type": self.player_type,
            "cursor": [self.current_line, self.current_column] if self.current_line else None,
            "action": self.last_action,
            "tests": f"{self.tests_passing}/{self.tests_total}",
            "progress": round(self.completion_percentage * 100, 1),
            **({"strategy": self.ai_strategy} if self.ai_strategy else {}),
            **({"thought": self.ai_thought} if self.ai_thought else {}),
        }


class MultiplayerStateCapture:
    """Capture multiplayer context."""

    def __init__(self, session):
        self.session = session

    def capture_others(self, exclude_player_id: str) -> list[OtherPlayerState]:
        """Capture state of all other players."""
        states = []

        for player in self.session.players:
            if player.id == exclude_player_id:
                continue

            states.append(OtherPlayerState(
                player_id=player.id,
                player_type="ai" if player.is_ai else "human",
                current_line=player.cursor.line if hasattr(player, "cursor") else None,
                current_column=player.cursor.column if hasattr(player, "cursor") else None,
                last_action=player.last_action,
                last_action_time=player.last_action_timestamp,
                tests_passing=player.tests_passing,
                tests_total=player.tests_total,
                completion_percentage=player.completion_percentage,
                ai_strategy=player.strategy if player.is_ai else None,
                ai_thought=player.last_thought if player.is_ai else None,
            ))

        return states
```

---

## Screenshot Class

The main Screenshot class that orchestrates capture:

```python
import io
from PIL import Image
from pathlib import Path
import json
import time

class Screenshot:
    """Capture screen state with full context metadata."""

    def __init__(self, game):
        self.game = game
        self.game_state_capture = GameStateCapture(game)
        self.player_state_capture = PlayerStateCapture(game.player, game.adaptive_engine)
        if hasattr(game, "multiplayer_session"):
            self.multiplayer_capture = MultiplayerStateCapture(game.multiplayer_session)
        else:
            self.multiplayer_capture = None

    def capture(self) -> ScreenshotBundle:
        """Capture screenshot + wireframe."""

        # Capture visual
        image_bytes = self._capture_screen()

        # Capture game state
        game_state = self.game_state_capture.capture()

        # Capture player state
        player_state = self.player_state_capture.capture()

        # Capture multiplayer (if active)
        other_players = []
        if self.multiplayer_capture:
            other_players_states = self.multiplayer_capture.capture_others(
                exclude_player_id=self.game.player.id
            )
            other_players = [p.summary() for p in other_players_states]

        # Build wireframe
        wireframe = Wireframe(
            # Code state
            code=game_state.current_code,
            ast_dump=ASTCapture.capture(game_state.current_code) or "",
            cursor_position=(game_state.cursor_line, game_state.cursor_column),

            # Game state
            current_challenge=game_state.current_challenge,
            tests_passing=game_state.tests_passing,
            tests_total=game_state.tests_total,

            # Player state
            player_id=player_state.player_id,
            mastery_levels=player_state.mastery_levels,
            current_emotion=player_state.current_emotion,

            # Session state
            session_duration=player_state.session_duration,
            challenges_completed=player_state.total_challenges,

            # Multiplayer state
            other_players=other_players,
        )

        return ScreenshotBundle(
            image=image_bytes,
            wireframe=wireframe,
            timestamp=time.time(),
        )

    def _capture_screen(self) -> bytes:
        """Capture current screen as PNG bytes."""
        # This would integrate with the actual rendering system
        # For now, placeholder implementation

        # In real implementation, would capture from Rich/Textual terminal
        # or from GUI rendering surface
        img = Image.new('RGB', (800, 600), color='black')

        # Render current game view to image
        # (This is where we'd draw the terminal/GUI state)

        # Convert to bytes
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()

    def capture_and_save(self, path: Path) -> ScreenshotBundle:
        """Capture and immediately save."""
        bundle = self.capture()
        bundle.save(path)
        return bundle
```

---

## Claude Vision Optimization

Optimizing wireframes for Claude's vision capabilities:

```python
class ClaudeOptimizedWireframe:
    """Optimize wireframe data for Claude vision analysis."""

    @staticmethod
    def format_for_claude(bundle: ScreenshotBundle) -> dict:
        """Format wireframe for Claude API."""
        wf = bundle.wireframe

        # Extract key information in Claude-friendly format
        return {
            "image": bundle.image,  # Actual screenshot
            "context": {
                "what": f"Challenge: {wf.current_challenge} ({wf.tests_passing}/{wf.tests_total} tests passing)",
                "code": wf.code,
                "structure": ASTCapture.extract_structure(wf.code),
                "cursor": {"line": wf.cursor_position[0], "col": wf.cursor_position[1]},
                "player": {
                    "id": wf.player_id,
                    "progress": f"{wf.challenges_completed} challenges completed",
                    "session_time": f"{round(wf.session_duration / 60, 1)} minutes",
                    "emotion": wf.current_emotion,
                    "mastery": {k: v for k, v in wf.mastery_levels.items() if v > 0},
                },
                "multiplayer": wf.other_players if wf.other_players else None,
            }
        }

    @staticmethod
    def generate_prompt(bundle: ScreenshotBundle, question: str) -> str:
        """Generate Claude prompt with wireframe context."""
        ctx = ClaudeOptimizedWireframe.format_for_claude(bundle)

        return f"""You're analyzing a screenshot from LMSP (Learn Me Some Py), a Python learning game.

**Challenge:** {ctx['context']['what']}

**Current Code:**
```python
{ctx['context']['code']}
```

**Code Structure:**
{json.dumps(ctx['context']['structure'], indent=2)}

**Cursor Position:** Line {ctx['context']['cursor']['line']}, Column {ctx['context']['cursor']['col']}

**Player State:**
- ID: {ctx['context']['player']['id']}
- Progress: {ctx['context']['player']['progress']}
- Session Time: {ctx['context']['player']['session_time']}
- Current Emotion: {ctx['context']['player']['emotion']}
- Mastery: {json.dumps(ctx['context']['player']['mastery'], indent=2)}

{f"**Multiplayer:** {json.dumps(ctx['context']['multiplayer'], indent=2)}" if ctx['context']['multiplayer'] else ""}

**Question:** {question}

Please analyze the screenshot AND the wireframe context to provide a comprehensive answer.
"""
```

---

## Usage Examples

```python
# Basic screenshot capture
screenshot = Screenshot(game)
bundle = screenshot.capture()

# Save to disk
bundle.save(Path("/tmp/screenshot_001"))
# Creates:
#   /tmp/screenshot_001.png
#   /tmp/screenshot_001.json

# Analyze with Claude
from lmsp.introspection.screenshot import ClaudeOptimizedWireframe

prompt = ClaudeOptimizedWireframe.generate_prompt(
    bundle,
    question="Why are only 2 of 5 tests passing? What's wrong with the code?"
)

# Send to Claude API
response = claude_api.analyze(prompt, images=[bundle.image])

# Get AST analysis
structure = ASTCapture.extract_structure(bundle.wireframe.code)
print(f"Functions: {len(structure['functions'])}")
print(f"Control flow: {structure['control_flow']}")

# Check complexity
complexity = ASTCapture.analyze_complexity(bundle.wireframe.code)
print(f"Depth: {complexity['depth']}, Branches: {complexity['branches']}")
```

---

## Integration with Discovery Primitives

```python
# /screenshot command (Level 0)
@command("/screenshot")
def cmd_screenshot(game):
    """Capture current state."""
    screenshot = Screenshot(game)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = Path(f"~/.lmsp/screenshots/{game.player.id}/{timestamp}").expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)

    bundle = screenshot.capture_and_save(path)

    print(f"Screenshot saved: {path}.png")
    print(f"Wireframe saved: {path}.json")
    print(f"Tests: {bundle.wireframe.tests_passing}/{bundle.wireframe.tests_total}")
    print(f"Session: {round(bundle.wireframe.session_duration / 60, 1)} minutes")

    return bundle

# /wireframe command (Level 3)
@command("/wireframe", unlock_level=3)
def cmd_wireframe(game):
    """Dump full context to console."""
    screenshot = Screenshot(game)
    bundle = screenshot.capture()

    print(json.dumps(bundle.to_json(), indent=2))

    return bundle
```

---

## Self-Teaching Note

This file demonstrates:
- **Dataclasses** (Level 5: Classes) - Clean data structures with @dataclass
- **Type hints** (Professional Python) - Optional, list, dict for clarity
- **AST module** (Level 6+: Metaprogramming) - Introspection of Python code
- **JSON serialization** (Level 4: Intermediate) - Converting objects to JSON
- **PIL/Image** (Standard library) - Image manipulation
- **Pathlib** (Professional Python) - Modern file path handling

Prerequisites to understand this file:
- Level 2: Collections (lists, dicts)
- Level 3: Functions (def, return, parameters)
- Level 5: Classes (class, __init__, self, @dataclass)

The learner will encounter this file AFTER mastering prerequisites, when building the introspection system for LMSP.
