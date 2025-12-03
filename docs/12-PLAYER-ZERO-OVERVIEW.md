# PLAYER-ZERO OVERVIEW - Universal App Automation

**Navigation:** [README](README.md) | [Architecture](10-ARCHITECTURE.md) | [LMSP Overview](11-LMSP-OVERVIEW.md) | [Palace Integration](13-PALACE-INTEGRATION.md)

---

## What is Player-Zero?

Player-Zero is a **universal app automation framework** that goes far beyond LMSP. It enables AI to playtest, analyze, and automate ANY application:

- **Python Games** → AI plays, finds bugs, tests edge cases, speedruns
- **Education Apps** → AI learns like a student, validates curriculum
- **Web Servers** → AI hits endpoints, validates behavior, fuzzes inputs
- **Browser Apps** → Playwright integration for full visual testing
- **CLI Tools** → AI runs commands, validates outputs, tests flags
- **APIs** → AI generates test cases, validates schemas, stress tests
- **Mobile Apps** → Via Appium integration, touch simulation

Think of it as **"Tool-Assisted Speedrunning meets AI-powered testing"** - but for any application, not just games.

---

## The Vision: Universal Automation

Traditional testing tools are application-specific:
- Selenium for web apps
- unittest/pytest for Python code
- Postman for APIs
- JMeter for load testing

Player-Zero provides a **unified framework** where Claude can interact with ANY application through a consistent interface:

```python
from player_zero import ClaudePlayer, Session

# AI playtests a game
player = ClaudePlayer(name="Tester")
session = Session(player=player, target=lmsp_game)
await session.run(goal="Complete level 1 without hints")

# Same AI playtests a web app
session = Session(player=player, target=web_app)
await session.run(goal="Find bugs in checkout flow")

# Same AI playtests a CLI tool
session = Session(player=player, target=cli_tool)
await session.run(goal="Test all command flags")
```

---

## Application Types Supported

### Python Games (like LMSP)

**Capabilities:**
- AI plays through challenges
- Discovers edge cases and bugs
- Tests different solution approaches
- Generates speedrun strategies
- Creates educational demos

**Example:**
```python
from player_zero import ClaudePlayer, PlaytestSession

player = ClaudePlayer(name="Speedrunner", skill_level=0.9)
session = PlaytestSession(
    player=player,
    target=lmsp_game,
    goal="Complete all Level 2 challenges in under 10 minutes"
)

report = await session.run()
# report.time_taken: 8.5 minutes
# report.bugs_found: ["Scope error in functions", "Off-by-one in median"]
# report.optimizations: ["Use list comprehension", "Cache sorted values"]
```

### Web Apps (Playwright)

**Capabilities:**
- Visual testing with screenshots
- Interaction with DOM elements
- Form filling and validation
- Navigation testing
- Accessibility audits

**Example:**
```python
from player_zero import ClaudePlayer
from player_zero.adapters import PlaywrightAdapter

async with PlaywrightAdapter() as browser:
    player = ClaudePlayer(name="WebTester")
    session = PlaytestSession(
        player=player,
        target=browser,
        goal="Test the checkout flow for edge cases"
    )

    report = await session.run(
        max_duration=300,
        screenshot_interval=5,
        record_video=True
    )

    # report contains:
    # - All actions taken
    # - Screenshots with wireframes
    # - Video mosaic
    # - Bugs discovered
    # - UX suggestions
```

### CLI Tools

**Capabilities:**
- Command execution and output validation
- Flag combination testing
- Error handling verification
- Performance benchmarking

**Example:**
```python
from player_zero import ClaudePlayer, CLISession

player = ClaudePlayer(name="CLITester")
session = CLISession(
    player=player,
    target="my-cli-tool",
    goal="Test all flags and combinations"
)

report = await session.run()
# report.commands_tested: 47
# report.bugs_found: ["--verbose conflicts with --quiet"]
# report.missing_docs: ["--format flag not in --help"]
```

### APIs (REST/GraphQL)

**Capabilities:**
- Endpoint discovery
- Schema validation
- Fuzz testing
- Load testing
- Documentation verification

**Example:**
```python
from player_zero import ClaudePlayer, APISession

player = ClaudePlayer(name="APITester")
session = APISession(
    player=player,
    base_url="https://api.example.com",
    goal="Find bugs and validate OpenAPI spec"
)

report = await session.run()
# report.endpoints_tested: 23
# report.schema_violations: ["POST /users returns wrong type"]
# report.bugs_found: ["Rate limiting broken", "Auth bypass on /admin"]
```

---

## Core Capabilities

### AI Playtesting

Claude plays your application like a real user:

```python
class ClaudePlayer:
    """AI player powered by Claude."""

    async def observe(self, state: GameState) -> Observation:
        """
        Observe current state and understand context.

        Returns Observation with:
        - What's visible
        - What's possible (available actions)
        - What's the goal
        - What's the current progress
        """
        pass

    async def decide(self, observation: Observation) -> Action:
        """
        Decide next action based on observation.

        Uses Claude to reason about:
        - What action moves toward goal
        - What actions explore new states
        - What actions test edge cases
        """
        pass

    async def act(self, action: Action) -> None:
        """
        Execute action in the application.

        Could be:
        - Typing code (LMSP)
        - Clicking button (web app)
        - Running command (CLI)
        - Sending request (API)
        """
        pass
```

**The Loop:**
```
Observe → Decide → Act → Observe → Decide → Act → ...
```

### Bug Discovery

AI explores edge cases humans miss:

- **Boundary testing** - Max values, min values, zero, negative
- **Invalid input** - Malformed data, wrong types, missing fields
- **State corruption** - Race conditions, interrupted flows
- **Integration issues** - Component interaction bugs
- **Accessibility** - Keyboard-only, screen reader compatibility

**Example Bug Report:**
```json
{
  "bug_id": "lmsp-001",
  "severity": "high",
  "title": "Scope error with nested functions",
  "description": "When defining a function inside another function, global variables leak into inner scope",
  "reproduction": [
    "Create challenge with nested functions",
    "Reference variable from outer scope",
    "Observe incorrect value"
  ],
  "expected": "Inner function should have own scope",
  "actual": "Inner function inherits outer variables",
  "screenshot": "lmsp-001.png",
  "video_mosaic": "lmsp-001-mosaic.webp"
}
```

### Demo Generation

AI plays your app to create marketing demos:

```python
session = PlaytestSession(
    player=ClaudePlayer(name="DemoCreator", style="smooth"),
    target=lmsp_game,
    goal="Create a 2-minute demo showing off radial typing"
)

demo = await session.run(
    record_video=True,
    target_duration=120,
    optimize_for="visual_clarity"
)

# demo.video: Full video of AI playing
# demo.narration: AI-generated voice-over script
# demo.key_moments: Timestamps of impressive actions
```

### Competitive Benchmarking

Multiple AIs race to solve the same problem:

```python
from player_zero import ClaudePlayer, CompetitiveSession

players = [
    ClaudePlayer(name="BruteForce", strategy="exhaustive"),
    ClaudePlayer(name="Elegant", strategy="minimal_code"),
    ClaudePlayer(name="Fast", strategy="speed"),
    ClaudePlayer(name="Readable", strategy="clarity")
]

session = CompetitiveSession(
    players=players,
    target=lmsp_game,
    challenge="container_add_exists"
)

results = await session.run()

# results.winner: "Fast" (completed in 45 seconds)
# results.approaches: {
#     "BruteForce": "45 lines, 12ms, verbose",
#     "Elegant": "23 lines, 8ms, list comprehension",
#     "Fast": "31 lines, 3ms, optimized",
#     "Readable": "52 lines, 15ms, well-commented"
# }
# results.analysis: "Fast wins on speed, Elegant on code quality"
```

### Educational Content

AI teaches by demonstrating:

```python
session = TeachingSession(
    teacher=ClaudePlayer(name="Teacher"),
    students=[
        ClaudePlayer(name="Student1", skill_level=0.3),
        ClaudePlayer(name="Student2", skill_level=0.5),
    ],
    target=lmsp_game,
    concept="list_comprehensions"
)

lesson = await session.run()

# lesson.transcript: Full conversation
# lesson.key_moments: When students had breakthroughs
# lesson.mistakes: Common errors and corrections
# lesson.assessments: How well each student learned
```

### Accessibility Testing

AI finds usability issues:

```python
session = AccessibilitySession(
    player=ClaudePlayer(name="A11yTester"),
    target=web_app,
    constraints=[
        "keyboard_only",  # No mouse
        "screen_reader",  # Narrated navigation
        "low_vision"      # High contrast, large text
    ]
)

report = await session.run()

# report.issues: [
#     "Button not reachable via Tab",
#     "Missing alt text on images",
#     "Form label not associated with input"
# ]
```

### Regression Testing

AI replays sessions after code changes:

```python
# Record original session
session = PlaytestSession(player=ai, target=lmsp_game)
recording = await session.run_and_record()
recording.save("baseline.json")

# ... make code changes ...

# Replay and compare
replay = PlaytestSession(player=ai, target=lmsp_game)
report = await replay.replay_and_compare("baseline.json")

# report.differences: [
#     "Challenge completion now takes 10% longer",
#     "Test output format changed",
#     "NEW BUG: Exception on edge case"
# ]
```

### Load Testing

Swarm of AIs simulate concurrent users:

```python
session = SwarmSession(
    player_count=100,
    target=web_app,
    goal="Stress test checkout flow"
)

report = await session.run(duration=300)

# report.requests_per_second: 450
# report.errors: 3 (timeouts)
# report.slowest_endpoint: "/api/payment" (2.5s avg)
# report.bottlenecks: ["Database connection pool saturated"]
```

---

## File Structure

```
/mnt/castle/garage/player-zero/
├── .palace/                      # Palace integration
│   ├── config.json               # Project configuration
│   └── history.jsonl             # Development log
│
├── player_zero/                  # Main Python package
│   ├── __init__.py
│   ├── main.py                   # CLI entry point
│   │
│   ├── player/                   # Player implementations
│   │   ├── __init__.py
│   │   ├── base.py               # Player protocol/trait
│   │   ├── claude.py             # Claude player implementation
│   │   ├── human.py              # Human player adapter
│   │   └── composite.py          # Multi-player wrapper
│   │
│   ├── session/                  # Session modes
│   │   ├── __init__.py
│   │   ├── base.py               # Session protocol
│   │   ├── coop.py               # Cooperative mode
│   │   ├── competitive.py        # Racing/competitive mode
│   │   ├── teaching.py           # One teaches, others learn
│   │   ├── spectator.py          # Watch AI with commentary
│   │   └── swarm.py              # N AIs, different approaches
│   │
│   ├── adapters/                 # Application adapters
│   │   ├── __init__.py
│   │   ├── python_game.py        # Python game adapter (LMSP)
│   │   ├── playwright.py         # Web app via Playwright
│   │   ├── cli.py                # CLI tool via subprocess
│   │   ├── api.py                # REST/GraphQL APIs
│   │   └── mobile.py             # Mobile via Appium
│   │
│   ├── stream/                   # Stream-JSON protocol
│   │   ├── __init__.py
│   │   ├── json.py               # Stream-JSON parser/emitter
│   │   ├── broadcast.py          # Multi-player broadcast
│   │   └── sync.py               # State synchronization
│   │
│   ├── tas/                      # Tool-Assisted features
│   │   ├── __init__.py
│   │   ├── record.py             # Recording actions
│   │   ├── playback.py           # Replaying actions
│   │   ├── rewind.py             # Step backward
│   │   ├── checkpoint.py         # Save states
│   │   └── diff.py               # Compare checkpoints
│   │
│   ├── sandbox/                  # Sandboxing
│   │   ├── __init__.py
│   │   ├── podman.py             # Rootless Podman integration
│   │   └── cgroups.py            # Direct cgroups (fallback)
│   │
│   └── introspection/            # Analysis tools
│       ├── __init__.py
│       ├── screenshot.py         # Capture + wireframe
│       ├── video.py              # Strategic recording
│       └── mosaic.py             # Frame mosaic for Claude vision
│
├── protocols/                    # Protocol definitions
│   ├── player.proto              # Player state protocol (protobuf)
│   └── game.proto                # Game state protocol
│
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── test_player.py
│   ├── test_session.py
│   ├── test_stream_json.py
│   ├── test_tas.py
│   └── integration/
│       ├── test_lmsp.py
│       └── test_playwright.py
│
├── examples/                     # Example scripts
│   ├── lmsp_coop.py              # LMSP cooperative mode
│   ├── lmsp_race.py              # LMSP competitive mode
│   ├── web_playtest.py           # Web app testing
│   └── api_fuzz.py               # API fuzzing
│
├── pyproject.toml                # Python project config
├── CLAUDE.md                     # Claude Code instructions
└── README.md                     # Documentation
```

---

## Playwright Connection Example

Player-Zero's power comes from **application adapters**. Here's how Playwright integration works:

```python
# player_zero/adapters/playwright.py
from playwright.async_api import async_playwright, Page
from player_zero.player import ClaudePlayer
from player_zero.session import PlaytestSession

class PlaywrightAdapter:
    """
    Adapter that lets Claude interact with web apps via Playwright.

    Claude can:
    - See screenshots of the page
    - Read DOM structure
    - Click elements
    - Type into forms
    - Navigate pages
    - Validate behavior
    """

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page: Page = None

    async def __aenter__(self):
        """Start browser."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch()
        self.page = await self.browser.new_page()
        return self

    async def __aexit__(self, *args):
        """Stop browser."""
        await self.browser.close()
        await self.playwright.stop()

    async def observe(self) -> dict:
        """
        Capture current state for Claude.

        Returns:
            {
                "url": Current URL,
                "title": Page title,
                "screenshot": Base64 screenshot,
                "dom": Simplified DOM tree,
                "visible_text": All visible text,
                "interactive_elements": Buttons, links, inputs
            }
        """
        screenshot = await self.page.screenshot()
        dom = await self.page.content()

        return {
            "url": self.page.url,
            "title": await self.page.title(),
            "screenshot": screenshot,
            "dom": self._simplify_dom(dom),
            "visible_text": await self._get_visible_text(),
            "interactive_elements": await self._get_interactive_elements()
        }

    async def act(self, action: dict):
        """
        Execute action based on Claude's decision.

        Supported actions:
        - {"type": "click", "selector": "#button"}
        - {"type": "type", "selector": "#input", "text": "hello"}
        - {"type": "navigate", "url": "https://..."}
        - {"type": "scroll", "direction": "down"}
        - {"type": "wait", "duration": 2.0}
        """
        action_type = action["type"]

        if action_type == "click":
            await self.page.click(action["selector"])

        elif action_type == "type":
            await self.page.fill(action["selector"], action["text"])

        elif action_type == "navigate":
            await self.page.goto(action["url"])

        elif action_type == "scroll":
            await self.page.evaluate(f"window.scrollBy(0, {action['amount']})")

        elif action_type == "wait":
            await self.page.wait_for_timeout(action["duration"] * 1000)

    async def _get_visible_text(self) -> str:
        """Extract all visible text from page."""
        return await self.page.evaluate("document.body.innerText")

    async def _get_interactive_elements(self) -> list[dict]:
        """Find all buttons, links, inputs."""
        return await self.page.evaluate("""
            () => {
                const elements = [];
                document.querySelectorAll('button, a, input, select').forEach(el => {
                    elements.push({
                        tag: el.tagName,
                        text: el.innerText || el.value,
                        selector: el.id ? `#${el.id}` : el.className ? `.${el.className.split(' ')[0]}` : el.tagName
                    });
                });
                return elements;
            }
        """)

# Usage
async with PlaywrightAdapter() as browser:
    player = ClaudePlayer(name="WebTester")

    session = PlaytestSession(
        player=player,
        target=browser,
        goal="Test the checkout flow"
    )

    await session.run()
```

**What Claude sees:**
```json
{
  "url": "https://shop.example.com/checkout",
  "title": "Checkout - Example Shop",
  "screenshot": "data:image/png;base64,...",
  "visible_text": "Checkout\n\nShipping Address\n[...]\n",
  "interactive_elements": [
    {"tag": "INPUT", "text": "", "selector": "#email"},
    {"tag": "INPUT", "text": "", "selector": "#address"},
    {"tag": "BUTTON", "text": "Continue", "selector": "#continue-btn"}
  ]
}
```

**What Claude decides:**
```json
{
  "type": "type",
  "selector": "#email",
  "text": "test@example.com",
  "reasoning": "Need to fill email before continuing"
}
```

---

## Session Modes

### Coop Mode

Human and AI work together on same problem:

```python
session = CoopSession(players=[human, ai])
session.set_challenge("container_add_exists")

# Human types: "def solution(queries):"
# AI sees typing, emits: {"type": "thought", "content": "Good start!"}
# Human types: "    container = []"
# AI emits: {"type": "suggestion", "content": "Don't forget to initialize results = []"}
# Human follows suggestion
# Both complete challenge together
```

### Competitive Mode

Race to solve first:

```python
session = CompetitiveSession(players=[human, ai1, ai2])
session.set_challenge("container_add_exists")

# All players start simultaneously
# First to pass all tests wins
# Leaderboard shows time, lines of code, approach
```

### Teaching Mode

One player teaches, others learn:

```python
session = TeachingSession(
    teacher=ai_teacher,
    students=[human, ai_student1, ai_student2]
)

# Teacher explains concept
# Students ask questions
# Teacher presents challenge
# Students attempt with guidance
# Teacher provides feedback
```

### Spectator Mode

Watch AI play with commentary:

```python
session = SpectatorSession(player=ai)

# AI plays LMSP
# Emits thoughts: "I'll use list comprehension here"
# Emits explanations: "This handles the edge case of empty input"
# Human watches and learns from AI's approach
```

### Swarm Mode

N AIs tackle problem with different strategies:

```python
session = SwarmSession(player_count=5, strategies=[
    "brute_force",
    "elegant",
    "fast",
    "readable",
    "creative"
])

# All AIs start simultaneously
# Each uses different approach
# Results compared at end
# Best approaches highlighted
```

---

## TAS (Tool-Assisted) Features

### Recording

```python
from player_zero.tas import Recorder

recorder = Recorder()
recorder.start()

# ... play LMSP ...

recording = recorder.stop()
recording.save("session.json")

# recording contains:
# - Every keystroke
# - Every test result
# - Every emotional input
# - Full game state at each moment
```

### Playback

```python
from player_zero.tas import Replayer

replayer = Replayer()
recording = replayer.load("session.json")

# Play at normal speed
await replayer.play(speed=1.0)

# Fast-forward
await replayer.play(speed=4.0)

# Single-step
while not replayer.done:
    await replayer.step()
    # Show current state
```

### Rewind

```python
# Go back 10 steps
await replayer.rewind(steps=10)

# Go back to checkpoint
await replayer.rewind_to_checkpoint("before_bug")
```

### Checkpoints

```python
# Create checkpoint
recorder.checkpoint("before_bug")

# ... continue playing ...

# Create another checkpoint
recorder.checkpoint("after_fix")

# Compare checkpoints
diff = recorder.diff("before_bug", "after_fix")
# diff shows:
# - Code changes
# - State changes
# - Events between checkpoints
```

---

## Integration with LMSP

Player-Zero is LMSP's multiplayer engine:

```
┌─────────────────────────────────────────────────────────────────┐
│                    LMSP + PLAYER-ZERO                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  LMSP Game                         Player-Zero                   │
│  ┌──────────────────┐              ┌──────────────────┐         │
│  │ Human plays      │              │ AI plays         │         │
│  │ Emits events     │──Stream────►│ Receives events  │         │
│  │ Receives events  │◄───JSON─────│ Emits events     │         │
│  └──────────────────┘              └──────────────────┘         │
│                                                                  │
│  Events:                           Events:                       │
│  - Keystrokes                      - Thoughts                    │
│  - Test results                    - Suggestions                 │
│  - Emotional input                 - Questions                   │
│  - Challenge completion            - Explanations                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**LMSP spawns Player-Zero:**
```python
# lmsp/multiplayer/player_zero.py
import subprocess
from player_zero import ClaudePlayer

def spawn_ai_player(name: str, style: str = "encouraging"):
    """Spawn Player-Zero process for multiplayer."""
    process = subprocess.Popen(
        ["player-zero", "play", "--name", name, "--style", style],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return process
```

**LMSP sends game state:**
```python
# lmsp/multiplayer/session.py
def broadcast_event(event: dict):
    """Send event to all AI players."""
    event_json = json.dumps(event) + "\n"
    for player in ai_players:
        player.stdin.write(event_json.encode())
        player.stdin.flush()
```

**Player-Zero reads and responds:**
```python
# player_zero/main.py
async def play():
    """Main loop for AI player."""
    player = ClaudePlayer()

    while True:
        # Read event from LMSP
        line = sys.stdin.readline()
        if not line:
            break

        event = json.loads(line)

        # Update internal state
        player.observe(event)

        # Decide action
        action = await player.decide()

        # Emit action to LMSP
        sys.stdout.write(json.dumps(action) + "\n")
        sys.stdout.flush()
```

---

## Future: Beyond LMSP

Player-Zero's architecture enables automation of ANY application:

### Mobile Apps (via Appium)
```python
from player_zero.adapters import AppiumAdapter

async with AppiumAdapter(platform="iOS", app="MyApp.app") as device:
    player = ClaudePlayer(name="MobileTester")
    session = PlaytestSession(player=player, target=device)
    await session.run(goal="Test signup flow")
```

### Desktop Apps (via accessibility APIs)
```python
from player_zero.adapters import DesktopAdapter

async with DesktopAdapter(app="MyDesktopApp") as desktop:
    player = ClaudePlayer(name="DesktopTester")
    session = PlaytestSession(player=player, target=desktop)
    await session.run(goal="Test all menu items")
```

### Video Games (via screen capture + input injection)
```python
from player_zero.adapters import GameAdapter

async with GameAdapter(window_title="My Game") as game:
    player = ClaudePlayer(name="Speedrunner")
    session = PlaytestSession(player=player, target=game)
    await session.run(goal="Complete game as fast as possible")
```

---

**Next:** [Palace Integration](13-PALACE-INTEGRATION.md) - TDD enforcement and development workflow

**See Also:**
- [Stream-JSON Protocol](13-STREAM-JSON.md) - Event specification
- [Multiplayer Integration](08-MULTIPLAYER-INTEGRATION.md) - LMSP multiplayer modes
- [TAS Recording](14-TAS-RECORDING.md) - Tool-assisted features
