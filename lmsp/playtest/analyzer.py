"""
Playtest Analyzer - Processes AI playtest data to find UX issues.

This module identifies:
- Confusing UX patterns (repeated failures, high frustration)
- Broken flows (stuck states, crashes)
- Missing hints (frustration without help available)
- Difficulty spikes (sudden increase in failure rate)

The analyzer closes the improvement loop by generating actionable tasks.

Self-teaching note:

This file demonstrates:
- Dataclasses for structured data (Level 5)
- Enums for type-safe categories (Level 4)
- List comprehensions for data processing (Level 2)
- JSON serialization (Level 4)
- Algorithm design for pattern detection (Level 6)

The learner will encounter this AFTER mastering collections and classes.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import List, Dict, Any, Optional
import json


class IssueType(Enum):
    """Types of UX issues detected during playtesting."""

    CONFUSING_UX = auto()
    BROKEN_FLOW = auto()
    MISSING_HINTS = auto()
    DIFFICULTY_SPIKE = auto()


@dataclass
class PlaytestEvent:
    """
    A single event captured during playtesting.

    Events track player actions, emotions, and results.
    """

    timestamp: datetime
    event_type: str
    data: Dict[str, Any]
    player: str

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "PlaytestEvent":
        """Create an event from a dictionary (e.g., from JSON)."""
        timestamp = d.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        elif timestamp is None:
            timestamp = datetime.now()

        return cls(
            timestamp=timestamp,
            event_type=d.get("event_type", ""),
            data=d.get("data", {}),
            player=d.get("player", "unknown"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type,
            "data": self.data,
            "player": self.player,
        }


@dataclass
class PlaytestSession:
    """
    A complete playtest session with all events.

    Sessions are the unit of analysis - one session per AI player run.
    """

    events: List[PlaytestEvent]
    session_id: str = ""
    player_name: str = ""

    def get_events_by_type(self, event_type: str) -> List[PlaytestEvent]:
        """Get all events of a specific type."""
        return [e for e in self.events if e.event_type == event_type]

    def get_duration(self) -> Optional[timedelta]:
        """Get session duration from first to last event."""
        if len(self.events) < 2:
            return None
        return self.events[-1].timestamp - self.events[0].timestamp


@dataclass
class PlaytestIssue:
    """
    An issue detected during playtest analysis.

    Issues represent UX problems that need to be fixed.
    """

    issue_type: IssueType
    description: str
    challenge_id: str
    severity: float  # 0.0 to 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert issue to dictionary."""
        return {
            "issue_type": self.issue_type.name,
            "description": self.description,
            "challenge_id": self.challenge_id,
            "severity": self.severity,
        }


@dataclass
class ImprovementTask:
    """
    An actionable task to improve the game.

    Tasks are generated from detected issues.
    """

    title: str
    description: str
    priority: str  # "low", "medium", "high", "critical"
    related_issue: PlaytestIssue

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "related_issue": self.related_issue.to_dict(),
        }


@dataclass
class AnalysisResult:
    """
    Result of analyzing a playtest session.

    Contains detected issues and generated improvement tasks.
    """

    issues: List[PlaytestIssue] = field(default_factory=list)
    improvement_tasks: List[ImprovementTask] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)

    def to_markdown(self) -> str:
        """Export analysis as markdown report."""
        lines = ["# Playtest Analysis Report", ""]

        # Summary section
        lines.append("## Summary")
        lines.append(f"- Total issues: {len(self.issues)}")
        lines.append(f"- Improvement tasks: {len(self.improvement_tasks)}")
        lines.append("")

        # Issues section
        lines.append("## Issues Found")
        if self.issues:
            for issue in self.issues:
                lines.append(
                    f"- **{issue.issue_type.name}** ({issue.challenge_id}): "
                    f"{issue.description} (severity: {issue.severity:.1%})"
                )
        else:
            lines.append("No issues detected.")
        lines.append("")

        # Tasks section
        lines.append("## Improvement Tasks")
        if self.improvement_tasks:
            for task in self.improvement_tasks:
                lines.append(f"### [{task.priority.upper()}] {task.title}")
                lines.append(f"{task.description}")
                lines.append("")
        else:
            lines.append("No improvement tasks generated.")

        return "\n".join(lines)

    def to_json(self) -> str:
        """Export analysis as JSON."""
        return json.dumps(
            {
                "issues": [i.to_dict() for i in self.issues],
                "improvement_tasks": [t.to_dict() for t in self.improvement_tasks],
                "summary": self.summary,
            },
            indent=2,
        )


@dataclass
class BatchAnalysisResult:
    """Result of analyzing multiple sessions."""

    session_count: int
    aggregated_issues: List[PlaytestIssue] = field(default_factory=list)
    aggregated_tasks: List[ImprovementTask] = field(default_factory=list)


@dataclass
class AnalyzerThresholds:
    """Configurable thresholds for issue detection."""

    # Confusion detection
    repeated_action_threshold: int = 5  # Same action this many times = confusion
    frustration_threshold: float = 0.7  # Frustration above this = concerning

    # Broken flow detection
    stuck_time_threshold: int = 300  # Seconds without progress = stuck
    high_hint_level_threshold: int = 2  # Hint level above this = really stuck

    # Missing hints
    frustration_without_hint_threshold: float = 0.6

    # Difficulty spike
    failure_rate_spike_threshold: float = 0.5  # Jump in failure rate
    consecutive_failures_threshold: int = 5


class PlaytestAnalyzer:
    """
    Analyzes playtest sessions to find UX issues.

    The analyzer processes events from AI playtest sessions and identifies
    patterns that indicate UX problems.
    """

    def __init__(self, thresholds: Optional[AnalyzerThresholds] = None):
        """Initialize analyzer with optional custom thresholds."""
        self.thresholds = thresholds or AnalyzerThresholds()

    def analyze(self, session: PlaytestSession) -> AnalysisResult:
        """
        Analyze a single playtest session.

        Args:
            session: The session to analyze

        Returns:
            AnalysisResult with detected issues and improvement tasks
        """
        result = AnalysisResult()

        if not session.events:
            return result

        # Detect different types of issues
        confusion_issues = self._detect_confusion(session)
        broken_flow_issues = self._detect_broken_flow(session)
        missing_hint_issues = self._detect_missing_hints(session)
        difficulty_spike_issues = self._detect_difficulty_spike(session)

        # Collect all issues
        result.issues.extend(confusion_issues)
        result.issues.extend(broken_flow_issues)
        result.issues.extend(missing_hint_issues)
        result.issues.extend(difficulty_spike_issues)

        # Generate improvement tasks from issues
        result.improvement_tasks = self._generate_tasks(result.issues)

        # Build summary
        result.summary = {
            "total_issues": len(result.issues),
            "confusion_count": len(confusion_issues),
            "broken_flow_count": len(broken_flow_issues),
            "missing_hint_count": len(missing_hint_issues),
            "difficulty_spike_count": len(difficulty_spike_issues),
        }

        return result

    def analyze_batch(self, sessions: List[PlaytestSession]) -> BatchAnalysisResult:
        """
        Analyze multiple sessions and aggregate results.

        Args:
            sessions: List of sessions to analyze

        Returns:
            BatchAnalysisResult with aggregated findings
        """
        result = BatchAnalysisResult(session_count=len(sessions))

        for session in sessions:
            analysis = self.analyze(session)
            result.aggregated_issues.extend(analysis.issues)
            result.aggregated_tasks.extend(analysis.improvement_tasks)

        return result

    def _detect_confusion(self, session: PlaytestSession) -> List[PlaytestIssue]:
        """Detect confusion from repeated actions without progress."""
        issues = []

        # Group submissions by code content
        code_submissions = session.get_events_by_type("code_submit")

        if len(code_submissions) >= self.thresholds.repeated_action_threshold:
            # Check for repeated identical submissions
            code_counts: Dict[str, int] = {}
            for event in code_submissions:
                code = event.data.get("code", "")
                code_counts[code] = code_counts.get(code, 0) + 1

            # Find repeated codes
            for code, count in code_counts.items():
                if count >= self.thresholds.repeated_action_threshold:
                    challenge_id = code_submissions[0].data.get("challenge_id", "unknown")
                    issues.append(
                        PlaytestIssue(
                            issue_type=IssueType.CONFUSING_UX,
                            description=(
                                f"Player repeated same code {count} times without progress. "
                                f"This suggests confusing instructions or unclear feedback."
                            ),
                            challenge_id=challenge_id,
                            severity=min(1.0, count / 10.0),
                        )
                    )

        return issues

    def _detect_broken_flow(self, session: PlaytestSession) -> List[PlaytestIssue]:
        """Detect broken flows from stuck states."""
        issues = []

        # Look for long gaps between events (player stuck)
        events = session.events
        for i in range(1, len(events)):
            gap = (events[i].timestamp - events[i - 1].timestamp).total_seconds()

            if gap >= self.thresholds.stuck_time_threshold:
                # Check if followed by high-level hint request
                if events[i].event_type == "hint_request":
                    hint_level = events[i].data.get("hint_level", 0)
                    if hint_level >= self.thresholds.high_hint_level_threshold:
                        challenge_id = events[i - 1].data.get(
                            "challenge_id",
                            events[i].data.get("challenge_id", "unknown"),
                        )
                        issues.append(
                            PlaytestIssue(
                                issue_type=IssueType.BROKEN_FLOW,
                                description=(
                                    f"Player was stuck for {gap:.0f} seconds and needed "
                                    f"level {hint_level} hint. Flow may be broken."
                                ),
                                challenge_id=challenge_id,
                                severity=min(1.0, gap / 600.0),
                            )
                        )

        # Also check for session abandonment
        abandon_events = session.get_events_by_type("session_abandon")
        for event in abandon_events:
            reason = event.data.get("reason", "unknown")
            challenge_id = event.data.get("challenge_id", "unknown")
            issues.append(
                PlaytestIssue(
                    issue_type=IssueType.BROKEN_FLOW,
                    description=f"Player abandoned session: {reason}",
                    challenge_id=challenge_id,
                    severity=0.9,
                )
            )

        return issues

    def _detect_missing_hints(self, session: PlaytestSession) -> List[PlaytestIssue]:
        """Detect when hints were needed but not available."""
        issues = []

        emotion_events = session.get_events_by_type("emotion")
        hint_events = session.get_events_by_type("hint_request")

        # Check for high frustration followed by no hints available
        for emotion in emotion_events:
            frustration = emotion.data.get("frustration", 0)
            if frustration >= self.thresholds.frustration_without_hint_threshold:
                # Look for nearby hint request with no hints available
                for hint in hint_events:
                    time_diff = abs(
                        (hint.timestamp - emotion.timestamp).total_seconds()
                    )
                    if time_diff < 60:  # Within 1 minute
                        if hint.data.get("result") == "no_hints_available":
                            challenge_id = hint.data.get(
                                "challenge_id",
                                emotion.data.get("challenge_id", "unknown"),
                            )
                            issues.append(
                                PlaytestIssue(
                                    issue_type=IssueType.MISSING_HINTS,
                                    description=(
                                        f"Player was frustrated ({frustration:.0%}) "
                                        f"but no hints were available."
                                    ),
                                    challenge_id=challenge_id,
                                    severity=frustration,
                                )
                            )

        return issues

    def _detect_difficulty_spike(self, session: PlaytestSession) -> List[PlaytestIssue]:
        """Detect sudden difficulty spikes."""
        issues = []

        # Get challenge completion events
        completions = session.get_events_by_type("challenge_complete")
        submissions = session.get_events_by_type("code_submit")

        if not completions and not submissions:
            return issues

        # Track success rate per challenge
        challenge_attempts: Dict[str, int] = {}
        challenge_successes: Dict[str, int] = {}

        for event in completions:
            challenge_id = event.data.get("challenge_id", "")
            if event.data.get("success"):
                challenge_successes[challenge_id] = (
                    challenge_successes.get(challenge_id, 0) + 1
                )

        for event in submissions:
            challenge_id = event.data.get("challenge_id", "")
            challenge_attempts[challenge_id] = challenge_attempts.get(challenge_id, 0) + 1

        # Look for challenges with many failures after easy successes
        prev_success_rate = 1.0
        for challenge_id in challenge_attempts:
            attempts = challenge_attempts[challenge_id]
            successes = challenge_successes.get(challenge_id, 0)

            if attempts > 0:
                success_rate = successes / attempts
                rate_drop = prev_success_rate - success_rate

                if (
                    rate_drop >= self.thresholds.failure_rate_spike_threshold
                    or attempts >= self.thresholds.consecutive_failures_threshold * 2
                ):
                    issues.append(
                        PlaytestIssue(
                            issue_type=IssueType.DIFFICULTY_SPIKE,
                            description=(
                                f"Difficulty spike detected: {attempts} attempts "
                                f"with {successes} successes ({success_rate:.0%}). "
                                f"Previous challenges were easier."
                            ),
                            challenge_id=challenge_id,
                            severity=min(1.0, rate_drop + 0.3),
                        )
                    )

                prev_success_rate = success_rate

        return issues

    def _generate_tasks(self, issues: List[PlaytestIssue]) -> List[ImprovementTask]:
        """Generate improvement tasks from detected issues."""
        tasks = []

        for issue in issues:
            task = self._issue_to_task(issue)
            tasks.append(task)

        # Sort by priority (critical first)
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        tasks.sort(key=lambda t: priority_order.get(t.priority, 99))

        return tasks

    def _issue_to_task(self, issue: PlaytestIssue) -> ImprovementTask:
        """Convert an issue to an improvement task."""
        # Determine priority based on severity
        if issue.severity >= 0.8:
            priority = "critical"
        elif issue.severity >= 0.6:
            priority = "high"
        elif issue.severity >= 0.4:
            priority = "medium"
        else:
            priority = "low"

        # Generate title and description based on issue type
        if issue.issue_type == IssueType.CONFUSING_UX:
            title = f"Improve UX clarity for {issue.challenge_id}"
            description = (
                f"Players are confused by the current UX. "
                f"Consider: clearer instructions, better error messages, "
                f"visual feedback. Issue: {issue.description}"
            )
        elif issue.issue_type == IssueType.BROKEN_FLOW:
            title = f"Fix broken flow in {issue.challenge_id}"
            description = (
                f"Players are getting stuck and can't progress. "
                f"Check for: impossible states, missing guidance, "
                f"blocking bugs. Issue: {issue.description}"
            )
        elif issue.issue_type == IssueType.MISSING_HINTS:
            title = f"Add hints for {issue.challenge_id}"
            description = (
                f"Players need hints but none are available. "
                f"Add progressive hints that guide without spoiling. "
                f"Issue: {issue.description}"
            )
        elif issue.issue_type == IssueType.DIFFICULTY_SPIKE:
            title = f"Smooth difficulty curve at {issue.challenge_id}"
            description = (
                f"Challenge is too hard relative to previous ones. "
                f"Consider: adding intermediate steps, better scaffolding, "
                f"prerequisite concepts. Issue: {issue.description}"
            )
        else:
            title = f"Address issue in {issue.challenge_id}"
            description = issue.description

        return ImprovementTask(
            title=title,
            description=description,
            priority=priority,
            related_issue=issue,
        )


# Self-teaching note:
#
# This file demonstrates:
# - Dataclasses for structured data (Level 5)
# - Enums for type-safe categories (Level 4)
# - List comprehensions for data processing (Level 2)
# - Dictionary operations for counting (Level 3)
# - JSON serialization (Level 4)
# - Algorithm design for pattern detection (Level 6)
# - Factory methods (from_dict) (Level 5)
#
# The playtest analyzer is a feedback loop:
# 1. AI players playtest the game
# 2. Events are captured (emotions, actions, results)
# 3. Analyzer identifies issues and patterns
# 4. Improvement tasks are generated
# 5. Developers implement fixes
# 6. Repeat
#
# This closes the loop and enables continuous improvement!
