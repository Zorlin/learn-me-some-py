"""
ZAI Player - AI playtester using Z.ai GLM API

Uses Z.ai's GLM models (cheaper alternative to Anthropic) to:
1. Observe game state and challenges
2. Generate code solutions
3. Provide UX feedback based on playtest experience
4. Detect confusing patterns and suggest improvements

This enables automated playtesting to find UX issues humans might miss.
"""

import asyncio
import re
import time
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import requests


@dataclass
class PlaytestFeedback:
    """Structured feedback from AI playtest session."""

    challenge_id: str
    success: bool
    attempts: int
    time_seconds: float
    confusion_score: float  # 0.0 = clear, 1.0 = very confusing
    suggestions: List[str] = field(default_factory=list)
    ux_issues: List[str] = field(default_factory=list)


class ZAIPlayer:
    """
    AI player that uses Z.ai GLM API to play LMSP challenges.

    Observes game state, writes code solutions, and provides
    feedback on UX issues and confusing patterns.
    """

    def __init__(
        self,
        name: str,
        api_key: str,
        model: str = "glm-4-plus",
    ):
        """
        Initialize ZAI player.

        Args:
            name: Player name
            api_key: Z.ai API key
            model: Z.ai model to use (glm-4-plus or glm-4-flash)
        """
        self.name = name
        self.api_key = api_key
        self.model = model

        # Game state tracking
        self.current_challenge: Optional[Any] = None
        self.challenge_context: str = ""
        self.current_code: str = ""

        # Playtest metrics
        self.attempt_count: int = 0
        self.failure_count: int = 0
        self.attempt_times: List[float] = []
        self.action_history: List[Dict[str, Any]] = []

        # Z.ai API endpoint
        self.api_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

    def observe_challenge(self, challenge: Any) -> None:
        """
        Observe and store a challenge.

        Args:
            challenge: Challenge object to observe
        """
        self.current_challenge = challenge
        self.challenge_context = f"""
Challenge: {challenge.name}
Description: {challenge.description_brief}
Details: {challenge.description_detailed}
Skeleton Code:
{challenge.skeleton_code}
Test Cases: {len(challenge.test_cases)} tests
Level: {challenge.level}
"""

    def observe_code(self, code: str) -> None:
        """
        Track current code state.

        Args:
            code: Current code being worked on
        """
        self.current_code = code

    def build_context(self) -> str:
        """
        Build context string from observations.

        Returns:
            Context string for AI
        """
        context = "Game Context:\n"

        if self.challenge_context:
            context += self.challenge_context + "\n"

        if self.current_code:
            context += f"\nCurrent Code:\n{self.current_code}\n"

        return context

    async def generate_solution(self) -> Optional[str]:
        """
        Generate code solution using Z.ai API.

        Returns:
            Generated code solution or None on error
        """
        if not self.current_challenge:
            return None

        context = self.build_context()

        prompt = f"""You are an AI player testing a Python learning game.
Your task is to solve the following challenge by writing Python code.

{context}

Write a complete solution that passes all test cases.
Return ONLY the Python code in a markdown code block.
"""

        try:
            # Call Z.ai API
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }

            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                "temperature": 0.7,
            }

            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return self.extract_code(content)
            else:
                return None

        except Exception as e:
            print(f"Error generating solution: {e}")
            return None

    def extract_code(self, response: str) -> str:
        """
        Extract Python code from markdown response.

        Args:
            response: API response with markdown code blocks

        Returns:
            Extracted Python code
        """
        # Find code blocks
        code_pattern = r"```python\n(.*?)```"
        matches = re.findall(code_pattern, response, re.DOTALL)

        if matches:
            return matches[0].strip()

        # If no code block, return the whole response stripped
        return response.strip()

    def record_attempt(
        self,
        success: bool,
        time_seconds: float = 0,
    ) -> None:
        """
        Record a challenge attempt.

        Args:
            success: Whether attempt succeeded
            time_seconds: Time taken for attempt
        """
        self.attempt_count += 1
        if not success:
            self.failure_count += 1

        if time_seconds > 0:
            self.attempt_times.append(time_seconds)

        self.action_history.append({
            "type": "attempt",
            "success": success,
            "time": time_seconds,
            "timestamp": time.time(),
        })

    def detect_ux_issues(self) -> List[str]:
        """
        Detect UX issues based on playtest metrics.

        Returns:
            List of detected UX issues
        """
        issues = []

        # Rapid failures suggest confusion
        if self.failure_count >= 3:
            recent_times = self.attempt_times[-3:] if len(self.attempt_times) >= 3 else self.attempt_times
            if recent_times and all(t < 10 for t in recent_times):
                issues.append("rapid failures - possible unclear instructions")

        # High failure rate
        if self.attempt_count > 0:
            failure_rate = self.failure_count / self.attempt_count
            if failure_rate > 0.5:
                issues.append("high failure rate - challenge may be too difficult")

        # Very long attempts suggest struggling
        if self.attempt_times:
            avg_time = sum(self.attempt_times) / len(self.attempt_times)
            if avg_time > 60:
                issues.append("long attempt times - challenge may be unclear")

        return issues

    def generate_feedback(self) -> PlaytestFeedback:
        """
        Generate structured feedback from playtest session.

        Returns:
            PlaytestFeedback object
        """
        # Calculate confusion score
        confusion_score = 0.0

        if self.attempt_count > 0:
            # Factor in failure rate
            failure_rate = self.failure_count / self.attempt_count
            confusion_score += failure_rate * 0.5

            # Factor in rapid failures
            if self.failure_count >= 3:
                confusion_score += 0.3

            # Factor in long attempt times
            if self.attempt_times:
                avg_time = sum(self.attempt_times) / len(self.attempt_times)
                if avg_time > 60:
                    confusion_score += 0.2

        confusion_score = min(1.0, confusion_score)

        # Generate suggestions
        suggestions = []
        issues = self.detect_ux_issues()

        if "unclear instructions" in " ".join(issues):
            suggestions.append("Add more examples to challenge description")
            suggestions.append("Clarify expected output format")

        if "too difficult" in " ".join(issues):
            suggestions.append("Consider breaking challenge into smaller steps")
            suggestions.append("Add hints or scaffolding")

        if "long attempt times" in " ".join(issues):
            suggestions.append("Provide clearer success criteria")
            suggestions.append("Add intermediate checkpoints")

        # Default suggestions if high confusion but no specific issues
        if confusion_score > 0.5 and not suggestions:
            suggestions.append("Review challenge clarity and instructions")

        # Determine success
        success = self.attempt_count > 0 and self.failure_count < self.attempt_count

        # Calculate total time
        total_time = sum(self.attempt_times) if self.attempt_times else 0.0

        return PlaytestFeedback(
            challenge_id=self.current_challenge.id if self.current_challenge else "unknown",
            success=success,
            attempts=self.attempt_count,
            time_seconds=total_time,
            confusion_score=confusion_score,
            suggestions=suggestions,
            ux_issues=issues,
        )


# Self-teaching note:
#
# This file demonstrates:
# - Dataclasses with default factories (Level 5: @dataclass, field(default_factory=list))
# - Async/await for API calls (Level 4: async def, await)
# - Type hints with Optional and List (Level 3: type annotations)
# - Regular expressions for parsing (Level 5: re module)
# - HTTP requests (Level 4: requests library)
# - Metric tracking and analysis (Level 4: data processing)
# - API integration patterns (Level 6: external APIs, authentication)
#
# Prerequisites:
# - Level 3: Classes, methods, type hints
# - Level 4: Async/await, HTTP requests
# - Level 5: Dataclasses, regex, complex patterns
# - Level 6: API design, testing patterns
#
# The learner will build this AFTER mastering prerequisite concepts.
