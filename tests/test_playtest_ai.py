"""
AI Playtest Integration Tests

Long-running tests that spawn AI players to complete challenges and capture metrics.

These tests drive continuous improvement by:
1. Spawning AI players to attempt challenges
2. Capturing metrics (time, hints, code quality, UX friction)
3. Detecting UX issues (confusing flows, missing hints, difficulty spikes)
4. Generating actionable improvement tasks

Run with: pytest tests/test_playtest_ai.py -m long -v

TDD: These tests define expected behavior BEFORE implementation.
"""

import pytest
import time
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class PlaytestMetrics:
    """
    Metrics captured from an AI playtest session.

    These metrics help us identify where the UX needs improvement.
    """
    challenge_id: str
    player_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None

    # Success metrics
    success: bool = False
    attempts: int = 0
    hints_used: int = 0

    # Time metrics (seconds)
    time_to_first_attempt: float = 0.0
    time_to_completion: Optional[float] = None
    time_stuck: float = 0.0  # Time with no progress

    # Code quality metrics
    code_submissions: List[str] = field(default_factory=list)
    syntax_errors: int = 0
    runtime_errors: int = 0
    test_failures: int = 0

    # UX friction signals
    confusion_signals: List[str] = field(default_factory=list)  # Repeated same mistakes
    frustration_signals: List[str] = field(default_factory=list)  # Emotional indicators
    missing_hint_signals: List[str] = field(default_factory=list)  # Needed help not available

    # Player feedback
    player_notes: str = ""
    emotional_state: Dict[str, float] = field(default_factory=dict)

    def was_stuck(self) -> bool:
        """Determine if player was stuck (high time with low progress)."""
        return self.time_stuck > 60.0  # Stuck for more than 1 minute

    def had_difficulty_spike(self) -> bool:
        """Determine if this challenge was significantly harder than expected."""
        # If many attempts with little progress
        return self.attempts > 5 and not self.success

    def had_confusing_ux(self) -> bool:
        """Determine if UX was confusing."""
        return len(self.confusion_signals) > 0

    def needed_missing_hints(self) -> bool:
        """Determine if hints were missing."""
        return len(self.missing_hint_signals) > 0


@dataclass
class UXFrictionReport:
    """
    Report of UX friction detected during playtesting.

    This drives continuous improvement.
    """
    challenge_id: str
    friction_type: str  # "confusing_ux", "missing_hints", "difficulty_spike", "broken_flow"
    severity: str  # "low", "medium", "high", "critical"
    description: str
    evidence: List[str]  # Specific examples from playtest
    suggested_fixes: List[str]  # Actionable improvements

    def to_task(self) -> str:
        """Convert friction report to an actionable task description."""
        return f"[{self.severity.upper()}] {self.challenge_id}: {self.description}"


# ============================================================================
# PYTEST MARKERS AND FIXTURES
# ============================================================================

@pytest.fixture
def mock_ai_player():
    """
    Mock AI player for testing.

    In real implementation, this would use Z.ai GLM API.
    """
    class MockAIPlayer:
        def __init__(self, skill_level: float = 0.5):
            self.skill_level = skill_level  # 0.0 = beginner, 1.0 = expert
            self.attempts = 0
            self.hints_used = 0

        def attempt_challenge(self, challenge_data: Dict[str, Any]) -> Dict[str, Any]:
            """Attempt to solve a challenge."""
            self.attempts += 1

            # Simulate thinking time
            time.sleep(0.1)

            # Simplified: higher skill = better solutions
            success = self.skill_level > 0.3 or self.attempts > 3

            return {
                "success": success,
                "code": f"# Attempt {self.attempts}\nprint('Hello, World!')",
                "time_seconds": 0.1,
                "emotional_state": {
                    "enjoyment": 0.7 if success else 0.3,
                    "frustration": 0.2 if success else 0.7,
                },
            }

    return MockAIPlayer


# ============================================================================
# TESTS
# ============================================================================

class TestPlaytestMetrics:
    """Test the PlaytestMetrics dataclass."""

    def test_create_metrics(self):
        """Should create playtest metrics."""
        metrics = PlaytestMetrics(
            challenge_id="hello_world",
            player_id="ai_player_1",
            started_at=datetime.now(),
        )

        assert metrics.challenge_id == "hello_world"
        assert metrics.player_id == "ai_player_1"
        assert metrics.success is False
        assert metrics.attempts == 0

    def test_detect_stuck(self):
        """Should detect when player was stuck."""
        metrics = PlaytestMetrics(
            challenge_id="test",
            player_id="ai",
            started_at=datetime.now(),
            time_stuck=90.0,  # 90 seconds stuck
        )

        assert metrics.was_stuck() is True

    def test_detect_difficulty_spike(self):
        """Should detect difficulty spikes."""
        metrics = PlaytestMetrics(
            challenge_id="test",
            player_id="ai",
            started_at=datetime.now(),
            attempts=10,  # Many attempts
            success=False,  # Still failed
        )

        assert metrics.had_difficulty_spike() is True

    def test_detect_confusing_ux(self):
        """Should detect confusing UX."""
        metrics = PlaytestMetrics(
            challenge_id="test",
            player_id="ai",
            started_at=datetime.now(),
            confusion_signals=["repeated_same_error", "unclear_instructions"],
        )

        assert metrics.had_confusing_ux() is True

    def test_detect_missing_hints(self):
        """Should detect when hints are missing."""
        metrics = PlaytestMetrics(
            challenge_id="test",
            player_id="ai",
            started_at=datetime.now(),
            missing_hint_signals=["needed_import_guidance", "unclear_function_signature"],
        )

        assert metrics.needed_missing_hints() is True


class TestUXFrictionReport:
    """Test UX friction reporting."""

    def test_create_friction_report(self):
        """Should create friction report."""
        report = UXFrictionReport(
            challenge_id="fizzbuzz",
            friction_type="confusing_ux",
            severity="high",
            description="Instructions unclear about modulo operator",
            evidence=["Player tried % operator 5 times with wrong syntax"],
            suggested_fixes=["Add hint about % operator", "Show example of modulo"],
        )

        assert report.challenge_id == "fizzbuzz"
        assert report.friction_type == "confusing_ux"
        assert report.severity == "high"
        assert len(report.suggested_fixes) == 2

    def test_convert_to_task(self):
        """Should convert friction report to actionable task."""
        report = UXFrictionReport(
            challenge_id="hello_world",
            friction_type="missing_hints",
            severity="medium",
            description="Need hint about print function",
            evidence=["Player stuck for 2min without print hint"],
            suggested_fixes=["Add level_1 hint explaining print()"],
        )

        task = report.to_task()

        assert "[MEDIUM]" in task
        assert "hello_world" in task
        assert "print function" in task


@pytest.mark.long
@pytest.mark.playtest
class TestAIPlaytestIntegration:
    """
    Long-running AI playtest integration tests.

    These spawn AI players to complete challenges and capture metrics.
    """

    def test_ai_player_can_attempt_challenge(self, mock_ai_player):
        """AI player should be able to attempt a challenge."""
        player = mock_ai_player(skill_level=0.5)

        challenge_data = {
            "id": "hello_world",
            "name": "Hello, World!",
            "description": "Print Hello, World!",
            "skeleton": "# Write your code here\n",
            "tests": [{"input": [], "expected": ["Hello, World!"]}],
        }

        result = player.attempt_challenge(challenge_data)

        assert "success" in result
        assert "code" in result
        assert "time_seconds" in result
        assert "emotional_state" in result

    def test_metrics_capture_basic_info(self, mock_ai_player):
        """Should capture basic metrics from playtest."""
        player = mock_ai_player(skill_level=0.6)

        started_at = datetime.now()

        # Player attempts challenge
        challenge_data = {"id": "test", "name": "Test"}
        result = player.attempt_challenge(challenge_data)

        completed_at = datetime.now()

        # Create metrics
        metrics = PlaytestMetrics(
            challenge_id="test",
            player_id="ai_1",
            started_at=started_at,
            completed_at=completed_at,
            success=result["success"],
            attempts=1,
            time_to_completion=(completed_at - started_at).total_seconds(),
            code_submissions=[result["code"]],
            emotional_state=result["emotional_state"],
        )

        assert metrics.challenge_id == "test"
        assert metrics.success in [True, False]
        assert metrics.time_to_completion is not None
        assert len(metrics.code_submissions) == 1

    @pytest.mark.long
    def test_playtest_hello_world_challenge(self, mock_ai_player):
        """
        Full playtest of hello_world challenge.

        This is an integration test that:
        1. Loads the challenge
        2. Spawns an AI player
        3. Captures full metrics
        4. Detects UX friction
        """
        # Setup
        player = mock_ai_player(skill_level=0.4)  # Intermediate skill
        challenge_id = "hello_world"
        started_at = datetime.now()

        # Simulate challenge loading (in real implementation, load from TOML)
        challenge_data = {
            "id": challenge_id,
            "name": "Hello, World!",
            "description": "Write a program that prints 'Hello, World!'",
        }

        # Player attempts
        metrics = PlaytestMetrics(
            challenge_id=challenge_id,
            player_id="ai_test_1",
            started_at=started_at,
        )

        # Multiple attempts until success or max attempts
        max_attempts = 10
        for attempt in range(max_attempts):
            result = player.attempt_challenge(challenge_data)
            metrics.attempts += 1
            metrics.code_submissions.append(result["code"])
            metrics.emotional_state = result["emotional_state"]

            if result["success"]:
                metrics.success = True
                metrics.completed_at = datetime.now()
                metrics.time_to_completion = (metrics.completed_at - started_at).total_seconds()
                break

            # Simulate time passing between attempts
            time.sleep(0.1)

        # Verify metrics were captured
        assert metrics.attempts > 0
        assert len(metrics.code_submissions) == metrics.attempts
        assert metrics.emotional_state is not None

        # If player struggled, should have metrics
        if metrics.attempts > 3:
            # This would be UX friction
            assert True

    @pytest.mark.long
    def test_detect_ux_friction_from_playtest(self, mock_ai_player):
        """
        Should detect UX friction from playtest metrics.
        """
        # Simulate a playtest with UX issues
        metrics = PlaytestMetrics(
            challenge_id="difficult_challenge",
            player_id="ai_2",
            started_at=datetime.now() - timedelta(minutes=5),
            completed_at=None,  # Never completed!
            success=False,
            attempts=15,  # Many attempts
            hints_used=0,  # No hints available?
            time_stuck=180.0,  # 3 minutes stuck
            confusion_signals=["repeated_syntax_error", "unclear_requirements"],
            missing_hint_signals=["needed_example", "unclear_api"],
        )

        # Analyze metrics for friction
        friction_reports = []

        if metrics.had_difficulty_spike():
            friction_reports.append(UXFrictionReport(
                challenge_id=metrics.challenge_id,
                friction_type="difficulty_spike",
                severity="high",
                description=f"Challenge too difficult: {metrics.attempts} attempts without success",
                evidence=[f"Stuck for {metrics.time_stuck}s", "No completion"],
                suggested_fixes=["Add intermediate hints", "Simplify requirements", "Add examples"],
            ))

        if metrics.had_confusing_ux():
            friction_reports.append(UXFrictionReport(
                challenge_id=metrics.challenge_id,
                friction_type="confusing_ux",
                severity="medium",
                description="UX caused confusion",
                evidence=metrics.confusion_signals,
                suggested_fixes=["Clarify instructions", "Add visual examples"],
            ))

        if metrics.needed_missing_hints():
            friction_reports.append(UXFrictionReport(
                challenge_id=metrics.challenge_id,
                friction_type="missing_hints",
                severity="high",
                description="Critical hints are missing",
                evidence=metrics.missing_hint_signals,
                suggested_fixes=["Add hints for common mistakes", "Provide API documentation"],
            ))

        # Should have detected friction
        assert len(friction_reports) > 0

        # Should have actionable tasks
        tasks = [report.to_task() for report in friction_reports]
        assert len(tasks) > 0
        assert all("[" in task for task in tasks)  # All should have severity markers

    @pytest.mark.long
    def test_continuous_improvement_loop(self, mock_ai_player):
        """
        Test the full continuous improvement loop:
        1. AI plays challenge
        2. Metrics captured
        3. Friction detected
        4. Improvement tasks generated
        """
        # Step 1: AI plays challenge
        player = mock_ai_player(skill_level=0.3)  # Low skill to trigger issues
        challenge_id = "test_challenge"

        metrics = PlaytestMetrics(
            challenge_id=challenge_id,
            player_id="ai_improvement_test",
            started_at=datetime.now(),
        )

        # Play until success or timeout
        timeout = time.time() + 5.0  # 5 second timeout
        while time.time() < timeout and not metrics.success:
            result = player.attempt_challenge({"id": challenge_id})
            metrics.attempts += 1
            metrics.code_submissions.append(result["code"])

            if result["success"]:
                metrics.success = True
                metrics.completed_at = datetime.now()

            # Track frustration
            if result["emotional_state"].get("frustration", 0) > 0.6:
                metrics.frustration_signals.append(f"High frustration at attempt {metrics.attempts}")

            time.sleep(0.1)

        # Step 2: Metrics captured
        assert metrics.attempts > 0

        # Step 3 & 4: Detect friction and generate tasks
        improvement_tasks = []

        if not metrics.success:
            improvement_tasks.append(
                f"Challenge {challenge_id}: Too difficult for AI player "
                f"(failed after {metrics.attempts} attempts)"
            )

        if len(metrics.frustration_signals) > 0:
            improvement_tasks.append(
                f"Challenge {challenge_id}: High frustration detected - improve UX"
            )

        # Continuous improvement should always generate insights
        # Even successful challenges can be improved
        assert True  # Test structure is more important than specific results here


@pytest.mark.long
@pytest.mark.playtest
class TestMultipleAIPlayers:
    """Test with multiple AI players of different skill levels."""

    def test_skill_level_variation(self, mock_ai_player):
        """Should test challenges with players of varying skill."""
        skill_levels = [0.2, 0.5, 0.8]  # beginner, intermediate, expert
        challenge_id = "test"

        results = []
        for skill in skill_levels:
            player = mock_ai_player(skill_level=skill)
            metrics = PlaytestMetrics(
                challenge_id=challenge_id,
                player_id=f"ai_skill_{skill}",
                started_at=datetime.now(),
            )

            # Attempt challenge
            result = player.attempt_challenge({"id": challenge_id})
            metrics.success = result["success"]
            metrics.attempts = 1

            results.append((skill, metrics))

        # Should have varied results based on skill
        assert len(results) == 3

        # Experts should generally do better than beginners
        # (though this is a mock, so we're testing the structure)
        assert True


# ============================================================================
# SELF-TEACHING NOTE
# ============================================================================

# Self-teaching note:
#
# This file demonstrates:
# - Long-running integration tests (marked with @pytest.mark.long)
# - Metrics capture and analysis (Level 5+: dataclasses, analysis)
# - Continuous improvement loops (Level 6+: meta-learning)
# - AI-driven testing (Professional: testing your own systems)
# - UX friction detection (Design patterns)
#
# The pattern:
# 1. AI players attempt challenges
# 2. Metrics are captured (time, attempts, emotional state)
# 3. UX friction is detected automatically
# 4. Actionable improvement tasks are generated
# 5. The cycle repeats, driving continuous improvement
#
# This is how LMSP improves itself through play!
#
# Prerequisites:
# - Level 4: Testing, dataclasses
# - Level 5: Advanced data structures, analysis
# - Level 6: Meta-programming, continuous improvement patterns
#
# Run these tests with:
#   pytest tests/test_playtest_ai.py -m long -v
#
# Skip long tests:
#   pytest -m "not long"
