"""
Weakness Detector - Gentle Resurfacing of Struggle Areas

Tracks concepts where the player struggles and gently resurfaces
them for practice WITHOUT making it feel like annoying drilling.

Key principles:
1. Notice struggles, don't punish them
2. Resurface weaknesses gently (disguised, scaffolded, fun-integrated)
3. Respect cooldown periods (don't be annoying)
4. Track improvement, celebrate progress
5. Consider prerequisite gaps as root causes

Self-teaching note:
This file demonstrates:
- Data aggregation patterns (Level 4: collections)
- Statistical analysis (Level 5: calculations)
- Strategy pattern for resurfacing approaches (Level 6: design patterns)
- Time-based scheduling (Level 4: datetime)
- JSON serialization (Level 4)
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from pathlib import Path
import json


@dataclass
class StrugglePattern:
    """
    Tracks struggle patterns for a single concept.

    Records attempts, successes, failures, time taken, and hints used
    to build a complete picture of where a player struggles.
    """

    concept_id: str

    # Attempt tracking
    success_count: int = 0
    failure_count: int = 0

    # Time tracking
    total_time_seconds: float = 0.0
    attempt_times: List[float] = field(default_factory=list)

    # Hint usage
    total_hints_used: int = 0

    # Timestamps
    first_seen: datetime = field(default_factory=datetime.now)
    last_practiced: datetime = field(default_factory=datetime.now)

    # Recent attempt results (for trend analysis)
    recent_results: List[bool] = field(default_factory=list)  # Last 10
    MAX_RECENT = 10

    @property
    def total_attempts(self) -> int:
        """Total number of attempts."""
        return self.success_count + self.failure_count

    @property
    def success_rate(self) -> float:
        """Success rate as a float 0.0-1.0."""
        if self.total_attempts == 0:
            return 0.0
        return self.success_count / self.total_attempts

    @property
    def average_time(self) -> float:
        """Average time per attempt in seconds."""
        if not self.attempt_times:
            return 0.0
        return sum(self.attempt_times) / len(self.attempt_times)

    @property
    def average_hints(self) -> float:
        """Average hints used per attempt."""
        if self.total_attempts == 0:
            return 0.0
        return self.total_hints_used / self.total_attempts

    def record_attempt(
        self,
        success: bool,
        time_seconds: float,
        hints_used: int
    ):
        """
        Record an attempt at this concept.

        Args:
            success: Whether the attempt succeeded
            time_seconds: How long the attempt took
            hints_used: How many hints were used
        """
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1

        self.total_time_seconds += time_seconds
        self.attempt_times.append(time_seconds)
        self.total_hints_used += hints_used
        self.last_practiced = datetime.now()

        # Track recent results for trend analysis
        self.recent_results.append(success)
        if len(self.recent_results) > self.MAX_RECENT:
            self.recent_results = self.recent_results[-self.MAX_RECENT:]

    def get_recent_success_rate(self) -> float:
        """Get success rate for recent attempts only."""
        if not self.recent_results:
            return 0.0
        return sum(1 for r in self.recent_results if r) / len(self.recent_results)

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "concept_id": self.concept_id,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "total_time_seconds": self.total_time_seconds,
            "attempt_times": self.attempt_times[-20:],  # Keep last 20
            "total_hints_used": self.total_hints_used,
            "first_seen": self.first_seen.isoformat(),
            "last_practiced": self.last_practiced.isoformat(),
            "recent_results": self.recent_results,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "StrugglePattern":
        """Deserialize from dictionary."""
        pattern = cls(concept_id=data["concept_id"])
        pattern.success_count = data.get("success_count", 0)
        pattern.failure_count = data.get("failure_count", 0)
        pattern.total_time_seconds = data.get("total_time_seconds", 0.0)
        pattern.attempt_times = data.get("attempt_times", [])
        pattern.total_hints_used = data.get("total_hints_used", 0)

        if data.get("first_seen"):
            pattern.first_seen = datetime.fromisoformat(data["first_seen"])
        if data.get("last_practiced"):
            pattern.last_practiced = datetime.fromisoformat(data["last_practiced"])

        pattern.recent_results = data.get("recent_results", [])

        return pattern


@dataclass
class WeaknessProfile:
    """
    Complete weakness profile for a player.

    Aggregates struggle patterns across all concepts.
    """

    player_id: str
    _patterns: Dict[str, StrugglePattern] = field(default_factory=dict)

    def get_all_patterns(self) -> Dict[str, StrugglePattern]:
        """Get all tracked patterns."""
        return dict(self._patterns)

    def get_pattern(self, concept_id: str) -> Optional[StrugglePattern]:
        """Get pattern for a specific concept."""
        return self._patterns.get(concept_id)

    def get_weakness_count(self) -> int:
        """Get number of tracked concepts."""
        return len(self._patterns)

    def record_attempt(
        self,
        concept_id: str,
        success: bool,
        time_seconds: float,
        hints_used: int
    ):
        """Record an attempt for a concept."""
        if concept_id not in self._patterns:
            self._patterns[concept_id] = StrugglePattern(concept_id=concept_id)

        self._patterns[concept_id].record_attempt(success, time_seconds, hints_used)

    def get_weak_concepts(self, threshold: float = 0.5) -> List[str]:
        """
        Get concepts with success rate below threshold.

        Args:
            threshold: Success rate threshold (0.0-1.0)

        Returns:
            List of weak concept IDs
        """
        weak = []
        for concept_id, pattern in self._patterns.items():
            if pattern.success_rate < threshold and pattern.total_attempts >= 2:
                weak.append(concept_id)
        return weak

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "player_id": self.player_id,
            "patterns": {
                cid: p.to_dict() for cid, p in self._patterns.items()
            }
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WeaknessProfile":
        """Deserialize from dictionary."""
        profile = cls(player_id=data.get("player_id", "unknown"))

        for cid, pdata in data.get("patterns", {}).items():
            profile._patterns[cid] = StrugglePattern.from_dict(pdata)

        return profile


@dataclass
class ResurfaceStrategy:
    """
    Strategy for resurfacing a weak concept.

    Determines when and how to resurface without being annoying.
    """

    concept_id: str
    should_resurface: bool = False

    # Timing
    cooldown_hours: float = 4.0
    next_review: Optional[datetime] = None

    # Approach (how to resurface)
    approach: str = "direct"  # direct, disguised, scaffolded, fun_integration

    # Difficulty adjustment (-1 = easier, 0 = same, +1 = harder)
    difficulty_adjustment: int = 0

    # Reason for this strategy
    reason: str = ""


@dataclass
class WeaknessRecommendation:
    """A recommendation to practice a weak concept."""

    concept_id: str
    approach: str
    reason: str
    severity: float  # 0-1, higher = more severe weakness
    priority: int = 0


class WeaknessDetector:
    """
    Detects weaknesses and recommends gentle practice.

    Uses multiple strategies to resurface weak concepts without
    making the player feel bad or annoyed.

    Resurfacing strategies:
    1. Disguised: Embed weak concept in fun challenge about something else
    2. Scaffolded: Break down into smaller pieces
    3. Fun integration: Mix with concepts the player enjoys
    4. Direct: Only for players who prefer direct feedback

    Usage:
        detector = WeaknessDetector()

        # Record attempts
        detector.record_challenge_result(profile, "loops", success=False, ...)

        # Get recommendations
        recommendations = detector.recommend_weakness_practice(profile)

        # Get resurface strategy for specific concept
        strategy = detector.get_resurface_strategy(profile, "loops")
    """

    # Thresholds
    WEAKNESS_THRESHOLD = 0.5  # Below this = weak
    MIN_ATTEMPTS_FOR_WEAKNESS = 2
    DEFAULT_COOLDOWN_HOURS = 4.0

    # Severity thresholds
    SEVERE_THRESHOLD = 0.3
    MODERATE_THRESHOLD = 0.5

    def __init__(self):
        pass

    def identify_weaknesses(
        self,
        profile: WeaknessProfile,
        min_attempts: int = None
    ) -> List[str]:
        """
        Identify weak concepts in a profile.

        Args:
            profile: Player's weakness profile
            min_attempts: Minimum attempts to consider (default 2)

        Returns:
            List of weak concept IDs
        """
        min_attempts = min_attempts or self.MIN_ATTEMPTS_FOR_WEAKNESS

        weak = []
        for concept_id, pattern in profile.get_all_patterns().items():
            if pattern.total_attempts >= min_attempts:
                if pattern.success_rate < self.WEAKNESS_THRESHOLD:
                    weak.append(concept_id)

        return weak

    def calculate_severity(
        self,
        profile: WeaknessProfile,
        concept_id: str
    ) -> float:
        """
        Calculate how severe a weakness is.

        Args:
            profile: Player's weakness profile
            concept_id: Concept to evaluate

        Returns:
            Severity score 0.0-1.0 (higher = more severe)
        """
        pattern = profile.get_pattern(concept_id)
        if not pattern:
            return 0.0

        # Factors:
        # 1. Inverse of success rate
        success_factor = 1.0 - pattern.success_rate

        # 2. Number of failures (more failures = more severe)
        failure_factor = min(1.0, pattern.failure_count / 10.0)

        # 3. Hints usage (more hints = more severe)
        hint_factor = min(1.0, pattern.average_hints / 5.0)

        # 4. Time factor (taking longer = more severe)
        # Assume 60 seconds is "normal"
        time_factor = min(1.0, pattern.average_time / 180.0)

        # Weighted combination
        severity = (
            success_factor * 0.4 +
            failure_factor * 0.3 +
            hint_factor * 0.2 +
            time_factor * 0.1
        )

        return severity

    def is_improving(
        self,
        profile: WeaknessProfile,
        concept_id: str,
        window: int = 5
    ) -> bool:
        """
        Check if player is improving on a concept.

        Args:
            profile: Player's weakness profile
            concept_id: Concept to check
            window: Number of recent attempts to consider

        Returns:
            True if showing improvement
        """
        pattern = profile.get_pattern(concept_id)
        if not pattern:
            return False

        recent = pattern.recent_results
        if len(recent) < window:
            return False

        # Compare first half to second half
        mid = len(recent) // 2
        first_half = recent[:mid]
        second_half = recent[mid:]

        first_rate = sum(1 for r in first_half if r) / len(first_half) if first_half else 0
        second_rate = sum(1 for r in second_half if r) / len(second_half) if second_half else 0

        return second_rate > first_rate

    def suggest_prerequisite_review(
        self,
        profile: WeaknessProfile,
        concept_id: str,
        prerequisites: Dict[str, List[str]]
    ) -> List[str]:
        """
        Suggest prerequisites that might be causing the struggle.

        Args:
            profile: Player's weakness profile
            concept_id: Concept they're struggling with
            prerequisites: Map of concept -> its prerequisites

        Returns:
            List of prerequisite concepts to review
        """
        if concept_id not in prerequisites:
            return []

        suggestions = []
        for prereq in prerequisites[concept_id]:
            prereq_pattern = profile.get_pattern(prereq)

            if prereq_pattern is None:
                # Never practiced this prerequisite
                suggestions.append(prereq)
            elif prereq_pattern.success_rate < self.WEAKNESS_THRESHOLD:
                # Also weak on prerequisite
                suggestions.append(prereq)

        return suggestions

    def get_resurface_strategy(
        self,
        profile: WeaknessProfile,
        concept_id: str
    ) -> ResurfaceStrategy:
        """
        Get the strategy for resurfacing a weak concept.

        Args:
            profile: Player's weakness profile
            concept_id: Concept to resurface

        Returns:
            ResurfaceStrategy with timing and approach
        """
        pattern = profile.get_pattern(concept_id)
        if not pattern:
            return ResurfaceStrategy(
                concept_id=concept_id,
                should_resurface=False,
                reason="No data for this concept"
            )

        # Check cooldown
        hours_since = (datetime.now() - pattern.last_practiced).total_seconds() / 3600
        cooldown_met = hours_since >= self.DEFAULT_COOLDOWN_HOURS

        if not cooldown_met:
            return ResurfaceStrategy(
                concept_id=concept_id,
                should_resurface=False,
                cooldown_hours=self.DEFAULT_COOLDOWN_HOURS - hours_since,
                reason="Still in cooldown period"
            )

        # Check severity
        severity = self.calculate_severity(profile, concept_id)

        # Determine approach based on severity
        if severity >= 0.7:
            # Very weak - use disguised or scaffolded
            approach = "disguised"
            difficulty_adjustment = -1  # Easier
            reason = "Very challenging - using gentle approach"
        elif severity >= 0.5:
            # Moderately weak
            approach = "scaffolded"
            difficulty_adjustment = 0
            reason = "Needs more practice - breaking it down"
        else:
            # Mild weakness
            approach = "fun_integration"
            difficulty_adjustment = 0
            reason = "Light refresh - mixing with fun content"

        return ResurfaceStrategy(
            concept_id=concept_id,
            should_resurface=True,
            approach=approach,
            difficulty_adjustment=difficulty_adjustment,
            reason=reason
        )

    def recommend_weakness_practice(
        self,
        profile: WeaknessProfile,
        max_count: int = 3,
        min_cooldown_hours: float = None,
        prefer_disguised: bool = False
    ) -> List[WeaknessRecommendation]:
        """
        Get recommendations for weakness practice.

        Args:
            profile: Player's weakness profile
            max_count: Maximum recommendations to return
            min_cooldown_hours: Override default cooldown
            prefer_disguised: Use disguised approach when possible

        Returns:
            List of WeaknessRecommendation objects
        """
        cooldown = min_cooldown_hours or self.DEFAULT_COOLDOWN_HOURS
        now = datetime.now()

        recommendations = []

        for concept_id, pattern in profile.get_all_patterns().items():
            # Check cooldown
            hours_since = (now - pattern.last_practiced).total_seconds() / 3600
            if hours_since < cooldown:
                continue

            # Check if weak enough to recommend
            if pattern.success_rate >= self.WEAKNESS_THRESHOLD:
                continue

            if pattern.total_attempts < self.MIN_ATTEMPTS_FOR_WEAKNESS:
                continue

            # Calculate severity and create recommendation
            severity = self.calculate_severity(profile, concept_id)

            approach = "disguised" if prefer_disguised or severity >= 0.6 else "scaffolded"

            rec = WeaknessRecommendation(
                concept_id=concept_id,
                approach=approach,
                reason=f"Success rate {pattern.success_rate:.0%}, "
                       f"severity {severity:.2f}",
                severity=severity,
            )

            recommendations.append(rec)

        # Sort by severity (most severe first)
        recommendations.sort(key=lambda r: r.severity, reverse=True)

        return recommendations[:max_count]

    def record_challenge_result(
        self,
        profile: WeaknessProfile,
        concept_id: str,
        success: bool,
        time_seconds: float,
        hints_used: int,
        attempts: int = 1
    ):
        """
        Record a challenge result into the weakness profile.

        Args:
            profile: Player's weakness profile
            concept_id: Concept being practiced
            success: Whether they succeeded
            time_seconds: Time taken
            hints_used: Hints used
            attempts: Number of attempts (for multi-attempt challenges)
        """
        profile.record_attempt(
            concept_id=concept_id,
            success=success,
            time_seconds=time_seconds,
            hints_used=hints_used
        )


# Self-teaching note:
#
# This file demonstrates:
# - Data aggregation (StrugglePattern collects attempt data)
# - Statistical analysis (success rate, severity calculation)
# - Strategy pattern (different resurfacing approaches)
# - Time-based scheduling (cooldown periods)
# - Dataclasses for clean data structures
# - Property decorators for computed values
#
# Key concepts for gentle learning:
# 1. Don't punish struggle - notice it quietly
# 2. Resurface weaknesses in non-obvious ways
# 3. Respect cooldowns - don't be annoying
# 4. Track trends - celebrate improvement
# 5. Consider root causes (prerequisites)
#
# The learner will encounter this AFTER mastering:
# - Level 3: Functions and classes
# - Level 4: Collections, datetime, JSON
# - Level 5: Dataclasses, properties
# - Level 6: Design patterns, algorithms
