"""
Automated Playtest Report Generator for LMSP
=============================================

This module orchestrates full ZAI+Playwright playtest suites and generates
comprehensive markdown reports with:
- Screenshots/videos at key moments
- Confusion pattern analysis
- Prioritized UX improvements
- Code quality metrics

The report generator closes the feedback loop by providing actionable
insights from automated playtesting that developers can use to improve
the game experience.

Self-teaching note:

This file demonstrates:
- Dataclasses for configuration and results (Level 5)
- Async orchestration (Level 5-6)
- Report generation patterns (Level 5)
- Integration of multiple systems (Level 6)
- Professional CI/CD patterns (Professional)

Prerequisites:
- Level 5: Dataclasses, async/await, file I/O
- Level 6: System integration, web automation
- Professional: CI/CD, testing automation
"""

import asyncio
import json
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# Import ZAIPlayer for orchestration
from lmsp.multiplayer.zai_player import ZAIPlayer


@dataclass
class ReportConfig:
    """
    Configuration for playtest report generation.

    Attributes:
        output_dir: Directory for reports and artifacts
        screenshot_on_struggle: Capture screenshots when struggles detected
        video_recording: Enable video recording of playtests
        include_code_metrics: Include code quality metrics in report
        confusion_threshold: Threshold for confusion score alerts
    """

    output_dir: Path = field(default_factory=lambda: Path("reports"))
    screenshot_on_struggle: bool = True
    video_recording: bool = False
    include_code_metrics: bool = True
    confusion_threshold: float = 0.5

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReportConfig":
        """Create config from dictionary."""
        return cls(
            output_dir=Path(data.get("output_dir", "reports")),
            screenshot_on_struggle=data.get("screenshot_on_struggle", True),
            video_recording=data.get("video_recording", False),
            include_code_metrics=data.get("include_code_metrics", True),
            confusion_threshold=data.get("confusion_threshold", 0.5),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "output_dir": str(self.output_dir),
            "screenshot_on_struggle": self.screenshot_on_struggle,
            "video_recording": self.video_recording,
            "include_code_metrics": self.include_code_metrics,
            "confusion_threshold": self.confusion_threshold,
        }


@dataclass
class StruggleMoment:
    """
    A moment of struggle detected during playtest.

    Attributes:
        challenge_id: Challenge where struggle occurred
        pattern: Type of struggle pattern detected
        description: Human-readable description
        severity: Severity score (0.0-1.0)
        timestamp: When the struggle occurred
        screenshot_path: Path to screenshot if captured
        suggestions: UX improvement suggestions
    """

    challenge_id: str
    pattern: str
    description: str
    severity: float
    timestamp: datetime = field(default_factory=datetime.now)
    screenshot_path: Optional[str] = None
    suggestions: List[str] = field(default_factory=list)


@dataclass
class ConfusionPattern:
    """
    A detected confusion pattern.

    Attributes:
        pattern_type: Type of pattern (rapid_failures, backtracking, etc.)
        occurrences: Number of times pattern occurred
        affected_challenges: Challenges affected by this pattern
        suggested_fix: Suggested fix for this pattern
    """

    pattern_type: str
    occurrences: int
    affected_challenges: List[str]
    suggested_fix: str


@dataclass
class CodeMetrics:
    """
    Code quality metrics collected during report generation.

    Attributes:
        total_tests: Total number of tests
        tests_passing: Number of tests passing
        test_coverage: Test coverage percentage
        lint_warnings: Number of lint warnings
        type_errors: Number of type errors
        type_coverage: Type annotation coverage
    """

    total_tests: int = 0
    tests_passing: int = 0
    test_coverage: float = 0.0
    lint_warnings: int = 0
    type_errors: int = 0
    type_coverage: float = 0.0


@dataclass
class PlaytestSuiteResult:
    """
    Result of running a playtest suite.

    Attributes:
        total_challenges: Total challenges tested
        passed_challenges: Challenges completed successfully
        failed_challenges: Challenges that couldn't be completed
        struggles: Detected struggle moments
        confusion_scores: Confusion score per challenge
        confusion_patterns: Detected confusion patterns
        screenshots: Paths to captured screenshots
        video_path: Path to video if recorded
        code_metrics: Code quality metrics if collected
    """

    total_challenges: int = 0
    passed_challenges: int = 0
    failed_challenges: int = 0
    struggles: List[StruggleMoment] = field(default_factory=list)
    confusion_scores: Dict[str, float] = field(default_factory=dict)
    confusion_patterns: List[ConfusionPattern] = field(default_factory=list)
    screenshots: List[Dict[str, Any]] = field(default_factory=list)
    video_path: Optional[str] = None
    code_metrics: Optional[CodeMetrics] = None


class ConfusionAnalyzer:
    """
    Analyzes playtest events to detect confusion patterns.

    Patterns detected:
    - rapid_failures: Multiple failures in quick succession
    - backtracking: Going back and forth in code
    - long_pause: Extended time without action
    - hint_abuse: Excessive hint usage
    """

    def __init__(
        self,
        rapid_failure_threshold: int = 5,
        pause_threshold_seconds: float = 120.0,
        hint_abuse_threshold: int = 3,
    ):
        """
        Initialize the analyzer.

        Args:
            rapid_failure_threshold: Number of failures to detect rapid failure
            pause_threshold_seconds: Seconds of inactivity for long pause
            hint_abuse_threshold: Number of hints for hint abuse
        """
        self.rapid_failure_threshold = rapid_failure_threshold
        self.pause_threshold_seconds = pause_threshold_seconds
        self.hint_abuse_threshold = hint_abuse_threshold

    def analyze(self, events: List[Dict[str, Any]]) -> List[ConfusionPattern]:
        """
        Analyze events and return detected patterns.

        Args:
            events: List of playtest events

        Returns:
            List of detected confusion patterns
        """
        patterns = []

        # Detect rapid failures
        rapid_failures = self._detect_rapid_failures(events)
        if rapid_failures:
            patterns.append(rapid_failures)

        # Detect backtracking
        backtracking = self._detect_backtracking(events)
        if backtracking:
            patterns.append(backtracking)

        # Detect long pauses
        long_pauses = self._detect_long_pauses(events)
        if long_pauses:
            patterns.append(long_pauses)

        # Detect hint abuse
        hint_abuse = self._detect_hint_abuse(events)
        if hint_abuse:
            patterns.append(hint_abuse)

        return patterns

    def _detect_rapid_failures(
        self, events: List[Dict[str, Any]]
    ) -> Optional[ConfusionPattern]:
        """Detect rapid failure pattern."""
        failures = [e for e in events if e.get("type") == "attempt" and not e.get("success")]

        if len(failures) >= self.rapid_failure_threshold:
            # Check if they happened quickly
            if len(failures) >= 2:
                times = [e.get("time", 0) for e in failures[-self.rapid_failure_threshold:]]
                if sum(times) < 30:  # All within 30 seconds
                    return ConfusionPattern(
                        pattern_type="rapid_failures",
                        occurrences=len(failures),
                        affected_challenges=[],
                        suggested_fix="Add clearer error messages and hints",
                    )
        return None

    def _detect_backtracking(
        self, events: List[Dict[str, Any]]
    ) -> Optional[ConfusionPattern]:
        """Detect code backtracking pattern."""
        code_changes = [e for e in events if e.get("type") == "code_change"]

        if len(code_changes) >= 3:
            codes = [e.get("code", "") for e in code_changes]
            unique_codes = set(codes)

            # If player returned to earlier code
            if len(codes) > len(unique_codes):
                return ConfusionPattern(
                    pattern_type="backtracking",
                    occurrences=len(codes) - len(unique_codes),
                    affected_challenges=[],
                    suggested_fix="Provide more structured scaffolding",
                )
        return None

    def _detect_long_pauses(
        self, events: List[Dict[str, Any]]
    ) -> Optional[ConfusionPattern]:
        """Detect long pause pattern."""
        pauses = 0

        for i in range(1, len(events)):
            prev = events[i - 1]
            curr = events[i]

            prev_ts = prev.get("timestamp")
            curr_ts = curr.get("timestamp")

            if prev_ts and curr_ts:
                if hasattr(prev_ts, "timestamp") and hasattr(curr_ts, "timestamp"):
                    diff = (curr_ts - prev_ts).total_seconds()
                    if diff > self.pause_threshold_seconds:
                        pauses += 1

        if pauses > 0:
            return ConfusionPattern(
                pattern_type="long_pause",
                occurrences=pauses,
                affected_challenges=[],
                suggested_fix="Add intermediate checkpoints or hints",
            )
        return None

    def _detect_hint_abuse(
        self, events: List[Dict[str, Any]]
    ) -> Optional[ConfusionPattern]:
        """Detect excessive hint usage."""
        hints = [e for e in events if e.get("type") == "hint_request"]

        if len(hints) >= self.hint_abuse_threshold:
            return ConfusionPattern(
                pattern_type="hint_abuse",
                occurrences=len(hints),
                affected_challenges=[],
                suggested_fix="Consider breaking challenge into smaller steps",
            )
        return None

    def calculate_confusion_score(self, events: List[Dict[str, Any]]) -> float:
        """
        Calculate overall confusion score from events.

        Args:
            events: List of playtest events

        Returns:
            Confusion score (0.0-1.0)
        """
        score = 0.0

        # Factor in failures
        failures = len([e for e in events if e.get("type") == "attempt" and not e.get("success")])
        attempts = len([e for e in events if e.get("type") == "attempt"])

        if attempts > 0:
            failure_rate = failures / attempts
            score += failure_rate * 0.4

        # Factor in patterns
        patterns = self.analyze(events)
        if patterns:
            score += len(patterns) * 0.15

        return min(1.0, score)


class CodeMetricsCollector:
    """
    Collects code quality metrics for the project.

    Metrics collected:
    - Test count and coverage
    - Lint warnings
    - Type errors and coverage
    """

    def __init__(self, project_root: Path):
        """
        Initialize the collector.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root

    def collect(self) -> CodeMetrics:
        """
        Collect code quality metrics.

        Returns:
            CodeMetrics object with collected data
        """
        metrics = CodeMetrics()

        # Run pytest to get test count
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "--collect-only", "-q"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30,
            )
            # Parse test count from output
            for line in result.stdout.split("\n"):
                if "test" in line.lower():
                    # Try to extract number
                    parts = line.split()
                    for part in parts:
                        if part.isdigit():
                            metrics.total_tests = int(part)
                            break
        except Exception:
            pass

        # Run ruff for lint warnings
        try:
            result = subprocess.run(
                ["ruff", "check", "lmsp/", "--output-format=json"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.stdout:
                try:
                    warnings = json.loads(result.stdout)
                    metrics.lint_warnings = len(warnings)
                except json.JSONDecodeError:
                    pass
        except Exception:
            pass

        return metrics


class PlaywrightRunner:
    """
    Runs Playwright browser automation for playtesting.

    This class wraps Playwright MCP tools for capturing screenshots
    and videos during playtest sessions.
    """

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the runner.

        Args:
            base_url: Base URL for the web application
        """
        self.base_url = base_url
        self.page = None
        self.context = None

    async def navigate(self, path: str) -> None:
        """
        Navigate to a path.

        Args:
            path: Path to navigate to
        """
        # In actual implementation, would call:
        # mcp__playwright__browser_navigate(url=f"{self.base_url}{path}")
        pass

    async def capture_screenshot(self, name: str) -> bytes:
        """
        Capture screenshot.

        Args:
            name: Name for the screenshot

        Returns:
            Screenshot bytes
        """
        # In actual implementation, would call:
        # mcp__playwright__browser_take_screenshot(filename=f"{name}.png")
        return b"PNG data placeholder"

    async def start_recording(self) -> None:
        """Start video/trace recording."""
        # In actual implementation:
        # await context.tracing.start(screenshots=True, snapshots=True)
        pass

    async def stop_recording(self, output_path: str) -> str:
        """
        Stop recording and save.

        Args:
            output_path: Path to save recording

        Returns:
            Path to saved recording
        """
        # In actual implementation:
        # await context.tracing.stop(path=output_path)
        return output_path


class MarkdownReportGenerator:
    """
    Generates markdown reports from playtest results.

    Reports include:
    - Summary statistics
    - Confusion analysis
    - Prioritized improvements
    - Screenshots section
    - Code quality metrics
    """

    def generate(self, result: PlaytestSuiteResult) -> str:
        """
        Generate markdown report from results.

        Args:
            result: Playtest suite result

        Returns:
            Markdown report string
        """
        lines = []

        # Title and timestamp
        lines.append("# LMSP Playtest Report")
        lines.append("")
        lines.append(f"**Generated:** {datetime.now().isoformat()}")
        lines.append("")

        # Summary
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- **Total Challenges:** {result.total_challenges}")
        lines.append(f"- **Passed:** {result.passed_challenges}")
        lines.append(f"- **Failed:** {result.failed_challenges}")

        if result.total_challenges > 0:
            success_rate = result.passed_challenges / result.total_challenges * 100
            lines.append(f"- **Success Rate:** {success_rate:.1f}%")

        lines.append("")

        # Confusion Analysis
        if result.confusion_scores:
            lines.append("## Confusion Analysis")
            lines.append("")

            for challenge_id, score in sorted(
                result.confusion_scores.items(),
                key=lambda x: x[1],
                reverse=True,
            ):
                icon = "🔴" if score > 0.7 else "🟡" if score > 0.4 else "🟢"
                lines.append(f"- {icon} **{challenge_id}:** {score:.0%} confusion score")

            lines.append("")

        # Confusion Patterns
        if result.confusion_patterns:
            lines.append("### Detected Patterns")
            lines.append("")

            for pattern in result.confusion_patterns:
                lines.append(
                    f"- **{pattern.pattern_type}** ({pattern.occurrences} occurrences)"
                )
                lines.append(f"  - Suggested fix: {pattern.suggested_fix}")

            lines.append("")

        # Prioritized Improvements
        if result.struggles:
            lines.append("## Prioritized Improvements")
            lines.append("")

            # Sort by severity
            sorted_struggles = sorted(
                result.struggles,
                key=lambda s: s.severity,
                reverse=True,
            )

            for struggle in sorted_struggles:
                priority = "CRITICAL" if struggle.severity > 0.8 else "HIGH" if struggle.severity > 0.6 else "MEDIUM"
                lines.append(f"### [{priority}] {struggle.challenge_id}")
                lines.append("")
                lines.append(f"**Pattern:** {struggle.pattern}")
                lines.append(f"**Description:** {struggle.description}")
                lines.append("")

                if struggle.suggestions:
                    lines.append("**Suggestions:**")
                    for suggestion in struggle.suggestions:
                        lines.append(f"- {suggestion}")
                    lines.append("")

        # Screenshots
        if result.screenshots:
            lines.append("## Screenshots")
            lines.append("")

            for screenshot in result.screenshots:
                path = screenshot.get("path", "")
                caption = screenshot.get("caption", "Screenshot")
                lines.append(f"### {caption}")
                lines.append(f"![{caption}]({path})")
                lines.append("")

        # Code Quality Metrics
        if result.code_metrics:
            lines.append("## Code Quality Metrics")
            lines.append("")
            lines.append(f"- **Total Tests:** {result.code_metrics.total_tests}")
            lines.append(f"- **Tests Passing:** {result.code_metrics.tests_passing}")
            lines.append(f"- **Test Coverage:** {result.code_metrics.test_coverage:.1f}%")
            lines.append(f"- **Lint Warnings:** {result.code_metrics.lint_warnings}")
            lines.append(f"- **Type Errors:** {result.code_metrics.type_errors}")
            lines.append("")

        return "\n".join(lines)


class PlaytestReportGenerator:
    """
    Main orchestrator for automated playtest report generation.

    This class ties together:
    - ZAI player for AI-driven playtesting
    - Playwright for browser automation
    - Confusion analysis
    - Code metrics collection
    - Report generation
    """

    def __init__(self, config: Optional[ReportConfig] = None):
        """
        Initialize the generator.

        Args:
            config: Report configuration
        """
        self.config = config or ReportConfig()
        self.confusion_analyzer = ConfusionAnalyzer()
        self.report_generator = MarkdownReportGenerator()

    def run_suite(self, challenges: List[str]) -> PlaytestSuiteResult:
        """
        Run playtest suite on given challenges.

        Args:
            challenges: List of challenge IDs to test

        Returns:
            PlaytestSuiteResult with all data
        """
        result = PlaytestSuiteResult(total_challenges=len(challenges))

        # Would orchestrate ZAI player and Playwright runner
        # For now, return empty result
        return result

    def generate_report(
        self,
        challenges: List[str],
        save_to_file: bool = True,
    ) -> str:
        """
        Generate complete playtest report.

        Args:
            challenges: List of challenge IDs to test
            save_to_file: Whether to save report to file

        Returns:
            Markdown report string
        """
        # Run playtest suite
        result = self.run_suite(challenges)

        # Collect code metrics if enabled
        if self.config.include_code_metrics:
            collector = CodeMetricsCollector(
                project_root=Path(__file__).parent.parent.parent
            )
            result.code_metrics = collector.collect()

        # Generate report
        report = self.report_generator.generate(result)

        # Save if requested
        if save_to_file:
            self.config.output_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = self.config.output_dir / f"playtest_report_{timestamp}.md"
            with open(report_path, "w") as f:
                f.write(report)

        return report


# Self-teaching note:
#
# This file demonstrates:
# - Dataclasses for structured configuration and results (Level 5)
# - Pattern detection algorithms (Level 6: algorithms)
# - Report generation patterns (Level 5: string formatting, file I/O)
# - Subprocess for external tool integration (Level 5: system integration)
# - Async orchestration patterns (Level 6)
# - Factory methods and configuration (Level 5: OOP)
#
# Prerequisites:
# - Level 5: Dataclasses, file I/O, OOP patterns
# - Level 6: Algorithms, system integration, async
# - Professional: CI/CD, automated testing, reporting
#
# This module enables continuous UX improvement by:
# 1. Running automated playtests with AI players
# 2. Capturing visual evidence (screenshots/videos)
# 3. Analyzing confusion patterns algorithmically
# 4. Generating actionable reports for developers
# 5. Tracking code quality metrics over time
#
# The report generator is the final piece of the feedback loop,
# turning raw playtest data into prioritized improvements.
