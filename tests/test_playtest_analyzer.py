"""
Tests for the Playtest Analyzer module.

The analyzer processes AI playtest data to identify:
- Confusing UX patterns
- Broken flows (stuck points)
- Missing hints
- Difficulty spikes

TDD: These tests are written BEFORE the implementation.
"""

import pytest
from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime, timedelta


class TestPlaytestAnalyzer:
    """Tests for PlaytestAnalyzer class."""

    def test_analyzer_initialization(self):
        """Analyzer can be initialized with default settings."""
        from lmsp.playtest.analyzer import PlaytestAnalyzer

        analyzer = PlaytestAnalyzer()
        assert analyzer is not None
        assert analyzer.thresholds is not None

    def test_analyze_empty_session(self):
        """Analyzing empty session returns empty results."""
        from lmsp.playtest.analyzer import PlaytestAnalyzer, PlaytestSession

        analyzer = PlaytestAnalyzer()
        session = PlaytestSession(events=[])

        result = analyzer.analyze(session)

        assert result is not None
        assert len(result.issues) == 0

    def test_detect_confusion_from_repeated_actions(self):
        """Detect confusion when player repeats same action without progress."""
        from lmsp.playtest.analyzer import (
            PlaytestAnalyzer,
            PlaytestSession,
            PlaytestEvent,
            IssueType
        )

        analyzer = PlaytestAnalyzer()
        base_time = datetime.now()

        # Player tries the same incorrect action 5+ times
        events = [
            PlaytestEvent(
                timestamp=base_time + timedelta(seconds=i * 2),
                event_type="code_submit",
                data={"code": "container.add(x)", "result": "error"},
                player="test_ai"
            )
            for i in range(6)
        ]

        session = PlaytestSession(events=events)
        result = analyzer.analyze(session)

        # Should detect confusion
        confusion_issues = [
            i for i in result.issues if i.issue_type == IssueType.CONFUSING_UX
        ]
        assert len(confusion_issues) > 0

    def test_detect_broken_flow_from_stuck_state(self):
        """Detect broken flow when player is stuck for extended time."""
        from lmsp.playtest.analyzer import (
            PlaytestAnalyzer,
            PlaytestSession,
            PlaytestEvent,
            IssueType
        )

        analyzer = PlaytestAnalyzer()
        base_time = datetime.now()

        events = [
            PlaytestEvent(
                timestamp=base_time,
                event_type="challenge_start",
                data={"challenge_id": "ch001"},
                player="test_ai"
            ),
            # Long gap (player stuck)
            PlaytestEvent(
                timestamp=base_time + timedelta(minutes=10),
                event_type="hint_request",
                data={"hint_level": 3},  # High level hint needed
                player="test_ai"
            ),
        ]

        session = PlaytestSession(events=events)
        result = analyzer.analyze(session)

        broken_flow_issues = [
            i for i in result.issues if i.issue_type == IssueType.BROKEN_FLOW
        ]
        assert len(broken_flow_issues) > 0

    def test_detect_missing_hints_from_frustration(self):
        """Detect missing hints when frustration is high without hint availability."""
        from lmsp.playtest.analyzer import (
            PlaytestAnalyzer,
            PlaytestSession,
            PlaytestEvent,
            IssueType
        )

        analyzer = PlaytestAnalyzer()
        base_time = datetime.now()

        events = [
            PlaytestEvent(
                timestamp=base_time,
                event_type="challenge_start",
                data={"challenge_id": "ch002"},
                player="test_ai"
            ),
            PlaytestEvent(
                timestamp=base_time + timedelta(seconds=30),
                event_type="emotion",
                data={"frustration": 0.9, "positive": 0.1},
                player="test_ai"
            ),
            PlaytestEvent(
                timestamp=base_time + timedelta(seconds=35),
                event_type="hint_request",
                data={"result": "no_hints_available"},
                player="test_ai"
            ),
        ]

        session = PlaytestSession(events=events)
        result = analyzer.analyze(session)

        missing_hint_issues = [
            i for i in result.issues if i.issue_type == IssueType.MISSING_HINTS
        ]
        assert len(missing_hint_issues) > 0

    def test_detect_difficulty_spike(self):
        """Detect difficulty spike from sudden increase in failure rate."""
        from lmsp.playtest.analyzer import (
            PlaytestAnalyzer,
            PlaytestSession,
            PlaytestEvent,
            IssueType
        )

        analyzer = PlaytestAnalyzer()
        base_time = datetime.now()

        events = []
        # First 5 challenges: success
        for i in range(5):
            events.append(PlaytestEvent(
                timestamp=base_time + timedelta(minutes=i),
                event_type="challenge_complete",
                data={
                    "challenge_id": f"ch00{i}",
                    "success": True,
                    "attempts": 1
                },
                player="test_ai"
            ))

        # Challenge 6: sudden difficulty spike (many failures)
        for attempt in range(8):
            events.append(PlaytestEvent(
                timestamp=base_time + timedelta(minutes=5, seconds=attempt * 30),
                event_type="code_submit",
                data={
                    "challenge_id": "ch006",
                    "result": "error"
                },
                player="test_ai"
            ))

        session = PlaytestSession(events=events)
        result = analyzer.analyze(session)

        spike_issues = [
            i for i in result.issues if i.issue_type == IssueType.DIFFICULTY_SPIKE
        ]
        assert len(spike_issues) > 0

    def test_generate_improvement_tasks(self):
        """Analyzer generates actionable improvement tasks."""
        from lmsp.playtest.analyzer import (
            PlaytestAnalyzer,
            PlaytestSession,
            PlaytestEvent,
            IssueType
        )

        analyzer = PlaytestAnalyzer()
        base_time = datetime.now()

        # Create a session with multiple issues
        events = [
            # Confusion issue
            *[
                PlaytestEvent(
                    timestamp=base_time + timedelta(seconds=i * 2),
                    event_type="code_submit",
                    data={"code": "container.add(x)", "result": "error"},
                    player="test_ai"
                )
                for i in range(6)
            ],
        ]

        session = PlaytestSession(events=events)
        result = analyzer.analyze(session)

        # Should have improvement tasks
        assert len(result.improvement_tasks) > 0

        # Tasks should have required fields
        for task in result.improvement_tasks:
            assert task.title
            assert task.description
            assert task.priority in ["low", "medium", "high", "critical"]
            assert task.related_issue is not None

    def test_improvement_task_prioritization(self):
        """Tasks are prioritized by severity and frequency."""
        from lmsp.playtest.analyzer import (
            PlaytestAnalyzer,
            PlaytestSession,
            PlaytestEvent
        )

        analyzer = PlaytestAnalyzer()
        base_time = datetime.now()

        # Create session with multiple issues of different severity
        events = [
            # Broken flow (high severity)
            PlaytestEvent(
                timestamp=base_time,
                event_type="challenge_start",
                data={"challenge_id": "ch001"},
                player="test_ai"
            ),
            PlaytestEvent(
                timestamp=base_time + timedelta(minutes=15),
                event_type="session_abandon",
                data={"reason": "stuck"},
                player="test_ai"
            ),
        ]

        session = PlaytestSession(events=events)
        result = analyzer.analyze(session)

        # High severity issues should be critical/high priority
        if result.improvement_tasks:
            priorities = [t.priority for t in result.improvement_tasks]
            assert "critical" in priorities or "high" in priorities

    def test_analyze_multiple_sessions(self):
        """Analyzer can process multiple sessions and aggregate findings."""
        from lmsp.playtest.analyzer import (
            PlaytestAnalyzer,
            PlaytestSession,
            PlaytestEvent
        )

        analyzer = PlaytestAnalyzer()
        base_time = datetime.now()

        sessions = [
            PlaytestSession(events=[
                PlaytestEvent(
                    timestamp=base_time,
                    event_type="challenge_complete",
                    data={"challenge_id": "ch001", "success": True},
                    player=f"ai_{i}"
                )
            ])
            for i in range(5)
        ]

        result = analyzer.analyze_batch(sessions)

        assert result is not None
        assert hasattr(result, "session_count")
        assert result.session_count == 5

    def test_track_challenge_specific_issues(self):
        """Issues are tracked per-challenge for targeted improvements."""
        from lmsp.playtest.analyzer import (
            PlaytestAnalyzer,
            PlaytestSession,
            PlaytestEvent
        )

        analyzer = PlaytestAnalyzer()
        base_time = datetime.now()

        events = [
            PlaytestEvent(
                timestamp=base_time + timedelta(seconds=i * 2),
                event_type="code_submit",
                data={
                    "challenge_id": "problematic_challenge",
                    "code": "wrong",
                    "result": "error"
                },
                player="test_ai"
            )
            for i in range(6)
        ]

        session = PlaytestSession(events=events)
        result = analyzer.analyze(session)

        # Issues should reference the specific challenge
        for issue in result.issues:
            assert issue.challenge_id == "problematic_challenge"

    def test_export_report_markdown(self):
        """Analyzer can export findings as markdown report."""
        from lmsp.playtest.analyzer import (
            PlaytestAnalyzer,
            PlaytestSession,
            PlaytestEvent
        )

        analyzer = PlaytestAnalyzer()
        base_time = datetime.now()

        events = [
            PlaytestEvent(
                timestamp=base_time + timedelta(seconds=i * 2),
                event_type="code_submit",
                data={"code": "x", "result": "error"},
                player="test_ai"
            )
            for i in range(6)
        ]

        session = PlaytestSession(events=events)
        result = analyzer.analyze(session)

        markdown = result.to_markdown()

        assert "# Playtest Analysis Report" in markdown
        assert "## Issues Found" in markdown
        assert "## Improvement Tasks" in markdown

    def test_export_report_json(self):
        """Analyzer can export findings as JSON for automation."""
        from lmsp.playtest.analyzer import (
            PlaytestAnalyzer,
            PlaytestSession,
            PlaytestEvent
        )
        import json

        analyzer = PlaytestAnalyzer()
        session = PlaytestSession(events=[])
        result = analyzer.analyze(session)

        json_str = result.to_json()
        data = json.loads(json_str)

        assert "issues" in data
        assert "improvement_tasks" in data
        assert "summary" in data


class TestPlaytestEvent:
    """Tests for PlaytestEvent data structure."""

    def test_event_creation(self):
        """Events can be created with required fields."""
        from lmsp.playtest.analyzer import PlaytestEvent

        event = PlaytestEvent(
            timestamp=datetime.now(),
            event_type="code_submit",
            data={"code": "print('hello')"},
            player="test_player"
        )

        assert event.event_type == "code_submit"
        assert event.player == "test_player"

    def test_event_from_dict(self):
        """Events can be created from dictionary."""
        from lmsp.playtest.analyzer import PlaytestEvent

        data = {
            "timestamp": "2024-01-01T12:00:00",
            "event_type": "challenge_complete",
            "data": {"success": True},
            "player": "ai_1"
        }

        event = PlaytestEvent.from_dict(data)

        assert event.event_type == "challenge_complete"
        assert event.data["success"] is True


class TestImprovementTask:
    """Tests for ImprovementTask data structure."""

    def test_task_creation(self):
        """Improvement tasks can be created with required fields."""
        from lmsp.playtest.analyzer import ImprovementTask, IssueType, PlaytestIssue

        issue = PlaytestIssue(
            issue_type=IssueType.CONFUSING_UX,
            description="Players are confused by the add method",
            challenge_id="ch001",
            severity=0.8
        )

        task = ImprovementTask(
            title="Improve add method documentation",
            description="Add clearer examples showing correct usage",
            priority="high",
            related_issue=issue
        )

        assert task.title == "Improve add method documentation"
        assert task.priority == "high"

    def test_task_to_dict(self):
        """Tasks can be serialized to dictionary."""
        from lmsp.playtest.analyzer import ImprovementTask, IssueType, PlaytestIssue

        issue = PlaytestIssue(
            issue_type=IssueType.MISSING_HINTS,
            description="No hints available",
            challenge_id="ch002",
            severity=0.6
        )

        task = ImprovementTask(
            title="Add hints for challenge",
            description="Create progressive hints",
            priority="medium",
            related_issue=issue
        )

        data = task.to_dict()

        assert data["title"] == "Add hints for challenge"
        assert data["priority"] == "medium"
        assert "related_issue" in data


# Self-teaching note:
#
# This test file demonstrates:
# - Test-Driven Development (TDD) - tests written BEFORE implementation
# - pytest fixtures and parametrization patterns
# - Dataclass testing patterns
# - Testing for both happy path and edge cases
# - Testing serialization (JSON, Markdown)
#
# The playtest analyzer is a feedback loop:
# 1. AI players playtest the game
# 2. Events are captured (emotions, actions, results)
# 3. Analyzer identifies issues and patterns
# 4. Improvement tasks are generated
# 5. Developers implement fixes
# 6. Repeat
