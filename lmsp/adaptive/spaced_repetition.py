"""
Anki-style SM-2 Spaced Repetition Scheduler

This module implements the SuperMemo 2 (SM-2) algorithm for optimal
learning through spaced repetition. Developed by Piotr Wozniak in 1987,
this algorithm is the foundation of Anki and other spaced repetition systems.

Key concepts:
- Ease Factor (EF): How easy a card is for the learner (starts at 2.5)
- Interval: Days until the next review
- Quality (0-5): How well the learner recalled the answer

The algorithm adjusts intervals based on recall quality:
- Perfect recall → longer intervals (memory is strong)
- Difficult recall → shorter intervals (needs more practice)
- Failed recall → reset to beginning (memory not formed)

Self-teaching note:
This file demonstrates:
- Dataclasses with validation (Level 5+)
- Enum with methods (Level 4)
- Algorithm implementation (Level 6: mathematical reasoning)
- datetime arithmetic (Standard library)
- JSON serialization patterns (Level 4)
- Type hints throughout (Professional Python)

The SM-2 algorithm is real cognitive science - the same math that
powers Anki, which has helped millions learn languages, medicine,
law, and programming concepts.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import IntEnum
from typing import Optional
from pathlib import Path
import json
import math


class ReviewQuality(IntEnum):
    """
    How well the learner recalled the concept.

    This follows the SM-2 scale (0-5):
    - 0-2: Failed recall (resets progress)
    - 3-5: Successful recall (extends interval)

    The quality affects both the ease factor adjustment
    and whether the card stays in the review queue.
    """
    BLACKOUT = 0           # Complete failure - no memory at all
    WRONG_BUT_OBVIOUS = 1  # Wrong, but recognized answer when shown
    WRONG_REMEMBERED_AFTER = 2  # Wrong, but remembered after review
    CORRECT_HARD = 3       # Correct but with serious difficulty
    CORRECT_HESITATION = 4  # Correct after some hesitation
    PERFECT = 5            # Perfect instant recall

    def is_passing(self) -> bool:
        """Quality >= 3 means the card was successfully recalled."""
        return self.value >= 3

    @classmethod
    def from_game_performance(
        cls,
        success: bool,
        time_seconds: float,
        hints_used: int,
        expected_time: float = 60.0
    ) -> "ReviewQuality":
        """
        Convert game performance metrics to SM-2 quality score.

        This maps LMSP challenge performance to the SM-2 scale:
        - Fast, no hints, success → Perfect (5)
        - Some hesitation/time → Correct with hesitation (4)
        - Struggled but succeeded → Correct but hard (3)
        - Failed but tried → Wrong (2)
        - Failed quickly (gave up) → Blackout (0-1)

        Args:
            success: Did the player solve the challenge?
            time_seconds: How long did they take?
            hints_used: How many hints were used?
            expected_time: Expected time for average solve

        Returns:
            Appropriate ReviewQuality rating
        """
        if not success:
            # Failed - determine how badly
            if hints_used >= 3 or time_seconds > expected_time * 3:
                return cls.WRONG_REMEMBERED_AFTER
            elif time_seconds < expected_time / 2:
                return cls.BLACKOUT  # Gave up quickly
            else:
                return cls.WRONG_BUT_OBVIOUS

        # Succeeded - determine how well
        time_ratio = time_seconds / expected_time

        if hints_used == 0 and time_ratio < 0.5:
            return cls.PERFECT
        elif hints_used <= 1 and time_ratio < 1.0:
            return cls.CORRECT_HESITATION
        else:
            return cls.CORRECT_HARD


@dataclass
class SpacedRepetitionCard:
    """
    Tracks spaced repetition data for a single concept.

    Each concept the player learns gets a card that tracks:
    - How easy it is for them (ease_factor)
    - When they last saw it (last_review)
    - When they should see it next (next_review)
    - How many successful reviews in a row (repetition_count)

    The SM-2 algorithm uses this data to calculate optimal
    review intervals for long-term memory formation.
    """
    concept_id: str
    ease_factor: float = 2.5  # SM-2 default EF
    interval_days: float = 0  # Current interval in days
    repetition_count: int = 0  # Number of successful reviews
    last_review: Optional[datetime] = None
    next_review: Optional[datetime] = None

    # Tracking for analytics
    total_reviews: int = 0
    total_correct: int = 0
    total_incorrect: int = 0
    streak: int = 0

    def is_due(self, now: Optional[datetime] = None) -> bool:
        """
        Check if this card is due for review.

        A card is due if:
        - It has never been reviewed (new card)
        - The next_review date has passed

        Args:
            now: Current time (defaults to datetime.now())

        Returns:
            True if the card should be reviewed
        """
        now = now or datetime.now()

        # New cards are always due
        if self.next_review is None:
            return True

        return now >= self.next_review

    def days_until_due(self, now: Optional[datetime] = None) -> float:
        """
        Days until this card is due.

        Returns:
            Positive = days until due
            Negative = days overdue
            0 = due now
            -infinity = new card (never reviewed)
        """
        now = now or datetime.now()

        if self.next_review is None:
            return float('-inf')

        delta = self.next_review - now
        return delta.total_seconds() / (24 * 3600)

    def to_dict(self) -> dict:
        """Serialize to dictionary for JSON storage."""
        return {
            "concept_id": self.concept_id,
            "ease_factor": self.ease_factor,
            "interval_days": self.interval_days,
            "repetition_count": self.repetition_count,
            "last_review": self.last_review.isoformat() if self.last_review else None,
            "next_review": self.next_review.isoformat() if self.next_review else None,
            "total_reviews": self.total_reviews,
            "total_correct": self.total_correct,
            "total_incorrect": self.total_incorrect,
            "streak": self.streak,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SpacedRepetitionCard":
        """Deserialize from dictionary."""
        return cls(
            concept_id=data["concept_id"],
            ease_factor=data.get("ease_factor", 2.5),
            interval_days=data.get("interval_days", 0),
            repetition_count=data.get("repetition_count", 0),
            last_review=(
                datetime.fromisoformat(data["last_review"])
                if data.get("last_review") else None
            ),
            next_review=(
                datetime.fromisoformat(data["next_review"])
                if data.get("next_review") else None
            ),
            total_reviews=data.get("total_reviews", 0),
            total_correct=data.get("total_correct", 0),
            total_incorrect=data.get("total_incorrect", 0),
            streak=data.get("streak", 0),
        )


class SpacedRepetitionScheduler:
    """
    SM-2 spaced repetition scheduler.

    Implements the SuperMemo 2 algorithm:

    For quality >= 3 (successful recall):
        if repetition_count == 0:
            interval = 1 day
        elif repetition_count == 1:
            interval = 6 days
        else:
            interval = interval * ease_factor

        repetition_count += 1

    For quality < 3 (failed recall):
        repetition_count = 0
        interval = 1 day

    Ease factor adjustment:
        EF' = EF + (0.1 - (5-q) * (0.08 + (5-q) * 0.02))
        EF = max(1.3, EF')

    Where q = quality (0-5)

    Usage:
        scheduler = SpacedRepetitionScheduler()
        scheduler.add_concept("list_comprehensions")

        # After player attempts a challenge
        scheduler.record_review("list_comprehensions", ReviewQuality.CORRECT_HESITATION)

        # Get what's due for review
        due = scheduler.get_due_concepts()

        # Get session for study
        session = scheduler.get_session_concepts(max_count=10)
    """

    # SM-2 constants
    MIN_EASE_FACTOR = 1.3
    DEFAULT_EASE_FACTOR = 2.5
    FIRST_INTERVAL = 1    # First successful review: 1 day
    SECOND_INTERVAL = 6   # Second successful review: 6 days

    def __init__(self):
        self._cards: dict[str, SpacedRepetitionCard] = {}

    def add_concept(self, concept_id: str) -> SpacedRepetitionCard:
        """
        Add a new concept to track.

        If the concept already exists, returns the existing card.

        Args:
            concept_id: Unique identifier for the concept

        Returns:
            The SpacedRepetitionCard for this concept
        """
        if concept_id not in self._cards:
            self._cards[concept_id] = SpacedRepetitionCard(concept_id=concept_id)
        return self._cards[concept_id]

    def get_card(self, concept_id: str) -> Optional[SpacedRepetitionCard]:
        """Get the card for a concept, or None if not tracked."""
        return self._cards.get(concept_id)

    def get_all_concepts(self) -> list[str]:
        """Get all tracked concept IDs."""
        return list(self._cards.keys())

    def review(
        self,
        card: SpacedRepetitionCard,
        quality: ReviewQuality,
        now: Optional[datetime] = None
    ) -> SpacedRepetitionCard:
        """
        Process a review and update the card.

        Implements the SM-2 algorithm to calculate:
        - New ease factor
        - New interval
        - Next review date

        Args:
            card: The card being reviewed
            quality: How well the learner recalled (0-5)
            now: Current time (for testing)

        Returns:
            Updated card (same object, modified in place)
        """
        now = now or datetime.now()

        # Update statistics
        card.total_reviews += 1
        card.last_review = now

        if quality.is_passing():
            # Successful recall
            card.total_correct += 1
            card.streak += 1

            # Calculate new interval
            if card.repetition_count == 0:
                card.interval_days = self.FIRST_INTERVAL
            elif card.repetition_count == 1:
                card.interval_days = self.SECOND_INTERVAL
            else:
                card.interval_days = card.interval_days * card.ease_factor

            card.repetition_count += 1

        else:
            # Failed recall - reset
            card.total_incorrect += 1
            card.streak = 0
            card.repetition_count = 0
            card.interval_days = self.FIRST_INTERVAL

        # Adjust ease factor using SM-2 formula
        # EF' = EF + (0.1 - (5-q) * (0.08 + (5-q) * 0.02))
        q = quality.value
        ef_adjustment = 0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)
        card.ease_factor = max(
            self.MIN_EASE_FACTOR,
            card.ease_factor + ef_adjustment
        )

        # Calculate next review date
        card.next_review = now + timedelta(days=card.interval_days)

        return card

    def record_review(
        self,
        concept_id: str,
        quality: ReviewQuality,
        now: Optional[datetime] = None
    ) -> SpacedRepetitionCard:
        """
        Record a review for a concept by ID.

        Convenience method that looks up the card and calls review().
        Creates the card if it doesn't exist.

        Args:
            concept_id: ID of the concept reviewed
            quality: How well the learner recalled (0-5)
            now: Current time (for testing)

        Returns:
            Updated card
        """
        card = self.add_concept(concept_id)
        return self.review(card, quality, now)

    def record_review_from_game(
        self,
        concept_id: str,
        success: bool,
        time_seconds: float,
        hints_used: int,
        expected_time: float = 60.0,
        now: Optional[datetime] = None
    ) -> SpacedRepetitionCard:
        """
        Record a review from game performance metrics.

        Converts LMSP game performance into SM-2 quality and records it.

        Args:
            concept_id: ID of the concept in the challenge
            success: Did the player solve the challenge?
            time_seconds: How long did they take?
            hints_used: How many hints were used?
            expected_time: Expected time for average solve
            now: Current time (for testing)

        Returns:
            Updated card
        """
        quality = ReviewQuality.from_game_performance(
            success=success,
            time_seconds=time_seconds,
            hints_used=hints_used,
            expected_time=expected_time
        )
        return self.record_review(concept_id, quality, now)

    def get_due_concepts(self, now: Optional[datetime] = None) -> list[str]:
        """
        Get all concepts that are due for review.

        Returns concept IDs sorted by how overdue they are
        (most overdue first).

        Args:
            now: Current time (for testing)

        Returns:
            List of concept IDs due for review
        """
        now = now or datetime.now()

        due = [
            (card.concept_id, card.days_until_due(now))
            for card in self._cards.values()
            if card.is_due(now)
        ]

        # Sort by how overdue (most negative first)
        due.sort(key=lambda x: x[1])

        return [concept_id for concept_id, _ in due]

    def get_session_concepts(
        self,
        max_count: int = 10,
        now: Optional[datetime] = None
    ) -> list[str]:
        """
        Get concepts for a study session.

        Returns an optimal mix of:
        - Overdue cards (priority)
        - New cards (if room)

        Args:
            max_count: Maximum cards for this session
            now: Current time (for testing)

        Returns:
            List of concept IDs for the session
        """
        now = now or datetime.now()

        # Get all due concepts
        due = self.get_due_concepts(now)

        # Return up to max_count
        return due[:max_count]

    def get_statistics(self) -> dict:
        """
        Get scheduler statistics.

        Returns:
            Dictionary with stats like total cards, due count,
            average ease factor, etc.
        """
        if not self._cards:
            return {
                "total_cards": 0,
                "due_count": 0,
                "new_count": 0,
                "average_ease_factor": 0,
                "average_interval_days": 0,
                "total_reviews": 0,
                "accuracy_rate": 0,
            }

        now = datetime.now()
        due = [c for c in self._cards.values() if c.is_due(now)]
        new = [c for c in self._cards.values() if c.last_review is None]

        total_reviews = sum(c.total_reviews for c in self._cards.values())
        total_correct = sum(c.total_correct for c in self._cards.values())

        return {
            "total_cards": len(self._cards),
            "due_count": len(due),
            "new_count": len(new),
            "average_ease_factor": sum(c.ease_factor for c in self._cards.values()) / len(self._cards),
            "average_interval_days": sum(c.interval_days for c in self._cards.values()) / len(self._cards),
            "total_reviews": total_reviews,
            "accuracy_rate": total_correct / total_reviews if total_reviews > 0 else 0,
        }

    def save(self, path: Path) -> None:
        """Save scheduler state to a JSON file."""
        data = {
            "version": "1.0",
            "cards": {
                concept_id: card.to_dict()
                for concept_id, card in self._cards.items()
            }
        }
        path.write_text(json.dumps(data, indent=2))

    @classmethod
    def load(cls, path: Path) -> "SpacedRepetitionScheduler":
        """Load scheduler state from a JSON file."""
        scheduler = cls()

        if path.exists():
            data = json.loads(path.read_text())
            for card_data in data.get("cards", {}).values():
                card = SpacedRepetitionCard.from_dict(card_data)
                scheduler._cards[card.concept_id] = card

        return scheduler


# Self-teaching note:
#
# This file demonstrates:
# - The SM-2 algorithm (real cognitive science!)
# - Dataclasses with methods (Level 5+)
# - IntEnum with custom methods (Level 4)
# - datetime arithmetic with timedelta (Standard library)
# - JSON serialization/deserialization patterns
# - Optional type hints (Professional Python)
# - Class methods vs instance methods
# - Default parameter values
#
# The SM-2 algorithm is:
# 1. Based on real memory research (spacing effect)
# 2. Powers Anki (used by millions)
# 3. Mathematically optimal for long-term retention
#
# The key insight: Review just before you'd forget!
# - Too soon = wasted time
# - Too late = relearning from scratch
# - Just right = maximum retention with minimum effort
