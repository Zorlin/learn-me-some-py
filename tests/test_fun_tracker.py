"""
Tests for Fun Pattern Tracker

TDD: These tests define how fun tracking works BEFORE implementation.

The 6 Fun Types (from game design research):
1. Puzzle - Problem solving, logic, pattern matching
2. Speedrun - Time pressure, fast execution, efficiency
3. Collection - Completing sets, achievements, unlocking
4. Creation - Building things, projects, making something new
5. Competition - Racing others, leaderboards, comparison
6. Mastery - Getting very good, flow state, deep understanding

Each player has a unique "fun profile" - their relative enjoyment of each type.
We detect this through:
- Emotional input (RT positive, LT negative)
- Time spent on different challenge types
- Replay patterns (what do they voluntarily revisit?)
- Performance patterns (what brings them into flow?)
"""

import pytest
from datetime import datetime, timedelta
from lmsp.adaptive.fun_tracker import (
    FunType,
    FunProfile,
    FunObservation,
    FunTracker,
)


class TestFunType:
    """Test the fun type enumeration."""

    def test_all_six_fun_types_exist(self):
        """All six fun types should be defined."""
        assert FunType.PUZZLE is not None
        assert FunType.SPEEDRUN is not None
        assert FunType.COLLECTION is not None
        assert FunType.CREATION is not None
        assert FunType.COMPETITION is not None
        assert FunType.MASTERY is not None

    def test_fun_types_have_descriptions(self):
        """Each fun type should have a human-readable description."""
        assert FunType.PUZZLE.description
        assert FunType.SPEEDRUN.description
        assert FunType.CREATION.description


class TestFunProfile:
    """Test the fun profile data structure."""

    def test_new_profile_has_neutral_weights(self):
        """New profile should start with equal weights."""
        profile = FunProfile()

        # All fun types should have equal starting weight
        weights = profile.get_weights()
        assert len(weights) == 6  # All fun types

        # Weights should sum to 1.0 (normalized)
        assert abs(sum(weights.values()) - 1.0) < 0.01

    def test_profile_tracks_dominant_fun_type(self):
        """Profile should identify dominant fun type."""
        profile = FunProfile()

        # Manually set weights (as if observed)
        profile.set_weight(FunType.SPEEDRUN, 0.4)
        profile.set_weight(FunType.PUZZLE, 0.2)
        profile.set_weight(FunType.COLLECTION, 0.15)
        profile.set_weight(FunType.CREATION, 0.1)
        profile.set_weight(FunType.COMPETITION, 0.1)
        profile.set_weight(FunType.MASTERY, 0.05)

        assert profile.dominant_type == FunType.SPEEDRUN

    def test_profile_top_n_fun_types(self):
        """Should return top N fun types in order."""
        profile = FunProfile()

        profile.set_weight(FunType.SPEEDRUN, 0.35)
        profile.set_weight(FunType.PUZZLE, 0.30)
        profile.set_weight(FunType.MASTERY, 0.15)
        profile.set_weight(FunType.COLLECTION, 0.10)
        profile.set_weight(FunType.CREATION, 0.05)
        profile.set_weight(FunType.COMPETITION, 0.05)

        top_3 = profile.get_top_types(3)
        assert top_3[0] == FunType.SPEEDRUN
        assert top_3[1] == FunType.PUZZLE
        assert top_3[2] == FunType.MASTERY

    def test_profile_serialization(self):
        """Profile should serialize/deserialize for persistence."""
        profile = FunProfile()
        profile.set_weight(FunType.PUZZLE, 0.5)
        profile.set_weight(FunType.SPEEDRUN, 0.3)

        data = profile.to_dict()
        restored = FunProfile.from_dict(data)

        assert restored.get_weight(FunType.PUZZLE) == profile.get_weight(FunType.PUZZLE)
        assert restored.get_weight(FunType.SPEEDRUN) == profile.get_weight(FunType.SPEEDRUN)


class TestFunObservation:
    """Test individual fun observations."""

    def test_observation_captures_moment(self):
        """Observation should capture a moment of fun/not-fun."""
        obs = FunObservation(
            fun_type=FunType.PUZZLE,
            enjoyment=0.8,  # High enjoyment
            context="list_comprehensions",
            timestamp=datetime.now()
        )

        assert obs.fun_type == FunType.PUZZLE
        assert obs.enjoyment == 0.8
        assert obs.context == "list_comprehensions"

    def test_observation_from_emotional_input(self):
        """Observation should convert emotional trigger values."""
        # RT = positive emotion, high value = enjoying
        obs = FunObservation.from_emotional_input(
            fun_type=FunType.SPEEDRUN,
            positive_trigger=0.9,  # RT pulled hard
            negative_trigger=0.1,  # LT barely touched
            context="timed_challenge"
        )

        # Net enjoyment should be positive
        assert obs.enjoyment > 0.5

    def test_observation_negative_net_enjoyment(self):
        """High negative trigger should result in low enjoyment."""
        obs = FunObservation.from_emotional_input(
            fun_type=FunType.PUZZLE,
            positive_trigger=0.2,  # RT barely touched
            negative_trigger=0.9,  # LT pulled hard
            context="hard_puzzle"
        )

        # Net enjoyment should be negative
        assert obs.enjoyment < 0.5


class TestFunTracker:
    """Test the fun tracking engine."""

    @pytest.fixture
    def tracker(self):
        """Create fresh tracker for each test."""
        return FunTracker()

    def test_observe_updates_profile(self, tracker):
        """Observations should update the fun profile."""
        # Multiple positive puzzle experiences
        for _ in range(5):
            tracker.observe(FunType.PUZZLE, enjoyment=0.9, context="puzzle_challenge")

        profile = tracker.get_profile()
        puzzle_weight = profile.get_weight(FunType.PUZZLE)

        # Puzzle should be weighted higher than default
        default_weight = 1.0 / 6  # Equal distribution
        assert puzzle_weight > default_weight

    def test_observe_from_challenge_type(self, tracker):
        """Should map challenge types to fun types."""
        # Different challenge types map to different fun types
        tracker.observe_challenge(
            challenge_type="speedrun",
            success=True,
            time_seconds=15,  # Very fast
            enjoyment=0.85
        )

        profile = tracker.get_profile()
        assert profile.get_weight(FunType.SPEEDRUN) > 1.0 / 6

    def test_multiple_fun_types_accumulate(self, tracker):
        """Multiple fun types can coexist in profile."""
        # Player enjoys both puzzle and creation
        for _ in range(3):
            tracker.observe(FunType.PUZZLE, enjoyment=0.8, context="puzzle_1")
            tracker.observe(FunType.CREATION, enjoyment=0.85, context="project_1")

        profile = tracker.get_profile()

        # Both should be above default
        default_weight = 1.0 / 6
        assert profile.get_weight(FunType.PUZZLE) > default_weight
        assert profile.get_weight(FunType.CREATION) > default_weight

    def test_negative_experience_decreases_weight(self, tracker):
        """Negative experiences should decrease fun type weight."""
        # First, build up some puzzle preference
        for _ in range(5):
            tracker.observe(FunType.PUZZLE, enjoyment=0.8, context="puzzle_1")

        puzzle_weight_before = tracker.get_profile().get_weight(FunType.PUZZLE)

        # Now have negative puzzle experiences
        for _ in range(5):
            tracker.observe(FunType.PUZZLE, enjoyment=0.2, context="puzzle_2")

        puzzle_weight_after = tracker.get_profile().get_weight(FunType.PUZZLE)

        # Weight should decrease
        assert puzzle_weight_after < puzzle_weight_before

    def test_recommend_challenge_type(self, tracker):
        """Should recommend challenge types based on fun profile."""
        # Build up speedrun preference
        for _ in range(10):
            tracker.observe(FunType.SPEEDRUN, enjoyment=0.9, context="speed_challenge")

        recommendation = tracker.recommend_fun_type()

        # Should recommend speedrun
        assert recommendation == FunType.SPEEDRUN

    def test_recommend_varied_for_diversity(self, tracker):
        """Recommendations should sometimes vary for exploration."""
        # Build up strong puzzle preference
        for _ in range(20):
            tracker.observe(FunType.PUZZLE, enjoyment=0.95, context="puzzle")

        # Get many recommendations
        recommendations = [tracker.recommend_fun_type(exploration_rate=0.3) for _ in range(100)]

        # Most should be puzzle, but some variety
        puzzle_count = sum(1 for r in recommendations if r == FunType.PUZZLE)
        assert puzzle_count > 50  # Majority are puzzle
        assert puzzle_count < 100  # But some exploration

    def test_flow_detection_triggers_mastery(self, tracker):
        """Flow state indicators should boost mastery weight."""
        # Flow indicators: optimal challenge, high enjoyment, sustained engagement
        tracker.observe_flow_indicators(
            time_in_challenge=300,  # 5 minutes sustained
            enjoyment_stability=0.9,  # Consistently high
            challenge_skill_balance=0.8,  # Well matched
            context="deep_learning"
        )

        profile = tracker.get_profile()
        assert profile.get_weight(FunType.MASTERY) > 1.0 / 6

    def test_collection_triggered_by_completionist_behavior(self, tracker):
        """Completing optional content should boost collection weight."""
        # Player voluntarily completes optional challenges
        for _ in range(5):
            tracker.observe_completion(
                was_optional=True,
                sought_out=True,  # Player found it themselves
                enjoyment=0.85
            )

        profile = tracker.get_profile()
        assert profile.get_weight(FunType.COLLECTION) > 1.0 / 6

    def test_tracker_persistence(self, tracker, tmp_path):
        """Tracker should save and load state."""
        # Build up some preferences
        for _ in range(5):
            tracker.observe(FunType.PUZZLE, enjoyment=0.8, context="puzzle")
            tracker.observe(FunType.SPEEDRUN, enjoyment=0.7, context="speed")

        save_path = tmp_path / "fun_tracker.json"
        tracker.save(save_path)

        loaded = FunTracker.load(save_path)
        loaded_profile = loaded.get_profile()
        original_profile = tracker.get_profile()

        assert loaded_profile.get_weight(FunType.PUZZLE) == pytest.approx(
            original_profile.get_weight(FunType.PUZZLE), rel=0.01
        )

    def test_get_fun_statistics(self, tracker):
        """Should provide fun tracking statistics."""
        for _ in range(10):
            tracker.observe(FunType.PUZZLE, enjoyment=0.8, context="puzzle")

        stats = tracker.get_statistics()

        assert stats["total_observations"] == 10
        assert stats["dominant_type"] == FunType.PUZZLE
        assert "average_enjoyment" in stats


class TestFunTypeMapping:
    """Test mapping challenge characteristics to fun types."""

    @pytest.fixture
    def tracker(self):
        return FunTracker()

    def test_timed_challenges_map_to_speedrun(self, tracker):
        """Challenges with time pressure map to speedrun."""
        fun_type = tracker.classify_challenge(
            has_time_limit=True,
            is_competitive=False,
            is_creative=False,
            is_collectible=False,
            requires_deep_thinking=False
        )
        assert fun_type == FunType.SPEEDRUN

    def test_logic_puzzles_map_to_puzzle(self, tracker):
        """Logic-heavy challenges map to puzzle."""
        fun_type = tracker.classify_challenge(
            has_time_limit=False,
            is_competitive=False,
            is_creative=False,
            is_collectible=False,
            requires_deep_thinking=True
        )
        assert fun_type == FunType.PUZZLE

    def test_project_challenges_map_to_creation(self, tracker):
        """Open-ended creative challenges map to creation."""
        fun_type = tracker.classify_challenge(
            has_time_limit=False,
            is_competitive=False,
            is_creative=True,
            is_collectible=False,
            requires_deep_thinking=False
        )
        assert fun_type == FunType.CREATION

    def test_achievement_unlocks_map_to_collection(self, tracker):
        """Achievement/unlock content maps to collection."""
        fun_type = tracker.classify_challenge(
            has_time_limit=False,
            is_competitive=False,
            is_creative=False,
            is_collectible=True,
            requires_deep_thinking=False
        )
        assert fun_type == FunType.COLLECTION

    def test_leaderboard_challenges_map_to_competition(self, tracker):
        """Competitive challenges map to competition."""
        fun_type = tracker.classify_challenge(
            has_time_limit=False,
            is_competitive=True,
            is_creative=False,
            is_collectible=False,
            requires_deep_thinking=False
        )
        assert fun_type == FunType.COMPETITION


class TestLMSPIntegration:
    """Test integration with LMSP game concepts."""

    @pytest.fixture
    def tracker(self):
        return FunTracker()

    def test_concept_challenge_updates_fun_profile(self, tracker):
        """Completing a concept challenge should update fun profile."""
        # Complete a timed list comprehension challenge
        tracker.observe_concept_challenge(
            concept_id="list_comprehensions",
            challenge_type="speedrun",
            success=True,
            time_seconds=25,
            hints_used=0,
            positive_emotion=0.8,
            negative_emotion=0.1
        )

        profile = tracker.get_profile()
        # Should have increased speedrun weight
        assert profile.get_weight(FunType.SPEEDRUN) > 1.0 / 6

    def test_recommend_challenge_type_for_concept(self, tracker):
        """Should recommend appropriate challenge type for a concept."""
        # Build up creation preference
        for _ in range(10):
            tracker.observe(FunType.CREATION, enjoyment=0.9, context="project")

        # Recommend challenge type for teaching a concept
        challenge_type = tracker.recommend_challenge_type_for_concept(
            concept_id="dictionaries",
            available_types=["puzzle", "speedrun", "creation", "collection"]
        )

        # Should recommend creation since that's their preference
        assert challenge_type == "creation"

    def test_fun_profile_affects_curriculum_suggestions(self, tracker):
        """Fun profile should influence which challenges to show."""
        # Build up puzzle preference
        for _ in range(10):
            tracker.observe(FunType.PUZZLE, enjoyment=0.9, context="puzzle")

        # When multiple challenges are available for a concept,
        # prefer ones matching the fun profile
        suggestions = tracker.filter_challenges_by_fun(
            available_challenges=[
                {"id": "c1", "type": "speedrun", "concept": "loops"},
                {"id": "c2", "type": "puzzle", "concept": "loops"},
                {"id": "c3", "type": "collection", "concept": "loops"},
            ],
            max_count=2
        )

        # Puzzle should be ranked first
        assert suggestions[0]["type"] == "puzzle"


# Self-teaching note:
#
# This test file demonstrates:
# - Enum testing patterns
# - Dataclass with methods testing
# - Statistical/probabilistic testing (exploration rate)
# - pytest.approx for floating point comparison
# - Behavioral testing (what the system DOES, not HOW)
#
# The 6 fun types come from game design research:
# - MDA framework (Mechanics, Dynamics, Aesthetics)
# - Bartle's Player Types (adapted for single-player)
# - Flow theory (Csikszentmihalyi)
#
# Understanding YOUR fun profile makes learning more enjoyable!
