"""
Tests for Weakness Detector

TDD: These tests define how weakness detection works BEFORE implementation.

The weakness detector:
1. Tracks struggle patterns across concepts
2. Identifies concepts that need more practice
3. Gently resurfaces weak concepts (not annoying drilling)
4. Considers prerequisite gaps as potential root causes
5. Integrates with spaced repetition for optimal timing
"""

import pytest
from datetime import datetime, timedelta
from lmsp.adaptive.weakness import (
    WeaknessProfile,
    WeaknessDetector,
    StrugglePattern,
    ResurfaceStrategy,
    WeaknessRecommendation,
)


class TestStrugglePattern:
    """Test the struggle pattern tracking."""

    def test_pattern_records_failure(self):
        """Struggle pattern should record failures."""
        pattern = StrugglePattern(concept_id="list_comprehensions")

        pattern.record_attempt(success=False, time_seconds=60, hints_used=2)

        assert pattern.failure_count == 1
        assert pattern.total_attempts == 1
        assert pattern.success_rate == 0.0

    def test_pattern_records_success(self):
        """Struggle pattern should record successes."""
        pattern = StrugglePattern(concept_id="list_comprehensions")

        pattern.record_attempt(success=True, time_seconds=30, hints_used=0)

        assert pattern.success_count == 1
        assert pattern.success_rate == 1.0

    def test_pattern_calculates_success_rate(self):
        """Success rate should be accurate."""
        pattern = StrugglePattern(concept_id="loops")

        # 3 successes, 2 failures = 60% success rate
        pattern.record_attempt(success=True, time_seconds=30, hints_used=0)
        pattern.record_attempt(success=False, time_seconds=60, hints_used=1)
        pattern.record_attempt(success=True, time_seconds=25, hints_used=0)
        pattern.record_attempt(success=True, time_seconds=35, hints_used=0)
        pattern.record_attempt(success=False, time_seconds=90, hints_used=3)

        assert pattern.success_rate == 0.6

    def test_pattern_tracks_time(self):
        """Pattern should track average time."""
        pattern = StrugglePattern(concept_id="loops")

        pattern.record_attempt(success=True, time_seconds=30, hints_used=0)
        pattern.record_attempt(success=True, time_seconds=50, hints_used=0)

        assert pattern.average_time == 40.0

    def test_pattern_tracks_hints(self):
        """Pattern should track hints used."""
        pattern = StrugglePattern(concept_id="loops")

        pattern.record_attempt(success=True, time_seconds=30, hints_used=1)
        pattern.record_attempt(success=True, time_seconds=40, hints_used=3)

        assert pattern.total_hints_used == 4
        assert pattern.average_hints == 2.0

    def test_pattern_serialization(self):
        """Pattern should serialize/deserialize."""
        pattern = StrugglePattern(concept_id="loops")
        pattern.record_attempt(success=True, time_seconds=30, hints_used=1)
        pattern.record_attempt(success=False, time_seconds=60, hints_used=2)

        data = pattern.to_dict()
        restored = StrugglePattern.from_dict(data)

        assert restored.concept_id == "loops"
        assert restored.success_count == 1
        assert restored.failure_count == 1


class TestWeaknessProfile:
    """Test the weakness profile data structure."""

    def test_new_profile_is_empty(self):
        """New profile should have no weaknesses."""
        profile = WeaknessProfile(player_id="test")

        assert len(profile.get_all_patterns()) == 0
        assert profile.get_weakness_count() == 0

    def test_profile_adds_pattern(self):
        """Profile should track struggle patterns."""
        profile = WeaknessProfile(player_id="test")

        profile.record_attempt("lists", success=False, time_seconds=60, hints_used=1)

        pattern = profile.get_pattern("lists")
        assert pattern is not None
        assert pattern.failure_count == 1

    def test_profile_identifies_weak_concepts(self):
        """Profile should identify concepts with low success rate."""
        profile = WeaknessProfile(player_id="test")

        # Lists: 2 failures, 0 success = weak
        profile.record_attempt("lists", success=False, time_seconds=60, hints_used=1)
        profile.record_attempt("lists", success=False, time_seconds=70, hints_used=2)

        # Loops: 3 success, 0 failure = strong
        profile.record_attempt("loops", success=True, time_seconds=30, hints_used=0)
        profile.record_attempt("loops", success=True, time_seconds=25, hints_used=0)
        profile.record_attempt("loops", success=True, time_seconds=35, hints_used=0)

        weak = profile.get_weak_concepts(threshold=0.5)

        assert "lists" in weak
        assert "loops" not in weak

    def test_profile_serialization(self):
        """Profile should serialize/deserialize."""
        profile = WeaknessProfile(player_id="test")
        profile.record_attempt("lists", success=False, time_seconds=60, hints_used=1)

        data = profile.to_dict()
        restored = WeaknessProfile.from_dict(data)

        assert restored.player_id == "test"
        assert restored.get_pattern("lists") is not None


class TestWeaknessDetector:
    """Test the weakness detection engine."""

    @pytest.fixture
    def detector(self):
        """Create a fresh detector for each test."""
        return WeaknessDetector()

    def test_detector_identifies_weakness(self, detector):
        """Detector should identify concepts needing practice."""
        profile = WeaknessProfile(player_id="test")

        # Create weakness: multiple failures
        for _ in range(3):
            profile.record_attempt("list_comprehensions", success=False,
                                 time_seconds=120, hints_used=3)

        weak_concepts = detector.identify_weaknesses(profile)

        assert "list_comprehensions" in weak_concepts

    def test_detector_ignores_new_concepts(self, detector):
        """Detector should not flag concepts with too few attempts."""
        profile = WeaknessProfile(player_id="test")

        # Just one failure shouldn't be flagged yet
        profile.record_attempt("new_concept", success=False,
                             time_seconds=60, hints_used=1)

        weak_concepts = detector.identify_weaknesses(profile, min_attempts=3)

        assert "new_concept" not in weak_concepts

    def test_detector_suggests_prerequisites(self, detector):
        """Detector should suggest checking prerequisites when stuck."""
        profile = WeaknessProfile(player_id="test")

        # Struggling with list comprehensions
        for _ in range(5):
            profile.record_attempt("list_comprehensions", success=False,
                                 time_seconds=120, hints_used=3)

        # Define prerequisites
        prerequisites = {"list_comprehensions": ["lists", "loops", "basics"]}

        suggestions = detector.suggest_prerequisite_review(
            profile,
            "list_comprehensions",
            prerequisites
        )

        # Should suggest reviewing prerequisites
        assert len(suggestions) > 0
        assert any(p in suggestions for p in ["lists", "loops", "basics"])

    def test_detector_calculates_weakness_severity(self, detector):
        """Detector should calculate how severe a weakness is."""
        profile = WeaknessProfile(player_id="test")

        # Mild weakness: 60% success rate
        profile.record_attempt("mild_weak", success=True, time_seconds=30, hints_used=0)
        profile.record_attempt("mild_weak", success=True, time_seconds=30, hints_used=0)
        profile.record_attempt("mild_weak", success=True, time_seconds=30, hints_used=0)
        profile.record_attempt("mild_weak", success=False, time_seconds=60, hints_used=1)
        profile.record_attempt("mild_weak", success=False, time_seconds=60, hints_used=1)

        # Severe weakness: 20% success rate
        profile.record_attempt("severe_weak", success=True, time_seconds=30, hints_used=0)
        profile.record_attempt("severe_weak", success=False, time_seconds=90, hints_used=3)
        profile.record_attempt("severe_weak", success=False, time_seconds=100, hints_used=3)
        profile.record_attempt("severe_weak", success=False, time_seconds=120, hints_used=3)
        profile.record_attempt("severe_weak", success=False, time_seconds=90, hints_used=2)

        mild_severity = detector.calculate_severity(profile, "mild_weak")
        severe_severity = detector.calculate_severity(profile, "severe_weak")

        assert severe_severity > mild_severity

    def test_detector_tracks_improvement(self, detector):
        """Detector should notice when a weakness is improving."""
        profile = WeaknessProfile(player_id="test")

        # Started weak, getting better
        profile.record_attempt("improving", success=False, time_seconds=120, hints_used=3)
        profile.record_attempt("improving", success=False, time_seconds=100, hints_used=2)
        profile.record_attempt("improving", success=True, time_seconds=60, hints_used=1)
        profile.record_attempt("improving", success=True, time_seconds=45, hints_used=0)
        profile.record_attempt("improving", success=True, time_seconds=30, hints_used=0)

        is_improving = detector.is_improving(profile, "improving", window=3)

        assert is_improving is True


class TestResurfaceStrategy:
    """Test the gentle resurfacing strategy."""

    @pytest.fixture
    def detector(self):
        return WeaknessDetector()

    def test_resurface_not_too_frequent(self, detector):
        """Resurfacing should not be annoying (too frequent)."""
        profile = WeaknessProfile(player_id="test")

        # Recent practice
        profile.record_attempt("weak_concept", success=False,
                             time_seconds=60, hints_used=1)
        pattern = profile.get_pattern("weak_concept")
        pattern.last_practiced = datetime.now()

        strategy = detector.get_resurface_strategy(profile, "weak_concept")

        # Should not resurface immediately
        assert strategy.should_resurface is False

    def test_resurface_after_cooldown(self, detector):
        """Resurfacing should happen after appropriate cooldown."""
        profile = WeaknessProfile(player_id="test")

        # Practiced long ago
        profile.record_attempt("weak_concept", success=False,
                             time_seconds=60, hints_used=1)
        pattern = profile.get_pattern("weak_concept")
        pattern.last_practiced = datetime.now() - timedelta(hours=6)

        strategy = detector.get_resurface_strategy(profile, "weak_concept")

        # Should resurface now
        assert strategy.should_resurface is True

    def test_resurface_gentle_approach(self, detector):
        """Resurfacing should use gentle approach types."""
        profile = WeaknessProfile(player_id="test")

        # Struggling concept
        for _ in range(3):
            profile.record_attempt("hard_concept", success=False,
                                 time_seconds=120, hints_used=3)

        pattern = profile.get_pattern("hard_concept")
        pattern.last_practiced = datetime.now() - timedelta(days=1)

        strategy = detector.get_resurface_strategy(profile, "hard_concept")

        # Should use gentle approach (not direct drilling)
        assert strategy.approach in ["disguised", "scaffolded", "fun_integration"]

    def test_resurface_with_easier_variant(self, detector):
        """For very hard concepts, resurface with easier variant."""
        profile = WeaknessProfile(player_id="test")

        # Very low success rate
        for _ in range(10):
            profile.record_attempt("very_hard", success=False,
                                 time_seconds=180, hints_used=5)

        pattern = profile.get_pattern("very_hard")
        pattern.last_practiced = datetime.now() - timedelta(days=1)

        strategy = detector.get_resurface_strategy(profile, "very_hard")

        # Should suggest easier difficulty
        assert strategy.difficulty_adjustment < 0  # Easier


class TestWeaknessRecommendation:
    """Test weakness-based recommendations."""

    @pytest.fixture
    def detector(self):
        return WeaknessDetector()

    def test_recommend_includes_reasoning(self, detector):
        """Recommendations should include reasoning."""
        profile = WeaknessProfile(player_id="test")

        for _ in range(3):
            profile.record_attempt("weak", success=False, time_seconds=60, hints_used=2)

        pattern = profile.get_pattern("weak")
        pattern.last_practiced = datetime.now() - timedelta(hours=12)

        rec = detector.recommend_weakness_practice(profile, max_count=3)

        assert len(rec) > 0
        assert rec[0].reason != ""

    def test_recommend_prioritizes_severe(self, detector):
        """Should prioritize more severe weaknesses."""
        profile = WeaknessProfile(player_id="test")

        # Mild weakness
        for _ in range(3):
            profile.record_attempt("mild", success=False, time_seconds=30, hints_used=1)
            profile.record_attempt("mild", success=True, time_seconds=30, hints_used=0)

        # Severe weakness
        for _ in range(5):
            profile.record_attempt("severe", success=False, time_seconds=90, hints_used=3)

        for concept in ["mild", "severe"]:
            pattern = profile.get_pattern(concept)
            pattern.last_practiced = datetime.now() - timedelta(hours=12)

        recs = detector.recommend_weakness_practice(profile, max_count=5)

        # Severe should come first
        assert recs[0].concept_id == "severe"

    def test_recommend_respects_cooldown(self, detector):
        """Should not recommend recently practiced concepts."""
        profile = WeaknessProfile(player_id="test")

        for _ in range(3):
            profile.record_attempt("weak", success=False, time_seconds=60, hints_used=2)

        # Just practiced
        pattern = profile.get_pattern("weak")
        pattern.last_practiced = datetime.now() - timedelta(minutes=30)

        recs = detector.recommend_weakness_practice(profile, min_cooldown_hours=1)

        # Should not recommend weak concept yet
        assert all(r.concept_id != "weak" for r in recs)


class TestLMSPIntegration:
    """Test integration with LMSP game concepts."""

    @pytest.fixture
    def detector(self):
        return WeaknessDetector()

    def test_integrate_with_challenge_completion(self, detector):
        """Weakness tracking should integrate with challenge completion."""
        profile = WeaknessProfile(player_id="test")

        # Player completes a challenge but struggles
        detector.record_challenge_result(
            profile=profile,
            concept_id="dictionaries",
            success=False,
            time_seconds=180,
            hints_used=4,
            attempts=3
        )

        # Should have recorded the struggle
        pattern = profile.get_pattern("dictionaries")
        assert pattern is not None
        assert pattern.failure_count >= 1

    def test_disguised_practice_recommendation(self, detector):
        """Should recommend disguised practice for sensitive concepts."""
        profile = WeaknessProfile(player_id="test")

        # Heavy failure, might be frustrating
        for _ in range(5):
            profile.record_attempt("frustrating_concept", success=False,
                                 time_seconds=120, hints_used=3)

        pattern = profile.get_pattern("frustrating_concept")
        pattern.last_practiced = datetime.now() - timedelta(days=1)

        rec = detector.recommend_weakness_practice(
            profile,
            max_count=1,
            prefer_disguised=True
        )

        # Should use disguised approach
        if rec:
            assert rec[0].approach == "disguised"


# Self-teaching note:
#
# This test file demonstrates:
# - Testing data structures (StrugglePattern, WeaknessProfile)
# - Testing algorithms (severity calculation, improvement detection)
# - Testing strategies (resurface timing, approach selection)
# - pytest fixtures for test isolation
# - Datetime manipulation for time-based tests
#
# The weakness detector uses several strategies for "gentle" resurfacing:
# - Disguised: embed weak concept in fun challenge about something else
# - Scaffolded: break down the concept into smaller pieces
# - Fun integration: mix with concepts the player enjoys
# - Cooldown: don't resurface too frequently
# - Easier variants: reduce difficulty for very hard concepts
#
# The goal: help players improve WITHOUT making them feel bad or annoyed.
