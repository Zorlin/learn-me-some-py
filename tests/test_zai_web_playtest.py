"""
Tests for AI-Driven UX Issue Discovery System

TDD: These tests define expected behavior for the ZAI player
navigating web UI via Playwright, detecting confusion/friction points,
capturing screenshots at struggle moments, and generating UX improvements.

Tests cover:
1. WebPlaytester initialization and configuration
2. Playwright-based navigation through web UI
3. Confusion and friction point detection
4. Screenshot capture at struggle moments
5. UX improvement suggestion generation
6. Integration with existing playtest analyzer
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
import tempfile

# Import from existing modules
from lmsp.multiplayer.zai_player import ZAIPlayer, PlaytestFeedback
from lmsp.multiplayer.player_zero.tas.recorder import (
    PlaytestRecorder,
    EventType,
    PlaytestEvent,
)


class TestWebPlaytesterInit:
    """Test WebPlaytester initialization."""

    def test_basic_initialization(self):
        """WebPlaytester should initialize with required config."""
        from lmsp.testing.web_playtester import WebPlaytester

        playtester = WebPlaytester(
            zai_player=Mock(spec=ZAIPlayer),
            base_url="http://localhost:8000",
        )

        assert playtester.base_url == "http://localhost:8000"
        assert playtester.screenshots_dir is not None
        assert playtester.friction_threshold == 0.5  # Default

    def test_custom_screenshots_dir(self):
        """Should allow custom screenshots directory."""
        from lmsp.testing.web_playtester import WebPlaytester

        with tempfile.TemporaryDirectory() as tmpdir:
            playtester = WebPlaytester(
                zai_player=Mock(spec=ZAIPlayer),
                base_url="http://localhost:8000",
                screenshots_dir=Path(tmpdir),
            )
            assert playtester.screenshots_dir == Path(tmpdir)

    def test_custom_friction_threshold(self):
        """Should allow custom friction threshold."""
        from lmsp.testing.web_playtester import WebPlaytester

        playtester = WebPlaytester(
            zai_player=Mock(spec=ZAIPlayer),
            base_url="http://localhost:8000",
            friction_threshold=0.8,
        )
        assert playtester.friction_threshold == 0.8


class TestPageNavigation:
    """Test Playwright-based page navigation."""

    @pytest.fixture
    def playtester(self):
        from lmsp.testing.web_playtester import WebPlaytester

        return WebPlaytester(
            zai_player=Mock(spec=ZAIPlayer),
            base_url="http://localhost:8000",
        )

    def test_navigation_event_recorded(self, playtester):
        """Should record navigation events."""
        playtester.record_navigation("/challenges/hello_world")

        assert len(playtester.navigation_history) == 1
        assert playtester.navigation_history[0]["url"] == "/challenges/hello_world"

    def test_element_interaction_recorded(self, playtester):
        """Should record element interactions."""
        playtester.record_interaction(
            element_type="button",
            element_id="start-btn",
            action="click",
        )

        assert len(playtester.interaction_history) == 1
        assert playtester.interaction_history[0]["element_type"] == "button"
        assert playtester.interaction_history[0]["action"] == "click"

    def test_wait_time_tracked(self, playtester):
        """Should track wait times between interactions."""
        playtester.record_interaction(element_type="button", action="click")
        # Simulate delay
        import time
        time.sleep(0.1)
        playtester.record_interaction(element_type="input", action="type")

        assert len(playtester.interaction_history) == 2
        # Second interaction should have duration
        assert playtester.interaction_history[1].get("duration_since_last", 0) >= 0.1


class TestFrictionDetection:
    """Test confusion and friction point detection."""

    @pytest.fixture
    def playtester(self):
        from lmsp.testing.web_playtester import WebPlaytester

        return WebPlaytester(
            zai_player=Mock(spec=ZAIPlayer),
            base_url="http://localhost:8000",
        )

    def test_detect_rapid_clicks(self, playtester):
        """Should detect rapid clicking as friction."""
        # Simulate rapid clicks (5+ clicks in 2 seconds)
        for _ in range(6):
            playtester.record_interaction(
                element_type="button",
                action="click",
                timestamp=0.3,  # 300ms apart
            )

        friction_points = playtester.detect_friction_points()

        assert len(friction_points) > 0
        assert any(fp["type"] == "rapid_clicks" for fp in friction_points)

    def test_detect_confusion_navigation(self, playtester):
        """Should detect back-and-forth navigation as confusion."""
        # Simulate confused navigation pattern
        playtester.record_navigation("/page1")
        playtester.record_navigation("/page2")
        playtester.record_navigation("/page1")  # Going back
        playtester.record_navigation("/page2")  # Going forward again

        friction_points = playtester.detect_friction_points()

        assert any(fp["type"] == "navigation_confusion" for fp in friction_points)

    def test_detect_long_wait(self, playtester):
        """Should detect long waits as potential confusion."""
        playtester.record_interaction(
            element_type="button",
            action="click",
        )
        # Record interaction with long gap
        playtester.record_interaction(
            element_type="button",
            action="click",
            duration_since_last=30.0,  # 30 seconds
        )

        friction_points = playtester.detect_friction_points()

        assert any(fp["type"] == "long_wait" for fp in friction_points)

    def test_detect_failed_submission(self, playtester):
        """Should detect repeated failed submissions."""
        for _ in range(3):
            playtester.record_submission(
                challenge_id="hello_world",
                success=False,
                error="SyntaxError",
            )

        friction_points = playtester.detect_friction_points()

        assert any(fp["type"] == "repeated_failures" for fp in friction_points)

    def test_calculate_friction_score(self, playtester):
        """Should calculate overall friction score."""
        # Add some friction indicators
        playtester.record_submission(challenge_id="test", success=False)
        playtester.record_submission(challenge_id="test", success=False)

        score = playtester.calculate_friction_score()

        assert 0.0 <= score <= 1.0
        assert score > 0.0  # Should have some friction


class TestScreenshotCapture:
    """Test screenshot capture at struggle moments."""

    @pytest.fixture
    def playtester(self):
        from lmsp.testing.web_playtester import WebPlaytester

        with tempfile.TemporaryDirectory() as tmpdir:
            playtester = WebPlaytester(
                zai_player=Mock(spec=ZAIPlayer),
                base_url="http://localhost:8000",
                screenshots_dir=Path(tmpdir),
            )
            yield playtester

    def test_screenshot_on_friction(self, playtester):
        """Should trigger screenshot capture on friction detection."""
        playtester.record_friction_screenshot(
            reason="rapid_clicks",
            page_url="/challenges/hello_world",
        )

        assert len(playtester.screenshots) == 1
        assert playtester.screenshots[0]["reason"] == "rapid_clicks"

    def test_screenshot_metadata_recorded(self, playtester):
        """Should record metadata with screenshot."""
        playtester.record_friction_screenshot(
            reason="repeated_failures",
            page_url="/challenges/test",
            element_selector="#code-editor",
        )

        screenshot = playtester.screenshots[0]
        assert screenshot["page_url"] == "/challenges/test"
        assert screenshot["element_selector"] == "#code-editor"
        assert "timestamp" in screenshot

    def test_screenshot_path_generated(self, playtester):
        """Should generate unique screenshot paths."""
        playtester.record_friction_screenshot(reason="test1", page_url="/")
        playtester.record_friction_screenshot(reason="test2", page_url="/")

        paths = [s["path"] for s in playtester.screenshots]
        assert len(set(paths)) == 2  # Should be unique


class TestUXSuggestions:
    """Test UX improvement suggestion generation."""

    @pytest.fixture
    def playtester(self):
        from lmsp.testing.web_playtester import WebPlaytester

        return WebPlaytester(
            zai_player=Mock(spec=ZAIPlayer),
            base_url="http://localhost:8000",
        )

    def test_generate_suggestions_from_friction(self, playtester):
        """Should generate suggestions from friction points."""
        # Add friction points
        playtester.friction_points.append({
            "type": "rapid_clicks",
            "description": "5 rapid clicks on submit button",
            "element": "#submit-btn",
        })

        suggestions = playtester.generate_ux_suggestions()

        assert len(suggestions) > 0
        assert any("click" in s["suggestion"].lower() for s in suggestions)

    def test_suggest_for_repeated_failures(self, playtester):
        """Should suggest improvements for repeated failures."""
        playtester.friction_points.append({
            "type": "repeated_failures",
            "description": "3 consecutive test failures",
            "challenge_id": "hello_world",
        })

        suggestions = playtester.generate_ux_suggestions()

        assert any(
            "hint" in s["suggestion"].lower() or
            "example" in s["suggestion"].lower() or
            "feedback" in s["suggestion"].lower()
            for s in suggestions
        )

    def test_suggest_for_navigation_confusion(self, playtester):
        """Should suggest improvements for navigation confusion."""
        playtester.friction_points.append({
            "type": "navigation_confusion",
            "description": "User navigated back and forth 4 times",
        })

        suggestions = playtester.generate_ux_suggestions()

        assert any(
            "navigation" in s["suggestion"].lower() or
            "breadcrumb" in s["suggestion"].lower() or
            "clear" in s["suggestion"].lower()
            for s in suggestions
        )

    def test_suggestions_have_priority(self, playtester):
        """Suggestions should have priority/severity."""
        playtester.friction_points.append({
            "type": "repeated_failures",
            "description": "Many failures",
        })

        suggestions = playtester.generate_ux_suggestions()

        for suggestion in suggestions:
            assert "priority" in suggestion
            assert suggestion["priority"] in ["low", "medium", "high", "critical"]


class TestPlaytestReport:
    """Test playtest report generation."""

    @pytest.fixture
    def playtester(self):
        from lmsp.testing.web_playtester import WebPlaytester

        return WebPlaytester(
            zai_player=Mock(spec=ZAIPlayer),
            base_url="http://localhost:8000",
        )

    def test_generate_report(self, playtester):
        """Should generate comprehensive playtest report."""
        # Add some data
        playtester.record_navigation("/")
        playtester.record_navigation("/challenges/hello_world")
        playtester.record_interaction(element_type="button", action="click")
        playtester.record_submission(challenge_id="hello_world", success=True)

        report = playtester.generate_report()

        assert "navigation" in report.lower() or "pages_visited" in report
        assert "interaction" in report.lower() or "actions" in report

    def test_report_includes_friction_score(self, playtester):
        """Report should include overall friction score."""
        report = playtester.generate_report()

        assert "friction" in report.lower() or "score" in report.lower()

    def test_report_includes_suggestions(self, playtester):
        """Report should include UX suggestions."""
        playtester.friction_points.append({
            "type": "rapid_clicks",
            "description": "test",
        })

        report = playtester.generate_report()

        assert "suggestion" in report.lower() or "improvement" in report.lower()

    def test_export_to_json(self, playtester):
        """Should export report to JSON."""
        playtester.record_navigation("/")
        playtester.record_submission(challenge_id="test", success=True)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            playtester.export_to_json(Path(f.name))

            # Read back
            with open(f.name, "r") as rf:
                data = json.load(rf)

            assert "navigation_history" in data
            assert "submissions" in data


class TestIntegrationWithRecorder:
    """Test integration with existing PlaytestRecorder."""

    @pytest.fixture
    def playtester(self):
        from lmsp.testing.web_playtester import WebPlaytester

        return WebPlaytester(
            zai_player=Mock(spec=ZAIPlayer),
            base_url="http://localhost:8000",
        )

    def test_convert_to_playtest_events(self, playtester):
        """Should convert navigation/interactions to PlaytestEvents."""
        playtester.record_navigation("/")
        playtester.record_interaction(element_type="button", action="click")

        events = playtester.to_playtest_events()

        assert len(events) >= 2
        assert all(isinstance(e, PlaytestEvent) for e in events)

    def test_compatible_with_recorder(self, playtester):
        """Should be compatible with PlaytestRecorder analysis."""
        playtester.record_navigation("/")
        playtester.record_submission(challenge_id="test", success=False)
        playtester.record_submission(challenge_id="test", success=False)
        playtester.record_submission(challenge_id="test", success=False)

        # Create recorder and add events
        recorder = PlaytestRecorder(
            session_name="web_playtest",
            player_name="zai_bot",
            challenge_id="test",
        )
        recorder.start_recording()

        for event in playtester.to_playtest_events():
            recorder.events.append(event)

        recorder.stop_recording()

        # Should be able to analyze
        issues = recorder.identify_ux_issues()
        assert isinstance(issues, list)


class TestZAIPlayerIntegration:
    """Test integration with ZAI player for solution generation."""

    @pytest.fixture
    def mock_zai_player(self):
        player = Mock(spec=ZAIPlayer)
        player.name = "TestBot"
        player.generate_solution = AsyncMock(
            return_value="def solution():\n    return 42"
        )
        player.generate_feedback = Mock(
            return_value=PlaytestFeedback(
                challenge_id="test",
                success=True,
                attempts=1,
                time_seconds=10.0,
                confusion_score=0.2,
            )
        )
        return player

    @pytest.fixture
    def playtester(self, mock_zai_player):
        from lmsp.testing.web_playtester import WebPlaytester

        return WebPlaytester(
            zai_player=mock_zai_player,
            base_url="http://localhost:8000",
        )

    @pytest.mark.asyncio
    async def test_use_zai_for_challenge_solution(self, playtester, mock_zai_player):
        """Should use ZAI player to generate solutions."""
        mock_zai_player.observe_challenge = Mock()

        # Mock challenge
        challenge = Mock()
        challenge.id = "hello_world"
        challenge.name = "Hello World"
        challenge.description_brief = "Print hello world"
        challenge.description_detailed = "Write a program that prints hello world"
        challenge.skeleton_code = "def hello():\n    pass"
        challenge.test_cases = []
        challenge.level = 1

        solution = await playtester.attempt_challenge(challenge)

        mock_zai_player.observe_challenge.assert_called_once()
        assert solution is not None

    def test_record_zai_confusion_metrics(self, playtester, mock_zai_player):
        """Should record ZAI confusion metrics."""
        mock_zai_player.confusion_score = 0.7

        playtester.record_zai_state(mock_zai_player)

        assert playtester.zai_confusion_history is not None
        assert len(playtester.zai_confusion_history) > 0


class TestChallengeFlow:
    """Test complete challenge flow through web UI."""

    @pytest.fixture
    def playtester(self):
        from lmsp.testing.web_playtester import WebPlaytester

        zai = Mock(spec=ZAIPlayer)
        zai.name = "TestBot"
        return WebPlaytester(
            zai_player=zai,
            base_url="http://localhost:8000",
        )

    def test_record_complete_challenge_attempt(self, playtester):
        """Should record complete challenge attempt flow."""
        # Simulate challenge flow
        playtester.start_challenge_session("hello_world")
        playtester.record_navigation("/challenges/hello_world")
        playtester.record_interaction(element_type="textarea", action="focus")
        playtester.record_interaction(element_type="textarea", action="type")
        playtester.record_submission(challenge_id="hello_world", success=False)
        playtester.record_interaction(element_type="textarea", action="type")
        playtester.record_submission(challenge_id="hello_world", success=True)
        playtester.end_challenge_session()

        session = playtester.current_session
        assert session["challenge_id"] == "hello_world"
        assert session["submissions"] == 2
        assert session["success"] is True


# Self-teaching note:
#
# This test file demonstrates:
# - Test-driven development (TDD) - tests written FIRST
# - Pytest fixtures for test setup (Level 5: pytest)
# - Mocking with unittest.mock (Level 5: mocking)
# - Async testing with pytest.mark.asyncio (Level 5: async testing)
# - Dataclasses for test data (Level 5: dataclasses)
# - Temporary file handling (Level 4: tempfile)
# - Testing integration between modules (Level 6: integration testing)
#
# Prerequisites:
# - Level 4: Functions, classes, file I/O
# - Level 5: Pytest, mocking, async/await
# - Level 6: Integration patterns, web testing
