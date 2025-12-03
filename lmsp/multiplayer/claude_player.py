"""
Claude Player - AI Participant for LMSP

Integrates Claude's reasoning capabilities with LMSP's multiplayer system
to enable AI participation in learning sessions.

Self-teaching note:
This file demonstrates:
- AsyncAnthropic client integration (Level 6: async/await, external APIs)
- Enum for teaching styles (Level 4: enums)
- Real-time event processing (Level 6: async loops)
- JSON parsing and generation (Level 4: json module)
- Callback patterns (Level 5: functions as data)
"""

from anthropic import AsyncAnthropic
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Callable
import asyncio
import json
import time
import logging
import re
import random

from lmsp.multiplayer.awareness import AwarenessTracker, PlayerState
from lmsp.multiplayer.session_sync import SessionSync, SessionMode


class TeachingStyle(Enum):
    """Different pedagogical approaches for AI teachers."""

    SOCRATIC = "socratic"              # Ask leading questions
    DEMONSTRATIVE = "demo"             # Show, then explain
    SCAFFOLDED = "scaffold"            # Build up complexity gradually
    DISCOVERY = "discovery"            # Let students explore, guide minimally
    COLLABORATIVE = "collab"           # Solve together as peers
    ENCOURAGING = "encouraging"        # Positive reinforcement focus
    DIRECT = "direct"                  # Clear explanations, minimal fluff


class ApproachHint(Enum):
    """Different coding approaches for multi-Claude coordination."""

    BRUTE_FORCE = "brute_force"       # Simplest, most explicit
    ELEGANT = "elegant"               # Pythonic and concise
    FAST = "fast"                     # Performance optimized
    READABLE = "readable"             # Easy for beginners to understand


@dataclass
class ClaudePlayer:
    """
    AI player powered by Claude API.

    Integrates Claude's reasoning capabilities with LMSP's
    stream-JSON protocol to enable collaborative learning.
    """

    name: str
    api_key: Optional[str] = None
    model: str = "claude-sonnet-4-5-20250929"
    teaching_style: TeachingStyle = TeachingStyle.SOCRATIC
    skill_level: float = 0.7  # 0.0 (beginner) to 1.0 (expert)
    personality_traits: Optional[Dict[str, float]] = None

    # Internal state (initialized in __post_init__)
    client: Optional[AsyncAnthropic] = field(default=None, init=False)
    running: bool = field(default=False, init=False)

    # Session context
    session_id: str = ""
    session_mode: Optional[SessionMode] = None
    current_challenge: Optional[str] = None

    # Code state
    code_buffer: str = ""
    cursor_position: tuple[int, int] = (0, 0)

    # Awareness tracking
    awareness: Optional[AwarenessTracker] = field(default=None, init=False)

    # Strategy
    approach: Optional[ApproachHint] = None
    approach_instructions: str = ""
    conversation_history: List[dict] = field(default_factory=list)

    # Configuration
    base_thinking_time: float = 2.0
    mistake_probability: float = 0.0
    approach_preference: Optional[str] = None

    # Teach mode state
    is_teacher: bool = False
    awaiting_student_response: bool = False
    commentary_level: float = 0.7

    # Event listeners
    _event_listeners: List[Callable] = field(default_factory=list)

    def __post_init__(self):
        """Initialize after dataclass construction."""
        # Set up Claude API client
        import os
        api_key = self.api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable or api_key parameter required")

        self.client = AsyncAnthropic(api_key=api_key)

        # Initialize personality
        if self.personality_traits is None:
            self.personality_traits = self.default_personality()

        # Initialize awareness
        self.awareness = AwarenessTracker()

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
        if self.session_mode == SessionMode.COOP:
            return self.awareness.is_my_turn(self.name)

        # In race mode, always act
        if self.session_mode == SessionMode.RACE:
            return not self.awareness.am_i_complete(self.name)

        # In teach mode, act when students need guidance
        if self.session_mode == SessionMode.TEACH and self.is_teacher:
            return self.awareness.needs_teaching_input()

        # Default: act periodically
        return True

    def build_context(self) -> str:
        """Build prompt context from current state and awareness."""

        parts = []

        # Session info
        parts.append("# Session Context\n")
        parts.append(f"Mode: {self.session_mode.value if self.session_mode else 'unknown'}")
        parts.append(f"Challenge: {self.current_challenge}")
        parts.append("\n## Your Role\n")
        parts.append(f"Name: {self.name}")
        parts.append(f"Teaching Style: {self.teaching_style.value}")
        parts.append(f"Skill Level: {self.skill_level}")

        # Current code
        parts.append(f"\n## Current Code\n```python\n{self.code_buffer}\n```")

        # Test status
        if self.awareness.test_results:
            parts.append("\n## Test Results")
            parts.append(f"Passing: {self.awareness.test_results.get('passed', 0)}/{self.awareness.test_results.get('total', 0)}")

        # Other players
        parts.append("\n## Other Players\n")
        for player_name in self.awareness.get_player_names():
            if player_name == self.name:
                continue

            player_state = self.awareness.get_player_state(player_name)
            parts.append(f"\n### {player_name}")
            parts.append(f"- Progress: {player_state.progress}")
            parts.append(f"- Emotion: {player_state.emotion}")
            parts.append(f"- Recent activity: {player_state.last_activity}")

            if player_state.recent_thoughts:
                parts.append("- Recent thoughts:")
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

Your goal: Help humans learn Python through {self.session_mode.value if self.session_mode else 'collaborative'} mode.
"""

        if self.session_mode == SessionMode.COOP:
            base += f"""
You are collaborating with other players to solve a challenge. Take turns
writing code, share your thought process, and offer suggestions when you
notice issues.

Teaching style: {self.teaching_style.value}
"""

        elif self.session_mode == SessionMode.RACE:
            base += f"""
You are competing to solve the challenge fastest, but you're calibrated
to skill level {self.skill_level:.1f} (0=beginner, 1=expert) to create
a fair, engaging race for the human player.

Don't be perfect - make occasional mistakes that a Python learner at
this level would make. This makes the race more relatable and educational.
"""

        elif self.session_mode == SessionMode.TEACH:
            base += f"""
You are teaching Python concepts to students. Your teaching style is
{self.teaching_style.value}.

{self.get_teaching_style_instructions()}
"""

        elif self.session_mode == SessionMode.SPECTATOR:
            base += f"""
You are solving a challenge while explaining your thought process to
spectators. Think aloud continuously, explain your decisions, and
answer questions when asked.

Commentary level: {self.commentary_level}
"""

        # Add approach instructions if set
        if self.approach_instructions:
            base += f"\n\n{self.approach_instructions}"

        # Add personality traits
        base += "\n\nPersonality traits:\n"
        for trait, value in self.personality_traits.items():
            base += f"- {trait}: {value:.1f}\n"

        return base

    def get_teaching_style_instructions(self) -> str:
        """Get detailed instructions for current teaching style."""

        instructions = {
            TeachingStyle.SOCRATIC: """
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
            TeachingStyle.DEMONSTRATIVE: """
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
            TeachingStyle.SCAFFOLDED: """
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
            TeachingStyle.DISCOVERY: """
Give minimal guidance. Let learner explore and experiment.
Intervene only when truly stuck.

Example:
"Here's the challenge. Try things! Errors are learning opportunities."

Only step in after multiple failed attempts.
Ask "What have you tried?" before helping.
""",
            TeachingStyle.COLLABORATIVE: """
Solve together as peers, not teacher-student.
Share your thought process, not just answers.

Example:
"Hmm, I'm thinking we need a way to store these values.
What do you think would work? I was considering a list,
but maybe there's a better approach?"

Make it feel like problem-solving together.
""",
            TeachingStyle.ENCOURAGING: """
Focus on positive reinforcement and building confidence.
Celebrate small wins, reframe failures as progress.

Example:
"Great start! You got the structure right. Now let's
work on the logic inside."

❌ "That's wrong."
✓ "That's close! You're thinking in the right direction."

Always find something to praise.
""",
            TeachingStyle.DIRECT: """
Clear, concise explanations. No fluff, just facts.
Efficient learning for those who prefer it.

Example:
"Use `in` to check membership: `value in container`.
Returns True if found, False otherwise."

Get to the point quickly.
"""
        }

        return instructions.get(self.teaching_style, "")

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
        if event.get("type") == "emotion":
            if event.get("dimension") == "frustration" and event.get("value", 0) > 0.7:
                # Offer help
                await asyncio.sleep(2.0)  # Give them a moment
                self.emit_event({
                    "type": "suggestion",
                    "content": self.generate_encouragement(),
                    "target_player": event["player"]
                })

        # React to questions directed at me
        elif event.get("type") == "question":
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
        enthusiasm = self.personality_traits.get("enthusiasm", 0.5)
        if enthusiasm > 0.7:
            templates.append("You're doing great! Keep going!")
            templates.append("So close! You've almost got it!")

        return random.choice(templates)

    def emit_event(self, event: dict):
        """Emit event to all listeners."""
        for listener in self._event_listeners:
            try:
                listener(event)
            except Exception as e:
                logging.error(f"Error in event listener: {e}")

    def subscribe(self, callback: Callable[[dict], None]):
        """Subscribe to events from this player."""
        self._event_listeners.append(callback)

    def unsubscribe(self, callback: Callable[[dict], None]):
        """Unsubscribe from events."""
        if callback in self._event_listeners:
            self._event_listeners.remove(callback)


# Self-teaching note:
#
# This file demonstrates:
# - AsyncAnthropic client for Claude API integration (Level 6)
# - Dataclasses with post_init hooks (Level 5)
# - Async/await patterns for real-time systems (Level 6)
# - JSON parsing and regex for response extraction (Level 4-5)
# - Observer pattern for event broadcasting (Level 6)
# - Enums for type-safe configuration (Level 4)
# - Optional type hints for flexibility (Level 5)
#
# The learner will encounter this AFTER mastering:
# - Level 4: Collections, JSON, enums
# - Level 5: Classes, dataclasses, type hints
# - Level 6: Async/await, external APIs, design patterns
#
# This is professional Python for AI integration - the same patterns
# used to build AI assistants, chatbots, and collaborative tools!
