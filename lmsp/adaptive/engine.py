"""
Adaptive Engine
===============

The core adaptive learning engine that orchestrates:
- Spaced repetition scheduling
- Fun pattern tracking
- Weakness detection
- Project-driven curriculum generation

This is the AI that learns YOUR learning style.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, timedelta
import json
from pathlib import Path

from lmsp.input.emotional import EmotionalState, EmotionalDimension


@dataclass
class LearnerProfile:
    """
    Everything we know about how YOU learn.

    This is your personalized learning DNA.
    """
    # Identity
    player_id: str

    # Learning patterns
    preferred_challenge_types: list[str] = field(default_factory=list)
    struggle_patterns: dict[str, int] = field(default_factory=dict)  # concept -> fail count
    mastery_levels: dict[str, int] = field(default_factory=dict)     # concept -> 0-4

    # Engagement patterns
    peak_focus_times: list[int] = field(default_factory=list)  # Hours of day
    session_duration_sweet_spot: int = 25  # minutes
    break_frequency_preference: int = 5    # challenges before suggesting break

    # Emotional patterns
    frustration_threshold: float = 0.6     # When to intervene
    flow_trigger_concepts: list[str] = field(default_factory=list)

    # Project goals
    current_goal: Optional[str] = None
    goal_concepts_needed: list[str] = field(default_factory=list)

    # Spaced repetition data
    concept_last_seen: dict[str, datetime] = field(default_factory=dict)
    concept_interval: dict[str, timedelta] = field(default_factory=dict)

    def to_json(self) -> str:
        """Serialize for persistence."""
        data = {
            "player_id": self.player_id,
            "preferred_challenge_types": self.preferred_challenge_types,
            "struggle_patterns": self.struggle_patterns,
            "mastery_levels": self.mastery_levels,
            "peak_focus_times": self.peak_focus_times,
            "session_duration_sweet_spot": self.session_duration_sweet_spot,
            "break_frequency_preference": self.break_frequency_preference,
            "frustration_threshold": self.frustration_threshold,
            "flow_trigger_concepts": self.flow_trigger_concepts,
            "current_goal": self.current_goal,
            "goal_concepts_needed": self.goal_concepts_needed,
            # datetime fields need special handling
            "concept_last_seen": {
                k: v.isoformat() for k, v in self.concept_last_seen.items()
            },
            "concept_interval": {
                k: v.total_seconds() for k, v in self.concept_interval.items()
            },
        }
        return json.dumps(data, indent=2)

    @classmethod
    def from_json(cls, data: str) -> "LearnerProfile":
        """Deserialize from persistence."""
        parsed = json.loads(data)
        # Convert datetime strings back
        if "concept_last_seen" in parsed:
            parsed["concept_last_seen"] = {
                k: datetime.fromisoformat(v)
                for k, v in parsed["concept_last_seen"].items()
            }
        if "concept_interval" in parsed:
            parsed["concept_interval"] = {
                k: timedelta(seconds=v)
                for k, v in parsed["concept_interval"].items()
            }
        return cls(**parsed)


@dataclass
class AdaptiveRecommendation:
    """What the adaptive engine thinks you should do next."""
    action: str  # "challenge", "review", "break", "project_step"
    concept: Optional[str] = None
    challenge_id: Optional[str] = None
    reason: str = ""
    confidence: float = 0.5  # How confident are we this is right for you?


class AdaptiveEngine:
    """
    The brain that learns your brain.

    Usage:
        engine = AdaptiveEngine(profile)
        engine.observe_attempt(concept="list_comprehensions", success=True, time_seconds=45)
        engine.observe_emotion(EmotionalDimension.ENJOYMENT, 0.8)
        recommendation = engine.recommend_next()
    """

    def __init__(self, profile: LearnerProfile):
        self.profile = profile
        self.emotional_state = EmotionalState()
        self._session_start = datetime.now()
        self._challenges_this_session = 0

    def observe_attempt(
        self,
        concept: str,
        success: bool,
        time_seconds: float,
        hints_used: int = 0
    ):
        """Record an attempt at a concept."""
        now = datetime.now()

        # Update last seen
        self.profile.concept_last_seen[concept] = now

        if success:
            # Increase mastery
            current = self.profile.mastery_levels.get(concept, 0)
            if hints_used == 0 and time_seconds < 60:
                # Quick, clean solve - big boost
                self.profile.mastery_levels[concept] = min(4, current + 1)
            else:
                # Slower or with hints - smaller boost
                self.profile.mastery_levels[concept] = min(4, current + 0.5)

            # Increase interval for spaced repetition
            current_interval = self.profile.concept_interval.get(
                concept, timedelta(hours=1)
            )
            self.profile.concept_interval[concept] = current_interval * 2

        else:
            # Record struggle
            self.profile.struggle_patterns[concept] = (
                self.profile.struggle_patterns.get(concept, 0) + 1
            )

            # Decrease interval - need to see this more often
            current_interval = self.profile.concept_interval.get(
                concept, timedelta(hours=1)
            )
            self.profile.concept_interval[concept] = current_interval / 2

        self._challenges_this_session += 1

    def observe_emotion(self, dimension: EmotionalDimension, value: float, context: str = ""):
        """Record emotional feedback."""
        self.emotional_state.record(dimension, value, context)

        # Update profile based on patterns
        if dimension == EmotionalDimension.ENJOYMENT and value > 0.8:
            if context and context not in self.profile.flow_trigger_concepts:
                self.profile.flow_trigger_concepts.append(context)

        if dimension == EmotionalDimension.FRUSTRATION and value > 0.7:
            # Lower threshold for this player
            self.profile.frustration_threshold = max(
                0.3, self.profile.frustration_threshold - 0.05
            )

    def recommend_next(self) -> AdaptiveRecommendation:
        """What should the player do next?"""

        # Priority 1: Do they need a break?
        if self._needs_break():
            return AdaptiveRecommendation(
                action="break",
                reason="You've been grinding hard. Take 5?"
            )

        # Priority 2: Are they frustrated? Offer something they're good at
        if self.emotional_state.get_frustration() > self.profile.frustration_threshold:
            flow_concept = self._find_flow_concept()
            if flow_concept:
                return AdaptiveRecommendation(
                    action="challenge",
                    concept=flow_concept,
                    reason="Let's do something you enjoy to reset",
                    confidence=0.8
                )

        # Priority 3: Spaced repetition - something due for review
        due_concept = self._find_due_for_review()
        if due_concept:
            return AdaptiveRecommendation(
                action="review",
                concept=due_concept,
                reason=f"Time to refresh {due_concept}",
                confidence=0.7
            )

        # Priority 4: Project goal - next step toward their goal
        if self.profile.current_goal:
            next_concept = self._find_next_for_goal()
            if next_concept:
                return AdaptiveRecommendation(
                    action="project_step",
                    concept=next_concept,
                    reason=f"This brings you closer to: {self.profile.current_goal}",
                    confidence=0.9
                )

        # Priority 5: Weakness drilling - something they struggle with
        weak_concept = self._find_weakness_to_drill()
        if weak_concept:
            return AdaptiveRecommendation(
                action="challenge",
                concept=weak_concept,
                reason="Let's strengthen this one",
                confidence=0.6
            )

        # Default: Something new and fun
        return AdaptiveRecommendation(
            action="challenge",
            reason="Explore something new!",
            confidence=0.5
        )

    def _needs_break(self) -> bool:
        """Should we suggest a break?"""
        session_duration = (datetime.now() - self._session_start).total_seconds() / 60

        return (
            session_duration > self.profile.session_duration_sweet_spot or
            self._challenges_this_session >= self.profile.break_frequency_preference or
            self.emotional_state.needs_break()
        )

    def _find_flow_concept(self) -> Optional[str]:
        """Find a concept that puts them in flow."""
        for concept in self.profile.flow_trigger_concepts:
            if self.profile.mastery_levels.get(concept, 0) >= 2:
                return concept
        return None

    def _find_due_for_review(self) -> Optional[str]:
        """Find a concept due for spaced repetition review."""
        now = datetime.now()
        for concept, last_seen in self.profile.concept_last_seen.items():
            interval = self.profile.concept_interval.get(concept, timedelta(hours=1))
            if now - last_seen > interval:
                return concept
        return None

    def _find_next_for_goal(self) -> Optional[str]:
        """Find the next concept needed for their project goal."""
        for concept in self.profile.goal_concepts_needed:
            if self.profile.mastery_levels.get(concept, 0) < 2:
                return concept
        return None

    def _find_weakness_to_drill(self) -> Optional[str]:
        """Find a concept they struggle with that needs work."""
        # Sort by struggle count, pick the worst one they haven't mastered
        struggles = sorted(
            self.profile.struggle_patterns.items(),
            key=lambda x: x[1],
            reverse=True
        )
        for concept, count in struggles:
            if count >= 2 and self.profile.mastery_levels.get(concept, 0) < 3:
                return concept
        return None

    def save(self, path: Path):
        """Save learner profile to disk."""
        path.write_text(self.profile.to_json())

    @classmethod
    def load(cls, path: Path) -> "AdaptiveEngine":
        """Load learner profile from disk."""
        profile = LearnerProfile.from_json(path.read_text())
        return cls(profile)


# Self-teaching note:
#
# This file demonstrates:
# - Complex dataclasses with default_factory (Level 5+)
# - Type hints with Optional and dict (Professional Python)
# - datetime and timedelta (Standard library)
# - JSON serialization/deserialization patterns
# - Property-based logic and decision trees
# - The Strategy pattern (implicit in recommend_next)
#
# The learner will encounter this AFTER mastering classes,
# so they can understand and modify this code themselves.
