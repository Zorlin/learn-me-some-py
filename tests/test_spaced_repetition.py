"""
Tests for Anki-style SM-2 Spaced Repetition Scheduler

TDD: These tests define how spaced repetition works BEFORE implementation.

The SM-2 algorithm:
- Ease Factor (EF): How "easy" a card is for this learner (starts at 2.5)
- Interval: Days until next review
- Quality: 0-5 rating on each review
  - 0: Complete blackout
  - 1: Incorrect, correct answer obvious when shown
  - 2: Incorrect, remembered after review
  - 3: Correct with serious difficulty
  - 4: Correct with some hesitation
  - 5: Perfect response

When quality < 3: Reset to learning mode (interval = 1 day)
When quality >= 3: Extend interval using ease factor
"""

import pytest
from datetime import datetime, timedelta
from lmsp.adaptive.spaced_repetition import (
    SpacedRepetitionCard,
    SpacedRepetitionScheduler,
    ReviewQuality,
)


class TestReviewQuality:
    """Test the quality rating system."""

    def test_quality_values(self):
        """Quality ratings should match SM-2 scale (0-5)."""
        assert ReviewQuality.BLACKOUT == 0
        assert ReviewQuality.WRONG_BUT_OBVIOUS == 1
        assert ReviewQuality.WRONG_REMEMBERED_AFTER == 2
        assert ReviewQuality.CORRECT_HARD == 3
        assert ReviewQuality.CORRECT_HESITATION == 4
        assert ReviewQuality.PERFECT == 5

    def test_quality_is_passing(self):
        """Quality >= 3 means the card was recalled."""
        assert not ReviewQuality.BLACKOUT.is_passing()
        assert not ReviewQuality.WRONG_BUT_OBVIOUS.is_passing()
        assert not ReviewQuality.WRONG_REMEMBERED_AFTER.is_passing()
        assert ReviewQuality.CORRECT_HARD.is_passing()
        assert ReviewQuality.CORRECT_HESITATION.is_passing()
        assert ReviewQuality.PERFECT.is_passing()


class TestSpacedRepetitionCard:
    """Test individual card tracking."""

    def test_new_card_defaults(self):
        """New cards should have sensible defaults."""
        card = SpacedRepetitionCard(concept_id="lists_basics")

        assert card.concept_id == "lists_basics"
        assert card.ease_factor == 2.5  # SM-2 default
        assert card.interval_days == 0  # New card, not yet learned
        assert card.repetition_count == 0
        assert card.last_review is None
        assert card.next_review is None

    def test_card_due_when_next_review_passed(self):
        """Card should be due when next_review date has passed."""
        card = SpacedRepetitionCard(
            concept_id="lists_basics",
            next_review=datetime.now() - timedelta(hours=1)
        )
        assert card.is_due()

    def test_card_not_due_when_next_review_future(self):
        """Card should not be due when next_review is in future."""
        card = SpacedRepetitionCard(
            concept_id="lists_basics",
            next_review=datetime.now() + timedelta(days=1)
        )
        assert not card.is_due()

    def test_new_card_is_due(self):
        """New cards (never reviewed) should be due."""
        card = SpacedRepetitionCard(concept_id="lists_basics")
        assert card.is_due()

    def test_card_serialization(self):
        """Cards should serialize/deserialize for persistence."""
        card = SpacedRepetitionCard(
            concept_id="lists_basics",
            ease_factor=2.3,
            interval_days=7,
            repetition_count=5,
            last_review=datetime(2025, 1, 15, 10, 30),
            next_review=datetime(2025, 1, 22, 10, 30),
        )

        data = card.to_dict()
        restored = SpacedRepetitionCard.from_dict(data)

        assert restored.concept_id == "lists_basics"
        assert restored.ease_factor == 2.3
        assert restored.interval_days == 7
        assert restored.repetition_count == 5


class TestSM2Algorithm:
    """Test the SM-2 algorithm implementation."""

    @pytest.fixture
    def scheduler(self):
        """Create a fresh scheduler for testing."""
        return SpacedRepetitionScheduler()

    def test_first_review_perfect_sets_one_day(self, scheduler):
        """First perfect review should set interval to 1 day."""
        card = SpacedRepetitionCard(concept_id="test")

        updated = scheduler.review(card, ReviewQuality.PERFECT)

        assert updated.interval_days == 1
        assert updated.repetition_count == 1

    def test_second_review_perfect_sets_six_days(self, scheduler):
        """Second perfect review should set interval to 6 days."""
        card = SpacedRepetitionCard(
            concept_id="test",
            interval_days=1,
            repetition_count=1,
        )

        updated = scheduler.review(card, ReviewQuality.PERFECT)

        assert updated.interval_days == 6
        assert updated.repetition_count == 2

    def test_third_review_uses_ease_factor(self, scheduler):
        """Third+ review uses: interval * ease_factor."""
        card = SpacedRepetitionCard(
            concept_id="test",
            interval_days=6,
            repetition_count=2,
            ease_factor=2.5,
        )

        updated = scheduler.review(card, ReviewQuality.PERFECT)

        # 6 * 2.5 = 15
        assert updated.interval_days == 15
        assert updated.repetition_count == 3

    def test_perfect_review_increases_ease_factor(self, scheduler):
        """Perfect reviews should increase ease factor."""
        card = SpacedRepetitionCard(
            concept_id="test",
            ease_factor=2.5,
            interval_days=1,
            repetition_count=1,
        )

        updated = scheduler.review(card, ReviewQuality.PERFECT)

        # SM-2: EF = EF + (0.1 - (5-q)*(0.08 + (5-q)*0.02))
        # For q=5: EF = 2.5 + (0.1 - 0*anything) = 2.6
        assert updated.ease_factor > 2.5

    def test_hard_review_decreases_ease_factor(self, scheduler):
        """Difficult but correct reviews should decrease ease factor."""
        card = SpacedRepetitionCard(
            concept_id="test",
            ease_factor=2.5,
            interval_days=1,
            repetition_count=1,
        )

        updated = scheduler.review(card, ReviewQuality.CORRECT_HARD)

        # q=3 means harder, ease should decrease
        assert updated.ease_factor < 2.5

    def test_ease_factor_minimum(self, scheduler):
        """Ease factor should never go below 1.3."""
        card = SpacedRepetitionCard(
            concept_id="test",
            ease_factor=1.4,  # Already low
            interval_days=1,
            repetition_count=1,
        )

        # Multiple hard reviews
        for _ in range(5):
            card = scheduler.review(card, ReviewQuality.CORRECT_HARD)

        assert card.ease_factor >= 1.3

    def test_failed_review_resets_interval(self, scheduler):
        """Failed review (quality < 3) should reset interval to 1."""
        card = SpacedRepetitionCard(
            concept_id="test",
            interval_days=30,  # Was doing well
            repetition_count=5,
            ease_factor=2.5,
        )

        updated = scheduler.review(card, ReviewQuality.BLACKOUT)

        assert updated.interval_days == 1  # Reset!
        assert updated.repetition_count == 0  # Reset!

    def test_failed_review_preserves_ease_factor(self, scheduler):
        """Failed review should decrease but preserve ease factor."""
        card = SpacedRepetitionCard(
            concept_id="test",
            interval_days=30,
            repetition_count=5,
            ease_factor=2.5,
        )

        updated = scheduler.review(card, ReviewQuality.WRONG_BUT_OBVIOUS)

        # Ease factor decreases but doesn't reset
        assert updated.ease_factor < 2.5
        assert updated.ease_factor >= 1.3

    def test_next_review_calculated(self, scheduler):
        """Next review date should be calculated from interval."""
        card = SpacedRepetitionCard(concept_id="test")

        before = datetime.now()
        updated = scheduler.review(card, ReviewQuality.PERFECT)
        after = datetime.now()

        # Next review should be approximately 1 day from now
        assert updated.next_review is not None
        expected_min = before + timedelta(days=1)
        expected_max = after + timedelta(days=1) + timedelta(seconds=1)

        assert expected_min <= updated.next_review <= expected_max


class TestSchedulerManagement:
    """Test scheduler card management."""

    @pytest.fixture
    def scheduler(self):
        return SpacedRepetitionScheduler()

    def test_add_new_concept(self, scheduler):
        """Should track new concepts."""
        scheduler.add_concept("lists_basics")

        assert "lists_basics" in scheduler.get_all_concepts()

    def test_add_duplicate_concept_no_effect(self, scheduler):
        """Adding same concept twice should be idempotent."""
        scheduler.add_concept("lists_basics")
        scheduler.add_concept("lists_basics")

        concepts = scheduler.get_all_concepts()
        assert concepts.count("lists_basics") == 1

    def test_get_due_concepts(self, scheduler):
        """Should return only due concepts."""
        scheduler.add_concept("new_concept")  # New = due
        scheduler.add_concept("learned_concept")

        # Mark one as learned and scheduled for future
        card = scheduler.get_card("learned_concept")
        card.next_review = datetime.now() + timedelta(days=30)

        due = scheduler.get_due_concepts()

        assert "new_concept" in due
        assert "learned_concept" not in due

    def test_record_review_updates_card(self, scheduler):
        """Recording a review should update the card state."""
        scheduler.add_concept("test")

        scheduler.record_review("test", ReviewQuality.PERFECT)

        card = scheduler.get_card("test")
        assert card.repetition_count == 1
        assert card.interval_days == 1

    def test_scheduler_persistence(self, scheduler, tmp_path):
        """Scheduler should save/load state."""
        scheduler.add_concept("test")
        scheduler.record_review("test", ReviewQuality.PERFECT)

        save_path = tmp_path / "scheduler.json"
        scheduler.save(save_path)

        loaded = SpacedRepetitionScheduler.load(save_path)

        card = loaded.get_card("test")
        assert card.repetition_count == 1


class TestLMSPIntegration:
    """Test integration with LMSP concepts."""

    @pytest.fixture
    def scheduler(self):
        return SpacedRepetitionScheduler()

    def test_review_from_game_success(self, scheduler):
        """Successful game challenge should update spaced repetition."""
        scheduler.add_concept("list_comprehensions")

        # Perfect solve = quality 5
        scheduler.record_review_from_game(
            concept_id="list_comprehensions",
            success=True,
            time_seconds=30,
            hints_used=0
        )

        card = scheduler.get_card("list_comprehensions")
        assert card.repetition_count == 1

    def test_fast_perfect_solve_is_quality_5(self, scheduler):
        """Fast solve with no hints should be quality 5."""
        scheduler.add_concept("test")

        scheduler.record_review_from_game(
            concept_id="test",
            success=True,
            time_seconds=20,  # Very fast
            hints_used=0
        )

        card = scheduler.get_card("test")
        # Quality 5 increases ease factor
        assert card.ease_factor > 2.5

    def test_slow_solve_with_hints_is_quality_3(self, scheduler):
        """Slow solve with hints should be quality 3."""
        scheduler.add_concept("test")

        scheduler.record_review_from_game(
            concept_id="test",
            success=True,
            time_seconds=300,  # Slow
            hints_used=3
        )

        card = scheduler.get_card("test")
        # Quality 3 decreases ease factor
        assert card.ease_factor < 2.5

    def test_failed_attempt_is_quality_1(self, scheduler):
        """Failed attempt should be quality 1 or 2."""
        scheduler.add_concept("test")

        scheduler.record_review_from_game(
            concept_id="test",
            success=False,
            time_seconds=60,
            hints_used=2
        )

        card = scheduler.get_card("test")
        assert card.interval_days == 1  # Reset
        assert card.repetition_count == 0  # Reset

    def test_get_concepts_for_review_session(self, scheduler):
        """Should return optimal set for a study session."""
        # Add various concepts
        for i in range(10):
            scheduler.add_concept(f"concept_{i}")

        # Some due, some not
        for i in range(5):
            scheduler.record_review(f"concept_{i}", ReviewQuality.PERFECT)
            card = scheduler.get_card(f"concept_{i}")
            card.next_review = datetime.now() + timedelta(days=30)

        # Get session (should return due ones)
        session = scheduler.get_session_concepts(max_count=5)

        assert len(session) <= 5
        # Should prioritize new/due concepts
        for concept_id in session:
            card = scheduler.get_card(concept_id)
            assert card.is_due()


# Self-teaching note:
#
# This test file demonstrates:
# - The SM-2 spaced repetition algorithm (Level 6+: algorithms)
# - pytest fixtures for test isolation
# - Testing edge cases and boundaries
# - Integration testing patterns
#
# The SM-2 algorithm is real science from cognitive psychology.
# It was developed by Piotr Wozniak in 1987 and powers Anki.
