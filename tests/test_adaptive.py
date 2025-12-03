"""
Tests for the Adaptive Learning Engine

TDD: These tests were written BEFORE the implementation.
They define how the AI learns YOUR learning patterns.
"""

import pytest
from datetime import datetime, timedelta
from lmsp.adaptive.engine import (
    LearnerProfile,
    AdaptiveRecommendation,
    AdaptiveEngine,
)
from lmsp.input.emotional import EmotionalDimension


class TestLearnerProfile:
    """Test the learner profile data structure."""

    def test_profile_serializes_to_json(self):
        """Profile should serialize cleanly for persistence."""
        profile = LearnerProfile(
            player_id="test-player",
            preferred_challenge_types=["puzzle", "speedrun"],
            mastery_levels={"lists": 2, "loops": 3}
        )
        json_str = profile.to_json()
        assert "test-player" in json_str
        assert "puzzle" in json_str

    def test_profile_deserializes_from_json(self):
        """Profile should deserialize back correctly."""
        profile = LearnerProfile(
            player_id="test-player",
            preferred_challenge_types=["puzzle"],
            mastery_levels={"lists": 2}
        )
        json_str = profile.to_json()
        restored = LearnerProfile.from_json(json_str)

        assert restored.player_id == "test-player"
        assert "puzzle" in restored.preferred_challenge_types
        assert restored.mastery_levels["lists"] == 2


class TestAdaptiveEngine:
    """Test the adaptive learning engine."""

    @pytest.fixture
    def engine(self):
        """Create a fresh engine for each test."""
        profile = LearnerProfile(player_id="test")
        return AdaptiveEngine(profile)

    def test_successful_attempt_increases_mastery(self, engine):
        """Success should increase mastery level."""
        engine.observe_attempt("lists", success=True, time_seconds=30)
        assert engine.profile.mastery_levels["lists"] > 0

    def test_failed_attempt_records_struggle(self, engine):
        """Failure should record a struggle pattern."""
        engine.observe_attempt("lists", success=False, time_seconds=60)
        assert engine.profile.struggle_patterns["lists"] == 1

    def test_multiple_failures_accumulate(self, engine):
        """Multiple failures should accumulate."""
        engine.observe_attempt("lists", success=False, time_seconds=60)
        engine.observe_attempt("lists", success=False, time_seconds=60)
        engine.observe_attempt("lists", success=False, time_seconds=60)
        assert engine.profile.struggle_patterns["lists"] == 3

    def test_quick_clean_solve_gives_bigger_boost(self, engine):
        """Fast solve with no hints should give bigger mastery boost."""
        # Slow solve
        engine.observe_attempt("slow_concept", success=True, time_seconds=120, hints_used=2)
        # Fast solve
        engine.observe_attempt("fast_concept", success=True, time_seconds=30, hints_used=0)

        assert engine.profile.mastery_levels["fast_concept"] > engine.profile.mastery_levels["slow_concept"]

    def test_high_enjoyment_tracks_flow_concepts(self, engine):
        """High enjoyment should track which concepts trigger flow."""
        engine.observe_emotion(EmotionalDimension.ENJOYMENT, 0.9, "list_comprehensions")
        assert "list_comprehensions" in engine.profile.flow_trigger_concepts

    def test_recommendation_suggests_break_when_needed(self, engine):
        """Engine should suggest breaks when player is tired."""
        # Simulate long session
        engine._session_start = datetime.now() - timedelta(minutes=30)
        engine._challenges_this_session = 10

        rec = engine.recommend_next()
        assert rec.action == "break"

    def test_recommendation_offers_flow_concept_when_frustrated(self, engine):
        """When frustrated, offer something enjoyable."""
        # Set up a flow concept
        engine.profile.flow_trigger_concepts = ["fun_thing"]
        engine.profile.mastery_levels["fun_thing"] = 3

        # Make player frustrated
        for _ in range(10):
            engine.observe_emotion(EmotionalDimension.FRUSTRATION, 0.8, "")

        rec = engine.recommend_next()
        # Should either suggest break or fun thing
        assert rec.action in ["break", "challenge"]
        if rec.action == "challenge":
            assert rec.concept == "fun_thing"


class TestSpacedRepetition:
    """Test spaced repetition scheduling."""

    @pytest.fixture
    def engine(self):
        profile = LearnerProfile(player_id="test")
        return AdaptiveEngine(profile)

    def test_success_increases_interval(self, engine):
        """Successful attempt should increase review interval."""
        engine.observe_attempt("concept", success=True, time_seconds=30)
        interval_after_first = engine.profile.concept_interval["concept"]

        engine.observe_attempt("concept", success=True, time_seconds=30)
        interval_after_second = engine.profile.concept_interval["concept"]

        assert interval_after_second > interval_after_first

    def test_failure_decreases_interval(self, engine):
        """Failed attempt should decrease review interval."""
        # First, get some interval
        engine.observe_attempt("concept", success=True, time_seconds=30)
        interval_before = engine.profile.concept_interval["concept"]

        # Now fail
        engine.observe_attempt("concept", success=False, time_seconds=60)
        interval_after = engine.profile.concept_interval["concept"]

        assert interval_after < interval_before


# Self-teaching note:
#
# This test file demonstrates:
# - pytest fixtures for reusable setup
# - Testing behavior, not implementation
# - Isolation between tests
# - Edge case coverage
# - Descriptive test names that read like specifications
#
# Reading these tests tells you HOW the adaptive engine behaves
# without needing to read the implementation.
