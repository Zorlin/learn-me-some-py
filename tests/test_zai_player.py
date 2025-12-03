"""
Tests for ZAI Player - AI playtester using Z.ai GLM API

TDD: These tests define expected behavior BEFORE implementation.

Tests cover:
1. Initialization with Z.ai API key
2. Observing game state
3. Writing code solutions
4. Providing UX feedback
5. Detecting confusing patterns
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import asyncio

from lmsp.multiplayer.zai_player import ZAIPlayer, PlaytestFeedback
from lmsp.game.engine import GameEngine, GameConfig
from lmsp.adaptive.engine import LearnerProfile
from lmsp.python.challenges import Challenge


class TestZAIPlayerInit:
    """Test ZAI player initialization."""

    def test_basic_initialization(self):
        """Player should initialize with Z.ai API key."""
        player = ZAIPlayer(
            name="TestBot",
            api_key="test-zai-key",
        )

        assert player.name == "TestBot"
        assert player.api_key == "test-zai-key"
        assert player.model == "glm-4-plus"  # Default Z.ai model

    def test_custom_model(self):
        """Should allow custom Z.ai model."""
        player = ZAIPlayer(
            name="TestBot",
            api_key="test-key",
            model="glm-4-flash",
        )

        assert player.model == "glm-4-flash"


class TestGameStateObservation:
    """Test observing and understanding game state."""

    @pytest.fixture
    def player(self):
        return ZAIPlayer(name="Observer", api_key="test-key")

    def test_observe_challenge(self, player):
        """Should observe and understand challenge."""
        challenge = Challenge(
            id="test_01",
            name="Test Challenge",
            description="Write a function that returns 42",
            skeleton_code="def answer():\n    pass",
            test_cases=["assert answer() == 42"],
            level=1,
        )

        player.observe_challenge(challenge)

        assert player.current_challenge == challenge
        assert "Write a function" in player.challenge_context

    def test_observe_code_state(self, player):
        """Should track current code state."""
        code = "def answer():\n    return 42"

        player.observe_code(code)

        assert player.current_code == code

    def test_build_observation_context(self, player):
        """Should build context from observations."""
        challenge = Challenge(
            id="test_01",
            name="Test",
            description="Test challenge",
            skeleton_code="",
            test_cases=[],
            level=1,
        )

        player.observe_challenge(challenge)
        player.observe_code("x = 5")

        context = player.build_context()

        assert "challenge" in context.lower()
        assert "x = 5" in context


class TestCodeGeneration:
    """Test generating code solutions."""

    @pytest.fixture
    def player(self):
        return ZAIPlayer(name="Coder", api_key="test-key")

    @pytest.mark.asyncio
    async def test_generate_solution_basic(self, player):
        """Should generate code solution."""
        challenge = Challenge(
            id="test_01",
            name="Return 42",
            description="Write a function that returns 42",
            skeleton_code="def answer():\n    pass",
            test_cases=["assert answer() == 42"],
            level=1,
        )

        player.observe_challenge(challenge)

        with patch("lmsp.multiplayer.zai_player.requests.post") as mock_post:
            # Mock Z.ai API response
            mock_response = Mock()
            mock_response.json.return_value = {
                "choices": [
                    {
                        "message": {
                            "content": "```python\ndef answer():\n    return 42\n```"
                        }
                    }
                ]
            }
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            solution = await player.generate_solution()

            assert solution is not None
            assert "return 42" in solution

    @pytest.mark.asyncio
    async def test_extract_code_from_response(self, player):
        """Should extract code from markdown response."""
        response = """
        Here's the solution:

        ```python
        def answer():
            return 42
        ```

        This returns 42 as requested.
        """

        code = player.extract_code(response)

        assert "def answer():" in code
        assert "return 42" in code
        assert "```" not in code  # Should strip markdown


class TestUXFeedback:
    """Test UX feedback generation."""

    @pytest.fixture
    def player(self):
        return ZAIPlayer(name="Critic", api_key="test-key")

    def test_track_confusion_signs(self, player):
        """Should track signs of confusion."""
        # Simulate multiple failed attempts
        player.record_attempt(success=False)
        player.record_attempt(success=False)
        player.record_attempt(success=False)

        assert player.attempt_count == 3
        assert player.failure_count == 3

    def test_detect_confusing_ux(self, player):
        """Should detect confusing UX patterns."""
        # Rapid failures suggest confusion
        player.record_attempt(success=False, time_seconds=5)
        player.record_attempt(success=False, time_seconds=3)
        player.record_attempt(success=False, time_seconds=4)

        issues = player.detect_ux_issues()

        assert len(issues) > 0
        assert any("rapid failures" in issue.lower() for issue in issues)

    def test_generate_feedback(self, player):
        """Should generate structured feedback."""
        challenge = Challenge(
            id="test_01",
            name="Confusing Challenge",
            description="Unclear instructions",
            skeleton_code="",
            test_cases=[],
            level=1,
        )

        player.observe_challenge(challenge)
        player.record_attempt(success=False)
        player.record_attempt(success=False)

        feedback = player.generate_feedback()

        assert isinstance(feedback, PlaytestFeedback)
        assert feedback.challenge_id == "test_01"
        assert feedback.confusion_score > 0.0

    def test_feedback_includes_suggestions(self, player):
        """Feedback should include actionable suggestions."""
        player.record_attempt(success=False)
        player.record_attempt(success=False)

        feedback = player.generate_feedback()

        assert len(feedback.suggestions) > 0


class TestEndToEnd:
    """Test end-to-end playtest simulation."""

    @pytest.mark.asyncio
    async def test_complete_challenge_playtest(self):
        """Should complete full playtest cycle."""
        player = ZAIPlayer(name="Playtester", api_key="test-key")

        challenge = Challenge(
            id="test_01",
            name="Simple Challenge",
            description="Return 42",
            skeleton_code="def answer():\n    pass",
            test_cases=["assert answer() == 42"],
            level=1,
        )

        with patch("lmsp.multiplayer.zai_player.requests.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "choices": [
                    {
                        "message": {
                            "content": "```python\ndef answer():\n    return 42\n```"
                        }
                    }
                ]
            }
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            # Observe challenge
            player.observe_challenge(challenge)

            # Generate solution
            solution = await player.generate_solution()
            assert solution is not None

            # Record successful attempt
            player.record_attempt(success=True, time_seconds=10)

            # Generate feedback
            feedback = player.generate_feedback()
            assert feedback.success is True


class TestPlaytestFeedback:
    """Test PlaytestFeedback dataclass."""

    def test_feedback_structure(self):
        """Feedback should have required fields."""
        feedback = PlaytestFeedback(
            challenge_id="test_01",
            success=True,
            attempts=1,
            time_seconds=10.0,
            confusion_score=0.0,
            suggestions=["Add more examples"],
            ux_issues=[],
        )

        assert feedback.challenge_id == "test_01"
        assert feedback.success is True
        assert feedback.attempts == 1
        assert len(feedback.suggestions) > 0

    def test_high_confusion_score(self):
        """Should flag high confusion."""
        feedback = PlaytestFeedback(
            challenge_id="test_01",
            success=False,
            attempts=5,
            time_seconds=120.0,
            confusion_score=0.9,
            suggestions=[],
            ux_issues=["Unclear instructions", "Missing examples"],
        )

        assert feedback.confusion_score > 0.7
        assert len(feedback.ux_issues) > 0


# Self-teaching note:
#
# This test file demonstrates:
# - Test-driven development (TDD) - tests written FIRST
# - Mocking external API calls
# - AsyncMock for async functions
# - Testing observation and feedback systems
# - Dataclass validation
#
# Prerequisites:
# - Level 3: Functions, classes, testing basics
# - Level 4: Async/await
# - Level 5: Mocking, complex testing
# - Level 6: API integration patterns
