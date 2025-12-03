"""
WebPlaytester - AI-Driven UX Issue Discovery System
=====================================================

Combines ZAI player AI with Playwright browser automation to:
1. Navigate web UI automatically
2. Record confusion/friction points
3. Capture screenshots at struggle moments
4. Generate actionable UX improvement suggestions

This module enables automated discovery of UX issues by analyzing
how an AI player interacts with the web interface.

Self-teaching note:

This file demonstrates:
- Dataclasses for state management (Level 5)
- Time-based event tracking (Level 5)
- Pattern detection algorithms (Level 6)
- Report generation (Level 5)
- Integration with playtest recording (Level 6)

Prerequisites:
- Level 4: Classes, dictionaries, file I/O
- Level 5: Dataclasses, time module, JSON serialization
- Level 6: Integration patterns, web automation
"""

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import tempfile

from datetime import datetime
from lmsp.multiplayer.player_zero.tas.recorder import (
    PlaytestEvent,
    EventType,
)


@dataclass
class FrictionPoint:
    """A detected point of friction/confusion."""

    type: str
    description: str
    element: Optional[str] = None
    challenge_id: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class UXSuggestion:
    """A UX improvement suggestion."""

    suggestion: str
    priority: str  # "low", "medium", "high", "critical"
    friction_type: str
    affected_element: Optional[str] = None


class WebPlaytester:
    """
    AI-driven web UI playtester that detects UX issues.

    Combines:
    - ZAI player for AI-driven navigation and solution generation
    - Event recording for friction detection
    - Screenshot capture at struggle moments
    - UX improvement suggestion generation
    """

    def __init__(
        self,
        zai_player: Any,
        base_url: str,
        screenshots_dir: Optional[Path] = None,
        friction_threshold: float = 0.5,
    ):
        """
        Initialize the WebPlaytester.

        Args:
            zai_player: ZAIPlayer instance for AI capabilities
            base_url: Base URL of the web application
            screenshots_dir: Directory for screenshots (defaults to temp)
            friction_threshold: Threshold for friction detection (0.0-1.0)
        """
        self.zai_player = zai_player
        self.base_url = base_url
        self.screenshots_dir = screenshots_dir or Path(tempfile.mkdtemp())
        self.friction_threshold = friction_threshold

        # Event tracking
        self.navigation_history: List[Dict[str, Any]] = []
        self.interaction_history: List[Dict[str, Any]] = []
        self.submissions: List[Dict[str, Any]] = []
        self.screenshots: List[Dict[str, Any]] = []
        self.friction_points: List[Dict[str, Any]] = []

        # ZAI player state tracking
        self.zai_confusion_history: List[Dict[str, Any]] = []

        # Session tracking
        self.current_session: Dict[str, Any] = {}
        self._session_active = False
        self._last_interaction_time: Optional[float] = None
        self._screenshot_counter = 0

    # ========== Navigation Recording ==========

    def record_navigation(self, url: str) -> None:
        """
        Record a navigation event.

        Args:
            url: URL navigated to
        """
        self.navigation_history.append({
            "url": url,
            "timestamp": time.time(),
        })

    def record_interaction(
        self,
        element_type: str,
        action: str,
        element_id: Optional[str] = None,
        timestamp: Optional[float] = None,
        duration_since_last: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        """
        Record an element interaction.

        Args:
            element_type: Type of element (button, input, etc.)
            action: Action performed (click, type, focus, etc.)
            element_id: Optional element ID
            timestamp: Optional timestamp override
            duration_since_last: Optional duration since last interaction
            **kwargs: Additional metadata
        """
        current_time = time.time()

        # Calculate duration since last interaction
        if duration_since_last is None and self._last_interaction_time is not None:
            duration_since_last = current_time - self._last_interaction_time

        interaction = {
            "element_type": element_type,
            "action": action,
            "element_id": element_id,
            "timestamp": timestamp or current_time,
            "duration_since_last": duration_since_last or 0.0,
            **kwargs,
        }

        self.interaction_history.append(interaction)
        self._last_interaction_time = current_time

    def record_submission(
        self,
        challenge_id: str,
        success: bool,
        error: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Record a code submission.

        Args:
            challenge_id: ID of the challenge
            success: Whether submission was successful
            error: Error message if failed
            **kwargs: Additional metadata
        """
        self.submissions.append({
            "challenge_id": challenge_id,
            "success": success,
            "error": error,
            "timestamp": time.time(),
            **kwargs,
        })

        # Update session if active
        if self._session_active:
            self.current_session["submissions"] = self.current_session.get("submissions", 0) + 1
            if success:
                self.current_session["success"] = True

    # ========== Friction Detection ==========

    def detect_friction_points(self) -> List[Dict[str, Any]]:
        """
        Analyze recorded events to detect friction points.

        Returns:
            List of detected friction points
        """
        friction_points = []

        # Detect rapid clicks
        rapid_clicks = self._detect_rapid_clicks()
        if rapid_clicks:
            friction_points.append(rapid_clicks)

        # Detect navigation confusion
        nav_confusion = self._detect_navigation_confusion()
        if nav_confusion:
            friction_points.append(nav_confusion)

        # Detect long waits
        long_waits = self._detect_long_waits()
        friction_points.extend(long_waits)

        # Detect repeated failures
        repeated_failures = self._detect_repeated_failures()
        if repeated_failures:
            friction_points.append(repeated_failures)

        return friction_points

    def _detect_rapid_clicks(self) -> Optional[Dict[str, Any]]:
        """Detect rapid clicking patterns (frustration indicator)."""
        if len(self.interaction_history) < 5:
            return None

        # Look for 5+ clicks in quick succession
        click_events = [
            i for i in self.interaction_history
            if i.get("action") == "click"
        ]

        if len(click_events) >= 5:
            # Check if any 5 consecutive clicks happened within 2 seconds
            for i in range(len(click_events) - 4):
                window = click_events[i:i + 5]
                timestamps = [e.get("timestamp", 0) for e in window]
                if max(timestamps) - min(timestamps) < 2.0:
                    return {
                        "type": "rapid_clicks",
                        "description": f"{len(window)} rapid clicks detected (frustration indicator)",
                        "element": window[0].get("element_id"),
                    }

        return None

    def _detect_navigation_confusion(self) -> Optional[Dict[str, Any]]:
        """Detect back-and-forth navigation patterns (confusion indicator)."""
        if len(self.navigation_history) < 4:
            return None

        # Look for A → B → A → B pattern
        urls = [n.get("url") for n in self.navigation_history]

        for i in range(len(urls) - 3):
            pattern = urls[i:i + 4]
            if pattern[0] == pattern[2] and pattern[1] == pattern[3] and pattern[0] != pattern[1]:
                return {
                    "type": "navigation_confusion",
                    "description": f"Back-and-forth navigation between {pattern[0]} and {pattern[1]}",
                }

        return None

    def _detect_long_waits(self) -> List[Dict[str, Any]]:
        """Detect long waits between interactions (confusion/stuck indicator)."""
        long_waits = []

        for interaction in self.interaction_history:
            duration = interaction.get("duration_since_last", 0)
            if duration > 20.0:  # 20 seconds threshold
                long_waits.append({
                    "type": "long_wait",
                    "description": f"Long wait of {duration:.1f} seconds before {interaction.get('action')}",
                    "element": interaction.get("element_id"),
                })

        return long_waits

    def _detect_repeated_failures(self) -> Optional[Dict[str, Any]]:
        """Detect repeated failed submissions (stuck indicator)."""
        # Group submissions by challenge
        challenge_submissions: Dict[str, List[bool]] = {}
        for sub in self.submissions:
            cid = sub.get("challenge_id", "unknown")
            if cid not in challenge_submissions:
                challenge_submissions[cid] = []
            challenge_submissions[cid].append(sub.get("success", False))

        # Check for 3+ consecutive failures
        for challenge_id, results in challenge_submissions.items():
            consecutive_failures = 0
            for success in results:
                if not success:
                    consecutive_failures += 1
                    if consecutive_failures >= 3:
                        return {
                            "type": "repeated_failures",
                            "description": f"{consecutive_failures} consecutive failures on challenge {challenge_id}",
                            "challenge_id": challenge_id,
                        }
                else:
                    consecutive_failures = 0

        return None

    def calculate_friction_score(self) -> float:
        """
        Calculate overall friction score (0.0-1.0).

        Returns:
            Friction score where higher = more friction
        """
        score = 0.0

        # Factor: Failed submissions
        total_subs = len(self.submissions)
        if total_subs > 0:
            failures = sum(1 for s in self.submissions if not s.get("success"))
            failure_rate = failures / total_subs
            score += failure_rate * 0.4

        # Factor: Friction points
        friction_points = self.detect_friction_points()
        score += min(0.4, len(friction_points) * 0.1)

        # Factor: Navigation confusion
        if any(fp.get("type") == "navigation_confusion" for fp in friction_points):
            score += 0.1

        # Factor: Long waits
        long_waits = sum(1 for fp in friction_points if fp.get("type") == "long_wait")
        score += min(0.1, long_waits * 0.02)

        return min(1.0, score)

    # ========== Screenshot Capture ==========

    def record_friction_screenshot(
        self,
        reason: str,
        page_url: str,
        element_selector: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Record a screenshot capture at a friction moment.

        Args:
            reason: Reason for the screenshot
            page_url: Current page URL
            element_selector: Optional element selector

        Returns:
            Screenshot metadata
        """
        self._screenshot_counter += 1
        timestamp = time.time()

        # Generate unique filename
        filename = f"friction_{self._screenshot_counter}_{int(timestamp)}.png"
        path = str(self.screenshots_dir / filename)

        screenshot = {
            "reason": reason,
            "page_url": page_url,
            "element_selector": element_selector,
            "timestamp": timestamp,
            "path": path,
        }

        self.screenshots.append(screenshot)
        return screenshot

    # ========== UX Suggestions ==========

    def generate_ux_suggestions(self) -> List[Dict[str, Any]]:
        """
        Generate UX improvement suggestions from friction points.

        Returns:
            List of prioritized UX suggestions
        """
        suggestions = []

        for friction in self.friction_points:
            friction_type = friction.get("type", "unknown")

            if friction_type == "rapid_clicks":
                suggestions.append({
                    "suggestion": "Add visual feedback for click actions. Consider disabling button during processing to prevent rapid clicking.",
                    "priority": "high",
                    "friction_type": friction_type,
                    "affected_element": friction.get("element"),
                })

            elif friction_type == "repeated_failures":
                suggestions.append({
                    "suggestion": "Provide more specific error feedback. Consider adding hints or examples after multiple failures.",
                    "priority": "high",
                    "friction_type": friction_type,
                    "affected_element": friction.get("challenge_id"),
                })

            elif friction_type == "navigation_confusion":
                suggestions.append({
                    "suggestion": "Add clearer navigation cues. Consider breadcrumbs or a progress indicator.",
                    "priority": "medium",
                    "friction_type": friction_type,
                })

            elif friction_type == "long_wait":
                suggestions.append({
                    "suggestion": "User hesitated for extended time. Consider adding contextual help or simplifying the interface.",
                    "priority": "medium",
                    "friction_type": friction_type,
                    "affected_element": friction.get("element"),
                })

            else:
                suggestions.append({
                    "suggestion": f"Review UX for {friction_type} issue: {friction.get('description', 'Unknown issue')}",
                    "priority": "low",
                    "friction_type": friction_type,
                })

        return suggestions

    # ========== Report Generation ==========

    def generate_report(self) -> str:
        """
        Generate a comprehensive playtest report.

        Returns:
            Markdown report string
        """
        friction_score = self.calculate_friction_score()
        friction_points = self.detect_friction_points()
        suggestions = self.generate_ux_suggestions()

        lines = [
            "# WebPlaytester Report",
            "",
            "## Summary",
            "",
            f"- **Pages Visited:** {len(self.navigation_history)}",
            f"- **Interactions:** {len(self.interaction_history)}",
            f"- **Submissions:** {len(self.submissions)}",
            f"- **Friction Score:** {friction_score:.2f}",
            "",
        ]

        # Navigation history
        if self.navigation_history:
            lines.extend([
                "## Navigation History",
                "",
            ])
            for nav in self.navigation_history:
                lines.append(f"- {nav.get('url')}")
            lines.append("")

        # Friction points
        if friction_points:
            lines.extend([
                "## Friction Points",
                "",
            ])
            for fp in friction_points:
                lines.append(f"- **{fp.get('type')}:** {fp.get('description')}")
            lines.append("")

        # Suggestions
        if suggestions:
            lines.extend([
                "## UX Improvement Suggestions",
                "",
            ])
            for s in suggestions:
                priority = s.get("priority", "medium").upper()
                lines.append(f"- [{priority}] {s.get('suggestion')}")
            lines.append("")

        return "\n".join(lines)

    def export_to_json(self, path: Path) -> None:
        """
        Export report data to JSON.

        Args:
            path: Output file path
        """
        data = {
            "navigation_history": self.navigation_history,
            "interaction_history": self.interaction_history,
            "submissions": self.submissions,
            "screenshots": self.screenshots,
            "friction_points": self.detect_friction_points(),
            "friction_score": self.calculate_friction_score(),
            "suggestions": self.generate_ux_suggestions(),
        }

        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    # ========== PlaytestRecorder Integration ==========

    def to_playtest_events(self) -> List[PlaytestEvent]:
        """
        Convert recorded events to PlaytestEvents for recorder integration.

        Returns:
            List of PlaytestEvent objects
        """
        events = []
        frame_counter = 0

        # Convert navigation events
        for nav in self.navigation_history:
            frame_counter += 1
            ts = nav.get("timestamp", time.time())
            events.append(PlaytestEvent(
                event_type=EventType.NAVIGATION,
                timestamp=datetime.fromtimestamp(ts) if isinstance(ts, (int, float)) else ts,
                frame_number=frame_counter,
                data={"url": nav.get("url")},
            ))

        # Convert interactions
        for interaction in self.interaction_history:
            frame_counter += 1
            ts = interaction.get("timestamp", time.time())
            events.append(PlaytestEvent(
                event_type=EventType.CODE_CHANGE,
                timestamp=datetime.fromtimestamp(ts) if isinstance(ts, (int, float)) else ts,
                frame_number=frame_counter,
                data={
                    "element_type": interaction.get("element_type"),
                    "action": interaction.get("action"),
                },
            ))

        # Convert submissions
        for sub in self.submissions:
            frame_counter += 1
            ts = sub.get("timestamp", time.time())
            event_type = EventType.TEST_PASS if sub.get("success") else EventType.TEST_FAIL
            events.append(PlaytestEvent(
                event_type=event_type,
                timestamp=datetime.fromtimestamp(ts) if isinstance(ts, (int, float)) else ts,
                frame_number=frame_counter,
                data={
                    "challenge_id": sub.get("challenge_id"),
                    "error": sub.get("error"),
                },
            ))

        return events

    # ========== ZAI Player Integration ==========

    async def attempt_challenge(self, challenge: Any) -> Optional[str]:
        """
        Use ZAI player to attempt a challenge.

        Args:
            challenge: Challenge object

        Returns:
            Generated solution or None
        """
        # Observe challenge with ZAI player
        self.zai_player.observe_challenge(challenge)

        # Generate solution
        solution = await self.zai_player.generate_solution(challenge)

        return solution

    def record_zai_state(self, zai_player: Any) -> None:
        """
        Record current ZAI player confusion state.

        Args:
            zai_player: ZAI player instance
        """
        confusion_score = getattr(zai_player, "confusion_score", 0.0)

        self.zai_confusion_history.append({
            "confusion_score": confusion_score,
            "timestamp": time.time(),
        })

    # ========== Session Management ==========

    def start_challenge_session(self, challenge_id: str) -> None:
        """
        Start a new challenge session.

        Args:
            challenge_id: ID of the challenge
        """
        self._session_active = True
        self.current_session = {
            "challenge_id": challenge_id,
            "start_time": time.time(),
            "submissions": 0,
            "success": False,
        }

    def end_challenge_session(self) -> Dict[str, Any]:
        """
        End the current challenge session.

        Returns:
            Session summary
        """
        self._session_active = False
        self.current_session["end_time"] = time.time()
        self.current_session["duration"] = (
            self.current_session["end_time"] - self.current_session["start_time"]
        )
        return self.current_session


# Self-teaching note:
#
# This file demonstrates:
# - Class design for complex state management (Level 5-6)
# - Time-based event tracking with timestamps (Level 5)
# - Pattern detection algorithms for UX analysis (Level 6)
# - Report generation in multiple formats (Level 5)
# - Integration with existing systems (Level 6)
# - Async/await for AI integration (Level 5)
#
# Prerequisites:
# - Level 4: Classes, dictionaries, file I/O
# - Level 5: Dataclasses, time module, JSON, async
# - Level 6: Integration patterns, algorithmic analysis
#
# The WebPlaytester enables:
# - Automated UX issue discovery without human testers
# - Objective friction measurement across the application
# - Prioritized improvement suggestions based on data
# - Integration with existing playtest recording systems
# - Screenshot evidence for UX issues
#
# This closes the feedback loop: AI plays → friction detected →
# suggestions generated → developers improve → AI plays again
