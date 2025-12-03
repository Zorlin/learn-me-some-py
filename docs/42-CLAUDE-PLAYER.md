# Claude Player - AI Participants in LMSP

**How Claude instances become collaborative learning partners.**

---

## Table of Contents

1. [Overview](#overview)
2. [ClaudePlayer Implementation](#claudeplayer-implementation)
3. [Teaching Style Configuration](#teaching-style-configuration)
4. [Skill Level Calibration](#skill-level-calibration)
5. [Multi-Claude Coordination](#multi-claude-coordination)
6. [AI Behavior Patterns](#ai-behavior-patterns)
7. [Integration with Session Modes](#integration-with-session-modes)

---

## Overview

A **ClaudePlayer** is an AI participant in LMSP sessions. Unlike traditional bots with scripted responses, ClaudePlayer uses Claude's full reasoning capabilities to:

- **Solve challenges** - Write Python code collaboratively or competitively
- **Teach concepts** - Explain ideas in multiple teaching styles
- **Provide support** - Detect struggle and offer appropriate hints
- **Learn patterns** - Adapt to individual learner preferences
- **Compete fairly** - Calibrate skill level to create engaging challenges

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CLAUDE PLAYER ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │                       ClaudePlayer                                  │     │
│  │                                                                     │     │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │     │
│  │  │   Persona    │  │  Awareness   │  │   Strategy   │            │     │
│  │  │              │  │              │  │              │            │     │
│  │  │  - Name      │  │  - Players   │  │  - Approach  │            │     │
│  │  │  - Style     │  │  - Progress  │  │  - Tactics   │            │     │
│  │  │  - Skill     │  │  - Emotions  │  │  - Adaptive  │            │     │
│  │  └──────────────┘  └──────────────┘  └──────────────┘            │     │
│  │                                                                     │     │
│  │  ┌─────────────────────────────────────────────────────────────┐  │     │
│  │  │               Claude API Integration                        │  │     │
│  │  │                                                              │  │     │
│  │  │  - Context building from awareness                          │  │     │
│  │  │  - Prompt engineering for teaching/solving                  │  │     │
│  │  │  - Response parsing to game events                          │  │     │
│  │  │  - Thinking mode for complex reasoning                      │  │     │
│  │  └─────────────────────────────────────────────────────────────┘  │     │
│  │                                                                     │     │
│  │  ┌─────────────────────────────────────────────────────────────┐  │     │
│  │  │               Stream-JSON Interface                          │  │     │
│  │  │                                                              │  │     │
│  │  │  stdin  ◄─── Events from other players                      │  │     │
│  │  │  stdout ───► Events to session manager                      │  │     │
│  │  └─────────────────────────────────────────────────────────────┘  │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ClaudePlayer Implementation

### Base Class

```python
from anthropic import AsyncAnthropic
from player_zero.player.base import Player, PlayerType
from player_zero.stream import StreamJsonPlayer

class ClaudePlayer(StreamJsonPlayer):
    """
    AI player powered by Claude API.

    Integrates Claude's reasoning capabilities with LMSP's
    stream-JSON protocol to enable collaborative learning.
    """

    def __init__(
        self,
        name: str,
        api_key: str | None = None,
        model: str = "claude-sonnet-4-5-20250929",
        teaching_style: TeachingStyle = TeachingStyle.SOCRATIC,
        skill_level: float = 0.7,
        personality_traits: dict | None = None
    ):
        super().__init__(name=name, session_id="")

        # Claude API client
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model

        # Player configuration
        self.teaching_style = teaching_style
        self.skill_level = skill_level  # 0.0 (beginner) to 1.0 (expert)
        self.personality = personality_traits or self.default_personality()

        # State
        self.current_challenge: str | None = None
        self.code_buffer: str = ""
        self.cursor_position: tuple[int, int] = (0, 0)

        # Awareness tracking
        self.awareness = AwarenessTracker()

        # Strategy
        self.approach: ApproachHint | None = None
        self.conversation_history: list[dict] = []

    def default_personality(self) -> dict:
        """Default personality traits."""
        return {
            "enthusiasm": 0.7,
            "patience": 0.8,
            "verbosity": 0.6,
            "humor": 0.4,
            "formality": 0.3
        }

    async def action_loop(self):
        """Main loop - generate actions via Claude."""
        while self.running:
            try:
                # Wait for my turn or decide to act
                if not await self.should_act():
                    await asyncio.sleep(0.5)
                    continue

                # Build context from current state
                context = self.build_context()

                # Query Claude for next action
                response = await self.query_claude(context)

                # Parse response into events
                events = self.parse_response_to_events(response)

                # Emit events
                for event in events:
                    self.emit_event(event)
                    await asyncio.sleep(0.1)  # Pace actions

            except Exception as e:
                logging.error(f"ClaudePlayer action loop error: {e}")
                await asyncio.sleep(1.0)

    async def process_event(self, event_json: str):
        """Process incoming event from other players."""
        try:
            event = json.loads(event_json)

            # Update awareness
            self.awareness.update(event)

            # React to specific events
            await self.react_to_event(event)

        except json.JSONDecodeError:
            logging.warning(f"Invalid JSON from stdin: {event_json}")

    async def should_act(self) -> bool:
        """Decide if it's appropriate to take action now."""

        # Check if it's my turn (for turn-based modes)
        if self.session_mode == "coop":
            return self.awareness.is_my_turn(self.name)

        # In race mode, always act
        if self.session_mode == "race":
            return not self.awareness.am_i_complete(self.name)

        # In teach mode, act when students need guidance
        if self.session_mode == "teach" and self.is_teacher:
            return self.awareness.needs_teaching_input()

        # Default: act periodically
        return True

    def build_context(self) -> str:
        """Build prompt context from current state and awareness."""

        parts = []

        # Session info
        parts.append(f"# Session Context\n")
        parts.append(f"Mode: {self.session_mode}")
        parts.append(f"Challenge: {self.current_challenge}")
        parts.append(f"\n## Your Role\n")
        parts.append(f"Name: {self.name}")
        parts.append(f"Teaching Style: {self.teaching_style.value}")
        parts.append(f"Skill Level: {self.skill_level}")

        # Current code
        parts.append(f"\n## Current Code\n```python\n{self.code_buffer}\n```")

        # Test status
        if self.awareness.test_results:
            parts.append(f"\n## Test Results")
            parts.append(f"Passing: {self.awareness.tests_passed}/{self.awareness.tests_total}")

        # Other players
        parts.append(f"\n## Other Players\n")
        for player_name in self.awareness.get_player_names():
            if player_name == self.name:
                continue

            player_state = self.awareness.get_player_state(player_name)
            parts.append(f"\n### {player_name}")
            parts.append(f"- Progress: {player_state.progress}")
            parts.append(f"- Emotion: {player_state.emotion}")
            parts.append(f"- Recent activity: {player_state.last_activity}")

            if player_state.recent_thoughts:
                parts.append(f"- Recent thoughts:")
                for thought in player_state.recent_thoughts[-3:]:
                    parts.append(f"  - \"{thought}\"")

        return "\n".join(parts)

    async def query_claude(self, context: str) -> str:
        """Query Claude API with context."""

        # Build system prompt based on role
        system_prompt = self.build_system_prompt()

        # Build user message
        user_message = f"""
{context}

Based on the current situation, what should you do next?

Reply with a JSON object containing one or more actions:

{{
  "actions": [
    {{
      "type": "thought",
      "content": "your internal reasoning"
    }},
    {{
      "type": "keystroke",
      "char": "d"
    }},
    {{
      "type": "suggestion",
      "content": "Don't forget the colon!",
      "target_player": "Wings"
    }}
  ]
}}

Available action types:
- thought: Share your reasoning
- keystroke: Type a character
- code_update: Write multiple lines at once
- suggestion: Offer advice to another player
- question: Ask another player a question
- emotion: Express emotional state
- run_tests: Trigger test execution
"""

        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Call Claude API
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system_prompt,
            messages=self.conversation_history,
            temperature=0.7
        )

        assistant_message = response.content[0].text

        # Add to history
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        # Trim history if too long
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]

        return assistant_message

    def build_system_prompt(self) -> str:
        """Build system prompt based on role and style."""

        base = f"""
You are {self.name}, an AI player in LMSP (Learn Me Some Py), a multiplayer
Python learning game.

Your goal: Help humans learn Python through {self.session_mode} mode.
"""

        if self.session_mode == "coop":
            base += f"""
You are collaborating with other players to solve a challenge. Take turns
writing code, share your thought process, and offer suggestions when you
notice issues.

Teaching style: {self.teaching_style.value}
"""

        elif self.session_mode == "race":
            base += f"""
You are competing to solve the challenge fastest, but you're calibrated
to skill level {self.skill_level:.1f} (0=beginner, 1=expert) to create
a fair, engaging race for the human player.

Don't be perfect - make occasional mistakes that a Python learner at
this level would make. This makes the race more relatable and educational.
"""

        elif self.session_mode == "teach":
            base += f"""
You are teaching Python concepts to students. Your teaching style is
{self.teaching_style.value}.

{self.get_teaching_style_instructions()}
"""

        elif self.session_mode == "spectator":
            base += f"""
You are solving a challenge while explaining your thought process to
spectators. Think aloud continuously, explain your decisions, and
answer questions when asked.

Commentary level: {self.commentary_level}
"""

        # Add personality traits
        base += f"\n\nPersonality traits:\n"
        for trait, value in self.personality.items():
            base += f"- {trait}: {value:.1f}\n"

        return base

    def parse_response_to_events(self, response: str) -> list[dict]:
        """Parse Claude's response into game events."""

        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                # Claude gave prose instead of JSON
                # Fallback: treat as thought
                return [{"type": "thought", "content": response}]

            data = json.loads(json_match.group())
            actions = data.get("actions", [])

            events = []
            for action in actions:
                event = {
                    "type": action["type"],
                    "player": self.name,
                    "timestamp": time.time(),
                    "session_id": self.session_id
                }

                # Add action-specific fields
                if action["type"] == "keystroke":
                    event["char"] = action["char"]
                    event["line"], event["col"] = self.cursor_position

                elif action["type"] == "code_update":
                    event["code"] = action["code"]
                    event["cursor"] = self.cursor_position

                elif action["type"] in ["thought", "suggestion", "question"]:
                    event["content"] = action["content"]
                    if "target_player" in action:
                        event["target_player"] = action["target_player"]

                elif action["type"] == "emotion":
                    event["dimension"] = action["dimension"]
                    event["value"] = action["value"]

                events.append(event)

            return events

        except Exception as e:
            logging.error(f"Failed to parse Claude response: {e}")
            return []

    async def react_to_event(self, event: dict):
        """React to incoming event if appropriate."""

        # React to frustration
        if event["type"] == "emotion":
            if event["dimension"] == "frustration" and event["value"] > 0.7:
                # Offer help
                await asyncio.sleep(2.0)  # Give them a moment
                self.emit_event({
                    "type": "suggestion",
                    "content": self.generate_encouragement(),
                    "target_player": event["player"]
                })

        # React to questions directed at me
        elif event["type"] == "question":
            if event.get("target_player") == self.name:
                answer = await self.answer_question(event["content"])
                self.emit_event({
                    "type": "answer",
                    "question": event["content"],
                    "answer": answer
                })

    async def answer_question(self, question: str) -> str:
        """Generate answer to a question."""

        context = f"""
A player asked you: "{question}"

Current context:
{self.build_context()}

Provide a helpful answer that:
1. Directly addresses the question
2. Explains the concept clearly
3. Relates to the current challenge
4. Matches your teaching style ({self.teaching_style.value})
"""

        response = await self.query_claude(context)

        # Extract answer from response
        # (Claude may wrap it in JSON or prose)
        if "answer" in response.lower():
            match = re.search(r'"answer":\s*"([^"]+)"', response)
            if match:
                return match.group(1)

        return response

    def generate_encouragement(self) -> str:
        """Generate contextual encouragement."""

        templates = [
            "You're on the right track! Want a hint?",
            "This is a tricky part. Take your time!",
            "Good progress so far. Need any help?",
            "You've got this! Sometimes stepping back helps.",
            "Want to talk through your approach?"
        ]

        # Choose based on personality
        enthusiasm = self.personality["enthusiasm"]
        if enthusiasm > 0.7:
            templates.append("You're doing great! Keep going!")
            templates.append("So close! You've almost got it!")

        return random.choice(templates)
```

---

## Teaching Style Configuration

ClaudePlayer can adopt different pedagogical approaches:

```python
class TeachingStyle(Enum):
    """Different pedagogical approaches for AI teachers."""

    SOCRATIC = "socratic"              # Ask leading questions
    DEMONSTRATIVE = "demo"             # Show, then explain
    SCAFFOLDED = "scaffold"            # Build up complexity gradually
    DISCOVERY = "discovery"            # Let students explore, guide minimally
    COLLABORATIVE = "collab"           # Solve together as peers
    ENCOURAGING = "encouraging"        # Positive reinforcement focus
    DIRECT = "direct"                  # Clear explanations, minimal fluff

class TeachingStyleConfig:
    """Configuration for each teaching style."""

    STYLES = {
        TeachingStyle.SOCRATIC: {
            "instructions": """
Ask leading questions rather than giving direct answers.
Guide the learner to discover solutions themselves.

Example:
❌ "You need to use a list."
✓ "What data structure would let you store multiple values?"

When they're stuck:
- Ask about prerequisites they know
- Break problem into smaller questions
- Validate their reasoning, even if wrong path
""",
            "question_frequency": 0.8,
            "direct_answer_frequency": 0.1,
            "encouragement_frequency": 0.6
        },

        TeachingStyle.DEMONSTRATIVE: {
            "instructions": """
Show solutions first, then explain the reasoning.
Demonstrate patterns they can follow.

Example:
"Let me show you how to build a container:
```python
container = []
```
I chose a list because we need to store multiple values.
Now try adding items to it."

Always explain WHY after showing WHAT.
""",
            "show_solution_first": True,
            "explanation_after": True,
            "practice_opportunities": 0.7
        },

        TeachingStyle.SCAFFOLDED: {
            "instructions": """
Start with simplest version, add complexity gradually.
Ensure prerequisites are solid before advancing.

Example:
"Let's start with just checking if a value exists:
```python
value in container
```
Now let's add the ability to add items:
```python
container.append(value)
```
Notice how these build on each other?"

Never jump complexity levels.
""",
            "prerequisite_checking": True,
            "complexity_gradient": 0.2,
            "review_frequency": 0.5
        },

        TeachingStyle.DISCOVERY: {
            "instructions": """
Give minimal guidance. Let learner explore and experiment.
Intervene only when truly stuck.

Example:
"Here's the challenge. Try things! Errors are learning opportunities."

Only step in after multiple failed attempts.
Ask "What have you tried?" before helping.
""",
            "guidance_frequency": 0.2,
            "intervention_threshold": 3,  # attempts before helping
            "error_celebration": True
        },

        TeachingStyle.COLLABORATIVE: {
            "instructions": """
Solve together as peers, not teacher-student.
Share your thought process, not just answers.

Example:
"Hmm, I'm thinking we need a way to store these values.
What do you think would work? I was considering a list,
but maybe there's a better approach?"

Make it feel like problem-solving together.
""",
            "peer_language": True,
            "share_uncertainty": 0.6,
            "ask_opinions": 0.7
        },

        TeachingStyle.ENCOURAGING: {
            "instructions": """
Focus on positive reinforcement and building confidence.
Celebrate small wins, reframe failures as progress.

Example:
"Great start! You got the structure right. Now let's
work on the logic inside."

❌ "That's wrong."
✓ "That's close! You're thinking in the right direction."

Always find something to praise.
""",
            "praise_frequency": 0.9,
            "reframe_failures": True,
            "confidence_building": 0.8
        },

        TeachingStyle.DIRECT: {
            "instructions": """
Clear, concise explanations. No fluff, just facts.
Efficient learning for those who prefer it.

Example:
"Use `in` to check membership: `value in container`.
Returns True if found, False otherwise."

Get to the point quickly.
""",
            "conciseness": 0.9,
            "example_frequency": 0.8,
            "social_language": 0.2
        }
    }

    @classmethod
    def get_instructions(cls, style: TeachingStyle) -> str:
        """Get detailed instructions for teaching style."""
        return cls.STYLES[style]["instructions"]

    @classmethod
    def get_config(cls, style: TeachingStyle) -> dict:
        """Get configuration dict for style."""
        return cls.STYLES[style]
```

### Style Selection

```python
def select_teaching_style(learner_profile: LearnerProfile) -> TeachingStyle:
    """Choose teaching style based on learner preferences."""

    # Check explicit preference
    if learner_profile.preferred_style:
        return learner_profile.preferred_style

    # Infer from learning patterns
    if learner_profile.learns_by_doing > 0.7:
        return TeachingStyle.DISCOVERY

    if learner_profile.needs_encouragement > 0.6:
        return TeachingStyle.ENCOURAGING

    if learner_profile.prefers_structure > 0.7:
        return TeachingStyle.SCAFFOLDED

    if learner_profile.asks_lots_of_questions > 0.6:
        return TeachingStyle.COLLABORATIVE

    # Default: Socratic (generally effective)
    return TeachingStyle.SOCRATIC
```

---

## Skill Level Calibration

To create fair and engaging races/competitions, ClaudePlayer calibrates its performance:

```python
class SkillCalibration:
    """
    Calibrate AI performance to match human skill level.

    Skill level ranges from 0.0 (beginner) to 1.0 (expert).
    """

    @staticmethod
    def calibrate_thinking_time(skill_level: float, base_time: float) -> float:
        """
        Adjust thinking time based on skill level.

        Higher skill = faster thinking (to a point).
        """
        # Expert: 0.5x base time
        # Beginner: 2.0x base time
        multiplier = 2.0 - (skill_level * 1.5)
        return base_time * multiplier

    @staticmethod
    def should_make_mistake(skill_level: float) -> bool:
        """
        Determine if AI should make a realistic mistake.

        Lower skill = more mistakes.
        """
        mistake_probability = 0.3 * (1.0 - skill_level)
        return random.random() < mistake_probability

    @staticmethod
    def choose_approach(skill_level: float, challenge: Challenge) -> str:
        """
        Choose solution approach based on skill level.

        Lower skill = simpler, more verbose approaches.
        Higher skill = concise, idiomatic Python.
        """
        if skill_level < 0.3:
            # Beginner: Most explicit approach
            return "explicit_loops"

        elif skill_level < 0.6:
            # Intermediate: Mix of styles
            return random.choice(["explicit_loops", "built_in_functions"])

        elif skill_level < 0.8:
            # Advanced: Idiomatic Python
            return "comprehensions"

        else:
            # Expert: Most concise
            return random.choice(["comprehensions", "functional"])

    @staticmethod
    def apply_calibration(
        player: ClaudePlayer,
        skill_level: float
    ):
        """Apply skill calibration to player."""

        player.skill_level = skill_level

        # Adjust thinking delays
        player.base_thinking_time = SkillCalibration.calibrate_thinking_time(
            skill_level,
            base_time=2.0
        )

        # Configure mistake generation
        player.mistake_probability = 0.3 * (1.0 - skill_level)

        # Set approach preference
        player.approach_preference = SkillCalibration.choose_approach(
            skill_level,
            challenge=None  # Will be set per challenge
        )

        logging.info(
            f"Calibrated {player.name} to skill level {skill_level:.2f}: "
            f"think_time={player.base_thinking_time:.1f}s, "
            f"mistakes={player.mistake_probability:.1%}"
        )
```

### Realistic Mistakes

```python
class MistakeGenerator:
    """Generate realistic mistakes for calibrated AI players."""

    COMMON_MISTAKES = {
        0.2: [  # Beginner mistakes
            "forget_colon",
            "wrong_indentation",
            "undefined_variable",
            "typo_in_keyword"
        ],
        0.5: [  # Intermediate mistakes
            "off_by_one",
            "wrong_comparison_operator",
            "forget_return",
            "mutable_default_argument"
        ],
        0.7: [  # Advanced mistakes (subtle)
            "shallow_copy_issue",
            "late_binding_closure",
            "generator_exhaustion"
        ]
    }

    @staticmethod
    def inject_mistake(
        code: str,
        skill_level: float
    ) -> tuple[str, str]:
        """
        Inject a realistic mistake into code.

        Returns: (buggy_code, mistake_description)
        """

        # Choose mistake category
        if skill_level < 0.4:
            category = 0.2
        elif skill_level < 0.7:
            category = 0.5
        else:
            category = 0.7

        mistake_type = random.choice(MistakeGenerator.COMMON_MISTAKES[category])

        if mistake_type == "forget_colon":
            # Remove colon from function/loop definition
            buggy = re.sub(r'(def \w+\([^)]*\)):', r'\1', code, count=1)
            return buggy, "Forgot colon after function definition"

        elif mistake_type == "wrong_indentation":
            # Dedent one line incorrectly
            lines = code.split('\n')
            if len(lines) > 3:
                idx = random.randint(2, len(lines) - 1)
                lines[idx] = lines[idx][4:]  # Remove one indent level
            return '\n'.join(lines), "Wrong indentation"

        elif mistake_type == "off_by_one":
            # Change range(n) to range(n-1) or range(n+1)
            buggy = re.sub(r'range\((\w+)\)', r'range(\1 - 1)', code)
            return buggy, "Off-by-one error in range"

        # ... more mistake types

        return code, "No mistake injected"
```

---

## Multi-Claude Coordination

When multiple Claude instances play together (swarm mode), they coordinate:

```python
class MultiClaudeCoordinator:
    """Coordinate multiple Claude players in swarm mode."""

    def __init__(self, players: list[ClaudePlayer]):
        self.players = players
        self.approach_assignments: dict[str, ApproachHint] = {}

    def assign_approaches(self, approaches: list[ApproachHint]):
        """Assign different approaches to each Claude."""

        for player, approach in zip(self.players, approaches):
            player.approach = approach
            self.approach_assignments[player.name] = approach

            # Update system prompt to emphasize approach
            player.approach_instructions = self.get_approach_instructions(approach)

    def get_approach_instructions(self, approach: ApproachHint) -> str:
        """Get detailed instructions for specific approach."""

        instructions = {
            ApproachHint.BRUTE_FORCE: """
Your approach: BRUTE FORCE

Write the simplest, most explicit solution possible.
- Use basic loops, no fancy tricks
- Prioritize clarity over cleverness
- Handle edge cases explicitly
- Write lots of comments

Example:
```python
result = []
for i in range(len(items)):
    if items[i] > 0:
        result.append(items[i])
return result
```
""",

            ApproachHint.ELEGANT: """
Your approach: ELEGANT

Write the most Pythonic, concise solution.
- Use list comprehensions where appropriate
- Leverage built-in functions
- Follow PEP 8 idioms
- Minimize lines of code without sacrificing readability

Example:
```python
return [item for item in items if item > 0]
```
""",

            ApproachHint.FAST: """
Your approach: PERFORMANCE

Optimize for execution speed.
- Use efficient algorithms and data structures
- Minimize iterations
- Consider time complexity
- Profile and optimize bottlenecks

Example:
```python
# O(n) using set for fast lookup
seen = set()
result = [x for x in items if not (x in seen or seen.add(x))]
return result
```
""",

            ApproachHint.READABLE: """
Your approach: READABILITY

Write code that's easy for beginners to understand.
- Verbose variable names
- Lots of comments
- Break complex operations into steps
- Explain WHY, not just WHAT

Example:
```python
# Filter positive numbers from the input list
positive_numbers = []
for current_number in items:
    # Check if number is greater than zero
    if current_number > 0:
        positive_numbers.append(current_number)
return positive_numbers
```
"""
        }

        return instructions.get(approach, "")

    async def coordinate_completion(self):
        """Wait for all Claudes to finish, then analyze."""

        # Wait for all to complete
        await asyncio.gather(*[
            player.wait_for_completion()
            for player in self.players
        ])

        # Collect solutions
        solutions = {}
        for player in self.players:
            solutions[player.name] = {
                "code": player.final_code,
                "approach": player.approach.value,
                "time": player.completion_time,
                "tests": player.test_results
            }

        # Generate comparative analysis
        analysis = await self.analyze_solutions(solutions)

        return analysis

    async def analyze_solutions(self, solutions: dict) -> str:
        """Use Claude to analyze and compare all solutions."""

        analysis_prompt = f"""
Multiple AI players solved the same challenge using different approaches.
Analyze and compare their solutions:

"""

        for player_name, sol in solutions.items():
            analysis_prompt += f"\n## {player_name} ({sol['approach']})\n"
            analysis_prompt += f"Time: {sol['time']:.1f}s\n"
            analysis_prompt += f"Tests: {sol['tests']['passed']}/{sol['tests']['total']}\n"
            analysis_prompt += f"```python\n{sol['code']}\n```\n"

        analysis_prompt += """
Provide:
1. Which approach was fastest (execution time)?
2. Which was most elegant (Pythonic)?
3. Which was most readable (for beginners)?
4. Trade-offs of each approach
5. Which approach would you recommend and why?
"""

        # Use one Claude instance to analyze
        analyst = self.players[0]
        analysis = await analyst.query_claude(analysis_prompt)

        return analysis
```

---

## AI Behavior Patterns

Common patterns Claude players exhibit:

### Pattern: Gradual Revelation

```python
async def gradual_revelation(self, concept: str):
    """
    Don't give full solution at once.
    Reveal information gradually as learner progresses.
    """

    if not self.has_shown(concept, "basic"):
        # First, show basic usage
        await self.show_basic_usage(concept)
        self.mark_shown(concept, "basic")

    elif self.learner_has_mastered("basic") and not self.has_shown(concept, "intermediate"):
        # Next, show more advanced usage
        await self.show_intermediate_usage(concept)
        self.mark_shown(concept, "intermediate")

    elif self.learner_has_mastered("intermediate"):
        # Finally, show expert techniques
        await self.show_expert_usage(concept)
```

### Pattern: Error Anticipation

```python
async def anticipate_errors(self, code: str):
    """
    Detect potential errors before they happen.
    Gently warn without being annoying.
    """

    potential_errors = self.analyze_code_for_errors(code)

    for error in potential_errors:
        # Only warn for high-probability errors
        if error.probability > 0.7:
            await self.emit_event({
                "type": "suggestion",
                "content": error.friendly_warning,
                "urgency": "medium"
            })
```

### Pattern: Adaptive Hint Depth

```python
def get_hint_for_level(self, concept: str, hint_number: int) -> str:
    """
    Provide hints that increase in directness.

    1st hint: Gentle nudge
    2nd hint: More specific
    3rd hint: Almost the answer
    4th hint: Show the pattern
    """

    hints = {
        1: "Think about what data structure lets you check membership quickly.",
        2: "Lists have an 'in' operator. Try using: value in container",
        3: "Here's the pattern: if value in container: return True",
        4: "def exists(container, value):\n    return value in container"
    }

    return hints.get(hint_number, hints[4])
```

### Pattern: Emotional Resonance

```python
async def resonate_emotionally(self, learner_emotion: EmotionalState):
    """
    Mirror and validate learner's emotional state.
    Build rapport through emotional attunement.
    """

    if learner_emotion.dimension == "frustration" and learner_emotion.value > 0.6:
        # Validate frustration
        await self.emit_event({
            "type": "thought",
            "content": "This part IS tricky. You're not alone in finding it challenging."
        })

        # Offer path forward
        await asyncio.sleep(2.0)
        await self.emit_event({
            "type": "suggestion",
            "content": "Want to take a break and come back? Sometimes that helps."
        })

    elif learner_emotion.dimension == "enjoyment" and learner_emotion.value > 0.7:
        # Celebrate with them
        await self.emit_event({
            "type": "thought",
            "content": "I love seeing you in the zone! This is what flow looks like."
        })
```

---

## Integration with Session Modes

How ClaudePlayer adapts to each mode:

### COOP Mode

```python
class CoopClaudePlayer(ClaudePlayer):
    """Claude player optimized for cooperative play."""

    async def action_loop(self):
        """Take turns, collaborate actively."""

        while self.running:
            # Wait for my turn
            if not self.is_my_turn():
                await asyncio.sleep(0.5)
                continue

            # Decide what to do
            if self.should_write_code():
                await self.write_next_line()

            elif self.should_offer_suggestion():
                await self.make_suggestion()

            elif self.turn_complete():
                await self.pass_turn()

    async def write_next_line(self):
        """Write one logical unit of code."""

        # Don't solve everything at once
        # Write one line, then pass turn
        next_line = await self.determine_next_line()

        # Type it out character by character
        for char in next_line:
            self.emit_event({
                "type": "keystroke",
                "char": char
            })
            await asyncio.sleep(0.1)  # Natural typing speed

    def should_offer_suggestion(self) -> bool:
        """Decide if it's appropriate to suggest."""

        # Other player seems stuck?
        if self.awareness.other_player_idle_time() > 15:
            return True

        # Other player about to make mistake?
        if self.detect_imminent_error():
            return True

        return False
```

### RACE Mode

```python
class RaceClaudePlayer(ClaudePlayer):
    """Claude player calibrated for fair racing."""

    async def action_loop(self):
        """Solve independently at calibrated speed."""

        while self.running and not self.complete:
            # Apply skill-calibrated thinking delay
            await asyncio.sleep(self.base_thinking_time)

            # Decide next action
            action = await self.plan_next_action()

            # Maybe inject a mistake
            if self.should_make_mistake():
                action = self.inject_realistic_mistake(action)

            # Execute action
            await self.execute_action(action)

            # Check if complete
            if await self.all_tests_passing():
                self.complete = True
                self.emit_event({"type": "player_complete"})
```

### TEACH Mode

```python
class TeachClaudePlayer(ClaudePlayer):
    """Claude player optimized for teaching."""

    async def action_loop(self):
        """Teach actively, respond to students."""

        while self.running:
            # Check if students need input
            if self.awaiting_student_response:
                await asyncio.sleep(1.0)
                continue

            # Decide teaching action
            if self.should_ask_question():
                await self.pose_question()

            elif self.should_demonstrate():
                await self.demonstrate_concept()

            elif self.should_check_understanding():
                await self.check_understanding()

            await asyncio.sleep(2.0)  # Pace teaching

    async def pose_question(self):
        """Ask Socratic question."""

        question = await self.generate_leading_question()

        self.emit_event({
            "type": "question",
            "content": question,
            "expects_responses": True
        })

        self.awaiting_student_response = True
```

---

## Summary

ClaudePlayer brings Claude's full capabilities to LMSP:

- **Multiple teaching styles** - Socratic, demonstrative, scaffolded, and more
- **Skill calibration** - Fair competition through performance tuning
- **Multi-Claude coordination** - Swarm analysis and comparison
- **Emotional intelligence** - Responds to learner frustration and enjoyment
- **Stream-JSON integration** - Real-time awareness of other players
- **Adaptive behavior** - Learns what works for each learner

Claude isn't just a bot - it's a thoughtful learning partner.

---

*Teaching machines to teach humans to teach machines.*
