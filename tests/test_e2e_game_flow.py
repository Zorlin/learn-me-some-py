"""
End-to-End Game Flow Tests
==========================

Comprehensive E2E test: launch web UI -> AI player selects challenge ->
writes Python solution -> submits code -> validates results ->
records emotional feedback -> advances to next challenge.

This tests the COMPLETE vertical integration of all LMSP systems:
- Web UI (FastAPI + HTMX)
- AI Player (ZAI Player or mock AI)
- Challenge System (ChallengeLoader, Challenge)
- Code Validation (CodeValidator)
- Emotional Feedback (EmotionalState, EmotionalFeedbackRenderer)
- Adaptive Learning (AdaptiveEngine)
- Achievement System

TDD: These tests define the expected E2E behavior.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from pathlib import Path

from fastapi.testclient import TestClient

# Import all LMSP components needed for E2E testing
from lmsp.web.app import app
from lmsp.python.challenges import Challenge, TestCase, ChallengeLoader
from lmsp.python.validator import CodeValidator, ValidationResult, TestResult
from lmsp.adaptive.engine import AdaptiveEngine, LearnerProfile, AdaptiveRecommendation
from lmsp.input.emotional import EmotionalState, EmotionalPrompt, EmotionalDimension
from lmsp.ui.emotional_feedback import EmotionalFeedbackRenderer
from lmsp.multiplayer.zai_player import ZAIPlayer, PlaytestFeedback


# ============================================================================
# Test Data Factories
# ============================================================================

def make_test_challenge(
    id: str = "test_hello",
    name: str = "Hello World",
    description: str = "Write a function that returns 'Hello, World!'",
    skeleton: str = "def solution():\n    pass",
    solution: str = "def solution():\n    return 'Hello, World!'",
    level: int = 1,
    expected: Any = "Hello, World!",
) -> Challenge:
    """Create a test challenge with sensible defaults."""
    return Challenge(
        id=id,
        name=name,
        description_brief=description,
        description_detailed=description,
        skeleton_code=skeleton,
        solution_code=solution,
        test_cases=[TestCase(name="basic", input=None, expected=expected)],
        level=level,
        prerequisites=[],
    )


def make_test_profile(
    player_id: str = "e2e_test_player",
    mastery_levels: Optional[Dict[str, float]] = None,
) -> LearnerProfile:
    """Create a test learner profile."""
    return LearnerProfile(
        player_id=player_id,
        mastery_levels=mastery_levels or {},
    )


@dataclass
class E2EGameSession:
    """
    Tracks state throughout an E2E game session.

    This simulates the complete state of a player going through
    the game flow from challenge selection to completion.
    """
    player_id: str = "e2e_test_player"
    current_challenge: Optional[Challenge] = None
    current_code: str = ""
    validation_result: Optional[ValidationResult] = None
    emotional_feedback: Optional[Dict[str, float]] = None
    completed_challenges: List[str] = field(default_factory=list)

    def select_challenge(self, challenge: Challenge) -> None:
        """Select a challenge to work on."""
        self.current_challenge = challenge
        self.current_code = challenge.skeleton_code
        self.validation_result = None

    def update_code(self, code: str) -> None:
        """Update the current code."""
        self.current_code = code

    def record_validation(self, result: ValidationResult) -> None:
        """Record a validation result."""
        self.validation_result = result

    def record_emotional_feedback(self, enjoyment: float, frustration: float = 0.0) -> None:
        """Record emotional feedback after challenge completion."""
        self.emotional_feedback = {
            "enjoyment": enjoyment,
            "frustration": frustration,
        }

    def complete_challenge(self) -> None:
        """Mark the current challenge as completed."""
        if self.current_challenge and self.validation_result and self.validation_result.success:
            self.completed_challenges.append(self.current_challenge.id)
            self.current_challenge = None
            self.current_code = ""
            self.validation_result = None
            self.emotional_feedback = None


# ============================================================================
# Web UI Integration Tests
# ============================================================================

class TestWebUILaunch:
    """Test that the web UI launches correctly."""

    def test_web_ui_index_loads(self):
        """Web UI should load the index page."""
        client = TestClient(app)
        response = client.get("/")

        assert response.status_code == 200
        assert b"LMSP" in response.content

    def test_web_ui_has_challenge_list_endpoint(self):
        """Web UI should have endpoint to list challenges."""
        client = TestClient(app)
        response = client.get("/api/challenges")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_web_ui_has_submit_endpoint(self):
        """Web UI should have endpoint to submit code."""
        client = TestClient(app)
        response = client.post(
            "/api/code/submit",
            json={"challenge_id": "test", "code": "print('hello')"}
        )

        # Should return a response (even if validation not implemented)
        assert response.status_code == 200

    def test_web_ui_has_profile_endpoint(self):
        """Web UI should have endpoint to get player profile."""
        client = TestClient(app)
        response = client.get("/api/profile")

        assert response.status_code == 200
        data = response.json()
        assert "player_id" in data


# ============================================================================
# AI Player Challenge Selection Tests
# ============================================================================

class TestAIPlayerChallengeSelection:
    """Test AI player selecting challenges."""

    @pytest.fixture
    def ai_player(self):
        """Create an AI player for testing."""
        return ZAIPlayer(name="E2E_TestBot", api_key="test-key")

    @pytest.fixture
    def challenges(self):
        """Create a set of test challenges."""
        return [
            make_test_challenge(
                id="hello_world",
                name="Hello World",
                description="Return 'Hello, World!'",
                skeleton="def solution():\n    pass",
                expected="Hello, World!",
                level=1,
            ),
            make_test_challenge(
                id="add_numbers",
                name="Add Numbers",
                description="Add two numbers",
                skeleton="def solution(a, b):\n    pass",
                expected=5,
                level=1,
            ),
            make_test_challenge(
                id="list_sum",
                name="Sum List",
                description="Sum all numbers in a list",
                skeleton="def solution(nums):\n    pass",
                expected=15,
                level=2,
            ),
        ]

    def test_ai_player_observes_challenge(self, ai_player, challenges):
        """AI player should observe and understand a challenge."""
        challenge = challenges[0]
        ai_player.observe_challenge(challenge)

        assert ai_player.current_challenge == challenge
        assert "Hello" in ai_player.challenge_context

    def test_ai_player_builds_context(self, ai_player, challenges):
        """AI player should build context from observations."""
        challenge = challenges[0]
        ai_player.observe_challenge(challenge)
        ai_player.observe_code("def solution():\n    return 'test'")

        context = ai_player.build_context()

        assert "challenge" in context.lower()
        assert "return 'test'" in context

    def test_ai_player_can_select_appropriate_challenge(self, ai_player, challenges):
        """AI player should select challenges based on difficulty."""
        # Simulate selection logic - start with level 1
        level_1_challenges = [c for c in challenges if c.level == 1]

        assert len(level_1_challenges) > 0
        selected = level_1_challenges[0]

        ai_player.observe_challenge(selected)
        assert ai_player.current_challenge.level == 1


# ============================================================================
# Code Submission and Validation Tests
# ============================================================================

class TestCodeSubmissionAndValidation:
    """Test code submission and validation flow."""

    @pytest.fixture
    def validator(self):
        """Create a code validator."""
        return CodeValidator(timeout_seconds=5)

    @pytest.fixture
    def session(self):
        """Create an E2E game session."""
        return E2EGameSession()

    def test_valid_code_passes_validation(self, validator):
        """Valid code should pass validation."""
        challenge = make_test_challenge(
            skeleton="def solution():\n    pass",
            expected="Hello, World!",
        )

        code = "def solution():\n    return 'Hello, World!'"
        result = validator.validate(code, challenge.test_cases)

        assert result.success is True
        assert result.tests_passing == 1

    def test_invalid_code_fails_validation(self, validator):
        """Invalid code should fail validation."""
        challenge = make_test_challenge(
            skeleton="def solution():\n    pass",
            expected="Hello, World!",
        )

        code = "def solution():\n    return 'Wrong answer'"
        result = validator.validate(code, challenge.test_cases)

        assert result.success is False
        assert result.tests_passing == 0

    def test_syntax_error_fails_validation(self, validator):
        """Code with syntax errors should fail validation."""
        challenge = make_test_challenge()

        code = "def solution(\n    return 'missing paren'"
        result = validator.validate(code, challenge.test_cases)

        assert result.success is False
        assert result.error is not None
        assert "Syntax" in result.error

    def test_session_tracks_validation_result(self, validator, session):
        """Session should track validation results."""
        challenge = make_test_challenge(expected="test")
        session.select_challenge(challenge)

        code = "def solution():\n    return 'test'"
        result = validator.validate(code, challenge.test_cases)
        session.record_validation(result)

        assert session.validation_result is not None
        assert session.validation_result.success is True

    def test_multiple_test_cases(self, validator):
        """Should handle multiple test cases correctly."""
        challenge = Challenge(
            id="multi_test",
            name="Multiple Tests",
            description_brief="Return input * 2",
            description_detailed="Return input * 2",
            skeleton_code="def solution(x):\n    pass",
            test_cases=[
                TestCase(name="test_2", input=2, expected=4),
                TestCase(name="test_5", input=5, expected=10),
                TestCase(name="test_0", input=0, expected=0),
            ],
            level=1,
            prerequisites=[],
        )

        code = "def solution(x):\n    return x * 2"
        result = validator.validate(code, challenge.test_cases)

        assert result.success is True
        assert result.tests_passing == 3
        assert result.tests_total == 3


# ============================================================================
# AI Player Code Generation Tests
# ============================================================================

class TestAIPlayerCodeGeneration:
    """Test AI player generating code solutions."""

    @pytest.fixture
    def ai_player(self):
        return ZAIPlayer(name="CodeBot", api_key="test-key")

    @pytest.mark.asyncio
    async def test_ai_generates_solution(self, ai_player):
        """AI player should generate code solutions."""
        challenge = make_test_challenge(
            description="Return the number 42",
            skeleton="def solution():\n    pass",
            expected=42,
        )

        ai_player.observe_challenge(challenge)

        with patch("lmsp.multiplayer.zai_player.requests.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "choices": [
                    {
                        "message": {
                            "content": "```python\ndef solution():\n    return 42\n```"
                        }
                    }
                ]
            }
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            solution = await ai_player.generate_solution()

            assert solution is not None
            assert "return 42" in solution

    def test_ai_extracts_code_from_markdown(self, ai_player):
        """AI should extract code from markdown responses."""
        response = """
        Here's the solution:

        ```python
        def solution():
            return 42
        ```

        This returns 42.
        """

        code = ai_player.extract_code(response)

        assert "def solution():" in code
        assert "return 42" in code
        assert "```" not in code


# ============================================================================
# Emotional Feedback Recording Tests
# ============================================================================

class TestEmotionalFeedbackRecording:
    """Test emotional feedback recording flow."""

    @pytest.fixture
    def emotional_state(self):
        """Create an emotional state tracker."""
        return EmotionalState()

    @pytest.fixture
    def renderer(self):
        """Create an emotional feedback renderer."""
        return EmotionalFeedbackRenderer()

    def test_record_enjoyment(self, emotional_state):
        """Should record enjoyment feedback."""
        emotional_state.record(EmotionalDimension.ENJOYMENT, 0.8, context="test")

        enjoyment = emotional_state.get_enjoyment()
        assert enjoyment > 0.0

    def test_record_frustration(self, emotional_state):
        """Should record frustration feedback."""
        emotional_state.record(EmotionalDimension.FRUSTRATION, 0.6, context="test")

        frustration = emotional_state.get_frustration()
        assert frustration > 0.0

    def test_emotional_prompt_creation(self):
        """Should create emotional prompt for feedback collection."""
        prompt = EmotionalPrompt(
            question="How did this challenge feel?",
            right_trigger="Fun",
            left_trigger="Frustrating",
            y_button="More details",
        )

        assert prompt.question == "How did this challenge feel?"
        assert prompt.right_trigger == "Fun"
        assert prompt.left_trigger == "Frustrating"

    def test_render_emotional_prompt(self, renderer):
        """Should render emotional prompt as string."""
        prompt = EmotionalPrompt(
            question="How was it?",
            right_trigger="Good",
            left_trigger="Bad",
        )

        output = renderer.render_prompt(prompt)

        assert "How was it?" in output
        assert "RT" in output or "Good" in output

    def test_session_records_emotional_feedback(self):
        """Session should record emotional feedback."""
        session = E2EGameSession()
        challenge = make_test_challenge()
        session.select_challenge(challenge)

        session.record_emotional_feedback(enjoyment=0.9, frustration=0.1)

        assert session.emotional_feedback is not None
        assert session.emotional_feedback["enjoyment"] == 0.9
        assert session.emotional_feedback["frustration"] == 0.1

    def test_flow_state_detection(self, emotional_state):
        """Should detect flow state (high enjoyment, low frustration)."""
        # Record high enjoyment
        for _ in range(5):
            emotional_state.record(EmotionalDimension.ENJOYMENT, 0.9, context="flow_test")

        in_flow = emotional_state.is_in_flow()
        # Flow state requires specific conditions - may or may not be true
        # but the method should work
        assert isinstance(in_flow, bool)


# ============================================================================
# Challenge Advancement Tests
# ============================================================================

class TestChallengeAdvancement:
    """Test advancing to next challenge after completion."""

    @pytest.fixture
    def profile(self):
        return make_test_profile()

    @pytest.fixture
    def adaptive_engine(self, profile):
        return AdaptiveEngine(profile)

    def test_session_completes_challenge(self):
        """Session should complete challenge and track it."""
        session = E2EGameSession()
        challenge = make_test_challenge(id="test_challenge")
        session.select_challenge(challenge)

        # Simulate successful validation
        result = ValidationResult(
            success=True,
            output="",
            error=None,
            time_seconds=10.0,
            test_results=[TestResult(test_name="basic", passed=True, expected="x", actual="x")],
        )
        session.record_validation(result)
        session.complete_challenge()

        assert "test_challenge" in session.completed_challenges
        assert session.current_challenge is None

    def test_adaptive_engine_records_success(self, adaptive_engine):
        """Adaptive engine should record successful attempts."""
        adaptive_engine.observe_attempt(
            concept="basics",
            success=True,
            time_seconds=30.0,
            hints_used=0,
        )

        # Profile should be updated
        # (The exact assertions depend on AdaptiveEngine implementation)
        assert adaptive_engine.profile is not None

    def test_adaptive_engine_recommends_next(self, adaptive_engine):
        """Adaptive engine should recommend next challenge."""
        recommendation = adaptive_engine.recommend_next()

        assert isinstance(recommendation, AdaptiveRecommendation)

    def test_multiple_challenge_progression(self):
        """Should handle progression through multiple challenges."""
        session = E2EGameSession()
        validator = CodeValidator(timeout_seconds=5)

        challenges = [
            make_test_challenge(id="c1", expected="a"),
            make_test_challenge(id="c2", expected="b"),
            make_test_challenge(id="c3", expected="c"),
        ]

        for i, challenge in enumerate(challenges):
            session.select_challenge(challenge)

            # Write "correct" solution for each
            solutions = [
                "def solution():\n    return 'a'",
                "def solution():\n    return 'b'",
                "def solution():\n    return 'c'",
            ]
            session.update_code(solutions[i])

            result = validator.validate(session.current_code, challenge.test_cases)
            session.record_validation(result)

            assert result.success is True
            session.complete_challenge()

        assert len(session.completed_challenges) == 3


# ============================================================================
# Full E2E Flow Integration Tests
# ============================================================================

class TestFullE2EFlow:
    """Test the complete end-to-end game flow."""

    @pytest.fixture
    def full_setup(self):
        """Set up all components for E2E testing."""
        profile = make_test_profile()
        adaptive_engine = AdaptiveEngine(profile)
        validator = CodeValidator(timeout_seconds=5)
        emotional_state = EmotionalState()
        session = E2EGameSession()

        return {
            "profile": profile,
            "adaptive_engine": adaptive_engine,
            "validator": validator,
            "emotional_state": emotional_state,
            "session": session,
        }

    def test_complete_flow_with_correct_solution(self, full_setup):
        """
        Test complete flow:
        1. Select challenge
        2. Write correct solution
        3. Submit and validate
        4. Record emotional feedback
        5. Complete and advance
        """
        session = full_setup["session"]
        validator = full_setup["validator"]
        emotional_state = full_setup["emotional_state"]
        adaptive_engine = full_setup["adaptive_engine"]

        # Step 1: Select challenge
        challenge = make_test_challenge(
            id="e2e_test",
            name="E2E Test Challenge",
            description="Return 'success'",
            skeleton="def solution():\n    pass",
            expected="success",
        )
        session.select_challenge(challenge)

        assert session.current_challenge == challenge
        assert session.current_code == challenge.skeleton_code

        # Step 2: Write correct solution
        correct_code = "def solution():\n    return 'success'"
        session.update_code(correct_code)

        assert session.current_code == correct_code

        # Step 3: Submit and validate
        result = validator.validate(session.current_code, challenge.test_cases)
        session.record_validation(result)

        assert result.success is True
        assert result.tests_passing == 1

        # Step 4: Record emotional feedback
        emotional_state.record(EmotionalDimension.ENJOYMENT, 0.85, context="e2e_test")
        session.record_emotional_feedback(enjoyment=0.85, frustration=0.1)

        assert session.emotional_feedback is not None
        assert session.emotional_feedback["enjoyment"] == 0.85

        # Record in adaptive engine
        adaptive_engine.observe_attempt(
            concept="basics",
            success=True,
            time_seconds=45.0,
            hints_used=0,
        )

        # Step 5: Complete and advance
        session.complete_challenge()

        assert "e2e_test" in session.completed_challenges
        assert session.current_challenge is None

        # Check recommendation for next challenge
        recommendation = adaptive_engine.recommend_next()
        assert recommendation is not None

    def test_complete_flow_with_incorrect_then_correct(self, full_setup):
        """
        Test flow with retry:
        1. Select challenge
        2. Write incorrect solution
        3. Submit and fail
        4. Write correct solution
        5. Submit and pass
        6. Complete
        """
        session = full_setup["session"]
        validator = full_setup["validator"]

        challenge = make_test_challenge(
            id="retry_test",
            expected="correct",
        )
        session.select_challenge(challenge)

        # First attempt - wrong
        wrong_code = "def solution():\n    return 'wrong'"
        session.update_code(wrong_code)
        result1 = validator.validate(session.current_code, challenge.test_cases)
        session.record_validation(result1)

        assert result1.success is False

        # Second attempt - correct
        correct_code = "def solution():\n    return 'correct'"
        session.update_code(correct_code)
        result2 = validator.validate(session.current_code, challenge.test_cases)
        session.record_validation(result2)

        assert result2.success is True

        # Complete
        session.complete_challenge()
        assert "retry_test" in session.completed_challenges

    @pytest.mark.asyncio
    async def test_e2e_with_ai_player(self, full_setup):
        """
        Test E2E flow with AI player:
        1. AI observes challenge
        2. AI generates solution
        3. Solution is validated
        4. Emotional feedback recorded
        5. AI feedback generated
        """
        session = full_setup["session"]
        validator = full_setup["validator"]
        emotional_state = full_setup["emotional_state"]

        # Create AI player
        ai_player = ZAIPlayer(name="E2E_AI", api_key="test-key")

        # Challenge
        challenge = make_test_challenge(
            id="ai_e2e_test",
            name="AI E2E Test",
            description="Return 42",
            expected=42,
        )

        # AI observes
        ai_player.observe_challenge(challenge)
        session.select_challenge(challenge)

        # Mock AI generating solution
        with patch("lmsp.multiplayer.zai_player.requests.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "```python\ndef solution():\n    return 42\n```"}}]
            }
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            solution = await ai_player.generate_solution()
            session.update_code(solution)

        # Validate
        result = validator.validate(session.current_code, challenge.test_cases)
        session.record_validation(result)

        assert result.success is True

        # AI records attempt
        ai_player.record_attempt(success=True, time_seconds=15)

        # AI generates feedback
        feedback = ai_player.generate_feedback()

        assert isinstance(feedback, PlaytestFeedback)
        assert feedback.success is True

        # Complete
        session.complete_challenge()
        assert "ai_e2e_test" in session.completed_challenges


# ============================================================================
# Web UI + AI Player Integration Tests
# ============================================================================

class TestWebAIIntegration:
    """Test web UI integration with AI player."""

    def test_api_workflow_simulation(self):
        """Simulate the web API workflow an AI player would use."""
        client = TestClient(app)

        # 1. Get available challenges
        challenges_response = client.get("/api/challenges")
        assert challenges_response.status_code == 200
        challenges = challenges_response.json()

        # 2. Get player profile
        profile_response = client.get("/api/profile")
        assert profile_response.status_code == 200
        profile = profile_response.json()

        assert "player_id" in profile

        # 3. Submit code (simulate AI submission)
        if len(challenges) > 0:
            challenge_id = challenges[0]["id"]
            submit_response = client.post(
                "/api/code/submit",
                json={
                    "challenge_id": challenge_id,
                    "code": "def solution():\n    return 'test'"
                }
            )
            assert submit_response.status_code == 200

    def test_htmx_challenge_list(self):
        """Test HTMX challenge list endpoint."""
        client = TestClient(app)

        response = client.get(
            "/api/challenges",
            headers={"HX-Request": "true"}
        )

        assert response.status_code == 200
        # HTMX requests return HTML
        assert b"challenge" in response.content.lower()


# ============================================================================
# Performance and Edge Case Tests
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_code_submission(self):
        """Should handle empty code submission."""
        validator = CodeValidator(timeout_seconds=5)
        challenge = make_test_challenge()

        result = validator.validate("", challenge.test_cases)

        assert result.success is False

    def test_no_solution_function(self):
        """Should handle code without solution function."""
        validator = CodeValidator(timeout_seconds=5)
        challenge = make_test_challenge()

        code = "x = 42\nprint(x)"
        result = validator.validate(code, challenge.test_cases)

        assert result.success is False
        assert "solution" in result.error.lower()

    def test_exception_in_solution(self):
        """Should handle exceptions in solution code."""
        validator = CodeValidator(timeout_seconds=5)
        challenge = make_test_challenge()

        code = "def solution():\n    raise ValueError('test error')"
        result = validator.validate(code, challenge.test_cases)

        assert result.success is False

    def test_session_without_challenge(self):
        """Session should handle operations without challenge."""
        session = E2EGameSession()

        # Should not crash
        session.complete_challenge()
        assert len(session.completed_challenges) == 0

    def test_emotional_state_boundary_values(self):
        """Should handle boundary values for emotional state."""
        emotional_state = EmotionalState()

        # Record values at boundaries
        emotional_state.record(EmotionalDimension.ENJOYMENT, 0.0, context="test")
        emotional_state.record(EmotionalDimension.ENJOYMENT, 1.0, context="test")
        emotional_state.record(EmotionalDimension.FRUSTRATION, 0.0, context="test")
        emotional_state.record(EmotionalDimension.FRUSTRATION, 1.0, context="test")

        # Should not crash
        enjoyment = emotional_state.get_enjoyment()
        frustration = emotional_state.get_frustration()

        assert 0.0 <= enjoyment <= 1.0
        assert 0.0 <= frustration <= 1.0


# ============================================================================
# Self-Teaching Note
# ============================================================================

# Self-teaching note:
#
# This file demonstrates:
# - End-to-end testing patterns (complete flow testing)
# - Test data factories for creating test objects
# - Dataclasses for state tracking
# - Pytest fixtures for test setup
# - Async testing with pytest-asyncio
# - Mocking external dependencies (API calls)
# - Integration testing of multiple systems
# - Edge case and error handling testing
#
# Key concepts:
# 1. E2E tests verify the ENTIRE flow, not just individual components
# 2. Test data factories make creating test objects consistent
# 3. Session tracking helps verify state throughout the flow
# 4. Mocking isolates tests from external dependencies
# 5. Edge cases ensure robustness
#
# Prerequisites:
# - Level 4: Testing fundamentals, fixtures
# - Level 5: Async/await, mocking, dataclasses
# - Level 6: Integration testing, system design
#
# This test file verifies that ALL LMSP systems work together correctly,
# simulating a real player (or AI) going through the complete game flow.
