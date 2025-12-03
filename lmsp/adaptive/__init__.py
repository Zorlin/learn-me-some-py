"""
Adaptive Learning Engine
========================

The brain that learns YOUR brain.

- Spaced repetition: Surface concepts at optimal intervals (Anki-style SM-2)
- Fun tracking: Notice what you enjoy, give you more (6 fun types)
- Weakness detection: Gently drill your gaps (gentle resurfacing)
- Project-driven: Generate curriculum from your goals (backwards from goal)
"""

from lmsp.adaptive.engine import AdaptiveEngine, LearnerProfile, AdaptiveRecommendation

# Spaced Repetition (SM-2 algorithm)
from lmsp.adaptive.spaced_repetition import (
    SpacedRepetitionScheduler,
    SpacedRepetitionCard,
    ReviewQuality,
)

# Fun Tracking (6 fun types)
from lmsp.adaptive.fun_tracker import (
    FunTracker,
    FunType,
    FunProfile,
    FunObservation,
)

# Weakness Detection (gentle resurfacing)
from lmsp.adaptive.weakness import (
    WeaknessDetector,
    WeaknessProfile,
    StrugglePattern,
    ResurfaceStrategy,
    WeaknessRecommendation,
)

# Project-Driven Curriculum
from lmsp.adaptive.curriculum import (
    ProjectCurriculumGenerator,
    Curriculum,
    LearningPath,
    ThemedChallenge,
    ConceptRequirement,
)

__all__ = [
    # Core engine
    "AdaptiveEngine",
    "LearnerProfile",
    "AdaptiveRecommendation",
    # Spaced Repetition
    "SpacedRepetitionScheduler",
    "SpacedRepetitionCard",
    "ReviewQuality",
    # Fun Tracking
    "FunTracker",
    "FunType",
    "FunProfile",
    "FunObservation",
    # Weakness Detection
    "WeaknessDetector",
    "WeaknessProfile",
    "StrugglePattern",
    "ResurfaceStrategy",
    "WeaknessRecommendation",
    # Project-Driven Curriculum
    "ProjectCurriculumGenerator",
    "Curriculum",
    "LearningPath",
    "ThemedChallenge",
    "ConceptRequirement",
]
