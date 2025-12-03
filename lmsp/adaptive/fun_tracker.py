"""
Fun Pattern Tracker

Tracks which types of fun resonate with each player.

The 6 Fun Types (from game design research):
1. Puzzle - Problem solving, logic, pattern matching
2. Speedrun - Time pressure, fast execution, efficiency
3. Collection - Completing sets, achievements, unlocking
4. Creation - Building things, projects, making something new
5. Competition - Racing others, leaderboards, comparison
6. Mastery - Getting very good, flow state, deep understanding

We detect player preferences through:
- Emotional input (RT positive, LT negative)
- Time spent on different challenge types
- Replay patterns (what do they voluntarily revisit?)
- Performance patterns (what brings them into flow?)

Self-teaching note:
This file demonstrates:
- Enum with custom descriptions (Level 4)
- Dataclasses with defaults (Level 5: @dataclass)
- Statistical tracking patterns (Level 5+)
- Weighted random sampling (Level 4: random.choices)
- JSON serialization patterns (Level 4)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, List, Any
from datetime import datetime
from pathlib import Path
import json
import random


class FunType(Enum):
    """
    The 6 types of fun that players experience.

    Based on game design research combining:
    - MDA framework (Mechanics, Dynamics, Aesthetics)
    - Bartle's Player Types (adapted for single-player)
    - Flow theory (Csikszentmihalyi)
    """
    PUZZLE = ("puzzle", "Problem solving, logic, pattern matching")
    SPEEDRUN = ("speedrun", "Time pressure, fast execution, efficiency")
    COLLECTION = ("collection", "Completing sets, achievements, unlocking")
    CREATION = ("creation", "Building things, projects, making something new")
    COMPETITION = ("competition", "Racing others, leaderboards, comparison")
    MASTERY = ("mastery", "Getting very good, flow state, deep understanding")

    def __init__(self, short_name: str, desc: str):
        self._short_name = short_name
        self._description = desc

    @property
    def description(self) -> str:
        """Human-readable description of this fun type."""
        return self._description


@dataclass
class FunProfile:
    """
    A player's fun profile - their relative enjoyment of each fun type.

    Weights are normalized to sum to 1.0 for easy comparison.
    Higher weight = player enjoys this type more.

    Usage:
        profile = FunProfile()
        profile.set_weight(FunType.PUZZLE, 0.3)
        print(profile.dominant_type)  # FunType.PUZZLE
    """
    _weights: Dict[FunType, float] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize with equal weights if empty."""
        if not self._weights:
            default = 1.0 / len(FunType)
            for fun_type in FunType:
                self._weights[fun_type] = default

    def get_weights(self) -> Dict[FunType, float]:
        """Get all weights as a dictionary."""
        return dict(self._weights)

    def get_weight(self, fun_type: FunType) -> float:
        """Get weight for a specific fun type."""
        return self._weights.get(fun_type, 0.0)

    def set_weight(self, fun_type: FunType, weight: float):
        """Set weight for a specific fun type."""
        self._weights[fun_type] = max(0.0, weight)

    def adjust_weight(self, fun_type: FunType, delta: float):
        """Adjust weight by a delta (can be negative)."""
        current = self.get_weight(fun_type)
        self._weights[fun_type] = max(0.0, current + delta)

    def normalize(self):
        """Normalize weights to sum to 1.0."""
        total = sum(self._weights.values())
        if total > 0:
            for fun_type in self._weights:
                self._weights[fun_type] /= total

    @property
    def dominant_type(self) -> FunType:
        """Get the fun type with highest weight."""
        return max(self._weights, key=lambda k: self._weights[k])

    def get_top_types(self, n: int = 3) -> List[FunType]:
        """Get top N fun types by weight."""
        sorted_types = sorted(
            self._weights.keys(),
            key=lambda k: self._weights[k],
            reverse=True
        )
        return sorted_types[:n]

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "weights": {ft.name: w for ft, w in self._weights.items()}
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FunProfile":
        """Deserialize from dictionary."""
        profile = cls()
        if "weights" in data:
            for name, weight in data["weights"].items():
                try:
                    fun_type = FunType[name]
                    profile._weights[fun_type] = weight
                except KeyError:
                    pass  # Unknown fun type, skip
        return profile


@dataclass
class FunObservation:
    """
    A single observation of fun/not-fun during gameplay.

    Each observation captures:
    - The type of fun being experienced
    - The enjoyment level (0-1)
    - Context (challenge, concept, etc.)
    - Timestamp
    """
    fun_type: FunType
    enjoyment: float  # 0.0 = not enjoying, 1.0 = maximum enjoyment
    context: str = ""
    timestamp: datetime = field(default_factory=datetime.now)

    @classmethod
    def from_emotional_input(
        cls,
        fun_type: FunType,
        positive_trigger: float,
        negative_trigger: float,
        context: str = ""
    ) -> "FunObservation":
        """
        Create observation from emotional trigger values.

        Args:
            fun_type: Type of fun being experienced
            positive_trigger: RT value (0-1), higher = more positive
            negative_trigger: LT value (0-1), higher = more negative
            context: What was happening (challenge, concept)

        Returns:
            FunObservation with computed enjoyment
        """
        # Net enjoyment: positive - negative, normalized to 0-1
        raw_enjoyment = positive_trigger - negative_trigger
        # Map from [-1, 1] to [0, 1]
        enjoyment = (raw_enjoyment + 1.0) / 2.0

        return cls(
            fun_type=fun_type,
            enjoyment=enjoyment,
            context=context
        )


class FunTracker:
    """
    Tracks fun patterns and updates player's fun profile.

    Features:
    - Observes gameplay and emotional feedback
    - Detects which fun types resonate
    - Recommends challenges based on fun profile
    - Tracks flow state indicators

    Usage:
        tracker = FunTracker()

        # After each challenge
        tracker.observe(FunType.PUZZLE, enjoyment=0.8, context="list_comprehensions")

        # Or from game performance
        tracker.observe_challenge(
            challenge_type="speedrun",
            success=True,
            time_seconds=30,
            enjoyment=0.9
        )

        # Get recommendation
        fun_type = tracker.recommend_fun_type()
    """

    # Learning rate for profile updates
    LEARNING_RATE = 0.1

    # Exploration rate for recommendations
    DEFAULT_EXPLORATION_RATE = 0.2

    # Flow state thresholds
    FLOW_TIME_THRESHOLD = 180  # 3 minutes sustained engagement
    FLOW_STABILITY_THRESHOLD = 0.7
    FLOW_BALANCE_THRESHOLD = 0.6

    def __init__(self):
        self._profile = FunProfile()
        self._observations: List[FunObservation] = []
        self._done_players: set = set()

        # Challenge type to fun type mapping
        self._type_mapping = {
            "puzzle": FunType.PUZZLE,
            "speedrun": FunType.SPEEDRUN,
            "collection": FunType.COLLECTION,
            "creation": FunType.CREATION,
            "competition": FunType.COMPETITION,
            "mastery": FunType.MASTERY,
        }

    def get_profile(self) -> FunProfile:
        """Get the current fun profile."""
        return self._profile

    def observe(
        self,
        fun_type: FunType,
        enjoyment: float,
        context: str = ""
    ):
        """
        Record an observation of fun/not-fun.

        Args:
            fun_type: Which type of fun was experienced
            enjoyment: How enjoyable (0-1), > 0.5 is positive
            context: What was happening (challenge ID, concept, etc.)
        """
        # Record observation
        obs = FunObservation(
            fun_type=fun_type,
            enjoyment=enjoyment,
            context=context
        )
        self._observations.append(obs)

        # Update profile
        self._update_profile_from_observation(obs)

    def _update_profile_from_observation(self, obs: FunObservation):
        """Update the fun profile based on an observation."""
        # Enjoyment > 0.5 means positive experience
        # Enjoyment < 0.5 means negative experience
        # We adjust the weight accordingly

        neutral = 0.5
        delta = (obs.enjoyment - neutral) * self.LEARNING_RATE

        self._profile.adjust_weight(obs.fun_type, delta)
        self._profile.normalize()

    def observe_challenge(
        self,
        challenge_type: str,
        success: bool,
        time_seconds: float,
        enjoyment: float
    ):
        """
        Observe a challenge completion with performance metrics.

        Args:
            challenge_type: Type of challenge (puzzle, speedrun, etc.)
            success: Did the player succeed?
            time_seconds: How long did it take?
            enjoyment: Self-reported or inferred enjoyment (0-1)
        """
        # Map challenge type to fun type
        fun_type = self._type_mapping.get(
            challenge_type.lower(),
            FunType.PUZZLE  # Default
        )

        # Adjust enjoyment based on success
        if not success:
            enjoyment = max(0.0, enjoyment * 0.7)  # Reduce if failed

        self.observe(fun_type, enjoyment, f"challenge:{challenge_type}")

    def observe_flow_indicators(
        self,
        time_in_challenge: float,
        enjoyment_stability: float,
        challenge_skill_balance: float,
        context: str = ""
    ):
        """
        Observe indicators of flow state.

        Flow indicators:
        - Sustained time engagement
        - Stable positive emotion
        - Challenge-skill balance

        Args:
            time_in_challenge: Seconds engaged with challenge
            enjoyment_stability: How stable was enjoyment (0-1)
            challenge_skill_balance: How well matched (0-1)
            context: What was being done
        """
        # Calculate flow score
        time_factor = min(1.0, time_in_challenge / self.FLOW_TIME_THRESHOLD)
        stability_factor = enjoyment_stability / self.FLOW_STABILITY_THRESHOLD
        balance_factor = challenge_skill_balance / self.FLOW_BALANCE_THRESHOLD

        flow_score = (time_factor + stability_factor + balance_factor) / 3.0

        # If strong flow indicators, boost mastery
        if flow_score > 0.7:
            self.observe(FunType.MASTERY, enjoyment=flow_score, context=context)

    def observe_completion(
        self,
        was_optional: bool,
        sought_out: bool,
        enjoyment: float
    ):
        """
        Observe completion behavior for collection fun type.

        Args:
            was_optional: Was this optional content?
            sought_out: Did player actively seek this?
            enjoyment: How enjoyable was completing it?
        """
        # Collection is about completionism
        if was_optional and sought_out:
            # Strong collection indicator
            boost = 0.2
        elif was_optional:
            boost = 0.1
        else:
            boost = 0.0

        adjusted_enjoyment = min(1.0, enjoyment + boost)
        self.observe(FunType.COLLECTION, adjusted_enjoyment, "completion")

    def observe_concept_challenge(
        self,
        concept_id: str,
        challenge_type: str,
        success: bool,
        time_seconds: float,
        hints_used: int,
        positive_emotion: float,
        negative_emotion: float
    ):
        """
        Observe a concept challenge with full metrics.

        Args:
            concept_id: ID of the concept being practiced
            challenge_type: Type of challenge
            success: Did player succeed?
            time_seconds: Time taken
            hints_used: Number of hints used
            positive_emotion: RT trigger value (0-1)
            negative_emotion: LT trigger value (0-1)
        """
        # Map to fun type
        fun_type = self._type_mapping.get(
            challenge_type.lower(),
            FunType.PUZZLE
        )

        # Create observation from emotional input
        obs = FunObservation.from_emotional_input(
            fun_type=fun_type,
            positive_trigger=positive_emotion,
            negative_trigger=negative_emotion,
            context=f"{concept_id}:{challenge_type}"
        )

        self._observations.append(obs)
        self._update_profile_from_observation(obs)

    def classify_challenge(
        self,
        has_time_limit: bool,
        is_competitive: bool,
        is_creative: bool,
        is_collectible: bool,
        requires_deep_thinking: bool
    ) -> FunType:
        """
        Classify a challenge based on its characteristics.

        Args:
            has_time_limit: Time-pressured challenge
            is_competitive: Against others or leaderboard
            is_creative: Open-ended, building something
            is_collectible: Achievement/unlock content
            requires_deep_thinking: Logic/pattern matching

        Returns:
            Most appropriate FunType
        """
        if is_competitive:
            return FunType.COMPETITION
        if has_time_limit:
            return FunType.SPEEDRUN
        if is_creative:
            return FunType.CREATION
        if is_collectible:
            return FunType.COLLECTION
        if requires_deep_thinking:
            return FunType.PUZZLE
        return FunType.MASTERY  # Default for skill-building

    def recommend_fun_type(
        self,
        exploration_rate: float = None
    ) -> FunType:
        """
        Recommend a fun type based on profile.

        Uses epsilon-greedy exploration:
        - Most of the time, recommend dominant type
        - Sometimes explore other types

        Args:
            exploration_rate: Probability of exploring (0-1)

        Returns:
            Recommended FunType
        """
        if exploration_rate is None:
            exploration_rate = self.DEFAULT_EXPLORATION_RATE

        # Explore vs exploit
        if random.random() < exploration_rate:
            # Explore: pick random type
            return random.choice(list(FunType))
        else:
            # Exploit: pick dominant type
            return self._profile.dominant_type

    def recommend_challenge_type_for_concept(
        self,
        concept_id: str,
        available_types: List[str]
    ) -> str:
        """
        Recommend challenge type for a concept based on fun profile.

        Args:
            concept_id: The concept being learned
            available_types: List of available challenge types

        Returns:
            Best challenge type from available options
        """
        # Score each available type by fun profile weight
        best_type = available_types[0]
        best_score = -1.0

        for ctype in available_types:
            fun_type = self._type_mapping.get(ctype.lower())
            if fun_type:
                score = self._profile.get_weight(fun_type)
                if score > best_score:
                    best_score = score
                    best_type = ctype

        return best_type

    def filter_challenges_by_fun(
        self,
        available_challenges: List[dict],
        max_count: int = 5
    ) -> List[dict]:
        """
        Filter and sort challenges by fun profile compatibility.

        Args:
            available_challenges: List of challenge dicts with 'type' key
            max_count: Maximum number to return

        Returns:
            Filtered list sorted by fun profile compatibility
        """
        def score_challenge(challenge: dict) -> float:
            ctype = challenge.get("type", "puzzle")
            fun_type = self._type_mapping.get(ctype.lower(), FunType.PUZZLE)
            return self._profile.get_weight(fun_type)

        # Sort by score (highest first)
        sorted_challenges = sorted(
            available_challenges,
            key=score_challenge,
            reverse=True
        )

        return sorted_challenges[:max_count]

    def get_statistics(self) -> dict:
        """Get statistics about fun tracking."""
        total = len(self._observations)
        if total == 0:
            return {
                "total_observations": 0,
                "dominant_type": self._profile.dominant_type,
                "average_enjoyment": 0.0,
            }

        avg_enjoyment = sum(o.enjoyment for o in self._observations) / total

        return {
            "total_observations": total,
            "dominant_type": self._profile.dominant_type,
            "average_enjoyment": avg_enjoyment,
            "top_types": self._profile.get_top_types(3),
        }

    def save(self, path: Path):
        """Save tracker state to file."""
        data = {
            "version": "1.0",
            "profile": self._profile.to_dict(),
            "observations": [
                {
                    "fun_type": o.fun_type.name,
                    "enjoyment": o.enjoyment,
                    "context": o.context,
                    "timestamp": o.timestamp.isoformat(),
                }
                for o in self._observations
            ]
        }
        path.write_text(json.dumps(data, indent=2))

    @classmethod
    def load(cls, path: Path) -> "FunTracker":
        """Load tracker state from file."""
        tracker = cls()

        if path.exists():
            data = json.loads(path.read_text())

            # Restore profile
            if "profile" in data:
                tracker._profile = FunProfile.from_dict(data["profile"])

            # Restore observations
            for obs_data in data.get("observations", []):
                try:
                    fun_type = FunType[obs_data["fun_type"]]
                    obs = FunObservation(
                        fun_type=fun_type,
                        enjoyment=obs_data.get("enjoyment", 0.5),
                        context=obs_data.get("context", ""),
                        timestamp=datetime.fromisoformat(
                            obs_data.get("timestamp", datetime.now().isoformat())
                        )
                    )
                    tracker._observations.append(obs)
                except (KeyError, ValueError):
                    pass  # Skip invalid entries

        return tracker


# Self-teaching note:
#
# This file demonstrates:
# - Enum with custom attributes (FunType with description)
# - Dataclasses with complex fields (FunProfile, FunObservation)
# - Statistical tracking (learning rate, normalization)
# - Epsilon-greedy exploration (recommend_fun_type)
# - JSON serialization/deserialization
# - Type hints with Optional, Dict, List
#
# The 6 fun types come from game design research:
# - MDA framework (Mechanics, Dynamics, Aesthetics)
# - Bartle's Player Types (Achiever, Explorer, Socializer, Killer)
# - Flow theory by Csikszentmihalyi
#
# Understanding YOUR fun profile makes learning more enjoyable!
# The adaptive engine uses this to select challenges that match
# your preferred play style.
