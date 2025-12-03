"""
Adaptive Learning Engine
========================

The brain that learns YOUR brain.

- Spaced repetition: Surface concepts at optimal intervals
- Fun tracking: Notice what you enjoy, give you more
- Weakness detection: Gently drill your gaps
- Project-driven: Generate curriculum from your goals
"""

from lmsp.adaptive.engine import AdaptiveEngine
from lmsp.adaptive.spaced import SpacedRepetitionScheduler
from lmsp.adaptive.fun import FunTracker
from lmsp.adaptive.weakness import WeaknessDetector
from lmsp.adaptive.project import ProjectCurriculumGenerator

__all__ = [
    "AdaptiveEngine",
    "SpacedRepetitionScheduler",
    "FunTracker",
    "WeaknessDetector",
    "ProjectCurriculumGenerator",
]
