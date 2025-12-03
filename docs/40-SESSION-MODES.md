# Session Modes - Multiplayer Learning in LMSP

**Complete reference for all multiplayer session modes in Learn Me Some Py.**

---

## Table of Contents

1. [Overview](#overview)
2. [Session Architecture](#session-architecture)
3. [COOP Mode](#coop-mode)
4. [RACE Mode](#race-mode)
5. [TEACH Mode](#teach-mode)
6. [SWARM Mode](#swarm-mode)
7. [SPECTATOR Mode](#spectator-mode)
8. [Session Lifecycle](#session-lifecycle)
9. [Mode Switching](#mode-switching)
10. [State Synchronization](#state-synchronization)

---

## Overview

LMSP supports five multiplayer session modes, each designed for different learning styles and goals:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SESSION MODE OVERVIEW                               │
├─────────────┬───────────────────────┬─────────────────────────────────────┤
│ Mode        │ Primary Use Case      │ Players                             │
├─────────────┼───────────────────────┼─────────────────────────────────────┤
│ COOP        │ Pair programming      │ 2-4 (mix of human/AI)              │
│ RACE        │ Competitive learning  │ 2-8 (any combination)              │
│ TEACH       │ Expert demonstration  │ 1 teacher + N students             │
│ SWARM       │ Strategy comparison   │ 3-8 AIs with different approaches  │
│ SPECTATOR   │ Watch & learn        │ 1 player + N spectators            │
└─────────────┴───────────────────────┴─────────────────────────────────────┘
```

Each mode has:
- **Shared state** - What all players can see
- **Private state** - What only individual players track
- **Communication rules** - How players interact
- **Win conditions** - How success is measured
- **Learning objectives** - What each mode teaches best

---

## Session Architecture

All session modes share a common base architecture:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SESSION ARCHITECTURE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         Session Manager                              │   │
│  │                                                                      │   │
│  │  - Challenge state (code, tests, validation)                       │   │
│  │  - Player roster (names, capabilities, status)                      │   │
│  │  - Event stream (cursor moves, keystrokes, emotions)                │   │
│  │  - Synchronization (state broadcast, conflict resolution)           │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                   │                                          │
│                 ┌─────────────────┼─────────────────┐                        │
│                 │                 │                 │                        │
│         ┌───────▼──────┐  ┌───────▼──────┐  ┌───────▼──────┐               │
│         │  Player 1    │  │  Player 2    │  │  Player N    │               │
│         │              │  │              │  │              │               │
│         │  - Input     │  │  - Input     │  │  - Input     │               │
│         │  - Cursor    │  │  - Cursor    │  │  - Cursor    │               │
│         │  - Progress  │  │  - Progress  │  │  - Progress  │               │
│         └──────────────┘  └──────────────┘  └──────────────┘               │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         Stream-JSON Bus                              │   │
│  │                                                                      │   │
│  │  All events flow through central message bus:                       │   │
│  │  - cursor_move, keystroke, thought, suggestion                      │   │
│  │  - emotion, test_result, completion                                 │   │
│  │                                                                      │   │
│  │  Each player receives all events (filtered by mode rules)           │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Base Session Interface

```python
class Session(ABC):
    """Base class for all session modes."""

    def __init__(self, players: list[Player], challenge: str):
        self.players = players
        self.challenge = challenge
        self.state = SharedState()
        self.event_bus = EventBus()
        self.started_at: float | None = None
        self.completed_at: float | None = None

    @abstractmethod
    async def start(self):
        """Start the session."""
        pass

    @abstractmethod
    async def handle_event(self, event: GameEvent):
        """Process game event according to mode rules."""
        pass

    @abstractmethod
    def check_completion(self) -> bool:
        """Determine if session is complete."""
        pass

    async def broadcast(self, event: GameEvent):
        """Send event to all players via event bus."""
        await self.event_bus.publish(event)
```

---

## COOP Mode

**Cooperative learning where players share a cursor and take turns solving challenges.**

### Visual Representation

```
┌──────────────────────────────────────────────────────────────┐
│                      COOP SESSION                             │
│                                                               │
│  Challenge: Container Add/Exists                              │
│  Players: Wings (Human), Lief (AI)                           │
│                                                               │
│  ╭──────────────────────────────────────────────────────╮    │
│  │ Code:                                                 │    │
│  │                                                       │    │
│  │   1  def solution(queries):                          │    │
│  │   2      container = []  ← Wings (completed)         │    │
│  │   3      results = []                                 │    │
│  │   4      for command, value in queries:  ← Lief      │    │
│  │   5          █                                        │    │
│  │                                                       │    │
│  ╰──────────────────────────────────────────────────────╯    │
│                                                               │
│  ┌────────────────────────────────────────────────────┐      │
│  │ Activity Feed:                                     │      │
│  │                                                     │      │
│  │ 14:32:45 Wings: Created function signature         │      │
│  │ 14:32:52 Wings: Initialized container list         │      │
│  │ 14:33:01 [Turn passed to Lief]                    │      │
│  │ 14:33:03 Lief: Starting for loop...                │      │
│  │ 14:33:05 Lief: "Don't forget the colon!"          │      │
│  └────────────────────────────────────────────────────┘      │
│                                                               │
│  Current Turn: Lief                                          │
│  [Pass Turn] [Hint] [Run Tests]                             │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### Turn-Based Mechanics

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          COOP TURN MECHANICS                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Turn Duration:                                                              │
│    - Default: 60 seconds per turn                                           │
│    - Extensions: +30s per hint request                                      │
│    - Auto-pass: If idle for 10 seconds                                      │
│                                                                              │
│  Turn Actions:                                                               │
│    ┌──────────────────────┬──────────────────────────────────────┐          │
│    │ Action               │ Effect                               │          │
│    ├──────────────────────┼──────────────────────────────────────┤          │
│    │ Type code            │ Adds to shared buffer                │          │
│    │ Run tests            │ Validates, shows results to all      │          │
│    │ Request hint         │ Extends turn, shows hint to all      │          │
│    │ Pass turn            │ Explicit handoff to next player      │          │
│    │ Suggest              │ Send message (doesn't use turn time) │          │
│    │ Express emotion      │ Update emotional state (no time)     │          │
│    └──────────────────────┴──────────────────────────────────────┘          │
│                                                                              │
│  Turn Passing:                                                               │
│    1. Player explicitly passes                                              │
│    2. Player completes a logical unit (function, loop, etc.)                │
│    3. Turn timer expires                                                    │
│    4. All tests pass (triggers celebration, continues session)              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Implementation

```python
class CoopSession(Session):
    """Cooperative session with shared cursor and turn-based input."""

    def __init__(self, players: list[Player], challenge: str):
        super().__init__(players, challenge)
        self.current_turn: int = 0  # Index into players list
        self.turn_started_at: float = 0
        self.turn_duration: float = 60.0  # seconds
        self.shared_code: str = ""
        self.shared_cursor: tuple[int, int] = (0, 0)

    async def start(self):
        """Begin cooperative session."""
        self.started_at = time.time()
        self.turn_started_at = time.time()

        # Load challenge
        challenge = await self.load_challenge()
        self.shared_code = challenge.skeleton

        # Notify all players
        await self.broadcast(SessionStartEvent(
            mode="coop",
            players=[p.name for p in self.players],
            challenge=challenge.name
        ))

        # Start first turn
        await self.start_turn(self.current_turn)

    async def start_turn(self, player_idx: int):
        """Grant turn to specific player."""
        self.current_turn = player_idx
        self.turn_started_at = time.time()

        current_player = self.players[player_idx]

        await self.broadcast(TurnStartEvent(
            player=current_player.name,
            duration=self.turn_duration,
            code=self.shared_code,
            cursor=self.shared_cursor
        ))

    async def handle_event(self, event: GameEvent):
        """Process events according to COOP rules."""

        # Only current turn player can modify code
        if event.type in ["keystroke", "cursor_move"]:
            if event.player != self.players[self.current_turn].name:
                return  # Ignore input from non-active player

            if event.type == "keystroke":
                self.apply_keystroke(event)
            else:
                self.shared_cursor = (event.line, event.col)

        # All players can express emotions and thoughts
        elif event.type in ["emotion", "thought", "suggestion"]:
            # Broadcast to all
            await self.broadcast(event)

        # Turn control events
        elif event.type == "pass_turn":
            await self.pass_turn()

        # Test execution
        elif event.type == "run_tests":
            results = await self.run_tests()
            await self.broadcast(TestResultEvent(
                passed=results.passed,
                total=results.total,
                details=results.details
            ))

            if results.all_passed:
                await self.complete_session()

        # Check turn timeout
        if time.time() - self.turn_started_at > self.turn_duration:
            await self.pass_turn()

    async def pass_turn(self):
        """Pass to next player."""
        next_idx = (self.current_turn + 1) % len(self.players)
        await self.start_turn(next_idx)

    def apply_keystroke(self, event: KeystrokeEvent):
        """Apply keystroke to shared code buffer."""
        # Split into lines
        lines = self.shared_code.split('\n')
        line, col = self.shared_cursor

        if event.char == '\n':
            # Insert newline
            current_line = lines[line]
            lines.insert(line + 1, current_line[col:])
            lines[line] = current_line[:col]
            self.shared_cursor = (line + 1, 0)
        elif event.char == '\b':
            # Backspace
            if col > 0:
                lines[line] = lines[line][:col-1] + lines[line][col:]
                self.shared_cursor = (line, col - 1)
        else:
            # Insert character
            lines[line] = lines[line][:col] + event.char + lines[line][col:]
            self.shared_cursor = (line, col + 1)

        self.shared_code = '\n'.join(lines)

        # Broadcast update
        asyncio.create_task(self.broadcast(CodeUpdateEvent(
            code=self.shared_code,
            cursor=self.shared_cursor,
            player=event.player
        )))

    def check_completion(self) -> bool:
        """Session complete when all tests pass."""
        return hasattr(self, '_completed') and self._completed

    async def complete_session(self):
        """Mark session complete, celebrate."""
        self._completed = True
        self.completed_at = time.time()
        duration = self.completed_at - self.started_at

        await self.broadcast(SessionCompleteEvent(
            duration=duration,
            players=[p.name for p in self.players],
            final_code=self.shared_code
        ))
```

### Best Practices

- **Communication is key** - Use thoughts/suggestions liberally
- **Bite-sized turns** - Complete one logical unit per turn
- **Respectful** - Let AI players have equal input time
- **Learning focus** - Slower is fine, understanding matters

---

## RACE Mode

**Competitive mode where players solve the same challenge independently and race to completion.**

### Visual Representation

```
┌────────────────────────────┬────────────────────────────┐
│         WINGS              │          LIEF              │
│    (Human Player)          │       (AI Player)          │
├────────────────────────────┼────────────────────────────┤
│                            │                            │
│ def solution(queries):     │ def solution(queries):     │
│     container = []         │     c = []                 │
│     results = []           │     r = []                 │
│     for q in queries:      │     for cmd, v in queries: │
│         █                  │         match cmd:         │
│                            │             case "add":    │
│                            │                 █          │
│                            │                            │
│ ┌────────────────────────┐ │ ┌────────────────────────┐ │
│ │ Tests: 2/5 passing     │ │ │ Tests: 4/5 passing     │ │
│ │ Time: 2:34             │ │ │ Time: 2:12             │ │
│ │ Hints used: 1          │ │ │ Hints used: 0          │ │
│ └────────────────────────┘ │ └────────────────────────┘ │
│                            │                            │
│ Emotion: 😊 (0.7)         │ Emotion: 🤔 (thinking)     │
│                            │                            │
└────────────────────────────┴────────────────────────────┘
│                                                          │
│  Leaderboard:                                            │
│    1. Lief      - 4/5 tests (2:12)                      │
│    2. Wings     - 2/5 tests (2:34)                      │
│                                                          │
│  [View Other Solutions] [Request Hint] [Run Tests]      │
└──────────────────────────────────────────────────────────┘
```

### Split-Screen Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          RACE MODE LAYOUT                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  2 Players: Side-by-side                                                    │
│  ┌──────────────────────────┬──────────────────────────┐                   │
│  │      Player 1            │      Player 2            │                   │
│  │                          │                          │                   │
│  │  [Full editor view]      │  [Full editor view]      │                   │
│  │  [Test results]          │  [Test results]          │                   │
│  │  [Stats]                 │  [Stats]                 │                   │
│  └──────────────────────────┴──────────────────────────┘                   │
│                                                                              │
│  3-4 Players: Quad view                                                     │
│  ┌──────────────────┬──────────────────┐                                   │
│  │   Player 1       │   Player 2       │                                   │
│  │  [Compact view]  │  [Compact view]  │                                   │
│  ├──────────────────┼──────────────────┤                                   │
│  │   Player 3       │   Player 4       │                                   │
│  │  [Compact view]  │  [Compact view]  │                                   │
│  └──────────────────┴──────────────────┘                                   │
│                                                                              │
│  5-8 Players: Grid view                                                     │
│  ┌───────┬───────┬───────┬───────┐                                         │
│  │  P1   │  P2   │  P3   │  P4   │                                         │
│  ├───────┼───────┼───────┼───────┤                                         │
│  │  P5   │  P6   │  P7   │  P8   │                                         │
│  └───────┴───────┴───────┴───────┘                                         │
│  (Minimal view: tests passing, time, position)                              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Implementation

```python
class RaceSession(Session):
    """Competitive session where players solve independently."""

    def __init__(self, players: list[Player], challenge: str):
        super().__init__(players, challenge)

        # Each player has private state
        self.player_states: dict[str, PlayerRaceState] = {}
        for player in players:
            self.player_states[player.name] = PlayerRaceState(
                code="",
                cursor=(0, 0),
                tests_passed=0,
                hints_used=0,
                started_at=0
            )

        self.completion_order: list[str] = []

    async def start(self):
        """Begin race."""
        self.started_at = time.time()

        # Load challenge
        challenge = await self.load_challenge()

        # Initialize all player states
        for player_name, state in self.player_states.items():
            state.code = challenge.skeleton
            state.started_at = time.time()

        # Countdown
        for i in [3, 2, 1]:
            await self.broadcast(CountdownEvent(count=i))
            await asyncio.sleep(1)

        await self.broadcast(SessionStartEvent(
            mode="race",
            players=[p.name for p in self.players],
            challenge=challenge.name
        ))

    async def handle_event(self, event: GameEvent):
        """Process events - each player edits their own code."""

        player_state = self.player_states.get(event.player)
        if not player_state:
            return

        # Already completed? Ignore further edits
        if event.player in self.completion_order:
            return

        if event.type == "keystroke":
            self.apply_keystroke_to_player(event.player, event)

            # Broadcast minimal update (just test status)
            await self.broadcast(PlayerProgressEvent(
                player=event.player,
                tests_passed=player_state.tests_passed,
                elapsed=time.time() - player_state.started_at
            ))

        elif event.type == "run_tests":
            results = await self.run_tests_for_player(event.player)
            player_state.tests_passed = results.passed

            await self.broadcast(TestResultEvent(
                player=event.player,
                passed=results.passed,
                total=results.total
            ))

            # Check completion
            if results.all_passed:
                await self.player_completed(event.player)

        elif event.type == "hint_request":
            player_state.hints_used += 1
            hint = await self.get_hint(player_state.hints_used)

            await self.send_to_player(event.player, HintEvent(
                content=hint,
                hint_level=player_state.hints_used
            ))

    async def player_completed(self, player_name: str):
        """Mark player as finished."""
        if player_name in self.completion_order:
            return  # Already finished

        self.completion_order.append(player_name)
        position = len(self.completion_order)

        player_state = self.player_states[player_name]
        completion_time = time.time() - player_state.started_at

        await self.broadcast(PlayerCompletedEvent(
            player=player_name,
            position=position,
            time=completion_time,
            hints_used=player_state.hints_used
        ))

        # Check if all players finished
        if len(self.completion_order) == len(self.players):
            await self.complete_session()

    async def complete_session(self):
        """All players finished - show final results."""
        self.completed_at = time.time()

        # Build leaderboard
        leaderboard = []
        for i, player_name in enumerate(self.completion_order):
            state = self.player_states[player_name]
            leaderboard.append(LeaderboardEntry(
                position=i + 1,
                player=player_name,
                time=state.completed_at - state.started_at,
                hints_used=state.hints_used,
                code=state.code
            ))

        await self.broadcast(SessionCompleteEvent(
            mode="race",
            leaderboard=leaderboard
        ))

    def check_completion(self) -> bool:
        """Complete when all players finish."""
        return len(self.completion_order) == len(self.players)
```

### Scoring System

```python
class RaceScore:
    """Calculate race scores accounting for time, hints, and code quality."""

    @staticmethod
    def calculate(
        completion_time: float,
        hints_used: int,
        code_quality: float  # 0.0-1.0 from static analysis
    ) -> float:
        """
        Base score starts at 1000 points.

        Time penalty:
          - Under 60s: +200 bonus
          - 60-120s: no penalty
          - 120-300s: -1 point per second over 120
          - 300s+: -5 points per second over 300

        Hint penalty:
          - -100 per hint used

        Code quality bonus:
          - +0 to +300 based on quality score
        """
        score = 1000.0

        # Time component
        if completion_time < 60:
            score += 200
        elif completion_time > 120:
            if completion_time <= 300:
                score -= (completion_time - 120)
            else:
                score -= (180 + (completion_time - 300) * 5)

        # Hint penalty
        score -= hints_used * 100

        # Code quality bonus
        score += code_quality * 300

        return max(0, score)  # Floor at 0
```

---

## TEACH Mode

**One player (human or AI) teaches concepts while others learn by watching and asking questions.**

### Visual Representation

```
┌──────────────────────────────────────────────────────────────┐
│                      TEACH SESSION                            │
│                                                               │
│  Teacher: Lief (AI, Teaching Style: Socratic)                │
│  Students: Wings, Claude-2, Claude-3                          │
│  Concept: List Comprehensions                                │
│                                                               │
│  ╭──────────────────────────────────────────────────────╮    │
│  │ Lief: "Let's build a container. First, we need       │    │
│  │        somewhere to store values. What data          │    │
│  │        structure would you use?"                      │    │
│  ╰──────────────────────────────────────────────────────╯    │
│                                                               │
│  ┌────────────────────────────────────────────────────┐      │
│  │ Student Responses:                                 │      │
│  │                                                     │      │
│  │ [Claude-2]: "A list!"          ✓                  │      │
│  │ [Wings]: "dictionary?"         ~ (could work)      │      │
│  │ [Claude-3]: Thinking...                            │      │
│  └────────────────────────────────────────────────────┘      │
│                                                               │
│  ╭──────────────────────────────────────────────────────╮    │
│  │ Lief: "Both could work! Let's start with a list     │    │
│  │        since it's simpler. Wings, can you tell me   │    │
│  │        why a dictionary might also work?"           │    │
│  ╰──────────────────────────────────────────────────────╯    │
│                                                               │
│  ╭──────────────────────────────────────────────────────╮    │
│  │ Code (Teacher writing):                             │    │
│  │                                                      │    │
│  │   container = []                                     │    │
│  │   █                                                  │    │
│  ╰──────────────────────────────────────────────────────╯    │
│                                                               │
│  [Ask Question] [Request Clarification] [Show Understanding] │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### Teaching Styles

```python
class TeachingStyle(Enum):
    """Different pedagogical approaches for AI teachers."""

    SOCRATIC = "socratic"        # Ask leading questions
    DEMONSTRATIVE = "demo"       # Show, then explain
    SCAFFOLDED = "scaffold"      # Build up complexity gradually
    DISCOVERY = "discovery"      # Let students explore, guide minimally
    COLLABORATIVE = "collab"     # Solve together as peers
```

### Implementation

```python
class TeachSession(Session):
    """Teaching session with one teacher and N students."""

    def __init__(
        self,
        teacher: Player,
        students: list[Player],
        concept: str,
        style: TeachingStyle = TeachingStyle.SOCRATIC
    ):
        super().__init__(players=[teacher] + students, challenge=concept)
        self.teacher = teacher
        self.students = students
        self.style = style

        # Track student understanding
        self.understanding: dict[str, float] = {}
        for student in students:
            self.understanding[student.name] = 0.0  # 0.0 to 1.0

        self.questions_asked: list[QuestionRecord] = []
        self.current_phase: TeachingPhase = TeachingPhase.INTRO

    async def start(self):
        """Begin teaching session."""
        self.started_at = time.time()

        # Load concept/challenge
        concept = await self.load_concept(self.challenge)

        await self.broadcast(SessionStartEvent(
            mode="teach",
            teacher=self.teacher.name,
            students=[s.name for s in self.students],
            concept=concept.name,
            style=self.style.value
        ))

        # Begin with teacher introduction
        await self.teacher_intro(concept)

    async def teacher_intro(self, concept: Concept):
        """Teacher introduces the concept."""
        self.current_phase = TeachingPhase.INTRO

        if self.style == TeachingStyle.SOCRATIC:
            # Ask opening question
            intro = f"Let's learn about {concept.name}. {concept.opening_question}"

        elif self.style == TeachingStyle.DEMONSTRATIVE:
            # Show example first
            intro = f"I'm going to show you {concept.name} in action, then explain."

        elif self.style == TeachingStyle.SCAFFOLDED:
            # Start with prerequisite review
            intro = f"Before we tackle {concept.name}, let's review {concept.prerequisites}..."

        elif self.style == TeachingStyle.DISCOVERY:
            # Minimal guidance
            intro = f"Here's a challenge involving {concept.name}. Try to solve it!"

        elif self.style == TeachingStyle.COLLABORATIVE:
            # Peer framing
            intro = f"Let's figure out {concept.name} together. I'll start..."

        await self.send_to_all(TeacherMessageEvent(
            teacher=self.teacher.name,
            content=intro,
            phase=self.current_phase
        ))

    async def handle_event(self, event: GameEvent):
        """Process teaching session events."""

        # Teacher actions
        if event.player == self.teacher.name:
            if event.type == "keystroke":
                # Teacher writing code
                await self.broadcast(event)

            elif event.type == "question":
                # Teacher asking students
                await self.pose_question(event)

            elif event.type == "explanation":
                # Teacher explaining
                await self.broadcast(event)
                await self.update_understanding_from_explanation(event)

        # Student actions
        elif event.player in [s.name for s in self.students]:
            if event.type == "answer":
                # Student answering teacher's question
                await self.process_answer(event)

            elif event.type == "question":
                # Student asking teacher
                self.questions_asked.append(QuestionRecord(
                    student=event.player,
                    question=event.content,
                    timestamp=time.time()
                ))
                await self.teacher_respond_to_question(event)

            elif event.type == "emotion":
                # Track confusion/understanding
                await self.update_understanding_from_emotion(event)

    async def pose_question(self, event: QuestionEvent):
        """Teacher asks students a question."""
        await self.broadcast(TeacherQuestionEvent(
            teacher=self.teacher.name,
            question=event.content,
            expects_responses=True
        ))

        # Wait for student responses
        self.awaiting_responses = True

    async def process_answer(self, event: AnswerEvent):
        """Evaluate student answer."""
        # Simple correctness check
        is_correct = await self.check_answer(event.content)

        # Update understanding
        if is_correct:
            self.understanding[event.player] = min(
                1.0,
                self.understanding[event.player] + 0.1
            )
        else:
            # Incorrect doesn't decrease understanding
            pass

        await self.broadcast(AnswerFeedbackEvent(
            student=event.player,
            answer=event.content,
            correct=is_correct,
            teacher_response=await self.teacher_respond(event, is_correct)
        ))

    async def teacher_respond_to_question(self, question_event: QuestionEvent):
        """Teacher responds to student question."""
        # If teacher is AI, use Claude to generate response
        if isinstance(self.teacher, ClaudePlayer):
            response = await self.teacher.answer_question(
                question=question_event.content,
                context=self.get_session_context()
            )
        else:
            # Human teacher - wait for input
            response = await self.teacher.get_response()

        await self.broadcast(TeacherResponseEvent(
            teacher=self.teacher.name,
            student=question_event.player,
            question=question_event.content,
            response=response
        ))

    def check_completion(self) -> bool:
        """Session complete when all students understand."""
        avg_understanding = sum(self.understanding.values()) / len(self.understanding)
        return avg_understanding >= 0.8  # 80% understanding threshold
```

### Understanding Metrics

```python
class UnderstandingTracker:
    """Track student understanding through multiple signals."""

    def __init__(self):
        self.scores: dict[str, float] = {}

    def update_from_answer(self, student: str, correct: bool):
        """Adjust understanding based on answer correctness."""
        if student not in self.scores:
            self.scores[student] = 0.5  # Start at 50%

        if correct:
            # Correct answer increases understanding
            self.scores[student] = min(1.0, self.scores[student] + 0.15)
        else:
            # Incorrect answer suggests misconception
            self.scores[student] = max(0.0, self.scores[student] - 0.05)

    def update_from_emotion(self, student: str, emotion: EmotionalDimension, value: float):
        """Infer understanding from emotional state."""
        if emotion == EmotionalDimension.FRUSTRATION and value > 0.7:
            # High frustration suggests confusion
            self.scores[student] = max(0.0, self.scores[student] - 0.1)

        elif emotion == EmotionalDimension.ENJOYMENT and value > 0.7:
            # High enjoyment suggests understanding and engagement
            self.scores[student] = min(1.0, self.scores[student] + 0.05)

    def update_from_question(self, student: str, question_quality: float):
        """Good questions indicate engagement and partial understanding."""
        # Quality scored 0.0-1.0 by AI
        self.scores[student] = min(
            1.0,
            self.scores[student] + question_quality * 0.1
        )

    def get_understanding(self, student: str) -> float:
        """Get current understanding score."""
        return self.scores.get(student, 0.5)
```

---

## SWARM Mode

**Multiple AI players tackle the same challenge with different approaches, then compare and analyze.**

### Visual Representation

```
┌──────────────────────────────────────────────────────────────┐
│                      SWARM SESSION                            │
│                 "Find the best solution"                      │
│                                                               │
│  Challenge: Median Finder                                    │
│  AIs: 4 (Different Approaches)                               │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ Claude-1 (brute_force):                              │    │
│  │   ✓ Complete - 45 lines, 12ms, all tests passing    │    │
│  │                                                       │    │
│  │ Claude-2 (elegant):                                  │    │
│  │   ✓ Complete - 23 lines, 8ms, all tests passing     │    │
│  │                                                       │    │
│  │ Claude-3 (fast):                                     │    │
│  │   ✓ Complete - 31 lines, 3ms, all tests passing     │    │
│  │                                                       │    │
│  │ Claude-4 (readable):                                 │    │
│  │   ✓ Complete - 52 lines, 15ms, all tests passing    │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                               │
│  ╭──────────────────────────────────────────────────────╮    │
│  │ Analysis:                                            │    │
│  │                                                       │    │
│  │ - Claude-3's solution is FASTEST (optimized for      │    │
│  │   speed, uses heapq for O(n log k) complexity)       │    │
│  │                                                       │    │
│  │ - Claude-2's solution is most ELEGANT (list          │    │
│  │   comprehension + sorted, Pythonic)                  │    │
│  │                                                       │    │
│  │ - Claude-4's solution is most READABLE (verbose      │    │
│  │   but clear comments, great for learning)            │    │
│  │                                                       │    │
│  │ - Claude-1's solution is COMPREHENSIVE (handles      │    │
│  │   edge cases explicitly)                             │    │
│  ╰──────────────────────────────────────────────────────╯    │
│                                                               │
│  [View All Code] [Compare Side-by-Side] [Learn From Best]   │
│  [Create Hybrid] [Export Analysis]                           │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### Approach Specifications

```python
class ApproachHint(Enum):
    """Different strategic approaches for swarm mode."""

    BRUTE_FORCE = "brute_force"      # Simplest, most explicit
    ELEGANT = "elegant"              # Pythonic, concise
    FAST = "fast"                    # Performance optimized
    READABLE = "readable"            # Comments, clarity
    DEFENSIVE = "defensive"          # Error handling, edge cases
    CREATIVE = "creative"            # Unusual algorithms
    STANDARD = "standard"            # Textbook implementation
    HACKER = "hacker"                # One-liners, tricks
```

### Implementation

```python
class SwarmSession(Session):
    """Multiple AIs solve same challenge with different approaches."""

    def __init__(
        self,
        players: list[ClaudePlayer],
        challenge: str,
        approach_hints: list[ApproachHint] | None = None
    ):
        super().__init__(players, challenge)

        # Assign approaches
        if approach_hints:
            assert len(approach_hints) == len(players)
            for player, hint in zip(players, approach_hints):
                player.approach_hint = hint
        else:
            # Distribute standard approaches
            hints = [
                ApproachHint.ELEGANT,
                ApproachHint.FAST,
                ApproachHint.READABLE,
                ApproachHint.DEFENSIVE
            ]
            for i, player in enumerate(players):
                player.approach_hint = hints[i % len(hints)]

        # Track completion
        self.solutions: dict[str, SwarmSolution] = {}
        self.analysis: SwarmAnalysis | None = None

    async def start(self):
        """Begin swarm session - all AIs start simultaneously."""
        self.started_at = time.time()

        challenge = await self.load_challenge()

        # Brief each AI on their approach
        for player in self.players:
            await self.send_to_player(player.name, SwarmBriefingEvent(
                challenge=challenge.name,
                approach=player.approach_hint,
                instructions=self.get_approach_instructions(player.approach_hint)
            ))

        # Start all simultaneously
        await self.broadcast(SessionStartEvent(
            mode="swarm",
            players=[p.name for p in self.players],
            approaches={p.name: p.approach_hint.value for p in self.players},
            challenge=challenge.name
        ))

        # Each AI works independently
        tasks = [self.run_ai_player(player) for player in self.players]
        await asyncio.gather(*tasks)

        # Analyze results
        await self.analyze_solutions()

    async def run_ai_player(self, player: ClaudePlayer):
        """Run single AI player to completion."""
        start_time = time.time()

        try:
            # AI solves independently
            solution = await player.solve_challenge(
                challenge=self.challenge,
                approach=player.approach_hint
            )

            completion_time = time.time() - start_time

            # Test solution
            results = await self.run_tests(solution.code)

            # Record solution
            self.solutions[player.name] = SwarmSolution(
                player=player.name,
                approach=player.approach_hint,
                code=solution.code,
                tests_passed=results.passed,
                tests_total=results.total,
                execution_time_ms=results.execution_time_ms,
                completion_time=completion_time,
                line_count=len(solution.code.split('\n')),
                reasoning=solution.reasoning
            )

            # Broadcast completion
            await self.broadcast(PlayerCompletedEvent(
                player=player.name,
                approach=player.approach_hint.value,
                time=completion_time
            ))

        except Exception as e:
            # AI failed
            await self.broadcast(PlayerFailedEvent(
                player=player.name,
                error=str(e)
            ))

    async def analyze_solutions(self):
        """Compare all solutions and generate insights."""
        # Wait for all to complete or timeout
        await self.wait_for_all(timeout=300)

        # Analyze via Claude
        analysis_prompt = self.build_analysis_prompt()
        analysis_result = await claude_analyze(analysis_prompt)

        self.analysis = SwarmAnalysis(
            fastest=self.find_fastest(),
            most_elegant=self.find_most_elegant(),
            most_readable=self.find_most_readable(),
            best_practices=analysis_result.best_practices,
            trade_offs=analysis_result.trade_offs,
            learning_points=analysis_result.learning_points,
            hybrid_recommendation=analysis_result.hybrid
        )

        await self.broadcast(AnalysisCompleteEvent(
            analysis=self.analysis
        ))

        await self.complete_session()

    def build_analysis_prompt(self) -> str:
        """Build prompt for Claude to analyze all solutions."""
        solutions_text = ""
        for name, sol in self.solutions.items():
            solutions_text += f"\n## {name} ({sol.approach.value})\n"
            solutions_text += f"Time: {sol.execution_time_ms}ms\n"
            solutions_text += f"Lines: {sol.line_count}\n"
            solutions_text += f"Tests: {sol.tests_passed}/{sol.tests_total}\n"
            solutions_text += f"```python\n{sol.code}\n```\n"
            solutions_text += f"Reasoning: {sol.reasoning}\n"

        return f"""
Analyze these different solutions to the same challenge:

{solutions_text}

Provide:
1. Which solution is objectively FASTEST (lowest execution time)
2. Which is most ELEGANT (Pythonic, concise, idiomatic)
3. Which is most READABLE (clear, well-commented)
4. Trade-offs between approaches
5. What each solution teaches
6. Suggestions for a hybrid that combines the best aspects
"""

    def find_fastest(self) -> str:
        """Find solution with lowest execution time."""
        return min(
            self.solutions.items(),
            key=lambda x: x[1].execution_time_ms
        )[0]

    def find_most_elegant(self) -> str:
        """Find solution with best elegance score."""
        # Score = low LOC + all tests pass + good style
        def elegance_score(sol: SwarmSolution) -> float:
            score = 0.0

            # Fewer lines is better (up to a point)
            if sol.line_count < 20:
                score += (20 - sol.line_count) * 5

            # All tests passing is critical
            if sol.tests_passed == sol.tests_total:
                score += 100

            # Penalize excessive length
            if sol.line_count > 50:
                score -= (sol.line_count - 50) * 2

            return score

        return max(
            self.solutions.items(),
            key=lambda x: elegance_score(x[1])
        )[0]

    def find_most_readable(self) -> str:
        """Find solution optimized for readability."""
        # Typically the one explicitly marked as "readable" approach
        for name, sol in self.solutions.items():
            if sol.approach == ApproachHint.READABLE:
                return name

        # Fallback: most comments
        def comment_count(code: str) -> int:
            return len([line for line in code.split('\n') if line.strip().startswith('#')])

        return max(
            self.solutions.items(),
            key=lambda x: comment_count(x[1].code)
        )[0]

    def check_completion(self) -> bool:
        """Complete when analysis is done."""
        return self.analysis is not None
```

### Swarm Analysis Output

```python
@dataclass
class SwarmAnalysis:
    """Results of comparing swarm solutions."""

    fastest: str  # Player name
    most_elegant: str
    most_readable: str

    best_practices: list[str]  # What all good solutions did
    trade_offs: dict[str, str]  # Approach -> trade-off description
    learning_points: list[str]  # Key takeaways

    hybrid_recommendation: str  # Suggested combined approach

    def to_markdown(self) -> str:
        """Format as readable markdown."""
        md = "# Swarm Analysis\n\n"

        md += "## Winners by Category\n\n"
        md += f"- **Fastest**: {self.fastest}\n"
        md += f"- **Most Elegant**: {self.most_elegant}\n"
        md += f"- **Most Readable**: {self.most_readable}\n\n"

        md += "## Best Practices\n\n"
        for practice in self.best_practices:
            md += f"- {practice}\n"
        md += "\n"

        md += "## Trade-offs\n\n"
        for approach, tradeoff in self.trade_offs.items():
            md += f"### {approach}\n{tradeoff}\n\n"

        md += "## Learning Points\n\n"
        for i, point in enumerate(self.learning_points, 1):
            md += f"{i}. {point}\n"
        md += "\n"

        md += "## Hybrid Recommendation\n\n"
        md += self.hybrid_recommendation

        return md
```

---

## SPECTATOR Mode

**Watch an AI solve challenges with real-time commentary and explanations.**

### Visual Representation

```
┌──────────────────────────────────────────────────────────────┐
│                    SPECTATOR SESSION                          │
│                                                               │
│  Watching: Lief (AI)                                         │
│  Challenge: Pyramid Builder                                  │
│  Spectators: Wings, Claude-Teacher                           │
│                                                               │
│  ╭──────────────────────────────────────────────────────╮    │
│  │ Code (Lief writing):                                 │    │
│  │                                                       │    │
│  │   def pyramid(height):                               │    │
│  │       for i in range(height):                        │    │
│  │           spaces = " " * (height - i - 1)            │    │
│  │           stars = "*" * (2 * i + 1)█                 │    │
│  │                                                       │    │
│  ╰──────────────────────────────────────────────────────╯    │
│                                                               │
│  ╭──────────────────────────────────────────────────────╮    │
│  │ Lief (thinking aloud):                               │    │
│  │ "I need to center each line. The number of spaces   │    │
│  │  before the stars decreases by 1 each row. The      │    │
│  │  number of stars follows the pattern 2i+1..."       │    │
│  ╰──────────────────────────────────────────────────────╯    │
│                                                               │
│  ┌────────────────────────────────────────────────────┐      │
│  │ Spectator Feed:                                    │      │
│  │                                                     │      │
│  │ [Wings]: "Why 2*i+1 for stars?"                   │      │
│  │ [Claude-Teacher]: "Good question! Let's see..."   │      │
│  │ [Lief]: "For row i: i=0 → 1 star, i=1 → 3 stars,  │      │
│  │          i=2 → 5 stars. Pattern is 2i+1!"         │      │
│  └────────────────────────────────────────────────────┘      │
│                                                               │
│  Speed: [0.5x] [1x] [2x] [Skip Ahead]                       │
│  [Ask Question] [Request Pause] [Replay Section]             │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### Implementation

```python
class SpectatorSession(Session):
    """Watch AI solve with commentary."""

    def __init__(
        self,
        player: ClaudePlayer,
        spectators: list[Player],
        challenge: str,
        commentary_level: str = "detailed"
    ):
        super().__init__(players=[player] + spectators, challenge=challenge)
        self.player = player
        self.spectators = spectators
        self.commentary_level = commentary_level

        self.playback_speed: float = 1.0
        self.paused: bool = False
        self.pause_requests: list[str] = []

    async def start(self):
        """Begin spectator session."""
        self.started_at = time.time()

        challenge = await self.load_challenge()

        await self.broadcast(SessionStartEvent(
            mode="spectator",
            player=self.player.name,
            spectators=[s.name for s in self.spectators],
            challenge=challenge.name
        ))

        # Run AI with commentary
        await self.run_with_commentary()

    async def run_with_commentary(self):
        """Execute AI solve with narration."""
        # Configure AI for verbose output
        self.player.commentary_mode = True
        self.player.commentary_level = self.commentary_level

        # Start solving
        async for event in self.player.solve_with_stream(self.challenge):
            # Check for pause requests
            if self.paused:
                await self.handle_pause()

            # Apply playback speed
            if hasattr(event, 'delay'):
                await asyncio.sleep(event.delay / self.playback_speed)

            # Broadcast event
            await self.broadcast(event)

            # Handle spectator interactions
            await self.check_spectator_actions()

    async def handle_event(self, event: GameEvent):
        """Process spectator interactions."""

        # Only spectators can control playback
        if event.player not in [s.name for s in self.spectators]:
            return

        if event.type == "pause_request":
            self.pause_requests.append(event.player)
            self.paused = True

            await self.broadcast(PausedEvent(
                requested_by=event.player
            ))

        elif event.type == "resume":
            self.paused = False
            self.pause_requests.clear()

            await self.broadcast(ResumedEvent())

        elif event.type == "speed_change":
            self.playback_speed = event.speed

            await self.broadcast(SpeedChangedEvent(
                speed=self.playback_speed
            ))

        elif event.type == "question":
            # Spectator asks player a question
            await self.player_answer_question(event)

    async def player_answer_question(self, question_event: QuestionEvent):
        """AI pauses and answers spectator question."""
        # Pause automatically
        self.paused = True

        # AI answers
        response = await self.player.answer_question(
            question=question_event.content,
            context=self.get_current_context()
        )

        await self.broadcast(PlayerResponseEvent(
            player=self.player.name,
            question=question_event.content,
            response=response,
            asker=question_event.player
        ))

        # Resume after answer
        await asyncio.sleep(2.0)
        self.paused = False

    def check_completion(self) -> bool:
        """Complete when AI finishes."""
        return hasattr(self, '_ai_completed') and self._ai_completed
```

### Commentary Levels

```python
class CommentaryLevel(Enum):
    """How verbose the AI commentary should be."""

    SILENT = "silent"          # No commentary, just watch
    MINIMAL = "minimal"        # Key decisions only
    MODERATE = "moderate"      # Explain main steps
    DETAILED = "detailed"      # Think aloud continuously
    TUTORIAL = "tutorial"      # Explain every line for beginners
```

---

## Session Lifecycle

All sessions follow a standard lifecycle:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SESSION LIFECYCLE                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. INITIALIZATION                                                           │
│     ├─ Create session object                                                │
│     ├─ Register players                                                     │
│     ├─ Load challenge/concept                                               │
│     └─ Initialize shared state                                              │
│                                                                              │
│  2. BRIEFING                                                                 │
│     ├─ Announce session to all players                                      │
│     ├─ Explain mode rules                                                   │
│     ├─ Show challenge/goal                                                  │
│     └─ Countdown (for RACE) or opening prompt (others)                      │
│                                                                              │
│  3. ACTIVE                                                                   │
│     ├─ Players interact according to mode                                   │
│     ├─ Events flow through event bus                                        │
│     ├─ State updates broadcast                                              │
│     └─ Track progress toward completion                                     │
│                                                                              │
│  4. COMPLETION                                                               │
│     ├─ Completion condition met                                             │
│     ├─ Broadcast completion event                                           │
│     ├─ Calculate results/scores                                             │
│     └─ Trigger celebration/analysis                                         │
│                                                                              │
│  5. DEBRIEF                                                                  │
│     ├─ Show results/leaderboard                                             │
│     ├─ Collect emotional feedback                                           │
│     ├─ Update learner profiles                                              │
│     └─ Offer next steps                                                     │
│                                                                              │
│  6. TEARDOWN                                                                 │
│     ├─ Save recording (TAS)                                                 │
│     ├─ Disconnect players                                                   │
│     ├─ Clean up resources                                                   │
│     └─ Return to lobby                                                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### State Machine

```python
class SessionState(Enum):
    """Session lifecycle states."""

    INIT = "initializing"
    BRIEFING = "briefing"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETING = "completing"
    DEBRIEF = "debrief"
    TEARDOWN = "teardown"
    FINISHED = "finished"

class SessionStateMachine:
    """Manages session lifecycle transitions."""

    TRANSITIONS = {
        SessionState.INIT: [SessionState.BRIEFING],
        SessionState.BRIEFING: [SessionState.ACTIVE],
        SessionState.ACTIVE: [SessionState.PAUSED, SessionState.COMPLETING],
        SessionState.PAUSED: [SessionState.ACTIVE, SessionState.TEARDOWN],
        SessionState.COMPLETING: [SessionState.DEBRIEF],
        SessionState.DEBRIEF: [SessionState.TEARDOWN],
        SessionState.TEARDOWN: [SessionState.FINISHED],
        SessionState.FINISHED: []
    }

    def __init__(self, session: Session):
        self.session = session
        self.state = SessionState.INIT

    async def transition(self, new_state: SessionState):
        """Validate and execute state transition."""
        if new_state not in self.TRANSITIONS[self.state]:
            raise ValueError(
                f"Invalid transition: {self.state} -> {new_state}"
            )

        old_state = self.state
        self.state = new_state

        # Execute state entry logic
        await self.on_enter_state(new_state)

        # Broadcast state change
        await self.session.broadcast(StateChangeEvent(
            old_state=old_state.value,
            new_state=new_state.value
        ))

    async def on_enter_state(self, state: SessionState):
        """Execute logic when entering a state."""
        if state == SessionState.BRIEFING:
            await self.session.send_briefing()

        elif state == SessionState.ACTIVE:
            await self.session.activate()

        elif state == SessionState.COMPLETING:
            await self.session.calculate_results()

        elif state == SessionState.DEBRIEF:
            await self.session.show_results()

        elif state == SessionState.TEARDOWN:
            await self.session.cleanup()
```

---

## Mode Switching

Sessions can dynamically switch modes during gameplay:

```python
class SessionManager:
    """Manages sessions and mode transitions."""

    def __init__(self):
        self.current_session: Session | None = None

    async def switch_mode(
        self,
        new_mode: str,
        preserve_state: bool = True
    ):
        """Switch from one mode to another."""

        if not self.current_session:
            raise ValueError("No active session")

        # Save current state
        if preserve_state:
            saved_state = self.current_session.export_state()

        # Pause current session
        await self.current_session.pause()

        # Create new session of different type
        if new_mode == "coop":
            new_session = CoopSession(
                players=self.current_session.players,
                challenge=self.current_session.challenge
            )
        elif new_mode == "race":
            new_session = RaceSession(
                players=self.current_session.players,
                challenge=self.current_session.challenge
            )
        # ... etc

        # Restore state if preserving
        if preserve_state:
            new_session.import_state(saved_state)

        # Switch sessions
        old_session = self.current_session
        self.current_session = new_session

        # Teardown old
        await old_session.teardown()

        # Start new
        await new_session.start()

        return new_session
```

### Example: COOP to RACE

```
Scenario: Two players are cooperating, both want to race
┌──────────────────────────────────────────────────────────────┐
│ COOP Session (Active):                                       │
│   Code: 80% complete                                         │
│   Players: Wings, Lief                                       │
│                                                               │
│ Wings: "Want to race from here?"                             │
│ Lief: "Let's do it!"                                         │
│                                                               │
│ [System]: Switching to RACE mode...                          │
│                                                               │
│ RACE Session (Starting):                                     │
│   Cloning code to each player's workspace                    │
│   Starting from current state (80% complete)                 │
│   First to finish the remaining 20% wins!                    │
│                                                               │
│ [3... 2... 1... GO!]                                         │
└──────────────────────────────────────────────────────────────┘
```

---

## State Synchronization

How sessions keep all players in sync:

```python
class StateSynchronizer:
    """Synchronizes state across all players in a session."""

    def __init__(self, session: Session):
        self.session = session
        self.sync_interval = 1.0  # seconds
        self.last_sync = time.time()

    async def sync_loop(self):
        """Continuously sync state."""
        while self.session.is_active():
            await asyncio.sleep(self.sync_interval)
            await self.sync_now()

    async def sync_now(self):
        """Perform synchronization."""
        state_snapshot = self.session.get_state_snapshot()

        # Broadcast to all players
        await self.session.broadcast(StateSyncEvent(
            snapshot=state_snapshot,
            timestamp=time.time()
        ))

        self.last_sync = time.time()

    def get_state_snapshot(self) -> dict:
        """Capture current session state."""
        return {
            "code": self.session.get_current_code(),
            "tests_status": self.session.get_test_status(),
            "player_positions": {
                p.name: self.session.get_player_position(p)
                for p in self.session.players
            },
            "elapsed_time": time.time() - self.session.started_at,
            "mode_specific": self.session.get_mode_specific_state()
        }
```

### Conflict Resolution

```python
class ConflictResolver:
    """Resolve conflicts when multiple players edit simultaneously."""

    def resolve_edit_conflict(
        self,
        edit_a: Edit,
        edit_b: Edit
    ) -> Edit:
        """Determine which edit wins."""

        # If edits don't overlap, both can apply
        if not self.edits_overlap(edit_a, edit_b):
            return MergedEdit([edit_a, edit_b])

        # Overlapping edits - use timestamp
        if edit_a.timestamp < edit_b.timestamp:
            return edit_a
        else:
            return edit_b

    def edits_overlap(self, edit_a: Edit, edit_b: Edit) -> bool:
        """Check if two edits affect same code region."""
        return (
            edit_a.line == edit_b.line and
            self.ranges_overlap(
                (edit_a.col_start, edit_a.col_end),
                (edit_b.col_start, edit_b.col_end)
            )
        )
```

---

## Summary

LMSP supports five powerful multiplayer modes:

1. **COOP** - Learn together, shared cursor, turn-based
2. **RACE** - Competitive learning, split-screen
3. **TEACH** - Expert demonstration with Q&A
4. **SWARM** - AI strategy comparison
5. **SPECTATOR** - Watch and learn with commentary

Each mode serves different learning objectives and can be switched dynamically during play.

---

*Multiplayer learning: Play together. Learn together. Build together.*
